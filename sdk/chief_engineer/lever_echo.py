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
import re
from datetime import datetime, timezone
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


#: A ``nonuniform List`` payload longer than this is field DATA, not a lever,
#: and is elided from the echo. A uniform entry is one short line; a
#: nonuniform one carries a value per cell or per face. 4 kB keeps every
#: uniform value and small hand-written table verbatim while catching the
#: 13 MB velocity fields.
MAX_INLINE_LIST_BYTES = 4096

_ELIDED = "<<< LEVER-ECHO elided nonuniform List"

#: ``nonuniform List<vector>`` / ``List<scalar>``, an optional element count,
#: then the opening paren of the payload.
_NONUNIFORM = re.compile(r"nonuniform\s+List<\w+>\s*(\d+)?\s*\(")


def _elide_bulk_lists(text: str) -> tuple[str, str, int]:
    """Drop bulk ``nonuniform List`` payloads, keep every lever verbatim.

    A ``0/`` file mixes two different things: the boundary-condition
    SPECIFICATION -- lever class 3, the reason these files are echoed at all
    -- and field VALUES, which after an initialization pass are computed
    solution data and no kind of lever. The echo inlined both, so a
    `potentialFoam` case echoed its own output: on B-52 rung 6 the block was
    **24.6 MB of a 25.2 MB log, 97.8%**, with `0/U` at 13.1 MB and `0/phi` at
    11.5 MB -- exactly the two files `potentialFoam -writephi` writes.

    That is one defect with two faces. The second is the B-52 arm's G4
    replicate-equality clause failing on those same two files: they are
    solutions on different meshes, so they can never be equal, and comparing
    them was never comparing levers.

    The rule is one rule, not a list of special cases: **any nonuniform list
    payload over the threshold goes, wherever it appears.** That catches the
    `internalField` (a value per cell) and the per-face `value nonuniform
    List<...>` inside a `boundaryField` alike -- the second mattered, because
    eliding only `internalField` still left 640 kB of per-face data in one
    file. What survives is what a reader needs to know which lever was set:
    `type freestreamVelocity;`, `freestreamValue uniform (0 0 100);`, every
    key, every scheme. Each elided payload leaves a marker carrying its
    element count, byte count and its own sha256, so the dropped bytes are
    accounted for rather than merely absent.

    Returns ``(shown, canonical, count)``. **They differ on purpose.**
    ``shown`` is what goes in the log and names each dropped payload's element
    count, byte count and sha256, so an auditor can see exactly what was left
    out. ``canonical`` replaces the whole nonuniform entry -- element count
    included -- with a constant token, and is what ``lever_sha256`` is taken
    over. The element count is mesh size, not a lever, so it must not
    participate in a same-recipe comparison; hashing ``shown`` would have made
    every replicate differ through the very marker added to describe the
    difference, which is how the first version of this fix failed its own G4
    test.
    """
    shown: list[str] = []
    canon: list[str] = []
    pos = 0
    elided = 0
    for match in _NONUNIFORM.finditer(text):
        # Elide the WHOLE entry, from `nonuniform` through the payload: the
        # element count sits between them and is mesh size, not a lever.
        start_idx = match.start()
        open_idx = match.end() - 1          # the '(' itself
        if start_idx < pos:                 # inside an entry already taken
            continue
        depth = 0
        close_idx = -1
        for i in range(open_idx, len(text)):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    close_idx = i
                    break
        if close_idx == -1:                 # unbalanced: leave it alone
            continue
        payload = text[open_idx:close_idx + 1]
        size = len(payload.encode())
        if size <= MAX_INLINE_LIST_BYTES:
            continue
        digest = hashlib.sha256(payload.encode()).hexdigest()
        head = text[pos:start_idx]
        shown.append(head)
        canon.append(head)
        shown.append(f"{_ELIDED}: {match.group(1) or 'unstated'} entries, "
                     f"{size} bytes, sha256 {digest} >>>")
        canon.append(f"{_ELIDED} >>>")
        pos = close_idx + 1
        elided += 1
    shown.append(text[pos:])
    canon.append(text[pos:])
    return "".join(shown), "".join(canon), elided


def echo_block(case_dir: Path) -> str:
    """The fenced LEVER-ECHO text for a case: every lever dictionary that
    exists, each under a header carrying its case-relative name, the sha256 of
    the exact bytes on disk, and the sha256 of the text echoed here.

    Two hashes, because they answer two questions and one cannot do both.
    ``sha256`` binds the entry to the exact bytes that ran -- the charter's
    binding, never weakened. ``lever_sha256`` covers what this block actually
    shows, which for a field file is the boundary specification with the bulk
    internal data elided. Comparing LEVERS across two runs means comparing the
    second; comparing whole files means comparing the first. The B-52 G4
    clause compared the first and failed on two solution fields.
    """
    case_dir = Path(case_dir)
    lines = [BEGIN, f"case {case_dir}"]
    for path in _echo_targets(case_dir):
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        rel = path.relative_to(case_dir).as_posix()
        shown, canonical, _ = _elide_bulk_lists(
            data.decode(errors="replace"))
        shown = shown.rstrip("\n")
        lever = hashlib.sha256(canonical.rstrip("\n").encode()).hexdigest()
        lines.append(f"{_FILE_MARK} {rel} sha256 {digest} "
                     f"lever_sha256 {lever} ----")
        lines.append(shown)
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


def supersede_log(log_path: Path) -> Path | None:
    """Move an existing run log aside before a new run would destroy it.

    L-42, enforced 2026-08-10. A rerun into an existing case directory used to
    overwrite the prior run's log in place -- `_foam` opened it ``"w"`` and the
    detached paths ``unlink``ed it -- so the earlier run's activity evidence
    stopped existing anywhere. The measured casualty is
    `MODEL_FORM_runs/H_re10595_realizableKE`, whose governing record states
    30,000 iterations beside a log that ends at 12,000: the 03:46 run's fields
    survive under `30000/`, its LOG was destroyed by a 23:52 rerun, and no
    conclusion resting on it can ever be re-verified. Nothing was falsified;
    both records were honest about their own run. The record survived only
    because the two runs happened to agree, which L-42 calls a coin landing
    the right way rather than a defense.

    The naming follows `scripts/launch_solve.sh`, which is the only launch
    path that already survives this -- its logs carry a UTC stamp and so never
    collide. That was an accident of its registry design; here it is
    deliberate, and it is the same supersede-don't-delete convention the
    records themselves use (L-39).

    **On return, ``log_path`` does not exist.** That is load-bearing: the
    detached callers test ``if not log_path.exists(): raise`` to decide
    whether the launch happened, so leaving an empty file behind would
    silently disable their launch check -- the failure mode section 5 of the
    family guidelines records as a worked example. An empty log carries no
    evidence, so it is removed rather than archived.

    Returns the archive path, or None when there was nothing worth keeping.
    """
    log_path = Path(log_path)
    try:
        if not log_path.is_file():
            return None
        if log_path.stat().st_size == 0:
            log_path.unlink()
            return None
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        # The stamp goes in FRONT of the name, not after it. `log.simpleFoam
        # .superseded_<stamp>` would read better and would be a bug: five
        # places in this repo select a case's run log by globbing `log.*`,
        # `log.*Foam` or `log.simpleFoam*`, and one of them
        # (`replay_s12_unsettled_stop.py`) picks the LARGEST match -- so an
        # archive bigger than the live log would silently be classified as
        # the run. This fix creates artifacts, so every check that reads
        # those artifacts had to be re-examined; the prefix form matches none
        # of the five patterns, and a test pins that.
        dest = log_path.with_name(f"superseded_{stamp}_{log_path.name}")
        n = 1
        while dest.exists():          # two runs inside one second
            dest = log_path.with_name(
                f"superseded_{stamp}_{n}_{log_path.name}")
            n += 1
        log_path.rename(dest)
        return dest
    except OSError:
        # Never block a launch on its own bookkeeping. A lost archive costs
        # one run's evidence; a refused launch costs the run.
        return None


ENVELOPE_BEGIN = "==== RUNTIME-ENVELOPE BEGIN ===="
ENVELOPE_END = "==== RUNTIME-ENVELOPE END ===="


def runtime_envelope_block(**limits: Any) -> str:
    """The EFFECTIVE execution envelope, written into the run log at launch.

    L-40 in the memory dimension (2026-08-10). A pre-registration declared a
    22 GiB container cap; the runner that executed applied its own, and
    nothing in between raised its hand. It had no effect that time -- peak was
    7.0 GiB -- and it was found only because one agent stated a number and
    another compared. That is the same shape as an echo certifying
    dictionaries the solve did not use: **the record said one thing, the
    execution did another, and the gap was silent.**

    A resource cap is a lever, so charter section 9 governs it: verified from
    the EXECUTION, never from the declaration. This block records what
    actually bound -- not what was asked for -- so an arm is self-documenting
    on this axis and a later reader never has to trust a prose number.

    Pass every limit that shaped the run, including the ones that are NOT
    set: ``cpus=None`` records "uncapped" as a fact, which is the difference
    between a limit that was chosen and a limit nobody applied. An absent line
    and an unrecorded value are indistinguishable to whoever reads this later.
    """
    lines = [ENVELOPE_BEGIN]
    for key in sorted(limits):
        value = limits[key]
        lines.append(f"{key} {'UNCAPPED' if value is None else value}")
    lines.append(ENVELOPE_END)
    return "\n".join(lines) + "\n"


def parse_runtime_envelope(log_text: str) -> dict[str, str]:
    """``{limit: effective value}`` from a log's RUNTIME-ENVELOPE block;
    empty when the log carries none."""
    if ENVELOPE_BEGIN not in log_text:
        return {}
    block = log_text.split(ENVELOPE_BEGIN, 1)[1].split(ENVELOPE_END, 1)[0]
    out: dict[str, str] = {}
    for line in block.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            out[parts[0]] = parts[1].strip()
    return out


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


def parse_echo_levers(log_text: str) -> dict[str, str]:
    """``{case-relative file name: lever sha256}`` -- the hash of the LEVER
    CONTENT, which is what two runs of the same recipe must agree on.

    Use this, not :func:`parse_echo`, to compare two runs. A field file's
    whole-file hash includes its internal data, so two replicates on different
    meshes differ there by construction and always will; their boundary
    SPECIFICATIONS are what a same-recipe claim is about. Logs written before
    2026-08-10 carry no lever hash and fall back to the whole-file one, which
    is what those logs can support and no more.
    """
    if BEGIN not in log_text:
        return {}
    block = log_text.split(BEGIN, 1)[1].split(END, 1)[0]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if not line.startswith(_FILE_MARK):
            continue
        parts = line.split()
        try:
            name = parts[3]
        except IndexError:
            continue
        for key in ("lever_sha256", "sha256"):
            if key in parts:
                out[name] = parts[parts.index(key) + 1]
                break
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
    levers = parse_echo_levers(log_text)
    return {"verified": [
                {"file": name, "sha256": digest,
                 # The lever hash is what a same-recipe comparison uses; it
                 # equals `sha256` on logs written before the split.
                 "lever_sha256": levers.get(name, digest),
                 "evidence": f"LEVER-ECHO block at head of the solver log, "
                             f"file {name}"}
                for name, digest in sorted(echoed.items())],
            "basis": "launcher echo, hash-bound to the dictionaries that "
                     "ran (Verification Charter v1.5 section 9)"}
