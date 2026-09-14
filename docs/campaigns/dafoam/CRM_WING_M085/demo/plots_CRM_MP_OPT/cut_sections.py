#!/usr/bin/env python3
"""TRUE PLANE CUTS of the CRM wing wall patch at three span stations.

    xvfb-run -a pvpython docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP_OPT/cut_sections.py

WHY THIS EXISTS. The first `section_eta*.csv` in this folder were not cuts at all: each
held a SLAB of wall-patch points gathered inside a spanwise tolerance band, written in
mesh-point order. The wing is swept and tapered, so a slab thick enough to hold points
spans several different sections; drawn as one polyline it crosses itself, and ordering
the slab does not repair it (50 % and 80 % stayed saw-toothed). The fix is geometric:
intersect the wall SURFACE with a plane, then walk the resulting polyline.

THE TWO READS ARE GENUINELY DIFFERENT FILES.
    baseline  Reconstructed Case, t = 0   -> mp04/constant/polyMesh/points.gz
    opt       Decomposed Case,    t = T   -> mp04/processor*/<T>/polyMesh/points.gz
The reader reports 11,205 wing-patch points for the first and 11,865 for the second
(processor-boundary duplicates), which is the tell that two different meshes were read
and not the same one twice.

WHAT THE CUTS SHOW ON THIS RUN. `MP_R2_DESIGN_ITERATIONS.tsv` records iteration 0 and
nothing after it: the run was killed (rc = 137) inside the FIRST adjoint solve, so no
design variable ever moved. The final-time `polyMesh` is therefore the baseline mesh
re-written by the solver, and a point-by-point comparison gives max |dx| = 9.94e-13 m
with ZERO points differing by more than 1e-12 m. The `opt` curve consequently lies on
the baseline exactly. That is the honest content of the figure and it is not disguised.

ORDERING. `SaveData` writes a CSV in dataset point order, and `vtkStripper` passes its
input points through unchanged -- it only builds new POLYLINE CELLS. Reading the CSV
that `SaveData` produces would therefore hand back the same unordered scatter this
script exists to replace. The rows are instead written from the stripper's own polyline
CONNECTIVITY, fetched here, longest polyline kept.

Writes, per station eta in {0.20, 0.50, 0.80}:
    section_eta{20,50,80}_baseline.csv
    section_eta{20,50,80}_opt.csv
each with columns x,y,z in polyline order, plus a header comment carrying the case, the
time directory, the patch, eta, the plane origin and the b/2 that was used.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/MP_R2/mp04"
PATCH = "patch/wing"
STATIONS = (0.20, 0.50, 0.80)
SPAN_AXIS = 1                      # asserted against the bounds below, not assumed


def stage(case_dir, subs, prefix):
    """A read-only symlink view of the case: nothing is written into the run tree."""
    root = tempfile.mkdtemp(prefix=prefix)
    for sub in subs:
        src = os.path.join(case_dir, sub)
        if os.path.exists(src):
            os.symlink(src, os.path.join(root, sub))
    for d in sorted(os.listdir(case_dir)):
        if d.startswith("processor"):
            os.symlink(os.path.join(case_dir, d), os.path.join(root, d))
    foam = os.path.join(root, "c.foam")
    open(foam, "w").close()
    return root, foam


def open_wing(case_type, prefix):
    """Open the wing patch alone and PROVE the time that was loaded.

    `Refresh()` + `UpdatePipelineInformation()` before reading `TimestepValues` is not
    optional on this reader: without it a decomposed case reports `[0.0]` and a request
    for the last time silently returns the initial mesh.
    """
    from paraview.simple import OpenFOAMReader
    subs = ("constant", "system", "0") if case_type == "Reconstructed Case" \
        else ("constant", "system")
    root, foam = stage(CASE, subs, prefix)
    r = OpenFOAMReader(FileName=foam)
    r.CaseType = case_type
    r.SkipZeroTime = 0
    r.Refresh()
    r.UpdatePipelineInformation()
    times = list(r.TimestepValues) or [0.0]
    t = min(times) if case_type == "Reconstructed Case" else max(times)
    if t not in times and times != [0.0]:
        raise SystemExit("REFUSE: time %s not in %s" % (t, times))
    r.MeshRegions = [PATCH]
    r.CellArrays = []
    r.UpdatePipeline(time=t)
    di = r.GetDataInformation()
    if di.GetNumberOfPoints() == 0:
        raise SystemExit("REFUSE: the %s read returned an empty wing patch" % case_type)
    return r, root, t, di


def polylines(proxy):
    """Every polyline of the proxy's output, as ordered lists of xyz.

    The stripper's points are in input order; its CELLS carry the order along the
    profile. This walks the cells, which is the whole point of running the stripper.
    """
    from paraview import servermanager as sm
    import vtk
    d = sm.Fetch(proxy)
    if d.IsA("vtkMultiBlockDataSet"):
        it = d.NewIterator()
        it.InitTraversal()
        blocks = []
        while not it.IsDoneWithTraversal():
            o = it.GetCurrentDataObject()
            if o is not None and o.GetNumberOfPoints():
                blocks.append(o)
            it.GoToNextItem()
        if not blocks:
            return []
        app = vtk.vtkAppendPolyData()
        for b in blocks:
            app.AddInputData(b)
        app.Update()
        d = app.GetOutput()
    out = []
    lines = d.GetLines()
    if lines is None:
        return out
    ids = vtk.vtkIdList()
    lines.InitTraversal()
    while lines.GetNextCell(ids):
        out.append([d.GetPoint(ids.GetId(k)) for k in range(ids.GetNumberOfIds())])
    return out


def cut(reader, t, origin):
    from paraview.simple import ExtractSurface, Slice, TriangleStrips, UpdatePipeline
    surf = ExtractSurface(Input=reader)
    UpdatePipeline(time=t, proxy=surf)
    s = Slice(Input=surf)
    s.SliceType = "Plane"
    s.SliceType.Origin = list(origin)
    s.SliceType.Normal = [0.0, 1.0, 0.0]
    s.Triangulatetheslice = 0
    UpdatePipeline(time=t, proxy=s)
    st = TriangleStrips(Input=s)   # vtkStripper: joins the cut segments into polylines
    UpdatePipeline(time=t, proxy=st)
    return polylines(st)


def write_csv(path, pts, meta):
    with open(path, "w") as f:
        for k, v in meta:
            f.write("# %s: %s\n" % (k, v))
        f.write("x,y,z\n")
        for p in pts:
            f.write("%.10g,%.10g,%.10g\n" % (p[0], p[1], p[2]))


def main():
    import shutil
    reads = {}
    try:
        for tag, ctype, prefix in (("baseline", "Reconstructed Case", "crm_base_"),
                                   ("opt", "Decomposed Case", "crm_opt_")):
            r, root, t, di = open_wing(ctype, prefix)
            b = di.GetBounds()
            reads[tag] = dict(reader=r, root=root, t=t, bounds=b,
                              npts=di.GetNumberOfPoints(), ncells=di.GetNumberOfCells(),
                              ctype=ctype)
            print("%-8s %-20s t=%-8s wing patch: %d points, %d faces"
                  % (tag, ctype, t, di.GetNumberOfPoints(), di.GetNumberOfCells()))
            print("         bounds x %.6f..%.6f  y %.6f..%.6f  z %.6f..%.6f"
                  % (b[0], b[1], b[2], b[3], b[4], b[5]))

        b = reads["baseline"]["bounds"]
        ext = [b[1] - b[0], b[3] - b[2], b[5] - b[4]]
        if ext.index(max(ext)) != SPAN_AXIS:
            raise SystemExit("REFUSE: the longest wing-patch extent is axis %d, not y; "
                             "the span axis assumption is wrong (extents %s)"
                             % (ext.index(max(ext)), ext))
        halfspan = b[2 * SPAN_AXIS + 1]
        print("span axis = y (extents x %.4f, y %.4f, z %.4f m); "
              "b/2 = %.6f m from the wing patch bounds" % (ext[0], ext[1], ext[2], halfspan))

        for eta in STATIONS:
            origin = [0.0, eta * halfspan, 0.0]
            for tag in ("baseline", "opt"):
                R = reads[tag]
                pls = cut(R["reader"], R["t"], origin)
                if not pls:
                    raise SystemExit("REFUSE: eta=%.2f %s returned no polyline" % (eta, tag))
                pls.sort(key=len, reverse=True)
                keep = pls[0]
                print("  eta %.2f %-8s origin %s : %d polyline(s), longest %d points"
                      % (eta, tag, origin, len(pls), len(keep)))
                stem = "section_eta%02d_%s.csv" % (int(round(eta * 100)), tag)
                write_csv(os.path.join(HERE, stem), keep, [
                    ("case", CASE),
                    ("time_directory", R["t"]),
                    ("case_type", R["ctype"]),
                    ("patch", PATCH),
                    ("eta", "%.2f" % eta),
                    ("plane_origin", "(%.6f, %.6f, %.6f)" % tuple(origin)),
                    ("plane_normal", "(0, 1, 0)"),
                    ("halfspan_b_over_2_m", "%.6f" % halfspan),
                    ("polylines_returned", len(pls)),
                    ("points_kept", len(keep)),
                ])
    finally:
        for R in reads.values():
            shutil.rmtree(R["root"], ignore_errors=True)


if __name__ == "__main__":
    main()
