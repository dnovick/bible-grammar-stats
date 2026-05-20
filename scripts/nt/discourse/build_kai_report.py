"""Build the καί semantic function report.

Outputs
-------
output/reports/nt/discourse/kai-semantic-functions.md   — narrative report
output/reports/nt/discourse/kai-gnt-profile.csv         — GNT-wide function counts
output/reports/nt/discourse/kai-by-book.csv             — per-book function counts
output/charts/nt/discourse/nt_kai_functions.png         — function bar chart
output/charts/nt/discourse/nt_kai_book_heatmap.png      — per-book heatmap

Run from the repo root:
    python scripts/nt/discourse/build_kai_report.py
"""
import matplotlib  # noqa: E402
matplotlib.use('Agg')
from pathlib import Path  # noqa: E402

from bible_grammar import (  # noqa: E402
    nt_kai_profile,
    nt_kai_by_book,
    nt_kai_instances,
    nt_kai_function_chart,
    nt_kai_book_heatmap,
    KAI_FUNCTIONS,
)

REPORT_DIR = Path('output/reports/nt/discourse')
CHART_DIR = Path('output/charts/nt/discourse')
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ── Data ──────────────────────────────────────────────────────────────────────

gnt_profile = nt_kai_profile()
by_book = nt_kai_by_book()

# Per-book pct table for the report
by_book_pct = by_book.div(by_book.sum(axis=1), axis=0).mul(100).round(1)

# ── Charts ────────────────────────────────────────────────────────────────────

chart1 = nt_kai_function_chart()
print(f"Chart: {chart1}")

chart2 = nt_kai_book_heatmap()
print(f"Chart: {chart2}")

# ── CSVs ─────────────────────────────────────────────────────────────────────

csv1 = REPORT_DIR / 'kai-gnt-profile.csv'
gnt_profile.to_csv(csv1, index=False)
print(f"CSV:   {csv1}")

csv2 = REPORT_DIR / 'kai-by-book.csv'
by_book.to_csv(csv2)
print(f"CSV:   {csv2}")

# ── Report ────────────────────────────────────────────────────────────────────

# Interesting book comparisons
FOCUS_BOOKS = ['Mat', 'Mrk', 'Luk', 'Jhn', 'Act', 'Rom', 'Gal', 'Eph', 'Heb', 'Rev']

total = gnt_profile['count'].sum()
top_func = gnt_profile.iloc[0]

# Books with highest adjunctive %
adj_pct = by_book_pct.get('adjunctive', by_book_pct.iloc[:, 0] * 0).sort_values(ascending=False)
top_adj = adj_pct.head(5)

# Books with highest ascensive %
asc_pct = by_book_pct.get('ascensive', by_book_pct.iloc[:, 0] * 0).sort_values(ascending=False)
top_asc = asc_pct.head(5)

lines = [
    '# καί Semantic Function Analysis',
    '',
    '*Build script: [scripts/nt/discourse/build_kai_report.py]'
    '(../../../../scripts/nt/discourse/build_kai_report.py)*',
    '',
    '## Contents',
    '',
    '1. [Overview](#overview)',
    '2. [GNT-Wide Function Profile](#gnt-wide-function-profile)',
    '3. [Key Observations](#key-observations)',
    '4. [Function Definitions](#function-definitions)',
    '5. [Per-Book Distribution](#per-book-distribution)',
    '6. [Notable Instances](#notable-instances)',
    '7. [Downloads](#downloads)',
    '',
    '---',
    '',
    '## Overview',
    '',
    f'καί (G2532) is the single most frequent word in the GNT with **{total:,} tokens**. '
    'Although its default translation is "and" (additive coordination), it serves '
    'a range of semantic functions that carry significant exegetical weight — '
    'particularly the **ascensive** ("even") and **adjunctive** ("also") uses, '
    'which are often obscured by flat translation.',
    '',
    'Classification uses the per-token translator gloss from the MACULA Greek '
    'syntax layer (Nestle 1904), which captures contextual usage at the word level.',
    '',
    '---',
    '',
    '## GNT-Wide Function Profile',
    '',
    '![καί function distribution]'
    '(../../../charts/nt/discourse/nt_kai_functions.png)',
    '',
    '| Function | Count | % | Description |',
    '|---|---:|---:|---|',
]

for _, row in gnt_profile.iterrows():
    lines.append(
        f"| **{row['function']}** | {row['count']:,} | {row['pct']}% | {row['description']} |"
    )

lines += [
    '',
    '---',
    '',
    '## Key Observations',
    '',
    f'- **{top_func["function"].title()} dominates** ({top_func["pct"]}% of all καί tokens) — '
    'plain coordination is the overwhelmingly default use.',
    '',
    '- **Adjunctive καί** ("also") is the second-most-common function at '
    f'{gnt_profile.set_index("function").loc["adjunctive", "pct"]}%. '
    'It is a hallmark of Pauline argumentation: '
    + ', '.join(f'{b} ({adj_pct.get(b, 0):.1f}%)' for b in ['Rom', 'Gal', 'Eph'] if b in adj_pct.index)
    + '.',
    '',
    '- **Ascensive καί** ("even / indeed") appears '
    f'{gnt_profile.set_index("function").loc["ascensive", "count"]:,} times GNT-wide. '
    'It is rare but exegetically significant — missing it in translation flattens '
    'the rhetorical force of the clause.',
    '',
    '- Books with the **highest adjunctive %**: '
    + ', '.join(f'{b} ({v:.1f}%)' for b, v in top_adj.items()) + '.',
    '',
    '- Books with the **highest ascensive %**: '
    + ', '.join(f'{b} ({v:.1f}%)' for b, v in top_asc.items()) + '.',
    '',
    '---',
    '',
    '## Function Definitions',
    '',
    '| Function | Gloss signals | Linguistic description |',
    '|---|---|---|',
]

GLOSS_SIGNALS = {
    'additive':    '"and"',
    'adjunctive':  '"also", "and also"',
    'temporal':    '"then", "and then"',
    'ascensive':   '"even", "indeed", "truly"',
    'correlative': '"both"',
    'adversative': '"but", "yet", "although", "however"',
    'explicative': '"that"',
    'other':       'misc.',
}

for func, desc in KAI_FUNCTIONS.items():
    lines.append(f"| **{func}** | {GLOSS_SIGNALS.get(func, '')} | {desc} |")

lines += [
    '',
    '---',
    '',
    '## Per-Book Distribution',
    '',
    '![καί function by book](../../../charts/nt/discourse/nt_kai_book_heatmap.png)',
    '',
    '### Focus Books — Function % Breakdown',
    '',
    '| Book |' + ''.join(f' {f} |' for f in by_book_pct.columns) + '',
    '|---|' + '---|' * len(by_book_pct.columns),
]

for book in FOCUS_BOOKS:
    if book not in by_book_pct.index:
        continue
    row = by_book_pct.loc[book]
    lines.append('| ' + book + ' |' + ''.join(f" {row.get(f, 0):.1f}% |" for f in by_book_pct.columns))

lines += [
    '',
    '---',
    '',
    '## Notable Instances',
    '',
    '### Ascensive καί in Romans',
    '',
    '| Reference | Prev word | καί | Next word | Gloss |',
    '|---|---|---|---|---|',
]

asc_rom = nt_kai_instances(function='ascensive', book='Rom')
for _, row in asc_rom.iterrows():
    lines.append(
        f"| {row['ref']} | {row['prev_word']} | {row['text']} | {row['next_word']} | {row['gloss']} |"
    )

lines += [
    '',
    '### Adversative καί in John',
    '',
    '| Reference | Prev word | καί | Next word | Gloss |',
    '|---|---|---|---|---|',
]

adv_jhn = nt_kai_instances(function='adversative', book='Jhn')
for _, row in adv_jhn.iterrows():
    lines.append(
        f"| {row['ref']} | {row['prev_word']} | {row['text']} | {row['next_word']} | {row['gloss']} |"
    )

lines += [
    '',
    '---',
    '',
    '## Downloads',
    '',
    '| File | Description |',
    '|---|---|',
    '| [kai-gnt-profile.csv](kai-gnt-profile.csv) | GNT-wide function counts and percentages |',
    '| [kai-by-book.csv](kai-by-book.csv) | Function counts per NT book |',
    '',
]

report = REPORT_DIR / 'kai-semantic-functions.md'
report.write_text('\n'.join(lines), encoding='utf-8')
print(f"Report: {report}")
