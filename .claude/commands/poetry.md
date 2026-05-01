# Hebrew Poetry Analysis

Analyze Hebrew poetry: split verses into cola using cantillation accents,
identify parallel word pairs, and classify parallelism type
(synonymous / antithetic / synthetic).

**Usage:** `/poetry <command> [args]`

**Commands:**
- `/poetry verse <book> <chapter>:<verse>` — analyze one verse (cola split + parallelism)
- `/poetry pairs <book>` — most frequent A/B parallel word pairs in a book
- `/poetry stats <book>` — parallelism type distribution for a book
- `/poetry compare [book1 book2 ...]` — compare parallelism profiles across books

**Primary poetry books:** `Psa` · `Pro` · `Job` · `Sng` · `Lam` · `Ecc`

**Examples:**
- `/poetry verse Psa 19:2`       — "The heavens declare the glory of God"
- `/poetry verse Pro 10:1`       — classic antithetic: wise son / foolish son
- `/poetry verse Job 3:3`        — Job's lament
- `/poetry pairs Pro`            — wisdom/knowledge, mouth/lips, king/ruler…
- `/poetry pairs Psa`            — heaven/earth, day/night, soul/heart…
- `/poetry stats Psa`            — how many synonymous vs. synthetic in Psalms?
- `/poetry compare Psa Pro Job`  — compare parallelism profiles

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_verse_analysis, print_book_pairs,
                            print_parallelism_stats, compare_poetry_books,
                            POETRY_BOOKS)

raw = "$ARGUMENTS".strip().split()

if not raw:
    print('Usage: /poetry verse <book> <ch>:<vs>')
    print('       /poetry pairs <book>')
    print('       /poetry stats <book>')
    print('       /poetry compare [book1 book2 ...]')
elif raw[0] == 'verse' and len(raw) >= 3:
    book = raw[1]
    ref = raw[2]
    try:
        if ':' in ref:
            ch, vs = ref.split(':')
        else:
            ch, vs = ref, raw[3] if len(raw) > 3 else '1'
        print_verse_analysis(book, int(ch), int(vs))
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /poetry verse Psa 19:2')
elif raw[0] == 'pairs' and len(raw) >= 2:
    book = raw[1]
    print_book_pairs(book, top_n=30, min_count=2)
elif raw[0] == 'stats' and len(raw) >= 2:
    book = raw[1]
    print_parallelism_stats(book)
elif raw[0] == 'compare':
    books = raw[1:] if len(raw) > 1 else POETRY_BOOKS
    df = compare_poetry_books(books)
    print(f'\n=== Parallelism type comparison: {" / ".join(books)} ===')
    print(df.to_string())
else:
    print(f'Unknown command: {raw[0]!r}')
    print('Usage: /poetry verse|pairs|stats|compare ...')
```
