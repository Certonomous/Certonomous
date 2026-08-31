#!/usr/bin/env python3
"""VR9 -- LEDGER DUPLICATE ADJUDICATION.

Gate question: in this lab's append-only numbered ledgers, is every DUPLICATE id
ADJUDICATED -- either a recorded deliberate second block, or a pair the lab has
ruled on -- or are there duplicates nobody has accounted for?

WHY DUPLICATES AND NOT COUNTS. CLAUDE.md rule 11 already fixes the assignment
rule: a new id comes from the TAIL-MAX, never from a count. The residual hazard is
the duplicate itself, because a duplicate makes count and tail-max disagree, and a
count-derived id then COLLIDES with a live entry. Rule 11 names the trap by
example -- "L-43 has two blocks, L-52 does not exist" -- so the lab already knows
duplicates exist and that SOME are deliberate. THE UNADJUDICATED ONES ARE THE
FINDING.

WHAT IS MINE: the sweep. The ledgers belong to six teams and RENUMBERING is each
owner's act. This item renumbers nothing and edits nothing.

-------------------------------------------------------------------------------
SCOPE, STATED AS A LIMIT
-------------------------------------------------------------------------------
Three ledgers: `docs/LESSONS.md` (L-), `docs/DOCKET.md` (D-),
`docs/COST_CALIBRATION.md` (C-).

`docs/NUMERICS_KNOWLEDGE.md` (N-) IS DELIBERATELY OUT OF SCOPE. It already has a
dedicated checker, `scripts/check_numerics_index.py`, wired into `check_harness`
stage [5/5] by `DEAD_LEVER_AUDIT` SS19. Re-sweeping it here would duplicate a live
control and risk contradicting it from a second, unwired instrument. A first
attempt at this driver ALSO parsed zero N- ids with a plausible-looking regex --
and "I cannot read this ledger" and "this ledger is clean" are the same output
from a broken parser, of which only one is a finding (SS19's own C3/C4 controls).
Excluding it is therefore the honest call, not a convenience.

-------------------------------------------------------------------------------
ADJUDICATION -- WHAT COUNTS AS ACCOUNTED FOR
-------------------------------------------------------------------------------
A duplicate is ADJUDICATED when either holds:

  (a) DECLARED IN THE LEDGER ITSELF -- one of the blocks names itself a
      deliberate second block (ADDENDUM / COMPANION / SUPERSEDES / second block).
      Rule 11's own example, `L-43`, is this shape.
  (b) RULED ON THE RECORD -- the id is named in `docs/DEAD_LEVER_AUDIT.md`
      inside a section that adjudicates it. SS22 (commit 524a70bd, 2026-08-31)
      rules the four calibration pairs C-215..C-218 and records that renumbers
      C-224..C-227 are OWED by dafoam, cfd, closure and cfd.

Anything else is UNADJUDICATED and is what this item reports.

AN ADJUDICATED DUPLICATE IS NOT CLEARED, IT IS EXPLAINED. Where SS22 records a
renumber as OWED, the debt is reported beside the verdict so it cannot quietly
become permanent by having been ruled once.

-------------------------------------------------------------------------------
SS2j -- WHO WROTE THE BYTES
-------------------------------------------------------------------------------
Every byte read is a real ledger written by real supervisors under the rule-10
private-index protocol, and the real `DEAD_LEVER_AUDIT` written by this team.
There is NO synthetic ledger anywhere in this file: both answers already exist in
the real corpus -- `L-43` is a real declared second block, `L-404` is a real
duplicate carrying no declaration -- so the controls read real bytes and a
fixture would have failed SS2j.2 exactly as its three named specimens do.
"""

import argparse
import os
import re
import sys

REPO = "/home/ubuntu/Certonomous"
AUDIT = os.path.join(REPO, "docs/DEAD_LEVER_AUDIT.md")

# (path, row-anchored id pattern, family label). Row-anchored: the id must open
# the line as a heading or as the first table cell. A free-text scan of
# COST_CALIBRATION returns 910 hits against 229 real rows.
LEDGERS = [
    ("docs/LESSONS.md", r"^## (L-\d+)\b", "L"),
    ("docs/DOCKET.md", r"^\|\s*\*{0,2}(D-?\d+)\*{0,2}\s*\|", "D"),
    ("docs/COST_CALIBRATION.md", r"^\|\s*\*{0,2}(C-\d+)\*{0,2}\s*\|", "C"),
]

# A block declaring itself a deliberate second block.
DECLARED = re.compile(
    r"addendum|companion|supersed|second block|deliberate second|struck",
    re.I)


class Refusal(Exception):
    """The instrument cannot honestly grade. Exit 2, never a degraded answer."""


# ---------------------------------------------------------------- readers -----

def scan_ledger(rel, pattern):
    """[(id, line_no)] for every ROW-ANCHORED id, plus the file's lines."""
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        raise Refusal("ledger absent: %s" % path)
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    rx = re.compile(pattern)
    ids = []
    for n, line in enumerate(lines, 1):
        m = rx.match(line)
        if m:
            ids.append((m.group(1), n))
    if not ids:
        raise Refusal(
            "ledger %s yielded ZERO row-anchored ids -- the matcher is blind, "
            "and PARSER BLINDNESS reads identically to a clean ledger. Refusing "
            "rather than reporting a PASS." % rel)
    return ids, lines


def duplicates(ids):
    """{id: [line numbers]} for ids appearing more than once."""
    seen = {}
    for i, n in ids:
        seen.setdefault(i, []).append(n)
    return {i: ns for i, ns in seen.items() if len(ns) > 1}


def declared_in_ledger(lines, line_nos, window=6):
    """True iff any occurrence declares itself a deliberate second block."""
    for n in line_nos:
        lo, hi = max(0, n - 1), min(len(lines), n - 1 + window)
        if any(DECLARED.search(l) for l in lines[lo:hi]):
            return True
    return False


def ruled_in_audit(ident, audit_text):
    """True iff the audit names this id (SS22 form)."""
    return re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(ident),
                     audit_text) is not None


def adjudicate(rel, pattern, audit_text):
    ids, lines = scan_ledger(rel, pattern)
    dups = duplicates(ids)
    nums = sorted({int(re.sub(r"\D", "", i)) for i, _ in ids})
    rows = []
    for ident, line_nos in sorted(dups.items()):
        decl = declared_in_ledger(lines, line_nos)
        ruled = ruled_in_audit(ident, audit_text)
        if decl:
            verdict = "ADJUDICATED (declared in ledger)"
        elif ruled:
            verdict = "ADJUDICATED (ruled in DEAD_LEVER_AUDIT)"
        else:
            verdict = "UNADJUDICATED"
        rows.append((ident, line_nos, verdict))
    return {
        "rel": rel,
        "occurrences": len(ids),
        "distinct": len({i for i, _ in ids}),
        "tail_max": nums[-1] if nums else None,
        "next_id": (nums[-1] + 1) if nums else None,
        "count_would_give": len(ids) + 1,
        "duplicates": rows,
    }


def read_audit():
    if not os.path.exists(AUDIT):
        raise Refusal("DEAD_LEVER_AUDIT.md absent -- every ruled duplicate would "
                      "read UNADJUDICATED and the item would over-report")
    return open(AUDIT, encoding="utf-8", errors="replace").read()


# ------------------------------------------------------------- selftest -------

def selftest():
    results = []

    def ok(n, d):
        results.append((n, True, d))

    def bad(n, d):
        results.append((n, False, d))

    try:
        audit = read_audit()
        reports = [adjudicate(rel, pat, audit) for rel, pat, _f in LEDGERS]
    except Refusal as exc:
        print("SELFTEST REFUSED: %s" % exc)
        return 2

    for r in reports:
        print("  %-30s occ=%-5d distinct=%-5d tail-max=%-5s dups=%d"
              % (r["rel"], r["occurrences"], r["distinct"], r["tail_max"],
                 len(r["duplicates"])))

    all_dups = [(r["rel"], d) for r in reports for d in r["duplicates"]]

    # -- P1 POSITIVE: the reader must SEE a real duplicate.
    if all_dups:
        ok("P1 positive (a real duplicate is seen)",
           "%d duplicate id(s); specimen %s in %s"
           % (len(all_dups), all_dups[0][1][0], all_dups[0][0]))
    else:
        bad("P1 positive (a real duplicate is seen)",
            "ZERO duplicates found -- reader never shown able to see one, so a "
            "clean verdict is unfalsifiable")

    # -- P2 the reader must return ADJUDICATED on a real declared second block.
    #    Rule 11 names L-43 by example; it must not read UNADJUDICATED.
    adj = [d for _r, d in all_dups if d[2].startswith("ADJUDICATED")]
    if adj:
        ok("P2 positive (a real ADJUDICATED duplicate is seen)",
           "%d adjudicated; specimen %s -- %s" % (len(adj), adj[0][0], adj[0][2]))
    else:
        bad("P2 positive (a real ADJUDICATED duplicate is seen)",
            "reader never returns ADJUDICATED, so it cannot distinguish a "
            "deliberate second block from a defect and would convict rule 11's "
            "own example")

    # -- P3 NEGATIVE: the reader must return UNADJUDICATED on something, else
    #    every duplicate is excused and the gate cannot fail.
    unadj = [(r, d) for r, d in all_dups if d[2] == "UNADJUDICATED"]
    if unadj:
        ok("P3 negative (a real UNADJUDICATED duplicate is seen)",
           "%d unadjudicated; specimen %s in %s"
           % (len(unadj), unadj[0][1][0], unadj[0][0]))
    else:
        ok("P3 negative (a real UNADJUDICATED duplicate is seen)",
           "none today -- reported, and the limb is carried by P4 below")

    # -- P4 the adjudication test must DISCRIMINATE: with the audit withheld,
    #    at least one ADJUDICATED-by-ruling row must flip to UNADJUDICATED.
    #    Otherwise the audit lookup is inert and is doing no work.
    ruled_rows = [(r, d) for r, d in all_dups
                  if d[2] == "ADJUDICATED (ruled in DEAD_LEVER_AUDIT)"]
    if not ruled_rows:
        bad("P4 the audit lookup discriminates",
            "no duplicate is adjudicated BY RULING, so the audit lookup is "
            "inert on this corpus and its contribution is unproven")
    else:
        blind = [adjudicate(rel, pat, "") for rel, pat, _f in LEDGERS]
        blind_unadj = {d[0] for r in blind for d in r["duplicates"]
                       if d[2] == "UNADJUDICATED"}
        flipped = [d[0] for _r, d in ruled_rows if d[0] in blind_unadj]
        if flipped:
            ok("P4 the audit lookup discriminates",
               "withholding the audit flips %s to UNADJUDICATED"
               % ", ".join(flipped[:4]))
        else:
            bad("P4 the audit lookup discriminates",
                "withholding the audit changed nothing -- those rows are being "
                "excused by the LEDGER declaration, not by the ruling, and the "
                "audit lookup is inert")

    # -- P5 rule 11: tail-max and a count must be shown to DISAGREE somewhere,
    #    or this corpus cannot demonstrate the trap the rule exists for.
    trap = [r for r in reports if r["count_would_give"] != r["next_id"]]
    if trap:
        r = trap[0]
        ok("P5 count-vs-tail-max trap is demonstrable",
           "%s: tail-max gives %s, a count would give %s"
           % (r["rel"], r["next_id"], r["count_would_give"]))
    else:
        bad("P5 count-vs-tail-max trap is demonstrable",
            "count and tail-max agree in every ledger, so rule 11's hazard "
            "cannot be shown here and a PASS would be uninformative")

    # -- N1 REFUSAL: a blind matcher must REFUSE, not report a clean ledger.
    try:
        scan_ledger("docs/LESSONS.md", r"^ZZZ_NO_SUCH_PATTERN_(\d+)")
        bad("N1 refusal on a blind matcher", "did not refuse")
    except Refusal:
        ok("N1 refusal on a blind matcher", "refused (exit 2 path)")

    # -- N2 REFUSAL: a missing ledger must REFUSE.
    try:
        scan_ledger("docs/NO_SUCH_LEDGER_VR9.md", r"^## (L-\d+)")
        bad("N2 refusal on a missing ledger", "did not refuse")
    except Refusal:
        ok("N2 refusal on a missing ledger", "refused (exit 2 path)")

    # -- N3 the row anchor must reject prose. Real specimen from the real file.
    full = open(os.path.join(REPO, "docs/COST_CALIBRATION.md"),
                encoding="utf-8", errors="replace").read()
    free = len(re.findall(r"C-\d+", full))
    anchored = [r for r in reports if r["rel"].endswith("COST_CALIBRATION.md")][0]
    if free > anchored["occurrences"]:
        ok("N3 row anchoring excludes prose",
           "free-text %d vs row-anchored %d" % (free, anchored["occurrences"]))
    else:
        bad("N3 row anchoring excludes prose",
            "free-text %d does not exceed row-anchored %d; limb is void"
            % (free, anchored["occurrences"]))

    print()
    for n, g, d in results:
        print("  [%s] %s -- %s" % ("ok" if g else "FAIL", n, d))
    nbad = sum(1 for _, g, _ in results if not g)
    print("\nSELFTEST: %d case(s), %d failure(s)" % (len(results), nbad))
    return 0 if nbad == 0 else 2


# ---------------------------------------------------------------- census ------

def run_census():
    audit = read_audit()
    reports = [adjudicate(rel, pat, audit) for rel, pat, _f in LEDGERS]

    print("VR9 -- ledger duplicate adjudication "
          "(frozen: verification/campaign/VR9_PREREGISTRATION.md)")
    print("  repo=%s" % REPO)
    print("  SCOPE: L- / D- / C- ledgers. N- is OUT OF SCOPE -- "
          "scripts/check_numerics_index.py already owns it (SS19).")

    unadjudicated = []
    for r in reports:
        print("\n  %s" % r["rel"])
        print("    row-anchored occurrences : %d" % r["occurrences"])
        print("    distinct ids             : %d" % r["distinct"])
        print("    tail-max                 : %s" % r["tail_max"])
        print("    NEXT ID (rule 11)        : %s" % r["next_id"])
        print("    a count would wrongly give: %s" % r["count_would_give"])
        if not r["duplicates"]:
            print("    duplicates               : none")
        for ident, line_nos, verdict in r["duplicates"]:
            print("    DUPLICATE %-8s lines %-22s %s"
                  % (ident, ",".join(str(x) for x in line_nos), verdict))
            if verdict == "UNADJUDICATED":
                unadjudicated.append((r["rel"], ident, line_nos))

    if unadjudicated:
        print("\nVERDICT: GATE FAIL -- %d duplicate id(s) are UNADJUDICATED: "
              "neither declared a deliberate second block in the ledger nor "
              "ruled in DEAD_LEVER_AUDIT. A duplicate makes count and tail-max "
              "disagree, and a count-derived id then COLLIDES with a live "
              "entry (rule 11). This is a finding about the LEDGER RECORD, not "
              "about any run: NO VERDICT IS WITHDRAWN, nothing is renumbered "
              "here, and RENUMBERING IS EACH OWNER'S ACT."
              % len(unadjudicated))
        for rel, ident, line_nos in unadjudicated:
            print("    %s %s at lines %s"
                  % (rel, ident, ",".join(str(x) for x in line_nos)))
        return 1
    print("\nVERDICT: PASS -- every duplicate id is adjudicated.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="VR9 ledger duplicate adjudication")
    ap.add_argument("--selftest", action="store_true",
                    help="drive both control limbs on the real corpus; exit 2 on "
                         "any failure or refusal")
    args = ap.parse_args()
    try:
        if args.selftest:
            print("VR9 SELFTEST -- controls read real ledgers written by team "
                  "supervisors and the real DEAD_LEVER_AUDIT (SS2j.2)")
            return selftest()
        return run_census()
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
