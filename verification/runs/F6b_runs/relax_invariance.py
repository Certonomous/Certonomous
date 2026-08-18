"""F6b relaxation-invariance check (L-47) — scoring script.

Pre-registration: campaign/F6b_RELAXATION_INVARIANCE_PREREGISTRATION.md (ce0b14be).

Reads arm A (the incumbent `medium` case, already on disk) and the two new arms
against the SAME crossing and profile logic `gate.py` uses, imported rather than
re-implemented so that a difference between arms cannot be a difference between
two copies of an analysis.

The bar is the pre-registered one and is not composed here:
  CONFIRMED    |dx_R|/x_R(A) <= 0.5%
  GREY         0.5% < ... <= 5%
  DISAGREEMENT > 5%
and an arm that did not print `SIMPLE solution converged` is INCONCLUSIVE, not a
disagreement -- a run that did not converge is not evidence about where a fixed
point is.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/Certonomous/demo-output/website/campaign/F6b_runs")
import gate as G  # noqa: E402  (same crossing + profile code the record used)

BASE = Path("/home/ubuntu/Certonomous/demo-output/website/campaign/F6b_runs")
ARMS = [
    ("A", "medium", "incumbent p 0.5 / U 0.5 / k 0.7 / omega 0.7 (shipped PH_Breuer)",
     BASE / "log.relax_A_not_run"),
    ("B", "medium_relax_B", "p 0.3 / U 0.7 / k 0.7 / omega 0.7", BASE / "log.relax_B"),
    ("C", "medium_relax_C", "p 0.3 / U 0.3 / k 0.5 / omega 0.5", BASE / "log.relax_C"),
]
CONFIRMED, GREY = 0.005, 0.05


def relax_of(case):
    s = (BASE / case / "system" / "fvSolution").read_text()
    blk = s[s.index("relaxationFactors"):]
    return {k: float(v) for k, v in re.findall(r"(\w+)\s+([0-9.]+);", blk)}


def converged(log):
    if not log.exists():
        return None, None
    t = log.read_text()
    m = re.search(r"SIMPLE solution converged in (\d+) iterations", t)
    n = t.count("SIMPLE solution converged")
    return (n, int(m.group(1)) if m else None)


def latest_time(case):
    ts = sorted(int(p.name) for p in (BASE / case).iterdir()
                if p.name.isdigit() and int(p.name) > 0)
    return ts[-1] if ts else None


def main():
    interp = G.les_interp()
    out = {"preregistration": "campaign/F6b_RELAXATION_INVARIANCE_PREREGISTRATION.md",
           "preregistration_commit": "ce0b14be3715d165cfc1415092c843529a99f155",
           "bar": {"confirmed_rel": CONFIRMED, "grey_upper_rel": GREY,
                   "separation_abs_h": 0.05, "profile_mae_pp": 1.0,
                   "required_n_crossings": 2},
           "arms": {}}
    for arm, case, label, log in ARMS:
        t = latest_time(case)
        if t is None:
            out["arms"][arm] = {"case": case, "state": "NO WRITTEN TIME"}
            continue
        x, tx, cr, utau = G.rung(case, t)
        prof, overall = G.profiles(case, t, interp)
        nsent, nit = converged(log)
        if arm == "A":  # incumbent: convergence evidence is the archived extract
            nsent, nit = 1, 5997
        out["arms"][arm] = {
            "case": case, "relaxation_label": label,
            "relaxation_read_from_dict": relax_of(case),
            "time_written": t,
            "convergence_sentences": nsent,
            "converged_at_iteration": nit,
            "converged": bool(nsent),
            "crossings_x_over_h": [round(c, 4) for c in cr],
            "n_crossings": len(cr),
            "separation_x_over_h": round(cr[0], 4) if len(cr) == 2 else None,
            "reattachment_x_over_h": round(cr[1], 4) if len(cr) == 2 else None,
            "steady_bubble": len(cr) == 2,
            "profile_scaled_mae_overall_percent": round(overall, 3) if overall else None,
        }
    A = out["arms"]["A"]
    out["comparisons"] = {}
    for arm in ("B", "C"):
        r = out["arms"].get(arm, {})
        c = {"vs": "A"}
        if not r.get("converged"):
            c["verdict"] = "INCONCLUSIVE"
            c["reason"] = ("arm did not print `SIMPLE solution converged` before its "
                           "20,000-iteration cap; a run that did not converge is not "
                           "evidence about where a fixed point is")
        elif not r.get("steady_bubble"):
            c["verdict"] = "INCONCLUSIVE"
            c["reason"] = (f"{r.get('n_crossings')} skin-friction sign changes, not 2 — "
                           "no separation or reattachment point is defined")
        else:
            d = abs(r["reattachment_x_over_h"] - A["reattachment_x_over_h"])
            rel = d / A["reattachment_x_over_h"]
            c["d_reattachment_x_over_h"] = round(d, 5)
            c["rel_reattachment"] = round(rel, 6)
            c["rel_reattachment_percent"] = round(100 * rel, 4)
            c["d_separation_h"] = round(abs(r["separation_x_over_h"] - A["separation_x_over_h"]), 5)
            c["d_profile_mae_pp"] = round(
                r["profile_scaled_mae_overall_percent"] - A["profile_scaled_mae_overall_percent"], 3)
            c["verdict"] = ("CONFIRMED" if rel <= CONFIRMED
                            else "GREY" if rel <= GREY else "DISAGREEMENT")
            c["separation_within_bar"] = c["d_separation_h"] <= 0.05
            c["profile_within_bar"] = abs(c["d_profile_mae_pp"]) <= 1.0
            c["outside_literature_band_4.21_4.70"] = not (
                4.21 <= r["reattachment_x_over_h"] <= 4.70)
        out["comparisons"][arm] = c

    # ---- positive control (pre-registration Addendum 1, commit 110da419) ----
    # The incumbent case at the INCUMBENT relaxation, stopped early: known-present
    # specimens of an unconverged field.  The instrument must fail to certify at
    # one or more of them, or arms B and C carry no evidence.
    pc = {"case": "medium_relax_PC",
          "relaxation_read_from_dict": relax_of("medium_relax_PC"),
          "note": ("same relaxation as arm A; the ONLY difference is early stopping, "
                   "so any disagreement it shows is non-convergence and nothing else"),
          "samples": {}}
    pcdir = BASE / "medium_relax_PC"
    if pcdir.exists():
        for t in sorted(int(p.name) for p in pcdir.iterdir()
                        if p.name.isdigit() and int(p.name) > 0):
            x, tx, cr, utau = G.rung("medium_relax_PC", t)
            s = {"n_crossings": len(cr),
                 "crossings_x_over_h": [round(c, 4) for c in cr]}
            if len(cr) == 2:
                rel = abs(cr[1] - A["reattachment_x_over_h"]) / A["reattachment_x_over_h"]
                s["reattachment_x_over_h"] = round(cr[1], 4)
                s["rel_reattachment_percent"] = round(100 * rel, 4)
                s["certifies"] = rel <= CONFIRMED
                s["verdict"] = ("CONFIRMED" if rel <= CONFIRMED
                                else "GREY" if rel <= GREY else "DISAGREEMENT")
            else:
                s["certifies"] = False
                s["verdict"] = "NO REATTACHMENT DEFINED (n_crossings != 2)"
            pc["samples"][str(t)] = s
        fired = [t for t, s in pc["samples"].items() if not s["certifies"]]
        pc["instrument_fired_at_iterations"] = fired
        pc["instrument_can_produce_disagreement"] = bool(fired)
        pc["conclusion"] = (
            "POSITIVE CONTROL PASSES — the instrument fails to certify an unconverged "
            "field on this exact case, so agreement between arms is informative"
            if fired else
            "POSITIVE CONTROL FAILS — the instrument certified every unconverged field, "
            "so the arms' agreement carries no evidence and must be reported as such")
    out["positive_control"] = pc
    (BASE / "relax_invariance.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
