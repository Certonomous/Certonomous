# Lane report — provenance of the three live `R_*_x` solvers

**Lane:** `lab-lane`, heat-transfer. **Supervisor:** heat-transfer-supervisor.
**Written:** 2026-08-25, while all three solvers were running. **Read-only on
every running case; nothing was restarted, killed or disturbed.**

**Headline: the brief's two framing assumptions are both wrong, and the news is
good.** This is **not** a Rayleigh sweep and it is **not** uncovered compute.
It is **T1b**, a **Reynolds** sweep, and the runs are covered by a
pre-registration **committed 78 seconds before the first solver started**.

---

## 0. Corrections to the brief, up front

| brief said | disk says | artifact |
| --- | --- | --- |
| "`R_*_x` looks like a Rayleigh-number sweep" | `R` is **Reynolds**. Re = 1e4 / 1e5 / 3e5 | `R_10k_x/CASE.txt` line `Re 10000`; `R_100k_x/CASE.txt` `Re 100000`; `R_300k_x/CASE.txt` `Re 300000` |
| `Time =` grepped from `log.blockMesh` | correct file is **`log.solve.ext1`** — these are *extension* runs, and `log.solve` is the finished first segment | `R_*_x/log.solve.ext1` |
| implicitly, fresh runs | each case was already **complete and marked DONE** at its original `endTime`; these are registered **restarts from `latestTime`** | `DONE.R_10k_x` etc., contents `strict rule met`; `log.solve` ends `End` |

The brief's `Time =` figures happen to be a mix: 20000 and 80000 are the
**original** `log.solve` end times, 83772 is a genuine mid-flight `ext1` value.
Neither came from a file that could give the current iteration reliably.

---

## 1. Which rung — **T1b**, fourth grid level (`x`), extension segment 1

**Rung id `T1b`** — *fully developed turbulent pipe, two-correlation band*,
`kOmegaSST`, resolved wall treatment, target y+ 0.390625, D = 0.2 m, L = 100 D.
Stated in each case's own self-describing card.

- **Artifact:** `verification/runs/T-family/T1_runs/R_10k_x/CASE.txt`, line
  `rung  T1b (fully developed turbulent pipe, two-correlation band)`.

**Campaign prose, all under `docs/campaigns/T-family/`:**

| document | role |
| --- | --- |
| `T1b_DESIGN.md` | the rung's design |
| `T1b_RESULTS.md` | the frozen (c, m, f) results record |
| `T1b_L4_AMENDMENT.md` | **registers the fourth level `x`**, the amended gating rule, the endTimes, and §4 the extension protocol these runs execute |
| `T1b_L4_GRADE_RULING_2026-08-25.md` | the supervisor's grade of the L4 pool: **`NOT A RESULT` × 4** |
| `T1b_L4_EXT2_PREREGISTRATION.md` | **the pre-registration these three runs are executing** |
| `T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md` | the rule-3 control for the same rung |

---

## 2. Pre-registration — **EXISTS, COMMITTED, AND FROZEN BEFORE COMPUTE**

**Verdict on the supervisor's undelegatable check 4: the check passes. Give it
your own eyes; here is what mine found.**

- **Path:** `/home/ubuntu/Certonomous/docs/campaigns/T-family/T1b_L4_EXT2_PREREGISTRATION.md`
- **Commit:** `72e9b58aed484a99a09b00f400f11a5f0854a56a`
  — *"T1b L4 extension: pre-registration FROZEN before any extension solver launches"*
- **Commit time:** 2026-08-25 **16:35:28 +0000**
- **Blob sha at HEAD:** `9d4beec421f1485ed4f7c400be8554191d23528f`
- **Blob sha of the worktree file:** `9d4beec421f1485ed4f7c400be8554191d23528f`
  — **identical. The committed file IS the file on disk.**

**The freeze margin, measured:** the earliest solver (`timeout 66000`, pid
2203926) has `lstart` **Tue Aug 25 16:36:46 2026**. The pre-registration was
committed at **16:35:28**. **The gate, cap and label were frozen 78 seconds
before the first solver started.** That is the whole evidentiary content of a
pre-registration and it holds here.

**One thing that will look alarming and is not.** `git status --porcelain` on
that path prints `D ` in the index column and `??` in the worktree — the
**decayed shared index** the brief warns of (1,228 paths). The file is present
on disk and its content hashes **byte-identically to the HEAD blob**. There is
no deletion. I did not clear, reset or touch the index.

**What the document does and does not do, in its own words:** it *"creates no
gate, no threshold, no band and no label"* — all of those were already frozen
2026-08-21 in `T1b_L4_AMENDMENT.md` §§2–4 and in `T1b_band.json`, and it adopts
§4's enumerated raised endTimes **unchanged; it does not choose them**. That is
the correct shape for a continuation: it cannot have been written to fit an
answer because it decides nothing.

---

## 3. `endTime`, current iteration, rate and ETA

**Source for every figure below: `R_<case>/log.solve.ext1`** (the real solver
log) for `Time =` and `ExecutionTime`, and `R_<case>/system/controlDict` for
`endTime`. Reading taken at **2026-08-25 19:05 UTC**, elapsed 8 976 s.

| case | pid | `endTime` (controlDict) | current `Time` | iters done in ext1 | `ExecutionTime` | overall s/it | recent s/it (last 600) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `R_10k_x` | 2203927 | **32 000** | 21 821 | 1 821 | 8 996.4 s | 4.9403 | **4.9852** |
| `R_100k_x` | 2203944 | **94 000** | 82 897 | 2 897 | 8 995.7 s | 3.1052 | **3.3393** |
| `R_300k_x` | 2203947 | **110 000** | 83 850 | 3 850 | 8 992.7 s | 2.3358 | **2.6469** |

**ETA and projected total wall, at the recent (conservative) rate:**

| case | iterations remaining | ETA | projected TOTAL wall | cap (s) | headroom |
| --- | ---: | ---: | ---: | ---: | ---: |
| `R_10k_x` | 10 179 | **14.10 h** | 59 741 s | 66 000 | 6 259 s (**9.5 %**) |
| `R_100k_x` | 11 103 | **10.30 h** | 46 072 s | 78 000 | 31 928 s (41 %) |
| `R_300k_x` | 26 150 | **19.23 h** | 78 208 s | 165 000 | 86 792 s (53 %) |

**All three are projected to finish inside their caps.**

**The one figure to watch: `R_10k_x`.** Its recent rate, 4.9852 s/it, is already
**92 % of the 5.4338 s/it ceiling basis** the pre-registration itself adopted.
Priced at that registered ceiling rate for every remaining iteration, the total
becomes **64 307 s against the 66 000 s cap — a 1 693 s margin, 2.6 %.** It fits,
but it is the only one of the three with no real slack, and it is the one that
will hit `timeout` first if box contention rises. Under §10 of the
pre-registration that outcome is not a crisis and is already pre-decided: rc 124,
`mark_done_t1b_L4.py` refuses the case, verdict **`NOT A RESULT`**, and **no
larger budget is issued.** Nothing here needs a decision from you today; it needs
a look tomorrow morning.

**Cross-check that the restart is the registered one:** the first `Time` of each
ext1 log is exactly `endTime + 1` of its first segment — 20001, 80001, 80001 —
which is the disclosure §4 of the amendment demands.

---

## 4. Is the `timeout` a correctly converted cap? — **YES, and ranks == 1 is proved three independent ways**

The identity is `timeout_s = cap_core_min × 60 ÷ ranks`, and it coincides with
wall seconds only at one rank. **`ranks == 1` for all three cases:**

1. **No decomposition on disk.** No `system/decomposeParDict` exists in any of
   the three cases, and `ls -d processor*` returns **0** directories in each.
2. **The launch command is serial.** The live command lines are
   `timeout <N> buoyantBoussinesqSimpleFoam` — **no `mpirun`, no `-parallel`**
   (pids 2203926/2203943/2203946 are the `timeout` parents of the three solver
   pids).
3. **`ExecutionTime` tracks wall time 1:1.** `ExecutionTime` ≈ 8 996 s against
   8 976 s elapsed since `lstart` — the signature of a single rank. A 4-rank job
   would show roughly 4× the wall.

It is also **registered** as such: §6 of the pre-registration, *"Serial, 1 rank,
no decomposition — `nProcs = 1`, no `decomposeParDict` is used, no
`decomposePar` is run, and the solver is invoked directly rather than through
`mpirun`."*

**Implied core-minute caps, and they match the register exactly:**

| case | `timeout` (s) | ÷ 60 × ranks(=1) | registered cap (core-min) | agree? |
| --- | ---: | ---: | ---: | :--: |
| `R_10k_x` | 66 000 | **1 100** | 1 100 | ✔ |
| `R_100k_x` | 78 000 | **1 300** | 1 300 | ✔ |
| `R_300k_x` | 165 000 | **2 750** | 2 750 | ✔ |
| **total** | | **5 150** | **5 150** | ✔ |

**No factor-of-ranks overrun. Nothing to report as an overspend.** The
pre-registration anticipated exactly this trap and says so: *"The identity is
written as `timeout = cap_core_min * 60 / ranks` and is coded that way in the
runner, so a later parallel case cannot inherit a silent factor-of-ranks
overrun."*

---

## 5. Does the registered cap cover the timeouts? — **YES; the timeouts ARE the caps**

There is no gap to find here, because the two are the same quantity in two
units. §10 of the pre-registration registers the cap **and** the enforced
timeout in one table, and the three numbers on the live command lines are
**identical** to the three in the frozen table.

The caps are not arbitrary either. §9 derives a POINT estimate of **2 865.8
core-min** from each case's own measured late-segment throughput on this same
209 920-cell mesh, and a CEILING of **5 071.5 core-min** using the slowest
sustained rate ever measured on this mesh applied to every case. **The
registered cap, 5 150 core-min, is that ceiling rounded up** — derived
**$4.40**, at $0.0513/core-h, **reported-by-owner, not measured** (the box
cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). Comfortably inside
Sanaa's standing under-$25 pre-authorisation.

**Owed at completion, and not yet done:** the rule-12 estimate-versus-actual
calibration row in `docs/COST_CALIBRATION.md`, actual core-minutes from
`STATUS_ext1.<case>`. **`STATUS_ext1.*` does not exist yet** — the runner writes
it at exit — so the calibration is **PENDING** and cannot be closed while the
solvers run.

---

## 6. Grid triple or sweep? — **NOT a grid triple. Three separate Reynolds numbers.**

**This is the answer with the most consequence for what these runs can and
cannot carry, so it is stated flatly: the three live processes are three
different Reynolds numbers at the SAME grid level. They are not three grid
levels and they cannot form a triple among themselves.**

T1b's structure is a **four-level grid ladder at each of four Reynolds
numbers**. The levels, measured from `log.checkMesh` at Re = 1e4:

| level | mesh | cells | refinement |
| --- | --- | ---: | --- |
| `c` | 50 × 250 | 12 500 | — |
| `m` | 80 × 400 | 32 000 | ×1.6 |
| `f` | 128 × 640 | 81 920 | ×1.6 |
| **`x`** | **205 × 1024** | **209 920** | **×1.6** |

Each `CASE.txt` names its own place: `level  x (fourth level, wall-refined)`,
`ladder_for  R_10k_{m,f,x} under T1b_L4_AMENDMENT.md`. **So `R_10k_x` is one
member of the (m, f, x) triple at Re = 1e4; `R_100k_x` of the triple at Re =
1e5; `R_300k_x` of the triple at Re = 3e5. Three different triples, one member
each.** The fourth Reynolds number, 3e4, is absent from this batch because
`R_30k_x` converged at its registered `endTime` and §1 of the pre-registration
explicitly **does not extend it**.

**On Sanaa's 2026-08-25 ruling.** Her words, at `docs/standards/MESH_STANDARD.md`
lines 450-453: *"Grid standard ruled: 3 levels... More levels are a research
option, never a gate requirement."* The `x` level here is **not** owed and was
never claimed to be: it was registered **2026-08-21**, four days before the
ruling, under Sanaa's own 2026-08-21 authorisation quoted at
`T1b_L4_AMENDMENT.md` line 8. It is exactly the research option the ruling
permits. **No agent required it and no gate presumes it.**

**And the ruling gives this rung nothing.** MESH_STANDARD is emphatic that the
ruling fixes a *count* and relaxes no other condition — standing rule 5 is
untouched. Per `T1b_L4_GRADE_RULING_2026-08-25.md` §1, **not one triple in this
rung is `CONVERGING`**: the (c, m, f) triples read DIVERGENT / DIVERGENT /
DIVERGENT / STAGNANT and the (m, f, x) triples DIVERGENT / STAGNANT / STAGNANT /
STAGNANT. **The rung is `NOT A RESULT` × 4 with zero graded rows, and reverting
to a three-level standard would not change that** — the three-level families
fail on their own evidence. **These extensions are an attempt to clear step (1),
iterative convergence, at the finest level. They are not, and cannot be, a route
to a `PASS` on their own.**

---

## 7. The completion instrument — and the self-blindness probe

**Grader chain, fixed by §7 of the pre-registration and §7 of the amendment:**

`mark_done_t1b_L4.py` (its `check_ext` branch) → `analyse_t1b_L4.py` → `gate_t1b_L4.json`

Both are **frozen and unmodified** — worktree hashes match HEAD blobs exactly:

| file | HEAD blob = worktree blob |
| --- | --- |
| `verification/runs/T-family/T1_runs/analyse_t1b_L4.py` | `59c345bd8f9c2744459dc9564942a47fb12bd5fe` |
| `verification/runs/T-family/T1_runs/mark_done_t1b_L4.py` | `2055d35be50f53c0c23cb8abf46444ca5b359a80` |

`mark_done_t1b_L4.py` will take the `check_ext` branch automatically, because
`has_ext()` keys on the existence of `log.solve.ext1` (line 67), which now
exists in all three cases. That branch applies the strict completion rule
**across both segments**: rc 0 on `STATUS` **and** `STATUS_ext1`; an `End` line
in `log.solve` **and** `log.solve.ext1`; summed `ExecutionTime` count ==
`endTime`; and the first `Time =` of ext1 exactly one past the first segment's
count. It also **removes a pre-existing marker** from an extended case that
fails — so the current `DONE.R_*_x` markers are not a loophole; they will be
withdrawn if the extension does not complete.

### `scripts/check_grader_self_blindness.py` — what it says

**I ran the selftest first (standing rule 3 — a probe never shown able to fire
is not evidence).** The selftest plants both defects and both clean
counterparts. **SELFTEST PASSED**, rc 0: probe A fired on the planted
differing-key-set defect and stayed silent on its clean counterpart; probe B
fired on the planted shared-constant fixture and stayed silent on its clean
counterpart.

**Then over both graders, rc 0:**

- `analyse_t1b_L4.py`: **clean on both probes**
- `mark_done_t1b_L4.py`: **clean on both probes**

**And I report the tool's own caveat rather than burying it**, because it is the
honest reading: the script prints *"clean on both probes (**NOT a proof of
correctness**)"*, and its docstring says *"They are cheap static smells for two
shapes that have each cost this lab a graded run. A clean report is not a
guarantee."* **This is a clean result on two specific failure shapes, not a
verified grader.**

**It is also not the whole picture on this grader, and you already know why.**
`T1b_L4_GRADE_RULING_2026-08-25.md` §4 records **four defects in
`analyse_t1b_L4.py`**, verified personally by the supervisor and docketed **NOT
FIXED** — chief among them that it **returns exit 0 on a rung with zero graded
rows**. None of those four is one of the two shapes this probe hunts, so a clean
probe here is entirely consistent with them and **must not be read as clearing
the grader.** In particular, when these extensions finish, **the exit code of
`analyse_t1b_L4.py` will not tell you whether the rung graded.** Read
`gate_t1b_L4.json` and the printed row count.

---

## VERDICT

**No finding against the runs.** Compute did **not** launch without a
pre-registration; the pre-registration is committed, frozen 78 s ahead of the
first solver, hashes identical to disk, and registers the cap, the rank count
and the enforcement mechanism. The caps are correctly converted, `ranks == 1` is
proved three ways, and the enforced timeouts equal the registered caps exactly.
**No overrun, no uncapped compute, no unregistered gate.**

**Status of the three runs: `PENDING`** — they are mid-flight, and no verdict is
available or permitted until `mark_done_t1b_L4.py` has judged both segments. §7
of the pre-registration forbids the running lane from assigning one, and I am
not assigning one.

**Standing status of the rung itself is unchanged and remains
`NOT A RESULT` × 4** per `T1b_L4_GRADE_RULING_2026-08-25.md`, tiered `NOT HELD`.
These extensions can clear step (1) at the `x` level; they cannot by themselves
produce a `PASS`, because no triple in this rung is `CONVERGING`.

**Cost of this lane:** negligible — read-only inspection, no solver launched,
no compute beyond the two static probe invocations.

### What I could not verify

- **`STATUS_ext1.<case>` does not exist yet.** The strict completion rule cannot
  be evaluated, and the **rule-12 estimate-versus-actual calibration row in
  `docs/COST_CALIBRATION.md` is owed and PENDING.** My ETAs are projections from
  `ExecutionTime`, not measurements of a finished run.
- **I did not re-run `analyse_t1b_L4.py`**, which would be premature and would
  write over a graded artifact mid-flight.
- **I did not verify that `run_one_ext1.sh` as executed matches the form §8 of
  the pre-registration registers.** Three scripts of that family exist
  (`launch_t1b_L4_ext1.sh`, `run_one_ext1.sh`, `run_one_t1b_L4_ext1.sh`); the
  *observed behaviour* is consistent with the registered form — `log.solve`
  untouched since 2026-08-23/24/25, `log.solve.ext1` appending, checkMesh to
  `log.checkMesh.ext1`, and `PRESERVED_L4_graded/<case>/` populated with the
  hardlink-preserved graded checkpoints and `controlDict.pre_ext1` — but I did
  not diff the launcher against the registered form line by line.
- **The 2.6 % ceiling-rate margin on `R_10k_x` is a projection, not a
  guarantee.** It fits at today's contention; it is the one that will trip if
  contention rises.
