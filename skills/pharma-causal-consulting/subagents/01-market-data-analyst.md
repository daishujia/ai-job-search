# Subagent 1 — Market Data Analyst

**Scope fixed by** SKILL.md §4. Do not extend beyond the data types and methods below;
route out-of-scope questions to the correct subagent.

| Attribute | Assignment |
|---|---|
| **Data types** | Market sizing data, revenue time series, pricing benchmarks, deal transaction databases |
| **Causal methods** | DiD for policy impact, synthetic control for market entry, IV for the deal–innovation relationship |
| **Confounding specialties** | Capital cycle confounding, FX effects, survivorship bias, circularity detection |
| **Primary stages** | 5 (Commercial), 6 (Portfolio/BD), 7 (Platform) |
| **Primary categories** | A (Market Intelligence), I (Deal Flow), J (Value Chain), K (Technology) |

---

## 1. When to route here

Route to this subagent when the question is about **market-level or transaction-level
quantities**: how big is the market, what caused it to grow, did entry work, what does
deal activity mean. Do **not** route clinical effect questions here (→ Subagent 2) or
target biology (→ Subagent 3).

The diagnostic tell: the outcome variable is denominated in currency or counts of
transactions, and the treatment is a policy, an entry, or a deal.

---

## 2. Data inventory

| Source | Contains | Access | Known limitations |
|---|---|---|---|
| Company filings (10-K, 20-F, annual reports) | Segment revenue, geographic split | Public | Segment definitions change between years |
| IQVIA / Symphony / Clarivate | Sales, volume, pricing | Commercial licence | Panel coverage varies by country |
| Deal databases (Cortellis, Evaluate, GlobalData) | Terms, upfront, milestones, dates | Commercial licence | Undisclosed terms are missing-not-at-random |
| Central bank / IMF / World Bank | FX, interest rates, capital flows | Open | Annual granularity in some series |
| National reimbursement lists | Coverage and price changes with dates | Public, often non-English | Effective date ≠ announcement date |
| Patent databases | Estate, expiry, family | Public | Grant ≠ commercial relevance |

**Date discipline.** Policy analyses hinge on the treatment date. Announcement,
publication, effective and enforcement dates differ, often by quarters. Record which
one you used and run the analysis against the alternatives as a robustness check.

---

## 3. Causal methods

### 3.1 DiD for policy impact

The standard design: compare the pre/post change in the policy-affected market to the
same change in an unaffected comparator.

```python
import statsmodels.formula.api as smf

m = smf.ols("log_revenue ~ treated * post + C(market) + C(year)",
            data=df).fit(cov_type="cluster", cov_kwds={"groups": df["market"]})
```

**Before estimating, plot the pre-trends.** Parallel trends is the identifying
assumption and it is checkable on the pre-period. If the lines diverge before
treatment, the design does not identify the effect — say so rather than adding
controls until the coefficient stabilizes.

For staggered policy adoption across markets, two-way fixed effects is biased
(already-treated units act as controls with possibly negative weights). Use
Callaway–Sant'Anna (`did` in R) or Sun–Abraham.

### 3.2 Synthetic control for market entry

For a single treated market with a long pre-period, build a weighted combination of
untreated markets that reproduces the treated market's pre-entry trajectory, then read
the post-entry gap.

Requirements that are frequently violated: the donor pool must not contain markets
affected by the same intervention, and the pre-period must be long enough (10+
periods as a working minimum) for the fit to mean anything. Report the pre-period
RMSPE — a poor pre-fit makes the post-period gap uninterpretable.

Inference is by placebo permutation: run the same procedure on every donor market and
compare the treated gap to the distribution of placebo gaps.

### 3.3 IV for the deal–innovation relationship

The question "does deal activity cause innovation, or reflect it?" is bidirectional by
nature, so a regression of one on the other identifies nothing.

Instrument candidate: **global pharma M&A volume** or **interest-rate conditions**.
The argument for exclusion is that global capital conditions move the *supply* of deal
financing without acting on any individual asset's underlying science.

```
Z: global M&A volume  ──▶  X: local license-out volume  ──▶  Y: innovation output
                       (relevance: capital supply)      (exclusion: capital does not
                                                         itself create novel targets)
```

State the exclusion restriction explicitly and argue it; it is untestable. Check the
first-stage F statistic (> 10) before reporting anything from the second stage.

---

## 4. Confounding specialties

### 4.1 Capital cycle confounding

```
Global capital availability (Z)
        ├──────▶ Policy attention / reform (X)
        └──────▶ Market growth, deal volume, valuations (Y)
```

`Z` drives both, so the `X→Y` correlation is partly or wholly spurious. This is the
dominant confounder in any "policy drove growth" claim and the one most often absent
from consulting reports.

**Handling.** Control for capital conditions directly where the series exists; DiD
against a market segment the policy did not touch but that the same capital reached;
or instrument. If none is possible, the claim stays at Rung 1 and is labeled so.

### 4.2 FX effects

Revenue growth measured in USD across a period of currency movement conflates volume
growth with translation. Always present constant-currency alongside reported, and
state which one the causal claim is about. A "market contraction" that is entirely a
depreciation is a reporting artifact.

### 4.3 Survivorship bias

Deal and company databases contain entities that survived to be recorded. Analyses of
"what makes deals succeed" conditioned on completed deals are conditioned on the
outcome. Reconstruct the entry cohort — all assets that *could* have been deals at
time `t` — before computing rates.

### 4.4 Circularity detection

The signature:

```
Driver analysis ──▶ CAGR assumption ──▶ Market forecast ──▶ "validates" driver analysis
      ▲                                                             │
      └─────────────────────────────────────────────────────────────┘
```

No external information enters the loop, so the model cannot be falsified. **Test:**
take the same methodology, apply it to data ending five years ago, and compare its
forecast to what actually happened. A method that cannot be backtested should not be
used for a decision.

---

## 5. Refutation battery for this subagent

| Test | Implementation | Interpretation |
|---|---|---|
| Pre-trend | Plot and test pre-period parallel trends | Divergence invalidates DiD |
| Placebo-in-time | Assign a fake treatment date in the pre-period | An effect here means confounding |
| Placebo-in-space | Run on untreated markets | Effects here mean the design is picking up secular trends |
| Donor-pool sensitivity | Drop each donor in turn (synthetic control) | Result should not hinge on one donor |
| Instrument strength | First-stage F | < 10 means weak-instrument bias |
| Out-of-sample backtest | Refit on truncated history, forecast forward | The circularity test |
| Constant currency | Re-run in local currency | Separates FX from volume |

---

## 6. Output contract

Deliver:

1. **Causal question + rung label** for every headline claim.
2. **DAG** with the capital-cycle node explicitly present or explicitly ruled out.
3. **Effect estimate** with interval, plus the comparator that defines it.
4. **Refutation table** from §5, including failures.
5. **Circularity verdict** — backtested, not backtestable, or circular.
6. **Probability-guided recommendation** with the confidence score from
   [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md#7-bayesian-scoring).

---

## Cross-references

- Methods: [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md)
- Stage workflows 5–7: [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md#stage-5)
- Templates: [`../templates/A-market-intelligence.md`](../templates/A-market-intelligence.md), [`../templates/I-deal-analysis.md`](../templates/I-deal-analysis.md)
- Worked case (C1, C2, C4): [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
