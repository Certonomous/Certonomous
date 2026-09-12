#!/usr/bin/env python3
"""render_on_completion.py -- [SANAA-DIRECT] 2026-09-12, relayed:

  "whenever a run completes, i want the paraview visualization of its mesh
   saved... The paraview should show the coarse mesh (or medium mesh if the
   coarse isnt converged). But all fields should be stored as the fine mesh
   result fields (whenever we have it)."

Operationally, and this is the lane's reading of her words, stated so it can be
corrected: the MESH shown is the COARSEST level that converged -- coarse if
coarse converged, medium if it did not -- while the FIELDS written beside it are
those of the FINEST COMPLETED level. Mesh and fields therefore come from
DIFFERENT levels by design, and every output says so on its face rather than
letting a reader assume they match.

It runs AT COMPLETION and is NEVER a reason to delay a launch. It writes only
into <run>/RENDER/ and touches no graded artifact -- no time directory, no field,
no log. It is safe to run against a graded tree because it only READS it.

MRF_R4 HAS ONE GRADED LEVEL BY RULING, so for R4 the mesh level and the field
level are the same level, and the output says that too rather than implying a
choice was made.

usage: render_on_completion.py <RUN_ROOT> [--mesh-level DIR] [--field-level DIR]
"""
import json, os, shutil, subprocess, sys, datetime

FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def foam(cmd, cwd):
    """Run an OpenFOAM command with the environment sourced, capturing rc INSIDE."""
    full = f"source {FOAM} >/dev/null 2>&1 || true; {cmd}"
    p = subprocess.run(["bash", "-c", full], cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def converged(level_dir):
    """Cheap, honest convergence read: the graded row if one exists, else unknown."""
    for name in ("GRADED_ROW.json", "MRF_R4_GRADED_ROW.json"):
        p = os.path.join(level_dir, name)
        if os.path.isfile(p):
            d = json.load(open(p))
            ic = d.get("iterative_convergence")
            if isinstance(ic, dict) and "passed" in str(ic):
                return all(v.get("passed") for v in ic.values() if isinstance(v, dict))
    rc = os.path.join(level_dir, "RC.txt")
    return os.path.isfile(rc) and open(rc).read().strip() == "0"


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: render_on_completion.py <RUN_ROOT> [--mesh-level D] [--field-level D]")
    root = os.path.abspath(sys.argv[1])
    args = sys.argv[2:]
    mesh_level = field_level = None
    if "--mesh-level" in args:
        mesh_level = args[args.index("--mesh-level") + 1]
    if "--field-level" in args:
        field_level = args[args.index("--field-level") + 1]

    levels = [d for d in ("coarse", "medium", "fine")
              if os.path.isdir(os.path.join(root, d))]
    if not levels:
        levels = ["."]

    # HER RULE: mesh from the coarsest CONVERGED level; fields from the finest COMPLETED one.
    if mesh_level is None:
        mesh_level = next((d for d in levels if converged(os.path.join(root, d))), levels[0])
    if field_level is None:
        field_level = next((d for d in reversed(levels) if converged(os.path.join(root, d))),
                           levels[-1])

    out = os.path.join(root, "RENDER")
    os.makedirs(out, exist_ok=True)
    mdir, fdir = os.path.join(root, mesh_level), os.path.join(root, field_level)

    manifest = {
        "written_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "directive": "[SANAA-DIRECT] 2026-09-12: mesh from the coarse level (medium if coarse "
                     "is not converged); fields from the finest completed level",
        "mesh_level": mesh_level, "mesh_dir": mdir,
        "field_level": field_level, "field_dir": fdir,
        "SAME_LEVEL": mesh_level == field_level,
        "note": ("MRF_R4 has ONE graded level by ruling, so mesh and fields come from the same "
                 "level here and no choice was made. Where a family has several, the mesh and "
                 "the fields are from DIFFERENT levels BY DESIGN and this manifest is the record "
                 "of which is which -- never assume a picture's mesh carries its own fields."
                 if mesh_level == field_level else
                 "MESH AND FIELDS ARE FROM DIFFERENT LEVELS, BY DESIGN AND BY HER INSTRUCTION."),
        "levels_present": levels,
        "touches_graded_tree": False,
    }

    # .foam stubs are zero-byte handles ParaView opens; they create no field data.
    for tag, d in (("mesh", mdir), ("fields", fdir)):
        stub = os.path.join(out, f"{tag}_{os.path.basename(d)}.foam")
        open(stub, "w").close()
        manifest[f"{tag}_foam_stub"] = stub

    # A VTK export, produced in a SYMLINKED WORK COPY so the graded tree is never
    # written into. foamToVTK in v2606 has NO -out option -- it writes into
    # <case>/VTK unconditionally -- so pointing it at the graded case would create
    # a directory there and make this script's own `touches_graded_tree: false`
    # false. The work copy is the same pattern paper_parity_setup.sh uses.
    work = os.path.join(out, "work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    for sub in ("constant", "system"):
        src = os.path.join(mdir, sub)
        if os.path.isdir(src):
            os.makedirs(os.path.join(work, sub), exist_ok=True)
            for name in os.listdir(src):
                os.symlink(os.path.join(src, name), os.path.join(work, sub, name))
    # the FIELD level's time directories, symlinked file by file
    for name in sorted(os.listdir(fdir)):
        d = os.path.join(fdir, name)
        if os.path.isdir(d) and name.replace(".", "", 1).isdigit():
            os.makedirs(os.path.join(work, name), exist_ok=True)
            for fn in os.listdir(d):
                fp = os.path.join(d, fn)
                if os.path.isfile(fp):
                    os.symlink(fp, os.path.join(work, name, fn))
    rc, so, se = foam("foamToVTK -constant -latestTime -no-boundary -overwrite", cwd=work)
    manifest["foamToVTK_rc"] = rc
    manifest["foamToVTK_cmd"] = "foamToVTK -constant -latestTime -no-boundary -overwrite"
    vtk = os.path.join(work, "VTK")
    if rc == 0 and os.path.isdir(vtk):
        dest = os.path.join(out, "VTK")
        shutil.rmtree(dest, ignore_errors=True)
        shutil.move(vtk, dest)
        manifest["vtk_dir"] = dest
        manifest["vtk_files"] = sorted(os.listdir(dest))[:20]
    else:
        manifest["foamToVTK_note"] = (
            "NON-ZERO rc or no VTK directory, RECORDED RATHER THAN HIDDEN. The .foam stubs "
            "still open the case in ParaView directly, so the deliverable is not lost. "
            "stderr tail: " + (se or "")[-400:])
    shutil.rmtree(work, ignore_errors=True)

    with open(os.path.join(out, "RENDER_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
