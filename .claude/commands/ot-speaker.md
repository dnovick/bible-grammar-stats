# OT Speaker Attribution

Find all speech-verb tokens in the Hebrew OT whose grammatical subject
resolves to a given entity via MACULA Hebrew `subjref` links.

**Usage:** `/ot-speaker <Strong's> [book...]`

- `Strong's` — one or more Strong's numbers, comma-separated
  `H3068,H0430` (YHWH+Elohim), `H4872` (Moses), `H0347` (Job)
- `book...`  — optional book IDs to restrict scope

**Special commands:**
- `/ot-speaker who <book>` — show all speakers in a book (character breakdown)
- `/ot-speaker bybook` — divine speech percentage for every OT book

**Examples:**
- `/ot-speaker H3068,H0430`         — all YHWH/Elohim speech in the OT
- `/ot-speaker H3068,H0430 Isa`    — YHWH speech in Isaiah
- `/ot-speaker who Job`             — who speaks in Job?
- `/ot-speaker bybook`             — divine speech % per book

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_speaker_summary, print_divine_speech_by_book,
                            who_speaks, speaker_report)

raw = "$ARGUMENTS".strip().split()

if not raw:
    print_divine_speech_by_book(min_count=3)
elif raw[0] == 'bybook':
    print_divine_speech_by_book(min_count=3)
elif raw[0] == 'who' and len(raw) > 1:
    book = raw[1]
    print(f'\n=== All speakers in {book} ===')
    df = who_speaks(book, top_n=20)
    if df.empty:
        print('  No results.')
    else:
        print(df.to_string(index=False))
else:
    strongs_raw = raw[0]
    strongs = strongs_raw.split(',')
    books = raw[1:] or None
    label = '+'.join(strongs)
    print_speaker_summary(strongs, books=books, top_n=20, label=label)
    report = speaker_report(strongs, books=books, label=label,
                            output_dir='output/reports')
    print(f'\nReport: {report}')
```
