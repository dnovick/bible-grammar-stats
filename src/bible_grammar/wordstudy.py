"""
Word study tool: one-stop profile for any Hebrew or Greek lemma.

Combines lexicon definitions (TBESH/TBESG), corpus statistics,
morphological form inventory, LXX translation equivalents (for Hebrew),
and example verses into a single structured result.

Usage
-----
from bible_grammar.wordstudy import word_study, print_word_study

# Hebrew word by Strong's
word_study('H1254')     # בָּרָא "to create"

# Greek word by Strong's
word_study('G4160')     # ποιέω "to do/make"

# Print formatted output
print_word_study('H1254')
print_word_study('G4160')
"""

from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
from . import db as _db
from .reference import BOOKS, book_info, all_book_ids

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TBESH = _REPO_ROOT / "stepbible-data" / "Lexicons" / \
    "TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt"
_TBESG = _REPO_ROOT / "stepbible-data" / "Lexicons" / \
    "TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt"

_BOOK_ORDER = {b[0]: b[3] for b in BOOKS}

# Module-level caches
_heb_lex: dict | None = None
_grk_lex: dict | None = None
_words_cache: pd.DataFrame | None = None
_lxx_cache: pd.DataFrame | None = None
_tr_cache: pd.DataFrame | None = None


def _words() -> pd.DataFrame:
    global _words_cache
    if _words_cache is None:
        _words_cache = _db.load()
    return _words_cache


def _lxx() -> pd.DataFrame:
    global _lxx_cache
    if _lxx_cache is None:
        _lxx_cache = _db.load_lxx()
    return _lxx_cache


def _translations() -> pd.DataFrame:
    global _tr_cache
    if _tr_cache is None:
        _tr_cache = _db.load_translations()
    return _tr_cache


def _clean_def(raw: str) -> str:
    """Strip HTML tags and normalize whitespace from lexicon definition."""
    text = re.sub(r'<[^>]+>', '', raw)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _load_heb_lex() -> dict:
    global _heb_lex
    if _heb_lex is not None:
        return _heb_lex
    if not _TBESH.exists():
        return {}
    result: dict[str, dict] = {}
    with open(_TBESH, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or line.startswith("=") or line.startswith("TBESH"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            # col2 = canonical extended strongs (H1234A), col3 = lemma,
            # col4 = translit, col5 = type, col6 = short gloss, col7 = definition
            ext_id = parts[2].strip()           # e.g. H1254A
            base   = re.sub(r'[A-Z]$', '', ext_id)  # H1254
            lemma  = parts[3].strip()
            translit = parts[4].strip()
            gloss  = parts[6].strip() if len(parts) > 6 else ""
            defn   = _clean_def(parts[7]) if len(parts) > 7 else ""
            pos_code = parts[5].strip()  # e.g. H:V, H:N-M, N:N-M-P

            # Index by both base and extended id
            for key in (base, ext_id):
                if key not in result:
                    result[key] = {
                        "strongs": ext_id, "lemma": lemma,
                        "translit": translit, "pos_code": pos_code,
                        "gloss": gloss, "definition": defn,
                    }
    _heb_lex = result
    return _heb_lex


def _load_grk_lex() -> dict:
    global _grk_lex
    if _grk_lex is not None:
        return _grk_lex
    if not _TBESG.exists():
        return {}
    result: dict[str, dict] = {}
    with open(_TBESG, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or line.startswith("=") or line.startswith("TBESG"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            ext_id   = parts[2].strip()   # e.g. G4160G
            base     = re.sub(r'[A-Z]$', '', ext_id)  # G4160
            lemma    = parts[3].strip()
            translit = parts[4].strip()
            pos_code = parts[5].strip()
            gloss    = parts[6].strip()
            defn     = _clean_def(parts[7]) if len(parts) > 7 else ""

            for key in (base, ext_id):
                if key not in result:
                    result[key] = {
                        "strongs": ext_id, "lemma": lemma,
                        "translit": translit, "pos_code": pos_code,
                        "gloss": gloss, "definition": defn,
                    }
    _grk_lex = result
    return _grk_lex


def _build_lemma_index() -> tuple[dict, dict]:
    """Return (heb_lemma→strongs, grk_lemma→strongs) reverse lookup dicts."""
    import unicodedata
    heb_idx: dict[str, str] = {}
    for k, v in _load_heb_lex().items():
        lemma = v.get("lemma", "").strip()
        if not lemma or not k.startswith("H"):
            continue
        num_part = k[1:].rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if not num_part.isdigit():
            continue
        nfc = unicodedata.normalize("NFC", lemma)
        if nfc not in heb_idx:
            heb_idx[nfc] = k
        # Also index without vowel points (consonants only)
        consonants = re.sub(r'[֑-ׇ]', '', nfc)
        if consonants not in heb_idx:
            heb_idx[consonants] = k

    grk_idx: dict[str, str] = {}
    for k, v in _load_grk_lex().items():
        lemma = v.get("lemma", "").strip()
        if not lemma or not k.startswith("G"):
            continue
        num_part = k[1:].rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if not num_part.isdigit():
            continue
        nfc = unicodedata.normalize("NFC", lemma.lower())
        if nfc not in grk_idx:
            grk_idx[nfc] = k

    return heb_idx, grk_idx


def resolve_strongs(term: str) -> str | None:
    """
    Resolve a term to a Strong's number.

    Accepts:
      - A Strong's number directly: 'H1285', 'G3056'
      - A Hebrew lemma (with or without vowel points): 'שָׁלוֹם', 'שלום'
      - A Greek lemma: 'λόγος', 'εἰρήνη'

    Returns the Strong's number string, or None if not found.
    """
    import unicodedata
    term = term.strip()

    # Direct strongs number
    if re.match(r'^[HG]\d', term.upper()):
        return term.upper()

    nfc = unicodedata.normalize("NFC", term)
    heb_idx, grk_idx = _build_lemma_index()

    # Try Hebrew (with vowels, then without)
    result = heb_idx.get(nfc)
    if result:
        return result
    consonants = re.sub(r'[֑-ׇ]', '', nfc)
    result = heb_idx.get(consonants)
    if result:
        return result

    # Try Greek (case-insensitive)
    result = grk_idx.get(nfc.lower())
    if result:
        return result

    return None


def _lookup_lex(strongs: str) -> dict | None:
    """Look up a Strong's number in the appropriate lexicon."""
    clean = strongs.strip("{}").upper()
    # Try direct, then zero-padded (H157 → H0157), then strip variant suffix
    m = re.match(r'^([HG])(\d+)([A-Z]?)$', clean)
    zero_padded = (f"{m.group(1)}{int(m.group(2)):04d}{m.group(3)}" if m else clean)
    base = re.sub(r'[A-Z]$', '', clean)
    base_padded = (f"{m.group(1)}{int(m.group(2)):04d}" if m else base)

    if clean.startswith("H"):
        lex = _load_heb_lex()
    elif clean.startswith("G"):
        lex = _load_grk_lex()
    else:
        return None

    return (lex.get(clean) or lex.get(zero_padded) or
            lex.get(base) or lex.get(base_padded))


def _kjv_verse(book_id: str, chapter: int, verse: int) -> str:
    tr = _translations()
    row = tr[
        (tr["book_id"] == book_id) &
        (tr["chapter"] == chapter) &
        (tr["verse"] == verse) &
        (tr["translation"] == "KJV")
    ]
    return row.iloc[0]["text"] if not row.empty else ""


def word_study(strongs: str, *, example_verses: int = 5) -> dict:
    """
    Complete word study for a Strong's number.

    Parameters
    ----------
    strongs        : e.g. 'H1254', 'H1254A', 'G4160', 'G4160G'
    example_verses : Number of example verses to include (default 5)

    Returns a dict with keys:
      strongs, lemma, translit, gloss, pos_code, definition,
      total_occurrences, by_book (DataFrame),
      morphological_forms (DataFrame),
      translation_equivalents (OT Hebrew only, DataFrame),
      nt_usage (OT Hebrew only — NT occurrences if any),
      lxx_usage (OT Hebrew only — LXX Greek equivalent stats),
      examples (list of {reference, word, context} dicts)
    """
    clean = strongs.strip("{}").upper()
    is_hebrew = clean.startswith("H")

    # --- Lexicon ---
    lex = _lookup_lex(clean)
    if lex is None:
        lex = {"strongs": clean, "lemma": "", "translit": "",
               "gloss": "(not found in lexicon)", "definition": "", "pos_code": ""}

    result = {
        "strongs": clean,
        "lemma": lex["lemma"],
        "translit": lex["translit"],
        "gloss": lex["gloss"],
        "pos_code": lex["pos_code"],
        "definition": lex["definition"],
    }

    # --- Corpus occurrences ---
    df = _words()
    source = "TAHOT" if is_hebrew else "TAGNT"
    corpus = df[df["source"] == source]

    # Match on strongs column using a regex that anchors the number to avoid
    # false positives (e.g. H157 matching H1571, H1573 etc.)
    # Hebrew strongs are wrapped in curly braces: {H1254A}, H9003/{H1254A}
    # Greek strongs are plain: G4160, G4160G
    m_clean = re.match(r'^([HG])0*(\d+)([A-Z]?)$', clean)
    if m_clean:
        pfx, num, suf = m_clean.groups()
        # Match the number with optional leading zeros and optional trailing variant letter
        pat = rf'\{{{pfx}0*{num}[A-Z]?\}}' if is_hebrew else rf'\b{pfx}0*{num}[A-Z]?\b'
    else:
        pat = re.escape(clean)
    mask = corpus["strongs"].str.upper().str.contains(pat, regex=True, na=False)
    base = re.sub(r'[A-Z]$', '', clean)

    hits = corpus[mask].copy()
    result["total_occurrences"] = len(hits)

    if hits.empty:
        result.update({
            "by_book": pd.DataFrame(), "morphological_forms": pd.DataFrame(),
            "translation_equivalents": pd.DataFrame(), "examples": [],
        })
        return result

    # --- By book ---
    by_book = (
        hits.groupby("book_id").size()
        .reset_index(name="count")
        .assign(book_name=lambda d: d["book_id"].apply(
            lambda b: book_info(b)["name"] if b in {bk[0] for bk in BOOKS} else b))
        .assign(_order=lambda d: d["book_id"].map(_BOOK_ORDER).fillna(99))
        .sort_values("_order")
        .drop(columns="_order")
    )
    total = by_book["count"].sum()
    by_book["pct"] = (by_book["count"] / total * 100).round(1)
    result["by_book"] = by_book[["book_id", "book_name", "count", "pct"]].reset_index(drop=True)

    # --- Morphological forms ---
    if is_hebrew:
        form_cols = ["stem", "conjugation", "part_of_speech", "state"]
    else:
        form_cols = ["tense", "voice", "mood", "part_of_speech"]
    form_cols = [c for c in form_cols if c in hits.columns]

    morph = (
        hits.groupby(form_cols, dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    morph["pct"] = (morph["count"] / len(hits) * 100).round(1)
    result["morphological_forms"] = morph.reset_index(drop=True)

    # --- Translation equivalents (Hebrew OT → LXX) ---
    if is_hebrew:
        # Prefer word-level IBM Model 1 alignment; fall back to verse-level
        te = pd.DataFrame()
        try:
            from .ibm_align import translation_equivalents_w
            te = translation_equivalents_w(heb_strongs=clean, top_n=15, min_count=1)
        except Exception:
            pass
        if te.empty:
            try:
                from .alignment import translation_equivalents
                te = translation_equivalents(heb_strongs=clean, top_n=15, min_count=1)
            except Exception:
                pass
        result["translation_equivalents"] = te

        # NT usage of the primary LXX equivalent (OT → LXX → NT trajectory)
        nt_equiv: list[dict] = []
        if not te.empty:
            grk_lex = _load_grk_lex()
            nt_df = df[df["source"] == "TAGNT"]
            for _, te_row in te.head(3).iterrows():
                g_strongs = te_row.get("lxx_strongs", "")
                if not g_strongs or g_strongs == "__NULL__":
                    continue
                g_base = re.sub(r'[A-Z]$', '', g_strongs.upper())
                nt_hits = nt_df[nt_df["strongs"].str.upper().str.contains(g_base, na=False)]
                if nt_hits.empty:
                    continue
                nt_by_book = (
                    nt_hits.groupby("book_id").size()
                    .reset_index(name="count")
                    .assign(_order=lambda d: d["book_id"].map(_BOOK_ORDER).fillna(99))
                    .sort_values("_order").drop(columns="_order")
                )
                g_lemma = te_row.get("lxx_lemma", "")
                if not g_lemma and g_strongs in grk_lex:
                    g_lemma = grk_lex[g_strongs]["lemma"]
                nt_equiv.append({
                    "strongs": g_strongs,
                    "lemma": g_lemma,
                    "nt_total": len(nt_hits),
                    "nt_by_book": nt_by_book,
                })
        result["nt_lxx_equiv"] = nt_equiv
    else:
        result["translation_equivalents"] = pd.DataFrame()
        result["nt_lxx_equiv"] = []

    # --- Example verses ---
    hits_sorted = hits.copy()
    hits_sorted["_order"] = hits_sorted["book_id"].map(_BOOK_ORDER).fillna(99)
    hits_sorted = hits_sorted.sort_values(["_order", "chapter", "verse", "word_num"])

    examples = []
    seen_verses: set = set()
    for _, row in hits_sorted.iterrows():
        ref = (row["book_id"], int(row["chapter"]), int(row["verse"]))
        if ref in seen_verses:
            continue
        seen_verses.add(ref)
        kjv = _kjv_verse(*ref)
        examples.append({
            "reference": f"{row['book_id']} {row['chapter']}:{row['verse']}",
            "word": row["word"],
            "context": kjv,
        })
        if len(examples) >= example_verses:
            break

    result["examples"] = examples
    return result


def print_word_study(strongs: str, *, example_verses: int = 5) -> None:
    """Print a formatted word study to stdout."""
    ws = word_study(strongs, example_verses=example_verses)

    is_hebrew = ws["strongs"].startswith("H")
    lang = "Hebrew" if is_hebrew else "Greek"

    print(f"\n{'='*65}")
    print(f"  Word Study: {ws['strongs']}  —  {lang}")
    print(f"{'='*65}")
    if ws["lemma"]:
        print(f"  Lemma       : {ws['lemma']}")
    if ws["translit"]:
        print(f"  Translit    : {ws['translit']}")
    if ws["gloss"]:
        print(f"  Gloss       : {ws['gloss']}")
    if ws["pos_code"]:
        print(f"  POS code    : {ws['pos_code']}")
    print(f"  Occurrences : {ws['total_occurrences']:,}")
    print()

    if ws["definition"]:
        print("  Definition:")
        defn = ws["definition"]
        # Wrap at ~70 chars
        words = defn.split()
        line, out_lines = [], []
        for w in words:
            line.append(w)
            if len(" ".join(line)) > 68:
                out_lines.append("    " + " ".join(line[:-1]))
                line = [w]
        if line:
            out_lines.append("    " + " ".join(line))
        print("\n".join(out_lines))
        print()

    print("  Distribution by Book (top 15):")
    by_book = ws["by_book"].head(15)
    for _, row in by_book.iterrows():
        bar = "█" * min(int(row["pct"] / 2), 25)
        print(f"    {row['book_name']:<20} {row['count']:4d}  ({row['pct']:5.1f}%)  {bar}")

    print()
    print("  Morphological Forms (top 10):")
    morph = ws["morphological_forms"].head(10)
    print(morph.to_string(index=False))

    if is_hebrew and not ws["translation_equivalents"].empty:
        print()
        print("  LXX Translation Equivalents (word-level alignment, top 10):")
        te = ws["translation_equivalents"].head(10)
        print(te.to_string(index=False))

    if is_hebrew and ws.get("nt_lxx_equiv"):
        print()
        print("  OT → LXX → NT Trajectory:")
        for equiv in ws["nt_lxx_equiv"]:
            print(f"    {equiv['lemma']} ({equiv['strongs']})  —  {equiv['nt_total']:,} NT occurrences")
            nt_bb = equiv["nt_by_book"].head(8)
            for _, row in nt_bb.iterrows():
                print(f"      {row['book_id']:<10} {row['count']:4d}")

    print()
    print(f"  Example Verses:")
    for ex in ws["examples"]:
        print(f"    [{ex['reference']}]  {ex['word']}")
        if ex["context"]:
            ctx = ex["context"]
            if len(ctx) > 90:
                ctx = ctx[:87] + "..."
            print(f"      {ctx}")
    print()


def word_study_table(strongs: str) -> pd.DataFrame:
    """
    Compact tabular form of a word study — one row per occurrence,
    with reference, inflected form, morphology, and KJV verse.
    Equivalent to concordance() but with lexicon gloss in the header.
    """
    from .concordance import concordance
    clean = strongs.strip("{}").upper()
    is_hebrew = clean.startswith("H")
    corpus = "OT" if is_hebrew else "NT"

    df = concordance(strongs=clean, corpus=corpus, context="KJV")

    lex = _lookup_lex(clean)
    if lex:
        df.attrs["gloss"] = lex["gloss"]
        df.attrs["lemma"] = lex["lemma"]
        df.attrs["translit"] = lex["translit"]

    return df
