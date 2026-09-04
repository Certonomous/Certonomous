#!/usr/bin/env python3
"""THE SOLVE-EVIDENCE GUARD — refuse to delete a directory that holds physics.

WHY THIS EXISTS, with the case that paid for it.

`verification/runs/F5_runs/run_rung.py` used to open `stage()` with

    shutil.rmtree(remote_dir, ignore_errors=True)

as its FIRST statement, against `~/certonomous-runs/f5a-cylinder-ladder/<rung>`,
and `cylinder_ladder.py:run_case()` and `cylinder_ladder_3d.py:stage()` carried
the identical line against the identical root.  That is not merely a sharp
edge, because of what sits on the other side of the same module:
`harvest()` REFUSES a rung whose `log.pimpleFoam` is missing.

`re2000` is a COMPLETED, GATED rung whose solver log is gone.  On disk it still
holds `90/` with `U p phi uniform yPlus` and a `coefficient.dat` carrying
10,191 data rows ending at t = 90 — exactly its `endTime` — bought at a
measured 66.09 core-min.  So `harvest()` refuses it forever, and the obvious
repair, "just re-stage and re-run it", is EXACTLY the call that destroys it.
`ignore_errors=True` meant it would not even have complained.  The only
sanctioned path forward deleted the evidence.

WHAT THIS MODULE DOES.  One rule, stated once:

    A directory that contains solve evidence is never deleted by a script.

Evidence is (a) any time directory > 0 holding field files — including inside
`processor*/`, because a parallel solve writes its fields there and nowhere
else — or (b) any `postProcessing/**/*.dat` carrying at least one data row.
Mesh alone (`0/`, `constant/polyMesh`, `system`, `log.blockMesh`,
`log.checkMesh`) is NOT evidence: a mesh-only staging directory is re-stageable
and must stay so, or the guard has broken the ladder to save one rung.

THERE IS NO OVERRIDE, AND THAT IS DELIBERATE.  A `--force-restage` flag is a
flag somebody pastes.  The recovery path this module prints instead is a human
`mv` of the directory aside, which PRESERVES the physics rather than destroying
it, and which no script can perform by accident.  This follows the doctrine
already written into `verification/runs/F4_runs/successor_2026-08-26/
grade_f4s.py` ("shutil.rmtree on a case directory is forbidden outright in
cfd's territory") and rule 4's launch-side guard.

`ignore_errors=True` is part of the defect and is not reproduced here: once the
guard has passed, a delete that fails must say so, not fall silent.

CONTROLS (rule 3).  `python3 scripts/solve_evidence_guard.py --selftest` builds
temporary fixtures — never a real run tree — plants the re2000 shape and
requires a REFUSAL, plants a mesh-only shape and requires it to stage, and
checks the refusal text actually names the time directory, the row count and
the last time.  `--mutation-control` neuters the detector in a temporary COPY
of this file and requires the suite to go RED; a control that cannot fail is
not a control.  No bare `assert` appears anywhere in this file, so `python3`
and `python3 -O` return the same rc.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

__all__ = [
    "SolveEvidencePresent",
    "find_solve_evidence",
    "format_evidence",
    "refuse_if_solve_evidence",
    "safe_rmtree_for_restage",
    "safe_replace_mirror",
]

# An OpenFOAM time directory name: 90, 0.5, 1e-05, 0.0001.  Anything else
# (constant, system, postProcessing, processor0) is not a time directory.
_TIME_NAME = re.compile(r"^\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$")


class SolveEvidencePresent(RuntimeError):
    """Raised instead of destroying a directory that holds physics."""


def _time_value(name: str):
    """Return the float value of a time-directory name, or None."""
    if not _TIME_NAME.match(name):
        return None
    try:
        return float(name)
    except ValueError:                                  # pragma: no cover
        return None


def _field_files(time_dir: Path) -> list[str]:
    """Regular files directly inside a time directory — i.e. written fields.

    `uniform/` is a directory and does not count on its own; a time directory
    holding only `uniform/` is bookkeeping, not a field.
    """
    try:
        return sorted(p.name for p in time_dir.iterdir() if p.is_file())
    except OSError:
        return []


def _data_rows(dat: Path):
    """(row count, last-row first column) for an OpenFOAM function-object .dat.

    A data row is any non-blank line not beginning with `#`.  The first column
    of the last such row is the last time the file records.
    """
    rows = 0
    last = None
    try:
        with dat.open("r", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                rows += 1
                last = s.split()[0]
    except OSError:
        return 0, None
    return rows, last


def _scan_time_dirs(root: Path, label: str) -> list[dict]:
    found = []
    try:
        entries = sorted(root.iterdir())
    except OSError:
        return found
    for d in entries:
        if not d.is_dir():
            continue
        t = _time_value(d.name)
        if t is None or t <= 0.0:
            continue
        fields = _field_files(d)
        if fields:
            found.append({
                "kind": "time_dir",
                "path": str(d),
                "label": label,
                "time": d.name,
                "n_fields": len(fields),
                "fields": fields[:8],
            })
    return found


def find_solve_evidence(target) -> list[dict]:
    """Every piece of solve evidence inside `target`.  Empty list == safe.

    Looked for in three places, because a run can leave its physics in any of
    them and a guard that checks only one is a memory of a guard:
      1. reconstructed time directories > 0 holding field files;
      2. the same inside `processor*/` — where a parallel solve writes, and
         where a reconstructPar was never run;
      3. `postProcessing/**/*.dat` with at least one data row.
    """
    target = Path(target)
    if not target.is_dir():
        return []

    found: list[dict] = []
    found.extend(_scan_time_dirs(target, "reconstructed"))

    try:
        procs = sorted(p for p in target.iterdir()
                       if p.is_dir() and re.match(r"^processor\d+$", p.name))
    except OSError:
        procs = []
    for p in procs:
        found.extend(_scan_time_dirs(p, p.name))

    pp = target / "postProcessing"
    if pp.is_dir():
        for dat in sorted(pp.rglob("*.dat")):
            if not dat.is_file():
                continue
            rows, last = _data_rows(dat)
            if rows > 0:
                found.append({
                    "kind": "series",
                    "path": str(dat),
                    "rows": rows,
                    "last_time": last,
                    "coefficients": dat.name.startswith("coefficient"),
                })
    return found


def format_evidence(target, found: list[dict]) -> str:
    """The refusal text.  It must show the operator what they nearly lost."""
    lines = [f"{target}: REFUSING to delete — this directory holds solve "
             f"evidence ({len(found)} item(s) that would have been destroyed):"]
    for f in found:
        if f["kind"] == "time_dir":
            lines.append(
                f"  time directory {f['time']}/ ({f['label']}) with "
                f"{f['n_fields']} field file(s): {', '.join(f['fields'])}"
                f"   [{f['path']}]")
        else:
            tag = "coefficient series" if f["coefficients"] else "series"
            lines.append(
                f"  {tag} with {f['rows']} data row(s), last time "
                f"{f['last_time']}   [{f['path']}]")
    lines.append(
        "The repair for missing bookkeeping is NEVER deletion of the physics "
        "(Sanaa, 2026-08-26: bookkeeping never voids physics). There is no "
        "override flag, deliberately. If this rung really must be re-staged, "
        "a HUMAN moves the directory aside first — e.g.")
    lines.append(f"  mv {target} {target}.PRESERVED_$(date -u +%Y%m%dT%H%MZ)")
    lines.append("which keeps every number above on disk, and then re-runs the "
                 "stage step.")
    return "\n".join(lines)


def refuse_if_solve_evidence(target, action: str = "delete") -> None:
    """Raise SolveEvidencePresent if `target` holds physics. Otherwise return."""
    target = Path(target)
    found = find_solve_evidence(target)
    if found:
        raise SolveEvidencePresent(
            f"[{action}] " + format_evidence(target, found))


def safe_rmtree_for_restage(target) -> bool:
    """The sanctioned replacement for `shutil.rmtree(d, ignore_errors=True)`.

    Refuses outright if `target` holds solve evidence.  Otherwise removes it
    WITHOUT `ignore_errors`: past the guard, a failed delete must be heard.
    Returns True if something was removed, False if there was nothing there.
    """
    target = Path(target)
    if not target.exists():
        return False
    refuse_if_solve_evidence(target, action="restage")
    shutil.rmtree(target)
    return True


def safe_replace_mirror(dst, src) -> bool:
    """Refresh a LOCAL mirror `dst` from `src`, never destroying the better copy.

    The same defect class, one line further down the same functions: harvest()
    did `shutil.rmtree(out_dir/"postProcessing", ignore_errors=True)` and then
    copied the remote one back BEST-EFFORT.  If the remote copy is gone, the
    local mirror — possibly the last copy — is destroyed and the failure only
    surfaces later as "no forceCoeffs output".  So: delete the mirror only when
    the source can actually replace it.
    """
    dst, src = Path(dst), Path(src)
    if not dst.exists():
        return False
    dst_ev = find_solve_evidence(dst.parent) if dst.name == "postProcessing" \
        else find_solve_evidence(dst)
    dst_rows = sum(f.get("rows", 0) for f in dst_ev if f["kind"] == "series")
    if dst_rows > 0:
        src_ev = find_solve_evidence(src.parent) if src.name == "postProcessing" \
            else find_solve_evidence(src)
        src_rows = sum(f.get("rows", 0) for f in src_ev if f["kind"] == "series")
        if src_rows < dst_rows:
            raise SolveEvidencePresent(
                f"[mirror] refusing to delete {dst}: it carries {dst_rows} "
                f"data row(s) and the replacement source {src} carries only "
                f"{src_rows}. Deleting the mirror would lose rows, not refresh "
                "them. Inspect the source; never revert the destination.")
    shutil.rmtree(dst)
    return True


# ---------------------------------------------------------------------------
# CONTROLS.  Fixtures only, always under a temporary directory.  Nothing in
# this section may touch ~/certonomous-runs — that is the tree being defended.
# ---------------------------------------------------------------------------
_FORBIDDEN_FIXTURE_ROOT = Path.home() / "certonomous-runs"


def _plant_re2000_shape(root: Path) -> Path:
    """The case that matters: endTime fields plus a coefficient series."""
    d = root / "re2000"
    (d / "0").mkdir(parents=True)
    (d / "0" / "U").write_text("// 0/U\n")
    (d / "0" / "p").write_text("// 0/p\n")
    (d / "constant" / "polyMesh").mkdir(parents=True)
    (d / "constant" / "polyMesh" / "points").write_text("// points\n")
    (d / "system").mkdir(parents=True)
    (d / "system" / "controlDict").write_text("// controlDict\n")
    (d / "log.blockMesh").write_text("End\n")
    (d / "log.checkMesh").write_text("End\n")
    t = d / "90"
    (t / "uniform").mkdir(parents=True)
    for f in ("U", "p", "phi", "yPlus"):
        (t / f).write_text(f"// 90/{f}\n")
    (t / "uniform" / "time").write_text("// time\n")
    pp = d / "postProcessing" / "forceCoeffs1" / "0"
    pp.mkdir(parents=True)
    rows = ["# Force coefficients", "# Time Cd Cs Cl"]
    for i in range(1, 10192):
        rows.append(f"{i * 90.0 / 10191:.6g} 1.5879 0 0.1")
    rows[-1] = "90 1.5879 0 0.1"
    (pp / "coefficient.dat").write_text("\n".join(rows) + "\n")
    return d


def _plant_mesh_only(root: Path) -> Path:
    """The negative: a genuinely re-stageable staging directory."""
    d = root / "meshonly"
    (d / "0").mkdir(parents=True)
    (d / "0" / "U").write_text("// 0/U\n")
    (d / "0" / "p").write_text("// 0/p\n")
    (d / "constant" / "polyMesh").mkdir(parents=True)
    (d / "constant" / "polyMesh" / "points").write_text("// points\n")
    (d / "system").mkdir(parents=True)
    (d / "system" / "controlDict").write_text("// controlDict\n")
    (d / "log.blockMesh").write_text("End\n")
    (d / "log.checkMesh").write_text("End\n")
    return d


def _plant_parallel_only(root: Path) -> Path:
    """Fields written by a parallel solve and never reconstructed."""
    d = root / "parallel"
    (d / "system").mkdir(parents=True)
    (d / "constant" / "polyMesh").mkdir(parents=True)
    for r in range(2):
        t = d / f"processor{r}" / "90"
        t.mkdir(parents=True)
        (t / "U").write_text("// U\n")
        (t / "p").write_text("// p\n")
    return d


def _plant_series_only(root: Path) -> Path:
    """Harvested rung: the time directories were cleaned, the series was not."""
    d = root / "seriesonly"
    (d / "system").mkdir(parents=True)
    pp = d / "postProcessing" / "forceCoeffs1" / "0"
    pp.mkdir(parents=True)
    (pp / "coefficient.dat").write_text(
        "# Force coefficients\n0.1 1.0 0 0\n0.2 1.0 0 0\n")
    return d


def _plant_empty_series(root: Path) -> Path:
    """postProcessing present but header-only: no physics, still re-stageable."""
    d = root / "emptyseries"
    (d / "system").mkdir(parents=True)
    pp = d / "postProcessing" / "forceCoeffs1" / "0"
    pp.mkdir(parents=True)
    (pp / "coefficient.dat").write_text("# Force coefficients\n# Time Cd Cs Cl\n")
    return d


def _selftest(mod) -> int:
    """Run every control against `mod` (this module, or a mutated copy).

    Returns 0 only if every control holds.  Never uses `assert`.
    """
    import tempfile

    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if ok:
            print(f"  PASS  {name}")
        else:
            print(f"  FAIL  {name}{('  -- ' + detail) if detail else ''}")
            failures.append(name)

    with tempfile.TemporaryDirectory(prefix="solve_evidence_guard_") as tmp:
        root = Path(tmp)
        real_root = root.resolve()
        forbidden = _FORBIDDEN_FIXTURE_ROOT.resolve()
        if real_root == forbidden or forbidden in real_root.parents:
            print(f"  REFUSE: fixture root {real_root} is inside "
                  f"{forbidden}; controls never touch the defended tree")
            return 2

        # C1 — THE CASE THAT MATTERS.  re2000 shape must REFUSE.
        d = _plant_re2000_shape(root)
        msg = ""
        refused = False
        try:
            mod.safe_rmtree_for_restage(d)
        except mod.SolveEvidencePresent as exc:
            refused, msg = True, str(exc)
        check("C1 re2000 shape refuses restage", refused,
              "the staging path DELETED a directory holding endTime fields "
              "and 10,191 coefficient rows")
        check("C1 the directory survived the attempt", d.is_dir())
        check("C1 the endTime fields survived", (d / "90" / "U").is_file())
        check("C1 the coefficient series survived",
              (d / "postProcessing" / "forceCoeffs1" / "0"
               / "coefficient.dat").is_file())
        # C2 — the refusal must NAME what it found.
        check("C2 refusal names the time directory", "90/" in msg, msg[:200])
        check("C2 refusal names the row count", "10191" in msg, msg[:200])
        check("C2 refusal names the last time", "last time 90" in msg, msg[:200])
        check("C2 refusal names the preserving recovery", "mv " in msg, msg[:200])

        # C3 — THE NEGATIVE.  A mesh-only directory must still stage.
        d2 = _plant_mesh_only(root)
        staged = False
        err = ""
        try:
            staged = mod.safe_rmtree_for_restage(d2)
        except Exception as exc:                              # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
        check("C3 mesh-only directory still stages", staged and not d2.exists(),
              err or "guard broke the ladder to save one rung")

        # C4 — a directory that does not exist is a no-op, not an error.
        gone = root / "neverexisted"
        noop = None
        err = ""
        try:
            noop = mod.safe_rmtree_for_restage(gone)
        except Exception as exc:                              # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
        check("C4 absent directory is a no-op", noop is False, err)

        # C5 — parallel-only fields count as evidence.
        d3 = _plant_parallel_only(root)
        refused = False
        try:
            mod.safe_rmtree_for_restage(d3)
        except mod.SolveEvidencePresent:
            refused = True
        check("C5 processor*/ fields refuse restage", refused and d3.is_dir(),
              "an un-reconstructed parallel solve was deleted")

        # C6 — a series with rows, time dirs already cleaned, is evidence.
        d4 = _plant_series_only(root)
        refused = False
        try:
            mod.safe_rmtree_for_restage(d4)
        except mod.SolveEvidencePresent:
            refused = True
        check("C6 series-only directory refuses restage", refused and d4.is_dir())

        # C7 — header-only series is NOT evidence.
        d5 = _plant_empty_series(root)
        staged = False
        err = ""
        try:
            staged = mod.safe_rmtree_for_restage(d5)
        except Exception as exc:                              # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
        check("C7 header-only series still stages", staged and not d5.exists(), err)

        # C8 — the mirror guard: never trade rows for fewer rows.
        mroot = root / "mirror"
        dst = mroot / "local" / "postProcessing" / "fc" / "0"
        dst.mkdir(parents=True)
        (dst / "coefficient.dat").write_text("# h\n1 1 0 0\n2 1 0 0\n3 1 0 0\n")
        src = mroot / "remote" / "postProcessing" / "fc" / "0"
        src.mkdir(parents=True)
        (src / "coefficient.dat").write_text("# h\n")
        refused = False
        try:
            mod.safe_replace_mirror(mroot / "local" / "postProcessing",
                                    mroot / "remote" / "postProcessing")
        except mod.SolveEvidencePresent:
            refused = True
        check("C8 mirror refresh refuses to lose rows",
              refused and (dst / "coefficient.dat").is_file())

        # C9 — and still refreshes when the source is at least as complete.
        (src / "coefficient.dat").write_text("# h\n1 1 0 0\n2 1 0 0\n3 1 0 0\n")
        ok = False
        err = ""
        try:
            ok = mod.safe_replace_mirror(mroot / "local" / "postProcessing",
                                         mroot / "remote" / "postProcessing")
        except Exception as exc:                              # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
        check("C9 mirror refresh proceeds when source is complete",
              ok and not (mroot / "local" / "postProcessing").exists(), err)

    if failures:
        print(f"\nRED: {len(failures)} control(s) failed: {', '.join(failures)}")
        return 1
    print("\nGREEN: every control held.")
    return 0


def _mutation_control() -> int:
    """Neuter the detector in a temporary COPY and require the suite to go RED.

    The mutation lives only in the copy; nothing weakens the shipped guard.
    """
    import importlib.util
    import tempfile

    src = Path(__file__).resolve().read_text()
    marker = "    found: list[dict] = []\n"
    if marker not in src:
        print("MUTATION CONTROL BROKEN: anchor line not found in "
              f"{__file__}; the control cannot be trusted and is a FAIL")
        return 2
    mutated = src.replace(
        marker,
        "    return []  # MUTATION: detector disabled\n" + marker, 1)
    if mutated == src:
        print("MUTATION CONTROL BROKEN: source unchanged after mutation")
        return 2

    with tempfile.TemporaryDirectory(prefix="solve_evidence_guard_mut_") as tmp:
        p = Path(tmp) / "mutated_guard.py"
        p.write_text(mutated)
        spec = importlib.util.spec_from_file_location("mutated_guard", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("MUTATION CONTROL: detector disabled in a temporary copy; "
              "the suite MUST go RED.")
        rc = _selftest(mod)

    if rc == 0:
        print("\nMUTATION CONTROL FAILED: the suite stayed GREEN with the "
              "detector disabled. A control that cannot fail is not a "
              "control.")
        return 1
    print("\nMUTATION CONTROL HELD: suite went RED (rc=%d) with the detector "
          "disabled." % rc)
    return 0


def _main(argv: list[str]) -> int:
    if "--selftest" in argv:
        print("SOLVE-EVIDENCE GUARD CONTROLS (temporary fixtures only)")
        return _selftest(sys.modules[__name__])
    if "--mutation-control" in argv:
        return _mutation_control()
    if "--check" in argv:
        rest = [a for a in argv if not a.startswith("--")]
        if not rest:
            print("usage: solve_evidence_guard.py --check <directory>")
            return 2
        found = find_solve_evidence(rest[0])
        if not found:
            print(f"{rest[0]}: no solve evidence found; safe to re-stage.")
            return 0
        print(format_evidence(rest[0], found))
        return 1
    print(__doc__)
    print("usage: solve_evidence_guard.py [--selftest | --mutation-control "
          "| --check <directory>]")
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
