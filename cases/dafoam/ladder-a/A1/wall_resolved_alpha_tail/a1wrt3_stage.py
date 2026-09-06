#!/usr/bin/env python3
"""A1WRT3 -- THE STAGER.  `A1WRT3_SUCCESSOR_DRAFT.md` section 6.

WHAT IT STAGES, AND THE ONE THING IT MUST NEVER DO
==================================================
`A1WRT3` STAGES A **COPY** OF `A1WRT` U1's `4000/` AND NEVER WRITES INTO
`A1WRT`'s RUN ROOT.  The source is another item's frozen evidence; a stager
that wrote there would corrupt the artefact the seam is measured against and
would do it silently.  Every write this file makes is under `RUN_ROOT`, and
`assert_write_target()` refuses any path that is not.

THE COLD-START RESET IS NOT STAGED AND MUST NOT BE
==================================================
`A1WRT/cmd.sh:51-52` reset `0/` from `0.orig` on every unit.  It is clause C11
of the accounting and IT IS THE ONE CLAUSE THAT MUST NOT BE RESTORED -- running
it would destroy the staged `4000/` this arm exists to read back and would drive
`G-SEAM` to `GATE FAIL` FOR A REASON THAT IS NOT THE RESTART MECHANISM.  So no
`0/` is created here, no `0.orig` is staged, and the stager asserts `0/` ABSENT
after it finishes.  `a1wrt3_cmd.sh`'s C4' asserts the same thing again inside
the container, at the point of use.

THE GUARD (`CLAUDE.md` rule 4)
==============================
A case where `0/` or a time directory already exists IS REFUSED.  A stager that
overwrote a populated case would produce fields whose age says nothing, and the
age guard -- every field at `endTime` newer than the case's own age reference --
is what dates the run allowed to produce the answer.  `.a1wrt3_age_ref` is
touched LAST, so it dates the launch and nothing earlier can outrank it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

ITEM = "A1WRT3"
RUN_ROOT = Path("/home/ubuntu/certonomous-runs/A1WRT3")
SRC_CASE = Path("/home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry")
SRC_PRODUCER = Path("/home/ubuntu/certonomous-runs/A1WRT2/runScript.py")
HERE = Path(__file__).resolve().parent

PIN_RUNSCRIPT_MD5 = "d48f48c5e2e41e86981acbf6feccb3c4"

# section 6: SEAM continues 4000 -> 4200 (200 iterations); TAIL continues from
# SEAM's final state, 4,000 iterations per point.
ARM_SPEC = {
    "SEAM": {"start": 4000, "end": 4200},
    "TAIL": {"start": 4200, "end": 8200},
}

AGE_REF = ".a1wrt3_age_ref"


class Refusal(Exception):
    def __init__(self, msg, code=2):
        super().__init__(msg)
        self.code = code


def md5_of(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def assert_write_target(p: Path):
    """EVERY WRITE IS UNDER `RUN_ROOT`.  Nothing this file does may touch
    `A1WRT`'s or `A1WRT2`'s run root, or the item directory in git."""
    rp = Path(os.path.realpath(str(p)))
    root = Path(os.path.realpath(str(RUN_ROOT)))
    if root not in rp.parents and rp != root:
        raise Refusal("REFUSE: write target %s is outside %s -- this stager "
                      "never writes into another item's run root" % (rp, root))
    return p


def guard_fresh_case(case: Path):
    """`CLAUDE.md` rule 4's guard: refuse a case where `0/` or a time directory
    already exists.  An overwrite would leave fields whose age proves nothing."""
    if not case.exists():
        return
    offenders = []
    for child in sorted(case.iterdir()):
        if child.is_dir() and re.fullmatch(r"0|0\.orig|\d+(\.\d+)?", child.name):
            offenders.append(child.name)
    if offenders:
        raise Refusal("REFUSE: %s already carries time/initial directories %s -- "
                      "the guard refuses a case that already exists rather than "
                      "overwriting it" % (case, offenders))


def write_control_dict(case: Path, start: int, end: int):
    """`startFrom startTime` with an EXPLICIT `startTime`, NOT `latestTime`.

    Section 8.3 branch B is the registered outcome in which the producer resets
    on a `latestTime` start; naming the start time explicitly means that if the
    first `Time =` line still reads 1, the reset came from the producer and not
    from an ambiguous controlDict.  `writeInterval == endTime` so the final
    state is written (a non-`writeInterval` `endTime` writes no fields at all --
    a trap this family has already paid for once).
    """
    body = """/*--------------------------------*- C++ -*----------------------------------*\\
| A1WRT3 controlDict -- CONTINUED start, written by a1wrt3_stage.py           |
\\*---------------------------------------------------------------------------*/
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }

application     DASimpleFoam;
startFrom       startTime;
startTime       %(start)d;
stopAt          endTime;
endTime         %(end)d;
deltaT          1;
writeControl    timeStep;
writeInterval   %(end)d;
purgeWrite      0;
writeFormat     ascii;
writePrecision  12;
writeCompression on;
timeFormat      general;
timePrecision   12;
runTimeModifiable false;
""" % {"start": start, "end": end}
    p = assert_write_target(case / "system" / "controlDict")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    return p


def stage(arm: str, dry_run: bool = False):
    if arm not in ARM_SPEC:
        raise Refusal("REFUSE: unknown arm %r" % arm)
    spec = ARM_SPEC[arm]
    case = RUN_ROOT / arm / "case"
    out = RUN_ROOT / arm / "out"
    notes = []

    for src in (SRC_CASE, SRC_PRODUCER, HERE / "a1wrt3_cmd.sh",
                HERE / "a1wrt3_run_arm.sh"):
        if not src.exists():
            raise Refusal("REFUSE: staging source absent: %s" % src)

    src_state = SRC_CASE / str(spec["start"]) if arm == "SEAM" else \
        RUN_ROOT / "SEAM" / "case" / str(ARM_SPEC["SEAM"]["end"])
    if not src_state.is_dir():
        raise Refusal("REFUSE: continued-start state absent: %s -- this arm "
                      "continues from it and there is nothing to continue from"
                      % src_state)

    got = md5_of(SRC_PRODUCER)
    if got != PIN_RUNSCRIPT_MD5:
        raise Refusal("REFUSE: producer md5 %s != pinned %s -- the tail would "
                      "not be comparable to the alpha 0..12 body it extends"
                      % (got, PIN_RUNSCRIPT_MD5), code=4)
    notes.append("producer md5 %s == pin" % got)

    guard_fresh_case(case)
    if dry_run:
        notes.append("DRY RUN -- nothing written")
        return notes

    assert_write_target(case).mkdir(parents=True, exist_ok=True)
    assert_write_target(out).mkdir(parents=True, exist_ok=True)

    # mesh + system + constant, then THE CONTINUED STATE, as a COPY.
    for sub in ("constant", "system"):
        s = SRC_CASE / sub
        if s.is_dir():
            d = assert_write_target(case / sub)
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(s, d)
            notes.append("copied %s -> %s" % (s, d))
    dst_state = assert_write_target(case / str(spec["start"]))
    if dst_state.exists():
        shutil.rmtree(dst_state)
    shutil.copytree(src_state, dst_state)
    notes.append("staged CONTINUED state %s -> %s (a COPY; %s untouched)"
                 % (src_state, dst_state, SRC_CASE))

    write_control_dict(case, spec["start"], spec["end"])
    notes.append("controlDict startTime=%d endTime=%d writeInterval=%d"
                 % (spec["start"], spec["end"], spec["end"]))

    # The instruments, into the run root, where G-FREEZE measures them.
    for name, src in (("runScript.py", SRC_PRODUCER),
                      ("cmd.sh", HERE / "a1wrt3_cmd.sh"),
                      ("run_arm.sh", HERE / "a1wrt3_run_arm.sh")):
        d = assert_write_target(RUN_ROOT / name)
        shutil.copyfile(src, d)
        notes.append("staged %s md5=%s" % (name, md5_of(d)))

    # C11's inverse, asserted here as well as in the container.
    if (case / "0").exists():
        raise Refusal("REFUSE: a cold 0/ exists in %s after staging -- this arm "
                      "continues, it does not cold-start" % case)
    if (case / "0.orig").exists():
        raise Refusal("REFUSE: 0.orig staged into %s -- A1WRT/cmd.sh:51-52 is "
                      "deliberately not restored and its input must not be "
                      "present to tempt a restoration" % case)
    notes.append("0/ and 0.orig ABSENT after staging -- C11 not restored")

    # THE AGE REFERENCE IS TOUCHED LAST.  It dates the launch, so every field
    # the run writes at endTime must be newer than it.
    ref = assert_write_target(RUN_ROOT / AGE_REF)
    ref.write_text("")
    os.utime(ref, None)
    notes.append("%s touched LAST at %s" % (ref, time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                               time.gmtime())))

    manifest = assert_write_target(RUN_ROOT / (".a1wrt3_staged_%s.json" % arm))
    manifest.write_text(json.dumps({
        "arm": arm, "src_state": str(src_state), "case": str(case),
        "start": spec["start"], "end": spec["end"],
        "producer_md5": got,
        "cmd_sh_md5": md5_of(RUN_ROOT / "cmd.sh"),
    }, indent=1, sort_keys=True) + "\n")
    notes.append("staged-inputs record %s" % manifest)
    return notes


def main(argv=None):
    ap = argparse.ArgumentParser(prog="a1wrt3_stage.py")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        for n in stage(args.arm, args.dry_run):
            print("%s_STAGE %s" % (ITEM, n))
    except Refusal as r:
        print(str(r))
        return r.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
