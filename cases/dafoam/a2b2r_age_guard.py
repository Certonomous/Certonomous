#!/usr/bin/env python3
"""A2-B2R age guard and staged-file manifest.

Frozen with cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md.

WHY THIS FILE EXISTS, AND WHY IT IS NOT CLAUDE.md RULE 4's AGE GUARD VERBATIM
----------------------------------------------------------------------------
Rule 4's age guard dates a run from the case's own `0/T`, on the premise that
`0/T` is touched last at launch.  THAT PREMISE IS FALSE FOR THIS CASE, and the
falsity is measured, not argued:

  * `0/` DOES NOT EXIST in the pristine MACH_Tutorial_Wing tree at all.  It is
    created INSIDE the container by `preProcessing.sh` (`cp -r 0.orig 0`), i.e.
    AFTER the launch datum.  A pre-launch manifest cannot pin a file that does
    not yet exist.
  * The decomposed copy is rewritten DURING the run.  In the A2 run
    (/home/ubuntu/certonomous-runs/ACTD-a2-decomposition) `processor0/0/U.gz`
    carries mtime 01:09:35 -- the run's END -- while its five siblings carry
    01:06:35, the decomposePar time.  The rewrite happens under `processor*/0/`,
    not only at case level, and it lands on a `.gz` name because
    `system/controlDict` sets `writeCompression on`.
  * A FILE COUNT IS NOT AN IDENTITY.  D19's count clause passed with 9 files
    before and 9 after while six of the nine NAMES had changed (`T` -> `T.gz`).
    Nothing below ever compares a count.  Every decision here is per NAME with a
    CONTENT HASH beside it.

So the datum is `t0`, written by the launcher after every stage copy and before
`docker run`, and the pinned manifest is the set of staged files that the run
must NOT rewrite.  The write-target exclusion is DERIVED from the same
enumeration the pinning loop consumes -- `partition()` returns both halves from
one pass -- so a record can never assert an exclusion the code does not enforce.

MEASURED BASIS FOR THE PREDICATE (A2 run, identical protocol, zero new compute):
of the 23 staged pristine files, EXACTLY ONE changed during the run --
`system/decomposeParDict`, which DAFoam rewrites with its own
`numberOfSubdomains`.  The other 22 were byte-identical afterwards and all kept
mtime < t0.  147 new files were created, all of them under the excluded heads.

REFUSAL TOKENS -- every refusal is exit 2 AND a named token on stdout, so that an
unrelated crash (which also exits non-zero) can never be read as an expected
refusal:
    REFUSE_CENSUS_NOT_PARTITION   pinned+excluded is not a partition of the census
    REFUSE_CENSUS_BLIND           the census cannot see processor*/0/ after a run
    REFUSE_PIN_EXCLUSION_DISAGREE a pinned name also classifies as a write target
    REFUSE_MANIFEST_NAME_MISSING  a pinned name is gone (or renamed) after the run
    REFUSE_MANIFEST_HASH_MOVED    a pinned name survives with different content
    REFUSE_AGE_DATUM_MOVED        a pinned file is not older than t0
    REFUSE_ARTIFACT_NOT_NEWER     a graded artifact is not newer than t0
    REFUSE_PREDICATE_OVERMATCH    the predicate excludes a file it must pin
"""
import hashlib
import json
import os
import re
import sys
import time

# --- the single write-target predicate -------------------------------------
# Derived from the A2 run's measured file census.  It is consumed by exactly one
# function, partition(), and both the pinned set and the excluded set come out of
# that one call.  Nothing else in this file classifies a path.

_TIMEDIR = re.compile(r"\d+(\.\d+)?$")
_PROCDIR = re.compile(r"processor\d+$")

# Case-level names the run creates or rewrites.  `paraview.foam`, `runScript.py`,
# `runScript_AeroOnly.py`, `genWingMesh.py`, `tacsSetup.py`, `wingbox.bdf`,
# `Allclean.sh`, `preProcessing.sh`, `FFD/`, `0.orig/`, `constant/*.dict-like`
# and `system/*` other than decomposeParDict are NOT here: they are pinned.
_WRITTEN_HEADS = frozenset(
    {
        "postProcessing",
        "reports",
        "mphys.html",
        "OptView.hst",
        "preproc.log",
        "logMeshGeneration.txt",
        "surfaceMesh.cgns",
        "volumeMesh.xyz",
        "mdolab_wing_surface_mesh.cgns",
    }
)
# NOT here, deliberately: `mdolab_wing_surface_mesh.cgns.tar.gz`.  The launcher
# pre-stages that tarball from the A2 run (sha256 bc70f99c...), so the surface
# geometry this rung meshes from is provably the same file A2 meshed from, and
# no network fetch can silently substitute another.  `tar -xvf` only reads it,
# so it must survive byte-identical and it is PINNED.  The EXTRACTED
# `mdolab_wing_surface_mesh.cgns` above stays a write target.
# The one staged file DAFoam rewrites, measured in the A2 run.
_WRITTEN_EXACT = frozenset({"system/decomposeParDict"})


def is_write_target(rel):
    """True if `rel` (a case-relative path) is a thing this run is allowed to
    write.  Everything else is pinned and must survive byte-identical."""
    parts = rel.split("/")
    head = parts[0]
    if head in _WRITTEN_HEADS:
        return True
    if rel in _WRITTEN_EXACT:
        return True
    if _PROCDIR.fullmatch(head):        # processor0/... including processor0/0/U.gz
        return True
    if _TIMEDIR.fullmatch(head):        # 0/, 1000/, 0.5/ ... at case level
        return True
    if rel.startswith("constant/polyMesh/"):
        return True
    if head.startswith("._"):           # AppleDouble spill from the tarball
        return True
    if head.endswith(".log"):
        return True
    return False


def enumerate_case(case_dir):
    """Every regular file under case_dir, as sorted case-relative paths."""
    out = []
    for dp, _dn, fn in os.walk(case_dir):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.isfile(p) and not os.path.islink(p):
                out.append(os.path.relpath(p, case_dir))
    return sorted(out)


def partition(rels):
    """ONE pass produces BOTH halves.  The excluded list a record may quote is
    this function's second return value and nothing else -- it is impossible for
    the document to name an exclusion the pinning loop did not honour."""
    pinned, excluded = [], []
    for r in rels:
        (excluded if is_write_target(r) else pinned).append(r)
    return pinned, excluded


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _refuse(token, detail):
    print("%s %s" % (token, detail))
    sys.exit(2)


# --- pin: run POST-STAGE, PRE-LAUNCH ----------------------------------------

def cmd_pin(case_dir, manifest_out):
    rels = enumerate_case(case_dir)
    pinned, excluded = partition(rels)
    if set(pinned) & set(excluded) or set(pinned) | set(excluded) != set(rels):
        _refuse("REFUSE_CENSUS_NOT_PARTITION", "pin census is not a partition")
    # A predicate that excluded everything would make the guard vacuous.  These
    # three staged files MUST land on the pinned side or the guard is not
    # measuring anything.  This is the guard's own planted control.
    for must_pin in ("system/fvSchemes", "0.orig/U", "constant/thermophysicalProperties"):
        if must_pin in rels and is_write_target(must_pin):
            _refuse("REFUSE_PREDICATE_OVERMATCH", must_pin)
    man = {
        "case_dir": os.path.abspath(case_dir),
        "pinned": {r: {"sha256": _sha256(os.path.join(case_dir, r)),
                       "mtime": os.path.getmtime(os.path.join(case_dir, r))}
                   for r in pinned},
        "excluded_write_targets": excluded,
        "pinned_at": time.time(),
    }
    with open(manifest_out, "w") as fh:
        json.dump(man, fh, indent=2, sort_keys=True)
    print("PIN_OK pinned=%d excluded=%d manifest=%s"
          % (len(pinned), len(excluded), manifest_out))
    return 0


# --- verify: run POST-RUN ----------------------------------------------------

def cmd_verify(case_dir, manifest_path, t0_path, artifacts, require_processor_zero=True):
    man = json.load(open(manifest_path))
    t0 = os.path.getmtime(t0_path)

    # (1) the exclusion is ENFORCING, not descriptive: re-classify every pinned
    #     name with the SAME predicate the pinning loop used.  A record that
    #     pinned `0/U` while claiming `0` was excluded dies here.
    still_pinned, wrongly_pinned = partition(sorted(man["pinned"]))
    if wrongly_pinned:
        _refuse("REFUSE_PIN_EXCLUSION_DISAGREE", ",".join(sorted(wrongly_pinned)[:8]))

    # (2) per NAME, then per CONTENT HASH.  No count is compared anywhere.
    for rel, rec in sorted(man["pinned"].items()):
        p = os.path.join(case_dir, rel)
        if not os.path.isfile(p):
            _refuse("REFUSE_MANIFEST_NAME_MISSING", rel)
        got = _sha256(p)
        if got != rec["sha256"]:
            _refuse("REFUSE_MANIFEST_HASH_MOVED", "%s %s->%s" % (rel, rec["sha256"][:12], got[:12]))
        if os.path.getmtime(p) >= t0:
            _refuse("REFUSE_AGE_DATUM_MOVED", "%s mtime %.3f >= t0 %.3f"
                    % (rel, os.path.getmtime(p), t0))

    # (3) the census must be able to SEE the decomposed time-0 directories --
    #     the exact site of the D19 rewrite.  A guard whose enumeration cannot
    #     reach processor*/0/ would pass by blindness.
    rels = enumerate_case(case_dir)
    proc_zero = [r for r in rels if re.match(r"processor\d+/0/", r)]
    if require_processor_zero and not proc_zero:
        _refuse("REFUSE_CENSUS_BLIND", "no processor*/0/ files found under " + case_dir)

    # (4) every graded artifact is strictly newer than the datum.
    for a in artifacts:
        if not os.path.isfile(a):
            _refuse("REFUSE_ARTIFACT_NOT_NEWER", a + " missing")
        if os.path.getmtime(a) <= t0:
            _refuse("REFUSE_ARTIFACT_NOT_NEWER", "%s mtime %.3f <= t0 %.3f"
                    % (a, os.path.getmtime(a), t0))

    rewritten = sorted(r for r in proc_zero
                       if os.path.getmtime(os.path.join(case_dir, r)) > t0 + 30)
    print("AGE_GUARD_OK pinned_names_verified=%d processor_zero_seen=%d "
          "processor_zero_rewritten_late=%d artifacts=%d"
          % (len(man["pinned"]), len(proc_zero), len(rewritten), len(artifacts)))
    if rewritten:
        print("AGE_GUARD_NOTE the run DID rewrite decomposed time-0 files: "
              + ",".join(rewritten[:6]))
    return 0


# --- selftest: every leg is DRIVEN, not asserted in prose --------------------

def _leg(name, fn, expect_token):
    import io
    import contextlib
    buf = io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(buf):
            fn()
        code = 0
    except SystemExit as e:
        code = e.code
    out = buf.getvalue()
    if expect_token is None:
        ok = (code == 0) and "REFUSE" not in out
        why = "expected clean exit"
    else:
        # BY NAME.  A bare non-zero exit would accept an unrelated crash.
        ok = (code == 2) and (expect_token in out)
        why = "expected exit 2 AND token %s" % expect_token
    print("  %-34s %-30s %s" % (name, expect_token or "(clean)", "PASS" if ok else "FAIL"))
    if not ok:
        print("     %s; got code=%r out=%r" % (why, code, out.strip()[:200]))
    return ok


def cmd_selftest():
    import shutil
    import tempfile
    ok = True
    print("A2-B2R AGE GUARD SELFTEST")

    print("\n[predicate] classification of paths that actually occur on disk")
    must_exclude = ["0/T", "0/U", "0/T.gz", "processor0/0/T.gz", "processor3/0/U.gz",
                    "processor1/1000/p.gz", "1000/U", "constant/polyMesh/points.gz",
                    "constant/polyMesh/points", "processor0/constant/polyMesh/faces.gz",
                    "system/decomposeParDict", "postProcessing/x.dat", "preproc.log",
                    "mphys.html", "reports/r.html", "._mdolab_wing_surface_mesh.cgns"]
    must_pin = ["system/fvSchemes", "system/controlDict", "system/fvSolution",
                "0.orig/U", "0.orig/T", "constant/thermophysicalProperties",
                "FFD/wingFFD.xyz", "runScript_AeroOnly.py", "a2_decomposition_driver.py",
                "a2b2r_rows.json", "preProcessing.sh", "paraview.foam", "wingbox.bdf",
                "mdolab_wing_surface_mesh.cgns.tar.gz"]
    for r in must_exclude:
        good = is_write_target(r)
        print("  EXCLUDE %-46s %s" % (r, "PASS" if good else "FAIL"))
        ok &= good
    for r in must_pin:
        good = not is_write_target(r)
        print("  PIN     %-46s %s" % (r, "PASS" if good else "FAIL"))
        ok &= good

    tmp = tempfile.mkdtemp(prefix="a2b2r_guard_selftest_")
    try:
        case = os.path.join(tmp, "case")
        for d in ("system", "0.orig", "constant", "FFD"):
            os.makedirs(os.path.join(case, d))
        for rel, body in (("system/fvSchemes", "schemes"),
                          ("system/controlDict", "control"),
                          ("system/decomposeParDict", "n 4"),
                          ("0.orig/U", "U0"),
                          ("0.orig/T", "T0"),
                          ("constant/thermophysicalProperties", "thermo"),
                          ("FFD/wingFFD.xyz", "ffd"),
                          ("a2_decomposition_driver.py", "driver")):
            open(os.path.join(case, rel), "w").write(body)
        man = os.path.join(tmp, "manifest.json")
        t0 = os.path.join(tmp, "t0")

        print("\n[pin] pre-launch")
        ok &= _leg("pin on a clean staged tree", lambda: cmd_pin(case, man), None)
        m = json.load(open(man))
        good = (set(m["excluded_write_targets"]) == {"system/decomposeParDict"}
                and "system/decomposeParDict" not in m["pinned"]
                and len(m["pinned"]) == 7)
        print("  %-34s %-30s %s" % ("exclusion derived from the census",
                                    "decomposeParDict only", "PASS" if good else "FAIL"))
        ok &= good

        # the run: create the write targets, leave the pinned files alone
        time.sleep(1.1)
        open(t0, "w").write("t0")
        time.sleep(0.05)
        for d in ("0", "processor0/0", "processor0/1000"):
            os.makedirs(os.path.join(case, d), exist_ok=True)
        for rel in ("0/T", "0/U", "processor0/0/T.gz", "processor0/0/U.gz",
                    "processor0/1000/U.gz"):
            open(os.path.join(case, rel), "w").write("field")
        open(os.path.join(case, "system/decomposeParDict"), "w").write("n 4 rewritten")
        log = os.path.join(tmp, "run.log")
        open(log, "w").write("DECOMP_ALL_ROWS_DONE")

        print("\n[verify] GREEN leg and the RED legs, each refusal demanded BY NAME")
        ok &= _leg("clean run", lambda: cmd_verify(case, man, t0, [log]), None)

        # RED 1: a pinned name that is really a write target
        bad = os.path.join(tmp, "m_disagree.json")
        m2 = json.load(open(man))
        m2["pinned"]["0/U"] = {"sha256": "0" * 64, "mtime": 0.0}
        json.dump(m2, open(bad, "w"))
        ok &= _leg("pinned name is a write target",
                   lambda: cmd_verify(case, bad, t0, [log]), "REFUSE_PIN_EXCLUSION_DISAGREE")

        # RED 2: a RENAME that holds the file COUNT constant (the D19 trap)
        n_before = len(enumerate_case(case))
        os.rename(os.path.join(case, "system/fvSchemes"),
                  os.path.join(case, "system/fvSchemes.gz"))
        n_after = len(enumerate_case(case))
        print("  count before %d, count after %d -- IDENTICAL, and the guard must "
              "still refuse" % (n_before, n_after))
        ok &= (n_before == n_after)
        ok &= _leg("rename at constant file count",
                   lambda: cmd_verify(case, man, t0, [log]), "REFUSE_MANIFEST_NAME_MISSING")
        os.rename(os.path.join(case, "system/fvSchemes.gz"),
                  os.path.join(case, "system/fvSchemes"))

        # RED 3: same name, different content
        keep = open(os.path.join(case, "system/controlDict")).read()
        open(os.path.join(case, "system/controlDict"), "w").write("control MUTATED")
        ok &= _leg("pinned content mutated",
                   lambda: cmd_verify(case, man, t0, [log]), "REFUSE_MANIFEST_HASH_MOVED")
        open(os.path.join(case, "system/controlDict"), "w").write(keep)
        os.utime(os.path.join(case, "system/controlDict"),
                 (m["pinned"]["system/controlDict"]["mtime"],
                  m["pinned"]["system/controlDict"]["mtime"]))

        # RED 4: the age datum moved
        os.utime(os.path.join(case, "system/fvSchemes"), (time.time(), time.time()))
        ok &= _leg("pinned file newer than t0",
                   lambda: cmd_verify(case, man, t0, [log]), "REFUSE_AGE_DATUM_MOVED")
        os.utime(os.path.join(case, "system/fvSchemes"),
                 (m["pinned"]["system/fvSchemes"]["mtime"],
                  m["pinned"]["system/fvSchemes"]["mtime"]))

        # RED 5: artifact older than the datum
        old = os.path.join(tmp, "stale.log")
        open(old, "w").write("stale")
        os.utime(old, (os.path.getmtime(t0) - 10, os.path.getmtime(t0) - 10))
        ok &= _leg("graded artifact older than t0",
                   lambda: cmd_verify(case, man, t0, [old]), "REFUSE_ARTIFACT_NOT_NEWER")

        # RED 6: the census is blind to processor*/0/
        blind = os.path.join(tmp, "blind")
        shutil.copytree(case, blind)
        shutil.rmtree(os.path.join(blind, "processor0"))
        ok &= _leg("census cannot see processor*/0/",
                   lambda: cmd_verify(blind, man, t0, [log]), "REFUSE_CENSUS_BLIND")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "pin" and len(argv) == 4:
        return cmd_pin(argv[2], argv[3])
    if len(argv) >= 5 and argv[1] == "verify":
        return cmd_verify(argv[2], argv[3], argv[4], argv[5:])
    if len(argv) == 2 and argv[1] == "selftest":
        return cmd_selftest()
    if len(argv) >= 3 and argv[1] == "census":
        rels = enumerate_case(argv[2])
        pinned, excluded = partition(rels)
        print("CENSUS files=%d pinned=%d excluded=%d" % (len(rels), len(pinned), len(excluded)))
        print("  processor*/0/ files seen: %d"
              % len([r for r in rels if re.match(r"processor\d+/0/", r)]))
        return 0
    print(__doc__)
    print("usage: a2b2r_age_guard.py pin <case_dir> <manifest.json>\n"
          "       a2b2r_age_guard.py verify <case_dir> <manifest.json> <t0> <artifact>...\n"
          "       a2b2r_age_guard.py census <case_dir>\n"
          "       a2b2r_age_guard.py selftest")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
