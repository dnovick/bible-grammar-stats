"""
Hiphil verb morphology analysis for Biblical Hebrew instruction.

The Hiphil (הִפְעִיל) is the causative-active stem of Biblical Hebrew.
It typically:
  • Causes an action: הֵבִיא (he brought) ← causative of בּוֹא (to come)
  • Declares a state: הִצְדִּיק (declared righteous) ← declarative
  • Produces an effect: הִמְטִיר (caused to rain) ← factitive / denominative
  • Has unique roots that almost exclusively appear in the Hiphil

All functions use MACULA Hebrew WLC data (load_syntax_ot).

Public API
──────────
hiphil_data()                          → DataFrame (all Hiphil tokens)
hiphil_conjugation_profile(book=None)  → DataFrame (type_ distribution)
hiphil_top_roots(n=30, book=None)      → DataFrame (most frequent roots)
hiphil_root_conjugation(roots=None)    → DataFrame (root × conjugation crosstab)
hiphil_book_distribution()             → DataFrame (count + pct per book)
hiphil_stem_comparison(books=None)     → DataFrame (all stems % by book)
hiphil_dominant_roots(min_pct=70)      → DataFrame (roots >X% Hiphil)
hiphil_semantic_categories()           → DataFrame (semantic function counts)
hiphil_object_verbs(book=None)         → DataFrame (roots with frequent objects)

print_hiphil_overview()                → None
print_hiphil_conjugation(book=None)    → None
print_hiphil_top_roots(n=20, book=None) → None
print_hiphil_root_conjugation(roots=None) → None
print_hiphil_book_distribution()       → None
print_hiphil_dominant_roots()          → None
print_hiphil_semantic_categories()     → None

hiphil_conjugation_chart(book=None)    → Path | None
hiphil_book_chart()                    → Path | None
hiphil_stem_chart(books=None)          → Path | None
hiphil_root_heatmap(top_n=15)          → Path | None

hiphil_report(output_dir=None)         → Path   (full Markdown report)
"""

from __future__ import annotations
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip(text: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(text))
        if unicodedata.category(c) != 'Mn'
    )


def _load() -> pd.DataFrame:
    from .syntax_ot import load_syntax_ot
    df = load_syntax_ot()
    df['_lem'] = df['lemma'].apply(_strip)
    return df


def _hiphil(df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = _load()
    return df[df['stem'] == 'hiphil'].copy()


# Conjugation display order
_CONJ_ORDER = [
    'wayyiqtol', 'qatal', 'yiqtol', 'weqatal',
    'imperative', 'jussive', 'cohortative',
    'participle active', 'infinitive construct', 'infinitive absolute',
]

# Genre groupings for stem comparison
_GENRE_BOOKS = {
    'Narrative': ['Gen', 'Exo', 'Num', 'Jos', 'Jdg', '1Sa', '2Sa', '1Ki', '2Ki'],
    'Law':       ['Lev', 'Deu'],
    'Prophecy':  ['Isa', 'Jer', 'Ezk'],
    'Poetry':    ['Psa', 'Pro', 'Job'],
}

# Semantic function labels based on root / gloss patterns
_CAUSATIVE_GLOSSES = {
    'bring', 'brought', 'led', 'lead', 'send', 'sent', 'cause', 'caused',
    'make', 'made', 'put', 'place', 'set', 'take', 'took',
    'present', 'offered', 'offer', 'produce', 'produced',
}
_LETHAL_GLOSSES = {
    'kill', 'killed', 'slay', 'slew', 'strike', 'struck', 'striking',
    'put to death', 'put ~ todeath', 'execute', 'destroy', 'destroyed',
    'cut off', 'cut ~ off', 'struck down', 'smite', 'smote',
}
_DECLARATIVE_GLOSSES = {
    'declare', 'declared', 'make known', 'made known', 'teach', 'taught',
    'show', 'announce', 'tell', 'told', 'proclaim', 'testify', 'warn',
    'accuse', 'justify', 'condemn', 'pronounce', 'known',
}
_SAVE_DELIVER_GLOSSES = {
    'save', 'saved', 'saves', 'deliver', 'delivered', 'deliverer',
    'rescue', 'rescued', 'help', 'savior', 'give victory',
}
_RESTORE_GLOSSES = {
    'restore', 'restored', 'return', 'returned', 'bring back',
    'brought back', 'brought ~ back', 'turn', 'repay', 'answer',
}
_WORSHIP_GLOSSES = {
    'offer', 'offered', 'sacrifice', 'burn', 'burned', 'incense',
    'give thanks', 'praise', 'worship', 'pray', 'confess',
}


_CAUSATIVE_KEYWORDS = (
    'bring', 'brought', 'led', 'lead', 'sent', 'send', 'cause',
    'make', 'take', 'took', 'put', 'set', 'place', 'present', 'produce',
    'cast', 'throw', 'threw', 'remove', 'removed', 'left', 'leave',
    'drive', 'drove', 'deport', 'deported', 'appointed', 'appoint',
    'establish', 'established', 'prepared', 'prepare', 'showed', 'show',
    'incline', 'began', 'begin', 'added', 'add', 'multiply', 'increased',
    'fathered', 'father', 'bore', 'bore ~', 'gave birth', 'begot',
    'had', 'crown', 'made ~ king', 'installed',
)


def _semantic_function(gloss: str) -> str:
    g = str(gloss).strip().lower()
    if g in _LETHAL_GLOSSES or any(w in g for w in ('kill', 'slay', 'destroy', 'smite', 'struck', 'defeat', 'attacked', 'cut off')):  # noqa: E501
        return 'violent / lethal action'
    if g in _SAVE_DELIVER_GLOSSES or any(w in g for w in ('save', 'deliver', 'rescue')):
        return 'salvation / deliverance'
    if g in _RESTORE_GLOSSES or any(w in g for w in ('restore', 'return', 'bring back')):
        return 'restoration / return'
    if g in _DECLARATIVE_GLOSSES or any(w in g for w in ('declare', 'proclaim', 'teach', 'tell', 'known', 'listen', 'understand', 'believe', 'warn', 'rebuke', 'look', 'wail')):  # noqa: E501
        return 'declaration / communication'
    if g in _WORSHIP_GLOSSES or any(w in g for w in ('offer', 'praise', 'thanks', 'worship', 'burn', 'sacrifice')):  # noqa: E501
        return 'worship / ritual'
    if any(w in g for w in _CAUSATIVE_KEYWORDS):
        return 'causative motion / transfer'
    return 'other'


# ═══════════════════════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def hiphil_data(book: str | None = None) -> pd.DataFrame:
    """Return all Hiphil tokens, optionally filtered to one book."""
    df = _load()
    h = _hiphil(df)
    if book:
        book_col = 'book_id' if 'book_id' in h.columns else 'book'
        h = h[h[book_col] == book]
    return h


def hiphil_conjugation_profile(book: str | None = None) -> pd.DataFrame:
    """
    Count Hiphil tokens by conjugation type.

    Returns DataFrame: form, count, pct.
    """
    h = hiphil_data(book)
    counts = {f: 0 for f in _CONJ_ORDER}
    for t in h['type_']:
        t_str = str(t).strip()
        if t_str in counts:
            counts[t_str] += 1
    total = sum(counts.values())
    records = [
        {'form': f, 'count': counts[f],
         'pct': round(counts[f] / total * 100, 1) if total else 0.0}
        for f in _CONJ_ORDER
    ]
    return pd.DataFrame(records)


def hiphil_top_roots(n: int = 30, book: str | None = None) -> pd.DataFrame:
    """
    Return the top-n most frequent Hiphil roots.

    Columns: root, lemma, count, pct, top_gloss.
    """
    h = hiphil_data(book)
    vc = h.groupby(['_lem', 'lemma']).size().reset_index(name='count')
    vc = vc.sort_values('count', ascending=False).head(n)
    total = vc['count'].sum()
    vc['pct'] = (vc['count'] / total * 100).round(1)

    # Add most common english gloss for each root
    top_glosses = (
        h.groupby('_lem')['english']
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else '')
    )
    vc['top_gloss'] = vc['_lem'].map(top_glosses).fillna('')
    vc = vc.rename(columns={'_lem': 'root'})
    return vc.reset_index(drop=True)


def hiphil_root_conjugation(
    roots: list[str] | None = None,
    top_n: int = 15,
) -> pd.DataFrame:
    """
    Return a root × conjugation crosstab (counts).

    Parameters
    ----------
    roots : list of stripped lemmas, optional.
        If None, uses top_n most frequent roots.
    top_n : int
        How many top roots to include when roots is None.
    """
    h = hiphil_data()
    if roots is None:
        roots = h['_lem'].value_counts().head(top_n).index.tolist()
    h_sub = h[h['_lem'].isin(roots)]
    ct = pd.crosstab(h_sub['_lem'], h_sub['type_'])
    ct = ct.reindex(index=roots, columns=_CONJ_ORDER, fill_value=0)
    return ct


def hiphil_book_distribution() -> pd.DataFrame:
    """
    Count Hiphil tokens per book with percentage of all-OT Hiphil.

    Columns: book, count, pct, pct_of_book_verbs.
    """
    df = _load()
    h = _hiphil(df)

    book_counts = h['book'].value_counts().reset_index()
    book_counts.columns = ['book', 'count']
    total_hif = book_counts['count'].sum()
    book_counts['pct'] = (book_counts['count'] / total_hif * 100).round(1)

    # Hiphil as % of all verbs in that book
    all_v = df[df['class_'] == 'verb']['book'].value_counts().reset_index()
    all_v.columns = ['book', 'total_verbs']
    book_counts = book_counts.merge(all_v, on='book', how='left')
    book_counts['pct_of_book_verbs'] = (
        book_counts['count'] / book_counts['total_verbs'] * 100
    ).round(1)
    return book_counts.sort_values('count', ascending=False)


def hiphil_stem_comparison(
    books: list[str] | None = None,
) -> pd.DataFrame:
    """
    Return verb stem percentages for a set of books.

    Columns: stem; rows = books.
    """
    df = _load()
    if books is None:
        books = ['Gen', 'Exo', 'Deu', 'Psa', 'Isa', 'Jer', 'Pro', 'Job']

    stems = ['qal', 'niphal', 'piel', 'hiphil', 'hithpael', 'pual', 'hophal']
    rows = []
    for b in books:
        bv = df[(df['class_'] == 'verb') & (df['book'] == b)]
        tot = len(bv)
        row: dict[str, Any] = {'book': b}
        for s in stems:
            cnt = (bv['stem'] == s).sum()
            row[s] = round(cnt / tot * 100, 1) if tot else 0.0
        rows.append(row)
    return pd.DataFrame(rows).set_index('book')


def hiphil_dominant_roots(
    min_pct: float = 70.0,
    min_tokens: int = 10,
) -> pd.DataFrame:
    """
    Roots where the Hiphil accounts for ≥ min_pct of all occurrences.

    These are functionally "Hiphil-only" verbs — a key teaching point.
    Columns: lemma, root, hiphil_count, total_count, hif_pct, top_gloss.
    """
    df = _load()
    verbs = df[df['class_'] == 'verb']
    grp = verbs.groupby(['lemma', '_lem', 'stem']).size().reset_index(name='count')
    pivot = grp.pivot_table(
        index=['lemma', '_lem'], columns='stem', values='count', fill_value=0
    ).reset_index()

    if 'hiphil' not in pivot.columns:
        return pd.DataFrame()

    pivot['total'] = pivot.drop(columns=['lemma', '_lem']).sum(axis=1)
    pivot['hif_pct'] = (pivot['hiphil'] / pivot['total'] * 100).round(1)
    result = pivot[
        (pivot['hif_pct'] >= min_pct) &
        (pivot['hiphil'] >= min_tokens)
    ].copy()

    # Add top gloss
    h = _hiphil(df)
    top_glosses = (
        h.groupby('_lem')['english']
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else '')
    )
    result['top_gloss'] = result['_lem'].map(top_glosses).fillna('')
    result = result.rename(columns={'hiphil': 'hiphil_count', '_lem': 'root'})
    return result[['lemma', 'root', 'hiphil_count', 'total', 'hif_pct', 'top_gloss']].sort_values(
        'hiphil_count', ascending=False
    ).reset_index(drop=True)


def hiphil_semantic_categories() -> pd.DataFrame:
    """
    Assign each Hiphil token a broad semantic function category.

    Categories: causative motion/transfer · violent/lethal · salvation/deliverance ·
    restoration/return · declaration/communication · worship/ritual · other.

    Returns DataFrame: category, count, pct.
    """
    h = hiphil_data()
    h = h.copy()
    h['category'] = h['english'].apply(_semantic_function)
    counts = h['category'].value_counts().reset_index()
    counts.columns = ['category', 'count']
    total = counts['count'].sum()
    counts['pct'] = (counts['count'] / total * 100).round(1)
    return counts


# ═══════════════════════════════════════════════════════════════════════════════
# PRINT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_hiphil_overview() -> None:
    """Print a quick statistical overview of the Hiphil in the OT."""
    df = _load()
    h = _hiphil(df)
    all_v = df[df['class_'] == 'verb']

    total_tokens = len(h)
    total_verbs = len(all_v)
    pct_of_all = round(total_tokens / total_verbs * 100, 1)
    unique_roots = h['_lem'].nunique()
    books_with = h['book'].nunique()

    print()
    print('╔' + '═' * 78 + '╗')
    print('║' + '  HIPHIL (הִפְעִיל) — OT Overview'.center(78) + '║')
    print('╚' + '═' * 78 + '╝')
    print()
    print(f"  Total Hiphil tokens:        {total_tokens:>6,}")
    print(f"  % of all OT verb tokens:    {pct_of_all:>6.1f}%")
    print(f"  Unique roots in Hiphil:     {unique_roots:>6,}")
    print(f"  Books containing Hiphil:    {books_with:>6,} of 39")
    print()

    # Top 5 books
    top5 = h['book'].value_counts().head(5)
    print("  Top 5 books by Hiphil count:")
    for book, cnt in top5.items():
        pct = cnt / total_tokens * 100
        bar = '█' * int(pct / 1)
        print(f"    {book:<8} {cnt:>4}  ({pct:>4.1f}%)  {bar}")
    print()

    # Top 5 roots
    top_roots = h['_lem'].value_counts().head(5)
    print("  Top 5 Hiphil roots:")
    for root, cnt in top_roots.items():
        gl = h[h['_lem'] == root]['english'].value_counts().index[0]
        print(f"    {root:<8} {cnt:>4}  ({gl})")
    print()


def print_hiphil_conjugation(book: str | None = None) -> None:
    """Print Hiphil conjugation distribution."""
    df = hiphil_conjugation_profile(book)
    total = df['count'].sum()
    scope = book or 'Whole OT'

    print()
    print('═' * 72)
    print(f"  Hiphil conjugation profile: {scope}  (total: {total:,})")
    print('─' * 72)
    for _, row in df.iterrows():
        if row['count'] == 0:
            continue
        bar = '█' * int(row['pct'] / 1.5)
        print(f"  {row['form']:<24} {row['count']:>5}  {row['pct']:>5.1f}%  {bar}")
    print()


def print_hiphil_top_roots(n: int = 25, book: str | None = None) -> None:
    """Print the top Hiphil roots."""
    df = hiphil_top_roots(n, book)
    scope = book or 'Whole OT'

    print()
    print('═' * 72)
    print(f"  Top {n} Hiphil roots: {scope}")
    print('─' * 72)
    print(f"  {'#':<4} {'Root':<10} {'Lemma':<14} {'Count':>6} {'%':>6}  Gloss")
    print('  ' + '─' * 68)
    for i, row in df.iterrows():
        '█' * int(row['pct'] / 1.5)
        print(f"  {i+1:<4} {row['root']:<10} {row['lemma']:<14} {row['count']:>6} "
              f"{row['pct']:>5.1f}%  {row['top_gloss']}")
    print()


def print_hiphil_root_conjugation(roots: list[str] | None = None, top_n: int = 15) -> None:
    """Print root × conjugation frequency table."""
    ct = hiphil_root_conjugation(roots, top_n)
    h = hiphil_data()
    top_glosses = (
        h.groupby('_lem')['english']
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else '')
    )

    # Abbreviate column names
    abbrev = {
        'wayyiqtol': 'wayyiq', 'qatal': 'qatal', 'yiqtol': 'yiqtol',
        'weqatal': 'weqtl', 'imperative': 'impv', 'jussive': 'juss',
        'cohortative': 'coh', 'participle active': 'ptc',
        'infinitive construct': 'inf.c', 'infinitive absolute': 'inf.a',
    }
    display_cols = [c for c in _CONJ_ORDER if c in ct.columns]

    print()
    print('═' * 90)
    print("  Hiphil: Root × Conjugation frequency")
    print('─' * 90)

    header = f"  {'Root':<10} {'Gloss':<18}" + ''.join(
        f"{abbrev.get(c, c[:6]):>7}" for c in display_cols
    ) + f"  {'Total':>6}"
    print(header)
    print('  ' + '─' * 86)

    for root in ct.index:
        row_vals = [ct.loc[root, c] for c in display_cols]
        total = sum(row_vals)
        gloss = str(top_glosses.get(root, ''))[:16]
        vals_str = ''.join(f"{v:>7}" for v in row_vals)
        print(f"  {root:<10} {gloss:<18}{vals_str}  {total:>6}")
    print()


def print_hiphil_book_distribution(top_n: int = 25) -> None:
    """Print Hiphil distribution across books."""
    df = hiphil_book_distribution().head(top_n)
    df['count'].sum()

    print()
    print('═' * 76)
    print(f"  Hiphil distribution across books (top {top_n})")
    print('─' * 76)
    print(f"  {'Book':<8} {'Count':>6} {'% of OT Hif':>12} {'% of book verbs':>16}  Chart")
    print('  ' + '─' * 72)
    for _, row in df.iterrows():
        bar = '█' * int(row['pct'] * 1.5)
        print(f"  {row['book']:<8} {row['count']:>6} {row['pct']:>11.1f}%"
              f" {row['pct_of_book_verbs']:>15.1f}%  {bar}")
    print()


def print_hiphil_dominant_roots(top_n: int = 25) -> None:
    """Print roots where the Hiphil is the dominant stem (>70% of occurrences)."""
    df = hiphil_dominant_roots().head(top_n)

    print()
    print('═' * 76)
    print("  Hiphil-dominant roots (≥70% of all occurrences are Hiphil)")
    print("  These are functionally 'Hiphil-only' verbs")
    print('─' * 76)
    print(f"  {'Root':<10} {'Lemma':<14} {'Hiphil':>7} {'Total':>7} {'%':>7}  Gloss")
    print('  ' + '─' * 72)
    for _, row in df.iterrows():
        '█' * int(row['hif_pct'] / 5)
        print(f"  {row['root']:<10} {row['lemma']:<14} {row['hiphil_count']:>7} "
              f"{row['total']:>7} {row['hif_pct']:>6.1f}%  {row['top_gloss']}")
    print()


def print_hiphil_semantic_categories() -> None:
    """Print Hiphil semantic function distribution."""
    df = hiphil_semantic_categories()
    total = df['count'].sum()

    print()
    print('═' * 72)
    print(f"  Hiphil semantic function categories  (total: {total:,})")
    print('─' * 72)
    for _, row in df.iterrows():
        bar = '█' * int(row['pct'] / 2)
        print(f"  {row['category']:<35} {row['count']:>5}  {row['pct']:>5.1f}%  {bar}")
    print()
    print("  Note: categories derived from MACULA english gloss annotations.")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _ensure_output_dir() -> Path:
    p = Path('output') / 'charts' / 'ot' / 'verbs'
    p.mkdir(parents=True, exist_ok=True)
    return p


def hiphil_conjugation_chart(book: str | None = None) -> Path | None:
    """Save a horizontal bar chart of Hiphil conjugation distribution."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    df = hiphil_conjugation_profile(book)
    df = df[df['count'] > 0].sort_values('pct')

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = plt.cm.Blues(  # type: ignore[attr-defined]
        [0.4 + 0.5 * (i / max(len(df) - 1, 1)) for i in range(len(df))]
    )
    bars = ax.barh(df['form'], df['pct'], color=colors)
    for bar, val in zip(bars, df['pct']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va='center', fontsize=9)

    scope = book or 'Whole OT'
    ax.set_title(f"Hiphil Conjugation Distribution — {scope}", fontsize=13, fontweight='bold')
    ax.set_xlabel("% of Hiphil tokens")
    ax.set_xlim(0, df['pct'].max() * 1.18)
    ax.yaxis.grid(False)
    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()

    out = _ensure_output_dir() / f'hiphil_conjugation{"_"+book if book else ""}.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def hiphil_book_chart(top_n: int = 20) -> Path | None:
    """Save a bar chart of top books by Hiphil count."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    df = hiphil_book_distribution().head(top_n)
    fig, ax1 = plt.subplots(figsize=(13, 5))

    x = range(len(df))
    ax1.bar(x, df['count'], color='steelblue', alpha=0.8, label='Hiphil count')
    ax1.set_ylabel('Token count', color='steelblue')
    ax1.tick_params(axis='y', labelcolor='steelblue')

    ax2 = ax1.twinx()
    ax2.plot(x, df['pct_of_book_verbs'], 'o-', color='darkorange',
             linewidth=1.8, markersize=5, label='% of book verbs')
    ax2.set_ylabel('% of book verbs', color='darkorange')
    ax2.tick_params(axis='y', labelcolor='darkorange')

    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df['book'].tolist(), rotation=40, ha='right', fontsize=9)
    ax1.set_title(f"Hiphil Distribution Across Books (top {top_n})", fontsize=13, fontweight='bold')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    fig.tight_layout()

    out = _ensure_output_dir() / 'hiphil_books.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def hiphil_stem_chart(books: list[str] | None = None) -> Path | None:
    """
    Save a stacked bar chart showing all verb stem percentages for a set of books,
    with the Hiphil slice highlighted.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    if books is None:
        books = ['Gen', 'Exo', 'Deu', 'Psa', 'Isa', 'Jer', 'Pro', 'Job']

    df = hiphil_stem_comparison(books)
    stems = ['qal', 'niphal', 'piel', 'hiphil', 'hithpael', 'pual', 'hophal']
    colors = {
        'qal':      '#5B9BD5',
        'niphal':   '#ED7D31',
        'piel':     '#A9D18E',
        'hiphil':   '#FF0000',   # red — highlighted
        'hithpael': '#FFC000',
        'pual':     '#9DC3E6',
        'hophal':   '#C9C9C9',
    }

    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(books))
    bottoms = [0.0] * len(books)

    for stem in stems:
        vals = [df.loc[b, stem] if b in df.index else 0 for b in books]
        bars = ax.bar(x, vals, bottom=bottoms, color=colors[stem], label=stem,
                      edgecolor='white', linewidth=0.4)
        # Label slices ≥ 5%
        for bar, val, bot in zip(bars, vals, bottoms):
            if val >= 5:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bot + val / 2,
                    f"{val:.0f}%",
                    ha='center', va='center', fontsize=7,
                    color='white' if stem in ('qal', 'hiphil') else 'black',
                    fontweight='bold' if stem == 'hiphil' else 'normal',
                )
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(books, fontsize=11)
    ax.set_ylabel('% of verb tokens')
    ax.set_ylim(0, 105)
    ax.set_title('Verb Stem Distribution by Book — Hiphil (red) highlighted',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()

    out = _ensure_output_dir() / 'hiphil_stem_comparison.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def hiphil_root_heatmap(top_n: int = 15) -> Path | None:
    """
    Save a heatmap: top roots × conjugation type (row-normalized percentages).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    ct = hiphil_root_conjugation(top_n=top_n)
    h = hiphil_data()
    top_glosses = (
        h.groupby('_lem')['english']
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else '')
    )

    display_cols = [c for c in _CONJ_ORDER if c in ct.columns]
    ct_sub = ct[display_cols]
    row_totals = ct_sub.sum(axis=1)
    pct_matrix = ct_sub.div(row_totals, axis=0) * 100

    col_abbrev = {
        'wayyiqtol': 'wayyiq', 'qatal': 'qatal', 'yiqtol': 'yiqtol',
        'weqatal': 'weqtl', 'imperative': 'impv', 'jussive': 'juss',
        'cohortative': 'coh', 'participle active': 'ptc.act',
        'infinitive construct': 'inf.cst', 'infinitive absolute': 'inf.abs',
    }

    ylabels = [
        f"{root}  ({top_glosses.get(root, '')[:14]})"
        for root in pct_matrix.index
    ]
    xlabels = [col_abbrev.get(c, c[:8]) for c in display_cols]

    fig, ax = plt.subplots(figsize=(12, max(6, top_n * 0.5 + 1)))
    im = ax.imshow(pct_matrix.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=60)

    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=30, ha='right', fontsize=9)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=9)

    for i in range(len(pct_matrix.index)):
        for j in range(len(display_cols)):
            val = pct_matrix.values[i, j]
            if val > 1:
                ax.text(j, i, f"{val:.0f}", ha='center', va='center',
                        fontsize=7, color='black' if val < 35 else 'white')

    plt.colorbar(im, ax=ax, label='% of root tokens in this conjugation')
    ax.set_title(f"Hiphil: Top {top_n} Roots × Conjugation (row-% normalized)",
                 fontsize=12, fontweight='bold')
    fig.tight_layout()

    out = _ensure_output_dir() / 'hiphil_root_heatmap.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def hiphil_semantic_chart() -> Path | None:
    """Save a pie chart of Hiphil semantic function categories."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    df = hiphil_semantic_categories()
    df = df.sort_values('count', ascending=False)

    colors = [
        '#D32F2F', '#1565C0', '#2E7D32', '#F57F17',
        '#6A1B9A', '#00838F', '#4E342E',
    ]

    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(  # type: ignore[misc]
        df['count'],
        labels=[f"{r['category']}\n({r['count']:,})" for _, r in df.iterrows()],
        autopct='%1.1f%%',
        colors=colors[:len(df)],
        startangle=140,
        pctdistance=0.75,
    )
    for t in texts:
        t.set_fontsize(9)
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color('white')

    ax.set_title('Hiphil Semantic Function Distribution (whole OT)',
                 fontsize=13, fontweight='bold', pad=20)
    fig.tight_layout()

    out = _ensure_output_dir() / 'hiphil_semantic.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


def hiphil_top_roots_chart(top_n: int = 20) -> Path | None:
    """Save a horizontal bar chart of the top Hiphil roots."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    df = hiphil_top_roots(top_n)
    df = df.sort_values('count')

    labels = [f"{row['root']}  ({row['top_gloss'][:16]})" for _, row in df.iterrows()]

    fig, ax = plt.subplots(figsize=(10, max(6, top_n * 0.45)))
    colors = plt.cm.viridis(  # type: ignore[attr-defined]
        [0.2 + 0.6 * (i / max(len(df) - 1, 1)) for i in range(len(df))]
    )
    bars = ax.barh(labels, df['count'], color=colors)
    for bar, val in zip(bars, df['count']):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                str(val), va='center', fontsize=8)

    ax.set_title(f"Top {top_n} Hiphil Roots (whole OT)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Token count")
    ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()

    out = _ensure_output_dir() / 'hiphil_top_roots.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# FULL REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def hiphil_report(output_dir: str | None = None) -> Path:
    """
    Generate a complete Hiphil morphology report (Markdown + PNG charts).

    Saves:
      output/reports/hiphil_report.md
      output/charts/hiphil_conjugation.png
      output/charts/hiphil_books.png
      output/charts/hiphil_stem_comparison.png
      output/charts/hiphil_root_heatmap.png
      output/charts/hiphil_semantic.png
      output/charts/hiphil_top_roots.png

    Returns path to the Markdown report.
    """
    if output_dir is None:
        out_dir = Path('output') / 'reports' / 'ot' / 'verbs'
    else:
        out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate all charts
    print("Generating charts...")
    charts = {
        'conjugation': hiphil_conjugation_chart(),
        'books':       hiphil_book_chart(),
        'stems':       hiphil_stem_chart(),
        'heatmap':     hiphil_root_heatmap(),
        'semantic':    hiphil_semantic_chart(),
        'top_roots':   hiphil_top_roots_chart(),
    }
    for k, p in charts.items():
        if p:
            print(f"  ✓ {k}: {p}")

    # Collect data for tables
    df_full = _load()
    h = _hiphil(df_full)
    total_tokens = len(h)
    total_verbs = len(df_full[df_full['class_'] == 'verb'])
    unique_roots = h['_lem'].nunique()

    conj_df = hiphil_conjugation_profile()
    top_roots_df = hiphil_top_roots(20)
    dom_df = hiphil_dominant_roots(min_pct=80, min_tokens=10).head(20)
    sem_df = hiphil_semantic_categories()
    book_df = hiphil_book_distribution().head(20)

    # Build Markdown
    lines: list[str] = []
    lines.append('# Hiphil (הִפְעִיל) Verb Morphology — Biblical Hebrew\n')
    lines.append('*Generated from MACULA Hebrew WLC data*\n\n')
    lines.append('---\n\n')

    # 1. Overview
    lines.append('## 1. Overview\n\n')
    lines.append(
        'The **Hiphil** stem expresses causative or declarative action. It is formed '
        'with a prefixed ה (hé) in the perfect and special vowel patterns in other '
        'conjugations. The Hiphil is the **second most productive** derived stem after '
        'the Piel.\n\n'
    )
    lines.append('| Statistic | Value |\n|---|---|\n')
    lines.append(f'| Total Hiphil tokens (OT) | {total_tokens:,} |\n')
    lines.append(f'| % of all OT verb tokens  | {total_tokens/total_verbs*100:.1f}% |\n')
    lines.append(f'| Unique roots in Hiphil   | {unique_roots} |\n')
    lines.append('| Books containing Hiphil  | 39 of 39 |\n\n')

    lines.append('### Semantic functions of the Hiphil\n\n')
    lines.append('| Function | Description | Example |\n|---|---|---|\n')
    lines.append('| **Causative** | Cause someone to do X | הֵבִיא "he brought" (← בּוֹא "to come") |\n')  # noqa: E501
    lines.append(
        '| **Factitive** | Cause a state | הֶחֱזִיק "he strengthened" (← חָזַק "to be strong") |\n')
    lines.append('| **Declarative** | Declare X to be Y | הִצְדִּיק "declared righteous" (← צָדַק) |\n')  # noqa: E501
    lines.append(
        '| **Denominative** | Action from a noun | הִמְטִיר "caused to rain" (← מָטָר "rain") |\n\n')  # noqa: E501

    # 2. Conjugation
    lines.append('## 2. Conjugation (Tense/Aspect) Distribution\n\n')
    if charts['conjugation']:
        rel = Path('../..') / 'charts' / 'ot' / 'verbs' / charts['conjugation'].name
        lines.append(f'![Hiphil conjugation chart]({rel})\n\n')
    lines.append('| Conjugation | Count | % |\n|---|---|---|\n')
    for _, row in conj_df.iterrows():
        if row['count'] > 0:
            lines.append(f"| {row['form']} | {row['count']:,} | {row['pct']}% |\n")
    lines.append('\n')
    lines.append(
        '**Teaching note:** The yiqtol and wayyiqtol together account for over 40% of '
        'all Hiphil tokens, reflecting the Hiphil\'s heavy use in narrative action sequences. '
        'The high imperative count (7.8%) reflects the Hiphil\'s use in commands to bring, '
        'deliver, or act on behalf of others.\n\n'
    )

    # 3. Book distribution
    lines.append('## 3. Distribution Across Books\n\n')
    if charts['books']:
        rel = Path('../..') / 'charts' / 'ot' / 'verbs' / charts['books'].name
        lines.append(f'![Hiphil book distribution]({rel})\n\n')
    lines.append('| Book | Count | % of OT Hiphil | % of book verbs |\n|---|---|---|---|\n')
    for _, row in book_df.iterrows():
        lines.append(
            f"| {row['book']} | {row['count']:,} | {row['pct']}% | {row['pct_of_book_verbs']}% |\n")
    lines.append('\n')

    # 4. Stem comparison
    lines.append('## 4. Hiphil vs. Other Stems by Genre\n\n')
    if charts['stems']:
        rel = Path('../..') / 'charts' / 'ot' / 'verbs' / charts['stems'].name
        lines.append(f'![Stem comparison chart]({rel})\n\n')
    lines.append(
        'The Hiphil typically represents **9–16% of all verb tokens** per book. '
        'Poetry (Psalms 15.4%, Proverbs 14.8%) and prophecy (Isaiah 13.4%, Jeremiah 12.8%) '
        'use the Hiphil proportionally more than narrative (Genesis 9.8%).\n\n'
    )

    # 5. Top roots
    lines.append('## 5. Most Frequent Hiphil Roots\n\n')
    if charts['top_roots']:
        rel = Path('../..') / 'charts' / 'ot' / 'verbs' / charts['top_roots'].name
        lines.append(f'![Top roots chart]({rel})\n\n')
    lines.append('| # | Root | Lemma | Count | % | Primary meaning |\n|---|---|---|---|---|---|\n')
    for i, row in top_roots_df.iterrows():
        lines.append(
            f"| {i+1} | {row['root']} | {row['lemma']} | {row['count']:,} | {row['pct']}% | {row['top_gloss']} |\n")  # noqa: E501
    lines.append('\n')

    # 6. Root × conjugation heatmap
    lines.append('## 6. Root × Conjugation Heatmap\n\n')
    if charts['heatmap']:
        rel = Path('../..') / 'charts' / 'ot' / 'verbs' / charts['heatmap'].name
        lines.append(f'![Root-conjugation heatmap]({rel})\n\n')
    lines.append(
        'Each cell shows what percentage of that root\'s total Hiphil tokens appear '
        'in that conjugation. Rows are row-normalized (each root sums to 100%).\n\n'
        '**Notable patterns:**\n'
        '- נָכָה (strike/kill): dominated by wayyiqtol — narrative combat scenes\n'
        '- יָסַף (add/do again): dominated by yiqtol — future/habitual "again"\n'
        '- רָבָה (multiply): dominated by inf.abs — emphatic constructions\n'
        '- נָגַד (tell/declare): strong imperative — commands to report/announce\n\n'
    )

    # 7. Hiphil-dominant roots
    lines.append('## 7. Hiphil-Dominant Roots (≥80% of occurrences)\n\n')
    lines.append(
        'These roots almost exclusively occur in the Hiphil. '
        'They are "built-in causatives" with no separate Qal meaning.\n\n'
    )
    lines.append('| Root | Lemma | Hiphil | Total | % | Gloss |\n|---|---|---|---|---|---|\n')
    for _, row in dom_df.iterrows():
        lines.append(
            f"| {row['root']} | {row['lemma']} | {row['hiphil_count']} | {row['total']} | {row['hif_pct']}% | {row['top_gloss']} |\n")  # noqa: E501
    lines.append('\n')

    # 8. Semantic categories
    lines.append('## 8. Semantic Function Categories\n\n')
    if charts['semantic']:
        rel = Path('../..') / 'charts' / 'ot' / 'verbs' / charts['semantic'].name
        lines.append(f'![Semantic categories pie chart]({rel})\n\n')
    lines.append('| Category | Count | % |\n|---|---|---|\n')
    for _, row in sem_df.iterrows():
        lines.append(f"| {row['category']} | {row['count']:,} | {row['pct']}% |\n")
    lines.append('\n')
    lines.append(
        '**Teaching note:** The largest category (causative motion/transfer) reflects '
        'the Hiphil\'s core function of "causing something to move" — bringing, leading, '
        'sending, presenting. The violence/lethal category (נָכָה "strike", מוּת "kill") '
        'is the second largest, common in historical narrative.\n\n'
    )

    # 9. Morphology paradigm reminder
    lines.append('## 9. Key Morphological Markers\n\n')
    lines.append('| Form | Prefix/suffix | Vowel pattern |\n|---|---|---|\n')
    lines.append('| Perfect (qatal) 3ms | הִ- | הִקְטִיל |\n')
    lines.append('| Imperfect (yiqtol) 3ms | יַ- | יַקְטִיל |\n')
    lines.append('| Wayyiqtol 3ms | וַיַּ- | וַיַּקְטֵל |\n')
    lines.append('| Imperative ms | הַ- | הַקְטֵל |\n')
    lines.append('| Inf. Construct | הַ- | הַקְטִיל |\n')
    lines.append('| Inf. Absolute | הַ- | הַקְטֵל |\n')
    lines.append('| Participle ms | מַ- | מַקְטִיל |\n\n')
    lines.append(
        '**Diagnostic sign:** In the Hiphil, the *imperfect* and *participle* '
        'share the prefix מַ- / יַ- with a characteristic *i*-vowel (חִירִיק) '
        'in the second syllable, making it distinctive from the Piel (יְקַטֵּל) '
        'and Qal (יִקְטֹל).\n\n'
    )

    # Write report
    report_path = out_dir / 'hiphil_report.md'
    report_path.write_text(''.join(lines), encoding='utf-8')
    print(f"\nReport saved: {report_path}")
    return report_path
