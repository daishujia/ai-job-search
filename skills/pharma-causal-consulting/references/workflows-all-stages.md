# Analytical Workflows — All Seven Value-Chain Stages

The CDIP 6-phase pipeline (SKILL.md §1) is generic. This file instantiates it for
each of the seven pharma value-chain stages: what data exists, what the DAG usually
looks like, which identification strategy is available, and what the deliverable is.

Every category template inherits its section skeleton from the phase structure here.

**Contents**
- [How to use this file](#how-to-use)
- [The invariant phase skeleton](#invariant-skeleton)
- [Stage 1 — Target Discovery](#stage-1)
- [Stage 2 — Preclinical](#stage-2)
- [Stage 3 — Clinical](#stage-3)
- [Stage 4 — Regulatory](#stage-4)
- [Stage 5 — Commercial](#stage-5)
- [Stage 6 — Portfolio / BD](#stage-6)
- [Stage 7 — Platform / Digital](#stage-7)
- [Cross-stage failure modes](#cross-stage-failures)

---

## How to use this file {#how-to-use}

1. Identify the stage from the client's question (the table in SKILL.md §3).
2. Read that stage's section here for the data landscape and identification options.
3. Open the matching category template in `../templates/` for the report structure.
4. Route to the subagent named in the stage section.

Stage and category are independent axes. "Market sizing" (Category A) at Stage 1
is a target-opportunity assessment; at Stage 5 it is a launch forecast. Same
category, different data, different identification strategy. The 84-cell matrix in
[`../templates/all-report-templates.md`](../templates/all-report-templates.md)
enumerates the combinations.

---

## The invariant phase skeleton {#invariant-skeleton}

Every stage runs the same six phases. Only the content changes.

| Phase | Question | Output artifact |
|---|---|---|
| 1. Context | What is the causal question, and at which rung? | Question statement + estimand + 5-Q diagnostic score |
| 2. Data design | What do we have, what is missing, what blocks us? | Source inventory + DAG + G1–G8 gap table (Subagent 6) |
| 3. Identification | Can the estimand be written from observables? | Adjustment set + stated assumptions + positivity check |
| 4. Estimation | What is the effect, and for whom? | ATE/ATT/CATE with intervals |
| 5. Refutation | Does it survive attack? | Refutation battery table + E-value |
| 6. Storytelling | What should the client do? | Decision card + dashboard + slide outline |

**Phase 2 is not optional and not a formality.** It is the phase that most often
terminates the engagement honestly — if the must-have variables are unavailable, the
deliverable is a data collection plan, not an effect estimate.

---

## Stage 1 — Target Discovery {#stage-1}

**Causal question.** Does modulating target `T` cause improvement in disease `D`?

**Primary subagent.** [Subagent 3 — Biological & Translational](../subagents/03-biological-translational-analyst.md)

### Data landscape

| Source | Contains | Access |
|---|---|---|
| GWAS Catalog / Open Targets Genetics | Variant–trait associations | Open API |
| UK Biobank, FinnGen, All of Us | Individual-level genotype + phenotype | Application required |
| pQTL studies (UKB-PPP, deCODE, Fenland) | Protein-level instruments | Summary stats open |
| eQTL (GTEx, eQTLGen) | Expression instruments by tissue | Open |
| Perturb-seq / CRISPR screens (DepMap) | Interventional perturbation data | Open |
| Open Targets Platform | Target–disease evidence aggregation | Open API |

### Typical DAG

```
   Confounders: population structure, LD, age, sex
              │
              ▼
   Genotype(Z) ──▶ Target level(T) ──▶ Disease(D)
        │                                 ▲
        └────── pleiotropy ───────────────┘   ← violates exclusion
```

### Identification

Germline variants are assigned at conception and precede disease, giving the
exclusion-restriction plausibility no other observational design has. MR is the
workhorse; colocalization guards against the LD artifact where the genetic signal
for the protein and for the disease come from distinct nearby variants.

### Estimation and refutation

IVW as primary; weighted median and MR-Egger as robustness; MR-PRESSO for outliers.
Report the Egger intercept — a non-zero intercept is direct evidence of directional
pleiotropy. Pair with colocalization posterior (`coloc` H4 probability). Confirm
direction with the perturbation data where it exists (Perturb-seq is interventional,
so it sits at Rung 2 natively).

### Stage-specific traps

- **Lifelong-modest ≠ therapeutic-dose.** MR validates direction and plausibility,
  never effect size for a 12-month drug course.
- **Tissue mismatch.** An eQTL in whole blood is weak evidence for a CNS target.
- **Reverse causation** if using a non-germline exposure — disease alters protein
  levels. Germline instruments are the defense.

### Deliverable

Target validation dossier: MR estimate with all four estimators, colocalization
result, perturbation confirmation, tractability, and a Rung-labeled evidence
confidence score. Template: [`C-target-validation.md`](../templates/C-target-validation.md).

---

## Stage 2 — Preclinical {#stage-2}

**Causal question.** Will preclinical efficacy translate causally to human outcomes?

**Primary subagent.** [Subagent 3 — Biological & Translational](../subagents/03-biological-translational-analyst.md)

### Data landscape

Animal efficacy studies, PK/PD time series, receptor occupancy, toxicology
(organ-level and ADMET panels), ex vivo human tissue, historical translation
success/failure databases by target class and modality.

### Typical DAG — cross-species alignment

```
Animal model:   Dose ─▶ Exposure ─▶ Target engagement ─▶ Biomarker ─▶ Animal outcome
                                          │
                        species-specific  │ (receptor homology, metabolism,
                        moderators ───────┘  immune repertoire, model construct validity)
                                          │
Human:          Dose ─▶ Exposure ─▶ Target engagement ─▶ Biomarker ─▶ Clinical outcome
```

Translation is a **mediation** question: the animal outcome is not the target of
inference. The question is whether the mediating chain (exposure → engagement →
biomarker) has the same structure in humans.

### Identification

Causal mediation analysis on the exposure→engagement→biomarker chain, with the
cross-species moderators made explicit. Where the mediator is fully mediating and
unconfounded, the front-door criterion applies — one of the few genuine front-door
opportunities in the value chain.

### Estimation and refutation

Decompose into natural direct and indirect effects. Estimate the proportion mediated;
a low proportion means the biomarker is not carrying the effect and should not be used
as the translational bridge. Refute with: negative-control biomarker, dose-response
monotonicity check, and back-translation (does the model reproduce a known human
result for an approved drug in the same class?).

### Stage-specific traps

- **Model construct validity.** A model that reproduces the phenotype by a different
  mechanism will translate badly no matter how strong the effect.
- **Exposure mismatch.** Comparing at equal dose rather than equal exposure or equal
  target engagement is the most common translational error.

### Deliverable

Translatability assessment with mediation decomposition and an explicit list of
cross-species assumptions that would have to hold.
Template: [`D-translational-assessment.md`](../templates/D-translational-assessment.md).

---

## Stage 3 — Clinical {#stage-3}

**Causal question.** What is the causal treatment effect, for whom, under what
conditions?

**Primary subagent.** [Subagent 2 — Pipeline & Clinical](../subagents/02-pipeline-clinical-analyst.md)

### Data landscape

ClinicalTrials.gov and EudraCT registries, published results, individual patient
data where licensed, EHR and claims for external comparators, historical
phase-transition rates by indication and modality.

### Typical DAG — target trial emulation

```
Eligibility ─▶ Time zero ─▶ Treatment assignment ─▶ Follow-up ─▶ Outcome
                    ▲              ▲                    │
                    │              │                    ▼
            (must be aligned)  Baseline confounders  Censoring
                                   (severity, prior lines, biomarker status)
```

### Identification

For trial data, randomization identifies ITT directly. For single-arm trials with
external controls, and for any RWE comparison, use **target trial emulation**:
write down the hypothetical randomized trial you would have run, then emulate each
component. The discipline forces the two errors into the open — misaligned time
zero (immortal time bias) and confounding by indication.

Specify the estimand under ICH E9(R1), especially the intercurrent event strategy.

### Estimation and refutation

ITT as primary. CATE via causal forests for heterogeneity — pre-specify the
candidate moderators or treat the analysis as exploratory and say so. Propensity
methods for external comparators, with overlap diagnostics shown, not just claimed.

Refute with negative control outcomes, a placebo-period analysis, and a
quantitative bias analysis for unmeasured confounding (E-value).

### Stage-specific traps

- **Simpson's paradox by target novelty** when pooling across trials: a portfolio of
  me-too assets on validated targets has systematically different success rates than
  first-in-class assets, and aggregate phase-transition rates conceal it.
- **Trial count as a quality proxy.** Counting trials measures activity, not
  probability of success.
- **Informative censoring** when dropout relates to prognosis.

### Deliverable

Clinical development strategy with estimand specification, CATE-based enrichment
recommendation, and a probability-of-success estimate with prior sensitivity.
Template: [`E-clinical-development.md`](../templates/E-clinical-development.md).

---

## Stage 4 — Regulatory {#stage-4}

**Causal question.** Does our evidence meet the causal standard required?

**Primary subagent.** [Subagent 4 — Regulatory & RWE](../subagents/04-regulatory-rwe-analyst.md)

### Data landscape

Regulatory guidance and precedent (approval packages, AdComm transcripts, CRLs),
HTA dossiers and appraisal decisions, EHR/claims/registry RWD, and the sponsor's own
evidence package.

### Identification — the causal roadmap

van der Laan's roadmap, which maps onto what reviewers actually ask:

1. Describe the data-generating process.
2. Specify the statistical model (what is assumed, what is not).
3. Define the target parameter as a functional of the distribution.
4. State the identification assumptions and their plausibility.
5. Choose an estimator matched to the parameter (TMLE for efficiency).
6. Quantify uncertainty, including from the assumptions.

### Estimation and refutation

TMLE or AIPW for RWE comparisons. Pre-specify everything in a protocol before
looking at outcomes — a post-hoc RWE analysis will not survive review. Negative
control outcomes and exposures are the most persuasive robustness evidence for
regulators because they are interpretable without accepting the model.

Report E-values as the standard summary of residual confounding tolerance.

### Stage-specific traps

- **Immortal time bias** in claims-based comparators — the single most common
  fatal defect in submitted RWE.
- **Confounding by indication** where the comparator is a different line of therapy.
- **Data-quality confounding**: completeness of covariate capture differs between
  treated and untreated, so adjustment quality itself is confounded.

### Deliverable

Evidence-standard gap analysis mapped to the roadmap, with a remediation plan per gap
and an assessment of which gaps are closable with existing data versus new collection.
Template: [`F-regulatory-strategy.md`](../templates/F-regulatory-strategy.md).

---

## Stage 5 — Commercial {#stage-5}

**Causal question.** Did our intervention cause the observed market outcome?

**Primary subagent.** [Subagent 5 — Commercial & Strategic](../subagents/05-commercial-strategic-analyst.md)

### Data landscape

Prescription and sales data (IQVIA, Symphony), promotional activity logs, formulary
and payer coverage changes, pricing and gross-to-net, competitor launch timing,
geographic and HCP-level panels.

### Typical DAG

```
   Market potential (unobserved) ──┬──▶ Promotional targeting ──▶ Prescriptions
                                   └──────────────────────────────────▲
                                                                      │
                          Competitor launch, formulary change, season ─┘
```

Promotional targeting is chosen *because* of expected potential. That is
self-selection, and it makes naive attribution mechanically upward-biased.

### Identification

Geographic DiD across markets with staggered rollout (Callaway–Sant'Anna, not
two-way FE). Synthetic control for a single-market launch. Uplift modeling where
some randomization or quasi-randomization exists in targeting. Interference is the
standing threat: competitor response violates SUTVA, so define the unit large enough
to contain spillover.

### Estimation and refutation

Uplift/CATE to find persuadables; report the four-segment decomposition, since
targeting sleeping dogs destroys value. Validate parallel trends on pre-periods and
show the plot. Placebo-in-time and placebo-in-space tests.

### Stage-specific traps

- **Last-click attribution** assigns the whole effect to the final touch.
- **Goodhart's Law / reflexivity**: once a metric becomes the sales target, it
  decouples from the construct.
- **Selection on the dependent variable** when analyzing only successful launches.

### Deliverable

Causal attribution of the launch or campaign with an uplift-ranked targeting
recommendation and an explicit monitoring plan.
Template: [`G-commercial-strategy.md`](../templates/G-commercial-strategy.md).

---

## Stage 6 — Portfolio / BD {#stage-6}

**Causal question.** Which assets maximize causal expected value under uncertainty?

**Primary subagents.** [Subagent 1 — Market Data](../subagents/01-market-data-analyst.md)
and [Subagent 5 — Commercial & Strategic](../subagents/05-commercial-strategic-analyst.md)

### Data landscape

Deal databases (terms, upfronts, milestones), pipeline databases, phase-transition
benchmarks, company financials, patent estates, and analyst forecasts.

### Identification

Two distinct questions get conflated here and must be separated:

1. **Asset value** — a forecasting problem conditioned on success probability. The
   causal input is a *defensible* probability of success, ideally MR-informed at
   target level and phase-transition-informed at development level.
2. **Deal-innovation relationship** — whether deal activity reflects or causes
   innovation. Needs an instrument; global M&A cycles or interest-rate conditions
   are the standard candidates, because they move deal supply without acting on any
   single asset's science.

### Estimation and refutation

CATE-informed prioritization: an asset's value depends on the subpopulation it can
be developed in, so portfolio ranking should use conditional, not average, effects.
Correct for survivorship — the deal database contains completed deals, so inference
about "what makes deals succeed" is conditioned on the outcome.

Refute with out-of-sample backtesting of the valuation model against historical
deals whose outcomes are now known.

### Stage-specific traps

- **NPV with assumed probabilities** dressed as analysis: the probability is where
  all the content lives, and it is usually a benchmark table lookup.
- **Capital-cycle confounding**: deal volume and valuations both track capital
  availability, so cross-sectional comparisons across years are not comparable.
- **Winner's curse** in competitive processes.

### Deliverable

Portfolio ranking with per-asset probability, prior-sensitivity band, and a
causal due-diligence memo per top asset.
Template: [`H-portfolio-strategy.md`](../templates/H-portfolio-strategy.md), with
deal-specific analysis in [`I-deal-analysis.md`](../templates/I-deal-analysis.md).

---

## Stage 7 — Platform / Digital {#stage-7}

**Causal question.** Which technology investments cause R&D acceleration?

**Primary subagent.** [Subagent 1 — Market Data](../subagents/01-market-data-analyst.md)
with process data from [Subagent 5](../subagents/05-commercial-strategic-analyst.md)

### Data landscape

Internal cycle-time and throughput logs, platform adoption timing by team, headcount
and spend, project outcomes, vendor benchmarks, and process-mining event logs.

### Identification

Staggered adoption across teams is the natural DiD design, and it is usually
available because platforms roll out unevenly. The threat is that early-adopting
teams differ — they are often the better-resourced or more capable ones, so adoption
is confounded with team quality.

Process mining supplies the mechanism: if the platform is claimed to remove a
bottleneck, the event log should show the bottleneck moving. A cycle-time improvement
with no change in the bottleneck structure is evidence of a confound, not of effect.

### Estimation and refutation

Callaway–Sant'Anna for staggered adoption with team fixed effects. Conditional
activation analysis — the effect should appear only in projects that actually use the
capability, which functions as a built-in negative control (projects that adopted but
could not use it should show no effect).

### Stage-specific traps

- **Technology readiness levels** are a descriptive scale, not an effect estimate.
- **Attribution to the platform** of improvements driven by concurrent reorganization,
  headcount growth, or portfolio mix shift.
- **Selection into adoption** by capability.

### Deliverable

Causal ROI assessment per platform investment with conditional-activation evidence
and a bottleneck-movement check.
Template: [`K-technology-assessment.md`](../templates/K-technology-assessment.md);
supply-chain variants in [`J-value-chain.md`](../templates/J-value-chain.md).

---

## Cross-stage failure modes {#cross-stage-failures}

Four defects appear at every stage and are worth checking by reflex:

| Failure | Signature | Where it bites hardest |
|---|---|---|
| **Circularity** | An input is derived from the output it validates | Stages 5, 6 (forecasts) |
| **Aggregation** | Statistic inverts under stratification | Stages 3, 6 (pooled rates) |
| **Selection** | Sample conditioned on the outcome | Stages 6, 7 (survivors, adopters) |
| **Regime change** | Rung 1 extrapolation used as a Rung 2 answer | All stages |

Each is scored by the 5-Question Diagnostic in
[`causal-inference-deep-review.md`](causal-inference-deep-review.md#8-five-question-diagnostic)
and detected on third-party reports by
[`L-report-reverse-engineering.md`](../templates/L-report-reverse-engineering.md).

---

## Cross-references

- Methods cited throughout: [`causal-inference-deep-review.md`](causal-inference-deep-review.md)
- Data gap design (Phase 2): [`../subagents/06-active-data-collection-designer.md`](../subagents/06-active-data-collection-designer.md)
- Report structures: [`../templates/all-report-templates.md`](../templates/all-report-templates.md)
- Stage-oriented fill-in templates: [`../templates/stage-specific-templates.md`](../templates/stage-specific-templates.md)
