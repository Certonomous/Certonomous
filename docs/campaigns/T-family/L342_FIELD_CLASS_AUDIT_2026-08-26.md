# L-342 field-class audit — heat-transfer territory (2026-08-26)

**Rule audited against:** L-342 (`d4d0c29d`), Sanaa's words verbatim: *"a bookkeeping
failure invalidates the bookkeeping, never the physics artifacts — and graders must
separate physics-critical fields from infrastructure fields so a dead poller can never
void a run again."*

**Classification applied (supervisor's, binding on this audit, one rule for all files):**

| class | fields |
|---|---|
| PHYSICS-CRITICAL | the solver's own exit status written INSIDE the detached wrapper (`rc=` in `STATUS.<case>` / `rc_solve=` in a runner-written `DONE.<case>`; an in-wrapper rc is not a poller), the `End` line, last time == `endTime`, fields present at `endTime`, `ExecutionTime` count, the age guard against the case's own `0/T`, `reconstructPar` rc where parallel, `DONE.<case>` EXISTENCE (it is the completion rule's certificate) |
| INFRASTRUCTURE | `wall`/`wall_s`, `timeout_s`, `ranks`, `core_min`, `capped`, `checkMesh_rc`, `solver_path`, `note`, launch logs, `log.checkMesh`, `COST.txt`, DONE-marker mtimes/timestamps, freeze-checker stamps, anything a poller writes — absent → NOT MEASURED, disclosed, grade proceeds |

**Verdict vocabulary of this audit:** CLEAN (refuses / moves a verdict on physics fields
only), CONFLATING (an infrastructure field can void a run or move a verdict — line quoted),
N/A (grades nothing). ZERO COMPUTE. Read-only on every instrument: **no instrument was
edited by this audit** (see §3 — no class (ii) rung exists in this territory at HEAD
`128d48d0`, so no amendment is owed).

**Population:** `git ls-tree -r HEAD --name-only` at `128d48d0`, pattern
`mark_done_*.py | analyse_*.py | grade_*.py` under `verification/runs/T-family/`,
`verification/runs/F14-cooling-ladder/`, `verification/runs/THERMAL_K0_runs/`, plus
`scripts/mark_done_k0f.py` and `scripts/analyse_k0f.py` → **55 files**, plus
`verification/runs/THERMAL_K0_runs/analyse.py` (name-adjacent, listed for completeness)
= **56 rows**. `T4b_runs/` and `T10aR2_runs/` hold no tracked instrument at HEAD (their
analysers are in progress on another lane) and are outside this table by the brief.

## 1. Table

Abbreviations: DONE = refuses when `DONE.<case>` is absent; STATUS-rc = reads the
in-wrapper `rc=` from `STATUS.<case>`; age = age guard vs `0/T`; spec = refuses when
the frozen specification / registered JSON cannot be read or disagrees with its own
derivation (a freeze check on the gate, not a run field); mesh/field = refuses when a
field, patch, time directory or monitor series cannot be read.

| # | file | refuses / moves a verdict on | class of those fields | verdict |
|---|---|---|---|---|
| 1 | `scripts/mark_done_k0f.py` | STATUS absent (exit 2), STATUS-rc≠0, End, last time, per-closure fields, ExecutionTime count, age; launch guard (clause 7). `wall=`/`checkMesh_rc=` in STATUS are parsed only through `\brc=(\d+)` (l.152) — never required | physics only | CLEAN (K0f RUNNING — audited read-only) |
| 2 | `scripts/analyse_k0f.py` | ten DONE (l.1551), case dir absent (l.1682), boundaryField readable (l.687–692), spec/derivation | physics + spec | CLEAN (K0f RUNNING — audited read-only) |
| 3 | `F14/K0b_D403_rerun/analyse_k0b_mesh.py` | mesh/field readable, `lab_paths` resolvable, blockMesh/writeCellCentres rc; `COST.txt` absent → `cost()` returns None, cost row omitted (l.377–389) | physics; cost handled | CLEAN |
| 4 | `F14/K0b_D403_rerun/grade_d403.py` | nothing refused; verdict from `measured_*.json` vs published values | physics | CLEAN |
| 5 | `F14/K0b_D406_repair/analyse_k0b_mesh.py` | as #3 | physics | CLEAN |
| 6 | `F14/K0b_D406_repair/grade_d406.py` | as #4 | physics | CLEAN |
| 7 | `F14/K0b_mesh_sensitivity/analyse_k0b_mesh.py` | as #3 (l.64–285 refusals; `cost()` l.370–389 tolerates absence) | physics | CLEAN |
| 8 | `F14/K0cG_runs/analyse_k0cg.py` | DONE (l.47) | physics | CLEAN |
| 9 | `F14/K0cP_runs/analyse_k0cp.py` | DONE (l.59) | physics | CLEAN |
| 10 | `F14/K0cQ_runs/analyse_k0cq.py` | DONE (l.134) | physics | CLEAN |
| 11 | `F14/K0cR_runs/analyse_k0cr.py` | DONE (l.138) | physics | CLEAN |
| 12 | `F14/K0cS_runs/analyse_k0cs.py` | DONE (l.455), marker `rc_solve≠0` (l.467 — in-wrapper rc written by the runner into the marker), spec rows (l.140), face closure (l.219) | physics + spec | CLEAN |
| 13 | `F14/K0cT_runs/analyse_k0ct.py` | spec (l.148–297, 1154), field/patch/time dir/CASE.txt (l.376–425), writeCellCentres (l.435), monitor series (l.582–624) | physics + spec | CLEAN |
| 14 | `F14/K0cX_runs/analyse_k0cx.py` | spec (l.132–266, 810), field/time dir (l.336–390), hotFlux history (l.651–662); DONE-marker `wall_seconds`/`iterations` read as optional diagnostics, `None` when absent (l.587–599) | physics + spec; infra optional | CLEAN |
| 15 | `F14/K0c_runs/analyse_k0c.py` | spec (l.173–225), field/time dir (l.250–290), held dT / plant witness / flux cross-check (l.400–500); `COST.txt` absent → `cost_of()` None (l.576–578) | physics + spec | CLEAN |
| 16 | `F14/K2b_runs/analyse_k2b.py` | `physics_rules.yaml` keys (l.91), sample count / span in the log (l.192–228 → `REFUSED`) | physics | CLEAN |
| 17 | `F14/K2b_runs/analyse_k2bU.py` | sample count / T_in span (l.110–128) | physics | CLEAN |
| 18 | `F14/K2b_runs/analyse_k2bU3.py` | decay-vs-aliasing distinguishability (l.60) | physics | CLEAN |
| 19 | `F14/K2e_runs/analyse_k2e.py` | field parse / uniform field / time dirs / solver log / cell count (l.103–237), threshold drift (l.421); `heat_balance.py` refusal is carried as a `note`, not a verdict (l.330–333) | physics | CLEAN |
| 20 | `T-family/E4_runs/analyse_e4a.py` | DONE (l.518), patch face counts / points (l.277–282), spec | physics + spec | CLEAN |
| 21 | `T-family/E4_runs/mark_done_e4a.py` | STATUS-rc, End, last time, fields, count, age | physics only | CLEAN |
| 22 | `T-family/E4a2_runs/analyse_e4a2.py` | DONE (l.348), frozen-module restore (l.355), spec | physics + freeze | CLEAN |
| 23 | `T-family/E4a2_runs/mark_done_e4a2.py` | frozen instrument hash / case list / field set (l.68–83) then `mark_done_e4a.check` clauses | physics + freeze | CLEAN |
| 24 | `T-family/T10aR_runs/analyse_t10aR.py` | DONE own + T10a `B_m`/`B_f` (l.516–519), Fs/r agreement (l.512), exact derivation (l.521) | physics + spec | CLEAN |
| 25 | `T-family/T10aR_runs/mark_done_t10aR.py` | STATUS-rc, End, last time, fields, count, age | physics only | CLEAN |
| 26 | `T-family/T10aVF_runs/analyse_t10avf.py` | nothing — streams `constant/F`, reports rowSum; no verdict | — | N/A |
| 27 | `T-family/T10a_runs/analyse_t10a.py` | registered vs derived references (l.804), DONE (l.810) | physics + spec | CLEAN |
| 28 | `T-family/T10a_runs/mark_done_t10a.py` | as #25 | physics only | CLEAN |
| 29 | `T-family/T11_runs/analyse_t11.py` | DONE (l.346) | physics | CLEAN |
| 30 | `T-family/T11_runs/mark_done_t11.py` | STATUS absent/no rc; **`capped` absent → NOT DONE**; End, last time, fields, count, age | **`capped` is INFRASTRUCTURE** | **CONFLATING** — l.57–59: `if "capped" not in d: return None, ("STATUS carries no \`capped\` witness: %r -- not written by run_one_t11.sh, and rc alone cannot separate a cap-stop ...")` → the case is NOT DONE with rc=0 and every physics clause met |
| 31 | `T-family/T1_runs/analyse_dts.py` | own completion rule (l.113–197) + DONE (l.581), face geometry (l.874), station (l.625) | **mixed** | **CONFLATING** — l.194–197: `ck["cells_parsed"] = rec["cells"] is not None` (from `log.checkMesh`) and `ck["exec_seconds_parsed"] = rec["exec_seconds"] is not None` are conjuncts of `rec["complete"] = all(ck.values())`, and l.552 refuses on `not rec["complete"]`; l.571 also refuses when an existing `DONE.<case>` differs from `marker_text()` (l.201–205), whose content includes `exec_seconds` and `finished_utc` (= `log.solve` mtime) |
| 32 | `T-family/T1_runs/analyse_dts_p.py` | imports `DTS.completion` (l.187–190 refuse on `not rec["complete"]`; l.203 marker-text disagreement), `SLUG_JSON` (l.145), station (l.257–260) | **mixed (inherited)** | **CONFLATING** — inherits #31's `cells_parsed` / `exec_seconds_parsed` / `finished_utc` conjuncts unchanged |
| 33 | `T-family/T1_runs/analyse_pesweep.py` | planted control (l.147), ≥3 positive points (l.193) | physics | CLEAN |
| 34 | `T-family/T1_runs/analyse_t1b.py` | DONE (l.138) | physics | CLEAN |
| 35 | `T-family/T1_runs/analyse_t1b_L4.py` | DONE (l.173) via `T1B.refuse` | physics | CLEAN |
| 36 | `T-family/T1_runs/analyse_t1c.py` | DONE (l.344), exact derivation (l.347), `CASE.txt` keys (l.108) | physics + spec | CLEAN |
| 37 | `T-family/T1_runs/mark_done_t1b.py` | STATUS-rc, End, last time, fields, count, age | physics only | CLEAN |
| 38 | `T-family/T1_runs/mark_done_t1b_L4.py` | as #37 for both segments; clause 6 also requires fields NEWER than `STATUS.<case>` (l.33, 90–92) — a second age datum written in-wrapper, treated as physics | physics only | CLEAN |
| 39 | `T-family/T1_runs/mark_done_t1b_ext1.py` | as #38 (STATUS2/STATUS3 rc, two End lines, raised endTime, age) | physics only | CLEAN |
| 40 | `T-family/T3_runs/analyse_t3.py` | DONE (l.795), planted zero (l.801), mesh/patch/nCells (l.165–485); `read_status` (l.758–765) parses `rc= wall= checkMesh_rc=` for the COST block only — a non-matching STATUS yields `wall_s=None` and cost `None` (l.917–923), never a refusal; `done_markers` mtimes (l.1003) are recorded, not gated | physics; infra disclosed | CLEAN |
| 41 | `T-family/T3_runs/analyse_t3_rff.py` | DONE (l.77), planted zero (l.85); outlet guard row absent → NOT MEASURED (l.71) | physics; already split | CLEAN (in progress on another lane — audited read-only) |
| 42 | `T-family/T3_runs/mark_done_t3.py` | STATUS-rc, End, last time, fields, count, age | physics only | CLEAN |
| 43 | `T-family/T3_runs/mark_done_t3_ext1.py` | STATUS/STATUS_EXT1 rc, two End lines, endTime > 20000, last time, count, age; selftest forges `wall=`/`endTime=` in STATUS but never requires them | physics only | CLEAN |
| 44 | `T-family/T3_runs/mark_done_t3_rff.py` | physics: rc, `reconstructpar_rc`, End, last time, fields, count, age; STATUS absent → exit 2. INFRA tuple (l.31) disclosed, never refused; selftest l.144 drives it | already split per L-342 | CLEAN (in progress on another lane — audited read-only) |
| 45 | `T-family/T4_runs/analyse_t4.py` | DONE (l.462) | physics | CLEAN |
| 46 | `T-family/T4_runs/mark_done_t4.py` | STATUS absent/no rc; **`capped` absent → NOT DONE**; End, last time, fields, count, age | **`capped` is INFRASTRUCTURE** | **CONFLATING** — l.74–77: `if "capped" not in d: return None, ("STATUS exists but carries no \`capped\` witness: %r -- it was not written by run_one_t4.sh, and rc alone cannot separate a cap-stop ...")` → NOT DONE with rc=0 and every physics clause met |
| 47 | `T-family/T5_runs/analyse_t5.py` | STATUS absent → refuse (l.67), rc, End, last time, count, fields, age (l.124–132); `capped=1` PRESENT → NOT DONE (l.85 — a witness that the solver was stopped, coincident with last time ≠ endTime); `capped` ABSENT proceeds (`st.get`) | physics; infra tolerant | CLEAN (T5 lane building — audited read-only) |
| 48 | `T-family/T5_runs/mark_done_t5.py` | STATUS absent → exit 2 (l.68), `rc≠"0"` (l.72), `capped=="1"` present → NOT DONE (l.74), End, last time, count, fields, age; `note` appears only in the message (l.73) | physics; infra tolerant | CLEAN (T5 lane building — audited read-only) |
| 49 | `T-family/T8_runs/analyse_t8.py` | freeze set (l.1120), completion (l.1154 ← `check_completion` l.385–490), mesh/geometry/planted zero/fits (l.1167–1279) | **mixed** | **CONFLATING** — l.426–427: `if not note("ranks == 1", st.get("ranks") == "1", ...): return False, "STATUS records ranks=%s; section 6 registers 1"`; l.437–442: `if not note("timeout = cap_core_min * 60 / ranks", str(st.get("timeout_s")) == str(want_to) == str(REGISTERED_TIMEOUT_S[level]), ...): return False, "the cap instrument is not the registered one"` — both are conjuncts of strict completion and refuse the level at l.1154 when `ranks`/`timeout_s` are ABSENT from STATUS; l.1404 `act = float(st["core_min"])` raises `KeyError` (uncaught) on an absent `core_min` after the verdicts print, so the exit code is lost |
| 50 | `T-family/T9aH_runs/analyse_t9a.py` | DONE (l.468), registered vs derived (l.461), mesh/layer map/patches (l.262–374) | physics + spec | CLEAN |
| 51 | `T-family/T9aH_runs/analyse_t9aH.py` | exact wall derivation (l.379–383), plant visibility (l.449–456), via `A.` #50 | physics | CLEAN |
| 52 | `T-family/T9aH_runs/mark_done_t9a.py` | STATUS-rc, End, last time, fields, count, age | physics only | CLEAN |
| 53 | `T-family/T9a_runs/analyse_t9a.py` | as #50 | physics + spec | CLEAN |
| 54 | `T-family/T9a_runs/analyse_t9aD.py` | two exact routes agree (l.144), registered vs derived (l.332), DONE (l.356) | physics + spec | CLEAN |
| 55 | `T-family/T9a_runs/mark_done_t9a.py` | as #52 | physics only | CLEAN |
| 56 | `T-family/T9a_runs/mark_done_t9aD.py` | delegates to the frozen `mark_done_t9a.check` clauses | physics only | CLEAN |
| — | `THERMAL_K0_runs/analyse.py` (name-adjacent) | field parse / `writeCellCentres` rc only; measurements, no verdict | — | N/A |

Rows 26 and the name-adjacent row are the two N/A entries; the numbered list holds 55
population files plus one name-adjacent file = 56 rows.

## 2. Counts

| verdict | count | files |
|---|---|---|
| CLEAN | **49** | all rows not listed below |
| CONFLATING | **5** | #30 `mark_done_t11.py`, #31 `analyse_dts.py`, #32 `analyse_dts_p.py`, #46 `mark_done_t4.py`, #49 `analyse_t8.py` |
| N/A | **2** | #26 `analyse_t10avf.py`, `THERMAL_K0_runs/analyse.py` |
| **total** | **56** | |

Files I could not classify: **none.** Every refusal site was read in context.

## 3. Disposition of the five CONFLATING files

| file | rung | state of the rung at HEAD `128d48d0` | class | action |
|---|---|---|---|---|
| `mark_done_t4.py` | T4 | closed — **NOT A RESULT ×3** on record (`3def5d39`, `7dcef0bc`; C-119) | **(i)** | NO REPAIR — verdict not reopened; remedy forward-only (chief's -O bound precedent). The `capped` conjunct did not fire on any T4 case (`gate_t4.json` graded all three levels) |
| `mark_done_t11.py` | T11 | closed — **PASS ×3** EXACT tier on record (C-118, `6becf266`); control C-T reported (`b1d91632`) | **(i)** | NO REPAIR — as above; `STATUS.T11_PW_*` carry `capped=`, the conjunct never fired |
| `analyse_t8.py` | T8 | closed — **NOT A RESULT** on record (`docs/campaigns/T-family/T8_VERDICT_2026-08-26.md`) | **(i)** | NO REPAIR — the record stands; a successor T8 registration inherits this finding and must declare the two classes before it freezes |
| `analyse_dts.py` | T1 DTS ladder | closed — `dts.json` on disk, cited by `T1c_RESULTS.md:177` | **(i)** | NO REPAIR |
| `analyse_dts_p.py` | T1 DTS-P ladder | closed — `dts_p.json` on disk, cited by `T1c_RESULTS.md:177` | **(i)** | NO REPAIR |

**Class (ii) — open/PENDING with compute still to be graded: NONE.** The only open rungs in
this territory at HEAD are K0f (instruments #1–#2, CLEAN, solver RUNNING — audited
read-only, nothing amended), T3 `R_ff` (#41, #44, already split per L-342, in progress on
another lane), T5 (#47–#48, CLEAN, lane building), and T4b / T10aR2 (no tracked instrument at
HEAD). **No pre-registered amendment is therefore owed by this audit, and none was written.**

**Class (iii) — instrument of a rung not yet fired: NONE among the CONFLATING five.**

## 4. Forward-only remedy (binding on the next instrument written in this territory)

1. A `mark_done_*.py` that reads `capped=` uses it only to LABEL a non-zero rc
   (CAPPED vs CRASH); its absence with rc=0 is disclosed as `capped: NOT MEASURED` and the
   case proceeds through the physics clauses. `mark_done_t3_rff.py` (#44) is the template.
2. A comparator's completion conjuncts are the rule-4 clauses and nothing else;
   `log.checkMesh` cell counts, `ExecutionTime` seconds, log mtimes, `ranks`, `timeout_s`
   and `core_min` are printed beside the verdict as NOT MEASURED when absent.
3. Every instrument carries a labelled `INFRA = (...)` tuple and a selftest that drives
   both ways under `python3` and `python3 -O` (L-332: no `assert` guards).

ZERO COMPUTE. Nothing sent, filed or posted outside this box (rule 7).
