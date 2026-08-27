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
