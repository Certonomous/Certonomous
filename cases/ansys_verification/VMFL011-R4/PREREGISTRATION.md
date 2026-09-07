# PRE-REGISTRATION — VMFL011-R4: Laminar Flow in a Triangular Cavity

**Re-registration of VMFL011-R3** (VM2026R1 p.41) under `ANSYS_VERIFICATION_CHARTER` §6: a
**NEW register row that cites row #36 and never overwrites it**. Row **#36 (VMFL011-R3) stands as
`GATE FAIL`** — rms 0.034088 at the finest level L3 vs band ≤ 0.030, on a `CONVERGING` u_min
triple, with the rms sequence STILL FALLING with refinement — whatever this row returns. Rows #26
(VMFL011) and #31 (VMFL011-R2) both stand as `NOT A RESULT` and are equally untouched.

Frozen by sha **before any R4 solver starts** (CLAUDE.md rule 2). Drafted by `ansys-lane-opus`,
**2026-09-07**. This file is a frozen file under rule 6.

**NOT YET RUN.** `verification/runs/ansys_verification/VMFL011-R4/` **does not exist** at
**2026-09-07T18:17:54Z** — `test -e` on that path returns false and the directory is absent from
`ls verification/runs/ansys_verification/`, whose entries include `VMFL011`, `VMFL011-R2` and
`VMFL011-R3`, **none of which is touched by this registration**. No R4 solver has started, no
level directory exists, no `RUN_RC.L*`, no `LAUNCH_RECORD.txt`.

---

## THE FIRST THING A READER SHOULD CHECK — THE L-502 TRAP WAS SPRUNG, AND THE DATED-PLAN CLAUSE IS STRUCK

`FIX_SUCCESSOR_REGISTRY.md` (row for VMFL011-R3 → VMFL011-R4) carried a dated OWED-PLAN with three
clauses: *"adds an L4 finer level AND a higher-order convection scheme (linearUpwind→linear), AND
bounds the Jyotsna & Vanka digitisation error (§2al/§2am) before reading the band."*

**The `linearUpwind→linear` clause is a NO-OP on a FALSE PREMISE and is STRUCK as a legal
pre-compute correction (rule 2).** L-502 requires the base case's OWN frozen files to be verified
against HEAD before any successor lever is adopted, and a HALT rather than a freeze around a false
premise. That verification was done independently:

- **THE CONDITION, AND HOW IT WAS CHECKED.** VMFL011-R3's frozen `case/system/fvSchemes` already
  contains `div(phi,U) bounded Gauss linear` — **2nd-order central `linear`, the least-diffusive
  scheme, NOT `linearUpwind`**. Checked by `git hash-object` of the R3 disk file against
  `git rev-parse HEAD:cases/ansys_verification/VMFL011-R3/case/system/fvSchemes`: both are
  **`5f997a3b9051bc7c4c284c065cebc946f66507ae`** (disk == HEAD, at R3 freeze commit
  `45c3e8a4ec3a805f98e7e2464cbbe770102c3f38`). The R4 `case/system/fvSchemes` is byte-identical to
  it (same blob). There is **no first-order blend to raise to second order**; the swap would change
  no byte and freezing it would put a false premise into a rule-6 record.
- This is the **identical falsification that hit VMFL063-R2** (registry row, corrected
  resolution-only, 2026-09-07). The dated-plan clause was written believing the base ran a
  first-order upwind scheme; it did not.
- **The gate does NOT move.** Striking a no-op scheme clause changes no gate constant, band, cap,
  ceiling or verdict path. `case/system/fvSchemes` and every other case input stay byte-identical
  to the attempt-1/R3 family, hashed by the launcher against their attempt-1 blobs before a
  core-minute is spent.

**The two GENUINE levers are kept:** (A) an L4 finer level extends the Roache ladder so the still-
falling rms can be read at a finer h; (C) the Jyotsna–Vanka digitisation error is bounded
**VALUE-BLIND**, off the gate path, as a characterisation that **cannot widen the 0.030 band**
(§25/L-487). Neither can move the gate.

---

## THE ONE THING ABOUT THE GATE — IT DID NOT MOVE, AND IT IS A `diff`, NOT A CLAIM

**The R3 run's answer is on disk** (row #36, `GATE FAIL`, rms 0.034088 at L3). Any change to a gate
constant, band, reader, verdict decision or triple classifier would be **gate-fitting** and is
refused (rule 2). So the gate is carried **character for character** from the R3 comparator blob
`3975d9ee3a60bde8b2c1537c27abb1431662d65b`, and the freeze publishes four EMPTY-DIFF spans plus the
single declared change:

```
# from the repository root
R3=cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py
R4=cases/ansys_verification/VMFL011-R4/grade_vmfl011_r4.py
py(){ python3 - "$1" "$2" "$3" "$4" <<'PY'
import sys
s=open(sys.argv[1]).read(); a=s.index(sys.argv[3]); b=s.index(sys.argv[4], a+1)
open('/dev/stdout','w').write(s[a:b])
PY
}
# 1. GATE READERS
diff <(py "$R3" x 'def _read_rms(path):' 'def _perturb(path, plant):') \
     <(py "$R4" x 'def _read_rms(path):' 'def _perturb(path, plant):')
# 2. ROACHE + P_MIN
diff <(py "$R3" x 'def roache(f1, f2, f3, r=2.0):' 'def planted_zero(') \
     <(py "$R4" x 'def roache(f1, f2, f3, r=2.0):' 'def planted_zero(')
# 3. VERDICT-DECISION cascade
diff <(py "$R3" x "    if R['blocking']:" "    R['ceiling_note']") \
     <(py "$R4" x "    if R['blocking']:" "    R['ceiling_note']")
# 4. GATE CONSTANTS block (module level, U_WALL..TIER_CEILING)
diff <(sed -n '/^U_WALL   = 2.0/,/^TIER_CEILING/p' "$R3") \
     <(sed -n '/^U_WALL   = 2.0/,/^TIER_CEILING/p' "$R4")
```

**MEASURED AT THIS FREEZE:**
- **Spans 1, 2, 3 are EMPTY DIFFS** — the two gate readers `_read_rms`/`_read_umin`, the `roache()`
  classifier with `P_MIN`, and the entire verdict-DECISION cascade (`if R['blocking']` /
  `elif triple != CONVERGING` / `else` band-check reading rms at `LEVELS[-1]` → GATE REACHED /
  GATE FAIL / NOT A RESULT) are carried character for character.
- **Span 4 has EXACTLY ONE changed line: `LEVELS` gains `'L4'`** (`['L1','L2','L3']` →
  `['L1','L2','L3','L4']`). `U_WALL = 2.0`, `BAND_RMS = 0.030`, `RESID_FLOOR = 1.0e-7`,
  `ENDTIME = 20000`, `FIELDS`, `PLANT = 1.234e-3`, `TIER_CEILING = 'GATE REACHED'` are all
  byte-identical. **The band did not move.**

A finer level EXTENDS the ladder; it cannot lower a failing rms below the band unless the physics
genuinely converges there. The triple SELECTION in `main()` is re-pointed at the finest three
(`GRADED_TRIPLE_LEVELS = LEVELS[-3:] = ('L2','L3','L4')`) — a declared change, proven in the
comparator's own selftest (change A), with **no fallback to a coarser triple and no dropped level
(L-500)**.

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL011-R4 -- Laminar flow in a triangular cavity, manual p.41
                     (title-page verified: "Release 2026 R1 - (c) ANSYS, Inc.").
                     Solver = simpleFoam (OpenFOAM v2606), steady incompressible
                     laminar SIMPLEC, Re = U_wall*base/nu = 2*2/0.01 = 400, 2-D.
                     NOT YET RUN; verification/runs/ansys_verification/VMFL011-R4/
                     absent at 2026-09-07T18:17:54Z.
2. REFERENCE       : the normalised x-velocity profile u_x/U_wall along the vertical
                     line bisecting the base of the cavity (manual Figure .11.2).
                     Source: R. Jyotsna & S.P. Vanka, "Multigrid Calculation of Steady,
                     Viscous Flow in a Triangular Cavity", J. Comp. Phys. 122, 107-117
                     (1995) -- the manual's own cited Reference. The manual p.42 prints
                     this ONLY as a FIGURE with NO discrete target table, so the curve
                     is carried as the digitised CSV
                     reference/vmfl011_benchmark_xnorm.csv, blob
                     9f11191b8c823eb32edd3f2b74bd29da855aab55 -- BYTE-IDENTICAL to
                     attempts 1/2/3 and re-hashed by the comparator at grade time.
                     Characteristic functional: u_min/U_wall = -0.318062 at y = -0.987 m.
3. REFERENCE KIND  : NUM, code-to-code, and doubly indirect (digitised from a figure).
                     Buys NEITHER V NOR P.
4. TIER CEILING    : GATE REACHED. BYTE-IDENTICAL. The comparator hard-codes it as the
                     in-band verdict; it CANNOT print PASS.
5. QUANTITIES      : gate = rms_vs_benchmark at the FINEST level (now L4) -- the RMS,
                     over the 46 benchmark abscissae, of (u_lab/U_wall - u_bench/U_wall),
                     the lab profile linearly interpolated from the 401 fixed bisector
                     samples onto those abscissae. Triple channel = u_min_norm, the most
                     negative normalised x-velocity on the bisector, on the FINEST THREE
                     levels (L2,L3,L4). BOTH readers BYTE-IDENTICAL to R3.
6. BANDS (THE GATE): rms_vs_benchmark <= 0.030 at the finest level. BYTE-IDENTICAL,
                     carried character for character and NOT re-justified from any
                     number. NEVER tightened or loosened from a run -- the R3 answer
                     0.034088 EXISTS on disk, which is precisely why this line is a
                     carry, not a justification.
7. LADDER          : simpleFoam, laminar, SIMPLEC (consistent yes), nu = 0.01 m2/s
                     (rho = 1, mu = 0.01, manual p.41). Triangular cavity: base 2 m
                     (x -1 -> 1), movingWall at y = 0 with U = (2,0,0), apex at (0,-4,0),
                     sideWalls noSlip, front/back empty, apex a genuinely COLLAPSED-hex
                     block. div(phi,U) = bounded Gauss linear (2nd-order central;
                     blob 5f997a3b, UNCHANGED -- the dated-plan linearUpwind->linear was
                     a NO-OP and is STRUCK). endTime = 20000 SIMPLE iterations, no
                     residualControl, so "last time == endTime" is literally testable.
                     EVERY CASE INPUT AND THE REFERENCE ARE THE ATTEMPT-1 FILES REUSED
                     BYTE FOR BYTE -- nine blob shas, CHECKED AT LAUNCH.
8. DECOMPOSITION   : grid family r = 2, base cells NB and height cells NH refined
   SEED              together: L1 (20,40)=800; L2 (40,80)=3 200; L3 (80,160)=12 800;
                     L4 (160,320)=51 200. NB EVEN at every level so the bisector x = 0
                     is a cell-face plane identically placed under refinement. SERIAL,
                     RANKS = 1, no domain decomposition and no RNG anywhere in the case.
                     GRADED Roache triple = the FINEST THREE (L2,L3,L4), fixed a-priori.
9. PRINCIPAL RISK  : THE PREDICTED OUTCOME OF THIS RUN IS `GATE FAIL` (see PRIOR
                     KNOWLEDGE). Two named risks: (i) a reader mistakes a FOURTH attempt
                     for persistence in search of a better number -- it is not; the gate
                     is a published empty-diff over the readers/roache/verdict cascade
                     and the predicted outcome is a failure. (ii) Adding L4 could be
                     mistaken for gate-fitting -- it is the OPPOSITE: a finer level can
                     only turn a genuinely-asymptotic-and-in-band solve into GATE REACHED;
                     a still-failing rms stays GATE FAIL, and a non-asymptotic triple is
                     NOT A RESULT with NO level dropped (L-500).
10. EXPECTED ORDER : formal p_f = 2; R3 measured p = 1.60 on u_min (GCI_fine 3.303%).
                     p_obs is NOT the headline (the gate is the RMS value). NO GCI is
                     quoted unless the finest-three triple is monotone CONVERGING and
                     p >= P_MIN = 0.05.
11. WEDGE/GEOM BIAS: N/A (planar 2-D Cartesian, not an axisymmetric wedge). The
                     collapsed-hex apex is a disclosed mesh property; it is why the first
                     bisector row carries u == 0 exactly (the whole of L-347's mechanism).
12. COST + CAPS    : PER-LEVEL caps (core-min), RANKS = 1: L1=3, L2=8, L3=25, L4=130,
                     with a running-TOTAL backstop of 170. A level's timeout_s =
                     min(per-level cap, remaining total) * 60 / RANKS; an overrun STOPS
                     the run (rc 124) and does NOT get a new budget (rule 12); endTime is
                     NEVER shrunk to fit a cap. ESTIMATE **~73.1 core-min total**. Basis:
                     L1+L2+L3 = 0.2667 + 1.0667 + 8.2333 = **9.5667 core-min MEASURED**
                     on byte-identical inputs (R3 row #36, calibration C-175); L4
                     EXTRAPOLATED at the measured L3/L2 = 7.72x PCG/DIC scaling ->
                     8.2333 * 7.72 ~ **63.6 core-min** (~3 800 wall s serial). DISCLOSED:
                     L4's ~3 800 wall s exceeds the 3 600 s stall heuristic BY DESIGN
                     (a 51 200-cell serial PCG solve at 20 000 iterations with 3
                     non-orthogonal correctors), not as a stall. Rate $0.0513/core-h
                     (c7a.4xlarge) is REPORTED-BY-OWNER, NOT MEASURED (COMPUTE_BUDGET
                     §5); dollars DERIVED: **$0.0625 at the ~73.1 core-min estimate**,
                     **$0.145 at the 170 core-min total backstop**. Under the 2026-08-21
                     blanket (<$25) and still costed per item. Estimate-vs-actual
                     calibrated at closure into docs/COST_CALIBRATION.md.
13. CONTROLS       : comparator cases/ansys_verification/VMFL011-R4/grade_vmfl011_r4.py,
                     blob cbf376c03d285c4b149a17e955878971fc25badf. Carried from R3
                     byte-identical and still DRIVEN on the real attempt-1/R2 bytes:
                     L-340 sizing control, L-347 placement control (4 probes), planted-
                     zero per channel with PRESENT + KNOWN-BAD arms (rule 3, L-487),
                     frozen-constant + reference-blob control, strict completion (rule 4)
                     with L-342 field classes, Roache gating (rule 5), P_MIN floor,
                     L-332 ast.Assert census, LAUNCHER FREEZE CHECK (rule 2), L-343 USER
                     pin. NEW in R4 and each selftest-driven: (A) the finest-three graded
                     triple (L-500, no drop) + a 4-point settling diagnostic; (C) a
                     VALUE-BLIND digitisation-floor characterisation (off gate, cannot
                     widen the band, L-487); (D) a GATE-BLIND physical-range guard with
                     PRESENT + KNOWN-BAD arms. NO `assert` carries any control:
                     ast.Assert count = 0, measured by the file itself with the counter
                     shown able to count a planted one. `--selftest` 64/64 PASS, exit 0,
                     output BYTE-IDENTICAL under `python3` and `python3 -O`.
```

---

## THE GENUINE LEVER (A) — AN L4 FINER LEVEL, AND WHY IT IS NOT GATE-FITTING

R3 landed `GATE FAIL` on a **CONVERGING** u_min triple whose rms was **still falling** with
refinement (0.040264 → 0.034775 → 0.034088). The open question R3 could not answer: **does the
still-falling rms enter the 0.030 band as h → 0, or plateau above it?** An L4 level
(160×320 = 51 200 cells, r = 2 finer than L3) answers it at one finer h.

- The **GRADED Roache triple is FIXED A-PRIORI as the finest three (L2,L3,L4)** =
  `GRADED_TRIPLE_LEVELS = LEVELS[-3:]`. There is **no search for the triple that passes** and **no
  fallback to a coarser triple** if the finest is missing — that would be gate-fitting by level
  selection (L-500/L-501). A 4-point (L1..L4) settling diagnostic reports both overlapping triples
  (L1L2L3 and L2L3L4) so a reader can see whether the observed order is settling toward the
  asymptotic range, but it **moves no gate quantity and no verdict reads it**.
- The band is read at `LEVELS[-1]`, which is now L4 — the byte-identical `else` branch of the
  verdict cascade. The direction is monotone and honest: adding a finer level can only turn a
  **genuinely-asymptotic-and-in-band** solve into `GATE REACHED`; a still-failing rms at L4 stays
  `GATE FAIL`; a non-asymptotic finest-three triple is `NOT A RESULT` (rule 5).

## THE GENUINE LEVER (C) — BOUNDING THE DIGITISATION ERROR, VALUE-BLIND AND OFF THE GATE

The reference is Ansys's digitisation of a FIGURE (Jyotsna & Vanka Fig .11.2; NO target table). The
comparator's `digitisation_floor_diagnostic()` bounds the referent's digitisation noise from its
**own bytes**, computed at grade time and reported beside the verdict:

- an **internal lower bound** — the RMS of the reference values in the physically-quiescent lower
  cavity (y ≤ −2 m), where the true velocity ≈ 0, so a non-zero there measures digitisation noise
  in the region where the digitiser could align to a nearly-flat curve;
- **reading-error floors** — for each full-scale fraction in (0.5, 1, 2, 3)%, `sigma = pct * span`,
  the rms a PERFECT model would STILL show against a curve carrying ~independent per-point read
  errors.

**This is a CHARACTERISATION, not a gate fold.** It references no band, is chosen from no run, and
**cannot widen the 0.030 gate** (L-487; and §25.7 blocks any *gate fold* on a digitised reference
until the §25 digitizer is calibrated — this case does not do that and does not need to). Its only
job is to answer: given the referent's quality, **is rms ≤ 0.030 even attainable, or is the band
inside the referent's own digitisation noise?** — a fact about the reference, disclosed, not a knob
on the answer. `§2al/§2am` (referred-to in the dated plan) is read here as: a digitised reference
carries a stated read-off uncertainty; that uncertainty is bounded before the band is read and is
never sized after the answer is known.

---

## PRIOR KNOWLEDGE — DISCLOSED IN FULL, BEFORE THE FREEZE

**This registration is NOT blind.** R3's graded fields (register row #36, calibration C-175) are:

| level | `rms_vs_benchmark` (band 0.030) | `u_min_norm` (bench −0.318062) |
|---|---|---|
| L1 (800 c)     | 0.040264 | −0.264494 |
| L2 (3 200 c)   | 0.034775 | −0.319438 |
| L3 (12 800 c)  | **0.034088** | −0.337560 |
| L4 (51 200 c)  | **UNKNOWN — the reason this run exists** | UNKNOWN |

R3's u_min triple: `CONVERGING`, R = 0.329844, p = 1.60014, GCI_fine 3.303 %, Richardson −0.3465.

1. **THE PREDICTED VERDICT OF THIS R4 IS `GATE FAIL`.** The rms sequence is still falling but
   slowly (steps −0.005489, −0.000687; ratio 0.125), so the Richardson limit of the rms is
   **~0.03395**, still **above 0.030**. If L4 lands there or anywhere above 0.030 on a CONVERGING
   finest-three triple, it is `GATE FAIL`, recorded honestly and never softened.
2. **`GATE REACHED` is a real possible outcome.** If the finest-three triple is CONVERGING and
   L4's rms lands ≤ 0.030, it is `GATE REACHED` — never `PASS` (the ceiling forbids more). This is
   the falsifiable upside the L4 level buys.
3. **`NOT A RESULT` is a real possible outcome.** The finest-three u_min triple must be monotone
   `CONVERGING`; `EXACT`, `STAGNANT`, `OSCILLATORY`, `DIVERGENT` or `DEGENERATE` (p < P_MIN) forces
   `NOT A RESULT` whatever the rms — **with NO level dropped to rescue it (L-500)**. So does any
   level failing iterative convergence against the frozen 1e-7 floor, or any physics-critical
   completion clause.
4. **A REFUSAL is a real possible outcome and this R4 does not make one less likely by weakening
   anything.** A blind reader on either channel, a drifted frozen constant, a reference blob that
   is not `9f11191b…`, an `assert` in the comparator, a corrupt/non-physical read (change D), a
   `RUN_RC` present and reporting `rc != 0`, or an absent gate artifact each REFUSE (exit 2).

## FALSIFICATION — named before the run

- **`GATE FAIL` is the PREDICTED outcome** and is recorded honestly if it lands, never softened.
- **Adding L4 must not become "drop the failing level in reverse."** The graded triple is FIXED as
  the finest three; if it is non-asymptotic the row is `NOT A RESULT`, and the coarse triple
  (L1,L2,L3) is a diagnostic only, never a fallback (L-500).
- **The digitisation bound cannot rescue a GATE FAIL.** It is off the gate path and references no
  band; if rms at L4 exceeds 0.030 on a CONVERGING triple, `GATE FAIL` stands even if the miss is
  within the digitisation floor — the floor is reported so a reader can *interpret* the miss, not
  *waive* it.

## GRADING PATH (fixed at this commit, rule 2)

`cases/ansys_verification/VMFL011-R4/grade_vmfl011_r4.py`, blob
`cbf376c03d285c4b149a17e955878971fc25badf`, reading
`verification/runs/ansys_verification/VMFL011-R4/{L1,L2,L3,L4}` and
`.../RUN_RC.{L1,L2,L3,L4}`.
Launcher: `cases/ansys_verification/VMFL011-R4/run_vmfl011_r4.sh`, blob
`4e96cd0f9e3e4553a8953f542d106a251d80e843`.
Grading output: `verification/runs/ansys_verification/VMFL011-R4/GRADING_VMFL011_R4.json`.

## THE LAUNCHER SMOKE — REGISTERED HERE, BEFORE IT RUNS

A **launcher smoke** — `VMFL_SMOKE=1`, **L1 only**, `endTime` shortened to **20**, in a
**scratchpad root the launcher itself refuses to leave** — exercises the launcher end to end (freeze
check, the nine input-blob checks, the `--selftest` gate under both interpreters, the L-343 USER
pin, the age guard, the per-level cap arithmetic, `blockMesh`, the detached `timeout` wrapper and
the `RUN_RC` write), **grades nothing**, writes nothing under `verification/runs/`, and **no gate,
band, cap, ceiling or label depends on it**. It runs AFTER this freeze (the launcher's freeze check
requires this file and the comparator to be committed at HEAD) and its cost is seconds, reported
with the run's calibration. The `VMFL_SMOKE` guard refuses any run root not under a scratch path, so
the registered scope is enforced in the executable path, not by this prose.

## PROVENANCE

- **Parent VMFL011-R3, cited and not overwritten:**
  `cases/ansys_verification/VMFL011-R3/PREREGISTRATION.md`, comparator blob
  `3975d9ee3a60bde8b2c1537c27abb1431662d65b`, freeze `45c3e8a4ec3a805f98e7e2464cbbe770102c3f38` —
  register row **#36**, `GATE FAIL`, measured cost 9.5667 core-min, calibration **C-175**.
- **Attempts 1 and 2, cited and not overwritten:** `VMFL011/` (row #26, `NOT A RESULT`, comparator
  `e369496b…`) and `VMFL011-R2/` (row #31, `NOT A RESULT`, comparator `45aa4613…`, freeze
  `9f9d6925`).
- **Manual:** `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
  p.41–43, title-page verified against the PDF beside it (rule 15): "Release 2026 R1 - (c) ANSYS,
  Inc." Density 1 kg/m3, viscosity 0.01 kg/m-s, cavity height 4 m, base width 2 m, moving base wall
  2 m/s.
- **Standing rules and lessons applied:** CLAUDE.md rules 1–6, 10, 12, 13; **L-332** (no guard on
  an `assert`); **L-339** (no `[0-9]*` glob); **L-340**, **L-342**, **L-343**, **L-347** (carried);
  **L-382** (FREEZE_COMMIT via `git rev-parse`, sha regex asserted at commit); **L-487** (byte-
  identical gate; digitisation characterisation never widens the band); **L-500** (never drop a
  level to rescue a non-asymptotic triple); **L-502** (the base's own frozen files verified against
  HEAD before adopting the successor lever; the `linearUpwind→linear` clause struck as a no-op on a
  false premise). Digitizer framework `ANSYS_VERIFICATION_CHARTER` §25 (§25.7 blocks a gate FOLD on
  a digitised reference; this case does a value-blind CHARACTERISATION only, off the gate).
- **Compute authority:** Sanaa's 2026-08-21 blanket (<$25/run), still costed per item. RANKS = 1.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING. A GATE FAIL, a NOT A RESULT or a refusal is recorded honestly and never softened.*
