# Subagent 2 — Pipeline & Clinical Analyst

**Scope fixed by** SKILL.md §4.

| Attribute | Assignment |
|---|---|
| **Data types** | Clinical trial registries, approval databases, phase transition data, efficacy/safety endpoints |
| **Causal methods** | Propensity score matching for approval probability, CATE for heterogeneous treatment effects, target trial emulation |
| **Confounding specialties** | Simpson's paradox by target novelty, trial count ≠ quality, selection bias |
| **Primary stages** | 3 (Clinical), 6 (Portfolio/BD) |
| **Primary categories** | B (Pipeline & Competitive Landscape), E (Clinical Development) |

---

## 1. When to route here

Route here when the unit of analysis is a **trial, a program, or a patient within a
trial**: what is the treatment effect, who benefits, will this program succeed, how
does this pipeline compare. Target biology routes to Subagent 3; regulatory evidence
standards route to Subagent 4.

---

## 2. Data inventory

| Source | Contains | Access | Known limitations |
|---|---|---|---|
| ClinicalTrials.gov (API v2) | Registrations, design, status, some results | Open | Self-reported; status often stale |
| EudraCT / EU CTIS | EU trials | Open | Partial overlap with CTG, different vocabulary |
| Drugs@FDA, EPAR | Approval packages, review documents | Open | Only successes are documented in detail |
| Phase-transition benchmarks | Historical success rates by phase and indication | Published studies | Definitions of "success" differ between sources |
| Published results / CSRs | Endpoints, subgroups, safety | Mixed | Publication bias toward positive results |
| Individual patient data | Patient-level covariates and outcomes | Licence / consortium | Rarely available for competitors |

**Registry caveat that changes conclusions.** Trial *registration* is not trial
*conduct*. Completed-but-unreported and terminated-but-not-updated records are common.
Any count-based pipeline statistic inherits this noise, and it is not random — it
correlates with sponsor size and country.

---

## 3. Causal methods

### 3.1 Target trial emulation

The organizing discipline for any non-randomized comparison. Write down the randomized
trial you would run, then emulate each component explicitly:

| Component | Specify | Failure if unspecified |
|---|---|---|
| Eligibility | Criteria applied at baseline only | Selection on post-baseline information |
| Time zero | The moment of "assignment" for both arms | **Immortal time bias** |
| Treatment strategies | What each arm receives, and for how long | Ill-defined intervention |
| Outcome | Variable, window, ascertainment | Differential ascertainment |
| Causal contrast | ITT or per-protocol | Estimand ambiguity |
| Analysis plan | Adjustment set, fixed before outcomes | Forking paths |

Misaligned time zero is the defect that most often invalidates an external-comparator
analysis, and it is invisible in the results table.

### 3.2 Propensity methods for approval probability

To ask whether a program characteristic (modality, target novelty, trial design
choice) causes higher approval probability, match programs on the confounders that
drive both the characteristic and success: indication, sponsor capability, year,
line of therapy, endpoint type.

```r
library(MatchIt)
m <- matchit(novel_target ~ indication + sponsor_size + start_year +
               line_of_therapy + endpoint_type,
             data = programs, method = "nearest", caliper = 0.2)
summary(m)          # check balance, not just that it ran
plot(m, type = "hist")   # overlap must be visible
```

Report the standardized mean difference before and after matching for every
covariate. Matching that does not achieve balance has not adjusted for anything.

### 3.3 CATE for heterogeneous treatment effects

```python
from econml.grf import CausalForest
cf = CausalForest(n_estimators=2000, min_samples_leaf=20, random_state=0)
cf.fit(X=X, T=T, y=Y)
tau = cf.predict(X_test)
```

Pre-specify candidate moderators (biomarker status, prior lines, severity) or declare
the analysis exploratory. A causal forest on 40 covariates in a 300-patient trial will
find heterogeneity whether or not it exists; validate on a held-out split and report
the calibration of predicted versus realized effect by quintile.

---

## 4. Confounding specialties

### 4.1 Simpson's paradox by target novelty

The signature finding this subagent exists to catch. An aggregate pipeline statistic
reverses when disaggregated by whether the target is validated or novel.

```
Aggregate:   Region A has more trials than Region B      → "A is ahead"

Stratified:  Validated targets (me-too):   A 80%,  B 55%
             Novel targets (first-in-class): A 20%,  B 45%
                                                     → B leads where it counts
```

The mechanism: target novelty is associated with both the count (me-too programs are
cheaper and more numerous) and the outcome of interest (novel programs carry the
innovation signal). Conditioning is mandatory, not optional.

**Always stratify pipeline counts by:** target novelty, modality, line of therapy,
and whether the trial is registrational.

### 4.2 Trial count ≠ quality

Counting trials measures activity. Activity is an input, and a cheap one. Converting
counts into a capability claim requires an argument that the count is informative
about the outcome — usually it is not, because the marginal trial is the cheapest one.

**Preferred quantities:** first-in-class share, registrational-trial share,
median enrollment per trial, phase-transition rate conditional on novelty.

### 4.3 Selection bias

Three forms recur:

- **Publication bias** — positive results are published faster and more often. Any
  meta-analytic input needs a funnel plot and a small-study-effects test.
- **Survivorship in the pipeline** — programs visible today are those that survived,
  so cross-sectional pipeline quality overstates the cohort's quality.
- **Competing risks** — a program "not approved" may have been discontinued for
  portfolio reasons unrelated to science. Treating discontinuation as scientific
  failure conflates two mechanisms.

---

## 5. Refutation battery for this subagent

| Test | Implementation | Interpretation |
|---|---|---|
| Time-zero sensitivity | Re-run with alternative alignments | Large shifts indicate immortal time bias |
| Balance diagnostics | SMD table pre/post matching | > 0.1 means residual imbalance |
| Overlap | Propensity distribution by arm | Mass near 0/1 means no counterfactual information |
| Negative control outcome | Outcome treatment cannot affect | Effect here means residual confounding |
| Stratified re-analysis | Disaggregate by novelty and modality | Sign flip means Simpson's paradox |
| CATE calibration | Predicted vs realized effect by quintile | Flat calibration means spurious heterogeneity |
| E-value | On the primary estimate | Compare to strongest measured confounder |

---

## 6. Output contract

1. **Estimand under ICH E9(R1)** — all five attributes, intercurrent event strategy
   named explicitly.
2. **Target trial protocol table** for any non-randomized comparison.
3. **Primary estimate** (ITT) with interval, plus CATE if heterogeneity was the question.
4. **Stratified view** of every aggregate pipeline statistic.
5. **Refutation table** from §5.
6. **Probability of success** with prior source stated and a prior-sensitivity band.

---

## Cross-references

- Methods: [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md)
- Stage 3 workflow: [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md#stage-3)
- Templates: [`../templates/B-pipeline-landscape.md`](../templates/B-pipeline-landscape.md), [`../templates/E-clinical-development.md`](../templates/E-clinical-development.md)
- Worked case (C3, Simpson's paradox): [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
