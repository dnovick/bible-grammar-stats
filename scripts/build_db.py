#!/usr/bin/env python3
"""Parse STEPBible TSV files and build the processed database."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bible_grammar.ingest import load_all
from bible_grammar.translations import load_translations
from bible_grammar.db import save, save_translations

if __name__ == "__main__":
    t0 = time.time()

    print("Loading TAHOT + TAGNT (Hebrew/Greek morphology)...")
    df = load_all()
    print(f"  {len(df):,} words loaded in {time.time()-t0:.1f}s")
    print(f"  OT: {(df.source=='TAHOT').sum():,}  NT: {(df.source=='TAGNT').sum():,}")
    save(df)

    print("\nLoading translations (KJV, Vulgate)...")
    t1 = time.time()
    tr = load_translations()
    print(f"  {len(tr):,} verses loaded in {time.time()-t1:.1f}s")
    save_translations(tr)

    print(f"\nAll done in {time.time()-t0:.1f}s")
