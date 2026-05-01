# Object / Argument Search

Find what a given entity acts *upon* — the grammatical objects of verbs
whose subject is the given Strong's number(s). Complements `/role-search`
(which finds verbs by subject) by exposing the object/patient slot.

**Usage:** `/object-search <Strong's> [corpus] [book...]`

- `Strong's` — one or more Strong's numbers, comma-separated
- `corpus`   — `OT` (default) or `NT`
- `book...`  — optional book IDs to restrict scope

**Examples:**
- `/object-search H3068,H0430`                 — What does God act upon in the OT?
- `/object-search G2424 NT Mat Mrk Luk Jhn`   — What does Jesus act upon in the Gospels?
- `/object-search H3068 OT Isa`               — YHWH's objects in Isaiah
- `/object-search H3478`                       — What is done TO Israel?  (object_verbs)

**Output includes:**
- Terminal table of top verb+object pairs by frequency
- Separate `object_verbs` call shows what verbs are performed *on* the entity

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import print_object_summary, object_verbs

raw = "$ARGUMENTS".strip().split()
strongs_raw = raw[0] if raw else 'H3068,H0430'
strongs = strongs_raw.split(',')

corpus = 'OT'
books = []
for part in raw[1:]:
    if part in ('OT', 'NT'):
        corpus = part
    else:
        books.append(part)

label = '+'.join(strongs)
print_object_summary(strongs, corpus, books=books or None, top_n=20, label=label)

print('\n--- What verbs are performed ON this entity? ---')
ov = object_verbs(strongs, corpus, books=books or None)
if not ov.empty:
    print(ov.head(20).to_string(index=False))
else:
    print('  No results.')
```
