# Hebrew Poetry Analysis

Analyze Hebrew poetry: cola splitting, parallelism, chiasm detection, acrostic
detection, and meter/stress counting.

**Usage:** `/poetry <command> [args]`

**Commands:**
- `/poetry verse <book> <chapter>:<verse>` — analyze one verse (cola split + parallelism)
- `/poetry pairs <book>` — most frequent A/B parallel word pairs in a book
- `/poetry stats <book>` — parallelism type distribution for a book
- `/poetry compare [book1 book2 ...]` — compare parallelism profiles across books
- `/poetry chiasm <book> <ch> <vs1> <vs2>` — detect A B B' A' structure across verses
- `/poetry acrostic <book> <ch> <vs1> <vs2> [stanza]` — detect alphabetic acrostic
- `/poetry meter <book> <ch>:<vs>` — stress/syllable count for one verse
- `/poetry meterstats <book>` — meter pattern distribution for a whole book

**Primary poetry books:** `Psa` · `Pro` · `Job` · `Sng` · `Lam` · `Ecc`

**Examples:**
- `/poetry verse Psa 19:2`          — "The heavens declare the glory of God"
- `/poetry verse Pro 10:1`          — classic antithetic: wise son / foolish son
- `/poetry pairs Pro`               — wisdom/knowledge, mouth/lips, king/ruler…
- `/poetry stats Psa`               — how many synonymous vs. synthetic in Psalms?
- `/poetry compare Psa Pro Job`     — compare parallelism profiles
- `/poetry chiasm Psa 8 1 9`        — check Psalm 8 for chiastic structure
- `/poetry chiasm Psa 23 1 6`       — Psalm 23 chiasm analysis
- `/poetry acrostic Psa 119 1 176 8` — Psalm 119 (stanza=8 verses per letter)
- `/poetry acrostic Lam 1 1 22`     — Lamentations 1 acrostic
- `/poetry acrostic Psa 25 1 22`    — Psalm 25 acrostic
- `/poetry meter Lam 1:1`           — classic qinah 3+2 meter
- `/poetry meterstats Lam`          — how much qinah in Lamentations?

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_verse_analysis, print_book_pairs,
                            print_parallelism_stats, compare_poetry_books,
                            print_chiasm, print_acrostic,
                            print_verse_meter, print_meter_stats,
                            POETRY_BOOKS)

raw = "$ARGUMENTS".strip().split()

def _parse_ref(ref_str):
    if ':' in ref_str:
        ch, vs = ref_str.split(':', 1)
        return int(ch), int(vs)
    return int(ref_str), 1

if not raw:
    print('Usage: /poetry verse|pairs|stats|compare|chiasm|acrostic|meter|meterstats ...')
elif raw[0] == 'verse' and len(raw) >= 3:
    book = raw[1]
    ref = raw[2]
    try:
        ch, vs = _parse_ref(ref)
        print_verse_analysis(book, ch, vs)
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /poetry verse Psa 19:2')
elif raw[0] == 'pairs' and len(raw) >= 2:
    print_book_pairs(raw[1], top_n=30, min_count=2)
elif raw[0] == 'stats' and len(raw) >= 2:
    print_parallelism_stats(raw[1])
elif raw[0] == 'compare':
    books = raw[1:] if len(raw) > 1 else POETRY_BOOKS
    from bible_grammar import compare_poetry_books
    df = compare_poetry_books(books)
    print(f'\n=== Parallelism type comparison: {" / ".join(books)} ===')
    print(df.to_string())
elif raw[0] == 'chiasm' and len(raw) >= 5:
    try:
        book, ch, vs1, vs2 = raw[1], int(raw[2]), int(raw[3]), int(raw[4])
        print_chiasm(book, ch, vs1, vs2)
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /poetry chiasm Psa 23 1 6')
elif raw[0] == 'acrostic' and len(raw) >= 5:
    try:
        book, ch, vs1, vs2 = raw[1], int(raw[2]), int(raw[3]), int(raw[4])
        stanza = int(raw[5]) if len(raw) > 5 else 1
        print_acrostic(book, ch, vs1, vs2, stanza_size=stanza)
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /poetry acrostic Lam 1 1 22')
elif raw[0] == 'meter' and len(raw) >= 3:
    try:
        book = raw[1]
        ch, vs = _parse_ref(raw[2])
        print_verse_meter(book, ch, vs)
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /poetry meter Lam 1:1')
elif raw[0] == 'meterstats' and len(raw) >= 2:
    try:
        print_meter_stats(raw[1])
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /poetry meterstats Lam')
else:
    print(f'Unknown command: {raw[0]!r}')
    print('Usage: /poetry verse|pairs|stats|compare|chiasm|acrostic|meter|meterstats ...')
```
