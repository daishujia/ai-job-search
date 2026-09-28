# Skill Development Plan — `pharma-causal-consulting`

## 1. Problem statement

`SKILL.md` (372 lines) is a complete orchestration layer that names **27 supporting
files**. None existed. Every load instruction in its Quick Start (steps 4–8) failed,
so the skill could not execute its documented workflow at all. This plan completes
the bundle.

## 2. Resolving the layout contradiction first

`SKILL.md` contradicted itself about its own layout. Before authoring anything, the
contradiction had to be resolved, because it determines the file set:

| Location in SKILL.md | Declared layout |
|---|---|
| File Map tree (line ~38) | `subagents/all-subagents.md` (5 agents in one file) + `06-…md` |
| Section 4 body (lines 203–227) | Six separate files, `01-…md` … `06-…md` |
| File Map tree | `templates/all-report-templates.md` + `stage-specific-templates.md` |
| Sections 2 body (lines 111–177) | Twelve separate files, `A-…md` … `L-…md` |
| File Map tree | `case-studies/antibody-bluebook-full-analysis.md` + `…-plan.md` |
| Section 5 body (line 177, 262) | `case-studies/antibody-bluebook-case.md` |

**Decision: satisfy both, without duplicating content.** Per-category and
per-subagent files hold the substance; the aggregate files are genuine *routers*
(selection tables, the 84-cell matrix, the glossary) that point into them. This is
the only option under which every reference in SKILL.md resolves no matter which
naming the model follows at runtime, and it avoids two copies of the same template
drifting apart. The File Map tree in `SKILL.md` is corrected to match the real
tree as the final build step.

## 3. Build order (dependency-ordered)

Content flows downhill, so shared vocabulary is authored before the files that use it.

| Stage | Files | Why this order |
|---|---|---|
| 1. Method foundation | `references/causal-inference-deep-review.md` | Defines the method vocabulary (estimands, DiD, MR, TMLE, DML, E-value, refutation) every other file cites. Nothing above it can be consistent until it exists. |
| 2. Process foundation | `references/workflows-all-stages.md` | Binds the CDIP 6 phases to the 7 value-chain stages. Templates inherit their section skeleton from this. |
| 3. Analyst layer | `subagents/01-…` … `06-…`, then `all-subagents.md` | Each subagent owns data types, methods and confounding specialties fixed by SKILL.md §4. Router written last, from the finished six. |
| 4. Template layer | `templates/A-…` … `L-…`, then the two aggregates | Each category's causal upgrade is fixed by SKILL.md §2. Aggregates (84-cell matrix, glossary) derive from the finished twelve. |
| 5. Worked example | `case-studies/antibody-bluebook-{case,full-analysis,plan}.md` | Instantiates C1–C4 confounders from SKILL.md §5 — needs the methods and templates to point at. |
| 6. Presentation layer | `references/sci-viz-causal-storytelling.md` | §6.1–6.6 viz components and the slide-outline generator consume outputs of every layer above. |
| 7. Reconcile | `SKILL.md` File Map | Tree corrected to the built reality. |

## 4. Acceptance criteria — verified

All checks run programmatically over the built bundle. Results as of the completed build:

- [x] Every one of the 27 paths named anywhere in `SKILL.md` exists. *(23 backticked paths +
      4 tree-only entries; 0 missing. The original audit that opened this work reported 23
      missing; it now reports 0.)*
- [x] Zero unresolved cross-references between bundle files. *(232 markdown links checked,
      0 broken.)*
- [x] No `TODO`, `TBD`, `FIXME`, or placeholder-prose markers in any file. *(Only hit is this
      criterion naming them.)*
- [x] The 12 category templates each state causal question, estimand, DAG, identification
      strategy, estimation method, refutation battery, and a probability-guided
      recommendation.
- [x] Each of the 6 subagents matches the data types, causal methods and confounding
      specialties `SKILL.md` §4 assigns it — checked term by term against the spec.
- [x] The 84-cell matrix is complete: 12 category sections × 7 stage rows = 84 rows, counted.
- [x] Every Python and R snippet is syntactically valid. *(10 Python blocks pass
      `ast.parse`; 6 R blocks pass a comment-stripped bracket-balance check. Not executed —
      see scope boundary.)*
- [x] `SKILL.md`'s File Map tree matches the real tree exactly, in both directions.

### Defects the verification pass caught

Two acceptance criteria failed on first run and were fixed rather than relaxed:

| File | Defect | Fix |
|---|---|---|
| `templates/F-regulatory-strategy.md` | No DAG at all — the template went from the causal roadmap straight to estimation | Added the RWE confounding DAG, including covariate-capture-completeness as a node and time-zero misalignment as a design defect rather than a structural one |
| `templates/L-report-reverse-engineering.md` | No estimand and no refutation framing | Added an **implied estimand** column to the claim inventory (naming the comparator is the test of whether a claim is causal at all), and reframed the four structural checks as this template's refutation battery, with a table mapping each to its analogue in an estimating engagement |

A third finding was a false positive worth recording: the visualization reference cited the
`dataviz` skill's palette file as a backticked relative path, which the link checker read as
a broken internal reference. Reworded to name it as external to this bundle.

## 5. Scope boundary

This plan covers the **bundle's missing files only**. `SKILL.md`'s frontmatter,
taxonomy and philosophy are treated as the fixed specification and are not
redesigned — the sole edit to `SKILL.md` is the File Map correction in stage 7.

Code snippets are **illustrative reference patterns**, not an executable package:
the bundle ships no runnable pipeline, and none is promised by `SKILL.md`. Snippets
are checked for syntactic validity, not executed, because the libraries they name
(DoWhy, EconML, CausalML, TwoSampleMR, grf, tmle3) are not installed here.
