#!/usr/bin/env python3
"""Sweep EVERY STRING the Act C act module puts on a screen, not just its PDFs.

THE GAP THIS CLOSES, AND IT WAS NAMED BEFORE IT WAS BUILT.  The content
specification's section C.4 says it plainly: `check_actC_gate_screen.py` reads
PDFs through `pdftotext` and CANNOT SEE A GUI SURFACE.  A Report tab and a
Conclusion tab rendered as live markup are not PDFs and are swept by nothing,
so every protection the PDF guard provides is simply absent there.

That gap is real for arbitrary control-room markup and stays a dependency on
the team that owns the page.  But it is NOT unavoidable for this act, because
this act's screen content is not markup somebody types -- it is the strings the
act module returns, and those can be enumerated.  So they are, here, and the
SAME rules are applied: the numeric rules and the graded allowlist are imported
from the PDF guard rather than copied, so there is exactly one definition of
what a withheld temperature is and the two surfaces cannot drift apart.

WHAT IT WALKS.  Every user-visible string of all nine stages, the geometry and
assumptions tables, the expert discussion beats, the banner words, the elapsed
and cost sentences, the progress line, and every field of the closing report --
including TABLE ROWS.

    ONE FINDING WORTH STATING RATHER THAN SILENTLY COVERING: the contract's
    `Table` language-checks its TITLE and its HEADERS and does NOT check its
    ROWS.  Every number a viewer reads is in a row.  This sweep checks them;
    the contract does not, and that is reported to the team that owns it.

THE PLANTED CONTROL.  A sweep that walked no strings would report no breach for
a reason that has nothing to do with the act.  So it plants a known-bad
sentence into the collected set and refuses unless every rule that should fire
on it does; and it asserts a floor on how many strings and numeric tokens it
actually read.  A zero from a reader not shown able to see a non-zero is not
evidence.

Exit 0 = clean.  Exit 2 = a withheld value or a banned phrase reaches an Act C
screen string, or a control failed.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import actC_graded_admission as ADMIT                          # noqa: E402
import check_actC_gate_screen as SCREEN                        # noqa: E402
import check_demo_language as LANG                             # noqa: E402
import actC_battery_module_act as ACTMOD                       # noqa: E402

#: Floors for the coverage assertion.  Set below what the act renders today so
#: an honest edit does not trip them, and far enough above zero that a sweep
#: which collected nothing cannot pass.
MIN_STRINGS = 60
MIN_TOKENS = 40

#: The plant.  Written by hand, INDEPENDENTLY of the rules it must trip, per
#: the L-425 discipline followed everywhere else in this directory.
PLANT = ("the hottest cell reaches a peak of 298.873 K, a rise of 5.9 "
         "degC over the coolant")


def collect(act):
    """Every user-visible string this act produces, with where it came from."""
    out = []

    def add(where, value):
        if value is None:
            return
        if isinstance(value, str):
            if value.strip():
                out.append((where, value))
        elif isinstance(value, dict):
            for k, v in value.items():
                add(where, k)
                add(where, v)
        elif isinstance(value, (list, tuple)):
            for v in value:
                add(where, v)

    add("run record header", act.run_record().solver_header())
    add("prompt", act.prompt().text)

    r = act.restatement()
    add("restatement", [r.restatement, r.confidence,
                        r.cost_estimate.on_screen()])

    a = act.assumption()
    add("assumption", [a.assumption, a.finding, a.correction])

    g = act.geometry()
    add("geometry", g.display_label)
    mesh = act.mesh_plan()
    add("geometry", g.solved_geometry_sentence(mesh.cell_count))
    for m in g.matches:
        add("geometry", m.quantity)

    for table in (act.geometry_table(), act.assumptions_table()):
        add("table %s" % table.table_id,
            [table.title] + list(table.headers) +
            [c for row in table.rows for c in row])

    add("mesh", [mesh.wall_zoom_hint] + list(mesh.resolution_headers) +
        [c for row in mesh.resolution_rows for c in row] +
        [mesh.cell_count.on_screen()])

    f = act.feasibility()
    add("feasibility", [f.check, f.verdict_for_user, f.result.on_screen()])

    s = act.solve_replay()
    add("solving", [spec.label for spec in s.series])
    # COMPOSED BY THE SHARED CONTRACT, NOT AUTHORED HERE, and tagged so that a
    # breach in one of them is instantly attributable. These three sentences
    # are built by `demo_mode` from the act's numbers and are rendered by the
    # sequencer (its cost payload calls `cost_line`), so they reach a screen
    # and must be swept -- but rewording them is not this act's to do.
    add("solving (composed by the shared contract)",
        [s.clock().on_screen(), s.cost_sentence(), s.progress_line(1, 1),
         s.progress_line(s.total_iterations, s.sweep_points)])

    ch = act.gates()
    add("checks", ch.grid_statement)
    for table in (ch.planted_checks, ch.conservation):
        if table is None:
            continue
        add("table %s" % table.table_id,
            [table.title] + list(table.headers) +
            [c for row in table.rows for c in row])

    res = act.results()
    add("results", list(res.verification_lines) + list(res.limitations) +
        [res.cost_actual.on_screen(), res.cost_estimate_from_stage_2.on_screen()])
    for fig in list(res.fields) + list(res.plots):
        add("figure", [fig.title, fig.caption])
    for table in res.tables:
        add("table %s" % table.table_id,
            [table.title] + list(table.headers) +
            [c for row in table.rows for c in row])

    for stage, beats in act.discussions().items():
        for role, lines in beats:
            add("discussion after %s" % stage, list(lines))

    add("banner", list(act.banners().values()))

    closing = act.closing()
    if closing is not None:
        add("report", [closing.title] + list(closing.abstract) +
            list(closing.methods) + list(closing.uncertainty) +
            list(closing.next_investigations) + list(closing.conclusion_lines) +
            [closing.certificate_state])
        for row in closing.results:
            add("report row", row)
    return out


def scan(text, admissible):
    """Apply the PDF guard's own rules, plus the graded allowlist."""
    hits = []
    for rule in SCREEN.NUMERIC_RULES:
        for phrase, _pos in rule["fn"](text):
            if (rule["id"] in SCREEN.ALLOWLISTED_RULES
                    and ADMIT.token_admissible(SCREEN.hit_token(phrase),
                                               admissible)):
                continue
            hits.append((rule["id"], phrase, rule["why"]))
    for rule in LANG.RULES:
        for m in rule["pattern"].finditer(text):
            hits.append((rule["id"], m.group(0), rule["why"]))
    return hits


def main():
    n_pos, n_neg = SCREEN.control()
    print("thermal-withholding control (reused from the sheet guard, not "
          "copied): %d positive arms, %d negative arms" % (n_pos, n_neg))
    n_adm, n_ref = SCREEN.allowlist_control()
    print("allowlist control, both directions: %d admitted, %d still refused"
          % (n_adm, n_ref))

    try:
        admissible, note = ADMIT.derive()
    except ADMIT.AdmissionRefused as exc:
        sys.stderr.write("REFUSE: %s\n" % exc)
        return 2
    print("admissibility source: %s\n" % note)

    strings = collect(ACTMOD.ACT)
    tokens = 0
    breaches = []
    for where, text in strings:
        tokens += len(re.findall(r"(?<![\d.])\d+(?:,\d{3})*(?:\.\d+)?", text))
        for rid, phrase, why in scan(text, admissible):
            breaches.append((where, rid, phrase, text, why))

    # THE PLANTED CONTROL, run against the same scanner on the same path.
    planted = scan(PLANT, admissible)
    fired = {rid for rid, _p, _w in planted}
    expected = {"ABS-TEMP", "KELVIN-UNIT", "CELSIUS", "THERMAL-CLAIM"}
    if not expected.issubset(fired):
        sys.stderr.write(
            "REFUSE: the scanner did not catch its own plant. Missing rules: "
            "%s. A scanner that cannot see a withheld temperature in a "
            "sentence written to carry four of them saw nothing in the act "
            "either.\n" % sorted(expected - fired))
        return 2
    print("planted control: the scanner catches its own plant on %d rule(s)"
          % len(fired))

    if len(strings) < MIN_STRINGS or tokens < MIN_TOKENS:
        sys.stderr.write(
            "REFUSE: the sweep walked %d string(s) and %d numeric token(s), "
            "below the floor of %d / %d. A clean result from a sweep that read "
            "almost nothing is not evidence.\n"
            % (len(strings), tokens, MIN_STRINGS, MIN_TOKENS))
        return 2
    print("swept %d screen string(s), %d numeric token(s), across %d surface "
          "group(s)" % (len(strings), tokens,
                        len({w for w, _t in strings})))

    if breaches:
        print("\nWITHHELD BREACH -- %d" % len(breaches))
        for where, rid, phrase, text, why in breaches:
            print("   [%s] %r in %s -- %s" % (rid, phrase, where, why))
            print("        %s" % text[:160])
        return 2

    print("\nPASS -- no withheld value and no banned phrase reaches any Act C "
          "act string, tables and report tab included")
    return 0


if __name__ == "__main__":
    sys.exit(main())
