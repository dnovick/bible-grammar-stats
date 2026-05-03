# Lesson Syllabus Prep

Generate a complete lesson syllabus file for a Biblical Hebrew (or Greek) grammar chapter.
Pulls frequency/morphology data from MACULA, writes structured Markdown to the correct
output path, and optionally generates a full paradigm reference file.

**Usage:** `/lesson <language> <textbook> <chapter> <stem-or-topic>`

- `language` — `hebrew`, `greek`, or `aramaic`
- `textbook` — textbook abbreviation: `bbh` (Basics of Biblical Hebrew), `mounce`, etc.
- `chapter` — chapter number, e.g. `26`
- `stem-or-topic` — the grammatical topic, e.g. `"Hiphil Strong Verbs"`, `"Niphal"`, `"Piel"`

**Output paths:**
- Lesson file: `output/lessons/<language>/<textbook>/ch<N>/ch<N>-<slug>.md`
- Paradigm file: `output/lessons/<language>/<textbook>/ch<N>/<stem>-paradigms.md`

**Examples:**
- `/lesson hebrew bbh 26 "Hiphil Strong Verbs"`
- `/lesson hebrew bbh 27 "Hiphil Weak Verbs"`
- `/lesson hebrew bbh 14 "Niphal"`
- `/lesson hebrew bbh 15 "Piel and Pual"`

---

## What the lesson file must contain

### 1. Function (BBH §X.2 or equivalent)
A table with columns: **Function | Description | Example**.
Rows: Causative, Declarative, Factitive, Simple action, Denominative (mark *(not in BBH)* if absent from the textbook).
Include a "Key diagnostic" callout block.

### 2. Form — Diagnostic Markers
Bullet list of the prefix/vowel pattern for each conjugation:
Perfect, Imperfect, Wayyiqtol, Imperative, Infinitive Construct, Infinitive Absolute, Participle.

### 3. Paradigm Table
Links to the paradigm file sections. Columns: **Conjugation (linked) | 3ms Form | BBH § | Notes**.
- Conjugation name is a Markdown link: `[Perfect (qatal)](paradigm-file.md#perfect-qatal)`
- Use `—` for BBH § when no section exists (wayyiqtol, weqatal).
- Use GitHub auto-generated anchors (lowercase, spaces→hyphens, strip punctuation).

### 4. Real Forms Table — a single high-frequency root
Show Perfect, Wayyiqtol, Imperfect, Imperative, Participle for one well-known root (e.g. בּוֹא for Hiphil).
Include a note about weak-root behavior if applicable.

### 5. Most Common Lemmas (Torah / Pentateuch)
Query `hiphil_data()` (or the appropriate stem function) filtered to Genesis–Deuteronomy.
Table: **Root | Lemma | Torah (×) | Hiphil/Stem Meaning | Function Type**.
Top 15 lemmas minimum.

### 6. Example Passages
**One example per semantic function × conjugation form** (where the combination exists in the OT).
- Organize by function type with `### Causative`, `### Declarative`, `### Factitive`, `### Simple Action` subsections.
- Prefer Torah (Gen→Exo→Lev→Num→Deu); fall back to Psa/Pro/Job, then any OT book.
- Note explicitly when a function × form combination has zero OT attestations.
- Each entry format:
  ```
  **Conjugation — Ref** — Hebrew text
  *"English translation."*
  → Root Stem+conjugation+PGN; one sentence of grammatical/contextual explanation.
  ```

### 7. Conjugation Distribution (OT-wide)
Table: **Conjugation | Count | % of all [stem]**.
Pull from `hiphil_conjugation_profile()` or equivalent.
Include a teaching note callout about the most notable distribution patterns.

---

## Paradigm file structure

One section per conjugation with a full person/number/gender table plus a `> Key marker:` callout.
Use plain heading text (no `{#id}` tags) so GitHub auto-anchors work correctly.

Sections in order: Perfect (Qatal), Imperfect (Yiqtol), Wayyiqtol, Weqatal, Imperative, Infinitive Construct, Infinitive Absolute, Participle (Active).

Close with a **Summary** table: Conjugation | Prefix | Final vowel | Quick ID.

---

## Data queries to run

```python
import sys
sys.path.insert(0, 'src')
import pandas as pd
from bible_grammar.hiphil import hiphil_data, hiphil_conjugation_profile

# All Hiphil tokens
df = hiphil_data()

# Torah subset for lemma frequency table
torah = ['Gen','Exo','Lev','Num','Deu']
torah_df = df[df['book'].isin(torah)]

# Conjugation morph code map
conj_map = {
    'Vhq': 'Perfect', 'Vhw': 'Wayyiqtol', 'Vhi': 'Imperfect',
    'Vhp': 'Weqatal',  'Vhv': 'Imperative', 'Vhc': 'Inf. Construct',
    'Vha': 'Inf. Absolute', 'Vhrm': 'Participle',
}

def morph_to_conj(m):
    for code, name in conj_map.items():
        if m.startswith(code): return name
    return None

df['conj'] = df['morph'].apply(morph_to_conj)

# Canonical book order for best-example selection
canon = ['Gen','Exo','Lev','Num','Deu','Jos','Jdg','Rut','1Sa','2Sa',
         '1Ki','2Ki','1Ch','2Ch','Ezr','Neh','Est','Job','Psa','Pro',
         'Ecc','Sng','Isa','Jer','Lam','Ezk','Dan','Hos','Jol','Amo',
         'Oba','Jon','Mic','Nah','Hab','Zep','Hag','Zec','Mal']
book_pri = {b: i for i, b in enumerate(canon)}
df['book_pri'] = df['book'].map(book_pri).fillna(99)
```

Adapt the morph codes for other stems (Niphal: `Vn*`, Piel: `Vp*`, etc.).

---

## After generating files

1. Verify all paradigm links resolve correctly (heading text → GitHub anchor slug).
2. Commit with message: `Add BBH Ch<N> lesson: <Topic>`.
3. Offer to commit and push.
