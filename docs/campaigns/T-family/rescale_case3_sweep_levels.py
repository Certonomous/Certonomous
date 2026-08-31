#!/usr/bin/env python3
"""Case 3 (motor-in-duct CHT) P_loss x U_inf sweep: LEVEL RESCALE ARITHMETIC.

Sanaa ruled "Rescale" (etc/sessions/2026-08-31T1615Z_sanaa_six_answers.md,
answer 5) on the Case 3 sweep levels of
etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md section 3.3.

THIS SCRIPT RUNS NO SOLVER.  It is a closed-form lumped series-resistance
estimate used to CHOOSE REGISTRATION LEVELS BEFORE ANY COMPUTE.  Every number
it prints is DERIVED from the tagged inputs below; none is MEASURED, and none
of it is a verdict from the CLAUDE.md rule-1 vocabulary.

PROVENANCE TAGS on every input are in the dict `INPUTS` and are printed.

Recovered from and re-derived against the pre-kill lane's scratch drafts
`rescale.py` (16:18:21Z) and `cand.py` (16:19:24Z); this file is the
repository copy, because the scratchpad is not a handoff channel (L-186).

CORRECTION 2026-08-31, AGAINST THE COMMIT THAT LANDED THIS FILE (`173d797c`).
That commit message asserts, as the rule-2 pre-compute evidence, that "a grep
for the 16-point map across docs/campaigns/T-family/, verification/ and cases/
returns zero files".  THAT SENTENCE IS FALSE AND THIS BLOCK IS THE CORRECTION.
The grep ran as a background command; its output file was read WHILE STILL
BEING WRITTEN, and the empty partial was reported as the complete result.

THE GREP RETURNS 11 FILES, NOT ZERO [MEASURED, re-run to completion]:
  - nine are the false-positive class -- snappyHexMesh logs containing the
    literal string "16 points" (mesh diagnostics, nothing to do with Case 3);
  - `verification/runs/T-family/T22_runs/T22_CHTb_L1/build_t22.py:6` names the
    SINGLE benign feasibility point "P_loss = 300 W, U_inf = 20 m/s", not a map;
  - `docs/campaigns/T-family/T21_PREREGISTRATION.md:51` and `:106` are the only
    real mentions of the map, and BOTH DISCLAIM IT: ":51" reads "nothing about
    the 16-point P_loss x U_inf map.  Those are separate rungs with separate
    registrations and this document may not be cited as covering them", and
    T21 is untracked and headed "DRAFT.  NOT FROZEN.  NOT COMMITTED.
    AUTHORISES NOTHING."

THE CONCLUSION IS UNCHANGED AND IS NOW BETTER SUPPORTED, WHICH IS EXACTLY WHY
THE FALSE EVIDENCE HAD TO BE CORRECTED RATHER THAN LEFT TO STAND: no document
registers the 16-point map, and the one document that mentions it says in terms
that it registers nothing about it.  The absent run directories named in that
commit message were checked by direct `ls` and are unaffected by this error.
"""
import math

# ---------------------------------------------------------------- inputs
# tag, value, basis
INPUTS = [
    ("rho_air",  1.2,     "kg/m3",  "REGISTERED", "directive 3.3, air properties"),
    ("cp_air",   1005.0,  "J/kgK",  "REGISTERED", "directive 3.3"),
    ("k_air",    0.026,   "W/mK",   "REGISTERED", "directive 3.3"),
    ("mu_air",   1.8e-5,  "Pa.s",   "REGISTERED", "directive 3.3"),
    ("k_Al",     167.0,   "W/mK",   "REGISTERED", "directive 3.3, aluminium housing"),
    ("k_core",   40.0,    "W/mK",   "REGISTERED", "directive 3.3, representative winding pack"),
    ("T_inf",    288.0,   "K",      "REGISTERED", "directive 3.3, fluid inlet T"),
    ("D_duct",   0.25,    "m",      "REGISTERED", "directive 3.2, D = 0.25 m"),
    ("r_o",      0.0375,  "m",      "DERIVED",    "0.3*D/2 = 0.075/2, directive 3.2"),
    ("r_i",      0.0335,  "m",      "DERIVED",    "r_o - 4 mm wall, directive 3.2"),
    ("L_hous",   0.125,   "m",      "DERIVED",    "0.5*D, directive 3.2"),
    ("r_bore",   0.006,   "m",      "ASSUMED",    "shaft bore radius; NOT in the directive, "
                                                  "chosen by judgement. Its effect is bounded "
                                                  "below (BORE SENSITIVITY block)."),
]
rho, cp, k, mu, kAl, kCore, Tinf, D, ro, ri, L, rb = [v for _, v, _, _, _ in INPUTS]

Pr = mu * cp / k                    # DERIVED
Dh = D - 2.0 * ro                   # DERIVED: annulus hydraulic diameter, directive 3.6
A  = 2.0 * math.pi * ro * L         # DERIVED: wetted housing cylinder (ends adiabatic, 3.3)
BOUND_C = 200.0                     # REGISTERED: directive 3.6 physicality sanity
ISO_C   = 120.0                     # REGISTERED: directive 3.6 hold-this-power isotherm

Us = [10, 20, 30, 40]               # REGISTERED: directive 3.3 airspeed levels, UNCHANGED


# ------------------------------------------------------- the two h bounds
def h_DB(U):
    """Dittus-Boelter on the annulus hydraulic diameter. PESSIMISTIC (low h)."""
    Re = rho * U * Dh / mu
    return 0.023 * Re ** 0.8 * Pr ** 0.4 * k / Dh


def h_FP(U):
    """Flat-plate average over the housing length. OPTIMISTIC (high h)."""
    Re = rho * U * L / mu
    return 0.037 * Re ** 0.8 * Pr ** (1.0 / 3.0) * k / L


# --------------------------------------------- the series-resistance model
R_WALL = math.log(ro / ri) / (2.0 * math.pi * kAl * L)          # K/W, DERIVED


def r_core(bore):
    """K/W for uniform generation in a hollow cylinder, adiabatic inner bore."""
    V = math.pi * (ri ** 2 - bore ** 2) * L
    return (1.0 / (2.0 * kCore * V)) * ((ri ** 2 - bore ** 2) / 2.0
                                        - bore ** 2 * math.log(ri / bore))


R_CORE = r_core(rb)                                             # K/W, DERIVED


def R_tot(U, hf):
    return 1.0 / (hf(U) * A) + R_WALL + R_CORE


def Tmax_C(P, U, hf):
    return Tinf + P * R_tot(U, hf) - 273.15


def P_at(U, hf, T_C):
    """Closed-form inverse: the model is exactly linear in P."""
    return (T_C + 273.15 - Tinf) / R_tot(U, hf)


def report(title, Ps, hf, label):
    over = []
    print("\n== %s -- %s ==" % (title, label))
    print("  P(W)\\U " + "".join("%11d" % u for u in Us))
    for P in Ps:
        cells = []
        for u in Us:
            T = Tmax_C(P, u, hf)
            flag = "*" if T > BOUND_C else " "
            if T > BOUND_C:
                over.append((P, u, T))
            cells.append("%10.1f%s" % (T, flag))
        print("  %5d  " % P + "".join(cells))
    print("  points above %.0f C: %d of %d" % (BOUND_C, len(over), len(Ps) * len(Us)))
    return over


def count_over(Ps, hf):
    return sum(1 for P in Ps for u in Us if Tmax_C(P, u, hf) > BOUND_C)


def main():
    print("CASE 3 SWEEP LEVEL RESCALE -- CLOSED FORM, NO SOLVER RAN")
    print("=" * 72)
    print("\nINPUTS (tag / basis):")
    for name, val, unit, tag, basis in INPUTS:
        print("  %-9s %-12g %-7s %-11s %s" % (name, val, unit, tag, basis))
    print("\nDERIVED: Pr = %.6f   D_h = %.4f m   A_housing = %.6f m2" % (Pr, Dh, A))
    print("DERIVED: R_wall = %.6e K/W   R_core = %.6e K/W" % (R_WALL, R_CORE))
    print("\nh [W/m2K] at the four REGISTERED airspeeds:")
    print("  U (m/s)        " + "".join("%11d" % u for u in Us))
    print("  Dittus-Boelter " + "".join("%11.1f" % h_DB(u) for u in Us))
    print("  flat-plate avg " + "".join("%11.1f" % h_FP(u) for u in Us))
    print("  ratio FP/DB    " + "".join("%11.3f" % (h_FP(u) / h_DB(u)) for u in Us))

    # ---- 1. the ORIGINAL registered levels, both estimators
    print("\n" + "=" * 72)
    print("1. THE ORIGINAL DIRECTIVE LEVELS {100, 300, 600, 1000} W")
    orig = [100, 300, 600, 1000]
    report("T_max [degC], Dittus-Boelter (pessimistic)", orig, h_DB, "ORIGINAL")
    report("T_max [degC], flat plate (optimistic)", orig, h_FP, "ORIGINAL")
    print("\n  ORIGINAL over-bound count: %d of 16 (DB)   %d of 16 (FP)"
          % (count_over(orig, h_DB), count_over(orig, h_FP)))

    # ---- 2. the structural incompatibility
    print("\n" + "=" * 72)
    print("2. THE INCOMPATIBILITY -- why NO full-factorial rectangle can clear the bound")
    print("   while still delivering the %.0f C isotherm of directive 3.6." % ISO_C)
    for hf, nm in ((h_DB, "Dittus-Boelter"), (h_FP, "flat plate")):
        iso_hi = P_at(max(Us), hf, ISO_C)     # top P must reach this to bracket at U=40
        p200_lo = P_at(min(Us), hf, BOUND_C)  # top P must not exceed this at U=10
        print("\n   %s:" % nm)
        print("     to BRACKET the %.0f C isotherm at U = %d m/s, max(P) >= %8.1f W"
              % (ISO_C, max(Us), iso_hi))
        print("     to keep every point under %.0f C at U = %d m/s, max(P) <= %8.1f W"
              % (BOUND_C, min(Us), p200_lo))
        print("     %8.1f > %8.1f  ->  INCOMPATIBLE by a factor %.3f"
              % (iso_hi, p200_lo, iso_hi / p200_lo))
    print("\n   Holds under BOTH estimators, so it is not an artefact of the h model.")
    print("   Minimum unavoidable flagged points on any bracketing rectangle: 1 (DB).")

    print("\n   The %.0f C isotherm, P [W] at which T_max = %.0f C:" % (ISO_C, ISO_C))
    print("     U (m/s)   " + "".join("%11d" % u for u in Us))
    print("     DB        " + "".join("%11.1f" % P_at(u, h_DB, ISO_C) for u in Us))
    print("     FP        " + "".join("%11.1f" % P_at(u, h_FP, ISO_C) for u in Us))
    print("   The %.0f C bound, P [W] at which T_max = %.0f C:" % (BOUND_C, BOUND_C))
    print("     DB        " + "".join("%11.1f" % P_at(u, h_DB, BOUND_C) for u in Us))
    print("     FP        " + "".join("%11.1f" % P_at(u, h_FP, BOUND_C) for u in Us))

    # ---- 3. candidate level sets
    print("\n" + "=" * 72)
    print("3. CANDIDATE LEVEL SETS")
    iso = {u: P_at(u, h_DB, ISO_C) for u in Us}
    cands = [
        ("ORIGINAL      100/300/600/1000", [100, 300, 600, 1000]),
        ("supervisor's   50/100/200/300",  [50, 100, 200, 300]),
        ("dead lane A    60/120/200/320",  [60, 120, 200, 320]),
        ("THIS LANE      80/155/230/305",  [80, 155, 230, 305]),
        ("min-flag       80/130/175/305",  [80, 130, 175, 305]),
    ]
    print("\n  %-32s %8s %8s  %-24s %s"
          % ("level set", "over(DB)", "over(FP)", "isotherm bracketed?", "widest iso gap [W]"))
    for name, Ps in cands:
        br = [u for u in Us if min(Ps) <= iso[u] <= max(Ps)]
        # resolution: for each bracketed U, the P-interval containing the crossing
        gaps = []
        for u in br:
            lo = max([p for p in Ps if p <= iso[u]], default=min(Ps))
            hi = min([p for p in Ps if p >= iso[u]], default=max(Ps))
            gaps.append(hi - lo)
        print("  %-32s %8d %8d  %-24s %s"
              % (name, count_over(Ps, h_DB), count_over(Ps, h_FP),
                 ("ALL FOUR" if len(br) == 4 else "only U = %s" % br),
                 ("%.0f" % max(gaps)) if gaps else "n/a"))

    # ---- 4. the recommended set in full, with margins
    print("\n" + "=" * 72)
    rec = [80, 155, 230, 305]
    print("4. RECOMMENDED SET %s W  (ASSUMED levels; U_inf levels UNCHANGED)" % rec)
    report("T_max [degC], Dittus-Boelter (pessimistic)", rec, h_DB, "RECOMMENDED")
    report("T_max [degC], flat plate (optimistic)", rec, h_FP, "RECOMMENDED")
    print("\n  MARGIN TO THE %.0f C BOUND, Dittus-Boelter (negative = above the bound):" % BOUND_C)
    print("  P(W)\\U " + "".join("%11d" % u for u in Us))
    for P in rec:
        print("  %5d  " % P + "".join("%11.1f" % (BOUND_C - Tmax_C(P, u, h_DB)) for u in Us))
    near = [(P, u, BOUND_C - Tmax_C(P, u, h_DB))
            for P in rec for u in Us if abs(BOUND_C - Tmax_C(P, u, h_DB)) < 50.0]
    print("\n  Points within 50 K of the bound under DB (the model cannot call these):")
    for P, u, m in near:
        print("    P = %d W, U = %d m/s: margin %+.1f K" % (P, u, m))
    if not near:
        print("    none")

    # ---- 5. bore sensitivity: how much does the one ASSUMED input matter?
    print("\n" + "=" * 72)
    print("5. SENSITIVITY TO THE ONE ASSUMED INPUT (r_bore), at the worst cell")
    Pw, Uw = max(rec), min(Us)
    base = Tmax_C(Pw, Uw, h_DB)
    for b in (0.0001, 0.003, 0.006, 0.010, 0.015):
        Rc = r_core(b)
        T = Tinf + Pw * (1.0 / (h_DB(Uw) * A) + R_WALL + Rc) - 273.15
        print("    r_bore = %6.4f m -> R_core = %.4e K/W, T_max(%d W, %d m/s) = %7.2f C "
              "(delta %+.2f K)" % (b, Rc, Pw, Uw, T, T - base))
    print("\n    The convective term dominates: r_bore moves T_max by a few K across a")
    print("    150x range of the assumption, while FP vs DB moves it by tens of K.")
    print("    The ASSUMED bore is therefore NOT what decides any flag.")


if __name__ == "__main__":
    main()
