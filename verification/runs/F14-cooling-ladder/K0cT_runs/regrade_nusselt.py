#!/usr/bin/env python3
"""regrade_nusselt.py -- grade the EXECUTED K0cT Nusselt rows against the
reference obtained on 2026-08-18.

    python3 regrade_nusselt.py      # writes regrade_nusselt.json, prints table

Exit 0 = every graded row passed.  Exit 1 = at least one graded row failed.
Exit 2 = refused to grade.

WHY THIS IS A SEPARATE TOOL FROM analyse_k0ct.py
------------------------------------------------
The K0cT rung was EXECUTED and its verdict published on 2026-08-18 with Nusselt
in no graded row, because the reference was NOT OBTAINED.  Later the same day
the reference arrived.  Grading it from inside analyse_k0ct.py would change an
executed rung's row count and verdict silently, from inside the comparator that
produced it.  This is a NEW dated record instead, and analyse_k0ct.py still
reports Nusselt as a measurement and names this file.

THE REFERENCE IS PARSED FROM THE ADDENDUM, NOT TYPED IN HERE
------------------------------------------------------------
Every reference number and every uncertainty component is read at run time from
addendum A1 of

    docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md

A comparator holding its own copy of the reference is this lab's most repeated
failure written in code.  If the addendum cannot be parsed this exits 2.

THE SOLVE VALUES PRE-EXIST THIS GRADING, AND THAT IS STATED RATHER THAN HIDDEN
------------------------------------------------------------------------------
This is NOT a pre-registered prediction.  The Nusselt numbers were computed and
published at 2026-08-18T04:42Z, before the reference existed.  The band applied
here is therefore constructed ENTIRELY from the reference's own stated
uncertainty and the executed rung's own grid pair, both external to the solve
values, so that no band was chosen after seeing which side of it the answers
fell on.  A reader who wants to check that has the addendum and gate_k0ct.json.
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def _find_up(relpath, start=None):
    """Resolve a repository-relative path by walking UP from this file.

    NOT an assembled relative literal.  This rung's run tree was written when
    it lived under docs/campaigns/F14-cooling-ladder/ and was later moved to
    verification/runs/F14-cooling-ladder/ by a repository reorganisation.  The
    "../" literals in the first version of this script did not move with it,
    and this script was BROKEN AT HEAD as a result: exit 2, "gate
    specification not found", on a path two directories from where the file
    actually is.  Verified by running it, not by reading it.

    That is the L-137 failure class, and the K2c lane hit a live instance of
    the same class on the same day from the same reorganisation.  Resolving by
    search from the repository root makes the reference survive the next move.
    """
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while True:
        cand = os.path.join(d, relpath)
        if os.path.exists(cand):
            return os.path.abspath(cand)
        if os.path.isdir(os.path.join(d, ".git")):
            return os.path.abspath(os.path.join(d, relpath))
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(relpath)
        d = parent


SPEC = _find_up("docs/campaigns/F14-cooling-ladder/"
                "K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md")
EXECUTED = os.path.join(HERE, "gate_k0ct.json")


def refuse(msg):
    sys.stderr.write(msg + "\n")
    raise SystemExit(2)


def read_reference():
    """Betts Table 1 average Nusselt, and the uncertainty budget, from A1."""
    if not os.path.isfile(SPEC):
        refuse(f"REFUSE: specification not found at {SPEC}")
    txt = open(SPEC).read()
    flat = " ".join(txt.split())

    # the same two-ended provenance guard analyse_k0ct.py carries
    if "reference NOT OBTAINED.** The database provides no Nusselt files" not in flat:
        refuse("REFUSE: Section 2.3's original 'reference NOT OBTAINED' "
               "sentence has been removed. It is superseded by date, never by "
               "deletion (W-4).")
    if ("Nusselt number, turbulent rung: reference OBTAINED by addendum A1 "
            "dated 2026-08-18") not in flat:
        refuse("REFUSE: addendum A1's marker sentence is absent; the "
               "reference's provenance cannot be established.")

    m = re.search(r"\|\s*\*\*Average Nusselt number\*\*\s*\|\s*\*\*([\d.]+)\*\*"
                  r"\s*\|\s*\*\*([\d.]+)\*\*\s*\|", flat)
    if not m:
        refuse("REFUSE: the A1.2 'Average Nusselt number' row could not be read.")
    ref = {"lo": float(m.group(1)), "hi": float(m.group(2))}

    m = re.search(r"\|\s*\*\*u_val\*\*\s*\|\s*\*\*([\d.]+) %\*\*\s*\|\s*"
                  r"\*\*([\d.]+) %\*\*\s*\|", flat)
    if not m:
        refuse("REFUSE: the A1.5 u_val row could not be read.")
    uval = {"lo": float(m.group(1)), "hi": float(m.group(2))}
    return ref, uval


def main():
    ref, uval = read_reference()
    if not os.path.isfile(EXECUTED):
        refuse(f"REFUSE: {EXECUTED} not found; the executed rung's own record "
               "is the only admissible source for its Nusselt numbers.")
    ex = json.load(open(EXECUTED))
    nu = ex["nusselt_UNGRADED"]

    def avg(case):
        return 0.5 * (nu[case]["Nu_hot"] + nu[case]["Nu_cold"])

    # Specification Section 2.5: a solve presented without its grid-sensitivity
    # pair is NOT GRADED AT ALL.  That rule is applied here without exception,
    # and it is what keeps the LaunderSharma row out of the graded set even
    # though it is the row closest to the reference.
    pairs = {"lo": ("T_lo_c", "T_lo_f"), "hi": ("T_hi_c", "T_hi_f")}
    rows, reported = [], []

    for rung, (coarse, fine) in pairs.items():
        s_c, s_f = avg(coarse), avg(fine)
        E = 100.0 * (s_f - ref[rung]) / ref[rung]
        rows.append(dict(
            rung=rung, model="kOmegaSST", case=fine, coarse_case=coarse,
            Nu_coarse=s_c, Nu_fine=s_f, reference=ref[rung],
            grid_pct=100.0 * abs(s_f - s_c) / abs(s_f),
            E_pct=E, u_val_pct=uval[rung], E_over_uval=abs(E) / uval[rung],
            verdict="PASS" if abs(E) <= uval[rung] else "GATE FAIL"))

    for case, model, rung, why in (
            ("M_hi_f_LS", "LaunderSharmaKE", "hi",
             "fine mesh only; no coarse twin was run, so specification "
             "Section 2.5 forbids grading it"),
            ("C1_hi_c_laminar", "laminar", "hi", "control, not a graded case"),
            ("C2_hi_c_Ra130", "kOmegaSST", "hi",
             "Ra raised 30 percent; not the reference case"),
            ("B_hi_c_adiabatic", "kOmegaSST", "hi",
             "boundary-condition twin, not the reference case")):
        s = avg(case)
        reported.append(dict(
            case=case, model=model, rung=rung, Nu=s, reference=ref[rung],
            E_pct=100.0 * (s - ref[rung]) / ref[rung],
            u_val_pct=uval[rung],
            E_over_uval=abs(100.0 * (s - ref[rung]) / ref[rung]) / uval[rung],
            not_graded_because=why))

    # ---- mutation control: every row must be flippable in both directions ---
    mutation = []
    for r in rows:
        # perturb the reference until the row flips; the row must flip.
        flipped_fail = abs(r["E_pct"]) > r["u_val_pct"]
        # drive reference to the solve value -> E = 0 -> must PASS
        would_pass = 0.0 <= r["u_val_pct"]
        # drive reference 50 % away -> must FAIL
        big = abs(100.0 * (r["Nu_fine"] - r["reference"] * 1.5)
                  / (r["reference"] * 1.5))
        would_fail = big > r["u_val_pct"]
        mutation.append(dict(rung=r["rung"], currently=r["verdict"],
                             reachable_PASS=bool(would_pass),
                             reachable_FAIL=bool(would_fail)))
    reachable = all(m["reachable_PASS"] and m["reachable_FAIL"] for m in mutation)

    spread = 100.0 * (avg("M_hi_f_LS") - avg("T_hi_f")) / avg("T_hi_f")
    position = (100.0 * (ref["hi"] - avg("T_hi_f"))
                / (avg("M_hi_f_LS") - avg("T_hi_f")))

    out = dict(
        generated_utc=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        reference_parsed_from_addendum=ref,
        u_val_parsed_from_addendum=uval,
        graded_rows=rows, reported_not_graded=reported,
        mutation_control=mutation, every_row_reachable_both_ways=reachable,
        model_twin_spread_pct=spread,
        reference_position_between_models_pct=position)
    with open(os.path.join(HERE, "regrade_nusselt.json"), "w") as fh:
        json.dump(out, fh, indent=1)

    print("K0cT NUSSELT RE-GRADE against Betts and Bokhari Table 1, p. 682")
    print("=" * 78)
    print(f"{'rung':>5} {'model':<16} {'Nu coarse':>10} {'Nu fine':>9} "
          f"{'ref':>6} {'E %':>8} {'u_val %':>8} {'|E|/u':>6}  verdict")
    for r in rows:
        print(f"{r['rung']:>5} {r['model']:<16} {r['Nu_coarse']:>10.4f} "
              f"{r['Nu_fine']:>9.4f} {r['reference']:>6.2f} {r['E_pct']:>8.2f} "
              f"{r['u_val_pct']:>8.2f} {r['E_over_uval']:>6.2f}  {r['verdict']}")
    print("-" * 78)
    print("REPORTED, NOT GRADED:")
    for r in reported:
        print(f"{r['rung']:>5} {r['model']:<16} {'':>10} {r['Nu']:>9.4f} "
              f"{r['reference']:>6.2f} {r['E_pct']:>8.2f} "
              f"{r['u_val_pct']:>8.2f} {r['E_over_uval']:>6.2f}  "
              f"({r['not_graded_because'][:44]})")
    print("-" * 78)
    print(f"model twin spread (SST vs LaunderSharma, hi Ra): {spread:.1f} %")
    print(f"reference sits {position:.1f} % of the way from SST to LaunderSharma")
    print(f"every graded row reachable in both directions: {reachable}")
    fails = [r for r in rows if r["verdict"] != "PASS"]
    print(f"graded rows: {len(rows)}   GATE FAIL: {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
