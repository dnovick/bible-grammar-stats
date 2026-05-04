# Plan: Learning a Qal Conjugation — Weak Verbs

*Template for a chapter that extends a Qal conjugation to its weak-root patterns.*
*Covers: BBH Ch14 (Qal Perfect Weak), Ch16 (Qal Imperfect Weak).*
*Pattern modeled on BBH Ch25 (Niphal Weak) and Ch27 (Hiphil Weak), adapted for the Qal.*

---

## Purpose

This plan describes the complete file set for a chapter that extends a Qal conjugation
already introduced in the preceding strong-verb chapter (Ch13 or Ch15) to its weak-root
patterns. The strong form (aspect/mode function, full paradigm, vocabulary frequency) was
covered in the preceding chapter; this lesson focuses exclusively on the eight weak classes
and how they modify the strong paradigm.

---

## Weak Classes Covered

| Class | Label | Representative roots |
|---|---|---|
| III-א (Lamed-Aleph) | `lamed-aleph` | מָצָא, קָרָא |
| III-ה (Lamed-He) | `lamed-he` | עָשָׂה, רָאָה |
| III-ח/ע (Lamed-Guttural) | `lamed-guttural` | שָׁלַח, שָׁמַע |
| I-guttural (Pe-Guttural) | `pe-guttural` | עָמַד, אָמַר |
| I-נ (Pe-Nun) | `pe-nun` | נָפַל, נָתַן |
| I-י (Pe-Yod) | `pe-yod` | יָלַד, יָדַע |
| Biconsonantal (II-י/ו) | `biconsonantal` | קוּם, שׁוּב |
| Geminate (Ayin-Doubled, II=III) | `geminate` | סָבַב, תָּמַם |

> **Scope note:** BBH Ch14 (Qal Perfect Weak) covers all eight classes.
> BBH Ch16 (Qal Imperfect Weak) covers all eight classes and also introduces
> the short imperfect (jussive) and wayyiqtol. Document any omissions from BBH
> in the lesson file's scope callout.

---

## Directory Layout

```
output/lessons/<language>/<textbook>/ch<N>/
  README.md                                          # Chapter index
  ch<N>-qal-<conjugation>-weak.md                   # Main lesson file
  qal-<conjugation>-paradigm.md                     # LINK ONLY — from strong chapter; do not recreate
  qal-<conjugation>-weak-lamed-aleph-paradigms.md
  qal-<conjugation>-weak-lamed-he-paradigms.md
  qal-<conjugation>-weak-lamed-guttural-paradigms.md
  qal-<conjugation>-weak-pe-guttural-paradigms.md
  qal-<conjugation>-weak-pe-paradigms.md            # I-נ and I-י combined
  qal-<conjugation>-weak-biconsonantal-paradigms.md
  qal-<conjugation>-weak-geminate-paradigms.md
  ch<N>-morphology-deck.md
  ch<N>-morphology-deck.txt
  ch<N>-vocab-deck.md
  ch<N>-vocab-deck.txt
  exercises/
    README.md
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

> **File format rule:** Every exercise must exist in `.md`, `.html`, and `.pdf`.

> **Conjugation slug table:**
> | BBH chapter | Conjugation | Slug |
> |---|---|---|
> | Ch14 | Perfect (Qatal) | `perfect` |
> | Ch16 | Imperfect (Yiqtol) | `imperfect` |

---

## README.md (Chapter Index)

Same four-section structure as `learning-qal-strong-conjugation.md`, but the
**Reference Files** section lists the strong paradigm file (link only, from prior chapter)
plus all seven weak paradigm files. Include only lines for classes actually covered.

---

## Main Lesson File: `ch<N>-qal-<conjugation>-weak.md`

### Header block
```
# Chapter <N> — Qal <Conjugation> Weak Verbs

*Basics of Biblical Hebrew, Pratico & Van Pelt*
*Builds on Ch<N-1> (Qal <Conjugation> Strong Verbs). Weak forms only.*

> **Scope:** This chapter extends the Qal <Conjugation> paradigm to eight weak-root classes.
> Each class modifies the strong pattern in a predictable, phonologically motivated way.
```

### Section 1 — Overview Table

One row per weak class. Columns:
**Class | Label | Representative roots | What changes in <Conjugation> | Affected cells**

Close with `> **Key principle:**` callout: all weak patterns derive from
phonological rules (quiescence, assimilation, compensatory lengthening, patach furtive);
none requires learning a new paradigm from scratch.

### Sections 2–9 — One section per weak class (same order as Overview Table)

For each class:
- **Pattern description:** One paragraph on what phonological rule applies for this class
  in this conjugation specifically.
- **Diagnostic markers:** Bulleted list of which PGN cells differ from the strong paradigm.
- **Paradigm summary table:** `Person/Cell | Strong (קָטַל) | <Class> (<root1>) | <Class> (<root2>)`
  — 3ms form and any other cells where the weak class is most visible.
  Full tables are in the paradigm file; this is a quick-reference view.
- **Link to full paradigm file.**
- **Key corpus examples:** 3–5 attested forms with references and one sentence each.

### High-Frequency Weak Lemmas section

Consolidated table of the most frequent OT Qal lemmas in this conjugation that belong to
a covered weak class. Columns: **Root | Class | Torah tokens | OT tokens | Gloss**.
Sort by Torah tokens descending; aim for 20–25 rows across all classes.
Source from MACULA corpus (tense == 'qatal' or 'yiqtol', stem == 'qal').

### Practice section

Table linking to both exercises and the morphology deck.

---

## Paradigm Files

Same structure as `learning-weak-stem.md` — one file per class, with I-נ + I-י combined.

### Key Qal-specific points per class:

**III-א (Lamed-Aleph):**
- Perfect 3ms/3fs/3cp: the aleph quiesces (loses its consonantal value); final vowel lengthens
  (קָטַל → מָצָא with *tsere* becoming *qamets* in some forms)
- Inf. construct often identical to perfect 3ms (מָצֹא vs. מָצָא)
- Imperfect: aleph quiesces in final syllable; the preceding vowel often lengthens

**III-ה (Lamed-He):**
- The He is a "vowel letter" (mater lectionis) and quiesces in most forms
- Perfect 3ms ends in ָה-: e.g., עָשָׂה, גָּלָה
- Imperfect 3ms ends in -ֶה: e.g., יַעֲשֶׂה
- Short imperfect (jussive / wayyiqtol 3ms): drops the final He entirely (יַעַשׂ, יַרְא)
- Inf. construct: forms like עֲשׂוֹת, רְאוֹת (with final ות-)

**III-ח/ע (Lamed-Guttural):**
- Patach furtive (פַּתַח גְּנוּבָה) in word-final open syllables before guttural
- Short forms (wayyiqtol, jussive): tsere → patach before guttural (no furtive; syllable already closed)
- Perfect 3ms: שָׁלַח, שָׁמַע — the guttural takes chateph-patach where shewa is expected

**I-guttural (Pe-Guttural):**
- Cannot take dagesh-forte (no doubling); compensatory lengthening of preceding vowel
- Imperfect prefixes: chateph-patach under guttural where vocal shewa expected
  (אֶ prefix: יַ → יַאֲ; but some take patach: יַעַמְד)
- Inf. construct: often with patach (עֲמֹד vs. regular קְטֹל)
- The aleph (א) gutturals: silent aleph quiesces in some forms

**I-נ (Pe-Nun):**
- Nun assimilates into the following consonant by dagesh-forte
- Perfect: no assimilation (נָפַל, נָתַן — nun is fully pronounced)
- Imperfect 3ms: nun assimilates → יִפֹּל, יִתֵּן (dagesh forte in R2)
- Wayyiqtol: same dagesh pattern (וַיִּפֹּל, וַיִּתֵּן)
- Imperative: no prefix → assimilation reveals itself: פְּל, תֵּן

**I-י (Pe-Yod):**
- Original yod contracts with the imperfect prefix vowel
- Most I-י verbs in Qal imperfect: prefix vowel shifts, yod drops
- Perfect: yod is fully pronounced (יָלַד, יָדַע)
- Imperfect: the yod quiesces — יֵלֵד, יֵדַע (Hireq-Yod pattern: יֵ prefix)
- Some I-י verbs follow a "hollow" pattern (יָשַׁב → יֵשֵׁב)
- Wayyiqtol: וַיֵּ pattern

**Biconsonantal (II-י/ו):**
- The middle root letter is a vocalic yod or vav (not a true consonant in many forms)
- Perfect 3ms: with qamets — e.g., קָם, בָּא, שָׁב
- Imperfect 3ms: with qamets under prefix — e.g., יָקוּם, יָבוֹא, יָשׁוּב
- Wayyiqtol 3ms: וַיָּ pattern (qamets under waw–prefix doubled consonant)
- Inf. construct: קוּם, בּוֹא, שׁוּב (same as 3ms imperfect consonants)
- Perfect 3ms = Participle ms (identical forms — context required)

**Geminate (Ayin-Doubled):**
- R2 = R3; the doubled consonant takes dagesh forte
- Perfect 3ms: strong vowel pattern, R2 doubled — סָבַב, תָּמַם
- Imperfect 3ms: יָסֹב, יִתְמַם (dagesh forte + holem/patach)
- Wayyiqtol: וַיָּ prefix
- **Critical note:** Geminate Qal perfect 3ms is visually very close to Biconsonantal;
  root knowledge is the only reliable distinguisher
- Full comparison table with Biconsonantal required in the Geminate paradigm file

---

## Exercises

### Passage Exercise (`ch<N>-passage-exercise`)
Same format as strong-verb passage exercise plus:
- An added **Weak Class** column: student identifies which of the eight classes applies
- Choose passages with a mix of weak classes; aim for at least four classes represented
- Cover both strong and weak roots (weak forms are the emphasis, but strong forms
  provide realistic context)

### Weak-Form Identification Drill (`ch<N>-weak-form-id`)
- 40–50 pointed Hebrew forms, all in the conjugation being taught (e.g., all Qal Perfect)
- **Part A — By Class (5 groups of 7–8):** student identifies conjugation + parses root for
  forms from a single class at a time
- **Part B — Mixed (10–15 items):** any class, student identifies class first
- Answer key includes: weak class, PGN, root, and a one-line explanation of the diagnostic
- 5–6 discussion questions comparing confusable pairs:
  - Required: III-א perfect vs. participle · Biconsonantal perfect vs. participle
    · I-נ assimilation vs. I-guttural compensatory lengthening
    · **Geminate vs. Biconsonantal (required when both covered)**

---

## Flashcard Decks

### Morphology Deck
- 5 cards per weak class × key conjugation cells (target: 30–40 total)
- 1–2 representative roots per class; prioritize cells where weak behavior is most visible
- **Front:** pointed Hebrew form + short reference
- **Back:** root + weak class + PGN + gloss + one-line marker note
- Anki tags: `bbh::ch<N>`, `qal::<conjugation>`, `weak::<class-slug>`

### Vocabulary Deck
*(To be populated by the user with the actual BBH chapter vocabulary list.)*
- Same format as strong-verb plan

---

## Formatting Conventions

All conventions from `learning-qal-strong-conjugation.md` and `learning-weak-stem.md` apply:

- Every `##` paradigm section in a weak-paradigm file must be preceded by `---`
- Combined I-נ + I-י file: use double `---` between Part 1 and Part 2
- Unattested theoretical forms: mark with `†`
- Geminate paradigm file must include a Biconsonantal comparison table
- **Commit message convention:** `Add BBH Ch<N> lesson: Qal <Conjugation> Weak Verbs`
