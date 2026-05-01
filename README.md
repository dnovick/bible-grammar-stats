# Bible Grammar Stats

A Python project for generating statistics, charts, and reports on the grammatical
constructs of the biblical text — Hebrew and Aramaic Old Testament, Greek New Testament,
and English/Latin translations.

Built to answer questions like:
- *How many Niphal perfect verbs are in each book of the OT?*
- *What is the verb stem distribution across the Torah?*
- *How does Paul use the aorist passive compared to the rest of the NT?*
- *Where does the word "grace" appear in Paul's letters (KJV)?*

---

## Contents

- [Data Sources](#data-sources)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Query API](#query-api)
- [Notebooks](#notebooks)
- [Reports](#reports)
- [Example Questions](#example-questions)

---

## Data Sources

| Submodule | Contents | License |
|---|---|---|
| `stepbible-data/` | Hebrew OT (TAHOT, ~284k words) and Greek NT (TAGNT, ~142k words) with full morphological tagging | CC BY 4.0 — Tyndale House Cambridge |
| `scrollmapper-data/` | KJV English (24,570 verses) and Latin Vulgate Clementine (24,909 verses) | MIT — scrollmapper |

### Morphological coverage

**Hebrew/Aramaic (TAHOT):** Every word tagged with stem (Qal, Niphal, Piel, Hiphil, etc.),
conjugation (Perfect, Imperfect, Imperative, Participle, Infinitive), person, gender, number,
state (absolute/construct), and Strong's number. Aramaic words (Daniel, Ezra) are tagged
separately as `language=Aramaic`.

**Greek (TAGNT):** Every word tagged with part of speech, tense, voice, mood, person, number,
gender, case, and Strong's number. Covers NA27/28, SBL, TR, Byzantine, and Textus Receptus
with variant notation.

**Translations:** Verse-level text for KJV (English) and Vulgate Clementine (Latin),
searchable by book, chapter, verse, or free-text keyword.

> **ESV note:** The ESV text is under copyright by Crossway and cannot be included without
> a license. If you obtain a Crossway license, adding ESV support is straightforward —
> the STEPBible tagging file (`stepbible-data/Tagged-Bibles/TTESV...`) is already present.

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
#    Parses all STEPBible TSV files and translation JSON files into
#    data/processed/bible_grammar.db (SQLite) and *.parquet files
python scripts/build_db.py

# 4. Launch Jupyter
jupyter notebook notebooks/
```

If you cloned without `--recurse-submodules`, initialize the submodules manually:

```bash
git submodule update --init --recursive
```

---

## Project Structure

```
bible-grammar-stats/
├── src/bible_grammar/          # Core Python library
│   ├── ingest.py               # Parse STEPBible TAHOT/TAGNT TSV files
│   ├── morphology.py           # Decode Hebrew and Greek morphology codes
│   ├── db.py                   # SQLite + Parquet persistence layer
│   ├── query.py                # Filtered query API (Hebrew/Greek + translations)
│   ├── reference.py            # Book metadata: names, testament, canonical order
│   ├── stats.py                # Frequency tables and aggregation helpers
│   ├── charts.py               # Matplotlib/seaborn chart helpers
│   └── translations.py         # Load KJV and Vulgate JSON data
│
├── scripts/
│   └── build_db.py             # Build data/processed/ from scratch
│
├── notebooks/
│   ├── 01_data_exploration.ipynb   # Sanity checks and raw data inspection
│   ├── 02_query_demo.ipynb         # Query API walkthrough with charts
│   └── 03_statistics.ipynb         # Full statistics showcase (exportable to HTML)
│
├── reports/                    # Markdown reports with embedded charts
│   └── README.md               # Index of all reports
│
├── output/
│   ├── charts/                 # Generated PNG chart files
│   └── exports/                # Generated CSV exports (gitignored)
│
├── stepbible-data/             # Git submodule: STEPBible/STEPBible-Data
├── scrollmapper-data/          # Git submodule: scrollmapper/bible_databases
└── data/processed/             # Generated database files (gitignored)
    ├── bible_grammar.db        # SQLite: words + books + translations tables
    ├── words.parquet           # Hebrew/Greek word data (fast pandas reload)
    └── translations.parquet    # KJV + Vulgate verse data
```

---

## Query API

All queries are made through two functions imported from `bible_grammar.query`.

### Hebrew/Greek morphology — `query()`

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar.query import query

# Niphal perfect verbs in Genesis
query(book='Gen', stem='Niphal', conjugation='Perfect')

# All verbs in the Torah
query(book_group='torah', part_of_speech='Verb')

# Greek aorist passive indicatives in Paul's letters
query(book_group='pauline', tense='Aorist', voice='Passive', mood='Indicative')

# 1st person singular perfect verbs in Galatians
query(book='Gal', part_of_speech='Verb', conjugation='Perfect', person='1st', number='Singular')
```

**Available filters:** `source` (TAHOT/TAGNT), `book`, `testament` (OT/NT),
`book_group` (torah/prophets/writings/gospels/pauline), `chapter`, `verse`,
`part_of_speech`, `stem`, `conjugation`, `tense`, `voice`, `mood`,
`person`, `number`, `gender`, `case_`, `state`

All string filters are case-insensitive substring matches.

### Translation text — `translation_query()`

```python
from bible_grammar.query import translation_query

# John 3:16 in both translations side by side
translation_query(book='Jhn', chapter=3, verse=16)

# KJV verses containing "grace" in Paul's letters
translation_query(translation='KJV', book_group='pauline', search='grace')

# Latin Vulgate — first chapter of Romans
translation_query(translation='VulgClementine', book='Rom', chapter=1)
```

**Available filters:** `translation` (KJV/VulgClementine), `book`, `testament`,
`book_group`, `chapter`, `verse`, `search` (free-text substring)

### Statistics helpers

```python
from bible_grammar import stats

stats.niphal_perfects_by_book()        # Count by book
stats.verb_stems_by_book(book='Isa')   # Stem breakdown for a book
stats.pos_distribution('TAHOT')        # Part-of-speech distribution
stats.greek_verb_forms(book='Jhn')     # Tense × voice × mood table
stats.freq_table(df, 'stem')           # Generic groupby count on any DataFrame
```

### Charts

```python
from bible_grammar import charts
import matplotlib.pyplot as plt

# Bar chart
fig = charts.bar_chart(df, x='stem', title='Verb Stems in Isaiah',
                       output_path='output/charts/isaiah_stems.png')

# Heatmap (e.g. tense × voice)
fig = charts.heatmap(df, index='tense', columns='voice',
                     title='Tense × Voice in John')

# Grouped bar (e.g. stems per book)
fig = charts.grouped_bar(df, x='book_id', hue='stem',
                         title='Stems by Book')
plt.show()
```

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `01_data_exploration.ipynb` | Raw data inspection, word counts, Gen 1:1 and Matt 1:1 spot-checks, part-of-speech distributions |
| `02_query_demo.ipynb` | End-to-end walkthrough: Niphal perfects, Torah verb stems, Pauline Greek tense/voice, CSV export |
| `03_statistics.ipynb` | Full showcase — OT verb stems, Torah comparison, Greek NT heatmaps, aorist passives by book |

Export a notebook as a shareable HTML file:

```bash
jupyter nbconvert --to html notebooks/03_statistics.ipynb
```

---

## Reports

The `reports/` directory contains Markdown reports for each generated chart, each with
an embedded image, plain-English summary, and key observations. See
[reports/README.md](reports/README.md) for the full index.

**Hebrew OT reports:**
- Verb stem distribution — entire OT and Genesis
- Torah verb stems compared across all five books
- Niphal Perfect verb counts for every OT book

**Greek NT reports:**
- Tense × Voice heatmap — entire NT
- Tense × Voice heatmap — Pauline letters
- Aorist Passive verb counts by NT book

---

## Example Questions

Here is a sample of the kinds of questions you can ask:

**Hebrew morphology**
- How many Qal perfect verbs are in Exodus?
- Which OT book has the most Piel imperfect verbs?
- How do Niphal and Pual counts compare across the Torah?
- Show all Hiphil imperatives in the Psalms.

**Greek morphology**
- How many aorist passive verbs are in Romans?
- What is the most common tense/voice combination in John's Gospel?
- Compare indicative vs. subjunctive counts across the Pauline letters.

**Part-of-speech**
- What percentage of words in Genesis are verbs vs. nouns vs. adjectives?
- Which NT book has the highest proportion of nouns?

**Translations**
- Show me John 3:16 in KJV and Latin side by side.
- How many KJV verses in Paul's letters contain the word "grace"?
- Find all Vulgate verses in Isaiah containing "lux" (light).

---

## Data Notes

- **Aramaic:** Daniel 2:4–7:28 and Ezra 4:8–6:18, 7:12–26 are in Aramaic. These words
  are tagged `language=Aramaic` and can be filtered separately.
- **Untagged tokens (~5%):** Some morphology fields are blank for prefix tokens (e.g.,
  the conjunction ו or preposition ב attached to a word) where STEPBible encodes the
  prefix as a separate token without a full stem parse.
- **Versification:** TAHOT follows NRSV versification; differences from KJV chapter/verse
  numbers are noted in the source data.
- **Word counts:** TAHOT ~284k words, TAGNT ~142k words, KJV 24,570 verses,
  Vulgate Clementine 24,909 verses (slightly more due to deuterocanonical content).
