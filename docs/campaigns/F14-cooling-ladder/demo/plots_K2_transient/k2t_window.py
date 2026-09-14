#!/usr/bin/env python3
"""k2t_window.py -- the WINDOW-MEAN patch arithmetic behind the K2 transient set.

Every number the K2bU3R3 figures draw comes from here, and every one of them is a
window mean over the run's OWN WRITTEN TIME DIRECTORIES INSIDE [50, 80] s.

WHICH TIMES, AND WHY IT IS SAID ON EVERY FIGURE
-----------------------------------------------
`K2bU3R3_D59/system/controlDict` writes on `adjustableRunTime` with
`writeInterval 20`, so the run holds 0, 20, 40, 60 and 80 only, and it carries NO
`fieldAverage` function object -- there is no `TMean` and no
`uniform/fieldAveragingProperties` anywhere in the tree. So the 50 -> 80 s window
mean is the MEAN OF THE TWO WRITTEN TIMES 60 AND 80, and that is what `WINDOW_TIMES`
says and what SIDECAR.md prints beside every figure. It is not a 30 s time average
and it is never called one.

THE READER, AND THE ONE PLACE IT HAD TO BE EXTENDED
---------------------------------------------------
Patch values come from the FROZEN `foam_patch_reader` (K2g, registered by
`K2g_PREREGISTRATION.md` section 4), imported and NOT edited. That reader refuses a
patch whose entry carries no `value`, which is correct for it and wrong here: `T` on
`rack{i}_in` is `zeroGradient`, because the rack inlet is an OUTFLOW of the room.
A zeroGradient patch face carries its owner cell's value by definition, so this
module reads `constant/polyMesh/owner`, takes the patch's own slice of it, and
indexes the internal field -- through the frozen reader's own `internal_field` and
`_list_after`. Which path produced a number is returned beside it and printed.

THE PLANTED CONTROL (CLAUDE.md rule 3)
--------------------------------------
Two of the numbers here are near-zero by construction -- the bypass flow and the
recirculation fraction -- and a zero from a reader not shown able to see a non-zero
is not evidence. `plant_check()` copies `80/T` into a scratch tree, plants
PLANT = 1.234e-03 K on the `tile` patch and on ONE `rack0_in` owner cell, re-reads
BOTH through the same functions the figures use, and REFUSES unless both come back
changed by exactly the plant. Nothing is written into the graded run tree.
"""
import os
import shutil
import sys
import tempfile

import numpy as np

REPO = "/home/ubuntu/Certonomous"
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2g_runs"))
import foam_patch_reader as FR            # FROZEN, imported not edited (rule 6)

CASE = os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59")
RUN = "K2bU3R3_D59"

#: The ordered window and the written times inside it. Stated on every figure.
WINDOW = (50.0, 80.0)
WINDOW_TIMES = ("60", "80")

K = 273.15
PLANT = 1.234e-03                         # K, the T-family plant constant
N_RACKS = 4
RACK_X = [(0.6 + 0.6 * i, 0.6 + 0.6 * (i + 1)) for i in range(N_RACKS)]

#: Design figures, from the builders -- NOT typed from memory.
#: build_k2b.QV_RACK = 0.35 m3/s, build_k2b.DT_RACK = 12.0 K,
#: build_k2bU3.QV_TILE = 0.245 m3/s (70 % provisioning), build_k2b.T_SUP = 289 K.
QV_RACK = 0.35
QV_TILE = 0.245
DT_RACK = 12.0
T_SUP = 289.0
RHO0, CP0 = 1.1614, 1007.0                # build_k2b, thermalAuditProperties lineage
P_RACK_W = RHO0 * CP0 * QV_RACK * DT_RACK  # 4.912 kW -- the "4.9 kW rack"


def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg)
    raise SystemExit(2)


class Case:
    """One OpenFOAM case, read through the frozen reader. No solver, no writes."""

    def __init__(self, case=CASE):
        self.case = case
        self.pm = os.path.join(case, "constant", "polyMesh")
        self.meta = FR.boundary_meta(self.pm)
        self._pts = None
        self._own = None
        self._int = {}
        self._area = {}
        self._cen = {}

    # -- mesh ------------------------------------------------------------
    @property
    def points(self):
        if self._pts is None:
            self._pts = FR._points(self.pm)
        return self._pts

    @property
    def owner(self):
        if self._own is None:
            a = FR._list_after(FR._after_header(os.path.join(self.pm, "owner")), 0)
            self._own = a.astype(np.int64)
        return self._own

    def areas(self, patch):
        if patch not in self._area:
            a = FR.patch_face_areas(self.pm, patch)
            if a is None or not len(a):
                refuse("patch %r carries no faces in %s" % (patch, self.pm))
            self._area[patch] = a
        return self._area[patch]

    def centres(self, patch):
        if patch not in self._cen:
            nf, sf = self.meta[patch]
            self._cen[patch] = np.array(
                [self.points[f].mean(axis=0) for f in FR._patch_faces(self.pm, sf, nf)])
        return self._cen[patch]

    # -- fields ----------------------------------------------------------
    def internal(self, time, field):
        key = (str(time), field)
        if key not in self._int:
            p = os.path.join(self.case, str(time), field)
            if not os.path.isfile(p):
                refuse("%s does not exist; this figure will not substitute another "
                       "time's data for it" % p)
            self._int[key] = FR.internal_field(p, 0)
        return self._int[key]

    def patch(self, time, field, patch):
        """(values, how). `how` is 'value entry' or 'zeroGradient owner cell'."""
        nf, sf = self.meta[patch]
        path = os.path.join(self.case, str(time), field)
        try:
            v = FR.patch_values(path, patch, nf)
            if v is None:
                refuse("patch %r is absent from %s" % (patch, path))
            return np.asarray(v, dtype=float), "value entry"
        except ValueError:
            # zeroGradient: the face value IS the owner cell's value.
            own = self.owner[sf:sf + nf]
            return self.internal(time, field)[own], "zeroGradient owner cell"

    # -- window means ----------------------------------------------------
    def window_patch(self, field, patch, times=WINDOW_TIMES):
        vals, how = [], None
        for t in times:
            v, how = self.patch(t, field, patch)
            vals.append(v)
        return np.mean(np.vstack(vals), axis=0), how


# ---------------------------------------------------------------- the numbers
def tile_flow(c, times=WINDOW_TIMES):
    """Total supply through the floor tiles, m3/s, and per rack column.

    `phi` on `tile` is NEGATIVE (flux into the domain); the magnitude is the flow.
    """
    q, how = c.window_patch("phi", "tile", times)
    cen = c.centres("tile")
    per = []
    for x0, x1 in RACK_X:
        m = (cen[:, 0] > x0) & (cen[:, 0] < x1)
        if not m.any():
            refuse("no tile face lies in the rack column x in (%g, %g)" % (x0, x1))
        per.append(float(np.abs(q[m]).sum()))
    return float(np.abs(q).sum()), per, how


def rack_flows(c, times=WINDOW_TIMES):
    """Volumetric demand of each rack, m3/s, from its inlet patch flux."""
    out = []
    for i in range(N_RACKS):
        q, _ = c.window_patch("phi", "rack%d_in" % i, times)
        out.append(float(np.abs(q).sum()))
    return out


def rack_temperatures(c, times=WINDOW_TIMES):
    """Per rack: (T_in mass-flow-weighted, T_out area-weighted, how_in) in K."""
    out = []
    for i in range(N_RACKS):
        tin, how = c.window_patch("T", "rack%d_in" % i, times)
        phin, _ = c.window_patch("phi", "rack%d_in" % i, times)
        tout, _ = c.window_patch("T", "rack%d_out" % i, times)
        aout = c.areas("rack%d_out" % i)
        w = np.abs(phin)
        out.append((float((tin * w).sum() / w.sum()),
                    float((tout * aout).sum() / aout.sum()), how))
    return out


def supply_return(c, times=WINDOW_TIMES):
    """(T_supply area-weighted on `tile`, T_return FLUX-weighted on `return`) in K."""
    tt, _ = c.window_patch("T", "tile", times)
    at = c.areas("tile")
    tr, _ = c.window_patch("T", "return", times)
    pr, _ = c.window_patch("phi", "return", times)
    if pr.sum() <= 0:
        refuse("the return patch carries no net outflow in the window; a "
               "flux-weighted return temperature would divide by ~0")
    return float((tt * at).sum() / at.sum()), float((tr * pr).sum() / pr.sum())


def inlet_profiles(c, times=WINDOW_TIMES):
    """Per rack, (z, T degC) -- the window-mean inlet temperature against height.

    The rack inlet patch is a 10 x 34 grid of faces; the profile is the mean over
    the rack's WIDTH at each of the 34 face-centre heights.
    """
    out = []
    for i in range(N_RACKS):
        t, how = c.window_patch("T", "rack%d_in" % i, times)
        z = c.centres("rack%d_in" % i)[:, 2]
        lev = np.unique(np.round(z, 9))
        prof = np.array([t[np.isclose(z, zz)].mean() for zz in lev])
        out.append((lev, prof - K, how))
    return out


def area_mean(c, field, patch, times=WINDOW_TIMES):
    """The AREA-weighted window mean of `field` on `patch`, in K.

    This is `foam_patch_reader.area_average`'s own arithmetic -- values times face
    areas over the sum of the areas -- taken on the window mean of the face values
    rather than on one time. It is written out here for one reason only: that
    function REFUSES a patch whose entry carries no `value`, which `T` on
    `rack{i}_in` does not (zeroGradient), and it reads one time directory. The
    weighting, the face areas and the field values all still come from the frozen
    reader; see `Case.patch` and `Case.areas`.
    """
    v, how = c.window_patch(field, patch, times)
    a = c.areas(patch)
    return float((v * a).sum() / a.sum()), how


def indices(c, times=WINDOW_TIMES):
    """The operator indices, ON THIS RUN, through the definitions ALREADY FROZEN in
    this folder's `make_k2t_indices.py` -- cited line by line, not re-derived:

        line 19-20  every temperature is an AREA average on its own patch;
                    T_sup on `tile`, T_ret on `return`
        line 24     rec = 100 (T_in - T_sup) / (T_out - T_sup);  cap = 100 - rec
        line 25     RCI_high = 100 if T_in <= 27 degC,
                    else max(0, 100 [1 - (T_in - 27) / 5])
        line 27-28  dT = mean over the four racks of (T_out - T_in);
                    RTI = 100 (T_ret - T_sup) / dT
        line 29     hottest inlet and the rack-to-rack spread

    NOTHING in those definitions is changed. What changes is the case they are
    evaluated on -- K2bU3R3_D59 over the 50 -> 80 s window instead of K2h_L3's
    110/TMean -- and that the rack-inlet average comes through the owner-cell path
    because the patch is zeroGradient here.

    Returns (rows, room) with temperatures in degC and indices in per cent.
    """
    tsup, _ = area_mean(c, "T", "tile", times)
    tret, _ = area_mean(c, "T", "return", times)
    rows = []
    for i in range(N_RACKS):
        tin, how = area_mean(c, "T", "rack%d_in" % i, times)
        tout, _ = area_mean(c, "T", "rack%d_out" % i, times)
        if tout <= tsup:
            refuse("rack %d outlet sits at or below the supply temperature; the "
                   "recirculation index has no denominator" % (i + 1))
        rec = 100.0 * (tin - tsup) / (tout - tsup)
        cap = 100.0 - rec
        rci = 100.0 if (tin - K) <= 27.0 else max(0.0, 100.0 * (1 - (tin - K - 27.0) / 5.0))
        rows.append(["rack %d" % (i + 1), tin - K, tout - K, rci, cap, rec, tout - tin])
    dT = sum(r[6] for r in rows) / float(N_RACKS)
    if dT <= 0:
        refuse("the mean rack rise is not positive; RTI has no denominator")
    rti = 100.0 * (tret - tsup) / dT
    hot = max(rows, key=lambda r: r[1])
    room = {"T_supply_degC": tsup - K, "T_return_degC": tret - K,
            "room_rise_K": tret - tsup, "RTI_pct": rti,
            "hottest_inlet_degC": hot[1], "hottest_rack": hot[0],
            "spread_K": hot[1] - min(r[1] for r in rows), "dT_mean_K": dT}
    return rows, room


def shi_rhi(c, times=WINDOW_TIMES):
    """Supply and Return Heat Index over the four racks, from the window means.

    SHI = sum_i Q_i (T_in,i - T_sup) / sum_i Q_i (T_out,i - T_sup);  RHI = 1 - SHI.
    """
    tsup, _ = supply_return(c, times)
    q = rack_flows(c, times)
    tt = rack_temperatures(c, times)
    num = sum(qi * (t[0] - tsup) for qi, t in zip(q, tt))
    den = sum(qi * (t[1] - tsup) for qi, t in zip(q, tt))
    if den <= 0:
        refuse("the rack outlets sit at or below the supply temperature; SHI has "
               "no denominator")
    return num / den, 1.0 - num / den


# ---------------------------------------------------------------- the control
def plant_check(verbose=True):
    """CLAUDE.md rule 3. Plant PLANT into a SCRATCH copy of 80/T, on BOTH read
    paths, and refuse unless the reader sees exactly it.

    The two paths are genuinely different code and both carry a near-zero this set
    draws: `tile` through the reader's `value` entry (the supply temperature that
    sets the room rise), and `rack0_in` through the owner-cell path (the inlet
    temperature that sets the capture and recirculation numbers).
    """
    c = Case()
    base_t, how_t = c.patch("80", "T", "tile")
    base_r, how_r = c.patch("80", "T", "rack0_in")
    root = tempfile.mkdtemp(prefix="k2t_plant_")
    try:
        os.makedirs(os.path.join(root, "constant"))
        os.symlink(os.path.join(CASE, "constant", "polyMesh"),
                   os.path.join(root, "constant", "polyMesh"))
        os.makedirs(os.path.join(root, "80"))
        txt = open(os.path.join(CASE, "80", "T")).read()

        # arm 1: the `value` entry on tile, 289 -> 289 + PLANT
        needle = "    tile\n    {\n        type            fixedValue;\n        value           uniform 289;"
        if needle not in txt:
            refuse("the tile patch in 80/T is not the fixedValue 289 block the "
                   "plant targets; the control cannot be armed blind")
        planted = txt.replace(needle, needle.replace("uniform 289;",
                                                     "uniform %.10g;" % (289.0 + PLANT)), 1)

        # arm 2: one owner cell of rack0_in, in the internal field
        nf, sf = c.meta["rack0_in"]
        cell = int(c.owner[sf])
        head = planted[:planted.index("internalField")]
        body = planted[planted.index("internalField"):]
        open_i = body.index("(")
        close_i = body.index(")", open_i)
        nums = body[open_i + 1:close_i].split()
        nums[cell] = "%.10g" % (float(nums[cell]) + PLANT)
        planted = head + body[:open_i + 1] + "\n" + "\n".join(nums) + "\n" + body[close_i:]
        open(os.path.join(root, "80", "T"), "w").write(planted)

        pc = Case(root)
        got_t, _ = pc.patch("80", "T", "tile")
        got_r, _ = pc.patch("80", "T", "rack0_in")
        d_t = float(np.abs(got_t - base_t).max())
        d_r = float(np.abs(got_r - base_r).max())
    finally:
        shutil.rmtree(root, ignore_errors=True)
    tol = 1e-9
    if abs(d_t - PLANT) > tol:
        refuse("PLANTED-ZERO CONTROL FAILED on the `value` path: planted %.6e K, "
               "read back %.6e K" % (PLANT, d_t))
    if abs(d_r - PLANT) > tol:
        refuse("PLANTED-ZERO CONTROL FAILED on the owner-cell path: planted %.6e K, "
               "read back %.6e K" % (PLANT, d_r))
    if verbose:
        print("PLANTED-ZERO CONTROL PASSES  plant %.6e K  tile (%s) read %.6e K  "
              "rack0_in (%s) read %.6e K  tol %.0e"
              % (PLANT, how_t, d_t, how_r, d_r, tol))
    return d_t, d_r


if __name__ == "__main__":
    plant_check()
    c = Case()
    tot, per, how = tile_flow(c)
    tsup, tret = supply_return(c)
    print("window %s s, written times %s (%d averaged)"
          % (WINDOW, ", ".join(WINDOW_TIMES), len(WINDOW_TIMES)))
    print("total tile flow      %.6f m3/s   per rack %s  (%s)"
          % (tot, ["%.4f" % p for p in per], how))
    print("room rise            %.4f K   (T_return %.4f K flux-weighted, "
          "T_supply %.4f K)" % (tret - tsup, tret, tsup))
    shi, rhi = shi_rhi(c)
    print("SHI %.5f   RHI %.5f" % (shi, rhi))
    rows, room = indices(c)
    for r in rows:
        print("  %s  T_in %.4f  T_out %.4f  RCI %.3f  CI %.3f  rec %.3f  dT %.4f"
              % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    print("  room: T_sup %.4f  T_ret %.4f  rise %.4f  RTI %.3f  spread %.4f"
          % (room["T_supply_degC"], room["T_return_degC"], room["room_rise_K"],
             room["RTI_pct"], room["spread_K"]))
