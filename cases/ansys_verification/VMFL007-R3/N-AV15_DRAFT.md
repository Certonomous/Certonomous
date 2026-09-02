# DRAFT for `docs/NUMERICS_KNOWLEDGE.md` — proposed `N-AV15`

**DRAFT. NOT LANDED. Written by `ansys-lane-opus` 2026-09-02 at the supervisor's
instruction; the supervisor lands it.** Nothing below is a verdict, and no
pre-registration, register row or gate is touched by it.

**Two things the lander must do, which this draft cannot do for itself:**

1. **RE-DERIVE THE NUMBER AT COMMIT (rule 11).** `N-AV15` is proposed from the
   tail as of 2026-09-02: `grep -rhoE '\bN-AV[0-9]+' docs/ | grep -oE '[0-9]+' |
   sort -n | tail -1` returns **14**, so the next id is 15. That is the **maximum
   existing number, not a count** — and peers commit constantly, so re-derive in
   the same shell invocation as the commit and renumber if it has moved.
2. **REGENERATE THE FAMILY INDEX AS A SUPERSEDING BLOCK.** Append this entry at
   the file tail, edit nothing above it, then regenerate a fresh `FAMILY INDEX`
   block with `scripts/check_numerics_index.py --gen` and the file's standing
   assertion — `lines whose number changed above this block: 0`, with the md5 of
   the pre-append prefix taken before and after the write.

---

## N-AV15. A steady SIMPLEC solve of a power-law fluid on a wedge-axis pipe lands in a PERSISTENT, LOCALISED, SINGLE-CELL LIMIT CYCLE in the entry region: the field is converged to 1e-09 everywhere else, the gate functional has a FLOOR rather than a plateau, and the phenomenon is ABSENT at 25×25 and 50×50 and PRESENT at 100×100 — MEASURED

**2026-09-02, ansys-verification. MEASURED, this session, 90 000 iterations.**

### The configuration

VMFL007 (non-Newtonian pipe, manual p. 29) as a 2-D axisymmetric **wedge of 1°
total angle**, pipe `L = 0.1 m`, `R = 0.00125 m`, uniform radial grading.
`simpleFoam`, **SIMPLEC** (`consistent yes`, `nNonOrthogonalCorrectors 0`,
relaxation `p 1.0` / `U 0.9`), `p` PBiCGStab/DIC `relTol 0.01`, `U`
smoothSolver/symGaussSeidel `relTol 0.1` `nSweeps 2`, `div(phi,U) bounded Gauss
linear`. Transport: `viscosityModels::powerLaw`, `k = 0.01` **kinematic**
(`= k_manual/ρ = 10/1000`), `n = 0.4`, `nuMin 1e-08`, `nuMax 1.0`. Inlet is the
**fully developed power-law profile** imposed by coded BC (mean 2 m/s, peak
3.1429 m/s). Levels 25×25 (625 cells), 50×50 (2 500), 100×100 (10 000).

### 1. The swing does not decay — it is a stationary limit cycle, not a transient

`max(nu)` over the domain, peak-to-peak in consecutive 5 000-iteration windows,
100×100, stitched across an original 0→30 000 leg and a 30 000→90 000 restart:

| window ends at | `max(nu)` ptp | `max(nu)` mean | Δp ptp (Pa) |
|---|---|---|---|
| 5 000 | 0.999522 | 0.030633 | 2.18e+07 |
| 10 000 | 0.544269 | 0.130062 | 22.71 |
| 15 000 | 0.099213 | 0.254612 | 1.2139 |
| 20 000 | 0.377772 | 0.330625 | 0.138778 |
| 25 000 | 0.415403 | 0.344830 | 0.020108 |
| 30 000 | 0.426881 | 0.345126 | 0.005826 |
| 35 000 | 0.435138 | 0.344606 | 0.002328 |
| 40 000 | 0.434938 | 0.344452 | 0.001729 |
| 50 000 | 0.434817 | 0.344407 | 0.001446 |
| 60 000 | 0.435102 | 0.344316 | 0.001535 |
| 70 000 | 0.435104 | 0.344370 | 0.001474 |
| 80 000 | 0.434820 | 0.344334 | 0.001495 |
| 90 000 | 0.434899 | 0.344371 | 0.001454 |

The amplitude is **flat from iteration 25 000 to 90 000** and the mean is steady
to four figures at 0.3443. Least squares on `ln(ptp)` against iteration over
windows past 30 000: **slope +1.184e-07 per iteration, r² = 0.17** — no trend.
**There is no settling iteration to extrapolate to, because there is no decay.**

### 2. The planted control that makes the null admissible

*"It does not decay"* is a **negative finding**, and a fit that cannot detect decay
proves nothing by failing to. Known exponential decays were injected into the real
series and the **same** fit re-run:

| planted half-life | recovered by the fit | slope | r² |
|---|---|---|---|
| 20 000 iterations | **20 967** | −3.306e-05 | 0.9921 |
| 60 000 iterations | **64 472** | −1.075e-05 | 0.9904 |
| — (real series) | **none — no decay** | +1.184e-07 | 0.1737 |

The instrument sees decay when decay is present. It sees none here. **This is
rule 3's planted-zero control transposed onto a null result, and a negative
convergence finding reported without it is not evidence.**

### 3. It is ONE CELL REGION, not "the near-axis field" — the part that matters

Fixed-point probes on `nu`, peak-to-peak over the last 5 000 iterations at 90 000:

| probe | location | `nu` at 90 000 | ptp over last 5 000 |
|---|---|---|---|
| 0 | axis cell, `x = 0.0175` (entry region) | 0.20746 | **0.4484** |
| 1 | axis cell, `x = 0.05` (mid-pipe) | 0.048795 | **8.28e-09** |
| 2 | axis cell, `x = 0.09` (near outlet) | 0.053199 | **9.07e-09** |
| 3 | mid-radius, `x = 0.05`, `r = 6.25e-04` | 1.1983e-04 | **2.60e-14** |

**Nine to sixteen decades quieter.** The oscillation is confined to the axis cell
in the **entry region**; the axis cells at mid-pipe and outlet are converged. A
plant control fired on all three quiet probes (a +10 % spike at a named window
index raises their ptp by five to nine orders), so the near-zeros are readings and
not blindness.

### 4. The reduced quantity is NOT a valid convergence instrument on its own

`max(nu)` is a **reduction whose argmax cell can move**, so a wandering maximum may
be an artifact of the reduction rather than of any cell. **Measured, not
hypothesised:** the argmax was **cell 17 at `r = 8.333e-06 m`** at iteration
30 000 and **cell 217 at `r = 3.167e-05 m`** at iteration 90 000. It moved. Every
reduced quantity used as a convergence instrument must be paired with a
fixed-point probe before its time series is read as a plateau.

### 5. The gate functional has a FLOOR, not a plateau

Δp peak-to-peak falls 22.71 → 1.214 → 0.1388 → 0.0201 → 0.00583 → 0.00233 Pa and
then **stops**, sitting at 0.00145–0.00153 Pa from iteration 40 000 to 90 000
without improving. Δp is a global integral and is insensitive to a single cell, so
its floor is small — **1.5e-03 Pa, i.e. 2.4e-08 relative** — but it is a floor set
by the oscillating cell and not a convergence to a point. **A plateau criterion
written as `ptp → 0` is unsatisfiable against a limit cycle and must never be
written; a criterion is a stated threshold on a stated window on a named channel,
fixed before compute.**

### 6. Refinement-triggered: absent at 25×25 and 50×50, present at 100×100

Same arm, same physics inputs, `max(nu)` ptp over the last 5 000 iterations:

| level | cells | `max(nu)` ptp | last `Ux` initial residual | last `p` initial residual |
|---|---|---|---|---|
| 25×25 | 625 | **3.69e-12** | 2.42e-14 | 4.10e-12 |
| 50×50 | 2 500 | **4.55e-10** | 6.45e-14 | 9.13e-12 |
| 100×100 | 10 000 | **0.4349** | 3.07e-09 | 1.47e-08 |

Nine orders of magnitude between L2 and L3. The two coarser levels converge to
machine precision; the finest does not. One weaker precursor is on record at
50×50: `max(nu)` touched the `nuMax` limiter transiently at iterations 4807–4817,
mid-run, and then settled — the only mid-run excursion at any level.

### 7. The limiters are not implicated, and the clip headroom must be quoted over the cycle

Across all 90 000 iterations the `nuMax = 1.0` limiter is touched **18 times, all
at iterations 1–18**, last touch at iteration 18; `nuMin` never. The discrete field
at 90 000 has **zero clipped cells** at either limb (plant fired). So the limit
cycle is **not** a limiter artifact.

But the exposure figure must be taken over the cycle, not from a snapshot: the
domain max ranges **0.2034 … 0.6400** over iterations 30 001–90 000, giving
**1.56× headroom to `nuMax`**, against snapshot values of 2.45× at iteration
30 000 and 4.34× at iteration 90 000. **A single snapshot understates the exposure
by up to 2.8×.**

### 8. What is OPEN — stated as open, not as caveat garnish

- **Mechanism undiagnosed.** Whether this is physical (an entry-region adjustment
  because the imposed analytic profile is not the discrete solution of the
  discretised equations) or a **wedge-axis discretisation artifact** is not
  determined. The axis `nu` is not uniform along `x` even in the quiet region
  (0.0488 at mid-pipe against 0.0532 near the outlet), which is consistent with a
  genuine entry adjustment, but that is an observation and not a diagnosis.
- **Not tested at 200×200.** Whether the limit cycle persists, grows or disappears
  under further refinement is unmeasured.
- **No comparison arm exists at this level.** The SIMPLE arm (`consistent no`,
  `p 0.3` / `U 0.7`, otherwise identical) **diverges with SIGFPE at 50×50 at
  iteration 13 274** and therefore cannot be run at 100×100 at all, so whether the
  limit cycle is SIMPLEC-specific is **unknown and not testable with this arm set**.
- The lane did not test whether a `div` scheme change, a non-orthogonal corrector
  or an axis-cell refinement removes it. No such lever was tried.

### Provenance

**MEASURED**, `verification/runs/ansys_verification/VMFL007-R3-DIAG/` —
`L3_100x100_B2/` (0→30 000) and `L3_100x100_B2_ext_90k/` (30 000→90 000, `rc 0`,
one `End`, last time 90 000, `ExecutionTime` count 60 000, 1 716 wall-s serial =
28.60 core-min), with `L1_25x25_B2/`, `L2_50x50_B2/` and the SIMPLE negative
control `L2_50x50_A5_control/`. Probe series at
`L3_100x100_B2_ext_90k/postProcessing/nuAxisProbes/30000/nu`. Instruments:
`cases/ansys_verification/VMFL007-R3/analyse_L3_plateau.py` (windowing, decay fit,
planted-null control) and `read_nu_clip.py` (discrete field reader, planted clip
control). **That tree is a DIAGNOSTIC tree and is deliberately untracked; it is
cited by absolute path because run outputs are not committed in this lab.**

**Two open defects in the instruments, recorded with the entry rather than
silently carried** (neither moves any number above, because both legs are stitched
explicitly by the caller): `analyse_L3_plateau.py` hardcodes the `ρ = 1000`
conversion instead of reading it from `transportProperties`, and its `leg()` helper
selects a `postProcessing` sub-directory with `sorted(glob(...))[0]` — **a
lexicographic sort on numeric directory names, which bears no reliable relation to
time order at all**: `sorted(['0','10000','30000','5000'])` is
`['0','10000','30000','5000']`, so `[0]` is not dependably the earliest and `[-1]`
is not dependably the latest. A fix that merely swaps the index is still wrong; the
names must be compared as integers. `read_nu_clip.py` carries the same class of
defect, hardcoding `nuMin`/`nuMax` rather than asserting them against
`transportProperties`.

**A measured fact.** The rules it argues for — pair every reduced convergence
instrument with a fixed-point probe; freeze a plateau criterion as a threshold on
a window on a named channel rather than as `ptp → 0`; plant a control for a
negative convergence finding — were adopted by this team as
`ANSYS_VERIFICATION_CHARTER` v1.11 §16.3, §16.2 and §16.4 on the same date, so
this entry evidences them and does not itself legislate.
