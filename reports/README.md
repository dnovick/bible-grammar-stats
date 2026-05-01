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
| [nouns-by-gender-by-book.md](nouns-by-gender-by-book.md) | Noun gender distribution (M/F/Both/Proper for OT; M/F/N for NT) per book |
| [verb-morphology-by-book.md](verb-morphology-by-book.md) | OT verb stems (binyanim) and NT verb tense/mood distribution per book |
| [nt-case-distribution-by-book.md](nt-case-distribution-by-book.md) | Greek NT case distribution (Nom/Gen/Acc/Dat/Voc) per book |
| [ot-hebrew-aramaic-by-book.md](ot-hebrew-aramaic-by-book.md) | Hebrew vs. Aramaic word counts for every OT book; Daniel and Ezra Aramaic sections |

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

## Word Studies (reports/)

| Report | Description |
|---|---|
| [obey-greek-word-study.md](obey-greek-word-study.md) | NT usage of ὑπακούω, ὑπακοή, πείθω, πειθαρχέω, ὑποτάσσω, ὑπήκοος with tense/voice/mood/KJV context. LXX analysis showing πείθω almost exclusively translates בָּטַח (trust), not obedience words. Zephaniah 3:2 as a key illustration. |

## Semantic Profiles (output/reports/)

Pre-generated semantic profiles in `../output/reports/`. Each file includes a lexicon entry, frequency by book, morphological forms, LXX equivalents and consistency, OT→LXX→NT trajectory, top collocates, and example verses.

| Report | Description |
|---|---|
| [../output/reports/h7965-semantic-profile.md](../output/reports/h7965-semantic-profile.md) | שָׁלוֹם (shalom / peace), H7965 |
| [../output/reports/h1285-semantic-profile.md](../output/reports/h1285-semantic-profile.md) | בְּרִית (covenant), H1285 |
| [../output/reports/h7307-semantic-profile.md](../output/reports/h7307-semantic-profile.md) | רוּחַ (spirit/wind), H7307 |
| [../output/reports/g3056-semantic-profile.md](../output/reports/g3056-semantic-profile.md) | λόγος (word), G3056 |

## Divine Names (output/reports/)

| Report | Description |
|---|---|
| [../output/reports/divine-names-report.md](../output/reports/divine-names-report.md) | Distribution of YHWH, Elohim, Adonai, El, Yah, Shaddai in OT Hebrew; Kyrios and Theos in the LXX; Theos, Kyrios, Iesous, Christos, Pater, Pneuma in the NT. Includes distribution by book and canonical section, stacked bar charts, and heatmaps. |

## Genre Comparison (output/reports/)

| Report | Description |
|---|---|
| [../output/reports/genre-comparison-report.md](../output/reports/genre-comparison-report.md) | Verb stem, conjugation, and POS distribution across Torah/Historical/Wisdom/Prophets (OT) and Gospels/Pauline/General (NT). Heatmap charts for each feature. Key findings: wayyiqtol dominates Historical prose (36%), Imperfect dominates Wisdom (31%), Paul's letters have highest Present tense ratio (55%). |

## Intertextuality (output/reports/)

Pre-generated intertextuality network reports in `../output/reports/`. Each includes a network graph, NT book coverage summary, full citation table with KJV text, and verse-by-verse detail.

| Report | Description |
|---|---|
| [../output/reports/isa-53-intertextuality.md](../output/reports/isa-53-intertextuality.md) | Isaiah 53: 26 NT citations across 13 books (min votes 20) |
| [../output/reports/psa-22-intertextuality.md](../output/reports/psa-22-intertextuality.md) | Psalm 22 (min votes 15) |
| [../output/reports/isa-intertextuality.md](../output/reports/isa-intertextuality.md) | Full Isaiah: 224+ links to 20 NT books (min votes 50) |

---
*Charts are in `../output/charts/`. Regenerate with `notebooks/02_query_demo.ipynb` or `notebooks/03_statistics.ipynb`.*  
*NT quotations notebook: `notebooks/04_nt_quotations.ipynb`.*  
*HTML and CSV exports are generated to `../output/exports/` (gitignored; regenerate via `/export`).*
