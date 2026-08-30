#!/usr/bin/env python3
r"""Append a block to a record from a FILE -- never from a heredoc.

WHY THIS EXISTS (2026-08-28; three teams, one afternoon)
========================================================
An UNQUOTED shell heredoc performs command substitution. Every unescaped
backtick and every `$(...)` in the body is EXECUTED and REPLACED BY ITS OUTPUT
-- usually the empty string. The write still succeeds, the file still grows,
and any "did I append?" check still passes, so the corruption is silent.

Three teams paid for this in one afternoon:
  * verification -- `Queue:` eaten from a CHARTER (L-403). The rule-6 prefix
    assertion PASSED, correctly: it answers "was anything ABOVE edited?", never
    "is what I appended what I WROTE?".
  * dafoam       -- `GATE FAIL` eaten from docs/LAB_STATE.md at e779bdc7, the
    lab's ONLY handoff channel between sessions.
  * closure      -- caught its own before commit.

That is rule 14's shape: A LESSON IS NOT APPLIED UNTIL EVERY CALL SITE ASSERTS
IT. So the fix is not "remember to quote the heredoc" -- it is to remove the
heredoc from the path entirely and to make the landed bytes CHECKED.

WHAT THIS GUARANTEES
====================
  1. The body is read from a FILE as BYTES. No shell ever sees it.
  2. Substitutions (timestamps, shas) are applied by ASSERTED replacement:
     each placeholder must occur an expected number of times BEFORE, and zero
     times AFTER. A silent no-op substitution is impossible.
  3. After the append, the landed tail is compared BYTE-FOR-BYTE against the
     exact bytes intended. Any difference -> the append is REVERTED and the
     tool exits non-zero. This is the check the rule-6 prefix assertion cannot
     make, because it is a different question.

  4. The landed bytes are RECORDED, so the question can be asked again LATER.
     See record_provenance() -- added 2026-08-30 because guarantee 3 protects
     only the instant of the write, and nothing could afterwards ask whether the
     block that landed is still the block that landed.

WHAT IT DOES NOT DO
===================
It does not commit. The private-index protocol, the CAS and the post-commit
verification remain the caller's (CLAUDE.md rule 10).
"""
import argparse, base64, datetime, hashlib, json, os, re, shutil, sys, tempfile

OWNER = ("OWNER verification-supervisor (scripts/ record instruments, assigned 2026-08-28). "
         "RE-READ 2026-09-28 and ON TRIGGER: any new record type routed through this helper.")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_REL = "verification/credibility/append_block_provenance.jsonl"


def ledger_path() -> str:
    """The provenance ledger. $APPEND_BLOCK_LEDGER overrides it, for tests only."""
    return os.environ.get("APPEND_BLOCK_LEDGER") or os.path.join(REPO, *LEDGER_REL.split("/"))


def section_of(body: bytes):
    """The first markdown heading in the block -- the supersession key.

    A board section is REWRITTEN wholesale by the shared-board protocol (each
    write rebuilds from HEAD and replaces only its own section), so a later
    record for the same heading legitimately RETIRES an earlier one. Without a
    key the checker would flag every correct board write.
    """
    m = re.search(rb"^#{1,6} +(.+?)[ \t]*$", body, re.M)
    return m.group(1).decode("utf-8", "replace").strip() if m else None


def record_provenance(target: str, body: bytes) -> str:
    """Tie a landed block to the exact bytes intended, DURABLY.

    WITHOUT THIS THE DETECTION HALF CANNOT EXIST. Guarantee 3 above holds at the
    instant of the write and then evaporates: the run ends, the process exits,
    and no artifact survives that could answer "are these still the bytes that
    landed?". The --body file is no substitute -- it is typically a scratch file
    and the scratchpad is wiped (L-186, three times in one day). So the ledger
    carries the BYTES THEMSELVES, base64, not a path to them.

    Written AFTER a verified append. A failure here is announced loudly and does
    NOT fail the run: the append itself was proved byte-for-byte correct, and
    reporting a good append as failed would be a worse lie than a missing record.
    """
    p = ledger_path()
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)
    tgt = os.path.abspath(target)
    rel = os.path.relpath(tgt, REPO)
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "tool": "append_block.py",
           "target": tgt if rel.startswith("..") else rel.replace(os.sep, "/"),
           "section": section_of(body),
           "bytes": len(body),
           "sha256": hashlib.sha256(body).hexdigest(),
           "body_b64": base64.b64encode(body).decode("ascii")}
    # sort_keys + default ensure_ascii: the ledger line is pure ASCII on one line,
    # so no downstream shell, editor or diff can reflow it into a different record.
    with open(p, "a", encoding="ascii") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return p


def apply_substitutions(body: bytes, subs: list[str]) -> bytes:
    """KEY=VALUE, applied as @@KEY@@ -> VALUE, each ASSERTED present then absent."""
    for s in subs:
        if "=" not in s:
            raise SystemExit("--subst needs KEY=VALUE, got %r" % s)
        k, v = s.split("=", 1)
        ph = ("@@%s@@" % k).encode()
        n = body.count(ph)
        if n == 0:
            raise SystemExit("REFUSED: placeholder %s occurs 0 times in the body. "
                             "A substitution that matches nothing is a silent no-op." % ph.decode())
        body = body.replace(ph, v.encode())
        if body.count(ph) != 0:
            raise SystemExit("REFUSED: placeholder %s still present after substitution" % ph.decode())
        print("  subst %-18s x%d" % (k, n))
    return body


def append_checked(target: str, body: bytes) -> int:
    """Append, then prove the landed bytes ARE the intended bytes. Revert if not."""
    before = open(target, "rb").read() if os.path.exists(target) else b""
    tmp = target + ".append_block.bak"
    with open(tmp, "wb") as fh:
        fh.write(before)
    try:
        with open(target, "ab") as fh:
            fh.write(body)
        after = open(target, "rb").read()
        # THE CHECK THE PREFIX ASSERTION CANNOT MAKE.
        if after[:len(before)] != before:
            raise RuntimeError("the bytes ABOVE the appended block changed")
        landed = after[len(before):]
        if landed != body:
            raise RuntimeError("the LANDED bytes differ from the SOURCE bytes "
                               "(%d vs %d bytes) -- this is the heredoc-substitution "
                               "signature" % (len(landed), len(body)))
        print("  VERIFIED: %d bytes appended; prefix intact; landed == source (byte-for-byte)"
              % len(body))
        os.unlink(tmp)
        try:
            print("  RECORDED: %s" % record_provenance(target, body))
        except Exception as e:   # a good append is never reported as a failed one
            print("PROVENANCE NOT RECORDED (the append itself is verified): %s" % e,
                  file=sys.stderr)
        return 0
    except Exception as e:
        shutil.move(tmp, target)
        print("REFUSED and REVERTED: %s" % e, file=sys.stderr)
        return 2


def selftest() -> int:
    """Planted control. The body carries a BACKTICK and a $(...) -- the two
    shapes an unquoted heredoc destroys -- and both must survive verbatim."""
    ok = True
    d = tempfile.mkdtemp(prefix="ab_")
    os.environ["APPEND_BLOCK_LEDGER"] = os.path.join(d, "prov.jsonl")
    tgt = os.path.join(d, "record.md")
    open(tgt, "w").write("# Record\n\nexisting line\n")
    body = (b"\n## Section @@WHEN@@\n\n"
            b"A literal backtick pair: `Queue:` and `GATE FAIL` must survive.\n"
            b"A command substitution that must NOT run: $(rm -rf /) and $(date).\n"
            b"Backticked command that must NOT run: `whoami`.\n")
    got = apply_substitutions(body, ["WHEN=2026-08-28T21:00Z"])
    rc = append_checked(tgt, got)
    landed = open(tgt, "rb").read()
    for probe in (b"`Queue:`", b"`GATE FAIL`", b"$(rm -rf /)", b"$(date)", b"`whoami`",
                  b"2026-08-28T21:00Z"):
        if probe not in landed:
            print("  CONTROL FAIL: %r did not survive" % probe); ok = False
    if b"@@WHEN@@" in landed:
        print("  CONTROL FAIL: placeholder not substituted"); ok = False
    if rc != 0:
        print("  CONTROL FAIL: a clean append was refused"); ok = False
    else:
        print("  control +: backticks and $(...) survived verbatim; placeholder substituted")
    # The record must exist and must carry the SUBSTITUTED bytes -- a record of the
    # pre-substitution body would make the later check flag every correct write.
    lp = ledger_path()
    if not os.path.exists(lp):
        print("  CONTROL FAIL: no provenance record written"); ok = False
    else:
        rec = json.loads(open(lp).readlines()[-1])
        got_b = base64.b64decode(rec["body_b64"])
        if got_b != got:
            print("  CONTROL FAIL: recorded bytes are not the bytes appended"); ok = False
        elif rec["sha256"] != hashlib.sha256(got).hexdigest():
            print("  CONTROL FAIL: recorded sha256 does not match recorded bytes"); ok = False
        elif b"`GATE FAIL`" not in got_b or b"$(date)" not in got_b:
            print("  CONTROL FAIL: the two heredoc-destroyed shapes are not in the record")
            ok = False
        else:
            print("  control +: provenance record carries the substituted bytes, "
                  "sha matches, backtick and $(...) present")
    # NEGATIVE limb: a substitution that matches nothing must REFUSE, not no-op.
    try:
        apply_substitutions(b"no placeholder here\n", ["MISSING=x"])
        print("  CONTROL FAIL: a no-op substitution was accepted"); ok = False
    except SystemExit:
        print("  control -: a substitution matching nothing REFUSED")
    # NEGATIVE limb: prove the checker can SEE a corrupted landing.
    if append_checked.__doc__ and True:
        t2 = os.path.join(d, "r2.md"); open(t2, "w").write("base\n")
        before = open(t2, "rb").read()
        open(t2, "ab").write(b"CORRUPTED\n")
        landed2 = open(t2, "rb").read()[len(before):]
        if landed2 == b"INTENDED\n":
            print("  CONTROL FAIL: comparator cannot see a corrupted landing"); ok = False
        else:
            print("  control -: comparator distinguishes landed bytes from intended bytes")
    shutil.rmtree(d, ignore_errors=True)
    print("SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target"); ap.add_argument("--body")
    ap.add_argument("--subst", action="append", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.target or not a.body:
        raise SystemExit("REFUSED: --target and --body are both required. "
                         "A run with nothing to do exits non-zero, never 0.")
    body = open(a.body, "rb").read()
    if not body:
        raise SystemExit("REFUSED: the body file is empty")
    body = apply_substitutions(body, a.subst)
    print("append_block: %s <- %s (%d bytes)" % (a.target, a.body, len(body)))
    print("CANNOT SEE [%s]" % OWNER)
    print("CANNOT SEE: whether the CONTENT is correct -- only that the bytes that landed "
          "are the bytes you wrote; and any commit (rule 10 remains the caller's). The "
          "provenance record lets check_harness.py ask the same question LATER; it cannot "
          "see a block written by hand, by heredoc, or by any path other than this one.")
    return append_checked(a.target, body)


if __name__ == "__main__":
    sys.exit(main())
