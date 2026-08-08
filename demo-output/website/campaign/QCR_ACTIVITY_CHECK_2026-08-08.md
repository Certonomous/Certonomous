# QCR activity check on the two null legs — adversarial verification, 2026-08-08

Ordered by the chief supervisor against the provisional three-leg class
sentence ("QCR2000 resurrects anisotropy-driven secondary flow and does not
touch 2D separated-shear-layer bubble length"; hold at review entries 1–2,
`cf14dbe3`). Executed by the Cases family supervisor, who ran neither
original arm. Brief: assume the two separated-class nulls (hump +0.0022 x/c,
hills +0.034 x/h) are silent no-ops until defended. **Zero solver core-min:
everything below is read from archives and source.**

## VERDICT: ACTIVE on both legs — the nulls are real physics, and the class sentence hardens

The QCR term was demonstrably live in both null runs: the model was selected
at runtime with its own coefficient banner, its nonlinear stress is wired
into the momentum equation at cited source lines, and the flow fields differ
from the SST counterparts by 2–19% in the compared quantities on
bit-identical meshes — five to seventeen orders of magnitude above roundoff
— while the reattachment point stayed put. That combination (fields move,
bubble length does not) is precisely what "the null is physics" looks like.

## Check 1 — model selection, per leg

| leg | case dict | solver log |
| --- | --- | --- |
| hump QCR (`W1_hump_runs/sst_qcr/`) | `turbulenceProperties`: `RASModel kOmegaSSTQCR` | `log.simpleFoam:71` "Selecting RAS turbulence model kOmegaSSTQCR"; printCoeffs banner lines 73–94 incl. **`Ccr1 0.3`** (line 94) |
| hump SST control (`W1_hump_runs/sst/`) | `RASModel kOmegaSST` | `log.simpleFoam:71` "Selecting RAS turbulence model kOmegaSST" |
| hills QCR (`F6b_runs/medium_qcr2000/`) | `constant/turbulenceProperties`: `RASModel kOmegaSSTQCR` | `log.simpleFoam:61` selection line; **`Ccr1 0.3`** at line 84 |
| hills SST control (`F6b_runs/medium/`) | `constant/turbulenceProperties:22`: `RASModel kOmegaSST` | (2026-08-05 gate record) |

Both QCR controlDicts load the lab-built library:
`W1_hump_runs/sst_qcr/controlDict:26` and
`F6b_runs/medium_qcr2000/system/controlDict:4`, both
`libs ( "libkOmegaSSTQCRTurbulenceModels.so" )`. A runtime "Selecting …
kOmegaSSTQCR" line is only printable if that library loaded and the class
registered — selection is proven from the run's own log, not inferred.

## Check 2 — fields differ far beyond roundoff, reattachment does not move

**Hump (622 wall faces, x-grids identical after sort, deltas computed
face-by-face):**

| quantity | SST vs QCR | scale |
| --- | --- | --- |
| wall tau_x | max \|delta\| 0.1514, rms delta 0.0311 | **8.97% max / 1.84% rms** of rms(tau_x,SST) = 1.689 |
| cf_min (peak reverse-flow Cf) | −0.0014505 vs −0.0013172 | 9.2% |
| cp_min / cp_max | −0.81301 vs −0.80740 / 0.31883 vs 0.31286 | 0.69% / 1.9% — **pressure-based, independent of any stress definition** |
| skin-friction sign changes | 4 vs 4, positions shifted | bubble topology unchanged, reattachment +0.0022 x/c |

**Hills (meshes bit-identical: `constant/polyMesh/points` md5
`2e9d541060045960e7a44852be397483` in both cases; SST at t=5997, QCR at
t=6177):**

| quantity | SST vs QCR | scale |
| --- | --- | --- |
| bottomWall tau_x | max \|delta\| 4.11e-4, rms delta 1.19e-4 | **18.8% max / 5.45% rms** of rms(tau_x,SST) = 2.18e-3 |
| nut (internal field) | max \|delta\| 1.90e-3 | rms delta = **1.54%** of rms(nut,SST) |
| U (internal field) | max \|dU\| 0.0352, rms 7.98e-3 | **4.9% of Ubar = 0.72** at max |
| separation / reattachment | 0.2604 → 0.2652 / 7.6472 → **7.6814** | +0.034 x/h (+0.45%) — the null as recorded |

No compared field pair is bit-identical anywhere. The definitional confound
is closed on both legs: `wallShearStress` diagnostics use the model's own
`devRhoReff`, which QCR overrides (see check 3), so a tau delta alone could
in principle reflect the stress *formula* rather than the flow — but the
hills U and nut internal fields (formula-independent) differ by up to 4.9%
of Ubar, and the hump's Cp extrema (pressure, formula-independent) differ by
0.7–1.9%. **The flow itself was different. The model was demonstrably
active, with numbers.**

## Check 3 — the QCR term is in the momentum equation, at file:line

- `sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C:142-154` — the
  `divDevRhoReff(volVectorField& U)` override returns
  `kOmegaSST<...>::divDevRhoReff(U) - fvc::div(this->alpha_*this->rho_*qcrStress())`:
  the nonlinear stress divergence is added to the momentum matrix itself,
  not to a diagnostic. (Density-explicit overload at `:159-170`;
  declarations `kOmegaSSTQCR.H:115-124`.)
- `sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C:40-61` — `qcrStress()`
  builds `tau_nl = −Ccr1·symm(O·tau_l − tau_l·O)` (QCR2000, rotation tensor
  O from the normalized antisymmetric velocity gradient, Boussinesq
  deviatoric `tau_l = nut·devTwoSymm(gradU)`).
- The call chain in these exact incompressible runs:
  `simpleFoam/UEqn.H:9` `+ turbulence->divDevReff(U)` →
  `src/TurbulenceModels/incompressible/IncompressibleTurbulenceModel/IncompressibleTurbulenceModel.C:123-129`
  `divDevReff(U) { return divDevRhoReff(U); }` → the override above
  (alpha = rho = one-fields in the incompressible instantiation). Sources
  read from the installed `/usr/lib/openfoam/openfoam2606` tree.
- `kOmegaSSTQCR.C:124-137` also overrides `devRhoReff` (subtracting
  `qcrStress()`), so force/wall-shear outputs are consistent with the
  corrected momentum equation — the ducts' 0.0004 agreement with Wu&Zhang
  already evidenced the term's correctness; these lines plus the check-2
  field deltas evidence that it was **live on the two null legs
  specifically**.

## Consequence

Per the brief's own rule: fields differ materially, reattachment does not
move → **the nulls are real physics on both separated legs, and the
three-leg class sentence stands on its evidence.** The hold at review
entries 1–2 is the chief's to lift; this record changes nothing in the
review file and edits no leg's own records. Cost: 0 solver core-min.

## 2026-08-08 addendum — the hills SST control leg's citation gets its log line (dead-lever audit `DEAD_LEVER_AUDIT_2026-08-08.md`, 946e4a26)

The check-1 table's hills SST control row cited "(2026-08-05 gate record)"
without a solver-log line, because `F6b_runs/medium/` keeps no `log.simpleFoam`.
The audit located the run's genuine log in the solve registry:
`demo-output/website/solve_registry/f6b2_medium_20260805T171046Z.log:50`
"Selecting RAS turbulence model kOmegaSST", whose `Case` header names
`campaign/F6b_runs/medium`. All four legs of check 1 now carry runtime
selection lines; nothing else in this record changes.
