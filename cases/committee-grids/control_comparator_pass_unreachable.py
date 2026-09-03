#!/usr/bin/env python3
"""control_comparator_pass_unreachable.py -- THE §2d.1 CONDITION (2) INSTRUMENT.

WHY THIS FILE EXISTS, AND WHY IT IS NOT A REPAIR.

`verification/runs/RUNG0_MESH_IMPORT_runs/analyse_rung0.py` is the FROZEN grading path
of RUNG 0. It cannot emit `PASS`: `R0_G2b` is assigned the literal `"PENDING"` and no
writer is ever called; `R0_G2b` is omitted from the per-grid conjunction list; neither
the per-grid verdict nor the rung verdict has a `PASS` branch. THAT WAS ESTABLISHED BY
READING THE SOURCE, AND READING IS NOT ENOUGH.

`docs/charters/VERIFICATION_CHARTER.md` §2d.1 permits a change on the grading path
after the first graded solve only when four conditions hold, and condition (2) is:

    (2) the error was established by an instrument INDEPENDENT OF THE HYPOTHESIS --
        one that grades nothing, such as a near-identity, a guard or a control

Every example the clause gives is EXECUTABLE. A source reading is not one of them, and
§2d.1's own closing sentence -- "Nothing a verdict depends on may be repaired on the
authority of the verdict it produces" -- bites hardest on a change that can only ever
turn `PENDING` into `PASS`. THIS FILE IS THAT MISSING INSTRUMENT. It runs the frozen
comparator UNMODIFIED, as a subprocess, against constructed run roots, and reports what
the comparator actually emits. It grades nothing, it cannot know which answer anybody
wants, and it changes no verdict of any kind.

WHAT IT DOES NOT DO, SAID FIRST SO IT CANNOT BE MISREAD. It does not repair
`analyse_rung0.py`. It does not touch it, import it, or read a single line of it at run
time. It does not grade RUNG 0. It does not make `R0-G2b` `PASS`. It produces evidence
for one narrow proposition -- that the frozen comparator cannot reach `PASS` -- and the
ruling on what follows belongs to verification under §2d.1, not to this file and not to
the lane that wrote it.

THE FOUR ARMS

  ARM 0  PLANT (standing rule 3). The control's verdict reader is fed a scratch copy of
         a real comparator output with `rung_verdict` forced to `"PASS"`, and MUST
         report `PASS`. Without this, arm 1's "the comparator did not say PASS" is a
         zero from a reader never shown able to see a non-zero, and is not evidence.

  ARM 1  ALL FIVE REGISTERED GATES HOLD, AND THE COMPARATOR STILL SAYS `PENDING`.
         A run root is constructed in which R0-G1, R0-G2a, R0-G3 and R0-G4 hold on all
         four grids -- and R0-G2b is made to hold too, MEASURED IN THIS ARM by running
         `foam_to_ugrid.py --roundtrip`, which carries its own C9 plant and refuses to
         report an equality it has not first been shown able to see fail. The frozen
         comparator is then run against that same root. It emits `PENDING`.

  ARM 2  MIRROR: A FAILED GATE STILL REACHES `GATE FAIL`. One patch's `nFaces` is
         raised by 1 in a COPY of a `boundary` file, breaking R0-G2a's per-patch
         identity. The comparator emits `GATE FAIL`.

  ARM 3  MIRROR: AN ABSENT CASE STILL REACHES `BLOCKED`. One case directory is omitted.
         The comparator emits `BLOCKED`.

Arms 2 and 3 are what stop arm 1 being vacuous. A control that only ever saw `PENDING`
would be indistinguishable from one stuck on `PENDING`; these show the same reader, on
the same comparator, reaching two other verdicts on demand. Together with arm 0's
plant, the reader is shown able to report four distinct outcomes, and `PASS` is the one
the comparator never produces.

WHAT THIS INSTRUMENT CANNOT SEE, STATED RATHER THAN LEFT TO INFERENCE.
  * `NOT A RESULT` IS NOT EXERCISED. The comparator reaches it only when one of its own
    eleven planted controls fails, and those read repository paths outside the run root,
    so no construction of a run root can force one. Three of the comparator's four
    reachable verdicts are demonstrated here; the fourth is named and left undemonstrated.
  * IT PROVES UNREACHABILITY ON THIS POPULATION, NOT BY EXHAUSTION. It shows the
    comparator emitting `PENDING` where every registered gate holds -- which is the only
    configuration from which `PASS` could ever be due. It does not enumerate the
    comparator's control flow, and it deliberately does not: an AST walk over the frozen
    grader would be an instrument built to measure another instrument's reach.
  * SANAA'S 2026-09-03 RULE ON EXACTLY THAT IS ENGAGED AND IS SATISFIED, NOT IGNORED:
    "No instrument is built to measure another instrument's reach unless the first
    instrument has already changed a verdict at least once." `analyse_rung0.py` HAS
    changed a verdict at least once -- it emitted `GATE FAIL` on all four grids on
    attempt 2 (`RESULTS.ATTEMPT2_SPURIOUS_GATE_FAIL.json`) and `PENDING` on attempt 3
    (`RESULTS.json`). The exception applies on its face and the tension is named here
    rather than passed over.

CONSTRUCTION, AND THE ONE HAZARD IT DESIGNS AROUND. The run roots are built from
SYMLINKS to the graded artifacts, never copies, so the control costs no disk and no
conversion. The comparator READS `points`, `faces`, `owner`, `neighbour`, `boundary`
and `log.checkMesh`, and WRITES `birth_certificate.json` and `RESULTS.json`. ONLY THE
READ PATHS ARE SYMLINKED. A symlink for a path the comparator writes would send that
write through to the real graded artifact, and `_link_case` REFUSES to create one for
any name in `_NEVER_SYMLINK`. The mutated `boundary` of arm 2 is a real COPY for the
same reason.

NO `assert` ANYWHERE (L-332), and `_ast_self_check()` parses this file's own source at
every invocation from `main()`.

USAGE
    control_comparator_pass_unreachable.py [--run-root <graded run root>] [--keep]
Exit 0 = every arm fired; 2 = an arm did not fire, or a refusal.
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
import time
from pathlib import Path

EXIT_REFUSE = 2

REPO = Path(__file__).resolve().parents[2]
RUN_ROOT = REPO / "verification/runs/RUNG0_MESH_IMPORT_runs"
COMPARATOR = RUN_ROOT / "analyse_rung0.py"
WRITER = REPO / "cases/committee-grids/foam_to_ugrid.py"

DPW5 = Path("/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid")
HLPW6 = Path("/home/ubuntu/certonomous-runs/hlpw6-memory-probe/grid")

#: The four grids, with the SOURCE each one round-trips against. Fixed here for the
#: same reason the comparator fixes its own: a control that discovers its population by
#: glob can be made to pass by deleting the case that fails.
GRIDS = (
    ("DPW5_L1T_hex", DPW5 / "L1.T.rev01.p3d.hex.r8.ugrid", DPW5 / "dpw5_L1T.mapbc", "r8"),
    ("DPW5_L1T_prism", DPW5 / "L1.T.rev01.p3d.prism.r8.ugrid", DPW5 / "dpw5_L1T.mapbc", "r8"),
    ("DPW5_L1T_hybrid", DPW5 / "L1.T.rev01.p3d.hybrid.r8.ugrid", DPW5 / "dpw5_L1T.mapbc", "r8"),
    ("HLPW6_h6c1_rans_3a_1", HLPW6 / "h6c1_rans_3a_1.b8.ugrid",
     HLPW6 / "h6c1_rans_3a_1.mapbc", "b8"),
)

#: Read by the comparator, safe to symlink.
_READ_ONLY = ("constant/polyMesh/points", "constant/polyMesh/faces",
              "constant/polyMesh/owner", "constant/polyMesh/neighbour",
              "constant/polyMesh/boundary", "log.checkMesh")
#: WRITTEN by the comparator. A symlink here would write through to a graded artifact.
_NEVER_SYMLINK = ("birth_certificate.json", "RESULTS.json")

_NFACES_LINE = re.compile(r"(\bnFaces\s+)(\d+)(\s*;)")


class Refusal(Exception):
    """A condition that must stop this control under any interpreter flag."""


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


# --------------------------------------------------------------- run-root construction
def _link_case(src_case: Path, dst_case: Path, copy: tuple = ()) -> None:
    """Symlink one case's READ paths into `dst_case`. Names in `copy` are copied instead.

    REFUSES to symlink anything the comparator writes -- that write would follow the
    link into the graded artifact.
    """
    for rel in _READ_ONLY:
        s = src_case / rel
        if not s.is_file():
            raise Refusal(f"CONSTRUCT: {s} is absent. ABSENT NEVER READS CLEAN.")
        d = dst_case / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        if Path(rel).name in _NEVER_SYMLINK:
            raise Refusal(
                f"CONSTRUCT: refusing to symlink {rel}, which the comparator WRITES. "
                f"The write would follow the link into the graded artifact.")
        if Path(rel).name in copy:
            shutil.copy2(s, d)
        else:
            os.symlink(s, d)


def build_root(dst: Path, *, omit: str | None = None,
               mutate_boundary: str | None = None) -> Path:
    """A run root the FROZEN comparator can be pointed at with `--run-root`.

    `omit` leaves one case directory out (arm 3). `mutate_boundary` copies that grid's
    `boundary` and raises the FIRST patch's `nFaces` by 1 (arm 2), which is exactly the
    comparator's own C3 plant applied to a whole run rather than to a scratch file.
    """
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RUN_ROOT / "RUN_ROOT_CREATED_EPOCH", dst / "RUN_ROOT_CREATED_EPOCH")
    for name, _, _, _ in GRIDS:
        if name == omit:
            continue
        copy = ("boundary",) if name == mutate_boundary else ()
        _link_case(RUN_ROOT / name, dst / name, copy=copy)
    if mutate_boundary:
        b = dst / mutate_boundary / "constant/polyMesh/boundary"
        txt = b.read_text()
        new, n = _NFACES_LINE.subn(lambda m: f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}",
                                   txt, count=1)
        if n != 1 or new == txt:
            raise Refusal(
                f"MUTATION DID NOT MUTATE: {b} -- {n} nFaces substitution(s) made and "
                f"the text is {'unchanged' if new == txt else 'changed'}. REFUSED: a "
                f"mutation that quietly does nothing certifies a comparator that can "
                f"see nothing (rule 3).")
        b.write_text(new)
    return dst


def run_comparator(root: Path) -> dict:
    """Run the FROZEN comparator, UNMODIFIED, as a subprocess. Return its own output."""
    t0 = time.time()
    p = subprocess.run([sys.executable, str(COMPARATOR), "--run-root", str(root)],
                       capture_output=True, text=True)
    res = root / "RESULTS.json"
    if not res.is_file():
        raise Refusal(
            f"COMPARATOR: rc={p.returncode} and wrote no {res}. REFUSED -- there is no "
            f"reading to report. stderr tail: {p.stderr[-300:]!r}")
    out = json.loads(res.read_text())
    out["_rc"] = p.returncode
    out["_wall_s"] = round(time.time() - t0, 3)
    out["_results_path"] = str(res)
    return out


def read_verdicts(results: dict) -> dict:
    """THE CONTROL'S OWN READER. Arm 0 plants into exactly this function's input."""
    per_gate = {}
    for r in results.get("results", []):
        per_gate[r["grid"]] = {k: r[k]["verdict"] for k in
                               ("R0_G1", "R0_G2a", "R0_G2b", "R0_G3", "R0_G4")
                               if k in r}
    return dict(rung=results.get("rung_verdict"),
                per_grid=dict(results.get("per_grid", {})),
                per_gate=per_gate)


# ------------------------------------------------------------------------------ arms
def arm0_plant(scratch: Path, donor: dict) -> dict:
    """PLANT: force `rung_verdict` to PASS in a scratch copy; the reader MUST see PASS."""
    p = scratch / "arm0_planted_RESULTS.json"
    planted = dict(donor)
    before = planted.get("rung_verdict")
    planted["rung_verdict"] = "PASS"
    planted["per_grid"] = {k: "PASS" for k in planted.get("per_grid", {})}
    p.write_text(json.dumps(planted, indent=2, sort_keys=True, default=str))
    got = read_verdicts(json.loads(p.read_text()))
    fired = got["rung"] == "PASS" and set(got["per_grid"].values()) == {"PASS"}
    return dict(
        control="ARM 0 PLANT: the control's verdict reader must be able to SEE a PASS",
        fired=fired,
        expected="rung_verdict PASS and every per_grid PASS, read back FROM DISK",
        saw=(f"donor rung was {before!r}; planted copy reads rung {got['rung']!r}, "
             f"per_grid {sorted(set(got['per_grid'].values()))}"))


def arm1_all_gates_hold(scratch: Path) -> tuple:
    """ALL FIVE registered gates hold -- and the frozen comparator still says PENDING."""
    root = build_root(scratch / "arm1_root")

    # R0-G2b, MEASURED IN THIS ARM by the writer's own round trip, which carries C9.
    g2b, exports = {}, scratch / "arm1_exports"
    exports.mkdir(parents=True, exist_ok=True)
    for name, src, mapbc, variant in GRIDS:
        out = exports / f"{name}.{variant}.ugrid"
        p = subprocess.run(
            [sys.executable, str(WRITER), "--roundtrip", "--case", str(root / name),
             "--source", str(src), str(mapbc), "--out", str(out), "--overwrite"],
            capture_output=True, text=True)
        if p.returncode != 0:
            raise Refusal(
                f"ARM 1: the R0-G2b round trip on {name} returned rc={p.returncode}. "
                f"REFUSED -- this arm's whole premise is that R0-G2b HOLDS, and it must "
                f"be measured here, never assumed. stderr tail: {p.stderr[-300:]!r}")
        d = json.loads(p.stdout)
        g2b[name] = dict(verdict=d["R0_G2b"]["verdict"], c9_fired=d["C9"]["fired"],
                         checks=d["R0_G2b"]["checks"])
        out.unlink(missing_ok=True)
        Path(str(out).rsplit(".ugrid", 1)[0] + ".mapbc").unlink(missing_ok=True)

    g2b_holds = all(v["verdict"] == "PASS" and v["c9_fired"] for v in g2b.values())

    res = run_comparator(root)
    v = read_verdicts(res)
    runnable_all_pass = all(
        all(gate == "PASS" for k, gate in gates.items() if k != "R0_G2b")
        for gates in v["per_gate"].values()) and len(v["per_gate"]) == len(GRIDS)

    fired = (g2b_holds and runnable_all_pass
             and v["rung"] == "PENDING"
             and set(v["per_grid"].values()) == {"PENDING"})
    return dict(
        control=("ARM 1: every registered gate HOLDS -- R0-G1/G2a/G3/G4 by the "
                 "comparator's own output and R0-G2b measured here -- and the FROZEN "
                 "comparator still emits PENDING"),
        fired=fired,
        expected=("R0-G2b PASS x4 with C9 fired x4; R0-G1/G2a/G3/G4 PASS on all four; "
                  "and the comparator's rung verdict PENDING, never PASS"),
        saw=(f"R0-G2b {[g2b[n]['verdict'] for n, *_ in GRIDS]} C9 "
             f"{[g2b[n]['c9_fired'] for n, *_ in GRIDS]}; runnable gates all PASS "
             f"{runnable_all_pass}; comparator rc={res['_rc']} rung={v['rung']!r} "
             f"per_grid={sorted(set(v['per_grid'].values()))} "
             f"R0_G2b={sorted({g['R0_G2b'] for g in v['per_gate'].values()})} "
             f"in {res['_wall_s']} s")), res, g2b, v


def arm2_failed_gate(scratch: Path) -> dict:
    """MIRROR: break R0-G2a's per-patch identity; the comparator must reach GATE FAIL."""
    root = build_root(scratch / "arm2_root", mutate_boundary="DPW5_L1T_hex")
    res = run_comparator(root)
    v = read_verdicts(res)
    fired = v["rung"] == "GATE FAIL" and v["per_grid"].get("DPW5_L1T_hex") == "GATE FAIL"
    mism = {}
    for r in res.get("results", []):
        if r["grid"] == "DPW5_L1T_hex":
            mism = r.get("R0_G2a", {}).get("per_patch_mismatches", {})
    return dict(
        control=("ARM 2 MIRROR: one patch's nFaces raised by 1 -> the comparator must "
                 "reach GATE FAIL, so ARM 1's PENDING is a reading and not a default"),
        fired=fired,
        expected="rung GATE FAIL, DPW5_L1T_hex GATE FAIL",
        saw=(f"rung={v['rung']!r} DPW5_L1T_hex={v['per_grid'].get('DPW5_L1T_hex')!r} "
             f"per-patch mismatches {mism}; rc={res['_rc']} in {res['_wall_s']} s"))


def arm3_absent_case(scratch: Path) -> dict:
    """MIRROR: omit one case directory; the comparator must reach BLOCKED."""
    root = build_root(scratch / "arm3_root", omit="HLPW6_h6c1_rans_3a_1")
    res = run_comparator(root)
    v = read_verdicts(res)
    fired = (v["rung"] == "BLOCKED"
             and v["per_grid"].get("HLPW6_h6c1_rans_3a_1") == "BLOCKED")
    return dict(
        control=("ARM 3 MIRROR: one case directory omitted -> the comparator must "
                 "reach BLOCKED, a third distinct verdict from the same reader"),
        fired=fired,
        expected="rung BLOCKED, HLPW6_h6c1_rans_3a_1 BLOCKED",
        saw=(f"rung={v['rung']!r} "
             f"HLPW6={v['per_grid'].get('HLPW6_h6c1_rans_3a_1')!r}; "
             f"rc={res['_rc']} in {res['_wall_s']} s"))


# ------------------------------------------------------------------------------ main
def main(argv):
    _ast_self_check()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scratch", default=None,
                    help="working directory (default: a temp dir, removed at exit)")
    ap.add_argument("--keep", action="store_true", help="keep the working directory")
    ap.add_argument("--json", default=None, help="write the full record here")
    a = ap.parse_args(argv)

    made = a.scratch is None
    scratch = Path(a.scratch) if a.scratch else Path(
        tempfile.mkdtemp(prefix="r0_pass_unreachable_"))
    scratch.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        for p, what in ((COMPARATOR, "the frozen comparator"), (WRITER, "the writer")):
            if not p.is_file():
                raise Refusal(f"{what} {p} is absent. ABSENT NEVER READS CLEAN.")
        arms = []
        a1, res1, g2b, v1 = arm1_all_gates_hold(scratch)
        arms.append(arm0_plant(scratch, res1))
        arms.append(a1)
        arms.append(arm2_failed_gate(scratch))
        arms.append(arm3_absent_case(scratch))
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return EXIT_REFUSE
    finally:
        if made and not a.keep:
            shutil.rmtree(scratch, ignore_errors=True)

    print("=== §2d.1 CONDITION (2) INSTRUMENT -- it grades nothing ===")
    for r in arms:
        print(f"  [{'FIRED' if r['fired'] else 'DID NOT FIRE':>12}] {r['control']}")
        print(f"                 expected: {r['expected']}")
        print(f"                 saw     : {r['saw']}")
    ok = all(r["fired"] for r in arms)
    verdicts = sorted({"PASS(planted)", v1["rung"], "GATE FAIL", "BLOCKED"})
    print(f"\nThe control's reader reported {len(verdicts)} distinct outcomes "
          f"{verdicts} on the SAME comparator. `PASS` appears there ONLY as arm 0's "
          f"plant, never as something `analyse_rung0.py` emitted.")
    print("NOT EXERCISED, AND NAMED: `NOT A RESULT`, which the comparator reaches only "
          "from its own planted controls, outside any run root this file can build.")
    if not ok:
        print("\nNOT A RESULT: an arm did not fire. Nothing above may be quoted "
              "(standing rule 3). REFUSED at exit 2.")
        return EXIT_REFUSE
    print(f"\nALL {len(arms)} ARMS FIRED in {time.time() - t0:.1f} s wall.")
    if a.json:
        Path(a.json).write_text(json.dumps(
            dict(instrument=str(Path(__file__).resolve()), arms=arms,
                 arm1_R0_G2b=g2b, arm1_comparator_reading=v1,
                 wall_s=round(time.time() - t0, 3)),
            indent=2, sort_keys=True, default=str))
        print(f"written: {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
