"""
Hebrew poetry analysis: cola splitting, parallelism detection, and word-pair statistics.

Hebrew poetry is organized into poetic lines (verses) divided into cola (half-lines)
by the cantillation accent system embedded in the MT text. The Etnahta (U+0591)
marks the main mid-verse division (end of A-colon); the Silluq / Sof Pasuq marks
verse end (end of B- or final colon). Stronger disjunctive accents (Zaqef, Revia,
Tifha, Athnach) subdivide further, yielding C-cola in longer verses.

Parallelism types (after Lowth / Watson / Alter):
  synonymous  — A and B express the same idea with different words
  antithetic  — A and B express contrasting ideas
  synthetic   — B extends, intensifies, or completes A
  emblematic  — one colon is literal, one figurative (simile/metaphor)

This module detects cola boundaries from accents, extracts content-word pairs across
cola, scores lexical / semantic similarity, and classifies parallelism.

Public API
──────────
split_cola(verse_df)                → list[DataFrame] — one df per colon
verse_parallel_pairs(book, ch, vs) → DataFrame of A/B word pairs
parallelism_type(book, ch, vs)     → str classification
book_word_pairs(book)              → most common A/B parallel word pairs
print_verse_analysis(book, ch, vs) → formatted terminal output
parallel_word_pair_table(book)     → canonical parallel pair inventory
POETRY_BOOKS                       → list of primary Hebrew poetry books
"""

from __future__ import annotations
import re
import unicodedata
from pathlib import Path

import pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────

POETRY_BOOKS = ['Psa', 'Pro', 'Job', 'Sng', 'Lam', 'Ecc']

# Cantillation accent codepoints — disjunctive (clause-dividing) accents only
# Ordered roughly by strength (strongest first)
_ACCENT_NAMES = {
    0x0591: 'etnahta',       # main A/B divider — strongest mid-verse pause
    0x05C3: 'sof_pasuq',     # verse end
    0x0592: 'segolta',
    0x0593: 'shalshelet',
    0x0594: 'zaqef_qatan',
    0x0595: 'zaqef_gadol',
    0x0596: 'tifha',
    0x0597: 'revia',
    0x0598: 'zarqa',
    0x059A: 'yetiv',
    0x059B: 'tevir',
    0x059C: 'geresh',
    0x059D: 'geresh_muqdam',
    0x059E: 'gershayim',
    0x059F: 'qarney_para',
    0x05A0: 'telisha_gedola',
    0x05A1: 'pazer',
    0x05A3: 'munah',         # conjunctive (but sometimes marks sub-division)
    0x05A8: 'qadma',
    0x05A9: 'telisha_qetana',
    0x05AA: 'yerah_ben_yomo',
    0x05AB: 'ole',
    0x05AC: 'iluy',
    0x05AD: 'dehi',
    0x05AE: 'zinor',
    0x05AF: 'masora',
}

# Accents that mark primary (strong) cola boundaries
_PRIMARY_DIVIDERS = {0x0591}       # etnahta: always splits A from B
_VERSE_END = {0x05C3, 0x05BD}      # sof pasuq; meteg sometimes used at verse end

# Content-word parts of speech (exclude particles, conjunctions, prepositions)
_CONTENT_POS = {'noun', 'verb', 'adjective', 'adverb'}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _has_accent(text: str, codepoints: set[int]) -> bool:
    """Return True if the text contains any of the given accent codepoints."""
    return any(ord(c) in codepoints for c in text)


def _accent_in(text: str) -> set[int]:
    """Return set of accent codepoints present in the text."""
    return {ord(c) for c in text if ord(c) in _ACCENT_NAMES}


def _strip_cantillation(text: str) -> str:
    """Remove cantillation marks (but keep consonants and vowel points)."""
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn'
                   or ord(c) < 0x0591 or ord(c) > 0x05C7)


def _is_content_word(pos: str) -> bool:
    return str(pos).lower() in _CONTENT_POS


def _load_macula() -> pd.DataFrame:
    from .syntax_ot import load_syntax_ot
    return load_syntax_ot()


# ── Cola splitting ─────────────────────────────────────────────────────────────

def split_cola(verse_df: pd.DataFrame) -> list[pd.DataFrame]:
    """
    Split a verse DataFrame (one row per word) into cola based on cantillation
    accents embedded in the `text` column.

    Returns a list of DataFrames: [colon_A, colon_B] or [A, B, C] for longer
    verses. Each colon includes the word that carries the dividing accent.

    The primary split is at the Etnahta (U+0591). If no Etnahta is found,
    falls back to splitting on Zaqef Gadol (U+0595) or Revia (U+0597).
    Single-word or empty verses return [verse_df].
    """
    if verse_df.empty or len(verse_df) <= 1:
        return [verse_df]

    texts = verse_df['text'].tolist()

    # Find Etnahta position
    etnahta_idx = None
    for i, t in enumerate(texts):
        if _has_accent(t, _PRIMARY_DIVIDERS):
            etnahta_idx = i
            break

    if etnahta_idx is None:
        # Try secondary dividers: Zaqef Gadol, Revia, Tifha
        secondary = {0x0595, 0x0597, 0x0596}
        for i, t in enumerate(texts):
            if _has_accent(t, secondary) and i > 0:
                etnahta_idx = i
                break

    if etnahta_idx is None or etnahta_idx == len(texts) - 1:
        # No mid-verse split found or split is at last word
        return [verse_df]

    cola_a = verse_df.iloc[:etnahta_idx + 1].copy()
    remainder = verse_df.iloc[etnahta_idx + 1:].copy()

    # Check for a C-colon: secondary split in remainder (skip last word = verse end)
    c_idx = None
    for i, t in enumerate(remainder['text'].tolist()[:-1]):
        if _has_accent(t, {0x0595, 0x0597, 0x0596, 0x0594}):
            c_idx = i
            break

    if c_idx is not None and c_idx < len(remainder) - 1:
        cola_b = remainder.iloc[:c_idx + 1].copy()
        cola_c = remainder.iloc[c_idx + 1:].copy()
        return [cola_a, cola_b, cola_c]

    return [cola_a, remainder]


def verse_cola(book: str, chapter: int, verse: int) -> list[pd.DataFrame]:
    """Return the cola for a single verse."""
    df = _load_macula()
    v = df[(df['book'] == book) & (df['chapter'] == chapter) & (df['verse'] == verse)]
    return split_cola(v)


# ── Content-word extraction ───────────────────────────────────────────────────

def _content_words(colon_df: pd.DataFrame) -> pd.DataFrame:
    """Extract content words (nouns, verbs, adjectives) from a colon."""
    mask = colon_df['class_'].str.lower().isin({'noun', 'verb', 'adj', 'adv'})
    return colon_df[mask].copy()


# ── Semantic domain overlap ───────────────────────────────────────────────────

def _domains(colon_df: pd.DataFrame) -> set[str]:
    """Return the set of coredomain codes present in a colon's content words."""
    domains: set[str] = set()
    for raw in colon_df['coredomain'].dropna():
        for code in str(raw).split():
            if code.strip():
                domains.add(code.strip()[:3])  # top-level domain prefix
    return domains


def _lexical_overlap(a: pd.DataFrame, b: pd.DataFrame) -> float:
    """Fraction of lemmas shared between two cola (0.0–1.0)."""
    la = set(a['lemma'].dropna())
    lb = set(b['lemma'].dropna())
    if not la or not lb:
        return 0.0
    return len(la & lb) / len(la | lb)


def _domain_overlap(a: pd.DataFrame, b: pd.DataFrame) -> float:
    """Fraction of semantic domain codes shared between two cola."""
    da = _domains(a)
    db = _domains(b)
    if not da or not db:
        return 0.0
    return len(da & db) / len(da | db)


# ── Parallelism word pairs ─────────────────────────────────────────────────────

def verse_parallel_pairs(
    book: str,
    chapter: int,
    verse: int,
) -> pd.DataFrame:
    """
    Return a DataFrame of content-word pairs across cola A and B for a verse.

    For each content word in colon A, pairs it with each content word in colon B,
    yielding a row with:
      lemma_a, gloss_a, strong_a, lemma_b, gloss_b, strong_b,
      same_lemma (bool), domain_overlap (float), book, chapter, verse
    """
    cola = verse_cola(book, chapter, verse)
    if len(cola) < 2:
        return pd.DataFrame()

    a_words = _content_words(cola[0])
    b_words = _content_words(cola[1])

    if a_words.empty or b_words.empty:
        return pd.DataFrame()

    rows = []
    for _, wa in a_words.iterrows():
        for _, wb in b_words.iterrows():
            la = str(wa.get('lemma', ''))
            lb = str(wb.get('lemma', ''))
            da = set(str(wa.get('coredomain', '')).split())
            db = set(str(wb.get('coredomain', '')).split())
            dom_overlap = len(da & db) / len(da | db) if da | db else 0.0
            rows.append({
                'lemma_a':   la,
                'gloss_a':   str(wa.get('gloss', '')),
                'strong_a':  str(wa.get('strong_h', '')),
                'lemma_b':   lb,
                'gloss_b':   str(wb.get('gloss', '')),
                'strong_b':  str(wb.get('strong_h', '')),
                'same_lemma': la == lb and la != '',
                'domain_overlap': round(dom_overlap, 2),
                'book':    book,
                'chapter': chapter,
                'verse':   verse,
            })

    return pd.DataFrame(rows)


def book_word_pairs(
    book: str,
    *,
    min_count: int = 2,
    top_n: int = 40,
    content_only: bool = True,
) -> pd.DataFrame:
    """
    Most frequent A/B parallel word pairs across all verses in a book.

    Returns a DataFrame: lemma_a | gloss_a | lemma_b | gloss_b | count
    sorted by count descending.
    """
    df = _load_macula()
    verses = df[(df['book'] == book)][['chapter', 'verse']].drop_duplicates()

    all_pairs: list[pd.DataFrame] = []
    for _, row in verses.iterrows():
        try:
            pairs = verse_parallel_pairs(book, int(row['chapter']), int(row['verse']))
            if not pairs.empty:
                all_pairs.append(pairs)
        except Exception:
            pass

    if not all_pairs:
        return pd.DataFrame()

    combined = pd.concat(all_pairs, ignore_index=True)

    agg = (
        combined.groupby(['lemma_a', 'gloss_a', 'lemma_b', 'gloss_b'])
        .size().reset_index(name='count')
        .sort_values('count', ascending=False)
    )
    agg = agg[agg['count'] >= min_count]
    return agg.head(top_n).reset_index(drop=True)


# ── Parallelism classification ────────────────────────────────────────────────

def parallelism_type(
    book: str,
    chapter: int,
    verse: int,
) -> tuple[str, float]:
    """
    Classify the parallelism type for a verse.

    Returns (type_label, confidence_score) where type_label is one of:
      'synonymous'  — high lexical/domain overlap, same polarity
      'antithetic'  — low lexical overlap, antithetic markers present
      'synthetic'   — low overlap, no antithetic marker; B extends A
      'single_colon'— verse has only one colon (no split found)

    Confidence is 0.0–1.0; classifications below 0.3 are uncertain.

    This is a heuristic classifier — it captures the dominant type for clear
    cases and marks ambiguous ones as 'synthetic' (the catch-all).
    """
    cola = verse_cola(book, chapter, verse)
    if len(cola) < 2:
        return ('single_colon', 1.0)

    a_cw = _content_words(cola[0])
    b_cw = _content_words(cola[1])

    lex = _lexical_overlap(a_cw, b_cw)
    dom = _domain_overlap(a_cw, b_cw)

    # Antithetic markers: look for negation or antithetical conjunctions in B-colon
    b_text = ' '.join(cola[1]['text'].tolist())
    b_gloss = ' '.join(cola[1]['gloss'].fillna('').tolist()).lower()
    has_negation = any(neg in cola[1]['lemma'].tolist()
                       for neg in ['לֹא', 'אַל', 'בַּל'])
    has_antithetic_conj = 'but' in b_gloss or 'however' in b_gloss or 'yet' in b_gloss

    combined_score = (lex + dom) / 2

    if combined_score >= 0.35:
        return ('synonymous', round(combined_score, 2))
    elif has_negation or has_antithetic_conj:
        return ('antithetic', round(0.5 + combined_score, 2))
    else:
        return ('synthetic', round(0.4 - combined_score, 2))


# ── Book-level statistics ──────────────────────────────────────────────────────

def book_parallelism_stats(book: str) -> pd.DataFrame:
    """
    Count parallelism types across all verses in a book.

    Returns a DataFrame: type | count | pct
    """
    df = _load_macula()
    verses = df[(df['book'] == book)][['chapter', 'verse']].drop_duplicates()

    counts: dict[str, int] = {}
    for _, row in verses.iterrows():
        ptype, _ = parallelism_type(book, int(row['chapter']), int(row['verse']))
        counts[ptype] = counts.get(ptype, 0) + 1

    total = sum(counts.values())
    rows = [{'type': k, 'count': v, 'pct': round(v / total * 100, 1)}
            for k, v in sorted(counts.items(), key=lambda x: -x[1])]
    return pd.DataFrame(rows)


def compare_poetry_books(
    books: list[str] | None = None,
) -> pd.DataFrame:
    """
    Compare parallelism type distribution across multiple poetry books.
    Returns a pivot DataFrame: rows=type, cols=books, values=pct.
    """
    books = books or POETRY_BOOKS
    profiles: dict[str, pd.Series] = {}
    for b in books:
        try:
            stats = book_parallelism_stats(b)
            if not stats.empty:
                profiles[b] = stats.set_index('type')['pct']
        except Exception:
            pass

    if not profiles:
        return pd.DataFrame()

    result = pd.DataFrame(profiles).fillna(0).round(1)
    result['_avg'] = result.mean(axis=1)
    return result.sort_values('_avg', ascending=False).drop(columns='_avg')


# ── Terminal output ───────────────────────────────────────────────────────────

def print_verse_analysis(
    book: str,
    chapter: int,
    verse: int,
    *,
    show_accents: bool = False,
) -> None:
    """Print a formatted cola analysis for a single verse."""
    cola = verse_cola(book, chapter, verse)
    ptype, conf = parallelism_type(book, chapter, verse)

    ref = f"{book} {chapter}:{verse}"
    w = 72
    print(f"\n{'═'*w}")
    print(f"  {ref}  —  Parallelism: {ptype.upper()}  (confidence {conf:.2f})")
    print(f"{'═'*w}")

    labels = ['A', 'B', 'C']
    for i, colon in enumerate(cola):
        label = labels[i] if i < len(labels) else str(i + 1)
        words = colon['text'].tolist()
        glosses = colon['gloss'].fillna('').tolist()
        lemmas = colon['lemma'].fillna('').tolist()
        hebrew = ' '.join(words)
        print(f"\n  Colon {label}:  {hebrew}")
        print(f"  {'─'*60}")
        print(f"  {'Word':<25} {'Lemma':<18} {'Gloss'}")
        print(f"  {'─'*24} {'─'*17} {'─'*20}")
        for word, lemma, gloss in zip(words, lemmas, glosses):
            clean = _strip_cantillation(word)
            print(f"  {word:<25} {lemma:<18} {gloss}")
        cw = _content_words(colon)
        if not cw.empty:
            cw_lemmas = ' · '.join(cw['lemma'].dropna().tolist())
            print(f"  Content words: {cw_lemmas}")

    if len(cola) >= 2:
        a_cw = _content_words(cola[0])
        b_cw = _content_words(cola[1])
        lex = _lexical_overlap(a_cw, b_cw)
        dom = _domain_overlap(a_cw, b_cw)
        print(f"\n  Lexical overlap: {lex:.0%}   Domain overlap: {dom:.0%}")

        # Shared lemmas
        shared = set(a_cw['lemma'].dropna()) & set(b_cw['lemma'].dropna())
        if shared:
            print(f"  Shared lemmas: {' · '.join(shared)}")
    print()


def print_book_pairs(
    book: str,
    *,
    top_n: int = 20,
    min_count: int = 3,
) -> None:
    """Print the most frequent parallel word pairs in a poetry book."""
    df = book_word_pairs(book, top_n=top_n, min_count=min_count)
    w = 76
    print(f"\n{'═'*w}")
    print(f"  Most frequent A/B parallel word pairs: {book}")
    print(f"{'═'*w}")

    if df.empty:
        print("  No pairs found.")
        return

    print(f"  {'Colon A lemma':<18} {'Gloss A':<22} {'Colon B lemma':<18} {'Gloss B':<20} Count")
    print(f"  {'─'*17} {'─'*21} {'─'*17} {'─'*19} ─────")
    for _, row in df.iterrows():
        print(
            f"  {str(row['lemma_a']):<18} {str(row['gloss_a']):<22} "
            f"{str(row['lemma_b']):<18} {str(row['gloss_b']):<20} "
            f"{int(row['count']):>5}"
        )
    print()


def print_parallelism_stats(book: str) -> None:
    """Print parallelism type distribution for a book."""
    df = book_parallelism_stats(book)
    w = 50
    print(f"\n{'═'*w}")
    print(f"  Parallelism types: {book}")
    print(f"{'═'*w}")
    if df.empty:
        print("  No data.")
        return
    for _, row in df.iterrows():
        bar = '█' * int(row['pct'] / 2)
        print(f"  {str(row['type']):<14} {row['count']:>5}  {row['pct']:>5.1f}%  {bar}")
    print()


# ── Report ────────────────────────────────────────────────────────────────────

def poetry_report(
    book: str,
    *,
    output_dir: str = 'output/reports',
    top_n_pairs: int = 30,
) -> str:
    """
    Generate a Markdown report on the poetry of a book:
      - parallelism type distribution
      - top parallel word pairs
    Returns path to saved Markdown file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    md_path = out / f'poetry-{book.lower()}.md'

    stats = book_parallelism_stats(book)
    pairs = book_word_pairs(book, top_n=top_n_pairs, min_count=2)

    lines = [
        f"# Hebrew Poetry Analysis: {book}",
        "",
        "## Parallelism Type Distribution",
        "",
        "| Type | Count | % |",
        "|---|---:|---:|",
    ]
    for _, r in stats.iterrows():
        lines.append(f"| {r['type']} | {r['count']} | {r['pct']}% |")

    lines += [
        "",
        f"## Top {top_n_pairs} Parallel Word Pairs",
        "",
        "| Colon A | Gloss A | Colon B | Gloss B | Count |",
        "|---|---|---|---|---:|",
    ]
    for _, r in pairs.iterrows():
        lines.append(
            f"| {r['lemma_a']} | {r['gloss_a']} | {r['lemma_b']} | {r['gloss_b']} | {r['count']} |"
        )

    lines += [
        "",
        "---",
        "_Sources: MACULA Hebrew WLC (Clear Bible, CC BY 4.0). "
        "Cola split by Etnahta cantillation accent (U+0591)._",
    ]

    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Saved: {md_path}")
    return str(md_path)
