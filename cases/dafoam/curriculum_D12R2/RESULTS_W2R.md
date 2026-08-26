# D12R2-W2R — PHASE 1 GRADED: `G12R-4` = `NOT A RESULT` AT `W = 900` TOO. THE ITEM CLOSES ON ITS REGISTERED BRANCH, AGENT-FREE, AND THE INSTRUMENT DISCLOSES ONE DEFECT OF ITS OWN

**Written 2026-08-26T22:20:48Z by dafoam lane V2 (fifteenth session) for dafoam-supervisor, `[lab-attributed]`.** Item `D12R2-W2R`; pre-registration `W2R_PREREGISTRATION.md` frozen at **`b168779c`** (v1.0), Addendum 1 **`7aed78af`** (comparator blob `aecceb4e…`, md5 `02a9ab62…`), Addendum 2 **`331d1a2d`** (wait-then-launch wrapper), Addendum 3 **`5d1f89cd`** (agent-independent plan steps). Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady`, stamp `20260826T160035Z_23510`, phase 1 fired **16:00:35Z** (`LAUNCH_RECORD.txt`, permission `bc0e687e`), cpuset 12, 8 g, np=1. **Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7). No frozen file was edited; the comparator is byte-identical to its committed blob (§2).

---

## 1. THE HEADLINE — and it is the registered one

> **`G12R-4` STEP SIZING = `NOT A RESULT`. `h_min = 1.575533e-01` EXCEEDS the registered `h_max = 5.000e-02` by 3.15×. NO ADMISSIBLE FD STEP EXISTS; `step_plan.json` reads `admissible: false`, `steps: []`.** Phase 2 was **NOT LAUNCHED** by the launcher's registered no-admissible-step branch (`d12y_w2r_stage_and_run.sh:919-923`; ledger `NO ADMISSIBLE FD STEP AT THIS WINDOW -- the comparator's registered G12R-4 branch fired. / Phase 2 is NOT LAUNCHED. That is a RESULT, not a failure`). **P3 — the PRIMARY, BINARY prediction — HIT.**

> **ITEM VERDICT: `NOT A RESULT` on `G12R-4`**, the registered result of the registered branch (`W2R_PREREGISTRATION.md` §4, §7; Addendum 3 A3.3: *"That is the registered outcome when P3 HITS, which is this item's primary prediction"*). Phases 2, 3 and 4 launch nothing; the gradient is never FD-verified at this window; `G12R-11` (optimisation authorisation, `PREREGISTRATION.md:277` @ `e6580910`) is never reached, so the optimiser was never authorised. **105.2334 core-min, all 33 registered stages, zero waste.**

**What changes against D12R2 at `W = 300`:** `h_min` falls from 0.1743 to 0.1576 on the frozen path (and to 0.0867 on the disclosed corrected reading, §4) — **still above `h_max`**; the finding upgrades exactly as W2 §1 framed it: not *"cannot cross at `W = 300`"* but *"cannot cross at 3× the window either"*. The next window is W3 (`W3_PREREGISTRATION_DRAFT.md`, on disk, **NOT FROZEN, not at HEAD** — nothing may be launched from it).

## 2. THE FROZEN COMPARATOR, RUN IN ITS GRADING MODE — and the hash first (rule 2)

The registered grading path for this item is the comparator's **`--plan` invocation** (Addendum 3 A3.2: *"the plan step is still the registered grading invocation"*), the same instrument and mode that graded D12R2 phase 1 (`curriculum_D12R2/RESULTS.md` @ `65882eb3`). **There is no run-root copy of `d12y_grade.py`; the file that runs is `cases/dafoam/curriculum_D12R2/d12y_grade.py`**: md5 **`02a9ab62fc26d963886ecd0ee97457ef`** == `git show HEAD:…/d12y_grade.py` == `git show 5d1f89cd:…/d12y_grade.py`, blob **`aecceb4e874eb6d306fb273d7408e762718c87a2`** (Addendum 1 A1.3), asserted by this lane before its run and by `d12y_plan_step.sh` step (4) before the registered run.

**Two runs, one instrument, identical output:**

1. **The registered, agent-independent run** — `W2R_plan_wait` (runner-launched 17:28:37Z, `PLANSTEP.W2R_plan_wait.log`; pid 289431) witnessed `^PHASE1_COMPLETE spent=` (`ledger.txt:149`), asserted the blob, ran `--plan` at **17:46:08Z** with `rc=0 event=COMPARATOR_EXIT` (`STATUS.W2R_plan_wait`), writing `step_plan.json` (md5 **`64cb67dfbcadd5d145d6bd4997102db8`**, echoed into the ledger by the launcher as `STEP_PLAN_MD5=`). **No agent was alive for it** (the fourth fleet kill was ~17:50Z; the third ~17:50Z earlier — the plan step landed inside that gap by the STATUS stamp).
2. **This lane's re-run, 22:12:26Z** — `python3 d12y_grade.py --manifest <root>/manifest.jsonl --root <root> --plan` → **`<root>/W2R_phase1_grade_V2_plan_20260826T221226Z.json`**, exit 0; **`step_plan.json` md5 `64cb67df…` before and after** (byte-identical rewrite; the file's content is the registered artefact, its mtime is not).

**Gate table, verbatim values from that file:**

| gate | verdict | reading |
|---|---|---|
| `G12R-0b` manifest ↔ ledger binding | **PASS** | `n_rows 33`, `n_ledger_stage_lines 33`, `registered 33` — ledger PRESENT, binding measured (Addendum 1's `NOT_MEASURED` limb not exercised) |
| `G12R-0` completion | **PASS** | 33 stages, every row `rc 0`, `oomkilled false`, `end_line_present`, age guard, cold start |
| `G12R-W` where-control | **PASS** | 31 stages witnessed |
| `G12R-1` limit cycle | **PASS** | 2400 samples, `p2p_rel 0.2005483140637519`, `period_steps 18.964426877470355` (`W/P` at 300 = 15.8191; not within 0.05 of a whole number → `delta_window` not cancelled by construction) |
| `G12R-3` `δ_window` | **PASS** | **`1.7958478225974517e-03`** (rel `2.7359804924328014e-03`), 2101 windows, **evaluated at `W = 300`** — §4 |
| `G12R-2` `δ_repeat` | **PASS** | `0.0` over S3_r1/r2/r3 (`0.6576633964036247` ×3, bit-deterministic at np=1) |
| `G12R-3b` `δ_pert` | **PASS** | `1.2227710898568865e-06` |
| `G12R-4` `δ_eff` | **PASS** | `1.7958478225974517e-03`, dominant `delta_window`, nothing excluded by name |
| **`G12R-4` step sizing** | **`NOT A RESULT`** | **`h_min 1.575533e-01` vs `h_max 5.000e-02`; `steps: []`; `admissible: false`** |
| `step_plan.g_component_0` | — | **`1.1398352621255485`** (S5 adjoint, `dobj_dshape[0]`, at `W = 900`) |

`G12R-5`–`G12R-11` are phase 2–4 gates and were never reached (registered: the no-launch branch). No grid family, so rule 5 has no row and **NO GCI IS QUOTED**; `St ≈ 0.53` is a resolution artefact and is never quoted as a Strouhal number (W2R §7).

## 3. PREDICTIONS `P1`–`P4`, SCORED AGAINST `W2R_PREREGISTRATION.md` §4 (cited unchanged from `90edbf27` §3.2) — HIT / MISS, never adjusted

| # | prediction (frozen) | measured | score |
|---|---|---|---|
| **P1** | S2b bit-identical to D12R2's, so `δ_window(900)` reproduces **exactly `9.879556064e-04`** | On the **frozen path** the comparator's `δ_window(300)` = `1.7958478225974517e-03`, equal to D12R2's `1.7958478e-03` to every printed digit (`curriculum_D12R2/RESULTS.md:47`) — the series IS bit-identical; on the **disclosed corrected reading** (§4, the frozen `g3_delta_window` called at `W = 900` on the same series) `δ_window(900)` = **`9.879556064e-04`**, equal to the prediction to all printed digits | **HIT** |
| **P2** | `\|g\|` at `W = 900` = `1.0304158599180422` ± 30 % → `[0.7213, 1.3396]` | **`1.1398352621255485`** (ratio 1.1062 to the `W = 300` value) | **HIT** |
| **P3** | **PRIMARY, BINARY:** `h_min(900) > h_max`, no admissible step; falsified iff `\|g\|` at 900 exceeds 1.9759 | `admissible: false` on the frozen path (`h_min` 0.1576) **and** on the corrected reading (`h_min` 0.0867 > 0.05); `\|g\|` 1.1398 < 1.9759 | **HIT** |
| **P4** | point `h_min(900)` = `9.587931e-02` (1.9176×), band `[7.375e-02, 1.370e-01]` | **frozen path: `1.575533e-01` — OUTSIDE the band → MISS**; corrected reading (§4): `8.667530e-02` — inside the band, 0.904× the point | **MISS on the frozen path; the disclosed corrected value lands in band. NOT re-scored (rule 2): recorded beside, never replacing** |

**The item verdict is invariant to P4's instrument reading**: `h_min` exceeds `h_max` on both readings, so P3 stands and the registered no-launch branch was the right branch either way.

## 4. `W2R-GRADER-DEF-1` — the comparator evaluates `δ_window` at `W = 300` whatever window the launcher ran. POST-COMPUTE DISCLOSURE; NO GATE OR THRESHOLD MOVES; THE FROZEN FILE IS UNTOUCHED

**The defect, by line.** `d12y_grade.py:37` fixes `W_PRIMARY = 300`. In `--plan` mode, `:2013` calls `g3_delta_window(retained, W_PRIMARY, …)`; in `grade_from_manifest`, `:2511` calls `g3_delta_window(retained, man.get("W", W_PRIMARY))` — and the launcher's manifest rows carry **no `W` key** (0 hits in `manifest.jsonl`). The launcher's `W_STEPS = 900` (`d12y_w2r_stage_and_run.sh:137`) reaches the S3/S3b/S5/S7 stages (their `controlDict` `endTime 9.0` = 900 × 0.01) and the S5 adjoint, **but never the comparator**. So the frozen `h_min` on this item mixes `δ_window(300)` with `|g|(900)`. W2R §4 declared the comparator byte-unchanged and cited P1–P4 at `W = 900`: **the registration itself carried the mismatch**, and this lane names it at the registration's expense rather than the instrument's. First disclosed on disk in `docs/capability/dafoam_GRID.md` Correction 1 (lane G; that file's Correction 1 is on disk and not yet at HEAD at this write).

**The disclosure computation** — the frozen module's own functions (`read_series`, `g1_limit_cycle`, `g3_delta_window`, `g4_delta_eff`, `g4_step_sizing`; md5 `02a9ab62…` asserted in the same invocation), called at `W = 900` on `S2b_20260826T160035Z_23510.log` (2400 samples, `TRANSIENT_DISCARD 0`), with `δ_repeat`, `δ_pert` and `g_component_0` read from `step_plan.json`:

| quantity | frozen path (`W = 300`) | corrected reading (`W = 900`) |
|---|---|---|
| `δ_window` | `1.795847823e-03` (rel `2.736e-03`, 2101 windows, 15.819 periods/window) | **`9.879556064e-04`** (rel `1.505e-03`, 1501 windows, 47.457 periods/window, not degenerate) |
| `δ_eff` (dominant) | `1.795847823e-03` (`delta_window`) | `9.879556064e-04` (`delta_window`) |
| `h_min = 100·δ_eff/\|g\|`, `\|g\| = 1.1398352621255485` | **`1.575533e-01`** | **`8.667530e-02`** |
| admissible (`h_max = 0.05`) | **false — `NOT A RESULT`** | **false — `NOT A RESULT`** |

**Consequence, stated exactly:** P3 stands; P4 moves (§3); the item verdict is unchanged; no gate, band, threshold, cap or label is altered; `d12y_grade.py` is not edited. The repair — a `W` carried from the launcher's manifest into the comparator, or `W_PRIMARY` registered per item — belongs to the **W3 registration, before its compute**, and is named there as a precondition of its freeze, not applied here.

## 5. THE LEDGER'S TWO CONTAMINATION LINES — named, not stages

`ledger.txt:46` `PHASE 2 RESUMING: cumulative spend so far 14.4667 core-min (S8: 0.0000)` — the 16:17:27Z premature fire (Addendum 2 A2.1). `ledger.txt:152` `PHASE 2 RESUMING: cumulative spend so far 105.2334 core-min (S8: 0.0000)` — the **registered** phase-2 pass at 17:46:38Z (`W2R_phase2_wait`, `rc=0 event=LAUNCHER_EXIT wall_s=0`; the launcher prints `:247` before its `:919-923` no-launch branch). Neither carries `STAGE=`; `G12R-0b` counted 33 `STAGE=` lines against 33 rows and PASSED. **Both are named here as ledger contamination, not as stages and not as phase-2 events.**

## 6. COST — estimate versus actual (`CLAUDE.md` rule 12), row `C-147`

| | figure |
|---|---|
| predicted (W2R §6, carried from W2 §6 without re-derivation) | **121.35 core-min**, cap 600.0 |
| actual, 33 stages, ledger `SPENT_CORE_MIN=105.2334` | **105.2334 core-min** (sum of the 33 `STAGE=` rows = 105.233; gross = cleaned, no row over 3600 wall s — longest S5 1,570 s) |
| ratio actual/predicted | **0.8672** |
| $ DERIVED at $0.0513/core-h, reported-by-owner, NOT MEASURED | **$0.0900** |
| plan steps and wrappers | **0 core-min** (`W2R_plan_wait` `wall_s=0`; the three still-waiting wrappers hold no core and no container) |
| waste | **none on this item**. W2's 1.2 core-min WASTE (W2R §1, §6) is W2's own figure and is not absorbed here |

**Gap attribution:** the estimate scaled the window stages (S3 + S3b + S5 + S7, D12R2 measured 32.9168) **linearly ×3** to 98.75; the measured `W = 900` stages carry a `W`-independent fixed cost, so they scaled **×2.4–2.6** — S3_r1 1.0667 → 2.8167 (2.64×), S5 10.9 → 26.1667 (2.40×); the `W`-independent groups came in at or under D12R2's (S2b 7.0167 vs 7.0833; S4 envelope 10.1667 vs 13.6833). A misprediction of the scaling law, on the safe side; the next window estimate should be `fixed + slope·W` from these two points, not `×(W/300)`.

## 7. RULING ON THE FOUR STILL-WAITING WRAPPERS, AND ON `held/` — `[lab-attributed]`, agreeing with the supervisor from the registration text

**The four processes** (all `bash`, no container, no core, no memory beyond a shell; every 30 s a line to `STATUS.<case>` and its log in this directory):

| case | pid | START (its own log) | bound | **closes BLOCKED (`rc=6`) no later than** | precondition it waits for | who could write it |
|---|---|---|---|---|---|---|
| `W2R_phase3_wait` | 251172 | 17:16:42Z | 86,400 s | **2026-08-27T17:16:42Z** | `step_plan2.json` | `--plan2`, only after `PHASE2_COMPLETE` — never written on the no-launch branch (`:922` exits before `:934`) |
| `W2R_phase4_wait` | 251492 | 17:17:47Z | 129,600 s | **2026-08-28T05:17:47Z** | `step_plan3.json` | `--plan3`, after `PHASE3_COMPLETE` — never |
| `W2R_plan2_wait` | 290211 | 17:29:42Z | 86,400 s | **2026-08-27T17:29:42Z** | `^PHASE2_COMPLETE` in the ledger | the phase-2 launcher — never |
| `W2R_plan3_wait` | 290739 | 17:30:47Z | 129,600 s | **2026-08-28T05:30:47Z** | `^PHASE3_COMPLETE` | never |

**Ruling: LEAVE THEM; DO NOT KILL.** I agree with the supervisor, and the ground is the registration's own words, not convenience: Addendum 3 A3.3 — *"the no-admissible-step branch exits at `:922` before `:934`, so `PHASE2_COMPLETE` is never written, `plan2` blocks at its bound (rc 6), and phases 3/4 block at theirs — zero compute, every entry closed with a recorded reason. That is the registered outcome when P3 HITS."* Addendum 2 A2.3 — *"A wrapper that reaches its bound writes `rc=6 … verdict=BLOCKED` and launches nothing."* A kill would close each entry with **no** `rc=6` line and **no** `BLOCKED` record — an unregistered close of a registered instrument, and the runner's `launched/` record would then name a process that ended for a reason not on disk. The cost of leaving them is zero core-min (measured: they run no solver); the runner's `ESTIMATE_OVERRUN.txt` notes for them, if written, are infrastructure notes on a wait, not on a run (Addendum 3 A3.4). **Their `rc=6` lines are to be boarded by whoever reads this directory after 2026-08-28T05:30:47Z**; the entries' verdict token is `BLOCKED`, at their bounds, 0 core-min, and that is this item's registered close for phases 2–4.

**`held/`** (`verification/queue/dafoam/held/README.md`, appended by this lane, nothing deleted): `W2R_phase2.json` — already SUPERSEDED by the drop-path `W2R_phase2_wait` (launched 17:15:37Z, closed `rc=0` on the registered no-launch branch 17:46:38Z) — and `D12R_phase3.json` / `D12R_phase4.json` — whose `step_plan*.json` can never be written by any registered grading path (D12R was superseded by D12R2, `e6580910`, C-107) — are **SUPERSEDED BY THE W3 PATH**: the live 2D·unsteady FD line continues, if at all, from `W3_PREREGISTRATION_DRAFT.md` once frozen, with its own entries; none of the three held files is a launch candidate. Held is not cancelled; the files stay as the record of the 16:10–16:17Z premature fires.

## 8. WHAT IS PRESERVED, AND WHAT IS NOT CLAIMED

The run root (33 stage directories and logs, `manifest.jsonl`, `ledger.txt` with its two named contamination lines, `step_plan.json` `64cb67df…`, both grade JSONs, `LAUNCH_RECORD.txt`) is preserved byte-for-byte. **Not claimed:** any Strouhal number; any GCI; any FD-verified gradient at any window; any phase-2/3/4 gate; anything about `W = 900` from the frozen comparator's `δ_window` (which is `W = 300`'s — §4). **Not verified by this lane:** the `rc=6` closes of the four wrappers (they lie in the future and are stated as bounds, not as events).
