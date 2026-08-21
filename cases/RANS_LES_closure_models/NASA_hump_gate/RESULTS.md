# RESULTS — NASA hump equivalence gate: **PASS**, on the registered branch

Preregistration: `PREREGISTRATION.md` in this directory, frozen and posted before
any solve. Registered decision rule, applied: **B-G0a BLOCKED and B-G0b PASS ->
the hump row becomes scorable comparably**, and dated appended notes are written.

| gate | registered band | measured | **VERDICT** |
|---|---|---|---|
| **B-G0a** fixed-iteration behavioural equivalence | rel-L2(`U`) < 1e-6 after 200 identical iterations | **not computable** — the shipped model cannot be instantiated here | **BLOCKED** (the registered branch, not a failure) |
| **B-G0b** converged NULL vs the published row | \|`U_rms` − 0.1260\| < 5e-3 | **0.1261769**, Δ = **1.77e-4** | **PASS** |

## 1. B-G0a — BLOCKED, and exactly why

Running the shipped case with its own `constant/turbulenceProperties` untouched,
on this machine:

```
--> FOAM FATAL IO ERROR: (openfoam-2606)
Unknown RAS model type AugmentedkOmegaSST
```

`rc` = 1 after 15.0 s, no time directory written. The shipped `controlDict` names
`libfrozenIncompressibleTurbulenceModels.so`, which is **not present on this
machine**, and `AugmentedkOmegaSST` lives in it. The preregistration anticipated
this and registered it as **BLOCKED, not GATE FAIL**: a model that cannot be
loaded cannot be shown to differ from anything.

The other half ran cleanly: `kOmegaSSTCorrected` with `bijDelta = 0`,
`kDeficit = 0`, `omegaMin 0.1` and the shipped `fvOptions` completed its 200
iterations in 45.0 s and wrote time 2200. **So the failure is one-sided and is a
property of this machine's library set, not of either model.**

## 2. B-G0b — PASS, and it is a tight pass

| quantity | value |
|---|---|
| state | **CONVERGED-residualControl** (`p` and `U` initial residuals < 1e-6) |
| iterations | **156** of a 5,000 cap |
| wall | 38.6 s, single core |
| `U_rms` | **0.1261769** |
| published row (`BASELINES.md` §3, `NASA_2DWMH`) | **0.1260** |
| **Δ** | **1.77e-4** against a registered band of 5e-3 |
| `U_mae` | **0.0621203** vs the published **0.0620** (Δ 1.2e-4) |
| RMS `div(U)` / gradient scale | 1.86e-3 |

The band was widened to 5e-3 before running, and justified there: the same test
gave 2.4e-4 on `AR_1_Ret_360` but **1.92e-3 on `AR_3_Ret_360`, where it failed a
1e-3 band purely through drift of the shipped field under further iteration**. The
hump did not need the room. **1.77e-4 would have passed the original 1e-3 band
too**, and `U_mae` — a second, independent quantity that carried no registered
band — lands 1.2e-4 from its published value as well.

That the solve **converged in 156 iterations** is itself evidence: restarted from
the shipped converged field, `kOmegaSSTCorrected(0,0)` had almost nothing to do.
A model that differed from the one that produced that field would have had to
move it.

## 3. What the gate establishes, and the strength of the inference

`log.run` line 153 selects `AugmentedkOmegaSST` and prints its full coefficient
dictionary: `baseline true`, `usekDeficit false`, `usebijDelta false`,
`useSigma false`, `modelbijDelta false`, `modelkDeficit false`,
`modelSigma false`, and every printed coefficient the stock Menter SST value
(`alphaK1 0.85`, `alphaOmega2 0.856`, `gamma1 0.555556`, `beta1 0.075`,
`betaStar 0.09`, `a1 0.31`, `b1 1`, `c1 10`, `F3 false`). It is a SpaRTA-style
corrected SST **run with every augmentation switched off**.

The gate shows: **a solver that is bit-identical to stock `kOmegaSST` at zero
correction, restarted from the shipped hump field, converges in 156 iterations to
a velocity field 1.77e-4 from the published `U_rms` and 1.2e-4 from the published
`U_mae`.** Combined with the printed dictionary, that is behavioural equivalence
at the operating point of interest.

**The chain is: `kOmegaSSTCorrected(0,0)` = stock `kOmegaSST`** — measured at
rel-L2 **0.0 exactly**, bit-identical, on `AR_1_Ret_360`
(`../Kaandorp2020_TBRF/aposteriori/RESULTS.md` §1) — **and stock `kOmegaSST`
reproduces the shipped hump baseline to 1.77e-4.** Each link is measured.

## 4. Consequence: the hump becomes scorable comparably

Under the registered rule, dated appended notes were written to:

* `_common/FEASIBILITY.md`
* `Wu2018_PIML_RF/aposteriori/RESULTS.md` (the `NASA_2DWMH is BLOCKED` bullet)
* `Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md` (the `NASA_2DWMH remains BLOCKED` bullet)

**Appended dated notes only. No frozen text was edited anywhere.**

`Xiao2016_EnKF/RESULTS.md` was named in the brief but **contains no
BLOCKED-hump line** — that lane never touched the hump, and inventing a line there
to append a note to would be manufacturing a record. Nothing was written to it.

## 5. What this gate CANNOT see

* **It cannot inspect the source.** `AugmentedkOmegaSST` is private and could not
  even be loaded here. Equivalence is behavioural, on one case, from one restart,
  at one operating point.
* **B-G0a — the stronger, two-sided test — was never run.** A one-sided
  reproduction of a published scalar is weaker evidence than a
  trajectory-by-trajectory comparison, and the registered rule let B-G0b decide
  alone only because the other side was impossible, not because it was redundant.
* **A pass shows agreement at zero augmentation on this case**, not that the two
  models agree with augmentation on, nor anywhere else.
* **Serial here against the shipped parallel run**, and OpenFOAM v2606 here
  against the case's OpenFOAM-7-era provenance in `log.run`'s paths.
* **The `limitVelocity` `fvOptions` source is active on all 51,626 cells** and was
  carried unchanged. Both sides inherit it, which makes the comparison fair and
  also blind to the limiter itself.
* **`omegaMin 0.1` was carried** into the corrected model's dictionary because the
  shipped dictionary sets it. Whether `kOmegaSST` in v2606 honours that key was
  not separately verified; if it silently ignores it, the two models differed in
  `omegaMin` and still agreed to 1.77e-4, which strengthens rather than weakens
  the conclusion.
* **Gate-only contact.** No LES/DNS quantity other than `U_rms` and `U_mae` was
  touched, and nothing from the hump enters any other lane's fit.

## 6. Compute

| item | core-hours |
|---|---|
| B-G0a, both sides (15.0 s + 45.0 s) | 0.017 |
| B-G0b converged NULL (38.6 s) | 0.011 |
| **Part B total** | **0.028** |

Part A was pure numpy on frozen fields. Lane total in §7 of `../_common/uq_eigenspace/UQ_EIGENSPACE.md`
and in the final report; the 10-core-hour cap was never approached.
