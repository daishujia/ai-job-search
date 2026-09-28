# Template H — Portfolio & BD Strategy

| Field | Value |
|---|---|
| **Business question** | Which assets should we back? |
| **Causal question** | Which assets maximize causal expected value under uncertainty? |
| **Conventional approach** | NPV with assumed probabilities — **Rung 1** |
| **Causal upgrade** | CATE-informed prioritization, MR-derived success probability, causal due diligence |
| **Subagent** | [1 — Market Data](../subagents/01-market-data-analyst.md) + [5 — Commercial & Strategic](../subagents/05-commercial-strategic-analyst.md) |
| **Typical stages** | 6 (Portfolio/BD) |

---

## Phase 1 — Context & question formulation

**Causal question:** For each asset, what is the probability of success and the conditional
value, and are those estimates defensible rather than assumed?

**Where all the content actually lives.** An NPV model's output is dominated by the
probability of success, which is usually a benchmark-table lookup presented as analysis.
The causal work in this category is making that probability defensible: MR-informed at
target level, phase-transition-informed at development level, CATE-informed on the
population the asset can actually be developed in.

**Estimand — note there are two distinct ones, and they must not be merged:**

```
Estimand 1 (asset value):     E[value | success] × P(success)
                              — a forecasting problem conditioned on a causal input
Estimand 2 (deal-innovation): ATT of deal activity on innovation output
                              — a genuine causal question, needs an instrument
```

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** deal databases (terms, upfronts, milestones), pipeline databases,
phase-transition benchmarks, company financials, patent estates, analyst forecasts.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Target causal evidence | PoS input | MR / coloc | | | Route to Subagent 3 |
| Indication-matched transition rate | PoS input | Benchmarks | G7 | | Harmonize "success" definitions |
| Developable population | Value input | CATE | | | Route to Subagent 2 |
| Undisclosed deal terms | Comparator | — | G8 / G4 | | Missing-not-at-random; state bias |
| Failed/abandoned assets | Cohort frame | Hard | G4 | Must-Have | Reconstruct entry cohort |

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Capital availability ──┬──▶ Deal volume & valuations
                          └──▶ Pipeline activity

   Target evidence ──▶ P(success) ──┐
                                    ├──▶ Asset value ──▶ Ranking
   Developable population ──────────┘
```

**Identification, per estimand:**

- **Asset value** — not a causal identification problem in itself; its causal inputs are.
  Each input carries its own rung label, and the ranking inherits the weakest one (see
  handoff rule 3 in [`../subagents/all-subagents.md`](../subagents/all-subagents.md#handoff-rules)).
- **Deal–innovation** — needs an instrument. Global M&A volume or interest-rate
  conditions move deal *supply* without acting on individual asset science. State the
  exclusion restriction and check first-stage F > 10.

**Survivorship correction is mandatory here.** The deal database contains completed
deals, so any inference about "what makes deals succeed" is conditioned on the outcome.
Reconstruct the cohort of assets that *could* have been deals at time `t`.

---

## Phase 4 — Estimation

**Per-asset scorecard:**

| Asset | P(success) | Prior source | Sensitivity band | Conditional value | Expected value | Rung of weakest input |
|---|---|---|---|---|---|---|
| | | | | | | |

**CATE-informed prioritization.** An asset's value depends on the subpopulation it can be
developed in, so ranking on average effects misprices assets whose effect concentrates in
a findable subgroup. Use conditional effects where the evidence supports them, and state
the screening burden that realizing the subgroup requires.

**Prior-sensitivity band is not optional.** Report each P(success) under skeptical,
neutral and enthusiastic priors. A ranking that reorders across the band is not a ranking.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| **Out-of-sample valuation backtest** (historical deals, known outcomes) | | |
| Survivorship correction (entry cohort reconstructed) | | |
| Prior sensitivity (does the ranking reorder?) | | |
| Capital-cycle adjustment (cross-year comparability) | | |
| Instrument strength (deal–innovation, first-stage F) | | |
| Winner's-curse adjustment in competitive processes | | |
| Definition harmonization ("success" across benchmark sources) | | |

---

## Phase 6 — Storytelling & recommendation

**Headline:**

> _[Ranking]_ — with the ranking **stable / unstable** across the prior-sensitivity band

**Evidence confidence score, per asset:**

| Asset | Causal Strength | Actionability | Robustness | Composite | Band |
|---|---|---|---|---|---|
| | | | | | |

**Probability-guided recommendation:**

```
Recommendation:  [back / pass / diligence further on (specific evidence gap)]
P(asset clears threshold | data) = [x]%   (prior: [source]; band: [...])
Decision band:   [≥60 act / 30–59 act with monitoring / <30 collect more data]
```

**Causal due-diligence memo per top asset:**

| Question | Finding | Rung | Confidence |
|---|---|---|---|
| Is the target causal for the disease? | | | |
| Does the preclinical package translate? | | | |
| Is the claimed population developable? | | | |
| Is the comparator assumption defensible? | | | |
| What would falsify the investment case? | | | |

**Monitoring plan:** the readouts in the next 12 months that would reorder the ranking.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Benchmark PoS lookup presented as analysis | Ask where the probability came from |
| Ranking unstable across priors, reported as stable | Ask for the sensitivity band |
| Survivorship in the deal comparator set | Ask how failed assets entered the frame |
| Cross-year valuation comparison without capital adjustment | Check the vintage years |
| Average effect used where the asset needs a subgroup | Ask for the developable population |
| Rung laundering — Rung 1 input, Rung 2 conclusion | Trace each input's rung label |

---

**Related:** [`I-deal-analysis.md`](I-deal-analysis.md) · [`C-target-validation.md`](C-target-validation.md) · [`B-pipeline-landscape.md`](B-pipeline-landscape.md)
