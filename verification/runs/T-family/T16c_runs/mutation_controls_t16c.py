#!/usr/bin/env python3
"""Mutation controls for `analyse_t16c.py` -- one control per selftest limb.

WHY THIS FILE EXISTS.  `analyse_t16c.py --selftest` prints 40 green limbs.  A
green limb proves nothing on its own: a limb that cannot go red is not a test,
it is a decoration.  This harness breaks ONE thing at a time in a SCRATCH COPY
of the comparator and MEASURES which limbs turn red.  A limb with no control
that reddens it is NOT VERIFIED, and this file names those explicitly rather
than quietly reporting 40/40.

METHOD, and every clause of it is load-bearing:

  1. The comparator is COPIED into a scratch directory.  The original is never
     edited.  `_find_repo()` falls back to the registered absolute path, so the
     copy still loads the REAL frozen instruments under the section 5 pin --
     and is still stopped by S8a, which is the point of the fallback.
  2. ONE exact string replacement is applied, and the harness REFUSES if the
     old text does not occur EXACTLY ONCE.  A mutation that silently matched
     zero or two sites would produce a meaningless matrix.
  3. `__pycache__` is cleared before every run.  Stale bytecode has INVERTED
     mutation tests in this lab -- a clean control failing while the mutated
     case passes -- and `PYTHONDONTWRITEBYTECODE` does not fix it.
  4. The mutant's `--selftest` is run and its `[ok ]` / `[FAIL]` lines parsed
     into a set of red limbs.
  5. THE UNMUTATED CONTROL RUNS FIRST and must be 0 red.  A harness that has
     not been shown to report green on an unbroken file cannot be believed when
     it reports red on a broken one -- this is standing rule 3's shape applied
     to the harness itself.

NOTHING HERE TOUCHES THE LIVE RUN TREE.  Every mutant is driven by
`--selftest`, whose every limb runs against a synthetic forge, and whose S8a/
S8b/S8c apparatus refuses and MEASURES any attempt on the live tree.  The
harness additionally fingerprints `T16_runs` (path + mtime + size) before and
after the whole sweep and REFUSES if one byte of it moved.

EXPECTATION VOCABULARY.  `expect` is the limb set this control is AIMED at.
The harness reports the MEASURED set beside it and classifies:

  EXACT      measured == expected: the control reddens that limb and no other.
  SUPERSET   measured strictly contains expected -- disclosed, not hidden.
             Several limbs share one instrument on purpose (the C_TRANSPOSE
             limbs, the S8a limbs), and a mutation to that instrument reddens
             the family.  That is a true statement about the coupling.
  ABORT      the mutation is caught by a guard that stops the run before the
             limbs print.  This is a REFUSAL, which is the behaviour standing
             rule 4 asks for -- it is recorded as reddening, and named.
  MISS       measured does not contain expected: THE LIMB IS NOT VERIFIED by
             this control and the harness says so in the summary.

Exit 0 if every limb in the union of the expectations was reddened by at least
one control; 1 otherwise.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "analyse_t16c.py")
PARENT = os.path.abspath(os.path.join(HERE, "..", "T16_runs"))

ALL_LIMBS = ["L%02d" % i for i in range(1, 41)]

# ---------------------------------------------------------------------------
# THE MUTATIONS.  (id, aimed-at limbs, what is broken and why that is the right
# break for that limb, old source, new source)
# ---------------------------------------------------------------------------
MUTATIONS = [
    ("M01", ["L01"],
     "the referent's Route B verification is forced to report a failure",
     '        r, f = EX.verify(quiet=True)',
     '        r, f = None, ["MUTANT: forced referent failure"]'),

    ("M02", ["L02"],
     "load_registered stops comparing the registered Roache floors with the "
     "imported ones (MESH_STANDARD 10.5: one name, one number)",
     '    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN:',
     '    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR and False:'),

    ("M03", ["L03"],
     "load_registered stops checking that this comparator's carried-over floors "
     "ARE the registered ones, so a relaxed W1 floor_T would pass",
     '        if want is None or got != want:',
     '        if want is None and False:'),

    ("M04", ["L04"],
     "the section 5 pin stops refusing on a digest mismatch -- a moved gate "
     "would then grade quietly instead of failing closed",
     '    if got != want:\n        refuse(',
     '    if got != want and False:\n        refuse('),

    ("M05", ["L05"],
     "REG_SHA256 is set to a digest the frozen registration does not have",
     'REG_SHA256 = "aead91aaab8480f6a4321a3d9eb01536d9ceb4cbfb7a3774426cea608ae72845"',
     'REG_SHA256 = "0000000000000000000000000000000000000000000000000000000000000000"'),

    ("M06", ["L06"],
     "apply_gate stops turning a non-CONVERGING triple into NOT A RESULT "
     "(standing rule 5 clause 2)",
     '    if not exact_class and tr["state"] != "CONVERGING":',
     '    if not exact_class and False and tr["state"] != "CONVERGING":'),

    ("M07", ["L07"],
     "gci_equal is wrapped so it reports a GCI on every triple, including "
     "non-monotone ones (standing rule 5: never quote a GCI there)",
     'from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, monotone    # noqa: E402',
     'from roache_triple import STAGNANT_FLOOR, P_MIN, FS, monotone               # noqa: E402\n'
     'from roache_triple import gci_equal as _gci_real                            # noqa: E402\n'
     'def gci_equal(*a, **k):\n'
     '    _t = dict(_gci_real(*a, **k))\n'
     '    _t.setdefault("GCI_pct", 1.0)\n'
     '    if _t.get("GCI_pct") is None:\n'
     '        _t["GCI_pct"] = 1.0\n'
     '    return _t'),

    ("M08", ["L08"],
     "apply_gate stops exempting EXACT-class rows, so a row whose floor IS its "
     "verdict is misgraded as NOT A RESULT",
     '    if not exact_class and tr["state"] != "CONVERGING":',
     '    if tr["state"] != "CONVERGING":'),

    ("M09", ["L09"],
     "the graded reader G1 is scaled by 1 + 1e-6, which is invisible to every "
     "gate but breaks agreement with the 1-D discrete model at 1e-12",
     '    out["G1"] = EX.lagrange4(Y, vrow, EX.Y_STAR)',
     '    out["G1"] = EX.lagrange4(Y, vrow, EX.Y_STAR) * (1.0 + 1.0e-6)'),

    ("M10", ["L10"],
     "select_station keeps overwriting, so it returns the LARGEST candidate row "
     "reaching the floor instead of section 4's SMALLEST",
     '        if chosen is None and w <= STATION_FLOOR_T:',
     '        if w <= STATION_FLOOR_T:'),

    ("M11", ["L11"],
     "the section 4 UNREACHABLE branch fabricates a value instead of recording "
     "none -- a value invented for the record is what the branch exists to refuse",
     '                         value_fine=None, triple=None, triple_state=None,',
     '                         value_fine=0.0, triple=None, triple_state=None,'),

    ("M12", ["L12"],
     "the section 4 THREE-LEVEL CONSISTENCY clause is forced true, so a triple "
     "built at three different physical locations would be graded",
     '            ok = bool(in_cand and w is not None and w <= STATION_FLOOR_T)',
     '            ok = True'),

    ("M13", ["L13", "L15"],
     "C_TRANSPOSE is compared against 2.0 at its use site, so the -1.0 "
     "signature of a transposed ordering no longer fires the guard",
     '        ct[lv] = dict(value=v, ok=abs(v) <= C_TRANSPOSE_TOL,',
     '        ct[lv] = dict(value=v, ok=abs(v) <= 2.0,'),

    ("M14", ["L13"],
     "the REGISTERED constant C_TRANSPOSE_TOL is moved off 0.5 -- this must be "
     "stopped structurally by _station_floor_identity_check, not merely noticed",
     'C_TRANSPOSE_TOL = 0.5',
     'C_TRANSPOSE_TOL = 2.0'),

    ("M15", ["L14"],
     "the ordering statistic is offset by +0.9, so a perfectly good untransposed "
     "row fires the guard (the NEGATIVE arm of section 2)",
     '    out["T_slope_rel"] = (slope / (-dT)) - 1.0',
     '    out["T_slope_rel"] = (slope / (-dT)) - 1.0 + 0.9'),

    ("M16", ["L15"],
     "THE D576 REGRESSION ITSELF: the C_TRANSPOSE refusal is moved ABOVE the "
     "witness block, restoring exactly the shape that made W1_T unreachable in "
     "analyse_t16.py -- the guard fires on physics and destroys the diagnosis",
     '    # ---- (ii) THE WITNESSES, ALL THREE LEVELS, BEFORE ANY GUARD -------------',
     '    for _lv in LEVELS:\n'
     '        _rr = readers(os.path.join(root, CASES[_lv]), times[_lv][-1], idents[_lv])\n'
     '        if abs(_rr["T_slope_rel"]) > C_TRANSPOSE_TOL:\n'
     '            refuse("C_TRANSPOSE (MUTANT: moved above the witness block)")\n'
     '    # ---- (ii) THE WITNESSES, ALL THREE LEVELS, BEFORE ANY GUARD -------------'),

    ("M17", ["L16"],
     "the W1 development gate is forced ok, so an undeveloped station grades",
     '        c["W1_ok"] = (r["W1_v_max"] <= W1_FLOOR_V and r["W1_g_max"] <= W1_FLOOR_G\n'
     '                      and r["W1_T_max"] <= W1_FLOOR_T)',
     '        c["W1_ok"] = True'),

    ("M18", ["L17"],
     "C_CONV stops reporting any residual above the registered floor",
     '    bad = [f for f in gated if worst[f] > CONV_FLOOR]',
     '    bad = []'),

    ("M19", ["L18"],
     "C_PLAT is forced ok, so a G1 still moving between the last two writes grades",
     '        c["plateau_ok"] = plat <= PLAT_FLOOR',
     '        c["plateau_ok"] = True'),

    ("M20", ["L19"],
     "C_MASS is forced ok, so a station row not carrying the registered mean grades",
     '        c["mass_ok"] = r["mass_dev"] <= MASS_FLOOR',
     '        c["mass_ok"] = True'),

    ("M21", ["L20"],
     "C_REV is forced ok, so a reversed cell on the graded row grades",
     '                         ("C_MASS", c["mass_ok"]), ("C_REV", c["reversed_cells"] == 0)):',
     '                         ("C_MASS", c["mass_ok"]), ("C_REV", True)):'),

    ("M22", ["L21"],
     "read_field fabricates a uniform field instead of refusing one -- the "
     "solver wrote no solution and the reader invents one",
     '        if re.search(r"internalField\\s+uniform", "\\n".join(lines[:40])):\n'
     '            refuse("%s at time %s is UNIFORM -- the solver wrote no solution into it" % (name, time))\n'
     '        refuse("could not locate the internalField of %s STRUCTURALLY" % p)',
     '        return [(300.0, 0.0, 0.0)] * 100000 if vector else [300.0] * 100000'),

    ("M23", ["L22"],
     "case_identity stops recomputing G = Gr/Re and Re from the case's own "
     "files, so a mutated nu is never caught",
     '    if abs(ident["G_mix"] - ph["G_mix"]) > G_TOL:',
     '    if False and abs(ident["G_mix"] - ph["G_mix"]) > G_TOL:'),

    ("M24", ["L23"],
     "the planted-zero POSITIVE arm stops refusing a blind reader, so a reader "
     "that cannot see the plant is accepted and its zeros mean nothing",
     '            if floor is None:',
     '            if False:'),

    ("M25", ["L24"],
     "G2's control reverts to a POINT plant, losing the all-row alternating-sign "
     "shape an RMS reader needs (L-340)",
     '            ("G2", "T", row, alt, None, ident["dT"]),        # ALL-ROW ALTERNATING (L-340)',
     '            ("G2", "T", [row[0]], [1.0], None, ident["dT"]),'),

    ("M26", ["L25"],
     "the ULP arithmetic that rejects analyse_t3.py's predicate is replaced by a "
     "recollection -- the reported ratio stops being a reading",
     '                   t3_slack_in_ulp=1e-15 / ulp,',
     '                   t3_slack_in_ulp=2.0,'),

    ("M27", ["L26"],
     "the station-metric planted control stops refusing when the plant is not "
     "recovered, so a BLIND station reader selects the first candidate row and "
     "nothing distinguishes that from a station selected on evidence",
     '        if not (lo_ok and hi_ok):',
     '        if False:'),

    ("M28", ["L27"],
     "the fast station scanner is detuned by 1e-7 relative, so it is no longer "
     "the frozen witness of analyse_t16.py:340-354",
     '    return m / dT',
     '    return m / dT * 1.0000001'),

    ("M29", ["L28"],
     "rule 4's AGE GUARD stops refusing a field older than the case's own 0/T",
     '        if ages[f] <= 0.0:',
     '        if False:'),

    ("M30", ["L29"],
     "rule 4's rc conjunct stops refusing a non-zero rc",
     '    if out["rc"] != 0:',
     '    if False:'),

    ("M31", ["L30"],
     "rule 4's End-line conjunct stops refusing a log with no End line",
     '    if not out["end_line"]:',
     '    if False:'),

    ("M32", ["L31"],
     "rule 4's field-presence conjunct skips a registered field that is absent "
     "at endTime instead of refusing -- a missing number treated as a non-event",
     '        if not os.path.isfile(p):\n'
     '            refuse("%s: registered field %s absent at endTime %s (rule 4)" % (case, f, ts[-1]))',
     '        if not os.path.isfile(p):\n            continue'),

    ("M33", ["L32", "L34", "L40"],
     "S8a stops comparing the grading root against the live roots -- this is "
     "analyse_t18.py:509's defect reintroduced deliberately",
     '        if r == lr or r.startswith(lr + os.sep) or lr.startswith(r + os.sep):',
     '        if False:'),

    ("M34", ["L33"],
     "S8b stops requiring the forge sentinel, so a path-innocent tree with no "
     "positive marker is graded (S8a alone is a path test; a symlink defeats it)",
     '    if not os.path.isfile(sentinel):',
     '    if False:'),

    ("M35", ["L34"],
     "S8a stops resolving symlinks, so an innocently-named link to the live "
     "tree passes the path test",
     '    r = os.path.realpath(os.path.abspath(root))',
     '    r = os.path.abspath(root)'),

    ("M36", ["L35"],
     "the S8d source detector looks for a name that does not occur, so it can "
     "no longer see a planted `grade(HERE, ...)` -- a detector never shown able "
     "to see a non-zero",
     '                        and sub.func.id == "grade"):',
     '                        and sub.func.id == "GRADE_NEVER_OCCURS"):'),

    ("M37", ["L36"],
     "an `assert` is planted in the comparator (L-332: an assert vanishes under "
     "python3 -O and the refusal it was carrying vanishes with it)",
     'def _station_floor_identity_check():',
     'def _station_floor_identity_check():\n    assert True  # MUTANT (L-332)'),

    ("M38", ["L37"],
     "a CARRIED-OVER function's source text is changed without changing its "
     "behaviour, so section 6's byte-identity claim becomes false while every "
     "numerical limb stays green",
     'def row_of(vals, N, j):\n    return vals[j * N:(j + 1) * N]',
     'def row_of(vals, N, j):\n    return vals[j * N:(j + 1) * N][:]'),

    ("M39", ["L38"],
     "the S8c watcher's PLANTED read is removed, so the watcher's zero is no "
     "longer evidence -- a zero from a reader not shown able to see a non-zero",
     '        os.path.isfile(os.path.join(PARENT, "run_one_t16.sh"))',
     '        pass  # MUTANT: the planted read is gone'),

    ("M40", ["L39"],
     "a deliberate unallowed read of the LIVE tree is performed inside the "
     "watched block -- S8c must record it",
     '        # ---------------- L01 the referent still verifies --------------------',
     '        open(os.path.join(PARENT, "run_one_t16.sh")).close()   # MUTANT\n'
     '        # ---------------- L01 the referent still verifies --------------------'),

    ("M41", ["L40"],
     "the -O probe stops driving S8a, so the python3 -O limb passes without "
     "having exercised a guard",
     '        _selftest_root_guard(LIVE_ROOT, "-O probe")\n        return EXIT_OK',
     '        return EXIT_OK'),
]

LIMB_RE = re.compile(r"^\s*\[(ok |FAIL)\]\s+(L\d+)\b")


def fingerprint(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for n in sorted(filenames):
            p = os.path.join(dirpath, n)
            try:
                st = os.stat(p)
                out.append("%s %.6f %d" % (p, st.st_mtime, st.st_size))
            except OSError as e:
                out.append("%s ERR %s" % (p, e))
    return out


def run_selftest(script_path, timeout=1800):
    for d, _, _ in os.walk(os.path.dirname(script_path)):
        if os.path.basename(d) == "__pycache__":
            shutil.rmtree(d, ignore_errors=True)
    pc = os.path.join(PARENT, "__pycache__")
    shutil.rmtree(pc, ignore_errors=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([sys.executable, script_path, "--selftest"],
                           capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return None, set(), "TIMEOUT"
    seen, red = set(), set()
    for line in r.stdout.splitlines():
        m = LIMB_RE.match(line)
        if m:
            seen.add(m.group(2))
            if m.group(1) == "FAIL":
                red.add(m.group(2))
    # A limb that never printed at all is red-by-absence: the run aborted before
    # reaching it, which is a refusal and is recorded as such.
    red |= (set(ALL_LIMBS) - seen)
    return r.returncode, red, ""


def apply_mutation(src_text, old, new):
    n = src_text.count(old)
    if n != 1:
        return None, "the old text occurs %d times, not exactly once" % n
    return src_text.replace(old, new), ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="comma-separated mutation ids")
    ap.add_argument("--jobs", type=int, default=1, help="reserved; runs are serial")
    a = ap.parse_args()

    if not os.path.isfile(TARGET):
        print("REFUSE: no analyse_t16c.py at %s" % TARGET)
        return 2
    src = open(TARGET).read()
    before = fingerprint(PARENT)

    work = tempfile.mkdtemp(prefix="t16cmut_")
    results = []
    try:
        # ---- THE UNMUTATED CONTROL.  Rule 3's shape applied to this harness. --
        d0 = os.path.join(work, "control")
        os.makedirs(d0)
        p0 = os.path.join(d0, "analyse_t16c.py")
        open(p0, "w").write(src)
        rc0, red0, err0 = run_selftest(p0)
        print("CONTROL (unmutated copy): exit %s, %d red limbs %s"
              % (rc0, len(red0), sorted(red0) if red0 else ""))
        if rc0 != 0 or red0:
            print("REFUSE: the UNMUTATED copy does not run clean, so no red this harness "
                  "reports can be attributed to a mutation.")
            return 2
        print("  the harness reports green on an unbroken file, so its reds are attributable.\n")

        chosen = set(a.only.split(",")) if a.only else None
        for mid, expect, why, old, new in MUTATIONS:
            if chosen and mid not in chosen:
                continue
            d = os.path.join(work, mid)
            os.makedirs(d)
            p = os.path.join(d, "analyse_t16c.py")
            mutated, err = apply_mutation(src, old, new)
            if mutated is None:
                print("%s  REFUSE: %s" % (mid, err))
                results.append((mid, expect, set(), "BAD-PATCH", why))
                continue
            open(p, "w").write(mutated)
            rc, red, rerr = run_selftest(p)
            exp = set(expect)
            if rerr:
                cls = "TIMEOUT"
            elif not red:
                cls = "MISS"
            elif red == exp:
                cls = "EXACT"
            elif red == set(ALL_LIMBS):
                cls = "ABORT"
            elif exp <= red:
                cls = "SUPERSET"
            else:
                cls = "MISS"
            results.append((mid, expect, red, cls, why))
            print("%s  aim %-18s -> %-8s exit %-4s reddened %s"
                  % (mid, ",".join(expect), cls, rc,
                     ("ALL 40 (the guard aborted the run)" if cls == "ABORT"
                      else ",".join(sorted(red)) if red else "NOTHING")))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    after = fingerprint(PARENT)
    print("\nLIVE-TREE CONTROL: %d entries fingerprinted under %s before and after; %s"
          % (len(before), os.path.basename(PARENT),
             "IDENTICAL" if before == after else "*** CHANGED ***"))
    if before != after:
        print("REFUSE: the live run tree changed during the sweep.")
        return 2

    covered = set()
    for _, _, red, cls, _ in results:
        covered |= red
    union_expect = set()
    for _, exp, _, _, _ in results:
        union_expect |= set(exp)
    unverified = sorted(l for l in union_expect if l not in covered)
    print("\nLIMB COVERAGE: %d of %d limbs reddened by at least one control."
          % (len(covered & set(ALL_LIMBS)), len(ALL_LIMBS)))
    never = sorted(set(ALL_LIMBS) - covered)
    if never:
        print("NOT VERIFIED (no control reddens them): %s" % ",".join(never))
    if unverified:
        print("AIMED AT BUT NOT REDDENED: %s" % ",".join(unverified))
    exact = sum(1 for r in results if r[3] == "EXACT")
    print("classification: %d EXACT, %d SUPERSET, %d ABORT, %d MISS/other"
          % (exact,
             sum(1 for r in results if r[3] == "SUPERSET"),
             sum(1 for r in results if r[3] == "ABORT"),
             sum(1 for r in results if r[3] in ("MISS", "TIMEOUT", "BAD-PATCH"))))
    return 0 if not never and not unverified else 1


if __name__ == "__main__":
    sys.exit(main())
