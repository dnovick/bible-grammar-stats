# Hebrew Verbal Syntax Analysis

Syntactic analysis of the Hebrew verb system for 2nd-year Biblical Hebrew study.
Covers verb form distribution, wayyiqtol narrative chains, infinitive construct/absolute
usage, clause type profiles, stem (binyan) distribution, and disjunctive clauses.

**Usage:** `/verbal-syntax <command> [args]`

**Commands:**
- `/verbal-syntax forms <book> [chapter]` — conjugation type distribution
- `/verbal-syntax chains <book> <chapter>` — wayyiqtol chain analysis
- `/verbal-syntax inf <book>` — infinitive construct/absolute usage
- `/verbal-syntax clauses <book>` — clause type profile (verbal/nominal/negation/conditional)
- `/verbal-syntax stems <book>` — verb stem (binyan) distribution
- `/verbal-syntax disj <book> [chapter]` — disjunctive (noun-first) clauses
- `/verbal-syntax disjchains <book> <chapter>` — chains annotated with disjunctive interruptions
- `/verbal-syntax cond <book> [chapter]` — conditional clauses (אִם/לוּ/לוּלֵא) with type classification
- `/verbal-syntax condsum <book>` — conditional type distribution summary for a book
- `/verbal-syntax report <book>` — full Markdown report (all analyses)

**Examples:**
- `/verbal-syntax forms Gen`          — wayyiqtol-heavy narrative profile
- `/verbal-syntax forms Psa`          — yiqtol-dominant poetry profile
- `/verbal-syntax forms Isa`          — prophecy: lots of qatal + yiqtol
- `/verbal-syntax forms Gen 1`        — chapter-level profile
- `/verbal-syntax chains Gen 1`       — creation narrative chains
- `/verbal-syntax chains Ruth 1`      — Ruth's return chains
- `/verbal-syntax chains 1Kgs 18`     — Elijah on Carmel chains
- `/verbal-syntax inf Gen`            — purpose (ל), temporal (ב), paronomastic abs
- `/verbal-syntax inf Deut`           — rich inf construct (law/instruction)
- `/verbal-syntax clauses Gen`        — Gen: 95% verbal, low nominal
- `/verbal-syntax clauses Pro`        — Proverbs: more nominal clauses
- `/verbal-syntax stems Gen`          — 77% Qal, 10% Hiphil
- `/verbal-syntax stems Psa`          — more Piel in poetry
- `/verbal-syntax disj Gen 1`         — Gen 1:1-2 disjunctives (setting the stage)
- `/verbal-syntax disj Gen 37`        — Gen 37:3 "Israel loved Joseph" (circumstantial)
- `/verbal-syntax disj Ruth`          — whole book disjunctive survey
- `/verbal-syntax disjchains Gen 37`  — chains + disjunctive interruptions
- `/verbal-syntax cond Gen 18`        — Abraham's bargaining (אִם + yiqtol)
- `/verbal-syntax cond Gen`           — all conditionals in Genesis
- `/verbal-syntax condsum Deu`        — Deuteronomy: 50% אִם + yiqtol
- `/verbal-syntax condsum Psa`        — Psalms conditional patterns
- `/verbal-syntax report Gen`         — full report saved to output/reports/

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_verb_form_profile, print_wayyiqtol_chains,
                            print_infinitive_usage, print_clause_type_profile,
                            print_stem_distribution, verbal_syntax_report,
                            print_disjunctive_clauses, print_disjunctive_in_chains,
                            print_conditional_clauses, print_conditional_summary)

raw = "$ARGUMENTS".strip().split()

def _usage():
    print('Usage: /verbal-syntax forms|chains|inf|clauses|stems|disj|disjchains|report <book> [args]')

if not raw:
    _usage()
elif raw[0] == 'forms' and len(raw) >= 2:
    book = raw[1]
    ch = int(raw[2]) if len(raw) > 2 else None
    print_verb_form_profile(book, ch)
elif raw[0] == 'chains' and len(raw) >= 3:
    try:
        print_wayyiqtol_chains(raw[1], int(raw[2]))
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /verbal-syntax chains Gen 1')
elif raw[0] == 'inf' and len(raw) >= 2:
    print_infinitive_usage(raw[1])
elif raw[0] == 'clauses' and len(raw) >= 2:
    print_clause_type_profile(raw[1])
elif raw[0] == 'stems' and len(raw) >= 2:
    print_stem_distribution(raw[1])
elif raw[0] == 'disj' and len(raw) >= 2:
    book = raw[1]
    ch = int(raw[2]) if len(raw) > 2 else None
    print_disjunctive_clauses(book, ch)
elif raw[0] == 'disjchains' and len(raw) >= 3:
    try:
        print_disjunctive_in_chains(raw[1], int(raw[2]))
    except Exception as e:
        print(f'Error: {e}')
        print('Usage: /verbal-syntax disjchains Gen 37')
elif raw[0] == 'cond' and len(raw) >= 2:
    book = raw[1]
    ch = int(raw[2]) if len(raw) > 2 else None
    print_conditional_clauses(book, ch)
elif raw[0] == 'condsum' and len(raw) >= 2:
    print_conditional_summary(raw[1])
elif raw[0] == 'report' and len(raw) >= 2:
    path = verbal_syntax_report(raw[1])
    print(f'Report saved: {path}')
else:
    print(f'Unknown command: {raw[0]!r}')
    _usage()
```
