# F27-WOMERSLEY NUMERICS SUCCESSOR — RE-REGISTRATION R2 (COST-CAP CORRECTION)

> **AUTHORISED — 2026-09-07.**
> The cfd supervisor took both non-delegable checks: check 4 (pre-registration
> committed before compute; gates/thresholds/bands byte-identical to the frozen
> parent) and check 1 (both R2 instruments read as diffs). This document is FROZEN
> at its own commit; the grading path is pinned here (rule 2).
> **FREEZE STAMP (2026-09-07):** grading path pinned to R2 grader git blob
> `706f4a4df5143b7fda6b821c321acba5564ea1fd` and R2 driver git blob
> `2105b6ccbb71da1959e589714c47e36603ffa125`. No solver was run in preparing this draft.

---

## 0. WHAT THIS IS, AND WHAT IT IS NOT

This is a **compute-budget cap correction** re-registration of the F27 numerics
successor. It **corrects ONLY the hard compute cap** so the full 3-level Roache
triple can complete; it changes **no gate, no threshold and no band**. The cap is a
**compute budget, not a gate** — a run stops when it crosses the cap (rule 12) — so
raising the cap of a **NEW, pre-compute run** to reflect the **measured** fine-level
cost is legal and is **not** gate-widening. Correcting a misprediction is not
answer-fitting.

**Frozen parent (rule 6, body never edited):**
`verification/campaign/F27_NUMERICS_SUCCESSOR_PREREGISTRATION.md`, freeze commit
`b86fe0cc` (verified present in this repository). This R2 re-registration is a
**separate document with its own commit**; the parent is cited, not rewritten.

**Chief ruling authorising this re-registration (recorded here, not a freeze):** the
F27 fine level projected 526.8 core-min against the frozen 500 cap and HALTED
lawfully (rule 12 forbids an in-flight raise). Re-registering a NEW run pre-compute
with a cap that reflects the measured fine cost is legal — the cap is a compute
budget, not a gate. GATES / THRESHOLDS / BANDS stay byte-identical. Fine resolution
is **NOT** reduced (that would break the r = 2 refinement ratio and void the Roache
triple). Projected cost ~542 core-min ≈ $0.46, under $25 — no Sanaa decision needed
beyond the standing pre-authorisation (rule 12), and this cap is still costed here.

---

## 1. WHAT HALTED, MEASURED (the anchor for the corrected cap)

The frozen-cap (500 core-min) run of the successor produced two **strictly complete**
levels and a lawful projected halt at the fine level, recorded in
`verification/runs/F27_NUMERICS_SUCCESSOR_runs/CAP_BREACH`:

| level | cells | cell-steps | rc | `End` | ClockTime | core-min (ClockTime × 4 ÷ 60) |
|---|---|---|---|---|---|---|
| coarse | 3,840 | 2,580,480 | 0 | yes | 11 s | 0.7333 |
| medium | 30,720 | 41,287,680 | 0 | yes | 214 s | 14.2667 |
| **coarse + medium measured** | | | | | | **15.0000** |
| fine | 245,760 | 660,602,880 | — | HALTED pre-spend | — | **526.7893 (PROJECTED)** |
| **total projected** | | | | | | **541.7893** |

**The misprediction being corrected.** The frozen parent §5 estimated the fine level
at ~360 core-min using an assumed medium→fine per-cell-step growth of ~1.4×. The
run **measured** the medium rate at **20.733 core-µs/cell-step** (ClockTime 214 s ×
4 ranks ÷ 41,287,680 cell-steps) and carried it forward by the frozen growth factor
**2.3078** to a fine rate **47.8462 core-µs/cell-step**, giving fine =
47.8462 µs × 660,602,880 cell-steps ÷ 60 = **526.79 core-min**. The ~2.3× per-cell-step
growth of the changed (limited-scheme, 3-corrector) numerics was **under-predicted**
at freeze; that is the sole cause of the halt. The physics, the ladder (r = 2 in h
and dt), and every gate are unchanged.

Completion of coarse and medium confirmed on disk: rc = 0, one `End` line each,
ClockTime present.

---

## 2. THE GATES, THRESHOLDS AND BANDS — BYTE-IDENTICAL TO THE FROZEN PARENT

Carried over **byte-identically** from the frozen parent §3. They are not re-typed
here from prose: they are **produced by the SAME grading instrument**
(`grade_f27_successor.py`, git blob `07206330`, **unchanged since the parent freeze**)
reading the **SAME shared model** (`exact_f27.py`, imported unchanged) — so they
**cannot** differ by construction.

| gate | quantity | band (IEEE double literals) | reference |
|---|---|---|---|
| G-F27R-1 | `E2_velocity_locked_phase` | `[6.052738753361828e-05, 0.001513184688340457]` | 0.0 |
| G-F27R-2 | `Einf_axial_velocity_locked_phase` | `[0.00011397841172247245, 0.002849460293061811]` | 0.0 |

`BAND_FACTOR = 5.0` (unchanged). Rule 5 applies in full: a non-CONVERGING triple is
**NOT A RESULT**; a CONVERGING triple inside the band is **PASS**, else **GATE FAIL**;
no GCI on a non-monotone triple. Four reported-not-gated channels unchanged:
`R-F27-W_bulk_mean_axial_velocity`, `R-F27-E_perp_spurious_cross_flow`,
`R-F27-A_z_axial_non_uniformity`, `R-F27-A_theta_azimuthal_non_uniformity`. The
periodicity and both uniformity limbs are unchanged.

**BYTE-IDENTICAL ASSERTION (executed 2026-09-07, no solver).** The band literals the
unchanged grader emits from `bands()` were compared field-for-field against the
frozen parent §3 literals:

- G-F27R-1: re-reg `[6.052738753361828e-05, 0.001513184688340457]` == parent → **True**
- G-F27R-2: re-reg `[0.00011397841172247245, 0.002849460293061811]` == parent → **True**
- **BYTE-IDENTICAL BANDS ASSERTION: PASS.**

Any non-identical gate/threshold/band would be a stop-and-report; none is non-identical.
**Fine resolution is NOT reduced**: cell counts 3,840 / 30,720 / 245,760 and dt halving
are byte-identical to the parent, preserving r = 2 and the Roache triple.

---

## 3. THE CORRECTED CAP — the ONLY quantity that changes

**Corrected hard cap = 625 core-min.**

Basis, stated explicitly:

- measured coarse + medium (from `CAP_BREACH`, ClockTime × 4 ÷ 60) = **15.0000** core-min
- projected fine (measured medium rate × frozen growth 2.3078) = **526.7893** core-min
- total projection = 15.0000 + 526.7893 = **541.7893** core-min
- × **1.15** stated safety margin = **623.0577** core-min
- rounded up to the nearest 5 = **625 core-min**

**Why 1.15×, and why bounded.** The fine figure is an extrapolation of a measured
medium rate by a fixed growth factor. Its risk is (i) ClockTime integer-second
quantisation (±0.5 s × 4 ÷ 60 = ±0.033 core-min/level, negligible) and (ii) the same
class of growth-factor misprediction that caused this halt (assumed 1.4×, measured
2.3078×) recurring at medium→fine. A 1.15× margin gives **83.21 core-min of headroom
(15.4% over the projection)** — enough to absorb a further modest under-projection
without being a blank cheque. The margin is stated and bounded; an overrun of **625**
still **STOPS the run** (rule 12), it does not get a new budget.

**Dollars (DERIVED, NOT MEASURED).** 625 core-min = 10.416667 core-h × $0.0513/core-h
= **$0.5344** — derived at the reported-by-owner c7a.4xlarge rate; the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation
ceiling. A calibration row is owed at completion (`docs/COST_CALIBRATION.md`), since
this run exists precisely to correct a tracked misprediction.

---

## 4. GRADING PATH — the VERDICT instrument is REUSED UNCHANGED

The grading (verdict) instrument is the frozen successor grader
`cases/F27_WOMERSLEY_PIPE/successor_numerics/grade_f27_successor.py`:

- **sha256** `53f748006c6acfa7c28123077a338d12434831641fad609e0ce3e9d997aeb0b4`
- **git blob** `07206330eb1fc8001912c193b2ed3ec307a26685` — **== HEAD:<path>** (verified;
  the grader is already committed and unchanged).

Every band, `BAND_FACTOR`, gate, rule-4/rule-5 gating, planted-zero control and reader
in this grader is **byte-identical to the frozen parent** and is **cap-independent**:
`CAP_CORE_MIN` in the grader is read **only** by `cost_claim()` and the printed/JSON
cost report (lines 539, 1159, 1179, 1202) and enters **no** verdict, band, or rule-4/5
gate. The verdict is produced solely by `grade_one` → `RT.grade_ladder` from `bands()`.
The driver **hashes the grader on disk against its committed git blob at grade time**
(rule 2); the grading path is fixed at **this R2 re-registration's commit**. Grading is
zero-new-compute after the solves.

**R2-B INSTRUMENT PAIR BUILT AND CITED (additive, 2026-09-07 — no gate/threshold/cap/label
change; DRAFT, still NOT AUTHORISED).** Per the supervisor's check-4 ruling selecting
**R2-B** (§6), the parallel new-file instrument pair was built by copying the frozen
instruments (rule 6: the frozen files are NEVER edited). The verdict instrument that
will grade the R2 run is the **R2 grader**:
`cases/F27_WOMERSLEY_PIPE/successor_numerics/grade_f27_successor_r2.py` — git blob
`706f4a4df5143b7fda6b821c321acba5564ea1fd`, sha256
`83b9b483d55a55e06f2e2eb0b47829031c5996b922023ab639244d9ae651c277`. It is byte-identical
to the frozen successor grader (blob `07206330`, sha256 `53f74800…`) **except the single
line** `CAP_CORE_MIN = 500.0` → `625.0` (line 128) — a reported-budget constant read only
by `cost_claim()` and the cost print/JSON, entering **no** band, gate or rule-4/5 verdict.
This blob/sha is what the supervisor pins at the R2 freeze.

---

## 5. RUN APPROACH — RECOMMENDATION AND CONFIRMED-ABSENT TARGET

Two approaches were assessed.

**(A) RESUME-FINE-ONLY** — reuse the strictly-complete coarse + medium in the existing
root `verification/runs/F27_NUMERICS_SUCCESSOR_runs`, run only fine. Least waste
(~15 core-min saved). **NOT RECOMMENDED.** The frozen driver cannot do this without
LOGIC surgery:
- Its **run-root guard** (`run_f27_successor.sh:263–269`) REFUSES with exit 3 if the run
  root already exists — the existing root exists.
- Its level loop (`:301`) drives **all three** levels and calls `refuse_if_answered`
  (`:308`) at each; coarse and medium already hold `0/` and processor directories, so
  the loop would REFUSE at coarse.
- The completed coarse + medium each already passed their own age guard at their
  original run (fields newer than that level's `0/U`); they remain valid graded
  artifacts, but re-driving them is what the guards refuse.
- The fine target under the existing root holds only `box_before.txt` (no `0/`, no time
  or processor directory), so it would not itself trip `refuse_if_answered` — but this
  is moot because the run-root guard refuses first.
Skipping completed levels would require editing the frozen driver's run-root guard and
its per-level loop — a **measurement/infrastructure LOGIC change** (check-1), higher
risk, and it splits the triple across two runs with two age-guard datums.

**(B) FRESH FULL 3-LEVEL RE-RUN in a NEW root — RECOMMENDED.** One coherent invocation
produces all three levels with a single age-guard lineage and the cleanest Roache
triple integrity (Sanaa's triple gating reads a coherent 3-level ladder). Versus the
frozen driver, the **only** differences are the run-root path and the cap value — both
**config**, no LOGIC change. Waste is re-spending ~15 core-min on coarse + medium
(≈$0.013 derived), trivially inside the 625 cap (15.0 + 526.79 = 541.79 < 625). The
physics config is byte-identical to the frozen parent (same successor
`fvSchemes`/`fvSolution` — the three registered levers — and the frozen parent `case/`
for every unchanged dictionary; builder `build_f27_successor.py` reused unchanged).

- **Declared R2 run root:** `verification/runs/F27_NUMERICS_SUCCESSOR_R2_runs` —
  **confirmed ABSENT** on disk 2026-09-07 (rule-2 absence condition holds; the driver's
  run-root guard passes).
- **Fine target** `verification/runs/F27_NUMERICS_SUCCESSOR_R2_runs/fine` — ABSENT
  (the whole R2 root is absent).

---

## 6. INSTRUMENT PATH — the cap coupling the supervisor must rule on (check-4 / check-1)

The corrected cap (625) is the **load-bearing halt budget** and lives in the **driver**
(`run_f27_successor.sh:69`, `CAP_CORE_MIN=500`) and its run-root (`:64`). The driver
additionally **asserts driver-cap == grader-cap** at `:168–171` (it greps the grader's
`CAP_CORE_MIN` and refuses if they differ). Therefore **reusing the grader unchanged
(cap 500) AND raising the driver's halt cap to 625 are mutually exclusive under the
frozen driver's own consistency assertion** — a driver at 625 against a grader at 500
ABORTS at `:170`. This is the one point that needs a supervisor ruling; the bands are
untouched, so this is not a gate issue. Two resolutions, classified:

**R2-A (literal grader reuse).** Keep the grader unchanged (cap 500); new driver at
625 with the cap-consistency check `:168–171` **relaxed/removed**. Downsides: relaxing
that check is a **driver LOGIC change** (check-1), and the grader would then **report
"cap 500" while the real budget is 625** — a rule-12 cap-honesty defect in the cost
report. **Not preferred.**

**R2-B (parallel instrument pair — RECOMMENDED).** Mirror exactly how the frozen parent
instruments were preserved when this successor set was built: create **new files**,
never editing the frozen ones.
- **New grader** `grade_f27_successor_r2.py` — byte-identical to the frozen successor
  grader **except the single line** `CAP_CORE_MIN = 500.0` → `625.0`. This touches a
  **reported budget constant only**; every band, `BAND_FACTOR`, gate, rule-4/5, planted
  control and reader is byte-identical, and the verdict path is cap-independent — so
  **check-1 confirms a one-line diff on a non-verdict field** and **check-4 treats it as
  a config-value change**.
- **New driver** `run_f27_successor_r2.sh` — byte-identical to the frozen successor
  driver **except** `CAP_CORE_MIN=625` (config value), `RUN_ROOT=…/F27_NUMERICS_SUCCESSOR_R2_runs`
  (config path), and `GRADER`/`GRADER_REL` pointing at the R2 grader. The
  cost-accounting, `proj_f27.py` projection, cap-consistency check and halt LOGIC stay
  **byte-identical** (both caps now 625).
- The frozen successor grader (sha256 `53f74800…` / blob `07206330`) and driver
  (sha256 `43555a43…`) and builder (sha256 `fa3b4d5d…`) are **NEVER edited**.

R2-B keeps **all driver LOGIC byte-identical** (the driver constraint), keeps **all
grader VERDICT logic byte-identical**, corrects **only** a reported budget constant and
the run-root path, makes the reported cap **honest** (rule 12), and edits **no frozen
file**. It is recommended over R2-A. Honest caveat: R2-B departs from the literal
instruction to reuse the exact grader **file**; it instead reuses the grader's verdict
logic byte-identically and bumps one non-verdict constant. Standing up this parallel
pair is the class of act the frozen parent §4 note reserved to a supervisor/chief
direction, so **it is left for the supervisor at check-4**; the diffs above are exact
enough that a lane can create both files in minutes on that direction. Until then the
grading path cited in §4 is the **verdict authority** (unchanged); the R2-B grader would
carry a new blob to be pinned at the R2 freeze commit.

**R2-B PAIR BUILT (additive, 2026-09-07; DRAFT, NOT AUTHORISED — banner unchanged).** Both
new files now exist on disk, copied from the frozen instruments (rule 6 — frozen files
never edited); no gate/threshold/cap/label changed by this build:

- **R2 grader** `cases/F27_WOMERSLEY_PIPE/successor_numerics/grade_f27_successor_r2.py`
  — git blob `706f4a4df5143b7fda6b821c321acba5564ea1fd`, sha256
  `83b9b483d55a55e06f2e2eb0b47829031c5996b922023ab639244d9ae651c277`. Diff vs the frozen
  grader is **one hunk, one line**: `CAP_CORE_MIN = 500.0` → `625.0` (line 128).
- **R2 driver** `cases/F27_WOMERSLEY_PIPE/successor_numerics/run_f27_successor_r2.sh`
  — sha256 `a025c48fbd4cf7c29b42f43502cb0bc277d834c5ce8b17c36dd1a08de5e03e5c`. Diff vs the
  frozen driver is the **four config lines only** — `CAP_CORE_MIN=500`→`625` (:69),
  `RUN_ROOT`→`…/F27_NUMERICS_SUCCESSOR_R2_runs` (:64), `GRADER`/`GRADER_REL`→the R2 grader
  (:61/:67); **no logic line changed** (cost-accounting, `proj_f27.py` projection, the
  cap-consistency check :168–171, the run-root guard, `refuse_if_answered`, the rc-inside-
  wrapper and halt logic all byte-identical).
- **Checks (no solver):** the driver cap-consistency check (:168–171) now compares grader
  `625.0` vs driver `625` → **MATCH**; R2 grader `--selftest` rc 0 (planted control fires,
  16 controls green), `-O` rc 2 (refusal armed); R2 driver `bash -n` clean,
  `--selftest-projector` rc 0.
- **Frozen originals unedited:** grader blob `07206330` / sha256 `53f74800…`, driver
  sha256 `43555a43…`, builder `build_f27_successor.py` sha256 `fa3b4d5d…` (reused unchanged).

**CHECK-1 FIX APPLIED TO THE R2 DRIVER (additive, 2026-09-07; DRAFT, NOT AUTHORISED —
banner unchanged; no gate/threshold/cap/label change).** The cfd supervisor's check-1
on the R2-B instrument pair found ONE functional defect in the R2 driver, now fixed
(the frozen parent `run_f27_successor.sh` / `grade_f27_successor.py` were NOT touched;
rule 6):

- **`--detach` self-reference (functional).** `run_f27_successor_r2.sh:277`
  `ME="$HERE/run_f27_successor.sh"` → `ME="$HERE/run_f27_successor_r2.sh"`. Without it a
  `--detach` launch of the R2 driver would re-exec the FROZEN PARENT (cap 500, parent
  run root) instead of itself. This is a config SELF-PATH correction — the same class
  as the `:61`/`:64`/`:67` pointers — not an accounting/guard/halt/projection/rule-2
  logic change.
- **STATUS-note honesty (string literals only, zero logic).** The two STATUS-note
  strings at `:99` and `:279` reading
  `note=exit-status-of-run_f27_successor.sh-NOT-the-solver-rc` now embed
  `run_f27_successor_r2.sh`, so the STATUS file the R2 run writes honestly names the R2
  driver. Note strings only; no logic touched.

Diff vs the frozen driver is now **seven lines**: the four original config lines
(`:61` grader ptr, `:64` run-root, `:67` grader-rel, `:69` cap 625) plus `:277` (ME
self-path, config-path) plus `:99`/`:279` (note-string script name). **Zero changes**
to cost-accounting, the `proj_f27.py` projection call, the cap-consistency check
(`:168–171`), the run-root guard, `refuse_if_answered`, the rc-inside-wrapper, the halt
logic, or the rule-2 blob-hash block. Re-checks, no solver: R2 grader `--selftest`
rc 0 and `-O --selftest` rc 2; R2 driver `bash -n` rc 0 and `--selftest-projector` rc 0.

- **R2 driver (post-fix)** `cases/F27_WOMERSLEY_PIPE/successor_numerics/run_f27_successor_r2.sh`
  — git blob `2105b6ccbb71da1959e589714c47e36603ffa125`, sha256
  `d016f2ca975dd3414d79ac505bf2c84f90d64cfffd64239905234fd7c3b84854`. This **supersedes**
  the pre-fix driver sha256 `a025c48f…` recorded above.
- **R2 grader UNCHANGED by this fix** — git blob `706f4a4df5143b7fda6b821c321acba5564ea1fd`,
  sha256 `83b9b483d55a55e06f2e2eb0b47829031c5996b922023ab639244d9ae651c277` (as above).

These blobs/shas are what the supervisor pins at the R2 freeze commit (the R2 driver
blob is now `2105b6cc…`). The supervisor re-takes check-1 on the diff; this lane
neither authorises nor launches.

---

## 7. WHAT THIS RE-REGISTRATION DOES AND DOES NOT DO

- **Does:** correct the hard compute cap 500 → 625 core-min on a NEW pre-compute run,
  with the basis and derived dollars stated; declare a fresh absent R2 run root;
  reuse the verdict instrument and all gates/thresholds/bands byte-identically.
- **Does not:** change any gate, threshold, band, `BAND_FACTOR`, reference, ladder,
  refinement ratio, physics dictionary or reported-not-gated channel; reduce fine
  resolution; authorise or launch anything.

**Nothing is sent, filed, uploaded, registered or posted (rule 7). Draft handed to the
cfd supervisor for check 4 (and check 1 on the R2-B instrument diffs). Banner stays
NOT AUTHORISED until then.**
