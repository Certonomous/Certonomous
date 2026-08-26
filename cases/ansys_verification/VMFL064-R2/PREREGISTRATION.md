# PRE-REGISTRATION — VMFL064-R2: Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion

**Re-registration of VMFL064** (backward-facing step, Armaly `LR/s = 5.0`) under
`ANSYS_VERIFICATION_CHARTER` §6: a **NEW register row that cites row #29 and never overwrites
it**. Row #29 stands as `NOT A RESULT` whatever this row returns.

Frozen by sha **before any R2 solver starts** (CLAUDE.md rule 2). Drafted by `ansys-lane-opus`,
**2026-08-26**. Built from `docs/ansys_verification/PREREG_TEMPLATE.md` (ten-line form,
Amendments 1–2 applied: tier vocabulary `HOLDS | GATE REACHED`; the launcher freeze check is
non-droppable). This file is a frozen file under rule 6.

**NOT YET RUN.** `verification/runs/ansys_verification/VMFL064-R2/` **does not exist** at
**2026-08-26T17:39:09Z** — `test -e` on that path returns false and the directory is absent
from `ls verification/runs/ansys_verification/`, whose sibling entries are all other cases
(`VMFL064` among them, the attempt-1 root, which is **not touched by this registration**).
No R2 solver has started, no level directory exists, no `RUN_RC.L1` and no `LAUNCH_RECORD.txt`.

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL064-R2 -- Low Re flow in a channel with sudden asymmetric expansion
                     (backward-facing step) -- manual p.195/196. Solver = simpleFoam (OpenFOAM
                     v2606), steady laminar SIMPLEC, Re_D = 200, 2-D Cartesian. NOT YET RUN;
                     verification/runs/ansys_verification/VMFL064-R2/ absent at 2026-08-26T17:39:09Z.
2. REFERENCE       : LR / s = 5.0 (non-dimensional reattachment length, s = 4.9 mm), the Target
                     of the manual's Table .64.1 (p.196). Source: B. Armaly, F. Durst,
                     J. Pereira & B. Schoenung, JFM 127 p.473 (1983); also Freitas, JFE 117
                     p.208 (1995). Ansys Fluent reported 4.91 (ratio 0.982) = CONTEXT ONLY.
3. REFERENCE KIND  : measured/experimental -- CAN buy P.
4. TIER CEILING    : GATE REACHED. Byte-identical to attempt 1 line 4: although the reference
                     is experimental, this team's product is REPRODUCING THE ANSYS MANUAL and
                     Sanaa's ruling caps that at GATE REACHED. The comparator hard-codes
                     GATE REACHED as the in-band verdict; it cannot print HOLDS or PASS.
5. QUANTITIES      : the reattachment length LR on patch `bottomWall` (y = 0, origin at the
                     step foot x = 0), non-dimensionalised by s = 4.9 mm, at the finest level.
                     *** THE ONE THING THIS R2 CHANGES *** -- LR is the **LAST**
                     negative-to-positive sign change of the PHYSICAL wall shear
                     (ORIENT = -1 applied to OpenFOAM's reported -(nHat & devTau)) inside the
                     REGISTERED SEARCH WINDOW  0.0 m < x <= 0.05 m, linearly interpolated
                     between the bracketing faces. Window justification, a priori:
                     0.05 m = 10.204*s is TWICE the experimental target (5*s = 0.0245 m) and
                     HALF the 0.1 m downstream channel -- wide enough that it cannot read as
                     tuned to an answer, short enough that it cannot admit an outlet artefact.
                     WHY THE LAST: a secondary counter-rotating CORNER VORTEX at the step foot
                     adds sign changes UPSTREAM of the primary reattachment and flips the sign
                     the profile STARTS with; it can NEVER add one downstream, because
                     downstream of reattachment the near-wall flow is attached and forward.
                     The last crossing in the window is therefore the primary reattachment
                     whether or not the eddy is resolved -- the same number on a mesh that
                     never sees it and on one that does.
6. BANDS (THE GATE): |LR/s - 5.0| / 5.0 <= 0.10 at the finest level, triple CONVERGING
                     (rule 5). BYTE-IDENTICAL to attempt 1 line 5 and NOT re-justified from
                     any number: (a) reattachment length is acutely sensitive to near-wall
                     resolution; (b) Armaly's experimental LR carries several-percent scatter;
                     (c) the manual's own Fluent sits at 1.8 %; (d) 10 % is deliberately looser
                     than this team's code-verification cases because the reference is a
                     physical measurement. NEVER tightened or loosened from a run.
7. LADDER          : simpleFoam, laminar (momentumTransport = laminar), SIMPLEC consistent yes,
                     nu = 1.5e-5 m2/s, rho = 1. Three blocks: A inlet channel 200 x 5.2 mm,
                     B downstream above step level 100 x 5.2 mm, C downstream below step level
                     100 x 4.9 mm. Inlet uniform 0.288462 m/s (Re_D = 200.0 on D = 10.4 mm),
                     outlet fixed p, no-slip walls, frontAndBack empty. MESH FAMILY AND EVERY
                     CASE INPUT ARE THE ATTEMPT-1 FILES REUSED BYTE FOR BYTE -- see
                     "WHAT IS BYTE-IDENTICAL" below, nine blob shas, checked AT LAUNCH.
                     Birth-certified per level from checkMesh (MESH_STANDARD sec.6).
8. DECOMPOSITION   : grid triple r = 2, x AND y refined together. (NXU, NXD, NY) =
   SEED              L1 (64, 64, 16) = 3 072 cells; L2 (128, 128, 32) = 12 288;
                     L3 (256, 256, 64) = 49 152. z = 1 cell (2-D). SERIAL, RANKS = 1, no
                     domain decomposition and no RNG anywhere in the case.
9. PRINCIPAL RISK  : ONE failure mode, named before compute -- **the primary reattachment
                     lands OUTSIDE the registered window**. If LR > X_WIN_HI = 0.05 m the wall
                     shear inside the window never recovers, there is no negative-to-positive
                     crossing in it, and "the last crossing" would not be a reattachment at
                     all. THE DESIGNED RESPONSE IS A REFUSAL, NOT A NUMBER: the reader returns
                     None and the comparator REFUSES (exit 2) rather than returning the corner
                     eddy's x ~ 7e-4 m, which is what a wrong number wearing a right shape
                     would look like (LR/s ~ 0.14). Sizing: the window is 2.04x the reference
                     and 2.10x the largest LR/s the published attempt-1 off-path diagnostic
                     reports (4.853), so reaching it requires a >100 % error.
10. EXPECTED ORDER : formal p_f = 2 (Gauss linear, corrected). p_obs is NOT the headline (the
                     gate is the LR value); p_obs > 2.3 is declared SUSPICIOUSLY HIGH -- a
                     warning (a lucky mesh, cancellation, a reference coincidence), never a
                     win -- and the comparator prints that warning itself. NO GCI is quoted
                     unless the triple is monotone CONVERGING and p >= P_MIN = 0.05.
11. WEDGE/GEOM BIAS: N/A (Cartesian planar 2-D, not an axisymmetric wedge; N-AV9 does not apply).
12. COST + CAP     : cap **90 core-min**, RUNNING TOTAL across the three levels, RANKS = 1 --
                     BYTE-IDENTICAL to attempt 1 line 10. An overrun STOPS the run and does
                     NOT get a new budget (rule 12); the launcher enforces it as
                     timeout_s = remaining_core_min * 60 / RANKS and refuses at zero.
                     ESTIMATE **5.4 core-min total**, and the basis is a MEASUREMENT, not a
                     guess: attempt 1 ran these byte-identical inputs to convergence at
                     424 / 907 / 2 152 iterations for **5.383 core-min measured**
                     (RESULTS.md blob 575bae85a584d22a483fc4399a91c989fe73e1b2; per-level
                     RUN_RC.txt and COST.txt under the attempt-1 run root). Rate
                     $0.0513/core-h (c7a.4xlarge) is REPORTED-BY-OWNER, NOT MEASURED -- the box
                     cannot read its own billing (COMPUTE_BUDGET_CHARTER sec.5); dollars are
                     DERIVED. Under the 2026-08-21 blanket (<$25) and still costed per item.
                     Estimate-vs-actual calibrated at closure into docs/COST_CALIBRATION.md.
13. CONTROLS       : comparator cases/ansys_verification/VMFL064-R2/grade_vmfl064_r2.py, blob
                     e04fdf937d557b4919928ab72b9fe5eb42f8b49a. CORNER-VORTEX PLANTED CONTROL
                     (the control that DRIVES this repair) + planted-zero (rule 3) + strict
                     completion (rule 4) with L-342 field classes + Roache gating (rule 5) +
                     observed-order floor P_MIN = 0.05 with its own planted control +
                     cross-instrument control + LAUNCHER FREEZE CHECK (rule 2, non-droppable,
                     PREREG_TEMPLATE Amendment 2). NO `assert` carries any of them (L-332):
                     ast.Assert count = 0. `--selftest` 37/37 PASS, exit 0, byte-identical
                     output under `python3` and `python3 -O`.
```

---

## WHAT IS BYTE-IDENTICAL — cited by blob sha, and CHECKED AT LAUNCH, not asserted in prose

The launcher hashes every one of these against its **attempt-1 HEAD blob** before a
core-minute is spent and **ABORTs (exit 2)** on any mismatch. "The mesh family did not change"
is therefore a check, not a claim.

| what | attempt-1 path | blob sha | R2 status |
|---|---|---|---|
| mesh family (all 3 levels) | `VMFL064/case/system/blockMeshDict.template` | `27cc03896bdd747279264b8051bec76179bfb516` | identical |
| controlDict (endTime 20000) | `VMFL064/case/system/controlDict.template` | `e0c609731d862d6efee7a07f5968d185de04ddb9` | identical |
| schemes | `VMFL064/case/system/fvSchemes` | `90434f3510e36fdad9eb393e9b9deb9ce980987e` | identical |
| solvers / SIMPLEC / residualControl | `VMFL064/case/system/fvSolution` | `abd77454aa646a4e36312896fe128b8e44bad391` | identical |
| initial/boundary U | `VMFL064/case/0/U` | `69bade678d479cad93a9ef1822dd7fccb7d849bd` | identical |
| initial/boundary p | `VMFL064/case/0/p` | `63609675be1c596403074dcdb56b4b3589c04a26` | identical |
| momentumTransport | `VMFL064/case/constant/momentumTransport` | `f7d93d54ebae9785586564ad6eb86faf764ebcc3` | identical |
| turbulenceProperties | `VMFL064/case/constant/turbulenceProperties` | `f7d93d54ebae9785586564ad6eb86faf764ebcc3` | identical |
| transportProperties (nu) | `VMFL064/case/constant/transportProperties` | `9322f68509449336eeecf8ae886708c9a9f09152` | identical |

And, carried unchanged **inside the comparator** from attempt-1 blob
`0be9126cd6a3e3c860b98854a4e21ba1102edfdc`: the gate quantity (`LR/s` on `bottomWall`), the
reference `REF_LRS = 5.0`, the band `TOL = 0.10`, the tier ceiling `GATE REACHED`, the cap
(90 core-min, prereg blob `7b9fd0dcaa141cacf4e0f3dee5a6ceab0b9f48b5` line 10), `ORIENT = -1`,
`PLANT = 1.234e-3`, `FS = 1.25`, `RATIO = 2.0`, `P_MIN = 0.05`, the `roache()` classifier and
the single shared `verdict_for()` path.

## WHAT CHANGED — the reattachment reader, and nothing else

| | attempt 1 (blob `0be9126c…`) | R2 (blob `e04fdf93…`) |
|---|---|---|
| locator | `first_sign_change()` — the **FIRST** negative-to-positive crossing, and `None` (→ refuse) whenever the profile does **not start negative** | `last_sign_change_in_window()` — the **LAST** negative-to-positive crossing inside `0.0 < x <= 0.05 m` |
| corner vortex | invalidates the reader's starting premise → refusal | upstream of the primary crossing by construction → no effect on the answer |
| search window | none (whole wall) | **registered**, `X_WIN_LO = 0.0`, `X_WIN_HI = 0.05 m` |
| attempt-1 logic | the grading path | **preserved verbatim** as `legacy_first_sign_change()` / `legacy_grade_path()`, **off the grading path**, used ONLY so the planted control can show it refusing the same bytes |
| completion field classes | one class; a missing `RUN_RC` voided the level | **L-342**: physics-critical fields gate; an **absent** infrastructure field prints `NOT MEASURED`, is disclosed in the grading JSON, and the grade **proceeds** |
| `RUN_RC` location | `<level>/RUN_RC.txt` | `<run root>/RUN_RC.<level>`, written by the VMFL017-R2-shaped launcher |

**Why this is a re-registration and not an amendment.** Attempt 1's first compute has happened;
rule 2 closes its gates permanently and its comparator is never edited. This is a **new case
directory, a new run root, a new comparator blob and a new register row**, exactly as
`ANSYS_VERIFICATION_CHARTER` §6 requires.

## PRIOR KNOWLEDGE — DISCLOSED IN FULL, BEFORE THE FREEZE

**This registration is NOT blind, and pretending otherwise would be the dishonest move.**
Attempt 1's `RESULTS.md` (blob `575bae85a584d22a483fc4399a91c989fe73e1b2`) already publishes,
under the heading **"OFF-PATH DIAGNOSTIC — explicitly NOT a result"**, what a last-crossing
reader returns on the attempt-1 fields: **LR/s = 4.714416 / 4.800738 / 4.853056**,
`CONVERGING`, `p = 0.7224`, `GCI_fine = 2.07 %`, finest **2.94 %** from the experimental 5.0.

Three consequences, stated so a reader can price them:

1. **The band could not have been chosen to fit**, because the band was **not chosen** — `TOL`
   is byte-identical to the attempt-1 freeze, made before any VMFL064 number existed. So are
   the reference, the ceiling, the mesh family and the cap. The only new gate-path constants
   are the window bounds, justified above from the geometry and the reference, not from 4.853.
2. **The expected outcome is therefore GATE REACHED**, and this registration says so in
   advance rather than discovering it: ~2.9 % deviation inside a 10 % band, on a `CONVERGING`
   triple with `p = 0.72` — above `P_MIN` and below `p_f = 2`, so no SUSPICIOUSLY-HIGH warning.
3. **It is still a re-run, not a re-read.** The R2 grades **fresh L1/L2/L3 solves in a new run
   root**; the attempt-1 fields are cited here and are not read by this comparator. The R2
   numbers may differ from the diagnostic (a fresh solve on a contended box converges on its
   own iteration count), and the falsification clause below is live.

## FALSIFICATION — named before the run

- **`GATE FAIL` is a real possible outcome.** An under-resolved bubble or a not-fully-developed
  inlet profile could put `LR/s` outside the 10 % band. Nothing in the R2 reader moves the band.
- **`NOT A RESULT` is a real possible outcome.** The `LR/s` triple must be monotone; a
  marginally resolved bubble gives famously non-monotone reattachment under refinement →
  `OSCILLATORY` / `DIVERGENT` → `NOT A RESULT` whatever the finest value. So does an observed
  order below `P_MIN = 0.05`.
- **A REFUSAL is a real possible outcome.** No crossing inside the registered window (principal
  risk, line 9); the two instruments disagreeing by more than 3 cell widths; a blind planted
  zero; any failed physics-critical completion clause. **The comparator refuses (exit 2) rather
  than degrading, exactly as attempt 1 did — and that refusal cost attempt 1 its credential
  rather than concealing a bad one.**
- **The R2 reader can be wrong in a way this registration would catch:** if the corner vortex
  appeared at NO level, probe (2) of the corner-vortex control (single-bubble agreement) is the
  statement that R2 then returns exactly what attempt 1 would have returned.

## CONTROLS — all non-droppable, all driven, NONE on an `assert`

`python3 -O` deletes every `assert` (L-332), so a refusal written as one is a refusal *offer*
the runner accepts or declines by an interpreter flag. **`ast.Assert` count in
`grade_vmfl064_r2.py` = 0** (measured with `ast.walk`, not by grep alone; `grep -nE '^\s*assert '`
is also 0). Every refusal is `SystemExit2` / `sys.exit(2)`.

1. **CORNER-VORTEX PLANTED CONTROL — the control that DRIVES this repair.** A repair nobody
   drives is a repair nobody has. `corner_vortex_control()` runs in `--selftest` **and in
   `main()` before any level is read**, writes OpenFOAM-format files to disk and reads them
   back through the real readers, and REFUSES (exit 2) on any of four probes:
   - **(1) drives the fix.** A profile with a corner vortex and a **known** primary
     reattachment `x_star = 6*s` (deliberately **not** the 5*s target, so a reader that
     returned the target is caught). Construction: `tau_phys(x) = (x − x_c)(x − x_star)` with
     `x_c = 7.0e-4 m` and 256 faces over 0.1 m — i.e. `dx = 3.906e-4 m`, **the same dx the real
     L3 reported**, and `x_c` **where the real L3 crossing sat** (attempt-1 triage: faces at
     `x = 1.95e-4` and `5.86e-4` positive, `9.77e-4` negative). The R2 reader must return
     `x_star`; **the ATTEMPT-1 LOGIC on the SAME BYTES must REFUSE with exit 2**, and the
     control refuses if it does not — because then nothing drives the change.
   - **(2) conservative on the old shape.** On a single-bubble profile (the attempt-1 L1/L2
     structure) the R2 reader and the attempt-1 reader must agree **exactly** (`< 1e-12`).
   - **(3) the window is load-bearing.** A spurious reversal planted **downstream of
     `X_WIN_HI`** must be ignored — and removing the window must **change** the answer, else
     the probe proves nothing.
   - **(4) cross-instrument.** The near-wall-`u` reader returns the same primary length.
2. **Planted-zero (rule 3), calibrated to the reader (L-340).** `PLANT = 1.234e-3` into face 0
   of a **copy** of `wallShearStress`, read back **from disk**. This is a **SINGLE-POINT plant
   into a SINGLE-POINT reader** (`seen[0] − base[0]`), never an RMS/mean over N faces, so there
   is no 1/√N dilution and the reader delta equals the plant. **Fall-through refusal:** the only
   way the control returns is to have seen the plant. The selftest also drives a **blind**
   reader and confirms it REFUSES (exit 2).
3. **Strict completion (rule 4) with L-342 FIELD CLASSES, declared here and not improvised.**
   Sanaa, verbatim: *"a bookkeeping failure invalidates the bookkeeping, never the physics
   artifacts — and graders must separate physics-critical fields from infrastructure fields so
   a dead poller can never void a run again."*
   - **PHYSICS-CRITICAL (these gate; any failure REFUSES exit 2):** an `\nEnd` line in
     `log.simpleFoam` **by exact name** (a `log*` glob matches `log.blockMesh` first);
     `SIMPLE solution converged` present; **last Time < endTime** (for a steady SIMPLE solve the
     literal "last time == endTime" would mean it ran out of clock **without** converging — the
     opposite of completion, so the equivalent and strictly stronger clause is used);
     `ExecutionTime` count == the iteration count; `U`, `p`, `wallShearStress`, `Cx`, `Cy`
     present at that time; **age guard** — `U` and `wallShearStress` strictly newer than the
     case's own `0/U`.
   - **INFRASTRUCTURE (L-342):** `RUN_RC.<level>` (rc, wall_s, core_min, timeout_s) and
     `COST.txt`. **Absent → `rc` is reported `NOT MEASURED`, disclosed in the printed output and
     in the grading JSON, and the grade PROCEEDS** on the physics artefacts, which are strictly
     the stronger evidence that the solver completed. **Present and bad (a recorded `rc != 0`)
     still REFUSES** — absence is a disclosure, not a licence. Both directions are driven in the
     selftest, together with an absent physics-critical field still refusing.
   - `rc` is parsed **tolerantly** (`^\s*rc\s*=\s*(-?\d+)`) because the launcher writes
     `rc = 0` with spaces.
4. **Roache triple gating (rule 5), `Fs = 1.25`, `r = 2`** on `LR/s`: any non-`CONVERGING`
   state → `NOT A RESULT` whatever the value; no GCI unless monotone.
5. **Observed-order floor `P_MIN = 0.05` with its own planted control**
   (`FINDING_p_floor.md` §4), carried unchanged from attempt 1's PRE-COMPUTE AMENDMENT 1 and
   driven in `--selftest` **and** in `main()`: `(1.0, 1.1, 1.2)` → `NOT A RESULT`, no GCI;
   a genuinely computed `p = 0.01` → `NOT A RESULT`, no GCI; `p = 0.5` → `CONVERGING` with a
   GCI, so the floor cannot swallow a real result.
6. **Cross-instrument control.** `LR` from wall shear vs `LR` from near-wall `u_x` (same window,
   same last-crossing rule) must agree within **3 cell widths**, else REFUSE. This is what
   proved `ORIENT = -1` correct on real data in attempt 1 (agreement 2.4e-7 / 5.8e-8 m).
7. **LAUNCHER FREEZE CHECK (rule 2; PREREG_TEMPLATE Amendment 2 — non-droppable).**
   `run_vmfl064_r2.sh` hashes **this file** and **the comparator** against their `HEAD` blobs,
   gating explicitly with `|| { echo ABORT…; exit 2; }`, records the resolved shas in
   `LAUNCH_RECORD.txt`, and additionally hashes all **nine** case inputs against their
   attempt-1 blobs. It also runs `--selftest` under **both** `python3` and `python3 -O` and
   ABORTs unless the two outputs are **byte-identical** and green.

**MEASURED at this freeze (numbers, not recollections):**
`--selftest` → **37 checks, 37 PASS, 0 FAIL, exit 0**, and `cmp` reports the `python3` and
`python3 -O` outputs **byte-identical**. `ast.Assert` = **0**. Corner-vortex probe: the R2
reader recovers **LR/s = 5.999803** against the constructed 6.000000 (dx = 3.906e-4 m) while
the attempt-1 logic **exits 2** on the same bytes with its own message
*"wall shear never changes sign -- no reattachment found"*. Window probe: **0.029399 m with the
window, 0.065038 m without it** — the window is load-bearing, measured. `bash -n` on the
launcher is clean; it contains **no `set -u` statement** (two mentions, both in comments
explaining its absence) and **no `[0-9]*` glob** (two mentions, both in comments citing L-339).

## GRADING PATH (fixed at this commit, rule 2)

`cases/ansys_verification/VMFL064-R2/grade_vmfl064_r2.py`, blob
`e04fdf937d557b4919928ab72b9fe5eb42f8b49a`, reading
`verification/runs/ansys_verification/VMFL064-R2/{L1,L2,L3}` and
`verification/runs/ansys_verification/VMFL064-R2/RUN_RC.{L1,L2,L3}`.
Launcher: `cases/ansys_verification/VMFL064-R2/run_vmfl064_r2.sh`, blob
`c17ee2e2693b382fd043aadc326bdae8e51fd7b6`, modelled line for line on
`cases/ansys_verification/VMFL017/R2/run_vmfl017_r2.sh`.
Grading output: `verification/runs/ansys_verification/VMFL064-R2/GRADING_VMFL064_R2.json`.

## PROVENANCE

- **Attempt 1, cited and not overwritten:** `cases/ansys_verification/VMFL064/PREREGISTRATION.md`
  (blob `7b9fd0dcaa141cacf4e0f3dee5a6ceab0b9f48b5`), `RESULTS.md` (blob
  `575bae85a584d22a483fc4399a91c989fe73e1b2`), comparator blob
  `0be9126cd6a3e3c860b98854a4e21ba1102edfdc`, and the refusal verbatim in
  `verification/runs/ansys_verification/VMFL064/GRADING_ATTEMPT_REFUSED.txt`:
  *"REFUSED (exit 2): L3: wall shear never changes sign -- no reattachment found"* — register
  row #29, `NOT A RESULT`.
- **Manual:** `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
  p.195/196, title-page verified against the PDF beside it (rule 15).
- **Standing rules and lessons applied:** CLAUDE.md rules 1–6, 10, 12, 13;
  `docs/ansys_verification/FINDING_p_floor.md` §4 (`P_MIN`); **L-332** (no guard on an
  `assert`); **L-339** (no `[0-9]*` glob); **L-340** (plant sized to the reader);
  **L-342** (physics-critical vs infrastructure field classes).
- **Compute authority:** Sanaa's permission boarded at commit `bc0e687e` —
  *"anything that leads to the lab having more runs under its belts"*. RANKS = 1, cap 90
  core-min, unchanged.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING. A GATE FAIL, a NOT A RESULT or a refusal is recorded honestly and never softened.*
