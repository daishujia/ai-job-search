# Template G — Commercial & Market Access

| Field | Value |
|---|---|
| **Business question** | Did our commercial investment work, and where should we spend next? |
| **Causal question** | Did our intervention cause the observed market outcome? |
| **Conventional approach** | Last-click attribution, market share tracking — **Rung 1** |
| **Causal upgrade** | Uplift modeling, geographic DiD, synthetic control for launches |
| **Subagent** | [5 — Commercial & Strategic Analyst](../subagents/05-commercial-strategic-analyst.md) |
| **Typical stages** | 5 (Commercial) |

---

## Phase 1 — Context & question formulation

**Causal question:** Did `[campaign / launch / access change]` cause `[prescriptions /
revenue / share]`, and for which prescribers or territories?

**Estimand:**

```
Estimand:   ATT of [intervention] on [scripts per territory-period]
Population: [territories, period]
Contrast:   treated territories vs not-yet-treated
Summary:    [difference in scripts, and incremental per unit spend]
```

**The question behind the question.** "Did it work" and "where should we spend next" need
different quantities: the first is an ATT, the second is a CATE. Ranking spend by
predicted *response* rather than predicted *uplift* is the dominant error in this
category, and it systematically overstates ROI.

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** prescription panels, sales/shipment data, promotional activity logs,
formulary and coverage changes with effective dates, competitor launch timing.

**Two data hygiene requirements specific to this category:**

- **Preserve forecast vintages.** Overwriting forecasts destroys the only data that can
  test whether forecasting works. Archive each vintage with its date.
- **Logged intent ≠ delivered contact.** CRM call logs record plans as often as events.
  Validate against an independent signal where one exists.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Market potential | **Unmeasured confounder** | none direct | G1 | Must-Have | Rollout timing as quasi-random |
| Promotional exposure | Treatment | CRM | G2 | | |
| Formulary status | Confounder | Payer data | | | |
| Competitor activity | Confounder | Public | | | |

Market potential is a textbook **G1** gap: it drives both targeting and outcome, and has
no direct measure. The design must work around it rather than adjust for it.

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Market potential (unobserved) ──┬──▶ Promotional targeting (X) ──▶ Prescriptions (Y)
                                   └────────────────────────────────────▲
                                                                        │
   Competitor launch, formulary change, seasonality ────────────────────┘
```

Reps call on high-potential prescribers, so naive comparison of called versus non-called
attributes their potential to the calls. The bias is mechanical, not marginal.

**Identification:** _[geographic DiD on staggered rollout / synthetic control for single
market / uplift where targeting was quasi-random / holdout if one exists]_

**Assumptions:**

- Parallel trends between treated and not-yet-treated territories.
- No anticipation ahead of rollout.
- **Interference bounded**: spillover from sales-force reallocation and competitor
  response is contained within the chosen unit. State the assumed spillover radius.

A holdout region remains the only clean answer, and is worth arguing for before the next
campaign rather than reconstructing after this one.

---

## Phase 4 — Estimation

**Use Callaway–Sant'Anna for staggered rollout**, not two-way fixed effects: with
staggered adoption, TWFE uses already-treated units as controls with weights that can be
negative, so the estimate need not lie within the range of the true effects.

| Element | Specification |
|---|---|
| Method | _[att_gt / synthetic control / X-learner uplift]_ |
| Unit / period | |
| Estimate | _[point, 95% CI]_ |
| Event-study path | _[dynamic effects by period since treatment]_ |

**Four-segment uplift decomposition — report all four with sizes:**

| Segment | Size | Behavior | Action |
|---|---|---|---|
| Persuadables | | Act only if treated | **Target** |
| Sure things | | Act regardless | Do not spend |
| Lost causes | | Never act | Do not spend |
| **Sleeping dogs** | | Act only if *not* treated | **Targeting destroys value** |

A non-trivial sleeping-dog segment changes the recommendation, not just its magnitude.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Pre-trend / event-study leads | | |
| Placebo-in-time | | |
| Placebo-in-space | | |
| Uplift validation (Qini curve, held out) | | |
| Sleeping-dog segment size | | |
| Spillover sensitivity (vary unit, drop borders) | | |
| **Forecast backtest by vintage** | | |
| Measure–construct gap (targeted vs untargeted proxy) | | |

The forecast backtest and the measure–construct gap are the reflexivity and Goodhart
tests. Both are specific to this category and both are routinely skipped.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Attribution finding]_ — **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Quasi-random assignment? Holdout? |
| Actionability | | Is the targeting operationally implementable? |
| Robustness | | Pre-trends clean? Uplift validated? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [reallocate spend to (segment) / hold / run a holdout next cycle]
P(incremental return > threshold | data) = [x]%   (prior: [source]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Counterfactual scenarios:**

| | Current allocation | Uplift-ranked allocation |
|---|---|---|
| Predicted scripts | | |
| Spend | | |
| Falsifier | | |

**Monitoring plan:** the untargeted proxy that detects Goodhart drift, and the review
cadence.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Response ranking presented as uplift | Ask whether sleeping dogs were estimated |
| Last-click attribution | Ask how the multi-touch path was handled |
| Two-way FE on staggered rollout | Check the estimator |
| Interference ignored | Ask about border territories and competitor response |
| Reflexivity in the forecast | Ask whether resourcing followed the forecast |
| Goodhart drift | Ask what the untargeted proxy shows |

---

**Related:** [`A-market-intelligence.md`](A-market-intelligence.md) · [`H-portfolio-strategy.md`](H-portfolio-strategy.md) · [`F-regulatory-strategy.md`](F-regulatory-strategy.md)
