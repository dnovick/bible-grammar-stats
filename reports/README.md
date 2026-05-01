# Reports

Markdown reports for generated Bible grammar charts. Each file embeds its chart and
includes a summary, key observations, and data notes.

## Hebrew Old Testament

| Report | Description |
|---|---|
| [hebrew-verb-stems-ot-total.md](hebrew-verb-stems-ot-total.md) | All Hebrew verb stems across the entire OT |
| [hebrew-verb-stems-genesis.md](hebrew-verb-stems-genesis.md) | Verb stem distribution in Genesis |
| [hebrew-verb-stems-torah-by-book.md](hebrew-verb-stems-torah-by-book.md) | Top 6 stems compared across all five Torah books |
| [niphal-perfects-by-book.md](niphal-perfects-by-book.md) | Niphal Perfect counts for every OT book |
| [niphal-perfects-by-book-top20.md](niphal-perfects-by-book-top20.md) | Top 20 OT books by Niphal Perfect count |

## Special Studies

| Report | Description |
|---|---|
| [2fp-perfect-verbs.md](2fp-perfect-verbs.md) | All 13 2nd person feminine plural perfect verbs in the OT, by book and stem |
| [hapax-legomena-by-book.md](hapax-legomena-by-book.md) | Hapax legomena counts by book for OT and NT, with sample lists |

## Greek New Testament

| Report | Description |
|---|---|
| [greek-nt-tense-voice-heatmap.md](greek-nt-tense-voice-heatmap.md) | Tense × Voice heatmap for all NT verbs |
| [greek-pauline-tense-voice-heatmap.md](greek-pauline-tense-voice-heatmap.md) | Tense × Voice heatmap for Paul's letters |
| [greek-aorist-passives-by-nt-book.md](greek-aorist-passives-by-nt-book.md) | Aorist Passive verb counts by NT book |

## Per-Book Language Profiles

Generated reports in `profiles/` — one file per book. Available for: Gen, Exo, Psa, Isa, Dan, Mat, Jhn, Rom, Heb, Rev (and any book via `save_profile_report()`).

| Report | Description |
|---|---|
| [profiles/Gen_profile.md](profiles/Gen_profile.md) | Genesis |
| [profiles/Isa_profile.md](profiles/Isa_profile.md) | Isaiah |
| [profiles/Rom_profile.md](profiles/Rom_profile.md) | Romans |
| [profiles/Heb_profile.md](profiles/Heb_profile.md) | Hebrews |

*See `notebooks/06_book_profiles.ipynb` for cross-book comparisons and batch generation.*

## Translation & Cross-Testament

| Report | Description |
|---|---|
| [nt_quotations_overview.md](nt_quotations_overview.md) | NT→OT quotation density by book, highest-confidence pairs, three-way text comparison |

---
*Charts are in `../output/charts/`. Regenerate with `notebooks/02_query_demo.ipynb` or `notebooks/03_statistics.ipynb`.*  
*NT quotations notebook: `notebooks/04_nt_quotations.ipynb`.*
