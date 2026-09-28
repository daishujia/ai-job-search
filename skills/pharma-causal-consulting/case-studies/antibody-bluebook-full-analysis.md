# Blue Book Full Analysis — Chapter-by-Chapter Transformation

Companion to [`antibody-bluebook-case.md`](antibody-bluebook-case.md), which holds the
diagnostic and the four confounders. This file works through the report **chapter by
chapter**, showing for each one what it asserts, what would be required to assert it
causally, and what the upgraded chapter looks like.

> **Verification note.** Chapter scope follows the structure characterized in SKILL.md §5.
> Values marked `[verify]` must be read from the source document. Do not carry any number
> from this file into a client deliverable without checking it against the report.

---

## How to read this file

Each chapter section has the same four parts:

| Part | Question |
|---|---|
| **Asserts** | What the chapter claims, in its own framing |
| **Requires** | What would have to be true, or measured, for the claim to be causal |
| **Breaks** | Where it fails, and which confounder (C1–C4) is responsible |
| **Upgrade** | The Rung 2–3 version, with method, data and feasibility |

---

## Chapter 1 — Market sizing and growth

**Asserts.** The global and regional antibody market reached `[verify]` and will grow at
`[verify]`% CAGR, driven by policy support, capital investment and unmet need.

**Requires.** For "driven by" to be causal: a comparator that shows what growth would have
been absent each driver, and separation of the drivers from their common cause.

**Breaks.** **C1 (policy–growth confounding)** and **C4 (circularity)**. Global capital
inflows drive both policy attention and growth, so the policy attribution is confounded
upward. The CAGR is derived from the driver analysis that the forecast then validates.

**Upgrade.**

| Element | Specification |
|---|---|
| Method | DiD: antibody vs non-antibody approvals and revenue, pre/post 2017 reform |
| Comparator | Modalities under the same regulatory regime, different capital intensity |
| Controls | Cumulative capital inflow, FX, epidemiological base |
| Refutation | Pre-trend test; announcement vs effective date; constant-currency re-run; **out-of-sample backtest of prior-vintage forecasts** |
| Output | Policy ATT with interval + counterfactual growth path + calibrated forecast |
| Feasible | **Yes** — public registries, filings, IMF series |

**What changes in the conclusion.** The policy effect becomes an interval with a stated
comparator rather than an attribution, and the forecast acquires a calibration record. If
the backtest shows prior vintages were systematically high, the forecast must be adjusted
or withdrawn — not annotated.

---

## Chapter 2 — Pipeline census and competitive ranking

**Asserts.** Regional pipelines ranked by trial and program count; China's ADC pipeline is
second-largest, presented as evidence of capability.

**Requires.** For count to indicate capability: that the marginal trial is informative
about quality. It is not — the marginal trial is the cheapest one.

**Breaks.** **C3 (Simpson's paradox by target novelty).** Novelty is associated with both
count and the capability signal, so the aggregate inverts under stratification.

**Upgrade.**

| Element | Specification |
|---|---|
| Method | Novelty-stratified census; propensity-matched approval probability |
| Curation | Target novelty per program — operational definition, double-coded, κ reported |
| Preferred metrics | First-in-class share; registrational share; median enrollment; transition rate conditional on novelty |
| Refutation | Alternative novelty definitions; registration-vs-conduct check; competing-risks handling of discontinuation |
| Output | Two-panel exhibit: aggregate beside stratified, same scale |
| Feasible | **Yes**, with a curation step (G2 gap, Must-Have) |

**What changes in the conclusion.** The headline ranking is withdrawn and replaced by a
novelty-stratified comparison. This is the cheapest remediation in the whole report and the
one that most changes the reading.

---

## Chapter 3 — Deal flow and license-out analysis

**Asserts.** License-out volume and value are rising; this reflects strengthening
innovation capability.

**Requires.** For deals to indicate capability: separation of capital-supply effects from
asset-quality effects, and a deal set not conditioned on disclosure or completion.

**Breaks.** **C2 (license-out as innovation proxy).** Four mechanisms are conflated — global
M&A demand pull, FX, survivorship in the recorded set, and early-stage selling as a
capital-pressure signal.

**Upgrade.**

| Element | Specification |
|---|---|
| Method | 2SLS with US pharma M&A volume as instrument; composition analysis |
| Composition metrics | Stage at deal; novel-target share; upfront as % of total; disclosure rate by size band |
| Supporting | Granger test for temporal precedence (**not** identification) |
| Refutation | First-stage F > 10; alternative instrument (interest rates); survivorship correction via reconstructed dealable-asset cohort; MNAR disclosure bias signed |
| Output | Elasticity with interval + composition trend + explicit capability-vs-pressure verdict |
| Feasible | **Yes**, with a stated missing-not-at-random caveat |

**What changes in the conclusion.** "Rising license-out = strengthening capability" becomes
a testable question with two candidate answers, and the composition metrics discriminate
between them. Rising volume composed of early-stage me-too assets with low upfronts
supports the *capital pressure* reading.

---

## Chapter 4 — Pricing and access comparison

**Asserts.** Cross-market price comparison with commentary on drivers of price differences.

**Requires.** For price differences to be attributed to clinical value: separation of value
from purchasing power, reference-pricing linkage, volume agreements and confidential
rebates.

**Breaks.** Confounding, and a measurement problem that is often decisive — list prices are
observable, net prices frequently are not, so the comparison may be between quantities that
do not correspond to what anyone pays.

**Upgrade.**

| Element | Specification |
|---|---|
| Method | DAG isolating clinical benefit from purchasing power, reference-pricing linkage, rebate structure |
| Data | Price, clinical benefit measure, access/coverage status, income measure, rebate visibility |
| Refutation | List-vs-net sensitivity; reference-pricing cluster analysis; access-conditioned re-run |
| Output | Price–value relationship with the confounded portion separated, plus an explicit statement of what is unobservable |
| Feasible | **Partially** — net prices are a G8 structural gap in several markets |

**What changes in the conclusion.** This is the chapter where the honest answer is partly
"cannot be determined." The upgrade's value is establishing *which* part of the price
difference is attributable and which is structurally unobservable, with the bias direction
signed.

---

## Chapter 5 — Technology and platform landscape

**Asserts.** Platform and modality trends (ADC, bispecific, engineering technologies) are
advancing, with implications for competitive position.

**Requires.** For platform adoption to indicate advantage: evidence that adoption caused
output change, rather than capable organizations adopting early.

**Breaks.** Selection into adoption — better-resourced organizations adopt sooner, so
adoption is confounded with capability.

**Upgrade.**

| Element | Specification |
|---|---|
| Method | Staggered-adoption event study on public disclosure dates; conditional activation where usage is observable |
| Data | Adoption timing by organization, program outcomes, pre-period capability proxy |
| Refutation | Pre-trend by adoption cohort; concurrent-change audit; placebo on non-adopters |
| Output | Adoption effect with interval, separated from the capability confound |
| Feasible | **Partially** — internal usage telemetry is unavailable externally (G6) |

**What changes in the conclusion.** Trend description is retained (it is legitimate Rung 1),
but any implication that adoption *produces* advantage is labeled as unidentified from
external data.

---

## Chapter 6 — Forecast and scenarios

**Asserts.** Market forecast to 2030 with scenario ranges.

**Requires.** External calibration — some information not derived from the analysis being
validated.

**Breaks.** **C4 (circularity)**, in its clearest form. Scenario ranges built by varying
assumptions within the same circular structure widen the interval without adding
information.

**Upgrade.**

| Element | Specification |
|---|---|
| Method | Out-of-sample backtest of prior-vintage forecasts; refutation-tested assumption set |
| Data | Prior blue-book vintages and realized outcomes |
| Scenarios | Each with stated intervention, assumption, and **falsifier** |
| Refutation | Vintage-by-vintage error decomposition; assumption sensitivity outside the circular loop |
| Output | Calibrated forecast with a documented historical error distribution |
| Feasible | **Yes** — prior vintages exist |

**What changes in the conclusion.** The forecast gains an error record. A forecast with a
known historical bias is usable after adjustment; a forecast with no calibration record is
not usable, however narrow its stated range.

---

## Cross-chapter summary

| Chapter | Dominant defect | Confounder | Remediation cost | Conclusion changes? |
|---|---|---|---|---|
| 1 Market sizing | Confounded attribution + circularity | C1, C4 | Medium | Yes — interval replaces attribution |
| 2 Pipeline census | Aggregation | C3 | **Low** | **Yes — headline inverts** |
| 3 Deal flow | Bidirectionality + selection | C2 | Medium–high | Yes — two readings discriminated |
| 4 Pricing | Confounding + unobservability | — | High | Partly — scope of the knowable |
| 5 Technology | Selection into adoption | — | High (external) | No — Rung 1 retained honestly |
| 6 Forecast | Circularity | C4 | **Low** | **Yes — calibration record** |

**The pattern worth generalizing.** The two cheapest remediations (chapters 2 and 6) produce
the two largest changes in conclusion. Stratification and backtesting require no new data
collection, only a different analysis of data already in hand. Start there on any report.

---

**Related:** [`antibody-bluebook-case.md`](antibody-bluebook-case.md) · [`antibody-bluebook-plan.md`](antibody-bluebook-plan.md) · [Template L](../templates/L-report-reverse-engineering.md) · [Template A](../templates/A-market-intelligence.md) · [Template B](../templates/B-pipeline-landscape.md) · [Template I](../templates/I-deal-analysis.md)
