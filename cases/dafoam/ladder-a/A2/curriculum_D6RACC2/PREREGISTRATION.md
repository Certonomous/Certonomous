# D6R-ACC2 — PRE-REGISTRATION (FROZEN). D6R's `ACC_mp` arm re-run at a correctly anchored cap

**Item:** `D6RACC2` — **one arm, `ACC_mp`**, the D6R multipoint acceptance gradient, re-run
with a cap derived from **two independent measurements of the program it actually runs**.
**Team:** dafoam. **Date:** 2026-08-30.
**Predecessor:** `cases/dafoam/ladder-a/A2/curriculum_D6R/` — `ACC_mp` ran 2026-08-29T01:54:22Z
and was **killed by its own in-container deadline at 363 s** (`rc = 124`, 24.2 of a 30.0
core-min cap).

---

## 1. THE DEFECT, ONE SENTENCE — `D6R-PREREG-DEF-1`

**`ACC_mp`'s cap priced a program the arm does not run.** The 30.0 core-min cap traces to D6's
`3.0 × 3 (C-94)` anchor, and **C-94 is a 45-second acceptance primal on an already-decomposed
tree, with no adjoint and no colouring** (`docs/COST_CALIBRATION.md:170`, whose own gap
attribution reads *"a tree staged from a finished arm is not a cold arm and must not be priced
as one"*). The registered `ACC_mp` program is `compute_totals` on a **cold staged copy at
np = 4**, which must first **colour the Jacobian — three times, once per scenario.**

**The arm could not have finished.** Not on a slow day, not on an empty box, never:

| | |
|---|---|
| what it needed | **1,685.98 s = 112.40 core-min** (§2) |
| what it was given | **360 s deadline / 30.0 core-min cap** |
| shortfall | **4.68×** the deadline, **3.75×** the cap |
| where it died | 53,124 of 98,959 cells still uncoloured at 335.62 s — **46.3 % through the FIRST of three colourings** |

**AND THIS EXACT DEFECT WAS ALREADY FOUND, NAMED AND REPAIRED FOUR DAYS EARLIER.** `C-139`
(`docs/COST_CALIBRATION.md:215`) classifies D5's identical failure as
**pre-registration mis-anchoring**, in words that describe D6R's arm verbatim: *"§4 priced
ACC48/ACC192 at 3.000 core-min, cap 10.0, on 'D4 ACC, C-94' — a 45 s acceptance primal — while
the registered program is `compute_totals` on a cold staged copy at np=4, which must first
colour the Jacobian."* **D6R inherited the unrepaired anchor.** That is rule 14's shape: *a
lesson is not applied until every call site asserts it*, and a lesson recorded in a ledger row
has no call site at all.

## 2. THE COST, DERIVED FROM TWO INDEPENDENT MEASUREMENTS

**The anchor NAMES the program it prices** — three primal + adjoint pairs including Jacobian
colouring, at np = 4, on the A2 wing — which is precisely what C-94 did not.

### 2a. Anchor (a) — from the run's own logs, 1,685.98 s

| segment | source | seconds |
|---|---|---|
| start-up + **all three primals**, to the first colouring | **`ACC_mp`'s own log**: `Calculating dRdW Coloring... 75.1 s` | **75.10 MEASURED** |
| colouring 1 | `O_mp` log: 886.73 → 1305.81 | **419.08 MEASURED** |
| adjoint 1 + total-derivative assembly | `O_mp` log: 1305.81 → 1417.45 | **111.64 MEASURED** |
| colouring 2 | `O_mp` log: 1417.45 → 1843.30 | **425.85 MEASURED** |
| adjoint 2 + assembly | `O_mp` log: 1843.30 → 1958.55 | **115.25 MEASURED** |
| colouring 3 | `O_mp` log: 1958.55 → 2384.16 | **425.61 MEASURED** |
| adjoint 3 + assembly | mean of the two measured adjoints | **113.45 INTERPOLATED** |
| **total** | | **1,685.98 s** |

**1,685.98 s × 4 ranks ÷ 60 = 112.399 core-min.**

**Six of the seven segments are directly measured**; the seventh is interpolated between two
measurements of the same quantity that differ by 3.2 %, and it is **labelled interpolated, not
measured**. The 75.10 s start-up term is the strongest number here: it is **`ACC_mp`'s own
measurement of its own cold start**, so the one segment most at risk of being wrong by analogy
is the one that is not an analogy at all.

Artefacts: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/ACC_mp_20260829T015422Z_2086625.log`
and `.../O_mp_20260828T162849Z_1898072.log`.

### 2b. Anchor (b) — from D5's ledger, 107.40 core-min

`/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density/ledger.txt` records
`ARM=ACC48 rc=0 wall_s=537 ranks=4 core_min=35.8` — **one** primal + adjoint pair on this same
wing at np = 4, on the same PATCHED image digest. Three pairs = **1,611 s = 107.40 core-min**.

**Its exposures, stated rather than buried.** `3 × 537` counts start-up **three times** where
D6R-ACC2 pays it **once**, so anchor (b) over-states; and D5's FFD density differs, so its
design-variable count and hence colouring cost may differ. **Anchor (b) is corroboration, not
the primary.**

### 2c. The two agree

**112.40 against 107.40 — within 4.7 %**, by two paths that share no arithmetic: one sums
timestamps inside two logs of *this* item, the other reads a single completed ledger row of a
*different* item. **A 4.7 % spread across independent methods is what makes 112.40 a
measurement rather than a projection.**

### 2d. The cap, and why 240.0

| | |
|---|---|
| **Registered estimate** | **112.40 core-min** — anchor (a), the larger of the two |
| **Cap** | **240.00 core-min** = **2.135×** the estimate. An overrun **stops the run**; it does not get a new budget |

Three reasons, in order of weight:

1. **The cap absorbs CONTENTION, not modelling error** — the anchors agree to 4.7 %, so
   modelling error is small. Both were measured at `delivered_cores_mean` **3.93–3.99 of 4**;
   the exposure is a *busier* box. A 2.135× cap covers a box delivering ≈ 1.9 of 4 cores. This
   family's own record puts a number on that class of miss: `C-190` records a rate sampled
   under contention missing by **2.8×**.
2. **The deadline inverts exactly and lands below the stall convention.**
   `TMO = round(CAP × 60 / RANKS) − FRAME_ALLOWANCE_S = round(240.0 × 60 / 4) − 90 =
   3600 − 90 = **3,510 s**`, and back: `(3510 + 90) × 4 / 60 = **240.000000**` core-min.
   **3,510 s sits BELOW rule 12's 3,600-second stall convention**, so an arm that runs all the
   way to its deadline is **never itself a stall row** — a property a cap of, say, 250.0 would
   lose.
3. **The family's own repaired precedent agrees.** D5's repair set ACC48's cap at **60.0**
   against a measured **35.8** — a **1.676×** margin. Applied to 112.40 that gives 188.4; the
   240.0 registered here is **more conservative than the precedent**, and deliberately so,
   because D5's repaired run had the box largely to itself and this one will not.

Headroom: **3,510 / 1,685.98 = 2.08×**.

### 2e. FRAME ALLOWANCE — sanity-checked against `D6R-CAP-FRAME-2`, both terms

The frame has **two** registered numbers and they are **not** the same check:

* **`FRAME_ALLOWANCE_S = 90`** — the term in the deadline inversion above.
* **`FRAME_ALLOWANCE_S − KILL_GRACE_S = 30 s`** — `G10`'s frame-**gap** limb, host bracket
  minus the container's own kernel clock.

**Measured in D6R's own run root:** `O_mp` gap **75 s** on a **12.7 MB** log; `ACC_mp` gap
**0 s** on a **100 kB** log. The 75 s is what `curriculum_D6RG/RESULTS.md` §3c names as
**`D6R-CAP-FRAME-2`** — the 30 s limb is under-registered for a log that size.

**Is the deadline safe for the log THIS arm will write? YES, and here is the reasoning.**
`ACC_mp` wrote 100 kB in 363 s while still inside its first colouring. Three complete colourings
plus three adjoints scale that to roughly **0.5–1 MB — still 13–25× SMALLER than `O_mp`'s
12.7 MB**, and 90 s already covers the measured worst case of 75 s at that much larger size. The
**deadline** is safe.

**Is the `G10` 30 s gap limb safe? MEASURED AT ZERO FOR THIS EXACT PROGRAM, AND INHERITED
UNCHANGED.** The identical program, at identical ranks, on this box, recorded a **0 s** gap.
**D6R-ACC2 does not widen the 30 s limb** — widening a registered allowance is a gate change and
is not this item's to make. **If the gap nonetheless exceeds 30 s, that is a `GATE FAIL` and it
is reported as one, not repaired.**

## 3. WHAT CHANGED FROM D6R, AND IT IS ONLY THE CAP

**The program is unchanged.** `d6r_opt_runScript.py -task compute_totals` at
`mpirun -np 4`, PATCHED `dafoam-idwarp-rot:v1`
`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, 20g, cpuset
`2,3,4,14`, H5 floor 24.0 GiB, aggregate ceiling 30.6 GiB — **all of D6R's, unedited.** The
instruments are **staged from `curriculum_D6R/` under D6R's own frozen md5s**; no frozen file is
copied into this item and none is edited (rule 6).

The launcher and driver are **byte-derived from D6R's frozen files by an ENUMERATED substitution
set, every substitution asserted present-then-absent**, in `d6ra2_derive.py`, with the whole
change readable as `d6ra2_run_arm_DELTAS_from_d6r.diff` (+40 / −11 lines) and
`d6ra2_chain_driver_DELTAS_from_d6r.diff` (+21 / −8). **Anything not in that set is D6R's
bytes.** The source launcher's md5 is asserted equal to `243f0f631719edf7ae354410276b3cfd`, the
value D6R's own driver pins at `:32`, before a byte is read.

**Two of the deltas are STRENGTHENINGS that can only turn a launch into a refusal:** the
launcher and the driver each **REFUSE any arm but `ACC_mp`** — this item registers exactly one
arm and a second arm is a separate item — and D6R's preserved run root is added at the head of
`FORBIDDEN_ROOTS` so a mis-pointed launcher **names the evidence it just protected**.

## 4. GUARDS ARE DRIVEN, NOT ASSERTED — 16/16, ZERO CONTAINERS CREATED

`d6ra2_run_arm.sh` contains `sudo -n rm -rf "$WORK"`. A launcher with a destructive step is
trusted only after its guards are **driven and shown to abort**. `d6ra2_guard_selftest.py`,
**16/16 under `python3` and `python3 -O`, container census before == after**:

| unit | what was driven |
|---|---|
| U2 | the launcher pointed at **D6R's own preserved run root** — the one holding `O_mp`'s 2,257.933 core-min — **REFUSES, rc 3**, against the real path |
| U3 | and the abort **names** that root |
| U4, U5 | D4's root refuses; a `..` traversal to D6R's root refuses (`realpath -m` normalises) |
| U6–U9 | every arm but `ACC_mp` refuses, rc 64; the guard is an **equality**, not a prefix match |
| U10–U12 | the cap in the file is **240.0**, its deadline **3,510 s**, the inversion **exact to six decimals**, below the 3,600 s stall convention, and **no `echo 30.0` branch survives** |
| U13 | the driver's pinned launcher md5 **equals the derived launcher's actual md5** |
| U14 | all four staged instruments carry **D6R's frozen md5s** — the program is unchanged, proved rather than asserted |
| U15, U16 | **every guard precedes the first destructive step**, with both line numbers **recomputed from the file**; exactly **one executable `rm -rf`**, at line 340, targeting `$BASE/$ARM` |

**Disclosed, because the control caught itself:** the first draft of U15/U16 reported a **false
positive** — it matched the D4-LAUNCHER-DEF-1 header **comment** that quotes
`sudo -n rm -rf "$WORK"` while explaining the defect. A detector that cannot tell a statement
from prose about a statement would fail every correct file. It was fixed to skip comment lines,
and the commented occurrence is now **counted and named rather than hidden**. This happened
**before** the freeze.

## 5. WHAT THIS ITEM MAY NOT CONCLUDE

* **Nothing about D6R's verdict.** D6R is `NOT A RESULT` and stays so; this item does not
  re-open, revise or repair it. `curriculum_D6RG` graded it and that record stands.
* **Nothing about `O_mp`, `F_mp` or `REF_off`.** `O_mp`'s 2,257.933 core-min is **spent and not
  re-bought**; `F_mp` and `REF_off` are not registered here.
* **Nothing about why the primal returns non-finite values at trial geometries.** D6R's §6
  declines that and prices it separately.
* **No new gate, threshold, band or label** — and **`D6R-CAP-FRAME-2` is inherited unrepaired**,
  by design.
* **A `GATE FAIL` or a `NOT A RESULT` here is a result and is reported as one.**

## 6. REGISTERED OUTCOMES, named before compute

1. `rc = 0` inside the cap → the acceptance gradient is bought; the arm's own record is graded
   against D6R's frozen `G1` completion clauses for a SCRIPT arm.
2. `rc = 124` at the 3,510 s deadline → **the estimate was wrong by more than 2.08×** and that
   is the finding; **no new budget** (rule 12).
3. `rc = 137` (OOM at 20g) → a finding about multipoint memory feasibility at np = 4, the P7
   question, and **not a wasted run**.
4. `BLOCKED` at the H5 or aggregate bound (4 h each) → zero compute, re-fireable, **not a
   defect**.
5. Any guard abort (rc 3, 4, 5, 64) → zero compute, reported with its clause.

## 7. COST (rule 12; `COMPUTE_BUDGET_CHARTER.md` §5)

| | |
|---|---|
| Registered estimate | **112.40 core-min**, ranks **4** |
| Cap | **240.00 core-min**; in-container deadline **3,510 s**; inversion exact |
| Rate | **$0.0513 / core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| Dollars, estimate | **$0.09610 DERIVED, NOT MEASURED** (1.87333 core-h) |
| Dollars, cap | **$0.20520 DERIVED, NOT MEASURED** (4.00000 core-h) |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Pre-authorisation | both figures are far inside the $25 blanket; **a blanket is not a per-item read** (rule 9), and this item is costed on its own measurements |
| Disk | ≈ 0.5 GB, a new run root; D6R's root is **not touched** |

A calibration row is owed in `docs/COST_CALIBRATION.md` on completion, with its id re-derived
from the tail at commit time (rule 11). **It will state the ratio against 112.40 and will name
whether the miss is contention or modelling** — and, given `C-139` and `C-214`, whether this
family has finally put a cache-state and a colouring term into its estimates rather than
recording the lesson again.

## 8. RULE-2 CONDITION — the run directory that does not exist

Checked at this freeze, 2026-08-30, **three times**: before the derivation, after the guard
selftest, and in the committing invocation.

* `ls -d /home/ubuntu/certonomous-runs/*D6RACC2*` → **0 entries.**
* `ls -d /home/ubuntu/Certonomous/verification/runs/*D6RACC2*` → **0 entries.**
* No `d6ra2_` container has ever existed on this box: the guard selftest's own census read
  `docker ps -a` before and after every invocation and **created zero**.
* `cases/dafoam/ladder-a/A2/curriculum_D6RACC2/` contains only the files frozen in §9 and this
  document. No ledger, no `RESULTS.md`, no run artefact exists.

**The gates close the moment the driver first fires.**

## 9. FROZEN BY MD5 WITH THIS DOCUMENT

| file | md5 |
|---|---|
| `d6ra2_run_arm.sh` | **`a561ab9309559680305c9ddb0fcc1d7b`** |
| `d6ra2_chain_driver.sh` | **`9b3e498806787b3d4a60a7cc23f85d44`** |
| `d6ra2_guard_selftest.py` | **`5f9060d9d207a83956df5059e56ffc10`** |
| `d6ra2_derive.py` | **`ee8bc0c7cd98e8d263b374bd79dca763`** |

Staged from `curriculum_D6R/`, **unedited and asserted at every launch**:
`d6r_opt_runScript.py` `93edb4a231e13a7af065368f61a468ef`, `d6r_fd_endpoint.py`
`7491c3a73c232fb6744990fd8109fd63`, `d6r_extract_endpoint.py`
`1743dd4232a7f06785f71be2f285f08d`, `d6r_ref_off.py` `ad67bbeb0c7b502262ebf5d4e8fa21cd`,
`d4_extract_endpoint.py` `ee7d3c99fd716da23779cb651961918e`. Source launcher
`d6r_run_arm.sh` `243f0f631719edf7ae354410276b3cfd`.

**Frozen guard-selftest unit count `EXPECTED_UNITS = 16`**; it must pass under `python3` **and**
`python3 -O` with **zero containers created**. **Zero `assert` statements**, AST-counted.

## 10. ENQUEUEING IS NOT AUTHORISATION

The queue entry `verification/queue/dafoam/D6RACC2.json` is **a proposal on a list**.
`SUPERVISION_CHARTER.md` §3 check-4 — *pre-registration committed before compute* — **is the
supervisor's own and this lane claims none of it.** This lane's disclosure to the supervisor:

* **The box is loaded at this freeze** — load 20.43 on 16 cores, `MemAvailable` 28.18 GiB, and a
  peer's container `d12y_w3_S3_r1_20260830T231011Z_1280361` is live. **It was not touched.** The
  driver's own H5 (24.0 GiB floor) and aggregate (30.6 GiB ceiling) **wait-and-retry** gates,
  each bounded at 4 h, will hold the arm until the box can carry it, and **`BLOCKED` at the
  bound is a registered outcome that spends nothing.**
* **The queue runner is alive** (pid 881, `--daemon`). Per Sanaa's 2026-08-26 detached-queue
  ruling, queues run as OS daemons independent of agents, and **this entry is not launched by
  hand** — that is the whole point: the work survives this lane's death.
* **A conflict on record, referred and not resolved here:** `verification/queue/dafoam/README.md`
  states *"There is no daemon, no scheduler, no watcher and no timer behind this directory."*
  That text **predates and is superseded in practice by** Sanaa's 2026-08-26 ruling and by the
  live pid 881. **Amending a standard's text is not this lane's call**; it is reported.

**Nothing in this item is sent, filed, uploaded, registered, posted or commented outside this
box** (rule 7). "Filed in the queue" means the local `verification/queue/` directory and
nothing else. **SUBMISSIONS PARKED.**
