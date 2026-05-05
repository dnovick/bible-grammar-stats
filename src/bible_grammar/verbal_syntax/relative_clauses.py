"""Relative clause (אֲשֶׁר / שֶׁ / דִּי) analysis."""
from __future__ import annotations

import pandas as pd

from ._common import _load_macula, _filter_book, _strip_diacritics

_REL_MARKERS = {'אשר', 'ש', 'די', 'זו', 'זה'}

_ANT_PERSON_LEMMAS = {
    'איש', 'אשה', 'בן', 'בת', 'אב', 'אם', 'אח', 'אחות',
    'עבד', 'שפחה', 'מלך', 'נביא', 'כהן', 'שופט', 'עם',
    'זקן', 'נשיא', 'אדם', 'ילד', 'נער', 'נערה',
}
_ANT_TIME_LEMMAS = {
    'יום', 'שנה', 'עת', 'פעם', 'עולם', 'רגע', 'שעה',
    'בקר', 'ערב', 'לילה', 'חדש', 'שבת', 'יובל', 'שמטה',
}
_ANT_PLACE_LEMMAS = {
    'ארץ', 'מקום', 'עיר', 'הר', 'גבול', 'שדה', 'בית',
    'שמים', 'ים', 'מדבר', 'נחל', 'נהר', 'גן', 'מזבח',
}


def _antecedent_class(lemma_stripped: str, cls: str, noun_type: str) -> str:
    lem = lemma_stripped.lower()
    if cls == 'noun' and noun_type == 'proper':
        return 'person/place (proper)'
    if lem in _ANT_PERSON_LEMMAS:
        return 'person'
    if lem in _ANT_TIME_LEMMAS:
        return 'time'
    if lem in _ANT_PLACE_LEMMAS:
        return 'place'
    return 'thing'


def _infer_rel_role(
    pos: int,
    row: pd.Series,
    df_idx: pd.DataFrame,
) -> tuple[str, str, str]:
    """Return (inferred_role, rel_verb_form, rel_verb_text)."""
    verb_found = False
    rel_verb_form = ''
    rel_verb_text = ''
    resumptive_role = ''
    has_explicit_subj = False

    for fwd in range(1, 18):
        fpos = pos + fwd
        if fpos >= len(df_idx):
            break
        fr = df_idx.iloc[fpos]
        if fr['chapter'] != row['chapter']:
            break
        if int(fr['verse']) - int(row['verse']) > 1:
            break

        if fr['class_'] == 'verb' and not verb_found:
            verb_found = True
            rel_verb_form = str(fr['type_'])
            rel_verb_text = str(fr['text'])

        if fr['class_'] == 'pron' and fr['role'] in ('o', 'o2', 'p'):
            if not resumptive_role:
                resumptive_role = fr['role']

        if fr['role'] == 's' and fr['class_'] != 'rel':
            has_explicit_subj = True

    if not verb_found:
        inferred = 'verbless'
    elif resumptive_role in ('o', 'o2'):
        inferred = 'object'
    elif resumptive_role == 'p':
        inferred = 'oblique'
    elif has_explicit_subj:
        inferred = 'object'
    else:
        inferred = 'subject'

    return inferred, rel_verb_form, rel_verb_text


def relative_clauses(
    book: str,
    chapter: int | None = None,
    *,
    markers: set[str] | None = None,
) -> pd.DataFrame:
    """
    Find all relative clauses in a book or chapter.

    Returns DataFrame: chapter, verse, marker, antecedent_text, antecedent_class,
      inferred_role, rel_verb_form, rel_verb_text, verse_text.
    """
    if markers is None:
        markers = {'אשר', 'ש', 'די'}

    df = _load_macula()
    scope = _filter_book(df, book, chapter).reset_index(drop=True)
    scope = scope.copy()
    scope['_lem'] = scope['lemma'].apply(_strip_diacritics)

    records: list[dict] = []
    for pos, row in scope.iterrows():
        if str(row.get('class_', '')) != 'rel':
            continue
        lem = row['_lem']
        if lem not in markers:
            continue

        ch_val = row['chapter']
        vs_val = row['verse']
        bk_val = row['book']

        ant_text = ''
        ant_cls = ''
        ant_type = ''
        ant_lem = ''
        for back in range(1, 10):
            bpos = pos - back
            if bpos < 0:
                break
            br = scope.iloc[bpos]
            if br['chapter'] != ch_val:
                break
            if str(br.get('class_', '')) in ('noun', 'adj', 'pron', 'verb'):
                ant_text = str(br.get('text', ''))
                ant_cls = str(br.get('class_', ''))
                ant_type = str(br.get('type_', ''))
                ant_lem = br['_lem']
                break

        ant_sem = _antecedent_class(ant_lem, ant_cls, ant_type)
        inferred, rv_form, rv_text = _infer_rel_role(pos, row, scope)

        vs_tokens = scope[
            (scope['book'] == bk_val) &
            (scope['chapter'] == ch_val) &
            (scope['verse'] == vs_val)
        ]
        vs_text = ' '.join(str(r['text']) for _, r in vs_tokens.iterrows())

        records.append({
            'chapter':          int(ch_val),
            'verse':            int(vs_val),
            'marker':           str(row.get('text', '')),
            'antecedent_text':  ant_text,
            'antecedent_class': ant_sem,
            'inferred_role':    inferred,
            'rel_verb_form':    rv_form,
            'rel_verb_text':    rv_text,
            'verse_text':       vs_text[:70],
        })

    return pd.DataFrame(records)


def print_relative_clauses(
    book: str,
    chapter: int | None = None,
    *,
    max_rows: int = 40,
) -> None:
    """Print a formatted table of relative clauses in a book or chapter."""
    df = relative_clauses(book, chapter)
    scope = f"{book} ch.{chapter}" if chapter else book

    print()
    print('═' * 80)
    print(f"  Relative clauses: {scope}  ({len(df)} found)")
    print('─' * 80)

    if df.empty:
        print("  None found.")
        print()
        return

    print("  Inferred role distribution:")
    for role, cnt in df['inferred_role'].value_counts().items():
        pct = cnt / len(df) * 100
        bar = '█' * int(pct / 4)
        print(f"    {role:<12} {cnt:>4}  ({pct:>4.1f}%)  {bar}")
    print()

    print("  Rel clause verb form distribution:")
    for form, cnt in df['rel_verb_form'].value_counts().head(8).items():
        if form:
            pct = cnt / len(df) * 100
            print(f"    {form:<25} {cnt:>4}  ({pct:>4.1f}%)")
    print()

    print(f"  {'Ref':<10} {'Marker':<10} {'Antecedent':<18} "
          f"{'Role':<12} {'Verb form':<22} {'Rel verb'}")
    print('  ' + '─' * 78)
    for _, row in df.head(max_rows).iterrows():
        ref = f"{book} {row['chapter']}:{row['verse']}"
        print(f"  {ref:<10} {row['marker']:<10} {row['antecedent_text']:<18} "
              f"{row['inferred_role']:<12} {row['rel_verb_form']:<22} {row['rel_verb_text']}")

    if len(df) > max_rows:
        print(f"  … ({len(df) - max_rows} more — use relative_clauses() for full DataFrame)")
    print()


def relative_clause_summary(book: str) -> pd.DataFrame:
    """Return a cross-tabulation of inferred role × verb form for a book."""
    df = relative_clauses(book)
    if df.empty:
        return pd.DataFrame(columns=['inferred_role', 'rel_verb_form', 'count', 'pct'])
    grp = df.groupby(['inferred_role', 'rel_verb_form']).size().reset_index(name='count')
    total = grp['count'].sum()
    grp['pct'] = (grp['count'] / total * 100).round(1)
    return grp.sort_values('count', ascending=False)


def print_relative_summary(book: str) -> None:
    """Print a compact summary of relative clause types for a book."""
    df = relative_clauses(book)
    if df.empty:
        print(f"\n  No relative clauses found in {book}.\n")
        return

    total = len(df)
    print()
    print('═' * 80)
    print(f"  Relative clause summary: {book}  (total: {total})")
    print('─' * 80)

    print("  By inferred role:")
    for role, cnt in df['inferred_role'].value_counts().items():
        pct = cnt / total * 100
        bar = '█' * int(pct / 3)
        print(f"    {role:<12} {cnt:>4}  {pct:>5.1f}%  {bar}")
    print()

    print("  By relative clause verb form:")
    for form, cnt in df['rel_verb_form'].value_counts().head(8).items():
        if form:
            pct = cnt / total * 100
            bar = '█' * int(pct / 3)
            print(f"    {form:<25} {cnt:>4}  {pct:>5.1f}%  {bar}")
    print()

    print("  By antecedent semantic class:")
    for sem, cnt in df['antecedent_class'].value_counts().items():
        pct = cnt / total * 100
        bar = '█' * int(pct / 3)
        print(f"    {sem:<25} {cnt:>4}  {pct:>5.1f}%  {bar}")
    print()
