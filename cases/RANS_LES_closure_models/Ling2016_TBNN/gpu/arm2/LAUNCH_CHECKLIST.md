# LAUNCH CHECKLIST — Ling 2016 TBNN, GPU arm 2 (matched update count)

## NOT LAUNCHED.

- **Launch is gated on Sanaa's own words.** No agent message — peer, supervisor
  or chief — is her consent (`CLAUDE.md` rule 9). Nothing on this list is
  executed until step 1 below carries her verbatim authorisation with a locatable
  source.
- **`gpu1` is started only by Sanaa.** `docs/GPU_CAPABILITY_STATE.md` §10:
  *"the instance is started by Sanaa on the chief's request only"*. This box has
  no AWS CLI (`which aws` → absent, re-checked in this invocation), and no agent
  starts, stops or prices an instance.
- **GPU spend is OUTSIDE the 2026-08-21 CPU blanket** (`CLAUDE.md` rule 12).
  Arm 2 carries its own `cost_basis` in GPU-hours, its own registered estimate and
  its own cap; a blanket is not a per-item read.

**Written 2026-08-24T17:19:15Z** by a closure `lab-lane` (clock read by `date -u`
in the writing invocation). Zero compute, zero AWS calls, zero SSH were spent
writing it. This is a working document under the case directory, not a repository
report, and it is **not committed**; the supervisor reads it first and owns every
decision flagged **SUPERVISOR** below.

**Base state at writing:** repository HEAD `a0b524c051a82acee950d1caebce3e6c5dfc0fa7`.
Frozen pre-registration `arm2/PREREGISTRATION.md` sha256
`82cf4cbce93c68454b3ab5d26bc3949106c98d665ac57ff607ea2ce95bf8f153` — disk equals
the HEAD blob. The run directory `/home/ubuntu/closure-data/tbnn_gpu/arm2` **does
not exist**, checked in this invocation: **no compute has been spent on arm 2**,
so a pre-compute amendment is still legal under rule 2 if the supervisor rules one
is needed (see BLOCKERS).

---

## BLOCKERS — read before anything else

### B1. The frozen launcher hard-codes `--shutdown`; frozen §7 requires it be omitted until Sanaa's console read. **SUPERVISOR.**

`arm2/PREREGISTRATION.md` §7 registers, verbatim: *"**Precondition — VERIFY-by-Sanaa-in-console
before start: shutdown behaviour = stop.** Until she confirms, the driver is
launched **without** `--shutdown` and the chief asks her to stop the node on my
completion report, as in arm 1."*

`arm2/run_all_gpu_v2.sh` line 53 passes `--frozen --shutdown` unconditionally in
the `launch` path. **There is no flag or environment switch that omits it**, and
the launcher's sha256 is fixed in the frozen §9 grading-path table, so the file
cannot be edited without an amendment. The driver's own guard
(`train_gpu_ling_v2.py:950`) refuses `--shutdown` only off the GPU node or with no
CUDA device — on `gpu1` it will halt the instance.

Consequence: `bash run_all_gpu_v2.sh launch` **cannot** satisfy §7's
until-she-confirms branch. The supervisor's options, none of which a lane takes:

1. Obtain the console reading first (step 2b). If it reads **stop**, §7's
   precondition is met, `--shutdown` is correct, and the launcher runs as frozen —
   **no amendment needed, and this is the clean path.**
2. If the reading is **terminate**, or if Sanaa launches before reading it: the
   launcher must not be used as frozen. Either a dated pre-compute amendment
   (legal — the run directory does not exist, checked above, which is rule 2's
   required condition-and-how-checked) or a hand-issued launch line that omits
   `--shutdown`, at the cost of the launcher's own driver-sha check and its
   `run_window.json` clock read, both of which would then have to be reproduced by
   hand and disclosed.

### B2. Two arithmetic readings of the same registered range inside the frozen file. **SUPERVISOR.**

§6's costing block registers **`REGISTERED ESTIMATE : 3 - 32 GPU-h = $2.41 - $25.75 derived`**.
Twelve lines later the calibration clause of the same section says the actual will
be compared against *"(b) this section's **8.5–32** range"*. The floor differs:
**3 vs 8.5**. The block's own arithmetic supports 3 (34 s/epoch-both × 300 epochs
= 2.83 GPU-h ≈ 3); 8.5 does not derive from any line in the block and reads as a
survival from an earlier draft. The dollar figures $2.41 and $25.75 are correct
for 3 and 32 at $0.8048/GPU-h, and the cap arithmetic (40 GPU-h = $32.19) is
correct.

Nothing here moves a gate, threshold or cap — but the calibration row owed at
completion (rule 12) must be written against **one** registered range, and the
supervisor should fix which before launch. Pre-compute amendment is legal now and
will not be after the first artefact lands.

### B3. `cost_basis` is still the published price feed, not a console read. **SUPERVISOR / SANAA.**

Arm 2 §6 uses **$0.8048/GPU-h** from `docs/GPU_CAPABILITY_STATE.md` §9 — AWS's
published on-demand price feed, retrieved 2026-08-23, labelled honestly. Audit
pass 8 §42 recorded this as a **DISCLOSED DEVIATION** from rule 12's *"priced from
the console, never from recall"*, noting that the arm-1 draft's dropped §14 had
demanded the console read, and that `GPU_CAPABILITY_STATE.md` §8's standing
operational rule reads *"nothing trains until the Ling2016 TBNN pre-registration
carries the console price in its `cost_basis`"* (§9 supersedes §8's price
paragraph, but not in those words). Step 2b asks Sanaa for the console figure,
which closes the deviation for arm 2 at no cost — she is already being asked for
the shutdown attribute in the same console session.

### B4. Nothing watches for completion. **SUPERVISOR — this is L-268's failure mode.**

Arm 1's node idled **7.88 GPU-h = $6.34 derived** after the batch completed at
08:03:58Z because the overnight session limit had killed the whole fleet and no
agent existed to report completion (`gpu/RESULTS.md` D-2, ledger C-16/C-19,
L-268). Arm 2's `--shutdown` is the structural fix, but it only fires if the
driver reaches its shutdown stage; a BLOCKED, refused or crashed run still writes
`COMPLETE.json` through the `finally` path, and a *failed halt* is visible only if
somebody reads `out/shutdown_attempt.json` on a node that is still up. See step 7.

---

## THE ORDERED STEPS

### 1. Sanaa's authorisation — quoted verbatim, with its source

**Not yet on this checklist. A lane cannot supply it.** The supervisor fills this
block in before step 2 and the block must be quotable back to Sanaa:

```
Sanaa, verbatim: "<...>"
Source: [ ] her message in this session, timestamped
        [ ] a commit at HEAD: <sha> <path>:<line>
```

**What already exists is not enough on its own, and the supervisor should say so
when asking.** The frozen §1 cites her 2026-08-24 rulings — *"2. Good for the
dispatched work, i approve of everything"* and *"1. GPU shutdown suggestion: yes
approved (also i stopped that instance)"* — recorded in
`docs/GPU_CAPABILITY_STATE.md` §10 as the chief's session record. Those approve
**the item** and **the mechanism**. They are not, by themselves, a start of the
instance: §10's own next-item row says the start is hers on the chief's request,
and the instance is stopped. Ruling 2 is also a blanket in form, and rule 9 says a
blanket is not a per-item read.

### 2. Sanaa's console readings — both taken in one console session

She is at the console to start the instance anyway; these cost her nothing extra
and close two open items.

**(a) The instance's shutdown-behaviour attribute for `gpu1`** — must read
**`stop`** or **`terminate`**.
*Where:* EC2 console → Instances → `gpu1` → Actions → Instance settings → Change
shutdown behaviour (or the instance's Details tab). *Why:* with `terminate`, the
driver's own `sudo shutdown -h now` would destroy the root volume and every
artefact on it. `docs/GPU_CAPABILITY_STATE.md` §10 records this as the
**VERIFY-by-Sanaa-in-console precondition before first reliance** on the standing
self-shutdown mechanism, and states that this box has no AWS CLI and cannot read
the attribute. Arm 2 §12 lists it among the things the frozen file cannot see.

```
Reading: [ ] stop      -> step 6, launch line A (--shutdown, as frozen)
         [ ] terminate -> STOP. Return to B1. Do not launch.
         [ ] not read  -> STOP. Return to B1. Do not launch.
```

**(b) The on-demand price of `g6.xlarge`, Linux, us-east-2 (Ohio), $/hr.**
*Where:* EC2 console pricing panel, or the on-demand pricing page with the region
set to US East (Ohio). *Why:* rule 12's GPU clause. Record the figure and the
date she read it. If it equals **$0.8048** the frozen §6 needs no change and B3
closes as *console-confirmed*. If it differs, the console figure supersedes
(`GPU_CAPABILITY_STATE.md` §9 says so explicitly) — **and the frozen §6's
dollar-derived estimate and cap would then be stated against a rate the frozen
file does not carry.** That is a disclosure, appended dated, never an edit; the
GPU-hour cap of 40 does not move, because the cap is registered in GPU-hours, not
dollars.

```
Reading: $______ /hr, read <date>.   [ ] equals $0.8048   [ ] differs -> disclose
```

**(c) Optional but worth asking for: the clock at which she starts the
instance.** Arm 2 §6's idle accounting registers the interval from her reported
start to the driver's first status stamp as **waste if she reports a clock,
stated absent if she does not**. Arm 1's pre-launch idle is unmeasured for exactly
this reason and pass 8 §47 could only bound it below at 14 min 21 s.

### 3. Instance started by Sanaa, and reachable

Only after steps 1 and 2. **Sanaa starts it; no agent does.**

- [ ] She reports the instance started (clock if she has one, per 2c).
- [ ] `gpu1` reachable from this box: the alias resolves to **172.31.44.162** —
      the *canonical private IP*, which persists across stop/start
      (`/home/ubuntu/.ssh/config` `Host gpu1` → `HostName 172.31.44.162`,
      `User ubuntu`, verified on disk in this invocation). **The public IP changes
      on restart and is never recorded as canonical.**
- [ ] **Plant the reachability zero** (rule 3, and the form pass 8 §43 used): a
      failed SSH is a zero, and a zero from a reader not shown able to see a
      non-zero is not evidence. Run the identical SSH form against this box's own
      private IP **172.31.43.247** as a positive control. The control must
      complete a TCP connection and negotiate (arm-1's audit read
      `Permission denied (publickey)` there) while `gpu1` is unreachable — that,
      and only that, makes an unreachable reading mean anything. When `gpu1` is
      up the control is still worth running once, so the pair is on the record.
- [ ] `nvidia-smi` on the node shows **1× NVIDIA L4, 23,034 MiB, driver
      595.91.07**, **0 MiB used and no compute process** — the L4 idle. A non-idle
      GPU means something else is on the box: **STOP and report**, do not launch
      over it.
- [ ] Node hostname begins `ip-172-31-44-162` — the driver's `--shutdown` guard
      (`train_gpu_ling_v2.py:83`, `GPU_HOST_PREFIX`) refuses anywhere else, so a
      renamed or different node silently loses the self-shutdown.
- [ ] **Capture the environment to a file on the node and pull it** (see step 8):
      `nvidia-smi`, `~/r_ling_gpu/venv/bin/python -V`, `pip freeze`. Arm 1's
      environment provenance survived only because `node_root/pip_install.log`
      happened to be synced; arm 2's launcher captures none of it, and the driver
      records only `torch.__version__` and the device name into its status JSONs
      (`train_gpu_ling_v2.py:739, 906`). Registered arm-1 environment, for
      comparison: Python 3.14.4, venv `~/r_ling_gpu/venv`, torch 2.13.0+cu130,
      numpy 2.5.2, optuna 4.9.0 (`gpu/PREREGISTRATION.md` F.3).

### 4. Freeze re-verification on the node — refuse on any mismatch

The frozen §9 fixes the grading path by sha256. **Rule 2: verify the frozen file
IS the file that ran.** All four values below are re-verified equal to the HEAD
blobs on this box as of `a0b524c0`, in the writing invocation.

| artefact | registered sha256 | where it must be re-hashed |
|---|---|---|
| `arm2/train_gpu_ling_v2.py` | `06d6d4a3f147c6e88d9d4db62b9af6a1b43d76baddb3464ae82d2275a5eb6543` | repo copy **and the node copy** at `~/r_ling_gpu/arm2/train_gpu_ling_v2.py` |
| `arm2/score_gpu_ling_v2.py` | `74aadda9aa3e6c02f543cefd6a3178f798f1ab590c6037cb95e63e50ffce6711` | this box only — the comparator never goes to the node |
| `arm2/run_all_gpu_v2.sh` | `1404dba0133bfa7bd79e8c3a4080f4d32a492e97723aa241c34fa80c475e43c8` | this box |
| `dataset.npz` | `aad528dbd2cb35d2ac32326cc083bebd1c155fbc1439fe48362ba6b96b0b5459` | **lab box: re-hashed in this invocation, MATCHES**; node copy at `~/r_ling_gpu/data/dataset.npz` still to check |

- [ ] Four repo/lab-box hashes re-derived **at launch time**, not trusted from
      this file. Any mismatch → **REFUSE, report, do not launch.**
- [ ] The launcher's own step 2 re-hashes the driver on the node after `scp` and
      exits 2 on mismatch. **It checks only the driver.** The dataset is checked
      by the driver's `g0` stage against `DATASET_SHA256`
      (`train_gpu_ling_v2.py:82, 275`), which refuses on mismatch — but that
      refusal costs a launch, so check the node's dataset hash by hand first.
- [ ] Also assert on the node: **TRAIN rows = 342,014**. The driver asserts it at
      load and refuses otherwise (`:77, 282`). This is the count the whole arm is
      named for; 341,717 is the *scorer's* count and is not it.
- [ ] Frozen pre-registration unchanged: `arm2/PREREGISTRATION.md` sha256
      `82cf4cbce93c68454b3ab5d26bc3949106c98d665ac57ff607ea2ce95bf8f153`, disk ==
      HEAD blob. If the supervisor lands a pre-compute amendment (B1/B2), **this
      value changes and every copy of it in this checklist is stale** — re-derive.

### 5. Data presence and disk

**On the node (`gpu1`), all still to check — no SSH was used to write this list:**

- [ ] `~/r_ling_gpu/data/dataset.npz` present, sha256 == the registered value.
      **The launcher does not sync it.** It is arm 1's copy, expected to survive on
      the EBS root volume across the stop/start — *expected*, not verified from
      here.
- [ ] `~/r_ling_gpu/venv/bin/python` present and importing torch with CUDA
      available. **The launcher does not build or check the venv.**
- [ ] `~/r_ling_gpu/arm2/` and `~/r_ling_gpu/arm2/out/` — the launcher creates
      these (`mkdir -p $RDIR/out`).
- [ ] Free space on the node root volume: arm 1 reported **96 G, 83 G free**.
      Arm 2 writes 6 runs (2 models × 3 seeds) against arm 1's 15, so its `out/`
      should land **well under arm 1's 86 MB**; the risk is not arm 2's outputs but
      arm 1's `~/r_ling_gpu/out/` still sitting there. Leave it — it is evidence,
      and it is small. **Do not delete anything on the node.**
- [ ] `~/r_ling_gpu/arm2/out/` **empty** before launch. A pre-existing status JSON
      makes the driver skip that stage as DONE (its stage-skip convention), which
      is right for a restart and wrong for a first launch.

**On the lab box, verified in the writing invocation:**

- [x] `/home/ubuntu/closure-data/tbnn/dataset.npz` — 167,118,904 B, sha256
      `aad528db…5459`, **matches the registered value**.
- [x] `/home/ubuntu/closure-venv/bin/python` present — the comparator's interpreter.
- [x] Comparator reference files all present and readable, so §6's
      "recorded ONLY if read from files on disk" branch will fire rather than
      silently skip: `Ling2016_TBNN/train_log.json` (5,476 B),
      `_common/trainmean_baseline.json` (3,908 B),
      `_common/sst_baseline_metrics.json` (87,388 B),
      `_common/of_read.py` (10,583 B — this is what makes
      `REALISABILITY_SOURCE` read *"_common/of_read.py (CPU lane)"* instead of the
      embedded fallback), and arm 1's
      `/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json` (26,981 B — the
      byte count pass 8 re-derived against the committed witness).
- [x] `/home/ubuntu/closure-data/tbnn_gpu/out/` — arm 1's 15 `pred_*`, 15 `hist_*`,
      10 `ck_*`, 6 `status_*`, `spend.json`, `armb_optuna.db`, 86 MB. **Reusable
      as-is** by the arm-2 comparator's `--pred-dir` path (`score_gpu_ling_v2.py`
      docstring (d)), which rescores arm 1 with arm-2 code — the per-case
      realisability table and the in-family pooled figures arm 1 never had.
      **Read-only. Nothing in arm 1's directory is overwritten, moved or re-graded.**
- [x] `/home/ubuntu/closure-data/tbnn_gpu/arm2/` — **does not exist**; the
      launcher creates it. Its absence is the rule-2 evidence that no arm-2
      compute has happened.
- [x] Lab-box free space: **298 G free of 484 G**. Ample.

### 6. The launch line

**Launch line A — ONLY if step 2a read `stop`.** This is the frozen launcher used
exactly as frozen:

```
cd /home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/arm2
bash run_all_gpu_v2.sh launch
```

which issues, on the node, in one remote shell line together with the `date -u`
that fixes the run window:

```
nohup ~/r_ling_gpu/venv/bin/python train_gpu_ling_v2.py \
    --frozen --shutdown \
    --data ~/r_ling_gpu/data/dataset.npz \
    --out  ~/r_ling_gpu/arm2/out \
    >> ~/r_ling_gpu/arm2/driver.log 2>&1 &
```

and writes `/home/ubuntu/closure-data/tbnn_gpu/arm2/run_window.json` with the
node-clock start, the driver name and its sha256. `launch` is idempotent: it will
not relaunch over a live `driver.pid`.

**Launch line B — if step 2a did NOT read `stop`: there is none.** Do not launch.
The frozen launcher cannot omit `--shutdown` (B1), and the alternative is the
supervisor's call, not a lane's.

**And say this plainly, because the obvious workaround does not exist:**
if the driver is ever launched **without** `--shutdown`, **no agent in this lab
can stop the instance afterwards.** A lane cannot stop it, the supervisor cannot
stop it, the chief cannot stop it — this box has no AWS CLI and stopping an
instance is an owner action reserved to Sanaa (`CLAUDE.md` FIRST-ACTION RULE:
*"root or an instance change"* is reserved to her). The most any agent can do is
`sudo shutdown -h now` **from inside the node**, which halts the OS and, with the
shutdown-behaviour attribute at `stop`, stops the instance — which is precisely
the mechanism step 2a exists to verify, and precisely why it cannot be assumed.
Without that verification the only stop path is a request to Sanaa, and every hour
between completion and her reading it is waste, named and reported (§6 idle
accounting). Arm 1 paid **7.88 GPU-h = $6.34 derived** for exactly this gap.

### 7. Monitoring — armed by the supervisor, before the launch line is typed

**The monitor is not optional and it is not a lane's `sleep` loop.** L-268: a
watcher dies with the agent that owns it, and the arm-1 node idled 7.88 GPU-h
because the session limit killed the fleet with no live agent left to notice
completion.

- [ ] **A supervisor-armed background monitor**, armed *before* launch, watching
      the completion marker — locally
      `/home/ubuntu/closure-data/tbnn_gpu/arm2/out/COMPLETE.json` after a `--pull`,
      or on the node at `~/r_ling_gpu/arm2/out/COMPLETE.json`. It must survive the
      lane that requested it.
- [ ] **`--pull` runs on a cadence, not once at the end.** With `--shutdown` the
      node powers off the moment it finishes, and everything after that is stranded
      on a stopped instance's volume until Sanaa restarts it. The launcher's own
      header says as much. A periodic
      `bash run_all_gpu_v2.sh --pull` (it never launches) keeps a current copy on
      this box and makes a mid-run BLOCKED visible while it still matters.
- [ ] Cadence anchored to the registered budget: `E` is decided by stage `p0` and
      written to `status_p0.json` **before the first training update** — pull once
      p0 has landed and **read `E` immediately**. `E < E_MIN = 50` → the driver
      writes **BLOCKED** with the numbers and goes to the shutdown stage: that is a
      legitimate registered outcome, not a failure, and it must be reported as
      **BLOCKED**, never softened.
- [ ] Watch for the cap. `CAP_HOURS = 40.0`; a run stopped at the cap is
      **BLOCKED** with no prediction file, and the frozen §10 fixes that a partial
      arm is graded BLOCKED and never as a shorter DONE. **An overrun stops the
      run; it does not get a new budget** (rule 12).
- [ ] Watch for a **failed halt**: `out/shutdown_attempt.json` present *and* the
      node still reachable means the driver tried to power off and did not. Report
      to the supervisor for a stop request to Sanaa; do not retry blind.
- [ ] Watch for `state: REFUSED` / exit 2 (a control refused), exit 3 (BLOCKED),
      exit 4 (unexpected error). **A crash is a finding until the supervisor's own
      triage says otherwise** — it is one of the four checks that may never be
      delegated.

### 8. Post-completion

1. **Pull everything.** `bash run_all_gpu_v2.sh --pull` →
   `/home/ubuntu/closure-data/tbnn_gpu/arm2/out/`. Then pull by hand what the
   launcher does **not** take: it copies `out/`, `driver.log` and `driver.pid` into
   `out/`, and **nothing else** — no `node_root/` equivalent, no `pip_install.log`,
   no `nvidia-smi` capture. Put the step-3 environment capture and the node's
   driver copy under
   `/home/ubuntu/closure-data/tbnn_gpu/arm2/node_root/`, mirroring arm 1's layout,
   so the arm has environment provenance at least as good as arm 1's.
   **Use `rsync -a`** — arm 1's audit (pass 8 §35) could date the run only because
   the sync preserved node mtimes; a `cp` without `-p` would have destroyed that
   evidence.
2. **Re-verify the frozen hashes after the run**, on both machines, as arm 1 did:
   the node's driver copy must still hash to `06d6d4a3…6543`. This is what turns
   *"the frozen file is the file that ran"* from an assertion into a measurement.
3. **Completion, checked as all-or-nothing** against the frozen §8, per run
   (model × seed) — `status` DONE; epochs reached == `E` from `status_p0.json`;
   history CSV continuous from update 0 to `E × 342,014` at the 20,000-update
   cadence with no NaN/inf; best-val checkpoint **and** final state saved;
   `pred_*.npz` present with `idx` equal to the clean dataset's TEST rows;
   **the prediction file newer than `status_p0.json`** (arm 2's form of the age
   guard). Per batch: `COMPLETE.json` present, `spend.json` total ≤ cap. Any clause
   failing → the run is not done, and it is not reported as done.
4. **Read `spend.json`.** Sum the stage seconds and check the sum against the
   file's own `total_hours` rather than trusting the field — pass 8 §43 re-derived
   arm 1's 38,539.6093 s = 10.705447 h that way. Record the wall window from
   `run_window.json` and name the difference as inter-stage overhead.
5. **Grade with the frozen comparator, and only it.**
   `/home/ubuntu/closure-venv/bin/python /home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/arm2/score_gpu_ling_v2.py`
   → `/home/ubuntu/closure-data/tbnn_gpu/arm2/grading_gpu_ling_v2.json`.
   The comparator emits **no verdict**; the supervisor grades its numbers against
   the frozen §4, **personally** — a relayed grade is a summary, not a check.
   Confirm the **comparator witness** is in the JSON: its own file sha256, the
   dataset sha256 and every prediction file's sha256. **A JSON without them is
   refused at grading** — the frozen §4 G0 clause says so, and this is arm 2's
   closure of arm 1's D-5. If G0's plant refuses, the comparator writes **no JSON
   at all**, so the existence of the JSON is itself the proof the plant was read
   back.
6. **Report every pooled figure twice** — 8-case and in-family (7 cases) — with
   the `NASA_2DWMH` row standing alone beside them. **G2 is graded on the in-family
   figure only.** No 8-case pooled figure carries a verdict on its own where an
   in-family companion is registered.
7. **The calibration row** in `docs/COST_CALIBRATION.md` (rule 12; a completion
   report without it is incomplete): actual GPU-h from `spend.json`, against
   (a) P0's in-run projection and (b) the frozen §6 registered range — **whichever
   floor B2 resolves to**; the ratio actual/predicted; the attribution;
   dollars **derived, not measured** at the recorded rate, stated as the console
   figure from step 2b if she read one and as the published-feed $0.8048 otherwise,
   with the provenance label attached either way. **Waste is named separately and
   never folded into the ratio** — arm 1's audit checked that arithmetically, and
   it will be checked again. Under the file's append rules and the rule-10
   private-index protocol. If G4 runs, its CPU cost is a separate line at
   $0.0513/core-h, owner-stated.
8. **Ask Sanaa to stop the instance** — through the supervisor and the chief, in
   the completion report, with the completion clock in it so the idle window has a
   measured start. If the self-shutdown fired, say so and say what evidence shows
   it (`shutdown_attempt.json` written, node unreachable, positive control run);
   if it did not, say that plainly and ask. **No agent stops it.** State the idle
   interval measured to the last verified read and state any open end as
   **absent, not estimated** — the form of ledger correction C-19, which pass 8
   audited as the honest direction.

---

## What this checklist could not verify

- **Anything on `gpu1`.** No SSH was used. Every node-side line above is derived
  from arm 1's records and from the arm-2 launcher and driver text, and is marked
  *to check*, not *checked*.
- **The instance's state or its shutdown-behaviour attribute.** No AWS CLI on this
  box; owner-reported only.
- **The $0.8048 rate.** Taken as recorded in `GPU_CAPABILITY_STATE.md` §9; not
  re-fetched.
- **Whether Sanaa's existing rulings authorise the start.** A lane does not read
  consent into a message. Step 1 is unfilled on purpose.

---

## STATUS CORRECTION, 2026-09-06 — closure-supervisor. TWO OF THE FOUR BLOCKERS WERE ALREADY DISCHARGED, AND THIS CHECKLIST DID NOT KNOW IT

Occasioned by Sanaa's approval (`b7c56371`) and the instruction to "land the B2 amendment".
**B2 had already been landed twelve days earlier.** Following the instruction literally would have
written a SECOND amendment on the same clause of a frozen pre-registration — the records damage
rule 6 exists to prevent. **A blocker list is an instrument, and this one had outlived its
blockers.** Verified by the supervisor against the artefacts, not relayed:

**B1 — DISCHARGED.** `PREREGISTRATION.md` **Item (A)** repairs exactly this, and
`run_all_gpu_v2.sh` now carries `SHUTDOWN=${SHUTDOWN:-1}` (line 34) with the launch line composing
the token from it (lines 51-55). `SHUTDOWN=1` is byte-identical to the frozen line; `SHUTDOWN=0`
omits ` --shutdown` and executes §7's until-confirmed branch. **B1's premise — "there is no flag or
environment switch that omits it" — is no longer true of the file on disk.**

**B2 — DISCHARGED.** `PREREGISTRATION.md` **Item (B)**, dated **2026-08-24T17:26:51Z**, struck the
unsupported `8.5` and fixed the calibration range at the registered **3 – 32 GPU-h = $2.41 – $25.75
derived**, cap **40 GPU-h = $32.19 derived**. **No further amendment is owed and none may be
written** — a second ruling on the same clause would be the defect, not the fix.

**B3 — OPEN, and it is HERS.** §6 still prices from the published feed (`$0.8048/GPU-h`,
`g6.xlarge` on-demand us-east-2, retrieved 2026-08-23, `GPU_CAPABILITY_STATE.md` §9), not from a
console read. Rule 12 wants the console. **Sanaa's console session closes it at zero cost**, in the
same session as the shutdown attribute.

**B4 — OPEN, and it is MINE.** Nothing watches for completion. Arm 1's measured cost of this gap:
the node idled **7 h 52 m 47 s = 7.88 GPU-h ≈ $6.34 derived**, plus an unmeasured pre-launch idle
and an unmeasured post-sync idle. `--shutdown` closes the tail only if the driver reaches its
shutdown stage; a BLOCKED, refused or crashed run still writes `COMPLETE.json` through `finally`,
and a **failed halt is visible only by reading `out/shutdown_attempt.json` on a node still up.**

## AND A FRAMING ERROR THIS CHECKLIST NEVER MADE, WHICH THE SUPERVISOR'S BOARD DID

**This run is HAND-LAUNCHED, not queue-dispatched.** Step 6 is a typed
`bash run_all_gpu_v2.sh launch` issued over ssh. **Neither this checklist nor the pre-registration
references the queue anywhere**, and `scripts/queue_runner.py:926-930` SKIPS any entry whose `host`
is not local — *"remote dispatch is not this runner's"* — so the CPU-box runner could not dispatch
a GPU node run even with a correct address.

**There is therefore NO QUEUE ROW for arm 2: none exists, none is drafted, and none is needed.**
The supervisor's board has carried, and reported upward, a framing in which arm 2 was "a
deliberately unfiled row whose missing `host` field would fire it on the CPU box." **That describes
a hazard of an artefact that does not exist.** The mechanism is real — an empty or absent `host`
IS treated as local, and `""` is inside the runner's accepted set — but it is a warning about
*writing such a row*, not a description of arm 2's state. **The operationally important half of
that warning was always the second half, and it stands: nothing will pick this run up
automatically. If the card is powered on and no one types the launch line, it idles and bills.**
