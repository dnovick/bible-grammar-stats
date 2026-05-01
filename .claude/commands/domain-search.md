# Louw-Nida Domain Search

Query the Greek NT by semantic domain (Louw-Nida taxonomy) — find all words
in a given domain, filter by subject, or compare domain profiles across books.

**Usage:** `/domain-search <domain> [subject] [book...]`

- `domain`  — Louw-Nida domain number (e.g. `33`) or name keyword (e.g. `communication`)
- `subject` — optional Strong's number: only tokens where this entity is subject
- `book...` — optional NT book IDs

**Special commands:**
- `/domain-search profile <book>` — semantic domain profile for one NT book
- `/domain-search compare <book1> <book2> ...` — compare domain profiles across books

**Examples:**
- `/domain-search 33`                       — all Communication-domain words in NT
- `/domain-search 12`                       — Supernatural Beings domain
- `/domain-search 33 G2316`                 — Communication verbs where God speaks
- `/domain-search 53 G2424 Mat Mrk Luk Jhn`— Religious Activity verbs where Jesus acts
- `/domain-search profile Rom`              — domain profile of Romans
- `/domain-search compare Rom Heb Rev`      — side-by-side domain comparison

**Key domains:**
`12` Supernatural Beings · `33` Communication · `39/40` Forgiveness ·
`41/88` Moral/Ethics · `53` Religious Activity · `31` Belief/Trust ·
`21` Salvation · `20` Death/Violence · `67` Time

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_domain_summary, print_domain_role,
                            domain_profile, domain_comparison, DOMAIN_NAMES)

raw = "$ARGUMENTS".strip().split()

if not raw:
    print('Usage: /domain-search <domain-number> [subject-strongs] [book...]')
    print('       /domain-search profile <book>')
    print('       /domain-search compare <book1> <book2> ...')
elif raw[0] == 'profile' and len(raw) > 1:
    book = raw[1]
    df = domain_profile(book, top_n=20)
    print(f'\n=== Semantic domain profile: {book} ===')
    print(df[['domain_num','domain_name','count','pct']].to_string(index=False))
elif raw[0] == 'compare' and len(raw) > 1:
    books = raw[1:]
    df = domain_comparison(books, top_n=15)
    print(f'\n=== Domain comparison: {" / ".join(books)} ===')
    print(df.to_string())
else:
    domain_arg = raw[0]
    # Resolve domain number
    try:
        domain_num = int(domain_arg)
    except ValueError:
        # Name match
        domain_num = None
        for num, name in DOMAIN_NAMES.items():
            if domain_arg.lower() in name.lower():
                domain_num = num
                break
        if domain_num is None:
            print(f'  Unknown domain: {domain_arg!r}')
            raise SystemExit(1)

    # Parse remaining args: optional subject Strong's and book list
    subject = None
    books = []
    for part in raw[1:]:
        if part.upper().startswith('G') and part[1:].isdigit():
            subject = part
        elif part.upper().startswith('H') and part[1:].isdigit():
            subject = part
        else:
            books.append(part)

    if subject:
        print_domain_role(domain_num, subject,
                          books=books or None, top_n=20,
                          subject_label=subject)
    else:
        print_domain_summary(domain_num, book=books or None, top_n=20)
```
