"""
Phrase search for Hebrew OT, Greek NT, and LXX.

Finds consecutive word sequences within a verse. Each position in the
phrase can be specified as a Strong's number, a lemma, a morphology
constraint dict, or a wildcard.

Usage
-----
from bible_grammar.phrase import phrase_search

# Hebrew: דְּבַר יְהוָה  "word of the LORD"
phrase_search(['H1697', 'H3068'])

# Greek NT: λόγος θεοῦ  "word of God"
phrase_search(['G3056', 'G2316'], corpus='NT')

# LXX: same phrase in Septuagint
phrase_search(['G3056', 'G2316'], corpus='LXX')

# Accept lemmas directly (resolved automatically)
phrase_search(['λόγος', 'θεός'], corpus='NT')
phrase_search(['דָּבָר', 'יְהוָה'], corpus='OT')

# Mixed: Niphal perfect followed by any noun
phrase_search([{'stem': 'Niphal', 'conjugation': 'Perfect'}, {'pos': 'Noun'}])

# Wildcard: word of ??? God  (any word between)
phrase_search(['H1697', '*', 'H0430'])

Constraint dict keys (for morphology-based positions):
  strongs, lemma, pos, stem, conjugation, tense, voice, mood,
  person, number, gender, case_, state
"""

from __future__ import annotations
import re
import unicodedata
import pandas as pd
from pathlib import Path
from . import db as _db

# Corpus identifiers
_OT  = "OT"
_NT  = "NT"
_LXX = "LXX"

_OT_BOOKS  = None
_NT_BOOKS  = None


def _ot_book_ids() -> set:
    global _OT_BOOKS
    if _OT_BOOKS is None:
        from .reference import all_book_ids
        _OT_BOOKS = set(all_book_ids("OT"))
    return _OT_BOOKS


def _nt_book_ids() -> set:
    global _NT_BOOKS
    if _NT_BOOKS is None:
        from .reference import all_book_ids
        _NT_BOOKS = set(all_book_ids("NT"))
    return _NT_BOOKS


# ── strongs normalisation ─────────────────────────────────────────────────────

def _norm_strongs(s: str) -> str:
    """Normalise a stored strongs value to H/G + unpadded number + optional letter.
    e.g. '{H0430G}' → 'H430G',  'H9003/{H1697I}' → 'H1697I' (content word),
         'G2316' → 'G2316'
    """
    # Hebrew: extract content word from curly braces, skip H9xxx grammatical tags
    braced = re.findall(r'\{([HG]\d+[A-Z]?)\}', s)
    for m in braced:
        if not re.match(r'H9\d+', m):
            # Strip leading zeros from numeric part
            pfx = m[0]
            rest = m[1:]
            num = re.match(r'0*(\d+)([A-Z]?)$', rest)
            if num:
                return pfx + num.group(1) + num.group(2)
            return m
    if braced:
        # All were H9xxx — return first anyway (shouldn't happen for content)
        m = braced[0]
        pfx = m[0]; rest = m[1:]
        num = re.match(r'0*(\d+)([A-Z]?)$', rest)
        return pfx + (num.group(1) + num.group(2) if num else rest)

    # Greek (plain, no braces): strip leading zeros
    m2 = re.match(r'^([HG])0*(\d+)([A-Z]?)$', s.strip().upper())
    if m2:
        return m2.group(1) + m2.group(2) + m2.group(3)
    return s.strip().upper()


def _query_strongs(s: str) -> str:
    """Normalise a user-supplied strongs for comparison against _norm_strongs output."""
    m = re.match(r'^([HG])0*(\d+)([A-Z]?)$', s.strip().upper())
    if m:
        return m.group(1) + m.group(2) + m.group(3)
    return s.strip().upper()


# ── token matching ────────────────────────────────────────────────────────────

def _resolve_token(token) -> dict:
    """
    Convert a user token to a canonical constraint dict with key 'strongs',
    'lemma', or morphology keys.

    Accepts: strongs string, lemma string, constraint dict, '*' wildcard.
    """
    if token is None or token == '*':
        return {'wildcard': True}

    if isinstance(token, dict):
        return token

    if isinstance(token, str):
        # Strong's number?
        if re.match(r'^[HG]\d', token.strip().upper()):
            return {'strongs': _query_strongs(token)}
        # Looks like a lemma — try to resolve
        from .wordstudy import resolve_strongs
        resolved = resolve_strongs(token)
        if resolved:
            return {'strongs': _query_strongs(resolved)}
        # Keep as lemma
        return {'lemma': unicodedata.normalize('NFC', token.strip().lower())}

    raise TypeError(f"Unsupported token type: {type(token)}")


def _matches_row(row: pd.Series, constraint: dict, is_lxx: bool = False) -> bool:
    """Check whether a single word row satisfies a constraint dict."""
    if constraint.get('wildcard'):
        return True

    if 'strongs' in constraint:
        norm = _norm_strongs(str(row.get('strongs', '')))
        target = constraint['strongs']
        # Strip trailing variant letter from both sides for root comparison
        norm_root   = re.sub(r'[A-Z]$', '', norm)
        target_root = re.sub(r'[A-Z]$', '', target)
        if norm_root != target_root:
            return False

    if 'lemma' in constraint:
        stored = unicodedata.normalize('NFC',
                     str(row.get('lemma', '')).strip().lower())
        if constraint['lemma'] not in stored:
            return False

    for key, col in [
        ('pos',         'part_of_speech'),
        ('stem',        'stem'),
        ('conjugation', 'conjugation'),
        ('tense',       'tense'),
        ('voice',       'voice'),
        ('mood',        'mood'),
        ('person',      'person'),
        ('number',      'number'),
        ('gender',      'gender'),
        ('case_',       'case_'),
        ('state',       'state'),
    ]:
        if key in constraint:
            val = str(row.get(col, '')).lower()
            if constraint[key].lower() not in val:
                return False

    return True


# ── main search ───────────────────────────────────────────────────────────────

def phrase_search(
    tokens: list,
    *,
    corpus: str = 'OT',
    book: str | list[str] | None = None,
    book_group: str | None = None,
    chapter: int | None = None,
    include_kjv: bool = True,
    max_results: int = 500,
) -> pd.DataFrame:
    """
    Search for a consecutive word sequence within verses.

    Parameters
    ----------
    tokens      : List of search tokens. Each element may be:
                    - A Strong's number string: 'H1697', 'G3056'
                    - A lemma string: 'λόγος', 'שָׁלוֹם', 'דָּבָר'
                    - A constraint dict: {'pos': 'Verb', 'stem': 'Niphal'}
                    - '*' or None — wildcard (matches any word)
    corpus      : 'OT' (Hebrew/Aramaic TAHOT), 'NT' (Greek TAGNT), or 'LXX'
    book        : Restrict to one book or list of books (book_id, e.g. 'Gen')
    book_group  : 'torah', 'prophets', 'writings', 'gospels', 'pauline'
    chapter     : Restrict to a single chapter number
    include_kjv : Attach KJV verse text to results (default True)
    max_results : Cap on number of results returned (default 500)

    Returns a DataFrame with columns:
      book_id, chapter, verse,
      word_1 .. word_N  (surface form of each matched word)
      strongs_1 .. strongs_N
      reference  (e.g. 'Gen 1:1')
      kjv_text   (if include_kjv=True)

    Examples
    --------
    # דְּבַר יְהוָה "word of the LORD" anywhere in OT
    phrase_search(['H1697', 'H3068'])

    # Same phrase in Jeremiah only
    phrase_search(['H1697', 'H3068'], book='Jer')

    # λόγος θεοῦ in NT
    phrase_search(['G3056', 'G2316'], corpus='NT')

    # Using lemmas
    phrase_search(['λόγος', 'θεός'], corpus='NT')

    # Niphal perfect followed by a noun in Isaiah
    phrase_search([{'stem': 'Niphal', 'conjugation': 'Perfect'}, {'pos': 'Noun'}],
                  book='Isa')

    # Wildcard: H1697 + anything + H3068
    phrase_search(['H1697', '*', 'H3068'])
    """
    from .reference import TORAH, PROPHETS, WRITINGS, GOSPELS, PAULINE

    corpus = corpus.upper()
    is_lxx = (corpus == _LXX)

    # Load appropriate dataframe
    if is_lxx:
        df = _db.load_lxx()
        df = df[~df['is_deuterocanon']].copy()
    else:
        df = _db.load()
        if corpus == _OT:
            df = df[df['source'] == 'TAHOT'].copy()
        else:
            df = df[df['source'] == 'TAGNT'].copy()

    # Book / group filters
    if book_group is not None:
        groups = {'torah': TORAH, 'prophets': PROPHETS, 'writings': WRITINGS,
                  'gospels': GOSPELS, 'pauline': PAULINE}
        grp = groups.get(book_group.lower())
        if grp is None:
            raise ValueError(f"Unknown book_group {book_group!r}")
        df = df[df['book_id'].isin(grp)]
    if book is not None:
        vals = [book] if isinstance(book, str) else book
        df = df[df['book_id'].isin(vals)]
    if chapter is not None:
        df = df[df['chapter'] == chapter]

    if df.empty:
        return pd.DataFrame()

    # Resolve tokens to constraint dicts
    constraints = [_resolve_token(t) for t in tokens]
    n = len(constraints)

    if n == 0:
        return pd.DataFrame()

    # Sort by position
    df = df.sort_values(['book_id', 'chapter', 'verse', 'word_num']).reset_index(drop=True)

    # Build a set of candidate starting rows for position 0
    # For efficiency, pre-filter on the first non-wildcard constraint
    first_real = next((i for i, c in enumerate(constraints) if not c.get('wildcard')), None)

    rows_out = []

    # Group by verse for efficient consecutive-word checking
    for (book_id, ch, vs), verse_df in df.groupby(['book_id', 'chapter', 'verse'],
                                                    sort=False):
        verse_df = verse_df.sort_values('word_num').reset_index(drop=True)
        words = verse_df.to_dict('records')
        nw = len(words)

        if nw < n:
            continue

        for start in range(nw - n + 1):
            matched = True
            for offset, constraint in enumerate(constraints):
                if not _matches_row(words[start + offset], constraint, is_lxx):
                    matched = False
                    break
            if matched:
                row: dict = {
                    'book_id':   book_id,
                    'chapter':   ch,
                    'verse':     vs,
                    'reference': f"{book_id} {ch}:{vs}",
                }
                for offset in range(n):
                    w = words[start + offset]
                    row[f'word_{offset+1}']    = w.get('word', '')
                    row[f'strongs_{offset+1}'] = _norm_strongs(str(w.get('strongs', '')))
                    if is_lxx:
                        row[f'lemma_{offset+1}'] = w.get('lemma', '')
                rows_out.append(row)
                if len(rows_out) >= max_results:
                    break
        if len(rows_out) >= max_results:
            break

    if not rows_out:
        return pd.DataFrame()

    result = pd.DataFrame(rows_out)

    # Attach KJV text
    if include_kjv:
        try:
            tr = _db.load_translations()
            kjv = tr[tr['translation'] == 'KJV'][['book_id', 'chapter', 'verse', 'text']]
            kjv = kjv.rename(columns={'text': 'kjv_text'})
            result = result.merge(kjv, on=['book_id', 'chapter', 'verse'], how='left')
        except Exception:
            pass

    return result.reset_index(drop=True)


def print_phrase_results(
    df: pd.DataFrame,
    *,
    max_rows: int = 30,
    show_strongs: bool = False,
) -> None:
    """Print phrase search results in a readable format."""
    if df.empty:
        print("  No matches found.")
        return

    total = len(df)
    shown = min(total, max_rows)
    print(f"  {total:,} match{'es' if total != 1 else ''}"
          f"{' (showing first ' + str(shown) + ')' if total > max_rows else ''}:\n")

    word_cols = [c for c in df.columns if c.startswith('word_')]
    strongs_cols = [c for c in df.columns if c.startswith('strongs_')]
    lemma_cols = [c for c in df.columns if c.startswith('lemma_')]

    for _, row in df.head(max_rows).iterrows():
        words = '  '.join(str(row[c]) for c in word_cols)
        ref = row['reference']
        print(f"  [{ref}]  {words}")
        if show_strongs:
            strongs = '  '.join(str(row[c]) for c in strongs_cols)
            print(f"           {strongs}")
        if 'kjv_text' in row and pd.notna(row['kjv_text']):
            text = str(row['kjv_text'])
            if len(text) > 100:
                text = text[:97] + '...'
            print(f"    {text}")
    print()
