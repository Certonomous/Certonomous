#!/usr/bin/env python3
"""PRE-SHOOT CONFORMANCE GATE — can every registered demo act actually start?

WHY THIS EXISTS, and it is a specific event rather than a principle. On
2026-09-01 at 04:43Z the jet-flap act stopped being able to start. A figure
generator ran, wrote ``figure_provenance.json`` holding only its own four
entries, and two figures the act displays were left with no provenance. The
act's own guard refused correctly -- "a picture whose grid cannot be named
must not go on camera" -- but nothing ASKED it until a lane happened to drive
the act five minutes later, for an unrelated reason. Between those two moments
the demo was broken and the lab did not know.

The record it depends on is not even in git: it exists only on disk, as the
union of whichever generators have run since it was last cleared. So any lane
that clears the artefacts directory and re-runs one generator breaks every act
that displays a figure from another, silently.

THE POINT IS THE MOMENT, NOT THE CHECK. ``validate_act`` already existed and
already worked. What did not exist was anything that ran it BEFORE the curtain
went up. This is that: one command, run it before a shoot.

    python3 scripts/check_demo_acts.py

Exit 0 when every act can start, 1 when any cannot, 2 when the harness itself
could not run -- never a silent pass.

THIS GATE HAS BEEN SEEN TO FAIL. ``--selftest`` plants a missing provenance
entry into a copy of the record and asserts the gate reports it, then restores.
A gate never observed failing is not known to work; that is CLAUDE.md rule 3's
planted control applied to a check rather than to a reader, and it is the same
finding VERIFICATION_CHARTER 2n.18 records against guards two supervisors had
personally read and certified.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(REPO / "scripts"))

#: Importing an act module is what registers it; the registry is populated by
#: import side effect and nothing walks the package for us. Listed explicitly
#: so a missing act is a visible edit here rather than a silent empty run.
ACT_MODULES = ("workflows.jet_flap_act", "workflows.adjoint_act")


def _load_acts() -> dict:
    from workflows.demo_mode import registered_acts

    for name in ACT_MODULES:
        __import__(name)
    return dict(registered_acts())


def _problems() -> dict:
    """Every registered act's problem list, by key. The gate's raw reading.

    Separated from :func:`check` so the selftest can compare problem SETS
    rather than exit codes; an exit code cannot tell a gate that saw the plant
    from one that was already failing for another reason.
    """
    from workflows.demo_mode import validate_act

    out = {}
    for key, act in _load_acts().items():
        try:
            out[key] = list(validate_act(act))
        except Exception as exc:                   # noqa: BLE001 - reported
            out[key] = [f"validation raised {type(exc).__name__}: {exc}"]
    return out


def check(verbose: bool = True) -> int:
    """Validate every registered act. Returns the process exit code."""
    from workflows.demo_mode import validate_act

    try:
        acts = _load_acts()
    except Exception as exc:                       # noqa: BLE001 - reported
        print(f"HARNESS FAILED: could not import the acts: "
              f"{type(exc).__name__}: {exc}")
        return 2

    if not acts:
        print("HARNESS FAILED: no acts registered; this gate would pass "
              "vacuously and must not")
        return 2

    bad = 0
    for key in sorted(acts):
        try:
            problems = validate_act(acts[key])
        except Exception as exc:                   # noqa: BLE001 - reported
            print(f"  {key}: CANNOT START -- validation itself raised "
                  f"{type(exc).__name__}: {exc}")
            bad += 1
            continue
        if problems:
            bad += 1
            print(f"  {key}: CANNOT START -- {len(problems)} problem(s)")
            for p in problems:
                print(f"      - {p}")
        elif verbose:
            print(f"  {key}: can start")

    print(f"{len(acts) - bad} of {len(acts)} registered acts can start.")
    return 1 if bad else 0


def selftest() -> int:
    """Plant a missing provenance entry and prove the gate reports it.

    IT NEVER WRITES THE SHARED RECORD. The obvious implementation edits
    ``figure_provenance.json`` in place and restores it in a ``finally``, and
    that is wrong here for a reason this lab has already paid for: the figure
    generators write that same file, from other lanes, at unpredictable
    moments. A plant-and-restore would race them, and the restore would put
    back a version that had been superseded in between -- silently reverting
    somebody's work to fix nothing.

    So the plant is made in a TEMPORARY COPY and the reader is pointed at it,
    which tests exactly the same thing without touching a shared artifact.
    """
    import tempfile

    from workflows import _jf1_numbers

    record = Path(_jf1_numbers.RUN_ROOT) / "artefacts" / "figure_provenance.json"
    if not record.is_file():
        print("SELFTEST INCONCLUSIVE: the provenance record is not on disk, "
              "so a missing entry cannot be planted. This is itself the "
              "condition the gate exists to catch.")
        return 2
    try:
        entries = json.loads(record.read_text(encoding="utf-8"))
    except ValueError:
        print("SELFTEST INCONCLUSIVE: the record on disk is not readable "
              "JSON, so nothing can be planted into it.")
        return 2
    if not isinstance(entries, dict) or not entries:
        print("SELFTEST INCONCLUSIVE: the record holds no entries to remove.")
        return 2

    # COMPARE PROBLEM SETS, NOT EXIT CODES. Tonight the gate is already red
    # for an unrelated reason, and a selftest that only watched the exit code
    # would read "1 before, 1 after" and call itself proved. The question is
    # whether the plant introduces a problem NAMING THE ENTRY IT REMOVED,
    # which is answerable whether or not the tree is otherwise healthy.
    before = _problems()
    dropped = sorted(entries)[0]
    planted = {k: v for k, v in entries.items() if k != dropped}

    # PATCH WHERE THE READER IS DEFINED, NOT WHERE IT IS RE-EXPORTED. The
    # first cut of this selftest replaced ``_jf1_numbers.read_figure_provenance``
    # and the plant had NO EFFECT: ``assert_display_grids`` lives in
    # ``jf1_display_numbers`` and resolves the reader from that module's own
    # globals, so the re-exported alias is never consulted. The selftest
    # reported "0 new problems" and correctly failed itself. That is the
    # planted control catching the control, and it is why this plants rather
    # than reasons about what the patch would do.
    impl = _jf1_numbers._impl
    real_reader = impl.read_figure_provenance
    with tempfile.TemporaryDirectory() as tmp:
        stand_in = Path(tmp) / "figure_provenance.json"
        stand_in.write_text(json.dumps(planted, indent=2, sort_keys=True)
                            + "\n", encoding="utf-8")

        def reading_the_plant(path=None):
            return real_reader(stand_in)

        impl.read_figure_provenance = reading_the_plant
        try:
            after = _problems()
        finally:
            impl.read_figure_provenance = real_reader

    restored = _problems()
    flat_before = {p for ps in before.values() for p in ps}
    flat_after = {p for ps in after.values() for p in ps}
    new = flat_after - flat_before
    names_the_plant = [p for p in new if dropped in p]

    print()
    print(f"  problems before planting      : {len(flat_before)}")
    print(f"  problems with '{dropped}' removed: {len(flat_after)}")
    print(f"  new problems naming the plant : {len(names_the_plant)}")
    print(f"  problems after withdrawing    : "
          f"{len({p for ps in restored.values() for p in ps})}")
    print(f"  shared record written by this : no")

    if not names_the_plant:
        print("SELFTEST FAILED: removing a provenance entry produced no new "
              "problem naming it. The gate cannot see the defect it exists "
              "for.")
        return 1
    if restored != before:
        print("SELFTEST FAILED: the problem set did not return to its "
              "starting state, so the plant was not fully withdrawn.")
        return 1
    print("SELFTEST PASSED: removing one provenance entry produces a problem "
          "naming that entry, the plant withdraws cleanly, and the shared "
          "record was never written.")
    if flat_before:
        print("NOTE: the tree was ALREADY failing before the plant, so this "
              "run proves the gate reports a missing entry and does NOT "
              "prove it passes a healthy tree. Re-run when the acts are "
              "green.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true",
                        help="plant a missing provenance entry and prove the "
                             "gate reports it")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
