# NOT FILED — VMFL038 manual defect: the printed geometry is a 100x units error

**NOT FILED. SUBMISSIONS ARE PARKED (`CLAUDE.md` rule 7).** This is a discrepancy
between the Ansys Fluid Dynamics Verification Manual and this lab's own reproduction,
recorded in this team's territory. It is **not sent, filed, posted or reported to
Ansys or anyone outside this box**; contacting Ansys is Sanaa's decision alone
(`ANSYS_VERIFICATION_CHARTER` §8). It is drafted here so the finding survives
compaction (L-186) and so no reader mistakes the derived geometry for a transcription
slip.

Drafted by `ansys-lane-opus48`, 2026-08-31, for the supervisor's read.

---

## The defect

VM2026R1 p.131 (VMFL038, *Falling Film Over an Inclined Plane*) prints, under
**Geometry**, *"Dimensions of the domain: 1 m X 18 m"*. **Taken as absolute metres
this is exactly 100x too large** — a metre-for-centimetre units error. The
self-consistent geometry, derived below from the manual's OWN other printed numbers,
is **0.01 m x 0.18 m**.

## Three independent identities fix the true geometry, and each is arithmetic

All computed with `math.sin(math.radians(30))` = `0.49999999999999994` (the float
residual of sin 30° is why the factor below reads `99.99999999999999` and not a clean
100; the discrepancy is a units error, not this residual).

| # | identity | result |
|---|---|---|
| 1 | `L = Delta_p / (rho*g*sin(beta))` = `706.32 / (800*9.81*sin30)` | **0.18000000000000002 m** |
| 2 | the head route reproduces the printed outlet gauge: `rho*g*sin(beta)*L` | **706.32 N/m2** exactly |
| 3 | `delta = L / 18` from the printed **1:18** aspect ratio | **0.010000000000000002 m** |

Taking the printed **18 m** as absolute instead: `rho*g*sin(beta)*18` = **70632 N/m2**,
which is **100x** the printed outlet gauge of **706.32 N/m2** — the internal
contradiction that proves the units error. `18 / 0.18` = **99.99999999999999**.

## What the error moves, and what it does NOT

| quantity | correct (0.01 m x 0.18 m) | printed-as-absolute (1 m x 18 m) | ratio |
|---|---|---|---|
| **u_max** = `(dp/L)*delta^2/(2 mu)` | **0.1962 m/s** | `(706.32/18)*1^2/(2*1)` = **19.62 m/s** | **100x** |
| **tau_w** = `(dp/L)*delta` = `Delta_p * delta / L` = `Delta_p / 18` | **39.24 Pa** | `706.32/18` = **39.24 Pa** | **1x (INVARIANT)** |

**The wall shear stress is SCALE-INVARIANT under the units error.** `tau_w = Delta_p / 18`
depends only on the outlet gauge (`706.32`, printed correctly) and the aspect ratio
(`18`, printed correctly), so it is **unchanged** whether the film is 1 cm or 1 m thick.
The velocity, by contrast, is off by 100x. This is one more reason VMFL038 is graded on
**tau_w** and not on velocity (the other, primary reason is RULING 1: a velocity gate on
a uniform mesh is machine-EXACT and grades NOT A RESULT).

## The number that reaches the gate

`tau_w = 39.24 Pa` is the frozen reference (`grade_vmfl038.py REF_TAU_W`), derived from
the manual alone and robust to this defect. The archive CSV `VMFL038_film-exp.csv` is
cited as **corroboration only** and is never a source of any registered number
(RULING 2).

## Classification

A **units/typographical error in a printed geometry**, corroborated by three internal
identities and self-contradicted by the manual's own pressure BC. Not a physics error
and not a solver error. The manual's reference physics (Bird/Stewart/Lightfoot p.45) is
correct; only the printed domain dimensions carry the factor.
