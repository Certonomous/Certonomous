#!/usr/bin/env python3
"""Generate the Phase-2 MOVE_MAP: every tracked path that moves, old -> new.

PROPOSAL INSTRUMENT ONLY. This script MOVES NOTHING. It reads `git ls-files`
and writes docs/PHASE2_MOVE_MAP.tsv. Execution of the map is gated on Ladder V
convergence, Sanaa's veto, and the quiet window (docket item F / F1).

Why a generator instead of a hand-written list: docket F condition 4 requires a
MOVE_MAP of EVERY file, and the tree has ~20,600 tracked paths that keep
moving. A hand-typed list would be stale the day it was committed; this one is
regenerated and carries its commit anchor (L-79). The classification frame
follows scripts/corpus_figures.py `tracked_shape()` with one deliberate
difference, stated rather than hidden:

  corpus_figures counts a file as solver output only when its IMMEDIATE parent
  is a non-zero time directory (8,582 at 26a32239). A move map cannot use that
  frame, because a time directory moves as a unit -- `0.025/U` cannot go to
  evidence/ while `0.025/uniform/functionObjects/...` stays behind. So the
  move frame is: any path containing a non-zero numeric COMPONENT anywhere.
  Both counts are printed; the delta is nested subdirectories of time dirs.

Safety control (same shape as TRACKED_ARTIFACT_SCOPING.md section 2): every
path classified as solver output must sit under a directory that is explainable
as an OpenFOAM case root (tracked constant/ or system/ sibling) or under
postProcessing/. Unexplained paths are printed and the generator exits nonzero
so they cannot slip into the map unreviewed.

Actions emitted:
  UNTRACK-MV   git rm --cached + mv to evidence/<same path>  (stage 1, G5)
  GIT-MV       git mv, history preserved                      (stages 2-3)
  GIT-RM-DUP   byte-identical duplicate of another tracked file; the other
               copy is the survivor (flagged, needs its own docket line)

KEEP set (never emitted; counted in the header): README.md, .gitignore,
.gitattributes, LESSONS.md (H6 standing record -- exception to "nothing loose
at root", Sanaa's call), uq_batch.err / uq_batch.log (cited from
docs/HANDOFF-UQ.md as living at the worktree root; GITIGNORE_PROPOSAL.md
pinned them there), everything under sdk/ (retained per section F's
"certonomous/ or a retained sdk/") and docs/ (already the documentation home).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "PHASE2_MOVE_MAP.tsv"

NUM = re.compile(r"^[0-9]+\.?[0-9]*(?:e-?[0-9]+)?$")
LOG = re.compile(r"(^|/)log\.")
# corpus_figures.py frame, reproduced for the printed cross-check only:
PARENT_TIME = re.compile(r"/[0-9]+\.?[0-9]*(?:e-?[0-9]+)?/[^/]+$")
PARENT_ZERO = re.compile(r"/0/[^/]+$")

KEEP_ROOT = {
    "README.md", ".gitignore", ".gitattributes",
    "LESSONS.md",                      # H6 standing record; veto item F1-V2
    "uq_batch.err", "uq_batch.log",    # cited evidence, pinned at root
}

DEDUPE = {
    # byte-identical to demo-surfaces/naca4412_wing.stl (blob 9b3a5a35)
    "Stl_files/naca4412_wing.stl":
        ("cases/demo-surfaces/naca4412_wing.stl", "GIT-RM-DUP",
         "identical blob to demo-surfaces copy; survivor is the mapped dest"),
}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout


def tracked() -> list[str]:
    return [p for p in _git("ls-files", "-z").split("\0") if p]


def nonzero_component(path: str) -> bool:
    for c in path.split("/")[:-1]:
        if NUM.match(c):
            try:
                if float(c) != 0.0:
                    return True
            except ValueError:
                pass
    return False


def classify(path: str):
    """Return (new_path, action, stage, note) or None if the file stays."""
    if "/" not in path and path in KEEP_ROOT:
        return None
    if path in DEDUPE:
        new, act, note = DEDUPE[path]
        return (new, act, "2", note)

    top = path.split("/", 1)[0]

    # ---- stage 1: generated artifacts leave tracking (G5) ----------------
    if LOG.search(path) or nonzero_component(path):
        note = ""
        if path == "demo-output/website/tmr/runs/naca-a10-medium/log.checkMesh":
            note = ("ONLY exact-path log citation in tracked markdown "
                    "(campaign/C4_naca0012_closure.md) -- citation must be "
                    "annotated in the same commit; TRACKED_ARTIFACT_SCOPING "
                    "section 3 correction")
        return ("evidence/" + path, "UNTRACK-MV", "1", note)
    if "/" not in path and path.startswith("mbc_retry"):
        return ("evidence/build-logs/" + path, "UNTRACK-MV", "1",
                "H3b, GITIGNORE_PROPOSAL.md rule 1")
    if "/" not in path and path.endswith(".whl"):
        return ("evidence/wheels/" + path, "UNTRACK-MV", "1",
                "H3b wheels trap: untrack at HEAD regardless of the "
                "history-purge decision, which is Katie's")
    if path == "dist/certonomous-demo.zip":
        return ("evidence/dist/certonomous-demo.zip", "UNTRACK-MV", "1",
                "D56-GATED: bundle carries falsified figures and a standing "
                "FAIL; do not rebuild/re-track without D56 settlement")

    # ---- keeps ------------------------------------------------------------
    if top in ("sdk", "docs"):
        return None

    # ---- stage 2: low-fanout renames --------------------------------------
    if path == "FILMING_COMMANDS.md":
        return ("docs/filming/FILMING_COMMANDS.md", "GIT-MV", "2", "")
    if path == "LAPTOP_SHOOT.md":
        return ("docs/filming/LAPTOP_SHOOT.md", "GIT-MV", "2", "")
    if top == "scripts":
        return ("ops/" + path.split("/", 1)[1], "GIT-MV", "2",
                "section F pointer list applies")
    if top == "models":
        return ("cases/" + path.split("/", 1)[1], "GIT-MV", "2", "")
    if top == "demo-surfaces":
        return ("cases/demo-surfaces/" + path.split("/", 1)[1], "GIT-MV",
                "2", "")

    # ---- stage 3: the big rename ------------------------------------------
    if path.startswith("demo-output/website/"):
        return ("web/site/" + path[len("demo-output/website/"):], "GIT-MV",
                "3", "served root moves with it; URL paths below the root "
                     "are unchanged")
    if top == "demo-output":
        return ("web/filming/" + path.split("/", 1)[1], "GIT-MV", "3", "")

    return ("UNMAPPED", "UNMAPPED", "?", "rule gap -- must not ship")


def output_control(paths: list[str]) -> list[str]:
    """Every solver-output path must be explainable. Returns offenders."""
    tset = set(paths)
    bad: set[str] = set()
    for p in paths:
        if not nonzero_component(p) or LOG.search(p):
            continue
        # postProcessing.<suffix>/ is the restart-collision rename this lab
        # has met before (OPENFOAM restart watcher traps): still output.
        if re.search(r"/postProcessing[./]", p) or "/uniform/" in p:
            continue
        parts = p.split("/")
        idx = next(i for i, c in enumerate(parts[:-1])
                   if NUM.match(c) and float(c) != 0.0)
        case_root = "/".join(parts[:idx])
        ok = any((case_root + "/" + d + "/" in q or
                  q.startswith(case_root + "/" + d + "/"))
                 for d in ("constant", "system") for q in tset
                 if q.startswith(case_root + "/"))
        if not ok:
            bad.add(case_root or p)
    return sorted(bad)


def main() -> int:
    head = _git("rev-parse", "--short", "HEAD").strip()
    paths = tracked()
    rows, keeps = [], 0
    for p in paths:
        c = classify(p)
        if c is None:
            keeps += 1
        else:
            rows.append((p, *c))

    unmapped = [r for r in rows if r[2] == "UNMAPPED"]
    dests: dict[str, str] = {}
    collisions = []
    for old, new, act, stage, note in rows:
        if act == "GIT-RM-DUP":
            continue
        if new in dests:
            collisions.append((dests[new], old, new))
        dests[new] = old

    offenders = output_control(paths)

    parent_frame = sum(1 for p in paths
                       if PARENT_TIME.search(p) and not PARENT_ZERO.search(p))
    n1 = sum(1 for r in rows if r[3] == "1")
    n2 = sum(1 for r in rows if r[3] == "2")
    n3 = sum(1 for r in rows if r[3] == "3")
    nlog = sum(1 for r in rows if LOG.search(r[0]))

    with OUT.open("w") as f:
        f.write(f"# PHASE2 MOVE_MAP -- generated by scripts/phase2_move_map.py"
                f" at commit {head}\n")
        f.write(f"# frame: git ls-files ({len(paths)} tracked); "
                f"{keeps} keep in place; {len(rows)} rows below\n")
        f.write(f"# stage1 (untrack to evidence/): {n1}  "
                f"[logs {nlog}; whole-time-dir frame; corpus_figures "
                f"immediate-parent frame = {parent_frame}]\n")
        f.write(f"# stage2 (git mv, low fanout): {n2}   "
                f"stage3 (git mv, big rename): {n3}\n")
        f.write("# EXECUTION GATED: Ladder V converged + Sanaa's veto + "
                "quiet window. See docs/PHASE2_STRUCTURE_PROPOSAL.md and "
                "docket F1.\n")
        f.write("old_path\tnew_path\taction\tstage\tnote\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    print(f"anchor {head}: {len(paths)} tracked, {len(rows)} move rows "
          f"({n1}/{n2}/{n3} by stage), {keeps} keeps")
    print(f"solver-output frames: whole-dir {n1 - nlog - 13} approx vs "
          f"immediate-parent {parent_frame}")
    ok = True
    if unmapped:
        print(f"UNMAPPED ({len(unmapped)}):", *unmapped[:20], sep="\n  ")
        ok = False
    if collisions:
        print(f"DEST COLLISIONS ({len(collisions)}):", *collisions[:20],
              sep="\n  ")
        ok = False
    if offenders:
        print(f"UNEXPLAINED OUTPUT CASE ROOTS ({len(offenders)}):",
              *offenders[:40], sep="\n  ")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
