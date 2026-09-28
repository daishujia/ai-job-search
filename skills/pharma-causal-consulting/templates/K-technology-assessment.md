# Template K — Technology & Platform Assessment

| Field | Value |
|---|---|
| **Business question** | Is this platform investment paying off? |
| **Causal question** | Which technology investments cause R&D acceleration? |
| **Conventional approach** | Technology readiness levels — **Rung 1** |
| **Causal upgrade** | Causal ROI measurement, platform value attribution, conditional activation analysis |
| **Subagent** | [1 — Market Data Analyst](../subagents/01-market-data-analyst.md) |
| **Typical stages** | 7 (Platform/Digital) |

---

## Phase 1 — Context & question formulation

**Causal question:** Does `[platform / tool / automation]` adoption cause
`[cycle time reduction / throughput increase / success rate improvement]`?

**Why TRL is not an answer.** Technology readiness level is a descriptive maturity scale.
It says nothing about effect on R&D output, and a high-TRL platform can have zero effect
if it does not relieve the binding constraint.

**Estimand:**

```
Estimand:   ATT of platform adoption on [cycle time / throughput]
Population: [teams, projects, periods]
Contrast:   adopting teams vs not-yet-adopting teams
Summary:    [days saved per project, or projects per FTE-year]
```

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** internal cycle-time and throughput logs, platform adoption timing by team,
usage telemetry, headcount and spend, project outcomes, process-mining event logs, vendor
benchmarks.

**The variable that makes this category tractable.** Usage **telemetry** — not adoption
status. Adoption records who was given access; telemetry records who actually used the
capability. The difference between them is what enables the conditional activation test
in Phase 5, which is the strongest available evidence here.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Adoption date by team | Treatment | Rollout records | | | |
| **Actual usage** | Activation | Telemetry | G2 | Must-Have | Instrument the platform |
| Team capability | **Confounder** | Proxy: prior throughput | G2 | Must-Have | Pre-period performance |
| Concurrent reorganization | Confounder | HR records | G6 | | |
| Portfolio mix | Confounder | Project records | | | |

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Team capability / resourcing ──┬──▶ Early adoption (X) ──▶ Cycle time (Y)
                                  └──────────────────────────────▲
                                                                 │
   Concurrent reorg, headcount growth, portfolio mix shift ──────┘
```

**The confound that dominates:** early-adopting teams are usually the better-resourced or
more capable ones. Adoption is therefore confounded with team quality, and a naive
before/after comparison measures capability, not platform effect.

**Identification:** staggered adoption DiD (Callaway–Sant'Anna) with team fixed effects,
which absorbs time-invariant capability. Time-*varying* capability (a team that is
improving anyway) remains a threat, addressed by the pre-trend test.

**Assumptions:**

- Parallel trends in cycle time absent adoption, conditional on team fixed effects.
- No spillover between teams (shared staff and shared infrastructure violate this).
- Portfolio mix stable or adjusted.

---

## Phase 4 — Estimation

| Element | Specification |
|---|---|
| Method | _[att_gt with team fixed effects]_ |
| Unit / period | |
| Estimate | _[point, 95% CI]_ |
| Event-study path | _[dynamic effects; expect a lag while teams learn the tool]_ |

**Causal ROI:**

```
Causal ROI = (estimated effect × value per unit × affected volume) − total cost of ownership
             ─────────────────────────────────────────────────────────────────────────────
                                  total cost of ownership
```

Use the **estimated** effect, not the vendor's claimed effect, and include the full cost of
ownership (licence, integration, training, maintenance, and the productivity dip during
the learning period, which the event-study path will show).

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Pre-trend / event-study leads | | |
| **Conditional activation analysis** | | |
| **Bottleneck movement check** (process mining) | | |
| Concurrent-change audit (reorg, headcount, mix) | | |
| Placebo-in-time | | |
| Placebo teams (never adopted) | | |
| Selection-into-adoption check (pre-period capability by cohort) | | |
| Spillover sensitivity (shared staff) | | |

**Conditional activation analysis is the strongest test in this category.** The effect
should appear only in projects that actually *used* the capability. Teams that adopted but
whose projects could not use it form a built-in negative control:

| Group | Adopted | Used capability | Expected effect |
|---|---|---|---|
| A | Yes | Yes | Effect present |
| B | Yes | No (not applicable to their projects) | **No effect — the negative control** |
| C | No | — | No effect |

An effect in group B is evidence of confounding, not of platform value. This test requires
telemetry, which is why it is a Must-Have gap in Phase 2.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Platform finding]_ — **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Staggered design + activation control? |
| Actionability | | Can adoption be expanded? |
| Robustness | | Group B clean? Bottleneck moved? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [expand / hold / sunset / renegotiate]
P(ROI > threshold | data) = [x]%   (prior: [source]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Counterfactual scenarios:**

| | Expand to all teams | Hold at current adoption |
|---|---|---|
| Expected days saved | | |
| Cost | | |
| Falsifier | | |

**Monitoring plan:** activation rate and bottleneck location, tracked quarterly. A falling
activation rate with flat adoption is the signal that reported benefit is decaying.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| TRL presented as effect evidence | Ask for the estimated effect |
| Adoption used where usage was needed | Ask for telemetry |
| Early-adopter capability confound | Ask about pre-period performance by cohort |
| Concurrent reorganization attributed to platform | Ask what else changed that year |
| Vendor-claimed effect in the ROI | Check whose estimate is in the numerator |
| Learning dip omitted from cost | Ask for the event-study path |

---

**Related:** [`J-value-chain.md`](J-value-chain.md) · [`H-portfolio-strategy.md`](H-portfolio-strategy.md)
