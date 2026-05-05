"""Conditional clause (אִם / לוּ / לוּלֵא) analysis."""
from __future__ import annotations

import pandas as pd

from ._common import _load_macula, _filter_book, _strip_diacritics

_COND_PARTICLE_LABELS: dict[str, str] = {
    'אם':    'אִם (if)',
    'לו':    'לוּ (wish/irreal)',
    'לולא':  'לוּלֵא (had it not been)',
    'לולי':  'לוּלֵי (had it not been)',
    'הן':    'הֵן (if/behold — rare cond.)',
}


def _condition_type(particle: str, verb_form: str) -> str:
    if particle == 'אם':
        if verb_form == 'yiqtol':
            return 'real — open future (אִם + yiqtol)'
        if verb_form == 'qatal':
            return 'real — past/present state (אִם + qatal)'
        if 'participle' in verb_form:
            return 'real — stative/habitual (אִם + ptc)'
        if verb_form == 'imperative':
            return 'real — command protasis (אִם + impv)'
        if verb_form in ('weqatal', 'cohortative', 'jussive'):
            return f'real — {verb_form} protasis'
        if verb_form == 'infinitive absolute':
            return 'real — emphatic (אִם + inf.abs)'
        if not verb_form:
            return 'real — nominal protasis'
        return f'real — {verb_form}'
    if particle in ('לו', 'לולא', 'לולי'):
        if verb_form == 'qatal':
            return 'irreal — past counterfactual (לוּ + qatal)'
        if verb_form == 'yiqtol':
            return 'irreal — wish/desire (לוּ + yiqtol)'
        if not verb_form:
            return 'irreal — nominal'
        return f'irreal — {verb_form}'
    if particle == 'הן':
        return f'hén condition — {verb_form or "?"}'
    return f'other — {verb_form or "?"}'


def conditional_clauses(
    book: str,
    chapter: int | None = None,
) -> pd.DataFrame:
    """
    Find all conditional clauses in a book or chapter.

    Returns DataFrame: chapter, verse, particle, particle_label,
      protasis_verb_text, protasis_verb_form, protasis_verb_stem,
      condition_type, verse_text.
    """
    df = _load_macula()
    scope = _filter_book(df, book, chapter).reset_index(drop=True)
    scope = scope.copy()
    scope['_lem'] = scope['lemma'].apply(_strip_diacritics)

    cond_stripped = set(_COND_PARTICLE_LABELS.keys())

    records = []
    for pos, row in scope.iterrows():
        lem = row['_lem']
        cls = str(row.get('class_', ''))

        if lem == 'אם' and cls != 'cj':
            continue
        if lem == 'הן' and cls != 'cj':
            continue
        if lem not in cond_stripped:
            continue

        ch_val = row['chapter']
        vs_val = row['verse']
        bk_val = row['book']

        proto_verb = None
        for offset in range(1, 20):
            npos = pos + offset
            if npos >= len(scope):
                break
            nrow = scope.iloc[npos]
            if nrow['book'] != bk_val or nrow['chapter'] != ch_val:
                break
            if nrow['verse'] != vs_val and offset > 8:
                break
            if nrow['class_'] == 'verb':
                proto_verb = nrow
                break

        proto_form = str(proto_verb['type_']) if proto_verb is not None else ''
        proto_stem = str(proto_verb['stem']) if proto_verb is not None else ''
        proto_text = str(proto_verb['text']) if proto_verb is not None else ''

        ctype = _condition_type(lem, proto_form)

        vs_tokens = scope[
            (scope['book'] == bk_val) &
            (scope['chapter'] == ch_val) &
            (scope['verse'] == vs_val)
        ]
        vs_text = ' '.join(str(r['text']) for _, r in vs_tokens.iterrows())

        records.append({
            'chapter':             int(ch_val),
            'verse':               int(vs_val),
            'particle':            str(row.get('text', '')),
            'particle_label':      _COND_PARTICLE_LABELS.get(lem, lem),
            'protasis_verb_text':  proto_text,
            'protasis_verb_form':  proto_form,
            'protasis_verb_stem':  proto_stem,
            'condition_type':      ctype,
            'verse_text':          vs_text[:70],
        })

    return pd.DataFrame(records)


def print_conditional_clauses(
    book: str,
    chapter: int | None = None,
    *,
    max_rows: int = 40,
) -> None:
    """Print a formatted table of conditional clauses in a book or chapter."""
    df = conditional_clauses(book, chapter)
    scope = f"{book} ch.{chapter}" if chapter else book

    print()
    print('═' * 80)
    print(f"  Conditional clauses: {scope}  ({len(df)} found)")
    print('─' * 80)

    if df.empty:
        print("  None found.")
        print()
        return

    print("  By condition type:")
    for ctype, cnt in df['condition_type'].value_counts().items():
        print(f"    {ctype:<46} × {cnt}")
    print()

    print(f"  {'Ref':<10} {'Particle':<10} {'Protasis verb':<20} {'Form':<22} {'Type'}")
    print('  ' + '─' * 76)
    for _, row in df.head(max_rows).iterrows():
        ref = f"{book} {row['chapter']}:{row['verse']}"
        print(f"  {ref:<10} {row['particle']:<10} {row['protasis_verb_text']:<20} "
              f"{row['protasis_verb_form']:<22} {row['condition_type'][:38]}")

    if len(df) > max_rows:
        print(f"  … ({len(df) - max_rows} more — use conditional_clauses() for full DataFrame)")
    print()


def conditional_summary(book: str) -> pd.DataFrame:
    """Return a summary DataFrame of conditional clause type counts for a book.
    Columns: condition_type, count, pct."""
    df = conditional_clauses(book)
    if df.empty:
        return pd.DataFrame(columns=['condition_type', 'count', 'pct'])
    counts = df['condition_type'].value_counts().reset_index()
    counts.columns = ['condition_type', 'count']
    total = counts['count'].sum()
    counts['pct'] = (counts['count'] / total * 100).round(1)
    return counts


def print_conditional_summary(book: str) -> None:
    """Print a compact summary of conditional clause types for a book."""
    df = conditional_summary(book)
    total = df['count'].sum()

    print()
    print('═' * 80)
    print(f"  Conditional clause summary: {book}  (total: {total})")
    print('─' * 80)
    for _, row in df.iterrows():
        bar = '█' * int(row['pct'] / 3)
        print(f"  {row['condition_type']:<46} {row['count']:>4}  {row['pct']:>5.1f}%  {bar}")
    print()
