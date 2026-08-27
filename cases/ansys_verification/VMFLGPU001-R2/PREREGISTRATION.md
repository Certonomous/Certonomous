# VMFLGPU001-R2 — PRE-REGISTRATION (frozen before compute)

**Case:** the lab's GPU solver path on flow between rotating and stationary
concentric cylinders (Taylor–Couette Couette flow), Ansys Fluid Dynamics
Verification Manual, Release 2026 R1, **p. 225**. CPU parent VMFL001 / VMFL001-R2.
**Drafted by `ansys-lane-opus48` (lane H), 2026-08-27, for the supervisor to freeze.**
Prediction-first, frozen by sha before any solver runs (CLAUDE.md rule 2).

**Comparator (frozen grading path):** `grade_vmflgpu001_r2.py`, blob **`6a5d0fe7`**
(committed in the freeze commit; the launcher verifies on-disk == HEAD before any solve).
**Launcher:** `run_vmflgpu001_r2.sh`. **Case inputs:** `case/` (byte-identical to R1).

---

## 1. Why R2 exists — a successor to a REFUSAL, not a second attempt at a number

VMFLGPU001 (R1), **register row #33**, is `NOT A RESULT`: R1's FROZEN plateau clause I5
refused, verbatim:

> REFUSE (VMFLGPU001 I5): L1_16x64: the plateau window has NULL RANGE (peak-to-peak
> exactly 0 over 600 samples). A dead field and a perfectly converged one look identical
> to a tolerance (Amendment 4 item 4).

The refusal was correct behaviour of the frozen clause on a **perfectly converged** channel:
the L1 probe (v_theta at r = 35 mm) rose from 1.86e-16 to 4.639246e-03 m/s and then went
bit-identical for its final 1662 iterations. A peak-to-peak test over the last window cannot
tell that live-and-converged channel from a dead one, so R1's clause refused rather than guess.

**Sanaa's 2026-08-27 §3 anti-gaming clause is the highest authority on why R1 stands and why
R2 is a FRESH REGISTRATION:** *"Frozen gates never edited post-compute"* and *"Converged-but-wrong
= NOT HELD with diagnosis, never a parameter hunt."* R1's I5 liveness could be established only
by reading R1's own run values, so amending R1 would be a change justified by the answer — the
bright line. R2 therefore re-registers the case from scratch, before any R2 compute, changing
**only the controls**.

## 2. GATE-IDENTICAL to R1 — the diff is EMPTY everywhere except the controls

Every gate-determining constant is **byte-identical to R1** (the launcher hashes the case
inputs; the comparator carries the same constants):

| gate element | value (identical to R1) |
|---|---|
| reference | EXACT analytical Taylor–Couette `v_theta(r) = omega·R_i²(R_o²−r²)/(r(R_o²−R_i²))` (White §3-2.3) |
| gate quantity | v_theta sampled at r = 20/25/30/35 mm |
| limb C band | 0.02 (2 %) at the finest level |
| limb B band | 1e-4 (GPU == forced-CPU) |
| tier ceiling | `GATE REACHED` (exact ref buys V never P; comparator cannot print `PASS`) |
| mesh family | 16x64 / 32x128 / 64x256 (r = 2) |
| endTime | 3000 / 3000 / 6000 |
| cap | 2.0 GPU-h; CPU-arm 40 core-min |
| P_MIN floor | 0.05 |

**What moved, and ONLY this:** (a) the plateau control gets a liveness floor (§3), and (b)
limb A's GPU tell is re-based (§4). Both are CONTROLS/READERS, not the gate — no limb, band,
threshold, cap or label moves. R1's answer is on disk (row #33), so any change to a
gate-determining constant would be gate-fitting; none is made.

## 3. THE ONE SUBSTANTIVE CHANGE — the liveness plateau control

**Registered NUMBER, before compute:** `LIVENESS_FLOOR = 0.1 × |v_exact(0.035)| =
4.547810e-04 m/s`. **Derived from the PHYSICS, not from R1's measured range.** The probe
channel is v_theta at r = 35 mm; the initial field is at rest (v_theta = 0) and a correct
solve MUST traverse to the exact analytic value 4.547810e-03 m/s. The floor is 10 % of that
exact value. It is deliberately NOT R1's measured 4.639e-3 m/s (that would be fitting the
control to the answer). A dead channel (full-history range 0) fails; the real solve
(range ~4.5e-3) clears it ~10×; a barely-moved channel fails.

**The clause:** plateau holds when the last-window peak-to-peak `< PLATEAU_TOL` (1e-6, unchanged)
**AND** the full-history range `≥ LIVENESS_FLOOR`. A NULL last-window range (ptp = 0) is no longer
refused when the channel is demonstrably live — that is a perfectly converged double-precision
fixed point, exactly what R1's I5 over-refused.

**Strictly stronger where it must be, driven both ways in `--selftest`:**
- `--drive-refusal dead-channel`: a channel bit-identical from the start (full-history range 0)
  **REFUSES** on the liveness floor. R2 still catches a dead channel.
- `--drive-verdict live-converged`: a channel that rose to `v_exact` then went bit-identical
  (null last-window range, full-history range above the floor) **GRADES to `GATE REACHED`**.
  R2 resolves R1's I5 over-refusal.

## 4. THE OTHER CONTROL CHANGE — limb-A GPU tell re-based (VMFLGPU002 Amendment 5, applied fresh)

R1's `tell1` matched PETSc's arm-independent `-log_view` legend (fires on the forced-CPU arm too
on a CUDA build) and `tell3` expected a `type: aijcusparse` ksp_view line this build echoes only
in the options block — both miscalibrated for this build. R2's limb A reads the GENUINE
discriminator: PETSc's **GPU %F table VALUE** (the last field of a `-log_view` event row), 0 on a
CPU solve and > 0 on a GPU one. `tell2` (a PID holding device memory) is kept; `tell3` is dropped
from the conjunction. The forced-CPU control refuses only on genuine device work in the control
arm. Limb A's MEANING is unchanged. **Driven:** `--drive-refusal gpu-zero-pctf` forges a GPU-arm
log that is cusparse-typed with the legend present (so R1's loose tells would fire) but with
GPU %F = 0 on every event row, and it **REFUSES**.

## 5. L-342 FIELD SPLIT and R-RC (Sanaa 2026-08-27), declared

**PHYSICS-CRITICAL (a failure refuses or votes NOT A RESULT):** rc VALUE (`rc != 0` refuses);
the `End` line; `Time =`-line count == endTime; the fields at endTime; the age guard; the
residual clause; the liveness+plateau clause; limb A's three-limb discrimination; the planted-zero
control; the mass/torque-free reference arithmetic.

**INFRASTRUCTURE (reported, never refuses):** the `ExecutionTime`-line count (petsc4Foam prints
endTime + 2 — two init timing lines inside `Time = 1`); COST.txt and every GPU-hour / core-minute
figure; LAUNCH_RECORD.txt's non-sha bookkeeping; contention/status files; pids/sids/mtimes.

**R-RC as an explicit conjunction (Sanaa's desk ruling):** an absent or unreadable RUN_RC record
is INFRASTRUCTURE and gives rc = **NOT MEASURED** (the level cannot be a PASS; the caller votes
NOT A RESULT) **ONLY WHEN** the other four rule-4 conditions (End line, last Time == endTime,
fields at endTime, age guard) all hold. If any of those is ALSO missing, completion **REFUSES**;
a missing rc record never becomes a blanket pass. **Driven:** `--drive-refusal norc-noend` removes
the rc record AND the End line and the comparator **REFUSES** (C4).

## 6. PLANTED-ZERO CONTROL — plant at the row the reader actually selects (L-347)

The gate is four POINT readers — v_theta at r = 20/25/30/35 mm from the sampled set file — so the
plant-to-read mapping is 1:1 (`PLANT = 1.234e-3` m/s planted at each radius reads back exactly
PLANT, no averaging dilution). The plant is placed at the RADIUS ROW the reader selects, not at an
arbitrary first row (the VMFL011 L-347 failure). Every channel's control executes before any exit,
and the negative arm (an unplanted copy sees 0 move) and the blind-reader refusal are both driven.
The plant is supra-threshold on the smallest gated channel (`PLANT / v(35 mm) > 0.1`).

## 7. COST (CLAUDE.md rule 12) — from the measured 0.4417 GPU-h, with real headroom

- **Estimate:** **0.44 GPU-h** for the whole case (both arms), from R1's **measured 0.441667
  GPU-h** (register row #33). CPU arm ~9.2 core-min (R1 measured 9.15).
- **Cap:** **2.0 GPU-h** ENFORCED by `timeout` in the launcher — **~4.5× headroom** over the
  estimate (R1 used 22 % of it; not a tight cap — VMFLGPU002 came within 10.3 % of its cap and
  that is not repeated here). CPU-arm cap **40 core-min** (R1 used 23 %). An overrun stops the run.
- **$ derived:** 0.441667 GPU-h × $0.8048/GPU-h = **$0.3555**, DERIVED not measured (published-list
  rate, g6.xlarge us-east-2; `COMPUTE_BUDGET_CHARTER.md` §5); console figure owed.

## 8. EVERY GUARD DRIVEN, not read (Sanaa §1 / L-314) — the selftest mutation table

`grade_vmflgpu001_r2.py --selftest` is **43 checks GREEN**, byte-identical under `python3` and
`python3 -O`, **zero `ast.Assert` nodes**. Each guard ships a planted-failure proof:

| guard | driven mutation | must |
|---|---|---|
| liveness floor (dead channel) | `dead-channel` (full-history range 0) | REFUSE |
| liveness (converged live) | `live-converged` (null last window, live) | GRADE to GATE REACHED |
| plateau min samples | `short-plateau` | REFUSE |
| limb A GPU tell | `gpu-zero-pctf` (GPU %F = 0, legend present) | REFUSE |
| limb A missing tells | `limbA-miss` | NOT A RESULT, exit 2 |
| forced-CPU control leak | `control-leak` | REFUSE |
| completion End line | `endline` | REFUSE |
| completion Time count | `time-count-short` | REFUSE (C7) |
| R-RC conjunction | `norc-noend` (rc + End gone) | REFUSE (C4) |
| age guard | `age-guard` | REFUSE |
| planted zero | `plant-blind` + negative arm | REFUSE / see 0 move |
| verdict vocabulary | `vocabulary` under -O | REFUSE |
| P_MIN / STAGNANT / limb-C routing | `below-p-min` / `stagnant-triple` / `limbC-miss` | NOT A RESULT / GATE FAIL |
| petsc4Foam log shape (endTime+2) | `petsc-exec-shape` | GRADE + print INFRA note |

## 9. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and only these
(rule 1). **This rung is `PENDING` until the comparator has graded a completed R2 run.** PASS is
unreachable (exact reference; ceiling GATE REACHED). Enqueueing is not authorisation; the freeze
is committed before any solver runs and the supervisor verifies the commit personally.

---

## PRE-COMPUTE AMENDMENT 1 — 2026-08-27 — the freeze check is bound to the tree it launches from

**Version 1.1.** Appended at the foot. **Nothing above this section is rewritten, edited
or struck** — not §1–§9, not one gate constant. **Lines whose number changed above this
section: 0**, verified by hashing the frozen blob `8e4de9bd3f65fa43e4a1a3bc463f840a27ea9c49`
as an exact byte prefix of this file, not merely asserted. Drafted by `ansys-lane-opus`
(lane R2) for the supervisor's `SUPERVISION_CHARTER` §3 check 4.

**This is a PRE-COMPUTE amendment under CLAUDE.md rule 2**, which requires it to *state the
condition and how it was checked*. It does both, below, before anything else.

### 1. THE CONDITION: this case has had NO COMPUTE, and here is how that was checked

**The condition:** no solver of VMFLGPU001-R2 has ever started; zero core-minutes and zero
GPU-seconds have been spent against this freeze; no field, no log and no arm directory of
this case exists anywhere.

**How it was checked — measured on the GPU instance (ip-172-31-44-162, 3.15.199.152) by
this lane, 2026-08-27T18:3xZ, not taken on report:** the case's run root
`/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFLGPU001-R2/` holds
**exactly two files and no directories**. `find` on that root returns three lines — the root
itself and:

| entry | bytes | mtime |
|---|---|---|
| `STATUS.VMFLGPU001-R2` | 93 | 2026-08-27 18:09 |
| `launcher.queue.out` | 666 | 2026-08-27 18:09 |

There is **no arm directory** (`gpu/`, `cpu/`), **no level directory** (`L1_16x64`,
`L2_32x128`, `L3_64x256`), **no time directory**, **no `LAUNCH_RECORD.txt`**, **no
`COST.txt`**, **no `RUN_RC.*`**, **no `log.*`** — none of the artifacts the launcher writes
after its freeze check. `STATUS.VMFLGPU001-R2` reads `launcher_rc=1`, and the wrapper output
carries the abort verbatim:

> `[2026-08-27T18:09:24Z] VMFLGPU001-R2: ABORT: cases/ansys_verification/VMFLGPU001-R2/PREREGISTRATION.md is not committed at HEAD -- the freeze is the evidence`

**What makes this unambiguous rather than merely suggestive:** in the frozen launcher
`c75076be` the statement `mkdir -p "$RUN_ROOT"` is at **line 216**, and the freeze check that
aborted is at **lines 199–211** — the `mkdir` sits *after* the check. **The launcher therefore
created nothing at all**; the run root and its two files were created by `queue_runner.py`
(which chdirs into the cwd and tees the wrapper output there) before the launcher was execed.
Every artifact this case's launcher would ever write is absent because the launcher exited
before writing its first one. Elapsed from START to abort: **one second** (18:09:23Z →
18:09:24Z), which is not a solve.

**Consequence:** gates are still open (rule 2), and this amendment is legal. Had any solver
output been found, this document would have taken a dated post-compute addendum under
`VERIFICATION_CHARTER` §2d.1 instead, and it does not.

### 2. WHAT THIS AMENDMENT MOVES: nothing that could change an answer

**NO limb, NO band, NO threshold, NO cap, NO label, NO reference, NO mesh family, NO
endTime, NO tolerance and NO verdict ceiling is moved by this amendment.** Every constant in
§2's gate-identity table stands byte-for-byte: limb C band 0.02, limb B band 1e-4, tier
ceiling `GATE REACHED`, mesh family 16x64 / 32x128 / 64x256, endTimes 3000 / 3000 / 6000,
cap 2.0 GPU-h and 40 core-min, `P_MIN` 0.05, `LIVENESS_FLOOR` as registered in §3. The
comparator `grade_vmflgpu001_r2.py` is **NOT TOUCHED**: its blob is
`6a5d0fe7b68e5f184edb97114a2dae31dcf7512c` before this amendment and
`6a5d0fe7b68e5f184edb97114a2dae31dcf7512c` after it. The case inputs under `case/` are not
touched. **The only file whose bytes change is the LAUNCHER**, and only in its launch-time
freeze check.

**Launcher blob transition, recorded as VMFLGPU002's Amendment 5 recorded its comparator
move (`8172a0d3` → `92a82426`):**

| file | blob BEFORE | blob AFTER |
|---|---|---|
| `run_vmflgpu001_r2.sh` | **`c75076be3aa1d83ea8e67145c25ad43141d926cb`** | **`dd657f9addb7f93bdf79768ab09bce2a0ead44bb`** |
| `PREREGISTRATION.md` | `8e4de9bd3f65fa43e4a1a3bc463f840a27ea9c49` | *(this file, with this amendment appended; the old blob is its exact prefix)* |
| `grade_vmflgpu001_r2.py` | `6a5d0fe7b68e5f184edb97114a2dae31dcf7512c` | `6a5d0fe7b68e5f184edb97114a2dae31dcf7512c` — **UNCHANGED** |

### 3. THE DEFECT, named exactly

The frozen launcher took its **case inputs** from `SCRIPT_DIR` (line 99–100) and proved its
**freeze** against `REPO="${REPO:-$HOME/Certonomous}"` (line 103). Those are two INDEPENDENT
paths, and that independence has two consequences:

1. **The loud one, which fired at 18:09:23Z.** The runner invoked the launcher out of an
   isolated checkout with `REPO` unset, so `REPO` fell back to the instance's *shared* clone
   at HEAD `8dfb4598`, which predates the freeze commit `1614f86f`. The guard aborted at zero
   compute. **The guard was right and the invocation was wrong** — this is a launch defect,
   not a gate defect, which is exactly why no gate moves here.
2. **The silent one, which is the one that matters.** Because the two paths are independent,
   the check **can PASS while proving nothing about the case that runs**: point `REPO` at any
   repository that happens to carry the three blobs, run the script out of a completely
   different tree, and `FREEZE VERIFIED` prints over unverified inputs. VMFLGPU003's launch
   was correct **only by coincidence** — its entry happened to set `REPO` to the same tree its
   `SCRIPT_DIR` sat in. **A freeze check that can certify the wrong tree is not a freeze
   check**, and under rule 2 the freeze is *the document's entire evidentiary content*.

### 4. THE REPAIR — four clauses, each of which ABORTS

The repair is confined to the launcher's STEP 1 and to the two lines that fed it. In the
amended launcher, `REPO` is **derived, never accepted**:

- **(a) `REPO` is derived from `SCRIPT_DIR`.** `REPO="$(git -C "$SCRIPT_DIR" rev-parse
  --show-toplevel)"`, with an **ABORT** if `SCRIPT_DIR` is not inside a git worktree, if the
  toplevel comes back empty, or if either path fails to resolve under `cd … && pwd -P`.
- **(b) `SCRIPT_DIR` must BE `$REPO/cases/ansys_verification/VMFLGPU001-R2`**, both resolved
  with `cd … && pwd -P` and compared as strings; **ABORT** otherwise. **This is the clause
  that closes the silent defect**: it makes it impossible for the certified blobs to belong to
  a different tree than the case inputs.
- **(c) A caller's `REPO` is neither silently ignored nor silently honoured.** If the
  environment sets `REPO`, it is captured as `REPO_ENV` and **ABORTS** unless it resolves
  (`pwd -P`) to the derived toplevel. An environment variable is a *claim* about which tree
  the run is against; a claim that disagrees with the derived truth is a launch built on a
  misunderstanding.
- **(d) The launcher is added as a THIRD freeze-checked path.** `HEAD:run_vmflgpu001_r2.sh`
  must exist and its `hash-object` on disk must equal it, exactly as the pre-registration and
  the comparator already do. **A launcher that verifies everything except itself is the same
  hole one level up** — the guards in (a)–(c) and the `timeout` cap are only evidence if they
  are the committed bytes. The three pre-existing checks (`cat-file -e HEAD:<prereg>`,
  `cat-file -e HEAD:<grader>`, disk-hash == HEAD-blob for both) are **kept unchanged**.

**`LAUNCH_RECORD.txt` is extended** with `script_dir`, `repo_toplevel_derived`,
`repo_env_as_passed`, `launcher`, `launcher_sha_head` and `launcher_sha_disk` beside the
existing `head` / prereg / comparator shas, so the record names the tree as well as the blobs.
The `FREEZE VERIFIED` line now prints the launcher blob too, and is still printed **inside**
the branch that verified it (PREREG_TEMPLATE Amendment 6a item 1).

### 5. EVERY NEW CLAUSE DRIVEN, not read (Sanaa §1 / L-314)

A guard nobody drove is decoration. Each of the four clauses was **planted-failed and shown
to ABORT**, and the clean control was shown to PASS, in a disposable sandbox git repository
holding the post-amendment bytes. The transcript, the exact abort strings, the fixture layout
and the reproduction command are recorded **beside this case**, not in scratch (L-186,
L-351), at:

`cases/ansys_verification/VMFLGPU001-R2/AMENDMENT1_FREEZE_GUARD_DRIVE.txt`

No solver ran in that drive: the control PASSES the freeze check, writes its
`LAUNCH_RECORD.txt`, and then stops at STEP 2's `OF_BASHRC` abort, which is the first step
after the freeze check and is reached at zero compute.

### 6. WHAT THIS AMENDMENT DOES NOT DO

- It does not re-open, widen or narrow any gate; §2's table is the gate and it is untouched.
- It does not authorise a launch. **Enqueueing is not authorisation** (§9;
  `QUEUE_ENTRY_STANDARD.md` §1), and `SUPERVISION_CHARTER` §3 check 4 — the pre-registration
  **committed** before compute — is the supervisor's own and is not discharged by this
  document, by a queue entry, or by any lane's report.
- It does not touch the instance's shared clone `/home/ubuntu/Certonomous`, which is under a
  standing hold (defect D-ANSYS-GPUCLONE): no pull, fetch, checkout, reset, stash or clean.
- It claims nothing about Ansys, nothing about GPU performance, and no verdict. **This rung
  remains `PENDING`.**

### 7. RECORDED, NOT REPAIRED — the launcher's FIELD COMPLETENESS check passes VACUOUSLY

**Plain record, moving no limb, band, threshold, cap or label.** The frozen launcher
`c75076be3aa1d83ea8e67145c25ad43141d926cb` contains a FIELD COMPLETENESS check.
**Measured by the supervisor personally, 2026-08-27, against that frozen blob and this case's
frozen `case/`, it prints `FIELD COMPLETENESS OK: closure=laminar required={} all present in
0/`** — an empty required set. **It gates nothing on VMFLGPU001-R2.**

**The cause, and the inherited explanation is WRONG.** The board's standing explanation was
that the parser cannot see `p` and `U` through the nested `petsc { options { … } }` blocks.
It can; the depth tracking handles that nesting correctly and always did. The supervisor's
discriminating pair, run on the frozen `fvSolution`: **(A)** nesting KEPT but the key and its
opening brace put on ONE line (`p {`) → `required={U, p}`, **the guard works**; **(B)**
nesting REMOVED entirely with the key left on its own line → `required={}`, **the guard still
fails**. The defect is the parser's final loop line, `if ch in ";\n" and depth == 0: tok = ""`,
which **clears the accumulated key name at the newline BETWEEN the key and its opening
brace**. OpenFOAM's standard style puts the key on its own line, so no key is ever captured.

**Consequence for this case, stated so it cannot be cited wrongly: the FIELD COMPLETENESS
line in this case's launcher output is NOT EVIDENCE about VMFLGPU001-R2 and must never be
cited as any** — not in the RESULTS record, not in the register row, not in a cost or
completion claim. It is not one of the rule-4 completion clauses, which are enforced by the
comparator against the run tree and are untouched here.

**It is left in place UNREPAIRED, deliberately.** This is a pre-compute amendment confined to
the freeze check. Every clause added to a launcher is a new way to abort at zero compute, and
this family has already burned launches on guards that refused; the vacuous guard gates no
verdict, so leaving it costs no evidence *provided it is never cited as any*, which the
paragraph above forecloses. The repair is the supervisor's, separately routed, and this lane
did not touch it.
