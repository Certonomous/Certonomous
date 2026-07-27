"""Derive a defensible reference Cd for the NACA 4412 finite-wing credential.

The number this replaces (models/curriculum/naca4412_wing/reference.yaml,
cd: 0.030) was hand-set in the initial commit with no computation behind it
(see that file's own "notes:" field, added 2026-07-27). This script is the
computation that should have been there: it builds the reference bottom-up
from the two physical contributions to a finite cambered wing's drag at zero
incidence —

    Cd_reference = Cd_section (2D, profile drag)  +  Cd_induced (3D, lift-induced)

— using only cited numbers and one solved input (the wing's own lift
coefficient), never a constant set by hand to land in a particular place.

Term 1 — section (profile) drag
--------------------------------
Cited already in the credential: Abbott & von Doenhoff, "Theory of Wing
Sections" (1959), NACA 4412 section polar, profile drag coefficient in the
range 0.006-0.009 over the low-drag bucket near the section's camber-carried
lift. Taken as a flat range (no distribution assumed beyond it), midpoint
0.0075, half-width 0.0015.

Term 2 — induced drag
----------------------
Classical finite-wing result: Cd_induced = Cl^2 / (pi * e * AR), where AR is
the wing's own aspect ratio (measured off the STL, not assumed) and Cl is the
wing's own solved lift coefficient (from the boundary-layer-resolved solve,
not assumed either). ``e`` is the span efficiency factor; e=1 is the
elliptical-loading ideal, and standard aerodynamics texts (e.g. Anderson,
"Fundamentals of Aerodynamics", discussion of span efficiency) bracket real
unswept wings at e = 0.7-0.85, with the LOW end of that bracket understood to
apply to low-aspect-ratio, untapered, unswept rectangular planforms — exactly
this wing's stated planform (reference.yaml: "aspect ratio ~ 3, extruded
straight"). Rather than pick one e, this script carries the whole bracket
through, so the induced-drag term is itself a range, not a point estimate.

The empirical Oswald formulas fit to typical-aircraft wings (Raymer's
e = 1.78(1 - 0.045 AR^0.68) - 0.64 among them) are reported for context only
and NOT used for the reference: at AR ~ 3 they extrapolate outside the
aspect-ratio range (roughly AR 6-10) they were fit to, and (checked below)
the extrapolation trends the WRONG way for a low-AR wing (predicting e closer
to 1, i.e. LESS induced drag, than the physically-expected strong tip-loss
penalty at this aspect ratio) -- a documented reason to distrust it here
rather than a reason to prefer it.

Band
----
The acceptance band combines THREE independent uncertainty sources, RSS'd
together, none of them picked after seeing the comparison:

  1. Section-drag citation range (Abbott & von Doenhoff): half-width 0.0015.
  2. Induced-drag closure uncertainty (the e = 0.70-0.85 bracket) at the
     chosen Cl.
  3. NUMERICAL (grid) uncertainty, from the wing's own 3-rung mesh-refinement
     study (263k / 645k / 1.85M cells, all with resolved boundary layers).
     Cd and Cl were NOT monotonic across that ladder (see
     naca4412_credential_repair.py rungs medium/fine/finer) — the ladder is
     not in the asymptotic range, so no Richardson/observed-order fit is
     performed. Instead the full observed spread of Cd and of Cl across the
     three rungs is carried through as a direct uncertainty band: Cl feeds
     Cl^2 into the induced-drag term, so an unconverged Cl makes the
     REFERENCE itself move, not only the measured Cd. Omitting this term
     would understate the band by roughly half its final width (see the
     numbers in the module's committed run).

Fixed before any comparison is made; does not depend on where the solved Cd
lands.

Run:
    python3 derive_naca4412_reference.py --cl 0.xxxx
    python3 derive_naca4412_reference.py --cl 0.xxxx --ar 2.9991 \
        --cl-grid-range 0.20955 0.25194 --cd-grid-range 0.018262 0.024478
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SDK))

# --- Term 1: section drag, Abbott & von Doenhoff (1959), NACA 4412 --------
SECTION_SOURCE = ("Abbott & von Doenhoff, Theory of Wing Sections (1959), "
                  "NACA 4412 section polar (profile drag over the low-drag "
                  "bucket near the section's camber-carried lift)")
CD_SECTION_LOW = 0.006
CD_SECTION_HIGH = 0.009
CD_SECTION_MID = (CD_SECTION_LOW + CD_SECTION_HIGH) / 2
CD_SECTION_HALF_WIDTH = (CD_SECTION_HIGH - CD_SECTION_LOW) / 2

# --- Term 2: induced drag bracket, Anderson "Fundamentals of Aerodynamics" -
E_SOURCE = ("Anderson, Fundamentals of Aerodynamics, span efficiency factor "
            "e: e=1 is the elliptical-loading ideal; real unswept wings "
            "bracket e = 0.70-0.85, low end for low-aspect-ratio, untapered, "
            "unswept (rectangular) planforms")
E_LOW = 0.70     # more induced drag (this wing's regime: AR~3, untapered, unswept)
E_HIGH = 0.85    # less induced drag (typical-aircraft end of the bracket)


def raymer_oswald_efficiency(ar: float) -> float:
    """Raymer's empirical straight-wing Oswald efficiency estimate.

    e = 1.78 (1 - 0.045 AR^0.68) - 0.64. Reported for context only (see
    module docstring) — NOT used to set the reference. Included so the
    mismatch with the physical expectation at low AR is visible on the
    record rather than silently omitted.
    """
    return 1.78 * (1 - 0.045 * ar ** 0.68) - 0.64


def induced_drag(cl: float, ar: float, e: float) -> float:
    return cl ** 2 / (math.pi * e * ar)


def derive(cl: float, ar: float, *, cl_grid_range=None, cd_grid_range=None,
          grid_conclusive: bool | None = None) -> dict:
    cdi_low = induced_drag(cl, ar, E_HIGH)   # high e -> lower Cdi
    cdi_high = induced_drag(cl, ar, E_LOW)   # low e -> higher Cdi
    cdi_mid = (cdi_low + cdi_high) / 2
    cdi_half_width = (cdi_high - cdi_low) / 2

    cd_ref = CD_SECTION_MID + cdi_mid

    # Numerical/grid term: the SAME e (bracket midpoint) applied to the
    # observed Cl spread across the mesh-refinement ladder, isolating what an
    # unconverged Cl alone does to the induced-drag term (independent of the
    # e-bracket's own spread, already counted above).
    numerical_half_width = 0.0
    numerical_detail = None
    if cl_grid_range:
        e_mid = (E_LOW + E_HIGH) / 2
        cdi_grid_lo = induced_drag(min(cl_grid_range), ar, e_mid)
        cdi_grid_hi = induced_drag(max(cl_grid_range), ar, e_mid)
        cl_driven_half_width = (cdi_grid_hi - cdi_grid_lo) / 2
        # Also count the solved Cd's own observed grid spread directly -- the
        # measurement side of the comparison, not the reference side, but it
        # belongs in the SAME acceptance band per the same logic (comparing a
        # point reference to an unconverged measurement is not meaningful
        # unless the measurement's own grid uncertainty is on the record too).
        cd_driven_half_width = ((max(cd_grid_range) - min(cd_grid_range)) / 2
                                if cd_grid_range else 0.0)
        numerical_half_width = math.sqrt(cl_driven_half_width ** 2
                                         + cd_driven_half_width ** 2)
        numerical_detail = {
            "cl_grid_range": list(cl_grid_range),
            "cd_grid_range": list(cd_grid_range) if cd_grid_range else None,
            "cd_induced_half_width_from_cl_spread": cl_driven_half_width,
            "cd_half_width_from_cd_spread": cd_driven_half_width,
            "note": ("3-rung ladder (263k/645k/1.85M cells, all with resolved "
                    "boundary layers) was NON-MONOTONIC in both Cd and Cl -- "
                    "not in the asymptotic range. No Richardson/observed-order "
                    "fit is used; the raw observed spread is carried as a "
                    "direct uncertainty term instead."),
        }

    abs_half_width = math.sqrt(CD_SECTION_HALF_WIDTH ** 2 + cdi_half_width ** 2
                               + numerical_half_width ** 2)
    band_rel = abs_half_width / cd_ref

    e_raymer = raymer_oswald_efficiency(ar)
    cdi_raymer = induced_drag(cl, ar, e_raymer)

    return {
        "inputs": {
            "cl_solved": cl, "aspect_ratio": ar,
            "cd_section_range": [CD_SECTION_LOW, CD_SECTION_HIGH],
            "cd_section_mid": CD_SECTION_MID,
            "e_bracket": [E_LOW, E_HIGH],
            "grid_conclusive": grid_conclusive,
        },
        "sources": {"section": SECTION_SOURCE, "induced_drag_e": E_SOURCE},
        "terms": {
            "cd_section_mid": CD_SECTION_MID,
            "cd_section_half_width": CD_SECTION_HALF_WIDTH,
            "cd_induced_low_e_high": cdi_low,
            "cd_induced_high_e_low": cdi_high,
            "cd_induced_mid": cdi_mid,
            "cd_induced_half_width": cdi_half_width,
            "numerical_half_width": numerical_half_width,
            "numerical_detail": numerical_detail,
        },
        "context_only_not_used": {
            "raymer_e_estimate": e_raymer,
            "raymer_cd_induced": cdi_raymer,
            "note": ("Raymer's formula gives e={:.3f} at AR={:.2f} -- HIGHER "
                    "(less induced drag) than this bracket's e=0.70 low end, "
                    "the wrong direction for a low-AR wing; not used for the "
                    "reference. See module docstring.").format(e_raymer, ar),
        },
        "reference": {
            "cd_reference": cd_ref,
            "band_abs": abs_half_width,
            "band_rel": band_rel,
            "cd_low": cd_ref - abs_half_width,
            "cd_high": cd_ref + abs_half_width,
            "band_components_abs": {
                "section_citation": CD_SECTION_HALF_WIDTH,
                "induced_drag_e_bracket": cdi_half_width,
                "numerical_grid": numerical_half_width,
            },
        },
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cl", type=float, required=True,
                  help="Solved lift coefficient (from the boundary-layer-resolved case)")
    p.add_argument("--ar", type=float, default=None,
                  help="Aspect ratio; default measures it off the STL directly")
    p.add_argument("--out", type=Path, default=None,
                  help="Optional path to write the derivation JSON")
    p.add_argument("--cl-grid-range", type=float, nargs=2, default=None,
                  metavar=("LOW", "HIGH"),
                  help="Observed Cl spread across the mesh-refinement ladder")
    p.add_argument("--cd-grid-range", type=float, nargs=2, default=None,
                  metavar=("LOW", "HIGH"),
                  help="Observed Cd spread across the mesh-refinement ladder")
    p.add_argument("--grid-conclusive", choices=["true", "false"], default=None,
                  help="Whether the mesh-refinement ladder reached the "
                       "asymptotic range (state honestly; do not set true to "
                       "pass a case)")
    args = p.parse_args(argv[1:])

    ar = args.ar
    if ar is None:
        from chief_engineer.external_aero import analyse_surface
        geometry = analyse_surface(SDK / "geometry" / "naca4412_wing.stl", streamwise_axis=0)
        ar = geometry["span"] / geometry["length"]
        print(f"aspect ratio measured off the STL: span={geometry['span']:.4f} m, "
             f"chord={geometry['length']:.4f} m -> AR={ar:.4f}")

    grid_conclusive = ({"true": True, "false": False}.get(args.grid_conclusive)
                       if args.grid_conclusive else None)
    result = derive(args.cl, ar, cl_grid_range=args.cl_grid_range,
                    cd_grid_range=args.cd_grid_range,
                    grid_conclusive=grid_conclusive)
    print(json.dumps(result, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2))
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
