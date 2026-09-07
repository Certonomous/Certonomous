# D9successor — RESULTS (A5 U-bend pressure-loss minimisation with a meshQualityKS non-orthogonality constraint)

**FROZEN** at `PERMISSION = 60dddc2c04c42008357574aa6a523b7e16bad110` (freeze commit `433a24a8`,
dafoam-supervisor 2026-09-07). Graded run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D9SUCCESSOR-a5-ubend-opt/`, run stamp
`20260907T185531Z_142898`, np=1, cpuset 15. Container `rc=0` on every stage except the registered
F-CEIL probe (`fd_1p0em3` `rc=1`, expected inversion). Total **32.9333 core-min** of the 120.0 cap.
**SUBMISSIONS PARKED.**

## 1. VERDICT

**OFFICIAL (frozen-path) VERDICT: `NOT A RESULT` — but CONFOUNDED by a harness defect, not physics.**
The frozen grader `d9succ_grade.py` produced `NOT A RESULT` driven by `G-FDPERF NOT A RESULT`
("0 of 3 tables"). That "0 tables" is an **L-504 launcher-vs-grader tag-derivation mismatch**, not a
physics finding (§3). The official verdict stands recorded as what the frozen grader produced (rule 2),
and the OFFICIAL disposition (a grading-path reconciliation + regrade of the existing valid records)
is **HELD for the dafoam-supervisor's ruling**.

**HEADLINE, REAL, STANDS ON ITS OWN:** `G-MESH PASS` — the fix works (§2).

## 2. HEADLINE — `G-MESH PASS`: the meshQualityKS constraint held the endpoint inside the envelope

> **The constrained-optimum endpoint measures raw `checkMesh` `Mesh non-orthogonality Max = 69.2937`
> `<= 70.0`** (the case's own `checkMeshThreshold { maxNonOrth 70; }`). D9's UNCONSTRAINED endpoint was
> **80.930** (`D9/RESULTS.md` §2). The mesh-quality inequality constraint drove the endpoint from 80.93
> down under the 70 limit — the fix Sanaa's directive `4ae4b33` required tried, run and recorded, and
> **it holds.** The KS aggregate the driver saw was `70.0077`, over-bounding the raw max by a slack of
> `0.7140` (`KS >= true max`, exactly as the KS design requires; §1.2 of the prereg). Read from the
> `mesh` stage's primal `checkMesh` block (`mesh_20260907T185531Z_142898.log`), the D9-proven
> maxNonOrth-measurement mechanism.

`G9-3 GATE FAIL`: the SLSQP driver reported failure (`driver_failed=True`), `OBJ 52.34522 -> 50.04350`
(objective moved; physical plant satisfied). This mirrors D9's G9-3 and is expected for a constrained
single-DV-group SLSQP run; the objective magnitude is reported, not gated (prereg §3.4).

## 3. CRASH-TRIAGE — the `G-FDPERF` "0 tables" is a FROZEN-INSTRUMENT tag mismatch (L-504)

The frozen launcher writes the FD-stage directories with `sed 's/./p/; s/-/m/; s/+/p/'` applied to the
literal step strings, giving `fd_5p0em5`, `fd_1p0em4`, `fd_2p0em4`, `fd_1p0em3`. The frozen grader's
`fmt_tag` uses `"%.1e"`, which **zero-pads the exponent**, so it looks for `fd_5p0em05`, `fd_1p0em04`,
`fd_2p0em04`. The names disagree, so the frozen grader finds **0 of 3** FD dirs and returns
`G-FDPERF NOT A RESULT` — although **all three usable records EXIST and are VALID** (`status COMPLETE`,
`J_an`/`J_fd` length 27, endpoint shape `l2 = 0.1622`).

This is exactly the **L-504** launcher-vs-grader derivation mismatch, and it vindicates the real-launch
requirement a second time: a self-consistent selftest (which builds AND reads with the same `fmt_tag`)
structurally cannot catch it; only the real launch, which uses the launcher's `sed`, exposed it. (D9
hit the same latent issue — `D9/RESULTS.md` notes `fd_1p0em05 -> fd_1p0em5`.) Recorded by the
dafoam-supervisor as an L-504 corroborating instance (crash-triage ruling 2026-09-07).

## 4. DIAGNOSTIC tag-corrected regrade — ***NOT the official verdict***

Authorized by the supervisor's ruling. `cases/dafoam/ladder-a/A5/curriculum_D9successor/d9succ_diag_regrade.py`
imports the FROZEN grader by path and monkeypatches ONLY its `fmt_tag` to reproduce the launcher's
`sed` derivation (the frozen grader file on disk is NEVER edited — rule 6); every gate, band, plant and
refusal path is the frozen logic. It reveals the TRUE picture the tag bug hid:

- **`G-FDPERF PASS`** — endpoint FD table formed over 3 of 3 registered usable steps
  (`5e-5, 1e-4, 2e-4`) at the optimised design point; the FD reader plant fired
  (planted `1.234e-3`, read back `1.234e-3`).
- **`G-GRAD PASS`** — aggregate adjoint-vs-FD relative error **`1.137e-3` `<= 5.0e-2`** band, **0 sign
  flips**, over the 15 gradeable components (excellent adjoint accuracy where measurable).
- **`G9-5 NOT A RESULT`** — only **15 of 27 components (55.6 %)** show a demonstrated plateau across the
  3 usable steps, below the registered `70 %` floor. **The 12 ungradeable components
  (`[1,2,7,9,10,11,13,15,18,19,22,23]`) were ALL *NOT* named in advance; the three idx16-class
  components named in advance (`[8,16,17]`) all GRADED cleanly** — the "more interesting half" the D9
  framework anticipated (an ungradeable component the document did not predict).

**DIAGNOSTIC verdict (not official): `NOT A RESULT`, driven by `G9-5` — the §3.3-registered
"necessary-but-not-sufficient GOOD-NOT-A-RESULT".** The mesh-quality constraint moved the endpoint into
the envelope (`G-MESH PASS`) AND the endpoint admits an FD verification (`G-FDPERF PASS`) with an
accurate adjoint (`G-GRAD PASS`), but the **squeezed FD window** (prereg §2) means only 55.6 % of
components form a common plateau across `{5e-5,1e-4,2e-4}` — below the 70 % floor. This is precisely the
predicted outcome that motivates the **primal-tightening (D6RF4-class) successor** to widen the window
from below. **This physics reading is DIAGNOSTIC** until the supervisor rules on the grading-path
reconciliation and an official regrade of the existing records (no re-solve).

## 5. COST (rule 12)

Per-stage MEASURED core-min (ledger, ranks=1 all): `cal 1.35 + rep1 0.2 + rep2 0.1833 + opt 6.6833 +
mesh 0.2167 + fd_5p0em5 7.1833 + fd_1p0em4 6.8667 + fd_2p0em4 6.75 + fd_1p0em3 3.5 = 32.9333` gross,
cap 120.0 (not hit). `= cleaned` (max stage wall 431 s < the 3600-s stall figure; no cap fired,
no OOM). Waste-in-run 0.000 core-min (the F-CEIL probe's 3.5 core-min bought the predicted-inversion
finding, not waste). Ratio actual/predicted `32.9333 / 39 = 0.844` (favourable, ~16 % under). Dollars
`0.54889 core-h x $0.0513 = $0.02816 DERIVED, NOT MEASURED`, reported-by-owner
(`COMPUTE_BUDGET_CHARTER.md` §5). **Calibration lesson (named-in-advance, prereg §5):** the `x1.5`
constraint-overhead multiplier on `opt` OVER-priced — measured `opt(constrained) / D9 opt = 6.6833 /
7.05 = 0.948`, i.e. the meshQualityKS constraint added essentially NO net wall (its adjoint is cheap and
SLSQP terminated similarly), so a future meshQualityKS-constrained A5 `opt` estimate should use `~1.0x`,
not `1.5x`. The full COST_CALIBRATION row is filed in `docs/COST_CALIBRATION.md`.

## 6. WHAT AWAITS

The OFFICIAL disposition is HELD for the dafoam-supervisor: a grading-path reconciliation (the grader's
`fmt_tag` -> the launcher's `sed` derivation) regrading the EXISTING valid records (no re-solve) — via a
`VERIFICATION_CHARTER.md` §2d.1 repair (coordinated with verification) or a clean successor grader
(supervisor's authority). The diagnostic (§4) is what that regrade will show: `NOT A RESULT` by `G9-5`
(the registered GOOD outcome), with `G-MESH`/`G-FDPERF`/`G-GRAD` all PASS. **`G-MESH PASS` (§2) stands
regardless of that ruling.**
