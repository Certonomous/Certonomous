#!/usr/bin/env python3
"""M6H1 H-G1 instrument, THE pyHyp CLAUSE -- read the marched **Min Quality** column out of
the pyHyp log and grade section 7's requirement "pyHyp **Min Quality > 0 at every layer**".

WHY THIS FILE EXISTS AT ALL.  `read_cell_count.py` grades the `checkMesh` half of H-G1 and
then says so on stdout rather than passing silently:

    "H-G1 (pyHyp Min Quality > 0 at every layer): NOT GRADED HERE -- it lives in the pyHyp
     log and has its own reader. H-G1 is NOT discharged by this instrument alone."

This is that reader.  Until it existed, H-G1 had a clause with no instrument, and a gate
clause with no instrument is a clause that cannot fail.

WHAT SECTION 7 REGISTERS (H-G1, third clause): mesh admission per level requires
"pyHyp **Min Quality > 0 at every layer**"; label if not met, **NOT A RESULT** for that
level.  The comparison is **STRICT**: a layer at exactly 0.00000 is NOT ">" 0 and is a
failure.  Zero is a degenerate cell, not a marginally acceptable one.

THE GATE HAS A MEASURED FAILING EXAMPLE ALREADY ON DISK, WHICH IS THE STRONGEST FORM OF
"what result would have failed this test?" --
  `verification/runs/CRM_WINGALONE_runs/L1/pyhyp.log`  layer 3, Min Quality **-0.05046**
  `verification/runs/CRM_WINGALONE_runs/L2/pyhyp.log`  layer 3, Min Quality **+0.00743**
Same instrument, same clause, opposite answers, both from real logs this lab produced.
`--demo` runs exactly those two and prints both verdicts.

HOW THE COLUMN IS FOUND, AND WHY NOT BY INDEX AND NOT BY REGEX.
The pyHyp march table is a fixed-width listing whose two-line header names its columns:

    # Grid | CPU  | Sub | KSP | nAvg |  Sl  | Sensor | Sensor | Min     | Min     | ...
    # Lvl  | Time | Its | Its |      |      | Max    | Min    | Quality | Volume  | ...

There are TWO columns whose first header word is "Min" -- **Min Quality** and **Min
Volume**, and they are ADJACENT.  So:
  * the column index is resolved from the log's OWN header, by pairing the two header
    lines cell by cell on the '|' separators and matching the joined name "Min Quality";
    it is NEVER hard-coded, and if the header is absent or ambiguous the reader REFUSES;
  * a row is accepted only if it splits into exactly as many whitespace fields as the
    header has columns, and only if field 0 is an integer grid level;
  * the value is taken **from that column index**, never from "the first negative number
    on the line".  A regex for a negative number would read Min Volume, CPU time or the
    Ratio column as happily as Min Quality.  PLANT B, PLANT C and PLANT D below exist to
    prove this reader does not do that, by building logs on which a sloppy reader fails.

  *(The lab measured this exact failure mode on 2026-09-12 in a different instrument: a
  loose pattern returned 520,192 where the truth was 524,288 -- plausible, and wrong.)*

PLANTED CONTROLS (rule 3).  Every arm plants **INTO THE INPUT** -- it writes a MODIFIED
COPY OF THE LOG TO DISK, **by line index**, and re-runs THE REAL READER (`read_log`,
`grade`) on that file.  Nothing is simulated in memory.  If an arm's expectation is not
met the instrument **REFUSES (exit 2)** and grades nothing.

  PLANT A -- SENSITIVITY, AGAINST A PREDICTED VALUE AND A PREDICTED LAYER.  Overwrite the
    Min Quality cell of ONE NAMED LAYER with PLANT_NEG = -1.234e-03 (the lab's planted
    constant, sign-flipped so it is a failing value).  The reader must (a) return the
    failing verdict, (b) name THAT layer, and (c) report THAT value to 1e-9.  A control
    that merely checks "the verdict changed" passes on any bug that perturbs the answer.
  PLANT A' -- THE WITHHELD ARM.  The same copy written WITHOUT the plant must return the
    passing verdict and report no negative layer.  A reader that always fails is not a
    reader.
  PLANT B -- DISCRIMINATION, ADJACENT COLUMN.  Put PLANT_NEG in **Min Volume** instead.
    The reader must NOT flag it.  A reader off by one column fails here.
  PLANT C -- DISCRIMINATION, "FIRST NEGATIVE ON THE LINE".  Put PLANT_NEG in the **CPU
    Time** column.  The reader must NOT flag it.  A regex-based reader fails here.
  PLANT D -- DISCRIMINATION, COMMENT LINES.  Put PLANT_NEG inside the '#' header block.
    The reader must NOT flag it, and must still find the header.
  PLANT E -- DISCRIMINATION, THE STRICTNESS OF ">".  Set one layer's Min Quality to
    **exactly 0.00000**.  The reader must FAIL that layer.  A reader written with ">=" or
    with a tolerance passes here and is refused.

DECLINING RATHER THAN EMITTING A NUMBER -- "two sources may describe different runs".
H-G1 is graded from TWO logs: `checkMesh` (read by `read_cell_count.py`) and this pyHyp
log.  If they come from different builds, H-G1 is graded on a chimera, and no planted zero
can catch that because both halves are individually valid.  So, when a level directory is
given, this reader asserts the build chain by mtime, in the order pyHyp actually runs:

    surface mesh  <=  pyhyp.log  <=  plot3dToFoam log  <=  checkMesh log

Any inversion, or any missing member, is a **DECLINE (exit 2)**, never a graded number and
never a warning beside one.  It also DECLINES if the directory holds more than one pyHyp
log, and if the log contains more than one march (grid levels that restart rather than
increase by exactly 1 across the repeated headers -- pyHyp reprints the header every 48
rows, which is NOT a second march and must not be mistaken for one).

Exit codes:  0 PASS   1 NOT A RESULT for that level (section 7's H-G1 label)   2 REFUSE/DECLINE
"""
import sys, os, re, shutil, tempfile, glob

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md section 7, H-G1). Do not edit to fit. ---
MIN_QUALITY_FLOOR = 0.0        # section 7: "Min Quality > 0 at every layer" -- STRICT
FIRST_MARCHED_LVL = 2          # pyHyp prints grid level 1 as the surface; marching starts at 2
# --- THE BUILD CHAIN, in the order pyHyp's own pipeline writes it -----------------------------
CHAIN = ['surfMesh.cgns', 'pyhyp.log', 'log.plot3dToFoam', 'log.checkMesh']
RC_FILE = 'pyhyp_rc.txt'       # written by the lab's own launcher; 'PYHYP_RC=0' required
# --- THE PLANTED CONSTANT --------------------------------------------------------------------
PLANT_NEG = -1.234e-03         # the lab's planted magnitude, signed to be a FAILING value
# ---------------------------------------------------------------------------------------------

HDR_RE = re.compile(r'^\s*#\s*(?:Grid|Lvl)\b')


# ------------------------------------------------------------------ header resolution
def resolve_columns(lines):
    """Find the two-line '|'-separated header and return (ncols, index_of_Min_Quality,
    index_of_Min_Volume, header_line_numbers). Raises ValueError if it cannot be resolved
    UNAMBIGUOUSLY -- the reader refuses rather than guessing a column index."""
    pairs = []
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        if not (HDR_RE.match(a) and HDR_RE.match(b)):
            continue
        ca = [c.strip() for c in a.lstrip().lstrip('#').split('|')]
        cb = [c.strip() for c in b.lstrip().lstrip('#').split('|')]
        if len(ca) != len(cb):
            continue
        names = [(x + ' ' + y).strip() for x, y in zip(ca, cb)]
        names = [n for n in names if n != '']
        pairs.append((i, names))
    if not pairs:
        raise ValueError("no pyHyp march header found -- this reader resolves the Min Quality "
                         "column FROM THE HEADER and will not fall back to a fixed index")
    namesets = set(tuple(n for n in nm) for _, nm in pairs)
    if len(namesets) != 1:
        raise ValueError("the log carries %d DIFFERENT march headers; the column layout is "
                         "ambiguous and a graded number would be a guess" % len(namesets))
    names = pairs[0][1]
    iq = [k for k, n in enumerate(names) if n.replace('  ', ' ') == 'Min Quality']
    iv = [k for k, n in enumerate(names) if n.replace('  ', ' ') == 'Min Volume']
    if len(iq) != 1:
        raise ValueError("expected exactly one 'Min Quality' column, found %d in %r"
                         % (len(iq), names))
    if len(iv) != 1:
        raise ValueError("expected exactly one 'Min Volume' column, found %d in %r"
                         % (len(iv), names))
    return len(names), iq[0], iv[0], [i for i, _ in pairs]


# ------------------------------------------------------------------ the reader
def read_log(path):
    """Read the pyHyp march table FROM DISK.
    Returns (layers, ncols, iq, notes) where layers is [(grid_lvl, min_quality), ...]
    in file order. Raises ValueError on anything it will not read."""
    with open(path) as f:
        lines = f.read().splitlines()
    ncols, iq, iv, hdr_lines = resolve_columns(lines)
    layers, notes = [], []
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        t = s.split()
        if len(t) != ncols:
            continue                      # not a march row (banner, warning, blank frame)
        if not re.fullmatch(r'\d+', t[0]):
            continue
        try:
            q = float(t[iq])
        except ValueError:
            raise ValueError("%s:%d: the 'Min Quality' column is not a number: %r"
                             % (path, ln, t[iq]))
        layers.append((int(t[0]), q, ln))
    if not layers:
        raise ValueError("%s: the header was found but NO march row parsed. A reader that "
                         "returns 'no negative layer' from zero rows is a false pass." % path)
    return layers, ncols, iq, notes


def march_is_single(layers):
    """pyHyp reprints the header every 48 rows; that is NOT a second march. A second march
    shows as a grid level that does not increase by exactly 1. Returns (ok, message)."""
    if layers[0][0] != FIRST_MARCHED_LVL:
        return False, ("the first marched grid level is %d, not %d -- this log does not start "
                       "at the first marched layer and may be a fragment"
                       % (layers[0][0], FIRST_MARCHED_LVL))
    for (a, _, la), (b, _, lb) in zip(layers, layers[1:]):
        if b != a + 1:
            return False, ("grid level goes %d -> %d between log lines %d and %d: the file "
                           "holds more than one march, or a truncated one. Two sources that "
                           "may describe different runs are DECLINED, not averaged."
                           % (a, b, la, lb))
    return True, "single march, grid levels %d..%d, %d marched layers" % (
        layers[0][0], layers[-1][0], len(layers))


def grade(layers):
    """Apply section 7's clause. Returns (ok, bad) with bad = [(lvl, q, line), ...]
    STRICT: q > 0. Exactly 0.0 FAILS."""
    bad = [(l, q, ln) for (l, q, ln) in layers if not (q > MIN_QUALITY_FLOOR)]
    return (len(bad) == 0), bad


# ------------------------------------------------------------------ same-run assertions
def build_chain_guard(case_dir, log_path):
    """Assert the pyHyp log belongs to the SAME BUILD as the checkMesh log that
    read_cell_count.py grades. Returns a list of failure strings (empty == ok)."""
    bad = []
    logs = sorted(glob.glob(os.path.join(case_dir, 'pyhyp*.log')))
    if len(logs) != 1:
        bad.append("the level directory holds %d files matching pyhyp*.log %s -- which one "
                   "produced the graded mesh is not determined, so nothing is graded"
                   % (len(logs), [os.path.basename(p) for p in logs]))
    elif os.path.realpath(logs[0]) != os.path.realpath(log_path):
        bad.append("the log given (%s) is not the one in the level directory (%s)"
                   % (log_path, logs[0]))
    rc = os.path.join(case_dir, RC_FILE)
    if not os.path.isfile(rc):
        bad.append("no %s in the level directory: the pyHyp exit status is unknown, and a "
                   "quality table from a run whose rc was never captured is not evidence"
                   % RC_FILE)
    else:
        txt = open(rc).read()
        m = re.search(r'PYHYP_RC\s*=\s*(-?\d+)', txt)
        if not m:
            bad.append("%s does not carry a PYHYP_RC= line" % RC_FILE)
        elif m.group(1) != '0':
            bad.append("%s reports PYHYP_RC=%s: the march did not exit clean"
                       % (RC_FILE, m.group(1)))
    ts = []
    for name in CHAIN:
        p = os.path.join(case_dir, name)
        if not os.path.isfile(p):
            bad.append("the build chain is incomplete: %s is missing from %s. The pyHyp log "
                       "cannot be tied to the checkMesh log that H-G1's other half is graded "
                       "from, so H-G1 is DECLINED rather than graded on two possibly "
                       "different builds." % (name, case_dir))
            ts.append(None)
        else:
            ts.append(os.path.getmtime(p))
    if all(t is not None for t in ts):
        for i in range(len(ts) - 1):
            if ts[i] > ts[i + 1] + 1e-6:
                bad.append("build-chain order violated: %s (%.0f) is NEWER than %s (%.0f). "
                           "pyHyp runs before plot3dToFoam before checkMesh; an inversion "
                           "means these artifacts are not one build."
                           % (CHAIN[i], ts[i], CHAIN[i + 1], ts[i + 1]))
    return bad


# ------------------------------------------------------------------ planting helpers
def _cell_slice(line, ncols, idx):
    """Byte span of field `idx` in a whitespace-separated row, so a plant can REPLACE THAT
    CELL in place and leave every other column byte-identical."""
    spans, pos = [], 0
    for tok in line.split():
        k = line.index(tok, pos)
        spans.append((k, k + len(tok)))
        pos = k + len(tok)
    if len(spans) != ncols:
        raise ValueError("row does not have %d fields" % ncols)
    return spans[idx]


def plant_into_log(src, dst, target_lvl, col, value, ncols):
    """Write a COPY OF THE LOG TO DISK with one cell overwritten, BY LINE INDEX.
    Returns the 1-based line number written."""
    lines = open(src).read().splitlines()
    hit = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        t = s.split()
        if len(t) != ncols or not re.fullmatch(r'\d+', t[0]):
            continue
        if int(t[0]) == target_lvl:
            a, b = _cell_slice(line, ncols, col)
            new = ('%.5f' % value) if abs(value) < 1e3 else ('%.4E' % value)
            new = new.rjust(b - a)
            lines[i] = line[:a] + new + line[b:]
            hit = i + 1
            break
    if hit is None:
        raise ValueError("no march row at grid level %d in %s" % (target_lvl, src))
    with open(dst, 'w') as f:
        f.write("\n".join(lines) + "\n")
    return hit


def plant_into_comment(src, dst):
    lines = open(src).read().splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith('#') and 'Grid' in line:
            lines[i] = line + ('   %.5f' % PLANT_NEG)
            break
    with open(dst, 'w') as f:
        f.write("\n".join(lines) + "\n")


# ------------------------------------------------------------------ controls
def planted_controls(log_path):
    """Plant into a COPY ON DISK, re-run THE REAL READER on it, and refuse if the reader
    cannot see the plant or sees one that is not there. Returns (ok, messages)."""
    msg = []
    layers0, ncols, iq, _ = read_log(log_path)
    _, iv, = 0, iq + 1                       # Min Volume is the column after Min Quality
    ok0, bad0 = grade(layers0)
    target = layers0[len(layers0) // 2][0]   # a mid-march layer, named in advance
    d = tempfile.mkdtemp(prefix='m6h1_minq_')
    try:
        # ---- PLANT A' : the withheld arm, written to disk with NO plant
        wa = os.path.join(d, 'withheld.log')
        shutil.copyfile(log_path, wa)
        la, _, _, _ = read_log(wa)
        okA2, badA2 = grade(la)
        cond_A2 = (okA2 == ok0) and (len(badA2) == len(bad0))
        msg.append("PLANT A' withheld : verdict on the unplanted copy = %s, %d failing layers "
                   "(same as the original) -> %s"
                   % ('PASS' if okA2 else 'FAIL', len(badA2), 'ok' if cond_A2 else 'REFUSE'))

        # ---- PLANT A : sensitivity, against a PREDICTED layer and a PREDICTED value
        pa = os.path.join(d, 'plantA.log')
        ln = plant_into_log(log_path, pa, target, iq, PLANT_NEG, ncols)
        la, _, _, _ = read_log(pa)
        okA, badA = grade(la)
        cond_A = ((not okA) and len(badA) == len(bad0) + 1
                  and any(l == target and abs(q - PLANT_NEG) < 1e-9 for (l, q, _) in badA))
        msg.append("PLANT A  sensitivity: planted %.6f into the Min Quality cell of grid level "
                   "%d (log line %d); reader reports %d failing layers and %s -> %s"
                   % (PLANT_NEG, target, ln, len(badA),
                      ("names level %d at %.6f" % (target, PLANT_NEG)) if cond_A
                      else "DOES NOT name that layer at that value", 'ok' if cond_A else 'REFUSE'))

        # ---- PLANT B : adjacent column (Min Volume) -- must NOT be seen
        pb = os.path.join(d, 'plantB.log')
        plant_into_log(log_path, pb, target, iv, PLANT_NEG, ncols)
        lb, _, _, _ = read_log(pb)
        okB, badB = grade(lb)
        cond_B = (okB == ok0) and (len(badB) == len(bad0))
        msg.append("PLANT B  discrimination (same value in the ADJACENT 'Min Volume' column): "
                   "reader reports %d failing layers, unchanged -> %s"
                   % (len(badB), 'ok' if cond_B else 'REFUSE -- the reader is off by a column'))

        # ---- PLANT C : CPU time column -- a "first negative on the line" reader fails here
        pc = os.path.join(d, 'plantC.log')
        plant_into_log(log_path, pc, target, 1, PLANT_NEG, ncols)
        lc, _, _, _ = read_log(pc)
        okC, badC = grade(lc)
        cond_C = (okC == ok0) and (len(badC) == len(bad0))
        msg.append("PLANT C  discrimination (same value in the CPU-time column): reader reports "
                   "%d failing layers, unchanged -> %s"
                   % (len(badC), 'ok' if cond_C else 'REFUSE -- the reader is reading the first '
                      'negative number on the line, not the Min Quality column'))

        # ---- PLANT D : inside a comment line -- must NOT be seen, header must still resolve
        pd = os.path.join(d, 'plantD.log')
        plant_into_comment(log_path, pd)
        try:
            ld, _, _, _ = read_log(pd)
            okD, badD = grade(ld)
            cond_D = (okD == ok0) and (len(badD) == len(bad0))
            how = "%d failing layers, unchanged" % len(badD)
        except ValueError as e:
            cond_D, how = False, "reader raised %s" % e
        msg.append("PLANT D  discrimination (same value appended to a '#' header line): %s -> %s"
                   % (how, 'ok' if cond_D else 'REFUSE'))

        # ---- PLANT E : exactly 0.0 must FAIL (the clause is '>', not '>=')
        pe = os.path.join(d, 'plantE.log')
        plant_into_log(log_path, pe, target, iq, 0.0, ncols)
        le, _, _, _ = read_log(pe)
        okE, badE = grade(le)
        cond_E = (not okE) and any(l == target and q == 0.0 for (l, q, _) in badE)
        msg.append("PLANT E  strictness ('> 0', not '>= 0'): planted EXACTLY 0.00000 at grid "
                   "level %d; reader %s -> %s"
                   % (target, "FAILS that layer" if cond_E else "PASSES that layer",
                      'ok' if cond_E else 'REFUSE -- the clause is strict and this reader is not'))

        good = cond_A and cond_A2 and cond_B and cond_C and cond_D and cond_E
        return good, msg
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------ main
def main(log_path, case_dir=None):
    print("M6H1 H-G1, pyHyp clause -- Min Quality at EVERY marched layer, read from the log")
    print("LOG:   %s" % log_path)
    print("REGISTERED (section 7, H-G1): Min Quality > %.1f at every layer, STRICT. "
          "Label if not met: NOT A RESULT for that level.\n" % MIN_QUALITY_FLOOR)

    if not os.path.isfile(log_path):
        print("REFUSE (exit 2): no pyHyp log at %s." % log_path)
        return 2

    if case_dir:
        bad = build_chain_guard(case_dir, log_path)
        if bad:
            print("SAME-RUN / BUILD-CHAIN ASSERTION")
            for b in bad:
                print("  " + b)
            print("\nDECLINE (exit 2): this pyHyp log is not tied to the checkMesh log that "
                  "H-G1's other half is graded from. Two sources that may describe different "
                  "runs are declined, never combined.")
            return 2
        print("BUILD CHAIN: %s -- in order, one build." % ' <= '.join(CHAIN))

    try:
        layers, ncols, iq, _ = read_log(log_path)
    except ValueError as e:
        print("REFUSE (exit 2): %s" % e)
        return 2
    single, how = march_is_single(layers)
    print("MARCH: %s" % how)
    if not single:
        print("\nDECLINE (exit 2): %s" % how)
        return 2
    print("COLUMN: 'Min Quality' resolved from the log's own header as field %d of %d.\n"
          % (iq, ncols))

    ok, msgs = planted_controls(log_path)
    print("PLANTED CONTROLS -- planted INTO A COPY OF THE LOG ON DISK, real reader re-run FROM DISK")
    for m in msgs:
        print("  " + m)
    if not ok:
        print("\nREFUSE (exit 2): the controls did not establish that this reader sees a known "
              "plant in the Min Quality column, does not see one placed in a neighbouring "
              "column or a comment, and treats the clause as strict. No verdict below would "
              "be evidence.")
        return 2

    passed, bad = grade(layers)
    qs = [q for (_, q, _) in layers]
    print("\n  marched layers: %d   min over all layers: %.5f at grid level %d"
          % (len(layers), min(qs), layers[qs.index(min(qs))][0]))
    if bad:
        print("  layers at or below the floor:")
        for (l, q, ln) in bad:
            print("    grid level %-4d Min Quality %+.5f   (log line %d)" % (l, q, ln))
        print("\nH-G1 (pyHyp Min Quality > 0 at every layer): NOT A RESULT for this level. "
              "Reported, NOT adjusted.")
        return 1
    print("\nH-G1 (pyHyp Min Quality > 0 at every layer): PASS")
    print("H-G1 is NOT discharged by this instrument alone -- the checkMesh half "
          "(non-orthogonality, skewness, negative volumes, cell count) is read_cell_count.py.")
    return 0


# ------------------------------------------------------------------ demo on real logs
DEMO = [("verification/runs/CRM_WINGALONE_runs/L1/pyhyp.log", 1,
         "L1: the lab measured Min Quality -0.05046 at layer 3"),
        ("verification/runs/CRM_WINGALONE_runs/L2/pyhyp.log", 0,
         "L2: the lab measured Min Quality +0.00743 at layer 3")]


def demo(root):
    print("=" * 100)
    print("BOTH-ANSWERS DEMONSTRATION ON REAL pyHyp LOGS THIS LAB PRODUCED (no case_dir, so the")
    print("build-chain guard is not exercised here; --selftest and main() carry that separately)")
    print("=" * 100)
    good = True
    for rel, want, what in DEMO:
        p = os.path.join(root, rel)
        print("\n### %s\n### %s" % (what, p))
        if not os.path.isfile(p):
            print("    MISSING -- cannot demonstrate; this is a failure of the demonstration, "
                  "not a pass.")
            good = False
            continue
        rc = main(p)
        print("    rc = %d, expected %d -> %s" % (rc, want, 'ok' if rc == want else 'MISMATCH'))
        good = good and (rc == want)
    print("\n" + "=" * 100)
    print("DEMONSTRATION %s -- the instrument returns BOTH the failing and the passing verdict "
          "from REAL logs, not from synthetic ones" % ('PASS' if good else 'FAIL'))
    return 0 if good else 1


# ------------------------------------------------------------------ selftest
def _synth(path, rows, ncols=14):
    """Build a minimal, well-formed pyHyp log so the selftest can exercise the refusals on
    inputs whose defect is known by construction."""
    h = ("#" + "-" * 115 + "\n"
         "# Grid | CPU  | Sub | KSP | nAvg |  Sl  | Sensor | Sensor | Min     | Min     |"
         "  deltaS  | March    | cMax  | Ratio |\n"
         "# Lvl  | Time | Its | Its |      |      | Max    | Min    | Quality | Volume  |"
         "          | Distance |       | kMax  |\n"
         "#" + "-" * 115 + "\n")
    body = ""
    for (lvl, q) in rows:
        body += ("%7d %6.1f %5d %5d %6d %6.3f %8.5f %8.5f %8.5f %10.3E %10.3E %10.3E "
                 "%7.4f %6.4f \n" % (lvl, 0.1, 2, 6, 0, 0.157, 1.0, 0.2, q,
                                     1.6e-10, 2.1e-4, 4.0e-4, 0.29, 1.0))
    open(path, 'w').write(h + body)


def selftest():
    root = os.path.dirname(os.path.abspath(__file__))
    d = tempfile.mkdtemp(prefix='m6h1_minq_st_')
    res = []
    try:
        good_rows = [(l, 0.30) for l in range(2, 12)]
        g = os.path.join(d, 'good.log'); _synth(g, good_rows)
        b = os.path.join(d, 'bad.log');  _synth(b, [(l, 0.30 if l != 5 else -0.02)
                                                    for l in range(2, 12)])

        # ARM 1 -- the gate must return PASS
        res.append(("ARM 1  a clean march grades PASS", main(g) == 0))
        # ARM 2 -- and it must return the FAILING label
        res.append(("ARM 2  a march with one negative layer grades NOT A RESULT", main(b) == 1))
        # ARM 3 -- the controls themselves
        okc, _ = planted_controls(g)
        res.append(("ARM 3  all planted controls hold on a clean log", okc))
        # ARM 4 -- exactly zero must fail (strictness), via the real reader from disk
        z = os.path.join(d, 'zero.log'); _synth(z, [(l, 0.30 if l != 7 else 0.0)
                                                    for l in range(2, 12)])
        res.append(("ARM 4  a layer at EXACTLY 0.00000 grades NOT A RESULT", main(z) == 1))
        # ARM 5 -- a log with no header must REFUSE, not fall back to a fixed column index
        nh = os.path.join(d, 'nohdr.log')
        open(nh, 'w').write("\n".join(l for l in open(g).read().splitlines()
                                      if not l.lstrip().startswith('#')) + "\n")
        res.append(("ARM 5  a log with the header stripped REFUSES (no fixed-index fallback)",
                    main(nh) == 2))
        # ARM 6 -- two marches in one file must DECLINE
        tm = os.path.join(d, 'two.log')
        open(tm, 'w').write(open(g).read() + open(g).read())
        res.append(("ARM 6  two marches concatenated DECLINE", main(tm) == 2))
        # ARM 7 -- a march that does not start at the first marched level DECLINES
        fr = os.path.join(d, 'frag.log'); _synth(fr, [(l, 0.30) for l in range(6, 16)])
        res.append(("ARM 7  a march starting at level 6, not %d, DECLINES" % FIRST_MARCHED_LVL,
                    main(fr) == 2))
        # ARM 8 -- an empty table (header only) REFUSES rather than passing on zero rows
        et = os.path.join(d, 'empty.log'); _synth(et, [])
        res.append(("ARM 8  header with NO march rows REFUSES (a false pass from zero rows)",
                    main(et) == 2))
        # ARM 9 -- the build-chain guard declines on an inverted chain, and passes on a good one
        cd = os.path.join(d, 'case'); os.makedirs(cd)
        shutil.copyfile(g, os.path.join(cd, 'pyhyp.log'))
        open(os.path.join(cd, RC_FILE), 'w').write('PYHYP_RC=0\n')
        import time
        for k, name in enumerate(CHAIN):
            p = os.path.join(cd, name)
            if not os.path.exists(p):
                open(p, 'w').write('x')
            os.utime(p, (1000 + k, 1000 + k))
        res.append(("ARM 9  an in-order build chain does NOT decline",
                    main(os.path.join(cd, 'pyhyp.log'), cd) == 0))
        os.utime(os.path.join(cd, 'log.checkMesh'), (900, 900))   # checkMesh older than pyHyp
        res.append(("ARM 10 an INVERTED build chain DECLINES",
                    main(os.path.join(cd, 'pyhyp.log'), cd) == 2))
        os.utime(os.path.join(cd, 'log.checkMesh'), (1003, 1003))
        shutil.copyfile(g, os.path.join(cd, 'pyhyp_second.log'))
        res.append(("ARM 11 TWO pyhyp*.log files in one level directory DECLINE",
                    main(os.path.join(cd, 'pyhyp.log'), cd) == 2))
        os.remove(os.path.join(cd, 'pyhyp_second.log'))
        open(os.path.join(cd, RC_FILE), 'w').write('PYHYP_RC=1\n')
        res.append(("ARM 12 PYHYP_RC != 0 DECLINES", main(os.path.join(cd, 'pyhyp.log'), cd) == 2))
        open(os.path.join(cd, RC_FILE), 'w').write('PYHYP_RC=0\n')
        os.remove(os.path.join(cd, 'log.plot3dToFoam'))
        res.append(("ARM 13 a MISSING build-chain member DECLINES",
                    main(os.path.join(cd, 'pyhyp.log'), cd) == 2))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("\n" + "=" * 100)
    for name, ok in res:
        print("  %-78s %s" % (name, 'ok' if ok else 'FAIL'))
    allok = all(ok for _, ok in res)
    print("\nSELFTEST %s -- the reader SEES a plant in the Min Quality column against a "
          "PREDICTED layer and value, does NOT see one in the adjacent column, the CPU column "
          "or a comment, treats '> 0' as strict, REFUSES a headerless log rather than "
          "falling back to a fixed index, DECLINES two marches, a fragment, an empty table "
          "and a broken build chain, and demonstrably returns BOTH PASS and NOT A RESULT"
          % ('PASS' if allok else 'FAIL'))
    return 0 if allok else 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        sys.exit(demo(sys.argv[2] if len(sys.argv) > 2 else os.getcwd()))
    if len(sys.argv) < 2:
        sys.exit("usage: read_min_quality.py <pyhyp.log> [level_dir_for_build_chain_guard]\n"
                 "       read_min_quality.py --selftest\n"
                 "       read_min_quality.py --demo [repo_root]")
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
