#!/usr/bin/env python3
"""
VMFL072 comparator -- DRAFT, UNTRACKED, NOT YET FROZEN.

Grades VMFL072 (Liquid Water Flow Over a Flat Plate Under the Influence of
Gravity) against the gate frozen in PREREGISTRATION.md.

REFUSES (exit 2) rather than degrading, on:
  * any strict-completion clause (rule 4, prereg 5.5)
  * a planted-zero control that does not fire (rule 3, prereg 5.4)
  * a missing or unreadable artifact

Verdict vocabulary is fixed (CLAUDE.md rule 1):
  PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING

Exit codes:  0 graded (any verdict)   2 refused   3 usage/internal
"""

import os
import re
import sys
import math
import shutil
import argparse

# ----------------------------------------------------------------------------
# FROZEN CONSTANTS -- these are the gate. They are fixed at the freeze commit of
# PREREGISTRATION.md and may not be edited after first compute (CLAUDE.md r2/r6).
# ----------------------------------------------------------------------------
CASE_ID = "VMFL072"
MANUAL_PAGE = "211-212"
REF_TABLE = "Table .72.1"

REF_MANUAL_M = 0.555e-3          # prereg 1  EXPERIMENTAL (Roy & Jain 1989)
REF_MANUAL_CLASS = "EXPERIMENTAL"
ANSYS_CONTEXT_M = 0.5497e-3      # prereg 1  context only, NEVER the gate

BAND_A = 0.0272                  # prereg 4.1  0.090 + 1.926 + 0.500 + 0.200 %
BAND_B = 0.0070                  # prereg 6.2  channel D + channel E only
CEILING_A = "GATE REACHED"       # prereg 3.4  experiment -> VERIF 2h.8.1 cap
CEILING_B = "PASS"               # prereg 6.2  exact soln of the same PDE

DELTA_N_M = 5.501148e-04         # prereg 2.5/6.1  lab-generated, indep. path in 6.5
GAMMA = 0.381000                 # kg/m/s
MU = 9.136691e-04                # Pa.s
RHO = 997.4                      # kg/m3
G_SIN = 6.305746                 # m/s2

MON_X_LO, MON_X_HI = 0.440, 0.460    # prereg 5.1  declared monitor station
MON_Y_LO, MON_Y_HI = 0.025, 0.075    # prereg 5.1  the manual's 50 mm width
STATION_CHECK_X = (0.300, 0.350, 0.400, 0.480)

PLATEAU_WINDOW_S = 2.0               # prereg 5.2
PLATEAU_THRESH_M = 2.7750e-07        # prereg 5.2  0.05 % of 0.555 mm (TEMPORAL)
READER_QUANTUM_M = 1.0e-15           # prereg 5.1  writePrecision 12 file quantum

# REPAIR 3 -- a SPATIAL development bound, derived separately from the temporal
# one. Propagating channel E's 0.200 % residual allowance at the monitor back
# along the known relaxation length L = 76.5 mm over x in [300, 480] mm:
#   resid(450) <= 0.002*delta_N  =>  spread <= resid(450)*(e^(130/L) - e^(-30/L))
# = 5.275e-06 m. Reusing PLATEAU_THRESH_M here would have FALSELY REFUSED a
# healthy run by 10.7x (measured) -- two different physical criteria, two
# different constants.
STATION_SPREAD_MAX_M = 5.275e-06      # prereg 5.1
RELAX_LENGTH_M = 0.0765               # U_eq * tau, prereg 3.3

# REPAIR 2 -- the threshold at which two grid levels stop being distinguishable.
# The file quantum (1e-15 m, 2e-12 relative) is NOT that threshold: it can never
# fire and would be an inert guard that reads as protective. The honest floor is
# the run's own TEMPORAL noise -- levels closer together than the plateau
# peak-to-peak are not resolved by this experiment.
TRIPLE_RESOLVE_M = PLATEAU_THRESH_M   # prereg 5.6

# REPAIR 1 -- the plant is a PROPER SUBSET of the averaging set, by area.
# The plant sub-region is frozen here; the expected shift is computed from the
# geometry the comparator itself reads and is NEVER hard-coded.
PLANT_M = 1.234000e-05               # prereg 5.4  2.24 % of delta -- must show
PLANT_SUBREGION_Y_MAX = 0.050        # prereg 5.4  lower half-span of the window
PLANT_TOL_M = 1.0e-09

# Admissibility floor. An additive plant on a LINEAR reader shifts the mean by a
# field-independent amount -- that is a property of linearity, not something a
# plant can defeat. The all-zeros hole is therefore closed HERE, by refusing a
# field that is not a film at all. 1e-6 m is 550x below delta_N and cannot be
# confused with a gate.
DELTA_ADMISSIBLE_MIN_M = 1.0e-06     # prereg 5.4

END_TIME = 10.0                      # prereg 5.2
WRITE_INTERVAL = 0.05
EXPECTED_TIME_DIRS = 200             # prereg 5.5 clause 5
REQUIRED_FIELDS_PRIMARY = ("U", "p")
REQUIRED_FIELDS_FILM = ("hf_film", "Uf_film")

GCI_FS = 1.25                        # CLAUDE.md rule 5
GCI_CAP = 0.005                      # prereg 4.1 channel D
BRACKET_CAP = 0.002                  # prereg 6.4 channel E
C1_CAP = 0.0005                      # prereg 6.3

COST_FILED_COREMIN = 360.0           # prereg 8.2
COST_CAP_COREMIN = 800.0   # prereg 8.2  4.50x method; see the cap table
RATE_USD_PER_COREH = 0.0513          # owner-stated; DERIVED, not measured


class Refuse(Exception):
    """Any condition on which the comparator must produce no number."""


# ----------------------------------------------------------------------------
# OpenFOAM ASCII readers
# ----------------------------------------------------------------------------
_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def read_scalar_field(path):
    """internalField of an OpenFOAM ASCII scalar field -> list[float]."""
    if not os.path.isfile(path):
        raise Refuse("field file absent: %s" % path)
    with open(path) as fh:
        txt = fh.read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(", txt)
    if m:
        depth, i, out, buf = 1, m.end(), [], []
        while i < len(txt) and depth:
            c = txt[i]
            if c == ")":
                depth -= 1
            elif c == "(":
                depth += 1
            else:
                buf.append(c)
            i += 1
        for tok in "".join(buf).split():
            try:
                out.append(float(tok))
            except ValueError:
                pass
        if not out:
            raise Refuse("empty internalField in %s" % path)
        return out
    m = re.search(r"internalField\s+uniform\s+(%s)" % _NUM, txt)
    if m:
        raise Refuse(
            "uniform internalField in %s -- a uniform film field at endTime is "
            "not a solved result" % path)
    raise Refuse("no parseable internalField in %s" % path)


def read_vector_field(path):
    """internalField of an OpenFOAM ASCII vector field -> list[(x,y,z)]."""
    if not os.path.isfile(path):
        raise Refuse("geometry file absent: %s" % path)
    with open(path) as fh:
        txt = fh.read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(", txt)
    if not m:
        raise Refuse("no nonuniform internalField in %s" % path)
    body = txt[m.end():]
    out = []
    for tup in re.finditer(r"\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM), body):
        out.append(tuple(float(g) for g in tup.groups()))
    if not out:
        raise Refuse("no vectors parsed from %s" % path)
    return out


def time_dirs(root):
    out = []
    if not os.path.isdir(root):
        return out
    for n in os.listdir(root):
        try:
            out.append((float(n), n))
        except ValueError:
            pass
    return sorted(out)


# ----------------------------------------------------------------------------
# Strict completion (CLAUDE.md rule 4 / prereg 5.5) -- refuse, never degrade
# ----------------------------------------------------------------------------
def check_completion(level_dir, log_path, rc_path):
    """All seven clauses. Any failure refuses."""
    notes = []

    # 1. rc = 0, captured INSIDE the detached wrapper
    if not os.path.isfile(rc_path):
        raise Refuse("no rc file at %s -- rc must be captured inside the "
                     "detached wrapper, never around the setsid line" % rc_path)
    rc = open(rc_path).read().strip()
    if rc != "0":
        raise Refuse("rc = %s (expected 0) at %s" % (rc, rc_path))
    notes.append("rc=0")

    # 2. an End line
    if not os.path.isfile(log_path):
        raise Refuse("no solver log at %s" % log_path)
    with open(log_path, errors="replace") as fh:
        log = fh.read()
    if not re.search(r"^End\s*$", log, re.M):
        raise Refuse("no 'End' line in %s" % log_path)
    notes.append("End")

    # 3. last time == endTime
    tds = [t for t, _ in time_dirs(level_dir)]
    if not tds:
        raise Refuse("no time directories in %s" % level_dir)
    if abs(max(tds) - END_TIME) > 1e-9:
        raise Refuse("last time %.6g != endTime %.6g in %s"
                     % (max(tds), END_TIME, level_dir))
    notes.append("lastTime==endTime")

    # 4. declared fields present at endTime
    end_name = [n for t, n in time_dirs(level_dir) if abs(t - END_TIME) <= 1e-9][0]
    end_dir = os.path.join(level_dir, end_name)
    for f in REQUIRED_FIELDS_PRIMARY:
        if not os.path.isfile(os.path.join(end_dir, f)):
            raise Refuse("primary field %s absent at endTime (%s)" % (f, end_dir))
    film_end = os.path.join(end_dir, "film")
    for f in REQUIRED_FIELDS_FILM:
        if not os.path.isfile(os.path.join(film_end, f)):
            raise Refuse("film field %s absent at endTime (%s)" % (f, film_end))
    notes.append("fields present")

    # 5. step accounting -- the registered analogue for an adjustable-step
    #    transient (prereg 5.5 clause 5). BOTH halves are checked.
    n_written = len([t for t in tds if t > 0.0])
    if n_written != EXPECTED_TIME_DIRS:
        raise Refuse("written time dirs = %d, expected endTime/writeInterval = %d"
                     % (n_written, EXPECTED_TIME_DIRS))
    n_exec = len(re.findall(r"^ExecutionTime", log, re.M))
    n_steps = len(re.findall(r"^Time = ", log, re.M))
    if n_exec != n_steps:
        raise Refuse("ExecutionTime lines (%d) != solver time steps (%d)"
                     % (n_exec, n_steps))
    notes.append("steps=%d writes=%d" % (n_steps, n_written))

    # 6. age guard -- every field at endTime strictly newer than the case's 0/U
    marker = os.path.join(level_dir, "0", "U")
    if not os.path.isfile(marker):
        raise Refuse("age-guard marker 0/U absent in %s" % level_dir)
    t0 = os.path.getmtime(marker)
    for d, fields in ((end_dir, REQUIRED_FIELDS_PRIMARY),
                      (film_end, REQUIRED_FIELDS_FILM)):
        for f in fields:
            p = os.path.join(d, f)
            if os.path.getmtime(p) <= t0:
                raise Refuse("AGE GUARD: %s is not newer than 0/U -- this field "
                             "predates the run allowed to produce it" % p)
    notes.append("age guard")

    return end_dir, film_end, notes


# ----------------------------------------------------------------------------
# The reader (prereg 5.1)
# ----------------------------------------------------------------------------
def load_geometry(level_dir):
    """faMesh face centres and areas, written once at t=0 (registered setup)."""
    gdir = os.path.join(level_dir, "constant", "film")
    ctr = read_vector_field(os.path.join(gdir, "Cf_film"))
    area = read_scalar_field(os.path.join(gdir, "magSf_film"))
    if len(ctr) != len(area):
        raise Refuse("faMesh geometry inconsistent: %d centres vs %d areas"
                     % (len(ctr), len(area)))
    return ctr, area


def window_indices(centres, xlo, xhi, ylo, yhi):
    idx = [i for i, c in enumerate(centres)
           if xlo <= c[0] <= xhi and ylo <= c[1] <= yhi]
    if not idx:
        raise Refuse("monitor window x[%g,%g] y[%g,%g] selects ZERO faces -- the "
                     "reader cannot see its own window" % (xlo, xhi, ylo, yhi))
    return idx


def area_weighted_mean(vals, areas, idx):
    num = sum(vals[i] * areas[i] for i in idx)
    den = sum(areas[i] for i in idx)
    if den <= 0.0:
        raise Refuse("zero total area over the monitor window")
    return num / den


def read_delta_mon(hf_path, centres, areas):
    hf = read_scalar_field(hf_path)
    if len(hf) != len(centres):
        raise Refuse("hf_film has %d values but faMesh has %d faces (%s)"
                     % (len(hf), len(centres), hf_path))
    idx = window_indices(centres, MON_X_LO, MON_X_HI, MON_Y_LO, MON_Y_HI)
    return area_weighted_mean(hf, areas, idx), hf, idx


def check_admissible(delta, where):
    """Close the all-zeros hole (prereg 5.4). An additive plant on a linear
    reader cannot do this; admissibility can."""
    if not (delta > 0.0) or delta < DELTA_ADMISSIBLE_MIN_M:
        raise Refuse(
            "monitor mean %.6e m at %s is not an admissible film thickness "
            "(floor %.1e m, 550x below delta_N). The run did not produce a "
            "film; there is nothing to grade." % (delta, where,
                                                  DELTA_ADMISSIBLE_MIN_M))


# ----------------------------------------------------------------------------
# Planted-zero control (CLAUDE.md rule 3, prereg 5.4)
# ----------------------------------------------------------------------------
def plant_and_reread(hf_path, centres, areas, idx, scratch, tag, reader=None):
    """Plant P into a PROPER SUBSET of the monitor window, by area, re-read
    through the SAME code path, and refuse unless the reader recovers the
    area-weighted expectation.

    REPAIR 1. The previous form planted into exactly the averaging set, so
    shift = P identically for EVERY possible input -- measured: it passed on
    ordinary values, wildly non-uniform values, all-identical values, negative
    garbage and ALL ZEROS, with |shift-P| <= 1.2e-14 in every case. Sizing P
    from the band defeats TUNING; it does nothing about CANCELLATION.

    Here the plant set is the lower half-span of the window and the expected
    shift is P * (sum a_planted / sum a_window), computed from the geometry the
    comparator itself reads -- never hard-coded. A reader that takes the wrong
    face set, returns a constant, reads a stale file, mis-maps token order to
    index, or reduces by max/min recovers a DIFFERENT shift and the control
    fires.

    HONEST LIMIT, stated rather than papered over: on a UNIFORM mesh the
    area-weighted and unweighted means are THE SAME FUNCTION, so no plant can
    separate them there -- they are not two readers. The --selftest arm uses a
    mesh whose area varies along the same axis as the sub-region predicate,
    where they differ and the unweighted mutant IS refused, proving the
    weighting is exercised.

    The plant acts on a scratch copy; the graded field is never mutated
    (prereg 5.4, VERIFICATION_CHARTER 35.2)."""
    rd = reader or read_delta_mon
    sub = [i for i in idx if centres[i][1] < PLANT_SUBREGION_Y_MAX]
    if not sub:
        raise Refuse("plant sub-region y < %g selects ZERO faces of the monitor "
                     "window" % PLANT_SUBREGION_Y_MAX)
    if len(sub) == len(idx):
        raise Refuse("plant sub-region is the WHOLE monitor window -- the plant "
                     "would cancel to P identically and could not fail")
    a_sub = sum(areas[i] for i in sub)
    a_win = sum(areas[i] for i in idx)
    frac = a_sub / a_win
    expected = PLANT_M * frac

    os.makedirs(scratch, exist_ok=True)
    planted = os.path.join(scratch, "hf_film.PLANTED.%s" % tag)
    shutil.copyfile(hf_path, planted)

    with open(planted) as fh:
        txt = fh.read()
    m = re.search(r"(internalField\s+nonuniform[^(]*\()", txt)
    if not m:
        raise Refuse("cannot locate internalField to plant into %s" % planted)
    start = m.end()
    depth, i = 1, start
    while i < len(txt) and depth:
        if txt[i] == ")":
            depth -= 1
        elif txt[i] == "(":
            depth += 1
        i += 1
    body_end = i - 1

    toks = txt[start:body_end].split()
    if len(toks) != len(centres):
        raise Refuse("plant: token count %d != face count %d"
                     % (len(toks), len(centres)))
    hit = set(sub)
    for j in range(len(toks)):
        if j in hit:
            toks[j] = repr(float(toks[j]) + PLANT_M)
    with open(planted, "w") as fh:
        fh.write(txt[:start] + "\n" + "\n".join(toks) + "\n" + txt[body_end:])

    clean, _, _ = rd(hf_path, centres, areas)
    seen, _, _ = rd(planted, centres, areas)
    shift = seen - clean
    if abs(shift - expected) >= PLANT_TOL_M:
        raise Refuse(
            "PLANTED-ZERO CONTROL DID NOT FIRE (%s): planted %.6e m into %d of "
            "the %d monitor faces (area fraction %.6f), so an area-weighted "
            "reader must shift by %.6e m; the reader shifted by %.6e m "
            "(discrepancy %.3e, tolerance %.1e). The reader cannot be shown "
            "able to recover a known non-zero, so its number is not evidence. "
            "No number is produced."
            % (tag, PLANT_M, len(sub), len(idx), frac, expected, shift,
               shift - expected, PLANT_TOL_M))
    return shift, expected, frac, len(sub)


# ----------------------------------------------------------------------------
# Plateau (prereg 5.2) and station check (prereg 5.1)
# ----------------------------------------------------------------------------
def plateau(level_dir, centres, areas):
    series = []
    for t, name in time_dirs(level_dir):
        if t < END_TIME - PLATEAU_WINDOW_S - 1e-9 or t <= 0.0:
            continue
        p = os.path.join(level_dir, name, "film", "hf_film")
        if not os.path.isfile(p):
            continue
        d, _, _ = read_delta_mon(p, centres, areas)
        series.append((t, d))
    if len(series) < 2:
        raise Refuse("fewer than 2 samples in the %.1f s plateau window -- the "
                     "criterion cannot be evaluated" % PLATEAU_WINDOW_S)
    vals = [d for _, d in series]
    ptp = max(vals) - min(vals)
    return ptp, ptp <= PLATEAU_THRESH_M, len(series)


def station_check(film_end_dir, centres, areas):
    hf = read_scalar_field(os.path.join(film_end_dir, "hf_film"))
    vals = []
    for x in STATION_CHECK_X:
        idx = window_indices(centres, x - 0.010, x + 0.010, MON_Y_LO, MON_Y_HI)
        vals.append((x, area_weighted_mean(hf, areas, idx)))
    spread = max(v for _, v in vals) - min(v for _, v in vals)
    # REPAIR 3: a SPATIAL bound, not the temporal one.
    return vals, spread, spread <= STATION_SPREAD_MAX_M


# ----------------------------------------------------------------------------
# Roache triple (CLAUDE.md rule 5)
# ----------------------------------------------------------------------------
def roache(f1, f2, f3, r=2.0):
    """f1 coarse, f2 medium, f3 fine. Returns (state, order, gci_fine).

    REPAIR 2: the EXACT/STAGNANT threshold is TRIPLE_RESOLVE_M -- the run's own
    temporal plateau noise -- NOT the 1e-15 m file quantum, which at 2e-12
    relative could essentially never fire and was an inert guard that read as
    protective. Two levels closer together than the run's temporal noise are
    not resolved by this experiment, whatever the file precision."""
    e32, e21 = f2 - f3, f1 - f2
    if abs(e32) < TRIPLE_RESOLVE_M and abs(e21) < TRIPLE_RESOLVE_M:
        return "EXACT", None, None
    if abs(e32) < TRIPLE_RESOLVE_M or abs(e21) < TRIPLE_RESOLVE_M:
        return "STAGNANT", None, None
    ratio = e21 / e32
    if ratio < 0.0:
        return "OSCILLATORY", None, None
    if abs(e32) >= abs(e21):
        return "DIVERGENT", None, None
    p = math.log(abs(ratio)) / math.log(r)
    gci = GCI_FS * abs(e32 / f3) / (r ** p - 1.0)
    return "CONVERGING", p, gci


# ----------------------------------------------------------------------------
# Grading
# ----------------------------------------------------------------------------
def grade(delta, ref, band):
    return abs(delta - ref) / abs(ref), abs(delta - ref) / abs(ref) <= band


def selftest(scratch):
    """Prove the planted control CAN FAIL, by driving it with mutant readers.
    A control that passes every mutant is not a control (VERIF 35.2)."""
    import random
    ok = True

    def build(nx, ny, nonuniform):
        ctr, ar = [], []
        dx, dy = 0.5 / nx, 0.1 / ny
        for i in range(nx):
            for j in range(ny):
                ctr.append((dx * (i + .5), dy * (j + .5), 0.0))
                ar.append(dx * dy * ((1.0 + 3.0 * j / ny) if nonuniform else 1.0))
        return ctr, ar

    def write(p, vals):
        with open(p, "w") as fh:
            fh.write("internalField   nonuniform List<scalar>\n%d\n(\n%s\n)\n;\n"
                     % (len(vals), "\n".join(repr(v) for v in vals)))

    os.makedirs(scratch, exist_ok=True)
    print("=" * 74)
    print("VMFL072 comparator --selftest : can the planted control FAIL?")
    print("=" * 74)

    # --- mutant readers, all with read_delta_mon's signature -----------------
    def mut_unweighted(path, centres, areas):
        hf = read_scalar_field(path)
        idx = window_indices(centres, MON_X_LO, MON_X_HI, MON_Y_LO, MON_Y_HI)
        return sum(hf[i] for i in idx) / len(idx), hf, idx

    def mut_wholeplate(path, centres, areas):
        hf = read_scalar_field(path)
        idx = window_indices(centres, MON_X_LO, MON_X_HI, MON_Y_LO, MON_Y_HI)
        allf = list(range(len(centres)))
        return area_weighted_mean(hf, areas, allf), hf, idx

    def mut_constant(path, centres, areas):
        hf = read_scalar_field(path)
        idx = window_indices(centres, MON_X_LO, MON_X_HI, MON_Y_LO, MON_Y_HI)
        return DELTA_N_M, hf, idx

    def mut_max(path, centres, areas):
        hf = read_scalar_field(path)
        idx = window_indices(centres, MON_X_LO, MON_X_HI, MON_Y_LO, MON_Y_HI)
        return max(hf[i] for i in idx), hf, idx

    def mut_stale(path, centres, areas):
        return read_delta_mon(os.path.join(scratch, "st_clean"), centres, areas)

    def mut_shifted(path, centres, areas):
        hf = read_scalar_field(path)
        idx = window_indices(centres, MON_X_LO + 0.02, MON_X_HI + 0.02,
                             MON_Y_LO, MON_Y_HI)
        return area_weighted_mean(hf, areas, idx), hf, idx

    for mesh_name, nonuni in (("NON-UNIFORM (weighting exercised)", True),
                              ("UNIFORM (production)", False)):
        ctr, ar = build(64, 16, nonuni)
        vals = [5.501148e-04 + 1e-7 * math.sin(c[0] * 40) for c in ctr]
        p = os.path.join(scratch, "st_clean")
        write(p, vals)
        _, _, idx = read_delta_mon(p, ctr, ar)
        print("\n--- %s mesh ---" % mesh_name)
        sh, exp, frac, nsub = plant_and_reread(p, ctr, ar, idx, scratch, "st")
        print("  TRUE reader                 : shift %.6e vs expected %.6e "
              "(frac %.6f, %d/%d faces)  -> FIRES"
              % (sh, exp, frac, nsub, len(idx)))
        for nm, mut in (("unweighted mean", mut_unweighted),
                        ("averages whole plate", mut_wholeplate),
                        ("returns a constant", mut_constant),
                        ("reduces by max", mut_max),
                        ("reads a stale file", mut_stale),
                        ("window shifted +20 mm", mut_shifted)):
            try:
                plant_and_reread(p, ctr, ar, idx, scratch, "st", reader=mut)
                verdict = "PASSED  <-- NOT CAUGHT"
                if not (nm == "unweighted mean" and not nonuni):
                    ok = False
            except Refuse:
                verdict = "REFUSED <-- caught"
            print("  mutant: %-24s -> %s" % (nm, verdict))
        if not nonuni:
            print("  NOTE: on a uniform mesh the area-weighted and unweighted")
            print("        means are THE SAME FUNCTION. No plant can separate")
            print("        them; they are not two readers. Expected, not a gap.")

    # --- all-zeros: closed by admissibility, NOT by the plant ---------------
    ctr, ar = build(64, 16, False)
    p = os.path.join(scratch, "st_zero")
    write(p, [0.0] * len(ctr))
    d, _, idx = read_delta_mon(p, ctr, ar)
    print("\n--- ALL-ZEROS field ---")
    sh, exp, _, _ = plant_and_reread(p, ctr, ar, idx, scratch, "z")
    print("  plant alone            : shift %.6e == expected %.6e -> PASSES."
          % (sh, exp))
    print("    (an additive plant on a LINEAR reader is field-independent by")
    print("     construction; no plant can defeat that.)")
    try:
        check_admissible(d, "selftest")
        print("  admissibility          : PASSED  <-- NOT CAUGHT"); ok = False
    except Refuse as e:
        print("  admissibility          : REFUSED <-- caught (%s)" % str(e)[:52])

    # --- roache limbs can all fire ------------------------------------------
    print("\n--- Roache classification (threshold %.4e m, REPAIR 2) ---"
          % TRIPLE_RESOLVE_M)
    for nm, t in (("CONVERGING", (0.5560e-3, 0.5520e-3, 0.5510e-3)),
                  ("OSCILLATORY", (0.5510e-3, 0.5540e-3, 0.5510e-3)),
                  ("DIVERGENT", (0.5510e-3, 0.5520e-3, 0.5560e-3)),
                  ("EXACT", (0.5501148e-3,) * 3),
                  ("STAGNANT", (0.5560e-3, 0.5501148e-3, 0.5501149e-3))):
        got = roache(*t)[0]
        good = got == nm
        ok = ok and good
        print("  %-12s -> %-12s %s" % (nm, got, "ok" if good else "<-- WRONG"))

    print("\n" + "=" * 74)
    print("SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    print("=" * 74)
    return 0 if ok else 3


def main():
    ap = argparse.ArgumentParser(description="VMFL072 comparator (DRAFT)")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the planted control can fail; grades nothing")
    ap.add_argument("--runs", required=False,
                    help="verification/runs/ansys_verification/VMFL072")
    ap.add_argument("--scratch", required=True, help="scratch dir for plants")
    ap.add_argument("--cost-coremin", type=float, default=None)
    ap.add_argument("--prereg-sha", default=None,
                    help="sha of the FROZEN PREREGISTRATION.md (rule 2)")
    a = ap.parse_args()

    if a.selftest:
        return selftest(a.scratch)
    if not a.runs:
        ap.error("--runs is required unless --selftest is given")

    print("=" * 74)
    print("%s comparator -- manual p.%s, %s" % (CASE_ID, MANUAL_PAGE, REF_TABLE))
    print("reference %.4f mm (%s) | Ansys Fluent %.4f mm (CONTEXT, not the gate)"
          % (REF_MANUAL_M * 1e3, REF_MANUAL_CLASS, ANSYS_CONTEXT_M * 1e3))
    print("prereg sha: %s" % (a.prereg_sha or "NOT SUPPLIED -- grading path unproven"))
    print("=" * 74)

    if not a.prereg_sha:
        print("\nVERDICT: NOT A RESULT")
        print("  the grading path is fixed at the pre-registration commit and the "
              "frozen file must be hashed against the committed blob (rule 2).")
        return 2

    levels = {}
    try:
        for tag in ("L1", "L2", "L3"):
            d = os.path.join(a.runs, tag)
            end_dir, film_end, notes = check_completion(
                d, os.path.join(d, "log.pimpleFoam"), os.path.join(d, "rc"))
            centres, areas = load_geometry(d)
            hf_path = os.path.join(film_end, "hf_film")
            delta, _, idx = read_delta_mon(hf_path, centres, areas)
            check_admissible(delta, "%s endTime" % tag)
            shift, exp, frac, nsub = plant_and_reread(
                hf_path, centres, areas, idx, a.scratch, tag)
            ptp, ok_plat, ns = plateau(d, centres, areas)
            stations, spread, ok_stat = station_check(film_end, centres, areas)
            levels[tag] = dict(delta=delta, ptp=ptp, ok_plat=ok_plat,
                               spread=spread, ok_stat=ok_stat, nfaces=len(idx),
                               shift=shift, notes=notes, nsamp=ns)
            print("\n[%s] completion: %s" % (tag, ", ".join(notes)))
            print("     plant FIRED: P=%.6e into %d of %d monitor faces "
                  "(area frac %.6f) -> expected %.6e, saw %.6e"
                  % (PLANT_M, nsub, len(idx), frac, exp, shift))
            print("     delta_mon = %.6f mm" % (delta * 1e3))
            print("     plateau ptp = %.4e m over %d samples (thresh %.4e) -> %s"
                  % (ptp, ns, PLATEAU_THRESH_M, "OK" if ok_plat else "NOT PLATEAUED"))
            print("     station spread %.4e m (thresh %.4e) -> %s"
                  % (spread, STATION_SPREAD_MAX_M,
                     "developed" if ok_stat else "NOT DEVELOPED"))
    except Refuse as e:
        print("\nREFUSED: %s" % e)
        print("\nVERDICT: NOT A RESULT")
        return 2

    # rule 5 limb (1), one-way -- no path below may lift this
    bad = [t for t in levels if not levels[t]["ok_plat"] or not levels[t]["ok_stat"]]
    state, order, gci = roache(levels["L1"]["delta"], levels["L2"]["delta"],
                               levels["L3"]["delta"])
    d3 = levels["L3"]["delta"]
    eA, okA = grade(d3, REF_MANUAL_M, BAND_A)
    eB, okB = grade(d3, DELTA_N_M, BAND_B)

    print("\n" + "-" * 74)
    print("TRIPLE (r=2, Fs=%.2f): %s" % (GCI_FS, state))
    if state == "CONVERGING":
        print("  observed order p = %.3f   GCI_fine = %.4f %%" % (order, gci * 100))
    else:
        print("  values L1/L2/L3 = %.6f / %.6f / %.6f mm"
              % tuple(levels[t]["delta"] * 1e3 for t in ("L1", "L2", "L3")))
    print("\nLIMB A (vs manual %.4f mm, %s): delta=%.4f mm  e=%.3f %%  band %.2f %%"
          % (REF_MANUAL_M * 1e3, REF_MANUAL_CLASS, d3 * 1e3, eA * 100, BAND_A * 100))
    print("LIMB B (vs delta_N %.4f mm, exact soln of the same PDE): e=%.3f %%  "
          "band %.2f %%" % (DELTA_N_M * 1e3, eB * 100, BAND_B * 100))

    if bad:
        vA = vB = "NOT A RESULT"
        print("\n  rule 5 limb (1): levels %s not plateaued/developed -- one-way."
              % ", ".join(sorted(bad)))
    elif state != "CONVERGING":
        vA = vB = "NOT A RESULT"
    else:
        vA = CEILING_A if okA else "GATE FAIL"
        vB = CEILING_B if okB and gci <= GCI_CAP else "GATE FAIL"

    print("\n" + "=" * 74)
    print("VERDICT LIMB A: %s   (ceiling %s -- experimental reference, "
          "VERIFICATION_CHARTER 2h.8.1 v1.27 2026-08-31 exact-PDE rule)"
          % (vA, CEILING_A))
    print("VERDICT LIMB B: %s   (ceiling %s -- discretisation-error claim only, "
          "bounded by the levels actually run)" % (vB, CEILING_B))
    if a.cost_coremin is not None:
        over = a.cost_coremin > COST_CAP_COREMIN
        print("COST: %.1f core-min actual vs %.1f filed (ratio %.2f), cap %.1f%s"
              % (a.cost_coremin, COST_FILED_COREMIN,
                 a.cost_coremin / COST_FILED_COREMIN, COST_CAP_COREMIN,
                 "  -- OVERRUN, RUN STOPS" if over else ""))
        print("      $%.2f DERIVED at $%.4f/core-h (owner-stated; the box cannot "
              "read its own billing) -- NOT measured"
              % (a.cost_coremin / 60 * RATE_USD_PER_COREH, RATE_USD_PER_COREH))
    print("=" * 74)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refuse as e:
        print("\nREFUSED: %s\n\nVERDICT: NOT A RESULT" % e)
        sys.exit(2)
