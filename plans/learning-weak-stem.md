# Plan: Learning the Weak Forms of a Verb Stem

*Template for a chapter that teaches weak-verb behavior in a derived stem already introduced in a prior chapter — e.g., BBH Ch25 (Niphal Weak) following Ch24 (Niphal Strong).*
*Modeled on BBH Chapter 25 (Niphal Weak Verbs) and the `niphal-weak-pe-paradigms.md` reference file.*

---

## Purpose

This plan describes the complete file set for a chapter that extends a previously taught derived stem to its weak-root patterns. The strong forms (functions, diagnostic markers, full paradigm) were covered in the preceding chapter; this lesson focuses exclusively on five weak classes and how they modify the strong paradigm:

| Class | Label | Representative roots |
|---|---|---|
| III-א (Lamed-Aleph) | `lamed-aleph` | מָצָא, יָרָא |
| III-ה (Lamed-He) | `lamed-he` | גָּלָה, רָאָה |
| I-guttural (Pe-Guttural) | `pe-guttural` | עָמַד, אָמַר |
| I-נ (Pe-Nun) | `pe-nun` | נָפַל, נָגַשׁ |
| I-י (Pe-Yod) | `pe-yod` | יָלַד, יָדַע |

> **Scope distinction:** This plan does NOT re-teach semantic functions, real-forms tables, lemma frequency, or conjugation distribution — those belong to the strong-verb plan. The weak lesson is narrower: phonological patterns, paradigm tables, recognition markers, and corpus examples.

---

## Directory Layout

```
output/lessons/<language>/<textbook>/ch<N>/
  README.md                                   # Chapter index (see §README below)
  ch<N>-<stem>-weak-verbs.md                  # Main lesson file
  <stem>-paradigms.md                         # LINK ONLY — from the strong chapter; do not recreate
  <stem>-weak-lamed-aleph-paradigms.md        # III-א paradigms (all 8 conjugations)
  <stem>-weak-lamed-he-paradigms.md           # III-ה paradigms (all 8 conjugations)
  <stem>-weak-pe-guttural-paradigms.md        # I-guttural paradigms (all 8 conjugations)
  <stem>-weak-pe-paradigms.md                 # I-נ and I-י paradigms combined (all 8 conjugations each)
  ch<N>-morphology-deck.md                    # Morphology flashcard deck (Markdown)
  ch<N>-morphology-deck.txt                   # Morphology flashcard deck (Anki import)
  ch<N>-vocab-deck.md                         # Vocabulary flashcard deck (Markdown)
  ch<N>-vocab-deck.txt                        # Vocabulary flashcard deck (Anki import)
  exercises/
    README.md                                 # Exercise index
    ch<N>-passage-exercise/
      README.md
      ch<N>-passage-exercise.md
      ch<N>-passage-exercise.html
      ch<N>-passage-exercise.pdf
    ch<N>-weak-form-id/
      README.md
      ch<N>-weak-form-id.md
      ch<N>-weak-form-id.html
      ch<N>-weak-form-id.pdf
```

> **Grouping rule for I-נ and I-י:** These two Pe-weak classes share the same assimilation behavior (both lose their first radical in the same conjugations) and are combined in a single file `<stem>-weak-pe-paradigms.md`, following the ch25 pattern. III-א, III-ה, and I-guttural each get their own file because their effects are phonologically independent.

> **File format rule:** Every exercise must exist in all three formats: `.md` (static answer key), `.html` (interactive, fillable), and `.pdf` (AcroForm, answers on a separate key page).

---

## README.md (Chapter Index)

Same four-section structure as the strong-verb plan, but the **Reference Files** section now lists multiple paradigm files:

```markdown
## Reference Files

| File | Description |
|---|---|
| [<stem>-paradigms.md](<stem>-paradigms.md) | Strong paradigm reference (from Ch<N-1>) |
| [<stem>-weak-lamed-aleph-paradigms.md](...) | III-א weak paradigms with strong comparison |
| [<stem>-weak-lamed-he-paradigms.md](...) | III-ה weak paradigms with strong comparison |
| [<stem>-weak-pe-guttural-paradigms.md](...) | I-guttural weak paradigms with strong comparison |
| [<stem>-weak-pe-paradigms.md](...) | I-נ and I-י weak paradigms with strong comparison |
```

The flashcard deck description should note the specific weak classes covered, e.g.:
`Morphology deck — 28 cards across 5 weak classes (III-א, III-ה, I-gutt., I-נ, I-י) and 5 conjugations`

---

## Main Lesson File: `ch<N>-<stem>-weak-verbs.md`

### Header block
```
# Chapter <N> — <Stem> Weak Verbs

*Basics of Biblical Hebrew, Pratico & Van Pelt*
*Builds on Ch<N-1> (<Stem> Strong Verbs). Weak forms only — semantic functions not repeated.*

> **Scope:** This chapter extends the <Stem> paradigm to five weak-root classes. Each class
> modifies the strong pattern in a predictable, phonologically motivated way.
```

### Section 1 — The Five Weak Classes: Overview Table

A single orientation table before the per-class sections. Columns:
**Class | What changes | Affected conjugations | Diagnostic signal**

One row per weak class in this order: III-א, III-ה, I-guttural, I-נ, I-י. This gives the student
a map before diving into the paradigm details.

Include a `> **Key principle:**` callout: all five classes are predictable from phonological rules
(quiescence, assimilation, compensatory lengthening, etc.); none requires memorizing a new stem.

### Section 2 — III-א (Lamed-Aleph) Verbs

- **Pattern description:** One paragraph explaining that א quiesces at the end of a word and causes the preceding vowel to lengthen compensatorily. Key conjugations affected: perfect 3ms/3fs (tsere not patah), imperfect (final form shape).
- **Diagnostic markers:** Bulleted list, one line per conjugation that differs from the strong root.
- **Paradigm summary table:** 3-column table — `Conjugation | Strong (קטל) | III-א (מצא)` — 3ms form only, all 8 conjugations. Full tables are in the paradigm file; this is a quick-reference view.
- **Link to full paradigm file.**
- **Key corpus examples:** 3–5 attested forms with references, one sentence of context each.

### Section 3 — III-ה (Lamed-He) Verbs

Same structure as Section 2. Representative roots: גָּלָה, רָאָה.
- Pattern: the ה ending is not a true root letter but a vowel letter; the final syllable contracts and takes a distinctive ending (-הּ in some forms, disappears in others).
- Paradigm summary table: `Strong (קטל) | III-ה (גלה)`.

### Section 4 — I-guttural (Pe-Guttural) Verbs

Same structure. Representative roots: עָמַד, אָמַר.
- Pattern: Gutturals (א ה ח ע) cannot take dagesh forte; when the Niphal's assimilated-נ would cause a dagesh in the first radical, compensatory lengthening of the preceding vowel occurs instead.
- Affected conjugations: imperfect, wayyiqtol, imperative, infinitives (the dagesh-forte conjugations).
- Paradigm summary table: `Strong (קטל) | I-gutt. (עמד)`.

### Section 5 — I-נ (Pe-Nun) Verbs

Same structure. Representative root: נָפַל.
- Pattern: נ assimilates into the following consonant in the same conjugations as the regular Niphal's prefix-נ assimilation, producing a doubled first radical (dagesh forte).
- Key point: I-נ verbs therefore show dagesh in R1 in imperfect/wayyiqtol/imperative/infinitives — the same conjugations as the strong Niphal — but for a different reason (the root's own נ, not the Niphal prefix).
- Paradigm summary table: `Strong (קטל) | I-נ (נפל)`.

### Section 6 — I-י (Pe-Yod) Verbs

Same structure. Two representative roots: יָלַד, יָדַע.
- Pattern: I-י splits into two sub-paradigms: perfect/weqatal/participle use נוֹ- prefix; imperfect/wayyiqtol/imperative/infinitives use יִוָּ-/הִוָּ-.
- This is the most complex of the five classes and warrants a slightly longer treatment.
- Paradigm summary table with three columns: `Strong (קטל) | I-י (ילד) | I-י (ידע)`.
- Note: certain I-י verbs behave as I-ו (Pe-Vav) in other stems; the Niphal always shows the יִוָּ-/נוֹ- split.

### Section 7 — High-Frequency Weak Lemmas

A single consolidated table of the most frequent OT lemmas of this stem that belong to one of the five weak classes. Columns: **Root | Class | OT tokens (this stem) | Gloss**. Sort by frequency descending; aim for 15–20 rows total across all five classes. Source from MACULA corpus.

### Section 8 — Practice

Table linking to the morphology flashcard deck `.md` and both exercises.

---

## Paradigm Files

There are four paradigm files for a weak lesson (plus the strong paradigm file inherited from the prior chapter).

### Structure of each weak paradigm file

**File header:**
```
# <Stem> Weak Verbs — <Class> Paradigms

*Full conjugation tables for <class description> roots in the <Stem> stem.*
*Representative root(s): <root(s) with gloss>.*
*Each section shows the strong root (קטל) alongside the weak paradigm for direct comparison.*
*Attested forms drawn from MACULA Hebrew WLC.*
```

**For each of the 8 conjugations, in order:**
1. `## Perfect (Qatal)` (no `{#id}` tags; GitHub auto-anchors)
2. `## Imperfect (Yiqtol)`
3. `## Wayyiqtol`
4. `## Weqatal`
5. `## Imperative`
6. `## Infinitive Construct`
7. `## Infinitive Absolute`
8. `## Participle`

**Each conjugation section:**
- `### The Pattern` subsection: one paragraph on what phonological rule applies in this conjugation. If the weak class does NOT affect this conjugation (e.g. I-guttural does not affect the perfect), state that explicitly: *"The perfect of I-guttural roots is identical to the strong paradigm."*
- **Paradigm table:** columns `Person | Strong (קטל) | <Class> (<root>)`. For I-י, use three data columns: `Strong (קטל) | I-י (ילד) | I-י (ידע)`. For I-גuttural, show a second representative root in a third column when the two roots behave differently.
- `> **Key:**` callout — one sentence naming the single most important recognition marker.
- **Attested passages:** 2–4 bullet-point OT examples with full Hebrew text, reference, and one sentence of context. If a conjugation has no OT attestation for the representative root, state it explicitly and illustrate from a related root of the same class.

**Summary at end of each file:**
`## Summary — <Class> <Stem> at a Glance`
Table: `Conjugation | Strong (קטל) | <Class> form | Key feature`

**For the `<stem>-weak-pe-paradigms.md` file (I-נ and I-י combined):**
- Part 1 covers I-נ completely (all 8 conjugations + summary)
- Part 2 covers I-י completely (all 8 conjugations + summary)
- Close with an overall comparison table: `Conjugation | Strong | I-נ | I-י (ילד) | I-י (ידע)`

---

## Exercises

### Passage Exercise (`ch<N>-passage-exercise`)
Same format as the strong-verb plan:
- 15–25 verbs from 2–4 OT passages, all confirmed tokens of the target stem
- **Emphasis:** choose passages that include a mix of weak classes — do not draw exclusively from strong roots
- Students parse: conjugation, PGN, root, **weak class** (added column vs. the strong exercise)
- Cover as many of the 5 weak classes as possible; document class distribution in the exercise README
- Answer key on a separate section/page
- Exercise README: description, class-coverage table, conjugation-coverage table, files table

### Weak-Form Identification Drill (`ch<N>-weak-form-id`)
- 20–25 pointed Hebrew forms, drawn from all five weak classes
- Organized in two parts:
  - **Part A — By Class (5 groups of 4–5):** student sees forms from a single class and identifies conjugation + parses root. Good for building class-by-class recognition.
  - **Part B — Mixed (10 items):** forms from any class, randomly ordered; student identifies class first, then parses. Tests discrimination between classes.
- Answer key includes: weak class, conjugation, PGN, root, brief explanation of the diagnostic marker that reveals the weak class
- 3–4 discussion questions at the end, each comparing two classes that could be confused (e.g. I-נ vs. strong root with dagesh, or III-ה vs. III-א in the perfect)
- Exercise README: description, class-distribution table, files table

> **Note:** The Qal–[Stem] Contrast Drill and Semantic Function Sorting exercises from the strong-verb plan are **omitted** for weak lessons. Functions were taught in the preceding chapter and do not change for weak roots.

---

## Flashcard Decks

### Morphology Deck
- 25–35 cards: one card per weak-class × conjugation combination
- Choose 1–2 representative roots per class; prioritize conjugations where the weak class is most distinctive
- **Front:** pointed Hebrew form + reference
- **Back:** root + weak class + conjugation + PGN + gloss
- Anki tags: `bbh-ch<N>`, `<stem>-<class>` (e.g. `niphal-lamed-he`), `<stem>-<conjugation>`
- Include a CSV section at the bottom of the `.md` file (same as the strong-verb plan)
- `.txt` file headers: `#separator:tab`, `#html:false`, `#notetype:Basic`, `#deck:BBH Chapter <N> — <Stem> Weak`, `#tags column:3`

### Vocabulary Deck
- Words introduced in this chapter's BBH vocabulary list (always use the actual textbook list)
- Same format as the strong-verb plan: Front = Hebrew lemma; Back = gloss + stems + frequency
- Anki tags: `bbh-ch<N>-vocab`, `bbh-ch<N>-verb`, `bbh-ch<N>-noun`, etc.

---

## Formatting Conventions

All conventions from `learning-new-stem.md` apply here, plus:

- **Paradigm columns:** When a conjugation is unaffected by the weak class, say so explicitly in a `> **Note:**` callout rather than silently repeating the strong form.
- **Attested vs. unattested forms:** If a paradigm cell has no OT attestation, fill it with the theoretically expected form and mark it with `†` or a footnote.
- **Horizontal rules:** Every `##` paradigm section within a weak-paradigm file must be preceded by `---`.
- **Double `---`:** When transitioning between Part 1 (I-נ) and Part 2 (I-י) in the combined pe-paradigms file, use a double `---` separator (two consecutive lines of `---`), as established in ch25's `niphal-weak-pe-paradigms.md`.
- **BBH section references:** For the weak lesson, BBH sections are typically grouped differently than the strong lesson. Verify the actual BBH section numbers in the chapter being written.
- **Commit message convention:** `Add BBH Ch<N> lesson: <Stem> Weak Verbs` for initial creation.
