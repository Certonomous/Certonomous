#!/usr/bin/env python3
"""AVWC SUCCESSOR COMPARATOR -- re-grades AV1, AV2 and AV1R from their PRESERVED RUN ROOTS
through readers repaired for ONE root cause: a reader that stats an UNCOMPRESSED filename
when `writeCompression on` has written the `.gz`.  ZERO SOLVER COMPUTE.

HOW IT RE-GRADES, and this is the whole design: **it does not re-implement any gate.**
For each item it imports THAT ITEM'S OWN FROZEN COMPARATOR, verifies the file on disk is
byte-identical to the committed blob, REBINDS AT MOST ONE NAME in the imported module, and
then runs THE FROZEN `grade()`.  Every band, threshold, composition rule, planted control
and refusal clause that decides the verdict is literally the frozen code, unedited on disk.
The successor's contribution is one function, and the audit below proves it is one.

  AV1   `av1_grade.py:192-202`  rebind `arm_datum`      (DATUM variant)
  AV2   `av2_grade.py:180-190`  rebind `arm_datum`      (DATUM variant)
  AV1R  `av1r_grade.py`         **REBINDS NOTHING**     (PARTITION variant)

**AV1R IS THE ONE WORTH READING TWICE.  ITS GRADER IS NOT DEFECTIVE.**  `av1r_grade.py:83`
already resolves the datum by candidates -- AV1R was the repair of AV1/AV2's datum variant
-- and `av1r_grade.py:407-419` correctly REFUSED on `partition_cells: [null, null], sum: 0`.
The defect is UPSTREAM, in the PRODUCER `av1r_x.py:75-87`, which stats
`processorN/constant/polyMesh/owner` and records `nCells: None` because the file is
`owner.gz`.  So AV1R is repaired by running the adopted producer reader over the PRESERVED
processor directories and writing the recovered record into a COPY of the artefact; the
grader is then run **completely unmodified**.  A grader that refuses on absent data is not
broken, and this successor does not treat it as though it were.

PRESERVED ROOTS ARE NEVER WRITTEN.  Every item and every control runs on a `cp -a` COPY in
scratch.  Before and after, this comparator takes an md5 manifest of every regular file in
each preserved root and REFUSES if a single hash moves -- see `manifest()` and the
`root_manifest_identical` field.  It is a content check, not a `git status`, because a run
root is not in git.

BIRTH REQUIREMENT (Sanaa 2026-08-28), and the sharpening that a ONE-DIRECTIONAL CONTROL
CERTIFIES HALF AN INSTRUMENT: every plant travels the REAL path -- real preserved files, the
real adopted reader, the real frozen grader -- and every reader is driven in BOTH
directions: a planted case it MUST flag and a planted case it MUST NOT flag.  A repaired
reader's whole risk is that it launders a genuine absence into a pass, so the MUST-FLAG
direction is not decoration here, it is the point.

L-332: NO `assert` anywhere; the module counts ast.Assert nodes in its own source and
refuses on any.  No unconditional success print.
"""
import ast
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import avwc_reader as R                                                    # noqa: E402

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 20

# ---- REGISTERED, frozen with this document -------------------------------------------
ITEMS = {
    # AV1 CARRIES **BOTH** MANIFESTATIONS.  Measured, not assumed: repairing only the datum
    # advances AV1 from `G1 age_reference_absent` to `G-NP partition_cells [null, null]`,
    # because `av1_x.py:75-87` is BYTE-IDENTICAL to `av1r_x.py:75-87` -- AV1R inherited the
    # producer defect verbatim.  A datum-only repair of AV1 moves it from one NOT A RESULT
    # to another, which is why `repairs` is a SET per item and not a single `kind`.
    "AV1": {"repairs": ("DATUM", "PARTITION"), "case": "curriculum_AV1", "grader": "av1_grade.py",
            "grader_md5": "87f15e05130cfdb3cbf195d1daba6154",
            "producer": "av1_x.py", "producer_md5": "74011a9c5e6c760b8aec1c78e928b4d2",
            "artefact": "av1_X.json",
            "root": "/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv",
            "datum_file": ".av1_age_datum", "rebind": ("arm_datum",),
            "defect_lines": "av1_grade.py:198-200 (DATUM) AND av1_x.py:75-87 (PARTITION, the producer)",
            "original_refusal": "G1 age_reference_absent .../X1-S/0/U"},
    # AV2 is SERIAL ON EVERY ARM (`av2_grade.py:59`, ARM_RANKS all 1) -- it has no processor
    # directories at all, so the PARTITION manifestation cannot reach it.  Datum only.
    "AV2": {"repairs": ("DATUM",), "case": "curriculum_AV2", "grader": "av2_grade.py",
            "grader_md5": "4bde0ad7dbdd3e460dcef1fe6d063979",
            "root": "/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality",
            "datum_file": ".av2_age_datum", "rebind": ("arm_datum",),
            "defect_lines": "av2_grade.py:186-188",
            "original_refusal": "G1 age_reference_absent .../X-S/0/U"},
    # AV1R's DATUM variant was already repaired in-item (`av1r_grade.py:83`
    # DATUM_REF_CANDIDATES).  Partition only, and the grader is NOT modified.
    "AV1R": {"repairs": ("PARTITION",), "case": "curriculum_AV1R", "grader": "av1r_grade.py",
             "grader_md5": "b5c1d0092c6d2a2608ad3cc0899ed0fd",
             "producer": "av1r_x.py", "producer_md5": "7313bab8b15629c9d872a39d0654aa08",
             "artefact": "av1r_X.json",
             "root": "/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv",
             "rebind": (),
             "defect_lines": "av1r_x.py:75-87 (THE PRODUCER; the grader is not defective)",
             "original_refusal": "G-NP partition_cells [null, null] sum 0 vs mesh_cells 4032"},
}


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifest(root):
    """md5 of every regular file under `root`, keyed by relative path.  A run root is not
    in git, so `git status` is blind to it (the 'gitignored is not filed' trap); the disk
    is read instead."""
    out = {}
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.isfile(p) and not os.path.islink(p):
                out[os.path.relpath(p, root)] = md5_file(p)
    return out


def load_frozen(item):
    """Import the item's frozen comparator AFTER proving the file on disk is the file that
    was frozen.  Bytecode writing is disabled so importing a frozen case's comparator
    cannot drop a __pycache__ into its directory, and no stale bytecode can invert a unit."""
    sys.dont_write_bytecode = True
    spec = ITEMS[item]
    path = os.path.join(A1, spec["case"], spec["grader"])
    got = md5_file(path)
    if got != spec["grader_md5"]:
        refuse("FROZEN_GRADER_MD5", {"item": item, "path": path,
                                     "registered": spec["grader_md5"], "on_disk": got})
    name = "avwc_frozen_%s" % item
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[name] = mod
    sp.loader.exec_module(mod)
    return mod, path


def _fingerprint(mod):
    return {k: id(v) for k, v in vars(mod).items() if callable(v)}


def make_repaired_arm_datum(mod, datum_file, audit):
    """The ONE replacement.  Same signature and same return as the frozen `arm_datum`, and
    it raises THE FROZEN MODULE'S OWN `refuse`, so a refusal from here is shaped exactly
    like the refusal that instrument would have raised.  The registered reference name is
    taken from the frozen module's OWN `DATUM_REF`, so the successor cannot quietly
    re-register a different reference: candidate[0] IS what the frozen document registered."""
    def arm_datum(base, arm):
        d = os.path.join(base, arm)
        p = os.path.join(d, datum_file)
        if not os.path.isfile(p):
            mod.refuse("G1", {"age_datum_absent": p, "arm": arm})
        datum = int(open(p).read().strip())
        res = R.resolve_datum(d, arm, datum, mod.DATUM_REF[arm], mod.refuse)
        audit[arm] = res
        return d, datum
    return arm_datum


def repair_partition_in_copy(copy_root, artefact):
    """AV1R.  Run the ADOPTED producer reader over the PRESERVED processor directories and
    write the recovered record into the COPY's artefact -- the field `av1r_x.py:75-87`
    should have written, recovered from the same files it was always reading.  Arms with no
    processor directory get `[]`, which is what a serial arm must record."""
    changed = {}
    for arm in sorted(os.listdir(copy_root)):
        adir = os.path.join(copy_root, arm)
        ap = os.path.join(adir, artefact)
        if not os.path.isdir(adir) or not os.path.isfile(ap):
            continue
        rec = R.partition_record(adir)
        j = json.load(open(ap))
        before = j.get("partition")
        j["partition"] = [{"dir": e["dir"], "nCells": e["nCells"]} for e in rec]
        json.dump(j, open(ap, "w"))
        changed[arm] = {"before": before, "after": j["partition"],
                        "resolved_names": [e.get("resolved_name") for e in rec],
                        "sum": sum(e["nCells"] for e in rec if e["nCells"] is not None)}
    return changed


def regrade(item, workdir, mutate=None, repairs=None):
    """Re-grade ONE item on a COPY of its preserved root.  `mutate(copy_root)` is the
    birth-control plant hook; it NEVER touches the preserved root."""
    spec = ITEMS[item]
    src = spec["root"]
    if not os.path.isdir(src):
        refuse("PRESERVED_ROOT_ABSENT", {"item": item, "root": src})
    before = manifest(src)
    copy_root = os.path.join(workdir, "root_%s" % item)
    if os.path.isdir(copy_root):
        shutil.rmtree(copy_root)
    shutil.copytree(src, copy_root, symlinks=True)
    for pc in ("__pycache__",):
        p = os.path.join(copy_root, pc)
        if os.path.isdir(p):
            shutil.rmtree(p)
    if mutate:
        mutate(copy_root)
    mod, gpath = load_frozen(item)
    fp0 = _fingerprint(mod)
    applied = tuple(repairs) if repairs is not None else tuple(spec["repairs"])
    for x in applied:
        if x not in spec["repairs"]:
            refuse("UNREGISTERED_REPAIR", {"item": item, "asked": x, "registered": list(spec["repairs"])})
    audit, part_repair = {}, None
    if "DATUM" in applied:
        mod.arm_datum = make_repaired_arm_datum(mod, spec["datum_file"], audit)
    if "PARTITION" in applied:
        ppath = os.path.join(A1, spec["case"], spec["producer"])
        got = md5_file(ppath)
        if got != spec["producer_md5"]:
            refuse("FROZEN_PRODUCER_MD5", {"item": item, "path": ppath,
                                           "registered": spec["producer_md5"], "on_disk": got})
        part_repair = repair_partition_in_copy(copy_root, spec["artefact"])
    fp1 = _fingerprint(mod)
    rebound = sorted(k for k in set(fp0) | set(fp1) if fp0.get(k) != fp1.get(k))
    expected_rebind = tuple(spec["rebind"]) if "DATUM" in applied else ()
    if tuple(rebound) != expected_rebind:
        refuse("REBIND_AUDIT", {"item": item, "expected": list(expected_rebind),
                                "actual": rebound,
                                "note": "the successor replaces exactly the registered names "
                                        "and no others; everything else that decides the "
                                        "verdict is the frozen code"})
    out = {"item": item, "repairs_applied": list(applied), "frozen_grader": gpath,
           "frozen_grader_md5": spec["grader_md5"], "names_rebound": rebound,
           "defect_lines": spec["defect_lines"], "original_refusal": spec["original_refusal"]}
    try:
        r = mod.grade(copy_root)
        out["verdict"] = r.get("verdict")
        out["refusal"] = None
        out["grade"] = r
    except Exception as ex:                                                # noqa: BLE001
        if type(ex).__name__ != "Refusal":
            raise
        out["verdict"] = "NOT A RESULT"
        out["refusal"] = str(ex)
        out["grade"] = None
    if out["verdict"] not in VOCAB:
        refuse("VOCAB", {"item": item, "verdict": out["verdict"]})
    out["datum_resolution"] = audit or None
    out["partition_repair"] = part_repair
    after = manifest(src)
    out["preserved_root"] = src
    out["preserved_root_files"] = len(before)
    out["root_manifest_identical"] = (before == after)
    if not out["root_manifest_identical"]:
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        refuse("PRESERVED_ROOT_MUTATED", {"item": item, "root": src, "files_moved": moved[:20]})
    return out


def refusal_clause(out):
    """The refusal's own key, so a control can check WHICH clause fired, not merely that
    something did.  A control that only checks 'it refused' passes on the wrong refusal."""
    if not out.get("refusal"):
        return None
    txt = out["refusal"]
    i = txt.find("{")
    try:
        d = json.loads(txt[i:]) if i >= 0 else {}
    except ValueError:
        return "UNPARSEABLE"
    det = d.get("detail")
    keys = sorted(det.keys()) if isinstance(det, dict) else []
    return "%s:%s" % (d.get("REFUSE"), ",".join(keys))


# ================= birth-control plants (they mutate COPIES, never the preserved root) ==
def plant_drop_both_datum_names(arm):
    def f(root):
        for n in ("0/U", "0/U.gz"):
            p = os.path.join(root, arm, n)
            if os.path.isfile(p):
                os.remove(p)
    return f


def plant_age_twin_older(arm, seconds=100):
    def f(root):
        d = os.path.join(root, arm)
        datum = int(open(os.path.join(d, [x for x in os.listdir(d) if x.endswith("_age_datum")][0])).read().strip())
        p = os.path.join(d, "0/U.gz")
        os.utime(p, (datum - seconds, datum - seconds))
    return f


def plant_uncompressed_twin_with_wrong_mtime(arm):
    """Put an UNCOMPRESSED `0/U` next to the real `0/U.gz`, with a WRONG mtime.  candidate[0]
    must win and the EXACT-mtime rule must fire on it -- proving both the ordering and that
    the uncompressed branch did not go slack when the compressed branch was added."""
    def f(root):
        p = os.path.join(root, arm, "0", "U")
        open(p, "w").write("planted uncompressed twin\n")
        os.utime(p, (1, 1))
    return f


def plant_drop_one_owner(arm, proc="processor0"):
    def f(root):
        p = os.path.join(root, arm, proc, "constant", "polyMesh", "owner.gz")
        if os.path.isfile(p):
            os.remove(p)
    return f


def plant_wrong_ncells(arm, proc="processor0", delta=-1):
    """Rewrite the nCells value INSIDE the real gzip.  The repaired reader must read the
    FILE, so the sum must move and the FROZEN grader must refuse on it."""
    def f(root):
        p = os.path.join(root, arm, proc, "constant", "polyMesh", "owner.gz")
        with gzip.open(p, "rt", errors="replace") as fh:
            txt = fh.read()
        import re as _re
        m = _re.search(r"nCells:\s*(\d+)", txt)
        txt = txt[:m.start(1)] + str(int(m.group(1)) + delta) + txt[m.end(1):]
        with gzip.open(p, "wt") as fh:
            fh.write(txt)
    return f


# ================= selftest ============================================================
def selftest(tmp):
    n = 0
    fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    # ---- the reader in isolation, on the REAL preserved files -------------------------
    av1r = ITEMS["AV1R"]["root"]
    rec = R.partition_record(os.path.join(av1r, "X2-S"))
    unit("U1 PARTITION reader on the REAL preserved X2-S: both processors resolve via "
         "`owner.gz` to 2016 + 2016 = 4032, the recorded mesh_cells",
         [e["nCells"] for e in rec] == [2016, 2016]
         and all(e["resolved_name"] == "owner.gz" for e in rec) and sum(e["nCells"] for e in rec) == 4032)
    rec4 = R.partition_record(os.path.join(av1r, "X4-S"))
    unit("U2 PARTITION reader on the REAL preserved X4-S: 1008 x 4 = 4032",
         [e["nCells"] for e in rec4] == [1008] * 4 and sum(e["nCells"] for e in rec4) == 4032)
    unit("U3 PARTITION reader on a SERIAL arm returns [] -- what np = 1 must record "
         "(`av1r_grade.py:409-411` refuses a non-empty record there)",
         R.partition_record(os.path.join(av1r, "X1-S")) == [])
    wc = R.read_write_compression(os.path.join(av1r, "X2-S"))
    unit("U4 `writeCompression` is READ from the arm's own controlDict and is `on` -- the "
         "cause is measured, not assumed (got %r)" % wc.get("write_compression"),
         wc.get("write_compression") == "on")

    # ---- AV1: BOTH manifestations ------------------------------------------------------
    a1d = regrade("AV1", tmp, repairs=("DATUM",))
    unit("U5 AV1 WITH THE DATUM REPAIR ALONE still returns NOT A RESULT -- and it is now a "
         "DIFFERENT refusal: `G-NP partition_cells [null, null] sum 0` against mesh_cells 4032. "
         "**AV1 CARRIES BOTH MANIFESTATIONS OF THE ONE ROOT CAUSE**, because `av1_x.py:75-87` "
         "is byte-identical to `av1r_x.py:75-87`. A datum-only repair moves AV1 from one "
         "NOT A RESULT to another, and this unit is what proves it rather than asserting it "
         "(clause %r)" % refusal_clause(a1d),
         a1d["verdict"] == "NOT A RESULT" and "partition_cells" in (a1d["refusal"] or "")
         and "age_reference_absent" not in (a1d["refusal"] or ""))
    a1 = regrade("AV1", tmp)
    unit("U6 AV1 with BOTH repairs: the original `G1 age_reference_absent` on `X1-S/0/U` is "
         "GONE and the partition is recovered on all four parallel arms to 4032",
         "age_reference_absent" not in (a1["refusal"] or "")
         and all(a1["partition_repair"][x]["sum"] == 4032 for x in ("X2-S", "X2-P", "X4-S", "X4-P")))
    dr = a1["datum_resolution"]
    unit("U7 THE DATUM DEFECT ONLY BITES SERIAL ARMS, measured on AV1's own root: the two "
         "np = 1 arms resolved to the COMPRESSED twin `0/U.gz` (+51 s and +54 s newer than "
         "their datum -- the solver rewrote them), while every np = 2 / np = 4 arm still "
         "carries the UNCOMPRESSED `0/U` at EXACTLY its datum, because each rank writes its "
         "own `processorN/0/U.gz` and the arm-root file is left alone. That is why AV1 "
         "refused on `X1-S`, the first serial arm",
         dr["X1-S"]["resolved_name"] == "0/U.gz" and dr["X1-P"]["resolved_name"] == "0/U.gz"
         and dr["X1-S"]["seconds_newer_than_datum"] == 51 and dr["X1-P"]["seconds_newer_than_datum"] == 54
         and all(dr[a]["resolved_name"] == "0/U" and dr[a]["seconds_newer_than_datum"] == 0
                 for a in ("X2-S", "X4-S", "X2-P", "X4-P")))
    unit("U8 AV1 rebound EXACTLY the registered name `arm_datum` and nothing else -- every "
         "band, threshold and composition rule that decides the verdict is the frozen code",
         a1["names_rebound"] == ["arm_datum"])
    unit("U9 AV1's preserved run root is byte-identical after the re-grade (%d files, md5 "
         "manifest before == after)" % a1["preserved_root_files"], a1["root_manifest_identical"])
    unit("U10 AV1's verdict is from the fixed vocabulary and is whatever the FROZEN "
         "instrument produced (got %r)" % a1["verdict"], a1["verdict"] in VOCAB)

    # ---- AV2 ---------------------------------------------------------------------------
    a2 = regrade("AV2", tmp)
    unit("U11 AV2 re-graded: the ORIGINAL refusal `G1 age_reference_absent` on `X-S/0/U` is "
         "GONE and the datum resolves to `0/U.gz`",
         a2["datum_resolution"] is not None
         and all(v["resolved_name"].endswith(".gz") for k, v in a2["datum_resolution"].items() if k != "MESH")
         and "age_reference_absent" not in (a2["refusal"] or ""))
    unit("U12 AV2 rebound exactly `arm_datum`; preserved root byte-identical; verdict in vocabulary",
         a2["names_rebound"] == ["arm_datum"] and a2["root_manifest_identical"] and a2["verdict"] in VOCAB)

    # ---- AV1R: the PARTITION variant ---------------------------------------------------
    ar = regrade("AV1R", tmp)
    unit("U13 AV1R REBINDS NOTHING -- its grader is not defective and is run completely "
         "unmodified; the repair is in the PRODUCER's reader",
         ar["names_rebound"] == [])
    unit("U14 AV1R partition recovered on all four parallel arms: X2 sums 4032, X4 sums "
         "4032, every processor resolved via `owner.gz`, serial arms still []",
         all(ar["partition_repair"][a]["sum"] == 4032 for a in ("X2-S", "X2-P", "X4-S", "X4-P"))
         and all(v == "owner.gz" for a in ("X2-S", "X4-P") for v in ar["partition_repair"][a]["resolved_names"])
         and ar["partition_repair"]["X1-S"]["after"] == []
         and all(e["nCells"] is None for e in ar["partition_repair"]["X2-S"]["before"]))
    unit("U15 AV1R's preserved run root is byte-identical after the re-grade (%d files) -- "
         "the recovered record was written into the COPY, never the preserved artefact"
         % ar["preserved_root_files"], ar["root_manifest_identical"])
    unit("U16 AV1R's verdict is from the fixed vocabulary (got %r)" % ar["verdict"], ar["verdict"] in VOCAB)

    # ---- BIRTH, MUST-FLAG: a repaired reader must not launder a genuine absence ---------
    b1 = regrade("AV1", tmp, mutate=plant_drop_both_datum_names("X1-S"))
    unit("U17 BIRTH must-FLAG (DATUM): NEITHER `0/U` nor `0/U.gz` on X1-S -> still REFUSED, "
         "on the repaired clause `age_reference_absent_in_every_registered_name`. A repaired "
         "reader that cannot still refuse is not repaired, it is disabled (clause %r)"
         % refusal_clause(b1),
         b1["verdict"] == "NOT A RESULT"
         and "age_reference_absent_in_every_registered_name" in (b1["refusal"] or ""))
    b2 = regrade("AV1", tmp, mutate=plant_age_twin_older("X1-S"))
    unit("U18 BIRTH must-FLAG (DATUM): the compressed twin planted OLDER than the datum -> "
         "REFUSED on `compressed_datum_twin_older_than_the_datum`. The age guard's SUBSTANCE "
         "survives the repair; only the reference PATH was ever wrong (clause %r)"
         % refusal_clause(b2),
         b2["verdict"] == "NOT A RESULT"
         and "compressed_datum_twin_older_than_the_datum" in (b2["refusal"] or ""))
    b3 = regrade("AV1", tmp, mutate=plant_uncompressed_twin_with_wrong_mtime("X1-S"))
    unit("U19 BIRTH must-FLAG (DATUM): an UNCOMPRESSED `0/U` planted beside the real "
         "`0/U.gz` with a wrong mtime -> candidate[0] wins and the EXACT-mtime rule fires "
         "(`age_reference_moved`). Ordering and the uncompressed branch both proved live "
         "(clause %r)" % refusal_clause(b3),
         b3["verdict"] == "NOT A RESULT" and "age_reference_moved" in (b3["refusal"] or ""))
    b4 = regrade("AV1R", tmp, mutate=plant_drop_one_owner("X2-S"))
    unit("U20 BIRTH must-FLAG (PARTITION), TWO plants in one: `owner.gz` deleted from "
         "X2-S/processor0 -> the reader reports `nCells: None` and the FROZEN grader refuses; "
         "and a planted WRONG nCells inside the real gzip moves the sum off 4032 and the "
         "FROZEN grader refuses on that too -- so the reader reads the FILE, not a constant",
         b4["verdict"] == "NOT A RESULT" and "partition_cells" in (b4["refusal"] or "")
         and _wrong_ncells_refuses(tmp))

    print("AVWC SELFTEST units=%d expected=%d failures=%d python_O=%s"
          % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("AVWC SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


def _wrong_ncells_refuses(tmp):
    b = regrade("AV1R", tmp, mutate=plant_wrong_ncells("X4-S"))
    return b["verdict"] == "NOT A RESULT" and "partition_cells" in (b["refusal"] or "")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--item", default=None, choices=sorted(ITEMS))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    for p in (os.path.abspath(__file__), os.path.join(HERE, "avwc_reader.py")):
        if count_asserts(p) != 0:
            print("REFUSAL: %s carries an assert statement (L-332)" % p)
            return 2
    d = os.path.join(a.tmpdir, "avwc_%d" % os.getpid())
    os.makedirs(d, exist_ok=True)
    if a.selftest:
        return selftest(d)
    items = [a.item] if a.item else sorted(ITEMS)
    res = {}
    for it in items:
        try:
            r = regrade(it, d)
        except Refusal as ex:
            r = {"item": it, "verdict": "NOT A RESULT", "successor_refusal": str(ex)}
        r.pop("grade", None)
        res[it] = r
        print("%-5s  ORIGINAL: NOT A RESULT (%s)" % (it, ITEMS[it]["original_refusal"]))
        print("       RE-GRADED: %s   rebound=%s   preserved_root_identical=%s"
              % (r.get("verdict"), r.get("names_rebound"), r.get("root_manifest_identical")))
        if r.get("refusal"):
            print("       refusal clause: %s" % refusal_clause(r))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
