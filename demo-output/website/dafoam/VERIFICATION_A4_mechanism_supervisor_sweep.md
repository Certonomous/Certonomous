# Supervisor sweep of the A4 mechanism record: the 329x cross-residual survives an independent map, an independent script, and a fresh serial run

**2026-08-04, adversarial verification of
`DISCRIMINATORS_A4_decomposition_mechanism.md` (commit 49ab2816) and of the drafted
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`.** Posture: the claim is wrong until
it survives. Method: everything re-derived from the on-disk dumps at
`/home/ubuntu/certonomous-runs/W4-a4-discriminators/` with independently written
scripts, plus one 9-second serial container run (0.30 core-min at the --cpus=2 cap,
`/home/ubuntu/certonomous-runs/W4-a4-verify-audit/`) re-applying the np=1 AD
operator to psi vectors mapped by this sweep's own permutation. No solver arm of the
original session was re-run; no upstream file was modified.

**Verdict up front: the mechanism claim SURVIVES on all five axes.** The 329x
cross-residual reproduces to every printed digit under a permutation this sweep
rebuilt from OpenFOAM's own addressing files and validated on a channel the
original session never used (exact cell/face coordinates, max deviation 0.0 across
all 26,149 scotch entries). The operator was applied matrix-free, not through the
M2-discredited assembled dump. All three confound controls check out bit-for-bit.
The interpretation — wrong operator, not equivalent-discretization adjoint — is
closed by the verified sweep's per-run FD column. What the sweep did find is five
small defects of bookkeeping and provenance, listed at the end; the sharpest is
that **the M1 table's numbers appear in no log** — the instrument script carried a
sign error (`Atpsi - b` where the system is `A^T psi = -b`), every arm's log prints
the degenerate `ratio=2.000000e+00` for its own-operator check, and the tabulated
values are offline sign-corrected recomputations. The correction is exact and this
sweep reproduces it, but the record cites `d_crossres.log` for numbers that log
visibly contradicts.

## Axis 1 — mapping audit: CONFIRMED

The proc-to-serial permutation is the claim's foundation; a wrong permutation would
fabricate exactly this kind of large cross-residual. This sweep re-derived it from
scratch (own parsers, own construction) using only
`processor*/constant/polyMesh/cellProcAddressing` / `faceProcAddressing` and the
`AdjointIndexing_*_of_4.txt` dumps, then compared against the session's stored
`map_np4_to_np1.npz`:

- **Identity:** `tgt` and `sgn` agree with the session's map bit-for-bit, both arms.
- **Exact geometric validation (new channel):** the AdjointIndexing dumps carry
  cell/face center coordinates. Mapped np=4 coordinates against np=1 coordinates:
  max |dxyz| = **0.0e+00** over all 26,149 (scotch) and 26,227 (simple) entries.
  This validates every entry of the map exactly, independent of any solved field.
- **Per-state-group validation** (the original validated on duplicated phi only):
  mapped scotch primal vs np=1 primal by group — U0 rel 5.5e-07, p rel 3.2e-06,
  phi rel 4.6e-07 (reconvergence noise); k 2.8e-03, omega 9.8e-03 (turbulence
  reconvergence, as expected at `primalMinResTol 1e-4`). Overall 2.005e-03,
  matching the record's 2.0e-03. Duplicated-phi copies: max 2.665e-15 (record:
  2.7e-15). Note p and U are not duplicated states — proc-face phi is the only
  duplicated coordinate — so the coordinate channel above is the exact-validation
  substitute this sweep used.
- **Recomputation from dumps:** corrected cross-residuals from `w4x_res_*.npy` +
  2b: np1 **1.140697e-04**, scotch **3.288078e+02** (abs 6.004094e+01, max entry
  42.25), simple **9.367397e-02** — every digit of the record's table.
- **Fresh-run reproduction:** a new case dir staged from the same source, fresh
  serial primal, `w4_crossres` applied to psi vectors mapped by THIS sweep's
  permutation: raw scotch ratio **3.288139e+02**, sign-corrected **3.288078e+02**;
  np1 control 1.140697e-04; simple 9.367397e-02
  (`W4-a4-verify-audit/audit_crossres.log`, 9 s, 0.30 core-min).

The 329x is real and is not a mapping artifact.

## Axis 2 — operator-application audit: CONFIRMED

`runScript_w4.py` task `w4_crossres` evaluates the cross-residual through
`solverAD.calcJacTVecProduct(state -> residual)` — the matrix-free reverse-AD
product, same API family as the KSP shell operator — **not** the assembled
`w4_dRdWT.bin` dump. The record states this and itself measures why it matters;
this sweep reproduces the assembled matrix's error: ||A_asm psi − A_AD psi|| =
**2.305886e+02** x ||b|| at np=1 (record: 230x). The conviction does not rest on
the instrument M2 discredited, and the serial floor 1.14e-04 vs 329x separation is
a property of the AD operator alone.

One undisclosed instrument use found: the **9.1e-03 either-copy confound bound was
computed with the assembled serial matrix** — this sweep reproduces 9.134e-03
exactly as ||A_asm (psi_copy − psi_avg)||. That is the discredited instrument, used
without saying so. It is immaterial here: even inflated by the full 230x
assembled-vs-AD discrepancy factor the bound stays ~30x below the 60.04 signal, and
the duplicate copies disagree by at most 3.6e-04 to begin with. The confound stays
closed; the record should have flagged the instrument.

## Axis 3 — controls audit: CONFIRMED

- **(a) Linearize-at-scotch-state control really used the scotch state:**
  `d_crossres2/w_override.npy` is bit-identical (max diff 0.0) to this sweep's own
  independently mapped scotch primal, sitting 2.005e-03 relative from the np=1
  state. Scotch reads 6.004094e+01 at both states; the np=1 control moves
  1.14e-04 -> 1.004e-03, i.e. the state confound contributes at 1e-03, five orders
  under the signal. Confirmed.
- **(b) RHS invariance under the same mapping:** mapped b vs np=1 b — scotch
  **4.765e-06**, simple **6.898e-06** relative (record: 4.8e-06 / 6.9e-06),
  identical under duplicate-sum and duplicate-average conventions.
- **(c) The discriminating contrast is real:** the SAME serial operator in the SAME
  run applied to the simple-4x1x1 psi maxes at **0.008439** (record: 0.0084), and
  that worst entry sits on a simple partition-interface cell (9 of the top 10 do)
  — 5,006x below scotch's 42.25. If simple's residual had also been huge the test
  would have proven nothing; it is not.
- **Localization reproduces entirely:** U0 rows carry 59.776 of the 60.041 norm;
  15 entries with |r| > 0.5, of which 13 on scotch interface cells, 2 at graph
  distance one, 0 farther; all 15 on `cellLevel` 0 cells (mesh has levels 0 and 1);
  the two worst (42.25, 42.24) at y = −0.1947 and +0.1949 — the y-normal cut
  signature as claimed.
- **Bonus M3(b) re-derivation:** with an independently built
  `pointProcAddressing` map, Xv0 matches np=1 at 0.0, dXv/dshape matches at
  **0.0e+00** both arms, and the captured dCD/dXv seed differs from np=1 by
  **38.437%** (scotch) / **3.086%** (simple) — the record's 38.4% / 3.1%.
- np=1 psi blocks p 0.0312 / U2 0.00494 and scotch 0.521 / 0.117: reproduced;
  the 16.5x norm inflation is real.

## Axis 4 — interpretation audit: CONFIRMED, with one gap noted and closed

Does 329x prove "wrong operator" rather than "exact adjoint of a
different-but-equivalent parallel discretization"? The record leans on serial-vs-
parallel operator disagreement, and its M3(a) primal compare is objective- and
state-level — it never demonstrates residual-field-level identity of the discrete
residual function across decompositions, and **does not acknowledge that gap**. If
decomposition changed the discrete residual itself at processor boundaries, the
scotch adjoint could in principle be consistent with *its* residual while differing
from serial, and the scotch self-consistency reading (1.223e-03, reproduced) would
even fit that story.

The gap is closed, but by the *prior* record, not this one:
`VERIFICATION_A4_decomposition_supervisor_sweep.md` establishes that **the FD
column is computed per run inside each arm's own `check_totals`** — so the scotch
analytic gradient (2.2086e-01) disagrees by 8.95% with the finite difference of its
own decomposed discretization (2.4258e-01). An adjoint that were the exact adjoint
of an equivalent parallel discretization would match its own FD. It does not.
Combined with the fact that OpenFOAM processor patches evaluate the same interior
face fluxes (no legitimate O(1) residual-function difference is available) and that
b maps invariantly at 4.8e-06, the conclusion "the parallel operator is not the
transpose Jacobian of the residual it claims to differentiate" is the one the
evidence supports. Verified in-log besides: 719 GMRES iterations, final residual
1.749572e-07, `PetscConvergedReason: 2`; and in-source: `DALinearEqn.C` sets
`KSPSetPCSide(PC_RIGHT)` and `KSPSetNormType(KSP_NORM_UNPRECONDITIONED)`, so
"converged in the unpreconditioned norm" is literal.

One nuance the record's hierarchy paragraph carries implicitly and readers should
not lose: the defect is a **continuum, not a scotch-only binary**. The
FD-exact simple-4x1x1 psi still leaves 9.4e-02 of ||b|| under the serial operator —
roughly 800x the np=1 floor — while its gradient is correct to 0.00054%. Every
np=4 operator tested differs measurably from serial; scotch's jagged cut is the
catastrophic point. The record's orientation-hierarchy paragraph is consistent with
this; no sentence overclaims it.

**The upstream report's framing survives.** Its table is the verified sweep's own;
"the two operators are different linear maps" is arithmetically forced
(||(A_serial − A_scotch)^T psi|| ≈ 60 given the 2.2e-04 absolute scotch
self-residual and the 4.8e-06 RHS invariance); its submission-readiness table
honestly lists the tutorial reproducer and line-level mechanism as NOT DONE. No
sentence requires retraction. One preemptive strengthening is available to Katie:
adding a line noting that the per-run FD column rules out the
"adjoint-of-an-equivalent-parallel-discretization" objection would close, in the
maintainer's first read, the one gap this sweep had to close from the prior record.
Its "Independent verification" row may now also cite this sweep for the mechanism
numbers themselves, not only the phenomenon.

## Axis 5 — ledger audit: CONFIRMED, two slips

The eight ledger entries sum to **56.77** as claimed against the docket's
`est_core_min` 45; the three coloring-off attempts (0.90 + 23.37 + 19.70 = 43.97)
are ledgered at full wall x cap including both rc=137 kills, and the record
volunteers that the second forced attempt should not have been launched — the
overrun accounting is honest. The surviving nocolor log confirms
`nJacConColors: 26149` and per-column FD progress through 26,148 of 26,149 at
257.8 s before the kill, exactly as narrated. Slips found:

1. **"The five arms that decided the item cost 12.63 core-min" is wrong: they cost
   12.80** (3.17 + 4.70 + 4.43 + 0.33 + 0.17; also 56.77 − 43.97 = 12.80). The
   12.63 omits d_crossres2 and contradicts the record's own totals. The commit
   message repeats it.
2. d_crossres2 is ledgered at `cpus_cap=1` (0.17 core-min) though the standard
   launcher hardcodes `--cpus=2`, and its ledger line lacks the launcher's decomp
   fields — it was launched by hand and the actual cap is unverifiable. At stake:
   0.16 core-min. The docket's `measured_basis` also says "seven container runs";
   the ledger has eight entries.

## Defects found (none overturn the finding)

1. **Provenance of the M1 table (the sharpest).** `w4_crossres` and `w4_dump`
   compute `res = Atpsi - b`, but the system is `A^T psi = -b`; every log therefore
   prints the sign-degenerate `ratio=2.000000e+00` for the controls
   (`d_crossres.log` line 4122; `W4D own_residual` in all three arm logs), and none
   of the record's own-operator numbers (1.14e-04 floor, 1.2e-03 scotch
   self-consistency, 2.083e-05) appears in any log. All are offline sign-corrected
   recomputations from the dumped vectors. The correction is exact
   (`res + 2b`), the record's phrase "the sign convention ... fixed by the np=1
   control" gestures at it, and this sweep reproduces every digit — but the table
   is captioned "`d_crossres.log`:" and the log contradicts it on its face. The
   defensible version: cite the dumped vectors (`w4x_res_*.npy`, `w4_Atpsi/w4_b`)
   and state the sign correction explicitly. (`w4_crossres2`, written after, has
   the sign right; its log matches its numbers.)
2. **The either-copy bound (9.1e-03) silently used the assembled matrix** (axis 2
   above). Immaterial by margin; should carry a one-line caveat.
3. **The cited first-attempt crash log no longer exists.** `run_arm.sh` truncates
   `${TAG}.log` per attempt and all three nocolor attempts share a TAG; the disk
   file is attempt three. The `DAColoring.C:1021` claim itself is corroborated
   statically by this sweep in the shipped container: `mphys_dafoam.py:458` skips
   `runColoring()` unless `adjUseColoring` is true, `DASolver.C:1043` calls
   `readJacConColoring()` unconditionally, and `DAColoring::validateColoring`
   (begins line 931) reaches its `FatalErrorIn ... abort` at line ~1021 — plus the
   ledger's rc=1 at 27 s fits a construction-time crash. Confirmed by code, not by
   the cited log.
4. **12.80 vs 12.63** (axis 5).
5. **Residual-function-identity gap unacknowledged** (axis 4) — closed by the
   prior record's per-run FD column, but the mechanism record should say so rather
   than leave the loophole to the reader.

## Cost of this sweep

One container run, 9 s wall at `--cpus=2` = **0.30 core-min**. Everything else was
arithmetic on dumps. Audit artifacts: `W4-a4-verify-audit/` (staged case, mapped
psi vectors from this sweep's own permutation, `audit_crossres.log`).
