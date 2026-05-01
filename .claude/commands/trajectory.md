# Cross-Testament Word Trajectory

Trace any Hebrew or Greek word through OT → LXX Septuagint → NT, showing
how it travels across corpora, how consistently the LXX renders it, and
whether the NT adopts LXX vocabulary (high continuity) or diverges.

**Usage:** `/trajectory <Strong's> [report]`

- `Strong's` — OT Hebrew (e.g. `H7965`) or NT Greek (e.g. `G1515`)
- `report`   — optional: also save a Markdown + chart report to `output/reports/`

**Special commands:**
- `/trajectory summary`            — table of all 14 pre-built theological terms
- `/trajectory all`                — generate full reports for all 14 theological terms
- `/trajectory <key>`              — run a named theological term (e.g. `shalom`, `ruach`)

**Named theological terms:**
`bara` (create) · `berith` (covenant) · `ruach` (spirit) · `shalom` (peace) ·
`tsedeq` (righteousness) · `hesed` (lovingkindness) · `yeshua` (salvation) ·
`kavod` (glory) · `ahav` (love) · `emunah` (faith) · `torah` (law) ·
`padah` (redemption) · `kaphar` (atonement) · `qadosh` (holy)

**Examples:**
- `/trajectory H7965`              — shalom trajectory (OT→LXX→NT)
- `/trajectory H7307 report`       — ruach with saved Markdown + chart
- `/trajectory G1515`              — eirene in NT (starting from Greek)
- `/trajectory summary`            — all 14 terms side-by-side
- `/trajectory all`                — batch generate all 14 reports

---

```python
import sys
sys.path.insert(0, 'src')
from bible_grammar import (print_trajectory, save_trajectory_report,
                            print_theological_summary, run_theological_report,
                            run_all_theological_reports, THEOLOGICAL_TRAJECTORIES)

raw = "$ARGUMENTS".strip().split()

if not raw or raw[0] == 'summary':
    print_theological_summary()
elif raw[0] == 'all':
    run_all_theological_reports()
elif raw[0] in THEOLOGICAL_TRAJECTORIES:
    key = raw[0]
    entry = THEOLOGICAL_TRAJECTORIES[key]
    strongs = entry['strongs']
    if len(raw) > 1 and raw[1] == 'report':
        r = run_theological_report(key)
        print(f'\nReport: {r["report_path"]}')
    else:
        print_trajectory(strongs)
elif raw[0].upper().startswith(('H', 'G')) and len(raw[0]) > 1:
    strongs = raw[0]
    if len(raw) > 1 and raw[1] == 'report':
        path = save_trajectory_report(strongs)
        print(f'\nReport: {path}')
    else:
        print_trajectory(strongs)
else:
    print(f'Unknown argument: {raw[0]!r}')
    print('Usage: /trajectory <H#### or G####> [report]')
    print('       /trajectory summary')
    print('       /trajectory all')
    print('       /trajectory <term-key>  (e.g. shalom, ruach, berith)')
```
