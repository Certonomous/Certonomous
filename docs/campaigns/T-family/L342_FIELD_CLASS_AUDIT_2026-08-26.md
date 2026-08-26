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

---

## 5. SECOND PASS — 2026-08-26T22:08Z: the thirteen instruments frozen AFTER `6812b444`

**Lines whose number changed above this section: 0.** Appended to a copy of the
HEAD blob (the worktree copy was verified byte-identical to HEAD before the
append, L-223 shape). Section 1's class table (PHYSICS-CRITICAL vs
INFRASTRUCTURE) is carried unchanged and is the rule applied below.

**Scope.** The first pass closed at `6812b444` (2026-08-26T16:35:13Z). Every
grading instrument this team has frozen **since** that commit is read here, plus
the two K0f instruments the first pass could only audit read-only, plus the one
new launcher. Blobs were hashed on disk with `git hash-object` at the audit and
are printed so a later reader can prove which bytes were read.

**The L-342 question, asked of every row:** *can an ABSENT INFRASTRUCTURE field
refuse a grade or produce a NOT A RESULT?* The rule is that it must not.

### 5.1 Table

| # | file | blob (hashed on disk at this audit) | frozen at | PHYSICS-CRITICAL fields it gates on | INFRASTRUCTURE fields it touches | can an ABSENT infra field refuse / force NOT A RESULT? | verdict |
|---|---|---|---|---|---|---|---|
| 57 | `T-family/T13_runs/analyse_t13.py` | `127ae6d3` | `0d2dc150` 20:55Z | `DONE.<case>` existence for all three levels (l.425 — "the whole rung is graded or none of it is"); `T13_registered.json` present and its floors EQUAL the imported `roache_triple` (l.86, l.90); case identity `Ra_L = 100` recomputed from the case files (l.145); `TRef` = antisymmetry point (l.148); `Ny` even and ≥ 10 N (l.150); single-block `blockMeshDict` form (l.127); ≥ 2 written times (l.439); latest time == `endTime` (l.441); field present and NON-UNIFORM at `endTime` (l.182, l.187); structural `internalField` location (l.188); cell count == mesh (l.219); `C_ORDER` hot-to-cold linear profile (l.451); planted-zero both arms (l.348, l.371, l.375) | none — no STATUS field is opened by this file. The only `capped=` string in it is a selftest fixture it *writes* (l.578) | **NO** — the file never reads a STATUS key, so no infrastructure absence has a path to a refusal | **CLEAN** |
| 58 | `T-family/T13_runs/mark_done_t13.py` | `02f43ea7` | `0d2dc150` 20:55Z | `STATUS.<case>` EXISTENCE (l.72 — "an absent STATUS is not inferred from an End line (K0d L1)"); integer `rc=` (l.78); `rc == 0`; `log.solve` present; `End`; last time == `endTime`; `ExecutionTime` count == `endTime`; registered fields present at `endTime`; the age guard against the case's own `0/T` | `INFRA = ("wall_s","timeout_s","ranks","core_min","capped","checkmesh_rc","solver","solver_path","note","started_utc","ended_utc")` (l.49) | **NO** — l.80 `not_measured = [k for k in INFRA if k not in d]` is a *report* returned beside the failures, never a failure. `capped` is read only through `st.get()` (l.94) and only to LABEL an already-non-zero `rc` (CAPPED vs CRASH, l.96/l.100); absent it appends "capped witness NOT MEASURED, cap-stop vs crash undetermined" (l.103) to a label that a non-zero `rc` had already earned. Driven: selftest arm l.214 *"every infrastructure field absent (incl. capped) -> still DONE, NOT MEASURED disclosed"*, expected exit 0 with the marker written | **CLEAN** — this is the `mark_done_t3_rff.py` template correctly applied; the header (l.16–21) names the T11/T4 CONFLATING form and states it is not repeated |
| 59 | `T-family/T14_runs/analyse_t14.py` | `386181db` | `5a870e54` 21:05Z | `DONE.<case>` for all three levels (l.239); `T14_registered.json` present and floors EQUAL the import (l.54, l.58); `CASE.txt` per level (l.66); value count == registered `N*N` (l.88); levels agree on `Bi`/`Fo_end` (l.245); `valueFraction == Bi/(Bi+2N)` (l.247, L-341); case files agree with registered physics (l.249); ladder is `r = 2` (l.253); a time directory beyond 0 (l.260); `T` readable (l.269 — "a missing number is not a zero"); derived reference == registered (l.291); planted-zero both arms (l.155–183) | none. The header states it in terms (l.15): *"(STATUS wall_s, capped, timeout_s, checkmesh_rc ...) are never read here"* | **NO.** The `f_CT` temporal-bias control is the model case: absent `DONE.<CT_CASE>` prints *"C-T temporal-bias control: NOT RUN — REPORTED as absent, never gated"* (l.309–317) and the graded rows proceed | **CLEAN** |
| 60 | `T-family/T14_runs/mark_done_t14.py` | `680eddd3` | `5a870e54` 21:05Z | as #58: STATUS existence (l.58), integer `rc` (l.62), `rc == 0`, `log.solve`, `End`, last time == `endTime`, `ExecutionTime` count, fields at `endTime`, age guard vs `0/T` | `INFRA` tuple l.35 (same eleven keys) | **NO** — l.73–75 collects the missing keys into `notes` with the literal text *"INFRASTRUCTURE fields NOT MEASURED (L-342, reported, not refused)"*; `notes` never enters `fails`. `capped` labels a non-zero `rc` only (l.78–84) and prints `NOT MEASURED` when absent. Driven: selftest l.195 *"all INFRASTRUCTURE fields absent -> DONE with NOTE (L-342)"*, `EXIT_OK` | **CLEAN** |
| 61 | `T-family/T9aR1b_runs/analyse_t9aR1b.py` | `fd6c43a0` | `3c39d08d` 21:18Z | `DONE.<case>` for all three levels (l.233); registered floors EQUAL the import (l.53, l.57); the exact plane-wall derivation agrees with T9a's registered `T_i1` and `q` to 1e-6 (l.67, l.69 — a referent cross-check, driven in the selftest at l.331 with a 1 mK plant); `CASE.txt` (l.76); a time directory beyond 0 (l.117); `T`/`DT` readable (l.121); cell count == registered layer counts (l.124); the `C_MAP` layer-conductivity map (l.128); `cells_per_layer` == registered (l.240); `CASE.txt` and `fvSchemes` on disk both record the HARMONIC scheme (l.242, l.245 — the whole point of the rung); planted-zero both arms (l.165, l.187, l.189) | none — no STATUS key is opened; header l.24 declares refusals are PHYSICS-CRITICAL only | **NO** | **CLEAN** |
| 62 | `T-family/T9aR1b_runs/mark_done_t9aR1b.py` | `68c78731` | `3c39d08d` 21:18Z | as #60 | `INFRA` tuple l.35 | **NO** — identical construction to #60; selftest l.196 drives the all-infra-absent arm to `EXIT_OK` | **CLEAN** |
| 63 | `T-family/T4b_runs/analyse_t4b.py` | `69abe6e5` | `91614764` 17:20Z | `DONE.<case>` all levels (l.478); registered `roache_floors` EQUAL `scripts/roache_triple.py` (l.78, exit 2 at l.80); a time directory beyond 0 (l.485); three independent control readers each return something on every level (l.522); sampling at each registered `r/D` (l.574, l.534); **three planted-zero controls with a BLIND comparator beside each** — y+ (l.356–372, incl. l.358 requiring the blind generic-`postProcess` path to return exactly 0), exit-line (l.394–432, plant AIMED at a located cell), flux (l.448–459) | none | **NO** | **CLEAN** |
| 64 | `T-family/T4b_runs/mark_done_t4b.py` | `d5411c3f` | `91614764` 17:20Z | as #58 | `INFRA` tuple l.53 | **NO** — l.84 `not_measured`; `capped` via `st.get()` at l.98 labels a non-zero `rc` only (l.100/l.104/l.107). Driven: selftest l.217, exit 0. Header l.21–25 names the T11/T4 CONFLATING precedent explicitly and states `capped` is NOT a conjunct | **CLEAN** |
| 65 | `T-family/T10aR2_runs/analyse_t10aR2.py` | `a252463b` | `fb4bf7e2` 17:20Z | `DONE.<case>` own three levels (l.259) **and** the frozen T10a levels (l.262) **and** the frozen T10a-R twin `2LI_f` (l.264) — three separate completion certificates, all physics; registered floors EQUAL `scripts/roache_triple.py` (l.108) and registered `Fs`/`r` EQUAL the frozen module (l.111); the frozen `analyse_t1c.gci` floor is `STAGNANT_FLOOR` (l.256); the exact theory agrees with itself (l.266); **iterative convergence per level before any triple is formed (l.280, D440)**; the planted-zero control (l.282); `R2_f` and `R_q` present the same patch order (l.306) | none | **NO** | **CLEAN** |
| 66 | `T-family/T10aR2_runs/mark_done_t10aR2.py` | `4fbff6a7` | `fb4bf7e2` 17:20Z | as #58 | `INFRA` tuple l.53 | **NO** — construction identical to #64 (same file lineage); selftest l.217 drives the all-infra-absent arm to exit 0 | **CLEAN** |
| 67 | `scripts/analyse_k0f.py` (= first-pass row #2) | `764dedc6` | `e7022828` **03:24Z — BEFORE `6812b444`** | ten `DONE` (l.1551); case dir (l.1682); `boundaryField` readable (l.687–692); spec / derivation | none | **NO** | **CLEAN — carried forward unchanged.** The on-disk blob `764dedc6` is byte-identical to the blob `K0f_PREREGISTRATION.md` §7.7 registers, so the file the first pass read is the file in force; no re-audit was owed and none of its bytes moved |
| 68 | `scripts/mark_done_k0f.py` (= first-pass row #1) | `f01e3fce` | `e7022828` **03:24Z — BEFORE `6812b444`** | STATUS EXISTENCE (exit 2, l.149); STATUS `rc ≠ 0`; `End`; last time; per-closure fields; `ExecutionTime` count; age guard; the clause-7 launch guard. For an EXTENDED case (AMENDMENT 3): `STATUS.<case>.ext1` rc, `log.solve.ext1`, a `STATUS.<case>.ext2` FAILS the case, last time == `endTime + 20000`, 60 000 `ExecutionTime` lines over both logs, first extension `Time = 40001`, age datums `0/T` **and** `STATUS.<case>` | `wall=` and `checkMesh_rc=` appear in the STATUS format but are parsed only through `\brc=(\d+)` (l.152) and are never required | **NO** | **CLEAN — carried forward unchanged**, blob matches §7.7 |
| 69 | `scripts/launch_k0f_ext1.sh` | `49ad67c0` | `c18ab05f` 21:11Z (registered at K0f AMENDMENT 3 §A3.3) | **This is a LAUNCHER, not a grader — it writes no verdict and cannot produce a NOT A RESULT.** Its pre-write refusals are: `--ranks ≠ 1` (l.61, the registered SERIAL form); no `log.solve` (l.66); no `STATUS.<case>` (l.67) or one not `rc=0` (l.68) — the *in-wrapper solver rc*, PHYSICS-CRITICAL by section 1's table; no `40000/` checkpoint (l.72); no `0/T` age datum (l.73); `controlDict` `endTime` ≠ 40000 or `stopAt` ≠ `endTime` (l.75, l.76); a time directory beyond 40 000 (l.77); G2 lineage-aware foreign process (l.96); unresolvable solver (l.121); failed `build_k0f.py --preflight` (l.123); every `controlDict` copy-edit grep post-checked with the snapshot restored on failure (l.128–131) | it WRITES `timeout_s= ranks= solver= solver_path= note= segment= restart_from= endTime_ext= controldict_restored= started_utc= ended_utc=` and hardcodes `checkMesh_rc=na` (l.105–112); it READS none of them back | **NO.** Two authorisation refusals — an existing `STATUS.<case>.ext1` (l.69), `.ext2` (l.70) or `log.solve.ext1` (l.71) — are gated on file EXISTENCE, and they refuse **to start a second extension §7.1 does not authorise**; they are one-way (a *present* file refuses, an *absent* one proceeds), so no ABSENCE can refuse anything | **CLEAN** |

### 5.2 Counts, second pass

| verdict | count | files |
|---|---|---|
| CLEAN | **13** | rows 57–69 |
| CONFLATING | **0** | — |
| N/A | **0** | — |

**Running total over both passes: 69 numbered rows + 1 name-adjacent = 70;
CLEAN 62, CONFLATING 5 (all first-pass, all class (i), all closed), N/A 2.**

Files I could not classify: **none.** Every refusal site in all thirteen files
was read in context, not by grep alone.

### 5.3 Amendments owed by this pass: NONE

The forward-only remedy §4 laid down is **met in full** by every instrument
frozen since it was written:

1. **Item 1 (`capped` labels, never voids).** All five new `mark_done_*.py`
   read `capped` through `.get()` and only to separate CAPPED from CRASH on an
   already-non-zero `rc`; four of the five (#58, #64, #66 and their headers)
   name the T11/T4 CONFLATING finding by name and state they do not repeat it.
2. **Item 2 (completion conjuncts are rule-4 clauses and nothing else).** No new
   instrument makes `log.checkMesh` cell counts, `ExecutionTime` seconds, log
   mtimes, `ranks`, `timeout_s` or `core_min` a conjunct. The `analyse_t8.py`
   failure mode — `act = float(st["core_min"])` raising an uncaught `KeyError`
   after the verdicts print and losing the exit code — **does not recur**: none
   of the five new comparators opens a STATUS file at all.
3. **Item 3 (labelled `INFRA` tuple + a selftest that drives both ways under
   `python3` and `python3 -O`).** All five new `mark_done_*.py` carry a named
   `INFRA` tuple and an explicit all-infrastructure-absent selftest arm asserting
   **DONE**; the five new comparators carry `--selftest` arms driving each
   refusal under both interpreters and carry **no `assert` statement** (L-332).

**No `<script>.L342_PROPOSED.py` and no `.diff` was written, because no
amendment is owed.** Proposing a change to a CLEAN frozen instrument would move
a grading-path blob for nothing, which §7.7-style freezes exist to prevent.

### 5.4 One finding recorded, outside the L-342 field-class question

`verification/runs/T-family/T5_runs/digitise_t5.py` is in T5's §16.9 FREEZE SET
at blob `e55d6208c511`. HEAD carries `e55d6208`; the **worktree copy on disk
hashes `ea789ea6`** and `git diff HEAD --numstat` reports **+929 / −1 lines**.
The frozen bytes are intact at HEAD and no T5 grade reads the digitiser today,
so nothing is refused by it — but a freeze-set file whose worktree copy is 929
lines ahead of its registered blob is somebody's uncommitted work sitting on a
frozen path. **Inspected, not reverted** (rule 10). Reported to the supervisor
for a landing decision; recorded here so the next reader of the freeze set is
not surprised by a hash mismatch against the on-disk file.

ZERO COMPUTE in this pass. Nothing sent, filed or posted outside this box (rule 7).
