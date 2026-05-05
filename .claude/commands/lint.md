# Pre-Commit Lint Check

Run flake8 and mypy on the source tree before committing. Both must pass clean
before a commit is made.

**Usage:** `/lint`

Run this automatically before every commit and push. If either tool reports
errors, fix them before proceeding.

---

## What to run

```bash
flake8 src/ --max-line-length=100
mypy src/ --ignore-missing-imports --no-error-summary
```

Config is in `setup.cfg`:
- `max-line-length = 100`
- `exercise_pdf.py` is excluded from E501/E221/E127/E128 (embedded Hebrew data strings)
- `__init__.py` is excluded from F401 (intentional re-exports)
- mypy: `ignore_missing_imports = True`, `check_untyped_defs = True`

---

## Pass criteria

- **flake8**: exit code 0, zero errors
- **mypy**: zero errors (excluding `exercise_pdf.py` which uses reportlab,
  a third-party library with no type stubs — filter with
  `grep -v "exercise_pdf.py"`)

---

## How to fix common issues

| Code | Issue | Fix |
|------|-------|-----|
| F401 | Unused import | Remove the import (unless in `__init__.py`) |
| F541 | f-string without placeholders | Remove the `f` prefix |
| F841 | Assigned but unused variable | Remove the assignment |
| F821 | Undefined name | Add the missing import at the top of the file |
| E501 | Line too long | Wrap string with `(\n  "part1"\n  "part2")` or add `# noqa: E501` for unsplittable strings |
| E231 | Missing whitespace after `,` | Add space after commas |
| E302 | Missing blank lines before function | Add 2 blank lines before top-level functions |
| E741 | Ambiguous variable name `l` | Rename to `ln`, `lem`, or a descriptive name |
| mypy `Name "pd" not defined` | `import pandas as pd` stripped by autoflake | Add `import pandas as pd` to file imports |
| mypy `Colormap has no attribute "colors"` | Use `[plt.get_cmap('tab10')(i) for i in range(10)]` |
| mypy `frozenset`/`set` mismatch | Change signature to `set \| frozenset` |

---

## Type annotation guidelines

- Use `from __future__ import annotations` at top of every file
- Annotate all public function signatures: parameters and return type
- Use `from typing import Any` for heterogeneous dicts/lists
- Use `dict[str, Any]` for mixed-type metadata dicts (e.g. `sections`)
- Use `list[str] | None` not `Optional[List[str]]`
- Use `# type: ignore[<code>]` only for third-party stub gaps
  (e.g. `ax.pie()` return tuple, matplotlib colormap attributes)

---

## SMS-safe Hebrew formatting (for nugget skill)

- Strip ALL diacritics (cantillation + vowel points) in SMS output
- Never mix Hebrew characters inline with Latin prose
- Hebrew only on its own dedicated lines
