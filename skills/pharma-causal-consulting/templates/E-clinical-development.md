# Template E — Clinical Development Strategy

| Field | Value |
|---|---|
| **Business question** | How should we design and position this program? |
| **Causal question** | What is the causal treatment effect, for whom, under what conditions? |
| **Conventional approach** | Standard statistical analysis — **Rung 1–2** |
| **Causal upgrade** | Target trial emulation, ICH E9(R1) estimand framework, CATE via causal forests |
| **Subagent** | [2 — Pipeline & Clinical Analyst](../subagents/02-pipeline-clinical-analyst.md) |
| **Typical stages** | 3 (Clinical) |

---

## Phase 1 — Context & question formulation

**Causal question:** What is the effect of `[regimen]` versus `[comparator]` on
`[endpoint]`, in whom, under what adherence conditions?

**Estimand — all five ICH E9(R1) attributes. None may be left implicit:**

| Attribute | Specification |
|---|---|
| 1. Treatment condition | _[regimen, permitted concomitant therapy]_ |
| 2. Population | _[criteria; subgroups of interest, pre-specified]_ |
| 3. Endpoint | _[variable, timing, scale]_ |
| 4. **Intercurrent event strategy** | _[treatment policy / hypothetical / principal stratum / while-on-treatment / composite]_ |
| 5. Population-level summary | _[difference in means / hazard ratio / risk difference]_ |

Attribute 4 is the one most often omitted, and it changes the answer materially. An
analysis that says "we estimated the treatment effect" without these five has not
specified an estimand.

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** own trial data, registries for external comparators, EHR/claims where an
external control is contemplated, historical phase-transition benchmarks.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Baseline severity | Confounder | | | | |
| Biomarker status | Effect modifier | | | | |
| Prior lines of therapy | Confounder | | | | |
| Adherence | Intercurrent event | | | | |
| Censoring reason | Nuisance | | | | |

---

## Phase 3 — Causal model & identification

**Target trial protocol.** Required for any non-randomized comparison, including any
external-control arm:

| Component | Specification |
|---|---|
| Eligibility | _[applied at baseline only]_ |
| **Time zero** | _[the single aligned moment of assignment for both arms]_ |
| Treatment strategies | |
| Outcome & ascertainment | |
| Causal contrast | _[ITT / per-protocol]_ |
| Analysis plan | _[adjustment set, fixed before outcomes are examined]_ |

**Time zero is the failure point.** Ask: could a patient in the comparator arm have become
a treated patient later? If yes, time zero is misaligned and the analysis carries
immortal time bias — invisible in the results table, fatal in review.

**DAG:**

```
Eligibility ─▶ Time zero ─▶ Assignment ─▶ Follow-up ─▶ Outcome
                   ▲            ▲             │
                   │            │             ▼
          (aligned for    Baseline        Censoring
           both arms)     confounders     (informative?)
```

---

## Phase 4 — Estimation

| Element | Specification |
|---|---|
| Primary analysis | ITT under the stated estimand |
| Estimate | _[point, 95% CI]_ |
| Heterogeneity | Causal forest CATE, moderators **pre-specified** or declared exploratory |
| External comparator | Propensity method with overlap shown, if applicable |

**Heterogeneity discipline.** A causal forest on 40 covariates in a 300-patient trial will
find heterogeneity whether or not it exists. Validate on a held-out split and report
calibration of predicted versus realized effect by quintile. A flat calibration curve
means the heterogeneity is noise, and the enrichment strategy built on it will fail.

**Enrichment recommendation:** _[subgroup, expected effect, expected prevalence, and the
cost of the screening required to find it]_

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Time-zero sensitivity (alternative alignments) | | |
| Balance diagnostics (SMD) | | |
| Overlap / propensity distribution | | |
| **CATE calibration by quintile** | | |
| Negative control outcome | | |
| Censoring sensitivity (IPCW vs naive) | | |
| Alternative intercurrent event strategy | | |
| E-value | | |

Re-running under a different intercurrent event strategy is the most informative
robustness check for this category: if the conclusion depends on the strategy, the
deliverable must say which decision each strategy supports.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Effect finding]_ — **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Randomized? Emulated? Triangulated? |
| Actionability | | Is the enrichment operationally feasible? |
| Robustness | | Full battery survived? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [design choice / population / go-no-go]
P(success at Phase n+1 | data) = [x]%   (prior: [phase-transition source, indication-matched]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Counterfactual scenarios:**

| | All-comers | Enriched population |
|---|---|---|
| Expected effect | | |
| Required n | | |
| Screening burden | | |
| Falsifier | | |

**Monitoring plan:** the interim readout that would change the design decision, with the
pre-specified threshold.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Estimand stated without the intercurrent event strategy | Check all five attributes |
| Misaligned time zero in external comparator | Ask if a control could later become treated |
| Post-hoc subgroup presented as enrichment evidence | Ask whether moderators were pre-specified |
| Spurious heterogeneity | Ask for CATE calibration |
| Informative censoring ignored | Ask why patients left |

---

**Related:** [`B-pipeline-landscape.md`](B-pipeline-landscape.md) · [`F-regulatory-strategy.md`](F-regulatory-strategy.md) · [`D-translational-assessment.md`](D-translational-assessment.md)
