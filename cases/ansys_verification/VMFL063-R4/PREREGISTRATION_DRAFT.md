# ***DRAFT — NOT FROZEN*** — PRE-REGISTRATION VMFL063-R4: Separated Laminar Flow Over a Blunt Plate

> **STATUS: DRAFT. THIS DOCUMENT IS NOT FROZEN AND AUTHORISES NO COMPUTE.**
> No sha is pinned; no gate, band, cap or label here is binding until the
> supervisor freezes it by commit (CLAUDE.md rule 2). It is delivered by
> `ansys-lane-opus48` on 2026-09-10 for the supervisor's §3 check-1 and revision.
> Every number below is a **proposal**, not a measurement, except where it cites a
> measured VMFL063-R3 artifact by path. **No VMFL063-R4 solver has ever run**;
> `verification/runs/ansys_verification/VMFL063-R4` does not exist.

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — page 193
(Test Case, geometry, Figure .63.1 Flow Domain) and page 194 Table .63.1 (Ansys
Fluent) / Table .63.2 (Ansys CFX).** Reference verified first-hand in the sidecar
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
lines 5008–5055: *"Target 4.0 / Ansys Fluent 4.16 (ratio 1.04) / Ansys CFX 4.05
(ratio 1.01)"*, reference **J.C. Lane, R.I. Loehrke, "Leading Edge Separation from a
Blunt Plate at Low Reynolds Number", Transactions of ASME Vol.102 pp.494-496,
1980**; physics *"Laminar flow, high resolution numerical models"*, Re = 260 on
plate thickness. Title-page verify against the PDF is OWED at freeze (rule 15).

**SUCCESSOR to VMFL063-R3** (which returned `NOT A RESULT`, no gate ever evaluated —
the frozen R3 comparator refused the anchor domain D0 on strict completion before the
domain ladder could be assessed). R4 does **not** vacate the R3 record.

---

## 0. THE RULE-2 CONDITION (to be re-checked and pinned at freeze)

**NOT YET RUN.** The run root `verification/runs/ansys_verification/VMFL063-R4` does
not exist (checked 2026-09-10). There is no VMFL063-R4 number on this box for any
band, cap, domain or window here to have been fitted to. When frozen, the supervisor
restates this condition at the freeze commit and pins HEAD.

---

## 1. THE CENTRAL FINDING R4 IS BUILT AROUND — measured in R3, and it is the scientific point

R3 ran a **domain-independence ladder** at a fixed R2-L3 near-field grid, de-confined
open top BC, over D0 (Lu=0.9 m=10·2t, H=1.8 m=20·2t), D1 (Lu=1.8=20·2t, H=3.6=40·2t),
D2 (Lu=3.6=40·2t, H=7.2=80·2t). Only D0 and D1 ran before the launcher was killed. What
they measured, cited by artifact:

| domain | extents | outcome | evidence |
|---|---|---|---|
| **D0** (368 640 cells) | Lu=0.9, H=1.8 | **DID NOT CONVERGE** — parked in a residual limit cycle at endTime 100000; `SIMPLE_converged_lines = 0`; final initial residuals **Ux 2.63e-06, Uy 9.93e-06, p 5.78e-04** against criteria p 1e-08, U 1e-09 (p sits ~4.6 orders ABOVE its criterion and never moved) | `verification/runs/ansys_verification/VMFL063-R3/D0/log.simpleFoam`; cost **849.85 core-min MEASURED** (`RUN_RC.D0`) |
| **D1** (482 304 cells) | Lu=1.8, H=3.6 | **CONVERGED CLEANLY** — "SIMPLE solution converged in 11941 iterations" (< endTime 100000); final initial residuals **Ux 2.24e-10, Uy 9.99e-10, p 9.05e-11**, all under criteria | `.../VMFL063-R3/D1/log.simpleFoam`; cost **≈ 277.9 core-min** (ExecutionTime 16674.73 s, serial; no `RUN_RC.D1` — log-measured) |

**THE FINDING (on the R3 termination record, and re-verified here first-hand):**
D0's non-convergence is a property of the **CONFINED / TOO-SMALL FAR FIELD, not of the
case setup.** With the physically-correct de-confined open top, the D0 extents place the
open boundary too close to the growing displacement layer and separation bubble, and the
steady SIMPLE solve hunts in a limit cycle. **Enlarging the far field to D1's extents
(Lu 20·2t, H 40·2t) removed the limit cycle entirely** and produced the first converging
rung this case has ever had. This is exactly what a domain ladder exists to discover — a
finding, not a failure.

**CONSEQUENCE FOR R4: the ladder STARTS AT OR BEYOND D1's domain and never repeats D0.**
Re-running D0 would only re-buy an 850-core-min refusal. The lever R4 completes is the
same off-gate lever R2/R3 left open — **domain extent** — resumed from the smallest
domain that is numerically well-posed.

---

## 2. THE CASE, EXACTLY AS THE MANUAL STATES IT (unchanged from R2/R3)

Density 1 kg/m³ (kinematic, rho=1); viscosity 1.7894e-5 (`nu 1.7894e-05`); plate
thickness 2t = 90 mm (`TWO_T = 0.090`, plate top at y=t=0.045); plate length 1500 mm
(x∈[0,1.5], held fixed — the manual fixes it); inlet 0.0517 m/s; Re = 260; **laminar**
(`simulationType laminar`, only U, p — no turbulence closure). Convection
`div(phi,U) bounded Gauss linear` (2nd-order), UNCHANGED. The **only** off-gate change
carried from R3 is the de-confined open far-field top BC
(`pressureInletOutletVelocity` U, `fixedValue 0` p; far-field patch `type patch`); all
other BCs byte-identical to R2. R4 adds nothing new to the BCs — it only extends the
**domain ladder** to larger extents than R3 reached.

---

## 3. THE REFERENCE TIER AND THE CEILING (unchanged from R2/R3)

Reference kind **EXPERIMENTAL** (Lane & Loehrke; manual Target 4.0). Limb A is a
CONTINUUM claim → ceiling **`GATE REACHED`** (`PASS` unavailable; discretisation error
not separable from a continuum property; `VERIFICATION_CHARTER` §2f.3). Limb B
(serial-determinism identity, L1 vs L1D) ceiling `PASS`. **The row verdict is the worst
limb, so the best attainable R4 row is `GATE REACHED` — NOT a credential**
(`ANSYS_VERIFICATION_CHARTER` §6). Stated before compute.

---

## 4. THE PROPOSED DOMAIN LADDER (DRAFT — for the supervisor to fix)

**Fixed near-field grid = R2-L3, reused byte-identical** (counts NXU=256, NXD=640,
NYL=96, NYU=384; gradings A(0.1 0.2 1) B(0.1 160 1) C(20 160 1)); grid-independence
inherited from R2 (`GCI_fine = 0.48 %`, p = 2.505) and re-checked by the r=2 gate triple
at D*. DOF-free far-field padding per R3's frozen `gen_domain_mesh.py` rule.

Proposed ladder (geometric 2t multiples, fixed a priori; **no LR value enters the
choice**; the anchor is the smallest R3 domain shown *numerically well-posed*, D1 —
chosen for convergence, not for proximity to 4.0, so the ladder stays answer-blind):

| domain | Lu | H | Ld | note | ≈ cells (L3) |
|---|---|---|---|---|---|
| **E0** | 1.800 m (20·2t) | 3.600 m (40·2t) | 1.500 m | = R3's D1; the anchor (the smallest converging domain) | 482 304 |
| **E1** | 3.600 m (40·2t) | 7.200 m (80·2t) | 1.500 m | = R3's D2 extents; first enlargement | ≈ 737 280 |
| **E2** | 7.200 m (80·2t) | 14.400 m (160·2t) | 1.500 m | second enlargement (new, beyond R3) | ≈ 1.1 M (est.) |

**Answer-blind self-convergence rule (carried verbatim from R3 §4.4):**
`DOMAIN_TOL = TOL/10 = 0.010`, derived from the gate band, references neither the Target
4.0 nor the answer. The ladder `SELF_CONVERGED` iff the **TERMINAL** step is within
`DOMAIN_TOL` (a genuine plateau, not a fortuitous single step; §16.2/§16.3). `D*` = the
earliest domain from which every remaining step stays within `DOMAIN_TOL`. If the
terminal step is out of tol → `NOT_CONVERGED` → `NOT A RESULT`, ladder not extended
beyond the frozen extents, a wider-ladder successor owed. **The gate is byte-identical to
R2/R3** (§5); the fix is entirely off-gate (domain extent).

**Optional diagnostics (gate nothing):** a BC-isolation twin at E0 (open vs
`symmetryPlane` top) may be retained; an `Ld`-sensitivity check at D*. Both diagnostic.

---

## 5. THE GATE — BYTE-IDENTICAL TO R2, EVALUATED AT D* (proposed unchanged)

Carry the R2/R3 comparator gate and all controls VERBATIM (`REF_LR2T = 4.0`,
`TOL = 0.10`, window X∈(0.0, 1.2], `X_SIGN_REF = 1.35`, `FS = 1.25`, `RATIO = 2.0`,
`P_MIN = 0.05`, planted-zero `K_PLANT = K_PLANT_U = 0.05`, `TIER_CEILING_A = "GATE
REACHED"`, `TIER_CEILING_B = "PASS"`). At `D*`: r=2 triple L1/L2/L3 (near-field 23 040 /
92 160 / 368 640 + padding) → `|LR/(2t) − 4.0|/4.0 ≤ 0.10` AND Roache triple `CONVERGING`;
plus the L1/L1D determinism twin. `--verify-frozen` re-hashes the carried R2 comparator
at grade time and refuses on drift. **R4 does not touch the gate** (L-487).

---

## 6. STRICT COMPLETION, PLANTED-ZERO, COST (proposed)

Strict completion (rule 4) and the two-stage/two-channel planted-zero control (rule 3)
carried verbatim from R3's frozen comparator — the reduction (last reversed-to-attached
crossing) is unchanged. `endTime = 100000` retained (a converging solve stops far earlier
on `residualControl`; the running-total core-min cap, not endTime, is the budget limit).

**COST (DRAFT ESTIMATE — NOT MEASURED).** All solves serial, **ranks = 1**. Basis: R2/R3
measured throughput ≈ 2.05e-6 s/cell/iteration; R3 D1 (E0) already measured at ≈ 277.9
core-min / 11 941 iters.

| solve | cells (L3) | plausible iters | est. core-min |
|---|---|---|---|
| E0 (= D1 geometry) | 482 304 | ~12 000 | ≈ 280 (anchor, measured basis) |
| E1 | ≈ 737 280 | 12 000–18 000 | ≈ 300–560 |
| E2 | ≈ 1.1 M | 12 000–18 000 | ≈ 450–800 |
| gate triple + L1D at D* | 23 040 / 92 160 / 368 640 (+pad) | R2 actuals + pad | ≈ 150–500 |
| **HONEST ESTIMATE** | | | **≈ 1 800 core-min** |
| **PROPOSED CAP** | | | **3 000 core-min, RUNNING TOTAL** (rc124 = stop) |

Dollars **DERIVED, NOT MEASURED**, at c7a.4xlarge $0.0513/core-h (owner-stated): estimate
≈ **$1.54**, cap ≈ **$2.57** — both far under the $25 pre-authorised ceiling.

**KNOWN INEFFICIENCY, named separately (rule 12):** the far-field padding is carried at
near-field resolution, inflating E1/E2 cell counts. Accepted for R4 (trivial dollar cost);
a graded far-field-coarsening mesh lever is a separate future successor, not an R4 change.
Named so completion calibration does not fold it into a misprediction ratio.

**A DEFECT TO FIX BEFORE FREEZE (carried from R3's termination record):** the R3 launcher
`run_vmfl063_r3.sh` re-initialised `TOTAL_CORE_MIN=0` at every invocation and persisted it
nowhere, so a relaunch silently restarted cap accounting from zero. The R4 launcher must
**persist the running total** so the cap is honest across relaunches. This is a launcher
repair, off-gate, to be made and disclosed before freeze.

---

## 7. NAMED LIVE OUTCOMES (rule 1 vocabulary) — the same map as R3 §10

`GATE REACHED` (best attainable) · `GATE FAIL` physics (if de-confined + enlarged still
lands ~5.5, it STANDS — nothing tuned to 4.0) · `GATE FAIL` determinism · `NOT A RESULT`
(triple not CONVERGING, or domain `NOT_CONVERGED`, or a completion clause fails) ·
`BLOCKED` (toolchain/mesh) · `PENDING` (registered, not yet run). **`PASS` is unreachable
at row level by construction (§3).** This lane declines to predict which lands; what is
predicted is that the ladder — now started from a domain known to converge — can return
any of them and directly tests whether `LR/(2t)` is domain-independent beyond D1.

---

## 8. GRADING PATH (to be frozen)

comparator `grade_vmfl063_r4.py` (R2/R3 gate + controls verbatim + the domain layer;
carries the R2 blob and `--verify-frozen`); mesh generator (frozen, DOF-free, sole mesh
authority); launcher (freeze-pins all inputs disk==HEAD, persists the running-total cost,
applies §4 `--pick-dstar`, age guard on every solve dir); answer-blind smoke; case inputs
(R2 inputs + the de-confined top; optional confined twin). Run root does not exist.

---

## 9. WHAT THIS DRAFT DOES NOT CLAIM

Not a statement about Ansys (no Ansys solver on the box; archive not present). Does not
tune the domain to hit 4.0. Cannot earn a credential (ceiling `GATE REACHED`). Nothing is
sent anywhere (rules 7, 8). **This is a DRAFT; it is not frozen and authorises no compute.**
