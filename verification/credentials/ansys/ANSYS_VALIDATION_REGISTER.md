# ANSYS VALIDATION REGISTER — every VM2026R1 case the lab has run

**Owner:** `ansys-verification-supervisor`. **Charter:**
`docs/charters/ANSYS_VERIFICATION_CHARTER.md` §6. **Created:** 2026-08-24 by
the harness-build lane, empty. **Append-only** under the private-index
protocol (CLAUDE.md rule 10): a row is never edited after it lands; a
correction or a re-run is a new row citing the old one.

**Reading rule.** Every case run is a row, whatever its verdict. **Only `PASS`
rows are credentials** — the lab's credential count from this suite is the
number of `PASS` rows and nothing else. `GATE FAIL` and `NOT A RESULT` rows
stay here honestly, with their numbers; they are findings, not deletions.
Verdict vocabulary only: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT`
/ `BLOCKED` / `PENDING`. Dates are UTC from a `date -u` read in the writing
invocation. Dollars are **derived** at the owner-stated $0.0513/core-h, never
measured (the box cannot read its own billing).

Reference result and tolerance are the **frozen** values from the case's
pre-registration, whose sha is the row's `prereg sha`; the comparator sha is the
committed grading script that produced the number.

| # | Case | Date (UTC) | Verdict | Lab value | Reference (source, manual p.) | Tolerance (frozen) | Artifact path | Prereg sha | Comparator sha | Cost, core-min (measured) | $ (derived) | RESULTS path |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

*No case has been run. Credential count: 0 PASS of 0 run.*
