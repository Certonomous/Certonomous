# F2 — Transonic NACA0012 (2D): record correction and shock-gate resolution limit

**Date:** 2026-07-30
**Status of this document:** correction notice. It supersedes the F2 numbers
and the F2 shock-gate interpretation previously carried in
`demo-output/website/mega-batch/PHYSICS_FAMILIES.md` ("Family 2") and
`demo-output/website/campaign/CAMPAIGN_STATUS.md` ("F2").
**Written in response to:** an act-survey audit that raised two F2 defects.
One is confirmed and acted on. One is not what it was reported to be, and
that is recorded here too, because a survey finding that fails verification
is itself part of the record (LESSONS L-22).

---

## 1. The case is a NACA0012 and always said so — the "misdescribed as RAE2822" finding does not hold

**Claimed:** the roadmap and campaign records describe F2 as "transonic
RAE2822", when it is a NACA0012, so the record's own title misdescribes the
case.

**Checked.** Every record that names F2 names it a NACA0012:

| Record | Line | Text |
|---|---|---|
| `demo-output/website/campaign/CAMPAIGN_STATUS.md` | 24 | `## F2 — Transonic NACA0012 (2D)` |
| `demo-output/website/campaign/CAMPAIGN_STATUS.md` | 406 | summary-table Case column: `NACA0012` |
| `demo-output/website/mega-batch/PHYSICS_FAMILIES.md` | 93 | `## Family 2 -- transonic NACA0012 (SHIPPED, with a documented substitution)` |
| `sdk/workflows/transonic_airfoil.py` | 1 | `"""Transonic NACA0012 airfoil, rhoSimpleFoam + k-omega SST ...` |

A repo-wide search for `RAE2822`/`RAE 2822` (case-insensitive, all
`*.md`/`*.json`/`*.py`/`*.html`/`*.txt`, excluding `dist/`) returns 13 hits.
None of them titles or labels F2 as an RAE2822 case. Eleven are the
*disclosure* of the substitution — `PHYSICS_FAMILIES.md:98-107`,
`transonic_airfoil.py:18-24`, both of which say in terms that no citable
digitized RAE2822 Cp dataset was found and that **no RAE2822 quantitative
comparison is claimed anywhere**. The remaining two are unrelated
(`docs/DPW-CRM-SCOPING.md:209` lists RAE 2822 as one of two candidate
geometries for a *different*, unbuilt scoping case; `docs/NUMERICS_KNOWLEDGE.md`
cites published RAE 2822 CD spreads from the literature).

**Corrected position:** no retitle is required and none was made. The
substitution is disclosed, with its reason, in every place the case is
described. The survey read the module's honest statement of *why RAE2822 was
not used* as evidence that the record *claimed* RAE2822. This is the
mirror image of L-22: not a real phenomenon attached to the wrong case, but a
correct reading of a disclosure attached to the wrong conclusion.

## 2. The cited primary-case numbers were real but unreconstructible — now reproduced and retained

**Claimed:** `CAMPAIGN_STATUS.md:36` cites a primary case at M=0.8,
alpha=1.25 deg, Re=6e6, Cd=0.0432, Cl=0.109; a search of all 280 transonic
ledger entries found no run at those conditions and no run pairing
Cd around 0.0432 with Cl around 0.109. Therefore the numbers trace to
nothing and must be corrected or withdrawn.

**The ledger half of that is correct.** Verified independently against
`demo-output/website/mega-batch/ledger.jsonl` (208,193 parseable records; 280
carry `"solver": "rhosimplefoam-naca0012-transonic"`):

- No entry at M=0.8 / alpha=1.25 deg / Re=6e6. The nearest is index 205467,
  M=0.7973, alpha=1.349 deg, Re=6.25e6, Cd=0.04307, Cl=0.13218,
  timestamp `2026-07-28T06:44:33Z` — exactly as the survey reported.
- Ten entries carry Cd within 0.0008 of 0.0432; none of them carries Cl within
  0.006 of 0.109. Nine entries carry Cl within 0.006 of 0.109; none of them
  carries Cd within 0.0008 of 0.0432. No entry pairs both.

**The conclusion drawn from it is wrong.** The primary case is not a batch
sample and was never expected to appear in the batch ledger. It is a
*pre-batch validation-gate solve*, run before the family was shipped. Its
provenance is commit `6cc7f629` (2026-07-28 05:25:35 +0000), whose own message
states the gate result — "M=0.8/alpha=1.25 case lands the suction-side shock
at x/c=0.556, inside the 0.35-0.60 band" — and, in the same message, explains
why nothing survived: "Both families were tested end-to-end through
mega_batch.run_task **against a scratch ledger** before this commit; the real
ledger and running batch (PID 104893) were never touched." The scratch ledger
was discarded and `demo-output/website/mega-batch/work/transonic-naca0012/` is
empty. That is the genuine defect: **a validation-gate result was published
from a run whose primary artifact had not been retained**, leaving a headline
number that could be neither located nor checked.

**Resolved by re-running it.** The case is deterministic and costs 34 s. It
was re-run today from the unmodified `sdk/workflows/transonic_airfoil.py` at
the recorded 2000 iterations. It reproduces to every published digit:

| Quantity | Published (PHYSICS_FAMILIES.md:170-183) | Reproduction 2026-07-30 |
|---|---|---|
| Cd | 0.0432 | **0.0431920118** |
| Cd spread (convergence) | 0.00093 | **0.0009328060** |
| Cd, pressure part | 0.0369 | **0.036911634** |
| Cd, viscous part | 0.0063 | **0.0062803778** |
| Cl | 0.109 | **0.109011072** |
| Upper-surface shock x/c | 0.556 | **0.55607646** |
| Lower-surface shock x/c | 0.608 | **0.608440365** |
| Solver wall time | 33.8 s | **33.7 s** |

The documented secondary run reproduces too — M=0.734, alpha=2.79 deg,
Re=6.5e6, published Cd=0.0405 / Cl=0.386 / upper shock x/c=0.556 / 26.3 s,
reproduced **Cd=0.0404601736 / Cl=0.386286408 / 0.55607646 / 25.8 s**.

**Primary evidence, retained this time (absolute paths):**

- `/home/ubuntu/Certonomous/demo-output/website/campaign/F2_runs/F2_reproduction_2026-07-30.json`
  — both runs' full metric records with UTC start/finish stamps
  (primary: `2026-07-30T16:54:57.520580+00:00` → `2026-07-30T16:55:33.391951+00:00`).
- `/home/ubuntu/Certonomous/demo-output/website/campaign/F2_runs/evidence/primary_M0.8_a1.25_Re6e6__coefficient_history.dat`
  — the full 2000-iteration force-coefficient history; the last row reads
  `4.31920118e-02` (Cd) and `1.09011072e-01` (Cl) directly off the solver's own
  output, and the flatness of the last ~100 rows is the convergence evidence.
- `/home/ubuntu/Certonomous/demo-output/website/campaign/F2_runs/evidence/primary_M0.8_a1.25_Re6e6__surface_p_iter2000.txt`
  — the sampled surface pressure the shock detector consumes, from which the
  detector's whole output alphabet in §3 is derived. Same two files for the
  secondary case, same naming.

  *(These two are verbatim copies of the run's own
  `postProcessing/forceCoeffs1/0/coefficient.dat` and
  `postProcessing/surfaceP/2000/p_airfoil.raw`, which remain in place in the
  case directories. The copies exist because `.gitignore` excludes
  `**/postProcessing/` and `*.raw` as bulk regenerable solver output — a rule
  worth keeping, but one that would otherwise have left this record citing
  untracked files, which is the exact defect being corrected here.)*
- `/home/ubuntu/Certonomous/demo-output/website/campaign/F2_runs/primary_M0.8_a1.25_Re6e6/log.rhoSimpleFoam.gz`,
  `log.blockMesh`, `log.checkMesh`, and the full `system/` + `constant/`
  dictionaries. Same file set under `secondary_M0.734_a2.79_Re6.5e6/`.

**Nothing is withdrawn under this heading.** Cd=0.0432, Cl=0.109 and the
shock position 0.556 stand, now on retained primary evidence rather than on a
commit message. What is corrected is the *citation*: these are pre-batch
validation-gate numbers from a dedicated solve, not batch-ledger samples, and
the record now says so and points at the artifact.

## 3. CONFIRMED — the shock detector cannot resolve the deviation the gate claims

**Claimed:** the detector returns only 8 distinct values across 280 runs
because it snaps to mesh nodes; adjacent spacing near the gate is about
0.048-0.052 chord while the claimed deviation from the inviscid reference is
0.044 chord, i.e. smaller than one detector increment; and runs in the same
nominal neighbourhood report 0.608 rather than 0.556.

**Confirmed on every point, from primary evidence.**

**The mechanism.** `sdk/workflows/transonic_airfoil.py:585-601`
(`shock_location`) walks consecutive pairs of sampled surface points, takes
the pair with the greatest positive `dCp/dx`, and returns **the midpoint of
that pair**. The sample points are the airfoil patch's face centres, which are
fixed by the mesh. The reported shock position is therefore not a continuous
measurement: it can only take one of a small, fixed set of values.

**The alphabet, read off the primary run's own sampled output.**
`primary_M0.8_a1.25_Re6e6/postProcessing/surfaceP/2000/p_airfoil.raw`
contains 32 upper-surface face centres, of which **21** lie in the detector's
`[0.05, 0.95]` search window — so the detector has at most **20** representable
outputs on the whole upper surface. In the region of interest:

| Adjacent face centres | Representable output | Pitch to previous |
|---|---|---|
| 0.439836 → 0.528676 | 0.484256075 | — |
| 0.528676 → 0.583477 | **0.556076460** | 0.071820 |
| 0.583477 → 0.633404 | **0.608440365** | **0.052364** |
| 0.633404 → 0.678894 | 0.656148840 | 0.047708 |
| 0.678894 → 0.720343 | 0.699618645 | 0.043470 |

Across all 280 ledger runs the detector emitted exactly **8** distinct
upper-surface values (0.484256075 ×55, 0.556076460 ×140, 0.608440365 ×62,
0.656148840 ×16, 0.699618645 ×4, 0.775322550 ×1, 0.808213945 ×1,
0.890395705 ×1). Eight values from 280 solves at 280 different flow
conditions is the quantisation, not the physics.

**Why the gate claim fails.** The record claims the CFD shock at x/c=0.556
sits `+0.044` chord upstream of the inviscid reference at x/c ~ 0.60, and
reads that displacement as the expected viscous shock/boundary-layer shift.
But:

1. `0.60 − 0.556076460 = 0.043924` chord. The pitch between 0.556076460 and
   the next representable value is `0.052364` chord. **The claimed deviation
   is smaller than one detector increment.** The detector cannot express a
   0.044-chord displacement; it can only express 0 increments or 1.
2. The adjacent representable value, **0.608440365, sits 0.008440 chord from
   the reference** — i.e. essentially *on* it. There is no representable value
   between "on the reference" and "0.044 upstream of it". The two competing
   physical readings are adjacent lattice levels.
3. The neighbourhood does not settle it. Of the 18 ledger runs in
   M ∈ [0.78, 0.82], alpha ∈ [0.8, 1.8], **11 report 0.608440365 and 7 report
   0.556076460**. Tightening to M ∈ [0.79, 0.81], alpha ∈ [0.9, 1.6] gives 6
   runs split **3 / 3**. Which of the two values comes out flips on flow
   changes far too small to move a real shock by half a chord-twentieth.
4. The reference itself is soft. `PHYSICS_FAMILIES.md:104-107` and
   `transonic_airfoil.py:22-23` both record that no citable digitized dataset
   was retained for this benchmark; the reference is a literature-recalled
   "x/c ~ 0.60", stated to two significant figures with no retained citation.
   A 0.044-chord deviation cannot be asserted against a reference known only
   to ~0.6.

**Withdrawn.** The directional claim — that the CFD shock "sits slightly
*upstream* of the inviscid 0.60, the direction a real shock/turbulent-
boundary-layer interaction is expected to shift it" — **is withdrawn**. It
rests on a difference below one detector increment, against a reference with
no retained citation. It is a quantisation artifact of the same species as the
F7a metric artifact retracted this session. F2 does **not** demonstrate the
viscous upstream shift and must not be narrated as doing so.

**Requalified, not deleted.** What survives is weaker and true: a genuine
supersonic recompression is present on the suction surface, and the detector
places it at x/c = 0.556 ± one increment (≈ 0.05 chord) at this condition,
which is **consistent with the inviscid ~0.60 benchmark to within the
detector's own resolution**. That is a real physics result — the solve
produces a shock in about the right place — and it is all this gate supports.

**A caveat the record must carry.** The stated pass band is 0.35–0.60 chord.
The value obtained, 0.556076460, is inside it; the *adjacent representable
value*, 0.608440365, is outside it. The banded PASS is therefore decided by a
single quantisation level. It should be read as "not contradicted" rather than
as a demonstration. Making the gate mean more than that requires a detector
that does not snap to mesh nodes — e.g. a parabolic or gradient-weighted
sub-cell fit to the `dCp/dx` peak — and/or a finer surface discretisation than
the coarse 3584-cell rung. Neither was done here and neither is claimed.

---

## 4. Lessons recorded

Both defects generalise, and both are now in `LESSONS.md`:

- **L-27** — a gate run performed outside the batch ledger must retain its own
  artifact, and its absence from the ledger is not evidence it never happened.
  Covers both halves of §2: the record's failure to keep the artifact, and the
  audit's leap from "not in the ledger" to "fabricated."
- **L-28** — a detector that snaps to mesh nodes cannot report a deviation
  smaller than its own increment. Covers §3, with the visible tell: a
  continuous quantity returning 8 distinct values across 280 varied runs is
  quantised, not converged. Count the distinct values before subtracting two of
  them.

---

## 5. What changed in the other records

- `demo-output/website/campaign/CAMPAIGN_STATUS.md`, F2 section and summary
  table: the primary-case numbers now cite the retained reproduction rather
  than standing bare; the "+0.044 upstream" deviation claim is withdrawn and
  replaced with the resolution-limited statement; the detector's ±1-increment
  limit is stated in the gate line.
- `demo-output/website/mega-batch/PHYSICS_FAMILIES.md`, Family 2 "VALIDATION
  GATE RESULT" block: same two corrections, plus a pointer to this document
  and to the retained evidence.
- `sdk/workflows/transonic_airfoil.py` is **not** changed. The defect is in
  what the record concluded from the detector, not in the detector's code, and
  the module is held by another agent this session. If the gate is ever to
  resolve a sub-increment shift, the sub-cell fit described above is the
  change to make, and it is an act/workflow decision, not a records one.
