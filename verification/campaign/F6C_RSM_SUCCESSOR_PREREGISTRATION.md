# F6c-RSM SUCCESSOR — pre-registration (DRAFT)

> **DRAFT — NOT AUTHORISED — CHECK-4 NOT TAKEN.**
> This document is a lane draft. It is **not frozen**. No sha is committed as its
> freeze, no gate is closed, and **no solver has been launched** in producing it.
> The freeze (the rule-2 commitment of gate, threshold, cap and label by sha, and
> the hash of the frozen grading path against the committed blob) is the cfd
> supervisor's non-delegable check 4 (`SUPERVISION_CHARTER.md` §3). Until the
> supervisor performs that freeze this file may be edited freely; after it, it is
> closed. Drafted 2026-09-07 by a cfd `lab-lane`.

**§2ay classification of the parent.** The parent verdict is **F6c GATE FAIL
(structural)** — `verification/campaign/CAMPAIGN_STATUS.md:460`;
`verification/campaign/F6_closure_aligned_flows.md` §"F6c"; `NOT_PASSING_REGISTER.md:773`.
The census flagged it as a standing violation: a landed GATE FAIL carrying **no
active dated fix-successor**. This draft is the successor that moves it to **state
(b)** — an active, dated, our-side fix that CHANGES what failed and re-runs. It is
**not** a capability gap (state a): a RANS closure that produces the Prandtl
secondary flow of the second kind **already exists on this box and has been measured
on this exact case** (`verification/campaign/D5_RSM_RESULT.md`). The fix is Sanaa's
"if it's the model, change the model."

---

## 1. WHAT FAILED, AND WHY IT IS RECOVERABLE

The original F6c gate compared the **secondary-flow RMS** (in-plane velocity
magnitude, root-mean-square over the duct cross-section, as a percentage of
`U_bulk`) of a converged `kOmegaSST` field against DNS, on two ERCOFTAC/leaderboard
duct cases:

| case | DNS secondary-flow RMS | `kOmegaSST` (linear RANS) | verdict |
|---|---|---|---|
| `AR_1_Ret_360` | **2.2201 % of U_bulk** (0.7344 m/s, U_bulk 33.0777 m/s) | 6.09e−16 % (machine zero) | **GATE FAIL** |
| `AR_3_Ret_360` | **2.07 % of U_bulk** | 2.4e−15 % (machine zero) | **GATE FAIL** |

The failure is **structural to the linear eddy-viscosity family**: a Boussinesq
closure has an isotropic eddy viscosity and cannot generate the anisotropic normal-
stress imbalance that drives the secondary flow of the second kind. This is a
property of the *model class*, not of OpenFOAM: the same solver, on the same mesh,
with a **Reynolds-stress closure**, produces a non-zero secondary flow. That was
demonstrated on `AR_1_Ret_360` in `D5_RSM_RESULT.md`:

| model | class | secondary-flow RMS (% U_bulk) | % of DNS | converged at |
|---|---|---|---|---|
| kOmegaSST | linear | 6.09e−16 % | 0 % | — |
| LienCubicKE | nonlinear | 0.1740 % | 7.84 % | — |
| **SSG** | RSM | **1.2213 %** | **55.01 %** | iter 118,424 |
| **EBRSM** | RSM | **1.1581 %** | **52.17 %** | iter 251,703 |
| LRR | RSM | 4.5948 % | 206.96 % | iter 141,982 |

**The change is: replace the linear closure with an RSM closure (SSG and EBRSM).**
Why it should recover the mechanism: an RSM transports the six Reynolds-stress
components directly, so the cross-plane normal-stress anisotropy that drives the
secondary flow is represented rather than assumed away. D5 measured a signal ten to
fourteen orders of magnitude above the linear models on this exact case.

---

## 2. THE GATE, AND THE THRESHOLD IS NOT WIDENED

**Gate quantity (unchanged from the parent):** secondary-flow RMS as a percentage
of `U_bulk`, on the converged field, compared to the DNS reference.

**Gate G-F6cR (per case):** **PASS** iff the model's secondary-flow RMS lies within
**±20 % of the DNS value**, i.e. RMS/DNS ∈ **[0.80, 1.20]**; else **GATE FAIL**.

| case | DNS (% U_bulk) | PASS band (% U_bulk) |
|---|---|---|
| `AR_1_Ret_360` | 2.2201 | [1.7761, 2.6641] |
| `AR_3_Ret_360` | 2.07 | [1.6560, 2.4840] |

**This band is NOT a widening of the parent gate, and the direction matters.** The
parent gate demanded that RANS *reproduce* the DNS secondary flow; it failed because
RANS captured ~0 %. A widening-to-manufacture-a-pass would move the bar *toward
zero* — e.g. "PASS if RMS > 0.5 % of U_bulk", which a 52 %-of-DNS result (1.15 %)
would clear. This registration does the **opposite**: it holds a genuine ±20 %
validation-agreement band around the DNS value, a bar that the best measured RANS
closure **does not clear**. Sanaa's T25 ruling — a gate is never relaxed to fit the
answer — is respected by making the band *tighter and answer-independent*, not
looser.

**Honest prediction, stated before any run (rule 2):** by the D5 prior, SSG (55.0 %
of DNS) and EBRSM (52.2 %) on `AR_1_Ret_360` will land at ~1.15–1.22 % of U_bulk —
**outside [1.7761, 2.6641] — and will therefore GATE FAIL.** If that is the outcome
it is a **MODEL-FORM finding**: *the best practical RANS closure recovers only ~half
of the DNS secondary-flow magnitude on this duct.* That is a real, publishable
statement about the closure family. **It remains state (b), not state (a):** the
capability (a RANS closure that produces the mechanism) exists and runs; what the
gate would then establish is a *quantitative model-form deficit*, not an OpenFOAM
gap. `AR_3_Ret_360` has **no prior RSM result on this box** and its outcome is
genuinely unknown — it is the case that makes this a fresh, answer-blind run.

**Rule-2 cleanliness.** This registration mandates **fresh SSG and EBRSM solves**
on both cases; it does **not** re-grade D5's existing fields. The band above is
justified from the physics of a secondary-flow validation (±20 % agreement), not
back-fitted to the D5 numbers — and, as noted, the D5 numbers *fail* it.

**Scope limit, stated.** Like the parent F6c, this is a **single-mesh model-form
gate** on the established converged duct mesh (`ladder-b/duct_baseline/`, 3,025
cells for `AR_1`). It is **not** a Roache grid-convergence triple, so rule 5 does
not apply; grid-independence of the secondary-flow magnitude is a separate question
and is explicitly out of scope. No GCI is or may be quoted.

**Models.** SSG and EBRSM only (the two RSMs D5 showed to be *accurate*, bracketing-
low). LRR is excluded from the gate because its 207 %-of-DNS overshoot fails for the
opposite reason and would muddy the model-form reading; it may be run as a reported-
not-gated diagnostic.

---

## 3. THE SPECIFIC CHANGED THING, AND THE SETUP TRAPS D5 ALREADY PAID FOR

**Changed:** `constant/turbulenceProperties` `RASModel` from `kOmegaSST` to `SSG`
(and a second case set to `EBRSM`). Everything else — mesh, `U_bulk`, body force,
boundary geometry, DNS reference — is held at the parent/B2 values.

**Setup requirements carried forward from `D5_RSM_RESULT.md` (each a preflight
gate, not a runtime surprise):**
1. every transported field needs a **solver entry** in `fvSolution` (`R`, `epsilon`,
   and for EBRSM the elliptic-blending `f`) — D5's preflight check 2b.
2. `f` is a **symmetric** equation: it needs `PCG/DIC`, not `PBiCGStab/DILU`.
3. `residualControl` must name the fields the RSM **actually transports** (`U`, `p`,
   `epsilon`, the six `R` components, `f`), never `k`/`omega` — otherwise the stop
   criterion can never be met and the run grinds to `endTime` (D5's fifth, costliest
   finding).
4. EBRSM required **relaxation 0.3** to clear a matrix-solve FPE at iteration ~300.

---

## 4. GRADING PATH — FIXED AT THE FREEZE, PLANTED-ZERO CONTROL MANDATED

The grading script is `cases/F6C_RSM/secondary_flow_gate_rsm.py`, to be written and
**frozen at the registration commit** (the supervisor hashes the disk blob against
the committed blob at check 4; the grader must refuse without `--prereg-commit`).
It shall:
- read the converged in-plane velocity field from the run root (**decomposed, never
  reconstructed**, per the F25/F27 precedent), compute the cross-sectional RMS of
  the in-plane velocity magnitude, normalise by `U_bulk`, and compare to the band;
- enforce the strict completion rule (rule 4) before grading, with the age guard;
- carry a **planted-zero control (rule 3)**: plant a known non-zero in-plane
  perturbation into a copy of the field, read it back through the *same* reader, and
  **refuse (exit 2)** if the reader cannot see it — following the parent's
  `secondary_flow_gate.py` pattern. A zero secondary flow is admissible evidence
  only from a reader shown able to see a non-zero.
- pin the DNS reference values as numbers at the freeze (2.2201 %, 2.07 %) with
  their provenance (`secondary_flow_gate.json`).

Grading is **zero-new-compute** once the solves complete.

---

## 5. COST — rule 12 (measured anchors from D5, single core)

Anchor rates measured from the D5 solve-registry logs (single core, 3,025 cells):
- LRR 141,982 iters, ExecutionTime **1754.08 s** → 4.08 core-µs/cell-iter
  (`demo-output/website/solve_registry/d5b_LRR_20260729T022123Z.log`);
- EBRSM 251,703 iters, ExecutionTime **4021.99 s** → 5.28 core-µs/cell-iter
  (`d5g_EBRSM_20260729T023927Z.log`).

| item | iters | cells | basis | core-min |
|---|---|---|---|---|
| AR_1 SSG | 118,424 | 3,025 | 4.08 µs/cell-iter (LRR anchor, same class) | **24.5** MEASURED-ANCHORED |
| AR_1 EBRSM | 251,703 | 3,025 | 5.28 µs/cell-iter (EBRSM anchor) | **67.0** MEASURED-ANCHORED |
| AR_3 SSG | ≤ ~120,000 assumed | ≤ 9,075 assumed (≤ 3× AR_1) | 4.08 µs/cell-iter | **≤ 75** ESTIMATED |
| AR_3 EBRSM | ≤ ~250,000 assumed | ≤ 9,075 assumed | 5.28 µs/cell-iter | **≤ 200** ESTIMATED |
| **estimate total** | | | | **≈ 366.5** |
| **HARD CAP** | | | | **550** |

`AR_3_Ret_360`'s cell count and iteration count are **not yet confirmed on disk**;
its figures above are explicit upper-bound assumptions (≤ 3× the AR_1 mesh; iters
comparable). **A preflight read of the AR_3 mesh is a legal pre-compute condition:
if it exceeds 9,075 cells the AR_3 cap is re-anchored to the measured rate before
first compute, per rule 2.** An overrun of the 550 cap **stops the run** (rule 12).
Dollars: 550 core-min = 9.167 core-h × $0.0513/core-h = **$0.470 — DERIVED, NOT
MEASURED** (c7a.4xlarge, reported-by-owner; the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5). Well under the $25 pre-authorised ceiling. A
calibration row (estimate vs actual) is owed to `docs/COST_CALIBRATION.md` at
completion.

---

## 6. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether an RSM closure brings the secondary-flow RMS within ±20 % of DNS
  (predicted NO on AR_1 from the D5 prior; unknown on AR_3), and quantify the
  model-form deficit either way.
- **Cannot:** anything about grid independence (single mesh), about the ~76 % of the
  duct error that is streamwise-profile error (`closure_challenge_C2_error_
  decomposition.md` — a perfect secondary flow closes at most ~24 %), or about any
  Reynolds number other than Re_τ 360. None of these is claimed.

**Nothing is sent, filed, uploaded, registered or posted (rule 7). This is a draft
handed to the cfd supervisor for the check-4 freeze.**
