# PRE-REGISTRATION — VMFL011-R3: Laminar Flow in a Triangular Cavity

**Re-registration of VMFL011-R2** (VM2026R1 p.41) under `ANSYS_VERIFICATION_CHARTER` §6: a
**NEW register row that cites rows #26 and #31 and never overwrites either**. Row #26 stands as
`NOT A RESULT` (the frozen comparator refused on the `rms_vs_benchmark` plant, L-340) and row
**#31 stands as `NOT A RESULT`** (the frozen comparator refused on the `u_min_norm` plant,
**L-347**) whatever this row returns.

Frozen by sha **before any R3 solver starts** (CLAUDE.md rule 2). Drafted by `ansys-lane-opus`,
**2026-08-26**. This file is a frozen file under rule 6.

**NOT YET RUN.** `verification/runs/ansys_verification/VMFL011-R3/` **does not exist** at
**2026-08-26T22:36:15Z** — `test -e` on that path returns false and the directory is absent from
`ls verification/runs/ansys_verification/`, whose 37 entries include `VMFL011` (attempt 1) and
`VMFL011-R2`, **neither of which is touched by this registration**. No R3 solver has started, no
level directory exists, no `RUN_RC.L1`, no `LAUNCH_RECORD.txt`.

---

## THE ONE THING A READER SHOULD CHECK FIRST — THE GATE DID NOT MOVE, AND IT IS A `diff`, NOT A CLAIM

**The R2 run's answer is on disk.** Any change to a gate constant, a band, a reader, the verdict
path or the triple classifier would therefore be **gate-fitting** and is refused outright (rule
2). So the gate section is carried **character for character** from the R2 comparator blob
`45aa4613253d1d594b69b7f774e18cd7a312a20e`, and the freeze publishes the diff:

```
# from the repository root
extract(){ python3 - "$1" <<'PY'
import sys
s=open(sys.argv[1]).read()
a=s.index("U_WALL   = 2.0"); b=s.index("TIER_CEILING = 'GATE REACHED'")+len("TIER_CEILING = 'GATE REACHED'")
print("### GATE CONSTANTS"); print(s[a:b])
c=s.index("    if R['blocking']:"); d=s.index("    R['ceiling_note']")
print("### VERDICT PATH"); print(s[c:d])
e=s.index("def roache(f1, f2, f3, r=2.0):"); f=s.index("def planted_zero(")
print("### ROACHE + P_MIN"); print(s[e:f])
g=s.index("def _read_rms(path):"); h=s.index("def _perturb(path, plant):")
print("### GATE READERS"); print(s[g:h])
PY
}
diff <(extract cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py) \
     <(extract cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py)
```

**MEASURED AT THIS FREEZE: the diff is EMPTY, over 77 lines** covering the gate constants
(`U_WALL`, `BAND_RMS`, `RESID_FLOOR`, `ENDTIME`, `FIELDS`, `LEVELS`, `PLANT`, `TIER_CEILING`),
the entire verdict path in `main()`, the `roache()` classifier with `P_MIN`, and both gate
readers `_read_rms` and `_read_umin`. **There is no new gate-path constant in this file.**

---

## THE TEN-LINE FORM

```
1. CASE            : VMFL011-R3 -- Laminar flow in a triangular cavity, manual p.41
                     (title-page verified). Solver = simpleFoam (OpenFOAM v2606), steady
                     incompressible laminar SIMPLEC, Re = U_wall*base/nu = 2*2/0.01 = 400,
                     2-D. NOT YET RUN; verification/runs/ansys_verification/VMFL011-R3/
                     absent at 2026-08-26T22:36:15Z.
2. REFERENCE       : the normalised x-velocity profile u_x/U_wall along the vertical line
                     bisecting the base of the cavity (manual Figure .11.2). Source:
                     R. Jyotsna & S.P. Vanka, "Multigrid Calculation of Steady, Viscous
                     Flow in a Triangular Cavity", J. Comp. Phys. 122, 107-117 (1995) --
                     the manual's own cited Reference. The manual p.42 prints this ONLY as
                     a FIGURE with NO discrete target table, so the curve is carried as the
                     digitised CSV reference/vmfl011_benchmark_xnorm.csv, blob
                     9f11191b8c823eb32edd3f2b74bd29da855aab55 -- BYTE-IDENTICAL to attempts
                     1 and 2 and re-checked by the comparator at grade time.
                     Characteristic functional: u_min/U_wall = -0.318062 at y = -0.987 m.
3. REFERENCE KIND  : NUM, code-to-code, and doubly indirect (digitised from a figure).
                     Buys NEITHER V NOR P.
4. TIER CEILING    : GATE REACHED. BYTE-IDENTICAL to attempts 1 and 2. The comparator
                     hard-codes it as the in-band verdict; it cannot print PASS.
5. QUANTITIES      : gate = rms_vs_benchmark at the finest level (L3) -- the RMS, over the
                     46 benchmark abscissae, of (u_lab/U_wall - u_bench/U_wall), the lab
                     profile linearly interpolated from the 401 fixed bisector samples onto
                     those abscissae. Triple channel = u_min_norm, the most negative
                     normalised x-velocity on the bisector. BOTH BYTE-IDENTICAL, and the
                     EMPTY diff above is the proof.
6. BANDS (THE GATE): rms_vs_benchmark <= 0.030 at L3. BYTE-IDENTICAL, carried character for
                     character and NOT re-justified from any number: the reference is a plot
                     digitisation whose reading error is ~1-3 % of full scale, and the
                     Jyotsna-Vanka curve carries its own multigrid discretisation. NEVER
                     tightened or loosened from a run -- and note that the R2 run's numbers
                     now EXIST on disk, which is precisely why this line is a carry and not
                     a justification.
7. LADDER          : simpleFoam, laminar, SIMPLEC (consistent yes), nu = 0.01 m2/s
                     (rho = 1, mu = 0.01, manual p.41). Triangular cavity: base 2 m
                     (x -1 -> 1), movingWall at y = 0 with U = (2,0,0), apex at (0,-4,0),
                     sideWalls noSlip, front/back empty, apex a genuinely COLLAPSED-hex
                     block. endTime = 20000 SIMPLE iterations, no residualControl, so
                     "last time == endTime" is literally testable. EVERY CASE INPUT AND THE
                     REFERENCE ARE THE ATTEMPT-1 FILES REUSED BYTE FOR BYTE -- nine blob
                     shas, CHECKED AT LAUNCH against the attempt-1 HEAD blobs.
8. DECOMPOSITION   : grid triple r = 2, base cells NB and height cells NH refined together:
   SEED              L1 (20, 40) = 800 cells; L2 (40, 80) = 3 200; L3 (80, 160) = 12 800.
                     NB EVEN at every level so the bisector x = 0 is a cell-face plane
                     identically placed under refinement. SERIAL, RANKS = 1, no domain
                     decomposition and no RNG anywhere in the case.
9. PRINCIPAL RISK  : THE PREDICTED OUTCOME OF THIS RUN IS `GATE FAIL`, and this registration
                     says so IN ADVANCE -- see PRIOR KNOWLEDGE below. The risk this
                     registration carries is that a reader mistakes a THIRD attempt for
                     persistence in search of a better number. It is not: the gate section
                     diff above is EMPTY, and the predicted outcome is a failure.
10. EXPECTED ORDER : formal p_f = 2 for the schemes in use; attempt 1 measured p = 1.60 on
                     u_min. p_obs is NOT the headline (the gate is the RMS value). NO GCI is
                     quoted unless the triple is monotone CONVERGING and p >= P_MIN = 0.05.
11. WEDGE/GEOM BIAS: N/A (planar 2-D Cartesian, not an axisymmetric wedge; N-AV9 does not
                     apply). The collapsed-hex apex is a mesh property, disclosed, not a bias
                     term -- and it is the reason the FIRST data row of the bisector carries
                     u == 0 exactly, which is the whole of L-347's mechanism.
12. COST + CAP     : cap **50 core-min**, RUNNING TOTAL across the three levels, RANKS = 1 --
                     BYTE-IDENTICAL to attempts 1 and 2. An overrun STOPS the run and does
                     NOT get a new budget (rule 12); the launcher enforces it as
                     timeout_s = remaining_core_min * 60 / RANKS and refuses at zero.
                     ESTIMATE **9.1 core-min total**, and the basis is a MEASUREMENT of these
                     byte-identical inputs: the R2 ran L1/L2/L3 to endTime 20000 for
                     0.2833 + 1.0500 + 7.7500 = **9.0833 core-min measured**, from
                     RUN_RC.L1/.L2/.L3 and COST.txt under
                     verification/runs/ansys_verification/VMFL011-R2/ (register row #31,
                     calibration C-144). 9.1 is that figure rounded up; nothing in this R3
                     changes a mesh, a scheme or an iteration count. The R2 figure is
                     PREFERRED over attempt 1's 8.2167 because it is the more recent
                     measurement on a comparably loaded box. Rate $0.0513/core-h
                     (c7a.4xlarge) is REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read
                     its own billing (COMPUTE_BUDGET_CHARTER sec.5); dollars are DERIVED
                     ($0.0078 at 9.1 core-min). Under the 2026-08-21 blanket (<$25) and
                     still costed per item. Estimate-vs-actual calibrated at closure into
                     docs/COST_CALIBRATION.md.
13. CONTROLS       : comparator cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py, blob
                     3975d9ee3a60bde8b2c1537c27abb1431662d65b. L-347 PLACEMENT CONTROL (the
                     control that DRIVES this repair, run on the REAL R2 L1 bytes) + L-340
                     SIZING CONTROL (carried, still driven on the real attempt-1 bytes) +
                     planted-zero per channel (rule 3) with EVERY channel run and reported
                     before any exit + frozen-constant and reference-blob control + strict
                     completion (rule 4) with L-342 field classes + Roache gating (rule 5) +
                     observed-order floor P_MIN = 0.05 with its own two-way control + L-332
                     ast.Assert census + LAUNCHER FREEZE CHECK (rule 2, non-droppable) +
                     L-343 USER pin. NO `assert` carries any of them: ast.Assert count = 0,
                     measured by the file itself with the counter shown able to count a
                     planted one. `--selftest` 50/50 PASS, exit 0, output BYTE-IDENTICAL
                     under `python3` and `python3 -O`.
```

---

## WHAT CHANGED — four things, and the gate is not among them

| | R2 (blob `45aa4613…`) | R3 (blob `3975d9ee…`) |
|---|---|---|
| (i) `u_min_norm` plant **LOCATION** | `_perturb` — the **FIRST** data row | `_perturb_at_argmin` — **the row the `min()` reader SELECTS** |
| (i) `u_min_norm` plant **MAGNITUDE** | `-abs(PLANT) * 100` | **UNCHANGED**, and `frozen_constants_control()` checks `UMIN_PLANT == -abs(PLANT) * 100` exactly |
| threshold rule | `delta > 0.1·|plant|` | **UNCHANGED, byte-identical** |
| (ii) channel controls | a dict literal — **exits inside the FIRST entry** | **every channel runs; every result is printed; ONE refusal at the end** |
| (iii) L-342 field classes | present | **UNCHANGED** |
| (iv) `ast.Assert` count | 0 | **0**, re-measured by the file itself |
| (v) launcher `USER` | inherited | **`export USER="${USER:-${LOGNAME:-$(id -un)}}"` before the bashrc, and USER / `id -un` / `FOAM_USER_LIBBIN` / `WM_PROJECT_USER_DIR` recorded in `LAUNCH_RECORD.txt`** (L-343) |
| `rms_vs_benchmark` sizing (the L-340 repair) | `rms_plant_for`, `K = 4`, all rows | **UNCHANGED, byte-identical, and still driven on the real attempt-1 bytes** |
| gate constants, verdict path, `roache()`, `P_MIN`, both gate readers | — | **EMPTY DIFF, 77 lines** |

### (i) The repair, and why it is a theorem rather than a tuning

`_read_umin` returns `min(u/U_WALL)` over the 401 bisector samples. Its support is **exactly one
row** — the argmin — and **which row that is depends on the data**. `_perturb` plants into the
**first** data row. On the real bisector that row is the sample at **y = −4 m, the collapsed-hex
apex, where the no-slip solution is `u ≡ 0` exactly**; `−0.1234` there gives `−0.1234`, which is
**above** `min(u) = −0.528988913215`, so the reader returns the identical number and moves by
**exactly 0**. Not diluted. Absent from the answer.

`_perturb_at_argmin` adds the plant to the argmin row. The plant is applied to the **raw**
column and the reader normalises by `U_WALL`, so

```
new_min = (min_raw + plant) / U_WALL  ,   delta = |plant| / U_WALL   EXACTLY,
threshold = 0.1 * |plant|             ,   delta / threshold = 10 / U_WALL = 5 .
```

The control therefore passes **by construction, for any data and any non-zero plant** — the
placement is what makes it a theorem, and the magnitude is left exactly where the parent had
it. **THE THRESHOLD RULE `delta > 0.1·|plant|` IS CARRIED CHARACTER FOR CHARACTER.** L-347 is
answered by placing the plant where the reader looks, **never** by loosening the test — a
control repaired by weakening its own threshold would be no control at all.

`_perturb_at_argmin` **refuses** a non-negative plant: a `min()` reader is driven downward or
not at all.

### (ii) Every channel control runs and reports before any exit — the second half of L-347

The R2 built its controls as a dict literal and **exited inside the first entry**. Across two
complete runs the `u_min_norm` control had therefore **never once executed on a real VMFL011
bisector file**, and the R2 pre-registration's good-faith note that *"`u_min_norm` — a point
reader — passed the identical control"* was true of the **selftest fixtures** only. **A control
standing behind another control's refusal is an untested control.** `controls()` now runs both
channels with `exit_on_fail=False`, collects the results, prints every channel with its plant,
its move and its threshold — passes included — and refuses **once** at the end. This is
registered as a **refusal-reporting** change: it can make a refusal more informative and can
never turn a refusal into a pass.

### The controls are DRIVEN ON THE R2's OWN OUTPUT, and that distinction is the load-bearing one

`umin_placement_control()` runs on the **real bytes** of register row #31's refusal —
`verification/runs/ansys_verification/VMFL011-R2/L1/postProcessing/bisector/20000/bisect_U.xy`,
401 points, git blob `11c1577972244f7d5fde3ea98d1676dce0468126`, embedded verbatim in the
comparator and re-hashed in-process so the check survives in a tree with no repository.

**USING AN EXISTING RUN'S OUTPUT TO DRIVE A CONTROL IS LEGITIMATE, AND L-347 CLAUSE 2 REQUIRES
IT** — a per-channel control is only registered once it has been observed to fire on a real
file, from the real solver, in the real format; a fixture certifies the code path and not the
plant against the data, which is exactly how this defect survived two freezes. **USING AN
EXISTING RUN'S OUTPUT TO SET A BAND, A THRESHOLD OR A GATE QUANTITY WOULD BE GATE-FITTING AND
IS REFUSED** (rule 2). No verdict in this file reads those bytes; the gate-section diff above is
the check that nothing on the gate path could have been chosen to fit them.

Four probes, each refusing (exit 2) on its own failing path:

1. **DRIVES THE FIX.** The R2 pair (row-0 plant, the same magnitude) must **still REFUSE** on
   those bytes and must move the `min()` reader by **exactly 0**, reproducing row #31's recorded
   refusal. If it did not refuse, nothing would justify this file existing.
2. **THE PLACEMENT IS LOAD-BEARING, NOT THE MAGNITUDE.** The registered argmin pair must PASS,
   and its move must equal `|plant|/U_WALL` to 1e-12 — the theorem, not a measurement.
3. **THE DEFECT IS DATA-DEPENDENT, AND THAT IS WHY A FIXTURE MISSED IT.** On a profile whose
   argmin **is** row 0, the parent's row-0 plant **passes**. A selftest built on such a fixture
   certifies a control that cannot see the real data — which is what happened.
4. **ADVERSARIAL.** A blind reader (returns a constant) must **still** be REFUSED under the new
   placement, so the repair did not buy its pass by weakening anything.

---

## "DO NOT RE-REGISTER" WAS CONSIDERED, AND HERE IS WHY R3 IS STILL WORTH 9 CORE-MINUTES

The honest case against a third attempt is strong and is stated first: **two registrations have
now spent 17.30 core-min on this case and produced no graded value**, both times because of the
grading instrument; the predicted outcome of this one is a **`GATE FAIL`**; and a team that
keeps re-registering a case until something comes out is doing the thing this charter exists to
prevent.

**It is nonetheless worth it, for one reason that is not about the number.** *"Every single case
ran and successfully validated"* is read strictly in `ANSYS_VERIFICATION_CHARTER` §6 as *every
case run is recorded, and the register says which were validated* — and **VMFL011 currently owes
a verdict on its band and has never once been given one.** Rows #26 and #31 record two
instrument failures; neither records what this solver does against the Jyotsna–Vanka curve. A
`GATE FAIL` printed with its value, its band and its triple is a **result**; two refusals are
not. Nine core-minutes and $0.0078 is the whole price of converting an open instrument question
into a closed physics one.

**And the safeguard against the obvious objection is structural, not a promise:** the gate
section is byte-identical with a published EMPTY diff, the predicted outcome is recorded here as
a failure before the run, and **if this attempt also fails to produce a verdict, the honest
conclusion is that the case has a grading problem this team has not diagnosed, and the next step
is a diagnosis and not a fourth registration.** That is written down now, before the run, so it
cannot be renegotiated after it.

---

## PRIOR KNOWLEDGE — DISCLOSED IN FULL, BEFORE THE FREEZE

**This registration is NOT blind, and pretending otherwise would be the dishonest move.**
Attempt 1's `RESULTS.md` (blob `23f33ad327c653569b2966c8968d02e1a86dd45b`) publishes, beside its
`NOT A RESULT`, what the ungraded channels read on the attempt-1 fields:

| level | `rms_vs_benchmark` (band 0.030) | `u_min_norm` (bench −0.318062) |
|---|---|---|
| L1 (800 c) | 0.0403 | −0.264494 |
| L2 (3 200 c) | 0.0348 | −0.319438 |
| L3 (12 800 c) | **0.0341** | −0.337560 |

The R2 run reproduced attempt 1's L1 minimum to six decimals (`min(u)/U_wall = −0.264494`), so
these are the numbers this solver produces on this mesh family.

1. **THE PREDICTED VERDICT OF THIS R3 IS `GATE FAIL`.** 0.0341 > 0.030 at the finest level. A
   correctly predicted failure is still a failure, and this registration is made **knowing**
   that and saying so on line 9.
2. **The band could not have been chosen to fit, because the band was not chosen** — the EMPTY
   gate diff is the check, not this sentence.
3. **The u_min triple is expected `CONVERGING`** (attempt 1: steps −0.05494, −0.01812, ratio
   0.330, `p = 1.60`, Richardson −0.3465), so the verdict is expected to be decided at the band
   rather than at the triple. **The converged lab minimum sits 8.9 % from the digitised
   benchmark −0.318, larger than the 1–3 % digitisation noise the band assumed.** That gap is
   **physics and/or digitisation, not an instrument defect**, and **this R3 changes nothing
   about it** — deliberately. Whether it is the digitisation, the collapsed-hex apex, or an
   under-resolved corner vortex (`p = 1.60` below the formal 2.0) is **OPEN**.
4. **It is still a re-run, not a re-read.** The R3 grades **fresh L1/L2/L3 solves in a new run
   root**; the attempt-1 and R2 fields are read by the comparator **only** inside the two
   sizing/placement controls, off the grading path.

## FALSIFICATION — named before the run

- **`GATE FAIL` is the PREDICTED outcome** and is recorded honestly if it lands, never softened.
- **`GATE REACHED` is a real possible outcome.** A fresh solve could land the L3 RMS below
  0.030 (attempt 1's 0.0341 is 14 % above the band). It would be a `GATE REACHED`, never a
  `PASS` — the ceiling forbids more.
- **`NOT A RESULT` is a real possible outcome.** The `u_min_norm` triple must be monotone
  `CONVERGING`; `EXACT`, `STAGNANT`, `OSCILLATORY`, `DIVERGENT` or `DEGENERATE` (`p < P_MIN`)
  forces `NOT A RESULT` whatever the RMS. So does any level failing iterative convergence
  against the frozen `1e-7` floor, or any physics-critical completion clause.
- **A REFUSAL IS STILL A REAL POSSIBLE OUTCOME, and this R3 does not make one less likely by
  weakening anything.** A blind reader on either channel, a drifted frozen constant, a reference
  blob that is not `9f11191b…`, an `assert` in the comparator, a `RUN_RC` present and reporting
  `rc != 0`, or an absent gate artifact each REFUSE (exit 2). **The R3 control is STRICTER than
  the R2's on every path except the one L-347 named** — and it now reports every channel, so a
  third refusal would name what the first two could not.
- **The repair can be shown wrong in a way this registration would catch:** if the R2's row-0
  pair ever *stopped* refusing those bytes, probe (1) refuses, because then nothing drives this
  re-registration.

## CONTROLS — all non-droppable, all driven, NONE on an `assert`

`python3 -O` deletes every `assert` (L-332). **`ast.Assert` count in `grade_vmfl011_r3.py` = 0**,
measured by the file itself with `ast.walk`, and **the counter is shown able to count a planted
assert**. `grep -cE '^\s*assert '` is also **0**. Every refusal is `sys.exit(2)`.

1. **FROZEN-CONSTANT AND REFERENCE-BLOB CONTROL.** Thirteen registered constants (the eleven
   carried plus `RMS_PLANT_K` and `UMIN_PLANT`, the latter checked against the parent's own
   expression `-abs(PLANT) * 100`) plus the reference CSV's git blob sha recomputed in-process
   and its row count. **REFUSES on any drift.**
2. **THE L-347 PLACEMENT CONTROL** — four probes on the real R2 L1 bytes, above.
3. **THE L-340 SIZING CONTROL** — carried unchanged, still driven on the real attempt-1 bytes.
4. **Planted-zero per channel (rule 3)**, with **every channel run and every result reported**
   before a single refusal at the end.
5. **Strict completion (rule 4) with L-342 FIELD CLASSES**, unchanged.
6. **Roache triple gating (rule 5), `Fs = 1.25`, `r = 2`** on `u_min_norm`, unchanged.
7. **Observed-order floor `P_MIN = 0.05`, driven both ways**, unchanged.
8. **LAUNCHER FREEZE CHECK (rule 2, non-droppable) + L-343 USER PIN.** `run_vmfl011_r3.sh`
   hashes **this file** and **the comparator** against their `HEAD` blobs, gating explicitly
   with `|| { echo ABORT…; exit 2; }`; hashes all **nine** case inputs and the reference against
   their attempt-1 blobs; runs `--selftest` under **both** `python3` and `python3 -O` and ABORTs
   unless the two outputs are **byte-identical** and green and unless each of nine named control
   lines is present; and **exports `USER` before sourcing the OpenFOAM bashrc**, recording
   `USER`, `id -un`, `FOAM_USER_LIBBIN` and `WM_PROJECT_USER_DIR` in `LAUNCH_RECORD.txt`. This
   case links no user-built library, so the pin **cannot change a number here**; it is applied
   because the launcher must be correct under the cron-started runner that will actually launch
   it (L-343), and it is recorded rather than assumed.

**MEASURED at this freeze (numbers, not recollections):**

- `--selftest` → **50 checks, 50 PASS, 0 FAIL, exit 0**; `cmp` reports the `python3` and
  `python3 -O` outputs **byte-identical**, and identical run to run.
- `ast.Assert` = **0**; `grep -cE '^\s*assert '` = **0**.
- **The gate-section diff is EMPTY over 77 lines** (command published above).
- **The repair, on the real R2 L1 bytes** (blob `11c1577972244f7d5fde3ea98d1676dce0468126`,
  401 rows, `min(u)/U_wall = −0.2644944566075` at row **300**, `y = −1.0` m; row 0 carries
  `u = 0.0` at the apex): the R2 row-0 pair moves the reader by **exactly 0.0** → **REFUSES**;
  the registered argmin pair moves it by **0.0617** > threshold **0.01234** → **PASSES**, equal
  to `|plant|/U_WALL` to 1e-12; on a fixture whose argmin **is** row 0 the parent pair
  **passes**, so the defect is measured to be data-dependent; a blind reader is **still
  refused**.
- **Six mutants, each under BOTH interpreters, none printing a green line:** placement reverted
  to the parent row-0 plant → rc 2 at probe (2); threshold multiplier zeroed → rc 2 at probe
  (1); the argmin reader replaced by row 0 → rc 2; `u_min` control made to exit on its own
  failure → rc 1, selftest FAILs (the other channel is hidden); `rms` control made to exit on
  its own failure → rc 1, selftest FAILs; a planted `assert` → **rc 2 at the L-332 census even
  under `-O`**, because the census parses the source, not the compiled code.
- Launcher: `bash -n` clean; **no `set -u` statement** (one mention, in the comment explaining
  its absence); **no `[0-9]*` glob** (two mentions, both in comments citing L-339); the argv
  usage guard drives — `bash run_vmfl011_r3.sh` with no argument exits **rc 1** with
  `usage: run_vmfl011_r3.sh <run_root> [levels...]`. **Every queue entry for this launcher MUST
  pass `<run_root>` as argv[1]** (VMFL064R2-ENTRY-DEF-1).
- Case inputs: all **nine** blobs verified equal to their attempt-1 HEAD blobs at this freeze.

## GRADING PATH (fixed at this commit, rule 2)

`cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py`, blob
`3975d9ee3a60bde8b2c1537c27abb1431662d65b`, reading
`verification/runs/ansys_verification/VMFL011-R3/{L1,L2,L3}` and
`verification/runs/ansys_verification/VMFL011-R3/RUN_RC.{L1,L2,L3}`.
Launcher: `cases/ansys_verification/VMFL011-R3/run_vmfl011_r3.sh`, blob
`53905e71d58ac3094af990bc0a7ce0ab4a18c4e5`.
Grading output: `verification/runs/ansys_verification/VMFL011-R3/GRADING_VMFL011_R3.json`,
with the comparator's stdout/stderr and rc captured to `GRADING.txt` beside it.

## PROVENANCE

- **Attempt 1, cited and not overwritten:** `cases/ansys_verification/VMFL011/PREREGISTRATION.md`
  (blob `4bd8c4285e379e93e1ad4e6c2b9967604d042523`), `RESULTS.md` (blob
  `23f33ad327c653569b2966c8968d02e1a86dd45b`), comparator blob
  `e369496bf2e28ccb7145756e1c2442eb11e8e3f7` — register row #26, `NOT A RESULT`. Measured cost
  8.2167 core-min.
- **Attempt 2 (R2), cited and not overwritten:**
  `cases/ansys_verification/VMFL011-R2/PREREGISTRATION.md` (blob
  `a8c9b6f30e4383e23594b4203eea3bd28ded0a2a`, frozen `9f9d6925`), `RESULTS.md`, comparator blob
  `45aa4613253d1d594b69b7f774e18cd7a312a20e`, launcher blob
  `b1d6a74a718e8e0dc8c5a76c0a07cf48006d2ab5` — register row **#31**, `NOT A RESULT`, calibration
  **C-144**. Measured cost **9.0833 core-min**.
- **Manual:** `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
  p.41–43, title-page verified against the PDF beside it (rule 15). Density 1 kg/m3, viscosity
  0.01 kg/m-s, cavity height 4 m, base width 2 m, moving (base) wall 2 m/s.
- **Standing rules and lessons applied:** CLAUDE.md rules 1–6, 10, 12, 13;
  `docs/ansys_verification/FINDING_p_floor.md` §4 (`P_MIN`); **L-332** (no guard on an
  `assert`); **L-339** (no `[0-9]*` glob); **L-340** (the plant sized to the reader, carried);
  **L-342** (physics-critical vs infrastructure field classes); **L-343** (the `USER` pin);
  **L-347** (the plant placed where the reader selects, and every channel's control run and
  reported — the defect this file repairs).
- **Compute authority:** Sanaa's permission boarded at commit `bc0e687e`. RANKS = 1, cap 50
  core-min, unchanged from attempts 1 and 2.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING. A GATE FAIL, a NOT A RESULT or a refusal is recorded honestly and never softened.*

---

## PRE-COMPUTE AMENDMENT 1 — 2026-08-26T22:40:23Z — the launcher smoke, registered BEFORE it runs

**Lines whose number changed above this section: 0.** Version 1.1.

**THE CONDITION, AND HOW IT WAS CHECKED.** This amendment is legal because **no compute has
happened under this registration**: `verification/runs/ansys_verification/VMFL011-R3/` — the run
directory this freeze names, and the one every gate artifact would live under — **does not
exist** at **2026-08-26T22:40:23Z**. Checked in the same shell invocation that wrote this
section: `test -e verification/runs/ansys_verification/VMFL011-R3` returns false, and the path is
absent from `ls verification/runs/ansys_verification/`. No level directory, no `RUN_RC.L1`, no
`LAUNCH_RECORD.txt`, no `STATUS.VMFL011-R3` exists anywhere.

**IT ALTERS NO GATE, THRESHOLD, CAP OR LABEL.** The gate quantity, the band `BAND_RMS = 0.030`,
the tier ceiling `GATE REACHED`, the cap of 50 core-min, `endTime` 20 000, `P_MIN`, the mesh
family, the reference and the verdict path are untouched; the EMPTY 77-line gate diff published
above still holds byte for byte.

**WHAT IS REGISTERED.** A **launcher smoke** — `VMFL_SMOKE=1`, **L1 only**, `endTime` shortened
to **20**, in a **scratchpad root that the launcher itself refuses to leave**. It exercises the
launcher end to end (freeze check, the nine input-blob checks, the `--selftest` gate under both
interpreters, the L-343 `USER` pin, the age guard, the cap arithmetic, `blockMesh`, the detached
`timeout` wrapper and the `RUN_RC` write), **grades nothing**, writes nothing under
`verification/runs/`, and **no gate, band, cap, ceiling or label depends on it**. Its cost is
seconds and is reported with the run's calibration.

**WHY IT IS BEING REGISTERED NOW RATHER THAN AT THE FREEZE, STATED PLAINLY AND NOT SOFTENED.**
The R2 registered its smoke inside its freeze; this freeze did not, and that is an omission by
the drafting lane, not a decision. Rather than run an unregistered smoke — which would be a
departure from a frozen document — or drop a queue entry for a launcher whose argv path has been
driven only as far as its usage guard, the smoke is registered here, before it runs, under the
clause that permits exactly this. **The launcher's own `VMFL_SMOKE` guard already refuses any
run root other than a scratch path**, so the registered scope is enforced in the executable path
and not by this prose.

**THE SPECIFIC RISK IT BUYS DOWN.** `run_vmfl011_r3.sh` is a line-for-line derivation of
`run_vmfl011_r2.sh` (blob `b1d6a74a718e8e0dc8c5a76c0a07cf48006d2ab5`), which has already run
this exact case to completion at register row #31 — but it carries one additive block that has
never executed: the L-343 `USER` pin and the four infrastructure fields it writes to
`LAUNCH_RECORD.txt`. **`VMFL064R2-ENTRY-DEF-1` is this team's own precedent for a launcher
defect discovered at launch rather than before it**, and a smoke is the cheap way not to repeat
it.
