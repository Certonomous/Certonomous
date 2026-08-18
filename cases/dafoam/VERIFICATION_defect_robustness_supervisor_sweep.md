# Supervisor sweep of the defect-robustness record: the 24,300-fold collapse and the hidden-defect number both reproduce from raw vectors; the one number that failed audit is a Krylov count copied from the wrong arm

**2026-08-07, adversarial verification of `DEFECT_ROBUSTNESS_mesh_and_setup.md`
(pre-registration commit 25f52868, amendment commits 671f40bb / c22b0f00 /
b0aa6102 / 4ea782e3, results commit 49631723) and of the two claims it feeds
the upstream report: the limiter branch in `linearUpwind limited` gates the
defect, and the `inletOutlet` BC lever hides a still-wrong operator under a
clean gradient.** Posture: every claim is wrong until it survives. Method:
everything re-derived from the on-disk artifacts at
`/home/ubuntu/certonomous-runs/W4-defect-robustness/` (and the discriminators'
reference dumps at `W4-a4-discriminators/`) with independently written numpy
and shell — **no solver was run; this sweep's ledgered solver cost is 0.00
core-min** (offline recomputation on dumped vectors, log re-extraction, byte
diffs). No upstream file was modified.

**Verdict up front: five axes CONFIRMED, one CONFIRMED WITH A NAMED ERRATUM.**
The R5 cross-residual pair — the record's most consequential numbers —
reproduce from the raw dumped vectors under this sweep's own recomputation:
**scheme lever 1.354841e-02 x ||b||, BC lever 1.047165e+00 x ||b||** (record:
1.3548e-02 / 1.0472), against an established reference this sweep also
recomputed from the discriminators' raw dumps (328.81 x ||b||, np=1 floor
1.1407e-04). The collapse factor is 328.81 / 0.013548 = **24,270 ≈ the
record's 24,300**; the hidden-defect ratio is 1.047165 / 6.4028e-06 =
**163,548 ≈ the record's 163,600**. The one factual error found anywhere in
the record: **the established configuration's adjoint KSP count is 719, not
590** — a fleet-wide grep shows "590 iterations" exists in exactly one log,
`W4-defect-reach/a4_simple2x2x1.log`, a *different* arm (simple 2x2x1 cut,
1.40% error). The error direction is harmless-to-favourable for the claim
(the true conditioning collapse is 719 -> 41 = 17.5x, larger than the reported
14.4x), but the number appears in at least six places and must be corrected.

## Axis 1 — R6 audit: CONFIRMED (one-word edit verified byte-level; all four error numbers and three of four KSP counts re-extracted; the fourth is the erratum)

**The one-word claim is literally true.** `diff` of
`a4knob_divlinupw_unlim/system/fvSchemes` against the established source
`A4-ahmed-body/coarse/system/fvSchemes` shows exactly one changed line —
`div(phi,U) bounded Gauss linearUpwind limited;` -> `... linearUpwind
default;` — and every other input is byte-identical: `fvSolution`,
`controlDict`, `decomposeParDict`, `blockMeshDict`, `snappyHexMeshDict`,
the whole of `0.orig`, and `runScript.py` all `cmp`/`diff -r` clean. The
naming claim behind the arm checks out in the file itself: `gradSchemes {
default Gauss linear; limited cellLimited Gauss linear 1; }`, so `limited` is
the limited gradient and `default` the unlimited one, as the record argues.
The driver (`run_a4_knob3.sh`) enforces this with its own in-script asserts.

Re-extracted from the logs, all matching the record's table:

| arm | analytic | FD | rel. err | KSP (log) | KSP (record) |
|---|---|---|---|---|---|
| established (`a4_np4_patched.log`, stepsweep) | 2.2086e-01 | 2.4258e-01 | 8.9531e-02 | **719, reason 2** | **590 — WRONG** |
| R6b `linearUpwind default` | 2.0572e-01 | 2.0399e-01 | 8.4866e-03 | 41, reason 2 | 41 ✓ |
| R6a `Gauss linear` | 2.0299e-01 | 2.0267e-01 | 1.5707e-03 | 223, reason 2 | 223 ✓ |
| R3a1 `upwind` | 2.7681e-01 | 2.7670e-01 | 4.0949e-04 | 41, reason 2 | 41 ✓ |
| R3a2 gradlim only | 3.1706e-01 | 3.2562e-01 | 2.6276e-02 | 780, reason 2 | 780 ✓ |
| R6b-control np=1 | 2.0572e-01 | 2.0568e-01 | 1.6215e-04 | 38, reason 2 | — |

**The erratum.** The established scotch np=4 arm reads **719 iterations** in
every log that ran it (`W4-a4-stepsweep/a4_np4_patched.log`,
`W4-a4-discriminators/d_np4scotch.log`, and every h-sweep leg — 15 logs, all
719). A grep of the entire runs tree for "iterations: 590" returns one file:
`W4-defect-reach/a4_simple2x2x1.log`, the simple-2x2x1 partition arm. The
record's "590" is a mis-transcription from that arm and appears in the R6
table, the R3a table and text, the R3c reasoning ("~10 restart cycles" — at
719 it is ~12), the R2b text, and finding 2. No verdict changes: 719 -> 41 is
a *larger* conditioning collapse than claimed. The gmresRelTol-1e-10 arm's 811
(record line 26) is correct (`a4_np4_tol1.0e-10.log`), as are np=1 542, np=2
561, np=3 753. The record's claim "0.849% is a factor 10.5 below 8.95%" and
the R6b np=1/np=4 identical-analytic observation (2.0572e-01 at both, FD
2.0568e-01 vs 2.0399e-01) both re-extract exactly.

## Axis 2 — R5 reproduction: CONFIRMED (both cross-residuals recomputed from raw vectors; convention, callback, mapping, and lever isolation all verified; one protocol gap named)

This sweep recomputed both cross-residuals from the dumped vectors with its own
script, trusting no staged intermediate:

| quantity | this sweep (own numpy, full precision) | record |
|---|---|---|
| R5a scheme lever, scotch psi under serial operator | **1.354841e-02 x \|\|b\|\|** | 1.3548e-02 ✓ |
| R5a np=1 control floor | 1.998129e-06 | 2.00e-06 ✓ |
| R5b BC lever, scotch psi under serial operator | **1.047165e+00 x \|\|b\|\|** | 1.0472 ✓ |
| R5b np=1 control floor | 6.402838e-06 | 6.40e-06 ✓ |
| established reference (recomputed from `W4-a4-discriminators/d_crossres` raw dumps) | 328.81 x \|\|b\|\|, floor 1.140697e-04 | 329 / 1.1e-04 ✓ |
| collapse factor, scheme lever | 328.81 / 1.354841e-02 = **24,270** | "24,300" ✓ (rounding) |
| floor ratio, BC lever | 1.047165 / 6.402838e-06 = **163,548** | "163,600" (display-precision rounding; both 1.6e5) |

- **Sign convention verified, not assumed.** The instrument saves
  `res = A^T psi - b` for the system `A^T psi = -b`; the correction
  `r_true = res + 2b` is the only reading under which the np=1 controls
  collapse (to 2.0e-06 / 6.4e-06) while the uncorrected ratios sit at the
  degenerate ~2.0 the logs print (2.000045 / 2.257554). The staged
  `r_true_*.npy` files equal this sweep's own `res + 2b` to the last bit.
- **Matrix-free callback verified in code.** `w4_crossres`
  (`W4-a4-discriminators/runScript_w4.py` lines 263-298) evaluates both `b`
  and `A^T psi` through `DASolver.solverAD.calcJacTVecProduct` — the same
  matrix-free AD product the KSP uses. The assembled `w4_dRdWT.bin` is dumped
  by `w4_dump` but never read by the crossres path.
- **The np4->np1 map independently rebuilt.** From the raw
  `cellProcAddressing`/`faceProcAddressing`/`AdjointIndexing` files, this
  sweep's own reconstruction of `psi_on_np1` equals the staged crossres input
  **exactly** (`np.array_equal` true) for both levers; 26,149 - 25,821 = 328
  duplicated proc-face phi states in both; duplicate phi copies agree at
  2.665e-15 / 3.553e-15 (machine zero); mapped primal states at 2.553e-03 /
  2.026e-03 (reconvergence noise). The `np1ctl` staged psi equals the np=1
  dump's own psi bit-for-bit. `build_maps_upw.py` / `build_maps_io.py` differ
  from each other only in the lever string.
- **Lever isolation verified byte-level.** The upw arms keep the established
  `freestreamVelocity` U block and change only `div(phi,U)` to `bounded Gauss
  upwind`; the io arms keep `linearUpwind limited` and carry a `0.orig/U`
  **byte-identical** to the N9 arm's (`diff` clean against
  `W4-defect-reach/a4_inletOutlet_scotch/0.orig/U`). All np=4 arms:
  `numberOfSubdomains 4; method scotch;`, same 2,777-cell mesh, same
  25,821-state serial system as the established reference.
- **The 16-digit corroboration is real:** `io_d_np4scotch.log` prints
  `framework_dCDdshape=2.406182395247966e-01`; the N9 record arm printed the
  same sixteen digits from a separately staged dir and a different task.
- **One protocol gap, named rather than waved off:** the established 329x was
  additionally confirmed under a state-override control (`w4_crossres2`:
  328.808 with the linearization-state confound removed vs 328.814 without —
  re-read from `d_crossres2.log` by this sweep). **No crossres2-style control
  was run for either R5 lever**, so the linearization-state confound (np=4
  psi evaluated under the np=1 reconverged state) is bounded only indirectly:
  by the crossres2 precedent showing the confound moves the ratio in the 4th
  digit, and by the sibling scheme-lever row putting the whole
  protocol-noise floor at <= 1.35e-02 on this mesh — 77x below the 1.047
  signal. The conclusion survives; the control worth ~0.4 core-min should be
  bought next time the container is warm.

## Axis 3 — seven-case survey: CONFIRMED (all seven fvSchemes re-read from disk; every cell of the table checks out)

Re-read by this sweep from each case's live `system/fvSchemes`, `0.orig/U` (or
`0/U`), `runScript*.py`, and `constant/turbulenceProperties`:

| case | dir checked | `div(phi,U)` | limited? | fsV? | tol | turb |
|---|---|---|---|---|---|---|
| A4 | `A4-ahmed-body/coarse` | `bounded Gauss linearUpwind limited` | **YES** | YES | 1.0e-4 | kOmegaSST |
| Ahmed-35 | `W4-defect-reach/a35_np4scotch` | same | **YES** | YES | 1.0e-4 | kOmegaSST |
| A1 | `W4-a1-rank/a1_np4` | `bounded Gauss linearUpwindV grad(U)`, gradSchemes `Gauss linear` | no | no | 1.0e-8 | SpalartAllmaras |
| A1+fsV (R1) | `W4-defect-robustness/a1fs_np4scotch` | same unlimited | no | **YES** | 1.0e-8 | SpalartAllmaras |
| A2 | `A2-mach-wing` | `bounded Gauss linearUpwindV grad(U)` | no | no | 1.0e-8 | SpalartAllmaras |
| A5 | `W4-a5-decomp/a5_scotch` | same | no | no | 1e-8 | SpalartAllmaras |
| CBFS | `S1-cbfs-inversion/cbfs_inv` | `Gauss linearUpwind grad(U)` | no | no | 1.0e-6 | kOmegaSST |
| sail | `W4-defect-reach/sail_simple311` | `bounded Gauss linearUpwindV grad(U)` | no | no | 1.0e-8 | SpalartAllmaras |

The limited-vs-unlimited split matches the record's table exactly. The CBFS
subtlety the record flags was checked directly: every limiter token in CBFS's
`fvSchemes` (`faceLimited` twice on line 25/28, the `cellLimited` family list,
`limited 0.33` on lines 44/63) sits inside `//` or `/* */` comments; the live
gradSchemes is unlimited `Gauss linear`. The turbulence-model elimination
holds (kOmegaSST on CBFS, clean side). The `primalMinResTol` third-confound
row is right, including that it remains open. The R1 arm's runScript contains
zero `patchV` references (`grep -c` = 0).

## Axis 4 — R4 conformal mesh: CONFIRMED

`a4conf_np4scotch/constant/polyMesh/cellLevel` reads **`2336{0}`** —
OpenFOAM's uniform-list form, 2,336 cells all at level 0; the mesh log prints
`cells: 2336` and `Mesh OK.`. The arm keeps `linearUpwind limited`, keeps the
`freestreamVelocity` block, and ran `scotch [4]` (in-log). The 2.82% traces to
`a4conf_np4scotch.log`: analytic 1.8315e-01, FD 1.8847e-01, rel. err
**2.8187e-02**, KSP 481 reason 2. As a bonus, both cut-classification claims
were re-run with the reach campaign's `analyze_cuts.py` (unmodified, offline):
A1 np=4 scotch = **131 cut faces, 120 oblique** and A4 np=4 scotch = **328 cut
faces, x143/y7/z159/oblique 19** — both exactly as the record states.

## Axis 5 — prediction scoring: CONFIRMED against the committed wording (one scoring observation, stated)

- **Registration integrity:** the file at commit 25f52868 equals the current
  file's first 188 lines byte-for-byte (only the trailing `---` separator was
  consumed by the first amendment). Nothing above the marked line moved.
- **Registration-before-run holds for every amendment**, by commit timestamp
  vs (ledger completion − wall): 671f40bb 17:14:47Z < R3a1 start ~17:15:08;
  c22b0f00 17:30:52Z < R6b start ~17:31:13 and first R5 dump ~17:32:02;
  b0aa6102 17:35:00Z < np=1 control start ~17:35:08; 4ea782e3 17:38:51Z <
  R2b start ~17:39:13. Tight, but ordered, every time.
- **R1 NOT HELD scored as written:** outcome 0.043% falls in the registered
  "<= 0.5%" alternative branch, and the results section quotes the registered
  alternative verbatim (checked word-for-word against 25f52868). Analytic
  shift 1.55e-07 re-derived from the logs (6.433596e-02 vs 6.433595e-02;
  rel. errs 4.2823e-04 / 4.2792e-04 recomputed from the printed abs errors).
- **R2 NOT SCORED scored as written:** `a4med_np4scotch.log` shows KSP
  residual 1.718753e-02 at iteration 1000, `PetscConvergedReason: -3`,
  `AnalysisError`, rc=1 — no analytic exists; the registered bands all
  presuppose one. R3b (primal gate failure) and R3c (stall at 2.507895e-02,
  reason -3) likewise evidenced in their logs and scored as misses, not spun.
- **The harsh direction is the spine and it held:** four NOT HELD, two NOT
  SCORED, all against pre-committed wording; R3a2's "direction held, magnitude
  under the band" is reported as NOT HELD, not upgraded.
- **One scoring observation, for the next registration rather than against
  this one:** R5b is scored "HELD numerically (1.047x <= 5x), loud in
  substance," and the substance — the lever hides the defect — rests on the
  floor-ratio criterion (163,548x), which was NOT one of the registered
  bands; by the registered `<= 5x ||b||` wording alone, 1.047x counts as a
  collapse. The record is transparent about this split, and the
  extra-registration reading runs in the harsh direction against the lab's
  own prior "safe" framing, so nothing is being smuggled — but the episode
  shows the `<= 5x` band was mis-calibrated by ~5 orders of magnitude
  against the actual np=1 floors (1e-6..1e-4). Future cross-residual
  registrations should band in units of the configuration's own floor, not
  of ||b||.

## Axis 6 — ledger: CONFIRMED

The 21 session lines re-sum to **exactly 128.28 core-min**, and every line's
`core_min` recomputes exactly as wall x 2 / 60 (21 of 21 OK). Spot-checked
lines as directed: the **33.60** refined-scotch arm is `rc=1` (the failed
adjoint) and is charged in full, as claimed; **19.83** (R2b) and **9.50**
(R3a2) also recompute exactly. The R2b line's self-written timestamp
(17:49:08Z) is present, consistent with the detached-driver survival story.
(Note for the file's future readers: a 22nd line — `a1lim_np1`, 6.40
core-min, 2026-08-07T20:16:15Z — was appended by the follow-on R7 campaign
while this sweep ran; it is outside the audited session and does not affect
the 128.28/150 figure, which describes the session at its closing commit.)

## What the upstream report must change (named, not applied — per the no-modification rule)

1. **Replace 590 with 719** everywhere the established scotch np=4 KSP count
   is cited (R6 table, R3a table and prose, R3c reasoning — "~10 restart
   cycles" becomes ~12, R2b prose, finding 2, and the same figure quoted
   forward into any successor doc). 590 belongs to the simple-2x2x1 arm at
   1.40%. Every collapse ratio only grows.
2. Optionally restate the hidden-defect floor ratio at full precision:
   163,548 (1.6e5), not 163,600 — display-precision rounding, flagged for
   hygiene only.
3. Add one sentence to R5 acknowledging that no crossres2-style
   state-override control was run for the levers, with the two bounds this
   sweep names (crossres2 precedent: 4th-digit effect; sibling-lever
   protocol floor 1.35e-02 << 1.047).
4. Carry the axis-5 banding lesson into the next registration: cross-residual
   verdict bands in units of the configuration's own np=1 floor.

## Cost

Solver core-min consumed by this sweep: **0.00** (offline numpy on dumped
vectors, log greps, byte diffs, and two `analyze_cuts.py` re-runs on
addressing files). Nothing was re-run in the container; the <=10 core-min
re-run authority was not needed.
