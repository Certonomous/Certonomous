# T26 — cost calibration record (mesh ladder)

**What this file is.** The rule-12 estimate-versus-actual comparison for T26's
absolute-Δ₁ **mesh ladder**, filed beside the case so a reader of T26 finds it
without reading the lab-wide ledger or the board.

**Why it exists.** These figures were landed in `docs/COST_CALIBRATION.md` on
2026-09-11 as row **`C-20260911T182921.263721Z-01f499e6`**, and before that they
existed **only in `docs/LAB_STATE.md`**. Both are correct homes and neither is
beside the case. Every other T-family and F14 rung that has produced a cost
comparison keeps one — `T4e_runs/COST_CALIBRATION_ROWS_NOT_LANDED.md`,
`K2d_runs/K2d_COST_CALIBRATION_ROW_PENDING.md`,
`K2f_runs/K2f_THROWAWAY_COST.md` — and T26 did not. **This file closes that
inconsistency; it does not restate a verdict and does not create one.**

**THIS SETTLES NO GATE.** The T26 **rung** is `PENDING` and has never launched a
solver: **zero solver core-minutes have been spent on it.** Everything below is
mesh-build cost.

---

## 1. THE COMPARISON

**Scope: the `L3ABS` rebuild** — third and finest level of the ABS ladder,
divisions 288 × 81, `snappyHexMesh`, **1 rank**, 3,636,801 built cells. For a
mesh ladder, first compute **is** the build.

| channel | figure |
|---|---|
| **PREDICTED** | **45 core-min at 1 rank**, band **43–57**, hard stop **180** |
| **ACTUAL** | **60.067 core-min MEASURED** = `total_wall_s` **3,604** × ranks **1** ÷ 60 |
| **RATIO** | **1.335** (60.067 / 45) — **outside the band, above its upper edge by 5.4 %** |
| against the hard stop | **0.334** — no overrun, no stop |
| **DOLLARS** | predicted **$0.0385**, actual **$0.0514** — **DERIVED, NEVER MEASURED**, at $0.0513/core-h, c7a.4xlarge, reported-by-owner; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **WASTE** | **4.2 core-min, $0.0036 derived** — named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and **never folded into the ratio** |

**The ladder's other two levels, for context and NOT part of the row above:**
`L1ABS` 209 wall s (3.483 core-min), `L2ABS` 844 wall s (14.067 core-min).
Ladder gross across all three = **77.617 core-min**.

**CLEANED — TWO FIGURES, AND THE QUESTION IS REFERRED, NOT RESOLVED.** The build
ran **3,604 wall s** against a 3,600-s clause. Both readings and the measured
consequences of each are set out in
`docs/campaigns/T-family/T4e_T26_STALL_CLAUSE_REFERRAL.md`; **neither is the
answer here either.** In one line: cleaned = gross = **60.067** under a scoped
reading, **0.000** under a literal one, and **a four-second difference in wall
time is what separates them.**

---

## 2. THE MISPREDICTION, OWNED AS TWO NAMED ERRORS

Not "a band miss" — two specific mistakes, both this lane's family's:

1. **The anchor came from a run that died.** The 45 core-min was scaled from the
   **first attempt's** refinement time, measured at box load ≈ 12.8 and therefore
   contention-inflated. **An anchor measured on a run that died under contention
   is not an anchor** — nobody chose those conditions and nothing about them was
   registered.
2. **One ratio was applied to all three `snappyHexMesh` phases when the layer
   phase needed its own.** A `snappyHexMesh` build is not one rate.

**THE CARRYABLE CORRECTION: cost a mesh build PER PHASE.** Measured here, the
layer phase cost **4.65×** its predecessor while refinement cost **2.90×**; no
single scaling factor can be right for both.

---

## 3. THE DECOMPOSITION, FROM MATCHED PHASES ONLY

Read from `log.snappy` of `L2ABS` and `L3ABS` and reproduced independently for
this record rather than copied from the board:

| quantity | L2ABS | L3ABS | ratio |
|---|---:|---:|---:|
| `Layers added in` | 525.57 s | 2442.37 s | **4.6471** |
| layer-addition iterations | 24 | 33 | **1.3750** |
| seconds per layer iteration | 21.899 | 74.011 | **3.3797** |
| `Mesh refined in` | 62.88 s | 182.44 s | **2.9014** |
| layer-candidate cells | 866,840 | 1,905,923 | **2.1987** |

**`1.3750 × 3.3797 = 4.6471` — the product matches the total EXACTLY, so there is
no residual inside the layer phase.** The iterations factor is a property of the
**ladder** and is not contention-producible; the seconds factor is the box and
the problem size. **The layer phase is the entire overrun.**

**AND THE ATTRIBUTION STOPS WHERE THE EVIDENCE STOPS.** Normalising the seconds
channel by layer-candidate cells — **2.1987×, which is a LINEAR-IN-CELLS
ASSUMPTION AND NOT A MEASUREMENT** — leaves **1.5371× UNATTRIBUTED**: contention
and any super-linear algorithmic cost **combined**, which cannot be separated
with the data on disk. **Reported as a residual, not attributed further, and not
called waste.**

**ONE FIGURE THAT DOES NOT RECONCILE, REPORTED RATHER THAN PICKED.** The
snapping-phase ratio computed here as a residual (`Finished meshing in` minus
refinement minus layers: 198.84 → 677.64 s) is **3.4080**; `docs/LAB_STATE.md`
board update 118 records **3.4311**. The 0.7 % difference moves no conclusion —
the layer phase is the overrun on either figure. **The board figure is the one
that does not reconcile and its correction belongs to the board's author, not to
this record**; it is noted here so a future reader meets the discrepancy rather
than inheriting one number silently.

---

## 4. THE WASTE, AND WHY IT IS NAMED AND NOT ABSORBED

**4.2 core-min, $0.0036 derived.** Attempt 1 of `L3ABS` was killed at ≈ 254 wall
s at 1 rank when the **agent session owning the foreground build died**. It left
a **castellated-only** mesh which is **quarantined and must never be graded,
compared or cited as a level of the ladder**. The competing OOM hypothesis was
ruled out by the supervisor's triage — a tiny read-only watcher with no plausible
memory footprint died in the same window, which session death explains and memory
pressure does not.

**The fix was detachment (`setsid`), applied AND fault-injection tested before
the rebuild launched** — not asserted. The rebuild ran at PPID 1 and its own
heartbeat self-reported `ppid=1` to the end.

---

## 5. THE PREDICTION'S PROVENANCE, STATED EXACTLY AND NOT DRESSED UP

**The 45 core-min prediction is NOT a rule-2 pre-registration freeze, and this
record says so rather than letting it wear a pre-registration's clothes.**

- It was committed at **`5122100da`, 2026-09-11T16:29:19Z**.
- The rebuild **launched at 16:26:39Z** — so the prediction is **160 s AFTER
  first compute**, not before it.
- It **finished at 17:26:44Z** — so the prediction is **57.6 minutes BEFORE any
  actual existed**.

**It therefore could not have been back-fitted to the answer, which is the
evidentiary property that matters here — but it is not a freeze, and the two are
not the same thing.** The same board block also pre-registered the *attribution*
of the then-likely under-spend (load had fallen from 12.8 to 5.4 when cfd's
8-rank SUBOFF ended), so a fall in contention would have been recorded as the
reason rather than claimed as a better estimate. It did not fall out that way.

---

## 6. ONE QUESTION SURFACED AND NOT TAKEN

`docs/campaigns/T-family/T26_PREREGISTRATION.md` §7.4 registers the
estimate-versus-actual obligation **for the rung**. The rung has not completed
and no solver has run, so that obligation is **not yet due**. Whether the frozen
pre-registration is nonetheless owed a **dated addendum under standing rule 6**
recording the mesh ladder's calibration — so that a reader of the frozen document
does not leave believing 45 core-min was the outcome — **is a supervisor's call
and is surfaced here, not taken.** The ACTD render pass faced the same question
and it was decided at supervisor level, not by the lane that measured the cost.

---

## 7. PROVENANCE OF EVERY FIGURE

**The primary artifacts are OUTSIDE git** by the lab's large-data policy
(`docs/LOCATIONS.md`, `/home/ubuntu/certonomous-runs/`). They are named here in
full so a reader can re-derive rather than trust:

- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS/BUILD_RC.txt` — `total_wall_s=3604`, `mesh_wall_s=3522`, all five rc zero
- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS/BUILD_STATE.txt` — phase timeline, `FINISHED` and `SHELL_EXIT rc=0`
- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS_HEARTBEAT_SERIES.tsv` — 15-s cadence, progress to the end
- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS/log.snappy` and `.../L2ABS/log.snappy` — every phase timing, the 24 and 33 `Layer addition iteration` counts, the 866,840 / 1,905,923 candidate-cell counts
- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L1ABS.out`, `.../L2ABS.out` — 209 s and 844 s
- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS.attempt1_session_sigterm_midsnap_FAILED/QUARANTINE_NOTE.txt` — the ≈254 s / ≈4.2 core-min waste and the OOM triage
- `/home/ubuntu/certonomous-runs/T26_mesh_dev/L3ABS_BUILT_COUNT_PREDICTION.txt` — the separate, genuinely pre-outcome cell-count prediction (**falsified and reported as falsified**; not a cost figure and not used as one here)

**Committed records:** prediction at `5122100da`; outcome and decomposition at
`a55e482f1` (`docs/LAB_STATE.md` heat-transfer update 118); the ledger row
`C-20260911T182921.263721Z-01f499e6`, landed at `a803f9af7`. Rung registration
`docs/campaigns/T-family/T26_PREREGISTRATION.md`, frozen `691a0961`.

**A limitation stated rather than hidden:** because the run tree is outside git,
**none of the primary artifacts above is protected by HEAD.** If that tree is
cleaned, these figures survive only in this file, in the ledger row and on the
board — which is exactly why this file exists.
