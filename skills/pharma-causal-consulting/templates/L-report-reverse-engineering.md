# Template L — Industry Report Reverse-Engineering

| Field | Value |
|---|---|
| **Business question** | Can we rely on this report? |
| **Causal question** | What causal assumptions are hidden in this report, and where do they break? |
| **Conventional approach** | Report summarization — **Rung 1** |
| **Causal upgrade** | Full 5-question diagnostic, confounder mapping, Simpson's paradox detection, circularity check |
| **Subagent** | Run the diagnostic first, then route each identified confounder to its owner — see [router §3](../subagents/all-subagents.md#3-confounding-specialty-map) |
| **Typical stages** | Any |
| **Worked example** | [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md) |

---

## How this template differs

Every other template analyzes a system. This one analyzes **an argument about a system**.
The object of study is the report: its claims, the inferential steps between them, and the
assumptions those steps require. A high-quality report is not one with no assumptions — it
is one whose assumptions are stated and whose conclusions are robust to them.

**Note on stance.** The output is a reliability assessment, not a takedown. Most industry
reports are competent Rung 1 documents; the defect is usually that a Rung 1 finding is
being *used* as a Rung 2 input somewhere downstream. Say where, and say what would fix it.

---

## Phase 1 — Claim inventory and diagnostic

### Step 1: Extract every causal claim

Go chapter by chapter. A causal claim is any statement that an action, policy, or
characteristic produced an outcome — including claims disguised as description
("policy support drove growth", "rising deals reflect strengthening capability").

| # | Claim (verbatim) | Chapter | Implied `X → Y` | **Implied estimand** | Stated rung | Rung actually supported |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

**Writing the implied estimand is the test.** A causal claim commits its author to a
specific quantity — a population, a contrast, and a comparator. Forcing the claim into
estimand form is what exposes whether it is causal at all: if you cannot name the comparator
the claim implies ("compared to what?"), the claim is Rung 1 wearing Rung 2 grammar. Do this
for every claim before assessing any of them.

### Step 2: The 5-Question Diagnostic

Score the report as a whole. One point each; **≥ 3 means causal methods are required**
([methods §8](../references/causal-inference-deep-review.md#8-five-question-diagnostic)).

| Q | Question | Score | Evidence from the report |
|---|---|---|---|
| 1 | Does it claim causation from observed correlation? | | |
| 2 | Is there a plausible unmeasured common cause? | | |
| 3 | Could an aggregate statistic invert under stratification? | | |
| 4 | Is a key input derived from the output it validates? | | |
| 5 | Would a decision change if the causal claim were false? | | |
| | **Total** | **/5** | |

Question 5 gates the effort. A report scoring 4 on questions 1–4 and 0 on question 5 is an
interesting read, not an engagement.

---

## Phase 2 — What the report would have needed

→ Invoke [Subagent 6](../subagents/06-active-data-collection-designer.md) against the
report's own claims.

For each major claim, ask what data would have been required to support it causally, and
whether that data exists at all. This distinguishes three very different verdicts:

| Verdict | Meaning | Implication for the reader |
|---|---|---|
| **Could have been done** | The identifying data existed and was not used | Report understates what is knowable; commission the analysis |
| **Could not have been done** | No identification strategy exists with available data | Report's Rung 1 framing is appropriate; the error is in how it is *used* downstream |
| **Cannot be done at any cost** | G8, structurally unobservable | Permanent limitation; decisions must be robust to both directions |

| Claim # | Data needed | Available? | Gap code | Verdict |
|---|---|---|---|---|
| | | | | |

---

## Phase 3 — Confounder mapping

For each significant claim, draw the DAG the report *implies*, then add the nodes it omits.

```
Report's implied model:        X ──▶ Y

Reconstructed model:      Z ──┬──▶ X ──▶ Y
                              └────────▲
                                       │
                          (omitted common cause)
```

| Claim # | Omitted node | Type | Direction of resulting bias | Owner subagent |
|---|---|---|---|---|
| | | Confounder / Collider / Mediator | Upward / Downward / Unsigned | |

**Sign the bias wherever the structure allows.** "The report omits `Z`" is much weaker than
"the report omits `Z`, and since `Z` raises both `X` and `Y`, the reported association is
an upper bound on the causal effect." The second is actionable; the first is a complaint.

**Route each confounder to its owner** using the
[confounding specialty map](../subagents/all-subagents.md#3-confounding-specialty-map).
Capital-cycle and FX issues go to Subagent 1, Simpson's paradox to Subagent 2, and so on.

---

## Phase 4 — Four structural checks (this template's refutation battery)

Every other template refutes *its own* estimate. Here the object of attack is the report's
argument, so these four checks **are** the refutation battery — the same role Phase 5 plays
elsewhere. Run all four on every report, and record failures as findings.

| Check | Attacks | Analogue in an estimating engagement |
|---|---|---|
| 4.1 Simpson's paradox | Aggregation | Stratified re-analysis |
| 4.2 Circularity | External validity of a forecast | Out-of-sample backtest |
| 4.3 Selection / survivorship | The sample frame | Negative controls, cohort reconstruction |
| 4.4 Rung substitution | The inferential step itself | Assumption sensitivity |

### 4.1 Simpson's paradox detection

Find every aggregate statistic used comparatively, and ask what variable is associated with
both group membership and the outcome.

| Aggregate statistic | Candidate stratifier | Stratified view available? | Inverts? |
|---|---|---|---|
| | | | |

Common stratifiers in pharma reports: target novelty, modality, line of therapy,
registrational status, company size, ancestry.

### 4.2 Circularity check

Trace the derivation of every forecast input back to its source. The signature:

```
Driver analysis ──▶ CAGR assumption ──▶ Forecast ──▶ "validates" driver analysis
      ▲                                                       │
      └───────────────────────────────────────────────────────┘
```

| Forecast input | Derived from | External calibration? | Verdict |
|---|---|---|---|
| | | | Backtested / Not backtestable / Circular |

**The test:** apply the report's methodology to data ending five years earlier and compare
its forecast to what happened. A methodology that cannot be backtested cannot support a
decision, however plausible its narrative.

### 4.3 Selection and survivorship audit

| Question | Finding |
|---|---|
| How was the sample or universe enumerated? | |
| Which entities are absent because they failed or exited? | |
| Is any rate computed on a denominator conditioned on the outcome? | |
| Are only disclosed or published cases included? | |

### 4.4 Rung-substitution audit

The defect that matters most in practice: a Rung 1 finding used as a Rung 2 input.

| Where | Rung 1 finding | Used as | Consequence |
|---|---|---|---|
| | | | |

---

## Phase 5 — Transformation table

For each chapter, show the upgrade path. This is the constructive output — what a causal
version of this report would do differently.

| Chapter | Conventional (Rung 1) | Causal upgrade (Rung 2–3) | Data required | Feasible now? |
|---|---|---|---|---|
| | | | | |

---

## Phase 6 — Reliability assessment & recommendation

**Overall verdict:**

> _[Report is a competent Rung 1 document whose findings are reliable for X and must not be
> used for Y]_ — diagnostic score _[n]_/5

**Claim-level reliability table** — the deliverable the client actually uses:

| Claim # | Reliable as stated? | Safe to use for | **Not** safe to use for |
|---|---|---|---|
| | | | |

**Evidence confidence score** for the report's central conclusion:

| Component | Score /5 | Basis |
|---|---|---|
| Causal Strength | | |
| Actionability | | |
| Robustness | | |
| **Composite** | | |

**Probability-guided recommendation:**

```
Recommendation:  [rely on / rely with adjustments / commission independent analysis]
P(central claim holds causally | available evidence) = [x]%   (prior: [source]; band: [...])
Decision band:   [≥60 / 30–59 / <30]
```

**Prioritized remediation** — what to analyze independently, in order of decision impact:

| Priority | What to analyze | Method | Owner subagent | Why it matters most |
|---|---|---|---|---|
| 1 | | | | |

**Monitoring plan:** which of the report's assumptions to re-test as new data arrives, and
the observable that would falsify each.

---

## Common failure modes when running this template

| Failure | Correction |
|---|---|
| Critiquing the report instead of assessing reliability | Produce the claim-level usable/not-usable table |
| Flagging omitted confounders without signing the bias | Sign the direction wherever the DAG allows |
| Treating all Rung 1 content as defective | Rung 1 is appropriate when identification is impossible; locate the *substitution* |
| Skipping the backtest | It is the only external check on a forecast |
| Not routing confounders to owners | Use the specialty map; each has a specialist treatment |

---

**Related:** all twelve category templates via [`all-report-templates.md`](all-report-templates.md) · worked example: [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md) and [`../case-studies/antibody-bluebook-plan.md`](../case-studies/antibody-bluebook-plan.md)
