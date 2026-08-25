#!/usr/bin/env python3
"""T1b PLANTED-ZERO CONTROL -- an EXTERNAL control instrument that grades nothing.

Built to the FROZEN specification
  docs/campaigns/T-family/T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md
  commit 3ae9e504, sha256 303924c1c1088559262996afe5aaf489205f8a07577422063fe3678c862b16f6

WHY THIS FILE EXISTS.  CLAUDE.md standing rule 3 -- "a zero from a reader not
shown able to see a non-zero is not evidence" -- was NOT armed on the T1b
chain.  analyse_t1b_L4.py, analyse_t1b.py and analyse_t1c.py carry no planted
perturbation (0 plant-idiom hits against 27 and 38 on the two comparators known
to carry one; that positive control is what makes the three zeros evidence).
The most exposed reader is analyse_t1c.iterative_convergence, because it gates
step (1) of Roache triple gating: a reader that silently cannot see a
difference would report CONVERGED everywhere and nothing else in the chain
would catch it.  A blind reader raises nothing, so refusal paths cannot catch
it; only a plant can.

WHAT THIS FILE IS NOT.
  * It does NOT modify analyse_t1b_L4.py, analyse_t1b.py or analyse_t1c.py.
    All three are byte-identical to their blobs at the L4 pre-registration
    commit 17209b50 (verified: 9698adb0..., 647d7412..., 60893b28...), and the
    Charter 2d.1 repair exception is explicitly NOT invoked -- adding a control
    repairs no value and moves no number.
  * It does NOT grade anything.  It returns PASS or REFUSE, and neither is a
    rung verdict.  Per the frozen spec section 2 it can only ever turn the
    rung's numbers into NOT A RESULT; it can never turn anything into a PASS.
  * It does NOT reimplement either reader.  Both are IMPORTED from the frozen
    files.  A reimplemented reader tests the reimplementation and is worthless
    as a control.

THE TWO ARMS (frozen spec 3.2) -- both must give their registered answer.
  POSITIVE: plant PLANT by line index, read back through the imported reader.
            The reader MUST see it, to TOL_REL.  If not -> REFUSE (blind).
  NEGATIVE: read back an UNMODIFIED copy.  The reader MUST report no change.
            If it reports one -> REFUSE (noisy).  A reader that always reports
            a difference passes the positive arm while being just as useless;
            the negative arm is the only thing that catches it.

HOW THE NEGATIVE ARM IS CONSTRUCTED, and this is a reading of the spec that
the supervisor should confirm.  For iterative_convergence the spec's "copy the
field and read it back unmodified; the reader MUST report no change" is
implemented by copying the LATEST checkpoint's T over the earlier slot, so the
two checkpoints the reader compares are byte-identical and a correct reader
must return max_change EXACTLY 0.0.  Reading it the other way -- run the reader
on the case as it stands -- cannot be right: the last two checkpoints of any
real case differ by a real physical amount, so "no change" would be
unsatisfiable by construction and the spec predicts the control passes.  The
identical-checkpoints construction is also analyse_t10a.py's own (its selftest
builds "two checkpoints, identical; then the plant"), and it makes BOTH arms
exact rather than inequalities: with the checkpoints identical, the true
max_change is 0 before the plant and is EXACTLY the plant's float effect after
it.  If the supervisor intended the other reading, this file must change.

WHAT THIS CONTROL CANNOT SEE.
  * Whether either reader is CORRECT.  It establishes that they are not blind
    and not noisy -- that their zeros are real zeros.  A reader that sees a
    difference and then computes the wrong Nu passes this control.
  * measure() on synthetic data: --selftest cannot exercise it, because
    measure runs postProcess against a real mesh.  --selftest proves the plant
    machinery, the two decision functions, and iterative_convergence end to end
    on synthetic scratch data, and says so.
  * Any grader outside the T1b chain (frozen spec section 5 lists those as
    OPEN, as a lead and not a finding).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t1b as T1B                                # noqa: E402
import analyse_t1c as T1C                                # noqa: E402

# ---- REGISTERED CONSTANTS, FROZEN BY THE PRE-REGISTRATION COMMIT ------------
PLANT = 1.234e-03          # K, the constant analyse_t3.py uses (its line 81)
TOL_REL = 1.0e-06          # relative, on the recovered change
EXIT_OK, EXIT_REFUSE = 0, 2
# ----------------------------------------------------------------------------

SUBJECT = "R_10k_x"        # see MODULE NOTE on the choice, and --help
STATION = T1B.STATIONS[-1]  # 80 D -- the station whose Nu the L4 row uses
SCRATCH = os.environ.get("T1B_PLANT_SCRATCH", tempfile.gettempdir())


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def assert_not_case_tree(path):
    """HARD GUARD.  measure() runs postProcess and WRITES into the directory it
    is handed (log.writeCellCentres, Cx, Cy, V).  Two T1b solvers were live
    while this file was written (R_100k_x, R_30k_x).  Nothing here may ever be
    pointed at the real tree, so this refuses instead of trusting the caller."""
    p = os.path.realpath(path)
    if p == os.path.realpath(HERE) or p.startswith(os.path.realpath(HERE) + os.sep):
        refuse(f"the control was pointed at the case tree ({p}); it copies and "
               "never touches. Nothing was written.")
    return p


# ---------------------------------------------------------------------------
# the plant: BY LINE INDEX, never by matching a value
# ---------------------------------------------------------------------------
def locate_internal_block(lines):
    """Return (first_value_line_index, n_values), located STRUCTURALLY.

    A value-matching plant can silently fail to land when the value it looks
    for is absent and then report success having done nothing; this walks the
    file's structure instead.  Mirrors analyse_t10a.planted_zero_control's
    idiom (its line 377) rather than reinventing it."""
    i = next((k for k, l in enumerate(lines)
              if re.search(r"internalField\s+nonuniform\s+List<scalar>", l)), None)
    if i is None:
        return None, None
    j = i
    while j < len(lines) and not re.fullmatch(r"\s*\(\s*", lines[j]):
        j += 1
    if j >= len(lines):
        return None, None
    n = None
    for k in range(i, j):
        if re.fullmatch(r"\s*\d+\s*", lines[k]):
            n = int(lines[k].strip())
    return j + 1, n


def plant_by_line_index(path, cell_index):
    """Add PLANT to ONE value, chosen BY INDEX, and read the file back FROM
    DISK to prove the plant landed.  Returns (old, expected, line_number).

    expected = fl(old + PLANT) - old is the change the plant CAN produce in
    float.  Asserting the reader recovers `expected` (not PLANT) is exact and
    still fails when the plant is swallowed -- analyse_t10a.py's reasoning,
    adopted rather than re-derived."""
    with open(path, errors="replace") as fh:
        lines = fh.read().split("\n")
    start, n = locate_internal_block(lines)
    if start is None:
        refuse(f"cannot locate an internalField scalar block in {path}")
    if not (0 <= cell_index < n):
        refuse(f"plant index {cell_index} outside the {n}-value block of {path}")
    target = start + cell_index
    old = float(lines[target])
    expected = (old + PLANT) - old
    lines[target] = repr(old + PLANT)
    with open(path, "w") as fh:
        fh.write("\n".join(lines))
    # READ BACK FROM DISK -- the plant is not trusted until disk confirms it
    with open(path, errors="replace") as fh:
        back = float(fh.read().split("\n")[target])
    if (back - old) != expected:
        refuse(f"the plant did not land in {path} line {target + 1}: "
               f"{old} -> {back}, expected a change of {expected}")
    return old, expected, target + 1


# ---------------------------------------------------------------------------
# the two decision functions -- PURE, so --selftest can prove them
# ---------------------------------------------------------------------------
def judge_positive(recovered, expected, reader_name, quantity):
    """The reader MUST have seen the plant."""
    if expected <= 0.0:
        return False, (f"{reader_name}: the plant produced no float change at all "
                       f"(expected {expected!r}); the control cannot conclude")
    if abs(expected - PLANT) > TOL_REL * PLANT:
        return False, (f"{reader_name}: the plant was distorted on disk "
                       f"({expected!r} against a planted {PLANT!r})")
    if abs(recovered - expected) <= TOL_REL * abs(expected):
        return True, (f"{reader_name} SAW the plant in {quantity}: recovered "
                      f"{recovered!r} against expected {expected!r}")
    return False, (f"{reader_name} IS BLIND to a {PLANT!r} K plant in {quantity}: "
                   f"it recovered {recovered!r} where {expected!r} was planted "
                   f"and read back from disk. Every zero this reader has "
                   f"produced for this rung is worthless.")


def judge_negative(recovered, reader_name, quantity):
    """The reader MUST report no change on an unmodified copy."""
    if recovered == 0.0:
        return True, (f"{reader_name} reported no change in {quantity} on an "
                      f"unmodified copy, as required")
    return False, (f"{reader_name} IS NOISY in {quantity}: it reported a change "
                   f"of {recovered!r} where nothing was planted. Its zeros are "
                   f"not zeros.")


# ---------------------------------------------------------------------------
# ARM 1 -- analyse_t1c.iterative_convergence, the reader that gates Roache (1)
# ---------------------------------------------------------------------------
def arm_iterative_convergence(subject_dir, reader=None, verbose=True):
    """Both arms on the imported iterative_convergence.

    `reader` exists ONLY so --selftest can inject a deliberately blind or noisy
    reader and prove this control REFUSES.  The real path always uses the
    frozen import."""
    reader = reader or T1C.iterative_convergence
    ts = sorted((d for d in os.listdir(subject_dir)
                 if re.fullmatch(r"\d+(\.\d+)?", d) and float(d) != 0.0),
                key=float)
    if len(ts) < 2:
        refuse(f"{subject_dir} has {len(ts)} checkpoint(s); the control needs two")
    early, late = ts[-2], ts[-1]
    tmp = tempfile.mkdtemp(prefix="t1b_plant_ic_", dir=SCRATCH)
    try:
        for t in (early, late):
            os.makedirs(os.path.join(tmp, t))
        # COPY, NEVER TOUCH: the LATEST T into BOTH slots, so a correct reader
        # must report EXACTLY 0.0 -- that is the negative arm's whole point.
        src = os.path.join(subject_dir, late, "T")
        shutil.copy2(src, os.path.join(tmp, late, "T"))
        shutil.copy2(src, os.path.join(tmp, early, "T"))

        neg = reader(tmp, field="T")
        ok_n, why_n = judge_negative(neg.get("max_change"),
                                     "analyse_t1c.iterative_convergence",
                                     "max_change between two identical checkpoints")
        if verbose:
            print(f"  NEGATIVE  {why_n}")
            print(f"            state={neg.get('state')} between={neg.get('between')}")

        old, expected, line = plant_by_line_index(
            os.path.join(tmp, early, "T"), cell_index=0)
        pos = reader(tmp, field="T")
        ok_p, why_p = judge_positive(pos.get("max_change"), expected,
                                     "analyse_t1c.iterative_convergence",
                                     "max_change")
        if verbose:
            print(f"  POSITIVE  {why_p}")
            print(f"            planted {PLANT!r} into {early}/T line {line} "
                  f"(value {old!r}); state={pos.get('state')}")
        return dict(ok=ok_n and ok_p, negative=(ok_n, why_n), positive=(ok_p, why_p),
                    planted=PLANT, expected=expected, line=line,
                    recovered_positive=pos.get("max_change"),
                    recovered_negative=neg.get("max_change"),
                    checkpoints=(early, late))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# ARM 2 -- analyse_t1b.measure, which supplies Nu, f, u_tau and y+
# ---------------------------------------------------------------------------
def _copy_runnable(subject_dir, dest, time_dir):
    """A runnable copy: measure() calls postProcess, so it needs the mesh, the
    system dict, CASE.txt and one time directory.  Nothing is written back."""
    os.makedirs(dest, exist_ok=True)
    for item in ("constant", "system"):
        shutil.copytree(os.path.join(subject_dir, item), os.path.join(dest, item))
    shutil.copy2(os.path.join(subject_dir, "CASE.txt"), os.path.join(dest, "CASE.txt"))
    shutil.copytree(os.path.join(subject_dir, time_dir), os.path.join(dest, time_dir))


def arm_measure(subject_dir, verbose=True):
    """Both arms on the imported measure().

    THE PLANT MUST BE AIMED.  measure computes Nu from |T_wall - T_bulk|, so a
    UNIFORM shift of T cancels exactly and a plant into a cell at another
    axial station changes nothing -- either would report a false blindness.
    The plant therefore goes into the ONE cell measure uses for T_wall: the
    largest-Cy cell of the station's cell set.  That set is recovered from
    measure's OWN returned station_xD and D_used and from the Cx/Cy that
    measure's own postProcess wrote, so nothing about the reader is
    reimplemented.  A mis-aimed plant can only make the positive arm FAIL --
    never pass falsely -- which is the safe direction, and the assertion that
    T_wall shifts by exactly the planted amount is itself the proof the aim
    was right."""
    late = T1C.latest_time(subject_dir)
    tmp = tempfile.mkdtemp(prefix="t1b_plant_me_", dir=SCRATCH)
    try:
        A, B = os.path.join(tmp, "A"), os.path.join(tmp, "B")
        _copy_runnable(subject_dir, A, late)
        _copy_runnable(subject_dir, B, late)
        assert_not_case_tree(A)
        assert_not_case_tree(B)

        base = T1B.measure(A, STATION)
        # NEGATIVE ARM: an independent, unmodified copy must read back identical
        other = T1B.measure(B, STATION)
        d_tw = other["T_wall"] - base["T_wall"]
        d_nu = other["Nu"] - base["Nu"]
        ok_n, why_n = judge_negative(d_tw, "analyse_t1b.measure",
                                     "T_wall on an unmodified independent copy")
        if verbose:
            print(f"  NEGATIVE  {why_n}")
            print(f"            Nu {base['Nu']!r} vs {other['Nu']!r} "
                  f"(delta {d_nu!r})")
        if ok_n and d_nu != 0.0:
            ok_n, why_n = judge_negative(d_nu, "analyse_t1b.measure",
                                         "Nu on an unmodified independent copy")
            if verbose:
                print(f"  NEGATIVE  {why_n}")

        # aim the plant at the cell measure uses for T_wall
        xsel = base["station_xD"] * base["D_used"]
        Cx = T1C.read_internal(os.path.join(A, late, "Cx"))
        Cy = T1C.read_internal(os.path.join(A, late, "Cy"))
        idx = [i for i, v in enumerate(Cx) if round(v, 10) == round(xsel, 10)]
        if not idx:
            refuse("could not aim the plant: no cell at the station measure "
                   f"reported (x = {xsel!r}); nothing was planted")
        iw = max(idx, key=lambda i: Cy[i])

        old, expected, line = plant_by_line_index(
            os.path.join(A, late, "T"), cell_index=iw)
        after = T1B.measure(A, STATION)
        rec = after["T_wall"] - base["T_wall"]
        ok_p, why_p = judge_positive(rec, expected, "analyse_t1b.measure", "T_wall")
        if verbose:
            print(f"  POSITIVE  {why_p}")
            print(f"            planted {PLANT!r} into {late}/T line {line} "
                  f"(cell {iw} of {len(Cx)}, value {old!r})")
            print(f"            Nu moved {base['Nu']!r} -> {after['Nu']!r} "
                  f"(delta {after['Nu'] - base['Nu']!r})")
        return dict(ok=ok_n and ok_p, negative=(ok_n, why_n), positive=(ok_p, why_p),
                    planted=PLANT, expected=expected, recovered_positive=rec,
                    recovered_negative=d_tw, cell=iw, line=line,
                    Nu_before=base["Nu"], Nu_after=after["Nu"], station=STATION)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# --selftest: SYNTHETIC SCRATCH DATA ONLY.  No case is read, nothing is graded.
# ---------------------------------------------------------------------------
SYNTH = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];

internalField   nonuniform List<scalar> 
{n}
(
{body}
)
;

boundaryField
{{
}}
"""


def _write_synth(path, values):
    with open(path, "w") as fh:
        fh.write(SYNTH.format(n=len(values),
                              body="\n".join(repr(v) for v in values)))


def selftest():
    print("planted_zero_control_t1b.py --selftest")
    print("  synthetic scratch data only; no case directory is read or written")
    print(f"  PLANT = {PLANT!r}   TOL_REL = {TOL_REL!r}   refusal exit = {EXIT_REFUSE}")
    ok = True
    checks = []

    def check(name, got, want=True):
        nonlocal ok
        good = (got == want)
        ok &= good
        checks.append(good)
        print(f"  {'ok ' if good else 'BAD'} {name}")
        return good

    # (i) the decision functions, proved on synthetic numbers
    exp = (300.0 + PLANT) - 300.0
    check("judge_positive accepts a reader that recovers exactly the plant",
          judge_positive(exp, exp, "R", "q")[0])
    check("judge_positive REFUSES a BLIND reader (recovers 0.0)",
          judge_positive(0.0, exp, "R", "q")[0], False)
    check("judge_positive REFUSES a reader that recovers half the plant",
          judge_positive(exp / 2, exp, "R", "q")[0], False)
    check("judge_positive REFUSES when the plant produced no float change",
          judge_positive(0.0, 0.0, "R", "q")[0], False)
    check("judge_positive accepts inside TOL_REL",
          judge_positive(exp * (1 + TOL_REL / 2), exp, "R", "q")[0])
    check("judge_positive REFUSES just outside TOL_REL",
          judge_positive(exp * (1 + TOL_REL * 10), exp, "R", "q")[0], False)
    check("judge_negative accepts an exact zero",
          judge_negative(0.0, "R", "q")[0])
    check("judge_negative REFUSES a NOISY reader (any non-zero)",
          judge_negative(1e-18, "R", "q")[0], False)
    print(f"      blind-reader message reads: {judge_positive(0.0, exp, 'analyse_t1c.iterative_convergence', 'max_change')[1][:96]}...")

    tmp = tempfile.mkdtemp(prefix="t1b_plant_self_", dir=SCRATCH)
    try:
        # (ii) the plant machinery on a synthetic field file
        vals = [300.0 + 0.001 * i for i in range(8)]
        p = os.path.join(tmp, "T")
        _write_synth(p, vals)
        start, n = locate_internal_block(open(p).read().split("\n"))
        check("locate_internal_block finds the value count", n == len(vals))
        old, expected, line = plant_by_line_index(p, cell_index=3)
        check("plant_by_line_index lands on the value chosen BY INDEX",
              old == vals[3])
        check("the plant is read back FROM DISK and equals fl(old+PLANT)-old",
              abs(expected - PLANT) <= TOL_REL * PLANT)
        back = T1C.read_internal(p)
        check("the FROZEN reader analyse_t1c.read_internal sees the plant",
              abs((back[3] - vals[3]) - expected) <= TOL_REL * expected)
        check("the frozen reader sees NO change in the untouched values",
              all(back[i] == vals[i] for i in range(len(vals)) if i != 3))

        # (iii) BOTH ARMS end to end on the REAL imported iterative_convergence
        case = os.path.join(tmp, "case")
        for t in ("100", "200"):
            os.makedirs(os.path.join(case, t))
            _write_synth(os.path.join(case, t, "T"), vals)
        r = arm_iterative_convergence(case, verbose=False)
        check("arm_iterative_convergence PASSES on a sound frozen reader", r["ok"])
        check("  its negative arm recovered exactly 0.0",
              r["recovered_negative"] == 0.0)
        check("  its positive arm recovered exactly the planted change",
              r["recovered_positive"] == r["expected"])

        # (iv) THE MUTATION CONTROL -- the arm must REFUSE a bad reader.
        #      Without this the control is unfalsifiable and proves nothing.
        blind = lambda d, field="T", tol=1e-6: dict(state="CONVERGED", max_change=0.0,
                                                    between=("100", "200"))
        rb = arm_iterative_convergence(case, reader=blind, verbose=False)
        check("a BLIND reader FAILS the arm (positive arm catches it)",
              rb["ok"], False)
        check("  and it is the POSITIVE arm that caught it", rb["positive"][0], False)
        check("  while the negative arm was happy -- which is exactly why "
              "the positive arm is needed", rb["negative"][0])
        noisy = lambda d, field="T", tol=1e-6: dict(state="NOT_CONVERGED",
                                                    max_change=7.7e-9,
                                                    between=("100", "200"))
        rn = arm_iterative_convergence(case, reader=noisy, verbose=False)
        check("a NOISY reader FAILS the arm (negative arm catches it)",
              rn["ok"], False)
        check("  and it is the NEGATIVE arm that caught it", rn["negative"][0], False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("  NOTE analyse_t1b.measure CANNOT be exercised on synthetic data: it")
    print("       runs postProcess against a real mesh. Its two arms are proved")
    print("       only by the real run, which the supervisor authorises "
          "separately.")
    print(f"SELFTEST {'PASSED' if ok else 'FAILED'} "
          f"({sum(checks)}/{len(checks)} checks)")
    return EXIT_OK if ok else EXIT_REFUSE


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        print(f"usage: {os.path.basename(__file__)} [--selftest] [--subject CASE]")
        print(f"  subject default {SUBJECT}; PLANT={PLANT!r} TOL_REL={TOL_REL!r}")
        return EXIT_OK

    subject = SUBJECT
    if "--subject" in argv:
        subject = argv[argv.index("--subject") + 1]
    sdir = os.path.join(HERE, subject)
    if not os.path.isdir(sdir):
        refuse(f"no such case {sdir}")
    if not os.path.isfile(os.path.join(HERE, f"DONE.{subject}")):
        refuse(f"{subject} carries no completion marker; the control is run "
               "against a COMPLETED case, never against one still solving")

    print(f"T1b PLANTED-ZERO CONTROL   subject {subject}   station {STATION} D")
    print(f"  PLANT = {PLANT!r} K   TOL_REL = {TOL_REL!r}   refusal exit = "
          f"{EXIT_REFUSE}")
    print(f"  frozen spec: docs/campaigns/T-family/"
          "T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md (commit 3ae9e504)")
    print("  the case tree is COPIED, never written to")

    print("\nARM 1  analyse_t1c.iterative_convergence  "
          "[gates step (1) of Roache triple gating]")
    r1 = arm_iterative_convergence(sdir)
    print("\nARM 2  analyse_t1b.measure  [supplies Nu, f, u_tau, y+]")
    r2 = arm_measure(sdir)

    print("\n" + "-" * 72)
    bad = []
    for nm, r in (("analyse_t1c.iterative_convergence", r1),
                  ("analyse_t1b.measure", r2)):
        for arm in ("positive", "negative"):
            if not r[arm][0]:
                bad.append(f"{nm} [{arm} arm]: {r[arm][1]}")
    if bad:
        for b in bad:
            print("  " + b)
        refuse("the T1b planted-zero control FAILED. Under the frozen "
               "pre-registration section 4 the disposition is fixed in advance: "
               "the T1b L4 rung is NOT A RESULT and every previously published "
               "T1b number depending on the affected reader is WITHDRAWN, not "
               "re-graded. Escalate; do not re-run until it agrees.")
    print("  PASSED -- both readers saw the plant and neither invented one.")
    print("  This is NOT a rung verdict. The control arms an existing gate; it")
    print("  does not create one, and it can only ever turn a number into NOT A")
    print("  RESULT, never into a PASS.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
