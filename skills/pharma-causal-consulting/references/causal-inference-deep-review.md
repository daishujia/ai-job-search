# Causal Inference Methods — Deep Reference

The method vocabulary for this skill. Every subagent and template cites this file
rather than re-deriving definitions. Organized by the question each method answers,
because method selection is driven by the data-generating process, not by preference.

**Contents**
1. [Pearl's Ladder and what each rung licenses](#1-pearls-ladder)
2. [Estimands: saying precisely what you are estimating](#2-estimands)
3. [Identification strategies](#3-identification)
4. [Estimation methods by data type](#4-estimation)
5. [Refutation and sensitivity](#5-refutation)
6. [Named confounding structures in pharma](#6-confounding-structures)
7. [Bayesian probability scoring for decisions](#7-bayesian-scoring)
8. [The 5-Question Diagnostic](#8-five-question-diagnostic)
9. [Method selection decision tree](#9-method-selection)

---

## 1. Pearl's Ladder {#1-pearls-ladder}

| Rung | Question form | Notation | What it licenses | What it cannot do |
|---|---|---|---|---|
| 1. Association | "What is?" | `P(Y \| X)` | Description, prediction under an unchanged regime | Any claim about the effect of acting |
| 2. Intervention | "What if we act?" | `P(Y \| do(X))` | Policy choice, dose choice, go/no-go | Statements about a specific unit's alternative past |
| 3. Counterfactual | "What if we had acted differently?" | `P(Y_x \| X=x', Y=y')` | Attribution, blame, individual-level "would it have worked for this patient" | — |

**Why the distinction is operationally load-bearing.** A market forecast built by
extrapolating observed growth is Rung 1. It answers "what will revenue be if
everything continues." It does *not* answer "what will revenue be if we enter this
market," because entry changes the regime that generated the data. Consulting reports
routinely present the first as though it answered the second. That substitution is
the single most common defect this skill exists to correct.

**Rung discipline in practice.** Label every claim in a deliverable with its rung.
A Rung 1 claim is not wrong — it is wrong *when used as* a Rung 2 claim. The
transformation table in each category template shows the specific upgrade path.

---

## 2. Estimands {#2-estimands}

An estimand is the quantity you want, stated before you choose an estimator. Naming
it prevents the common failure of computing something well-defined that answers a
different question than the one asked.

| Estimand | Definition | Reads as | Use when |
|---|---|---|---|
| ATE | `E[Y(1) − Y(0)]` | Effect if everyone were treated vs. no one | Population policy, formulary decisions |
| ATT | `E[Y(1) − Y(0) \| T=1]` | Effect among those actually treated | Evaluating a program as delivered |
| ATU | `E[Y(1) − Y(0) \| T=0]` | Effect if the untreated had been treated | Expansion decisions |
| CATE | `E[Y(1) − Y(0) \| X=x]` | Effect for a subgroup defined by `x` | Patient stratification, targeting |
| ITT | Effect of assignment, not receipt | Pragmatic effect including non-adherence | Registrational trials |
| LATE / CACE | Effect among compliers | Effect where the instrument moves treatment | IV designs |

### ICH E9(R1) estimand framework

For clinical work, regulators require five attributes to be specified jointly.
Omitting any one of them makes the estimand ambiguous:

1. **Treatment condition** — the regimen, including what is permitted alongside it.
2. **Population** — including how subgroups are defined.
3. **Endpoint** — the variable, its timing, and its scale.
4. **Intercurrent event strategy** — one of: treatment policy, hypothetical,
   principal stratum, while-on-treatment, composite. This is the attribute most
   often left implicit, and it changes the answer materially.
5. **Population-level summary** — difference in means, hazard ratio, risk difference.

A deliverable that says "we estimated the treatment effect" without these five has
not specified an estimand.

---

## 3. Identification {#3-identification}

Identification asks: given the causal structure, can the target estimand be written
as a function of observable data at all? This is a question about assumptions, not
about sample size. No amount of data rescues a failure here.

### 3.1 Backdoor criterion

A set `Z` suffices to identify `X → Y` if `Z` blocks every path from `X` to `Y` that
starts with an arrow *into* `X`, and `Z` contains no descendant of `X`.

```
Adjustment formula:  P(Y | do(X)) = Σ_z P(Y | X, Z=z) · P(Z=z)
```

**The two errors that matter most:**

- **Under-adjustment** — leaving a common cause out. Biases the estimate, direction
  depends on the signs of the two edges.
- **Over-adjustment** — controlling for a *mediator* (on the causal path) or a
  *collider* (common effect). Conditioning on a collider *creates* association
  where none existed. "Control for everything available" is not a conservative
  choice; it is an active source of bias.

### 3.2 Front-door criterion

When an unmeasured confounder blocks the backdoor, a fully mediating, unconfounded
mediator `M` can still identify the effect:

```
P(Y | do(X)) = Σ_m P(m | X) Σ_x' P(Y | m, x') P(x')
```

Requires: `X → M → Y` with no direct `X → Y`, and no confounding of `M → Y`.
Rare but powerful — PK/PD mediation in translational work is the natural candidate.

### 3.3 Instrumental variables

`Z` is a valid instrument for `X → Y` when:

1. **Relevance** — `Z` actually moves `X` (weak instruments bias badly; check
   first-stage F, conventionally > 10).
2. **Exclusion** — `Z` affects `Y` only through `X`.
3. **Independence** — `Z` is unconfounded with `Y`.

Exclusion is untestable and is where most IV claims fail. State it as an assumption
and probe it with over-identification tests when you have multiple instruments.

### 3.4 Positivity / overlap

Every covariate stratum must have some probability of both treatment values.
Violations are common and often silent: a propensity score with mass near 0 or 1
means the data contain no counterfactual information for those units. Check the
propensity distribution by arm before estimating anything. Trimming restores
positivity but changes the estimand to the overlap population — say so.

### 3.5 Consistency and no-interference (SUTVA)

The treatment must be well-defined ("well-defined intervention"), and one unit's
treatment must not affect another's outcome. Market-level and supply-chain analyses
frequently violate no-interference — competitor response is interference.

---

## 4. Estimation by data type {#4-estimation}

### 4.1 Randomized data

Randomization identifies the effect by design. Covariate adjustment still helps
precision. Pre-specify the adjustment set to avoid garden-of-forking-paths.

### 4.2 Observational / RWE — propensity and doubly-robust methods

| Method | Mechanism | Choose when |
|---|---|---|
| Matching (`MatchIt`) | Pair treated to comparable controls | Few covariates, need transparency for regulators |
| IPW | Weight by inverse treatment probability | Need marginal (ATE) estimand |
| AIPW | Outcome model + IPW combined | Want one-model-wrong protection |
| TMLE (`tmle3`) | Targeted update of initial fit | Efficiency; van der Laan roadmap alignment |
| DML (`EconML`) | Cross-fitted residual-on-residual | Many covariates, ML nuisance models |
| Causal forests (`grf`) | Recursive partitioning on effect | Heterogeneity is the question |

**Double robustness** means the estimate stays consistent if *either* the outcome
model or the treatment model is right. It does not mean both can be wrong.

```python
# DML for a continuous treatment effect with ML nuisance models
from econml.dml import LinearDML
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier

est = LinearDML(
    model_y=GradientBoostingRegressor(),
    model_t=GradientBoostingClassifier(),
    discrete_treatment=True,
    cv=5,
)
est.fit(Y, T, X=X, W=W)
print(est.effect(X_test))
print(est.effect_interval(X_test, alpha=0.05))
```

### 4.3 Genetic data — Mendelian Randomization

Germline variants are randomized at conception and precede disease, so they serve as
instruments for lifelong target modulation. This is the strongest observational
evidence available for target validation.

| Estimator | Assumption about pleiotropy | Role |
|---|---|---|
| IVW | None (all instruments valid) | Primary estimate |
| Weighted median | Valid if >50% of weight is valid | Robustness |
| MR-Egger | Allows directional pleiotropy; intercept tests it | Robustness + bias diagnostic |
| MR-PRESSO | Detects and removes outlier variants | Outlier handling |

```r
library(TwoSampleMR)
dat <- harmonise_data(exposure_dat, outcome_dat)
res <- mr(dat, method_list = c(
  "mr_ivw", "mr_weighted_median", "mr_egger_regression"))
mr_pleiotropy_test(dat)   # MR-Egger intercept: directional pleiotropy
mr_heterogeneity(dat)     # Cochran's Q: instrument disagreement
```

**Interpretation caution.** MR estimates the effect of *lifelong* modest exposure
difference, not of a drug given for 12 months at therapeutic dose. It validates
direction and target plausibility; it does not size the clinical effect.
**Colocalization** should accompany MR — shared causal variant between the pQTL/eQTL
and the disease signal, rather than two distinct variants in linkage disequilibrium.

### 4.4 Policy and time-series — DiD, synthetic control, SCCS

**Difference-in-differences.** Compares pre/post change in a treated group to the
same change in an untreated group. Identifying assumption is **parallel trends** —
absent treatment, both groups would have moved together. Test it on pre-periods;
a pre-trend divergence invalidates the design.

```python
import statsmodels.formula.api as smf
# Two-way fixed effects DiD with cluster-robust inference
m = smf.ols("outcome ~ treated * post + C(unit) + C(period)", data=df).fit(
    cov_type="cluster", cov_kwds={"groups": df["unit"]})
```

**Staggered adoption.** When units are treated at different times, two-way fixed
effects is biased — already-treated units enter the control group with weights that
can be negative. Use Callaway–Sant'Anna (`did` in R) or Sun–Abraham instead.

**Synthetic control.** Builds a weighted combination of untreated units matching the
treated unit's pre-period trajectory. Suited to a single treated unit (one country,
one market entry) with a long pre-period.

**Self-controlled case series.** Each subject is their own control across time
windows. Removes all time-invariant confounding by construction. Good for safety
signals; vulnerable to time-varying confounding and to event-dependent exposure.

### 4.5 Uplift modeling

For commercial targeting, the quantity of interest is not who responds but who
responds *because of* the intervention.

```python
from causalml.inference.meta import BaseXRegressor
from xgboost import XGBRegressor
learner = BaseXRegressor(learner=XGBRegressor())
cate = learner.fit_predict(X=X, treatment=T, y=Y)
# Rank by cate, not by predicted response
```

Four segments: persuadables (act only if treated), sure things (act regardless),
lost causes (never act), sleeping dogs (act only if *not* treated — targeting them
destroys value). Response models cannot distinguish the first two; uplift can.

### 4.6 Causal discovery

When the DAG itself is unknown, structure learning proposes candidates:
**PC** (constraint-based), **GES** (score-based), **NOTEARS** (continuous
optimization), **LiNGAM** (non-Gaussian identification). Perturb-seq data suits
these because perturbations are interventions.

Treat output as hypothesis generation. Discovery recovers a Markov equivalence class,
not a unique DAG, and is sensitive to hidden confounders and to faithfulness.

---

## 5. Refutation and sensitivity {#5-refutation}

Estimation produces a number. Refutation is what earns the right to act on it.
Run the whole battery; report every result including failures.

| Test | Mechanism | Pass looks like |
|---|---|---|
| Random common cause | Add an irrelevant covariate | Estimate unchanged |
| Placebo treatment | Replace treatment with a random variable | Effect collapses to ~0 |
| Data subset | Re-estimate on random subsets | Estimate stable |
| Unobserved common cause | Simulate a confounder of stated strength | Sign survives plausible strength |
| Negative control outcome | An outcome the treatment cannot affect | No effect |
| Negative control exposure | An exposure that cannot affect the outcome | No effect |

```python
refute = model.refute_estimate(identified_estimand, estimate,
                               method_name="placebo_treatment_refuter",
                               placebo_type="permute", num_simulations=100)
```

### E-value

The minimum strength of association an unmeasured confounder would need with both
treatment and outcome to explain away the observed effect.

```
For risk ratio RR > 1:   E-value = RR + sqrt(RR × (RR − 1))
```

An RR of 1.5 gives an E-value of ~2.37: a confounder would need RR ≈ 2.4 with both
exposure and outcome. Judge that against the strongest *measured* confounder — if
something you did measure has RR 3, an unmeasured one plausibly could too.

### Triangulation

Independent designs with *different* failure modes agreeing is stronger evidence than
one design with a tight confidence interval. MR + RWE + trial evidence pointing the
same way is the translational gold standard, precisely because pleiotropy,
confounding by indication, and external validity are unrelated threats.

---

## 6. Named confounding structures in pharma {#6-confounding-structures}

These recur across engagements. Each subagent owns the ones in its domain.

**Immortal time bias.** Treatment defined by an event that requires survival to
occur. The treated group is guaranteed to have survived to that point, so it looks
better for reasons unrelated to treatment. Fix: align time zero for both arms
(target trial emulation).

**Confounding by indication.** Sicker patients get the aggressive drug. Comparing
raw outcomes attributes their prognosis to the drug. Fix: adjust for severity at
baseline, active comparator design.

**Simpson's paradox.** An aggregate association reverses within every stratum.
Arises when stratum membership is associated with both exposure and outcome. Fix:
always disaggregate along the variable that drives selection.

**Survivorship bias.** The sample contains only survivors, so the distribution of
observed outcomes is conditioned on success. Fix: reconstruct the entry cohort.

**Collider stratification.** Selecting on a common effect of exposure and outcome
induces association. Fix: do not condition on post-treatment variables.

**Reverse causation.** `Y → X` rather than `X → Y`. Fix: temporal ordering, MR
(germline variants precede outcomes).

**Circularity.** A forecast's assumptions are derived from the analysis the forecast
is then used to validate. No external information enters, so the model cannot be
wrong. Fix: out-of-sample backtest against forecasts made in prior years.

**Reflexivity / Goodhart's Law.** The forecast changes the behavior it forecasts;
a metric used as a target stops measuring what it measured. Fix: hold out an
untargeted control, monitor the measure–construct gap.

**Capital-cycle confounding.** Macro capital availability drives both policy
attention and market growth, making policy look causal. Fix: instrument or control
for global capital conditions; DiD against a market the policy did not touch.

---

## 7. Bayesian probability scoring {#7-bayesian-scoring}

Decisions need a probability, not a point estimate with a p-value. Report the
posterior probability that the effect exceeds the decision-relevant threshold.

```
P(effect > threshold | data)   — not  P(data | no effect)
```

Specify priors explicitly and from a stated source: historical phase-transition
rates, prior trials in the indication, MR-derived plausibility. Report a
**prior-sensitivity band** — the posterior under skeptical, neutral and enthusiastic
priors — so the reader sees how much the conclusion depends on the prior rather than
the data.

### Evidence confidence score

Composite used throughout the templates:

```
Confidence = Causal Strength × Actionability × Robustness
```

| Component | 1 (low) | 3 (moderate) | 5 (high) |
|---|---|---|---|
| Causal Strength | Association only | Identified with assumptions | Randomized or triangulated |
| Actionability | No lever | Lever exists, indirect | Direct, controllable lever |
| Robustness | Fails refutation | Survives some tests | Survives full battery |

Map to action: **≥ 60** act now; **30–59** act with monitoring plan;
**< 30** collect more data before committing (route to Subagent 6).

---

## 8. The 5-Question Diagnostic {#8-five-question-diagnostic}

Scored on any report or analysis to decide whether causal methods are needed.
One point each; **≥ 3 means causal inference is required, not optional.**

1. **Does it claim causation from observed correlation?** ("policy drove growth")
2. **Is there a plausible unmeasured common cause?** (capital cycle, secular trend)
3. **Could an aggregate statistic invert under stratification?** (mix shift present)
4. **Is a key input derived from the output it is used to validate?** (circularity)
5. **Would a decision change if the causal claim were false?** (stakes)

Question 5 is the gate on effort. A report scoring 4/5 on questions 1–4 but 0 on
question 5 is an interesting read, not an engagement.

---

## 9. Method selection decision tree {#9-method-selection}

```
What kind of data do you have?
│
├── Randomized assignment
│   └── Direct comparison + pre-specified covariate adjustment
│       └── Heterogeneity the question? → causal forest on trial data
│
├── Observational, treatment measured, confounders plausibly measured
│   ├── Need transparency for a regulator? → matching / IPW
│   ├── Many covariates, ML nuisance acceptable? → DML / TMLE
│   └── Effect heterogeneity the question?    → causal forest, policy tree
│
├── Observational, unmeasured confounding likely
│   ├── Valid instrument available?      → IV / LATE
│   ├── Germline genetic instrument?     → MR + colocalization
│   ├── Fully mediating mediator?        → front-door
│   ├── Group + time structure?          → DiD (staggered → Callaway–Sant'Anna)
│   ├── One treated unit, long pre-period? → synthetic control
│   └── None of the above               → do not estimate; report as Rung 1
│                                          and route to Subagent 6
│
└── Structure itself unknown
    └── Causal discovery (PC / GES / NOTEARS / LiNGAM) → hypotheses only,
        then confirm with an identified design
```

The terminal case matters most. When nothing identifies the effect, the correct
deliverable is an explicit Rung 1 label plus a data collection design — not a
causal claim with caveats in a footnote.

---

## Cross-references

- Process that wraps these methods: [`workflows-all-stages.md`](workflows-all-stages.md)
- Analyst specialization by data type: [`../subagents/all-subagents.md`](../subagents/all-subagents.md)
- Communicating results: [`sci-viz-causal-storytelling.md`](sci-viz-causal-storytelling.md)
- Worked application: [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
