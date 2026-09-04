#!/usr/bin/env python3
"""INTEGRATION CONTROLS for the solve-evidence guard's wiring into cfd's own
GEN_ALT, FPE_DIAG, B52_RUNG6_REPLICATE, F9, F7, R4, F5c and F6a drivers.

WHAT THIS IS FOR, AND WHAT IT IS NOT FOR.

`scripts/solve_evidence_guard.py --selftest` proves the GUARD works.  It says
nothing about whether any driver actually calls it.  A guard that is imported
and never reached is a decoration, and the failure mode is silent: the delete
still happens and the file still mentions a guard.  So these controls exercise
the DRIVERS' OWN call sites -- the real functions, by name -- and require the
refusal to arrive from there.

THE EIGHT DRIVERS, and the nineteen delete sites wired:

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
  verification/runs/R4_runs/run_c3_replicates.py                 [added 09-04]
      stage (re-stage, FATAL)                   solve() 0/ reset (not evidence)
  verification/runs/F5c_runs/run_stage_a.py                      [added 09-04]
      run_leg out_dir (re-stage, FATAL)         run_leg archive dest (FATAL)
  scripts/run_f6a_greenblatt.py                                  [added 09-04]
      main() ss6.3 smoke <--scratch>/f6a_smoke (re-stage, FATAL)

F6a WAS THE LAST cfd-OWNED SITE OF THIS SHAPE, and it is the F7 shape exactly:
the delete target is built from an OPERATOR-SUPPLIED path with no default, so
the blast radius was whatever was typed.  Its frozen ss6.3 check refused only a
`verification/runs` prefix, which left `--scratch /home/ubuntu/certonomous-runs`
open even though THIS SAME FILE's `RUN_ROOTS` already names that tree as
evidence-bearing.  The prefix test is kept and extended to both evidence roots
and normalised through realpath, but it is POLICY, not the instrument: a prefix
test can only refuse trees somebody remembered to enumerate.  Control I5b states
that as a checked fact -- physics in a scratch matching NO prefix is still
refused, because the guard asks the target what is inside it.

WHERE F6a's PHYSICS SITS, MEASURED RATHER THAN ASSUMED (the F5c trap).  `smoke`
is a `copytree` of the case root and `simpleFoam -case smoke` writes into it, so
for F6a the TOP-LEVEL check is the load-bearing one -- `--check` on the shape
that is copied, `attempt3_Re936k`, reports 201 evidence items at the top level:
time directories 50..2000 with field files, the same times under `processor0..3`
and a postProcessing series.  Nothing of F6a's own physics is one level down.
The nested level is therefore defence in depth here, and control I3b isolates it
the way F5c I3b does -- the bare guard is required to find NOTHING at the
driver's own path first, so a nested refusal cannot be a lucky top-level hit --
while I4 requires the top-level check to be live, so I1/I2 cannot pass for the
wrong reason either.

NEITHER R4 NOR F5c NOR F6a HAS A TEARDOWN-AFTER-HARVEST SITE.  That was looked for
specifically, because it is the shape that turned out to be deleting COMPLETED
solves on purpose in GEN_ALT, FPE_DIAG and F9.  All three drivers leave their
run directories on disk after the record is written; every delete in each file
is listed above.  F5c's archive `dest` LOOKS like a teardown and is not: it is
cleared BEFORE collect.py refills it, and collect.py's non-zero return code is
only logged, so the delete is not conditional on a successful replacement.  It
is therefore a re-stage and its refusal is FATAL.  F6a has no teardown either:
an AST parse of the whole launcher finds exactly ONE destructive call in the
file -- the one wired above -- and the smoke directory is deliberately left on
disk after the pre-flight test, which is why its `scratch` path is reported in
the launcher's own record.

THE NESTED-EVIDENCE CONTROL, AND WHY IT EXISTS.  The guard scans its target for
time directories > 0, `processor*/` time directories, and
`postProcessing/**/*.dat` with data rows.  It does not recurse into an
arbitrary child.  F5c's `run_leg` deletes `SCRATCH/f5c-stageA-<leg>` while
`run_case` writes the whole OpenFOAM case one level down in `.../case/`, so the
obvious wiring -- guard the directory the driver names -- answers "no solve
evidence found; safe to re-stage" over a completed solve.  Measured 2026-09-04
with `solve_evidence_guard.py --check`: `f5c-stageA-A1` reported SAFE while
`f5c-stageA-A1/case` reported a time directory `2000/` with seven fields and a
series ending at t = 2000, and all four of A1..A4 have that shape.  Both
drivers therefore call a `safe_restage` wrapper that ALSO refuses on any
directory one level down, and controls R4 I5 and F5c I3 drive that path through
the drivers' own functions.  A guard that answers "safe" over physics is worse
than no guard, because it is believed.

F9 IS THE SHARPEST OF THE SEVEN AND IS NOT UNDER THE SHARED RUN ROOT AT ALL.
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

NOTHING UNDER ANY DEFENDED TREE IS TOUCHED.  Every fixture is built in a
temporary directory.  GEN_ALT and FPE_DIAG are redirected with
CERTONOMOUS_TMR_RUN_ROOT, set before `tmr_verification` is imported.  B52, R4
and F5c CANNOT be redirected that way -- each holds an ABSOLUTE LITERAL run
root (`RUNS`, `RUNS`, `SCRATCH`) that never consults `_RUN_ROOT`, so no
environment variable reaches them, including inside a control that believes it
has redirected them.  Their module globals are rebound after import.  F9's
`HERE` is derived from `__file__` and is likewise rebound.  R4 and F5c also
carry an absolute `HERE` inside the REPOSITORY (and R4 a `TEMPLATE` under it),
so those are rebound too and `demo-output/website/campaign` joins the defended
roots.  Controls B0 and B0b check EVERY rebound global of every driver against
EVERY defended root and REFUSE the whole run if a rebinding did not take -- a
control that silently ran against the real tree is the worst outcome available
here, and that tree holds `re2000`, a completed gated rung whose solver log is
already gone and which cannot be re-created.

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
    "R4": REPO / "verification/runs/R4_runs/run_c3_replicates.py",
    "F5c": REPO / "verification/runs/F5c_runs/run_stage_a.py",
    "F6a": REPO / "scripts/run_f6a_greenblatt.py",
}

# The trees these controls exist to defend.  Nothing here may write into any.
FORBIDDEN_ROOT = Path.home() / "certonomous-runs"
# F9 does not use the shared run root at all: it builds IN the repository, and
# the sixteen solved time directories currently sitting there are exactly what
# its guard defends.  A control that only checked ~/certonomous-runs would have
# been blind to F9's entire blast radius.
F9_FORBIDDEN_ROOT = REPO / "verification" / "runs" / "F9_work"

# R4 and F5c both carry an absolute `HERE` under `demo-output/website/campaign`
# -- R4's `TEMPLATE` is `HERE/"c3"`, F5c's archive destination is
# `HERE/"stage_a_<leg>"` -- and F5c's real record lives in
# `verification/runs/F5c_runs/`.  All three are defended: a control that only
# checked ~/certonomous-runs would have been blind to the archive site, which
# is the one that holds the ONLY copy of a gitignored postProcessing tree.
# F6a's own physics is in the repository too: `attempt3_Re936k` currently holds
# 201 evidence items (time directories 50..2000, `processor0..3`, and a
# postProcessing series) and `attempt2_Re936k` and `baseline_Re936k` are
# PRESERVED trees the launcher refuses to run without.  The controls rebind
# F6a's RUN_CASE away from all of it and B0 refuses if that rebinding did not
# take.
F6A_FORBIDDEN_ROOT = REPO / "verification" / "runs" / "F6a_GREENBLATT_runs"

DEFENDED_ROOTS = (
    FORBIDDEN_ROOT,
    F9_FORBIDDEN_ROOT,
    F6A_FORBIDDEN_ROOT,
    REPO / "demo-output" / "website" / "campaign",
    REPO / "verification" / "runs" / "F5c_runs",
    REPO / "verification" / "runs" / "R4_runs",
)


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


def plant_evidence_nested(d: Path, child: str = "case") -> Path:
    """The F5c shape: the physics is ONE LEVEL DOWN, under `case/`.

    Measured on disk 2026-09-04, this is not a hypothetical layout:
    `~/certonomous-runs/f5c-stageA-A1` reports "no solve evidence found" to the
    guard while `.../f5c-stageA-A1/case` reports a time directory `2000/` with
    seven fields and a series ending at t = 2000.  A wrapper that does not look
    one level down deletes that while printing that it was safe.
    """
    d.mkdir(parents=True, exist_ok=True)
    plant_evidence(d / child)
    return d


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
            and n.func.id in ("safe_rmtree_for_restage", "rmtree_after_harvest",
                              "safe_restage")
        )
        s.check(f"{tag} S3 delete sites route through the guard", guarded > 0,
                "no guarded delete call found at all")


# ---------------------------------------------------------------------------
# behavioural controls, per driver


def load_drivers(run_root: Path):
    """Import every driver with its run root redirected.  Returns
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
        # R4's RUNS is an absolute literal, exactly like B52's, and its HERE
        # (hence TEMPLATE, hence LOG) is an absolute literal inside the
        # repository.  All four are rebound; B0/B0b below refuse if any did
        # not take.  `stage()` copies FROM template, so the template is built
        # by the R4 negative control rather than here.
        if tag == "R4":
            mod.RUNS = run_root
            mod.HERE = run_root / "r4_here"
            mod.TEMPLATE = mod.HERE / "c3"
            mod.LOG = mod.HERE / "c3_replicates_driver.log"
            mod.HERE.mkdir(parents=True, exist_ok=True)
        # F5c's SCRATCH is an absolute literal and its HERE -- the ARCHIVE
        # destination, the only copy of a gitignored postProcessing tree -- is
        # an absolute literal inside the repository.  `run_case` is the solver
        # entry point and is replaced by the sentinel; it is a module global of
        # this driver (`from workflows.backstep_case import ... run_case`), so
        # rebinding it here is what the driver will actually call.
        if tag == "F5c":
            mod.SCRATCH = run_root
            mod.HERE = run_root / "f5c_here"
            mod.DRIVER_LOG = mod.HERE / "stage_a_driver.log"
            mod.HERE.mkdir(parents=True, exist_ok=True)
            mod.run_case = sentinel
        # F6a's roots are absolute literals inside the repository, and its
        # delete target is `<--scratch>/f6a_smoke` where `--scratch` is
        # OPERATOR-SUPPLIED with no default -- the same shape as F7's `--out`.
        # Four module globals are rebound and F6a B0/B0b/B0d refuse if any did
        # not take.  BOTH BUILDERS ARE REPLACED so no control can start
        # OpenFOAM: `build_case` becomes a stub that materialises a minimal
        # case (counted separately -- a stub call is not a compute attempt),
        # and the `subprocess` module in this driver's globals becomes a shim
        # that answers `checkMesh` with a Gate-M-passing text and routes EVERY
        # other binary -- simpleFoam, mpirun, decomposePar -- to the shared
        # sentinel, so an F6a compute attempt is counted in `calls` with
        # everyone else's rather than hidden in a private counter.
        if tag == "F6a":
            mod.RUN_CASE = str(run_root / "f6a_run_case")
            mod.RUN_ROOTS = (mod.RUN_CASE,
                             str(run_root / "f6a_second_root_absent"))
            mod.PRESERVED_TREES = {}
            mod._control_build_calls = []

            def _build_case_stub(repo, run_case, dry_run=False,
                                 _m=mod):     # noqa: ANN001
                steps = [(str(run_root / "shipped" / n), os.path.join(
                    run_case, n)) for n in ("0", "constant", "system")]
                if dry_run:
                    return steps
                _m._control_build_calls.append(str(run_case))
                case = Path(run_case)
                (case / "0").mkdir(parents=True, exist_ok=True)
                (case / "0" / "U").write_text("// 0/U\n")
                (case / "constant" / "polyMesh").mkdir(parents=True,
                                                       exist_ok=True)
                (case / "constant" / "polyMesh" / "points").write_text("// p\n")
                (case / "system").mkdir(parents=True, exist_ok=True)
                (case / "system" / "controlDict").write_text(
                    "// controlDict\napplication     simpleFoam;\n"
                    "endTime         2000;\nwriteInterval   50;\n")
                return steps

            mod.build_case = _build_case_stub

            _real_subprocess = mod.subprocess
            _GATE_M_PASSING = ("Mesh non-orthogonality Max: 42.1 average: 5.0\n"
                               "Max skewness = 1.2 OK.\nEnd\n")

            class _SubprocessShim:
                """Answers checkMesh; everything else trips the sentinel."""
                TimeoutExpired = _real_subprocess.TimeoutExpired
                CompletedProcess = _real_subprocess.CompletedProcess
                PIPE = _real_subprocess.PIPE

                @staticmethod
                def run(args, *a, **kw):
                    if args and args[0] == "checkMesh":
                        return _real_subprocess.CompletedProcess(
                            args, 0, _GATE_M_PASSING, "")
                    return sentinel(args, *a, **kw)

            mod.subprocess = _SubprocessShim
    return mods, calls


def behavioural_controls(s: Suite, mods, calls, root: Path) -> None:
    # --- B0: the redirect actually took.  If it did not, every control below
    # would be aiming at a defended tree, so this refuses rather than checks.
    # F7 is absent from this loop BY CONSTRUCTION, not by oversight: it holds no
    # root global at all, its only target is the `--out` argv the control itself
    # supplies, and B0b below states that as a checked fact rather than a claim.
    roots = {"B52": ("RUNS",), "F9": ("HERE",), "GEN_ALT": ("RUN_ROOT",),
             "FPE_DIAG": ("RUN_ROOT",),
             "R4": ("RUNS", "HERE", "TEMPLATE", "LOG"),
             "F5c": ("SCRATCH", "HERE", "DRIVER_LOG"),
             "F6a": ("RUN_CASE",)}
    for tag, mod in mods.items():
        for attr in roots.get(tag, ()):
            real = Path(getattr(mod, attr)).resolve()
            bad = []
            for forbidden in DEFENDED_ROOTS:
                f = forbidden.resolve()
                if real == f or f in real.parents:
                    bad.append(str(f))
            s.check(f"{tag} B0 {attr} redirected away from every defended tree",
                    not bad, f"{attr} is {real}, inside {bad}")
            if bad:
                print("  REFUSING to continue: controls never touch "
                      f"{', '.join(bad)}")
                return
            s.check(f"{tag} B0b {attr} was actually rebound to the fixture "
                    "root", str(real).startswith(str(root.resolve())),
                    f"{attr} is {real}, not under the fixture root {root}")

    # F7 carries no root global; assert that rather than assume it, because if
    # a future edit gave it one, the loop above would silently skip it.
    f7 = mods["F7"]
    f7_roots = [n for n in ("RUNS", "HERE", "RUN_ROOT", "OUT", "ROOT")
                if isinstance(getattr(f7, n, None), (str, Path))]
    s.check("F7 B0c has no root global to redirect (target is argv only)",
            not f7_roots, f"unexpected root global(s) {f7_roots}: if this file "
            "gained a default --out, the controls below stop defending it")

    # F6a's other three rebindings are a tuple and a dict, so the Path loop
    # above cannot cover them.  They are checked explicitly rather than
    # assumed: if RUN_ROOTS still named the real trees, `main()` would refuse
    # at the ss9.2 freeze condition and every F6a control below would pass for
    # the wrong reason; if PRESERVED_TREES still named them, it would refuse
    # even earlier.  A control that green-lights on an early refusal is the
    # exact failure this file exists to prevent.
    f6 = mods["F6a"]
    fixture_prefix = str(root.resolve())
    s.check("F6a B0d RUN_ROOTS rebound to the fixture root",
            all(str(Path(r).resolve()).startswith(fixture_prefix)
                for r in f6.RUN_ROOTS),
            f"RUN_ROOTS is {f6.RUN_ROOTS}")
    s.check("F6a B0e PRESERVED_TREES rebound away from the real trees",
            f6.PRESERVED_TREES == {},
            f"PRESERVED_TREES is {list(f6.PRESERVED_TREES)}")
    s.check("F6a B0f both builders were replaced",
            f6.build_case.__name__ == "_build_case_stub"
            and f6.subprocess.__name__ == "_SubprocessShim",
            f"build_case={f6.build_case!r} subprocess={f6.subprocess!r}")

    # --- I1: ONE guard module object across all eight drivers.
    registered = sys.modules.get("solve_evidence_guard")
    same = all(m.solve_evidence_guard is registered for m in mods.values())
    s.check("I1 all eight drivers share ONE guard module object", same,
            "two module objects means two SolveEvidencePresent classes and an "
            "`except` that silently misses the other copy's refusal")

    exc_same = len({id(m.SolveEvidencePresent) for m in mods.values()}) == 1
    s.check("I1b all eight drivers share ONE SolveEvidencePresent class",
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

    # ---- R4 ----------------------------------------------------------------
    # `RUNS` is an absolute literal.  Two sites: stage() is a RE-STAGE (FATAL),
    # solve()'s `0/` reset is a genuinely-not-evidence reset that must KEEP
    # deleting.  There is no teardown-after-harvest site in this file; that was
    # looked for specifically and every delete it contains is exercised here.
    r4 = mods["R4"]
    refuses("R4", "I2 stage", r4.stage, root / "r4-ahmed-c3b",
            "c3b", (99, 21, 58))

    # R4 I3 -- the L-42 reuse check in main() is NOT what protects this site.
    # It skips re-staging only when BOTH log.simpleFoam AND
    # postProcessing/forceCoeffs1 exist.  A case whose SOLVER LOG IS GONE but
    # whose fields are not -- the exact `re2000` shape the guard was written
    # for -- passes straight through it and reaches stage()'s delete.  This
    # fixture is that case: fields and a series, no log.
    r4_nolog = root / "r4-ahmed-nolog"
    plant_evidence(r4_nolog)
    before = len(calls)
    _, exc = attempt(r4.stage, "nolog", (99, 21, 58))
    s.check("R4 I3 a case with fields but NO solver log still refuses",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'} -- the L-42 "
            "reuse check does not cover this shape and never did")
    s.check("R4 I3 the endTime fields survived", (r4_nolog / "90" / "U").is_file())
    s.check("R4 I3 no compute was launched", len(calls) == before)

    # R4 I4 -- nested evidence one level down.  Defence in depth here (R4's own
    # cases carry their physics at the top level) but it is the same wrapper
    # F5c depends on, so it is proved at both sites, not assumed at one.
    r4_nested = root / "r4-ahmed-nested"
    plant_evidence_nested(r4_nested)
    _, exc = attempt(r4.stage, "nested", (99, 21, 58))
    s.check("R4 I4 evidence one level down refuses re-stage",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'}")
    s.check("R4 I4 the nested endTime fields survived",
            (r4_nested / "case" / "90" / "U").is_file())
    s.check("R4 I4 the nested coefficient series survived",
            (r4_nested / "case" / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())

    # R4 I5 -- the NEGATIVE.  stage() never invokes a solver, so the proof it
    # staged is structural, as for B52: the mesh-only fixture is replaced from
    # the template, `0.orig` survives the ignore filter, and the new draw's hex
    # triple is written.
    r4_tmpl = r4.TEMPLATE
    (r4_tmpl / "system").mkdir(parents=True, exist_ok=True)
    (r4_tmpl / "system" / "blockMeshDict").write_text(
        "hex (0 1 2 3 4 5 6 7) (10 10 10) simpleGrading (1 1 1)\n")
    (r4_tmpl / "0.orig").mkdir(parents=True, exist_ok=True)
    (r4_tmpl / "0.orig" / "U").write_text("// pristine U\n")
    (r4_tmpl / "constant").mkdir(parents=True, exist_ok=True)
    (r4_tmpl / "constant" / "marker").write_text("from the template\n")
    r4_neg = root / "r4-ahmed-meshonly"
    plant_mesh_only(r4_neg)
    out, exc = attempt(r4.stage, "meshonly", (99, 21, 58))
    s.check("R4 I5 stage mesh-only is NOT refused",
            not isinstance(exc, registered.SolveEvidencePresent),
            "the guard refused a directory that holds no physics")
    s.check("R4 I5 the mesh-only fixture was replaced from the template",
            (r4_neg / "constant" / "marker").is_file()
            and not (r4_neg / "log.blockMesh").exists(),
            f"exc {type(exc).__name__ if exc else None}: {exc}")
    s.check("R4 I5 0.orig survived staging (the pristine fields)",
            (r4_neg / "0.orig" / "U").is_file())
    r4_bmd = r4_neg / "system" / "blockMeshDict"
    s.check("R4 I5 the new draw's divisions were written",
            r4_bmd.is_file() and "(99 21 58) simpleGrading" in r4_bmd.read_text())

    # R4 I6 -- the 0/ reset.  t = 0 is NOT evidence, so it must still delete,
    # or every replicate's solve path is broken to save nothing.
    r4_zero = root / "r4-ahmed-zero"
    plant_mesh_only(r4_zero)
    out, exc = attempt(r4.safe_restage, r4_zero / "0")
    s.check("R4 I6 the 0/ reset still deletes (t=0 is not evidence)",
            out is True and not (r4_zero / "0").exists(),
            f"returned {out!r}, exc {type(exc).__name__ if exc else None}")

    # R4 I7 -- and the same call MIS-AIMED refuses, which is what routing the
    # reset through the guard buys: `ignore_errors=True` would have erased this.
    r4_mis = root / "r4-ahmed-misaimed"
    plant_evidence(r4_mis)
    out, exc = attempt(r4.safe_restage, r4_mis)
    s.check("R4 I7 a mis-aimed reset target REFUSES",
            isinstance(exc, registered.SolveEvidencePresent)
            and evidence_intact(r4_mis),
            f"returned {out!r}, exc {type(exc).__name__ if exc else None}")

    # ---- F5c ---------------------------------------------------------------
    # `SCRATCH` is an absolute literal; so is `HERE`, which is the ARCHIVE and
    # holds the only copy of a gitignored postProcessing tree.  Two sites, both
    # RE-STAGE, both FATAL.  No teardown-after-harvest site exists in this file.
    fc = mods["F5c"]

    # F5c I2 -- top-level evidence at the run directory.
    fc_ev = root / "f5c-stageA-A1"
    plant_evidence(fc_ev)
    before = len(calls)
    _, exc = attempt(fc.run_leg, fc.LEGS[0])
    s.check("F5c I2 run_leg refuses re-stage over solve evidence",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'}")
    s.check("F5c I2 the endTime fields survived", (fc_ev / "90" / "U").is_file())
    s.check("F5c I2 the coefficient series survived",
            (fc_ev / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())
    s.check("F5c I2 no compute was launched", len(calls) == before)

    # F5c I3 -- THE ONE THAT MATTERS, and the reason `safe_restage` exists.
    # This is the real on-disk shape: `f5c-stageA-A2` is empty apart from
    # `case/`, and `case/` holds an 8,000-iteration solve.  A bare
    # `safe_rmtree_for_restage(out_dir)` reports "safe to re-stage" here and
    # deletes it.  Without this control the wiring would look complete and be
    # decorative for all four of A1..A4.
    fc_nested = root / "f5c-stageA-A2"
    plant_evidence_nested(fc_nested)
    before = len(calls)
    _, exc = attempt(fc.run_leg, fc.LEGS[1])
    s.check("F5c I3 NESTED case/ evidence refuses re-stage",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'} -- the guard "
            "does not recurse; a wrapper that does not look one level down "
            "deletes a completed solve while printing that it was safe")
    s.check("F5c I3 the nested endTime fields survived",
            (fc_nested / "case" / "90" / "U").is_file())
    s.check("F5c I3 the nested coefficient series survived",
            (fc_nested / "case" / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())
    s.check("F5c I3 no compute was launched", len(calls) == before)
    # F5c I3b -- and the refusal above must be coming from the WRAPPER, not
    # from the bare guard, or the control proves nothing about the one-level
    # check.  The guard's own detector is asked directly and must find NOTHING
    # at the directory the driver names: that emptiness is the defect, and the
    # refusal in I3 therefore has only one possible source.
    s.check("F5c I3b the bare guard finds NOTHING at the directory the driver "
            "names -- so I3's refusal came from the nested check",
            registered.find_solve_evidence(fc_nested) == [],
            "the bare guard already saw this evidence, so I3 does not prove "
            "the nested check does anything")
    s.check("F5c I3b the bare guard DOES see it one level down",
            len(registered.find_solve_evidence(fc_nested / "case")) > 0)

    # F5c I4 -- the NEGATIVE, in its STRONG form: a mesh-only run directory
    # must stage all the way through into the solver, where the sentinel stops
    # it.  Reaching the sentinel is the proof it staged.
    fc_neg = root / "f5c-stageA-A3"
    plant_mesh_only(fc_neg)
    before = len(calls)
    _, exc = attempt(fc.run_leg, fc.LEGS[2])
    s.check("F5c I4 mesh-only is NOT refused",
            not isinstance(exc, registered.SolveEvidencePresent),
            "the guard refused a directory that holds no physics -- the "
            "ladder is broken for every normal re-stage")
    s.check("F5c I4 mesh-only staged through to compute", len(calls) > before,
            f"never reached the solver: {type(exc).__name__ if exc else ''}"
            f" {exc}")

    # F5c I5 -- the ARCHIVE site, reached for real.  `run_case` is swapped for
    # a STUB that returns a record without launching anything, so the driver
    # runs on past the solver call to the archive delete at its own call site.
    # The stub is counted separately from the sentinel so Z1 stays exact: a
    # stub call is NOT a compute attempt, because the stub is what replaced
    # compute.
    stub_calls: list[str] = []

    def run_case_stub(level, out_dir, **kw):
        stub_calls.append(str(out_dir))
        case = Path(out_dir) / "case"
        (case / "system").mkdir(parents=True, exist_ok=True)
        (case / "log.checkMesh").write_text("End\n")
        return {"x_r_over_h": 5.6, "x_r_over_h_nearwall_U": 5.6,
                "x_r_over_h_history": [], "mesh_certificate": {"verdict": "OK"},
                "levers_verified_active": {"verified": []}}

    arch_leg = dict(fc.LEGS[0])
    arch_leg["name"] = "ARCH"
    fc_dest = fc.HERE / "stage_a_ARCH"
    plant_evidence(fc_dest)
    real_run_case = fc.run_case
    fc.run_case = run_case_stub
    before = len(calls)
    try:
        _, exc = attempt(fc.run_leg, arch_leg)
    finally:
        fc.run_case = real_run_case
    s.check("F5c I5 the ARCHIVE destination refuses over solve evidence",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'} -- collect.py's "
            "non-zero rc is only logged, so this delete is not conditional on "
            "a successful replacement and the archive is the only copy")
    s.check("F5c I5 the archived endTime fields survived",
            (fc_dest / "90" / "U").is_file())
    s.check("F5c I5 the archived coefficient series survived",
            (fc_dest / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())
    s.check("F5c I5 the archive site was actually reached", len(stub_calls) == 1,
            f"the stub was called {len(stub_calls)}x: the control did not get "
            "past the solver call, so it did not exercise the archive site")
    s.check("F5c I5 no compute was launched", len(calls) == before)

    # F5c I6 -- and an archive with no data rows still clears, or a second
    # Stage A run can never write its record.
    fc_dest_neg = fc.HERE / "stage_a_MESHONLY"
    plant_mesh_only(fc_dest_neg)
    out, exc = attempt(fc.safe_restage, fc_dest_neg)
    s.check("F5c I6 a mesh-only archive destination still clears",
            out is True and not fc_dest_neg.exists(),
            f"returned {out!r}, exc {type(exc).__name__ if exc else None}")

    # ------------------------------------------------------------------
    # F6a -- `<--scratch>/f6a_smoke`, the ss6.3 pre-flight smoke re-stage.
    #
    # SHAPE: RE-STAGE BEFORE A BUILD, refusal FATAL.  Looked for a
    # teardown-after-harvest site specifically, because that is the shape found
    # deleting COMPLETED solves on purpose in GEN_ALT, FPE_DIAG and F9: F6a has
    # none.  An AST parse of the launcher finds exactly ONE destructive call in
    # the whole file (the one wired here) and the smoke directory is
    # deliberately left on disk afterwards.
    #
    # These controls drive `main()` ITSELF, not just the wrapper, so the
    # refusal has to arrive from the driver's own call site with the real
    # argument parsing, the real ss9.2 freeze condition and the real Gate M
    # in front of it.
    import contextlib
    import io as _io
    import json as _json

    f6_call = [0]

    def drive_main(argv: list[str]):
        """Run F6a's real main() with its report captured. Returns (rc, report,
        exception).

        A FRESH RUN_CASE PER CALL, and that is load-bearing rather than
        hygiene.  ss9.2 refuses outright (exit 3) when a registered run
        directory already exists, and the builder stub creates one; without
        this, the FIRST drive would exercise the site and every later drive
        would return 3 before reaching any of the code under test -- an early
        refusal that a naive control reads as success.  The fresh path is
        re-asserted to be inside the fixture root on every call, so a rebinding
        that escaped would raise here rather than aim a control at a real tree.
        """
        f6_call[0] += 1
        fresh = root / f"f6a_run_case_{f6_call[0]}"
        if not str(fresh.resolve()).startswith(str(root.resolve())):
            raise RuntimeError(f"F6a RUN_CASE {fresh} escaped the fixture root")
        f6.RUN_CASE = str(fresh)
        f6.RUN_ROOTS = (str(fresh), str(root / f"f6a_absent_{f6_call[0]}"))
        buf = _io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), \
                    contextlib.redirect_stderr(_io.StringIO()):
                rc = f6.main(argv)
        except BaseException as exc:            # noqa: BLE001 -- reported, not swallowed
            return None, {}, exc
        try:
            rep = _json.loads(buf.getvalue())
        except ValueError:
            rep = {}
        return rc, rep, None

    # F6a I1 -- the wrapper the site calls, over top-level physics.
    f6_t1 = root / "f6a-scratch-1" / "f6a_smoke"
    plant_evidence(f6_t1)
    _, exc = attempt(f6.safe_restage, f6_t1)
    s.check("F6a I1 safe_restage refuses over solve evidence",
            isinstance(exc, registered.SolveEvidencePresent),
            f"raised {type(exc).__name__ if exc else 'nothing'}")
    s.check("F6a I1 the endTime fields survived", (f6_t1 / "90" / "U").is_file())
    s.check("F6a I1 the coefficient series survived",
            (f6_t1 / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())

    # F6a I2 -- THE SITE ITSELF, through main().  Exit 8, nothing deleted.
    f6_s2 = root / "f6a-scratch-2"
    f6_t2 = f6_s2 / "f6a_smoke"
    plant_evidence(f6_t2)
    before = len(calls)
    rc, rep, exc = drive_main(["--scratch", str(f6_s2)])
    s.check("F6a I2 main() exits 8 at the smoke re-stage over solve evidence",
            rc == 8, f"rc={rc} exc={type(exc).__name__ if exc else None} {exc}")
    s.check("F6a I2 the report is NOT A RESULT and says nothing was deleted",
            rep.get("VERDICT") == "NOT A RESULT"
            and "NO DELETE WAS PERFORMED" in rep.get("refusal_kind", ""),
            f"VERDICT={rep.get('VERDICT')!r}")
    s.check("F6a I2 the refusal names the evidence it would have destroyed",
            "REFUSING to delete" in rep.get("REFUSAL", ""),
            rep.get("REFUSAL", "")[:200])
    s.check("F6a I2 the endTime fields survived", (f6_t2 / "90" / "U").is_file())
    s.check("F6a I2 the coefficient series survived",
            (f6_t2 / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())
    s.check("F6a I2 the site was actually reached (Gate M passed first)",
            rep.get("gate_m") is not None,
            "main() returned before Gate M, so the smoke site never ran and "
            "this control proves nothing")
    s.check("F6a I2 no compute was launched", len(calls) == before,
            f"sentinel reached {len(calls) - before}x")

    # F6a I3 -- THE STRONG NEGATIVE.  A mesh-only smoke directory must be
    # cleared and the case re-staged over it, all the way into the solver call
    # where the sentinel stops it.  Reaching the sentinel is the proof it
    # staged; a refusal is not.
    f6_s3 = root / "f6a-scratch-3"
    f6_t3 = f6_s3 / "f6a_smoke"
    plant_mesh_only(f6_t3)
    before = len(calls)
    rc, rep, exc = drive_main(["--scratch", str(f6_s3)])
    s.check("F6a I3 mesh-only is NOT refused",
            not isinstance(exc, registered.SolveEvidencePresent),
            "the guard refused a directory holding no physics -- every normal "
            "pre-flight smoke test is now broken")
    s.check("F6a I3 mesh-only staged through to the solver", len(calls) > before,
            f"never reached simpleFoam: {type(exc).__name__ if exc else ''} {exc}")
    s.check("F6a I3 the stale mesh-only tree was actually replaced",
            not (f6_t3 / "log.blockMesh").exists()
            and (f6_t3 / "system" / "controlDict").is_file(),
            "the old directory survived the re-stage, so the delete did not "
            "happen and the negative proves nothing")

    # F6a I3b -- THE NESTED CHECK, ISOLATED.  Physics one level down, under
    # `f6a_smoke/case`.  The BARE guard is asked directly at the driver's own
    # path and MUST find nothing there -- that is what makes this a test of the
    # nested level rather than a lucky top-level hit.  Then the driver must
    # refuse anyway.  Without the first half you cannot tell a real defence
    # from luck.
    f6_s4 = root / "f6a-scratch-4"
    f6_t4 = f6_s4 / "f6a_smoke"
    plant_evidence_nested(f6_t4)
    bare_top = registered.find_solve_evidence(f6_t4)
    bare_child = registered.find_solve_evidence(f6_t4 / "case")
    s.check("F6a I3b the bare guard finds NOTHING at the driver's own path",
            bare_top == [],
            f"{len(bare_top)} item(s) at the top level: this fixture is not "
            "nested, so it cannot test the nested check")
    s.check("F6a I3b the bare guard does find the physics one level down",
            len(bare_child) > 0, "the fixture planted no evidence at all")
    before = len(calls)
    rc, rep, exc = drive_main(["--scratch", str(f6_s4)])
    s.check("F6a I3b main() still exits 8 -- the refusal came from the NESTED "
            "check", rc == 8,
            f"rc={rc}: the driver deleted a directory the bare guard called "
            "safe while a completed solve sat one level inside it")
    s.check("F6a I3b the nested endTime fields survived",
            (f6_t4 / "case" / "90" / "U").is_file())
    s.check("F6a I3b the nested coefficient series survived",
            (f6_t4 / "case" / "postProcessing" / "forceCoeffs1" / "0"
             / "coefficient.dat").is_file())
    s.check("F6a I3b no compute was launched", len(calls) == before)

    # F6a I4 -- and the converse, measured rather than assumed: for F6a's own
    # layout the TOP-LEVEL check is the load-bearing one, because `smoke` is a
    # copytree of the case root and `simpleFoam -case smoke` writes its time
    # directories directly into it.  I3b proves the nested level works; this
    # proves the level that actually fires in production is not vestigial.
    s.check("F6a I4 the bare guard sees F6a's own layout at the top level",
            len(registered.find_solve_evidence(f6_t1)) > 0,
            "the top-level check -- the one F6a's real layout depends on -- "
            "finds nothing, so I1/I2 passed for the wrong reason")

    # F6a I5 -- THE ss6.3 POLICY TEST, EXTENDED.  The frozen form enumerated
    # only `verification/runs`, so nothing stopped `--scratch
    # /home/ubuntu/certonomous-runs`.  Both evidence roots are now refused, and
    # refused through REALPATH so a `..` walk cannot step past the test.
    # NOTHING IS WRITTEN: these refusals happen before build_case, and the
    # control asserts the path was not created.
    policy_cases = [
        ("certonomous-runs", str(FORBIDDEN_ROOT / "f6a-policy-probe")),
        ("verification/runs", str(REPO / "verification" / "runs"
                                  / "f6a-policy-probe")),
        ("a `..` walk into certonomous-runs",
         str(root / ".." / ".." / ".." / ".." / ".." / ".." / ".."
             / "home" / "ubuntu" / "certonomous-runs" / "f6a-policy-probe")),
    ]
    for label, probe in policy_cases:
        rc, rep, exc = drive_main(["--scratch", probe])
        s.check(f"F6a I5 --scratch inside {label} is REFUSED",
                rc == 6 and rep.get("VERDICT") == "NOT A RESULT",
                f"rc={rc} exc={type(exc).__name__ if exc else None}")
        s.check(f"F6a I5 the {label} refusal names the evidence root",
                "MUST be outside the evidence roots" in rep.get("REFUSAL", ""),
                rep.get("REFUSAL", "")[:160])
        s.check(f"F6a I5 nothing was created for {label}",
                not Path(probe).exists(), f"{probe} exists")

    # F6a I5b -- the policy test is not the safety instrument, and this states
    # that as a checked fact: a scratch OUTSIDE every enumerated root, holding
    # physics, is still refused.  A prefix test alone would have waved it past.
    f6_s6 = root / "f6a-unenumerated-scratch"
    f6_t6 = f6_s6 / "f6a_smoke"
    plant_evidence(f6_t6)
    rc, rep, exc = drive_main(["--scratch", str(f6_s6)])
    s.check("F6a I5b physics is refused even where NO prefix test applies",
            rc == 8, f"rc={rc}: the content check is not what is defending "
            "this delete -- the path list is, and a path list only refuses "
            "trees somebody remembered to enumerate")
    s.check("F6a I5b that physics survived", evidence_intact(f6_t6))

    # F6a I6 -- NO OVERRIDE FLAG.  A `--force-scratch` is a flag somebody
    # pastes, so its absence is a control, not a convention.
    f6_src = DRIVERS["F6a"].read_text()
    f6_tree = ast.parse(f6_src, filename=str(DRIVERS["F6a"]))
    f6_flags = [c.args[0].value for c in ast.walk(f6_tree)
                if isinstance(c, ast.Call)
                and isinstance(c.func, ast.Attribute)
                and c.func.attr == "add_argument"
                and c.args and isinstance(c.args[0], ast.Constant)
                and isinstance(c.args[0].value, str)]
    s.check("F6a I6 no override flag exists",
            not [f for f in f6_flags
                 if "force" in f or "ignore" in f or "no-guard" in f],
            f"override-shaped flag(s) in {f6_flags}")
    s.check("F6a I6 no ignore_errors survives in the launcher",
            not [k for c in ast.walk(f6_tree) if isinstance(c, ast.Call)
                 for k in c.keywords if k.arg == "ignore_errors"],
            "ignore_errors=True is part of the defect: past the guard, a "
            "failed delete must be heard")

    # F6a I7 -- the AST binding between the guarded call and the delete target.
    # S1/S3 prove there is no bare rmtree and that SOME guarded call exists;
    # they do not prove the guarded call names the directory that is about to
    # be overwritten.  This does: `safe_restage(X)` and `copytree(_, X)` must
    # name the SAME variable, and X must be the smoke path.
    guarded_names, copy_dsts = set(), set()
    for node in ast.walk(f6_tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "safe_restage" \
                and node.args and isinstance(node.args[0], ast.Name):
            guarded_names.add(node.args[0].id)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "copytree" \
                and len(node.args) > 1 and isinstance(node.args[1], ast.Name):
            copy_dsts.add(node.args[1].id)
    s.check("F6a I7 the guarded delete names the directory copytree overwrites",
            copy_dsts and copy_dsts <= guarded_names,
            f"copytree destinations {sorted(copy_dsts)} vs guarded "
            f"{sorted(guarded_names)}")
    s.check("F6a I7 that directory is the ss6.3 smoke path", "smoke" in
            guarded_names, f"guarded names are {sorted(guarded_names)}")


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

    # O3 -- F6a AS SHIPPED, both interpreters, no stubbing at all.  On this box
    # `attempt3_Re936k` exists, so the launcher refuses at the ss9.2 freeze
    # condition (exit 3) BEFORE it reaches the ss6.3 policy test.  That is the
    # honest observed behaviour and it is asserted as such rather than
    # engineered around; what the -O control needs from it is that both
    # interpreters agree, and that the defended tree is not touched on the way.
    f6a = DRIVERS["F6a"]
    probe = str(FORBIDDEN_ROOT / "f6a-O3-policy-probe")
    f6a_outs = []
    for flags in ([], ["-O"]):
        r = subprocess.run([sys.executable, *flags, str(f6a),
                            "--scratch", probe],
                           capture_output=True, text=True, timeout=120)
        f6a_outs.append((r.returncode, r.stdout + r.stderr))
    s.check("O3 F6a as shipped: same rc under python3 and python3 -O",
            f6a_outs[0][0] == f6a_outs[1][0],
            f"rc {f6a_outs[0][0]} vs -O rc {f6a_outs[1][0]}")
    s.check("O3 F6a as shipped refuses at ss9.2 before any scratch work",
            f6a_outs[1][0] == 3
            and "registered run directory already exists" in f6a_outs[1][1],
            f"rc {f6a_outs[1][0]}: {f6a_outs[1][1][:160]}")
    s.check("O3 neither interpreter created the probe directory",
            not Path(probe).exists(),
            f"{probe} exists: a refused scratch was written to the defended "
            "tree anyway")

    # O3b -- and the ss6.3 policy test itself, REACHED, in a real subprocess
    # under both interpreters.  ss9.2 stands in front of it on this box, so the
    # runner rebinds only the three root globals -- exactly what the in-process
    # controls rebind -- and changes nothing else.  Both the enumerated form
    # and the `..` walk must refuse, and must refuse identically under -O.
    runner = root / "o3b_runner.py"
    runner.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(f6a.parent)!r})\n"
        "import run_f6a_greenblatt as L\n"
        f"L.RUN_CASE = {str(root / 'o3b_run_case')!r}\n"
        "L.RUN_ROOTS = (L.RUN_CASE,)\n"
        "L.PRESERVED_TREES = {}\n"
        "sys.exit(L.main(sys.argv[1:]))\n")
    for label, p in (("enumerated", str(FORBIDDEN_ROOT / "f6a-O3b-probe")),
                     ("`..` walk", str(root / ".." / ".." / ".." / ".." / ".."
                                       / ".." / ".." / "home" / "ubuntu"
                                       / "certonomous-runs" / "f6a-O3b-walk"))):
        outs = []
        for flags in ([], ["-O"]):
            r = subprocess.run([sys.executable, *flags, str(runner),
                                "--scratch", p],
                               capture_output=True, text=True, timeout=120)
            outs.append((r.returncode, r.stdout + r.stderr))
        s.check(f"O3b {label} scratch: same rc under python3 and python3 -O",
                outs[0][0] == outs[1][0],
                f"rc {outs[0][0]} vs -O rc {outs[1][0]}")
        s.check(f"O3b {label} scratch is REFUSED under -O too", outs[1][0] == 6,
                f"rc {outs[1][0]}: {outs[1][1][:200]}")
        s.check(f"O3b the {label} -O refusal names the evidence root",
                "MUST be outside the evidence roots" in outs[1][1],
                outs[1][1][:200])
        s.check(f"O3b neither interpreter created the {label} probe",
                not Path(p).exists(), f"{p} exists")


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
        # Z1 is NOT "the sentinel was never reached" -- the mesh-only negatives
        # are REQUIRED to reach it, because getting that far is what proves the
        # directory really staged.  What must hold is that no REAL solver ever
        # ran: every compute attempt was intercepted by the sentinel, and the
        # attempts came only from those negative controls.  There are exactly
        # THREE strong negatives that reach a solver entry point: GEN_ALT I4
        # (build_and_certify -> tv._foam), F5c I4 (run_leg -> run_case) and
        # F6a I3 (main -> simpleFoam via the subprocess shim).  The other
        # negatives -- B52 I4, F9 I5/I6, F7 I3/I4, R4 I5 -- prove staging
        # structurally because those functions never invoke a solver.
        s.check("Z1 exactly three compute attempts, all from mesh-only "
                "negatives, all intercepted by the sentinel", len(calls) == 3,
                f"{len(calls)} compute attempt(s): {calls[:6]}")
        s.check("Z2 no real OpenFOAM binary was invoked",
                all("SENTINEL" not in c for c in calls) and len(calls) <= 3,
                f"attempts: {calls[:6]}")
        s.check("Z3 F6a's checkMesh never ran either -- the shim answered it",
                mods["F6a"].subprocess.__name__ == "_SubprocessShim")

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
