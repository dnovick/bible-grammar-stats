"""Clause type profile and nominal vs. verbal clause analysis."""
from __future__ import annotations

import pandas as pd

from ._common import _load_macula, _filter_book, _strip_diacritics

_NEGATION_LEMMAS = {'לֹא', 'אַל', 'בַּל', 'לְבַלְתִּי', 'אֵין', 'בְּלִי', 'לֹא'}
_CONDITIONAL_LEMMAS = {'אִם', 'לוּ', 'לוּלֵא', 'לוּלֵי', 'הֵן', 'הִן'}
_RELATIVE_LEMMAS = {'אֲשֶׁר', 'שֶׁ'}

_NEG_STRIPPED = {_strip_diacritics(lem) for lem in _NEGATION_LEMMAS}
_COND_STRIPPED = {_strip_diacritics(lem) for lem in _CONDITIONAL_LEMMAS}
_REL_STRIPPED = {_strip_diacritics(lem) for lem in _RELATIVE_LEMMAS}


def clause_type_profile(book: str) -> pd.DataFrame:
    """
    Compute clause-type statistics for a book.

    Returns a DataFrame with columns: feature, count, per_100_verses.
    Features: verbal_clauses, nominal_clauses, negations, conditionals,
              relative_clauses, questions, total verses.
    """
    df = _load_macula()
    book_df = _filter_book(df, book)

    n_verses = book_df[['chapter', 'verse']].drop_duplicates().shape[0]

    verbal = (book_df[book_df['role'] == 'v']
              .groupby(['chapter', 'verse'])
              .size()
              .reset_index(name='n'))
    n_verbal = len(verbal)

    v_refs = set(zip(book_df[book_df['role'] == 'v']['chapter'],
                     book_df[book_df['role'] == 'v']['verse']))
    p_refs = set(zip(book_df[book_df['role'] == 'p']['chapter'],
                     book_df[book_df['role'] == 'p']['verse']))
    n_nominal = len(p_refs - v_refs)

    book_df = book_df.copy()
    book_df['_lem_stripped'] = book_df['lemma'].apply(
        lambda x: _strip_diacritics(str(x)))
    n_neg = int((book_df['_lem_stripped'].isin(_NEG_STRIPPED)).sum())
    n_cond = int((book_df['_lem_stripped'].isin(_COND_STRIPPED)).sum())
    n_rel = int((book_df['_lem_stripped'].isin(_REL_STRIPPED)).sum())
    n_q = int((book_df['type_'] == 'interrogative').sum())

    records = [
        ('verbal clauses',        n_verbal,  round(n_verbal / n_verses * 100, 1)),
        ('nominal clauses',       n_nominal, round(n_nominal / n_verses * 100, 1)),
        ('negation tokens',       n_neg,     round(n_neg / n_verses * 100, 1)),
        ('conditional (אם/לו)',   n_cond,    round(n_cond / n_verses * 100, 1)),
        ('relative clauses',      n_rel,     round(n_rel / n_verses * 100, 1)),
        ('interrogative',         n_q,       round(n_q / n_verses * 100, 1)),
        ('total verses',          n_verses,  100.0),
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
