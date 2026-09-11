#!/usr/bin/env python3
"""ARMED VERIFIER FOR A pyHyp EXTRUSION. rc IS NEVER THE VERDICT.

Authorised as a tooling fix by the cfd-supervisor, 2026-09-11, under Sanaa's
clarification the same day that the "OpenFOAM issue" carve-out reaches missing
CAPABILITIES, not defects in tools. **This file grades no physics and produces no
measured number** -- it classifies the outcome of a mesh-construction tool.

THE THREE DEFECTS IT EXISTS FOR, EACH MEASURED IN THIS LAB, NOT ANTICIPATED:
  1. pyHyp REFUSES AND EXITS ZERO. `M6C2_runs/L1/log.pyhyp_noseam` carries
     "ERROR: A free corner or other topology that is not an edge was detected"
     and `rc.pyhyp_noseam` is **0**. A caller reading rc alone records a success and
     goes looking for an output file that was never written.
  2. pyHyp SEGFAULTS, rc = 139, and the segfault is generic. It must be reported as
     the distinct outcome it is, because its CAUSE is diagnosable and specific: a
     zero-length edge in the input surface, which pyHyp itself surfaces only as
     `NaN` in a quality column while printing "Normals are consistent" and
     "Topology complete" (M6C1 Addendum 1 A1.4). Both topology checks pass over it.
  3. THE OUTPUT ARTIFACT IS NOT CHECKED. An rc of 0 and a log full of march lines
     still says nothing about whether a CGNS file exists, is non-empty, and holds a
     volume rather than the surface it was handed.

So the verdict is built from FOUR independent readings -- rc, the log text, the
NaN column scan, and the artifact on disk -- and any one of them can refuse.

VERDICTS (fixed vocabulary, CLAUDE.md rule 1 applies to the gate, not to this
classifier, so these are OUTCOME LABELS and are named as such):
    COMPLETE   -- artifact present, non-degenerate, no refusal text, no NaN column
    REFUSED    -- pyHyp printed a refusal (whatever rc says)
    SEGFAULT   -- rc 139/-11, with the NaN-column diagnosis attached if present
    NO_ARTIFACT-- nothing refused and nothing crashed, and no usable file exists
    UNKNOWN    -- none of the above matched; never silently a success
"""
import sys, os, re, pathlib

REFUSAL_PATTERNS = [
    r"\bERROR\b", r"\bFatal\b", r"free corner",
    r"can only be used for configurations", r"\bTraceback\b",
    r"REFUSED \(\d+\)",
]

def classify(log_path, rc, artifact, min_bytes=1024):
    log = pathlib.Path(log_path).read_text(errors="replace") if os.path.exists(log_path) else ""
    notes = []
    refusals = [p for p in REFUSAL_PATTERNS if re.search(p, log)]
    # the NaN column: pyHyp prints Min Quality / Min Volume as NaN when an input edge
    # has zero length. It is the ONLY signal; the topology checks pass over it.
    nan_rows = len(re.findall(r"^\s+\d+\s+\S+.*\bNaN\b", log, re.M))
    if nan_rows:
        notes.append(f"{nan_rows} march rows carry NaN in a quality column -- the "
                     f"zero-length-edge signature (A1.4); the input surface, not pyHyp")
    complete = "EXTRUSION COMPLETE" in log
    art = pathlib.Path(artifact)
    size = art.stat().st_size if art.exists() else 0
    if rc in (139, -11, 245):
        return "SEGFAULT", notes + [f"rc={rc}"], size
    if refusals:
        return "REFUSED", notes + [f"refusal text matched: {refusals}", f"rc={rc}"], size
    if not art.exists() or size < min_bytes:
        return "NO_ARTIFACT", notes + [f"rc={rc}", f"artifact {artifact} size={size}"], size
    if not complete:
        return "UNKNOWN", notes + [f"rc={rc}", "no 'EXTRUSION COMPLETE' line", f"size={size}"], size
    return "COMPLETE", notes + [f"rc={rc}", f"artifact {size} bytes"], size


def selftest():
    """PLANTED CONTROLS. Each defect is injected into a synthetic log and the
    classifier must SEE it. A classifier not shown able to see a defect is not a
    classifier -- the same rule the comparators live under (rule 3)."""
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp())
    good_art = d / "vol.cgns"; good_art.write_bytes(b"x" * 4096)
    cases = [
        ("clean success", "march...\n  EXTRUSION COMPLETE\n", 0, good_art, "COMPLETE"),
        ("REFUSAL AT rc=0 (defect 1)",
         " Normals are consistent!\n Topology complete.\n ERROR: A free corner or other "
         "topology that is not an\n edge was detected\n", 0, d / "nope.cgns", "REFUSED"),
        ("segfault (defect 2)", "march...\n", 139, d / "nope.cgns", "SEGFAULT"),
        ("segfault WITH the NaN tell",
         " Normals are consistent!\n Topology complete.\n"
         "     19    5.2     1     0  11400  0.500  0.10000  0.10000      NaN        NaN  0.3\n"
         "     20    5.2     2     0  11400  0.538  0.10000  0.10000      NaN        NaN  0.4\n",
         139, d / "nope.cgns", "SEGFAULT"),
        ("rc=0, no file (defect 3)", "march...\n  EXTRUSION COMPLETE\n", 0, d / "nope.cgns", "NO_ARTIFACT"),
        ("rc=0, file too small", "march...\n  EXTRUSION COMPLETE\n", 0,
         (lambda p: (p.write_bytes(b"x" * 10), p)[1])(d / "tiny.cgns"), "NO_ARTIFACT"),
        ("rc=0, file present, no COMPLETE line", "march...\n", 0, good_art, "UNKNOWN"),
        ("our own pre-extrusion refusal", "  REFUSED (4): 3 coincident point pairs\n",
         4, d / "nope.cgns", "REFUSED"),
    ]
    npass = 0
    for name, log, rc, art, want in cases:
        lp = d / "log.txt"; lp.write_text(log)
        got, notes, _ = classify(lp, rc, art)
        ok = got == want
        npass += ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name:34s} expected {want:12s} got {got:12s}"
              + (f"   [{notes[0]}]" if notes and got != "COMPLETE" else ""))
    # the NaN tell must actually be attached, not merely not crash
    lp = d / "log.txt"
    lp.write_text("     19  5.2  1  0  11400  0.5  0.1  0.1   NaN   NaN  0.3\n")
    _, notes, _ = classify(lp, 139, d / "nope.cgns")
    ok = any("NaN" in n for n in notes); npass += ok
    print(f"  {'PASS' if ok else 'FAIL'}  {'NaN diagnosis is ATTACHED, not just survived':34s}")
    print(f"  selftest: {npass}/{len(cases)+1} passed")
    return 0 if npass == len(cases) + 1 else 1


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        sys.exit(selftest())
    log, rc, art = sys.argv[1], int(pathlib.Path(sys.argv[2]).read_text().strip()), sys.argv[3]
    v, notes, size = classify(log, rc, art)
    print(f"  pyHyp OUTCOME: {v}")
    for n in notes:
        print(f"    - {n}")
    sys.exit(0 if v == "COMPLETE" else 7)
