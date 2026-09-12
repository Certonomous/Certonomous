#!/usr/bin/env python3
"""M6H1 H-G6 instrument -- compare the SOLVED surface Cp against AGARD AR-138
Table B1-14 at the seven spanwise sections, upper and lower surface separately.

WHAT SECTION 7 REGISTERS (H-G6): "Cp against AGARD Table B1-14, the seven sections";
threshold "RMS dCp <= 0.05 at each section, upper and lower surface separately,
EXCLUDING the four points nearest the shock at each section (the shock is a
discontinuity and a pointwise RMS there measures grid alignment, not physics)";
label if not met "GATE FAIL".

TWO GAPS IN SECTION 7 THAT THIS INSTRUMENT CANNOT CLOSE ON ITS OWN AND WILL NOT
SILENTLY PAPER OVER.  They are raised to the cfd-supervisor WITH the diff, because a
threshold with a free parameter is not frozen even when the number in it is:
  GAP 1.  Section 7 says "the four points nearest the shock" but does NOT say HOW the
          shock is located.  Located on the SOLVED distribution it is a free parameter
          that moves with the answer and can be tuned after the fact.  This instrument
          therefore locates it on the REFERENCE side (SHOCK_SIDE = 'reference'), where
          it is fixed by Table B1-14 at the freeze and cannot move with the solution.
          THAT CHOICE IS THIS LANE'S, NOT THE REGISTRATION'S, AND MUST BE WRITTEN INTO
          SECTION 7 BEFORE FREEZE OR THE GATE HAS A FREE PARAMETER.
  GAP 2.  Section 7 says "upper and lower surface separately" and "the four points
          nearest the shock at each section".  It does not say whether the lower
          surface is also masked.  This instrument masks the UPPER surface only
          (MASK_LOWER = False), because the transonic shock is an upper-surface
          phenomenon -- but the registration must say so itself.

PLANTED CONTROLS (rule 3).  Both plant INTO THE INPUT -- they perturb the REFERENCE
table in a COPY ON DISK and RE-RUN the real comparator on that file.

  PLANT A -- SENSITIVITY, AGAINST A PREDICTED VALUE.  Add a known dCp to ONE INCLUDED
  reference point.  The section's RMS must move to the ANALYTICALLY PREDICTED value
      RMS' = sqrt( ( sum r_i^2 - r_k^2 + (r_k - dCp)^2 ) / n )
  not merely "move".  A control that only checks for movement passes on any bug that
  perturbs the answer at all.
  Code path exercised: load_table()'s parser, match_sections()'s y/b matching,
  interp_solved()'s linear interpolation onto the reference abscissae, shock_mask()'s
  exclusion, and rms() -- i.e. the whole path that produces the graded number.

  PLANT B -- DISCRIMINATION (the plant is on the REFERENCE side ONLY).  Section 10:
  "an RMS change could come from re-interpolation -- the plant is applied to the
  reference side only, holding the solved side fixed".  So the comparator records the
  interpolated SOLVED Cp vector for every section, and PLANT B REFUSES if a single
  solved value moved.  If the solved side moved, the RMS change is re-interpolation
  and not the plant, and the control has measured nothing.

  PLANT C -- DISCRIMINATION (the exclusion mask is live, not decorative).  Add the
  same dCp to a reference point INSIDE the shock-exclusion window.  The RMS must NOT
  move at all.  A comparator whose mask is decorative moves, and is refused.

THE SAME-RUN ASSERTION -- WHY THIS COMPARATOR CAN DECLINE RATHER THAN EMIT A NUMBER.
This is the reader that combines two sources: a tabulated EXPERIMENT and a SOLVED
field.  A planted zero cannot catch a comparator that pairs reference section 3 with
solved section 4 -- that returns a plausible RMS, not a zero.  So:
  (i)   every reference section must match EXACTLY ONE solved section by y/b within
        SECTION_MATCH_TOL, and vice versa.  Zero matches, or two, -> DECLINE.
        SECTIONS ARE NEVER PAIRED BY ROW ORDER OR BY INDEX.
  (ii)  all N_SECTIONS reference sections must be present, both surfaces.
  (iii) reference abscissae outside the solved x/c span are NOT extrapolated; if more
        than OUTSIDE_FRAC of a surface's points fall outside, -> DECLINE.
  (iv)  the solved file must be NEWER than the case's own 0/U when --case is given
        (the age guard, rule 4 / falsifier 2c: an artifact written by a run other than
        the graded one).

Exit codes:  0 PASS   1 GATE FAIL (reported, never adjusted)   2 REFUSE / DECLINE

INPUT FORMAT (both files, whitespace- or comma-separated, '#' comments):
    section_id   y_over_b   surface   x_over_c   Cp
`surface` is `upper` or `lower`.  section_id is a label; MATCHING IS ON y_over_b.
"""
import sys, os, re, math, shutil, tempfile

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md sections 1.2, 7). Do not edit to fit. ---
N_SECTIONS        = 7        # section 1.2: "seven spanwise stations, SECTION 1...7"
RMS_GATE          = 0.05     # section 7, H-G6
N_SHOCK_EXCLUDE   = 4        # section 7, H-G6: "the four points nearest the shock"
SEMISPAN_M        = 1.1963   # section 1.2, AGARD B1 2.1.8
# --- THIS LANE'S CHOICES, NOT THE REGISTRATION'S. See GAP 1 and GAP 2 above. ---
SHOCK_SIDE        = 'reference'
MASK_LOWER        = False
SECTION_MATCH_TOL = 0.005    # in y/b
OUTSIDE_FRAC      = 0.10     # max fraction of reference points outside the solved x span
# ---------------------------------------------------------------------------------------------

# TEST HOOK, touched ONLY by selftest ARM 4.  It makes compare() apply NO shock mask, so
# the selftest can build a comparator whose mask is DECORATIVE and show PLANT C refusing
# it by the RMS MOVING -- a stronger demonstration than "no point was masked".
# It is never set outside selftest(); main() never reads it as anything but False.
_DISABLE_MASK = False


def load_table(path):
    """Read a Cp table FROM DISK. Returns {(y_over_b, surface): [(x_over_c, Cp), ...]}
    with each list sorted by x_over_c, plus {y_over_b: section_id}."""
    rows, labels = {}, {}
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            s = line.split('#')[0].strip()
            if not s:
                continue
            t = re.split(r'[,\s]+', s)
            if len(t) < 5:
                raise ValueError("%s:%d: expected 5 fields "
                                 "(section y_over_b surface x_over_c Cp), got %d"
                                 % (path, ln, len(t)))
            sec, yb, surf, xc, cp = t[0], float(t[1]), t[2].lower(), float(t[3]), float(t[4])
            if surf not in ('upper', 'lower'):
                raise ValueError("%s:%d: surface must be 'upper' or 'lower', got %r"
                                 % (path, ln, surf))
            rows.setdefault((yb, surf), []).append((xc, cp))
            labels[yb] = sec
    for k in rows:
        rows[k].sort(key=lambda p: p[0])
    return rows, labels


def match_sections(ref, sol):
    """Match reference y/b to solved y/b ONE-TO-ONE, by VALUE, never by row order or
    index. Returns (pairs, failures)."""
    ry = sorted({k[0] for k in ref})
    sy = sorted({k[0] for k in sol})
    pairs, bad = [], []
    used = set()
    for y in ry:
        cand = [z for z in sy if abs(z - y) <= SECTION_MATCH_TOL]
        if not cand:
            bad.append("reference section at y/b = %.5f has NO solved section within %.4f -- "
                       "it is NOT paired by index, so it is not paired at all"
                       % (y, SECTION_MATCH_TOL))
            continue
        if len(cand) > 1:
            bad.append("reference section at y/b = %.5f matches %d solved sections %s within "
                       "%.4f -- ambiguous, and an ambiguous pairing returns a PLAUSIBLE RMS"
                       % (y, len(cand), ['%.5f' % c for c in cand], SECTION_MATCH_TOL))
            continue
        if cand[0] in used:
            bad.append("solved section y/b = %.5f claimed by two reference sections" % cand[0])
            continue
        used.add(cand[0])
        pairs.append((y, cand[0]))
    for z in sy:
        if z not in used:
            bad.append("solved section at y/b = %.5f matches NO reference section" % z)
    if len(ry) != N_SECTIONS:
        bad.append("reference carries %d sections, section 1.2 registers %d"
                   % (len(ry), N_SECTIONS))
    return pairs, bad


def interp_solved(pts, x):
    """Linear interpolation of the SOLVED curve at x. Returns None outside its span --
    NEVER extrapolated: an extrapolated Cp is an invented measurement."""
    if len(pts) < 2 or x < pts[0][0] or x > pts[-1][0]:
        return None
    lo, hi = 0, len(pts) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pts[mid][0] <= x:
            lo = mid
        else:
            hi = mid
    x0, y0 = pts[lo]
    x1, y1 = pts[hi]
    if x1 == x0:
        return y0
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def shock_index(pts):
    """Locate the shock as the panel of maximum |dCp/d(x/c)| on the given curve.
    Returns the index of the point at the downstream end of that panel, or None."""
    if len(pts) < 2:
        return None
    best, bi = -1.0, None
    for i in range(1, len(pts)):
        dx = pts[i][0] - pts[i - 1][0]
        if dx <= 0:
            continue
        g = abs(pts[i][1] - pts[i - 1][1]) / dx
        if g > best:
            best, bi = g, i
    return bi


def shock_mask(ref_pts, n_exclude=N_SHOCK_EXCLUDE):
    """Indices of ref_pts EXCLUDED as the n_exclude points nearest the shock.
    Located on the REFERENCE curve (GAP 1) so the mask is fixed at the freeze."""
    si = shock_index(ref_pts)
    if si is None:
        return set(), None
    xs = ref_pts[si][0]
    order = sorted(range(len(ref_pts)), key=lambda i: abs(ref_pts[i][0] - xs))
    return set(order[:n_exclude]), xs


def compare(ref_path, sol_path):
    """Returns (result, failures). result is a list of per-(section,surface) dicts, each
    carrying its residuals, the interpolated SOLVED vector (for PLANT B) and the RMS."""
    ref, rlab = load_table(ref_path)
    sol, _ = load_table(sol_path)
    pairs, bad = match_sections(ref, sol)
    if bad:
        return None, bad
    res = []
    for ry, sy in pairs:
        for surf in ('upper', 'lower'):
            rk, sk = (ry, surf), (sy, surf)
            if rk not in ref:
                bad.append("reference has no %s surface at y/b = %.5f" % (surf, ry))
                continue
            if sk not in sol:
                bad.append("solved has no %s surface at y/b = %.5f" % (surf, sy))
                continue
            rp, sp = ref[rk], sol[sk]
            mask, xs = (shock_mask(rp) if (surf == 'upper' or MASK_LOWER) else (set(), None))
            if _DISABLE_MASK:            # selftest ARM 4 only
                mask = set()
            xs_list, r_list, s_list, outside = [], [], [], 0
            for i, (x, cpr) in enumerate(rp):
                if i in mask:
                    continue
                v = interp_solved(sp, x)
                if v is None:
                    outside += 1
                    continue
                xs_list.append(x)
                s_list.append(v)
                r_list.append(v - cpr)
            n_incl = len(rp) - len(mask)
            if n_incl and outside / float(n_incl) > OUTSIDE_FRAC:
                bad.append("y/b %.5f %s: %d of %d included reference points lie OUTSIDE the "
                           "solved x/c span -- refusing to extrapolate, and refusing to grade "
                           "on the remainder" % (ry, surf, outside, n_incl))
                continue
            if not r_list:
                bad.append("y/b %.5f %s: no comparable points" % (ry, surf))
                continue
            res.append({'yb_ref': ry, 'yb_sol': sy, 'label': rlab.get(ry, '?'), 'surface': surf,
                        'n': len(r_list), 'n_masked': len(mask), 'n_outside': outside,
                        'x_shock': xs, 'x': xs_list, 'solved': s_list, 'resid': r_list,
                        'rms': math.sqrt(sum(v * v for v in r_list) / len(r_list))})
    return (None, bad) if bad else (res, [])


# ------------------------------------------------------------------ planted controls
def _key(r):
    return (round(r['yb_ref'], 9), r['surface'])


def planted_controls(ref_path, sol_path, dcp=0.25):
    """PLANT A (sensitivity against a PREDICTED RMS), PLANT B (the solved side must not
    move), PLANT C (the shock mask must be live). All plant into a COPY OF THE REFERENCE
    TABLE ON DISK and re-run the real comparator FROM DISK."""
    out = []
    clean, bad = compare(ref_path, sol_path)
    if clean is None:
        return False, bad
    base = {_key(r): r for r in clean}

    ref, _ = load_table(ref_path)
    lines = open(ref_path).read().splitlines(True)

    def data_lines():
        idx = []
        for i, l in enumerate(lines):
            s = l.split('#')[0].strip()
            if s and len(re.split(r'[,\s]+', s)) >= 5:
                idx.append(i)
        return idx

    di = data_lines()

    def write_plant(dst, pick):
        """pick(yb, surf, xc) -> True to perturb that row."""
        n = 0
        with open(dst, 'w') as f:
            for i, l in enumerate(lines):
                if i in di:
                    t = re.split(r'[,\s]+', l.split('#')[0].strip())
                    yb, surf, xc, cp = float(t[1]), t[2].lower(), float(t[3]), float(t[4])
                    if pick(yb, surf, xc):
                        f.write("%s %s %s %s %.10g\n" % (t[0], t[1], t[2], t[3], cp + dcp))
                        n += 1
                        continue
                f.write(l)
        return n

    # choose a target: the first (section, upper) row that is INCLUDED (not masked)
    tgt = clean[0]
    tx = tgt['x'][len(tgt['x']) // 2]
    d = tempfile.mkdtemp(prefix='m6h1_cp_')

    # ---- PLANT A + B ----
    a = os.path.join(d, 'ref.A')
    na = write_plant(a, lambda yb, s, x: abs(yb - tgt['yb_ref']) < 1e-9 and s == tgt['surface']
                     and abs(x - tx) < 1e-12)
    pa, bada = compare(a, sol_path)
    out.append("target: section %s (y/b %.5f) %s, INCLUDED point x/c = %.6f, dCp = %+.4f"
               % (tgt['label'], tgt['yb_ref'], tgt['surface'], tx, dcp))
    out.append("PLANT A (sensitivity): perturbed %d REFERENCE row(s) in a COPY ON DISK" % na)
    if pa is None:
        out += ["   comparator refused on the planted file:"] + ['   ' + b for b in bada]
        shutil.rmtree(d, ignore_errors=True)
        return False, out
    pm = {_key(r): r for r in pa}
    tp = pm[_key(tgt)]
    k = tgt['x'].index(tx)
    rk = tgt['resid'][k]
    n = tgt['n']
    ss = sum(v * v for v in tgt['resid'])
    pred = math.sqrt((ss - rk * rk + (rk - dcp) ** 2) / n)
    moved_a = abs(tp['rms'] - tgt['rms']) > 1e-12 * max(1.0, tgt['rms'])
    exact_a = abs(tp['rms'] - pred) <= 1e-9 * max(1.0, pred)
    seen_a = bool(na == 1 and moved_a and exact_a and abs(dcp) > 1e-12)
    out.append("   clean RMS = %.10f   re-read RMS = %.10f   PREDICTED %.10f"
               % (tgt['rms'], tp['rms'], pred))
    out.append("   MOVED off clean: %s    moved to the PREDICTED value: %s    SEEN: %s"
               % (moved_a, exact_a, seen_a))
    if abs(dcp) <= 1e-12:
        out.append("   NOT A PLANT: dCp = 0 perturbs nothing, so nothing can be detected. "
                   "The control reports NOT DETECTED, as it must.")

    # PLANT B: the SOLVED side must be byte-identical
    sol_moved = []
    for kk, r in base.items():
        p = pm.get(kk)
        if p is None or len(p['solved']) != len(r['solved']):
            sol_moved.append("%s %s: solved vector changed LENGTH" % kk)
            continue
        for u, v in zip(r['solved'], p['solved']):
            if abs(u - v) > 0.0:
                sol_moved.append("%s %s: an interpolated SOLVED Cp moved (%.12g -> %.12g)"
                                 % (kk[0], kk[1], u, v))
                break
    seen_b = not sol_moved
    out.append("PLANT B (reference side ONLY): every interpolated SOLVED Cp unchanged: %s"
               % seen_b)
    for m in sol_moved[:3]:
        out.append("   " + m)

    # ---- PLANT C: perturb a MASKED point; RMS must not move ----
    seen_c, note_c = False, 'no masked point available -- the mask could not be exercised'
    rp = ref[(tgt['yb_ref'], tgt['surface'])]
    mask, xshock = shock_mask(rp)
    if mask:
        mx = rp[sorted(mask)[0]][0]
        c = os.path.join(d, 'ref.C')
        nc = write_plant(c, lambda yb, s, x: abs(yb - tgt['yb_ref']) < 1e-9
                         and s == tgt['surface'] and abs(x - mx) < 1e-12)
        pc, badc = compare(c, sol_path)
        if pc is None:
            note_c = 'comparator refused on the masked-plant file: %s' % '; '.join(badc)
        else:
            cm = {_key(r): r for r in pc}[_key(tgt)]
            unmoved = abs(cm['rms'] - tgt['rms']) <= 1e-12 * max(1.0, tgt['rms'])
            seen_c = (nc == 1) and unmoved
            note_c = ("perturbed %d EXCLUDED reference row(s) at x/c = %.6f (shock at x/c = %s); "
                      "RMS re-read %.10f vs clean %.10f -- UNMOVED: %s"
                      % (nc, mx, ('%.6f' % xshock) if xshock is not None else 'n/a',
                         cm['rms'], tgt['rms'], unmoved))
    out.append("PLANT C (the shock mask is live): " + note_c)
    shutil.rmtree(d, ignore_errors=True)

    ok = seen_a and seen_b and seen_c
    if not seen_a:
        out.append("   REFUSE: the comparator did not move to the PREDICTED RMS under a known "
                   "reference perturbation. Its clean RMS is NOT evidence (rule 3).")
    if not seen_b:
        out.append("   REFUSE: the solved side moved under a REFERENCE-ONLY plant. The RMS change "
                   "is re-interpolation, not the plant, and the control measured nothing "
                   "(section 10).")
    if not seen_c:
        out.append("   REFUSE: perturbing an EXCLUDED point moved the RMS, so the shock mask is "
                   "decorative, or no point was excluded at all.")
    return ok, out


# ------------------------------------------------------------------ age guard
def age_guard(sol_path, case):
    """Falsifier 2c / rule 4: an artifact written by a run other than the graded one."""
    z = os.path.join(case, '0', 'U')
    if not os.path.isfile(z):
        return ["--case %s given but it has no 0/U -- the age guard's reference file is absent, "
                "so the guard cannot be run and its silence would not be a pass" % case]
    if os.path.getmtime(sol_path) <= os.path.getmtime(z):
        return ["the solved Cp file is NOT NEWER than %s -- it was not written by the run this "
                "grading claims (age guard)" % z]
    return []


# ------------------------------------------------------------------ selftest
def _synth(path, sections, shift=0.0, noise=0.0, shock_at=0.62, jump=0.9):
    """A synthetic Cp table with a shock-like jump at shock_at on the upper surface."""
    with open(path, 'w') as f:
        f.write("# section y_over_b surface x_over_c Cp\n")
        for si, yb in enumerate(sections, 1):
            for surf in ('upper', 'lower'):
                for j in range(41):
                    x = j / 40.0
                    cp = -0.8 * math.sin(math.pi * min(x, 0.999)) if surf == 'upper' else 0.3 * x
                    if surf == 'upper' and x > shock_at:
                        cp += jump
                    cp += shift + noise * math.sin(37.0 * x + si)
                    f.write("S%d %.5f %s %.6f %.8f\n" % (si, yb, surf, x, cp))


def selftest():
    d = tempfile.mkdtemp(prefix='m6h1_cp_self_')
    secs = [0.20, 0.44, 0.65, 0.80, 0.90, 0.95, 0.99]
    ref = os.path.join(d, 'ref.dat')
    sol = os.path.join(d, 'sol.dat')
    _synth(ref, secs)
    _synth(sol, secs, noise=0.01)

    print("ARM 1 -- PLANT APPLIED, sound comparator: all three controls must be SEEN")
    ok1, msg = planted_controls(ref, sol)
    for m in msg:
        print("   " + m)
    print("   -> %s (expected DETECTED)" % ('DETECTED' if ok1 else 'NOT DETECTED'))

    print("\nARM 2 -- PLANT WITHHELD (dCp = 0: the reference is rewritten but UNCHANGED):")
    print("         the control must report NOT DETECTED.")
    ok2, msg = planted_controls(ref, sol, dcp=0.0)
    for m in msg:
        print("   " + m)
    print("   -> %s (expected NOT DETECTED)" % ('DETECTED' if ok2 else 'NOT DETECTED'))

    print("\nARM 3 -- BLINDED comparator (ignores its reference file): must REFUSE")
    g = globals()
    saved = g['compare']
    frozen = saved(ref, sol)
    g['compare'] = lambda r, s: frozen
    ok3, msg = planted_controls(ref, sol)
    g['compare'] = saved
    print("   " + msg[2])
    print("   " + msg[-1])
    print("   -> %s (expected NOT DETECTED)" % ('DETECTED' if ok3 else 'NOT DETECTED'))

    print("\nARM 4 -- DECORATIVE MASK comparator: the shock WINDOW is still identified (so a")
    print("         masked point can be targeted) but the comparator GRADES IT ANYWAY.")
    print("         PLANT C must refuse it by the RMS MOVING on an EXCLUDED point.")
    g['_DISABLE_MASK'] = True
    ok4, msg = planted_controls(ref, sol)
    g['_DISABLE_MASK'] = False
    print("   " + [m for m in msg if m.startswith('PLANT C')][0])
    print("   " + [m for m in msg if 'decorative' in m][0])
    print("   -> %s (expected NOT DETECTED)" % ('DETECTED' if ok4 else 'NOT DETECTED'))

    print("\nARM 5 -- SECTION PAIRING: a solved table whose sections are SHIFTED in y/b must")
    print("         DECLINE, not silently pair by row order and return a plausible RMS.")
    sol5 = os.path.join(d, 'sol5.dat')
    _synth(sol5, [0.21, 0.45, 0.66, 0.81, 0.91, 0.96, 0.995], noise=0.01)
    r5, bad5 = compare(ref, sol5)
    for x in bad5[:3]:
        print("   " + x)
    ok5 = r5 is None and any('NO solved section' in x for x in bad5)
    print("   -> %s (expected DECLINE)" % ('DECLINE' if ok5 else 'NO DECLINE -- DEFECT'))
    print("   (a comparator pairing by INDEX would have returned an RMS here, not a zero --")
    print("    which is why a planted zero cannot catch this class and the assertion must.)")

    print("\nARM 6 -- SECTION COUNT: a reference with 6 sections must DECLINE")
    ref6 = os.path.join(d, 'ref6.dat')
    _synth(ref6, secs[:6])
    sol6 = os.path.join(d, 'sol6.dat')
    _synth(sol6, secs[:6], noise=0.01)
    r6, bad6 = compare(ref6, sol6)
    ok6 = r6 is None and any('section 1.2 registers' in x for x in bad6)
    print("   " + (bad6[0] if bad6 else 'NO DECLINE -- DEFECT'))
    print("   -> %s (expected DECLINE)" % ('DECLINE' if ok6 else 'NO DECLINE -- DEFECT'))

    print("\nARM 7 -- NO EXTRAPOLATION: a solved table covering only x/c <= 0.5 must DECLINE")
    sol7 = os.path.join(d, 'sol7.dat')
    with open(sol7, 'w') as f, open(sol) as fi:
        for l in fi:
            if l.startswith('#'):
                f.write(l)
                continue
            t = l.split()
            if float(t[3]) <= 0.5:
                f.write(l)
    r7, bad7 = compare(ref, sol7)
    ok7 = r7 is None and any('OUTSIDE' in x for x in bad7)
    print("   " + (bad7[0] if bad7 else 'NO DECLINE -- DEFECT'))
    print("   -> %s (expected DECLINE)" % ('DECLINE' if ok7 else 'NO DECLINE -- DEFECT'))

    print("\nARM 8 -- the GATE must be able to FAIL: a solved table offset by dCp = 0.30")
    sol8 = os.path.join(d, 'sol8.dat')
    _synth(sol8, secs, shift=0.30)
    r8, bad8 = compare(ref, sol8)
    worst = max(x['rms'] for x in r8) if r8 else None
    ok8 = r8 is not None and worst > RMS_GATE
    print("   worst section RMS = %.5f against the gate %.3f -> %s"
          % (worst, RMS_GATE, 'GATE FAIL' if ok8 else 'NO FAIL -- DEFECT'))

    print("\nARM 9 -- and it must be able to PASS: the matched pair with 0.01 noise")
    r9, _ = compare(ref, sol)
    worst9 = max(x['rms'] for x in r9)
    ok9 = worst9 <= RMS_GATE
    print("   worst section RMS = %.5f against the gate %.3f -> %s"
          % (worst9, RMS_GATE, 'PASS' if ok9 else 'NO PASS -- DEFECT'))

    shutil.rmtree(d, ignore_errors=True)
    good = ok1 and (not ok2) and (not ok3) and (not ok4) and ok5 and ok6 and ok7 and ok8 and ok9
    print("\nSELFTEST %s" % ('PASS -- the controls SEE a real plant against a PREDICTED RMS, do '
                             'NOT see a withheld one, REFUSE a blinded comparator, REFUSE a '
                             'decorative mask, DECLINE on section mispairing, section count and '
                             'extrapolation, and the gate demonstrably returns BOTH PASS and '
                             'GATE FAIL' if good else 'FAIL'))
    return 0 if good else 1


# ------------------------------------------------------------------ main
def main(ref_path, sol_path, case=None):
    print("M6H1 H-G6 -- solved Cp against AGARD AR-138 Table B1-14, seven sections")
    print("REFERENCE: %s" % ref_path)
    print("SOLVED:    %s" % sol_path)
    print("REGISTERED (section 7): RMS dCp <= %.3f per section per surface, excluding the %d "
          "points nearest the shock.\n" % (RMS_GATE, N_SHOCK_EXCLUDE))
    print("SHOCK LOCATED ON THE %s SIDE (this lane's choice -- see GAP 1 in this file's "
          "header; it is NOT yet written into section 7)." % SHOCK_SIDE.upper())
    print("LOWER SURFACE MASKED: %s (GAP 2, likewise not yet in section 7).\n" % MASK_LOWER)

    for p, what in ((ref_path, 'reference table'), (sol_path, 'solved Cp')):
        if not os.path.isfile(p):
            print("REFUSE (exit 2): no %s at %s.\n"
                  "Note for the record: as at 2026-09-12 NO machine copy of AGARD Table B1-14 "
                  "exists on this box -- `find` over the repository returns none. H-G6 cannot be "
                  "graded until one is acquired and title-page verified under rule 15."
                  % (what, p))
            return 2

    if case:
        ag = age_guard(sol_path, case)
        if ag:
            for a in ag:
                print("  " + a)
            print("\nDECLINE (exit 2): age guard.")
            return 2

    ok, msg = planted_controls(ref_path, sol_path)
    print("PLANTED CONTROLS -- planted INTO THE REFERENCE, real comparator re-run FROM DISK")
    for m in msg:
        print("  " + m)
    if not ok:
        print("\nREFUSE (exit 2): the controls did not establish that this comparator responds to "
              "a known reference perturbation by the PREDICTED amount, holds the solved side "
              "fixed, and actually excludes the shock window. No RMS below would be evidence.")
        return 2

    res, bad = compare(ref_path, sol_path)
    if res is None:
        print("\nSAME-RUN / PAIRING ASSERTION")
        for b in bad:
            print("  " + b)
        print("\nDECLINE (exit 2): the reference and the solution are not paired section for "
              "section. A plausible RMS from a mispairing is a confident FALSE NUMBER, which a "
              "planted zero cannot catch.")
        return 2

    print("\n  %-6s %8s %8s %7s %7s %8s %10s %10s"
          % ('sec', 'y/b ref', 'y/b sol', 'surf', 'n', 'masked', 'x_shock', 'RMS dCp'))
    worst, fails = 0.0, []
    for r in res:
        worst = max(worst, r['rms'])
        flag = '' if r['rms'] <= RMS_GATE else '   *** ABOVE GATE ***'
        print("  %-6s %8.5f %8.5f %7s %7d %8d %10s %10.5f%s"
              % (r['label'], r['yb_ref'], r['yb_sol'], r['surface'], r['n'], r['n_masked'],
                 ('%.5f' % r['x_shock']) if r['x_shock'] is not None else '-', r['rms'], flag))
        if r['rms'] > RMS_GATE:
            fails.append(r)

    print("\nworst RMS dCp over %d (section, surface) pairs: %.5f, gate %.3f"
          % (len(res), worst, RMS_GATE))
    if fails:
        print("H-G6: GATE FAIL -- %d of %d pairs above the gate. Reported, NOT adjusted."
              % (len(fails), len(res)))
        return 1
    print("H-G6: PASS")
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    if len(sys.argv) < 3:
        sys.exit("usage: compare_cp.py <reference_table> <solved_cp> [case_dir_for_age_guard] "
                 "| --selftest")
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
