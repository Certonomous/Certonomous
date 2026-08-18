#!/usr/bin/env python3
"""grade_d403.py -- grade the re-run legs against K0b's PUBLISHED numbers.

    python3 grade_d403.py        # writes k0b_d403_regrade.json here

Reads the published `k0b_mesh_sensitivity.json` from the committed rung and the
`measured_*.json` files this re-run produced, and states every deviation as a
number.  The Richardson arithmetic is `analyse_k0b_mesh.richardson` imported
VERBATIM from the byte-identical copy in this directory -- a re-run that regrades
a published ladder with a freshly written formula grades the formula.

Thresholds are the ones fixed in
`docs/campaigns/F14-cooling-ladder/K0b_D403_RERUN_PREREGISTRATION.md` section 4
BEFORE the first solve: < 0.1 % reproduced, > 1 % NOT REPRODUCED, and the band
between carries no verdict of its own.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_k0b_mesh as A  # noqa: E402

PUBLISHED = os.path.join(
    A.REPO, "verification", "runs", "F14-cooling-ladder",
    "K0b_mesh_sensitivity", "k0b_mesh_sensitivity.json")

# quantity list: exactly analyse_k0b_mesh.main()'s, in its order
KEYS = ["Nu_avg_hot", "Nu_max_hot", "Nu_min_hot", "V_star_max",
        "U_star_max", "stratification_S_leastsq_mid25pct"]
# reported, never gated on: a sealed cavity with Dirichlet side walls satisfies
# the hot/cold Nusselt closure by construction (VERIFICATION_CHARTER.md:106-111)
IDENTITY_KEYS = ["energy_balance_pct"]
ALSO_REPORTED = ["Nu_avg_cold", "V_star_min", "U_star_min",
                 "x_over_L_at_v_max", "Pr", "dT_K", "cells", "time"]

REPRODUCED_PCT = 0.1
NOT_REPRODUCED_PCT = 1.0


def load(tag):
    with open(os.path.join(HERE, f"measured_{tag}.json")) as fh:
        return json.load(fh)


def dev(new, old):
    """Relative deviation in percent, and the absolute difference."""
    if old == 0:
        return None, new - old
    return 100.0 * (new - old) / abs(old), new - old


def verdict(pct):
    if pct is None:
        return "n/a"
    a = abs(pct)
    if a < REPRODUCED_PCT:
        return "REPRODUCED"
    if a > NOT_REPRODUCED_PCT:
        return "NOT REPRODUCED"
    return "deviating, no verdict (0.1-1 %)"


def main():
    pub = json.load(open(PUBLISHED))
    legs = {t: load(t) for t in
            ("L32", "L64", "L64P", "L128a_endTime4000", "L128b_endTime16000")}

    # which published leg each re-run leg is graded against
    against = {"L32": "32x32", "L64": "64x64", "L64P": "64x64",
               "L128a_endTime4000": "128x128", "L128b_endTime16000": "128x128"}

    out = {"what": "D403 re-run: K0b mesh-sensitivity ladder regraded against "
                   "its own published numbers",
           "published_source": os.path.relpath(PUBLISHED, A.REPO),
           "thresholds_pct": {"reproduced_below": REPRODUCED_PCT,
                              "not_reproduced_above": NOT_REPRODUCED_PCT},
           "deviations": {}, "identities_reported_never_gated": {},
           "bitwise": {}, "richardson": {}, "cost": {}}

    for tag, leg in legs.items():
        p = pub["legs"][against[tag]]
        row = {"graded_against_published_leg": against[tag],
               "time": leg["time"], "published_time": p["time"],
               "cells": leg["cells"]}
        for k in KEYS:
            pct, absd = dev(leg[k], p[k])
            row[k] = {"rerun": leg[k], "published": p[k],
                      "abs_diff": absd, "dev_pct": pct, "verdict": verdict(pct)}
        for k in ALSO_REPORTED:
            if isinstance(leg.get(k), (int, float)) and isinstance(p.get(k), (int, float)):
                pct, absd = dev(leg[k], p[k])
                row[k] = {"rerun": leg[k], "published": p[k],
                          "abs_diff": absd, "dev_pct": pct}
            else:
                row[k] = {"rerun": leg.get(k), "published": p.get(k)}
        out["deviations"][tag] = row
        out["identities_reported_never_gated"][tag] = {
            k: {"rerun": leg[k], "published": p[k],
                "note": "identity on a sealed Dirichlet cavity; reported, never gated"}
            for k in IDENTITY_KEYS}

    # the ladder, rebuilt: the pre-registered triple uses the FRESH 64x64 leg
    for label, fine_tag in (("published_protocol_L32_L64_L128b", "L128b_endTime16000"),
                            ("script_alone_L32_L64_L128a", "L128a_endTime4000")):
        block = {}
        for k in KEYS:
            f1 = legs["L32"][k]
            f2 = legs["L64"][k]
            f3 = legs[fine_tag][k]
            block[k] = dict(coarse=f1, medium=f2, fine=f3,
                            change_64_to_128_pct=100.0 * abs(f3 - f2) / abs(f3),
                            **A.richardson(f1, f2, f3))
            pr = pub["richardson"][k]
            block[k]["published_p"] = pr["p"]
            block[k]["published_GCI_fine_pct"] = pr["GCI_fine_pct"]
            block[k]["published_extrapolated"] = pr["extrapolated"]
        out["richardson"][label] = block

    with open(os.path.join(HERE, "k0b_d403_regrade.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    w = print
    w("=" * 104)
    w("D403 RE-RUN -- K0b mesh sensitivity regraded against its own published numbers")
    w("=" * 104)
    for tag in ("L32", "L64", "L64P", "L128a_endTime4000", "L128b_endTime16000"):
        r = out["deviations"][tag]
        w(f"\n{tag}  (t={r['time']['rerun']}, published leg "
          f"{r['graded_against_published_leg']} at t={r['time']['published']}, "
          f"{r['cells']['rerun']} cells)")
        w(f"  {'quantity':<38}{'re-run':>20}{'published':>20}{'dev %':>14}  verdict")
        for k in KEYS:
            d = r[k]
            pct = "exact" if d["dev_pct"] == 0.0 else f"{d['dev_pct']:.6f}"
            w(f"  {k:<38}{d['rerun']:>20.10f}{d['published']:>20.10f}{pct:>14}  {d['verdict']}")
    w("\n" + "=" * 104)
    for label, block in out["richardson"].items():
        w(f"\nLADDER: {label}")
        w(f"  {'quantity':<38}{'32x32':>12}{'64x64':>12}{'128x128':>12}"
          f"{'64->128 %':>11}{'p':>8}{'GCI %':>9}{'pub p':>8}")
        for k in KEYS:
            d = block[k]
            pp = f"{d['p']:.2f}" if d["p"] is not None else "--"
            gg = f"{d['GCI_fine_pct']:.3f}" if d["GCI_fine_pct"] is not None else "--"
            pubp = f"{d['published_p']:.2f}" if d["published_p"] is not None else "--"
            w(f"  {k:<38}{d['coarse']:>12.4f}{d['medium']:>12.4f}{d['fine']:>12.4f}"
              f"{d['change_64_to_128_pct']:>11.3f}{pp:>8}{gg:>9}{pubp:>8}")
        for k in KEYS:
            if block[k]["p"] is None:
                w(f"    {k}: {block[k]['reason']}")
    w("=" * 104)
    return 0


if __name__ == "__main__":
    sys.exit(main())
