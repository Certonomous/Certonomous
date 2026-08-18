# K2b-U3 — does the oscillation survive in 3D? Pre-registration

**Campaign F14, rung K2b, 3D unsteadiness check. Written 2026-08-18 BEFORE any
3D transient ran.** Every threshold, every gate and every outcome-to-meaning
mapping below is fixed here. Authorisation: ~11 core-minutes.

---

## 1. The question, and why this rung raised it against itself

`K2b_PILOT_RESULTS.md` §14 established outcome **O1**: the 2D rack-row slice at
70 % provisioning is **physically unsteady** — a coherent 6.000 s limit cycle of
≈1.1 K in rack-inlet temperature, non-decaying over 40 s, growing 1.81× when
under-relaxation is halved. §14.6 then said, against its own finding:

> **A 2D slice suppresses spanwise instabilities and can also manufacture
> oscillations that a 3D flow would damp by three-dimensionalising — a 2D
> cylinder wake is the classic case. So O1 is a warning about the 3D module, not
> a measurement of it.**

This document tests that warning.

## 2. THE GATE — a control that must pass before the 3D test means anything

**The 3D mesh affordable here is 8× coarser than the 2D slice the limit cycle was
found on** (100 mm against 12.5 mm). If a 3D run at 100 mm shows no oscillation,
that could be three-dimensionality damping it **or the coarse mesh damping it**,
and those are opposite conclusions.

**Control M**: the same 2D slice, same 70 % provisioning, same transient solver,
**at the 3D test's own 100 mm resolution.** It asks one thing: does the 6.000 s
limit cycle survive coarsening *alone*?

- **Control M shows the oscillation surviving** → mesh resolution is excluded as
  the explanation, and Test D's answer is about dimensionality. Proceed.
- **Control M shows it damping** → mesh and dimensionality are confounded at this
  price and **Test D cannot answer the question**. Outcome **P3**, declared
  without running Test D, with the cost of the un-confounded experiment stated.

Control M costs ~0.2 core-minutes. **It is run first and its result is reported
whichever way it falls.**

## 3. The runs, and the numbers fixed before they start

Both cases: `buoyantBoussinesqPimpleFoam`, Euler ddt, PIMPLE 2 outer / 2 inner
correctors, 70 % tile provisioning, all other boundary conditions exactly those
of `K2bP_under`, started from a uniform field at T_sup.

| | Control M (2D) | Test D (3D) |
|---|---|---|
| mesh | y–z slice at h = 0.1 m | full module, N = 4 racks, h = 0.1 m |
| cells | ≈725 | ≈28,700 |
| row ends | none (slice) | **open, 0.60 m each** — the 3D-only path |
| endTime | 80 s | 80 s |
| maxCo | **2.0** | **2.0** |
| expected Δt | ≈0.167 s | ≈0.167 s |
| **steps per 6.000 s period** | **≈36** | **≈36** |
| monitor interval | 0.2 s | 0.2 s |
| **samples per period** | **≈30** | **≈30** |
| estimated cost | 0.2 core-min | 5.4 core-min |

### 3.1 The aliasing guard, stated before the run

A period sampled too coarsely aliases into something that looks like decay.
**Required, and reported as measured whatever happens: ≥ 20 time steps per
period and ≥ 10 monitor samples per period.** The design gives ≈36 and ≈30. **If
the achieved Δt delivers fewer than 10 samples per period, the run is REFUSED as
unable to distinguish decay from aliasing** — outcome P3 — rather than graded
into a soft answer.

### 3.2 Windows

The room turnover time at 70 % provisioning in 3D is ≈35 s, so the flow needs
that long to develop from a uniform start. **The first 40 s are discarded as
development.** Graded on the **final 20 s (60–80 s) against the preceding 20 s
(40–60 s)** — each ≈3.3 periods.

### 3.3 Thresholds — the same shape as K2b-U, on T_in over `rack_in`

For the 3D case, T_in is the **mass-flow-weighted mean over all four rack front
faces**, and the per-rack values are reported alongside.

| reading | verdict |
|---|---|
| final-window p2p **≥ 0.30 K** and ratio final/preceding **≥ 0.8** | **SURVIVES** |
| final-window p2p **≤ 0.10 K**, or ratio **≤ 0.5** | **DAMPS** |
| anything else | **UNDECIDABLE** |

## 4. The three outcomes, and what each MEANS — fixed before the runs

**P1 — IT SURVIVES IN 3D.** Control M passes and Test D reads SURVIVES.
→ The limit cycle is not an artefact of two-dimensionality. **O1's consequence
carries to the 3D module**: it needs a transient formulation, the §9 steady
estimate stays void, and K2a §9 must be re-specified for transient-with-averaging
at this provisioning.

**P2 — IT DAMPS IN 3D.** Control M passes and Test D reads DAMPS.
→ **Three-dimensionality damps the mode.** The 2D finding stands **as true of the
2D slice** — it is not retracted and it was not wrong; it was a measurement of a
2D slice, and the three failures it explained (C3's 48.3 W floor, the
wall-treatment 1.1 K swing, the convergence refusals) were all measured on 2D
cases and remain explained. What changes is only its *extrapolation*: the 3D
module may be steady-solvable, the §9 estimate becomes **revivable but not
revived** — it was built on iteration counts taken from an unsteady 2D case and
must be re-derived before it is quoted.

**P3 — UNDECIDABLE AT THIS PRICE.** Control M fails, or the aliasing guard of
§3.1 fails, or Test D reads UNDECIDABLE.
→ **Stated as the answer, not resolved by preference.** The 3D module stays held,
the §9 estimate stays void, and the cost of the un-confounded experiment is
named: a 3D transient at the spec's own 60 mm coarse mesh, 80 s, is
**≈42 core-minutes** at this rung's measured transient rate of
4.26e4 cell·steps/(core·s).

## 5. What this cannot reach, whichever way it falls

- **100 mm is coarser than the spec's 60 mm 3D coarse mesh.** Even P1 or P2 is a
  statement about a 100 mm 3D module, and Control M is what stops that being a
  statement about nothing.
- **One provisioning, one geometry.** 70 % under-provisioning with N = 4. A
  balanced 3D module was not tested and the 2D balanced case was nearly steady.
- **80 s cannot see a mode slower than ≈25 s.** If a slow aisle-scale mode exists
  above that, this run does not exclude it.
