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

Exit 0 = clean.  Exit 2 = a thermal result reached a screen, a banned phrase
reached a screen, a figure is not latexified, or a control failed.
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

SHEET = os.path.join(HERE, "ACT_C_GATE_sheet.pdf")
FIGDIR = os.path.join(HERE, "figures_actC_gate")

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


NUMERIC_RULES = [
    dict(id="ABS-TEMP", fn=rule_abs_temp,
         why="a decimal in the absolute-temperature band is a thermal result",
         plants=["the hottest point sits at 298.873 on the last frame",
                 "the module starts from 293.0 everywhere"],
         negatives=["the mesh carries 16,608 cells",
                    "the flow Courant number is near 1600",
                    "the difference is 0.0232 at the pulse edge",
                    "the run costs 26.4 min of wall time"]),
    dict(id="KELVIN-UNIT", fn=rule_kelvin_unit,
         why="a kelvin quantity at or above %.1f K is a thermal result, not a "
             "convergence difference" % KELVIN_MAX,
         plants=["the rise at the end of the pulse is 2.384 K",
                 "the adiabatic bound over the run is 10.8 K"],
         negatives=["the two arms agree to 0.0232 K at the pulse edge",
                    "the limit is 0.0123 K",
                    "all values in K"]),
    dict(id="CELSIUS", fn=rule_celsius,
         why="nothing admissible on these screens is quoted in Celsius",
         plants=["the module rises 5.9 °C over the pulse",
                 "peak 25.9 degC at the downstream end"],
         negatives=["the coolant outlet parts from its twin inside the pulse",
                    "0.0232 K against a 0.0123 K limit"]),
    dict(id="THERMAL-CLAIM", fn=rule_claim,
         why="asserts a thermal outcome",
         plants=[p for _, p in CLAIM_ALTS],
         negatives=["withheld: cell temperatures; the temperature rise; the "
                    "coolant outlet temperature; the energy ledger",
                    "the gate refuses it and no thermal result exists"]),
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
          "on its own plant\n" % n_alt)

    targets = [SHEET]
    if os.path.isdir(FIGDIR):
        targets += [os.path.join(FIGDIR, f) for f in sorted(os.listdir(FIGDIR))
                    if f.endswith(".pdf")]
    missing = [t for t in targets if not os.path.exists(t)]
    if missing:
        sys.stderr.write("REFUSE: not built: %s\n"
                         % [os.path.basename(m) for m in missing])
        return 2

    bad = 0
    per_rule = {r["id"]: 0 for r in NUMERIC_RULES}
    per_rule["LANGUAGE"] = 0
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
            for phrase, _pos in rule["fn"](text):
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
    print("hits per rule: %s" % ", ".join("%s %d" % (k, v)
                                          for k, v in sorted(per_rule.items())))
    print("(a rule at 0 has been PROVED able to fire by its own plant above; "
          "the zero is a measurement, not an absence of coverage)")
    if bad:
        raise SystemExit(2)
    print("PASS -- no thermal result and no banned phrase reaches an Act C "
          "gate screen, and every artifact went through LaTeX")
    return 0


if __name__ == "__main__":
    sys.exit(main())
