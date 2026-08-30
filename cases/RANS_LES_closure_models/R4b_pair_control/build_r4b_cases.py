#!/usr/bin/env python3
"""R4b instrument A3 - build the propagation cases, and enforce the freeze order.

Builds the 12 pair-control propagation cases by calling
`R4_sparta_build/build_aposteriori.build()` **unmodified** with the `xi`-scaled
term sets of `MODEL.json`.

ORDER A, the RUNTIME freeze order (`R4b/PREREGISTRATION.md` sec. 3.5), is not a
convention this module follows -- it is a property this module ENFORCES, and
`INSTRUMENT_BUILD_PREREGISTRATION.md` B4 grades whether it does:

    select_control.py writes MODEL.md/MODEL.json
      -> those two are COMMITTED
        -> only then may this module run.

**No propagation case can be built before the control value is on the record.**

REGISTERED REFUSALS (sec. 2.2), each an explicit `SystemExit(2)`, NEVER an
`assert` (L-332: `python3 -O` deletes `assert`).  ZERO `ast.Assert` nodes in
this file; `--selftest` proves it by parsing its own source.

  MODEL-ABSENT      no `MODEL.json`
  MODEL-FROZEN-AT   a `MODEL.json` carrying no `frozen_at` timestamp
  MODEL-HASH        a `MODEL.json` whose sha256 differs from the committed blob
  COVERAGE-ABSENT   no `COVERAGE.md` (R4b sec. 9, the FS2/FS5 discharge)
  CASE-TREE-EXISTS  an existing case tree at the destination
  TERM-ORDER        any term registered with `n` outside (1,2,3)
  SOLVE-ROOT-GUARD  any write inside `/home/ubuntu/closure-data/r4b/`

CASE-TREE-EXISTS IS LOAD-BEARING AND MUST RUN FIRST.  `r4_lib.copy_skeleton`
opens with `shutil.rmtree(dst)` -- calling `build()` over an existing tree does
not fail, it DELETES the tree.  R4b sec. 4.3: "A guard refuses a case whose
destination directory already holds a `0/` or a numeric time directory. No run
is resumed in place, restarted in place, or re-graded after the fact."  The
guard therefore runs BEFORE `build()` is called, never after.

STANDING RULE 14 - a lesson is not applied until EVERY call site asserts it.
Two are re-asserted here, at this new call site:

  * `n in (1,2,3)`.  `kOmegaSSTSparta` implements T1, T2 and T3 only and would
    silently evaluate a term registered with `n = 4` AS T3 -- a wrong model
    that runs, converges and reports a number.  `build_aposteriori.main()`
    carries this check, but `main()` is NOT re-used (R4b sec. 9 says so
    explicitly), so the check does not travel with `build()`.  Re-asserted
    below as a refusal that survives `-O`.
  * L-221/L-222, the `libs` entry.  `r4_lib.set_libs` inserts-or-replaces and
    then asserts the library name is present.  It matters in BOTH directions
    in this corpus: the hills carry **no `libs` line at all**, so a bare
    `str.replace` is a silent no-op and the solve then returns the BASELINE
    field, which looks like a physical answer; the ducts, `CBFS13700` and
    `PHLL10595` carry one naming `libfrozenIncompressibleTurbulenceModels.so`,
    which exists nowhere on this machine.  `set_libs`' own guarantee is a bare
    `assert` in a frozen file, so this call site re-checks the bytes on disk
    explicitly.

sec. 3.1, quoted, because it decides what is written into the case: "R4's
FS4-frozen term sets, unchanged in form and in relative coefficient, with ONE
scalar `xi` multiplying EVERY coefficient of BOTH targets."  Both term sets are
therefore taken already-scaled from `MODEL.json`.
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

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(CLOSURE))
sys.path.insert(0, os.path.join(CLOSURE, "R4_sparta_build"))
sys.path.insert(0, os.path.join(CLOSURE, "_common"))

import r4_lib as R                          # noqa: E402
import build_aposteriori as BA              # noqa: E402

INSTRUMENT_ROOT = "/home/ubuntu/closure-data/r4b_instruments"
SOLVE_ROOT = "/home/ubuntu/closure-data/r4b"
MODEL_JSON = os.path.join(HERE, "MODEL.json")
COVERAGE_MD = os.path.join(HERE, "COVERAGE.md")
CONFIG = "pair"                             # the one pair-control arm
LEGAL_N = (1, 2, 3)                         # kOmegaSSTSparta implements T1-T3
SPARTA_LIB = R.SPARTA_LIB                   # libspartaTurbulenceModels.so


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
            f"{p} is inside R4b's solve run root {SOLVE_ROOT}; writing there "
            f"would destroy R4b's pre-compute condition")
    return p


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def committed_sha256(path, ref="HEAD"):
    """sha256 of the COMMITTED blob at `path`, or None if it is not tracked.

    ORDER A's whole content is that the control value is on the record before
    any case is built, so "the committed blob" is resolved from git, not from
    the working tree.  A file that is present but untracked returns None and
    the caller refuses.
    """
    rel = os.path.relpath(os.path.abspath(path), REPO)
    try:
        blob = subprocess.run(["git", "-C", REPO, "cat-file", "blob",
                               f"{ref}:{rel}"],
                              capture_output=True, check=False)
    except OSError:
        return None
    if blob.returncode != 0:
        return None
    return hashlib.sha256(blob.stdout).hexdigest()


# ------------------------------------------------- ORDER A, mechanically
def check_freeze_order(model_path, coverage_path, expect_sha=None, ref="HEAD"):
    """R4b sec. 3.5 + sec. 9. Returns the loaded model. Refuses, never warns."""
    require(os.path.exists(model_path), "MODEL-ABSENT",
            f"{model_path} does not exist. R4b sec. 3.5: no propagation case "
            f"can be built before the control value is on the record.")
    try:
        model = json.load(open(model_path))
    except ValueError as e:
        refuse("MODEL-ABSENT", f"{model_path} is not readable JSON: {e}")

    require(bool(model.get("frozen_at")), "MODEL-FROZEN-AT",
            f"{model_path} carries no `frozen_at` timestamp; an unfrozen model "
            f"is not on the record.")

    disk = sha256_file(model_path)
    want = expect_sha or committed_sha256(model_path, ref)
    require(want is not None, "MODEL-HASH",
            f"{model_path} is not committed at {ref} and no --model-sha256 was "
            f"given. ORDER A requires the control value to be on the record "
            f"BEFORE any case is built; an uncommitted model is not on it.")
    require(disk == want, "MODEL-HASH",
            f"{model_path} sha256 {disk} != the committed blob {want}. The "
            f"file that would be built from is not the file that was frozen.")

    require(os.path.exists(coverage_path), "COVERAGE-ABSENT",
            f"{coverage_path} does not exist. R4b sec. 9 makes a present "
            f"COVERAGE.md (the FS2/FS5 discharge) a precondition of building.")
    return model, dict(model_path=os.path.abspath(model_path),
                       model_sha256=disk, expected_sha256=want,
                       expected_source=("--model-sha256" if expect_sha
                                        else f"git blob {ref}"),
                       frozen_at=model["frozen_at"],
                       coverage_path=os.path.abspath(coverage_path),
                       coverage_sha256=sha256_file(coverage_path))


def check_terms(rterms, bterms):
    """Standing rule 14, re-asserted AT THIS CALL SITE.

    `build_aposteriori.main()` carries this check but main() is not re-used, so
    without this the check does not travel with `build()`.  A refusal, not an
    `assert`: `python3 -O` would delete an assert and let an `n = 4` term be
    written into a case that then runs, converges, and reports a number for a
    model nobody registered.
    """
    for label, ts in (("R", rterms), ("bDelta", bterms)):
        for t in ts:
            require(len(t) == 4, "TERM-ORDER",
                    f"{label} term {t!r} is not (n, p, q, c)")
            require(int(t[0]) in LEGAL_N, "TERM-ORDER",
                    f"{label} term {t!r} registers n = {int(t[0])}. "
                    f"kOmegaSSTSparta implements T1, T2, T3 only and would "
                    f"SILENTLY evaluate it as T3 (R4 sec. 1).")
    return dict(legal_n=list(LEGAL_N), n_R_terms=len(rterms),
                n_bDelta_terms=len(bterms),
                n_values_seen=sorted({int(t[0]) for t in rterms + bterms}))


# ------------------------------------------------------------- L-221/L-222
def libs_shape(control_dict_path):
    """What `libs` shape a controlDict carries, BEFORE anything touches it."""
    s = open(control_dict_path).read()
    tops = re.findall(r"^\s*libs\s*\(([^;]*)\);\s*$", s, flags=re.M)
    return dict(path=os.path.abspath(control_dict_path),
                has_libs_line=bool(tops),
                n_top_level_libs_entries=len(tops),
                names=[t.strip() for t in tops],
                sparta_present=SPARTA_LIB in s)


def apply_set_libs(control_dict_path):
    """`r4_lib.set_libs` at the new call site, then re-check the BYTES.

    `set_libs` ends in a bare `assert` -- deleted by `-O`.  The explicit checks
    below are the same guarantee in a form `-O` cannot erase, and they read the
    file back from disk rather than trusting the return value.
    """
    before = libs_shape(control_dict_path)
    R.set_libs(control_dict_path)
    s = open(control_dict_path).read()
    tops = re.findall(r"^\s*libs\s*\(([^;]*)\);\s*$", s, flags=re.M)
    require(SPARTA_LIB in s, "LIBS",
            f"L-221: the libs entry did not land in {control_dict_path}. On a "
            f"case carrying no libs line a bare replace is a silent no-op and "
            f"the solve returns the BASELINE field, which looks physical.")
    require(len(tops) == 1, "LIBS",
            f"L-222: {len(tops)} top-level libs entries in "
            f"{control_dict_path}; a duplicate is the signature of a blind "
            f"append.")
    require(SPARTA_LIB in tops[0], "LIBS",
            f"the single top-level libs entry does not name {SPARTA_LIB}: "
            f"{tops[0].strip()!r}")
    return dict(before=before, after=libs_shape(control_dict_path),
                shape=("no-libs-line" if not before["has_libs_line"]
                       else "libs-line-naming-" + ",".join(before["names"])))


def verify_set_libs_both_shapes(scratch):
    """B4's positive half, the `set_libs` clause, on BOTH REAL shapes.

    Not synthetic: a real hill controlDict (which carries no `libs` line at
    all) and a real duct controlDict (which carries one naming a library that
    exists nowhere on this machine).  Each is copied to scratch and put through
    the real `set_libs`.
    """
    guard_write_root(scratch)
    os.makedirs(scratch, exist_ok=True)
    byname = {c: (p, f) for c, p, f in R.training_cases()}
    out = {}
    for label, case in (("hills", "alpha_125"), ("ducts", "AR_1_Ret_180")):
        src, _fam = byname[case]
        cd = os.path.join(src, "system", "controlDict")
        require(os.path.exists(cd), "LIBS-ARTEFACT",
                f"PENDING: {cd} - no real controlDict of shape {label!r}")
        dst = os.path.join(scratch, f"controlDict_{label}")
        shutil.copy(cd, dst)
        out[label] = dict(case=case, real_source=os.path.abspath(cd),
                          **apply_set_libs(dst))
    require(out["hills"]["before"]["has_libs_line"] is False, "LIBS-SHAPE",
            "the hill case used for the demonstration already carries a libs "
            "line; the no-libs-line shape is then not exercised at all")
    require(out["ducts"]["before"]["has_libs_line"] is True, "LIBS-SHAPE",
            "the duct case used for the demonstration carries no libs line; "
            "the replace shape is then not exercised at all")
    out["both_shapes_exercised"] = True
    return out


# ------------------------------------------------------------------ build
def existing_tree(dst):
    """R4b sec. 4.3: a `0/` or any numeric time directory means DO NOT TOUCH."""
    if not os.path.isdir(dst):
        return None
    kids = sorted(os.listdir(dst))
    times = [k for k in kids
             if re.fullmatch(r"[0-9]+(\.[0-9]+)?", k)
             and os.path.isdir(os.path.join(dst, k))]
    if times:
        return times
    return kids or ["<empty directory>"]


def build_cases(out_root, model, cases, config=CONFIG, dry_run=False):
    """Call `build_aposteriori.build()` UNMODIFIED, into `out_root`.

    `build()`'s destination is `build_aposteriori.OUT`, a module global that
    points at R4's own run root.  It is REBOUND here, from the caller, so the
    function's code is untouched and its output lands in this build's root.
    R4b needs exactly this rebinding for its own solve arm too: its cases live
    under `/home/ubuntu/closure-data/r4b/`, not under R4's `aposteriori/`.
    """
    out_root = guard_write_root(out_root)
    rterms = [tuple(t) for t in model["R_terms_scaled"]]
    bterms = [tuple(t) for t in model["bDelta_terms_scaled"]]
    terms_info = check_terms(rterms, bterms)

    byname = {c: (p, f) for c, p, f in R.training_cases()}
    # The destination guard runs over EVERY case BEFORE any build, because
    # copy_skeleton deletes what it finds.  One existing tree stops the batch.
    for case in cases:
        require(case in byname, "CASE-UNKNOWN",
                f"{case} is not one of R4's registered training cases")
        found = existing_tree(os.path.join(out_root, case, config))
        require(found is None, "CASE-TREE-EXISTS",
                f"{os.path.join(out_root, case, config)} already exists and "
                f"holds {found}. R4b sec. 4.3: no run is resumed in place, "
                f"restarted in place, or re-graded after the fact -- and "
                f"copy_skeleton would DELETE it.")
    R.assert_no_test_case(cases)
    zero_shot(cases)

    if dry_run:
        return dict(dry_run=True, terms=terms_info, cases=list(cases),
                    out_root=out_root, config=config)

    saved = BA.OUT
    built = []
    try:
        BA.OUT = out_root                    # module global, function untouched
        os.makedirs(out_root, exist_ok=True)
        for case in cases:
            src, family = byname[case]
            rec = BA.build(case, src, family, config, list(rterms),
                           list(bterms))
            cd = os.path.join(rec["dir"], "system", "controlDict")
            rec["libs"] = apply_set_libs(cd)       # L-221 at the new call site
            rec["source_controlDict"] = os.path.join(src, "system",
                                                     "controlDict")
            rec["source_libs_shape"] = libs_shape(rec["source_controlDict"])
            built.append(rec)
            print(f"[built] {case:22s} {config:8s} cap={rec['cap']} "
                  f"libs={rec['libs']['shape']}", flush=True)
    finally:
        BA.OUT = saved

    manifest = dict(
        built_at=utcnow(), out_root=out_root, config=config,
        builder=os.path.abspath(__file__),
        builder_sha256=sha256_file(os.path.abspath(__file__)),
        build_aposteriori_sha256=sha256_file(BA.__file__.rstrip("c")),
        terms=terms_info,
        R_terms_scaled=model["R_terms_scaled"],
        bDelta_terms_scaled=model["bDelta_terms_scaled"],
        xi_star=model.get("xi_star"), cases=built)
    mf = guard_write_root(os.path.join(out_root, "build_manifest.json"))
    with open(mf, "w") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    return manifest


def zero_shot(cases):
    """G0f re-asserted here so `-O` cannot erase it (r4_lib's is a bare assert)."""
    bad = sorted(set(cases) & (R.TEST_CASES | R.VAL_CASES))
    require(not bad, "ZERO-SHOT",
            f"ZERO-SHOT VIOLATION: test/validation case in build set: {bad}")


# --------------------------------------------------------------- selftest
def _selftest():
    import tempfile
    ok = []

    def check(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    def refused(fn, code_expected=2):
        try:
            fn()
            return False, "did not refuse"
        except SystemExit as e:
            return e.code == code_expected, f"code={e.code}"

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    check("zero_ast_assert_nodes", n_assert == 0, f"count={n_assert}")

    check("legal_n_is_123", LEGAL_N == (1, 2, 3))
    check("build_aposteriori_imported", hasattr(BA, "build"))
    check("build_out_is_a_module_global", isinstance(BA.OUT, str))

    c, d = refused(lambda: guard_write_root(os.path.join(SOLVE_ROOT, "x")))
    check("solve_root_guard", c, d)

    with tempfile.TemporaryDirectory() as td:
        # MODEL-ABSENT
        c, d = refused(lambda: check_freeze_order(
            os.path.join(td, "nope.json"), os.path.join(td, "COVERAGE.md")))
        check("refusal_MODEL_ABSENT", c, d)

        mj = os.path.join(td, "MODEL.json")
        cov = os.path.join(td, "COVERAGE.md")
        open(cov, "w").write("# coverage\n")

        # MODEL-FROZEN-AT
        json.dump({"xi_star": 0.05}, open(mj, "w"))
        c, d = refused(lambda: check_freeze_order(mj, cov, expect_sha="x" * 64))
        check("refusal_MODEL_FROZEN_AT", c, d)

        # MODEL-HASH (a sha that is not the file's)
        json.dump({"xi_star": 0.05, "frozen_at": utcnow()}, open(mj, "w"))
        c, d = refused(lambda: check_freeze_order(mj, cov, expect_sha="0" * 64))
        check("refusal_MODEL_HASH", c, d)

        # MODEL-HASH, the uncommitted branch: no expect_sha, not tracked
        c, d = refused(lambda: check_freeze_order(mj, cov))
        check("refusal_MODEL_HASH_uncommitted", c, d)

        # the positive: the true sha passes and returns the model
        good = sha256_file(mj)
        try:
            m, info = check_freeze_order(mj, cov, expect_sha=good)
            check("freeze_order_positive",
                  info["model_sha256"] == good and m["xi_star"] == 0.05)
        except SystemExit as e:
            check("freeze_order_positive", False, f"refused code={e.code}")

        # COVERAGE-ABSENT
        os.remove(cov)
        c, d = refused(lambda: check_freeze_order(mj, cov, expect_sha=good))
        check("refusal_COVERAGE_ABSENT", c, d)

        # CASE-TREE-EXISTS, through the real guard
        dst = os.path.join(td, "root", "alpha_125", CONFIG)
        os.makedirs(os.path.join(dst, "0"))
        check("existing_tree_sees_zero_dir",
              existing_tree(dst) == ["0"], repr(existing_tree(dst)))
        check("existing_tree_none_when_absent",
              existing_tree(os.path.join(td, "root", "nothing", CONFIG)) is None)
        c, d = refused(lambda: build_cases(
            os.path.join(td, "root"),
            {"R_terms_scaled": [[1, 0, 0, 1.0]],
             "bDelta_terms_scaled": [[2, 0, 0, 1.0]]},
            ["alpha_125"], dry_run=True))
        check("refusal_CASE_TREE_EXISTS", c, d)

    # TERM-ORDER, both halves: n = 4 refuses, n in (1,2,3) does not.
    c, d = refused(lambda: check_terms([(1, 0, 0, 1.0)], [(4, 0, 0, 1.0)]))
    check("refusal_TERM_ORDER_n4", c, d)
    c, d = refused(lambda: check_terms([(0, 0, 0, 1.0)], []))
    check("refusal_TERM_ORDER_n0", c, d)
    try:
        info = check_terms([(1, 0, 0, 1.0)], [(2, 0, 1, -1.0), (3, 0, 0, 2.0)])
        check("terms_positive", info["n_values_seen"] == [1, 2, 3])
    except SystemExit as e:
        check("terms_positive", False, f"refused code={e.code}")

    # ZERO-SHOT, both halves, at THIS call site (survives -O).
    c, d = refused(lambda: zero_shot(["PHLL10595", "NASA_2DWMH"]))
    check("refusal_ZERO_SHOT", c, d)
    try:
        zero_shot(["PHLL10595", "CBFS13700"])
        check("zero_shot_silent_on_clean", True)
    except SystemExit:
        check("zero_shot_silent_on_clean", False, "refused a clean list")

    bad = [n for n, c2, _ in ok if not c2]
    for n, c2, d2 in ok:
        print(f"  [{'ok ' if c2 else 'FAIL'}] {n} {d2}")
    print(f"build_r4b_cases.py --selftest: {len(ok) - len(bad)}/{len(ok)} "
          f"(optimize={sys.flags.optimize})")
    if bad:
        sys.stderr.write(f"SELFTEST FAILED: {bad}\n")
        return 1
    return 0


# ------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default=MODEL_JSON)
    ap.add_argument("--coverage", default=COVERAGE_MD)
    ap.add_argument("--model-sha256", default="",
                    help="the committed blob's sha256; default: resolved from "
                         "git at --ref")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--out-root", default=INSTRUMENT_ROOT)
    ap.add_argument("--cases", default="")
    ap.add_argument("--config", default=CONFIG)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify-set-libs", action="store_true",
                    help="B4: exercise set_libs on BOTH real shapes and report")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    out_root = guard_write_root(a.out_root)
    if a.verify_set_libs:
        rep = verify_set_libs_both_shapes(
            os.path.join(out_root, "birth", "build_r4b_cases"))
        print(json.dumps(rep, indent=1))
        return 0

    model, freeze = check_freeze_order(a.model, a.coverage,
                                       a.model_sha256 or None, a.ref)
    cases = [c for c in a.cases.split(",") if c]
    if not cases:
        cases = sorted(json.load(open(os.path.join(
            os.path.join(R.WORK, "dataset"), "dataset_manifest.json")))["cases"])
    man = build_cases(out_root, model, cases, a.config, a.dry_run)
    man["freeze_order"] = freeze
    print(f"\n{len(man.get('cases', []))} propagation cases -> {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
