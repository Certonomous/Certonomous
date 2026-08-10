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

### Filing complete (2026-08-10, commit 0d070079) — 19 proposals, all `status: proposed`

All 15 §2/§3 proven-by items plus the 4 remaining §1 machinery items are filed and validated end
to end. Mechanical note: `hard_criterion` is a CLOSED set at intake, so each PROOF clause is
carried verbatim in the proposal's `gate` field (operationalised into a gradeable pass/fail) while
`hard_criterion` carries the hardness answer. That is the right workaround and needs no schema
change; opening the closed list would be Katie's call, and nothing depends on it.

### Fourth dated correction (2026-08-10 night) — §2's first PROOF clause is refuted BY EXECUTION

§2's linear-solvers item reads: *"A3's transonic adjoint conditioned deliberately (diagonal-spread
diagnosis → chosen preconditioner → converged), not by knob-luck."* The arm ran (pre-reg a9bb202d,
choice dda82819, outcome 368996c3) and **the diagnosis route the clause names is a measured dead
end for this case**: rung 2 spreads **14.40 decades and CONVERGES**; rung 3 spreads **14.47 and
cannot**. Seven hundredths of a decade separate a working rung from a walled one, so diagonal
spread does not discriminate here and no preconditioner choice can be derived from it. The 6.2
core-min rung-2 comparison dump that killed the hypothesis was the agent's own idea, aimed at the
hypothesis it most expected to confirm.

What the arm bought instead is an **elimination table**, every entry measured rather than argued:
method breakdown (true residual tracks the recursive one to 7–12 digits through the stall — the
arithmetic is faithful, the operator genuinely offers no progress), subspace size, field separation
(none — extremes flat across all six slots), geometric localisation (none — extremes diffuse, and
LESS near-wing than average, so the tip-TE pathology is not the driver), volume scaling (r = −0.135
across ten decades), spread magnitude, Schwarz overlap (the chosen lever, which failed its own
pre-stated falsifier: κ ratio 0.979/1.062, residual 3% WORSE), and stronger PC application. The
survivor is a negative characterisation carrying a number: **κ ≈ 10¹¹, insensitive to every
preconditioner parameter this build exposes.**

**The finding that outranks the failed clause:** the remedies the evidence now points to — a
two-level coarse space, `PCFIELDSPLIT`/`PCGAMG`, `lgmres`/`dgmres` — are **unreachable in this
build**, because DAFoam's `KSPSetType`/`PCSetType` calls override `KSPSetFromOptions`. The
diagnosis therefore terminates not in a wrong answer but in a **capability boundary**, and that
boundary is itself a reportable upstream defect of the same diagnosability family the defect report
already documents.

**Chief re-phrasing of the clause, replacing the original:** *conditioning diagnosed to a stated
mechanism and the chosen remedy either applied or shown unreachable, with the elimination table
published either way.* The proof is not "we made it converge"; it is "we know what it is and what
it would take", which this arm has half-delivered and which the upstream-reachability question
completes. The original clause is retained above, unedited, per L-44.

### Three dated corrections to this document, found while filing it

The strategy was written from the record as it stood on 2026-08-08 morning; three of its premises
moved that same day, and the corrections belong beside them rather than in a quiet edit:

1. **§2's numerics-clinic agenda item "F5c 4-12x reattachment" is RETRACTED by our own record**
   (2026-08-08, commits fe121af2 / 6d806733 / a10ebc31): the 4–12× reading was a wall-shear
   sign-convention defect in the detector; the honest miss is −10.5% with wander. The clinic's
   first real case is re-pointed accordingly (the filed proposal names the A6 temperature-residual
   trace instead).
2. **§2's "NACA0012 aspect ratio" open anomaly CLOSED the night the strategy was adopted**
   (41f0e1df): generator-owned, proven by exact cell-count twins (pyHyp ×1.71 worse under
   refinement vs the C-grid's ×0.945 better). What remains of that item is the MESH_STANDARD
   generator-selection RULE, which is what its proposal now asks for.
3. **§1's cross-family propagation names four families (DAFoam / closure / batch / marine) that
   disagree with the supervision charter's four** (DAFoam-adjoint / Closure+UQ / Cases-campaigns /
   Infrastructure). Ruling: the charter's list governs supervision; the strategy's list names
   WORK AREAS to sweep, which is a superset — and the finding that matters is that **the batch
   family was never swept by the dead-lever precedent**. That sweep is ordered (2026-08-10).
