"""Discourse particle tagging and analysis."""
from __future__ import annotations

import pandas as pd

from ._common import _load_macula, _filter_book, _strip_diacritics

_PTCL_REGISTRY: dict[str, tuple[str | None, str, str]] = {
    'הנה':  (None,  'הִנֵּה',  'presentative'),
    'כי':   ('cj',  'כִּי',    'connective'),
    'ו':    ('cj',  'וְ',      'connective'),
    'לכן':  (None,  'לָכֵן',   'consequence'),
    'עתה':  (None,  'עַתָּה',  'temporal'),
    'גם':   (None,  'גַּם',    'additive'),
    'אך':   (None,  'אַךְ',    'restrictive'),
}

_KI_SENSE_MAP: dict[str, str] = {
    'because': 'causal', 'for': 'causal', 'since': 'causal', 'so': 'causal',
    'that': 'content', 'indeed': 'asseverative', 'surely': 'asseverative',
    'yes': 'asseverative', 'truly': 'asseverative', 'verily': 'asseverative',
    'but': 'adversative', 'yet': 'adversative', 'though': 'adversative',
    'although': 'adversative', 'however': 'adversative',
    'nevertheless': 'adversative', 'if': 'conditional', 'unless': 'conditional',
    'except': 'conditional', 'when': 'temporal', 'as': 'temporal',
    'while': 'temporal', 'how': 'exclamatory', 'even': 'emphatic', 'and': 'emphatic',
}

_WAW_SENSE_MAP: dict[str, str] = {
    'and': 'sequential', 'then': 'sequential', 'or': 'sequential',
    'now': 'sequential', 'that': 'sequential', 'with': 'sequential',
    'but': 'adversative', 'yet': 'adversative', 'though': 'adversative',
    'however': 'adversative', 'nevertheless': 'adversative',
    'so': 'logical', 'for': 'logical', 'since': 'logical', 'therefore': 'logical',
    'when': 'temporal', 'while': 'temporal',
    'even': 'emphatic', 'indeed': 'emphatic', 'also': 'emphatic', 'also ': 'emphatic',
}


def _ptcl_function(lem: str, english_gloss: str) -> str:
    g = english_gloss.strip().lower()
    if lem == 'כי':
        return _KI_SENSE_MAP.get(g, f'other ({g})' if g else 'unclassified')
    if lem == 'ו':
        return _WAW_SENSE_MAP.get(g, f'other ({g})' if g else 'sequential')
    fixed = {
        'הנה': 'presentative', 'לכן': 'consequence', 'עתה': 'temporal',
        'גם': 'additive', 'אך': 'restrictive',
    }
    return fixed.get(lem, 'particle')


def discourse_particles(
    book: str,
    chapter: int | None = None,
    *,
    particles: list[str] | None = None,
) -> pd.DataFrame:
    """
    Tag all discourse particle tokens in a book or chapter.

    Returns DataFrame: chapter, verse, particle_label, particle_text,
      discourse_function, following_text, verse_text.
    """
    if particles is None:
        particles = list(_PTCL_REGISTRY.keys())

    df = _load_macula()
    scope = _filter_book(df, book, chapter).reset_index(drop=True)
    scope = scope.copy()
    scope['_lem'] = scope['lemma'].apply(_strip_diacritics)

    records: list[dict] = []
    for pos, row in scope.iterrows():
        lem = row['_lem']
        if lem not in particles:
            continue
        cls = str(row.get('class_', ''))
        reg_cls, display_label, _ = _PTCL_REGISTRY.get(lem, (None, lem, ''))
        if reg_cls is not None and cls != reg_cls:
            continue

        ch_val = row['chapter']
        vs_val = row['verse']
        bk_val = row['book']

        english = str(row.get('english', ''))
        func = _ptcl_function(lem, english)

        following = []
        for fwd in range(1, 6):
            fpos = pos + fwd
            if fpos >= len(scope):
                break
            fr = scope.iloc[fpos]
            if fr['chapter'] != ch_val:
                break
            if str(fr.get('class_', '')) in ('noun', 'verb', 'adj', 'pron', 'adv'):
                following.append(str(fr.get('text', '')))
                if len(following) >= 3:
                    break

        vs_tokens = scope[
            (scope['book'] == bk_val) &
            (scope['chapter'] == ch_val) &
            (scope['verse'] == vs_val)
        ]
        vs_text = ' '.join(str(r['text']) for _, r in vs_tokens.iterrows())

        records.append({
            'chapter':            int(ch_val),
            'verse':              int(vs_val),
            'particle_label':     display_label,
            'particle_text':      str(row.get('text', '')),
            'discourse_function': func,
            'following_text':     ' '.join(following),
            'verse_text':         vs_text[:70],
        })

    return pd.DataFrame(records)


def print_discourse_particles(
    book: str,
    chapter: int | None = None,
    *,
    particles: list[str] | None = None,
    max_rows: int = 50,
    omit_waw: bool = True,
) -> None:
    """Print a formatted report of discourse particles in a book or chapter."""
    df = discourse_particles(book, chapter, particles=particles)
    scope = f"{book} ch.{chapter}" if chapter else book

    print()
    print('═' * 80)
    print(f"  Discourse particles: {scope}  ({len(df)} total tokens)")
    print('─' * 80)

    if df.empty:
        print("  None found.")
        print()
        return

    print("  By particle and discourse function:")
    for ptcl_lbl in df['particle_label'].unique():
        sub = df[df['particle_label'] == ptcl_lbl]
        print(f"\n  {ptcl_lbl}  ({len(sub)} tokens)")
        for func, cnt in sub['discourse_function'].value_counts().items():
            pct = cnt / len(sub) * 100
            bar = '█' * int(pct / 5)
            print(f"    {func:<30} {cnt:>4}  {pct:>5.1f}%  {bar}")

    print()
    print(f"  {'Ref':<10} {'Particle':<10} {'Function':<28} {'Following'}")
    print('  ' + '─' * 78)

    display_df = df if not omit_waw else df[df['particle_label'] != 'וְ']
    shown = 0
    for _, row in display_df.iterrows():
        if shown >= max_rows:
            remaining = len(display_df) - shown
            print(f"  … ({remaining} more — use discourse_particles() for full DataFrame)")
            break
        ref = f"{book} {row['chapter']}:{row['verse']}"
        print(f"  {ref:<10} {row['particle_text']:<10} "
              f"{row['discourse_function']:<28} {row['following_text']}")
        shown += 1
    print()


def discourse_particle_summary(book: str) -> pd.DataFrame:
    """Return a summary DataFrame of discourse particle function counts for a book.
    Columns: particle_label, discourse_function, count, pct_of_particle."""
    df = discourse_particles(book)
    if df.empty:
        return pd.DataFrame(columns=['particle_label', 'discourse_function',
                                     'count', 'pct_of_particle'])
    grp = df.groupby(['particle_label', 'discourse_function']).size().reset_index(name='count')
    totals = grp.groupby('particle_label')['count'].transform('sum')
    grp['pct_of_particle'] = (grp['count'] / totals * 100).round(1)
    return grp.sort_values(['particle_label', 'count'], ascending=[True, False])


def print_particle_summary(book: str) -> None:
    """Print a compact summary of all discourse particle functions for a book."""
    df = discourse_particle_summary(book)
    if df.empty:
        print(f"\n  No discourse particles found in {book}.\n")
        return
    total_tokens = df['count'].sum()

    print()
    print('═' * 80)
    print(f"  Discourse particle summary: {book}  (total tokens: {total_tokens})")
    print()
    for ptcl_lbl, sub in df.groupby('particle_label'):
        ptcl_total = sub['count'].sum()
        print(f"  {ptcl_lbl}  — {ptcl_total} tokens")
        for _, row in sub.iterrows():
            bar = '█' * int(row['pct_of_particle'] / 5)
            print(f"    {row['discourse_function']:<30} {row['count']:>4}  "
                  f"{row['pct_of_particle']:>5.1f}%  {bar}")
        print()
