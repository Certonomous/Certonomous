#!/usr/bin/env python3
"""MP-A1 age guard: the SO-3aR2 datum form PLUS a manifest by NAME AND CONTENT HASH.

WHAT IS CARRIED UNCHANGED FROM SO-3aR2, AND WHY IT IS NOT REPLACED
-------------------------------------------------------------------
`CLAUDE.md` rule 4's age guard dates a run from the case's own `0/T`, on the
premise that `0/T` is touched last at launch.  **THAT PREMISE IS FALSE FOR THIS
CASE**, and SO-3aR2 already solved the DAFoam-specific half of it:

  * the datum is resolved BY EXISTENCE over both registered names (`0/U` and
    `0/U.gz`), because `system/controlDict` sets `writeCompression on` and a
    guard pinned to the plain name would refuse a run whose artefact is intact
    -- or, worse, pass by not finding anything to check;
  * the name actually used is RECORDED (`.mpa1_age_datum_ref`) rather than left
    for the grader to infer, and `is_compressed_twin` and `write_compression`
    travel with the reading;
  * the datum is stamped PER OPERATING POINT, because DAFoam rewrites `0/U`
    inside the case directory DURING a ranks = 1 run -- MEASURED by the
    dafoam-supervisor on D19, 2026-08-31T21:54Z: `S1/0/U.gz` mtime 43 s into a
    51 s run -- and the rewrite also lands under `processor*/0/`.

That form is CARRIED, not re-derived.  This module ADDS to it.

WHAT IS ADDED, AND THE MEASUREMENT THAT DEMANDS IT
---------------------------------------------------
**A COUNT IS NOT AN IDENTITY.**  D19's count clause passed with 9 files before
and 9 after while SIX OF THE NINE FILENAMES HAD CHANGED (`T` -> `T.gz`) under
`writeCompression on`.  Nothing below ever compares a count.  Every decision is
per NAME with a CONTENT HASH beside it -- the shape of
`cases/dafoam/a2b2r_age_guard.py`, which was frozen against the A2 run's own
measured census (of 23 staged pristine files EXACTLY ONE changed during the run,
`system/decomposeParDict`, which DAFoam rewrites with its own
`numberOfSubdomains`).

**THE WRITE-TARGET EXCLUSION IS ENFORCING, NOT DESCRIPTIVE.**  `partition()`
returns BOTH halves from ONE pass over ONE predicate, so the excluded list a
record may quote is that function's second return value and nothing else: it is
impossible for a document to name an exclusion the pinning loop did not honour.
`cmd_verify` then RE-CLASSIFIES every pinned name with the SAME predicate, so a
manifest that pinned `0/U` while its record claimed `0/` was excluded dies at
`REFUSE_PIN_EXCLUSION_DISAGREE`.  Leg (a3) drives exactly that disagreement red.

THE PREDICATE IS THIS CASE'S, NOT A2's, AND THE DIFFERENCE IS REGISTERED
-------------------------------------------------------------------------
A2 is `MACH_Tutorial_Wing`; this is `NACA0012_Airfoil/incompressible`.  The
differences that matter:

  * **`mp0/ mp1/ mp2/` are WRITE TARGETS IN FULL.**  Each is a complete case copy
    for one operating point (the SO-3aR repair, ported from
    `d6r_opt_runScript.py:59,120,138`), and the run owns all of it.  They carry
    their OWN datum and their OWN manifest and are pinned by their own
    invocation, not by the arm-level one -- pinning a point's whole case from the
    arm level would pin files the point's own solver is entitled to rewrite.
  * **`0.orig/` is PINNED here and is NOT a time directory.**  The `_TIMEDIR`
    predicate must not eat it: `0.orig` does not fullmatch `\\d+(\\.\\d+)?`, and
    leg (a1) drives that classification explicitly because it is one character
    away from being wrong.
  * **`opt_IPOPT.txt`, `MPA1_STALL_ABORT`, `mpa1_O.json`, `mpa1_xopt.json`,
    `mphys.html`, `OptView.hst`, `reports/` are WRITE TARGETS** -- this item runs
    an optimiser and its ancestor did not.
  * **`mpa1_xopt.json` IS A WRITE TARGET ON THE O ARM AND A PINNED INPUT ON THE
    ENDPOINT ARMS.**  It is the ONE file whose role depends on the arm, so the
    role is passed in explicitly (`--xopt-is-input`) rather than guessed from the
    directory: a predicate that guessed would classify the endpoint arms' only
    dependency as something the run may overwrite.

REFUSAL TOKENS -- exit 2 AND a named token on stdout, so an unrelated crash
(which also exits non-zero) can never be read as an expected refusal:
    REFUSE_CENSUS_NOT_PARTITION   pinned+excluded is not a partition of the census
    REFUSE_PIN_EXCLUSION_DISAGREE a pinned name also classifies as a write target
    REFUSE_MANIFEST_NAME_MISSING  a pinned name is gone (or renamed) after the run
    REFUSE_MANIFEST_HASH_MOVED    a pinned name survives with different content
    REFUSE_AGE_DATUM_MOVED        a pinned file is not older than the datum
    REFUSE_ARTIFACT_NOT_NEWER     a graded artifact is not newer than the datum
    REFUSE_PREDICATE_OVERMATCH    the predicate excludes a file it must pin
    REFUSE_DATUM_UNRESOLVED       neither registered datum name exists
"""
import hashlib
import json
import os
import re
import sys
import time

# --- the single write-target predicate -------------------------------------
# Consumed by exactly one function, partition(), and both halves come out of that
# one call.  Nothing else in this file classifies a path.

_TIMEDIR = re.compile(r"\d+(\.\d+)?$")
_PROCDIR = re.compile(r"processor\d+$")
_POINTDIR = re.compile(r"mp\d+$")

# Case-level names this run creates or rewrites.  `0.orig/`, `FFD/`, `profiles/`,
# `constant/*` other than polyMesh, `system/*` other than decomposeParDict,
# `genAirFoilMesh.py`, `preProcessing.sh` and the staged instruments are NOT
# here: they are PINNED.
_WRITTEN_HEADS = frozenset({
    "postProcessing",
    "reports",
    "mphys.html",
    "OptView.hst",
    "opt_IPOPT.txt",
    "opt_IPOPT.out",
    "MPA1_STALL_ABORT",
    "mpa1_O.json",
    "mpa1_X.json",
    "mpa1_F.json",
    "mpa1_X.jsonl",
    "mpa1_F.jsonl",
    "mpa1_cmd.sh",
    "checkMesh.log",
    "logMeshGeneration.txt",
    "volumeMesh.xyz",
    "surfaceMesh.xyz",
    "paraview.foam",
})
# The one staged file DAFoam rewrites with its own numberOfSubdomains, measured
# in the A2 run.
_WRITTEN_EXACT = frozenset({"system/decomposeParDict"})
# Written by THIS launcher after the manifest is pinned, so they must never be
# pinned by it.
_LAUNCHER_WRITES = frozenset({".mpa1_manifest.json"})

# The default role of `mpa1_xopt.json`: a WRITE TARGET (the O arm produces it).
# On an endpoint arm it is a PINNED INPUT and the caller says so.
XOPT = "mpa1_xopt.json"


def is_write_target(rel, xopt_is_input=False):
    """True if `rel` (a case-relative path) is something this run is allowed to
    write.  Everything else is pinned and must survive byte-identical."""
    parts = rel.split("/")
    head = parts[0]
    if rel == XOPT:
        return not xopt_is_input
    if head in _WRITTEN_HEADS:
        return True
    if rel in _WRITTEN_EXACT or rel in _LAUNCHER_WRITES:
        return True
    if _PROCDIR.fullmatch(head):        # processor0/... including processor0/0/U.gz
        return True
    if _POINTDIR.fullmatch(head):       # mp0/... -- a whole per-point case copy
        return True
    if _TIMEDIR.fullmatch(head):        # 0/, 1000/, 0.0001/ at case level.
        return True                     # `0.orig` does NOT fullmatch: leg (a1).
    if rel.startswith("constant/polyMesh/"):
        return True
    if head.startswith("._"):           # AppleDouble spill
        return True
    if head.startswith(".mpa1_"):        # the launcher's own datum sidecars
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


def partition(rels, xopt_is_input=False):
    """ONE pass produces BOTH halves.  The excluded list a record may quote is
    this function's second return value and nothing else."""
    pinned, excluded = [], []
    for r in rels:
        (excluded if is_write_target(r, xopt_is_input) else pinned).append(r)
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


# ---- THE DATUM, RESOLVED BY EXISTENCE.  SO-3aR2's form, carried. -------------
DATUM_NAMES = ("0/U", "0/U.gz")


def resolve_datum(case_dir, candidates=DATUM_NAMES):
    """Returns the datum record: which of the registered names exists, its mtime,
    whether it is the compressed twin, and the case's `writeCompression` setting.
    REFUSES when neither name exists -- a guard that cannot find its datum must
    not fall back to `now`, which would pass everything."""
    wc = "NOT_MEASURED"
    cd = os.path.join(case_dir, "system", "controlDict")
    if os.path.isfile(cd):
        for line in open(cd, errors="replace"):
            if "writeCompression" in line:
                wc = line.split()[-1].strip(";").strip()
                break
    for i, name in enumerate(candidates):
        p = os.path.join(case_dir, name)
        if os.path.isfile(p):
            return {"datum_reference": name, "path": p,
                    "is_compressed_twin": name.endswith(".gz"),
                    "mtime": os.path.getmtime(p), "write_compression": wc,
                    "resolved_by": "EXISTENCE"}
    _refuse("REFUSE_DATUM_UNRESOLVED",
            "none of %r exists under %s (write_compression=%s)"
            % (list(candidates), case_dir, wc))


# --- pin: run POST-STAGE, PRE-LAUNCH ----------------------------------------

def cmd_pin(case_dir, manifest_out, xopt_is_input=False):
    rels = enumerate_case(case_dir)
    pinned, excluded = partition(rels, xopt_is_input)
    if set(pinned) & set(excluded) or set(pinned) | set(excluded) != set(rels):
        _refuse("REFUSE_CENSUS_NOT_PARTITION", "pin census is not a partition")
    # A predicate that excluded everything would make the guard vacuous.  These
    # staged files MUST land on the pinned side or the guard measures nothing.
    # This is the guard's own PLANTED CONTROL and it is checked at PIN time, when
    # a wrong predicate can still be repaired before any compute.
    for must_pin in ("system/fvSchemes", "system/fvSolution", "0.orig/U",
                     "FFD/wingFFD.xyz", "mpa1_runScript.py", "mpa1_xf.py"):
        if must_pin in rels and is_write_target(must_pin, xopt_is_input):
            _refuse("REFUSE_PREDICATE_OVERMATCH", must_pin)
    datum = resolve_datum(case_dir)
    man = {
        "case_dir": os.path.abspath(case_dir),
        "datum": datum,
        "xopt_is_input": bool(xopt_is_input),
        "pinned": {r: {"sha256": _sha256(os.path.join(case_dir, r)),
                       "mtime": os.path.getmtime(os.path.join(case_dir, r))}
                   for r in pinned},
        "excluded_write_targets": excluded,
        "pinned_at": time.time(),
    }
    with open(manifest_out, "w") as fh:
        json.dump(man, fh, indent=2, sort_keys=True)
    print("PIN_OK pinned=%d excluded=%d datum_reference=%s is_compressed_twin=%s "
          "write_compression=%s xopt_is_input=%s manifest=%s"
          % (len(pinned), len(excluded), datum["datum_reference"],
             datum["is_compressed_twin"], datum["write_compression"],
             bool(xopt_is_input), manifest_out))
    return 0


# --- verify: run POST-RUN ----------------------------------------------------

def cmd_verify(case_dir, manifest_path, datum_path, artifacts):
    man = json.load(open(manifest_path))
    xin = bool(man.get("xopt_is_input"))
    if not os.path.isfile(datum_path):
        _refuse("REFUSE_DATUM_UNRESOLVED", "datum file absent at verify: " + datum_path)
    t0 = os.path.getmtime(datum_path)

    # (1) THE EXCLUSION IS ENFORCING.  Re-classify every pinned name with the
    #     SAME predicate the pinning loop used, and with the SAME role for
    #     `mpa1_xopt.json` -- read from the manifest, never re-guessed here.
    _still, wrongly_pinned = partition(sorted(man["pinned"]), xin)
    if wrongly_pinned:
        _refuse("REFUSE_PIN_EXCLUSION_DISAGREE", ",".join(sorted(wrongly_pinned)[:8]))

    # (2) per NAME, then per CONTENT HASH.  No count is compared anywhere.
    for rel, rec in sorted(man["pinned"].items()):
        p = os.path.join(case_dir, rel)
        if not os.path.isfile(p):
            _refuse("REFUSE_MANIFEST_NAME_MISSING", rel)
        got = _sha256(p)
        if got != rec["sha256"]:
            _refuse("REFUSE_MANIFEST_HASH_MOVED",
                    "%s %s->%s" % (rel, rec["sha256"][:12], got[:12]))
        if os.path.getmtime(p) > t0:
            _refuse("REFUSE_AGE_DATUM_MOVED",
                    "%s mtime %.3f > datum %.3f" % (rel, os.path.getmtime(p), t0))

    # (3) every graded artifact is strictly NEWER than the datum.
    for a in artifacts:
        if not os.path.isfile(a):
            _refuse("REFUSE_ARTIFACT_NOT_NEWER", a + " missing")
        if os.path.getmtime(a) <= t0:
            _refuse("REFUSE_ARTIFACT_NOT_NEWER",
                    "%s mtime %.3f <= datum %.3f" % (a, os.path.getmtime(a), t0))

    # (4) THE D19 REWRITE, MEASURED AND REPORTED, NEVER GATED.  A per-point `0/`
    #     rewritten during the run is the mechanism D19 dated mid-run; it is
    #     counted here so the record carries the number rather than the inference.
    rels = enumerate_case(case_dir)
    pt_zero = [r for r in rels if re.match(r"mp\d+/0/", r)]
    rewritten = sorted(r for r in pt_zero
                       if os.path.getmtime(os.path.join(case_dir, r)) > t0)
    print("AGE_GUARD_OK pinned_names_verified=%d datum_reference=%s "
          "is_compressed_twin=%s write_compression=%s point_zero_files=%d "
          "point_zero_rewritten_after_datum=%d artifacts=%d xopt_is_input=%s"
          % (len(man["pinned"]), man["datum"]["datum_reference"],
             man["datum"]["is_compressed_twin"], man["datum"]["write_compression"],
             len(pt_zero), len(rewritten), len(artifacts), xin))
    if rewritten:
        print("AGE_GUARD_NOTE the run DID rewrite per-point time-0 files (D19's "
              "mechanism, MEASURED here): " + ",".join(rewritten[:6]))
    return 0


# --- selftest ----------------------------------------------------------------

def _leg(name, fn, expect_token):
    import contextlib
    import io
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
        ok = (code == 2) and (expect_token in out)
        why = "expected exit 2 AND token %s" % expect_token
    print("  %-44s %-32s %s" % (name, expect_token or "(clean)",
                                "PASS" if ok else "FAIL"))
    if not ok:
        print("     %s; got code=%r out=%r" % (why, code, out.strip()[:220]))
    return ok


def cmd_selftest():
    import shutil
    import tempfile
    ok = True
    print("MP-A1 AGE GUARD SELFTEST")

    # ---- (a1) THE PREDICATE, on paths that actually occur in THIS case.
    print("\n[a1] classification of paths that occur in this case's own tree")
    must_exclude = ["0/U", "0/U.gz", "0/p", "0.0001/U.gz", "mp0/0/U.gz",
                    "mp2/constant/polyMesh/points.gz", "mp1/mpa1_cmd.sh",
                    "processor0/0/U.gz", "constant/polyMesh/points",
                    "system/decomposeParDict", "opt_IPOPT.txt", "mpa1_O.json",
                    "mpa1_X.json", "mpa1_F.jsonl", "MPA1_STALL_ABORT",
                    "reports/r.html", "mphys.html", "OptView.hst",
                    "checkMesh.log", ".mpa1_age_datum", ".mpa1_manifest.json"]
    must_pin = ["system/fvSchemes", "system/controlDict", "system/fvSolution",
                "0.orig/U", "0.orig/p", "0.orig/nuTilda",
                "constant/transportProperties", "FFD/wingFFD.xyz",
                "profiles/NACA0012PS.profile", "genAirFoilMesh.py",
                "preProcessing.sh", "mpa1_runScript.py", "mpa1_xf.py",
                "mpa1_stall.py"]
    for r in must_exclude:
        good = is_write_target(r)
        print("  EXCLUDE %-44s %s" % (r, "PASS" if good else "FAIL"))
        ok &= good
    for r in must_pin:
        good = not is_write_target(r)
        print("  PIN     %-44s %s" % (r, "PASS" if good else "FAIL"))
        ok &= good
    # `0.orig` is ONE CHARACTER from matching the time-directory predicate, so it
    # is driven explicitly in both directions rather than trusted.
    good = (_TIMEDIR.fullmatch("0.orig") is None and _TIMEDIR.fullmatch("0.0001")
            is not None and _TIMEDIR.fullmatch("0") is not None)
    print("  %-52s %s" % ("`0.orig` is NOT a time dir; `0` and `0.0001` ARE",
                          "PASS" if good else "FAIL"))
    ok &= good

    # ---- (a2) THE ROLE-DEPENDENT FILE, DRIVEN IN BOTH DIRECTIONS.
    print("\n[a2] mpa1_xopt.json's role is PASSED IN, never guessed")
    good = is_write_target(XOPT, xopt_is_input=False)
    print("  %-52s %s" % ("O arm: mpa1_xopt.json is a WRITE TARGET",
                          "PASS" if good else "FAIL"))
    ok &= good
    good = not is_write_target(XOPT, xopt_is_input=True)
    print("  %-52s %s" % ("endpoint arm: mpa1_xopt.json is PINNED",
                          "PASS" if good else "FAIL"))
    ok &= good

    tmp = tempfile.mkdtemp(prefix="mpa1_guard_selftest_")
    try:
        case = os.path.join(tmp, "arm")
        for d in ("system", "0.orig", "constant", "FFD", "0", "mp0/0", "mp1/0"):
            os.makedirs(os.path.join(case, d), exist_ok=True)
        for rel, body in (("system/fvSchemes", "schemes"),
                          ("system/controlDict",
                           "writeFormat ascii;\nwriteCompression on;\n"),
                          ("system/fvSolution", "solution"),
                          ("system/decomposeParDict", "numberOfSubdomains 1;"),
                          ("0.orig/U", "U0"),
                          ("0.orig/p", "p0"),
                          ("constant/transportProperties", "nu"),
                          ("FFD/wingFFD.xyz", "ffd"),
                          ("mpa1_runScript.py", "producer"),
                          ("mpa1_xf.py", "instrument"),
                          ("mpa1_stall.py", "detector"),
                          ("0/U.gz", "field-U"),
                          ("mp0/0/U.gz", "mp0-U"),
                          ("mp1/0/U.gz", "mp1-U")):
            open(os.path.join(case, rel), "w").write(body)
        man = os.path.join(tmp, "manifest.json")
        datum = os.path.join(case, "0/U.gz")

        print("\n[a3] pin, then the ENFORCING exclusion driven RED")
        ok &= _leg("pin a clean staged arm", lambda: cmd_pin(case, man), None)
        m = json.load(open(man))
        good = (m["datum"]["datum_reference"] == "0/U.gz"
                and m["datum"]["is_compressed_twin"] is True
                and m["datum"]["write_compression"] == "on")
        print("  %-52s %s" % ("datum resolved BY EXISTENCE to the compressed twin",
                              "PASS" if good else "FAIL"))
        ok &= good
        good = ("0/U.gz" not in m["pinned"] and "mp0/0/U.gz" not in m["pinned"]
                and "system/decomposeParDict" not in m["pinned"]
                and "0.orig/U" in m["pinned"] and "mpa1_runScript.py" in m["pinned"])
        print("  %-52s %s" % ("exclusion derived from the census, not asserted",
                              "PASS" if good else "FAIL"))
        ok &= good

        # the run: create write targets, leave the pinned files alone
        time.sleep(1.1)
        os.utime(datum, None)                      # the launcher's `touch 0/*`
        t0 = os.path.getmtime(datum)
        time.sleep(0.05)
        for rel in ("mpa1_O.json", "mpa1_xopt.json", "opt_IPOPT.txt"):
            open(os.path.join(case, rel), "w").write("{}")
        open(os.path.join(case, "mp0/0/U.gz"), "w").write("rewritten mid-run")
        arts = [os.path.join(case, "mpa1_O.json")]

        print("\n[a4] the GREEN leg")
        ok &= _leg("clean run", lambda: cmd_verify(case, man, datum, arts), None)

        print("\n[a5] the RED legs, each refusal demanded BY NAME")
        # RED 1 -- THE BRIEF'S OWN REQUIREMENT: a manifest that pins a name the
        # predicate calls a write target must REFUSE.  This is the leg that
        # proves the exclusion is ENFORCING and not descriptive.
        bad = os.path.join(tmp, "m_disagree.json")
        m2 = json.load(open(man))
        m2["pinned"]["0/U.gz"] = {"sha256": "0" * 64, "mtime": 0.0}
        json.dump(m2, open(bad, "w"))
        ok &= _leg("pinned name is a write target",
                   lambda: cmd_verify(case, bad, datum, arts),
                   "REFUSE_PIN_EXCLUSION_DISAGREE")

        # RED 1b -- THE ROLE DISAGREEMENT.  A manifest pinned on an ENDPOINT arm
        # (xopt an input) verified with that role must accept `mpa1_xopt.json`
        # pinned; the SAME manifest with the role flipped must refuse.  This is
        # the leg that proves the role travels in the manifest rather than being
        # re-guessed at verify time.
        endcase = os.path.join(tmp, "endarm")
        shutil.copytree(case, endcase)
        endman = os.path.join(tmp, "end_manifest.json")
        ok &= _leg("pin an ENDPOINT arm (xopt is an input)",
                   lambda: cmd_pin(endcase, endman, xopt_is_input=True), None)
        me = json.load(open(endman))
        good = XOPT in me["pinned"]
        print("  %-52s %s" % ("endpoint manifest PINS mpa1_xopt.json",
                              "PASS" if good else "FAIL"))
        ok &= good
        flip = os.path.join(tmp, "m_roleflip.json")
        me2 = json.load(open(endman))
        me2["xopt_is_input"] = False          # the role flipped under the manifest
        json.dump(me2, open(flip, "w"))
        edatum = os.path.join(endcase, "0/U.gz")
        ok &= _leg("role flipped between pin and verify",
                   lambda: cmd_verify(endcase, flip, edatum, []),
                   "REFUSE_PIN_EXCLUSION_DISAGREE")

        # RED 2 -- A RENAME THAT HOLDS THE FILE COUNT CONSTANT.  This is D19's
        # trap and the reason no count is compared anywhere in this file.
        n_before = len(enumerate_case(case))
        os.rename(os.path.join(case, "system/fvSchemes"),
                  os.path.join(case, "system/fvSchemes.gz"))
        n_after = len(enumerate_case(case))
        print("  count before %d, count after %d -- IDENTICAL, and the guard must "
              "still refuse" % (n_before, n_after))
        ok &= (n_before == n_after)
        ok &= _leg("rename at constant file count",
                   lambda: cmd_verify(case, man, datum, arts),
                   "REFUSE_MANIFEST_NAME_MISSING")
        os.rename(os.path.join(case, "system/fvSchemes.gz"),
                  os.path.join(case, "system/fvSchemes"))
        os.utime(os.path.join(case, "system/fvSchemes"),
                 (m["pinned"]["system/fvSchemes"]["mtime"],
                  m["pinned"]["system/fvSchemes"]["mtime"]))

        # RED 3 -- same name, different content
        keep = open(os.path.join(case, "system/controlDict")).read()
        open(os.path.join(case, "system/controlDict"), "w").write("MUTATED")
        ok &= _leg("pinned content mutated",
                   lambda: cmd_verify(case, man, datum, arts),
                   "REFUSE_MANIFEST_HASH_MOVED")
        open(os.path.join(case, "system/controlDict"), "w").write(keep)
        os.utime(os.path.join(case, "system/controlDict"),
                 (m["pinned"]["system/controlDict"]["mtime"],
                  m["pinned"]["system/controlDict"]["mtime"]))

        # RED 4 -- a pinned file newer than the datum
        os.utime(os.path.join(case, "system/fvSchemes"), (t0 + 60, t0 + 60))
        ok &= _leg("pinned file newer than the datum",
                   lambda: cmd_verify(case, man, datum, arts),
                   "REFUSE_AGE_DATUM_MOVED")
        os.utime(os.path.join(case, "system/fvSchemes"),
                 (m["pinned"]["system/fvSchemes"]["mtime"],
                  m["pinned"]["system/fvSchemes"]["mtime"]))

        # RED 5 -- a graded artifact older than the datum
        stale = os.path.join(tmp, "stale.json")
        open(stale, "w").write("{}")
        os.utime(stale, (t0 - 10, t0 - 10))
        ok &= _leg("graded artifact older than the datum",
                   lambda: cmd_verify(case, man, datum, [stale]),
                   "REFUSE_ARTIFACT_NOT_NEWER")

        # RED 6 -- the datum cannot be resolved at all
        nodatum = os.path.join(tmp, "nodatum")
        shutil.copytree(case, nodatum)
        os.remove(os.path.join(nodatum, "0/U.gz"))
        ok &= _leg("neither registered datum name exists",
                   lambda: cmd_pin(nodatum, os.path.join(tmp, "nd.json")),
                   "REFUSE_DATUM_UNRESOLVED")

        # RED 7 -- THE PREDICATE'S OWN PLANTED CONTROL.  A predicate that
        # excluded everything would make the guard vacuous and every leg above
        # would still be green.  This drives the overmatch directly.
        print("\n[a6] the predicate's own planted control -- an OVERMATCHING "
              "predicate must refuse at PIN time")
        saved = globals()["_WRITTEN_HEADS"]
        try:
            globals()["_WRITTEN_HEADS"] = frozenset(set(saved) | {"system"})
            ok &= _leg("predicate excludes a file it must pin",
                       lambda: cmd_pin(case, os.path.join(tmp, "over.json")),
                       "REFUSE_PREDICATE_OVERMATCH")
        finally:
            globals()["_WRITTEN_HEADS"] = saved
        ok &= _leg("and the guard is GREEN again once it is restored",
                   lambda: cmd_pin(case, os.path.join(tmp, "restored.json")), None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    a = list(argv[1:])
    xin = False
    if "--xopt-is-input" in a:
        xin = True
        a.remove("--xopt-is-input")
    if len(a) == 3 and a[0] == "pin":
        return cmd_pin(a[1], a[2], xin)
    if len(a) >= 4 and a[0] == "verify":
        return cmd_verify(a[1], a[2], a[3], a[4:])
    if len(a) == 1 and a[0] == "selftest":
        return cmd_selftest()
    if len(a) == 2 and a[0] == "census":
        rels = enumerate_case(a[1])
        pinned, excluded = partition(rels, xin)
        print("CENSUS files=%d pinned=%d excluded=%d" % (len(rels), len(pinned),
                                                         len(excluded)))
        return 0
    print(__doc__)
    print("usage: mpa1_age_guard.py pin <case_dir> <manifest.json> [--xopt-is-input]\n"
          "       mpa1_age_guard.py verify <case_dir> <manifest.json> <datum_file> <artifact>...\n"
          "       mpa1_age_guard.py census <case_dir> [--xopt-is-input]\n"
          "       mpa1_age_guard.py selftest")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
