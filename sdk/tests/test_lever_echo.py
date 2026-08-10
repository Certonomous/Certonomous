"""Lever echo (Verification Charter v1.5 section 9, adopted 2026-08-08):
the four lever classes stock OpenFOAM never echoes enter the run log at
launch, fenced and hash-bound, so levers_verified_active is satisfiable at
write time. The dead-lever audit's 16 unverifiable-from-logs conclusions are
the measured cost of not having this."""

import hashlib
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer import lever_echo
from workflows import tmr_verification as tv


def _foam_file(kind: str, obj: str) -> str:
    return (f"FoamFile\n{{\n    version 2.0;\n    format ascii;\n"
            f"    class {kind};\n    object {obj};\n}}\n")


def _preflight_clean_case(root: Path, scheme: str) -> Path:
    """A case minimal enough to read at a glance and complete enough to pass
    `scripts/case_preflight.sh`, which `launch_solve.sh` gates on before it
    will launch anything. Laminar, so no turbulence fields are required.

    `scheme` is what distinguishes two of these from each other, and it is the
    thing the echo must be caught certifying: if a test ever sees one case's
    scheme in the other's log, the run-directory binding has broken.
    """
    (root / "system").mkdir(parents=True)
    (root / "constant").mkdir()
    (root / "0").mkdir()
    (root / "system" / "fvSchemes").write_text(
        _foam_file("dictionary", "fvSchemes")
        + f"divSchemes {{ div(phi,U) {scheme}; }}\n")
    (root / "system" / "fvSolution").write_text(
        _foam_file("dictionary", "fvSolution")
        + "solvers { p { solver PCG; } U { solver PBiCGStab; } }\n"
          "SIMPLE { consistent yes; }\n")
    (root / "system" / "controlDict").write_text(
        _foam_file("dictionary", "controlDict")
        + "application simpleFoam;\nstartTime 0;\nendTime 10;\ndeltaT 1;\n"
          "writeControl timeStep;\nwriteInterval 5;\n")
    (root / "constant" / "turbulenceProperties").write_text(
        _foam_file("dictionary", "turbulenceProperties")
        + "simulationType laminar;\n")
    (root / "0" / "U").write_text(
        _foam_file("volVectorField", "U")
        + "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (1 0 0);\n"
          "boundaryField { inlet { type freestreamVelocity; } }\n")
    (root / "0" / "p").write_text(
        _foam_file("volScalarField", "p")
        + "dimensions [0 2 -2 0 0 0 0];\ninternalField uniform 0;\n"
          "boundaryField { inlet { type zeroGradient; } }\n")
    return root


def _fixture_case(root: Path) -> Path:
    case = root / "case"
    (case / "system").mkdir(parents=True)
    (case / "constant").mkdir()
    (case / "0").mkdir()
    (case / "system" / "fvSchemes").write_text(
        "divSchemes { div(phi,U) bounded Gauss linearUpwind grad(U); }\n")
    (case / "system" / "fvSolution").write_text(
        "SIMPLE { consistent yes; }\n")
    (case / "constant" / "turbulenceProperties").write_text(
        "simulationType RAS;\n")
    (case / "0" / "U").write_text(
        "boundaryField { inlet { type freestreamVelocity; } }\n")
    return case


class EchoBlockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-echo-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)

    def test_every_present_lever_file_is_echoed_and_hash_bound(self):
        block = lever_echo.echo_block(self.case)
        echoed = lever_echo.parse_echo(block)
        self.assertEqual(
            set(echoed),
            {"system/fvSchemes", "system/fvSolution",
             "constant/turbulenceProperties", "0/U"})
        # The hash binds the echo to the exact bytes that ran: class 2,
        # the SIMPLEC `consistent` flag no solver banner ever states.
        expected = hashlib.sha256(
            (self.case / "system" / "fvSolution").read_bytes()).hexdigest()
        self.assertEqual(echoed["system/fvSolution"], expected)
        self.assertIn("consistent yes", block)

    def test_a_log_without_an_echo_says_so_plainly(self):
        field = lever_echo.levers_verified_active("Time = 100\nEnd\n")
        self.assertEqual(field["verified"], [])
        self.assertIn("unverifiable", field["basis"])

    def test_the_record_field_cites_the_echo_by_hash(self):
        log_text = lever_echo.echo_block(self.case) + "Time = 100\nEnd\n"
        field = lever_echo.levers_verified_active(log_text)
        names = {entry["file"] for entry in field["verified"]}
        self.assertIn("system/fvSchemes", names)
        for entry in field["verified"]:
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("LEVER-ECHO", entry["evidence"])

    def test_absent_dictionaries_are_simply_absent(self):
        (self.case / "system" / "fvSolution").unlink()
        echoed = lever_echo.parse_echo(lever_echo.echo_block(self.case))
        self.assertNotIn("system/fvSolution", echoed)


class FoamRunnerEchoTests(unittest.TestCase):
    """The workflows' shared solver runner echoes for SOLVER launches only;
    utility logs stay pristine for their parsers."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-foam-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)
        patcher = mock.patch.object(tv, "_run_prefix", return_value=["echo"])
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_solver_launch_carries_the_echo(self):
        tv._foam(["simpleFoam"], self.case, "log.simpleFoam")
        text = (self.case / "log.simpleFoam").read_text()
        self.assertTrue(text.startswith(lever_echo.BEGIN))
        self.assertIn("system/fvSchemes", lever_echo.parse_echo(text))

    def test_a_utility_launch_stays_pristine(self):
        tv._foam(["blockMesh"], self.case, "log.blockMesh")
        text = (self.case / "log.blockMesh").read_text()
        self.assertNotIn(lever_echo.BEGIN, text)

    # -- the parallel spelling -------------------------------------------
    #
    # WHY THIS TEST EXISTS. The echo's launch test was `args[0] in SOLVERS`
    # until commit 199e9d17, so a parallel launch -- spelled
    # `mpirun -np N <solver> -parallel`, which is how the campaign's long
    # solves launch -- silently produced NO echo block. The defect emitted no
    # error and no warning: the log was written, the solve ran, and
    # `levers_verified_active` merely reported "unverifiable", which reads
    # exactly like a pre-adoption log. It survived adoption for two days
    # because every test asserted on a SERIAL spelling. So these tests assert
    # on the block's PRESENCE and CONTENT; asserting the absence of an error
    # would have passed against the defect.

    def test_a_parallel_spelled_launch_carries_the_echo(self):
        tv._foam(["mpirun", "-np", "2", "simpleFoam", "-parallel"],
                 self.case, "log.simpleFoam")
        text = (self.case / "log.simpleFoam").read_text()
        self.assertTrue(text.startswith(lever_echo.BEGIN),
                        "a parallel-spelled solver launch wrote no LEVER-ECHO "
                        "block at the head of its log")
        echoed = lever_echo.parse_echo(text)
        # Content, not merely presence: the block must carry the lever files
        # bound to the exact bytes on disk.
        self.assertIn("system/fvSchemes", echoed)
        self.assertIn("system/fvSolution", echoed)
        self.assertEqual(
            echoed["system/fvSolution"],
            hashlib.sha256(
                (self.case / "system" / "fvSolution").read_bytes()).hexdigest())
        self.assertIn("consistent yes", text)

    def test_the_record_field_from_a_parallel_launch_is_mechanical(self):
        """The field the charter names must come out MECHANICAL, not
        'unverifiable', for the launch shape the campaign actually uses."""
        tv._foam(["mpirun", "-np", "4", "simpleFoam", "-parallel"],
                 self.case, "log.simpleFoam")
        field = lever_echo.levers_verified_active(
            (self.case / "log.simpleFoam").read_text())
        self.assertTrue(field["verified"],
                        "levers_verified_active came back empty for a "
                        "parallel launch -- the L-40 gate did not fire")
        self.assertIn("launcher echo", field["basis"])
        self.assertNotIn("unverifiable", field["basis"])

    def test_every_solver_spelling_a_repo_caller_uses_in_parallel_echoes(self):
        """The repo's real parallel spellings, not just simpleFoam: the
        rae2822 case-9 workflow launches `mpirun -np N rhoSimpleFoam
        -parallel` THROUGH this runner, so the fix is not a no-op there."""
        for solver in ("simpleFoam", "rhoSimpleFoam", "pimpleFoam"):
            with self.subTest(solver=solver):
                name = f"log.{solver}"
                tv._foam(["mpirun", "-np", "2", solver, "-parallel"],
                         self.case, name)
                echoed = lever_echo.parse_echo(
                    (self.case / name).read_text())
                self.assertIn("system/fvSchemes", echoed)

    def test_a_parallel_utility_launch_still_stays_pristine(self):
        """Generalizing the membership test must not start echoing into
        utility logs their parsers expect clean."""
        tv._foam(["mpirun", "-np", "2", "redistributePar", "-parallel"],
                 self.case, "log.redistributePar")
        text = (self.case / "log.redistributePar").read_text()
        self.assertNotIn(lever_echo.BEGIN, text)


class RunDirectoryBindingTests(unittest.TestCase):
    """L-45: the echo is derived from the directory the process RUNS IN,
    never from a path a caller supplied describing what it intended.

    WHY THIS TEST EXISTS. `scripts/launch_solve.sh` built its echo from the
    caller-supplied `--case` while the command ran under `setsid nohup "$@"`
    in the launcher's inherited working directory, with nothing binding the
    two. A mismatched `--case` would have certified dictionaries that did not
    run, at the head of the log of a solve that did. That is a FALSE
    verification, not a missing one, and it is the failure direction that
    costs the whole corpus rather than one record.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-rundir-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # Two cases with DELIBERATELY different levers, so "which directory
        # did this hash come from" has an observable answer.
        self.ran = _fixture_case(self.tmp / "actually-ran")
        self.claimed = _fixture_case(self.tmp / "merely-claimed")
        (self.claimed / "system" / "fvSchemes").write_text(
            "divSchemes { div(phi,U) Gauss upwind; }\n")

    def _sha(self, case: Path, rel: str) -> str:
        return hashlib.sha256((case / rel).read_bytes()).hexdigest()

    def test_the_echo_hashes_the_directory_that_runs_not_the_one_declared(self):
        block = lever_echo.echo_block_for_run_dir(self.ran)
        echoed = lever_echo.parse_echo(block)
        self.assertEqual(echoed["system/fvSchemes"],
                         self._sha(self.ran, "system/fvSchemes"))
        # The content assertion that pins the bug: the OTHER case's scheme
        # must appear nowhere, by hash or by text.
        self.assertNotEqual(echoed["system/fvSchemes"],
                            self._sha(self.claimed, "system/fvSchemes"))
        self.assertIn("linearUpwind", block)
        self.assertNotIn("Gauss upwind", block)

    def test_a_mismatched_declared_case_produces_no_passing_echo(self):
        """THE case that would have caught it. A caller describing one
        directory while the process runs in another must not get a
        verification out of it."""
        out = lever_echo.echo_block_for_run_dir(
            self.ran, declared_case=self.claimed)
        # 1. Nothing downstream may read this as a verification.
        self.assertEqual(lever_echo.parse_echo(out), {})
        field = lever_echo.levers_verified_active(out)
        self.assertEqual(field["verified"], [])
        self.assertIn("unverifiable", field["basis"])
        # 2. And the refusal is VISIBLE, with both paths named -- a filter
        #    nobody can see is a filter nobody can question.
        self.assertIn(lever_echo.REFUSED, out)
        self.assertIn("L-45", out)
        self.assertIn(str(self.ran.resolve()), out)
        self.assertIn(str(self.claimed.resolve()), out)
        # 3. It must not smuggle either case's dictionaries in.
        self.assertNotIn(self._sha(self.claimed, "system/fvSchemes"), out)
        self.assertNotIn(self._sha(self.ran, "system/fvSchemes"), out)

    def test_a_matching_declared_case_echoes_normally(self):
        for declared in (self.ran, str(self.ran) + "/.",
                         self.ran.parent / self.ran.name):
            with self.subTest(declared=str(declared)):
                out = lever_echo.echo_block_for_run_dir(
                    self.ran, declared_case=declared)
                echoed = lever_echo.parse_echo(out)
                self.assertEqual(echoed["system/fvSchemes"],
                                 self._sha(self.ran, "system/fvSchemes"))

    def test_a_directory_with_no_levers_refuses_rather_than_claiming_nothing(self):
        """Launched from somewhere that is not a case at all -- the repo root,
        say. An empty echo block would parse as a verification of zero files;
        a refusal says why."""
        empty = self.tmp / "not-a-case"
        empty.mkdir()
        out = lever_echo.echo_block_for_run_dir(empty)
        self.assertIn(lever_echo.REFUSED, out)
        self.assertIn("nothing to hash", out)
        self.assertEqual(lever_echo.levers_verified_active(out)["verified"], [])

    def test_the_refusal_fence_cannot_be_mistaken_for_an_echo(self):
        """The refusal must not contain the BEGIN marker, or every downstream
        parser would read a refusal as an empty verification."""
        out = lever_echo.refusal_block("any reason at all", a=1)
        self.assertNotIn(lever_echo.BEGIN, out)
        self.assertNotIn(lever_echo._FILE_MARK, out)


def _field_file(root: Path, name: str, n_cells: int, bc_type: str) -> Path:
    """A 0/ field file shaped like OpenFOAM writes one after an
    initialization pass: a lever-bearing boundaryField wrapped around bulk
    nonuniform data."""
    body = "\n".join(f"({i} 0 0)" for i in range(n_cells))
    faces = "\n".join(f"({i} 0 0)" for i in range(n_cells // 2))
    path = root / "0" / name
    path.write_text(
        _foam_file("volVectorField", name)
        + "dimensions      [0 1 -1 0 0 0 0];\n"
        + f"internalField   nonuniform List<vector>\n{n_cells}\n({body})\n;\n"
        + "boundaryField\n{\n    farfield\n    {\n"
          "        type            freestreamVelocity;\n"
          "        freestreamValue uniform (0 0 100);\n"
        + f"        value           nonuniform List<vector>\n{n_cells // 2}\n"
          f"({faces})\n;\n"
        + "    }\n    body\n    {\n        type            noSlip;\n"
          "    }\n}\n")
    return path


class EchoSizeAndLeverIdentityTests(unittest.TestCase):
    """The echo must record levers, not solution fields.

    WHY THIS TEST EXISTS. On B-52 rung 6 the echo block was 24.6 MB of a
    25.2 MB solver log -- 97.8% -- because `0/` is treated as the BC
    dictionaries while, after a `potentialFoam -writephi` pass, it holds
    computed fields too: `0/U` contributed 13.1 MB and `0/phi` 11.5 MB. The
    same root cause failed the B-52 arm's G4 replicate-equality clause on
    exactly those two files, because solutions on two different meshes can
    never be equal and comparing them was never comparing levers.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-size-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)

    def test_bulk_field_data_does_not_reach_the_log(self):
        path = _field_file(self.case, "U", 40000, "freestreamVelocity")
        self.assertGreater(path.stat().st_size, 400_000)
        block = lever_echo.echo_block(self.case)
        self.assertLess(len(block), 20_000,
                        "the echo block is still carrying bulk field data")

    def test_the_levers_themselves_survive_verbatim(self):
        _field_file(self.case, "U", 40000, "freestreamVelocity")
        block = lever_echo.echo_block(self.case)
        for lever in ("type            freestreamVelocity;",
                      "freestreamValue uniform (0 0 100);",
                      "type            noSlip;",
                      "dimensions      [0 1 -1 0 0 0 0];"):
            with self.subTest(lever=lever):
                self.assertIn(lever, block)

    def test_every_elision_is_accounted_for_not_merely_absent(self):
        _field_file(self.case, "U", 40000, "freestreamVelocity")
        block = lever_echo.echo_block(self.case)
        markers = [l for l in block.splitlines() if lever_echo._ELIDED in l]
        self.assertEqual(len(markers), 2, "internalField and the per-face "
                                          "boundary values should both go")
        for line in markers:
            self.assertRegex(line, r"\d+ entries")
            self.assertRegex(line, r"\d+ bytes")
            self.assertRegex(line, r"sha256 [0-9a-f]{64}")

    def test_the_whole_file_binding_is_never_weakened_by_elision(self):
        """`sha256` must still be the hash of the exact bytes on disk. That is
        the charter's binding and elision must not touch it."""
        path = _field_file(self.case, "U", 40000, "freestreamVelocity")
        echoed = lever_echo.parse_echo(lever_echo.echo_block(self.case))
        self.assertEqual(echoed["0/U"],
                         hashlib.sha256(path.read_bytes()).hexdigest())

    def test_two_meshes_one_recipe_agree_on_levers_and_differ_on_files(self):
        """G4, the clause that failed. Same recipe, different mesh sizes: the
        FILES differ by construction and always will; the LEVERS are what a
        same-recipe claim is about, and they must compare equal."""
        other = _fixture_case(self.tmp / "replicate")
        _field_file(self.case, "U", 40000, "freestreamVelocity")
        _field_file(other, "U", 41000, "freestreamVelocity")   # finer mesh
        a, b = (lever_echo.echo_block(c) for c in (self.case, other))
        self.assertNotEqual(lever_echo.parse_echo(a)["0/U"],
                            lever_echo.parse_echo(b)["0/U"],
                            "different field data must still hash differently")
        self.assertEqual(lever_echo.parse_echo_levers(a)["0/U"],
                         lever_echo.parse_echo_levers(b)["0/U"],
                         "same recipe on two meshes must agree on LEVERS")

    def test_a_changed_lever_still_breaks_lever_equality(self):
        """The other direction, or the comparison would be worthless: elision
        must not hide an actual lever difference."""
        other = _fixture_case(self.tmp / "replicate")
        _field_file(self.case, "U", 40000, "freestreamVelocity")
        p = _field_file(other, "U", 41000, "freestreamVelocity")
        p.write_text(p.read_text().replace("noSlip", "slip"))
        self.assertNotEqual(
            lever_echo.parse_echo_levers(lever_echo.echo_block(self.case))["0/U"],
            lever_echo.parse_echo_levers(lever_echo.echo_block(other))["0/U"])

    def test_small_uniform_entries_are_left_alone(self):
        block = lever_echo.echo_block(self.case)
        self.assertNotIn(lever_echo._ELIDED, block)
        self.assertIn("freestreamVelocity", block)

    def test_a_pre_split_log_still_parses_both_ways(self):
        """Backward compatibility: logs written before the lever hash existed
        carry one hash, and must keep parsing as they always did."""
        old = (f"{lever_echo.BEGIN}\ncase /x\n"
               f"{lever_echo._FILE_MARK} system/fvSchemes sha256 {'a'*64} ----\n"
               f"divSchemes {{}}\n{lever_echo.END}\n")
        self.assertEqual(lever_echo.parse_echo(old),
                         {"system/fvSchemes": "a" * 64})
        self.assertEqual(lever_echo.parse_echo_levers(old),
                         {"system/fvSchemes": "a" * 64})
        field = lever_echo.levers_verified_active(old)
        self.assertEqual(field["verified"][0]["lever_sha256"], "a" * 64)


class SolverInvocationTests(unittest.TestCase):
    """`launches_a_solver` is the one place the lab decides whether a launch
    is a solve. Six launchers used to answer it separately, or not at all."""

    def test_a_solver_at_any_argument_position_is_a_solve(self):
        for args in (["simpleFoam"],
                     ["mpirun", "-np", "2", "simpleFoam", "-parallel"],
                     ["mpirun", "-np", "48", "rhoSimpleFoam", "-parallel"],
                     ["potentialFoam", "-writephi"]):
            with self.subTest(args=args):
                self.assertTrue(lever_echo.launches_a_solver(args))

    def test_utilities_are_not_solves(self):
        for args in (["blockMesh"], ["checkMesh", "-allGeometry"],
                     ["decomposePar", "-force"], ["reconstructPar"],
                     ["mpirun", "-np", "2", "redistributePar", "-parallel"]):
            with self.subTest(args=args):
                self.assertFalse(lever_echo.launches_a_solver(args))

    def test_a_solver_binary_running_postprocess_is_not_a_solve(self):
        """`simpleFoam -postProcess -func yPlus` integrates nothing; its log
        belongs to a utility parser and there is no switch-that-ran question
        to answer. Keying on the solver NAME alone cannot see this, which is
        the same mistake as keying on args[0]."""
        self.assertFalse(lever_echo.launches_a_solver(
            ["simpleFoam", "-postProcess", "-func", "yPlus", "-latestTime"]))

    def test_echo_if_solver_returns_the_block_or_nothing(self):
        tmp = Path(tempfile.mkdtemp(prefix="lever-invoke-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        case = _fixture_case(tmp)
        block = lever_echo.echo_if_solver(["simpleFoam"], case)
        self.assertIn("system/fvSchemes", lever_echo.parse_echo(block))
        self.assertEqual(lever_echo.echo_if_solver(["blockMesh"], case), "")


class DetachedSolveWrapperTests(unittest.TestCase):
    """The four detached/watched solver paths inside `tmr_verification` used
    to launch straight into `bash -c` with no echo at all -- and they are the
    paths the LONGEST solves use. Routed through the canonical emitter
    2026-08-10 (P-4.1 C+D). The exit-file protocol is untouched, and these
    tests are what says so."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-detach-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)

    def _run(self, command: list[str]) -> tuple[str, str]:
        wrapper = tv._detached_solve_wrapper(command, "log.simpleFoam")
        subprocess.run(["bash", "-c", wrapper], cwd=str(self.case),
                       timeout=120, capture_output=True)
        return ((self.case / "log.simpleFoam").read_text(errors="replace"),
                (self.case / "solve.exit").read_text().strip())

    def test_the_detached_wrapper_emits_the_echo_before_the_solver(self):
        text, _ = self._run(["/bin/echo", "solver-output-here"])
        self.assertTrue(text.startswith(lever_echo.BEGIN))
        echoed = lever_echo.parse_echo(text)
        self.assertEqual(
            echoed["system/fvSolution"],
            hashlib.sha256(
                (self.case / "system" / "fvSolution").read_bytes()).hexdigest())
        self.assertIn("solver-output-here", text)
        self.assertLess(text.index(lever_echo.END),
                        text.index("solver-output-here"))

    def test_solve_exit_still_carries_the_SOLVERS_exit_code(self):
        """The protocol every detached poll depends on. If the echo command's
        status ever leaked into `solve.exit`, a failed solve would be
        collected as a successful one."""
        _, code = self._run(["/bin/sh", "-c", "exit 7"])
        self.assertEqual(code, "7", "solve.exit did not carry the solver's "
                                    "exit code -- the polling protocol broke")

    def test_a_successful_solve_still_writes_zero(self):
        _, code = self._run(["/bin/true"])
        self.assertEqual(code, "0")

    def test_the_log_is_created_by_the_shell_not_by_python(self):
        """The callers' launch check is `if not log_path.exists(): raise`.
        Pre-seeding the log from Python would make that check vacuous, so the
        emitter must be what creates it."""
        wrapper = tv._detached_solve_wrapper(["/bin/true"], "log.simpleFoam")
        self.assertFalse((self.case / "log.simpleFoam").exists(),
                         "building the wrapper must not itself write the log")
        self.assertIn("lever_echo_emit.py", wrapper)
        self.assertTrue(tv._LEVER_ECHO_EMIT.exists(),
                        f"the emitter is missing at {tv._LEVER_ECHO_EMIT}")


class SupersededLogTests(unittest.TestCase):
    """L-42: a rerun into an existing case directory must not destroy the
    prior run's log.

    WHY THIS TEST EXISTS. `MODEL_FORM_runs/H_re10595_realizableKE`'s governing
    record states 30,000 iterations beside a log that ends at 12,000. Nothing
    was falsified -- a later rerun overwrote the log in place and both records
    were honest about their own run -- but the earlier run's activity evidence
    stopped existing anywhere, so no conclusion resting on it can ever be
    re-verified. It survived only because the two runs agreed, which is a coin
    landing the right way rather than a defense. Every launch path in this
    module truncated or unlinked, so the whole family had the defect.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-supersede-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.case = _fixture_case(self.tmp)
        self.log = self.case / "log.simpleFoam"

    def test_an_existing_log_is_preserved_with_its_content(self):
        self.log.write_text("Time = 30000\nEnd\n")
        archive = tv._supersede_log(self.log)
        self.assertIsNotNone(archive, "the prior log was not archived")
        # Content, not merely existence: the evidence must still be readable.
        self.assertEqual(archive.read_text(), "Time = 30000\nEnd\n")
        self.assertTrue(archive.name.startswith("superseded_"))
        self.assertTrue(archive.name.endswith("log.simpleFoam"))

    def test_the_archive_name_follows_the_launcher_utc_stamp_convention(self):
        self.log.write_text("x\n")
        archive = tv._supersede_log(self.log)
        stamp = archive.name[len("superseded_"):-len("_log.simpleFoam")]
        # Same shape launch_solve.sh stamps its registry logs with: the one
        # launch path that already survived L-42, by accident.
        self.assertRegex(stamp, r"^\d{8}T\d{6}Z(_\d+)?$")

    def test_the_live_name_is_free_afterwards(self):
        """THE property that keeps the callers' launch check meaningful: the
        detached paths test `if not log_path.exists(): raise` to decide
        whether the shell ran. If this left anything at the live name, that
        check would pass whether or not the launch happened -- a fix that
        creates the artifact a check tests for disables the check."""
        for content in ("Time = 1\n", ""):
            with self.subTest(content=repr(content)):
                self.log.write_text(content)
                tv._supersede_log(self.log)
                self.assertFalse(self.log.exists())

    def test_the_archive_is_invisible_to_every_log_glob_in_the_repo(self):
        """This fix CREATES artifacts, so every check that reads those
        artifacts got re-examined (guidelines 5.1, in the other direction).

        Five places select a case's run log by glob. One of them,
        `sdk/scripts/replay_s12_unsettled_stop.py`, takes the LARGEST match --
        so an archive named `log.simpleFoam.superseded_<stamp>` that happened
        to be bigger than the live log would have been classified AS the run.
        The stamp therefore goes in front of the name, and this test is what
        stops a future tidy-up from moving it back.
        """
        import fnmatch
        self.log.write_text("Time = 1\n")
        name = tv._supersede_log(self.log).name
        for pattern in ("log.*", "log.*Foam", "log.simpleFoam*", "*.log"):
            with self.subTest(pattern=pattern):
                self.assertFalse(
                    fnmatch.fnmatch(name, pattern),
                    f"archive {name!r} is picked up by a consumer globbing "
                    f"{pattern!r}, which selects run logs")

    def test_an_empty_log_is_not_archived_as_evidence(self):
        self.log.write_text("")
        self.assertIsNone(tv._supersede_log(self.log))
        self.assertEqual(list(self.case.glob("*superseded*")), [])

    def test_a_missing_log_is_not_an_error(self):
        self.assertIsNone(tv._supersede_log(self.log))

    def test_two_reruns_in_one_second_do_not_collide(self):
        first_names = set()
        for i in range(3):
            self.log.write_text(f"run {i}\n")
            first_names.add(tv._supersede_log(self.log).name)
        self.assertEqual(len(first_names), 3,
                         "a same-second rerun overwrote an earlier archive")
        self.assertEqual(len(list(self.case.glob("superseded_*"))), 3)

    def test_the_settle_watched_path_archives_too(self):
        """Found by the cross-family propagation sweep, not by the pass that
        wrote _supersede_log: this launch path had the lever echo added and
        the archive call forgotten, so it was the one launch in the module
        that still destroyed a prior run's log."""
        import inspect
        src = inspect.getsource(tv._run_simplefoam_to_settle)
        self.assertIn("_supersede_log(log_path)", src)
        self.assertLess(src.index("_supersede_log(log_path)"),
                        src.index('log_path.open("w")'),
                        "the archive must happen BEFORE the truncating open")

    def test_the_shared_archiver_supersedes_a_committed_log(self):
        """L-42's archive side. `_copy_best_effort` is the shared archiver for
        the F5 ladders and several workflows; the committed copy is the one
        every record cites and the one the H_re10595 casualty actually lost."""
        out = self.tmp / "committed"
        out.mkdir()
        (out / "log.simpleFoam").write_text("the prior run's archived evidence\n")
        (self.tmp / "fresh.log").write_text("the new run\n")
        tv._copy_best_effort(self.tmp / "fresh.log", out / "log.simpleFoam")
        archives = list(out.glob("superseded_*_log.simpleFoam"))
        self.assertEqual(len(archives), 1)
        self.assertIn("prior run's archived evidence", archives[0].read_text())
        self.assertEqual((out / "log.simpleFoam").read_text(), "the new run\n")

    def test_the_shared_archiver_leaves_non_logs_alone(self):
        """Narrow by design: widening this guard would be a second,
        unreviewed change riding along with the first."""
        out = self.tmp / "committed2"
        out.mkdir()
        (out / "record.json").write_text("{}\n")
        (self.tmp / "new.json").write_text('{"a":1}\n')
        tv._copy_best_effort(self.tmp / "new.json", out / "record.json")
        self.assertEqual(list(out.glob("superseded_*")), [])
        self.assertEqual((out / "record.json").read_text(), '{"a":1}\n')

    def test_the_shared_runner_archives_before_it_overwrites(self):
        """End to end through `_foam`, which opens the log 'w'."""
        self.log.write_text("Time = 30000\nthe prior run's evidence\n")
        with mock.patch.object(tv, "_run_prefix", return_value=["echo"]):
            tv._foam(["simpleFoam"], self.case, "log.simpleFoam")
        archives = list(self.case.glob("superseded_*_log.simpleFoam"))
        self.assertEqual(len(archives), 1)
        self.assertIn("the prior run's evidence", archives[0].read_text())
        # And the new run's log is a real new log, echo and all.
        new_text = self.log.read_text()
        self.assertIn("system/fvSchemes", lever_echo.parse_echo(new_text))
        self.assertNotIn("the prior run's evidence", new_text)

    def test_a_superseded_echo_survives_and_stays_parseable(self):
        """The evidence this whole campaign exists to create is exactly what a
        rerun used to destroy: a hash-bound echo block."""
        with mock.patch.object(tv, "_run_prefix", return_value=["echo"]):
            tv._foam(["simpleFoam"], self.case, "log.simpleFoam")
            first = lever_echo.parse_echo(self.log.read_text())
            (self.case / "system" / "fvSchemes").write_text(
                "divSchemes { div(phi,U) Gauss upwind; }\n")
            tv._foam(["simpleFoam"], self.case, "log.simpleFoam")
        archives = list(self.case.glob("superseded_*_log.simpleFoam"))
        self.assertEqual(len(archives), 1)
        preserved = lever_echo.parse_echo(archives[0].read_text())
        self.assertEqual(preserved, first,
                         "the first run's hash-bound levers did not survive")
        self.assertNotEqual(
            lever_echo.parse_echo(self.log.read_text())["system/fvSchemes"],
            first["system/fvSchemes"],
            "the second run should record its own, different levers")


class LaunchSolveEchoTests(unittest.TestCase):
    """The launcher end-to-end: `scripts/launch_solve.sh` must emit the block
    from the launched process's own working directory."""

    LAUNCHER = Path("/home/ubuntu/Certonomous/scripts/launch_solve.sh")

    def setUp(self):
        if not self.LAUNCHER.exists():
            self.skipTest("launch_solve.sh not present")
        self.tmp = Path(tempfile.mkdtemp(prefix="lever-launch-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.registry = self.tmp / "registry"
        self.registry.mkdir()
        # The two cases differ in exactly one observable: their div scheme.
        self.ran = _preflight_clean_case(self.tmp / "actually-ran",
                                         "bounded Gauss linearUpwind grad(U)")
        self.claimed = _preflight_clean_case(self.tmp / "merely-claimed",
                                             "bounded Gauss upwind")

    def _launch(self, cwd: Path, case_arg: str | None) -> str:
        """Run the launcher and return the run log it wrote."""
        cmd = [str(self.LAUNCHER), "--name", "levertest"]
        if case_arg is not None:
            cmd += ["--case", case_arg]
        cmd += ["--", "/bin/echo", "solver-would-run-here"]
        env = dict(os.environ, SOLVE_REGISTRY=str(self.registry))
        done = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True,
                              text=True, timeout=120)
        logs = sorted(self.registry.glob("levertest_*.log"))
        # A preflight refusal writes no log and would otherwise look exactly
        # like an echo failure; say which it was.
        self.assertNotIn("REFUSING TO LAUNCH", done.stdout,
                         "the launcher refused this fixture at preflight, so "
                         "this test measured nothing about the lever echo")
        self.assertTrue(logs, "the launcher wrote no run log")
        for _ in range(50):          # the block is written by the child
            text = logs[-1].read_text(errors="replace")
            if "solver-would-run-here" in text:
                return text
            time.sleep(0.1)
        return logs[-1].read_text(errors="replace")

    def test_the_launcher_echoes_the_directory_the_solver_runs_in(self):
        text = self._launch(cwd=self.ran, case_arg=str(self.ran))
        self.assertIn(lever_echo.BEGIN, text)
        echoed = lever_echo.parse_echo(text)
        self.assertEqual(
            echoed["system/fvSchemes"],
            hashlib.sha256(
                (self.ran / "system" / "fvSchemes").read_bytes()).hexdigest())
        # The command still ran, after the block: the echo is a prefix, not a
        # replacement.
        self.assertIn("solver-would-run-here", text)
        self.assertLess(text.index(lever_echo.BEGIN),
                        text.index("solver-would-run-here"))

    def test_a_launcher_case_that_is_not_the_run_directory_is_refused(self):
        """The regression proper: describe one case, run in another, and the
        log must carry a stated refusal rather than a passing echo."""
        text = self._launch(cwd=self.ran, case_arg=str(self.claimed))
        self.assertEqual(lever_echo.parse_echo(text), {})
        self.assertIn(lever_echo.REFUSED, text)
        self.assertIn(str(self.claimed.resolve()), text)
        self.assertEqual(
            lever_echo.levers_verified_active(text)["verified"], [])
        self.assertIn("solver-would-run-here", text)

    def test_the_launcher_records_the_solvers_own_pid_not_a_wrappers(self):
        """The echo moved inside a `bash -c` wrapper; the `exec` that keeps
        $! pointing at the real process is L-6 and must not regress."""
        self._launch(cwd=self.ran, case_arg=str(self.ran))
        jobs = sorted(self.registry.glob("levertest_*.job"))
        self.assertTrue(jobs, "the launcher registered no job")
        body = jobs[-1].read_text()
        self.assertIn("JOB_PID=", body)
        pid = int(body.split("JOB_PID=")[1].split("\n")[0])
        self.assertGreater(pid, 0)
        # No surviving `bash -c` wrapper holding that pid: exec replaced it.
        ps = subprocess.run(["ps", "-o", "args=", "-p", str(pid)],
                            capture_output=True, text=True)
        self.assertNotIn("lever_echo_emit", ps.stdout)


if __name__ == "__main__":
    unittest.main()
