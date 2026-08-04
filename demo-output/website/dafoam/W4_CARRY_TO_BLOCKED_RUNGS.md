# W4 — carrying the warp patch to the blocked rungs: the survey came first, and the survey is the result

**Session 2026-08-04. Docket item `w4-carry-the-warp-patch-to-the-blocked-rungs`,
`est_core_min` 180, gate: *"Each previously failing rung is re-graded under the patched
warp, with the stock verdict kept beside it."* The patch in question is the
adversarially-verified rotation-guard fix
(`rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`,
`VERIFICATION_rotation_patch_supervisor_sweep.md`, commit 6782d33a).**

**Measured spend: 0.0 core-minutes of solve against a 180 core-min estimate.** Not
because the work was skipped, but because the survey this item's claim note promised
found every carry the gate names already on disk — landed piecemeal under four other
items over 2026-08-01 to 2026-08-04 — and found that every rung still blocked is
blocked by a mechanism the warp patch structurally cannot reach. What was missing was
not a solve; it was the consolidated statement, one stale summary row, and the grading
policy the ladder had been following without ever writing down. This document supplies
all three. L-1 (check the repository before acting on a docket premise) and L-32
(satellite rows outlive the corrections that obsolete them) are both operating here,
and this item is the measured demonstration of why they are rules.

---

## 1. The carry table: every previously failing rung, stock verdict beside patched number

"Previously failing" is read broadly: every rung that ever carried FAIL, CONDITIONAL,
or a suspect calibration on the stock-vs-patched question. Grades are against the
shipped toolchain per the policy in §4; patched numbers sit beside them as diagnosis.

| rung | stock verdict (stands) | patched-warp number beside it | evidence | landed under |
| --- | --- | --- | --- | --- |
| A1 CD/shape | **FAIL**, 11.43% agg, idx6 sign-flipped 640.2586% | 0.03745% agg; idx6 1.1649% right-signed; 8/8 in band; 196 of 204 full-table entries bit-identical between halves | `W5-regrade/a1_{unpatched_stock,patched_patched}.log` | `w5-regrade-every-published-gradient-claim` (§1) + `w5-a1-a5-full-fd-tables-under-patched-warp` (§7.1, commit 4e01ef0e) |
| A5 OBJ/shapexUpper | **FAIL**, 46.6377% agg, idx8/idx17 sign-flipped | 2.2372% agg as `check_totals` reports it; idx16's stored FD then shown wrong (`W4_IDX16_IS_THE_REFERENCE.md`): against re-measured FD the patched table is **27/27 in band, 0 flips, aggregate 0.1826%** | `W5-regrade/a5pl_{stock,patched}_checktotals.log`, `/home/ubuntu/certonomous-runs/W4-idx16/` | same two items + the W4 idx16 resolution |
| A4 CD/shape | was CONDITIONAL 10.04%; **verdict of record now PASS — np=1 stock, 1.10%** (decomposition finding, supervisor-confirmed W-3, commit 27d25762) | patched 8.953% at np=4 `scotch` (the patch closes ~11% of the published gap); patched + `simple` 4×1×1 0.00054% | `W5-regrade/a4_{stock,patched}_checktotals.log`, `a4_np1_stock.log` | `w5-regrade` (§2) + the W4 decomposition thread (`PROOF.md` §25.5) |
| A2, all six VERIFIED rows | **PASS**, and the stock re-run reproduces the published 18-row table to every printed digit | CD/shape 1.713791e-02 → **5.059114e-04** (33.9×); CL/shape 1.165163e-02 → **2.189473e-04** (53.2×); CL/twist 1.120617e-02 → **9.737824e-05** (115.1×); CD/twist **degrades** 3.890805e-03 → 5.049348e-03, deep in PASS; patchV rows and geometric constraints bit-identical | `/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_{stock,patched}_checktotals.log` | the W4 A2-provenance session (`PROOF.md` §25.1b), adversarially spot-checked in commit 6782d33a |
| naca0015_sail_coarse CD/CL/shape | **PASS**, 4.52%/0.53% | 0.0246%/0.0125% — the PASS was 97.6–99.5% defect; the "better-behaved than A1" comparison struck | `W5-regrade/sail_{stock,patched}_checktotals.log` | `w5-regrade` (§4b) |

Re-verified for this record at zero compute, not taken from the satellites:

* **The A2 pair was re-parsed from the raw logs by this session** (independent parse,
  not `extract_table.py`), and every number in the row above reproduces. Both logs
  carry the provenance stamp at line 3: stock
  `IDWARP_IMPORTED_FROM: /home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/idwarp/__init__.py`,
  patched `IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py`.
* **All eight W5-regrade `check_totals` logs in the table carry the same stamp pair**
  (checked today, every file). The W-2 hygiene gap the A4 supervisor sweep flagged was
  specific to the `W4-a4-stepsweep` logs and does not touch anything this table rests
  on. No new solves were run, so there were no new logs to stamp.
* The patch file is present, md5 `5d5afd856760c19f03e8c363f0c3ac3d`, and the scratch
  clone precedent (`/home/ubuntu/certonomous-runs/W5-patch/idwarp`) is the one the
  supervisor sweep diffed byte-identical against it.

## 2. The rungs that stay blocked, and why the patch cannot be the unblock

The item's objective — "which other blocked rungs does the same repair unblock?" — has
a measured answer: **none, and none of them for want of trying the patch.** Every
remaining blocked rung dies upstream of, or entirely outside, the one call the patch
changes. The patch touches only IDWarp's generated adjoint derivative files
(`vectorUtils_{b,d}.f90`); the primal warp is md5-identical (supervisor sweep §3).
`warpDeriv` executes in the reverse sweep's warper component — after the state adjoint
is solved. Anything that fails before that point fails identically under either
toolchain.

| rung | where it actually dies | relation to `warpDeriv` |
| --- | --- | --- |
| A3 ONERA M6 adjoint | OOM in `dRdW` Jacobian-coloring setup (fine, 399,360 cells) or the GMRES state-adjoint solve (coarse, 99,840), 8 mitigations ruled out | dies one to two pipeline stages **before** any IDWarp derivative call |
| A6 CRM adjoint | never attempted — 1.45× A3's already-OOM mesh, same structural wall | never reaches the chain at all |
| naca0015_sail_medium | `check_totals` log ends mid-coloring, no result | before the chain |
| naca4412_wing_coarse | `compute_totals` log ends after `d[CD]/d[aero_vol_coords]^T * psi` — DAFoam's own partial, inside the solver component | stops at the solver's partial, upstream of the warper component |
| B3 CBFS field inversion | was `-9` at GMRES iteration 0 — a singular ASM sub-block ILU factorization in the **state adjoint solve**, reproduced offline in scipy; converged 2026-08-04 under `DAFOAM_SUBPC_TYPE=lu` (`fiml-adjoint-conditioning-unblock`, image `dafoam-subpclu:v1`) | the failure was before `warpDeriv`; and the unblocked gradient's β DVs are per-cell `DAInputField` fields that never touch DVGeo/IDWarp. The earlier `patchVelocity` stand-in does not cross `warpDeriv` either — measured, not argued: every patchV row in A1 (§7.1) and A2 (§1 above) is bit-identical between stock and patched runs |

So the repair's reach is now bounded from both sides by measurement: it collapses
every shape-DV gradient error the ladder ever attributed to the rotation branch
(five geometries), it closes ~11% and no more of A4's decomposition artifact, and it
has nothing to offer the memory- and conditioning-blocked rungs because their failures
precede the code it fixes.

## 3. What this session changed in the records

1. **The stale A2 summary cell is struck.** `ACTIVE_RESEARCH.md`'s Ladder-A row A2
   still said "the 96 local FFD shape DVs … are unregraded" two days after the regrade
   landed — the exact satellite-lag defect L-32 names, and the stale cell propagated
   into this very item's launch brief. Corrected in place with a dated supersession.
2. **The grading policy the ladder has been following is now written down** — as a
   PROPOSED section in `DAFOAM_CASE_STATUS.md` (§ "Grading policy — shipped vs patched
   toolchain"), flagged for supervisor review rather than declared. See it there; the
   short form: verdicts are graded against the shipped toolchain and stand; patched
   numbers are recorded beside them as diagnosis-confirmed-by-repair; a rung may
   additionally carry a clearly-labeled patched grade when the paired-run controls are
   on the record; only upstream shipping the fix (or Katie formally adopting a fork)
   can ever move a shipped grade, and that adoption is not a session's call.
3. **The docket item is closed on the record**, with this document as its evidence,
   per the precedent of `w5-a1-a5-full-fd-tables-under-patched-warp` (closed at 0.0
   core-min when the runs turned out to be on disk unread) and the two SPARTA items of
   2026-08-04.

## 4. Ledger

No solver was launched and no container was started for this item; there is nothing to
enter in `solve_registry` for it. Every number above traces to a log produced under an
earlier item and cited by path, and the two A2 headline logs were re-parsed rather than
quoted.
