# Stage-Specific Fill-In Templates & Glossary

Seven fill-in-the-blank skeletons, one per value-chain stage, plus the glossary for the
whole bundle.

**When to use these instead of a category template.** Category templates
([`all-report-templates.md`](all-report-templates.md)) are organized by the *question*.
These are organized by the *stage*, and are the right starting point when the client's
brief is stage-shaped ("help us with our Phase 3 strategy") rather than
question-shaped ("did our campaign work"). Both converge on the same six CDIP phases —
fill one of these in, then open the matching category template for the phase detail.

**Contents:** [Stage 1](#stage-1) · [Stage 2](#stage-2) · [Stage 3](#stage-3) ·
[Stage 4](#stage-4) · [Stage 5](#stage-5) · [Stage 6](#stage-6) · [Stage 7](#stage-7) ·
[Glossary](#glossary)

---

## Stage 1 — Target Discovery {#stage-1}

```
ENGAGEMENT:     ______________________________
TARGET:         ______________  DISEASE: ______________
MODULATION:     [ ] inhibition  [ ] activation  [ ] degradation

CAUSAL QUESTION
  Does modulating ______ cause improvement in ______ ?
  Rung required by the decision: [ ] 1  [ ] 2  [ ] 3
  Estimand: effect of a 1-SD genetically-proxied change in ______ on ______
  NOTE: this is lifelong modest modulation, NOT therapeutic-dose effect.

DATA (Subagent 6)
  Instrument source:  [ ] cis-pQTL  [ ] eQTL  [ ] both     n variants: ____
  Outcome GWAS:       ______________  ancestry: ______  n cases: ____
  Perturbation data:  [ ] DepMap  [ ] Perturb-seq  [ ] none
  Must-Have gaps:     ______________________________

IDENTIFICATION
  Relevance  — F stat / variance explained: ______
  Exclusion  — argued how: ______________________ (untestable)
  Independence — ancestry PCs / stratification check: ______

ESTIMATION
  IVW ______  Weighted median ______  MR-Egger ______  PRESSO ______
  Egger intercept ______   Cochran Q ______   Steiger ______
  Colocalization  H4 ______  H3 ______

REFUTATION
  [ ] estimators agree   [ ] leave-one-out stable   [ ] coloc supports
  [ ] second platform    [ ] positive control recovered

OUTPUT
  Verdict: ______________   Confidence score: ____/125   Band: ________
  On-target safety read-across: ______________________
  P(target is causal) = ____%   prior: ______  band: ______
```

→ Detail: [`C-target-validation.md`](C-target-validation.md) ·
[workflow](../references/workflows-all-stages.md#stage-1)

---

## Stage 2 — Preclinical {#stage-2}

```
ENGAGEMENT:     ______________________________
MODEL:          ______________  MODALITY: ______________

CAUSAL QUESTION
  Does the chain exposure → engagement → biomarker carry the effect,
  and does it have the same structure in humans?
  Estimand: proportion of total effect of ______ mediated by ______
  COMPARISON BASIS: [ ] equal dose (weak)  [ ] equal exposure  [ ] equal engagement

DATA (Subagent 6)
  PK sampling density: ______   adequate for mediation? [ ] yes [ ] no (G3)
  Engagement assay: ______   Biomarker: ______
  Human ex vivo comparator: [ ] yes [ ] no
  Must-Have gaps: ______________________________

IDENTIFICATION
  Sequential ignorability argued: ______________
  Front-door available? [ ] yes [ ] no
  Cross-species moderators enumerated: ______________

ESTIMATION
  Total ______  NDE ______  NIE ______  Proportion mediated ______
  If proportion mediated is low, biomarker is NOT the translational bridge.

REFUTATION
  [ ] negative-control biomarker   [ ] dose-response monotonic
  [ ] BACK-TRANSLATION: approved drug recovered in this model
  [ ] alternative comparison basis   [ ] ex vivo concordance

OUTPUT
  Verdict: ______________   Confidence score: ____   Band: ________
  ASSUMPTION LEDGER (carried into clinical plan):
    ____________________  [ ] supported  [ ] unverified
    ____________________  [ ] supported  [ ] unverified
  P(translation) = ____%   prior: ______  band: ______
```

→ Detail: [`D-translational-assessment.md`](D-translational-assessment.md) ·
[workflow](../references/workflows-all-stages.md#stage-2)

---

## Stage 3 — Clinical {#stage-3}

```
ENGAGEMENT:     ______________________________
PROGRAM:        ______________  PHASE: ____  INDICATION: ______________

ESTIMAND — all five ICH E9(R1) attributes (none may be blank)
  1 Treatment condition: ______________________
  2 Population:          ______________________
  3 Endpoint:            ______________________
  4 Intercurrent event strategy: [ ] treatment policy [ ] hypothetical
      [ ] principal stratum [ ] while-on-treatment [ ] composite
  5 Population summary:  ______________________

TARGET TRIAL PROTOCOL (required for any non-randomized comparison)
  Eligibility: ______________   TIME ZERO: ______________
  Treatment strategies: ______________   Contrast: [ ] ITT [ ] per-protocol
  TEST: could a comparator patient later become treated? [ ] no [ ] YES → misaligned

DATA (Subagent 6)
  Own trial data: ______  External comparator: [ ] none [ ] registry [ ] EHR/claims
  Must-Have gaps: ______________________________

ESTIMATION
  Primary (ITT): ______  95% CI ______
  CATE moderators PRE-SPECIFIED? [ ] yes [ ] no → exploratory
  CATE calibration by quintile: ______

REFUTATION
  [ ] time-zero sensitivity   [ ] balance SMD < 0.1   [ ] overlap shown
  [ ] CATE calibration        [ ] negative control    [ ] censoring (IPCW)
  [ ] alternative intercurrent event strategy   E-value ______

OUTPUT
  Design recommendation: ______________   Confidence score: ____
  Enrichment: subgroup ______  prevalence ____%  screening burden ______
  P(success at next phase) = ____%   prior: ______  band: ______
```

→ Detail: [`E-clinical-development.md`](E-clinical-development.md) ·
[workflow](../references/workflows-all-stages.md#stage-3)

---

## Stage 4 — Regulatory {#stage-4}

```
ENGAGEMENT:     ______________________________
DECISION-MAKER: [ ] FDA [ ] EMA [ ] PMDA [ ] HTA: ______  PROCEDURE: ______

CAUSAL ROADMAP (complete in writing BEFORE estimation)
  1 Data-generating process: ______________________
  2 Statistical model:       ______________________
  3 Target parameter:        ______________________
  4 Identification assumptions + plausibility: ______________________
  5 Estimator:               ______________________
  6 Uncertainty incl. from assumptions: ______________________

PRE-SPECIFICATION
  Protocol registered: [ ] yes, date ______  [ ] no → label exploratory

TIME-ZERO AUDIT (do this first, always)
  Definition of assignment: ______________
  Uses any post-index information? [ ] no  [ ] YES → immortal time bias

ESTIMATION
  Estimator: [ ] TMLE [ ] AIPW   Estimate ______  95% CI ______
  Overlap shown [ ] yes   Trimming effect on estimand: ______
  Balance: max SMD ______

REFUTATION
  Negative control outcome (pre-specified): ______  result ______
  Negative control exposure (pre-specified): ______  result ______
  E-value ______  vs strongest MEASURED confounder ______
  [ ] IPCW sensitivity  [ ] capture rate by arm  [ ] active comparator re-run

OUTPUT
  Verdict: [ ] meets standard [ ] material gap [ ] blocking gap
  GAP TABLE: gap ______  severity ______  closable with existing data? [ ] y [ ] n
  P(acceptance) = ____%   prior: precedent base rate ______  band: ______
```

→ Detail: [`F-regulatory-strategy.md`](F-regulatory-strategy.md) ·
[workflow](../references/workflows-all-stages.md#stage-4)

---

## Stage 5 — Commercial {#stage-5}

```
ENGAGEMENT:     ______________________________
INTERVENTION:   ______________  OUTCOME: ______________

CAUSAL QUESTION
  Did ______ cause ______ , and for which territories/prescribers?
  Estimand: [ ] ATT (did it work)  [ ] CATE (where to spend next)
  NOTE: ranking by predicted RESPONSE instead of UPLIFT overstates ROI.

DATA (Subagent 6)
  Market potential measurable? [ ] no → G1 Must-Have, design around it
  Forecast vintages archived? [ ] yes [ ] no → cannot test the forecast
  Logged-intent vs delivered contact validated? [ ] yes [ ] no

IDENTIFICATION
  Design: [ ] staggered geographic DiD [ ] synthetic control [ ] uplift [ ] holdout
  Estimator for staggered: [ ] Callaway–Sant'Anna [ ] TWFE (BIASED — do not use)
  Assumed spillover radius: ______________

ESTIMATION
  Estimate ______  95% CI ______   Event-study path: ______
  UPLIFT SEGMENTS   persuadables ____  sure things ____
                    lost causes ____   SLEEPING DOGS ____

REFUTATION
  [ ] pre-trend/leads  [ ] placebo-in-time  [ ] placebo-in-space
  [ ] Qini on held-out [ ] spillover sensitivity
  [ ] FORECAST BACKTEST by vintage  [ ] measure–construct gap

OUTPUT
  Recommendation: ______________   Confidence score: ____
  P(incremental return > threshold) = ____%   prior: ______  band: ______
  Monitoring: untargeted proxy ______  cadence ______
```

→ Detail: [`G-commercial-strategy.md`](G-commercial-strategy.md) ·
[workflow](../references/workflows-all-stages.md#stage-5)

---

## Stage 6 — Portfolio / BD {#stage-6}

```
ENGAGEMENT:     ______________________________
ASSETS IN SCOPE: ______________________________

TWO ESTIMANDS — do not merge
  1 Asset value:      E[value | success] × P(success)   (forecast w/ causal input)
  2 Deal–innovation:  ATT of deal activity on innovation  (needs instrument)

DATA (Subagent 6)
  Entry cohort reconstructed (incl. failures)? [ ] yes [ ] no → survivorship
  Disclosure rate by size band: ______   bias direction: ______
  Must-Have gaps: ______________________________

PER-ASSET SCORECARD
  asset ______  P(success) ____  prior source ______  band ______
                conditional value ______  EV ______
                RUNG OF WEAKEST INPUT ____  ← the ranking inherits this

REFUTATION
  [ ] out-of-sample valuation backtest  [ ] survivorship corrected
  [ ] prior sensitivity — does the ranking REORDER? [ ] no [ ] yes
  [ ] capital-cycle adjusted across vintages  [ ] winner's-curse adjusted
  [ ] "success" definitions harmonized across benchmark sources

CAUSAL DUE DILIGENCE (top asset)
  Target causal for disease?      ______  rung ____
  Preclinical package translates? ______  rung ____
  Claimed population developable? ______  rung ____
  What would falsify the case?    ______________________

OUTPUT
  Ranking: ______________   stable across band? [ ] yes [ ] no
  P(asset clears threshold) = ____%   band: ______
```

→ Detail: [`H-portfolio-strategy.md`](H-portfolio-strategy.md) and
[`I-deal-analysis.md`](I-deal-analysis.md) ·
[workflow](../references/workflows-all-stages.md#stage-6)

---

## Stage 7 — Platform / Digital {#stage-7}

```
ENGAGEMENT:     ______________________________
PLATFORM:       ______________  OUTCOME: ______________

CAUSAL QUESTION
  Does adoption of ______ cause ______ ?
  Estimand: ATT on [ ] cycle time [ ] throughput [ ] success rate

DATA (Subagent 6)
  Adoption date by team: ______
  USAGE TELEMETRY (not adoption status): [ ] yes [ ] no → G2 Must-Have
  Pre-period capability by cohort: ______
  Concurrent changes (reorg, headcount, mix): ______________

IDENTIFICATION
  Design: staggered adoption DiD with team fixed effects
  Estimator: [ ] Callaway–Sant'Anna [ ] TWFE (BIASED — do not use)
  Spillover via shared staff: ______________

ESTIMATION
  Estimate ______  95% CI ______   Event-study path (learning dip?): ______
  Causal ROI = (effect × value/unit × volume − TCO) / TCO = ______
  TCO includes licence + integration + training + maintenance + learning dip.

REFUTATION — conditional activation is the strongest test here
  Group A adopted+used:     effect ______  (expect effect)
  Group B adopted+NOT used: effect ______  (expect ZERO — negative control)
  Group C never adopted:    effect ______  (expect zero)
  [ ] bottleneck MOVED (process mining)  [ ] pre-trend clean
  [ ] concurrent-change audit  [ ] selection-into-adoption check

OUTPUT
  Recommendation: [ ] expand [ ] hold [ ] sunset [ ] renegotiate
  Confidence score: ____   P(ROI > threshold) = ____%   band: ______
  Monitoring: activation rate ______  bottleneck location ______
```

→ Detail: [`K-technology-assessment.md`](K-technology-assessment.md) and
[`J-value-chain.md`](J-value-chain.md) ·
[workflow](../references/workflows-all-stages.md#stage-7)

---

## Glossary {#glossary}

Terms used across the bundle. Full treatment in
[`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md).

| Term | Definition |
|---|---|
| **AIPW** | Augmented inverse probability weighting; doubly robust estimator |
| **ATE / ATT / ATU** | Average treatment effect, on the treated, on the untreated |
| **Backdoor criterion** | Condition under which an adjustment set identifies an effect |
| **CATE** | Conditional average treatment effect; effect for a covariate-defined subgroup |
| **CDIP** | Causal Decision Intelligence Process; this skill's 6-phase pipeline |
| **Circularity** | A forecast input derived from the output it is used to validate |
| **Collider** | Common effect of two variables; conditioning on it induces association |
| **Colocalization** | Test of whether one shared causal variant explains two signals |
| **Confounding by indication** | Treatment chosen because of prognosis |
| **DAG** | Directed acyclic graph encoding causal assumptions |
| **DiD** | Difference-in-differences |
| **DML** | Double machine learning; cross-fitted residual-on-residual estimation |
| **Doubly robust** | Consistent if *either* outcome or treatment model is correct |
| **E-value** | Minimum confounder strength needed to explain away an effect |
| **Estimand** | The quantity to be estimated, specified before choosing an estimator |
| **Exclusion restriction** | Instrument affects outcome only through treatment (untestable) |
| **Front-door criterion** | Identification via a fully mediating, unconfounded mediator |
| **G1–G8** | This bundle's data-gap taxonomy ([Subagent 6](../subagents/06-active-data-collection-designer.md#3-step-2--dag-driven-gap-analysis-g1g8-taxonomy)) |
| **Goodhart's Law** | A metric used as a target ceases to measure its construct |
| **ICH E9(R1)** | Regulatory estimand framework; five required attributes |
| **Immortal time bias** | Treatment defined by an event requiring survival to occur |
| **Informative censoring** | Dropout related to prognosis |
| **Instrument (IV)** | Variable moving treatment but not otherwise the outcome |
| **ITT** | Intention to treat; effect of assignment rather than receipt |
| **LATE / CACE** | Local / complier average causal effect |
| **LD** | Linkage disequilibrium; correlation between nearby genetic variants |
| **MR** | Mendelian Randomization; genetic instrumental variables |
| **MR-Egger** | MR estimator whose intercept tests directional pleiotropy |
| **NDE / NIE** | Natural direct / indirect effect in mediation |
| **Negative control** | Outcome or exposure that cannot causally be affected |
| **Overlap / positivity** | Every covariate stratum has non-zero probability of both arms |
| **Pleiotropy** | A variant affects the outcome other than through the target |
| **pQTL / eQTL** | Genetic variant associated with protein / expression level |
| **Refutation** | Battery of tests attacking an estimate's assumptions |
| **Reflexivity** | A forecast changing the behavior it forecasts |
| **Rung 1 / 2 / 3** | Association / intervention / counterfactual (Pearl's ladder) |
| **Rung laundering** | Passing a Rung 1 input through a model to present a Rung 2 claim |
| **Simpson's paradox** | Aggregate association reverses within every stratum |
| **Sleeping dogs** | Units that act only if *not* treated; targeting them destroys value |
| **SUTVA** | Consistency plus no interference between units |
| **Survivorship bias** | Sample contains only those that survived to be observed |
| **Synthetic control** | Weighted donor combination matching a treated unit's pre-period |
| **Target trial emulation** | Specifying the hypothetical RCT, then emulating it in observational data |
| **TMLE** | Targeted maximum likelihood estimation |
| **Triangulation** | Agreement across designs with different failure modes |
| **Uplift modeling** | Estimating who responds *because of* the intervention |

---

**Related:** [`all-report-templates.md`](all-report-templates.md) · [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md) · [`../subagents/all-subagents.md`](../subagents/all-subagents.md)
