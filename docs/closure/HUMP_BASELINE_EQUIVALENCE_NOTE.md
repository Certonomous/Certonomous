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

---

## WITHDRAWAL OF ATTRIBUTION — 2026-08-25. APPENDED AT THE FOOT.

**Appended 2026-08-25T00:39:39Z (box clock, read in the writing invocation) by a
closure lane at the closure supervisor's direction. Version 1.0 → 1.1.
lines whose number changed above this section: 0.**

**Proved, not asserted.** The pre-append prefix is bytes 1–3099 (59 lines); sha256
`bb3e1cb8d5f3e784b7a5fad623ea6d40360f149dbe3803b7076edc74b35bc6f2` before this block
was written and the identical value after, and byte-identical to this file's blob at
HEAD `72bc966d`. Nothing above this line was edited, renumbered or reflowed. **The
block is at the FOOT** — L-304: an in-file "0 lines changed above" assertion
certifies only what is above it.

**Status term: `ATTRIBUTION WITHDRAWN — TEXT STANDS AS A RELAYED PARAPHRASE`** —
deliberately not one of `CLAUDE.md` rule 1's six verdict words; no gate is graded here.

### What is withdrawn

Line 3–4 of this note reads *"Investigated at Sanaa's request"* and quotes:

> can you pull the benchmark repo / any other repo this might be coming from and check?

**The attribution is WITHDRAWN. The text stands as a relayed paraphrase** — wording
that reached the closure team through an agent brief, not established as Sanaa's
verbatim words. The text above is **kept exactly as written** and is not altered or
struck.

**Why.** Under a non-ignoring `find <abs-path> -type f | xargs grep -F` across the
whole worktree, that sentence exists in **exactly one file: this one.** It names no
session, no message and no source document — the three things the 2026-08-21 R3
appendix in `docs/closure/R2_SHORTLIST_MEMO.md` does name, and which is why that
attribution stands and this one does not.

**Control fired on the negative** (rule 3, applied to a documentary search): on the
identical apparatus, over the identical file list, *"bands-vs-corrections"* returned
**7 files** and *"R3: Sparta"* returned **6**. The apparatus can see. It does not see
this sentence anywhere but here.

**Class: SELF-ASSERTED ONLY** (audit class **C UNSOURCED**).

### What this is, and what it is not

- **Against closure's own favour**: it removes the stated warrant for this
  investigation having been commissioned.
- **NOT a claim the words are not Sanaa's.** She may well have asked exactly this.
  The finding is only that closure cannot source it and will not vouch for it.
- **REVERSIBLE the moment Sanaa confirms**, in one line, with nothing else re-opened.
- **Nothing in the note's finding depends on it.** The equivalence result —
  `NASA_2DWMH`'s baseline being stock `kOmegaSST` — rests on files and a proof on
  disk, not on who asked for the check. **No verdict, gate or number moves.**

### Scope

Records only. **Zero compute: 0.0 core-minutes.** Nothing sent, filed, uploaded,
registered, posted or commented — **SUBMISSIONS PARKED** stands. Owner: closure.
