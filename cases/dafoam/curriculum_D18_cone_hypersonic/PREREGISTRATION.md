# CURRICULUM D18 — `Cone_Supersonic` as a 2D WEDGE at **M 5.0002** (`DAHisaFoam`, inviscid): the BASELINE adjoint gradient of CD w.r.t. the tutorial's `shape` functions, FD-VERIFIED on TWO TOOLCHAIN ROWS — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (B). Supervisor: `dafoam-supervisor` (dispatch: *"D18 — `2D · steady · hypersonic` off D17's exact staging, one registered delta (freestream Mach) … carry `NONCONVERGENCE_STANDARD`'s anti-gaming clause explicitly and by name … say in §7 what D18 can and cannot resolve before it runs"*). **This document is `curriculum_D17_cone_supersonic/PREREGISTRATION.md` with the registered deltas of §2 and §7 and nothing else inherited silently: where a number here disagrees with D17's text for a clause this document does not list as a delta, D17's text wins and this document is defective.** Permission `bc0e687e`; Sanaa's standing directives 2026-08-27T16:54Z (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`); `NONCONVERGENCE_STANDARD.md` (`7ffd6c73`); L-342 `d4d0c29d`; grid `068c2bf0`. `[lab-attributed]`.

**NOT FILED ANYWHERE.** Nothing here is filed, sent, emailed, uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

---

## 0. THE CELL, AND WHAT "HYPERSONIC" HONESTLY MEANS HERE

**Cell: `2D · steady · hypersonic`, column "gradients computed + FD-verified"** — today `CAN NOT DO — not attempted`. **Only the gradient column moves**; no optimiser runs.

**Dimension, solver, geometry, mesh, DVs, objective and constraints are D17's, unchanged and not re-derived** (`curriculum_D17_cone_supersonic/PREREGISTRATION.md` §0 @ `2d8796e3`): a planar 2D wedge, half-angle **11.3099°**, **40,000 cells** after `mirrorMesh`, `DAHisaFoam` (HiSA density-based, JST flux, dual-time steadyState, `endTime 500` pseudo-steps), **inviscid** (`mu 0`, `RASModel dummy`), aoa 0, `shape` with 6 components, objective `cruise.aero_post.CD`, `CL` a symmetry reading and never a gate. **Not axisymmetric** (no `wedge` patch pair) and not 3D (one cell thick).

> ### THE REAL-GAS CAVEAT, STATED BEFORE THE RUN AND NOT AFTER IT
>
> **This cell is hypersonic IN THE MACH NUMBER ONLY.** `constant/thermophysicalProperties` carries a **calorically perfect** gas with constant `Cp` and `mu 0`. At M 5 real air begins vibrational excitation, and higher still it dissociates. **None of that is modelled and none of it is claimed.** The registered post-shock static temperature on the perfect-gas oblique-shock relations is **450.7 K**, where the perfect-gas assumption is still defensible; the stagnation temperature is not, and no stagnation quantity is graded. **A reader of the capability grid must not take this cell as a statement about hypersonic AEROTHERMODYNAMICS.** The grader writes this caveat into every artefact (`real_gas_caveat`), so it cannot be separated from the verdict.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic` DOES NOT EXIST.**

`test -e` → **false**, driven **twice inside `d18_groot5_selftest.sh`** (its opening leg and again as the closing freeze condition after the temporary root is removed) at **2026-08-27T17:34:55Z**, `18/18`, evidence `d18_groot5_selftest_evidence.txt`. **0 solver core-min. No arm container has started.** The only containers this lane ran are the sacrificial `sleep` of the G-ROOT.5 selftest. After the first arm container, gates are **CLOSED**.

**Disclosed, because it is the shape of a defect and not a footnote:** an earlier drive of the selftest (17:33:33Z) left **one file** in the run root — its own `(e)`-fixture copy of `d18_mach_agreement.py`, which the cleanup list did not name. The next drive then correctly **REFUSED to test over an existing root**. The leftover was **inspected before anything was removed** (one entry, byte-identical to this directory's own file, no ledger, no manifest, no arm directory, no log — nothing a run produced), then cleared, and the cleanup list was repaired to name every file the fixture stages. **The guard worked; the fixture was wrong.**

## 2. THE ONE REGISTERED DELTA — and the gate that exists because it is carried TWICE

| | D17 | **D18** |
|---|---|---|
| `U0` | 680.0 m/s | **1736.0 m/s** |
| M∞ = `U0`/√(1.4·287·300) = `U0`/347.1887 | 1.9586 | **5.0002** |
| `p0`, `T0`, mesh, FFD, DVs, objective, steps, arms, images, caps, cpuset | — | **all unchanged** |

**Everything else is D17's**: chain `d18_chain_driver.sh MESH X-S F-S X-P F-P`; arms MESH (SCRIPT, SHIPPED, 1 rank), X-S/X-P (SOLVER, 2 ranks), F-S/F-P (SOLVER, 2 ranks); two rows or it is not a verdict; components `shape[0,1,3,4,5]`; steps `{1e-2, 1e-3, 1e-4}`; 32 primals per F arm; the `CTRL` planted-zero control.

**`U0` IS CARRIED INDEPENDENTLY BY TWO FILES, AND THAT IS A DEFECT WAITING TO HAPPEN:**

- `0.orig/include/freestreamConditions` — `U (1736.0 0 0)`. **The solver reads its actual boundary condition here.** The `primalBC` block in `runScript.py` that would override it **is commented out in the tutorial.**
- `runScript.py` — `U0`, used **only** for `scale = 1/(0.5·U0²·A0·ρ0)` on CD and CL and for `normalizeStates`. **It does not move the flow.**

A change to one alone produces **a plausible CD that is wrong by the square of a ratio, with every other check in this family passing**: rc 0, an `End` line, the age guard, the cell count, the FD plateau, the two-row divergence — all of them. Nothing else in this instrument set can see it. That is precisely the shape of `D5-LAUNCHER-DEF-1` and `W3-LAUNCHER-DEF-1`: **one quantity, two spellings, no gate across them.**

**Both files are staged as registered overlays** — the tutorial's own bytes are md5-asserted at staging and then replaced, exactly as D17 does for `decomposeParDict`. `d18_runScript.py` is **not** a byte copy of the tutorial and its md5 pin says so.

## 3. GATES — D17 §3 verbatim, with ONE ADDITION and ONE BAND CHANGE

**Every gate, band, label and composition rule is D17 §3 (hence D16/D15), verbatim** — G1 arm-kind-aware completion with the age guard and the `.inspect.txt` kernel fallback; L-342 field classes; **G5 band D 5.0 % per component with the sign-flip rule, band E 5.0 % aggregate, plateau 10 %, ≥ 3 graded components**; G6 dot-product/duality **NOT MEASURED, named**; G9 two `.so` md5s and two digests; G10 caps, ceiling **785.0**; G11 OOM hard; G12 delivered cores and cpuset `12,15`; G-M2 `cells == 40,000`; the CL symmetry reading; **no GCI** (no grid family; standing rule 5 has no row).

**ADDED — `G-MACH`** (`d18_mach_agreement.py`). The two carriers of `U0` (and of `p0`, `T0`) must **agree with each other AND with the registered value**, exactly — these are typed constants, not measurements, so the tolerance is **zero**. A non-zero freestream `v`/`w` refuses (it would break the CL symmetry reading silently). More than one top-level `U0 =` in the producer refuses. A value the gate cannot read **refuses; it never passes.** G-MACH runs **before every arm** in the launcher and after staging in the driver, and is **re-read at grade time from the staged bytes** through the **staged copy of the instrument, whose md5 is asserted first** — the freeze discipline applied to the flow condition. The **ledger line is corroboration only**; its absence is INFRASTRUCTURE (L-342), the staged bytes are the physics.

**CHANGED — P3's band only** (§6). No other band, threshold, cap, label or composition rule moves.

## 4. COST — on a MEASURED anchor, D17's own arms

D17 is the same mesh, the same solver and the same **fixed 500 pseudo-steps per primal**, so the wall per primal is bounded by the step count and not by the Mach. **Measured** (`curriculum_D17_cone_supersonic/RESULTS.md` §8): MESH 0.167, X-S 7.833, F-S 75.733, X-P 7.100, F-P 82.000 → **172.833 core-min against 180.3 predicted, ratio 0.959**, waste 0.000.

| arm | point (core-min) | cap | in-container wall | mem |
|---|---|---|---|---|
| MESH | 0.2 | 5.0 | 300 s (1 rank) | 4g |
| X-S, X-P | 9.0 each | 90.0 each | 2,700 s (2 ranks) | 8g |
| F-S, F-P | 82.0 each | 300.0 each | 9,000 s (2 ranks) | 4g |
| **total** | **182.2** point, band **[60, 450]** | **ceiling 785.0 = Σ caps** | | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED**: point **$0.1558**, ceiling **$0.6712**. The point is **above** D17's measured 172.833 because a stiffer shock may need more GMRES work per pseudo-step; the step count that bounds it does not move. **No pre-compute probe cost is billed here** — D17 already established both images carry `hisa` and the DAFoam wrapper, and this item re-uses that reading rather than re-buying it (3.05 core-min saved and named). Calibration row owed at completion.

## 5. PLACEMENT, MEMORY AND THE DETACHED FORM

**D17 §5 verbatim**, cpuset **`12,15`** (unchanged — reusing D17's placement keeps the registered delta count at exactly one), including **G-CPUSET** wait-and-retry against D8R's overlapping `0,1,12,15` (poll 30 s, bound 14,400 s, `rc=6` at the bound, zero compute), the per-arm H5 floors (12.0 GiB for X, 8.0 for MESH/F), the aggregate wait-and-retry < 30.6 GiB, the detached driver with `STATUS.<arm>` / `STATUS.chain` / `d18_driver.pid`, no `--rm`, the `.inspect.txt` kernel record, and **`CHAIN_DONE`** appended on every exit of a started chain. **G-ROOT.1–.5 demonstrated 18/18 at 2026-08-27T17:34:55Z**; the forbidden-root list gains **D17's own root**.

## 6. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

| # | prediction | value / band |
|---|---|---|
| **P1** | MESH reproduces the mesh | **cells == 40,000** |
| **P2** | baseline `CL` (symmetry reading) | **abs(CL) ≤ 1.0e-3** |
| **P3** | baseline `CD` | **[0.055, 0.105]**, point **0.078842** |
| **P4** | PATCHED row G5 (CD) `PASS` with **≥ 4 of 5** in band D | scored |
| **P5** | SHIPPED `shape[0]` (the LE-class function) outside band D or sign-flipped | HIT / MISS / `NOT_MEASURED` |
| **P6** | total graded core-min in **[60, 450]** (point 182.2); MESH wall ≤ 120 s | both scored |
| **P7** | **the two rows are NOT DISCRIMINATING: S/N ≤ 1.0** | scored, with the number printed |

**P3 is not a guess and its falsifier is sharp.** The oblique-shock model `CD = (A_proj/A0)·p2/q` with `A_proj/A0 = 0.4` reproduces **D17's MEASURED `CD_baseline` 0.269886 to 0.014 %** (model 0.269849). Re-evaluated at M 5.0002 — β 20.615°, `Mn1` 1.7605, `p2/p1` 3.4491, q 1.7733e6 Pa, **shock ATTACHED** (θ_max at M 5 is 41.12° against a wedge 11.31°) — it gives **0.078842**. The band is ±30 %/+33 %. **Because the model's residual on D17 was 0.014 %, a miss wider than 30 % says the 1-D oblique-shock reading of this configuration breaks down at hypersonic Mach — which is itself the finding, not a defect of the item.**

## 7. WHAT D18 CAN AND CANNOT RESOLVE — STATED BEFORE IT RUNS

**D17 was NOT DISCRIMINATING and said so** (`curriculum_D17_cone_supersonic/RESULTS.md` §"signal-to-noise"): its worst shipped-vs-patched divergence, **2.268 %** (`shape[3]`), was **smaller than its own PATCHED control row's worst FD error, 2.777 %** — **S/N 0.82**. Its P5 MISS is a statement about D17's resolving power, not about the IDWarp rotation defect.

**At M 5 the common-mode FD error will very likely be WORSE, not better**: a stronger, thinner shock on the same 40,000-cell mesh moves further per FFD perturbation relative to the cell size, and the JST smoothing that captures it is the term the FD difference is most sensitive to. **So D18 is registered on the expectation that it too will not discriminate the two rows — P7, `S/N ≤ 1.0`, HIT.**

**Therefore, and this is the registration that matters:**

- **What D18 CAN establish:** whether `DAHisaFoam` produces an **FD-verified baseline adjoint gradient at hypersonic Mach at all** — the cell — and **how the solver behaves there** (primal convergence, plateau quality, the common-mode error's own magnitude, which is a number this family has never had above M 2).
- **What D18 CANNOT establish, and must never be read as establishing:** a shipped-versus-patched **discrimination**. If both rows `PASS`, **that is not evidence the two toolchains agree**; it is evidence that at this noise level they cannot be told apart. **A `PASS` here must not imply a discrimination the item never had**, and the grader prints `_P7_signal_to_noise` beside every verdict so the two cannot be separated.
- If P7 MISSES — S/N > 1 — then D18 **is** discriminating and its P5 reading carries weight the D15/D16/D17 sequence did not. That would be the surprise, and it is registered as such.

## 8. NON-CONVERGENCE — `NONCONVERGENCE_STANDARD.md` (`7ffd6c73`), BY NAME

**`DAHisaFoam` cleared its own primal guard at M 1.958 on this box, on the tutorial's options, unmodified** (D17 §1). **At M 5 it may not.** Registered plainly, before the run:

> **If the primal does not satisfy DAFoam's convergence guard, X-S exits non-zero with `Primal solution failed`, the chain STOPS, and the item is `NOT A RESULT` with ≤ one X cap spent. THAT IS A RESULT AND IT IS THE REGISTERED OUTCOME — the finding is *the tutorial as shipped does not clear its own primal guard at M 5 on this box*. A named `BLOCKED` or `GATE FAIL` or `NOT A RESULT` in an empty grid cell is still a result, and predicting it in advance is what makes it one.**

**THE ANTI-GAMING CLAUSE, quoted from Sanaa's §3 and binding on this item:**

> *"Convergence aids (L1–L5) tune freely, disclosed. Answer-changing choices (model, scheme class, formulation) are never selected by agreement with the reference. Converged-but-wrong = NOT HELD with diagnosis, never a parameter hunt. Frozen gates never edited post-compute."*

**Operationally, and this is the temptation this item must be fenced against:** M ≥ 5 on a JST/dual-time density solver is exactly where one is tempted to keep changing things until it converges, and then to keep the version whose CD looks closest to the oblique-shock estimate. **That is forbidden here, twice over.** (i) **NOTHING IS TUNED IN THIS ITEM AT ALL.** D18 registers the tutorial's options unmodified; there is no L1–L5 arm. A non-convergence closes the item as above and any diagnostic ladder is a **separate, separately frozen item** with its own caps and one change per run. (ii) **P3's band is frozen in this document, before the run, and `d18_grade.py`'s md5 is fixed at this commit** — so no scheme, limiter or CFL choice can be selected by how close it lands to 0.078842. **Frozen gates are never edited post-compute.** If the primal converges only under a changed scheme, that is a **model-form finding to be registered**, never a repair folded into this item.

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

D17 §8 verbatim, plus: **nothing about real-gas hypersonics** (§0 — perfect gas, no vibrational excitation, no dissociation, no viscous or radiative heating); nothing about the shock's position or strength (no Cp is graded); nothing axisymmetric (the `axisym` row stays `CAN NOT DO — not attempted`); nothing about the constraints (no optimiser; the `optimization converged` column does not move); **nothing about shipped-versus-patched discrimination unless P7 MISSES** (§7); nothing about `DAHisaFoam` beyond the tutorial's own options.

## 10. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | derivation |
|---|---|---|
| `d18_run_arm.sh` | `1fd05704a7ef0ede0057c9b18283c775` | `d17_run_arm.sh` + names/root, D17's root forbidden, the producer pin, the freestreamConditions md5 assert and the G-MACH call before every arm |
| `d18_chain_driver.sh` | `f41bd1a74b098de34e2a80f008b99bea` | `d17_chain_driver.sh` + names/root, the freestreamConditions overlay, staging the G-MACH instrument, and the post-staging G-MACH call teed to the ledger |
| `d18_xf.py` | `3e63a9fa945bc6d7b3196e1e3e084a7f` | `d17_xf.py` + item/artefact names and the producer pin. CTRL control, emit/fsync, η, the plant read-back: unchanged |
| `d18_grade.py` | `e4ade11ed9e3db18d2c4988b30e929b4` | `d17_grade.py` + `g_mach()`, P3's band and point, P7, the re-priced `PREDICTED_CORE_MIN`, the cell string and the real-gas caveat, and seven new selftest units. **Bands D/E, plateau, sign-flip, field classes: unchanged. `EXPECTED_UNITS` 22 → 29; 29/29 plain and `-O`** |
| `d18_mach_agreement.py` | `d6a5b389f0976801416bfd81909e0176` | **NEW** — G-MACH. **10/10 plain and `-O`** |
| `d18_pin_sweep.py` | `7293bc885a8003a835a2c7c3226c881a` | **NEW** — every `MD5_*` pin against the file it names. **5/5 plain and `-O`** |
| `d18_groot5_selftest.sh` | `568575353978a44dfaaaef98efb51e3b` | `d17_groot5_selftest.sh` + names, D17's root in (d), the two new staged artefacts in the (e) fixture and in its cleanup. **18/18** |
| `d18_runScript.py` | `e6f0baf0e07a4ede7bff555e5e0ed332` | the tutorial's `runScript.py` with **the one registered delta**; comments stripped and the delta reversed, it is **byte-identical** to the tutorial (proved in `d18_control_evidence.txt`) |
| `d18_freestreamConditions` | `2c18bb481b762706ab03bbbac3a91a4d` | the tutorial's file with **one line changed** (proved, same evidence file) |
| `d18_cpuset_overlap.py` | `f884114b3f2baac5df5644bc53f4394e` | D17's, re-pointed |
| `d18_decomposeParDict` | `68ecc827562886fb43c3aedb0627b344` | byte-identical to D17's / D16's / D15's |
| `d18_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | byte-identical to D17's |

**`ast.Assert` count 0 in every python file above** (`-O` deletes asserts). **Classifier denials while building this item: none.**

**FOUR STALE PINS WERE FOUND AND REPAIRED BEFORE THE FREEZE, and they are recorded rather than tidied.** Building D18 by copy-and-delta from D17 left `MD5_LAUNCHER`, `MD5_GRADER` and `MD5_XF` stale in the driver and `MD5_XF` stale in the launcher — the renamed files hash differently and nothing was checking. **That is `D8R-DRIVER-DEF-1`'s class**, where a frozen driver named an md5 that no longer matched and the chain would have aborted at staging, exit 4, buying nothing. The G-ROOT.5 selftest caught one; `d18_pin_sweep.py` was then written to catch all of them at once, is driven with a **planted stale pin**, and **refuses rather than reporting a clean zero over an empty population.** It sweeps clean over 9 pins at this commit.

## 11. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). The grading path is fixed at this commit: `d18_grade.py` md5 `e4ade11ed9e3db18d2c4988b30e929b4`, asserted by the driver before every arm. **Queue entry `verification/queue/dafoam/D18_chain.json`:** team `dafoam`, `prereg_commit` = the sha of the commit introducing this file, `launch_cmd` = `["bash", "<abs>/d18_chain_driver.sh", "MESH", "X-S", "F-S", "X-P", "F-P"]`, `cwd` = this directory, `ranks 2`, `cost_core_min_estimate 182.2`, `cap_core_min_registered 785.0`, `memory_floor_gb 12.0`, `cost_basis` derived / not measured, `permission bc0e687e`. **Enqueueing is not authorisation** — `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own.

**Predicted outcome:** P1, P2, P3, P4, P6 HIT; **P7 HIT (the two rows do not discriminate)**; P5 undetermined and reported as whatever it is; the `2D · steady · hypersonic` gradient cell moves from `CAN NOT DO — not attempted` to **`CAN DO, CAVEATS`** — the caveats being the single mesh, the perfect-gas assumption of §0, and the absence of two-row discrimination. **If the primal does not converge, the item is `NOT A RESULT` and the finding is §8's.**

---

## ADDENDUM A — 2026-08-27, appended by dafoam lane C on `dafoam-supervisor`'s explicit order — CITATION FORM ONLY

**Version 1.0 → 1.0a. Appended at the foot. Lines whose number changed above this section: 0**,
proved by byte comparison of the 138-line prefix against the blob this document was frozen at, not
by eyeball. **This document was authored by another lane (B), which is gone. Lane C appended this
section and touched nothing else in it**, on the supervisor's order and with no other change.

**The condition rule 2 requires, named and checked.** This is a **pre-compute** amendment: the run
root **`/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic` DOES NOT EXIST**, verified at
**2026-08-27T19:41:01Z**; `verification/queue/runner.log` carries **zero** D18 mentions;
`verification/queue/dafoam/D18_chain.json` is still on the drop path and **not** in `launched/`.
No container has started and no gate has closed.

### A.1 THE DEFECT — a citation that makes the reader infer the identifier's type

§0 line 3 reads ``NONCONVERGENCE_STANDARD.md (`7ffd6c73`)`` and §8's heading at line 97 reads the
same. **A bare hex string in parentheses does not say what kind of identifier it is.** The same file
has **three** identifiers and only one of them is that one:

| identifier | value | what it names |
|---|---|---|
| **commit** | **`7ffd6c7386e76b54572714378ab12d975fa518a1`** | the revision — **this is the one cited, and the one that governs** |
| blob id | `d553b963b4a727b894729a5d793bedd07c83820d` | the file's bytes, as git names them |
| content sha256 | `14d72954cbe853ae859c083417963758985181391484fd5da08b3ded86e08885` | the file's bytes, as `sha256sum` names them |

**Both original citations are STRUCK and superseded by this section. They are left byte-identical on
the page rather than edited**, because frozen files are never edited in place and other records cite
documents here by line; the strike is recorded here, not applied above.

### A.2 THE CORRECTION, AND ITS SEVERITY STATED HONESTLY RATHER THAN INFLATED

**`7ffd6c73` is a COMMIT.** Verified independently by lane C, not accepted on relay:
`git cat-file -t 7ffd6c73` returns **`commit`**, and
`git log --diff-filter=A -- docs/standards/NONCONVERGENCE_STANDARD.md` returns **that same commit**,
so it is the commit that *landed* the standard. **The commit is the right thing to cite here**,
because what this document points at is the standard's **text at that revision**, and only a commit
makes that text recoverable.

**Nothing was at risk and no freeze integrity is touched.** Eight hex characters cannot be a sha256;
the reference resolves correctly as a commit; and neither §0 nor §8 uses it as an integrity check —
it is a pointer to a standard's text. **This is not a freeze-integrity failure and is not to be
written up as one.** It is worth a one-line fix on a document that has spent zero compute because
this family was bitten today by one notch worse: two commits sharing a subject 52 s apart, where the
wrong one resolved to a real commit and failed only at the path check (`VERIFICATION_CHARTER` v1.12).

**One measurement that bounds the exposure exactly.** The blob at `7ffd6c73` is
`d553b963b4a727b894729a5d793bedd07c83820d` and the blob at HEAD is **the same** — the standard's
text has not changed since it landed. **So the ambiguity currently resolves to identical bytes
whichever identifier a reader reached for. That is true today and is not a property anyone may rely
on tomorrow**, which is the whole reason to fix the form now rather than after the text moves.

### A.3 THE CLASS IS CLOSED HERE, NOT ONE INSTANCE OF IT

`7ffd6c73` is not the only bare hex in this document. **Every distinct 8-hex token in it was typed
by `git cat-file -t`, and all five are COMMITS:**

`068c2bf0` · `2d8796e3` · `7ffd6c73` · `bc0e687e` · `d4d0c29d` — **commit, all of them.**

**Every bare hex on this page names a commit.** Naming them explicitly is what stops the ambiguity
recurring by someone later "correcting" a commit id into a digest.

### A.4 WHAT THIS ADDENDUM DOES NOT TOUCH

**No gate, threshold, band, cap, label, verdict mapping, prediction, cost, cpuset, image or arm
moves.** §2's registered delta, §7's scope, §8's anti-gaming carriage, the 182.2 core-min estimate,
the 785.0 cap, `ranks 2`, `memory_floor_gb 12.0` and `d18_grade.py` md5
`e4ade11ed9e3db18d2c4988b30e929b4` all stand exactly as frozen at
`dae3dc9d17dab4ecda7d44e30c9a3016637f9987`, which remains this document's freeze. Nothing was sent
anywhere; **submissions remain parked.**
