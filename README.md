# Bible Grammar Stats

A Python project for generating statistics, charts, and reports on the grammatical
constructs of the biblical text — Hebrew and Aramaic Old Testament, Greek New Testament,
Greek Septuagint (LXX), and English/Latin translations.

The LXX (Septuagint) is the ancient Greek translation of the Hebrew scriptures, and plays
a central role in this project: it bridges the Hebrew OT and Greek NT vocabulary, and is
the primary text NT authors quote when citing the Old Testament. This project supports
word-level alignment between the Hebrew OT and the LXX, per-book translation consistency
analysis, and NT quotation alignment that determines whether a NT author follows the LXX
wording or the Hebrew MT.

Built to answer questions like:
- *How many Niphal perfect verbs are in each book of the OT?*
- *What is the verb stem distribution across the Torah?*
- *How does Paul use the aorist passive compared to the rest of the NT?*
- *Where does the word "grace" appear in Paul's letters (KJV)?*
- *How consistently does the LXX render רוּחַ (spirit/wind) across books?*
- *Does Hebrews quote the OT following the LXX or the Hebrew MT?*
- *What Greek word does the LXX use to translate חֶסֶד (lovingkindness), and how does that word travel into the NT?*
- *Which words cluster significantly near שָׁלוֹם (peace) in the OT?*
- *How does Paul's use of Χριστός (Christ) compare to the Gospels? Where does the title concentrate?*
- *What OT passages does Isaiah 53 echo in the NT — and through which books?*
- *How do verb conjugation patterns differ between narrative prose and wisdom poetry?*

---

## Contents

- [Data Sources](#data-sources)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Features](#features)
  - [Query API](#query-api)
  - [Word Study](#word-study)
  - [Semantic Profile](#semantic-profile)
  - [Concordance](#concordance)
  - [Frequency Statistics](#frequency-statistics)
  - [Book Profiles](#book-profiles)
  - [Translation Equivalents (IBM Model 1)](#translation-equivalents-ibm-model-1)
  - [LXX Translation Consistency](#lxx-translation-consistency)
  - [Collocation Statistics](#collocation-statistics)
  - [Morphological Distribution](#morphological-distribution)
  - [NT Quotations](#nt-quotations)
  - [NT Quotation Word Alignment](#nt-quotation-word-alignment)
  - [Intertextuality Network](#intertextuality-network)
  - [Theological Term Map](#theological-term-map)
  - [Synonym Comparison](#synonym-comparison)
  - [Phrase & Proximity Search](#phrase--proximity-search)
  - [Divine Names Analysis](#divine-names-analysis)
  - [Genre Comparison](#genre-comparison)
  - [Hapax Legomena](#hapax-legomena)
  - [Parallel Passages](#parallel-passages)
  - [HTML & CSV Export](#html--csv-export)
  - [Charts](#charts)
  - [Slash Commands (Claude Code skills)](#slash-commands-claude-code-skills)
- [Notebooks](#notebooks)
- [Data Notes](#data-notes)

---

## Data Sources

| Submodule | Contents | License |
|---|---|---|
| `stepbible-data/` | Hebrew OT (TAHOT, ~284k words) and Greek NT (TAGNT, ~142k words) with full morphological tagging; LXX Greek (TALXX); lexicons TBESH/TBESG; NT→OT cross-references | CC BY 4.0 — Tyndale House Cambridge |
| `scrollmapper-data/` | KJV English (24,570 verses) and Latin Vulgate Clementine (24,909 verses) | MIT — scrollmapper |

### Morphological coverage

**Hebrew/Aramaic (TAHOT):** Every word tagged with stem (Qal, Niphal, Piel, Hiphil, etc.),
conjugation (Perfect, Imperfect, Imperative, Participle, Infinitive), person, gender, number,
state (absolute/construct), and Strong's number. Aramaic words (Daniel, Ezra) are tagged
separately as `language=Aramaic`.

**Greek (TAGNT):** Every word tagged with part of speech, tense, voice, mood, person, number,
gender, case, and Strong's number.

**LXX (TALXX):** Greek Septuagint with Strong's numbers, used for Hebrew→Greek translation
alignment and NT quotation analysis.

**Lexicons:** TBESH (Hebrew) and TBESG (Greek) — Translators Brief lexicons with lemma,
transliteration, gloss, definition, and POS code for every Strong's number.

> **ESV note:** The ESV text is under copyright by Crossway and cannot be included. If you
> obtain a Crossway license, adding ESV support is straightforward — the STEPBible tagging
> file is already present in the submodule.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git (with submodule support)
- Jupyter Notebook or JupyterLab

### Installation

```bash
# 1. Clone the repository with all submodules
git clone --recurse-submodules <repo-url>
cd bible-grammar-stats

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Build the processed database (one-time, ~5 seconds)
python scripts/build_db.py

# 4. (Optional) Build the IBM Model 1 word alignment (~30 seconds)
python -c "from bible_grammar.ibm_align import build_alignment; build_alignment()"

# 5. Launch Jupyter
jupyter notebook notebooks/
```

If you cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

---

## Project Structure

```
bible-grammar-stats/
├── src/bible_grammar/          # Core Python library
│   ├── query.py                # Filtered morphology + translation query API
│   ├── wordstudy.py            # Word study: lexicon + stats + LXX equivalents
│   ├── semantic_profile.py     # Unified semantic range report (lexicon+stats+collocations)
│   ├── concordance.py          # Concordance, lemma frequency, top lemmas
│   ├── stats.py                # Frequency tables, aggregation helpers
│   ├── charts.py               # Matplotlib/seaborn chart helpers
│   ├── profiles.py             # Per-book morphological profiles
│   ├── ibm_align.py            # IBM Model 1 word-level Hebrew↔LXX alignment
│   ├── lxx_consistency.py      # LXX translation consistency by book
│   ├── collocation.py          # PMI and G² collocate scoring
│   ├── morph_chart.py          # Morphological distribution charts by book
│   ├── quotations.py           # NT→OT cross-references (scrollmapper)
│   ├── quotation_align.py      # NT quotation word alignment (LXX vs MT)
│   ├── intertextuality.py      # OT verse/chapter/book → NT citation network
│   ├── termmap.py              # Theological term mapping OT→LXX→NT
│   ├── synonym.py              # Near-synonym comparison
│   ├── phrase.py               # Phrase search and proximity search
│   ├── divine_names.py         # Divine name / christological title frequency
│   ├── genre_compare.py        # Morphological patterns across literary genres
│   ├── hapax.py                # Hapax legomena analysis
│   ├── parallel.py             # Parallel passage comparison
│   ├── export.py               # HTML and CSV export for all analyses
│   ├── alignment.py            # Verse-level Hebrew↔Greek alignment
│   ├── morphology.py           # Decode Hebrew/Greek morphology codes
│   ├── reference.py            # Book metadata: names, testament, order
│   ├── db.py                   # SQLite + Parquet persistence
│   └── ingest.py               # Parse STEPBible TSV files
│
├── scripts/
│   └── build_db.py             # Build data/processed/ from scratch
│
├── notebooks/                  # Jupyter notebooks
├── reports/                    # Markdown reports with embedded charts
├── output/
│   ├── charts/                 # Generated PNG chart files
│   └── exports/                # Generated CSV exports (gitignored)
├── .claude/commands/           # Claude Code slash command skills
├── stepbible-data/             # Git submodule: STEPBible/STEPBible-Data
├── scrollmapper-data/          # Git submodule: scrollmapper/bible_databases
└── data/processed/             # Generated files (gitignored)
    ├── bible_grammar.db        # SQLite database
    ├── words.parquet           # Hebrew/Greek word data
    ├── translations.parquet    # KJV + Vulgate verse data
    └── word_alignment.parquet  # IBM Model 1 alignment data
```

---

## Features

### Query API

The `query()` function is the core access point for morphological data.

```python
from bible_grammar import query

# Niphal perfect verbs in Genesis
query(book='Gen', stem='Niphal', conjugation='Perfect')

# All verbs in the Torah
query(book_group='torah', part_of_speech='Verb')

# Greek aorist passive indicatives in Paul's letters
query(book_group='pauline', tense='Aorist', voice='Passive', mood='Indicative')
```

**Available filters:** `source`, `book`, `testament`, `book_group` (torah/prophets/writings/
gospels/pauline/general), `chapter`, `verse`, `part_of_speech`, `stem`, `conjugation`,
`tense`, `voice`, `mood`, `person`, `number`, `gender`, `case_`, `state`

```python
from bible_grammar import translation_query

# KJV verses containing "grace" in Paul's letters
translation_query(translation='KJV', book_group='pauline', search='grace')

# Latin Vulgate — first chapter of Romans
translation_query(translation='VulgClementine', book='Rom', chapter=1)
```

---

### Word Study

Complete lexical and statistical profile for any Hebrew or Greek word.

```python
from bible_grammar import word_study, print_word_study

# Full word study dict
ws = word_study('H7307')   # רוּחַ spirit/wind
ws = word_study('G3056')   # λόγος word

# Formatted report to stdout
print_word_study('H1254')  # בָּרָא to create
print_word_study('G4160')  # ποιέω to do/make
```

Each study includes: lemma, transliteration, gloss, definition, total occurrences,
distribution by book, morphological forms breakdown, LXX translation equivalents
(Hebrew only, word-level IBM Model 1 alignment), and the OT→LXX→NT trajectory.

Lemmas can be resolved to Strong's numbers by name:

```python
from bible_grammar import resolve_strongs

resolve_strongs('שָׁלוֹם')   # → 'H7965'
resolve_strongs('λόγος')    # → 'G3056'
```

---

### Semantic Profile

A unified full-profile report combining lexicon entry, frequency, morphology, LXX equivalents,
collocations, and example verses into a single analysis.

```python
from bible_grammar import semantic_profile, print_semantic_profile, save_semantic_profile

# Terminal report
print_semantic_profile('H7965')   # שָׁלוֹם peace
print_semantic_profile('G3056')   # λόγος word

# Save as Markdown + PNG chart to output/reports/
save_semantic_profile('H1285')    # בְּרִית covenant
save_semantic_profile('H7307')    # רוּחַ spirit/wind
```

Pre-generated profiles for שָׁלוֹם, בְּרִית, רוּחַ, and λόγος are in `output/reports/`.

---

### Concordance

```python
from bible_grammar import concordance, lemma_frequency, top_lemmas

# All occurrences of H7307 with KJV context
concordance(strongs='H7307', context='KJV')

# Frequency table for all lemmas in Psalms
lemma_frequency(book='Psa', corpus='OT')

# Top 20 lemmas in Romans
top_lemmas(book='Rom', n=20)
```

---

### Frequency Statistics

```python
from bible_grammar import freq_table
from bible_grammar import query

df = query(book_group='torah', part_of_speech='Verb')
freq_table(df, 'stem')           # Count by binyan (Qal, Piel, Niphal…)
freq_table(df, ['stem', 'book_id'])  # Cross-tab
```

---

### Book Profiles

Morphological fingerprint for any OT or NT book.

```python
from bible_grammar import book_profile, print_profile, batch_profiles

print_profile('Gen')   # Genesis: verb stems, top lemmas, morph breakdown
print_profile('Rom')   # Romans: tense/voice/mood distribution

# Compare multiple books
batch_profiles(['Gen', 'Exo', 'Lev', 'Num', 'Deu'])
```

---

### Translation Equivalents (IBM Model 1)

Statistical word-level alignment between the Hebrew OT and the LXX, trained using
IBM Model 1. Answers: *which Greek word does the LXX use to translate this Hebrew root?*

```python
from bible_grammar import translation_equivalents_w, hebrew_sources_w

# Top Greek renderings for H1285 (בְּרִית covenant)
translation_equivalents_w(heb_strongs='H1285')

# Top Hebrew sources for G1242 (διαθήκη covenant)
hebrew_sources_w(lxx_strongs='G1242')
```

---

### Collocation Statistics

Identifies words that co-occur with a target root significantly more than chance, scored
by Pointwise Mutual Information (PMI) and log-likelihood ratio (G²).

```python
from bible_grammar import collocations, print_collocations, collocation_network

# Top collocates of שָׁלוֹם (peace) in the OT
print_collocations('H7965', corpus='OT', window=5)

# Top collocates of εἰρήνη (peace) in the NT
print_collocations('G1515', corpus='NT', window=5)

# Heatmap comparing collocate overlap for multiple roots
collocation_network(['H7965', 'H2617', 'H6666'], output_path='output/charts/peace-network.png')
```

---

### Morphological Distribution

Per-book distribution of morphological forms for any root — Hebrew stem × conjugation,
Greek tense × voice, or Greek case.

```python
from bible_grammar import morph_distribution, print_morph_distribution, morph_chart

# OT verb — stem breakdown across books
print_morph_distribution('H1696')    # דָּבַר to speak
morph_chart('H1696', chart_type='stacked_bar',
            output_path='output/charts/dabar-stems.png')

# NT verb — tense × voice per book
morph_chart('G3004', chart_type='heatmap',
            output_path='output/charts/lego-tense.png')
```

---

### LXX Translation Consistency

Measures how uniformly each LXX book/translator renders a given Hebrew root.
High consistency (>90%) means one dominant Greek equivalent; low consistency or
divergent books may indicate semantic range, translation philosophy differences,
or recensional variation.

```python
from bible_grammar import lxx_consistency, print_lxx_consistency
from bible_grammar import consistency_heatmap, batch_consistency

# Per-book rendering profile for רוּחַ (spirit/wind)
print_lxx_consistency('H7307')

# Heatmap: rows=LXX lemmas, cols=OT books, cells=% usage
consistency_heatmap('H7307', output_path='output/charts/ruach-consistency.png')

# Batch summary across multiple roots
batch_consistency(['H7307', 'H1697', 'H2617', 'H6944'])
```

The `batch_consistency()` result across the full theological terms list shows:
- **100% consistent:** בְּרִית (covenant), שָׁלוֹם (peace), קֹדֶשׁ (holiness), חֶסֶד (lovingkindness)
- **Most divergent:** דָּבָר (word, 9 divergent books), מִשְׁפָּט (justice, 8 books), שׁוּב (return, 6 books)

---

### NT Quotations

Cross-reference database linking NT verses to their OT sources (scrollmapper,
vote-weighted confidence scores).

```python
from bible_grammar import nt_quotations, verse_comparison, quotation_table

# All NT quotations of Isaiah
nt_quotations(ot_book='Isa', min_votes=50)

# All OT quotations in Hebrews
nt_quotations(nt_book='Heb', min_votes=30)

# Side-by-side verse text comparison
verse_comparison(nt_book='Mat', nt_chapter=4, nt_verse=4)
```

---

### NT Quotation Word Alignment

For each NT→OT quotation, analyses whether the NT author's Greek vocabulary follows
the LXX wording or diverges toward the Hebrew MT. Per-word verdicts:

| Verdict | Meaning |
|---|---|
| `LXX` | NT word's Strong's number appears in the LXX rendering of the OT verse |
| `LXX+MT` | Matches LXX and the Hebrew root is also present in the OT verse |
| `MT-diverge` | NT word's Hebrew root is in the OT verse but the LXX used a different Greek word |
| `neutral` | Function word or no alignment data |

```python
from bible_grammar import quotation_align, print_quotation_align, batch_align

# Word-level analysis for a single NT verse
print_quotation_align('Mat', 4, 4)   # Deut 8:3 — "man shall not live by bread alone"

# Batch summary across all high-confidence quotations in Hebrews
df = batch_align(nt_book='Heb', min_votes=50)
```

---

### Intertextuality Network

Given any OT verse, chapter, or book, finds all NT verses that quote or allude to it,
scored by community vote confidence (scrollmapper / OpenBible.info). Produces a bipartite
network graph (OT verses on the left, NT books/verses on the right) and a full report.

```python
from bible_grammar import intertextuality, print_intertextuality
from bible_grammar import intertextuality_graph, intertextuality_report

# Chapter scope — Isaiah 53 → all NT citations
print_intertextuality('Isa', chapter=53, min_votes=20)

# Single verse — Psalm 22:1 ("My God, my God…")
print_intertextuality('Psa', chapter=22, verse=1, min_votes=15)

# Full book — all Isaiah links at high confidence
print_intertextuality('Isa', min_votes=50)

# Network graph PNG
intertextuality_graph('Isa', chapter=53, min_votes=20,
                      output_path='output/charts/isa53-network.png')

# Markdown report + CSV
intertextuality_report('Psa', chapter=22, output_dir='output/reports')
```

Vote scores reflect how many independent scholars have identified the connection;
scores ≥50 are strong explicit quotations, 20–49 are probable allusions, 10–19 are
possible echoes. Pre-generated reports for Isaiah 53, Psalm 22, and full Isaiah
are in `output/reports/`.

---

### Theological Term Map

Traces key theological concepts across OT Hebrew → LXX Greek → NT Greek,
showing whether NT authors adopt LXX vocabulary or use fresh terminology.

```python
from bible_grammar import term_map, print_term_map, THEOLOGICAL_TERMS

# Built-in theological domains
print(list(THEOLOGICAL_TERMS.keys()))
# ['Covenant / Faithfulness', 'Holiness / Purity', 'Righteousness / Justice', ...]

# Full trajectory for "Covenant / Faithfulness"
print_term_map('Covenant / Faithfulness')

# Custom term set
term_map(['H7965', 'G1515'])   # שָׁלוֹם / εἰρήνη (peace)
```

---

### Synonym Comparison

Side-by-side comparison of near-synonym Hebrew or Greek roots.

```python
from bible_grammar import compare_synonyms, print_synonym_comparison

# אָהַב vs חָשַׁק (love vs desire)
print_synonym_comparison(['H157', 'H2836'])

# NT love words
print_synonym_comparison(['G26', 'G5368'])   # ἀγάπη vs φιλέω

# Uses Hebrew/Greek lemmas directly (auto-resolved to Strong's)
print_synonym_comparison(['שָׁלוֹם', 'εἰρήνη'])
```

Output includes: frequency comparison with bars, LXX translation equivalents
(shared renderings marked †), OT→LXX→NT trajectory, book distribution, and
morphological form breakdown.

---

### Phrase & Proximity Search

Search for consecutive word sequences or statistically proximate words in the
Hebrew OT, Greek NT, or LXX.

```python
from bible_grammar import phrase_search, print_phrase_results
from bible_grammar import proximity_search, print_proximity_results

# Consecutive phrase search — tokens can be Strong's numbers, lemmas, or '*' wildcard
results = phrase_search(['H3068', 'H559'], corpus='OT')   # יְהוָה + אָמַר
print_phrase_results(results)

# "word" near "spirit" within 5 words (ordered, any direction)
results = proximity_search(['H1697', 'H7307'], within=5, corpus='OT')
print_proximity_results(results)

# Cross-verse proximity is supported; distance is in word tokens
results = proximity_search(['G3056', 'G2316'], within=10, corpus='NT')
```

Token types:
- Strong's number string: `'H7307'`, `'G3056'`
- Hebrew/Greek lemma (auto-resolved): `'רוּחַ'`, `'λόγος'`
- Wildcard: `'*'` matches any word
- Constraint dict: `{'strongs': 'H7307', 'stem': 'Qal'}` for morphological filtering

---

### Divine Names Analysis

Tracks the major divine names and christological titles across three corpora with
frequency tables, per-section breakdowns, stacked bar charts, and heatmaps.

**OT Hebrew:** YHWH (H3068G), Elohim (H0430), Adonai (H0136), El (H0410), Yah (H3050), Shaddai (H7706)  
**LXX Greek:** Kyrios (G2962), Theos (G2316)  
**NT Greek:** Theos (G2316), Kyrios (G2962), Iesous (G2424G), Christos (G5547), Pater (G3962), Pneuma (G4151)

```python
from bible_grammar import print_divine_names, divine_name_table
from bible_grammar import divine_name_by_section, divine_names_chart, divine_names_report

# Terminal summary
print_divine_names('OT')    # YHWH 65.8% | Elohim 26.3% | Adonai 4.4% …
print_divine_names('NT')    # Theos 30.2% | Iesous 22.1% | Kyrios 16.9% …

# Distribution by canonical section
divine_name_by_section('OT')   # Torah / Historical / Wisdom / Prophets

# Charts
divine_names_chart('NT', chart_type='stacked_bar')
divine_names_chart('OT', chart_type='heatmap')

# Full Markdown report (OT + LXX + NT)
divine_names_report(output_dir='output/reports')
```

Notable finding: **Adonai** is overwhelmingly a prophetic title (343 of 440 OT occurrences
are in the Prophets, 222 in Ezekiel alone). **Christos** concentrates heavily in Paul
(403 of 571 NT occurrences), while **Iesous** dominates the Gospels & Acts.

---

### Genre Comparison

Compares morphological patterns across the literary genres of the OT and NT —
verb stems, conjugations, tense, voice, mood, and part-of-speech distribution.

```python
from bible_grammar import genre_compare, print_genre_compare
from bible_grammar import genre_heatmap, genre_report

# OT: verb stem distribution across Torah / Historical / Wisdom / Prophets
print_genre_compare('OT', feature='verb_stem')
print_genre_compare('OT', feature='verb_conjugation')

# NT: verb tense/mood distribution across Gospels / Pauline / General
print_genre_compare('NT', feature='verb_tense')
print_genre_compare('NT', feature='verb_mood')

# Heatmap chart
genre_heatmap('OT', feature='verb_stem',
              output_path='output/charts/ot-genre-verb-stem.png')

# Full Markdown report (OT + NT, all features)
genre_report(output_dir='output/reports')
```

Key findings:
- **Consecutive Perfect (wayyiqtol)** dominates Historical prose (36% of verbs) vs. Wisdom (5%) — narrative drive vs. reflection
- **Imperfect** dominates Wisdom poetry (31%) — habitual, timeless, or ongoing action
- **Paul** has the highest Present tense ratio (55%) in the NT — characteristic of didactic/hortatory style
- **Revelation/General letters** have the highest participle density (28%)

---

### Hapax Legomena

Words occurring only once in a given corpus or book.

```python
from bible_grammar import hapax_legomena, hapax_table, hapax_summary

# All hapax in Job
hapax_legomena(book='Job')

# Summary counts per book across the OT
hapax_summary(corpus='OT')
```

---

### Parallel Passages

Compare parallel passages between books (e.g. Samuel/Kings vs Chronicles,
Synoptic parallels).

```python
from bible_grammar import parallel_passage, print_parallel

print_parallel('2Sa', 22, 'Psa', 18)   # Psalm 18 = 2 Samuel 22
print_parallel('Mat', 5, 'Luk', 6)     # Sermon on the Mount / Plain
```

---

### HTML & CSV Export

Export any analysis as a self-contained HTML report (inline CSS and embedded charts,
ready to open in a browser or share) plus companion CSV data files.

```python
from bible_grammar import (export_word_study, export_semantic_profile,
                            export_genre_compare, export_divine_names, export_all)

# Word study → HTML + CSV
export_word_study('H7965')        # output/exports/html/h7965-word-study.html

# Semantic profile → HTML + CSV
export_semantic_profile('G3056')  # output/exports/html/g3056-semantic-profile.html

# Genre comparison → HTML + CSV (all features for one corpus)
export_genre_compare('OT')
export_genre_compare('NT')

# Divine names → HTML + CSV (all three corpora)
export_divine_names()

# Run all exporters at once
export_all()
```

Output directories:
- `output/exports/html/` — standalone HTML files (gitignored, regenerated on demand)
- `output/exports/csv/`  — raw CSV files organised by analysis type (gitignored)

---

### Charts

```python
from bible_grammar import charts

# Bar chart from any DataFrame
charts.bar_chart(df, x='stem', title='Verb Stems in Isaiah',
                 output_path='output/charts/isaiah_stems.png')

# Heatmap (e.g. tense × voice)
charts.heatmap(df, index='tense', columns='voice', title='Tense × Voice in John')

# Grouped bar (e.g. stems per book)
charts.grouped_bar(df, x='book_id', hue='stem', title='Stems by Book')

# LXX consistency heatmap
from bible_grammar import consistency_heatmap
consistency_heatmap(['H7307', 'H2617'], output_path='output/charts/consistency.png')
```

---

### Slash Commands (Claude Code skills)

When using this project with [Claude Code](https://claude.ai/code), the following
slash commands are available:

| Command | Description |
|---|---|
| `/word-study <strongs>` | Full word study for any Hebrew or Greek root |
| `/semantic-profile <strongs>` | Unified report: lexicon + freq + morph + LXX + collocations |
| `/synonym <term1> <term2>` | Side-by-side near-synonym comparison |
| `/lxx-consistency <strongs>` | LXX rendering consistency by book |
| `/collocations <strongs>` | Statistically significant collocates (PMI / G²) |
| `/morph-chart <strongs>` | Morphological distribution chart by book |
| `/term-map <domain>` | Theological term trajectory OT→LXX→NT |
| `/phrase-search <token1> <token2>` | Consecutive phrase or proximity search |
| `/divine-names [OT\|NT\|LXX\|all]` | Divine name / christological title frequency |
| `/genre-compare [OT\|NT] [feature]` | Morphological patterns across literary genres |
| `/intertextuality <OT-ref>` | OT verse/chapter/book → NT citation network |
| `/export <type> [args]` | Export any analysis to HTML + CSV |

Examples:
```
/word-study H7307
/semantic-profile H7965
/synonym H157 H2836
/lxx-consistency H1697
/collocations H7965
/morph-chart H1696
/term-map "Covenant / Faithfulness"
/phrase-search H3068 H559
/divine-names OT
/genre-compare OT verb_stem
/intertextuality Isa 53
/export word-study G3056
```

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `01_data_exploration.ipynb` | Raw data inspection, word counts, Gen 1:1 and Matt 1:1 spot-checks |
| `02_query_demo.ipynb` | End-to-end walkthrough: Niphal perfects, Torah verb stems, Greek tense/voice, CSV export |
| `03_statistics.ipynb` | Full showcase — OT verb stems, Torah comparison, Greek NT heatmaps, aorist passives by book |
| `04_nt_quotations.ipynb` | NT→OT quotation database, three-way text comparison, LXX vs MT alignment |
| `05_concordance.ipynb` | Concordance, lemma frequency, top lemmas by book |
| `06_book_profiles.ipynb` | Per-book morphological fingerprints, cross-book comparison |
| `07_word_study.ipynb` | Word study API, LXX equivalents, OT→LXX→NT trajectory |
| `08_parallel_passage.ipynb` | Parallel passage comparison (Synoptics, Samuel/Psalms) |
| `09_language_analysis.ipynb` | LXX consistency, collocations, morphological distribution, semantic profiles, theological term maps |
| `10_advanced_analysis.ipynb` | Divine names, genre comparison, intertextuality networks, HTML/CSV export |

Export a notebook as a shareable HTML file:

```bash
jupyter nbconvert --to html notebooks/10_advanced_analysis.ipynb
```

---

## Data Notes

- **Aramaic:** Daniel 2:4–7:28 and Ezra 4:8–6:18, 7:12–26 are tagged `language=Aramaic`.
- **Pronominal suffixes:** Hebrew pronominal suffixes are encoded as separate word tokens
  (own `word_num` row). When using proximity search, add ~30% to your mental window size
  to account for suffix tokens.
- **Untagged tokens:** Some morphology fields are blank for prefix tokens (conjunction ו,
  preposition ב, etc.) attached to a word where STEPBible encodes the prefix separately.
- **Versification:** TAHOT follows NRSV versification; some chapter/verse numbers differ
  from KJV (especially in Psalms and some prophetic books).
- **Strong's normalization:** The library normalizes Strong's numbers throughout —
  zero-padding (H530 ↔ H0530) and variant suffixes (H1697A → H1697) are handled
  transparently.
- **Word counts:** TAHOT ~284k words, TAGNT ~142k words, LXX ~480k words,
  KJV 24,570 verses, Vulgate Clementine 24,909 verses.
