# Report Template Router & the 84-Cell Engagement Matrix

The **index** for the twelve category templates, plus the complete 12 × 7 matrix of
engagement types. Each category's full template is its own file; this file routes to them
and enumerates every category–stage combination.

> Referenced from SKILL.md's File Map as "12-category templates + 84-cell matrix". The
> twelve templates are files `A-…md` through `L-…md`; stage-oriented fill-in-the-blank
> skeletons are in [`stage-specific-templates.md`](stage-specific-templates.md).

---

## 1. The twelve categories

| Code | Category | Causal question | Subagent | Template |
|---|---|---|---|---|
| **A** | Market Intelligence & Sizing | What causes the market to grow? | 1 | [`A`](A-market-intelligence.md) |
| **B** | Pipeline & Competitive Landscape | Which pipelines succeed, and why? | 2 | [`B`](B-pipeline-landscape.md) |
| **C** | Target Validation & Discovery | Does modulating T cause improvement in D? | 3 | [`C`](C-target-validation.md) |
| **D** | Translational & Preclinical | Will preclinical efficacy translate? | 3 | [`D`](D-translational-assessment.md) |
| **E** | Clinical Development Strategy | What is the effect, for whom? | 2 | [`E`](E-clinical-development.md) |
| **F** | Regulatory Strategy & RWE | Does evidence meet the causal standard? | 4 | [`F`](F-regulatory-strategy.md) |
| **G** | Commercial & Market Access | Did our intervention cause the outcome? | 5 | [`G`](G-commercial-strategy.md) |
| **H** | Portfolio & BD Strategy | Which assets maximize causal EV? | 1 + 5 | [`H`](H-portfolio-strategy.md) |
| **I** | Deal Flow & License Analysis | Do deals reflect or cause innovation? | 1 | [`I`](I-deal-analysis.md) |
| **J** | Value Chain & Supply Chain | Which interventions cause cost reduction? | 1 + 5 | [`J`](J-value-chain.md) |
| **K** | Technology & Platform | Which investments cause R&D acceleration? | 1 | [`K`](K-technology-assessment.md) |
| **L** | Report Reverse-Engineering | What assumptions are hidden, and where do they break? | diagnostic first | [`L`](L-report-reverse-engineering.md) |

## 2. Routing to a category

```
What is the client actually deciding?
│
├── Whether to enter / how big is the opportunity        → A
├── Which competitor or pipeline to worry about          → B
├── Whether to start a program on this target            → C
├── Whether to take this program into humans             → D
├── How to design the trial / which population           → E
├── Whether the filing will succeed                      → F
├── Where to spend commercial budget                     → G
├── Which assets to fund, buy, or drop                   → H
├── What deal activity means                             → I
├── Where to intervene in manufacturing / supply         → J
├── Whether a platform investment paid off               → K
└── Whether to trust someone else's report               → L
```

When two categories fit, run the one matching the **decision**, not the one matching the
data. The data determines the subagent; the decision determines the template.

---

## 3. The 84-cell engagement matrix

Twelve categories × seven stages. Each cell gives the engagement, its causal question, and
the primary method. Stages: **1** Target Discovery · **2** Preclinical · **3** Clinical ·
**4** Regulatory · **5** Commercial · **6** Portfolio/BD · **7** Platform/Digital.

### A — Market Intelligence & Sizing

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Target-space opportunity sizing | Does unmet need in this target space cause addressable demand? | Epidemiological decomposition + genetic prevalence |
| 2 | Modality market potential | Does modality choice cause addressable-population expansion? | Scenario modeling with translation priors |
| 3 | Indication sizing by eligibility | Does eligibility breadth cause the treatable population? | Eligibility-cascade decomposition |
| 4 | Label-driven market boundary | Does label scope cause accessible market size? | Precedent DiD on label-expansion events |
| 5 | Launch market forecast | Does market entry cause the observed growth? | Synthetic control on comparable launches |
| 6 | Portfolio-level TAM aggregation | Do overlapping assets cause double-counted demand? | Overlap-corrected aggregation |
| 7 | Platform-enabled market expansion | Does platform capability cause new market access? | Staggered DiD on capability rollout |

### B — Pipeline & Competitive Landscape

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Target crowding assessment | Does crowding cause lower expected returns? | Novelty-stratified competitor census |
| 2 | Preclinical competitive position | Does modality differentiation cause a translation advantage? | Class-matched translation rates |
| 3 | Trial landscape and enrollment competition | Does competing trial density cause enrollment delay? | Site-level DiD on trial density |
| 4 | Approval-probability benchmarking | Does program design cause approval probability? | Propensity matching on program features |
| 5 | Launch sequence and share capture | Does order of entry cause durable share? | Event-study on entry order |
| 6 | Competitive threat ranking | Which competitor programs causally threaten our asset? | Novelty-stratified PoS comparison |
| 7 | Platform-adoption benchmarking | Does competitor platform adoption cause cycle-time advantage? | Public-disclosure event study |

### C — Target Validation & Discovery

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Genetic target validation | Does modulating T cause improvement in D? | MR + colocalization |
| 2 | Perturbation confirmation | Does perturbing T cause the expected phenotype? | Perturb-seq / CRISPR causal discovery |
| 3 | Target engagement–outcome link | Does engagement cause clinical benefit? | Mediation on engagement → outcome |
| 4 | Genetic evidence in the filing | Does genetic support strengthen the causal case? | Precedent review + E-value framing |
| 5 | Biomarker-defined population value | Does target expression cause differential response? | CATE by biomarker status |
| 6 | Target-level due diligence | Is the licensor's target claim causal? | Independent MR replication |
| 7 | Target-discovery platform validation | Does the platform cause better target selection? | Conditional activation on platform-derived targets |

### D — Translational & Preclinical Assessment

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Model selection for a new target | Does this model causally represent human biology? | Cross-species DAG alignment |
| 2 | Translatability assessment | Does preclinical efficacy translate? | Causal mediation + back-translation |
| 3 | Dose and exposure selection | Does exposure cause target engagement at the proposed dose? | PK/PD mediation |
| 4 | Nonclinical package adequacy | Does the package causally support the proposed dose? | Precedent gap analysis |
| 5 | Biomarker strategy for launch | Does the biomarker mediate response in humans? | Proportion-mediated estimation |
| 6 | Preclinical due diligence | Are the licensor's animal data translatable? | Independent assumption audit |
| 7 | Translational platform ROI | Does the platform cause better translation rates? | Staggered DiD on program outcomes |

### E — Clinical Development Strategy

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Clinical hypothesis from genetics | Does genetic evidence predict the clinical estimand? | MR-informed effect prior |
| 2 | First-in-human design | Does the design causally isolate the safety signal? | Estimand specification + simulation |
| 3 | Pivotal design and enrichment | What is the effect, for whom? | Target trial emulation + causal forest CATE |
| 4 | Estimand alignment with the agency | Does the estimand match the regulatory question? | ICH E9(R1) attribute mapping |
| 5 | Label-supporting subgroup strategy | Does the subgroup effect causally differ? | Pre-specified CATE with calibration |
| 6 | Development-plan valuation input | Does the design choice cause higher PoS? | Design-matched transition rates |
| 7 | Trial-execution platform impact | Does the platform cause faster enrollment? | Site-level staggered DiD |

### F — Regulatory Strategy & RWE

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Evidence standard for a novel target | What causal standard will a first-in-class target face? | Precedent review incl. CRLs |
| 2 | Nonclinical evidence sufficiency | Does the package meet the causal standard? | Causal roadmap gap analysis |
| 3 | External control arm feasibility | Can RWD causally substitute for a control? | Target trial emulation + overlap |
| 4 | Submission readiness assessment | Does our evidence meet the standard? | Full causal roadmap + E-value |
| 5 | Post-approval commitment design | Will the study causally answer the agency's question? | Estimand + power under assumptions |
| 6 | Regulatory risk in diligence | Does the target's regulatory path carry unpriced risk? | Precedent base rates |
| 7 | RWD infrastructure assessment | Does the data asset causally support submission-grade analysis | Fitness-for-purpose audit |

### G — Commercial & Market Access

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Early commercial viability | Does the target profile cause payer acceptability? | Analogue-based scenario modeling |
| 2 | Target product profile testing | Does profile attribute X cause preference? | Conjoint with causal framing |
| 3 | Payer evidence planning | Does the endpoint cause coverage decisions? | HTA precedent analysis |
| 4 | Launch access strategy | Does formulary position cause uptake? | Coverage-change DiD |
| 5 | Campaign and launch attribution | Did our intervention cause the outcome? | Geographic DiD + uplift modeling |
| 6 | Revenue forecast for valuation | Does the forecast survive reflexivity? | Vintage backtest + scenarios |
| 7 | Digital-channel effectiveness | Does digital promotion cause incremental scripts? | Uplift on quasi-random exposure |

### H — Portfolio & BD Strategy

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Target-portfolio construction | Which targets maximize causal EV? | MR-informed PoS across targets |
| 2 | Preclinical portfolio triage | Which programs causally warrant advancement? | Translation-prior ranking |
| 3 | Clinical portfolio prioritization | Which programs maximize causal EV? | CATE-informed value + PoS |
| 4 | Regulatory-risk-adjusted ranking | Does regulatory path change the ranking? | Precedent-adjusted PoS |
| 5 | Launch-portfolio resourcing | Where does resourcing causally pay off? | Uplift across assets |
| 6 | Asset acquisition decision | Does this asset maximize causal EV? | Causal due diligence + backtested valuation |
| 7 | Platform-vs-asset capital allocation | Does platform investment cause more value than assets? | Causal ROI comparison |

### I — Deal Flow & License Analysis

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Target-space deal intensity | Does deal activity reveal target validity? | Composition analysis by novelty |
| 2 | Preclinical-stage deal benchmarking | Does early-stage selling signal capital pressure? | Stage-composition trend |
| 3 | Clinical-stage deal comparables | Do comparable terms reflect causal asset quality? | Quality-adjusted comparables |
| 4 | Post-approval deal valuation | Does approval cause the observed term step-up? | Event study on approval dates |
| 5 | Commercial partnership assessment | Does partnering cause higher uptake than going alone? | Matched launch comparison |
| 6 | Deal-market timing | Do capital cycles cause deal terms? | IV with global M&A volume |
| 7 | Platform-deal analysis | Do platform deals cause capability gain? | Post-deal capability event study |

### J — Value Chain & Supply Chain

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Reagent and tool supply risk | Does supplier concentration cause research delay? | Dependency mapping + event study |
| 2 | Preclinical CRO strategy | Does CRO choice cause data quality differences? | Matched vendor comparison |
| 3 | Clinical supply and trial risk | Does supply design cause trial delay? | Process mining on supply events |
| 4 | CMC and process-validation risk | Does process choice cause filing risk? | Deviation-log causal attribution |
| 5 | Commercial manufacturing cost | Which interventions cause cost reduction? | Staggered DiD + bottleneck check |
| 6 | Supply-chain risk in diligence | Does the target's supply chain carry unpriced risk? | Single-point-of-failure audit |
| 7 | Digital supply-chain investment | Does digitization cause resilience gains? | Staggered DiD + process mining |

### K — Technology & Platform Assessment

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Discovery-platform assessment | Does the platform cause better target output? | Conditional activation analysis |
| 2 | Preclinical automation ROI | Does automation cause throughput gains? | Staggered DiD on assay volume |
| 3 | Clinical-trial technology ROI | Does the technology cause faster or cleaner trials? | Site-level staggered DiD |
| 4 | Regulatory-technology assessment | Does the tooling cause fewer submission deficiencies | Deficiency-rate DiD |
| 5 | Commercial-analytics stack value | Does the stack cause better allocation decisions? | Causal ROI on decision quality |
| 6 | Build-vs-buy for capability | Does building cause more value than licensing? | Counterfactual ROI comparison |
| 7 | Enterprise platform ROI | Which investments cause R&D acceleration? | Causal ROI + bottleneck movement |

### L — Report Reverse-Engineering

| Stage | Engagement | Causal question | Primary method |
|---|---|---|---|
| 1 | Target-landscape report audit | Are the target claims causal? | 5-Q diagnostic + MR check |
| 2 | Preclinical white-paper audit | Are translation claims supported? | Assumption audit |
| 3 | Clinical-landscape report audit | Are pipeline comparisons Simpson-safe? | Stratification detection |
| 4 | Regulatory-precedent report audit | Is precedent selection biased toward successes? | Selection audit incl. CRLs |
| 5 | Market report / blue book audit | What assumptions are hidden, and where do they break? | Full diagnostic + circularity check |
| 6 | Banker or analyst model audit | Is the valuation circular? | Vintage backtest |
| 7 | Vendor ROI claim audit | Is the claimed platform effect causal? | Activation and confound audit |

**Matrix total: 12 × 7 = 84 engagements.**

---

## 4. Using a cell

1. Open the **category template** (`A`–`L`) — it supplies the six-phase structure.
2. Open the **stage section** in
   [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md) — it
   supplies the data landscape, typical DAG, and stage-specific traps.
3. Use the cell's **primary method** as the starting point, and confirm it against the
   [method selection tree](../references/causal-inference-deep-review.md#9-method-selection);
   the cell names the usual choice, but the data decides.
4. Route to the **subagent** in §1, after running
   [Subagent 6](../subagents/06-active-data-collection-designer.md).

The category template is the skeleton and the stage section is the content. Neither alone
is sufficient.

---

## 5. What every deliverable contains, regardless of cell

| # | Element | Source |
|---|---|---|
| 1 | Causal question + rung label + estimand | Phase 1 of the template |
| 2 | Gap table with G1–G8 codes | [Subagent 6](../subagents/06-active-data-collection-designer.md) |
| 3 | DAG with omitted-node check | Phase 3 |
| 4 | Effect estimate with comparator stated | Phase 4 |
| 5 | Refutation battery, failures included | Phase 5 |
| 6 | Evidence confidence score | [methods §7](../references/causal-inference-deep-review.md#7-bayesian-scoring) |
| 7 | Probability-guided recommendation + decision band | Phase 6 |
| 8 | Monitoring plan with falsifier | Phase 6 |

A deliverable missing element 5, 7, or 8 is not a CDIP deliverable. Element 8 in particular
is what makes the recommendation revisable rather than a one-time assertion.

---

**Related:** [`stage-specific-templates.md`](stage-specific-templates.md) · [`../subagents/all-subagents.md`](../subagents/all-subagents.md) · [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md)
