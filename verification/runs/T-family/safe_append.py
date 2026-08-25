#!/usr/bin/env python3
"""safe_append -- guards for appending to a SHARED file under the private-index
protocol.  Heat-transfer team tool; offered to the lab, not imposed on it.

WHY THIS EXISTS.  Three guards that everyone writes by hand, that everyone
writes slightly wrong, and that this team got wrong once tonight:

  1. PREFIX.  The append must not disturb a byte above it.  Written with
     str.split("\n") this produces a FALSE ALARM on every clean append, because
     split leaves a trailing "" element that the comparison then misaligns.
     That fired on this team's C-53 append: the assertion said PREFIX CHANGED
     on a file that was byte-perfect.  Compare BYTES.

  2. ANCHOR.  "Append at the foot" lands inside the file's LAST BLOCK -- which
     is the block you intend ONLY FOR AS LONG AS NOBODY ELSE APPENDS FIRST.  If
     a peer lands a new lesson between your read and your write, your addendum
     goes INSIDE THEIR BLOCK, silently, with every other assertion passing.
     A foot append to a shared file is a bet on nobody else appending, and that
     bet needs a guard.  (ansys-verification, via the chief, 2026-08-25.)

  3. TRAILING NEWLINE.  A base without one MERGES your first line into its last
     line while the prefix assertion still passes.

THE SYMMETRY REQUIREMENT -- the point of the whole file.  A guard must be shown
to ABORT on a known-BAD input AND shown NOT to abort on a known-GOOD one.  A
guard with only the positive arm is untested in the direction that matters most
in practice: it may be firing on everything, and a guard that always fires is
indistinguishable from a guard that works until you feed it something good.
This is standing rule 3's structure -- the planted-zero control passes only
because it proves the reader is neither BLIND nor NOISY -- pointed at a checking
tool instead of at a field reader.

Every guard below therefore ships with BOTH arms in --selftest.

v1.1 -- AND THE CHECKER ITSELF OWES THE SAME.  v1.0 computed that verdict in
AGGREGATE and so passed a suite in which one guard had only a bad-input arm,
while still printing "every guard".  A check reporting on the AGGREGATE rather
than on each ITEM -- L-314's shape, inside the tool built to cure it.  Fixed by
grouping per guard family; and symmetry_verdict is now itself exercised in both
directions by _meta_selftest, because a guard that is not tested is a guard.
"""
import re
import sys

EXIT_OK, EXIT_REFUSE = 0, 2


class GuardFailure(Exception):
    pass


def check_prefix(base: bytes, result: bytes) -> None:
    """RESULT must begin with BASE, byte for byte.  Bytes, never split()."""
    if not isinstance(base, bytes) or not isinstance(result, bytes):
        raise GuardFailure("check_prefix takes bytes; text would reintroduce "
                           "the split artifact this guard exists to kill")
    if not result.startswith(base):
        n = min(len(base), len(result))
        i = next((k for k in range(n) if base[k] != result[k]), n)
        raise GuardFailure(
            f"PREFIX CHANGED at byte {i}: the append disturbed content above it")


def check_trailing_newline(base: bytes) -> None:
    if base and not base.endswith(b"\n"):
        raise GuardFailure(
            "BASE HAS NO TRAILING NEWLINE: an append would MERGE its first line "
            "into the base's last line while the prefix assertion still passes")


def check_anchor_is_last(base: bytes, block_re: str, anchor: str) -> None:
    """ANCHOR must be the LAST block-opening match in BASE.

    block_re matches a block opener (e.g. r'^## L-\\d+' for LESSONS.md).
    anchor is the exact opener text the caller believes it is appending after.
    """
    pat = re.compile(block_re, re.M)
    found = pat.findall(base.decode("utf-8", "replace"))
    if not found:
        raise GuardFailure(f"NO BLOCK MATCHED {block_re!r}: the anchor cannot be "
                           "confirmed, so the append is unguarded")
    if found[-1] != anchor:
        raise GuardFailure(
            f"ANCHOR IS NOT LAST: you intend to append after {anchor!r} but the "
            f"file now ends with block {found[-1]!r}. A PEER APPENDED BETWEEN "
            "YOUR READ AND YOUR WRITE. Re-read the blob and rebuild.")


def symmetry_verdict(results):
    """THE VERDICT, AS A PURE FUNCTION SO IT CAN ITSELF BE TESTED.

    v1.0 of this file computed the verdict IN AGGREGATE:

        pos = sum(1 for r in results if r[2] == "BAD-input")
        neg = len(results) - pos
        if neg == 0: REFUSE

    which refuses only when the WHOLE SUITE has no good-input arm anywhere.  Add
    a fourth guard carrying only a bad-input arm and it PASSED -- while still
    printing "every guard fires on bad input and stays quiet on good", a claim it
    had never checked.  Found by the ansys-verification team, who planted exactly
    that results set and ran the tail logic verbatim rather than inferring the
    bug from reading.

    That is L-314's own shape -- A CHECK REPORTING ON THE AGGREGATE RATHER THAN
    ON EACH ITEM -- sitting inside the tool built to cure it, written by the hand
    that had just diagnosed four instances of it.  The lesson is not that
    aggregate checks are careless; it is that this class of defect survives
    active hunting, so the remedy has to be structural: GROUP BY ITEM, REQUIRE
    BOTH ARMS PER ITEM, and never print a per-item claim from a whole-suite sum.

    Guards are grouped by FAMILY -- the name before any "/" -- because
    "anchor/peer-raced-us" is a further arm of "anchor", not a separate guard.
    """
    from collections import defaultdict
    arms = defaultdict(set)
    failed = []
    for ok, name, kind, note in results:
        arms[name.split("/")[0]].add(kind)
        if not ok:
            failed.append((name, kind, note))

    lines, refuse = [], False
    if not results:
        return False, ["  REFUSED: empty suite -- a guard suite that checks "
                       "nothing cannot report symmetry"]

    missing_good = sorted(f for f, k in arms.items() if "GOOD-input" not in k)
    missing_bad = sorted(f for f, k in arms.items() if "BAD-input" not in k)

    for fam in sorted(arms):
        kinds = arms[fam]
        mark = "OK  " if {"GOOD-input", "BAD-input"} <= kinds else "GAP "
        lines.append(f"  {mark}{fam:<24} arms: {', '.join(sorted(kinds))}")

    if missing_good:
        refuse = True
        lines.append(f"  REFUSED: {len(missing_good)} guard(s) have NO GOOD-INPUT "
                     f"arm -- {', '.join(missing_good)}. A guard shown only to "
                     "fire is untested in the direction that matters: it may be "
                     "firing on everything.")
    if missing_bad:
        refuse = True
        lines.append(f"  REFUSED: {len(missing_bad)} guard(s) have NO BAD-INPUT "
                     f"arm -- {', '.join(missing_bad)}. A guard never shown to "
                     "fire has not been shown to work at all.")
    if failed:
        refuse = True
        for name, kind, note in failed:
            lines.append(f"  REFUSED: {name} failed its {kind} arm -- {note}")

    if not refuse:
        lines.append(f"  SYMMETRY HELD across {len(arms)} guard(s), CHECKED "
                     "PER GUARD: each fires on bad input and stays quiet on good")
    return (not refuse), lines


def _meta_selftest():
    """THE SYMMETRY REQUIREMENT, APPLIED TO THE SYMMETRY CHECKER ITSELF.

    symmetry_verdict is a guard, so it owes what every guard owes: proof that it
    REFUSES a known-bad suite AND proof that it stays QUIET on a known-good one.
    v1.0 had neither, which is why its defect survived.
    """
    G, B = "GOOD-input", "BAD-input"
    cases = [
        ("good suite stays quiet", True, [
            (True, "prefix", G, ""), (True, "prefix", B, ""),
            (True, "anchor", G, ""), (True, "anchor", B, "")]),
        ("sub-named arms roll up to family", True, [
            (True, "anchor", G, ""), (True, "anchor/peer-raced-us", B, "")]),
        # THE v1.0 DEFECT, planted exactly as ansys-verification planted it
        ("v1.0 REGRESSION: guard with only a bad arm", False, [
            (True, "prefix", G, ""), (True, "prefix", B, ""),
            (True, "newline", G, ""), (True, "newline", B, ""),
            (True, "NEWGUARD", B, "")]),
        ("guard with only a good arm", False, [
            (True, "prefix", G, ""), (True, "prefix", B, ""),
            (True, "NEWGUARD", G, "")]),
        ("a failing arm refuses", False, [
            (True, "prefix", G, ""), (False, "prefix", B, "did not fire")]),
        ("empty suite refuses", False, []),
    ]
    ok_all = True
    for name, want_pass, res in cases:
        got, _ = symmetry_verdict(res)
        good = (got == want_pass)
        ok_all &= good
        print(f"  {'PASS' if good else 'FAIL'}  meta: {name:<44} "
              f"expected {'pass' if want_pass else 'REFUSE'}, got "
              f"{'pass' if got else 'REFUSE'}")
    pos = sum(1 for _, w, _ in cases if not w)
    neg = len(cases) - pos
    print(f"\n  meta: {len(cases)} cases -- {pos} must REFUSE, {neg} must PASS")
    if pos == 0 or neg == 0:
        print("  REFUSED: the meta-suite itself lacks an arm")
        return False
    return ok_all


def _selftest():
    """BOTH ARMS on every guard.  A guard is not tested until it has been shown
    to stay QUIET on a known-good input as well as to fire on a known-bad one."""
    results = []

    def arm(name, fn, must_raise):
        try:
            fn()
        except GuardFailure as e:
            ok = must_raise
            note = f"fired: {str(e)[:60]}"
        except Exception as e:  # noqa: BLE001
            ok, note = False, f"WRONG EXCEPTION {type(e).__name__}: {e}"
        else:
            ok = not must_raise
            note = "stayed quiet"
        results.append((ok, name, "BAD-input" if must_raise else "GOOD-input", note))

    base = b"line one\nline two\n"

    # 1. PREFIX -- positive and NEGATIVE arm
    arm("prefix", lambda: check_prefix(base, base + b"appended\n"), False)
    arm("prefix", lambda: check_prefix(base, b"line ONE\nline two\nappended\n"), True)
    arm("prefix", lambda: check_prefix(base, b"line one\n"), True)
    # the exact shape that produced this team's C-53 FALSE ALARM
    arm("prefix/C-53-regression",
        lambda: check_prefix(base, base + b"| C-53 | a row |\n"), False)

    # 2. TRAILING NEWLINE -- both arms
    arm("newline", lambda: check_trailing_newline(base), False)
    arm("newline", lambda: check_trailing_newline(b"no newline here"), True)

    # 3. ANCHOR -- both arms
    two = b"## L-1\nbody\n\n## L-2\nbody\n"
    arm("anchor", lambda: check_anchor_is_last(two, r"^## L-\d+", "## L-2"), False)
    arm("anchor", lambda: check_anchor_is_last(two, r"^## L-\d+", "## L-1"), True)
    # the exact race the guard exists for: a peer landed L-3 after our read
    three = two + b"\n## L-3\npeer's block\n"
    arm("anchor/peer-raced-us",
        lambda: check_anchor_is_last(three, r"^## L-\d+", "## L-2"), True)
    arm("anchor/no-match",
        lambda: check_anchor_is_last(two, r"^## Q-\d+", "## Q-1"), True)

    width = max(len(n) for _, n, _, _ in results)
    for ok, name, kind, note in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {kind:<10} {note}")
    print()
    passed, lines = symmetry_verdict(results)
    for l in lines:
        print(l)
    print()
    meta_ok = _meta_selftest()
    if not passed or not meta_ok:
        print("\n  OVERALL: REFUSED")
        return EXIT_REFUSE
    print("\n  OVERALL: PASS -- guards symmetric, and the symmetry checker is "
          "itself checked in both directions")
    return EXIT_OK


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    print("usage: safe_append.py --selftest   (import the check_* functions to use)")
    sys.exit(EXIT_OK)
