# CERTONOMOUS — LAB CAPABILITY STRATEGY
### (performance · intelligence · self-improvement · numerics · probability)

Katie's directive, received 2026-08-08 (evening). Recorded verbatim below the rule; chief
adoption notes at the end. This document is strategy, not a run queue — items enter the docket
through the normal proposal/pricing machinery, each with its measurable proxy attached.

Principle: expertise is proven by solving OUR OWN open problems, not by reading.
Every reading item ends in a reproduction, a tool, or a ruling on a live case.
Every capability gets a measurable proxy so "smarter" is a number, not a feeling.

## 1. SELF-IMPROVEMENT MACHINERY (the lab getting better at getting better)

- [ ] Improvement metrics dashboard (monthly): repeat-incident rate (same lesson
      twice = failure), lessons->preflight conversion rate, median time-to-root-cause,
      % conclusions surviving re-audit, orphaned-run count. Target: all trending right.
- [ ] Calibration scorecard — the lab's SELF-knowledge: every prediction the lab
      makes (cost forecasts, gate pass/fail predictions, interpretation confidence,
      band containment) logged prediction-vs-outcome; quarterly reliability curves.
      Includes the agentic-confidence study (does 70% mean 70%?). Paper-shaped.
- [ ] Charter evolution loop: every charter's "nothing enforces this yet" clause
      becomes a harness task; every incident amends exactly one charter; changelog
      audit that no clause has gone stale (cited by zero decisions in 30 days ->
      review).
- [ ] Knowledge compounding test: quarterly, pick 3 old missions; would today's lab
      solve them faster/cheaper/better? Measure, don't assume. The delta IS the
      learning rate.
- [ ] Post-mortem-to-preflight pipeline SLA: root-caused incident -> executable
      check within 48h, else it escalates.
- [ ] Cross-family lesson propagation: a lesson learned in DAFoam (dead lever)
      must be checked against closure, batch, marine within a week — one agent owns
      the sweep.

## 2. HARD NUMERICS EXPERTISE (become the people who fix solvers, not just run them)

Proven-by list — each expertise counts only when it closes a live problem:
- [ ] Linear solvers & preconditioning: Saad (Iterative Methods, open PDF) working
      group -> PROOF: A3's transonic adjoint conditioned deliberately (diagonal-
      spread diagnosis -> chosen preconditioner -> converged), not by knob-luck.
- [ ] Discretization & stability theory: LeVeque FV book + von Neumann analysis
      toolkit -> PROOF: scheme choices in physics_rules justified by stability
      regions, not folklore; the schemes-knob DAFoam finding explained mechanistically.
- [ ] Adjoint methods deep expertise: Giles & Pierce papers + discrete-adjoint
      consistency theory -> PROOF: the transposed-Jacobian defect written up at
      publishable depth; frozen-turbulence error bounded on one case.
- [ ] Mesh generation science: pyHyp pathology characterized (when does tip
      collapse occur) + alternative-generator matrix -> PROOF: MESH_STANDARD gains
      a generator-selection rule with evidence; birth certificates universal.
- [ ] Convergence & error estimation: Roache/Eca-Hoekstra already in house ->
      extend: goal-oriented (adjoint-weighted) error estimates as a mission
      primitive — the numerics flex almost nobody ships.
- [ ] Time integration: her step-size-resolution closure line enters the lab as a
      research family (LMM->RK order elevation), with the lab reproducing the
      paper's cases. Sanaa's own research becomes lab capability.
- [ ] Weekly "numerics clinic": one open anomaly (F5c 4-12x reattachment, NACA0012
      aspect ratio, temperature-residual signature) gets a theory-first treatment —
      hypothesis from analysis before any run.

## 3. PROBABILITY / UQ EXPERTISE (the moat — nobody else ships this)

- [ ] GP theory to mastery: Rasmussen&Williams (in house) + sparse variational
      lineage (Titsias, Hensman) -> PROOF: the 3x-too-narrow GP error bars fixed
      with a principled method (not inflation), validated on held-out.
- [ ] Bayesian inverse problems: Stuart's acta numerica / Kaipio-Somersalo ->
      PROOF: S1's regularization chosen by theory (prior interpretation), posterior
      uncertainty on beta reported, not just a point field.
- [ ] Calibration & validation theory: Kennedy-O'Hagan framework -> PROOF: model
      discrepancy formally separated from parameter uncertainty on one case
      (the hump is perfect); band-containment campaigns get a scoring rule.
- [ ] Monte Carlo craft: variance reduction (control variates, multilevel MC) ->
      PROOF: one family's band at equal accuracy for measurably fewer solves;
      MLMC using our own mesh ladders as levels (they already exist!).
- [ ] Polynomial chaos maturity: adaptive/sparse PCE beyond order-2 -> PROOF:
      dimension >5 case banded at tractable cost.
- [ ] Rare-event / tail probability: subset simulation basics -> PROOF: one
      "probability of constraint violation" number on a design case (customers ask
      exactly this).
- [ ] Information-theoretic experiment design: expected-information-gain for the
      agenda ranking -> PROOF: proposals ranked by EIG/core-min, beating the
      current heuristic on a lookback test.
- [ ] Probability of rank: before any future leaderboard submission, a posterior
      over our score vs the board (bootstrap over cases) — "P(rank 1) = x%" —
      internal only, but it is the house asking the right question.

## 4. PERFORMANCE (throughput, cost, scale)

- [ ] Cost model v2: per-family scaling laws with confidence bands; forecasts
      auto-approve when 3-for-3 within 20%.
- [ ] Bin-packing scheduler measured: packing efficiency in every morning report;
      target >70% busy-core fraction on batch nights.
- [ ] Spot + checkpoint discipline for ladders (after read-only role lands).
- [ ] Adjoint memory: the r-family per-session protocol written and tested once.
- [ ] Parallel-correctness gate: decomposition-invariance check (np=1 vs np=N)
      required for any NEW solver capability before it ships (A4's lesson as a
      standing gate, cheap version).

## 5. SEQUENCING (what this quarter actually means)

1. Now-to-send: Ladder V only. Nothing above jumps that queue.
2. Post-send month: §3 GP-calibration fix + Kennedy-O'Hagan on the hump +
   S1-with-priors (these three make Stage 2 publishable, not just runnable).
3. Parallel slow-burn: §1 dashboard + calibration scorecard (cheap, compounding).
4. §2 proven-by items ride existing open problems — no new compute, just depth.
5. Quarterly review: the knowledge-compounding test decides what worked.

---

## Chief adoption notes (2026-08-08)

- **Sequencing rule 1 read carefully:** "Now-to-send: Ladder V only" names Ladder V as the ONLY
  path to any send and forbids the strategy items from jumping that queue. It is NOT read as an
  unpark: submissions remain parked until Katie says send. Ladder V stands at V1–V5/V7/V10 PASS;
  the remaining rungs bind to a concrete submission package.
- Items already moving that this strategy absorbs: the pyHyp characterization (§2 mesh science —
  audit f41e969f + the alternative-generator diagnostic), birth certificates (§2 — Infra adoption
  in progress), A3 preconditioning (§2 Saad proof case — the PC-alone convergence 11b90d25 is the
  opening evidence), L-40/lesson machinery (§1 — the cross-family propagation item generalizes
  it), S1 posterior work (§3 Bayesian inverse problems — the weighted arm feeds it).
- Every §2/§3 "PROOF:" clause is docket-shaped: filed through the normal proposal machinery with
  its proxy as the hard criterion. §1 dashboard + calibration scorecard start as slow-burn per
  rule 3.
