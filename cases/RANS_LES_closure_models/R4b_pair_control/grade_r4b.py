#!/usr/bin/env python3
"""R4b instrument A7 - THE COMPARATOR, and it may not grade until it is born.

Grades R4b's G0-G7 as `R4b/PREREGISTRATION.md` sec. 5 writes them, re-hashes
every re-used instrument and refuses on any mismatch, applies the strict
completion rule with its age guard, and writes `artefacts/r4b_grading.json`.

THE BIRTH REQUIREMENT, AND IT IS ENFORCED ON THIS FILE BY THIS FILE
-------------------------------------------------------------------
Sanaa canonised it on 2026-08-28:

  "rule 3's question - 'was this reader ever shown able to see a non-zero
   through the real code path?' - is now the birth requirement for every
   reader/comparator: no instrument grades anything until that answer is yes,
   demonstrated."

So, before ANY gate is graded, this module reads
`artefacts/r4b_instrument_birth.json`, VERIFIES THAT RECORD'S OWN HASH, and
EXITS 2 if any control the gate it is about to grade needs is not recorded
born.  A comparator that has never returned a non-zero through the real path is
NOT BORN and its zeros are not evidence.

EVERY BIRTH DEMONSTRATION IS TWO-SIDED and both halves are graded:
  * positive - the instrument MUST SEE the plant, recovered through the real
    reader from a REAL FILE ON DISK, written by the real producer's code;
  * negative - the instrument MUST NOT FLAG an unperturbed copy of the same
    real file through the same path.
A demonstration carrying only the positive half certifies nothing about false
positives; only the negative half separates a working reader from one that
flags everything.

WHICH CONTROL SERVES WHICH GATE.  sec. 3.2's carve-out is registered in
advance: if a control's real artefact is absent, that control is
`PENDING: <path>`, the comparator is NOT BORN for the gate that control serves,
and it MUST REFUSE TO GRADE THAT GATE.  The mapping is fixed here so it cannot
be chosen after a reading:

    G1  <- G0b (field reader, a-priori scoring), G0f
    G2  <- G0f            (completion is read from logs and time dirs)
    G3  <- G0c (the U reader), G0f
    G4  <- G0d (the written grad(U) reader)
    G5  <- G0e (the realisability reader)
    G6  <- G0c (the U reader)
    G7  <- re-used, not re-fired (R4b sec. 6.3 governs when the re-use voids)

THE TWO RUN ROOTS, AND WHY THEY MUST BE TWO (sec. 3.3).  R4b's own
pre-registration is pre-compute and its pre-compute condition is that
`/home/ubuntu/closure-data/r4b/` does not exist.  Writing there would destroy
that condition and close R4b's amendment window before Sanaa has ruled on the
increment.  `--birth-only` ASSERTS THAT ROOT IS ABSENT before it begins and
exits 2 if it is not.

NO REFUSAL IN THIS FILE IS AN `assert` (L-332): `python3 -O` deletes `assert`,
which would erase every refusal in exactly the configuration a production run
is most likely to use.  This file contains ZERO `ast.Assert` nodes and
`--selftest` proves it by parsing its own source.

VERDICT VOCABULARY, and nothing else (standing rule 1):
PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(CLOSURE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(CLOSURE, "R4_sparta_build"))
sys.path.insert(0, os.path.join(CLOSURE, "_common"))

import r4_lib as R                                                   # noqa: E402
import score_aposteriori as SA                                       # noqa: E402
from of_read import read_field, realisability_violation, barycentric  # noqa: E402
import select_control as SC                                          # noqa: E402

INSTRUMENT_ROOT = "/home/ubuntu/closure-data/r4b_instruments"
SOLVE_ROOT = "/home/ubuntu/closure-data/r4b"
BIRTH_RECORD = os.path.join(HERE, "artefacts", "r4b_instrument_birth.json")
GRADING_OUT = os.path.join(HERE, "artefacts", "r4b_grading.json")

VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
         "PENDING")

# The reader THIS module uses for every OpenFOAM field it reads.  Bound by
# name so the birth demonstration provably exercises the same object the
# production path uses.
READER = read_field

# INSTRUMENT_BUILD_PREREGISTRATION.md sec. 3.1 - the ten re-used instruments,
# by path and by the sha256 measured at the freeze.  All ten are re-used
# UNMODIFIED; this comparator re-hashes all ten at grading and REFUSES on any
# mismatch.  A grading run against a silently edited instrument is not a result.
REUSED_SHA256 = {
    "R4_sparta_build/r4_lib.py":
        "23f37c0c2f296bc82e2dd48aeb68ac5baaffa25d8beb3c119430eadcbcf81fe0",
    "R4_sparta_build/build_aposteriori.py":
        "7c1150c5aad67252aeb1fbacf945809bce7bb386b0cbb7dfbdeaacbcce77e4dd",
    "R4_sparta_build/score_apriori.py":
        "b034c9ef6214ba9c56f11f0145e29a96928320e9693ff73fe3e9e9dc26b04da2",
    "R4_sparta_build/score_aposteriori.py":
        "6dc3cce2ce00f7d3d7bbda45f528bea6c9023a528babad19ed09f9ec21aa099c",
    "R4_sparta_build/fs3_select.py":
        "287e03d9f2c7b477a79a45f70ca6b18c4284969cff05b5b3786158d4b51e02e4",
    "R4_sparta_build/make_coverage.py":
        "f8c40810349c1caf5d633797d4e8d3f703a5a6b53de11c9f8b49010f82a6adb6",
    "R4_sparta_build/ic1_check.py":
        "342ac8ce735c6035e9e770abfa73e8b72eaace2a0d94a25e4ac8d1ac7e7282a0",
    "_common/of_read.py":
        "4263001cf8ad58b3671e22b8b12b72de926c6638416c7d9711aa9f0cd31705c8",
    "_common/sst_baseline_metrics.py":
        "7d78aebc222daa60fdb644d744e6f2d90d83337a84e665ea8f435dac341080ed",
    "_common/trainmean_baseline.json":
        "eb6378a403c923b238c984a16df193674d05857c78e38918cfe3ded8ff566f00",
}

NEW_INSTRUMENTS = ("select_control.py", "build_r4b_cases.py", "run_r4b.sh",
                   "grade_r4b.py")

# sec. 3.2 - the REAL producer artefacts each control must travel.
DEFAULT_ARTEFACTS = {
    "G0a": os.path.join(R.WORK, "frozen", "AR_10_Ret_180", "1654", "bijDelta"),
    "G0b": os.path.join(R.WORK, "frozen", "AR_10_Ret_180", "1654", "bijDelta"),
    "G0c": os.path.join(R.WORK, "aposteriori", "PHLL10595", "ceiling", "3513",
                        "U"),
    "G0d": "/home/ubuntu/closure-data/r5c/frozen/CBFS13700/354/grad(U)",
}

GATE_CONTROLS = {
    "G1": ("G0b", "G0f"), "G2": ("G0f",), "G3": ("G0c", "G0f"),
    "G4": ("G0d",), "G5": ("G0e",), "G6": ("G0c",), "G7": (),
}

# B5's two real cases, named in the registration.
REAL_COMPLETE_CASE = os.path.join(R.WORK, "aposteriori", "PHLL10595", "ceiling")
REAL_INCOMPLETE_CASE = os.path.join(R.WORK, "aposteriori", "PHLL10595",
                                    "discovered")


def refuse(code, msg):
    sys.stderr.write(f"REFUSED [{code}] {msg}\n")
    raise SystemExit(2)


def require(cond, code, msg):
    if not cond:
        refuse(code, msg)


def guard_write_root(path):
    p = os.path.abspath(path)
    require(p != os.path.abspath(SOLVE_ROOT)
            and not p.startswith(os.path.abspath(SOLVE_ROOT) + os.sep),
            "SOLVE-ROOT-GUARD",
            f"{p} is inside R4b's solve run root {SOLVE_ROOT}")
    return p


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_sha256(obj):
    """The birth record's OWN hash: sha256 over a canonical serialisation."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def write_json(path, obj):
    guard_write_root(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1)
        fh.write("\n")


def verdict_ok(v):
    return v in VOCAB


# ------------------------------------------------------- instrument hashes
def hash_sweep(strict=True):
    """Re-hash the 10 re-used instruments and the 4 new ones. Refuses (B1)."""
    reused, bad = {}, []
    for rel, want in REUSED_SHA256.items():
        p = os.path.join(CLOSURE, rel)
        if not os.path.exists(p):
            reused[rel] = dict(present=False, expected=want, measured=None)
            bad.append(f"{rel}: ABSENT")
            continue
        got = sha256_file(p)
        reused[rel] = dict(present=True, expected=want, measured=got,
                           matches=bool(got == want))
        if got != want:
            bad.append(f"{rel}: {got} != {want}")
    new = {}
    for name in NEW_INSTRUMENTS:
        p = os.path.join(HERE, name)
        new[name] = dict(present=os.path.exists(p),
                         sha256=sha256_file(p) if os.path.exists(p) else None,
                         committed_sha256=committed_sha256(p))
    if strict and bad:
        refuse("INSTRUMENT-HASH",
               "a re-used instrument does not match its registered sha256; a "
               "grading run against a silently edited instrument is not a "
               "result:\n  " + "\n  ".join(bad))
    return dict(reused=reused, new=new, mismatches=bad)


def committed_sha256(path, ref="HEAD"):
    rel = os.path.relpath(os.path.abspath(path), REPO)
    try:
        b = subprocess.run(["git", "-C", REPO, "cat-file", "blob", f"{ref}:{rel}"],
                           capture_output=True, check=False)
    except OSError:
        return None
    return hashlib.sha256(b.stdout).hexdigest() if b.returncode == 0 else None


# ------------------------------------------------ THE BIRTH DEMONSTRATIONS
def _split_field(text):
    i = text.index("internalField")
    j = text.index("boundaryField")
    return text[:i], text[i:j], text[j:]


def _rewrite_body(body, delta):
    """The SAME rewrite `r4_lib.planted_zero_reader_check` performs, with the
    added amount as a parameter: PLANT for the positive half, 0.0 for the
    negative half."""
    if "(" in body.split("\n", 3)[3]:
        return re.sub(r"\(\s*(-?[\d.eE+-]+)",
                      lambda m: "(" + f"{float(m.group(1)) + delta:.17g}", body)
    return re.sub(r"^\s*(-?\d[\d.eE+-]*)\s*$",
                  lambda m: f"{float(m.group(1)) + delta:.17g}", body,
                  flags=re.M)


def field_control(name, field_path, scratch_dir, producer):
    """G0a-G0d, TWO-SIDED, on a REAL file written by the real producer.

    Positive: `r4_lib.planted_zero_reader_check`, re-used UNMODIFIED, driven
    with THIS module's READER.  Its bar is magnitude-aware -- max(1e-12,
    8*eps*max|field|) AND the median recovery matching the plant to 1e-9
    relative -- for the reason R4 recorded as departure D-9: an absolute 1e-12
    bar refused a demonstrably correct reader on a field reaching 2.8e+06.
    It raises SystemExit(2) itself if the reader cannot see the plant.

    Negative: the same rewrite at delta = 0.0.  Nothing may move.

    THE ORIGINAL IS NEVER WRITTEN TO.  Every plant goes into a scratch copy.
    """
    if not os.path.exists(field_path):
        # sec. 3.2's registered carve-out, and it can only make things WORSE:
        # PENDING, NOT BORN for the gate this control serves, and the
        # comparator must then refuse to grade that gate.
        return dict(control=name, verdict="PENDING", pending_path=field_path,
                    born=False, both_halves=False,
                    reason=f"PENDING: {field_path} - the real artefact this "
                           f"control must travel does not exist")
    guard_write_root(scratch_dir)
    os.makedirs(scratch_dir, exist_ok=True)
    tag = os.path.basename(field_path).replace("(", "_").replace(")", "_")

    pos = R.planted_zero_reader_check(
        field_path, READER, os.path.join(scratch_dir, f"{name}_{tag}_planted"))

    head, body, tail = _split_field(open(field_path).read())
    neg_path = os.path.join(scratch_dir, f"{name}_{tag}_unperturbed")
    with open(neg_path, "w") as fh:
        fh.write(head + _rewrite_body(body, 0.0) + tail)
    a = np.asarray(READER(field_path), dtype=float).reshape(-1)
    b = np.asarray(READER(neg_path), dtype=float).reshape(-1)
    require(a.size == b.size, f"{name}-NEG",
            f"the unperturbed copy changed the value count {a.size} -> {b.size}")
    d = b - a
    n_moved = int((np.abs(d) > 0).sum())
    require(n_moved == 0, f"{name}-NEG",
            f"the reader flagged {n_moved} values on an UNPERTURBED copy of "
            f"{field_path}; a reader that moves on nothing cannot certify that "
            f"it moved on something")
    return dict(control=name, verdict="PASS", born=True, both_halves=True,
                reader="of_read.read_field",
                bar="r4_lib.planted_zero_reader_check (unmodified)",
                real_artefact=os.path.abspath(field_path),
                real_artefact_producer=producer,
                real_artefact_bytes=os.path.getsize(field_path),
                positive=pos,
                negative=dict(scratch=os.path.abspath(neg_path),
                              path="same rewrite, delta = 0.0",
                              n_values_moved=n_moved, flagged=False))


def realisability_control(scratch_dir, dataset=None, model=None):
    """G0e, TWO-SIDED, on a total-b array built from REAL frozen fields.

    A violating fraction of 0.0000 is exactly the kind of zero rule 3 exists
    for: without a planted non-realisable cell, a broken barycentric routine
    and a perfectly realisable model return the same number.

    The violating count must rise by EXACTLY ONE.  "At least one" is also
    satisfied by a routine that flags everything, which is the failure this
    control exists to exclude.
    """
    dataset = dataset or SC.DATASET
    model = model or SC.R4_MODEL
    guard_write_root(scratch_dir)
    os.makedirs(scratch_dir, exist_ok=True)

    man = json.load(open(os.path.join(dataset, "dataset_manifest.json")))
    cand = list(man["candidates"])
    m = json.load(open(model))
    case = sorted(man["cases"])[0]
    b_lin, b_mod, _, _ = SC.load_case(dataset, case, cand,
                                      list(m["bDelta"]["names"]),
                                      [list(t) for t in m["bDelta"]["terms"]])
    b_total = b_lin + SC.GRID[3] * b_mod        # a real, feasible amplitude

    base_p = os.path.join(scratch_dir, "G0e_b_total.npy")
    np.save(base_p, b_total)
    v0, _ = realisability_violation(np.load(base_p), tol=SC.TOL)
    n0 = int(v0.sum())

    clean = np.where(~v0)[0]
    require(clean.size > 0, "G0E-NOCELL",
            "no realisable cell to plant into")
    idx = int(clean[0])
    planted = np.load(base_p)
    planted[idx] = SC.NONREALISABLE_CELL
    pos_p = os.path.join(scratch_dir, "G0e_b_total_planted.npy")
    np.save(pos_p, planted)
    v1, _ = realisability_violation(np.load(pos_p), tol=SC.TOL)
    n1 = int(v1.sum())

    neg_p = os.path.join(scratch_dir, "G0e_b_total_unperturbed.npy")
    np.save(neg_p, np.load(base_p))
    v2, _ = realisability_violation(np.load(neg_p), tol=SC.TOL)
    n2 = int(v2.sum())

    coords, _ = barycentric(SC.NONREALISABLE_CELL[None, :, :])
    require(n1 - n0 == 1, "G0E-POS",
            f"the violating count rose by {n1 - n0}, not by EXACTLY one "
            f"({n0} -> {n1})")
    require(bool(v1[idx]), "G0E-POS",
            f"the count moved but cell {idx} - the one planted into - is not "
            f"the cell flagged")
    require(n2 == n0, "G0E-NEG",
            f"the unperturbed copy raised the count {n0} -> {n2}")
    return dict(control="G0e", verdict="PASS", born=True, both_halves=True,
                reader="of_read.realisability_violation",
                source_case=case, xi_used=SC.GRID[3], tolerance=SC.TOL,
                array_path=os.path.abspath(base_p),
                array_shape=list(b_total.shape),
                planted_cell_index=idx,
                planted_min_barycentric_coordinate=float(coords.min()),
                n_violating_baseline=n0, n_violating_planted=n1,
                n_violating_unperturbed=n2, rose_by=n1 - n0, required_rise=1)


def zero_shot_control():
    """G0f, TWO-SIDED, through the real frozen guard AND this call site's own.

    MEASURED AND DISCLOSED, not worked around: `r4_lib.assert_no_test_case` is
    a bare `assert` in a FROZEN file this item may not edit.  Under `python3
    -O` that assert is DELETED and the guard raises on NEITHER list.  The
    explicit refusal at this call site does survive `-O`, and both readings are
    recorded.
    """
    clean = ["PHLL10595", "CBFS13700", "AR_1_Ret_180"]
    dirty = clean + ["NASA_2DWMH"]
    optimized = bool(sys.flags.optimize)

    frozen_dirty = False
    try:
        R.assert_no_test_case(dirty)
    except AssertionError:
        frozen_dirty = True
    frozen_clean = False
    try:
        R.assert_no_test_case(clean)
    except AssertionError:
        frozen_clean = True

    own_dirty = False
    try:
        own_zero_shot(dirty)
    except SystemExit:
        own_dirty = True
    own_clean = True
    try:
        own_zero_shot(clean)
    except SystemExit:
        own_clean = False

    if not optimized:
        require(frozen_dirty, "G0F-POS",
                "assert_no_test_case did not raise on NASA_2DWMH")
    require(not frozen_clean, "G0F-NEG",
            "assert_no_test_case raised on a clean training list")
    require(own_dirty, "G0F-POS-OWN", "own zero-shot refusal did not fire")
    require(own_clean, "G0F-NEG-OWN", "own zero-shot refusal fired on a clean list")
    return dict(control="G0f", verdict="PASS", born=True, both_halves=True,
                guard="r4_lib.assert_no_test_case", planted_case="NASA_2DWMH",
                interpreter_optimized=optimized,
                frozen_guard_raised_on_planted=frozen_dirty,
                frozen_guard_raised_on_clean=frozen_clean,
                frozen_guard_blind_under_dash_O=bool(optimized and not frozen_dirty),
                own_refusal_fired_on_planted=own_dirty,
                own_refusal_silent_on_clean=own_clean)


def own_zero_shot(cases):
    bad = sorted(set(cases) & (R.TEST_CASES | R.VAL_CASES))
    require(not bad, "ZERO-SHOT",
            f"ZERO-SHOT VIOLATION: test/validation case in set: {bad}")


# ------------------------------------------------------------------- B1
def _run(cmd, env=None, cwd=None, timeout=300):
    """Run a command and return (rc, stdout, stderr).  rc is captured DIRECTLY
    from the process, never through a pipe: a pipeline's status is the LAST
    command's, so `cmd | tail` reports tail's success for a refused cmd."""
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, env=e,
                       cwd=cwd or HERE, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def b1_existence_and_refusals(root, model_json, coverage_md, built_case_dir):
    """B1: all four exist, are executable/importable, and EVERY registered
    refusal fires - under `python3` AND under `python3 -O`."""
    out = {"instruments": {}, "refusals": [], "selftests": {}}
    for name in NEW_INSTRUMENTS:
        p = os.path.join(HERE, name)
        out["instruments"][name] = dict(
            path=p, present=os.path.exists(p),
            sha256=sha256_file(p) if os.path.exists(p) else None,
            executable=os.access(p, os.X_OK))

    for name in NEW_INSTRUMENTS:
        p = os.path.join(HERE, name)
        if name.endswith(".sh"):
            rc, _, _ = _run(["bash", p, "--selftest"])
            out["selftests"][name] = dict(python3=rc, python3_O=None,
                                          note="shell script; -O is a Python "
                                               "flag and does not apply")
        else:
            rc1, _, _ = _run([sys.executable, p, "--selftest"])
            rc2, _, _ = _run([sys.executable, "-O", p, "--selftest"])
            out["selftests"][name] = dict(python3=rc1, python3_O=rc2)

    bad_model = os.path.join(root, "birth", "b1", "MODEL_n4.json")
    guard_write_root(bad_model)
    os.makedirs(os.path.dirname(bad_model), exist_ok=True)
    m = json.load(open(model_json))
    m4 = dict(m)
    m4["bDelta_terms_scaled"] = [[4, 0, 0, -1.0]]
    m4["frozen_at"] = utcnow()
    with open(bad_model, "w") as fh:
        json.dump(m4, fh, indent=1)
    good_sha = sha256_file(model_json)

    sc = os.path.join(HERE, "select_control.py")
    bc = os.path.join(HERE, "build_r4b_cases.py")
    rr = os.path.join(HERE, "run_r4b.sh")
    gr = os.path.join(HERE, "grade_r4b.py")
    missing = os.path.join(root, "birth", "b1", "NO_SUCH_MODEL.json")
    nocov = os.path.join(root, "birth", "b1", "NO_SUCH_COVERAGE.md")

    checks = [
        ("select_control.py", "CRITERION",
         [sc, "--criterion", "b_rms", "--out-dir", os.path.join(root, "birth")]),
        ("select_control.py", "SOLVE-ROOT-GUARD",
         [sc, "--out-dir", os.path.join(SOLVE_ROOT, "x")]),
        ("select_control.py", "G0A-ARTEFACT (carve-out)",
         [sc, "--birth", "--bijdelta", "/nonexistent/bijDelta",
          "--out-dir", os.path.join(root, "birth")]),
        ("build_r4b_cases.py", "MODEL-ABSENT",
         [bc, "--model", missing, "--coverage", coverage_md,
          "--out-root", os.path.join(root, "b1cases")]),
        ("build_r4b_cases.py", "MODEL-HASH",
         [bc, "--model", model_json, "--coverage", coverage_md,
          "--model-sha256", "0" * 64,
          "--out-root", os.path.join(root, "b1cases")]),
        ("build_r4b_cases.py", "COVERAGE-ABSENT",
         [bc, "--model", model_json, "--coverage", nocov,
          "--model-sha256", good_sha,
          "--out-root", os.path.join(root, "b1cases")]),
        ("build_r4b_cases.py", "TERM-ORDER (n = 4)",
         [bc, "--model", bad_model, "--coverage", coverage_md,
          "--model-sha256", sha256_file(bad_model), "--dry-run",
          "--cases", "alpha_125", "--out-root", os.path.join(root, "b1cases")]),
        ("build_r4b_cases.py", "SOLVE-ROOT-GUARD",
         [bc, "--model", model_json, "--coverage", coverage_md,
          "--model-sha256", good_sha, "--out-root", SOLVE_ROOT]),
        ("grade_r4b.py", "BIRTH-RECORD-ABSENT",
         [gr, "--birth-record", missing, "--grade", "--root", root]),
    ]
    if built_case_dir:
        checks.insert(7, ("build_r4b_cases.py", "CASE-TREE-EXISTS",
                          [bc, "--model", model_json, "--coverage", coverage_md,
                           "--model-sha256", good_sha,
                           "--cases", os.path.basename(
                               os.path.dirname(built_case_dir)),
                           "--out-root", os.path.dirname(os.path.dirname(
                               built_case_dir))]))

    for inst, code, argv in checks:
        rc1, _, e1 = _run([sys.executable] + argv)
        rc2, _, e2 = _run([sys.executable, "-O"] + argv)
        out["refusals"].append(dict(
            instrument=inst, refusal=code,
            rc_python3=rc1, rc_python3_O=rc2,
            fires=bool(rc1 == 2 and rc2 == 2),
            is_assertion_error=bool("AssertionError" in e1
                                    or "AssertionError" in e2),
            stderr_head=(e1.strip().splitlines() or [""])[0][:200]))

    for code, argv in [("SOLVE-ROOT-GUARD",
                        ["bash", rr, "--root", os.path.join(SOLVE_ROOT, "x")]),
                       ("ROOT-ABSENT",
                        ["bash", rr, "--root",
                         os.path.join(root, "no_such_root")])]:
        rc, _, e = _run(argv)
        out["refusals"].append(dict(
            instrument="run_r4b.sh", refusal=code, rc_python3=rc,
            rc_python3_O=None, fires=bool(rc == 2), is_assertion_error=False,
            stderr_head=(e.strip().splitlines() or [""])[0][:200],
            note="shell script; -O does not apply"))

    n = len(out["refusals"])
    fired = sum(1 for r in out["refusals"] if r["fires"])
    assertion = any(r["is_assertion_error"] for r in out["refusals"])
    st_ok = all(v["python3"] == 0 and (v["python3_O"] in (0, None))
                for v in out["selftests"].values())
    present = all(v["present"] for v in out["instruments"].values())
    out.update(n_refusals=n, n_fired=fired,
               all_present=present, any_assertion_error=assertion,
               selftests_rc0=st_ok,
               verdict=("PASS" if (present and fired == n and not assertion
                                   and st_ok) else "GATE FAIL"))
    return out


# ------------------------------------------------------------------- B5
def b5_runner(root, case_dir):
    """B5, all three clauses, both halves each, with the REGISTERED SOLVER
    SUBSTITUTION.  No `simpleFoam` is launched.  See the module docstring and
    the script's own header: B5 does NOT establish that `run_r4b.sh` can drive
    `simpleFoam`."""
    rr = os.path.join(HERE, "run_r4b.sh")
    rep = {}

    # -- clause 1, capacity, two-sided, with a REAL planted background process.
    scratch = guard_write_root(os.path.join(root, "birth", "run_r4b"))
    os.makedirs(scratch, exist_ok=True)
    rc, quiet, _ = _run(["bash", rr, "--capacity-only"])
    n_quiet = int(re.search(r"foreign solvers \(pgrep\)\s+(\d+)", quiet).group(1))
    jobs_quiet = re.search(r"registered concurrency -> (\S+)", quiet).group(1)

    # A REAL process, really running, whose name the sweep is required to
    # count.  Named so no reader can mistake it for a solver: it is a copy of
    # /bin/sleep and its full command line is recorded below.
    planted = os.path.join(scratch, "r4bBirthDemoNotASolverFoam")
    shutil.copy("/bin/sleep", planted)
    proc = subprocess.Popen([planted, "20"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.7)
        rc, busy, _ = _run(["bash", rr, "--capacity-only"])
        n_busy = int(re.search(r"foreign solvers \(pgrep\)\s+(\d+)",
                               busy).group(1))
        saw_it = bool(re.search(re.escape(os.path.basename(planted)), busy))
    finally:
        proc.terminate()          # the process THIS function started, and only it
        proc.wait(timeout=10)
    require(n_busy > n_quiet and saw_it, "B5-CAPACITY-POS",
            f"the capacity check did not see a real planted process it is "
            f"required to count ({n_quiet} -> {n_busy}, matched={saw_it})")
    require(jobs_quiet != "BLOCKED", "B5-CAPACITY-NEG",
            f"the capacity check refused on a quiet box (concurrency "
            f"{jobs_quiet}); a check that refuses always permits nothing")
    rep["capacity"] = dict(
        n_solvers_quiet=n_quiet, n_solvers_busy=n_busy,
        planted_process=planted, planted_argv=[planted, "20"],
        planted_process_seen_by_name=saw_it,
        concurrency_on_quiet_box=jobs_quiet, refused_on_quiet_box=False,
        both_halves=True, verdict="PASS")

    # -- clause 1b, THE NON-pgrep PATH FIRES BY ITSELF (L-41).
    fresh = os.path.join(scratch, "fresh_run_dir")
    os.makedirs(fresh, exist_ok=True)
    os.utime(fresh, None)
    rc, nop, _ = _run(["bash", rr, "--capacity-only", "--no-pgrep"])
    n_sweep_off = int(re.search(r"foreign solvers \(pgrep\)\s+(\d+)",
                                nop).group(1))
    mtimes = int(re.search(r"run dirs touched < \d+ min\s+(\d+)", nop).group(1))
    docket = int(re.search(r"docket in-flight rows\s+(\d+)", nop).group(1))
    commits = int(re.search(r"commits < \d+ min\s+(\d+)", nop).group(1))
    require(n_sweep_off == 0, "B5-NONPGREP",
            "the sweep was not actually disabled")
    require(mtimes > 0, "B5-NONPGREP",
            "with the process sweep disabled the mtime path saw nothing; the "
            "non-pgrep path does not fire by itself and L-41 is not addressed")
    rep["non_pgrep_path"] = dict(
        pgrep_disabled=True, n_solvers_reported=n_sweep_off,
        run_dirs_touched=mtimes, docket_rows=docket, recent_commits=commits,
        fires_by_itself=True, verdict="PASS")

    # -- clause 2, skip-if-complete, two-sided, on TWO REAL cases.
    rc_c, o_c, _ = _run(["bash", rr, "--check-dir", REAL_COMPLETE_CASE])
    rc_i, o_i, _ = _run(["bash", rr, "--check-dir", REAL_INCOMPLETE_CASE])
    require(rc_c == 0, "B5-SKIP-POS",
            f"{REAL_COMPLETE_CASE} - a real COMPLETE run under sec. 4.2 - was "
            f"not recognised as complete (rc {rc_c}: {o_c.strip()})")
    require(rc_i == 1, "B5-SKIP-NEG",
            f"{REAL_INCOMPLETE_CASE} - a real INCOMPLETE run - was reported "
            f"complete (rc {rc_i}: {o_i.strip()})")
    rep["skip_if_complete"] = dict(
        real_complete_case=REAL_COMPLETE_CASE, rc_complete=rc_c,
        reading_complete=o_c.strip(),
        real_incomplete_case=REAL_INCOMPLETE_CASE, rc_incomplete=rc_i,
        reading_incomplete=o_i.strip(), both_halves=True, verdict="PASS")

    # -- clause 3, it never kills: mechanical, on the script's own bytes, with
    #    its own planted control.  The DIFF is the supervisor's non-delegable
    #    check-1 and this does not replace it.
    rc_st, o_st, _ = _run(["bash", rr, "--selftest"])
    rep["never_kills"] = dict(
        selftest_rc=rc_st,
        no_kill_verbs="[ok ] no_kill_verbs" in o_st,
        planted_control_sees_one="[ok ] kill_check_sees_a_planted_kill" in o_st,
        verified_by="mechanical grep of the script's own bytes, with a planted "
                    "positive control; the DIFF remains the supervisor's "
                    "non-delegable SUPERVISION_CHARTER sec.3 check 1",
        verdict="PASS" if (rc_st == 0 and "[ok ] no_kill_verbs" in o_st)
                else "GATE FAIL")

    # -- the drive path itself, with the REGISTERED NO-OP SOLVER.
    if case_dir and os.path.isdir(case_dir):
        case = os.path.basename(os.path.dirname(case_dir))
        cfg = os.path.basename(case_dir)
        rc_r, o_r, e_r = _run(["bash", rr, "--root",
                               os.path.dirname(os.path.dirname(case_dir)),
                               "--config", cfg, "--cases", case],
                              env={"R4B_SOLVER": "/bin/true"})
        ws = os.path.join(case_dir, "wall_seconds")
        rep["drive_with_noop_solver"] = dict(
            rc=rc_r, case=case, config=cfg,
            solver="/bin/true (REGISTERED NO-OP; no simpleFoam was launched)",
            wall_seconds_recorded=os.path.exists(ws),
            wall_seconds=(open(ws).read().strip()
                          if os.path.exists(ws) else None),
            rc_file=(open(os.path.join(case_dir, "rc")).read().strip()
                     if os.path.exists(os.path.join(case_dir, "rc")) else None),
            verdict="PASS" if rc_r == 0 and os.path.exists(ws) else "GATE FAIL")

    sub = [v["verdict"] for v in rep.values() if isinstance(v, dict)]
    rep["verdict"] = "PASS" if all(v == "PASS" for v in sub) else "GATE FAIL"
    rep["registered_limitation"] = (
        "B5 exercises run_r4b.sh with its solver invocation replaced by a "
        "registered no-op. NO simpleFoam is launched by this item. B5 "
        "therefore does NOT establish that run_r4b.sh can drive simpleFoam, "
        "and this item may not be read as having established it.")
    return rep


# ---------------------------------------------------------------- birth
def run_birth(root, model_json, coverage_md, built_case_dir, artefacts=None):
    """sec. 3.3: --birth-only ASSERTS R4b's SOLVE run root is absent FIRST."""
    require(not os.path.exists(SOLVE_ROOT), "SOLVE-ROOT-PRESENT",
            f"{SOLVE_ROOT} EXISTS. That is R4b's solve run root and its "
            f"absence is R4b's own pre-compute condition; this item may not "
            f"run while it exists, because anything written there closes "
            f"R4b's amendment window before Sanaa has ruled on the increment.")
    root = guard_write_root(root)
    art = dict(DEFAULT_ARTEFACTS)
    art.update(artefacts or {})
    scratch = os.path.join(root, "birth", "grade_r4b")

    controls = {}
    controls["G0a"] = field_control("G0a", art["G0a"], scratch,
                                    "the frozen extraction (kCorrectiveFrozenFoam)")
    controls["G0b"] = field_control("G0b", art["G0b"], scratch,
                                    "the frozen extraction (kCorrectiveFrozenFoam)")
    controls["G0c"] = field_control("G0c", art["G0c"], scratch,
                                    "the propagation solver (simpleFoam / "
                                    "kOmegaSSTCorrected)")
    controls["G0d"] = field_control("G0d", art["G0d"], scratch,
                                    "OpenFOAM postProcess -func 'grad(U)'")
    controls["G0e"] = realisability_control(scratch)
    controls["G0f"] = zero_shot_control()

    b1 = b1_existence_and_refusals(root, model_json, coverage_md,
                                   built_case_dir)
    b5 = b5_runner(root, built_case_dir)

    born = {k: bool(v.get("born")) for k, v in controls.items()}
    n_born = sum(born.values())
    pending = {k: v["pending_path"] for k, v in controls.items()
               if v.get("verdict") == "PENDING"}
    not_born_gates = sorted({g for g, cs in GATE_CONTROLS.items()
                             for c in cs if not born.get(c)})

    b2 = dict(gate="B2", n_controls=len(controls), n_born=n_born,
              controls_born=born, pending=pending,
              verdict="PASS" if n_born == len(controls) else "GATE FAIL",
              not_born_gates=not_born_gates)

    record = dict(
        item="R4b-I", gate_set=["B1", "B2", "B3", "B4", "B5"],
        registration="cases/RANS_LES_closure_models/R4b_pair_control/"
                     "INSTRUMENT_BUILD_PREREGISTRATION.md",
        registration_sha256=sha256_file(os.path.join(
            HERE, "INSTRUMENT_BUILD_PREREGISTRATION.md")),
        at=utcnow(),
        interpreter=sys.version.split()[0],
        interpreter_optimize=int(sys.flags.optimize),
        instrument_root=root, solve_root=SOLVE_ROOT,
        solve_root_absent_at_start=True,
        birth_requirement="INSTRUMENT_BUILD_PREREGISTRATION.md section 5.0; "
                          "every demonstration is TWO-SIDED and both halves "
                          "are graded",
        hashes=hash_sweep(strict=False),
        controls=controls, gate_controls={k: list(v)
                                          for k, v in GATE_CONTROLS.items()},
        B1=b1, B2=b2, B5=b5)
    return record


def write_birth_record(record, path):
    """The record carries ITS OWN HASH, over a canonical serialisation, so a
    later edit to it is detectable by the comparator that reads it."""
    payload = dict(record=record, record_sha256=canonical_sha256(record))
    write_json(path, payload)
    return payload


def load_birth_record(path):
    require(os.path.exists(path), "BIRTH-RECORD-ABSENT",
            f"{path} does not exist. sec. 5.0: no instrument grades anything "
            f"until it has returned a non-zero through the real code path on a "
            f"real producer artefact, and that demonstration is on the record.")
    try:
        payload = json.load(open(path))
    except ValueError as e:
        refuse("BIRTH-RECORD-UNREADABLE", f"{path}: {e}")
    require(isinstance(payload, dict) and "record" in payload
            and "record_sha256" in payload, "BIRTH-RECORD-SHAPE",
            f"{path} is not a birth record (no record / record_sha256)")
    got = canonical_sha256(payload["record"])
    require(got == payload["record_sha256"], "BIRTH-RECORD-HASH",
            f"{path} fails its OWN hash: {got} != {payload['record_sha256']}. "
            f"A birth record that has been edited since it was written is not "
            f"a demonstration.")
    return payload["record"]


def assert_born_for(record, gate):
    """sec. 5.0 / sec. 3.2: refuse to grade a gate whose control is not born."""
    needed = GATE_CONTROLS.get(gate, ())
    controls = record.get("controls", {})
    missing = [c for c in needed
               if not controls.get(c, {}).get("born")
               or not controls.get(c, {}).get("both_halves")]
    require(not missing, "NOT-BORN",
            f"{gate} cannot be graded: control(s) {missing} are not recorded "
            f"born two-sided in the birth record. A comparator that has never "
            f"returned a non-zero through the real path is NOT BORN and its "
            f"zeros are not evidence.")
    return dict(gate=gate, controls=list(needed), all_born=True)


# ---------------------------------------------------------------- grading
def grade(record, root, config="pair", cases=None):
    """Grade R4b's G0-G7 as sec. 5 writes them.  Every gate first checks that
    the controls it depends on are recorded born, and REFUSES if they are not.
    """
    hash_sweep(strict=True)
    out = dict(item="R4b", at=utcnow(), root=root, config=config,
               birth_record_verified=True,
               instrument_hashes=hash_sweep(strict=False),
               gates={})

    out["gates"]["G0"] = dict(
        verdict="PASS" if all(c.get("born") for c in record["controls"].values())
        else "NOT A RESULT",
        controls={k: v.get("verdict") for k, v in record["controls"].items()},
        note="any G0 control failing -> NOT A RESULT, and the lane stops. The "
             "comparator is not evidence.")
    if out["gates"]["G0"]["verdict"] != "PASS":
        out["verdict"] = "NOT A RESULT"
        return out

    if not os.path.isdir(root):
        for g in ("G1", "G2", "G3", "G4", "G5", "G6", "G7"):
            out["gates"][g] = dict(verdict="PENDING", path=root,
                                   born=assert_born_for(record, g))
        out["verdict"] = "PENDING"
        out["pending_reason"] = (
            f"PENDING: {root} - the propagation run root does not exist. R4b's "
            f"solve arm is BLOCKED on Sanaa's direction on the increment "
            f"(INSTRUMENT_BUILD_PREREGISTRATION.md section 1) and this "
            f"comparator does not move it.")
        return out

    cases = cases or sorted(os.listdir(root))
    own_zero_shot(cases)
    rows = {}
    for case in cases:
        d = os.path.join(root, case, config)
        if not os.path.isdir(d):
            continue
        ok, why, info = R.solve_complete(d)
        lf = SA.log_facts(d) if os.path.isdir(d) else {}
        if ok and lf.get("floating_point_exception"):
            ok, why = False, "Foam::sigFpe::sigHandler frame (sec. 4.2 cond 6)"
        rows[case] = dict(dir=d, complete=bool(ok), reason=why,
                          converged=bool(info.get("stop_state") == "converged"),
                          iterations=lf.get("iterations"),
                          log_facts=lf, completion_info=info)

    n = len(rows)
    n_conv = sum(1 for r in rows.values() if r["complete"] and r["converged"])
    out["gates"]["G2"] = dict(
        born=assert_born_for(record, "G2"),
        n_cases=n, n_converged=n_conv,
        verdict=("PASS" if (n == 12 and n_conv == 12)
                 else "GATE REACHED" if n_conv >= 8 else "GATE FAIL"),
        rule="PASS requires all 12 COMPLETE and CONVERGED; GATE REACHED if "
             ">= 8 of 12 converge; below 8 GATE FAIL.",
        per_case={k: dict(complete=v["complete"], converged=v["converged"],
                          reason=v["reason"], iterations=v["iterations"])
                  for k, v in rows.items()})

    # G1, G3-G7 are delegated to the RE-USED scorers, which are the registered
    # instruments (R4b sec. 9).  Each first refuses if its control is not born.
    for g in ("G1", "G3", "G4", "G5", "G6", "G7"):
        out["gates"][g] = dict(born=assert_born_for(record, g),
                               verdict="PENDING",
                               instrument=dict(
                                   G1="R4_sparta_build/score_apriori.py",
                                   G3="R4_sparta_build/score_aposteriori.py",
                                   G4="_common/of_read.py (grad(U), "
                                      "RMS_vol(div U)/RMS_vol(||grad U||_F))",
                                   G5="R4_sparta_build/score_aposteriori."
                                      "realisability",
                                   G6="R4_sparta_build/score_aposteriori + "
                                      "_common/sst_baseline_metrics.py",
                                   G7="re-used, not re-fired (R4b sec. 6.3)")[g],
                               note="PENDING until the propagation run this "
                                    "gate reads has been produced under R4b's "
                                    "own registration.")

    vs = [v["verdict"] for v in out["gates"].values()]
    out["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in vs
                      else "GATE FAIL" if "GATE FAIL" in vs
                      else "PENDING" if "PENDING" in vs
                      else "GATE REACHED" if "GATE REACHED" in vs else "PASS")
    return out


# --------------------------------------------------------------- selftest
def _selftest():
    import tempfile
    ok = []

    def check(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    def refused(fn, want=2):
        try:
            fn()
            return False, "did not refuse"
        except SystemExit as e:
            return e.code == want, f"code={e.code}"

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    check("zero_ast_assert_nodes", n_assert == 0, f"count={n_assert}")

    check("vocab_is_the_six", VOCAB == ("PASS", "GATE REACHED", "GATE FAIL",
                                        "NOT A RESULT", "BLOCKED", "PENDING"))
    check("no_synonyms_emitted", all(verdict_ok(v) for v in VOCAB))
    check("ten_reused_instruments", len(REUSED_SHA256) == 10,
          str(len(REUSED_SHA256)))
    check("four_new_instruments", len(NEW_INSTRUMENTS) == 4)

    c, d = refused(lambda: guard_write_root(os.path.join(SOLVE_ROOT, "x")))
    check("solve_root_guard", c, d)

    # the birth record's own hash, both halves: a good record loads, an edited
    # one is refused.
    with tempfile.TemporaryDirectory() as td:
        rec = dict(controls={"G0a": dict(born=True, both_halves=True)},
                   at=utcnow())
        p = os.path.join(td, "birth.json")
        payload = dict(record=rec, record_sha256=canonical_sha256(rec))
        json.dump(payload, open(p, "w"))
        try:
            back = load_birth_record(p)
            check("birth_record_roundtrip", back["at"] == rec["at"])
        except SystemExit as e:
            check("birth_record_roundtrip", False, f"code={e.code}")

        tampered = json.load(open(p))
        tampered["record"]["controls"]["G0a"]["born"] = False
        json.dump(tampered, open(p, "w"))
        c, d = refused(lambda: load_birth_record(p))
        check("birth_record_hash_refuses_a_tampered_record", c, d)

        c, d = refused(lambda: load_birth_record(os.path.join(td, "nope.json")))
        check("refusal_BIRTH_RECORD_ABSENT", c, d)

        json.dump({"record": rec}, open(p, "w"))
        c, d = refused(lambda: load_birth_record(p))
        check("refusal_BIRTH_RECORD_SHAPE", c, d)

    # NOT-BORN, both halves: a born control grades, an unborn one refuses.
    born_rec = dict(controls={c: dict(born=True, both_halves=True)
                              for c in ("G0a", "G0b", "G0c", "G0d", "G0e",
                                        "G0f")})
    try:
        assert_born_for(born_rec, "G4")
        check("assert_born_positive", True)
    except SystemExit as e:
        check("assert_born_positive", False, f"code={e.code}")
    unborn = dict(controls=dict(born_rec["controls"]))
    unborn["controls"]["G0d"] = dict(born=False, both_halves=False)
    c, d = refused(lambda: assert_born_for(unborn, "G4"))
    check("refusal_NOT_BORN", c, d)
    try:
        assert_born_for(unborn, "G5")     # G5 does not depend on G0d
        check("not_born_is_gate_specific", True)
    except SystemExit as e:
        check("not_born_is_gate_specific", False, f"code={e.code}")

    # the instrument hash sweep: strict=False reports, strict=True refuses on a
    # planted mismatch, and the sweep is shown able to SEE a mismatch.
    sweep = hash_sweep(strict=False)
    check("hash_sweep_reads_ten", len(sweep["reused"]) == 10)
    check("hash_sweep_all_match", not sweep["mismatches"],
          str(sweep["mismatches"])[:120])
    saved = REUSED_SHA256["_common/of_read.py"]
    REUSED_SHA256["_common/of_read.py"] = "f" * 64
    planted = hash_sweep(strict=False)
    check("hash_sweep_sees_a_planted_mismatch", len(planted["mismatches"]) == 1)
    c, d = refused(lambda: hash_sweep(strict=True))
    check("refusal_INSTRUMENT_HASH", c, d)
    REUSED_SHA256["_common/of_read.py"] = saved

    # the rewrite: exact at delta = 0, moves at delta = PLANT.
    body = ("internalField   nonuniform List<vector>\n2\n(\n"
            "(1.5 2.5 3.5)\n(-2.25e-03 0 1)\n)\n;\n")
    first = lambda s: float(re.search(r"\(\s*(-?[\d.eE+-]+)",
                                      s.split("(\n", 1)[1]).group(1))
    check("rewrite_exact_at_zero", first(_rewrite_body(body, 0.0)) == 1.5)
    check("rewrite_moves_at_plant",
          abs(first(_rewrite_body(body, R.PLANT)) - (1.5 + R.PLANT)) < 1e-15)

    # the planted non-realisable cell, through the real reader.
    coords, _ = barycentric(SC.NONREALISABLE_CELL[None, :, :])
    check("planted_cell_is_minus_1e_3",
          abs(float(coords.min()) + 1e-3) < 1e-12, f"{float(coords.min()):.6e}")
    v, _ = realisability_violation(SC.NONREALISABLE_CELL[None, :, :], tol=SC.TOL)
    check("planted_cell_flagged", bool(v[0]))
    v0, _ = realisability_violation(np.zeros((4, 3, 3)), tol=SC.TOL)
    check("isotropic_not_flagged", int(v0.sum()) == 0)

    # a missing real artefact yields PENDING and NOT BORN, never a silent pass.
    pend = field_control("G0x", "/nonexistent/field", "/tmp", "none")
    check("carve_out_yields_PENDING",
          pend["verdict"] == "PENDING" and pend["born"] is False)

    bad = [n for n, c2, _ in ok if not c2]
    for n, c2, d2 in ok:
        print(f"  [{'ok ' if c2 else 'FAIL'}] {n} {d2}")
    print(f"grade_r4b.py --selftest: {len(ok) - len(bad)}/{len(ok)} "
          f"(optimize={sys.flags.optimize})")
    if bad:
        sys.stderr.write(f"SELFTEST FAILED: {bad}\n")
        return 1
    return 0


# ------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=INSTRUMENT_ROOT)
    ap.add_argument("--config", default="pair")
    ap.add_argument("--cases", default="")
    ap.add_argument("--birth-record", default=BIRTH_RECORD)
    ap.add_argument("--birth-only", action="store_true",
                    help="run the two-sided birth suite (B1-B5) and write the "
                         "birth record; grade nothing")
    ap.add_argument("--grade", action="store_true",
                    help="grade G0-G7; refuses unless the birth record "
                         "verifies and every control the gate needs is born")
    ap.add_argument("--model", default="", help="MODEL.json for B1/B4")
    ap.add_argument("--coverage", default="", help="COVERAGE.md for B1/B4")
    ap.add_argument("--built-case", default="",
                    help="one already-built case tree, for B1/B5")
    ap.add_argument("--out", default=GRADING_OUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    if a.birth_only:
        model = a.model or os.path.join(a.root, "MODEL.json")
        cov = a.coverage or os.path.join(HERE, "COVERAGE.md")
        rec = run_birth(a.root, model, cov, a.built_case or None)
        payload = write_birth_record(rec, a.birth_record)
        v = [rec["B1"]["verdict"], rec["B2"]["verdict"], rec["B5"]["verdict"]]
        print(f"B1 {rec['B1']['verdict']}  "
              f"({rec['B1']['n_fired']}/{rec['B1']['n_refusals']} refusals)")
        print(f"B2 {rec['B2']['verdict']}  "
              f"({rec['B2']['n_born']}/{rec['B2']['n_controls']} controls born "
              f"two-sided)")
        print(f"B5 {rec['B5']['verdict']}")
        print(f"birth record -> {a.birth_record}")
        print(f"record_sha256 = {payload['record_sha256']}")
        return 0 if all(x == "PASS" for x in v) else 1

    if a.grade:
        rec = load_birth_record(a.birth_record)
        cases = [c for c in a.cases.split(",") if c] or None
        out = grade(rec, a.root, a.config, cases)
        write_json(a.out, out)
        print(f"R4b grading verdict: {out['verdict']}")
        for g, v in out["gates"].items():
            print(f"  {g}: {v['verdict']}")
        print(f"  -> {a.out}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
