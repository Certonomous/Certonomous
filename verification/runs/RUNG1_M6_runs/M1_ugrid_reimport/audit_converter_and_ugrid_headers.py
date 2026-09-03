#!/usr/bin/env python3
"""Emit the two evidence artifacts the RUNG 0b amendment needs to cite BY PATH.

WHY THIS FILE EXISTS, AND IT IS A DEFECT OF MINE. I measured the five-copy converter
manifest and the 13-header byte-budget audit, then filed them as PROSE IN A COMMIT
MESSAGE (10ba2567) and treated them as filed. A commit message is not a citable
artifact: it cannot be read by a script, cannot be hashed as an input, and cannot be
cited by path from another registration's FROZEN PATHS table. The Rung 0 lane searched
the tree for these records, could not find them, and had to mark its own citation
RELAYED NOT VERIFIED. That was correct of them and avoidable by me.

  -> A MEASUREMENT THAT LIVES ONLY IN A COMMIT MESSAGE IS NOT FILED.

Both artifacts below are RE-MEASURED here from the disk, not transcribed from that
message, so each file is the instrument's own output rather than a copy of my prose.

ARTIFACT 1 -- CONVERTER_COPY_MANIFEST.json
  Every copy of ugrid_to_foam.py on this box, its sha256, size, whether it carries a
  sniff_layout, whether it carries the defective plausibility branch, whether git tracks
  it, and its equivalence class. Purpose: a repair to one copy silently leaves the others
  defective and no reader can tell which is authoritative.

ARTIFACT 2 -- UGRID_HEADER_AUDIT.json
  Every .ugrid file on this box, with the byte-order and packaging PROVEN by total-byte-
  budget identity, what ugrid_to_foam.sniff_layout actually returns when called on it, and
  whether those agree. Purpose: the blast radius of the sniff_layout defect, measured on
  the real population rather than argued from the size of the grids.

THE FROZEN CONVERTER IS IMPORTED READ-ONLY AND IS NOT MODIFIED. This calls
sniff_layout to observe it. Rule 6 -- it is RUNG 0's frozen grading path.

NO BARE assert (L-332): python3 -O deletes asserts, so every refusal here raises.
"""
import hashlib
import json
import os
import struct
import subprocess
import sys

sys.path.insert(0, "/home/ubuntu/Certonomous/cases/committee-grids")
import ugrid_to_foam as u2f  # noqa: E402  -- READ-ONLY observation of the frozen module

ROOTS = ["/home/ubuntu/Certonomous", "/home/ubuntu/certonomous-runs",
         "/home/ubuntu/closure-data", "/home/ubuntu/closure-challenge-benchmark"]
OUT = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"


def die(m):
    raise SystemExit(f"REFUSED: {m}")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def find(pattern_fn):
    out = []
    for R in ROOTS:
        if not os.path.isdir(R):
            continue
        for d, dirs, fs in os.walk(R, onerror=lambda e: None):
            dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "__pycache__")]
            for f in fs:
                if pattern_fn(f):
                    out.append(os.path.join(d, f))
    return sorted(out)


def tracked(p):
    if not p.startswith(REPO + "/"):
        return False
    rel = p[len(REPO) + 1:]
    r = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                       cwd=REPO, capture_output=True)
    return r.returncode == 0


# ---------------------------------------------------------------- artifact 1
def manifest():
    paths = find(lambda f: f == "ugrid_to_foam.py")
    if not paths:
        die("no copy of ugrid_to_foam.py found at all -- the scanner is blind, "
            "and a zero from a blind scanner is not evidence")
    rows = []
    for p in paths:
        txt = open(p, errors="replace").read()
        rows.append({
            "path": p,
            "bytes": os.path.getsize(p),
            "sha256": sha(p),
            "has_sniff_layout": "def sniff_layout" in txt,
            "has_defective_plausibility_branch": "2_000_000_000" in txt,
            "git_tracked": tracked(p),
            "inside_repo": p.startswith(REPO + "/"),
            "mtime": os.path.getmtime(p),
        })
    classes = {}
    for r in rows:
        classes.setdefault(r["sha256"], []).append(r["path"])
    # CONTROL: the frozen committee-grids copy MUST be present and MUST show the defect.
    # A manifest that cannot see the one copy we have independently proven defective is
    # not evidence about the copies it does report.
    frozen = REPO + "/cases/committee-grids/ugrid_to_foam.py"
    ctrl = [r for r in rows if r["path"] == frozen]
    if not ctrl:
        die("CONTROL DID NOT FIRE: the known frozen copy is absent from the manifest")
    if not ctrl[0]["has_defective_plausibility_branch"]:
        die("CONTROL DID NOT FIRE: the known-defective copy reports no defect")
    defective = [r["path"] for r in rows if r["has_defective_plausibility_branch"]]
    return {
        "artifact": "every copy of ugrid_to_foam.py on this box",
        "THIS_IS_NOT_A_GRADED_RUN": True,
        "verdict": "NONE -- an inventory carries no verdict of the fixed vocabulary",
        "roots_searched": ROOTS,
        "n_copies": len(rows),
        "n_equivalence_classes": len(classes),
        "equivalence_classes": {k: sorted(v) for k, v in classes.items()},
        "n_carrying_the_defect": len(defective),
        "paths_carrying_the_defect": sorted(defective),
        "copies": rows,
        "control_frozen_copy_present_and_defective": True,
        "hazard": (
            "Copies are byte-identical across the repo boundary. A repair to one SILENTLY "
            "leaves the others defective and no reader can tell which is authoritative. "
            "At least one defective copy lives OUTSIDE git, so a repo-only divergence "
            "check would not see it."),
        "nothing_here_is_modified": (
            "This script observes only. cases/committee-grids/ugrid_to_foam.py is RUNG 0's "
            "frozen grading path (rule 6) and is imported read-only."),
    }


# ---------------------------------------------------------------- artifact 2
def budget(h, fortran):
    if min(h) < 0:
        return -1
    nN, nT, nQ, nTet, nPyr, nPri, nHex = h
    bulk = (nN * 24 + nT * 12 + nQ * 16 + nT * 4 + nQ * 4
            + nTet * 16 + nPyr * 20 + nPri * 24 + nHex * 32)
    return (44 if fortran else 28) + bulk


def header_audit():
    paths = find(lambda f: f.lower().endswith(".ugrid"))
    if not paths:
        die("no .ugrid file found at all -- the scanner is blind")
    rows = []
    for p in paths:
        size = os.path.getsize(p)
        head = open(p, "rb").read(36)
        truth = []
        for e in ("<", ">"):
            if len(head) >= 28:
                h = struct.unpack(e + "7i", head[:28])
                if budget(h, False) == size:
                    truth.append((e, False, h))
            if len(head) >= 36 and struct.unpack(e + "i", head[:4])[0] == 28:
                h = struct.unpack(e + "7i", head[4:32])
                if budget(h, True) == size:
                    truth.append((e, True, h))
        try:
            got = u2f.sniff_layout(p)
            got_s = ("big" if got[0] == ">" else "little",
                     "fortran" if got[1] else "rawC")
        except Exception as ex:                       # noqa: BLE001 -- recorded, not raised
            got, got_s = None, ("ERROR", type(ex).__name__)
        row = {
            "path": p, "bytes": size,
            "byte_budget_packagings_matching": len(truth),
            "sniff_layout_returns": list(got_s),
        }
        if len(truth) == 1:
            e, fo, h = truth[0]
            row["proven_byte_order"] = "big" if e == ">" else "little"
            row["proven_packaging"] = "fortran" if fo else "rawC"
            row["header"] = list(h)
            row["cells_from_header"] = h[3] + h[4] + h[5] + h[6]
            row["AGREES"] = (got is not None and (e, fo) == (got[0], got[1]))
        else:
            row["proven_byte_order"] = None
            row["proven_packaging"] = None
            row["AGREES"] = None
        rows.append(row)
    # CONTROL: the audit must be able to report BOTH outcomes. If every file agrees, the
    # audit has never been shown able to say "mis-detects", and its agreements are not
    # evidence. The M6I small levels are the known disagreement.
    seen = {r["AGREES"] for r in rows}
    if seen != {True, False}:
        die(f"CONTROL DID NOT FIRE: the audit reported only {seen}. A reader that has "
            f"not been shown able to report BOTH agreement and disagreement is not "
            f"evidence for either.")
    mis = [r["path"] for r in rows if r["AGREES"] is False]
    return {
        "artifact": "byte-budget layout audit of every .ugrid file on this box",
        "THIS_IS_NOT_A_GRADED_RUN": True,
        "verdict": "NONE -- an audit of a reader carries no verdict of the fixed vocabulary",
        "method": ("For each file the exact size implied by its 7-integer header is computed "
                   "under both byte orders and both packagings; exactly one must reproduce "
                   "the on-disk size. That identity is arithmetic, not inference. What "
                   "ugrid_to_foam.sniff_layout actually returns is then recorded beside it."),
        "roots_searched": ROOTS,
        "n_files": len(rows),
        "n_mis_detecting": len(mis),
        "paths_mis_detecting": sorted(mis),
        "blast_radius": ("raw-C-stream UGRID files small enough that the byte-swapped first "
                         "word stays positive and below 2e9. Nothing in RUNG 0 and nothing "
                         "in the four R0-G2b round-trip exports."),
        "why_the_RUNG0_grids_are_safe_CORRECTED": (
            "NOT because they are large. The three DPW5 grids are Fortran unformatted and "
            "the record-marker test fires BEFORE the defective plausibility branch is "
            "reached: the marker reads 28 big-endian and 469,762,048 little-endian. Only "
            "HLPW6 is saved by the overflow mechanism. They are safe BY THE ORDERING OF "
            "THE TESTS, not by their size -- a correct conclusion that rested on a wrong "
            "mechanism until it was measured."),
        "control_both_outcomes_observed": True,
        "files": rows,
    }


def main():
    for name, fn in (("CONVERTER_COPY_MANIFEST.json", manifest),
                     ("UGRID_HEADER_AUDIT.json", header_audit)):
        d = fn()
        p = os.path.join(OUT, name)
        with open(p, "w") as f:
            json.dump(d, f, indent=2, sort_keys=True)
        print(f"WROTE {p}")
    print("\nmanifest: %d copies, %d classes, %d defective"
          % (len(manifest()["copies"]), manifest()["n_equivalence_classes"],
             manifest()["n_carrying_the_defect"]))
    a = header_audit()
    print("audit: %d ugrid files, %d mis-detecting" % (a["n_files"], a["n_mis_detecting"]))


if __name__ == "__main__":
    main()
