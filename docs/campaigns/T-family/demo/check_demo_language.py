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
        pattern=re.compile(
            r"(?i)\b(recorded|replayed|re-displayed|screens come from|"
            r"retained on disk|no new number)\b"),
        plants=[
            ("recorded", "these values were recorded earlier this week"),
            ("replayed", "the stored monitors are replayed at speed"),
            ("re-displayed", "this request re-displayed that run"),
            ("screens come from", "the screens come from that run"),
            ("retained on disk", "all figures are read from files retained on disk"),
            ("no new number", "no new number is produced by this request"),
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


def control():
    """One plant per ALTERNATIVE, each attributed to its own rule."""
    dead = []
    total = 0
    for rule in RULES:
        for alt, plant in rule["plants"]:
            total += 1
            hits = [r["id"] for r in RULES if r["pattern"].search(plant)]
            if rule["id"] not in hits:
                dead.append((rule["id"], alt, plant, hits))
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
