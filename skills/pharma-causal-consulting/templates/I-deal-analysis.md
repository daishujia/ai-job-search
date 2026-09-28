# Template I — Deal Flow & License Analysis

| Field | Value |
|---|---|
| **Business question** | What does deal activity tell us about innovation? |
| **Causal question** | Does deal activity reflect or cause innovation? |
| **Conventional approach** | Deal-count time series — **Rung 1** |
| **Causal upgrade** | IV analysis (global M&A cycles as instrument), Granger causality, survivorship correction |
| **Subagent** | [1 — Market Data Analyst](../subagents/01-market-data-analyst.md) |
| **Typical stages** | 6 (Portfolio/BD) |

---

## Phase 1 — Context & question formulation

**Causal question:** Does `[license-out / M&A volume]` cause `[innovation output]`, does
innovation cause deals, or does a third factor cause both?

**Why a regression identifies nothing here.** The relationship is bidirectional by
nature — innovation attracts deals, and deal capital funds innovation — and both are
driven by capital availability. Regressing one on the other estimates a mixture of three
mechanisms and cannot separate them. This category exists because the conventional
deal-count trend line is presented as evidence of capability.

**Estimand:**

```
Estimand:   ATT of deal volume on innovation output (novel-target program starts)
Population: [markets, years]
Contrast:   instrument-induced variation in deal volume
Summary:    [elasticity or per-deal effect]
```

**Also state what the client may actually want.** Often the real question is "is rising
license-out a good sign or a bad sign?" — which is a question about *what kind* of assets
are being sold, not about volume. Answer that one too; see Phase 4.

---

## Phase 2 — Data collection design

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md).

**Sources:** Cortellis / Evaluate / GlobalData, press releases, filings, global M&A volume
series, interest-rate and capital-flow series, patent and program databases.

**The missingness problem that biases everything.** Undisclosed deal terms are missing
**not** at random — small and unfavorable deals disclose less. Any analysis of deal value
conditioned on disclosure is conditioned on a variable related to the outcome. Record
disclosure rate by year and by deal size band, and state the direction of the resulting
bias.

**Gap table:**

| DAG node | Role | Best source | Gap code | Class | Remedy |
|---|---|---|---|---|---|
| Deal terms | Outcome/exposure | Databases | G4 | | Disclosure-rate bias, signed |
| Global capital conditions | Instrument / confounder | IMF, central banks | G3 | | Interpolate to quarterly |
| Asset stage at deal | Effect modifier | Curation | G2 | Must-Have | Structured dataset |
| Failed negotiations | Cohort frame | — | G8 | Infeasible | State as limitation |

---

## Phase 3 — Causal model & identification

**DAG:**

```
   Global capital conditions (Z) ──┬──▶ Deal volume (X) ──▶ Innovation output (Y)
                                   └──────────────────────────────▲
                                                                  │
                           FX, domestic policy, talent supply ────┘

   And the reverse path:  Y ──▶ X   (innovation attracts deals)
```

**Identification — IV:**

| Condition | Assessment |
|---|---|
| Relevance: `Z` moves `X` | _[first-stage F; must exceed 10]_ |
| Exclusion: `Z` affects `Y` only via `X` | **untestable — argue it.** Global capital supply does not itself create novel targets |
| Independence: `Z` unconfounded with `Y` | _[consider global science trends as a threat]_ |

**Granger causality** as a supporting, not identifying, analysis: it establishes temporal
precedence in the series, which is necessary but not sufficient for causation. Do not
present a Granger result as a causal effect.

---

## Phase 4 — Estimation

| Element | Specification |
|---|---|
| Method | _[2SLS with global M&A volume as instrument]_ |
| First-stage F | |
| Second-stage estimate | _[point, 95% CI]_ |
| Granger test (supporting) | _[lag order, direction, p]_ |

**The composition analysis that answers the real question.** Deal volume alone is
uninformative about capability; composition is informative:

| Metric | Value | Reading |
|---|---|---|
| Share of deals at preclinical/Phase I | | High and rising → **capital pressure**, selling early |
| Share at Phase II+ | | Rising → negotiating from strength |
| Novel-target share of out-licensed assets | | Low → me-too assets clearing |
| Upfront as % of total deal value | | Low → risk retained by seller |
| Disclosure rate | | Falling → composition shifting to weaker deals |

Rising license-out volume composed of early-stage, me-too assets with low upfronts is
evidence of capital pressure, not of strengthening innovation. The volume trend alone
cannot distinguish the two readings — which is the defect in the conventional analysis.

---

## Phase 5 — Refutation & robustness

| Test | Result | Verdict |
|---|---|---|
| Instrument strength (first-stage F) | | |
| Over-identification (if multiple instruments) | | |
| **Survivorship correction** (entry cohort of dealable assets) | | |
| Disclosure-rate bias, direction signed | | |
| Alternative instrument (interest rates vs M&A volume) | | |
| Reverse-direction Granger test | | |
| Placebo: unrelated sector deal volume | | |
| Capital-cycle-adjusted cross-year comparison | | |

---

## Phase 6 — Storytelling & recommendation

**Headline, with rung label:**

> _[Deal activity reflects / causes / is confounded with innovation]_ — **Rung _[n]_**,
> confidence _[score]_

**Evidence confidence score:**

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | Instrument defensible? |
| Actionability | | Does the finding change a decision? |
| Robustness | | Survivorship and disclosure handled? |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [interpretation of the deal trend + implied action]
P(innovation interpretation correct | data) = [x]%   (prior: [source]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Monitoring plan:** the composition metrics from Phase 4 to track quarterly, with the
thresholds that would flip the reading.

---

## Common failure modes for this category

| Failure | Detection |
|---|---|
| Deal count read as capability | Ask for the composition breakdown |
| Granger result presented as causal | Check whether identification was argued |
| Disclosure bias ignored | Ask for disclosure rate by size band |
| Survivorship in the deal set | Ask how non-deals entered the frame |
| Capital cycle omitted | Ask what else moved in the same years |
| Weak instrument | Check first-stage F |

---

**Related:** [`A-market-intelligence.md`](A-market-intelligence.md) · [`H-portfolio-strategy.md`](H-portfolio-strategy.md) · worked example (C2): [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
