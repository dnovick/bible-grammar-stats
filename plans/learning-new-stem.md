# Plan: Learning a New Verb Stem

*Template for introducing a new Hebrew (or Aramaic) derived stem — e.g., Hiphil, Niphal, Piel, Pual, Hithpael.*
*Modeled on BBH Chapter 26 (Hiphil Strong Verbs). Adapt section numbers to the target chapter.*

---

## Purpose

This plan describes the complete set of files to create when a new derived stem is introduced in a grammar chapter. The goal is a self-contained lesson package a student can work through end-to-end: read the lesson → consult the paradigms → drill flashcards → do exercises.

---

## Directory Layout

```
output/lessons/<language>/<textbook>/ch<N>/
  README.md                              # Chapter index (see §README below)
  ch<N>-<stem>-<type>-verbs.md           # Main lesson file
  <stem>-paradigms.md                    # Full conjugation paradigm reference
  ch<N>-morphology-deck.md               # Morphology flashcard deck (Markdown)
  ch<N>-morphology-deck.txt              # Morphology flashcard deck (Anki import)
  ch<N>-vocab-deck.md                    # Vocabulary flashcard deck (Markdown)
  ch<N>-vocab-deck.txt                   # Vocabulary flashcard deck (Anki import)
  exercises/
    README.md                            # Exercise index (see §Exercises below)
    ch<N>-passage-exercise/
      README.md
      ch<N>-passage-exercise.md
      ch<N>-passage-exercise.html
      ch<N>-passage-exercise.pdf
    ch<N>-qal-<stem>-contrast/           # (stems that have a Qal counterpart)
      README.md
      ch<N>-qal-<stem>-contrast.md
      ch<N>-qal-<stem>-contrast.html
      ch<N>-qal-<stem>-contrast.pdf
    ch<N>-function-sort/                 # (stems with multiple semantic function types)
      README.md
      ch<N>-function-sort.md
      ch<N>-function-sort.html
      ch<N>-function-sort.pdf
```

> **File format rule:** Every exercise must exist in all three formats: `.md` (static answer key), `.html` (interactive, fillable), and `.pdf` (AcroForm, answers on a separate key page). Never create an exercise in fewer than three formats.

---

## README.md (Chapter Index)

Four sections, separated by `---` rules:

1. **Main Lesson** — single-row table linking to the lesson `.md` file
2. **Reference Files** — table linking to the paradigm file(s)
3. **Exercises** — single row linking to `exercises/README.md`
4. **Flashcards** — four-row table with columns `File | Format | Description`; one row each for morphology `.md`, morphology `.txt`, vocab `.md`, vocab `.txt`

---

## Main Lesson File: `ch<N>-<stem>-verbs.md`

### Header block
```
# Chapter <N> — <Stem> <Type> Verbs (<Hebrew>)

*Basics of Biblical Hebrew, Pratico & Van Pelt*
*Data: MACULA Hebrew WLC (<N> OT <Stem> tokens)*

> **Context:** <Stem rank and % of OT verb tokens>. See [OT Verb Stems Overview](...) for comparison.
```

### Section 1 — Function (`BBH §X.2`)
- Table with columns: **Function | Description | Example**
- Rows: all attested function types for this stem, in canonical textbook order
- Function types not covered by BBH: add to the bottom, mark `*(not in BBH)*`
- Close with a `> **Key diagnostic:**` callout block

### Section 2 — Form
**Diagnostic Markers** subsection: bulleted list, one line per conjugation:
`Perfect`, `Imperfect`, `Wayyiqtol`, `Imperative`, `Infinitive Construct`, `Infinitive Absolute`, `Participle`

**Paradigm — Model Root קטל** subsection: table with columns `Conjugation (linked) | 3ms Form | BBH § | Notes`
- Conjugation name is a Markdown link into the paradigm file: `[Perfect (qatal)](paradigm-file.md#perfect-qatal)`
- Use `—` for BBH § when no section exists (wayyiqtol, weqatal)
- Use GitHub-style auto-anchors (lowercase, spaces → hyphens, strip punctuation)

**Real Forms from the Pentateuch** subsection: table with columns `Conjugation | Pointed Form | Reference`
- Pick one well-known, high-frequency root (e.g. בּוֹא for Hiphil, רָאָה for Niphal)
- Show: Perfect, Wayyiqtol, Imperfect, Imperative, Participle
- Add a note about weak-root behavior

### Section 3 — Most Common Lemmas (Pentateuch)
- Source: MACULA corpus, Torah subset (Gen–Deu)
- Table: **Root | Lemma | Torah (×) | Stem Meaning | Function Type**
- Minimum 15 rows, sorted by frequency descending
- Closing callout noting any "lexically [stem]" roots with no Qal counterpart

### Section 4 — Example Passages
*One example per semantic function × conjugation form, where that combination exists in the OT.*

- One `###` subsection per function type, in the same order as Section 1
- Each subsection preceded by a `---` horizontal rule
- Prefer Torah (Gen → Exo → Lev → Num → Deu); fall back to Psalms/Proverbs, then any OT book
- Note explicitly when a function × form combination has zero OT attestations
- Format per entry:
  ```
  **Conjugation — Ref** — Hebrew text
  *"English translation."*
  → Root Stem+conjugation+PGN; one sentence grammatical/contextual note.
  ```
- When an example falls outside Torah, add a parenthetical: `*(Torah has no attestation; X is earliest.)*`

### Section 5 — Conjugation Distribution (OT-wide)
- Table: **Conjugation | Count | % of all [Stem]**
- Sorted by count descending
- Footer: `*Total OT [Stem] tokens: N across 39 books.*`
- Closing callout highlighting the most pedagogically notable distribution facts

### Section 6 — Practice
Table linking to the morphology flashcard deck `.md` and the passage exercise `.md`.

### Section 7 — Links
Table: Anki app URL + morphology deck `.txt` import file link.

---

## Paradigm File: `<stem>-paradigms.md`

One section per conjugation, in this order:
1. Perfect (Qatal)
2. Imperfect (Yiqtol)
3. Wayyiqtol
4. Weqatal
5. Imperative
6. Infinitive Construct
7. Infinitive Absolute
8. Participle (Active or Passive, as appropriate)

**Each section:**
- Plain heading text only — no `{#id}` tags (GitHub auto-anchors are used)
- Section header: `## Perfect (Qatal)` etc.
- Subtitle line: `*BBH §X.Y — [key vowel/prefix description]*`
- Full PGN table with columns: `Person | Qal | **[Stem]**`
  - Include the Qal paradigm column for direct comparison
  - Bold both the Stem column header and every Stem form
- `> **Key marker:**` callout

Close with a **Summary: Qal vs. [Stem] at a Glance** table: `Conjugation | Qal marker | **[Stem] marker**`

---

## Exercises

### Passage Exercise (`ch<N>-passage-exercise`)
- 15–25 verbs drawn from 2–4 OT passages; all must be confirmed tokens of the target stem
- Prefer Torah passages; use Psalms/Proverbs/Samuel for gaps
- Cover all 8 conjugations; document coverage in the exercise README
- Students parse: conjugation, PGN, root, semantic function
- No redundant "Is this a [Stem]?" column — every verb in the exercise is the target stem
- Answer key on a separate section/page (not interspersed)
- Exercise README: description paragraph, conjugation coverage table, files table

### Qal–[Stem] Contrast Drill (`ch<N>-qal-<stem>-contrast`)
*(Omit for stems with no Qal counterpart, e.g. pure passive stems)*
- 12–16 roots organized by semantic group (e.g. motion verbs / stative verbs / no-Qal)
- For each root: give Qal meaning + attested [Stem] form; student translates + names function type
- Cover all function types proportionally
- Exercise README: description paragraph, function coverage table, files table

### Semantic Function Sorting (`ch<N>-function-sort`)
*(Omit for stems with only one function type)*
- 20–30 attested OT forms, drawn entirely from Torah where possible
- Student classifies each as one of the function types (abbreviated: C / F / D / SA / DN etc.)
- Include ambiguous cases that reward close reasoning
- 3–5 discussion questions at the end connecting specific items to the broader grammar
- Exercise README: description paragraph, function coverage table, files table

---

## Flashcard Decks

### Morphology Deck
- 28–36 cards: one card per conjugation × root combination
- Roots: choose 3–5 high-frequency roots that span different function types
- Front: `[Stem] [Conjugation] of [Root] — [gloss]`
- Back: pointed Hebrew form + parsing notes
- Anki tags: `bbh::ch<N>`, `stem::[stem]`, `conj::[conjugation]`

### Vocabulary Deck
- Words introduced in this chapter's vocabulary list (BBH chapter vocab)
- Front: Hebrew lemma
- Back: gloss + POS + frequency + example reference
- Anki tags: `bbh::ch<N>::vocab`

---

## Formatting Conventions

- **Horizontal rules:** Every `###` subsection within Section 4 (Example Passages) must be preceded by a `---` rule — including when appending at the end of the list.
- **Bidi/verse ranges:** Never place a verse range (e.g. `6:19–20`) and Hebrew text on the same line; RTL reordering renders it backwards.
- **Bold in paradigm tables:** Bold both the column header and every form in the target stem column.
- **BBH section references:** Verify section numbers against the actual textbook chapter before writing. Niphal paradigms are in ch24 even when taught in ch25; Hiphil paradigms are in ch26. Use the actual BBH § number, not the lesson chapter number.
- **Commit message convention:** `Add BBH Ch<N> lesson: <Topic>` for initial creation; describe incremental fixes specifically.
