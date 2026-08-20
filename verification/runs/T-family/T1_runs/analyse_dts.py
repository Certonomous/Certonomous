#!/usr/bin/env python3
"""
The constant-Ts Reynolds sweep: does the h -> 0 excess scale as 1/Pe^2 ?

REGISTERED IN `DIAGNOSTIC_PREDICTION.md` ("NEXT TEST, REGISTERED BEFORE IT IS
BUILT, 2026-08-20") BEFORE ANY D_Ts CASE WAS BUILT.  The prediction being
tested, verbatim from that file:

  "REGISTERED PREDICTION. If axial conduction is the cause of the constant-Ts
   excess, the h->0 excess scales as 1/Pe^2, so a log-log fit against Pe over
   Re = 25, 50, 100, 200 has slope -2, and Re = 25 (Pe = 17.7, 16x the
   baseline's 1/Pe^2) lands near +1.78 % against the baseline's +0.111 %."

and its falsifying outcomes, also registered in advance, verbatim:

  - slope ~ 0 -- axial conduction is refuted on the constant-Ts arm too, and
    the excess is then unexplained on BOTH arms, which is the end of this line
    of inquiry and gets reported as such.
  - slope far from -2 -- the fitted slope is the finding, and 1/Pe^2 is the
    wrong form.
  - any case whose driving difference at its own station falls below the 10 %
    saturation floor is DISCARDED, not rescued by moving its station again.

  "Each Re needs its own three-level ladder for an h->0 excess, so this is 12
   cases, not 4.  Still diagnostic, still ungraded, and no T1c verdict can
   move on it."

The station moves with Re by analyse_t1c.amended_station (geometric centre of
the window where the driving difference is between 100 % and 10 % of its inlet
value), the rule already committed for T1c.  Nothing here may move a T1c
verdict.  These cases carry no band and cannot pass or fail.

WHAT THIS CARRIES FORWARD FROM analyse_pesweep.py BECAUSE IT WAS PAID FOR:

  * a zero is not believed until a planted perturbation is recovered from it
    (analyse_pesweep.planted_zero_control, which plants by line index and
    reads the plant back from disk; acceptance is PLANT <= got <= real+PLANT).
  * the excess is measured against the SAME reference and the SAME estimator
    on every level: the h -> 0 excess is the Richardson extrapolate of a
    three-level ladder, never a single mesh compared against an extrapolate.

WHAT IT ADDS:

  * a STRICT COMPLETION RULE before any DONE marker is written (STATUS rc=0,
    `End` in log.solve, last time directory == endTime holding T U p_rgh
    alphat phi, one ExecutionTime line per iteration, every field newer than
    0/T).
  * a HEAT-BALANCE CLOSURE from the written fields and the mesh, with the
    face-geometry code validated against the wedge's chord geometry before it
    is trusted, and the inlet conduction flux -- the axial-conduction
    signature at the inlet -- reported explicitly.
  * a Poiseuille check at each fine station (centreline U / U_bulk vs 2.0).

Exit 0 = completed; 2 = refused (a precondition failed and nothing below it
is a result).
"""
import datetime
import json
import math
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCRATCH = ("/tmp/claude-1000/-home-ubuntu/64b13819-ff95-4d4d-a50f-3720bab19084"
           "/scratchpad")
if os.path.isdir(SCRATCH):
    os.environ["TMPDIR"] = SCRATCH
    tempfile.tempdir = SCRATCH
import analyse_t1c as T1C                                # noqa: E402
import analyse_pesweep as PES                            # noqa: E402

NU_TS = 3.6567934
PR = 0.71
PLANT = PES.PLANT
REGISTERED_RE25_PCT = 1.78
REGISTERED_BASELINE_PCT = 0.111
FIELDS = ("T", "U", "p_rgh", "alphat", "phi")
LEVELS = ("c", "m", "f")
LADDERS = [("Re25", 25.0, {l: f"D_Ts_Re25_{l}" for l in LEVELS}),
           ("Re50", 50.0, {l: f"D_Ts_Re50_{l}" for l in LEVELS}),
           ("Re100", 100.0, {l: f"L_Ts_{l}" for l in LEVELS}),
           ("Re200", 200.0, {l: f"D_Ts_Re200_{l}" for l in LEVELS})]
ALL_CASES = [(tag, Re, l, cases[l]) for tag, Re, cases in LADDERS
             for l in LEVELS]
GEOM_TOL = 1e-6


def refuse(msg):
    print(msg)
    sys.exit(2)


def cdir(case):
    return os.path.join(HERE, case)


# ---------------------------------------------------------------------------
# 1. STRICT COMPLETION RULE
# ---------------------------------------------------------------------------
def parse_kv_file(path):
    d = {}
    for tok in open(path).read().split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            d[k] = v
    return d


def completion(case):
    """Every clause of the rule, evaluated and recorded; nothing short-cuts."""
    d = cdir(case)
    rec = dict(case=case, checks={})
    ck = rec["checks"]

    status_p = os.path.join(HERE, f"STATUS.{case}")
    done_p = os.path.join(HERE, f"DONE.{case}")
    if os.path.isfile(status_p):
        st = parse_kv_file(status_p)
        rec["status"] = st
        rec["rc"] = st.get("rc")
        rec["wall_seconds"] = float(st["wall"]) if "wall" in st else None
        rec["checkMesh_rc"] = st.get("checkMesh_rc")
        ck["status_rc0"] = (st.get("rc") == "0")
        rec["status_source"] = f"STATUS.{case}"
    elif os.path.isfile(done_p):
        # the pre-existing Re = 100 ladder has a DONE marker, no STATUS file
        st = dict(line.strip().split("=", 1) for line in open(done_p)
                  if "=" in line)
        rec["status"] = st
        rec["rc"] = st.get("rc")
        rec["wall_seconds"] = (float(st["exec_seconds"])
                               if "exec_seconds" in st else None)
        ck["status_rc0"] = (st.get("rc") == "0")
        rec["status_source"] = f"DONE.{case} (pre-existing; no STATUS file)"
    else:
        ck["status_rc0"] = False
        rec["status_source"] = "NONE"

    log = os.path.join(d, "log.solve")
    if os.path.isfile(log):
        txt = open(log, errors="replace").read()
        ck["log_End"] = re.search(r"^End\s*$", txt, re.M) is not None
        n_exec = len(re.findall(r"^ExecutionTime", txt, re.M))
        rec["n_ExecutionTime"] = n_exec
        last = re.findall(r"^ExecutionTime\s*=\s*([-0-9.eE+]+)\s*s", txt, re.M)
        rec["exec_seconds"] = float(last[-1]) if last else None
        m = re.search(r"^nProcs\s*:\s*(\d+)", txt, re.M)
        rec["nProcs"] = int(m.group(1)) if m else None
        rec["finished_utc"] = datetime.datetime.fromtimestamp(
            os.path.getmtime(log), datetime.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        ck["log_End"] = False
        rec["n_ExecutionTime"] = 0
        rec["exec_seconds"] = None
        rec["nProcs"] = None
        rec["finished_utc"] = None

    cd = os.path.join(d, "system", "controlDict")
    m = (re.search(r"^endTime\s+([-0-9.eE+]+)\s*;", open(cd).read(), re.M)
         if os.path.isfile(cd) else None)
    end_time = float(m.group(1)) if m else None
    rec["endTime"] = end_time

    ts = sorted((x for x in os.listdir(d)
                 if re.fullmatch(r"\d+(\.\d+)?", x) and float(x) != 0.0),
                key=float) if os.path.isdir(d) else []
    rec["time_dirs"] = ts
    last_t = ts[-1] if ts else None
    rec["latest_time"] = last_t
    ck["latest_is_endTime"] = (last_t is not None and end_time is not None
                               and float(last_t) == end_time)
    ck["fields_present"] = bool(last_t) and all(
        os.path.isfile(os.path.join(d, last_t, f)) for f in FIELDS)
    ck["one_ExecutionTime_per_iteration"] = (
        end_time is not None and rec["n_ExecutionTime"] == int(end_time))
    t0 = os.path.join(d, "0", "T")
    if ck["fields_present"] and os.path.isfile(t0):
        m0 = os.path.getmtime(t0)
        ages = {f: os.path.getmtime(os.path.join(d, last_t, f)) - m0
                for f in FIELDS}
        rec["field_age_after_0T_s"] = ages
        ck["fields_newer_than_0T"] = all(v > 0 for v in ages.values())
    else:
        ck["fields_newer_than_0T"] = False

    cm = os.path.join(d, "log.checkMesh")
    m = (re.search(r"^\s*cells:\s+(\d+)", open(cm).read(), re.M)
         if os.path.isfile(cm) else None)
    rec["cells"] = int(m.group(1)) if m else None
    ck["cells_parsed"] = rec["cells"] is not None
    ck["exec_seconds_parsed"] = rec["exec_seconds"] is not None

    rec["complete"] = all(ck.values())
    return rec


def marker_text(rec):
    return (f"case={rec['case']}\nrc={rec['rc']}\ncells={rec['cells']}\n"
            f"exec_seconds={rec['exec_seconds']}\n"
            f"finished_utc={rec['finished_utc']}\n")


# ---------------------------------------------------------------------------
# 6. MESH READER AND FACE GEOMETRY (validated before use)
# ---------------------------------------------------------------------------
def _foam_list_body(path):
    txt = open(path, errors="replace").read()
    m = re.search(r"\n(\d+)\s*\n\(", txt)
    if not m:
        refuse(f"REFUSE: cannot find the list header in {path}")
    return int(m.group(1)), txt[m.end():]


def read_points(path):
    n, body = _foam_list_body(path)
    pts = [tuple(float(x) for x in v.split())
           for v in re.findall(r"\(([^()]*)\)", body)[:n]]
    if len(pts) != n:
        refuse(f"REFUSE: points: expected {n}, parsed {len(pts)} in {path}")
    return pts


def read_faces(path):
    n, body = _foam_list_body(path)
    out = []
    for k, v in re.findall(r"(\d+)\s*\(([^()]*)\)", body)[:n]:
        ids = [int(x) for x in v.split()]
        if len(ids) != int(k):
            refuse(f"REFUSE: face with {k} declared and {len(ids)} listed "
                   f"vertices in {path}")
        out.append(ids)
    if len(out) != n:
        refuse(f"REFUSE: faces: expected {n}, parsed {len(out)} in {path}")
    return out


def read_labels(path):
    n, body = _foam_list_body(path)
    vals = [int(x) for x in re.findall(r"-?\d+", body)[:n]]
    if len(vals) != n:
        refuse(f"REFUSE: labelList: expected {n}, parsed {len(vals)} in {path}")
    return vals


def read_boundary(path):
    txt = open(path, errors="replace").read()
    patches = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", txt):
        blk = m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        if nf and sf:
            patches[m.group(1)] = dict(nFaces=int(nf.group(1)),
                                       startFace=int(sf.group(1)))
    for p in ("inlet", "outlet", "wall"):
        if p not in patches:
            refuse(f"REFUSE: patch {p} absent from {path}")
    return patches


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def face_geometry(pts, face):
    """Area vector and area-weighted centre by triangulation about the
    estimated centroid (the OpenFOAM primitiveMesh construction)."""
    k = len(face)
    c0 = tuple(sum(pts[i][j] for i in face) / k for j in range(3))
    sf = [0.0, 0.0, 0.0]
    cf = [0.0, 0.0, 0.0]
    asum = 0.0
    for i in range(k):
        p1 = pts[face[i]]
        p2 = pts[face[(i + 1) % k]]
        n = _cross(_sub(p2, p1), _sub(c0, p1))
        n = (0.5 * n[0], 0.5 * n[1], 0.5 * n[2])
        a = math.sqrt(_dot(n, n))
        tc = tuple((p1[j] + p2[j] + c0[j]) / 3.0 for j in range(3))
        for j in range(3):
            sf[j] += n[j]
            cf[j] += a * tc[j]
        asum += a
    if asum > 0:
        cf = [v / asum for v in cf]
    else:
        cf = list(c0)
    area = math.sqrt(_dot(sf, sf))
    nrm = tuple(v / area for v in sf) if area > 0 else (0.0, 0.0, 0.0)
    return area, nrm, tuple(cf)


def wedge_geometry(pts):
    """theta (the angle between the wedge planes), R at the vertices, R at
    the wall chord (max y, as analyse_t1c.wall_radius), and L -- all READ
    FROM THE POINTS."""
    half = [math.atan2(abs(p[2]), p[1]) for p in pts
            if p[1] > 1e-12 and abs(p[2]) > 1e-15]
    half.sort()
    h = half[len(half) // 2]
    theta = 2.0 * h
    return dict(theta=theta, half_angle_spread=half[-1] - half[0],
                theta_deg=math.degrees(theta),
                R_vertex=max(math.hypot(p[1], p[2]) for p in pts),
                R_wall=max(p[1] for p in pts),
                x_min=min(p[0] for p in pts), x_max=max(p[0] for p in pts))


def heat_balance(case):
    d = cdir(case)
    t = T1C.latest_time(d)
    pm = os.path.join(d, "constant", "polyMesh")
    pts = read_points(os.path.join(pm, "points"))
    faces = read_faces(os.path.join(pm, "faces"))
    owner = read_labels(os.path.join(pm, "owner"))
    bnd = read_boundary(os.path.join(pm, "boundary"))
    if len(faces) != len(owner):
        refuse(f"REFUSE: {case}: {len(faces)} faces but {len(owner)} owners")

    for f in ("Cx", "Cy", "Cz", "V"):
        if not os.path.isfile(os.path.join(d, t, f)):
            func = "writeCellVolumes" if f == "V" else "writeCellCentres"
            r = T1C.foam(d, f"postProcess -func {func} -time {t} "
                            f"> log.{func} 2>&1")
            if r.returncode != 0:
                refuse(f"REFUSE: {func} failed in {d}")
    Cx = T1C.read_internal(os.path.join(d, t, "Cx"))
    Cy = T1C.read_internal(os.path.join(d, t, "Cy"))
    Cz = T1C.read_internal(os.path.join(d, t, "Cz"))
    V = T1C.read_internal(os.path.join(d, t, "V"))
    T = T1C.read_internal(os.path.join(d, t, "T"))
    U = T1C.read_internal(os.path.join(d, t, "U"), vector=True)
    alphat = T1C.read_internal(os.path.join(d, t, "alphat"))
    n_cells = len(T)
    if not (len(Cx) == len(Cy) == len(Cz) == len(V) == len(U) == n_cells):
        refuse(f"REFUSE: {case}: field sizes disagree")
    if max(owner) >= n_cells:
        refuse(f"REFUSE: {case}: owner label exceeds the cell count")

    nu = float(T1C.case_txt(d, "nu").split()[0])
    Pr = float(T1C.case_txt(d, "Pr").split()[0])
    alpha = nu / Pr
    T_wall = float(T1C.case_txt(d, "T_wall").split()[0])
    T_in = float(T1C.case_txt(d, "T_in").split()[0])

    # ---- geometry validation, before any flux is believed ----------------
    g = wedge_geometry(pts)
    theta, h = g["theta"], g["theta"] / 2.0
    L = g["x_max"] - g["x_min"]
    R_wall = g["R_wall"]
    geo = {}
    areas = {}
    for p in ("inlet", "outlet", "wall"):
        s, n = bnd[p]["startFace"], bnd[p]["nFaces"]
        areas[p] = [face_geometry(pts, faces[f]) for f in range(s, s + n)]
    A_wall = sum(a for a, _, _ in areas["wall"])
    A_in = sum(a for a, _, _ in areas["inlet"])
    A_out = sum(a for a, _, _ in areas["outlet"])
    # the wedge's wall is a flat CHORD strip: width 2 R_wall tan(theta/2),
    # not an arc of length R_wall theta.  The chord comparison is exact.
    A_wall_chord = L * 2.0 * R_wall * math.tan(h)
    A_wall_arc = R_wall * L * theta
    # the inlet is the triangle apex-to-chord: R_wall^2 tan(theta/2), not the
    # sector R_wall^2 theta / 2.
    A_in_chord = R_wall ** 2 * math.tan(h)
    A_in_sector = R_wall ** 2 * theta / 2.0
    geo.update(
        theta_rad=theta, theta_deg=g["theta_deg"],
        half_angle_spread_rad=g["half_angle_spread"],
        R_vertex=g["R_vertex"], R_wall=R_wall, L=L,
        n_wall_faces=len(areas["wall"]), n_inlet_faces=len(areas["inlet"]),
        n_outlet_faces=len(areas["outlet"]),
        A_wall=A_wall, A_wall_chord_exact=A_wall_chord,
        A_wall_rel_err_vs_chord=(A_wall - A_wall_chord) / A_wall_chord,
        A_wall_arc_nominal=A_wall_arc,
        A_wall_rel_err_vs_arc=(A_wall - A_wall_arc) / A_wall_arc,
        arc_to_chord_expected=math.tan(h) / h - 1.0,
        A_inlet=A_in, A_inlet_chord_exact=A_in_chord,
        A_inlet_rel_err_vs_chord=(A_in - A_in_chord) / A_in_chord,
        A_inlet_sector_nominal=A_in_sector,
        A_inlet_rel_err_vs_sector=(A_in - A_in_sector) / A_in_sector,
        sector_to_chord_expected=math.tan(h) / h - 1.0,
        A_outlet=A_out,
        A_outlet_rel_err_vs_inlet=(A_out - A_in) / A_in,
        wall_normals_max_dev_from_y=max(
            abs(1.0 - nrm[1]) for _, nrm, _ in areas["wall"]),
        inlet_normals_max_dev_from_minus_x=max(
            abs(-1.0 - nrm[0]) for _, nrm, _ in areas["inlet"]),
        outlet_normals_max_dev_from_x=max(
            abs(1.0 - nrm[0]) for _, nrm, _ in areas["outlet"]))
    geo["valid"] = (abs(geo["A_wall_rel_err_vs_chord"]) <= GEOM_TOL and
                    abs(geo["A_inlet_rel_err_vs_chord"]) <= GEOM_TOL and
                    abs(geo["A_outlet_rel_err_vs_inlet"]) <= GEOM_TOL and
                    geo["wall_normals_max_dev_from_y"] <= 1e-9 and
                    geo["inlet_normals_max_dev_from_minus_x"] <= 1e-9 and
                    geo["outlet_normals_max_dev_from_x"] <= 1e-9)

    # ---- fluxes, kinematic units (W per rho cp) ---------------------------
    def cond_flux(patch, T_face):
        s = bnd[patch]["startFace"]
        q = 0.0
        dn_min, dn_max = float("inf"), 0.0
        for k, (a, nrm, cf) in enumerate(areas[patch]):
            o = owner[s + k]
            dn = abs(_dot(_sub(cf, (Cx[o], Cy[o], Cz[o])), nrm))
            dn_min, dn_max = min(dn_min, dn), max(dn_max, dn)
            q += alpha * a * (T_face - T[o]) / dn
        return q, dn_min, dn_max

    Q_wall, dn_w_min, dn_w_max = cond_flux("wall", T_wall)
    Q_in_cond, dn_i_min, dn_i_max = cond_flux("inlet", T_in)

    phi_p = os.path.join(d, t, "phi")
    phi_in = T1C.read_patch(phi_p, "inlet")
    phi_out = T1C.read_patch(phi_p, "outlet")
    if phi_in is None or phi_out is None:
        refuse(f"REFUSE: {case}: cannot read phi on inlet/outlet")
    if len(phi_in) == 1 and bnd["inlet"]["nFaces"] > 1:
        phi_in = phi_in * bnd["inlet"]["nFaces"]
    if len(phi_out) == 1 and bnd["outlet"]["nFaces"] > 1:
        phi_out = phi_out * bnd["outlet"]["nFaces"]
    if (len(phi_in) != bnd["inlet"]["nFaces"] or
            len(phi_out) != bnd["outlet"]["nFaces"]):
        refuse(f"REFUSE: {case}: phi patch lengths {len(phi_in)}/{len(phi_out)}"
               f" do not match nFaces")
    s_out = bnd["outlet"]["startFace"]
    s_in = bnd["inlet"]["startFace"]
    conv_out = sum(phi_out[k] * T[owner[s_out + k]]
                   for k in range(len(phi_out)))
    conv_in = sum(phi_out_k * T_in for phi_out_k in phi_in)
    Q_conv_net = conv_out + conv_in
    mdot = -sum(phi_in)
    mdot_out = sum(phi_out)
    Tb_out_phi = conv_out / mdot_out if mdot_out else float("nan")

    # bulk temperature of the first and last cell columns, measure() style
    xs = sorted(set(round(v, 10) for v in Cx))
    def col(xv):
        return [i for i, v in enumerate(Cx) if round(v, 10) == xv]
    def Tb(idx):
        return (sum(U[i][0] * T[i] * V[i] for i in idx) /
                sum(U[i][0] * V[i] for i in idx))
    Tb_first, Tb_last = Tb(col(xs[0])), Tb(col(xs[-1]))

    closure = (Q_wall + Q_in_cond - Q_conv_net) / Q_wall
    return dict(
        case=case, time=t, n_cells=n_cells, alpha=alpha, nu=nu, Pr=Pr,
        T_wall=T_wall, T_in=T_in, alphat_max=max(abs(v) for v in alphat),
        geometry=geo,
        Q_wall=Q_wall, Q_inlet_cond=Q_in_cond,
        Q_inlet_cond_over_Q_wall=Q_in_cond / Q_wall,
        Q_conv_out=conv_out, Q_conv_in=conv_in, Q_conv_net=Q_conv_net,
        closure_residual=closure,
        mdot=mdot, mdot_out=mdot_out,
        mdot_rel_imbalance=(mdot_out - mdot) / mdot,
        dTb_implied=Q_conv_net / mdot,
        Tb_outlet_phi_weighted=Tb_out_phi,
        Tb_first_column=Tb_first, Tb_last_column=Tb_last,
        dTb_columns=Tb_last - Tb_first,
        Q_from_columns=mdot * (Tb_last - Tb_first),
        Q_columns_vs_conv_net_rel=(mdot * (Tb_last - Tb_first) - Q_conv_net)
                                  / Q_conv_net,
        # the first cell column sits half a cell downstream of the inlet and
        # has already been heated, so mdot (Tb_last - Tb_first) is NOT the
        # whole convective gain; the like-for-like checks are the outlet
        # column against the phi-weighted outlet bulk, and the inlet-face
        # value T_in against the first column.
        Tb_last_minus_Tb_out_phi=Tb_last - Tb_out_phi,
        Tb_first_minus_T_in=Tb_first - T_in,
        Q_absorbed_before_first_centre=mdot * (Tb_first - T_in),
        Q_absorbed_before_first_centre_over_Q_wall=mdot * (Tb_first - T_in)
                                                   / Q_wall,
        dn_wall_min=dn_w_min, dn_wall_max=dn_w_max,
        dn_inlet_min=dn_i_min, dn_inlet_max=dn_i_max,
        x_first_column=xs[0], x_last_column=xs[-1])


# ---------------------------------------------------------------------------
# 7. POISEUILLE CHECK
# ---------------------------------------------------------------------------
def poiseuille(case, station_xD):
    d = cdir(case)
    t = T1C.latest_time(d)
    Cx = T1C.read_internal(os.path.join(d, t, "Cx"))
    Cy = T1C.read_internal(os.path.join(d, t, "Cy"))
    V = T1C.read_internal(os.path.join(d, t, "V"))
    U = T1C.read_internal(os.path.join(d, t, "U"), vector=True)
    R_wall = T1C.wall_radius(d)
    D = 2.0 * R_wall
    xs = sorted(set(round(v, 10) for v in Cx))
    xsel = min(xs, key=lambda v: abs(v - station_xD * D))
    idx = [i for i, v in enumerate(Cx) if round(v, 10) == xsel]
    icl = min(idx, key=lambda i: Cy[i])
    Ub_col = sum(U[i][0] * V[i] for i in idx) / sum(V[i] for i in idx)
    Ub_nom = float(T1C.case_txt(d, "U").split()[0])
    Re = float(T1C.case_txt(d, "Re").split()[0])
    return dict(case=case, sample_xD=xsel / D, U_centreline=U[icl][0],
                r_centreline_cell=Cy[icl], U_bulk_column=Ub_col,
                parabola_at_cell_radius=2.0 * (1.0 - (Cy[icl] / R_wall) ** 2),
                U_bulk_nominal=Ub_nom,
                ratio_column=U[icl][0] / Ub_col,
                ratio_nominal=U[icl][0] / Ub_nom,
                hydro_entry_lengths=(xsel / D) / (0.05 * Re),
                Ub_col_vs_nominal_rel=(Ub_col - Ub_nom) / Ub_nom)


# ---------------------------------------------------------------------------
def main():
    out = {"registered_in": "DIAGNOSTIC_PREDICTION.md, NEXT TEST 2026-08-20",
           "reference_Nu_Ts": NU_TS, "Pr": PR,
           "registered_Re25_pct": REGISTERED_RE25_PCT,
           "registered_baseline_Re100_pct": REGISTERED_BASELINE_PCT,
           "saturation_floor": T1C.SATURATION_FLOOR,
           "refinement_ratio": T1C.R_REFINE, "Fs": T1C.FS,
           "completion": {}, "markers": {}, "convergence": {},
           "measurements": {}, "station_sensitivity": {}, "ladders": {},
           "heat_balance": {}, "poiseuille": {}, "discarded": [],
           "not_a_result": []}

    # ---- 1. completion rule and DONE markers --------------------------------
    print("1. STRICT COMPLETION RULE (all clauses must pass before a DONE "
          "marker is written)")
    bad = []
    for tag, Re, lvl, case in ALL_CASES:
        rec = completion(case)
        out["completion"][case] = rec
        flags = " ".join(f"{k}={'ok' if v else 'FAIL'}"
                         for k, v in rec["checks"].items())
        print(f"  {case:13s} {'COMPLETE' if rec['complete'] else 'INCOMPLETE':10s}"
              f" latest={rec['latest_time']} endTime={rec['endTime']:.0f}"
              f" ExecutionTime lines={rec['n_ExecutionTime']}"
              f" cells={rec['cells']} exec_s={rec['exec_seconds']}"
              f" wall_s={rec['wall_seconds']} nProcs={rec['nProcs']}"
              f" [{rec['status_source']}]")
        print(f"      {flags}")
        if not rec["complete"]:
            bad.append(case)
    if bad:
        refuse("REFUSE: the completion rule failed for " + ", ".join(bad) +
               "; no marker written for them and nothing below is a result")

    for tag, Re, lvl, case in ALL_CASES:
        p = os.path.join(HERE, f"DONE.{case}")
        rec = out["completion"][case]
        if case.startswith("L_Ts_"):
            st = "pre-existing (Re = 100 ladder; not rewritten)"
            if not os.path.isfile(p):
                st = "MISSING"
        else:
            new = marker_text(rec)
            if os.path.isfile(p):
                old = open(p).read()
                if old == new:
                    st = "already present, identical (idempotent)"
                else:
                    print(f"  DONE.{case} exists with DIFFERENT content:\n"
                          f"--- on disk ---\n{old}--- computed ---\n{new}")
                    refuse(f"REFUSE: DONE.{case} disagrees with the rule's "
                           f"result; it is NOT overwritten")
            else:
                open(p, "w").write(new)
                st = "WRITTEN"
        out["markers"][case] = st
        print(f"  DONE.{case:13s} {st}")
    missing = [c for _, _, _, c in ALL_CASES
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(missing))

    # ---- 2. iterative convergence with the planted-zero control -----------
    print("\n2. ITERATIVE CONVERGENCE, each zero controlled by a planted "
          f"{PLANT:.3e} K perturbation (acceptance: PLANT <= control <= "
          "real + PLANT)")
    unconverged = []
    for tag, Re, lvl, case in ALL_CASES:
        c = T1C.iterative_convergence(cdir(case))
        ctl = PES.planted_zero_control(case)
        rec = c["max_change"]
        got = ctl["max_change"]
        want = max(rec, PLANT)
        ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)
        print(f"  {case:13s} max change {rec:.3e} K (relative {c['relative']:.3e},"
              f" range {c['field_range']:.4f} K, between {c['between']})"
              f"  [{c['state']}]   planted control returns {got:.6e} "
              f"(expected max(real, plant) = {want:.6e}: "
              f"{'RECOVERED' if ok else 'BROKEN READER'})")
        out["convergence"][case] = dict(c, control_max_change=got,
                                        control_expected=want,
                                        control_ok=ok)
        if not ok:
            refuse("REFUSE: the convergence reader failed its planted control")
        if c["state"] != "CONVERGED":
            unconverged.append((case, rec))
    if unconverged:
        print("  NOT ITERATIVELY CONVERGED (kept, reported, NOT discarded): " +
              ", ".join(f"{c} ({v:.3e} K)" for c, v in unconverged))
    else:
        print("  all 12 cases CONVERGED")
    out["unconverged"] = [dict(case=c, max_change=v) for c, v in unconverged]

    # ---- 3. Nu at each case's own amended station ---------------------------
    print(f"\n3. Nu AT EACH CASE'S OWN AMENDED STATION "
          f"(analyse_t1c.amended_station(Re, {PR}, {NU_TS}); discard if "
          f"driving fraction < {T1C.SATURATION_FLOOR})")
    print(f"  {'case':13s} {'Re':>5s} {'Pe':>7s} {'station':>8s} {'sample':>8s}"
          f" {'Nu':>10s} {'excess %':>9s} {'drive':>7s} {'T_bulk':>9s}"
          f" {'T_wall':>7s} {'fRe':>8s} {'h_wall':>10s} {'ncol':>4s}")
    discarded_re = {}
    for tag, Re, cases in LADDERS:
        station, lo, hi = T1C.amended_station(Re, PR, NU_TS)
        if station is None:
            refuse(f"REFUSE: no admissible station for Re = {Re}")
        out["ladders"][tag] = dict(Re=Re, Pe=Re * PR, station_xD=station,
                                   window_lo_xD=lo, window_hi_xD=hi,
                                   cases=cases, levels={})
        for lvl in LEVELS:
            case = cases[lvl]
            Re_txt = float(T1C.case_txt(cdir(case), "Re").split()[0])
            if Re_txt != Re:
                refuse(f"REFUSE: {case} CASE.txt says Re = {Re_txt}, ladder "
                       f"says {Re}")
            m = T1C.measure(cdir(case), station)
            m["excess_pct"] = 100.0 * (m["Nu"] - NU_TS) / NU_TS
            m["Re_case_txt"] = Re
            m["Pe"] = Re * PR
            m["station_xD_requested"] = station
            m["discarded"] = m["driving_fraction"] < T1C.SATURATION_FLOOR
            out["measurements"][case] = m
            out["ladders"][tag]["levels"][lvl] = m
            flag = ""
            if m["discarded"]:
                flag = (f"   DISCARDED (driving fraction "
                        f"{m['driving_fraction']:.4f} < "
                        f"{T1C.SATURATION_FLOOR}; NOT rescued)")
                out["discarded"].append(dict(
                    case=case, ladder=tag, driving_fraction=m["driving_fraction"],
                    reason="driving difference at its own station below the "
                           "10 % saturation floor (registered clause)"))
                discarded_re.setdefault(tag, []).append(case)
            print(f"  {case:13s} {Re:5.0f} {Re*PR:7.2f} {station:8.3f} "
                  f"{m['sample_xD']:8.4f} {m['Nu']:10.6f} {m['excess_pct']:+9.4f}"
                  f" {m['driving_fraction']:7.4f} {m['T_bulk']:9.4f} "
                  f"{m['T_wall']:7.1f} {m['fRe']:8.4f} {m['near_wall_h']:10.3e}"
                  f" {m['n_cells_station']:4d}{flag}")
        xd = [out["ladders"][tag]["levels"][l]["sample_xD"] for l in LEVELS]
        print(f"      {tag}: actual nearest cell-centre x/D per level c/m/f = "
              f"{xd[0]:.4f} / {xd[1]:.4f} / {xd[2]:.4f} "
              f"(requested {station:.4f}; spread {max(xd)-min(xd):.4f} D)")

    print("\n  STATION SENSITIVITY on the fine level (REPORTED ONLY; never "
          "used to discard): Nu at lo and hi of the admissible window")
    print(f"  {'case':13s} {'lo x/D':>8s} {'Nu_lo':>10s} {'exc_lo %':>9s}"
          f" {'hi x/D':>8s} {'Nu_hi':>10s} {'exc_hi %':>9s} {'drive_hi':>8s}"
          f" {'spread pp':>9s} {'fine exc %':>10s} {'spread/|exc|':>12s}")
    for tag, Re, cases in LADDERS:
        L = out["ladders"][tag]
        case = cases["f"]
        mlo = T1C.measure(cdir(case), L["window_lo_xD"])
        mhi = T1C.measure(cdir(case), L["window_hi_xD"])
        elo = 100.0 * (mlo["Nu"] - NU_TS) / NU_TS
        ehi = 100.0 * (mhi["Nu"] - NU_TS) / NU_TS
        ef = L["levels"]["f"]["excess_pct"]
        spread = abs(ehi - elo)
        out["station_sensitivity"][tag] = dict(
            case=case, lo_xD_requested=L["window_lo_xD"],
            lo_xD_sampled=mlo["sample_xD"], Nu_lo=mlo["Nu"], excess_lo_pct=elo,
            driving_fraction_lo=mlo["driving_fraction"],
            hi_xD_requested=L["window_hi_xD"],
            hi_xD_sampled=mhi["sample_xD"], Nu_hi=mhi["Nu"], excess_hi_pct=ehi,
            driving_fraction_hi=mhi["driving_fraction"],
            spread_pp=spread, fine_excess_at_station_pct=ef,
            spread_over_abs_fine_excess=(spread / abs(ef) if ef else
                                         float("nan")))
        print(f"  {case:13s} {mlo['sample_xD']:8.4f} {mlo['Nu']:10.6f} "
              f"{elo:+9.4f} {mhi['sample_xD']:8.4f} {mhi['Nu']:10.6f} "
              f"{ehi:+9.4f} {mhi['driving_fraction']:8.4f} {spread:9.4f} "
              f"{ef:+10.4f} {spread/abs(ef) if ef else float('nan'):12.3f}")

    # ---- 4. GCI per Re triple ----------------------------------------------
    print("\n4. GCI PER Re TRIPLE (analyse_t1c.gci; r = 1.6, Fs = 1.25); "
          f"h -> 0 excess % = 100 (richardson - {NU_TS}) / {NU_TS}")
    for tag, Re, cases in LADDERS:
        L = out["ladders"][tag]
        nus = [L["levels"][l]["Nu"] for l in LEVELS]
        conv = T1C.gci(*nus)
        L["gci"] = conv
        exc = {l: L["levels"][l]["excess_pct"] for l in LEVELS}
        L["excess_pct_per_level"] = exc
        unconv = [l for l in LEVELS
                  if out["convergence"][cases[l]]["state"] != "CONVERGED"]
        L["unconverged_levels"] = unconv
        disc = discarded_re.get(tag, [])
        print(f"  {tag:6s} Re={Re:4.0f} Pe={Re*PR:6.2f}  Nu c/m/f = "
              f"{nus[0]:.6f} / {nus[1]:.6f} / {nus[2]:.6f}   per-level excess "
              f"% c/m/f = {exc['c']:+.4f} / {exc['m']:+.4f} / {exc['f']:+.4f}")
        print(f"         gci: {conv}")
        why = []
        if disc:
            why.append(f"level(s) {', '.join(disc)} DISCARDED at the "
                       "saturation floor, which voids the h -> 0 excess")
        if conv["state"] != "CONVERGING":
            why.append(f"grid triple is {conv['state']}; no Richardson "
                       "extrapolate exists")
        if unconv:
            why.append(f"level(s) {', '.join(unconv)} not iteratively "
                       "converged (reported; the extrapolate is still computed "
                       "but flagged)")
        if conv["state"] == "CONVERGING" and not disc:
            L["h0_excess_pct"] = 100.0 * (conv["richardson"] - NU_TS) / NU_TS
            L["usable_for_fit"] = True
            print(f"         order p = {conv['order']:.4f}, GCI = "
                  f"{conv['GCI_pct']:.4f} %, richardson Nu = "
                  f"{conv['richardson']:.6f}, h -> 0 excess = "
                  f"{L['h0_excess_pct']:+.4f} %"
                  + ("   [FLAG: " + "; ".join(why) + "]" if why else ""))
        else:
            L["h0_excess_pct"] = None
            L["usable_for_fit"] = False
            L["why_not_a_result"] = "; ".join(why)
            out["not_a_result"].append(dict(ladder=tag, why=L["why_not_a_result"]))
            print(f"         NOT A RESULT for the fit: {L['why_not_a_result']}")
        ss = out["station_sensitivity"][tag]
        # THE SAMPLE STATION DIFFERS BY LEVEL (nearest cell centre), and the
        # excess varies along x.  Estimate, from the fine-level lo/hi pair,
        # how much of each level's excess is station offset.  REPORTED ONLY;
        # nothing is corrected by it.
        dexdx = ((ss["excess_hi_pct"] - ss["excess_lo_pct"]) /
                 (ss["hi_xD_sampled"] - ss["lo_xD_sampled"]))
        shift = {l: dexdx * (L["levels"][l]["sample_xD"] - L["station_xD"])
                 for l in LEVELS}
        L["station_mismatch"] = dict(
            d_excess_pct_per_D_from_fine_lo_hi=dexdx,
            sample_xD_minus_station={l: L["levels"][l]["sample_xD"]
                                     - L["station_xD"] for l in LEVELS},
            estimated_excess_shift_pp=shift,
            e32_measured_pp=exc["c"] - exc["m"],
            e21_measured_pp=exc["m"] - exc["f"],
            e32_station_part_pp=shift["c"] - shift["m"],
            e21_station_part_pp=shift["m"] - shift["f"])
        print(f"         station mismatch (REPORTED ONLY): d(excess)/d(x/D) ~ "
              f"{dexdx:+.4f} pp/D from the fine lo/hi pair; sample - station "
              f"c/m/f = {L['station_mismatch']['sample_xD_minus_station']['c']:+.4f}"
              f" / {L['station_mismatch']['sample_xD_minus_station']['m']:+.4f}"
              f" / {L['station_mismatch']['sample_xD_minus_station']['f']:+.4f} D"
              f" -> estimated excess shift c/m/f = {shift['c']:+.4f} / "
              f"{shift['m']:+.4f} / {shift['f']:+.4f} pp; measured e32 = "
              f"{exc['c']-exc['m']:+.4f} pp (station part {shift['c']-shift['m']:+.4f}),"
              f" e21 = {exc['m']-exc['f']:+.4f} pp (station part "
              f"{shift['m']-shift['f']:+.4f})")
        if L["h0_excess_pct"] is not None:
            print(f"         station-sensitivity spread {ss['spread_pp']:.4f} pp "
                  f"against |h -> 0 excess| {abs(L['h0_excess_pct']):.4f} pp "
                  f"(ratio {ss['spread_pp']/abs(L['h0_excess_pct']) if L['h0_excess_pct'] else float('nan'):.3f})")
        # f.Re triple, for the record
        fres = [L["levels"][l]["fRe"] for l in LEVELS]
        L["fRe_gci"] = T1C.gci(*fres)
        print(f"         f.Re c/m/f = {fres[0]:.4f} / {fres[1]:.4f} / "
              f"{fres[2]:.4f}  (64 exact)  {L['fRe_gci']}")

    # ---- 5. log-log fits ----------------------------------------------------
    print("\n5. LOG-LOG FIT of h -> 0 excess against Pe = Re x 0.71")
    usable = [(L["Pe"], L["h0_excess_pct"], tag) for tag, L in out["ladders"].items()
              if L["usable_for_fit"]]
    pos = [(p, e, t) for p, e, t in usable if e > 0]
    nonpos = [(p, e, t) for p, e, t in usable if e <= 0]
    print(f"  {len(usable)} of 4 Re points have an h -> 0 excess; "
          f"{len(pos)} of those are POSITIVE (a log-log fit needs one)"
          + (";  non-positive: " + ", ".join(f"{t} ({e:+.4f} %)"
                                            for _, e, t in nonpos)
             if nonpos else ""))
    for p, e, t in pos:
        print(f"    {t:6s} Pe = {p:7.2f}  h -> 0 excess = {e:+.4f} %")
    out["fit_h0"] = dict(points=[dict(ladder=t, Pe=p, excess_pct=e)
                                 for p, e, t in pos])
    if len(pos) < 3:
        print("  NOT A RESULT: fewer than three positive h -> 0 points; a slope "
              "on this is not a measurement")
        out["fit_h0"]["verdict"] = "NOT A RESULT (fewer than 3 usable points)"
    else:
        slope, inter, r2, se = PES.fit_loglog([p for p, _, _ in pos],
                                              [e for _, e, _ in pos])
        z = (slope + 2.0) / se if se and not math.isnan(se) else float("nan")
        print(f"  slope    = {slope:+.4f}  +/- {se:.4f} (standard error)")
        print(f"  intercept= {inter:+.4f}  (ln excess% at Pe = 1)")
        print(f"  R^2      = {r2:.5f}")
        print(f"  registered slope for axial conduction, O(1/Pe^2) = -2")
        print(f"  the fit is {abs(z):.2f} standard errors from -2")
        out["fit_h0"].update(n=len(pos), slope=slope, intercept=inter, r2=r2,
                             slope_se=se, sigma_from_minus2=z)
    L25 = out["ladders"]["Re25"]
    if L25["h0_excess_pct"] is not None:
        print(f"  the Re = 25 h -> 0 excess, registered near {REGISTERED_RE25_PCT:+.2f} %"
              f" (baseline Re = 100 registered at {REGISTERED_BASELINE_PCT:+.3f} %):"
              f" measured {L25['h0_excess_pct']:+.4f} %"
              f"   (Re = 100 h -> 0 excess here: "
              f"{out['ladders']['Re100']['h0_excess_pct']}"
              + (f" -> ratio Re25/Re100 = "
                 f"{L25['h0_excess_pct']/out['ladders']['Re100']['h0_excess_pct']:.3f}"
                 f" against 16 registered"
                 if out['ladders']['Re100']['h0_excess_pct'] else "") + ")")
        out["Re25_h0_measured_pct"] = L25["h0_excess_pct"]
    else:
        print(f"  the Re = 25 point has no h -> 0 excess ({L25.get('why_not_a_result')});"
              f" registered {REGISTERED_RE25_PCT:+.2f} % cannot be compared")
        out["Re25_h0_measured_pct"] = None

    print("\n  SECONDARY LINE: log-log fit of the FINE-mesh excess against Pe "
          "(single level, no extrapolation; reported separately)")
    fine = [(L["Pe"], L["levels"]["f"]["excess_pct"], tag)
            for tag, L in out["ladders"].items()
            if not L["levels"]["f"]["discarded"]]
    fpos = [(p, e, t) for p, e, t in fine if e > 0]
    for p, e, t in fine:
        print(f"    {t:6s} Pe = {p:7.2f}  fine excess = {e:+.4f} %"
              + ("" if e > 0 else "   (non-positive, excluded)"))
    out["fit_fine"] = dict(points=[dict(ladder=t, Pe=p, excess_pct=e)
                                   for p, e, t in fpos])
    if len(fpos) < 3:
        print("  NOT A RESULT: fewer than three positive fine points")
        out["fit_fine"]["verdict"] = "NOT A RESULT (fewer than 3 usable points)"
    else:
        slope, inter, r2, se = PES.fit_loglog([p for p, _, _ in fpos],
                                              [e for _, e, _ in fpos])
        z = (slope + 2.0) / se if se and not math.isnan(se) else float("nan")
        print(f"  slope    = {slope:+.4f}  +/- {se:.4f} (standard error)")
        print(f"  R^2      = {r2:.5f}")
        print(f"  the fine-mesh fit is {abs(z):.2f} standard errors from -2")
        out["fit_fine"].update(n=len(fpos), slope=slope, intercept=inter,
                               r2=r2, slope_se=se, sigma_from_minus2=z)

    # ---- 6. heat-balance closure -------------------------------------------
    print("\n6. HEAT-BALANCE CLOSURE from the written fields and the mesh "
          "(kinematic units, W per rho cp), latest time")
    print("  face-geometry validation (theta read from the points; the wedge "
          "wall is a flat CHORD strip, so the exact comparisons are "
          "L 2 R_wall tan(theta/2) and R_wall^2 tan(theta/2); the arc/sector "
          "forms R_wall L theta and R_wall^2 theta/2 differ by tan(h)/h - 1)")
    for tag, Re, lvl, case in ALL_CASES:
        hb = heat_balance(case)
        out["heat_balance"][case] = hb
        g = hb["geometry"]
        print(f"  {case:13s} theta = {g['theta_deg']:.6f} deg (spread "
              f"{g['half_angle_spread_rad']:.1e} rad)  R_vertex = "
              f"{g['R_vertex']:.8f}  R_wall = {g['R_wall']:.8f}  L = {g['L']:.6f}"
              f"  faces wall/in/out = {g['n_wall_faces']}/{g['n_inlet_faces']}/"
              f"{g['n_outlet_faces']}")
        print(f"      A_wall = {g['A_wall']:.10e}  vs chord {g['A_wall_chord_exact']:.10e}"
              f" (rel {g['A_wall_rel_err_vs_chord']:+.2e})  vs arc "
              f"{g['A_wall_arc_nominal']:.10e} (rel {g['A_wall_rel_err_vs_arc']:+.3e};"
              f" tan(h)/h-1 = {g['arc_to_chord_expected']:+.3e})")
        print(f"      A_inlet = {g['A_inlet']:.10e} vs chord triangle "
              f"{g['A_inlet_chord_exact']:.10e} (rel {g['A_inlet_rel_err_vs_chord']:+.2e})"
              f"  vs sector {g['A_inlet_sector_nominal']:.10e} (rel "
              f"{g['A_inlet_rel_err_vs_sector']:+.3e})  A_outlet/A_inlet - 1 = "
              f"{g['A_outlet_rel_err_vs_inlet']:+.2e}  normals dev "
              f"{g['wall_normals_max_dev_from_y']:.1e}/"
              f"{g['inlet_normals_max_dev_from_minus_x']:.1e}/"
              f"{g['outlet_normals_max_dev_from_x']:.1e}"
              f"  -> {'VALID' if g['valid'] else 'INVALID'}")
        if not g["valid"]:
            refuse(f"REFUSE: face geometry for {case} does not reproduce the "
                   f"chord geometry to {GEOM_TOL:.0e}; no flux from it is "
                   "believed")
        print(f"      Q_wall = {hb['Q_wall']:+.6e}  Q_inlet_cond = "
              f"{hb['Q_inlet_cond']:+.6e} ({100*hb['Q_inlet_cond_over_Q_wall']:+.4f} % "
              f"of Q_wall)  Q_conv_out = {hb['Q_conv_out']:+.6e}  Q_conv_in = "
              f"{hb['Q_conv_in']:+.6e}  Q_conv_net = {hb['Q_conv_net']:+.6e}")
        print(f"      closure residual (Q_wall + Q_inlet_cond - Q_conv_net)/Q_wall"
              f" = {hb['closure_residual']:+.3e}   mdot = {hb['mdot']:.6e} "
              f"(out/in - 1 = {hb['mdot_rel_imbalance']:+.2e})  dTb implied = "
              f"{hb['dTb_implied']:.5f} K  Tb_out(phi) = "
              f"{hb['Tb_outlet_phi_weighted']:.5f} K")
        print(f"      columns: Tb_first = {hb['Tb_first_column']:.5f} K at x = "
              f"{hb['x_first_column']:.5f}, Tb_last = {hb['Tb_last_column']:.5f} K"
              f" at x = {hb['x_last_column']:.5f}; mdot dTb_columns = "
              f"{hb['Q_from_columns']:+.6e} vs Q_conv_net (rel "
              f"{hb['Q_columns_vs_conv_net_rel']:+.3e}; the first column is "
              f"already {hb['Tb_first_minus_T_in']:.5f} K above T_in, i.e. "
              f"{100*hb['Q_absorbed_before_first_centre_over_Q_wall']:.2f} % of "
              f"Q_wall is absorbed before the first cell centre); "
              f"Tb_last - Tb_out(phi) = {hb['Tb_last_minus_Tb_out_phi']:+.2e} K"
              f"  alphat max = "
              f"{hb['alphat_max']:.1e}  d_n wall {hb['dn_wall_min']:.3e}.."
              f"{hb['dn_wall_max']:.3e}  d_n inlet {hb['dn_inlet_min']:.3e}.."
              f"{hb['dn_inlet_max']:.3e}")

    # ---- 7. Poiseuille check at each fine station ---------------------------
    print("\n7. POISEUILLE CHECK at each fine case's station: centreline-cell "
          "U_x / U_bulk against 2.0")
    for tag, Re, cases in LADDERS:
        L = out["ladders"][tag]
        pz = poiseuille(cases["f"], L["station_xD"])
        out["poiseuille"][tag] = pz
        print(f"  {cases['f']:13s} Re={Re:4.0f} x/D = {pz['sample_xD']:.4f} = "
              f"{pz['hydro_entry_lengths']:.2f} nominal hydrodynamic entry "
              f"lengths (0.05 Re D): U_cl = {pz['U_centreline']:.6e} at r = "
              f"{pz['r_centreline_cell']:.3e};  U_cl/U_bulk(column) = "
              f"{pz['ratio_column']:.5f}  ({100*(pz['ratio_column']-2)/2:+.3f} %"
              f" from 2.0; the exact parabola at this cell's radius is "
              f"{pz['parabola_at_cell_radius']:.5f});  U_cl/U_nominal = "
              f"{pz['ratio_nominal']:.5f};  "
              f"U_bulk(column)/U_nominal - 1 = {pz['Ub_col_vs_nominal_rel']:+.2e}")

    # ---- per-case record ---------------------------------------------------
    print("\nPER-CASE RECORD")
    print(f"  {'case':13s} {'cells':>6s} {'wall_s':>8s} {'exec_s':>9s} "
          f"{'nProcs':>6s} {'conv':>14s} {'Nu':>10s} {'excess %':>9s} "
          f"{'closure':>10s} {'Qin_cond/Qw':>11s}")
    out["per_case"] = {}
    for tag, Re, lvl, case in ALL_CASES:
        c = out["completion"][case]
        m = out["measurements"][case]
        hb = out["heat_balance"][case]
        cv = out["convergence"][case]
        out["per_case"][case] = dict(
            ladder=tag, level=lvl, Re=Re, cells=c["cells"],
            wall_seconds=c["wall_seconds"], exec_seconds=c["exec_seconds"],
            nProcs=c["nProcs"], convergence_state=cv["state"],
            Nu=m["Nu"], excess_pct=m["excess_pct"], discarded=m["discarded"],
            closure_residual=hb["closure_residual"],
            Q_inlet_cond_over_Q_wall=hb["Q_inlet_cond_over_Q_wall"])
        print(f"  {case:13s} {c['cells']:6d} {c['wall_seconds']:8.1f} "
              f"{c['exec_seconds']:9.2f} {c['nProcs']:6d} {cv['state']:>14s} "
              f"{m['Nu']:10.6f} {m['excess_pct']:+9.4f} "
              f"{hb['closure_residual']:+10.3e} "
              f"{hb['Q_inlet_cond_over_Q_wall']:+11.4e}")

    with open(os.path.join(HERE, "dts.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(f"\nwrote {os.path.join(HERE, 'dts.json')}")
    print("DIAGNOSTIC, NOT GRADED: no band, no pass/fail, no T1c verdict moves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
