# Vocabulary Anki Deck Builder

Build Anki-ready vocabulary flashcard decks for a BBH (or other textbook) chapter from a
user-provided word list. Generates both a human-readable `.md` card list and a
tab-separated `.txt` import file with POS tags.

**Usage:** `/vocab <language> <textbook> <chapter>`

Then paste the vocabulary list when prompted (or include it in the same message).

- `language` — `hebrew`, `greek`, or `aramaic`
- `textbook` — textbook abbreviation: `bbh`, `mounce`, etc.
- `chapter` — chapter number, e.g. `25`

**Output paths:**
- `output/lessons/<language>/<textbook>/ch<N>/ch<N>-vocab-deck.md` — human-readable card list
- `output/lessons/<language>/<textbook>/ch<N>/ch<N>-vocab-deck.txt` — Anki import file
- Update `output/lessons/<language>/<textbook>/ch<N>/README.md` to link both files

**Examples:**
- `/vocab hebrew bbh 25` — then paste Ch25 word list
- `/vocab hebrew bbh 26` — then paste Ch26 word list

---

## Input format expected

The user will paste a vocabulary list in one of these formats:

```
Verbs
    הָפַךְ    (Q) to turn, overturn; (Ni) be destroyed (95)
    חָרָה    (Q) to burn with anger (93)
Nouns
    זָכָר    male, man (82)
Other / Adjectives
    טָהוֹר   (adj) clean, pure (96)
```

Parse:
- **Section headers** (Verbs / Nouns / Adjectives / Other / Adverbs / Particles / Prepositions) → POS tag
- **Hebrew form** — the pointed lemma
- **Stem list** in parentheses before the gloss — e.g. `(Q)`, `(Pi)`, `(Ni)`, `(Q/Pi)`, etc.
- **Gloss** — the English definition
- **Frequency** in parentheses at the end — e.g. `(95)`
- **Plural/alternate forms** — any note after `;` or in a separate parenthetical, e.g. `mp נְהָרוֹת`
- **Special phrases** — e.g. `מִצְוֹת יְהוָה "the commandments of the LORD"`

---

## Card format

### `.md` file

```markdown
# Chapter N — Vocabulary Flashcard Deck

*X words from BBH Chapter N. Frequency counts are OT-wide occurrences.*
*Import `chN-vocab-deck.txt` directly into Anki (File → Import).*

## Card List

| # | Front — Hebrew Form | POS | Gloss | Stems | Freq |
|---|---|---|---|---|---|
| 1 | הָפַךְ | verb | to turn, overturn, overthrow, destroy | Q / Ni | 95 |
...

## Tags for Import
| Tag | Cards |
|---|---|
| `bbh-chN-vocab` | all |
| `bbh-chN-verb` | 1–6 |
| `bbh-chN-noun` | 7–12 |
| `bbh-chN-adj` | 13–15 |
```

### `.txt` import file

```
#separator:tab
#html:false
#notetype:Basic
#deck:BBH Chapter N — Vocabulary
#tags column:3
הָפַךְ<TAB>verb — (Q) to turn, overturn, destroy; (Ni) be destroyed — 95×<TAB>bbh-chN-vocab bbh-chN-verb
```

---

## POS tags

| Section header | Tag suffix |
|---|---|
| Verbs | `bbh-chN-verb` |
| Nouns | `bbh-chN-noun` |
| Adjectives / Other (adj) | `bbh-chN-adj` |
| Adverbs / Other (adv) | `bbh-chN-adv` |
| Particles / Prepositions | `bbh-chN-particle` |

Always add `bbh-chN-vocab` as the first tag (covers all cards in the chapter).

---

## Cross-chapter notes

If a word also appears in an earlier chapter with a **different grammatical role** (e.g. שִׁיר
as noun in Ch25 and verb in Ch26), add a bracket note on the card back:
`[cf. Ch25: שִׁיר noun "song" 78×]`

---

## README update

Add two rows to the chapter README table (after the morphology Anki deck rows):

```markdown
| [chN-vocab-deck.md](chN-vocab-deck.md) | Vocabulary flashcard list — X words (breakdown by POS) with tags and frequency |
| [chN-vocab-deck.txt](chN-vocab-deck.txt) | Vocabulary Anki import file — tab-separated, ready for File → Import |
```

If no README exists for the chapter yet, create one following the standard README structure
defined in the `/lesson` skill.

---

## After generating files

1. Confirm card count and POS breakdown with the user.
2. Note any cross-chapter word overlaps.
3. Offer to commit and push.
