# VMFL001-R2 — Flow Between Rotating and Stationary Concentric Cylinders: RESULTS

**NOT FILED ANYWHERE. Nothing in this document is sent, emailed, uploaded, filed,
posted, registered or commented outside this box, now or ever** (CLAUDE.md rules 7
and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is proprietary Ansys
documentation. **SUBMISSIONS PARKED.**

**This file does not revise `PREREGISTRATION.md` and cannot.** The gate (2 % vs the
manual's printed targets at all four radii, at L3), the exact-formula diagnostic
(0.5 %), the Roache quantity (v_θ at r = 35 mm), the per-level endTimes, the cap
(10 core-min) and the labels were frozen at blob **`c6b4a7c4`** (commit `4507fc66`)
**before any R2 solver started**, and nothing here edits a line of that file
(CLAUDE.md rules 2 and 6).

**Written 2026-08-24T18:19:35Z (`date -u`) by `ansys-lane-opus`**, on the
`ansys-verification-supervisor`'s launch authorisation, which followed its own
personal read of the R2 comparator diff (`8cb29610` → `64b02be8`) —
`SUPERVISION_CHARTER.md` §3 checks 1 and 4. **No agent message is Sanaa's consent**
(CLAUDE.md rule 9); the compute here is under the 2026-08-21 CPU blanket at a
per-item cost of $0.0028 derived, which is a per-item read and not a new ceiling.

---

## 1. VERDICT

# `PASS`

**v_θ(35 mm) = 0.00454578 m/s against the manual's printed target 0.0046 m/s —
deviation 1.179 %, inside the frozen 2 % gate**, and all four radii are inside it.
The grid triple on that quantity is **`CONVERGING`** at observed order
**p = 2.0102** with **GCI_fine = 0.0563 %**, so rule 5 step 2 does not turn the row
into `NOT A RESULT`; all three levels are iteratively converged and plateaued, so
step 1 does not either. The planted-zero control fired and was read back from disk
exactly.

**This is a statement about this lab's OpenFOAM v2606 run of this case against the
manual's reference result. It is not a statement about Ansys**
(`ANSYS_VERIFICATION_CHARTER.md` §2). This box has no Fluent and no CFX;
`rot_conc_cyl.cas` and `rotating_cylinder.def` were not run, and no VM2026R1 archive
was opened. Fluent's and CFX's own numbers are context in §3, never the gate.

**This rung cites run 1 and does not re-grade it.** Run 1 is
`cases/ansys_verification/VMFL001/RESULTS.md`, verdict **`NOT A RESULT`**, register
row **#1**, commits `ae30f914` and `dee5870d`. That verdict stands unchanged, is not
removed, re-labelled or softened, and this row is **register row #2 citing row #1**
(`VERIFICATION_CHARTER.md` §6; `PREREGISTRATION.md` §0–§1).

---

## 2. What ran

`run_vmfl001_r2.sh` (frozen blob **`116c7c2d`**) built and ran all three levels
serially at **HEAD = `1fb3bf74d7a7e8281926303e9c36ce48dccfe0ec`**, finishing
2026-08-24T18:14:02Z. The script re-read the pre-registration blob at launch and
printed `pre-registration frozen at blob c6b4a7c4…` before starting; each level's
`RUN_RC.txt` carries that same blob, so the freeze is recorded by the run itself and
not only asserted here.

| level | cells (`log.checkMesh`) | registered cells | endTime | rc | wall s | core-min | finished (UTC) |
|---|---|---|---|---|---|---|---|
| `L1_16x64` | **1024** | 16 × 64 = 1024 ✅ | 3000 | 0 | 2 | 0.0333 | 18:10:47Z |
| `L2_32x128` | **4096** | 32 × 128 = 4096 ✅ | 3000 | 0 | 12 | 0.2000 | 18:10:59Z |
| `L3_64x256` | **16384** | 64 × 256 = 16384 ✅ | **6000** | 0 | 183 | 3.0500 | 18:14:02Z |
| **total** | 21,504 | | | | **197** | **3.2833** | |

`checkMesh` returns **`Mesh OK`** at all three levels (mesh birth certificate,
`VERIFICATION_CHARTER.md` §9). No `CAP_EXCEEDED.txt` exists; the run used **32.8 %**
of the 10 core-minute cap.

### 2.1 Pre-compute freeze verification (rule 2, and `PREREGISTRATION.md` §8)

Before the solver started, every file of the grading path was hashed in the worktree
and compared to its committed blob at HEAD. **All eleven tracked files under
`cases/ansys_verification/VMFL001/R2/` matched their HEAD blobs byte for byte** —
the comparator `64b02be8`, the run script `116c7c2d`, this rung's pre-registration
`c6b4a7c4`, and all eight files under `case/`. The run directory
`verification/runs/ansys_verification/VMFL001/R2/` was confirmed **absent** with
`ls -d` immediately before launch, and the run script's own guard 1 (refuse if any
level directory pre-exists) was live on top of that.

**One untracked artifact was found and is disclosed:** a stale
`R2/__pycache__/grade_vmfl001_r2.cpython-312.pyc`, mtime 17:59:44Z, **39 seconds
older than the comparator source it was compiled from** (18:00:23Z) — i.e. compiled
from a pre-supervisor-edit version of the comparator. CPython would have recompiled
it on the mtime/size mismatch, so it could not in fact have shadowed the frozen
comparator; it was nonetheless **deleted before grading** and `PYTHONDONTWRITEBYTECODE=1`
was set for the grading invocation, so the comparator that ran is unambiguously the
source at blob `64b02be8`. No tracked file was touched.

### 2.2 Strict completion rule (CLAUDE.md rule 4, per-level endTime per `PREREGISTRATION.md` §6)

All six clauses hold at **all three** levels, read from the artifacts and not
inferred. The comparator checks these itself and refuses (exit 2) on any failure; it
did not refuse.

| clause | L1_16x64 | L2_32x128 | L3_64x256 |
|---|---|---|---|
| 1. `rc = 0` (`RUN_RC.txt`) | ✅ | ✅ | ✅ |
| 2. `End` line in `log.simpleFoam` (count) | ✅ 1 | ✅ 1 | ✅ 1 |
| 3. last time == that level's `endTime` | ✅ 3000 | ✅ 3000 | ✅ **6000** |
| 4. `U` and `p` present at `endTime` | ✅ | ✅ | ✅ |
| 5. `ExecutionTime` line count == `endTime` | ✅ 3000 | ✅ 3000 | ✅ **6000** |
| 6. age guard: fields at `endTime` newer than the case's own `0/U` | ✅ | ✅ | ✅ |

Time directories present are exactly `0` and the endTime at each level. `fvSolution`
carries no `residualControl`, so SIMPLE could not stop early and clause 3 is
meaningful rather than tautological.

### 2.3 Iterative convergence — and whether the N = 6000 extrapolation held

This is the clause that made run 1 `NOT A RESULT`, so it is reported in full. The
registered clause (`PREREGISTRATION.md` §4 step 1) is: final `Ux`, `Uy` **and** `p`
initial residuals **< 1e-6**, and the monitor probe's peak-to-peak over the last
20 % of iterations **< 1e-6 m/s**.

| level | final `Ux` | final `Uy` | final `p` | plateau ptp (m/s) | plateau window | converged |
|---|---|---|---|---|---|---|
| `L1_16x64` | 4.69187e-14 | 4.56645e-14 | 6.50871e-11 | 1.00e-14 | last 600 | ✅ |
| `L2_32x128` | 1.48771e-12 | 1.48751e-12 | 4.85296e-11 | 1.27e-11 | last 600 | ✅ |
| `L3_64x256` | **1.61027e-09** | **1.61026e-09** | **8.42766e-11** | **1.77237e-07** | last 1200 | ✅ |

**The N = 6000 extrapolation HELD, and it is stated plainly because it was the whole
justification for change (d).** `PREREGISTRATION.md` §3.2 fitted run 1's L3 `Ux`
residual decay over iterations 2000→3000 at **−9.6065×10⁻⁴ decades/iteration** and
predicted **≈ 1.57×10⁻⁹ at iteration 6000**. The measured value at iteration 6000 is
**1.61027×10⁻⁹** — **ratio 1.026, a 2.6 % miss on a two-decade extrapolation across
3000 iterations**. The registered criterion is 1e-6 and the achieved residual is
**620× below it**; the two-decade margin the freeze asked for (< 1e-8) is met with
room. L3's plateau ptp is **1.772e-07 m/s**, **5.6× inside** the 1e-6 m/s clause,
against run 1's 2.772e-05 m/s which was 27.7× outside it.

For the record, run 1's L3 at iteration 3000 read `Ux` = 1.19876e-06 (outside) and
ptp = 2.77178e-05 m/s (outside). Both mechanisms of run 1's `NOT A RESULT` are
therefore repaired and **measured** to be repaired, not assumed.

---

## 3. The gate — four values against the manual's printed targets

**THE FROZEN GATE:** at L3, |v_lab(r) − v_manual(r)| / |v_manual(r)| ≤ **0.02** at
**all four** radii. Source: `verification/runs/ansys_verification/VMFL001/R2/L3_64x256/postProcessing/radialProbes/6000/gateAxis_p_U.xy`.

| r (mm) | **v_lab, m/s** | manual target, m/s | **dev vs manual** | gate (2 %) | exact v_θ, m/s | **dev vs exact** | diagnostic (0.5 %) |
|---|---|---|---|---|---|---|---|
| 20 | **0.0151121317** | 0.0151 | **0.0803 %** | ✅ | 0.0151201250 | **0.0529 %** | ✅ |
| 25 | **0.0105287949** | 0.0105 | **0.2742 %** | ✅ | 0.0105336000 | **0.0456 %** | ✅ |
| 30 | **0.0071835454** | 0.0072 | **0.2285 %** | ✅ | 0.0071865648 | **0.0420 %** | ✅ |
| 35 | **0.0045457781** | 0.0046 | **1.1787 %** | ✅ | 0.0045478095 | **0.0447 %** | ✅ |

**All four inside the 2 % gate ⇒ the gate is MET.** The frozen 0.5 % diagnostic
against the exact White §3-2.3 formula is **also met at all four radii** — the worst
deviation from the analytic solution anywhere is **0.0529 %**, an order of magnitude
inside the diagnostic. The diagnostic is not the gate and does not change the
verdict; it is printed beside it as registered.

**The 35 mm row is the interesting one and the freeze predicted why.** Its 1.179 %
deviation is the largest of the four and is dominated by **the manual's own printed
rounding**, not by this lab's solver: the manual prints 0.0046 where the exact value
is 0.00454781, a rounding worth **1.148 %** on its own. Against the exact formula the
same lab value deviates by **0.0447 %** — i.e. **97 % of the 35 mm gate deviation is
the manual's rounding of its own target**, exactly the justification frozen in
`PREREGISTRATION.md` §2 before any number was seen.

**Ansys's own numbers, context only and never the gate**
(`ANSYS_VERIFICATION_CHARTER.md` §2), manual Tables .01.1 and .01.2 at pp. 15–16:
Fluent 0.0151 / 0.0105 / 0.0072 / **0.0045** (worst ratio 0.978 at 35 mm); CFX
0.0150 / 0.0105 / 0.0071 / 0.0045 (worst ratio 0.988 at 30 mm). This lab's L3 value
at 35 mm, 0.0045458, sits between Fluent's printed 0.0045 and the exact 0.0045478.
Nothing is claimed about Fluent or CFX from this.

---

## 4. Roache triple on v_θ(35 mm) — CLAUDE.md rule 5

Refinement ratio **2.0** exactly in both directions; Fs = **1.25**; the quantity is
the manual's worst-agreement point, as frozen.

| quantity | value |
|---|---|
| coarse `L1_16x64` (1024 cells) | **0.0045145840 m/s** |
| medium `L2_32x128` (4096 cells) | **0.0045395745 m/s** |
| fine `L3_64x256` (16384 cells) | **0.0045457781 m/s** |
| d32 = f_med − f_coarse | −2.4990511e-05 |
| d21 = f_fine − f_med | −6.2035594e-06 |
| **R = d21/d32** | **0.2482366** |
| **state** | **`CONVERGING`** |
| **observed order p** | **2.0102123** |
| **GCI_fine (Fs = 1.25)** | **5.632839e-04 = 0.0563 %** |
| **Richardson extrapolated f** | **0.0045478265 m/s** |

**`CONVERGING`**, so rule 5 step 2 does not fire and the gate verdict stands. The
three values are **monotone** (increasing with refinement toward the analytic value),
so the GCI is quotable and is quoted. **R = 0.248 ≈ 1/4** and **p = 2.0102 ≈ 2** —
the observed order matches the formal second order of the frozen `fvSchemes` to
**0.5 %**, on a mesh family refined by exactly 2.

**The extrapolated value lands on the analytic solution to 3.7 parts per million.**
Richardson extrapolation of the three levels gives **0.00454782654 m/s**; the exact
White §3-2.3 value is **0.00454780952 m/s**. The difference is **1.70e-11 m/s =
0.000374 %** — three orders of magnitude finer than the finest grid's own 0.0447 %
discretisation error, and it is an *independent* check: the extrapolation uses only
the three lab values and the refinement ratio, and never sees the analytic formula.

---

## 5. Planted-zero control (CLAUDE.md rule 3) — it fired

The comparator copied L3's sampled `gateAxis_p_U.xy` to a temp tree, added
**PLANT = 1.234×10⁻³ m/s** to the derived `U_y` column (index 5 of
`x y z p U_x U_y U_z`) of the r = 35 mm row, **read it back from disk**, and re-ran
the same extraction.

| channel | value |
|---|---|
| planted | **1.234000e-03** |
| **read_back_delta** (what the file on disk changed by) | **1.234000e-03** |
| **reader_delta** (what the extractor reported) | **1.234000e-03** |
| agreement with PLANT | **exact to 1e-15 m/s** (residual ≈ 1e-19) |
| file | `gateAxis_p_U.xy` |
| **passed** | **`True`** |
| other radii moved | **none** |

**The reader is demonstrated able to see a non-zero in this exact file format**, on
the real L3 output, before its zeros are believed. This is the control run 1 never
reached — run 1's reader refused before it could plant anything.

---

## 6. Levers and the axisymmetry diagnostic

**Levers, read from the run tree by the comparator at every level** (not from the
case source): **ν = 2.0×10⁻⁴ m²/s** ✅ (manual: μ = 0.0002 kg/m-s, ρ = 1 kg/m³),
**ω = 1.0 rad/s** ✅ (manual: inner wall 1 rad/s), **`laminar`** confirmed
active-in-log ✅ at all three levels, and cells **1024 / 4096 / 16384** with
`mesh_ok` true at all three ✅. Every lever matches what `PREREGISTRATION.md` §2
registered and what the manual specifies at p. 15.

**Azimuthal spread diagnostic** — the `azimuthCheck` set samples **8 azimuthal
positions** at each gate radius. The analytic solution is axisymmetric, so any
spread is numerical asymmetry introduced by the mesh or the solver:

| level | worst spread across the four radii (m/s) | at |
|---|---|---|
| `L1_16x64` | **6.78e-14** | r = 25 mm |
| `L2_32x128` | **4.96e-14** | r = 25 mm |
| `L3_64x256` | **3.10e-13** | r = 25 mm |

**Worst anywhere: 3.10e-13 m/s, which is 6.8×10⁻¹¹ of the local value** — machine
precision. The solution is axisymmetric to round-off at every level, so the four
gate values are properties of the radial discretisation and not artefacts of one
azimuthal ray. The mild growth with refinement is consistent with accumulated
round-off over 4× the cells and 2× the iterations, not with a physical asymmetry.

---

## 7. Cost (CLAUDE.md rule 12) — estimate versus actual

| item | value |
|---|---|
| ranks | **1 (serial)**; core-min = wall_s × 1 ÷ 60 |
| **predicted** (`PREREGISTRATION.md` §7) | **3.7167 core-min** (223 wall s) = **$0.003178 derived** |
| **CAP** | 10 core-min = $0.008550 derived — **not approached** (32.8 % used) |
| **actual, MEASURED, gross** | **3.2833 core-min** (197 wall s) — `COST.txt`, corroborated by the three `RUN_RC.txt` |
| **actual, cleaned** | **= gross, 3.2833 core-min.** Longest single wall is 183 s, an order and a half below the 3600-s stall rule (`COMPUTE_BUDGET_CHARTER.md` §2), so stall cleaning removes nothing |
| **dollars** | **$0.002807 DERIVED, NOT MEASURED** (3.2833 ÷ 60 × $0.0513/core-h) |
| **ratio actual/predicted** | **0.8834×** — inside the estimate, in the conservative direction |
| `cost_basis` | owner-stated rate **$0.0513/core-h**, c7a.4xlarge, Sanaa 2026-08-21/22 — **reported-by-owner, not measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **waste** | **0.000 core-min**, named separately per §6 and netted off nothing: no level failed, no level restarted, no level was capped, and the comparator returned exit 0 on its first invocation |

**Per level, against the frozen basis:**

| level | predicted wall s | actual wall s | ratio |
|---|---|---|---|
| `L1_16x64` | 2 | 2 | **1.00×** |
| `L2_32x128` | 13 | 12 | **0.92×** |
| `L3_64x256` | **208** | **183** | **0.88×** |

**Attribution — misprediction only, mechanism named, conservative direction.** The
gap is entirely L3 and its mechanism is the **linear scaling assumption in change
(d)**: §7 scaled run 1's measured 104 s / 3000 iterations to 208 s / 6000 iterations
at constant cost per outer iteration. Measured per-outer-iteration cost was
**34.67 ms in run 1's first 3000** and **30.50 ms across R2's 6000** — the second
3000 iterations are **cheaper**, because as the residuals fall the inner linear
solves converge in fewer sweeps. At iteration 6000 the log shows `Ux` taking **4**
smoothSolver iterations and the second `p` GAMG solve taking **0**. **Transferable
rule for the next estimate: extending a converging steady SIMPLE run's endTime is
sub-linear in wall time — scaling by N/N₀ over-estimates, here by ≈ 12 %; price a
continuation at ≈ 0.88 × linear.**

**Contention: present, and it makes the gap wider rather than narrower.** Three
T-family solvers (heat-transfer team) were live on the 16-core box for the whole of
this run — checked with a `find -mmin -10` sweep over `verification/runs/` before
launch. Contention pushes serial wall time **up**, so the no-contention cost would be
lower still and the 0.88× is if anything an under-statement of the over-estimate. No
load figure was taken, so **no numerical contention penalty is claimed** — only its
direction.

Landed as calibration row **C-45** in `docs/COST_CALIBRATION.md`.

---

## 8. Artifacts, and the shas that bind them

Every number above cites a file that is on disk and committed. A number whose
artifact is gone is not a result.

| what | path / sha |
|---|---|
| **pre-registration (frozen, as it ran)** | `cases/ansys_verification/VMFL001/R2/PREREGISTRATION.md` blob **`c6b4a7c4fd09d2286a30440f5090116a7dae0eea`**, commit `4507fc66` |
| **comparator (frozen, as it ran)** | `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py` blob **`64b02be807a8adb6c2638fe739c55f735c8259ca`** |
| **run script (frozen, as it ran)** | `cases/ansys_verification/VMFL001/R2/run_vmfl001_r2.sh` blob **`116c7c2d5fc5ebe1ac742f69478d66ed37dbfc17`** |
| **HEAD at run** | **`1fb3bf74d7a7e8281926303e9c36ce48dccfe0ec`** |
| grading JSON | `verification/runs/ansys_verification/VMFL001/R2/GRADING_VMFL001_R2.json` |
| grading stdout | `verification/runs/ansys_verification/VMFL001/R2/GRADING_VMFL001_R2.stdout.txt` |
| cost | `verification/runs/ansys_verification/VMFL001/R2/COST.txt`; per level `<level>/RUN_RC.txt` |
| gate source (L3) | `…/R2/L3_64x256/postProcessing/radialProbes/6000/gateAxis_p_U.xy` |
| logs per level | `…/R2/<level>/log.blockMesh`, `log.checkMesh`, `log.simpleFoam` |
| **run 1, cited not re-graded** | `cases/ansys_verification/VMFL001/RESULTS.md`, verdict `NOT A RESULT`, register row **#1**, commits `ae30f914` / `dee5870d`, prereg blob `d6ea5de9`, comparator blob `8cb29610` |
| register | `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` row **#2**, citing row #1 |
| manual | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt` lines 896–960 (= PDF pp. 15–16) |

**Not committed, by design:** `constant/polyMesh/` and the field time directories
(`0/`, `3000/`, `6000/`) — regenerable from the committed `blockMeshDict` templates
and the frozen case at the shas above.

---

## 9. What this rung does NOT claim

- **Nothing about Ansys.** No Fluent, no CFX, no VM2026R1 archive on this box.
- **Nothing about the transport properties beyond the lever check** — the gated
  v_θ(r) of the analytic solution is independent of ν and ρ, so this case cannot
  verify them and does not try.
- **Nothing about 3-D, transitional or turbulent operation.** The case is steady,
  laminar, and solved on a planar 360° annulus with `empty` front and back.
- **Nothing about run 1.** Run 1's `NOT A RESULT` is a permanent row; this rung
  repairs the two mechanisms and reports its own numbers.
- **Only the `PASS` is a credential** (`ANSYS_VERIFICATION_CHARTER.md` §6). It is one
  case of one manual, verified against one analytic reference, in this lab, and it is
  not evidence about any other case in the suite.
