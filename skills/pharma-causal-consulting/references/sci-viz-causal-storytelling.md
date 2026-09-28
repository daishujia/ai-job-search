# Sci-Viz Causal Storytelling

How to show causal findings so a decision-maker can act on them: a visual grammar for
causation, seven chart components, three dashboards, and a presentation-outline generator.

**Contents**
1. [Rules that apply to every exhibit](#1-rules)
2. [The visual grammar for causation](#2-grammar)
3. [The seven components](#3-components)
4. [The three dashboards](#4-dashboards)
5. [Storyline articulation](#5-storyline)
6. [Structured presentation outline generator](#6-outline-generator)

---

## 1. Rules that apply to every exhibit {#1-rules}

These are not stylistic preferences. Each one prevents a specific misreading.

| Rule | Why it matters here |
|---|---|
| **One y-axis. Never two scales.** | A dual axis lets the author manufacture a visual correlation between two series — exactly the illusion a causal deliverable exists to dispel. Two measures → two charts, small multiples, or index to a common base. |
| **Identity never by color alone.** | Legend always present for ≥2 series; ≤4 series also directly labeled. DAG node roles carry **shape + label**, with color redundant. |
| **Color follows the entity, not its rank.** | Filtering to fewer series must not repaint the survivors, or the reader re-learns the chart on every interaction. |
| **Status colors are reserved.** | good / warning / serious / critical never double as a series hue, and always ship with an icon + text label. |
| **Every estimate shows its uncertainty.** | A point estimate with no interval invites the reader to treat it as known. Intervals are mandatory on every effect mark. |
| **Rung label on every exhibit.** | A small persistent badge (`Rung 1` / `Rung 2` / `Rung 3`). This is the single highest-value piece of chart chrome in the bundle — it stops Rung-1 findings from being read as causal once the chart is separated from its caption. |
| **Hover layer by default.** | Crosshair + tooltip on line/area; per-mark tooltip on bar/dot/cell. Only a bare stat tile with no plot skips it. |
| **Thin marks, recessive chrome.** | 2px lines, ≥8px markers, 4px rounded data-ends anchored to the baseline, 2px surface gap between adjacent fills, hairline grid. |
| **Dark mode is selected, not flipped.** | Its steps come from the same ramps, validated against the dark surface. |
| **A table view always exists.** | It is the accessibility fallback and the audit trail. |

### Palette

Use the **validated default palette** from the `dataviz` skill unchanged — its palette
reference file, which is external to this bundle and not shipped here. Relevant facts, as
documented there:

- The eight categorical slots clear every adjacent-pair gate in both light and dark.
- Under **all-pairs** viewing (scatter, DAG, small multiples — anything where every pair is
  on screen at once) only the **first three slots** validate: blue `#2a78d6`,
  orange `#eb6834`, aqua `#1baf7a` in light. This is why the DAG grammar below caps
  simultaneous hues at three and puts role on shape.
- Diverging (for effect direction): **blue ↔ red**, neutral gray midpoint.
- Sequential (for magnitude, e.g. confounder strength): single blue hue, light → dark.
- Status: good `#0ca30c`, warning `#fab219`, serious `#ec835a`, critical `#d03b3b`.

**If you substitute a brand palette, re-run the validator**
(`node scripts/validate_palette.js "<hex,…>" --mode light --pairs all`, and again for
`--mode dark`) against your own surfaces. Do not carry the numbers above over to a
different palette.

---

## 2. The visual grammar for causation {#2-grammar}

A DAG is an all-pairs exhibit, so role is carried by **shape and label**, with color as a
redundant channel capped at three hues.

### Node roles

| Role | Shape | Color | Label |
|---|---|---|---|
| Treatment `X` | Filled **square** | series-1 blue | always |
| Outcome `Y` | Filled **circle** | series-2 orange | always |
| Confounder, **adjusted for** | Filled **diamond** | series-3 aqua | always |
| Confounder, **unmeasured** | **Dashed-outline diamond**, texture fill | muted ink | always, + "unmeasured" |
| Mediator `M` | Circle with **inner ring** | muted ink | always |
| Collider | Circle with **slash through** | muted ink | always, + "do not adjust" |
| Instrument `Z` | **Triangle** | muted ink | always |

The unmeasured confounder gets the texture fill because it is the node that decides whether
the estimate means anything; it should be the most visually distinct thing in the figure.

### Edge semantics

| Edge | Rendering | Meaning |
|---|---|---|
| Open causal path | 2px solid arrow | Effect flows |
| Open backdoor path | 2px solid arrow, **critical** status color | Confounding, unblocked |
| Blocked path | 2px arrow with a **small perpendicular bar** at the blocking node | Adjusted away |
| Assumed absent | 1px **dotted**, no arrowhead | An assumption, not an observation |

The blocking bar is what makes an adjustment-set claim legible: the reader can count blocked
paths rather than take the author's word.

### The three-color discipline in practice

A DAG with eight nodes does **not** get eight hues. Treatment, outcome and the adjusted
confounder set take the three validated slots; everything else is muted ink differentiated
by shape. If a figure seems to need a fourth hue, the figure is doing too much — split it
into a base DAG plus an overlay showing one identification strategy at a time.

---

## 3. The seven components {#3-components}

### Component 1 — CDIP process flow & method-selection tree

**Job:** orientation. Shows where in the six phases a finding came from, and why the method
was chosen.

- Form: left-to-right flow, six nodes, current phase emphasized by weight (not by hue).
- The method-selection tree from
  [methods §9](causal-inference-deep-review.md#9-method-selection) rendered as a collapsible
  tree; the taken path is 2px solid, untaken branches are hairline.
- Terminal "do not estimate — report as Rung 1" leaf is styled as prominently as the
  estimating leaves. It is a legitimate outcome, and hiding it biases method choice.

### Component 2 — Interactive DAG with adjustment-set explorer

**Job:** make the identification claim inspectable.

- Base figure per the §2 grammar.
- Clicking a node toggles it into or out of the adjustment set; the figure re-renders
  blocked/open paths and updates a live readout: **"backdoor paths open: n"**.
- Selecting a collider surfaces an inline warning (icon + text, status **serious**):
  conditioning on it induces association.
- Panel beside the figure lists: adjustment set, open paths, untestable assumptions.
- Table view: node, role, measured (y/n), in adjustment set (y/n).

### Component 3 — Simpson's paradox decomposition

**Job:** show an aggregate inverting. The single most persuasive exhibit in the bundle.

- **Two panels side by side, identical y-scale** — the shared scale is what makes the
  inversion undeniable, and a differing scale is the commonest way this exhibit fails.
- Left: aggregate comparison. Right: same comparison stratified.
- Stratum sizes shown as bar widths or as an explicit `n` label, so the reader sees the mix
  shift that drives the reversal.
- A connector line links each aggregate bar to its constituent strata.
- Caption states the stratifying variable and why it is associated with both group
  membership and outcome.

### Component 4 — Ladder of Causation navigator

**Job:** show what the same data supports at each rung.

- Three stacked panels: Rung 1 (association), Rung 2 (intervention), Rung 3
  (counterfactual), sharing one x-axis.
- Each panel states the question form (`P(Y|X)`, `P(Y|do(X))`, `P(Y_x|X=x',Y=y')`), the
  estimate if available, and **"not identified"** where it is not.
- Rungs that are not identified are rendered as an explicit empty state with the reason —
  never omitted, because omission reads as "not relevant" rather than "not knowable."

### Component 5 — CATE waterfall & uplift segments

**Job:** who benefits, and who is harmed by being targeted.

- Waterfall of subgroup effects, sorted by effect size, each bar with its confidence
  interval, `n` labeled.
- Diverging blue ↔ red about a **zero baseline**, gray neutral midpoint — direction is the
  polarity the color encodes.
- The zero line is the strongest mark on the chart, not a gridline.
- Companion four-segment uplift panel: persuadables, sure things, lost causes, **sleeping
  dogs**. Sleeping dogs carry a status **serious** icon + label, since targeting them
  destroys value.
- Calibration inset: predicted vs realized effect by quintile. A flat calibration line means
  the heterogeneity is noise, and this inset is what stops a spurious enrichment strategy.

### Component 6 — DiD parallel-trends event study

**Job:** let the reader judge the identifying assumption instead of accepting it.

- Event-study coefficients on a single axis, x = periods relative to treatment, vertical rule
  at zero.
- **Pre-period coefficients must be visible.** Their being indistinguishable from zero *is*
  the parallel-trends evidence; a chart that starts at treatment hides the assumption.
- Treatment and comparator trajectories shown as a companion two-line panel, directly
  labeled, no legend box needed at two series if both are labeled.
- Placebo-in-time and placebo-in-space results as small multiples beneath, same scale.

### Component 7 — Refutation panel

**Job:** summarize whether the estimate survived attack.

Three linked marks, read left to right:

1. **Sensitivity tornado** — horizontal bars, one per assumption, ordered by how much moving
   it moves the estimate. The assumption that matters most is the top bar.
2. **E-value gauge** — a single-dial meter with the E-value, and a reference tick at the
   **strongest measured confounder**. The tick is the whole point: an E-value without that
   comparison is uninterpretable.
3. **Triangulation radar** — one axis per independent design (MR, RWE, trial), showing
   agreement. Designs with different failure modes agreeing is the evidence.

Every test in the battery appears, including failures. A refutation panel showing only
passed tests is worse than no panel, because it implies a complete battery.

---

## 4. The three dashboards {#4-dashboards}

Shared layout rules: filters in **one row above** the charts; one headline claim per
dashboard; the rung badge and confidence score persistently visible; a table view toggle.

### Dashboard 1 — Executive decision dashboard

For the person making the call. One screen, no scrolling.

```
┌──────────────────────────────────────────────────────────────┐
│  HEADLINE CLAIM                       [Rung 2]  [Conf. 72]   │
├───────────────────────┬──────────────────────────────────────┤
│  Hero number:         │  Recommendation card                 │
│  effect + interval    │  · action                            │
│                       │  · P(outcome > threshold) = x%       │
│                       │  · decision band                     │
├───────────────────────┴──────────────────────────────────────┤
│  Counterfactual: World A vs World B  (two stat tiles)        │
├──────────────────────────────────────────────────────────────┤
│  Refutation summary (Component 7, compact)                   │
├──────────────────────────────────────────────────────────────┤
│  Monitoring plan: falsifier · threshold · review date        │
└──────────────────────────────────────────────────────────────┘
```

The hero number is a **stat tile with an interval**, never a bare figure. The monitoring row
is not optional — it is what makes the recommendation revisable rather than an assertion.

### Dashboard 2 — Evidence confidence dashboard

For the analyst or reviewer auditing the work.

- Three gauges: Causal Strength, Actionability, Robustness, plus the composite.
- Beside each gauge, the **basis text** — the score alone is not auditable.
- Full refutation battery as a table: test, result, verdict.
- Gap table from Subagent 6 with G1–G8 codes, Must-Have gaps flagged status **critical**.
- Rung badge, and the rung of every upstream input (this is where **rung laundering** is
  caught: a Rung 2 conclusion with a Rung 1 input is visible here and nowhere else).

### Dashboard 3 — Competitive intelligence dashboard

For comparing claims across competitors or assets.

- One row per competitor/asset; columns are evidence dimensions.
- Cells carry a **sequential** blue ramp for evidence strength (magnitude, one hue) plus a
  numeric label — never color alone.
- Sortable by any dimension; **color stays attached to the entity** when sorted.
- Expanding a row reveals that entity's DAG and refutation panel.
- Explicit "no evidence located" state, visually distinct from "evidence located, weak."
  Conflating absence of evidence with weak evidence is the failure mode this state prevents.

---

## 5. Storyline articulation {#5-storyline}

### The arc

Every causal deliverable follows the same seven beats:

```
Context → Observation → Causal finding → Confidence/robustness
        → Counterfactual scenarios → Recommendation → Monitoring plan
```

The beat most often dropped is **Confidence/robustness**, and dropping it converts an
estimate into an assertion. The beat most often dropped *second* is the monitoring plan,
which converts a revisable recommendation into a permanent one.

### Executive decision card

One page, and the only artifact many readers will see:

| Element | Content |
|---|---|
| Claim | One sentence, with rung label |
| Effect | Point estimate + interval + the comparator that defines it |
| Confidence | Composite score + the binding weakness |
| Action | What to do |
| Probability | `P(outcome > threshold)` + prior source + sensitivity band |
| If wrong | The falsifier and what it would cost |

### Stakeholder framing

The finding does not change; the emphasis does.

| Audience | Leads with | Needs most |
|---|---|---|
| Investors | Probability and expected value | Prior sensitivity band |
| Regulators | Estimand and identification assumptions | Negative controls, E-value |
| Scientists | Mechanism and DAG | Refutation battery detail |
| Commercial | Segments and uplift | Sleeping-dog segment, monitoring |

Never present a different *number* to different audiences. Present the same number with
different surrounding detail; a table view identical across versions keeps this honest.

---

## 6. Structured presentation outline generator {#6-outline-generator}

Produces a markdown slide outline from any completed report. Two formats.

### Per-slide specification

Every slide, in both formats, specifies five fields:

```
SLIDE n — [Title: the message, not the topic]
  Key message:   [one declarative sentence — what the audience should conclude]
  Data visual:   [component # or chart type] · source: [where the data comes from]
  Layout:        [split | full-bleed | dashboard | text-only]
  Speaker notes: [the assumption or caveat that belongs in the voice, not on the slide]
```

Titles are **messages, not topics**: "Policy effect is an upper bound once capital is
controlled" rather than "Policy analysis." A deck whose titles read in sequence should
convey the argument without the body content.

### Short format — executive, ≤ 15 slides

| # | Slide | Component | Layout |
|---|---|---|---|
| 1 | Title + the decision being made | — | text-only |
| 2 | Executive summary: claim, rung, confidence | Decision card | full-bleed |
| 3 | Context: the decision and what it turns on | — | text-only |
| 4 | What the data shows (association) | Component 4, Rung 1 panel | split |
| 5 | Why association is not enough here | Component 2 (DAG) | split |
| 6 | The causal finding | Component 5 or 6 | full-bleed |
| 7 | Does it survive attack? | Component 7 | dashboard |
| 8 | Counterfactual scenarios | World A/B tiles | split |
| 9 | Recommendation + probability | Decision card | full-bleed |
| 10 | Monitoring plan and falsifier | — | text-only |
| 11–15 | Appendix: estimand, gap table, full battery | tables | full-bleed |

Slides 4 and 5 are the pivot: show the conventional reading, then show why it does not
license the decision. Cutting slide 5 to save time removes the entire argument.

### Long format — technical, unlimited

Full storyline with the arc expanded. Section structure:

| Section | Slides | Content |
|---|---|---|
| A. Context & question | 3–5 | Decision, causal question, estimand (all five ICH attributes if clinical), 5-Q diagnostic |
| B. Data & gaps | 4–8 | Source inventory, gap table with G1–G8, structured dataset specs, infeasible list with signed bias |
| C. Causal model | 3–6 | DAG, adjustment set, assumptions stated individually, positivity |
| D. Estimation | 4–10 | Method and why, estimate with interval, heterogeneity + calibration |
| E. Refutation | 5–10 | Every test, failures included, E-value vs measured confounder, triangulation |
| F. Scenarios | 2–4 | Counterfactuals, each with its falsifier |
| G. Recommendation | 2–3 | Action, probability with prior sensitivity, decision band |
| H. Monitoring | 1–2 | Observables, thresholds, review cadence |
| I. Appendix | as needed | Code, full tables, sensitivity grids |

### Generator procedure

1. Read the completed report's six CDIP phases.
2. Map each phase to its section (Phase 1→A, 2→B, 3→C, 4→D, 5→E, 6→F/G/H).
3. For each finding, select the component from §3 by the finding's **form**: an inverting
   aggregate → Component 3; heterogeneity → Component 5; a policy or rollout effect →
   Component 6; an identification argument → Component 2.
4. Write the title as the key message.
5. Put every caveat in **speaker notes**, not on the slide — except the rung label and the
   confidence score, which are always on the slide.
6. Verify the title sequence reads as the argument. If it does not, the deck's structure is
   wrong, not its wording.

### Checks before shipping a deck

- [ ] Every effect mark carries an interval.
- [ ] Every exhibit carries a rung badge.
- [ ] No dual-axis chart anywhere.
- [ ] Simpson's paradox panels share one y-scale.
- [ ] Event-study charts show pre-periods.
- [ ] The refutation section includes failed tests.
- [ ] The E-value is shown beside the strongest measured confounder.
- [ ] Every ≥2-series chart has a legend; ≤4-series charts are also directly labeled.
- [ ] Dark-mode steps validated against the dark surface, not flipped.
- [ ] A table view exists for every chart.
- [ ] Title sequence alone conveys the argument.
- [ ] The monitoring plan names a falsifier and a review date.

---

## Cross-references

- Methods and estimands: [`causal-inference-deep-review.md`](causal-inference-deep-review.md)
- Stage workflows: [`workflows-all-stages.md`](workflows-all-stages.md)
- Confidence scoring: [`causal-inference-deep-review.md §7`](causal-inference-deep-review.md#7-bayesian-scoring)
- Report structures: [`../templates/all-report-templates.md`](../templates/all-report-templates.md)
- Worked example to present: [`../case-studies/antibody-bluebook-case.md`](../case-studies/antibody-bluebook-case.md)
