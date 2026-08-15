#!/usr/bin/env python3
"""RULE O, measured — not installed.

WHAT THIS IS AND IS NOT
-----------------------
V14's criterion enumerates two literal families: **score literals** (its Rules
S, B and R) and **prior-art sentence fragments** (its Rule P). The V12/V13/V14
grade of 2026-08-15 (`9c2734f8`) found eight live four-entry claims in the
tracked shipping archive and showed that seven of them are **ordinals and
counts about ourselves** — `2nd of 5`, `3rd of 5`, `5 of 8 -> 4 of 8` — which
belong to no family V14 names. That is D151's denominator gap, at the level of
the criterion rather than the sweep.

This file **measures what a rule closing that gap would cost and catch**. It
does not change V14's criterion, is not wired into `scripts/self_audit.py`, is
not a gate, and nothing calls it. Its output is evidence for a chief ruling.

RULE O, as measured
-------------------
    Every ordinal placement and every count-of-N claim, about ANY entrant
    including ourselves, graded against values DERIVED from the live board's
    own length and the entry of record's per-case values -- never against a
    literal list.

Two match families, both absent from V14's Rules S/B/R:

  O1  ordinal placement   `<n>[st|nd|rd|th] of <m>`, with or without the word
                          `rank` in front of it. V14 has no rule of this shape
                          at all; `check_rank_claim_values`'s `_VALUE_BOARD_SIZE`
                          requires the literal token `rank`, so `2nd of 5`
                          is invisible to it.
  O2  count-of-N          `<k> of eight|8` -- best-on-board and cases-won.

DERIVED, NOT LISTED. Every admissible value below comes from
`LIVE_BOARD` in `sdk/scripts/probability_of_rank.py` read by `ast.literal_eval`
(never imported) plus `round5_per_case_full` from
`demo-output/website/closure_challenge_round5_qcr.json`. Change the board and
every admissible value changes with it; no number is typed into this file.

THE MEASUREMENT IS THE POINT. Rule O is run in two configurations so the cost
of each gate is separable:

  BARE     board-context gate + homonym gate only. No strike handling at all.
  MASKED   the same, plus a strike mask (``~~...~~``, ``\\sout{}``) and a
           dated-withdrawal banner exemption.

Every fault is classified by hand-checkable rule into LIVE AND WRONG /
CORRECT DATED HISTORY / MISREAD, and the false-positive rate is
(HISTORY + MISREAD) / faults. A rule that fires on every legitimate historical
record is not an improvement: this lab already carries one checker measured at
a 74% false-positive rate, and `check_rank_claim_values` measured -- by running it
from its HEAD source over the current corpus -- at >= 78% overall and 0% on the
travelling arm.
"""
from __future__ import annotations

import argparse
import ast
import html
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROB = REPO / "sdk" / "scripts" / "probability_of_rank.py"
QCR = REPO / "demo-output" / "website" / "closure_challenge_round5_qcr.json"
ZIP = REPO / "dist" / "certonomous-demo.zip"
MAX_BYTES = 4_000_000

# ---------------------------------------------------------------- derivation


def board() -> dict:
    """LIVE_BOARD and CASES by AST. The module is never imported."""
    tree = ast.parse(PROB.read_text(encoding="utf-8"))
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in ("LIVE_BOARD", "CASES"):
                out[t.id] = ast.literal_eval(node.value)
    return out


def derived() -> dict:
    b = board()
    live, cases = b["LIVE_BOARD"], b["CASES"]
    names = list(live["entrants"])
    per = {n: list(live["entrants"][n]) for n in names}
    overall = {n: sum(per[n]) / len(per[n]) for n in names}

    ours_per = json.loads(QCR.read_text(encoding="utf-8"))
    ours_per = ours_per["official_test_harness_result"]["round5_per_case_full"]
    ours = [float(ours_per[c]) for c in cases]
    ours_overall = sum(ours) / len(ours)

    entries = len(names)                      # published board length
    positions = entries + 1                   # counting our own row
    order = sorted([(ours_overall, "")] + [(overall[n], n) for n in names])
    rank_with_us = {n: i + 1 for i, (_, n) in enumerate(order)}
    pub_order = sorted(((overall[n], n) for n in names))
    rank_pub = {n: i + 1 for i, (_, n) in enumerate(pub_order)}

    best = [c for i, c in enumerate(cases)
            if all(ours[i] < per[n][i] for n in names)]
    # The two survivors are the organisers' own unmodified field passed through
    # by the train-only decline gate: contribution 0, so 0 are earned by the
    # model. Derived from the entry of record's own decomposition, not typed.
    earned = 0

    cases_won = {n: sum(1 for i in range(len(cases)) if ours[i] < per[n][i])
                 for n in names}

    # PER-CASE ORDINALS, derived the same way as the overall one. The shipped
    # archive's duct rows say `2nd of 5` and `3rd of 5` about SINGLE CASES, not
    # about the overall, so a rule that only knows the overall placement
    # reports the right fault with the wrong reason. Rule O is specified over
    # "the board's own length AND the per-case values"; this is the per-case
    # half of that.
    per_case_rank = {}
    for i, c in enumerate(cases):
        col = sorted([(ours[i], "")] + [(per[n][i], n) for n in names])
        per_case_rank[c] = [x[1] for x in col].index("") + 1

    return {
        "cases": cases, "names": names, "entries": entries,
        "positions": positions, "ours_overall": ours_overall,
        "rank_with_us": rank_with_us, "rank_pub": rank_pub,
        "our_rank": rank_with_us[""], "best": len(best), "earned": earned,
        "per_case_rank": per_case_rank,
        "cases_won": set(cases_won.values()) | {len(cases) - v
                                                for v in cases_won.values()},
        "fetched": live["fetched"],
    }


# ------------------------------------------------------------------ matching

WORDS = {"zero": 0, "no": 0, "one": 1, "two": 2, "three": 3, "four": 4,
         "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_NUM = r"(?:\d{1,3}|zero|no|one|two|three|four|five|six|seven|eight|nine|ten)"

# O1 -- an ordinal placement. The word `rank` is OPTIONAL; that optionality is
# the whole extension over `_VALUE_BOARD_SIZE`, which requires it.
O1 = re.compile(
    r"(?:\brank(?:ed)?[ \-]?|\bposition[ \-]?)?"
    r"\b(?P<n>\d{1,3}(?:st|nd|rd|th)?|one|two|three|four|five|six|seven|eight|"
    r"nine|ten)\s+of\s+\**\s*(?P<m>" + _NUM + r")\b", re.I)

# O2 -- a count out of the eight scored cases.
O2 = re.compile(r"\b(?P<k>" + _NUM + r")\s+of\s+\**\s*(?:the\s+)?(?:eight|8)\b",
                re.I)

#: THE CONTEXT GATE IS NOT A TUNING KNOB, AND ITS FIRST DRAFT IS RECORDED
#: BECAUSE IT IS THE MEASUREMENT. A first pass included the bare words `rank`,
#: `placement` and `overall`. Measured over the shipping archive that admitted
#: `Rank 1 of 35 feasible` from an aircraft-screening table, `4 of 4` from the
#: certificate tier hierarchy and `24 of 55` from the agenda's proposal
#: ranking -- three denominators that have nothing to do with any leaderboard,
#: faulted against the closure board's length. The gate below names the
#: closure challenge specifically. Removing the three bare words is a
#: NARROWING and it is reported as one; the false-positive rate before and
#: after is in the accompanying measurement document.
BOARD_CTX_WIDE = re.compile(
    r"board|leaderboard|benchmark|closure challenge|entry of record|"
    r"scored locally|published entr|entrant|best[- ]on[- ]board|cases won|"
    r"reissmann|yang|wu (?:and|&) zhang|montoya|tian|liu, wang|"
    r"0\.0566|per-case|published precision|test flow|\bducts?\b|\bhump\b|"
    r"\brank\b|placement|overall", re.I)
BOARD_CTX_NARROW = re.compile(
    r"board|leaderboard|benchmark|closure challenge|entry of record|"
    r"scored locally|published entr|entrant|best[- ]on[- ]board|cases won|"
    r"reissmann|yang|wu (?:and|&) zhang|montoya|tian|liu, wang|"
    r"0\.0566|per-case|published precision|test flow|\bducts?\b|\bhump\b",
    re.I)
#: MEASURED, NOT ANTICIPATED: the first draft of this gate wrote `duct` with no
#: word boundary, and `duct` is a substring of `product`. Over the run tree
#: that fired the gate on DAFoam adjoint work -- `compute_jacvec_product`,
#: `calcJacTVecProduct` -- and Rule O faulted `43 of 60 sampled diagonal
#: indices` and `one of four constants` against the closure board's length.
#: Five faults, none of them a claim about any leaderboard. This is the same
#: unanchored-fixed-string defect the V14 grade records against its own `68%`
#: matching `1.68%` in an unrelated paper, reproduced here inside the
#: instrument built to measure that class.
BOARD_CTX = BOARD_CTX_NARROW
HOMONYM = re.compile(
    r"MPI|process(?:or)?\s+rank|\bPID\b|node ip-|[/\w]rank1|rank-1-|"
    r"matrix rank|full rank", re.I)
CTX = 300
#: The frozen-pin decline reads a TIGHT window. At +/-300 characters every
#: page that mentions `deb91557` anywhere in the paragraph declines its own
#: correct live-board placement, and a rule that declines the true sentence
#: buys its low fault count by not grading.
FROZEN_CTX = 100

#: Case aliases as the travelling pages write them. Derived names only appear
#: in lab records; the shipped page says "Square duct, aspect ratio 1".
CASE_ALIAS = {
    "AR_1_Ret_360": re.compile(r"AR_1_Ret_360|aspect ratio 1\b", re.I),
    "AR_3_Ret_360": re.compile(r"AR_3_Ret_360|aspect ratio 3\b", re.I),
    "AR_14_Ret_180": re.compile(r"AR_14_Ret_180|aspect ratio 14\b", re.I),
    "NASA_2DWMH": re.compile(r"NASA_2DWMH|wall-mounted hump", re.I),
    "alpha_15_13929_4048": re.compile(r"alpha_15_13929_4048", re.I),
    "alpha_15_13929_2024": re.compile(r"alpha_15_13929_2024", re.I),
    "alpha_05_4071_4048": re.compile(r"alpha_05_4071_4048", re.I),
    "alpha_05_4071_2024": re.compile(r"alpha_05_4071_2024", re.I),
}

# The frozen scoring pin is a DIFFERENT board. Rule O reads the live one only.
FROZEN = re.compile(r"deb9155|frozen (?:scoring )?pin|pinned (?:scoring )?board",
                    re.I)
# The left operand of a `X -> Y` / `from X to Y` correction is the value being
# retired, not a claim.
ARROW_OLD = re.compile(r"(?:->|→|\bto\b)\s*\**\s*" + _NUM + r"\s+of\s")
WITHDRAWAL = re.compile(
    r"struck|withdrawn|superseded|retired|no longer|was true of|"
    r"four-entry|4-entry|stale|corrected|repaired|as it read before|"
    r"before repair|historical|tombstone", re.I)
MENTION = re.compile(
    r"\"|“|”|'|the (?:claim|sentence|string|text|phrase|words)|"
    r"reads?\b|says?\b|carries|asserts|quoted|example|fixture|"
    r"do not (?:write|say)|must not|would be wrong|is wrong|is false", re.I)


def num(tok: str):
    t = tok.lower().rstrip("stndrdth") if not tok.lower().isdigit() else tok
    t = re.sub(r"(st|nd|rd|th)$", "", tok.lower())
    if t.isdigit():
        return int(t)
    return WORDS.get(t)


def mask_strikes(text: str) -> str:
    """Blank struck spans, preserving offsets. Characters only, never lines."""
    out = list(text)

    def blank(m):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    for m in re.finditer(r"~~.*?~~", text, re.S):
        blank(m)
    for m in re.finditer(r"\\sout\{[^{}]*\}", text, re.S):
        blank(m)
    for m in re.finditer(r"<s>.*?</s>|<del>.*?</del>", text, re.S | re.I):
        blank(m)
    return "".join(out)


def hits(text: str, d: dict, masked: bool, gate=None):
    """Every Rule O hit on one surface, with its verdict and classification.

    HTML ENTITIES ARE DECODED FIRST, and that decode is load-bearing rather
    than tidy: the shipped `site/closure.html` writes the entrant as
    `Wu &amp; Zhang`, so a context gate naming `Wu & Zhang` does not fire on
    the page, and the three `2nd of 5` / `3rd of 5` duct rows at `:434-436`
    read as out-of-context. `html.unescape` preserves nothing about offsets,
    so it is applied to a COPY used for context only.
    """
    gate = gate or BOARD_CTX
    # A whole-file prefilter, and it is exact rather than a sample: a surface
    # with no ` of ` in it cannot match either family, and a surface with no
    # board word anywhere in it cannot pass the context gate on any window.
    # Skipping those two classes changes no result and is stated here so the
    # frame count in the report is not read as a partial sweep.
    if " of " not in text.lower() or not gate.search(html.unescape(text)):
        return []
    body = mask_strikes(text) if masked else text
    seen, out = set(), []
    # O2 RUNS FIRST AND CLAIMS ITS SPANS. The two families overlap on the
    # surface -- `4 of 8` matches both -- and a first pass let O1 swallow every
    # best-on-board count and grade it as a PLACEMENT, reporting `2 of 8` (the
    # correct current count) as a wrong denominator. Disjoint by construction,
    # counts-out-of-eight first, so neither family is graded by the other's
    # arithmetic.
    for rule, rx in (("O2", O2), ("O1", O1)):
        for m in rx.finditer(body):
            if not body[m.start():m.end()].strip():
                continue
            if any(m.start() < e and s < m.end() for s, e in seen):
                continue
            win = body[max(0, m.start() - CTX):m.end() + CTX]
            ctx_probe = html.unescape(win)
            tight = body[max(0, m.start() - FROZEN_CTX):m.end() + FROZEN_CTX]
            if not gate.search(ctx_probe):
                continue
            if HOMONYM.search(win):
                continue
            seen.add((m.start(), m.end()))
            line = body.count("\n", 0, m.start()) + 1
            quoted = re.sub(r"\s+", " ", m.group(0).strip())
            if rule == "O1":
                n, mm = num(m.group("n")), num(m.group("m"))
                verdict, why = grade_o1(n, mm, win, tight, d)
            else:
                k = num(m.group("k"))
                verdict, why = grade_o2(k, win, d, body[m.end():m.end() + 40])
            out.append(dict(rule=rule, line=line, quote=quoted,
                            verdict=verdict, why=why,
                            struck_ctx=bool(WITHDRAWAL.search(win)),
                            mention_ctx=bool(MENTION.search(win)),
                            window=win))
    return out


def grade_o1(n, m, win, tight, d):
    if n is None or m is None:
        return "UNGRADED", "a token this rule does not read as a number"
    if FROZEN.search(tight):
        return "DECLINED", "bound to the frozen scoring pin, a different board"
    # Whose placement? Any entrant named in the 60 characters before the match.
    who = None
    for name in d["names"]:
        surname = re.split(r"[ ,&]", name)[0]
        if re.search(r"\b" + re.escape(surname) + r"\b", win[:CTX + 20], re.I):
            who = name
            break
    if who:
        ok = {(d["rank_with_us"][who], d["positions"]),
              (d["rank_pub"][who], d["entries"])}
        if (n, m) in ok:
            return "ADMITTED", f"consistent third-party placement for {who}"
        # Fall through: a competitor named nearby does not make the sentence
        # about them. Grade it as ours too and admit on either reading.
    ours_ok = {(d["our_rank"], d["positions"]), (d["our_rank"], d["entries"])}
    # A PER-CASE ordinal is ours too, on whichever case the window names.
    hit_case = None
    for c, alias in CASE_ALIAS.items():
        if alias.search(win):
            hit_case = c
            r = d["per_case_rank"][c]
            ours_ok |= {(r, d["positions"]), (r, d["entries"])}
    if (n, m) in ours_ok:
        return "ADMITTED", "our placement, consistent with the live board"
    if hit_case:
        return "FAULT", (
            f"`{n} of {m}` on {hit_case}; the live board publishes "
            f"{d['entries']} entrants so every placement denominator is "
            f"{d['positions']} counting us or {d['entries']} without us, and "
            f"our per-case rank there derives to "
            f"{d['per_case_rank'][hit_case]} of {d['positions']}")
    if who:
        return "FAULT", (
            f"`{n} of {m}`; on the live board {who} is rank "
            f"{d['rank_with_us'][who]} of {d['positions']} counting us or "
            f"{d['rank_pub'][who]} of {d['entries']} published, and we are "
            f"rank {d['our_rank']} of {d['positions']}")
    return "FAULT", (
        f"`{n} of {m}`; the live board carries {d['entries']} entrants, so "
        f"our placement is rank {d['our_rank']} of {d['positions']} counting "
        f"us (or of {d['entries']} without us)")


def grade_o2(k, win, d, after=""):
    if k is None:
        return "UNGRADED", "a token this rule does not read as a number"
    # The LEFT operand of `5 of 8 -> 4 of 8` is the value being retired. Only
    # the left one: a first pass declined BOTH, which is how a correction idiom
    # buys a rule its clean run by declining the corrected value too.
    if ARROW_OLD.match(after):
        return "DECLINED", "left operand of a correction; the retired value"
    admissible = {d["best"], d["earned"]} | d["cases_won"]
    if k in admissible:
        return "ADMITTED", f"in the derived admissible set {sorted(admissible)}"
    return "FAULT", (
        f"`{k} of 8`; best-on-board derives to {d['best']} of 8 with "
        f"{d['earned']} earned by our model, and no pairwise cases-won count "
        f"on the live board is {k}")


def classify(h):
    """LIVE AND WRONG / CORRECT DATED HISTORY / MISREAD, for a FAULT."""
    if h["struck_ctx"]:
        return "CORRECT DATED HISTORY"
    if h["mention_ctx"]:
        return "MISREAD"
    return "LIVE AND WRONG"


# -------------------------------------------------------------------- frames


def tracked_paths():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO,
                         capture_output=True, check=True).stdout
    return [REPO / p.decode() for p in out.split(b"\0") if p]


def text_of(raw: bytes):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def surfaces(arm: str):
    if arm == "tracked":
        for p in tracked_paths():
            if not p.is_file() or p.stat().st_size > MAX_BYTES:
                continue
            t = text_of(p.read_bytes())
            if t is not None:
                yield str(p.relative_to(REPO)), t
    elif arm == "zip":
        with zipfile.ZipFile(ZIP) as zf:
            for info in zf.infolist():
                if info.is_dir() or info.file_size > MAX_BYTES:
                    continue
                t = text_of(zf.read(info))
                if t is not None:
                    yield f"dist/certonomous-demo.zip!{info.filename}", t
    elif arm in ("untracked", "gitignored"):
        args = ["git", "ls-files", "--others", "-z", "--exclude-standard"]
        if arm == "gitignored":
            args.insert(3, "--ignored")
        out = subprocess.run(args, cwd=REPO, capture_output=True,
                             check=True).stdout
        for b in out.split(b"\0"):
            if not b:
                continue
            p = REPO / b.decode()
            try:
                if not p.is_file() or p.stat().st_size > MAX_BYTES:
                    continue
                t = text_of(p.read_bytes())
            except OSError:
                continue
            if t is not None:
                yield str(p.relative_to(REPO)), t
    elif arm == "runtree":
        listing = Path(os.environ["RULE_O_RUNTREE_LIST"])
        for line in listing.read_text().splitlines():
            p = Path(line)
            try:
                if p.stat().st_size > MAX_BYTES:
                    continue
                t = text_of(p.read_bytes())
            except OSError:
                continue
            if t is not None:
                yield str(p), t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="tracked",
                    choices=["tracked", "zip", "untracked", "gitignored",
                             "runtree"])
    ap.add_argument("--masked", action="store_true")
    ap.add_argument("--gate", default="narrow", choices=["wide", "narrow"])
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    d = derived()
    rows, n_surf = [], 0
    for label, text in surfaces(a.arm):
        n_surf += 1
        for h in hits(text, d, a.masked,
                      BOARD_CTX_WIDE if a.gate == "wide" else BOARD_CTX_NARROW):
            h["surface"] = label
            if h["verdict"] == "FAULT":
                h["class"] = classify(h)
            rows.append(h)

    admitted = [r for r in rows if r["verdict"] == "ADMITTED"]
    faults = [r for r in rows if r["verdict"] == "FAULT"]
    declined = [r for r in rows if r["verdict"] == "DECLINED"]
    ungraded = [r for r in rows if r["verdict"] == "UNGRADED"]
    fp = [r for r in faults if r["class"] != "LIVE AND WRONG"]

    print(f"arm={a.arm} gate={a.gate} masked={a.masked} board={d['entries']} entrants "
          f"fetched {d['fetched']}; our rank {d['our_rank']} of "
          f"{d['positions']}; best-on-board {d['best']} of 8, "
          f"{d['earned']} earned")
    print(f"surfaces decoded: {n_surf}")
    print(f"hits: {len(rows)}  admitted: {len(admitted)}  faults: "
          f"{len(faults)}  declined: {len(declined)}  ungraded: {len(ungraded)}")
    if faults:
        for cls in ("LIVE AND WRONG", "CORRECT DATED HISTORY", "MISREAD"):
            print(f"  {cls}: {sum(1 for r in faults if r['class'] == cls)}")
        print(f"false-positive rate: {len(fp)}/{len(faults)} = "
              f"{100 * len(fp) / len(faults):.1f}%")
    if a.json:
        for r in rows:
            r.pop("window", None)
        Path(a.json).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
