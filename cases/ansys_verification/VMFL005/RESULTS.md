# VMFL005 — Poiseuille Flow in a Pipe: RESULTS

**NOT FILED ANYWHERE. Nothing in this document is sent, emailed, uploaded, filed,
posted, registered or commented outside this box, now or ever** (CLAUDE.md rules 7
and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is proprietary Ansys
documentation. **SUBMISSIONS PARKED.**

**This file does not revise `PREREGISTRATION.md` and cannot.** The gate (2 % relative
to the manual's printed target of 10.24 Pa, at L3), the exact-formula diagnostic
(1 %), the Roache quantity (the inlet-to-outlet pressure drop `dP`), the per-level
endTimes, the cap (13 core-min) and the labels were frozen at blob
**`43aaf6bf5c5f1189495e1460e5de415e56860447`**, commit **`2d54a629`**, at
**2026-08-24T18:42:07Z** — **before any VMFL005 solver started** (first run artifact
2026-08-24T18:45:32Z, 3 min 25 s later). Nothing here edits a line of that file
(CLAUDE.md rules 2 and 6).

**Written 2026-08-24T19:12:38Z (`date -u`, read in the writing invocation) by
`ansys-lane-opus`**, from artifacts only — **zero compute was spent producing this
record**: no solver was re-run and the comparator was not re-invoked. The verdict
below is the one the frozen comparator returned at grade time and is not re-derived
here. **No agent message is Sanaa's consent** (CLAUDE.md rule 9); the compute this
record describes ran under the 2026-08-21 CPU blanket at a per-item derived cost of
$0.003420, which is a per-item read and not a new ceiling.

---

## 1. VERDICT

# `PASS`

**dP = 10.2909853852 Pa at L3 (400 × 40, 16 000 cells) against the manual's printed
target of 10.24 Pa — deviation 0.4979 %, inside the frozen 2 % gate by a factor of
4.0.** The same value deviates from the exact Hagen–Poiseuille solution
(8·μ·L·V_avg/R² = 10.24 Pa) by the same **0.4979 %**, inside the frozen 1 %
diagnostic (which is not the gate).

The grid triple on `dP` is **`CONVERGING`** at observed order **p = 1.9341** with
**GCI_fine = 5.0212e-04 = 0.0502 %**, so CLAUDE.md rule 5 step 2 does not turn this
row into `NOT A RESULT`; all three levels are iteratively converged and plateaued, so
step 1 does not either. The planted-zero control fired and was read back from disk
exactly.

**Read §5 before citing this `PASS`.** The deviation from the analytic reference is
**9.92× larger than the fine-grid discretisation uncertainty**, and Richardson
extrapolation moves the answer **further from** the analytic value, not closer. The
gate is genuinely met and the triple is genuinely converging — and grid refinement
does **not** close the remaining gap. That is a measured fact about this rung and it
is stated at the top because a `PASS` on its own does not convey it.

**This is a statement about this lab's OpenFOAM v2606 run of this case against the
manual's reference result. It is not a statement about Ansys**
(`ANSYS_VERIFICATION_CHARTER.md` §2). This box has no Fluent and no CFX;
`poiseuille-flow.cas` and `VMFL005B_VV005CFX.def` were not run, and no VM2026R1
archive was opened by this rung. Fluent's and CFX's own numbers are context in §4,
never the gate.

**Register row #3.** Row #1 is VMFL001 run 1 (`NOT A RESULT`), row #2 is VMFL001-R2
(`PASS`). This rung is independent of both and re-grades neither.

---

## 2. What ran

`run_vmfl005.sh` (frozen blob **`06056e18a9fee92e2e8765b279ae31f5373c62c5`**) built
and ran all three levels serially. Each level's `RUN_RC.txt` carries
`prereg_blob=43aaf6bf5c5f1189495e1460e5de415e56860447`, matching the pre-registration
blob at HEAD — the freeze is recorded **by the run itself** and not only asserted
here.

| level | cells (`log.checkMesh`) | registered | endTime | rc | wall s | core-min | finished (UTC, `RUN_RC.txt`) |
|---|---|---|---|---|---|---|---|
| `L1_100x10` | **1 000** | 100 × 10 = 1 000 ✅ | 2000 | 0 | 11 | 0.1833 | 18:45:32Z |
| `L2_200x20` | **4 000** | 200 × 20 = 4 000 ✅ | 3000 | 0 | 29 | 0.4833 | 18:46:01Z |
| `L3_400x40` | **16 000** | 400 × 40 = 16 000 ✅ | 6000 | 0 | 200 | 3.3333 | 18:49:21Z |
| **total** | 21 000 | | | | **240** | **4.0000** | 18:49:21Z (`COST.txt`) |

`checkMesh` returns **`Mesh OK`** at all three levels (mesh birth certificate,
`VERIFICATION_CHARTER.md` §9). No `CAP_EXCEEDED.txt` exists; the run used **30.8 %**
of the 13 core-minute cap.

**Geometry and physics as the manual specifies them at p. 25.** Axisymmetric **wedge**,
one cell thick, half-angle 2.5° (5° total), pipe axis +x, 0 ≤ x ≤ L = 0.1 m, wall at
**exact** radius R = 0.00125 m (`blockMeshDict.template` places the wall vertices at
y = R cos 2.5°, z = ±R sin 2.5° rather than y = R, z = R tan 2.5°, which would put the
wall at R/cos α and bias the 1/R⁴ dependence by ≈ 0.19 %). ν = μ/ρ = **1e-5 m²/s**
(`constant/transportProperties`), model **`laminar`**, confirmed active-in-log at all
three levels. **Re = ρ V_avg D / μ = 500.0000**, against the manual's 500.

**ρ = 1 kg/m³ is what makes the units work.** `simpleFoam` solves for kinematic
pressure p/ρ in m²/s². The manual sets ρ = 1 kg/m³, so the monitored kinematic
pressure is **numerically equal to pressure in Pa** and the gate compares like with
like. This is stated because it is the one place a unit error would silently pass.

**The wedge was verified by this lane from the mesh, not from the solver log.** The
comparator's `wedge_in_log` lever reads **`false`** at all three levels — v2606's
`simpleFoam` log does not print patch types, so that lever is a null and not a
failure. `constant/polyMesh/boundary` at L3 carries `wedge1` and `wedge2`, both
**`type wedge`**, 16 000 faces each; `walls` is `type wall` with 400 faces; `inlet`
and `outlet` are `patch` with 40 faces each; `defaultFaces` is `empty` with 0 faces.
Independently, the inlet monitor's own header gives the patch area as
**6.809042402188e-08 m²**, which is **½ R² sin 5° = 6.809042402161e-08 m²** to twelve
significant figures — the planar 5° wedge sector at exactly R.

### 2.1 The inlet condition, and that all three levels compiled the same code

The inlet is `codedFixedValue`, `name poiseuilleInlet`, imposing the fully developed
parabola from each patch face's own centre radius:

```
r  = sqrt(Cf.y² + Cf.z²)
ux = 2 · V_avg · (1 − (r/R)²)      V_avg = 2.0 m/s,  R = 0.00125 m
```

OpenFOAM compiled this at runtime once per level. **The SHA1 digest OpenFOAM computes
over the coded body is `9d9f75ceaa7aae19ef2f8f01cb1a11f7a87fb674` at all three
levels** (`dynamicCode/poiseuilleInlet/Make/SHA1Digest`, byte-identical, md5
`6b135ec8…` ×3), and the three generated `fixedValueFvPatchFieldTemplate.C` files
differ from one another by **exactly one line** — the `#line` directive naming that
level's own `0/U`. The three levels therefore ran the **same** inlet code, verified
rather than assumed.

### 2.2 Strict completion rule (CLAUDE.md rule 4, per-level endTime per `PREREGISTRATION.md` §6)

All six clauses hold at **all three** levels, read from the artifacts. The comparator
checks these itself and **refuses (exit 2)** on any failure; it did not refuse.

| clause | L1_100x10 | L2_200x20 | L3_400x40 |
|---|---|---|---|
| 1. `rc = 0` (`RUN_RC.txt`) | ✅ | ✅ | ✅ |
| 2. `End` line in `log.simpleFoam` (count) | ✅ 1 | ✅ 1 | ✅ 1 |
| 3. last time == that level's `endTime` | ✅ 2000 | ✅ 3000 | ✅ 6000 |
| 4. `U` and `p` present at `endTime` | ✅ | ✅ | ✅ |
| 5. `ExecutionTime` line count == `endTime` | ✅ 2000 | ✅ 3000 | ✅ 6000 |
| 6. age guard: fields at `endTime` newer than that level's own `0/U` | ✅ | ✅ | ✅ |

Time directories present are exactly `0` and the endTime at each level — no partial
write, no restart. `fvSolution` carries no `residualControl`, so SIMPLE could not stop
early and clause 3 is meaningful rather than tautological.

### 2.3 Iterative convergence (the registered clause, `PREREGISTRATION.md` §4 step 1)

Registered: final `Ux`, `Uy` **and** `p` initial residuals **< 1e-6**, and the inlet
pressure monitor's peak-to-peak over the last 20 % of iterations **< 1e-4**. Both
tolerances are printed beside the measurements, as frozen.

| level | final `Ux` | final `Uy` | final `p` | tol | plateau ptp | plateau window | tol | converged |
|---|---|---|---|---|---|---|---|---|
| `L1_100x10` | 4.14311e-12 | 5.39759e-08 | 7.09973e-10 | 1e-6 | **4.100e-10** | last 400 | 1e-4 | ✅ |
| `L2_200x20` | 1.35528e-12 | 9.49414e-08 | 7.36848e-10 | 1e-6 | **3.200e-10** | last 600 | 1e-4 | ✅ |
| `L3_400x40` | 1.73203e-13 | 1.99873e-08 | 8.39135e-10 | 1e-6 | **6.000e-11** | last 1200 | 1e-4 | ✅ |

The worst gated residual anywhere is `Uy` = **9.49e-08** at L2, **10.5× inside** the
1e-6 clause; the worst plateau ptp is **4.1e-10**, **240 000× inside** the 1e-4
clause. The inlet pressure is flat to the twelfth significant figure over the last
1200 iterations at L3 (`1.029098538520e+01` at iterations 5999 and 6000).

**`Uz` is reported and is NOT gated, as registered.** Its final initial residuals are
1.848e-02 / 8.819e-03 / 2.538e-03 — three to five orders above the gated components.
This is the expected signature of a **wedge**: the z-component is the out-of-plane
direction that the wedge transformation constrains rather than solves, its solution is
identically zero to round-off, and its *relative* initial residual is therefore
normalised by a vanishing scale and carries no information. It falls monotonically
with refinement (7.3× coarse→fine), which is consistent with a round-off-scale
quantity and not with a physical residual. The pre-registration excluded it from the
gate before any number was seen; it is printed here because excluding a channel
silently would be worse than printing it.

---

## 3. The gate

**THE FROZEN GATE:** at L3, |dP_lab − dP_manual| / |dP_manual| ≤ **0.02**.
`dP = p_inlet − p_outlet`, both area-averaged over the patch, taken from the **last
row (endTime)** of the two `surfaceFieldValue.dat` monitors.

| level | cells | p_inlet (Pa) | p_outlet (Pa) | **dP (Pa)** | dev vs manual 10.24 Pa |
|---|---|---|---|---|---|
| `L1_100x10` | 1 000 | 10.23475565622 | 0.0 | **10.23475566** | 0.0512 % |
| `L2_200x20` | 4 000 | 10.27932261636 | 0.0 | **10.27932262** | 0.3841 % |
| **`L3_400x40`** (the gate) | 16 000 | 10.29098538520 | 0.0 | **10.29098539** | **0.4979 %** ✅ |

`p_outlet = 0` **exactly** at all three levels, as it must be: the outlet is
`fixedValue` at 0. It is measured rather than assumed because a monitor that cannot
read a zero is the failure CLAUDE.md rule 3 exists for — see §6.

**Sources (the gate's own artifacts, on disk and committed):**
`L3_400x40/postProcessing/pInletMonitor/0/surfaceFieldValue.dat` and
`L3_400x40/postProcessing/pOutletMonitor/0/surfaceFieldValue.dat`, and their L1/L2
counterparts.

**Gate MET: 0.4979 % against a 2 % threshold — a factor of 4.0 of margin.**

### 3.1 The diagnostic (printed beside the gate, never the gate)

Frozen tolerance 1 % against the closed-form Hagen–Poiseuille solution:

| form | value |
|---|---|
| 8·μ·L·V_avg / R² (μ=1e-5, L=0.1, V_avg=2.0, R=0.00125) | **10.240000 Pa** |
| 8·μ·L·Q / (π R⁴) cross-check, Q = V_avg·πR² | **10.240000 Pa** |
| deviation of L3 | **0.4979 %** — inside 1 % ✅ |

The two algebraic forms agree, so the reference itself is not a transcription. **The
manual's printed target of 10.24 Pa is the exact value to the four figures it
prints** — unlike VMFL001, where printed-target rounding dominated the worst gate row
(`N-AV3`), here the gate deviation and the analytic deviation are the **same number**
to eight significant figures (0.49790415 % both ways). Nothing in this rung's
deviation is the manual's rounding.

---

## 4. Ansys's own numbers — context only, never the gate

Manual Tables .05.1 and .05.2 at p. 25 (`ANSYS_VERIFICATION_CHARTER.md` §2):

| solver | dP, Pa | ratio to target |
|---|---|---|
| Target (White, *Fluid Mechanics* 3rd ed., Hagen–Poiseuille) | 10.24 | 1.000 |
| Ansys Fluent | 10.22 | 0.998 |
| Ansys CFX | 10.49 | 1.024 |
| **this lab, OpenFOAM v2606 `simpleFoam`, L3** | **10.2909853852** | **1.0050** |

**This box has no Fluent and no CFX.** This lab's value sits between Fluent's and
CFX's, closer to the target than CFX and further than Fluent. **Nothing is claimed
about either solver from this**, and no Ansys archive was opened by this rung.

---

## 5. THE FINDING — the deviation is ~10× the discretisation uncertainty, and refinement moves the answer AWAY from the analytic value

**This section is the reason the `PASS` above is defensible rather than lucky, and it
is not softened.**

### 5.1 The Roache triple (CLAUDE.md rule 5)

Refinement ratio **2.0** exactly in both directions (100→200→400 axial, 10→20→40
radial); Fs = **1.25**; the quantity is `dP`, as frozen.

| quantity | value |
|---|---|
| coarse `L1_100x10` (1 000 cells) | **10.23475565622 Pa** |
| medium `L2_200x20` (4 000 cells) | **10.27932261636 Pa** |
| fine `L3_400x40` (16 000 cells) | **10.29098538520 Pa** |
| d32 = f_med − f_coarse | −0.04456696014 |
| d21 = f_fine − f_med | −0.01166276884 |
| **R = d21/d32** | **0.26169092088** |
| **state** | **`CONVERGING`** |
| **observed order p** | **1.93406422** |
| **GCI_fine (Fs = 1.25)** | **5.021173e-04 = 0.0502 %** |
| **Richardson extrapolated f** | **10.29511921046 Pa** |

`CONVERGING`, so rule 5 step 2 does not fire and the gate verdict stands. The three
values are **monotone** (increasing with refinement), so the GCI is quotable and is
quoted. **R = 0.2617 ≈ 1/4** and **p = 1.934 ≈ 2** — the observed order matches the
formal second order of the frozen `fvSchemes` to **3.3 %**, on a family refined by
exactly 2. The numerics are behaving exactly as they should.

### 5.2 And that is precisely why the next three numbers matter

| channel | value |
|---|---|
| **deviation of the fine grid from the analytic 10.24 Pa** | **0.4979 %** |
| **fine-grid discretisation uncertainty, GCI_fine** | **0.0502 %** |
| **ratio deviation / GCI** | **9.92** |
| **Richardson-extrapolated value** | **10.295119 Pa** |
| **deviation of the EXTRAPOLATED value from 10.24 Pa** | **0.5383 %** |
| — against the fine level's | 0.4979 % |

**Richardson extrapolation moves the answer further from the analytic value, not
closer.** The extrapolated `dP` overshoots the exact Hagen–Poiseuille result by
0.5383 %, against the finest grid's own 0.4979 %. The grid sequence is converging —
cleanly, at second order — but it is converging to **10.2951 Pa, not to 10.24 Pa**.

**What this means, stated as measurement and not as interpretation.** The grid triple
is genuinely `CONVERGING`, the gate is genuinely met, and **grid refinement does not
close the gap to the analytic solution.** Taking GCI_fine as the discretisation
component, roughly **90 %** of the 0.4979 % residual deviation is **not**
discretisation error: it is a modelling / setup signature of this discrete
reproduction of the case.

**This is the exact opposite of what VMFL001-R2 showed** (`N-AV6`), where Richardson
extrapolation of a `CONVERGING` second-order triple landed on the analytic value to
3.7 parts per million without ever seeing the formula. Two cases, both `PASS`, both
`CONVERGING`, both p ≈ 2 — and the extrapolation is a 3.7 ppm confirmation in one and
a 0.54 % *miss* in the other. **A small GCI is a statement about grid convergence
only. It does not license the claim that the remaining deviation from a reference is
numerical.** Recorded as `N-AV7`.

### 5.3 Candidate mechanisms — NOT asserted, and the docket carries the question

The mechanism is **unresolved**. This lane did not determine it and does not claim it.
Three candidates, with what is and is not measurable from this rung's artifacts:

1. **Discrete face-centre sampling of the parabolic inlet on the wedge.** The
   `codedFixedValue` evaluates `2·V_avg·(1 − (r/R)²)` at each inlet face's **centre
   radius**, so the discrete mass flow through the inlet is a midpoint-rule
   approximation of the continuum integral, not the exact ∫. **Not measured here** —
   testing it needs the face-centre radii and face areas from the mesh, which is
   arithmetic this rung did not do.
2. **Planar-wedge geometry.** The 5° wedge sector is a **flat-sided triangle**, area
   ½R² sin 5° = **6.809042e-08 m²**, against the true circular sector
   (5/360)·πR² = **6.817692e-08 m²** — a deficit of **0.1269 %**, measured from the
   monitor header and confirmed by closed form. Same order of magnitude as the
   residual deviation but **not equal to it**, and the sign relation is not
   established. This is a measured geometric fact and **not a mechanism claim**.
3. **Entrance adjustment.** The pipe is L = 0.1 m at Re = 500, D = 0.0025 m; the
   continuum laminar entrance length is 0.05·Re·D = **0.0625 m** (0.06·Re·D =
   0.075 m), i.e. 62.5–75 % of the pipe. The inlet imposes the *continuum* parabola,
   which need not be the *discrete* fully developed profile, so a short redevelopment
   is possible. **NOT TESTABLE from this run's artifacts:** the case sampled pressure
   at the inlet and outlet patches only, with no axial pressure profile, so whether
   dP/dx is constant along the pipe cannot be read from anything committed. Saying so
   is the honest answer; it is also the cheapest thing the next rung could add.

**Docketed as `D510`:** which mechanism accounts for the ≈ 0.5 % non-discretisation
residual, and does it recur in **VMFL007** — the non-Newtonian power-law pipe at
manual p. 29, which re-uses this exact axisymmetric wedge pipeline and is therefore
the direct test of whether the residual is **pipeline-borne**.

---

## 6. Planted-zero control (CLAUDE.md rule 3) — it fired

The comparator copied L3's `surfaceFieldValue.dat` to a **temp tree** — the run tree
was never modified — added **PLANT = 1.234 Pa**, **read it back from disk**, and
re-ran the same extraction.

| channel | value |
|---|---|
| planted | **1.234** |
| **read_back_delta** (what the file on disk changed by) | **1.234** |
| **reader_dp_delta** (what the dP extractor reported) | **1.234** |
| file | `surfaceFieldValue.dat` |
| **passed** | **`True`** |
| run tree modified | **no** — the plant was applied to a temp copy |

**This is the control that makes `p_outlet = 0.0` evidence.** The outlet reads exactly
zero at every level, and a zero from a reader not shown able to see a non-zero is not
evidence. The reader is demonstrated able to see a non-zero **in this exact file
format, on this run's real L3 output**, before its zeros are believed. The control
fires **before** the verdict and the comparator refuses on its failure.

---

## 7. Cost (CLAUDE.md rule 12) — estimate versus actual

| item | value |
|---|---|
| ranks | **1 (serial)**; core-min = wall_s × 1 ÷ 60 |
| **predicted** (`PREREGISTRATION.md` §9) | **4.9 core-min** (295 wall s) = **$0.004190 derived** |
| **CAP** | **13 core-min** = $0.011115 derived — **not approached** (30.8 % used, no `CAP_EXCEEDED.txt`) |
| **actual, MEASURED, gross** | **4.0000 core-min** (240 wall s) — `COST.txt`, corroborated by the three `RUN_RC.txt` (0.1833 + 0.4833 + 3.3333) |
| **actual, cleaned** | **= gross, 4.0000 core-min.** Longest single wall is 200 s, 18× below the 3600-s stall rule (`COMPUTE_BUDGET_CHARTER.md` §2), so stall cleaning removes nothing |
| **dollars** | **$0.003420 DERIVED, NOT MEASURED** (4.0000 ÷ 60 × $0.0513/core-h) |
| **ratio actual/predicted** | **0.8163×** (4.0000 / 4.9) — inside the estimate, in the conservative direction. In wall seconds, 240 / 295 = 0.8136× |
| `cost_basis` | owner-stated rate **$0.0513/core-h**, c7a.4xlarge, Sanaa 2026-08-21/22 — **reported-by-owner, not measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **waste** | **0.000 core-min**, named separately per §6 of that charter and netted off nothing: no level failed, no level restarted, no level was capped, the comparator returned exit 0 on its first invocation, and no re-run of any kind was needed |

### 7.1 Attribution — measured, not guessed, because the logs separate the two terms

The pre-registration's estimate had three named terms. **All three are separately
measurable from the logs**, because `log.simpleFoam` prints both `ExecutionTime`
(solver CPU) and `ClockTime` (wall), so startup-and-compile is
`wall_s − final ExecutionTime`:

| term | predicted | **measured** | ratio |
|---|---|---|---|
| solver | **217 s** (1.3 + 12.7 + 203.1) | **221.43 s** (4.68 + 23.37 + 193.38, final `ExecutionTime` per level) | **1.020×** |
| `codedFixedValue` runtime compile + startup | **45 s** (~15 s/level × 3) | **18.57 s** (6.32 + 5.63 + 6.62) | **0.413×** |
| margin (3rd U component, `linearUpwind`, 2 per-iteration function objects) | **33 s** | **0 s consumed** | — |
| **total** | **295 s** | **240 s** | **0.814×** |

**The whole of the −18.6 % gap is the compile allowance and the unused margin; the
solver estimate was accurate to +2.0 %.** At every level the first `ExecutionTime`
line reads `ClockTime = 6 s` while `ExecutionTime` itself is ≤ 0.17 s — i.e. an
OpenFOAM `codedFixedValue` `wmake libso` build plus solver startup costs **≈ 6.2 s per
level on this box**, not the 15 s the freeze allowed. **Transferable rule for the next
estimate: price a `codedFixedValue` runtime compile at ≈ 6 s per fresh case directory
on this box, not 15.**

**The per-level structure of the solver term is the more interesting miss, and it
cancels.** The frozen basis borrowed VMFL001's per-cell-iteration rates, which *grew*
with mesh size (6.51e-7 → 1.06e-6 → 2.12e-6 s/cell·iter). VMFL005's measured rates are
**flat**: **2.34e-6 / 1.95e-6 / 2.01e-6** s/cell·iter at L1 / L2 / L3. So the two
small levels were under-predicted (L1 1.3 s → 4.68 s, 3.6×; L2 12.7 s → 23.37 s,
1.84×) and the large level over-predicted (L3 203.1 s → 193.38 s, 0.95×), and because
L3 is 87 % of the solver time the net came out at 1.020×. **The right basis for a 2D
axisymmetric wedge `simpleFoam` case on this box is a constant ≈ 2.0e-6 s per
cell-iteration, not a size-dependent rate borrowed from a different geometry.**

**Contention: not characterised.** No load figure was taken before or during this run,
so no contention penalty is claimed in either direction. Peer teams were committing
throughout the window (`f2b54c3b`, `10b3e97c`, `2f1d6cb7`, `22abb11d` all land between
18:45 and 18:47Z), but a commit is not a solve and this lane did not check for live
solvers. **Stated as unknown rather than assumed to be zero.**

Landed as calibration row **`C-47`** in `docs/COST_CALIBRATION.md`.

### 7.2 A defect in the pre-registration's cost arithmetic — DISCLOSED, NOT EDITED

`PREREGISTRATION.md` §9 prints the per-cell-iteration basis as "L1 6.51e-10, L2
1.06e-9, L3 2.12e-9 s/(cell·iter)". **Those exponents are 1000× too small.** VMFL001's
measured 2 s / (1024 cells × 3000 iters) is **6.51e-7** s/(cell·iter), not 6.51e-10;
likewise 1.06e-6 and 2.12e-6. The **products** in the next row are computed from the
correct values and are right (1000 × 2000 × 6.51e-7 = 1.3 s; 4 000 × 3 000 ×
1.06e-6 = 12.7 s; 16 000 × 6 000 × 2.12e-6 = 203.5 ≈ 203.1 s), so the frozen estimate
of **295 s = 4.9 core-min** and the **cap of 13** are unaffected.

This is a **display defect in a frozen file** and it changes **no gate, threshold, cap
or label**. Under CLAUDE.md rule 6 the frozen file is **not edited**; the defect is
recorded here and reported to the supervisor, who decides whether a dated addendum is
warranted. Nothing in §1–§5 depends on it.

---

## 8. Artifacts, and the shas that bind them

Every number above cites a file that is on disk and committed. **A number whose
artifact is gone is not a result.**

| what | path / sha |
|---|---|
| **pre-registration (frozen, as it ran)** | `cases/ansys_verification/VMFL005/PREREGISTRATION.md` blob **`43aaf6bf5c5f1189495e1460e5de415e56860447`**, commit **`2d54a629`**, 2026-08-24T18:42:07Z. No amendment, no addendum |
| **comparator (frozen, as it ran)** | `cases/ansys_verification/VMFL005/grade_vmfl005.py` blob **`8e7410cc356c3e175fe0d993efa366d51085ba81`** |
| **run script (frozen, as it ran)** | `cases/ansys_verification/VMFL005/run_vmfl005.sh` blob **`06056e18a9fee92e2e8765b279ae31f5373c62c5`** |
| **worktree == committed** | all three worktree copies re-hashed by this lane with `git hash-object` and found **byte-identical** to the blobs above |
| **HEAD at run** | **`22abb11de3ad82b8324e5148cbd3fdae7f9cff46`** — derived, not read from a launch record: the first run artifact is 18:45:32Z and `22abb11d` (18:45:04Z) is the newest commit at or before it. **HEAD moved during the run** (`10b3e97c` 18:45:38Z → `792acd8f` 18:48:47Z, all peer commits in other teams' territories, none touching `cases/ansys_verification/VMFL005/` or the run tree), so a single "HEAD at run" is an approximation. **What is exact, and is what actually binds the run, is the per-level `prereg_blob` stamp** — all three `RUN_RC.txt` carry `43aaf6bf…`, identical to HEAD's blob |
| grading JSON | `verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json` |
| grading stdout | `verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.stdout.txt` |
| cost | `verification/runs/ansys_verification/VMFL005/COST.txt`; per level `<level>/RUN_RC.txt` |
| **gate sources** | `<level>/postProcessing/pInletMonitor/0/surfaceFieldValue.dat` and `<level>/postProcessing/pOutletMonitor/0/surfaceFieldValue.dat`, all three levels. **These match `.gitignore:67` `**/postProcessing/` and are invisible to `git add`; they were filed deliberately by explicit path via `git update-index --add`, which does not consult the ignore rules** (L-300) |
| logs per level | `<level>/log.blockMesh`, `log.checkMesh`, `log.simpleFoam` |
| mesh birth certificate | `<level>/log.checkMesh` — `Mesh OK` ×3 |
| inlet code provenance | `<level>/dynamicCode/poiseuilleInlet/fixedValueFvPatchFieldTemplate.{C,H}`, `Make/SHA1Digest` = `_9d9f75ceaa7aae19ef2f8f01cb1a11f7a87fb674` ×3 |
| register | `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` row **#3** |
| numerics | `docs/NUMERICS_KNOWLEDGE.md` **`N-AV7`**, **`N-AV8`** |
| docket | `docs/DOCKET.md` **`D510`** |
| calibration | `docs/COST_CALIBRATION.md` **`C-47`** |
| manual | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt` lines 1170–1218 (= PDF p. 25) |

**Not committed, by design:** `constant/polyMesh/` (regenerable from the committed
`blockMeshDict`), the field time directories (`0/`, `2000/`, `3000/`, `6000/`, all
regenerable from the committed case at the shas above), and the `dynamicCode` **build
products** — `*.so`, `*.o`, `*.dep`, and `Make/<platform>/{options,sourceFiles,variables}`.
Those last are compiler output and machine-specific absolute paths, not evidence; the
generated `.C`/`.H` source and OpenFOAM's own `SHA1Digest` **are** committed, because
they are what proves which inlet code ran.

---

## 9. What this rung does NOT claim

- **Nothing about Ansys.** No Fluent, no CFX, no VM2026R1 archive opened by this rung.
- **Nothing about the mechanism of the 0.5 % residual.** §5.3 lists candidates and
  measures one geometric fact; it asserts no cause, and `D510` carries the question.
- **Nothing about whether the residual is pipeline-borne.** VMFL007 is the test and it
  has not been run.
- **Nothing about turbulent pipe flow.** The case is steady and laminar at Re = 500;
  VMFL003 (turbulent pipe, k-ε) is a different rung.
- **Nothing about 3D.** This is a one-cell-thick axisymmetric wedge.
- **Nothing about the entrance region.** No axial pressure profile was sampled, so
  dP/dx along the pipe is not measured and is not claimed to be constant.
- **Only the `PASS` is a credential** (`ANSYS_VERIFICATION_CHARTER.md` §6). It is one
  case of one manual against one analytic reference in this lab, and it is not
  evidence about any other case in the suite.

---

## 10. VERIFY — what this lane did not personally check

- **The comparator's correctness beyond its own controls.** It refuses rather than
  degrades, its planted-zero control fired, and it returned exit 0 — but this lane did
  not re-implement the extraction. The **supervisor's personal diff read** of
  `8e7410cc` and its **independent recomputation of every number from the raw
  `surfaceFieldValue.dat` files** (`SUPERVISION_CHARTER.md` §3 checks 1 and 3, done
  before this record was commissioned) are the checks that stand behind it.
- **Check 4** (freeze committed before compute) was done **by the supervisor
  personally**; this lane re-derived only the blob hashes and the artifact timestamps,
  which agree with it.
- **The manual's printed target itself** was read from the sidecar (lines 1170–1218),
  not from the PDF; the PDF's title-page verification is carried from a previous
  lane's report (CLAUDE.md rule 15).
- **`N-AV` and `L-` tails** were re-derived from HEAD in the commit invocation that
  used them; the **`D-` tail** was re-derived after running
  `scripts/check_docket_reconciliation.py`, which reported the worktree docket **25
  rows behind HEAD** (D485–D509 present in HEAD, absent in the worktree) — so the
  docket row was built **from the HEAD blob**, never from the worktree copy.
- **Contention during the run** — not characterised, see §7.1.

---

## Dated correction — 2026-08-25 — every `D510` citation in this record is wrong; the open question is `D512`

This record cites docket **`D510`** for the VMFL005 open-mechanism question in four
places — §5.3 ("Docketed as `D510`" and "…`D510` carries the question"), the §... summary
row (`| docket | docs/DOCKET.md `D510` |`), and the surrounding prose. **`D510` is
wrong.** `docs/DOCKET.md` `D510` is the closure team's R3 SpaRTA ratification, an
unrelated item (the id was written into this record before it was appended to the
docket — the collision `L-292` names). The VMFL005 open-mechanism question was opened
under a genuinely free id, **`D512`**, at commit `20afae1b` (2026-08-25),
`docs/DOCKET.md` `D512`, carrying §5.3's candidates and the `N-AV9` wedge-geometry
arithmetic (which quantifies the planar-wedge azimuthal area deficit as a
quarter-to-half contributor, not the resolution).

**Read `D512`, not `D510`, everywhere this record says `D510`.** The register carries the
same correction at its foot. The body above is left unedited (CLAUDE.md rule 6 spirit);
this note is the correction of record.

**Lines whose number changed above this section: 0.**
