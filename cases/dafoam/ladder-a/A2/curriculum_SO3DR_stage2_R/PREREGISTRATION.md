FROZEN — dafoam-supervisor freeze taken 2026-09-07. Chief cost sign-off received (est 66 / cap 198 core-min). Check-1 (rig diff, grader/sample byte-identity) and the `check_sidecar_before_run.py` ordering guard (PASS both directions) discharged by the supervisor. The freeze commit is this file's committing sha; the launch marker `so3dr_stage2_FREEZE.marker` is placed in this dir. SUBMISSIONS PARKED.

# CURRICULUM SO-3D-R — STAGE 2 · SUCCESSOR "R" (SO3DR-F4 grading-path successor). PRE-REGISTRATION (FROZEN).

**Version 1.0 FROZEN 2026-09-07. Gate, thresholds, cap and labels committed before first compute. Rig md5 pinned `9c1905c0220604946dbd6a8016d5b9de`; grader `2d32ec9b933764b5eb3e3bb61e6657cd`; sample `55bf8e2dcc07fbe3197f2c53421ad019`. After this freeze commit no gate/threshold/cap/label changes — only dated addenda.**

This is the **fresh successor** mandated by verification ruling **V-127** (relayed by the chief): the
frozen Stage-2 grading path is unrepairable in place, so Stage-2 is re-run through a **clean grading
path** built on an ordering-fixed rig. `CLAUDE.md` rule 2: the gate, thresholds, cap and labels below
are committed **before** this successor's first compute. The freeze itself is **NOT taken by this
draft** — it is the dafoam-supervisor's, after check-1 on the rig diff and the ordering check, and the
chief's sign-off on the costed figure.

---

## 0. WHY A FRESH SUCCESSOR, AND WHAT IT DOES AND DOES NOT BUY

**The defect (verified, not re-derived here).** Stage-2 (`../curriculum_SO3DR_stage2/`) ran 36 legs
(**55.27 core-min measured**). The FROZEN rig
(`so3dr_stage2_standalone_runScript.py`, md5 `dc67cced46235f897f6257353402ea57`) writes its
`injected_dv.json` echo-sidecar **AFTER** `prob.run_model()` (frozen rig lines 314–329, run at line
312). On the **32 primal-raised legs** — where DAFoam raises its EXPECTED post-`End`
`AnalysisError("Primal solution failed!")`, which is the **very outcome the experiment counts** — the
write is never reached, the sidecar is absent, and the frozen grader's **F4 echo-check hard-REFUSES
(exit 2)**. Verification RULED this is **NOT** a §2d.1 value-invariant repair (the grader refused;
there is no value to be invariant to, and a diagnostic monkeypatch would drop F4's md5 arm on 32/36
legs). The lawful vehicle is a FRESH SUCCESSOR with a clean grading path.

**What this successor changes — exactly two things, both ordering/packaging, zero physics:**
1. **The rig** (`so3dr_stage2R_standalone_runScript.py`): byte-identical to the frozen Stage-2 rig
   EXCEPT the rank-0 sidecar-echo write is moved to **BEFORE** `prob.run_model()` (after the
   cold-start guard establishes `run_dir_abs`, before `om.Problem()`), so the echo survives the
   primal raise. Every sidecar field was confirmed **input-derived and pre-run knowable** field by
   field (§1.3); the move touches no value, no solver byte, no gate.
2. **The grading path**: the Stage-2 grader logic is **re-frozen byte-identical** into this dir
   (`so3dr_stage2R_grade.py`, md5 `2d32ec9b933764b5eb3e3bb61e6657cd`;
   `so3dr_stage2R_registered_sample.json`, md5 `55bf8e2dcc07fbe3197f2c53421ad019`). **Justification:
   the grader was never the defect.** Its F4 refusal on an absent sidecar was a *correct* refusal
   against a defective rig. The grader is rig-path-agnostic (it takes `--runs-root`), its pins (D6R
   log sha256, sample md5) are unchanged, and it already self-runs `freeze_check` + planted-zero
   (`control_planted_zero`) + F6 (`falsifier_f6_sample`). Copying it gives the successor its **own
   frozen grading path** without editing the parent's frozen files (rule 6). Once the rig writes the
   sidecar before `run_model`, this identical grader reads it and grades.

**What the successor buys, stated honestly.** A **clean F4 record** — the F4 md5/AoA echo arm exercised
on all 36 legs, including the 32 primal-raised legs. It does **NOT** buy a different answer. The gate
G-SA-DISCRIM and its thresholds are **inherited unchanged** from the frozen Stage-2 pre-registration
(frozen before any compute); this successor re-uses them verbatim, so no gate can be accused of being
chosen to fit the answer. The prediction below is a **reproduction expectation**, explicitly labelled.

---

## 1. THE RIG AND THE REGISTERED SAMPLE

### 1.1 The rig
`so3dr_stage2R_standalone_runScript.py`. See the SO3DR-F4 successor stanza in its docstring and the
exact diff vs the frozen parent (returned to the supervisor). One ordering hunk + one provenance
stanza; no other change. The `if MPI.COMM_WORLD.rank == 0` guard is preserved. The NOT_FROZEN
permission gate, the accept-floor guard (primalMinResTol 1e-8 / primalMinResTolDiff 1e3, D6R values,
must not move), the cold-start guard, the D6R-log-sha256 guard and the design-vector parse are all
byte-identical to the frozen parent.

### 1.2 The registered stratified sample
`so3dr_stage2R_registered_sample.json` (md5 `55bf8e2dcc07fbe3197f2c53421ad019`, byte-identical to the
frozen Stage-2 sample): **N = 36 = 24 FAILED-stratum + 12 SUCCEEDED-stratum**, drawn deterministically
from the sha256-pinned D6R log (`394d9f5d…675d`, `SEED 20260907`). F6 recomputes and pins it.

### 1.3 Field-by-field pre-run-knowability of the sidecar (the fix's load-bearing claim)
Every field written to `injected_dv.json` is derived only from argparse input, module constants, or the
design vector parsed from the pinned D6R log **before** `run_model` — **none** depends on `run_model`
output:

| field | source | pre-run knowable? |
|---|---|---|
| `dv_block_line` | `args.dv_block_line` (argparse input) | YES |
| `d6r_log_sha256` | `D6R_LOG_SHA256` (module constant) | YES |
| `patchV_cl04` | `patchv.tolist()` — from `read_design_vector` (called at the line above `run_model`) | YES |
| `aoa_injected` | `float(patchv[1])` — same parse | YES |
| `shape_md5` | md5 of `shape` — same parse | YES |
| `twist_md5` | md5 of `twist` — same parse | YES |
| `shape_n` | `len(shape)` — same parse | YES |
| `twist_n` | `len(twist)` — same parse | YES |
| `primalMinResTol` | `daOptions["primalMinResTol"]` (module constant) | YES |
| `primalMinResTolDiff` | `daOptions["primalMinResTolDiff"]` (module constant) | YES |
| `cold_start` | literal `True` | YES |

**Conclusion: no sidecar field needs a post-run value.** The write-before-run fix is sound and the
alternative ("guard the grader's F4 for the primal-raised leg", the supervisor's call) is NOT needed.

---

## 2. THE GATE — G-SA-DISCRIM (INHERITED UNCHANGED, frozen before any compute)

The gate, thresholds, F3 confound threshold, boundary arithmetic, binomial resolution and the six-token
verdict mapping are **inherited verbatim** from `../curriculum_SO3DR_stage2/PREREGISTRATION.md` §2 and
are re-stated here so this successor is self-contained:

> **G-SA-DISCRIM.** `r_sa` = fraction of the 36 registered standalone legs carrying the
> `Primal solution failed!` banner (over legs completed to rule 4). Six-token verdict; the
> discrimination direction is a SEPARATE `finding`/`discrimination` field:
> - **`r_sa ≥ 50 %` (≥ 18/36) → `GATE REACHED`; HIGH; "cl04's own primal is the pathology; route to D6RF5-class fix".**
> - **`r_sa ≤ 10 %` (≤ 3/36) → `GATE REACHED`; LOW; "multipoint aborted-trial coupling; route to the om.ExecComp code-read".**
> - **`10 % < r_sa < 50 %` (4–17/36) → `NOT A RESULT`; INDETERMINATE.**
> - **A HIGH reading with the SUCCEEDED stratum unstable (F3 confound, `r_succ > 10 %`) → `NOT A RESULT`; HIGH-CONFOUNDED.**
> - **Any leg not completed to rule 4 → `PENDING`** (re-run the incomplete legs; no verdict on a partial run). A control failure or any F-refusal → grader **refuses, exit 2**.

Boundary arithmetic (inclusive): 18/36 = 50.0 % → HIGH; 17/36 = 47.2 % → NOT A RESULT; 3/36 = 8.33 % →
LOW; 4/36 = 11.1 % → NOT A RESULT. RULING 2's bar holds: no `r_sa` and no ratio is a verdict; the 39.7×
is never computed.

**REGISTERED PREDICTION — a REPRODUCTION expectation, labelled as such.** This successor is authored
*after* Stage-2 already ran the identical 36 legs and produced, before the F4 refusal aborted grading,
a **SUCCEEDED-stratum standalone rate `r_succ` = 8/12 = 66.7 % ≫ the 10 % F3 threshold**. Because the
rig fix is ordering-only (no physics changes), the expected successor outcome is the **same F3-borne
finding: `NOT A RESULT` | discrimination `HIGH-CONFOUNDED`.** The gate cannot be accused of fitting
this: it is the frozen Stage-2 gate, unchanged. Written so it can be wrong: if the clean F4 record on
all 36 legs yields `r_succ ≤ 10 %`, the confound is *not* reproduced and the discrimination would then
be read on its merits (LOW / INDETERMINATE / HIGH per the bands) — that would be a genuine surprise and
a finding in its own right. The successor is registered to **reproduce, not manufacture,** the
confounded answer.

**Diagnostic decomposition, NEVER gated.** `r_fail` (over 24 FAILED) and `r_succ` (over 12 SUCCEEDED)
are reported beside `r_sa`; `r_succ` feeds F3. RULING 2's bar preserved.

---

## 3. CONTROLS, COMPLETION, DECOMPOSITION, MEMORY (inherited)

- **§3.1 Planted-zero control (rule 3).** `control_planted_zero` in the re-frozen grader: PLANT-SA-BANNER
  (honest reader must move +1; a blinded reader that cannot see the banner must be caught) and
  PLANT-SA-DECOY (a non-banner "failed" line must NOT be counted). Refuses (exit 2) if the reader cannot
  see a planted banner. Unchanged from Stage-2.
- **§3.2 Strict completion + age guard (rule 4), per leg.** `rc=0`, `End`, last time == `endTime` (1000),
  primal fields present (`U p T nut alphat nuTilda phi`), every `endTime` field newer than the leg's own
  `0/`. A DAFoam post-`End` acceptance refusal (the banner) IS a completed primal and IS the failure
  `r_sa` counts; an infra kill is not a banner (§3.3).
- **§3.3 Infrastructure vs physics.** OOM / watchdog / container kill / cost stop → stopped-by-that-cause,
  NOT A RESULT about convergence, never a banner; re-run once under a repair note.
- **§3.4 Decomposition.** `np = 4`, method scotch, the D6R/D6RF4 A2-wing system unchanged; all 36 legs
  identical `np` so per-leg cost is comparable to the D6RF4 measured basis and to the Stage-2 actual.
- **§3.5 Memory.** Primal only, no adjoint / no `compute_totals` / no `run_driver`; predicted peak well
  under the 20 GiB cgroup (~5–8 GiB). A memory stop → stopped-by-memory, NOT A RESULT, never a banner.

---

## 4. FALSIFIERS (inherited verbatim — F1…F6)

F1 banner-blind reader (PLANT-SA-BANNER, Δ ≠ +1 → REFUSE); F2 over-count (per-leg count ∉ {0,1} →
REFUSE); **F3 rig confound** (`r_succ > 10 %` AND `r_sa ≥ 50 %` → HIGH downgraded to NOT A RESULT — the
arm this successor expects to fire); **F4 wrong design injected** (leg log AoA vs registered `|Δ| ≤ 1e-6`
AND injected shape[96]+twist[7] md5 vs the D6R block md5 → mismatch REFUSES that leg) — **this is the
arm that hard-refused on the 32 absent sidecars in Stage-2; the fix makes the sidecar present on every
leg so F4 grades instead of aborting**; F5 indeterminate-band honesty; F6 sample tampering (recomputed
sample md5 ≠ `55bf8e2d…` → REFUSE).

**New pre-freeze guard for THIS class (L-504 clause-c).** Before the supervisor's freeze, the rig is
gated by `scripts/check_sidecar_before_run.py`, a static AST check that REFUSES (exit 3) if a
sidecar-echo write's source line is after a run-trigger line. It PASSES on this successor rig (echo
write line 352 ≤ run line 359) and REFUSES on the frozen parent rig (write 328 after run 312) — both
directions demonstrated on the real files. This turns the write-after-run defect (4th occurrence this
session: D6RF5, D6RF6, D9successor, SO3DR-F4) into an enforced invariant.

---

## 5. COST (`CLAUDE.md` rule 12) — CORE-MINUTES, ANCHORED TO THE STAGE-2 MEASURED ACTUAL

**Basis: the MEASURED Stage-2 actual, not the stale flat estimate.** The parent prereg's flat
`36 × 5.4 = 195 core-min` over-predicted: Stage-2 actually spent **55.27 core-min** for the identical 36
legs, because 32 legs hit the `Primal solution failed!` banner and cut back early (~1.4 core-min each)
while only 4 ran a full converged primal. The successor runs the **identical** 36 legs with an
ordering-only rig fix (zero solver-time impact), so the Stage-2 actual is the correct predictive basis.

| field | value |
|---|---|
| unit | **core-minutes** = wall s × ranks ÷ 60 |
| Stage-2 MEASURED actual (basis) | **55.27 core-min** for 36 legs at `np = 4` (blended per-leg ≈ 1.53 core-min) |
| composition (predictive model) | 32 banner legs ≈ 1.4 core-min + 4 converged full-primal legs ≈ 5.4 core-min gross → **≈ 66 core-min** |
| **point estimate** | **≈ 66 core-min** [PREDICTION] — the composition upper form; **above** the 55.27 measured actual (ratio 66/55.27 ≈ 1.19) to leave honest margin |
| **cap (family MAX form)** | max(3.0 × 66, 1.25 × (4/3) × 66) = max(**198**, 110) = **198 core-min** |
| **stop rule** | at 198 core-min the campaign **stops**; an overrun gets no new budget. A leg whose wall exceeds ~3× the converged per-leg envelope (> ~16 core-min) or 3600 wall s (rule-12 stall) is stopped and recorded, not absorbed |
| solver core-min | the whole estimate IS solver time (36 real primals); not a host-only reader |
| dollars | **DERIVED, NOT MEASURED, REPORTED-BY-OWNER** at $0.0513/core-h (`COMPUTE_BUDGET_CHARTER.md` §5): estimate 66 core-min = 1.10 core-h → **$0.056**; cap 198 core-min = 3.30 core-h → **$0.169**. **Both far under $25.** |
| pre-authorisation | under $25, inside the standing pre-authorisation; a blanket is not a per-item read (rule 9) — costed here on its own terms |
| rule-12 calibration | on completion, predicted (66) vs measured (ratio + attribution) as a row in `docs/COST_CALIBRATION.md`, naming the Stage-2 measured 55.27 row as the basis it continues. (A concurrent dafoam lane owns that ledger this session; do not co-edit.) A completion report without this comparison is incomplete |

---

## 6. WHAT THIS SUCCESSOR MAY NOT CONCLUDE

It may not compute, quote or reconstruct the 39.7× (RULING 2's bar). It may not treat a clean F4 record
as a *new* answer — the finding it reproduces is the Stage-2 F3-borne confound. It may not conclude a
D6RF5-class primal fix is warranted (a HIGH reading is expected to be CONFOUNDED, not clean). It grades
nothing until the supervisor's freeze places the marker; SUBMISSIONS PARKED.

---

## 7. GRADING PATH AND FROZEN ARTIFACT NAMES (to be fixed at the supervisor's freeze)

| file | role | freeze state |
|---|---|---|
| `so3dr_stage2R_standalone_runScript.py` | the ordering-fixed standalone single-point rig | **FROZEN**; md5 `9c1905c0220604946dbd6a8016d5b9de` (pinned at freeze) |
| `so3dr_stage2R_grade.py` | the banner reader / `r_sa` grader + F1–F6 controls (byte-identical re-freeze) | **FROZEN**; md5 `2d32ec9b933764b5eb3e3bb61e6657cd` (unchanged from Stage-2) |
| `so3dr_stage2R_registered_sample.json` | the registered 24+12 stratified sample (byte-identical) | **FROZEN**; md5 `55bf8e2dcc07fbe3197f2c53421ad019` (unchanged) |
| `scripts/check_sidecar_before_run.py` | pre-freeze ordering guard (L-504 clause-c) | pre-freeze instrument; selftest green |

**Freeze pre-conditions (the supervisor's, per L-504):** (a) fixpoint every md5/threshold constant to a
real file; (b) validate by a real end-to-end launch that reaches the solver arm; (c) run
`scripts/check_sidecar_before_run.py` on the rig and require PASS; (d) reconcile the cap (registered
source here = this prereg literal 66 / cap 198 + the launcher assertion, no cap constant in the grader).

---

## 8. FREEZE STATEMENT — TAKEN 2026-09-07 (dafoam-supervisor)

**FROZEN.** The dafoam-supervisor takes this freeze after discharging, personally:
(a) check-1 on the rig diff vs the frozen parent — exactly two ordering/packaging changes, value-invariant
(all 11 sidecar fields input-derived, §1.3); (b) grader and sample byte-identity confirmed against disk
(grader md5 `2d32ec9b`, sample md5 `55bf8e2d`); (c) the `check_sidecar_before_run.py` ordering guard run
both directions on the REAL rigs — PASS on this successor (write line 352 ≤ run line 359), REFUSE exit 3 on
the frozen parent (write 328 after run 312), selftest OK; (d) confirmed `freeze_check` pins the grader's own
instruments + F6 sample + D6R sha256 (NOT the rig md5), so the byte-identical grader is lawful. The chief's
cost sign-off (est 66 / cap 198 core-min, $0.056 / $0.169 derived) is received. The rig md5
`9c1905c0220604946dbd6a8016d5b9de` is pinned in §7. The launch marker `so3dr_stage2_FREEZE.marker` is placed
in this dir at freeze. Grading runs the frozen `so3dr_stage2R_grade.py` WITHOUT `--skip-freeze` so
`freeze_check` + planted-zero + F6 self-run. SUBMISSIONS PARKED.
