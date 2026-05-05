"""
Piel verb morphology analysis for Biblical Hebrew instruction.

The Piel (פִּעֵל) is the intensive-active stem of Biblical Hebrew.
It typically:
  • Expresses an intensive action: שִׁבֵּר (shattered) ← Qal שָׁבַר (broke)
  • Expresses a factitive (makes state into action): קִדֵּשׁ (made holy) ← קָדוֹשׁ (holy)
  • Expresses a declarative: הִצְדִּיק → Piel צִדֵּק (declared righteous)
  • Expresses a denominative (verb from noun): דִּבֵּר (spoke) ← דָּבָר (word)
  • Has a simple active sense for some roots that rarely appear in Qal

All functions use MACULA Hebrew WLC data (load_syntax_ot).

Public API
──────────
piel_data()                           → DataFrame (all Piel tokens)
piel_conjugation_profile(book=None)   → DataFrame (type_ distribution)
piel_top_roots(n=30, book=None)       → DataFrame (most frequent roots)
piel_root_conjugation(roots=None)     → DataFrame (root × conjugation crosstab)
piel_book_distribution()              → DataFrame (count + pct per book)
piel_stem_comparison(books=None)      → DataFrame (all stems % by book)
piel_dominant_roots(min_pct=70)       → DataFrame (roots >X% Piel)
piel_semantic_categories()            → DataFrame (semantic function counts)

print_piel_overview()                 → None
print_piel_conjugation(book=None)     → None
print_piel_top_roots(n=20, book=None) → None
print_piel_root_conjugation(roots=None) → None
print_piel_book_distribution()        → None
print_piel_dominant_roots()           → None
print_piel_semantic_categories()      → None

piel_conjugation_chart(book=None)     → Path | None
piel_book_chart()                     → Path | None
piel_stem_chart(books=None)           → Path | None
piel_root_heatmap(top_n=15)           → Path | None

piel_report(output_dir=None)          → Path   (full Markdown report)
"""

from __future__ import annotations
from pathlib import Path

import pandas as pd

from ._stem_analysis import StemAnalysis, StemConfig


# ── Semantic function classifier ──────────────────────────────────────────────

_INTENSIVE_KEYWORDS = (
    'shattered', 'broke in pieces', 'smashed', 'destroyed', 'tore',
    'scattered', 'drove out', 'pursued', 'chased', 'crushed',
    'bless', 'blessed', 'curse', 'cursed', 'praise', 'praised',
    'seek', 'sought', 'inquire', 'inquired',
)

_FACTITIVE_KEYWORDS = (
    'made holy', 'consecrated', 'sanctified', 'purified', 'made clean',
    'defiled', 'made unclean', 'honored', 'glorified', 'justified',
    'made righteous', 'made great', 'magnified', 'made numerous',
    'made strong', 'strengthened', 'made full', 'filled',
)

_DECLARATIVE_KEYWORDS = (
    'declared', 'declared righteous', 'declared guilty', 'declared clean',
    'declared unclean', 'counted', 'regarded as', 'reckoned',
    'pronounced', 'called', 'named',
)

_DENOMINATIVE_KEYWORDS = (
    'spoke', 'speak', 'told', 'commanded', 'prophesied', 'prophesy',
    'prayed', 'pray', 'ministered', 'minister', 'served as priest',
    'acted as priest', 'played', 'sang', 'sang praise',
)


def _piel_semantic_fn(gloss: str) -> str:
    g = str(gloss).strip().lower()
    if any(w in g for w in _DECLARATIVE_KEYWORDS):
        return 'declarative'
    if any(w in g for w in _FACTITIVE_KEYWORDS):
        return 'factitive'
    if any(w in g for w in _DENOMINATIVE_KEYWORDS):
        return 'denominative'
    if any(w in g for w in _INTENSIVE_KEYWORDS):
        return 'intensive'
    return 'other'


# ── Config + analysis engine ──────────────────────────────────────────────────

_CONFIG = StemConfig(
    name='piel',
    macula_value='piel',
    display='Piel (פִּעֵל)',
    chart_color='#5B9BD5',  # blue
)

_ANALYSIS = StemAnalysis(_CONFIG)


# ── Public API wrappers ───────────────────────────────────────────────────────

def piel_data(book: str | None = None) -> pd.DataFrame:
    """Return all Piel tokens, optionally filtered to one book."""
    return _ANALYSIS.data(book)


def piel_conjugation_profile(book: str | None = None) -> pd.DataFrame:
    """Count Piel tokens by conjugation type. Returns DataFrame: form, count, pct."""
    return _ANALYSIS.conjugation_profile(book)


def piel_top_roots(n: int = 30, book: str | None = None) -> pd.DataFrame:
    """Return the top-n most frequent Piel roots. Columns: root, lemma, count, pct, top_gloss."""
    return _ANALYSIS.top_roots(n, book)


def piel_root_conjugation(
    roots: list[str] | None = None,
    top_n: int = 15,
) -> pd.DataFrame:
    """Return a root × conjugation crosstab (counts)."""
    return _ANALYSIS.root_conjugation(roots, top_n)


def piel_book_distribution() -> pd.DataFrame:
    """Count Piel tokens per book with percentage of all-OT Piel."""
    return _ANALYSIS.book_distribution()


def piel_stem_comparison(books: list[str] | None = None) -> pd.DataFrame:
    """Return verb stem percentages for a set of books."""
    return _ANALYSIS.stem_comparison(books)


def piel_dominant_roots(
    min_pct: float = 70.0,
    min_tokens: int = 10,
) -> pd.DataFrame:
    """Roots where the Piel accounts for ≥ min_pct of all occurrences."""
    return _ANALYSIS.dominant_roots(min_pct, min_tokens)


def piel_semantic_categories() -> pd.DataFrame:
    """Assign each Piel token a broad semantic function category."""
    return _ANALYSIS.semantic_categories(_piel_semantic_fn)


def print_piel_overview() -> None:
    """Print a quick statistical overview of the Piel in the OT."""
    _ANALYSIS.print_overview()


def print_piel_conjugation(book: str | None = None) -> None:
    """Print Piel conjugation distribution."""
    _ANALYSIS.print_conjugation(book)


def print_piel_top_roots(n: int = 25, book: str | None = None) -> None:
    """Print the top Piel roots."""
    _ANALYSIS.print_top_roots(n, book)


def print_piel_root_conjugation(roots: list[str] | None = None, top_n: int = 15) -> None:
    """Print root × conjugation frequency table."""
    _ANALYSIS.print_root_conjugation(roots, top_n)


def print_piel_book_distribution(top_n: int = 25) -> None:
    """Print Piel distribution across books."""
    _ANALYSIS.print_book_distribution(top_n)


def print_piel_dominant_roots(top_n: int = 25) -> None:
    """Print roots where the Piel is the dominant stem."""
    _ANALYSIS.print_dominant_roots(top_n)


def print_piel_semantic_categories() -> None:
    """Print Piel semantic function distribution."""
    _ANALYSIS.print_semantic_categories(_piel_semantic_fn)


def piel_conjugation_chart(book: str | None = None) -> Path | None:
    """Save a horizontal bar chart of Piel conjugation distribution."""
    return _ANALYSIS.conjugation_chart(book)


def piel_book_chart(top_n: int = 20) -> Path | None:
    """Save a bar chart of top books by Piel count."""
    return _ANALYSIS.book_chart(top_n)


def piel_stem_chart(books: list[str] | None = None) -> Path | None:
    """Save a stacked bar chart showing all verb stem percentages."""
    return _ANALYSIS.stem_comparison_chart(books)


def piel_root_heatmap(top_n: int = 15) -> Path | None:
    """Save a heatmap: top roots × conjugation type (row-normalised %)."""
    return _ANALYSIS.root_heatmap(top_n)


def piel_semantic_chart() -> Path | None:
    """Save a pie chart of Piel semantic function categories."""
    return _ANALYSIS.semantic_chart(_piel_semantic_fn)


def piel_top_roots_chart(top_n: int = 20) -> Path | None:
    """Save a horizontal bar chart of the top Piel roots."""
    return _ANALYSIS.top_roots_chart(top_n)


def piel_report(output_dir: str | None = None) -> Path:
    """Generate a complete Piel morphology report (Markdown + PNG charts)."""
    if output_dir is None:
        out_dir = Path('output') / 'reports' / 'ot' / 'verbs'
    else:
        out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating charts...")
    charts: dict[str, Path | None] = {
        'conjugation': piel_conjugation_chart(),
        'books':       piel_book_chart(),
        'stems':       piel_stem_chart(),
        'heatmap':     piel_root_heatmap(),
        'semantic':    piel_semantic_chart(),
        'top_roots':   piel_top_roots_chart(),
    }
    for k, p in charts.items():
        if p:
            print(f"  ✓ {k}: {p}")

    df_full = _ANALYSIS._load()
    h = _ANALYSIS._stem_df(df_full)
    total_tokens = len(h)
    total_verbs = len(df_full[df_full['class_'] == 'verb'])
    unique_roots = h['_lem'].nunique()

    conj_df = piel_conjugation_profile()
    top_roots_df = piel_top_roots(20)
    dom_df = piel_dominant_roots(min_pct=80, min_tokens=10).head(20)
    sem_df = piel_semantic_categories()
    book_df = piel_book_distribution().head(20)

    lines: list[str] = []
    lines.append('# Piel (פִּעֵל) Verb Morphology — Biblical Hebrew\n')
    lines.append('*Generated from MACULA Hebrew WLC data*\n\n')
    lines.append('---\n\n')

    lines.append('## 1. Overview\n\n')
    lines.append(
        'The **Piel** stem is the primary intensive-active stem of Biblical Hebrew. '
        'It is formed with a **Dagesh Forte in the middle root consonant (R2)** '
        'and a characteristic Tsere or Patach vowel pattern.\n\n'
    )
    lines.append('| Statistic | Value |\n|---|---|\n')
    lines.append(f'| Total Piel tokens (OT) | {total_tokens:,} |\n')
    lines.append(f'| % of all OT verb tokens  | {total_tokens/total_verbs*100:.1f}% |\n')
    lines.append(f'| Unique roots in Piel   | {unique_roots} |\n')

    lines.append('## 2. Conjugation Distribution\n\n')
    lines.append('| Conjugation | Count | % |\n|---|---|---|\n')
    for _, row in conj_df.iterrows():
        if row['count'] > 0:
            lines.append(f"| {row['form']} | {row['count']:,} | {row['pct']}% |\n")
    lines.append('\n')

    lines.append('## 3. Distribution Across Books\n\n')
    lines.append('| Book | Count | % of OT Piel | % of book verbs |\n|---|---|---|---|\n')
    for _, row in book_df.iterrows():
        lines.append(
            f"| {row['book']} | {row['count']:,} | {row['pct']}% "
            f"| {row['pct_of_book_verbs']}% |\n")
    lines.append('\n')

    lines.append('## 4. Most Frequent Piel Roots\n\n')
    lines.append('| # | Root | Lemma | Count | % | Primary meaning |\n|---|---|---|---|---|---|\n')
    for i, row in top_roots_df.iterrows():
        lines.append(
            f"| {i+1} | {row['root']} | {row['lemma']} | {row['count']:,} "
            f"| {row['pct']}% | {row['top_gloss']} |\n")
    lines.append('\n')

    lines.append('## 5. Piel-Dominant Roots (≥80%)\n\n')
    lines.append('| Root | Lemma | Piel | Total | % | Gloss |\n|---|---|---|---|---|---|\n')
    for _, row in dom_df.iterrows():
        lines.append(
            f"| {row['root']} | {row['lemma']} | {row['piel_count']} "
            f"| {row['total']} | {row['hif_pct']}% | {row['top_gloss']} |\n")
    lines.append('\n')

    lines.append('## 6. Semantic Function Categories\n\n')
    lines.append('| Category | Count | % |\n|---|---|---|\n')
    for _, row in sem_df.iterrows():
        lines.append(f"| {row['category']} | {row['count']:,} | {row['pct']}% |\n")
    lines.append('\n')

    report_path = out_dir / 'piel_report.md'
    report_path.write_text(''.join(lines), encoding='utf-8')
    print(f"\nReport saved: {report_path}")
    return report_path
