#!/usr/bin/env python3
"""build_t5f.py -- the T5f case builder: T5b's recipe plus the FIVE registered items.

Registration: docs/campaigns/T-family/T5f_PREREGISTRATION.md (FROZEN, never edited).

WHY THIS FILE IS A WRAPPER AND NOT A COPY.  T5f registers the SAME geometry, the
SAME mesh ladder and the SAME closure as T5b (registration S3.1: "T5f runs on
T5b's mesh definition, unchanged").  So this file DRIVES the frozen
`../T5_runs/build_t5.py`, re-applies T5b's ONE function-object repair by
IMPORTING it from `../T5b_runs/build_t5b.py` (never by re-typing it), then
applies the five registered items S1-S5 and READS EVERY ONE BACK FROM DISK.
The supervisor's check-1 diff against `build_t5b.py` is then S1-S5, the
checkMesh guard, and the case rename -- and nothing else.

NOTHING IN THIS FILE HOLDS A COPY OF A REGISTERED QUANTITY
-----------------------------------------------------------
The board's standing finding (T26 S19/S20: four instruments carried stale copies
of a registered number) is that an instrument holding its own COPY of a
registered quantity IS the defect, and the fix is to stop copying.  So every
gate, value, scheme, wall type, relaxation factor, cell count, refinement ratio
and cap in this file is PARSED OUT OF THE FROZEN REGISTRATION at run time by
`parse_registration()`, which REFUSES unless each row is found exactly once.
If the frozen document moved, this builder stops; it does not run on a memory.

The two quantities that could NOT be parsed out of the frozen document are named
explicitly rather than smuggled in:

  C1  THE SIX WALL PATCH NAMES.  S3.2 item S2 says "`k` on all six walls" and
      registers the TYPE, but names no patch.  This file does not hold a list.
      It reads the SIX wall patches out of the BUILT MESH
      (`constant/air/polyMesh/boundary`, every patch whose type is `wall` or
      `mappedWall`) and refuses unless the count equals the word parsed from the
      registration ("six").  Ground truth from the mesh beats a copy.

  C2  THE FROZEN RECIPE'S OWN CASE NAMES.  `build_t5.py` only accepts the names
      in its own CASES dict (`T5_CUBE_{c,m,f}`).  T5f's cases are named in the
      registration's rule-2 block as `T5F_CUBE_{c,m,f}`.  This file therefore
      builds under the recipe's name and RENAMES to the registered name, and the
      registered names are parsed out of the registration, not typed here.

THE DEFECT THIS FILE DOES NOT INHERIT
--------------------------------------
`build_t5.py:626` runs `checkMesh` through `foam()`, which tests only the
process rc.  `checkMesh` exits 0 on a FAILED check, so that control could not
fire: the log was written and never read.  T5f registration S6 makes every
checkMesh limb EXCEPT the cell determinant a HARD STOP, and the determinant limb
REPORTED ONLY.  `classify_checkmesh()` below parses the log per region, and is
driven in BOTH directions in `--selftest`: it accepts a clean log, accepts a
determinant-only failure while REPORTING its numbers, and REFUSES a
non-determinant failure.  A guard that cannot be made to fire is not a guard.

Usage:  build_t5f.py --level c [--force]      build one level
        build_t5f.py --print-registration     print every parsed value
        build_t5f.py --selftest
Exit 0 built, 2 refusal.  Zero `assert` statements (L-332); every guard raises
or exits, and the guards are driven under `python3 -O` in --selftest.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T_FAMILY = os.path.abspath(os.path.join(HERE, ".."))
T5_RUNS = os.path.join(T_FAMILY, "T5_runs")
T5B_RUNS = os.path.join(T_FAMILY, "T5b_runs")
BUILD_T5 = os.path.join(T5_RUNS, "build_t5.py")
BUILD_T5B = os.path.join(T5B_RUNS, "build_t5b.py")
REPO = os.path.abspath(os.path.join(T_FAMILY, "..", "..", ".."))
REGISTRATION = os.path.join(REPO, "docs", "campaigns", "T-family",
                            "T5f_PREREGISTRATION.md")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# T5b's ONE change and its inflow-map digest are IMPORTED, never re-typed, so a
# move in T5b's file is a refusal here rather than a silent fork.
sys.path.insert(0, T5B_RUNS)
try:
    import build_t5b  # noqa: E402
except ImportError as exc:
    refuse("../T5b_runs/build_t5b.py not importable: %s" % exc)


# =========================================================================
# THE REGISTRATION PARSER -- every registered quantity is read from the
# frozen document at run time.  Each rule REFUSES unless it matches exactly
# once: a document that moved stops the build, it does not fall back.
# =========================================================================
WORD_NUMBER = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}


def _one(pattern, text, what, flags=0):
    m = re.findall(pattern, text, flags)
    if len(m) != 1:
        refuse("registration parse: %s -- pattern %r matched %d times, expected "
               "exactly 1, in %s. The frozen document has moved and this builder "
               "will not run on a remembered value."
               % (what, pattern, len(m), REGISTRATION))
    return m[0]


def _row(tag, text):
    """The one table row of section 3.2 whose first cell is **<tag>**."""
    return _one(r"^\|\s*\*\*%s\*\*\s*\|(.*)$" % re.escape(tag), text,
                "section 3.2 row %s" % tag, re.M)


def parse_registration(path=None):
    path = path or REGISTRATION
    if not os.path.isfile(path):
        refuse("the frozen registration is not on disk at %s" % path)
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    flat = re.sub(r"\s+", " ", raw)          # rows that wrap across lines
    r = {"registration_path": path, "registration_sha256": sha256_file(path)}

    # ---- rule-2 block: the three registered case names -------------------
    cases = re.findall(r"`?(T5F_CUBE_[cmf])`?", raw)
    uniq = sorted(set(cases))
    if len(uniq) != 3:
        refuse("registration parse: expected exactly three distinct T5F_CUBE_* "
               "case names in %s, found %d (%s)" % (path, len(uniq), uniq))
    r["cases"] = {c[-1]: c for c in uniq}

    # ---- S1: the divergence schemes --------------------------------------
    s1 = _row("S1", raw)
    r["s1_keys"] = sorted(set(re.findall(r"`(div\(phi,(?:k|omega)\))`", s1)))
    if len(r["s1_keys"]) != 2:
        refuse("registration parse: S1 row names %d div keys, expected 2"
               % len(r["s1_keys"]))
    r["s1_old_family"] = _one(r"`(linearUpwind)`", s1, "S1 old scheme family")
    r["s1_new"] = _one(r"\*\*`([^`]+)`\*\*", s1, "S1 new scheme")

    # ---- S2: the wall k boundary condition -------------------------------
    s2 = _row("S2", raw)
    r["s2_old"] = _one(r"`(fixedValue uniform 0)`", s2, "S2 old wall k BC")
    r["s2_new"] = _one(r"\*\*`([^`]+)`\*\*", s2, "S2 new wall k BC")
    word = _one(r"on all (\w+) walls", s2, "S2 wall count word")
    if word not in WORD_NUMBER:
        refuse("registration parse: S2 wall count word %r is not a number word" % word)
    r["n_walls"] = WORD_NUMBER[word]

    # ---- S3: omega internalField (old here, new value in 3.3) ------------
    s3 = _row("S3", raw)
    r["s3_old"] = _one(r"`uniform ([0-9.eE+-]+)`", s3, "S3 old omega internalField")

    # ---- S4: relaxation factors ------------------------------------------
    s4 = _row("S4", raw)
    r["s4_dict"] = _one(r"`(relaxationFactors/equations)`", s4, "S4 dictionary path")
    r["s4_old"] = _one(r"`(k 0\.\d+; omega 0\.\d+)`(?!\*)", s4, "S4 old factors")
    r["s4_new_txt"] = _one(r"\*\*`(k 0\.\d+; omega 0\.\d+)`\*\*", s4, "S4 new factors")
    r["s4_new"] = {k: float(v) for k, v in
                   re.findall(r"(k|omega) (0\.\d+)", r["s4_new_txt"])}
    if sorted(r["s4_new"]) != ["k", "omega"]:
        refuse("registration parse: S4 new factors did not yield k and omega")

    # ---- S5: nNonOrthogonalCorrectors, UNCHANGED -------------------------
    s5 = _row("S5", raw)
    r["s5_key"] = _one(r"`(nNonOrthogonalCorrectors)`", s5, "S5 key")
    r["s5_value"] = int(_one(r"UNCHANGED at (\d+)", s5, "S5 registered value"))

    # ---- 3.3 the registered values ---------------------------------------
    r["omega_internal"] = _one(
        r"\|\s*`omega`\s*`internalField`\s*\|\s*\*\*([0-9.eE+-]+)\*\*", raw,
        "3.3 omega internalField")
    r["k_internal"] = _one(
        r"\|\s*`k`\s*`internalField`\s*\|\s*\*\*([0-9.eE+-]+)\*\*", raw,
        "3.3 k internalField")
    r["end_time"] = int(_one(r"\|\s*`endTime`\s*\|\s*\*\*(\d+)\*\*", raw,
                             "3.3 endTime"))
    unchanged = _one(r"\|\s*solver, model, `Prt`, interface scheme, ranks\s*\|(.*)$",
                     raw, "3.3 unchanged row", re.M)
    r["solver"] = _one(r"`(chtMultiRegionSimpleFoam)`", unchanged, "3.3 solver")
    r["ras_model"] = _one(r"`(kOmegaSST)`", unchanged, "3.3 RAS model")
    r["prt"] = float(_one(r"`Prt ([0-9.]+)`", unchanged, "3.3 Prt"))
    r["interface_scheme"] = _one(r"`(harmonic)`", unchanged, "3.3 interface scheme")
    r["ranks"] = int(_one(r"\*\*(\d+) rank\*\*", unchanged, "3.3 ranks"))

    # ---- 3.1 the mesh the rung inherits ----------------------------------
    counts = _one(r"cell counts \*\*([\d,]+) / ([\d,]+) / ([\d,]+)\*\* air and "
                  r"\*\*([\d,]+) / ([\d,]+) / ([\d,]+)\*\* epoxy", flat,
                  "3.1 cell counts")
    n = [int(x.replace(",", "")) for x in counts]
    r["cells"] = {"air": dict(zip("cmf", n[:3])), "epoxy": dict(zip("cmf", n[3:]))}
    ratios = _one(r"air `r32 = ([\d.]+)`, `r21 = ([\d.]+)`; epoxy `r32 = ([\d.]+)`, "
                  r"`r21 = ([\d.]+)`", flat, "3.1 refinement ratios")
    r["ratios"] = {"air": {"r32": float(ratios[0]), "r21": float(ratios[1])},
                   "epoxy": {"r32": float(ratios[2]), "r21": float(ratios[3])}}
    r["first_layer_um"] = float(_one(r"first layer of \*\*([\d.]+) µm\*\*", flat,
                                     "3.1 first layer"))

    # ---- 6 the checkMesh ruling ------------------------------------------
    r["checkmesh_reported_limb"] = _one(
        r"\*\*the (cell-determinant) limb is REPORTED\*\*", raw, "6 reported limb")

    # ---- 8 the caps -------------------------------------------------------
    caps = re.findall(r"^\|\s*`([cmf])`\s*\|\s*([\d.]+)\s*\|\s*\*\*([\d.]+)\*\*\s*\|$",
                      raw, re.M)
    if len(caps) != 3 or sorted(c[0] for c in caps) != ["c", "f", "m"]:
        refuse("registration parse: section 8 CAP table did not yield exactly one "
               "row per level (got %r)" % (caps,))
    r["point_core_min"] = {c[0]: float(c[1]) for c in caps}
    r["cap_core_min"] = {c[0]: float(c[2]) for c in caps}
    return r


# =========================================================================
# THE checkMesh GUARD -- registration S6.  Parses the log, per region.
# Determinant limb: REPORTED.  Every other limb: HARD STOP.
# =========================================================================
# The ONE checkMesh message that registration S6 makes REPORTED rather than
# gating.  Matched on its EXACT shape: a `***` line this parser does not
# recognise EXACTLY is a hard stop, never a near-miss waved through.
DET_MESSAGE = re.compile(r"^Cells with small determinant \(< [0-9.eE+-]+\) found, "
                         r"number of cells: \d+$")


def classify_checkmesh(log_text):
    """Return (regions, hard_stops, determinant_report).

    regions: [(name, verdict, [failed-check messages])]
    hard_stops: the failed-check messages that are NOT the determinant limb
    determinant_report: per region, (flagged_cells, worst_value) or None

    FAILS CLOSED.  A region with neither terminator, or a `Failed N mesh checks`
    whose N disagrees with the number of `***` lines parsed, is a hard stop: the
    parser refuses to certify a log it did not fully understand.
    """
    blocks = re.split(r"^Mesh stats\s+(\S+)\s*$", log_text, flags=re.M)
    if len(blocks) < 3:
        return ([], ["checkMesh log carries no `Mesh stats <region>` block -- the "
                     "log was not produced by a multi-region checkMesh, or is "
                     "truncated. Refusing to certify a log this parser did not "
                     "understand."], {})
    regions, hard, det = [], [], {}
    for i in range(1, len(blocks), 2):
        name, body = blocks[i], blocks[i + 1]
        stars = [s.strip() for s in re.findall(r"^\s*\*\*\*(.*)$", body, re.M)]
        ok = re.search(r"^Mesh OK\.\s*$", body, re.M)
        failed = re.search(r"^Failed (\d+) mesh checks\.\s*$", body, re.M)
        if not ok and not failed:
            hard.append("region %s: neither `Mesh OK.` nor `Failed N mesh checks.` "
                        "-- the log is truncated or checkMesh died mid-region" % name)
            regions.append((name, "UNPARSED", stars))
            continue
        if ok and failed:
            hard.append("region %s: the log carries BOTH `Mesh OK.` and "
                        "`Failed N mesh checks.`" % name)
        n_failed = int(failed.group(1)) if failed else 0
        if n_failed != len(stars):
            hard.append("region %s: `Failed %d mesh checks.` but %d `***` lines "
                        "parsed -- this parser did not see every failure and will "
                        "not certify the mesh" % (name, n_failed, len(stars)))
        for s in stars:
            if DET_MESSAGE.match(s):
                continue                      # S6: REPORTED, never gating
            hard.append("region %s: %s" % (name, s))
        m = re.search(r"determinant.*number of cells:\s*(\d+)", body, re.I)
        w = re.search(r"Cell determinant \(wellposedness\)\s*:\s*minimum:\s*"
                      r"([0-9.eE+-]+)", body)
        det[name] = (int(m.group(1)) if m else 0,
                     float(w.group(1)) if w else None)
        regions.append((name, "OK" if ok else "FAILED %d" % n_failed, stars))
    return (regions, hard, det)


def checkmesh_gate(logp, reg):
    """THE decision the build makes on a checkMesh log -- ONE implementation,
    driven both by build() and by `--drive-checkmesh`, so the proof that this
    guard fires is a proof about the code that actually gates the build."""
    if not os.path.isfile(logp):
        refuse("%s: no checkMesh log on disk. A control whose log cannot be read "
               "is not a control." % logp)
    regions, hard, det = classify_checkmesh(open(logp, errors="replace").read())
    for name, verdict, stars in regions:
        d = det.get(name, (0, None))
        print("  checkMesh %-6s %-10s  %s limb: %d flagged cells, worst %s  "
              "(REPORTED, never gating)"
              % (name, verdict, reg["checkmesh_reported_limb"], d[0],
                 "n/a" if d[1] is None else "%.9g" % d[1]))
    return regions, hard, det


# =========================================================================
# THE FIVE REGISTERED ITEMS -- applied, then READ BACK FROM DISK
# =========================================================================
def _sub_once(path, old, new, what):
    with open(path) as fh:
        txt = fh.read()
    if txt.count(old) != 1:
        refuse("%s: %s -- the text %r is present %d times, expected exactly once. "
               "Nothing is patched." % (path, what, old, txt.count(old)))
    txt = txt.replace(old, new)
    with open(path, "w") as fh:
        fh.write(txt)
    with open(path) as fh:
        back = fh.read()
    if new not in back:
        refuse("%s: %s -- the change is NOT on disk after writing it" % (path, what))
    if old in back:
        refuse("%s: %s -- the OLD text survives the change" % (path, what))
    return back


def wall_patches(case, region, n_expected):
    """C1: the wall patch names come from the BUILT MESH, never from a list."""
    b = os.path.join(case, "constant", region, "polyMesh", "boundary")
    if not os.path.isfile(b):
        refuse("no polyMesh boundary file at %s" % b)
    txt = open(b).read()
    walls = []
    for m in re.finditer(r"^ {4}(\w+)\n {4}\{\n(.*?)^ {4}\}", txt, re.M | re.S):
        t = re.search(r"^\s*type\s+(\w+);", m.group(2), re.M)
        if t and t.group(1) in ("wall", "mappedWall"):
            walls.append(m.group(1))
    walls = sorted(walls)
    if len(walls) != n_expected:
        refuse("%s: found %d wall patches %s, but the registration says all %d "
               "walls. The mesh is not the registered mesh."
               % (b, len(walls), walls, n_expected))
    return walls


def apply_s1(case, reg):
    p = os.path.join(case, "system", "air", "fvSchemes")
    for key in reg["s1_keys"]:
        old = _one(r"^([ \t]*%s[ \t]+bounded Gauss %s grad\([^)]*\);)$"
                   % (re.escape(key), re.escape(reg["s1_old_family"])),
                   open(p).read(), "the %s scheme line in %s" % (key, p), re.M)
        indent = re.match(r"^\s*", old).group(0)
        pad = old[len(indent):].index("bounded")
        new = "%s%s%s;" % (indent, (key + " " * 99)[:pad], reg["s1_new"])
        _sub_once(p, old, new, "S1 %s" % key)
    return p


def apply_s2(case, reg, walls):
    p = os.path.join(case, "0.orig", "air", "k")
    txt = open(p).read()
    for w in walls:
        blk = _one(r"^( {4}%s\n {4}\{\n {8}type )fixedValue;$" % re.escape(w),
                   txt, "the %s wall block in %s" % (w, p), re.M)
        _sub_once(p, blk + "fixedValue;", blk + reg["s2_new"] + ";", "S2 %s" % w)
        txt = open(p).read()
    return p


def apply_s3(case, reg):
    p = os.path.join(case, "0.orig", "air", "omega")
    old = _one(r"^(internalField[ \t]+uniform[ \t]+%s;)$" % re.escape(reg["s3_old"]),
               open(p).read(), "the omega internalField line in %s" % p, re.M)
    new = "internalField uniform %s;" % reg["omega_internal"]
    return _sub_once(p, old, new, "S3 omega internalField")


def apply_s4(case, reg):
    p = os.path.join(case, "system", "air", "fvSolution")
    old = _one(r"(\{[^{}]*%s[^{}]*\})" % re.escape(reg["s4_old"]), open(p).read(),
               "the relaxationFactors equations block in %s" % p)
    new = old.replace(reg["s4_old"], reg["s4_new_txt"])
    return _sub_once(p, old, new, "S4 relaxation factors")


def verify_s5(case, reg):
    """S5 is UNCHANGED: this is a check, never a patch."""
    seen = {}
    for region in ("air", "epoxy"):
        p = os.path.join(case, "system", region, "fvSolution")
        v = int(_one(r"%s\s+(\d+);" % re.escape(reg["s5_key"]), open(p).read(),
                     "%s in %s" % (reg["s5_key"], p)))
        if v != reg["s5_value"]:
            refuse("%s: %s is %d but the registration registers it UNCHANGED at %d"
                   % (p, reg["s5_key"], v, reg["s5_value"]))
        seen[region] = v
    return seen


# =========================================================================
def numeric_time_dirs(d):
    return [x for x in os.listdir(d)
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x) and x != "0"]


def build(level, force):
    reg = parse_registration()
    if level not in reg["cases"]:
        refuse("level %r is not one of the registered levels %s"
               % (level, sorted(reg["cases"])))
    dest_name = reg["cases"][level]                 # T5F_CUBE_<lvl>
    stage_name = "T5_CUBE_%s" % level               # C2: the frozen recipe's name
    dest = os.path.join(HERE, dest_name)
    stage = os.path.join(HERE, stage_name)
    finding = os.path.join(HERE, "FINDING_%s_checkMesh" % dest_name)

    # --- the age-guard precondition (rule 4): refuse an armed or run case ---
    if os.path.isdir(dest):
        if os.path.isdir(os.path.join(dest, "0")) or numeric_time_dirs(dest) \
                or os.path.exists(os.path.join(dest, "log.solve")):
            refuse("%s is ARMED OR RUN (0/, a time directory or log.solve). "
                   "Building over it would destroy evidence and break the age "
                   "guard. Nothing is touched." % dest)
        if not force:
            refuse("%s exists; pass --force to rebuild an UNRUN case" % dest)
        shutil.rmtree(dest)
    for leftover in (stage, finding):
        if os.path.exists(leftover):
            refuse("%s is left over from an earlier build. Inspect it -- it is "
                   "evidence, not clutter -- and move it out of the way by hand."
                   % leftover)
    for f in (BUILD_T5, BUILD_T5B):
        if not os.path.isfile(f):
            refuse("the recipe %s is not on disk" % f)

    # --- 1. the frozen T5 recipe, under the recipe's own case name ---------
    r = subprocess.run([sys.executable, BUILD_T5, "--root", HERE,
                        "--case", stage_name], cwd=T5_RUNS)
    if r.returncode != 0:
        refuse("the frozen build_t5.py failed on %s (rc %d)" % (stage_name, r.returncode))

    # --- 2. THE checkMesh GUARD (registration S6) -- read the log, act on it
    logp = os.path.join(stage, "log.checkMesh")
    regions, hard, det = checkmesh_gate(logp, reg)
    if hard:
        os.rename(stage, finding)
        sys.stderr.write(
            "\nHARD STOP -- registration S6: a checkMesh limb other than the "
            "%s failed.\n" % reg["checkmesh_reported_limb"])
        for h in hard:
            sys.stderr.write("  FAILED CHECK: %s\n" % h)
        refuse("%s: %d non-%s checkMesh failure(s). This is a FINDING and goes to "
               "the supervisor; it is not worked around. The built case is kept "
               "at %s as evidence." % (logp, len(hard),
                                       reg["checkmesh_reported_limb"], finding))

    # --- 3. the inflow map, digest-verified (imported from build_t5b) ------
    src = os.path.join(T5_RUNS, stage_name, "constant", "air", "boundaryData")
    if not os.path.isdir(src):
        refuse("no X_2d inflow map at %s" % src)
    d, n, b = build_t5b.dir_digest(src)
    if (d, n, b) != (build_t5b.BOUNDARYDATA_DIGEST, build_t5b.BOUNDARYDATA_FILES,
                     build_t5b.BOUNDARYDATA_BYTES):
        refuse("the T5 inflow map has MOVED: %s (%d files, %d bytes) against the "
               "digest T5b registered. T5f's inflow would not be T5b's, so the "
               "ladder would not be the registered ladder." % (d, n, b))
    dst = os.path.join(stage, "constant", "air", "boundaryData")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    if build_t5b.dir_digest(dst) != (d, n, b):
        refuse("the copied inflow map does not read back identical")

    # --- 4. T5b's ONE change, imported and driven, never re-typed ----------
    build_t5b.patch_control_dict(os.path.join(stage, "system", "controlDict"))

    # --- 5. THE FIVE REGISTERED ITEMS --------------------------------------
    walls = wall_patches(stage, "air", reg["n_walls"])
    apply_s1(stage, reg)
    apply_s2(stage, reg, walls)
    apply_s3(stage, reg)
    apply_s4(stage, reg)
    verify_s5(stage, reg)

    # --- 6. the registered name (C2) ---------------------------------------
    os.rename(stage, dest)

    with open(os.path.join(dest, "CASE.txt"), "a") as fh:
        fh.write("\n# --- T5f ---\n"
                 "rung=T5f\ncase=%s\nlevel=%s\n"
                 "registration=docs/campaigns/T-family/T5f_PREREGISTRATION.md\n"
                 "registration_sha256=%s\n"
                 "built_from=T5b recipe (build_t5.py + build_t5b.py function-object repair)\n"
                 "build_t5_sha256=%s\nbuild_t5b_sha256=%s\nbuild_t5f_sha256=%s\n"
                 "S1_div_schemes=%s -> %s\nS2_wall_k=%s -> %s on %d walls (%s)\n"
                 "S3_omega_internalField=%s -> %s\nS4_%s=%s -> %s\n"
                 "S5_%s=UNCHANGED at %d (verified, not patched)\n"
                 "checkMesh_hard_stop_limbs=every limb except the %s\n"
                 % (os.path.basename(dest), level, reg["registration_sha256"],
                    sha256_file(BUILD_T5), sha256_file(BUILD_T5B),
                    sha256_file(os.path.abspath(__file__)),
                    " ".join(reg["s1_keys"]), reg["s1_new"],
                    reg["s2_old"], reg["s2_new"], len(walls), " ".join(walls),
                    reg["s3_old"], reg["omega_internal"],
                    reg["s4_dict"], reg["s4_old"], reg["s4_new_txt"],
                    reg["s5_key"], reg["s5_value"],
                    reg["checkmesh_reported_limb"]))
    print("BUILT %s" % dest)
    return 0


# =========================================================================
CLEAN_LOG = """Mesh stats air
    points: 100
Checking geometry...
    Max skewness = 2.8e-13 OK.
    Cell determinant (wellposedness) : minimum: 0.0017 average: 0.5
    Cell determinant check OK.
Mesh OK.

Mesh stats epoxy
    points: 10
Checking geometry...
    Cell determinant (wellposedness) : minimum: 0.0018 average: 0.6
    Cell determinant check OK.
Mesh OK.

End
"""
DET_ONLY_LOG = CLEAN_LOG.replace(
    """    Cell determinant (wellposedness) : minimum: 0.0017 average: 0.5
    Cell determinant check OK.
Mesh OK.""",
    """    Cell determinant (wellposedness) : minimum: 3.262130392e-08 average: 0.15
 ***Cells with small determinant (< 0.001) found, number of cells: 7658
  <<Writing 7658 under-determined cells to set cellDeterminant
Failed 1 mesh checks.""", 1)
OTHER_LIMB_LOG = CLEAN_LOG.replace(
    """    Max skewness = 2.8e-13 OK.""",
    """ ***Max skewness = 6.2 is greater than 4; the mesh is highly skewed.""", 1
).replace("Mesh OK.", "Failed 1 mesh checks.", 1)
STAR_WITH_OK_LOG = CLEAN_LOG.replace(
    """    Max skewness = 2.8e-13 OK.""",
    """ ***Max skewness = 6.2 is greater than 4; the mesh is highly skewed.""", 1)
NEAR_MISS_LOG = CLEAN_LOG.replace(
    """    Max skewness = 2.8e-13 OK.""",
    """ ***Cells with small determinant found in some other phrasing""", 1
).replace("Mesh OK.", "Failed 1 mesh checks.", 1)
MISCOUNT_LOG = DET_ONLY_LOG.replace("Failed 1 mesh checks.", "Failed 2 mesh checks.", 1)


def selftest():
    fails = []

    def ok(cond, msg):
        print("  %-6s %s" % ("ok" if cond else "FAIL", msg))
        if not cond:
            fails.append(msg)

    print("build_t5f.py --selftest")
    print(" A. THE REGISTRATION PARSER (no value in this file is a copy)")
    reg = parse_registration()
    ok(reg["s1_new"] == "bounded Gauss limitedLinear 1", "S1 new scheme parsed: %r" % reg["s1_new"])
    ok(reg["s2_new"] == "kLowReWallFunction", "S2 new wall k BC parsed: %r" % reg["s2_new"])
    ok(reg["n_walls"] == 6, "S2 wall count parsed from the word: %d" % reg["n_walls"])
    ok(float(reg["omega_internal"]) == 1.0e4, "omega internalField parsed: %s" % reg["omega_internal"])
    ok(float(reg["k_internal"]) == 0.0119885, "k internalField parsed: %s" % reg["k_internal"])
    ok(reg["s4_new"] == {"k": 0.3, "omega": 0.3}, "S4 factors parsed: %r" % reg["s4_new"])
    ok(reg["s5_value"] == 0, "S5 registered UNCHANGED at %d" % reg["s5_value"])
    ok(reg["end_time"] == 5000 and reg["ranks"] == 1, "endTime %d, ranks %d" % (reg["end_time"], reg["ranks"]))
    ok(reg["cap_core_min"] == {"c": 38.6, "m": 201.4, "f": 799.2}, "caps parsed: %r" % reg["cap_core_min"])
    ok(sorted(reg["cases"].values()) == ["T5F_CUBE_c", "T5F_CUBE_f", "T5F_CUBE_m"],
       "case names parsed: %r" % sorted(reg["cases"].values()))

    # a moved document must REFUSE, not fall back on a remembered value
    import tempfile
    tmp = tempfile.mkdtemp(prefix="t5f_st_")
    try:
        moved = os.path.join(tmp, "moved.md")
        with open(REGISTRATION, encoding="utf-8") as fh:
            txt = fh.read()
        with open(moved, "w", encoding="utf-8") as fh:
            fh.write(txt.replace("**`kLowReWallFunction`**", "`kLowReWallFunction`"))
        p = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                            "--drive-parse", moved], capture_output=True, text=True)
        ok(p.returncode == 2, "a registration whose S2 row MOVED refuses (exit 2)")
        ok("matched 0 times" in p.stderr, "and names the rule that failed")

        print(" B. THE checkMesh GUARD, BOTH DIRECTIONS (registration S6)")
        regs, hard, det = classify_checkmesh(CLEAN_LOG)
        ok(len(regs) == 2 and not hard, "a CLEAN two-region log is ACCEPTED (%d hard stops)" % len(hard))
        regs, hard, det = classify_checkmesh(DET_ONLY_LOG)
        ok(not hard, "a DETERMINANT-ONLY failure is ACCEPTED (%d hard stops)" % len(hard))
        ok(det["air"] == (7658, 3.262130392e-08),
           "and its numbers are REPORTED: %d flagged cells, worst %.9g" % det["air"])
        regs, hard, det = classify_checkmesh(OTHER_LIMB_LOG)
        ok(len(hard) == 1 and "skew" in hard[0].lower(),
           "a NON-determinant failure is REFUSED and named: %s" % (hard[0] if hard else "NOTHING"))
        regs, hard, det = classify_checkmesh(MISCOUNT_LOG)
        ok(any("did not see every failure" in h for h in hard),
           "a `Failed N` that disagrees with the *** count FAILS CLOSED")
        regs, hard, det = classify_checkmesh("garbage with no region block\n")
        ok(len(hard) == 1, "a log with no region block FAILS CLOSED")
        regs, hard, det = classify_checkmesh(CLEAN_LOG.replace("Mesh OK.", "", 1))
        ok(any("truncated" in h for h in hard), "a region with no terminator FAILS CLOSED")
        regs, hard, det = classify_checkmesh(STAR_WITH_OK_LOG)
        ok(len(hard) >= 1, "a `***` line under a `Mesh OK.` terminator FAILS CLOSED")
        regs, hard, det = classify_checkmesh(NEAR_MISS_LOG)
        ok(len(hard) == 1 and "other phrasing" in hard[0],
           "a determinant-LIKE message that is not the exact registered shape is a "
           "HARD STOP, not a near-miss waved through")

        print(" C. THE FIVE ITEMS, DRIVEN ON REAL DICTIONARY BYTES")
        sys.path.insert(0, T5_RUNS)
        import build_t5
        fs = os.path.join(tmp, "fvSchemes")
        with open(fs, "w") as fh:
            fh.write(build_t5.fv_schemes_air(False))
        st = os.path.join(tmp, "case", "system", "air")
        os.makedirs(st)
        shutil.copy(fs, os.path.join(st, "fvSchemes"))
        with open(os.path.join(st, "fvSolution"), "w") as fh:
            fh.write(build_t5.fv_solution_air(False))
        os.makedirs(os.path.join(tmp, "case", "system", "epoxy"))
        with open(os.path.join(tmp, "case", "system", "epoxy", "fvSolution"), "w") as fh:
            fh.write(build_t5.fv_solution_epoxy())
        os.makedirs(os.path.join(tmp, "case", "0.orig", "air"))
        flds = build_t5.air_fields(True, False, reg["prt"], True, build_t5.CUBE_FACES)
        for nm in ("k", "omega"):
            with open(os.path.join(tmp, "case", "0.orig", "air", nm), "w") as fh:
                fh.write(flds[nm])
        case = os.path.join(tmp, "case")
        apply_s1(case, reg)
        back = open(os.path.join(st, "fvSchemes")).read()
        ok(back.count("bounded Gauss limitedLinear 1;") == 2 and "linearUpwind grad(k)" not in back,
           "S1 applied to both div keys and read back")
        ok("div(phi,U)      bounded Gauss linearUpwind grad(U);" in back,
           "S1 left div(phi,U) and div(phi,h) UNTOUCHED (not registered)")
        w = ["cube_front", "cube_rear", "cube_side_n", "cube_top", "floor", "roof"]
        apply_s2(case, reg, w)
        kb = open(os.path.join(case, "0.orig", "air", "k")).read()
        ok(kb.count("type kLowReWallFunction;") == 6, "S2 applied to all six walls")
        ok(kb.count("type fixedValue;") == 0, "and no wall keeps the hard zero type")
        ok(kb.count("value uniform 0;") == 6,
           "S2 changed ONLY the type -- `value uniform 0` is untouched (nothing else)")
        apply_s3(case, reg)
        ob = open(os.path.join(case, "0.orig", "air", "omega")).read()
        ok(re.search(r"internalField\s+uniform\s+1\.0e\+04;", ob), "S3 omega internalField applied")
        ok("uniform 55.9957" in ob, "S3 left the omega WALL and INLET values untouched (not registered)")
        apply_s4(case, reg)
        sb = open(os.path.join(st, "fvSolution")).read()
        ok("k 0.3; omega 0.3" in sb and "U 0.5; h 0.5" in sb,
           "S4 changed k and omega only -- U and h untouched")
        ok(verify_s5(case, reg) == {"air": 0, "epoxy": 0}, "S5 verified UNCHANGED at 0 in both regions")

        # PLANTED FAILURES: each patch must REFUSE on a moved dictionary
        with open(os.path.join(st, "fvSchemes"), "w") as fh:
            fh.write(build_t5.fv_schemes_air(False).replace(
                "div(phi,k)      bounded Gauss linearUpwind grad(k);", ""))
        p = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                            "--drive-s1", case], capture_output=True, text=True)
        ok(p.returncode == 2, "S1 on a dictionary MISSING div(phi,k) REFUSES (exit 2)")
        p = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                            "--drive-s5", case, "--plant-s5"], capture_output=True, text=True)
        ok(p.returncode == 2, "S5 REFUSES when nNonOrthogonalCorrectors is not the registered value")
        ok("registers it UNCHANGED" in p.stderr, "and says why")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["c", "m", "f"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--print-registration", action="store_true")
    ap.add_argument("--drive-parse", help="internal: parse one registration path")
    ap.add_argument("--drive-checkmesh", help="drive the checkMesh gate on one log file")
    ap.add_argument("--drive-s1", help="internal: drive apply_s1 on one case dir")
    ap.add_argument("--drive-s5", help="internal: drive verify_s5 on one case dir")
    ap.add_argument("--plant-s5", action="store_true", help="internal")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.drive_parse:
        parse_registration(a.drive_parse)
        return 0
    if a.drive_checkmesh:
        reg = parse_registration()
        _regions, hard, _det = checkmesh_gate(a.drive_checkmesh, reg)
        if hard:
            for h in hard:
                sys.stderr.write("  FAILED CHECK: %s\n" % h)
            refuse("%s: %d non-%s checkMesh failure(s). HARD STOP per registration "
                   "S6." % (a.drive_checkmesh, len(hard), reg["checkmesh_reported_limb"]))
        print("CHECKMESH GATE: ACCEPTED (%s)" % a.drive_checkmesh)
        return 0
    if a.drive_s1:
        apply_s1(a.drive_s1, parse_registration())
        return 0
    if a.drive_s5:
        if a.plant_s5:
            p = os.path.join(a.drive_s5, "system", "air", "fvSolution")
            with open(p) as fh:
                txt = fh.read()
            with open(p, "w") as fh:
                fh.write(txt.replace("nNonOrthogonalCorrectors 0;",
                                     "nNonOrthogonalCorrectors 2;"))
        verify_s5(a.drive_s5, parse_registration())
        return 0
    if a.print_registration:
        reg = parse_registration()
        for k in sorted(reg):
            print("%-24s %s" % (k, reg[k]))
        return 0
    if not a.level:
        refuse("--level is required")
    return build(a.level, a.force)


if __name__ == "__main__":
    sys.exit(main())
