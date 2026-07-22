"""An idealized aortic systolic flow waveform, generated in-repo.

No patient data and no external file: the systolic ejection is modelled as a
half-sine pulse, the simplest shape that rises from zero, peaks mid-systole, and
returns to zero at valve closure.  From it we derive the three phase points the
multi-point valve study solves at — accelerating systole, peak, deceleration —
and the cycle weights each carries.

Waveform (normalised systolic time tau in [0,1]):

    Q(tau) = Q_peak * sin(pi * tau)          # half-sine ejection pulse

Phase points are the midpoints of the three equal thirds of systole; each
phase's WEIGHT is the fraction of the stroke volume (the integral of Q) ejected
during its third.  For the half-sine those integrals are analytic:

    third 1 (accelerating):  (1 - cos(pi/3)) / pi  =  0.5/pi   -> weight 0.25
    third 2 (peak):          (cos(pi/3) + 0.5) ... = 1.0/pi    -> weight 0.50
    third 3 (decelerating):  (0.5 + 1) ...         = 0.5/pi    -> weight 0.25

So the peak third carries half the ejected volume and the two shoulders a
quarter each — a clean, defensible weighting derived from the waveform itself
rather than assigned by hand.

Physiological scale (idealized adult): peak aortic flow ~ 0.5 L/s, systolic
duration ~ 0.30 s within a ~0.9 s cardiac cycle.  Blood is taken as Newtonian
with kinematic viscosity ~ 3.3e-6 m^2/s (mu ~ 3.5e-3 Pa.s, rho ~ 1060 kg/m^3).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Idealized cardiac parameters (SI).
Q_PEAK = 5.0e-4          # peak volumetric flow rate, m^3/s (~0.5 L/s)
T_SYSTOLE = 0.30         # systolic ejection duration, s
T_CYCLE = 0.90           # full cardiac cycle, s (~67 bpm)
RHO_BLOOD = 1060.0       # kg/m^3
NU_BLOOD = 3.3e-6        # kinematic viscosity, m^2/s (Newtonian idealization)


def flow(tau: float) -> float:
    """Instantaneous flow rate at normalised systolic time tau in [0,1]."""
    if tau <= 0.0 or tau >= 1.0:
        return 0.0
    return Q_PEAK * math.sin(math.pi * tau)


@dataclass(frozen=True)
class Phase:
    name: str
    tau: float           # normalised systolic time of the phase point
    flow_rate: float     # m^3/s at that point
    weight: float        # fraction of stroke volume in this phase's third


def phase_points() -> list[Phase]:
    """The k=3 phase points with waveform-derived cycle weights (sum to 1)."""
    names = ("accelerating systole", "peak systole", "decelerating systole")
    # Midpoints of the three equal thirds of systole.
    taus = (1.0 / 6.0, 1.0 / 2.0, 5.0 / 6.0)
    # Stroke-volume fraction in each third of the half-sine (analytic).
    edges = (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0)
    raw = []
    for a, b in zip(edges[:-1], edges[1:]):
        integral = (math.cos(math.pi * a) - math.cos(math.pi * b)) / math.pi
        raw.append(integral)
    total = sum(raw)
    weights = [r / total for r in raw]
    return [Phase(n, t, flow(t), w) for n, t, w in zip(names, taus, weights)]


def womersley(radius: float, t_cycle: float = T_CYCLE,
              nu: float = NU_BLOOD) -> float:
    """Womersley number alpha = R * sqrt(omega / nu), omega = 2 pi / T_cycle."""
    omega = 2.0 * math.pi / t_cycle
    return radius * math.sqrt(omega / nu)


if __name__ == "__main__":
    for p in phase_points():
        print(f"{p.name:22s} tau={p.tau:.3f}  Q={p.flow_rate*1e3:6.3f} L/s  "
              f"weight={p.weight:.3f}")
    print("sum weights =", round(sum(p.weight for p in phase_points()), 6))
    print("Womersley (root R=11.5mm) =", round(womersley(0.0115), 2))
