# Supervisor sweep of the reach matrix: the BC-times-cut trigger survives six axes at zero solver cost, and the "second independent case" is more sibling than stranger

**2026-08-05, adversarial verification of `DEFECT_REACH_decomposition_cases.md`
(pre-registration commits 99f5d41d / b8ea85c4 / ad55154a / aa51ca08, results
commits 1057b8c0 / 0b022b36) and of the trigger claim it feeds the upstream
report: (freestreamVelocity farfield BC in the recorded tape — necessary;
patchVelocity registration inert per N9) x (cut geometry: scotch np>=3 worst,
planar slabs benign).** Posture: the claim is wrong until it survives. Method:
everything re-derived from the on-disk artifacts at
`/home/ubuntu/certonomous-runs/W4-defect-reach/` with independently written
scripts — **no solver was run; this sweep's ledgered solver cost is 0.00
core-min** (offline numpy only, seconds of wall time). No upstream file was
modified.

**Verdict up front: five axes CONFIRMED, one CONFIRMED with a named evidential
caveat.** The 5.45x cross-residual reproduces to every printed digit from the
dumps under a map this sweep rebuilt byte-identically and then validated on the
exact-coordinate channel (max deviation 0.0 over all 26,149 scotch and 26,227
simple entries). The 7-case BC survey is factually right in every row. The
prediction scoring is honest against the committed text, including all four
misses. What the sweep found against the record is not a refutation but a
weight correction: **the "second, independently meshed snappy case" is a
near-sibling of the first at the operator level** (same background mesh, same
2,777-cell count, same 25,821-state serial system, same 328-face scotch cut,
same dominant serial cells), and across the survey's external-flow cases the
freestreamVelocity BC is perfectly anti-correlated with patchVelocity
registration — so the cross-case survey, taken alone, cannot carry the causal
claim. The record survives anyway because it does not lean on the survey alone:
the N9 within-case control (same mesh, same scotch partition, only the U
farfield block swapped, byte-verified by this sweep) is the separating
experiment, and it is clean.

## Axis 1 — BC survey audit: CONFIRMED, with the confound analysis the record needs stated

Re-read from each case's actual on-disk U boundary file (0.orig/U), not from
the record's table:

| case | file checked | farfield/inlet U BC | freestreamVelocity count in file | defect? |
|---|---|---|---|---|
| A4 (established arms) | `W4-defect-reach/a4_simple2x2x1/0.orig/U` | `freestreamVelocity` | 1 | YES |
| Ahmed-35 | `W4-defect-reach/a35_np1/0.orig/U` | `freestreamVelocity` | 1 | YES |
| A1 | `W4-a1-rank/a1_np4/0.orig/U` | `inletOutlet` (inout) | 0 | no |
| A2 | `W4-a2-provenance/a2_ct_scotch/0.orig/U` | `inletOutlet` (inout) | 0 | no |
| A5 | `W4-a5-decomp/a5_scotch/0.orig/U` | `fixedValue` inlet (internal flow) | 0 | no |
| CBFS | `W4-defect-reach/cbfs_simple411/0.orig/U` | `fixedValue` inlet | 0 | no |
| sail | `W4-defect-reach/sail_simple3x1x1/0.orig/U` | `inletOutlet` (farfield) | 0 | no |

Seven of seven rows check out; the correlate is factually perfect. The N9 arm's
`0.orig/U` reads `inletOutlet` as claimed, and `diff -r` of its `0.orig`
against the established arm's confirms the U farfield block is the ONLY
difference — the record's "verified by diff" statement is itself verified.

**Controls that ARE in place** (checked in each case's own runScript): DV type
and objective are controlled — A1, A2, and the sail are clean cases with shape
DVs and a CD objective, exactly A4/a35's DV type and objective, so "shape DVs +
CD" does not separate defect from clean. Solver is controlled (DASimpleFoam
everywhere except A2's DARhoSimpleFoam, which sits on the clean side). Mesh
family is controlled via the sail (snappy, `cellLevel` present, clean).

**Confounds that remain, and what breaks them:**

1. **The two defect cases are one case family.** Ahmed-35 is A4's own recipe
   with only the STL swapped, and at the operator level the kinship is closer
   than "independently meshed" suggests: same 2,777 cells, same 25,821-state
   serial system, and — measured by this sweep from the addressing files — the
   scotch np=4 cut has the **same 328 processor faces** on both cases, with the
   dominant cross-residual rows landing on the same serial background-mesh
   cells (338/407/275; the record itself observes this as the "defect follows
   the cut" fingerprint). Both share the domain box, the 40 m/s freestream, the
   bluff-body separated regime, and the loose `primalMinResTol` 1e-4. As
   cross-case breadth for the BC correlate, the defect side is effectively
   n=1 case family, not n=2 independent draws.
2. **freestreamVelocity is perfectly anti-correlated with patchVelocity
   registration across the survey.** All three clean external-flow cases (A1,
   A2, sail) register a `patchVelocity` input (checked in their runScripts);
   neither defect case does — the pairing DAFoam's `DAInputPatchVelocity`
   FatalError branch forces. On the survey alone, "patchV registration
   suppresses the defect" fits the seven cases exactly as well as "the BC
   gates it."

Neither confound stands after N9: the papers-protocol arm (inletOutlet WITH
patchV) and the N9 arm (inletOutlet WITHOUT patchV) are both clean on the same
mesh and the same scotch partition where the established configuration reads
8.95%, which separates the BC from the registration **within the case**, where
every other property is held fixed. The verdict is therefore CONFIRMED — but
the causal weight sits on N9 plus the within-case A4 evidence, and the survey
is corroboration, not proof. The upstream report should say so (see the list at
the end).

## Axis 2 — cross-residual reproduction: CONFIRMED (recomputed 5.446299, floor 3.984082e-04, state control to 6 digits)

Recomputed by this sweep's own script from the dumped vectors
(`a35_d_crossres/w4x_res_*.npy`, `w4x_b_np1.npy`), applying the stated
correction `r_true = res + 2b` for the instrument's `Atpsi - b` sign
convention:

| psi from | this sweep, ||r||/||b|| | record | state-controlled (`w4x2_res_*`, in-log crossres2) |
|---|---|---|---|
| np=1 control | **3.984082e-04** | 3.984e-04 | 1.915304e-03 |
| np=4 scotch | **5.446299e+00** | 5.446e+00 | **5.446301e+00** |
| np=4 simple 4x1x1 | **3.308109e-01** | 3.308e-01 | 3.308152e-01 |

with ||b|| = 1.787288e-01 and psi norms 5.804e-02 / 3.042e-02 / 2.440e-02 —
every number in the record's table, to every printed digit. The corrected
vectors match the stored `r_true_*.npy` to the last bit (max |diff| = 0.0).
The scotch ratio is unchanged to six significant digits under the serial
operator linearized at the scotch arm's own mapped state (5.446299 vs
5.446301): the state confound contributes at the 1e-03 level, as claimed.

Three validations this sweep ran that go beyond recomputation:

- **The sign convention is self-proving in the logs.** Every own-operator line
  prints `ratio=2.000000e+00` exactly (`A^T psi = -b` makes `Atpsi - b = -2b`),
  and the raw in-log scotch cross ratio 5.801911 corrects to precisely this
  sweep's 5.446299. The saved raw AD product `a35_d_np1/w4_Atpsi_rank0.npy`
  gives ||Atpsi + b||/||b|| = 3.9841e-04 directly — the floor, computed without
  touching the instrument's res files.
- **The map was rebuilt and exactly validated.** Re-running `build_maps_a35.py`
  reproduces `psi_on_np1_*.npy` and `map_np4_to_np1.npz` **byte-identically**
  (md5 unchanged), with the validation prints matching the record (duplicated
  proc-face phi copies 2.665e-15 scotch / 3.553e-15 simple; mapped primal
  states 8.513e-04 / 2.296e-03). Then the exact-coordinate channel of the A4
  mechanism sweep, applied fresh here: mapped np=4 AdjointIndexing coordinates
  against np=1 coordinates, **max |dxyz| = 0.0 over all 26,149 (scotch) and
  26,227 (simple) entries.** The 5.45x is not a mapping artifact.
- **Localization re-derived from scratch** (own parsers, addressing files,
  face-normal computation): top three |r| entries are 0.7942 / 0.3971 / 0.3971
  on **U2 rows of serial cells 338 / 407 / 275**, all `cellLevel` 0, each
  touching exactly ONE foreign rank through exactly ONE processor face, each
  face x-normal to ~3 digits (normals (1, 0, 0.002-0.007)) — z-momentum
  tangential to x-normal cuts, as claimed. 13 of the top 15 rows sit on
  interface cells (the two exceptions, cells 224 and 281, carry no processor
  face — matching the record's "13 of 15").

One wording nit: the record's "three dominant entries — 82% of the norm"
understates its own evidence. The FIRST entry alone is 81.6% of ||r||; the
three together are 99.9%.

One sub-item COULD-NOT-VERIFY, stated for honesty: a fully
instrument-independent operator product. The assembled `w4_dRdWT.bin` dump is
not in the AD product's normalization (this sweep tried it; momentum rows are
orders off while p rows match — consistent with the M2 finding of the A4
mechanism sweep, which already discredited the assembled dump as a comparison
channel). The operator behind the 5.45x is therefore vouched for by the AD
product's own anchors (exact degenerate 2.000000, np=1 floor 3.98e-04, KSP
convergence of the psi it checks) rather than by a second independent matrix.
Same status as the A4 record; no new exposure.

## Axis 3 — N9 audit: CONFIRMED ("print-identical" is exactly as strong as the printed digits, and the record says so)

- Arm configuration verified byte-level: `a4_inletOutlet_scotch/0.orig/U` is
  **identical** to the papers-protocol arm's (`W4-a4-du0check/du0_np4scotch`)
  — same inletOutlet block, same values. The runScript diff between the two
  arms contains exactly the patchVelocity block: the `patchV` inputInfo entry,
  its DV registration, and the du0 check task. Nothing else differs. `grep -c
  patchVelocity` on the N9 runScript: 0.
- Result verified in-log: `a4_inletOutlet_scotch.log` line
  `W4T framework_dCDdshape=2.406182395247966e-01 CD0=1.522907906302396e-01`,
  under `Decomposition method scotch [4]`. The papers-protocol arm's log prints
  its shape analytic at 5 significant digits: `2.4062e-01`. N9's value rounds
  to exactly that. So "patchV registration inert" is established **at the 1e-05
  relative level the printed precision supports** — which is what the record
  claims ("at printed precision"), and is 4 orders finer than the 9% defect
  separation the arm was built to discriminate. CD0 0.44% below the
  established config's 1.5297e-01, as stated (the BC genuinely changes the
  flow; the analytic still lands in the clean class).
- Pre-registration timing: commit aa51ca08 at 15:23:54Z; the arm started
  ~15:24:14Z (ledger end 15:26:31Z minus wall 137 s). Registered before run,
  20 s of margin. **One record error found:** the doc's N9 header says
  "registered 2026-08-05 ~15:40Z" — wrong; the commit witness is 15:23:54Z.
  The error is against the record's own interest (the true time is EARLIER and
  still pre-run), but it should be corrected.

## Axis 4 — prediction-scoring integrity: CONFIRMED (all four misses scored against the committed words)

The pre-registration text at 99f5d41d was extracted and compared against the
final doc's prediction table: **verbatim identical for N1-N7** — bands,
decision rules, and the N7 ">= 10x ||b||" threshold all unedited. N8 was
registered twice (b8ea85c4 15:15:08Z, ad55154a 15:16:18Z — two wordings, same
thresholds: <= 0.5% vs own FD, <= 1% analytic shift), both before the sail arm
started at ~15:16:23Z; the second commit's margin is 5 seconds, which is
cutting it close enough to note, but the first registration alone (75 s margin)
already covers the arm, and both texts predate the run.

Scores re-checked against logs:

- **N2 NOT HELD is honest**: 1.40% > the registered <= 1%; the registered
  decision rule (> 2%) correctly did not fire.
- **N3/N4/N5 NOT HELD are honest and the numbers are real**: 67.8% / 66.3% /
  62.5% read directly from the three logs' check_totals tables; the N4
  analytic-shift clause fails at 1.36% < 2% exactly as scored. One point in
  the record's favor it does not claim: N4's FD-stability clause ("FD column
  stays within ~0.5% of N3's") actually held — 1.7745e-01 vs 1.7826e-01 =
  0.45%. The record scored the arm NOT HELD anyway because the shift clause
  failed. That is scoring against the letter, in the harsh direction.
- **N7 split is honest**: 5.446 < the registered 10; localization
  ("momentum rows of partition-interface cells" — verified independently, axis
  2) and the np=1 floor ("~1e-04-ish" — 3.98e-04) held.
- **N6, N8, N9 HELD verified from logs**: CBFS objective 1.5279278602e-02 in
  the simple411 log (2.0e-08 from the record arm); the FD pair reconstructs to
  0.055% at serial cell 471 from the two probe logs' objective values; sail
  analytic `2.042422e-01` appears identically in both arms' logs with FD
  2.042325 / 2.042324.

One convention inconsistency found in the N8 table: the new arm's "0.0047%" is
|analytic mag - FD mag| / FD, while the "0.0246% record" cited beside it is
OpenMDAO's vector relative error ||Jan - Jfd|| / ||Jfd|| (the new arm's own log
prints 2.461237e-04 = 0.0246% by that convention — essentially identical to the
record's 2.459048e-04). Same-convention comparison is 0.0246% vs 0.0246%. Both
conventions sit 1-2 orders under the registered 0.5%, so no score changes; the
table should still use one convention.

## Axis 5 — FD-unresolvable check: CONFIRMED on the measured range; no hidden plateau exists in any log

Read directly from the three step-study logs' check_totals tables (analytic
2.9916e-01 in all three):

| h | FD | source |
|---|---|---|
| 1e-3 | 1.7826e-01 | `a35_np1.log` |
| 3e-3 | 1.9774e-01 | `a35_np1_h3e-3.log` |
| 1e-2 | 2.4702e-01 | `a35_np1_h1e-2.log` |

Monotone in h, spacing far outside any Richardson band, no plateau — exactly as
recorded. A grep across the campaign's logs finds no fourth step and no
resolved band anywhere for this case: there is no suppressed FD leg. Scope
caveat, stated: "no plateau" is measured on these three steps only; no h below
1e-3 was tried, and the record's own noise-floor argument (CD tail drift ~6e-4
relative -> ~28% FD noise at h=1e-3) is the reason smaller steps were not
bought. The a35 conviction therefore rests on the cross-residual instrument
alone, exactly as the record states — and axis 2 held that instrument.

## Axis 6 — ledger: CONFIRMED (159.91 re-summed; three entries re-derived)

- The 18 ledger lines re-sum to **159.91** core-min exactly.
- **sail_simple3x1x1, 77.87**: the driver computes wall x 2 / 60 in the ledger
  line itself; 2336 s x 2 / 60 = 77.87. Independent corroboration: the arm's
  `system/decomposeParDict` was staged at 15:16:29Z and the log's last write is
  15:55:15Z (2326 s, plus staging), ledger stamp 15:55:19Z. The stated
  overshoot cause is verified in-log: `Calculating dRdW Coloring... Completed!
  951.38 s` — the "~950 s of the 2336" coloring claim to the digit.
- **cbfs_simple411, 20.00**: 600 s x 2 / 60 = 20.00; log mtime 18:54:40Z vs
  ledger stamp 18:54:41Z, start ~18:44:41Z — after the pre-registration commit
  at 18:44:15Z. (All 2026-08-04 arms start after that commit; the earliest,
  a35_mesh, starts ~20 s after it.)
- **a4_inletOutlet_scotch, 4.57**: 137 s x 2 / 60 = 4.57 (in-log task time
  t=125.8 s + container overhead is consistent); started after the N9
  registration commit, as axis 3 shows.
- Charging convention is consistent: np=3 and np=4 arms under `--cpus=2` are
  charged at the cap (wall x 2), which is what the box actually spends.

## What the upstream report should change (named, not applied)

1. **Qualify "second, independently meshed case."** The honest sentence is:
   same recipe with only the STL swapped, same 2,777-cell background mesh,
   same 25,821-state serial system, and the same 328-face scotch cut hitting
   the same dominant serial cells — a deliberately controlled sibling, which is
   exactly what makes the "defect follows the cut" fingerprint meaningful, but
   which means the defect side of the 7-case survey is one case family, not two
   independent geometries. The reproduction evidence is real; the breadth
   evidence is narrower than the current wording implies.
2. **State the patchVelocity anti-correlation.** Across the survey's
   external-flow cases, every clean case registers patchVelocity and neither
   defect case does; on the survey alone the two hypotheses are
   indistinguishable, and it is the papers-protocol + N9 within-case pair that
   separates them. One clause saying so forecloses the objection an upstream
   maintainer would otherwise raise.
3. **Fix "82% of the norm"** to "the dominant entry is 82% of the norm; the
   three together are 99.9%" (both files carry the current phrasing).
4. In `DEFECT_REACH_decomposition_cases.md` (named here since this sweep does
   not modify records): the N9 header's "registered ~15:40Z" should read
   15:23:54Z (commit aa51ca08), and the N8 sail table should quote both arms
   in one FD-error convention (0.0246% vs 0.0246% by OpenMDAO's vector
   relative error).

## Sweep cost

Zero solver runs; all six axes from on-disk dumps, logs, addressing files, and
git history with this sweep's own scripts. Solver core-min: **0.00**. The only
compute was offline numpy/scipy on the box's own cores, seconds of wall.
