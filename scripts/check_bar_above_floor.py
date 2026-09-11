#!/usr/bin/env python3
"""check_bar_above_floor.py — the executable check shipping with L-530.

THE PROPOSITION UNDER TEST
--------------------------
A screen whose BAR sits below its own instrument's MEASURED FLOOR on the mesh it
is applied to is not strict, it is BLIND. It still renders a verdict — the reader
runs, returns a number, the number exceeds a registered threshold, and the
refusal is faithfully recorded — but the verdict is about the INSTRUMENT wearing
the costume of a verdict about the world.

The paid example is RC3's continuity screen. A GLOBAL bar of `1e-4` was applied
to three meshes. On `CBFS13700` the reader's own measured floor on the
UNCORRECTED baseline (correction field identically zero, so nothing can be
blamed on the correction) is **9.6193e-03** — the bar sat ~1000x TIGHTER than
the floor. 8 of 54 real rows were admissible and the case would have been retired
for a reader artifact, with the record reading as rigour.

L-530's rule, which this file makes executable:

    Before a bar is registered, MEASURE THE INSTRUMENT'S FLOOR ON EVERY MESH THE
    BAR WILL BE APPLIED TO, by reading the metric on a case where the signal is
    known to be ~zero. A bar tighter than that floor screens the instrument, not
    the physics. State the floor beside the bar in the registration, with the
    named artifact it was read from.

And the anti-exploit clause, because the repair must not become the exploit:
"widen the bar because the rows fail it" is gate-shopping; "set the bar from the
instrument's measured floor by a mechanical rule fixed before any run" is
calibration. The rule this file grades against is the registered one:

    bar(mesh) = max(BAR_MIN, smallest decade >= 10 x floor(mesh))

WHY ast-ONLY, AND NEVER AN IMPORT
---------------------------------
The module under test IS the instrument. Importing it would execute it, and an
instrument that must run to be screened cannot be screened before it runs — which
is the only moment at which a bar is still movable. This file therefore parses
the named module with `ast` and reads its module-level dict literals. It never
imports, never executes, and never writes to the module it reads.

The case-local precedent (`rc3_ceiling.continuity_bar`, `check_continuity_bars`)
checks its OWN module constants against its OWN rule and can screen no other
registration. This file screens ANY named module, and — via `--json` — any
registration that publishes its bar table as data rather than as constants, so
real registered numbers are READ rather than transcribed into a fixture.

REFUSAL DISCIPLINE
------------------
The refusal is carried by `sys.exit(2)`, NEVER by `assert` (L-332 / D476 31.3:
asserts vanish under `python3 -O`). This file is green under BOTH `python3` and
`python3 -O`, and its `--selftest` drives the refusal on the REAL REGISTERED
NUMBERS in both directions, then PLANTS a mutation in the one quantity the
detector claims to read and requires the verdict to move.

USAGE
-----
    check_bar_above_floor.py --module M.py --floor-dict FLOORS --bar-dict BARS
                             [--artifact-dict ARTS] [--bar-min-name NAME]
                             [--bar-min FLOAT] [--emit-json]
    check_bar_above_floor.py --module M.py --floor-dict FLOORS
                             --global-bar CONTINUITY_MAX [...]
    check_bar_above_floor.py --json TABLE.json
    check_bar_above_floor.py --selftest

EXIT CODES
----------
    0   no finding
    2   REFUSAL: a registered bar is not above its instrument's measured floor,
        or its provenance is missing
    3   usage / unreadable input / a named table absent from the module — a
        refusal too, because a check that could not be made is not a pass
"""

import argparse
import ast
import json
import math
import os
import subprocess
import sys
import tempfile

VERSION = "1.0"

# The registered rule's multiple: a bar must clear its measured floor by at
# least this factor before it is measuring the field rather than the reader.
FLOOR_MULTIPLE = 10.0

# A single bar shared by meshes whose floors differ by more than this many
# decades is not derivable from any one floor.
DEFAULT_SPREAD_DECADES = 1.0

# The real registration the selftest drives. Not a fixture: these are the
# numbers a committed closure registration carries.
REAL_MODULE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cases", "RANS_LES_closure_models", "RC3_wu_ceiling_gate_validation",
    "rc3_ceiling.py")
REAL_FLOOR_DICT = "CONTINUITY_FLOOR"
REAL_BAR_DICT = "CONTINUITY_BAR"
REAL_ARTIFACT_DICT = "CONTINUITY_FLOOR_ARTIFACT"
REAL_BAR_MIN_NAME = "CONTINUITY_MAX"


def refuse(msg):
    """The single refusal path. Never an assert (L-332)."""
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def unreadable(msg):
    """A check that could not be made is not a pass."""
    sys.stderr.write("REFUSED (check could not be made): %s\n" % msg)
    sys.exit(3)


# ---------------------------------------------------------------------------
# THE RULE
# ---------------------------------------------------------------------------

def smallest_decade_ge(x):
    """The smallest power of ten >= x, robust to log10 landing just under.

    A floor of exactly 1e-5 gives 10*floor = 1e-4, whose log10 can come back as
    -4.000000000000001; a bare ceil would then return 1e-3 and the rule would
    silently loosen by a decade.
    """
    if x <= 0.0:
        raise ValueError("smallest_decade_ge needs a positive number")
    e = int(math.ceil(round(math.log10(x), 12)))
    while 10.0 ** e < x:
        e += 1
    while 10.0 ** (e - 1) >= x:
        e -= 1
    return 10.0 ** e


def derived_bar(floor, bar_min):
    """bar = max(BAR_MIN, smallest decade >= 10 x floor). BAR_MIN may be None."""
    d = smallest_decade_ge(FLOOR_MULTIPLE * floor)
    if bar_min is None:
        return d
    return max(float(bar_min), d)


def _same_decade(a, b):
    return abs(math.log10(a) - math.log10(b)) <= 1e-9


# ---------------------------------------------------------------------------
# READING A REGISTRATION — ast over a module, or a published JSON table
# ---------------------------------------------------------------------------

def _module_toplevel_names(path):
    """Return {name: literal value} for every module-level literal assignment.

    Parsed with `ast` and evaluated with `ast.literal_eval`, so no code in the
    module under test is ever executed. Names whose value is not a literal are
    simply absent, which is reported rather than guessed at.
    """
    try:
        src = open(path, errors="replace").read()
    except OSError as exc:
        unreadable("cannot read module %s: %s" % (path, exc))
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as exc:
        unreadable("cannot parse module %s: %s" % (path, exc))
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, SyntaxError):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out[target.id] = value
    return out


def _artifact_path(value):
    """A floor's named artifact: a bare path, or the first slot of a tuple."""
    if isinstance(value, (tuple, list)) and value:
        value = value[0]
    return value if isinstance(value, str) else None


def table_from_module(path, floor_dict, bar_dict, artifact_dict,
                      global_bar_name, bar_min_name, bar_min):
    names = _module_toplevel_names(path)

    if floor_dict not in names:
        unreadable("module %s carries no module-level literal `%s`; the floor "
                   "table is what this check reads and it is not there"
                   % (path, floor_dict))
    floors = names[floor_dict]
    if not isinstance(floors, dict):
        unreadable("`%s` in %s is not a dict" % (floor_dict, path))

    arts = {}
    if artifact_dict:
        if artifact_dict not in names:
            unreadable("module %s carries no module-level literal `%s`"
                       % (path, artifact_dict))
        raw = names[artifact_dict]
        if not isinstance(raw, dict):
            unreadable("`%s` in %s is not a dict" % (artifact_dict, path))
        arts = {k: _artifact_path(v) for k, v in raw.items()}

    if bar_min is None and bar_min_name:
        if bar_min_name not in names:
            unreadable("module %s carries no module-level literal `%s`"
                       % (path, bar_min_name))
        try:
            bar_min = float(names[bar_min_name])
        except (TypeError, ValueError):
            unreadable("`%s` in %s is not a number" % (bar_min_name, path))

    if global_bar_name:
        if global_bar_name not in names:
            unreadable("module %s carries no module-level literal `%s`"
                       % (path, global_bar_name))
        try:
            g = float(names[global_bar_name])
        except (TypeError, ValueError):
            unreadable("`%s` in %s is not a number" % (global_bar_name, path))
        # A GLOBAL bar is, by construction, the same number on every mesh the
        # floor table names. This is how a retired global screen is read back.
        bars = {k: g for k in floors}
        bar_source = "%s (GLOBAL, one scalar over %d mesh(es))" % (
            global_bar_name, len(bars))
    else:
        if bar_dict not in names:
            unreadable("module %s carries no module-level literal `%s`"
                       % (path, bar_dict))
        bars = names[bar_dict]
        if not isinstance(bars, dict):
            unreadable("`%s` in %s is not a dict" % (bar_dict, path))
        bar_source = bar_dict

    meshes = {}
    for tag in sorted(set(list(floors) + list(bars))):
        meshes[tag] = dict(floor=floors.get(tag), bar=bars.get(tag),
                           artifact=arts.get(tag))
    return dict(source=path, bar_source=bar_source, bar_min=bar_min,
                meshes=meshes)


def table_from_json(path):
    try:
        obj = json.load(open(path, errors="replace"))
    except (OSError, ValueError) as exc:
        unreadable("cannot read bar table %s: %s" % (path, exc))
    if not isinstance(obj, dict):
        unreadable("bar table %s is not a JSON object" % path)

    if isinstance(obj.get("meshes"), dict):
        meshes_raw = obj["meshes"]
        bar_min = obj.get("bar_min")
        source = obj.get("source", path)
        bar_source = obj.get("bar_source", "json:meshes")
    else:
        # The loose form: a bare mapping of tag -> {floor, bar, artifact}.
        meshes_raw = {k: v for k, v in obj.items() if isinstance(v, dict)}
        if not meshes_raw:
            unreadable("bar table %s carries neither a `meshes` object nor a "
                       "mapping of mesh -> {floor, bar}; there is nothing to "
                       "screen, and nothing to screen is not a pass" % path)
        bar_min = obj.get("bar_min")
        source = path
        bar_source = "json:flat"

    meshes = {}
    for tag, row in meshes_raw.items():
        if not isinstance(row, dict):
            unreadable("bar table %s: entry %r is not an object" % (path, tag))
        meshes[tag] = dict(floor=row.get("floor"), bar=row.get("bar"),
                           artifact=_artifact_path(row.get("artifact")))
    return dict(source=source, bar_source=bar_source,
                bar_min=None if bar_min is None else float(bar_min),
                meshes=meshes)


# ---------------------------------------------------------------------------
# THE SCREEN
# ---------------------------------------------------------------------------

def evaluate(table, spread_decades=DEFAULT_SPREAD_DECADES, check_disk=True):
    """Return (findings, cannot_see). An empty findings list is a clean read."""
    findings = []
    cannot_see = []
    bar_min = table.get("bar_min")
    meshes = table["meshes"]

    def finding(code, tag, why, **kw):
        f = dict(code=code, tag=tag, why=why)
        f.update(kw)
        findings.append(f)

    for tag in sorted(meshes):
        row = meshes[tag]
        floor, bar = row.get("floor"), row.get("bar")

        if bar is None:
            cannot_see.append(
                "mesh %s carries a measured floor but no registered bar; "
                "nothing is screened on it here" % tag)
            continue

        bar = float(bar)

        if floor is None:
            finding("NO_FLOOR_MEASURED", tag,
                    "a bar is registered for this mesh but no instrument floor "
                    "was measured on it. L-530: the floor must be measured on "
                    "EVERY mesh the bar is applied to, before the bar is "
                    "registered. An unmeasured floor is not a floor of zero.",
                    bar=bar)
            continue

        floor = float(floor)
        if floor <= 0.0:
            finding("FLOOR_NOT_POSITIVE", tag,
                    "the measured instrument floor is %r; a floor read off a "
                    "baseline where the signal is known to be ~zero is small, "
                    "never zero or negative. A zero here is far more likely a "
                    "reader that saw nothing than an instrument with no noise."
                    % floor, bar=bar, floor=floor)
            continue

        need = FLOOR_MULTIPLE * floor
        if bar < need:
            finding("BAR_BELOW_FLOOR_RULE", tag,
                    "the registered bar is %.4g while the instrument's own "
                    "MEASURED floor on this mesh is %.4g. The bar is %.3gx the "
                    "floor, where the registered rule requires at least %gx. "
                    "A bar under its instrument's floor screens the reader, "
                    "not the physics, and every refusal it issues is an "
                    "instrument finding wearing the costume of a physics one. "
                    "The rule derives %.4g here."
                    % (bar, floor, bar / floor, FLOOR_MULTIPLE,
                       derived_bar(floor, bar_min)),
                    bar=bar, floor=floor, ratio=bar / floor,
                    derived=derived_bar(floor, bar_min))
        elif bar_min is not None:
            d = derived_bar(floor, bar_min)
            if not _same_decade(bar, d):
                finding("BAR_DRIFTED_FROM_RULE", tag,
                        "the registered bar is %.4g but the rule "
                        "max(%.4g, smallest decade >= %gx floor) derives %.4g "
                        "from the measured floor %.4g. A bar LOOSER than its "
                        "own derivation is chosen, not calibrated, and that is "
                        "the gate-shopping L-530 warns the repair must not "
                        "become."
                        % (bar, bar_min, FLOOR_MULTIPLE, d, floor),
                        bar=bar, floor=floor, derived=d)

        if bar_min is not None and bar < float(bar_min):
            finding("BAR_TIGHTER_THAN_REGISTERED_MINIMUM", tag,
                    "the bar is %.4g, tighter than the registration's own "
                    "minimum %.4g. The floor rule may only ever loosen."
                    % (bar, float(bar_min)), bar=bar, bar_min=float(bar_min))

        art = row.get("artifact")
        if art is None:
            finding("FLOOR_ARTIFACT_MISSING", tag,
                    "the floor %.4g is stated with no named artifact. L-530 "
                    "requires the floor to be stated beside the bar WITH the "
                    "named artifact it was read from; a floor with no artifact "
                    "is a number no successor can re-derive." % floor,
                    floor=floor)
        elif check_disk and not os.path.exists(art):
            finding("FLOOR_ARTIFACT_NOT_ON_DISK", tag,
                    "the floor's named artifact %s is not on disk. A number "
                    "whose artifact is gone is not a result." % art,
                    floor=floor, artifact=art)

    # --- the GLOBAL form: one scalar spread over meshes with unlike floors.
    if bar_min is None:
        cannot_see.append(
            "no registered BAR_MIN was supplied (--bar-min / --bar-min-name, "
            "or a `bar_min` key in the JSON), so the drift check and the "
            "global-bar check are SKIPPED, not passed. Without the minimum, a "
            "bar sitting far above its floor cannot be told apart from one "
            "the registration's own floor forces there.")
    else:
        groups = {}
        for tag in sorted(meshes):
            row = meshes[tag]
            if row.get("bar") is None or row.get("floor") is None:
                continue
            if float(row["floor"]) <= 0.0:
                continue
            groups.setdefault(float(row["bar"]), []).append(tag)
        for bar, tags in sorted(groups.items()):
            if len(tags) < 2:
                continue
            fl = [float(meshes[t]["floor"]) for t in tags]
            spread = math.log10(max(fl)) - math.log10(min(fl))
            if spread <= spread_decades:
                continue
            # A shared bar that the rule derives for EVERY member is forced by
            # the registration's own minimum, not chosen. That is the legitimate
            # case and it is exempt.
            if all(_same_decade(bar, derived_bar(float(meshes[t]["floor"]),
                                                 bar_min)) for t in tags):
                continue
            finding("GLOBAL_BAR_OVER_HETEROGENEOUS_FLOORS", ",".join(tags),
                    "one bar of %.4g is applied to %d meshes whose measured "
                    "floors span %.1f decades (%.4g .. %.4g), and the rule does "
                    "not derive that bar for all of them. A single scalar "
                    "cannot be above the floor on the blind mesh and still "
                    "screening anything on the sharp one: it is either blind "
                    "somewhere or toothless somewhere, and it takes the whole "
                    "item down with it."
                    % (bar, len(tags), spread, min(fl), max(fl)),
                    bar=bar, spread_decades=spread)

    return findings, cannot_see


CANNOT_SEE_STRUCTURAL = (
    "CANNOT SEE: (1) whether each stated floor is the TRUE reading of its named "
    "artifact — this check is ast-only and never runs the instrument, by "
    "design, because an instrument that must run to be screened cannot be "
    "screened while its bar is still movable; it screens the registration's "
    "arithmetic and its provenance, not its measurement. (2) Whether the bar "
    "can still FAIL a real row (L-530 clause 4) — that needs the population, "
    "and this reads only the table. (3) Whether the mesh list is COMPLETE: a "
    "mesh the bar will be applied to but which the floor table never names is "
    "invisible here, and is exactly how a global bar hides. (4) A bar living "
    "in prose, in a function body, or behind a computed expression rather than "
    "in the named module-level dicts — `ast.literal_eval` sees literals only, "
    "and a name it cannot evaluate is reported absent, never guessed."
)


def report(table, findings, cannot_see):
    print("check_bar_above_floor v%s" % VERSION)
    print("  registration source : %s" % table["source"])
    print("  bar table           : %s" % table.get("bar_source", "?"))
    print("  registered BAR_MIN  : %s"
          % ("(none supplied)" if table.get("bar_min") is None
             else "%.4g" % table["bar_min"]))
    print("  rule                : bar = max(BAR_MIN, smallest decade >= %gx "
          "measured floor)" % FLOOR_MULTIPLE)
    print("")
    print("  %-18s %14s %14s %12s  %s"
          % ("mesh", "measured floor", "registered bar", "bar/floor",
             "floor artifact"))
    for tag in sorted(table["meshes"]):
        row = table["meshes"][tag]
        fl, br = row.get("floor"), row.get("bar")
        ratio = ("%.3g" % (float(br) / float(fl))
                 if fl not in (None, 0) and br is not None else "-")
        art = row.get("artifact") or "(none named)"
        print("  %-18s %14s %14s %12s  %s"
              % (tag,
                 "-" if fl is None else "%.4e" % float(fl),
                 "-" if br is None else "%.4e" % float(br),
                 ratio, art))

    if not findings:
        print("\nVERDICT: no finding — every registered bar clears its own "
              "instrument's measured floor by the registered rule, and every "
              "floor names an artifact on disk.")
    else:
        print("\n%d FINDING(S):" % len(findings))
        for f in findings:
            print("  [%s] %s" % (f["code"], f["tag"]))
            print("      %s" % f["why"])

    for c in cannot_see:
        print("\nCANNOT SEE: %s" % c)
    print("\n" + CANNOT_SEE_STRUCTURAL)


# ---------------------------------------------------------------------------
# PLANTED-FAILURE SELFTEST, DRIVEN ON THE REAL REGISTERED NUMBERS
#
# The weak test shows the check passes on good input. What matters is whether
# the refusal FIRES on input known to be bad — and, harder, whether it STOPS
# firing when the one quantity it claims to read is moved. Every fixture below
# is driven through the real entry point as a subprocess. No fixture invents a
# number: the floors and bars come out of a real committed closure registration,
# and the two PLANT fixtures mutate exactly one of those real numbers.
# ---------------------------------------------------------------------------

def _run(argv):
    cmd = [sys.executable]
    if sys.flags.optimize:
        cmd += ["-O"] * sys.flags.optimize
    cmd += [os.path.abspath(__file__)] + argv
    return subprocess.run(cmd, capture_output=True, text=True)


def _emit(argv, dest):
    proc = _run(argv + ["--emit-json"])
    if proc.returncode != 0:
        sys.stderr.write("REFUSED: could not read the real registration "
                         "(%s):\n%s\n" % (" ".join(argv), proc.stderr[:500]))
        sys.exit(2)
    open(dest, "w").write(proc.stdout)
    return json.loads(proc.stdout)


def selftest():
    opt = "ON" if sys.flags.optimize else "off"
    print("check_bar_above_floor v%s — PLANTED-FAILURE SELFTEST" % VERSION)
    print("python3 -O optimization: %s (sys.flags.optimize=%d)"
          % (opt, sys.flags.optimize))
    print("real registration under test: %s\n" % REAL_MODULE)

    if not os.path.exists(REAL_MODULE):
        sys.stderr.write(
            "REFUSED: the real registration %s is not on disk, so the "
            "two-direction control cannot be driven on real registered "
            "numbers. A selftest that falls back to invented numbers is the "
            "fixture L-530 warns about, and is not offered.\n" % REAL_MODULE)
        sys.exit(2)

    ast_per_mesh = ["--module", REAL_MODULE,
                    "--floor-dict", REAL_FLOOR_DICT,
                    "--bar-dict", REAL_BAR_DICT,
                    "--artifact-dict", REAL_ARTIFACT_DICT,
                    "--bar-min-name", REAL_BAR_MIN_NAME]
    ast_global = ["--module", REAL_MODULE,
                  "--floor-dict", REAL_FLOOR_DICT,
                  "--global-bar", REAL_BAR_MIN_NAME,
                  "--artifact-dict", REAL_ARTIFACT_DICT,
                  "--bar-min-name", REAL_BAR_MIN_NAME]

    cases = []
    with tempfile.TemporaryDirectory() as td:
        j_amended = os.path.join(td, "amended.json")
        j_retired = os.path.join(td, "retired_global.json")
        amended = _emit(ast_per_mesh, j_amended)
        retired = _emit(ast_global, j_retired)

        # PLANT 1 — the silent direction must BREAK. Multiply the one number
        # the detector claims to read, CBFS13700's measured floor, by 100. The
        # registered 1e-1 bar then sits below 10x floor and the silence must end.
        plant_up = json.loads(json.dumps(amended))
        plant_up["meshes"]["CBFS13700"]["floor"] *= 100.0
        j_plant_up = os.path.join(td, "plant_floor_x100.json")
        open(j_plant_up, "w").write(json.dumps(plant_up))

        # PLANT 2 — the refusing direction must STOP. Divide the same real
        # floor by 1000 so the retired 1e-4 bar becomes exactly what the rule
        # derives on all three meshes. If the refusal still fires, the check is
        # not reading the floor at all and every red above is worthless.
        plant_dn = json.loads(json.dumps(retired))
        plant_dn["meshes"]["CBFS13700"]["floor"] /= 1000.0
        j_plant_dn = os.path.join(td, "plant_floor_div1000.json")
        open(j_plant_dn, "w").write(json.dumps(plant_dn))

        # A bar with no measured floor, and a floor whose artifact is gone.
        j_nofloor = os.path.join(td, "no_floor.json")
        open(j_nofloor, "w").write(json.dumps(
            {"bar_min": 1e-4,
             "meshes": {"NASA_2DWMH": {"bar": 1e-4, "artifact": REAL_MODULE}}}))
        j_gone = os.path.join(td, "artifact_gone.json")
        gone = json.loads(json.dumps(amended))
        gone["meshes"]["CBFS13700"]["artifact"] = os.path.join(
            td, "a_file_that_does_not_exist", "U")
        open(j_gone, "w").write(json.dumps(gone))

        cases = [
            # name, argv, expect_rc, must_contain, must_not_contain
            ("REAL amended per-mesh bars (ast, no import)",
             ast_per_mesh, 0, [], ["BAR_BELOW_FLOOR_RULE",
                                   "GLOBAL_BAR_OVER_HETEROGENEOUS_FLOORS",
                                   "FLOOR_ARTIFACT"]),
            ("REAL retired GLOBAL 1e-4 bar (ast, no import)",
             ast_global, 2, ["BAR_BELOW_FLOOR_RULE",
                             "GLOBAL_BAR_OVER_HETEROGENEOUS_FLOORS",
                             "CBFS13700"], []),
            ("REAL amended table, read back as JSON",
             ["--json", j_amended], 0, [], ["BAR_BELOW_FLOOR_RULE"]),
            ("REAL retired global table, read back as JSON",
             ["--json", j_retired], 2, ["BAR_BELOW_FLOOR_RULE"], []),
            ("PLANT floor x100 — the SILENT reading must break",
             ["--json", j_plant_up], 2, ["BAR_BELOW_FLOOR_RULE",
                                         "CBFS13700"], []),
            ("PLANT floor /1000 — the REFUSAL must stop entirely",
             ["--json", j_plant_dn], 0, [],
             ["BAR_BELOW_FLOOR_RULE",
              "GLOBAL_BAR_OVER_HETEROGENEOUS_FLOORS"]),
            ("a bar with NO measured floor",
             ["--json", j_nofloor], 2, ["NO_FLOOR_MEASURED"], []),
            ("a floor whose named artifact is GONE",
             ["--json", j_gone], 2, ["FLOOR_ARTIFACT_NOT_ON_DISK"], []),
            ("a module that names no floor table at all",
             ["--module", REAL_MODULE, "--floor-dict", "NO_SUCH_TABLE",
              "--bar-dict", REAL_BAR_DICT], 3, [], []),
        ]

        fired = 0
        clean = 0
        failures = []
        for name, argv, expect_rc, must, must_not in cases:
            proc = _run(argv)
            out = proc.stdout + proc.stderr
            got = proc.returncode
            ok = (got == expect_rc)
            missing = [c for c in must if c not in out]
            present = [c for c in must_not if c in out]
            ok = ok and not missing and not present
            verb = ("FIRED" if got == 2 else
                    "clean" if got == 0 else "rc=%d" % got)
            print("  %-48s expect rc=%d  got rc=%d  %-5s  %s"
                  % (name[:48], expect_rc, got, verb,
                     "OK" if ok else "**MISMATCH**"))
            if not ok:
                failures.append((name, expect_rc, got, missing, present,
                                 out[:800]))
            elif expect_rc == 2:
                fired += 1
            elif expect_rc == 0:
                clean += 1

    n_bad = sum(1 for c in cases if c[2] == 2)
    n_good = sum(1 for c in cases if c[2] == 0)
    print("\n  refusals driven and observed : %d of %d refusing fixtures"
          % (fired, n_bad))
    print("  clean passes observed        : %d of %d clean fixtures"
          % (clean, n_good))
    print("  BOTH DIRECTIONS were driven on the REAL registered numbers out of")
    print("  %s" % REAL_MODULE)

    if failures:
        print("\nSELFTEST FAILED — %d fixture(s) did not behave as registered:"
              % len(failures))
        for name, exp, got, missing, present, out in failures:
            print("  %s: expected rc=%d, got rc=%d" % (name, exp, got))
            if missing:
                print("    expected code(s) ABSENT from output: %s"
                      % ", ".join(missing))
            if present:
                print("    forbidden code(s) PRESENT in output: %s"
                      % ", ".join(present))
        sys.exit(2)

    if fired == 0:
        sys.stderr.write(
            "REFUSED: the selftest completed without driving a single "
            "refusal. A check not shown able to fire is not evidence — it is "
            "the decoration L-529 names.\n")
        sys.exit(2)
    if clean == 0:
        sys.stderr.write(
            "REFUSED: the selftest never observed a CLEAN read. A check that "
            "fires on everything screens nothing.\n")
        sys.exit(2)

    print("\nSELFTEST GREEN: %d/%d fixtures behaved as registered; the refusal "
          "was DRIVEN AND OBSERVED %d times and the clean read %d times, and "
          "the two PLANTS moved the verdict in BOTH directions by mutating the "
          "one number this check claims to read." % (len(cases), len(cases),
                                                     fired, clean))
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Refuse a registered bar that sits below its own "
                    "instrument's MEASURED floor on the mesh it is applied to "
                    "(L-530).")
    ap.add_argument("--module", help="module carrying the registered tables; "
                                     "parsed with ast, NEVER imported")
    ap.add_argument("--floor-dict", default="CONTINUITY_FLOOR",
                    help="module-level dict of mesh -> measured floor")
    ap.add_argument("--bar-dict", default="CONTINUITY_BAR",
                    help="module-level dict of mesh -> registered bar")
    ap.add_argument("--artifact-dict", default=None,
                    help="module-level dict of mesh -> the named artifact the "
                         "floor was read from (a path, or a tuple whose first "
                         "slot is the path)")
    ap.add_argument("--global-bar", default=None,
                    help="read the bar as ONE module-level scalar applied to "
                         "every mesh in the floor table — how a retired global "
                         "screen is read back")
    ap.add_argument("--bar-min-name", default=None,
                    help="module-level scalar holding the registration's "
                         "minimum bar (BAR_MIN in the rule)")
    ap.add_argument("--bar-min", type=float, default=None,
                    help="the registration's minimum bar, given directly")
    ap.add_argument("--json", dest="json_path", default=None,
                    help="a published bar table: {bar_min, meshes: {tag: "
                         "{floor, bar, artifact}}}, or a bare mapping of the "
                         "same rows")
    ap.add_argument("--spread-decades", type=float,
                    default=DEFAULT_SPREAD_DECADES,
                    help="how many decades of floor spread a single shared bar "
                         "may cover before it is a finding")
    ap.add_argument("--no-artifact-disk-check", action="store_true",
                    help="do not stat the named floor artifacts")
    ap.add_argument("--emit-json", action="store_true",
                    help="print the table this check read, as JSON, and exit 0 "
                         "— so a registration's real numbers are READ rather "
                         "than transcribed into a fixture")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted failures on the real registered "
                         "numbers and prove the refusal fires")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if bool(args.module) == bool(args.json_path):
        sys.stderr.write("REFUSED: give exactly one of --module or --json "
                         "(or --selftest).\n")
        sys.exit(3)

    if args.module:
        table = table_from_module(
            args.module, args.floor_dict, args.bar_dict, args.artifact_dict,
            args.global_bar, args.bar_min_name, args.bar_min)
    else:
        table = table_from_json(args.json_path)
        if args.bar_min is not None:
            table["bar_min"] = args.bar_min

    if args.emit_json:
        print(json.dumps(table, indent=2, sort_keys=True))
        return 0

    findings, cannot_see = evaluate(
        table, spread_decades=args.spread_decades,
        check_disk=not args.no_artifact_disk_check)
    report(table, findings, cannot_see)

    if findings:
        refuse("%d registered bar finding(s). A bar below its own instrument's "
               "measured floor retires cases for instrument reasons while the "
               "record reads as rigour." % len(findings))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
