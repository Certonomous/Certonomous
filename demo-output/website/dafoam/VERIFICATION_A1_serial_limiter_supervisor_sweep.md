# Supervisor sweep of the R7 serial-limiter finding: the 92.8% survives the one attack that could have killed it — the FD legs' own one-sided slopes, mined free from the logs, bracket a positive derivative where the adjoint says negative

**2026-08-07, adversarial verification of the R7 acquisition-arm record in
`DEFECT_ROBUSTNESS_mesh_and_setup.md` (pre-registration commits 0263d950 /
aa7fcddc, results commit 85dfbe68, docket-close commit d63b3212) and of the
claim it feeds upstream: on A1 (4,032-cell structured NACA0012,
`freestreamVelocity` farfield), `cellLimited Gauss linear 1` feeding
`linearUpwind` breaks the SERIAL adjoint at CD/shape 92.8% vs its own
step-stable FD, identically at np=1 and np=4-scotch (3.9e-04 analytic
invariance), curable by the one-word lever `limited` -> `default` (0.121%).**
Posture: every claim is wrong until it survives. Method: byte-level config
diffs, independent log re-extraction and numpy recomputation, commit/ledger
timestamp reconciliation — **no solver was run; this sweep's ledgered solver
cost is 0.00 core-min.** The decisive check (axis 3) that could have gutted
the finding was obtained at zero cost by mining the per-leg converged CD
values the FD primals already printed. No upstream file was modified.

**Verdict up front: all five axes CONFIRMED.** Two findings are named against
the record, neither fatal: (F1) the record's step-stability test (R7f1) is,
by itself, logically insufficient to exclude the classic limiter-kink FD
artifact — a symmetric kink at the base point leaves a central difference
step-invariant — and the record nowhere runs the one-sided-slope check that
closes this hole, though the data to run it was already in its own logs;
this sweep ran it, and the finding SURVIVES decisively (below). (F2) the
"no acquisition" verdict is scored on the decomposition-invariance
instrument adopted in Amendment 6 AFTER R7's numbers were in hand — the
record discloses this ("measured before this amendment was written", "with
the FD-band caveat disclosed"), and the inference is forced (a 3.9e-04
analytic shift cannot support the >= 2% acquisition clause under any
registered band), but the instrument choice is post-hoc relative to the R7
registration and should be named as such, not only caveated.

## Axis 1 — config audit: CONFIRMED. The arm is the established clean case plus exactly two `fvSchemes` lines; the R7f2 lever is literally one word

`diff -r` of `a1lim_np1/` against the established clean arm `a1fs_np1/`
(the R1 case that measured 0.043%), excluding only solution-output
directories (`242/` vs `251/`), `reports/`, and coloring binaries: **the
single differing input file is `system/fvSchemes`**, and the diff is exactly
the two disclosed lines —

- `gradSchemes` gains `limited  cellLimited Gauss linear 1;`
- `div(phi,U)`: `bounded Gauss linearUpwindV grad(U);` -> `bounded Gauss
  linearUpwind limited;`

`runScript.py` is byte-identical, `0.orig/U` carries `freestreamVelocity`
(`freestreamValue uniform (9.959800351 0.895754972 0)`) in both, and the
driver log asserts `patchVelocity-count: 0`. So relative to the established
A1+freestream case the change is {scheme pair}; the BC edit was inherited
from R1 unchanged, exactly as Amendment 5 claims. The disclosed
`linearUpwindV` -> `linearUpwind` family swap is real and is carried by
R7f2 (which retains it and is clean), so the exoneration logic holds.

The other three arms, byte-audited the same way against `a1lim_np1`:

- `a1lim_np4scotch`: `fvSchemes` identical, `runScript.py` identical; the
  log reads `Decomposition method scotch [4]`.
- `a1lim_np1_h3e3` (R7f1): ONE changed line in `runScript.py` — `step=1e-3`
  -> `step=3e-3` in the `check_totals` call; `fvSchemes` identical.
- `a1limdef_np1` (R7f2): ONE changed word in `system/fvSchemes` —
  `linearUpwind limited;` -> `linearUpwind default;`; `runScript.py`
  identical. **The one-word claim is literally true at byte level.**

Patched IDWarp is stamped in every log (`IDWARP_IMPORTED_FROM:
/patch/idwarp/...`).

## Axis 2 — number re-extraction: CONFIRMED. Every headline number reproduces from the raw logs under independent parsing and arithmetic

From the four logs at `/home/ubuntu/certonomous-runs/W4-defect-robustness/`,
re-extracted with this sweep's own grep/numpy (all values are the OpenMDAO
vector-relative convention ||Jan−Jfd||/||Jfd||, the same convention every
number in the record uses):

| claim | record | this sweep | source line |
|---|---|---|---|
| np=1 CD/shape rel. err | 92.8% | 9.284586e-01, recomputed from raw vectors 0.928459 | `a1lim_np1.log:2319` |
| np=4 CD/shape rel. err | 92.8% | 9.280696e-01 | `a1lim_np4scotch.log:2669` |
| np=1 CL/shape rel. err | 7.86% | 7.864249e-02 | `a1lim_np1.log:2334` |
| sign-flipped component | one CD component | exactly one: **index 6 of 8** (analytic −0.02591213, FD +0.00849673); no other component flips | raw Jfor/Jfd vectors |
| analytic np1-vs-np4 invariance | 3.9e-04 vector-relative | 3.9446e-04; per-component max 0.197%, median 0.040% (record: 0.20% / 0.04%) | recomputed |
| FD columns np1-vs-np4 | 1e-6 apart | max abs component diff 1.9e-07, vector-relative 4.3e-06 | recomputed |
| CL analytic np1-vs-np4 | 3.8e-05 | (4.919616−4.919431)/4.919616 = 3.76e-05 | log magnitudes |
| Krylov counts | 95/96 vs 96/97, reason 2 | np1: `Total iterations: 95 / 96, PetscConvergedReason: 2`; np4: 96/97 reason 2 | `:637/:646`, `:822/:831` |
| R7f1 FD step shift | 2.10% vector, max comp 15.1% | 2.099%; per-component max 15.14%, at component 6 | recomputed |
| R7f1 analytic unchanged | byte-identical | Jfor vectors identical at every printed digit; magnitude 1.066449e-01 both | both logs |
| 44x-too-small ratio | 44x | 0.928 / 0.02099 = 44.2 | recomputed |
| R7f2 rel. err | 0.121% | 1.213592e-03; KSP 32/32 reason 2; CL 1.8e-04 | `a1limdef_np1.log:2319` |

The np=4 log prints identical Jfor/Jfd on all four MPI ranks — the 92.8% is
not a rank-local artifact of the print path.

## Axis 3 — the FD instrument at the component it condemns: CONFIRMED, and the kink hypothesis is now CLOSED, not merely disfavoured

This is the axis that could have gutted the finding, so it got the full
treatment. Three layers:

**(a) The FD legs' primals are as claimed.** Each of the four logs contains
exactly 17 primal solves (1 baseline + 8 DVs x central ±h), and **all 17 in
all four logs print `Minimal residual ... satisfied the prescribed tolerance
1e-08`**; the worst final residual across every leg of every log is
9.99e-09, and no solve exits on the iteration cap. The FD reference is not
polluted by unconverged primals.

**(b) The central-difference arithmetic is right.** Each FD primal leg
prints its own converged CD. Mining those 17 values per log and rebuilding
the central differences under the leg ordering (comp i: +h then −h)
reproduces the log's printed Jfd vector to **max 4.7e-09 abs** at both
h=1e-3 and h=3e-3 — the ordering hypothesis, the step, and OpenMDAO's
arithmetic all check.

**(c) The kink question, answered with the record's own data.** The classic
FD trap for branchy schemes: if the limiter's min/max selection flips
between the +h and −h legs, central FD measures a kink-average, not a
slope — and a symmetric kink at the base point is STEP-INVARIANT under
central differencing, so the record's R7f1 two-step stability check cannot,
by itself, exclude it (finding F1: the record registered the kink hypothesis
in Amendment 6 and tested it only via step-stability). The closing check is
free: the same mined per-leg CD values give the **one-sided slopes**
(CD(+h)−CD(0))/h and (CD(0)−CD(−h))/h, which a kink at the base point would
split apart. Result, per component, h=1e-3:

| comp | central FD | forward | backward | fwd/bwd asym | analytic |
|---|---|---|---|---|---|
| 0 | −0.009054 | −0.008926 | −0.009182 | 2.8% | **−0.034900** |
| 1 | −0.020342 | −0.019338 | −0.021345 | 9.9% | **−0.037237** |
| 4 | +0.037311 | +0.037465 | +0.037158 | 0.8% | **+0.061443** |
| 5 | +0.040489 | +0.040656 | +0.040322 | 0.8% | **+0.064415** |
| **6** | +0.008497 | **+0.009660** | **+0.007334** | 27.4% | **−0.025912** |

(h=3e-3 asymmetries: comp 6 grows to 91%, all others <= 20%.) Read:

- On the components carrying most of the 92.8% gap (0, 1, 4, 5) the
  one-sided slopes agree to within 10% — the function is locally SMOOTH
  there at the FD scale, no kink to blame, and the analytic still misses by
  65–285%.
- Component 6 — the sign-flipped one — IS visibly branchy (27% asymmetry at
  1e-3, growing with h: real limiter chatter). But **both one-sided slopes
  are positive at both steps** (+0.0053 to +0.0143 across all four
  secants), while the analytic is −0.0259: the analytic lies OUTSIDE the
  [backward, forward] bracket, on the wrong side of zero, at 3x the
  magnitude. No branch selection available to the FD produces a negative
  slope here. The kink cannot rescue the adjoint even on its own worst
  component.
- Triangulation, also free: the limited case's FD vector lies at cosine
  **0.994** to the unlimited case's analytic (which R7f2 validated against
  its own FD at 0.121%), while the limited analytic sits at cosine 0.90 to
  its own FD. Three of the four instruments (limited FD, unlimited FD,
  unlimited adjoint) agree with each other; the limited serial adjoint is
  alone.

**The FD-kink answer: the FD is measuring a slope, not a kink; the 92.8% is
the analytic's.** No discriminating solve was needed — the check came out of
the existing logs at zero core-min, and the record (or its successor) should
adopt the one-sided-slope reconstruction as the standard closing move for
this symptom class: it is strictly stronger than a second step size and
costs nothing.

## Axis 4 — pre-registration: CONFIRMED, with one named caveat (F2)

**Text integrity.** Amendment 5 as committed in 0263d950 is byte-identical
to Amendment 5 in the results commit 85dfbe68 (all 61 lines); Amendment 6 as
committed in aa7fcddc is byte-identical to its final form. Nothing was
reworded after measurement. Neither pre-commit contains any R7/R7f results
section.

**Ordering.** Commit times vs run windows (ledger end-times cross-checked
against log mtimes to the second; starts reconstructed as end − wall):

| event | time (UTC) |
|---|---|
| Amendment 5 commit 0263d950 | 20:12:55 |
| `a1lim_np1` runs | ~20:13:02 – 20:16:14 |
| `a1lim_np4scotch` runs | ~20:16:27 – 20:17:39 |
| Amendment 6 commit aa7fcddc | 20:20:50 |
| `a1lim_np1_h3e3` runs | ~20:20:58 – 20:22:47 |
| `a1limdef_np1` runs | ~20:22:48 – 20:24:10 |
| results commit 85dfbe68 | 20:29:00 |

Both pre-commits genuinely precede their arms — by 7 and 8 seconds
respectively. Tight, but ordered, and the tightness is consistent with a
commit-then-launch pipeline rather than backfill (backfilled registration
would have no reason to land seconds before the run).

**Scoring against registered wording.** R7's escape clause ("np=1 control
dirty -> reported unmeasurable, not scored") fired and was followed. R7f1's
three bands (>= 20% kink / <= 2% loud alternative / 2–20% middle NOT HELD)
were applied as written: 2.10% lands in the middle band by 0.10 points and
is scored NOT HELD, with the loud alternative claimed only "in substance" —
honest. R7f2's <= 0.5% band HELD at 0.121%. **Caveat F2:** the acquisition
verdict ("the defect did NOT acquire") is scored on the
decomposition-invariance instrument, which Amendment 6 adopted with the R7
numbers already in hand; the record discloses the sequence, the instrument
echoes R1's registered clause-(ii) subclause, and no registered band could
read a 3.9e-04 shift as acquisition — but strictly, that verdict's
instrument is post-hoc and the record should say the word.

## Axis 5 — ledger: CONFIRMED

`ledger_r7.txt`: four lines, all rc=0, all `cpus_cap=2`; re-sum 6.40 + 2.40
+ 3.63 + 2.73 = **15.16 core-min** exactly as reported, against the 30 cap
(docket estimate 25). Wall x cap arithmetic checks per line (192s, 72s,
109s, 82s at 2 cpus). The audited `ledger.txt` still holds exactly 21 `==`
lines and now ends with the audit-separation pointer line naming
`ledger_r7.txt` and this docket, per the previous sweep's request — the R7
session is charged nowhere in the audited 21. One internal nit, not an
error: Amendment 6's in-text running-total ("8.80 of the 30 cap") was a
projection written before the R7f arms ran; the results-section ledger
paragraph carries the true 15.16.

## Changes made by this sweep

None to any upstream file. This report is the only file added. Named for
the record's next revision: (F1) adopt the one-sided-slope reconstruction
(free, from the FD legs' printed CD values) as the registered closing check
for the kink symptom class — R7f1-style step-stability alone does not
exclude a symmetric kink; (F2) label the acquisition verdict's
decomposition-invariance instrument as post-hoc-adopted, not merely
caveated.

Sweep cost: **0.00 solver core-min** (byte diffs, log mining, offline
numpy). The one running container observed at sweep start
(`s1re_fd_5491_minus`, S1's work) was left untouched; no compute was
contended.
