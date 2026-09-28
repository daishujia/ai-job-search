# Blue Book Causal Diagnostic Plan

The **execution plan** for the analysis described in
[`antibody-bluebook-case.md`](antibody-bluebook-case.md) and
[`antibody-bluebook-full-analysis.md`](antibody-bluebook-full-analysis.md).

Those two files establish *what* is wrong and *what* the upgrade is. This file is the
runnable plan: work packages in dependency order, with data requirements, effort,
deliverables, and the decision gates that stop work when it stops paying.

Use it as the model for planning any Category L engagement.

---

## 1. Engagement frame

| Field | Value |
|---|---|
| Object of study | Frost & Sullivan *2026 Global Antibody Drug Industry Development Blue Book* (84 pp.) |
| Diagnostic score | 5/5 — causal methods required |
| Client decision at stake | `[entry timing / partnering / portfolio allocation — specify]` |
| Question 5 verdict | Decisions **would** change if the causal claims were false → engagement justified |
| Template | [L — Report Reverse-Engineering](../templates/L-report-reverse-engineering.md) |

**Sequencing principle.** Order work packages by **decision impact per unit effort**, not by
chapter order and not by intellectual interest. On this report that puts stratification and
backtesting first, because both are cheap and both invert a headline.

---

## 2. Work packages

### WP1 — Novelty-stratified pipeline re-analysis (C3)

| Field | Value |
|---|---|
| Closes | C3, Simpson's paradox by target novelty |
| Owner | [Subagent 2](../subagents/02-pipeline-clinical-analyst.md) |
| Effort | **Low** — days |
| Data | ClinicalTrials.gov + EudraCT extract; Drugs@FDA for approval dates |
| New collection | Dataset **D-1**: target novelty per program (G2 Must-Have) |
| Method | Stratified census; propensity-matched approval probability |
| Deliverable | Two-panel exhibit (aggregate beside stratified, same scale) + stratified rankings |
| Success criterion | Every aggregate comparison in the report has a stratified counterpart |

**Dataset D-1 specification** (per
[Subagent 6 §4](../subagents/06-active-data-collection-designer.md#4-step-3--structured-dataset-design-for-must-have-gaps)):

```
Unit of observation:  one antibody/ADC program
Frame:                all programs with a registered trial in [window], any region
Variable:             target_novelty ∈ {first_in_class, validated}
Operational rule:     first_in_class iff no approved agent against this target
                      as of the program's first trial start date, per Drugs@FDA
Source of truth:      Drugs@FDA, evaluated at the trial start date
Quality control:      double-coded by 2 coders, Cohen's κ reported, disagreements adjudicated
Sample size basis:    stratum coverage — minimum 30 programs per region × novelty cell
```

**Why first.** Lowest cost, and it reverses the report's central pipeline conclusion.

### WP2 — Forecast backtest (C4)

| Field | Value |
|---|---|
| Closes | C4, market-sizing circularity |
| Owner | [Subagent 1](../subagents/01-market-data-analyst.md) |
| Effort | **Low** — days |
| Data | Prior-vintage blue books (or equivalent forecasts) + realized market outcomes |
| New collection | None — archival retrieval only |
| Method | Apply the report's methodology to truncated history; compare forecast to realized |
| Deliverable | Vintage-by-vintage error distribution; verdict: backtested / not backtestable / circular |
| Success criterion | A documented historical error distribution, or a stated reason none can be built |

**Decision gate.** If prior vintages are systematically biased, the 2030 forecast is
adjusted or withdrawn — not footnoted. If no prior vintage is retrievable, the forecast is
labeled **not backtestable** and excluded from any investment case.

### WP3 — Policy-impact DiD (C1)

| Field | Value |
|---|---|
| Closes | C1, policy–growth confounding |
| Owner | [Subagent 1](../subagents/01-market-data-analyst.md) |
| Effort | **Medium** — 2–3 weeks |
| Data | Antibody vs non-antibody approvals and revenue; reform dates; IMF/central-bank capital series; FX |
| New collection | Reform date table (announced / published / effective / enforced) |
| Method | DiD with cumulative-capital control; Callaway–Sant'Anna if reform was staggered |
| Deliverable | Policy ATT with interval + counterfactual growth path |
| Success criterion | Pre-trend parallelism demonstrated, or the design is declared unidentified |

**Stop condition.** If pre-trends diverge and no comparator restores parallelism, report the
association as Rung 1 and stop. Do not add controls until the coefficient stabilizes — that
is specification search, not identification.

### WP4 — Deal composition and IV analysis (C2)

| Field | Value |
|---|---|
| Closes | C2, license-out as innovation proxy |
| Owner | [Subagent 1](../subagents/01-market-data-analyst.md) |
| Effort | **Medium–high** — 3–4 weeks |
| Data | Deal databases; global M&A volume; interest-rate series; program stage and novelty |
| New collection | Dataset **D-2**: stage and novelty at deal date; disclosure rate by size band |
| Method | 2SLS (instrument: US pharma M&A volume) + composition analysis + survivorship correction |
| Deliverable | Elasticity with interval + composition trend + capability-vs-capital-pressure verdict |
| Success criterion | First-stage F > 10 **and** composition metrics computed; either alone is insufficient |

**Stop condition.** If the first-stage F is below 10 and no alternative instrument works,
drop the IV and deliver the composition analysis alone — it answers the client's real
question without requiring identification.

### WP5 — Synthesis and reliability assessment

| Field | Value |
|---|---|
| Owner | Lead, consolidating WP1–WP4 |
| Effort | **Low** — days |
| Inputs | All prior work packages |
| Deliverable | Claim-level reliability table; transformation table; prioritized recommendation; monitoring plan |
| Success criterion | Every extracted claim has a safe-to-use / not-safe-to-use verdict |

---

## 3. Dependency and sequencing

```
WP1 (stratification) ──┐
                       ├──▶ WP5 (synthesis) ──▶ Client deliverable
WP2 (backtest) ────────┤
                       │
WP3 (policy DiD) ──────┤
                       │
WP4 (deals: IV + comp) ┘

WP1 and WP2 are independent and run in parallel — start both immediately.
WP3 and WP4 both need the capital-conditions series: collect it once, use it twice.
WP5 cannot start until WP1 and WP2 report, and should not wait for WP3/WP4 if the
client decision date arrives first — an interim synthesis on WP1+WP2 is already
decision-relevant.
```

---

## 4. Decision gates

| Gate | After | Test | If failed |
|---|---|---|---|
| G-A | WP1 | Does the stratified view invert the aggregate? | If no inversion, the report's pipeline claim stands; say so plainly |
| G-B | WP2 | Is a historical error distribution constructible? | If not, forecast is unusable for decisions; stop WP-forecast work |
| G-C | WP3 | Do pre-trends run parallel? | If not, declare unidentified; deliver Rung 1 label |
| G-D | WP4 | First-stage F > 10? | If not, deliver composition analysis only |
| G-E | WP5 | Does every claim have a usability verdict? | If not, the deliverable is incomplete |

Gates exist to stop work honestly. A failed gate is a finding, not a setback — "this cannot
be identified from available data" is a valid and useful deliverable, and is far more useful
than a causal claim with the failure hidden in a caveat.

---

## 5. Effort summary

| WP | Effort | Data cost | Decision impact | Priority |
|---|---|---|---|---|
| WP1 Stratification | Low | Curation only | **High** — inverts headline | **1** |
| WP2 Backtest | Low | Archival only | **High** — gates forecast use | **2** |
| WP3 Policy DiD | Medium | Public series | Medium–high — entry timing | 3 |
| WP4 Deals IV + composition | Medium–high | Licence + curation | Medium — partnering read | 4 |
| WP5 Synthesis | Low | — | Required | 5 |

**Minimum viable engagement.** WP1 + WP2 + WP5. It is cheap, it changes two headline
conclusions, and it establishes whether the forecast may be used at all. Propose this first;
WP3 and WP4 are justified only if the client's decision turns on policy timing or partnering
specifically.

---

## 6. Deliverable package

1. **Executive decision card** — one page: what the report may and may not be used for.
2. **Claim-level reliability table** — the artifact the client actually consults.
3. **Two-panel pipeline exhibit** — aggregate beside stratified.
4. **Forecast calibration record** — vintage error distribution, or the reason none exists.
5. **Transformation table** — the Rung 2–3 upgrade path per chapter.
6. **Prioritized remediation plan** — what to analyze independently, in order.
7. **Monitoring plan** — which assumptions to re-test as new data arrives, and the falsifier
   for each.

Slide structure for presenting this: see
[`../references/sci-viz-causal-storytelling.md`](../references/sci-viz-causal-storytelling.md).

---

**Related:** [`antibody-bluebook-case.md`](antibody-bluebook-case.md) · [`antibody-bluebook-full-analysis.md`](antibody-bluebook-full-analysis.md) · [Subagent 6](../subagents/06-active-data-collection-designer.md)
