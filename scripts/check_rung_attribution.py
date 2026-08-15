#!/usr/bin/env python3
"""Per-agent commit attribution: put authorship in the artifact that travels.

WHY THIS EXISTS (docket D124, and D127 which records what this does and does not fix)
=====================================================================================
Ladder V's R-ISOLATE turns on a non-author measuring a rung. D124 measured that
this cannot be checked from the repository at all. Re-measured here on
2026-08-15T02:51Z at `e639796e`, frame `git log HEAD` over the first-parent-free
ancestry of HEAD, author identities counted with `--pretty='%an <%ae>'`:

    1,849 commits reachable from HEAD, 4 distinct author identities
    1,217 of 1,217 commits since 2026-08-01T00:00Z -- 100% -- carry the single
          identity `Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`
       36 of 36 today (2026-08-15) carry it too
    the other three identities are a human (`Sanaa Mouzahir`, last commit
          2026-07-26, before the agent era) and an 11-commit window of
          `Claude <noreply@anthropic.com>` on 2026-07-30/31

(D124's figures were 1,837 / 1,165 / 102 when it was written a few hours
earlier. The numbers move because the lab commits; the ratio does not move,
because it is a floor and not a spread.)

The only per-commit field that varies is `Co-Authored-By`, and it names a MODEL.
Any two of the hundreds of same-model agent sessions are byte-identical in
metadata. So every "a non-author measured this" claim in this lab rests on
evidence outside the repository -- dispatch briefs and per-machine session
transcripts under `~/.claude/projects/.../*.jsonl`, which no reader of a clone
can see. That is the same defect as `check_bundle_drift()` grading against a
gitignored reference: **the evidence for a verification must live where a later
reader can reach it**, and if it does not, the verification expires the moment
it is made.

The fact that makes this fixable: nothing configures that identity. There is no
`user.name` or `user.email` in `.git/config`, and `~/.gitconfig` does not exist
-- verified 2026-08-15. Git synthesises `Ubuntu <ubuntu@$(hostname)>` from the
unix user and the host. It is convention, not constraint.

THE CARRIER, AND THE FOUR THINGS REJECTED
=========================================
CHOSEN -- a `Lab-Agent:` trailer in the commit message:

    Lab-Agent: <host>/<session-uuid>/<tag>
    Lab-Agent: ip-172-31-43-247/64b13819-ff95-4d4d-a50f-3720bab19084/-

The message is part of the commit object. It travels with `clone`, `fetch`,
`format-patch`, `bundle` and `archive`; it is replayed verbatim by `cherry-pick`
and `rebase`. A reader of a clone re-derives the claim with `git log`, which is
the whole point and the test the rejected options fail.

REJECTED -- `GIT_AUTHOR_EMAIL` / the author and committer fields. Three reasons,
the first decisive: this harness does not persist shell state between tool
calls ("Shell state (env vars, functions) does not persist; the shell is
initialized from the user's profile"), so an `export GIT_AUTHOR_EMAIL=...` in
one call is gone by the next -- an adoption instruction built on it silently
stops working after one command. Second, it is destructive rather than additive:
it overwrites the one field that has been uniform for 1,849 commits, and any
future archaeology keyed on that uniformity breaks. Third, author and committer
diverge under `cherry-pick` -- the replay keeps the original author and takes a
new committer -- so two fields disagree about who did what and tooling reads
whichever it happens to read. This lab has already been bitten by assuming a
relation survives a cherry-pick; a scheme whose two halves disagree across one
is a second helping.

REJECTED -- `git notes`. Notes live in `refs/notes/*`, which `git clone` does
not fetch, `git push` does not send, and `cherry-pick` does not copy without
`notes.rewriteRef` configured per clone. A note is evidence stored beside the
artifact instead of inside it: exactly the gitignored-reference failure, wearing
a different hat.

REJECTED -- per-agent GPG signing. It would be genuinely unforgeable, and that
is not the threat (see below). Key material must be provisioned per agent, which
cannot be compressed into one line of a dispatch brief, so it would not be
adopted; an unadopted strong mechanism is weaker than an adopted weak one.

REJECTED -- overloading `Co-Authored-By`. It already carries the model name and
is consumed by GitHub's coauthor UI. Two meanings in one key makes the 1,217
existing values ambiguous, and it would attach a synthetic address to a live UI.

WHAT THE IDENTITY IS, AND WHAT IT IS NOT
========================================
The deciding part of the identity is `<host>/<session-uuid>`, taken from
`os.uname().nodename` and `$CLAUDE_CODE_SESSION_ID`. That UUID names a Claude
Code SESSION -- one `claude` process, one context window, one transcript. It is
set by the harness, not chosen by the agent.

It does NOT name an individual subagent. Measured 2026-08-15: every subagent of
a session inherits the same `CLAUDE_CODE_SESSION_ID` and the same `CLAUDE_PID`
(the pid of the `claude` process itself), and the per-call shell pid changes on
every tool call, so no finer handle is derivable from the environment. The
consequence is stated plainly rather than papered over:

    TWO AGENTS DISPATCHED BY THE SAME CHIEF SESSION READ AS THE SAME AGENT.

`<tag>` is a free slug an agent may pass to distinguish itself within a session.
It is recorded, it is printed, and **it does not decide the verdict**: a
same-session pair is AUTHOR whatever the tags say. The tag is the one field an
agent types, therefore the one field a copied dispatch brief can duplicate by
accident, therefore the last field that should be allowed to certify
independence. It is carried so a human reading the log can see which agent, and
so a later mechanism with a real per-agent handle can strengthen this one
without changing the grammar.

The price, stated so nobody discovers it in a rung: **to close a rung
mechanically, the grader must be dispatched from a different chief session than
the author.** Two chief sessions run on this box, so that is reachable. Where it
is not reachable the checker says AUTHOR, the closure is not certified here, and
it rests on dispatch records exactly as it does today. Nothing regresses; some
things stop being claimable.

THREAT MODEL, in one paragraph
==============================
This is an honesty instrument, not a security boundary. It defends against
accident: an agent cannot inherit another agent's identity by copying a brief,
because the deciding fields are read from the environment at commit time and
never typed. It defends against nothing done on purpose. Any agent can write any
`Lab-Agent:` line into any message file; the trailer is unsigned, unverified
against any registry, and the session UUID it names is not checkable by a reader
of a clone. A `cherry-pick` or `rebase` replays the ORIGINAL agent's trailer onto
a NEW sha, so a replayed commit attributes itself to whoever wrote it first, not
to whoever replayed it -- and `--amend` by a second agent leaves the first
agent's trailer in place unless it is re-emitted. Treat a NON-AUTHOR verdict as
"the repository contains no evidence that these were the same session", never as
"these were provably different agents". The mechanism raises the cost of a false
independence claim from zero to one deliberate lie, and that is all it does.

IT DEGRADES TO UNKNOWN, NEVER TO INDEPENDENT
============================================
A missing identifier reading as independence would be strictly worse than
today's uniform ignorance, because today nobody is fooled. So: absent trailer,
malformed trailer, two trailers on one commit, or a commit predating the anchor
all resolve to no identity, and a query touching one returns UNKNOWN with a
reason naming which commits and why. The one exception is deliberate and runs
the safe way: if some graded commit is unattributed and ANOTHER graded commit
matches the closing commit's identity, the verdict is AUTHOR, not UNKNOWN --
because AUTHOR can only ever deny a closure, so resolving that ambiguity toward
AUTHOR cannot manufacture an independence claim.

BACKFILL IS IMPOSSIBLE, AND THE MECHANISM STARTS AT ONE NAMED COMMIT
====================================================================
`ANCHOR` below is the commit that introduces this mechanism. Commits before it
carry no identity and never will: the information -- which session made them --
was never recorded anywhere that travels, and reconstructing it would require
rewriting 1,849 commits, which is forbidden here and would be a fabrication
anyway. **Every independence claim about work before `ANCHOR` continues to rest
on dispatch records outside the repository, and this mechanism does not reach
backwards to help it.** Any `Lab-Agent:` line found on a commit before `ANCHOR`
is therefore a FAIL, not a bonus: it means either history was rewritten or a
trailer was fabricated.

WHAT A GREEN RUN HERE DOES NOT MEAN
===================================
The unargumented run is an INTEGRITY check on the mechanism, not a coverage
claim. PASS means "no commit since the anchor lies about its identity, and no
commit before the anchor claims one". It does NOT mean authorship is known: the
adoption ratio is printed in the frame on every run, loudly, and while it reads
`1 of 40` the honest summary of this repository is still "authorship is
unknown for 39 of the last 40 commits".

And it does not touch the other half of R-ISOLATE. That rule also requires a
grader to EXECUTE the claim rather than read the author's summary of it, and
nothing here can see the difference: a grader that read a summary and a grader
that ran the code commit identical bytes. A green attribution check is not a
green independence claim. It is one of the two necessary conditions, machine-
checked for the first time; the other stays on the honour system.

USAGE
=====
    scripts/check_rung_attribution.py                    # integrity check (no args)
    scripts/check_rung_attribution.py --emit-trailer     # the line to append
    scripts/check_rung_attribution.py --emit-trailer --tag grader-v13
    scripts/check_rung_attribution.py --closing <rev> --graded <rev-or-range> ...
    scripts/check_rung_attribution.py --json             # same verdicts, machine-readable

ADOPTION -- one line, quotable in a dispatch brief:

    Before committing, append your agent identity to the message file:
    `python3 scripts/check_rung_attribution.py --emit-trailer >> <msgfile>`

Nothing here installs itself and nothing here writes to the tree: `--emit-trailer`
prints one line to stdout and the shell's `>>` does the writing, so the commit
invocation this lab mandates -- `git add <paths>` then
`git commit -F <msgfile> -- <paths>` -- is unchanged.

EXIT CODES -- the contract `scripts/lab_check.py` reads
    0  PASS      1  FAIL      3  UNKNOWN
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
AUTHOR, NON_AUTHOR = "AUTHOR", "NON-AUTHOR"

#: The exit contract, as literals. `sdk/tests/test_rung_attribution.py` types
#: these numbers out again rather than importing them, for the reason
#: `test_lab_check.py` gives: a test that asks the module under test what the
#: right answer is has not tested it.
EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_UNKNOWN = 3

#: THE COMMIT THIS MECHANISM STARTS FROM. `None` until the introducing commit
#: exists and its sha is known -- the first commit cannot name itself. Commits
#: before this one carry no identity and cannot be given one; see the docstring.
ANCHOR: str | None = "e933e31b62b056e65bb99572adc91c0914e6b83f"

#: The grammar, deliberately strict. Anything that starts `Lab-Agent:` and does
#: not match this is MALFORMED -- a broken emitter -- and is never silently
#: treated as absent, because "the emitter is broken" and "this agent did not
#: adopt the mechanism" are different findings.
TRAILER_RE = re.compile(
    r"^Lab-Agent:[ \t]+"
    r"(?P<host>[A-Za-z0-9][A-Za-z0-9._-]{0,63})/"
    r"(?P<session>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/"
    r"(?P<tag>[A-Za-z0-9._-]{1,32})[ \t]*$")
ANY_TRAILER_RE = re.compile(r"^Lab-Agent:")

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

#: Trailer states. `ok` is the only one that yields an identity; every other
#: value yields `None`, which is what makes UNKNOWN the default rather than a
#: special case somebody has to remember to write.
OK, ABSENT, MALFORMED, DUPLICATE, PRE_ANCHOR = (
    "ok", "absent", "malformed", "duplicate", "pre-anchor")

_UNIT = "\x1f"
_REC = "\x1e"


@dataclasses.dataclass
class Commit:
    """One commit, and what the repository says about who made it."""
    sha: str
    when: str
    subject: str
    state: str
    identity: str | None = None      # "<host>/<session>" -- the deciding part
    tag: str | None = None           # self-declared, never decides
    after_anchor: bool | None = None

    @property
    def short(self) -> str:
        return self.sha[:8]

    def describe(self) -> str:
        who = self.identity or f"<{self.state}>"
        tag = f" tag={self.tag}" if self.tag else ""
        return f"{self.short} {self.when} {who}{tag}  {self.subject[:60]}"


# ---------------------------------------------------------------------------
# git, read-only. Nothing in this module writes anything, anywhere.
# ---------------------------------------------------------------------------

def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True)


def parse_trailer(body: str) -> tuple[str, str | None, str | None]:
    """(state, identity, tag) for one commit message body.

    Returns an identity ONLY for state `ok`. Two `Lab-Agent:` lines is
    DUPLICATE rather than "take the first": a commit that claims two identities
    has not told us which agent made it, and picking one would invent an answer.
    """
    lines = [ln.rstrip("\r") for ln in body.splitlines()]
    claims = [ln for ln in lines if ANY_TRAILER_RE.match(ln)]
    if not claims:
        return ABSENT, None, None
    if len(claims) > 1:
        return DUPLICATE, None, None
    m = TRAILER_RE.match(claims[0])
    if not m:
        return MALFORMED, None, None
    return OK, f"{m.group('host')}/{m.group('session')}", m.group("tag")


def _is_after_anchor(root: Path, sha: str, anchor: str | None) -> bool | None:
    """True if `anchor` is an ancestor of `sha` (or is `sha`); None if unknown."""
    if not anchor:
        return None
    r = _git(root, "merge-base", "--is-ancestor", anchor, sha)
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False
    return None


def read_commits(root: Path, revs: list[str], anchor: str | None
                 ) -> tuple[list[Commit], str]:
    """Read commits by sha. Returns (commits, error) -- error is "" on success."""
    out: list[Commit] = []
    for sha in revs:
        r = _git(root, "log", "-1",
                 f"--format=%H{_UNIT}%aI{_UNIT}%s{_UNIT}%B{_REC}", sha)
        if r.returncode != 0:
            return [], f"git log failed for {sha!r}: {r.stderr.strip()}"
        blob = r.stdout.split(_REC)[0]
        parts = blob.split(_UNIT)
        if len(parts) < 4:
            return [], f"unreadable commit record for {sha!r}"
        full, when, subject, body = parts[0].strip(), parts[1], parts[2], parts[3]
        state, identity, tag = parse_trailer(body)
        after = _is_after_anchor(root, full, anchor)
        # A commit before the anchor is not "missing a trailer" -- the
        # mechanism did not exist. Naming that separately is what stops the
        # report from reading as though those agents were careless.
        if state == ABSENT and after is False:
            state = PRE_ANCHOR
        out.append(Commit(sha=full, when=when, subject=subject, state=state,
                          identity=identity, tag=tag, after_anchor=after))
    return out, ""


def resolve(root: Path, specs: list[str]) -> tuple[list[str], str]:
    """Expand rev specs to shas. A spec containing `..` walks; a bare rev does not.

    `git rev-list <sha>` without `--no-walk` returns every ancestor, so a
    dispatcher that meant "this one commit" would silently grade the whole
    history and get a guaranteed AUTHOR. The two forms are separated here.
    """
    shas: list[str] = []
    seen: set[str] = set()
    for spec in specs:
        args = ["rev-list", spec] if ".." in spec else ["rev-list", "--no-walk", spec]
        r = _git(root, *args)
        if r.returncode != 0:
            return [], f"cannot resolve {spec!r}: {r.stderr.strip()}"
        found = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        if not found:
            return [], f"{spec!r} resolved to zero commits"
        for sha in found:
            if sha not in seen:
                seen.add(sha)
                shas.append(sha)
    return shas, ""


# ---------------------------------------------------------------------------
# The verdict. Pure, so the tests can drive it directly as well as end to end.
# ---------------------------------------------------------------------------

def attribution(closing: Commit, graded: list[Commit]) -> tuple[str, str]:
    """AUTHOR / NON-AUTHOR / UNKNOWN, with the reason that produced it.

    Rule order is load-bearing and is not the obvious one. The same-agent test
    runs BEFORE the completeness test, so a graded set that is half unattributed
    and half provably the closing agent returns AUTHOR rather than UNKNOWN.
    AUTHOR can only ever DENY a closure, so resolving that ambiguity toward
    AUTHOR cannot manufacture an independence claim; resolving it the other way
    could.
    """
    if not graded:
        return UNKNOWN, ("the graded set is empty -- zero commits matched the "
                         "selector. Defect class B1: a checker that examined "
                         "nothing reports UNKNOWN, never a clean answer")

    if closing.identity is None:
        if closing.state == PRE_ANCHOR:
            return UNKNOWN, (f"the closing commit {closing.short} predates the "
                             f"anchor {(ANCHOR or '?')[:8]}, where this mechanism "
                             f"starts. Backfill is impossible; this closure's "
                             f"independence rests on dispatch records outside "
                             f"the repository")
        return UNKNOWN, (f"the closing commit {closing.short} carries no readable "
                         f"agent identity ({closing.state})")

    same = [c for c in graded if c.identity == closing.identity]
    if same:
        names = ", ".join(c.short for c in same[:6])
        more = "" if len(same) <= 6 else f" (+{len(same) - 6} more)"
        return AUTHOR, (f"{len(same)} of {len(graded)} graded commits carry the "
                        f"closing commit's own identity {closing.identity}: "
                        f"{names}{more}. The measurer is an author")

    blind = [c for c in graded if c.identity is None]
    if blind:
        pre = [c for c in blind if c.state == PRE_ANCHOR]
        tail = ""
        if pre:
            tail = (f"; {len(pre)} of them predate the anchor "
                    f"{(ANCHOR or '?')[:8]} and can never be attributed")
        names = ", ".join(c.short for c in blind[:6])
        more = "" if len(blind) <= 6 else f" (+{len(blind) - 6} more)"
        return UNKNOWN, (f"{len(blind)} of {len(graded)} graded commits carry no "
                         f"readable agent identity: {names}{more}{tail}. A "
                         f"missing identity is UNKNOWN, never independence")

    others = sorted({c.identity for c in graded if c.identity})
    return NON_AUTHOR, (f"the closing identity {closing.identity} appears on none "
                        f"of the {len(graded)} graded commits, which carry "
                        f"{len(others)} other identit"
                        f"{'y' if len(others) == 1 else 'ies'}: "
                        f"{', '.join(others)}")


def integrity(commits: list[Commit], pre_anchor_claims: list[str]
              ) -> tuple[str, str, dict]:
    """The unargumented run: is the mechanism telling the truth about itself?

    This is an INTEGRITY verdict, not a coverage one. Adoption is reported as a
    number in the frame and never as a verdict, because a check that goes red on
    the permanent state of the repository is a check somebody deletes -- after
    which it checks nothing at all.
    """
    counts = {s: 0 for s in (OK, ABSENT, MALFORMED, DUPLICATE, PRE_ANCHOR)}
    for c in commits:
        counts[c.state] = counts.get(c.state, 0) + 1
    stats = {"examined": len(commits), **counts,
             "pre_anchor_claims": len(pre_anchor_claims)}

    if not commits:
        return UNKNOWN, ("zero commits examined since the anchor. Defect class "
                         "B1: nothing was looked at, so nothing is known"), stats
    if pre_anchor_claims:
        names = ", ".join(s[:8] for s in pre_anchor_claims[:8])
        return FAIL, (f"{len(pre_anchor_claims)} commits BEFORE the anchor carry a "
                      f"Lab-Agent trailer ({names}). The mechanism starts at the "
                      f"anchor and cannot reach backwards, so either history was "
                      f"rewritten or a trailer was fabricated"), stats
    broken = [c for c in commits if c.state in (MALFORMED, DUPLICATE)]
    if broken:
        names = ", ".join(f"{c.short}({c.state})" for c in broken[:8])
        return FAIL, (f"{len(broken)} commits carry a Lab-Agent line that does not "
                      f"parse or claim two identities: {names}. A broken emitter "
                      f"is a defect in the instrument, not a gap in adoption"), stats
    if counts[OK] == 0:
        return UNKNOWN, ("no commit since the anchor carries a well-formed "
                         "identity, including the anchor itself -- there is "
                         "nothing here to check"), stats
    return PASS, (f"every Lab-Agent claim since the anchor is well formed "
                  f"({counts[OK]} of {len(commits)} commits carry one), and no "
                  f"commit before the anchor claims an identity. This says "
                  f"nothing about the {counts[ABSENT]} commits that carry none: "
                  f"their authorship is UNKNOWN"), stats


# ---------------------------------------------------------------------------
# Emitting an identity for THIS process
# ---------------------------------------------------------------------------

def local_identity(tag: str = "-") -> tuple[str | None, str]:
    """(trailer, why) for the session this process is running in."""
    session = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip().lower()
    if not session:
        return None, ("CLAUDE_CODE_SESSION_ID is not set: this process is not "
                      "inside a Claude Code session, so it has no agent identity "
                      "to claim. Emitting nothing rather than a placeholder -- a "
                      "placeholder is a fabricated identity")
    if not _UUID_RE.match(session):
        return None, (f"CLAUDE_CODE_SESSION_ID={session!r} is not a UUID; refusing "
                      f"to emit an identity this checker's own grammar rejects")
    host = re.sub(r"[^A-Za-z0-9._-]", "-", os.uname().nodename)[:64]
    slug = re.sub(r"[^A-Za-z0-9._-]", "-", tag)[:32] or "-"
    if not host or not host[0].isalnum():
        return None, f"hostname {os.uname().nodename!r} yields no usable host field"
    return f"Lab-Agent: {host}/{session}/{slug}", ""


# ---------------------------------------------------------------------------
# Frames. Printed on every run, in every mode, before the verdict.
# ---------------------------------------------------------------------------

_NOT_VERIFIED = (
    "NOT VERIFIED BY THIS CHECK: R-ISOLATE also requires a grader to EXECUTE the "
    "claim rather than read the author's summary of it. A grader that read a "
    "summary and a grader that ran the code commit identical bytes, so no "
    "attribution mechanism can tell them apart. A green run here is one of two "
    "necessary conditions, not independence.")

_FORGEABLE = (
    "FORGEABILITY: the trailer is unsigned and self-asserted. It resists accident "
    "(the deciding fields are read from the environment, never typed) and nothing "
    "done on purpose. NON-AUTHOR means 'no evidence of the same session', not "
    "'provably different agents'.")


def _print_frame(title: str, rows: list[tuple[str, str]]) -> None:
    print("=" * 78)
    print(title)
    print("=" * 78)
    width = max((len(k) for k, _ in rows), default=0)
    for k, v in rows:
        print(f"  {k.ljust(width)} : {v}")
    print("-" * 78)


def run_integrity(root: Path, as_json: bool) -> tuple[str, dict]:
    head = _git(root, "rev-parse", "HEAD")
    head_sha = head.stdout.strip() if head.returncode == 0 else ""
    frame: dict = {"mode": "integrity", "anchor": ANCHOR, "head": head_sha,
                   "repo": str(root)}

    if ANCHOR is None:
        v, why = UNKNOWN, ("this build of the mechanism is not anchored: ANCHOR is "
                           "None, so there is no commit from which attribution is "
                           "expected and nothing can be checked")
        frame.update(verdict=v, reason=why, stats={})
        return _emit(frame, as_json, "ATTRIBUTION INTEGRITY", [
            ("anchor", "NONE -- unanchored build"),
            ("head", head_sha[:8] or "?"),
        ])

    if _git(root, "cat-file", "-e", f"{ANCHOR}^{{commit}}").returncode != 0:
        v, why = UNKNOWN, (f"the anchor {ANCHOR[:8]} is not present in this "
                           f"repository. A clone that does not contain the anchor "
                           f"cannot be checked against it")
        frame.update(verdict=v, reason=why, stats={})
        return _emit(frame, as_json, "ATTRIBUTION INTEGRITY", [
            ("anchor", f"{ANCHOR[:8]} -- ABSENT from this repository"),
            ("head", head_sha[:8] or "?"),
        ])

    if not head_sha:
        frame.update(verdict=UNKNOWN, reason="HEAD does not resolve", stats={})
        return _emit(frame, as_json, "ATTRIBUTION INTEGRITY",
                     [("head", "unresolvable")])

    if _git(root, "merge-base", "--is-ancestor", ANCHOR, head_sha).returncode != 0:
        v, why = UNKNOWN, (f"HEAD {head_sha[:8]} is not a descendant of the anchor "
                           f"{ANCHOR[:8]}; this branch does not contain the "
                           f"mechanism's starting commit")
        frame.update(verdict=v, reason=why, stats={})
        return _emit(frame, as_json, "ATTRIBUTION INTEGRITY", [
            ("anchor", ANCHOR[:8]),
            ("head", f"{head_sha[:8]} -- not a descendant of the anchor"),
        ])

    shas, err = _since_anchor(root, ANCHOR, head_sha)
    if err:
        frame.update(verdict=UNKNOWN, reason=f"range unreadable: {err}", stats={})
        return _emit(frame, as_json, "ATTRIBUTION INTEGRITY", [("range", err)])

    commits, err = read_commits(root, shas, ANCHOR)
    if err:
        frame.update(verdict=UNKNOWN, reason=err, stats={})
        return _emit(frame, as_json, "ATTRIBUTION INTEGRITY", [("read", err)])

    pre = _pre_anchor_claims(root, ANCHOR)
    verdict, why, stats = integrity(commits, pre)
    adopted = stats.get(OK, 0)
    frame.update(verdict=verdict, reason=why, stats=stats,
                 commits=[c.describe() for c in commits[:20]])
    return _emit(frame, as_json, "ATTRIBUTION INTEGRITY", [
        ("anchor", f"{ANCHOR[:8]}  (backfill impossible -- see module docstring)"),
        ("head", head_sha[:8]),
        ("frame", f"git rev-list {ANCHOR[:8]}..HEAD, plus the anchor itself"),
        ("examined", str(stats["examined"])),
        ("ADOPTION", f"{adopted} of {stats['examined']} commits since the anchor "
                     f"carry an identity; {stats.get(ABSENT, 0)} carry none and "
                     f"their authorship is UNKNOWN"),
        ("malformed", str(stats.get(MALFORMED, 0))),
        ("duplicate", str(stats.get(DUPLICATE, 0))),
        ("pre-anchor claims", str(len(pre))),
    ])


def _has_parent(root: Path, rev: str) -> bool:
    r = _git(root, "rev-parse", "--verify", "--quiet", f"{rev}~1")
    return r.returncode == 0


def _since_anchor(root: Path, anchor: str, head: str) -> tuple[list[str], str]:
    """The anchor and every commit after it, inclusive.

    Written as `rev-list HEAD --not <anchor>^@` rather than `<anchor>~1..HEAD`
    because `^@` -- all parents of a rev -- expands to nothing for a root
    commit, while `~1` is an error. The anchoring commit of a fresh repository
    is a root commit, and a range expression that throws there would make the
    first run of a new clone UNKNOWN for a reason that is about git syntax
    rather than about attribution.
    """
    r = _git(root, "rev-list", head, "--not", f"{anchor}^@")
    if r.returncode != 0:
        return [], f"rev-list failed: {r.stderr.strip()}"
    shas = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if not shas:
        return [], (f"the anchor {anchor[:8]} is an ancestor of HEAD but the "
                    f"range is empty, which cannot happen -- treat this clone "
                    f"as unreadable rather than clean")
    return shas, ""


def _pre_anchor_claims(root: Path, anchor: str) -> list[str]:
    """Commits strictly before the anchor that nonetheless claim an identity."""
    if not _has_parent(root, anchor):
        return []
    # `<anchor>^@` is every parent, so a merge anchor's second-parent ancestry
    # is searched too. `<anchor>~1` would walk only the first-parent side and
    # report a clean zero over the half it never opened.
    r = _git(root, "log", "--format=%H", "--extended-regexp",
             "--grep=^Lab-Agent:", f"{anchor}^@")
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def run_query(root: Path, closing_spec: str, graded_specs: list[str],
              as_json: bool) -> tuple[str, dict]:
    frame: dict = {"mode": "attribution", "anchor": ANCHOR, "repo": str(root),
                   "closing_spec": closing_spec, "graded_specs": graded_specs}

    closing_shas, err = resolve(root, [closing_spec])
    if err or len(closing_shas) != 1:
        why = err or (f"--closing {closing_spec!r} resolved to "
                      f"{len(closing_shas)} commits; it must name exactly one")
        frame.update(verdict=UNKNOWN, reason=why)
        return _emit(frame, as_json, "RUNG ATTRIBUTION", [("closing", why)])

    graded_shas, err = resolve(root, graded_specs) if graded_specs else ([], "")
    if err:
        frame.update(verdict=UNKNOWN, reason=err)
        return _emit(frame, as_json, "RUNG ATTRIBUTION", [("graded", err)])

    # A closing commit that also appears in its own graded set is trivially an
    # author; it stays in the set rather than being filtered out, because
    # filtering it would hide a dispatch error behind a clean answer.
    all_commits, err = read_commits(root, [closing_shas[0], *graded_shas], ANCHOR)
    if err:
        frame.update(verdict=UNKNOWN, reason=err)
        return _emit(frame, as_json, "RUNG ATTRIBUTION", [("read", err)])

    closing, graded = all_commits[0], all_commits[1:]
    verdict, why = attribution(closing, graded)
    ids = sorted({c.identity for c in graded if c.identity})
    frame.update(verdict=verdict, reason=why,
                 closing=closing.describe(),
                 graded=[c.describe() for c in graded[:40]],
                 graded_count=len(graded),
                 graded_identities=ids,
                 unattributed=sum(1 for c in graded if c.identity is None))
    return _emit(frame, as_json, "RUNG ATTRIBUTION", [
        ("anchor", f"{(ANCHOR or 'NONE')[:8]}  (no commit before it can be attributed)"),
        ("closing", closing.describe()),
        ("graded selector", " ".join(graded_specs) or "<none given>"),
        ("graded commits", str(len(graded))),
        ("graded identities", ", ".join(ids) or "<none readable>"),
        ("unattributed", str(sum(1 for c in graded if c.identity is None))),
        ("decided by", "host/session -- the tag field never decides a verdict"),
    ])


def _emit(frame: dict, as_json: bool, title: str,
          rows: list[tuple[str, str]]) -> tuple[str, dict]:
    verdict = frame.get("verdict", UNKNOWN)
    if as_json:
        print(json.dumps(frame, indent=2, sort_keys=True))
        return verdict, frame
    _print_frame(title, rows)
    print(f"VERDICT: {verdict}")
    print(f"BECAUSE: {frame.get('reason', '')}")
    for c in frame.get("commits", [])[:20]:
        print(f"    {c}")
    print("-" * 78)
    print(_FORGEABLE)
    print(_NOT_VERIFIED)
    return verdict, frame


# ---------------------------------------------------------------------------
# CLI. Every option is a flag: `scripts/lab_check.py` refuses any check that
# declares a required positional, and it is right to.
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Per-agent commit attribution for Ladder V's R-ISOLATE.")
    p.add_argument("--repo", default=str(REPO),
                   help="repository to read (default: this checkout)")
    p.add_argument("--closing", default=None,
                   help="the rung's closing commit (exactly one rev)")
    p.add_argument("--graded", action="append", default=[], metavar="REV",
                   help="a commit or `A..B` range the closing commit grades; "
                        "repeatable")
    p.add_argument("--emit-trailer", action="store_true",
                   help="print this session's Lab-Agent trailer and exit")
    p.add_argument("--tag", default="-",
                   help="self-declared agent slug for --emit-trailer; recorded, "
                        "printed, and never allowed to decide a verdict")
    p.add_argument("--anchor", default=None, metavar="SHA",
                   help="override the built-in anchor. For grading another "
                        "repository and for this module's own controls. It "
                        "cannot turn AUTHOR into NON-AUTHOR -- it only moves the "
                        "line before which no identity exists -- and the anchor "
                        "actually used is printed in the frame on every run.")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    return p


def main() -> int:
    global ANCHOR
    args = build_parser().parse_args()
    if args.anchor is not None:
        ANCHOR = args.anchor
    codes = {PASS: EXIT_PASS, NON_AUTHOR: EXIT_PASS,
             FAIL: EXIT_FAIL, AUTHOR: EXIT_FAIL,
             UNKNOWN: EXIT_UNKNOWN}
    root = Path(args.repo)

    if args.emit_trailer:
        trailer, why = local_identity(args.tag)
        if trailer is None:
            print(f"no identity: {why}", file=sys.stderr)
            return EXIT_UNKNOWN
        print(trailer)
        return EXIT_PASS

    if args.closing or args.graded:
        if not args.closing:
            print("--graded needs --closing: there is no attribution question "
                  "without a measurer", file=sys.stderr)
            return EXIT_UNKNOWN
        verdict, _ = run_query(root, args.closing, args.graded, args.json)
        return codes[verdict]

    verdict, _ = run_integrity(root, args.json)
    return codes[verdict]


if __name__ == "__main__":
    sys.exit(main())
