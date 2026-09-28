# Template J — Value Chain & Supply Chain Intelligence

| Field | Value |
|---|---|
| **Business question** | Where should we intervene in the value chain? |
| **Causal question** | Which supply chain interventions cause cost reduction? |
| **Conventional approach** | Porter value chain mapping — **Rung 1** |
| **Causal upgrade** | Causal process mining, staggered DiD for localization impact, bottleneck causal attribution |
| **Subagent** | [1 — Market Data](../subagents/01-market-data-analyst.md) + [5 — Commercial & Strategic](../subagents/05-commercial-strategic-analyst.md) |
| **Typical stages** | 7 (Platform/Digital), 5 (Commercial) |

---

## Phase 1 — Context & question formulation

**Causal question:** Does `[intervention: localization / dual-sourcing / automation /
vendor change]` cause `[cost per unit / lead time / failure rate]`?

**Why mapping is not analysis.** A value chain map describes where cost sits. It does not
say where intervening would move cost, because cost concentration and intervention
leverage are different properties. The largest cost node is often the least elastic.

**Estimand:**

```
Estimand:   ATT of [intervention] on [cost per unit / lead time]
Population: [sites, product lines, periods]
Contrast:   intervened sites vs not-yet-intervened
Summary:    [cost delta per unit, and lead-time days]
```

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** ERP and MES event logs, procurement records, vendor scorecards, batch records
and deviation logs, freight and customs data, tariff and trade-policy dates.

**The data this category uniquely needs.** Process **event logs** with timestamps per
step, not just aggregate cycle time. Without them, a bottleneck claim is unfalsifiable,
because there is no way to observe whether the bottleneck moved.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Step-level timestamps | Mechanism | MES logs | G3 | Must-Have | Extract at step granularity |
| Product mix | Confounder | ERP | | | |
| Volume | Confounder | ERP | | | |
| Vendor quality | Confounder | Scorecards | G2 | | |
| Trade policy dates | Treatment timing | Public | G7 | | Announced vs effective |

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Volume growth, product mix shift ──┬──▶ Intervention decision (X) ──▶ Cost per unit (Y)
                                      └────────────────────────────────────▲
                                                                           │
   Learning curve, input prices, FX, regulatory change ────────────────────┘
```

**The confound that dominates:** the **learning curve**. Unit cost falls with cumulative
volume regardless of intervention, so any before/after comparison during a ramp attributes
learning to the intervention. Sites are also selected for intervention *because* they are
costly, adding regression to the mean.

**Identification:** staggered DiD across sites or product lines (Callaway–Sant'Anna), with
cumulative volume included so the learning curve is not absorbed into the treatment effect.

**Assumptions:**

- Parallel trends in cost trajectory absent the intervention, conditional on cumulative volume.
- No spillover between sites (shared vendors and shared engineering staff violate this —
  state the assumed isolation).
- Product mix stable, or adjusted for explicitly.

---

## Phase 4 — Estimation

| Element | Specification |
|---|---|
| Method | _[staggered DiD (att_gt) with cumulative-volume control]_ |
| Unit / period | |
| Estimate | _[cost delta, 95% CI]_ |
| Event-study path | _[by period since intervention]_ |

**Bottleneck causal attribution via process mining.** The mechanism check that makes the
effect credible:

| Check | Before | After | Reading |
|---|---|---|---|
| Binding constraint (longest queue step) | | | Should **move** if the intervention worked |
| Throughput at the targeted step | | | Should rise |
| Downstream queue | | | Often rises — the constraint relocated |
| Overall cycle time | | | The headline number |

A cycle-time improvement with **no change in bottleneck structure** is evidence of a
confound (volume, mix, learning), not of effect. This is the most useful single test in
the category and it requires only the event log.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Pre-trend / event-study leads | | |
| **Bottleneck movement check** | | |
| Learning-curve control sensitivity (cumulative volume in/out) | | |
| Product-mix adjustment | | |
| Placebo-in-time | | |
| Placebo sites (untouched) | | |
| Regression-to-the-mean check (were costly sites selected?) | | |
| Spillover sensitivity (shared vendors / staff) | | |

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Intervention finding]_ — **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Staggered design available? |
| Actionability | | Is the lever controllable and scalable? |
| Robustness | | Bottleneck moved? Learning curve handled? |
| **Composite** | | |

**Intervention leverage ranking** — by elasticity, not by cost share:

| Node | Cost share | Estimated elasticity | Leverage (share × elasticity) | Confidence |
|---|---|---|---|---|
| | | | | |

**Probability-guided recommendation:**

```
Recommendation:  [intervene at node / pilot / do not intervene]
P(cost reduction > threshold | data) = [x]%   (prior: [source]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Monitoring plan:** the bottleneck location and the downstream queue, tracked monthly —
relocation is the early signal that the intervention's benefit is exhausted.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Cost share mistaken for leverage | Ask for elasticity |
| Learning curve attributed to intervention | Ask whether cumulative volume was controlled |
| Bottleneck claim without event logs | Ask where the constraint moved to |
| Regression to the mean | Ask how sites were selected |
| Mix shift absorbed into the effect | Ask whether product mix changed |
| Spillover via shared vendors | Ask what the control sites share with treated ones |

---

**Related:** [`K-technology-assessment.md`](K-technology-assessment.md) · [`A-market-intelligence.md`](A-market-intelligence.md)
