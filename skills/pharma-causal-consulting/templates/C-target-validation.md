# Template C — Target Validation & Discovery

| Field | Value |
|---|---|
| **Business question** | Is this a good target? |
| **Causal question** | Does modulating target `T` cause improvement in disease `D`? |
| **Conventional approach** | GWAS association, differential expression — **Rung 1** |
| **Causal upgrade** | Mendelian Randomization, colocalization, causal discovery from Perturb-seq |
| **Subagent** | [3 — Biological & Translational Analyst](../subagents/03-biological-translational-analyst.md) |
| **Typical stages** | 1 (Target Discovery) |

---

## Phase 1 — Context & question formulation

**Causal question:** Does modulating `[target]` cause improvement in `[disease]`?

**Estimand — state the exposure contrast precisely:**

```
Estimand:   Effect of a 1-SD genetically-proxied change in [target] level on [disease risk]
Population: [ancestry, cohort]
Contrast:   lifelong modest difference in target level
Summary:    [OR or HR per SD]
```

**The interpretation boundary that must be stated in the deliverable.** MR estimates the
effect of a *lifelong modest* difference in target level. It does not estimate the effect
of a drug given at therapeutic dose for a defined period. MR validates direction and
target plausibility; it does not size the clinical effect. Reports that slide between the
two overstate their evidence.

**Direction of intended modulation:** _[inhibition / activation]_ — and does the genetic
evidence support that direction, or the opposite?

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** GWAS Catalog, Open Targets Genetics, UKB-PPP / deCODE / Fenland pQTL,
GTEx / eQTLGen, DepMap and Perturb-seq atlases.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Target level instrument | Exposure | pQTL | | | |
| Disease outcome | Outcome | GWAS | | | |
| Ancestry / population structure | Confounder | PCs | | | |
| Tissue-relevant expression | Moderator | GTEx | G4? | | |

**Two coverage issues to record explicitly:** ancestry skew toward European cohorts
(limits generalizability of the estimate), and tissue mismatch (a whole-blood eQTL is
weak evidence for a CNS target).

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Population structure, LD ──────┐
                                  ▼
   Genotype (Z) ──────▶ Target level (T) ──────▶ Disease (D)
        │                                          ▲
        └──────── pleiotropy ──────────────────────┘   ← violates exclusion
```

**Identification:** instrumental variables via germline genetics. The three IV conditions,
assessed rather than assumed:

| Condition | Assessment | Evidence |
|---|---|---|
| Relevance — `Z` moves `T` | | F statistic, variance explained |
| Exclusion — `Z` affects `D` only via `T` | **untestable; argue it** | Egger intercept as diagnostic |
| Independence — `Z` unconfounded with `D` | | Ancestry PCs, population stratification checks |

**Instrument construction:** clumped to independence (r² < 0.001), _[n]_ variants,
_[cis-only / cis+trans]_. Cis instruments are more defensible for a protein target because
the mechanism is local.

---

## Phase 4 — Estimation

**MR table — all estimators, not just the significant one:**

| Estimator | Estimate (95% CI) | Assumption about pleiotropy |
|---|---|---|
| IVW | | All instruments valid |
| Weighted median | | Valid if >50% of weight valid |
| MR-Egger | | Allows directional pleiotropy |
| MR-PRESSO (outlier-corrected) | | Outliers removed |

| Diagnostic | Value | Interpretation |
|---|---|---|
| MR-Egger intercept | | ≠ 0 → directional pleiotropy |
| Cochran's Q | | High → instruments disagree |
| Steiger directionality | | Failure → possible reverse causation |

**Colocalization:**

| Posterior | Value | Reading |
|---|---|---|
| H4 (one shared causal variant) | | Supports the MR interpretation |
| H3 (two distinct variants) | | **Undermines it, even if MR is significant** |

MR without colocalization is incomplete evidence for a target. Report both.

**Perturbation confirmation:** _[DepMap dependency / Perturb-seq phenotype — direction
consistent with MR?]_ Perturbation data is interventional and therefore Rung 2 natively.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Estimator agreement (IVW / median / Egger) | | |
| Egger intercept | | |
| Heterogeneity (Cochran's Q) | | |
| MR-PRESSO outlier removal | | |
| Leave-one-variant-out | | |
| Colocalization H4 vs H3 | | |
| Steiger directionality | | |
| Second pQTL platform (Olink vs SomaScan) | | |
| Positive control (known target–disease pair) | | |

Platform disagreement between aptamer and antibody assays is informative about the
instrument, not noise to average away. Report it.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Target] modulation is supported / not supported as causal for [disease]_ —
> **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Triangulated MR + coloc + perturbation? |
| Actionability | | Tractability, modality fit |
| Robustness | | Full battery survived? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [advance / deprioritize / collect specific evidence]
P(target is causal | data) = [x]%   (prior: [source]; band: [skeptical–enthusiastic])
Decision band:   [≥60 / 30–59 / <30]
```

**Safety read-across from genetics:** phenotypes associated with the same variants in
the opposite direction are candidate on-target adverse effects. List them — this is one
of the highest-value outputs of genetic target validation and is routinely omitted.

**Monitoring plan:** which forthcoming cohort releases or perturbation datasets would
change this assessment.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| MR effect size read as clinical effect size | Check for "therapeutic" language on an MR estimate |
| Colocalization skipped | Ask for H3/H4 |
| Egger intercept suppressed | Ask for all four estimators |
| Tissue mismatch ignored | Ask which tissue the instrument came from |
| Direction of modulation unchecked | Confirm inhibition vs activation matches the genetics |
| Reverse causation via non-germline exposure | Confirm the instrument is germline |

---

**Related:** [`D-translational-assessment.md`](D-translational-assessment.md) · [`H-portfolio-strategy.md`](H-portfolio-strategy.md)
