# RESULTS — VMFL038: Falling Film Over an Inclined Plane

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — printed p.131-132.**
Reproduced in this lab's OpenFOAM `simpleFoam` (v2606); this box has no Ansys solver, so
nothing here is a statement about Ansys. Reference is Bird, Stewart & Lightfoot's analytical
falling-film wall shear (the manual's own cited reference), an exact solution of the same
continuum model the solver discretises.

Written by `ansys-lane-opus48` on **2026-08-31**, in the RUN ROOT (FILING_CHARTER: run outputs
live under `verification/runs/<CAMPAIGN>/`, never beside the prose; standing ruling of this team,
matching row #46 / VMFL069-R2). This record VERIFIES a verdict the frozen comparator already
returned; it does not re-grade and edits no frozen file. **No solver was re-run.**

---

## VERDICT: NOT A RESULT

Triple **DIVERGENT** (R = 9.051), so the row is `NOT A RESULT` whatever the value (CLAUDE.md
rule 5, one-way). Read from the machine-readable grading record, not from stdout:
`R["verdict"] = "NOT A RESULT"`, `R["triple"]["state"] = "DIVERGENT"`, `p = None`, `gci_fine =
None`. No GCI is quoted, and none is quotable (see the DIAGNOSIS).

| quantity | value | provenance |
|---|---|---|
| `tau_w` L1 / L2 / L3 | **39.234403 / 39.209012 / 38.979197 Pa** | MEASURED (comparator, `wallShearStress` FO ×RHO=800) |
| finest (L3) vs analytical 39.24 Pa | deviation **0.6646 %**, band **2.0 %** | MEASURED — inside the band on value, but the band is not reached because the triple is not CONVERGING |
| Roache convergence ratio | **R = d32/d21 = 9.051** (d21 = −0.025391, d32 = −0.229815) | MEASURED |
| triple state | **DIVERGENT** (R > 1, both differences same sign) | MEASURED |
| observed order p, fine-grid GCI | **not quoted** (None) — rule 5 forbids a GCI on a non-CONVERGING triple | MEASURED |
| velocity DIAGNOSTIC (not gated) L3 | u_max 0.194458 (analytic 0.1962), RMS/u_max 6.123e-03, machine_exact = False | MEASURED |

The cost was **7.75 core-min MEASURED** against a 15 core-min cap and a 6 core-min estimate
(calibration row C-228; ratio 1.292).

---

## (A) VERIFICATION OF THE VERDICT — done, not accepted

### A1. Freeze integrity (CLAUDE.md rule 2)
`git hash-object` on disk vs the blob at the freeze commit `c5ae8427a1e649b61a6362daa6b988911075fb2c`
and at HEAD, for all three frozen files — **IDENTICAL in every cell**:

| file | disk | @c5ae8427 | @HEAD | recorded blob |
|---|---|---|---|---|
| `PREREGISTRATION.md` | a1ac0104… | a1ac0104… | a1ac0104… | a1ac010431a3e65f8a4ee9af8b0edadf81d1f248 ✓ |
| `grade_vmfl038.py` | 04a2606e… | 04a2606e… | 04a2606e… | 04a2606e11ecfb36dd59e65606aab6f8e9990d38 ✓ |
| `run_vmfl038.sh` | 83e897ba… | 83e897ba… | 83e897ba… | 83e897ba2efdc83431b60eabc5ef2cb1df89b907 ✓ |

The three `RUN_RC.<level>` files independently record `prereg_blob = a1ac0104…` and
`comparator_blob = 04a2606e…`, so **the launcher hashed the same bytes the verification hashed**.
The launcher's own `LAUNCH_RECORD.txt` records `freeze_commit_head = 5bd012b4…` (HEAD at launch
15:43:48Z), which is 4 min after the freeze commit c5ae8427 (15:39:34Z) — HEAD moved on peer
commits in between, but the three frozen files are **byte-identical between c5ae8427 and 5bd012b4**
(`git diff --stat` empty), so the move touched nothing graded. Age guard intact (supervisor-
established): the run root did not exist at the freeze; only `0/` + one graded time dir per level.

### A2. The instrument is not a one-answer instrument (planted-zero of the grader)
`grade_vmfl038.py --selftest`: **52 checks, 0 failures, rc 0** under BOTH `python3` and
`python3 -O` (`__pycache__` cleared before each). PASS, GATE FAIL and NOT A RESULT are each
proven REACHABLE end-to-end in the selftest — `verdict PASS` (CONVERGING, in band, GCI ≤ max),
`verdict GATE FAIL` (CONVERGING, out of band), `verdict NOT A RESULT` (EXACT triple; GCI > GCI_MAX;
non-CONVERGING inside band). `roache DIVERGENT` is exercised on `roache(39.0, 39.1, 39.3)`, the
same shape as the real data. AST guard: `ast.Assert` count 0.

### A3. Verdict read from the JSON, not the stdout
Re-graded through the frozen comparator with
`--out verification/runs/ansys_verification/VMFL038/GRADING_RECORD_2026-08-31T1710Z.json`;
`R["verdict"]` and `R["limb_A"]["verdict"]` both read **NOT A RESULT** directly from the JSON;
triple DIVERGENT, `R["triple"]["R"] = 9.051035629030038`, `p = None`, `gci_fine = None`,
`R["planted_zero"][*]["passed"] = [True, True, True]`, `ast_assert_count = 0`.

**Correction, 2026-08-31T17:10Z, by the lane that landed this record.** The first grading pass
(stdout at `GRADING_STDOUT_2026-08-31T1605Z.txt`, 16:05Z) wrote its JSON **to the scratchpad**, which
is temp only and is not a durable artifact (`CLAUDE.md` rule 13 / L-186). The JSON was therefore gone
by the time this record was written, and both this section and the register row cited a
machine-readable grading record **that was not on disk** — a number whose artifact is gone is not a
result. The frozen comparator was re-run at 17:10Z (post-processing only; it plants into `tempfile`
copies and mutates no run data) with `--out` pointed **into the run root**, and the artifact above is
that output. It reproduces the 16:05Z stdout value-for-value: `tau_w` 39.234403 / 39.209012 /
38.979197 Pa, deviation 0.6646 %, triple `DIVERGENT`. **No gate, threshold, cap or label changed and
the case was not re-run.**

### A4. Strict completion (CLAUDE.md rule 4) — the registered clause, on its own terms
This case stops on `residualControl { p 1e-10 }`, **not** at endTime. The frozen PREREGISTRATION
§6 registered a **declared adaptation** of rule 4's "last == endTime": for a residualControl-
terminated steady solve the passing condition is **last Time STRICTLY LESS THAN endTime** (last ==
endTime would mean it ran out of clock without converging), plus the final `Ux` initial residual
< `ITER_RES_FLOOR = 1e-5`. All clauses hold at every level, checked with LINE-ANCHORED patterns
(`^Time = `, `^ExecutionTime`, `^End`) — a bare `Time = ` also matches inside every `ExecutionTime = `
line and doubles the count (measured: bare count 4186/10680/26660 = exactly 2× the anchored count):

| level | ^Time = | ^ExecutionTime | last Time < endTime 30000 | ^End | ^SIMPLE converged | rc | final Ux init resid < 1e-5 |
|---|---|---|---|---|---|---|---|
| L1 | 2093 | 2093 | 2093 ✓ | 1 | 1 | 0 | 7.889e-07 ✓ |
| L2 | 5340 | 5340 | 5340 ✓ | 1 | 1 | 0 | 1.467e-06 ✓ |
| L3 | 13330 | 13330 | 13330 ✓ | 1 | 1 | 0 | 3.721e-06 ✓ |

The NOT A RESULT is therefore **not** a completion failure. The solve completed on its own
registered criterion; the verdict is driven purely by the DIVERGENT triple.

### A5. Planted-zero control (CLAUDE.md rule 3) — FIRED AND PASSED AT ALL THREE LEVELS
The sized all-face plant is written to disk into a COPY of the real solver bytes and read back
through the production reader; `passed = True` at L1, L2, L3, worst readback error ~1e-14, and the
gate functional moved by exactly `RHO·plant` (gate_move vs expected agree to ~1e-11 Pa). This
closes the L1-only weakness carried by rows #44 (VMFL063) and #46 (VMFL069-R2).

---

## (B) DIAGNOSIS — why the triple diverged

### B1. The certain, load-bearing finding: the refinement sequence is ANISOTROPIC, so a Roache/GCI triple does not apply to it
The mesh is uniform hex, `simpleGrading (1 1 1)` (uniform in both x and y; checkMesh
non-orthogonality 0). But **only Ny refines**: Nx is FIXED at 180, Ny = 40/80/160, cells
7200/14400/28800 (×2 per level, not ×4), so the near-wall cell aspect ratio degrades **4 → 8 → 16**.
Richardson extrapolation and the Roache GCI (Fs = 1.25) are derived for **systematic refinement by a
constant ratio in ALL directions**, characterised by a single representative mesh size h whose
reduction scales the whole truncation error. A y-only sequence has **no single h** with that
property: the streamwise truncation is a fixed floor that does not scale, and the aspect ratio
changes level to level. **Therefore an observed order p and a fine-grid GCI are NOT QUOTABLE on this
sequence**, and the row quotes neither. The frozen comparator, correctly, returns `p = None`,
`gci = None` because the state is DIVERGENT — but the deeper point is that even a monotone-converging
outcome would not have entitled this sequence to a p or a GCI. NOT A RESULT is correct, and correct
for the strong reason that **the sequence does not satisfy the premise of the method applied to it**,
not merely because the triple came out DIVERGENT.

This is a defensible design that carries an undisclosed cost, not a concealment: for a fully-developed
unidirectional film the solution is x-invariant in the graded window, so refining only y is a
legitimate systematic refinement of the functional's dominant (film-normal) truncation, and it was
declared in the frozen bytes before compute (PREREGISTRATION §4). The finding is that the declared
design produces a refinement sequence to which Roache/GCI cannot be applied.

### B2. The discriminating measurement: velocity RMS GROWS under refinement
Per-level RMS(u − analytic)/u_max, from the comparator's own diagnostic:

| level | RMS/u_max | u_max sampled (analytic 0.196200) |
|---|---|---|
| L1 | **7.098e-05** | 0.196159 (0.02 % low) |
| L2 | **7.088e-04** | 0.195985 (0.11 % low) |
| L3 | **6.123e-03** | 0.194458 (0.89 % low) |

The velocity error **grows ~10× per r=2 level**. On a mesh uniform in y a 2nd-order scheme reproduces
the exact quadratic profile to round-off (the discrete Laplacian of a quadratic is exact), and in the
developed window the field is x-invariant so the fixed streamwise resolution contributes no
discretisation error either. A velocity error that GROWS with refinement is therefore not the
discretisation error of the developed profile — it is the solution moving further from the exact
steady state as the mesh refines. `tau_w` is read from the OpenFOAM `wallShearStress` function object
(= nuEff·snGrad(U), a one-sided near-wall gradient) ×RHO; as the near-wall velocity is progressively
under-resolved, that gradient reads progressively lower, so `tau_w` moves monotonically AWAY from
39.24 (39.234 → 39.209 → 38.979), which IS the DIVERGENT triple.

### B3. On the mechanism, an honest split — and a partial disagreement recorded
The design assumed the iterative wall-shear error is ≈ `res·tau_w` (comparator lines 80-82). Against
the observed miss from 39.24 Pa this model under-predicts by **181× / 538× / 1786×**, the shortfall
GROWING with refinement. That is why `res·tau_w` cannot be read as the whole story — **but it does not
establish that the error is non-iterative, because `res·tau_w` is not a valid iterative-error model**:
it assumes error ∝ residual with a mesh-INDEPENDENT constant. The data contradict that assumption
directly — the residual-to-error amplification (RMS/res) grows **90 → 483 → 1646**, i.e. **~4.3× per
level**, bracketing the AR² growth of 4.0× per level (AR doubling 4 → 8 → 16). The most defensible
reading is that the velocity error is **iterative under-convergence at the p-only termination whose
depth is amplified by the anisotropy-degraded conditioning of the momentum/pressure coupling (~AR²)** —
which is why "iterative" and "anisotropy" are the same coupled effect described from two sides, and why
the naive `res·tau_w` model fails by a factor that itself grows with AR.

**What cannot be separated on the frozen data, stated plainly:** "iterative error amplified by
anisotropy" vs "a genuine anisotropic discretisation floor" would be distinguished only by running L3
to a much tighter residual and seeing whether `tau_w → 39.24`. That is forbidden here — the case is
frozen and closed — and is answerable only by a **repair registration** (a NEW frozen registration, e.g.
adding `U` to residualControl or refining isotropically, graded as a new row citing this one). The
existing data give a directional hint without settling it: L1, the best-converged level (Ux residual
7.9e-7), also has the `tau_w` closest to analytic (39.234, 0.014 % low), so tighter convergence
plausibly moves `tau_w` toward 39.24 — but this is corroboration, not proof.

**Neither of the supervisor's two successive hypotheses is adopted wholesale.** The original
"residualControl inversion (same absolute residual = larger error)" over-simplified: the p residual is a
NORMALISED initial residual and is identical (~1.0e-10) at every level, so pressure is equally converged
everywhere. The later "iterative error cannot be the primary mechanism (per `res·tau_w`)" over-corrected:
the `res·tau_w` model it rests on is contradicted by the ~AR² amplification measured here. The finding
that survives both and is not in doubt is B1: **the anisotropic (y-only) sequence violates the Roache/GCI
premise, and the velocity error grows under refinement** — which is sufficient for NOT A RESULT and does
not depend on resolving the iterative-vs-discretisation split.

---

## (C) COST CALIBRATION (CLAUDE.md rule 12) — calibration row C-228
- Registered point estimate **6 core-min** (PREREGISTRATION §7); cap **15 core-min** (running total).
- MEASURED actual **7.75 core-min** (Σ RUN_RC core_min at RANKS = 1: L1 0.2333 + L2 1.3167 + L3 6.2).
- **Ratio actual/predicted = 1.292.** Attribution: misprediction of the iteration count, concentrated
  at L3 (the estimate rolled L3 up at ~4 core-min ∝ cells; actual 6.2, because the finer mesh needed
  6.4× more SIMPLE iterations — 13330 vs L1's 2093 — to drive p to 1e-10, growing faster than cells).
  Contention: negligible and NAMED SEPARATELY, never folded into the ratio — log ExecutionTime vs
  ClockTime give wall/CPU 1.039 (L1, 14 wall-s, tiny) / 1.0003 (L2) / 1.0004 (L3). **Waste: 0 core-min**,
  named separately (three levels launched, three completed rc = 0, no restart, no re-mesh, no abandoned
  partial). Cap 15 unspent by 7.25 core-min (48 % used). Dollars **DERIVED, not measured** at
  $0.0513/core-h (owner-stated, reported-by-owner; the box cannot read its own billing): actual
  **$0.006626**, estimate $0.00513, cap $0.012825. CPU only, under the $25 pre-authorisation.

---

## ARTIFACTS — committed vs on disk only
This team's standing ruling (Sanaa 2026-08-27 §1): solver logs and time directories stay OUT of git,
cited by absolute path with sizes and mtimes; the small evidence set is committed by explicit path.

**COMMITTED (explicit paths, no glob):** `RESULTS.md` (this file), `RUN_RC.L1/L2/L3`, `COST.txt`,
`LAUNCH_RECORD.txt`, `CONTENTION.txt`, `STATUS.VMFL038`, `GRADING_STDOUT_2026-08-31T1605Z.txt`,
`GRADING_RECORD_2026-08-31T1710Z.json` (the machine-readable grading record the verdict is read
from), `launcher.queue.out`, `L{1,2,3}/birth_certificate.json`.

**ON DISK ONLY, deliberately not in git** (run root total 27 MB):
- `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL038/L1/log.simpleFoam` — 1 105 394 B, mtime 2026-08-31T15:44:02Z
- `.../L2/log.simpleFoam` — 2 831 758 B, mtime 2026-08-31T15:45:21Z
- `.../L3/log.simpleFoam` — 7 097 609 B, mtime 2026-08-31T15:51:34Z
- time directories `L1/2093` (1020 K), `L2/5340` (2.0 M), `L3/13330` (3.9 M) and the `0/`, `constant/`,
  `system/` trees; `postProcessing/wallShearStress/…`.
- **STRUCK 2026-08-31T17:10Z** — ~~"The verification JSON grading record was written to scratch (not a
  repository artifact; L-186)."~~ That was true of the 16:05Z pass and is exactly why this record and
  the register row cited an artifact not on disk. The grading record is now a **committed run-root
  artifact**, `GRADING_RECORD_2026-08-31T1710Z.json` (see §A3 correction). Scratch is where it must
  NOT live; a grading record is the artifact a verdict cites, not a temp file.

Every number on this row cites an artifact still on disk. The comparator mutated nothing — it plants
into `tempfile` copies of the solver bytes, never the run's own files.

## Freeze / grading provenance
- Prereg blob `a1ac010431a3e65f8a4ee9af8b0edadf81d1f248`, frozen commit `c5ae8427a1e649b61a6362daa6b988911075fb2c` (2026-08-31T15:39:34Z), launch HEAD `5bd012b4…` (15:43:48Z).
- Comparator blob `04a2606e11ecfb36dd59e65606aab6f8e9990d38`; launcher blob `83e897ba2efdc83431b60eabc5ef2cb1df89b907`.
- Selftest 52/0/rc0 under python3 and python3 -O; JSON verdict NOT A RESULT.
