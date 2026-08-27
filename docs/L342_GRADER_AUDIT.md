# L-342 GRADER AUDIT — which frozen comparators still refuse on an INFRASTRUCTURE field

**Version 1.0 — 2026-08-27.** Owner: `verification-supervisor`, under the cross-team gate-audit
mandate. **Zero compute.** This is a **findings** record: it names defects by `file:line` in
other teams' territory and **repairs none of them**. The owning supervisor decides the repair.

**The rule audited.** `L-342`, Sanaa's universal rule of 2026-08-26T16:15Z (`d4d0c29d`), verbatim:

> *"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts — and graders
> must separate physics-critical fields from infrastructure fields so a dead poller can never void
> a run again."*

Operationally: every grader labels its two field classes; an **absent INFRASTRUCTURE field is
NOT MEASURED and never refuses a grade**; `CLAUDE.md` rule 2 (strict completion) is **unchanged**
for PHYSICS fields. The motivating incident is `59110074` — VMFLGPU001's comparator refused a good
run because `petsc4Foam` printed `endTime + 2` `ExecutionTime` lines.

**The classification applied here, stated so it can be overruled.** The `ExecutionTime` / `ClockTime`
**line count** is **INFRASTRUCTURE**. Completion is carried by the `Time =` count, the `End` line,
last time `== endTime`, the fields present at `endTime`, and the age guard — every one of which is a
physics artifact. A timing-report line count is a property of *which libraries were linked*, not of
*whether the solve completed*. A refusal keyed on it is therefore **CONFLATED**.

---

## §1 — THE TWO ROWS THAT MATTER THIS WEEK

**1. `cases/ansys_verification/VMFLGPU002/grade_vmflgpu002.py:585-587` is heading for the
VMFLGPU001 failure, on a run that was already launched.** It is a `petsc4Foam` case
(`VMFLGPU002/PREREGISTRATION.md:7`, `:371` — `libs (petscFoam)`) whose comparator **retains the exact
clause that voided VMFLGPU001** — `if n_exec != endtime: refuse("C7", ...)`. The run went out
unattended at 22:46:12Z (`55879187`). Unless `petsc4Foam` behaves differently on this case, the rung
is heading for a refusal on a good run. **Frozen and fired: only `VERIFICATION_CHARTER` §2d.1's
four-condition repair exception can reach it — and the precedent is already written at `59110074`.**
**For `ansys-verification-supervisor`.**

**2. `cases/dafoam/curriculum_D12R2/d12y_grade_w3.py` is frozen (`eb1eb97d`) and HAS NOT FIRED —
it is the highest-leverage fix in the tree and the window is open only until W3 launches.** W3 sits
on the held drop path at **0 core-min**. Its `:376` `ExecutionTime` refusal and its ledger-absent
refusals at `:453`, `:1976`, `:1984`, `:1986` are **freely amendable under rule 2's pre-compute
amendment clause**, at no cost, naming the absent run root as the condition. **Once it fires the
cheap route closes and only §2d.1 remains.** **For `dafoam-supervisor`.**

---

## §2 — RULING R-RC: the `RUN_RC.txt` boundary, which the audit could not settle and this team can

**The question.** Seventeen ansys comparators exit 2 when the launcher's rc record is absent
(`VMFL001:295`, `VMFL001/R2:355`, `VMFL003:318`, `VMFL003_M2:339` and `:341`, `VMFL005:297`,
`VMFL007:444`, `VMFL019:175`, `VMFL021:212`, `VMFL021/R2:331`, `VMFL022:212`, `VMFL023:290`,
`VMFL033:241`, `VMFL036:293`, `VMFL045:526`, `VMFL045/R2:526`, `VMFL050:203`, `VMFL051:493`,
`VMFL064:216`). `CLAUDE.md` rule 4 makes **`rc`** physics-critical. **Nothing rules on the RECORD
that carries it**, and the lab has already ruled both ways in practice — `VMFL011-R2/grade_vmfl011_r2.py:105`
lists `RUN_RC.<level>` under `INFRASTRUCTURE` and `:112` returns *rc NOT MEASURED, the grade proceeds*;
`VMFLGPU001/grade_vmflgpu001.py:454-461` does the same.

**RULED, `[lab-attributed]`, and disclosed as overrulable by Sanaa:**

- **R-RC-1.** The rc **VALUE** is **PHYSICS-CRITICAL** — rule 4 is unchanged. The rc **RECORD**
  (`RUN_RC.txt` or any launcher stamp carrying it) is **INFRASTRUCTURE**: it is written by the
  launcher, not by the solver, and a dead launcher is precisely the dead poller `L-342` names.
- **R-RC-2.** When the record is **ABSENT**, the grader **does not refuse on its absence**. It marks
  rc **NOT MEASURED** and proceeds — **but only if all four remaining rule-4 physics conditions hold**
  (`End` line; last time `== endTime`; the registered fields present at `endTime`; the age guard).
  In that case `rc = 0` is **INFERRED**, and **the inference is printed as an inference, never as a
  measurement.** If any of the four fails, the row is `NOT A RESULT` **on that condition** — not on
  the missing record.
- **R-RC-3.** When the record is **PRESENT and non-zero**, the grader **refuses**. Rule 4 unchanged.
- **R-RC-4 — the hole named rather than glossed.** R-RC-2 is a **WIDENING in the permissive
  direction** and this team does not pretend otherwise. It is legal only because `L-342` is Sanaa's
  own instruction to widen exactly here, and it is fenced: the one shape that could pass the four
  conditions and still deserve refusal is a solver that returns **non-zero after** writing every
  field and the `End` line — a post-solve function object or a cleanup step failing. **A grader
  inferring rc under R-RC-2 must therefore also refuse on a `FOAM FATAL ERROR`, `FOAM FATAL IO ERROR`
  or signal token in the log, `End` line notwithstanding.** Without that limb the inference is not
  safe and R-RC-2 does not apply.

**On Sanaa's desk**, because R-RC-2 lets a grade proceed where the lab previously refused.

---

## §3 — THE DELTA TABLE

`frozen` = the grader's basename is named in a committed pre-registration. **`frozen` here means
*named and committed*, NOT *proven byte-identical to what ran*** — no comparator was hashed against
its blob in this audit; that is `scripts/check_comparator_freeze.py`'s job and it was not run.
`fired` = a run root exists. **A CONFLATED row that is frozen-and-fired needs §2d.1; a CONFLATED row
that has not fired is still freely amendable pre-compute, and that is the cheap column.**

### §3.1 ansys-verification — `cases/ansys_verification/`

Every row frozen **and fired** unless stated. Refusal shape unless stated: `ExecutionTime` line count.

| grader | L-342 | file:line | note |
|---|---|---|---|
| `VMFLGPU001/grade_vmflgpu001.py` | **COMPLIANT** | repair `f4b07b7f` → `21fa2387` at `59110074` | `n_time` refuses (physics) `:518`; `n_exec` reported `:521`, `warn_infra` `:529` |
| `VMFL006/grade_vmfl006.py` | **COMPLIANT** | — | **not frozen** (untracked, no prereg names it); counts `Time =`; absent `RUN_RC.txt` → `rc_unknown` + `infra_warn` `:270` |
| `VMFLGPU002/grade_vmflgpu002.py` | **CONFLATED** | `:585`→`:586` | **frozen, RUNNING NOW** — see §1 |
| `VMFL001/grade_vmfl001.py` | CONFLATED | `:321`→`:322` | |
| `VMFL001/R2/grade_vmfl001_r2.py` | CONFLATED | `:381`→`:382` | |
| `VMFL002/grade_vmfl002.py` | CONFLATED | `:66`→`:67` → `:403` `NOT A RESULT` | |
| `VMFL004/grade_vmfl004.py` | CONFLATED | `:66`→`:67` | |
| `VMFL004-R2/grade_vmfl004_r2.py` | CONFLATED | `:112`→`:113` | |
| `VMFL011/grade_vmfl011.py` | CONFLATED | `:66`→`:67` | |
| `VMFL011-R2/grade_vmfl011_r2.py` | **CONFLATED — MISCLASSIFIED** | classes `:99-105`, ExecutionTime put in `PHYSICS_CRITICAL` `:103`; refuses `:160`→`:161` | good structure, wrong line |
| `VMFL011-R3/grade_vmfl011_r3.py` | **CONFLATED — MISCLASSIFIED** | `:103`; `:160`→`:161` | |
| `VMFL003/grade_vmfl003.py` | CONFLATED | `:361`→`:362` | |
| `VMFL003_M2/grade_vmfl003_m2.py` | CONFLATED | `:382`→`:383` | |
| `VMFL003_M2/grade_vmfl003_m2_omega.py` | CONFLATED | `:384`→`:385` | |
| `VMFL005/grade_vmfl005.py` | CONFLATED | `:322`→`:323` | |
| `VMFL007/grade_vmfl007.py` | CONFLATED | `:470`→`:471` | |
| `VMFL007_R2/grade_vmfl007_r2.py` | CONFLATED | `:361-365` | |
| `VMFL019/grade_vmfl019.py` | CONFLATED | `:197`→`:198` | |
| `VMFL050/grade_vmfl050.py` | CONFLATED | `:225`→`:226` | |
| `VMFL023/grade_vmfl023.py` | CONFLATED | `:319`→`:320` | |
| `VMFL033/grade_vmfl033.py` | CONFLATED | `:260`→`:261` | |
| `VMFL036/grade_vmfl036.py` | CONFLATED | `:333`→`:334` | |
| `VMFL076/grade_vmfl076.py` | CONFLATED | `:283`→`:284` | |
| `VMFL076-R2/grade_vmfl076.py` | CONFLATED | `:283`→`:284` | |
| `VMFL064/grade_vmfl064.py` | CONFLATED | `:241`→`:242` | |
| `VMFL064-R2/grade_vmfl064_r2.py` | CONFLATED | `:401`→`:402` | |
| `VMFL045/grade_vmfl045.py` | **CONFLATED — exact GPU001 shape** | `:573`→`:574` `n_exec != n_time` | a petsc-style surplus fires it |
| `VMFL045/R2/grade_vmfl045_r2.py` | CONFLATED (same shape) | `:573`→`:574` | |
| `VMFL051/grade_vmfl051.py` | CONFLATED (same shape) | `:540`→`:541` | |
| `VMFL021/grade_vmfl021.py` | CONFLATED (weak) | `:236`→`:237` | floor of 10; cannot fire on a surplus, fires on suppressed timing |
| `VMFL021/R2/grade_vmfl021_r2.py` | CONFLATED (weak) | `:355`→`:356` | |
| `VMFL022/grade_vmfl022.py` | CONFLATED (weak) | `:236`→`:237` | |

Second axis: the 17 absent-`RUN_RC.txt` refusals listed in §2 — **ruled by R-RC above.**

### §3.2 heat-transfer — `verification/runs/T-family/` and `scripts/`

All frozen and fired. Refusal shape: `ExecutionTime` count mismatch → `fails`/`why` → exit 1 **NOT DONE**.

| grader | L-342 | file:line |
|---|---|---|
| `T1_runs/mark_done_t1b.py` | CONFLATED | `:111` |
| `T1_runs/mark_done_t1b_L4.py` | CONFLATED | `:121` — **the file `CLAUDE.md` rule 5 cites as its own provenance** |
| `T1_runs/mark_done_t1b_ext1.py` | CONFLATED | `:145`→`:146` (two-segment form) |
| `T1_runs/mark_done_dts_u.py` | **CONFLATED — MISCLASSIFIED** | classes `:21`, ExecutionTime on the physics side; refuses `:120` |
| `T3_runs/mark_done_t3.py` | CONFLATED | `:98` |
| `T3_runs/mark_done_t3_ext1.py` | CONFLATED | `:126`→`:127`, `:175`→`:176` |
| `T3_runs/mark_done_t3_rff.py` | **CONFLATED — MISCLASSIFIED, INHERITED** | `:10-11` lists it PHYSICS-CRITICAL; gate via `mark_done_t3.check` imported `:27`. Its INFRASTRUCTURE list `:15-18` is otherwise exemplary |
| `T4_runs/mark_done_t4.py` | CONFLATED | `:136` |
| `T4b_runs/mark_done_t4b.py` | CONFLATED | `:137` |
| `T5_runs/mark_done_t5.py` | CONFLATED | `:91` |
| `T5_runs/analyse_t5.py` | CONFLATED | `:110` |
| `T8_runs/analyse_t8.py` | CONFLATED | `:455`→`:457` |
| `T9a_runs/mark_done_t9a.py` | CONFLATED | `:64` |
| `T9a_runs/mark_done_t9aD.py` | CONFLATED (inherited) | delegates, imported `:23` |
| `T9aH_runs/mark_done_t9a.py` | CONFLATED | `:64` |
| `T9aR1b_runs/mark_done_t9aR1b.py` | **CONFLATED — MISCLASSIFIED** | classes `:15`; refuses `:107` |
| `T10a_runs/mark_done_t10a.py` | CONFLATED | `:80` |
| `T10aR_runs/mark_done_t10aR.py` | CONFLATED | `:80` |
| `T10aR2_runs/mark_done_t10aR2.py` | CONFLATED | `:137` |
| `T11_runs/mark_done_t11.py` | CONFLATED | `:109` |
| `T13_runs/mark_done_t13.py` | CONFLATED | `:133` |
| `T14_runs/mark_done_t14.py` | **CONFLATED — MISCLASSIFIED** | `:14-16`; refuses `:107`. Otherwise the cleanest class declaration in the T-family |
| `T15_runs/mark_done_t15.py` | **CONFLATED — MISCLASSIFIED** | `:20`; refuses `:134` |
| `E4_runs/mark_done_e4a.py` | CONFLATED | `:81`→`:82` |
| `E4a2_runs/mark_done_e4a2.py` | CONFLATED (inherited) | delegates, imported `:32` |
| `scripts/mark_done_k0d.py` | CONFLATED | `:249`→`:250` — K0d fired (`docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md`) |
| `scripts/mark_done_k0f.py` | CONFLATED | `:266`→`:267` |
| `T13/T14/T15/T9aR1b analyse_*.py`, `T1_runs/analyse_dts.py`, `analyse_dts_p.py` | **COMPLIANT** | count and report; no refusal path reaches it |

### §3.3 cfd

| grader | L-342 | file:line |
|---|---|---|
| `cases/F15_oblique_shock_reflection/grade_f15_r2.py` | **COMPLIANT — EXEMPLAR** | `:42-44` |
| `cases/F15_oblique_shock_reflection/grade_f15_r3.py` | COMPLIANT | `:96` |
| `cases/F15_oblique_shock_reflection/grade_f15.py` | COMPLIANT | `:355-358` — clause declared, *not applied*; replaced by the final-step limb |
| `cases/F16_stokes_second_problem/grade_f16_r2.py` | COMPLIANT | `:31-33` |
| `cases/F16b_stokes_second_problem/grade_f16b.py` | **COMPLIANT — STRONGEST IN THE TREE** | `:102-105` `infrastructure_census()` |
| F17, F17b, F18, F18b, F19_SOD, F20, F21, F22, F23, F24, F25 graders (11) | **COMPLIANT** | all declare classes; none gates a timing-line count |
| `verification/runs/F3_runs/conversion_2026-08-24/grade_f3.py` | CONFLATED | `:176` `C5_log_step_integrity`, gated `:229` |
| `verification/runs/F4_runs/conversion_2026-08-25/grade_f4.py` | CONFLATED — exact GPU001 shape | `:213`→`:214` |
| `verification/runs/F4_runs/successor_2026-08-26/grade_f4s.py` | CONFLATED | `:461`→`:463` |
| `verification/runs/F11_runs/conversion_2026-08-25/grade_f11.py` | CONFLATED | `:694-697`, gated `:746`, `NOT A RESULT` `:1020` |
| `verification/runs/DPW8_V2_runs/analyse_l4_diag.py` | CONFLATED | `:374`, gated `:403`, arm labelled `BLOCKED` `:428` |

### §3.4 dafoam — `cases/dafoam/`

| grader | L-342 | file:line |
|---|---|---|
| `ladder-a/A2/curriculum_D4_SHIPPED/d4s_grade.py` | **PARTLY COMPLIANT — the L-342 origin repair** | classes `:76-89`; a missing ledger **row** falls back to the kernel record — **but `:864` `refuse("ledger", {"absent": path})` still voids on a missing ledger FILE. The dead-poller shape survives the repair that was made for it.** |
| `curriculum_D17_cone_supersonic/d17_grade.py` | PARTLY COMPLIANT | `:172-184` `inspect_file_fallback`; `:142` same residual file-absent refusal |
| `AV1:135`, `AV2:126`, `D15:135`, `D16:136`, `D5:160`, `D6:132`, `D4_SHIPPED_F3S:141`, `D8R:169` | **CONFLATED (residual)** | each `refuse("ledger", {"absent": path})` — the ledger is poller-written bookkeeping |
| `curriculum_D12/d12r_grade.py` | CONFLATED | `:237`→`:238` |
| `curriculum_D12R/d12x_grade.py` | CONFLATED | `:259`→`:260` |
| `curriculum_D12R2/d12y_grade.py` | CONFLATED | `:374`→`:375`; ledger `:452`. Half-repaired — `:1770-1776` already returns `NOT_MEASURED` for the 33-row case |
| `curriculum_D12R2/d12y_grade_w3.py` | **CONFLATED — NOT YET FIRED** | `:375`→`:376`; ledger `:453`, `:1976`, `:1984`, `:1986` — **see §1** |
| `d460_sweep1_solver_family/analyse_sweep1.py` | CONFLATED | `:234`, gated `:269` |
| `ladder-a/A3/curriculum_D7F/d7f_grade.py`, `D7FR/d7fr_grade.py` | COMPLIANT | ExecutionTime only in selftest fixtures (`:1395`, `:1433`, `:1442`); no gate |
| `ladder-a/A2/curriculum_D14/d14m_grade.py` | COMPLIANT | declares classes; no timing-count gate, no ledger-absent refusal |

### §3.5 closure and shared scripts

`cases/RANS_LES_closure_models/R5C_omega_repair/grade_r5c.py` — **COMPLIANT**: reads `ExecutionTime`
only as a *value* for cost derivation (`:150-151`, `:440`), never as a count. `analyse_tbnn.py` /
`analyse_tbrf.py`: no infrastructure gate. `scripts/roache_triple.py` — **COMPLIANT** (no
infrastructure field appears in it at all). `scripts/check_comparator_freeze.py` — not a grader.

---

## §4 — THE FIVE EXEMPLARS, so a team is handed a pattern and not only a defect list

1. **`cases/ansys_verification/VMFLGPU001/grade_vmflgpu001.py:490-545`** — the canonical split
   (`n_time` refuses, `n_exec` measured and reported with an `INFRA:` note). Its comment block at
   `:497-515` is a ready-made §2d.1 amendment rationale.
2. **`cases/F16b_stokes_second_problem/grade_f16b.py:102-105`** — `infrastructure_census()`: reads
   every infrastructure field, marks absence `NOT MEASURED`, returns a BOOKKEEPING DEFECT list,
   **never refuses**.
3. **`cases/F15_oblique_shock_reflection/grade_f15_r2.py:42-44`** — the one-line header disclosure
   that makes this whole audit answerable by reading a file's top: *"Refusals reclassified from
   refusal to BOOKKEEPING DEFECT: NONE"*.
4. **`cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py:99-112`** — explicit
   `PHYSICS_CRITICAL` / `INFRASTRUCTURE` module constants. **Good structure, wrong line** — it puts
   `ExecutionTime count` on the physics side.
5. **`verification/runs/T-family/T3_runs/mark_done_t3_rff.py:8-18`** — the best prose class
   declaration in the T-family, with a selftest at `:143-144` driving **both** halves. Copy the
   selftest shape; move `ExecutionTime` across the line.

---

## §5 — COVERAGE LIMITS, stated rather than glossed

Three sweeps, and each row above states which population it came from. `git ls-files` gave **157**
tracked files matching `grade_*` / `analyse_*` / `analyze_*` / `mark_done_*.py`; a raw `find`
(ignore-files bypassed — `grep -r` here is blind to gitignored case archives) gave **192**
grader-shaped files including `*_grade*.py` and `regrade_*.py`. The delta: one untracked file
(`cases/ansys_verification/VMFL006/grade_vmfl006.py`) plus nine tracked-but-deleted-in-worktree paths
(the staged `F25_DUCT3D` and `curriculum_D12R2` deletions visible at HEAD `c9ff33d9`), read from disk
where present.

**130 of 192 carry no `ExecutionTime` / `ClockTime` gate at all** and are not at risk on that axis.
They were **not** individually traced for other infrastructure gates — they were swept for
`poller|ledger|pid|core_min|wall_s|COST.txt|STAMP` refusals, and the dafoam ledger cluster in §3.4 is
what that sweep returned. **A bespoke infrastructure field under a name not guessed would have
escaped**, and this audit does not claim otherwise.

**Not audited:** the out-of-git tree `/home/ubuntu/certonomous-runs/` holds 14 `analy[sz]e_*.py`
files (S1, F6a, W4, B3, F12 work). None is named as a comparator in any committed pre-registration
and so none carries a frozen verdict — **but that claim was not verified file by file.**
`/home/ubuntu/closure-data/` and `/home/ubuntu/closure-challenge-benchmark/` hold no grader-shaped
files. **No comparator was hashed against its committed blob**, so every `frozen` in §3 means *named
and committed*, never *proven byte-identical to what ran*.

Nothing was edited, nothing committed outside this file, no other team's artifact touched.

---

## Addendum 1 — 2026-08-27 — THE COUNTING RULE v1.0 NEVER STATED, AND THE CENSUS CORRECTED AGAINST THIS TEAM

**Ordered by the chief at 16:48Z after `ansys-verification` contested the census. Appended at the
foot; nothing above is edited, struck or renumbered. `lines whose number changed above this
section: 0` — the 249 lines of v1.0 are byte-identical to their `HEAD` blob, proved by `cmp`
before this file was written.**

### 1. The defect in v1.0, stated plainly

**v1.0 reported a COVERAGE figure as though it were a CENSUS.** "ansys 30 CONFLATED of 32 read"
is arithmetically correct about the 32 rows in §3.1 — 30 CONFLATED, 2 COMPLIANT — **but 32 was
never the population.** The population is **37**. v1.0 never stated its counting rule, so a
reader could not tell a coverage denominator from a census denominator, and three teams derived
three different numbers from the same tree. **The contest was caused by this audit, not by the
teams disputing it.**

### 2. THE COUNTING RULE, now fixed for this audit and every re-derivation of it

> **One row per grader FILE — `grade_*.py`, `analyse_*.py`, `analyze_*.py`, `mark_done_*.py`,
> `*_grade*.py`, `regrade_*.py` — found ON DISK under the family root at ANY DEPTH, tracked or
> not, `__pycache__` excluded.**

Three consequences, each of which produced one of the contested numbers:

- **NOT per case directory.** Four ansys graders live **nested** one level down, not as sibling
  case dirs: `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py`, `VMFL017/R2/`,
  `VMFL021/R2/`, `VMFL045/R2/`. **This is why `VMFL001-R2`, `VMFL021-R2` and `VMFL045-R2` "could
  not be matched to case directories" — they have none, and v1.0's paths were correct.** A scan
  of top-level dirs cannot see them.
- **NOT tracked-only.** Two ansys graders are real and **untracked**:
  `VMFL006/grade_vmfl006.py` and `VMFLGPU003/grade_vmflgpu003.py`. A `git ls-files` census
  returns **35** and misses both.
- **Case dirs are not graders.** `cases/ansys_verification/` holds **33** top-level directories —
  **29 `VMFL*` + 3 `VMFLGPU*` + `_template/`** — against **37** graders. `_template/` has none;
  four cases carry two.

### 3. ANSYS — the authoritative derivation

| | count | derivation |
|---|---|---|
| **Population (the rule above)** | **37** | `find cases/ansys_verification -name 'grade_*.py'`, `__pycache__` excluded |
| tracked | 35 | the remaining 2 are `VMFL006`, `VMFLGPU003` |
| read in v1.0 §3.1 | 32 | 32 table rows, 31 distinct basenames (`grade_vmfl076.py` appears in both `VMFL076/` and `VMFL076-R2/`) |
| **missed by v1.0** | **5** | listed in §4 below; **32 + 5 = 37**, and **nothing v1.0 named is absent from disk** — the audit invented no file |
| **AUTHORITATIVE: CONFLATED** | **30** | unchanged — every one of the 5 missed is COMPLIANT |
| **AUTHORITATIVE: COMPLIANT** | **7** | v1.0's 2 (`VMFLGPU001`, `VMFL006`) + the 5 below |

**The three contested figures reconciled, each correct under its own rule and none under this one:**
this team's **"30 of 32"** was coverage, not census, and understated the denominator by 5;
ansys's **"28 of 35"** counts **committed** graders — its 35 is exactly the tracked count and is
right under that rule, and its 28 is its own classification, which this addendum does not
adjudicate; the directory scan's **"31 VMFL* + 3 VMFLGPU = 34"** overcounts `VMFL*` by two
(measured: **29** non-GPU `VMFL*` dirs, plus `_template/`, giving 33 dirs) and counts directories,
which are not the unit.

### 4. THE FIVE GRADERS v1.0 MISSED — read for this addendum, all five COMPLIANT

| grader | tracked | L-342 | evidence |
|---|---|---|---|
| `cases/ansys_verification/VMFL010/grade_vmfl010.py` | yes | **COMPLIANT** | **zero** `ExecutionTime`/`ClockTime` tokens in 152 lines; no `RUN_RC`/ledger/poller refusal site among its 17 exit paths |
| `cases/ansys_verification/VMFL017/grade_vmfl017.py` | yes | **COMPLIANT** | zero timing tokens in 236 lines; none of its 17 exits is infrastructure-keyed |
| `cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py` | yes | **COMPLIANT** | zero timing tokens in 485 lines; none of its 21 exits is infrastructure-keyed |
| `cases/ansys_verification/VMFL059/grade_vmfl059.py` | yes | **COMPLIANT** | zero timing tokens in 204 lines; none of its 15 exits is infrastructure-keyed |
| `cases/ansys_verification/VMFLGPU003/grade_vmflgpu003.py` | **no** | **COMPLIANT — AND IT IS THE FIX** | see §5 |

**CORRECTION TO A CLAIM MADE ABOUT THIS AUDIT, not by it: `VMFL059` appears NOWHERE in v1.0.**
It is not called `UNFIRED` and is not classified at all — it is one of the five omissions. The
omission is the defect; there is no misclassification to withdraw. Its run root
`verification/runs/ansys_verification/VMFL059` **is present**, consistent with the register.

### 5. ⚠ THE REPAIR ansys NEEDS FOR `VMFLGPU002` IS ALREADY WRITTEN, ONE DIRECTORY AWAY

`VMFLGPU003/grade_vmflgpu003.py` **already implements the L-342 split correctly for exactly the
petsc4Foam defect that voided `VMFLGPU001` and that §1 of this audit flags as live on
`VMFLGPU002`.** Verified at source:

- `:783-786` names the mechanism and the precedent in its own comment — *"petsc4Foam prints
  endTime + 2 timing lines. VMFLGPU001 froze this count as physics-critical and has no verdict as
  a result (commit `59110074`). It is recorded here and it NEVER refuses."*
- `:787-794` computes `n_exec`, and on mismatch calls `warn_infra(...)` with the message *"A
  TIMING-LINE COUNT IS BOOKKEEPING (L-342): it is recorded, it does not refuse, and it cannot void
  the physics"*, setting `exec_note = "ANOMALOUS -- recorded, not refused (L-342)"`.
- `:262-266` — `warn_infra` **prints and returns `None`**. It has no exit path. The refusal
  immediately below it, `:797-799` `refuse("C8", ... no 0/U age-guard marker)`, is on a **physics**
  field, which is rule 4 working as intended.
- It declares its two field classes **29 times**.

**For `ansys-verification`: `VMFLGPU003` is the pattern for the `VMFLGPU002` §2d.1 amendment, and
it is this team's own prior art rather than anything imposed from outside.** `VMFLGPU003` is
untracked and its run root is absent — **unfrozen and unfired**, so it is still freely amendable
and nothing here constrains it.

### 6. PER-FAMILY DENOMINATORS under the rule in §2 — and what remains VERIFY

| family | population (rule §2) | read in v1.0 | status |
|---|---|---|---|
| ansys-verification | **37** | 32 | **SETTLED** by this addendum: 30 CONFLATED / 7 COMPLIANT |
| heat-transfer | **73** | §3.2's table | **VERIFY** |
| dafoam | **46** | §3.4's table | **VERIFY** |
| cfd | **34** | §3.3's table | **VERIFY** |
| closure | **3** | §3.5 prose | **VERIFY** |

Roots: heat-transfer = `verification/runs/{T-family,F14-cooling-ladder,THERMAL_K0_runs}/` plus
`scripts/mark_done_k0*.py`; cfd = `cases/` minus the three family roots, plus `verification/runs/`
minus heat-transfer's three; dafoam = `cases/dafoam/`; closure =
`cases/RANS_LES_closure_models/`. Total **193**, against v1.0's raw-find figure of 192 — the
difference is this rule's wider pattern set, not a new file.

**The four non-ansys counts stay `VERIFY` and are NOT corrected here**, because correcting a
denominator without reading the files it adds would repeat v1.0's error in the opposite
direction. **What clears them:** the same treatment ansys just received — enumerate under §2,
diff against the section's table, read every grader the diff adds, classify it, and state
CONFLATED / COMPLIANT against the full population. Until then **every non-ansys CONFLATED count
in v1.0 is a coverage figure, not a census**, and must be cited as one.

### 7. What did NOT change

**No verdict moved. No comparator was edited. No case was re-graded.** §1's two urgent rows and
§2's Ruling R-RC stand exactly as written; the `VMFLGPU002` and `d12y_grade_w3.py` findings are
unaffected by the census correction, since both were identified by reading the file, not by
counting. The CONFLATED total for ansys is **unchanged at 30** — the correction moves the
denominator, not the defect list.

---

## Addendum 2 — 2026-08-27 — THE BOUNDED INFRA-ONLY AUDIT: 2 RE-GRADEABLE ROWS IN THE ENTIRE LAB, AND NEITHER IS ON THE `ExecutionTime` AXIS

**Ordered by the chief at 16:48Z. Appended at the foot; nothing above edited or renumbered.
`lines whose number changed above this section: 0` — proved by `cmp` against the `HEAD` blob in the
same invocation as the commit. NO VERDICT MOVED IN THIS AUDIT. No comparator was edited, no case
re-graded, no solver run.**

**The question, per row:** was the refusal on an **INFRASTRUCTURE field ALONE**, with the physics
artefacts complete under `CLAUDE.md` rule 4's **other** conditions?

### 1. THE RESULT

| family | rows examined | `INFRA-ONLY YES` | `INFRA-ONLY NO` | `NOT MEASURED` |
|---|---|---|---|---|
| ansys-verification (register) | 20 | **0** | 20 | 0 |
| heat-transfer | 43 | **0** | 43 | 0 |
| cfd | 28 | **1** | 27 | 0 |
| dafoam | ~50 | **1** | ~49 | 0 |
| closure | 10 | **0** | 10 | 0 |
| **total** | **~151** | **2** | **~149** | **0** |

**THE RE-GRADEABLE POPULATION IN THE ENTIRE LAB IS TWO ROWS.** Both are verified below by this
supervisor personally, not taken on lane report (`SUPERVISION_CHARTER` §3 check 3).

**THE HEADLINE FINDING IS THE ONE NOBODY EXPECTED: the `ExecutionTime` line-count conflation that
§3.1–§3.4 flags in ~60 frozen comparators HAS VOIDED NOTHING, ANYWHERE.** Neither YES row is on
that axis. The defect is **real, frozen and latent** — it will bite the next petsc4Foam-style run,
which is why §1's `VMFLGPU002` warning stands — **but it is not a backlog of lost results.** Three
independent reasons, each measured:

- **ansys:** the clause exists in ~30 comparators and **fired in none of them.** A sweep of grading
  artefacts returns only `VMFLGPU001/GRADING.txt` and `GRADING_regrade.txt`, and **`VMFLGPU001` has
  no register row at all** — its verdict is withheld at `59110074`. **That is the positive control
  for this zero**, and it is why the zero is a measurement rather than a blind spot: the one place
  the defect fired is excluded from the population by construction.
- **heat-transfer:** the 27 CONFLATED comparators are `mark_done_*` **completion markers that exit
  1 NOT DONE upstream of grading.** They never compose a verdict row, so the conflation cannot
  reach a record. All 43 rows are rule 5.
- **dafoam:** the `refuse("ledger", {"absent": path})` cluster §3.4 named as *"the single most
  likely INFRA-ONLY YES family"* **yields zero.** `AV1`/`AV2` refused at a *different* clause
  (`av1_grade.py:200`, `av2_grade.py:188` — the G1 age reference, a **physics** field);
  `D15`/`D16` graded to `GATE FAIL`/`PASS` with no `NOT A RESULT` rows; `D5`, `D6`,
  `D4_SHIPPED_F3S` and `D8R` have **no `RESULTS.md` at all** and no row ever reached a verdict.
  **This team's own prediction was wrong, and the measurement is the finding.**

### 2. `INFRA-ONLY YES` #1 — cfd, F6a attempt 2 (`verification/runs/F6a_GREENBLATT_runs/attempt2_Re936k`)

**Turns on the ABSENT rc RECORD — the exact axis of Ruling R-RC, which Sanaa APPROVED at 16:54Z.**

**Verified by this supervisor on disk, not relayed** — the four remaining rule-4 physics conditions
and the R-RC-4 fence:

| rule-4 conjunct | measured | holds |
|---|---|---|
| rc record | **ABSENT** — no rc file anywhere in the run root | the infrastructure field, and the only missing one |
| `End` line | `grep -c '^End' log.simpleFoam` = **1** | ✔ |
| last time == endTime | `Time = 1813` == effective endTime **1813** | ✔ (caveat below) |
| fields at endTime | `1813/` holds `U k nut omega p phi wallShearStress` | ✔ |
| age guard | `1813/U` mtime **1787626925** > `0/U` **1787626839** (+86 s) | ✔ |
| **R-RC-4 fence** | `FOAM FATAL` **0**, `SIGSEGV` **0**, `Aborted` **0**; the sole `SIGFPE` hit is `log.simpleFoam:29`, the `trapFpe … enabled` **startup banner** | ✔ clear |

**Under R-RC-2 this row reads `GATE FAIL`, not `NOT A RESULT`** (P1 separation `PASS` −1.59 %; P2
reattachment `GATE FAIL` +13.95 %). **Stated rather than glossed:** the `last time == endTime` limb
holds against the **effective** endTime 1813, not the `controlDict` declared 2000 — a substitution
ruled by the cfd supervisor in Addendum 3 (Ruling 2) on the (P-a) plateau clause. **That is a
registered deviation this team is reporting, not asserting.**

**⚠ AND A RULE-2 FINDING THAT IS INDEPENDENT OF L-342 AND MATTERS MORE.** The registered extractor
is `cases/dafoam/f6a_nasa_hump/case/hump_gate_analysis.py`, resolved by the `extractor_sha256`
`9a6ec855…` recorded in `result.json` and **confirmed by this supervisor** (`sha256sum` matches,
79 lines). That file contains **zero occurrences of `NOT A RESULT` and zero rc / completion-rule
clauses.** ~~**The refusal that voided this row was composed directly into `result.json` and was not
produced by any executable comparator.**~~ **STRUCK 2026-08-27 — FALSE. See Addendum 3.** Consequences, both of which bound the chief's re-grade
ruling: **(a) this row cannot be "re-graded by re-running" — there is nothing to re-run**; **(b) a
verdict with no executable grading path is a standing-rule-2 defect in its own right**, and it
should be settled on that ground before L-342 is applied to it. **For `cfd-supervisor`.**

### 3. `INFRA-ONLY YES` #2 — dafoam, D12R phase 1 (`cases/dafoam/curriculum_D12R`)

**This is the canonical L-342 case — the dead poller, exactly as Sanaa described it.**

The refusing clause, verified at source, `cases/dafoam/curriculum_D12R/d12x_grade.py:204-205`:

```
        if st.get("status") != "COMPLETE":
            raise Refusal("G12R-0 %s: JSON status=%r" % (nm, st.get("status")))
```

`status` is read from `manifest.jsonl`, which the **frozen launcher itself** populates —
`d12x_stage_and_run.sh` sets `row["status"] = j.get("status")` when a stage JSON exists and
**`row["status"] = None` in the `else` branch when it does not**, which is the designed path for a
`task=shell` stage that writes no JSON. **The launcher writes the null; the grader refuses on it.**

**Measured by this supervisor across all 32 manifest rows** at
`/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady/manifest.jsonl`:

| field | value |
|---|---|
| rows | **32** |
| `status` null | **1** — and it is `task = shell`, `rc = 0` |
| `status` `COMPLETE` | 31 |
| **`rc == 0`** | **32 / 32** |
| **`end_line_present` true** | **32 / 32** |
| **`age_guard_ok` true** | **32 / 32** |
| `oomkilled` true | **0** |

**One launcher-metadata field, absent by the launcher's own design, voided a rung whose thirty-two
stages are every one of them physically complete.** `INFRA-ONLY YES`. **For `dafoam-supervisor`.**

### 4. WHAT IS EXPLICITLY *NOT* RE-GRADEABLE, so the ruling cannot be over-applied

**Of ~149 `INFRA-ONLY NO` rows, the overwhelming majority are rule 5** — a level not iteratively
converged or not plateaued, or a triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` /
`DEGENERATE`. **Rule 5 is a physics verdict and `L-342` does not touch it.** Also `INFRA-ONLY NO`,
and named so they are not mistaken for bookkeeping: **failed planted-zero controls** (rule 3 —
ansys `VMFL011`, `VMFL011-R2`; dafoam `D10 probe`), **non-zero rc** (ansys `VMFL045` rc = 1,
`VMFL007` rc = 136; cfd `F12` rc = 134), **absent `End` line / absent `endTime` fields** (ansys
`VMFL003-M2` arms C and D, `VMFL017-R2`, `VMFL021`), **registered band failures**, and **physics
gate-readers** (ansys `VMFL064` — wall shear never changes sign, a real corner vortex at L3, not a
log artefact).

### 5. ~~FOUR ROW-CLASSES WHOSE REFUSAL EXISTS IN NO COMPARATOR~~ — **WITHDRAWN IN WHOLE, 2026-08-27. Every claim in this section is unsafe; see Addendum 3.**

Independent of L-342, and reported because a verdict with no executable grading path cannot be
re-derived by anyone: **F6a attempt 2** (§2 above); **T1b B0–B4**, 4 rows where the frozen
comparator returned `PASS ×4` (blob `08732fd6`, byte-identical) and the `NOT A RESULT` is rule 5
applied **by hand** over its output, with both readings displayed and neither picked
(`MATRIX_CONTRIBUTION.md:255`, D440); **~13 dafoam A2/A3 `grading_confirmation` and A1 `reverify`
near-zero rows**, hand-applied by the confirming lane; and **MATRIX `G-21`**, which states plainly
that it has *"no pre-registered gate of its own"*.

### 6. COVERAGE LIMITS

`git grep` / `git ls-files` for the tracked population, raw `find` for disk — **a `NOT A RESULT`
living only in a gitignored file would have escaped.** Outside git, **read**:
`/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady/` (where YES #2 was verified).
**Not read:** the remaining ~500 run roots under `/home/ubuntu/certonomous-runs/`,
`/home/ubuntu/closure-data/`, `/home/ubuntu/closure-challenge-benchmark/`; a whole-tree grep for
`completion_rule_limb_by_limb` **timed out at 120 s and was abandoned**, so §2's negative result for
the F6a comparator rests on a tracked-file grep plus targeted finds, **not** an exhaustive sweep.
**No comparator was hashed against its committed blob** except the F6a extractor (sha256 matched),
so "frozen" keeps §5's meaning: *named and committed*, never *proven byte-identical to what ran*.
**The dafoam row count is ~50, not exact** — that family nests verdicts at item, arm and component
level and the row boundary is a judgement, not a measurement. **The ansys count of 20 is the lane's
and is NOT independently confirmed by this supervisor**: the register defeats column indexing (rows
carry escaped pipes and multi-line narrative cells) and a naive `grep 'NOT A RESULT'` over it
returns **73** occurrences against ~20 real rows. **Register machine-readability is itself a finding
for `ansys-verification`.**

---

## Addendum 3 — 2026-08-27 — TWO CORRECTIONS AGAINST THIS AUDIT, BOTH THE SAME ERROR: I NAMED A COMMIT'S CLASS FROM ONE HUNK

**Raised by `cfd-supervisor`'s own check 1 and relayed by the chief at 17:24Z. Verified at source by
this supervisor before acceptance — a relayed check is a summary, not a check — and cfd is RIGHT.
Two sentences above are struck in place; the line count above is unchanged, and the struck text is
preserved inside the strike rather than deleted.**

**THE LESSON, in `cfd-supervisor`'s wording, and it is now this team's too:**

> **A commit is not its most interesting hunk — enumerate every path before naming its class.**

### 1. F6a attempt 2 — the "no executable comparator" sentence is FALSE and is struck

**What I did wrong.** I resolved `result.json`'s `extractor_sha256` to
`cases/dafoam/f6a_nasa_hump/case/hump_gate_analysis.py`, found no `NOT A RESULT` and no rule-4
clause in its 79 lines, and concluded no executable comparator produced the verdict. **I checked
the EXTRACTOR and called it the COMPARATOR. They are different objects with different jobs**: the
extractor pulls numbers out of the case; the comparator applies rule 4 and the bands.

**Measured now, at source:**

- **`scripts/f6a_greenblatt_gate.py` is the comparator — 726 lines, 12 occurrences of
  `NOT A RESULT`, 52 rule-4 / rc clause hits**, with `refuse()` at `:96` and an exit-code contract
  at `:30` (`0 graded | 2 REFUSAL | 3 usage error`). It even refuses on an **extractor hash
  mismatch** at `:115`. **There was an executable comparator the whole time and I did not open it.**
- **Commit `072cfc2e` touches FIVE paths, not one** — `scripts/f6a_greenblatt_gate.py` (+24),
  `scripts/f6a_greenblatt_selftest.py` (+90), `scripts/run_f6a_greenblatt.py` (+81),
  `verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md` (**+105 disclosed pre-registration
  lines**), and the `result.json` (+20). Its subject names itself **ADDENDUM 4**: *"the supervisor
  REFUSED the inferred rc limb … rc now persisted to disk on capture."*
- **The instrument was HARDENED in the same commit**: `--rc` moved from `default=0` to
  `default=None`, `--rc-file` was added, and the comparator now refuses with *"rule 4's rc limb is
  MEASURED, not inferred"* when the file is absent and *"no exit code supplied"* when neither is
  given. The selftest gained two negative cases driving exactly those paths.

**This is a disclosed, pre-registered supervisor refusal to infer a physics limb, with the
instrument hardened to measure it instead. It is not a bookkeeping accident and it is not a
records-integrity failure.**

### 2. THE CLASSIFICATION CHANGES: F6a attempt 2 is `INFRA-ONLY NO`, and the physics is not why

**Asked directly by the chief, answered directly.** The physics I measured in Addendum 2 §2 still
holds and is not withdrawn: `End` count **1**, last `Time = 1813` == effective endTime **1813**,
`1813/` holding `U k nut omega p phi wallShearStress`, age guard **+86 s**, and the **R-RC-4 fence
clear** (`FOAM FATAL` 0, `SIGSEGV` 0, `Aborted` 0). **Under R-RC-2 the rc limb is `NOT MEASURED`
and the row would read `GATE FAIL` on the physics alone.**

**But `INFRA-ONLY YES` was never a claim about the physics — it is a claim about WHY THE GRADER
REFUSED, and that claim is now false.** The refusal was not an infrastructure field voiding a good
run; it was a **supervisor declining to infer**, disclosed across +105 pre-registration lines and
frozen. **L-342 reaches graders that void physics through bookkeeping. It does not reach a
supervisor who refuses an inference and hardens the instrument to measure it.** Reading R-RC-2 as
authority to overturn that would be using a later general rule to override a **specific,
pre-registered, disclosed instrument choice** — which is exactly what `VERIFICATION_CHARTER` §2d
exists to prevent.

**`INFRA-ONLY NO`. cfd's conclusion — DO NOT FLIP — stands, and this team now agrees on the
record.** Attempt 3 is registered to produce a measured rc; that is the correct route, not a
re-grade of attempt 2.

**CONSEQUENCE FOR ADDENDUM 2's HEADLINE, stated rather than buried: the lab-wide re-gradeable
population falls from TWO rows to ONE.** The table in Addendum 2 §1 is corrected here rather than
rewritten: **cfd `INFRA-ONLY YES` 1 → 0; lab total 2 → 1.** **The only re-gradeable row in the
entire lab is dafoam D12R phase 1**, whose evidence in Addendum 2 §3 is unaffected — its refusal is
a launcher-written `status: null` on a `task=shell` stage, with rc==0, `end_line_present` and
`age_guard_ok` true on **32 of 32** manifest rows, all verified by this supervisor.

### 3. §5 IS WITHDRAWN IN WHOLE — two of its four claims checked, both false; two unsourceable

**The chief ordered §5's T1b claim re-checked by the same standard. It fails, and so does the
section.**

- **T1b B0–B4 — FALSE.** I wrote that the frozen comparator returned `PASS ×4` and the
  `NOT A RESULT` was *"rule 5 applied BY HAND over its output"*. **Measured:
  `verification/runs/T-family/T1_runs/gate_t1b_L4.json` holds 7 rows — 4 × `NOT A RESULT` and
  3 × `REPORTED` — each `NOT A RESULT` carrying a machine-written `why`:** *"levels x not
  iteratively converged"* and *"grid triple (m,f,x) is STAGNANT; the x value is 0.299 % / 0.626 % /
  0.078 % from the reference…"*. **The comparator emitted these verdicts itself. Nothing was
  hand-applied.** *(The three `REPORTED` rows are the D534 row-class, behaving exactly as that
  ruling describes.)*
- **AND THE SAME OBJECT ERROR AGAIN, TWICE IN ONE SENTENCE.** I called `08732fd6` a **blob**; it is
  a **commit** — *"Freeze the T1b comparator with all nineteen cases unsolved"*, 2026-08-19 — and
  it touches **`analyse_t1b.py`, not `analyse_t1b_L4.py`**, which is the L4 comparator and was
  frozen separately at `17209b50`. **Wrong object class and wrong file, in a citation offered as
  proof.**
- **MATRIX `G-21` — NOT MEASURED, withdrawn.** A search for `G-21` returns **only this audit and
  this team's own board block**. That is a self-citation loop, not a source. Per this team's own
  near-miss doctrine (`L-308`) a failed search is **not** proof of absence, so the claim is
  withdrawn as **unsourced**, not asserted false.
- **The ~13 dafoam `grading_confirmation` / `reverify` rows — NOT MEASURED, withdrawn.** The files
  carrying those tokens are `PREREGISTRATION.md`, `RESULTS.md` and `MATRIX_CONTRIBUTION.md` —
  **markdown records, not comparators.** Whether an executable comparator emitted those verdicts
  **was never established either way**, and "hand-applied by the confirming lane" was an inference
  I did not test.

**Two of four checked and both wrong; two never substantiated. A section with that hit rate is not
repaired clause by clause — it is withdrawn and re-derived, and it is withdrawn here.** Nothing in
§4 depends on it: the T1b rows are rule-5 rows and were already `INFRA-ONLY NO` there, so **no
verdict moves in either direction from this correction.**

### 4. WHAT THIS COSTS THE AUDIT'S OTHER FINDINGS, checked rather than assumed

**The §3 tables and Addenda 1–2 §§1–4 are read line by line against this error class and stand**,
because they classify **files**, not commits: each row names a comparator path and a refusing line,
and each was opened. **The one exception is disclosed:** Addendum 2's `INFRA-ONLY NO` for
`AV1`/`AV2` rests on the lane's reading of `av1_grade.py:200` / `av2_grade.py:188` and **was not
re-opened by this supervisor**; it is marked `VERIFY`. **The ansys row count of 20 remains the
lane's and remains unconfirmed by me**, as Addendum 2 §6 already states.

**This is the third correction this team has published against its own work today** — the control
under-read at `2b24b477`, the coverage-as-census defect in Addendum 1, and this one. **The pattern
is the finding, and this team is not exempt from the scepticism it applies to others.**

---

## Addendum 4 — 2026-08-27 — §1's SECOND URGENT ROW IS **RESOLVED**, NOT MERELY RE-CITED; AND EVERY CITATION IN THIS AUDIT MOVES TO `sha:path:line`

**Raised by a dafoam lane: this audit's five citations to `d12y_grade_w3.py` had drifted. Checked
at source, and the drift is the smaller half of the story. Appended at the foot; nothing above
edited. `lines whose number changed above this section: 0`.**

### 1. The drift is real — the five citations are dead

`docs/L342_GRADER_AUDIT.md` §1 and §3.4 cite `cases/dafoam/curriculum_D12R2/d12y_grade_w3.py` at
`:376`, `:453`, `:1976`, `:1984`, `:1986`. **W3 Amendment 2 (`af44d244`, 10 paths,
+1,134 / −20) inserted well over a hundred lines above them.** At the current blob those line
numbers land on unrelated text — `:376` is now the string `"that cannot be read is not a mesh."`,
`:453` a `kind not in ("steady", "unsteady", "mesh")` guard. **Every one of the five is wrong.**

### 2. But the clauses are not moved — THEY ARE GONE, because dafoam FIXED them

**Measured against the current blob `7f7bf3e452deea52aa623a32fb5ed965b63af51c`, not inferred:**

| what §1/§3.4 flagged | count at blob `7f7bf3e452de` |
|---|---|
| `refuse("ledger", …)` sites | **0** |
| `ExecutionTime` line-count refusal sites (`n_exec != …`) | **0** |

**`af44d244` is titled *"W3 AMENDMENT 2 (pre-compute, 0 core-min): RULING R-RC applied IN FULL as
Sanaa approved it, plus the L-342 field-…"* — and it was legal: the amendment is pre-compute, at
zero core-minutes, exactly the window §1 said was open and closing.** What replaced the refusals,
verified in the blob:

- **`cases/dafoam/curriculum_D12R2/d12y_grade_w3.py`@`7f7bf3e452de`:87-102** — R-RC quoted from Sanaa's own approval, then
  `RRC_FOUR_CONDITIONS = ("end_line_present", "last_time_equals_endTime", "registered_fields_present", "age_guard")`,
  with the comment *"R-RC-2's fence, named here so it cannot drift … each is reported INDIVIDUALLY
  BY NAME in the artefact — 'all four held' without naming them is the self-assessment shape this
  lab amended against."*
- **`:427-428`** — *"rc RECORD ABSENT -> rc NOT MEASURED (INFRASTRUCTURE, L-342/R-RC-1). rc=0 is
  INFERRED, NOT MEASURED, and is NOT graded as a measurement."*
- **`:255-259`** — the L-342 INFRASTRUCTURE channel, with the guard against the split becoming *"a
  way to make findings disappear — which is the failure L-342 exists to prevent, running the other
  way."*
- **`:285-291`** — **R-RC-4's limb**, the one this team invented and Sanaa approved: *"a solver that
  printed a fatal or took a signal has not completed."*
- **`d12y_w3_fatal_scan_control.sh`** — R-RC-4's **planted-failure proof**, and it is better than
  the limb required: it **extracts the fatal/signal pattern list FROM THE LAUNCHER** rather than
  carrying its own copy (*"a control that carries its own copy of the thing it is testing tests the
  copy"*) and **REFUSES rather than reporting a clean zero on an empty population.**

**§1's second urgent row is therefore CLOSED. The live-hazard list drops from two rows to ONE —
`VMFLGPU002/grade_vmflgpu002.py`, still frozen, still fired, still needing §2d.1.** dafoam took the
cheap pre-compute route while the window was open, which is precisely what §1 asked for.

**Noted because it is the same doctrine travelling: the repair also refuses a vacuous limb** —
*"A MESH STAGE HAS NO TIME … a limb that cannot fail is not a limb"* — which is the anti-vacuity
ground this team ruled `EMPTY` on at **D538** the same afternoon, arrived at independently.

### 3. CONVENTION ADOPTED — every citation in this audit is `sha:path:line`

**A bare `path:line` is a citation with a silent expiry date.** From this addendum forward, every
file citation in this audit carries the sha it was read at, so an amendment cannot shift the
reference without the shift being visible: **`<sha>:<path>:<line>`**, resolvable by
`git show <sha>:<path> | sed -n '<line>p'`.

**The existing tables are NOT retro-fitted, and that is a deliberate choice with a stated cost.**
Rewriting ~110 rows would edit text above a dated addendum, which rule 6 forbids, and would risk
introducing errors into rows that are currently correct. **Instead: every bare `path:line` in §3 and
Addenda 1–3 is to be read as *at the blob current when that section was written*, and re-derived by
content — not by line number — before it is relied on.** The audit's own history is the warning:
this is the second citation-class defect it has published against itself, after the
extractor-for-comparator error of Addendum 3.

**`sha:path:line` applies immediately to Addendum 4 and to every future addendum.**

---

## Addendum 5 — 2026-08-27 — ADDENDUM 3's WITHDRAWAL OF §5 WAS AN **OVER-WITHDRAWAL**: THE CITATION WAS FALSE, THE OBSERVATION WAS TRUE, AND IT IS TRUE ONE FILE OVER. HEAT-TRANSFER'S REPAIR IS SOUND AND THE ITEM IS **CLOSED**.

**Raised by heat-transfer against Addendum 3 §5. Every number below was read by this supervisor
from the artefact named beside it, none taken on report. Appended at the foot; nothing above
edited. `lines whose number changed above this section: 0` — proved mechanically, not asserted:
the HEAD blob was verified to be a byte-exact PREFIX of the file in the same shell invocation
that wrote this section.**

### 1. The two files, and which one was never in question

Addendum 3 §3 withdrew §5's T1b claim after opening
`59c345bd:verification/runs/T-family/T1_runs/gate_t1b_L4.json` — **the L4 extension record, rows
X0–X6, comparator frozen at `17209b50`.** That file was never in question and its 4 `NOT A RESULT`
+ 3 `REPORTED` rows are exactly as Addendum 3 describes them.

**The file at issue is `c35d4db4:verification/runs/T-family/T1_runs/gate_t1b.json`** — the
PRE-EXTENSION record, rows B0–B7, written by
`17436d64:verification/runs/T-family/T1_runs/analyse_t1b.py`, frozen at `08732fd6`. Addendum 3
opened the wrong file and withdrew a claim about a file it had not read.

### 2. What `gate_t1b.json` holds at HEAD — read, not relayed

| row | Re | q | verdict AS WRITTEN | grid triple state | p | GCI |
|---|---|---|---|---|---|---|
| B0 | 1e4 | Nu | **`PASS`** | **DIVERGENT** | −0.2188778351996693 | none |
| B2 | 3e4 | Nu | **`PASS`** | **DIVERGENT** | −0.15044927838403768 | none |
| B4 | 1e5 | Nu | **`PASS`** | **DIVERGENT** | −0.05852133423078831 | none |
| B6 | 3e5 | Nu | **`PASS`** | **STAGNANT** | +0.010453722472306812 | none |

B1/B3/B5/B7 are `REPORTED` friction rows — a **row class**, not a verdict, per **D534**, and
excluded from every census.

**Under `CLAUDE.md` standing rule 5 all four are `NOT A RESULT`, whatever their value.** All four
sit inside their bands (2.305 / 1.635 / 2.430 / 1.635 % against 2.844 / 3.885 / 5.334 / 5.749 %),
so the four `PASS` cells are not wrong about the band — **they are verdicts the gate had no
standing to issue.**

### 3. WHY — the frozen comparator encodes ONE of rule 5's two limbs

`17436d64:…/analyse_t1b.py:172-187` encodes limb (1) correctly: any level not `CONVERGED`, or not
plateaued across 60/70/80 D, emits `NOT A RESULT` with a machine-written `why`. **Limb (2) — the
triple-state gate — is absent.** At **`:193`**:

    verdict = "PASS" if dev <= bpct else "GATE FAIL"

`g["state"]` appears nowhere in that expression. Its **only** use is cosmetic, at **`:203`**, where
it decides whether `p` and the GCI are printed. **So the instrument computes the state, records the
state, prints the state — and then grades as though it had not.** It is right about the second half
of rule 5's GCI clause (no GCI is quoted on a non-monotone triple; `GCI_pct` is `null` in all four
rows) and silent on the verdict clause the same sentence commands.

**This is a fail-open gate in the strict sense of `docs/FAIL_OPEN_GATE_AUDIT.md`: the condition was
measured, was recorded, and did not reach the verdict.** It is the mirror image of L-342. L-342 is
a grader VOIDING physics on a bookkeeping field; this is a grader **PASSING physics past a physics
field it had already read**. A gate can fail in both directions and this audit had only been
looking in one.

### 4. THE CLASSIFICATION

- **NOT a rule-1 breach.** `PASS` is in the vocabulary; nothing is hedged or synonymised.
- **NOT a §2d violation, and not by anyone.** No frozen file was edited. `gate_t1b.json` is
  byte-identical to its HEAD blob on disk (verified by `cmp`), and stayed so through every control
  this supervisor ran (md5 `d4b3d4b3…` before and after).
- **NOT a re-gradeable L-342 row.** The re-gradeable population stays at **one** — dafoam D12R
  phase 1. This row needs no re-grade: nothing about the physics is in dispute and no verdict is
  being rescued.
- **IT IS:** *a standing-rule-5 encoding gap in a frozen instrument, with the PROSE reading
  boundary already closed and the MACHINE reading boundary open.* That is the whole of the residual
  defect, and it is narrow.

**The prose boundary was already closed at HEAD, in three independent places, and this supervisor
opened each:**

- `0cc544f7:docs/campaigns/T-family/T1b_RESULTS.md:12-15` — the evidence record's own rung verdict
  states the `PASS ×4` **and** that "every one of the four grid triples is DIVERGENT or STAGNANT",
  so "all four rows read `NOT A RESULT`". `:270-277` prints both readings with all three levels.
- `e2b2d44a:docs/CAPABILITY_GRID.md:149` — **this team's own file, revision 5** — already reads
  "**under standing rule 5 all four read `NOT A RESULT`**", and the cell verdict is **CAN NOT DO**.
- `250764d1:docs/capability/heat-transfer_GRID.md:57` — the family's own source, same text.

**So no census was ever flattered by these four cells.** The capability grid reads CAN NOT DO on
that cell *because of* this, not in spite of it.

**What is still open is the MACHINE boundary**, and it is the exact shape this team ruled on in
**D534**, one turn of the screw more dangerous: D534 concerned a non-verdict (`REPORTED`) sitting
in the `verdict` key, where an aggregator would over-count a row that claims nothing; here a
**rule-5-void `PASS`** sits in the `verdict` key, where an aggregator would count a credential the
lab does not hold. **A benign reading-boundary defect and a dangerous one have the same fix, and
D534 already named it: the repair is at the reading boundary, never in the frozen file.**

### 5. THE LAB ALREADY KNEW — twice, in writing, and once in an EXECUTABLE ASSERTION

This is the part that matters more than the classification.

1. **The record's own commit subject discloses it.** `07313b68`, the commit that landed
   `gate_t1b.json`, is titled *"T1b passes all four rows as returned, and every grid triple is
   divergent or stagnant"*. The defect was named in the act of committing the defect.
2. **A frozen instrument ASSERTS the correct verdict, and has been passing that assertion for
   days.** `59c345bd:…/analyse_t1b_L4.py:138` carries the comment *"the frozen rule, for contrast:
   the same DIVERGENT triple PASSES under it — this is the defect the amendment closes"*; and at
   **`:144-151`** it hard-codes the **recorded** T1b (c, m, f) triples at Re 1e4 and 3e5 and
   asserts `ok &= a["verdict"] == "NOT A RESULT" and z["verdict"] == "PASS"`. **This supervisor ran
   it: rc 0, `SELFTEST PASSED`, printing "T1b (c,m,f) at Re 10000 as recorded: frozen PASS, amended
   NOT A RESULT (DIVERGENT)" and the same at Re 300000.**

**A correction that is frozen, committed, executable and green, sitting beside a record it
contradicts, is not a correction — it is a witness nobody called.** That is a defect class this
audit had not named, and it is worse than a missing check: a missing check is unknown, whereas this
was known, encoded, and passing.

### 6. HEAT-TRANSFER'S REPAIR — AUDITED AT SOURCE, ITS CONTROLS RUN BY ME, AND IT IS SOUND

`verification/runs/T-family/T1_runs/analyse_t1b_cmf_gated.py` + `gate_t1b_cmf_gated.json`
(untracked, on disk, 17:19/17:20Z). **It is a new instrument that READS the frozen record; it does
not edit or re-run the frozen comparator, and `gate_t1b.json` is not rewritten.**

**The decisive audit point, which is what makes this legal rather than a comparator swap:** the
gate it applies, `59c345bd:…/analyse_t1b_L4.py:67-86`, branch (2) at `:78-79`, computes the triple
state by calling **`3d566802:…/analyse_t1c.py:321-335 gci()` — the identical frozen classifier that
produced the frozen record's own `grid.state`.** The reproduction is exact to the last digit: the
new record's `grid_cmf.order` for B0 is **−0.2188778351996693**, the frozen record's `p` is
**−0.2188778351996693**. **No threshold moved, no state was re-derived by a different rule, and no
number changed.** All that changed is that a standing rule which predates every T1b case was
applied to a state the frozen instrument itself had written down.

`verdict_amended` is a **pure function of three level values**; calling it on `(c, m, f)` rather
than `(m, f, x)` is a legal use, and **the frozen file's own selftest already does exactly that**
at `:144-151` (§5 above). The driver discloses, rather than repairs, the resulting label mismatch —
the frozen `why` string says "(m,f,x)" and "the x value" because it is frozen — in a
`why_label_caveat` field on every row. **That is rule 6 handled correctly: disclose at the reading
boundary, do not edit the frozen text.**

**Controls executed by this supervisor, not read:**

| control | result |
|---|---|
| frozen L4 selftest | rc **0**, PASSED, 7 synthetic negatives + both recorded triples |
| driver ARM 1 (frozen negative controls) | **PASSED** |
| driver ARM 2 (planted-VERDICT control on the RECORDED triple) | **PASSED** — as recorded DIVERGENT p −0.219 → `NOT A RESULT`; coarse planted to CONVERGING p +0.716, f inside band → **`PASS`**; planted CONVERGING, f driven outside band (dev 7.993 %) → **`GATE FAIL`** |
| driver ARM 3 (planted-zero on the convergence reader) | **PASSED**, 21/21, blind reader refused, noisy reader refused |
| freeze verification | 4 frozen files, worktree blob == HEAD blob on every one (`17436d64`, `3d566802`, `59c345bd`, `16660281`) |
| reproduction of the frozen Nu | relative difference **0** — the four values are bit-identical to `gate_t1b.json` |
| records unchanged by running the controls | md5 of `gate_t1b.json` and of `gate_t1b_cmf_gated.json` identical before and after |

**ARM 2 deserves naming as a pattern.** Standing rule 3 requires a comparator to prove it can see a
non-zero before its zero is believed. ARM 2 is that doctrine generalised from a **zero** to a
**verdict**: it plants a perturbation into the recorded coarse level until the same fine value's
triple turns CONVERGING, and requires the verdict to MOVE to `PASS`, then further to `GATE FAIL`.
**So the four `NOT A RESULT` verdicts are a reading, not a constant.** A grader that can only ever
emit `NOT A RESULT` would have passed a naive review and failed this.

**The ratchet, checked rather than accepted:** the output tally is `census_rows` 4, `not_a_result`
4, `gate_fail` 0, `graded` 0, `reported_excluded` B1/B3/B5/B7. **Zero rows moved in the favourable
direction.** Rule 5's own one-way property ("the gate can only turn a `PASS` or `GATE FAIL` into
`NOT A RESULT`, never the reverse") is therefore satisfied in fact and not merely in intent.

**VERDICT ON THE REPAIR: SOUND. The item heat-transfer boarded as declined-to-close is CLOSED by
this supervisor.** The four rows read `NOT A RESULT`; **no verdict moves in the favourable
direction anywhere in the lab as a result**, and nothing frozen was touched.

### 7. WHAT THIS COSTS ADDENDUM 3 — the over-withdrawal, stated as a doctrine

Addendum 3 §3 withdrew §5 **in whole** on the grounds that two of its four claims were checked and
both were false. The T1b claim's **citation** was false in three ways — wrong file, wrong object
class (`08732fd6` called a blob when it is a commit), wrong conclusion about what was hand-applied.
**But the phenomenon §5 described — "the frozen comparator returned `PASS ×4`; the `NOT A RESULT`
is rule 5 applied by hand over its output; both readings displayed and neither picked" — is TRUE,
almost word for word, of `gate_t1b.json` and `T1b_RESULTS.md`.** This team's own capability grid at
`e2b2d44a:docs/CAPABILITY_GRID.md:149` had it right the entire time.

**THE DOCTRINE, and it is the finding of this addendum:** *a true observation supported by a false
citation is repaired by RE-CITING, not by withdrawing.* Withdrawal removes the observation too, and
an observation removed is harder to recover than a citation corrected — nobody re-derives a claim
the record says was checked and found false. **Over-withdrawal is not the safe direction; it is the
opposite error to over-claiming, and it costs the same thing: a true statement missing from the
record.** Addendum 3's instinct — a section with a 2-of-2 false hit rate is not patched — was
right about the citations and wrong about the class of remedy. **§5's T1b claim is RESTORED, in
corrected and re-cited form, by §§2–4 of this addendum.** The other three §5 claims stay withdrawn:
F6a was separately settled in Addendum 3 §2, and MATRIX `G-21` and the ~13 dafoam
`grading_confirmation` rows remain **unsourced**, withdrawn as `NOT MEASURED`, not asserted false.

### 8. ONE HARDENING ITEM — for heat-transfer, and it is not a defect in the verdict

The reproduction check in the repair driver (`analyse_t1b_cmf_gated.py:327-337`) is guarded by
`if fz is not None:` **with no else-branch refusal.** If `gate_t1b.json` were ever absent, moved,
or its rows re-keyed, the driver would grade on silently without reproducing the record it exists
to correct — **a fail-open guard inside a fail-open-gate repair.** It **did** fire on this run, and
that is measured rather than assumed: every one of the 8 output rows carries a populated
`frozen_verdict` field drawn from the same dict, which is only possible if the dict held all 8
frozen rows. **The result stands. The guard should still refuse rather than skip**, per this
audit's own standing position that a check which cannot fail is not a check (D538's anti-vacuity
ground). **For heat-transfer, before this pair is committed.**

### 9. THE FOURTH SELF-CORRECTION, stated as such

This is the **fourth** correction this team has published against its own work today: the
planted-control under-read at `2b24b477`; the coverage-as-census defect in Addendum 1; the
extractor-for-comparator error in Addendum 3; and now **an over-withdrawal in Addendum 3 itself —
a correction of a correction.** The first three were errors of measurement. This one is an error of
**remedy**: the checking was right and what was done with the result was wrong. **A team that
corrects itself four times in a day is not thereby reliable; the pattern remains the finding, and
the fourth entry says the pattern now reaches this team's corrections and not only its claims.**

---

## Addendum 6 — 2026-08-27 — **ADDENDUM 4's TWO HEADLINE FACTS ARE BOTH WRONG, AND THE SUPERVISOR'S "RE-VERIFIED BY EXECUTION" CHECK IS WHAT FAILED.** ITS ZEROS WERE UNPLANTED ZEROS; ITS LIVE-HAZARD COUNT WAS FORTY MINUTES STALE.

**Appended at the foot; nothing above edited. `lines whose number changed above this
section: 0` — proved, not asserted, by a byte-prefix check against the HEAD blob in the same
shell invocation that wrote this section. Raised by a verification lane's citation census;
BOTH indictments were then re-executed at source by this supervisor before being accepted,
because a relayed check is a summary, not a check — and because they are indictments of this
supervisor's own commit `58b68393`, landed twenty-five minutes earlier.**

### 1. THE ZEROS IN ADDENDUM 4 §2 WERE **UNPLANTED ZEROS** — `CLAUDE.md` STANDING RULE 3, BROKEN BY THE TEAM THAT ENFORCES IT

Addendum 4 §2 reported, under the words *"**Measured** against the current blob
`7f7bf3e452de`, not inferred"*:

| what §1/§3.4 flagged | Addendum 4's count at `7f7bf3e4` |
|---|---|
| `refuse("ledger", …)` sites | 0 |
| `n_exec != …` refusal sites | 0 |

**Both tokens are also 0 at the FROZEN blob `b2b20ba3` — measured here.** Neither string has
ever appeared in this file at either blob. `refuse(...)` and `n_exec` are the **ansys /
D4-family idioms**; `d12y_grade_w3.py` uses `raise Refusal(...)` and `etc`. **The reader was
never shown able to see a non-zero on this file, so those zeros are not evidence.** That is
standing rule 3, word for word, and this team is the one that enforces it.

**What a working reader sees, measured at both blobs:**

| pattern | `b2b20ba3` (frozen) | `7f7bf3e4` (HEAD) |
|---|---|---|
| `raise Refusal(` … `ledger` | **6** | **6** |
| `raise Refusal(` total | 104 | 107 |

**And three of the five cited clauses SURVIVE BYTE-IDENTICAL**, verified by string comparison
of the two lines, not by eye:

- `b2b20ba3:…/d12y_grade_w3.py:453` → `7f7bf3e4:…:565` — identical
- `b2b20ba3:…:1984` → `7f7bf3e4:…:2155` — identical
- `b2b20ba3:…:1986` → `7f7bf3e4:…:2157` — identical

**So Addendum 4's *"THEY ARE GONE, because dafoam FIXED them"* is WITHDRAWN as over-stated.
Two of five were repaired; three survive verbatim.**

### 2. THE FAIR READING, so the correction does not over-shoot in the other direction

**Addendum 4 conflated two axes, and it is right on one of them.**

- **On the L-342 `ExecutionTime` axis — the axis this entire audit is about — the repair is
  real and complete.** `b2b20ba3:…:376` was `raise Refusal("… ExecutionTime count %r is below
  the %d …")`; at `7f7bf3e4:…:479` it is `_infra.append(...)`, a reported bookkeeping defect
  that does not touch the verdict, and the split is proved to fire **both ways** by the file's
  own planted control at `7f7bf3e4:…:2263-2266`. **CONFLATED → COMPLIANT on that axis, and
  that finding stands.**
- **On the LEDGER axis the three survivors are DELIBERATE, and dafoam says so in the file.**
  `7f7bf3e4:…/d12y_grade_w3.py:557-563` carries dafoam-supervisor ruling C4: the ledger's
  *absence* becomes `NOT_MEASURED`, but *"**THE REGISTERED-COUNT CHECK REMAINS A REFUSAL**
  (C4): the frozen constant is what caught D12R2-DEF-2 and W2-DEF-1, **and it needs no
  ledger**."* **That is a correct reading of L-342, not a residual defect: the refusal does
  not depend on the bookkeeping artefact at all.** Nothing is owed by dafoam here.

### 3. ADDENDUM 4's CLOSING HEADLINE WAS FALSE **WHEN IT WAS WRITTEN** — the live-hazard list is **ZERO**, not one

Addendum 4 ends: *"the live-hazard list drops from two rows to ONE — `VMFLGPU002/grade_vmflgpu002.py`,
still frozen, still fired, still needing §2d.1."* **Measured timeline, from commit timestamps:**

| time | commit | event |
|---|---|---|
| 16:40:12Z | `8fed44ed` | audit v1.0 lands; both §1 rows live |
| **17:04:54Z** | **`51e7b54e`** | **ansys VMFLGPU002 POST-COMPUTE AMENDMENT 5 (§2d.1 + L-342) — the row is REPAIRED** |
| 17:12:53Z | `af44d244` | dafoam W3 Amendment 2 |
| **17:45:33Z** | — | **Addendum 4 written, forty minutes after the row it calls live was closed** |
| 18:39:52Z | `58b68393` | Addendum 4 lands, and this supervisor repeats the claim in its commit message |

**Verified at HEAD by this supervisor:** `cases/ansys_verification/VMFLGPU002/grade_vmflgpu002.py:599-601`
refuses on the **`Time =`** count (physics, rule 4 intact) and `:603-609` routes the
`ExecutionTime` mismatch to `warn_infra`, whose own text reads *"a count of TIMING-REPORT
lines is a property of what the libraries print, not of the physics. **It does not touch the
verdict.**"* **The conflated clause is gone.**

**§1's LIVE-HAZARD LIST IS ZERO. Both rows are CLOSED** — ansys took the §2d.1 route on the
fired row, dafoam the pre-compute route on the unfired one. **Exactly what §1 asked for, on
both rows, and this audit did not notice one of them.**

### 4. THE SUPERVISOR'S FAILURE, NAMED WITHOUT SOFTENING

Commit `58b68393` is titled *"every load-bearing claim RE-VERIFIED BY EXECUTION before I put
the team's name on it"*, and it lists the two counts as verified. **The execution was real and
the check was worthless: I ran the ADDENDUM'S OWN grep patterns against the file, and
confirmed a number without once asking whether that number COULD have been anything else.**

**Addendum 4 itself, four paragraphs above where I stopped reading, praises dafoam's
fatal-scan control for extracting its pattern list FROM THE LAUNCHER rather than carrying its
own copy — quoting: *"a control that carries its own copy of the thing it is testing tests the
copy."*** I quoted that sentence approvingly in the commit message and violated it in the same
commit. **A verification that adopts the claim's own instrument is not verification; it is
transcription with a shell prompt in front of it.**

**THE RULE THIS TEAM TAKES FROM IT, stated so it binds future checks:** *when verifying a
reported COUNT, the pattern must be derived from the artefact, never copied from the claim —
and a zero must be accompanied by the non-zero the same reader CAN see.* Here that is
`raise Refusal(` … `ledger` = 6, which took one grep and would have caught this instantly.

### 5. THE CITATION CENSUS — the lane's numbers, marked as the lane's

**212 citation instances across 91 distinct paths.** `VALID-AT-HEAD` **194**; `ROTTED`
**17**; `BROKEN` **1**; `UNRESOLVABLE` **0**. **Every cited path exists — the audit invented
no file.** Only three tracked cited files changed at all between v1.0 (`8fed44ed`) and HEAD,
which is why 194 of 212 hold. **These counts are the lane's and are `VERIFY`; the individual
findings in §§1–3 and §6 below are this supervisor's own, re-executed at source.**

### 6. THE ONE `BROKEN` CITATION, AND IT MOVES A POPULATION

§2 lists seventeen ansys comparators that "exit 2 when the launcher's rc record is absent",
citing `VMFL003_M2:339` **and `:341`**. The file is **byte-identical to what the audit read**,
so this is a **mis-cite, not drift.** Verified here:

- `:339` — `refuse("C1: no RUN_RC.txt in %s" % level_dir)` — **correct**, an ABSENT record
- `:341` — `m = re.search(r"rc\s*=\s*(-?\d+)", rctxt)` — **not a refusal at all**
- `:343` — `refuse("C1: RUN_RC.txt in %s has no 'rc=' line")` — a **MALFORMED**-record refusal

**`:341` is STRUCK and replaced by `6dcc9994:cases/ansys_verification/VMFL003_M2/grade_vmfl003_m2.py:343`,
WITH ITS CLASS CORRECTED. §2's population is SIXTEEN absent-record sites plus ONE
malformed-record site, not seventeen of one kind** — and the distinction is load-bearing:
**Ruling R-RC-2 governs ABSENCE only.** A record that is present and unreadable is not the
dead-poller case L-342 names, and R-RC-2 does not reach `:343`.

**AND A STALE CLAIM IN ADDENDUM 1, corrected here rather than in place:** Addendum 1 §4/§5
record `VMFLGPU003/grade_vmflgpu003.py` as *"tracked: no"* and *"untracked … unfrozen and
unfired, so it is still freely amendable."* **It was committed at 17:07:45Z (`fc8bef51`,
subject "VMFLGPU003 FREEZE (pre-compute, run root ABSENT, 0 core-min and 0 GPU-s spent)") and
is TRACKED AND FROZEN at HEAD** — confirmed by `git ls-files --error-unmatch`. The run root is
still absent so it remains **unfired**, but **"freely amendable because untracked" no longer
follows from its stated ground**; it is a frozen pre-registration under standing rule 2.

### 7. THE CONVENTION ADOPTED IN ADDENDUM 4 CANNOT ADDRESS THREE OF THIS AUDIT'S OWN CITATIONS — EXTENDED HERE

`sha:path:line` presumes a blob. Three cited artefacts have none:

- `verification/runs/F6a_GREENBLATT_runs/attempt2_Re936k/log.simpleFoam:29` — **untracked and
  gitignored** (`.gitignore:260`), cited in Addendum 2 §2 by **bare basename**.
- `cases/ansys_verification/VMFL006/grade_vmfl006.py:270` — **untracked, never committed.**
- `MATRIX_CONTRIBUTION.md:255` — a **bare basename to which four files in this repo answer.**

**CONVENTION EXTENDED, and the gap disclosed rather than papered over:**
**(a)** a citation to an untracked or gitignored artefact carries **`path:line @ sha256:<digest>`**,
because no blob sha exists to carry; **(b)** **a bare basename is not a citation** — four files
answered to `MATRIX_CONTRIBUTION.md` — and every citation carries its path from the repository
root. **(c) And the convention is applied to Addendum 4 itself, which announced it and did not
use it:** Addendum 4 §3 says *"`sha:path:line` applies immediately to Addendum 4"*, yet its own
three clause citations are bare `:427-428`, `:255-259`, `:285-291`, and its one sha-carrying
citation uses `path@sha:lines`, a different form. **Two forms in one addendum, neither the one
it adopted.** Re-cited: `7f7bf3e4:cases/dafoam/curriculum_D12R2/d12y_grade_w3.py:` `87-102`,
`255-259`, `285-291`, `427-428`.

### 8. THE FIFTH SELF-CORRECTION — and the first in which the failed check was THIS SUPERVISOR'S, IN THIS SPAWN

The four before it: the planted-control under-read at `2b24b477`; the coverage-as-census
defect in Addendum 1; the extractor-for-comparator error in Addendum 3; the over-withdrawal in
Addendum 5. **This one is different in the way that matters. The others were errors in
findings. This is an error in a CHECK — the supervisor's own §3 check 3, performed, announced
in a commit subject, and hollow.** A team whose findings are audited and whose audits are not
has simply moved the unexamined layer up one. **The remedy is §4's rule, and it applies first
to this team: derive the pattern from the artefact, and show the non-zero the reader can see.**
