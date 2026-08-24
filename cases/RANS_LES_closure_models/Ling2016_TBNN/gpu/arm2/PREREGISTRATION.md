STATUS: **FROZEN — 2026-08-24T16:27:45Z.** Committed ALONE before any compute; this file's
sha256 is in its commit message. The instance is STOPPED at freeze; it is
started by Sanaa on the chief's request only, and nothing runs before this
commit lands.

# PREREGISTRATION — Ling, Kurzawski & Templeton (2016) TBNN, GPU arm 2: matched update count

Written 2026-08-24T16:27:45Z by the closure supervisor. **Zero compute was spent writing it.**
Authorised under Sanaa's rulings of 2026-08-24, verbatim (chief's session
record): *"2. Good for the dispatched work, i approve of everything"* — read
as approval of this dispatched item **with its own costing still required**
(rule 9: a blanket is not a per-item read; §6 is that read) — and *"1. GPU
shutdown suggestion: yes approved (also i stopped that instance)"*.

Companion to arm 1 (`PREREGISTRATION.md`, frozen `e8309b6c`; `RESULTS.md`,
**NOT A RESULT**, commit `353925c7`) and to the CPU lane (`../PREREGISTRATION.md`,
`../RESULTS.md`, GATE REACHED). Nothing in those three is re-opened, re-scored
or amended. **VARIANT** (Charter §9): none of Ling's nine flows is on this box.

---

## 1. Why this arm exists — one paragraph

Arm 1 registered "Ling's own optimiser" as plain SGD at the paper's rate
(2.5e-7) **at full batch** — one update per epoch, chosen to fit the GPU cost
estimate — and the TBNN did not move in 200,000 updates. The paper updated
**after each training point** (sidecar `Ling2016_tbnn_embedded_invariance.txt`
l.131–132: *"stochastic gradient descent was used, in which the weights were
updated after each training point"*): **342,014 updates per epoch** on this
training set (v1's training mask; §10.1), ~3.4e5× arm 1's. Arm 1's falsifier therefore fired on the wrong
question (arm 1 `RESULTS.md` D-1; L-267). This arm runs the paper's actual
regime — batch size 1, the paper's rate, no scaling — and settles departure D3
either way.

## 2. THE CLAIM

> **Per-point SGD at Ling's stated learning rate trains the 8×30 TBNN on this
> data within a costed update budget, to a validation error within the CPU
> lane's Adam-trained seed band.**

If it does, D3 (the optimiser) was the reason the CPU lane needed Adam, and
arm 1's full batch was the confound. If it does not, the paper's own regime is
inert on this data at this budget, and D3 is closed as *not the cause*.

## 3. Arms, seeds, budget — and why the epoch count is decided by P0

| arm | model | optimiser | updates/epoch | seeds |
|---|---|---|---|---|
| **A2-TBNN** | 5 → 8×30 LeakyReLU(0.01) → 10, merged with the 10 basis tensors; CPU-lane preprocessing (D4, D5) | plain SGD, lr **2.5e-7**, **batch 1**, per-sample squared-Frobenius loss (no batch mean) | 342,014 (a full permutation of the TRAIN rows per epoch) | 0, 1, 2 |
| **A2-MLP** (control) | 5 → 10×10 → 6 components → symmetric traceless | plain SGD, lr **2.5e-6**, batch 1 | 342,014 | 0, 1, 2 |

**Epoch budget `E` is registered as a rule, not a number**, because the
per-update cost of a launch-bound batch-1 step on the L4 has never been measured
here and is the entire cost. `E_TARGET = 300`, `E_MIN = 50`:

```
P0 (first thing after G0, inside the frozen run):
  time 20,000 per-point updates after warm-up      -> s_per_update
  epoch_s(model) = 342,014 x s_per_stacked_update + measured val-eval cost per epoch
                   (one stacked update advances all three seeds; §10.2)
  E = min( E_TARGET, floor( 0.8 x (CAP_H - spent) x 3600 / (epoch_s_tbnn + epoch_s_mlp) ) )
  E < E_MIN  ->  BLOCKED (written with the numbers), then the shutdown stage
```

`E` is written into `status_p0.json` before the first training update and is
the same for all six runs. Three seeds, not five, because the budget buys
epochs with them; the seed spread is reported as max − min over three.

**Two P0 controls, both refusals (BLOCKED, exit 3, then shutdown):**
(i) if CUDA-graph capture is used for the step, 1,000 updates from one seed in
graph mode and in eager mode must agree on every parameter to **1e-6 relative**;
(ii) the SGD semantics control: one update from a known state must equal
`theta − lr·grad(loss_i)` to 1e-6 relative, computed independently in eager
float64 on the lab box for the same sample (a reader shown to see a wrong step).

**Update-count target on record:** `E × 342,014` per run; at `E = 300` that is
**1.026e8 updates** — 513× arm 1's 200,000.

## 4. Gates, with thresholds (verdict vocabulary: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING)

Scoring cells: `valid` ∧ finite `b_LES` ∧ finite `b_RANS` (arm 1's F.5(4); 152,520
TEST cells, 114 dropped). Per-case `b_rms` = RMS of `‖b_pred − b_LES‖_F`.
**`NASA_2DWMH` is registered as the out-of-training-range TEST case** (FS5/D476:
9.596 % of its cells above the training unclipped `q1_wallRe` max; D484) and is
**split out in every pooled reading**: every pooled figure is reported twice —
8-case, and **in-family (7 cases)** — and the NASA row stands alone beside them.
No 8-case pooled figure may carry a verdict on its own where an in-family
companion is registered below.

**G0 — planted-zero controls. Run first; refusal → NOT A RESULT for the arm.**
As arm 1: `PLANT = 1.234e-03` into `b_LES[k,0,1]` and `[k,1,0]` of a named cell
in a copy, read back through the `b_rms` scorer within **1e-9** relative via the
single-cell contribution; a cell forced to `diag(1,1,−2)` flagged by the
realisability reader. Plus the two P0 controls of §3. Plus the **comparator
witness**: the comparator writes its own file sha256, the dataset sha256 and
every prediction file's sha256 into its JSON (closing arm 1's D-5); a JSON
without them is refused at grading.

**G1 — A2-TBNN a-priori, per case (8 cases).** Best-val prediction, mean over 3
seeds: below SST, below `b = 0`, below the train-mean tensor on **≥ 6 of 8**
TEST cases → **PASS**; 4–5 → **GATE FAIL**; ≤ 3, **or failure to beat `b = 0`
on any case** → **NOT A RESULT**. The in-family 7-case count is reported beside
it; it does not replace it.

**G2 — the invariance embedding, in-family.** A2-TBNN **in-family pooled**
`b_rms` (7 cases) below A2-MLP's in-family pooled by **more than the larger of
the two seed spreads** → **PASS**; else **GATE FAIL**. The 8-case pooled figures
and the NASA row are reported beside; **G2 is not graded on the 8-case pooled
figure** — arm 1 measured that a single out-of-range case moves it by seven
orders (arm 1 §2), which §8 of arm 1 had anticipated in words and this file
registers in the gate.

**G3 — realisability, per case (Charter §4 applied on each case's own cells).**
For every TEST case, every model: violation fraction ≤ **3×** that case's own
truth violation fraction, **and** `max ‖b‖_F` ≤ **1.633** (= 2·√(2/3)). A case
failing either clause is **NOT A RESULT for that case**, named. The arm's G3 is
**PASS** if **at most one** of the 8 cases is NOT A RESULT (the registered
expectation is that `NASA_2DWMH` is that case), **NOT A RESULT** if two or more
are. The Charter-§4 pooled figure over all TEST cells is reported beside the
per-case table, and the per-case truth fractions are printed (arm 1 measured
truth 0.79 % pooled; SST 0.10 %; the ducts' own truth fractions are not yet on
record and are what this table adds).

**G4 — a-posteriori, CPU, on the G3-passing cases.** Runs only if G3 is PASS.
The best A2-TBNN seed's `b` propagated through `simpleFoam` (OpenFOAM v2606) on
each G3-passing TEST case, scored against the LES fields with RMS `div(U)`
reported (Charter §7, floor 10.5 %); Charter §22.4 model-form band shipped with
every prediction, axis named, never applied as a correction. Velocity error
below the frozen-field ceiling on **all but at most one** of the propagated
cases → **PASS**; on at least half → **GATE FAIL**; fewer, or non-convergence
on more than one case → **NOT A RESULT**. **Not run → the arm's verdict is capped
at GATE REACHED.** Cost: 7 propagations at R4's measured 0.259 core-h/case =
**1.81 core-h = $0.093 derived** at $0.0513/core-h (CPU blanket; costed here).

**Order of combination.** G0 refusal → NOT A RESULT, stop. Then G1; then G2 and
G3 read independently; the arm's verdict is the worst of {G1, G2, G3} in the
order NOT A RESULT > GATE FAIL > PASS, with G4 lifting a PASS/PASS/PASS to the
final PASS only if it runs and passes. BLOCKED at P0 or at the cap is BLOCKED.

## 5. The falsifier, pre-stated with numbers

Let `v_A2` = the best validation `b_rms` reached by A2-TBNN (mean over seeds)
within budget `E`. The CPU lane's Adam-trained 8×30: `v_CPU = 0.1646 ± 0.0073`
(`../train_log.json`, five seeds). Arm 1's SGD-full-batch MLP control: 0.30–0.37.

* `v_A2 ≤ 0.1646 + 0.0073 = 0.1719` → **D3 confirmed as the cause**: the paper's
  regime trains the TBNN here; arm 1's full batch was the confound.
* `v_A2 ≥ 0.30` (not better than the arm-1 MLP control's band) → **D3 refuted**:
  the paper's own regime is inert on this data at `E × 342,014` updates; the
  CPU lane's Adam was necessary, not a departure to apologise for.
* `0.1719 < v_A2 < 0.30` → **indeterminate at this budget**, reported as such
  with the loss slope over the last 20 % of updates, and no claim about D3.

A second registered reading, because arm 1's verdict turned on it: **if A2-TBNN
passes G1 and G2 and still fails G3 on two or more cases**, the invariance
embedding is confirmed to buy accuracy and not realisability under the paper's
own optimiser, and Charter §4's gate — not RMSE — is what stands between this
model class and a PASS.

## 6. Compute — costed before launch, with the arithmetic shown

Rate **$0.8048/GPU-h** (`g6.xlarge` on-demand, us-east-2, published price list
retrieved 2026-08-23; `docs/GPU_CAPABILITY_STATE.md` §9). Dollars **derived,
not measured**. GPU-hours = the driver's stage wall-seconds (`spend.json`),
as arm 1.

**The per-update time is unmeasured and sets everything.** Arm 1's P0 measured
**18.645 ms per full-batch epoch** — one launch round over the 342,014 training rows. A batch-1
round is launch-bound; its cost is PyTorch's per-step overhead, not FLOPs.
Registered assumption range, stated as one, per STACKED update (all three
seeds): **0.05 ms (CUDA-graph replay) to 1.0 ms (eager).** Lab-box CPU smoke
measurement on a 2,000-row subset (eager, 4 threads, no GPU): **0.54 ms per
stacked update (TBNN), 0.55 ms (MLP) = 0.18 ms per seed-update; ~190 s/epoch
per model** — an upper-bound hint for the eager path, not a GPU figure.

```
epoch_s(model)   = 342,014 x s_per_stacked_update   = 17 s (0.05 ms)  to  342 s (1.0 ms)
both models                                          = 34 s            to  684 s
E = 300 epochs                                       = 2.9 GPU-h       to  57 GPU-h
CAP_H = 40 GPU-h  ->  E = min(300, floor(0.8 x (40 - spent) x 3600 / epoch_s_both))
                   = 300 (fast case)  ...  168 (at 684 s/epoch)  ...  BLOCKED below E_MIN=50
                     (E_MIN = 50 is reached at 2,304 s/epoch_both = 3.4 ms per stacked update)
REGISTERED ESTIMATE  : 3 - 32 GPU-h  =  $2.41 - $25.75 derived
                       (32 = 0.8 x cap, the most P0 can allocate)
REGISTERED CAP       : 40 GPU-h  =  $32.19 derived.  Overrun stops the run;
                       BLOCKED; no new budget (rule 12).
G4 (CPU, if reached)  : 1.81 core-h = $0.093 derived, CPU blanket.
```

**Idle accounting.** The instance is started by Sanaa on the chief's request;
the launch follows within the same working session, and the interval from her
reported start to the driver's first status stamp is **waste** if she reports a
clock, **stated absent** if she does not. After completion the driver halts the
instance itself (§7); any interval between the completion marker and the halt
is reported from the marker's stamp to the last artifact mtime.

**Calibration row** (`docs/COST_CALIBRATION.md`): actual `spend.json` GPU-h vs
(a) P0's in-run projection and (b) this section's 8.5–32 range, ratio and
attribution, waste separately named — at grading, from committed records.

## 7. Self-shutdown — the standing mechanism, first use

*The driver ends with `sudo shutdown -h now` after writing its completion marker
and `spend.json`; the instance's shutdown-behaviour attribute is
VERIFY-by-Sanaa = stop; idle time between completion and halt is waste,
reported separately.* (`GPU_REPRODUCTION_PLAN.md` A1.)

Concretely: `out/COMPLETE.json` (utc, final state, spend) and `spend.json` are
flushed **before** `out/shutdown_attempt.json` is written, and that file is
written **before** the `shutdown` call; a node that is still up with
`shutdown_attempt.json` present has failed to halt, visibly. The driver refuses
`--shutdown` unless it is on the GPU node (hostname/CUDA check), so the lab-box
smoke test cannot halt this box. **Precondition — VERIFY-by-Sanaa-in-console
before start: shutdown behaviour = stop.** Until she confirms, the driver is
launched **without** `--shutdown` and the chief asks her to stop the node on my
completion report, as in arm 1.

## 8. Completion rule — a run is DONE only if all of it holds

Per run (model × seed): `status` DONE; epochs reached = `E` from
`status_p0.json`; history CSV continuous from update 0 to `E × 342,014` at the
registered 20,000-update cadence with no NaN/inf; best-val checkpoint and final
state both saved; `pred_*.npz` present with `idx` equal to the clean dataset's
TEST rows (the comparator refuses otherwise); the prediction file **newer than
`status_p0.json`**. Per batch: `COMPLETE.json` present, `spend.json` total ≤
cap. A run stopped by the cap is BLOCKED, not partial-DONE.

## 9. Grading path, fixed at this commit

| artefact | sha256 |
|---|---|
| `arm2/train_gpu_ling_v2.py` | `06d6d4a3f147c6e88d9d4db62b9af6a1b43d76baddb3464ae82d2275a5eb6543` |
| `arm2/score_gpu_ling_v2.py` (numbers only; writes its own sha) | `74aadda9aa3e6c02f543cefd6a3178f798f1ab590c6037cb95e63e50ffce6711` |
| `arm2/run_all_gpu_v2.sh` | `1404dba0133bfa7bd79e8c3a4080f4d32a492e97723aa241c34fa80c475e43c8` |
| `dataset.npz` (lab box = node, verified for arm 1) | `aad528dbd2cb35d2ac32326cc083bebd1c155fbc1439fe48362ba6b96b0b5459` |

The supervisor grades the comparator's JSON against §4; the comparator emits no
verdict. The frozen file that ran is verified by hashing against the committed
blob and the node's copy, as arm 1.

## 10. Implementation decisions ratified at freeze

Nine implementation decisions, read by the supervisor in the driver and comparator source (not relayed) and ratified; none moves a gate, threshold, seed, rate or cap:

1. **Updates per epoch are 342,014**, v1's training mask (`valid`); the scorer's 341,717 additionally drops non-finite `b_RANS`. The driver asserts the count at load and refuses otherwise. Every "341,717 updates" in §1 is read as 342,014; the ~3.4e5× ratio is unchanged.
2. **The three seeds train as a stack** (weights `(3, out, in)`, one `baddbmm` per layer). Each seed sees only its own permutation row and its own parameters, so the stacked step is exactly three independent per-point SGD steps; initialisation is v1's `make_tbnn()`/`make_mlp()` under `manual_seed(s)` per seed. **Consequence for P0:** `E = min(300, floor(0.8·(CAP − spent)·3600 / (epoch_s_tbnn + epoch_s_mlp)))` — two stacked runs cover 2 models × 3 seeds; both models are timed.
3. **CUDA-graph replay unrolls 64 steps** (a 1-step graph handles remainders; history cadence stays an exact 20,000 updates). Binding controls: graph-vs-eager and stacked-vs-v1-reference, each **1e-6 relative on every parameter after 1,000 updates, and the parameters must have moved > 1e-9** (a non-vacuous check). Lab-box CPU measurement of the second control: **3.3e-8 (TBNN), 8.4e-9 (MLP)**, movement 9e-3.
4. **TF32 disabled** so the reference and stacked paths share float32 semantics.
5. **Per-epoch permutation seeded from `(seed, epoch)`**; a restart repeats the interrupted epoch from its start.
6. **Validation `b_rms` accumulates in float64** (v1 used a float32 torch mean).
7. **`smoke` is a separate stage** that never writes `pred_*` files and refuses `--frozen`.
8. **The launcher requires an explicit `launch` subcommand**, refuses if the driver sha on the node differs from the repository copy, and takes the run-window start from the node's `date -u` in the same remote line as the `nohup`.
9. **Exit codes**: refusal 2, BLOCKED 3, unexpected error 4 — all through the shutdown stage via `finally`.

**Cap-stop semantics (supervisor's reading of the code):** the deadline is checked at each epoch end; a run stopped there is BLOCKED with no prediction file — a partial arm is graded as BLOCKED, never as a shorter DONE.

**The CPU alternative, disclosed:** the same job on this box's CPU at the measured 0.54 ms per stacked update (4 threads) is ~190 s/epoch/model → 300 epochs × 2 models ≈ 32 wall-h × 4 threads ≈ **127 core-h ≈ $6.5 derived** — inside the CPU blanket. The GPU is used because the item is approved as a GPU item, the CPU cores are the thermal lanes', and the P0 measurement is itself the lab's first per-point GPU throughput record; the CPU figure stands beside the GPU actual in the calibration row.

## 11. Departures carried forward, and what this arm removes

Carried unchanged from the CPU lane: D1 (flows), D2 (`eps = β* k ω`), D4
(signed-log1p input scaling), D5 (basis RMS rescaling), LeakyReLU(0.01).
**Removed:** the CPU lane's D3 (optimiser) — this arm runs the paper's; arm 1's
D-1 (update count) — this arm matches it. **Not repeated:** ARM-B (the search;
N-B41 stands). **New, named:** three seeds instead of five; `E` decided by P0;
graph-mode stepping if used (controlled in P0).

## 12. What this file cannot see

The per-update time on an L4 it has never measured (P0 measures it and decides
`E`); whether `E ≤ 300` is enough for a per-point regime whose epoch count the
paper never states (the falsifier's third branch exists for that); the ducts'
own truth violation fractions (the G3 table produces them); the instance's
shutdown-behaviour attribute (Sanaa's console); Ling's flows (VARIANT).
**It cannot authorise itself**: the item is approved under Sanaa's ruling 2 and
costed here; the start is hers on the chief's request.

## 13. Verdict at freeze: PENDING — nothing has been run.

---

## AMENDMENT 1 — 2026-08-24T17:26:51Z — before first compute

**Version: v1.0 (frozen `f36fbdd9`) → v1.1.** The frozen file carried no explicit
version string; its identity was the freeze stamp on line 1 and its blob sha256.
This amendment introduces explicit versioning, and v1.0 names the frozen text
above, unaltered.

**Condition, and how it was checked (rule 2, first bullet).** No run directory
exists: `/home/ubuntu/closure-data/tbnn_gpu/arm2` is **ABSENT**, checked by
`test -e` on the lab box at **2026-08-24T17:26:51Z** (the `date -u` read in the
same shell invocation as the test), and its parent
`/home/ubuntu/closure-data/tbnn_gpu/` holds only arm 1's artefacts. The GPU
instance is **STOPPED** (Sanaa, 2026-08-24: *"also i stopped that instance"*,
quoted at line 13 above); it is started by her alone. **Zero compute has been
spent on this arm.** Amendments are therefore legal here and gates are still
open — and this amendment nevertheless moves **no** gate.

Both frozen artefacts were verified identical to their committed blobs before
any edit: `PREREGISTRATION.md` disk sha256
`82cf4cbce93c68454b3ab5d26bc3949106c98d665ac57ff607ea2ce95bf8f153` == the
`f36fbdd9` blob == the HEAD blob; `run_all_gpu_v2.sh` disk sha256
`1404dba0133bfa7bd79e8c3a4080f4d32a492e97723aa241c34fa80c475e43c8` == the HEAD
blob (= the §9 registered value).

---

### Item (A) — §7's until-confirmed branch was not executable with the registered launcher

**The defect.** §7 (lines 213–216) registers a precondition and a fallback:
*"**Precondition — VERIFY-by-Sanaa-in-console before start: shutdown behaviour =
stop.** Until she confirms, the driver is launched **without** `--shutdown`"*.
The registered launcher `run_all_gpu_v2.sh` (§9, sha `1404dba0…`) hard-coded
`--frozen --shutdown` on its launch line (line 53) with no switch of any kind.
The until-confirmed branch of §7 therefore **could not be executed with the
registered launcher** — an operator obeying §7 would have had to edit a
sha-registered frozen artefact at launch time, which rule 6 forbids. This is an
internal inconsistency between two frozen artefacts of the same pre-registration,
found before first compute.

**The repair — one environment switch, nothing else functional.**
`SHUTDOWN=${SHUTDOWN:-1}` is added beside the other launcher configuration
constants. The launch line composes the token from it:

* `SHUTDOWN=1` (**default**, unchanged behaviour) → the composed launch line is
  **byte-identical** to the frozen line 53, verified by textual substitution
  against the committed blob, not by running the launcher (which would ssh).
* `SHUTDOWN=0` → the ` --shutdown` token is **omitted**; the line is otherwise
  the frozen line with exactly that token removed, and the emitted argv is
  `… --frozen --data … --out …`.

The launcher additionally **echoes which form it used** into the same launch line
that already carries the node's `date -u` stamp, as
`SHUTDOWN=1 (launched WITH --shutdown; self-shutdown ARMED)` or
`SHUTDOWN=0 (launched WITHOUT --shutdown; the stop stays Sanaa's)`, so the launch
record states whether self-shutdown was armed.

**Both launch forms are hereby registered, with the condition on each:**

| form | when it is used | consequence |
|---|---|---|
| `SHUTDOWN=1` (default) — `bash run_all_gpu_v2.sh launch` | **ONLY** once Sanaa's console reading of the instance's shutdown-behaviour attribute as **`stop`** is on the record. That reading is recorded in **`docs/GPU_CAPABILITY_STATE.md` §10, row "driver self-shutdown"** (or a later dated section of that same file, which then governs). No agent may read the attribute on her behalf; §12 already lists it among the things this file cannot see. | The driver writes `out/COMPLETE.json` and `spend.json`, then `out/shutdown_attempt.json`, then halts the node (§7). A node still up with `shutdown_attempt.json` present has visibly failed to halt. |
| `SHUTDOWN=0` | **Otherwise** — i.e. by default in the absence of that recorded console reading. This is §7's until-confirmed branch. | The driver is launched without `--shutdown`; **`out/shutdown_attempt.json` is never written**, and its absence under this form is expected, not a failure. **The stop remains Sanaa's**: the chief asks her to stop the node on the completion report, as in arm 1. The idle interval from the completion marker to her stop is **waste**, reported per §6's idle-accounting clause from the marker's stamp to the last artifact mtime. |

**§9 grading-path table — struck and replaced row** (rule 2: originals are struck,
never rewritten; the table above this section is unedited):

> ~~| `arm2/run_all_gpu_v2.sh` | `1404dba0133bfa7bd79e8c3a4080f4d32a492e97723aa241c34fa80c475e43c8` |~~
>
> **STRUCK 2026-08-24T17:26:51Z, before first compute, by this amendment.**
> **old** `1404dba0133bfa7bd79e8c3a4080f4d32a492e97723aa241c34fa80c475e43c8`
> **new** `a88aa5fbd633bbd13a7b4583442456fa8b6112ef2c275fd93d02f15f786721bd`
> **Reason:** the old file could not execute §7's registered until-confirmed
> branch (above). The new file is the registered launcher for both forms; §9's
> rule is otherwise unchanged — the frozen file that ran is still verified by
> hashing against the committed blob and the node's copy.

The other three §9 rows — `train_gpu_ling_v2.py`, `score_gpu_ling_v2.py`,
`dataset.npz` — are **unchanged**. The driver and the comparator are untouched by
this amendment.

**Disclosed deviations inside the launcher edit** (named here so the diff carries
no surprises):

1. Two **comment-only** blocks were also updated, because they stated the old
   unconditional behaviour and would have been false after the switch: the header
   paragraph describing `--shutdown`, and one added `Usage:` line showing
   `SHUTDOWN=0 bash run_all_gpu_v2.sh launch`. Neither is executable text;
   `bash -n` passes.
2. **Not changed, and flagged:** `run_window.json`'s printf schema still records
   `start_utc`, `driver`, `driver_sha256`, `node`, `remote_out` and **not** the
   shutdown form. The form is stated on the launcher's stdout launch line only.
   The on-disk launch record therefore does not by itself say which form was
   used; whoever launches must capture that stdout line into the launch record.

---

### Item (B) — §6's calibration clause named a range the section does not register

**The defect.** §6 line 183 registers
`REGISTERED ESTIMATE : 3 - 32 GPU-h = $2.41 - $25.75 derived`, while the
calibration clause at line 198 compares the actual against *"this section's
8.5–32 range"*. The two disagree on the lower bound, and **the block's own
arithmetic supports 3, not 8.5**: line 177 gives `epoch_s(both)` = 34 s at the
fast end (0.05 ms per stacked update × 342,014 × 2 models), and 34 s × 300
epochs = 10,200 s = **2.83 GPU-h ≈ 3**. The dollar figure agrees: 3 × $0.8048 =
$2.41, exactly line 183's lower bound. The upper bound 32 is independently
supported (0.8 × the 40 GPU-h cap; 32 × $0.8048 = $25.75). **8.5 derives from
nothing in the block** — no line yields it, and 8.5 × $0.8048 = $6.84 appears
nowhere in §6.

**The amendment.** The calibration comparison of §6 uses the **3 – 32 GPU-h**
range and this block's registered point/cap — i.e. actual `spend.json` GPU-h
against (a) P0's in-run projection and (b) the registered estimate **3 – 32
GPU-h = $2.41 – $25.75 derived**, against the registered **cap 40 GPU-h**, with
ratio and attribution, waste separately named (rule 12; `COMPUTE_BUDGET_CHARTER`
§6). The **"8.5" is struck as unsupported**:

> ~~"…and (b) this section's 8.5–32 range…"~~ → **read as: "…and (b) this
> section's registered 3–32 GPU-h estimate…"**. STRUCK 2026-08-24T17:26:51Z.

**Gate-neutral, explicitly.** This item changes **no gate, no threshold, no cap
and no label.** G0–G4 and their thresholds are untouched; the falsifier's three
branches (§5) are untouched; `CAP_H = 40 GPU-h`, `E_TARGET = 300`, `E_MIN = 50`
and the BLOCKED-on-overrun rule are untouched; the verdict vocabulary is
untouched. Only the lower bound quoted inside the calibration-reporting sentence
is corrected to the value the same section already registers.

**Noted, no change: G4's propagation count.** §4's G4 costs *"7 propagations at
R4's measured 0.259 core-h/case = 1.81 core-h = $0.093 derived"*, but G3 is PASS
when **at most one** of the 8 TEST cases is NOT A RESULT — so **8** G3-passing
cases are admissible and 8 propagations would cost 8 × 0.259 = **2.07 core-h =
$0.106 derived** at $0.0513/core-h. Both figures are inside the CPU blanket
(rule 12) and neither approaches $25. **The registered G4 cost line is NOT
amended**; this is a disclosure so that a G4 spend of 2.07 core-h is not read as
an overrun of a 1.81 core-h cap. G4's gate and its "not run → capped at GATE
REACHED" clause are unchanged.

---

**Nothing above this section was edited.** Verified by hashing the amended file's
first 278 lines — the entire pre-amendment body — against the `f36fbdd9` /
HEAD blob in the same shell invocation that wrote this text: **identical**
(`82cf4cbce93c68454b3ab5d26bc3949106c98d665ac57ff607ea2ce95bf8f153`).

**lines whose number changed above this section: 0**

**Verdict, unchanged: PENDING — nothing has been run.**
