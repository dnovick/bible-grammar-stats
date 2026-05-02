# Hiphil Verb Morphology Analysis

Statistical and morphological analysis of the Hebrew Hiphil (הִפְעִיל) stem
for Biblical Hebrew teaching. Covers conjugation distribution, top roots,
root × conjugation cross-tab, book distribution, dominant roots, semantic
function categories, and a full printable report with charts.

**Usage:** `/hiphil <command> [args]`

**Commands:**
- `/hiphil overview` — key statistics (total tokens, top books, top roots)
- `/hiphil conj [book]` — conjugation (tense/aspect) distribution
- `/hiphil roots [n] [book]` — top n most frequent roots (default 20)
- `/hiphil roottable [n]` — root × conjugation frequency table (top n roots)
- `/hiphil books` — Hiphil distribution across all OT books
- `/hiphil dominant` — roots where Hiphil ≥70% of all occurrences
- `/hiphil semantic` — semantic function category distribution
- `/hiphil report` — generate full Markdown report + all charts

**Examples:**
- `/hiphil overview`                — 9,409 tokens, 12.9% of all OT verbs
- `/hiphil conj`                    — yiqtol 21.5%, qatal 19.1%, wayyiqtol 18.6%
- `/hiphil conj Gen`                — Genesis Hiphil conjugation profile
- `/hiphil roots`                   — בוא/נכה/שוב/נגד/יצא top 5
- `/hiphil roots 30`                — top 30 roots
- `/hiphil roottable`               — root × form heatmap (top 15 roots)
- `/hiphil roottable 20`            — top 20 roots
- `/hiphil books`                   — Psalms leads (887), then Jeremiah, Isaiah
- `/hiphil dominant`                — נָכָה 96.2%, נוח 98.6%, שָׁכַם 100%
- `/hiphil semantic`                — causative 30.8%, violent 8.6%, declar. 7.5%
- `/hiphil report`                  — full report + 6 charts saved to output/

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_hiphil_overview, print_hiphil_conjugation,
                            print_hiphil_top_roots, print_hiphil_root_conjugation,
                            print_hiphil_book_distribution, print_hiphil_dominant_roots,
                            print_hiphil_semantic_categories, hiphil_report)

raw = "$ARGUMENTS".strip().split()

def _usage():
    print('Usage: /hiphil overview|conj|roots|roottable|books|dominant|semantic|report [args]')

if not raw:
    _usage()
elif raw[0] == 'overview':
    print_hiphil_overview()
elif raw[0] == 'conj':
    book = raw[1] if len(raw) > 1 else None
    print_hiphil_conjugation(book)
elif raw[0] == 'roots':
    n = int(raw[1]) if len(raw) > 1 and raw[1].isdigit() else 20
    book = raw[2] if len(raw) > 2 else (raw[1] if len(raw) > 1 and not raw[1].isdigit() else None)
    print_hiphil_top_roots(n, book)
elif raw[0] == 'roottable':
    n = int(raw[1]) if len(raw) > 1 else 15
    print_hiphil_root_conjugation(top_n=n)
elif raw[0] == 'books':
    print_hiphil_book_distribution()
elif raw[0] == 'dominant':
    print_hiphil_dominant_roots()
elif raw[0] == 'semantic':
    print_hiphil_semantic_categories()
elif raw[0] == 'report':
    path = hiphil_report()
    print(f'Report saved: {path}')
else:
    print(f'Unknown command: {raw[0]!r}')
    _usage()
```
