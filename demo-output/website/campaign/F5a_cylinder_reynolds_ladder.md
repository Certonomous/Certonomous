# F5a — unsteady cylinder Reynolds ladder

Ladder: Re 1000 -> 2000 -> 3900 -> 5000 -> 10,000 -> 1e5 -> 1e6. Each rung must
pass its gate before the next starts.

**Provenance note.** The agent running this ladder was interrupted twice and left
results on disk without a report. The measurements below were **salvaged by the
supervisor directly from the solver output** (`postProcessing/forceCoeffs1`), not
relayed from an agent summary. Re 2000 is **incomplete** and is recorded as such.

Last updated 2026-07-29 02:0x UTC.

---

## Measured so far

| rung | status | Cd_mean | Cd std | Cl_rms | St | wall-time |
| --- | --- | --- | --- | --- | --- | --- |
| Re 1000 | complete, t=90 | **1.4678** | 0.1445 | 0.9666 | **0.2343** | 2417 s |
| Re 2000 | **INCOMPLETE**, t=56.7 of 90 | 1.5221 | 0.2123 | 1.1217 | 0.2341 | 2339 s |

Statistics taken over the second half of each run. Strouhal from mean-crossing
periods of the lift signal.

**Re 2000 is not a result yet.** It reached 63% of its intended window before the
host restarted. Its numbers are recorded for continuity, not gated.

## The 2D question, which governs every rung from here

These are **2D** solves. Above Re ~190 the real cylinder wake becomes
three-dimensional (mode A, then mode B instability), and the 3D wake carries
momentum that a 2D solve cannot represent. The well-known consequence is that 2D
simulations **over-predict Cd and over-predict St** relative to 3D experiment,
because the spanwise instability that weakens the vortex street is absent.

Our numbers are consistent with that direction: Cd ~1.47 at Re 1000 and St ~0.234
are both high against the values a 3D experiment gives at this Reynolds number.

**Stated honestly: I have not yet verified citable reference values for Re 1000
or Re 2000, so no deviation figure is claimed here.** The next rung's agent must
obtain them and gate against BOTH the 3D experimental value AND the documented
2D-simulation behaviour, so that a 2D deviation is attributed to dimensionality
rather than mistaken for solver error.

## Cost model (D13) — prediction before the next rung burns

| rung | wall-time | vs Re 100 |
| --- | --- | --- |
| Re 100 (batch family) | ~250 s | 1.0x |
| Re 1000 | 2417 s | **9.7x** |
| Re 2000 | 3715 s *(projected from 63% complete)* | 14.9x |

**The ~10x-per-decade rule from D14(a) holds:** Re 100 to Re 1000 measured
**9.7x**. Fitting a power law through those two points gives an exponent of
**0.99** — cost scales very nearly linearly in Reynolds number on this setup,
which makes sense when the timestep is Courant-limited and the cell count is
fixed.

### Prediction for the Re 3900 rung, posted before it runs

**Predicted wall-time: ~9,240 s (2.6 hours) single-core.**

Per D13 and P2, this prediction is on the record *before* the rung executes, and
measured-versus-predicted goes into the rung record. If it lands far off, the
cost model is wrong and that is itself the finding.

## Why Re 3900 is the rung that matters

It is the canonical cylinder-wake benchmark, with extensive published LES, DNS
and experimental data (Lourenco & Shih; Ong & Wallace; Kravchenko & Moin;
Parnaudeau et al. 2008). It should be gated hard on four quantities, not one:
mean drag, Strouhal number, recirculation-bubble length, and base pressure
coefficient.

**Per D6, the Re 3900 rung must also produce a scoped cost estimate for a 3D
LES/DES-class run alongside the 2D URANS result**, so the decision to run 3D
comes back to the docket with a number attached rather than as a guess.

## Learning questions (D6, answered as the ladder climbs)

- **Mesh that converged:** not yet established per rung; each rung must record it.
- **Where 2D stops being defensible:** physically, above Re ~190. Every rung from
  Re 1000 upward is therefore reporting a 2D approximation to a 3D flow, and must
  say so rather than presenting a 2D number as the answer.
- **Cost scaling:** measured at ~10x per decade of Re, exponent 0.99, on a fixed
  mesh with Courant-limited timestepping.
- **Steady vs unsteady:** the batch's steady cylinder family runs ~2.4 s per
  evaluation against ~394 s for the unsteady family at Re 100-1000 — a factor of
  roughly 164x, measured, and the dominant cost driver in the whole batch.
