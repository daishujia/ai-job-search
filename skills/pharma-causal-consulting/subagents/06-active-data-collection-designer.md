# Subagent 6 — Active Data Collection Designer ★

**Scope fixed by** SKILL.md §4. This subagent runs **before** analysis (CDIP Phase 2),
not after it.

| Attribute | Assignment |
|---|---|
| **Purpose** | Design the data collection strategy: inventory available sources, identify gaps, propose structured datasets for acquisition or generation |
| **Capabilities** | Public source inventory with access methods · gap analysis (Must-Have vs Good-to-Have) · structured dataset design with schemas · active learning loop · hook-and-loop iteration |
| **Output** | Context-specific data collection plan + structured dataset specifications |
| **Stages** | All seven |
| **Invoked by** | Every engagement, at Phase 2, before identification |

---

## 1. Why this subagent runs first

Identification is a question about assumptions, and assumptions are claims about
variables. Until the variable inventory is settled, no identification strategy can be
assessed and no estimate can be trusted. Running estimation before this phase produces
the characteristic failure of consulting analytics: a well-computed number answering a
question nobody asked, resting on a variable that was never measured.

This subagent also supplies the honest exit. When a must-have variable is unavailable,
the correct deliverable is a **collection plan**, not an estimate with caveats in a
footnote. That verdict is this subagent's to issue.

---

## 2. Step 1 — Source inventory across the eight public data categories

Search systematically. Each category has characteristic access mechanics and
characteristic biases.

| # | Category | Representative sources | Access | Characteristic bias |
|---|---|---|---|---|
| 1 | **Clinical** | ClinicalTrials.gov, EudraCT/CTIS, WHO ICTRP, published results | Open APIs | Registration ≠ conduct; positive-result publication bias |
| 2 | **Regulatory** | Drugs@FDA, EPAR, PMDA, AdComm transcripts, CRLs | Open | Failures documented far less than successes |
| 3 | **Financial** | Filings (10-K/20-F), central banks, IMF/World Bank | Open | Segment definitions shift between years; FX translation |
| 4 | **Deal** | Cortellis, Evaluate, GlobalData, press releases | Licence + public | Undisclosed terms missing-not-at-random; survivorship |
| 5 | **Genetic** | GWAS Catalog, Open Targets Genetics, UKB-PPP, GTEx, DepMap | Open | Ancestry skew; tissue/cell-type averaging |
| 6 | **RWE** | Claims, EHR, registries, Sentinel, DARWIN EU | Licence / network | Care-delivery generated; missingness tracks prognosis |
| 7 | **Policy** | Reimbursement lists, HTA appraisals, national plans | Public, often non-English | Announced vs effective vs enforced dates differ |
| 8 | **Epidemiology** | GBD, WHO, national cancer registries, surveillance | Open | Ascertainment differs by health-system capacity |

**Record for each source:** what variable it supplies, the access route (API, licence,
application, scraping), granularity, latency, cost, and the bias that comes with it.
A source list without the bias column is an inventory, not a design.

---

## 3. Step 2 — DAG-driven gap analysis (G1–G8 taxonomy)

Walk **every node in the causal DAG**, not every available dataset. The DAG determines
what is needed; availability determines what is obtainable. The gap is the difference,
and it is classified as follows.

| Code | Gap type | Definition | Default class |
|---|---|---|---|
| **G1** | Unmeasured confounder | A common cause of treatment and outcome with no proxy | **Must-Have** |
| **G2** | Weak proxy | A variable measured only through a noisy or partial proxy | Must-Have if it is a confounder; else Good-to-Have |
| **G3** | Coarse granularity | Right variable, wrong resolution (annual when the effect is quarterly; national when the intervention is regional) | Must-Have if it destroys the design's variation |
| **G4** | Coverage gap | Variable exists for part of the population, period, or geography only | Must-Have if the missing part is the treated group |
| **G5** | Latency gap | Variable exists but arrives after the decision date | Good-to-Have; drives interim-analysis design |
| **G6** | Access-restricted | Variable exists and is adequate, but licence, consent or application blocks it | Must-Have if no substitute; cost question, not a science question |
| **G7** | Definitional mismatch | Variable exists under a definition incompatible with the estimand (e.g. "response" defined differently across sources) | Must-Have if it is the outcome |
| **G8** | Structurally unobservable | No instrument, no proxy, not collectable at any cost (counterfactual quantities, private competitor intent) | **Infeasible** |

### Classification rules

- **Must-Have** — the analysis cannot be identified without it. Its absence changes the
  deliverable from an estimate to a collection plan.
- **Good-to-Have** — improves precision, enables a subgroup analysis, or strengthens a
  robustness test, but identification survives without it.
- **Infeasible** — G8, or a G6 whose cost exceeds the decision's value. Must be stated
  in the deliverable as a permanent limitation, with the direction of the resulting
  bias where it can be signed.

### Gap table format

| DAG node | Role | Needed granularity | Best available source | Gap code | Class | Remedy |
|---|---|---|---|---|---|---|
| Capital availability | Confounder | Quarterly, by market | IMF flows (annual) | G3 | Must-Have | Interpolate + validate against central-bank quarterly |
| Target novelty | Effect modifier | Per program | Manual curation | G2 | Must-Have | Structured dataset D-1 (below) |
| Competitor intent | Confounder | — | none | G8 | Infeasible | State as limitation; bias direction unsigned |

**Sign the bias wherever possible.** "We could not measure X" is much less useful than
"we could not measure X, and because X raises both treatment and outcome, our estimate
is an upper bound."

---

## 4. Step 3 — Structured dataset design for Must-Have gaps

For each Must-Have gap, produce a specification precise enough that someone else could
execute it.

### Specification template

```
Dataset ID:        D-n
Closes gap:        [gap code + DAG node]
Unit of observation: [one row is ...]
Population / frame: [inclusion rule, and how the frame is enumerated]
Sample size:       [n, with the justification below]
Collection method: [curation from source X | survey | expert elicitation | licence | primary generation]
Timeline & cost:   [duration, budget band]
Quality controls:  [double-coding with κ, audit sample, source-of-truth rule]
```

### Variable schema

| Variable | Type | Definition (operational) | Permitted values | Source of truth | Missing policy |
|---|---|---|---|---|---|
| `program_id` | string | Registry ID of the lead trial | CTG NCT pattern | ClinicalTrials.gov | Required |
| `target_novelty` | factor | First-in-class if no approved agent against this target at trial start | `first_in_class` / `validated` | Drugs@FDA at start date | Adjudicated by 2 coders |

Definitions must be **operational**: a rule two people apply independently and agree on.
"Innovative target" is not operational; "no approved agent against this target as of the
trial start date, per Drugs@FDA" is.

### Sample size justification

State which of these the number comes from, and show the calculation:

- **Precision** — target CI half-width on the estimand.
- **Power** — minimum detectable effect at stated α and 1−β.
- **Stratum coverage** — smallest subgroup needs `n` for a stable estimate.
- **Saturation** — for qualitative or curation work, the point at which new records stop
  changing the distribution.

A sample size with no stated basis is a budget, not a design.

---

## 5. Step 4 — The active learning loop

Collection is iterative. After each round, ask where the next unit of effort buys the
most confidence.

```
   ┌───────────────────────────────────────────────────────────┐
   │                                                           │
   ▼                                                           │
Collect (round k) ──▶ Analyze ──▶ Confidence check ──▶ Sufficient? ──no──┘
                                       │                  │
                                       │                 yes
                                       ▼                  ▼
                            Where is uncertainty      Deliver estimate
                            concentrated?             + monitoring plan
```

**Confidence check.** Compute the evidence confidence score
([methods §7](../references/causal-inference-deep-review.md#7-bayesian-scoring)).
Route by band:

| Score | Verdict | Next action |
|---|---|---|
| ≥ 60 | Sufficient | Deliver with monitoring plan |
| 30–59 | Marginal | One more targeted round, on the binding constraint only |
| < 30 | Insufficient | Collection plan is the deliverable; no causal claim |

**Where to spend the next round.** Rank candidate collections by expected reduction in
decision uncertainty, not by ease of collection:

1. Does it close a **G1 confounder gap**? Highest value — it changes identifiability
   itself, not merely precision.
2. Does it enable a **refutation test** currently impossible? Second — it changes
   whether the result is believable.
3. Does it shrink the interval around a **decision threshold**? Valuable only if the
   interval currently straddles the threshold. Precision far from the threshold buys
   nothing, because the decision does not change.
4. Does it enable a **subgroup** the decision depends on? Valuable if the recommendation
   is conditional.

This is the step that distinguishes active design from "collect more data": more data
on a variable whose interval is already on one side of the decision threshold has zero
decision value, however cheap it is.

### Hook-and-loop iteration

Each analysis round raises new questions; each new question implies new variables. Keep
a running register so scope growth is visible rather than accidental:

| Round | Question raised | New variable implied | Gap code | Decision |
|---|---|---|---|---|
| 1 | Is the effect driven by a subset of markets? | Market-level policy intensity | G3 | Collect in round 2 |
| 2 | Does the timing suggest anticipation? | Announcement vs effective date | G7 | Closed from public sources |

Stop when either the confidence score clears 60, or the next round's expected decision
value falls below its cost. Say which of the two ended the loop.

---

## 6. Output contract

1. **Source inventory** across the eight categories, each entry with access route and
   characteristic bias.
2. **Gap table** walking every DAG node, with G1–G8 code, class, and remedy.
3. **Structured dataset specifications** for every Must-Have gap, each with schema,
   operational definitions, sample size justification, and quality controls.
4. **Infeasible list** with bias direction signed where possible.
5. **Active learning plan** — round 1 scope, confidence gate, and the ranked candidate
   list for round 2.
6. **Go / no-go verdict on analysis itself**: whether identification is currently
   possible. If not, the collection plan *is* the deliverable.

---

## Cross-references

- Confidence scoring: [`../references/causal-inference-deep-review.md`](../references/causal-inference-deep-review.md#7-bayesian-scoring)
- Where Phase 2 sits in the pipeline: [`../references/workflows-all-stages.md`](../references/workflows-all-stages.md#invariant-skeleton)
- Domain source detail: the data inventory section of each analyst subagent, [`01`](01-market-data-analyst.md) – [`05`](05-commercial-strategic-analyst.md)
