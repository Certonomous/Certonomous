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

---

## AMENDMENT A1 — 2026-09-11, **POST-COMPUTE. DISCLOSURE ONLY.** Document **v1.0 → v1.1**.

**`lines whose number changed above this section: 0`.** This amendment is appended at the foot
under `CLAUDE.md` rule 6. **It alters NO gate, threshold, cap, band, floor, reference, prediction or
label** (`CLAUDE.md` rule 2: gates closed at first compute, 2026-09-10T15:44:03Z). Nothing in §0–§12
above is edited, struck or renumbered. **No frozen instrument is patched by this amendment** — see
A1.4 for why the two instrument gaps below are recorded rather than repaired.

**Occasion.** The rule-4 discharge of the coarse and medium legs, 2026-09-11. Both graded **`PASS`**
by the registered instrument `verification/runs/T-family/T4e_runs/mark_done_t4e.py` (blob `e4e44396`,
== the §12 pin), all seven conjuncts evidenced separately: rc 0; exactly one `End`; last time
30000/60000 == `controlDict` `endTime`; 8/8 fields `T U p_rgh alphat nut k omega phi`;
`ExecutionTime` count 30000/60000 == `round(endTime/deltaT)` at the registered `deltaT` 1;
age-guard margins **+1469.0 s** and **+13109.1 s** (oldest field at `endTime` minus the case's own
`0/T`). **The rung stays `PENDING`** — `T4e_IJ_f` is still iterating, so there is no triple, no
observed order and no GCI, and none is quoted anywhere in this amendment.

**Grading-path re-hash, recorded because §12 exists to be checked and not merely written.** All six
frozen files and all three frozen imports were re-hashed against the §12 pins at this reading and
**every one matches**: `build_t4e.py` `6e77d62f`, `analyse_t4e.py` `740575a7`, `mark_done_t4e.py`
`e4e44396`, `launch_t4e.sh` `441ccdfb`, `T4e_registered.json` `a11380c6`, `trajectory_t4e.py`
`512b3691`, `T4_runs/analyse_t4.py` `6f362447`, `scripts/roache_triple.py` `78e56a3b`,
`T4_runs/build_t4.py` `ff032f3e`. §8's **pure-rename claim was re-proved by forward reproduction**
rather than taken on trust: `s/T4d/T4e/g; s/t4d/t4e/g` on `T4d_runs/mark_done_t4d.py` reproduces
`mark_done_t4e.py` **byte-for-byte**, the same on `launch_t4d.sh` (plus `s/T4D_/T4E_/g`) reproduces
`launch_t4e.sh` **byte-for-byte**, and the same on `analyse_t4d.py` reproduces `analyse_t4e.py` with
**exactly the three stale-name fixes §8a item 1 discloses, at lines 478, 612 and 740, and nothing
else**.

### A1.1 — `mark_done_t4e.py:121` does NOT enforce "exactly one `End` line"

**Measured, not inferred.** The clause reads `if n_end == 0: fails.append("log.solve has no End
line")`. It therefore fails a log with **zero** `End` lines and passes a log with **one or more**.
`CLAUDE.md` rule 4 and `T1b_L4_AMENDMENT.md` §7 are satisfied by the instrument's behaviour on a
single-run log, and **both completed legs measure exactly 1** (`T4e_IJ_c/log.solve`,
`T4e_IJ_m/log.solve`), so **no verdict on this rung is affected and none is withdrawn**.

**Why it is recorded anyway, and it is live rather than hypothetical:** a restarted solver whose
output is **appended** into the same `log.solve` produces two `End` lines, an `ExecutionTime` count
that can still sum to `endTime`, and fields written by the second run that are newer than `0/T` — so
the concatenated-restart case passes every conjunct this instrument tests. `T4e_IJ_f` is **still
running** at this amendment, which is exactly the window in which such a restart could occur.
Detection costs nothing: the count is already computed at `:119-120` and only the comparison is
weak.

### A1.2 — `mark_done_t4e.py:143` uses `mtime < age`, so an EQUAL mtime passes the age guard

`CLAUDE.md` rule 4 requires every field at `endTime` to be **strictly NEWER** than the case's own
`0/T`. The instrument's test is `os.path.getmtime(...) < age` → stale, so a field whose mtime is
**exactly equal** to `0/T`'s is not flagged. **Both legs' measured margins are 1469.0 s and
13109.1 s**, orders of magnitude away from the boundary, so **no verdict is affected**. The
launcher's `sleep 1` between `cp -r 0.orig 0` and `touch 0/T` (`launch_t4e.sh:167-169`) makes
equality unlikely in practice; it does not make it impossible on a filesystem with coarse mtime
granularity, and the rule's word is *strictly*.

### A1.3 — THE D1 EARLY-TERMINATION INSTRUMENT WAS REGISTERED AND NEVER SCHEDULED

**The largest of the three, and it is an infrastructure omission with a measured cost, not a gate
defect.** §3a registers a clean early terminate for the fine leg, and §9 sizes what it buys. **At
this amendment `trajectory_t4e.py` has never been run against `T4e_IJ_f`.** Measured
2026-09-11T15:3x Z: no `trajectory_t4e.py` process in a `ps -eo args` sweep carrying its own planted
non-zero (the same sweep sees the rate watcher pid 1276443 and the full solver lineage
1231217 → 1233986 → 1233987); no `crontab` entry; no `D1_CONFIRMED_TERMINATE.T4e_IJ_f` marker; and
`autograde_t4e.sh` names the instrument **only inside a comment reproducing the §12 freeze table**.

**Consequence, stated exactly.** With the instrument unscheduled the fine leg runs to the 160000
hard iteration cap whatever its trajectory does. Per §9 that is the difference between the
**EXPECTED** 2 250.4 core-min at ~120000 and the **WORST/HARD-CAP** 3 000.6 core-min at 160000 —
**up to ~750 core-min, ~$0.64 derived at $0.0513/core-h** — spent after the answer would have been
measured. It is **not** a gate deviation: §3a names endTime 160000 as the HARD cap and §11 registers
the hard-cap landing as **D2** or **D3**, so running to it is a **registered outcome**, and no band,
threshold, cap or label moves either way.

**And the D1 FINDING ITSELF IS NOT LOST BY THE OMISSION** — this is the reassuring half and it is a
consequence of registered change #2. `purgeWrite 2 → 0` was registered precisely so *"every written
checkpoint survives"*, and `trajectory_t4e.py::c63_series` rebuilds the whole trajectory **from disk**
on every invocation, holding no state between runs. So a D1 classification can be made **at any
later time, including after the leg has ended**, from the surviving checkpoints. **What the omission
can cost is core-minutes; it cannot cost the finding.**

### A1.4 — WHY NONE OF A1.1–A1.3 IS PATCHED HERE

`analyse_t4e.py` and `mark_done_t4e.py` are **frozen by sha in §12 and first compute has occurred**
(2026-09-10T15:44:03Z). Editing either now would be a post-first-compute change to a fixed grading
path, which `CLAUDE.md` rule 2 forbids and which `scripts/check_comparator_freeze.py` enforces. A1.1
and A1.2 therefore land as **disclosures carried forward to the successor registration**, where the
two clauses are written as `n_end == 1` and `mtime <= age → stale`; A1.3 is an **operational** matter
that changes no file on the grading path and may be discharged at any time by running the already
frozen `trajectory_t4e.py` unchanged.

### A1.5 — TWO BOOKKEEPING DIVERGENCES IN THE COST FIGURES. **No verdict rests on either.**

Recorded because an unexplained pair of numbers in two files is how a future reader is misled, and
because **the conservative figure is the registered one** — which is worth stating rather than
leaving to be re-derived.

1. **`T4E_RATE_PROJECTION.json` reports `registered_cap` 43.334 / 412.2 / 6001.2; the registered
   `T4e_registered.json` `cases.*.cap_core_min` reads 45 / 412 / 6001.** The projection file's
   figures are its own `2 × POINT` re-computation (2 × 21.667 = 43.334), **not** a read of the
   registration. **The registered values are the operative ones and they are the LARGER pair**, and
   they are what the launcher actually enforced: `launch_t4e.sh:66-75` reads `timeout_s` from
   `T4e_registered.json` and **refuses any `--timeout` not EQUAL to it**, so the legs ran under
   `timeout_s` 2700 / 24720 / 360060 s = 45 / 412 / 6001 core-min at ranks 1. The projection file
   states of itself that it *"Grades nothing, moves no marker, stops no solver"*.
2. **§9's prose cap for the coarse level reads 45 while its own stated rule `cap = 2× POINT` gives
   2 × 21.667 = 43.33.** §9's prose figure agrees with the registered JSON and with the enforced
   `timeout_s`; the 43.33 is the unrounded arithmetic. **The registered 45 is the conservative
   figure and is the one that bound the run.** Neither leg came near either number (coarse 24.483
   core-min = 54.4 % of 45; medium 218.500 = 53.0 % of 412), so no cap-stop was in prospect on any
   reading.

### A1.6 — WHAT THIS AMENDMENT DOES NOT DO

It withdraws no verdict, demotes nothing, and moves no number in §0–§12. It asserts nothing about
`T4e_IJ_f`, whose rule-4 state is **`PENDING`** and unknowable until the leg lands. It does not
authorise a launch, a stop, an arming of the D1 trigger, or a send (`CLAUDE.md` rule 7: SUBMISSIONS
REMAIN PARKED). **And it records one scoping correction for the successor's benefit:** T4e is a
registered **axisymmetric 2.5° wedge**, and its three `log.checkMesh` files accordingly read
`Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)` with 2 `wedge` patches and 1 `empty`
axis patch in `constant/polyMesh/boundary` — **the correct signature for this discretisation**.
`VERIFICATION_CHARTER.md` §2bo.1/§2bo.3 (v1.84, 2026-09-10, which post-dates this freeze) binds the
**claim** and not the comparator: **T4e may not be described as a 3D case in any caption, board line,
report or demo.** No refusal is owed on these runs and no verdict is withdrawn — §2bo.3 says so in
terms, naming T4e.

---

## ADDENDUM A2 — 2026-09-11, **POST-COMPUTE, PRE-OUTCOME PREDICTION.** Document **v1.1 → v1.2**.

**`lines whose number changed above this section: 0`.** Appended at the foot under `CLAUDE.md` rule 6.
**It alters NO gate, threshold, cap, band, floor, reference, prediction, label or registered branch**
(`CLAUDE.md` rule 2: gates closed at first compute, 2026-09-10T15:44:03Z). Nothing in §0–§12 or in
Amendment A1 is edited, struck or renumbered. **The registered D1 / D2 / D3 branches of §3a, §3b and
§11 are untouched**, and §3a's hard cap `endTime 160000` is untouched.

> **THIS ADDENDUM CHANGES NOTHING ABOUT WHETHER THE LEG RUNS. `T4e_IJ_f` RUNS TO `endTime`.**
> D3 is a registered outcome, completing is what the owner asked for, and **a predicted D3 that is
> allowed to run and is then confirmed is worth more than a D3 asserted and stopped early to save
> compute.** No D1 trigger is armed, no marker is written, no `controlDict` is touched.
> Nothing here has been sent, filed or uploaded (`CLAUDE.md` rule 7).

### A2.0 — WHY A PREDICTION IS RECORDED NOW RATHER THAN AFTER

**A prediction made before the number exists is a test of this lab's understanding; the same sentence
written afterwards is a rationalisation of whatever arrived.** At this writing `T4e_IJ_f` is at
iteration ~64,500 of 160,000 and none of the quantities predicted below exists yet.

### A2.1 — THE MEASUREMENT THIS RESTS ON, AND HOW IT WAS TAKEN

The **frozen** `trajectory_t4e.py` (worktree blob `512b36911812004746e032267a5b66980e7b930d`, which
reproduces the §12 pin `512b3691`; `HEAD:` returns the same blob) was run **read-only, without
`--commit`**, against a **mirror** of the case in a scratch directory — never against the live case,
because the frozen reader `analyse_t4.sample_profile:117-119` **writes** `system/t4sample` into the
case it grades and then runs `postProcess` into `postProcessing/`. The mirror was proved faithful by
sha256 on four field checkpoints and `constant/polyMesh/owner`, under a planted control.

**An mtime + size census of the live `system/` and `constant/`, taken at 16:24:26Z before the work
and 17:24:22Z after it, is IDENTICAL on all 17 entries**, and the census comparator was proved able to
see a planted single-byte change. `stopAt endTime` is unchanged; no `D1_CONFIRMED_TERMINATE` marker
exists; no `system/t4sample` and no `postProcessing/` exist in the live case.

**The classifier does NOT confirm D1 at 64,000.** All three registered conditions fail:
`rho_fit` 0.8414710 against ≥ 0.95; `max/min` 75.16424 against ≤ 5; detrended `sign_changes` 2
against ≥ 4. Only cond1's second limb passes (`trend/ptp` 0.42940 against ≤ 0.50) and cond2's mean
limb (0.1182410 against ≥ 1e-3). The iteration gate and the W = 15 window requirement both opened at
exactly 64,000. **The measured C6.3 series, 15 points, window [8000, 64000]:**

| iter | C6.3 | iter | C6.3 | iter | C6.3 |
|---:|---:|---:|---:|---:|---:|
| 8000 | 1.140860e+00 | 28000 | 4.815198e-02 | 48000 | 2.470830e-02 |
| 12000 | 1.994201e-01 | 32000 | 7.237710e-02 | 52000 | 1.898578e-02 |
| 16000 | 1.846361e-02 | 36000 | 5.754263e-02 | 56000 | 1.682133e-02 |
| 20000 | 1.934310e-02 | 40000 | 4.910431e-02 | 60000 | 1.584375e-02 |
| 24000 | 3.988422e-02 | 44000 | 3.693016e-02 | **64000** | **1.517823e-02** |

The tail is **monotone decreasing over nine consecutive checkpoints** and its decay ratio is
**rising** — 0.669, 0.768, 0.886, 0.942, **0.958** — i.e. the decay is *decelerating*.

> **THIS IS AN EXTRAPOLATION OF NINE POINTS AND NOTHING MORE.** It is not a measurement of anything
> beyond 64,000, it is not a gate, and no verdict rests on it. It is recorded so that it can be
> scored against what actually arrives.

### A2.2 — PREDICTION P-A2-1: the fine leg reaches the 160,000 hard cap WITHOUT clearing C6.3

**Predicted C6.3 at iteration 160,000: point `5.42e-03`, band `[2.57e-03, 1.52e-02]`.**

- **Point** — decay ratio frozen at the last measured value 0.95799 over the remaining 24
  checkpoints: `1.517823e-02 × 0.95799^24 = 5.419e-03` = **27.1× the 2e-4 tolerance**.
- **Band lower** — ratio frozen at the mean of the last three (0.92863): `2.567e-03` = **12.8× tol**.
- **Band upper** — the decay stalls completely from here (ratio → 1): `1.518e-02`, i.e. no further
  descent. This limb is included **because the measured ratio is rising toward 1**, so a plateau is
  the physically indicated upper end and excluding it would make the band dishonestly narrow.
- Clearing 2e-4 at the last measured ratio would need **403,542 further iterations against the
  96,000 the cap allows.**

**NAMED FALSIFIERS, checkable against the artifact:**
1. **C6.3 at 160,000 ≤ 2.0e-04** falsifies the prediction outright.
2. **C6.3 at 160,000 outside `[2.57e-03, 1.52e-02]`** falsifies the *band*, even where the
   "does not clear" claim survives.

> **WHICH LIMB IS LOAD-BEARING, said plainly so a later reader does not mis-weigh this.** The band
> `[2.57e-03, 1.52e-02]` spans 12.8x to 76x tol and **its upper limb is essentially the present
> value** — a complete stall. It is deliberately that wide, because excluding the plateau would have
> been drawing the band to be met. The consequence is that **a result landing inside this band is
> WEAK confirmation and must not be reported as a strong one.** **The prediction's teeth are
> falsifier 3, the mid-flight ratio test** — it is sharp, it rests on evidence that will exist long
> before the cap, and it can fire while the leg is still running. That is the limb to watch.

3. **Mid-flight, before the cap:** the prediction requires the decay ratio to stay above **0.835** on
   average over the remaining 24 checkpoints — `(2e-4 / 1.517823e-2)^(1/24) = 0.8350` is exactly the
   ratio that would reach tol at 160,000. **A sustained per-checkpoint ratio ≤ 0.835 over any three
   consecutive checkpoints falsifies this prediction before the leg ends.** The last three measured
   are 0.886, 0.942, 0.958 — all above it.

### A2.3 — PREDICTION P-A2-2: the registered outcome is D3, not D1 and not D2

§3a registers: *"if D1 is never robustly confirmed by 160,000, the outcome is **D2** (if C6.3 cleared
2e-4 → grade the full triple) or **D3** (decaying-not-cleared → continuation rung)."* The trajectory
is decaying and is predicted not to clear, so **D3**. **Falsified by** C6.3 clearing 2e-4 (→ D2), or
by a genuine limit cycle developing after 64,000 such that the registered classifier's three
conditions all hold on some later W = 15 window (→ D1).

### A2.4 — PREDICTION P-A2-3: the triple returns `NOT A RESULT` on gate (1)

**Mechanism verified in the frozen comparator, not assumed:** `analyse_t4e.py:560` appends
`"C6.3 field change %s > %g"` to that level's `gate1` list whenever `c6_3` is false, and `:335`
returns `"NOT A RESULT", state, p, None, "gate (1): " + …` before any band is read. `FIELD_TOL` is
read at `:88` from the registered JSON. So a fine level above tol produces `NOT A RESULT` at gate (1),
ahead of the triple — `CLAUDE.md` rule 5 clause (1) by authority, and this line by mechanism.

**The sharper reading, and it is the reason this prediction is worth recording.** The coarse and
medium levels **cleared** C6.3 — 1.396e-06 and 3.390e-06 against 2e-4 — while the fine level sits at
1.518e-02, **4,478× worse than the medium.** **The coarser levels converge and the fine level does
not.** That is the same shape `K2f_PREREGISTRATION.md` §0.2–§0.3 measured on the rack row, where the
coarse mesh converged six decades and the refined levels limit-cycled. §0.3's reasoning applies here
in terms: *where convergence STATE differs across the ladder the triple is invalid in principle,
because the inter-level differences then measure a mixture of discretisation error and convergence
state.* **Rule 5 clause (1) and §0.3 reach the same verdict by different routes — one by authority,
one by mechanism — and their agreement is itself the finding.**

**NAMED FALSIFIERS:**
1. **The fine level clearing 2e-4 at 160,000** — then gate (1) does not fire on C6.3 and the triple
   is consulted. This is the same falsifier as P-A2-1 and is the principal one.
2. **A gate-(1) failure on a DIFFERENT control** — C1, C1b, C2, C3, C6.1 or C6.2 — would make
   `NOT A RESULT` correct for a reason this prediction did not name, which falsifies the prediction's
   *stated ground* even though its verdict survives. **T4d's coarse level already failed gate (1) on
   C2** (`U_c/U_bulk` 1.1793 outside ±3 % of 1.2245), so this limb is live, not hypothetical.
3. **NOT a falsifier, stated so it is not mistaken for one:** the fine level *plateauing* above tol.
   A plateau above the registered tolerance is still not iteratively converged by C6.3's own
   threshold, so gate (1) still fires. That outcome confirms rather than refutes.

### A2.5 — TWO MEASUREMENTS RECORDED IN THEIR OWN RIGHT

**(a) A full-ladder bit-exact reproduction across two separately launched runs.** At matched times,
`T4d_IJ_*` and `T4e_IJ_*` are **byte-identical on `T`, `U` and `p_rgh` at all three levels** —
coarse at 30,000, medium at 60,000, fine at 64,000 — on meshes that are themselves byte-identical
(`owner`, `faces`, `points`, `neighbour`, `boundary` all matching). The fine C6.3 agrees to every
printed digit: `T4d_RESULTS.md:139` records `0.015178230567379214` and this leg's measured value at
64,000 is `0.015178230567379214`. **A first comparison of the c and m levels appeared to DIFFER; that
was an artifact of a lexical rather than numeric sort over the time directories and is corrected
here rather than left on the record.** The consequence for this rung: **every bit of new information
in the fine leg lies beyond iteration 64,000.**

**(b) The price of a clean provenance chain, measured.** The fine leg spent
**`ExecutionTime` 90,831.08 s to reach iteration 64,000 = 1,513.85 core-min = 25.231 core-h**,
**$1.294 DERIVED** at $0.0513/core-h (derived, never measured — the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5), re-deriving from scratch a result T4d already held. That is the
cost of a launch guard that refuses a case where `0` or a time directory already exists, and of an
age guard whose referent is the case's own `0/T`. **It is not waste and is not booked as waste: it is
a cost this lab chose in exchange for a provenance chain with no restart in it, and it is now
MEASURED rather than asserted.**

> **A SUPERSEDED FIGURE, recorded as an ERROR and not as an alternative.** A figure of ~1,206
> core-min / ~$1.03 was carried in discussion before this reading. **It is wrong and it is not an
> alternative estimate.** Its defect is named so the class is recognisable: it applied the leg's
> CURRENT rate of ~1.13 core-s/iteration to the whole history, when **the leg's own average over
> 63,999 iterations is 90,831.08 / 63,999 = 1.4193 core-s/iteration.** That is estimating a quantity
> that was available to be read. **The only figure of record is 1,513.85 core-min / $1.294 derived,
> read from `log.solve`.**

### A2.6 — WHAT THIS ADDENDUM DOES NOT DO

It moves no gate, threshold, band, cap or label; it withdraws no verdict; it demotes nothing; it does
not alter the registered D1/D2/D3 branches or the 160,000 hard cap; it does not authorise or forbid a
launch, a stop, an arming or a send; and it patches none of the three instrument gaps recorded in
A1.1–A1.3, which remain live and are carried to the successor. **The rung's state remains `PENDING`**
and this addendum assigns no verdict.

*Written by a heat-transfer `lab-lane`, 2026-09-11, on the supervisor's ruling. Zero solver
core-minutes; the only compute spent is ~5.4 core-min of read-only `postProcess` on a scratch mirror.
Nothing sent, filed or uploaded (`CLAUDE.md` rule 7).*

---

## ADDENDUM A3 — 2026-09-12, **POST-COMPUTE. GRADING-PATH DRIFT DISCLOSURE.** Document **v1.2 → v1.3**.

**`lines whose number changed above this section: 0`.** Appended at the foot under `CLAUDE.md` rule 6;
**checked, not asserted** — after writing, this file was diffed against its `HEAD` blob and the change
is **insertions only, in a single hunk at the end of the file, zero deletions**. **It alters NO gate,
threshold, cap, band, floor, reference, prediction, label, registered branch or verdict** (`CLAUDE.md`
rule 2: gates closed at first compute, 2026-09-10T15:44:03Z). Nothing in §0–§12, A1 or A2 is edited,
struck or renumbered, and **no frozen instrument is patched, reverted or touched by this addendum**.
**The rung stays `PENDING`**; no triple, order or GCI is quoted here.

### A3.1 — ONE §12 PIN HAS DRIFTED. It is recorded BEFORE the triple is graded, not after.

Re-hash of the §12 freeze table at this reading, `git hash-object` on the worktree and
`git rev-parse HEAD:<path>` on `HEAD`, the two agreeing on every row:

| §12 pin | pinned blob | worktree == HEAD | state |
|---|---|---|---|
| `build_t4e.py` | `6e77d62f` | `6e77d62f` | HOLDS |
| `analyse_t4e.py` | `740575a7` | `740575a7` | HOLDS |
| `mark_done_t4e.py` | `e4e44396` | `e4e44396` | HOLDS |
| `launch_t4e.sh` | `441ccdfb` | `441ccdfb` | HOLDS |
| `T4e_registered.json` | `a11380c6` | `a11380c6` | HOLDS |
| `trajectory_t4e.py` | `512b3691` | `512b3691` | HOLDS |
| `T4_runs/analyse_t4.py` | `6f362447` | `6f362447` | HOLDS |
| `T4_runs/build_t4.py` | `ff032f3e` | `ff032f3e` | HOLDS |
| **`scripts/roache_triple.py`** | **`78e56a3b`** | **`23afaee3`** | **DRIFTED** |

Eight of nine hold. `scripts/roache_triple.py` moved
`78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` → `23afaee32f770f9f38a827e38ac963b9368b7707` in commit
**`a7b3846d89c516d90e9cb863702fc3cb877f431a`**, authored by the **verification** team,
**2026-09-11 16:43:37 +0000** (*"REPAIR roache_triple under the §2db/§2d.1 grant -- ONE function now
writes the reason a GCI is withheld…"*), **203 insertions, 10 deletions**. That commit **postdates
T4e's first compute** (2026-09-10T15:44:03Z) by **25.0 hours**, so it lands inside the window in which
`CLAUDE.md` rule 2 has the grading path fixed.

**A1's re-hash was true when it was written and is false at `HEAD`, and the clock says why.** A1's
"every one matches" was committed in `2c1e81b3f416fa048078de3c4c6d6cdf331fc0b6` at
**2026-09-11 15:46:09 +0000** — **57 minutes BEFORE** the drift commit. A1 is not corrected or struck;
it is **superseded as to that one row from 16:43:37 onward**, and this addendum is the record of it.

**The drifted file is NOT reverted and NOT repaired here.** It is another team's instrument and other
work now rests on it; `CLAUDE.md` rule 10 says an unexpected change is **inspected, never reverted**.

### A3.2 — MEASURED: the drift is INERT for T4e. Both surfaces re-derived at this reading.

**Surface 1 — the runtime import.** `analyse_t4e.py:64` is the **only** runtime import from that
module: `from roache_triple import STAGNANT_FLOOR, P_MIN`. Nothing else is imported at run time
(`grade_ladder`, `format_row`, `_seal`, `gci_unequal`, `triple_from_cells` are never referenced).
Both constants are **byte-identical across the two blobs**, at **line 170** (`STAGNANT_FLOOR = 0.5`)
and **line 171** (`P_MIN = 0.05`), comments included. `analyse_t4e.py:77` **REFUSES (exit 2)** if
those two values disagree with `T4e_registered.json`'s `roache_floors`, so a future move of either
constant cannot pass silently into a T4e grade.

**Surface 2 — the selftest cross-check.** The selftest additionally does `import roache_triple as RT`
at `analyse_t4e.py:647` and cross-checks its own `classify()` against **`RT.gci_equal`** on eight
synthetic triples at `:651`–`:653`. That is the module's **only** other use anywhere in the grading
path. `gci_equal` occupies **lines 239–275 in BOTH blobs** and is **byte-identical**: **1,525 bytes**
each, md5 `316f8844db022b4e00c79765802edbe0` on both.

**How far the identity runs.** The two blobs are **byte-identical through line 619**; the first
differing byte is at line 620. The list of top-level statements is identical apart from a single
added `def`, so **import-time behaviour is unchanged** — importing the new blob executes the same
statements and binds the same names plus one.

**What actually changed, stated exactly, because an incomplete account is not evidence.** The new
blob adds **one** top-level function, `gci_refusal_reason` (new-blob lines 720–809), and rewrites two
call sites to use it — the `NOT A RESULT` branch inside **`grade_ladder`** (old lines ~620–635) and
the "GCI NOT QUOTED" block inside **`format_row`** (old lines ~697–708); **all 10 deletions sit in
those two call sites**. The remaining growth is in `selftest` and `main`. **None of
`gci_refusal_reason`, `grade_ladder` or `format_row` is on T4e's import surface** — T4e imports two
floats and calls one function, and that function did not move a byte. **The drift is therefore inert
for this rung**, and this is a measurement, not an inference from the commit subject.

### A3.3 — WHAT IS **NOT** FIXED: this rung has NO runtime freeze verification. Standing exposure.

§12 registers **no** runtime freeze check in `analyse_t4e.py` and says so in its own words: the
comparator "carries **no** `EXPECTED_SELF_BLOB` / `GRADING_PATH_FREEZE_COMMIT` constant (it prints its
sha256 for external comparison, **print-only**)". There is likewise **no blob check on the three
frozen imports** at execution. Consequently **`CLAUDE.md` rule 2's hash check for T4e is EXTERNAL AND
MANUAL**: nothing in the grading path refuses, or even notices, a drifted import — the pin is only
ever checked when a human or a lane chooses to check it.

**That is exactly why this drift went unrecorded for 10.3 hours** (16:43:37Z on 2026-09-11 to
02:59:57Z on 2026-09-12), and it would have gone unnoticed indefinitely had the fine leg landed and
been graded first. **This addendum does NOT repair it.** Adding a runtime freeze check to
`analyse_t4e.py` would patch a frozen instrument after first compute, which rule 2 forbids and
`scripts/check_comparator_freeze.py` enforces — the same reasoning A1.4 gave for A1.1–A1.3. It is
recorded here as a **standing exposure of this rung**, carried to the successor registration, where
the check belongs **inside** the comparator: pin the imports by blob at execution and **refuse** on
mismatch, rather than printing a sha for somebody to compare by hand.

### A3.4 — RE-VERIFICATION AFTER THE APPEND (the registration is not read by its own grader)

Appending to a pre-registration is only safe if nothing on the grading path parses it. **Checked, not
assumed.** All eight files of the §12 grading path were searched for any read of this document:
`analyse_t4e.py`, `mark_done_t4e.py`, `launch_t4e.sh`, `trajectory_t4e.py`, `build_t4e.py`,
`T4_runs/analyse_t4.py`, `T4_runs/build_t4.py` and `scripts/roache_triple.py`. **The string
`PREREGISTRATION` does not appear in any of them.** Every occurrence of `.md` in those files is
docstring or comment prose (e.g. `CLAUDE.md rule 5`, `MESH_STANDARD.md section 10.5`), and **no
`open()` / read call in any of them takes a `.md` path** — `analyse_t4e.py`'s only registration read
is `json.load(open(.../T4e_registered.json))` at `:66`. **No file on T4e's grading path reads
`T4e_PREREGISTRATION.md` at run time**, so this append cannot perturb a grade; **no selftest re-drive
was required and none was run.**

### A3.5 — WHAT THIS ADDENDUM DOES NOT DO

It moves no gate, threshold, band, cap, floor or label; it withdraws no verdict and assigns none; it
does not alter the registered D1/D2/D3 branches or the 160,000 hard cap; it does not edit, revert or
re-pin `scripts/roache_triple.py`, and it does **not** amend the §12 table — the pin stays `78e56a3b`,
and this section is the disclosure that the file at `HEAD` is no longer that blob and why that is
inert. It does not patch the instrument gaps in A1.1–A1.3, which remain live. It authorises no launch,
no stop and no send (`CLAUDE.md` rule 7: SUBMISSIONS REMAIN PARKED).

*Written by a heat-transfer `lab-lane`, 2026-09-12. **Zero solver core-minutes; zero compute beyond
reading files** — no solver, selftest or `postProcess` was run for this addendum, and no running case
was touched. Nothing sent, filed or uploaded (`CLAUDE.md` rule 7).*
