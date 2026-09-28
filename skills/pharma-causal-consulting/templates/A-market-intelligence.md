# Template A — Market Intelligence & Sizing

| Field | Value |
|---|---|
| **Business question** | What is the market size, and what causes it to grow? |
| **Causal question** | Does driver `X` cause market growth `Y`, or do both track a common cause? |
| **Conventional approach** | Bottom-up / top-down extrapolation — **Rung 1** |
| **Causal upgrade** | DiD for policy effects, synthetic control for market entry, circularity detection |
| **Subagent** | [1 — Market Data Analyst](../subagents/01-market-data-analyst.md) |
| **Typical stages** | 5 (Commercial), 6 (Portfolio/BD) |

---

## Phase 1 — Context & question formulation

**Business question as asked:** _[verbatim from the client]_

**Causal question restated:** Does `[driver]` cause `[market outcome]`?

**Rung classification:** _[Association / Intervention / Counterfactual]_ — and, critically,
which rung the *decision* requires. A market-entry decision requires Rung 2; a forecast
of an unchanged regime requires only Rung 1.

**Estimand:**

```
Estimand:   ATT of [policy/entry] on [log market revenue]
Population: [markets, years]
Contrast:   [treated market] vs [comparator that defines "absent the intervention"]
Summary:    [difference in log revenue growth / percentage points of CAGR]
```

**5-Question Diagnostic:** _[score /5 — see [methods §8](../references/causal-inference-deep-review.md#8-five-question-diagnostic)]_

| Q | Assessment |
|---|---|
| Causation claimed from correlation? | |
| Plausible unmeasured common cause? | |
| Aggregate could invert under stratification? | |
| Input derived from the output it validates? | |
| Would the decision change if the claim were false? | |

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources inventoried:** filings, prescription/sales panels, reimbursement lists with
effective dates, FX and capital-flow series, epidemiology denominators.

**Date discipline:** state which date defines treatment — announcement, publication,
effective, or enforcement — and check the alternatives in refutation.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Capital availability | Confounder | | | | |
| Policy intensity | Treatment | | | | |
| Epidemiological base | Confounder | | | | |
| FX | Confounder | | | | |

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Capital availability (Z) ──┬──▶ Policy / market reform (X) ──▶ Market revenue (Y)
                              └───────────────────────────────────▲
                                                                  │
   Epidemiology, income growth, FX ───────────────────────────────┘
```

The capital-cycle node is the one most often missing from conventional analyses. Include
it explicitly or state explicitly why it does not apply.

**Identification strategy:** _[DiD / synthetic control / IV / none]_

**Adjustment set:** _[from the backdoor criterion — list it]_

**Assumptions, stated plainly:**

- Parallel trends between treated and comparator markets, absent the intervention.
- No anticipation before the treatment date.
- No spillover from treated to comparator market (SUTVA).
- Positivity: comparator markets are genuinely comparable on pre-period trajectory.

**If nothing identifies the effect:** stop. Label the finding Rung 1, report the
association, and deliver the collection plan from Phase 2. Do not proceed to Phase 4.

---

## Phase 4 — Estimation

| Element | Specification |
|---|---|
| Method | _[DiD / staggered DiD (Callaway–Sant'Anna) / synthetic control / IV]_ |
| Unit / period | |
| Comparator | |
| Currency basis | **State constant-currency vs reported** |
| Estimate | _[point, 95% CI]_ |

**Pre-trend plot:** required, not optional. Include it in the deliverable.

For staggered policy adoption, use Callaway–Sant'Anna rather than two-way fixed effects
([methods §4.4](../references/causal-inference-deep-review.md#44-policy-and-time-series--did-synthetic-control-sccs)).

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Pre-period parallel trends | | |
| Placebo-in-time (fake pre-period date) | | |
| Placebo-in-space (untreated markets) | | |
| Donor-pool sensitivity (synthetic control) | | |
| Alternative treatment date | | |
| Constant currency re-run | | |
| **Out-of-sample forecast backtest** | | |
| E-value | | |

**Circularity verdict:** _[backtested / not backtestable / circular]_

The backtest is the load-bearing test for this category. Take the same methodology,
truncate the data five years back, forecast forward, and compare to what happened. A
sizing method that cannot be backtested should not support a decision.

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Finding]_ — **Rung _[n]_**, confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | |
| Actionability | | |
| Robustness | | |
| **Composite** | | |

**Counterfactual scenarios:**

| | World A (intervene) | World B (do not) |
|---|---|---|
| Assumption | | |
| Predicted outcome | | |
| Falsifier | | |

**Probability-guided recommendation:**

```
Recommendation:  [action]
P(outcome > threshold | data) = [x]%   (prior: [source]; sensitivity band: [skeptical–enthusiastic])
Decision band:   [≥60 act now / 30–59 act with monitoring / <30 collect more data]
```

**Monitoring plan:** the observable that would falsify this recommendation, the
threshold that triggers revisiting, and the review date.

**Stated limitations:** every Infeasible gap from Phase 2, with bias direction signed
where it can be.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Rung 1 extrapolation presented as an entry decision | Ask what changes the regime |
| Capital cycle omitted from the DAG | Check for a "policy drove growth" claim |
| FX mistaken for volume | Compare reported vs constant currency |
| Circular forecast | Ask what external data could falsify the CAGR |
| Survivorship in the market definition | Ask how exited players were handled |

---

**Related:** [`I-deal-analysis.md`](I-deal-analysis.md) · [`L-report-reverse-engineering.md`](L-report-reverse-engineering.md) · worked example: [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
