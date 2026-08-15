#!/usr/bin/env python3
"""DERIVED-FIGURE CHECK. Every published figure, against the record it came from.

WHY THIS EXISTS (docket D88, motivated by D85 and D89)
=====================================================
`scripts/self_audit.py`'s `board_placement_faults` binds ORDINALS to ENTRANT
NAMES. It has no arithmetic predicate at all, and D88 measured the cost: the
blocking finding repaired on 2026-08-15 -- the seed bound stated as *"covers 84%
of the margin"* when against the live board it is 177% -- was never detectable in
either direction. Re-introducing that exact withdrawn sentence verbatim swept
clean under BOTH board referents, and falsifying a margin tenfold
(0.001365 -> 0.013650) also returned zero faults. A margin, a ratio and a
percentage are outside that check by construction, and nothing else looks.

D85 adds the second half: strike-and-keep, the convention this lab requires for
every correction, makes a sentence INVISIBLE to the placement check -- falsify an
ordinal and leave the strike marker beside it and the guard returns 0; delete the
marker and it returns 1. So the convention that makes a repair honest to a reader
exempts it from the only instrument that existed for it.

This module is a different instrument, not a widening of that one. Nothing in
`scripts/self_audit.py` is imported, read or modified here.

WHAT IT CHECKS
==============
Three predicates, in increasing order of how much context they need:

  R1  SOURCE.   A figure quoted in prose under an anchor phrase that names it
                must agree with the machine record it is derived from, at the
                precision the prose itself writes. Catches a transcribed number
                that no longer matches its record, and a number carrying more
                significant digits than its stated basis supports.

  R2  ARITHMETIC. Where prose states a computation with all three terms
                (`0.002419 / 0.0028863 = 0.838`), the arithmetic must hold under
                interval arithmetic on the written operands. Catches D88's own
                prescription: "a transcribed percentage that no longer divides".

  R3  COVERAGE. The idiom `<the seed bound> covers <P>% of ... the margin`, when
                it does NOT name its own denominator, is a claim about the
                CURRENT operative margin and must equal the ratio the records
                imply. When it DOES name a denominator, R2 grades it instead and
                R3 stands down -- which is the whole reason the dated ladder
                rounds that state `84% of the 0.0028863 margin` do not fault.

R2 IS DELIBERATELY NOT RUN CORPUS-WIDE, AND THAT WAS MEASURED
=============================================================
An unanchored arithmetic sweep over all 455 tracked Markdown and HTML files was
built first and measured before being rejected. With maximality guards (no
operator abutting either end, single-operator chains only) it checked 69
expressions and disagreed with 8. All 8 were inspected and all 8 are FALSE, in
three classes: a symbolic prefix the matcher cannot see (`p_inf + U^2/2 = 200.01`,
`(16+217+1,672)x4/60 = 127.0`), a parallel list matched last-term-to-first
(`16/33, 12/13, 7/35 = 48% / 92% / 20%`), and a ratio-as-notation where the `=`
binds a different quantity (`the weighted arm's 229.07/250 = 33`). A 100%
false-positive rate is not a check; this lab already ships one instrument with a
74% false-positive rate (`check_absolutes.py`) and the cost of that is that
readers ignore it. So R2 fires only on expressions in which a registered
quantity participates. The unanchored sweep's measurement is recorded here
instead of shipped.

READING ONLY UNSTRUCK TEXT IS MOST OF THE WORK (D85, inverted)
==============================================================
A struck figure is a deliberate historical record. Flagging one would punish the
convention that makes corrections honest and would train readers to ignore this
check, so A FALSE POSITIVE ON CORRECTLY STRUCK TEXT IS A WORSE DEFECT THAN A MISS
and the masker is written that way round. The idioms below were enumerated FROM
THE CORPUS, not assumed:

  X1  `~~ ... ~~`.  277 spans across the tracked corpus, of which 69 SPAN
      MULTIPLE LINES -- so a line-by-line masker is wrong here, and an early cut
      of this one was. Spans are bounded by a blank line (no renderer carries a
      strikethrough across a paragraph break), which also contains the damage
      from the 27 files that hold an ODD number of `~~` markers: every one is a
      generated OpenMDAO `n2.html` whose embedded payload happens to contain the
      digraph. Without the blank-line bound a single stray marker masks the rest
      of a file, which is a silent loss of coverage rather than a visible one.

  X2  `<s>`, `<del>`, `<strike>` element bodies, case-insensitive, and the
      `text-decoration: line-through` class names used on the website pages.

  X3  KEPT-RECORD BLOCKS. A block preserved verbatim as history, WITHOUT any
      inline strike marker, opened by a heading or bolded line saying `KEPT AS
      THE RECORD` / `kept for the record` / `AS WRITTEN <date>, KEPT ...`. The
      draft's `### <STOP> THE BANNER AS WRITTEN 2026-08-10, KEPT AS THE RECORD`
      is the load-bearing instance: the `84%` at `:652` sits inside it, is
      correct against the four-entry margin named on the same line, and must not
      fire. The block runs to the end of the enclosing blockquote when the
      marker is inside one, otherwise to the next heading at the same or a
      shallower level.

  X4  NEGATED AND QUOTED VALUES. `**177%**, not 84%` and `0.0028863 rather than
      0.001365` state a figure in order to REJECT it. A match whose number is
      immediately preceded by `not`, `rather than`, `instead of`, `no longer`,
      `never`, `was` or `used to` is a rejection, not a claim.

  What is NOT masked, deliberately: a `**STRUCK <date> -- ...**` or
  `**CORRECTED <date> ...**` NOTE. Those notes are the live corrected text and
  carry the figures a reader is meant to believe; the text they withdraw carries
  its own `~~` and is masked by X1. Masking the note as well would have hidden
  this run's flagship finding.

TOLERANCE IS A DESIGN DECISION, AND THIS IS THE DECISION
========================================================
A figure quoted to 2 significant figures and one quoted to 15 are both
legitimate. So:

  (a) EVERY COMPARISON IS AT THE PRECISION THE PROSE WROTE. A written decimal
      `0.838` denotes the interval [0.8375, 0.8385); `84%` denotes [83.5, 84.5).
      A quotation agrees if the source value falls inside the interval its own
      written form denotes. Nothing is compared with a fixed epsilon, because a
      fixed epsilon either fails every rounded figure or passes every wrong one.

  (b) OPERANDS IN R2 ARE INTERVALS TOO. `0.002419 / 0.0028863 = 0.838` is
      graded by propagating both operand intervals through the division and
      asking whether the result interval intersects the one the written result
      denotes. Without this, every correctly-rounded computation in the corpus
      faults.

  (c) A QUANTITY MAY HAVE SEVERAL LEGITIMATE BASES, AND EACH BASIS CARRIES THE
      PRECISION IT SUPPORTS. Our margin over Yang has three in circulation:
      0.0013528... against Yang's published 4-dp 0.0580, 0.0013658... against
      the 6-dp 0.058013 that `BOARD_RESCORE_2026-08-14.md` §3.1 prints, and
      0.0013653... against the full mean of eight per-case values, 0.0580125.
      All three are defensible and all three give 177%. A quotation passes if it
      agrees with ANY basis -- BUT ONLY UP TO THE DIGITS THAT BASIS SUPPORTS. A
      basis derived from a 6-dp input supports 6 dp; seventeen digits printed
      from it are digits nobody measured, and that is a fault, not a rounding.

WHAT THE TOLERANCE RULE CANNOT DISTINGUISH
  * A figure correct to the digits written but derived from a stale referent
    that happens to round the same way. `84%` of the four-entry margin and any
    percentage that also rounds to 84 are the same string to this check.
  * An error smaller than half an ulp of the last digit written. A figure
    quoted as `0.06` cannot be checked more tightly than +-0.005, and quoting
    coarsely is therefore a way to be unfalsifiable here. The check reports the
    written precision of every match so that is visible.
  * WHICH basis a document meant, when it names none. It reports the set.
  * A number that is simply absent. This check grades figures that are
    PRESENT; a claim that should have been made and was not is invisible to it.

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
===================================================================
    PASS     every source record was read, the in-memory controls behaved in
             both directions, at least one figure was matched, and no matched
             figure disagreed.
    FAIL     at least one unstruck figure disagrees with its record.
    UNKNOWN  a source record was unreadable or a key was missing; or zero
             figures matched; or a control misfired. An instrument that
             examined nothing has not cleared anything (D62), and a check whose
             controls do not fire is a statement about the instrument.

Exit codes: 0 PASS, 1 FAIL, 3 UNKNOWN. Nothing is written; no `2>/dev/null`
anywhere; no network. D55 rejected a network-dependent audit -- an audit that
needs the network is off whenever the network is, and its verdict stops being
reproducible from the tree. Every source here is a committed artifact.

ENUMERATION
===========
`git ls-files` for the tracked frame; `os.walk` is not used because a figure
that is not tracked does not travel. The shell's `grep` execs
`ugrep --ignore-files` and honours `.gitignore` (~23% of this tree) and its
`find` is `bfs`, which rejects GNU expressions; neither is invoked. The frame
block on every run states how many files were considered, how they were
selected, how many were opened, and how many could not be.

USAGE
=====
    scripts/check_derived_figures.py            # verdict + frame
    scripts/check_derived_figures.py --verbose  # every match, not just faults
    scripts/check_derived_figures.py --json
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import json
import re
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}

#: Tracked prose. HTML is in scope because `closure.html` and `benchmarks.html`
#: are travelling surfaces and have both carried a stale figure this week.
PROSE_GLOBS = ("*.md", "*.html")

#: Files above this are machine-generated report payloads, not prose. Stated
#: rather than silent: the count and the names are printed in the frame.
MAX_BYTES = 2_000_000

#: 53 of the 57 tracked HTML files are DAFoam-generated OpenMDAO `n2.html` /
#: `inputs.html` reports carrying minified d3 and Tabulator. Their payloads
#: contain `<s` (from `i<s;++i`) and `~~` as JS operators, which is where every
#: one of the 27 odd-`~~`-parity files in this tree comes from. They hold no
#: prose and no derived figure. Excluded by path, and the exclusion is counted
#: in the frame rather than being silent.
GENERATED_HTML = re.compile(r"/reports/.*\.html$")


# ---------------------------------------------------------------------------
# Numbers, and the interval a written decimal denotes
# ---------------------------------------------------------------------------

NUM = r"[0-9](?:[0-9,]*[0-9])?(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?"
_NUM_RE = re.compile(NUM)


def parse_written(text: str):
    """(value, half_width) for a written decimal, or None.

    `0.838` denotes [0.8375, 0.8385); the half-width is half an ulp of the last
    digit written. This is the whole tolerance rule for a single figure.
    """
    s = text.replace(",", "").replace("−", "-").strip()
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    exp = d.as_tuple().exponent
    if not isinstance(exp, int):
        return None
    return d, Decimal(1).scaleb(exp) / 2


def written_digits(text: str) -> int:
    """Significant digits actually written. `0.0013658082957863568` -> 17."""
    s = text.replace(",", "").lstrip("-−").lstrip("0.")
    return len(re.sub(r"[^0-9]", "", s).lstrip("0")) or 1


def agrees(written: str, value: Decimal) -> bool:
    """Does `value` fall inside the interval the written form denotes?"""
    pw = parse_written(written)
    if pw is None:
        return False
    v, h = pw
    return v - h <= value < v + h


# ---------------------------------------------------------------------------
# Source records -- committed artifacts only, read not imported
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Record:
    path: str
    how: str
    data: object = None
    error: str = ""


def _read_json(path: Path, rel: str) -> Record:
    try:
        return Record(rel, "json.load", json.loads(path.read_text()))
    except OSError as exc:
        return Record(rel, "json.load", error=f"unreadable: {exc}")
    except ValueError as exc:
        return Record(rel, "json.load", error=f"not valid JSON: {exc}")


def _read_module_literal(path: Path, rel: str, name: str) -> Record:
    """Pull a module-level literal out by AST, without importing the module.

    `sdk/scripts/probability_of_rank.py` is the machine record for the board --
    `LIVE_BOARD` is a dict literal in its source. `self_audit.py` reads it the
    same way and for the same reason: the audit must not need numpy, and must
    not execute the file it is grading.
    """
    how = f"ast literal {name}"
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError) as exc:
        return Record(rel, how, error=f"unparseable: {exc}")
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    try:
                        return Record(rel, how, ast.literal_eval(node.value))
                    except ValueError as exc:
                        return Record(rel, how,
                                      error=f"{name} is not a literal: {exc}")
    return Record(rel, how, error=f"no module-level {name}")


SOURCES = {
    "seed": ("demo-output/website/closure_challenge_seed_sensitivity.json",
             "json"),
    "qcr": ("demo-output/website/closure_challenge_round5_qcr.json", "json"),
    "board": ("sdk/scripts/probability_of_rank.py", "LIVE_BOARD"),
    "rank": ("sdk/scripts/probability_of_rank_record.json", "json"),
    "floor": ("demo-output/website/closure_challenge_rans_floor.json", "json"),
}


def read_sources(root: Path) -> dict:
    out = {}
    for key, (rel, how) in SOURCES.items():
        p = root / rel
        out[key] = (_read_json(p, rel) if how == "json"
                    else _read_module_literal(p, rel, how))
    return out


def dig(obj, *path):
    """Follow a key path; raise KeyError naming the path that broke."""
    cur = obj
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            raise KeyError(".".join(str(x) for x in path))
        cur = cur[k]
    return cur


# ---------------------------------------------------------------------------
# The registry: quantities, their bases, and the anchors that quote them
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Basis:
    value: Decimal
    digits: int            # significant digits this basis actually supports
    why: str


@dataclasses.dataclass
class Quantity:
    qid: str
    label: str
    bases: list
    anchors: list          # compiled regexes with a group named `v`
    unit: str = ""         # "" or "%"

    def verdict(self, written: str):
        """(ok, note). Passes on ANY basis, capped at that basis's digits."""
        n = written_digits(written)
        best = []
        for b in self.bases:
            if n > b.digits:
                best.append(f"{b.why}: supports {b.digits} sig digits, "
                            f"{n} written")
                continue
            if agrees(written, b.value):
                return True, b.why
            best.append(f"{b.why} = {b.value}")
        return False, "; ".join(best)


#: Quantities measured, priced and deliberately NOT shipped. Printed on every
#: run: an omission a reader cannot see is the same defect as a silent skip.
P_RANK1_NOT_SHIPPED: list = []


def _mean(vals):
    return sum(Decimal(str(v)) for v in vals) / Decimal(len(vals))


def _fsub(a: Decimal, b: Decimal) -> Decimal:
    """a - b as the lab's own Python computes it: IEEE double, then repr."""
    return Decimal(repr(float(a) - float(b)))


def build_registry(src: dict) -> tuple[list, list, dict]:
    """Returns (quantities, problems, derived-values-for-the-frame).

    Any unreadable record or missing key becomes a PROBLEM, which the caller
    turns into UNKNOWN. A quantity is never silently dropped.
    """
    problems, facts = [], {}
    P_RANK1_NOT_SHIPPED.clear()
    for k, r in src.items():
        if r.error:
            problems.append(f"source {k} ({r.path}): {r.error}")

    def get(k, *path):
        r = src[k]
        if r.error:
            raise KeyError(f"{r.path} unreadable")
        return dig(r.data, *path)

    qs = []

    # -- our overall, and the seed bound -----------------------------------
    try:
        ours = Decimal(str(get("qcr", "official_test_harness_result",
                               "round5_overall_full")))
        facts["ours_overall"] = ours
        # `our overall` legitimately names the as-scored entry OR a seed leg,
        # depending on the sentence -- "loaded adversely our overall becomes
        # 0.059047" is correct prose about a correct number. This check has no
        # discriminator for which one a sentence means, so all four are bases
        # and it says so. Consequence: it cannot catch a sentence that quotes
        # the adverse leg where it means the as-scored one.
        ov = [Basis(ours, 17, "closure_challenge_round5_qcr.json -> "
                              "official_test_harness_result.round5_overall_full")]
        for leg, node in sorted((src["rank"].data or {}).get("seed", {}).items()
                                if not src["rank"].error else []):
            if isinstance(node, dict) and "overall" in node:
                ov.append(Basis(Decimal(str(node["overall"])), 17,
                                f"probability_of_rank_record.json -> "
                                f"seed.{leg}.overall"))
        qs.append(Quantity(
            "ours_overall", "our round-5 overall (official harness)",
            ov,
            [re.compile(
                r"\bour\b[^.,;\n]{0,40}?(?:overall|entry|score)"
                r"[^.,;\n]{0,20}?(?:is|of|at|=|becomes)?\s*\*{0,2}"
                r"(?P<v>0\.0[45][0-9]{2,20})\b"),
             re.compile(
                r"(?<![-\w])(?:locally scored|we scored|scored)\s*\*{0,2}"
                r"(?P<v>0\.0[45][0-9]{2,20})\b"),
             re.compile(
                r"\*{0,2}(?P<v>0\.0[45][0-9]{2,20})\*{0,2}\s*"
                r"(?:is\s+)?(?:our|ours)\b[^.,;\n]{0,14}?"
                r"(?:overall|entry|score)")]))
    except KeyError as exc:
        problems.append(f"ours_overall: missing {exc}")

    try:
        bound = Decimal(str(get("seed", "spreads",
                                "overall_equivalent_S_bound")))
        facts["seed_bound"] = bound
        qs.append(Quantity(
            "seed_bound", "one-seed overall-equivalent bound",
            [Basis(bound, 17, "closure_challenge_seed_sensitivity.json -> "
                              "spreads.overall_equivalent_S_bound")],
            [re.compile(
                r"seed[- ](?:bound|uncertainty)[^.\n]{0,40}?"
                r"(?:of|is|at|=)\s*\*{0,2}(?P<v>0\.00[0-9]{1,20})\b"),
             re.compile(
                r"\*{0,2}(?P<v>0\.002[0-9]{1,20})\*{0,2}\s*"
                r"(?:seed|one-seed|single-seed)[- ](?:bound|uncertainty)"),
             re.compile(
                r"overall_equivalent_S_bound[^0-9\n]{0,40}"
                r"(?P<v>0\.00[0-9]{1,20})\b")]))
    except KeyError as exc:
        problems.append(f"seed_bound: missing {exc}")

    # -- the board, and the margin over the entry immediately ahead --------
    try:
        board = src["board"].data
        if src["board"].error:
            raise KeyError(src["board"].error)
        entrants = board["entrants"]
        pub = board.get("published_overall", {})
        leader = min(entrants, key=lambda n: _mean(entrants[n]))
        facts["leader"] = leader
        y_mean = _mean(entrants[leader])
        y_pub = Decimal(str(pub[leader])) if leader in pub else None
        facts["leader_overall_mean"] = y_mean
        facts["leader_overall_published"] = y_pub

        # The leader's overall is 0.058x. Anchoring on the leading digits as
        # well as on the name is deliberate: `<leader> ... at 0.001365` is our
        # MARGIN over the leader, a different quantity with its own entry, and
        # an early cut of this pattern bound the two together.
        anchors = [re.compile(
            re.escape(leader) + r"\b(?:'s)?[^.,;\n]{0,30}?"
            r"\b(?:at|of|is|scores?|overall)\s*\*{0,2}"
            r"(?P<v>0\.05[0-9]{2,20})\b"),
            re.compile(r"\*{0,2}(?P<v>0\.05[0-9]{2,20})\*{0,2}[^.,;\n]{0,20}?"
                       r"\b" + re.escape(leader) + r"\b(?:'s)?\s*"
                       r"(?:overall|score|entry)")]
        qs.append(Quantity(
            f"leader_overall", f"{leader}'s overall (the entry ahead of ours)",
            [Basis(y_mean, 17, "probability_of_rank.py LIVE_BOARD -> mean of "
                               f"eight published per-case values for {leader}"),
             ] + ([Basis(y_pub, 3, "probability_of_rank.py LIVE_BOARD -> "
                                   f"published_overall[{leader}] (4 dp)")]
                  if y_pub is not None else []),
            anchors))

        if "ours_overall" in facts:
            # Derived margins are computed in FLOAT, not exact decimal,
            # because that is what the lab's own Python produces and therefore
            # what the corpus prints. `0.058013 - 0.056647191704213645` is
            # exactly 0.0013658082957863568 in IEEE double and
            # 0.001365808295786355 in exact decimal; grading against the
            # decimal form would fault the draft at the eighteenth digit for a
            # representation difference and hide the real finding, which is
            # that seventeen digits were printed from a six-decimal input.
            m_mean = _fsub(y_mean, facts["ours_overall"])
            bases = [Basis(m_mean, 17,
                           f"{leader} full mean {y_mean} minus our "
                           f"{facts['ours_overall']}")]
            if y_pub is not None:
                bases.append(Basis(_fsub(y_pub, facts["ours_overall"]), 3,
                                   f"{leader} published 4-dp {y_pub} minus "
                                   f"ours -- supports 4 dp, not more"))
            # The 6-dp form BOARD_RESCORE_2026-08-14.md 3.1 prints -- rounded
            # HALF UP, which is what a human writing a table does and what that
            # table did (0.0580125 -> 0.058013). Decimal's default is
            # ROUND_HALF_EVEN and would give 0.058012, i.e. a basis nobody uses.
            y6 = y_mean.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            bases.append(Basis(_fsub(y6, facts["ours_overall"]), 5,
                               f"{leader} at the 6-dp {y6} that "
                               "BOARD_RESCORE_2026-08-14.md 3.1 prints -- "
                               "supports 5 sig digits, not more"))
            facts["live_margin"] = m_mean
            # `margin` alone is far too promiscuous: this corpus carries a
            # per-case margin, a four-entry Reissmann margin, a mesh margin and
            # a budget margin. The anchor must bind the margin to the entry
            # immediately ahead of ours, by name or by the `below it` idiom.
            qs.append(Quantity(
                "live_margin", f"our margin over {leader}", bases,
                [re.compile(
                    r"\b(?:over|to|behind|against)\s+\*{0,2}"
                    + re.escape(leader) + r"\b[^.;\n]{0,60}?\bmargin\b"
                    r"[^.;\n]{0,20}?(?:is|of|at|=)\s*\*{0,2}"
                    r"(?P<v>0\.0[0-9]{2,20})\b"),
                 re.compile(
                    r"\bmargin\b[^.;\n]{0,30}?\b(?:over|to|against)\s+\*{0,2}"
                    + re.escape(leader) + r"\b[^.;\n]{0,30}?(?:is|of|at|=)\s*"
                    r"\*{0,2}(?P<v>0\.0[0-9]{2,20})\b"),
                 # `below` alone matches any gap in the corpus -- an early cut
                 # bound a turbulence-model convergence gap of 0.0278. It must
                 # name what it is below.
                 re.compile(
                    r"sits?\s*\*{0,2}(?P<v>0\.0[0-9]{2,20})\*{0,2}\**\s*"
                    r"below\s+(?:it\b|that\b|"
                    + re.escape(leader) + r"\b)"),
                 re.compile(
                    r"our margin (?:is|of|at|=)\s*\*{0,2}"
                    r"(?P<v>0\.0[0-9]{2,20})\b")]))

            # -- the coverage ratio, R3's referent --------------------------
            if "seed_bound" in facts:
                ratios = []
                for b in bases:
                    if b.value > 0:
                        ratios.append(Basis(
                            (facts["seed_bound"] / b.value) * 100,
                            min(b.digits, 4),
                            f"seed bound / ({b.why})"))
                facts["coverage_pct"] = ratios[0].value if ratios else None
                qs.append(Quantity(
                    "coverage_pct",
                    "the seed bound as a percentage of the live margin",
                    ratios,
                    [re.compile(
                        r"(?:seed[- ](?:bound|uncertainty)|bound)[^.\n]{0,60}?"
                        r"covers?\s*\*{0,2}(?P<v>[0-9]{1,3}(?:\.[0-9]+)?)\s*%"),
                     re.compile(
                        r"covers?\s*\*{0,2}(?P<v>[0-9]{1,3}(?:\.[0-9]+)?)\s*%"
                        r"\*{0,2}\s*of\s+(?:that|the|this)\s+margin")],
                    unit="%"))
    except (KeyError, TypeError, ValueError) as exc:
        problems.append(f"board/margin: {exc}")

    # -- P(rank 1) ---------------------------------------------------------
    # The record holds SEVERAL legitimate P(rank 1) values, and a package
    # sentence may correctly quote any of them: as scored, the three seed legs,
    # and the eight leave-one-out drops. All are admitted as bases and named, so
    # a fault here means the figure matches NONE of them -- which is what the
    # stale four-entry 68% does.
    try:
        rk = src["rank"].data
        pb = [Basis(Decimal(str(get("rank", "p_rank1"))) * 100, 7,
                    "probability_of_rank_record.json -> p_rank1 (as scored)")]
        for leg, node in sorted((rk.get("seed") or {}).items()):
            if isinstance(node, dict) and "p_rank1" in node:
                pb.append(Basis(Decimal(str(node["p_rank1"])) * 100, 7,
                                f"seed.{leg}.p_rank1"))
        for case, node in sorted((rk.get("loo") or {}).items()):
            if isinstance(node, dict) and "p_rank1" in node:
                pb.append(Basis(Decimal(str(node["p_rank1"])) * 100, 7,
                                f"loo.{case}.p_rank1"))
        facts["p_rank1_pct"] = pb[0].value
        # NOT SHIPPED, and the measurement is the reason. With P(rank 1) in the
        # registry this check returned 13 further disagreements on the corpus,
        # of which the great majority are the four-entry board's 68% correctly
        # recorded in a DATED ladder round or closeout -- true of the board they
        # are dated to. The record itself holds twelve legitimate values (as
        # scored, three seed legs, eight leave-one-out drops) and the corpus
        # carries a thirteenth that was true until 2026-08-11T23:33Z. Telling a
        # stale assertion from a correct dated record needs the dated-context
        # discriminator that `self_audit.py`'s own BLIND-TO item 9 says does not
        # exist, and D85/D89 both name building it as the prerequisite. Shipping
        # this quantity without it would make this check the second instrument
        # in the lab with a false-positive rate high enough to be ignored.
        # Filed rather than shipped.
        P_RANK1_NOT_SHIPPED.append(
            "p_rank1: 13 hits on the corpus, mostly correct dated records; "
            "needs a dated-context discriminator (docket)")
        _unshipped = Quantity(
            "p_rank1", "P(rank 1), 400k-draw case bootstrap",
            pb,
            [re.compile(r"P\(rank ?1\)\s*(?:=|is|of|at)?\s*\*{0,2}"
                        r"(?P<v>[0-9]{1,3}(?:\.[0-9]+)?)\s*%")],
            unit="%")
        del _unshipped
    except KeyError as exc:
        problems.append(f"p_rank1: missing {exc}")

    # -- the adverse seed leg ---------------------------------------------
    try:
        adv = Decimal(str(get("rank", "seed", "adverse", "overall")))
        facts["adverse_overall"] = adv
        qs.append(Quantity(
            "adverse_overall", "our overall with the seed bound loaded adversely",
            [Basis(adv, 17, "probability_of_rank_record.json -> "
                            "seed.adverse.overall")],
            [re.compile(r"(?:adversely|adverse)[^.\n]{0,80}?our overall "
                        r"(?:becomes|is)\s*\*{0,2}(?P<v>0\.0[0-9]{3,20})\b"),
             re.compile(r"our overall (?:becomes|is)\s*\*{0,2}"
                        r"(?P<v>0\.059[0-9]{0,18})\b")]))
    except KeyError as exc:
        problems.append(f"adverse_overall: missing {exc}")

    # -- the RANS-identity floor ------------------------------------------
    try:
        fl = Decimal(str(get("floor", "rans_identity_reference_floor",
                             "overall_score")))
        facts["rans_floor"] = fl
        qs.append(Quantity(
            "rans_floor", "the RANS-identity reference floor",
            [Basis(fl, 4, "closure_challenge_rans_floor.json -> "
                          "rans_identity_reference_floor.overall_score")],
            [re.compile(r"(?:RANS[- ]identity|identity)\s*(?:reference\s*)?"
                        r"floor[^.\n]{0,40}?(?:of|is|at|=)\s*\*{0,2}"
                        r"(?P<v>0\.[0-9]{3,20})\b"),
             re.compile(r"\*{0,2}(?P<v>0\.10[0-9]{2,18})\*{0,2}\s*"
                        r"(?:RANS[- ]identity\s*)?floor\b")]))
    except KeyError as exc:
        problems.append(f"rans_floor: missing {exc}")

    return qs, problems, facts


# ---------------------------------------------------------------------------
# The masker -- X1..X3. Offsets are preserved so line numbers stay true.
# ---------------------------------------------------------------------------

#: X1. Bounded by a blank line: no renderer carries `~~` across a paragraph
#: break, and the bound is what stops one stray marker in a generated
#: `n2.html` from masking the rest of the file.
_TILDE = re.compile(r"~~(?:[^\n]|\n(?![ \t>]*\n))*?~~")

#: X2. Element bodies. Non-greedy and blank-line-bounded for the same reason.
_TAGS = re.compile(
    r"<(s|del|strike)\b[^>]*>(?:[^\n]|\n(?![ \t>]*\n))*?</\1>", re.I)
_STRIKE_CLASS = re.compile(
    r"<(\w+)[^>]*class=\"[^\"]*(?:strike|struck|line-through|superseded|"
    r"withdrawn)[^\"]*\"[^>]*>(?:[^\n]|\n(?!\s*\n))*?</\1>", re.I)

#: X3a. A block preserved verbatim as history, carrying no inline strike.
_KEPT_HEAD = re.compile(
    r"^[ \t>]*[#*_ ]*[^\n]*?"
    r"(?:KEPT AS THE RECORD|KEPT FOR THE RECORD|kept as the record"
    r"|kept for the record|AS WRITTEN \d{4}-\d{2}-\d{2}[^\n]*KEPT"
    r"|kept unchanged as the record)"
    r"[^\n]*$", re.M)

#: X3b. A HEADING that declares its own section struck or superseded. The
#: corpus uses this where a whole numbered section is withdrawn, e.g.
#: `### 6.1 STRUCK, 2026-08-14 -- "the deviation was roughly halved"`. Only
#: withdrawal verbs; `AMENDED`, `RESTATED`, `CORRECTED` and `UPDATE` head
#: blocks whose text still STANDS, and 17 `**[RESTATED ...]**` banners in this
#: corpus end with the literal sentence "This is not a withdrawal".
_STRUCK_HEAD = re.compile(
    r"^[ \t]*>?[ \t]*(#{1,6})[^\n]*?"
    r"\b(?:STRUCK|Struck|struck|WITHDRAWN|Withdrawn|SUPERSEDED|Superseded"
    r"|RETRACTED|Retracted|FALSIFIED)\b[^\n]*$", re.M)

#: X3c. A whole-document supersession banner in the opening lines, e.g.
#: `> # EVERY PROBABILITY IN THIS DOCUMENT IS SUPERSEDED -- the board it was
#: computed against no longer exists`. Masks the file and says so.
_DOC_BANNER = re.compile(
    r"^[ \t>#*\s]*[^\n]{0,120}?\b(?:IN THIS DOCUMENT|THIS (?:DOCUMENT|FILE|"
    r"PAGE|SECTION|ROUND))\b[^\n]{0,120}?\b(?:IS |ARE )?"
    r"(?:SUPERSEDED|WITHDRAWN|STRUCK|OBSOLETE|RETIRED)\b", re.M)

_HEADING = re.compile(r"^([ \t]*>?[ \t]*)(#{1,6})\s")

#: X4. A figure stated in order to be rejected, or quoted from elsewhere.
_NEGATED = re.compile(
    r"(?:\bnot\b|\brather than\b|\binstead of\b|\bno longer\b|\bnever\b|"
    r"\bwas\b|\bused to\b|\bwould (?:be|have been)\b|\bcarr(?:y|ies|ied)\b|"
    r"\bread(?:s|ing)?\b|\bstated?\b|\bsaid\b|\bquotes?d?\b|\bclaims?\b)"
    r"[^0-9a-zA-Z]{0,4}$")

#: X5. A figure inside INLINE CODE or inside a QUOTATION is a report of what
#: some other surface says, not a claim this document makes. This is not a nicety:
#: `docs/P33_CROSS_SURFACE_SWEEP.md` and `docs/DOCKET.md` exist to enumerate
#: stale figures on other surfaces, and every one of them is backticked or
#: quoted. Without this idiom the check faults the documents that FOUND the
#: defect, which is the fastest way to make it unusable.
_CODE_SPAN = re.compile(r"``[^`\n]*``|`[^`\n]*`")
_FENCE = re.compile(r"^[ \t>]*```.*?^[ \t>]*```", re.M | re.S)
#: Bounded at 300 characters, and NEVER across `<`, `>` or `=`. An early cut
#: matched bare `"` pairs with no such guard and reported 185,549 "quotations"
#: over the corpus -- it was pairing HTML attribute delimiters (`class="..."`)
#: and swallowing whole pages. A mask that over-reaches is a SILENT loss of
#: coverage, which is why the frame now prints the fraction of the corpus this
#: masker blanked rather than only the span count.
_QUOTED = re.compile(
    r"[\"“](?:[^\"“”\n<>=]|\n(?![ \t>]*\n)){1,300}?[\"”]")

#: X6. `~~68%~~ -> **50.2%**` and `68% -> 50.2%`: the left of a correction arrow
#: is the superseded value. Only when both sides are numeric and the right side
#: is the one being asserted.
_ARROW_OLD = re.compile(
    r"(?P<old>[0-9][0-9,]*(?:\.[0-9]+)?)\s*%?\s*(?:→|->|-->)\s*"
    r"\**\s*[0-9]")


def _blank(out, start, end):
    for i in range(start, end):
        if out[i] != "\n":
            out[i] = " "


def _kept_block_end(text: str, lines, li: int) -> int:
    """End offset of the kept-record block opened on line index `li`."""
    head = lines[li]
    in_quote = head.lstrip().startswith(">")
    m = _HEADING.match(head)
    level = len(m.group(2)) if m else 0
    j = li + 1
    while j < len(lines):
        ln = lines[j]
        if in_quote and not ln.lstrip().startswith(">") and ln.strip():
            break
        if level:
            m2 = _HEADING.match(ln)
            if m2 and len(m2.group(2)) <= level:
                break
        j += 1
    return j


def mask_exempt(text: str) -> tuple[str, dict]:
    """Blank out every struck / kept-as-record / quoted region.

    Offsets are preserved (regions become spaces, newlines survive) so every
    line number this check prints is a line number in the file as committed.
    """
    out = list(text)
    counts = {"chars": len(text), "masked": 0, "tilde": 0, "tag": 0, "class": 0, "kept_block": 0,
              "struck_head": 0, "doc_banner": 0, "code": 0, "quoted": 0,
              "arrow": 0}
    for key, rx in (("tilde", _TILDE), ("tag", _TAGS), ("class", _STRIKE_CLASS),
                    ("code", _FENCE), ("code", _CODE_SPAN),
                    ("quoted", _QUOTED)):
        for m in rx.finditer(text):
            counts[key] += 1
            _blank(out, m.start(), m.end())
    for m in _ARROW_OLD.finditer(text):
        counts["arrow"] += 1
        _blank(out, m.start("old"), m.end("old"))

    lines = text.split("\n")
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln) + 1

    # X3c first: a document-level banner in the opening 15 lines masks the file.
    head_end = starts[15] if len(starts) > 15 else len(text)
    b = _DOC_BANNER.search(text[:head_end])
    if b is not None:
        counts["doc_banner"] = 1
        _blank(out, 0, len(text))
        counts["masked"] = sum(1 for a, b in zip(text, out)
                               if a != b and not a.isspace())
        return "".join(out), counts

    for key, rx in (("kept_block", _KEPT_HEAD), ("struck_head", _STRUCK_HEAD)):
        for m in rx.finditer(text):
            li = text.count("\n", 0, m.start())
            end_li = _kept_block_end(text, lines, li)
            counts[key] += 1
            end = starts[end_li] if end_li < len(starts) else len(text)
            _blank(out, m.start(), min(end, len(text)))

    # Finally, blank the BLOCKQUOTE PREFIXES themselves. A claim in this corpus
    # routinely wraps across `> ` lines -- `our margin is` / `> **0.00136...**`
    # is the shape of the flagship finding -- and an anchor that cannot cross a
    # blockquote continuation misses every figure inside a banner. Offsets are
    # preserved, so `\s*` in an anchor now spans the wrap.
    for m in re.finditer(r"^[ \t]*>+[ \t]*", "".join(out), re.M):
        _blank(out, m.start(), m.end())
    counts["masked"] = sum(1 for a, b in zip(text, out)
                           if a != b and not a.isspace())
    return "".join(out), counts


# ---------------------------------------------------------------------------
# The predicates
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Finding:
    rule: str
    path: str
    line: int
    quantity: str
    written: str
    expected: str
    excerpt: str


def _line_of(text: str, off: int) -> int:
    return text.count("\n", 0, off) + 1


#: X4a. A negation anywhere in the 45 characters before the figure, with no
#: sentence break between. `It does not cover 84% of the margin` is the shape,
#: and a 4-character lookbehind (the first cut) missed it because the verb sits
#: in between. Widening can only cause misses, which is the safe direction.
_NEG_NEAR = re.compile(
    r"\b(?:not|never|no longer|rather than|instead of|nor)\b[^.;!?]{0,45}$")

#: X4c. A REPORTING VERB before the figure means the document is narrating what
#: some other surface says, not asserting it. `all four now carry P(rank 1) =
#: 68%`, `which added P(rank 1) = 68%`, `still reads RANK 1 OF 5`. This is the
#: same family as the quotation mask (X5) and it is the idiom in which this lab
#: writes about its own stale figures -- D71 records the trap directly: a docket
#: row that quotes its own false positive files a fresh fault.
_REPORTED = re.compile(
    r"\b(?:carry|carries|carried|carrying|read|reads|reading|state|states|"
    r"stated|say|says|said|quote|quotes|quoted|quoting|added|adds|assert|"
    r"asserts|asserted|claim|claims|claimed|announce|announces|print|prints|"
    r"printed|record|records|recorded|showing|shows|showed|listed|lists)\b"
    r"[^.;!?]{0,55}$")


def _is_rejection(live: str, off: int) -> bool:
    w = live[max(0, off - 70):off]
    return bool(_NEG_NEAR.search(w) or _REPORTED.search(w))


def _is_discrepancy_report(live: str, off: int, q) -> bool:
    """Is the CORRECT value also quoted beside this one?

    `... state the seed bound covers 84% of the margin when against the live
    board the same bound is 177% of it` reports a defect; it does not commit
    one. No document in this corpus asserts both 84% and 177% as the same
    quantity, so a window carrying an admissible basis alongside a
    non-admissible one is a report about the discrepancy. This is the single
    idiom that separates the graders who FOUND the stale figure from the
    documents that CARRY it, and without it every ladder round that names the
    defect faults for naming it (D71 records the same trap one level down: a
    docket row that quotes its own false positive files a fresh fault).
    """
    lo, hi = max(0, off - 200), min(len(live), off + 200)
    for m in _NUM_RE.finditer(live[lo:hi]):
        if lo + m.start() == off:
            continue
        for b in q.bases:
            if written_digits(m.group(0)) <= b.digits and \
                    agrees(m.group(0), b.value):
                return True
    return False


def _excerpt(raw: str, off: int, width: int = 130) -> str:
    lo = raw.rfind("\n", 0, off) + 1
    hi = raw.find("\n", off)
    hi = len(raw) if hi < 0 else hi
    s = raw[lo:hi].strip()
    if len(s) > width:
        k = max(0, off - lo - width // 2)
        s = "..." + s[k:k + width] + "..."
    return s


def scan_r1(live: str, raw: str, path: str, qs, matches: list) -> list:
    faults = []
    for q in qs:
        for rx in q.anchors:
            for m in rx.finditer(live):
                written = m.group("v")
                off = m.start("v")
                if _is_rejection(live, off):
                    continue
                ok, note = q.verdict(written)
                if not ok and _is_discrepancy_report(live, off, q):
                    continue
                rec = (q.qid, path, _line_of(live, off), written, ok, note)
                matches.append(rec)
                if not ok:
                    faults.append(Finding(
                        "R1", path, _line_of(live, off), q.qid, written,
                        note, _excerpt(raw, off)))
    return faults


_OPS = {"/": "/", "÷": "/", "*": "*", "×": "*",
        "+": "+", "-": "-", "−": "-", "–": "-"}
_OPCLASS = r"[/÷*×+\-−–]"
_EXPR = re.compile(
    r"(?P<expr>" + NUM + r"(?:[ \t]*" + _OPCLASS + r"[ \t]*" + NUM + r")+)"
    r"[ \t]*=[ \t]*\**[ \t]*(?P<res>[−-]?" + NUM + r")(?P<pct>[ \t]*%)?")


def _interval(op, vals):
    if op == "+":
        return (sum(v - h for v, h in vals), sum(v + h for v, h in vals))
    if op == "-":
        lo = vals[0][0] - vals[0][1]
        hi = vals[0][0] + vals[0][1]
        for v, h in vals[1:]:
            lo, hi = lo - (v + h), hi - (v - h)
        return lo, hi
    (a, ha), (b, hb) = vals
    if op == "*":
        c = [(a - ha) * (b - hb), (a - ha) * (b + hb),
             (a + ha) * (b - hb), (a + ha) * (b + hb)]
    else:
        if (b - hb) <= 0 <= (b + hb):
            return None
        c = [(a - ha) / (b - hb), (a - ha) / (b + hb),
             (a + ha) / (b - hb), (a + ha) / (b + hb)]
    return min(c), max(c)


def scan_r2(live: str, raw: str, path: str, anchors, checked: list) -> list:
    """Arithmetic, but only where a registered quantity participates.

    `anchors` is the set of registered values. An expression qualifies when one
    of its terms agrees, at that term's own written precision, with a registered
    value. See the module docstring for the measurement that made this
    restriction non-negotiable.
    """
    faults = []
    for m in _EXPR.finditer(live):
        expr, res, pct = m.group("expr"), m.group("res"), m.group("pct")
        pre = live[:m.start()].rstrip(" \t")
        pre = re.sub(r"\*+$", "", pre)
        # `(` is NOT a rejection: a parenthesised computation is the most
        # common form in this corpus -- `(0.002419 / 0.001365 = 1.77)` -- and
        # rejecting it dropped the flagship expression on the first cut.
        if pre[-1:] and (pre[-1] in "+-*/=.^_)×÷−–"
                         or pre[-1].isdigit()):
            continue
        post = live[m.end():].lstrip(" \t")
        if post[:1] and (post[0].isdigit()
                         or post[0] in "+-*/×÷−–."
                         or post.startswith("/")):
            continue
        toks = re.split(r"(" + _OPCLASS + r")", expr)
        nums = [toks[i] for i in range(0, len(toks), 2)]
        ops = {_OPS[toks[i]] for i in range(1, len(toks), 2)}
        if len(ops) != 1:
            continue
        op = ops.pop()
        if op in "/*" and len(nums) != 2:
            continue
        parsed = [parse_written(n) for n in nums]
        if any(p is None for p in parsed):
            continue
        if not any(any(agrees(n, a) and written_digits(n) >= 3
                       for a in anchors) for n in nums):
            continue
        pr = parse_written(res.lstrip("−-"))
        if pr is None:
            continue
        R, hR = pr
        if res[0] in "−-":
            R = -R
        iv = _interval(op, parsed)
        if iv is None:
            continue
        scale = Decimal(100) if pct else Decimal(1)
        lo, hi = iv[0] * scale, iv[1] * scale
        off = m.start()
        checked.append((path, _line_of(live, off), m.group(0)[:80]))
        if not (lo - hR <= R <= hi + hR):
            faults.append(Finding(
                "R2", path, _line_of(live, off), "stated computation", res,
                f"the written operands give [{lo:.10g}, {hi:.10g}]"
                f"{'%' if pct else ''}", _excerpt(raw, off)))
    return faults


#: R3. `covers N% of ... margin` with NO denominator named on the same line is a
#: claim about the current operative margin. With one named, R2 grades it.
_COVERS = re.compile(
    r"covers?\s*\*{0,2}(?P<v>[0-9]{1,3}(?:\.[0-9]+)?)\s*%\*{0,2}"
    r"(?P<tail>[^.\n]{0,60})")
_DENOM_NAMED = re.compile(r"0\.\d{3,}")


def scan_r3(live: str, raw: str, path: str, coverage, matches: list) -> list:
    if coverage is None:
        return []
    faults = []
    for m in _COVERS.finditer(live):
        tail = m.group("tail")
        if "margin" not in tail and "margin" not in \
                live[max(0, m.start() - 90):m.start()]:
            continue
        off = m.start("v")
        if _is_rejection(live, off):
            continue
        if _is_discrepancy_report(live, off, coverage):
            continue
        lo = live.rfind("\n", 0, m.start()) + 1
        hi = live.find("\n", m.end())
        line_text = live[lo:len(live) if hi < 0 else hi]
        if _DENOM_NAMED.search(line_text.replace(m.group("v"), "", 1)):
            continue          # names its own denominator -- R2's ground
        written = m.group("v")
        ok, note = coverage.verdict(written)
        matches.append((coverage.qid + "/R3", path, _line_of(live, off),
                        written, ok, note))
        if not ok:
            faults.append(Finding(
                "R3", path, _line_of(live, off), "coverage of the live margin",
                written + "%", note, _excerpt(raw, off)))
    return faults


# ---------------------------------------------------------------------------
# Controls -- both halves, in memory, on every invocation (lesson L-84)
# ---------------------------------------------------------------------------

CONTROLS = [
    # (name, must_fault, text)
    ("POS-1 withdrawn sentence, unstruck", True,
     "Our 0.002419 seed bound covers 84% of that margin.\n"),
    ("POS-2 margin falsified tenfold", True,
     "our locally scored 0.056647191704213645 sits **0.013658082957863568** "
     "below it\n"),
    ("POS-3 stated computation that no longer divides", True,
     "the ratio is 0.002419121853891026 / 0.0013653082957863563 = 0.8381\n"),
    ("POS-4 seed bound transcribed wrong", True,
     "The seed bound of **0.002439121853891026** is therefore larger.\n"),
    ("NEG-1 the same withdrawn sentence, correctly struck", False,
     "~~Our 0.002419 seed bound covers 84% of that margin.~~ Struck.\n"),
    ("NEG-2 the falsified margin, correctly struck", False,
     "~~our locally scored 0.056647191704213645 sits "
     "**0.013658082957863568** below it~~\n"),
    ("NEG-3 the correct current coverage figure", False,
     "Our 0.002419 seed bound covers 177% of that margin.\n"),
    ("NEG-4 84% inside a kept dated banner", False,
     "> ### THE BANNER AS WRITTEN 2026-08-10, KEPT AS THE RECORD\n"
     "> Like-for-like margin **0.0028863**, against which the 0.002419 seed\n"
     "> bound covers **84%**.\n"),
    ("NEG-5 84% naming its own four-entry denominator", False,
     "the bound of 0.002419 covers 84% (0.002419 / 0.0028863 = 0.838)\n"),
    ("NEG-6 the correct margin at the precision its basis supports", False,
     "our locally scored 0.056647191704213645 sits **0.001365** below it\n"),
    ("NEG-7 a rejected value stated to be rejected", False,
     "the ratio is **177%**, not 84% of the margin\n"),
    ("NEG-8 a correctly transcribed full-precision seed bound", False,
     "The seed bound of **0.002419121853891026** exceeds it.\n"),
    ("NEG-9 a multiline strikethrough spanning the claim", False,
     "~~Our 0.002419 seed bound\ncovers 84% of that margin.~~ Struck 2026.\n"),
]


def run_controls(qs, anchors, coverage) -> tuple[list, list]:
    """Returns (misbehaving control names, one-line results for the frame)."""
    bad, log = [], []
    for name, must_fault, text in CONTROLS:
        live, _ = mask_exempt(text)
        matches, checked = [], []
        f = scan_r1(live, text, "<control>", qs, matches)
        f += scan_r2(live, text, "<control>", anchors, checked)
        f += scan_r3(live, text, "<control>", coverage, matches)
        fired = bool(f)
        ok = fired == must_fault
        if not ok:
            bad.append(name)
        log.append(f"    [{'ok ' if ok else 'BAD'}] "
                   f"{'must fault' if must_fault else 'must NOT fault':<15} "
                   f"fired={str(fired):<5} {name}"
                   + (f"  ({f[0].rule} {f[0].quantity})" if f else ""))
    return bad, log


# ---------------------------------------------------------------------------
# Frame and run
# ---------------------------------------------------------------------------

def tracked_prose(root: Path) -> tuple[list, str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *PROSE_GLOBS],
        capture_output=True, text=True)
    if proc.returncode != 0:
        return [], f"git ls-files failed rc={proc.returncode}: {proc.stderr}"
    return sorted(p for p in proc.stdout.split("\0") if p), proc.stderr.strip()


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="check_derived_figures",
        description="Verify published figures against the machine records they "
                    "are derived from. Reads only unstruck text.")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--verbose", action="store_true",
                    help="print every match, not only the disagreements")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    out = []
    src = read_sources(root)
    qs, problems, facts = build_registry(src)
    anchors = [b.value for q in qs for b in q.bases if q.unit == ""]
    coverage = next((q for q in qs if q.qid == "coverage_pct"), None)

    bad_controls, control_log = run_controls(qs, anchors, coverage)

    files, git_note = tracked_prose(root)
    opened, unreadable, oversize = [], [], []
    faults, matches, checked = [], [], []
    generated = []
    mask_counts = {"chars": 0, "masked": 0,
                   "tilde": 0, "tag": 0, "class": 0, "kept_block": 0,
                   "struck_head": 0, "doc_banner": 0, "code": 0, "quoted": 0,
                   "arrow": 0}

    for rel in files:
        p = root / rel
        if GENERATED_HTML.search(rel):
            generated.append(rel)
            continue
        try:
            data = p.read_bytes()
        except OSError as exc:
            unreadable.append(f"{rel}: {exc}")
            continue
        if len(data) > MAX_BYTES:
            oversize.append(f"{rel} ({len(data) // 1024} KiB)")
            continue
        try:
            raw = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            unreadable.append(f"{rel}: not UTF-8 ({exc.reason})")
            continue
        opened.append(rel)
        live, counts = mask_exempt(raw)
        for k in mask_counts:
            mask_counts[k] += counts[k]
        faults += scan_r1(live, raw, rel, qs, matches)
        faults += scan_r2(live, raw, rel, anchors, checked)
        faults += scan_r3(live, raw, rel, coverage, matches)

    # Two anchors -- and R3 as well -- can all match one sentence. One
    # sentence is one defect; reporting it three times inflates the count a
    # reader acts on.
    seen, deduped = set(), []
    for f in faults:
        k = (f.path, f.line, f.written.rstrip("%"))
        if k in seen:
            continue
        seen.add(k)
        deduped.append(f)
    duplicates = len(faults) - len(deduped)
    faults = deduped

    # ---- verdict -------------------------------------------------------
    reasons = []
    if problems:
        verdict = UNKNOWN
        reasons += [f"source record problem: {p}" for p in problems]
    elif bad_controls:
        verdict = UNKNOWN
        reasons += [f"control misfired: {b}" for b in bad_controls]
    elif not matches and not checked:
        verdict = UNKNOWN
        reasons.append("zero figures matched -- an instrument that examined "
                       "nothing has not cleared anything (defect class B1)")
    elif faults:
        verdict = FAIL
        reasons.append(f"{len(faults)} unstruck figure(s) disagree with the "
                       f"record they are derived from")
    else:
        verdict = PASS
        reasons.append(f"{len(matches)} anchored figure(s) and {len(checked)} "
                       f"stated computation(s) all agree")

    # ---- report --------------------------------------------------------
    out.append("=" * 78)
    out.append("DERIVED-FIGURE CHECK -- published figures against their records")
    out.append("  (docket D88; D85 for why it reads only unstruck text)")
    out.append("=" * 78)
    out.append("")
    out.append("FRAME -- what was looked at, and how it was found")
    out.append(f"  repo                {root}")
    out.append("  enumeration         git ls-files -- " + " ".join(PROSE_GLOBS)
               + "  (NOT the shell's grep: it execs ugrep --ignore-files and")
    out.append("                      honours .gitignore; NOT find: it is bfs "
               "and rejects GNU expressions)")
    out.append(f"  files considered    {len(files)} tracked prose files")
    out.append(f"  files opened        {len(opened)}")
    out.append(f"  not opened          "
               f"{len(oversize) + len(unreadable) + len(generated)}  "
               f"({len(generated)} generated OpenMDAO report HTML under "
               f"*/reports/, {len(oversize)} over")
    out.append(f"                      {MAX_BYTES // 1000} kB, "
               f"{len(unreadable)} unreadable or not UTF-8)")
    for x in oversize[:5]:
        out.append(f"      oversize        {x}")
    for x in unreadable[:5]:
        out.append(f"      unreadable      {x}")
    if git_note:
        out.append(f"  git stderr          {git_note}")
    out.append("  network             none. Every source is a committed "
               "artifact (D55: an audit that needs the")
    out.append("                      network is off whenever the network is)")
    out.append("")

    out.append("SOURCE RECORDS -- read, not imported, not fetched")
    for k, (rel, how) in SOURCES.items():
        r = src[k]
        out.append(f"  [{'ok ' if not r.error else 'ERR'}] {rel}")
        out.append(f"        via {r.how}"
                   + (f"   -- {r.error}" if r.error else ""))
    out.append("")

    out.append("QUANTITIES DERIVED FROM THEM")
    for q in qs:
        out.append(f"  {q.qid:18s} {q.label}")
        for b in q.bases:
            out.append(f"      = {str(b.value)[:26]:26s} "
                       f"({b.digits} sig digits) {b.why}")
    out.append("")

    if P_RANK1_NOT_SHIPPED:
        out.append("MEASURED, PRICED, AND NOT SHIPPED -- an omission a reader "
                   "cannot see is a silent skip")
        for n in P_RANK1_NOT_SHIPPED:
            out.append(f"  {n}")
        out.append("")
    out.append("EXEMPT TEXT -- what was masked before anything was read (D85)")
    out.append(f"  {mask_counts['tilde']:5d}  ~~struck~~ spans "
               f"(blank-line bounded; 69 of these span >1 line corpus-wide)")
    out.append(f"  {mask_counts['tag']:5d}  <s>/<del>/<strike> element bodies")
    out.append(f"  {mask_counts['class']:5d}  elements with a strike/superseded "
               f"class")
    out.append(f"  {mask_counts['kept_block']:5d}  KEPT-AS-THE-RECORD blocks "
               f"(a verbatim historical block carrying no inline marker)")
    out.append(f"  {mask_counts['struck_head']:5d}  sections whose own heading "
               f"declares them struck/withdrawn/superseded")
    out.append(f"  {mask_counts['doc_banner']:5d}  whole files under a "
               f"document-level supersession banner")
    out.append(f"  {mask_counts['code']:5d}  inline-code spans and fenced "
               f"blocks, and {mask_counts['quoted']} quotations -- a figure")
    out.append("         inside either is a report of what another surface "
               "says, not a claim (D71's trap)")
    out.append(f"  {mask_counts['arrow']:5d}  values on the left of a "
               f"`old -> new` correction arrow")
    pct = (100.0 * mask_counts["masked"] / mask_counts["chars"]
           if mask_counts["chars"] else 0.0)
    out.append(f"  MASKED IN TOTAL: {mask_counts['masked']:,} of "
               f"{mask_counts['chars']:,} non-space characters ({pct:.1f}%). "
               f"This is the")
    out.append("  coverage this check gave up in order not to fault a "
               "correctly struck figure, and it is")
    out.append("  printed because a masker that over-reaches loses coverage "
               "SILENTLY.")
    out.append("  A **STRUCK <date>** / **CORRECTED <date>** note is NOT masked:"
               " it is the live corrected")
    out.append("  text. The sentence it withdraws carries its own ~~ and is "
               "masked by that.")
    out.append("")

    out.append("CONTROLS -- both halves, in memory, on this invocation (L-84)")
    out += control_log
    out.append("")

    out.append("WHAT WAS EXAMINED")
    out.append(f"  {len(matches):5d}  anchored figure quotations matched "
               f"(R1 + R3)")
    out.append(f"  {len(checked):5d}  stated computations involving a "
               f"registered quantity (R2)")
    if args.verbose:
        for qid, path, line, written, ok, note in matches:
            out.append(f"      [{'ok ' if ok else 'FAIL'}] {path}:{line}  "
                       f"{qid} = {written}")
        for path, line, txt in checked:
            out.append(f"      [arith] {path}:{line}  {txt}")
    out.append("")

    if faults:
        out.append("DISAGREEMENTS")
        for f in faults:
            out.append(f"  [FAIL] {f.path}:{f.line}  ({f.rule} {f.quantity})")
            out.append(f"         written   {f.written}")
            out.append(f"         record    {f.expected}")
            out.append(f"         line      {f.excerpt}")
        out.append("")

    out.append("BLIND TO -- read this before reading the verdict")
    out.append("  1. A figure correct to the digits written but derived from a "
               "stale referent that")
    out.append("     rounds the same way. 84% of a four-entry margin and any "
               "other 84% are one string.")
    out.append("  2. An error below half an ulp of the last digit written. "
               "Quoting coarsely is a way to")
    out.append("     be unfalsifiable here; the written precision of every "
               "match is printed under --verbose.")
    out.append("  3. Arithmetic that names no registered quantity. Measured: "
               "an unanchored corpus-wide")
    out.append("     sweep checked 69 expressions and disagreed with 8, all "
               "8 false on inspection.")
    out.append("  4. A claim that should have been made and was not. This "
               "grades figures that are PRESENT.")
    out.append("  5. Any figure whose anchor phrase is not in the registry. "
               "The registry is the coverage")
    out.append("     statement and it is printed above; a headline figure "
               "absent from it is unchecked.")
    out.append("  6. Struck text, by construction and on purpose. A masked "
               "region is never graded.")
    out.append("  7. Whether a source record is itself right. It grades "
               "agreement with the record.")
    out.append("")
    out.append("=" * 78)
    out.append(f"VERDICT: {verdict}")
    for r in reasons:
        out.append(f"  {r}")
    out.append("=" * 78)

    if args.json:
        print(json.dumps({
            "verdict": verdict,
            "reasons": reasons,
            "frame": {"considered": len(files), "opened": len(opened),
                      "generated_html_skipped": len(generated),
                      "oversize": oversize, "unreadable": unreadable,
                      "masked": mask_counts},
            "sources": {k: {"path": r.path, "how": r.how, "error": r.error}
                        for k, r in src.items()},
            "quantities": {q.qid: [str(b.value) for b in q.bases] for q in qs},
            "controls_bad": bad_controls,
            "matched": len(matches), "computations": len(checked),
            "faults": [dataclasses.asdict(f) for f in faults],
        }, indent=1))
    else:
        print("\n".join(out))
    return EXIT[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
