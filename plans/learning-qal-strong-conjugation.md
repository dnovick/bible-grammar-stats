# Plan: Learning a Qal Conjugation — Strong Verbs

*Template for introducing a single Qal conjugation form in its strong-verb (no weak consonants) version.*
*Covers: BBH Ch13 (Qal Perfect), Ch15 (Qal Imperfect), Ch18 (Qal Imperative),*
*Ch20 (Qal Infinitive Construct), Ch21 (Qal Infinitive Absolute), Ch22 (Qal Participle).*

---

## Purpose

This plan describes the complete file set for a chapter that introduces one Qal conjugation form
for strong (fully regular, no weak consonants) roots. The Qal is the base stem; there are no
Causative/Declarative/Factitive function categories. Instead, the key teaching concerns are:

- **Aspect or mode** — what the conjugation expresses (perfective completion, imperfective
  action, command, purpose, etc.)
- **Form** — the prefix/suffix pattern and vowel signatures
- **Paradigm** — the full person/number/gender inflection table (for inflected forms)
- **Stative vs. fientive** — relevant for Perfect and Imperfect (stative roots use different
  theme vowels)

> **Scope difference from derived-stem lessons:** Derived stem chapters (Ch24 Niphal, Ch26
> Hiphil, etc.) organize example passages by semantic function type (Causative, Declarative,
> Factitive). Qal conjugation chapters organize them by usage type (Simple Past, Perfect of
> Experience, Prophetic Perfect, etc. — or Future, Habitual, Modal, etc.). The exercises are
> also different: a **parsing drill** replaces the function-sort; no Qal–stem contrast drill.

---

## Directory Layout

```
output/lessons/<language>/<textbook>/ch<N>/
  README.md                              # Chapter index (see §README below)
  ch<N>-qal-<conjugation>-strong.md     # Main lesson file (e.g. ch13-qal-perfect-strong.md)
  qal-<conjugation>-paradigm.md         # Full PGN paradigm + stative variants (if applicable)
  ch<N>-morphology-deck.md              # Morphology flashcard deck (Markdown)
  ch<N>-morphology-deck.txt             # Morphology flashcard deck (Anki import)
  ch<N>-vocab-deck.md                   # Vocabulary flashcard deck (Markdown)
  ch<N>-vocab-deck.txt                  # Vocabulary flashcard deck (Anki import)
  exercises/
    README.md                           # Exercise index
    ch<N>-passage-exercise/
      README.md
      ch<N>-passage-exercise.md
      ch<N>-passage-exercise.html
      ch<N>-passage-exercise.pdf
    ch<N>-parsing-drill/
      README.md
      ch<N>-parsing-drill.md
      ch<N>-parsing-drill.html
      ch<N>-parsing-drill.pdf
```

> **File format rule:** Every exercise must exist in all three formats: `.md` (static answer key),
> `.html` (interactive, fillable), and `.pdf` (AcroForm, answers on a separate key page).

> **Conjugation slug table:**
> | BBH chapter | Conjugation | Slug |
> |---|---|---|
> | Ch13 | Perfect (Qatal) | `perfect` |
> | Ch15 | Imperfect (Yiqtol) | `imperfect` |
> | Ch18 | Imperative | `imperative` |
> | Ch20 | Infinitive Construct | `infinitive-construct` |
> | Ch21 | Infinitive Absolute | `infinitive-absolute` |
> | Ch22 | Participle | `participle` |

---

## README.md (Chapter Index)

Four sections, separated by `---` rules:

1. **Main Lesson** — single-row table linking to the lesson `.md` file
2. **Reference Files** — table linking to the paradigm `.md` file
3. **Exercises** — single row linking to `exercises/README.md`
4. **Flashcards** — four-row table with columns `File | Format | Description`; one row each
   for morphology `.md`, morphology `.txt`, vocab `.md`, vocab `.txt`

---

## Main Lesson File: `ch<N>-qal-<conjugation>-strong.md`

### Header block
```
# Chapter <N> — Qal <Conjugation> (Strong Verbs)

*Basics of Biblical Hebrew, Pratico & Van Pelt*
*Data: MACULA Hebrew WLC (~<N>k Qal <Conjugation> tokens OT-wide)*

> **Context:** The Qal <conjugation> accounts for X% of all Qal verb tokens in the OT
> (Y total). See the complete Qal conjugation distribution in §<N>.8 of this lesson.
```

### Section 1 — The Hebrew Verb System: A Brief Overview
*(Only for the first Qal conjugation chapter, Ch13. Omit for Ch15+.)*
- Three-consonant roots (triliteral); a few biconsonantal/geminate roots
- Seven major stems (binyanim): Qal (base), Niphal, Piel, Pual, Hiphil, Hophal, Hithpael
- Two major aspects (not tenses): perfect (complete) and imperfect (incomplete)
- Verb position: Hebrew often places the verb first (verb–subject–object order)
- Note: this section is a roadmap, not a full treatment — details unfold chapter by chapter

### Section 2 — Function (BBH §X.Y)
- Explain what this conjugation expresses (aspect, mood, mode)
- Use a **two-column table**: `Use | Description + Example`
- Include all major uses from BBH, plus any significant uses BBH notes as less common
- Close with a `> **Key diagnostic:**` callout

**Per-conjugation usage table guidance:**

| Conjugation | Uses to cover |
|---|---|
| Perfect | Simple past · Perfect of experience · Stative present · Prophetic perfect |
| Imperfect | Simple future · Habitual/repeated · Jussive/modal · Negation with אַל |
| Imperative | Direct command (2nd person only) · Cohortative relation |
| Inf. Construct | Purpose (לְ) · Temporal (בְּ/כְּ/אַחֲרֵי) · Object complement |
| Inf. Absolute | Emphatic assertion (doubled with finite verb) · Adverbial |
| Participle | Ongoing/continuous · Predicate nominative · Attributive adj. |

### Section 3 — Form: Diagnostic Markers
Bullet list, one bullet per diagnostic feature of this conjugation. Cover:
- Presence/absence of prefix or suffix
- Characteristic vowel pattern (the "theme vowel" under R2 or R3)
- Accent position (penult vs. ultima)
- How to distinguish from visually similar conjugations (e.g. Perfect 3ms ≠ Participle ms)

### Section 4 — Paradigm Table
Reference the full paradigm file with a short intro sentence, then embed a **summary table**:

| Person/Number/Gender | Form | Ending | Key vowel |
|---|---|---|---|
| (all 9 PGN cells for Perfect and Imperfect; fewer for Imperative, none for Inf/Participle) |

Link: `→ Full paradigm with stative comparison: [qal-<conjugation>-paradigm.md](...)`

### Section 5 — Stative vs. Fientive Verbs
*(Perfect and Imperfect only; omit for Imperative, Infinitives, Participle.)*
- Fientive verbs: describe an action or event → type-A/type-B theme vowel
- Stative verbs: describe a state or quality → type-B or type-C theme vowel
- Table showing 3ms form for all three vowel types side by side (קָטַל / כָּבֵד / קָטֹן)
- Common stative roots: כָּבֵד (heavy), גָּדֹל (great/big), קָטֹן (small), מָלֵא (full), יָרֵא (afraid)
- Note: stative roots cannot usually take the Hiphil causative; they take Hiphil only with
  factitive force (e.g. Hiphil of כָּבֵד = "to glorify/make heavy")

### Section 6 — Most Common Lemmas (Torah)
- Source: MACULA corpus, Genesis–Deuteronomy
- Filter to this conjugation (e.g., `tense == 'qatal'` for Perfect)
- Table: **Lemma | Hebrew | Torah (×) | Gloss | Notes**
- Minimum 15 rows, sorted by frequency descending
- Closing callout noting any pedagogically important roots in this conjugation

### Section 7 — Example Passages
One or two examples per usage type (as listed in §2).

- One `###` subsection per usage type, in the same order as §2
- Each subsection preceded by a `---` horizontal rule
- Prefer Torah (Gen → Exo → Lev → Num → Deu); fall back to Psalms/Proverbs, then any OT
- Format per entry:
  ```
  **Ref** — Hebrew text
  *"English translation."*
  → Root Qal+conjugation+PGN; one sentence grammatical/contextual note.
  ```
- Mark off-Torah examples: `*(Fall back: Torah has no clean example of this use.)*`

### Section 8 — Conjugation Distribution (OT-wide)
- Table: **Conjugation | Count | % of all Qal**
- Show all major Qal conjugation forms; highlight the one being taught
- Footer: `*Total OT Qal tokens: ~50,179.*`
- Closing callout with the most pedagogically notable pattern

---

## Paradigm File: `qal-<conjugation>-paradigm.md`

**File header:**
```
# Qal <Conjugation> Paradigm

*Full inflection tables for the Qal <conjugation> — strong (קָטַל) root.*
*All attested forms drawn from MACULA Hebrew WLC unless marked †.*
```

### For Perfect and Imperfect (fully inflected):
One table per vowel type (fientive A-class, stative e-class, stative o-class).

**Each table:** `Person | Fientive (קָטַל) | Stative-e (כָּבֵד) | Stative-o (גָּדֹל)`
- Bold the Stative columns only when contrasting with fientive
- Suffix column on the far right (for Perfect)
- Prefix column on the far left (for Imperfect)
- `> **Key:**` callout below each table naming the single most important recognition marker

### For Imperative:
- Short table: only 2ms, 2fs, 2mp, 2fp forms
- Relation to imperfect noted: imperative = imperfect minus prefix

### For Infinitive Construct and Absolute:
- Single row: one form each, plus variant with לְ prefix (for inf. construct)
- Note: inf. construct with לְ = purpose; with בְּ/כְּ = temporal

### For Participle:
- Table: ms, fs, mp, fp forms for both active (Qal active ptc.) and passive (Qal passive ptc.)
- Note the ambiguity between Qal passive participle and some Perfect forms

**Summary table at end:** `Conjugation | Marker (prefix/suffix) | Theme vowel | Quick ID`

---

## Exercises

### Passage Exercise (`ch<N>-passage-exercise`)
- 12–20 Qal verbs from 2–3 Torah passages, all in the conjugation being taught
- Prefer continuous narrative passages (not word lists)
- Students parse: PGN, root, and identify the usage type from §2
- Answer key on a separate section; include a brief grammatical note for each form
- Exercise README: description, coverage table (usage type × count), files table

### Parsing Drill (`ch<N>-parsing-drill`)
*(Replaces function-sort from derived-stem chapters.)*
- 20–30 pointed Hebrew forms, all in the conjugation being taught
- Mix: about half regular forms, half with vowel reductions or accent shifts
- Student writes: (a) conjugation (already given), (b) person, (c) number, (d) gender, (e) root
- Organize: Part A (10–12 forms with clear suffix/prefix patterns), Part B (10–15 forms with
  vowel reduction making parsing harder), Part C for Perfect: 5 forms that are stative (student
  must identify as stative and give the 3ms dictionary form)
- Exercise README: description, coverage table, files table

---

## Flashcard Decks

### Morphology Deck
- 20–30 cards: one card per PGN form for 2–3 high-frequency roots
- Roots should be from §6 (most common Torah lemmas)
- **Front:** pointed Hebrew form + reference
- **Back:** root + conjugation + PGN + gloss + one-line parsing note
- Anki tags: `bbh::ch<N>`, `qal::<conjugation>`, `pgn::<person>-<number>-<gender>`
- Include a summary table at the bottom of the `.md` file

### Vocabulary Deck
*(To be populated by the user with the actual BBH chapter vocabulary list.)*
- **Front:** Hebrew lemma
- **Back:** gloss + POS + total OT occurrences + one Torah reference
- Anki tags: `bbh::ch<N>::vocab`

---

## Formatting Conventions (inherited from `learning-new-stem.md`, adapted)

- **Section 7 (Example Passages):** Every `###` usage-type subsection must be preceded by `---`.
- **Bidi/verse ranges:** Never place a verse range (e.g. `Gen 3:16`) and Hebrew text on the
  same line. Put the reference on the previous bold line; Hebrew on its own line below.
- **Paradigm tables:** Bold the "unique to this conjugation" column header and cells only when
  making a contrast (e.g., comparing fientive vs. stative). Do not bold routine paradigm cells.
- **BBH section references:** Mark uncertain section numbers with *(verify §X.Y)*. Do not guess.
- **Stative note placement:** Always in Section 5, never embedded in Section 3 or 4.
- **Commit message convention:** `Add BBH Ch<N> lesson: Qal <Conjugation> Strong Verbs`
