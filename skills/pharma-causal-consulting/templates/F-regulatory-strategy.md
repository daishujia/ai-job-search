# Template F — Regulatory Strategy & RWE

| Field | Value |
|---|---|
| **Business question** | Will our evidence be accepted? |
| **Causal question** | Does our evidence meet the causal standard required? |
| **Conventional approach** | Checklist compliance — **Rung 1** |
| **Causal upgrade** | FDA causal framework alignment, van der Laan causal roadmap, E-value analysis |
| **Subagent** | [4 — Regulatory & RWE Analyst](../subagents/04-regulatory-rwe-analyst.md) |
| **Typical stages** | 4 (Regulatory) |

---

## Phase 1 — Context & question formulation

**Causal question:** Does the evidence package identify the effect the decision-maker
needs, to the standard that decision-maker applies?

**Name the decision-maker.** FDA, EMA, and an HTA body apply different standards to the
same package, and a gap analysis against the wrong one is wasted work. Specify:
_[agency / HTA body, jurisdiction, procedure]_.

**Estimand:** as it will be stated in the submission, with all five ICH E9(R1) attributes
([Template E Phase 1](E-clinical-development.md)).

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** Drugs@FDA, EPAR, PMDA, AdComm transcripts and CRLs for precedent; HTA
appraisals for payer standards; claims, EHR, registries, Sentinel/DARWIN EU for RWD.

**Precedent asymmetry to account for.** Approval packages document successes in detail;
failures are documented far less. A precedent search that finds only accepted approaches
will overstate what is acceptable. Search CRLs and AdComm transcripts deliberately.

**Gap table — classify each gap by whether it is closable with existing data:**

| Evidence requirement | Current status | Gap code | Class | Closable with existing data? | Remedy |
|---|---|---|---|---|---|
| | | | | | |

---

## Phase 3 — Causal model & identification

**The causal roadmap, completed in writing before estimation:**

| Step | Content | Reviewer's question |
|---|---|---|
| 1 | Data-generating process described | "Where did these data come from?" |
| 2 | Statistical model specified | "What are you assuming?" |
| 3 | Target parameter defined | "What exactly are you estimating?" |
| 4 | Identification assumptions + plausibility | "Why should I believe it?" |
| 5 | Estimator matched to the parameter | "Is the method appropriate?" |
| 6 | Uncertainty incl. from assumptions | "How wrong could this be?" |

Step 6 is where most packages are thin. Confidence intervals reflect sampling variability
only, while the dominant uncertainty is assumption violation. E-values and quantitative
bias analysis are what address it.

**Target trial protocol** with time zero explicit — required for any RWE comparison.

**DAG — the RWE confounding structure a reviewer will look for:**

```
   Baseline severity, prior lines, comorbidity ──┬──▶ Treatment choice (X) ──▶ Outcome (Y)
                                                 └──────────────────────────────▲
                                                                                │
   Care-seeking intensity ──▶ Covariate capture completeness ─────────────────────┘
                                   │
                                   └──▶ (adjustment quality itself confounded)

   Time zero misalignment ──▶ guaranteed survival in the treated arm  ← immortal time bias
```

Two features distinguish this from a generic confounding DAG, and both are specific to
real-world data. **Covariate capture completeness** is itself a variable: patients who
interact with the health system more have better-measured confounders, so adjustment quality
differs by arm. And **time zero** is not a node in the causal structure at all — it is a
design choice that, made wrongly, manufactures an association no adjustment can remove.

Draw both explicitly. A submitted DAG that omits capture completeness invites the reviewer to
find it.

---

## Phase 4 — Estimation

| Element | Specification |
|---|---|
| Estimator | _[TMLE / AIPW — doubly robust]_ |
| Nuisance models | _[Super Learner ensemble / specified parametric]_ |
| Pre-specification | _[protocol registered on (date) — required]_ |
| Estimate | _[point, 95% CI]_ |
| Overlap | _[propensity plot, trimming and its effect on the estimand]_ |
| Balance | _[SMD table, all covariates]_ |

**Pre-specification is not a formality.** An RWE analysis whose adjustment set was chosen
after seeing outcomes will not survive review, and should not. If the analysis was
exploratory, label it exploratory and plan the confirmatory version.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| **Time-zero audit** | | |
| Negative control outcome (pre-specified) | | |
| Negative control exposure (pre-specified) | | |
| Overlap and trimming sensitivity | | |
| Balance after weighting | | |
| **E-value vs strongest measured confounder** | | |
| Censoring sensitivity (IPCW) | | |
| Missingness / capture rate by arm | | |
| Active comparator re-run | | |

Negative controls are the most persuasive robustness evidence available for RWE, because
a reviewer can interpret them without accepting the model. They must be chosen on
mechanistic grounds and pre-specified — a post-hoc null negative control is not evidence.

**E-value benchmarking:** report the E-value beside the strongest *measured* confounder in
the same analysis. An E-value of 2.4 in a dataset where a measured covariate carries RR 3
does not reassure.

---

## Phase 6 — Storytelling & recommendation

**Headline:**

> _[The package meets / does not meet the standard for [decision-maker], because [binding gap]]_

**Gap analysis with remediation plan:**

| # | Gap | Severity | Closable with existing data | Remediation | Owner | Timeline |
|---|---|---|---|---|---|---|
| 1 | | Blocking / Material / Minor | Yes / No | | | |

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | |
| Actionability | | Can the gap be closed before submission? |
| Robustness | | Negative controls clean? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [submit / strengthen then submit / generate new evidence]
P(acceptance | package, precedent) = [x]%   (prior: [precedent base rate]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**For gaps not closable with existing data:** route to
[Subagent 6](../subagents/06-active-data-collection-designer.md) for a structured dataset
specification, and state the timeline consequence for the submission.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Immortal time bias in a claims comparator | Audit time zero first, always |
| Post-hoc adjustment set | Ask for the registered protocol |
| Confounding by indication with a cross-line comparator | Ask whether an active comparator was available |
| Uncertainty from assumptions omitted | Ask for the E-value |
| Gap analysis against the wrong decision-maker | Confirm agency and procedure |
| Data-quality confounding | Compare covariate capture rates by arm |

---

**Related:** [`E-clinical-development.md`](E-clinical-development.md) · [`G-commercial-strategy.md`](G-commercial-strategy.md)
