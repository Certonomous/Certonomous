# The hump baseline is stock kOmegaSST in disguise, and equivalence is provable

**Dated 2026-08-21. Investigated at Sanaa's request ("can you pull the
benchmark repo / any other repo this might be coming from and check?").**

## The finding

`NASA_2DWMH` is the one benchmark case whose `constant/turbulenceProperties`
names `RASModel AugmentedkOmegaSST` from
`libfrozenIncompressibleTurbulenceModels.so`, a library that exists nowhere on
this machine and whose source is not public. Every a-posteriori lane therefore
shipped the hump BLOCKED rather than substitute a non-comparable baseline.

The case's own `log.run` resolves it. With `printCoeffs on`, the shipped run
prints the model's full dictionary at selection:

- `baseline true;`
- `usekDeficit false; usebijDelta false; useSigma false;`
- `modelbijDelta false; modelkDeficit false; modelSigma false;`
- every remaining coefficient numerically identical to stock `kOmegaSST`
  (alphaK1 0.85, alphaK2 1, alphaOmega1 0.5, alphaOmega2 0.856,
  gamma1 0.555556, gamma2 0.44, beta1 0.075, beta2 0.0828, betaStar 0.09,
  a1 0.31, b1 1, c1 10, F3 false), plus stabiliser/ramp knobs
  (`bijDeltastabilizer 1; kDeficitstabilizer 1; rampStartTime 0;
  rampEndTime 100; xi_ramp 1`) that are inert with the flags off.

So `AugmentedkOmegaSST` is a SpaRTA-style corrected SST — the same
`kDeficit`/`bijDelta` interface as this lab's `kOmegaSSTCorrected` — and **the
shipped hump baseline was produced with the augmentation entirely off:
behaviourally stock kOmegaSST.**

## Where the source lives, and why that no longer matters

The log's case path (`/home/openfoam/TurbFOAM-7-Cases/...`) points at a private
tree. Searched without result on 2026-08-21: the GitHub API over all twenty of
the benchmark author's repositories (no path matching augmented/frozen/
turbulence-model), GitHub repository search for the class and library names
(zero hits), and grep.app. The source is treated as unobtainable.

It is also unnecessary. The lab already proved, twice and bitwise, that
`kOmegaSSTCorrected` with zero corrections is identical to stock `kOmegaSST`
over a same-start fixed-iteration run (G0a gates, rel-L2 = 0.0 exactly). The
registered path to an equivalent hump baseline is therefore:

1. run the shipped hump case under `kOmegaSSTCorrected(0,0)` from
   `libspartaTurbulenceModels.so` (inserting, not replacing, the `libs` entry —
   see the Parm_PH_29 lesson);
2. gate on a G0a-style same-start comparison against stock `kOmegaSST` and on
   reproducing the BASELINES hump row;
3. only then score corrected configurations against that baseline.

**What this cannot see:** whether the private `AugmentedkOmegaSST` deviates
from stock SST in some code path not exercised by the shipped baseline run
(e.g. with augmentation on). Equivalence is claimed only for the
baseline-off configuration, and only as far as the registered gate measures it.

Recorded for: the Wu2018/Kaandorp/Xiao BLOCKED-hump rows (dated notes to be
added by the closure team), FEASIBILITY.md, and the R4 build ladder, whose
all-eight-cases requirement this unblocks.
