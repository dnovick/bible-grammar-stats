"""Persist and load the word DataFrame to/from SQLite and Parquet."""

from pathlib import Path
import pandas as pd
from .reference import BOOKS

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROCESSED = _REPO_ROOT / "data" / "processed"
DB_PATH = _PROCESSED / "bible_grammar.db"
PARQUET_PATH = _PROCESSED / "words.parquet"
TRANSLATIONS_PARQUET = _PROCESSED / "translations.parquet"


def save(df: pd.DataFrame, db_path: Path = DB_PATH,
         parquet_path: Path = PARQUET_PATH) -> None:
    """Write DataFrame to SQLite and Parquet. Creates directories if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Parquet — fast reload
    df.to_parquet(parquet_path, index=False)
    print(f"Saved Parquet: {parquet_path}  ({len(df):,} rows)")

    # SQLite — ad-hoc SQL queries
    import sqlite3
    with sqlite3.connect(db_path) as con:
        df.to_sql("words", con, if_exists="replace", index=True,
                  index_label="id")

        # books lookup table
        books_df = pd.DataFrame(
            BOOKS,
            columns=["book_id", "name", "testament", "canonical_order", "chapter_count"],
        )
        books_df.to_sql("books", con, if_exists="replace", index=False)

        con.execute("CREATE INDEX IF NOT EXISTS idx_book ON words(book_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_pos ON words(part_of_speech)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_stem ON words(stem)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_conj ON words(conjugation)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_source ON words(source)")

    print(f"Saved SQLite:  {db_path}")


def save_translations(df: pd.DataFrame, db_path: Path = DB_PATH,
                      parquet_path: Path = TRANSLATIONS_PARQUET) -> None:
    """Write the translations DataFrame to SQLite and Parquet."""
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    print(f"Saved Parquet: {parquet_path}  ({len(df):,} rows)")

    import sqlite3
    with sqlite3.connect(db_path) as con:
        df.to_sql("translations", con, if_exists="replace", index=True,
                  index_label="id")
        con.execute("CREATE INDEX IF NOT EXISTS idx_tr_book ON translations(book_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_tr_trans ON translations(translation)")
    print(f"Saved SQLite translations table: {db_path}")


def load_translations(parquet_path: Path = TRANSLATIONS_PARQUET) -> pd.DataFrame:
    """Load translation verses from Parquet."""
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if DB_PATH.exists():
        import sqlite3
        with sqlite3.connect(DB_PATH) as con:
            return pd.read_sql("SELECT * FROM translations", con)
    raise FileNotFoundError(
        f"No translations data found. Run: python scripts/build_db.py"
    )


def load(parquet_path: Path = PARQUET_PATH) -> pd.DataFrame:
    """Load from Parquet (fast). Falls back to SQLite if Parquet not found."""
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if DB_PATH.exists():
        import sqlite3
        with sqlite3.connect(DB_PATH) as con:
            return pd.read_sql("SELECT * FROM words", con)
    raise FileNotFoundError(
        f"No processed data found at {parquet_path} or {DB_PATH}.\n"
        "Run: python scripts/build_db.py"
    )


def is_built() -> bool:
    return PARQUET_PATH.exists() or DB_PATH.exists()
