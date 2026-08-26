#!/usr/bin/env python3
"""Build T9a-R1b: T9a's three WALL levels with the interface scheme corrected.

ONE-ROW SUCCESSOR of T9a (GATE FAIL on R1, T9a_RESULTS.md section 1.1: the
face conductivity at each material interface under `Gauss linear` is the
ARITHMETIC mean of the two layer conductivities, 0.42 against the
series-resistance 0.0762 at the 0.8|0.04 interface -- one face per interface
too conductive by a margin that shrinks with dx).  The fix is the HARMONIC face
interpolation of DT: `laplacianSchemes { default Gauss harmonic corrected; }`.

EVERYTHING ELSE IS THE PARENT'S, BYTE FOR BYTE, taken from the parent's freeze
commit with `git show <sha>:<path>` (never from the working tree): 0.orig/T,
0.orig/DT, constant/transportProperties, system/blockMeshDict, controlDict,
fvSolution.  The ONLY line that differs from the parent's fvSchemes is the
laplacianSchemes line, and this builder REFUSES if the diff is anything else.

blockMesh + checkMesh run at build.  NO assert (L-332).

usage: build_t9aR1b.py --root DIR [--level c|m|f ...] | --selftest
"""
import argparse
import difflib
import os
import re
import subprocess
import sys
import time

PARENT_SHA = "0cbaea26573924a27d489a8472fad233e198ca6d"     # T9a case inputs at HEAD of the T9a report commit
PARENT_DIR = "verification/runs/T-family/T9a_runs"
PARENT_CASE = {"c": "W_c", "m": "W_m", "f": "W_f"}
CASE_OF = {lv: "W1b_%s" % lv for lv in PARENT_CASE}
COPIED = ("0.orig/T", "0.orig/DT", "constant/transportProperties", "system/blockMeshDict",
          "system/controlDict", "system/fvSolution", "system/fvSchemes")
OLD_LINE = "laplacianSchemes { default Gauss linear corrected; }"
NEW_LINE = "laplacianSchemes { default Gauss harmonic corrected; }"
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def git_show(path):
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (PARENT_SHA, path)], capture_output=True, text=True)
    if r.returncode != 0:
        refuse("git show %s:%s failed: %s" % (PARENT_SHA, path, r.stderr.strip()))
    return r.stdout


def verify_against_parent(written_text, parent_text):
    """REFUSES unless the written fvSchemes differs from the parent's blob by
    EXACTLY the one registered line."""
    diff = [l for l in difflib.unified_diff(parent_text.splitlines(), written_text.splitlines(), lineterm="", n=0)
            if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    if diff != ["-" + OLD_LINE, "+" + NEW_LINE]:
        refuse("the fvSchemes diff against the parent is not the single registered line: %r" % diff)


def patched_schemes(parent_text):
    if parent_text.count(OLD_LINE) != 1:
        refuse("the parent fvSchemes does not carry exactly one %r line" % OLD_LINE)
    new = parent_text.replace(OLD_LINE, NEW_LINE)
    verify_against_parent(new, parent_text)
    return new


def write_case(root, lv):
    case = os.path.join(root, CASE_OF[lv])
    src = "%s/%s" % (PARENT_DIR, PARENT_CASE[lv])
    for rel in COPIED:
        txt = git_show("%s/%s" % (src, rel))
        if rel == "system/fvSchemes":
            txt = patched_schemes(txt)
        p = os.path.join(case, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(txt)
    parent_case_txt = git_show("%s/CASE.txt" % src)
    cells = re.findall(r"(\d+) cells", parent_case_txt)
    open(os.path.join(case, "CASE.txt"), "w").write(
        "case=%s\nrung=T9a-R1b (one-row successor of T9a: R1 with the harmonic interface scheme)\n"
        "parent_case=%s\nparent_sha=%s\nlevel=%s\ncells_per_layer=%s\nlaplacianSchemes=Gauss harmonic corrected\n"
        "solver=laplacianFoam\nranks=1\nendTime=1000\ndeltaT=1\n"
        % (CASE_OF[lv], PARENT_CASE[lv], PARENT_SHA, lv, ",".join(cells)))
    return case


def mesh(case):
    env = "set +u; . %s >/dev/null 2>&1; " % FOAM_BASHRC
    t0 = time.time()
    bm = subprocess.run(["bash", "-c", env + "blockMesh -case '%s'" % case], capture_output=True, text=True)
    open(os.path.join(case, "log.blockMesh"), "w").write(bm.stdout + bm.stderr)
    cm = subprocess.run(["bash", "-c", env + "checkMesh -case '%s'" % case], capture_output=True, text=True)
    open(os.path.join(case, "log.checkMesh.build"), "w").write(cm.stdout + cm.stderr)
    lines = [l.strip() for l in (cm.stdout + cm.stderr).splitlines() if re.search(r"^\s*cells:|Mesh OK|Failed", l)]
    open(os.path.join(case, "BUILD.txt"), "w").write(
        "case            %s\ndate            %s\nblockMesh_rc    %d\ncheckMesh_rc    %d   wall %.3f s\n%s\n"
        % (os.path.basename(case), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), bm.returncode,
           cm.returncode, time.time() - t0, "\n".join("checkMesh       " + l for l in lines)))
    if bm.returncode != 0 or cm.returncode != 0 or "Mesh OK" not in (cm.stdout + cm.stderr):
        refuse("blockMesh/checkMesh failed in %s" % case)


def selftest():
    import ast
    fails = []
    txt = git_show("%s/W_c/system/fvSchemes" % PARENT_DIR)
    new = patched_schemes(txt)
    ok = (NEW_LINE in new and OLD_LINE not in new)
    print("  [%s] parent fvSchemes at %s patched to the single harmonic line" % ("ok " if ok else "FAIL", PARENT_SHA[:8]))
    if not ok:
        fails.append("patch")
    fired = False
    try:
        verify_against_parent(new + "\nplantedExtraLine yes;\n", txt)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] written file with a second changed line (planted extra line) vs the parent blob -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("second-line")
    fired = False
    try:
        patched_schemes(txt.replace(OLD_LINE, "laplacianSchemes { default Gauss linear uncorrected; }"))
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] parent without the registered linear line -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("no-line")
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--level", action="append", choices=list(PARENT_CASE))
    ap.add_argument("--no-mesh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.root:
        refuse("--root is required")
    for lv in (a.level or ["c", "m", "f"]):
        case = write_case(a.root, lv)
        if not a.no_mesh:
            mesh(case)
        print("  built %s from %s@%s with %s" % (os.path.basename(case), PARENT_CASE[lv], PARENT_SHA[:8], NEW_LINE))
