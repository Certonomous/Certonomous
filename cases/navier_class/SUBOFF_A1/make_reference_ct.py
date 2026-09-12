#!/usr/bin/env python3
"""
SUBOFF_A1 -- BUILD THE Gate-D2 REFERENCE JSON, BEFORE THE FREEZE.

SUBOFF_A1_PREREGISTRATION.md 5.3 requires, verbatim, that `CT_ref` be
"R1's ITTC-1957 friction-line + form-factor anchor of 3.6e-3 on wetted area, PLUS A
SAIL INCREMENT COMPUTED BY THE SAME ENGINEERING METHOD AND RECORDED IN THE REFERENCE
JSON BEFORE THE FREEZE", and that `Aref` be "read back from the built wall patches".
This script is the instrument that does both.  IT PRODUCES NO VERDICT.

WHAT IT IS NOT.  `CT_ref` is a MANIFEST / ENGINEERING ANCHOR, not a measurement.
No title-verified SUBOFF force measurement is on disk (pre-registration 2.2: Huang
et al. 1992, Liu & Huang 1998 and Crook 1990 are all NOT OBTAINED).  Gate D2 is
BOUNDED-AGREEMENT against this anchor and is NOT experiment-validated.

RULE 3.  Every area in the output is produced by `suboff_a1_polymesh.patch_area`,
whose planted control is run FIRST, on EVERY invocation, from disk, and which
REFUSES (exit 2) if the reader cannot see a planted 12.345 m^2 patch behind a decoy
patch of 6.1725 m^2.  The plant's result is written verbatim into the output.

READ-ONLY ON THE GRADED TREE.

ZERO `assert` (L-332).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)
import os, json, math, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suboff_a1_polymesh as PM                                   # noqa: E402

FT2M   = 0.3048
L_M    = 14.291667 * FT2M          # 4.3561001016 m  (geometry_manifest.json)
RE_L   = 1.2e7                     # pre-registration 2.2: the lab's WORKING condition,
NU     = 1.0e-6                    #   NOT a value read from a source on disk.
RHO    = 998.2                     # kg/m^3, water at 20 C.  CT is invariant to it.
CT_HULL_ANCHOR = 3.6e-3            # pre-registration 5.3, inherited from SUBOFF R1.
SAIL_CHORD_M   = 0.3682999         # geometry_manifest.json, truncated at 0.995 c
SAIL_TOC       = 0.181035          # pre-registration 11.1, measured from the equations


def cf_ittc57(re):
    """ITTC-1957 model-ship correlation line."""
    if re <= 100.0:
        sys.stderr.write(f"REFUSED: Re={re} is not a turbulent Reynolds number.\n")
        sys.exit(2)
    return 0.075 / (math.log10(re) - 2.0) ** 2


def stl_area_ascii(path, z_min=None):
    """Total facet area of an ASCII STL; if z_min is given, only facets whose
    centroid has z >= z_min.  Used ONLY as an independent cross-check of the
    built-patch area -- never as Aref."""
    tot, v, n = 0.0, [], 0
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if s.startswith("vertex"):
                p = s.split()
                v.append((float(p[1]), float(p[2]), float(p[3])))
                if len(v) == 3:
                    if z_min is None or (v[0][2] + v[1][2] + v[2][2]) / 3.0 >= z_min:
                        ax = v[1][0] - v[0][0]; ay = v[1][1] - v[0][1]; az = v[1][2] - v[0][2]
                        bx = v[2][0] - v[0][0]; by = v[2][1] - v[0][1]; bz = v[2][2] - v[0][2]
                        cx = ay * bz - az * by; cy = az * bx - ax * bz; cz = ax * by - ay * bx
                        tot += 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)
                    n += 1
                    v = []
    if n == 0:
        sys.stderr.write(f"REFUSED: {path} yielded zero facets.\n"); sys.exit(2)
    return tot, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level-dir", required=True,
                    help="the BUILT level whose wall patches set Aref (use the FINEST)")
    ap.add_argument("--scratch", required=True, help="where the rule-3 plant is written")
    ap.add_argument("--out", required=True)
    ap.add_argument("--stl-hull", default=None, help="optional independent cross-check")
    a = ap.parse_args()

    if os.path.exists(a.out):
        sys.stderr.write(f"REFUSED: {a.out} already exists.  A reference anchor is "
                         "written once, before the freeze, and never rewritten.\n")
        sys.exit(2)

    plant = PM.plant_and_verify(a.scratch)          # RULE 3, FIRST, BEFORE ANY MESH

    s_hull = PM.patch_area(a.level_dir, "hull", patches=("hull", "sail"))
    s_sail = PM.patch_area(a.level_dir, "sail", patches=("hull", "sail"))
    s_tot = s_hull + s_sail
    if s_hull <= 0.0 or s_sail <= 0.0:
        sys.stderr.write("REFUSED: a wall patch measured non-positive area.\n"); sys.exit(2)

    u = RE_L * NU / L_M
    cf_l = cf_ittc57(RE_L)
    k_hull = CT_HULL_ANCHOR / cf_l - 1.0            # back out R1's implied form factor

    re_c = u * SAIL_CHORD_M / NU
    cf_c = cf_ittc57(re_c)
    k_sail = 2.0 * SAIL_TOC + 60.0 * SAIL_TOC ** 4  # classical foil form factor
    cd_sail = cf_c * (1.0 + k_sail)

    ct_ref = (CT_HULL_ANCHOR * s_hull + cd_sail * s_sail) / s_tot

    out = {
        "WHAT_THIS_IS": "Gate D2 reference anchor.  MANIFEST / ENGINEERING ANCHOR, "
                        "NOT a measurement and NOT experiment-validated.  No "
                        "title-verified SUBOFF force measurement is on disk "
                        "(SUBOFF_A1_PREREGISTRATION.md 2.2).",
        "written_utc": datetime.datetime.now(datetime.timezone.utc)
                       .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "level_dir_Aref_read_from": os.path.abspath(a.level_dir),
        "rule3_plant": plant,
        "condition": {"Re_L": RE_L, "L_m": L_M, "nu_m2_s": NU,
                      "U_m_s": u, "rho_kg_m3": RHO,
                      "rho_note": "CT is a ratio; rhoInf cancels between force and "
                                  "reference force and changes no verdict."},
        "wetted_area_HALF_MODEL_measured_m2": {
            "hull": s_hull, "sail": s_sail, "total": s_tot,
            "source": "constant/polyMesh of the built level, via "
                      "suboff_a1_polymesh.patch_area (rule-3 plant ARMED above)"},
        "hull_limb": {"Cf_ITTC57_at_Re_L": cf_l,
                      "CT_hull_anchor": CT_HULL_ANCHOR,
                      "implied_form_factor_1_plus_k": 1.0 + k_hull,
                      "provenance": "SUBOFF_A1_PREREGISTRATION.md 5.3, inherited "
                                    "from SUBOFF R1's ITTC-1957 + form-factor anchor"},
        "sail_limb": {"chord_m": SAIL_CHORD_M, "t_over_c": SAIL_TOC,
                      "Re_chord": re_c, "Cf_ITTC57_at_Re_chord": cf_c,
                      "form_factor_1_plus_k": 1.0 + k_sail,
                      "form_factor_form": "1 + 2(t/c) + 60(t/c)^4",
                      "CD_sail_on_sail_wetted_area": cd_sail,
                      "method_note": "THE SAME ENGINEERING METHOD as the hull limb: "
                                     "ITTC-1957 friction line at the component's own "
                                     "Reynolds number, times a classical form factor. "
                                     "It is an estimate stacked on an estimate, which "
                                     "is why 5.3 registers the band at +/-15 %, not "
                                     "R1's +/-10 %."},
        "CT_ref": ct_ref,
        "GATE_D2_BAND": {"form": "|CT_cfd - CT_ref| <= 0.15 * CT_ref",
                         "lo": ct_ref * 0.85, "hi": ct_ref * 1.15,
                         "frozen_by": "SUBOFF_A1_PREREGISTRATION.md 5.3"},
        "Aref_rule": "Each level uses ITS OWN measured (hull + sail) wall-patch area "
                     "as forceCoeffs Aref.  CT_ref above uses the FINEST BUILT level's "
                     "hull/sail split and is the SAME number for every level.",
    }

    if a.stl_hull:
        tot, n = stl_area_ascii(a.stl_hull, z_min=0.0)
        out["cross_check_independent"] = {
            "hull_stl_facet_area_z_ge_0_m2": tot, "n_facets_total": n,
            "measured_hull_patch_m2": s_hull,
            "ratio_patch_over_stl": s_hull / tot if tot > 0 else None,
            "EXPECTED_SIGN": "the built hull PATCH must be SMALLER than the bare-hull "
                             "STL half-area, because the sail footprint is cut out of "
                             "it by the union.  A ratio >= 1 is a finding, not a pass.",
        }

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("wetted_area_HALF_MODEL_measured_m2", "hull_limb", "sail_limb",
                       "CT_ref", "GATE_D2_BAND", "rule3_plant")}, indent=2))
    if a.stl_hull:
        print(json.dumps(out["cross_check_independent"], indent=2))


if __name__ == "__main__":
    main()
