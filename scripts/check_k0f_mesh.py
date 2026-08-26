#!/usr/bin/env python3
"""K0d mesh verification -- refusal conditions A-G, EVERY MESH-JUDGING ONE READ
FROM DISK.  See the docstring correction recorded in AMENDMENT 2 section A2.3.

Written 2026-08-25 from the FROZEN registration and from nothing else:
  docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md   section 5, 5.1
  docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md  section 4 (adopted unchanged)

"Every mesh is read from constant/polyMesh BEFORE any solver runs, against
refusal conditions A-G -- including condition G, the planted-positive test: an
inverted grading and a slot one cell short are each injected and each must be
REFUSED."  (re-registration 5.1)

    A  total cell count equals the design value exactly on each level
    B  the inlet slot spans >= 10/14/20 cells (L1/L2/L3), the outlet >= 12/17/24
    C  every block's cell count scales by 1.40 +/- 0.05 between consecutive
       levels, COUNTED FROM THE MESH (see the A2.3 note below)
    D  the first wall-normal cell equals the design value to 1% AND is the
       smallest wall-normal cell in its block
    E  each graded half is geometric to 1e-6
    F  block heights sum to 1.040 m and block widths to 1.040 m, to 1e-9
    G  the planted-positive test FIRES

T1b attempt 1 lost 57 core-hours to a grading direction nobody read from disk.
This rung reads it.

AMENDMENT 2, SECTION A2.3 -- THE DOCSTRING THIS FILE USED TO CARRY WAS FALSE.
Until 2026-08-25 this docstring asserted "refusal conditions A-G, every one READ
FROM DISK", and CONDITION C DID NOT READ THE MESH: main() called it as
condition_C(None, LEVELS[lo], None, LEVELS[hi]) -- both mesh arguments None --
so at run time it was a TAUTOLOGY OVER THIS SCRIPT'S OWN CONSTANTS and could not
fail on any real mesh.  The selftest hid it by planting into a MODIFIED SPEC
(dict(LEVELS["L2"], nB=400)) rather than a modified mesh: a planted control
planted into the wrong channel.  BOTH SELFTESTS PASSED AND THE BLINDNESS CHECKER
REPORTED CLEAN THROUGHOUT -- a green selftest is not a green instrument.

The hole was exploitable, not theoretical: a mesh redistributing cells between
blocks A/B/C while holding Ny = nA+nB+nC and Nx*Ny passes condition A (total
cells, from disk), passes condition B (slot minimums tested with >=, so a LARGER
slot passes), and condition C never looked.  Block B is the CAVITY INTERIOR, and
condition C underwrites the refinement ratio the entire Roache triple rests on
(standing rule 5).

AS REPAIRED:
  * condition_C COUNTS EACH BLOCK'S CELLS FROM THE MESH and REFUSES to run at
    all if a mesh is missing.  It never falls back to LEVELS -- that fallback
    WAS the defect.
  * condition_C_spec keeps the registered-table check and is LABELLED AS NOT A
    CHECK ON THE MESH.  The two are reported separately so no reader can mistake
    one for the other.
  * the planted control PLANTS INTO THE MESH: synthetic_mesh(..., redistribute=k)
    moves k cells out of block B into blocks A and C, holding Ny and Nx*Ny and
    both slot minimums, and the selftest asserts REPAIRED CONDITION C REFUSES IT
    WHILE CONDITIONS A AND B BOTH STAY QUIET.  That assertion is the proof the
    hole is closed.
  * a single-level invocation now SAYS condition C was not evaluated.  A check
    omitted in silence reads as a check passed.

CONDITION G IS NOT OPTIONAL AND IS NOT A SEPARATE MODE.  It runs on every
invocation, BEFORE the real mesh is judged, and a run in which the planted
defects are NOT refused REFUSES the whole check (exit 2): a condition never
shown able to fire is not evidence (standing rule 3).

Exit codes:  0  every condition holds on every level presented
             1  a condition FAILED on a real mesh
             2  REFUSAL -- condition G did not fire, or the mesh could not be
                read, or a level was named that is not registered

Usage:
    python3 check_k0f_mesh.py --case <case dir> --level L1|L2|L3
    python3 check_k0f_mesh.py --root <K0f_runs dir>      # all present cases
    python3 check_k0f_mesh.py --selftest
"""
import argparse
import os
import re
import sys

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS -- superseded section 4 table, adopted unchanged by
# re-registration section 5, with the FIRST WALL CELL COLUMN RE-DERIVED at
# nu = 1.569e-5 in re-registration section 5.1 (the superseded column at
# nu = 1.55e-5 is NOT used: it is 1.2258 % away, and condition D's tolerance
# is 1 %, so carrying it across would have refused every level).
# --------------------------------------------------------------------------
DOMAIN = 1.040                      # m, both x and y (superseded 3.1)
BLOCK_Y = {                         # superseded section 4
    "A": (0.000, 0.024),            # outlet band
    "B": (0.024, 1.022),            # cavity interior
    "C": (1.022, 1.040),            # inlet band
}
INLET_Y = (1.022, 1.040)            # superseded 3.1 / A5.2
OUTLET_Y = (0.000, 0.024)

LEVELS = {
    #        Nx    nA   nB   nC   Ny    cells   first wall cell (m)
    "L1": dict(Nx=160, nA=12, nB=138, nC=10, Ny=160, cells=25600,
               first_cell=1.101053e-03, inlet_min=10, outlet_min=12),
    "L2": dict(Nx=224, nA=18, nB=192, nC=14, Ny=224, cells=50176,
               first_cell=7.864662e-04, inlet_min=14, outlet_min=17),
    "L3": dict(Nx=314, nA=24, nB=270, nC=20, Ny=314, cells=98596,
               first_cell=5.610459e-04, inlet_min=20, outlet_min=24),
}
LEVEL_ORDER = ["L1", "L2", "L3"]

COND_D_TOL_PCT = 1.0                # superseded 4, condition D
COND_E_TOL = 1e-6                   # superseded 4, condition E
COND_F_TOL = 1e-9                   # superseded 4, condition F
COND_C_RATIO, COND_C_TOL = 1.40, 0.05

# The mesh-planted condition-C control moves this many cells out of block B
# (the cavity interior) into blocks A and C, holding Ny and Nx*Ny and both slot
# minimums.  AMENDMENT 2 section A2.3, repair item 3.
REDISTRIBUTE_K = 20

# re-registration 5.2 / A1.2b: which level each case sits on.
CASE_LEVEL = {
    "M1_c": "L1", "M1_m": "L2", "M1_f": "L3",
    "M2_c": "L1", "M2_m": "L2", "M2_f": "L3",
    "C_lam": "L2", "B_hi": "L2", "I_hi": "L2", "M1_m_seed": "L2",
}


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# polyMesh readers -- pure standard library, ascii
# --------------------------------------------------------------------------
def _strip_foam(txt):
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", "", txt)
    txt = re.sub(r"FoamFile\s*\{.*?\}", "", txt, flags=re.S)
    return txt


def read_points(polymesh):
    """Return the list of (x, y, z) vertices of constant/polyMesh/points."""
    p = os.path.join(polymesh, "points")
    if not os.path.isfile(p):
        return None
    txt = _strip_foam(open(p, errors="replace").read())
    pts = [(float(a), float(b), float(c)) for a, b, c in
           re.findall(r"\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)", txt)]
    return pts or None


def read_n_cells(polymesh):
    """Cell count from constant/polyMesh/owner -- max label + 1, cross-checked
    against the header note when one is present."""
    p = os.path.join(polymesh, "owner")
    if not os.path.isfile(p):
        return None
    raw = open(p, errors="replace").read()
    note = re.search(r"nCells:\s*(\d+)", raw)
    txt = _strip_foam(raw)
    m = re.search(r"^\s*(\d+)\s*\n\s*\(", txt, re.M)
    if not m:
        return int(note.group(1)) if note else None
    body = txt[m.end():]
    labels = [int(x) for x in re.findall(r"-?\d+", body.split(")")[0])]
    n = (max(labels) + 1) if labels else None
    if note and n is not None and int(note.group(1)) != n:
        refuse(f"owner header says nCells {note.group(1)} but the labels give "
               f"{n}; the mesh file disagrees with itself")
    return n if n is not None else (int(note.group(1)) if note else None)


def unique_axis(pts, axis, tol=1e-10):
    """The sorted distinct coordinate lines along `axis` (0=x, 1=y)."""
    vals = sorted(set(round(p[axis] / tol) * tol for p in pts))
    out = [vals[0]]
    for v in vals[1:]:
        if v - out[-1] > tol * 10:
            out.append(v)
    return out


# --------------------------------------------------------------------------
# the conditions.  Each takes an already-read mesh so that condition G can
# present a SYNTHETIC mesh to exactly the same code path.
# --------------------------------------------------------------------------
def _spacings(lines):
    return [lines[i + 1] - lines[i] for i in range(len(lines) - 1)]


def _count_between(lines, lo, hi, tol=1e-9):
    """Number of cells whose extent lies within [lo, hi]."""
    inside = [v for v in lines if lo - tol <= v <= hi + tol]
    return max(len(inside) - 1, 0)


def _is_geometric(sp, tol):
    """Is `sp` a geometric sequence to relative tolerance `tol`?"""
    if len(sp) < 3:
        return True, 0.0
    ratios = [sp[i + 1] / sp[i] for i in range(len(sp) - 1)]
    mean = sum(ratios) / len(ratios)
    if mean == 0:
        return False, float("inf")
    dev = max(abs(r - mean) / mean for r in ratios)
    return dev <= tol, dev


def condition_A(mesh, spec):
    n = mesh["n_cells"]
    if n is None:
        return False, "cell count could not be read from owner"
    return n == spec["cells"], f"{n} cells, design {spec['cells']}"


def condition_B(mesh, spec):
    yl = mesh["y_lines"]
    n_in = _count_between(yl, *INLET_Y)
    n_out = _count_between(yl, *OUTLET_Y)
    ok = n_in >= spec["inlet_min"] and n_out >= spec["outlet_min"]
    return ok, (f"inlet slot {n_in} cells (>= {spec['inlet_min']}), "
                f"outlet slot {n_out} cells (>= {spec['outlet_min']})")


def block_cells_from_mesh(mesh):
    """Cells per registered BLOCK_Y band, COUNTED FROM THE MESH.

    Nx is taken as len(x_lines) - 1 and each block's y-cell count with
    _count_between -- the SAME disk-reading helper condition B already uses.
    Nothing here consults LEVELS.  (AMENDMENT 2 section A2.3, repair item 1.)
    """
    nx = len(mesh["x_lines"]) - 1
    counts = {}
    for blk, (lo, hi) in BLOCK_Y.items():
        counts[blk] = nx * _count_between(mesh["y_lines"], lo, hi)
    return counts, nx


def condition_C(mesh_lo, mesh_hi):
    """Per-BLOCK cell-count scaling between consecutive levels, COUNTED FROM
    THE MESH.

    THIS FUNCTION REFUSES TO RUN WITHOUT BOTH MESHES.  It does NOT fall back to
    the registered LEVELS table when a mesh is absent: that fallback was the
    defect AMENDMENT 2 section A2.3 registers, and a silent fallback would
    restore it.  The registered-table check lives in condition_C_spec and is
    reported separately.
    """
    if mesh_lo is None or mesh_hi is None:
        raise ValueError(
            "condition_C requires BOTH meshes read from disk; it must never be "
            "called with None (AMENDMENT 2 section A2.3)")
    lo_counts, nx_lo = block_cells_from_mesh(mesh_lo)
    hi_counts, nx_hi = block_cells_from_mesh(mesh_hi)
    bad, notes = [], []
    for blk in ("A", "B", "C"):
        lo, hi = lo_counts[blk], hi_counts[blk]
        if lo <= 0 or hi <= 0:
            bad.append(blk)
            notes.append(f"block {blk} {lo}->{hi} EMPTY IN THE MESH")
            continue
        r = (hi / lo) ** 0.5           # linear ratio from the 2D cell counts
        notes.append(f"block {blk} {lo}->{hi}, r={r:.4f}")
        if abs(r - COND_C_RATIO) > COND_C_TOL:
            bad.append(blk)
    head = f"[FROM THE MESH, Nx {nx_lo}->{nx_hi}] "
    return not bad, head + "; ".join(notes) + (
        f"  OUTSIDE {COND_C_RATIO}+/-{COND_C_TOL}: {bad}" if bad else "")


def condition_C_spec(spec_lo, spec_hi):
    """THE REGISTERED TABLE'S OWN SCALING.  THIS IS NOT A CHECK ON THE MESH.

    Verifying that the REGISTERED LEVELS table scales by 1.40 is worth doing --
    it is simply a check on this script's constants, not on any mesh on disk.
    It is kept, and it is labelled, so that no reader can mistake it for
    condition C (AMENDMENT 2 section A2.3, repair item 2).
    """
    bad, notes = [], []
    for blk in ("A", "B", "C"):
        key = {"A": "nA", "B": "nB", "C": "nC"}[blk]
        lo = spec_lo["Nx"] * spec_lo[key]
        hi = spec_hi["Nx"] * spec_hi[key]
        r = (hi / lo) ** 0.5
        notes.append(f"block {blk} {lo}->{hi}, r={r:.4f}")
        if abs(r - COND_C_RATIO) > COND_C_TOL:
            bad.append(blk)
    head = "[REGISTERED TABLE -- NOT A CHECK ON THE MESH] "
    return not bad, head + "; ".join(notes) + (
        f"  OUTSIDE {COND_C_RATIO}+/-{COND_C_TOL}: {bad}" if bad else "")


def condition_D(mesh, spec):
    """First wall-normal cell at each of the four walls, to 1 %, AND smallest
    in its block."""
    target = spec["first_cell"]
    yl, xl = mesh["y_lines"], mesh["x_lines"]
    checks = []
    # floor  (y = 0, block A bottom) and ceiling (y = 1.04, block C top)
    a_lines = [v for v in yl if BLOCK_Y["A"][0] - 1e-9 <= v <= BLOCK_Y["A"][1] + 1e-9]
    c_lines = [v for v in yl if BLOCK_Y["C"][0] - 1e-9 <= v <= BLOCK_Y["C"][1] + 1e-9]
    a_sp, c_sp = _spacings(a_lines), _spacings(c_lines)
    x_sp = _spacings(xl)
    if not (a_sp and c_sp and x_sp):
        return False, "a block has fewer than two coordinate lines"
    checks.append(("floor", a_sp[0], a_sp))
    checks.append(("ceiling", c_sp[-1], c_sp))
    checks.append(("leftWall", x_sp[0], x_sp))
    checks.append(("rightWall", x_sp[-1], x_sp))
    bad, notes = [], []
    for name, first, block in checks:
        pct = 100.0 * abs(first - target) / target
        smallest = first <= min(block) * (1.0 + 1e-9)
        notes.append(f"{name} {first:.6e} ({pct:.3f}% off)"
                     + ("" if smallest else " NOT SMALLEST IN BLOCK"))
        if pct > COND_D_TOL_PCT or not smallest:
            bad.append(name)
    return not bad, "; ".join(notes) + (f"  FAILED: {bad}" if bad else "")


def condition_E(mesh, spec):
    """Each graded half geometric to 1e-6.  Halves are taken at the midpoint of
    each block in y and of the domain in x -- 'two-sided geometric grading to
    every wall and to both slot lips' (superseded section 4)."""
    bad, notes = [], []
    groups = [("x", mesh["x_lines"], 0.0, DOMAIN)]
    for blk, (lo, hi) in BLOCK_Y.items():
        groups.append((f"y{blk}", [v for v in mesh["y_lines"]
                                   if lo - 1e-9 <= v <= hi + 1e-9], lo, hi))
    for name, lines, lo, hi in groups:
        mid = 0.5 * (lo + hi)
        lower = [v for v in lines if v <= mid + 1e-12]
        upper = [v for v in lines if v >= mid - 1e-12]
        for half, seq in (("lo", lower), ("hi", upper)):
            sp = _spacings(seq)
            ok, dev = _is_geometric(sp, COND_E_TOL)
            notes.append(f"{name}.{half} dev={dev:.2e}")
            if not ok:
                bad.append(f"{name}.{half}")
    return not bad, "; ".join(notes) + (f"  NOT GEOMETRIC: {bad}" if bad else "")


def condition_F(mesh, spec):
    xl, yl = mesh["x_lines"], mesh["y_lines"]
    w = xl[-1] - xl[0]
    h = yl[-1] - yl[0]
    blocks = sum(hi - lo for lo, hi in BLOCK_Y.values())
    ok = (abs(w - DOMAIN) <= COND_F_TOL and abs(h - DOMAIN) <= COND_F_TOL
          and abs(blocks - DOMAIN) <= COND_F_TOL)
    return ok, (f"width {w:.9f}, height {h:.9f}, block heights sum "
                f"{blocks:.9f}, design {DOMAIN:.9f}")


# --------------------------------------------------------------------------
# synthetic mesh construction, used by condition G and by --selftest
# --------------------------------------------------------------------------
def _two_sided(lo, hi, n, first):
    """A two-sided geometric distribution over [lo, hi] with n cells whose
    first cell at EACH end is `first`.  Solved by bisection on the expansion."""
    half_n, rem = divmod(n, 2)
    def build(m, length):
        if m <= 1:
            return [length]
        r_lo, r_hi = 1.0 + 1e-12, 4.0
        for _ in range(200):
            r = 0.5 * (r_lo + r_hi)
            s = first * (r ** m - 1.0) / (r - 1.0)
            if s > length:
                r_hi = r
            else:
                r_lo = r
        r = 0.5 * (r_lo + r_hi)
        cells = [first * r ** i for i in range(m)]
        scale = length / sum(cells)
        return [c * scale for c in cells]
    half_len = 0.5 * (hi - lo)
    lower = build(half_n, half_len)
    upper = build(half_n + rem, (hi - lo) - half_len)[::-1]
    lines, v = [lo], lo
    for c in lower + upper:
        v += c
        lines.append(v)
    lines[-1] = hi
    return lines


def synthetic_mesh(level, invert_grading=False, short_slot=False,
                   redistribute=0):
    """A mesh that satisfies A-F, or one with exactly one defect injected.

    `redistribute=k` MOVES k CELLS OUT OF BLOCK B (the cavity interior) AND
    PUTS THEM INTO BLOCKS A AND C.  This is the mesh-planted control for the
    repaired condition C (AMENDMENT 2 section A2.3, repair item 3):

      * Ny = nA + nB + nC is UNCHANGED, so Nx*Ny is unchanged and CONDITION A
        (total cell count, read from disk) STAYS QUIET;
      * both slots get LARGER, and condition B tests its minimums with >=, so
        CONDITION B STAYS QUIET;
      * block B is under-resolved by k*Nx cells and NOTHING ELSE CAN SEE IT.

    Repaired condition C must REFUSE this mesh.  If A or B fires on it, the
    control is wrong and the proof that the hole is closed is not made.
    """
    spec = LEVELS[level]
    x = _two_sided(0.0, DOMAIN, spec["Nx"], spec["first_cell"])
    y = []
    counts = {"A": spec["nA"], "B": spec["nB"], "C": spec["nC"]}
    if short_slot:
        counts["C"] -= 1                       # the inlet slot, one cell short
    if redistribute:
        k = int(redistribute)
        to_a, to_c = k - k // 2, k // 2
        counts["B"] -= k
        counts["A"] += to_a
        counts["C"] += to_c
        if counts["B"] < 3:
            raise ValueError("redistribute would empty block B")
    for blk in ("A", "B", "C"):
        lo, hi = BLOCK_Y[blk]
        seg = _two_sided(lo, hi, counts[blk], spec["first_cell"])
        y.extend(seg if not y else seg[1:])
    if invert_grading:
        # THE GRADING DIRECTION INVERTED: coarse AT THE WALLS, fine in the
        # middle of each block.  Cell COUNT and domain extent are untouched, so
        # conditions A, B and F cannot see it and only D can -- which is the
        # whole point of reading the grading from disk rather than trusting the
        # blockMeshDict that was meant to produce it (T1b attempt 1, 57 core-h).
        #
        # Note that merely REVERSING a two-sided distribution reproduces it
        # exactly, because it is symmetric.  The inversion therefore reverses
        # each HALF of each block independently, which is the defect a
        # hand-written reciprocal gets wrong in practice (L-142).
        def invert(lines):
            lo, hi = lines[0], lines[-1]
            sp = _spacings(lines)
            h = len(sp) // 2
            sp = sp[:h][::-1] + sp[h:][::-1]
            out, v = [lo], lo
            for c in sp:
                v += c
                out.append(v)
            out[-1] = hi
            return out
        y2 = []
        for blk in ("A", "B", "C"):
            lo, hi = BLOCK_Y[blk]
            seg = [v for v in y if lo - 1e-12 <= v <= hi + 1e-12]
            seg = invert(seg)
            y2.extend(seg if not y2 else seg[1:])
        y = y2
        x = invert(x)
    n = (len(x) - 1) * (len(y) - 1)
    return dict(x_lines=x, y_lines=y, n_cells=n, level=level)


def condition_G():
    """THE PLANTED-POSITIVE TEST.  Inject an inverted grading and a slot one
    cell short and require each to be REFUSED by the same conditions that
    judge the real mesh.  Also require the CLEAN synthetic mesh to be accepted:
    a condition that flags everything is as useless as one that flags nothing.
    Returns (fired, notes)."""
    notes, fired = [], True
    for level in LEVEL_ORDER:
        spec = LEVELS[level]
        clean = synthetic_mesh(level)
        okD, _ = condition_D(clean, spec)
        okB, _ = condition_B(clean, spec)
        if not (okD and okB):
            notes.append(f"{level}: the CLEAN synthetic mesh is not accepted "
                         f"(D={okD}, B={okB}) -- the planted control is "
                         f"uninformative")
            fired = False
        inv = synthetic_mesh(level, invert_grading=True)
        okD_inv, dinv = condition_D(inv, spec)
        if okD_inv:
            notes.append(f"{level}: an INVERTED GRADING was NOT refused by D")
            fired = False
        short = synthetic_mesh(level, short_slot=True)
        okB_short, _ = condition_B(short, spec)
        if okB_short:
            notes.append(f"{level}: a SLOT ONE CELL SHORT was NOT refused by B")
            fired = False

    # THE MESH-PLANTED CONDITION-C CONTROL (AMENDMENT 2 section A2.3, repair
    # item 3).  Clean L1 against an L2 mesh with REDISTRIBUTE_K cells moved out
    # of block B into blocks A and C.  Repaired C must REFUSE it; A and B must
    # BOTH STAY QUIET, because a control that trips another condition proves
    # nothing about this one.
    lo_clean = synthetic_mesh("L1")
    hi_redis = synthetic_mesh("L2", redistribute=REDISTRIBUTE_K)
    okC_clean, nC_clean = condition_C(lo_clean, synthetic_mesh("L2"))
    if not okC_clean:
        notes.append("the CLEAN L1->L2 synthetic pair is REFUSED by condition C "
                     "-- the planted control is uninformative: " + nC_clean)
        fired = False
    okA_r, nA_r = condition_A(hi_redis, LEVELS["L2"])
    okB_r, nB_r = condition_B(hi_redis, LEVELS["L2"])
    okC_r, nC_r = condition_C(lo_clean, hi_redis)
    if not okA_r:
        notes.append("condition A FIRED on the redistribution control -- the "
                     "control is wrong, not the instrument: " + nA_r)
        fired = False
    if not okB_r:
        notes.append("condition B FIRED on the redistribution control -- the "
                     "control is wrong, not the instrument: " + nB_r)
        fired = False
    if okC_r:
        notes.append("A BLOCK REDISTRIBUTION WAS NOT REFUSED BY CONDITION C. "
                     "The condition-C hole of AMENDMENT 2 section A2.3 is OPEN: "
                     + nC_r)
        fired = False
    elif okA_r and okB_r:
        notes.append(f"condition C REFUSES a {REDISTRIBUTE_K}-cell block "
                     f"redistribution that A and B BOTH let through "
                     f"({nC_r[:80]})")

    if fired:
        notes.append("inverted grading refused by D, short slot refused by "
                     "B on all three levels, block redistribution refused by C; "
                     "clean synthetic mesh and clean level pair both accepted")
    return fired, notes


# --------------------------------------------------------------------------
def judge(mesh, level):
    spec = LEVELS[level]
    rows = [("A", *condition_A(mesh, spec)),
            ("B", *condition_B(mesh, spec)),
            ("D", *condition_D(mesh, spec)),
            ("E", *condition_E(mesh, spec)),
            ("F", *condition_F(mesh, spec))]
    return rows


def load_case(case_dir):
    pm = os.path.join(case_dir, "constant", "polyMesh")
    pts = read_points(pm)
    if pts is None:
        return None
    return dict(x_lines=unique_axis(pts, 0), y_lines=unique_axis(pts, 1),
                n_cells=read_n_cells(pm))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case")
    ap.add_argument("--level")
    ap.add_argument("--root")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    # --- CONDITION G FIRST, ALWAYS ------------------------------------
    fired, notes = condition_G()
    print("condition G (planted positive):")
    for n in notes:
        print("   " + n)
    if not fired:
        refuse("condition G did not fire.  A mesh check not shown able to "
               "REFUSE a defective mesh cannot certify a good one "
               "(standing rule 3).")
    print()

    targets = []
    if a.case:
        lvl = a.level or CASE_LEVEL.get(os.path.basename(a.case.rstrip("/")))
        if lvl not in LEVELS:
            refuse(f"level {lvl!r} is not one of the three registered levels "
                   f"{LEVEL_ORDER}")
        targets.append((a.case, lvl))
    elif a.root:
        for c, lvl in sorted(CASE_LEVEL.items()):
            d = os.path.join(a.root, c)
            if os.path.isdir(d):
                targets.append((d, lvl))
        if not targets:
            refuse(f"no registered K0d case directory found under {a.root}")
    else:
        refuse("give --case or --root; this script does not guess.")

    bad = False
    meshes = {}                 # level -> (case name, mesh READ FROM DISK)
    for case_dir, lvl in targets:
        mesh = load_case(case_dir)
        name = os.path.basename(case_dir.rstrip("/"))
        if mesh is None:
            print(f"{name} ({lvl}): REFUSE -- no readable constant/polyMesh/points")
            bad = True
            continue
        print(f"{name} ({lvl}):")
        for cond, ok, note in judge(mesh, lvl):
            print(f"   {cond}  {'ok  ' if ok else 'FAIL'}  {note}")
            bad = bad or not ok
        meshes.setdefault(lvl, (name, mesh))

    # ---- CONDITION C.  It compares two levels and it READS BOTH MESHES.
    # A single-level invocation SAYS SO rather than silently omitting it: a
    # check omitted in silence reads as a check passed (AMENDMENT 2 A2.3,
    # repair item 5).
    print()
    print("condition C (per-block refinement ratio):")
    evaluated = 0
    for i in range(len(LEVEL_ORDER) - 1):
        lo, hi = LEVEL_ORDER[i], LEVEL_ORDER[i + 1]
        if lo in meshes and hi in meshes:
            ok, note = condition_C(meshes[lo][1], meshes[hi][1])
            print(f"   C  {'ok  ' if ok else 'FAIL'}  {lo}({meshes[lo][0]})"
                  f"->{hi}({meshes[hi][0]}): {note}")
            bad = bad or not ok
            evaluated += 1
        else:
            missing = [l for l in (lo, hi) if l not in meshes]
            print(f"   C  NOT EVALUATED  {lo}->{hi}: no mesh was read for "
                  f"{missing}.  CONDITION C WAS NOT RUN ON THIS PAIR.")
    if evaluated == 0:
        print("   CONDITION C WAS NOT EVALUATED AT ALL IN THIS INVOCATION.")
        print("   It compares two consecutive levels and needs BOTH meshes on")
        print("   disk; a single-level --case invocation can never evaluate it.")
    # the registered table's own scaling, reported SEPARATELY and labelled
    print("registered-table scaling (NOT a check on any mesh):")
    for i in range(len(LEVEL_ORDER) - 1):
        lo, hi = LEVEL_ORDER[i], LEVEL_ORDER[i + 1]
        okS, noteS = condition_C_spec(LEVELS[lo], LEVELS[hi])
        print(f"   C-spec  {'ok  ' if okS else 'FAIL'}  {lo}->{hi}: {noteS}")
        bad = bad or not okS
    return EXIT_FAIL if bad else EXIT_OK


def selftest():
    print("=" * 74)
    print("check_k0f_mesh.py -- SELFTEST (planted controls)")
    print("=" * 74)
    fails = []

    def check_(label, cond, detail=""):
        print(f"  {'OK  ' if cond else 'FAIL'}  {label}"
              + (f"   [{detail}]" if detail else ""))
        if not cond:
            fails.append(label)

    # the registered arithmetic, re-derived rather than trusted
    for lvl, s in LEVELS.items():
        check_(f"{lvl}: nA+nB+nC == Ny", s["nA"] + s["nB"] + s["nC"] == s["Ny"],
               f"{s['nA']}+{s['nB']}+{s['nC']}={s['Ny']}")
        check_(f"{lvl}: Nx*Ny == registered cell count",
               s["Nx"] * s["Ny"] == s["cells"], str(s["Nx"] * s["Ny"]))
    r21 = (LEVELS["L2"]["cells"] / LEVELS["L1"]["cells"]) ** 0.5
    r32 = (LEVELS["L3"]["cells"] / LEVELS["L2"]["cells"]) ** 0.5
    check_("r21 = 1.400000 from the CELL COUNTS", abs(r21 - 1.400000) < 5e-7,
           f"{r21:.6f}")
    check_("r32 = 1.401786 from the CELL COUNTS", abs(r32 - 1.401786) < 5e-7,
           f"{r32:.6f}")
    check_("both ratios >= 1.30", r21 >= 1.30 and r32 >= 1.30)

    # the first wall cell column re-derived from the registered formula at
    # nu = 1.569e-5 -- re-registration 5.1.  NOT copied from the superseded
    # column, which is 1.2258 % away and would fail condition D's own 1 %.
    nu, u_in, Cf = 1.569e-5, 0.57, 0.005
    u_tau = u_in * (Cf / 2.0) ** 0.5
    y1 = 2.0 * 1.0 * nu / u_tau
    check_("u_tau = 0.028500 m/s", abs(u_tau - 0.028500) < 1e-9, f"{u_tau:.6f}")
    check_("L1 first cell reproduces 1.101053e-03",
           abs(y1 - LEVELS["L1"]["first_cell"]) / y1 < 1e-6, f"{y1:.6e}")
    check_("L2 first cell reproduces 7.864662e-04",
           abs(y1 / r21 - LEVELS["L2"]["first_cell"]) / (y1 / r21) < 1e-5,
           f"{y1 / r21:.6e}")
    check_("L3 first cell reproduces 5.610459e-04",
           abs(y1 / r21 / r32 - LEVELS["L3"]["first_cell"])
           / (y1 / r21 / r32) < 1e-5, f"{y1 / r21 / r32:.6e}")
    superseded = 1.55e-5
    drift = 100.0 * (nu - superseded) / superseded
    check_("the superseded column is > 1 % away, so condition D would have "
           "refused every level had it been carried across",
           drift > COND_D_TOL_PCT, f"{drift:.4f} %")

    # CONDITION G, both directions
    fired, notes = condition_G()
    check_("condition G FIRES: inverted grading and short slot both refused, "
           "clean synthetic mesh accepted", fired, "; ".join(notes)[:110])

    # each condition shown able to stay quiet AND to fire
    for lvl in LEVEL_ORDER:
        spec, clean = LEVELS[lvl], synthetic_mesh(lvl)
        okA, _ = condition_A(clean, spec)
        check_(f"{lvl}: condition A quiet on the clean mesh", okA)
        dirty = dict(clean, n_cells=clean["n_cells"] - 1)
        okA2, _ = condition_A(dirty, spec)
        check_(f"{lvl}: condition A FIRES on one cell missing", not okA2)
        okF, note = condition_F(clean, spec)
        check_(f"{lvl}: condition F quiet on the clean mesh", okF, note[:60])
        stretched = dict(clean, x_lines=[v * 1.001 for v in clean["x_lines"]])
        okF2, _ = condition_F(stretched, spec)
        check_(f"{lvl}: condition F FIRES on a 0.1 % stretched domain", not okF2)
    # ---- CONDITION C, REPAIRED: PLANTED INTO THE MESH, NOT INTO THE SPEC ----
    # The pre-repair selftest planted into dict(LEVELS["L2"], nB=400) -- a
    # MODIFIED SPEC, not a modified mesh -- which is why a passing selftest hid
    # a condition that never read the mesh (AMENDMENT 2 section A2.3).
    m_L1, m_L2, m_L3 = (synthetic_mesh("L1"), synthetic_mesh("L2"),
                        synthetic_mesh("L3"))
    okC, note = condition_C(m_L1, m_L2)
    check_("condition C quiet on the CLEAN L1->L2 MESH PAIR", okC, note[:80])
    okC32, note32 = condition_C(m_L2, m_L3)
    check_("condition C quiet on the CLEAN L2->L3 MESH PAIR", okC32, note32[:80])

    # the counts condition C now uses come FROM THE MESH, not from LEVELS
    for lvl, m in (("L1", m_L1), ("L2", m_L2), ("L3", m_L3)):
        cnt, nx = block_cells_from_mesh(m)
        spec = LEVELS[lvl]
        check_(f"{lvl}: block counts read FROM THE MESH reproduce the "
               f"registered table",
               nx == spec["Nx"]
               and cnt["A"] == spec["Nx"] * spec["nA"]
               and cnt["B"] == spec["Nx"] * spec["nB"]
               and cnt["C"] == spec["Nx"] * spec["nC"],
               f"Nx={nx}, A={cnt['A']}, B={cnt['B']}, C={cnt['C']}")

    # THE MESH-PLANTED REDISTRIBUTION CONTROL -- the proof the hole is closed
    redis = synthetic_mesh("L2", redistribute=REDISTRIBUTE_K)
    okA_r, nA_r = condition_A(redis, LEVELS["L2"])
    okB_r, nB_r = condition_B(redis, LEVELS["L2"])
    okC_r, nC_r = condition_C(m_L1, redis)
    check_(f"redistribution control: condition A STAYS QUIET "
           f"(total cells unchanged)", okA_r, nA_r)
    check_(f"redistribution control: condition B STAYS QUIET "
           f"(both slots larger, tested with >=)", okB_r, nB_r)
    check_(f"REPAIRED CONDITION C REFUSES a {REDISTRIBUTE_K}-cell block "
           f"redistribution THAT A AND B BOTH LET THROUGH", not okC_r,
           nC_r[:100])
    check_("the redistribution control actually under-resolves BLOCK B "
           "(the cavity interior)",
           block_cells_from_mesh(redis)[0]["B"]
           < LEVELS["L2"]["Nx"] * LEVELS["L2"]["nB"],
           f"{block_cells_from_mesh(redis)[0]['B']} vs "
           f"{LEVELS['L2']['Nx'] * LEVELS['L2']['nB']}")

    # condition C REFUSES to run without a mesh -- it must never silently fall
    # back to LEVELS, because that fallback WAS the defect.
    try:
        condition_C(None, m_L2)
        raised = False
    except ValueError:
        raised = True
    check_("condition C RAISES rather than falling back to LEVELS when a mesh "
           "is missing", raised)

    # the registered-table check is KEPT and LABELLED as not a mesh check
    okS, noteS = condition_C_spec(LEVELS["L1"], LEVELS["L2"])
    check_("C-spec quiet on the registered L1->L2 table", okS, noteS[:70])
    okS2, _ = condition_C_spec(LEVELS["L1"], dict(LEVELS["L2"], nB=400))
    check_("C-spec FIRES on a registered table that does not scale by 1.40",
           not okS2)
    check_("C-spec LABELS ITSELF as not a check on the mesh",
           "NOT A CHECK ON THE MESH" in noteS)
    check_("condition C LABELS ITSELF as read from the mesh",
           "FROM THE MESH" in note)

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s) did not hold")
        for f in fails:
            print("   - " + f)
        return EXIT_FAIL
    print("SELFTEST PASSED: every condition was shown able to FIRE on a planted")
    print("defect and able to STAY QUIET on its clean counterpart.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
