---
name: pharma-causal-consulting
description: "Pharma & biotech causal decision intelligence (CDIP) framework. Transforms consulting reports from associational (Rung 1) to interventional/counterfactual (Rung 2-3) via Pearl's Ladder, DoWhy/EconML, Bayesian analysis. 12 categories x 7 R&D stages = 84 engagement types with probability-guided recommendations. 6 subagents: market, pipeline, translational, regulatory, commercial, active data collection. Generates presentation outlines, causal DAGs, evidence-scored reports. Includes report reverse-engineering with Simpson's paradox and confounding detection. Triggers: pharma consultant report, market intelligence, causal analysis, portfolio decision, clinical strategy, RWE, deal flow, pipeline analysis, blue book audit, decision intelligence, data collection design, active learning, Bayesian decision, probability-guided action, competitive intelligence, pricing strategy, target validation."
license: MIT
---

# Pharma Causal Consulting: Full-Stack Intelligence Framework

## Overview

This skill generates **consultant-grade analytical workflows, report templates, and causal inference analyses** for pharmaceutical and biotech decision-making across the full value chain — from target discovery through commercial launch to portfolio strategy. It transforms conventional consulting reports from associational reasoning (Rung 1) to interventional and counterfactual intelligence (Rung 2-3).

**Three integrated capabilities:**
1. **Causal Inference Analysis Engine** — 6 specialized subagents (5 analytical + 1 active data collection designer)
2. **Sci-Viz Storytelling** (causal-enhanced) — Interactive dashboards + structured presentation outlines
3. **Consulting Report Templates** — 12-category × 7-stage portfolio with CDIP logic chains landing to probability-guided actions

> **Core Philosophy**: Every analysis builds a **logic chain** from context-specific data collection → causal DAG construction → estimation → refutation → Bayesian probability scoring → actionable recommendation. The goal is not description but **decision**: what to do, with what probability of success, and what monitoring plan if assumptions fail.

---

## Quick Start

1. **Read this SKILL.md** fully
2. **Identify the consulting category** from the 12-category taxonomy (Section 2)
3. **Identify the pharma stage** from the 7-stage framework (Section 3)
4. **Select the appropriate subagent** from `subagents/` (Section 4)
5. **Invoke Subagent 6** for data collection design before analysis
6. **Load the report template**: `templates/all-report-templates.md` (category-oriented) AND `templates/stage-specific-templates.md` (stage-oriented fill-in-the-blank)
7. **Load analytical workflows**: `references/workflows-all-stages.md` (7-stage pipeline details)
8. **Read causal-viz reference**: `references/sci-viz-causal-storytelling.md` (includes presentation outline generator)
9. **Generate the deliverable** — HTML dashboard + structured report + presentation outline

### File Map
```
pharma-causal-consulting/
├── SKILL.md                                    ← You are here
├── DEVELOPMENT-PLAN.md                         ← Build plan, layout decision, acceptance criteria
├── subagents/
│   ├── all-subagents.md                        ← Router: routing rules + confounder/method ownership
│   ├── 01-market-data-analyst.md               ← Markets, deals, policy impact
│   ├── 02-pipeline-clinical-analyst.md         ← Trials, PoS, treatment effects
│   ├── 03-biological-translational-analyst.md  ← MR, colocalization, translation
│   ├── 04-regulatory-rwe-analyst.md            ← Evidence standards, RWD pathologies
│   ├── 05-commercial-strategic-analyst.md      ← Uplift, attribution, portfolio
│   └── 06-active-data-collection-designer.md   ← Subagent 6: gap analysis (G1–G8), runs FIRST
├── templates/
│   ├── all-report-templates.md                 ← Router + complete 84-cell matrix (12 × 7)
│   ├── stage-specific-templates.md             ← 7 fill-in-the-blank stage skeletons + glossary
│   ├── A-market-intelligence.md                ← Categories A–L: one file each, six CDIP phases
│   ├── B-pipeline-landscape.md
│   ├── C-target-validation.md
│   ├── D-translational-assessment.md
│   ├── E-clinical-development.md
│   ├── F-regulatory-strategy.md
│   ├── G-commercial-strategy.md
│   ├── H-portfolio-strategy.md
│   ├── I-deal-analysis.md
│   ├── J-value-chain.md
│   ├── K-technology-assessment.md
│   └── L-report-reverse-engineering.md
├── references/
│   ├── causal-inference-deep-review.md         ← Method vocabulary: estimands, identification, refutation
│   ├── workflows-all-stages.md                 ← 7-stage analytical pipeline details
│   └── sci-viz-causal-storytelling.md          ← 7 viz components + 3 dashboards + outline generator
└── case-studies/
    ├── antibody-bluebook-case.md               ← Canonical worked example (diagnostic + C1–C4)
    ├── antibody-bluebook-full-analysis.md      ← Chapter-by-chapter transformation
    └── antibody-bluebook-plan.md               ← Causal diagnostic execution plan
```

---

## 1. The Causal Decision Intelligence Process (CDIP)

Every analysis follows a 6-phase pipeline mirroring DoWhy's Model→Identify→Estimate→Refute:

### Phase 1: Context & Question Formulation
- Define the **causal question** (not just the business question)
- Classify on Pearl's ladder: Association / Intervention / Counterfactual
- Specify the **estimand** (what exactly are we estimating?)
- Identify the **5-Question Diagnostic** score (from case study methodology)

### Phase 2: Active Data Collection Design → **Subagent 6**
- **Invoke Subagent 6** (Active Data Collection Designer) for hook-and-loop data strategy
- **Source inventory**: Systematic search across 8 public data categories (clinical, regulatory, financial, deal, genetic, RWE, policy, epidemiology)
- Design the **causal DAG** encoding domain knowledge and assumptions
- Identify **confounders, mediators, instruments, colliders** in the DAG
- **Gap analysis**: Classify each DAG variable as Available / Must-Have Gap / Good-to-Have Gap / Infeasible using G1-G8 taxonomy
- **Structured dataset design**: For Must-Have gaps, propose schemas with variable definitions, collection methods, sample size justification
- Plan **active learning loop**: initial collection → analysis → confidence check → refined collection

### Phase 3: Causal Identification
- Apply backdoor/front-door/IV identification
- Check positivity (overlap)
- Document all causal assumptions explicitly
- Flag HRT-style confounding risks and Simpson's paradox scenarios

### Phase 4: Estimation & Analysis
- Select estimation method matched to data:
  - **RCT data**: Direct comparison with covariate adjustment
  - **Observational/RWE**: DML, TMLE, causal forests, IPW/AIPW
  - **Genetic data**: MR (IVW, weighted median, MR-Egger)
  - **Time-series/policy**: DiD, synthetic control, SCCS
  - **Deal/transaction**: IV analysis with external instruments
- Estimate ATE, ATT, CATE

### Phase 5: Refutation & Robustness
- Random common cause test
- Placebo treatment refutation
- Data subset validation
- E-value and sensitivity analysis
- Triangulation across methods
- **Circularity check**: Does the forecast embed the confounder?

### Phase 6: Causal Storytelling & Visualization
- Translate findings into executive-ready narratives
- Build interactive HTML dashboards via sci-viz-storytelling
- Apply the visual grammar for causation (color-coded DAGs, ladder navigator, CATE waterfalls)
- Generate evidence confidence scores (Causal Strength × Actionability × Robustness)

---

## 2. Twelve Consulting Service Categories

### Category A: Market Intelligence & Sizing
**Question**: What is the market size, and what CAUSES it to grow?
**Conventional**: Bottom-up/top-down extrapolation (Rung 1)
**Causal upgrade**: DiD for policy effects, synthetic control for market entry, circularity detection
**Template**: `templates/A-market-intelligence.md`

### Category B: Pipeline & Competitive Landscape
**Question**: Which pipelines will succeed, and WHY?
**Conventional**: Trial count census, target heatmaps (Rung 1)
**Causal upgrade**: Simpson's paradox decomposition by target novelty, approval probability modeling
**Template**: `templates/B-pipeline-landscape.md`

### Category C: Target Validation & Discovery
**Question**: Does modulating target T CAUSE improvement in disease D?
**Conventional**: GWAS association, differential expression (Rung 1)
**Causal upgrade**: Mendelian Randomization, colocalization, causal discovery from Perturb-seq
**Template**: `templates/C-target-validation.md`

### Category D: Translational & Preclinical Assessment
**Question**: Will preclinical efficacy TRANSLATE causally to human outcomes?
**Conventional**: PK/PD descriptive analysis (Rung 1)
**Causal upgrade**: Causal mediation analysis, cross-species DAG alignment, ADMET causal networks
**Template**: `templates/D-translational-assessment.md`

### Category E: Clinical Development Strategy
**Question**: What is the causal treatment effect, for whom, under what conditions?
**Conventional**: Standard statistical analysis (Rung 1-2)
**Causal upgrade**: Target trial emulation, ICH E9(R1) estimand framework, CATE via causal forests
**Template**: `templates/E-clinical-development.md`

### Category F: Regulatory Strategy & RWE
**Question**: Does our evidence meet the causal standard required?
**Conventional**: Checklist compliance (Rung 1)
**Causal upgrade**: FDA causal framework alignment, van der Laan causal roadmap, E-value analysis
**Template**: `templates/F-regulatory-strategy.md`

### Category G: Commercial & Market Access
**Question**: Did our intervention CAUSE the observed market outcome?
**Conventional**: Last-click attribution, market share tracking (Rung 1)
**Causal upgrade**: Uplift modeling, geographic DiD, synthetic control for launches
**Template**: `templates/G-commercial-strategy.md`

### Category H: Portfolio & BD Strategy
**Question**: Which assets maximize causal expected value under uncertainty?
**Conventional**: NPV with assumed probabilities (Rung 1)
**Causal upgrade**: CATE-informed prioritization, MR-derived success probability, causal due diligence
**Template**: `templates/H-portfolio-strategy.md`

### Category I: Deal Flow & License Analysis
**Question**: Does deal activity REFLECT or CAUSE innovation?
**Conventional**: Deal count time series (Rung 1)
**Causal upgrade**: IV analysis (global M&A cycles as instrument), Granger causality, survivorship correction
**Template**: `templates/I-deal-analysis.md`

### Category J: Value Chain & Supply Chain Intelligence
**Question**: Which supply chain interventions CAUSE cost reduction?
**Conventional**: Porter value chain mapping (Rung 1)
**Causal upgrade**: Causal process mining, staggered DiD for localization impact, bottleneck causal attribution
**Template**: `templates/J-value-chain.md`

### Category K: Technology & Platform Assessment
**Question**: Which technology investments CAUSE R&D acceleration?
**Conventional**: Technology readiness levels (Rung 1)
**Causal upgrade**: Causal ROI measurement, platform value attribution, conditional activation analysis
**Template**: `templates/K-technology-assessment.md`

### Category L: Industry Report Reverse-Engineering
**Question**: What causal assumptions are hidden in this report, and where do they break?
**Conventional**: Report summarization (Rung 1)
**Causal upgrade**: Full 5-question diagnostic, confounder mapping, Simpson's paradox detection, circularity check
**Template**: `templates/L-report-reverse-engineering.md`
**Case study**: `case-studies/antibody-bluebook-case.md`

---

## 3. Seven Pharma Value-Chain Stages

Each consulting category can be applied at any of 7 stages:

| Stage | Focus | Key Causal Question |
|-------|-------|-------------------|
| 1. Target Discovery | Target identification & validation | Does modulating T cause improvement in D? |
| 2. Preclinical | Translational assessment | Will preclinical efficacy translate? |
| 3. Clinical | Trial design & analysis | What is the causal treatment effect? |
| 4. Regulatory | Submission strategy | Does evidence meet causal standard? |
| 5. Commercial | Launch & market access | Did intervention cause market outcome? |
| 6. Portfolio/BD | Asset prioritization | Which assets maximize causal EV? |
| 7. Platform/Digital | Infrastructure investment | Which investments cause R&D acceleration? |

**Matrix**: 12 categories × 7 stages = **84 possible consulting engagements**, each with a specific causal question, method, and template.

---

## 4. Six Specialized Subagents (5 Analytical + 1 Active Data Collection)

### Subagent 1: Market Data Analyst
**File**: `subagents/01-market-data-analyst.md`
**Data types**: Market sizing data, revenue time series, pricing benchmarks, deal transaction databases
**Causal methods**: DiD for policy impact, synthetic control for market entry, IV for deal-innovation relationship
**Confounding specialties**: Capital cycle confounding, FX effects, survivorship bias, circularity detection

### Subagent 2: Pipeline & Clinical Analyst
**File**: `subagents/02-pipeline-clinical-analyst.md`
**Data types**: Clinical trial registries, approval databases, Phase transition data, efficacy/safety endpoints
**Causal methods**: Propensity score matching for approval probability, CATE for HTE, target trial emulation
**Confounding specialties**: Simpson's paradox by target novelty, trial count ≠ quality, selection bias

### Subagent 3: Biological & Translational Analyst
**File**: `subagents/03-biological-translational-analyst.md`
**Data types**: GWAS, pQTL, Perturb-seq, omics, biomarker data, PK/PD
**Causal methods**: Mendelian Randomization, colocalization, causal mediation, causal discovery (NOTEARS/PC)
**Confounding specialties**: Pleiotropy, LD artifacts, reverse causation, cross-species non-translatability

### Subagent 4: Regulatory & RWE Analyst
**File**: `subagents/04-regulatory-rwe-analyst.md`
**Data types**: EHR, claims, registries, RWD, regulatory filings, HTA dossiers
**Causal methods**: TMLE, AIPW, causal roadmap checklist, E-value computation, negative controls
**Confounding specialties**: Immortal time bias, confounding by indication, informative censoring

### Subagent 5: Commercial & Strategic Analyst
**File**: `subagents/05-commercial-strategic-analyst.md`
**Data types**: Sales data, prescription data, promotional activity, deal terms, portfolio financials
**Causal methods**: Uplift modeling (CausalML), geographic DiD, causal attribution, counterfactual scenario modeling
**Confounding specialties**: Self-selection in promotional targeting, Goodhart's Law in forecasting, reflexivity

### Subagent 6: Active Data Collection Designer ★ NEW
**File**: `subagents/06-active-data-collection-designer.md`
**Purpose**: Before analysis begins, designs the data collection strategy — inventories available sources, identifies gaps, and proposes structured datasets for acquisition or generation.
**Capabilities**:
- Public data source inventory (registries, APIs, databases) with access methods
- Gap analysis: Must-Have (blocks analysis) vs. Good-to-Have (enriches) classification
- Structured dataset design with schemas, collection methodologies, variable definitions
- Active learning loop: after initial analysis, identifies where more data most improves confidence
- Hook-and-loop iteration: continuously refines data requirements as questions emerge
**Output**: Context-specific data collection plan + structured dataset specifications

---

## 5. Case Study: Antibody Blue Book Reverse-Engineering

### Summary
The Frost & Sullivan "2026 Global Antibody Drug Industry Development Blue Book" (84 pages) is a high-quality Level 1 (associational) industry report. Our causal analysis reveals:

**5-Question Diagnostic Score: 5/5** — Causal inference methods strongly needed.

### Four Critical Confounders Identified

**C1: Policy-Growth Confounding**
- Claim: "Policy support drove China's antibody market growth"
- Confounder: Global capital inflows independently drove both policy attention AND market growth
- Causal structure: Capital(Z) → Policy(X) AND Market(Y). X-Y correlation partly spurious
- Method: DiD comparing antibody vs. non-antibody approvals pre/post 2017 reform

**C2: License-Out as Innovation Proxy**
- Claim: "Rising license-out = innovation capability strengthening"
- Confounders: Global M&A demand pull, FX dynamics, survivorship bias, early-stage selling as capital pressure signal
- Method: IV analysis using US pharma M&A volume as instrument

**C3: Trial Count ≠ Quality (Simpson's Paradox)**
- Claim: "China's ADC pipeline is world's second-largest" (positive indicator)
- Simpson's paradox: China has 80% trials on validated targets (me-too) vs. US 55% novel targets
- Aggregate statistic inverts when disaggregated by target novelty
- Method: Stratified analysis with target novelty decomposition

**C4: Market Sizing Circularity**
- Driver analysis → CAGR assumptions → Market forecast → "Validates" driver analysis
- No external calibration breaks the circular reasoning
- Method: Out-of-sample backtesting of historical forecasts

### Transformation Demonstrated
The case study shows how each chapter of a conventional blue book can be upgraded:

| Chapter | Conventional (Rung 1) | Causal Upgrade (Rung 2-3) |
|---------|----------------------|--------------------------|
| Market sizing | Bottom-up extrapolation | DiD-adjusted growth + counterfactual scenarios |
| Pipeline census | Trial count rankings | Simpson-decomposed by target novelty |
| Deal analysis | Trend line + top deals | IV-adjusted innovation-deal relationship |
| Pricing | Descriptive comparison | DoWhy DAG isolating clinical value vs. confounders |
| Forecast | Linear CAGR extension | Calibrated models with refutation-tested assumptions |

Reference: `case-studies/antibody-bluebook-case.md` for full methodology.

---

## 6. Sci-Viz Storytelling (Causal-Enhanced)

### Enriched Capabilities

The sci-viz storytelling layer now includes causal inference analysis at every level:

#### 6.1 Causal Logic Workflow Visualization
- **Process flow diagrams** showing the CDIP 6-phase pipeline
- **Decision trees** for method selection based on data type and question type
- **Subagent routing diagrams** matching data to the appropriate analyst

#### 6.2 Causal Model Visualization
- **Interactive DAGs** with click-to-explore identification strategies
- **Confounder mapping panels** showing adjustment sets and blocked paths
- **Simpson's paradox decomposition** — aggregate vs. stratified views side by side

#### 6.3 Estimation & Effect Visualization
- **Ladder of Causation Navigator** — three-panel Rung 1/2/3 comparison
- **CATE waterfall charts** — who benefits most
- **Policy tree visualizations** — optimal decision rules
- **DiD parallel trends plots** — treatment vs. control trajectories

#### 6.4 Robustness & Confidence Visualization
- **Refutation dashboard** — sensitivity tornado + E-value gauge + triangulation radar
- **Evidence confidence architecture** — three-gauge composite scoring
- **Circularity detection diagrams** — showing self-referential forecast structures

#### 6.5 Storyline Articulation
- **Executive decision cards** — one-page causal summaries for C-suite
- **Stakeholder-specific narratives** — different framing for investors, regulators, scientists
- **Counterfactual scenario cards** — "World A vs. World B" comparison panels
- **Competitive intelligence dashboards** — causal evidence scoring across competitors

#### 6.6 Structured Presentation Outline Generator ★ NEW
Produces markdown-formatted presentation outlines from any completed report:
- **Short format** (≤15 slides): Executive summary → Key findings → Decision recommendation
- **Long format** (unlimited): Full storyline with detailed page contents, layout specs, and visual patterns
- Each slide specifies: title, key message, data visual (chart type + data source), layout (split/full/dashboard), and speaker notes
- Storyline arc: Context → Observation (data patterns) → Causal finding → Confidence/robustness → Counterfactual scenarios → Recommendation → Monitoring plan
- Reference: `references/sci-viz-causal-storytelling.md` Section 6

Reference: `references/sci-viz-causal-storytelling.md`

---

## 7. Technology Stack

### Python (Primary)
- **DoWhy** → Model, Identify, Estimate, Refute
- **EconML** → DML, Causal Forests, Meta-Learners, CATE, IV methods
- **CausalML** (Uber) → Uplift modeling, commercial analytics
- **causal-learn** (CMU) → Causal structure discovery
- **statsmodels** → DiD, Granger causality, time-series methods

### R (Biomedical Specialty)
- **TwoSampleMR** / **MendelianRandomization** → Drug target MR
- **grf** → Generalized random forests for HTE
- **tmle3** → Semiparametric efficient estimation
- **dagitty** → DAG specification and testing
- **MatchIt** / **WeightIt** → Propensity methods
- **did** → Callaway-Sant'Anna staggered DiD

### Visualization
- **D3.js** → Interactive causal DAGs, Sankey diagrams
- **Recharts** → Treatment effect forest plots, waterfalls
- **Chart.js** → Market sizing charts, deal flow visualizations
- **Custom HTML/CSS** → Consultant-grade dashboard templates

---

## 8. Cross-Skill Integration

This skill enriches and is enriched by:
- **`mckinsey-presentations`** → Causal storytelling adds rigor to SCQA structure
- **`first-principles-framework`** → Causal thinking IS first-principles reasoning
- **`lit-distiller`** → Extract causal claims from literature for DAG construction
- **`academic-literature-review`** → Systematic causal evidence synthesis
- **`scientific-literature-review`** → Causal gap analysis methodology
- **`omics-network-analysis`** → Network topology → causal structure learning
- **`r-shiny-frontend-design`** → Interactive causal dashboards in R Shiny
- **`code-reverse-engineering`** → Reverse-engineer existing consultant reports
- **`deep-dive-product-architect`** → Causal root-cause analysis for product opportunities
