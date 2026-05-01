"""
Syntactic role search — "who does what to whom" across OT and NT.

Uses MACULA Hebrew (syntax_ot) and MACULA Greek (syntax) subjref links to
find verbs by their grammatical subject, object, or argument.

Questions this answers
──────────────────────
  • What verbs take God as their grammatical subject in the OT?
  • What does creation/salvation/judgment language look like when YHWH acts?
  • What verbs take Jesus as subject in the Gospels?
  • What does God say about Himself? (speech verbs + divine subject)
  • What verbs travel from OT (Hebrew) → LXX (Greek) when God is the agent?
  • Cross-testament: same semantic field, God as subject, OT vs NT

Public API
──────────
subject_verbs(subject_strongs, corpus, ...)   → DataFrame of verb tokens
verb_subjects(verb_strongs, corpus, ...)       → DataFrame of subject tokens
role_report(subject_strongs, ...)              → Markdown report + chart
print_role_summary(subject_strongs, ...)       → terminal table

Typical usage
─────────────
from bible_grammar.role_search import subject_verbs, print_role_summary, role_report

# What does YHWH do in the OT?
subject_verbs(['H3068','H0430'], corpus='OT')

# What does Jesus do in the Gospels?
subject_verbs(['G2424'], corpus='NT', books=['Mat','Mrk','Luk','Jhn'])

# Cross-testament: divine agency verbs (OT Hebrew + LXX equivalents)
role_report(['H3068','H0430'], corpus='OT', output_dir='output/reports')
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

# Strong's numbers for divine / key figures — convenience constants
GOD_OT    = {'H0430', 'H3068', 'H0136', 'H0410'}   # Elohim, YHWH, Adonai, El
GOD_NT    = {'G2316'}                                # Theos
JESUS_NT  = {'G2424'}                                # Iesous
SPIRIT_NT = {'G4151'}                                # Pneuma
HUMAN_OT  = {'H0120', 'H0376', 'H0582'}             # adam, ish, enosh

_CORPUS_MAP = {
    'OT': 'ot',
    'NT': 'nt',
}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_ot():
    from .syntax_ot import load_syntax_ot
    return load_syntax_ot()


def _load_nt():
    from .syntax import load_syntax
    return load_syntax()


def _ot_id_to_strong() -> dict[str, str]:
    """Map stripped OT xml_id (no 'o' prefix) → strongnumberx."""
    ot = _load_ot()
    return ot.set_index(ot['xml_id'].str.lstrip('o'))['strongnumberx'].to_dict()


def _nt_id_to_strong() -> dict[str, str]:
    """Map NT xml_id → strong (plain integer string)."""
    nt = _load_nt()
    return nt.set_index('xml_id')['strong'].to_dict()


def _normalise_strongs(strongs: list[str], corpus: str) -> set[str]:
    """
    Normalise a list of Strong's numbers to the format used internally
    by each corpus.

    OT (MACULA Hebrew): zero-padded 4-digit strings without prefix, e.g. '0430'
    NT (MACULA Greek):  plain integer strings without prefix, e.g. '2316'
    """
    result = set()
    for s in strongs:
        s = s.strip().upper().lstrip('HhGg')
        if corpus == 'OT':
            # zero-pad to 4 digits (may have letter suffix e.g. '2050b')
            digits = s.rstrip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            suffix = s[len(digits):]
            try:
                result.add(f"{int(digits):04d}{suffix}")
            except ValueError:
                result.add(s)
        else:
            # NT: plain integer
            try:
                result.add(str(int(s)))
            except ValueError:
                result.add(s)
    return result


# ── Core functions ────────────────────────────────────────────────────────────

def subject_verbs(
    subject_strongs: list[str] | str,
    corpus: str = 'OT',
    *,
    books: list[str] | None = None,
    stem: str | None = None,
    tense: str | None = None,
    min_count: int = 1,
    top_n: int | None = None,
    include_tokens: bool = False,
) -> pd.DataFrame:
    """
    Return verbs whose grammatical subject is one of the given Strong's numbers.

    Parameters
    ----------
    subject_strongs : Strong's number(s) for the subject,
                      e.g. ['H3068','H0430'] or 'G2424'
    corpus          : 'OT' or 'NT'
    books           : restrict to specific book_ids
    stem            : OT only — filter by verb stem (e.g. 'qal', 'niphal')
    tense           : OT: clause type ('wayyiqtol', 'qatal', …)
                      NT: tense ('aorist', 'present', …)
    min_count       : minimum occurrence count for aggregated results
    top_n           : return only top N verbs by count
    include_tokens  : if True return full token DataFrame; if False (default)
                      return aggregated (lemma, gloss, count) summary

    Returns a DataFrame sorted by count descending.
    """
    if isinstance(subject_strongs, str):
        subject_strongs = [subject_strongs]

    targets = _normalise_strongs(subject_strongs, corpus)

    if corpus == 'OT':
        df = _load_ot()
        id_map = _ot_id_to_strong()
        verbs = df[df['pos'] == 'verb'].copy()
        if books:
            verbs = verbs[verbs['book'].isin(books)]
        if stem:
            verbs = verbs[verbs['stem'].str.lower() == stem.lower()]
        if tense:
            verbs = verbs[verbs['type_'].str.lower() == tense.lower()]
        matched = verbs[
            verbs['subjref'].notna() &
            verbs['subjref'].map(lambda x: id_map.get(x, '') in targets)
        ].copy()
        if include_tokens:
            return matched
        agg_cols = ['lemma', 'strongnumberx', 'gloss', 'stem', 'greek', 'greek_g']

    else:  # NT
        df = _load_nt()
        id_map = _nt_id_to_strong()
        verbs = df[df['class_'] == 'verb'].copy()
        if books:
            verbs = verbs[verbs['book'].isin(books)]
        if tense:
            verbs = verbs[verbs['tense'].str.lower() == tense.lower()]
        matched = verbs[
            verbs['subjref'].notna() &
            verbs['subjref'].map(lambda x: id_map.get(x, '') in targets)
        ].copy()
        if include_tokens:
            return matched
        agg_cols = ['lemma', 'strong_g', 'gloss']

    if matched.empty:
        return pd.DataFrame(columns=agg_cols + ['count'])

    # Aggregate — keep available columns
    agg_cols = [c for c in agg_cols if c in matched.columns]
    result = (
        matched.groupby(agg_cols, dropna=False)
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
    )
    result = result[result['count'] >= min_count]
    if top_n:
        result = result.head(top_n)
    return result.reset_index(drop=True)


def verb_subjects(
    verb_strongs: list[str] | str,
    corpus: str = 'OT',
    *,
    books: list[str] | None = None,
) -> pd.DataFrame:
    """
    Return the subjects (by Strong's number and lemma) that appear as the
    grammatical subject of a given verb.

    Useful for: "who calls, commands, saves, creates…"
    """
    if isinstance(verb_strongs, str):
        verb_strongs = [verb_strongs]

    targets = _normalise_strongs(verb_strongs, corpus)

    if corpus == 'OT':
        df = _load_ot()
        id_map = df.set_index(df['xml_id'].str.lstrip('o'))[['strongnumberx', 'lemma', 'gloss']].to_dict('index')
        verbs = df[df['pos'] == 'verb']
        if books:
            verbs = verbs[verbs['book'].isin(books)]
        verb_rows = verbs[verbs['strongnumberx'].isin(targets)]
        subjects = []
        for _, vrow in verb_rows[verb_rows['subjref'].notna()].iterrows():
            subj = id_map.get(vrow['subjref'])
            if subj:
                subjects.append({
                    'verb_lemma': vrow['lemma'],
                    'verb_ref': vrow['ref'],
                    'subject_strong': 'H' + subj['strongnumberx'],
                    'subject_lemma': subj['lemma'],
                    'subject_gloss': subj['gloss'],
                })
    else:
        df = _load_nt()
        id_map = df.set_index('xml_id')[['strong', 'lemma', 'gloss']].to_dict('index')
        verbs = df[df['class_'] == 'verb']
        if books:
            verbs = verbs[verbs['book'].isin(books)]
        verb_rows = verbs[verbs['strong'].isin(targets)]
        subjects = []
        for _, vrow in verb_rows[verb_rows['subjref'].notna()].iterrows():
            subj = id_map.get(vrow['subjref'])
            if subj:
                subjects.append({
                    'verb_lemma': vrow['lemma'],
                    'verb_ref': vrow['ref'],
                    'subject_strong': 'G' + subj['strong'],
                    'subject_lemma': subj['lemma'],
                    'subject_gloss': subj['gloss'],
                })

    if not subjects:
        return pd.DataFrame()

    result = pd.DataFrame(subjects)
    return (
        result.groupby(['subject_strong', 'subject_lemma', 'subject_gloss'])
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .reset_index(drop=True)
    )


# ── Terminal output ───────────────────────────────────────────────────────────

def print_role_summary(
    subject_strongs: list[str] | str,
    corpus: str = 'OT',
    *,
    books: list[str] | None = None,
    top_n: int = 20,
    label: str | None = None,
) -> None:
    """Print a formatted table of verbs with the given subject to stdout."""
    df = subject_verbs(subject_strongs, corpus, books=books, top_n=top_n)
    if isinstance(subject_strongs, str):
        subject_strongs = [subject_strongs]

    display_label = label or '/'.join(subject_strongs)
    scope = f" ({', '.join(books)})" if books else ''
    w = 72

    print(f"\n{'═'*w}")
    print(f"  Verbs with subject: {display_label}{scope}  [{corpus}]")
    print(f"{'═'*w}")

    if df.empty:
        print("  No results found.")
        print()
        return

    if corpus == 'OT':
        print(f"  {'Lemma':<16} {'Gloss':<24} {'Stem':<12} {'LXX':<16} Count")
        print(f"  {'-'*15} {'-'*23} {'-'*11} {'-'*15} -----")
        for _, row in df.iterrows():
            lxx = row.get('greek', '')[:15] if row.get('greek') else ''
            stem = row.get('stem', '')[:11] if row.get('stem') else ''
            print(f"  {str(row['lemma']):<16} {str(row['gloss']):<24} {stem:<12} {lxx:<16} {row['count']:>5}")
    else:
        print(f"  {'Lemma':<20} {'Gloss':<30} Count")
        print(f"  {'-'*19} {'-'*29} -----")
        for _, row in df.iterrows():
            print(f"  {str(row['lemma']):<20} {str(row['gloss']):<30} {row['count']:>5}")

    print(f"\n  Total distinct verb lemmas: {len(df)}")
    print()


# ── Chart ─────────────────────────────────────────────────────────────────────

def role_chart(
    subject_strongs: list[str] | str,
    corpus: str = 'OT',
    *,
    books: list[str] | None = None,
    top_n: int = 20,
    label: str | None = None,
    output_path: str | None = None,
    figsize: tuple = (12, 6),
) -> str:
    """
    Horizontal bar chart of top verbs for the given subject.
    Returns path to saved PNG.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    if isinstance(subject_strongs, str):
        subject_strongs = [subject_strongs]

    df = subject_verbs(subject_strongs, corpus, books=books, top_n=top_n)
    display_label = label or '/'.join(subject_strongs)
    scope = f" ({', '.join(books)})" if books else ''

    if output_path is None:
        slug = display_label.replace('/', '-').replace(' ', '').lower()
        out_dir = Path('output/charts')
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f'role-{slug}-{corpus.lower()}.png')

    if df.empty:
        return output_path

    # Build display labels: lemma + gloss
    if corpus == 'OT':
        labels = [f"{r['lemma']}  \"{r['gloss'][:18]}\"" for _, r in df.iterrows()]
    else:
        labels = [f"{r['lemma']}  \"{r['gloss'][:22]}\"" for _, r in df.iterrows()]

    fig, ax = plt.subplots(figsize=figsize)
    color = '#2c5f8a' if corpus == 'OT' else '#8a2c2c'
    ax.barh(labels[::-1], df['count'][::-1], color=color, alpha=0.85)
    ax.set_xlabel('Occurrences', fontsize=9)
    ax.set_title(
        f'Verbs with subject: {display_label}{scope}  [{corpus}]\n'
        f'(syntactic subject resolved via MACULA {corpus} subjref links)',
        fontsize=10, fontweight='bold', pad=10,
    )
    ax.xaxis.grid(True, linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return output_path


# ── Cross-testament comparison ────────────────────────────────────────────────

def divine_action_comparison(
    *,
    ot_strongs: list[str] | None = None,
    nt_strongs: list[str] | None = None,
    top_n: int = 20,
    output_path: str | None = None,
    figsize: tuple = (14, 7),
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Side-by-side comparison: God's verbs in OT Hebrew vs NT Greek.

    For OT verbs, also shows the inline LXX Greek equivalent (greek_g column)
    to facilitate direct lexical comparison with NT vocabulary.

    Returns (ot_df, nt_df, chart_path).
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    if ot_strongs is None:
        ot_strongs = ['H3068', 'H0430', 'H0136', 'H0410']
    if nt_strongs is None:
        nt_strongs = ['G2316']

    ot_df = subject_verbs(ot_strongs, 'OT', top_n=top_n)
    nt_df = subject_verbs(nt_strongs, 'NT', top_n=top_n)

    if output_path is None:
        out_dir = Path('output/charts')
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / 'divine-action-ot-nt.png')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # OT panel
    if not ot_df.empty:
        ot_labels = [f"{r['lemma']}  \"{r['gloss'][:16]}\"" for _, r in ot_df.iterrows()]
        ax1.barh(ot_labels[::-1], ot_df['count'][::-1], color='#2c5f8a', alpha=0.85)
        ax1.set_title('OT: God (YHWH/Elohim)\nas grammatical subject', fontsize=9, fontweight='bold')
        ax1.xaxis.grid(True, linestyle='--', alpha=0.4)
        ax1.set_axisbelow(True)

    # NT panel
    if not nt_df.empty:
        nt_labels = [f"{r['lemma']}  \"{r['gloss'][:20]}\"" for _, r in nt_df.iterrows()]
        ax2.barh(nt_labels[::-1], nt_df['count'][::-1], color='#8a2c2c', alpha=0.85)
        ax2.set_title('NT: God (Theos)\nas grammatical subject', fontsize=9, fontweight='bold')
        ax2.xaxis.grid(True, linestyle='--', alpha=0.4)
        ax2.set_axisbelow(True)

    fig.suptitle(
        'Divine Action: Verbs with God as Grammatical Subject\n'
        '(OT Hebrew via MACULA Hebrew subjref; NT Greek via MACULA Greek subjref)',
        fontsize=11, fontweight='bold', y=1.01,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return ot_df, nt_df, output_path


# ── Markdown report ───────────────────────────────────────────────────────────

def role_report(
    subject_strongs: list[str] | str,
    corpus: str = 'OT',
    *,
    books: list[str] | None = None,
    top_n: int = 30,
    label: str | None = None,
    output_dir: str = 'output/reports',
    include_cross_testament: bool = True,
) -> str:
    """
    Generate a Markdown report: top verbs for the given subject,
    with chart, book distribution, and optional cross-testament panel.

    Returns path to saved Markdown file.
    """
    if isinstance(subject_strongs, str):
        subject_strongs = [subject_strongs]

    display_label = label or '/'.join(subject_strongs)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = display_label.replace('/', '-').replace(' ', '').lower()
    md_path = out_dir / f'role-{slug}-{corpus.lower()}.md'

    df = subject_verbs(subject_strongs, corpus, books=books, top_n=top_n)
    chart_path = role_chart(
        subject_strongs, corpus,
        books=books, top_n=top_n, label=display_label,
        output_path=str(out_dir / f'role-{slug}-{corpus.lower()}.png'),
    )

    scope_str = f" in {', '.join(books)}" if books else ''
    lines = [
        f"# Syntactic Role Analysis: {display_label}{scope_str} [{corpus}]",
        "",
        f"Verbs whose grammatical subject is **{display_label}**, resolved via "
        f"MACULA {'Hebrew' if corpus == 'OT' else 'Greek'} `subjref` links.",
        "",
        "> **Method:** Each verb token in the MACULA syntax tree carries a `subjref` "
        "attribute pointing to its grammatical subject. This analysis finds all verb "
        "tokens where that subject resolves to the given Strong's number(s).",
        "",
        f"![Role chart]({Path(chart_path).name})",
        "",
        "## Top Verbs by Frequency",
        "",
    ]

    if corpus == 'OT':
        lines += ["| Lemma | Gloss | Stem | LXX Greek | LXX Strong | Count |",
                  "|---|---|---|---|---|---:|"]
        for _, row in df.iterrows():
            lines.append(
                f"| {row['lemma']} | {row['gloss']} | {row.get('stem','')} "
                f"| {row.get('greek','')} | {row.get('greek_g','')} | {row['count']} |"
            )
    else:
        lines += ["| Lemma | Gloss | Strong | Count |",
                  "|---|---|---|---:|"]
        for _, row in df.iterrows():
            lines.append(
                f"| {row['lemma']} | {row['gloss']} "
                f"| {row.get('strong_g','')} | {row['count']} |"
            )

    lines.append("")

    # Book distribution for top 5 verbs
    if not df.empty:
        lines += ["## Distribution by Book (Top 5 Verbs)", ""]
        tokens = subject_verbs(subject_strongs, corpus, books=books,
                               include_tokens=True)
        top5_lemmas = df.head(5)['lemma'].tolist()
        top5_tokens = tokens[tokens['lemma'].isin(top5_lemmas)]
        if not top5_tokens.empty:
            by_book = (
                top5_tokens.groupby(['lemma', 'book'])
                .size().reset_index(name='count')
                .pivot(index='book', columns='lemma', values='count')
                .fillna(0).astype(int)
            )
            lines += ["| Book | " + " | ".join(top5_lemmas) + " |",
                      "|---|" + "---:|" * len(top5_lemmas)]
            for book, row in by_book.iterrows():
                vals = " | ".join(str(row.get(l, 0)) for l in top5_lemmas)
                lines.append(f"| {book} | {vals} |")
            lines.append("")

    # Cross-testament section
    if include_cross_testament and corpus == 'OT':
        lines += ["## Cross-Testament: OT vs NT Divine Action", ""]
        ot_df2, nt_df2, ct_chart = divine_action_comparison(
            ot_strongs=subject_strongs,
            output_path=str(out_dir / 'divine-action-ot-nt.png'),
        )
        lines += [
            f"![OT vs NT divine action chart]({Path(ct_chart).name})",
            "",
            "The OT column shows Hebrew verb lemmas with their inline LXX Greek "
            "equivalent. The NT column shows Greek verbs with Θεός as subject.",
            "",
        ]

    lines += [
        "---",
        "",
        "_Source: MACULA Hebrew WLC and MACULA Greek Nestle1904 (CC BY 4.0, "
        "Clear Bible / Tyndale House Cambridge). Syntactic subject resolved via "
        "`subjref` attribute in the MACULA lowfat syntax trees._",
    ]

    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Saved: {md_path}")
    print(f"  Chart: {chart_path}")
    return str(md_path)
