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
