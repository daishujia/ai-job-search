# Template D — Translational & Preclinical Assessment

| Field | Value |
|---|---|
| **Business question** | Will this preclinical result hold up in humans? |
| **Causal question** | Will preclinical efficacy translate causally to human outcomes? |
| **Conventional approach** | PK/PD descriptive analysis — **Rung 1** |
| **Causal upgrade** | Causal mediation analysis, cross-species DAG alignment, ADMET causal networks |
| **Subagent** | [3 — Biological & Translational Analyst](../subagents/03-biological-translational-analyst.md) |
| **Typical stages** | 2 (Preclinical) |

---

## Phase 1 — Context & question formulation

**Causal question:** Does the mediating chain (exposure → target engagement → biomarker)
carry the effect, and does it have the same structure in humans?

**Reframe the question before analyzing it.** The animal outcome is not the target of
inference. Translation is a **mediation** question about whether the chain has the same
structure across species, not a question about whether the animal effect was large.
A large animal effect through a species-specific mechanism translates worse than a modest
effect through a conserved one.

**Estimand:**

```
Estimand:   Proportion of the total effect of [dose] on [outcome] mediated by [biomarker]
Population: [species, model, n]
Contrast:   [dose levels], compared at equal EXPOSURE or equal ENGAGEMENT, not equal dose
Summary:    NDE, NIE, proportion mediated
```

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** animal efficacy studies, PK/PD time series, receptor occupancy, toxicology
and ADMET panels, ex vivo human tissue, historical translation-success databases by target
class and modality.

**The gap that recurs here.** Mediation analysis needs the mediator measured at adequate
temporal resolution. Sparse PK sampling is a **G3 (coarse granularity)** gap that can make
mediation unidentifiable. Diagnose it before estimating, not after.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Exposure (AUC, Cmax) | Mediator step 1 | PK | | | |
| Target engagement | Mediator step 2 | Occupancy assay | | | |
| Biomarker | Mediator step 3 | | | | |
| Cross-species moderators | Moderator | Literature | G2 | | |
| Human tissue comparator | Validation | Ex vivo | | | |

---

## Phase 3 — Causal model & identification

**Cross-species DAG alignment:**

```
Animal:  Dose ─▶ Exposure ─▶ Engagement ─▶ Biomarker ─▶ Animal outcome
                                 │
       moderators ───────────────┤ receptor homology, metabolic route,
                                 │ immune repertoire, model construct validity
                                 │
Human:   Dose ─▶ Exposure ─▶ Engagement ─▶ Biomarker ─▶ Clinical outcome
```

**Identification:** causal mediation on the exposure → engagement → biomarker chain.
Where the mediator is fully mediating and unconfounded, the **front-door criterion**
applies — one of the few genuine front-door opportunities in the value chain
([methods §3.2](../references/causal-inference-deep-review.md#32-front-door-criterion)).

**Assumptions:**

- Sequential ignorability: no unmeasured confounding of dose→mediator or mediator→outcome.
- No dose–mediator interaction, or it is modeled explicitly.
- The moderator list is complete enough that the chain structure is comparable.

**Mandatory assumption list.** Enumerate every cross-species assumption and flag each as
**supported** (with evidence) or **unverified**. An unverified assumption is not a minor
caveat here; it is the mechanism by which translational failure happens.

---

## Phase 4 — Estimation

| Quantity | Estimate | Interpretation |
|---|---|---|
| Total effect | | |
| Natural direct effect (NDE) | | Not through the biomarker |
| Natural indirect effect (NIE) | | Through the biomarker |
| **Proportion mediated** | | **If low, the biomarker is not the bridge** |

**The decision this drives.** A biomarker that carries little of the effect should not be
used as the translational endpoint, however well it correlates with response. Correlation
with response and mediation of response are different properties, and only the second
justifies using it to make a go decision.

**Comparison basis:** state whether arms were compared at equal dose, equal exposure, or
equal target engagement. Equal dose is the most common translational error and makes the
comparison uninterpretable across species.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Sequential ignorability sensitivity | | |
| Negative-control biomarker | | |
| Dose–response monotonicity | | |
| **Back-translation (approved drug in this model)** | | |
| Alternative comparison basis (dose vs exposure vs engagement) | | |
| Cross-species moderator sensitivity | | |
| Ex vivo human tissue concordance | | |

**Back-translation is the decisive test.** Does the model reproduce a known human result
for an approved drug in the same class? A model that cannot recover a positive control
should not support a go decision, regardless of the effect size it shows for the candidate.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Finding on translatability]_ — **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Mediation identified? Front-door available? |
| Actionability | | Is the bridge biomarker measurable in humans? |
| Robustness | | Back-translation passed? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [advance / add translational study / deprioritize]
P(translation | data) = [x]%   (prior: [historical class translation rate]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Cross-species assumption ledger** (carried forward into the clinical plan):

| Assumption | Status | If false, consequence |
|---|---|---|
| Receptor homology adequate | | |
| Metabolic route conserved | | |
| Model construct validity | | |
| Biomarker mediates in humans | | |

**Monitoring plan:** the first human study readout that tests each unverified assumption,
and the value that would falsify it.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Comparison at equal dose across species | Check the units of the contrast |
| Biomarker correlation mistaken for mediation | Ask for proportion mediated |
| Construct validity unexamined | Ask by what mechanism the model reproduces the phenotype |
| Back-translation never attempted | Ask which approved drug works in this model |
| Assumption list absent | Ask what would have to be true |

---

**Related:** [`C-target-validation.md`](C-target-validation.md) · [`E-clinical-development.md`](E-clinical-development.md)
