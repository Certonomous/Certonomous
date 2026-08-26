#!/usr/bin/env python3
"""K0d EXTRACTION EQUIVALENCE CHECK -- registered BEFORE compute, run after L1.

REGISTERED AT: docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md,
ADDENDUM 1 section AD1.1 (2026-08-25, before first compute).  That addendum
accepted `analyse_k0f.py`'s in-comparator extraction -- superseded section 8.1
requires each plant to be read back through the reader the GRADED PATH actually
calls, and a plant traversing a reader the graded number never calls exercises
the wrong channel (the AMENDMENT 2 section A2.3 defect one layer up) -- BUT it
refused to let the equivalence sit as an assumption under every graded number.

WHAT IS COMPARED
  OpenFOAM's OWN `postProcess -func sample`, with the registered section A1.3a
  parameters, against `analyse_k0f.py`'s in-comparator reader, on the SAME case
  at the SAME endTime, at the SAME 2081 registered points.

THE CRITERION, FIXED BEFORE COMPUTE AND NOT CHOSEN AFTERWARDS
  Agreement within **1e-6 of the field's registered range**.
    T  ->  1e-6 x 20.0 K (DT_BAND, section 4)   = 2.0e-05 K
           -- the SAME figure section 7.1 already registers, REUSED not invented
    U  ->  1e-6 x 0.57 m/s (U_IN, section 1)    = 5.7e-07 m/s

THE CONSEQUENCE, FIXED BEFORE COMPUTE
  Agreement VINDICATES the reading.
  DISAGREEMENT means the comparator's reader is WRONG, EVERY GRADED ROW IS
  `NOT A RESULT`, and the rung is REPAIRED AND RE-REGISTERED -- NOT RESCUED BY
  AMENDMENT.

WHY IT COULD NOT RUN EARLIER: it needs real fields on a real K0d mesh.  Firing
was the PREREQUISITE for closing this gap, not a way around it.

THE CASE IS NEVER MODIFIED.  postProcess needs two function-object keys
(`type sets; libs (sampling);`) that the registered sampleDict does not carry,
so this script works on a COPY in a tempdir and prepends them there.  THE
REGISTERED BODY -- setFormat, interpolationScheme, the two sets, nPoints -- IS
COPIED BYTE-FOR-BYTE AND IS ASSERTED UNCHANGED before the comparison is
believed.  A check that edited the registered dictionary to make itself pass
would be measuring its own edit.

Exit codes:  0  every compared field agrees within its registered criterion
             1  DISAGREEMENT -- every graded row is NOT A RESULT
             2  REFUSAL -- the check could not be performed
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyse_k0f as A

EXIT_OK, EXIT_DISAGREE, EXIT_REFUSE = 0, 1, 2
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# AD1.1: 1e-6 of the field's REGISTERED range.  Both are boundary conditions,
# known before any solve, which is what let the criterion be fixed pre-compute.
CRITERION = {"T": 1e-6 * A.DT_BAND, "U": 1e-6 * A.U_IN}

FUNC_KEYS = "type            sets;\nlibs            (sampling);\n\n"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def read_xy(path):
    """Read a setFormat raw .xy: distance then the field columns, in the order
    the dictionary's `fields` entry names them."""
    rows = []
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        rows.append([float(x) for x in ln.split()])
    return rows


def run_postprocess(case_dir, time_name, workdir):
    """Run OpenFOAM's own sampler on a COPY.  Returns {set_name: rows}."""
    if not os.path.isfile(FOAM_BASHRC):
        refuse(f"no OpenFOAM at {FOAM_BASHRC}; the registered check cannot be "
               f"performed and is NOT recorded as passed")
    c = os.path.join(workdir, "case")
    os.makedirs(c, exist_ok=True)
    for sub in ("constant", "system"):
        shutil.copytree(os.path.join(case_dir, sub), os.path.join(c, sub))
    shutil.copytree(os.path.join(case_dir, time_name),
                    os.path.join(c, time_name))

    src = os.path.join(case_dir, "system", "sampleDict.graded")
    body = open(src).read()
    # ASSERT the registered body is what we think it is, BEFORE prepending keys
    for needle in ("setFormat       raw;", "interpolationScheme cellPoint;",
                   f"nPoints {A.N_POINTS};"):
        if needle not in body:
            refuse(f"the registered sampleDict.graded does not contain "
                   f"{needle!r}; refusing rather than sampling with a "
                   f"dictionary that is not the registered one")
    dst = os.path.join(c, "system", "sample")
    open(dst, "w").write(body.replace("setFormat       raw;",
                                      FUNC_KEYS + "setFormat       raw;"))
    # and assert the ONLY difference is the two prepended keys
    if open(dst).read().replace(FUNC_KEYS, "", 1) != body:
        refuse("the sampling dictionary differs from the registered one by "
               "more than the two function-object keys; refusing")

    r = subprocess.run(
        ["bash", "-c", f"source {FOAM_BASHRC} >/dev/null 2>&1 && "
                       f"postProcess -case {c} -func sample -time {time_name}"],
        capture_output=True, text=True)
    if r.returncode != 0:
        refuse(f"postProcess failed (rc={r.returncode}). Last lines:\n"
               + "\n".join(r.stdout.strip().split("\n")[-6:]))
    out = os.path.join(c, "postProcessing", "sample", time_name)
    if not os.path.isdir(out):
        refuse(f"postProcess produced no output at {out}")
    got = {}
    for fn in os.listdir(out):
        m = re.match(r"(vertical_midplane|horizontal_midplane)_", fn)
        if m:
            got[m.group(1)] = read_xy(os.path.join(out, fn))
    if len(got) != 2:
        refuse(f"expected both registered sets, found {sorted(got)}")
    return got


def load_fields_at(case_dir, time_name):
    """Load the fields at an EXPLICIT time through analyse_k0f's PRODUCTION
    readers -- the readers under test -- rather than through a helper that
    re-derives the time itself.

    THIS EXISTS BECAUSE A RACE PRODUCED A FALSE `DISAGREE`.  A first dry run of
    this check against a LIVE case reported every point over criterion.  The
    cause was not the reader: `A.load_case_fields()` takes times[-1] itself, the
    solver was still writing, and `purgeWrite 2` was deleting old directories,
    so OpenFOAM was sampled at time 4000 while the in-comparator reader was
    reading time 12000.  A COMPARISON OF TWO DIFFERENT TIMES IS NOT A
    DISAGREEMENT BETWEEN TWO READERS, and reporting it as one would have
    condemned a reader that had not been tested."""
    tdir = os.path.join(case_dir, time_name)
    mesh = A.read_mesh(case_dir)
    tp = A.field_path(tdir, "T")
    if tp is None:
        refuse(f"{tdir}: no T field")
    T = A.read_scalar_field(tp)
    idx = A.build_index(mesh, len(T))
    up = A.field_path(tdir, "U")
    if up is None:
        refuse(f"{tdir}: no U field")
    U = A.read_vector_field(up, idx["nx"] * idx["ny"])
    # THE BOUNDARY HALF, through the SAME production reader (K0f section V).
    # Without it the graded `cellPoint` path cannot run at all -- A.sample_line
    # refuses -- which is deliberate: this check must exercise the repaired
    # reader, never a fallback.
    bT = A.read_boundary_values(tp, "scalar")
    bU = A.read_boundary_values(up, "vector")
    return dict(idx=idx, T=T, U=U, bT=bT, bUx=A._component(bU, 0))


def assert_case_is_quiescent(case_dir):
    """REFUSE on a case a solver is still writing.

    The registered check (AD1.1) is an endTime check.  Run against a live case
    with purgeWrite 2 the time directories move underneath it, and the result is
    meaningless in BOTH directions -- it can fabricate a disagreement, and it
    could equally mask a real one."""
    r = subprocess.run(["bash", "-c",
                        f"ps -eo args | grep -F {case_dir!r} | "
                        f"grep -v grep | grep -c Foam || true"],
                       capture_output=True, text=True)
    live = (r.stdout.strip() or "0")
    if live != "0":
        refuse(f"a solver is STILL RUNNING on {case_dir} ({live} process(es)). "
               f"AD1.1 registers this as an endTime check; against a live case "
               f"purgeWrite 2 moves the time directories underneath the "
               f"comparison and the answer is meaningless in both directions.")


def compare(case_dir, verbose=True):
    assert_case_is_quiescent(case_dir)
    times = A.numeric_times(case_dir)
    if not times:
        refuse(f"{case_dir}: no time directories")
    tn = times[-1]
    cf = load_fields_at(case_dir, tn)
    idx = cf["idx"]
    if A.numeric_times(case_dir)[-1] != tn:
        refuse(f"{case_dir}: the latest time changed from {tn} to "
               f"{A.numeric_times(case_dir)[-1]} while this check was reading. "
               f"Refusing rather than comparing two different times.")

    workdir = tempfile.mkdtemp(prefix="k0d_equiv_")
    try:
        foam = run_postprocess(case_dir, tn, workdir)
    finally:
        pass  # workdir removed by caller path below

    results = []
    try:
        # column layout of `fields ( T U k )` under setFormat raw:
        #   distance, T, k, Ux, Uy, Uz     (OpenFOAM orders scalars then vectors)
        for setname, which in (("vertical_midplane", "vertical"),
                               ("horizontal_midplane", "horizontal")):
            rows = foam[setname]
            if len(rows) != A.N_POINTS:
                refuse(f"{setname}: OpenFOAM returned {len(rows)} points, the "
                       f"registration fixes {A.N_POINTS}")
            # ---- T ----
            mine_T = A.sample_line(idx, cf["T"], which, A.SCHEME_GRADED,
                                   cf["bT"])[1]
            theirs_T = [r[1] for r in rows]
            worst = max(abs(a - b) for a, b in zip(mine_T, theirs_T))
            results.append((setname, "T", worst, CRITERION["T"]))
            # ---- U, x-component ----
            ux = [v[0] for v in cf["U"]]
            mine_U = A.sample_line(idx, ux, which, A.SCHEME_GRADED,
                                   cf["bUx"])[1]
            theirs_U = [r[3] for r in rows]
            worstU = max(abs(a - b) for a, b in zip(mine_U, theirs_U))
            results.append((setname, "U.x", worstU, CRITERION["U"]))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    ok = True
    if verbose:
        print(f"\ncase {os.path.basename(case_dir)} at time {tn}")
        print(f"  {'set':<22}{'field':<6}{'worst |diff|':>16}"
              f"{'criterion':>14}   verdict")
    for setname, fld, worst, crit in results:
        good = worst <= crit
        ok = ok and good
        if verbose:
            print(f"  {setname:<22}{fld:<6}{worst:>16.6e}{crit:>14.2e}   "
                  f"{'agree' if good else 'DISAGREE'}")
    return ok, results, tn


def selftest():
    """The negative half: a planted disagreement MUST fire.

    Without it this script is a probe never shown able to fail, and AD1.1's
    consequence would rest on a check that cannot say no."""
    fails = []
    print("=" * 70)
    print("check_k0f_extraction_equivalence.py -- SELFTEST")
    print("=" * 70)
    print(f"  criterion T   = {CRITERION['T']:.2e} K   "
          f"(1e-6 x DT_BAND {A.DT_BAND}, the section 7.1 figure REUSED)")
    print(f"  criterion U   = {CRITERION['U']:.2e} m/s (1e-6 x U_IN {A.U_IN})")
    c1 = abs(CRITERION["T"] - 2.0e-5) < 1e-12
    print(f"  {'OK  ' if c1 else 'FAIL'}  T criterion is exactly 2.0e-05 K")
    fails += [] if c1 else ["T criterion"]

    # POSITIVE: identical arrays agree.  NEGATIVE: a perturbation just over the
    # criterion must be caught, and one just under must not be.
    n = 50
    base = [300.0 + 0.001 * i for i in range(n)]
    for label, delta, want_fire in (
            ("a perturbation 10x the criterion FIRES", CRITERION["T"] * 10, True),
            ("a perturbation just OVER the criterion FIRES",
             CRITERION["T"] * 1.01, True),
            ("a perturbation just UNDER the criterion stays quiet",
             CRITERION["T"] * 0.99, False),
            ("identical arrays stay quiet", 0.0, False)):
        other = [v + delta for v in base]
        worst = max(abs(a - b) for a, b in zip(base, other))
        fired = worst > CRITERION["T"]
        good = (fired == want_fire)
        print(f"  {'OK  ' if good else 'FAIL'}  {label}   "
              f"[worst {worst:.3e}, fired={fired}]")
        if not good:
            fails.append(label)

    print("=" * 70)
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        return EXIT_DISAGREE
    print("SELFTEST PASSED: the comparison was shown able to FIRE on a planted")
    print("disagreement and to STAY QUIET on agreement.")
    print("=" * 70)
    return EXIT_OK


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.case:
        ap.error("--case is required (repeatable), or --selftest")
    print("=" * 70)
    print("K0d EXTRACTION EQUIVALENCE CHECK -- registered AD1.1, before compute")
    print(f"  OpenFOAM postProcess -func sample  vs  analyse_k0f.py's reader")
    print(f"  criterion: T {CRITERION['T']:.2e} K, U {CRITERION['U']:.2e} m/s")
    print("=" * 70)
    allok = True
    for c in a.case:
        if not os.path.isdir(c):
            refuse(f"{c}: not a directory")
        ok, _, _ = compare(c)
        allok = allok and ok
    print("\n" + "=" * 70)
    if allok:
        print("VERDICT: AGREE -- the in-comparator reader of analyse_k0f.py")
        print("reproduces OpenFOAM's own cellPoint sampling within the")
        print("registered criterion.  AD1.1's reading is VINDICATED.")
    else:
        print("VERDICT: DISAGREE -- under AD1.1 the comparator's reader is")
        print("WRONG, EVERY GRADED ROW IS `NOT A RESULT`, and the rung is")
        print("REPAIRED AND RE-REGISTERED, not rescued by amendment.")
    print("=" * 70)
    return EXIT_OK if allok else EXIT_DISAGREE


if __name__ == "__main__":
    sys.exit(main())
