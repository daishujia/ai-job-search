# Case Study — Reverse-Engineering an Antibody Industry Blue Book

**Subject.** The Frost & Sullivan *2026 Global Antibody Drug Industry Development Blue
Book* (84 pages), as characterized in SKILL.md §5: a high-quality **Level 1
(associational)** industry report.

**Purpose.** A worked application of [Template L](../templates/L-report-reverse-engineering.md)
end to end. This is the reference example for the whole bundle — every phase of the
diagnostic is instantiated here.

> **Scope and verification note.** The confounder structure, diagnostic score and
> transformation logic below are the methodological content of this case and are what the
> case is for. The report's own specific figures are **not reproduced here**; before using
> any of this with a client, read the source document and verify each claim against it.
> Quantities shown as `[verify]` are placeholders for values that must come from the
> source, not from this file. Treating a case study's numbers as the source's numbers is
> itself a Rung-1-laundering error of exactly the kind this template exists to catch.

---

## Phase 1 — Claim inventory and diagnostic

### 5-Question Diagnostic: **5/5** — causal inference methods strongly needed

| Q | Question | Score | Basis in the report |
|---|---|---|---|
| 1 | Causation claimed from correlation? | 1 | "Policy support drove market growth"; "rising license-out = strengthening innovation" |
| 2 | Plausible unmeasured common cause? | 1 | Global capital inflows drive policy attention *and* market growth |
| 3 | Aggregate could invert under stratification? | 1 | Pipeline rankings by trial count, unstratified by target novelty |
| 4 | Input derived from the output it validates? | 1 | Driver analysis → CAGR → forecast → "validates" driver analysis |
| 5 | Would a decision change if the claim were false? | 1 | Used for entry, partnering and portfolio decisions |
| | **Total** | **5/5** | |

A 5/5 score means the report should not be used as a Rung 2 input anywhere without the
adjustments below. It does **not** mean the report is poor — it is a competent Rung 1
document. The defect is in how such documents get used downstream.

### Central claims extracted

| # | Claim | Implied `X → Y` | Stated rung | Rung supported |
|---|---|---|---|---|
| 1 | Policy support drove China's antibody market growth | Policy → Market growth | 2 (implied) | 1 |
| 2 | Rising license-out reflects strengthening innovation capability | Deals → Innovation | 2 (implied) | 1 |
| 3 | China's ADC pipeline is the world's second-largest (positive indicator) | Count → Capability | 1, used as 2 | 1, and inverts |
| 4 | Market will reach `[verify]` by 2030 | Drivers → Forecast | 2 (implied) | Circular |

---

## Phase 2 — What the report would have needed

| Claim | Data needed for a causal claim | Available? | Verdict |
|---|---|---|---|
| 1 Policy → growth | Approval/revenue series for antibody vs non-antibody, pre/post reform | **Yes** — public registries and filings | **Could have been done** |
| 2 Deals → innovation | Global M&A volume as instrument + deal composition by stage and novelty | **Yes** — partially; disclosure is MNAR | **Could have been done, with stated bias** |
| 3 Pipeline count | Target novelty per program | **Yes**, but requires curation (G2) | **Could have been done** |
| 4 Forecast | Prior-vintage forecasts and realized outcomes | **Yes** — historical reports exist | **Could have been done** |

All four were feasible with public data. That is the substantive finding of Phase 2: the
report's Rung 1 framing reflects method choice, not a data constraint.

---

## Phase 3 — The four critical confounders

### C1 — Policy–growth confounding

**Claim.** "Policy support drove China's antibody market growth."

**Structure.**

```
   Global capital inflows (Z) ──┬──▶ Policy attention / 2017 reform (X)
                                └──▶ Antibody market growth (Y)
```

`Z` independently drives both, so the `X→Y` correlation is partly spurious. Capital
availability raises policy salience (governments respond to visible sector activity) and
directly funds the companies generating growth.

**Method.** DiD comparing antibody versus non-antibody approvals pre/post the 2017
regulatory reform. Antibodies are the treated group; other modalities under the same
regulatory regime but with different capital intensity form the comparator.

**Owner.** [Subagent 1 §4.1](../subagents/01-market-data-analyst.md) ·
[bias direction] Upward — the reported policy effect is an upper bound.

**Checks required.** Pre-trend parallelism; announcement vs effective date of the reform;
constant-currency re-run.

### C2 — License-out as an innovation proxy

**Claim.** "Rising license-out volume = innovation capability strengthening."

**Confounders.** Global M&A demand pull; FX dynamics; survivorship bias in the recorded
deal set; and early-stage selling as a *capital pressure* signal rather than a capability
signal.

**Structure.**

```
   Global capital conditions (Z) ──┬──▶ License-out volume (X) ──▶ Innovation output (Y)
                                   └────────────────────────────────────▲
                                                                        │
                                        And the reverse path: Y ──▶ X ──┘
```

**Method.** IV analysis using US pharma M&A volume as the instrument, on the argument that
global capital supply moves deal volume without itself creating novel targets.

**The composition analysis that answers the real question.** Volume alone cannot
distinguish two opposite readings. Composition can:

| Metric | Reading if high/rising |
|---|---|
| Share of out-licensed assets at preclinical/Phase I | **Capital pressure** — selling early |
| Share at Phase II+ | Negotiating from strength |
| Novel-target share of out-licensed assets | Genuine capability |
| Upfront as % of total deal value | Risk retained by seller if low |

**Owner.** [Subagent 1](../subagents/01-market-data-analyst.md) ·
template [`I`](../templates/I-deal-analysis.md).

### C3 — Trial count ≠ quality (Simpson's paradox)

**Claim.** "China's ADC pipeline is the world's second-largest," presented as a positive
indicator.

**Structure.** Target novelty is associated with both the count (me-too programs on
validated targets are cheaper and therefore more numerous) and the outcome of interest
(the innovation signal lives in first-in-class programs).

```
Aggregate:    Region A trial count > Region B trial count       → "A is ahead"

Stratified:   Validated targets (me-too):     A ~80%,  B ~55%
              Novel targets (first-in-class):  A ~20%,  B ~45%
                                                    → B leads where it counts
```

The stratum shares above are the structure SKILL.md §5 records for this case; the precise
figures are `[verify]` against the source and against independent curation.

**Method.** Stratified analysis with target-novelty decomposition. The aggregate count must
not appear as a headline anywhere once the inversion is established — including in the
executive summary, which is where it usually survives.

**Owner.** [Subagent 2 §4.1](../subagents/02-pipeline-clinical-analyst.md) ·
template [`B`](../templates/B-pipeline-landscape.md).

### C4 — Market sizing circularity

**Claim.** The 2030 market forecast.

**Structure.**

```
   Driver analysis ──▶ CAGR assumptions ──▶ Market forecast ──▶ "validates" driver analysis
         ▲                                                              │
         └──────────────────────────────────────────────────────────────┘
```

No external information enters the loop, so the model cannot be falsified — which means it
carries no information about the future state of the world.

**Method.** Out-of-sample backtesting of historical forecasts: take the same methodology,
apply it to data ending five years earlier, and compare its forecast to what actually
happened. Prior-vintage blue books make this feasible.

**Owner.** [Subagent 1 §4.4](../subagents/01-market-data-analyst.md) ·
template [`A`](../templates/A-market-intelligence.md).

---

## Phase 4 — Structural checks summary

| Check | Result |
|---|---|
| Simpson's paradox | **Present** (C3) — aggregate pipeline ranking inverts under novelty stratification |
| Circularity | **Present** (C4) — forecast not externally calibrated |
| Selection / survivorship | **Present** (C2) — deal set conditioned on disclosure and completion |
| Rung substitution | **Present** — claims 1, 2 and 3 are Rung 1 findings used as Rung 2 inputs |

---

## Phase 5 — Transformation table

How each chapter upgrades from Rung 1 to Rung 2–3:

| Chapter | Conventional (Rung 1) | Causal upgrade (Rung 2–3) | Data required | Feasible now |
|---|---|---|---|---|
| Market sizing | Bottom-up extrapolation | DiD-adjusted growth + counterfactual scenarios | Antibody vs non-antibody series, reform dates | Yes |
| Pipeline census | Trial-count rankings | Simpson-decomposed by target novelty | Novelty curation (G2) | Yes, with curation |
| Deal analysis | Trend line + top deals | IV-adjusted innovation–deal relationship + composition | Global M&A series, deal stage/novelty | Yes, with MNAR caveat |
| Pricing | Descriptive comparison | DAG isolating clinical value from confounders | Pricing + clinical benefit + access data | Partially |
| Forecast | Linear CAGR extension | Calibrated models with refutation-tested assumptions | Prior-vintage forecasts + outcomes | Yes |

---

## Phase 6 — Reliability assessment

**Verdict.** A competent Rung 1 document. Reliable as a descriptive census of activity and
as a structured inventory of participants. **Not** reliable as evidence that policy caused
growth, that deal volume indicates capability, that pipeline rank indicates capability, or
that the forecast is calibrated.

**Claim-level reliability:**

| # | Claim | Safe to use for | **Not** safe to use for |
|---|---|---|---|
| 1 | Policy → growth | Describing the policy timeline | Estimating policy impact; entry timing |
| 2 | Deals → innovation | Cataloguing transactions | Judging capability; partner selection |
| 3 | Pipeline rank | Counting registered activity | Competitive threat assessment |
| 4 | 2030 forecast | Understanding stated assumptions | Any investment case or capacity decision |

**Prioritized remediation** — the order in which independent analysis pays off:

| Priority | Analysis | Method | Owner | Why first |
|---|---|---|---|---|
| 1 | Novelty-stratified pipeline | Stratification (C3) | Subagent 2 | Cheapest; reverses a headline conclusion |
| 2 | Forecast backtest | Out-of-sample (C4) | Subagent 1 | Determines whether any forecast is usable |
| 3 | Policy DiD | DiD (C1) | Subagent 1 | Directly informs entry timing |
| 4 | Deal composition + IV | IV + composition (C2) | Subagent 1 | Changes the read on partnering |

Priority 1 costs days and inverts a headline; priority 4 costs weeks. Order by decision
impact per unit effort, not by intellectual interest.

---

## What this case teaches beyond the specific report

1. **A 5/5 diagnostic does not mean a bad report.** It means the report's rung and its use
   are mismatched. Locating the substitution is the deliverable.
2. **The feasibility verdict matters as much as the confounder.** All four analyses were
   possible with public data, which makes the finding actionable rather than academic.
3. **Composition beats volume** whenever a count is being used as a capability claim.
4. **The cheapest remediation is often the one that changes the most.** Stratification
   requires no new data collection and inverted the central pipeline comparison.

---

**Related:** [`antibody-bluebook-full-analysis.md`](antibody-bluebook-full-analysis.md) (chapter-by-chapter) · [`antibody-bluebook-plan.md`](antibody-bluebook-plan.md) (execution plan) · [Template L](../templates/L-report-reverse-engineering.md)
