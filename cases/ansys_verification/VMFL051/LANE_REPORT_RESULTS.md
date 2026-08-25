# VMFL051 — LANE REPORT: run, grade, records

**From:** `ansys-lane-opus` (Opus 5), ansys-verification team.
**To:** `ansys-verification-supervisor`.
**Date:** 2026-08-25.

**THIS IS THE REPORT OF RECORD, ON DISK, BECAUSE `SendMessage` TO THE SUPERVISOR WAS
UNREACHABLE** — the tool returned *"No agent named 'ansys-verification-supervisor' is
reachable"*. That is the fallback this lane's brief specifies, and it is `L-306`: a
lane's report of record lives on disk in its own case directory, committed. The
supervisor's mid-task course corrections (the `C-50` collision, the register
correction, the lesson number) arrived and **were executed in full**; this file is the
reply to them.

---

## 1. COMMITS

| sha | subject |
|---|---|
| `fc46ad2d` | VMFL051 run artifacts filed, 25 files — the evidentiary core of a `NOT A RESULT` |
| `ef3499f9` | VMFL051 GRADED `NOT A RESULT`, on two independent clauses of rule 5 (`RESULTS.md`) |
| `393476d9` | `ANSYS_VALIDATION_REGISTER.md` row #4 |
| `dc0a096c` | **EMPTY COMMIT — a defect of this lane's, disclosed in §5** |
| `0c3f3054` | `COST_CALIBRATION.md` row **`C-51`** for VMFL051 |
| `969c6074` | register foot-note correcting row #4's `C-50` citation to `C-51` (row #4 NOT edited) |

Every one landed through the `CLAUDE.md` rule-10 private-index protocol with HEAD
captured once per invocation, a `git diff-tree --stat` assertion before, a CAS on
`refs/heads/main`, and the post-commit `git diff HEAD~1 HEAD --stat` verification
after. **The shared index was never touched**, and its ~50 staged paths — including
the staged deletions of this team's own VMFL051 files — were **inspected, never
reverted** and never entered any commit, because every commit was built from
`read-tree HEAD` plus explicit paths.

---

## 2. THE VERDICT

# `NOT A RESULT`

**Cost 23.3167 core-minutes** (1 399 wall s × 1 rank ÷ 60, serial) of a frozen **28
core-minute** cap — **83.27 % used, never reached**, no `CAP_EXCEEDED.txt`.
**$0.019936 DERIVED, NOT MEASURED**, at $0.0513/core-h, c7a.4xlarge, reported-by-owner.

**Two independent clauses of `CLAUDE.md` rule 5 each produce it on its own:**

1. **Rule 5 step 1 — the frozen plateau clause. L1 AND L2 BOTH FAIL.** Peak-to-peak of
   the `volAverage(Ma)` gate series over each level's last 20 %: **L1 6.240e−03** (339
   of 1 693 rows) and **L2 3.535e−03** (673 of 3 365) against a frozen **1.000e−03** —
   **6.24× and 3.54×**. Only **L3** plateaus, at **8.549e−04** (1 343 of 6 714), 0.85×.
2. **Rule 5 step 2 — the Roache triple is `OSCILLATORY`.** Coarse **3.2278606097**,
   medium **3.2233427020**, fine **3.2294355513**; **d32 = +4.517908e−03**, **d21 =
   −6.092849e−03**, **R = −1.348600**. **No observed order and NO GCI QUOTED** —
   correctly, the values are not monotone. `f_extrapolated` and `gci_fine` are both
   `null`, so Amendment 1's ρ and dev_extrap are **not computable**: this is that
   amendment's reading **(d)**, and none of (a), (b) or (c) is available or claimed.

**Gate value (L3, finest): `Ma = 3.2294355513`.** Manual printed target 3.2370
(Table .51.1), frozen band **± 0.5000 %**, deviation **−0.233687 %** — inside.
**Diagnostic only, never the gate:** closed-form exact **3.2355411372251854** at
**γ = 1.3990093734749485** from the manual's own Cp = 1006.43 and MW = 28.966,
deviation **−0.188704 %** against a **± 0.25 %** diagnostic band — inside.
Context only: Fluent 3.2316, CFX 3.2354; **this box has neither solver**.

**All three planted-zero controls FIRED** — PZ-1 dat reader, PZ-2 `Ma` field reader on
the real 99 840-cell **non-uniform** field, PZ-3 reference solve (identity returned
14.999999999999972° against 15°). **Declared inner-zone clause passed** at
2.284871e−04 vs 1e−2. **Strict completion held at all three levels**, with the freeze's
two declared departures for an adaptive-step transient solver.

**§4 of `RESULTS.md` states plainly what the supervisor asked for:** the gate value
sits inside **both** bands and inside the manual's own 3 % goal by **12.8×**, and rule
5 makes it `NOT A RESULT` anyway. Had the order been read gate-first this would be an
unsupported `PASS`. **The discipline is working as designed**, and the rule's one-way
property held.

---

## 3. MECHANISM — leading candidate, NOT established (`RESULTS.md` §3)

The level-to-level differences are **the same order as the coarse levels' own residual
unsteadiness**: |d32| = 4.518e−03 is **0.72×** L1's peak-to-peak and **1.28×** L2's;
|d21| = 6.093e−03 is **1.72×** L2's. On that arithmetic the triple is **plausibly
measuring transient noise rather than discretisation error**.

**Four named reasons it is not claimed as established:** the arithmetic is a
consistency argument, not a demonstration; **L2, not L1, is the outlier** (3.2279 /
3.2233 / 3.2294 — the medium level dips below both neighbours) and nothing explains why
the middle level specifically; **no time-refinement study was run and none was
pre-registered**; and L3 being both plateaued and closest to exact is suggestive, not
evidence. **No re-run is proposed and no `endTime` is recommended** — the supervisor's
call.

---

## 4. RATIO AND CALIBRATION — row `C-51`

**actual / predicted = 2.0634×** (23.3167 / 11.3). Cap fraction 0.8327×.

**The finding inverts this ledger's usual shape: the frozen estimate's physics was
right and its environment assumption was wrong.**

- **Solver CPU MEASURED 534.52 s** (final `ExecutionTime` 7.71 + 59.31 + 467.50)
  against a 637 s solver-plus-function-object allowance = **0.839×, inside and
  conservative**.
- **The per-cell-step rate borrowed from cfd's F3 COMPRESSION cases transferred to this
  EXPANSION to within 3.7 % at worst:** measured **7.2982e−07 / 7.0615e−07 /
  6.9742e−07** s/cell-step against the frozen **7.24e−07** = **1.008× / 0.975× /
  0.963×**, and the rate is **flat in mesh size**. This **vindicates `C-47`'s
  constant-rate recommendation on a second solver**. Price `rhoCentralFoam` 2D on this
  box at **7.0e−07 s per cell-step**.
- CFL step counts also good: **0.965× / 0.959× / 0.956×**.
- **The only real misprediction is the meshing term:** ~40 s allowed, **≤ 2 s MEASURED
  as a bound** (solver `ClockTime` sums to 1 397 s of a 1 399 s run wall) — **≥ 20×**
  too large. A bound and not a value, because `blockMesh` and `topoSet` print no
  `ExecutionTime` on v2606.
- **CONTENTION 864.48 s = 14.408 core-min, MEASURED, named SEPARATELY, netted off
  neither column nor the ratio** (`COMPUTE_BUDGET_CHARTER.md` §6) — **62 % of the
  entire spend on this item**. loadavg **68.38 → 75.84** on `nproc = 16` from two
  `buoyantBoussinesq*` at 99.9 % and five `tesseract` at 84–89 %, **none of it this
  case's and none of it touched**. Measured `ClockTime`/`ExecutionTime`: **L1 1.17×,
  L2 3.49×, L3 2.53×** — L1 ran before the load built and is the only level whose wall
  is near its CPU.
- **WASTE 0.000 core-min**, named separately, netted off nothing.

**Instrument note carried into `C-51`, `RESULTS.md` §7.1 and `CONTENTION.txt`:** the
cap is denominated in **core-minutes** and was enforced as a **wall-clock `timeout`**.
They coincide here **only because the run is serial**. On an 8-rank job the same idiom
permits **8× the registered budget** before firing. Correct form:
**`timeout_seconds = cap_core_min * 60 / ranks`**. Referred; changing the launcher is
not this lane's call.

**Standing gap, PROPOSED AND NOT DECIDED:** the lab's estimating method has **no
contention term at all**. `C-47` left contention uncharacterised; `C-48` measured it
and found it minor; **here it is the whole story**. Referred to the supervisor and to
verification; **unruled**, and `C-51` does not act as though it were ruled.

---

## 5. DEFECTS OF THIS LANE'S, BOTH DISCLOSED

### 5.1 The `C-50` collision — repaired

Register row #4 cited *"Calibration row `C-50`"*. **`C-50` at HEAD is the cfd team's
F12 rung 1** (RAE 2822, AGARD AR-138 Case 9). This lane caught it independently in the
same minute the supervisor's message arrived, and repaired it as directed:

- **`C-51` landed at `0c3f3054`**, built from `git show HEAD:docs/COST_CALIBRATION.md`,
  with the **id re-derived inside the same shell invocation that wrote the tree**
  (max existing C-50 → C-51) and re-derivation wired into the CAS retry loop.
  **Verified after: all 50 pre-existing rows byte-identical; C-50 unchanged.**
- **Register foot-note at `969c6074`**, insertions-only (50 insertions, 0 deletions).
  **Row #4 NOT edited**; rows #1–#4 asserted byte-identical; the `D510` correction
  intact. The **"lines whose number changed above this section: 0"** claim is
  **VERIFIED BY HASHING** — prefix sha256 `54e232197d24d1f1…` identical before and
  after — not merely asserted.

**Cause, stated plainly and not softened, in both records:** the id was **derived
before the commit and not re-derived inside the committing shell invocation**, which
`CLAUDE.md` rule 11 requires in terms. **The timestamps are the proof that nothing
raced:** cfd's `C-50` landed at `cd1ac21a`, **01:09:21Z**; register row #4 landed at
**01:14:13Z** — **four minutes fifty-two seconds later**, so the id was already taken
and already visible at HEAD. **Contributing, and recorded as a factor and not an
excuse:** the worktree `COST_CALIBRATION.md` is **~19.8 kB shorter than HEAD**, so an
id derived from it is wrong before any race begins. **This is the team's SECOND
`L-292` instance, and it was committed inside the very row that cites `L-292`.**

### 5.2 An EMPTY COMMIT on shared history — `dc0a096c`

**`dc0a096c` carries `C-51`'s message and is EMPTY.** Its shell invocation aborted
inside the row-building step — **the HEAD blob of `COST_CALIBRATION.md` does not end
with a trailing newline**, which fired a build guard — and the invocation then
committed the **unchanged `read-tree` of HEAD** before the failure was noticed. By the
time it was inspected a peer (`4eb673a3`) had already committed on top, so it is
**LEFT STANDING and corrected forward rather than rewritten**: history on a shared
branch is inspected, never reverted. `0c3f3054` carries the actual row and its message
discloses the empty one.

**Fixed, not just noted:** the builder now **refuses to commit unless the tree actually
changed**. That guard **fired correctly once afterwards**, on the register note, and
blocked a bad commit.

---

## 6. ID CHECKS AT HEAD — the supervisor's follow-up 3

**Confirmed, and every id in row #4 was re-checked, not only the `C-` one.**

| id | at HEAD | state |
|---|---|---|
| `N-AV7` | **EXISTS** | repair **LANDED**, not open |
| `N-AV8` | **EXISTS** | repair **LANDED**, not open |
| `D510` → `D512` | **`D512` EXISTS**; the register already carried the dated correction at commit `23fed33c` | repair **LANDED**, not open |
| `L-292`, `L-300`, `N-AV9` | **EXIST** | cited safely |
| `C-50` | exists, **belongs to cfd** | **the single failing citation — corrected to `C-51`** |

`N-AV1`–`N-AV9` all exist. **Row #4 cites no `N-AV` and no docket id of its own, by
design** — none has been appended for VMFL051, and an id in prose before its append is
a prediction, not an identifier.

**Method note worth keeping.** This lane's first existence check for `L-307`/`L-309`
returned a **FALSE NEGATIVE**, because it matched `^## L-307\.` while those headings use
an **em-dash** rather than a period. Both exist. **An id-existence check must not assume
the separator** — the same class of error as `L-308`'s line-bounded grep.

---

## 7. NEXT FREE LESSON NUMBER — not written, as instructed

Re-derived from HEAD at `969c6074`: **max existing `L-310` → next free is `L-311`.**
**Nothing was written**; the wording is the supervisor's to rule on.

The candidate matches the supervisor's, with a second clause this lane hit itself:
*a records id must be re-derived inside the committing shell invocation — deriving it
even minutes earlier races every peer, and deriving it from a truncated worktree copy
races nothing but is wrong from the start; and the same invocation must refuse to
commit when the tree is unchanged, or an aborted build lands an empty commit under a
message claiming work it did not do.*

---

## 8. WHAT COULD NOT BE VERIFIED — stated plainly

- **The mechanism of §3 is a candidate, not established.** No time-refinement study
  exists and none was pre-registered.
- **Meshing time is a measured BOUND (≤ 2 s), not a measured value.**
- **The drafting lane's wall** (freeze §9.2's 35/60 pair) is **not measurable** from
  committed timestamps and is left **stated as absent, not approximated**. This
  grading lane's wall is a **floor** only, because `C-40`'s transferable fix — a lane
  should `date -u` into a scratch file as its **first** action — was **again not
  applied**. That is four rows recommending it and four not applying it.
- **~51 MB of OpenFOAM field data is on disk and deliberately NOT committed.** Every
  graded number comes from committed `.dat` series and logs, **with one exception:
  PZ-2 read the L3 `Ma` field directly**, so if that run root is cleared **PZ-2 becomes
  unreproducible from the repository alone**. Its firing is recorded in the committed
  grading JSON.
- **The manual defect** (p. 165 calls the flow *"incompressible"* while its own
  Physics/Models line on the same page says *"Compressible, inviscid flow"*; an
  incompressible treatment gives **no Mach change at all**, M 2.5 vs target 3.2370,
  **−22.77 %**, failing the gate by **45×**) and the **timeout-unit instrument defect**
  are recorded in `RESULTS.md` §5 and §7.1 and are **REFERRED** to the supervisor for an
  `N-AV`/`LESSONS` append under a genuinely free id. **This lane appended neither and
  cited neither.** Both are **`NOT FILED`** — contacting Ansys is Sanaa's alone.

---

## 9. FILES

- `cases/ansys_verification/VMFL051/RESULTS.md` — the record of the case
- `cases/ansys_verification/VMFL051/PREREGISTRATION.md` — frozen, blob `7dad5616…`, **not edited**
- `cases/ansys_verification/VMFL051/grade_vmfl051.py` — frozen comparator, blob `acad1aff…`
- `verification/runs/ansys_verification/VMFL051/` — artifacts, commit `fc46ad2d`
- `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` — row #4 + the dated correction
- `docs/COST_CALIBRATION.md` — row `C-51`

**Credential count unchanged: 2 PASS of 4 run.** Only `PASS` rows are credentials, and
row #4 is not one. It stays on the register honestly, with its numbers, as a finding.

---

# PART 2 — the supervisor's follow-up directives, 2026-08-25

**`SendMessage` to `ansys-verification-supervisor` FAILED AS UNREACHABLE A SECOND
TIME.** The channel is **one-way**: the supervisor's messages reach this lane and this
lane's replies do not reach it. Report of record therefore continues on disk (`L-306`).

## Commits, in order

| sha | item |
|---|---|
| `b72e6211` | `C-51` id formatting — unbold to match every neighbour |
| `4c0919c2` | `CASE_MAP.md` — tier column on all 95 rows, scope arithmetic |
| `63c8d044` | VMFL051 `RESULTS.md` — tier `NOT HELD` + disclosure amendment |
| `4716ec45` | register addendum — tier back-filled onto rows #1–#4 |
| `a8a5be9f` | `CASE_MAP.md` — **Sanaa's scope ruling applied, denominator 73** |
| `565ea88c` | `CASE_MAP_AUDIT.md` correction — 95 cases, not 105 |
| `96e2bbef` | `RUN_STATUS_EVIDENCE.md` correction — 3 tracked case dirs, not 0 |
| `df156f8e` | **`L-312`** — a grep is not an enumeration instrument without a discriminator |
| `66d1f857` | **`L-313`** — re-derive a records id inside the committing invocation |
| `649aa42a` | charter dated note — the innocent explanation; v1.2 UNDERSTATED |
| `3abac11f` | charter **Amendment 1.3** — sharpened `L-308`, relay provenance |

## The campaign fraction

**3 of 73 in-scope cases run; 70 never run.** The denominator is **73, not 95, by
Sanaa's ruling** — 10 `VMFLGPU` `DEFERRED`, 12 no-solver `OUT OF SCOPE — BY RULING`,
zero overlap, 73 + 10 + 12 = 95. All 95 rows remain in the map; **nothing is deleted**,
because an exclusion that hides the excluded rows cannot be audited. Every count is
**derivable by counting the file's own rows**, with the deriving rule printed beside it
and each rule scoped to the row set — an unscoped `grep -c 'OUT OF SCOPE'` returns the
wrong answer because the header's own prose matches, and **the document says so**.

## Charter notes — the two prefix hashes asserted

| commit | prefix sha256 asserted **before** `commit-tree` | numstat |
|---|---|---|
| `649aa42a` | `8339141a7a61b175…` | 76 ins / 0 del |
| `3abac11f` | `3bdc0b86210aa0a5793cb714138b19579eee8aac3443559cf96e0315ab2533fa` | 73 ins / 0 del |

**Verified in this lane rather than relayed**, because the whole note turns on it: the
session record at `/home/ubuntu/harness-state/sessions/` returns *"outside repository"*
to `git ls-files --error-unmatch` — untracked, unreachable by any repository search, and
never was. **The Class-C-is-empty finding and the three true withdrawals are the
verification team's measurements, recorded as reported; this lane did not re-run the
lab-wide sweep and both notes say so.**

**Neither note upgrades the classification, restores any attribution, or licenses
touching the referred `teams.yaml` defect.** Amendment 1.3 names the four things that
are **not** Sanaa's consent: a chief's message, a peer's finding, a supervisor's
instruction, and the amendment itself.

## A correction to the supervisor's brief, measured

The discriminator was given as *"a real case id recurs 5–7 times"*. **Measured: 4–10**
(17 ids × 4, 46 × 5, 13 × 6, 13 × 7, 2 × 8, 3 × 9, 1 × 10). **The stronger fact is that
no identifier occurs 2 or 3 times at all** — the gap is empty, so any threshold in
≥ 2 … ≥ 4 returns exactly 95, split 78/10/7, and the separation is a **property of the
document** rather than a cutoff anyone chose. Also measured: the sidecar holds **106**
identifier-shaped tokens, not 105 — which is why the audit's list of ten missed
`VMFL010B`, **and why its two errors cancelled into plausible arithmetic**. `L-312`
records the measured figures and notes the 5–7 belief so nobody re-derives it from
memory.

## Protocol confirmation

**Every assertion was built in BEFORE `commit-tree`, not checked afterwards.** Base
captured in the same invocation as the commit; **prefix** (and on `CASE_MAP`, **suffix**)
hashed and compared before the blob was staged; `diff-tree --name-only` required to
**equal** the intended paths; on every append-only ledger **`insertions == lines
written` and `deletions == 0`**; trailing newline ensured before appending; ids
**re-derived inside the committing invocation**, with re-derivation wired into the CAS
retry. **The CAS retry fired once**, on `63c8d044`, and correctly re-read its base. A
build-abort guard added after `dc0a096c` **fired correctly** on the next commit and
blocked a bad one.

## Case status

**VMFL051 is CLOSED.** Verdict **`NOT A RESULT`**, tier **`NOT HELD`**, cost **23.3167
core-minutes**, ratio **2.0634×**, **$0.019936 derived, not measured**.
