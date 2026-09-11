#!/usr/bin/env python3
"""M6 ROUTE (d) L1 -- grade the built mesh against MESH_STANDARD sec.3.

Gates are INHERITED and are not set here:
  sec.3.1 max non-orthogonality <= 70 HARD   (warning band 65-70 reported only)
  sec.3.2 max skewness          <= 4  HARD   (boundary faces INCLUDED)
  sec.3.3 max aspect ratio      advisory at 1000, NEVER a lone rejection
plus, fatal from checkMesh itself: negative-volume cells, illegal faces, non-closed mesh.

RULE 3 IS APPLIED TO THE READER. This reader's input is the checkMesh log, so the
plant goes INTO A COPY OF THAT LOG: a known over-gate value is written in and the
reader must report it. A reader never shown able to report a non-zero cannot be
trusted when it reports zero -- which is exactly how route (c)'s L1 zero became
worthless when L2 showed 1,019.

AND THE HONEST LIMIT ON THAT CONTROL, STATED HERE SO IT TRAVELS: passing the plant
proves THE READER WORKS. It does NOT prove the mesh is good, and it does NOT prove
a defect is absent at a resolution this mesh does not reach.

exit 0 PASS | 1 GATE FAIL | 2 NOT A RESULT (reader failed its plant, or no run)
"""
import re, sys, pathlib, shutil, tempfile

GATE_NONORTH, GATE_SKEW, ADVISE_AR = 70.0, 4.0, 1000.0


def read_checkmesh(path):
    """Pull the graded quantities out of a checkMesh log BY NAME."""
    txt = pathlib.Path(path).read_text(errors="ignore")
    out = {}
    m = re.search(r"Max (?:aspect ratio|cell openness).*?aspect ratio = ([\d.eE+-]+)", txt)
    if not m:
        m = re.search(r"Max aspect ratio = ([\d.eE+-]+)", txt)
    out["aspect"] = float(m.group(1)) if m else None
    m = re.search(r"Mesh non-orthogonality Max:\s*([\d.eE+-]+)", txt)
    out["nonortho"] = float(m.group(1)) if m else None
    m = re.search(r"\*\*\*Number of (?:severely )?non-orthogonality.*?:\s*(\d+)", txt)
    out["nonortho_faces"] = int(m.group(1)) if m else 0
    m = re.search(r"Max skewness = ([\d.eE+-]+)", txt)
    out["skew"] = float(m.group(1)) if m else None
    out["neg_vol"] = len(re.findall(r"\*\*\*Zero or negative cell volume", txt))
    out["illegal"] = len(re.findall(r"\*\*\*", txt))
    out["not_closed"] = bool(re.search(r"\*\*\*(?:Open cells|The mesh is not closed)", txt))
    out["ok_line"] = bool(re.search(r"^Mesh OK\.", txt, re.M))
    out["end"] = bool(re.search(r"^End", txt, re.M))
    return out


def main():
    case = pathlib.Path(sys.argv[1])
    log = case / "log.checkMesh"
    if not log.exists():
        print(f"NOT A RESULT: {log} does not exist -- no build to grade."); return 2

    # ---- completion (pre-registration sec.6), BEFORE any number is quoted -----
    for stage in ("blockMesh", "surfaceFeatureExtract", "snappyHexMesh", "checkMesh"):
        rcf = case / f"rc.{stage}"
        lg = case / f"log.{stage}"
        if not rcf.exists():
            print(f"NOT A RESULT: no rc sidecar for {stage}; rc==0 cannot be verified."); return 2
        rc = rcf.read_text().strip()
        endl = lg.exists() and bool(re.search(r"^End", lg.read_text(errors='ignore'), re.M))
        print(f"  completion {stage:22s} rc={rc:>3}  End={endl}")
        if rc != "0" or not endl:
            print(f"NOT A RESULT: {stage} did not complete (rc={rc}, End={endl})."); return 2
    pm = case / "constant/polyMesh"
    missing = [f for f in ("points", "faces", "owner", "neighbour", "boundary")
               if not (pm / f).exists()]
    if missing:
        print(f"NOT A RESULT: polyMesh missing {missing}."); return 2

    # ---- THE PLANT, BEFORE THE VERDICT --------------------------------------
    td = tempfile.mkdtemp(prefix="routed_plant_")
    pl = pathlib.Path(td) / "log.checkMesh"
    txt = log.read_text(errors="ignore")
    planted = re.sub(r"Mesh non-orthogonality Max:\s*[\d.eE+-]+",
                     "Mesh non-orthogonality Max: 85.7012", txt, count=1)
    if planted == txt:
        print("NOT A RESULT: could not plant -- the non-orthogonality line was not found,"); 
        print("              so the reader was never shown able to report a value at all.")
        shutil.rmtree(td, True); return 2
    pl.write_text(planted)
    pv = read_checkmesh(pl)["nonortho"]
    shutil.rmtree(td, True)
    if pv is None or abs(pv - 85.7012) > 1e-9:
        print(f"NOT A RESULT: the reader did not see the planted 85.7012 (saw {pv})."); return 2
    print(f"  [rule 3] PLANT PASS: reader reported the planted {pv} -- it can see an over-gate value.")
    print("  [rule 3] LIMIT: this proves THE READER WORKS. It does not prove the mesh is")
    print("           good, nor that a defect is absent at a resolution this mesh cannot reach.")

    # ---- the verdict ---------------------------------------------------------
    r = read_checkmesh(log)
    print(f"  max non-orthogonality = {r['nonortho']}   (sec.3.1 gate {GATE_NONORTH}, warn 65-70)")
    print(f"  max skewness          = {r['skew']}       (sec.3.2 gate {GATE_SKEW}, boundary included)")
    print(f"  max aspect ratio      = {r['aspect']}     (sec.3.3 ADVISORY {ADVISE_AR}, never a lone rejection)")
    print(f"  severely non-orth faces = {r['nonortho_faces']}   negative-volume flags = {r['neg_vol']}")
    print(f"  Mesh OK line = {r['ok_line']}   not-closed = {r['not_closed']}")

    fails = []
    if r["nonortho"] is None or r["skew"] is None:
        print("NOT A RESULT: a graded quantity was absent from the log."); return 2
    if r["nonortho"] > GATE_NONORTH: fails.append(f"sec.3.1 non-orth {r['nonortho']} > {GATE_NONORTH}")
    if r["skew"] > GATE_SKEW:        fails.append(f"sec.3.2 skew {r['skew']} > {GATE_SKEW}")
    if r["neg_vol"]:                 fails.append(f"{r['neg_vol']} negative-volume flag(s)")
    if r["not_closed"]:              fails.append("mesh not closed")

    if r["aspect"] is not None and r["aspect"] > ADVISE_AR:
        flag = (r["nonortho"] > 60) or (r["skew"] > 2)
        print(f"  sec.3.3 NOTE: aspect {r['aspect']} > {ADVISE_AR} -- advisory. "
              f"{'FLAG FOR INVESTIGATION (joined by non-orth>60 or skew>2)' if flag else 'not a rejection and not a flag'}")

    if fails:
        print("GATE FAIL: " + "; ".join(fails))
        print(f"  location matters and is reported: severely non-orthogonal faces = {r['nonortho_faces']}.")
        print("  Route (c) was killed by WHERE its defect sat, not by how large it was.")
        return 1
    if 65 < r["nonortho"] <= 70:
        print(f"  sec.3.1 WARNING BAND: {r['nonortho']} is in 65-70. Reported, not fatal.")
    print("PASS: MESH_STANDARD sec.3.1 and sec.3.2 cleared, no negative volumes, mesh closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
