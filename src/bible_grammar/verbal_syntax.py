"""
Hebrew verbal syntax analysis for 2nd-year Biblical Hebrew study.

Focuses on the syntactic and discourse-level behaviour of the Hebrew verb system:
  • verb_form_profile     — distribution of all conjugation types by book / passage
  • wayyiqtol_chains      — find and describe consecutive wayyiqtol sequences
  • infinitive_usage      — inf construct vs. absolute with governing prepositions
  • clause_type_profile   — nominal vs. verbal clause ratio; question / negation / relative
  • stem_distribution     — Qal/Nif/Piel/Hif/Hitpael etc. by book

All functions use the MACULA Hebrew WLC data (`syntax_ot`) which provides
word-level `type_` (wayyiqtol, qatal, yiqtol, …) and `role` (v, s, o, adv, p)
annotations — more reliable than the raw TAHOT morphology codes for syntactic work.

Public API
──────────
verb_form_profile(book, chapter=None)           → DataFrame
print_verb_form_profile(book, chapter=None)     → None (terminal output)
verb_form_chart(book, *, output_path=None)      → Path | None

wayyiqtol_chains(book, chapter)                 → list[dict]
print_wayyiqtol_chains(book, chapter)           → None

infinitive_usage(book)                          → dict
print_infinitive_usage(book)                    → None

clause_type_profile(book)                       → DataFrame
print_clause_type_profile(book)                 → None

stem_distribution(book)                         → DataFrame
print_stem_distribution(book)                   → None
stem_chart(book, *, output_path=None)           → Path | None

disjunctive_clauses(book, chapter=None)         → DataFrame
print_disjunctive_clauses(book, chapter=None)   → None
disjunctive_in_chains(book, chapter)            → list[dict]
print_disjunctive_in_chains(book, chapter)      → None

conditional_clauses(book, chapter=None)         → DataFrame
print_conditional_clauses(book, chapter=None)   → None
conditional_summary(book)                       → DataFrame
print_conditional_summary(book)                 → None
"""

from __future__ import annotations
import unicodedata
from pathlib import Path

import pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────

# MACULA `type_` values for verbs — canonical display names
VERB_FORM_ORDER = [
    'wayyiqtol',
    'qatal',
    'yiqtol',
    'weqatal',
    'participle active',
    'participle passive',
    'imperative',
    'jussive',
    'cohortative',
    'infinitive construct',
    'infinitive absolute',
]

# Short labels for charts
VERB_FORM_LABELS = {
    'wayyiqtol':            'wayyiqtol',
    'qatal':                'qatal',
    'yiqtol':               'yiqtol',
    'weqatal':              'weqatal',
    'participle active':    'ptc.act',
    'participle passive':   'ptc.pass',
    'imperative':           'impv',
    'jussive':              'juss',
    'cohortative':          'coh',
    'infinitive construct': 'inf.cst',
    'infinitive absolute':  'inf.abs',
}

# Governing-preposition lemmas (consonantal, diacritics stripped)
_PREP_DISPLAY = {
    'ל':    'lamed (purpose/result)',
    'ב':    'bet (temporal/instrumental)',
    'כ':    'kaf (comparative)',
    'מן':   'min (from)',
    'עד':   'ayin-dalet (until)',
    'על':   'ayin-lamed (upon)',
    'אחר':  'after',
    'בלת':  'without (neg. purpose)',
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_macula() -> pd.DataFrame:
    from .syntax_ot import load_syntax_ot
    return load_syntax_ot()


def _strip_diacritics(text: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(text))
        if unicodedata.category(c) != 'Mn'
    )


def _filter_book(df: pd.DataFrame, book: str, chapter: int | None = None) -> pd.DataFrame:
    book_col = 'book_id' if 'book_id' in df.columns else 'book'
    result = df[df[book_col] == book]
    if chapter is not None:
        result = result[result['chapter'] == chapter]
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERB FORM PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

def verb_form_profile(
    book: str,
    chapter: int | None = None,
) -> pd.DataFrame:
    """
    Count occurrences of each Hebrew verb conjugation type in a book or chapter.

    Returns a DataFrame with columns:
      form, count, pct
    Rows are ordered by VERB_FORM_ORDER (wayyiqtol → inf.abs).
    """
    df = _load_macula()
    scope = _filter_book(df, book, chapter)
    verbs = scope[scope['class_'] == 'verb']

    counts: dict[str, int] = {f: 0 for f in VERB_FORM_ORDER}
    for t in verbs['type_']:
        t_str = str(t).strip()
        if t_str in counts:
            counts[t_str] += 1
        # merge 'common' / unlabelled into nearest form based on morph? Skip for now.

    total = sum(counts.values())
    records = []
    for form in VERB_FORM_ORDER:
        n = counts[form]
        pct = round(n / total * 100, 1) if total else 0.0
        records.append({'form': form, 'count': n, 'pct': pct})

    return pd.DataFrame(records)


def print_verb_form_profile(
    book: str,
    chapter: int | None = None,
) -> None:
    """Print a formatted verb form profile for a book or chapter."""
    df = verb_form_profile(book, chapter)
    total = df['count'].sum()
    scope = f"{book} ch.{chapter}" if chapter else book

    print()
    print('═' * 72)
    print(f"  Verb form profile: {scope}  (total verb tokens: {total})")
    print('─' * 72)
    for _, row in df.iterrows():
        bar = '█' * int(row['pct'] / 2)
        print(f"  {row['form']:<22} {row['count']:>5}  {row['pct']:>5.1f}%  {bar}")
    print()


def verb_form_chart(
    book: str,
    chapter: int | None = None,
    *,
    output_path: str | None = None,
) -> Path | None:
    """
    Bar chart of verb form distribution.
    Saves PNG to output_path (or output/charts/verb-forms-<book>.png).
    Returns the Path, or None if matplotlib is unavailable.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — cannot generate chart")
        return None

    df = verb_form_profile(book, chapter)
    df = df[df['count'] > 0]
    scope = f"{book} ch.{chapter}" if chapter else book

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.tab20.colors[:len(df)]
    ax.bar([VERB_FORM_LABELS.get(f, f) for f in df['form']], df['count'],
           color=colors, edgecolor='white', linewidth=0.5)
    ax.set_title(f"Hebrew Verb Form Distribution — {scope}", fontsize=13)
    ax.set_ylabel("Token count")
    ax.set_xlabel("Conjugation type")
    plt.xticks(rotation=30, ha='right', fontsize=9)
    plt.tight_layout()

    if output_path is None:
        slug = f"{book.lower()}-ch{chapter}" if chapter else book.lower()
        out = Path('output/charts')
        out.mkdir(parents=True, exist_ok=True)
        output_path = str(out / f'verb-forms-{slug}.png')

    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Saved chart: {output_path}")
    return Path(output_path)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. WAYYIQTOL CHAINS
# ═══════════════════════════════════════════════════════════════════════════════
#
# A wayyiqtol chain is a sequence of consecutive wayyiqtol verbs driving the
# narrative forward (the classic "and he did X, and he did Y" of Hebrew prose).
# Chains break when:
#   - A non-wayyiqtol verb appears (qatal, yiqtol, jussive, participle, …)
#   - A noun-first / disjunctive clause interrupts (subject before verb)
#   - Direct speech begins (introduces a new discourse unit)
#
# Each chain record includes:
#   start / end reference, length, the verb sequence, and what broke the chain.
# ───────────────────────────────────────────────────────────────────────────────

def wayyiqtol_chains(book: str, chapter: int) -> list[dict]:
    """
    Identify wayyiqtol chains in a chapter.

    Returns a list of chain dicts, each with:
      start_verse   : int
      end_verse     : int
      length        : int (number of wayyiqtols)
      verbs         : list of (verse, text, lemma, stem) tuples
      break_type    : str — what ended the chain
      break_form    : str — type_ of the breaking token (or 'end-of-chapter')
    """
    df = _load_macula()
    chap = _filter_book(df, book, chapter)
    # Work only with verb-role tokens for chain detection
    verb_rows = chap[chap['role'] == 'v'].reset_index(drop=True)

    chains: list[dict] = []
    current: list[dict] = []

    for _, row in verb_rows.iterrows():
        form = str(row.get('type_', '')).strip()
        if form == 'wayyiqtol':
            current.append({
                'verse': int(row['verse']),
                'text':  str(row.get('text', '')),
                'lemma': str(row.get('lemma', '')),
                'stem':  str(row.get('stem', '')),
                'gloss': str(row.get('gloss', '')),
            })
        else:
            if len(current) >= 2:
                chains.append(_make_chain(current, form))
            elif len(current) == 1:
                # Single wayyiqtol is still noteworthy in isolation
                pass
            current = []

    if len(current) >= 2:
        chains.append(_make_chain(current, 'end-of-chapter'))

    return chains


def _make_chain(verbs: list[dict], break_form: str) -> dict:
    # Classify the break
    if break_form == 'end-of-chapter':
        break_type = 'end of chapter'
    elif break_form in ('qatal', 'weqatal'):
        break_type = 'perfect / weqatal (summary or result)'
    elif break_form in ('yiqtol', 'jussive', 'cohortative'):
        break_type = 'modal/jussive (speech or wish)'
    elif 'participle' in break_form:
        break_type = 'participle (circumstantial/descriptive)'
    elif break_form == 'infinitive construct':
        break_type = 'infinitive construct (purpose clause)'
    elif break_form == 'infinitive absolute':
        break_type = 'infinitive absolute (intensification)'
    elif break_form == 'imperative':
        break_type = 'imperative (command)'
    else:
        break_type = f'other ({break_form})'

    return {
        'start_verse': verbs[0]['verse'],
        'end_verse':   verbs[-1]['verse'],
        'length':      len(verbs),
        'verbs':       verbs,
        'break_type':  break_type,
        'break_form':  break_form,
    }


def print_wayyiqtol_chains(book: str, chapter: int) -> None:
    """Print a formatted wayyiqtol chain analysis for a chapter."""
    chains = wayyiqtol_chains(book, chapter)
    total_wayy = sum(c['length'] for c in chains)

    print()
    print('═' * 72)
    print(f"  Wayyiqtol chains: {book} ch.{chapter}  "
          f"({len(chains)} chains, {total_wayy} wayyiqtol verbs total)")
    print('─' * 72)

    if not chains:
        print("  No wayyiqtol chains of length ≥ 2 found.")
        print()
        return

    for i, ch in enumerate(chains, 1):
        vref = (f"v{ch['start_verse']}" if ch['start_verse'] == ch['end_verse']
                else f"vv{ch['start_verse']}–{ch['end_verse']}")
        print(f"\n  Chain {i}  [{vref}]  length={ch['length']}  "
              f"→ breaks: {ch['break_type']}")
        for v in ch['verbs']:
            gloss = v['gloss'][:20] if v['gloss'] else ''
            print(f"    v{v['verse']}  {v['text']:<20}  {v['lemma']:<12}  "
                  f"{v['stem']:<12}  {gloss}")

    print()
    # Summary stats
    lengths = [c['length'] for c in chains]
    print(f"  Longest chain: {max(lengths)} verbs  |  "
          f"Mean length: {sum(lengths)/len(lengths):.1f}")
    break_counts: dict[str, int] = {}
    for c in chains:
        k = c['break_form']
        break_counts[k] = break_counts.get(k, 0) + 1
    print("  Chain-break forms:")
    for form, cnt in sorted(break_counts.items(), key=lambda x: -x[1]):
        print(f"    {form:<28} × {cnt}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. INFINITIVE USAGE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Infinitive construct: typically governs purpose/result (with ל), temporal
# clauses (with כ/ב), or functions as a verbal noun (subject/object).
# Infinitive absolute: most often used paronomastically (emphatic doubling with
# a finite verb) or adverbially (modifying manner/degree).
# ───────────────────────────────────────────────────────────────────────────────

def infinitive_usage(book: str) -> dict:
    """
    Analyse infinitive construct and absolute usage in a book.

    Returns a dict with:
      inf_cst_total    : int
      inf_abs_total    : int
      inf_cst_by_prep  : dict[str, int]  — governing prep lemma → count
      inf_cst_by_role  : dict[str, int]  — clause role (v/s/o/adv) → count
      inf_abs_examples : list[dict]      — sample tokens with context
      inf_cst_examples : list[dict]      — sample tokens per prep
    """
    df = _load_macula()
    book_df = _filter_book(df, book).reset_index(drop=True)

    inf_cst_rows = book_df[book_df['type_'] == 'infinitive construct']
    inf_abs_rows = book_df[book_df['type_'] == 'infinitive absolute']

    # Governing preposition: look up to 3 tokens back for a prep
    def _find_prep(pos: int) -> str:
        for back in range(1, 4):
            if pos - back < 0:
                break
            prev = book_df.iloc[pos - back]
            if prev['class_'] == 'prep':
                return _strip_diacritics(str(prev.get('lemma', '')))
            if prev['class_'] in ('verb', 'noun', 'adj'):
                break  # passed a content word — no governing prep
        return '(none)'

    inf_cst_by_prep: dict[str, int] = {}
    inf_cst_by_role: dict[str, int] = {}
    inf_cst_examples: list[dict] = []

    for pos, (_, row) in enumerate(inf_cst_rows.iterrows()):
        actual_pos = book_df.index.get_loc(row.name)
        prep = _find_prep(actual_pos)
        inf_cst_by_prep[prep] = inf_cst_by_prep.get(prep, 0) + 1
        role = str(row.get('role', ''))
        inf_cst_by_role[role] = inf_cst_by_role.get(role, 0) + 1
        if len(inf_cst_examples) < 30:
            inf_cst_examples.append({
                'book': book,
                'chapter': int(row['chapter']),
                'verse': int(row['verse']),
                'text': str(row.get('text', '')),
                'lemma': str(row.get('lemma', '')),
                'stem': str(row.get('stem', '')),
                'governing_prep': prep,
                'role': role,
                'gloss': str(row.get('gloss', '')),
            })

    # For inf absolute: collect examples and check for paronomastic use
    # (inf absolute immediately precedes or follows the same root finite verb)
    inf_abs_examples: list[dict] = []
    for pos, (_, row) in enumerate(inf_abs_rows.iterrows()):
        actual_pos = book_df.index.get_loc(row.name)
        # Check neighbours for same-root finite verb (paronomastic)
        paronomastic = False
        root = _strip_diacritics(str(row.get('lemma', '')))
        for delta in (-2, -1, 1, 2):
            nbr_pos = actual_pos + delta
            if 0 <= nbr_pos < len(book_df):
                nbr = book_df.iloc[nbr_pos]
                if (_strip_diacritics(str(nbr.get('lemma', ''))) == root
                        and nbr.get('class_') == 'verb'
                        and nbr.get('type_') != 'infinitive absolute'):
                    paronomastic = True
                    break
        inf_abs_examples.append({
            'chapter': int(row['chapter']),
            'verse': int(row['verse']),
            'text': str(row.get('text', '')),
            'lemma': str(row.get('lemma', '')),
            'stem': str(row.get('stem', '')),
            'gloss': str(row.get('gloss', '')),
            'paronomastic': paronomastic,
        })

    return {
        'inf_cst_total':    len(inf_cst_rows),
        'inf_abs_total':    len(inf_abs_rows),
        'inf_cst_by_prep':  inf_cst_by_prep,
        'inf_cst_by_role':  inf_cst_by_role,
        'inf_cst_examples': inf_cst_examples,
        'inf_abs_examples': inf_abs_examples,
    }


def print_infinitive_usage(book: str) -> None:
    """Print a formatted infinitive usage analysis for a book."""
    result = infinitive_usage(book)

    print()
    print('═' * 72)
    print(f"  Infinitive usage: {book}")
    print(f"  Infinitive construct: {result['inf_cst_total']}  |  "
          f"Infinitive absolute: {result['inf_abs_total']}")
    print('─' * 72)

    print("\n  Infinitive Construct — governing preposition:")
    by_prep = sorted(result['inf_cst_by_prep'].items(), key=lambda x: -x[1])
    total_cst = result['inf_cst_total'] or 1
    for prep, cnt in by_prep:
        desc = _PREP_DISPLAY.get(prep, prep)
        pct = cnt / total_cst * 100
        bar = '█' * int(pct / 3)
        print(f"    {prep:<8} {desc:<32} {cnt:>4}  {pct:>5.1f}%  {bar}")

    print("\n  Infinitive Construct — clause role:")
    role_labels = {'v': 'verb (main predicate)', 's': 'subject',
                   'o': 'object', 'adv': 'adverbial', 'p': 'predicate',
                   '': 'unlabelled'}
    for role, cnt in sorted(result['inf_cst_by_role'].items(), key=lambda x: -x[1]):
        label = role_labels.get(role, role)
        print(f"    {role or '–':<6} {label:<28} {cnt:>4}")

    print("\n  Infinitive Absolute — sample (with paronomastic flag):")
    for ex in result['inf_abs_examples'][:20]:
        paro = '⟦paronomastic⟧' if ex['paronomastic'] else ''
        print(f"    {book} {ex['chapter']}:{ex['verse']:<4}  "
              f"{ex['text']:<20}  {ex['lemma']:<12}  {ex['gloss'][:20]:<20}  {paro}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CLAUSE TYPE PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Verbal clause: the main verb token bears role='v' (wayyiqtol, qatal, etc.)
# Nominal clause: predication without a finite verb (noun/pronoun as predicate)
# In MACULA these show up as role='p' (predicate) with class_='noun' or 'adj'.
#
# We also count:
#   negation tokens (לֹא, אַל, בַּל, לְבַלְתִּי)
#   question markers (הֲ, מָה, מִי, אֵיכָה)
#   relative clauses (אֲשֶׁר tokens with following verb)
#   conditional protases (אִם / כִּי / לוּ)
# ───────────────────────────────────────────────────────────────────────────────

_NEGATION_LEMMAS = {'לֹא', 'אַל', 'בַּל', 'לְבַלְתִּי', 'אֵין', 'בְּלִי', 'לֹא'}
_CONDITIONAL_LEMMAS = {'אִם', 'לוּ', 'לוּלֵא', 'לוּלֵי', 'הֵן', 'הִן'}
_RELATIVE_LEMMAS = {'אֲשֶׁר', 'שֶׁ'}

_NEG_STRIPPED = {_strip_diacritics(l) for l in _NEGATION_LEMMAS}
_COND_STRIPPED = {_strip_diacritics(l) for l in _CONDITIONAL_LEMMAS}
_REL_STRIPPED  = {_strip_diacritics(l) for l in _RELATIVE_LEMMAS}


def clause_type_profile(book: str) -> pd.DataFrame:
    """
    Compute clause-type statistics for a book.

    Returns a DataFrame with columns: feature, count, pct_of_verses.
    Features: verbal_clauses, nominal_clauses, negations, conditionals,
              relative_clauses, questions.
    """
    df = _load_macula()
    book_df = _filter_book(df, book)

    # Count verses
    n_verses = book_df[['chapter', 'verse']].drop_duplicates().shape[0]

    # Verbal clauses: verses with at least one role='v' token
    verbal = (book_df[book_df['role'] == 'v']
              .groupby(['chapter', 'verse'])
              .size()
              .reset_index(name='n'))
    n_verbal = len(verbal)

    # Nominal clauses: verses with role='p' but no role='v'
    v_refs = set(zip(book_df[book_df['role'] == 'v']['chapter'],
                     book_df[book_df['role'] == 'v']['verse']))
    p_refs = set(zip(book_df[book_df['role'] == 'p']['chapter'],
                     book_df[book_df['role'] == 'p']['verse']))
    n_nominal = len(p_refs - v_refs)

    # Negation tokens
    book_df = book_df.copy()
    book_df['_lem_stripped'] = book_df['lemma'].apply(
        lambda x: _strip_diacritics(str(x)))
    n_neg = (book_df['_lem_stripped'].isin(_NEG_STRIPPED)).sum()

    # Conditional tokens
    n_cond = (book_df['_lem_stripped'].isin(_COND_STRIPPED)).sum()

    # Relative clause markers
    n_rel = (book_df['_lem_stripped'].isin(_REL_STRIPPED)).sum()

    # Question markers: type_='interrogative' OR lemma הֲ (prefix — class_='ptcl')
    n_q = (book_df['type_'] == 'interrogative').sum()

    records = [
        ('verbal clauses',   n_verbal, round(n_verbal / n_verses * 100, 1)),
        ('nominal clauses',  n_nominal, round(n_nominal / n_verses * 100, 1)),
        ('negation tokens',  int(n_neg), round(int(n_neg) / n_verses * 100, 1)),
        ('conditional (אם/לו)', int(n_cond), round(int(n_cond) / n_verses * 100, 1)),
        ('relative clauses', int(n_rel), round(int(n_rel) / n_verses * 100, 1)),
        ('interrogative',    int(n_q),  round(int(n_q) / n_verses * 100, 1)),
        ('total verses',     n_verses,  100.0),
    ]
    return pd.DataFrame(records, columns=['feature', 'count', 'per_100_verses'])


def print_clause_type_profile(book: str) -> None:
    """Print a formatted clause-type profile for a book."""
    df = clause_type_profile(book)
    n_verses = int(df[df['feature'] == 'total verses']['count'].iloc[0])

    print()
    print('═' * 72)
    print(f"  Clause type profile: {book}  ({n_verses} verses)")
    print('─' * 72)
    for _, row in df[df['feature'] != 'total verses'].iterrows():
        bar = '█' * int(row['per_100_verses'] / 4)
        print(f"  {row['feature']:<28} {row['count']:>5}  "
              f"{row['per_100_verses']:>6.1f}/100v  {bar}")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. STEM DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════════

# Canonical stem order for display (main 7 binyanim + extras)
_STEM_ORDER = [
    'qal', 'niphal', 'piel', 'pual', 'hiphil', 'hophal', 'hithpael',
    'polel', 'hithpolel', 'pilpel', 'poel', 'hithpeel', 'peal',
    'pael', 'aphel', 'haphel', 'shaph',
]


def stem_distribution(book: str) -> pd.DataFrame:
    """
    Count verb tokens by stem (binyan) for a book.

    Returns DataFrame: stem, count, pct.
    """
    df = _load_macula()
    book_df = _filter_book(df, book)
    verbs = book_df[book_df['class_'] == 'verb']

    counts = verbs['stem'].value_counts().reset_index()
    counts.columns = ['stem', 'count']
    total = counts['count'].sum()
    counts['pct'] = (counts['count'] / total * 100).round(1)
    counts = counts.sort_values('count', ascending=False).reset_index(drop=True)
    return counts


def print_stem_distribution(book: str) -> None:
    """Print a formatted stem distribution for a book."""
    df = stem_distribution(book)
    total = df['count'].sum()

    print()
    print('═' * 72)
    print(f"  Verb stem distribution: {book}  (total: {total})")
    print('─' * 72)
    for _, row in df.iterrows():
        bar = '█' * int(row['pct'] / 2)
        print(f"  {str(row['stem']):<20} {row['count']:>5}  {row['pct']:>5.1f}%  {bar}")
    print()


def stem_chart(
    book: str,
    *,
    output_path: str | None = None,
) -> Path | None:
    """
    Horizontal bar chart of verb stem distribution.
    Returns the saved Path, or None if matplotlib unavailable.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — cannot generate chart")
        return None

    df = stem_distribution(book)
    df = df[df['count'] >= 2]

    fig, ax = plt.subplots(figsize=(8, max(4, len(df) * 0.4)))
    colors = plt.cm.tab20.colors[:len(df)]
    ax.barh(df['stem'][::-1], df['count'][::-1],
            color=colors[::-1], edgecolor='white', linewidth=0.5)
    ax.set_title(f"Verb Stem Distribution — {book}", fontsize=12)
    ax.set_xlabel("Token count")
    plt.tight_layout()

    if output_path is None:
        out = Path('output/charts')
        out.mkdir(parents=True, exist_ok=True)
        output_path = str(out / f'stems-{book.lower()}.png')

    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Saved chart: {output_path}")
    return Path(output_path)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE: full verbal syntax report for a book
# ═══════════════════════════════════════════════════════════════════════════════

def verbal_syntax_report(book: str, *, output_dir: str = 'output/reports') -> str:
    """
    Generate a Markdown report covering all five verbal syntax analyses for a book.
    Returns path to the saved file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    md_path = out / f'verbal-syntax-{book.lower()}.md'

    vfp  = verb_form_profile(book)
    stems = stem_distribution(book)
    ctp  = clause_type_profile(book)
    inf  = infinitive_usage(book)

    lines = [
        f"# Hebrew Verbal Syntax Report: {book}",
        "",
        "## 1. Verb Form Profile",
        "",
        "| Form | Count | % |",
        "|---|---:|---:|",
    ]
    for _, r in vfp.iterrows():
        lines.append(f"| {r['form']} | {r['count']} | {r['pct']}% |")

    lines += [
        "",
        "## 2. Verb Stem (Binyan) Distribution",
        "",
        "| Stem | Count | % |",
        "|---|---:|---:|",
    ]
    for _, r in stems.iterrows():
        lines.append(f"| {r['stem']} | {r['count']} | {r['pct']}% |")

    lines += [
        "",
        "## 3. Clause Type Profile",
        "",
        "| Feature | Count | Per 100 verses |",
        "|---|---:|---:|",
    ]
    for _, r in ctp.iterrows():
        lines.append(f"| {r['feature']} | {r['count']} | {r['per_100_verses']} |")

    lines += [
        "",
        "## 4. Infinitive Usage",
        "",
        f"- Infinitive construct: {inf['inf_cst_total']}",
        f"- Infinitive absolute: {inf['inf_abs_total']}",
        "",
        "### Infinitive Construct — governing preposition",
        "",
        "| Prep | Description | Count |",
        "|---|---|---:|",
    ]
    for prep, cnt in sorted(inf['inf_cst_by_prep'].items(), key=lambda x: -x[1]):
        desc = _PREP_DISPLAY.get(prep, prep)
        lines.append(f"| {prep} | {desc} | {cnt} |")

    lines += [
        "",
        "### Infinitive Absolute — sample occurrences",
        "",
        "| Ref | Form | Lemma | Gloss | Paronomastic? |",
        "|---|---|---|---|---|",
    ]
    for ex in inf['inf_abs_examples'][:30]:
        paro = 'yes' if ex['paronomastic'] else ''
        lines.append(
            f"| {book} {ex['chapter']}:{ex['verse']} "
            f"| {ex['text']} | {ex['lemma']} | {ex['gloss']} | {paro} |"
        )

    lines += [
        "",
        "---",
        "_Sources: MACULA Hebrew WLC (Clear Bible, CC BY 4.0)._",
    ]

    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Saved: {md_path}")
    return str(md_path)


# ═══════════════════════════════════════════════════════════════════════════════
# DISJUNCTIVE CLAUSE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
#
# In Biblical Hebrew prose, the normal (non-disjunctive) word order is VERB-first:
#   וַיֹּאמֶר אֱלֹהִים — "And God said" (wayyiqtol + subject)
#
# A disjunctive clause opens with a NON-VERB content word (noun, pronoun, or
# adjective), typically prefixed with וְ. Discourse grammarians (Longacre,
# Waltke-O'Connor, Niccacci) identify several functions:
#
#   Circumstantial  — background setting (Gen 1:2 וְהָאָרֶץ הָיְתָה תֹהוּ)
#   Contrastive     — adversative contrast (Gen 37:3 וְיִשְׂרָאֵל אָהַב)
#   Resumptive      — restarts after an embedded section
#   Flashback       — analeptic (going back in time to explain)
#   Summary/Comment — editorial aside or conclusion
#
# Detection heuristic:
#   A verse (or clause) is disjunctive when its FIRST CONTENT WORD
#   (skipping conjunctions, articles, prepositions) is NOT a verb.
#   We also classify the leading conjunction (וְ / וַ / כִּי / אֲבָל / רַק / אַךְ)
#   and the type of first content word (noun / pronoun / adjective / adverb).
#
# Limitation: MACULA does not mark clause boundaries within a verse.
# We work at verse granularity; within-verse disjunctions are not detected.
# ───────────────────────────────────────────────────────────────────────────────

# POS classes that can open a disjunctive clause
_DISJUNCTIVE_OPENERS = {'noun', 'pron', 'adj'}

# Classes that are transparent (skip over them to find first content word)
_TRANSPARENT = {'cj', 'art', 'prep', 'om', 'ptcl'}

# Conjunction lemmas and their discourse labels
_CONJ_LABELS = {
    'וְ':    'waw-disjunctive',
    'וַ':    'waw-disjunctive',
    'כִּי':  'ki (causal/asseverative)',
    'אֲבָל': 'aval (but)',
    'רַק':   'raq (only/however)',
    'אַךְ':  'akh (surely/however)',
    'אֶפֶס': 'efes (nevertheless)',
    'אוּלָם':'ulam (but)',
}

# Discourse function heuristics — based on the verb form that follows the
# subject-first opening.  These are approximations; context always wins.
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
        # Unusual — wayyiqtol after subject-first signals a strong contrast
        return 'contrastive'
    return 'nominal / comment'


def disjunctive_clauses(
    book: str,
    chapter: int | None = None,
) -> pd.DataFrame:
    """
    Find all disjunctive (noun/subject-first) clauses in a book or chapter.

    Returns a DataFrame with columns:
      chapter, verse, opener_text, opener_class, opener_type,
      leading_conj, verb_form, discourse_function, full_text
    """
    df = _load_macula()
    scope = _filter_book(df, book, chapter)

    # Group by verse
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

        # Collect leading conjunction (first token if class_=='cj')
        leading_conj = ''
        start_idx = 0
        if not verse_df.empty and verse_df.iloc[0]['class_'] == 'cj':
            leading_conj = _strip_diacritics(
                str(verse_df.iloc[0].get('lemma', '')))
            start_idx = 1

        # Find first content word (skip art/prep/om/ptcl after conj)
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

        # Disjunctive: opener is NOT a verb
        if opener_class in _DISJUNCTIVE_OPENERS:
            opener_type = str(first_content.get('type_', ''))
            opener_text = str(first_content.get('text', ''))

            # Find the first VERB in the verse for the form
            verb_rows = verse_df[verse_df['class_'] == 'verb']
            verb_form = ''
            if not verb_rows.empty:
                verb_form = str(verb_rows.iloc[0].get('type_', ''))

            # Full verse text (joined, first 60 chars)
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

    # Summary by discourse function
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
        print(f"  … ({len(df) - max_rows} more rows — use disjunctive_clauses() for full DataFrame)")
    print()


def disjunctive_in_chains(book: str, chapter: int) -> list[dict]:
    """
    Cross-reference wayyiqtol chains with disjunctive clauses in a chapter.

    Returns a list of dicts describing each wayyiqtol chain, annotated with
    any disjunctive clauses that appear WITHIN or IMMEDIATELY AFTER the chain.
    This reveals how disjunctives interrupt the narrative flow.

    Each dict has all fields from wayyiqtol_chains() plus:
      disjunctives_in_chain  : list of (verse, discourse_function) tuples
      interruption_type      : 'clean' | 'interrupted' | 'terminated-by-disj'
    """
    chains = wayyiqtol_chains(book, chapter)
    disj_df = disjunctive_clauses(book, chapter)
    disj_by_verse: dict[int, str] = {
        int(r['verse']): r['discourse_function']
        for _, r in disj_df.iterrows()
    }

    annotated = []
    for ch in chains:
        chain_verses = set(range(ch['start_verse'], ch['end_verse'] + 1))
        # Look one verse past the end of the chain too (terminating disjunctive)
        post_verse = ch['end_verse'] + 1

        disj_in = [(v, disj_by_verse[v])
                   for v in sorted(chain_verses)
                   if v in disj_by_verse]
        disj_post = disj_by_verse.get(post_verse)

        if disj_in:
            interruption = 'interrupted'
        elif disj_post:
            interruption = 'terminated-by-disj'
        else:
            interruption = 'clean'

        annotated.append({
            **ch,
            'disjunctives_in_chain': disj_in,
            'post_chain_disj':       disj_post,
            'interruption_type':     interruption,
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

    # Summary stats
    clean = sum(1 for c in annotated if c['interruption_type'] == 'clean')
    inter = sum(1 for c in annotated if c['interruption_type'] == 'interrupted')
    term  = sum(1 for c in annotated if c['interruption_type'] == 'terminated-by-disj')
    print(f"\n  Summary: {len(annotated)} chains — "
          f"{clean} clean · {inter} interrupted · {term} terminated-by-disjunctive")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# CONDITIONAL CLAUSE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
#
# Hebrew conditionals fall into three main types:
#
#  Real / open conditions — אִם + protasis (if X, then Y)
#    Protasis verb forms:
#      אִם + yiqtol  → open future condition (most common; "if you do…")
#      אִם + qatal   → present/past state ("if you have found…")
#      אִם + ptc     → stative/habitual ("if one goes…")
#
#  Irreal / contrary-to-fact — לוּ / לוּלֵא / לוּלֵי
#    לוּ + qatal  → wish or unfulfilled past ("if only…" / "would that…")
#    לוּלֵא       → "had it not been that…" (strong counterfactual)
#
#  Concessive / emphatic כִּי + אִם — "but only if / except"
#    (not handled separately here; classified as אִם)
#
# For each conditional token we record:
#   - the particle (אִם / לוּ / לוּלֵא)
#   - the first verb in the same verse / immediately following clause
#   - its form (yiqtol / qatal / participle / etc.)
#   - a condition_type label (real-future / real-past / real-stative /
#                              irreal-wish / irreal-counterfactual)
# ───────────────────────────────────────────────────────────────────────────────

# Stripped lemma → display label
_COND_PARTICLE_LABELS = {
    'אם':    'אִם (if)',
    'לו':    'לוּ (wish/irreal)',
    'לולא':  'לוּלֵא (had it not been)',
    'לולי':  'לוּלֵי (had it not been)',
    'הן':    'הֵן (if/behold — rare cond.)',
}

# Condition type based on particle + protasis verb form
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

    Detects אִם, לוּ, לוּלֵא, לוּלֵי, and conditionally הֵן.
    For each token records the particle, the first following verb form,
    and a condition_type classification.

    Returns DataFrame with columns:
      chapter, verse, particle, particle_label, protasis_verb_text,
      protasis_verb_form, protasis_verb_stem, condition_type,
      verse_text
    """
    df = _load_macula()
    scope = _filter_book(df, book, chapter).reset_index(drop=True)
    scope['_lem'] = scope['lemma'].apply(_strip_diacritics)

    # Particle classes we treat as conditional markers
    cond_stripped = set(_COND_PARTICLE_LABELS.keys())

    records = []
    for pos, row in scope.iterrows():
        lem = row['_lem']
        cls = str(row.get('class_', ''))

        # אִם: must be class cj (not the noun אֵם = mother)
        if lem == 'אם' and cls != 'cj':
            continue
        # הֵן: only class cj
        if lem == 'הן' and cls != 'cj':
            continue

        if lem not in cond_stripped:
            continue

        ch_val = row['chapter']
        vs_val = row['verse']
        bk_val = row['book']

        # Find first verb token in this verse (or next few tokens)
        proto_verb = None
        for offset in range(1, 20):
            npos = pos + offset
            if npos >= len(scope):
                break
            nrow = scope.iloc[npos]
            # Stay within the same verse (and next verse for לוּ which may
            # have the verb in the following verse)
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

        # Full verse text
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

    # Summary by condition_type
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
    """
    Return a summary DataFrame of conditional clause type counts for a book.

    Columns: condition_type, count, pct.
    """
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
