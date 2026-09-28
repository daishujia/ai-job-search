# Subagent Router — Selecting the Right Analyst

This is the **index** for the six subagents. Each subagent's full specification lives in
its own file; this file exists to route a question to the right one and to define the
handoff rules between them.

> Referenced from SKILL.md's File Map as "5 analytical subagents". The five analytical
> specifications are files `01`–`05`; the sixth (data collection design) runs before them
> at CDIP Phase 2 and is specified in
> [`06-active-data-collection-designer.md`](06-active-data-collection-designer.md).

---

## 1. The six at a glance

| # | Subagent | Owns | Data signature | Full spec |
|---|---|---|---|---|
| 1 | Market Data Analyst | Market size, growth causes, entry, deal structure | Currency or transaction counts | [`01`](01-market-data-analyst.md) |
| 2 | Pipeline & Clinical Analyst | Treatment effect, who benefits, program success | Trials, patients, endpoints | [`02`](02-pipeline-clinical-analyst.md) |
| 3 | Biological & Translational Analyst | Does target cause disease; will it translate | Variants, proteins, PK/PD | [`03`](03-biological-translational-analyst.md) |
| 4 | Regulatory & RWE Analyst | Will the evidence be accepted | Claims, EHR, filings | [`04`](04-regulatory-rwe-analyst.md) |
| 5 | Commercial & Strategic Analyst | Did our action work; where to act next | Scripts, promotion, portfolio financials | [`05`](05-commercial-strategic-analyst.md) |
| 6 | Active Data Collection Designer ★ | What data do we need before any of the above | — (runs first) | [`06`](06-active-data-collection-designer.md) |

---

## 2. Routing by question

```
What is the outcome variable?
│
├── Currency, market share, transaction counts
│   ├── "How big / what caused the growth / did entry work?"     → Subagent 1
│   └── "Did our campaign or launch cause this?"                 → Subagent 5
│
├── A clinical endpoint in patients
│   ├── "What is the effect, and for whom?"                      → Subagent 2
│   └── "Will a regulator or payer accept this evidence?"         → Subagent 4
│
├── A molecular or physiological quantity
│   └── "Does the target cause the disease / will it translate?"  → Subagent 3
│
├── An internal process metric (cycle time, throughput)
│   └── "Did the platform investment cause acceleration?"         → Subagent 1
│
└── Not yet determined — the variable does not exist
    └── ALWAYS                                                    → Subagent 6
```

**Routing by data type, when the question is ambiguous:**

| If the analysis will touch… | Route to |
|---|---|
| Deal databases, FX, capital flows, filings | 1 |
| Trial registries, phase transitions, endpoints | 2 |
| GWAS, pQTL, Perturb-seq, omics, PK/PD | 3 |
| Claims, EHR, registries, HTA dossiers | 4 |
| Prescription panels, promotional logs, portfolio financials | 5 |

---

## 3. Confounding specialty map

The fastest routing heuristic is often the confounder, not the outcome. Each named
confounding structure has one owner:

| Confounding structure | Owner | Full treatment |
|---|---|---|
| Capital cycle confounding | 1 | [`01` §4.1](01-market-data-analyst.md) |
| FX effects | 1 | [`01` §4.2](01-market-data-analyst.md) |
| Survivorship bias | 1 | [`01` §4.3](01-market-data-analyst.md) |
| Circularity | 1 | [`01` §4.4](01-market-data-analyst.md) |
| Simpson's paradox by target novelty | 2 | [`02` §4.1](02-pipeline-clinical-analyst.md) |
| Trial count ≠ quality | 2 | [`02` §4.2](02-pipeline-clinical-analyst.md) |
| Selection / publication bias | 2 | [`02` §4.3](02-pipeline-clinical-analyst.md) |
| Pleiotropy | 3 | [`03` §4.1](03-biological-translational-analyst.md) |
| LD artifacts | 3 | [`03` §4.2](03-biological-translational-analyst.md) |
| Reverse causation | 3 | [`03` §4.3](03-biological-translational-analyst.md) |
| Cross-species non-translatability | 3 | [`03` §4.4](03-biological-translational-analyst.md) |
| Immortal time bias | 4 | [`04` §4.1](04-regulatory-rwe-analyst.md) |
| Confounding by indication | 4 | [`04` §4.2](04-regulatory-rwe-analyst.md) |
| Informative censoring | 4 | [`04` §4.3](04-regulatory-rwe-analyst.md) |
| Self-selection in targeting | 5 | [`05` §4.1](05-commercial-strategic-analyst.md) |
| Goodhart's Law | 5 | [`05` §4.2](05-commercial-strategic-analyst.md) |
| Reflexivity | 5 | [`05` §4.3](05-commercial-strategic-analyst.md) |

---

## 4. Method ownership

| Method | Primary owner | Also used by |
|---|---|---|
| DiD (incl. staggered) | 1 | 5, and 7-stage platform work |
| Synthetic control | 1 | 5 |
| IV / LATE | 1 | 3 (as MR) |
| Propensity matching / IPW | 2 | 4 |
| CATE / causal forests | 2 | 5 (as uplift) |
| Target trial emulation | 2 | 4 |
| Mendelian Randomization | 3 | — |
| Colocalization | 3 | — |
| Causal mediation | 3 | — |
| Causal discovery | 3 | — |
| TMLE / AIPW | 4 | 2 |
| E-value / negative controls | 4 | all |
| Uplift modeling | 5 | — |
| Counterfactual scenarios | 5 | 1 |

Definitions and code for all of these: [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md).

---

## 5. Multi-subagent engagements

Most real engagements need more than one analyst. The recurring combinations:

| Engagement | Sequence | Handoff artifact |
|---|---|---|
| Target validation dossier | 6 → 3 → 2 | MR + coloc result becomes the prior for probability of success |
| RWE submission package | 6 → 2 → 4 | Target trial protocol becomes the roadmap's step 1–3 |
| Launch post-mortem | 6 → 5 → 1 | Uplift estimate becomes an input to market-level attribution |
| BD due diligence | 6 → 3 → 2 → 5 | Target evidence → PoS → asset value |
| Blue-book reverse-engineering | 6 → 1 + 2 (parallel) | Confounder inventory, merged in the diagnostic |

### Handoff rules

1. **Subagent 6 always runs first** and its gap table is an input to every downstream
   subagent. A downstream subagent that finds an unlisted Must-Have gap returns to 6
   rather than proceeding.
2. **Estimands are not renegotiated downstream.** If subagent 2 estimates a CATE, and
   subagent 5 needs an ATE, that is a new estimand requiring its own identification —
   not a reweighting of the first result.
3. **Rung labels travel with the number.** A Rung 1 input consumed by a downstream
   subagent makes the downstream conclusion Rung 1, however sophisticated the second
   step is. This rule is what prevents laundering an extrapolation into a causal claim
   by passing it through another model.
4. **Confounder inventories merge, they do not average.** When two subagents analyze the
   same system, the union of their confounder lists applies.
5. **Disagreement is reported, not resolved by preference.** Two subagents reaching
   different conclusions from different designs is triangulation information. Present
   both with their assumptions; the divergence localizes the binding assumption.

---

## 6. Common routing mistakes

| Mistake | Why it happens | Correct route |
|---|---|---|
| Sending "will this drug succeed" to 1 | It sounds commercial | 2 (PoS), with 3 for target evidence |
| Sending "is our RWE good enough" to 2 | It involves patients | 4 |
| Sending "does this biomarker predict response" to 3 | It is molecular | 3 only if asking *causation*; prediction alone is Rung 1 and needs no causal subagent |
| Skipping 6 because data "obviously exists" | Time pressure | Always run 6; the gap table takes minutes and prevents the dominant failure mode |
| Sending report critique to the category owner | It is about markets, pipelines, etc. | Reverse-engineering is Category L: run the diagnostic first, then route each identified confounder to its owner |

---

## Cross-references

- Full method reference: [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md)
- Stage-by-stage workflows: [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md)
- Report templates by category: [`../templates/all-report-templates.md`](../templates/all-report-templates.md)
