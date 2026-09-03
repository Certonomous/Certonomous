#!/usr/bin/env python3
"""A1ZE staging -- and THE ONE-VARIABLE ASSERT, which is the heart of the item.

Stages BOTH arms of one pair from the SAME sources in the SAME invocation, then
proves mechanically that the only thing that differs between them is the patch
identity of `symmetry1` and `symmetry2`. A control arm that silently differs in
a second variable destroys the comparison and would do it quietly; this refuses
instead.

THE TREATMENT TYPE IS READ OUT OF THE COMMIT UNDER TEST. It is not hard-coded:
it is parsed from `system/createPatchDict` at HEAD, whose md5 is asserted to be
the post-`d3f47bfa` value. If that commit is wrong, the wrong type is staged and
G-DIRN.E / G-U2.E see it. The control type is parsed the same way from the
ancestor blob at `d3f47bfa^`. Neither is a literal in this file.

Registered by A1ZE_PREREGISTRATION.md sections 3, 3a and 3b.
Refuses (non-zero exit) rather than degrading. No solver, no container, no launch.
"""
import argparse
import difflib
import hashlib
import os
import re
import shutil
import subprocess
import sys

# --- pinned facts, all verified by execution at freeze -----------------------
DICT_REL = "system/createPatchDict"
TEMPLATE = "cases/dafoam/work/NACA0012_Airfoil_Incompressible"
MD5_HEAD_DICT = "b06b32856f75d4813a763af819b6149c"      # after  d3f47bfa: empty
MD5_ANCESTOR_DICT = "5e89709961881491e3f05dc97bbcf75c"  # before d3f47bfa: symmetry
COMMIT = "d3f47bfa50944c466ff0bad019b36a7b048a0fae"
PLANES = ("symmetry1", "symmetry2")
ITERS = 2000

# The ONLY line kinds whose content may differ between the two staged arms.
# `inGroups` is included deliberately and is NOT a second variable: a patch
# cannot be `type empty` while its inGroups still says `symmetry`, so the two
# lines are one logical change -- the same reason d3f47bfa had to touch the
# field files as well as the dict. Any other differing line refuses.
ALLOWED_KEYS = ("type", "inGroups")

PAIRS = {
    # pair    : (control arm, treatment arm, mesh source, skeleton, alpha)
    "coarse": ("Sc", "Ec",
               "/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-"
               "shape7-primal-tightening/MESH",
               "/home/ubuntu/certonomous-runs/CURRICULUM-D19T-a1-naca0012-"
               "shape7-primal-tightening/MESH",
               4.0),
    "L3": ("S3", "E3",
           "/home/ubuntu/certonomous-runs/A1WR/L3",
           "/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-"
           "polar-incompressible/case",
           12.0),
}

RE_TYPE = re.compile(r"^(\s*)type(\s+)(\w+)(\s*;.*)$")
RE_INGRP = re.compile(r"^(\s*)inGroups(\s+)(\S+)(\s*;.*)$")


class Refuse(Exception):
    pass


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def patch_type_from_dict(text):
    """Parse the patchInfo type each of the two planes carries. Returns the one
    type both agree on, or refuses."""
    types = {}
    pending = None
    for line in text.splitlines():
        s = line.strip()
        for p in PLANES:
            if s == p or s.startswith(p + " ") or s == "name %s;" % p:
                pending = p
        m = RE_TYPE.match(line)
        if m and pending:
            types.setdefault(pending, m.group(3))
    got = {p: types.get(p) for p in PLANES}
    if None in got.values():
        raise Refuse("createPatchDict: could not read a type for %s" % got)
    vals = set(got.values())
    if len(vals) != 1:
        raise Refuse("createPatchDict: the two planes disagree: %s" % got)
    return vals.pop()


def set_patch_types(path, want):
    """Rewrite ONLY the `type` and `inGroups` lines inside the two planes'
    blocks. Returns the number of lines changed. Touches nothing else."""
    with open(path, errors="replace") as f:
        lines = f.readlines()
    out, depth, cur, changed = [], 0, None, 0
    for line in lines:
        s = line.strip()
        if cur is None:
            for p in PLANES:
                if s == p:
                    cur, depth = p, 0
                    break
        elif s.startswith("{"):
            depth += 1
        if cur is not None and depth >= 1:
            m = RE_TYPE.match(line.rstrip("\n"))
            if m:
                new = "%stype%s%s%s\n" % (m.group(1), m.group(2), want, m.group(4))
                if new != line:
                    changed += 1
                out.append(new)
                continue
            m = RE_INGRP.match(line.rstrip("\n"))
            if m:
                new = "%sinGroups%s1(%s)%s\n" % (m.group(1), m.group(2), want,
                                                 m.group(4))
                if new != line:
                    changed += 1
                out.append(new)
                continue
        if cur is not None and s.startswith("}") and depth >= 1:
            cur, depth = None, 0
        out.append(line)
    with open(path, "w") as f:
        f.writelines(out)
    return changed


def declares_planes(path):
    try:
        with open(path, errors="replace") as f:
            t = f.read()
    except (IsADirectoryError, PermissionError):
        return False
    return all(p in t for p in PLANES)


def walk(root):
    out = {}
    for d, _, fs in os.walk(root):
        for fn in fs:
            p = os.path.join(d, fn)
            if os.path.islink(p):
                continue
            out[os.path.relpath(p, root)] = md5(p)
    return out


def controldict(et):
    return """FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         %d;
deltaT          1;
writeControl    timeStep;
writeInterval   %d;
purgeWrite      0;
writeFormat     ascii;
writePrecision  16;
writeCompression on;
timeFormat      general;
timePrecision   16;
runTimeModifiable true;
DebugSwitches { SolverPerformance 0; }
""" % (et, et)


def stage_arm(arm_dir, skel, mesh, want, here):
    os.makedirs(os.path.join(arm_dir, "out"))
    case = os.path.join(arm_dir, "case")
    shutil.copytree(skel, case, symlinks=False, ignore=shutil.ignore_patterns(
        "processor*", "postProcessing", "reports", "*.log", "*.foam",
        "*.html", "*.bin", "*.bin.info", "0"))
    for junk in ("constant/polyMesh", "0"):
        p = os.path.join(case, junk)
        if os.path.isdir(p):
            shutil.rmtree(p)
    # AGE-GUARD PRECONDITION (registration section 3, requirement 3): no `0/`
    # and no numeric time directory may exist in a staged case. `0.orig` starts
    # with a digit and MUST survive -- deleting it is A1WR ADDENDUM D's bug.
    for d in sorted(os.listdir(case)):
        if d == "0.orig":
            continue
        if os.path.isdir(os.path.join(case, d)) and re.match(r"^[0-9]", d):
            raise Refuse("time directory %r present in staged case %s" % (d, case))
    shutil.copytree(os.path.join(mesh, "constant", "polyMesh"),
                    os.path.join(case, "constant", "polyMesh"))
    touched = []
    b = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.exists(b):
        raise Refuse("staged mesh has no constant/polyMesh/boundary")
    set_patch_types(b, want)
    touched.append(os.path.relpath(b, arm_dir))
    orig = os.path.join(case, "0.orig")
    if not os.path.isdir(orig):
        raise Refuse("staged case has no 0.orig")
    for fn in sorted(os.listdir(orig)):
        p = os.path.join(orig, fn)
        if os.path.isfile(p) and declares_planes(p):
            set_patch_types(p, want)
            touched.append(os.path.relpath(p, arm_dir))
    if len(touched) < 2:
        raise Refuse("only %d file(s) declare both planes -- expected the "
                     "boundary plus the 0.orig fields" % len(touched))
    with open(os.path.join(case, "system", "controlDict"), "w") as f:
        f.write(controldict(ITERS))
    shutil.copy(os.path.join(here, "a1ze_runScript.py"),
                os.path.join(arm_dir, "runScript.py"))
    shutil.copy(os.path.join(here, "a1ze_cmd.sh"),
                os.path.join(arm_dir, "a1ze_cmd.sh"))
    return sorted(touched)


def one_variable_assert(ctl_dir, trt_dir, touched, ctl_type, trt_type):
    """REFUSE unless the ONLY files that differ are the ones the patch
    legitimately touches, and their diffs are confined to `type` / `inGroups`
    lines whose new value is the arm's own registered patch type."""
    a, b = walk(ctl_dir), walk(trt_dir)
    if set(a) != set(b):
        only_a = sorted(set(a) - set(b))[:8]
        only_b = sorted(set(b) - set(a))[:8]
        raise Refuse("arm file SETS differ. only in control: %s; only in "
                     "treatment: %s" % (only_a, only_b))
    differ = sorted(p for p in a if a[p] != b[p])
    allowed = set(touched)
    stray = [p for p in differ if p not in allowed]
    if stray:
        raise Refuse("A SECOND VARIABLE: %d file(s) differ that the patch does "
                     "not touch: %s" % (len(stray), stray[:8]))
    missing = [p for p in allowed if p not in differ]
    if missing and ctl_type != trt_type:
        raise Refuse("the patch was staged but %d file(s) are IDENTICAL between "
                     "the arms: %s -- the mutation did not take" % (len(missing),
                                                                    missing[:8]))
    nlines = 0
    for rel in differ:
        with open(os.path.join(ctl_dir, rel), errors="replace") as f:
            la = f.readlines()
        with open(os.path.join(trt_dir, rel), errors="replace") as f:
            lb = f.readlines()
        for line in difflib.unified_diff(la, lb, n=0):
            if line.startswith(("---", "+++", "@@")):
                continue
            if not line.startswith(("+", "-")):
                continue
            body = line[1:].strip()
            key = body.split()[0] if body.split() else ""
            if key not in ALLOWED_KEYS:
                raise Refuse("A SECOND VARIABLE inside %s: differing line is "
                             "not a %s line: %r" % (rel, "/".join(ALLOWED_KEYS),
                                                    body))
            want = trt_type if line.startswith("+") else ctl_type
            if want not in body:
                raise Refuse("differing line in %s does not carry its arm's "
                             "registered type %r: %r" % (rel, want, body))
            nlines += 1
    return differ, nlines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", required=True, choices=sorted(PAIRS))
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--repo", default="/home/ubuntu/Certonomous")
    ap.add_argument("--here", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()

    try:
        ctl, trt, mesh, skel, alpha = PAIRS[a.pair]

        # 1. THE TREATMENT TYPE COMES OUT OF THE COMMIT UNDER TEST.
        dpath = os.path.join(a.repo, TEMPLATE, DICT_REL)
        if md5(dpath) != MD5_HEAD_DICT:
            raise Refuse("HEAD createPatchDict md5 %s != pinned %s -- the "
                         "template moved since A1ZE froze"
                         % (md5(dpath), MD5_HEAD_DICT))
        with open(dpath, errors="replace") as f:
            trt_type = patch_type_from_dict(f.read())

        # 2. THE CONTROL TYPE COMES OUT OF THE ANCESTOR BLOB, not a literal.
        blob = subprocess.run(
            ["git", "-C", a.repo, "show",
             "%s^:%s/%s" % (COMMIT, TEMPLATE, DICT_REL)],
            capture_output=True)
        if blob.returncode != 0:
            raise Refuse("cannot read the ancestor createPatchDict at %s^" % COMMIT)
        if md5_bytes(blob.stdout) != MD5_ANCESTOR_DICT:
            raise Refuse("ancestor createPatchDict md5 %s != pinned %s"
                         % (md5_bytes(blob.stdout), MD5_ANCESTOR_DICT))
        ctl_type = patch_type_from_dict(blob.stdout.decode("utf-8", "replace"))

        if ctl_type == trt_type:
            raise Refuse("control and treatment types are BOTH %r -- the commit "
                         "under test changed nothing and there is no experiment"
                         % ctl_type)
        print("A1ZE_STAGE_TYPES control=%s (from %s^) treatment=%s (from HEAD)"
              % (ctl_type, COMMIT[:8], trt_type))

        for src in (mesh, skel):
            if not os.path.isdir(src):
                raise Refuse("source absent: %s" % src)

        ctl_dir = os.path.join(a.run_root, ctl)
        trt_dir = os.path.join(a.run_root, trt)
        for d in (ctl_dir, trt_dir):
            if os.path.exists(d):
                raise Refuse("arm directory already exists: %s" % d)

        t_ctl = stage_arm(ctl_dir, skel, mesh, ctl_type, a.here)
        t_trt = stage_arm(trt_dir, skel, mesh, trt_type, a.here)
        if t_ctl != t_trt:
            raise Refuse("the two arms touched different file sets: %s vs %s"
                         % (t_ctl, t_trt))
        print("A1ZE_STAGE_TOUCHED %d file(s): %s" % (len(t_ctl), t_ctl))

        differ, nlines = one_variable_assert(ctl_dir, trt_dir, t_ctl,
                                             ctl_type, trt_type)
        print("A1ZE_ONE_VARIABLE_PASS pair=%s arms=%s/%s files_compared=%d "
              "files_differing=%d lines_differing=%d alpha=%s iters=%d"
              % (a.pair, ctl, trt, len(walk(ctl_dir)), len(differ), nlines,
                 alpha, ITERS))
        for rel in differ:
            print("A1ZE_STAGE_DIFF %s" % rel)
        return 0
    except Refuse as e:
        print("A1ZE_STAGE REFUSED -- %s" % e)
        return 7


if __name__ == "__main__":
    sys.exit(main())
