"""
Hebrew verbal syntax analysis for 2nd-year Biblical Hebrew study.

Focuses on the syntactic and discourse-level behaviour of the Hebrew verb system:
  • verb_form_profile     — distribution of all conjugation types by book / passage
  • wayyiqtol_chains      — find and describe consecutive wayyiqtol sequences
  • infinitive_usage      — inf construct vs. absolute with governing prepositions
  • clause_type_profile   — nominal vs. verbal clause ratio; question / negation / relative
  • stem_distribution     — Qal/Nif/Piel/Hif/Hitpael etc. by book

All functions use the MACULA Hebrew WLC data (`syntax_ot`) which provides
word-level `type_` (wayyiqtol, qatal, yiqtol, …) and `role` (v, s, o, adv, p)
annotations — more reliable than the raw TAHOT morphology codes for syntactic work.

Sub-modules
-----------
verb_forms        — verb_form_profile, wayyiqtol_chains, stem_distribution,
                    aspect_comparison, GENRE_SETS
clause_types      — clause_type_profile
infinitives       — infinitive_usage
disjunctive       — disjunctive_clauses, disjunctive_in_chains
conditionals      — conditional_clauses, conditional_summary
relative_clauses  — relative_clauses, relative_clause_summary
particles         — discourse_particles, discourse_particle_summary
"""

from __future__ import annotations
from pathlib import Path

from ._common import VERB_FORM_ORDER, VERB_FORM_LABELS, _strip_diacritics

from .verb_forms import (
    verb_form_profile, print_verb_form_profile, verb_form_chart,
    wayyiqtol_chains, print_wayyiqtol_chains,
    stem_distribution, print_stem_distribution, stem_chart,
    aspect_comparison, print_aspect_comparison, aspect_comparison_chart,
    GENRE_SETS,
)
from .clause_types import (
    clause_type_profile, print_clause_type_profile,
)
from .infinitives import (
    infinitive_usage, print_infinitive_usage,
)
from .disjunctive import (
    disjunctive_clauses, print_disjunctive_clauses,
    disjunctive_in_chains, print_disjunctive_in_chains,
)
from .conditionals import (
    conditional_clauses, print_conditional_clauses,
    conditional_summary, print_conditional_summary,
)
from .relative_clauses import (
    relative_clauses, print_relative_clauses,
    relative_clause_summary, print_relative_summary,
)
from .particles import (
    discourse_particles, print_discourse_particles,
    discourse_particle_summary, print_particle_summary,
)

from ._common import _PREP_DISPLAY


def verbal_syntax_report(book: str, *, output_dir: str = 'output/reports/ot/verbs') -> str:
    """
    Generate a Markdown report covering all five verbal syntax analyses for a book.
    Returns path to the saved file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    md_path = out / f'verbal-syntax-{book.lower()}.md'

    vfp = verb_form_profile(book)
    stems = stem_distribution(book)
    ctp = clause_type_profile(book)
    inf = infinitive_usage(book)

    lines = [
        f"# Hebrew Verbal Syntax Report: {book}",
        "",
        "## 1. Verb Form Profile",
        "",
        "| Form | Count | % |",
        "|---|---:|---:|",
    ]
    for _, r in vfp.iterrows():
        lines.append(f"| {r['form']} | {r['count']} | {r['pct']}% |")

    lines += [
        "",
        "## 2. Verb Stem (Binyan) Distribution",
        "",
        "| Stem | Count | % |",
        "|---|---:|---:|",
    ]
    for _, r in stems.iterrows():
        lines.append(f"| {r['stem']} | {r['count']} | {r['pct']}% |")

    lines += [
        "",
        "## 3. Clause Type Profile",
        "",
        "| Feature | Count | Per 100 verses |",
        "|---|---:|---:|",
    ]
    for _, r in ctp.iterrows():
        lines.append(f"| {r['feature']} | {r['count']} | {r['per_100_verses']} |")

    lines += [
        "",
        "## 4. Infinitive Usage",
        "",
        f"- Infinitive construct: {inf['inf_cst_total']}",
        f"- Infinitive absolute: {inf['inf_abs_total']}",
        "",
        "### Infinitive Construct — governing preposition",
        "",
        "| Prep | Description | Count |",
        "|---|---|---:|",
    ]
    for prep, cnt in sorted(inf['inf_cst_by_prep'].items(), key=lambda x: -x[1]):
        desc = _PREP_DISPLAY.get(prep, prep)
        lines.append(f"| {prep} | {desc} | {cnt} |")

    lines += [
        "",
        "### Infinitive Absolute — sample occurrences",
        "",
        "| Ref | Form | Lemma | Gloss | Paronomastic? |",
        "|---|---|---|---|---|",
    ]
    for ex in inf['inf_abs_examples'][:30]:
        paro = 'yes' if ex['paronomastic'] else ''
        lines.append(
            f"| {book} {ex['chapter']}:{ex['verse']} "
            f"| {ex['text']} | {ex['lemma']} | {ex['gloss']} | {paro} |"
        )

    lines += [
        "",
        "---",
        "_Sources: MACULA Hebrew WLC (Clear Bible, CC BY 4.0)._",
    ]

    md_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Saved: {md_path}")
    return str(md_path)


__all__ = [
    # Constants
    'VERB_FORM_ORDER', 'VERB_FORM_LABELS', 'GENRE_SETS',
    # verb_forms
    'verb_form_profile', 'print_verb_form_profile', 'verb_form_chart',
    'wayyiqtol_chains', 'print_wayyiqtol_chains',
    'stem_distribution', 'print_stem_distribution', 'stem_chart',
    'aspect_comparison', 'print_aspect_comparison', 'aspect_comparison_chart',
    # clause_types
    'clause_type_profile', 'print_clause_type_profile',
    # infinitives
    'infinitive_usage', 'print_infinitive_usage',
    # disjunctive
    'disjunctive_clauses', 'print_disjunctive_clauses',
    'disjunctive_in_chains', 'print_disjunctive_in_chains',
    # conditionals
    'conditional_clauses', 'print_conditional_clauses',
    'conditional_summary', 'print_conditional_summary',
    # relative_clauses
    'relative_clauses', 'print_relative_clauses',
    'relative_clause_summary', 'print_relative_summary',
    # particles
    'discourse_particles', 'print_discourse_particles',
    'discourse_particle_summary', 'print_particle_summary',
    # composite report
    'verbal_syntax_report',
]
