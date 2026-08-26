# CURRICULUM D7R — RESULTS. Arm `O` COMPLETED, AND THE REGISTERED GRADING PATH **REFUSED** ON IT.

**Date: 2026-08-26. Lane: dafoam `lab-lane`. Item root:**
`cases/dafoam/ladder-a/A3/curriculum_D7R/`. **Run root:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin/`.

**Frozen pre-registration:** `PREREGISTRATION.md` v1.0 (this directory).
**Registered grading path:** `../curriculum_D7/d7_grade.py`, md5 `10eb6d0928addc56272854f017e01538`
(`PREREGISTRATION.md` §5, §10) — **hashed against its committed blob before use and IDENTICAL**
(§1.1 below).

---

## 0. THE HEADLINE, IN THE FIXED VOCABULARY

| | |
|---|---|
| **Arm `O` rung verdict** | **`NOT A RESULT`** |
| **Why** | the registered grader **REFUSED (exit 2)** on the real arm-`O` artifacts and wrote no output, so **no gate ruled on this arm** |
| **Independently** | drag reduction **30.402283 %** lies **outside** the frozen band C **[3 %, 25 %]**, and D7 §5 `G3` registers *"cap-stop → `GATE REACHED` if band C and band A both hold, **else `NOT A RESULT`**"* — in advance |
| **`P1`** | **`PASS`** (`ledger.txt`, `rc=0`) |
| **`P2`** | **`PASS`** — gates `H1` and `H2` both PASS (`RESULTS_P2_H1_H2.md`) |
| **`F-S`, `F-P`** | **`BLOCKED`** — `PREREGISTRATION.md` §6, on the `D4-DEF-4` repair this item does not author |
| **Two-row status** | **SHIPPED row bought. PATCHED row `BLOCKED`. D7R IS NOT A TWO-ROW DAFOAM VERDICT** and its own §7 said so before compute |
| **`GATE REACHED` was a CEILING, not a floor** | `PREREGISTRATION.md` §11 registers `GATE REACHED` as the **best** an unconverged `max_iter` stop may be, *"never `PASS`"*. It is not a verdict this arm earned; the frozen mapping requires band C to hold and it does not |

**Nothing in this record is a regrade.** `PREREGISTRATION.md` §11 registers, before compute:
*"The grader refuses on real artifacts → **a finding under R4, recorded before any regrade**."*
This is that record. No instrument was patched, no input was manufactured to get past the refusal,
and the refusal was reproduced under `python3 -O` as well (§7).

---

## 1. STEP ONE — THE GRADER'S FIRST CONTACT WITH A REAL ARM

`PREREGISTRATION.md` §R4 registered this as *"an event to watch, not a formality"*. It was.

### 1.1 Frozen-file hash check, BEFORE anything ran

| copy | md5 | bytes |
|---|---|---|
| `git show HEAD:cases/dafoam/ladder-a/A3/curriculum_D7/d7_grade.py` | `10eb6d0928addc56272854f017e01538` | 74,338 |
| worktree `cases/dafoam/ladder-a/A3/curriculum_D7/d7_grade.py` | `10eb6d0928addc56272854f017e01538` | 74,338 |
| the copy that ran, `<run root>/d7_grade.py` | `10eb6d0928addc56272854f017e01538` | 74,338 |

**All three identical**, and identical to the md5 `PREREGISTRATION.md` §5/§10 froze. Frozen at commit
`0e229a0a` (the D7 freeze commit). `CLAUDE.md` rule 2 satisfied: the file that ran **is** the file
that was frozen.

**Filing note, reported not corrected:** `d7_grade.py` does **not** exist under
`curriculum_D7R/` at `HEAD` — D7R inherits D7's copy by md5, which is what §10 says it does. The
`--out` document the grader writes self-labels `"item": "curriculum_D7"` (`d7_grade.py:944`), so a
D7R grade would have carried D7's item name. Recorded; not repaired by this lane.

### 1.2 `--selftest`, run immediately before grading

| | |
|---|---|
| units | **65**, **65 passed, 0 failed** |
| coverage | emitted **14**, exercised **15**, `UNEXERCISED=0 [none]` |
| exit code | **0** |

**DEFECT `D7R-GRADER-DEF-5`, MEASURED, NOT ASSUMED.** The file's own header (`d7_grade.py:21-24`)
claims `--selftest` *"has a DISTINCT EXIT PATH (exit 3, used by nothing else)"*. It does not.
`selftest()` (`:1470`) returns **`0` on success** and `3` on failure or zero units, and a clean
graded run also exits `0` (`main()`, `:1509`). **On the success path the exit code cannot
distinguish "the selftest passed" from "a grade ran clean"** — which is exactly the `D4-DEF-1`
confusion the header claims to have repaired. It is *mitigated*, not repaired, by two other
differences that are real: a selftest writes **no** `--out` file, and it prints `D7_SELFTEST` on
stdout. **This does not weaken the 65/65 result; it falsifies the claim the file makes about its own
exit contract.**

### 1.3 THE GRADE — **THE GRADER REFUSED**

Invocation (registered arms, `F-S`/`F-P` excluded because §6 blocks them):

    python3 d7_grade.py --base . --work ./O --out ./D7R_grade_O.json \
        --cl-target ./O/d7_cl_target.json --arms P1,P2,O

**Result:**

    D7_GRADER REFUSED G2: {"absent": "./O/d7_major_history.json"}
    exit 2, no --out file written

Identical refusal with the default arm set `P1,P2,O,F-S,F-P`, and identical under `python3 -O` (§7).

**THE MECHANISM, AND IT IS STRUCTURAL, NOT A MISHAP.** `O/d7_major_history.json` and
`O/d7_endpoint_dvs.json` are written by `d7_extract_endpoint.py`, and the frozen launcher
`d7r_run_arm.sh` invokes that extractor in **one place only — line 325, inside the `F-S`/`F-P`
branch**. Arm `O` never runs it. So:

> **THE FROZEN LAUNCHER DOES NOT PRODUCE, FOR ARM `O`, TWO OF THE FOUR ARTIFACTS THE FROZEN
> GRADER'S `G1` AGE GUARD REQUIRES AND THAT `G2` AND `G4` READ.** With `F-S`/`F-P` blocked by §6,
> the registered instruments cannot be composed into a grade of arm `O` at all.

This is recorded as **`D7R-DEF-8`**. The one instrument that would close it is
`d7_extract_endpoint.py` — **the instrument this item's own §6 and §10 record as carrying
`D7-DEF-4`**. Running it to satisfy the grader is the same action as working around the refusal, so
this lane did not run it. **It is the supervisor's call, and it is a call about a frozen
document's arm plan, not a formality.**

### 1.4 Gate dispositions

**No gate verdict exists for D7R arm `O`.** The grader refused before writing any output. The
column below labelled *diagnostic* was produced by calling the **frozen instrument's own gate
functions** on the **real artifacts**, writing no `--out` and producing no verdict. **A diagnostic
is not a gate verdict and is never lifted as one.**

| gate | disposition | diagnostic reading, and the artifact it cites |
|---|---|---|
| **`G1`** completion + age guard | **NO VERDICT**; and **`NOT ESTABLISHED` as named** (see below) | `pass: false`. `rc` read `0` for all three arms (`ledger.txt`). Age guard checked **2 of 4** artifacts: `opt_IPOPT.txt` and `OptView.hst` both `newer: true` (mtime `1787711453` > datum `1787697486`, `O/.d7_age_datum`); **`d7_major_history.json` ABSENT, `d7_endpoint_dvs.json` ABSENT** |
| **`G2`** CL bands A/B | **NO VERDICT — THIS IS THE GATE THAT REFUSED** | `{"absent": "./O/d7_major_history.json"}` |
| **`G3`** IPOPT exit | diagnostic | `EXIT: Maximum Number of Iterations Exceeded.`; 31 iterate rows, `highest_iter 30` == registered `max_iter 30`; `converged: false`, `cap_stop: true` — `O/opt_IPOPT.txt` |
| **`G4`** band C | diagnostic — **OUTSIDE THE BAND** | `CD` **`0.033117368` → `0.023048932`** = **`30.402283 %`** against frozen band **`[3.0, 25.0] %`**, prediction 10 % — `O/opt_IPOPT.txt`. **No cross-check against the history: the history does not exist** |
| **`G5` `G6` `G6b` `G7`** FD / plant / blind reader / count control | **`BLOCKED`** (§6) | zero FD artifacts. The grader's own words for this state: *"NOT_MEASURED — zero FD artifacts present; a plant that was never made is not a passing plant"* (`d7_grade.py:929-930`) |
| **`G8`** decomposition determinism | diagnostic | `pass: true`. Maps A and B **identical**, 4 subdomains, `10635/10506/10538/10441` summing to **42,120** == registered `NCELLS` — `P1/d7_decomp_A.json`, `P1/d7_decomp_B.json` |
| **`G9`** two rows, distinct IDWarp `.so` md5 | **`BLOCKED`** (§6) | `two_rows_present: false` — both `F-S` and `F-P` absent from `ledger.txt`. `pass: false`, but `map_verdict` does not hard-fail `G9` when the rows are absent (`d7_grade.py:840`) |
| **`G10`** caps | diagnostic `pass: false`, **and the failure is an INSTRUMENT-PROVENANCE MISMATCH, not a run defect** | see **`D7R-GRADER-DEF-6`** below |
| **`G11`** OOMKilled | diagnostic | `pass: true`, `status: MEASURED`, 3 of 3 arms read, `inspect(exit,oomkilled)=[0 false]` on every arm — `ledger.txt` |
| **`G12`** CPU placement | diagnostic `pass: false`, **on one limb of one arm** | arm `O`: 4 rank files, affinity `[2],[3],[4],[6]` all single-core, all distinct, inside `cpuset 2,3,4,6`, `delivered_cores_mean 3.9919 ≥ 3.0` — **every limb passes**. `P2` likewise. **`P1` fails on `delivered_cores_mean=[NOT_MEASURED]`** — its 11 s run produced no sampler mean — `ledger.txt`, `O/d7_placement_rank{0..3}.json` |
| **`G13`** adjoint health, band F | diagnostic | `pass: true`. **64** `PetscConvergedReason` lines, **all `2`**, `min_reason 2`, `n_nonpositive 0`, `n_minus9 0` — `O_20260825T223806Z_2844774.log` |
| **`H1`** colouring provenance | **`PASS`** | `D7R_H1_PASS item=D7R arm=P2 rc=0 stamp=20260825T222104Z_2765730 md5=a2e5f3172f3b889656e51b67ca4e55a6` (`O_run.log`); three refusal cases fired first (`RESULTS_P2_H1_H2.md` §4) |
| **`H2`** baseline agreement | **`PASS` at exactly zero** | `CD` and `CL` relative difference **`0.000e+00`** against the inherited D7 numbers (`RESULTS_P2_H1_H2.md` §2) |

**`G1` is recorded `NOT ESTABLISHED` as named**, under the one-way disposition. Its docstring
(`d7_grade.py:225`) names **three** clauses: *"`rc == 0`, the producer's own output FILE terminal,
and THE AGE GUARD"*. The function implements **two**. There is no `End`-line, no `.log.ok` and no
terminal-statement check anywhere in `g1_completion` — the string `End` occurs in this file exactly
once, **inside that docstring**. Recorded as **`D7R-GRADER-DEF-7`**. The disposition removes
nothing here (`G1` has no verdict either way), and it is one-way: it may only remove a `PASS`,
never create one.

> **The `rc` clause IS implemented, and this lane did not take that on the page — it drove the
> condition. See §6.**

**CLAUDE.md rule 4's terminal clause is satisfied for arm `O`, by the LAUNCHER and not by `G1`:**
`rc=0`; **49 `End` lines**; last `ExecutionTime = 13947.88 s`; log terminating on
`Finalising parallel run`; success marker `O_20260825T223806Z_2844774.log.ok.20260825T223806Z_2844774`
written; both graded artifacts newer than `O/.d7_age_datum`. **That is the launcher's check, not
the gate's, and the two are not interchangeable.**

### 1.5 `D7R-GRADER-DEF-6` — the frozen grader carries **D7's** caps, not D7R's

`PREREGISTRATION.md` §5 says gates `G1`–`G13` are *"inherited unchanged from D7's frozen §5 and
graded by the committed `d7_grade.py`"*. **The gate LOGIC is inherited. Three of the THRESHOLDS the
grader carries are D7's numbers and they contradict D7R's own §4.**

| constant in `d7_grade.py` | value it carries (D7 §8) | D7R's own registered value (§4) |
|---|---|---|
| `CAPS["P2"]` (`:59`) | **60.0** | **120.0** |
| `CAPS["O"]` (`:59`) | **600.0** | **900.0** |
| `ITEM_CEILING_CORE_MIN` (`:60`) | **928.0** | D7R registers **per-arm** ceilings (32.0 / 480.0 / 3600.0) and **no item ceiling** |

Consequence, measured: `g10_caps` reports `cap_matches_registered: false` for `P2` and `O`, and
`overrun_core_min: 332.533` for arm `O` — **against D7's 600.0**. **The true overrun against
D7R's registered cap is `32.533` core-min** (§3). `G10` is **not** a hard gate in `map_verdict`, so
this could not have changed the verdict token; it would have put a `GATE FAIL`-shaped reading on the
page for a reason that is instrument provenance, not run behaviour. **Reported, not repaired.**

---

## 2. THE `ROW=SHIPPED` QUESTION — SETTLED FROM THE ARTIFACTS

| question | measured answer | artifact |
|---|---|---|
| image digest arm `O` actually ran on | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `ledger.txt` `ARM=O … DIGEST=`, **and independently** `O_run.log` `D7_IMAGE_OK row=SHIPPED image=dafoam/opt-packages:latest digest=…` |
| IDWarp `.so` md5 actually imported | **`f0fcb488e0e98156575cd19548e91663`** | `D7_IDWARP_SO_MD5:` in `ledger.txt` and `O_run.log`, printed from inside the process that loaded the library |
| is that digest SHIPPED or PATCHED? | **SHIPPED** | `docs/dafoam/TOOLCHAIN_INVENTORY.md` §3 records `dafoam/opt-packages:latest` as image id `9d45679d55fd`, digest `sha256:9d45679d55fd…90f07fc`, *"Imported from -"*, 7.83 GB, and states *"the image on this box **is** the image every published number was measured on"* |
| is that `.so` md5 stock or patched? | **stock** | `cases/dafoam/MATRIX_CONTRIBUTION.md:113` records stock `libidwarp.so` md5 **`f0fcb488…`**, 491,344 B; `:114` records the patched build as **`85f59e87253e0a71a813f64ca6e4c425`**, also 491,344 B and also reporting version `2.6.2` |
| what did the frozen pre-registration register arm `O`'s row as? | **SHIPPED** | `PREREGISTRATION.md` §3 (`O … row SHIPPED`) and §7 (*"`P1`/`P2`/`O` are **SHIPPED-only**"*) |

**THE LEDGER'S `ROW=` LABEL AND THE MEASURED DIGEST AGREE, AND BOTH AGREE WITH THE REGISTRATION.
THERE IS NO DEFECT HERE.**

**CORRECTION TO THE BRIEF, on the source rather than the answer.**
`docs/dafoam/TOOLCHAIN_INVENTORY.md` at `HEAD` **does not name `dafoam-idwarp-rot:v1` at all** and
carries neither the PATCHED digest `sha256:2927768a16ac…f6d35` nor the patched `.so` md5
`85f59e87…`. That file can settle only the SHIPPED half. The PATCHED half is settled from
`cases/dafoam/MATRIX_CONTRIBUTION.md:113-114`, which carries both, and from
`TOOLCHAIN_INVENTORY.md` §4, which states the rotation patch is in **no** container image and
exists only as a host-side build. **Naming one file as the authority for both rows would have been
a citation this lane could not make good on.**

### 2.1 Which row D7R has bought

* **SHIPPED — BOUGHT.** `P1`, `P2` and `O` all ran on the stock image with the stock IDWarp, and
  the digest and `.so` md5 were both printed from inside the running process.
* **PATCHED — `BLOCKED`.** `PREREGISTRATION.md` §7 registers the PATCHED row as bought *"only by
  `F-P`"*, and §6 gates `F-P` on the `D4-DEF-4` repair *"which this item does not author"*. The
  correct token is **`BLOCKED`**, not `PENDING`: the obstruction is a **named, unlanded repair in
  another item**, not a queue position. `PENDING` is reserved for "not yet run"
  (`CLAUDE.md` rule 1).
* **Consequently, and exactly as §7 required in advance:** *"if this item completes with `F-P`
  blocked, IT IS NOT A TWO-ROW DAFOAM VERDICT and must say so"* (`DAFOAM_CHARTER.md` §6).
  **D7R IS NOT A TWO-ROW DAFOAM VERDICT.** This record says so.

---

## 3. THE CAP OVERRUN — REPORTED, NAMED SEPARATELY, NEVER ABSORBED

**Measured**, `ledger.txt` and `O_run.log`:

    D7R_CAP_CROSSED arm=O core_min=900.267 cap=900.0 ceiling=3600.0
                    action=REPORTED_RUN_CONTINUES supervisor_decides

| | |
|---|---|
| registered CAP (§4) | **900.0** core-min |
| actual | **932.533** core-min |
| **overrun** | **32.533 core-min = 3.615 % of the cap** |
| CEILING (§4, R1) | **3600.0** core-min — `ceiling_hit=no`; the run used **25.9 %** of it |
| derived cost of the overrun | **$0.0278** — DERIVED at $0.0513/core-h, **not measured** |
| what the run terminated on | its registered **`max_iter 30`**, not the cap — `EXIT: Maximum Number of Iterations Exceeded.`, `O/opt_IPOPT.txt` |

**SUPERVISOR'S RULING, RECORDED AND NOT RE-LITIGATED BY THIS LANE: the continuation STANDS and the
cap DOES NOT MOVE.** Grounds, as given:

1. **§R1 registered the reporting-cap design IN ADVANCE**, deliberately, because D7's hard
   `timeout` `SIGKILL` had made arm `O` structurally unreachable (§0, §R1).
2. **The run terminated on its registered `max_iter 30`, not on the cap.** The overrun bought the
   last majors of a registered 30-major ladder; a kill at the cap would have produced a truncated
   ladder and a `NOT A RESULT`.
3. **The crossing is 3.6 % of the cap, $0.0278 derived, and the 3600.0 ceiling was never
   approached.**

**The overrun is REPORTED as an overrun and is named separately in every cost statement below. It
is never folded into a ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

**REFERRED UPWARD, NOT ANSWERED HERE.** The general question — whether a frozen document may
register a cap that **reports** rather than **stops**, when `CLAUDE.md` rule 12 says an overrun
**stops the run** — is referred by the dafoam-supervisor as a charter question. **This lane does
not answer it and this record does not presume its answer.**

---

## 4. COST CALIBRATION — `CLAUDE.md` rule 12, the 2026-08-23 clause

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.** The box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Core-minutes are MEASURED from
`ledger.txt`. Every dollar figure below is DERIVED.**

### 4.1 Arm `O`

| | |
|---|---|
| predicted (§4) | **570.0** core-min — basis *"19.0 core-min/major × 30 majors, carried from D7 §2a"* |
| actual | **932.533** core-min (`ledger.txt`, `wall_s=13988 ranks=4`) |
| **ratio actual/predicted** | **1.6360** |
| derived cost | **$0.7973** DERIVED |

**ATTRIBUTION OF THE 1.636 GAP.**

* **Contention — NOT ATTRIBUTED, BECAUSE NO UNCONTENDED CONTROL WAS BOUGHT.** There is no np=4 run
  of this arm on an idle box to compare against, and this lane will not attribute to contention
  without one. **What IS measured:** `delivered_cores_mean=[3.9919 n=925]` against 4 requested =
  **99.80 % of requested cores delivered**, with `siblings_pre=[]` and `siblings_post=[]` — **no
  peer container shared the cpuset for the whole run**. That bounds the *sibling-contention* share
  at **≤ 0.20 %**, i.e. **≤ ~1.9 core-min of the 362.533 core-min overshoot**.
  `max_nr_throttled=52435` records the container hitting **its own cgroup quota**; with four ranks
  on a four-core quota that is expected, and it is **not convertible into lost work without a
  control**. Those are two different claims and only the first is supported.
* **Misprediction — essentially the entire gap.** The basis assumed **one primal + one adjoint per
  major**. `O/opt_IPOPT.txt`'s own summary block records **46 objective function evaluations** and
  **31 gradient evaluations** for **30 majors** — **1.53 primals per major**, from IPOPT line-search
  backtracking. Measured **31.084 core-min per major** (932.533/30) against **19.0** predicted =
  **1.636×**. **The per-major basis was right about the structure and wrong about how many function
  evaluations a line search buys.**
* **Waste — 0 core-min identified**, and named separately as charter §6 requires rather than
  absorbed. Preflight aborts (`H1_control_test.log`, `H1_testA/B/C.log`) refused **before any
  container ran** and cost nothing. **One measurement gap, stated rather than estimated:** the
  `D7-DEF-4` witness probe did run a container (`D7R_DEF4_WITNESS.txt`, `rc=0`) and
  `d7r_def4_witness_test.sh` **records no core-minutes at all**, so that spend is **UNMEASURED**. It
  is not estimated here.

### 4.2 Item roll-up

**Verified per arm from `ledger.txt`, and confirmed independently by the frozen grader's own
`g10_caps`, which computes `total_actual_core_min: 995.999`.**

| arm | predicted (§4) | actual (`ledger.txt`) | ratio |
|---|---|---|---|
| `P1` | 0.30 | **0.733** | 2.44 (**+0.43 core-min absolute**) |
| `P2` | 60.1 | **62.733** | **1.0438** |
| `O` | 570.0 | **932.533** | **1.6360** |
| **item (arms fired)** | **630.4** | **995.999** | **1.5799** |

Derived: **$0.8516** for the item, DERIVED, not measured.

**CORRECTION TO THE BRIEF — A DOUBLE-COUNT.** The roll-up as handed to this lane read
*"P1 0.733 + P2 62.733 + colouring build 24.43 + O 932.533"*. **The colouring build is INSIDE
`P2`'s 62.733 and adding it again double-counts by 24.43 core-min.** Verified three ways:
`PREREGISTRATION.md` §4 prices the colouring **as a term of `P2`'s 60.1 basis**; the cache
`dRdWColoring_4.bin` was written **2026-08-25 22:27:49**, inside `P2`'s window (22:21:04 →
~22:36:45); and the launcher publishes it from `P2` (`D7R_COLORING_PUBLISHED_FRESH item=D7R arm=P2`).
**The item total is 995.999 core-min, not 1,020.429.**

**AND THE COLOURING PRICE — `C-89` — CAME IN.** §R2 priced the colouring at **24.43 core-min**,
measured from D7's log. D7R's own `P2` log records the build from **34.74 s** to
**`Calculating dRdW Coloring... Completed! 397.31 s`** = 362.57 s wall × 4 ranks ÷ 60 = **24.17
core-min**. **Ratio 0.99 — the term `C-89` forced into the document is accurate to 1.1 %.** That is
the calibration datum this item was designed to produce.

### 4.3 Against the ceilings

| | |
|---|---|
| per-arm ceilings (§4, the only ceilings D7R registers) | `P1` 32.0, `P2` 480.0, `O` 3600.0 — **none hit** (`ceiling_hit=no` on every row) |
| the frozen grader's `ITEM_CEILING_CORE_MIN = 928.0` | **D7's number, not D7R's** (`D7R-GRADER-DEF-6`). D7R's 995.999 exceeds it. **D7R never registered an item ceiling**, so this is reported as an instrument mismatch and **not** as a budget breach |

---

## 5. PREDICTIONS, SCORED — HIT / MISS / UNSCORED, NEVER ADJUSTED

| # | registered prediction | where | outcome |
|---|---|---|---|
| 1 | `O` reaches `max_iter` 30 without converging → **`GATE REACHED`, never `PASS`** | §11 | **HIT on its antecedent** — `max_iter 30` reached, not converged (`EXIT: Maximum Number of Iterations Exceeded.`). **`GATE REACHED` is a CEILING in that clause, not an award**, and it did not bind: band C failed, and D7 §5 `G3` registers the else-branch as `NOT A RESULT` |
| 2 | convergence inside 30 majors *"would be a genuine surprise"* | §11 | **HIT** — no convergence; no surprise to report |
| 3 | band C prediction **10 %**, band **[3 %, 25 %]** | §4 (D7 §4 line 94) | **MISS** — **30.402283 %**, outside the band on the **high** side. *"A result outside the band is reported as a MISS, never re-banded"* (`d7_grade.py:349`). **The optimiser did better than the band's upper bound and the frozen instrument therefore refuses to call it a result. That is the rule working, not the rule failing** |
| 4 | `d7_extract_endpoint.py` will read `patchV[0]` as **29.16**, not 291.6 | §6 | **HIT — CONFIRMED.** Read `29.160000000000004`; and `patchV[1]` read `0.30600000000000005` = 3.06 × 0.1, a second confirmation the prediction did not claim (`D7R_DEF4_WITNESS.txt`, `D7R_DEF4_CONFIRMED.md`) |
| 5 | the grader refuses on real artifacts → **a finding under R4** | §11, §R4 | **HIT, AND IT FIRED.** §1.3 above is that finding |
| 6 | `O` predicted **570.0** core-min | §4 | **MISS** — 932.533, ratio 1.636 (§4.1) |
| 7 | `P2` predicted **60.1** core-min, its adjoint term registered as a **FLOOR** | §4 | **HIT** — 62.733, ratio 1.044; the floor held |
| 8 | the colouring priced at **24.43** core-min (`C-89` made binding) | §R2 | **HIT** — 24.17 core-min measured in D7R's own `P2` log, ratio 0.99 |
| 9 | `H2` refuses — D7's `P2` is not reproducible | §11 (a falsifier) | **DID NOT FIRE** — agreement at exactly `0.000e+00` |
| 10 | any `G8` failure → every np=4 number `NOT A RESULT` | §11 (a falsifier) | **DID NOT FIRE** — maps identical, 42,120 cells == registered |
| 11 | `MemAvailable ≥ 16.0 GiB` throughout, absolute floor 12 GiB | §8 | **HIT** — `memavail_pre 26.80`, `memavail_min_during=[16.822 n=926]`, `memavail_post 28.23`; never below the floor |
| 12 | R1: a converging solve **reports and continues**; a runaway is still stopped | §R1 | **HIT** — `D7R_CAP_CROSSED … REPORTED_RUN_CONTINUES`; the run finished on `max_iter`, and the 3600.0 ceiling was never approached |
| — | bands A and B (`G2`, CL feasibility per-major and final) | §4 | **UNSCORED** — `d7_major_history.json` does not exist. **The final constraint violation `2.23e-06` is visible in `O/opt_IPOPT.txt`'s `inf_pr` column at iterate 30, but band A is a per-major test over the whole history and that history was never written. It is not scored from one row** |

---

## 6. THE `rc` CLAUSE — DRIVEN, NOT READ

A defect class was found the same night in D4's frozen grader and its supplement: `g_completion()`
names three clauses and **implements only the age guard**, recording `rc` into its report and never
comparing it to `0` — so D4 emitted `G1_completion_and_age = PASS` on a run whose arm `F` ledger row
reads `rc=1`.

**`d7_grade.py` DOES NOT CARRY THAT DEFECT, AND THIS LANE DID NOT TAKE THAT ON THE PAGE.** The
condition was **driven**: the frozen grader was copied to a sacrificial location (md5 asserted
identical, `10eb6d0928addc56272854f017e01538`), handed a complete input set, and a **required arm's
ledger `rc` was set to `1`**.

| fixture | `ARM=O` ledger `rc` | verdict emitted |
|---|---|---|
| **B** — band C forced inside `[3, 25] %` | **0** | **`GATE REACHED`** — *"band C holds (10.0000 % in [3.0, 25.0]); band A holds"* |
| **B** | **1** | **`NOT A RESULT`** — *"G1 completion/age guard"* |
| **A** — the **real** arm-`O` `opt_IPOPT.txt` | **0** | `NOT A RESULT` — *"cap-stop AND a frozen band did not hold; band C pass=False; band A pass=True"* |
| **A** | **1** | `NOT A RESULT` — *"G1 completion/age guard"* |

**THE VERDICT TOKEN CHANGES on fixture B: `GATE REACHED` → `NOT A RESULT`.** The guard is shown to
work by making the condition it guards actually occur. On fixture A — the real IPOPT file — the
token was already `NOT A RESULT` for band C, and the `rc` flip **moved the reason** to
`G1 completion/age guard`, so the `rc` clause is live on the real artifacts too. The implementing
line is `d7_grade.py:244-245`: `if rc != 0:` / `ok = False`.

**HONEST STATEMENT OF WHAT THE FIXTURES ARE.** Both carry the real `ledger.txt`, the real arm log,
the real `opt_IPOPT.txt` (fixture B's final objective altered by one line, deliberately, to put band
C inside its band), the real `P1` decomposition maps and the real placement files. The
`d7_major_history.json` and the two FD artifacts are **synthetic** — the history built from the real
IPOPT objective column and marked `"_SYNTHETIC"` in the file, the FD documents built by the
grader's **own** `_st_fd_doc()` fixture builder. **They are a guard demonstration and are not D7R
artifacts. No number from them is reported as a D7R measurement anywhere in this record.**

**A SECOND FINDING FELL OUT OF FIXTURE A, AND IT MATTERS TO THE ITEM.** With `F-S`/`F-P` blocked by
§6 there are **zero FD artifacts**, and `map_verdict` hard-fails on `G6`, `G6b` **and** `G7` for
that absence (`d7_grade.py:925-928`, `:834-838`). **So even had the extractor been run, the frozen
grading path could not have emitted `GATE REACHED` for D7R as actually armed.** Recorded as
**`D7R-DEF-9`**: `PREREGISTRATION.md` §11's registered ceiling outcome is **unreachable by its own
registered grading path** while §6 holds. Reported; **not repaired by this lane**.

---

## 7. `-O` EXPOSURE

**`assert`-based guards, refusals and gates vanish under `python3 -O`. This was tested, with a
planted control first.**

**PLANTED CONTROL — is `-O` actually in effect on this interpreter?** A probe that asserts `False`:
plain `python3` → `__debug__=True`, `ASSERT-GUARD FIRED`; `python3 -O` → `__debug__=False`,
**`ASSERT-GUARD VANISHED`**. **The flag demonstrably strips asserts here**, so the invariances below
are measurements, not a null flag.

| what was run under `-O` | result |
|---|---|
| **the real D7R grade** | **`D7_GRADER REFUSED G2: {"absent": "./O/d7_major_history.json"}`, exit 2** — **byte-identical to the plain run. THE REFUSAL FIRES UNDER BOTH.** |
| the §6 `rc` demonstration, all four cells | **identical verdicts and identical `because` lists** under `-O` |
| `--selftest` | `units=65 passed=65 failed=0`, `UNEXERCISED=0`, exit 0 — identical |

**AND THE REASON IS MEASURED, NOT ASSUMED.** An AST walk of the frozen grader counts
**`ast.Assert` nodes = 0**. `__debug__` is never referenced and no `.__doc__` is read. **Every
refusal in this file is `raise Refuse(...)` and every gate failure is a boolean branch — there is no
`assert` anywhere for `-O` to strip.** That is why the refusals survive, and it is a property of the
file rather than luck.

**The selftest passing under `-O` is, as the brief says, the weak reading.** The load-bearing one is
the first row: **the refusal fires under `-O`.**

**Nothing was repaired here.** No measurement script was edited by this lane.

---

## 8. WHAT THIS RECORD DOES **NOT** CLAIM

* **It does not claim a graded verdict for arm `O`.** The registered grading path refused. Every
  gate reading in §1.4 marked *diagnostic* was produced by calling the frozen instrument's own
  functions outside a grade, and **a diagnostic is not a gate verdict.**
* **It does not claim `GATE REACHED`.** `GATE REACHED` is the **ceiling** §11 set for an
  unconverged `max_iter` stop. It was never earned: band C failed and the grader never ran to a
  verdict.
* **It does not claim the 30.402283 % drag reduction as a result.** It is a number in a file
  (`O/opt_IPOPT.txt`) that **no gate has ruled on**, and it lies outside the band that was frozen to
  rule on it.
* **It does not claim bands A or B.** `d7_major_history.json` does not exist; the per-major CL
  history was never written. The final `inf_pr = 2.23e-06` is one row, not the band.
* **It does not claim an endpoint gradient, an FD table, or any gradient verification.** `F-S` and
  `F-P` are `BLOCKED`; `G5` — this family's bright line — **was never run on this item.**
* **It does not claim a two-row DAFoam verdict.** SHIPPED only. The PATCHED row is `BLOCKED`
  (§2.1).
* **It does not claim a mesh-convergence result.** No Roache triple exists on this case; none was
  attempted (`CLAUDE.md` rule 5 has nothing to gate here because nothing was formed).
* **It does not attribute any part of the 1.636 cost ratio to contention.** No uncontended control
  was bought (§4.1).
* **It does not price the `D7-DEF-4` witness probe.** That container's core-minutes were never
  recorded and are stated as unmeasured, not estimated (§4.1).
* **It does not repair `D7R-GRADER-DEF-5`, `-DEF-6`, `-DEF-7`, `D7R-DEF-8` or `D7R-DEF-9`, and it
  does not amend any frozen file.** They are reported to the dafoam-supervisor, who reads every
  measurement-script diff personally, as a diff, before its output is believed.
* **Nothing here was sent, filed, uploaded, registered, posted or commented anywhere**
  (`CLAUDE.md` rule 7).

---

## 9. OPEN, FOR THE SUPERVISOR

1. **`D7R-DEF-8`** — arm `O` cannot be graded by the registered path, because the launcher never
   runs `d7_extract_endpoint.py` outside the blocked `F-S`/`F-P` branch. The only instrument that
   closes it is the one §6 and §10 record as carrying `D7-DEF-4`. **This lane did not run it.**
2. **`D7R-DEF-9`** — with §6 holding, `map_verdict` hard-fails `G6`/`G6b`/`G7` on the absence of FD
   artifacts, so §11's registered ceiling outcome is unreachable by its own registered path.
3. **`D7R-GRADER-DEF-6`** — the frozen grader carries D7's `CAPS` and item ceiling.
4. **`D7R-GRADER-DEF-7`** — `g1_completion` implements two of the three clauses its docstring names.
5. **`D7R-GRADER-DEF-5`** — the `--selftest` exit contract the file documents is not the one it has.
6. **The charter question on reporting-versus-stopping caps** is referred upward and is
   **unanswered here** (§3).
