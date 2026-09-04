#!/usr/bin/env python3
"""D-J1 DENOMINATOR PROBE — read-only, imports the FROZEN readers, never copies them.

WHAT D-J1 IS.  `rel = dmax / rng if rng > 0 else 0.0` at

    verification/runs/T-family/T1_runs/analyse_t1c.py:229          (the T limb)
    verification/runs/T-family/T3_runs/analyse_t3.py:278           (the |U| limb)

is a divide-by-zero guard that, on the `rng == 0` branch, substitutes THE VALUE
THAT GRADES BEST.  `rel = 0.0` is unconditionally <= tol, so the level reads
`CONVERGED` **irrespective of dmax** — a field that moved 10 K between the last
two checkpoints is certified converged if the later checkpoint happens to be
spatially uniform.  Both limbs are composed at analyse_t3.py:625-631 into
`convergence_state`, which analyse_t3d.py:200 gates the whole T3d ladder on.

WHY A SEPARATE PROBE AT ALL.  `gate_t3d.json` cannot show its own work.
analyse_t3d.py:242-245 builds the emitted `measurements` block from a fixed key
list that carries `convergence_state` and carries NEITHER `convergence_T` NOR
`convergence_U` — the only two dicts that hold `field_range`, i.e. the branch's
denominator.  So the published JSON records the WORD `CONVERGED` and not one
denominator that produced it.  This probe supplies the denominator, beside the
verdict, from the same functions the grader calls.

HOW IT CANNOT DRIFT FROM THE GRADER.  The two readers are IMPORTED, not
reimplemented:

    T1C.iterative_convergence(case, "T")        <- analyse_t1c.py:197
    A3.iterative_convergence_vector(case, "U")  <- analyse_t3.py:263

If either frozen file changes, this probe changes with it, silently and
correctly.  Nothing here is a copy of their logic.

RULE 3 — THIS PROBE CARRIES ITS OWN PLANTED-ZERO CONTROL, IN THREE LIMBS.
A zero from a reader not shown able to see a non-zero is not evidence, and a
`field_range = 0.0` reported for R_fx by a reader never shown able to read ~51 K
off R_m would be worth nothing.  The control runs BEFORE any level is probed and
REFUSES (exit 2) if any limb fails.

  LIMB W (WITNESS, on real disk bytes).  The two already-closed levels must come
      back at their independently recorded ranges: R_m/(34000,36000) T = 51.2959 K
      and |U| = 11.0155; R_f/(76000,78000) T = 50.7293 K and |U| = 11.0257.
      Tolerance 1e-3 — those figures are quoted to four decimals, so the rounding
      half-width is 5e-4 and this is twice it.  The tolerance is fixed from the
      QUOTED PRECISION, not chosen to make anything pass.

  LIMB P (PLANT, on a scratch copy).  A real T checkpoint is copied into two
      identical time directories of a throwaway case, so the reader's honest
      answer is dmax == 0.0 exactly — a true zero.  Then PLANT = 1.234e-03 K is
      added to ONE cell of the later copy and the file is read back FROM DISK.
      The reader must then return dmax == PLANT.  This is the fails-CLOSED limb:
      it shows the reader can see a non-zero that was not there a moment ago.
      NOTHING IN THE REPOSITORY IS WRITTEN — the plant lands in a temporary
      directory created by tempfile and removed on the way out.

  LIMB D (THE DEFECT ITSELF, on a synthetic case).  A pair of checkpoints whose
      LATER member is spatially uniform: dmax = 10.0 K, rng = 0.0.  The frozen
      reader MUST return `CONVERGED`.  If it does not, D-J1 is not what this
      probe says it is and the probe refuses rather than reporting a defect it
      cannot demonstrate.  This limb is the proof that the classifier below is
      reading a real branch and not a hypothesis.

WHAT THIS PROBE DOES NOT DO.  It runs no solver, writes nothing into any case
directory, computes no gate, grades nothing and closes nothing.  It reports the
denominator and the branch taken.  A `CONVERGED` never leaves it without a
`field_range` on the same line.

WHAT THIS PROBE CANNOT SEE, stated because a check that overstates its reach is
worse than none:
  - It does not verify the run is complete (CLAUDE.md rule 4).  A level with two
      checkpoints on disk is probeable long before it is gradeable.
  - It does not verify the checkpoint pair it reports is the pair the grader will
      read.  It reports `between` so a reader can compare; if the case writes
      again between probe and grade, the pair moves.
  - It says nothing about the Roache triple (rule 5), the band, or the primary.
  - `rng > 0` is necessary, not sufficient: it clears D-J1 only.  A level can take
      the honest branch and still be NOT_CONVERGED.

Usage:  python3 probe_djone_denominator.py [--root DIR] [CASE ...]
        default CASE list: R_m R_f     (R_fx is added by the caller once it writes)
Exit 0 ran, 2 refusal.  Zero `assert` statements (L-332).
"""
import math
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True          # no .pyc beside a frozen comparator (stale-pycache hazard)

HERE = os.path.dirname(os.path.abspath(__file__))
T1_DIR = os.path.normpath(os.path.join(HERE, "..", "T1_runs"))
sys.path[:0] = [HERE, T1_DIR]
import analyse_t1c as T1C                                          # noqa: E402
import analyse_t3 as A3                                            # noqa: E402

EXIT_OK, EXIT_REFUSE = 0, 2
PLANT = 1.234e-03                       # K, the same constant analyse_t3.py:81 plants
WITNESS_TOL = 1.0e-3                    # 2x the half-width of a 4-decimal quotation
SYNTH_N = 64                            # cells in the synthetic limb-D case
SYNTH_DMAX = 10.0                       # K, the change D-J1 must certify away
DEFAULT_CASES = ("R_m", "R_f")

# Independently recorded, by a predecessor lane, from these same two levels.
# Cited, not re-derived.  If disk disagrees beyond WITNESS_TOL that is a FINDING.
WITNESS = {
    "R_m": dict(between=("34000", "36000"), T=51.2959, U=11.0155),
    "R_f": dict(between=("76000", "78000"), T=50.7293, U=11.0257),
}


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def scalar_field_file(path, values, location, obj="T", dims="[0 0 0 1 0 0 0]"):
    """Write a volScalarField OpenFOAM ASCII file.  Scratch only."""
    body = "\n".join(repr(float(v)) for v in values)
    open(path, "w").write(
        "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        "    class       volScalarField;\n    location    \"%s\";\n"
        "    object      %s;\n}\n\ndimensions      %s;\n\n"
        "internalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n\n"
        "boundaryField\n{\n}\n" % (location, obj, dims, len(values), body))


def vector_field_file(path, vectors, location, obj="U"):
    """Write a volVectorField OpenFOAM ASCII file.  Scratch only."""
    body = "\n".join("(%r %r %r)" % tuple(float(c) for c in v) for v in vectors)
    open(path, "w").write(
        "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        "    class       volVectorField;\n    location    \"%s\";\n"
        "    object      %s;\n}\n\ndimensions      [0 1 -1 0 0 0 0];\n\n"
        "internalField   nonuniform List<vector> \n%d\n(\n%s\n)\n;\n\n"
        "boundaryField\n{\n}\n" % (location, obj, len(vectors), body))


def plant_one_cell(path, index, delta):
    """Add delta to internal value `index`, IN PLACE, and return (before, after)
    read back FROM DISK.  Located the same way analyse_t3.plant_into_T locates
    the field: the count line followed by the bare '(' opener."""
    txt = open(path).read().split("\n")
    start = None
    for i in range(len(txt) - 2):
        if txt[i].strip().isdigit() and txt[i + 1].strip() == "(":
            start = i + 2
            break
    if start is None:
        refuse("cannot locate the internal field in the scratch file %s" % path)
    before = float(txt[start + index].strip())
    txt[start + index] = repr(before + delta)
    open(path, "w").write("\n".join(txt))
    return before, float(open(path).read().split("\n")[start + index].strip())


# ---------------------------------------------------------------------------
# the rule-3 control
# ---------------------------------------------------------------------------
def limb_W(root, out):
    """Real disk bytes: the reader must return the independently recorded ranges."""
    ok = True
    for case, w in WITNESS.items():
        cd = os.path.join(root, case)
        if not os.path.isdir(cd):
            refuse("LIMB W: %s does not exist; the witness cannot be driven and a zero "
                   "from this probe would mean nothing" % cd)
        cT = T1C.iterative_convergence(cd, "T")
        cU = A3.iterative_convergence_vector(cd, "U")
        for tag, got, want in (("T", cT.get("field_range"), w["T"]),
                               ("|U|", cU.get("field_range"), w["U"])):
            good = got is not None and abs(got - want) <= WITNESS_TOL
            ok = ok and good
            out("    %-4s %-4s field_range = %s   recorded %.4f   %s"
                % (case, tag, ("%.4f" % got) if got is not None else "None", want,
                   "SEEN" if good else "*** MISMATCH ***"))
        pair = tuple(cT.get("between") or ())
        if pair != w["between"]:
            ok = False
            out("    %-4s pair = %r   recorded %r   *** MISMATCH ***" % (case, pair, w["between"]))
    return ok


def limb_P(root, out):
    """Plant: a true zero baseline, then one planted cell the reader must see."""
    src = os.path.join(root, "R_m", "36000", "T")
    if not os.path.isfile(src):
        refuse("LIMB P: no %s to copy; the plant cannot be driven" % src)
    tmp = tempfile.mkdtemp(prefix="djone_plant_")
    try:
        for t in ("1000", "2000"):
            os.makedirs(os.path.join(tmp, t))
            shutil.copy2(src, os.path.join(tmp, t, "T"))
        base = T1C.iterative_convergence(tmp, "T")
        zero_ok = base.get("max_change") == 0.0
        out("    baseline (identical copies)  max_change = %r  rng = %.4f  %s"
            % (base.get("max_change"), base.get("field_range") or 0.0,
               "TRUE ZERO" if zero_ok else "*** NOT A TRUE ZERO ***"))
        before, after = plant_one_cell(os.path.join(tmp, "2000", "T"), 0, PLANT)
        got = T1C.iterative_convergence(tmp, "T")
        dmax = got.get("max_change")
        tol = 32 * math.ulp(max(abs(before), abs(after)))
        seen = dmax is not None and abs(dmax - PLANT) <= tol
        out("    planted %.6e K into cell 0 (%.10f -> %.10f), read back from disk"
            % (PLANT, before, after))
        out("    reader max_change = %r   tolerance %.3e (32 ulp of the operands)   %s"
            % (dmax, tol, "PLANT SEEN" if seen else "*** PLANT INVISIBLE ***"))
        rng_ok = (got.get("field_range") or 0.0) > 0.0
        out("    planted case field_range = %.4f   %s"
            % (got.get("field_range") or 0.0, "non-zero" if rng_ok else "*** ZERO ***"))
        return zero_ok and seen and rng_ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def limb_D(out):
    """The defect itself: a uniform later checkpoint must be certified CONVERGED."""
    tmp = tempfile.mkdtemp(prefix="djone_defect_")
    try:
        for t, v in (("1000", 300.0), ("2000", 300.0 + SYNTH_DMAX)):
            os.makedirs(os.path.join(tmp, t))
            scalar_field_file(os.path.join(tmp, t, "T"), [v] * SYNTH_N, t)
            vector_field_file(os.path.join(tmp, t, "U"),
                              [(v / 100.0, 0.0, 0.0)] * SYNTH_N, t)
        cT = T1C.iterative_convergence(tmp, "T")
        cU = A3.iterative_convergence_vector(tmp, "U")
        out("    synthetic T   dmax = %.4f  rng = %.4f  rel = %r  state = %s"
            % (cT.get("max_change") or 0.0, cT.get("field_range") or 0.0,
               cT.get("relative"), cT.get("state")))
        out("    synthetic |U| dmax = %.4f  rng = %.4f  rel = %r  state = %s"
            % (cU.get("max_change") or 0.0, cU.get("field_range") or 0.0,
               cU.get("relative"), cU.get("state")))
        fires = (cT.get("field_range") == 0.0 and cT.get("state") == "CONVERGED"
                 and (cT.get("max_change") or 0.0) > 0.0
                 and cU.get("field_range") == 0.0 and cU.get("state") == "CONVERGED"
                 and (cU.get("max_change") or 0.0) > 0.0)
        out("    D-J1 reproduced on both limbs: %s" % ("YES" if fires else "*** NO ***"))
        return fires
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control(root, out):
    out("rule-3 control — a zero from a reader not shown able to see a non-zero is not evidence")
    out("  LIMB W (witness, real disk bytes):")
    w = limb_W(root, out)
    out("  LIMB P (plant on a scratch copy; nothing in the repository is written):")
    p = limb_P(root, out)
    out("  LIMB D (the defect itself, synthetic):")
    d = limb_D(out)
    out("  control: LIMB W = %s   LIMB P = %s   LIMB D = %s"
        % (("PASS" if w else "FAIL"), ("PASS" if p else "FAIL"), ("PASS" if d else "FAIL")))
    if not (w and p and d):
        refuse("the planted-zero control did not pass (W=%s P=%s D=%s). This probe has NOT "
               "been shown able to see a non-zero field_range, so any zero it would report "
               "is not evidence and no level may be classified from this run." % (w, p, d))


# ---------------------------------------------------------------------------
# the probe
# ---------------------------------------------------------------------------
def classify(case, tag, c, out):
    """Print state, denominator, numerator and pair — and the branch taken.
    A bare CONVERGED never leaves this function without its denominator."""
    state = c.get("state")
    if state == "UNJUDGED":
        out("  %-5s %-4s PENDING — %s" % (case, tag, c.get("why")))
        out("        BRANCH: NOT MEASURABLE — the denominator does not exist yet; this level "
            "is not gradeable and P-1 is UNANSWERED for it.")
        return "PENDING"
    rng = c.get("field_range")
    out("  %-5s %-4s state = %-13s field_range = %.6g   max_change = %.6g   "
        "relative = %.6g   between = %s   tol = %g"
        % (case, tag, state, rng, c.get("max_change"), c.get("relative"),
           tuple(c.get("between") or ()), c.get("tol")))
    if rng is not None and rng > 0.0:
        out("        BRANCH: rng>0 TAKEN — the ratio is a real ratio; D-J1 did not fire on "
            "this field at this level.")
        return "HONEST"
    out("        BRANCH: rng==0 — D-J1 FIRES, LEVEL IS NOT A RESULT.  The last checkpoint's "
        "%s is spatially uniform, so `rel = dmax / rng if rng > 0 else 0.0` substituted 0.0 "
        "and certified CONVERGED without dividing by anything.  The word CONVERGED here is "
        "the defect's output, not a finding, and prediction P-1 is UNANSWERED — not answered "
        "CONVERGED." % tag)
    return "DEFECT"


def probe(root, cases, out=print):
    control(root, out)
    out("")
    out("denominators (frozen readers, imported: T1C.iterative_convergence / "
        "A3.iterative_convergence_vector)")
    verdicts = {}
    for case in cases:
        cd = os.path.join(root, case)
        if not os.path.isdir(cd):
            out("  %-5s ABSENT — %s does not exist" % (case, cd))
            verdicts[case] = "ABSENT"
            continue
        cT = T1C.iterative_convergence(cd, "T")
        cU = A3.iterative_convergence_vector(cd, "U")
        bT = classify(case, "T", cT, out)
        bU = classify(case, "|U|", cU, out)
        verdicts[case] = (bT, bU)
    out("")
    out("summary")
    for case in cases:
        v = verdicts[case]
        if v == "ABSENT":
            out("  %-5s ABSENT" % case)
        elif "DEFECT" in v:
            out("  %-5s NOT A RESULT — D-J1 fired (T=%s, |U|=%s)" % (case, v[0], v[1]))
        elif "PENDING" in v:
            out("  %-5s PENDING — a denominator is not yet on disk (T=%s, |U|=%s)"
                % (case, v[0], v[1]))
        else:
            out("  %-5s denominator honest on both fields — rng>0 taken for T and |U|. "
                "This clears D-J1 ONLY; it is not a convergence verdict and not a gate."
                % case)
    return verdicts


def main(argv):
    root, cases = HERE, []
    i = 0
    while i < len(argv):
        if argv[i] == "--root":
            root = os.path.abspath(argv[i + 1]); i += 2
        elif argv[i].startswith("-"):
            refuse("unknown option %r; usage: probe_djone_denominator.py [--root DIR] [CASE ...]"
                   % argv[i])
        else:
            cases.append(argv[i]); i += 1
    if not cases:
        cases = list(DEFAULT_CASES)
    print("D-J1 DENOMINATOR PROBE — read-only; no solver, no case-directory write, no grade")
    print("root  : %s" % root)
    print("cases : %s" % " ".join(cases))
    print("readers: analyse_t1c.py sha256 %s" % A3.sha256(os.path.join(T1_DIR, "analyse_t1c.py")))
    print("         analyse_t3.py  sha256 %s" % A3.sha256(os.path.join(HERE, "analyse_t3.py")))
    print("")
    probe(root, cases)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
