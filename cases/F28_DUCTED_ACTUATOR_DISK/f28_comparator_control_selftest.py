#!/usr/bin/env python3
"""F28 -- SELFTEST FOR THE REPAIRED COMPARATOR'S PLANTED CONTROLS AND GUARDS.

BOTH LIMBS ON EVERY CONTROL.  A green limb that stays green when you break the
thing it names tests nothing, so every control here is exercised twice: once on
a healthy fixture (it must FIRE / PASS), and once with its OWN LOGIC REVERTED or
with the reader it certifies BROKEN (it must REFUSE / FAIL).  Where the thing
being replaced is real code rather than a hypothesis, the MUTANT IS THE
SUPERSEDED FILE ITSELF -- `analyse_f28.py` at md5
f217d293762b0a644a95f32fb63b850f -- which is the strongest mutation limb
available: it is not a synthetic defect, it is the defect.

Subject: `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28_candidate.py`
Superseded: `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py`

NO SOLVER RUNS.  The fixture is built from artifacts already on disk in
`verification/runs/F28_runs/FEAS_L1_dp1000_U20_A2`, a LABEL=FEASIBILITY run
whose outputs are never gradeable as verdicts; nothing here reports a physical
number as a result.  The function-object series are TRUNCATED to a few rows on
purpose: what is under test is the READER and its CONTROLS, not the physics.

Run:  python3 cases/F28_DUCTED_ACTUATOR_DISK/f28_comparator_control_selftest.py
Exit: 0 every limb held, 1 a limb failed.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATE = os.path.join(HERE, "analyse_f28_candidate.py")
SUPERSEDED = os.path.join(HERE, "analyse_f28.py")
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC_RUN = os.path.join(REPO, "verification", "runs", "F28_runs",
                       "FEAS_L1_dp1000_U20_A2")

END_TIME = 100.0
T0 = 1_700_000_000          # the age anchor's mtime; postProcessing is newer
T_NEW = T0 + 1000

fails = []
_tmpdirs = []


def check(name, ok, detail=""):
    print("  %-4s %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  -- " + detail) if detail else ""))
    if not ok:
        fails.append(name)


def load(path, tag):
    """Import a module from `path` under a unique name.

    __pycache__ is cleared first: stale bytecode has inverted mutation tests in
    this lab before -- a clean control failing while a mutated case passes.
    """
    for d in (os.path.dirname(path), HERE):
        pc = os.path.join(d, "__pycache__")
        if os.path.isdir(pc):
            shutil.rmtree(pc, ignore_errors=True)
    spec = importlib.util.spec_from_file_location("f28_%s" % tag, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mutant(subs, tag):
    """A copy of the candidate with exact string substitutions applied.

    Every substitution must match EXACTLY ONCE or the mutation is refused --
    a mutation test whose mutation silently did not apply is the green that
    means nothing.
    """
    src = open(CANDIDATE).read()
    for old, new in subs:
        n = src.count(old)
        if n != 1:
            raise SystemExit("MUTATION %r matched %d times, not once -- the "
                             "selftest refuses to run a mutation it cannot "
                             "place: %s" % (tag, n, old[:70]))
        src = src.replace(old, new)
    d = tempfile.mkdtemp(prefix="f28mut_")
    _tmpdirs.append(d)
    p = os.path.join(d, "mut_%s.py" % tag)
    open(p, "w").write(src)
    return load(p, tag)


def refuses(fn, *a, **kw):
    """(did_it_refuse, message).  `refuse()` exits 2; `Refusal` is raised.

    stderr is captured, because `refuse()` writes the reason there and exits --
    and WHICH refusal fired is the whole question in a mutation test.  A control
    credited with a refusal another guard actually made is a green that means
    nothing.
    """
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            fn(*a, **kw)
        return False, "returned normally"
    except SystemExit as e:
        return (e.code == 2), buf.getvalue().strip() or "SystemExit(%r)" % (e.code,)
    except Exception as e:                                  # noqa: BLE001
        return type(e).__name__ == "Refusal", "%s: %s" % (type(e).__name__, e)


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ---------------------------------------------------------------------------
# THE FIXTURE
# ---------------------------------------------------------------------------
SFV_HEADER = ("# Region type :   sampledSurface %s\n"
              "# Faces           : 88\n"
              "# Area            : 5.9265905022e-04\n"
              "# Scale factor    : 1.0000000000e+00\n"
              "# Time            \t%s\n")
FORCE_HEADER = ("# %s           \n"
                "# CofR            : (0.0000000000e+00 0.0000000000e+00 0.0)\n"
                "#\n"
                "# Time            \ttotal_x total_y total_z\tpressure_x "
                "pressure_y pressure_z\tviscous_x viscous_y viscous_z\n")


def write_series(path, header, rows, mtime=T_NEW):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(header)
        for t, vals in rows:
            fh.write("%-18s\t%s\n" % (t, " ".join(vals)))
    os.utime(path, (mtime, mtime))


def nine(x):
    return ["%.10e" % x] + ["%.10e" % (x / 7.0)] * 8


def build_fixture(with_source=True, dp_up=-8.4652590895e+02,
                  dp_dn=-8.4652590895e+02 + 1000.0 / 1.2):
    fx = tempfile.mkdtemp(prefix="f28fx_")
    _tmpdirs.append(fx)
    os.makedirs(os.path.join(fx, "0"))
    os.makedirs(os.path.join(fx, "system"))
    os.makedirs(os.path.join(fx, "constant"))
    shutil.copytree(os.path.join(SRC_RUN, "constant", "polyMesh"),
                    os.path.join(fx, "constant", "polyMesh"))
    shutil.copy(os.path.join(SRC_RUN, "constant", "fvOptions"),
                os.path.join(fx, "constant", "fvOptions"))
    open(os.path.join(fx, "system", "controlDict"), "w").write(
        "FoamFile { version 2.0; format ascii; class dictionary; "
        "object controlDict; }\n"
        "writeFormat     ascii;\nwritePrecision  10;\nwriteCompression off;\n")
    # The age anchor.  `0/U` is touched last at launch, so everything the run
    # produced must be NEWER than it.
    open(os.path.join(fx, "0", "U"), "w").write("dummy 0/U age anchor\n")
    os.utime(os.path.join(fx, "0", "U"), (T0, T0))
    tdir = os.path.join(fx, "%g" % END_TIME)
    os.makedirs(tdir)
    shutil.copy(os.path.join(SRC_RUN, "14000", "p"), os.path.join(tdir, "p"))

    rows = [(int(END_TIME) - 2, None), (int(END_TIME) - 1, None),
            (int(END_TIME), None)]
    write_series(os.path.join(fx, "postProcessing", "diskPlaneUp", "0",
                              "surfaceFieldValue.dat"),
                 SFV_HEADER % ("planeUp", "areaAverage(p)"),
                 [(t, ["%.10e" % dp_up]) for t, _ in rows])
    write_series(os.path.join(fx, "postProcessing", "diskPlaneDown", "0",
                              "surfaceFieldValue.dat"),
                 SFV_HEADER % ("planeDown", "areaAverage(p)"),
                 [(t, ["%.10e" % dp_dn]) for t, _ in rows])
    write_series(os.path.join(fx, "postProcessing", "diskFlow", "0",
                              "surfaceFieldValue.dat"),
                 SFV_HEADER % ("planeFlow", "areaNormalIntegrate(U)"),
                 [(t, ["%.10e" % 2.1887020890e-02] ) for t, _ in rows])
    # `forces` writes BOTH of these, with IDENTICAL column names and times.
    write_series(os.path.join(fx, "postProcessing", "forcesDuct", "0",
                              "force.dat"),
                 FORCE_HEADER % "Force",
                 [(t, nine(-3.2288097331e-01)) for t, _ in rows])
    write_series(os.path.join(fx, "postProcessing", "forcesDuct", "0",
                              "moment.dat"),
                 FORCE_HEADER % "Moment",
                 [(t, nine(-4.3230998769e-19)) for t, _ in rows])
    return fx, os.path.join(fx, "0", "U"), tdir


print("=== F28 COMPARATOR CONTROL SELFTEST ===")
print("subject:    %s" % CANDIDATE)
print("superseded: %s  md5 %s"
      % (SUPERSEDED,
         hashlib.md5(open(SUPERSEDED, "rb").read()).hexdigest()))
print()

cand = load(CANDIDATE, "cand")
old = load(SUPERSEDED, "old")
FX, AGE, TDIR = build_fixture()

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 1 -- THE PLANT ON function_object_series (defect 1) ===")
# POSITIVE: the control fires on the reader that actually grades.
r = cand.plant_into_function_object(FX, "diskPlaneUp", "areaAverage(p)",
                                    END_TIME, AGE)
check("plant fires on function_object_series",
      r["fired"] and r["unperturbed_twin_silent"],
      "column %r index %d, plant %.4g" % (r["column"], r["column_index"],
                                          r["plant"]))
check("the graded .dat is BYTE-IDENTICAL after a successful control",
      r["artifact_byte_identical"], "sha256 %s" % r["artifact"]["sha256"][:16])

# MUTATION A -- break the READER the control certifies, with the defect this
# control exists to catch: a STALE CACHE, so the second read returns the
# pre-plant row.  `Time` is still correct, so nothing but the plant's own
# refusal can catch it -- an earlier attempt at this mutation made the reader
# return the FIRST row, and the endTime check caught that instead, which would
# have credited the plant with a refusal it did not make.
STALE_READER = [
    ("def _parse_fo_file(path):",
     "_FOCACHE = {}\n\n\ndef _parse_fo_file(path):\n"
     "    if path in _FOCACHE:\n        return _FOCACHE[path]"),
    ("    return dict(zip(cols, (float(v) for v in vals)))",
     "    return _FOCACHE.setdefault(path, dict(zip(cols, "
     "(float(v) for v in vals))))"),
]
mA = mutant(STALE_READER, "fo_stale_reader")
ok, msg = refuses(mA.plant_into_function_object, FX, "diskPlaneUp",
                  "areaAverage(p)", END_TIME, AGE)
check("MUTATION: a reader that cannot see the plant is REFUSED", ok, msg)
check("...and it is the PLANT's refusal that caught it, not another guard",
      "PLANTED CONTROL ON function_object_series DID NOT FIRE" in msg
      or "DID NOT FIRE" in msg, msg[:90])

# MUTATION B -- revert THE CONTROL'S OWN LOGIC (drop its refusal) on top of the
# same broken reader.  The blind reader must now sail through, which is what
# proves the refusal -- and not something else -- is what caught it.
mB = mutant(STALE_READER
            + [("        if abs(seen - PLANT_FO) > tol:\n",
                "        if False and abs(seen - PLANT_FO) > tol:\n"),
               ("        if abs(twin[column] - before) > tol:\n",
                "        if False and abs(twin[column] - before) > tol:\n")],
            "fo_no_refusal")
ok, msg = refuses(mB.plant_into_function_object, FX, "diskPlaneUp",
                  "areaAverage(p)", END_TIME, AGE)
check("MUTATION: with the control's refusal reverted the blind reader PASSES",
      not ok, msg)

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 2 -- THE GRADED ARTIFACT IS NOT REWRITTEN (defect 3) ===")
a = os.path.join(TDIR, "p")
b = a + ".supersededcopy"
shutil.copy(a, b)
s_before = sha(a)
mt_before = os.stat(a).st_mtime_ns
rp = cand.plant_into_p(a)
check("plant fires on read_volScalarField", rp["fired"] and
      rp["unperturbed_twin_silent"], "cell %d" % rp["cell_index"])
check("candidate leaves `p` BYTE-IDENTICAL", sha(a) == s_before,
      "sha256 %s" % s_before[:16])
check("candidate leaves `p` mtime UNMOVED", os.stat(a).st_mtime_ns == mt_before)
check("candidate leaves the FoamFile header intact",
      b"FoamFile" in open(a, "rb").read())

# MUTATION -- the superseded implementation, run on an identical copy.  This is
# not a synthetic defect: it is the code being replaced.
n_before = os.path.getsize(b)
old.plant_into_p(b)
n_after = os.path.getsize(b)
check("MUTATION (the superseded plant_into_p): artifact is CORRUPTED",
      sha(b) != s_before and b"FoamFile" not in open(b, "rb").read(),
      "%d -> %d bytes, FoamFile header DELETED, after a control that reported "
      "success" % (n_before, n_after))

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 3 -- C3 ARM (b): fvOptions AND cell_volumes (defect 1) ===")
rf = cand.plant_into_fvoptions(FX)
check("plant fires on read_fvoptions_source", rf["fired"] and
      rf["unperturbed_twin_silent"], "Su_x = %.10g m/s^2" % rf["Su_x_before"])
check("constant/fvOptions BYTE-IDENTICAL after the control",
      rf["artifact_byte_identical"])
mC = mutant([('    t = _strip_foam_comments(open(p, errors="replace").read())\n'
              '    mode = sole_entry(',
              '    t = _FVCACHE.setdefault(p, _strip_foam_comments('
              'open(p, errors="replace").read()))\n'
              '    mode = sole_entry('),
             ("class Refusal(Exception):", "_FVCACHE = {}\n\n\nclass Refusal(Exception):")],
            "fvopt_stale")
ok, msg = refuses(mC.plant_into_fvoptions, FX)
check("MUTATION: a stale fvOptions reader is REFUSED", ok, msg)

rv = cand.plant_into_points(FX, "disk")
check("plant fires on cell_volumes", rv["fired"] and
      rv["unperturbed_twin_silent"],
      "point %d, V %.10g -> %.10g m^3"
      % (rv["point_index"], rv["zone_volume_m3"],
         rv["zone_volume_perturbed_m3"]))
check("constant/polyMesh/points BYTE-IDENTICAL after the control",
      rv["artifact_byte_identical"])
mD = mutant([('def _body(path):\n    t = open(path, errors="replace").read()',
              'def _body(path):\n    t = _BCACHE.setdefault('
              'path, open(path, errors="replace").read())'),
             ("class Refusal(Exception):",
              "_BCACHE = {}\n\n\nclass Refusal(Exception):")], "mesh_stale")
ok, msg = refuses(mD.plant_into_points, FX, "disk")
check("MUTATION: a stale mesh reader is REFUSED", ok, msg)

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 4 -- THE AGE GUARD REACHES postProcessing (defect 2) ===")
stale = os.path.join(FX, "postProcessing", "diskFlow", "0",
                     "surfaceFieldValue.dat")
os.utime(stale, (T0 - 500, T0 - 500))           # older than 0/U
ok, msg = refuses(cand.function_object_series, FX, "diskFlow",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("a function-object file OLDER than 0/U is REFUSED", ok, msg)
mE = mutant([("        if mt <= t0:\n", "        if False and mt <= t0:\n")],
            "no_age_guard")
ok, msg = refuses(mE.function_object_series, FX, "diskFlow",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("MUTATION: with the age guard reverted the stale file is ACCEPTED",
      not ok, msg)
# And the superseded reader, which never stat'd a function-object file at all.
row = old.function_object_series(FX, "diskFlow")
check("MUTATION (the superseded reader): grades the stale file silently",
      row is not None, "returned Time=%r" % (row or {}).get("Time"))
os.utime(stale, (T_NEW, T_NEW))

ok, msg = refuses(cand.function_object_series, FX, "diskFlow",
                  "surfaceFieldValue.dat", END_TIME + 1.0, AGE)
check("a series that does not reach endTime is REFUSED", ok, msg)
mF = mutant([('    if abs(best["Time"] - end_time) > 1e-9:\n',
              '    if False and abs(best["Time"] - end_time) > 1e-9:\n')],
            "no_endtime")
ok, msg = refuses(mF.function_object_series, FX, "diskFlow",
                  "surfaceFieldValue.dat", END_TIME + 1.0, AGE)
check("MUTATION: with the endTime check reverted the short series is ACCEPTED",
      not ok, msg)

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 5 -- A MOMENT IS NOT A FORCE (defect 7, measured) ===")
t_cand = cand.total_thrust(FX, END_TIME, AGE)["T_duct"]
t_old = old.total_thrust(FX)["T_duct"]
check("candidate reads force.dat", abs(t_cand - 23.24742) < 1e-3,
      "T_duct = %+.6g N" % t_cand)
check("MUTATION (the superseded reader): reads moment.dat and calls it a force",
      abs(t_old) < 1e-10 and abs(t_old) < 1e-15 * abs(t_cand),
      "T_duct = %+.6g N against %+.6g N -- 17 orders down and a DIFFERENT "
      "PHYSICAL QUANTITY (N.m, not N).  Not a sign flip on this arm: worse, "
      "section 6.3's registered SIGN gate would have been decided by the sign "
      "of a rounding-level moment component." % (t_old, t_cand))

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 6 -- DETERMINISTIC ROW SELECTION (defect 5) ===")
d2 = os.path.join(FX, "postProcessing", "diskPlaneUp", "50")
write_series(os.path.join(d2, "surfaceFieldValue.dat"),
             SFV_HEADER % ("planeUp", "areaAverage(p)"),
             [(int(END_TIME), ["%.10e" % -1.0])])
ok, msg = refuses(cand.function_object_series, FX, "diskPlaneUp",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("two files tied at the final Time with DIFFERENT rows are REFUSED",
      ok, msg)
mG = mutant([("        if any(rows[p] != first for p in tied[1:]):\n",
              "        if False and any(rows[p] != first for p in tied[1:]):\n")],
            "no_tie_refusal")
ok, msg = refuses(mG.function_object_series, FX, "diskPlaneUp",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("MUTATION: with the tie refusal reverted a winner is picked silently",
      not ok, msg)
shutil.rmtree(d2)

notime = os.path.join(FX, "postProcessing", "noTime", "0")
write_series(os.path.join(notime, "surfaceFieldValue.dat"),
             "# Region type :   x\n# Iter            \tareaAverage(p)\n",
             [(int(END_TIME), ["%.10e" % 1.0])])
ok, msg = refuses(cand.function_object_series, FX, "noTime",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("a file with NO `Time` column is REFUSED", ok, msg)
mH = mutant([('    if "Time" not in cols:\n',
              '    if False and "Time" not in cols:\n')], "no_time_refusal")
ok, msg = refuses(mH.function_object_series, FX, "noTime",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("MUTATION: with that refusal reverted the Time-less file is ACCEPTED",
      not ok, msg)

ok, msg = refuses(cand.function_object_series, FX, "forcesDuct",
                  "surfaceFieldValue.dat", END_TIME, AGE)
check("a NAMED file that is absent is REFUSED, not substituted", ok, msg)

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 7 -- writeFormat (defect 6) AND guard_virgin_case (4) ===")
wf = cand.assert_write_format(FX)
check("assert_write_format accepts `ascii`", wf["writeFormat"] == "ascii",
      "writePrecision %r, RECORDED not gated" % wf["writePrecision"])
cd = os.path.join(FX, "system", "controlDict")
keep = open(cd).read()
open(cd, "w").write(keep.replace("writeFormat     ascii;",
                                 "writeFormat     binary;"))
ok, msg = refuses(cand.assert_write_format, FX)
check("assert_write_format REFUSES `binary`", ok, msg)
open(cd, "w").write(keep.replace("writeFormat     ascii;\n", ""))
ok, msg = refuses(cand.assert_write_format, FX)
check("assert_write_format REFUSES a MISSING writeFormat", ok, msg)
open(cd, "w").write(keep)

ok, msg = refuses(cand.guard_virgin_case, FX)
check("guard_virgin_case REFUSES a case that already has `0`", ok, msg)
virgin = tempfile.mkdtemp(prefix="f28virgin_")
_tmpdirs.append(virgin)
ok, msg = refuses(cand.guard_virgin_case, virgin)
check("guard_virgin_case ACCEPTS a virgin directory", not ok, msg)
check("guard_virgin_case now HAS a call site", "--guard-virgin" in
      open(CANDIDATE).read(), "`--guard-virgin` entry point in main()")

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 8 -- NOTHING THE REVIEWS CALLED SOUND HAS MOVED ===")
v_new = cand.cell_volumes(FX)
v_old = old.cell_volumes(FX)
check("cell_volumes is BIT-IDENTICAL to the superseded implementation",
      len(v_new) == len(v_old) and all(a == b for a, b in zip(v_new, v_old)),
      "%d cells, exact equality on every one" % len(v_new))
check("WEDGE_SCALE is still the named constant 72",
      cand.WEDGE_SCALE == old.WEDGE_SCALE == 72.0)
check("C4's negative limb is still ONE-WAY", "C4 is one-way" in
      open(CANDIDATE).read())

print("=== LIMB GROUP 8b -- THE volumeMode GUARD READS THE LIVE ENTRY (defect 9) ===")
# The LIVE entry is set to `absolute` -- the silent factor registration section
# 2.4 calls load-bearing -- while the BANNER COMMENT on line 6 is left saying
# `volumeMode specific;`, exactly as `fvOptions.template` always writes it.
fv = os.path.join(FX, "constant", "fvOptions")
kept = open(fv).read()
live = re.compile(r"(?m)^(\s*volumeMode\s+)specific(\s*;)")
assert live.search(kept), "fixture has no live volumeMode entry to mutate"
comment_says = "`volumeMode specific;`" in kept
open(fv, "w").write(live.sub(r"\1absolute\2", kept))
check("the fixture is the real trap: comment says `specific`, live entry says "
      "`absolute`", comment_says and
      re.search(r"(?m)^\s*volumeMode\s+absolute\s*;", open(fv).read()) is not None)
ok, msg = refuses(cand.read_fvoptions_source, FX)
check("candidate REFUSES a live `volumeMode absolute;`", ok, msg[:150])
ok_old, msg_old = refuses(old.read_fvoptions_source, FX)
check("MUTATION (the superseded reader): ACCEPTS it, reading the comment",
      not ok_old,
      "returned volumeMode=%r from line 6 of the banner while the live entry "
      "on line 56 says `absolute` -- the guard on the first of the three "
      "silent factors was blind"
      % (old.read_fvoptions_source(FX)["volumeMode"],))
mI = mutant([('    t = _strip_foam_comments(open(p, errors="replace").read())\n'
              '    mode = sole_entry(',
              '    t = open(p, errors="replace").read()\n'
              '    mode = sole_entry(')], "no_comment_strip")
ok, msg = refuses(mI.read_fvoptions_source, FX)
check("MUTATION: with ONLY the comment stripper reverted it STILL refuses -- "
      "the two halves of the fix are independently sufficient", ok,
      "on AMBIGUOUS ENTRY (2 matches, lines [6, 56]) rather than on the value")
open(fv, "w").write(kept)

# -- THE MATRIX verification REQUIRED: FOUR states x THREE keys, every cell
# -- DRIVEN.  This is the class that stayed green through two independent,
# -- personal, non-delegable supervisor check-1 reads, so nothing here is
# -- reasoned about.  THE BLIND MUTANT IS `old` -- the superseded file itself,
# -- which is exactly "no comment stripping + re.search takes the first match".
QUOTE_ANCHOR = ("  `volumeMode specific;` APPEARS HERE VERBATIM AND IS "
                "LOAD-BEARING.")
assert QUOTE_ANCHOR in kept, "fixture banner comment not as expected"
KEYS = (("volumeMode", "specific", "absolute"),
        ("selectionMode", "cellZone", "faceZone"),
        ("cellZone", "disk", "elsewhere"))
for key, good, bad in KEYS:
    live = re.compile(r"(?m)^(\s*%s\s+)%s(\s*;)" % (key, good))
    assert live.search(kept), "fixture has no live `%s` entry" % key
    quoting = kept.replace(QUOTE_ANCHOR, QUOTE_ANCHOR + "\n"
                           "  `%s %s;` IS REGISTERED AND LOAD-BEARING TOO."
                           % (key, good))
    assert quoting != kept, "planted comment did not land for %s" % key

    # STATE 1 -- live entry WRONG.
    open(fv, "w").write(live.sub(r"\1%s\2" % bad, kept))
    ok, _ = refuses(cand.read_fvoptions_source, FX)
    check("%-13s live entry WRONG (`%s`) -> REFUSE" % (key + ":", bad), ok)

    # STATE 2 -- live entry DELETED ENTIRELY.  verification's own test, the one
    # that proved the superseded guard reports `specific` even for absence.
    open(fv, "w").write(live.sub("", kept))
    ok, msg = refuses(cand.read_fvoptions_source, FX)
    check("%-13s live entry DELETED -> REFUSE, never a default" % (key + ":"),
          ok and "ABSENT ENTRY" in msg)

    # STATE 3 -- THE CLASS DEFECT.  Live entry WRONG, and a comment QUOTES THE
    # CORRECT ONE VERBATIM.  For volumeMode the real banner already does this;
    # for the two siblings it is one careful comment away, which is the point.
    open(fv, "w").write(live.sub(r"\1%s\2" % bad, quoting))
    ok, _ = refuses(cand.read_fvoptions_source, FX)
    check("%-13s live WRONG + comment QUOTING the right value -> REFUSE"
          % (key + ":"), ok)
    ok_old, _ = refuses(old.read_fvoptions_source, FX)
    check("  MUTATION (the superseded reader): reads the comment, ACCEPTS it",
          not ok_old, "blind on `%s`" % key)

    # STATE 4 -- NO FALSE ALARM.  Live entry CORRECT with the same quoting
    # comment present: the repaired guard must still pass it.
    open(fv, "w").write(quoting)
    ok, _ = refuses(cand.read_fvoptions_source, FX)
    check("%-13s live CORRECT + the same quoting comment -> ACCEPT"
          % (key + ":"), not ok)

# MULTIPLICITY -- two LIVE entries must refuse, not silently take the first.
open(fv, "w").write(kept.replace("    volumeMode      specific;",
                                 "    volumeMode      specific;\n"
                                 "    volumeMode      absolute;"))
ok, msg = refuses(cand.read_fvoptions_source, FX)
check("two LIVE `volumeMode` entries -> REFUSE rather than take the first",
      ok and "AMBIGUOUS ENTRY" in msg)
ok_old, _ = refuses(old.read_fvoptions_source, FX)
check("  MUTATION (the superseded reader): takes the first silently", not ok_old)
open(fv, "w").write(kept)
check("the fixture is restored byte-for-byte", open(fv).read() == kept)

print("=== LIMB GROUP 8 (cont.) ===")
check("section 6.3 still registers SIGN as well as magnitude",
      "sign_pass_must_be_drag" in open(CANDIDATE).read())
check("the strict completion rule still has all six clauses plus clause 7",
      all(("clause %d" % i) in open(CANDIDATE).read() for i in range(1, 8)))

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 9 -- ADDENDUM 3's UNWIRED CHANNEL IS NOT GRADED ===")
src = open(CANDIDATE).read()
check("section 6.3 REFUSES rather than grading without the registered "
      "stationarity channel",
      "SECTION 6.3 CANNOT BE GRADED BY THIS COMPARATOR" in src)
check("the refusal names the SECTOR frame and the full-annulus value",
      "5-DEGREE SECTOR" in src and "STATIONARITY_FLOOR_SECTOR_N" in src)
check("the floor is carried in sector newtons, not full-annulus newtons",
      abs(cand.STATIONARITY_FLOOR_SECTOR_N - 5.934119457e-04) < 1e-13,
      "full-annulus would be %.4e N, a factor of %g away"
      % (0.001 * cand.A_DISK * 1000.0, cand.WEDGE_SCALE))

print("=== LIMB GROUP 10 -- END-TO-END PLUMBING OF control_6_2 / control_6_3 ===")
# >>> THE VERDICTS BELOW ARE NOT RESULTS AND MUST NEVER BE CITED AS ONE.  The
# >>> function-object series in this fixture are FABRICATED, no solver ran, and
# >>> the fixture exists to prove that the repaired call graph EXECUTES -- that
# >>> every new argument (`filename`, `end_time`, `age_ref`) is threaded to
# >>> every call site and no path raises TypeError or NameError.  A repair whose
# >>> pieces each pass in isolation and whose wiring is untested is half-checked.


def finish_case(fx, tdir):
    """Give a fixture the things `completion()` requires."""
    with open(os.path.join(fx, "log.simpleFoam"), "w") as fh:
        for i in range(int(END_TIME)):
            fh.write("ExecutionTime = %g s  ClockTime = %d s\n" % (i * 0.1, i))
        fh.write("End\n")
    for f in ("U", "k", "omega", "nut"):
        open(os.path.join(tdir, f), "w").write("stub field %s\n" % f)
    for root, _d, files in os.walk(fx):
        for f in files:
            p = os.path.join(root, f)
            if os.path.abspath(p) != os.path.abspath(os.path.join(fx, "0", "U")):
                os.utime(p, (T_NEW, T_NEW))
    return fx


DP = 1000.0
PLANT_CASE = finish_case(*build_fixture()[::2])
BASE_CASE = finish_case(*build_fixture(dp_up=-100.0, dp_dn=-100.0)[::2])
C4_CASE = finish_case(*build_fixture(dp_up=-100.0,
                                     dp_dn=-100.0 + 2 * DP / 1.2)[::2])
# The baseline must carry NO source (delta_p = 0) and a SMALLER mass flow.
for c, q in ((BASE_CASE, 1.0e-02),):
    f = os.path.join(c, "postProcessing", "diskFlow", "0",
                     "surfaceFieldValue.dat")
    write_series(f, SFV_HEADER % ("planeFlow", "areaNormalIntegrate(U)"),
                 [(int(END_TIME) - 2, ["%.10e" % q]),
                  (int(END_TIME) - 1, ["%.10e" % q]),
                  (int(END_TIME), ["%.10e" % q])])

try:
    out = cand.control_6_2(PLANT_CASE, BASE_CASE, C4_CASE, END_TIME, 0, 0, 0)
    ran, why = True, ""
except SystemExit as e:
    out, ran, why = None, False, "SystemExit(%r)" % (e.code,)
except Exception as e:                                      # noqa: BLE001
    out, ran, why = None, False, "%s: %s" % (type(e).__name__, e)
check("control_6_2 runs end to end (wiring, not physics)", ran, why)
if ran:
    pc = out["planted_control"]
    check("all SIX graded readers carry a fired plant in one run",
          pc["read_volScalarField"]["fired"]
          and pc["read_fvoptions_source"]["fired"]
          and pc["cell_volumes"]["fired"]
          and len(pc["function_object_series"]) == 6
          and all(v["fired"] for v in pc["function_object_series"].values()),
          "function_object_series plants: %s"
          % ", ".join(sorted(pc["function_object_series"])))
    check("the baseline was held to the completion rule",
          "completion_baseline" in out,
          out["completion_baseline"]["clauses"])
    check("C1..C4 all evaluated", sorted(out["conditions"]) ==
          ["C1", "C2", "C3", "C4"])
    print("       [NOT A RESULT -- fabricated fixture, no solver ran] "
          "structural verdict field = %r" % out["verdict"])

# The EMPTY DUCT: `delta_p = 0`, so `Su_x = 0` -- exactly what the launcher
# writes for section 6.3, and exactly what the superseded reader refused.
EMPTY_CASE = finish_case(*build_fixture()[::2])
fv_e = os.path.join(EMPTY_CASE, "constant", "fvOptions")
_loaded = open(fv_e).read()          # read BEFORE opening for write: "w" truncates
assert "((166666.66666666666 0 0) 0)" in _loaded, "fixture fvOptions unexpected"
open(fv_e, "w").write(_loaded.replace("((166666.66666666666 0 0) 0)",
                                      "((0 0 0) 0)"))
os.utime(fv_e, (T_NEW, T_NEW))
# Drag: T_duct must be negative, so total_x must be POSITIVE before the flip.
write_series(os.path.join(EMPTY_CASE, "postProcessing", "forcesDuct", "0",
                          "force.dat"), FORCE_HEADER % "Force",
             [(int(END_TIME) - 2, nine(4.0e-03)),
              (int(END_TIME) - 1, nine(4.0e-03)),
              (int(END_TIME), nine(4.0e-03))])

ok_old, msg_old = refuses(old.read_fvoptions_source, EMPTY_CASE)
check("MUTATION (the superseded reader): REFUSES the registered zero source, "
      "so section 6.3 could never pass", ok_old, msg_old[:130])
src = cand.read_fvoptions_source(EMPTY_CASE, zero_source_expected=True)
check("candidate accepts a zero source ONLY where one is registered",
      src["Su"][0] == 0.0)
ok, _ = refuses(cand.read_fvoptions_source, EMPTY_CASE)
check("...and REFUSES the same file when no zero source is registered", ok)
neg = open(fv_e).read().replace("((0 0 0) 0)", "((-1.0 0 0) 0)")
open(fv_e, "w").write(neg)
ok, msg = refuses(cand.read_fvoptions_source, EMPTY_CASE,
                  zero_source_expected=True)
check("...and STILL refuses a -x source even with a zero source registered",
      ok, msg[:110])
open(fv_e, "w").write(neg.replace("((-1.0 0 0) 0)", "((0 0 0) 0)"))
os.utime(fv_e, (T_NEW, T_NEW))

ok, msg = refuses(cand.control_6_3, EMPTY_CASE, 42.7256601, END_TIME, 0)
check("control_6_3 runs end to end and REFUSES on the unwired stationarity "
      "channel", ok, msg.split("\n")[0][:110])
check("...and it got far enough to plant on forcesDuct and test sign/magnitude",
      "Addendum 3" in msg and "SECTOR NEWTONS" in msg)

print()
for d in _tmpdirs:
    shutil.rmtree(d, ignore_errors=True)
if fails:
    print("SELFTEST FAILED -- %d limb(s): %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("SELFTEST PASSED -- every limb held, and every mutation limb went red.")
sys.exit(0)
