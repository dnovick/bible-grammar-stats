"""Disjunctive (noun/subject-first) clause analysis."""
from __future__ import annotations

import pandas as pd

from ._common import _load_macula, _filter_book, _strip_diacritics
from .verb_forms import wayyiqtol_chains

_DISJUNCTIVE_OPENERS = {'noun', 'pron', 'adj'}
_TRANSPARENT = {'cj', 'art', 'prep', 'om', 'ptcl'}

_CONJ_LABELS: dict[str, str] = {
    'וְ':    'waw-disjunctive',
    'וַ':    'waw-disjunctive',
    'כִּי':  'ki (causal/asseverative)',
    'אֲבָל': 'aval (but)',
    'רַק':   'raq (only/however)',
    'אַךְ':  'akh (surely/however)',
    'אֶפֶס': 'efes (nevertheless)',
    'אוּלָם': 'ulam (but)',
}


def _discourse_function(verb_form: str, opener_class: str) -> str:
    if not verb_form:
        return 'nominal clause'
    if verb_form == 'qatal':
        return 'circumstantial / background'
    if verb_form in ('yiqtol', 'weqatal'):
        return 'prospective / result'
    if 'participle' in verb_form:
        return 'circumstantial (ongoing action)'
    if verb_form == 'wayyiqtol':
        return 'contrastive'
    return 'nominal / comment'


def disjunctive_clauses(
    book: str,
    chapter: int | None = None,
) -> pd.DataFrame:
    """
    Find all disjunctive (noun/subject-first) clauses in a book or chapter.

    Returns DataFrame: chapter, verse, opener_text, opener_class, opener_type,
      leading_conj, verb_form, discourse_function, full_text.
    """
    df = _load_macula()
    scope = _filter_book(df, book, chapter)

    refs = (scope[['chapter', 'verse']]
            .drop_duplicates()
            .sort_values(['chapter', 'verse'])
            .values.tolist())

    records = []
    for ch, vs in refs:
        verse_df = scope[
            (scope['chapter'] == ch) & (scope['verse'] == vs)
        ].sort_values('word_num').reset_index(drop=True)

        if verse_df.empty:
            continue

        leading_conj = ''
        start_idx = 0
        if not verse_df.empty and verse_df.iloc[0]['class_'] == 'cj':
            leading_conj = _strip_diacritics(str(verse_df.iloc[0].get('lemma', '')))
            start_idx = 1

        first_content = None
        for idx in range(start_idx, len(verse_df)):
            row = verse_df.iloc[idx]
            cls = str(row.get('class_', ''))
            if cls not in _TRANSPARENT:
                first_content = row
                break

        if first_content is None:
            continue

        opener_class = str(first_content.get('class_', ''))
        if opener_class in _DISJUNCTIVE_OPENERS:
            opener_type = str(first_content.get('type_', ''))
            opener_text = str(first_content.get('text', ''))

            verb_rows = verse_df[verse_df['class_'] == 'verb']
            verb_form = ''
            if not verb_rows.empty:
                verb_form = str(verb_rows.iloc[0].get('type_', ''))

            full_text = ' '.join(str(r['text']) for _, r in verse_df.iterrows())
            conj_label = _CONJ_LABELS.get(leading_conj, leading_conj or '—')
            disc_fn = _discourse_function(verb_form, opener_class)

            records.append({
                'chapter':            int(ch),
                'verse':              int(vs),
                'opener_text':        opener_text,
                'opener_class':       opener_class,
                'opener_type':        opener_type,
                'leading_conj':       conj_label,
                'verb_form':          verb_form,
                'discourse_function': disc_fn,
                'full_text':          full_text[:70],
            })

    return pd.DataFrame(records)


def print_disjunctive_clauses(
    book: str,
    chapter: int | None = None,
    *,
    max_rows: int = 40,
) -> None:
    """Print a formatted list of disjunctive clauses in a book or chapter."""
    df = disjunctive_clauses(book, chapter)
    scope = f"{book} ch.{chapter}" if chapter else book

    print()
    print('═' * 80)
    print(f"  Disjunctive clauses: {scope}  ({len(df)} found)")
    print('─' * 80)

    if df.empty:
        print("  None found.")
        print()
        return

    fn_counts = df['discourse_function'].value_counts()
    print("  By discourse function:")
    for fn, cnt in fn_counts.items():
        print(f"    {fn:<36} × {cnt}")
    print()

    print(f"  {'Ref':<10} {'Opener':<18} {'Class':<8} {'Verb form':<22} {'Function'}")
    print('  ' + '─' * 76)
    for _, row in df.head(max_rows).iterrows():
        ref = f"{book} {row['chapter']}:{row['verse']}"
        print(f"  {ref:<10} {row['opener_text']:<18} {row['opener_class']:<8} "
              f"{row['verb_form']:<22} {row['discourse_function']}")

    if len(df) > max_rows:
        print(f"  … ({len(df) - max_rows} more"
              f" — use disjunctive_clauses() for full DataFrame)")
    print()


def disjunctive_in_chains(book: str, chapter: int) -> list[dict]:
    """
    Cross-reference wayyiqtol chains with disjunctive clauses in a chapter.

    Returns a list of dicts describing each wayyiqtol chain, annotated with
    any disjunctive clauses that appear WITHIN or IMMEDIATELY AFTER the chain.
    """
    chains = wayyiqtol_chains(book, chapter)
    disj = disjunctive_clauses(book, chapter)
    disj_by_verse = {r['verse']: r['discourse_function'] for _, r in disj.iterrows()}

    annotated = []
    for ch in chains:
        chain_verses = {v['verse'] for v in ch['verbs']}
        disj_in = [(vs, fn) for vs, fn in disj_by_verse.items() if vs in chain_verses]

        end_v = ch['end_verse']
        post_disj = disj_by_verse.get(end_v + 1, '')

        if disj_in:
            itype = 'interrupted'
        elif post_disj:
            itype = 'terminated-by-disj'
        else:
            itype = 'clean'

        annotated.append({
            **ch,
            'disjunctives_in_chain': disj_in,
            'post_chain_disj': post_disj,
            'interruption_type': itype,
        })

    return annotated


def print_disjunctive_in_chains(book: str, chapter: int) -> None:
    """Print wayyiqtol chains annotated with interrupting disjunctive clauses."""
    annotated = disjunctive_in_chains(book, chapter)

    print()
    print('═' * 80)
    print(f"  Wayyiqtol chains + disjunctive interruptions: {book} ch.{chapter}")
    print('─' * 80)

    if not annotated:
        print("  No chains found.")
        print()
        return

    for i, ch in enumerate(annotated, 1):
        vref = (f"v{ch['start_verse']}"
                if ch['start_verse'] == ch['end_verse']
                else f"vv{ch['start_verse']}–{ch['end_verse']}")
        itype = ch['interruption_type']
        icon = {'clean': '✓', 'interrupted': '⚡', 'terminated-by-disj': '↵'}.get(itype, '?')
        print(f"\n  {icon} Chain {i}  [{vref}]  length={ch['length']}  [{itype}]")

        for v in ch['verbs']:
            disj_note = ''
            for dv, dfn in ch['disjunctives_in_chain']:
                if dv == v['verse']:
                    disj_note = f'  ← DISJUNCTIVE ({dfn})'
            print(f"    v{v['verse']}  {v['text']:<20}  {v['lemma']:<12}  "
                  f"{v['stem']:<10}{disj_note}")

        if ch['post_chain_disj']:
            print(f"    → chain ends; v{ch['end_verse']+1} = "
                  f"disjunctive ({ch['post_chain_disj']})")

    clean = sum(1 for c in annotated if c['interruption_type'] == 'clean')
    inter = sum(1 for c in annotated if c['interruption_type'] == 'interrupted')
    term = sum(1 for c in annotated if c['interruption_type'] == 'terminated-by-disj')
    print(f"\n  Summary: {len(annotated)} chains — "
          f"{clean} clean · {inter} interrupted · {term} terminated-by-disjunctive")
    print()
