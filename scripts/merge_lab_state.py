#!/usr/bin/env python3
"""THE NIGHTLY MERGER. Regenerates docs/LAB_STATE.md from docs/lab_state/*.md.

Sanaa's PLUMBING FREEZE directive, 2026-08-31: "Boards become per-team files (one
writer each), merged into the lab board by a nightly tool -- no shared-file splicing
by agents, ever." And: "Instrument repairs are done once, with the fail-closed +
planted-control standard, then the topic closes."

DERIVED, NOT MAINTAINED (VERIFICATION_CHARTER §2l, first specimen). The merged board
is a pure function of its seven sources, so it CANNOT drift from them: `--check`
answers "has anyone hand-edited the board?" as a byte comparison, not a judgement.
The output carries no timestamp for exactly this reason -- a nightly run that changes
nothing produces no diff, and every diff that appears is a real board change.

FAIL-CLOSED. A missing, unreadable or malformed source REFUSES with a non-zero exit
and writes NOTHING. The dangerous output here is not a crash, it is a board with one
team's section quietly absent: a supervisor reading it sees "nothing to report" where
the truth is "the merger could not read that team's file". Every clause of the
validator in `lab_state_sources.validate()` answers one way that could happen.

  exit 0  wrote the board (or --check found no drift, or --selftest passed)
  exit 2  REFUSED: a source is missing/unreadable/malformed, or the board manifest
          disagrees with harness/teams.yaml. Nothing written.
  exit 3  REFUSED: the target is not a generated board and --adopt was not given.
          (This is the CUTOVER interlock -- see --adopt.)
  exit 4  --check found drift: the board on disk differs from its sources.
  exit 5  REFUSED: the LIVE PLANTED CONTROL failed. Nothing written.
  exit 6  REFUSED-AFTER-WRITE: the board read back from disk is not the board that
          was built. The target is left in place and must be treated as suspect.

CUTOVER INTERLOCK. Until the board is adopted, docs/LAB_STATE.md is a hand-maintained
file that six supervisors are actively splicing, and overwriting it would destroy
work. So this tool REFUSES to overwrite any target that does not already carry the
generated-file marker, unless invoked with --adopt. Cutover is therefore one explicit
deliberate act by a human hand, and no cron entry, no stray invocation and no agent
can perform it by accident.

PLANTED CONTROL -- LIVE, ON EVERY RUN, NOT ONLY IN --selftest.
CLAUDE.md rule 3 requires a comparator to plant a known perturbation, READ IT BACK
FROM DISK, and refuse if the reader cannot see it. Until 2026-08-31 this tool's
control lived only in `--selftest` and in a one-off birth demonstration, so a
nightly run at 03:17 carried no control at all: it read seven files, wrote a board,
and trusted both. `planted_control()` below now runs on every production invocation.

It has SEVEN POSITIVE LIMBS, one per source, because the hazard this tool exists to
refuse is team-shaped: a sentinel planted in `dafoam.md` proves that `dafoam.md` was
actually read and actually reached the board, and proving it for `cfd.md` proves
nothing about `dafoam.md`. It has a NEGATIVE LIMB -- a detector that fires on
everything is not a detector (VERIFICATION_CHARTER §2j.3): the unplanted rebuild must
be byte-identical to the board being published, so the plant was the only delta.

It plants into a SCRATCH COPY of the sources, never the real ones. A control that
mutates the live board sources would, if killed between plant and restore, leave a
sentinel line inside a supervisor's board section -- trading a missing control for a
corrupted record. The bytes are real, the code path is the real one, and the
producer is `atomic_write` + a real re-read; only the directory is scratch.

`--selftest` additionally drives every refusal path, and SAYS SO: those bytes are
written by the harness, which per §2j.2 is NOT the birth demonstration. The birth
demonstration plants into the REAL source file at its real path with the same tool a
supervisor edits it with, and is recorded at
`verification/credibility/lab_state_merger_birth_demonstration_2026-08-31.txt`.
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_state_sources as M  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def atomic_write(path, data):
    d = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".merge_lab_state.")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --------------------------------------------------- LIVE PLANTED CONTROL ---

# A string that cannot occur in board prose by accident and is greppable if it ever
# escapes into a real file. It never touches a real source: see the module docstring.
SENTINEL = "PLANTED-SENTINEL-MERGE-CONTROL-3f9c1e77"


def planted_control(src_dir=None, repo=None, expect=None, verbose=False):
    """Run the control. Returns (ok, [report lines]). Writes nothing outside a tmpdir.

    POSITIVE LIMBS (seven): plant the sentinel into a scratch copy of source i, run
    the REAL build and the REAL atomic_write, RE-READ THE RESULT FROM DISK, and
    require exactly one occurrence. Fails if any single source's bytes do not reach
    the board -- which is exactly the "a team is silently missing" outcome.

    NEGATIVE LIMB: with nothing planted, the same path must produce a board carrying
    zero occurrences AND byte-identical to `expect` (the board about to be published).
    Without this, the control would pass on a reader that simply echoes everything.

    WHAT THESE LIMBS DO NOT PROVE -- written down rather than fixed, because the
    coverage already exists elsewhere and the 14-day rule freeze forbids adding a
    check for it (verification-supervisor, 2026-08-31).

        The plant is an APPEND (`open(p, "ab")`). So a limb proves that source i's
        bytes REACH the board. IT DOES NOT PROVE THEY REACH IT IN FULL. A `build()`
        that systematically dropped bytes from the MIDDLE of every source would drop
        them from `base` and from `planted` alike -- `only_delta` would still hold,
        the sentinel would still be seen exactly once, and all seven limbs would
        pass on a board missing content from every team.

        THAT FAILURE IS CAUGHT, JUST NOT HERE. Two other limbs carry it:
          * `--check` (rc 4) compares the built board against the board on disk
            byte-for-byte, so silent mid-file loss appears as drift; and
          * `split_lab_state.py` asserts `concat(sources) == board` exactly, in
            memory and again re-read from disk, at migration and at every re-split.

        The distinction matters because THIS control is what an unattended 03:17
        cron run relies on when nothing else is looking, and `--check` is not run
        on that path. A reader of a nightly `rc=0` should know the guarantee is
        "every team's bytes reached the board", not "every team's bytes reached the
        board intact".

        This is the same shape as a control that fires on one property while the
        verdict rests on a slightly different one. Named, not repaired.
    """
    repo = repo or M.REPO
    lines = []
    real_dir = src_dir or os.path.join(repo, M.SRC_DIR_REL)
    tmp = tempfile.mkdtemp(prefix="merge_lab_state_control.")
    try:
        pristine = {}
        for stem, _o, _h in M.order():
            p = os.path.join(real_dir, stem + ".md")
            if not os.path.isfile(p):
                return False, [f"control cannot run: {p} missing"]
            b = open(p, "rb").read()
            pristine[stem] = b
            open(os.path.join(tmp, stem + ".md"), "wb").write(b)

        # ---- negative limb first, so a pre-firing reader is caught before any plant
        board = os.path.join(tmp, "board.md")
        base, _ = M.build(repo=repo, src_dir=tmp)
        atomic_write(board, base)
        back = open(board, "rb").read()
        if back != base:
            return False, ["NEGATIVE LIMB: the board read back from disk is not the "
                           "board that was built"]
        if SENTINEL in back.decode("utf-8", "replace"):
            return False, ["NEGATIVE LIMB FAILED: the unplanted board already "
                           "contains the sentinel; the reader is pre-firing"]
        if expect is not None and back != expect:
            return False, [f"NEGATIVE LIMB FAILED: the control's unplanted rebuild "
                           f"({len(back)} bytes, sha {sha(back)[:16]}) is not the "
                           f"board about to be published ({len(expect)} bytes, sha "
                           f"{sha(expect)[:16]})"]
        lines.append(f"negative limb: 0 sentinels in {len(back)} bytes, "
                     f"rebuild == the board being published")

        # ---- seven positive limbs, one per source
        for stem, _o, _h in M.order():
            p = os.path.join(tmp, stem + ".md")
            with open(p, "ab") as f:
                f.write((SENTINEL + "\n").encode("utf-8"))
            planted, _ = M.build(repo=repo, src_dir=tmp)
            atomic_write(board, planted)
            got = open(board, "rb").read().decode("utf-8", "replace")
            n = got.count(SENTINEL)
            only_delta = planted.replace((SENTINEL + "\n").encode("utf-8"), b"") == base
            open(p, "wb").write(pristine[stem])          # restore the scratch copy
            if n != 1 or not only_delta:
                return False, lines + [
                    f"POSITIVE LIMB FAILED for {stem}.md: the sentinel planted in "
                    f"that source produced {n} occurrence(s) in the board read back "
                    f"from disk (expected 1), only-delta={only_delta}. The merger "
                    f"cannot be shown to carry that team's bytes into the board, so "
                    f"a board it publishes cannot be trusted to contain them."]
            lines.append(f"positive limb {stem+'.md':<24} sentinel seen 1x in the "
                         f"board re-read from disk; it was the only delta")

        # ---- restore-check: the scratch tree is back to pristine, so the seven
        # limbs did not accumulate. If this fails the limbs above were not independent.
        final, _ = M.build(repo=repo, src_dir=tmp)
        if final != base:
            return False, lines + ["RESTORE CHECK FAILED: the scratch sources did "
                                   "not return to their pre-plant state"]
        lines.append("restore check: scratch sources byte-identical to pre-plant")
        return True, lines
    except M.Malformed as e:
        return False, lines + [f"control raised Malformed: {e}"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- selftest ---

CHIEF_BODY = (M.TITLE_LINE + "\n\npreamble line.\n\n---\n\n"
              + M.CHIEF_HEADING + "\n\n**Section last written:** 2026-08-31T00:00Z\n\n"
              "chief body.\n")


def _good_tree(d):
    """A minimal but STRUCTURALLY REAL source tree: same manifest, same headings,
    same order as production. Written by the harness -- which is why this is a
    selftest and not the §2j birth demonstration."""
    os.makedirs(d, exist_ok=True)
    for stem, _o, head in M.order():
        if stem == M.CHIEF[0]:
            body = CHIEF_BODY
        else:
            body = (head + "\n\n**Section last written:** 2026-08-31T00:00Z\n\n"
                    f"{stem} body line.\n")
        open(os.path.join(d, stem + ".md"), "w", encoding="utf-8").write(body)


def selftest():
    cases = []

    def case(name, fn):
        try:
            ok, note = fn()
        except Exception as e:  # a selftest case must never crash silently
            ok, note = False, f"raised {e!r}"
        cases.append((ok, name, note))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}   {note}")

    root = tempfile.mkdtemp(prefix="merge_lab_state_selftest.")
    try:
        src = os.path.join(root, "src")
        _good_tree(src)

        base, warns = M.build(src_dir=src)
        case("A1 seven sources merge",
             lambda: (len(warns) == 0 and base.startswith(M.HEADER.encode()),
                      f"{len(base)} bytes, {len(warns)} warnings"))
        case("A2 output carries the GENERATED marker",
             lambda: (M.MARKER in base.decode(), "marker present"))
        case("A3 every team heading appears exactly once",
             lambda: (all(base.decode().count("\n" + h) == 1
                          for _, _, h in M.order()[1:]), "6 team headings, once each"))
        case("A4 output is deterministic (no timestamp)",
             lambda: (M.build(src_dir=src)[0] == base, "two builds byte-identical"))
        case("A5 sources concatenate to output minus header",
             lambda: (b"".join(open(os.path.join(src, s + ".md"), "rb").read()
                               for s, _, _ in M.order())
                      == base[len(M.HEADER.encode()):], "byte-for-byte"))

        # ---- PLANTED CONTROL, both limbs, on a real source file --------------
        vpath = os.path.join(src, "verification.md")
        pre = open(vpath, "rb").read()
        SENT = "PLANTED-SENTINEL-9c1f2a7e"

        case("B0 negative limb BEFORE the plant: sentinel absent from output",
             lambda: (SENT not in base.decode(), "reader is not pre-firing"))

        open(vpath, "a", encoding="utf-8").write(SENT + "\n")
        planted, _ = M.build(src_dir=src)
        case("B1 POSITIVE LIMB: planted sentinel reaches the merged board",
             lambda: (planted.decode().count(SENT) == 1,
                      f"{planted.decode().count(SENT)} occurrence"))
        case("B2 the plant is the ONLY delta",
             lambda: (planted.replace((SENT + "\n").encode(), b"") == base,
                      "removing the sentinel restores the earlier output exactly"))

        open(vpath, "wb").write(pre)
        unplanted, _ = M.build(src_dir=src)
        case("B3 NEGATIVE LIMB: sentinel removed, output no longer carries it",
             lambda: (SENT not in unplanted.decode(), "0 occurrences"))
        case("B4 unplanted output == pre-plant output",
             lambda: (unplanted == base, f"sha {sha(unplanted)[:16]}"))

        # ---- FAIL-CLOSED refusals -------------------------------------------
        def refuses(mutate, why):
            d = os.path.join(root, "m")
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(src, d)
            mutate(d)
            try:
                M.build(src_dir=d)
                return False, "BUILT A BOARD -- did not refuse"
            except M.Malformed as e:
                # The refusal must be the RIGHT refusal. `or True` here would make
                # every case in this block pass on any error at all -- a fail-open
                # inside the fail-closed test.
                return (why.lower() in str(e).lower(),
                        str(e).split(":", 1)[-1].strip()[:70])

        case("C1 missing source refuses",
             lambda: refuses(lambda d: os.remove(os.path.join(d, "cfd.md")), "missing"))
        case("C2 unreadable source refuses",
             lambda: refuses(lambda d: os.chmod(os.path.join(d, "dafoam.md"), 0),
                             "unreadable"))
        case("C3 empty source refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "closure.md"), "wb").close(),
                             "empty"))
        case("C4 heading-only source refuses (truncation)",
             lambda: refuses(lambda d: open(os.path.join(d, "closure.md"), "w",
                                            encoding="utf-8").write("## closure\n"),
                             "heading only"))
        case("C5 wrong heading refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "cfd.md"), "w",
                                            encoding="utf-8").write("## dafoam\nx\n"),
                             "expected"))
        case("C6 second '## ' heading refuses (namespace splice)",
             lambda: refuses(lambda d: open(os.path.join(d, "cfd.md"), "w",
                                            encoding="utf-8").write(
                                 "## cfd\nx\n## verification\nhijack\n"), "headings"))
        case("C7 no trailing newline refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "cfd.md"), "w",
                                            encoding="utf-8").write("## cfd\nx"),
                             "newline"))
        case("C8 non-UTF-8 source refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "cfd.md"), "wb").write(
                 b"## cfd\n\xff\xfe body\n"), "UTF-8"))
        case("C9 NUL byte refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "cfd.md"), "wb").write(
                 b"## cfd\nbody\x00\n"), "NUL"))
        case("C10 a source that is a COPY OF THE MERGED BOARD refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "cfd.md"), "wb").write(base),
                             "marker"))
        case("C11 chief source with the wrong title refuses",
             lambda: refuses(lambda d: open(os.path.join(d, "chief.md"), "w",
                                            encoding="utf-8").write(
                                 "# Something Else\n\n" + M.CHIEF_HEADING + "\nx\n"),
                             "title"))

        # a refusal must WRITE NOTHING -- the clause that matters most
        def refusal_writes_nothing():
            d = os.path.join(root, "n")
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(src, d)
            os.remove(os.path.join(d, "verification.md"))
            out = os.path.join(root, "board_never.md")
            rc = run_merge(src_dir=d, out=out, adopt=True)
            return (rc == 2 and not os.path.exists(out),
                    f"rc={rc}, output exists={os.path.exists(out)}")
        case("C12 a refusal writes NO output file at all", refusal_writes_nothing)

        def partial_board_impossible():
            d = os.path.join(root, "p")
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(src, d)
            os.remove(os.path.join(d, "heat-transfer.md"))
            try:
                b, _ = M.build(src_dir=d)
            except M.Malformed:
                return True, "refused rather than emit a 6-team board"
            return False, f"emitted a board of {len(b)} bytes with a team missing"
        case("C13 a board with a team missing is never emitted",
             partial_board_impossible)

        # ---- write path, --check, and the cutover interlock -------------------
        out = os.path.join(root, "board.md")
        case("D1 --adopt writes a board where none exists",
             lambda: (run_merge(src_dir=src, out=out, adopt=True) == 0
                      and open(out, "rb").read() == base, f"{os.path.getsize(out)} bytes"))
        case("D2 --check on an in-sync board is rc 0",
             lambda: (run_merge(src_dir=src, out=out, check=True) == 0, "no drift"))

        with open(out, "a", encoding="utf-8") as f:
            f.write("a hand edit\n")
        case("D3 --check DETECTS a hand edit (rc 4)",
             lambda: (run_merge(src_dir=src, out=out, check=True) == 4, "drift seen"))
        case("D4 the merge overwrites a hand edit without --adopt "
             "(target already generated)",
             lambda: (run_merge(src_dir=src, out=out) == 0
                      and open(out, "rb").read() == base, "restored"))

        hand = os.path.join(root, "hand_board.md")
        open(hand, "w", encoding="utf-8").write("# LAB_STATE\n\n## cfd\nlive work\n")
        case("E1 CUTOVER INTERLOCK: refuses to overwrite a NON-generated board (rc 3)",
             lambda: (run_merge(src_dir=src, out=hand) == 3
                      and "live work" in open(hand, encoding="utf-8").read(),
                      "target untouched"))
        case("E2 --adopt is required and sufficient for the first overwrite",
             lambda: (run_merge(src_dir=src, out=hand, adopt=True) == 0
                      and open(hand, "rb").read() == base, "adopted"))

        ok, msg = M.assert_matches_roster()
        case("F1 manifest matches harness/teams.yaml", lambda: (ok, msg))

        # ---- THE ROSTER GATE IS LIVE IN PRODUCTION, not only here ------------
        def roster_gate_is_live():
            """The gate that measured its condition and did not act on it
            (FAIL_OPEN_GATE_AUDIT §11) is the defect being closed. Point the
            manifest at a roster it disagrees with and require build() to REFUSE."""
            saved = M.TEAMS[:]
            try:
                M.TEAMS.append(("ghost-team", "nobody"))
                try:
                    M.build(src_dir=src)
                    return False, "BUILT A BOARD with the manifest != the roster"
                except M.Malformed as e:
                    return "ROSTER MISMATCH" in str(e), str(e).split(".")[0][:70]
            finally:
                M.TEAMS[:] = saved
        case("F2 build() REFUSES when the manifest disagrees with teams.yaml",
             roster_gate_is_live)

        def roster_zero_refuses():
            """A roster reader that returns nothing must refuse, not agree.
            This is the planted zero applied to the roster itself."""
            try:
                M.roster_teams(repo=root)      # a directory with no harness/
                return False, "returned a roster from a repo that has none"
            except M.Malformed as e:
                return "not found" in str(e), str(e).split(":")[0][:60]
        case("F3 a roster it cannot read REFUSES rather than reading as agreement",
             roster_zero_refuses)

        # ---- THE LIVE PLANTED CONTROL, and its own mutation demonstration ----
        case("G1 live planted control passes on a good source tree",
             lambda: (lambda r: (r[0], f"{len(r[1])} limbs reported"))(
                 planted_control(src_dir=src)))

        def control_catches_a_dropped_team():
            """MUTATE THE READER. A build that silently skips one source is exactly
            the failure the control exists to catch. If the control still passes
            against it, the control is decoration."""
            real = M.build

            def blind(repo=M.REPO, src_dir=None, check_roster=True):
                data, w = real(repo=repo, src_dir=src_dir, check_roster=check_roster)
                drop = open(os.path.join(src_dir, "dafoam.md"), "rb").read()
                return data.replace(drop, b""), w      # dafoam silently vanishes
            M.build = blind
            try:
                ok2, rep = planted_control(src_dir=src)
                return (not ok2 and any("dafoam" in ln for ln in rep),
                        rep[-1][:70] if rep else "no report")
            finally:
                M.build = real
        case("G2 MUTATED READER: a build that drops one team FAILS the control",
             control_catches_a_dropped_team)

        def control_catches_pre_firing():
            """A reader that emits the sentinel unprompted must fail the NEGATIVE
            limb. A detector that fires on everything is not a detector (§2j.3)."""
            real = M.build

            def noisy(repo=M.REPO, src_dir=None, check_roster=True):
                data, w = real(repo=repo, src_dir=src_dir, check_roster=check_roster)
                return data + (SENTINEL + "\n").encode(), w
            M.build = noisy
            try:
                ok2, rep = planted_control(src_dir=src)
                return (not ok2 and any("pre-firing" in ln or "NEGATIVE" in ln
                                        for ln in rep),
                        rep[-1][:70] if rep else "no report")
            finally:
                M.build = real
        case("G3 MUTATED READER: a pre-firing build FAILS the negative limb",
             control_catches_pre_firing)

        def control_gates_the_write():
            """The control must STOP the publication, not merely report. rc 5, and
            no file written."""
            real = M.build

            def blind(repo=M.REPO, src_dir=None, check_roster=True):
                data, w = real(repo=repo, src_dir=src_dir, check_roster=check_roster)
                drop = open(os.path.join(src_dir, "cfd.md"), "rb").read()
                return data.replace(drop, b""), w
            M.build = blind
            target = os.path.join(root, "board_control_gate.md")
            try:
                rc = run_merge(src_dir=src, out=target, adopt=True)
                return (rc == 5 and not os.path.exists(target),
                        f"rc={rc}, output exists={os.path.exists(target)}")
            finally:
                M.build = real
        case("G4 a FAILED control refuses the write entirely (rc 5, nothing written)",
             control_gates_the_write)

        # ---- POST-WRITE READ-BACK -------------------------------------------
        def readback_catches_a_bad_write():
            """MUTATE THE WRITER. A write that lands different bytes than it was
            given must be caught by re-reading from disk, not trusted."""
            real_w = globals()["atomic_write"]

            def truncating(path, data):
                real_w(path, data[:len(data) // 2])
            globals()["atomic_write"] = truncating
            target = os.path.join(root, "board_truncated.md")
            try:
                rc = run_merge(src_dir=src, out=target, adopt=True, control=False)
                return (rc == 6, f"rc={rc}, on disk {os.path.getsize(target)} bytes "
                                 f"vs {len(base)} built")
            finally:
                globals()["atomic_write"] = real_w
        case("G5 MUTATED WRITER: a truncated write is caught by the read-back (rc 6)",
             readback_catches_a_bad_write)

        def good_write_reads_back():
            target = os.path.join(root, "board_readback_ok.md")
            rc = run_merge(src_dir=src, out=target, adopt=True)
            return (rc == 0 and open(target, "rb").read() == base,
                    f"rc={rc}, read-back identical")
        case("G6 a good write reads back identical (rc 0)", good_write_reads_back)

    finally:
        for r, _d, fs in os.walk(root):
            for f in fs:
                try:
                    os.chmod(os.path.join(r, f), 0o600)
                except OSError:
                    pass
        shutil.rmtree(root, ignore_errors=True)

    npass = sum(1 for ok, _, _ in cases if ok)
    print(f"\n  {npass}/{len(cases)} cases pass")
    print("  HONEST LABEL (VERIFICATION_CHARTER §2j.2): every byte read above was "
          "written by\n  THIS HARNESS, not by a supervisor. The selftest proves the "
          "merger's LOGIC; it is\n  NOT the birth demonstration. See "
          "verification/credibility/"
          "lab_state_merger_birth_demonstration_2026-08-31.txt")
    return 0 if npass == len(cases) else 1


# ------------------------------------------------------------------- merge ---

def run_merge(src_dir=None, out=None, check=False, adopt=False, quiet=True,
              control=True):
    """The whole production path. Returns the process exit code."""
    out = out or os.path.join(M.REPO, M.BOARD_REL)
    try:
        data, warns = M.build(src_dir=src_dir)
    except M.Malformed as e:
        print(f"REFUSED (rc 2): {e}", file=sys.stderr)
        print("nothing written; the board on disk is untouched", file=sys.stderr)
        return 2
    for w in warns:
        print(f"warning: {w}", file=sys.stderr)

    # THE CONTROL RUNS BEFORE ANY DECISION IS TAKEN ON `data` -- before --check
    # grades it and before it is written. A control run after the write would be a
    # report about a board that is already published.
    if control:
        ok, report = planted_control(src_dir=src_dir, expect=data)
        if not quiet:
            for ln in report:
                print(f"  control: {ln}")
        if not ok:
            print("REFUSED (rc 5): THE LIVE PLANTED CONTROL FAILED. This tool cannot "
                  "demonstrate that it can see a team's bytes reach the board, so "
                  "the board it would publish is not evidence of anything "
                  "(CLAUDE.md rule 3). Nothing written.", file=sys.stderr)
            for ln in report:
                print(f"    {ln}", file=sys.stderr)
            return 5

    if check:
        if not os.path.exists(out):
            print(f"DRIFT (rc 4): {out} does not exist", file=sys.stderr)
            return 4
        cur = open(out, "rb").read()
        if cur == data:
            if not quiet:
                print(f"in sync: {out} == its sources ({len(data)} bytes)")
            return 0
        print(f"DRIFT (rc 4): {out} differs from its sources "
              f"(on disk {len(cur)} bytes sha {sha(cur)[:16]}, "
              f"from sources {len(data)} bytes sha {sha(data)[:16]})", file=sys.stderr)
        return 4

    if os.path.exists(out):
        cur = open(out, "rb").read()
        if M.MARKER.encode() not in cur and not adopt:
            print(f"REFUSED (rc 3): {out} does not carry the generated-board marker, "
                  f"so it is still a HAND-MAINTAINED board that agents are writing. "
                  f"Overwriting it would destroy their work. This is the CUTOVER "
                  f"INTERLOCK: pass --adopt, deliberately, once, by a human hand.",
                  file=sys.stderr)
            return 3
        if cur == data:
            if not quiet:
                print(f"unchanged: {out} ({len(data)} bytes)")
            return 0

    atomic_write(out, data)

    # READ IT BACK FROM DISK. `atomic_write` returning without raising is not proof
    # that the bytes are on the disk: a full filesystem, a truncated rename, a
    # checkout racing the write, or a filter this tool does not know about all leave
    # a plausible-looking file behind. Rule 3's second clause is "reads it back from
    # disk", and until 2026-08-31 this path did not.
    verify = open(out, "rb").read()
    if verify != data:
        print(f"REFUSED-AFTER-WRITE (rc 6): {out} was written but reads back "
              f"DIFFERENT: on disk {len(verify)} bytes sha {sha(verify)[:16]}, "
              f"built {len(data)} bytes sha {sha(data)[:16]}. The target is left as "
              f"it is and must be treated as suspect -- do not read this board as "
              f"the lab's state until it is regenerated successfully.",
              file=sys.stderr)
        return 6

    if not quiet:
        print(f"wrote {out}: {len(data)} bytes, sha256 {sha(data)}, "
              f"{len(M.order())} sources; read back from disk and verified identical")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None,
                    help="target board (default docs/LAB_STATE.md)")
    ap.add_argument("--src-dir", default=None,
                    help="source directory (default docs/lab_state)")
    ap.add_argument("--check", action="store_true",
                    help="compare only; rc 4 if the board has drifted from its sources")
    ap.add_argument("--adopt", action="store_true",
                    help="permit the FIRST overwrite of a board that is not yet "
                         "generated. This is the cutover. One deliberate act.")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        print("merge_lab_state.py --selftest")
        return selftest()
    return run_merge(src_dir=a.src_dir, out=a.out, check=a.check, adopt=a.adopt,
                     quiet=False)


if __name__ == "__main__":
    sys.exit(main())
