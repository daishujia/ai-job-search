# Subagent 3 — Biological & Translational Analyst

**Scope fixed by** SKILL.md §4.

| Attribute | Assignment |
|---|---|
| **Data types** | GWAS, pQTL, Perturb-seq, omics, biomarker data, PK/PD |
| **Causal methods** | Mendelian Randomization, colocalization, causal mediation, causal discovery (NOTEARS/PC) |
| **Confounding specialties** | Pleiotropy, LD artifacts, reverse causation, cross-species non-translatability |
| **Primary stages** | 1 (Target Discovery), 2 (Preclinical) |
| **Primary categories** | C (Target Validation), D (Translational Assessment) |

---

## 1. When to route here

Route here when the question is **mechanistic**: does this target cause this disease,
will this biomarker carry the effect, does the animal result mean anything for humans.
Clinical effect magnitude routes to Subagent 2; evidence-standard questions to
Subagent 4.

---

## 2. Data inventory

| Source | Contains | Access | Known limitations |
|---|---|---|---|
| GWAS Catalog, Open Targets Genetics | Variant–trait associations | Open API | Ancestry skew toward European cohorts |
| UK Biobank, FinnGen, All of Us | Genotype + deep phenotype | Application | Healthy-volunteer selection in UKB |
| UKB-PPP, deCODE, Fenland (pQTL) | Protein-level instruments | Summary stats open | Aptamer vs. antibody platform disagreement |
| GTEx, eQTLGen (eQTL) | Expression instruments by tissue | Open | Bulk tissue averages over cell types |
| DepMap, Perturb-seq atlases | CRISPR/perturbation phenotypes | Open | Cell-line context ≠ patient tissue |
| PK/PD study data | Exposure, engagement, biomarker time courses | Internal | Sparse sampling limits mediation analysis |

**Platform caveat.** SomaScan (aptamer) and Olink (PEA) disagree for a meaningful
fraction of analytes. An MR result built on one platform's pQTL should be checked
against the other where available; disagreement is informative about the instrument,
not noise to be averaged away.

---

## 3. Causal methods

### 3.1 Mendelian Randomization

Germline variants are assigned at conception and precede disease onset, which makes
the exclusion restriction more defensible here than in any other observational design.

```r
library(TwoSampleMR)
dat <- harmonise_data(exposure_dat, outcome_dat)     # align effect alleles
res <- mr(dat, method_list = c("mr_ivw",
                               "mr_weighted_median",
                               "mr_egger_regression"))
mr_pleiotropy_test(dat)    # Egger intercept ≠ 0 → directional pleiotropy
mr_heterogeneity(dat)      # Cochran's Q → instruments disagree
run_mr_presso(dat)         # outlier detection and correction
```

Report all estimators. Agreement across IVW, weighted median and MR-Egger is the
evidence; IVW alone is not, because it assumes every instrument is valid.

**Steiger directionality test** guards against reverse causation: the instrument should
explain more variance in the exposure than in the outcome.

### 3.2 Colocalization

MR can be fooled when the variant driving protein level and the variant driving
disease are distinct but in linkage disequilibrium. Colocalization tests whether a
*single shared* causal variant explains both signals.

```r
library(coloc)
res <- coloc.abf(dataset1 = list(pvalues = p_pqtl, N = n1, type = "quant",
                                 MAF = maf, snp = snps),
                 dataset2 = list(pvalues = p_gwas, N = n2, type = "cc",
                                 s = case_fraction, snp = snps))
res$summary["PP.H4.abf"]   # posterior for one shared causal variant
```

Interpretation: high H4 supports a shared variant; high H3 (two distinct variants)
is evidence *against* the MR interpretation even when the MR estimate is significant.
**MR without colocalization is incomplete evidence for a target.**

### 3.3 Causal mediation for translation

Translation is a mediation question: does the exposure→engagement→biomarker chain
carry the effect, and does it have the same structure in humans?

```python
# Natural direct and indirect effects
from dowhy import CausalModel
model = CausalModel(data=df, treatment="dose", outcome="response",
                    common_causes=["age", "weight", "baseline_severity"],
                    mediators=["target_engagement"])
```

Report the **proportion mediated**. If the biomarker carries little of the effect, it
is not the translational bridge, however well it correlates with response.

### 3.4 Causal discovery

Perturb-seq data is interventional, which places structure learning at Rung 2 natively
rather than requiring the faithfulness gymnastics observational discovery needs.

Methods: **PC** (constraint-based), **GES** (score-based), **NOTEARS** (continuous
optimization), **LiNGAM** (non-Gaussian, identifies orientation).

```python
from causallearn.search.ConstraintBased.PC import pc
cg = pc(data, alpha=0.05, indep_test="fisherz")
```

Output is a Markov equivalence class, not a unique DAG. Treat every edge as a
hypothesis requiring confirmation by an identified design.

---

## 4. Confounding specialties

### 4.1 Pleiotropy

A variant affects the outcome through a path other than the target, violating
exclusion.

- **Horizontal (balanced)** — effects in both directions; IVW is roughly unbiased,
  weighted median is robust.
- **Directional** — effects share a sign; IVW is biased. MR-Egger's intercept
  estimates and corrects it.

Report the Egger intercept always. A significant intercept is a finding about the
instrument, and it must appear in the deliverable rather than being suppressed in
favor of the IVW point estimate.

### 4.2 LD artifacts

Two distinct causal variants in LD produce a spurious MR signal. Defenses: clump
instruments to independence (r² < 0.001), run colocalization, and check whether the
signal survives conditioning on the lead variant for the other trait.

### 4.3 Reverse causation

Disease alters protein and expression levels, so a cross-sectional association
between analyte and disease is uninformative about direction. Germline instruments
are the structural defense; Steiger's test is the diagnostic. For non-germline
exposures, temporal ordering in longitudinal samples is the minimum requirement.

### 4.4 Cross-species non-translatability

```
Animal:  Dose ─▶ Exposure ─▶ Engagement ─▶ Biomarker ─▶ Outcome
                                 │
       moderators ───────────────┤ receptor homology, metabolic route,
                                 │ immune repertoire, model construct validity
                                 │
Human:   Dose ─▶ Exposure ─▶ Engagement ─▶ Biomarker ─▶ Outcome
```

Three specific failures:

1. **Exposure mismatch** — comparing at equal dose rather than equal exposure or
   equal target engagement. The most common translational error.
2. **Construct validity** — the model reproduces the phenotype through a different
   mechanism, so effect size in the model is uninformative.
3. **Homology gap** — the target's binding site, expression pattern, or downstream
   wiring differs between species.

**Back-translation check:** does the model reproduce a known human result for an
approved drug in the same class? A model that cannot recover a positive control
should not be used to support a go decision.

---

## 5. Refutation battery for this subagent

| Test | Implementation | Interpretation |
|---|---|---|
| Estimator agreement | IVW vs weighted median vs MR-Egger | Disagreement means pleiotropy |
| Egger intercept | `mr_pleiotropy_test` | ≠ 0 means directional pleiotropy |
| Heterogeneity | Cochran's Q | High Q means instruments disagree |
| Outliers | MR-PRESSO | Result should survive outlier removal |
| Colocalization | H4 vs H3 posterior | High H3 undermines the MR reading |
| Directionality | Steiger test | Failure means possible reverse causation |
| Leave-one-out | Drop each instrument | No single variant should drive the result |
| Positive control | Known target–disease pair | Pipeline must recover it |
| Back-translation | Approved drug in the model | Model must reproduce the human result |

---

## 6. Output contract

1. **Target–disease causal question** with the estimand stated (lifelong modest
   modulation, explicitly distinguished from therapeutic-dose effect).
2. **MR table**: all four estimators, Egger intercept, Q statistic.
3. **Colocalization posterior** (H3 and H4 both reported).
4. **Perturbation confirmation** where the data exists.
5. **Mediation decomposition** with proportion mediated, for translational questions.
6. **Cross-species assumption list** — every assumption that must hold, flagged as
   supported or unverified.
7. **Refutation table** from §5 and an evidence confidence score.

---

## Cross-references

- Methods: [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md#43-genetic-data--mendelian-randomization)
- Stage 1–2 workflows: [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md#stage-1)
- Templates: [`../templates/C-target-validation.md`](../templates/C-target-validation.md), [`../templates/D-translational-assessment.md`](../templates/D-translational-assessment.md)
