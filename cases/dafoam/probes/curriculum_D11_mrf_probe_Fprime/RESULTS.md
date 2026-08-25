# D11-F′ — THE CLI RE-BUY — RESULTS

## 1. Verdict

**`GATE REACHED`.** DAFoam's **MRF rotating-frame formulation reaches the adjoint** on
image `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`, and on
this configuration the MRF-active adjoint agrees with a central finite difference to
**1.70e-07 relative**.

Pre-registration frozen `57c4a516`; grading path `d11f_grade.py` md5
`0618094c0f63a94e23d9dfc1ecc2fa6b`, verified against the HEAD blob before the launch.
**No amendment; nothing changed after the freeze.**

## 2. Gates, all six

| gate | verdict | measured |
|---|---|---|
| **G11-1** | `PASS` | MRF-active primal completed; `TPIn(ω=30) = 1.1859858226e+00`, `TPIn(ω=0) = 1.1836719785e+00` |
| **G11-2a** | `PASS` | clean copy reproduces `ω=0` to **`0.000e+00`** relative (tol `1.0e-12`) |
| **G11-2b** | `PASS` | **MRF-zone plant response `1.954802e-03`**, floor `1.0e-6` |
| **G11-3** | `PASS` | `max |d(TPIn)/d(patchV)| = 2.3058711101e-01` over **2** components: `[2.3058711101e-01, −1.3660119098e-04]` |
| **G11-4** | `PASS` | adjoint differs `ω=30` vs `ω=0` by `6.055922e-04` relative L2 — **DIAGNOSTIC, necessary and not sufficient** |
| **G11-5** | `PASS` | **MRF-ON adjoint vs central FD, `h = 1.0e-3 m/s`: adj `2.3058711101e-01`, FD `2.3058707170e-01`, relative error `1.704895e-07`**, band `5.0e-2` |

All five stages `rc = 0`, `OOMKilled false`. Plant read-back on disk: `omegaP` and the
two FD stages carry `omega 30.0;`, `omega0` and `clean` carry `omega 0.0;`.

## 3. The named failure mode did NOT occur

The curriculum's D11 row names *"MRF interface derivatives silently zero"*. **It did not
happen.** The MRF-active derivative is `2.3058711101e-01`, eleven orders above the
`1.0e-12` floor, and it is not bit-identical to the MRF-inert one. **G11-5 is the load-
bearing gate** — a linearisation that had dropped the MRF term from `dR/dW` would
disagree with FD, and it agrees to seven digits.

**The registered terminology correction stands and should be carried into D11's own
prereg:** in this build MRF is a **cell-zone** formulation (`IOMRFZoneListDF`;
`DAResidualSimpleFoam.C:39–40, :144 MRF_.DDt(U_), :183 makeRelative, :199
constrainPressure, :246 correctBoundaryVelocity`), **not an interface**. There is no MRF
interface object to plant on; the zone's `omega` is the parameter that switches the whole
contribution on and off, and DAFoam reads it as a **scalar `omega` in rad/s, not `rpm`**
(`MRFZoneDF.C:217`).

## 4. What this does NOT establish

Reachability only. **It establishes nothing about MRF at engineering rotational rates** —
it is a statement about a **30 rad/s** zone on a 720-cell 2D channel. `G11-5` says only
that on this one configuration, this one component, adjoint and central FD agree inside
the band. Nothing about AMI or sliding interfaces, `DATurboFoam`, MRF as a design
variable (DAFoam 5.0.0 ships **no** `DAInput` class for MRF), or any real rotor at scale.

**The measured fact that a 300 rad/s zone STALLS this steady substrate stands**
(`../curriculum_D11_mrf_probe_Dprime/RESULTS.md` §3) and must be carried into D11's own
pre-registration, which will need a rotating-frame-appropriate case or an unsteady
formulation.

## 5. Cost

| | |
|---|---|
| predicted | **0.85 core-min** (measured basis: D11-O′'s identical five stages at 0.7167 with `fdm` dying in `argparse`) |
| actual gross | **0.7501 core-min** |
| ratio | **0.883×** |
| cap | 5.0 core-min; **`0.150×` of cap**, guard never fired |
| derived | **$0.000641 DERIVED, NOT MEASURED**, $0.0513/core-h c7a.4xlarge, reported-by-owner |
| waste | **0.000 core-min on this row.** The chain's prior 2.2667 core-min is named separately and is **not** absorbed into this ratio |

Calibration row **C-69**.

## 6. What D11 proper now has

The Tier-4 D11 row's `PROBE FIRST` prerequisite is **discharged**. **The row remains
`UNPRICED`** — see `../LANE_REPORT.md` §6 for why, and for the anchor this probe
delivered toward its costing.
