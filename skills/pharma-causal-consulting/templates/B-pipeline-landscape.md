# Template B — Pipeline & Competitive Landscape

| Field | Value |
|---|---|
| **Business question** | Which pipelines will succeed, and why? |
| **Causal question** | Does program characteristic `X` cause higher probability of success? |
| **Conventional approach** | Trial-count census, target heatmaps — **Rung 1** |
| **Causal upgrade** | Simpson's paradox decomposition by target novelty, approval probability modeling |
| **Subagent** | [2 — Pipeline & Clinical Analyst](../subagents/02-pipeline-clinical-analyst.md) |
| **Typical stages** | 3 (Clinical), 6 (Portfolio/BD) |

---

## Phase 1 — Context & question formulation

**Business question as asked:** _[verbatim]_

**Causal question restated:** Does `[characteristic: modality / novelty / design choice]`
cause `[higher approval probability]`?

**The substitution to catch first.** "Which pipeline is larger" and "which pipeline will
succeed" are different questions. Count answers the first and is silent on the second,
because the marginal trial is the cheapest one. If the client asked the second question,
a census does not answer it.

**Estimand:**

```
Estimand:   ATT of [characteristic] on P(approval)
Population: [programs entering Phase n, years]
Contrast:   [programs with characteristic] vs [matched programs without]
Summary:    [risk difference in approval probability]
```

**5-Question Diagnostic:** _[score /5]_ — question 3 (aggregate inversion) is nearly
always positive for this category.

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** ClinicalTrials.gov, EudraCT/CTIS, Drugs@FDA, EPAR, phase-transition
benchmarks, published results.

**The curation gap you will always hit.** Target novelty is not a field in any registry.
It requires a structured dataset with an operational definition — "no approved agent
against this target as of the trial start date, per Drugs@FDA" — double-coded with a
reported κ. Specify it as dataset D-1 per
[Subagent 6 §4](../subagents/06-active-data-collection-designer.md).

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Target novelty | Effect modifier | Manual curation | G2 | Must-Have | Dataset D-1 |
| Sponsor capability | Confounder | | | | |
| Indication difficulty | Confounder | | | | |
| Registrational status | Stratifier | | | | |

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Sponsor capability ──┬──▶ Program characteristic (X) ──▶ Approval (Y)
                        └────────────────────────────────────▲
                                                             │
   Indication difficulty, target novelty, era ───────────────┘
```

**Identification:** propensity matching on indication, sponsor size, start year, line of
therapy, and endpoint type. Report standardized mean differences before and after —
matching that does not achieve balance has adjusted for nothing.

**Assumptions:**

- No unmeasured confounding after conditioning on the matched covariates.
- Positivity: overlap in the propensity distribution, shown as a plot.
- Consistent definition of "approval" across eras and jurisdictions.

---

## Phase 4 — Estimation

**Mandatory stratified presentation.** Every aggregate count is reported alongside its
decomposition:

| Stratum | Region/Sponsor A | Region/Sponsor B | Inverts? |
|---|---|---|---|
| All programs (aggregate) | | | — |
| Validated targets (me-too) | | | |
| Novel targets (first-in-class) | | | |
| Registrational trials only | | | |
| Median enrollment per trial | | | |

**Preferred quantities over raw counts:** first-in-class share, registrational-trial
share, median enrollment, phase-transition rate conditional on novelty.

**Approval probability model:** _[matched estimate, 95% CI]_

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Balance diagnostics (SMD table) | | |
| Overlap / propensity distribution | | |
| **Stratified re-analysis (sign flip?)** | | |
| Alternative novelty definition | | |
| Publication-bias funnel plot | | |
| Competing-risks treatment of discontinuation | | |
| Negative control outcome | | |
| E-value | | |

**Simpson's paradox verdict:** _[aggregate holds under stratification / inverts / attenuates]_

If it inverts, the aggregate statistic must not appear as a headline anywhere in the
deliverable — including in the executive summary, which is where it usually survives.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Finding]_ — **Rung _[n]_**, confidence _[score]_

**The two-panel exhibit.** For this category, the single most useful visual is the
aggregate view beside the stratified view, at the same scale, so the inversion is
visible rather than argued. See
[`../references/sci-viz-causal-storytelling.md`](../references/sci-viz-causal-storytelling.md).

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | |
| Actionability | | |
| Robustness | | |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [action]
P(success | characteristic, data) = [x]%   (prior: [phase-transition source]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Monitoring plan:** which readouts in the next 12 months would change the ranking.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Count used as a capability claim | Ask what the marginal trial cost |
| Simpson's paradox unexamined | Ask for the novelty-stratified view |
| Registration mistaken for conduct | Check completion and update status |
| Discontinuation read as scientific failure | Separate portfolio from science reasons |
| Survivorship in a cross-sectional pipeline | Reconstruct the entry cohort |

---

**Related:** [`E-clinical-development.md`](E-clinical-development.md) · [`H-portfolio-strategy.md`](H-portfolio-strategy.md) · worked example (C3): [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
