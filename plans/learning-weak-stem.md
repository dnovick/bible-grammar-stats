# Plan: Learning the Weak Forms of a Verb Stem

*Template for a chapter that teaches weak-verb behavior in a derived stem already introduced in a prior chapter — e.g., BBH Ch25 (Niphal Weak) following Ch24 (Niphal Strong), or BBH Ch27 (Hiphil Weak) following Ch26 (Hiphil Strong).*
*Modeled on BBH Chapter 25 (Niphal Weak Verbs) and Chapter 27 (Hiphil Weak Verbs).*

---

## Purpose

This plan describes the complete file set for a chapter that extends a previously taught derived stem to its weak-root patterns. The strong forms (functions, diagnostic markers, full paradigm) were covered in the preceding chapter; this lesson focuses exclusively on seven weak classes and how they modify the strong paradigm:

| Class | Label | Representative roots |
|---|---|---|
| III-א (Lamed-Aleph) | `lamed-aleph` | מָצָא, יָרֵא |
| III-ה (Lamed-He) | `lamed-he` | גָּלָה, רָאָה |
| III-ח/ע (Lamed-Guttural) | `lamed-guttural` | שָׁמַע, שָׁלַח |
| I-guttural (Pe-Guttural) | `pe-guttural` | עָמַד, אָמַר |
| I-נ (Pe-Nun) | `pe-nun` | נָפַל, נָגַשׁ |
| I-י (Pe-Yod) | `pe-yod` | יָלַד, יָדַע |
| Biconsonantal (II-י/ו) | `biconsonantal` | קוּם, שׁוּב |

> **Not every textbook covers all seven classes in a single chapter.** BBH Ch25 (Niphal) covers 5 classes (omits III-ח/ע and Biconsonantal); BBH Ch27 (Hiphil) covers all 7. Use the class list appropriate to the actual textbook chapter, and note any omissions in the lesson file's scope callout.

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
  <stem>-weak-lamed-guttural-paradigms.md     # III-ח/ע paradigms (all 8 conjugations)
  <stem>-weak-pe-guttural-paradigms.md        # I-guttural paradigms (all 8 conjugations)
  <stem>-weak-pe-paradigms.md                 # I-נ and I-י paradigms combined (all 8 conjugations each)
  <stem>-weak-biconsonantal-paradigms.md      # Biconsonantal (II-י/ו) paradigms (all 8 conjugations)
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

> **Grouping rule for I-נ and I-י:** These two Pe-weak classes share the same assimilation behavior (both lose their first radical in the same conjugations) and are combined in a single file `<stem>-weak-pe-paradigms.md`, following the ch25/ch27 pattern. All other classes get their own file because their effects are phonologically independent.

> **Omitted classes:** If the target textbook chapter only covers a subset of the seven classes, omit the corresponding paradigm file(s). Document the omission in the main lesson file's scope callout: `> **Scope:** This chapter covers five of the seven weak classes. III-ח/ע and Biconsonantal are not treated in BBH Ch25.`

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
| [<stem>-weak-lamed-guttural-paradigms.md](...) | III-ח/ע weak paradigms with strong comparison |
| [<stem>-weak-pe-guttural-paradigms.md](...) | I-guttural weak paradigms with strong comparison |
| [<stem>-weak-pe-paradigms.md](...) | I-נ and I-י weak paradigms with strong comparison |
| [<stem>-weak-biconsonantal-paradigms.md](...) | Biconsonantal (II-י/ו) weak paradigms with strong comparison |
```

Include only the lines for classes actually covered in the chapter. The flashcard deck description should note the specific weak classes covered, e.g.:
`Morphology deck — 35 cards across 7 weak classes (III-א, III-ה, III-ח/ע, I-gutt., I-נ, I-י, Biconsonantal)`

---

## Main Lesson File: `ch<N>-<stem>-weak-verbs.md`

### Header block
```
# Chapter <N> — <Stem> Weak Verbs

*Basics of Biblical Hebrew, Pratico & Van Pelt*
*Builds on Ch<N-1> (<Stem> Strong Verbs). Weak forms only — semantic functions not repeated.*

> **Scope:** This chapter extends the <Stem> paradigm to [five/seven] weak-root classes. Each class
> modifies the strong pattern in a predictable, phonologically motivated way.
```

### Section 1 — The [Five/Seven] Weak Classes: Overview Table

A single orientation table before the per-class sections. Columns:
**Class | Label | Representative roots | What changes | Affected conjugations**

One row per weak class covered in the chapter. Recommended order: III-א, III-ה, III-ח/ע, I-guttural, I-נ, I-י, Biconsonantal. This gives the student a map before diving into the paradigm details.

Include a `> **Key principle:**` callout: all classes are predictable from phonological rules (quiescence, assimilation, compensatory lengthening, patach furtive, etc.); none requires memorizing a new stem.

### Sections 2–[N] — One section per weak class

For each class, in the order listed above:

- **Pattern description:** One paragraph explaining what phonological rule applies for this class and stem combination.
- **Diagnostic markers:** Bulleted list, one line per conjugation that differs from the strong root.
- **Paradigm summary table:** `Conjugation | Strong (קטל) | <Class> (<root1>) | <Class> (<root2>)` — 3ms form only, all 8 conjugations. Full tables are in the paradigm file; this is a quick-reference view. Two representative root columns when the two roots behave differently (e.g., I-gutt. עָמַד vs. אָמַר).
- **Link to full paradigm file.**
- **Key corpus examples:** 3–5 attested forms with references, one sentence of context each.

**Per-class section numbers and paradigm file mapping:**

| Class | Section | Paradigm file |
|---|---|---|
| III-א | 2 | `<stem>-weak-lamed-aleph-paradigms.md` |
| III-ה | 3 | `<stem>-weak-lamed-he-paradigms.md` |
| III-ח/ע | 4 | `<stem>-weak-lamed-guttural-paradigms.md` |
| I-guttural | 5 | `<stem>-weak-pe-guttural-paradigms.md` |
| I-נ | 6 | `<stem>-weak-pe-paradigms.md` (Part 1) |
| I-י | 7 | `<stem>-weak-pe-paradigms.md` (Part 2) |
| Biconsonantal | 8 | `<stem>-weak-biconsonantal-paradigms.md` |

Renumber as needed when classes are omitted.

### High-Frequency Weak Lemmas section

A single consolidated table of the most frequent OT lemmas of this stem that belong to one of the covered weak classes. Columns: **Root | Class | OT tokens (this stem) | Gloss**. Sort by frequency descending; aim for 15–20 rows total across all classes. Source from MACULA corpus.

### Practice section

Table linking to the morphology flashcard deck `.md` and both exercises. Update the card count to match the actual deck.

---

## Paradigm Files

There are up to six paradigm files for a full 7-class weak lesson (plus the strong paradigm file inherited from the prior chapter). Each class except I-נ+I-י gets its own file.

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
- `### The Pattern` subsection: one paragraph on what phonological rule applies in this conjugation. If the weak class does NOT affect this conjugation, state that explicitly.
- **Paradigm table:** columns `Person | Strong (קטל) | <Class> (<root1>) | <Class> (<root2>)`.
- `> **Key:**` callout — one sentence naming the single most important recognition marker.
- **Attested passages:** 2–4 bullet-point OT examples with full Hebrew text, reference, and one sentence of context. If a conjugation has no OT attestation for the representative root, state it explicitly and illustrate from a related root of the same class. Mark unattested theoretical forms with `†`.

**Summary at end of each file:**
`## Summary — <Class> <Stem> at a Glance`
Table: `Conjugation | Strong (קטל) | <Class> form | Key feature`

**For the `<stem>-weak-pe-paradigms.md` file (I-נ and I-י combined):**
- Part 1 covers I-נ completely (all 8 conjugations + summary)
- Part 2 covers I-י completely (all 8 conjugations + summary)
- Separate parts with a double `---` separator (two consecutive lines of `---`)
- Close with an overall comparison table: `Conjugation | Strong | I-נ | I-י (<root1>) | I-י (<root2>)`

### Class-specific notes

**III-ח/ע (Lamed-Guttural):**
- The key phenomenon is *patach furtive* (פַּתַח גְּנוּבָה) in open word-final syllables (perfect 3ms/3fs/3cp, imperfect short forms, inf. construct, participle ms)
- In short forms (wayyiqtol 3ms, imperative 2ms), *tsere* shifts to *patach* before the guttural — no furtive appears because the syllable is already short
- The furtive is written below and to the right of the preceding vowel and is pronounced *before* the guttural

**Biconsonantal (II-י/ו):**
- Strong Niphal: נִ prefix. Biconsonantal Niphal perfect and participle: **נָ prefix** (*qamets*)
- Strong Hiphil: הִ prefix perfect. Biconsonantal Hiphil perfect: **הֵ prefix** (*tsere*)
- In the Hiphil imperfect, the biconsonantal marker is *qamets* under the prefix consonant (יָ/תָּ instead of יַ/תַּ)
- Perfect 3ms and participle ms of the Niphal biconsonantal are vocally identical (both נָ prefix) — context distinguishes them

---

## Exercises

### Passage Exercise (`ch<N>-passage-exercise`)
Same format as the strong-verb plan:
- 15–25 verbs from 2–4 OT passages, all confirmed tokens of the target stem
- **Emphasis:** choose passages that include a mix of weak classes — do not draw exclusively from strong roots
- Students parse: conjugation, PGN, root, **weak class** (added column vs. the strong exercise)
- Cover as many of the covered weak classes as possible; document class distribution in the exercise README
- Answer key on a separate section/page
- Exercise README: description, class-coverage table, conjugation-coverage table, files table

### Weak-Form Identification Drill (`ch<N>-weak-form-id`)
- 35–47 pointed Hebrew forms, drawn from all covered weak classes
- Organized in two parts:
  - **Part A — By Class (5–7 groups of 5):** student sees forms from a single class and identifies conjugation + parses root. Five items per class is the target.
  - **Part B — Mixed (10–12 items):** forms from any class, randomly ordered; student identifies class first, then parses. Tests discrimination between classes.
- Answer key includes: weak class, conjugation, PGN, root, brief explanation of the diagnostic marker
- 4–6 discussion questions at the end, each comparing two classes or forms that could be confused
  - Required pairings to discuss: III-א perfect vs. participle (identical forms), I-נ vs. I-guttural in wayyiqtol, III-ה apocopation vs. I-נ short forms, Biconsonantal perfect vs. participle (also identical)
- Exercise README: description, class-distribution table, files table

> **Note:** The Qal–[Stem] Contrast Drill and Semantic Function Sorting exercises from the strong-verb plan are **omitted** for weak lessons. Functions were taught in the preceding chapter and do not change for weak roots.

---

## Flashcard Decks

### Morphology Deck
- 5 cards per covered weak class × representative conjugations (target: 25–35 total)
- Choose 1–2 representative roots per class; prioritize conjugations where the weak class is most distinctive
- **Front:** pointed Hebrew form + reference
- **Back:** root + weak class + conjugation + PGN + gloss
- Anki tags: `bbh-ch<N>`, `<stem>-<class>` (e.g. `niphal-lamed-guttural`, `niphal-biconsonantal`), `<stem>-<conjugation>`
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
- **Attested vs. unattested forms:** If a paradigm cell has no OT attestation, fill it with the theoretically expected form and mark it with `†`.
- **Horizontal rules:** Every `##` paradigm section within a weak-paradigm file must be preceded by `---`.
- **Double `---`:** When transitioning between Part 1 (I-נ) and Part 2 (I-י) in the combined pe-paradigms file, use a double `---` separator (two consecutive lines of `---`).
- **BBH section references:** For the weak lesson, BBH sections are typically grouped differently than the strong lesson. Verify the actual BBH section numbers in the chapter being written.
- **Commit message convention:** `Add BBH Ch<N> lesson: <Stem> Weak Verbs` for initial creation.
