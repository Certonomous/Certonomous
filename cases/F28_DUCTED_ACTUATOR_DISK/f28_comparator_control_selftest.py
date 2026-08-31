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
                  dp_dn=-8.4652590895e+02 + 1000.0 / 1.2,
                  end_time=END_TIME, n_force_rows=3):
    """`end_time` and `n_force_rows` default to the values every pre-existing
    limb was written against, so adding them changes no fixture already in use.

    They exist because Addendum 3's stationarity channel grades a 2000-row
    window: the section 6.3 fixture needs a `forcesDuct` series LONGER than the
    registered window, and a fixture whose series is shorter than the criterion
    would test the refusal instead of the criterion.
    """
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
    tdir = os.path.join(fx, "%g" % end_time)
    os.makedirs(tdir)
    shutil.copy(os.path.join(SRC_RUN, "14000", "p"), os.path.join(tdir, "p"))

    rows = [(int(end_time) - 2, None), (int(end_time) - 1, None),
            (int(end_time), None)]
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
    frows = [int(end_time) - n_force_rows + 1 + i for i in range(n_force_rows)]
    write_series(os.path.join(fx, "postProcessing", "forcesDuct", "0",
                              "force.dat"),
                 FORCE_HEADER % "Force",
                 [(t, nine(-3.2288097331e-01)) for t in frows])
    write_series(os.path.join(fx, "postProcessing", "forcesDuct", "0",
                              "moment.dat"),
                 FORCE_HEADER % "Moment",
                 [(t, nine(-4.3230998769e-19)) for t in frows])
    return fx, os.path.join(fx, "0", "U"), tdir


def real_arm_fixture(arm, end_time=15000.0):
    """A case directory carrying ONE real arm's `force.dat`, unaltered.

    The acceptance limb reproduces the registration's own table, and it must do
    so THROUGH THE WIRED CODE from THE ARTIFACT ON DISK -- not from numbers
    typed into this file.  So the arm's `postProcessing/forcesDuct/0/force.dat`
    is COPIED BYTE-FOR-BYTE (`shutil.copy2`, contents and mtime), the age anchor
    is dated behind it, and the comparator's own reader chain does the rest.
    Nothing else about the arm is fabricated because nothing else is read.
    """
    src = os.path.join(REPO, "verification", "runs", "F28_runs", arm,
                       "postProcessing", "forcesDuct", "0", "force.dat")
    if not os.path.isfile(src):
        return None, None
    fx = tempfile.mkdtemp(prefix="f28arm_")
    _tmpdirs.append(fx)
    os.makedirs(os.path.join(fx, "0"))
    dst = os.path.join(fx, "postProcessing", "forcesDuct", "0", "force.dat")
    os.makedirs(os.path.dirname(dst))
    shutil.copy2(src, dst)
    age = os.path.join(fx, "0", "U")
    open(age, "w").write("dummy 0/U age anchor\n")
    os.utime(age, (os.path.getmtime(dst) - 1000, os.path.getmtime(dst) - 1000))
    return fx, age


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
print("=== LIMB GROUP 9 -- ADDENDUM 3's FLOOR IS DERIVED, NOT PASTED ===")
# Limb group 9 previously asserted that the channel was NOT graded and that
# section 6.3 REFUSED.  That refusal was correct while the criterion was
# unwired and the supervisor ruled it standing "until the criterion is wired"
# (CHECK1_ANALYSE_F28_CANDIDATE.md, ruling 1).  It is wired, so the limb that
# certified its absence is replaced by limbs that certify its presence.
src = open(CANDIDATE).read()
# The struck refusal's text SURVIVES IN A COMMENT, because a change is disclosed
# by naming what it removed.  So this limb asks the question limb group 8b was
# built for -- is the live line what the comment says? -- and answers it the
# same way: EVERY surviving occurrence must be on a comment line.  (Written the
# obvious way, as a bare `not in src`, this limb FAILED against a correctly
# wired file, caught by the comment it was reading.  Kept as measured.)
_hits = [ln for ln in src.splitlines()
         if "SECTION 6.3 CANNOT BE GRADED BY THIS COMPARATOR" in ln]
check("the standing 'CANNOT BE GRADED' refusal is STRUCK from the LIVE code",
      _hits and all(ln.lstrip().startswith("#") for ln in _hits),
      "%d surviving occurrence(s), all in comments disclosing the strike"
      % len(_hits))
d = cand.FLOOR_DERIVATION
check("the geometry chain IS Addendum 3 section 4's, by exact equality",
      cand.R_TIP == cand.D / 2.0 - 0.01 * cand.D
      and cand.R_HUB == 0.3 * cand.D / 2.0,
      "r_tip = D/2 - 0.01 D = %.17g m, r_hub = 0.3 D / 2 = %.17g m"
      % (cand.R_TIP, cand.R_HUB))
for nm, unit in (("A_disk", "m^2"), ("T_disk_ref,full", "N"),
                 ("T_floor,sector", "N")):
    e = d[nm]
    check("%-16s derived %.12g %s agrees with %s's %.12g"
          % (nm, e["derived"], unit, e["authority"].split(", ")[0]
             .replace("registration ", ""), e["registered"]),
          e["abs_difference"] <= e["tolerance"],
          "|diff| %.3e <= %.3e (half the last digit printed)"
          % (e["abs_difference"], e["tolerance"]))
check("T_floor is the DERIVED product, bit-for-bit, not the printed literal",
      cand.STATIONARITY_FLOOR_SECTOR_N
      == 0.001 * ((1000.0 * cand.A_DISK) / cand.WEDGE_SCALE)
      and cand.STATIONARITY_FLOOR_SECTOR_N != 5.934119457e-04,
      "%.17e derived; the registration prints %.9e, and the two are NOT the "
      "same double -- which is the tell that the code derives rather than "
      "pastes" % (cand.STATIONARITY_FLOOR_SECTOR_N, 5.934119457e-04))
check("the floor is in SECTOR newtons, and the full-annulus value is named "
      "but never compared against",
      abs(cand.STATIONARITY_FLOOR_FULL_N
          - cand.WEDGE_SCALE * cand.STATIONARITY_FLOOR_SECTOR_N) < 1e-15
      and "STATIONARITY_FLOOR_FULL_N" not in src.split(
          "def stationarity_criterion")[1].split("def thrust_stationarity")[0],
      "sector %.6e N, full-annulus %.6e N, factor %g apart"
      % (cand.STATIONARITY_FLOOR_SECTOR_N, cand.STATIONARITY_FLOOR_FULL_N,
         cand.WEDGE_SCALE))

# MUTATION -- THE FRAME SLIP, made in the derivation itself: scale to the full
# annulus instead of the sector.  This is the exact 72x error Addendum 3
# section 5 exists to foreclose, and the import-time assertion must kill it.
FRAME_SLIP = [("STATIONARITY_FLOOR_SECTOR_N = STATIONARITY_REL "
               "* T_DISK_REF_SECTOR_N",
               "STATIONARITY_FLOOR_SECTOR_N = STATIONARITY_REL "
               "* T_DISK_REF_FULL_N")]
ok, msg = refuses(mutant, FRAME_SLIP, "floor_frame_slip")
check("MUTATION: a floor derived in the FULL-ANNULUS frame REFUSES AT IMPORT",
      ok, msg[:120])
check("...and it is the DERIVATION assertion that caught it",
      "THE DERIVED FLOOR DOES NOT REPRODUCE THE REGISTERED ONE" in msg)
ok, msg = refuses(mutant, FRAME_SLIP + [
    ("        if not abs(derived - registered) <= tol:\n",
     "        if False and abs(derived - registered) <= tol:\n")],
    "floor_no_assert")
check("MUTATION: with that assertion reverted the 72x-wrong floor IMPORTS "
      "CLEAN", not ok, msg[:100])

# MUTATION -- the literal pasted back in place of the chain.  It must still
# import (the literal IS the registered value), but it must no longer be the
# derived double: the limb above is what distinguishes the two.
mPaste = mutant([("STATIONARITY_FLOOR_SECTOR_N = STATIONARITY_REL "
                  "* T_DISK_REF_SECTOR_N",
                  "STATIONARITY_FLOOR_SECTOR_N = 5.934119457e-04")],
                "floor_pasted")
check("MUTATION: a PASTED floor is a different double from the derived one",
      mPaste.STATIONARITY_FLOOR_SECTOR_N
      != cand.STATIONARITY_FLOOR_SECTOR_N,
      "pasted %.17e vs derived %.17e -- %.3e apart, which is why the check "
      "above is an equality against the CHAIN and not against the literal"
      % (mPaste.STATIONARITY_FLOOR_SECTOR_N, cand.STATIONARITY_FLOOR_SECTOR_N,
         abs(mPaste.STATIONARITY_FLOOR_SECTOR_N
             - cand.STATIONARITY_FLOOR_SECTOR_N)))
# ...and a WRONG geometry chain must not be rescued by the printed literal.
ok, msg = refuses(mutant, [("R_HUB        = 0.15 * D",
                            "R_HUB        = 0.10 * D")], "hub_wrong")
check("MUTATION: a wrong hub radius REFUSES AT IMPORT", ok,
      "on the exact-equality check against `0.3 D / 2`"
      if "GEOMETRY CHAIN IS NOT SECTION 4" in msg else msg[:110])

print("=== LIMB GROUP 9b -- THE FLOOR IS THRUST-ONLY (Addendum 3 s.3) ===")
# Addendum 3 section 3, final paragraph: the disk mass-flow stationarity row is
# NOT touched, and a mass-flow floor is "not derived, not registered and not in
# force".  This is the boundary of Sanaa's approval, so it is enforced in code.
r = cand.stationarity_criterion(1.0e-05, -0.33372464, "thrust")
check("the criterion evaluates THRUST", r["governing_limb"] in ("FLOOR",
                                                                "RELATIVE"),
      "limit %.6e N, governing %s" % (r["limit_N"], r["governing_limb"]))
check("FLOORED_QUANTITIES registers thrust AND NOTHING ELSE",
      cand.FLOORED_QUANTITIES == ("thrust",), repr(cand.FLOORED_QUANTITIES))
for q in ("disk mass flow", "mdot", "mass_flow", "diskFlow"):
    ok, msg = refuses(cand.stationarity_criterion, 1.0e-05, 2.1887e-02, q)
    check("the floor REFUSES to be applied to %r" % q, ok
          and "NOT REGISTERED FOR" in msg)
# MUTATION -- revert the guard's OWN logic.  THE FLOOR THEN LEAKS ONTO THE
# MASS-FLOW ROW: `diskFlow`'s stationarity would be graded against a threshold
# that is not derived, not registered and not approved.
mLeak = mutant([("    if quantity not in FLOORED_QUANTITIES:\n",
                 "    if False and quantity not in FLOORED_QUANTITIES:\n")],
               "floor_leak")
leaked = None
try:
    leaked = mLeak.stationarity_criterion(1.0e-05, 2.1887e-02, "disk mass flow")
except SystemExit:
    pass
check("MUTATION: with the guard reverted THE FLOOR LEAKS ONTO THE MASS-FLOW "
      "ROW", leaked is not None
      and leaked["floor_limb_N"] == cand.STATIONARITY_FLOOR_SECTOR_N,
      "a mass flow of %.6g kg/s would be graded against a THRUST floor of "
      "%.6e N -- an unregistered gate on a second row, in the wrong units"
      % (2.1887e-02, (leaked or {}).get("floor_limb_N", float("nan"))))
check("the criterion has exactly ONE call site, and it grades thrust",
      src.count("stationarity_criterion(") == 2
      and 'stationarity_criterion(ptp, mean, "thrust")' in src,
      "%d occurrences: the definition and one call"
      % src.count("stationarity_criterion("))
check("no floor constant appears anywhere in the C2 mass-flow block",
      "STATIONARITY_FLOOR" not in
      src.split("# C2 -- disk mass flow")[1].split("# C3 --")[0])

print("=== LIMB GROUP 10 -- END-TO-END PLUMBING OF control_6_2 / control_6_3 ===")
# >>> THE VERDICTS BELOW ARE NOT RESULTS AND MUST NEVER BE CITED AS ONE.  The
# >>> function-object series in this fixture are FABRICATED, no solver ran, and
# >>> the fixture exists to prove that the repaired call graph EXECUTES -- that
# >>> every new argument (`filename`, `end_time`, `age_ref`) is threaded to
# >>> every call site and no path raises TypeError or NameError.  A repair whose
# >>> pieces each pass in isolation and whose wiring is untested is half-checked.


def finish_case(fx, tdir, end_time=END_TIME):
    """Give a fixture the things `completion()` requires."""
    with open(os.path.join(fx, "log.simpleFoam"), "w") as fh:
        for i in range(int(end_time)):
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
# Its `forcesDuct` series is LONGER THAN THE REGISTERED 2000-ROW WINDOW,
# because section 6.3 now grades Addendum 3's stationarity channel on it.
LONG_END = 2100.0
EMPTY_CASE = finish_case(*build_fixture(end_time=LONG_END,
                                        n_force_rows=int(LONG_END))[::2],
                         end_time=LONG_END)
fv_e = os.path.join(EMPTY_CASE, "constant", "fvOptions")
_loaded = open(fv_e).read()          # read BEFORE opening for write: "w" truncates
assert "((166666.66666666666 0 0) 0)" in _loaded, "fixture fvOptions unexpected"
open(fv_e, "w").write(_loaded.replace("((166666.66666666666 0 0) 0)",
                                      "((0 0 0) 0)"))
os.utime(fv_e, (T_NEW, T_NEW))
# Drag: T_duct must be negative, so total_x must be POSITIVE before the flip.
# A CONSTANT series, so `ptp` is exactly zero and the fabricated fixture passes
# stationarity: what limb group 10 tests is that the wiring EXECUTES, and a
# fixture that failed the criterion would not distinguish "wired" from "broken".
write_series(os.path.join(EMPTY_CASE, "postProcessing", "forcesDuct", "0",
                          "force.dat"), FORCE_HEADER % "Force",
             [(int(LONG_END) - int(LONG_END) + 1 + i, nine(4.0e-03))
              for i in range(int(LONG_END))])

ok_old, msg_old = refuses(old.read_fvoptions_source, EMPTY_CASE)
check("MUTATION (the superseded reader): REFUSES the registered zero source, "
      "so section 6.3 could never pass", ok_old, msg_old[:130])
src_fv = cand.read_fvoptions_source(EMPTY_CASE, zero_source_expected=True)
check("candidate accepts a zero source ONLY where one is registered",
      src_fv["Su"][0] == 0.0)
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

try:
    v_b = cand.control_6_3(EMPTY_CASE, 42.7256601, LONG_END, 0)
    ran_b, why_b = True, ""
except SystemExit as e:
    v_b, ran_b, why_b = None, False, "SystemExit(%r)" % (e.code,)
except Exception as e:                                          # noqa: BLE001
    v_b, ran_b, why_b = None, False, "%s: %s" % (type(e).__name__, e)
check("control_6_3 runs end to end WITH the stationarity channel wired",
      ran_b, why_b)
if ran_b:
    check("both plants on `forcesDuct` fired -- the last row AND the window",
          v_b["planted_control"]["fired"]
          and v_b["planted_control_stationarity"]["fired"]
          and v_b["planted_control_stationarity"]["artifact_byte_identical"],
          "window plant into %s, %.6g N"
          % (v_b["planted_control_stationarity"]["row"],
             v_b["planted_control_stationarity"]["plant_N"]))
    check("the sector-frame proof is part of the record and is BIT-EXACT",
          v_b["sector_frame_proof"]["bit_exact"]
          and v_b["sector_frame_proof"]["implied_T_total_N"]
          == v_b["T_total_N"])
    check("the floor derivation is carried into the graded record",
          v_b["floor_derivation"]["T_floor,sector"]["derived"]
          == cand.STATIONARITY_FLOOR_SECTOR_N)
    check("magnitude, SIGN and stationarity are ALL three evaluated",
          set(("magnitude_pass", "sign_pass_must_be_drag",
               "stationarity_pass")) <= set(v_b))
    print("       [NOT A RESULT -- fabricated fixture, no solver ran] "
          "structural verdict field = %r" % v_b["verdict"])

# THE SIGN GATE STILL BINDS, AND IT BINDS AHEAD OF STATIONARITY.  A positive
# T_total on a delta_p = 0 duct is NOT A RESULT regardless of magnitude
# (Addendum 3 section 6: "untouched"), and a PERFECTLY stationary series must
# not buy its way past that.  The series below is constant -- ptp exactly 0, so
# stationarity passes outright -- and negative, so T_total comes out positive.
write_series(os.path.join(EMPTY_CASE, "postProcessing", "forcesDuct", "0",
                          "force.dat"), FORCE_HEADER % "Force",
             [(1 + i, nine(-4.0e-03)) for i in range(int(LONG_END))])
ok, msg = refuses(cand.control_6_3, EMPTY_CASE, 42.7256601, LONG_END, 0)
check("a PERFECTLY stationary but THRUST-POSITIVE V(b) is still refused on "
      "SIGN", ok and "NET THRUST FROM NOTHING" in msg, msg.split(".")[0][:100])

# AN UNSTATIONARY V(b) IS `NOT A RESULT`, AND IT IS NOT A REFUSAL.  This is the
# behavioural half of striking the standing refusal: a REGISTERED CRITERION
# with a threshold reports its failure through the verdict field, and the
# comparator keeps its exit-2 refusals for instrument failures.  Section 9.2
# then consumes that `NOT A RESULT` and no gated solve is launched -- the same
# outcome the refusal produced, reached the way the registration registers it.
# The oscillation is sized so MAGNITUDE and SIGN both still pass: `ptp` of
# 2.0e-03 N is 3.4x over the floor, while |T_total| stays at 0.84 % of the
# loaded reference, well inside section 6.3's 2 %.  A fixture that failed two
# gates at once would not show which limb carried the verdict.
_noisy = [(1 + i, nine(4.0e-03 + (2.0e-03 if i % 2 else 0.0)))
          for i in range(int(LONG_END))]
write_series(os.path.join(EMPTY_CASE, "postProcessing", "forcesDuct", "0",
                          "force.dat"), FORCE_HEADER % "Force", _noisy)
try:
    v_ns = cand.control_6_3(EMPTY_CASE, 42.7256601, LONG_END, 0)
    ran_ns, why_ns = True, ""
except SystemExit as e:
    v_ns, ran_ns, why_ns = None, False, "SystemExit(%r)" % (e.code,)
check("an UNSTATIONARY V(b) returns `NOT A RESULT` and does NOT refuse",
      ran_ns and v_ns["stationarity_pass"] is False
      and v_ns["verdict"] == "NOT A RESULT"
      and v_ns["magnitude_pass"] and v_ns["sign_pass_must_be_drag"],
      "ptp %.6g N against a limit of %.6e N (governing %s): magnitude and sign "
      "both PASS and the verdict is still %r, carried by the stationarity limb "
      "alone"
      % ((v_ns or {}).get("thrust_stationarity", {}).get("ptp_N", float("nan")),
         (v_ns or {}).get("thrust_stationarity", {}).get("limit_N",
                                                         float("nan")),
         (v_ns or {}).get("thrust_stationarity", {}).get("governing_limb", "?"),
         (v_ns or {}).get("verdict", why_ns)))
write_series(os.path.join(EMPTY_CASE, "postProcessing", "forcesDuct", "0",
                          "force.dat"), FORCE_HEADER % "Force",
             [(1 + i, nine(4.0e-03)) for i in range(int(LONG_END))])

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 11 -- THE WINDOW READER AND ITS PLANTED CONTROL ===")
st = cand.thrust_stationarity(EMPTY_CASE, LONG_END, os.path.join(EMPTY_CASE,
                                                                 "0", "U"))
check("the window reader takes the registered %d rows, not the whole series"
      % cand.STATIONARITY_WINDOW_ITERS,
      st["n_samples"] == cand.STATIONARITY_WINDOW_ITERS
      and st["window_last_Time"] == LONG_END,
      "%d of %d rows on disk, Time %g..%g"
      % (st["n_samples"], int(LONG_END), st["window_first_Time"],
         st["window_last_Time"]))
pw = cand.plant_into_stationarity_window(EMPTY_CASE, LONG_END,
                                         os.path.join(EMPTY_CASE, "0", "U"))
check("plant fires on the stationarity window",
      pw["fired"] and pw["unperturbed_twin_silent"],
      "row %d (%s), plant %.6g N, mean shift %.6g N observed vs %.6g expected"
      % (pw["row_index_in_file"], pw["row"], pw["plant_N"],
         pw["mean_shift_observed_N"], pw["mean_shift_expected_N"]))
check("force.dat is BYTE-IDENTICAL after the window control",
      pw["artifact_byte_identical"], "sha256 %s" % pw["artifact"]["sha256"][:16])

# MUTATION A -- a window reader that silently grades ONLY THE FINAL ROW.  This
# is the defect the LAST-ROW plant cannot see, and it is why this control
# exists: `plant_into_function_object` passes on such a reader.
LASTROW_ONLY = [("    return vals[-window:], times[-window], times[-1], path",
                 "    return [vals[-1]] * window, times[-window], "
                 "times[-1], path")]
mJ = mutant(LASTROW_ONLY, "window_lastrow_only")
ok, msg = refuses(mJ.plant_into_stationarity_window, EMPTY_CASE, LONG_END,
                  os.path.join(EMPTY_CASE, "0", "U"))
check("MUTATION: a reader that grades only the FINAL ROW is REFUSED", ok,
      msg[:100])
check("...and it is the WINDOW plant's refusal that caught it",
      "PLANTED CONTROL ON THE STATIONARITY WINDOW" in msg, msg[:90])
r_lastrow = mJ.plant_into_function_object(EMPTY_CASE, "forcesDuct", "total_x",
                                          LONG_END, os.path.join(EMPTY_CASE,
                                                                 "0", "U"))
check("...and the pre-existing LAST-ROW plant passes that same broken reader, "
      "which is exactly why a second control was needed", r_lastrow["fired"])

# MUTATION B -- revert the window control's OWN refusals on top of the same
# broken reader.  The blind reader must now sail through.
mK = mutant(LASTROW_ONLY + [
    ("        if d_ptp <= 0.0:\n", "        if False and d_ptp <= 0.0:\n"),
    ("        if abs(d_mean - delta / window) > tol:\n",
     "        if False and abs(d_mean - delta / window) > tol:\n")],
    "window_no_refusal")
ok, msg = refuses(mK.plant_into_stationarity_window, EMPTY_CASE, LONG_END,
                  os.path.join(EMPTY_CASE, "0", "U"))
check("MUTATION: with the window control's refusals reverted the blind reader "
      "PASSES", not ok, msg[:90])

# MUTATION C -- a reader that averages the WRONG 2000 rows: `ptp` still moves,
# so only the mean identity can catch it.  This is the half of the control that
# a fire-only test would never exercise.
mL = mutant([("    return vals[-window:], times[-window], times[-1], path",
              "    return vals[-window:] + vals[:1], times[-window], "
              "times[-1], path")], "window_wrong_rows")
ok, msg = refuses(mL.plant_into_stationarity_window, EMPTY_CASE, LONG_END,
                  os.path.join(EMPTY_CASE, "0", "U"))
check("MUTATION: a reader averaging the WRONG rows is caught by the MEAN "
      "identity", ok and "AVERAGED THE WRONG ROWS" in msg, msg[:100])

# THE SHORT WINDOW.  `read_ptp_f28.py:61` refuses one; so must this.
SHORT_CASE = finish_case(*build_fixture()[::2])
ok, msg = refuses(cand.thrust_stationarity, SHORT_CASE, END_TIME,
                  os.path.join(SHORT_CASE, "0", "U"))
check("a series SHORTER than the registered window is REFUSED", ok,
      "3 rows against a registered window of %d"
      % cand.STATIONARITY_WINDOW_ITERS)
mM = mutant([("    if len(vals) < window:\n",
              "    if False and len(vals) < window:\n")], "short_window")
ok, msg = refuses(mM.thrust_stationarity, SHORT_CASE, END_TIME,
                  os.path.join(SHORT_CASE, "0", "U"))
check("MUTATION: with that refusal reverted a 3-row window is GRADED", not ok,
      "a 3-sample `ptp` graded against a 2000-sample criterion")

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 12 -- THE SECTOR FRAME IS PROVED, NOT ASSERTED ===")
AGE_E = os.path.join(EMPTY_CASE, "0", "U")
st = cand.thrust_stationarity(EMPTY_CASE, LONG_END, AGE_E)
t_e = cand.total_thrust(EMPTY_CASE, LONG_END, AGE_E)["T_duct"]
fr = cand.assert_stationarity_frame(st, t_e)
check("the frame proof holds against THE ACTUAL GRADED COLUMN, bit-exactly",
      fr["implied_T_total_N"] == t_e,
      "last windowed total_x = %.10g (sector N) -> x(-72) -> T_total = %.10g N, "
      "which is the graded value to the bit" % (st["last_value_sector_N"], t_e))
# MUTATION -- WEDGE_SCALE applied inside the window reader, i.e. the series
# handed to the criterion in FULL-ANNULUS newtons.  A 72x frame slip.
mN = mutant([("            vals.append(float(f[cols.index(column)]))",
              "            vals.append(float(f[cols.index(column)]) "
              "* WEDGE_SCALE)")], "frame_slip_reader")
st_bad = mN.thrust_stationarity(EMPTY_CASE, LONG_END, AGE_E)
ok, msg = refuses(mN.assert_stationarity_frame, st_bad, t_e)
check("MUTATION: a series scaled to the FULL ANNULUS is REFUSED by the frame "
      "proof", ok and "SECTOR-FRAME PROOF FAILED" in msg, msg[:100])
mO = mutant([("            vals.append(float(f[cols.index(column)]))",
              "            vals.append(float(f[cols.index(column)]) "
              "* WEDGE_SCALE)"),
             ("    if implied != t_total_N:\n",
              "    if False and implied != t_total_N:\n")], "frame_no_proof")
ok, msg = refuses(mO.assert_stationarity_frame,
                  mO.thrust_stationarity(EMPTY_CASE, LONG_END, AGE_E), t_e)
check("MUTATION: with the proof reverted the 72x-wrong series is ACCEPTED",
      not ok, msg[:90])

# ---------------------------------------------------------------------------
print("=== LIMB GROUP 13 -- THE ACCEPTANCE TEST: REPRODUCE THE "
      "REGISTRATION'S OWN TABLE ===")
# Addendum 3 section 7 (PREREGISTRATION.md:1757-1761) and Addendum 4 section 1
# (:1853-1857) publish the three feasibility arms read against the floored
# criterion.  THE WIRED CODE IS DRIVEN ON THOSE ARMS' OWN `force.dat` FILES and
# must reproduce which limb governs, the ratios to the printed digits, and all
# three readings -- WITHOUT ANY NUMBER BEING TUNED TO THE TABLE.  A disagreement
# here is a finding about the registration or the code, never a licence to
# adjust either.  These are FEASIBILITY rows carrying no verdict of the fixed
# vocabulary; "FAIL"/"PASS" below are readings of a criterion, exactly as
# Addendum 3 section 7 says of its own table.
REGISTERED = [
    # arm, ptp (s.7), |T_mean| (Add.4 s.1), rel limb, floor/rel (Add.4),
    # ptp/floor margin (s.7)
    ("FEAS_L1_dp0_U20_A2",            0.020421899, 0.003308274,
     3.308274e-06, 179.372, 34.4),
    ("FEAS_L1_dp1000_U20_A2",         0.060453719, 0.333724642,
     3.337246e-04, 1.778, 101.9),
    ("FEAS_L1_dp1000_U20_A2_BCPROBE", 0.063349822, 0.313215680,
     3.132157e-04, 1.895, 106.8),
]
print("  %-30s %14s %14s %13s %8s %9s %8s %6s"
      % ("arm", "ptp (N)", "|T_mean| (N)", "rel limb (N)", "govern",
         "floor/rel", "ptp/flr", "read"))
rp_spec = importlib.util.spec_from_file_location(
    "read_ptp_f28_ref", os.path.join(HERE, "read_ptp_f28.py"))
rp = importlib.util.module_from_spec(rp_spec)
rp_spec.loader.exec_module(rp)
for arm, r_ptp, r_absmean, r_rel, r_ratio, r_margin in REGISTERED:
    fxa, agea = real_arm_fixture(arm)
    if fxa is None:
        check("acceptance arm %s is on disk" % arm, False,
              "force.dat absent -- the acceptance test cannot be driven")
        continue
    s = cand.thrust_stationarity(fxa, 15000.0, agea)
    print("  %-30s %14.9f %14.9f %13.6e %8s %9.3f %8.1f %6s"
          % (arm, s["ptp_N"], abs(s["T_mean_N"]), s["relative_limb_N"],
             s["governing_limb"], s["floor_over_relative"],
             s["ptp_N"] / s["floor_limb_N"], "PASS" if s["pass"] else "FAIL"))
    check("  %s: ptp reproduces the registered %.9f N" % (arm, r_ptp),
          abs(s["ptp_N"] - r_ptp) <= 5e-10,
          "read %.9f N from the arm's own force.dat" % s["ptp_N"])
    check("  %s: |T_mean| reproduces the registered %.9f N" % (arm, r_absmean),
          abs(abs(s["T_mean_N"]) - r_absmean) <= 5e-10,
          "read %.9f N" % abs(s["T_mean_N"]))
    check("  %s: relative limb reproduces the registered %.6e N"
          % (arm, r_rel), abs(s["relative_limb_N"] - r_rel) <= 5e-11)
    check("  %s: the FLOOR governs, as Addendum 4 registers" % arm,
          s["governing_limb"] == "FLOOR")
    check("  %s: floor/relative reproduces the registered %.3fx"
          % (arm, r_ratio), abs(s["floor_over_relative"] - r_ratio) <= 5e-4,
          "%.6f" % s["floor_over_relative"])
    check("  %s: the ptp/floor margin reproduces Addendum 3 s.7's %.1fx"
          % (arm, r_margin),
          abs(s["ptp_N"] / s["floor_limb_N"] - r_margin) <= 5e-2,
          "%.4f" % (s["ptp_N"] / s["floor_limb_N"]))
    check("  %s: FAILS the floored criterion, as registered" % arm,
          not s["pass"])
    # THE `max` JOIN IS ONE-WAY, and Addendum 3 section 6 says so plainly: the
    # floor moves the criterion in the PERMISSIVE direction.  Addendum 4 then
    # struck section 3's claim that the change is "inert on the loaded arms" --
    # it relaxes them by 1.778x and 1.895x.  So the floored limit must be >=
    # the struck relative-only limit on EVERY arm, never below it.
    check("  %s: the floored limit is >= the struck relative-only limit "
          "(the `max` join is permissive, per Addendum 3 s.6 / Addendum 4)"
          % arm, s["limit_N"] >= s["relative_limb_N"],
          "limit %.6e N vs relative-only %.6e N -- %s by %.3fx"
          % (s["limit_N"], s["relative_limb_N"],
             "relaxed" if s["limit_N"] > s["relative_limb_N"] else "unchanged",
             s["limit_N"] / s["relative_limb_N"]))
    check("  %s: the window spans %d iterations, so rows and iterations "
          "coincide here" % (arm, cand.STATIONARITY_WINDOW_ITERS),
          s["window_Time_span"] == float(cand.STATIONARITY_WINDOW_ITERS),
          "Time %g..%g" % (s["window_first_Time"], s["window_last_Time"]))
    # `ptp` and `T_mean` ARE `read_ptp_f28.py`'s, not a re-derivation: the
    # frozen reader is run on the same file and the doubles must be IDENTICAL.
    lo, hi, mean, _pct, _t0, _t1 = rp.ptp_percent(rp.read_total_x(fxa))
    check("  %s: ptp and T_mean are BIT-IDENTICAL to read_ptp_f28.py's" % arm,
          s["T_mean_N"] == mean and s["ptp_N"] == hi - lo
          and s["min_N"] == lo and s["max_N"] == hi,
          "mean %.17g, ptp %.17g -- same doubles, not merely equal to the "
          "printed digits" % (mean, hi - lo))

# THE 72x ERROR, MADE VISIBLE AS A VERDICT FLIP RATHER THAN AS AN ARGUMENT.
fx0, age0 = real_arm_fixture("FEAS_L1_dp0_U20_A2")
if fx0 is not None:
    s0 = cand.thrust_stationarity(fx0, 15000.0, age0)
    would_pass_full = s0["ptp_N"] <= max(s0["relative_limb_N"],
                                         cand.STATIONARITY_FLOOR_FULL_N)
    check("the FULL-ANNULUS floor would have RESCUED the zero-source arm, and "
          "the SECTOR floor does not",
          would_pass_full and not s0["pass"],
          "ptp %.9f N: against the sector floor %.6e N it FAILS by %.1fx; "
          "against the full-annulus floor %.6e N it would PASS.  That flip is "
          "the whole content of Addendum 3 section 5, and it is why the frame "
          "is proved by identity in limb group 12 rather than read off a "
          "comment." % (s0["ptp_N"], cand.STATIONARITY_FLOOR_SECTOR_N,
                        s0["ptp_N"] / cand.STATIONARITY_FLOOR_SECTOR_N,
                        cand.STATIONARITY_FLOOR_FULL_N))
print("       [FEASIBILITY -- no verdict of the fixed vocabulary attaches to "
      "any row above; 'FAIL' is a reading of a criterion, per Addendum 3 s.7]")

print()
for d in _tmpdirs:
    shutil.rmtree(d, ignore_errors=True)
if fails:
    print("SELFTEST FAILED -- %d limb(s): %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("SELFTEST PASSED -- every limb held, and every mutation limb went red.")
sys.exit(0)
