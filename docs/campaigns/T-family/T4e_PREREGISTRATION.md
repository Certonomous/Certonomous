# T4e — impinging round jet, H/D = 2, Re = 23 000: the fine-convergence DISCRIMINATOR successor of T4d, with a robust D1 EARLY-TERMINATION design — pre-registration (FROZEN v1.0)

> **STATUS AT THIS COMMIT: FROZEN v1.0, BEFORE ANY SOLVER HAS ITERATED ON ANY `T4e_IJ_*` CASE.**
> NOT BUILT. NOT ENQUEUED. NOT LAUNCHED. **Zero solver core-minutes have been spent on this rung**
> (the run dir `verification/runs/T-family/T4e_runs/` holds only the six frozen instruments — no `0/`
> dir, no numeric time dir, no `STATUS`/`log`/`DONE` marker; confirmed age-guard-style at the freeze).
>
> **The grading path is fixed by sha in §12 below** (the six-file freeze set + the frozen imported
> members, computed with `git hash-object` on the exact committed files; the frozen comparator prints
> its own `sha256_of()` provenance at runtime, so the file that ran can be hashed against the pinned
> blob). The heat-transfer supervisor's non-delegable §3 checks are complete (2026-09-08, incl. an
> independent re-run of `trajectory_t4e.py --controls` confirming ARM A fires and the ARM S2 noisy-decay
> hole is closed): `analyse_t4e.py` / `mark_done_t4e.py` / `launch_t4e.sh` are pure renames (proven by
> forward reproduction, §8), `build_t4e.py`'s five `system_files()` changes are guarded, and
> `trajectory_t4e.py`'s two-arm + two-decay-arm planted control is green under both interpreters.
> Changes remain legal ONLY as dated addenda that cannot alter a gate, threshold, cap or label
> (CLAUDE.md rule 2: gates close at first compute; none has run). **The build (`blockMesh`/`checkMesh`
> birth certificate) and the queue entries remain WITHHELD** — launch is HELD for box capacity (§9), a
> chief-endorsed freeze-now / hold-launch. Nothing here authorises a launch or a send (CLAUDE.md rule 7:
> SUBMISSIONS REMAIN PARKED).

**Predecessor: T4d** (`docs/campaigns/T-family/T4d_PREREGISTRATION.md`; grade record
`docs/campaigns/T-family/T4d_RESULTS.md`, committed `73e008dc`). T4d graded **`NOT A RESULT`** (whole
rung, 2026-09-08). Coarse (C6.3 1.4e-6) and medium (3.38966e-6) cleared the 2e-4 tol, but the **FINE**
level reached endTime 64000 **CLEAN yet NOT field-converged**: C6.3 **0.01518 ≈ 76× the 2e-4 tol**, and
all three Roache radial triples non-CONVERGING (G1 OSCILLATORY, G2/G3 DIVERGENT, all fine values below
band, no GCI). The frozen T4d record (§6) leaves the discriminator **OPEN**: a still-decaying transient
(→ larger endTime) vs physical unsteadiness at Re = 23 000 (→ transient/URANS). **T4e's job is to MEASURE
which**, on the fine C6.3 trajectory, and to stop the moment the answer is robust. Chain
**T4 → T4b → T4c → T4d → T4e**.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.**

---

## 0. What T4e changes against T4d, and what it does NOT

**T4e carries over BYTE-INVARIANT the entire T4d physics/design/gate/band/threshold/reference/prediction
set** — every BC, scheme, mesh (nrj = 3N/2, 8 640 / 34 560 / 138 240 cells), relaxation (0.6), the graded
stations G1/G2/G3 with their bands and references, controls C1–C6 **including the C6.3 = 2e-4 tol**, the
Roache floors, and predictions P1–P9. The reference value is re-read from the held ERCOFTAC file at every
run. **No band, threshold, floor, reference or prediction is widened, moved or loosened** (T25 discipline).

**The FOUR registered changes vs T4d, all named** (`T4e_registered.json` `registered_change_vs_T4d`):

1. **FINE `endTime` 64000 → 160000** (coarse **30000** and medium **60000** UNCHANGED). Re-run all three
   levels **FRESH** into new `T4e_IJ_{c,m,f}` case directories — the rule-4 age guard bars re-using a T4d
   time directory (a guard refuses a case where `0` or a time dir already exists), and one consistent T4e
   registration grading all three against the same frozen path is cleaner than mixing rungs.
2. **`purgeWrite` 2 → 0** (all levels), so **every** written checkpoint survives — the fine C6.3 sliding
   window (§3a) needs all 40 fine checkpoints; with `purgeWrite 2` only the last two survive and no
   trajectory could be built.
3. **`runTimeModifiable` false → true** (all levels), so the D1 clean-stop trigger (§3a) can rewrite
   `controlDict stopAt` at runtime. This enables a runtime-readable controlDict and changes **no** band,
   threshold, floor, reference or prediction.
4. **The cost table is re-computed** for the 160000 fine window, with the D1 early-termination
   best/expected/hard-cap structure (§9).

`build_t4e.py` is `build_t4d.py` + these; `analyse_t4e.py` / `mark_done_t4e.py` / `launch_t4e.sh` are
**pure renames** (§8, §12). `trajectory_t4e.py` is the ONE new instrument (§3a).

## 1. The case — inherited from T4d §1 (and thus T4b §1) UNCHANGED

Normally-impinging round air jet from a fully developed pipe (recycling `mapped` inlet), H/D = 2,
Re_D = 23 000, D = 0.02 m, ν = 1.5e-05 m²/s, U_bulk = 17.25 m/s, Pr/Pr_t = 0.71/0.85, plate at 1000 W/m²,
jet 293.15 K; `buoyantBoussinesqSimpleFoam` (β = 0, passive T), `kOmegaSST`, steady, axisymmetric 2.5°
wedge, wall-resolved on every level. All BCs / `transportProperties` / `turbulenceProperties` / `g` /
`fvSchemes` are the frozen `build_t4.fields()` / `constant_files()` / `system_files()` output, called
unchanged. Reference: ERCOFTAC Classic Collection case025 `ij2lr`, HELD at
`docs/campaigns/T-family/reference-data/ercoftac_case025/`, re-read at every run.

## 2. Why the fine endTime goes to 160000, and why coarse/medium do not move

The T4d **fine** C6.3 = 0.01518 at 64000 is the whole reason for the successor. Two hypotheses, both
consistent with a clean-but-unconverged fine field:
- **still-decaying transient** (the finer T4e mesh + relaxation-0.6 settle more slowly than T4b's ρ ≈ 0.44
  per 4000-it basis) → a larger endTime clears it (this is the D2/D3 world);
- **physical unsteadiness** at Re = 23 000 — the fine mesh resolves an intrinsically unsteady impinging-jet
  structure that a steady solver renders as a sustained residual/field limit cycle → **no** steady endTime
  clears it (this is the D1 world; the remedy is a transient/URANS successor, §3c).

**160000 = 2.5× the T4d fine window**, sized to give the fine C6.3 trajectory enough checkpoints (40 at
`writeInterval` 4000) to hold a full W = 15 sliding window (§3a) **clear of the initial transient** and so
DISCRIMINATE D1 from D2/D3. **Coarse (30000) and medium (60000) already cleared 2e-4 in T4d** (1.4e-6,
3.39e-6) — they need no more window and are re-run fresh only to sit under one consistent T4e registration.
The C6.3 tol (2e-4) and the `writeInterval` window (4000) are UNCHANGED, so C6.3 measures the identical
per-checkpoint quantity it measured in T4d.

## 3a. THE EARLY-TERMINATION DESIGN (CLAUDE.md rule 12 efficiency)

At the T4d-measured rate the fine leg to the 160000 hard cap is **~50 h (~2 d) single-rank** (§9; ~20 h at
the earliest legal confirmation). Once the answer (D1) is robustly measured, running the remaining time is
waste. So the fine leg **terminates cleanly** on robust D1 confirmation.

**The measured trajectory.** `trajectory_t4e.py` reads, at each written fine checkpoint k, the SAME C6.3
quantity control C6.3 grades:
`C6.3(k) = max over G1/G2/G3 of | peak(U/U_bulk) at k − peak at k−1 |`, through the **FROZEN**
`analyse_t4.sample_profile` / `analyse_t4.peak_of` (imported, never re-implemented). The trajectory is the
series `{(iteration_k, C6.3(k))}`.

**The robust-confirmation threshold (registered VERBATIM, prediction-first; the supervisor set it, and
REVISED cond1 at the §3 review to close the false-D1 hole — `T4e_registered.json`
`early_termination_D1.robust_confirmation_threshold_VERBATIM`):**

> D1 is ROBUSTLY CONFIRMED (=> clean early terminate of the fine leg) when ALL THREE hold over a sliding
> window of the most recent **W = 15** consecutive fine-level checkpoints (= 60,000 iters), evaluated only
> once **iteration >= 64,000** (past the initial transient):
> (1) **NON-DECAY / OSCILLATION-DOMINATES-TREND:** the OLS slope of ln(C6.3) vs iteration corresponds to a
> per-checkpoint decay ratio **rho_fit >= 0.95** (fast-decay backstop; a genuine transient shows rho <=
> ~0.81), AND the net trend the OLS **linear** fit of C6.3 vs iteration explains across the window
> (**net_trend_drop = |slope| × (iter_last − iter_first)**) is **<= 0.5 × the detrended peak-to-peak swing**
> (**ptp_detrended = max(resid) − min(resid)**) — i.e. the oscillation swing is at least 2× the net drift.
> A limit cycle has ~zero net trend << oscillation and passes; a monotone OR noisy decay has the trend
> dominating and fails. *(The former endpoint clause window-last >= 0.85 × window-first is DEPRECATED: it
> false-rejects a limit cycle caught in an unlucky phase and admits a noisy slow decay at rho 0.95–0.99.)*
> (2) **BOUNDED WELL ABOVE TOL:** window-mean C6.3 >= **1e-3** (5× the 2e-4 tol), AND
> window-max/window-min <= **5**.
> (3) **OSCILLATORY (limit cycle, not a stall):** the detrended C6.3 series has >= **4** sign changes
> (>= 2 full oscillation periods) within the window.
> endTime **160,000** remains the HARD cap: if D1 is never robustly confirmed by 160,000, the outcome is
> **D2** (if C6.3 cleared 2e-4 → grade the full triple) or **D3** (decaying-not-cleared → continuation rung).

Fire rule = cond1 **AND** cond2 **AND** cond3. `rho_fit = exp(OLS_slope_of_ln_C63_vs_iteration ×
writeInterval)`; the detrend is the residual of an OLS **linear** fit of C6.3 vs iteration over the window.

**The clean stop.** On confirmation the instrument rewrites the fine `system/controlDict`
`stopAt endTime` → `stopAt writeNow` (`runTimeModifiable true`). OpenFOAM re-reads controlDict at the next
time step, **writes the current fields and stops with a clean `End` line**. It is **NOT a kill** — a killed
solver leaves no End line and half-written fields. The instrument refuses to arm the stop unless
`runTimeModifiable true` is present (else the rewrite would silently do nothing) and unless exactly one
`stopAt endTime` line is found. **The D1 marker is written by the instrument** (never inferred):
`D1_CONFIRMED_TERMINATE.T4e_IJ_f` in the run root, recording the confirmation iteration and the full
trajectory evidence, clearly distinguished from an accidental timeout cap.

## 3b. COMPLETION SEMANTICS (early-stop never masquerades as a rule-4 completion)

- **D1 branch:** the fine level is **deliberately** terminated at the robust-confirmation iteration.
  `last time == endTime` is **NOT claimed and NOT needed** — D1 is a **NON-CONVERGENCE finding** whose
  deliverable is the measured limit-cycle trajectory, not a converged field. Verdict **`NOT A RESULT`
  (unsteadiness)**, **DISCHARGED** by routing to the transient/URANS successor (§3c). In this branch
  `mark_done_t4e.py` will (correctly) report the fine **NOT DONE** (last < endTime), and `analyse_t4e.py`
  will (correctly) **refuse** to grade the full triple — there is no converged fine field to grade; the D1
  finding is reported from the marker + the trajectory.
- **D2 / D3 branches:** these **DO** need a completed/converged fine field. They require reaching the
  registered endTime 160000 (D2) or the D3 continuation rung, graded by the strict-completion instrument
  `mark_done_t4e.py` **+** the Roache triple in `analyse_t4e.py`. **The strict completion rule (CLAUDE.md
  rule 4: rc = 0, an `End` line, last == endTime, fields `T U p_rgh alphat nut k omega phi` present and
  NEWER than `0/T`, ExecutionTime count == endTime) and the age guard are UNCHANGED** in
  `mark_done_t4e.py` (a pure rename of `mark_done_t4d.py`).

**Invariant:** rule 4 governs ONLY D2/D3; D1 is a separately-marked non-convergence finding. The D1 marker
`D1_CONFIRMED_TERMINATE` is distinct from any DONE marker and from a timeout cap.

## 3c. THE D1 → TRANSIENT/URANS ROUTE (a SEPARATE downstream rung, FLAGGED — never a silent swap)

If D1 is robustly confirmed, the finding is a **measured capability statement** (steady RANS renders an
intrinsically unsteady jet as a limit cycle), **not** a terminal capability-gap filing. It is discharged by
a **separately registered** transient/URANS successor rung. **T4e's registered solver stays
`buoyantBoussinesqSimpleFoam` (steady) on every level** — the transient solver is never silently swapped in.
Chief ENDORSED this route (2026-09-08) as a separate downstream rung (§2ay state-b route).

## 4. Controls — carried over from T4d UNCHANGED, byte-identical readers

`analyse_t4e.py` imports the frozen `analyse_t4.py` unchanged; no reader, threshold, band, floor, gate order
or planted control is touched (§8). C1/C1b plate & pipe-wall y+ < 1.0 (with the y+ scaling control and the
blind generic reader beside it); C2 nozzle-exit U_c/U_bulk within ±3% of 1.2245; C3 mass conservation
|Σφ|/|φ_in| < 1e-3; **C4 planted-zero controls, both arms, on EVERY grading-path reader** (frozen
`analyse_t4.planted_zero_control`); C5 strict completion + age guard (`mark_done_t4e.py`); C6.1/C6.2/C6.3
iterative convergence with the **unchanged 2e-4** C6.3 tol; Roache floors `STAGNANT_FLOOR = 0.5`,
`P_MIN = 0.05` imported by name. Graded rows G1 r/D = 1.0 band [1.069, 1.109]; G2 r/D = 2.0 band
[0.7688, 0.8088]; G3 r/D = 3.0 band [0.4432, 0.4832]. Nu rows remain REPORT-ONLY / **BLOCKED** (T4 §2.1).

**A second, NEW planted control (rule 3) on `trajectory_t4e.py`.** Because that instrument BOTH measures
AND controls the run (it triggers the stop), a reader not shown able to BOTH see D1 AND reject decay is not
evidence. It carries a **two-arm + two-decay-arm (ARM S monotone, ARM S2 noisy)** planted control on its NEW logic — the windowed classifier
(the frozen physics read `sample_profile`/`peak_of` is already plant-controlled inside C4):
- **ARM A** — a synthetic sustained limit cycle → the confirmation **MUST FIRE**;
- **ARM B** — a synthetic decaying series at rho ≤ 0.81 → **MUST NOT** fire;
- **ARM S** — a synthetic monotone slow decay at rho ≈ 0.99 → **MUST NOT** fire;
- **ARM S2** — a synthetic **NOISY** slow decay at rho ≈ 0.97 with a superimposed oscillation large enough
  to give ≥ 4 detrended sign-changes → **MUST NOT** fire (this is the exact false-D1 hole the §3 review
  closed: cond2 and cond3 both pass, so only the new cond1 trend-vs-oscillation clause can reject it);
plus gate arms (iteration < 64000; fewer than W checkpoints) that must not fire, and a determinism arm.
**Measured (self-test, both `python3` and `python3 -O`, all green):** ARM A fires (cond1/2/3 all True;
rho_fit 0.9949, net_trend 1.396e-4 ≤ 0.5×ptp 9.949e-4, mean 2.00e-3, max/min 1.64, sign-changes 9); ARM B
does not (cond1 False: rho_fit 0.81 < 0.95 and net_trend 4.285e-3 > 0.5×ptp 1.751e-3; cond2 False; cond3
False); **ARM S** does not (**cond1 False**: net_trend 3.937e-4 >> 0.5×ptp 6.974e-6 — the monotone drift
dominates; cond3 False); **ARM S2** does not (**cond1 False**: net_trend 1.095e-3 > 0.5×ptp 4.101e-4 — the
decay trend dominates the noise; **cond2 True, cond3 True, sign-changes 8** — so cond1 is the ONLY clause
rejecting it, which is the point). The trend-vs-oscillation cond1 replaces the deprecated endpoint clause
(§8a).

## 5. THE EVIDENCE — the T4d measured fine result (why the discriminator exists)

Read-only from the T4d grade (`T4d_RESULTS.md`, committed `73e008dc`; `T4e_registered.json`
`convergence_evidence_from_T4d`): coarse C6.3 **1.4e-6**, medium **3.38966e-6** (both cleared 2e-4); fine
C6.3 at 64000 **0.01518 (~76× tol)**, triples G1 (1.0778,1.0825,1.0591) OSCILLATORY, G2
(0.8265,0.8173,0.6615) DIVERGENT, G3 (0.5490,0.5409,0.4403) DIVERGENT, no GCI. The T4b decay basis
(ρ ≈ 0.44 per 4000-it, fine transient cleared by ~40000–64000; `convergence_evidence_from_T4b`) sizes the
expected D1 confirmation window (§9).

## 6. Predictions — carried over from T4d UNCHANGED (P1–P9, byte-invariant in `T4e_registered.json`)

P1–P9 are copied from T4d verbatim; none is loosened. The prediction-first **loss modes** are now
operationalised into the registered decision structure: **P6** (fine C6.3 clears 2e-4 given room) is the
**D2** world; **P9** (fine limit-cycle contingency) is the **D1** world; a decay that never clears is
**D3**. The D1/D2/D3 structure and the W = 15 threshold are NEW registered content that operationalises the
existing P6/P9 dichotomy — they do not edit P6/P9. *(One byte-invariance note: P2's prose still reads
"T4d coarse now carries 72 jet-core-radial cells"; the coarse mesh is identical in T4e, and the string is
left byte-invariant inside the frozen prediction rather than edited — §8a.)*

## 7. — (reserved; see §9 for cost)

## 8. Instruments and the measurement-script changes, as diffs (for the supervisor's §3 read)

The freeze set lives in `verification/runs/T-family/T4e_runs/`. Every change from the T4d instrument is a
diff to read before belief (`SUPERVISION_CHARTER` §3):

- **`build_t4e.py`** — `build_t4d.py` + FIVE registered `system_files()` changes verified by refuse-guards:
  (inherited) residualControl removal, four 0.7→0.6 relaxation factors, `writeInterval` pin; **(new)**
  `purgeWrite 2 → 0` (refuse unless exactly one `purgeWrite 2` line) and `runTimeModifiable false → true`
  (refuse unless exactly one `runTimeModifiable false` line); LEVELS fine `endTime 64000 → 160000`;
  CASE.txt records `purgeWrite 0` + `runTimeModifiable true`. `stopAt endTime` is kept (the instrument
  rewrites it at runtime). Verified: on the frozen writer the fine controlDict emits `writeInterval 4000`,
  `purgeWrite 0`, `runTimeModifiable true`, `stopAt endTime`, `endTime 160000`, no residualControl, four
  0.6 relax; and the purgeWrite guard REFUSES (exit 2) if the frozen writer's `purgeWrite 2` line moves.
- **`analyse_t4e.py`**, **`mark_done_t4e.py`**, **`launch_t4e.sh`** — **PURE RENAMES**. Proven by forward
  reproduction: applying `s/T4d/T4e/g; s/t4d/t4e/g` (plus `s/T4D_/T4E_/g` for the launcher's
  `T4D_DETACHED` env var) to the T4d originals reproduces `mark_done_t4e.py` and `launch_t4e.sh`
  **byte-for-byte**; the same, PLUS the three named stale-name fixes below, reproduces `analyse_t4e.py`
  byte-for-byte. No reader, threshold, band, floor, gate, completion clause or launch guard changed. The
  frozen `analyse_t4.py` is imported unchanged (the `../T4_runs` import path and `T4DIR` are untouched).
- **`trajectory_t4e.py`** — the ONE new file (§3a); its two-arm + two-decay-arm planted control is §4 / §8a.
- **`T4e_registered.json`** — vs `T4d_registered.json`: rung id, case keys `T4d_IJ_* → T4e_IJ_*`,
  `parent`/`registered_change_vs_T4d`, the fine case (endTime 160000, purgeWrite 0, cost + `d1_early_terminate`),
  C5's instrument name (`mark_done_t4d.py → mark_done_t4e.py`), one convergence-note schedule pointer, the
  cost block, and the FOUR new blocks (`convergence_evidence_from_T4d`, `early_termination_D1`,
  `completion_semantics`, `d1_transient_route`). Confirmed byte-invariant vs T4d: `graded_rows`,
  `roache_floors`, `predictions` (P1–P9), controls C1/C1b/C2/C3/C4/C6, `planted_control_value` and the two
  plant scales, `refinement_ratio`, `factor_of_safety`, `verdict_vocabulary`, `reference`, `solver`,
  `registered_changes_vs_T4b`, and the measured VALUES of `convergence_evidence_from_T4b`.

### 8a. Disclosures at the §3 read

1. **The three stale-name fixes in `analyse_t4e.py` (lines 478, 612, 740) — APPROVED at the §3 review.** A
   purely mechanical `s/t4d/t4e/` would carry forward the stale strings `T4d_RESULTS.md` §8 flagged: the
   DONE-gate refuse message named `mark_done_t4b.py` (now `mark_done_t4e.py`), the `--json` default was
   `gate_t4b.json` (now `gate_t4e.json`), and the AST self-check label read `analyse_t4b.py` (now
   `analyse_t4e.py`). These are rung-id / JSON-filename self-references pointing at THIS rung's own artifacts,
   corrected in a **new** file (not a frozen-file edit).
2. **The cond1 false-D1 hole — CLOSED at the §3 review (REVISION 1).** The original cond1 endpoint clause
   `window-last >= 0.85 × window-first` was the wrong metric for an oscillating signal: it can false-REJECT
   a genuine limit cycle caught in an unlucky phase, and (with `rho_fit >= 0.95`) it let a **noisy** slow
   decay at rho 0.95–0.99 with ≥ 4 noise sign-changes pass all three conditions → false D1. It is **replaced
   by a trend-vs-oscillation test** reusing the linear fit already computed for cond3:
   `cond1 = (rho_fit >= 0.95) AND (net_trend_drop <= 0.5 × ptp_detrended)`, where `net_trend_drop = |slope| ×
   (iter_last − iter_first)` and `ptp_detrended = max(resid) − min(resid)` — the oscillation swing must be at
   least 2× the net drift. A limit cycle (net trend ≈ 0) passes; a monotone or noisy decay (trend dominates)
   fails. `rho_fit >= 0.95` is kept as the fast-decay backstop; the `0.85` endpoint clause is **deprecated,
   recorded, not silently dropped** (the param key survives as `_deprecated_last_ge_frac_of_first` in the
   JSON, with a comment in `trajectory_t4e.py`). The new arm **ARM S2** (noisy slow decay rho 0.97) verifies
   the fix: it passes cond2 and cond3 (sign-changes 8) and is rejected by cond1 alone (§4).

## 9. Cost — rule 12, from T4d's OWN CLEAN MEASURED core-min (the T4c per-cell basis is SIGTERM-inflated ~4.5×)

**Basis (CORRECTED at the §3 review, REVISION 2).** The T4d prereg priced the fine leg off the T4c per-cell
rate 3.67e-05 core-s/cell-it — but that basis is **SIGTERM-TRUNCATED and ~4.5× inflated** (board update 19;
`T4d_RESULTS.md` §11). T4e instead uses **T4d's OWN clean measured legs** (all `capped=no`) on the
**identical** meshes: coarse **21.667** core-min @ 30000, medium **206.100** @ 60000, fine **1200.233** @
64000 → fine rate **1200.233 / 64000 = 0.0187536 core-min/iter**. Coarse and medium run to the same endTimes
as T4d, so their measured core-min apply directly; the fine scales at its measured rate. ranks = 1 (F15).
**The T4c per-cell rate is NOT used.**

| level | iterations | **POINT core-min (T4d-measured basis)** | wall @ POINT (ranks 1) |
|---|---:|---:|---:|
| `T4e_IJ_c` | 30 000 | **21.667** (measured) | 0.36 h |
| `T4e_IJ_m` | 60 000 | **206.1** (measured) | 3.44 h |
| `T4e_IJ_f` (160000 HARD cap) | 160 000 | **3 000.6** (= 160000 × 0.0187536) | **50.0 h ≈ 2.08 d** |

**The fine leg with EARLY TERMINATION** (the operative expectation; `d1_early_terminate` in the JSON):

| fine outcome | iteration | fine core-min | wall (ranks 1) | derived $ |
|---|---:|---:|---:|---:|
| BEST (earliest legal confirmation, window 8000–64000) | 64 000 | **1 200.2** | 20.0 h | $1.03 |
| EXPECTED (window clear of the transient, ~64000–120000) | ~120 000 | **2 250.4** | 37.5 h ≈ 1.56 d | $1.92 |
| WORST = HARD CAP (D2/D3, or D1 never confirmed) | 160 000 | **3 000.6** | 50.0 h ≈ 2.08 d | $2.57 |

*Expected ground:* the confirmation fires only once the most-recent 15 checkpoints (60000 iters) sit clear
of the decaying transient (T4b's fine transient cleared ~40000–64000); on the finer T4e mesh with lower
relaxation the limit cycle, if D1, is expected to occupy the window by an evaluation iteration ~120000
(window start ~64000).

**Cap / timeout (stall BACKSTOP only).** Per-level **cap = 2× POINT** (coarse **45**, medium **412**, fine
**6 001**), **ceiling = 1.5× POINT**, `timeout_s = cap_core_min × 60 / ranks`. The fine `timeout_s = 360 060
s`. The core-min cap/timeout is only a backstop against a stall; the operative fine-leg stop is the D1
early-terminate or the endTime 160000 hard iteration cap. An overrun of the cap **stops the run**
(`capped=yes` → NOT A RESULT); it does not get a new budget (rule 12).

**Rung totals:** POINT (fine at hard cap) **3 228.4** core-min (53.8 core-h); EXPECTED **2 478.2** (41.3
core-h); BEST **1 428.0** (23.8 core-h); ceiling 4 842.6; per-level cap sum **6 458**.

**USD, DERIVED not measured**, owner-stated $0.0513/core-h (`COMPUTE_BUDGET_CHARTER` §5; the box cannot
read its own billing): whole-rung POINT **$2.76**, EXPECTED **$2.12**, BEST **$1.22**, ceiling $4.14,
cap-sum $5.52. **The $25 pre-authorised unit is PER RUN:** the dearest single run is the fine at its 2×
cap = 6 001 core-min = 100.0 core-h × $0.0513 = **$5.13 ≪ $25**; the whole-rung cap-sum $5.52 is a sum, not
a single run. Well inside Sanaa's 2026-08-21 blanket, still costed here per rule 12. Estimate-vs-actual
lands in `docs/COST_CALIBRATION.md` at completion (rule 12).

**OPERATIONAL FLAG (capacity call to chief).** With the corrected basis the fine leg is a **~20 h (best) to
~50 h POINT / ~100 h cap single-rank** solve — still the longest single run this ladder has scheduled, but
**NOT the 9.4 d the inflated T4c basis implied**. The D1 early-terminate design shortens it further once the
answer is measured. Scheduling a ~1–4 day single-tenant leg while the box is contended is a
cross-family/daemon call flagged to chief, not decided in this draft.

## 10. What this rung cannot see

- No Nu row is graded (BLOCKED, T4 §2.1); a PASS on G1–G3 is a joint code-plus-closure statement.
- A different mesh family from T4b (3.75 N² vs 2.625 N²): no cross-rung triple; T4b/T4c/T4d numbers are
  context, never a level.
- A confirmed D1 is a MEASURED finding about a **steady** solver; the transient/URANS successor (§3c), not
  T4e, characterises the unsteady structure. T4e's wedge is one 2.5° sector: nothing about azimuthal
  structure.
- The D1/D3 discriminator rests on the pinned cond1 bounds (§8a item 2, the trend-vs-oscillation test); the
  noisy-slow-decay risk was closed at the §3 review and is verified by ARM S2.
- Nothing here authorises a launch or a send (rule 7). No frozen T4/T4b/T4c/T4d file is modified.

## 11. Completion-semantics summary (the anti-masquerade clause)

| branch | fine reaches endTime 160000? | rule-4 completion? | grading instrument | verdict |
|---|---|---|---|---|
| **D1** (robust limit cycle) | No — clean early stop at confirmation | **No** (not claimed, not needed) | `D1_CONFIRMED_TERMINATE` marker + trajectory | **NOT A RESULT** (unsteadiness), DISCHARGED → transient successor |
| **D2** (clears 2e-4 by 160000) | Yes | **Yes** (`mark_done_t4e.py`, unchanged rule 4 + age guard) | Roache triple, `analyse_t4e.py` | PASS in band / GATE FAIL, or NOT A RESULT if a triple is non-CONVERGING |
| **D3** (decays, not cleared, by 160000) | Yes (or continuation) | **Yes** for the field reached | continuation rung | measured finding → continuation successor |

## 12. The freeze set — grading path FIXED BY SHA (committed in the same commit as this document)

`git hash-object` blobs of the exact committed files. The frozen comparator prints its own `sha256_of()`
provenance at runtime, so the file that ran can be hashed against the pinned blob below. This freeze table
lives in the `.md`, so the `.md` itself is not among the hashed files. The self-referential comparator
`analyse_t4e.py` carries **no** `EXPECTED_SELF_BLOB` / `GRADING_PATH_FREEZE_COMMIT` constant (it prints its
sha256 for external comparison, print-only — the T4d mechanism, `analyse_t4d.py` was frozen the same way in
`eae8e96c`); its authoritative self-pin is the **FREEZE-PIN line `analyse_t4e.py@740575a7` in the freeze
commit message** (the git pre-image self-reference impossibility — a file cannot contain its own committed
hash). No two-commit re-pin is needed (that pattern, T23G2R, applies only to a comparator that embeds its
own freeze-commit sha).

| file (grading path) | git blob | lines | note |
|---|---|---:|---|
| `verification/runs/T-family/T4e_runs/build_t4e.py` | `6e77d62f` | 325 | rename of `build_t4d.py` + endTime 160000 + purgeWrite 0 + runTimeModifiable true, each behind a refuse-guard; py_compile clean |
| `verification/runs/T-family/T4e_runs/analyse_t4e.py` | `740575a7` | 753 | PURE RENAME + the 3 named stale-name fixes; selftest 20/20 (`python3` and `-O`); frozen `analyse_t4.py` imported unchanged |
| `verification/runs/T-family/T4e_runs/mark_done_t4e.py` | `e4e44396` | 256 | PURE RENAME; selftest PASS both interpreters; strict rule 4 + age guard UNCHANGED |
| `verification/runs/T-family/T4e_runs/launch_t4e.sh` | `441ccdfb` | 185 | PURE RENAME (incl. `T4E_DETACHED`); `bash -n` clean; reads the cap from `T4e_registered.json` |
| `verification/runs/T-family/T4e_runs/T4e_registered.json` | `a11380c6` | 341 | byte-invariant gates/bands/predictions; the revised cond1 threshold, the fine schedule, the T4d-measured cost, and the four new D1 blocks |
| `verification/runs/T-family/T4e_runs/trajectory_t4e.py` | `512b3691` | 435 | NEW instrument; two-arm + two-decay-arm planted control (ARM A fires; ARM B, ARM S, ARM S2 do not); trend-vs-oscillation cond1; selftest PASS both interpreters |

**Frozen inherited members, imported and never copied — pinned by blob at this freeze:**

| frozen import | git blob | imported by | provides |
|---|---|---|---|
| `verification/runs/T-family/T4_runs/analyse_t4.py` | `6f362447` | `analyse_t4e.py`, `trajectory_t4e.py` | `sample_profile`, `peak_of`, `classify`, `gci`, `planted_zero_control`, `latest_time` |
| `scripts/roache_triple.py` | `78e56a3b` | `analyse_t4e.py` | `STAGNANT_FLOOR` (0.5), `P_MIN` (0.05) |
| `verification/runs/T-family/T4_runs/build_t4.py` | `ff032f3e` | `build_t4e.py` (build-time, not on the grading path) | `header`, `grading_ratio`, `system_files`, `constant_files`, `fields` |

These are UNCHANGED in the worktree at this freeze; none is modified by T4e (CLAUDE.md rule 6).

**Still WITHHELD until the supervisor's separate STAGED launch phase:** the build (`blockMesh`/`checkMesh`
birth certificate) and the queue entries. Launch is HELD for box capacity (§9). Freeze-now-hold-launch
(chief-endorsed 2026-09-08).
