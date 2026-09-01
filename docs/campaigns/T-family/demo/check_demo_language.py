#!/usr/bin/env python3
"""Refuse unless the Act A and Act C screens obey Sanaa's language rules.

The surface this reads is the RENDERED one -- the text layer of the compiled
sheet PDFs and of every figure PDF -- because that is what a viewer sees.  A
rule checked against source strings can pass while the screen says something
else.

Rules encoded, from the directives themselves:
  * 2026-09-01 04:20Z -- "no internal information, no past tense, no long
    sentences, ... NOTHING that makes it look recorded".
  * 2026-09-01 03:10Z -- "Solver: none" never on a results screen; remove
    "recorded", "replayed", "re-displayed", "screens come from", "source case".
  * 2026-09-01 03:40Z -- DEMO MODE never-list: "already finished",
    "presenting", "nothing new is solved", "no compute booked", "reference
    body", "surface on file", "not meshed by this screen", "two grids were
    built".  DEMO MODE PERMITS past tense for RESULTS, so only past tense
    about RUNNING STAGES and lab machinery is hunted here.
  * Supervisor ruling, 2026-09-01 -- core-minutes are internal lab accounting
    and do not belong on a customer screen; wall time and dollars do.

L-425 CONTROL -- THE PART THAT MATTERS
--------------------------------------
In ``\\b(a|b|c)\\b`` the trailing ``\\b`` binds to EVERY alternative, so an
alternative that is a strict prefix of the word it means to catch matches only
the bare prefix -- and if that prefix is not a word anybody writes, it matches
NOTHING, EVER, while the sweep runs green.  One plant per RULE does not catch
this, because a live alternative catches the rule's plant and the dead one
hides behind it.

So every alternative carries ITS OWN plant, each asserted to fire and to be
attributed to its own rule.  The plants are hand-written realistic sentences
declared INDEPENDENTLY of the patterns: deriving them from ``PATTERN.pattern``
would reproduce any typo in the plant, the plant would fire, and the mutation
would survive its own fix.  A control derived from the thing it controls is not
a control.

Exit 0 = clean.  Exit 2 = a banned phrase reached a screen, or the control
itself failed.

==========================================================================
AMENDMENT 1 -- 2026-09-01.  THE `RECORDED` RULE IS NARROWED TO SANAA'S OWN
WORDING.  ONE ALTERNATIVE CHANGES AND NO OTHER BANNED PHRASE IS TOUCHED.
==========================================================================

Authority: Sanaa's demo shooting protocol, 2026-09-01 ~20:30Z
(`etc/sessions/2026-09-01T2030Z_sanaa_demo_shooting_protocol.md`, commit
`cfcf766f`), whose never-list item is the phrase **"not recorded"**.  Ruled by
the heat-transfer supervisor, 2026-09-01, on the reading below.

THE ALTERNATIVE THIS REPLACES, QUOTED AND STRUCK RATHER THAN REWRITTEN:

    ~~`recorded`~~   -- the bare word, anywhere, case-insensitive.

IT BECOMES:

    `not\\s+recorded`  -- her phrase, tolerating intervening whitespace.

WHY THE OLD ONE OVER-BANNED.  "Derived at the recorded rate" does not confess
an absence.  It says the rate is one this lab holds ON RECORD, which is exactly
the cost-basis honesty CLAUDE.md rule 12 demands -- the box cannot read its own
billing, so every dollar figure must name the rate it was derived at and say it
was not measured.  Banning that sentence pushes an author toward VAGUER
language about the lab's own costs, which is the opposite of what the rule is
for.  The phrase she actually wrote, "not recorded", is the one that reads as a
confession of a missing value, and it is the one still refused.

MEASURED BLAST RADIUS, BEFORE THE CHANGE: `pdftotext` over every PDF in this
directory found the word "recorded" **zero times**.  Nothing currently on a
rendered screen is released by this narrowing.  What it releases is the cost
sentence the shared contract composes for the act modules, which no act
authors and no act can reword.

⚠ THE CONSEQUENCE, STATED RATHER THAN DISCOVERED.  A sentence like "these
values were recorded earlier this week" -- the old alternative's own plant --
is no longer caught by THIS rule, and it is not caught by `PAST-RUNNING`
either, whose alternatives do not include it.  That is a real gap opened by
this narrowing.  Closing it means adding a past-tense-about-machinery
alternative to `PAST-RUNNING`, which is a DIFFERENT banned phrase and is
therefore excluded from this change by the ruling's own condition.  It is
reported for a separate change and must not be forgotten because this
amendment reads complete.

DRIVEN BOTH WAYS, and the drive is `--selftest` on this file: the narrowed
alternative still fires on all four wordings of "not recorded in this bundle"
that the Act A display module emits, and stays silent on "derived at the
recorded rate" and on three further legitimate uses of the word.
"""

import os
import re
import subprocess
import sys


HERE = os.path.dirname(os.path.abspath(__file__))

# Rendered artifacts, in the order a viewer meets them.
TARGETS = [
    os.path.join(HERE, "ACT_A_thermal_map_sheet.pdf"),
    os.path.join(HERE, "ACT_C_battery_module_sheet.pdf"),
]
FIGURE_DIRS = [os.path.join(HERE, "figures_actA"), os.path.join(HERE, "figures")]


# --------------------------------------------------------------------------
# Rules.  Each alternative is listed with its OWN plant, hand-written as a
# sentence that could plausibly appear on a screen.  Longer forms are taken
# whole -- record(?:ed|ing) not "record" -- per the L-425 remedy.
# --------------------------------------------------------------------------
RULES = [
    dict(
        id="RECORDED",
        why="reads as a recording rather than a live run (04:20Z, 03:10Z)",
        # AMENDMENT 1, 2026-09-01.  `recorded` -> `not\s+recorded`; see the
        # module docstring for the authority, the struck alternative, the
        # measured blast radius and the gap this opens.  The other five
        # alternatives are UNTOUCHED.
        pattern=re.compile(
            r"(?i)(\bnot\s+recorded\b|\b(replayed|re-displayed|"
            r"screens come from|retained on disk|no new number)\b)"),
        plants=[
            ("not recorded", "the peak for that point is not recorded here"),
            ("replayed", "the stored monitors are replayed at speed"),
            ("re-displayed", "this request re-displayed that run"),
            ("screens come from", "the screens come from that run"),
            ("retained on disk", "all figures are read from files retained on disk"),
            ("no new number", "no new number is produced by this request"),
        ],
        # THE NEGATIVE ARM, ADDED WITH AMENDMENT 1.  A narrowing that has not
        # been shown to still fire is not a narrowing, it is a deletion; and a
        # narrowing that has not been shown to release what it was narrowed FOR
        # has not been driven either.  Both arms live here, beside the rule.
        #
        # `negatives` is an OPTIONAL key: every other rule is unchanged and
        # supplies none, so this adds an arm without touching any other phrase.
        negatives=[
            # The sentence this narrowing exists to release. Composed by the
            # shared demo contract and rendered by the sequencer; no act
            # authors it and no act can reword it.
            "Compute used: 19.8 processor-minutes (gross), about $0.02, "
            "derived at the recorded rate.",
            # Three further legitimate uses of the word, which the bare-word
            # alternative also refused.
            "the rate is the one recorded for this machine",
            "every field is newer than the moment recorded at launch",
            "the estimate and the actual are both recorded in the report",
        ],
    ),
    dict(
        id="SOLVER-NONE",
        why='"Solver: none" is never shown on a results screen (03:10Z)',
        pattern=re.compile(r"(?i)solver:\s*none"),
        plants=[("Solver: none", "Solver: none on this request")],
    ),
    dict(
        id="NO-GEOMETRY",
        why="denies the geometry the act is bound to (03:40Z never-list)",
        pattern=re.compile(
            r"(?i)\b(no surface loaded|reference body|surface on file|"
            r"not meshed by this screen)\b"),
        plants=[
            ("no surface loaded", "No surface loaded for this case"),
            ("reference body", "the reference body is shown instead"),
            ("surface on file", "the surface on file is used here"),
            ("not meshed by this screen",
             "the upload is not meshed by this screen"),
        ],
    ),
    dict(
        id="INTERNAL-COST",
        why="core-minutes are internal lab accounting; a user sees wall time "
            "and dollars (supervisor ruling)",
        pattern=re.compile(r"(?i)core[- ]minute(?:s)?"),
        plants=[
            ("core-minute(s)", "upfront estimate 87.902 core-minutes"),
        ],
    ),
    dict(
        id="PAST-RUNNING",
        why="past tense about a RUNNING stage or lab machinery; DEMO MODE "
            "allows past tense only for results",
        pattern=re.compile(
            r"(?i)\b(before the first solver started|were fixed before|"
            r"was written down|were written down|two grids were built|"
            r"already finished|no compute booked|nothing new is solved)\b"),
        plants=[
            ("before the first solver started",
             "the labels were set before the first solver started"),
            ("were fixed before", "the criteria were fixed before running"),
            ("was written down", "the tolerance was written down in advance"),
            ("were written down", "the labels were written down in advance"),
            ("two grids were built", "two grids were built for this point"),
            ("already finished", "this sweep is already finished"),
            ("no compute booked", "no compute booked against this request"),
            ("nothing new is solved", "nothing new is solved on this screen"),
        ],
    ),
]


def pdftotext(path):
    out = subprocess.run(["pdftotext", "-q", path, "-"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    # Rejoin words the layout engine split across lines, so a banned phrase
    # cannot hide in a line break.
    return re.sub(r"\s+", " ", out.stdout)


#: The four wordings the Act A display module emits for a missing value.
#: Taken from that module's own strings, not paraphrased: a narrowing driven
#: against a paraphrase proves nothing about the text that actually renders.
NOT_RECORDED_SITES = (
    "not recorded in this bundle",
    "not recorded in this bundle; the readers and the guard are named below",
    "Mesh cells: not recorded in this bundle",
    "Geometry guard: not recorded in this bundle",
)


def control():
    """One plant per ALTERNATIVE, each attributed to its own rule.

    AMENDMENT 1 adds a second arm: a rule carrying `negatives` must stay SILENT
    on every one of them. A rule that fires on everything is as useless as one
    that fires on nothing, and only the negative arm separates them. The key is
    optional, so every rule that does not carry one behaves exactly as before.
    """
    dead = []
    loud = []
    total = 0
    for rule in RULES:
        for alt, plant in rule["plants"]:
            total += 1
            hits = [r["id"] for r in RULES if r["pattern"].search(plant)]
            if rule["id"] not in hits:
                dead.append((rule["id"], alt, plant, hits))
        for neg in rule.get("negatives", ()):
            total += 1
            m = rule["pattern"].search(neg)
            if m:
                loud.append((rule["id"], neg, m.group(0)))
    # AMENDMENT 1's OWN ARM, driven against the strings that really render.
    for site in NOT_RECORDED_SITES:
        total += 1
        if not any(r["pattern"].search(site) for r in RULES):
            dead.append(("RECORDED", "not recorded", site, []))
    if loud:
        sys.stderr.write(
            "REFUSE: %d rule(s) fire on a sentence that must stay clean. A "
            "narrowing that still refuses what it was narrowed for has not "
            "been made, and a rule that fires on everything is as useless as "
            "one that fires on nothing.\n" % len(loud))
        for rid, neg, phrase in loud:
            sys.stderr.write("  rule %-14s negative %r -> matched %r\n"
                             % (rid, neg, phrase))
        raise SystemExit(2)
    if dead:
        sys.stderr.write(
            "REFUSE: %d alternative(s) never fire on their own plant. An "
            "alternative that cannot catch its own plant catches nothing on a "
            "real screen either, and the sweep would run green.\n" % len(dead))
        for rid, alt, plant, hits in dead:
            sys.stderr.write("  rule %-14s alternative %-32r plant %r -> %s\n"
                             % (rid, alt, plant, hits or "NO RULE FIRED"))
        raise SystemExit(2)
    return total


def main():
    n_alt = control()
    print("L-425 control: %d alternatives, each fires on its own plant and is "
          "attributed to its own rule\n" % n_alt)

    targets = list(TARGETS)
    for d in FIGURE_DIRS:
        if os.path.isdir(d):
            targets += [os.path.join(d, f) for f in sorted(os.listdir(d))
                        if f.endswith(".pdf")]

    missing = [t for t in targets if not os.path.exists(t)]
    present = [t for t in targets if os.path.exists(t)]
    if not present:
        sys.stderr.write("REFUSE: no rendered artifact found; nothing was "
                         "checked. Compile the sheets first.\n")
        raise SystemExit(2)
    for t in missing:
        print("SKIP (not built) %s" % os.path.basename(t))

    bad = 0
    for path in present:
        text = pdftotext(path)
        if text is None:
            print("UNREADABLE   %s" % os.path.basename(path))
            bad += 1
            continue
        hits = []
        for rule in RULES:
            for m in rule["pattern"].finditer(text):
                s = max(0, m.start() - 45)
                hits.append((rule["id"], m.group(0),
                             text[s:m.end() + 45].strip(), rule["why"]))
        if hits:
            bad += 1
            print("BANNED PHRASE %s" % os.path.basename(path))
            for rid, phrase, ctx, why in hits:
                print("   [%s] %r\n      ...%s...\n      %s"
                      % (rid, phrase, ctx, why))
        else:
            print("clean        %s" % os.path.basename(path))

    print("\n%d rendered artifacts checked, %d carrying banned phrases"
          % (len(present), bad))
    if bad:
        raise SystemExit(2)
    print("PASS -- no banned phrase reaches an Act A or Act C screen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
