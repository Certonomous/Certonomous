#!/usr/bin/env python3
"""Refuse unless the Act C GATE screens keep every thermal result off the page.

WHAT THIS ADDS THAT NOTHING ELSE CHECKS.  `check_demo_language.py` guards the
lab's language rules and this file REUSES its rules rather than copying them --
imported, so there is exactly one definition of a banned phrase in the tree.
What no committed guard checks is the boundary this act turns on:

  ADMISSIBLE -- a DIFFERENCE BETWEEN TWO ARMS differing only in outer-sweep
    count.  `0.0232 K` says the answer still moves when an arbitrary iteration
    count is doubled.  It is a statement about the METHOD.

  WITHHELD -- anything that tells a viewer how hot the module got: a cell
    temperature, a rise, the outlet temperature, the acceptance criteria, the
    energy ledger, and the adiabatic bounds, which would disclose the scale of
    the answer by the back door.

THE MECHANICAL FORM OF THE BOUNDARY.  Judging that distinction sentence by
sentence is exactly the kind of care that fails at 6 a.m., so it is reduced to
arithmetic:

  * an ABSOLUTE temperature in kelvin is a decimal in roughly [200, 500];
  * a temperature RISE worth withholding is of order 0.1 K and up;
  * every admissible convergence difference on these screens lies between
    5.2e-04 and 2.4e-02 K, and the two limits are 1.234e-03 and 1.234e-02 K.

Two orders of magnitude separate the two sets, so the rule is decidable by
reading a number rather than by judging a sentence.

CONTROLS, BOTH DIRECTIONS, PER ALTERNATIVE.  Following `check_demo_language`'s
L-425 discipline: every alternative carries its OWN hand-written plant, and the
plants are written INDEPENDENTLY of the patterns -- deriving a plant from its
own pattern reproduces any typo in both and the mutation survives its own fix.
A control derived from the thing it controls is not a control.

Each numeric rule also carries a NEGATIVE arm: a sentence it must NOT fire on.
A rule that fires on everything is as useless as one that fires on nothing, and
only the negative arm separates them.

AND THE COVERAGE ASSERTION, WHICH IS THE PLANTED-ZERO GUARD.  If `pdftotext`
returns a stub, every numeric rule finds nothing and the sweep runs green
having read no numbers at all.  So the sweep asserts it parsed at least
MIN_TOKENS numeric tokens from the sheet, and reports the per-rule hit count so
that a rule with zero live matches is VISIBLE rather than assumed harmless.

WHY THIS IS NOT BELT-AND-BRACES.  Driven end to end by mutation: a scratch copy
of the sheet carrying *"Peak cell temperature is 298.873 K, a rise of 5.873 K"*
was compiled, and **`pdflatex` RETURNED 0 AND REPORTED SUCCESS**.  The toolchain
is perfectly happy to render a banned thermal result onto a filmed surface.
**Only this guard stands between the lab and that.**  Two independent rules
caught the plant; the committed sheet scores zero on all four.

CANDIDATES, NOT ONLY HITS.  A rule reporting zero hits can mean two different
things -- *it examined candidates and none was bad*, or *it had nothing to
examine*.  Those are not the same evidence and the report must not blur them,
so every numeric rule also reports HOW MANY CANDIDATES IT EXAMINED.  On this
sheet ABS-TEMP carries the live coverage (it inspects every decimal on the
page); KELVIN-UNIT examines zero, because the sheet puts its unit in the column
header rather than beside each number.  KELVIN-UNIT's zero is therefore
"nothing to look at here", and it is printed as such.  Its plant proves it can
fire when there IS something to look at, which is what keeps it honest coverage
against a later edit rather than decoration.

Exit 0 = clean.  Exit 2 = a thermal result reached a screen, a banned phrase
reached a screen, a figure is not latexified, or a control failed.

==========================================================================
AMENDMENT 1 -- 2026-09-01.  THE WITHHOLDING IS RE-SCOPED, AS A RECORDED
POLICY CHANGE.  Authority: Sanaa, "battery: approved.", captured verbatim at
`etc/sessions/2026-09-01T2010Z_sanaa_battery_approved.md`, commit `0fe482c4`;
and her demo shooting protocol at `cfcf766f`, whose battery beat is "the run
completes, the gate refuses it, the platform says so and schedules the
corrected run. The feature is the refusal."
==========================================================================

THE BEHAVIOUR THIS AMENDMENT REPLACES, STATED AND STRUCK RATHER THAN
REWRITTEN, so a reader who finds the two knows which is current and why:

    ~~Every decimal in [200, 500] and every kelvin quantity at or above
    0.1 K is a thermal result and is refused, unconditionally, on every Act C
    surface.~~

WHAT IT BECOMES.  The bands are UNCHANGED and every value in them is still
refused, with ONE exception: a numeric token that matches a value the
corrected run ACTUALLY GRADED, to the token's own printed precision.  That set
is DERIVED from the corrected run's committed graded artefact by
`actC_graded_admission.py`; it is never written here and never written by hand.

WHY NOT SIMPLY A WIDER BAND, which is what "admit T25R4's numbers" sounds like
it means.  A widened band admits EVERY value inside it -- a number nobody
graded, a number typed into a sheet, and the adiabatic bounds this guard has
withheld since it was written.  A band cannot tell a graded value from a
plausible one.  An allowlist can, and one derived from the artefact cannot be
quietly widened by an author, because widening it would mean editing a graded
result.

THE PROPERTY THAT MAKES THIS SELF-ENFORCING, AND IT IS WHY THE DESIGN IS THIS
DESIGN.  If the corrected run has not graded, the derived set is EMPTY, and
this guard's behaviour is BIT-IDENTICAL to its behaviour before the amendment:
every temperature refused, no exception reachable.  Sanaa's own battery beat is
that refusal, and her screen 8 permits exactly two endings -- the convergence
study shown done, or shown automatically underway.  So the instrument does not
merely PERMIT the fallback ending; while the corrected run is ungraded IT
ENFORCES IT.  Nobody has to remember.  The fallback is the DEFAULT and the
reporting ending is the exception a graded artefact has to earn.

WHAT THE AMENDMENT DOES NOT TOUCH:
  * the adiabatic bounds (2.400 / 10.800 / 10.7950 K) stay refused
    UNCONDITIONALLY -- they are analytic consequences of the registered heat
    input, not outputs of any solve, and no allowlist reaches them;
  * Celsius stays banned outright;
  * the eight thermal-claim phrases stay banned outright.  The approval put to
    Sanaa was about T25R4's NUMBERS; widening the phrase ban is a separate
    policy question and is not taken here;
  * every existing control keeps driving the RAW rules, unfiltered, so a live
    allowlist can never make a control arm look dead.

ADDED IN THE SAME AMENDMENT -- BARRED-FIGURE.  The content specification's
section 0 records that nothing mechanical stopped the five figures of the
barred 0.4 K run reaching a screen; only a written rule did.  A written rule is
not an instrument, so the sweep now refuses if any of those five files appears
in a swept directory.  A barred run's figure is barred by provenance and no
numeric test recovers that.

LINE-CITATION NOTE.  The Act C content specification cites this file's target
list "at lines 263-266".  This amendment inserts code above it and that
citation is superseded; the target list is now built in `sweep_targets()` and
the specification is re-cited in the same commit.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_demo_language as LANG                              # noqa: E402
sys.path.insert(0, os.path.abspath(
    os.path.join(HERE, "..", "..", "..", "..", "scripts")))
import check_thermal_latexified as TEX                          # noqa: E402
import actC_graded_admission as ADMIT                           # noqa: E402

SHEET = os.path.join(HERE, "ACT_C_GATE_sheet.pdf")
FIGDIR = os.path.join(HERE, "figures_actC_gate")

#: The only two rules an allowlist may reach.  CELSIUS and THERMAL-CLAIM are
#: absent deliberately: the approval was about numbers, and a phrase is not a
#: number.  Naming the set here rather than testing rule ids inline means a
#: rule added later is NOT allowlisted by default, which is the safe direction.
ALLOWLISTED_RULES = frozenset({"ABS-TEMP", "KELVIN-UNIT"})

#: A hit's numeric token.  ABS-TEMP returns the bare decimal; KELVIN-UNIT
#: returns it with its unit attached, and the unit is not part of the value.
_LEADING_NUMBER = re.compile(r"^-?\d[\d,]*(?:\.\d+)?")


def hit_token(phrase):
    m = _LEADING_NUMBER.match(str(phrase).strip())
    return m.group(0) if m else ""

# Below this, a kelvin quantity is a convergence difference; at or above it, it
# is a thermal result.  The nearest admissible value is 2.4e-02 and the nearest
# withheld one is of order 1, so the line sits in a two-order gap.
KELVIN_MAX = 0.1
# An absolute temperature in kelvin, as a decimal.
ABS_LO, ABS_HI = 200.0, 500.0
MIN_TOKENS = 20


def _num(s):
    """Parse a rendered numeric token.  `,` is a THOUSANDS separator here, not
    a decimal point -- reading `16,608` as `16.608` would drop it straight into
    the absolute-temperature band and the rule would fire on a cell count."""
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def cand_abs_temp(text):
    return len(re.findall(r"(?<![\d.])\d{1,3}(?:,\d{3})*\.\d+(?![\d])", text))


def cand_kelvin_unit(text):
    return len(re.findall(
        r"(?<![\d.])\d+(?:,\d{3})*(?:\.\d+)?\s?K\b", text))


def cand_celsius(text):
    return len(re.findall(r"(?i)(°\s?C\b|\bdeg\s?C\b|\bcelsius\b)", text))


def cand_claim(text):
    return len(CLAIM_RE.findall(text))


def rule_abs_temp(text):
    """A decimal number in the absolute-temperature band."""
    hits = []
    for m in re.finditer(r"(?<![\d.])(\d{1,3}(?:,\d{3})*\.\d+)(?![\d])", text):
        v = _num(m.group(1))
        if v is not None and ABS_LO <= v <= ABS_HI:
            hits.append((m.group(1), m.start()))
    return hits


def rule_kelvin_unit(text):
    """A number carrying a kelvin unit whose magnitude is a thermal result."""
    hits = []
    for m in re.finditer(r"(?<![\d.])(\d+(?:,\d{3})*(?:\.\d+)?)\s?K\b", text):
        v = _num(m.group(1))
        if v is not None and abs(v) >= KELVIN_MAX:
            hits.append((m.group(0), m.start()))
    return hits


def rule_celsius(text):
    """Any Celsius at all.  Nothing admissible on these screens needs it."""
    return [(m.group(0), m.start()) for m in
            re.finditer(r"(?i)(°\s?C\b|\bdeg\s?C\b|\bcelsius\b)", text)]


# Phrases that ASSERT a thermal outcome.  Each is chosen so that it cannot
# occur in the sheet's own WITHHELD list, which legitimately names the
# quantities without disclosing a value ("the temperature rise;" is a name, not
# a claim, and is not banned here).
CLAIM_ALTS = [
    ("peak temperature is", "the peak temperature is 298.9"),
    ("peak temperature of", "a peak temperature of 299 across the pack"),
    ("hottest cell", "the hottest cell sits at the downstream end"),
    ("rises by", "the module rises by 5.9 over the pulse"),
    ("warms to", "the outlet warms to 295.1 by the end"),
    ("reaches a peak", "the pack reaches a peak at 465 s"),
    ("energy balance closes", "the energy balance closes to 0.4 per cent"),
    ("runs hotter", "the downstream end runs hotter than the inlet end"),
]
CLAIM_RE = re.compile(
    r"(?i)\b(peak temperature is|peak temperature of|hottest cell|rises by|"
    r"warms to|reaches a peak|energy balance closes|runs hotter)\b")


def rule_claim(text):
    return [(m.group(0), m.start()) for m in CLAIM_RE.finditer(text)]


# --------------------------------------------------------------------------
# AMENDMENT 2 -- 2026-09-01.  PROCESS-WORD, and the defect that earned it.
#
# Sanaa's demo shooting protocol (2026-09-01 ~20:30Z, `cfcf766f`) extends the
# never-list with process vocabulary: "prior runs, replay, agreements, paths,
# ids, tiers".  MEASURED THE SAME DAY: all three Act C gate figures carried the
# word "Agreement" in their RENDERED in-figure titles, and the sheet carried it
# in a table row -- six occurrences in the sheet and five across the figures.
#
# WHY NOTHING CAUGHT IT, AND THIS IS THE GENERAL LESSON.  The contract's
# `Figure.__post_init__` checks the title an act DECLARES.  The offending
# string was matplotlib text rendered INSIDE the PDF, which that check cannot
# see -- the same blindness the content specification's section 6.3 recorded
# for over-length in-figure titles.  A declaration check is not a rendering
# check, and only reading the rendered artifact found this.
#
# WHY THE RULE LIVES HERE AND NOT IN THE SHARED LANGUAGE CHECKER.  Adding a
# banned phrase to `check_demo_language` would apply it to Act A's surfaces
# too, and turning another act's screens red is a policy call above this lane.
# MEASURED before adding: all five words below occur ZERO times across the four
# Act C artifacts, so this rule turns nothing red today -- it stops the defect
# recurring.  Extending it to the shared checker is recommended, not taken.
#
# The word is banned; the MEANING is not. "difference", "differ" and "settling"
# all say what these screens say, and the figures were regenerated to use them.
# --------------------------------------------------------------------------
PROCESS_ALTS = [
    ("agreement", "the two arms are drawn against their agreement limit"),
    ("agreements", "both agreements sit inside the band"),
    ("prior run", "the prior run is drawn beside this one"),
    ("prior runs", "prior runs are shown for context"),
    ("tier", "this result is reported at the second tier"),
]
PROCESS_RE = re.compile(r"(?i)\b(agreements?|prior\s+runs?|tiers?)\b")


def cand_process(text):
    return len(PROCESS_RE.findall(text))


def rule_process(text):
    return [(m.group(0), m.start()) for m in PROCESS_RE.finditer(text)]


NUMERIC_RULES = [
    dict(id="ABS-TEMP", cand=cand_abs_temp, fn=rule_abs_temp,
         why="a decimal in the absolute-temperature band is a thermal result",
         plants=["the hottest point sits at 298.873 on the last frame",
                 "the module starts from 293.0 everywhere"],
         negatives=["the mesh carries 16,608 cells",
                    "the flow Courant number is near 1600",
                    "the difference is 0.0232 at the pulse edge",
                    "the run costs 26.4 min of wall time"]),
    dict(id="KELVIN-UNIT", cand=cand_kelvin_unit, fn=rule_kelvin_unit,
         why="a kelvin quantity at or above %.1f K is a thermal result, not a "
             "convergence difference" % KELVIN_MAX,
         plants=["the rise at the end of the pulse is 2.384 K",
                 "the adiabatic bound over the run is 10.8 K"],
         negatives=["the two arms agree to 0.0232 K at the pulse edge",
                    "the limit is 0.0123 K",
                    "all values in K"]),
    dict(id="CELSIUS", cand=cand_celsius, fn=rule_celsius,
         why="nothing admissible on these screens is quoted in Celsius",
         plants=["the module rises 5.9 °C over the pulse",
                 "peak 25.9 degC at the downstream end"],
         negatives=["the coolant outlet parts from its twin inside the pulse",
                    "0.0232 K against a 0.0123 K limit"]),
    dict(id="THERMAL-CLAIM", cand=cand_claim, fn=rule_claim,
         why="asserts a thermal outcome",
         plants=[p for _, p in CLAIM_ALTS],
         negatives=["withheld: cell temperatures; the temperature rise; the "
                    "coolant outlet temperature; the energy ledger",
                    "the gate refuses it and no thermal result exists"]),
    dict(id="PROCESS-WORD", cand=cand_process, fn=rule_process,
         why="process vocabulary from the 2026-09-01 never-list; say the "
             "quantity instead",
         plants=[p for _, p in PROCESS_ALTS],
         negatives=["the difference between 10 and 20 sweeps, K",
                    "how far the two arms differ over the run",
                    "each check against its limit",
                    "the answer is still settling at the pulse edge"]),
]


def control():
    """Drive every rule to fire on its own plants and to stay silent on its own
    negatives.  Both arms, per alternative."""
    dead, loud = [], []
    n_pos = n_neg = 0
    for rule in NUMERIC_RULES:
        for plant in rule["plants"]:
            n_pos += 1
            if not rule["fn"](plant):
                dead.append((rule["id"], plant))
        for neg in rule["negatives"]:
            n_neg += 1
            if rule["fn"](neg):
                loud.append((rule["id"], neg, rule["fn"](neg)))
    # Every CLAIM alternative individually, per the L-425 discipline: a live
    # alternative would otherwise mask a dead one behind the rule's own plant.
    for alt, plant in CLAIM_ALTS:
        n_pos += 1
        if not CLAIM_RE.search(plant):
            dead.append(("THERMAL-CLAIM/" + alt, plant))
    # Same discipline for PROCESS-WORD (Amendment 2): a live alternative would
    # otherwise mask a dead one behind the rule's own plant.
    for alt, plant in PROCESS_ALTS:
        n_pos += 1
        if not PROCESS_RE.search(plant):
            dead.append(("PROCESS-WORD/" + alt, plant))
    if dead:
        sys.stderr.write(
            "REFUSE: %d control arm(s) never fire on their own plant. A rule "
            "that cannot catch its own plant catches nothing on a real screen "
            "either, and this sweep would run green.\n" % len(dead))
        for rid, plant in dead:
            sys.stderr.write("  %-24s plant %r\n" % (rid, plant))
        raise SystemExit(2)
    if loud:
        sys.stderr.write(
            "REFUSE: %d control arm(s) fire on a sentence that must stay "
            "clean. A rule that fires on everything is as useless as one that "
            "fires on nothing.\n" % len(loud))
        for rid, neg, hits in loud:
            sys.stderr.write("  %-24s negative %r -> %r\n" % (rid, neg, hits))
        raise SystemExit(2)
    return n_pos, n_neg


def allowlist_control():
    """Drive the amendment BOTH WAYS, and refuse unless both arms hold.

    A loosening that has not been shown to still refuse is not a guard, so this
    runs on every invocation rather than living in a separate selftest nobody
    runs before a shoot.  It is pure arithmetic over hand-written strings and
    touches no artifact.

    ARM 1 -- THE EMPTY SET.  With nothing graded, every one of the raw rules'
    own thermal plants must still be refused.  This is the arm that proves the
    amendment's central claim: no grading, no change in behaviour.

    ARM 2 -- A PLANTED GRADED SET.  With two values planted, exactly those two
    must be admitted, and a neighbour that was NOT graded must still be
    refused.  The plants here are written INDEPENDENTLY of the ones in
    `actC_graded_admission`, per the L-425 discipline: a control derived from
    the thing it controls reproduces its typos and survives its own bugs.
    """
    dead, loud = [], []

    # ARM 1 -- empty.
    for token in ("298.873", "293.000", "376.7578", "2.384", "10.8", "0.420"):
        if ADMIT.token_admissible(token, ()):
            loud.append(("EMPTY-SET", token))

    # ARM 2 -- planted.  Values chosen by hand, not lifted from the module.
    planted = (301.4409, 0.2537)
    for token in ("301.4409", "301.441", "301.4", "0.2537", "0.254"):
        if not ADMIT.token_admissible(token, planted):
            dead.append(("PLANTED", token))
    for token in ("301.5409", "301.3", "302.4409", "0.3537", "0.26",
                  "293.0", "298.873"):
        if ADMIT.token_admissible(token, planted):
            loud.append(("PLANTED-NEIGHBOUR", token))

    # ARM 3 -- the barred set, reachable by no allowlist.
    for token in ("2.400", "2.4", "10.800", "10.8", "10.7950"):
        if ADMIT.token_admissible(token, (2.400, 10.800, 10.7950, 301.4409)):
            loud.append(("BARRED", token))

    # ARM 4 -- an integer kelvin token carries too little precision to match.
    if ADMIT.token_admissible("301", planted):
        loud.append(("INTEGER", "301"))

    if dead:
        sys.stderr.write(
            "REFUSE: %d allowlist arm(s) refuse a value that WAS graded. The "
            "amendment cannot admit its own plant, so it would refuse a real "
            "result on camera.\n" % len(dead))
        for rid, tok in dead:
            sys.stderr.write("  %-20s %r\n" % (rid, tok))
        raise SystemExit(2)
    if loud:
        sys.stderr.write(
            "REFUSE: %d allowlist arm(s) admit a value that was NOT graded. A "
            "loosening not shown to still refuse is not a guard.\n" % len(loud))
        for rid, tok in loud:
            sys.stderr.write("  %-20s %r\n" % (rid, tok))
        raise SystemExit(2)
    return 6, 12


def sweep_targets():
    """Every surface this sweep covers.

    The sheet plus every PDF in the gate figure directory.  A surface placed
    anywhere else is invisible here -- that is the coverage boundary and it is
    stated in the content specification rather than left to be discovered.
    """
    targets = [SHEET]
    if os.path.isdir(FIGDIR):
        targets += [os.path.join(FIGDIR, f) for f in sorted(os.listdir(FIGDIR))
                    if f.endswith(".pdf")]
    return targets


def barred_figures_present():
    """The five figures of the barred run, if any reached a swept directory.

    Barred by PROVENANCE, not by content: they are the run the owner ruled off
    screen, and no numeric test recovers that fact from the pixels.  Refusing
    the FILE is the only mechanical form the rule has.
    """
    found = []
    for directory in (HERE, FIGDIR):
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if name in ADMIT.BARRED_FIGURE_BASENAMES:
                found.append(os.path.join(directory, name))
    return found


def latexified(path):
    """Classify with the COMMITTED reader, not a local copy.

    `check_thermal_latexified.classify` is the lab's definition of "this went
    through LaTeX", and it carries its own planted control -- it renders a
    figure with usetex OFF and refuses unless that figure is read back as NOT
    LATEXIFIED.  Importing it means this act is judged by the same reader as
    every other screen, and it inherits that negative arm rather than
    asserting a positive one on its own authority."""
    fonts = TEX.pdf_fonts(path)
    verdict = TEX.classify(fonts)
    return verdict == "LATEXIFIED", (fonts or []), verdict


def main():
    # The committed latexified reader must prove it can see a NON-latexified
    # figure before any pass of it is worth anything.
    print("latexified reader planted control: a usetex-OFF figure is read "
          "back as %r" % TEX.planted_control())
    n_pos, n_neg = control()
    print("thermal-withholding control: %d positive arms fire on their own "
          "plants, %d negative arms stay silent" % (n_pos, n_neg))
    n_alt = LANG.control()
    print("language control (reused, not copied): %d alternatives, each fires "
          "on its own plant" % n_alt)
    n_adm, n_ref = allowlist_control()
    print("allowlist control (Amendment 1, both directions): %d planted graded "
          "values admitted, %d non-graded values still refused" % (n_adm, n_ref))

    # THE ADMISSIBILITY SOURCE, PRINTED EVERY RUN.  A reader must never have to
    # infer which regime this sweep ran in from a hit count.
    try:
        admissible, note = ADMIT.derive()
    except ADMIT.AdmissionRefused as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return 2
    print("admissibility source: %s" % note)
    if not admissible:
        print("  -> the derived set is EMPTY, so every temperature is refused "
              "and this sweep is bit-identical to the sweep before Amendment "
              "1. The convergence-study ending is what plays.\n")
    else:
        print("  -> %d value(s) admitted, and only at their own printed "
              "precision. Everything else in the bands still refuses.\n"
              % len(admissible))

    barred = barred_figures_present()
    if barred:
        sys.stderr.write(
            "REFUSE: %d figure(s) of the barred run are sitting in a swept "
            "directory: %s. They are barred by provenance and no formatting "
            "fix cures that.\n"
            % (len(barred), [os.path.basename(b) for b in barred]))
        return 2

    targets = sweep_targets()
    missing = [t for t in targets if not os.path.exists(t)]
    if missing:
        sys.stderr.write("REFUSE: not built: %s\n"
                         % [os.path.basename(m) for m in missing])
        return 2

    bad = 0
    per_rule = {r["id"]: 0 for r in NUMERIC_RULES}
    per_cand = {r["id"]: 0 for r in NUMERIC_RULES}
    per_rule["LANGUAGE"] = 0
    per_admitted = {r["id"]: 0 for r in NUMERIC_RULES}
    tokens_seen = 0

    for path in targets:
        name = os.path.basename(path)
        text = LANG.pdftotext(path)
        if text is None:
            print("UNREADABLE   %s" % name)
            bad += 1
            continue
        toks = re.findall(r"(?<![\d.])\d+(?:,\d{3})*(?:\.\d+)?", text)
        tokens_seen += len(toks)

        hits = []
        for rule in NUMERIC_RULES:
            per_cand[rule["id"]] += rule["cand"](text)
            for phrase, _pos in rule["fn"](text):
                # AMENDMENT 1.  The RAW rule is unchanged and still fires on
                # everything it ever fired on; the only thing that has changed
                # is that a hit whose token matches a GRADED value is released
                # rather than refused. With an empty derived set this branch is
                # never taken and the loop is what it was.
                if (rule["id"] in ALLOWLISTED_RULES
                        and ADMIT.token_admissible(hit_token(phrase),
                                                   admissible)):
                    per_admitted[rule["id"]] += 1
                    continue
                per_rule[rule["id"]] += 1
                hits.append((rule["id"], phrase, rule["why"]))
        for rule in LANG.RULES:
            for m in rule["pattern"].finditer(text):
                per_rule["LANGUAGE"] += 1
                hits.append((rule["id"], m.group(0), rule["why"]))

        ok, fonts, verdict = latexified(path)
        if not ok:
            bad += 1
            print("%-14s %s -- embedded fonts %s" % (verdict, name, fonts))

        if hits:
            bad += 1
            print("WITHHELD BREACH %s" % name)
            for rid, phrase, why in hits:
                print("   [%s] %r  -- %s" % (rid, phrase, why))
        elif ok:
            print("clean        %-32s %d numeric tokens, fonts %s"
                  % (name, len(toks), fonts[0] if fonts else "none"))

    # THE PLANTED-ZERO GUARD.  A sweep that read no numbers found no thermal
    # result for a reason that has nothing to do with the screens.
    if tokens_seen < MIN_TOKENS:
        sys.stderr.write(
            "REFUSE: the numeric sweep parsed only %d token(s) across %d "
            "artifact(s), below the %d it must see. A zero from a reader that "
            "read nothing is not evidence that nothing is there.\n"
            % (tokens_seen, len(targets), MIN_TOKENS))
        return 2

    print("\n%d artifacts checked, %d numeric tokens read" % (len(targets),
                                                              tokens_seen))
    print("per rule -- hits / candidates examined:")
    for rid in sorted(per_cand):
        note = ("  <-- NOTHING TO LOOK AT on these artifacts; its plant above "
                "proves it fires when there is" if per_cand[rid] == 0 else "")
        released = ("  <-- %d token(s) RELEASED by the graded allowlist"
                    % per_admitted[rid] if per_admitted.get(rid) else "")
        print("   %-14s %d hit(s) / %d candidate(s)%s%s"
              % (rid, per_rule[rid], per_cand[rid], note, released))
    print("   %-14s %d hit(s)" % ("LANGUAGE", per_rule["LANGUAGE"]))
    print("(a rule reporting 0 hits over 0 candidates has SEEN NOTHING, which "
          "is different evidence from 0 hits over many, and is printed as "
          "such rather than blurred into one clean line)")
    if bad:
        raise SystemExit(2)
    print("PASS -- no thermal result and no banned phrase reaches an Act C "
          "gate screen, and every artifact went through LaTeX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
