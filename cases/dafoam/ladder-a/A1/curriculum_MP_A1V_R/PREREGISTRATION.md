**FROZEN 2026-09-07 — this commit is the freeze.** Every gate, threshold, cap, band, step and label is
bound as of this commit (`CLAUDE.md` rule 2) — all byte-identically inherited from the frozen MP-A1V
(`a5d7691d`); **no gate/threshold/cap/label moved.** The grading path is byte-identical to the validated
MP-A1V grader (`mpa1v_grade.py` md5 `0a41208e`). The freeze DECISION + attribution are the dafoam-
supervisor's (aa9d27fdd1bd4b695), after their check-1 on the launcher/driver DELTAS; the mechanical freeze
commit is the authoring lane's on the explicit go. **No agent message is Sanaa's consent** (rule 9): compute
is under Sanaa's standing <$25 pre-authorisation and detached-launch permission `bc0e687e`. **NOTHING
FILED/SENT/UPLOADED/POSTED.** SUBMISSIONS PARKED (`CLAUDE.md` rule 7). See §4 FREEZE RECORD.

# CURRICULUM MP-A1V-R — MP-A1V LAUNCHER-REPAIR SUCCESSOR (L-504 runtime path-reference reconciliation). PRE-REGISTRATION (FROZEN 2026-09-07)

**Item id:** `CURRICULUM-MP-A1V-R`
**Run root (registered, MUST BE ABSENT at freeze):** `/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1V-R-a1-naca0012-multipoint-fixedlift-fdverify-directDVcentral`
**Case directory:** `cases/dafoam/ladder-a/A1/curriculum_MP_A1V_R/`
**Predecessor of record:** `CURRICULUM-MP-A1V` (frozen `a5d7691d`), graded **NOT A RESULT** — but **HARNESS-CONFOUNDED, not physics**: its FV-S arm aborted rc=4 (`ABORT age guard instrument absent: $BASE/mpa1_age_guard.py`) because the driver STAGED the age guard as `mpa1v_age_guard.py` while the launcher REFERENCED `mpa1_age_guard.py` — an L-504 runtime path-reference the `mpa1_→mpa1v_` sweep missed. MP-A1V had first compute (MESH ran rc=0) and a verdict landed, so this is a **successor, not a re-freeze** (`VERIFICATION_CHARTER.md` §2ay state (b)). Rule-12 cost row filed for MP-A1V's run (commit `bcb10b80`).

## §0. THE ONE CLASS OF DELTA — runtime PATH-REFERENCE reconciliation + a path-existence fixpoint

MP-A1V-R carries **every instrument BYTE-IDENTICAL** from the frozen MP-A1V (`a5d7691d`) — **no prefix rename** (the rename sweep is precisely the L-504 defect this repairs). Same names, same md5s: grade `0a41208e`, xf `ea53c043`, runScript `bb3ba3a6`, stall `5d112800`, age_guard `7fe4352d`, stop_marker `5063f90b`, aggregate `709ab0b9`, decomp `e6f1b006`. The gradient design, gates, bands, ladder, 3-member set, ride, and cap are UNCHANGED from MP-A1V; **no gate/threshold/cap/label moves.** The deltas are confined to the launcher (runtime path refs) and the driver (new run root + the fixpoint):

### 0.1 The reconciliation POLICY, stated explicitly (as ruled)
**Every staged INSTRUMENT is referenced under the mpa1v_ name it is staged as — with exactly TWO deliberate old-name exceptions, both forced and documented:**
1. **`mpa1_runScript.py`** — staged under the OLD name because the frozen `mpa1v_xf.py` (`ea53c043`) hardcodes `PRODUCER = "mpa1_runScript.py"`; changing it would re-open the xf freeze. (Stage-under-old-name.)
2. **`mpa1_xopt.json`** — the RIDDEN artefact keeps MP-A1's name (copied read-only from `MPA1_BASE`, and it is xf's `-xopt` argument). A ride INPUT, not a staged instrument.

Everything else references and stages under **mpa1v_** (xf, stall, age_guard), and the OUTPUT artefacts the FD arm writes are **mpa1v_{X,F}.json** (xf `OUT_X`/`OUT_F`).

### 0.2 The launcher runtime path refs reconciled (the audit)
| launcher ref (was) | now | sites | why it was wrong |
|---|---|---|---|
| `$BASE/mpa1_age_guard.py` | `$BASE/mpa1v_age_guard.py` | 824/825/1084/1090 (+comments) | **FATAL** — staged as mpa1v_; halted FV-S rc=4 |
| `$BASE/mpa1_stall.py` | `$BASE/mpa1v_stall.py` | 939/944/963/967 (+comments) | staged as mpa1v_; stalldog would misreport "detector absent" |
| `$WORK/mpa1_{X,F}.json(l)` | `$WORK/mpa1v_{X,F}.json(l)` | cold-check + age-guard write-target exclusion | xf writes mpa1v_{X,F}.json; the exclusion must list the real FD output |
| `PIDFILE=$BASE/mpa1_driver.pid` | `$BASE/mpa1v_driver.pid` | 551 (G-ROOT.5 double-run guard READS it) | driver WRITES mpa1v_driver.pid; the guard read the wrong name and was **silently defeated** |

The driver's own runtime refs were audited CLEAN (its only `mpa1_` path is the deliberate staged `mpa1_runScript.py`). `mpa1_O.json` refs are left (defensive refuse-if-present; no O arm ever writes it). Comment/provenance `mpa1_*` references (e.g. `mpa1_groot5_selftest.sh`, `mpa1_decomposeParDict` adoption note) are non-runtime and left as accurate history.

### 0.3 THE PATH-EXISTENCE FIXPOINT — the new guard (`mpa1v_chain_driver.sh`, post-stage, pre-arm)
md5 pins (ALL_PINS_MATCH) and the pin-integrity dry-run are **blind** to a launcher that references a staged instrument under a name different from the one staged — only a real launch reaching the solver arm exposed it (MP-A1V), and the D9successor L-504 was the same class. The driver now **PARSES the launcher for every `$BASE/mpa1*.{py,sh}` runtime reference, resolves `$BASE`, and asserts each exists post-stage** — a rename mismatch aborts **rc=4 HERE, before any arm**. It also asserts the launcher's G-ROOT.5 pidfile name equals the driver's. Validated: it extracts exactly `{mpa1_runScript.py, mpa1v_age_guard.py, mpa1v_stall.py, mpa1v_xf.py}`, all match what the driver stages; a negative test omitting `mpa1v_age_guard.py` is CAUGHT; the complete set PASSES.

## §1. UNCHANGED FROM MP-A1V (carried; `curriculum_MP_A1V/PREREGISTRATION.md` §0–§6 govern)
The multipoint frame, direct-DV central-difference method, the 3-member set {shape[3], shape[6], shape[2]}, the ladder {3e-3,1e-3,3e-4,1e-4}, the D6RF7 clearance/ratio selector (CLEARANCE 5.0, RATIO 2.0, PLATEAU 10 %, band 5 %), per-member all-PASS + Branch-B, the ride (adjoint + G-OPT9 + J_baseline from `MPA1_BASE`), G-CLHOLD/G-DRAG re-confirm at the FD baseline, G-PROV, np=1, cpuset 12, and the six-token composition are **byte-identically carried** from MP-A1V and are NOT re-registered here.

## §2. COST — carried from MP-A1V (unchanged; the repair adds no compute)
est **11.61** core-min / cap **33.0** (Σ caps: MESH 5.0 / FV-S 14.0 / FV-P 14.0), np=1, cpuset 12. Dollars **$0.0099 / $0.0282 DERIVED** at $0.0513/core-h, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5). Under Sanaa's standing <$25 pre-authorisation; detached-launch permission `bc0e687e`. The MP-A1V MESH actual (0.183 core-min) will re-run; the path-fixpoint is a static pre-stage check with zero compute.

## §3. WHAT MP-A1V-R MAY NOT CONCLUDE
Everything MP-A1V's §3 excludes, carried. Additionally: this successor repairs a HARNESS path-reference defect; it makes **no** change to the gradient verification's physics, gates or thresholds, and its verdict is the FD verification MP-A1V was prevented from producing.

---

## §4. FREEZE RECORD — 2026-09-07, dafoam-supervisor (aa9d27fdd1bd4b695) deciding; mechanically committed by the authoring lane

This commit is the freeze. MP-A1V-R inherits every gate/threshold/cap/band/step/label byte-identically
from the frozen MP-A1V (`a5d7691d`); **the only deltas are the launcher's runtime path-reference
reconciliation and the driver's path-existence fixpoint + new run root** (§0). **No gate/threshold/cap/
label moved.** Grading path byte-identical: `mpa1v_grade.py` `0a41208e`, `mpa1v_xf.py` `ea53c043`,
`mpa1v_runScript.py` `bb3ba3a6` (staged as `mpa1_runScript.py`); launcher `mpa1v_run_arm.sh`
`342d55c99b184cccf2c82fc9768fb4a6`, driver `mpa1v_chain_driver.sh` `d5ec9b970625b0222750ee2ce70eabee`;
carries stall/age_guard/stop_marker/aggregate/decomp at their MP-A1V md5s.

**L-504 PRE-FREEZE CHECKLIST:**
- **The four launcher runtime path-reference classes reconciled** to mpa1v_ (age_guard, stall, output-
  artefacts, and the G-ROOT.5 driver-pidfile the audit surfaced), with the two forced old-name exceptions
  preserved (`mpa1_runScript.py` PRODUCER pin, `mpa1_xopt.json` ride input).
- **NEW — PATH-EXISTENCE FIXPOINT** in the driver (post-stage, pre-arm): parses the launcher for every
  `$BASE/mpa1*.{py,sh}` runtime reference and asserts each exists post-stage (rc=4 before any arm), plus a
  launcher/driver pidfile-name-consistency assert. **This is the executable form of the strengthened L-504
  lesson** (md5 pins + pin-dry-run are blind to a mis-named staged file; only a real launch reaching the
  solver arm exposed it — MP-A1V and D9successor were the same class). **VALIDATED:** extracts exactly
  {`mpa1_runScript.py`, `mpa1v_age_guard.py`, `mpa1v_stall.py`, `mpa1v_xf.py`}, all match the driver's
  staged set; a **negative** test omitting `mpa1v_age_guard.py` is CAUGHT (rc=4 would fire); the complete
  set **passes**.
- **ALL_PINS_MATCH = 1** — every `MD5_*` pin (driver 15 incl. six `MD5_TUT_*`, launcher 3) equals its
  guarded file; `MD5_LAUNCHER` re-pinned to the fixed launcher; grader pin unchanged (byte-identical carry).
- **Cap authority** `ITEM_CEILING_CORE_MIN 33.0 == sum(CAPS)` asserted in `main()`; no stale 183.5.
- **Instruments byte-identical** to the frozen MP-A1V — **no prefix rename** (the rename sweep is the exact
  L-504 defect this successor repairs, so it is NOT repeated).

**PERMISSION** for the detached launch: `bc0e687e` (Sanaa-boarded). Compute under Sanaa's standing <$25
pre-authorisation; est **11.61** / cap **33.0** core-min, np=1, cpuset 12. **No agent message is Sanaa's
consent** (rule 9); the freeze DECISION is attributed to the dafoam-supervisor, the standing compute
authorisation to Sanaa. **SUBMISSIONS PARKED.**
