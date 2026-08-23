# A3 ONERA M6, sweep rung 1 (21,840 cells) — the patched-IDWarp column at np=4: PRE-REGISTRATION

**Filed 2026-08-23, dafoam lane, BEFORE any arm of this item was launched and before any run
directory named in this file existed.** Predictions, acceptance bands, gates, caps and falsifiers
below are committed first; `RESULTS.md` is written afterwards and does not revise this file.
Departures discovered after this commit land as dated amendments appended at the foot, never by
editing the text above them. **Nothing is filed, sent, uploaded, posted or pushed. Filing stays
NOT APPROVED and is Sanaa's alone.**

**Companion item:** `../rung3_patched_idwarp_np4/PREREGISTRATION.md`, the same column at sweep
rung 3. The two are separate items with separate budgets, separate ceilings and separate commits.

---

## 1. Question, and why this rung is not a repeat of rung 2

`LADDER_A_STATUS.md:193` row **12b** reads **PENDING — NOT MEASURED** for *"A3 rungs 1, 3 and the
399,360 campaign"* in the PATCHED column: *"rung 2 is now measured; no patched arm exists at any
other A3 size."* This item buys exactly one cell of that column: **sweep rung 1, 21,840 cells,
np = 4.**

The rung-2 patched arm produced the ladder's first measured A/B pair in which **the rotation patch
degrades a gradient the shipped toolchain already had right**
(`../rung2_patched_idwarp_np4/RESULTS.md` headline and §4; N-D18; D462):

| component | shipped-equiv analytic | patched analytic | analytic moved | FD(h), identical both images | rel err shipped | rel err patched |
|---|---|---|---|---|---|---|
| `patchV[1]` | `7.90292882576689e-03` | `7.90292882576689e-03` | **0** | `7.90232345e-03` | 0.0077% | **0.0077%** |
| `twist[1]` | `1.80386731629814e-03` | `1.79204040523569e-03` | 0.6556% | `1.80882369e-03` | 0.2740% | **0.9279%** (3.39×) |
| `shape[115]` | `-1.30055677346768e-01` | `-1.29871804107421e-01` | 0.1414% | `-1.30078078e-01` | 0.0172% | **0.1586%** (9.2084×) |

**Whether that degradation is a property of the patch or a property of rung 2 is the whole
question, and this rung can answer it — because at rung 1 the shipped analytic sits on the OTHER
SIDE of the FD reference.** Read the two rungs' signed shipped errors, `analytic − FD(h)`:

| rung | shipped analytic | FD(h) | shipped error `analytic − FD` | sign |
|---|---|---|---|---|
| 2, 42,120 cells | `-1.30055677346768e-01` | `-1.30078077925157e-01` | **`+2.2401e-05`** | **positive** |
| 1, 21,840 cells | `-1.24189675803981e-01` | `-1.23048666802475e-01` | **`-1.141009e-03`** | **negative** |

Sources, read at the line: rung-2 values `../rung2_patched_idwarp_np4/RESULTS.md:169-171` and
`Correction 1`; rung-1 values `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/fd3_run.log:4910`
(`FD3 shape[115]: adjoint -1.24189676e-01  FD(h) -1.23048667e-01`) with the full-precision analytic
at `:885` and the full-precision FD at `:4196`.

At rung 2 the patch moved the analytic **toward zero** on both warp-crossing components — and
because the shipped error there was positive, moving toward zero moved it **away** from FD. At
rung 1 the shipped error is negative. **If the patch's analytic delta has the same sign at rung 1,
the identical patch will move rung 1's gradient TOWARD FD — i.e. it will look like an improvement
at rung 1 and a degradation at rung 2, from one unchanged shared library.** That is prediction
**R1-P8b**, and it is registered here so that either outcome is a scored prediction and neither can
be read favourably after the fact.

The claim that would follow if R1-P8b lands is the one Sanaa's toolchain-adoption question actually
needs: **the patch applies a consistent shift to A3's analytic gradient, and the sign of the
apparent "improvement" is set by which side of FD the shipped analytic happened to sit — so
"the patch made it better/worse" is not a property of the patch at all on this case.** If R1-P8b
misses, the degradation looks like a genuine property of the patch on A3 and the adoption question
tightens.

**What this rung cannot do, said before it runs:** at rung 1 only **two** of four FD components were
ever step-consistent, so only **one** warp-crossing component (`shape[115]`) can carry a verdict.
§4 and §9 state this at the number rather than at the foot.

## 2. Case and configuration

| item | value | source, read at the line |
|---|---|---|
| archived case | `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/` — **read-only to this item; copied, never run in** | `../grading_confirmation/RESULTS.md:92` |
| **run root (new, does not exist at filing)** | `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/` — arms in `patched/`, `shipped/`, `wrongstep/` | this file |
| mesh | **21,840 cells** (`decompose_opt5_onera_n15_21840.log`, per-processor counts summing to 21,840), pyHyp **N=15** layers on the 3×-coarsened M6 surface | this file, §3 departure 3 |
| mesh identity | `sha256(constant/polyMesh/points.gz)` = **`695b729da801ed2f95723877e34702ee65ce37a87fddbddacb3f3b4ce38f0a7f`** | computed 2026-08-23 from the archived case; **see §3 departure 3 — rung 1 has NO birth certificate** |
| solver | `DARhoSimpleCFoam`, `primalMinResTol 1e-8`, `primalMinResTolDiff 1e4` | `A3-onera-m6-sweep-n15_21840/runScript_fd3.py`; `../../A3_FD3_PREREGISTRATION.md` §1 |
| adjoint | `transonicPCOption 1`, stock ILU(0) (`pcFillLevel 0`), `jacMatReOrdering natural`, `gmresRestart 200`, **`gmresMaxIters` NOT set** (DAFoam default 1000), `DAFOAM_SUBPC_TYPE` **unset** | `runScript_fd3.py:105`; the absent `gmresMaxIters` is a real difference from rung 2 and is §3 departure 4 |
| task | `-task fd3` — 1 cold primal, 1 CD adjoint, **four hand-listed components**, central FD at h=1e-2 and 2h=2e-2, repeat-baseline drift | `runScript_fd3.py:310` |
| **components** | **`patchV[1]`, `twist[1]`, `shape[5]`, `shape[115]`** — hand-listed at rung 1, NOT runtime `argmax` | `runScript_fd3.py:310`; §3 departure 5 |
| FD convention | central, `step_calc` abs, **h = 1e-2 / 2h = 2e-2** — the sizes that cleared **this rung's own** measured floor, see §5 | `../grading_confirmation/RESULTS.md:119-125` |
| **np / decomposition** | **np = 4**, `scotch`, 4 subdomains — the same np as the shipped row, because an FD reference is never carried across np (`DAFOAM_CHARTER.md` §5) | `A3-onera-m6-sweep-n15_21840/decompose_opt5_onera_n15_21840.log` |
| colouring cache | `dRdWColoring_4.bin`, md5 **`a6919b8494a78f09c9c876e0d21686e2`**, **1233 colours** — carried into every staged copy and READ, never rebuilt | archived case; `fd3_run.log:844,848` |
| container caps | `--cpus=4 --memory=12g`, `--rm`, foreground under `timeout`, `-x PYTHONPATH` | this file, §7 |
| image, PATCHED arm | **`dafoam-idwarp-rot:v1`**, image ID `2927768a16ac`, `libidwarp.so` md5 **`85f59e87253e0a71a813f64ca6e4c425`** — **identity is the hash, never the version string** | `../../patched_build/idwarp_rot/BUILD.md` §2, §3 |
| image, SHIPPED arm | **`dafoam/opt-packages:latest`**, image ID `9d45679d55fd`, stock `libidwarp.so` md5 **`f0fcb488e0e98156575cd19548e91663`** | image ID read from `docker images` 2026-08-23; md5 cited from `../rung2_patched_idwarp_np4/PREREGISTRATION.md:49` |
| image, archived ‡ row | `dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE` unset — **SHIPPED-equivalent, not the shipped image** | `../grading_confirmation/RESULTS.md:94-96` |

### Why the literal shipped image is run here when rung 2 declined it

Rung 2 declined its shipped twin because the archived rung-2 logs already carried the raw
per-component arrays **and** the full 120-component analytic `CD wrt dvs.shape` row, at matched np
(`../rung2_patched_idwarp_np4/PREREGISTRATION.md` §3 departure 1, restated at A2.2). **That
reasoning does not transfer to rung 1, and the reason is a fact on disk:**

* The rung-1 archived logs carry the four hand-listed components' analytic values
  (`fd3_run.log:882-885`) — but **there is no `print(totals)` anywhere in the rung-1 tree**.
  `tpc1_computetotals.log` was searched for it and does not contain one. **The full 120-component
  shipped analytic shape row does not exist at rung 1.** Without a fresh shipped arm, the
  analytic-vs-analytic patch-effect measurement (R1-P10, the rung-2 P9 analogue and the cleanest
  cross-rung comparison there is) is **unmeasurable**.
* Running `dafoam/opt-packages:latest` also **closes at rung 1 the ‡ gap rung 2 could not close**
  (`../rung2_patched_idwarp_np4/RESULTS.md:352-355`, limit 5: *"this item did not run
  `dafoam/opt-packages:latest` at rung 2"*). Both images in this item are built FROM
  `dafoam/opt-packages:latest`, so the FD-invariance control (R1-P5) and the adjoint-identity
  control (R1-P4) are measured between the literal shipped image and the patched image — strictly
  stronger than rung 2's comparison against `dafoam-subpclu:v1`.
* It removes every tolerance and script confound: both arms run **the same `runScript_fd3p.py` at
  the same `primalMinResTol 1e-8`**, so the only difference between the two analytic vectors is one
  shared library. Rung 2 had to measure a `1e-6` vs `1e-8` confound away after the fact
  (`../rung2_patched_idwarp_np4/RESULTS.md:194-197`).

**Three rows, never merged:** archived ‡ (cited), fresh literal-SHIPPED (measured), PATCHED
(measured). Per R11 a patched number never moves a shipped grade
(`../../FAMILY_SUPERVISION_GUIDELINES.md` §3.4).

## 3. Departures, each disclosed with its reason

1. **The `dRdWColoring_4.bin` cache is carried into every staged copy and NOT deleted.**
   `../../FAMILY_SUPERVISION_GUIDELINES.md` §8 item 1: *"Partition and coloring caches stay
   untouched."* The cold-start hazard the staging rule exists for is pyDAFoam writing primal end
   state into time-0 — a **field-state** hazard, not a colouring one — and it is closed by
   departure 2 and prediction **R1-P2**. Carrying the cache also keeps all three arms on the
   identical colouring the shipped row read, which is the comparability this item exists for.
   **The departure is now GUARDED, not merely asserted:** `coloring_guard.sh:55` kills any arm that
   prints `Calculating dRdW Coloring`, and `:63` kills any arm whose colour count is not 1233.
2. **Cold start proved, not assumed.** Each staged copy is made from the archived case with
   `processor*`, `_prior_state_backup_*`, `reports/`, `mphys.html`, `dump_*.dat*` and every `*.log`
   excluded. `diff -rq 0 0.orig` over the archived case was run before filing and returned **no
   differences** — the serial `0/` is byte-identical to `0.orig` (pyDAFoam writes state into
   `processor*/0`, not the serial `0/`). `decomposePar -force` runs inside each copy, and **R1-P2**
   asserts this rung's cold-from-uniform signature in the log. A guard refuses any staged tree in
   which a `processor*` directory or a non-`0` time directory already exists.
3. **Rung 1 has no mesh birth certificate, and this item does not manufacture one.**
   `A3-onera-m6-sweep-n15_21840/constant/` contains `polyMesh`, `thermophysicalProperties` and
   `turbulenceProperties` — **no `birth_certificate.json`**, unlike rungs 2 and 3. The mesh identity
   registered in §2 is the `points.gz` sha256, computed by this lane on 2026-08-23 under the same
   convention the rung-3 certificate uses (verified: hashing `A3-rung2-n28-tpc1/constant/polyMesh/points.gz`
   reproduces the recorded `7eb9866e…`, and hashing the rung-3 file reproduces its certificate's
   `cf35cf14…`). **A hash is not a quality verdict.** No `checkMesh` record for rung 1 was found on
   disk and none is asserted; §9 item 6 carries this as a stated limit. The staging step re-asserts
   the hash before launch and refuses on a mismatch.
4. **`gmresMaxIters` is left unset (DAFoam default 1000), because that is the shipped rung-1
   configuration.** Rung 2 raised it to 2000 (`runScript_fd3.py:106` there) after its CL solve hit
   the 1000 cap. Rung 1's CD adjoint converged in **368** iterations, so the cap never bound, and
   changing it would be changing a numeric option to no purpose. Registered consequence: if the
   patched adjoint were to need more than 1000 iterations it would return `reason -3` at the cap —
   which **R1-P4**'s falsifier treats as a stop-and-report, not as a failure of the patch.
5. **The components are rung 1's hand-listed four, not a runtime `argmax`, and the sequence is not
   changed.** Rung 2's script picks components at runtime; rung 1's does not
   (`runScript_fd3.py:310`, `comps = [("patchV", 1), ("twist", 1), ("shape", 5), ("shape", 115)]`).
   **This is deliberate and it is the only choice that preserves the FD control.** The FD loop warm-
   restarts each perturbed primal from its neighbour's converged state
   (`../../A3_FD3_PREREGISTRATION.md` §3, disclosed there), so **inserting, removing or reordering a
   component or a step changes the warm-start chain and can move FD digits that must not move.**
   Adding a third step to strengthen the plateau read would therefore break the bit-identity control
   R1-P5 depends on, and it is **declined by name** rather than silently omitted; §5 registers the
   plateau limitation instead, and §9 item 1 carries it.
   *A log-only line printing the runtime `argmax|g|` index per group is added (D2b below) so a moved
   argmax is visible, without changing which components are graded.*
6. **`runScript_fd3.py` → `runScript_fd3p.py`, four insertions, all log-only or new-branch, all
   asserted by `diff` before launch and the `diff` pasted into `RESULTS.md`:**
   * **(D1)** a provenance stamp block after the imports, printed **per MPI rank**: rank,
     `idwarp.__file__`, the md5 of the `libidwarp.so` adjacent to the loaded package, and the
     `idwarp` version string. Log-only, executes before any numeric call. Reason:
     `../../patched_build/idwarp_rot/BUILD.md` §6 warns Open MPI may not forward the parent
     environment to every rank, and a per-rank hash is the only thing that closes it — the version
     string is identical across both stacks and discriminates nothing (BUILD.md §2).
   * **(D2)** one added line, `log0(repr(totals))`, immediately after `compute_totals`. Log-only.
     It is what makes **R1-P10** measurable at all, on both arms.
   * **(D2b)** one added line per DV group printing the runtime `argmax|g|` index and value.
     Log-only; changes nothing about which components are perturbed or graded (departure 5).
   * **(D3)** a new `fd1wrong` task branch for the trivial baseline (§6, arm R1-C). It touches no
     existing branch. Carried across from the rung-2 script, where it ran and produced its
     registered refusal.
   **No numeric option, DV set, scheme, tolerance, step or component ordering in the `fd3` branch is
   changed.** The identical `runScript_fd3p.py` runs on both the patched and the shipped arm.
7. **`-x PYTHONPATH` is added to the `mpirun` line** on all arms, per `BUILD.md` §6.

Everything else — mesh, `constant/`, `system/`, `FFD/`, `daOptions`, `meshOptions`, DV set, FD
steps, `decomposeParDict`, the colouring cache, ranks — is byte-identical to the archived rung-1
arm.

## 4. Grading bands and the verdict instrument

**Aggregate band**, cited not invented — read at the line, `../../A_stepsize_study.md:92-94`:
*"Bands: **PASS ≤5%** with zero flagged components; **CONDITIONAL 5-15%**, requires a per-component
breakdown before grading; **>15% or any flagged component → FAIL pending investigation**, regardless
of the aggregate percentage."*

> **An open conflict between two rules on record, named here rather than quietly resolved.** The
> aggregate band above says *any flagged component ⇒ FAIL*. The per-component rule below says a
> flagged component is **NOT A RESULT** and the arm still PASSes on ≥ 2 evaluable components. **At
> rung 1 these two rules give different answers**, because `twist[1]` and `shape[5]` are flagged
> (§5). **The archived rung-1 row was graded PASS under the per-component rule**
> (`../grading_confirmation/RESULTS.md:134-136`), and **this item uses the same instrument the
> archived row used, so that all three rows are graded alike** — that is the whole reason for
> choosing it, not a preference for the friendlier answer. **Choosing between the two rules retires
> or reinterprets a gate threshold and is therefore NOT a lane's call** (CLAUDE.md, *Reserved to
> Sanaa*). It is **referred to the supervisor and to verification, unruled**, and `RESULTS.md` will
> print **both** readings side by side: the per-component verdict, and the aggregate band's
> `FAIL pending investigation` reading. Registering the conflict before the run is what stops the
> reading being chosen to fit the answer.

**This rung's stricter pre-registered per-component rule**, inherited unchanged from
`../../A3_FD3_PREREGISTRATION.md` §4 so the archived row and the two new rows are graded by one
instrument:

* **Evaluability gate:** a component is evaluable only if `|CD(+h) − CD(−h)| > 10 ×` the measured
  repeat-baseline drift **of that arm**.
* **Step-consistency gate:** `|FD(h) − FD(2h)| / |FD(h)| < 1%`.
* **Per-component verdict on evaluable, step-consistent components:** PASS < 5%, CONDITIONAL
  5–15%, FAIL > 15% or sign flip.
* **Arm verdict:** PASS = all evaluable-and-step-consistent components PASS with ≥ 2 such;
  CONDITIONAL = one at 5–15% with none failing; FAIL = any FAIL; **NOT EVALUABLE** = fewer than 2,
  reported with the noise numbers and carrying no verdict either way.

**The flagged components are named here, before the run, not discovered afterwards.** At rung 1 the
shipped arm measured step-consistency **0.4573% / 5.2887% / 8.2023% / 0.2043%** for `patchV[1]`,
`twist[1]`, `shape[5]`, `shape[115]` (`fd3_run.log:4907-4910`). Against the 1% gate, **`twist[1]`
and `shape[5]` fail it and are FLAGGED BY NAME**: they carry **NOT A RESULT** in the FD column on
every arm of this item, are **excluded by name from any aggregate quoted as agreement**
(`DAFOAM_CHARTER.md` §3), and are **never rescued** by any later reading. Their analytic values are
still reported, as analytic-vs-analytic deltas with no FD in them.

**So the verdict-carrying set at rung 1 is `patchV[1]` and `shape[115]`, and `patchV[1]` does not
cross the mesh-warp chain.** One warp-crossing component carries this rung's FD verdict. Stated at
the headline of `RESULTS.md`, not in a footnote.

**Error convention, named at the number** (`DAFOAM_CHARTER.md` §2): the per-component figure is
`|J_an − J_fd(h)| / |J_fd(h)|`, a **per-component relative error**, not a vector norm. The **patch
effect** in R1-P10 is a **vector L2 relative difference** `‖g_patched − g_shipped‖₂ / ‖g_shipped‖₂`
between two **analytic** vectors with no FD in it. **Three different statistics; none is ever quoted
against another, and no ratio is formed from two already-rounded percentages**
(`../rung2_patched_idwarp_np4/RESULTS.md` Correction 1 — that error was made at rung 2 and is not
repeated here).

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING. No other
word grades an arm here.

## 5. The FD step ladder, and what plateau evidence actually exists at rung 1

`DAFOAM_CHARTER.md` §3 requires the step to be proved in the plateau by a sweep, run at the primal
tolerance the graded run uses, and read **per component**. **What exists at rung 1 is a two-point
sweep, and calling it a proved plateau would be a false statement.** Both points are on disk and
both are reported:

| step pair | drift (noise floor) | evaluability threshold | step-consistency `patchV[1]` / `twist[1]` / `shape[5]` / `shape[115]` | status |
|---|---|---|---|---|
| **h=1e-3, 2h=2e-3** (attempt 1) | `2.107e-06` | `2.107e-05` | **16.8666% / 25.3372% / 37.4584%** / — | **all fail the 1% gate; NOT EVALUABLE** |
| **h=1e-2, 2h=2e-2** (attempt 2) | `1.626e-06` | `1.626e-05` | **0.4573% / 5.2887% / 8.2023% / 0.2043%** | **two clear, two flagged** |

Sources, read at the line: attempt 1 `A3-onera-m6-sweep-n15_21840/fd3_run_attempt1.log:3958-3962`
(4-component `shape[115]` was added only in attempt 2); attempt 2 `fd3_run.log:4905-4910`. Both ran
at `primalMinResTol 1e-8`, the tolerance this item's graded arms use — which is the half of §3 that
a loose-tolerance sweep gets wrong.

**Registered step ladder for this item: h = 1e-2, 2h = 2e-2, unchanged from the shipped row, and no
third step is added.** The reasons are stated rather than assumed:

1. **It is the only choice that keeps the FD control alive.** §3 departure 5: the FD loop warm-
   restarts from neighbouring converged states, so a third step reorders the chain and can move the
   very digits R1-P5 requires not to move. A control that has never failed on this ladder (8/8 on
   A1, 27/27 on A5, 18/18 on A2, 9/9 on A6, 12/12 on A3 rung 2) is worth more than a third sweep
   point.
2. **It is the step the shipped row was graded at**, so the archived ‡ row, the fresh shipped row
   and the patched row are graded by one instrument on one step.
3. **A wider sweep at rung 1 is a SHIPPED-column question, not a patched-column one.** The FD
   column is a property of the primal, and the primal warp is untouched by the patch —
   `warpMesh` output is md5-identical patched vs unpatched with max|diff| = 0.0
   (`../../patched_build/idwarp_rot/BUILD.md` §3). A rung-1 plateau sweep would measure the shipped
   FD plateau and does not need the patched image at all. **It is declined by name here and left as
   a named follow-on**, not silently skipped.

**Consequence, registered:** `twist[1]` and `shape[5]` are flagged at rung 1 by §4 and stay flagged
whatever this item measures. This item does **not** claim a proved plateau at rung 1 for any
component; it claims a **measured two-point step-consistency check at a step whose floor clearance
is measured**, which is what the shipped row claimed and no more.

## 6. Arms and predictions, with bands

Three arms, run **strictly sequentially**, never more than one container from this item at a time.
Order is **PATCHED first**, deliberately: it is the cell row 12b needs, so a budget stop after one
arm still delivers what this item was dispatched for.

### Arm R1-A — PATCHED

`dafoam-idwarp-rot:v1`, np=4, `runScript_fd3p.py -task fd3`, everything else as §2.

> **R1-P1 — provenance and activity proofs. Band: exact, all five limbs.**
> **(a)** every one of the 4 ranks prints `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425` and an
> `IDWARP_IMPORTED_FROM:` path under the patched package; **(b)** the DAOption dump contains
> `transonicPCOption 1;`; **(c)** **zero** occurrences of
> `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU`; **(d)** the solver header reads
> `nProcs : 4` and 4 `processor*` directories are created; **(e)** the `idwarp` version string reads
> `2.6.2` — recorded as the demonstration that it **discriminates nothing** (`BUILD.md` §2), never
> as a check. *Reading the `decomposePar` utility's own `nProcs : 1` header instead of the solver's
> would make limb (d) say the opposite of what it says; the solver's is the one after the DAOption
> dump (`../rung2_patched_idwarp_np4/RESULTS.md:66-68`).*
> **Falsifier:** any rank reporting `f0fcb488…`, a missing or `2;` `transonicPCOption` line, or a
> sub-LU banner → **the arm is void and stops.** A run without its stamp does not count.

> **R1-P2 — cold start. Band: exact to all 16 digits.** The first
> `Time step continuity errors : sum local` printed is **`0.5969274433533561`**, this mesh's
> np=4 cold-from-uniform signature (`A3-onera-m6-sweep-n15_21840/fd3_run.log:631`; the same value
> appears in both the TPC1 and the negative-control arms, `../grading_confirmation/RESULTS.md:115-116`),
> with `initRes ≈ 1` on all six fields.
> **Falsifier:** any other value → the copy warm-started; the arm is void and stops. *Registered
> caveat, learned at rung 2: this signature is **np-specific**. It is asserted exactly here only
> because this arm runs at the matched np=4 (`../rung2_patched_idwarp_np4/RESULTS.md:264-269`,
> P16 MISS).*

> **R1-P3 — the colouring is READ, not rebuilt. Band: exact, and it is WIRED.** The log prints
> `Checking if Coloring file exists..`, `dRdWColoring_4.bin exists.`, `Reading Coloring
> dRdWColoring_4` and `dRdWTPC: 0 of 1233`, with **zero** occurrences of `Calculating dRdW
> Coloring`. Cache md5 **`a6919b8494a78f09c9c876e0d21686e2`**, asserted before launch.
> *A rebuild also prints a `Reading Coloring` line afterwards, so the discriminator is the
> **presence** of `Calculating`, never the absence of `Reading`.*
> **Stop rule, and what executes it:** `coloring_guard.sh:55` `docker kill`s the arm on a rebuild
> (exit 3) and `:63` kills it on a colour count other than 1233 (exit 5); the kill itself is
> `coloring_guard.sh:38`. Fired ⇒ the arm's warm-cache cost basis is void, the arm is **NOT A
> RESULT**, and no second budget is taken.

> **R1-P4 — the adjoint is bit-identical across images. Band: exact, all 5 printed pairs.** The
> single CD adjoint returns **`PetscConvergedReason: 2` at exactly `Total iterations: 368`**, with
> every printed `Main iteration N KSP Residual norm` matching the archived shipped row digit for
> digit (`A3-onera-m6-sweep-n15_21840/fd3_run.log:873-877`):
> `0 → 2.120880199369e-02`, `100 → 8.391224496030e-03`, `200 → 7.448585645712e-04`,
> `300 → 3.863378322670e-05`, `368 → 2.045016030763e-06`.
> **Why exact and not a band:** the IDWarp patch touches
> `src/adjoint/output{Reverse,Forward}/vectorUtils_{b,d}.f90` only (`BUILD.md` §3) — the mesh-warp
> derivative, which enters the chain **after** `Aᵀψ = −∂F/∂W` is solved. The Krylov solve cannot see
> it. This is the same identity that held 11/11 at rung 2.
> **Falsifier:** a different iteration count, a different reason, or any residual digit differing
> between arms R1-A and R1-B → the two images do **not** share a numeric path, the comparison is
> void, **stop and report**. Per `DAFOAM_CHARTER.md` §6 a `reason 2` is an **identity** check here,
> not evidence of a correct operator (L-35, L-36).

> **R1-P5 — THE CONTROL THAT MAKES THIS READABLE: the FD column must not move. Band: bit-identical,
> every printed digit, between arms R1-A and R1-B.** The primal warp is untouched by the patch and
> `warpMesh` output is md5-identical patched vs unpatched, max|diff| = 0.0 (`BUILD.md` §3;
> `../../PATCH_getRotationMatrix3d.md` §9.5). Required to match, and additionally to match the
> archived shipped row at `fd3_run.log`:
> baseline1 CD **`3.85282119087294e-02`** (`:832`); baseline2 CD **`3.85298377020484e-02`**
> (`:4904`); drift **`1.626e-06`** (`:4905`); all **sixteen** perturbed CD values; and all **eight**
> FD estimates —
> `FD(h) patchV[1] = 7.66002800367815e-03` (`:1358`), `twist[1] = 1.75500956925284e-03` (`:2304`),
> `shape[5] = 7.82812275236522e-03` (`:3250`), `shape[115] = -1.23048666802475e-01` (`:4196`);
> `FD(2h) = 7.62500231714161e-03` (`:1831`), `1.66219194764755e-03` (`:2777`),
> `8.47020820459801e-03` (`:3723`), `-1.22797279557467e-01` (`:4669`).
> **Falsifier:** any FD or baseline digit differing between R1-A and R1-B → the two arms are
> measuring different functions, nothing can be concluded from the comparison, **stop and report.**

> **R1-P6 — a by-product registered so it cannot be claimed as a discovery afterwards: does the
> LITERAL shipped image reproduce the archived ‡ row? Band: bit-identical on every printed digit**
> — analytic, FD, baselines, drift and the adjoint residual path — between arm R1-B
> (`dafoam/opt-packages:latest`) and `A3-onera-m6-sweep-n15_21840/fd3_run.log`.
> **Why it matters beyond this rung:** the ‡ label asserts that `dafoam-subpclu:v1` with the env
> unset is numerically the shipped image, and **that assertion carries every SHIPPED-equivalent row
> on the A3 sweep ladder** (`LADDER_A_STATUS.md:33-36`). It has never been tested directly at any
> A3 rung.
> **Falsifier and its disposition, fixed now:** any digit differing → **stop and report**; the ‡
> equivalence claim is escalated to the supervisor as a ladder-wide finding, **the archived-row
> comparison is void**, and the patched row is graded against **arm R1-B**, which is the literal
> shipped image and the better comparator regardless. The arm survives; only the archived
> comparison dies.

> **R1-P7 — `patchV[1]` is bit-identical between images, and it is evidence, not a gate. Band:
> exact.** `patchV` (U₀, AoA) is a boundary-condition DV and does not cross `warpDeriv`, so the
> patched analytic reads **`7.64611787804267e-03`** (`fd3_run.log:882`), unchanged, and its
> per-component relative error is therefore **0.1816%** — the shipped figure, to the digit.
> Precedent: bit-identical at A3 rung 2, at A6 row 27, and at A1 §3.
> **Reported as identity-gate IG-2 evidence and explicitly NOT gated on**
> (`../../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §5.2). A difference here is a falsifier **of
> the image**, not of the patch: it would mean the image changed something outside the warp chain →
> stop and report.

> **R1-P8 — `shape[115]`, patched: the one verdict-carrying warp-crossing component at this rung.
> Band: per-component relative error in `0.00% – 2.20%`, sign unchanged (negative), verdict
> predicted PASS.** Shipped reads **0.9273%** (`fd3_run.log:4910`).
> **How the band was derived, so it can be checked rather than trusted.** The FD reference is fixed
> at `-1.23048666802475e-01` and the shipped analytic at `-1.24189675803981e-01`. Let δ be the
> patch's analytic delta as a fraction of |g|. Rung 2 measured δ = **0.1414%** on this same
> component; the band admits two orders around it, **δ ∈ [0.01%, 3.0%]**, because the delta is the
> rotation defect's contraction with **this mesh's** `dObj/dXv` and rung 1 is a different mesh
> (N=15 vs N=28 layers). Mapping that δ range through the fixed FD reference gives relative errors
> of **0.917% (δ=0.01%) → 0.785% (δ=0.1414%) → 0.000% (δ=0.9188%, the delta that lands exactly on
> FD) → 2.100% (δ=3.0%)**. Rounded outward: **0.00% – 2.20%.** Point prediction **0.78%**.
> **Falsifier:** > 5% (CONDITIONAL) or a sign flip (FAIL) → the patch damages at rung 1 a row the
> shipped toolchain gets right, which would make rung 2's degradation a general property of the
> patch on A3 and is escalated before any regrade.

> **R1-P8b — THE DIRECTIONAL PREDICTION, and it is the one this item is bought for. Band: the
> patched `shape[115]` relative error is STRICTLY LOWER than the shipped 0.9273%, and the patched
> analytic delta is POSITIVE (magnitude decreases, i.e. moves toward zero).**
> Basis: at rung 2 the patch moved **both** warp-crossing analytic components toward zero —
> `shape[115]` `-1.30055677e-01 → -1.29871804e-01` and `twist[1]` `1.80386732e-03 → 1.79204041e-03`
> (`../rung2_patched_idwarp_np4/RESULTS.md:170-171`). At rung 1 the shipped analytic is **more**
> negative than FD, so the same signed delta moves it **toward** FD.
> **Stated honestly: this is a two-component pattern measured on ONE mesh, and it is registered as a
> prediction precisely because it is not yet a law.**
> **Named alternative, registered so no outcome can be re-read favourably:** if the patched error is
> **higher** than 0.9273%, the delta's sign reversed between rungs, R1-P8b is a **MISS**, and the
> honest reading is that the patch's effect on A3 is not a consistent signed shift — which weakens,
> not strengthens, any adoption argument. If the delta's sign holds but the magnitude overshoots
> past FD (error rising again above 0.9273% while δ > 0.9188%), that is reported as **overshoot**
> with its number, and it is a third distinct outcome, not a version of either of the first two.

> **R1-P9 — the flagged components, reported and NOT graded. Band: `twist[1]` and `shape[5]` fail
> the 1% step-consistency gate on every arm** (shipped measured 5.2887% and 8.2023%), so both carry
> **NOT A RESULT** in the FD column, on the patched arm as on the shipped one, and are **excluded by
> name** from any aggregate (`DAFOAM_CHARTER.md` §3). Their **analytic** deltas patched-vs-shipped
> are reported with no FD in them; predicted **positive (magnitude decreases) on both**, in
> `0.01% – 3.0%`, consistent with R1-P8b.
> **Named alternative:** if either becomes step-consistent under `< 1%` on both new arms, that is a
> finding about the fresh runs, is reported with its numbers, and **still does not promote the
> component to a graded row in this item** — a component rescued by a step at which it happens to
> cross is exactly what §3 of the charter forbids. Promotion needs its own pre-registration.

> **R1-P10 — the patch effect, analytic vs analytic, and the reason arm R1-B is bought. Band:
> `‖g_patched − g_shipped‖₂ / ‖g_shipped‖₂` over the full 120-component `CD wrt dvs.shape` row in
> `0.005% – 5%`.** Both vectors are analytic; no FD enters; both come from the D2 dump on arms run
> at the same tolerance with the same script.
> **Prior:** rung 2 measured **1.469586%** with **120 of 120** components differing at printed
> precision and **3 analytic sign flips** at indices 12, 13, 24 where no FD exists
> (`../rung2_patched_idwarp_np4/RESULTS.md:186-192`). Against **97–99.5%** for the same defect on
> A1/A2/A5 shape rows and **0.664%** on A6's twist.
> **Named alternatives, registered so neither can be re-read favourably:** an effect **> 15%** while
> the shipped analytic matches FD at 0.9273% would mean the patched vector must be the wrong one, and
> is reported as **the patched row FAILing against the FD reference**, not as a patch success. An
> effect **< 0.001%** (below the printed resolution) is reported as **NOT A RESULT** for R1-P10 —
> resolution-limited, no claim either way — with the raw vectors kept.
> **Analytic-vs-analytic sign flips carry no verdict** and are reported as counts and magnitudes
> only: no FD was measured at those indices, so nothing says which sign is right.

> **R1-P11 — memory. Band: container aggregate peak RSS `3.5 – 6.5 GiB` against a `12 GiB` cap;
> host `MemAvailable` never below `8 GiB`.** Basis, stated as a scaling and not as a measurement:
> rung 2 measured **9.263 GiB** aggregate peak at 42,120 cells
> (`../rung2_patched_idwarp_np4/RESULTS.md:252`) = **0.225 MiB/cell**, and the family's serial fit
> gives **0.169 – 0.240 MiB/cell** (`../rung2_patched_idwarp_np4/PREREGISTRATION.md:620-628`).
> At 21,840 cells that is **3.60 – 5.12 GiB** by the fit and **4.80 GiB** at rung 2's own rate;
> the band is widened to 3.5 – 6.5 GiB because per-cell scaling ignores fixed overhead.
> **Stop rule, and what executes it — this is the L-239 repair.** Rung 2 registered this exact floor
> with a **record-only** watcher, drove host `MemAvailable` to **5.85 GiB** for **82 of 156
> samples**, and **no stop fired** (`../rung2_patched_idwarp_np4/RESULTS.md` §9.1; L-239).
> Here the enforcement path is named: **`mem_guard.sh` polls the container's own RSS and
> `/proc/meminfo` MemAvailable every 5 s (`mem_guard.sh:79-80` are the two threshold tests),
> requires 3 consecutive breaching samples (`:25`, `:85`), and then `sudo -n docker kill`s the
> container at `mem_guard.sh:98` and exits 4 (`:100`)**, writing `MEMORY_STOP_FIRED.<arm>`.
> Thresholds passed by `drive.sh`: **RSS ceiling 11.0 GiB, host floor 8.0 GiB.** A `docker stats`
> parse failure is a **refusal**, not a silent pass (`mem_guard.sh:73`) — the guard will not run
> blind.
> **And the guard is proved able to fire before any arm launches:** `guard_selftest.sh` runs it
> against a planted unbreachable-threshold container that it **must** kill (limb 1, `:33`) and a
> planted unbreachable-in-the-other-direction container it **must not** kill (limb 2, `:55`), and
> writes `GUARD_SELFTEST_PASS` (`:123`) only if both pass. **`drive.sh` refuses to launch any arm
> without that marker.** A guard never shown able to fire is not a guard (CLAUDE.md rule 3).
> **Disposition if it fires:** the arm is **stopped by memory** ⇒ **NOT A RESULT**. No gradient,
> conditioning or patch claim in either direction, **the cap is NOT raised, and no new budget is
> taken** (`COMPUTE_BUDGET_CHARTER.md`).

> **R1-P12 — wall and cost. Band: wall `246 – 640 s`, core-min `16.4 – 42.7`; point estimate
> `418 s` / `27.9 core-min`.** See §8 for the derivation and for why the inflation band's upper end
> is 2.6× and not rung 2's 2.1×. The box is shared; contention is disclosed in `RESULTS.md` either
> way, and a contended wall is **not** offered as a clean cost basis for scaling.

### Arm R1-B — SHIPPED, the literal shipped image

`dafoam/opt-packages:latest`, np=4, **the identical `runScript_fd3p.py`**, `-task fd3`, identical
staged tree, identical colouring cache, identical caps. Its purpose is R1-P5, R1-P6 and R1-P10.
R1-P1 limb (a) inverts for this arm: every rank must print
`IDWARP_SO_MD5 = f0fcb488e0e98156575cd19548e91663` and a site-packages import path. All other
predictions apply unchanged.

> **R1-P13 — the shipped arm's own FD verdict. Band: `patchV[1]` 0.10 – 0.30%, `shape[115]`
> 0.80 – 1.10%, both PASS, zero sign flips; `twist[1]` and `shape[5]` flagged and NOT graded.**
> Prior: the archived ‡ row at 0.1816% and 0.9273%. The band is narrow because R1-P6 predicts this
> arm reproduces that row bit-for-bit; it is a band rather than a point only so that R1-P6's
> falsifier and R1-P13 are scored separately.

### Arm R1-C — TRIVIAL BASELINE (`DAFOAM_CHARTER.md` §4), deliberately wrong FD step

`dafoam-idwarp-rot:v1` — **the patched stack, the one predicted to PASS** — np=4,
`-task fd1wrong`: **one component, `patchV[1]` only, step = 1e-8, one step, no adjoint.**

Three choices recorded here rather than left to the reading:

1. **Why 1e-8 and not 1e-3.** At **rung 1 itself** a step one decade off the registered one was
   *measured* and landed in the **NOT EVALUABLE / step-inconsistent** branch, not the wrong-answer
   branch (`fd3_run_attempt1.log:3960-3962`, step-consistency 16.87–37.46%), so it would give an
   ambiguous control. 1e-8 is the step the A1 step-size study measured at **94.95%** on the
   roundoff-dominated branch, and at which the rung-2 control returned **100.0293%** with the sign
   reversed on a stack reading 0.0077% at its own step.
2. **Why `patchV[1]` and why one component.** It keeps the control under 15 core-min (§8). The index
   is **not** a hand transcription from any printed output — `patchV` is `[U0, aoa0]` with `U0`
   registered at `lower = upper = U0`, so index 1 (AoA) is the only free component by construction.
   The rung-1 mis-parse hazard (`../grading_confirmation/RESULTS.md:138-143`) is therefore not
   reopened.
3. **Why no adjoint.** Its analytic reference is arm R1-A's own `patchV[1]` value, and **the check
   that licenses that reuse is registered**: R1-C's baseline CD must equal R1-A's baseline CD
   **bit-identically**, proving the two arms are at the same primal state. If it does not, the
   control is reported as **NOT A RESULT** rather than compared.

> **R1-P14 — the wrong step fails this rung's own evaluability gate. Band: `|CD(+h) − CD(−h)|` in
> `3.0e-07 – 6.0e-06`, i.e. `delta / threshold` in `0.018 – 0.37`, against a threshold of
> `10 × drift ≈ 1.63e-05`; verdict predicted NOT EVALUABLE.**
> **This band is derived from rung 2's own scored MISS, not from the true derivative, and that is
> the point.** Rung 2 predicted `1.0e-10 – 2.5e-10` from the smooth derivative and measured
> **`5.402995e-07`**, 2,161× above its band, because *"at h=1e-8 the difference between two
> perturbed primals is set by primal re-convergence noise, not by the derivative"*
> (`../rung2_patched_idwarp_np4/RESULTS.md:274-280`). Rung 1's measured drift is `1.626e-06`, twice
> rung 2's `8.093e-07`, so the noise-floor-derived expectation here is of that order. The lesson is
> applied rather than recorded.
> **R1-P15 — and if the ratio is computed anyway, it is large. Band: `> 20%`** against arm R1-A's
> patched analytic. **Registered gray zone:** a noise-dominated estimate is **random**, so a small
> percentage is possible by luck and would **not** be evidence that 1e-8 is a good step — the
> discriminating quantity is R1-P14's delta-vs-floor, not R1-P15's percentage. R1-P15 carries no
> verdict on its own.
> **THE FALSIFIER THAT WITHDRAWS ARM R1-A'S VERDICT:** if the wrong step both **clears** the
> evaluability gate **and** returns ≤ 5%, then the gate is not measuring what it claims, and per
> `DAFOAM_CHARTER.md` §4 **arm R1-A's verdict is withdrawn, not defended.**
> **Second falsifier:** a primal failing to converge under the perturbation → the arm is NOT
> EVALUABLE, not a pass.
> **R1-P16 — control cost. Band: wall `60 – 200 s`, core-min `4.0 – 13.3`; peak RSS `< 3 GiB`** (no
> adjoint, no Jacobian assembly).

## 7. Mechanics, launch condition, and stop rules

* **Staged copies.** `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/{patched,shipped,wrongstep}/`,
  each a fresh copy carrying `0/ 0.orig/ FFD/ constant/ system/ dRdWColoring_4.bin{,.info}` and the
  scripts; **no** `processor*`, `_prior_state_backup_*`, `reports/`, `mphys.html`, `dump_*.dat*` or
  `*.log` is copied. The archived case is **read-only** to this item.
* **Staging asserts, all before any launch:** `sha256(constant/polyMesh/points.gz)` equals
  `695b729d…`; `md5(dRdWColoring_4.bin)` equals `a6919b8494a78f09c9c876e0d21686e2`; `diff -rq 0
  0.orig` is empty; no `processor*` and no non-`0` time directory exists; `diff runScript_fd3.py
  runScript_fd3p.py` shows only D1, D2, D2b, D3. Any failure ⇒ **BLOCKED**, nothing launches.
* **Cores.** `--cpus=4`, inside the 4-core lane cap and the 8-core team cap.
* **Memory.** `--memory=12g`, per R1-P11.
* **Foreground, bounded.** `timeout 780` on R1-A and R1-B, `timeout 300` on R1-C.
  `(780 + 780 + 300) × 4 / 60 = 124.0 core-min` — **the registered ceiling is reachable but not
  exceedable by construction.** No unbounded process is started; nothing is detached without a
  self-writing ledger.
* **GUARDS — every registered stop names what polls it and what performs the stop (L-239).**

  | threshold | polled by | fired by | on fire |
  |---|---|---|---|
  | own RSS > **11.0 GiB**, 3 consecutive 5 s samples | `mem_guard.sh:79` | `mem_guard.sh:98` (`docker kill`), exit 4 at `:100` | arm **NOT A RESULT — stopped by memory**; cap NOT raised |
  | host `MemAvailable` < **8.0 GiB**, 3 consecutive 5 s samples | `mem_guard.sh:80` | `mem_guard.sh:98`, exit 4 | same |
  | `docker stats` unparseable | `mem_guard.sh:73` | refusal, exit 2 | arm must not run blind ⇒ **BLOCKED** |
  | `Calculating dRdW Coloring` present | `coloring_guard.sh` loop | `coloring_guard.sh:55` (exit 3) via `:38` | warm-cache basis **VOID**, arm **NOT A RESULT** |
  | colour count ≠ **1233** | `coloring_guard.sh` | `coloring_guard.sh:63` (exit 5) via `:38` | not the same colouring, arm **NOT A RESULT** |
  | guards not proved able to fire | `guard_selftest.sh` limbs 1–5 | writes `GUARD_SELFTEST_PASS` at `:123` only on a clean sweep; exits 1 at `:128` otherwise | **`drive.sh` refuses to launch any arm** ⇒ **BLOCKED** |
  | wall > `timeout` | `timeout(1)` | SIGTERM, rc 124 | arm stopped at its measured cost with no number; **no second budget** |

  **The selftest is the part that is new, and it is what makes the rest of the table true rather
  than decorative.** Limb 1 plants thresholds no container can satisfy and requires the guard to
  kill; limb 2 plants thresholds no container can breach and requires it **not** to; limbs 3–5 plant
  a rebuild log (carrying a masking `Reading Coloring` line), a genuine warm-cache log, and a log
  with rung 3's colour count, and require exit 3, 0 and 5 respectively. `GUARD_SELFTEST_PASS` must
  be **newer than every guard script it names**, so editing a guard invalidates its own licence.
* **LAUNCH CONDITION, checked in a bounded polling loop immediately before each arm:**
  **`free_cores ≥ 4` AND `MemAvailable ≥ 12 GiB`**, with
  ```
  busy       = median over 5 samples taken 2 s apart of ( `ps -eo state= | grep -c '^R'` − 1 )
  free_cores = nproc − busy                                    ( nproc = 16 )
  ```
  Polled every 60 s for at most **240 polls (4 h)**. This is the gate Amendment 2 of the rung-2 item
  derived and which opened in 9 polls where `load1 ≤ 8` had failed in 12
  (`../rung2_patched_idwarp_np4/RESULTS.md:75-92`); the load-average limb is **not** used, because
  it never measured the resource a `--cpus=4` container consumes.
  **Reading at filing, 2026-08-23:** `MemTotal` **30.64 GiB**, `MemAvailable` **26.10 GiB**,
  `load1` 7.83, runnable threads **9** ⇒ `free_cores ≈ 7`, so the gate is **open at filing**. Live
  compute at filing: 4 `buoyantBoussinesqSimpleFoam` (T-family), 1 `simpleFoam`, and **a live 4-rank
  DAFoam W4 run in container `w4m1m2_m2` on `dafoam-subpclu:v1`** — **another lane's, not touched.**
  The W4 container is why the poll is retained rather than skipped: it may finish or a successor may
  start between filing and launch, and the gate is what decides, not this reading.
  If the condition is not met inside the window, **no arm launches**, the item is recorded
  **BLOCKED on host contention with $0.00 of solver compute spent**, and the staged tree is left for
  a later window.
* **RSS trace.** `mem_guard.sh` writes every sample to `rss_<arm>.txt`; it is the same trace the
  rung-2 record-only watcher produced, now written by the process that can also act on it.
* **Ledger.** One line per arm in `ledger.txt`: arm, image, image ID, `.so` md5, ranks, `t0`, `t1`,
  wall s, `core-min = wall × 4 / 60`, rc, peak RSS, guard exit codes.
* **Registered decision rule, so no budget escape is decided in the moment:** if arm **R1-A** expires
  on its `timeout`, **arms R1-B and R1-C are NOT launched**, the item reports what it has, and **no
  second budget is requested**. If R1-A succeeds but R1-B expires, R1-C still runs, the patched row
  is graded against the **archived ‡ row** (matched np, matched script, matched steps), R1-P6 and
  R1-P10 are recorded **PENDING**, never as absent, and the ‡ caveat stays on the comparator.
* **Escalation.** Any outcome that moves one of the guidelines' §6 headline numbers — which includes
  the FD-gate percentages — is reported, not acted on. No regrade, no verdict move, no board edit
  and no satellite edit is made by this item.

## 8. Cost, registered before the runs

**Measured basis, not an estimate.** The shipped rung-1 `fd3` arm ran **this exact task, this exact
script, this exact four-component set, these exact steps, on this exact mesh, at np=4, with the
warm colouring cache**, in **246 s** wall — `.t0 1786228698`, `.t1 1786228944`, `.rc 0` in
`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/` — = **16.400 core-min**.

**How this item scales, said plainly.** It does **not** scale by cell count. Rung 1 has its own
task-matched, np-matched, script-matched, warm-cache measured wall, so the only quantity carried
across from another rung is the **contention inflation factor**. That factor is taken from rung 2's
measurement on **this** box — arm P-A ran **955 s** against a **452 s** idle basis, **2.11×**
(`../rung2_patched_idwarp_np4/RESULTS.md:292`) — and is widened to **1.0× – 2.6×** with a point
estimate of **1.7×**. The upper end is 2.6× and not 2.1× for a stated reason: **rung 2's own
inflation band was 1.0–2.1× and was scored a MISS by 5 s of wall**
(`../rung2_patched_idwarp_np4/RESULTS.md:260-262`); a band that only just fails to contain the last
measurement is not a band. *For the same reason the patched and shipped arms are costed identically:
rung 2 measured the two images' adjoints bit-identical on 11/11 points, so the patch changes the
answer, not the work.*

The trivial baseline's basis is rung 2's **measured** control, **152 s** at 42,120 cells
(`RESULTS.md:293`), which already carries contention; scaled by the two rungs' shipped `fd3` wall
ratio `246/452 = 0.544` it gives **83 s**, and the band is widened to 60–200 s.

| item | ranks | predicted wall | predicted core-min | band | `timeout` | worst-case core-min | $ @ $0.0513/core-h |
|---|---|---|---|---|---|---|---|
| **R1-A** PATCHED `fd3` | 4 | 418 s | **27.9** | 16.4 – 42.7 | 780 s | 52.000 | $0.0239 |
| **R1-B** SHIPPED `fd3` | 4 | 418 s | **27.9** | 16.4 – 42.7 | 780 s | 52.000 | $0.0239 |
| **R1-C** trivial baseline `fd1wrong` | 4 | 110 s | **7.3** | 4.0 – 13.3 | 300 s | 20.000 | $0.0062 |
| guard selftest (4 `alpine` containers) | 1 | ~110 s | **1.8** | 0.5 – 2.0 | — | 2.000 | $0.0015 |
| per-rank provenance pre-flight (no solver, no case) | 4 | 3 s | **0.200** | — | — | 0.200 | $0.0002 |
| launch-condition polling | — | — | **0.000** | — | 4 h | 0.000 | $0.00 |
| rung-1 plateau sweep (§5) | — | **not run — declined by name** | **0** | — | — | 0 | **$0.00** |
| fresh colouring pass | — | **not run — cache carried, §3 departure 1** | **0** | — | — | 0 | **$0.00** |
| **predicted total** | | | **65.1** | 37.5 – 100.3 | | | **$0.0557** |
| **worst case by construction** | | | | | | **126.200** | $0.1079 |
| **REGISTERED CEILING** | | | | | | **127.0** | **$0.1086** |

**`cost_basis`: c7a.4xlarge at $0.0513/core-hour, owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure here is REPORTED-BY-OWNER, NOT MEASURED.
The core-minute figures are measured or scaled from measurement as stated above; the dollars are
not.**

**HARD STOP: total item spend must stay ≤ 127.0 core-min.** The three timeouts plus the two bounded
pre-flights make the worst case **126.200** by construction, so the ceiling cannot be breached
without a `timeout` failing to fire. **Nothing here approaches $25** — the worst case is **0.43%**
of the bar at which an item is listed for Sanaa instead of run. An overrun **stops the run; it does
not get a new budget.** The estimate is registered here and **the miss is reported as a miss** in
`RESULTS.md`, against this table and not against a re-derived one.

## 9. What this item cannot see, stated in advance

1. **Three of four FD components carry no verdict at this rung.** `twist[1]` and `shape[5]` are
   step-inconsistent at 5.2887% and 8.2023% against a 1% gate and are flagged by name (§4);
   `patchV[1]` does not cross the warp chain and is IG-2 evidence, not a gate (R1-P7). **One
   warp-crossing component, `shape[115]`, carries this rung's FD verdict.** R1-P10 measures the
   patch effect across all 120 shape components, but **that row has no FD beside it** — it is
   analytic-vs-analytic, and rung 2 turned up 3 analytic sign flips at indices nobody has ever
   FD'd. A5's `idx16` is the standing demonstration that a component nobody looked at can be the one
   that matters.
2. **The plateau at rung 1 is a two-point read, not a proved plateau** (§5), and no third step is
   bought. This item claims a measured step-consistency check at a step with measured floor
   clearance; it does not claim §3 of the charter is satisfied at rung 1.
3. **The decomposition axis.** np=4, `scotch`, one partition, on all three arms — because an FD
   reference is never carried across np (`DAFOAM_CHARTER.md` §5). A4's **16,600×** split between two
   decompositions of one mesh is why this is a real limitation. **A3 still has no decomposition
   datum**; rung 2's np=1 attempt was stopped before it produced a gradient. Nothing here says A3
   rung 1 is decomposition-invariant, and `DAFOAM_CHARTER.md` §5's *"serial before parallel"* remains
   unsatisfied on A3.
4. **Regime 2 of the rotation defect.** `fd3` evaluates at the undeformed baseline and at ±1e-2 DV
   perturbations, where the `sqrt(eps)` guard fires and regime 1 dominates. The near-threshold
   ill-conditioned `acos` regime survives the patch **by design** (`BUILD.md` §7 limit 2) and is not
   probed here.
5. **The limiter lever and the DAFoam-side defects.** The patch does not touch DAFoam (`BUILD.md`
   §7 limit 3). A3's `fvSchemes` is unchanged and has no counterpart to A1's 92.8% → 0.121%
   `limited`/`default` arm.
6. **Mesh quality at rung 1 is unverified by this item.** There is no birth certificate and no
   `checkMesh` record on disk for the rung-1 mesh (§3 departure 3). The `points.gz` hash pins
   *identity*, not *quality*. This item inherits whatever the archived rung-1 mesh is and says so.
7. **The `CL` rows.** `fd3` computes totals for **CD only**. `dCL/d*` at rung 1 is unmeasured on
   every image, by this item and by the archived one.
8. **Whether a converged adjoint licenses the gradient.** R1-P4's `reason 2` is an identity check
   between two images, not evidence of a correct operator (L-35, L-36; `DAFOAM_CHARTER.md` §6). The
   FD table grades the gradient, and at this rung it grades one warp-crossing component of it.
9. **The other cells of row 12b.** This buys rung 1 only. Rung 3 is the companion item; the original
   399,360-cell campaign keeps **PENDING** in the PATCHED column and is BLOCKED for reasons neither
   item touches.
10. **Whether the R1-P8b mechanism generalises beyond A3.** Two rungs of one case cannot establish
    that the patch's analytic delta has a consistent sign in general. If R1-P8b lands it is a
    two-point pattern on one case, and `RESULTS.md` will say exactly that.

## 10. Standing statements

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

**Three rows, never merged.** The archived SHIPPED-equivalent ‡ row is cited from
`../grading_confirmation/RESULTS.md` §2b and `A3-onera-m6-sweep-n15_21840/fd3_run.log`; the fresh
literal-SHIPPED row and the PATCHED row are measured here. **A patched grade never replaces a
shipped grade** — that requires the fix shipping upstream or Sanaa formally adopting a forked
toolchain, and it is her call, not a session's (R11, `../../FAMILY_SUPERVISION_GUIDELINES.md` §3.4).

**Toolchain identity is an image ID and a library hash, never a version string**
(`DAFOAM_CHARTER.md` §6). `idwarp` reports `2.6.2` on both stacks.

**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

This item edits no frozen file, and edits none of `docs/LAB_STATE.md`, `docs/LESSONS.md`,
`docs/DOCKET.md`, `docs/NUMERICS_KNOWLEDGE.md`, `cases/dafoam/INDEX.md`, `LADDER_A_STATUS.md` or any
charter. Drafted text for those is delivered to the supervisor, who owns the append.

## 11. Frozen-file manifest

The grading path is fixed at this commit and is verified before launch by hashing each file against
its committed blob (CLAUDE.md rule 2). The four files frozen by this pre-registration are:

| file | role |
|---|---|
| `PREREGISTRATION.md` (this file) | gates, thresholds, bands, caps, labels |
| `mem_guard.sh` | the wired memory stop (R1-P11) |
| `coloring_guard.sh` | the wired colouring-cache stop (R1-P3) |
| `guard_selftest.sh` | the proof that both guards can fire, and the launch licence |

The guards are **duplicated per rung rather than shared** with `../rung3_patched_idwarp_np4/`, and
that is deliberate: each item's grading path must be a file frozen at **its own** pre-registration
commit and hashable against **its own** blob. A shared script could be edited by the other item
between the two freezes.

**No run directory named in this file exists at the time of this commit.**
`/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/` was checked and does not exist, and neither do
`patched/`, `shipped/` or `wrongstep/` beneath it.

## 12. The exact launch sequence a phase-2 lane runs

Registered so the launch is executed rather than re-designed, and so `RESULTS.md` can be checked
against what was supposed to happen. **Nothing below is run by this item.**

```
# 0. freeze check — the file that runs must BE the committed blob
cd /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/rung1_patched_idwarp_np4
for f in PREREGISTRATION.md mem_guard.sh coloring_guard.sh guard_selftest.sh; do
  git cat-file blob HEAD:cases/dafoam/ladder-a/A3/rung1_patched_idwarp_np4/$f | cmp - $f || exit 1
done

# 1. stage, with every §7 assert. Refuses on any mismatch.
./stage.sh            # written by the phase-2 lane; asserts points.gz sha256, cache md5,
                      # diff -rq 0 0.orig, no processor*, and the fd3 -> fd3p diff

# 2. prove the guards can fire — BEFORE any solver starts
./guard_selftest.sh /home/ubuntu/certonomous-runs/P4-a3-rung1-patched "$PWD"
test -f /home/ubuntu/certonomous-runs/P4-a3-rung1-patched/GUARD_SELFTEST_PASS || exit 1

# 3. per-rank provenance pre-flight: 4 ranks, no solver, no case, ~3 s
sudo -n docker run --rm --cpus=4 dafoam-idwarp-rot:v1 bash -lc \
  'source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 -x PYTHONPATH \
   python -c "import idwarp,hashlib,os;p=os.path.dirname(idwarp.__file__); \
   print(idwarp.__file__, hashlib.md5(open(os.path.join(p,\"../libidwarp.so\"),\"rb\").read()).hexdigest())"'

# 4. the arms, strictly sequential, guards armed per arm, gate polled before each
./drive.sh            # R1-A patched fd3 780s -> R1-B shipped fd3 780s -> R1-C wrongstep 300s
                      # drive.sh preconditions: GUARD_SELFTEST_PASS exists and is newer than
                      # mem_guard.sh and coloring_guard.sh; free_cores >= 4; MemAvailable >= 12 GiB
                      # decision rule: R1-A rc=124 -> R1-B and R1-C are NOT launched
```

`stage.sh` and `drive.sh` are written by the phase-2 lane **after** this file is committed, are
committed **before** they run, and may change no gate, threshold, band, cap or label in this
document.
