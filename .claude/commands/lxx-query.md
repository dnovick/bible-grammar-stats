# LXX Query

Query the Septuagint (LXX Rahlfs 1935, CenterBLC edition) as a full
morphologically-tagged Greek corpus. Find words, verb stats, per-book
distribution, or frequency tables.

**Usage:** `/lxx-query <Strong's-or-lemma> [book_or_group]`

- `Strong's` — Greek Strong's number, e.g. `G1242` (διαθήκη), `G2316` (θεός)
- `lemma`    — Greek lemma string, e.g. `εἰρήνη`
- `book_or_group` — optional book_id (e.g. `Isa`) or group (`torah`, `prophets`)

**Examples:**
- `/lxx-query G1242`              — διαθήκη (covenant) across the LXX
- `/lxx-query G2316 prophets`     — θεός in the LXX Prophets
- `/lxx-query G4151 Isa`          — πνεῦμα in Isaiah
- `/lxx-query G2588`              — καρδία (heart) — LXX rendering of לֵב

**Output includes:**
- Total occurrences (canonical + deuterocanon breakdown)
- Per-book count table (canonical OT order)
- Verb tense/voice/mood breakdown (if the word is a verb)

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import print_lxx_query, lxx_verb_stats

raw = "$ARGUMENTS".strip().split()
if not raw:
    print("Usage: /lxx-query <Strong's> [book_or_group]")
else:
    term = raw[0]
    rest = raw[1] if len(raw) > 1 else None
    book_groups = {'torah', 'historical', 'wisdom', 'prophets'}
    book_arg = None
    group_arg = None
    if rest:
        if rest.lower() in book_groups:
            group_arg = rest.lower()
        else:
            book_arg = rest

    # Determine if it's a Strong's number or a lemma
    if term.upper().startswith('G') and term[1:].isdigit():
        print_lxx_query(strongs=term, book=book_arg, book_group=group_arg, top_n=20)
    else:
        print_lxx_query(lemma=term, book=book_arg, book_group=group_arg, top_n=20)
```
