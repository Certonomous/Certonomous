#!/usr/bin/env python3
"""grade_rung0b.py -- THE SUCCESSOR COMPARATOR. It grades §4's conjunction AS WRITTEN.

Registration: `verification/campaign/RUNG0b_MESH_IMPORT_PREREGISTRATION.md`.

WHY A SUCCESSOR AND NOT A REPAIR, WHICH IS THE WHOLE POINT OF THIS FILE.
The predecessor `RUNG0_MESH_IMPORT` (frozen `d127d83d`) graded four of its five gates
and returned `PENDING`, because `R0-G2b`'s writer did not exist when it was frozen.
`cases/committee-grids/foam_to_ugrid.py` now does. The predecessor's comparator,
`verification/runs/RUNG0_MESH_IMPORT_runs/analyse_rung0.py`, IS NOT DEFECTIVE AND IS
NOT REPAIRED: it implements its registration faithfully, it withholds the rung `PASS`
deliberately at its `:512-518` and prints its own reason, and it says so in its header
at `:16-17`. Verification ruled at `f5b8deec` (charter v1.52) that `§2d.1` therefore
HAS NO OBJECT -- the comparator and the registration agree, so there is no departure to
repair -- and REFUSED BY NAME the alternative of striking `R0-G2b`, on the ground that
"a limb becoming runnable is not evidence it was never meant."

**THE PREDECESSOR IS NOT AMENDED AND ITS `PENDING` STANDS AS COMMITTED.** Rung 0 gets
its verdict through the front door: a new registration, a new frozen grading path, and
the same five gates graded as they were always written.

THE STRUCTURAL DEFECT THIS FILE'S LOCATION FIXES, AND IT IS GENERAL.
The predecessor filed its comparator at `verification/runs/RUNG0_MESH_IMPORT_runs/
analyse_rung0.py` -- INSIDE the run root whose ABSENCE was its own pre-compute proof
under rule 2 ("name the run directory that does not exist"). Those two conditions
cannot both hold at one commit: committing the comparator creates the run root, and an
existing run root voids the absence proof. Its queue row therefore read
`ABSENT-AT-FREEZE` and no honest pin existed. **THIS FILE LIVES IN `cases/`, OUTSIDE
ANY RUN ROOT**, so the freeze commit can carry the comparator AND the writer AND the
reader while `verification/runs/RUNG0b_MESH_IMPORT_runs/` does not yet exist. The pin
is derivable. That is a FILING fix, not a gate change.

WHAT IS INSIDE THE GRADING PATH NOW -- all three, named in the registration's FROZEN
PATHS table and in the queue entry's `grading_freeze`:
    cases/committee-grids/grade_rung0b.py        (this file)
    cases/committee-grids/foam_to_ugrid.py       (the writer -- R0-G2b's export limb)
    cases/committee-grids/read_ugrid_identity.py (the independent reader, unmodified)
`ugrid_to_foam.py` is the ARTEFACT UNDER TEST, not part of the grading path.

`R0-G2b`'s `PASS` ON ALL FOUR GRIDS IS AT PRESENT A MEASUREMENT, NOT A VERDICT.
It was taken on 2026-09-03 by `foam_to_ugrid.py --roundtrip`, an instrument OUTSIDE any
frozen grading path, and recorded at
`verification/runs/RUNG0_MESH_IMPORT_runs/R0G2B_DIAGNOSTIC_NOT_A_GRADED_RUN.json`.
**IT BECOMES A VERDICT ONLY WHEN THIS FILE EMITS IT FROM ITS OWN FROZEN PATH.** Nothing
in this file may be read as inheriting that measurement, and this file recomputes it
from scratch rather than citing it.

THE VERDICT VOCABULARY, AND THIS COMPARATOR CAN REACH ALL OF IT.
    PASS         -- R0-G1, R0-G2a, R0-G2b hold on ALL FOUR grids and R0-G3 is complete
                    on all four. THE CONJUNCTION, AS §4 WRITES IT, ALL FIVE GATES.
    GATE FAIL    -- any integer identity fails, or any R0-G3 field is absent.
    NOT A RESULT -- a planted control does not fire.
    BLOCKED      -- a source grid or its `.mapbc` is unreachable.
    PENDING      -- display/queue state only: not yet run.

RULE 3, IN TWO PHASES, BOTH MANDATORY.
    PHASE A, BEFORE ANY CONVERSION, so a failure costs ZERO conversion core-minutes:
      B0  ABSOLUTE -- a hand-built one-hex polyMesh exported and re-read, counts known
          a priori, in BOTH the Fortran and raw-stream layouts.
      B1  rename one `.mapbc` group in a scratch copy -> the new name appears.
      B2  delete one boundary face from a scratch copy of a real grid -> exactly one
          patch drops by exactly 1, cells unchanged.
      B5  `checkMesh` fed BOTH label forms (`=` and `:`) -> a non-null value from each.
      B6  `checkMesh` with Min != Max volume -> a non-trivial derived ratio, never 1.
      B7  an ABSENT `checkMesh` log reads `ABSENT`. IT NEVER READS CLEAN.
      B10 `foam_to_ugrid.py --selftest` exits 0 -- its own 21 controls, run as a
          subprocess, because a writer inside the grading path must carry its battery.
    PHASE B, AFTER CONVERSION AND BEFORE ANY GATE READS A NUMBER:
      B3  +1 on one `nFaces` in a scratch `boundary` -> R0-G2a reports UNEQUAL.
      B4  rename a patch in a scratch `boundary` -> a NAME-SET MISMATCH.
      B8  a header note CONTRADICTING the mesh's own lists -> the reader REFUSES, on
          EVERY distinct label form on disk.
      B9  **THE ONE THE PREDECESSOR COULD NOT RUN.** §7 row 7: drop one face from the
          WRITTEN file -> R0-G2b reports UNEQUAL. It is enforced inside
          `foam_to_ugrid.roundtrip()`, which REFUSES to report an equality it has not
          first been shown able to see fail, and is surfaced here per grid.

A `PASS` reported by a reader whose plant did not fire is `NOT A RESULT`, not a pass.

NO `assert` ANYWHERE (L-332); `_ast_self_check()` parses this file's own source at every
invocation from `main()`. L-459: no verdict line is ever read -- every quality number is
PARSED off its named maximum and `checkMesh`'s own verdict strings are captured into a
field named `verdict_line_IGNORED_NEVER_A_GATE` solely to show they were discarded.

USAGE
    grade_rung0b.py --run-root <root> [--controls-only | --phase-a-only]
Exit 0 = graded (whatever the verdict); 2 = REFUSED / NOT A RESULT.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import read_ugrid_identity as R      # noqa: E402  the independent reader, unmodified
import foam_to_ugrid as W            # noqa: E402  the writer, inside the grading path

EXIT_REFUSE = 2

PREREG = "verification/campaign/RUNG0b_MESH_IMPORT_PREREGISTRATION.md"
PREDECESSOR = "verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md"
PREDECESSOR_FREEZE = "d127d83d4ebf4caaaf0c12c39a063c5f624a03a4"
RULING = "f5b8deec  (verification CHARTER v1.52)"

DPW5 = Path("/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid")
HLPW6 = Path("/home/ubuntu/certonomous-runs/hlpw6-memory-probe/grid")

#: The population is FIXED HERE, not discovered by glob: a comparator that grades
#: whatever it happens to find can be made to pass by deleting the grid that fails.
#: The variant is each grid's OWN source layout, so the round trip exercises both the
#: Fortran-unformatted and the raw-C-stream paths on real data.
GRIDS = (
    ("DPW5_L1T_hex", DPW5 / "L1.T.rev01.p3d.hex.r8.ugrid", DPW5 / "dpw5_L1T.mapbc", "r8"),
    ("DPW5_L1T_prism", DPW5 / "L1.T.rev01.p3d.prism.r8.ugrid", DPW5 / "dpw5_L1T.mapbc", "r8"),
    ("DPW5_L1T_hybrid", DPW5 / "L1.T.rev01.p3d.hybrid.r8.ugrid", DPW5 / "dpw5_L1T.mapbc", "r8"),
    ("HLPW6_h6c1_rans_3a_1", HLPW6 / "h6c1_rans_3a_1.b8.ugrid",
     HLPW6 / "h6c1_rans_3a_1.mapbc", "b8"),
)

#: The written UGRIDs are 37-89 MB each. Data too large for git lives OUTSIDE it
#: (CLAUDE.md, "where things live"); the run root records their paths and sha256.
EXPORT_ROOT = Path("/home/ubuntu/certonomous-runs/RUNG0b_exports")

#: Two real logs on this box, one per `checkMesh` label form. B5's population.
LOG_COLON = REPO / "cases/committee-grids/logs/DPW5_hex_checkMesh.log"
LOG_EQ = REPO / "verification/runs/F24_PRANDTL_MEYER_runs/coarse/log.checkMesh"

#: Every field §4's R0-G3 requires on the birth certificate, NON-NULL.
G3_FIELDS = (
    "cells", "faces", "max_non_orthogonality", "severe_non_ortho_faces",
    "max_skewness", "max_aspect_ratio", "aspect_ratio_flagged", "min_cell_volume",
    "max_cell_volume", "cell_volume_ratio", "geometric_directions", "checkMesh_log",
    "points_sha256", "generator", "created_at", "grid_provenance",
)


_NFACES_LINE = re.compile(r"(\bnFaces\s+)(\d+)(\s*;)")


class Refusal(Exception):
    """A condition that must stop this comparator under any interpreter flag."""


def _ast_self_check(path: Path | None = None) -> int:
    """REFUSE if this file's own source contains an `assert` statement (L-332)."""
    path = Path(path or __file__).resolve()
    try:
        tree = ast.parse(path.read_text(errors="replace"), filename=str(path))
    except SyntaxError as exc:
        raise Refusal(f"L-332 SELF-CHECK: cannot parse {path}: {exc}")
    bad = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if bad:
        raise Refusal(
            f"L-332: {path} contains `assert` at line(s) {bad}. `python3 -O` deletes "
            f"every one of them. Use `raise`.")
    return 0


def _row(control, fired, expected, saw):
    return dict(control=control, fired=fired, expected=expected, saw=str(saw)[:400])


# =========================================================== PHASE A -- pre-conversion
def phase_a(scratch: Path) -> list:
    """Controls that cost ZERO conversion core-minutes, so a failure is free."""
    out = []

    # ---- B10. The writer's own 21 controls, run as a subprocess. --------------------
    p = subprocess.run([sys.executable, str(HERE / "foam_to_ugrid.py"), "--selftest"],
                       capture_output=True, text=True)
    n_fired = p.stdout.count("[       FIRED]")
    out.append(_row(
        "B10 foam_to_ugrid.py --selftest (the writer is INSIDE the grading path, so it "
        "carries its battery here)",
        p.returncode == 0,
        "exit 0 with every control fired",
        f"rc={p.returncode}, {n_fired} FIRED rows, tail: "
        f"{p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-160:]!r}"))

    # ---- B0. ABSOLUTE: a hand-built one-hex mesh, counts known a priori. ------------
    for variant in ("r8", "b8"):
        case = W._build_synth(scratch, f"B0_{variant}", W._SYNTH["hex1"])
        out_ug = scratch / f"B0_{variant}.{variant}.ugrid"
        try:
            info = W.export(case, out_ug)
            back = R.read_source_identity(out_ug, Path(info["mapbc"]))
            fired = (back["cells"] == 1 and info["hex"] == 1
                     and back["patches"] == {"lid": 2, "sides": 4}
                     and back["boundary_faces"] == 6)
            saw = (f"cells {back['cells']}, hex {info['hex']}, {back['patches']}, "
                   f"bnd {back['boundary_faces']}, endian {back['endian']}, "
                   f"fortran {back['fortran']}")
        except (W.Refusal, R.Refusal) as exc:
            fired, saw = False, f"REFUSED: {exc}"
        out.append(_row(
            f"B0 ABSOLUTE one-hex export/re-read, {variant} layout",
            fired, "cells 1, hex 1, {lid:2, sides:4}, bnd 6 -- known a priori", saw))

    src, mapbc = GRIDS[0][1], GRIDS[0][2]
    if not src.is_file() or not mapbc.is_file():
        out.append(_row("B1/B2 source-side plants", False,
                        "the real DPW5 hex grid and its .mapbc are readable",
                        f"BLOCKED: {src} or {mapbc} unreachable"))
        return out

    # ---- B1. Rename one .mapbc group in a scratch copy. -----------------------------
    mb2 = scratch / "B1.mapbc"
    lines = mapbc.read_text(errors="replace").splitlines()
    renamed, planted = [], False
    for ln in lines:
        parts = ln.split()
        if not planted and len(parts) >= 3 and parts[0].lstrip("-").isdigit():
            parts[2] = "PLANTED_GROUP_RENAME"
            planted, ln = True, " ".join(parts)
        renamed.append(ln)
    mb2.write_text("\n".join(renamed) + "\n")
    try:
        got = R.read_source_identity(src, mb2)
        fired = planted and "PLANTED_GROUP_RENAME" in got["patches"]
        saw = f"names {sorted(got['patches'])}"
    except R.Refusal as exc:
        fired, saw = False, f"REFUSED: {exc}"
    out.append(_row("B1 rename one .mapbc group (scratch copy)", fired,
                    "the renamed patch appears in the emitted name set", saw))

    # ---- B2. Delete one boundary face from a scratch copy of the REAL grid. ---------
    # The plant CHECKS ITS OWN BYTE ARITHMETIC inside `drop_one_boundary_face` and
    # refuses if the file did not actually shrink by one face. A control that quietly
    # does nothing certifies a reader that can see nothing.
    try:
        clean = R.read_source_identity(src, mapbc)
        dst = scratch / f"B2{''.join(src.suffixes[-2:])}"
        plant = W.drop_one_boundary_face(src, dst)
        after = R.read_source_identity(dst, mapbc)
        drops = {k: clean["patches"][k] - after["patches"].get(k, 0)
                 for k in clean["patches"]}
        fired = (sorted(drops.values()) == [0] * (len(drops) - 1) + [1]
                 and clean["cells"] == after["cells"])
        saw = (f"per-patch drop {drops}, bnd {clean['boundary_faces']} -> "
               f"{after['boundary_faces']}, cells {clean['cells']} -> {after['cells']}, "
               f"plant removed {plant['bytes_removed']} bytes ({plant['kind']})")
    except (R.Refusal, W.Refusal) as exc:
        fired, saw = False, f"REFUSED: {exc}"
    out.append(_row("B2 delete one boundary face (scratch copy of the real grid)",
                    fired,
                    "exactly one patch's face count drops by exactly 1; cells unchanged",
                    saw))

    # ---- B5/B6/B7. The checkMesh reader. L-459 -- numbers, never verdict lines. -----
    forms = {}
    for label, log in (("=", LOG_EQ), (":", LOG_COLON)):
        q = R.read_checkmesh_quality(log) if log.is_file() else {"state": "ABSENT"}
        forms[label] = q
    fired = all(forms[k].get("max_aspect_ratio") is not None for k in ("=", ":"))
    out.append(_row(
        "B5 checkMesh fed BOTH aspect-ratio label forms",
        fired,
        "a NON-NULL max aspect ratio from EACH form -- a reader matching only `=` sees "
        "the healthy logs and silently misses exactly the pathological ones",
        {k: (forms[k].get("max_aspect_ratio"), forms[k].get("aspect_ratio_label_form"))
         for k in ("=", ":")}))

    q = forms[":"]
    lo, hi, ratio = (q.get("min_cell_volume"), q.get("max_cell_volume"),
                     q.get("cell_volume_ratio"))
    fired = (lo is not None and hi is not None and lo != hi
             and ratio is not None and ratio != 1)
    out.append(_row("B6 a log with Min volume != Max volume", fired,
                    "a NON-TRIVIAL derived cell-volume ratio, never 1",
                    f"min {lo}, max {hi}, ratio {ratio}"))

    absent = R.read_checkmesh_quality(scratch / "no_such.log")
    fired = (absent.get("state") == "ABSENT"
             and absent.get("max_non_orthogonality") is None)
    out.append(_row("B7 an ABSENT checkMesh log", fired,
                    "state ABSENT and NO number. ABSENT NEVER READS CLEAN.",
                    f"state {absent.get('state')!r}, keys {sorted(absent)}"))
    return out


# ========================================================== PHASE B -- post-conversion
def phase_b(scratch: Path, cases: list) -> list:
    """Controls that need a polyMesh. They run BEFORE any gate reads a number."""
    out = []
    donors = [c for c in cases if (c / "constant/polyMesh/boundary").is_file()]
    if not donors:
        return [_row("B3/B4/B8 polyMesh plants", False,
                     "at least one converted polyMesh to plant into",
                     "NOT RUN -- no polyMesh is on disk. Reported, never skipped.")]
    donor = donors[0]

    def _scratch_case(tag):
        c = scratch / tag
        (c / "constant/polyMesh").mkdir(parents=True, exist_ok=True)
        for f in ("owner", "neighbour", "boundary"):
            shutil.copy2(donor / "constant/polyMesh" / f, c / "constant/polyMesh" / f)
        return c

    # ---- B3. +1 on one nFaces. -----------------------------------------------------
    c = _scratch_case("B3")
    b = c / "constant/polyMesh/boundary"
    before = R.read_polymesh_identity(donor)["patches"]
    txt = b.read_text()
    new, n = _NFACES_LINE.subn(
        lambda m: f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}", txt, count=1)
    if n != 1 or new == txt:
        raise Refusal(
            f"B3 PLANT DID NOT PLANT: {n} nFaces substitution(s) in {b}. REFUSED -- a "
            f"control that quietly does nothing certifies a reader that can see "
            f"nothing (rule 3).")
    b.write_text(new)
    after = R.read_polymesh_identity(c)["patches"]
    fired = n == 1 and after != before and sum(after.values()) == sum(before.values()) + 1
    out.append(_row("B3 +1 on one nFaces (scratch polyMesh)", fired,
                    "R0-G2a reports UNEQUAL, not equal",
                    f"{before} -> {after}"))

    # ---- B4. Rename a patch. -------------------------------------------------------
    c = _scratch_case("B4")
    b = c / "constant/polyMesh/boundary"
    first = sorted(before)[0]
    b.write_text(b.read_text().replace(f"    {first}\n", "    PLANTED_PATCH\n", 1))
    after = R.read_polymesh_identity(c)["patches"]
    fired = "PLANTED_PATCH" in after and first not in after
    out.append(_row("B4 rename one patch (scratch polyMesh)", fired,
                    "R0-G2a reports a NAME-SET MISMATCH",
                    f"{sorted(before)} -> {sorted(after)}"))

    # ---- B8. A header note contradicting the mesh's own lists must REFUSE, on EVERY
    # distinct label form on disk. A control planted into only one form would certify a
    # reader that still could not see the other.
    seen = set()
    for i, d in enumerate(donors):
        clean = R.read_polymesh_identity(d)
        form = clean.get("header_note_form") or "no header note"
        if form in seen:
            continue
        seen.add(form)
        c = _scratch_case(f"B8_{i}")
        own = c / "constant/polyMesh/owner"
        head, sep, rest = own.read_text(errors="replace").partition("\n(")
        bad = head.replace(f"nCells:{clean['cells']}", f"nCells:{clean['cells'] + 1}", 1)
        planted = bad != head
        own.write_text(bad + sep + rest)
        try:
            R.read_polymesh_identity(c)
            fired, saw = False, "the reader ACCEPTED a header contradicting the mesh"
        except R.Refusal as exc:
            fired, saw = planted and "CONTRADICTS" in str(exc), str(exc)
        out.append(_row(
            f"B8 a header note contradicting the mesh's own lists [{form} form]",
            fired,
            f"nCells {clean['cells']} -> {clean['cells'] + 1} in the header alone must "
            f"REFUSE, never be preferred over the lists", saw))
    return out


# ================================================================== the five gates
def grade_grid(name, ugrid, mapbc, variant, case: Path, root_epoch: float) -> dict:
    """R0-G1, R0-G2a, **R0-G2b**, R0-G3 and R0-G4 for ONE grid. ALL FIVE ARE GRADED."""
    g = dict(grid=name, source=str(ugrid), case=str(case))
    try:
        src = R.read_source_identity(ugrid, mapbc)
    except R.Refusal as exc:
        return dict(g, verdict="BLOCKED", why=f"source unreadable: {exc}")
    try:
        foam = R.read_polymesh_identity(case)
    except R.Refusal as exc:
        return dict(g, verdict="GATE FAIL", why=f"imported polyMesh unreadable: {exc}")

    log = case / "log.checkMesh"
    q = R.read_checkmesh_quality(log)
    g["source_reading"], g["polymesh_reading"], g["quality_reading"] = src, foam, q

    # ---- R0-G1 ---------------------------------------------------------------------
    g1 = {
        "n_patches_equals_distinct_mapbc_names":
            foam["n_patches"] == src["distinct_mapbc_names"],
        "patch_names_set_equal": set(foam["patches"]) == set(src["patches"]),
        "defaultFaces_absent": not foam["default_faces_present"],
        "boundary_face_sum_equals_source":
            sum(foam["patches"].values()) == src["boundary_faces"],
    }
    g["R0_G1"] = dict(checks=g1, verdict="PASS" if all(g1.values()) else "GATE FAIL")

    # ---- R0-G2a. INTEGERS. No tolerance. -------------------------------------------
    mism = {k: (src["patches"].get(k), foam["patches"].get(k))
            for k in set(src["patches"]) | set(foam["patches"])
            if src["patches"].get(k) != foam["patches"].get(k)}
    g2a = {"cell_count_exact": src["cells"] == foam["cells"],
           "patch_names_set_equal": set(foam["patches"]) == set(src["patches"]),
           "per_patch_face_counts_exact": not mism}
    g["R0_G2a"] = dict(checks=g2a, per_patch_mismatches=mism,
                       source_cells=src["cells"], imported_cells=foam["cells"],
                       verdict="PASS" if all(g2a.values()) else "GATE FAIL")

    # ---- R0-G2b. THE LIMB THE PREDECESSOR COULD NOT RUN. IT RUNS HERE. -------------
    # `W.roundtrip` exports, re-reads with the SAME independent reader, and REFUSES to
    # report an equality until its own C9 plant -- drop one face from the written file
    # -- has been seen to make that same comparison unequal. B9 is that plant, and it
    # is surfaced per grid rather than folded into the gate.
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    out_ug = EXPORT_ROOT / f"{name}.{variant}.ugrid"
    try:
        rt = W.roundtrip(case, ugrid, mapbc, out_ug, overwrite=True)
    except (W.Refusal, R.Refusal) as exc:
        g["R0_G2b"] = dict(verdict="GATE FAIL", why=f"round trip refused: {exc}")
        g["B9"] = _row("B9 round-trip plant (§7 row 7)", False,
                       "drop one face from the written file -> R0-G2b UNEQUAL",
                       f"REFUSED before the plant could be read: {exc}")
    else:
        g["R0_G2b"] = dict(
            checks=rt["R0_G2b"]["checks"],
            per_patch_mismatches=rt["R0_G2b"]["per_patch_mismatches"],
            source_cells=rt["R0_G2b"]["source_cells"],
            written_cells=rt["R0_G2b"]["written_cells"],
            written=dict(ugrid=rt["written"]["ugrid"], mapbc=rt["written"]["mapbc"],
                         bytes=rt["written"]["bytes"], variant=rt["written"]["variant"],
                         elements_verified=rt["written"]["elements_verified"],
                         mapbc_groups=rt["written"]["mapbc_groups"],
                         mapbc_group_note=rt["written"]["mapbc_group_note"]),
            verdict=rt["R0_G2b"]["verdict"])
        g["B9"] = _row("B9 round-trip plant (§7 row 7) -- THE CONTROL THE PREDECESSOR "
                       "RECORDED AS UNBUILT",
                       rt["C9"]["fired"],
                       "drop one face from the written file -> R0-G2b UNEQUAL",
                       rt["C9"]["saw"])

    # ---- R0-G3. REPORTED, NOT GATED. Fails ONLY on a MISSING number. ---------------
    cert = dict(q)
    cert.update(
        points_sha256=_sha256(case / "constant/polyMesh/points"),
        generator="cases/committee-grids/ugrid_to_foam.py",
        created_at=_iso(case / "constant/polyMesh/owner"),
        grid_provenance="workshop committee family, quality as published",
        published_quality_comparison=(
            "no published quality figure located -- searched the grid's own "
            "distribution directory on this box and no max non-orthogonality, skewness "
            "or aspect-ratio figure is published there. §4 gates this comparison on "
            "being MADE, not on agreeing. NEVER silence, NEVER a blank."),
        non_orthogonality_gate_deg=70,
        quality_reporting_mode="REPORTED, NOT GATED (MESH_STANDARD §11.4)",
        roundtrip_export=str(out_ug),
        roundtrip_export_sha256=_sha256(out_ug),
    )
    missing = [f for f in G3_FIELDS if cert.get(f) is None]
    g["R0_G3"] = dict(missing_fields=missing,
                      verdict="PASS" if not missing else "GATE FAIL")
    g["birth_certificate"] = cert

    # ---- R0-G4. THE AGE GUARD. -----------------------------------------------------
    stale = []
    for p in (case / "constant/polyMesh/owner", case / "constant/polyMesh/boundary",
              case / "constant/polyMesh/faces", case / "constant/polyMesh/points", log):
        if not p.is_file():
            stale.append(f"{p.name}: ABSENT")
        elif p.stat().st_mtime <= root_epoch:
            stale.append(f"{p.name}: mtime {p.stat().st_mtime} <= root stamp {root_epoch}")
    g["R0_G4"] = dict(root_epoch=root_epoch, stale_or_absent=stale,
                      verdict="PASS" if not stale else "GATE FAIL")

    # ---- THE CONJUNCTION, AS §4 WRITES IT. ALL FIVE GATES. -------------------------
    per = [g[k]["verdict"] for k in
           ("R0_G1", "R0_G2a", "R0_G2b", "R0_G3", "R0_G4")]
    if "GATE FAIL" in per:
        g["verdict"] = "GATE FAIL"
    elif "PENDING" in per:
        g["verdict"] = "PENDING"
    else:
        g["verdict"] = "PASS"
    g["verdict_basis"] = (
        "§4: PASS -- R0-G1, R0-G2a, R0-G2b hold and R0-G3 is complete. The conjunction "
        f"over ALL FIVE gates, evaluated in full: {dict(zip(('R0_G1','R0_G2a','R0_G2b','R0_G3','R0_G4'), per))}")
    return g


def _sha256(p: Path):
    import hashlib
    if not Path(p).is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _iso(p: Path):
    import datetime
    if not Path(p).is_file():
        return None
    return datetime.datetime.fromtimestamp(
        Path(p).stat().st_mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================================== main
def _print_controls(rows, header):
    print(header)
    for c in rows:
        mark = {True: "FIRED", False: "DID NOT FIRE", None: "NOT RUN"}[c["fired"]]
        print(f"  [{mark:>12}] {c['control']}")
        print(f"                 expected: {c['expected']}")
        print(f"                 saw     : {c['saw']}")


def main(argv):
    _ast_self_check()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--controls-only", action="store_true",
                    help="phase A only; no conversion is graded and no verdict claimed")
    a = ap.parse_args(argv)
    root = Path(a.run_root)

    scratch = Path(tempfile.mkdtemp(prefix="rung0b_controls_"))
    try:
        try:
            a_rows = phase_a(scratch)
        except (R.Refusal, W.Refusal) as exc:
            print(f"REFUSED in phase A: {exc}", file=sys.stderr)
            return EXIT_REFUSE
        _print_controls(a_rows, "=== PHASE A CONTROLS (rule 3; before any conversion) ===")
        if [c for c in a_rows if c["fired"] is False]:
            print("\nNOT A RESULT: a phase-A control did not fire. Every number this "
                  "comparator could print is worthless until they do (rule 3). REFUSED "
                  "at exit 2; NO CONVERSION CORE-MINUTES WERE SPENT.")
            return EXIT_REFUSE
        if a.controls_only:
            print("\ncontrols-only: no grid was graded, no verdict is claimed.")
            return 0

        stamp = root / "RUN_ROOT_CREATED_EPOCH"
        if not stamp.is_file():
            print(f"REFUSED: {stamp} is absent, so R0-G4's age guard has no datum. "
                  f"Rule 4: refuse, never degrade.", file=sys.stderr)
            return EXIT_REFUSE
        root_epoch = float(stamp.read_text().split()[0])

        cases = [root / n for n, *_ in GRIDS if (root / n).is_dir()]
        try:
            b_rows = phase_b(scratch, cases)
        except (R.Refusal, W.Refusal) as exc:
            print(f"REFUSED in phase B: {exc}", file=sys.stderr)
            return EXIT_REFUSE
        _print_controls(b_rows, "\n=== PHASE B CONTROLS (rule 3; before any gate reads "
                                "a number) ===")
        if [c for c in b_rows if c["fired"] is False]:
            print("\nNOT A RESULT: a phase-B control did not fire. REFUSED at exit 2.")
            return EXIT_REFUSE
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    results, per_grid = [], {}
    for name, ug, mb, variant in GRIDS:
        case = root / name
        if not case.is_dir():
            results.append(dict(grid=name, verdict="BLOCKED",
                                why=f"case directory {case} absent -- not converted"))
        else:
            results.append(grade_grid(name, ug, mb, variant, case, root_epoch))
        per_grid[name] = results[-1]["verdict"]
        cert = results[-1].get("birth_certificate")
        if cert is not None:
            (case / "birth_certificate.json").write_text(
                json.dumps(cert, indent=2, sort_keys=True, default=str))

    b9 = [r["B9"] for r in results if "B9" in r]
    print("\n=== PER-GRID READING ===")
    for r in results:
        print(f"  {r['grid']:24s} {r['verdict']}")
        for k in ("R0_G1", "R0_G2a", "R0_G2b", "R0_G3", "R0_G4"):
            if k in r:
                print(f"      {k:7s} {r[k]['verdict']}")
        q = r.get("quality_reading") or {}
        if q.get("max_non_orthogonality") is not None:
            print(f"      quality REPORTED NOT GATED: max non-orth "
                  f"{q['max_non_orthogonality']} deg (70 deg generation gate), severe "
                  f"{q['severe_non_ortho_faces']}, skew {q['max_skewness']}, AR "
                  f"{q['max_aspect_ratio']} ({q['aspect_ratio_label_form']} form), "
                  f"cell-volume ratio {q['cell_volume_ratio']:.4g} DERIVED")
    _print_controls(b9, "\n=== B9, THE ROUND-TRIP PLANT, PER GRID ===")

    if [c for c in b9 if c["fired"] is not True]:
        rung = "NOT A RESULT"
        why = ("B9 did not fire on every grid. R0-G2b's equality is a zero from a "
               "reader not shown able to see a non-zero, and rule 3 makes it NOT A "
               "RESULT rather than a pass.")
    else:
        verdicts = set(per_grid.values())
        if "GATE FAIL" in verdicts:
            rung, why = "GATE FAIL", "at least one grid failed a registered gate."
        elif "BLOCKED" in verdicts:
            rung, why = "BLOCKED", "at least one source grid was unreachable."
        elif "PENDING" in verdicts:
            rung, why = "PENDING", "at least one gate was not evaluated."
        else:
            rung = "PASS"
            why = ("§4's conjunction holds on ALL FOUR grids across ALL FIVE gates, "
                   "R0-G2b included and graded from this frozen path rather than "
                   "inherited from any earlier measurement.")
    print(f"\n=== RUNG 0b VERDICT: {rung} ===")
    print(why)
    print(f"Predecessor {PREDECESSOR} (frozen {PREDECESSOR_FREEZE}) is NOT amended and "
          f"its PENDING stands as committed. Authority for the successor route: {RULING}.")

    out = dict(case_id="RUNG0b_MESH_IMPORT", prereg=PREREG,
               predecessor=PREDECESSOR, predecessor_freeze=PREDECESSOR_FREEZE,
               ruling=RULING, rung_verdict=rung, rung_verdict_why=why,
               per_grid=per_grid, controls_phase_a=a_rows, controls_phase_b=b_rows,
               controls_B9=b9, results=results, root_epoch=root_epoch)
    (root / "RESULTS.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\nwritten: {root / 'RESULTS.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
