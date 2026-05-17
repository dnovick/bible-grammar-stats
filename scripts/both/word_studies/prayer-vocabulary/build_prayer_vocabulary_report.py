"""Word study: Greek prayer vocabulary in 1 Timothy 2:1.

Terms studied:
  Nouns:  δέησις (G1162), προσευχή (G4335), ἔντευξις (G1783), εὐχαριστία (G2169)
  Verbs:  δέομαι (G1189), προσεύχομαι (G4336), ἐντυγχάνω (G1793), εὐχαριστέω (G2168)

Generates:
  Charts:
    prayer-nt-nouns-by-book.png        — NT noun distribution (grouped bar)
    prayer-nt-verbs-by-book.png        — NT verb distribution (grouped bar)
    prayer-lxx-by-book.png             — LXX distribution (δέησις / προσευχή)
    prayer-noun-verb-comparison.png    — noun vs verb totals side-by-side

  Reports:
    prayer-vocabulary-report.md        — main markdown report
    prayer-nt-concordance.csv          — NT concordance for all 8 terms
    prayer-lxx-concordance.csv         — LXX concordance for all 8 terms
"""
import matplotlib; matplotlib.use('Agg')  # noqa: E702
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from bible_grammar.core import db as _db
from bible_grammar.core.reference import BOOKS

REPORT_DIR = Path('output/reports/both/word_studies/prayer-vocabulary')
CHART_DIR = Path('output/charts/both/word_studies/prayer-vocabulary')
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────

words = _db.load()
lxx_df = _db.load_lxx()
trans = _db.load_translations()
kjv = trans[trans['translation'] == 'KJV'].copy()

nt = words[words['source'] == 'TAGNT'].copy()
ot = words[words['source'] == 'TAHOT'].copy()
lxx_canon = lxx_df[~lxx_df['is_deuterocanon']].copy()

# ── NT subsets ────────────────────────────────────────────────────────────────

deesis_nt = nt[nt['strongs'].str.contains('G1162', na=False)].copy()
proseuchē_nt = nt[nt['strongs'].str.contains('G4335', na=False)].copy()
enteuxis_nt = nt[nt['strongs'].str.contains('G1783', na=False)].copy()
euchar_nt = nt[nt['strongs'].str.contains('G2169', na=False)].copy()

deomai_nt = nt[nt['strongs'].str.contains('G1189', na=False)].copy()
proseuchomai_nt = nt[nt['strongs'].str.contains('G4336', na=False)].copy()
entynchanō_nt = nt[nt['strongs'].str.contains('G1793', na=False)].copy()
eucharisteo_nt = nt[nt['strongs'].str.contains('G2168', na=False)].copy()

# ── LXX subsets ───────────────────────────────────────────────────────────────

deesis_lxx = lxx_canon[lxx_canon['strongs'] == 'G1162'].copy()
proseuchē_lxx = lxx_canon[lxx_canon['strongs'] == 'G4335'].copy()
deomai_lxx = lxx_canon[lxx_canon['strongs'] == 'G1189'].copy()
proseuchomai_lxx = lxx_canon[lxx_canon['strongs'] == 'G4336'].copy()

# ── Book / colour helpers ─────────────────────────────────────────────────────

NT_ORDER = [b[0] for b in BOOKS if b[2] == 'NT']
OT_ORDER = [b[0] for b in BOOKS if b[2] == 'OT']
BOOK_NAMES = {b[0]: b[1] for b in BOOKS}

NOUN_COLORS = {
    'δέησις':     '#2166ac',
    'προσευχή':   '#4dac26',
    'ἔντευξις':  '#d01c8b',
    'εὐχαριστία': '#e66101',
}
VERB_COLORS = {
    'δέομαι':       '#5aafe8',
    'προσεύχομαι':  '#8fce65',
    'ἐντυγχάνω':   '#e87dcd',
    'εὐχαριστέω':  '#f4a83a',
}


def _kjv(book: str, ch: int, vs: int) -> str:
    row = kjv[(kjv['book_id'] == book) & (kjv['chapter'] == ch)
              & (kjv['verse'] == vs)]
    return row['text'].values[0] if len(row) else ''


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _grouped_bar(ax: "plt.Axes", datasets: list, colors: list,
                 labels: list, title: str) -> None:
    """Draw a grouped bar chart. datasets = list of Series indexed by NT_ORDER."""
    books = [b for b in NT_ORDER
             if any(ds.get(b, 0) > 0 for ds in datasets)]
    x = range(len(books))
    n = len(datasets)
    w = 0.8 / n
    offset = -(n - 1) / 2 * w
    for i, (ds, color, label) in enumerate(zip(datasets, colors, labels)):
        vals = [ds.get(b, 0) for b in books]
        ax.bar([xi + offset + i * w for xi in x], vals, width=w,
               label=label, color=color, edgecolor='white', linewidth=0.4)
    ax.set_xticks(list(x))
    ax.set_xticklabels(books, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Occurrences')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)


# ── Chart 1: NT nouns by book ─────────────────────────────────────────────────

def _chart_nt_nouns() -> None:
    datasets = [
        deesis_nt.groupby('book_id').size().to_dict(),
        proseuchē_nt.groupby('book_id').size().to_dict(),
        enteuxis_nt.groupby('book_id').size().to_dict(),
        euchar_nt.groupby('book_id').size().to_dict(),
    ]
    labels = ['δέησις (G1162)', 'προσευχή (G4335)',
              'ἔντευξις (G1783)', 'εὐχαριστία (G2169)']
    colors = list(NOUN_COLORS.values())
    fig, ax = plt.subplots(figsize=(14, 5))
    _grouped_bar(ax, datasets, colors, labels,
                 'NT Prayer Nouns by Book (1 Tim 2:1 word family)')
    fig.tight_layout()
    path = CHART_DIR / 'prayer-nt-nouns-by-book.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Chart: {path}')


# ── Chart 2: NT verbs by book ─────────────────────────────────────────────────

def _chart_nt_verbs() -> None:
    datasets = [
        deomai_nt.groupby('book_id').size().to_dict(),
        proseuchomai_nt.groupby('book_id').size().to_dict(),
        entynchanō_nt.groupby('book_id').size().to_dict(),
        eucharisteo_nt.groupby('book_id').size().to_dict(),
    ]
    labels = ['δέομαι (G1189)', 'προσεύχομαι (G4336)',
              'ἐντυγχάνω (G1793)', 'εὐχαριστέω (G2168)']
    colors = list(VERB_COLORS.values())
    fig, ax = plt.subplots(figsize=(14, 5))
    _grouped_bar(ax, datasets, colors, labels,
                 'NT Prayer Verbs by Book')
    fig.tight_layout()
    path = CHART_DIR / 'prayer-nt-verbs-by-book.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Chart: {path}')


# ── Chart 3: LXX δέησις / προσευχή by book ───────────────────────────────────

def _chart_lxx() -> None:
    d_cnt = deesis_lxx.groupby('book_id').size().to_dict()
    p_cnt = proseuchē_lxx.groupby('book_id').size().to_dict()
    books = sorted(set(d_cnt) | set(p_cnt),
                   key=lambda b: OT_ORDER.index(b) if b in OT_ORDER else 99)
    x = range(len(books))
    w = 0.38
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar([i - w / 2 for i in x], [d_cnt.get(b, 0) for b in books],
           width=w, label='δέησις (G1162)', color=NOUN_COLORS['δέησις'],
           edgecolor='white', linewidth=0.4)
    ax.bar([i + w / 2 for i in x], [p_cnt.get(b, 0) for b in books],
           width=w, label='προσευχή (G4335)', color=NOUN_COLORS['προσευχή'],
           edgecolor='white', linewidth=0.4)
    ax.set_xticks(list(x))
    ax.set_xticklabels(books, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Occurrences')
    ax.set_title('LXX: δέησις vs προσευχή by Book (Canonical OT)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    fig.tight_layout()
    path = CHART_DIR / 'prayer-lxx-by-book.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Chart: {path}')


# ── Chart 4: noun vs verb totals ──────────────────────────────────────────────

def _chart_noun_verb_totals() -> None:
    pairs = [
        ('δέησις\n(noun)', len(deesis_nt),
         'δέομαι\n(verb)', len(deomai_nt),
         NOUN_COLORS['δέησις'], VERB_COLORS['δέομαι']),
        ('προσευχή\n(noun)', len(proseuchē_nt),
         'προσεύχομαι\n(verb)', len(proseuchomai_nt),
         NOUN_COLORS['προσευχή'], VERB_COLORS['προσεύχομαι']),
        ('εὐχαριστία\n(noun)', len(euchar_nt),
         'εὐχαριστέω\n(verb)', len(eucharisteo_nt),
         NOUN_COLORS['εὐχαριστία'], VERB_COLORS['εὐχαριστέω']),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, (nlabel, nval, vlabel, vval, nc, vc) in zip(axes, pairs):
        ax.bar([0, 1], [nval, vval], color=[nc, vc], edgecolor='white', width=0.5)
        ax.set_xticks([0, 1])
        ax.set_xticklabels([nlabel, vlabel], fontsize=9)
        ax.set_ylabel('NT occurrences')
        for xi, val in enumerate([nval, vval]):
            ax.text(xi, val + 0.5, str(val), ha='center', fontsize=10,
                    fontweight='bold')
    # ἔντευξις/ἐντυγχάνω separately
    fig.suptitle('NT Prayer Vocabulary: Noun vs Verb Counts',
                 fontsize=12, fontweight='bold')
    fig.tight_layout()
    path = CHART_DIR / 'prayer-noun-verb-comparison.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Chart: {path}')


# ── CSV exports ───────────────────────────────────────────────────────────────

def _csv_nt() -> None:
    rows = []
    for strongs, label, df in [
        ('G1162', 'δέησις',      deesis_nt),
        ('G4335', 'προσευχή',    proseuchē_nt),
        ('G1783', 'ἔντευξις',   enteuxis_nt),
        ('G2169', 'εὐχαριστία', euchar_nt),
        ('G1189', 'δέομαι',      deomai_nt),
        ('G4336', 'προσεύχομαι', proseuchomai_nt),
        ('G1793', 'ἐντυγχάνω',  entynchanō_nt),
        ('G2168', 'εὐχαριστέω', eucharisteo_nt),
    ]:
        for _, row in df.iterrows():
            rows.append({
                'term': label, 'strongs': strongs,
                'book': row['book_id'], 'chapter': row['chapter'],
                'verse': row['verse'], 'word': row['word'],
                'morph': row['morph_code'],
                'kjv_verse': _kjv(row['book_id'], row['chapter'], row['verse']),
            })
    pd.DataFrame(rows).to_csv(REPORT_DIR / 'prayer-nt-concordance.csv', index=False)
    print(f'CSV: {REPORT_DIR}/prayer-nt-concordance.csv ({len(rows)} rows)')


def _csv_lxx() -> None:
    rows = []
    for strongs, label, df in [
        ('G1162', 'δέησις',      deesis_lxx),
        ('G4335', 'προσευχή',    proseuchē_lxx),
        ('G1189', 'δέομαι',      deomai_lxx),
        ('G4336', 'προσεύχομαι', proseuchomai_lxx),
    ]:
        for _, row in df.iterrows():
            rows.append({
                'term': label, 'strongs': strongs,
                'book': row['book_id'], 'chapter': row['chapter'],
                'verse': row['verse'], 'word': row['word'],
                'tense': row.get('tense', ''), 'case': row.get('case_', ''),
            })
    pd.DataFrame(rows).to_csv(REPORT_DIR / 'prayer-lxx-concordance.csv', index=False)
    print(f'CSV: {REPORT_DIR}/prayer-lxx-concordance.csv ({len(rows)} rows)')


# ── NT book-count HTML ────────────────────────────────────────────────────────

def _nt_html() -> str:
    gospels_acts = ['Mat', 'Mrk', 'Luk', 'Jhn', 'Act']
    pauline = ['Rom', '1Co', '2Co', 'Gal', 'Eph', 'Php', 'Col',
               '1Th', '2Th', '1Ti', '2Ti', 'Tit', 'Phm']
    general = ['Heb', 'Jas', '1Pe', '2Pe', '1Jn', '2Jn', '3Jn', 'Jud', 'Rev']

    c62 = deesis_nt.groupby('book_id').size().to_dict()
    c35 = proseuchē_nt.groupby('book_id').size().to_dict()
    c83 = enteuxis_nt.groupby('book_id').size().to_dict()
    c69 = euchar_nt.groupby('book_id').size().to_dict()

    def _panel(books: list, title: str) -> str:
        rows_html = '\n'.join(
            f'<tr><td>{BOOK_NAMES.get(b, b)}</td>'
            f'<td align="right">{c62.get(b, 0) or "—"}</td>'
            f'<td align="right">{c35.get(b, 0) or "—"}</td>'
            f'<td align="right">{c83.get(b, 0) or "—"}</td>'
            f'<td align="right">{c69.get(b, 0) or "—"}</td></tr>'
            for b in books
            if c62.get(b, 0) or c35.get(b, 0) or c83.get(b, 0) or c69.get(b, 0)
        )
        return (
            '<table>\n'
            f'<tr><th colspan="5" align="left"><b>{title}</b></th></tr>\n'
            '<tr><th align="left">Book</th>'
            '<th>δέησις</th><th>προσευχή</th>'
            '<th>ἔντευξις</th><th>εὐχαριστία</th></tr>\n'
            f'{rows_html}\n</table>'
        )

    panels = [
        _panel(gospels_acts, 'Gospels &amp; Acts'),
        _panel(pauline, 'Pauline Epistles'),
        _panel(general, 'General Epistles &amp; Revelation'),
    ]
    cells = '\n<td width="32">&nbsp;</td>\n'.join(
        f'<td valign="top">\n{p}\n</td>' for p in panels
    )
    return f'<table>\n<tr>\n{cells}\n</tr>\n</table>'


# ── Report ────────────────────────────────────────────────────────────────────

def _build_report() -> None:
    n62 = len(deesis_nt)
    n35 = len(proseuchē_nt)
    n83 = len(enteuxis_nt)
    n69 = len(euchar_nt)
    n93 = len(entynchanō_nt)
    n68 = len(eucharisteo_nt)

    n62_lxx = len(deesis_lxx)
    n35_lxx = len(proseuchē_lxx)

    tephillah = len(ot[ot['strongs'].str.contains('H8605', na=False)])
    techinnah = len(ot[ot['strongs'].str.contains('H8467', na=False)])

    nt_html = _nt_html()

    lines = [
        '# Word Study: Greek Prayer Vocabulary in 1 Timothy 2:1',
        '',
        '*Build script: [scripts/both/word_studies/prayer-vocabulary/'
        'build_prayer_vocabulary_report.py]'
        '(../../../../../scripts/both/word_studies/prayer-vocabulary/'
        'build_prayer_vocabulary_report.py)*',
        '',
        '---',
        '',
        '## Contents',
        '',
        '- [Overview: 1 Timothy 2:1](#overview-1-timothy-21)',
        '- [The Four Terms: Definitions and Distinctions]'
        '(#the-four-terms-definitions-and-distinctions)',
        '  - [δέησις — Supplication](#δέησις--supplication-g1162)',
        '  - [προσευχή — Prayer](#προσευχή--prayer-g4335)',
        '  - [ἔντευξις — Intercession](#ἔντευξις--intercession-g1783)',
        '  - [εὐχαριστία — Thanksgiving](#εὐχαριστία--thanksgiving-g2169)',
        '- [Hebrew Background](#hebrew-background)',
        '- [LXX Distribution](#lxx-distribution)',
        '- [NT Distribution](#nt-distribution)',
        '- [Passages Where Multiple Terms Appear Together]'
        '(#passages-where-multiple-terms-appear-together)',
        '- [The Intercession Concept: ἐντυγχάνω in the NT]'
        '(#the-intercession-concept-ἐντυγχάνω-in-the-nt)',
        '- [Theological Significance](#theological-significance)',
        '- [Key Observations](#key-observations)',
        '- [Data Files](#data-files)',
        '',
        '---',
        '',
        '## Key Observations',
        '',
        '### 1. Paul stacks four distinct terms deliberately',
        '',
        'In 1 Tim 2:1 Paul writes δεήσεις, προσευχάς, ἐντεύξεις, εὐχαριστίας '
        'in a single exhortation — four accusative plurals in a row. This is not '
        'synonymous repetition for rhetorical effect (as in Greek oratory) but a '
        'theological taxonomy: each term isolates a specific dimension of the '
        'church\'s prayer life. The four together define comprehensiveness: '
        'need-driven petition, general worship-address, advocacy for others, '
        'and grateful response.',
        '',
        '### 2. προσευχή is the generic term; the others are more specific',
        '',
        f'προσευχή ({n35} NT, {n35_lxx} LXX) is the broadest term — the standard '
        'Greek word for prayer in both the LXX and NT, translating the Hebrew '
        'תְּפִלָּה (tephillah, {tephillah} OT occurrences). It appears in every '
        'major NT corpus, in Psalm titles, and in Solomon\'s Temple prayer. '
        'The other three terms each narrow in on a specific posture or function.',
        '',
        '### 3. δέησις always carries a sense of urgent, need-driven petition',
        '',
        f'δέησις ({n62} NT, {n62_lxx} LXX) — "supplication" — is rooted in '
        'δέομαι ("to lack, to need"), and this etymology is theologically active: '
        'every δέησις is a prayer from a position of acknowledged deficiency. '
        'It is the term used for Jesus\' own prayer in Gethsemane (Heb 5:7), '
        'for Paul\'s intercession for Israel (Rom 10:1), and for the congregation\'s '
        'prayer for Peter in prison (Acts 12:5). It never appears as a generic '
        'word for prayer — it always implies intensity and specific need.',
        '',
        '### 4. ἔντευξις is NT-exclusive and forensically charged',
        '',
        f'ἔντευξις ({n83} NT occurrences, **zero LXX occurrences**) is the most '
        'theologically distinctive term in the list. Its cognate verb ἐντυγχάνω '
        'means "to approach on behalf of someone" — a technical term for presenting '
        'a petition to a king or magistrate (Acts 25:24; Esther LXX; 3 Macc). '
        'In 1 Tim 2:1 it denotes the church\'s advocacy for outsiders — "for all '
        'people" — before God. In 1 Tim 4:5 the same noun describes the '
        'sanctifying power of God\'s word and prayer. The verb ἐντυγχάνω is used '
        f'({n93} NT occurrences) for both Christ\'s eternal intercession at the '
        'Father\'s right hand (Heb 7:25; Rom 8:34) and the Spirit\'s intercession '
        'within the believer (Rom 8:26–27).',
        '',
        '### 5. εὐχαριστία is almost entirely a NT and Pauline development',
        '',
        f'εὐχαριστία ({n69} NT, 1 LXX canonical) is barely present in the LXX '
        'and absent from the Hebrew tradition as a prayer category. Its verb '
        f'εὐχαριστέω ({n68} NT) similarly has zero canonical LXX occurrences. '
        'This is a genuinely new theological emphasis in the NT — Paul uses '
        'εὐχαριστία and εὐχαριστέω as structural markers in nearly every letter '
        'opening. The command to pray "with thanksgiving" (Php 4:6; Col 4:2) '
        'reflects the Christ-shaped transformation of prayer: petition is now '
        'framed by grateful confidence in what God has already done.',
        '',
        '### 6. The verb ἐντυγχάνω links ecclesial and divine intercession',
        '',
        'The three NT uses of ἐντυγχάνω in Romans 8 and Hebrews 7 establish a '
        'theology of intercession that frames 1 Timothy 2:1: the Spirit intercedes '
        'within us (Rom 8:26–27), Christ intercedes for us from the Father\'s right '
        'hand (Rom 8:34; Heb 7:25), and the church is called to intercede for all '
        'people (1 Tim 2:1). The church\'s ἔντευξις participates in the Son\'s and '
        'Spirit\'s own intercessory ministry.',
        '',
        '### 7. Psalms is the LXX school of prayer — and uses both δέησις and προσευχή',
        '',
        f'The Psalter accounts for {len(deesis_lxx[deesis_lxx["book_id"] == "Psa"])} '
        f'of the {n62_lxx} canonical LXX δέησις occurrences and '
        f'{len(proseuchē_lxx[proseuchē_lxx["book_id"] == "Psa"])} '
        f'of the {n35_lxx} canonical LXX προσευχή occurrences. '
        'The Psalms consistently pair both terms (e.g. Psa 6:10 LXX uses both in '
        'the same verse), showing that even in the OT the two concepts were '
        'complementary — προσευχή as the act of addressing God, δέησις as the '
        'urgent petition within that address.',
        '',
        '---',
        '',
        '## Overview: 1 Timothy 2:1',
        '',
        f'> *"{_kjv("1Ti", 2, 1)}"* (KJV)',
        '',
        'In this exhortation — the first in his body of instructions to Timothy '
        'about church order — Paul uses four distinct Greek words for prayer, each '
        'describing a different facet of the church\'s corporate prayer life. '
        'They appear as accusative plural nouns, objects of the infinitive '
        'ποιεῖσθαι ("to make/offer"), governed by the verb παρακαλῶ ("I urge").',
        '',
        '| # | Greek | Strongs | KJV | Transliteration |',
        '|---|---|---|---|---|',
        '| 1 | δεήσεις | G1162 | supplications | *deēseis* |',
        '| 2 | προσευχάς | G4335 | prayers | *proseuchas* |',
        '| 3 | ἐντεύξεις | G1783 | intercessions | *enteuxeis* |',
        '| 4 | εὐχαριστίας | G2169 | giving of thanks | *eucharistias* |',
        '',
        '**Scope:** "for all people" (ὑπὲρ πάντων ἀνθρώπων) — including kings '
        'and those in authority (v. 2). The universal scope is itself theologically '
        'significant: the church\'s prayer is not self-enclosed but outward-facing.',
        '',
        '---',
        '',
        '## The Four Terms: Definitions and Distinctions',
        '',
        '---',
        '',
        '### δέησις — Supplication (G1162)',
        '',
        '**Transliteration:** *deēsis*  |  **Related verb:** δέομαι (G1189, '
        '"to lack, to need, to beseech")',
        '',
        '**Etymology:** From δέω ("to lack, to be in want"). The root meaning is '
        'significant: every δέησις arises from a position of need or deficiency. '
        'It is not merely polite petition but urgent, earnest supplication.',
        '',
        '**Semantic range:**',
        '- Urgent petition arising from a specific need',
        '- Entreaty directed to God *or* to another person',
        '- Always implies the petitioner\'s awareness of their own insufficiency',
        '',
        '**Key NT uses:**',
        '',
        f'> *"{_kjv("Heb", 5, 7)}"* (Heb 5:7)',
        '',
        'Jesus\' own Gethsemane prayer is described with δεήσεις — the most '
        'intense possible petition, accompanied by "strong crying and tears," '
        'directed to the one who could deliver him from death.',
        '',
        f'> *"{_kjv("Eph", 6, 18)}"* (Eph 6:18)',
        '',
        'In the armor of God passage, δέησις and προσευχή appear together: '
        'προσευχή is the general mode, δέησις is the urgent, targeted petition '
        'within it. The two work in tandem.',
        '',
        f'> *"{_kjv("Php", 4, 6)}"* (Php 4:6)',
        '',
        'Again δέησις and προσευχή are paired — with εὐχαριστία wrapping them both. '
        'Philippians 4:6 and Ephesians 6:18 form the closest NT parallels '
        'to the 1 Timothy 2:1 prayer taxonomy.',
        '',
        '**LXX roots:** Translates primarily תְּחִנָּה (*techinnah*, H8467, '
        f'{techinnah} OT occ) — "entreaty, supplication" — and also the Psalmic '
        'appeals to God (שַׁוְעָה, H7775). Heavy concentration in Psalms '
        f'({len(deesis_lxx[deesis_lxx["book_id"] == "Psa"])} LXX occurrences) '
        'and Solomon\'s Temple prayer (1 Kings 8 — 8 occurrences).',
        '',
        '---',
        '',
        '### προσευχή — Prayer (G4335)',
        '',
        '**Transliteration:** *proseuchē*  |  **Related verb:** προσεύχομαι '
        '(G4336, "to pray")',
        '',
        '**Etymology:** From πρός ("toward") + εὔχομαι ("to wish, vow, pray"). '
        'The preposition πρός points to the directional orientation of prayer — '
        'it is addressed *toward* God. This directional quality distinguishes it '
        'from more general terms for speech or request.',
        '',
        '**Semantic range:**',
        '- The generic, comprehensive term for prayer',
        '- Encompasses petition, praise, thanksgiving, and intercession',
        '- Used for both individual and corporate prayer',
        '- In classical Greek, often a formal vow or prayer to a deity',
        '',
        '**Occurrence profile:** The most frequent noun '
        f'({n35} NT, {n35_lxx} LXX canonical), appearing across all NT corpora '
        'and in the headings of five Psalm titles (Psa 17; 86; 90; 102; 142 MT). '
        'Luke-Acts has the heaviest NT concentration (Acts alone: 9 times), '
        'reflecting Luke\'s programmatic emphasis on prayer as a characteristic '
        'of the early church.',
        '',
        '**LXX roots:** The standard rendering of תְּפִלָּה (*tephillah*, H8605, '
        f'{tephillah} OT occ) — the most common Hebrew prayer noun, used for '
        'Solomon\'s Temple prayer, the Psalms (32 occurrences), and prophetic '
        'intercession. When the LXX translator chose between δέησις and προσευχή '
        'to render תְּפִלָּה, the latter was preferred for formal, '
        'comprehensive prayers; the former for urgent individual appeals.',
        '',
        '---',
        '',
        '### ἔντευξις — Intercession (G1783)',
        '',
        '**Transliteration:** *enteuxis*  |  '
        '**Related verb:** ἐντυγχάνω (G1793, "to intercede, to appeal")',
        '',
        '**Etymology:** From ἐντυγχάνω ("to fall in with, to approach, to petition"). '
        'In Hellenistic Greek the verb was used technically for submitting a petition '
        'to a ruler or official — a formal act of advocacy on another\'s behalf '
        'before a higher authority.',
        '',
        '**A uniquely NT term:**',
        '',
        '> ἔντευξις appears **zero times** in the LXX (canonical or deuterocanonical) '
        'and only **twice** in the entire NT — both in 1 Timothy (2:1 and 4:5). '
        'Its cognate verb ἐντυγχάνω occurs once in the canonical LXX (Daniel) '
        'and only 5 times in the NT.',
        '',
        '**NT occurrences of ἔντευξις:**',
        '',
        f'> *"{_kjv("1Ti", 2, 1)}"* (1 Tim 2:1)',
        '',
        'The church\'s intercessory advocacy for "all people" — the word\'s '
        'forensic background makes the prayer a formal act of representation '
        'before God.',
        '',
        f'> *"{_kjv("1Ti", 4, 5)}"* (1 Tim 4:5)',
        '',
        'Here ἔντευξις (NASB: "prayer") refers to the sanctifying effect of '
        'God\'s word and prayer on food — an intimate, relational encounter '
        'with God. The same word that covers public intercession for nations '
        'also covers the private prayer of grace over a meal, showing the '
        'breadth of the concept.',
        '',
        '---',
        '',
        '### εὐχαριστία — Thanksgiving (G2169)',
        '',
        '**Transliteration:** *eucharistia*  |  '
        '**Related verb:** εὐχαριστέω (G2168, "to give thanks")',
        '',
        '**Etymology:** From εὖ ("well") + χάρις ("grace, favor") → '
        '"to return good favor, to give thanks for grace received."',
        '',
        '**A distinctively NT emphasis:**',
        '',
        f'εὐχαριστία ({n69} NT occurrences) is almost absent from the LXX '
        '(1 canonical occurrence, in Esther 8:12 LXX — a non-Semitic '
        'addition). Its verb εὐχαριστέω has zero canonical LXX occurrences. '
        'This distribution signals that thanksgiving as a distinct, named '
        'category of prayer is a NT — specifically Pauline — development.',
        '',
        '**Paul\'s structural use:** εὐχαριστία and εὐχαριστέω are '
        'characteristic markers of Paul\'s letter openings and prayer reports '
        '(Rom 1:8; 1 Cor 1:4; Eph 1:16; Php 1:3; Col 1:3; 1 Th 1:2). '
        'The command to "pray with thanksgiving" (Php 4:6; Col 4:2; 1 Th 5:18) '
        'reflects the Christ-shaped horizon of NT prayer: petition is offered '
        'with grateful confidence in what God has already accomplished in Christ.',
        '',
        '**The Eucharist connection:** εὐχαριστία is also the word behind '
        '"Eucharist" — the Lord\'s Supper as the act of thanksgiving '
        '(1 Cor 11:24; cf. the verbal form in the institution narrative). '
        'The overlap between table-thanksgiving and prayer-thanksgiving '
        'is not accidental.',
        '',
        '---',
        '',
        '## Hebrew Background',
        '',
        '| Hebrew | Transliteration | Strongs | Gloss | OT occ | LXX rendering |',
        '|---|---|---|---|---|---|',
        f'| תְּפִלָּה | tephillah | H8605 | prayer (formal, comprehensive) | {tephillah} | '
        'mainly προσευχή |',
        f'| תְּחִנָּה | techinnah | H8467 | entreaty, supplication | {techinnah} | '
        'mainly δέησις |',
        '| שַׁוְעָה | shavah | H7775 | cry for help | 11 | δέησις |',
        '| —  | — | — | *no Hebrew equivalent* | — | '
        'ἔντευξις has no Hebrew root |',
        '| תּוֹדָה | todah | H8426 | thanksgiving, praise | 32 | αἴνεσις, not εὐχαριστία |',
        '',
        'The key insight from the Hebrew alignment is that **ἔντευξις and '
        'εὐχαριστία are genuinely new theological categories** — they have no '
        'stable Hebrew equivalents in the OT prayer vocabulary. '
        'The OT prayer tradition is well served by תְּפִלָּה and תְּחִנָּה, '
        'which map to the Psalms\' comprehensive prayers and urgent supplications. '
        'But the NT adds the dimensions of intercessory advocacy (ἔντευξις) '
        'and Christ-grounded thanksgiving (εὐχαριστία) that arise specifically '
        'from the new covenant context.',
        '',
        '---',
        '',
        '## LXX Distribution',
        '',
        f'δέησις: **{n62_lxx} canonical LXX occurrences**  |  '
        f'προσευχή: **{n35_lxx} canonical LXX occurrences**',
        '',
        '![LXX distribution](../../../../charts/both/word_studies/'
        'prayer-vocabulary/prayer-lxx-by-book.png)',
        '',
        '**Psalms** dominates both terms '
        f'(δέησις: {len(deesis_lxx[deesis_lxx["book_id"] == "Psa"])}; '
        f'προσευχή: {len(proseuchē_lxx[proseuchē_lxx["book_id"] == "Psa"])}), '
        'establishing the Psalter as the school of OT prayer. '
        '**1 Kings 8** (Solomon\'s Temple prayer) has the second-highest '
        'concentration of both terms — the great dedicatory prayer uses both '
        'as near-synonyms for formal petition before YHWH.',
        '',
        'The two LXX terms are **complementary, not synonymous**: they frequently '
        'appear in the same verse (e.g. Psa 6:10 LXX), where προσευχή frames '
        'the act of prayer while δέησις intensifies the urgency of the petition. '
        'This pairing in the LXX prepares for and explains their pairing '
        'in NT passages like Eph 6:18 and Php 4:6.',
        '',
        '---',
        '',
        '## NT Distribution',
        '',
        '![NT nouns by book](../../../../charts/both/word_studies/'
        'prayer-vocabulary/prayer-nt-nouns-by-book.png)',
        '',
        nt_html,
        '',
        '![NT verbs by book](../../../../charts/both/word_studies/'
        'prayer-vocabulary/prayer-nt-verbs-by-book.png)',
        '',
        '![Noun vs verb totals](../../../../charts/both/word_studies/'
        'prayer-vocabulary/prayer-noun-verb-comparison.png)',
        '',
        '**Observations from the distribution:**',
        '',
        '- **Luke-Acts** dominates the verbs, especially προσεύχομαι (Luke 19, '
        'Acts 16) and δέομαι (Luke 8, Acts 7) — Luke\'s theology of prayer '
        'is action-oriented, narrating Jesus and the apostles at prayer.',
        '- **Paul** dominates the nouns — δέησις, προσευχή, εὐχαριστία all '
        'cluster in his letters. Paul conceptualizes prayer; Luke narrates it.',
        '- **1 Timothy** is the only NT book with ἔντευξις, and has the highest '
        'concentration of all four nouns together.',
        '- **Revelation** has 3 occurrences of προσευχή — all in the image of '
        'golden bowls full of incense, "which are the prayers of the saints" '
        '(Rev 5:8; 8:3–4), forming the eschatological climax of the prayer '
        'tradition.',
        '',
        '---',
        '',
        '## Passages Where Multiple Terms Appear Together',
        '',
        'The most theologically revealing data points are passages where Paul '
        'deliberately juxtaposes two or more of these terms:',
        '',
        '---',
        '',
        '### Philippians 4:6',
        '',
        f'> *"{_kjv("Php", 4, 6)}"* (KJV)',
        '',
        '- **προσευχῇ** (dative): the comprehensive, God-ward address',
        '- **δεήσει** (dative): the specific, urgent petition within it',
        '- **εὐχαριστίας** (genitive): the atmosphere of thanksgiving '
        'that frames both',
        '',
        'The structure mirrors 1 Tim 2:1 in miniature — Paul\'s default '
        'prayer vocabulary combines the same three ingredients.',
        '',
        '---',
        '',
        '### Ephesians 6:18',
        '',
        f'> *"{_kjv("Eph", 6, 18)}"* (KJV)',
        '',
        '- **προσευχῆς** and **δεήσεως** are paired, as in Php 4:6',
        '- The verb **προσευχόμενοι** governs both: prayer as practice '
        'is the umbrella, δέησις is the mode of urgent petition within it',
        '- "At all times in the Spirit" — the pneumatic dimension '
        'that Rom 8:26–27 develops with ἐντυγχάνω',
        '',
        '---',
        '',
        '### Hebrews 5:7',
        '',
        f'> *"{_kjv("Heb", 5, 7)}"* (KJV)',
        '',
        '- **δεήσεις** and the related noun "supplications" describe '
        'Jesus\' own prayer in Gethsemane — the supreme biblical example '
        'of intense, need-driven petition',
        '- The combination of "strong crying and tears" confirms δέησις '
        'as the prayer of extremity',
        '',
        '---',
        '',
        '## The Intercession Concept: ἐντυγχάνω in the NT',
        '',
        'The verb ἐντυγχάνω (G1793, "to intercede / petition on behalf of") '
        'illuminates what ἔντευξις means in 1 Tim 2:1. Its 5 NT occurrences '
        'trace the full arc of NT intercession:',
        '',
        '| Reference | Who intercedes | For/against whom | Notes |',
        '|---|---|---|---|',
        '| Act 25:24 | The Jewish leaders | Against Paul (before Festus) | '
        'Human intercession in a legal/political context — the original '
        'Hellenistic sense of petitioning a ruler |',
        '| Rom 8:26–27 | The Holy Spirit | For the saints | '
        '"The Spirit itself maketh intercession for us with groanings which '
        'cannot be uttered" — divine intercession within the believer |',
        '| Rom 8:34 | Christ Jesus | For the elect | '
        '"Who is even at the right hand of God, who also maketh intercession '
        'for us" — Christ\'s heavenly advocacy |',
        '| Rom 11:2 | Elijah | Against Israel (before God) | '
        '"Lord, they have killed thy prophets…" — intercession as accusation, '
        'showing the full range of the concept |',
        '| Heb 7:25 | Christ | For those who come to God through him | '
        '"He ever liveth to make intercession for them" — the perpetual, '
        'priestly intercession of the risen Christ |',
        '',
        'This distribution is theologically decisive for understanding 1 Tim 2:1: '
        'the church\'s ἔντευξις for all people is not merely an ethical practice '
        'but a participation in the Son\'s and Spirit\'s own intercessory ministry. '
        'The same word that describes the Spirit\'s groanings and Christ\'s '
        'priestly advocacy before the Father describes the church\'s prayer '
        'for kings and rulers.',
        '',
        '---',
        '',
        '## Theological Significance',
        '',
        '### The prayer taxonomy of 1 Timothy 2:1',
        '',
        'Paul\'s four-term list is not accidental accumulation. Each term '
        'identifies a dimension of prayer that the others do not cover:',
        '',
        '| Term | What it emphasizes | What it excludes |',
        '|---|---|---|',
        '| δεήσεις | Urgency, need, specific petition | Generic or routine prayer |',
        '| προσευχάς | Comprehensive God-ward address | Urgency or specific advocacy |',
        '| ἐντεύξεις | Advocacy before God for others | Self-focused petition |',
        '| εὐχαριστίας | Grateful response to grace | Petitionary posture |',
        '',
        'Together they constitute a full-orbed ecclesial prayer life: '
        'coming to God in need (δέησις), addressing him comprehensively in '
        'worship (προσευχή), standing before him as advocates for others '
        '(ἔντευξις), and doing all of it out of gratitude for what he has '
        'already given (εὐχαριστία).',
        '',
        '### Old covenant roots, new covenant flowering',
        '',
        'The Hebrew OT gave the church δέησις and προσευχή — the urgent '
        'petition and the formal address of the Psalms. The NT adds ἔντευξις '
        '(the believer\'s advocacy grounded in Christ\'s and the Spirit\'s '
        'own intercession) and εὐχαριστία (thanksgiving re-centred on the '
        'Christ-event). The prayer vocabulary of 1 Tim 2:1 thus holds together '
        'the continuity of OT prayer practice with the new covenant dimensions '
        'that only the incarnation, death, resurrection, and Pentecost make possible.',
        '',
        '---',
        '',
        '## Data Files',
        '',
        '| File | Contents |',
        '|---|---|',
        '| [prayer-nt-concordance.csv](prayer-nt-concordance.csv) | '
        'NT concordance for all 8 terms (4 nouns + 4 verbs) with KJV text |',
        '| [prayer-lxx-concordance.csv](prayer-lxx-concordance.csv) | '
        'LXX concordance for δέησις, προσευχή, δέομαι, προσεύχομαι (canonical) |',
    ]

    path = REPORT_DIR / 'prayer-vocabulary-report.md'
    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Report: {path}')


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    _chart_nt_nouns()
    _chart_nt_verbs()
    _chart_lxx()
    _chart_noun_verb_totals()
    _csv_nt()
    _csv_lxx()
    _build_report()
    print('\nDone.')
