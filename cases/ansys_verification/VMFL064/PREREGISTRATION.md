# PRE-REGISTRATION — VMFL064: Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion

Frozen by sha before any solver starts (rule 2). Drafted by `ansys-lane-opus48` (Opus 4.8),
2026-08-26. Backward-facing step (asymmetric expansion), laminar, Re_D = 200.

1. **Case id + manual page:** VMFL064, VM2026R1 **p. 195/196** (title-page verified: "Ansys
   Fluid Dynamics Verification Manual, Release 2026 R1, March 2026").

2. **Reference value + unit + source:** non-dimensional reattachment length
   **LR / s = 5.0** (s = step height = 4.9 mm), the **Target** in the manual's Table .64.1
   (p. 196). Source: **B. Armaly, F. Durst, J. Pereira & B. Schönung, "Experimental and
   theoretical investigation of a backward-facing step", *J. Fluid Mechanics* 127, p. 473,
   1983** (also Freitas, *J. Fluids Eng.* 117, p. 208, 1995). **REFERENCE KIND:
   EXPERIMENTAL** — a measured quantity, the higher-value validation class.

3. **Ansys's own reported value (context only, NEVER the gate):** Ansys Fluent LR/s = **4.91**,
   ratio 0.982 (Table .64.1). This is context only; the gate is against the experimental 5.0.

4. **TIER CEILING declared in advance:** **`GATE REACHED`**. Although the reference is
   experimental (and could in principle buy validation/HOLDS), this team's product is
   *reproducing the Ansys manual*, and Sanaa's ruling caps that at `GATE REACHED`
   ("Anything gate reached for that team means we reached Ansys, which is good enough").
   The comparator hard-codes `GATE REACHED` as the in-band verdict. Fallbacks: triple not
   `CONVERGING` → `NOT A RESULT`; `CONVERGING` but outside the band → `GATE FAIL`.

5. **GATE quantity + expression + tolerance:** the reattachment length **LR** on the
   `bottomWall` (y = 0, x ∈ [0, 0.1 m], origin at the step foot), non-dimensionalised by
   s = 4.9 mm, at the finest level:
   **`|LR/s − 5.0| / 5.0 ≤ 0.10` (10 %)**, triple `CONVERGING` (rule 5).
   The manual (p. 195) fixes the definition: *"Reattachment length is measured from the
   reversal of the sign of the wall shear along the flow direction."* The band is set a
   priori, not from a run: (a) reattachment length is a derived quantity acutely sensitive to
   near-wall resolution and the recirculation structure; (b) Armaly's experimental LR carries
   several-percent scatter; (c) the manual's own Fluent sits at 1.8 % (0.982), well inside
   10 %; (d) 10 % is deliberately looser than this team's code-verification cases because this
   is a VALIDATION against a physical measurement carrying real uncertainty, not a comparison
   to a closed form. **It is never tightened or loosened from a first run.**

6. **Level family (grid triple — 3 levels), refinement ratio r = 2:** x AND y refined together
   by ratio 2. `(NXU, NXD, NY)` per block = L1 (64, 64, 16) → **3 072 cells**; L2 (128, 128,
   32) → **12 288 cells**; L3 (256, 256, 64) → **49 152 cells**; z is 1 empty cell (2-D). Three
   blocks: A = inlet channel (200 mm × 5.2 mm, upstream of the step), B = downstream above step
   level (100 mm × 5.2 mm), C = downstream below step level (100 mm × 4.9 mm). Solver
   `simpleFoam` (steady incompressible laminar, SIMPLEC `consistent yes`), ν = μ/ρ = 1.5e-5
   m²/s, ρ = 1 kg/m³. BCs: `inlet` uniform velocity 0.288462 m/s developing over the 200 mm
   inlet section (Re_D = ρ·U·D/μ = 1·0.288462·0.0104/1.5e-5 = **200.0**, D = 2× inlet height =
   10.4 mm, matches the manual to the printed digit); `outlet` fixed pressure; no-slip on all
   walls; `frontAndBack` empty. **Mesh birth-certified from checkMesh** (L1 scratch-validated:
   3 072 cells, Max aspect ratio 9.62 OK, Max skewness 7e-14 OK, Mesh OK).

7. **PRINCIPAL RISK (the ONE failure mode named before compute):** the reattachment length is
   read from the **sign change of the reported `wallShearStress.x`**, and OpenFOAM reports wall
   shear as `-(nHat & devTau)`, so on the y = 0 wall the reported x-component carries the
   **OPPOSITE sign** to the physical μ·du/dy. A silently inverted convention would place the
   reattachment point INSIDE the recirculation bubble and read LR wrong. The comparator
   applies `ORIENT = −1` to convert reported → physical, and — this is the guard — computes LR a
   **second, independent way** (the sign change of near-wall streamwise velocity `u_x` in the
   first cell row) and **REFUSES (exit 2) if the two disagree by more than 3 cell widths**. If
   the sign convention ever changes, the cross-instrument control fires instead of mis-grading.

8. **EXPECTED ORDER:** formal p_f = 2 (Gauss linear, corrected). p_obs is not the headline here
   (the gate is the LR value, not an order), but a p_obs materially above 2 on the LR triple
   would be declared SUSPICIOUS (a lucky mesh or a reference coincidence), not a win. No GCI is
   quoted unless the triple is monotone `CONVERGING`.

9. **WEDGE/GEOM BIAS:** N/A — Cartesian planar 2-D, not an axisymmetric wedge.

10. **CAP in core-minutes + cost_basis:** cap **90 core-min total** across all three levels
    (running-total drawdown; an overrun STOPS the run and does NOT get a new budget, rule 12;
    the cap is also a runaway guard reported to the supervisor). A-priori estimate: from the
    scratch validation, L1 (3 072 cells) runs at ~6 ms/iter (~2 µs/cell/iter, consistent with
    VMFL004's 2.9 µs/cell/iter); laminar convergence to the residualControl floor (p 1e-8,
    U 1e-9) is estimated at ≈ 3 000–5 000 iterations, giving roughly L1 ~0.5, L2 ~2, L3 ~8
    core-min → **~10–15 core-min total**, with the 90 cap as a generous runaway guard for a
    2-D BFS whose convergence can be stubborn. RANKS = 1, so the wall timeout IS the core-minute
    cap. Rate **$0.0513/core-h (c7a.4xlarge), REPORTED-BY-OWNER, NOT MEASURED** — the box cannot
    read its own billing (COMPUTE_BUDGET_CHARTER §5); dollars are DERIVED. Under the 2026-08-21
    blanket (<$25) and still costed per item. **Estimate-vs-actual calibrated at closure into
    `docs/COST_CALIBRATION.md` (rule 12).**

11. **CONTROLS (all non-droppable, NONE on an `assert`):**
    `cases/ansys_verification/VMFL064/grade_vmfl064.py`. `python3 -O` strips `assert`, so no
    `assert` carries any refusal, guard, control or gate (sweep empty); every refusal is
    `SystemExit2` (`sys.exit(2)`) or `raise`.
    - **Planted-zero (rule 3):** plant **1.234e-3** into the FIRST face of a COPY of the
      `bottomWall` `wallShearStress`, read it back FROM DISK with the same reader, and **REFUSE
      (exit 2) INSIDE the control** (fall-through refusal, Amendment 6a) if the reader cannot see
      it. **Calibrated to the reader (L-340):** this is a **SINGLE-POINT plant into a
      SINGLE-POINT reader** (face 0 only, `seen[0] − base[0]`), NOT an averaging (RMS/mean over N
      faces) reader, so there is no 1/√N dilution — the reader delta equals the plant. Verified
      in the selftest.
    - **Strict completion (rule 4), WRITTEN OUT IN FULL — adapted for a residualControl-stopped
      STEADY run and declared THAT WAY here, not improvised in the grader.** For a steady SIMPLE
      solve the literal clause "last time == endTime" would mean the solver *ran out of clock
      without converging* — the opposite of completion — so the equivalent, strictly stronger
      clause is used: (i) `rc == 0`, parsed TOLERANTLY as `^\s*rc\s*=\s*(-?\d+)` so the
      launcher's `rc = 0` (with spaces) is read (Amendment 5); (ii) an `\nEnd` line in
      `log.simpleFoam` BY EXACT NAME (a `log*` glob matches `log.blockMesh` first); (iii) the log
      reports **`SIMPLE solution converged`** (stopped on its own residualControl criterion);
      (iv) **last Time < endTime** (did NOT run out of clock); (v) fields `U`, `p`,
      `wallShearStress`, `Cx`, `Cy` present at that time; (vi) `ExecutionTime` count == the
      iteration count; (vii) **AGE GUARD** — `U` and `wallShearStress` at the final time strictly
      newer than the case's own `0/U`. Any failed clause REFUSES (exit 2). The launcher's own age
      guard additionally REFUSES before compute if `0/` or any time directory (matched by regex
      `^[0-9]+(\.[0-9]+)?$`, never a `[0-9]*` glob that matches `0.orig`) already exists.
    - **Roache triple gating (rule 5), Fs = 1.25, r = 2** on LR/s across the three levels: any
      non-`CONVERGING` state (`EXACT`/`STAGNANT`/`OSCILLATORY`/`DIVERGENT`) → `NOT A RESULT`
      whatever the value; no GCI quoted unless monotone.
    - **Cross-instrument control** (see §7): LR from wall shear vs LR from near-wall u must agree
      within 3 cell widths, else REFUSE.
    - **Comparator `--selftest`** exercises every control (not just describes them): the LR
      extraction is DRIVEN on a **constructed field whose reattachment point is known** (x* =
      6·s, deliberately ≠ the 5·s target — both instruments return x* exactly, proving the reader
      reports what is on disk, not the target); the planted-zero seeing AND blind paths; and
      strict completion accepting a good run and REFUSING `rc ≠ 0`. `--selftest` = **all checks
      passed, exit 0, IDENTICAL under `python3` and `python3 -O`**. **Mutation test**
      `mutation_test_vmfl064.py`: breaks the planted-zero refusal and the completion rc-refusal on
      sacrificial copies and confirms `--selftest` exits NON-ZERO with no all-checks-passed line
      under BOTH interpreters (**9/9, exit 0 under both**).

12. **Launcher (`run_vmfl064.sh`) — required artifacts:** launch-time freeze verification of the
    prereg AND comparator against HEAD (gating with `|| { echo ABORT...; exit 1; }`, shas into
    `LAUNCH_RECORD.txt`); cap enforcement by `timeout_s = remaining_core_min × 60 / RANKS` with
    running core-minute accounting that REFUSES at zero; **no `set -u`** (v2606 bashrc cycle,
    reason in header); mesh birth certificate from checkMesh; `postProcess -func writeCellCentres
    -latestTime` after a successful solve so the grader's `Cx`/`Cy` abscissae exist; `RUN_RC.txt`
    on BOTH the success and abort paths including the timeout-fired rc = 124; **detached solver**
    (`exec setsid timeout … simpleFoam &` then `wait`, detachment VERIFIED by the wrapper's
    SID == its own PID, field 6 of `/proc/<pid>/stat`, never by ppid). A pre-flight **smoke** mode
    exercises the launcher end-to-end (freeze check included) at a tiny endTime and grades nothing.

13. **Grading path (fixed at this commit, rule 2):** `grade_vmfl064.py` reads
    `verification/runs/ansys_verification/VMFL064/{L1,L2,L3}`.

14. **FALSIFICATION clause (named before the run):**
    - **A `GATE FAIL` is a real possible outcome:** an under-resolved bubble, a not-fully-
      developed inlet profile, or a scheme-dependent reattachment could put LR/s outside the
      10 % band.
    - **A `NOT A RESULT` is a real possible outcome:** if the LR/s triple is not monotone
      (reattachment length is notoriously non-monotone under refinement for a marginally
      resolved bubble), the triple reads `OSCILLATORY`/`DIVERGENT` → `NOT A RESULT` whatever the
      finest value — exactly the VMFL033/VMFL076 pattern, named here in advance.
    - **The cross-instrument control can REFUSE:** if the wall-shear sign convention differs from
      the assumed ORIENT, the two LR instruments disagree and the case REFUSES rather than
      reporting a wrong reattachment point.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened. **This is a PREP
registration: the case is frozen and smoke-tested, but the real levels are NOT launched until
the supervisor clears it.***

---

## PRE-COMPUTE AMENDMENT 1 — 2026-08-26T16:05:19Z — observed-order floor `P_MIN = 0.05`

**Author:** `ansys-lane-opus`. **Lines whose number changed above this section: 0** (this
section is appended at the foot; nothing above it is edited — rule 6).

**LEGALITY, WITH THE EVIDENCE, NOT THE CLAIM (rule 2).** Amendments are legal only *before
first compute*, and the condition must state how it was checked. **Checked:** the run root
`verification/runs/ansys_verification/VMFL064` **DOES NOT EXIST** at
**2026-08-26T16:05:19Z** — `test -e` on that path returns false and it is absent from
`ls verification/runs/ansys_verification/`, whose 25 sibling case directories are all other
cases. No solver has been started for VMFL064, no level directory exists, no `RUN_RC.txt`
exists, and `LAUNCH_RECORD.txt` (which the launcher writes *before* the first solver) does
not exist either. **First compute has not happened, so this amendment is pre-compute.**

**NOTHING GATED IS TOUCHED.** The gate quantity (LR/s on `bottomWall`), the threshold
(`|LR/s − 5.0| / 5.0 ≤ 0.10`), the cap (**90 core-min**, RANKS = 1), the level family
(L1/L2/L3, r = 2), the reference (5.0, EXPERIMENTAL) and the tier ceiling label
(**`GATE REACHED`**) are **unchanged, character for character**. This amendment adds a
**refusal**, and a refusal can only turn a would-be `GATE REACHED`/`GATE FAIL` into
`NOT A RESULT` — never the reverse (rule 5's direction of travel).

**WHAT IS ADDED.** `grade_vmfl064.py` gains an **observed-order floor `P_MIN = 0.05`**:
a grid triple whose observed order `p` falls below it is **`NOT A RESULT`** and **NO GCI is
printed**. Provenance: `docs/ansys_verification/FINDING_p_floor.md` §4, measured by this
team's supervisor on 2026-08-26 — `R = e21/e32` near 1 is a *stagnant* family, and
`ln(R)/ln(r)` of it returns a floating-point crumb (measured **3.2034e-15** in three of five
probed comparators) that reads as a valid, very small observed order, from which a GCI would
then be computed and quoted. **A GCI computed from a near-zero order is a number with no
meaning, and printing one is worse than printing nothing.**

**AND IT IS DRIVEN, NOT DECLARED** — a floor nobody tests is a floor nobody has. A **planted
control**, `p_floor_control()`, feeds three constructed triples through the comparator's own
`roache()` and its own (now single, shared) verdict path `verdict_for()`, and **REFUSES
(exit 2)** if any is graded the wrong way:

| probe | constructed | required |
|---|---|---|
| (a) equally spaced | `(1.0, 1.1, 1.2)` — the exact probe of FINDING_p_floor §2 | `NOT A RESULT`, **no GCI**, though the fine value sits inside the band |
| (b) below the floor | `p = 0.01` genuinely computed (`d32/d21 = r^-0.01`) | `NOT A RESULT`, **no GCI** — this is the probe that drives the floor itself, since (a) is caught one step earlier by the ratio test |
| (c) above the floor | `p = 0.5` | `CONVERGING`, **GCI quoted**, `GATE REACHED` — the floor must not swallow real results |

The control runs in **`--selftest` AND in `main()`** before any level is read, so the frozen
grading path exercises it on the real run. **NO `assert` carries it:** `python3 -O` strips
`assert`, so every branch refuses with `SystemExit2` / `sys.exit(2)`.
`grep -nE '^\s*assert ' grade_vmfl064.py` → **0**, unchanged from the freeze.

**MEASURED, at this amendment (all four numbers re-measured here, none recalled):**
- `--selftest`: **25/25 checks PASS, 0 FAIL, exit 0 — IDENTICAL under `python3` and
  `python3 -O`**. Probe (a) reports `STAGNANT`, `gci = None`; (b) recovers `p = 0.01`;
  (c) recovers `p = 0.5` with a GCI.
- **The floor is load-bearing on the real defect:** with the floor removed, `(1.0, 1.1, 1.2)`
  classifies **`CONVERGING` with `p = 3.20343e-15`** in this comparator — the FINDING's
  number, reproduced here in this file's own code — and the GCI it would then have printed
  is **4.69e+13 (i.e. 4.7e+15 %)**. Adding the floor is therefore a repair, not a
  precaution.
- `mutation_test_vmfl064.py`: **9/9 expectations held**, exit 0, against the amended
  comparator (needles B and C untouched by this amendment).
- Two further mutations were driven ad hoc to prove the NEW control is real (they are not
  added to the frozen mutation file): defanging `if p < P_MIN` and zeroing `P_MIN` each make
  `--selftest` **REFUSE with exit 2 under BOTH `python3` and `python3 -O`**, printing no
  all-checks-passed line.

**Comparator blob:** `dfb05817745d88eb9298e2d00543d23aeff2314b` (freeze `1dc0e4d5`) →
**`0be9126cd6a3e3c860b98854a4e21ba1102edfdc`** (this amendment). The launcher's launch-time
freeze check hashes the on-disk comparator against `HEAD` and **ABORTs** on any mismatch, so
the run that follows is bound to the amended blob and to no other.

**Authority for the compute that follows:** Sanaa's permission boarded verbatim at commit
`bc0e687e` — *"anything that leads to the lab having more runs under its belts"*. RANKS = 1,
cap **90 core-min**, unchanged.
