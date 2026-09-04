#!/usr/bin/env python3
"""INTEGRATION CONTROLS for the solve-evidence guard's wiring into cfd's own
GEN_ALT, FPE_DIAG, B52_RUNG6_REPLICATE, F9 and F7 drivers.

WHAT THIS IS FOR, AND WHAT IT IS NOT FOR.

`scripts/solve_evidence_guard.py --selftest` proves the GUARD works.  It says
nothing about whether any driver actually calls it.  A guard that is imported
and never reached is a decoration, and the failure mode is silent: the delete
still happens and the file still mentions a guard.  So these controls exercise
the DRIVERS' OWN call sites -- the real functions, by name -- and require the
refusal to arrive from there.

THE FIVE DRIVERS, and the fourteen delete sites wired:

  verification/runs/GEN_ALT_runs/run_gen_alt.py
      build_and_certify  (re-stage, FATAL)      smoke_solve (re-stage, FATAL)
      smoke_solve teardown (PRESERVING)         main() per-pair teardown
  verification/runs/FPE_DIAG_runs/run_fpe_diag.py
      stage_hills_kepsilon (re-stage, FATAL)    stage_bump case_root (FATAL)
      stage_bump teardown (PRESERVING)          solve() teardown (PRESERVING)
  verification/runs/B52_RUNG6_REPLICATE_runs/run_rung6_replicates.py
      stage (re-stage, FATAL)                   solve() 0/ reset (FATAL path)
  verification/runs/F9_work/setup_f9_round3.py                   [added 09-04]
      build_steady (re-stage, FATAL)            build_pulsatile (FATAL)
      build_restart (re-stage, FATAL)
  verification/runs/F7_runs/make_dambreak.py                     [added 09-04]
      main() --out (re-stage, FATAL)

F9 IS THE SHARPEST OF THE FIVE AND IS NOT UNDER THE SHARED RUN ROOT AT ALL.
Its `HERE = Path(__file__).resolve().parent` puts every case it builds INSIDE
THE REPOSITORY, in `verification/runs/F9_work/`, and on 2026-09-04 all five
cases `main()` rebuilds already existed there holding sixteen solved time
directories between them -- `lowalpha_ext` out to t = 10.8 and `physio_dt_half`
out to t = 2.7, each exactly its own endTime.  So this file's controls defend a
SECOND tree, `F9_FORBIDDEN_ROOT` below, and refuse if a fixture or a rebinding
would let anything reach it.

F7 HAS NO REDIRECTABLE ROOT BECAUSE IT HAS NO ROOT: `make_dambreak.py --out` is
operator-supplied with NO default (`required=True`).  Its controls therefore
pass a fixture path directly as argv, which is the whole target -- nothing can
leak to a real tree because nothing else is consulted.  That is also exactly
why the guard matters there: a mistyped `--out` was an unconditional delete.

NO COMPUTE IS LAUNCHED.  `tmr_verification._foam` is replaced by a SENTINEL
that raises if it is ever called, and `valve_pulsatile_cfd._foam` likewise for
F9.  A refusal that works arrives before the sentinel; a refusal that does not
work trips it loudly instead of starting OpenFOAM.  That is deliberate: the
sentinel is a control in its own right.

NOTHING UNDER ~/certonomous-runs IS TOUCHED, AND NOTHING UNDER F9_work IS
TOUCHED.  Every fixture is built in a temporary directory.  GEN_ALT and
FPE_DIAG are redirected with CERTONOMOUS_TMR_RUN_ROOT, set before
`tmr_verification` is imported.  B52 CANNOT be redirected that way -- its
`RUNS` is an absolute literal that never consults `_RUN_ROOT` -- so its module
globals are rebound after import.  F9's `HERE` is derived from `__file__` and
is likewise rebound after import.  A refusal below aborts the whole run if
either rebinding did not take.

THE -O CONTROL.  `make_dambreak.py` carried a bare `assert` that `python3 -O`
deletes outright, so under -O a non-integer `1.25*yres` was silently rounded
and a case was built at a resolution nobody asked for.  Control O1 runs the
real file as a subprocess under BOTH `python3` and `python3 -O` and requires
the SAME non-zero rc and the same refusal text from each.

CONTROLS.  `--selftest` runs them all.  `--mutation-control` registers a
MUTATED copy of the guard in `sys.modules` under the guard's own name BEFORE
the drivers are imported, so each driver's `if "solve_evidence_guard" in
sys.modules` branch adopts it, and requires the suite to go RED.  That control
does double duty: it is the only thing that proves the single-registration
branch is load-bearing, because a driver that ignored `sys.modules` and loaded
its own second copy would shrug the mutation off and stay GREEN.

No bare `assert` appears in this file, so `python3` and `python3 -O` agree.
"""
from __future__ import annotations

import ast
import importlib
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GUARD_PATH = REPO / "scripts" / "solve_evidence_guard.py"

DRIVERS = {
    "GEN_ALT": REPO / "verification/runs/GEN_ALT_runs/run_gen_alt.py",
    "FPE_DIAG": REPO / "verification/runs/FPE_DIAG_runs/run_fpe_diag.py",
    "B52": (REPO / "verification/runs/B52_RUNG6_REPLICATE_runs"
            / "run_rung6_replicates.py"),
    "F9": REPO / "verification/runs/F9_work/setup_f9_round3.py",
    "F7": REPO / "verification/runs/F7_runs/make_dambreak.py",
}

# The trees these controls exist to defend.  Nothing here may write into either.
FORBIDDEN_ROOT = Path.home() / "certonomous-runs"
# F9 does not use the shared run root at all: it builds IN the repository, and
# the sixteen solved time directories currently sitting there are exactly what
# its guard defends.  A control that only checked ~/certonomous-runs would have
# been blind to F9's entire blast radius.
F9_FORBIDDEN_ROOT = REPO / "verification" / "runs" / "F9_work"


# ---------------------------------------------------------------------------
# result plumbing


class Suite:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            print(f"  PASS  {name}")
        else:
            print(f"  FAIL  {name}{('  -- ' + detail) if detail else ''}")
            self.failures.append(name)


def attempt(fn, *a, **kw):
    """Run `fn`, returning (returned, exception).  Never propagates."""
    try:
        return fn(*a, **kw), None
    except BaseException as exc:                              # noqa: BLE001
        return None, exc


# ---------------------------------------------------------------------------
# fixtures -- the re2000 shape, and the negative


def plant_evidence(d: Path) -> Path:
    """endTime fields plus a coefficient series with data rows."""
    (d / "0").mkdir(parents=True)
    (d / "0" / "U").write_text("// 0/U\n")
    (d / "constant" / "polyMesh").mkdir(parents=True)
    (d / "constant" / "polyMesh" / "points").write_text("// points\n")
    (d / "system").mkdir(parents=True)
    (d / "system" / "controlDict").write_text("// controlDict\n")
    t = d / "90"
    t.mkdir(parents=True)
    for f in ("U", "p", "phi", "yPlus"):
        (t / f).write_text(f"// 90/{f}\n")
    pp = d / "postProcessing" / "forceCoeffs1" / "0"
    pp.mkdir(parents=True)
    rows = ["# Force coefficients", "# Time Cd Cs Cl"]
    rows += [f"{i * 0.01:.4g} 1.5879 0 0.1" for i in range(1, 501)]
    rows.append("90 1.5879 0 0.1")
    (pp / "coefficient.dat").write_text("\n".join(rows) + "\n")
    return d


def plant_mesh_only(d: Path) -> Path:
    """A genuinely re-stageable staging directory: mesh, no physics."""
    (d / "0").mkdir(parents=True)
    (d / "0" / "U").write_text("// 0/U\n")
    (d / "constant" / "polyMesh").mkdir(parents=True)
    (d / "constant" / "polyMesh" / "points").write_text("// points\n")
    (d / "system").mkdir(parents=True)
    (d / "system" / "controlDict").write_text("// controlDict\n")
    (d / "log.blockMesh").write_text("End\n")
    return d


def evidence_intact(d: Path) -> bool:
    return (d.is_dir() and (d / "90" / "U").is_file()
            and (d / "postProcessing" / "forceCoeffs1" / "0"
                 / "coefficient.dat").is_file())


# ---------------------------------------------------------------------------
# the mutation vector


def register_mutated_guard() -> bool:
    """Put a detector-disabled copy of the guard in sys.modules, under the
    guard's own name, BEFORE any driver imports it.  Returns False if the
    mutation could not be applied -- an unapplied mutation is a FAIL, never a
    pass, because it would let the suite go green for the wrong reason.
    """
    src = GUARD_PATH.read_text()
    marker = "    found: list[dict] = []\n"
    if marker not in src:
        print("MUTATION CONTROL BROKEN: anchor line not found in "
              f"{GUARD_PATH}; the control cannot be trusted and is a FAIL")
        return False
    mutated = src.replace(
        marker, "    return []  # MUTATION: detector disabled\n" + marker, 1)
    if mutated == src:
        print("MUTATION CONTROL BROKEN: source unchanged after mutation")
        return False
    tmp = Path(tempfile.mkdtemp(prefix="restage_wiring_mut_")) / "guard.py"
    tmp.write_text(mutated)
    spec = importlib.util.spec_from_file_location("solve_evidence_guard", tmp)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["solve_evidence_guard"] = mod
    spec.loader.exec_module(mod)
    return True


# ---------------------------------------------------------------------------
# structural control: no unguarded delete survives in these files


def structural_controls(s: Suite) -> None:
    """By AST PARSE, not grep.  A grep for `shutil.rmtree` is defeated by an
    alias, a line break or a comment; the parse is not, and this team has been
    burned by grep scope twice.
    """
    for tag, path in DRIVERS.items():
        tree = ast.parse(path.read_text(), filename=str(path))

        bare = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = None
            if isinstance(f, ast.Attribute):
                if isinstance(f.value, ast.Name) and f.value.id == "shutil":
                    name = f"shutil.{f.attr}"
            elif isinstance(f, ast.Name):
                name = f.id
            if name in ("shutil.rmtree", "rmtree"):
                bare.append(node.lineno)
        s.check(f"{tag} S1 no bare rmtree call survives", not bare,
                f"unguarded delete still at line(s) {bare}")

        n_assert = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))
        s.check(f"{tag} S2 zero ast.Assert nodes", n_assert == 0,
                f"{n_assert} assert statement(s): -O would remove them")

        guarded = sum(
            1 for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id in ("safe_rmtree_for_restage", "rmtree_after_harvest")
        )
        s.check(f"{tag} S3 delete sites route through the guard", guarded > 0,
                "no guarded delete call found at all")


# ---------------------------------------------------------------------------
# behavioural controls, per driver


def load_drivers(run_root: Path):
    """Import the three drivers with their run roots redirected.  Returns
    (modules, sentinel_calls).  Raises nothing the caller cannot see.
    """
    os.environ["CERTONOMOUS_TMR_RUN_ROOT"] = str(run_root)
    for p in (REPO / "sdk", REPO):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))

    mods = {}
    for tag, path in DRIVERS.items():
        spec = importlib.util.spec_from_file_location(f"_driver_{tag}", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"_driver_{tag}"] = mod
        spec.loader.exec_module(mod)
        mods[tag] = mod

    calls: list[str] = []

    def sentinel(args, *a, **kw):
        calls.append(str(args))
        raise RuntimeError(
            "SENTINEL TRIPPED: a control reached the OpenFOAM runner. These "
            "controls launch no compute; reaching this line means a delete "
            "site was NOT refused and the driver carried on into a solve.")

    for tag, mod in mods.items():
        if hasattr(mod, "log"):
            mod.log = lambda msg, _t=tag: None      # keep the repo clean
        if hasattr(mod, "tv"):
            mod.tv._foam = sentinel
        # B52 cannot be redirected by environment: rebind its literals.
        if tag == "B52":
            mod.RUNS = run_root
            mod.TEMPLATE = run_root / "study-b52-rung8-uq"
        # F9 cannot be redirected by environment either: its HERE is derived
        # from __file__ and points at the repository directory holding the real
        # solved cases.  Rebind it, and silence its solver path too -- `v` is
        # valve_pulsatile_cfd, whose run_util()/build_and_check() would launch
        # blockMesh.  setup_f9_round3 never calls them today; the sentinel is
        # there so that a future edit which does cannot start OpenFOAM from
        # inside a control.
        if tag == "F9":
            mod.HERE = run_root / "f9_work"
            (run_root / "f9_work").mkdir(parents=True, exist_ok=True)
            mod.v._foam = sentinel
    return mods, calls


def behavioural_controls(s: Suite, mods, calls, root: Path) -> None:
    # --- B0: the redirect actually took.  If it did not, every control below
    # would be aiming at a defended tree, so this refuses rather than checks.
    # F7 is absent from this loop BY CONSTRUCTION, not by oversight: it holds no
    # root global at all, its only target is the `--out` argv the control itself
    # supplies, and B0b below states that as a checked fact rather than a claim.
    roots = {"B52": "RUNS", "F9": "HERE", "GEN_ALT": "RUN_ROOT",
             "FPE_DIAG": "RUN_ROOT"}
    for tag, mod in mods.items():
        attr = roots.get(tag)
        if attr is None:
            continue
        real = Path(getattr(mod, attr)).resolve()
        bad = []
        for forbidden in (FORBIDDEN_ROOT, F9_FORBIDDEN_ROOT):
            f = forbidden.resolve()
            if real == f or f in real.parents:
                bad.append(str(f))
        s.check(f"{tag} B0 {attr} redirected away from every defended tree",
                not bad, f"{attr} is {real}, inside {bad}")
        if bad:
            print("  REFUSING to continue: controls never touch "
                  f"{', '.join(bad)}")
            return
        s.check(f"{tag} B0b {attr} was actually rebound to the fixture root",
                str(real).startswith(str(root.resolve())),
                f"{attr} is {real}, not under the fixture root {root}")

    # F7 carries no root global; assert that rather than assume it, because if
    # a future edit gave it one, the loop above would silently skip it.
    f7 = mods["F7"]
    f7_roots = [n for n in ("RUNS", "HERE", "RUN_ROOT", "OUT", "ROOT")
                if isinstance(getattr(f7, n, None), (str, Path))]
    s.check("F7 B0c has no root global to redirect (target is argv only)",
            not f7_roots, f"unexpected root global(s) {f7_roots}: if this file "
            "gained a default --out, the controls below stop defending it")

    # --- I1: ONE guard module object across all five drivers.
    registered = sys.modules.get("solve_evidence_guard")
    same = all(m.solve_evidence_guard is registered for m in mods.values())
    s.check("I1 all five drivers share ONE guard module object", same,
            "two module objects means two SolveEvidencePresent classes and an "
            "`except` that silently misses the other copy's refusal")

    exc_same = len({id(m.SolveEvidencePresent) for m in mods.values()}) == 1
    s.check("I1b all five drivers share ONE SolveEvidencePresent class",
            exc_same)

    def refuses(tag, label, fn, target: Path, *a, **kw):
        """The re-stage control: physics planted at `target`, driver function
        called for real, refusal required from the driver's own call site."""
        plant_evidence(target)
        before = len(calls)
        _, exc = attempt(fn, *a, **kw)
        refused = isinstance(exc, registered.SolveEvidencePresent)
        s.check(f"{tag} {label} refuses re-stage over solve evidence", refused,
                f"raised {type(exc).__name__ if exc else 'nothing'}")
        s.check(f"{tag} {label} the endTime fields survived",
                (target / "90" / "U").is_file())
        s.check(f"{tag} {label} the coefficient series survived",
                (target / "postProcessing" / "forceCoeffs1" / "0"
                 / "coefficient.dat").is_file())
        s.check(f"{tag} {label} no compute was launched",
                len(calls) == before,
                f"the OpenFOAM sentinel was reached {len(calls) - before}x")

    def stages_via_driver(tag, label, fn, target: Path, *a, **kw):
        """The STRONG negative: the real driver function is called over a
        mesh-only directory and must get all the way past staging into compute
        -- where the sentinel stops it.  Reaching the sentinel is the proof it
        staged; a refusal, or an early failure, is not.
        """
        plant_mesh_only(target)
        before = len(calls)
        _, exc = attempt(fn, *a, **kw)
        wrong = isinstance(exc, registered.SolveEvidencePresent)
        s.check(f"{tag} {label} mesh-only is NOT refused", not wrong,
                "the guard refused a directory that holds no physics -- the "
                "ladder is broken for every normal re-stage")
        s.check(f"{tag} {label} mesh-only staged through to compute",
                len(calls) > before,
                f"never reached the solver: {type(exc).__name__ if exc else ''}"
                f" {exc}")

    def stages_via_site(tag, label, mod, target: Path):
        """The narrower negative, used where driving the whole staging function
        would need a large synthetic source case.  It exercises the SITE'S OWN
        bound guard call -- the same object the site invokes -- over a mesh-only
        directory, and requires the delete to proceed.  Honest limit, stated so
        nobody reads more into it: this proves the guard admits a mesh-only
        directory at this site; the STRONG form above additionally proves the
        function continues into compute afterwards.
        """
        plant_mesh_only(target)
        out, exc = attempt(mod.safe_rmtree_for_restage, target)
        s.check(f"{tag} {label} mesh-only still deletes at the site's own "
                "guard call", out is True and not target.exists(),
                f"returned {out!r}, exc "
                f"{type(exc).__name__ if exc else None}")

    def preserves(tag, label, mod, target: Path):
        """The teardown control: evidence present, no raise, nothing lost."""
        plant_evidence(target)
        out, exc = attempt(mod.rmtree_after_harvest, target, "control")
        s.check(f"{tag} {label} teardown does not raise", exc is None,
                f"raised {type(exc).__name__ if exc else ''}")
        s.check(f"{tag} {label} teardown reports it deleted nothing",
                out is False, f"returned {out!r}")
        s.check(f"{tag} {label} teardown PRESERVED the physics",
                evidence_intact(target))

    # ---- GEN_ALT -----------------------------------------------------------
    g = mods["GEN_ALT"]
    lvl, first = g.PAIR[0][1], g.PAIR[0][2]
    refuses("GEN_ALT", "I2 build_and_certify",
            g.build_and_certify, root / "genalt-alt_coarse",
            "alt_coarse", lvl, first)
    refuses("GEN_ALT", "I3 smoke_solve",
            g.smoke_solve, root / "genalt-alt_refined_smoke", lvl, first)
    stages_via_driver("GEN_ALT", "I4 build_and_certify",
                      g.build_and_certify, root / "genalt-meshonly",
                      "meshonly", lvl, first)
    preserves("GEN_ALT", "I5", g, root / "genalt-teardown")

    # ---- FPE_DIAG ----------------------------------------------------------
    f = mods["FPE_DIAG"]
    refuses("FPE_DIAG", "I2 stage_hills_kepsilon",
            f.stage_hills_kepsilon, root / "fpediag-HP1", "HP1", 100, True)
    refuses("FPE_DIAG", "I3 stage_bump case_root",
            f.stage_bump, root / "fpediag-BP1-case", "BP1", "kOmegaSST",
            200, True)
    stages_via_site("FPE_DIAG", "I4", f, root / "fpediag-meshonly")
    preserves("FPE_DIAG", "I5", f, root / "fpediag-teardown")

    # ---- B52 ---------------------------------------------------------------
    b = mods["B52"]
    refuses("B52", "I2 stage", b.stage, root / "study-b52-rung6b-uq",
            "rung6b", (52, 44, 76))
    # B52's negative is driver-level and needs its TEMPLATE to exist, because
    # stage() copies from it.  stage() never invokes the solver, so the proof
    # that it staged is structural: the mesh-only fixture is gone and the
    # replacement carries the patched hex division triple.
    tmpl = b.TEMPLATE
    (tmpl / "system").mkdir(parents=True, exist_ok=True)
    (tmpl / "system" / "blockMeshDict").write_text(
        "hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)\n")
    (tmpl / "constant").mkdir(parents=True, exist_ok=True)
    (tmpl / "constant" / "marker").write_text("from the template\n")
    b52_neg = root / "study-b52-meshonly-uq"
    plant_mesh_only(b52_neg)
    out, exc = attempt(b.stage, "meshonly", (52, 44, 76))
    s.check("B52 I4 stage mesh-only is NOT refused",
            not isinstance(exc, registered.SolveEvidencePresent),
            "the guard refused a directory that holds no physics")
    s.check("B52 I4 the mesh-only fixture was replaced from the template",
            (b52_neg / "constant" / "marker").is_file()
            and not (b52_neg / "0").exists(),
            f"exc {type(exc).__name__ if exc else None}: {exc}")
    bmd = b52_neg / "system" / "blockMeshDict"
    s.check("B52 I4 the new draw's divisions were written",
            bmd.is_file() and "(52 44 76) simpleGrading" in bmd.read_text())

    # B52's 0/ reset: t = 0 is NOT evidence, so this must still delete --
    # otherwise the solve path is broken for every replicate.
    zero_case = root / "study-b52-zero-uq"
    plant_mesh_only(zero_case)
    out, exc = attempt(b.safe_rmtree_for_restage, zero_case / "0")
    s.check("B52 I6 the 0/ reset still deletes (t=0 is not evidence)",
            out is True and not (zero_case / "0").exists(),
            f"returned {out!r}, exc {type(exc).__name__ if exc else None}")

    # ---- F9 ----------------------------------------------------------------
    # All three sites are RE-STAGE, so all three refusals are FATAL.  The names
    # used here are the real ones `main()` rebuilds, so a reader can see that
    # the fixture stands in for a directory that genuinely exists on disk.
    n = mods["F9"]
    refuses("F9", "I2 build_steady", n.build_steady,
            n.HERE / "mesh_coarse_q100", "mesh_coarse_q100", n.COARSE_MESH,
            1e-4)
    refuses("F9", "I3 build_pulsatile", n.build_pulsatile,
            n.HERE / "pulsatile_fine", "pulsatile_fine", n.FINE_MESH,
            2.5e-5, 3.6)
    # build_restart is the sharpest site: lowalpha_ext and physio_dt_half are
    # the two real directories sitting at their own endTime.
    refuses("F9", "I4 build_restart", n.build_restart,
            n.HERE / "lowalpha_ext", "lowalpha_ext", "pulsatile_lowalpha",
            5.4, 10.8)

    # F9 negatives.  A mesh-only staging directory MUST still rebuild, or the
    # whole round-3 setup is broken to save one rung.  Proof that it rebuilt is
    # structural: the mesh-only marker is gone and write_case's own outputs are
    # present.
    f9_neg = n.HERE / "meshonly_steady"
    plant_mesh_only(f9_neg)
    out, exc = attempt(n.build_steady, "meshonly_steady", n.COARSE_MESH, 1e-4)
    s.check("F9 I5 mesh-only is NOT refused by build_steady",
            not isinstance(exc, registered.SolveEvidencePresent),
            "the guard refused a directory that holds no physics")
    s.check("F9 I5 build_steady rebuilt over the mesh-only fixture",
            (f9_neg / "system" / "blockMeshDict").is_file()
            and (f9_neg / "0" / "U").is_file()
            and not (f9_neg / "log.blockMesh").exists(),
            f"exc {type(exc).__name__ if exc else None}: {exc}")

    # And the restart path's negative, which needs a real source to copy from.
    src9 = n.HERE / "src_parent"
    for sub in ("constant/polyMesh", "system", "5.4"):
        (src9 / sub).mkdir(parents=True)
    (src9 / "constant" / "polyMesh" / "points").write_text("// points\n")
    (src9 / "5.4" / "U").write_text("// U\n")
    (src9 / "system" / "controlDict").write_text(
        "startTime       0;\nendTime         5.4;\npurgeWrite      3;\n"
        "maxCo           0.9;\nmaxDeltaT       0.001;\n")
    f9_rneg = n.HERE / "meshonly_restart"
    plant_mesh_only(f9_rneg)
    out, exc = attempt(n.build_restart, "meshonly_restart", "src_parent",
                       5.4, 10.8)
    s.check("F9 I6 mesh-only is NOT refused by build_restart",
            not isinstance(exc, registered.SolveEvidencePresent),
            f"exc {type(exc).__name__ if exc else None}: {exc}")
    cd9 = f9_rneg / "system" / "controlDict"
    s.check("F9 I6 build_restart rebuilt and patched the controlDict",
            cd9.is_file() and "startTime       5.4;" in cd9.read_text()
            and "endTime         10.8;" in cd9.read_text()
            and not (f9_rneg / "log.blockMesh").exists(),
            f"exc {type(exc).__name__ if exc else None}: {exc}")
    s.check("F9 I6 the restart SOURCE was never deleted",
            (src9 / "5.4" / "U").is_file(),
            "build_restart destroyed the parent run it copies from")

    # ---- F7 ----------------------------------------------------------------
    # RE-STAGE, FATAL, against an OPERATOR-SUPPLIED --out with no default.  The
    # target is argv, so the control supplies it directly.
    d7 = mods["F7"]

    def run_f7(target: Path, *extra: str):
        argv = sys.argv
        sys.argv = ["make_dambreak.py", "--out", str(target), "--res", "8",
                    *extra]
        try:
            return attempt(d7.main)
        finally:
            sys.argv = argv

    f7_ev = root / "f7-dambreak-r32"
    plant_evidence(f7_ev)
    before = len(calls)
    _, exc = run_f7(f7_ev)
    s.check("F7 I2 --out over solve evidence refuses",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'}")
    s.check("F7 I2 the endTime fields survived", (f7_ev / "90" / "U").is_file())
    s.check("F7 I2 the coefficient series survived",
            (f7_ev / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())
    s.check("F7 I2 nothing was overwritten in the refused directory",
            not (f7_ev / "constant" / "g").exists(),
            "the generator wrote into a directory it had just refused")
    s.check("F7 I2 no compute was launched", len(calls) == before)

    f7_neg = root / "f7-dambreak-meshonly"
    plant_mesh_only(f7_neg)
    _, exc = run_f7(f7_neg)
    s.check("F7 I3 mesh-only is NOT refused",
            not isinstance(exc, registered.SolveEvidencePresent),
            "the guard refused a directory that holds no physics")
    s.check("F7 I3 the case was rebuilt over the mesh-only fixture",
            (f7_neg / "system" / "blockMeshDict").is_file()
            and (f7_neg / "constant" / "g").is_file()
            and (f7_neg / "0.orig" / "alpha.water").is_file()
            and not (f7_neg / "log.blockMesh").exists(),
            f"exc {type(exc).__name__ if exc else None}: {exc}")

    f7_new = root / "f7-dambreak-fresh"
    _, exc = run_f7(f7_new)
    s.check("F7 I4 an absent --out is a no-op delete, then a clean build",
            exc is None and (f7_new / "system" / "controlDict").is_file(),
            f"exc {type(exc).__name__ if exc else None}: {exc}")


# ---------------------------------------------------------------------------


def optimisation_controls(s: Suite, root: Path) -> None:
    """O-controls: `python3` and `python3 -O` must return the SAME rc.

    `make_dambreak.py` carried a bare `assert` that -O deletes outright, so
    under -O a non-integer `1.25*yres` was silently rounded and the case was
    built at a resolution nobody asked for.  These run the REAL file as a
    subprocess under both interpreters and compare.

    HONEST LIMIT, stated rather than left for a reader to discover: a
    subprocess starts a fresh interpreter and loads the REAL guard, so these
    two controls are NOT sensitive to `--mutation-control`'s in-process
    mutation.  They are an -O control, not a wiring control; the wiring
    controls above are the ones the mutation must turn red.
    """
    import subprocess

    f7 = DRIVERS["F7"]

    def both(label: str, args: list[str]) -> tuple:
        outs = []
        for flags in ([], ["-O"]):
            r = subprocess.run([sys.executable, *flags, str(f7), *args],
                               capture_output=True, text=True, timeout=120)
            outs.append((r.returncode, (r.stdout + r.stderr)))
        s.check(f"O {label}: same rc under python3 and python3 -O",
                outs[0][0] == outs[1][0],
                f"rc {outs[0][0]} vs -O rc {outs[1][0]}")
        return outs

    # O1 -- the assert that -O used to delete.  1.25 * 6 = 7.5, not an integer.
    tgt = root / "o1-should-never-be-built"
    outs = both("O1 non-integer yres",
                ["--out", str(tgt), "--res", "8", "--yres", "6"])
    s.check("O1 non-integer yres is REFUSED under -O", outs[1][0] != 0,
            "-O accepted a resolution the un-optimised run rejected; this is "
            "exactly the bare-assert defect")
    s.check("O1 the -O refusal names the constraint",
            "multiple of 4" in outs[1][1], outs[1][1][:200])
    s.check("O1 no case was built by either interpreter", not tgt.exists(),
            f"{tgt} exists: a rejected resolution was written to disk anyway")

    # O2 -- the guard refusal itself must be identical under -O.
    ev = root / "o2-evidence"
    plant_evidence(ev)
    outs = both("O2 refusal over solve evidence",
                ["--out", str(ev), "--res", "8"])
    s.check("O2 the refusal happens under -O too", outs[1][0] != 0,
            "-O built over a directory holding physics")
    s.check("O2 the -O refusal names the evidence",
            "REFUSING to delete" in outs[1][1], outs[1][1][:300])
    s.check("O2 the physics survived both interpreters", evidence_intact(ev))


def run_suite() -> int:
    s = Suite()
    print("STRUCTURAL CONTROLS (AST parse, not grep)")
    structural_controls(s)
    print("\nBEHAVIOURAL CONTROLS (temporary fixtures; no compute; "
          "~/certonomous-runs untouched)")
    with tempfile.TemporaryDirectory(prefix="restage_wiring_") as tmp:
        root = Path(tmp)
        real = root.resolve()
        if real == FORBIDDEN_ROOT.resolve() or \
                FORBIDDEN_ROOT.resolve() in real.parents:
            print(f"  REFUSE: fixture root {real} is inside {FORBIDDEN_ROOT}")
            return 2
        for defended in (FORBIDDEN_ROOT, F9_FORBIDDEN_ROOT):
            d = defended.resolve()
            if real == d or d in real.parents:
                print(f"  REFUSE: fixture root {real} is inside {d}")
                return 2
        mods, calls = load_drivers(root)
        behavioural_controls(s, mods, calls, root)
        print("\nOPTIMISATION CONTROLS (python3 vs python3 -O, real "
              "subprocesses, temporary fixtures)")
        optimisation_controls(s, root)
        # Z1 is NOT "the sentinel was never reached" -- the mesh-only negative
        # is REQUIRED to reach it, because getting that far is what proves the
        # directory really staged.  What must hold is that no REAL solver ever
        # ran: every compute attempt was intercepted by the sentinel, and the
        # only attempt came from that one negative control.
        s.check("Z1 exactly one compute attempt, from the mesh-only negative, "
                "and the sentinel intercepted it", len(calls) == 1,
                f"{len(calls)} compute attempt(s): {calls[:5]}")
        s.check("Z2 no real OpenFOAM binary was invoked",
                all("SENTINEL" not in c for c in calls) and len(calls) <= 1,
                f"attempts: {calls[:5]}")

    if s.failures:
        print(f"\nRED: {len(s.failures)} control(s) failed: "
              f"{', '.join(s.failures)}")
        return 1
    print("\nGREEN: every control held.")
    return 0


def main(argv: list[str]) -> int:
    if "--mutation-control" in argv:
        print("MUTATION CONTROL: registering a detector-disabled guard under "
              "the guard's own name before the drivers import it.")
        print("The drivers MUST adopt it (single-registration branch) and the "
              "suite MUST go RED.\n")
        if not register_mutated_guard():
            return 2
        rc = run_suite()
        if rc == 0:
            print("\nMUTATION CONTROL FAILED: the suite stayed GREEN with the "
                  "detector disabled. Either the wiring is decorative or the "
                  "drivers loaded their own second copy of the guard. A "
                  "control that cannot fail is not a control.")
            return 1
        print(f"\nMUTATION CONTROL HELD: suite went RED (rc={rc}) with the "
              "detector disabled.")
        return 0
    if "--selftest" in argv:
        return run_suite()
    print(__doc__)
    print("usage: check_restage_guard_wiring.py "
          "[--selftest | --mutation-control]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
