#!/usr/bin/env python3
"""T15 -- the FROZEN comparator.  UNSTEADY axisymmetric MTT plume on T8's fine
mesh, ONE LEVEL, buoyantBoussinesqPimpleFoam.

THIS RUNG HAS ONE MESH.  THERE IS NO ROACHE TRIPLE AND NONE IS COMPUTED.
gci_equal IS IMPORTED AND EXERCISED IN THE SELFTEST SO THAT THE IMPORTED FLOORS
ARE DEMONSTRABLY LIVE, AND IT IS CALLED ON NO GRADED ROW.  Every graded row
carries the stamp SINGLE-MESH, NO GRID-CONVERGENCE EVIDENCE; no GCI, no
Richardson extrapolate and no discretisation uncertainty is quoted anywhere,
and the capability this rung can earn is CAN DO, CAVEATS at best
(docs/capability/heat-transfer_GRID.md).

ROACHE FLOORS ARE IMPORTED (MESH_STANDARD.md section 10.5, chief ruling
01967a7b): STAGNANT_FLOOR, P_MIN, FS, gci_equal and PLANT come from
scripts/roache_triple.py; this file defines none of them and REFUSES if
T15_registered.json's `roache_floors` block differs from the import.

T8 GROUND 2 (T8_VERDICT_2026-08-26.md section 4): "READ CENTROIDS FROM DISK.
NEVER REGISTER A RATIO TAKEN FROM THE NOMINAL MESH SPEC."  Every radius and
every cell volume in this file is read from `0/Cx`, `0/Cz`, `0/V` that OpenFOAM
itself wrote; the ONLY geometric fact asserted is the STRUCTURAL one
r2 > r1 > 0.  The measured r2/r1 is PRINTED and gated on nothing.

L-342 FIELD CLASSES: this comparator refuses only on PHYSICS-CRITICAL facts
(the DONE marker, the fields on disk, the probe series, the log's Courant
numbers, the registered specification and its own referent).  Infrastructure
fields (STATUS wall_s, capped, timeout_s, checkmesh_rc ...) are never read here.

NO `assert` (L-332).  Every refusal is sys.exit(2).  apply_gate() is the ONLY
function that writes a verdict.

Exit: 0 graded, 2 REFUSAL.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import mtt_t15 as MTT                                                   # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT   # noqa: E402

CASE = "T15_UP_f"
EXIT_OK, EXIT_REFUSE = 0, 2
PLANE_TOL = 1e-9


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def load_registered(root=None):
    p = os.path.join(root or HERE, "T15_registered.json")
    if not os.path.isfile(p):
        refuse("no T15_registered.json -- the gate is not registered")
    reg = json.load(open(p))
    fl = reg.get("roache_floors", {})
    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN or fl.get("FS") != FS:
        refuse("registered floors %r disagree with the imported roache_triple STAGNANT_FLOOR=%r P_MIN=%r "
               "FS=%r (MESH_STANDARD 10.5: one name, one number)" % (fl, STAGNANT_FLOOR, P_MIN, FS))
    if reg.get("grid_triple") is not False:
        refuse("T15_registered.json must record grid_triple = false: this rung has ONE mesh and no triple "
               "may be computed from it")
    return reg


def case_meta(case_dir):
    p = os.path.join(case_dir, "CASE.txt")
    if not os.path.isfile(p):
        refuse("no CASE.txt for %s" % case_dir)
    out = {}
    for ln in open(p):
        if ln.startswith("#") or not ln.strip():
            continue
        parts = ln.split()
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    return out


def latest_time(case_dir):
    ts = [t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    return max(ts, key=float) if ts else None


# ------------------------------------------------------------ THE READERS
def read_scalar(path):
    if not os.path.isfile(path):
        return None
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", txt, re.S)
    if m:
        return [float(v) for v in m.group(1).split()]
    m = re.search(r"internalField\s+uniform\s+([0-9.eE+-]+)\s*;", txt)
    if m:
        return ("uniform", float(m.group(1)))
    return None


def read_vector_z(path):
    """z component of a volVectorField, in cell order."""
    if not os.path.isfile(path):
        return None
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\n\(\s*\n(.*?)\n\)\s*\n;", txt, re.S)
    if not m:
        return None
    out = []
    for tup in re.findall(r"\(([^()]*)\)", m.group(1)):
        p = tup.split()
        if len(p) != 3:
            return None
        out.append(float(p[2]))
    return out


def build_planes(cx, cz, nz_expect, nr_expect):
    """Group cells into axial planes by their MEASURED Cz, radial order by the
    MEASURED Cx.  Nothing about blockMesh's cell ordering is assumed; the plane
    and column counts are checked STRUCTURALLY and refused, never repaired."""
    buckets = {}
    for i, z in enumerate(cz):
        buckets.setdefault(round(z / PLANE_TOL), []).append(i)
    keys = sorted(buckets)
    if len(keys) != nz_expect:
        refuse("the measured cell centres form %d axial planes, the registered mesh has %d "
               "(Cz read from 0/Cz, written by OpenFOAM)" % (len(keys), nz_expect))
    planes = []
    for k in keys:
        idx = sorted(buckets[k], key=lambda i: cx[i])
        if len(idx) != nr_expect:
            refuse("an axial plane holds %d cells, the registered mesh has %d radial columns"
                   % (len(idx), nr_expect))
        planes.append((cz[idx[0]], idx))
    return planes


def axis_extrapolate(f1, f2, r1, r2):
    """Parabolic-with-zero-axis-slope extrapolation to r = 0 from the two
    innermost cells, at their MEASURED radii:  f(r) = f0 - a r^2 gives
        f0 = (f1 r2^2 - f2 r1^2) / (r2^2 - r1^2).
    The ONLY precondition asserted is the STRUCTURAL r2 > r1 > 0 -- T8's
    registered (9 f1 - f2)/8 asserted r2 = 3 r1 from the nominal spec and the
    mesh gave 7/3 (T8_VERDICT_2026-08-26.md section 3).  NO RATIO IS ASSERTED."""
    if not (r2 > r1 > 0.0):
        refuse("axis extrapolation: the measured radii are not r2 > r1 > 0 (r1 = %.12g, r2 = %.12g)" % (r1, r2))
    return (f1 * r2 * r2 - f2 * r1 * r1) / (r2 * r2 - r1 * r1)


def axis_linear(f1, f2, r1, r2):
    """Linear extrapolation to r = 0: REPORTED beside the parabolic one so a
    reader sees the extrapolation's own contribution.  Never graded."""
    return (f1 * r2 - f2 * r1) / (r2 - r1)


def axis_profile(vals, planes, cx, kind="parab"):
    fn = axis_extrapolate if kind == "parab" else axis_linear
    out = []
    for z, idx in planes:
        i1, i2 = idx[0], idx[1]
        out.append((z, fn(vals[i1], vals[i2], cx[i1], cx[i2])))
    return out


def interp_station(prof, zs):
    """Linear interpolation in z between the two bracketing planes; the same
    physical stations on any mesh."""
    zz = [p[0] for p in prof]
    vv = [p[1] for p in prof]
    out = []
    for z in zs:
        if z < zz[0] or z > zz[-1]:
            refuse("station z = %.6g is outside the meshed range [%.6g, %.6g]" % (z, zz[0], zz[-1]))
        j = 0
        while j < len(zz) - 2 and zz[j + 1] < z:
            j += 1
        s = (z - zz[j]) / (zz[j + 1] - zz[j])
        out.append(vv[j] + s * (vv[j + 1] - vv[j]))
    return out


def plume_fluxes(w, vol, planes, scale, dz):
    """Q(z) and M(z) from the MEASURED cell volumes, over the CONNECTED radial
    run from the axis out to the first cell where the mean w is not positive.
    The run's outer radius r_e(z) is REPORTED."""
    Q, M, RE, NC = [], [], [], []
    for z, idx in planes:
        q = m = 0.0
        n = 0
        for i in idx:
            if w[i] <= 0.0:
                break
            q += w[i] * vol[i]
            m += w[i] * w[i] * vol[i]
            n += 1
        Q.append((z, scale * q / dz))
        M.append((z, scale * m / dz))
        RE.append((z, n))
        NC.append(n)
    return Q, M, RE, NC


def tophat_radius(Q, M):
    out = []
    for (z, q), (_z, m) in zip(Q, M):
        if m <= 0.0 or q <= 0.0:
            out.append((z, 0.0))
        else:
            out.append((z, q / math.sqrt(math.pi * m)))
    return out


# ------------------------------------------------- the probe time series
def read_probe_series(case_dir, want_z, comp="z"):
    """(times, values) at the probe whose HEADER z equals want_z.  The column is
    located from the file's own `# Probe k (x y z)` header, never by position."""
    base = os.path.join(case_dir, "postProcessing", "axisProbes")
    if not os.path.isdir(base):
        return None, None, "no postProcessing/axisProbes"
    subs = sorted(os.listdir(base), key=lambda s: float(s) if re.fullmatch(r"[0-9.eE+-]+", s) else 1e30)
    name = "U" if comp == "z" else "T"
    times, vals = [], []
    col = None
    for sub in subs:
        p = os.path.join(base, sub, name)
        if not os.path.isfile(p):
            continue
        for ln in open(p):
            if ln.startswith("#"):
                m = re.match(r"#\s*Probe\s+(\d+)\s+\(([^)]*)\)", ln)
                if m:
                    xyz = [float(v) for v in m.group(2).split()]
                    if len(xyz) == 3 and abs(xyz[2] - want_z) < 1e-9:
                        col = int(m.group(1))
                continue
            if col is None:
                continue
            if comp == "z":
                m = re.match(r"\s*([0-9.eE+-]+)\s+(.*)$", ln)
                if not m:
                    continue
                tup = re.findall(r"\(([^()]*)\)", m.group(2))
                if col >= len(tup):
                    continue
                p3 = tup[col].split()
                if len(p3) != 3:
                    continue
                times.append(float(m.group(1)))
                vals.append(float(p3[2]))
            else:
                p2 = ln.split()
                if len(p2) < col + 2:
                    continue
                times.append(float(p2[0]))
                vals.append(float(p2[col + 1]))
    if col is None:
        return None, None, "no probe at z = %.6g in the file's own header" % want_z
    if not times:
        return None, None, "the probe file at z = %.6g holds no samples" % want_z
    return times, vals, ""


def window_stats(times, vals, t0, t1):
    w = [(t, v) for t, v in zip(times, vals) if t0 <= t <= t1]
    if len(w) < 20:
        refuse("the registered window [%g, %g] holds only %d probe samples; a fluctuation statistic "
               "over fewer than 20 samples is not a statistic" % (t0, t1, len(w)))
    ts = [a for a, _ in w]
    vs = [b for _, b in w]
    n = len(vs)
    mean = sum(vs) / n
    var = sum((v - mean) ** 2 for v in vs) / n
    sd = math.sqrt(var)
    mt = sum(ts) / n
    sxx = sum((t - mt) ** 2 for t in ts)
    slope = sum((t - mt) * (v - mean) for t, v in w) / sxx if sxx > 0 else 0.0
    half = n // 2
    def sdev(xs):
        if len(xs) < 2:
            return 0.0
        mu = sum(xs) / len(xs)
        return math.sqrt(sum((x - mu) ** 2 for x in xs) / len(xs))
    s1h, s2h = sdev(vs[:half]), sdev(vs[half:])
    return dict(n=n, t0=ts[0], t1=ts[-1], mean=mean, sd=sd,
                rel_sd=(sd / abs(mean)) if mean != 0.0 else float("inf"),
                trend_slope=slope,
                drift_frac=(abs(slope) * (ts[-1] - ts[0]) / abs(mean)) if mean != 0.0 else float("inf"),
                sd_first_half=s1h, sd_second_half=s2h,
                persistence=(s2h / s1h) if s1h > 0 else None)


# ---------------------------------------------------- the log-side controls
def courant_and_bounding(case_dir, dt, t_window_start):
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return None, "no log.solve"
    body = open(log, errors="replace").read()
    co, t = [], 0.0
    for m in re.finditer(r"^(?:Courant Number mean:.*max: ([0-9.eE+-]+)|Time = ([0-9.eE+-]+))\s*$", body, re.M):
        if m.group(2) is not None:
            t = float(m.group(2))
        else:
            co.append((t, float(m.group(1))))
    if not co:
        return None, "log.solve carries no Courant lines"
    n_bound = len(re.findall(r"bounding (?:epsilon|k),", body))
    n_steps = len(re.findall(r"^ExecutionTime", body, re.M))
    win = [c for tt, c in co if tt >= t_window_start]
    return dict(max_all=max(c for _, c in co), max_window=max(win) if win else None,
                n_courant=len(co), n_bounding_lines=n_bound, n_steps=n_steps,
                bounding_per_step=(n_bound / n_steps) if n_steps else None,
                has_End=bool(re.search(r"^End\s*$", body, re.M))), ""


# ------------------------------------------- rule 3: planted-zero control
def _plant_scalar_file(path, idxs, mag, alternate=False):
    lines = open(path).read().splitlines(True)
    start = None
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if start is None:
        refuse("planted-zero control: could not locate internalField STRUCTURALLY in %s" % path)
    orig = list(lines)
    for n, k in enumerate(idxs):
        s = (-1.0 if (alternate and n % 2) else 1.0) * mag
        raw = lines[start + k].strip()
        mv = re.fullmatch(r"\(([^()]*)\)", raw)
        if mv:                       # volVectorField: plant into the z component
            c = mv.group(1).split()
            if len(c) != 3:
                refuse("planted-zero control: %s line %d is not a 3-vector" % (path, start + k))
            c[2] = "%.17g" % (float(c[2]) + s)
            lines[start + k] = "(%s)\n" % " ".join(c)
        else:
            lines[start + k] = "%.17g\n" % (float(raw) + s)
    open(path, "w").write("".join(lines))
    return orig


def _plant_probe_file(path, col, t0, t1, mag, alternate=True, comp="z"):
    lines = open(path).read().splitlines(True)
    orig = list(lines)
    n = 0
    for i, ln in enumerate(lines):
        if ln.startswith("#"):
            continue
        if comp == "z":
            m = re.match(r"\s*([0-9.eE+-]+)\s+(.*)$", ln)
            if not m:
                continue
            tt = float(m.group(1))
            if not (t0 <= tt <= t1):
                continue
            tup = re.findall(r"\(([^()]*)\)", m.group(2))
            if col >= len(tup):
                continue
            p3 = tup[col].split()
            s = (-1.0 if (alternate and n % 2) else 1.0) * mag
            p3[2] = "%.17g" % (float(p3[2]) + s)
            tup[col] = " ".join(p3)
            lines[i] = "%s\t%s\n" % (m.group(1), " ".join("(%s)" % x for x in tup))
            n += 1
    open(path, "w").write("".join(lines))
    return orig, n


def planted_zero_control(case_dir, time, reg, readers, probe_reader):
    """BOTH ARMS, SIZED TO EACH READER (L-340), and sized RELATIVE TO THE
    READER'S OWN SCALE rather than to an absolute constant -- the lesson
    T8_STEADINESS_MEASUREMENT_2026-08-26.md section 7.2 paid for: "a planted-zero
    control sized against a converged field is blind precisely on the cases
    where a reader most needs checking".

      * POINT readers (the axis extrapolation) get a plant in the two cells the
        extrapolation reads, located STRUCTURALLY by index;
      * the INTEGRATING reader (the top-hat radius, ~N cells of a radial run)
        gets an ALL-CELL plant over that run, so the read moves by ~plant
        instead of plant/N;
      * the FLUCTUATION reader (S1 = sigma/mean over the probe window) gets an
        ALTERNATING +-plant over every sample in the window: a CONSTANT offset
        moves the mean and not the standard deviation, so a constant plant
        would be invisible to a WORKING reader.  The constant-offset arm is
        driven too and the control REFUSES if sigma moves by more than
        round-off under it.

    Copies the files the readers read into scratch first; never writes into the
    case.  A descending ladder records the demonstrated detection floor as a
    FRACTION OF THE READER'S OWN SCALE."""
    tmp = tempfile.mkdtemp(prefix="t15pz_")
    out = {}
    try:
        dst = os.path.join(tmp, CASE)
        for rel in (os.path.join("0", "Cx"), os.path.join("0", "Cz"), os.path.join("0", "V"),
                    os.path.join(str(time), "UMean"), os.path.join(str(time), "TMean")):
            src = os.path.join(case_dir, rel)
            if not os.path.isfile(src):
                refuse("planted-zero control: %s is missing; a missing number is not a zero" % src)
            os.makedirs(os.path.dirname(os.path.join(dst, rel)), exist_ok=True)
            shutil.copy2(src, os.path.join(dst, rel))
        pp = os.path.join(case_dir, "postProcessing")
        if os.path.isdir(pp):
            shutil.copytree(pp, os.path.join(dst, "postProcessing"))
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control: scratch copy resolved INSIDE the case tree")

        for name, target_rel, fn, idxs in readers:
            p = os.path.join(dst, target_rel)
            ref = fn(dst)
            again = fn(dst)
            if ref != again:
                refuse("planted-zero control %s NEGATIVE ARM FAILED: two reads of identical bytes differ "
                       "(%.17g vs %.17g) -- the reader is NOISY" % (name, ref, again))
            scale = abs(ref) if ref != 0.0 else 1.0
            seen, floor = {}, None
            for frac in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
                orig = _plant_scalar_file(p, idxs, frac * scale)
                got = fn(dst)
                open(p, "w").write("".join(orig))
                d = abs(got - ref)
                seen[frac] = d
                if d > 0.0:
                    floor = frac
            if floor is None:
                refuse("planted-zero control %s POSITIVE ARM FAILED: no plant magnitude was visible -- "
                       "the reader is BLIND" % name)
            if seen[PLANT] < 0.1 * PLANT * scale:
                refuse("planted-zero control %s: the registered plant %.6g x scale %.6g moved the read by "
                       "only %.3g (< 0.1 x plant; L-340 sizing) while %.6g x scale was visible"
                       % (name, PLANT, scale, seen[PLANT], floor))
            out[name] = dict(status="PASS", plant_fraction=PLANT, reader_scale=scale,
                             cells_planted=len(idxs), recovered=seen[PLANT],
                             demonstrated_detection_floor_fraction=floor,
                             ladder={("%g" % k): v for k, v in seen.items()})
            print("planted-zero control %-10s PASS: plant %.6g x reader scale %.6g in %d cell(s), "
                  "recovered %.6g, floor %.1g x scale" % (name, PLANT, scale, len(idxs), seen[PLANT], floor))

        # the FLUCTUATION reader
        name, prel, col, t0, t1 = probe_reader
        p = os.path.join(dst, prel)
        if not os.path.isfile(p):
            refuse("planted-zero control: no probe file at %s" % p)
        ref = _s1_of(dst, reg)
        if ref != _s1_of(dst, reg):
            refuse("planted-zero control %s NEGATIVE ARM FAILED: the reader is NOISY" % name)
        _t, _v, _w = read_probe_series(dst, reg["s1_station_z_m"])
        if _t is None:
            refuse("planted-zero control %s: %s" % (name, _w))
        st_ref = window_stats(_t, _v, t0, t1)
        mean_scale = abs(st_ref["mean"])
        seen, floor = {}, None
        for frac in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
            orig, n = _plant_probe_file(p, col, t0, t1, frac * mean_scale, alternate=True)
            got = _s1_of(dst, reg)
            open(p, "w").write("".join(orig))
            d = abs(got - ref)
            seen[frac] = d
            if d > 0.0:
                floor = frac
        if floor is None:
            refuse("planted-zero control %s POSITIVE ARM FAILED: no alternating plant was visible -- "
                   "the fluctuation reader is BLIND" % name)
        # THE SIZING RULE FOR A DISPERSION-RATIO READER, AND WHY IT IS NOT THE
        # 0.1 x plant RULE THE ADDITIVE READERS CARRY.  S1 = sigma/mean combines
        # a plant IN QUADRATURE: an alternating +-p raises sigma to
        # sqrt(sigma^2 + p^2), so the response to a small p on a series that is
        # ALREADY fluctuating is second order and NO fixed fraction of the plant
        # can be demanded of it.  This is exactly the inversion
        # T8_STEADINESS_MEASUREMENT_2026-08-26.md section 7.2 measured -- "the
        # control gets weaker exactly as the case gets worse" -- and the answer
        # registered here is to demand (a) an exactly-zero negative arm, (b) a
        # visible plant, (c) a plant equal to the WHOLE MEAN moving sigma/mean by
        # at least 0.5, (d) the registered plant moving it above round-off, and
        # (e) the MEASURED detection floor and the quadrature prediction recorded
        # rather than asserted in advance.
        quad = math.sqrt(st_ref["sd"] ** 2 + (PLANT * mean_scale) ** 2) / abs(st_ref["mean"]) - ref
        if seen[1.0] < 0.5:
            refuse("planted-zero control %s: a plant equal to the WHOLE MEAN moved sigma/mean by only "
                   "%.3g -- a dispersion reader that cannot see that is not reading dispersion"
                   % (name, seen[1.0]))
        if seen[PLANT] <= 1e-9:
            refuse("planted-zero control %s: the registered plant %.6g x mean moved sigma/mean by %.3g, "
                   "at or below round-off, while %.6g x mean was visible -- the reader cannot be credited "
                   "with seeing it" % (name, PLANT, seen[PLANT], floor))
        orig, n = _plant_probe_file(p, col, t0, t1, 1.0 * mean_scale, alternate=False)
        got_const = _s1_of(dst, reg)
        open(p, "w").write("".join(orig))
        d_const = abs(got_const - ref)
        if d_const > 0.5 * ref:
            refuse("planted-zero control %s: a CONSTANT offset of one mean moved sigma/mean by %.3g -- a "
                   "working fluctuation reader must be nearly blind to a constant offset; this one is not"
                   % (name, d_const))
        out[name] = dict(status="PASS", plant_fraction=PLANT, reader_scale=mean_scale,
                         samples_planted=n, recovered=seen[PLANT],
                         quadrature_prediction=quad,
                         recovered_over_prediction=(seen[PLANT] / quad) if quad > 0 else None,
                         whole_mean_plant_move=seen[1.0],
                         demonstrated_detection_floor_fraction=floor,
                         constant_offset_arm_move=d_const,
                         ladder={("%g" % k): v for k, v in seen.items()})
        print("planted-zero control %-10s PASS: alternating plant %.6g x mean over %d samples moved "
              "sigma/mean by %.6g (quadrature prediction %.6g, ratio %s); a whole-mean plant moved it "
              "%.4g; MEASURED floor %.1g x mean; CONSTANT offset of one mean moved it %.3g (near-blind, "
              "as a dispersion reader must be)"
              % (name, PLANT, n, seen[PLANT], quad,
                 ("%.3f" % (seen[PLANT] / quad)) if quad > 0 else "n/a", seen[1.0], floor, d_const))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _s1_of(case_dir, reg):
    t, v, why = read_probe_series(case_dir, reg["s1_station_z_m"])
    if t is None:
        refuse("S1 reader: %s" % why)
    st = window_stats(t, v, reg["window_s"][0], reg["window_s"][1])
    return st["rel_sd"]


# ------------------------------------------------------------- the gate
def apply_gate(value, lo, hi, gate1_ok, gate1_why):
    """The ONLY function that writes a verdict.  ONE MESH: there is no triple,
    so rule 5 clause (2) has no operand here and NO GCI IS EVER QUOTED.  Clause
    (1) -- a level not converged, not stationary, or not integrated within the
    registered Courant number -- still fires first and still turns every row
    into NOT A RESULT."""
    bv = "PASS" if lo <= value <= hi else "GATE FAIL"
    if not gate1_ok:
        return "NOT A RESULT", bv, "gate (1): " + gate1_why
    return bv, bv, ""


# ---------------------------------------------------------------- the grade
def grade(root, json_out, reg):
    case_dir = os.path.join(root, CASE)
    if not os.path.isfile(os.path.join(root, "DONE.%s" % CASE)):
        refuse("no DONE.%s -- mark_done_t15.py rules and the rung is graded only after it" % CASE)
    meta = case_meta(case_dir)

    # C_OP: operand identity (L-331) -- the physics is READ FROM THE CASE FILES
    tp = open(os.path.join(case_dir, "constant", "transportProperties")).read()
    def dictval(txt, key):
        m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, txt, re.M)
        if not m:
            refuse("C_OP: the case files state no %s" % key)
        return float(m.group(1))
    nu, beta, tref = dictval(tp, "nu"), dictval(tp, "beta"), dictval(tp, "TRef")
    b0, w0, gp0 = float(meta["b0"]), float(meta["w0"]), float(meta["gprime0"])
    F0_case = math.pi * b0 ** 2 * w0 * gp0
    if abs(F0_case - float(meta["F0"])) / F0_case > 1e-9:
        refuse("C_OP: F0 recomputed from the case's own b0/w0/g'0 is %.12g, CASE.txt states %s"
               % (F0_case, meta["F0"]))
    for k, want in (("nu", reg["physics"]["nu"]), ("beta", reg["physics"]["beta"]), ("TRef", reg["physics"]["TRef"])):
        got = {"nu": nu, "beta": beta, "TRef": tref}[k]
        if abs(got - want) > 1e-12 * max(1.0, abs(want)):
            refuse("C_OP: the case states %s = %.12g, the registration %.12g" % (k, got, want))
    print("C_OP operand identity: nu, beta, TRef, b0, w0, g'0 READ FROM THE CASE; F0 recomputed %.12g "
          "matches CASE.txt to %.2e" % (F0_case, abs(F0_case - float(meta["F0"])) / F0_case))

    # C_REF: the referent, verified before any comparison
    m, fails = MTT.verify(F0_case, reg["physics"]["alpha_nominal"], b0, w0, gp0)
    if fails:
        refuse("C_REF: the MTT referent failed route B: %s" % "; ".join(fails))

    t_end = latest_time(case_dir)
    if t_end is None:
        refuse("%s has no time directory beyond 0" % CASE)

    # measured geometry, written by OpenFOAM (T8 GROUND 2)
    cx = read_scalar(os.path.join(case_dir, "0", "Cx"))
    cz = read_scalar(os.path.join(case_dir, "0", "Cz"))
    vol = read_scalar(os.path.join(case_dir, "0", "V"))
    for nm, a in (("Cx", cx), ("Cz", cz), ("V", vol)):
        if not isinstance(a, list):
            refuse("0/%s is missing or not a nonuniform list -- the MEASURED geometry is the whole point "
                   "(T8 GROUND 2); a nominal value is not substituted" % nm)
    nz, nr = int(meta["nz"]), sum(int(x) for x in meta["nr_blocks"].split("/"))
    if not (len(cx) == len(cz) == len(vol) == nz * nr):
        refuse("0/Cx,0/Cz,0/V hold %d/%d/%d values; the registered mesh has %d cells"
               % (len(cx), len(cz), len(vol), nz * nr))
    planes = build_planes(cx, cz, nz, nr)
    r1, r2 = cx[planes[0][1][0]], cx[planes[0][1][1]]
    dz = planes[1][0] - planes[0][0]
    v_total = sum(vol)
    scale = math.pi * float(meta["R_domain"]) ** 2 * float(meta["H_domain"]) / v_total
    scale_nominal = 2.0 * math.pi / math.sin(math.radians(2.0 * float(meta["wedge_half_angle_deg"])))
    print("MEASURED geometry (0/Cx, 0/Cz, 0/V written by OpenFOAM): r1 = %.12g m, r2 = %.12g m, "
          "r2/r1 = %.9f PRINTED AND ASSERTED NOWHERE (T8 GROUND 2); dz = %.9g m; wedge->annulus SCALE "
          "%.6f measured from the mesh's own volume (flat-sided nominal 2pi/sin(5deg) = %.6f, relative "
          "difference %.3e, REPORTED)" % (r1, r2, r2 / r1, dz, scale, scale_nominal,
                                          abs(scale - scale_nominal) / scale))

    uz = read_vector_z(os.path.join(case_dir, str(t_end), "UMean"))
    tm = read_scalar(os.path.join(case_dir, str(t_end), "TMean"))
    if not isinstance(uz, list) or not isinstance(tm, list):
        refuse("UMean/TMean at %s could not be read as nonuniform fields -- the time-averaged field is the "
               "graded operand and a missing number is not a zero" % t_end)
    if len(uz) != len(cx) or len(tm) != len(cx):
        refuse("UMean/TMean hold %d/%d values against %d cells" % (len(uz), len(tm), len(cx)))

    # gate (1) controls
    co, why = courant_and_bounding(case_dir, reg["deltaT_s"], reg["window_s"][0])
    if co is None:
        refuse("C_CO: %s" % why)
    t_series, v_series, why = read_probe_series(case_dir, reg["s1_station_z_m"])
    if t_series is None:
        refuse("S1: %s" % why)
    st_w = window_stats(t_series, v_series, reg["window_s"][0], reg["window_s"][1])
    tT, vT, whyT = read_probe_series(case_dir, reg["s1_station_z_m"], comp="T")
    st_T = window_stats(tT, vT, reg["window_s"][0], reg["window_s"][1]) if tT else None

    co_ok = co["max_window"] is not None and co["max_window"] <= reg["controls"]["C_CO"]["max_window"]
    stat_ok = st_w["drift_frac"] <= reg["controls"]["C_STAT"]["max_drift_frac"]
    gate1_ok = co_ok and stat_ok and co["has_End"]
    gate1_why = "; ".join(
        ([] if co["has_End"] else ["log.solve has no End line"]) +
        ([] if co_ok else ["C_CO: max Courant in the window %.4f > %.2f"
                           % (co["max_window"] if co["max_window"] is not None else float("nan"),
                              reg["controls"]["C_CO"]["max_window"])]) +
        ([] if stat_ok else ["C_STAT: the window mean drifts by %.4f of itself > %.3f -- the run is not "
                             "statistically stationary over the registered window and no statistic taken "
                             "on it is a property of the run (T8 section 0)"
                             % (st_w["drift_frac"], reg["controls"]["C_STAT"]["max_drift_frac"])]))
    print("C_CO   max Courant: whole run %.4f (REPORTED), window [%g, %g] %.4f (gate, floor %.2f) -> %s"
          % (co["max_all"], reg["window_s"][0], reg["window_s"][1],
             co["max_window"] if co["max_window"] is not None else float("nan"),
             reg["controls"]["C_CO"]["max_window"], "ok" if co_ok else "FAILED"))
    print("C_STAT window drift %.5f of the mean (floor %.3f), %d samples over [%g, %g] -> %s"
          % (st_w["drift_frac"], reg["controls"]["C_STAT"]["max_drift_frac"], st_w["n"],
             st_w["t0"], st_w["t1"], "ok" if stat_ok else "FAILED"))
    print("REPORTED epsilon/k bounding: %d lines over %d steps = %.5f per step"
          % (co["n_bounding_lines"], co["n_steps"], co["bounding_per_step"] or 0.0))

    # ---- the readers the graded rows are built from
    zs = [0.1 * i for i in range(20, 51)]        # z/D = 10.0 .. 25.0, 31 stations at 0.5 D
    prof_w = axis_profile(uz, planes, cx, "parab")
    prof_t = axis_profile(tm, planes, cx, "parab")
    prof_w_lin = axis_profile(uz, planes, cx, "lin")
    w_st = interp_station(prof_w, zs)
    t_st = [v - tref for v in interp_station(prof_t, zs)]
    w_st_lin = interp_station(prof_w_lin, zs)
    Q, M, RE, NC = plume_fluxes(uz, vol, planes, scale, dz)
    b_st = interp_station(tophat_radius(Q, M), zs)
    q_st = interp_station(Q, zs)

    fb = MTT.fit_radius(zs, b_st)
    z0 = fb["z0"]
    fw, whyw = MTT.fit_exponent(zs, w_st, z0)
    ft, whyt = MTT.fit_exponent(zs, t_st, z0)
    fq, whyq = MTT.fit_exponent(zs, q_st, z0)
    if fw is None or ft is None:
        refuse("the exponent fit refused its own operand: %s %s" % (whyw, whyt))
    print("virtual origin z0 = %+.6f m from the b(z) x-intercept (T8 section 12 S4's registered route; the "
          "MTT closed form puts it at %+.6f m for alpha = %.3g) -- REPORTED, and the exponents refitted at "
          "z0 = 0 are reported below" % (z0, m.z0, reg["physics"]["alpha_nominal"]))

    # planted-zero control, per reader, sized to the reader
    i1, i2 = planes[0][1][0], planes[0][1][1]
    jz = min(range(len(planes)), key=lambda j: abs(planes[j][0] - reg["s1_station_z_m"]))
    k1, k2 = planes[jz][1][0], planes[jz][1][1]
    run_idx = planes[jz][1][:max(NC[jz], 1)]

    def rd_w_axis(d):
        u = read_vector_z(os.path.join(d, str(t_end), "UMean"))
        return axis_extrapolate(u[k1], u[k2], cx[k1], cx[k2])

    def rd_b(d):
        u = read_vector_z(os.path.join(d, str(t_end), "UMean"))
        q = m2 = 0.0
        for i in planes[jz][1]:
            if u[i] <= 0.0:
                break
            q += u[i] * vol[i]
            m2 += u[i] * u[i] * vol[i]
        return (scale * q / dz) / math.sqrt(math.pi * scale * m2 / dz) if m2 > 0 else 0.0

    def rd_t_axis(d):
        tt = read_scalar(os.path.join(d, str(t_end), "TMean"))
        return axis_extrapolate(tt[k1], tt[k2], cx[k1], cx[k2])

    probe_sub = sorted(os.listdir(os.path.join(case_dir, "postProcessing", "axisProbes")))[0]
    pcol = None
    for ln in open(os.path.join(case_dir, "postProcessing", "axisProbes", probe_sub, "U")):
        mm = re.match(r"#\s*Probe\s+(\d+)\s+\(([^)]*)\)", ln)
        if mm and abs(float(mm.group(2).split()[2]) - reg["s1_station_z_m"]) < 1e-9:
            pcol = int(mm.group(1))
    if pcol is None:
        refuse("the S1 probe column could not be located from the probe file's own header")
    pz = planted_zero_control(
        case_dir, t_end, reg,
        (("w_axis(POINT)", os.path.join(str(t_end), "UMean"), rd_w_axis, [k1, k2]),
         ("T_axis(POINT)", os.path.join(str(t_end), "TMean"), rd_t_axis, [k1, k2]),
         ("b_th(INTEGRATING)", os.path.join(str(t_end), "UMean"), rd_b, list(run_idx))),
        ("S1(FLUCTUATION)", os.path.join("postProcessing", "axisProbes", probe_sub, "U"),
         pcol, reg["window_s"][0], reg["window_s"][1]))

    # ------------------------------------------------------------- the rows
    R = reg["graded_rows"]
    rows = []
    for rid, value in (("S1", st_w["rel_sd"]),
                       ("V1", fw["exponent"]),
                       ("V2", ft["exponent"]),
                       ("V3", fb["slope"])):
        lo, hi = R[rid]["band"]
        verdict, bv, note = apply_gate(value, lo, hi, gate1_ok, gate1_why)
        rows.append(dict(row=rid, quantity=R[rid]["quantity"], reference=R[rid].get("reference"),
                         band=[lo, hi], value=value, band_verdict=bv, verdict=verdict, note=note,
                         mesh_levels=1, triple="NONE -- SINGLE MESH, NO GRID-CONVERGENCE EVIDENCE",
                         gci_pct=None, richardson=None,
                         capability_ceiling="CAN DO, CAVEATS (single mesh)"))
        print("%-3s %-46s value=%+.8g band=[%+.6g, %+.6g] -> %s%s  [SINGLE MESH, NO TRIPLE, NO GCI]"
              % (rid, R[rid]["quantity"][:46], value, lo, hi, verdict, (" [" + note + "]") if note else ""))

    reported = dict(
        S2_persistence=st_w["persistence"], S1_sigma=st_w["sd"], S1_mean=st_w["mean"],
        S1_n_samples=st_w["n"],
        S3_T_rel_sd=(st_T["rel_sd"] if st_T else None), S3_T_persistence=(st_T["persistence"] if st_T else None),
        n_Q=fq["exponent"] if fq else None, n_Q_r2=fq["r2"] if fq else None,
        alpha_from_slope=fb["alpha"], b_fit_r2=fb["r2"], z0_m=z0, z0_closed_form_m=m.z0,
        V1_r2=fw["r2"], V2_r2=ft["r2"],
        exponents_at_z0_zero=dict(
            n_w=(MTT.fit_exponent(zs, w_st, 0.0)[0] or {}).get("exponent"),
            n_T=(MTT.fit_exponent(zs, t_st, 0.0)[0] or {}).get("exponent")),
        axis_extrapolation_sensitivity_rel=[(a - b) / a if a else None for a, b in zip(w_st, w_st_lin)][:3],
        r1_m=r1, r2_m=r2, r2_over_r1_MEASURED_ASSERTED_NOWHERE=r2 / r1,
        scale_measured=scale, scale_nominal_flat_wedge=scale_nominal,
        plume_run_cells_at_stations=NC[::64],
        courant=co,
        mtt_closed_form=dict(c_b=m.c_b, c_w=m.c_w, exponents=dict(n_w=MTT.N_W, n_T=MTT.N_T, n_Q=MTT.N_Q)))
    print("REPORTED: S2 persistence %s (registered reading: >= %.2f persistent, < %.2f decaying); "
          "alpha = (5/6) db/dz = %.5f; n_Q %+.5f; b-fit R2 %.6f; V1 R2 %.6f; V2 R2 %.6f"
          % (("%.4f" % st_w["persistence"]) if st_w["persistence"] is not None else "n/a (no dispersion in the first half)",
             reg["controls"]["S2"]["persistent_at_or_above"],
             reg["controls"]["S2"]["persistent_at_or_above"], fb["alpha"],
             fq["exponent"] if fq else float("nan"), fb["r2"], fw["r2"], ft["r2"]))

    out = dict(rung="T15", scope="UNSTEADY axisymmetric turbulent plume (URANS kEpsilon), ONE MESH",
               grid_triple=False,
               single_mesh_disclosure="ONE LEVEL: no Roache triple exists, gci_equal is called on no graded "
                                      "row, no GCI and no Richardson extrapolate is quoted, and no "
                                      "discretisation uncertainty is claimed. The capability ceiling of "
                                      "every row here is CAN DO, CAVEATS.",
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, FS=FS,
                           source="scripts/roache_triple.py (imported; exercised in the selftest, called on "
                                  "no graded row)"),
               endTime=t_end, gate1=dict(ok=gate1_ok, why=gate1_why),
               planted_zero_controls=pz, rows=rows, reported=reported)
    json.dump(out, open(json_out, "w"), indent=2, default=str)
    print("wrote %s" % json_out)
    return EXIT_OK


# ---------------------------------------------------------------- selftest
def selftest():
    import ast
    fails = []
    reg = load_registered()
    print("analyse_t15 selftest:")

    # (i) floors: a registered copy differing from the import is refused
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t15reg_")
    try:
        bad = dict(reg)
        bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        json.dump(bad, open(os.path.join(tmpj, "T15_registered.json"), "w"))
        try:
            load_registered(tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered P_MIN mutated to 0.5 -> REFUSE (the import %g / %g is the one number)"
          % ("ok " if fired else "FAIL", STAGNANT_FLOOR, P_MIN))
    if not fired:
        fails.append("floors")

    # (ii) a registration claiming a grid triple on this one-mesh rung is refused
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t15reg2_")
    try:
        bad = dict(reg)
        bad["grid_triple"] = True
        json.dump(bad, open(os.path.join(tmpj, "T15_registered.json"), "w"))
        try:
            load_registered(tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registration claiming grid_triple = true on a ONE-MESH rung -> REFUSE"
          % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("triple")

    # (iii) the imported Roache machinery is LIVE: the floors classify a ladder
    ok = True
    for label, vals, want in (("p = 2.00", (1.16, 1.04, 1.01), "CONVERGING"),
                              ("p = 0.51 (just above STAGNANT_FLOOR)", None, "CONVERGING"),
                              ("p = 0.49 (just below STAGNANT_FLOOR)", None, "STAGNANT"),
                              ("p = 0.01 (below P_MIN)", None, "DEGENERATE"),
                              ("oscillatory", (1.01, 0.99, 1.005), "OSCILLATORY")):
        if vals is None:
            p = {"p = 0.51 (just above STAGNANT_FLOOR)": 0.51,
                 "p = 0.49 (just below STAGNANT_FLOOR)": 0.49,
                 "p = 0.01 (below P_MIN)": 0.01}[label]
            e = 1e-3
            vals = (1.0 + e * 4 ** p, 1.0 + e * 2 ** p, 1.0 + e)
        tr = gci_equal(vals[0], vals[1], vals[2], 2.0, 2, fs=FS)
        good = (tr["state"] == want)
        ok = ok and good
        print("    [%s] imported gci_equal on %-38s -> %s" % ("ok " if good else "FAIL", label, tr["state"]))
    print("  [%s] the imported floors are LIVE (and are called on NO graded row of this rung)"
          % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("gci-live")

    # (iv) the axis extrapolation is exact on a parabola at the MEASURED radii,
    #      and refuses a non-structural pair
    r1, r2 = 0.0041666666, 0.0097222222      # the wedge centroids of cells 0 and 1
    f0, a = 0.15, 42.0
    v = axis_extrapolate(f0 - a * r1 ** 2, f0 - a * r2 ** 2, r1, r2)
    ok = abs(v - f0) < 1e-14
    print("  [%s] axis extrapolation exact on f0 - a r^2 at the measured radii: %.15f vs %.15f"
          % ("ok " if ok else "FAIL", v, f0))
    if not ok:
        fails.append("axis")
    fired = False
    try:
        axis_extrapolate(1.0, 1.0, 0.01, 0.005)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] axis extrapolation on radii that are not r2 > r1 > 0 -> REFUSE (the ONLY geometric fact "
          "this file asserts)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("axis-guard")

    # (v) the whole grade on a FORGED case built from the analytic plume
    code, res = _run_forged(reg)
    rr = {r["row"]: r for r in res["rows"]} if res else {}
    ok = (code == 0 and rr and rr["V1"]["verdict"] == "PASS" and rr["V2"]["verdict"] == "PASS"
          and rr["V3"]["verdict"] == "PASS" and rr["S1"]["verdict"] == "PASS"
          and all(res["planted_zero_controls"][k]["status"] == "PASS" for k in res["planted_zero_controls"])
          and all(r["gci_pct"] is None for r in res["rows"]))
    print("  [%s] VALUE CONTROL: forged analytic plume grades V1 %s V2 %s V3 %s S1 %s; %d planted controls "
          "PASS; NO GCI on any row"
          % ("ok " if ok else "FAIL", rr.get("V1", {}).get("verdict"), rr.get("V2", {}).get("verdict"),
             rr.get("V3", {}).get("verdict"), rr.get("S1", {}).get("verdict"),
             len(res["planted_zero_controls"]) if res else 0))
    if not ok:
        fails.append("value-control")

    code, res = _run_forged(reg, co_max=1.9)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] Courant 1.9 in the window -> gate (1) -> NOT A RESULT on every row" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("courant")

    code, res = _run_forged(reg, drift=0.20)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"])
          and not res["gate1"]["ok"])
    print("  [%s] a window mean drifting 20 percent -> C_STAT -> NOT A RESULT on every row (the T8 failure "
          "this control exists for)" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("stat")

    code, res = _run_forged(reg, noise=0.10)
    ok = (code == 0 and res and {r["row"]: r["verdict"] for r in res["rows"]}["S1"] == "GATE FAIL")
    print("  [%s] a persistent 10 percent fluctuation -> S1 GATE FAIL (the UNSTEADY branch of the "
          "discriminator)" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("s1-fail")

    code, res = _run_forged(reg, alpha=0.20)
    ok = (code == 0 and res and {r["row"]: r["verdict"] for r in res["rows"]}["V3"] == "GATE FAIL"
          and {r["row"]: r["verdict"] for r in res["rows"]}["V1"] == "PASS")
    print("  [%s] entrainment alpha forged to 0.20 -> V3 GATE FAIL while V1 still PASS (T8's P1 shape)"
          % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("v3-fail")

    # (vi) a BLIND reader must be refused by the planted-zero control
    fired = False
    global read_vector_z
    real = read_vector_z
    tmp = tempfile.mkdtemp(prefix="t15blind_")
    try:
        _forge_case(tmp, reg)
        frozen = real(os.path.join(tmp, CASE, "240", "UMean"))
        read_vector_z = lambda p: frozen                       # noqa: E731  ignores the disk
        try:
            grade(tmp, os.path.join(tmp, "gate.json"), reg)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        read_vector_z = real
        shutil.rmtree(tmp, ignore_errors=True)
    print("  [%s] BLIND field reader (ignores the plant) -> the planted-zero control REFUSES"
          % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("blind")

    # (vii) the live tree without a DONE marker refuses
    fired = False
    try:
        grade(HERE, os.path.join(tempfile.gettempdir(), "t15_never.json"), reg)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] live tree, no DONE marker -> exit 2 REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("live")

    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


# ------------------------------------------------------------ the forgery
def _wedge_centroid(ra, rb):
    return (2.0 / 3.0) * (rb * rb + rb * ra + ra * ra) / (rb + ra)


def _forge_case(root, reg, alpha=0.12, noise=0.0, drift=0.0, co_max=0.5, nz=40, seed=7):
    """A forged T15 case: the ANALYTIC MTT plume written as UMean/TMean on a
    reduced-height mesh with the same radial structure, plus a synthetic probe
    series.  The referent module is not consulted by the forgery for anything
    the comparator then re-derives."""
    import random
    rnd = random.Random(seed)
    d = os.path.join(root, CASE)
    b0, w0, gp0 = 0.1, 0.6, 0.6912
    F0 = math.pi * b0 ** 2 * w0 * gp0
    mm = MTT.MTT(F0, alpha, b0)
    edges = []
    for (ra, rb, n) in ((0.0, 0.1, 16), (0.1, 0.4, 48), (0.4, 1.2, 64), (1.2, 2.4, 32)):
        for j in range(n):
            edges.append((ra + (rb - ra) * j / n, ra + (rb - ra) * (j + 1) / n))
    nr = len(edges)
    H, R = 8.0, 2.4
    dz = H / nz
    cxv, czv, vv, uzv, tmv = [], [], [], [], []
    sinq = math.sin(math.radians(5.0))
    for j in range(nz):
        z = (j + 0.5) * dz
        bz = mm.b(z)
        wz = mm.w(z)
        dTz = mm.gprime(z) / (9.81 * (1.0 / 300.0))
        for (ra, rb) in edges:
            rc = _wedge_centroid(ra, rb)
            cxv.append(rc)
            czv.append(z)
            vv.append(0.5 * sinq * (rb * rb - ra * ra) * dz)
            g = math.exp(-(rc / (bz / math.sqrt(2.0))) ** 2)   # b_th = sqrt(2) b_gauss
            uzv.append(wz * (g - 0.5 * math.exp(-(rc / (3 * bz)) ** 2) * 0.0) - 0.002 * (1 - g))
            tmv.append(300.0 + dTz * g)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    os.makedirs(os.path.join(d, "240"), exist_ok=True)

    def wr(p, vals):
        open(p, "w").write("FoamFile{version 2.0; format ascii; class volScalarField; object x;}\n"
                           "dimensions [0 0 0 0 0 0 0];\ninternalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n"
                           "boundaryField{}\n" % (len(vals), "\n".join("%.17g" % v for v in vals)))
    wr(os.path.join(d, "0", "Cx"), cxv)
    wr(os.path.join(d, "0", "Cz"), czv)
    wr(os.path.join(d, "0", "V"), vv)
    wr(os.path.join(d, "240", "TMean"), tmv)
    open(os.path.join(d, "240", "UMean"), "w").write(
        "FoamFile{version 2.0; format ascii; class volVectorField; object UMean;}\n"
        "dimensions [0 1 -1 0 0 0 0];\ninternalField   nonuniform List<vector> \n%d\n(\n%s\n)\n;\n"
        "boundaryField{}\n" % (len(uzv), "\n".join("(0 0 %.17g)" % v for v in uzv)))
    open(os.path.join(d, "0", "T"), "w").write("x\n")
    os.makedirs(os.path.join(d, "constant"), exist_ok=True)
    open(os.path.join(d, "constant", "transportProperties"), "w").write(
        "nu 1.5e-05;\nbeta 0.003333333333;\nTRef 300.000000;\nPr 0.71;\nPrt 0.85;\n")
    open(os.path.join(d, "CASE.txt"), "w").write(
        "case %s\nb0 %.10g m\nw0 %.10g m/s\ngprime0 %.10g m/s2\nF0 %.12g m4/s3\n"
        "nz %d -\nnr_blocks 16/48/64/32 -\nR_domain %.10g m\nH_domain %.10g m\n"
        "wedge_half_angle_deg 2.5 deg\nTRef 300 K\n" % (CASE, b0, w0, gp0, F0, nz, R, H))
    # the log: Courant lines and one ExecutionTime per step
    L = []
    for k in range(200):
        t = 240.0 * (k + 1) / 200.0
        L.append("Courant Number mean: 0.0003 max: %.6f\n" % (co_max if t >= reg["window_s"][0] else 0.4))
        L.append("Time = %.6g\n" % t)
        L.append("ExecutionTime = %g s\n" % (k + 1))
    L.append("End\n")
    open(os.path.join(d, "log.solve"), "w").write("".join(L))
    # the probe series
    pdir = os.path.join(d, "postProcessing", "axisProbes", "0")
    os.makedirs(pdir, exist_ok=True)
    z_s1 = reg["s1_station_z_m"]
    hdr = "".join("# Probe %d (0.0015625 0 %g)\n" % (i, z) for i, z in enumerate((2.0, 3.0, 4.0, 5.0)))
    hdr += "# Time\n"
    rowsU, rowsT = [hdr], [hdr]
    base = mm.w(z_s1)
    for k in range(2400):
        t = 0.1 * (k + 1)
        f = 1.0 + drift * (t - 120.0) / 120.0 + noise * math.sin(2 * math.pi * t / 3.0) + \
            noise * 0.2 * rnd.gauss(0, 1)
        vals = [mm.w(z) * f for z in (2.0, 3.0, 4.0, 5.0)]
        rowsU.append("%.10g\t%s\n" % (t, " ".join("(0 0 %.17g)" % v for v in vals)))
        rowsT.append("%.10g\t%s\n" % (t, " ".join("%.17g" % (300.0 + 5.0 * f) for _ in vals)))
    open(os.path.join(pdir, "U"), "w").write("".join(rowsU))
    open(os.path.join(pdir, "T"), "w").write("".join(rowsT))
    open(os.path.join(root, "DONE.%s" % CASE), "w").write("done\n")
    return d


def _run_forged(reg, **kw):
    tmp = tempfile.mkdtemp(prefix="t15forge_")
    try:
        _forge_case(tmp, reg, **kw)
        out = os.path.join(tmp, "gate.json")
        code = None
        try:
            code = grade(tmp, out, reg)
        except SystemExit as e:
            code = e.code
        res = json.load(open(out)) if os.path.isfile(out) else None
        return code, res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t15.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json, load_registered())


if __name__ == "__main__":
    sys.exit(main())
