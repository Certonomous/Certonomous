# ADDENDUM to `analyse_t1c.py` — the Richardson-extrapolate sign

**Written 2026-08-24T18:43:26Z** (stamp read from `date -u` in the same shell invocation as
this write — the `bd3edfe8` class rule).
**Owner:** heat-transfer. **Class:** dated amendment under CLAUDE.md rule 6.

**THIS FILE IS A SIDECAR, NOT AN EDIT.** `analyse_t1c.py` is **unchanged**:
sha256 **`60893b28e284127f61b41842c520897a2202cb024d5a4d260272c6ee7e6c5135`**. §4 states why the
amendment cannot be appended inside the file, as rule 6 would otherwise require.

---

## 1. The defect, as coded and as it should be

`analyse_t1c.py`'s `gci()` (line 321 onward) defines `e21 = f_med - f_fine`,
`e32 = f_coarse - f_med`, and returns at **line 337**

    richardson = f_fine + e21 / den        den = R_REFINE ** p - 1.0

Roache / Celik et al. (2008) for this convention give
`f_ext = f_fine + (f_fine - f_med)/(r^p - 1) = f_fine - e21/den`. The coded
form carries **`+` where the derivation gives `−`**, which reflects the
extrapolate through `f_fine` onto the coarse side. `GCI_pct` (which uses
`|e21|`) and the observed order `p` are **unaffected**. The signature is exact:
`frozen + corrected = 2 * f_fine`.

This is the identical expression to `T3_runs/analyse_t3.py:384` and
`T9a_runs/analyse_t9a.py:241`; the sidecar beside `analyse_t3.py` carries the
same finding for T3.

## 2. Every published value this instrument's `richardson` produced, corrected

`analyse_t1c.py`'s `gci()` is imported by `analyse_dts.py`, `analyse_dts_p.py`,
`E4_runs/analyse_e4a.py` (as `T1C`), `E4a2_runs/analyse_e4a2.py` and
`T10aR_runs/analyse_t10aR.py`. Values that reached a record:

| where published | quantity | frozen (printed) | corrected | status |
| --- | --- | ---: | ---: | --- |
| `T1c_RESULTS.md:125` (via `DIAGNOSTIC_PREDICTION.md:12`) | constant-`Ts` Nu, h→0 | 3.6608395 (**+0.1106 %**) | 3.6590762 (**+0.0624 %**) | display-only |
| `T1c_RESULTS.md:125` (via `DIAGNOSTIC_PREDICTION.md:13`) | constant-`q″` Nu, h→0 | 4.3669013 (**+0.0748 %**) | **4.3636945 (+0.0013 %)** | display-only |
| `dts.json` `/ladders/Re100` | Nu, h→0 | 3.6608395 (+0.1106 %) | 3.6590762 (+0.0624 %) | display-only |
| `dts.json` `/ladders/Re200` | Nu, h→0 | 3.6599854 (+0.0873 %) | 3.6584315 (+0.0448 %) | display-only |
| `dts.json` `/ladders/Re50` | Nu, h→0 | 3.6635815 (+0.1856 %) | 3.6624644 (+0.1551 %) | display-only |
| `dts.json` `/ladders/Re25` | Nu, h→0 | 3.6753275 (+0.5068 %) | 3.6752005 (+0.5034 %) | display-only |
| `dts_p.json` `/ladders/Re100_P` (`DIAGNOSTIC_PREDICTION.md:694`) | Nu, h→0 | 3.6594289 (+0.0721 %) | 3.6578682 (+0.0294 %) | display-only |
| `dts_p.json` `/ladders/Re25_P` | Nu, h→0 | 3.6728907 (+0.4402 %) | 3.6722727 (+0.4233 %) | display-only |
| `E4a2_RESULTS.md:106` (R1) | fan `Q` | 1.506878761e-07 | 1.497435362e-07 | already printed **both**, corrected one used |
| `gate_t10a.json` / `gate_t10aR.json` | three rows | printed | printed | already printed **both**, labelled |
| `gate_t3.json` G2 (`analyse_t3.py`) | `x_peak/H` | 6.14027 | 6.142121 | display-only |

**The one substantive movement is the constant-`q″` arm.** Its corrected h→0
excess is **+0.0013 %**, not +0.0748 % — i.e. the extrapolated Nu sits on the
exact constant 48/11 to a part in 10⁵. `T1c_RESULTS.md` §5's reading, *"Both
arms overshoot the exact constant even after Richardson extrapolation … so the
excess is **not** discretisation error"*, therefore **survives for the
constant-`Ts` arm (+0.0624 %, still above its 0.0301 % band) and does NOT
survive for the constant-`q″` arm**, whose corrected extrapolate is consistent
with pure discretisation error. This is recorded as a dated addendum at the foot
of `T1c_RESULTS.md` and of `DIAGNOSTIC_PREDICTION.md`.

## 3. Graded or display-only, read from the grading code

**Every use is DISPLAY-ONLY. No `PASS`, `GATE FAIL`, `GATE REACHED` or
`NOT A RESULT` anywhere in the T-family is a function of a `richardson` value.**
Established by reading the verdict operands, not the prose:

* `analyse_t1c.py:446-452, :464-470` — the verdict is `dev <= band`, where
  `dev` is the **fine-level** value against the reference and `band` is
  `GCI_pct`. `gate_t1c.json` rows carry `value`, `reference`, `deviation_pct`,
  `band_pct`, `order`, `verdict` — **no `richardson` key**.
* `analyse_t9a.py:409-441` (`grade_triple`) — same operands; the triple dict is
  printed, the row stores only `convergence`/`band_pct`/`deviation_pct`/`order`.
* `analyse_dts.py:944` and `analyse_dts_p.py:639` — both comparators print
  **"DIAGNOSTIC, NOT GRADED: no band, no pass/fail, no T1c verdict moves."**
  The `h0_excess_pct` derived from `richardson` feeds a log-log slope and the
  P1/P2/P3 prediction-**consistency** flags in `dts_p.json` — a registered
  non-verdict channel, named here because those flags do move with the sign.
* `analyse_t3.py` — `gate_t3.json` carries no `richardson` key on any row.
* `analyse_t10a.py:611` / `analyse_t10aR.py:146` — already print the **corrected**
  form beside the frozen one; T10a-R's RX5 is registered as *"reported
  diagnostic; grades nothing"* (`T10aR_PREREGISTRATION.md:179, :269`).
* `T1b` / `T1b_L4` (`analyse_t1b_L4.py`) — **NEVER PUBLISHED**: no Richardson
  extrapolate is computed or printed there at all.
* `docs/product/DC_CERTIFICATE_TEMPLATE.md` — **quotes no Richardson value**;
  the template has no `richardson`/`extrapolat` token.

## 4. Why the frozen file is not edited — the citers, enumerated

`analyse_t1c.py`'s sha256 is **registered as a frozen-import identity by other
rungs**, and one citation sits inside an executable refusal:

* **`verification/runs/T-family/E4a2_runs/analyse_e4a2.py:139-141` — REFUSES
  (exit 2) if the file's sha256 differs from the registered value**:
  `refuse(f"frozen instrument {rel} hashes {got}, registered {want}")`.
  The registered table is `E4a2_runs/E4a2_registered.json:355`.
* `verification/runs/T-family/E4_runs/FREEZE_CHECK.txt:18` and
  `E4a2_runs/FREEZE_CHECK.txt:26`
* `verification/runs/T-family/T10aR_runs/gate_t10aR.json:9` (provenance record)
* run logs: `E4_runs/log.analyse_e4a.20260824T160518Z.txt:5, :14`;
  `E4a2_runs/log.analyse_e4a2.20260824T173504Z.txt:15`
* `E4a2_runs/analyse_e4a2.py:32` (docstring identity)
* `docs/campaigns/T-family/E4a_PREREGISTRATION.md:268, :362`,
  `E4a_RESULTS.md:277`, `E4a2_PREREGISTRATION.md:531`, `E4a2_RESULTS.md:341`,
  `T10aR_PREREGISTRATION.md:438`

**One byte changed in `analyse_t1c.py` makes `analyse_e4a2.py` refuse to run and
falsifies six committed pre-registration/results tables.** That is why this is a
sidecar.

## 5. The corrected instrument, already built and in use

`E4_runs/analyse_e4a.py:128` `richardson_corrected(f_c, f_m, f_f, r)`, printed
beside the frozen value at `:356-357` and `:581-583`; imported by
`E4a2_runs/analyse_e4a2.py:29`. Its value-checking selftest control
(`analyse_e4a.py:759-764`, *"corrected vs frozen (sign-defect) Richardson"*)
recovers a synthetic power law's exact limit to 1e-8 relative and asserts the
frozen form does not; `analyse_e4a2.py:575-577` repeats it.
`T10aR_runs/analyse_t10aR.py:383-406` carries four controls of the same class,
including *"richardson_corrected recovers the exact value of a clean power law"*
and *"the shared gci's own richardson carries the registered SIGN DEFECT"*.
`T9a_runs/analyse_t9aD.py:129, :214-242` is a third corrected implementation
with its own paired control.

## 6. Same defect class in two F14 comparators, found by this trace

Not `analyse_t1c.py`'s code, but the identical expression, independently
written:

* `verification/runs/F14-cooling-ladder/K0cG_runs/analyse_k0cg.py:107` —
  `rec["richardson_extrapolate"] = f1 + e21 / den` with `f1` the **finest**
  and `e21 = f2 - f1`. Its five `kOmegaSST` extrapolates in `gate_k0cg.json`
  are wrong on the same side; the comparator prints **"GRADES NOTHING. No K0cS
  verdict moves."** (`:142`) and no K0cG record quotes a value — status
  **NEVER PUBLISHED (in a record)**, defective in the JSON.
* `verification/runs/F14-cooling-ladder/K0cX_runs/grid_convergence.py:106` —
  same form. Its one CONVERGING row is `kOmegaSST`'s stratification `S`:
  finest **0.23105658418258596**, printed extrapolate **0.2365**, corrected
  **0.22560**. `docs/campaigns/F14-cooling-ladder/K0cX_GRID_CONVERGENCE.md:100`
  publishes 0.2365 — **PUBLISHED DISPLAY-ONLY**; a dated addendum at that
  file's foot records the correction. The reading survives: 2.61 band-widths
  from the measured 0.095 instead of 2.83, still "refining to infinity does not
  reach the experiment".

**Not defective, checked and cleared:** the three `K0b` instruments
(`K0b_mesh_sensitivity/`, `K0b_D403_rerun/`, `K0b_D406_repair/analyse_k0b_mesh.py:310-321`)
use `ext = f3 + d32/(r^p - 1)` with `f3` fine and `d32 = f_fine - f_med` — the
**correct** Roache form. K0b's published extrapolate 4.52001514525647 stands.

**Outside this trace's territory, flagged not adjudicated:**
`verification/runs/F9_work/f9_criteria.py:527` and
`verification/runs/4G_runs/bump_iteration_matched/ladder.py:64` carry an
`f + e/(r^p - 1)` form whose sign depends on how their `e` is defined. They are
cfd/verification territory and were **not** read to a verdict here.

## 7. Provenance

Verification audit pass 9 §66 (`eab2f6c5`), supervisor's own read §72
(`a82a8d76`) — which named the T1c exposure explicitly as unestablished and
routed it to heat-transfer. Traced and recorded here on 2026-08-24.
Earlier record of the same class: `T9a_RESULTS.md` §8 item 1.
