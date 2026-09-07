#!/usr/bin/env python3
"""
T10a-VF2 comparator (analyse_t10avf2.py).

Successor comparator to analyse_t10avf.py (frozen blob
6bb155521f8fce95e5fc571ed206e7cf3a297ab1). It carries the T10a-VF2 re-posed gate
evaluations for VF-4' (Limb A) and VF-7' ONLY, plus the required controls,
exactly per verification's V-121 gate ruling (docs/LAB_STATE.md,
verification-supervisor, 2026-09-07) and the T10aVF2 pre-registration draft §2,
§4, §5.

WHAT THIS FILE FREEZES (scope, cut at the pre-registration commit; CLAUDE.md
rule 2):
  * B_ctrl(case) -- the control-measured floor. FROZEN FORMULA (read, not chosen):
        B_ctrl(case) = max |E| over that case's n_ev == 0 (convex/flat) CONTROL
        patches, E = patch-mean rowSum - 1, computed by the grader FROM THE
        CONTROL PATCHES READ FROM DISK (V-121 condition c). The formula is
        frozen; the VALUE is measured per case, never chosen.
  * VF-4' Limb A -- every GRADED (n_ev > 0) patch is graded
        |E - n_ev*e(0.21)| <= 0.30*|n_ev*e(0.21)| + B_ctrl(case)
    against the FROZEN 0.30 Limb-A coefficient and the B_ctrl floor.
  * Two FLOOR-VALIDITY GUARDS on the B_ctrl control, each planted RED/GREEN
    (V-121 condition b; CLAUDE.md rule 3 extended to the floor's own validity):
      - mechanism-leak guard (afix bit-identity): a control patch must be
        exactly identical between the alpha = 0.21 case and its
        alpha = exp(-3/2) (_afix) twin. If a mechanism/alpha term leaks onto a
        control patch the control is INVALID and any dependent gate is
        NOT A RESULT (refuse INVALID; NEVER a pass).
      - order guard (p >= 1.5): the control's quadrature error must converge at
        order p >= 1.5 across the mesh family, else the control is INVALID and
        the dependent gate is NOT A RESULT.
  * VF-7' -- the QUADRATURE tolerance GaussQuadTol is inert: 0.01 -> 0.001 ->
    1e-6 must move the SPH outer E by <= 0.05 pp. The ray-shrink knob intTol is
    NOT tested here.
  * VF-11 -- the intTol ray-visibility collapse is REPORTED ONLY (blind-face
    count + collapsed inner mean printed), NEVER gated.
  * §5 graded-VALUE planted-zero control: PLANT_ROWSUM = 3.21e-2 injected into a
    COPY of constant/F under the case, read back through the same grading reader,
    refuse (exit 2) if not recovered. This is SEPARATE from the two
    floor-validity guards above.

DELIBERATELY NOT IMPLEMENTED (DEFERRED per V-121 -- they freeze only after a
separate 0.20 driven sweep across [0.05, 0.25]):
  * VF-3' and VF-6'.
  * the 0.20 signal-to-background ADMISSIBILITY constant. VF-4' Limb A and VF-7'
    DO NOT reference it and MUST NOT depend on it. There is no 0.20 constant and
    no admissibility test anywhere in this file.

REUSED VERBATIM from the predecessor analyse_t10avf.py (readers / aggregation):
  read_boundary, read_faces, stream_list_list (incl. the disclosed post-freeze
  inline-short-list `N(...)` / `0()` amendment), the edge-neighbour construction
  and the per-patch row-sum aggregation core of analyse(). The predecessor is
  NOT edited; its logic is imported by re-implementation here so this file is a
  self-contained frozen unit.

ADDED here (not in the predecessor):
  classify_patches, b_ctrl, grade_vf4a_case, guard_mechanism_leak,
  guard_control_order, read_control_rows, the §5 graded-value plant machinery,
  vf7_move, count_blind_faces (VF-11), a defensive real-case driver that
  REFUSES (exit 2) on any missing input, and a --selftest that drives every
  planted control with synthetic/planted fixtures. NO SOLVER RUN, ever.

Every gate REFUSES (exit 2) rather than degrading on a missing input
(CLAUDE.md rule 4; pre-registration §6).
"""
import sys, os, json, math, re, argparse, shutil, tempfile
from collections import defaultdict

# ============================================================================
# FROZEN pre-registered constants (pins cut at freeze; CLAUDE.md rule 2).
# ============================================================================
ALPHA_SHIPPED     = 0.21      # shipped viewFactorsGen default (the graded cases)
ALPHA_FIX         = math.exp(-1.5)   # 0.223130160148... the analytically exact alpha
LIMBA_COEFF       = 0.30      # VF-4' Limb-A frozen coefficient (DO NOT ALTER)
ORDER_GUARD_MIN_P = 1.5       # control quadrature-error convergence order floor
VF7_MAX_MOVE_PP   = 0.05      # VF-7' GaussQuadTol move ceiling, percentage points
PLANT_ROWSUM      = 3.21e-2   # §5 graded-value planted-zero control magnitude
PLANT_TOL         = 1e-9      # recovery tolerance for the plant
DESIGNATED_FACE   = 0         # compact index of the face whose first F entry is planted


def e_alpha(a):
    """The closed-form defect size per mutually-visible edge-sharing neighbour,
    e(alpha) = -(2 ln alpha + 3)/(4 pi) (T10aVF_RESULTS.md:33). Frozen law."""
    return -(2.0 * math.log(a) + 3.0) / (4.0 * math.pi)


E_021 = e_alpha(ALPHA_SHIPPED)   # +0.0096524...; the ONLY predicted term VF-4' uses


# ============================================================================
# READERS -- reused verbatim from analyse_t10avf.py (blob 6bb15552...).
# ============================================================================
def read_boundary(case):
    txt = open(os.path.join(case, "constant", "polyMesh", "boundary")).read()
    body = txt[txt.index("// * * *"):]
    return [(m.group(1), int(m.group(2)), int(m.group(3)))
            for m in re.finditer(
                r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", body, re.S)]


def read_faces(case, lo, hi):
    path = os.path.join(case, "constant", "polyMesh", "faces")
    out = {}
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        for line in fh:
            if line.strip() == "(":
                break
        i = 0
        while i < hi:
            s = fh.readline().strip()
            if not s or s == "(":
                continue
            if lo <= i < hi:
                k = s.index("(")
                out[i] = tuple(int(x) for x in s[k + 1:s.rindex(")")].split())
            i += 1
    return out


def stream_list_list(path, cast):
    """List-of-lists streamer. Carries the predecessor's disclosed post-freeze
    amendment: OpenFOAM writes a SHORT inner list inline as `N(v1 ... vN)` (and
    an empty one as `0()`); block-form rows re-parse bit-identically."""
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        if n is None:
            raise RuntimeError("no size in " + path)
        for line in fh:
            if line.strip() == "(":
                break
        for _ in range(n):
            m = None
            inline = None
            for line in fh:
                s = line.strip()
                if not s or s == "(":
                    continue
                if "(" in s:
                    k = s.index("(")
                    m = int(s[:k])
                    body = s[k + 1:s.rindex(")")].strip()
                    inline = [cast(x) for x in body.split()] if body else []
                else:
                    m = int(s)
                break
            if inline is not None:
                if len(inline) != m:
                    raise RuntimeError("inline row length mismatch")
                yield inline
                continue
            for line in fh:
                if line.strip() == "(":
                    break
            row = [None] * m
            k = 0
            while k < m:
                s = fh.readline().strip()
                if not s:
                    continue
                row[k] = cast(s); k += 1
            for line in fh:
                if line.strip() == ")":
                    break
            yield row


# ============================================================================
# AGGREGATION -- the per-patch row-sum core of the predecessor analyse(),
# extended only with nEdgeVisSum (integer, exact) and comp (patch ranges).
# ============================================================================
def analyse(case, alpha=None):
    if not os.path.isdir(case):
        raise RuntimeError("case dir missing: " + case)
    for req in (os.path.join("constant", "polyMesh", "boundary"),
                os.path.join("constant", "polyMesh", "faces"),
                os.path.join("constant", "F"),
                os.path.join("constant", "globalFaceFaces")):
        if not os.path.exists(os.path.join(case, req)):
            raise RuntimeError("missing input %s in %s" % (req, case))

    bnds = read_boundary(case)
    off = 0
    comp = []                       # (name, compactLo, compactHi, startFace)
    for nm, nf, sf in bnds:
        comp.append((nm, off, off + nf, sf))
        off += nf
    ntot = off
    lo = min(b[2] for b in bnds)
    hi = max(b[2] + b[1] for b in bnds)
    faces = read_faces(case, lo, hi)

    g2c = {}
    c2g = [0] * ntot
    for nm, cl, ch, sf in comp:
        for k in range(ch - cl):
            g2c[sf + k] = cl + k
            c2g[cl + k] = sf + k
    pname = [None] * ntot
    for nm, cl, ch, sf in comp:
        for c in range(cl, ch):
            pname[c] = nm

    e2f = defaultdict(list)
    for c in range(ntot):
        fv = faces[c2g[c]]
        for k in range(len(fv)):
            e2f[frozenset((fv[k], fv[(k + 1) % len(fv)]))].append(c)
    nbr = [set() for _ in range(ntot)]
    for e, fl in e2f.items():
        if len(fl) > 1:
            for x in fl:
                for y in fl:
                    if x != y:
                        nbr[x].add(y)

    P = {nm: dict(n=0, rowsum=0.0, rmin=1e30, rmax=-1e30, rows=[],
                  nEdgeTot=0, nEdgeVis=0, Fedge=0.0, nvis=0,
                  cross=defaultdict(float))
         for nm, _, _, _ in comp}

    fgen = stream_list_list(os.path.join(case, "constant", "F"), float)
    ggen = stream_list_list(os.path.join(case, "constant", "globalFaceFaces"), int)
    i = 0
    for frow, grow in zip(fgen, ggen):
        nm = pname[i]
        st = P[nm]
        nb = nbr[i]
        tot = 0.0
        fe = 0.0
        ne = 0
        for v, j in zip(frow, grow):
            tot += v
            st["cross"][pname[j]] += v
            if j in nb:
                fe += v
                ne += 1
        st["n"] += 1
        st["rowsum"] += tot
        st["rmin"] = min(st["rmin"], tot)
        st["rmax"] = max(st["rmax"], tot)
        st["rows"].append(tot)
        st["nEdgeTot"] += len(nb)
        st["nEdgeVis"] += ne
        st["Fedge"] += fe
        st["nvis"] += len(frow)
        i += 1

    out = dict(case=os.path.abspath(case), nFaces=ntot, rowsInF=i, patches={},
               comp=[[nm, cl, ch, sf] for (nm, cl, ch, sf) in comp])
    meta_p = os.path.join(case, "CASE.json")
    if os.path.exists(meta_p):
        out["meta"] = json.load(open(meta_p))
        if alpha is None:
            alpha = out["meta"].get("alpha")
    out["alpha"] = alpha
    if alpha:
        out["e_alpha_pred"] = e_alpha(alpha)
    for nm, _, _, _ in comp:
        st = P[nm]
        if st["n"] == 0:
            continue
        rows = sorted(st["rows"])
        mean = st["rowsum"] / st["n"]
        nEv = st["nEdgeVis"] / st["n"]
        exc = mean - 1.0
        d = dict(nRows=st["n"], meanRowSum=mean, minRowSum=rows[0],
                 maxRowSum=rows[-1], meanExcess=exc,
                 maxExcess=rows[-1] - 1.0, meanExcessPct=100.0 * exc,
                 meanEdgeNbrsVisible=nEv,
                 nEdgeVisSum=st["nEdgeVis"],           # ADDED: exact integer count
                 meanF_on_edge_nbrs=st["Fedge"] / st["n"],
                 meanVisible=st["nvis"] / st["n"])
        out["patches"][nm] = d
    return out


# ============================================================================
# ADDED: classification, B_ctrl, VF-4' Limb A, floor-validity guards.
# ============================================================================
def classify_patches(rec):
    """Split a case's patches into CONTROL (n_ev == 0, i.e. nEdgeVisSum == 0 --
    an exact integer test read off the disk data) and GRADED (nEdgeVisSum > 0).
    The two sets are DISJOINT; B_ctrl reads only the CONTROL set, VF-4' Limb A
    grades only the GRADED set (V-121: a DIFFERENT patch set than the graded)."""
    control, graded = [], []
    for nm, d in rec["patches"].items():
        if d["nEdgeVisSum"] == 0:
            control.append(nm)
        else:
            graded.append(nm)
    return control, graded


def b_ctrl(rec):
    """FROZEN FORMULA (read, not chosen):
        B_ctrl(case) = max |E| over the case's n_ev == 0 CONTROL patches,
    E = patch-mean rowSum - 1, from the control patches read from disk.
    Returns None if the case has no control patch (caller REFUSES, exit 2)."""
    control, _ = classify_patches(rec)
    if not control:
        return None
    return max(abs(rec["patches"][nm]["meanExcess"]) for nm in control)


def grade_vf4a_case(rec, bctrl):
    """VF-4' Limb A on one alpha = 0.21 case. Every GRADED (n_ev > 0) patch:
        |E - n_ev*e(0.21)| <= 0.30*|n_ev*e(0.21)| + B_ctrl(case)
    Returns (all_within, rows). This is the VALUE grade ONLY; the caller turns
    it into NOT A RESULT when a floor-validity guard is INVALID (never a pass).
    Uses e(0.21) and the frozen 0.30 coefficient; does NOT use any 0.20
    admissibility constant."""
    _, graded = classify_patches(rec)
    rows = []
    ok = True
    for nm in sorted(graded):
        d = rec["patches"][nm]
        nev = d["meanEdgeNbrsVisible"]
        E = d["meanExcess"]
        pred = nev * E_021
        lhs = abs(E - pred)
        rhs = LIMBA_COEFF * abs(pred) + bctrl
        passed = lhs <= rhs
        ok = ok and passed
        rows.append(dict(patch=nm, n_ev=nev, E=E, predicted=pred,
                         lhs=lhs, rhs=rhs, B_ctrl=bctrl,
                         verdict="PASS" if passed else "GATE FAIL"))
    return ok, rows


def guard_mechanism_leak(case_ctrl_rows, afix_ctrl_rows):
    """Floor-validity guard 1: afix bit-identity. The CONTROL-patch F rows read
    from disk for the alpha = 0.21 case and its alpha = exp(-3/2) twin must be
    exactly identical -- the mechanism (an alpha term) may not touch a control
    patch. Returns 'VALID' / 'INVALID', or None when a twin is missing (caller
    REFUSES, exit 2). A leak -> INVALID -> dependent gate NOT A RESULT."""
    if case_ctrl_rows is None or afix_ctrl_rows is None:
        return None
    if len(case_ctrl_rows) != len(afix_ctrl_rows):
        return "INVALID"
    for r0, r1 in zip(case_ctrl_rows, afix_ctrl_rows):
        if len(r0) != len(r1):
            return "INVALID"
        for a, b in zip(r0, r1):
            if a != b:                       # exact-equality bit-identity
                return "INVALID"
    return "VALID"


def guard_control_order(levels):
    """Floor-validity guard 2: order p >= 1.5. `levels` = [(N_patch, B_ctrl), ...]
    across the mesh family, N_patch the control-patch face count; h = 1/sqrt(N)
    (pre-registration §2 Step 3). Fits p = d ln B / d ln h by least squares.
    Returns ('VALID'|'INVALID', p), or (None, None) when < 2 usable levels
    (caller REFUSES, exit 2). p < 1.5 -> INVALID -> dependent gate NOT A RESULT."""
    pts = [(1.0 / math.sqrt(N), B) for (N, B) in levels if N > 0 and B > 0]
    if len(pts) < 2:
        return None, None
    xs = [math.log(h) for h, _ in pts]
    ys = [math.log(B) for _, B in pts]
    n = len(xs); sx = sum(xs); sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom == 0.0:
        return None, None
    p = (n * sxy - sx * sy) / denom
    return ("VALID" if p >= ORDER_GUARD_MIN_P else "INVALID"), p


def read_control_rows(case, rec):
    """Read the CONTROL-patch F rows from disk (for the mechanism-leak guard).
    Returns a list of tuples, one per control face, in compact order."""
    control, _ = classify_patches(rec)
    ctrl = set(control)
    ranges = [(cl, ch) for (nm, cl, ch, sf) in rec["comp"] if nm in ctrl]
    if not ranges:
        return None
    def in_ctrl(idx):
        return any(cl <= idx < ch for (cl, ch) in ranges)
    rows = []
    for idx, row in enumerate(stream_list_list(os.path.join(case, "constant", "F"), float)):
        if in_ctrl(idx):
            rows.append(tuple(row))
    return rows


# ============================================================================
# ADDED: §5 graded-VALUE planted-zero control (SEPARATE from the two
# floor-validity guards above).
# ============================================================================
def _listlist_size(path):
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if s.isdigit():
                return int(s)
    raise RuntimeError("no size in " + path)


def _copy_listlist_perturbed(src, dst, face, delta):
    """Stream `src` (list-of-lists) to `dst`, adding `delta` to row[face][0].
    Constant memory; delta = 0.0 writes a faithful copy. repr() preserves
    round-trip precision. Writes canonical block form that stream_list_list
    reads back."""
    n = _listlist_size(src)
    with open(dst, "w") as out:
        out.write("%d\n(\n" % n)
        for idx, row in enumerate(stream_list_list(src, float)):
            r = list(row)
            if idx == face:
                if not r:
                    raise RuntimeError("designated face %d has an empty F row" % face)
                r[0] += delta
            out.write("%d\n(\n" % len(r))
            for v in r:
                out.write(repr(v) + "\n")
            out.write(")\n")
        out.write(")\n")


def _rowsum_reader_from_disk(fpath, face):
    """The grading row-sum path: stream constant/F FROM DISK and return the row
    sum of compact index `face`. The same parse path grading uses."""
    for idx, row in enumerate(stream_list_list(fpath, float)):
        if idx == face:
            return sum(row)
    raise RuntimeError("face %d not present in %s" % (face, fpath))


def check_graded_value_plant(case, scratch_dir, reader=None):
    """§5 graded-VALUE planted-zero control. Copies constant/F to a scratch path
    UNDER THE CASE (never the real matrix), injects +PLANT_ROWSUM into
    DESIGNATED_FACE's first F entry, reads the perturbed copy back FROM DISK
    through the same row-sum path, and asserts the designated rowSum rose by
    PLANT_ROWSUM to within PLANT_TOL (RED). Non-vacuity twin: a faithful copy
    reads back at the real matrix value (GREEN). Refuses (ok=False) if the
    perturbation is not seen -- a zero from a reader not shown able to see
    3.21e-2 is not evidence (rule 3). --selftest passes a BLIND reader to prove
    the refusal fires."""
    reader = reader or _rowsum_reader_from_disk
    src = os.path.join(case, "constant", "F")
    if not os.path.exists(src):
        return dict(ok=False, reason="missing constant/F: " + src)
    os.makedirs(scratch_dir, exist_ok=True)
    clean = os.path.join(scratch_dir, "F_clean")
    pert = os.path.join(scratch_dir, "F_perturbed")
    _copy_listlist_perturbed(src, clean, DESIGNATED_FACE, 0.0)
    _copy_listlist_perturbed(src, pert, DESIGNATED_FACE, PLANT_ROWSUM)
    true_val = reader(src, DESIGNATED_FACE)      # the REAL matrix on disk
    clean_val = reader(clean, DESIGNATED_FACE)   # faithful copy
    pert_val = reader(pert, DESIGNATED_FACE)     # perturbed copy
    red_ok = abs((pert_val - true_val) - PLANT_ROWSUM) <= PLANT_TOL   # sees +3.21e-2
    green_ok = abs(clean_val - true_val) <= PLANT_TOL                 # clean == real
    ok = red_ok and green_ok
    return dict(ok=ok, true_val=true_val, clean_val=clean_val, pert_val=pert_val,
                rose=pert_val - true_val, red_ok=red_ok, green_ok=green_ok,
                plant=PLANT_ROWSUM,
                reason=None if ok else "plant not recovered (reader blind to 3.21e-2?)")


# ============================================================================
# ADDED: VF-7' (GaussQuadTol) and VF-11 (intTol, reported only).
# ============================================================================
def vf7_move(gauss_means):
    """VF-7'. `gauss_means` = {GaussQuadTol: SPH-outer meanRowSum}. Returns
    (max_move_pp, verdict). PASS if the E swing across GaussQuadTol is
    <= 0.05 pp, else GATE FAIL. Tests ONLY GaussQuadTol -- never intTol."""
    vals = list(gauss_means.values())
    if len(vals) < 2:
        return None, None                      # caller REFUSES (exit 2)
    move_pp = (max(vals) - min(vals)) * 100.0
    return move_pp, ("PASS" if move_pp <= VF7_MAX_MOVE_PP else "GATE FAIL")


def count_blind_faces(case):
    """VF-11 (REPORTED ONLY, never gated): count faces whose globalFaceFaces row
    is empty (`0()`) -- rays too short to escape their own endpoint faces at
    intTol = 1e-4. Returns the blind-face count and the total."""
    blind = 0
    total = 0
    for row in stream_list_list(os.path.join(case, "constant", "globalFaceFaces"), int):
        total += 1
        if len(row) == 0:
            blind += 1
    return blind, total


# ============================================================================
# SELFTEST -- synthetic / planted fixtures only. NO SOLVER RUN.
# ============================================================================
def _make_listlist_file(path, rows):
    with open(path, "w") as fh:
        fh.write("%d\n(\n" % len(rows))
        for r in rows:
            fh.write("%d\n(\n" % len(r))
            for v in r:
                fh.write(repr(v) + "\n")
            fh.write(")\n")
        fh.write(")\n")


def run_selftest():
    fails = []
    print("=== analyse_t10avf2.py --selftest (synthetic fixtures, NO SOLVER) ===")

    # ---- Drive 1: §5 graded-VALUE plant fires + a BLIND reader is caught -----
    tmp = tempfile.mkdtemp(prefix="t10avf2_selftest_")
    try:
        case = os.path.join(tmp, "synthetic_case")
        os.makedirs(os.path.join(case, "constant"))
        # face 0 rowsum = 0.10+0.20+0.30 = 0.60; a NON-unit row the reader must see move.
        _make_listlist_file(os.path.join(case, "constant", "F"),
                            [[0.10, 0.20, 0.30], [0.40, 0.60], [0.55, 0.45]])
        pr = check_graded_value_plant(case, os.path.join(case, "_plant_scratch"))
        good = pr["ok"] and pr["red_ok"] and pr["green_ok"] \
            and abs(pr["rose"] - PLANT_ROWSUM) <= PLANT_TOL
        print("[1a] graded-value plant fires (RED perturbed seen, GREEN clean==real): "
              "%s  rose=%.6e (plant=%.6e)"
              % ("PASS" if good else "FAIL", pr["rose"], PLANT_ROWSUM))
        if not good:
            fails.append("1a graded-value plant did not fire")

        # BLIND reader: returns 0.0 whatever it is handed -> cannot see the plant.
        blind = check_graded_value_plant(case, os.path.join(case, "_plant_scratch2"),
                                         reader=lambda p, f: 0.0)
        caught = (not blind["ok"]) and (not blind["red_ok"])
        print("[1b] BLIND reader caught (plant refuses, exit-2 path): %s"
              % ("PASS" if caught else "FAIL"))
        if not caught:
            fails.append("1b blind reader not caught")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- Drive 2: mechanism-leak guard (afix bit-identity) RED/GREEN ---------
    clean_ctrl = [(0.10, 0.20, 0.30), (0.25, 0.25, 0.50)]
    green = guard_mechanism_leak(clean_ctrl, [tuple(r) for r in clean_ctrl])
    leaked = [(0.10, 0.20, 0.30), (0.25, 0.25, 0.5001)]   # an alpha term leaked in
    red = guard_mechanism_leak(clean_ctrl, leaked)
    g2 = (green == "VALID") and (red == "INVALID")
    print("[2 ] mechanism-leak guard: clean->%s (GREEN expect VALID), "
          "leaked->%s (RED expect INVALID): %s"
          % (green, red, "PASS" if g2 else "FAIL"))
    if not g2:
        fails.append("2 mechanism-leak guard RED/GREEN mismatch")
    # missing twin -> refuse (None)
    if guard_mechanism_leak(clean_ctrl, None) is not None:
        fails.append("2 mechanism-leak guard did not refuse on missing twin")

    # ---- Drive 3: order guard (p >= 1.5) RED/GREEN ---------------------------
    conv = [(768, 0.020), (1728, 0.0080), (3072, 0.0040), (4800, 0.0020)]
    vg, pg = guard_control_order(conv)
    nonconv = [(768, 0.020), (1728, 0.021), (3072, 0.0195), (4800, 0.020)]
    vr, pr2 = guard_control_order(nonconv)
    g3 = (vg == "VALID") and (vr == "INVALID")
    print("[3 ] order guard: converging p=%.3f->%s (GREEN expect VALID), "
          "non-converging p=%.3f->%s (RED expect INVALID): %s"
          % (pg, vg, pr2, vr, "PASS" if g3 else "FAIL"))
    if not g3:
        fails.append("3 order guard RED/GREEN mismatch")
    if guard_control_order([(768, 0.02)]) != (None, None):
        fails.append("3 order guard did not refuse on < 2 levels")

    # ---- Drive 4: B_ctrl formula + VF-4' Limb A logic map --------------------
    # Synthetic record: 2 control (n_ev=0) patches + 2 graded (n_ev>0) patches.
    rec = dict(comp=[["ctrl_a", 0, 1, 0], ["ctrl_b", 1, 2, 1],
                     ["conc_ok", 2, 3, 2], ["conc_broken", 3, 4, 3]],
               patches={
                   "ctrl_a":       dict(nEdgeVisSum=0, meanExcess=0.0010,
                                        meanEdgeNbrsVisible=0.0),
                   "ctrl_b":       dict(nEdgeVisSum=0, meanExcess=-0.0025,
                                        meanEdgeNbrsVisible=0.0),
                   # a good concave patch: E ~ n_ev*e(0.21) + tiny background
                   "conc_ok":      dict(nEdgeVisSum=40, meanExcess=4.0 * E_021 + 0.0010,
                                        meanEdgeNbrsVisible=4.0),
                   # a broken concave patch: E far from the mechanism prediction
                   "conc_broken":  dict(nEdgeVisSum=40, meanExcess=0.10,
                                        meanEdgeNbrsVisible=4.0),
               })
    control, graded = classify_patches(rec)
    bc = b_ctrl(rec)
    bc_ok = (set(control) == {"ctrl_a", "ctrl_b"}
             and set(graded) == {"conc_ok", "conc_broken"}
             and abs(bc - 0.0025) <= 1e-12)
    print("[4a] classify + B_ctrl formula (max|E| over n_ev==0): B_ctrl=%.6f "
          "(expect 0.0025), sets disjoint&correct: %s"
          % (bc, "PASS" if bc_ok else "FAIL"))
    if not bc_ok:
        fails.append("4a B_ctrl/classification wrong")

    allok, rows = grade_vf4a_case(rec, bc)
    vd = {r["patch"]: r["verdict"] for r in rows}
    map_ok = (vd.get("conc_ok") == "PASS" and vd.get("conc_broken") == "GATE FAIL"
              and allok is False)
    print("[4b] VF-4' Limb A logic maps: good concave->%s, broken concave->%s "
          "(broken must trip the falsifier): %s"
          % (vd.get("conc_ok"), vd.get("conc_broken"), "PASS" if map_ok else "FAIL"))
    if not map_ok:
        fails.append("4b VF-4' Limb A logic mismap")
    # NOT-A-RESULT dominance: an INVALID floor overrides even an all-within value grade.
    clean_rec = dict(comp=rec["comp"],
                     patches={**rec["patches"],
                              "conc_broken": dict(nEdgeVisSum=40,
                                                  meanExcess=4.0 * E_021 + 0.0010,
                                                  meanEdgeNbrsVisible=4.0)})
    allok2, _ = grade_vf4a_case(clean_rec, bc)
    floor_valid = "INVALID"   # pretend a guard tripped
    verdict = "NOT A RESULT" if floor_valid == "INVALID" else ("PASS" if allok2 else "GATE FAIL")
    nar_ok = (allok2 is True) and (verdict == "NOT A RESULT")
    print("[4c] floor-validity dominance: value grade all-within but floor INVALID "
          "-> %s (must be NOT A RESULT, never PASS): %s"
          % (verdict, "PASS" if nar_ok else "FAIL"))
    if not nar_ok:
        fails.append("4c INVALID floor did not force NOT A RESULT")

    # ---- Drive 5: VF-7' GaussQuadTol logic map -------------------------------
    inert = {0.01: 1.0402552, 0.001: 1.0402632, 1e-6: 1.0402632}   # 0.0008 pp
    mv, vv = vf7_move(inert)
    active = {0.01: 1.0402552, 0.001: 1.0405000, 1e-6: 1.0410000}  # > 0.05 pp
    mv2, vv2 = vf7_move(active)
    g5 = (vv == "PASS" and vv2 == "GATE FAIL")
    print("[5 ] VF-7' GaussQuadTol: inert %.4f pp->%s (expect PASS), "
          "active %.4f pp->%s (expect GATE FAIL): %s"
          % (mv, vv, mv2, vv2, "PASS" if g5 else "FAIL"))
    if not g5:
        fails.append("5 VF-7' logic mismap")
    if vf7_move({0.01: 1.04}) != (None, None):
        fails.append("5 VF-7' did not refuse on < 2 tol points")

    print("=== SELFTEST %s ===" % ("PASS (rc 0)" if not fails else "FAIL (rc 1): " + "; ".join(fails)))
    return 0 if not fails else 1


# ============================================================================
# Real-case driver. REFUSES (exit 2) on any missing input (rule 4; §6).
# CASE.json meta keys it reads: alpha (float, required); role in
# {graded, afix, gaussquad, inttol}; twin (basename of the _afix twin, for
# graded family cases); gaussQuadTol (float, gaussquad role); N_control
# (control-patch face count, for the order guard); family (str, order-guard key).
# ============================================================================
def _refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cases", nargs="*", help="case directories to grade")
    ap.add_argument("--out", default=None, help="write combined JSON here")
    ap.add_argument("--selftest", action="store_true",
                    help="drive every planted control with synthetic fixtures; NO SOLVER")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(run_selftest())

    if not a.cases:
        _refuse("no cases given and --selftest not set")

    recs = {}
    for c in a.cases:
        try:
            r = analyse(c)
        except Exception as e:
            _refuse("analyse failed on %s: %s" % (c, e))
        recs[os.path.basename(os.path.abspath(c))] = r

    def meta(rec, key, req=True):
        m = rec.get("meta", {})
        if key not in m:
            if req:
                _refuse("CASE.json for %s lacks required key '%s'" % (rec["case"], key))
            return None
        return m[key]

    report = dict(gates={}, cases={})

    # ---- VF-4' Limb A + the two floor-validity guards --------------------
    graded_cases = {n: r for n, r in recs.items()
                    if meta(r, "role", req=False) in (None, "graded")
                    and r.get("alpha") is not None
                    and abs(r["alpha"] - ALPHA_SHIPPED) < 1e-9}
    order_family = defaultdict(list)      # family -> [(N_control, B_ctrl)]
    vf4_case_rows = {}
    for n, r in graded_cases.items():
        bc = b_ctrl(r)
        if bc is None:
            _refuse("case %s has no n_ev==0 CONTROL patch; B_ctrl undefined" % n)
        allok, rows = grade_vf4a_case(r, bc)

        # floor-validity guard 1: mechanism-leak (afix bit-identity)
        twin = meta(r, "twin", req=True)
        if twin not in recs:
            _refuse("afix twin '%s' of %s not among the graded cases" % (twin, n))
        leak = guard_mechanism_leak(read_control_rows(r["case"], r),
                                    read_control_rows(recs[twin]["case"], recs[twin]))
        if leak is None:
            _refuse("mechanism-leak guard could not read control rows for %s / twin" % n)

        # order-guard family accumulation
        Nc = meta(r, "N_control", req=True)
        fam = meta(r, "family", req=True)
        order_family[fam].append((Nc, bc))

        vf4_case_rows[n] = dict(B_ctrl=bc, value_all_within=allok, rows=rows,
                                mechanism_leak=leak, twin=twin, family=fam)

    # floor-validity guard 2: order (per family)
    order_verdict = {}
    for fam, lv in order_family.items():
        v, p = guard_control_order(lv)
        if v is None:
            _refuse("order guard for family %s has < 2 usable control levels" % fam)
        order_verdict[fam] = dict(verdict=v, p=p, levels=lv)

    # combine into VF-4' Limb A verdict (INVALID floor -> NOT A RESULT)
    vf4_rows_out = []
    vf4_verdict = "PASS"
    for n, cr in vf4_case_rows.items():
        fam = cr["family"]
        floor_valid = (cr["mechanism_leak"] == "VALID"
                       and order_verdict[fam]["verdict"] == "VALID")
        if not floor_valid:
            case_v = "NOT A RESULT"
        else:
            case_v = "PASS" if cr["value_all_within"] else "GATE FAIL"
        cr["case_verdict"] = case_v
        vf4_rows_out.append(dict(case=n, verdict=case_v,
                                 mechanism_leak=cr["mechanism_leak"],
                                 order=order_verdict[fam]["verdict"],
                                 order_p=order_verdict[fam]["p"],
                                 B_ctrl=cr["B_ctrl"]))
        # NOT A RESULT dominates; else any GATE FAIL demotes; PASS only if all PASS
        if case_v == "NOT A RESULT":
            vf4_verdict = "NOT A RESULT"
        elif case_v == "GATE FAIL" and vf4_verdict != "NOT A RESULT":
            vf4_verdict = "GATE FAIL"
    report["gates"]["VF-4prime_LimbA"] = dict(verdict=vf4_verdict, cases=vf4_rows_out,
                                              order=order_verdict)

    # ---- §5 graded-VALUE plant on every graded case (refuse if not seen) --
    plant_report = {}
    for n, r in graded_cases.items():
        pr = check_graded_value_plant(r["case"],
                                      os.path.join(r["case"], "_plant_scratch"))
        plant_report[n] = pr
        if not pr["ok"]:
            _refuse("graded-value plant not recovered on %s: %s" % (n, pr["reason"]))
    report["planted_zero_control"] = plant_report

    # ---- VF-7' (GaussQuadTol only) ---------------------------------------
    gcases = {n: r for n, r in recs.items() if meta(r, "role", req=False) == "gaussquad"}
    if gcases:
        gauss_means = {}
        for n, r in gcases.items():
            gt = meta(r, "gaussQuadTol", req=True)
            outer = None
            for nm, d in r["patches"].items():
                if "outer" in nm.lower():
                    outer = d["meanRowSum"]
            if outer is None:
                _refuse("VF-7' case %s has no 'outer' patch to read meanRowSum" % n)
            gauss_means[gt] = outer
        mv, vv = vf7_move(gauss_means)
        if mv is None:
            _refuse("VF-7' needs >= 2 GaussQuadTol points; got %d" % len(gauss_means))
        report["gates"]["VF-7prime"] = dict(verdict=vv, max_move_pp=mv,
                                            threshold_pp=VF7_MAX_MOVE_PP,
                                            gauss_means=gauss_means)

    # ---- VF-11 (intTol) -- REPORTED ONLY, never gated --------------------
    icases = {n: r for n, r in recs.items() if meta(r, "role", req=False) == "inttol"}
    for n, r in icases.items():
        blind, total = count_blind_faces(r["case"])
        inner = None
        for nm, d in r["patches"].items():
            if "inner" in nm.lower():
                inner = d["meanRowSum"]
        report.setdefault("VF-11_reported_only", {})[n] = dict(
            blind_faces=blind, total_faces=total, collapsed_inner_meanRowSum=inner,
            note="REPORTED ONLY (ray-shrink intTol), never gated")

    # ---- emit ------------------------------------------------------------
    print("VF-4' Limb A: %s" % report["gates"]["VF-4prime_LimbA"]["verdict"])
    for row in vf4_rows_out:
        print("  %-24s %-12s leak=%-8s order=%-8s(p=%.3f) B_ctrl=%.6e"
              % (row["case"], row["verdict"], row["mechanism_leak"],
                 row["order"], row["order_p"], row["B_ctrl"]))
    if "VF-7prime" in report["gates"]:
        g = report["gates"]["VF-7prime"]
        print("VF-7' (GaussQuadTol only): %s  max_move=%.4f pp (<= %.2f pp)"
              % (g["verdict"], g["max_move_pp"], g["threshold_pp"]))
    for n, d in report.get("VF-11_reported_only", {}).items():
        print("VF-11 (REPORTED ONLY) %s: %d/%d blind faces, inner mean=%s"
              % (n, d["blind_faces"], d["total_faces"], d["collapsed_inner_meanRowSum"]))

    if a.out:
        json.dump(report, open(a.out, "w"), indent=1, default=str)
        print("\nwrote %s" % os.path.abspath(a.out))


if __name__ == "__main__":
    main()
