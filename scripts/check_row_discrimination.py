#!/usr/bin/env python3
r"""Does each graded gate row separate the hypothesis it grades from that
hypothesis being ABSENT.

WHY THIS EXISTS (docket D413; the K0cS re-gate of 2026-08-18)
============================================================
`docs/charters/VERIFICATION_CHARTER.md` section 2a already refuses one kind of
hollow row: *"A gate whose quantity is derivable by construction from its own
inputs is an IDENTITY, not a control."* That rule catches a row whose value is
fixed by ALGEBRA.

K0cS found the sibling, whose value is fixed by nothing the hypothesis controls.
The rung graded three turbulence closures against Ampofo and Karayiannis (2003)
and ran a registered RECOGNITION control, C1, with the turbulence model switched
off. The reading:

    C1, NO turbulence model     passed G3, G4, G5, G9   -- four rows
    kOmegaSST, fine mesh        passed G5, G9           -- two rows

**The set of rows kOmegaSST passed that no-model-at-all did not pass was
EMPTY.** G5 and G9 read PASS for a closure and PASS for its absence, so neither
PASS was evidence about the closure. On G5 the two answers sat 0.0055 percent
apart on the same mesh.

The rung's own mutation control had already stamped
`every_row_reachable_both_ways: true` over all twenty graded rows. It was not
wrong. It perturbs the MEASURED NUMBER and asks whether the verdict can move;
this check perturbs the HYPOTHESIS and asks whether the verdict does move. A row
can pass the first and fail the second, and two rows did.

THE RULE, AND WHERE IT STOPS
============================
A row that GRADES a hypothesis is not the same object as a row that GUARDS a
run, and only the first is covered.

    GRADE row   Its verdict is read as evidence about the hypothesis under test.
                Its referent comes from outside the run -- an experiment, exact
                theory, a benchmark. A FAIL withdraws the HYPOTHESIS. It is
                counted in the rung's "N of M rows" tally.

    GUARD row   Its verdict is read as evidence about the RUN. Its referent is
                an invariant every valid run of any hypothesis must satisfy --
                conservation closure, convergence, a boundary condition applied,
                a marker written. A FAIL withdraws the RUN, not the hypothesis:
                the numbers are not evidence yet and it is re-run. It is a
                precondition for reading the other rows and is counted in no
                tally.

A GUARD row is SUPPOSED to pass for the treatment and for the trivial baseline
alike. Demanding that it discriminate is section 17a's over-reach, which "looks
like rigour while it is happening", so guards are exempt by declaration -- and
the declaration is what D3 below makes binding. A guard MAY discriminate
(K0cS's heat-balance closure does, because the laminar arm is unsteady); it is
simply never required to.

The one-question test that separates them, and it is asked at creation:

    IF THIS ROW FAILS, WHAT IS WITHDRAWN -- the hypothesis, or the run?

WHERE THE LINE IS GENUINELY FUZZY, stated because a rule with a boundary nobody
can state gets applied wrongly:

  1. **A rung with no runnable null.** "Does this solver solve the equations"
     has no no-solver arm. The rule is then UNMEASURABLE, not satisfied, and
     this check prints those rows in their own bucket. UNMEASURED is never
     printed as clean -- the lab has twice shipped a check whose "no violations"
     meant "no population".
  2. **A rung that IS an A/B by construction.** K2e sweeps Boussinesq against
     variable-density on identical geometry; the separation IS the measurement,
     so a discrimination test on top of it is circular. Such rungs are declared
     `design: AB` and excluded, and the exclusion is stated per rung.
  3. **A row that is both.** K0cS's heat balance is a near-identity on a sealed
     cavity (guard) and it is what found a 10-27 percent Nusselt error in the
     comparator (instrument). Classified by what its verdict is COUNTED toward,
     which is nothing, so: guard.
  4. **What counts as the trivial baseline is a judgement, not a datum.** For a
     turbulence closure it is the model switched off. For a correction it is the
     uncorrected run. For a mesh claim it is the coarser mesh. The null arm is
     therefore DECLARED in the registry below with the record that registered
     it, never inferred, and a wrong null gives a wrong answer with no warning.

THE RULES ENFORCED
==================
    D1-HOLLOW-PASS   A GRADE row on a GRADED arm reads PASS, and the declared
                     null arm reads PASS on the same row. The PASS does not
                     separate the hypothesis from its absence and may not be
                     counted toward the hypothesis's verdict. The separation
                     names the remedy: under one band, the QUANTITY is inert and
                     the row should be replaced or restated as a measurement;
                     one band or more, the quantity is fine and the BAND is
                     wider than the effect it must resolve.
    D2-INERT-ROW     A GRADE row on a GRADED arm reads GATE FAIL, the null arm
                     reads GATE FAIL, and the two are separated by less than one
                     band. The row fails for a reason the hypothesis does not
                     control, so the FAIL is not evidence against it either.
                     A FAIL/FAIL pair that IS separated is not flagged: the row
                     grades, both arms are simply outside.
    D3-GUARD-GRADED  A row declared GUARD appears in the rung's graded tally.
                     The guard exemption from D1 and D2 is sound only while the
                     row grades nothing; this is the smuggling path and it is
                     the reason the exemption has teeth.

Reported, and never a violation:
    UNMEASURED       A graded rung, arm or row with no null value on disk. It is
                     counted and named in its own bucket.

Every rule carries a planted control exercised by `--selftest`, and the negative
controls include the shape that must NOT fire: a guard row displaying the exact
hollow-pass signature on real data. `theta_centre` on K0cS reads PASS for
kOmegaSST and PASS for the laminar null 0.19 bands apart, and it is correct that
it does -- Tian p. 862 states a Boussinesq solve returns 0.5 by symmetry, so the
row measures the non-Boussinesq defect and never the closure. A check that
condemned it would condemn the whole inventory and be scrolled past.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DEFAULT = "/home/ubuntu/Certonomous"

PASS = "PASS"
FAIL = "GATE FAIL"


# --------------------------------------------------------------------------
# Deviation conventions. Copied from the comparators that produced the run
# trees, not re-invented: `analyse_k0cs.py` grades REL/ABS, and K0cT's
# antisymmetry row is graded on the solve's OWN defect, which its gate json
# records in the row note.
# --------------------------------------------------------------------------
def deviation(kind: str, reference: float, value: float) -> float:
    if kind == "REL":
        return 100.0 * abs(value - reference) / abs(reference)
    if kind == "ABS":
        return abs(value - reference)
    if kind == "SELF":
        return abs(value)
    raise ValueError(f"unknown deviation kind {kind!r}")


def separation(kind: str, reference: float, a: float, b: float) -> float:
    """How far the two arms sit apart, in the row's own deviation units."""
    if kind == "REL":
        return 100.0 * abs(a - b) / abs(reference)
    return abs(a - b)


def verdict_of(kind: str, reference: float, band: float, value: float) -> str:
    return PASS if deviation(kind, reference, value) <= band else FAIL


# --------------------------------------------------------------------------
# The registry. What is DATA is read from the gate json on disk. What is a
# JUDGEMENT -- which arm is the null, which rows guard rather than grade, which
# arms were graded -- is written here with the record that settled it, because
# a judgement inferred by a script is a judgement nobody made.
# --------------------------------------------------------------------------
K0CS = "verification/runs/F14-cooling-ladder/K0cS_runs/gate_k0cs.json"
K0CT = "verification/runs/F14-cooling-ladder/K0cT_runs/gate_k0ct.json"

REGISTRY = [
    {
        "rung": "K0cS",
        "hypothesis": "the turbulence closure, on the Ampofo square cavity at Ra 1.58e9",
        "gate_json": K0CS,
        "loader": "k0cs",
        "design": "TREATMENT_VS_NULL",
        # C1 was registered as a RECOGNITION control in K0cS_PREREGISTRATION.md
        # BEFORE the run, with the turbulence model switched off. It is the null
        # arm by its own registration and not by hindsight.
        "null_arm": "C1_laminar",
        "null_registered_in":
            "docs/campaigns/F14-cooling-ladder/K0cS_PREREGISTRATION.md, control C1",
        # C1 ran on the COARSE mesh only. The graded verdict is taken on the
        # fine mesh, so the fine arms carry a mesh confound; the coarse arms are
        # mesh-matched to the null and are carried for exactly that reason.
        "arms": {
            "S_SST_f": {"model": "kOmegaSST", "mesh": "fine", "graded": True},
            "S_KE_f": {"model": "kEpsilon", "mesh": "fine", "graded": True},
            "S_SST_c": {"model": "kOmegaSST", "mesh": "coarse", "graded": False,
                        "note": "mesh-matched to the null"},
            "S_KE_c": {"model": "kEpsilon", "mesh": "coarse", "graded": False,
                       "note": "mesh-matched to the null"},
            "S_LS_c": {"model": "LaunderSharmaKE", "mesh": "coarse", "graded": False,
                       "note": "REFUSED on convergence, graded nothing"},
            "S_LS_f": {"model": "LaunderSharmaKE", "mesh": "fine", "graded": False,
                       "note": "REFUSED on convergence, graded nothing"},
            "C4_adiabatic": {"model": "kOmegaSST", "mesh": "coarse", "graded": False,
                             "note": "SENSITIVITY arm, boundary condition changed"},
        },
        # Guard rows. K0cS reports all three and grades none of them
        # (K0cS_RESULTS.md section 6). Their bands are set HERE and not in the
        # gate specification, because the specification declines to band a row
        # it never grades; they are carried so the check has live negative
        # controls on real data. They grade nothing, here or there.
        "guards": [
            {"row": "H1", "quantity": "theta_centre", "reference": 0.5, "band": 0.05,
             "kind": "ABS",
             "why": "Boussinesq symmetry fixes 0.5 (Tian p. 862); the row measures "
                    "the non-Boussinesq defect, never the closure"},
            {"row": "H2", "quantity": "heat_balance_pct", "reference": 0.0, "band": 1.0,
             "kind": "ABS",
             "why": "near-identity on a sealed impermeable domain "
                    "(VERIFICATION_CHARTER.md:106-111)"},
        ],
    },
    {
        "rung": "K0cT-hi",
        "hypothesis": "the turbulence closure, on the Betts tall cavity at Ra 1.43e6",
        "gate_json": K0CT,
        "loader": "k0ct",
        "loader_arg": "hi",
        "design": "TREATMENT_VS_NULL",
        "null_arm": "C1_hi_c_laminar",
        "null_registered_in":
            "gate_k0ct.json control C1, kind RECOGNITION, prediction registered "
            "before the control ran",
        "arms": {
            "T_hi_f": {"model": "kOmegaSST", "mesh": "fine", "graded": True},
            "T_hi_c": {"model": "kOmegaSST", "mesh": "coarse", "graded": False,
                       "note": "mesh-matched to the null"},
            "M_hi_f_LS": {"model": "LaunderSharmaKE", "mesh": "fine", "graded": False,
                          "note": "model-form comparison, graded nothing"},
        },
        "guards": [],
    },
    {
        "rung": "K0cT-lo",
        "hypothesis": "the turbulence closure, on the Betts tall cavity at Ra 0.86e6",
        "gate_json": K0CT,
        "loader": "k0ct",
        "loader_arg": "lo",
        "design": "TREATMENT_VS_NULL",
        # The turbulence-off control was run at the HIGH Rayleigh number only.
        # There is no null arm for this rung on disk and this check does not
        # borrow the other rung's: a null at a different Rayleigh number is a
        # different null.
        "null_arm": None,
        "null_registered_in": "none -- C1 was run at the hi rung only",
        "arms": {"T_lo_f": {"model": "kOmegaSST", "mesh": "fine", "graded": True}},
        "guards": [],
    },
    {
        "rung": "K0c-Ra1e5",
        "hypothesis": "the laminar buoyant solver, on the de Vahl Davis cavity at Ra 1e5",
        "gate_json": "verification/runs/F14-cooling-ladder/K0c_runs/gate_k0c.json",
        "loader": "k0c",
        "loader_arg": "100000.0",
        "design": "TREATMENT_VS_NULL",
        # C1_g0 is an exact twin of the graded Ra = 1e5 fine case with
        # constant/g set to (0 0 0), registered as a RECOGNITION control before
        # it ran. With no buoyancy source the cavity solves pure conduction, so
        # it is the trivial baseline for "this solver reproduces buoyancy-driven
        # convection".
        "null_arm": "C1_Ra1e5_m128_g0",
        "null_registered_in": "gate_k0c.json control_predictions_registered, C1",
        "arms": {
            "Ra1e5_m128": {"model": "laminar buoyant", "mesh": "fine", "graded": True},
            "Ra1e5_m64": {"model": "laminar buoyant", "mesh": "coarse", "graded": False,
                          "note": "coarse leg of the mandatory pair"},
        },
        # `docs/VALIDATION_INVENTORY.md` section 7.1 lists all four K0c
        # energy-balance rows as a DEMONSTRATED identity: on a sealed
        # impermeable domain the discrete temperature equation conserves at
        # every iteration, converged or not. The record excludes them from the
        # rung's evidence; the comparator output still carries them in
        # `gate_rows`, which is what D3 is for.
        "guards": [
            {"row": "H1-energy-balance", "quantity": "energy_balance_pct",
             "reference": 0.0, "band": 0.5, "kind": "ABS",
             "why": "near-identity on a sealed impermeable domain "
                    "(VERIFICATION_CHARTER.md:106-111; VALIDATION_INVENTORY.md 7.1)"},
        ],
    },
    {
        "rung": "K0c-other-Ra",
        "hypothesis": "the laminar buoyant solver at Ra 1e3, 1e4 and 1e6",
        "gate_json": "verification/runs/F14-cooling-ladder/K0c_runs/gate_k0c.json",
        "loader": "k0c",
        "loader_arg": "1000.0,10000.0,1000000.0",
        "design": "TREATMENT_VS_NULL",
        # C1_g0 was built as a twin of the Ra = 1e5 case. A gravity-off twin at
        # a different Rayleigh number is a different null, and this check does
        # not borrow one.
        "null_arm": None,
        "null_registered_in": "none -- C1_g0 twins the Ra = 1e5 case only",
        "arms": {"Ra1e3_m64": {"model": "laminar buoyant", "mesh": "fine", "graded": True}},
        "guards": [],
    },
    {
        "rung": "K2e",
        "hypothesis": "where the Boussinesq approximation stops being right",
        "gate_json": "verification/runs/F14-cooling-ladder/K2e_runs/gate_k2e.json",
        "loader": None,
        # Boundary case 2 of the docstring. K2e's every row IS a difference
        # between the treatment (variable density) and the null (Boussinesq) on
        # identical geometry, so the discrimination is the measurement and a
        # discrimination test on top of it restates its own input.
        "design": "AB",
        "null_arm": None,
        "null_registered_in": "not applicable -- the rung is an A/B by construction",
        "arms": {},
        "guards": [],
    },
]


# --------------------------------------------------------------------------
# Loaders. Each returns (rows, arms): rows are row definitions, arms map an arm
# name to {quantity: value}. Values that a case cannot have are None and travel
# as None -- an adiabatic case has no bottom-wall Nusselt number, and inventing
# one would be the failure section 17a names.
# --------------------------------------------------------------------------
def load_k0cs(doc: dict, _arg=None):
    ref = doc["reference_parsed_from_spec"]
    rows = [
        {"row": r, "quantity": ref[r]["quantity"], "reference": ref[r]["reference"],
         "band": ref[r]["band"], "kind": ref[r]["kind"], "role": "GRADE"}
        for r in sorted(ref, key=lambda x: int(x[1:]))
    ]
    arms = {name: dict(case["measure"]) for name, case in doc["cases"].items()}
    return rows, arms


K0CT_MAP = {
    "core stratification S": ("S", "ABS"),
    "core stratification S (bound)": ("S", "ABS"),
    "mid-height peak upward velocity (magnitude)": ("Vup", "REL"),
    "mid-height peak upward velocity (location)": ("Vup_x", "ABS"),
    "mid-height peak downward velocity (magnitude)": ("Vdn", "REL"),
    "mid-height peak downward velocity (location)": ("Vdn_x", "ABS"),
    "mid-width temperature at y/H = 0.30": ("Tmid_C:0", "ABS"),
    "mid-width temperature at y/H = 0.50": ("Tmid_C:1", "ABS"),
    "mid-width temperature at y/H = 0.70": ("Tmid_C:2", "ABS"),
    # The gate json's own note: "graded on the solve's own defect, not on its
    # difference from the experiment's".
    "antisymmetry defect of the two peaks": ("asym", "SELF"),
}


def load_k0ct(doc: dict, rung: str):
    rows = []
    for i, r in enumerate(doc["graded_rows"]):
        if r["rung"] != rung:
            continue
        key, kind = K0CT_MAP[r["quantity"]]
        # PREFER THE ROW'S OWN TAG.  f"R{i}" is positional, so it renames every
        # row after any retirement and silently re-points historical citations.
        # Comparators that tag their own rows (K0cS as G1..G10, K0cT as R0..R17
        # assigned before the split) are authoritative; the positional form is
        # only a fallback for a document that carries no tag at all.
        rows.append({"row": r.get("row") or f"R{i}",
                     "quantity": key, "reference": r["reference"],
                     "band": r["band"], "kind": kind, "role": "GRADE",
                     "label": r["quantity"]})
    arms = {}
    for name, case in doc["cases"].items():
        m = case["measure"]
        flat = {k: v for k, v in m.items() if not isinstance(v, list)}
        for k, v in m.items():
            if isinstance(v, list):
                for j, el in enumerate(v):
                    flat[f"{k}:{j}"] = el
        arms[name] = flat
    return rows, arms


K0C_MAP = {
    "Nu_avg": ("Nu_avg", "REL"), "Nu_max": ("Nu_max", "REL"),
    "Nu_min": ("Nu_min", "REL"), "u1max": ("u1max", "REL"),
    "u2max": ("u2max", "REL"),
    # Reference 0, so the gate json's own deviation for this row IS the value.
    "energy_balance": ("energy_balance_pct", "ABS"),
}


def load_k0c(doc: dict, ra_arg: str):
    """K0c grades six quantities at each of four Rayleigh numbers.

    `ra_arg` is a comma-separated list of Rayleigh numbers to take, because the
    turbulence-off... gravity-off control C1_g0 is an exact twin of the Ra = 1e5
    fine case ONLY, so only that Rayleigh number has a null arm on disk.
    """
    wanted = {float(x) for x in ra_arg.split(",")}
    rows = []
    for r in doc["gate_rows"]:
        if r["Ra"] not in wanted:
            continue
        key, kind = K0C_MAP[r["quantity"]]
        rows.append({"row": f"{r['quantity']}@{r['Ra']:.0e}", "quantity": key,
                     "reference": r["reference"], "band": r["band_pct"],
                     "kind": kind, "role": "GRADE", "label": r["quantity"]})
    arms = {name: dict(case) for name, case in doc["cases"].items()}
    return rows, arms


LOADERS = {"k0cs": load_k0cs, "k0ct": load_k0ct, "k0c": load_k0c}


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------
class Finding:
    def __init__(self, rule, rung, arm, row, why):
        self.rule, self.rung, self.arm, self.row, self.why = rule, rung, arm, row, why

    def __str__(self):
        return f"  [{self.rule}] {self.rung} / {self.arm} / {self.row}\n      {self.why}"


def classify(row, treat_value, null_value):
    """Return (class, verdict_treatment, verdict_null, separation_in_bands)."""
    if treat_value is None or null_value is None:
        return "UNMEASURED", None, None, None
    k, ref, band = row["kind"], row["reference"], row["band"]
    vt = verdict_of(k, ref, band, treat_value)
    vn = verdict_of(k, ref, band, null_value)
    sep = separation(k, ref, treat_value, null_value) / band
    if vt != vn:
        return "DISCRIMINATES", vt, vn, sep
    if vt == PASS:
        return "HOLLOW PASS", vt, vn, sep
    return ("INERT FAIL" if sep < 1.0 else "BOTH FAIL, SEPARATED"), vt, vn, sep


def evaluate(root: Path, registry=None, docs=None):
    """Measure every registered rung. `docs` injects gate documents for selftest."""
    registry = REGISTRY if registry is None else registry
    findings: list[Finding] = []
    report = []
    for spec in registry:
        entry = {"rung": spec["rung"], "design": spec["design"],
                 "null_arm": spec["null_arm"], "cells": [], "skipped": None}
        if spec["design"] == "AB":
            entry["skipped"] = ("A/B by construction: the separation IS the "
                                "measurement, so a discrimination test restates it")
            report.append(entry)
            continue
        if docs is not None and spec["rung"] in docs:
            doc = docs[spec["rung"]]
        else:
            p = root / spec["gate_json"]
            if not p.exists():
                entry["skipped"] = f"gate json absent: {spec['gate_json']}"
                report.append(entry)
                continue
            doc = json.loads(p.read_text())
        rows, arms = LOADERS[spec["loader"]](doc, spec.get("loader_arg"))

        graded_row_ids = {r["row"] for r in rows}
        for g in spec["guards"]:
            if g["row"] in graded_row_ids or g["quantity"] in {r["quantity"] for r in rows}:
                findings.append(Finding(
                    "D3-GUARD-GRADED", spec["rung"], "-", g["row"],
                    f"declared GUARD but its quantity {g['quantity']!r} is in the "
                    f"rung's graded tally; the guard exemption from D1 and D2 is "
                    f"sound only while the row grades nothing"))
            rows = rows + [dict(g, role="GUARD")]

        null = spec["null_arm"]
        if null is None:
            entry["skipped"] = (f"no null arm on disk ({spec['null_registered_in']}); "
                                f"{len([r for r in rows if r['role'] == 'GRADE'])} graded "
                                f"rows x {len(spec['arms'])} arms UNMEASURED")
            entry["unmeasured_rows"] = (
                len([r for r in rows if r["role"] == "GRADE"]) * len(spec["arms"]))
            report.append(entry)
            continue
        if null not in arms:
            entry["skipped"] = f"declared null arm {null!r} is not in the run tree"
            report.append(entry)
            continue

        for arm_name, arm_meta in spec["arms"].items():
            if arm_name not in arms:
                entry["cells"].append({"arm": arm_name, "row": "-", "class": "UNMEASURED",
                                       "why": "arm not in the run tree"})
                continue
            for row in rows:
                tv = arms[arm_name].get(row["quantity"])
                nv = arms[null].get(row["quantity"])
                cls, vt, vn, sep = classify(row, tv, nv)
                cell = {"arm": arm_name, "row": row["row"],
                        "label": row.get("label", row["quantity"]),
                        "role": row["role"], "graded_arm": arm_meta["graded"],
                        "class": cls, "verdict": vt, "null_verdict": vn,
                        "sep_bands": sep, "treat": tv, "null": nv}
                entry["cells"].append(cell)
                if row["role"] != "GRADE" or not arm_meta["graded"]:
                    continue
                if cls == "HOLLOW PASS":
                    remedy = (
                        "the QUANTITY barely moves when the hypothesis is removed"
                        if sep < 0.25 else
                        f"the quantity moved {sep:.2f} bands, so the BAND is wide "
                        f"enough to admit the null arm as well")
                    findings.append(Finding(
                        "D1-HOLLOW-PASS", spec["rung"], arm_name, row["row"],
                        f"{row.get('label', row['quantity'])}: PASS for the treatment "
                        f"and PASS for the null arm {null}, {sep:.3f} bands apart "
                        f"({tv:.6g} against {nv:.6g}) -- {remedy}"))
                elif cls == "INERT FAIL":
                    findings.append(Finding(
                        "D2-INERT-ROW", spec["rung"], arm_name, row["row"],
                        f"{row.get('label', row['quantity'])}: GATE FAIL for the "
                        f"treatment and GATE FAIL for the null arm {null}, only "
                        f"{sep:.3f} bands apart ({tv:.6g} against {nv:.6g}) -- the row "
                        f"fails for a reason the hypothesis does not control"))
        report.append(entry)
    return findings, report


# --------------------------------------------------------------------------
# Printing. Every verdict carries its population size beside it. A zero over an
# empty population is not a pass; it is a check that did not run.
# --------------------------------------------------------------------------
def print_report(report, findings, verbose):
    graded_cells = unmeasured = 0
    for entry in report:
        print(f"\n=== {entry['rung']}  (design {entry['design']}, "
              f"null arm {entry['null_arm'] or 'NONE'})")
        if entry["skipped"]:
            print(f"    NOT MEASURED: {entry['skipped']}")
            unmeasured += entry.get("unmeasured_rows", 0)
            continue
        counts: dict[str, int] = {}
        for c in entry["cells"]:
            counts[c["class"]] = counts.get(c["class"], 0) + 1
            if c["class"] == "UNMEASURED":
                unmeasured += 1
            if c.get("role") == "GRADE" and c.get("graded_arm"):
                graded_cells += 1
        for arm in dict.fromkeys(c["arm"] for c in entry["cells"]):
            cells = [c for c in entry["cells"] if c["arm"] == arm]
            tag = "GRADED" if cells and cells[0].get("graded_arm") else "measured"
            hollow = [c["row"] for c in cells
                      if c["class"] == "HOLLOW PASS" and c.get("role") == "GRADE"]
            disc = [c["row"] for c in cells
                    if c["class"] == "DISCRIMINATES" and c.get("role") == "GRADE"]
            n = len([c for c in cells if c.get("role") == "GRADE"])
            print(f"    {arm:16} {tag:8}  {n} grade rows: "
                  f"{len(disc)} discriminate, {len(hollow)} hollow pass"
                  f"{'  ' + ','.join(hollow) if hollow else ''}")
            if verbose:
                for c in cells:
                    if c["class"] == "UNMEASURED":
                        print(f"        {c['row']:5} {str(c.get('label', ''))[:34]:34} "
                              f"{'UNMEASURED':22}")
                        continue
                    print(f"        {c['row']:5} {str(c['label'])[:34]:34} "
                          f"{c['class']:22} {c['role']:5} "
                          f"treat={c['verdict']:9} null={c['null_verdict']:9} "
                          f"sep={c['sep_bands']:7.3f} bands")
        print(f"    classes: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print()
    print(f"POPULATION: {len(report)} registered rungs; "
          f"{graded_cells} (graded row x graded arm) cells evaluated against a "
          f"declared null arm; {unmeasured} cells UNMEASURED")
    if graded_cells == 0:
        print("NOT A RESULT: no cell was evaluated, so this check did not run.")
        return 2
    if not findings:
        print(f"PASS: 0 violations over {graded_cells} evaluated cells.")
        return 0
    by_rule: dict[str, list] = {}
    for f in findings:
        by_rule.setdefault(f.rule, []).append(f)
    for rule in sorted(by_rule):
        print(f"\n{rule}  ({len(by_rule[rule])})")
        for f in by_rule[rule]:
            print(str(f))
    print(f"\nGATE FAIL: {len(findings)} violations over {graded_cells} "
          f"evaluated cells, across {len(by_rule)} rules.")
    return 1


# --------------------------------------------------------------------------
# Planted controls. Positives are shapes the rule exists to catch. Negatives are
# rows that legitimately do not discriminate, or legitimately are not covered,
# and MUST survive -- a check that condemns the whole inventory gets scrolled
# past, which is how a check becomes the decoration it was built to detect.
# --------------------------------------------------------------------------
def _synthetic():
    """A gate document in the K0cS shape, every row planted deliberately.

    Band is 10 percent REL on a reference of 100 throughout, so one band is ten
    units of the quantity and every number below can be read by eye.
    """
    ref, treat, null, guard_vals = {}, {}, {}, {}
    plant = [
        # row, treatment, null, expected class, expected rule (None = must survive)
        ("P1", 103.0, 97.0, "HOLLOW PASS", "D1-HOLLOW-PASS"),   # both pass, 0.6 bands
        ("P2", 109.0, 91.0, "HOLLOW PASS", "D1-HOLLOW-PASS"),   # both pass, 1.8 bands
        ("P3", 130.0, 127.0, "INERT FAIL", "D2-INERT-ROW"),     # both fail, 0.3 bands
        ("N1", 105.0, 140.0, "DISCRIMINATES", None),            # pass / fail
        ("N2", 140.0, 105.0, "DISCRIMINATES", None),            # fail / pass
        ("N3", 130.0, 170.0, "BOTH FAIL, SEPARATED", None),     # both fail, 4 bands
        ("N4", 103.0, None, "UNMEASURED", None),                # null never ran
        # A guard smuggled into the graded tally is BOTH a D3 and, because it
        # is then a graded row that does not discriminate, a D1.
        ("S1", 101.0, 99.0, "HOLLOW PASS", "D1-HOLLOW-PASS"),
    ]
    for row, tv, nv, _cls, _rule in plant:
        ref[row] = {"quantity": f"q_{row}", "reference": 100.0, "band": 10.0,
                    "kind": "REL", "unit": "%"}
        treat[f"q_{row}"] = tv
        null[f"q_{row}"] = nv
    # The guard declared on row S1's own quantity is the D3 smuggling shape.
    # The live negative control shape: a GUARD row that displays the exact
    # hollow-pass signature and must survive because it grades nothing.
    guard_vals["q_GUARD"] = (101.0, 99.0)
    treat["q_GUARD"], null["q_GUARD"] = guard_vals["q_GUARD"]
    doc = {"reference_parsed_from_spec": ref,
           "cases": {"TREAT": {"measure": treat}, "NULL": {"measure": null},
                     "UNGRADED": {"measure": dict(treat)}}}
    return doc, plant


SELFTEST_REGISTRY = [
    {
        "rung": "SYNTH", "hypothesis": "planted", "gate_json": "-", "loader": "k0cs",
        "design": "TREATMENT_VS_NULL", "null_arm": "NULL",
        "null_registered_in": "planted",
        "arms": {"TREAT": {"model": "t", "mesh": "-", "graded": True},
                 "UNGRADED": {"model": "t", "mesh": "-", "graded": False}},
        "guards": [
            {"row": "H1", "quantity": "q_GUARD", "reference": 100.0, "band": 10.0,
             "kind": "REL", "why": "planted negative control"},
            {"row": "H2", "quantity": "q_S1", "reference": 100.0, "band": 10.0,
             "kind": "REL", "why": "planted D3 control"},
        ],
    },
    {
        "rung": "SYNTH-NONULL", "hypothesis": "planted", "gate_json": "-",
        "loader": "k0cs", "design": "TREATMENT_VS_NULL", "null_arm": None,
        "null_registered_in": "planted: no null arm exists",
        "arms": {"TREAT": {"model": "t", "mesh": "-", "graded": True}},
        "guards": [],
    },
    {
        "rung": "SYNTH-AB", "hypothesis": "planted", "gate_json": "-", "loader": None,
        "design": "AB", "null_arm": None, "null_registered_in": "planted A/B",
        "arms": {}, "guards": [],
    },
]


def selftest(root: Path) -> int:
    doc, plant = _synthetic()
    findings, report = evaluate(
        root, registry=SELFTEST_REGISTRY,
        docs={"SYNTH": doc, "SYNTH-NONULL": doc})

    ok = True
    # Counted, never asserted by hand: one expectation per planted row, plus the
    # D3 smuggle, plus the five structural negatives asserted after the loop.
    positives = sum(1 for *_x, rule in plant if rule) + 1
    negatives = sum(1 for *_x, rule in plant if not rule) + 5
    print(f"planted {len(plant) + 1} row shapes into a synthetic gate document "
          f"({positives} must fire, {negatives} must survive); "
          f"the check returned {len(findings)} violations")
    if not findings:
        print("FAIL: the check found nothing at all, which means it did not run")
        return 1

    synth = [e for e in report if e["rung"] == "SYNTH"][0]
    cells = {(c["arm"], c["row"]): c for c in synth["cells"]}
    fired = {(f.arm, f.row): f.rule for f in findings}

    for row, _tv, _nv, want_cls, want_rule in plant:
        c = cells.get(("TREAT", row))
        got_cls = c["class"] if c else "MISSING"
        got_rule = fired.get(("TREAT", row))
        cls_ok = got_cls == want_cls
        rule_ok = got_rule == want_rule
        if cls_ok and rule_ok:
            what = f"caught   {want_rule}" if want_rule else "ignored  (negative)"
            print(f"  {what:<28} {row}  class {got_cls}")
        else:
            print(f"  MISBEHAVED {row}: class {got_cls} (wanted {want_cls}), "
                  f"rule {got_rule} (wanted {want_rule})")
            ok = False

    # The guard row must display the hollow-pass signature and must NOT fire.
    g = cells.get(("TREAT", "H1"))
    if g and g["class"] == "HOLLOW PASS" and ("TREAT", "H1") not in fired:
        print(f"  ignored  (negative)          H1  class HOLLOW PASS, role GUARD, "
              f"sep {g['sep_bands']:.3f} bands -- a guard that legitimately does not "
              f"discriminate survived")
    else:
        print(f"  MISBEHAVED H1: a declared GUARD showing the hollow-pass signature "
              f"was not handled as a surviving negative "
              f"(class {g['class'] if g else 'MISSING'}, fired {('TREAT','H1') in fired})")
        ok = False

    # D3: a guard whose quantity is also in the graded tally.
    if any(f.rule == "D3-GUARD-GRADED" for f in findings):
        print("  caught   D3-GUARD-GRADED       H2  guard quantity found in the graded tally")
    else:
        print("  MISBEHAVED H2: the smuggled guard was not caught by D3-GUARD-GRADED")
        ok = False

    # A row on an UNGRADED arm must be measured and must never be a violation.
    ung = cells.get(("UNGRADED", "P1"))
    if ung and ung["class"] == "HOLLOW PASS" and ("UNGRADED", "P1") not in fired:
        print("  ignored  (negative)          P1  same shape on an UNGRADED arm survived")
    else:
        print("  MISBEHAVED: a hollow shape on an UNGRADED arm was treated as a violation")
        ok = False

    # UNMEASURED must be counted as unmeasured and never as clean.
    n4 = cells.get(("TREAT", "N4"))
    if n4 and n4["class"] == "UNMEASURED" and ("TREAT", "N4") not in fired:
        print("  ignored  (negative)          N4  a row whose null never ran read "
              "UNMEASURED, not clean")
    else:
        print("  MISBEHAVED N4: a row with no null value was not reported as UNMEASURED")
        ok = False

    nonull = [e for e in report if e["rung"] == "SYNTH-NONULL"][0]
    if nonull["skipped"] and "no null arm" in nonull["skipped"]:
        print(f"  ignored  (negative)          SYNTH-NONULL  reported NOT MEASURED "
              f"({nonull.get('unmeasured_rows')} cells), not PASS")
    else:
        print("  MISBEHAVED: a rung with no null arm was not reported as NOT MEASURED")
        ok = False

    ab = [e for e in report if e["rung"] == "SYNTH-AB"][0]
    if ab["skipped"] and "A/B" in ab["skipped"]:
        print("  ignored  (negative)          SYNTH-AB  an A/B-by-construction rung "
              "was excluded with its reason stated")
    else:
        print("  MISBEHAVED: an A/B rung was not excluded")
        ok = False

    print()
    print(f"control: {positives} planted violations and {negatives} shapes that "
          f"must survive, over a population of {len(synth['cells'])} synthetic cells; "
          f"{'every one behaved' if ok else 'SOME DID NOT BEHAVE'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--selftest", action="store_true",
                    help="plant every shape, positive and negative, and assert each behaves")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="print every (row x arm) cell with its class and separation")
    ap.add_argument("--json", action="store_true", help="emit the full report as JSON")
    args = ap.parse_args()

    root = Path(args.root)
    if args.selftest:
        return selftest(root)

    findings, report = evaluate(root)
    if args.json:
        print(json.dumps({"report": report,
                          "findings": [{"rule": f.rule, "rung": f.rung, "arm": f.arm,
                                        "row": f.row, "why": f.why} for f in findings]},
                         indent=1))
        return 1 if findings else 0
    return print_report(report, findings, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
