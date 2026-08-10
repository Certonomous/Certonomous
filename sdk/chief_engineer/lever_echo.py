"""Lever echo: the launcher prints the dictionaries that ran, or the lever
prints its own banner (Verification Charter v1.5 section 9,
``levers_verified_active``; adopted 2026-08-08 on the dead-lever audit).

The audit verified 126 lever/conclusion pairs from runtime logs and found
every one of its 16 unverifiable entries traces to four lever classes stock
OpenFOAM structurally never echoes: fvSchemes tokens (no scheme selection is
printed on success), fvSolution ``consistent`` (SIMPLEC prints the same
banner either way), boundary-condition types, and silent dictionary values
(MRF omega, thermophysical mu). For those classes no discipline at
record-writing time can recover the evidence afterwards -- the F5c headline's
algorithm attribution is unverifiable forever from its existing logs.

So the launcher echoes the levers into the run log at t=0, fenced and
hash-bound: each echoed file carries its sha256, so the echo is bound to the
exact bytes that ran, the same binding the mesh birth certificate uses. A
``levers_verified_active`` entry then cites either a lever's own activation
banner (the sub-LU pattern: printed at activation, distinguishable
off-state, hard-fail on unrecognized values) or the echo block's line for
that file.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

BEGIN = "==== LEVER-ECHO BEGIN ===="
END = "==== LEVER-ECHO END ===="
_FILE_MARK = "---- LEVER-ECHO file"

#: The dictionaries carrying the audit's four echo-less lever classes.
ECHO_FILES = (
    "system/fvSchemes",
    "system/fvSolution",
    "constant/turbulenceProperties",
    "constant/transportProperties",
    "constant/thermophysicalProperties",
    "constant/MRFProperties",
)

#: Solvers whose launch earns an echo. Utility logs stay pristine so their
#: parsers read exactly what they always read.
SOLVERS = frozenset({
    "simpleFoam", "pimpleFoam", "pisoFoam", "icoFoam", "rhoSimpleFoam",
    "rhoCentralFoam", "rhoPimpleFoam", "sonicFoam", "interFoam",
    "potentialFoam", "dafoam",
})


#: Flags that turn a solver binary into a post-processing utility. A launch
#: spelled ``simpleFoam -postProcess -func yPlus`` runs no solve: it writes a
#: utility log whose parsers expect utility output, and there is no "the
#: switch that ran" question to answer because nothing was integrated. The
#: solver-name test alone cannot tell the two apart, which is the same class
#: of mistake as testing ``args[0]`` -- keying on a spelling instead of on
#: what the invocation does.
UTILITY_FLAGS = frozenset({"-postProcess"})


def launches_a_solver(args: list[str]) -> bool:
    """Whether this argument vector actually RUNS a solver.

    Membership is over ALL arguments, never ``args[0]``: a parallel launch
    spells the solver ``mpirun -np N <solver> -parallel``, and an
    ``args[0]``-only test silently skipped the echo on exactly the runs a
    lever gate matters most on (fixed 2026-08-10, commit 199e9d17).
    """
    if any(arg in UTILITY_FLAGS for arg in args):
        return False
    return any(arg in SOLVERS for arg in args)


def echo_if_solver(args: list[str], run_dir: Path) -> str:
    """The echo block when ``args`` launches a solver in ``run_dir``, and the
    empty string otherwise -- the one place that decision is made.

    Every launcher in the lab routes its echo through this: the shared runner,
    the detached solve wrapper, and the two workflow scripts that used to
    carry private copies. One predicate and one format, because two
    implementations of a proof format are two things that can disagree about
    what was proved.
    """
    return echo_block_for_run_dir(run_dir) if launches_a_solver(args) else ""


def _echo_targets(case_dir: Path) -> list[Path]:
    case_dir = Path(case_dir)
    targets = [case_dir / rel for rel in ECHO_FILES]
    # The 0/ boundary-condition files: class 3, never echoed at runtime by
    # the solver itself.
    zero = case_dir / "0"
    if zero.is_dir():
        targets.extend(sorted(p for p in zero.iterdir() if p.is_file()))
    return [p for p in targets if p.is_file()]


def echo_block(case_dir: Path) -> str:
    """The fenced LEVER-ECHO text for a case: every lever dictionary that
    exists, each under a header carrying its case-relative name and the
    sha256 of the exact bytes echoed."""
    case_dir = Path(case_dir)
    lines = [BEGIN, f"case {case_dir}"]
    for path in _echo_targets(case_dir):
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        rel = path.relative_to(case_dir).as_posix()
        lines.append(f"{_FILE_MARK} {rel} sha256 {digest} ----")
        lines.append(data.decode(errors="replace").rstrip("\n"))
    lines.append(END)
    return "\n".join(lines) + "\n"


#: Fence for the block written when an echo is REFUSED. Deliberately does not
#: contain ``BEGIN``, so :func:`parse_echo` reads it as no echo at all and
#: ``levers_verified_active`` reports ``unverifiable`` -- the gate fails OPEN.
REFUSED = "==== LEVER-ECHO REFUSED ===="
REFUSED_END = "==== LEVER-ECHO REFUSED END ===="


def refusal_block(reason: str, **facts: Any) -> str:
    """A stated refusal to mint an echo, in place of one.

    A filter nobody can see is a filter nobody can question (the family's
    schema-rails principle), so a refused echo says so in the run log with
    the facts that refused it, rather than leaving a silent absence that
    reads exactly like a pre-adoption log.
    """
    lines = [REFUSED, f"reason {reason}"]
    lines += [f"{k} {v}" for k, v in facts.items()]
    lines.append(REFUSED_END)
    return "\n".join(lines) + "\n"


def echo_block_for_run_dir(run_dir: Path,
                           declared_case: Path | str | None = None) -> str:
    """The echo for the directory a process is ACTUALLY RUNNING IN.

    L-45, 2026-08-10. ``scripts/launch_solve.sh`` used to mint its echo from
    the caller-supplied ``--case`` path while the command itself ran under
    ``setsid nohup "$@"`` in the launcher's inherited working directory, with
    nothing binding the two. A mismatched ``--case`` would therefore have
    written an echo of dictionaries that DID NOT RUN at the head of the log of
    a solve that did -- a manufactured verification, indistinguishable
    downstream from a real one. (It never fired: every registry log predates
    the echo's adoption by twenty hours. The channel was open, not used.)

    So the evidence is derived from the thing that executed. ``run_dir`` is
    the process's own working directory, read inside the launched process
    rather than passed in by whoever described the launch. ``declared_case``,
    when given, is the caller's CLAIM about that directory: it is used only to
    DISAGREE with. Agreement echoes ``run_dir``; disagreement refuses, because
    the two paths differing means nobody can say which directory the solver
    will open its dictionaries from, and an unverified record is cheap while a
    falsely-verified one costs the whole corpus the gate ever touched.
    """
    run = Path(run_dir).resolve()
    if declared_case is not None:
        declared = Path(declared_case).resolve()
        if declared != run:
            return refusal_block(
                "the declared --case is not the directory this process runs "
                "in; refusing to certify dictionaries that may not be the "
                "ones the solver opens (LESSONS.md L-45)",
                declared_case=declared, run_directory=run)
    if not _echo_targets(run):
        return refusal_block(
            "no lever dictionaries under the directory this process runs in; "
            "nothing to hash, so nothing is claimed",
            run_directory=run)
    return echo_block(run)


def parse_echo(log_text: str) -> dict[str, str]:
    """``{case-relative file name: sha256}`` from a log's LEVER-ECHO block;
    empty when the log carries none (every log written before adoption)."""
    if BEGIN not in log_text:
        return {}
    block = log_text.split(BEGIN, 1)[1].split(END, 1)[0]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if line.startswith(_FILE_MARK):
            parts = line.split()
            try:
                name = parts[3]
                digest = parts[parts.index("sha256") + 1]
            except (IndexError, ValueError):
                continue
            out[name] = digest
    return out


def levers_verified_active(log_text: str) -> dict[str, Any]:
    """The record field the charter's section 9 names, built mechanically
    from the log itself: which lever dictionaries the launcher proved at
    t=0, cited by hash. A log with no echo block says so plainly instead of
    implying the levers were checked."""
    echoed = parse_echo(log_text)
    if not echoed:
        return {"verified": [],
                "basis": "no lever echo in this log; dictionary levers are "
                         "unverifiable from it (pre-adoption log, or the "
                         "launcher did not echo)"}
    return {"verified": [
                {"file": name, "sha256": digest,
                 "evidence": f"LEVER-ECHO block at head of the solver log, "
                             f"file {name}"}
                for name, digest in sorted(echoed.items())],
            "basis": "launcher echo, hash-bound to the dictionaries that "
                     "ran (Verification Charter v1.5 section 9)"}
