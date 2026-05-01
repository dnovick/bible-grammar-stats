# Bible Grammar Stats

Statistics and charts for Hebrew/Aramaic OT and Greek NT grammatical constructs, powered by [STEPBible data](https://github.com/STEPBible/STEPBible-Data).

## Quick start

```bash
# 1. Clone with submodule
git clone --recurse-submodules <repo-url>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build the database (one-time, ~5 seconds)
python scripts/build_db.py

# 4. Launch Jupyter
jupyter notebook notebooks/
```

## Example queries

```python
import sys; sys.path.insert(0, 'src')
from bible_grammar.query import query
from bible_grammar import stats, charts

# How many Niphal perfect verbs are in Genesis?
df = query(book='Gen', stem='Niphal', conjugation='Perfect')
print(len(df))  # 80

# Verb stem counts in Genesis
stats.verb_stems_by_book(book='Gen')

# Greek aorist passives in Paul's letters
query(book_group='pauline', tense='Aorist', voice='Passive')

# Export to CSV
df.to_csv('output/exports/my_query.csv', index=False)
```

## Notebooks

| Notebook | Purpose |
|---|---|
| `01_data_exploration.ipynb` | Sanity checks, word counts, Gen 1:1 spot-check |
| `02_query_demo.ipynb` | Demonstrates the query API with charts |
| `03_statistics.ipynb` | Full statistics showcase — export as shareable HTML |

Export a notebook as HTML:
```bash
jupyter nbconvert --to html notebooks/03_statistics.ipynb
```

## Project structure

```
src/bible_grammar/
  ingest.py      # Parse TAHOT/TAGNT TSVs -> DataFrames
  morphology.py  # Decode morphology code strings
  db.py          # SQLite + Parquet persistence
  query.py       # Filtered query API
  reference.py   # Book metadata (names, testament, canonical order)
  stats.py       # Frequency tables and aggregations
  charts.py      # Matplotlib/seaborn chart helpers
scripts/
  build_db.py    # One-time database build
data/processed/  # Generated: bible_grammar.db + words.parquet (gitignored)
stepbible-data/  # Git submodule: STEPBible/STEPBible-Data
```

## Data source

[STEPBible Data](https://github.com/STEPBible/STEPBible-Data) by Tyndale House Cambridge, CC BY 4.0.
- **TAHOT**: Hebrew/Aramaic OT (~284k words, ETCBC morphology)
- **TAGNT**: Greek NT (~142k words, Robinson morphology)
