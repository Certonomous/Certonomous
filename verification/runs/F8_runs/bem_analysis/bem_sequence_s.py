#!/usr/bin/env python3
"""F8 zero-compute BEM cross-check -- NREL Phase VI Sequence S, 7 m/s, 72 RPM.

Executes proposal `f8-bem-torque-bound-at-sequence-s` (approved 2026-08-07,
supervisor review section 3, first diagnostic). PRE-REGISTRATION: everything in
this header block -- method, geometry source, polar source, arm list -- was
written before the integrator below was first run. The +800 N.m target was
already in context (it is in the proposal text itself); what is pre-registered
is the calculation, not blindness to the reference.

METHOD. Standard annular blade-element momentum: for each annulus iterate the
axial/tangential induction factors (a, a') to convergence with Prandtl tip AND
hub loss, Buhl's correction above a = 0.4. Torque is the tangential-force
moment integrated over the S809-bladed span, times B = 2 blades. The cylinder/
transition root (0.508-1.257 m) is excluded from the lifting integral and
charged separately as a drag-only penalty with Cd = 1.0.

CONDITIONS (the case on disk, F8_MRF_HAND2001_GATE.md sections 0-1):
  U = 7.0 m/s axial, Omega = 7.5398 rad/s (72 RPM), rho = 1.225 kg/m^3
  (rhoInf of the bladeForces object -- the comparison target uses the same
  density the CFD record uses), R_tip = 5.029 m, root attach 0.508 m.
  Tip-speed ratio lambda = Omega*R/U = 5.416.

GEOMETRY. Hand et al. 2001, NREL/TP-500-29955, Table A-1 (fetched from the
OSTI full text 2026-08-08; the same table the F8 record's section-10 STL audit
verified against the case geometry to 2-3 mm chord and 0.04 deg twist span).
Twist values are relative to zero twist at the 3.772-m station; twist at the
5.029-m tip is -1.815 deg (interpolated, matching the literature's "-1.816").

PITCH CONVENTION -- run as TWO ARMS because the record itself leaves it open:
  arm "tip-chord-3deg": section angle theta = twist - twist(tip) + 3.0
      = twist + 4.815 deg. This reproduces EXACTLY the +1.8 deg uniform offset
      the section-10 STL audit measured at all three stations (19.1/5.9/3.3
      measured vs 17.3/4.1/1.5 for twist+3), i.e. the as-built STL sits at
      this setting; TP-29955 defines blade pitch at the tip chord.
  arm "station-ref-3deg": theta = twist + 3.0 deg -- the reading the F8
      record's section 10 used, with the +1.8 deg attributed to chord-line
      measurement bias on the cambered section.

POLARS. NREL S809, AERODAS parameterisation of the TU Delft measured pre-stall
data: Spera, NASA/CR-2008-215434 (2008), Table 5 ("S809 Smooth", input data
credited to TU Delft as reported by Lindenburg 2003 and Tangler & Kocurek
2005), with the 2012 errata for eq. 12b. Two polar arms:
  arm "2D+tiploss" (primary, standard BEM practice): infinite-aspect-ratio
      polar (Table 5 "Reference" column) + Prandtl tip/hub loss in the
      momentum balance.
  arm "AR15.28": Spera's aspect-ratio-adjusted blade polar (Table 5 "Blade"
      column, AR = 15.28) with tip loss OFF -- his own BEM used the AR
      adjustment in place of a tip-loss factor and matched the measured UAE
      power to -1.3% +/- 4.0% over 54 points.
Drag sensitivity: a +50% Cd arm on the primary, because BEM torque at high
lambda is drag-sensitive.

REFERENCE for comparison (not used inside the calculation): Q = +800 N.m
turbine-signed at 7 m/s, secondary tier, Processes 12(9):1994 (2024) Table 6
digitised from Hand et al. 2001; corroborated by Spera fig. 7 (measured rotor
power ~5.5-6.5 kW at 7 m/s at 72 RPM -> Q = P/Omega ~ 730-860 N.m).

Zero solver compute: pure arithmetic, no OpenFOAM, no containers.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

# ---------------------------------------------------------------- conditions
U0 = 7.0                  # m/s
OMEGA = 7.5398            # rad/s (+x, 72 RPM)
RHO = 1.225               # kg/m^3 (the case's rhoInf)
R_TIP = 5.029             # m
R_ROOT_ATTACH = 0.508     # m (hub attach; cylinder/transition to 1.257 m)
R_AERO_IN = 1.257         # m (full S809 section begins)
B = 2                     # blades
LAMBDA = OMEGA * R_TIP / U0

# ------------------------------------------------- Table A-1 (TP-500-29955)
# (r [m], chord [m], twist [deg], zero-twist datum at r = 3.772 m)
TABLE_A1 = [
    (1.2575, 0.737, 20.040),
    (1.343, 0.728, 18.074),
    (1.510, 0.711, 14.292),
    (1.648, 0.697, 11.909),
    (1.952, 0.666, 7.979),
    (2.257, 0.636, 5.308),
    (2.343, 0.627, 4.715),
    (2.562, 0.605, 3.425),
    (2.867, 0.574, 2.083),
    (3.172, 0.543, 1.150),
    (3.185, 0.542, 1.115),
    (3.476, 0.512, 0.494),
    (3.781, 0.482, -0.015),
    (4.023, 0.457, -0.381),
    (4.086, 0.451, -0.475),
    (4.391, 0.420, -0.920),
    (4.696, 0.389, -1.352),
    (4.780, 0.381, -1.469),
    (5.000, 0.358, -1.775),
    (5.029, 0.35573, -1.81466),   # tip, linear interp of the 5.000/5.305 rows
]
TWIST_TIP = TABLE_A1[-1][2]


def interp(r: float, col: int) -> float:
    t = TABLE_A1
    if r <= t[0][0]:
        return t[0][col]
    for (r0, *v0), (r1, *v1) in zip(t, t[1:]):
        if r0 <= r <= r1:
            f = (r - r0) / (r1 - r0)
            return v0[col - 1] + f * (v1[col - 1] - v0[col - 1])
    return t[-1][col]


# ------------------------------------------------- AERODAS S809 (Spera 2008)
# Table 5 columns. "ref" = infinite aspect ratio (TU Delft data), "blade" =
# AR 15.28 adjusted. Constants for all airfoils: ACL2=41.0, S2=-0.032,
# ACD2=90.0. A0 and CD0 are AR-independent.
A0 = -1.00
CD0 = 0.0070
S809 = {
    "ref":   dict(S1=0.155, ACL1=14.0, ACD1=20.1, CL1max=1.070, RCL1=1.254,
                  N1=1.85, CD1max=0.200, CL2max=1.138, RCL2=0.494, N2=3.30,
                  CD2max=1.921, M=3.0),
    "blade": dict(S1=0.125, ACL1=15.7, ACD1=21.8, CL1max=1.047, RCL1=1.033,
                  N1=2.01, CD1max=0.226, CL2max=1.036, RCL2=0.596, N2=2.74,
                  CD2max=1.624, M=3.0),
}
S2 = -0.0320


def polar(alpha: float, p: dict) -> tuple[float, float]:
    """(Cl, Cd) at alpha [deg], AERODAS eqs. 3, 6, 7, 11, 12 (+2012 errata)."""
    # pre-stall lift, eq 6
    if alpha >= A0:
        cl1 = p["S1"] * (alpha - A0) - p["RCL1"] * (
            max((alpha - A0) / (p["ACL1"] - A0), 0.0)) ** p["N1"]
    else:
        cl1 = p["S1"] * (alpha - A0) + p["RCL1"] * (
            max((A0 - alpha) / (p["ACL1"] - A0), 0.0)) ** p["N1"]
    # pre-stall drag, eq 7
    if (2 * A0 - p["ACD1"]) <= alpha <= p["ACD1"]:
        cd1 = CD0 + (p["CD1max"] - CD0) * (
            abs((alpha - A0) / (p["ACD1"] - A0))) ** p["M"]
    else:
        cd1 = 0.0
    # post-stall lift, eq 11 (only the alpha >= 0 branches are reachable here)
    if 0.0 < alpha < p["ACL1"]:
        cl2 = 0.0
    elif alpha <= 92.0:
        rcl2 = 1.632 - p["CL2max"]
        n2 = 1 + p["CL2max"] / rcl2
        cl2 = S2 * (alpha - 92.0) - rcl2 * ((92.0 - alpha) / 51.0) ** n2
    else:
        rcl2 = 1.632 - p["CL2max"]
        n2 = 1 + p["CL2max"] / rcl2
        cl2 = S2 * (alpha - 92.0) + rcl2 * ((alpha - 92.0) / 51.0) ** n2
    # post-stall drag, eq 12 + errata
    if (2 * A0 - p["ACD1"]) < alpha < p["ACD1"]:
        cd2 = 0.0
    elif alpha >= p["ACD1"]:
        cd2 = p["CD1max"] + (p["CD2max"] - p["CD1max"]) * math.sin(
            math.radians((alpha - p["ACD1"]) / (90.0 - p["ACD1"]) * 90.0))
    else:
        cd2 = 0.0
    if alpha >= A0:
        cl = max(cl1, cl2)
    else:
        cl = min(cl1, cl2)
    return cl, max(cd1, cd2)


# ----------------------------------------------------------------- BEM core
def bem(pitch_offset: float, polar_key: str, tip_loss: bool,
        cd_scale: float = 1.0, n: int = 300) -> dict:
    p = S809[polar_key]
    r_edges = [R_AERO_IN + (R_TIP - R_AERO_IN) * i / n for i in range(n + 1)]
    q_total = 0.0
    thrust = 0.0
    stations = []
    for r0, r1 in zip(r_edges, r_edges[1:]):
        r = 0.5 * (r0 + r1)
        dr = r1 - r0
        c = interp(r, 1)
        theta = interp(r, 2) + pitch_offset
        sigma = B * c / (2 * math.pi * r)
        a, ap = 0.25, 0.0
        phi = alpha = f_loss = 0.0
        cl = cd = cn = ct = 0.0
        for _ in range(500):
            ut = OMEGA * r * (1 + ap)
            un = U0 * (1 - a)
            phi = math.atan2(un, ut)
            alpha = math.degrees(phi) - theta
            cl, cd = polar(alpha, p)
            cd *= cd_scale
            sphi, cphi = math.sin(phi), math.cos(phi)
            cn = cl * cphi + cd * sphi
            ct = cl * sphi - cd * cphi
            if tip_loss and sphi > 1e-6:
                ft = 2 / math.pi * math.acos(min(1.0, math.exp(
                    -B * (R_TIP - r) / (2 * r * abs(sphi)))))
                fh = 2 / math.pi * math.acos(min(1.0, math.exp(
                    -B * (r - R_ROOT_ATTACH) / (2 * r * abs(sphi)))))
                f_loss = max(ft * fh, 1e-4)
            else:
                f_loss = 1.0
            k = sigma * cn / (4 * f_loss * sphi * sphi) if sphi else 0.0
            a_new = k / (1 + k)
            # Buhl high-induction correction
            if a_new > 0.4:
                ctl = sigma * (1 - a) ** 2 * cn / (sphi * sphi)
                a_new = (18 * f_loss - 20 - 3 * math.sqrt(max(
                    ctl * (50 - 36 * f_loss) + 12 * f_loss * (3 * f_loss - 4),
                    0.0))) / (36 * f_loss - 50)
            kp = sigma * ct / (4 * f_loss * sphi * cphi) if cphi else 0.0
            ap_new = kp / (1 - kp) if kp < 1 else 0.5
            if abs(a_new - a) < 1e-8 and abs(ap_new - ap) < 1e-8:
                a, ap = a_new, ap_new
                break
            a = 0.7 * a + 0.3 * a_new
            ap = 0.7 * ap + 0.3 * ap_new
        vrel2 = (U0 * (1 - a)) ** 2 + (OMEGA * r * (1 + ap)) ** 2
        dq = B * 0.5 * RHO * vrel2 * c * ct * r * dr
        dt = B * 0.5 * RHO * vrel2 * c * cn * dr
        q_total += dq
        thrust += dt
        stations.append(dict(r=round(r, 4), alpha=round(alpha, 3),
                             a=round(a, 4), cl=round(cl, 4),
                             cd=round(cd, 5), dq=round(dq, 3)))
    # Root cylinder/transition drag penalty (0.508-1.257 m), Cd = 1.0,
    # torque-opposing component only. Chord tapers ~0.218 -> 0.737 through the
    # transition; use the Table A-1 rows below r = 1.257 as the width.
    root_rows = [(0.508, 0.218), (0.883, 0.183), (1.008, 0.349),
                 (1.134, 0.544), (1.2575, 0.737)]
    q_root = 0.0
    for (ra, ca), (rb, cb) in zip(root_rows, root_rows[1:]):
        r = 0.5 * (ra + rb)
        c = 0.5 * (ca + cb)
        vrel2 = U0 ** 2 + (OMEGA * r) ** 2
        cphi = OMEGA * r / math.sqrt(vrel2)
        q_root -= B * 0.5 * RHO * vrel2 * c * 1.0 * cphi * r * (rb - ra) * 0.0
        # NOTE: a bluff root section's drag vector opposes Vrel; its torque
        # component is -D*cos(phi)*r:
        q_root -= B * 0.5 * RHO * vrel2 * c * 1.0 * cphi * r * (rb - ra)
    return dict(torque_Nm=round(q_total, 1),
                torque_with_root_drag_Nm=round(q_total + q_root, 1),
                root_drag_torque_Nm=round(q_root, 1),
                power_kW=round(q_total * OMEGA / 1e3, 2),
                thrust_N=round(thrust, 1),
                stations=stations[::30])


def main() -> None:
    arms = {
        "A_tipchord3_2Dpolar_tiploss": bem(3.0 - TWIST_TIP, "ref", True),
        "B_stationref3_2Dpolar_tiploss": bem(3.0, "ref", True),
        "C_tipchord3_AR15polar_noloss": bem(3.0 - TWIST_TIP, "blade", False),
        "D_tipchord3_2Dpolar_tiploss_cd150": bem(3.0 - TWIST_TIP, "ref", True,
                                                 cd_scale=1.5),
    }
    out = dict(
        conditions=dict(U=U0, omega=OMEGA, rho=RHO, R=R_TIP,
                        tsr=round(LAMBDA, 3), blades=B,
                        seq_s_tip_pitch_deg=3.0, twist_tip_deg=TWIST_TIP),
        reference=dict(Q_ref_Nm=800.0, tier="secondary",
                       source="Processes 12(9):1994 (2024) Table 6, "
                              "digitised from Hand et al. 2001"),
        arms=arms,
    )
    path = Path(__file__).parent / "bem_result.json"
    path.write_text(json.dumps(out, indent=1))
    for name, r in arms.items():
        print(f"{name}: Q = {r['torque_Nm']} N.m "
              f"({r['torque_with_root_drag_Nm']} with root drag), "
              f"P = {r['power_kW']} kW, T = {r['thrust_N']} N")
    print(f"lambda = {LAMBDA:.3f}; reference +800 N.m (secondary tier)")


if __name__ == "__main__":
    main()
