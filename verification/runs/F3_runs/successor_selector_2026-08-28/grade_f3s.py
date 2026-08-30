#!/usr/bin/env python3
"""
F3 SUCCESSOR (grid triples) -- THE GRADING PATH. It calls `grade_ladder`.

WHAT CHANGED AND WHY, stated first because the previous design failed here
---------------------------------------------------------------------------
The band-only predecessor routed grading to F3's frozen `grade_f3.py` as a
subprocess. cfd-supervisor refused the freeze on it, and correctly: `grade_f3.py`
REIMPLEMENTS the Roache triple at :377-395 and supplies NO iterative or plateau
states, so rule 5 limb (1) is never asked. Running full triples through it would
have produced `ABSENT` rows -- the exact defect ruled on at `887ddfaf` -- and the
extra core-minutes would have bought a triple that nothing gates.

    THE BANDS ARE INHERITED. THE VERDICT RULE IS NOT.

Reading a frozen band out of F3's registration is not re-deriving it. Invoking
F3's comparator to obtain a verdict IS inheriting the thing that bypasses rule 5.
So every band and every exact reference below is taken from the frozen sources
and CROSS-CHECKED against them at run time, while the gate itself is
`scripts/roache_triple.py::grade_ladder` and nothing else.

`grade_successor.py` is RETIRED from the graded path. Its `:336` guard refuses
any row carrying a triple -- correct for a band-only rung, fatal for this one --
and inverting that test would only keep a band-only instrument inside a
triple-scoped rung.

REFUSAL DISCIPLINE
------------------
`raise` / `sys.exit(2)` only. Zero `assert` statements (L-332), re-checked by AST
as a launch precondition. And because `grade_ladder` reaches its own gate through
FOUR asserts -- `roache_triple.py:195, 632, 634, 637`, carrying rule 1's verdict
vocabulary and rule 5's one-way asymmetry -- which `python3 -O` deletes, THIS
FILE REFUSES TO RUN UNDER `-O` AT ALL, at entry, before anything else executes.
That converts a prose commitment into a flag-proof refusal at the boundary this
rung owns, without editing a shared instrument that is not this rung's to edit.
"""
import sys

# ---------------------------------------------------------------------------
# THE -O REFUSAL. FIRST STATEMENT AFTER THE STDLIB IMPORT, BEFORE ANY OTHER
# IMPORT RUNS. `python3 -O` sets __debug__ False and deletes every `assert`,
# including the four in roache_triple.py that enforce rule 1 and rule 5's
# asymmetry. A registration that merely SAYS "never run under -O" is prose;
# this is the guard.
# ---------------------------------------------------------------------------
if not __debug__:
    sys.stderr.write(
        "REFUSED: this grading path must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including roache_triple.py:195,632,634,637,\n"
        "  which carry require_dim and the _seal invariants: the verdict must be in\n"
        "  the fixed vocabulary, the verdict must be one-way against the band\n"
        "  verdict, and NO GCI may be quoted on a non-monotone triple. With those\n"
        "  deleted, rule 1 and rule 5 are not enforced by anything.\n")
    sys.exit(2)

import os
import re
import ast
import json
import math
import shutil
import hashlib
import tempfile
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
F3_ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(F3_ROOT)))
CONV = os.path.join(F3_ROOT, "conversion_2026-08-24")
FROZEN_PREREG = os.path.join(REPO, "verification", "campaign",
                             "F3_CONVERSION_PREREGISTRATION.md")

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, F3_ROOT)
sys.path.insert(0, CONV)

import roache_triple as RT           # THE GATE. Rule 5 lives here and nowhere else.
import instrument as INS             # iterative_state_from_log, plateau_state


DIM = 2          # single-cell-thick 2-D blockMesh slabs; printed beside every order
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# THE UNIQUE SELECTOR -- docs/standards/UNIQUE_SELECTOR_RULE.md sec.6, frozen at
# ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6.  Clause U (cardinality) and clause P
# (leading field token) are BOTH present; sec.4 of that spec argues at length why
# neither substitutes for the other.  Refusal is unconditional: no --force, no
# environment override, no "degrade to the first match with a warning".
# ---------------------------------------------------------------------------

def select_one(d, want_field, ext=".raw"):
    """Select the single artifact for `want_field` in `d`, or REFUSE (exit 2)."""
    names = sorted(os.listdir(d))
    cands = [f for f in names if f.endswith(ext)
             and f.split("_", 1)[0] == want_field]
    if len(cands) != 1:
        shown, trunc = names, ""
        if len(names) > 20:
            shown = names[:20]
            trunc = " ...TRUNCATED, first 20 of %d shown" % len(names)
        refuse(
            "UNIQUE-SELECTOR: expected exactly 1 artifact for field %r in\n"
            "  %s\n"
            "  predicate : basename.endswith(%r) and basename.split('_',1)[0] == %r\n"
            "  matched   : %d -> %s\n"
            "  directory : %d entries -> %s%s\n"
            "A reader that cannot say how many things it matched cannot say it\n"
            "matched the right one. Not degraded, not defaulted: refused."
            % (want_field, os.path.abspath(d), ext, want_field,
               len(cands), cands, len(names), shown, trunc))
    return os.path.join(d, cands[0])



# ---------------------------------------------------------------------------
# BANDS AND REFERENCES -- INHERITED, CITED BY LINE, AND CROSS-CHECKED
# ---------------------------------------------------------------------------
# Each band is quoted with the line of the frozen registration that fixes it, so
# a reader can confirm no measured deviation entered. NOTHING HERE IS DERIVED.
REGISTERED_BANDS_PCT = {
    "p_wall_mean": (0.5, "F3_CONVERSION_PREREGISTRATION.md:150,158 -- reference "
                         "class + second-order requirement; exact analytic "
                         "reference contributes zero uncertainty"),
    "beta_deg":    (2.0, "F3_CONVERSION_PREREGISTRATION.md:162,179 -- rounded-up "
                         "2-sigma detector quantization floor from MESH GEOMETRY "
                         "ONLY (wedge M2.5 th10: H=0.9940, dy=H/80, 2sigma=1.937%)"),
    "cd":          (1.0, "F3_CONVERSION_PREREGISTRATION.md:190,196 -- 2 x the "
                         "surface-pressure band, one band per panel"),
}
# Exact analytic references, frozen at full double precision.
REGISTERED_EXACT = {
    ("wedge", "M2.5_th10", "p_wall_mean"):
        (1.8638705181801498, "F3_CONVERSION_PREREGISTRATION.md:108"),
    ("wedge", "M2.5_th10", "beta_deg"):
        (31.85059223127216,  "F3_CONVERSION_PREREGISTRATION.md:108"),
    ("diamond", "M2.5_eps5", "cd"):
        (0.01343027834624868, "F3_CONVERSION_PREREGISTRATION.md:111"),
}
# The keys those pairs carry in grade_f3.py's frozen EXACT table.
EXACT_KEY = {("wedge", "M2.5_th10"): "wedge_M2.5_th10.0",
             ("diamond", "M2.5_eps5"): "diamond_M2.5_eps5.0"}
EXACT_FIELD = {"p_wall_mean": "p2_p1", "beta_deg": "beta_deg", "cd": "cd"}

FROZEN_SHA256 = {
    "conversion_2026-08-24/grade_f3.py":
        "e7602996cb75fd61e95a51a85910b24cf0a675b6eee05e8b7c3d2e5ae0b88570",
    "exact_theory.py":
        "1e1879a3034c4eaabf092a4a05bd76ef01f216473e366c32cd4f7b0ecc4ca8d6",
    "make_wedge_case.py":
        "5741fd6229157287291edc94a36b9fa072bf98126ce57e857ddba3f19d891e3a",
    "make_diamond_case.py":
        "c2a5a70dd7d9f1d981cc98c4c02a76768c43956c7317abb57a7727bd46a5ad68",
}

# The run matrix, frozen. COARSE FIRST -- grade_ladder requires that order.
LEVELS = ("coarse", "medium", "fine")
CELLS = {("wedge", "coarse"): 1800, ("wedge", "medium"): 7200, ("wedge", "fine"): 28800,
         ("diamond", "coarse"): 2000, ("diamond", "medium"): 8000, ("diamond", "fine"): 32000}
GATE_ROWS = (
    ("G-F3S-1_wedge_surface_pressure", "wedge",   "M2.5_th10", "p_wall_mean"),
    ("G-F3S-2_wedge_shock_angle",      "wedge",   "M2.5_th10", "beta_deg"),
    ("G-F3S-5_diamond_wave_drag",      "diamond", "M2.5_eps5", "cd"),
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_frozen_bytes():
    seen = {}
    for rel, want in sorted(FROZEN_SHA256.items()):
        p = os.path.join(F3_ROOT, rel)
        if not os.path.exists(p):
            refuse("frozen artifact missing: %s" % p)
        got = sha256_file(p)
        if got != want:
            refuse("frozen artifact CHANGED: %s\n  expected %s\n  on disk  %s"
                   % (rel, want, got))
        seen[rel] = got
    return seen


def crosscheck_inherited_values():
    """The bands and references above are QUOTED from the frozen registration.
    Here they are checked against the frozen COMPARATOR's own constants, which
    are a second, independent copy. A mismatch means the two frozen sources
    disagree and nothing may be graded until a human resolves it.

    grade_f3 is IMPORTED for its constants only. `apply_gate` is never called --
    that is the verdict rule this path exists to replace.
    """
    import grade_f3 as G
    checks = []
    pairs = (("p_wall_mean", G.BAND_SURFACE_PRESSURE_PCT),
             ("beta_deg", G.BAND_SHOCK_ANGLE_PCT),
             ("cd", G.BAND_WAVE_DRAG_PCT))
    for q, frozen_val in pairs:
        mine = REGISTERED_BANDS_PCT[q][0]
        if mine != frozen_val:
            refuse("band for %s disagrees between the two frozen sources: this "
                   "registration says %r (%s); grade_f3.py says %r"
                   % (q, mine, REGISTERED_BANDS_PCT[q][1], frozen_val))
        checks.append(dict(kind="band", quantity=q, value=mine,
                           cited=REGISTERED_BANDS_PCT[q][1], agrees=True))
    for (fam, pair, q), (mine, cite) in sorted(REGISTERED_EXACT.items()):
        frozen_val = G.EXACT[EXACT_KEY[(fam, pair)]][EXACT_FIELD[q]]
        if mine != frozen_val:
            refuse("exact reference for %s/%s/%s disagrees: this registration "
                   "says %.17g (%s); grade_f3.py says %.17g"
                   % (fam, pair, q, mine, cite, frozen_val))
        checks.append(dict(kind="reference", family=fam, pair=pair, quantity=q,
                           value=mine, cited=cite, agrees=True))
    return checks


def crosscheck_control():
    """PLANTED CONTROL on the cross-check itself (standing rule 3).

    A cross-check that returns "agrees" for everything would certify a band that
    had drifted. Perturb one registered value in a COPY of the table and require
    the cross-check to refuse. Run in a subprocess so the real table is never
    touched by the control.
    """
    import subprocess
    probe = (
        "import sys; sys.path.insert(0, %r)\n"
        "import grade_f3s as g\n"
        "g.REGISTERED_BANDS_PCT['cd'] = (99.0, 'PLANTED -- not the frozen band')\n"
        "try:\n"
        "    g.crosscheck_inherited_values()\n"
        "    print('CONTROL_FAILED_NO_REFUSAL')\n"
        "except SystemExit as e:\n"
        "    print('REFUSED_AS_REQUIRED' if e.code == 2 else 'WRONG_CODE')\n"
    ) % HERE
    p = subprocess.run([sys.executable, "-c", probe],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode().strip()
    if "REFUSED_AS_REQUIRED" not in out:
        refuse("CROSS-CHECK CONTROL FAILED: a band planted at 99.0 did not make "
               "crosscheck_inherited_values() refuse (got %r). The cross-check "
               "has not been shown able to see a disagreement, so its agreement "
               "is NOT EVIDENCE." % out)
    return dict(control="PZ-XCHECK_band_disagreement_is_seen",
                planted_band=99.0, refused=True, passed=True)


# ---------------------------------------------------------------------------
# Readers -- one per graded quantity, each with a REAL plant into a REAL artifact
# ---------------------------------------------------------------------------

def read_p_wall_mean(case_dir):
    """The graded surface pressure, from the raw patch sample."""
    d = latest_numeric(os.path.join(case_dir, "postProcessing", "surfaceSampleDict"))
    if d is None:
        return None, None
    # UNIQUE-SELECTOR REPAIR of site grade_f3s.py:239 in
    # successor_triple_2026-08-26 (post-first-compute; NOT edited there -- this is
    # the successor, UNIQUE_SELECTOR_RULE.md sec.8.2).  The substring predicate
    # ("p" in f) and the bare cands[0] are gone, and the
    # `if not cands: return None, None` early return is DELETED per sec.5.1:
    # absence is a REFUSAL, not a None the caller may interpret.
    path = select_one(d, "p")
    return p_wall_mean_from_raw(path, case_dir), path


def p_wall_mean_from_raw(path, case_dir):
    meta = json.load(open(os.path.join(case_dir, "meta.json")))
    arr = np.loadtxt(path, comments="#")
    x_wall, p_wall = arr[:, 0], arr[:, 3]
    order = np.argsort(x_wall)
    x_wall, p_wall = x_wall[order], p_wall[order]
    mid = (x_wall > 0.3 * meta["Lramp"]) & (x_wall < 0.85 * meta["Lramp"])
    return float(np.mean(p_wall[mid]))


def read_cd(case_dir):
    d = latest_numeric(os.path.join(case_dir, "postProcessing", "forces1"))
    if d is None:
        return None, None
    path = os.path.join(d, "force.dat")
    if not os.path.exists(path):
        return None, None
    return cd_from_force(path, case_dir), path


def cd_from_force(path, case_dir):
    meta = json.load(open(os.path.join(case_dir, "meta.json")))
    rows = [l for l in open(path) if not l.startswith("#") and l.strip()]
    fx = float(rows[-1].split()[1])
    q1 = 0.5 * 1.4 * 1.0 * meta["M"] ** 2
    return 2.0 * (fx / 0.01) / (q1 * meta["c"])


def latest_numeric(root):
    """Numeric-sorted latest. NOT `sorted(glob(...))[-1]`, which is
    LEXICOGRAPHIC and picks '9.0' over '10.0' the moment there is more than one
    sampled time -- which this rung creates. See instrument.py::numeric_time_dirs."""
    if not os.path.isdir(root):
        return None
    subs = []
    for d in os.listdir(root):
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d):
            subs.append((float(d), os.path.join(root, d)))
    if not subs:
        return None
    subs.sort(key=lambda t: t[0])
    return subs[-1][1]


def plant_column_delta(quantity, case_dir):
    """THE PLANT IS STATED IN THE GRADED QUANTITY'S UNITS, and this converts it
    into the artifact-column increment that produces exactly that much movement.

    This matters and the first draft got it wrong. Planting `PLANT` straight into
    `force.dat`'s Fx column moves `cd` by `2*PLANT/(z*q1*c)`, not by `PLANT` --
    so the control refused a reader that was in fact working. Inverting the
    definition instead makes the control STRICTER: the reader must reproduce a
    movement of exactly `PLANT` in the units the gate grades, to 1e-12.
    """
    if quantity == "p_wall_mean":
        return RT.PLANT                      # a uniform shift moves the mean 1:1
    if quantity == "cd":
        meta = json.load(open(os.path.join(case_dir, "meta.json")))
        q1 = 0.5 * 1.4 * 1.0 * meta["M"] ** 2
        return RT.PLANT * q1 * meta["c"] * 0.01 / 2.0
    refuse("no plant conversion registered for %r" % quantity)


def plant_control_for(quantity, artifact, case_dir, column):
    """Plant into the REAL artifact with the REAL parser, and hand the two values
    to grade_ladder's external_plant_control. A zero from a reader not shown able
    to see a non-zero is not evidence (rule 3)."""
    reader = {"p_wall_mean": p_wall_mean_from_raw, "cd": cd_from_force}[quantity]
    delta = plant_column_delta(quantity, case_dir)
    before = reader(artifact, case_dir)
    tmpd = tempfile.mkdtemp(prefix="f3s_plant_")
    try:
        work = os.path.join(tmpd, os.path.basename(artifact))
        lines = open(artifact).read().rstrip("\n").split("\n")
        out, planted = [], False
        for ln in lines:
            if ln.startswith("#") or not ln.strip():
                out.append(ln)
                continue
            parts = ln.split()
            parts[column] = repr(float(parts[column]) + delta)
            out.append(" ".join(parts))
            planted = True
        if not planted:
            refuse("%s: nothing to plant into %s -- the artifact has no data rows"
                   % (quantity, artifact))
        open(work, "w").write("\n".join(out) + "\n")
        after = reader(work, case_dir)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    pc = RT.external_plant_control(reader.__name__, before, after,
                                   artifact=artifact, level=os.path.basename(case_dir))
    if not pc.get("passed"):
        refuse("PLANTED-ZERO CONTROL FAILED for %s on %s: a column increment of "
               "%.6e was planted, which the definition says must move %s by "
               "exactly %.6e; the reader moved it %.6e. The reader has not been "
               "shown able to see a plant, so its values are NOT EVIDENCE."
               % (quantity, artifact, delta, quantity, RT.PLANT,
                  pc.get("reader_delta")))
    return pc


def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read()))
                 if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path and `python3 -O` "
               "deletes every one (L-332): %s" % json.dumps(bad))
    return dict(files_checked=len(paths), assert_nodes=0)


# ---------------------------------------------------------------------------
# THE GRADE -- and rule 5 is reached ONLY through grade_ladder
# ---------------------------------------------------------------------------

QUANTITY_ARTIFACT = {"p_wall_mean": (read_p_wall_mean, 3),
                     "cd": (read_cd, 1)}


def load_level(root, family, pair, level, quantity):
    """One mesh level: the graded value, its iterative state and its plateau
    state. Any of the three missing is a refusal or a PENDING, never a default."""
    case_dir = os.path.join(root, family, pair, level)
    if not os.path.isdir(case_dir):
        return None
    res_path = os.path.join(case_dir, "result.json")
    if not os.path.exists(res_path):
        return None
    res = json.load(open(res_path))

    if quantity == "beta_deg":
        value = res.get("beta_computed_deg")
        artifact = res_path
    else:
        reader, _col = QUANTITY_ARTIFACT[quantity]
        value, artifact = reader(case_dir)
    if value is None:
        refuse("%s/%s/%s: %s is absent from the case's own artifacts. An absent "
               "measurement is reported as absent, never graded as a pass."
               % (family, pair, level, quantity))

    it_state, it_detail = INS.iterative_state_from_log(
        os.path.join(case_dir, "log.rhoCentralFoam"))

    series_path = os.path.join(case_dir, "series_%s.json" % quantity)
    if not os.path.exists(series_path):
        refuse("%s/%s/%s: no plateau series for %s at %s. The Class C gate "
               "cannot be evaluated and an UNEVALUATED step is not a passed one."
               % (family, pair, level, quantity, series_path))
    ser = json.load(open(series_path))
    end_time = float(res.get("endTime", ser["end_time"]))
    pl_control = INS.plateau_plant_control(ser["t"], ser["v"], quantity, end_time)
    pl_state, pl_detail = INS.plateau_state(ser["t"], ser["v"], quantity, end_time)

    return dict(name=level, cells=CELLS[(family, level)], value=float(value),
                case_dir=case_dir, artifact=artifact,
                iterative=it_state, iterative_detail=it_detail,
                plateau=pl_state, plateau_detail=pl_detail,
                plateau_control=pl_control)


def grade_one(root, gid, family, pair, quantity):
    levels = []
    for lv in LEVELS:                      # COARSE FIRST, as grade_ladder requires
        got = load_level(root, family, pair, lv, quantity)
        if got is None:
            return dict(gate=gid, verdict="PENDING",
                        note="level %r absent from this rung's run root" % lv)
        levels.append(got)

    exact, cite = REGISTERED_EXACT[(family, pair, quantity)]
    band_pct, band_cite = REGISTERED_BANDS_PCT[quantity]
    band = (exact * (1.0 - band_pct / 100.0), exact * (1.0 + band_pct / 100.0))

    if quantity == "beta_deg":
        # No raw column to plant into: the value is the output of the frozen
        # 5-station fit. Plant into the FIT INPUT and require the fitted beta to
        # move -- the same discipline, applied one level up.
        pc = beta_plant_control(levels[-1])
    else:
        _reader, col = QUANTITY_ARTIFACT[quantity]
        pc = plant_control_for(quantity, levels[-1]["artifact"],
                               levels[-1]["case_dir"], col)

    row = RT.grade_ladder(
        quantity="%s / %s %s" % (gid, family, pair),
        levels=[dict(name=l["name"], cells=l["cells"], value=l["value"])
                for l in levels],
        dim=DIM, band=band, plant_control=pc,
        iterative_states={l["name"]: l["iterative"] for l in levels},
        plateau_states={l["name"]: l["plateau"] for l in levels},
        reference=exact)

    row["gate"] = gid
    row["family"], row["pair"] = family, pair
    row["band_pct"] = band_pct
    row["band_citation"] = band_cite
    row["reference_citation"] = cite
    row["deviation_pct"] = 100.0 * (levels[-1]["value"] - exact) / exact
    row["levels_detail"] = [
        dict(name=l["name"], cells=l["cells"], value=l["value"],
             iterative=l["iterative"], iterative_basis=l["iterative_detail"]["basis"],
             plateau=l["plateau"], plateau_detail=l["plateau_detail"],
             plateau_control=l["plateau_control"]) for l in levels]
    row["gated_by"] = ("scripts/roache_triple.py::grade_ladder -- rule 5 is "
                       "reached through this call and through nothing else")
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r"
               % (gid, row["verdict"]))
    return row


def beta_plant_control(level):
    """Plant a KNOWN slope increment into the stored shock locus and require the
    refitted beta to move by exactly what the definition demands."""
    res = json.load(open(os.path.join(level["case_dir"], "result.json")))
    pts = np.asarray(res["shock_pts"], dtype=float)
    if pts.shape[0] < 4:
        refuse("beta plant control: only %d shock stations stored; the frozen "
               "fit needs at least 4" % pts.shape[0])

    def fit(p):
        xk, yk = p[1:, 0], p[1:, 1]          # station 0 dropped, as frozen
        A = np.vstack([xk, np.ones_like(xk)]).T
        m = np.linalg.lstsq(A, yk, rcond=None)[0][0]
        return math.degrees(math.atan(m))

    before = fit(pts)
    slope0 = math.tan(math.radians(before))
    bumped = pts.copy()
    bumped[:, 1] = bumped[:, 1] + RT.PLANT * bumped[:, 0] / max(pts[:, 0].max(), 1e-300)
    after = fit(bumped)
    expect = math.degrees(math.atan(slope0 + RT.PLANT / max(pts[:, 0].max(), 1e-300)))
    if abs(after - expect) > 1e-9:
        refuse("BETA PLANT CONTROL FAILED: planted a slope increment; the fit "
               "moved beta to %.12f where the definition demands %.12f. The "
               "detector has not been shown able to see a plant."
               % (after, expect))
    return RT.external_plant_control("beta_5station_lstsq", before, after,
                                     plant=(after - before),
                                     artifact=os.path.join(level["case_dir"], "result.json"),
                                     level=level["name"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg-commit", help="sha of this rung's freeze commit")
    ap.add_argument("--root", default=os.path.join(HERE, "runs"))
    ap.add_argument("--out", default=os.path.join(HERE, "F3S_GRADED.json"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    frozen = assert_frozen_bytes()
    xchecks = crosscheck_inherited_values()
    xcontrol = crosscheck_control()
    astcheck = ast_no_asserts([os.path.join(HERE, "grade_f3s.py"),
                               os.path.join(HERE, "instrument.py")])

    if a.selftest:
        ok, why = selftest_predicate(frozen, xchecks, xcontrol, astcheck)
        print(json.dumps(dict(frozen_bytes_asserted=frozen,
                              inherited_value_crosschecks=xchecks,
                              crosscheck_control=xcontrol,
                              assert_census=astcheck,
                              debug_flag=__debug__,
                              predicate=dict(ok=ok, why=why)), indent=2))
        # THE CLAIM IS INSIDE THE PASSING BRANCH. Removing the check removes it.
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade")

    rows = [grade_one(a.root, gid, fam, pair, q) for gid, fam, pair, q in GATE_ROWS]
    report = dict(
        rung="F3-SUCCESSOR-TRIPLE",
        prereg="verification/campaign/F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md",
        prereg_commit=a.prereg_commit,
        frozen_bytes_asserted=frozen,
        inherited_value_crosschecks=xchecks,
        crosscheck_control=xcontrol,
        assert_census=astcheck,
        gate_is=("scripts/roache_triple.py::grade_ladder, supplied with "
                 "iterative_states AND plateau_states. grade_f3.py::apply_gate "
                 "is NOT called: it reimplements the triple at :377-395 and "
                 "supplies no states, which is the ABSENT defect ruled on at "
                 "887ddfaf."),
        does_not_alter_F3=("F3 is CLOSED at 5 PASS, 1 GATE FAIL, 1 NOT A RESULT, "
                           "3 PENDING. This rung produces its own rows under its "
                           "own registration and changes none of F3's."),
        rows=rows)
    with open(a.out, "w") as f:
        json.dump(report, f, indent=2)

    print("F3 SUCCESSOR (grid triples) -- TALLY")
    print("=" * 78)
    for r in rows:
        print("%-44s %s" % (r["gate"], r["verdict"]))
        if "why" in r:
            print("    %s" % r["why"])
    print("=" * 78)
    print("gated by: grade_ladder. F3 is NOT altered by this rung.")
    print("written: %s" % a.out)
    return 0


def selftest_predicate(frozen, xchecks, xcontrol, astcheck):
    """The success PREDICATE, separate from any print."""
    if len(frozen) != len(FROZEN_SHA256):
        return False, "expected %d frozen artifacts, got %d" % (len(FROZEN_SHA256), len(frozen))
    n_expected = len(REGISTERED_BANDS_PCT) + len(REGISTERED_EXACT)
    if len(xchecks) != n_expected or not all(c.get("agrees") for c in xchecks):
        return False, ("expected %d inherited-value crosschecks all agreeing, got %d"
                       % (n_expected, len(xchecks)))
    if not xcontrol.get("passed"):
        return False, "the cross-check control did not pass"
    if astcheck.get("assert_nodes") != 0:
        return False, "assert nodes present in this rung's path"
    if not __debug__:
        return False, "running under -O, which deletes roache_triple's four gate asserts"
    return True, ("%d frozen artifacts byte-asserted; %d inherited values agree with "
                  "the frozen comparator; cross-check control saw a planted "
                  "disagreement; 0 assert nodes; __debug__ True"
                  % (len(frozen), len(xchecks)))




def _selector_selftest():
    """C1-C6 of UNIQUE_SELECTOR_RULE.md sec.7, driven through THIS module's own
    select_one -- never a re-implementation.  Refuses (exit 2) if any control fails,
    and refuses under -O because a control that vanishes is not a control."""
    import selector_controls
    return selector_controls.run_battery(sys.modules[__name__], sys.stderr)

if __name__ == "__main__":
    if "--selector-selftest" in sys.argv:
        sys.exit(_selector_selftest())
    # `roache_triple.refuse()` RAISES `Refusal`; it does not exit. Without this
    # every gate refusal from the shared instrument would surface as an uncaught
    # traceback at rc=1, not the rc=2 that standing rule 4 requires of a
    # comparator ("refuse rather than degrade"). Found by neutering the
    # planted-zero control in a mutation run and watching rc come back 1.
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
