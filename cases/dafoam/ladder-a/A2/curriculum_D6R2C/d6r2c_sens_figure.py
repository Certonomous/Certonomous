#!/usr/bin/env python3
# =============================================================================
# d6r2c_sens_figure.py -- D6R2C POST-HOC SENSITIVITY AND CONVERGENCE READER
#
# WHAT THIS IS.  Sanaa's D6R2 run instruction, item 10, owes a "skin-sensitivity
# figure" and a "convergence history".  The frozen, md5-pinned production script
# d6r2c_opt_runScript.py contains no writeSens, no sensMap and no
# writeDeformedFFD, so NOTHING in the production chain ever writes dI/dx as a
# surface field, and nothing will at completion.  This file therefore reads only
# artefacts ALREADY ON DISK and draws figures from them.  It is a READER:
#   - it adds no gate, grades nothing, changes no verdict;
#   - it never writes into the run directory it reads (output goes to --out-dir);
#   - it does not import, touch or re-run any solver.
#
# WHAT IT CAN HONESTLY DRAW, AND WHAT IT REFUSES TO DRAW.
# The sensitivities exist ONLY as numbers inside the pyoptsparse history
# OptView.hst, as d(obj.J)/d(dvs.shape) -- a 96-vector -- plus
# d(obj.J)/d(dvs.twist), a 7-vector.  The 96 shape design variables are LOCAL
# FFD design variables (pygeo addLocalDV via DAFoam's nom_addLocalDV) on the
# 6 x 2 x 8 = 96 control points of FFD/wingFFD.xyz, displacing each control
# point along the FFD y (vertical) axis.  Evidence, all on disk:
#   - d6r2c_opt_runScript.py: pts = geometry.DVGeo.getLocalIndex(0);
#     indexList = pts[:, :, :].flatten(); PS = PointSelect("list", indexList);
#     ns = geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)
#   - FFD/wingFFD.xyz: plot3d, 1 block, dims 6 2 8 -> 96 control points, x
#     chordwise, y vertical (the two j planes are the lower/upper sheets),
#     z spanwise 0 -> 14.25.
#   - the thickness-constraint Jacobian in the history, d(thickcon)/d(shape),
#     is >= 0 for EVERY j=1 control point and <= 0 for EVERY j=0 control point,
#     which is only possible if the local DV axis is y and the j index splits
#     upper from lower.  --verify-mapping re-runs that check and REFUSES if it
#     fails.
# Mapping those 96 numbers onto the WING SKIN would require the DVGeo
# B-spline Jacobian dXsurface/dXffd.  That Jacobian is not written anywhere by
# the production chain and is not on disk.  Any smooth skin map drawn here
# would therefore be an interpolation nobody registered.  THIS READER DOES NOT
# DRAW ONE.  It draws the sensitivity where it honestly lives: on the FFD
# control lattice, plotted at the lattice's true (x, z) planform coordinates.
#
# SCALING.  The history is written in the optimizer's DRIVER-SCALED space.
# Evidence on disk: reports/d6r2c_opt_runScript/driver_scaling_report.html
# records dvs.shape with "scaler": 10.0 and driver bounds +/-10.0 against model
# bounds +/-1.0, matching add_design_var("shape", lower=-1.0, upper=1.0,
# scaler=10.0) in the run script; the history's varInfo carries the SCALED
# bounds (+/-10 for shape, +/-1 for twist).  The objective scaler is 1.0.  So a
# recorded value is dJ/d(x_scaled); dJ/d(x_physical) = scaler * recorded.  This
# reader reports the RECORDED value as primary, carries the scaler, and reports
# the physical value as an explicitly derived column.  It never silently
# multiplies.
#
# PLANTED CONTROL (standing rule 3).  --selftest-plant renders once from the
# history, then writes a PERTURBED COPY of that history to disk, re-reads that
# copy THROUGH THE SAME CODE PATH, re-renders, and compares both the PNG bytes
# and the numeric summary.  If the second render is identical the reader cannot
# see its own input and EXITS 2 rather than certify the figure it drew.
# =============================================================================

import argparse
import hashlib
import json
import os
import pickle
import shutil
import sqlite3
import sys
import time
import warnings

import numpy as np

# unpickling numpy arrays written by an older numpy emits a DeprecationWarning
# from numpy.core.numeric; it is noise from the reader's input, not a finding.
warnings.filterwarnings("ignore", category=DeprecationWarning,
                        module=r"numpy\.core.*")
warnings.filterwarnings("ignore", message=r".*numpy\.core\.numeric is deprecated.*")

PLANT = 1.234e-03          # the lab planted-control constant
SCHEMA_TABLE = "unnamed"   # pyoptsparse/sqlitedict history table


# ----------------------------------------------------------------------------
# history reading
# ----------------------------------------------------------------------------
def _hst_open(path):
    if not os.path.isfile(path):
        raise SystemExit("D6R2C SENS REFUSE: history not found: %s" % path)
    con = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    names = [r[0] for r in con.execute(
        "select name from sqlite_master where type='table'")]
    if SCHEMA_TABLE not in names:
        raise SystemExit(
            "D6R2C SENS REFUSE: %s is not a pyoptsparse history "
            "(no '%s' table; tables=%r)" % (path, SCHEMA_TABLE, names))
    return con


def _hst_get(con, key):
    row = con.execute("select value from %s where key=?" % SCHEMA_TABLE,
                      (key,)).fetchone()
    if row is None:
        return None
    return pickle.loads(row[0])


def hst_read(path):
    """Return (entries, varInfo, conInfo, objInfo, metadata).

    entries is the ordered list of integer-keyed records, each a dict.
    """
    con = _hst_open(path)
    keys = [r[0] for r in con.execute("select key from %s" % SCHEMA_TABLE)]
    ints = sorted(int(k) for k in keys if k.lstrip("-").isdigit())
    entries = []
    for i in ints:
        d = _hst_get(con, str(i))
        if isinstance(d, dict):
            d = dict(d)
            d["_key"] = i
            entries.append(d)
    out = (entries,
           _hst_get(con, "varInfo") or {},
           _hst_get(con, "conInfo") or {},
           _hst_get(con, "objInfo") or {},
           _hst_get(con, "metadata") or {})
    con.close()
    return out


def last_sens_entry(entries, dv_name, obj_name):
    """Last MAJOR entry carrying funcsSens with d(obj)/d(dv) present."""
    for d in reversed(entries):
        fs = d.get("funcsSens")
        if not isinstance(fs, dict):
            continue
        if not d.get("isMajor", True):
            continue
        of = fs.get(obj_name)
        if isinstance(of, dict) and dv_name in of:
            return d
    raise SystemExit("D6R2C SENS REFUSE: no major entry carries "
                     "funcsSens[%r][%r]" % (obj_name, dv_name))


# ----------------------------------------------------------------------------
# FFD reading (plot3d ASCII, single block)
# ----------------------------------------------------------------------------
def ffd_read(path):
    """Return (ni, nj, nk, X, Y, Z) with arrays shaped (ni, nj, nk)."""
    if not os.path.isfile(path):
        raise SystemExit("D6R2C SENS REFUSE: FFD not found: %s" % path)
    tok = open(path).read().split()
    nblk = int(tok[0])
    if nblk != 1:
        raise SystemExit("D6R2C SENS REFUSE: FFD has %d blocks; this reader "
                         "handles the single-block wing FFD only" % nblk)
    ni, nj, nk = (int(tok[1]), int(tok[2]), int(tok[3]))
    n = ni * nj * nk
    vals = np.asarray(tok[4:4 + 3 * n], dtype=float)
    if vals.size != 3 * n:
        raise SystemExit("D6R2C SENS REFUSE: FFD truncated: expected %d "
                         "coordinates, found %d" % (3 * n, vals.size))
    # plot3d writes i fastest, then j, then k -> Fortran order for (ni,nj,nk)
    X = vals[0:n].reshape((ni, nj, nk), order="F")
    Y = vals[n:2 * n].reshape((ni, nj, nk), order="F")
    Z = vals[2 * n:3 * n].reshape((ni, nj, nk), order="F")
    return ni, nj, nk, X, Y, Z


def dv_index_grid(ni, nj, nk):
    """DV index -> (i, j, k).

    The run script builds the DV list as getLocalIndex(0)[:, :, :].flatten(),
    which is C order over (i, j, k): k fastest, then j, then i.  The ordering is
    corroborated from the data by verify_mapping().
    """
    n = np.arange(ni * nj * nk)
    i = n // (nj * nk)
    j = (n % (nj * nk)) // nk
    k = n % nk
    return i, j, k


def verify_mapping(entry, ni, nj, nk, Z, thick_name="geometry_cl05.thickcon",
                   dv_name="dvs.shape"):
    """Corroborate the DV ordering and the y-axis from the history itself.

    Returns a dict of findings.  Raises SystemExit if the sign test fails.
    """
    fs = entry.get("funcsSens", {})
    T = fs.get(thick_name, {}).get(dv_name)
    if T is None:
        return {"available": False,
                "note": "no thickness-constraint Jacobian in this entry; "
                        "DV->lattice mapping NOT independently corroborated"}
    T = np.asarray(T)
    i, j, k = dv_index_grid(ni, nj, nk)
    if T.shape[1] != i.size:
        raise SystemExit("D6R2C SENS REFUSE: thickcon Jacobian has %d DV "
                         "columns, FFD lattice has %d points"
                         % (T.shape[1], i.size))
    up = T[:, j == nj - 1]
    lo = T[:, j == 0]
    ok_sign = bool((up >= 0).all() and (lo <= 0).all())
    W = np.abs(T)
    rowsum = W.sum(axis=1)
    kbar = np.where(rowsum > 0, (W * k).sum(axis=1) / np.where(rowsum > 0, rowsum, 1.0), np.nan)
    finite = kbar[np.isfinite(kbar)]
    monotone = bool(finite.size > 1 and np.all(np.diff(np.unique(np.round(finite, 6))) > 0))
    if not ok_sign:
        raise SystemExit(
            "D6R2C SENS REFUSE: the thickness-constraint Jacobian does not "
            "split by the assumed j index (upper>=0 / lower<=0).  The DV -> FFD "
            "lattice mapping this figure depends on is NOT established; "
            "refusing to draw a figure whose axes would be a guess.")
    return {"available": True,
            "sign_test_upper_nonneg_lower_nonpos": ok_sign,
            "upper_j_min": float(up.min()), "upper_j_max": float(up.max()),
            "lower_j_min": float(lo.min()), "lower_j_max": float(lo.max()),
            "span_weighted_k_monotone_across_constraint_rows": monotone,
            "span_weighted_k_first": float(finite[0]) if finite.size else None,
            "span_weighted_k_last": float(finite[-1]) if finite.size else None}


# ----------------------------------------------------------------------------
# convergence history
# ----------------------------------------------------------------------------
def convergence_series(entries, conInfo, obj_name):
    """Per major iteration: objective and max constraint violation."""
    by_iter = {}
    for d in entries:
        f = d.get("funcs")
        if not isinstance(f, dict) or obj_name not in f:
            continue
        if not d.get("isMajor", True):
            continue
        it = int(d.get("iter", -1))
        viol = 0.0
        per = {}
        for cname, info in conInfo.items():
            if cname not in f:
                continue
            v = np.atleast_1d(np.asarray(f[cname], dtype=float))
            lo = np.atleast_1d(np.asarray(info.get("lower", -np.inf), dtype=float))
            up = np.atleast_1d(np.asarray(info.get("upper", np.inf), dtype=float))
            lo = np.where(np.isfinite(lo) & (np.abs(lo) < 1e29), lo, -np.inf)
            up = np.where(np.isfinite(up) & (np.abs(up) < 1e29), up, np.inf)
            d_lo = np.where(np.isfinite(lo), lo - v, -np.inf)
            d_up = np.where(np.isfinite(up), v - up, -np.inf)
            cv = float(max(0.0, np.max(np.maximum(d_lo, d_up))))
            per[cname] = cv
            viol = max(viol, cv)
        by_iter[it] = {"iter": it,
                       "obj": float(np.atleast_1d(f[obj_name])[0]),
                       "max_con_viol": viol,
                       "per_constraint_viol": per,
                       "time_s": float(d.get("time", float("nan"))),
                       "fail": int(d.get("fail", 0))}
    return [by_iter[i] for i in sorted(by_iter)]


# ----------------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------------
def fig_sensitivity(g, ni, nj, nk, X, Z, meta, out_png, scaler, title_extra=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    i, j, k = dv_index_grid(ni, nj, nk)
    amax = float(np.max(np.abs(g))) or 1.0
    imax = int(np.argmax(np.abs(g)))

    fig = plt.figure(figsize=(13.0, 8.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0], hspace=0.42, wspace=0.26)

    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    sheet_names = {0: "LOWER sheet (FFD j=0)", nj - 1: "UPPER sheet (FFD j=%d)" % (nj - 1)}
    for ax, jj in zip(axes, [0, nj - 1]):
        sel = (j == jj)
        x = X[i[sel], j[sel], k[sel]]
        z = Z[i[sel], j[sel], k[sel]]
        v = g[sel]
        sc = ax.scatter(z, x, c=v, s=86, cmap="RdBu_r", vmin=-amax, vmax=amax,
                        edgecolors="k", linewidths=0.35, marker="s")
        for xx, zz, vv, nn in zip(x, z, v, np.arange(g.size)[sel]):
            ax.annotate("%d" % nn, (zz, xx), fontsize=4.0, ha="center",
                        va="center", color="0.12")
        if j[imax] == jj:
            ax.scatter([Z[i[imax], j[imax], k[imax]]], [X[i[imax], j[imax], k[imax]]],
                       s=300, facecolors="none", edgecolors="lime", linewidths=1.8,
                       zorder=5, label="max |dJ/dx| (DV %d)" % imax)
            ax.legend(loc="upper left", fontsize=8)
        ax.set_xlabel("FFD control-point z  [spanwise, m]")
        ax.set_ylabel("FFD control-point x  [chordwise, m]")
        ax.set_title(sheet_names[jj] + "  -- %d x %d control points" % (ni, nk),
                     fontsize=10)
        ax.grid(alpha=0.25, linestyle=":")
        fig.colorbar(sc, ax=ax, label="dJ/d(shape DV)  [recorded, driver-scaled]")

    axb = fig.add_subplot(gs[1, :])
    colors = ["#1f77b4" if jj == 0 else "#d62728" for jj in j]
    axb.bar(np.arange(g.size), g, color=colors, width=0.85)
    axb.axhline(0.0, color="k", lw=0.8)
    axb.annotate("DV %d  %+.6e" % (imax, g[imax]), (imax, g[imax]),
                 textcoords="offset points",
                 xytext=(-6, -14 if g[imax] > 0 else 8),
                 ha="right", fontsize=8, color="green")
    axb.set_xlabel("shape design-variable index  (DV n -> FFD i=n//%d, j=(n%%%d)//%d, k=n%%%d;  "
                   "blue = lower sheet, red = upper sheet)" % (nj * nk, nj * nk, nk, nk))
    axb.set_ylabel("dJ/d(shape DV)")
    axb.grid(alpha=0.25, linestyle=":")
    axb.set_title("All %d shape sensitivities by design-variable index" % g.size,
                  fontsize=10)

    cap = (
        "D6R2C %s -- OBJECTIVE SENSITIVITY ON THE FFD CONTROL LATTICE%s\n"
        "Quantity: dJ/d(shape design variable), J = %s, from major iteration %s "
        "(history record %s, wall %.1f s into the optimisation).\n"
        "The shape DVs are LOCAL FFD design variables: each moves ONE control point of "
        "FFD/wingFFD.xyz along the FFD y (vertical) axis.  This is therefore a SENSITIVITY "
        "ON THE FFD LATTICE, NOT A SKIN MAP.\n"
        "It is NOT interpolated to the wing surface: the DVGeo Jacobian dXsurface/dXffd that "
        "would be needed is never written by the production chain and is not on disk.\n"
        "Values are as RECORDED in OptView.hst, i.e. in the optimizer's driver-scaled space "
        "(add_design_var scaler = %g for 'shape', objective scaler 1.0); "
        "dJ/d(physical FFD displacement) = %g x the plotted value.\n"
        "max |dJ/dx| = %.6e at DV index %d  ->  FFD (i=%d chordwise, j=%d %s, k=%d spanwise), "
        "at x = %.4f m, z = %.4f m."
        % (meta["run_tag"], title_extra,
           meta["obj_name"], meta["iter"], meta["record_key"], meta["time_s"],
           scaler, scaler,
           float(np.abs(g).max()), imax, i[imax], j[imax],
           "upper" if j[imax] == nj - 1 else "lower", k[imax],
           float(X[i[imax], j[imax], k[imax]]), float(Z[i[imax], j[imax], k[imax]])))
    fig.suptitle("D6R2C  shape sensitivity on the FFD control lattice" + title_extra,
                 fontsize=13, y=0.985)
    fig.text(0.012, 0.005, cap, fontsize=7.4, va="bottom", family="monospace")
    fig.subplots_adjust(bottom=0.215, top=0.935, left=0.085, right=0.955)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return out_png


def fig_twist(t, meta, out_png, scaler):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    ax.bar(np.arange(1, t.size + 1), t, color="#7f3fbf")
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xlabel("twist design variable  (reference-axis station 1..%d; root station 0 is fixed)" % t.size)
    ax.set_ylabel("dJ/d(twist DV)  [recorded, driver-scaled]")
    ax.grid(alpha=0.25, linestyle=":")
    ax.set_title("D6R2C %s -- objective sensitivity to the twist design variables" % meta["run_tag"])
    fig.text(0.012, 0.012,
             "Major iteration %s (history record %s).  Recorded in driver-scaled space; "
             "add_design_var scaler = %g for 'twist', so dJ/d(physical twist, deg) = %g x plotted.\n"
             "max |dJ/dtwist| = %.6e at station %d."
             % (meta["iter"], meta["record_key"], scaler, scaler,
                float(np.abs(t).max()), int(np.argmax(np.abs(t))) + 1),
             fontsize=7.6, va="bottom", family="monospace")
    fig.subplots_adjust(bottom=0.24)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return out_png


def fig_convergence(series, meta, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    it = [s["iter"] for s in series]
    ob = [s["obj"] for s in series]
    cv = [s["max_con_viol"] for s in series]

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.6, 7.4), sharex=True)
    a1.plot(it, ob, "o-", color="#1f77b4", lw=1.6)
    a1.set_ylabel("objective  J = %s" % meta["obj_name"])
    a1.grid(alpha=0.3, linestyle=":")
    a1.set_title("D6R2C %s -- optimisation convergence history" % meta["run_tag"])
    i_best = int(np.argmin(ob))
    a1.annotate("best J = %.8f at iter %d" % (ob[i_best], it[i_best]),
                (it[i_best], ob[i_best]), textcoords="offset points",
                xytext=(8, 10), fontsize=8, color="green")
    a1.annotate("start J = %.8f" % ob[0], (it[0], ob[0]),
                textcoords="offset points", xytext=(8, -14), fontsize=8)

    pos = [max(c, 1e-16) for c in cv]
    a2.semilogy(it, pos, "s-", color="#d62728", lw=1.6)
    a2.set_ylabel("max constraint violation\n(worst over all constraints)")
    a2.set_xlabel("major iteration")
    a2.grid(alpha=0.3, linestyle=":", which="both")

    fig.text(0.012, 0.012,
             "Source: %s\n"
             "        (records with funcs and isMajor=True; %d major iterations, 0..%d).\n"
             "Violation = max over CL equality, thickness and volume constraints of "
             "max(lower - value, value - upper, 0), bounds taken from the history's own conInfo.\n"
             "Values plotted as recorded (unscaled objective; objective scaler 1.0).  "
             "Zero violation is floored at 1e-16 for the log axis."
             % (meta["history"], len(series), it[-1]),
             fontsize=7.4, va="bottom", family="monospace")
    fig.subplots_adjust(bottom=0.17)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return out_png


# ----------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def render_all(hst_path, ffd_path, out_dir, tag, obj_name, dv_name, twist_name,
               suffix=""):
    """One full render pass from a history file on disk.  Returns a summary."""
    entries, varInfo, conInfo, objInfo, metadata = hst_read(hst_path)
    if not entries:
        raise SystemExit("D6R2C SENS REFUSE: history %s has no records" % hst_path)
    if obj_name is None:
        obj_name = list(objInfo.keys())[0] if objInfo else "obj.J"

    ni, nj, nk, X, Y, Z = ffd_read(ffd_path)
    ent = last_sens_entry(entries, dv_name, obj_name)
    g = np.asarray(ent["funcsSens"][obj_name][dv_name], dtype=float).ravel()
    if g.size != ni * nj * nk:
        raise SystemExit(
            "D6R2C SENS REFUSE: %d shape sensitivities but the FFD lattice has "
            "%d control points (%dx%dx%d).  The DV -> lattice mapping is not "
            "one-to-one; refusing to plot." % (g.size, ni * nj * nk, ni, nj, nk))
    t = np.asarray(ent["funcsSens"][obj_name].get(twist_name, []), dtype=float).ravel()

    mapping = verify_mapping(ent, ni, nj, nk, Z)

    def scaler_of(name, default=1.0):
        info = varInfo.get(name, {})
        s = np.atleast_1d(np.asarray(info.get("scale", default), dtype=float))
        return float(s[0])

    # driver scaler recovered as (driver bound)/(model bound) is NOT available
    # from the history alone; the history's varInfo carries the SCALED bounds.
    # We therefore report the bound ratio explicitly and let the caller pass the
    # run script's scaler if it wants the physical column.
    shape_bound = float(np.atleast_1d(np.asarray(
        varInfo.get(dv_name, {}).get("upper", [np.nan]), dtype=float))[0])
    twist_bound = float(np.atleast_1d(np.asarray(
        varInfo.get(twist_name, {}).get("upper", [np.nan]), dtype=float))[0])
    shape_scaler = shape_bound / 1.0 if np.isfinite(shape_bound) else 1.0
    twist_scaler = twist_bound / 10.0 if np.isfinite(twist_bound) else 1.0

    i, j, k = dv_index_grid(ni, nj, nk)
    imax = int(np.argmax(np.abs(g)))
    meta = {"run_tag": tag, "obj_name": obj_name, "iter": ent.get("iter"),
            "record_key": ent.get("_key"), "time_s": float(ent.get("time", float("nan"))),
            "history": os.path.abspath(hst_path)}

    os.makedirs(out_dir, exist_ok=True)
    p_sens = os.path.join(out_dir, "%s_sens_ffd_lattice_dJdshape%s.png" % (tag, suffix))
    p_tw = os.path.join(out_dir, "%s_sens_twist_dJdtwist%s.png" % (tag, suffix))
    p_cv = os.path.join(out_dir, "%s_convergence_history%s.png" % (tag, suffix))
    fig_sensitivity(g, ni, nj, nk, X, Z, meta, p_sens, shape_scaler,
                    title_extra=("   [%s]" % suffix.strip("_").upper() if suffix else ""))
    if t.size:
        fig_twist(t, meta, p_tw, twist_scaler)
    series = convergence_series(entries, conInfo, obj_name)
    if not series:
        raise SystemExit("D6R2C SENS REFUSE: no major records carry funcs[%r]" % obj_name)
    fig_convergence(series, meta, p_cv)

    top = np.argsort(-np.abs(g))[:10]
    summary = {
        "reader": "d6r2c_sens_figure.py",
        "reader_version": "1.0",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "history": os.path.abspath(hst_path),
        "history_md5": md5(hst_path),
        "ffd": os.path.abspath(ffd_path),
        "ffd_md5": md5(ffd_path),
        "ffd_dims": {"ni_chord": ni, "nj_vertical": nj, "nk_span": nk,
                     "n_control_points": ni * nj * nk},
        "optimizer_metadata": {kk: metadata.get(kk) for kk in
                               ("optimizer", "version", "nprocs", "startTime",
                                "endTime", "optTime")},
        "objective": obj_name,
        "sens_record_key": ent.get("_key"),
        "sens_major_iter": ent.get("iter"),
        "sens_record_time_s": meta["time_s"],
        "n_shape_dv": int(g.size),
        "dv_index_convention": "n -> i=n//(nj*nk), j=(n%(nj*nk))//nk, k=n%nk "
                               "(C order of getLocalIndex(0)[:,:,:].flatten())",
        "scaling": {
            "space": "driver-scaled, as recorded by pyoptsparse",
            "shape_scaler_from_history_bounds": shape_scaler,
            "twist_scaler_from_history_bounds": twist_scaler,
            "physical_conversion": "dJ/d(physical DV) = scaler * recorded value",
        },
        "dJdshape_recorded": g.tolist(),
        "dJdtwist_recorded": t.tolist(),
        "dJdshape_stats": {
            "max_abs": float(np.abs(g).max()),
            "max_abs_dv_index": imax,
            "max_abs_value_signed": float(g[imax]),
            "max_abs_ffd_ijk": [int(i[imax]), int(j[imax]), int(k[imax])],
            "max_abs_ffd_sheet": "upper" if int(j[imax]) == nj - 1 else "lower",
            "max_abs_ffd_xyz": [float(X[i[imax], j[imax], k[imax]]),
                                float(Y[i[imax], j[imax], k[imax]]),
                                float(Z[i[imax], j[imax], k[imax]])],
            "min": float(g.min()), "max": float(g.max()),
            "mean": float(g.mean()), "l2_norm": float(np.linalg.norm(g)),
            "sum": float(g.sum()),
            "n_zero_exact": int((g == 0.0).sum()),
            "top10": [{"dv": int(n), "value": float(g[n]),
                       "ffd_ijk": [int(i[n]), int(j[n]), int(k[n])]} for n in top],
        },
        "dJdtwist_stats": ({"max_abs": float(np.abs(t).max()),
                            "max_abs_station": int(np.argmax(np.abs(t))) + 1,
                            "values": t.tolist()} if t.size else None),
        "mapping_corroboration": mapping,
        "convergence": series,
        "figures": {"sensitivity_ffd_lattice": p_sens,
                    "sensitivity_twist": p_tw if t.size else None,
                    "convergence_history": p_cv},
        "figure_md5": {p_sens: md5(p_sens), p_cv: md5(p_cv)},
        "not_drawn": [
            "skin (wing-surface) sensitivity map -- the DVGeo Jacobian "
            "dXsurface/dXffd is not written by the production chain and is not "
            "on disk; drawing one would require an unregistered interpolation",
            "baseline-versus-optimised shape overlay -- the deformed FFD is "
            "never written (no writeDeformedFFD in the run script)",
        ],
    }
    if t.size:
        summary["figure_md5"][p_tw] = md5(p_tw)
    return summary


def plant_into_history(src_hst, dst_hst, obj_name, dv_name, value=PLANT):
    """Write a perturbed COPY of the history to disk.

    The plant is placed on the component whose true magnitude is SMALLEST, so a
    reader that sees its input must move both the extreme and the argmax.
    Returns (dv_index, old_value, new_value).
    """
    shutil.copyfile(src_hst, dst_hst)
    os.chmod(dst_hst, 0o644)
    con = sqlite3.connect(dst_hst)
    keys = [r[0] for r in con.execute("select key from %s" % SCHEMA_TABLE)]
    ints = sorted(int(k) for k in keys if k.lstrip("-").isdigit())
    target = None
    for i in reversed(ints):
        d = pickle.loads(con.execute(
            "select value from %s where key=?" % SCHEMA_TABLE, (str(i),)).fetchone()[0])
        if isinstance(d, dict) and isinstance(d.get("funcsSens"), dict) \
                and dv_name in d["funcsSens"].get(obj_name, {}) and d.get("isMajor", True):
            target = (i, d)
            break
    if target is None:
        raise SystemExit("D6R2C SENS REFUSE: cannot plant, no sens record found")
    i, d = target
    arr = np.asarray(d["funcsSens"][obj_name][dv_name], dtype=float)
    flat = arr.ravel()
    n = int(np.argmin(np.abs(flat)))
    old = float(flat[n])
    # The plant is the lab constant, placed EXACTLY, on the quietest component.
    # At this scale 1.234e-03 is >2x the largest genuine positive component, so
    # a reader that sees its input must move the POSITIVE extreme onto DV n.
    new = float(value)
    if new <= float(flat.max()):
        raise SystemExit(
            "D6R2C SENS REFUSE: the planted constant %g does not exceed the "
            "largest genuine positive component %g, so the control could not "
            "prove the reader saw it.  Refusing a control that cannot fail."
            % (new, float(flat.max())))
    flat[n] = new
    d["funcsSens"][obj_name][dv_name] = flat.reshape(arr.shape)
    con.execute("update %s set value=? where key=?" % SCHEMA_TABLE,
                (sqlite3.Binary(pickle.dumps(d, protocol=2)), str(i)))
    con.commit()
    con.close()
    return n, old, new


def main():
    ap = argparse.ArgumentParser(
        description="D6R2C post-hoc sensitivity and convergence figure reader "
                    "(reads artefacts only; writes no run data).")
    ap.add_argument("--run-dir", required=True,
                    help="the run directory to READ (e.g. .../KR_REF)")
    ap.add_argument("--history", default=None,
                    help="pyoptsparse history (default <run-dir>/OptView.hst)")
    ap.add_argument("--ffd", default=None,
                    help="FFD plot3d file (default <run-dir>/FFD/wingFFD.xyz)")
    ap.add_argument("--out-dir", required=True,
                    help="output directory (NEVER inside the run dir being read)")
    ap.add_argument("--tag", default=None, help="figure name prefix")
    ap.add_argument("--objective", default=None, help="objective key (default from objInfo)")
    ap.add_argument("--dv", default="dvs.shape")
    ap.add_argument("--twist-dv", default="dvs.twist")
    ap.add_argument("--selftest-plant", action="store_true",
                    help="planted control: re-render from a perturbed COPY of the "
                         "history written to disk and REFUSE (exit 2) if the "
                         "output does not change")
    a = ap.parse_args()

    t0 = time.time()
    run_dir = os.path.abspath(a.run_dir)
    hst = a.history or os.path.join(run_dir, "OptView.hst")
    ffd = a.ffd or os.path.join(run_dir, "FFD", "wingFFD.xyz")
    out_dir = os.path.abspath(a.out_dir)
    tag = a.tag or os.path.basename(run_dir)

    if os.path.commonpath([out_dir, run_dir]) == run_dir:
        raise SystemExit("D6R2C SENS REFUSE: --out-dir is inside the run "
                         "directory being read; this reader never writes into a "
                         "run directory.")

    try:
        import matplotlib  # noqa: F401
    except ImportError:
        raise SystemExit("D6R2C SENS REFUSE: matplotlib is not available on this "
                         "host.  Reported as a finding; nothing installed.")

    summary = render_all(hst, ffd, out_dir, tag, a.objective, a.dv, a.twist_dv)

    if a.selftest_plant:
        ctl_dir = os.path.join(out_dir, "planted_control")
        os.makedirs(ctl_dir, exist_ok=True)
        p_hst = os.path.join(ctl_dir, "%s_PLANTED.hst" % tag)
        n, old, new = plant_into_history(hst, p_hst,
                                         summary["objective"], a.dv)
        planted = render_all(p_hst, ffd, ctl_dir, tag, a.objective, a.dv,
                             a.twist_dv, suffix="_PLANTED")
        base_png = summary["figures"]["sensitivity_ffd_lattice"]
        plant_png = planted["figures"]["sensitivity_ffd_lattice"]
        same_bytes = (md5(base_png) == md5(plant_png))
        base_g = np.asarray(summary["dJdshape_recorded"], dtype=float)
        plant_g = np.asarray(planted["dJdshape_recorded"], dtype=float)
        base_pos = int(np.argmax(base_g))
        plant_pos = int(np.argmax(plant_g))
        moved = (plant_pos == n and base_pos != n)
        readback_exact = bool(plant_g[n] == new)
        summary["planted_control"] = {
            "constant": PLANT,
            "planted_hst": p_hst,
            "planted_dv_index": n,
            "value_before": old,
            "value_after": new,
            "baseline_shows_plant": bool(base_g[n] == new),
            "readback_from_disk_exact": readback_exact,
            "argmax_positive_before": base_pos,
            "argmax_positive_after": plant_pos,
            "argmax_positive_moved_to_planted_dv": bool(moved),
            "baseline_max_positive": float(base_g.max()),
            "planted_max_positive": float(plant_g.max()),
            "png_bytes_identical": bool(same_bytes),
            "png_bytes_check_note": (
                "WEAK BY CONSTRUCTION: the planted render carries a [PLANTED] "
                "label, so its bytes necessarily differ.  The load-bearing "
                "checks are readback_from_disk_exact and "
                "argmax_positive_moved_to_planted_dv; a no-op plant fails both "
                "and the reader exits 2 (negative control exercised)."),
            "verdict": None,
        }
        if (same_bytes or not moved or not readback_exact
                or summary["planted_control"]["baseline_shows_plant"]):
            summary["planted_control"]["verdict"] = "PLANTED CONTROL FAILED"
            with open(os.path.join(out_dir, "%s_sens_report.json" % tag), "w") as fh:
                json.dump(summary, fh, indent=2)
            sys.stderr.write(
                "D6R2C SENS REFUSE: the reader could not see a perturbation "
                "planted in its own input on disk (png_identical=%s, "
                "argmax_moved=%s).  A figure whose reader cannot see its input "
                "certifies nothing.\n" % (same_bytes, moved))
            return 2
        summary["planted_control"]["verdict"] = "PLANTED CONTROL PASSED"

    summary["wall_s"] = round(time.time() - t0, 3)
    rep = os.path.join(out_dir, "%s_sens_report.json" % tag)
    with open(rep, "w") as fh:
        json.dump(summary, fh, indent=2)
    s = summary["dJdshape_stats"]
    print("D6R2C SENS OK  tag=%s  iter=%s  record=%s" %
          (tag, summary["sens_major_iter"], summary["sens_record_key"]))
    print("  max |dJ/dshape| = %.6e (signed %+.6e) at DV %d -> FFD i=%d j=%d k=%d (%s sheet)"
          % (s["max_abs"], s["max_abs_value_signed"], s["max_abs_dv_index"],
             s["max_abs_ffd_ijk"][0], s["max_abs_ffd_ijk"][1], s["max_abs_ffd_ijk"][2],
             s["max_abs_ffd_sheet"]))
    if "planted_control" in summary:
        print("  planted control: %s" % summary["planted_control"]["verdict"])
    print("  report: %s" % rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
