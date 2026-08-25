# PRE-REGISTRATION TEMPLATE — standard VMFL case (10 lines of substance)

**This is the team's instrument for a STANDARD case** (CLAUDE.md rule 2; ANSYS
charter §5.1). Bespoke documents are for NOVEL or CONTESTED cases only. Copy this
file to `cases/ansys_verification/<CASE>/PREREGISTRATION.md`, fill every field, and
**commit it before any solver starts** — the freeze is the document's entire
evidentiary content. Frozen file (rule 6): after first compute, dated addenda only.

1. **Case id + manual page:** `<VMFLnnn>`, VM2026R1 p. `<page>` (title-page verified).
2. **Reference value + unit + source:** `<value> <unit>` — `<full citation as printed>`.
3. **Reference CATEGORY (Sanaa 2026-08-25):** `V` (exact/analytic) · `P` (genuinely
   measured/experimental, primary in the manual) · `NEITHER` (manual's own Fluent/CFX
   code output = code-to-code). State which and why.
4. **Ansys's own reported value (context only, NEVER the gate):** `<value>`.
5. **GATE expression + tolerance:** `|lab − ref| / |ref| ≤ <tol>` (or an absolute band
   where ref = 0), evaluated at the finest level; `<tol>` justified from the manual's
   agreement class and the grid triple, not from a first run.
6. **Level family (grid triple — 3 levels is the gate standard, Sanaa 2026-08-25):**
   `<L1 / L2 / L3 cell counts, refinement ratio>`; solver, model, mesh.
7. **CAP in core-minutes + cost_basis:** cap `<N>` core-min (est `<e>` × slack `<s>` for
   I/O contention); `$0.0513/core-h`, **REPORTED-BY-OWNER, NOT MEASURED**. Overrun STOPS
   the run (rule 12). Per-level wall `timeout = cap×60/ranks`, ranks=1.
8. **Comparator path + sha:** `<path>` — planted-zero control, strict-completion rule,
   Roache triple gating; passes `scripts/check_grader_self_blindness.py` (exit 0).
9. **TIER CEILING declared in advance + reason:** `HOLDS` · `GATE REACHED` · `SURVEYED`
   · `NOT HELD` — the ceiling this row can reach and why (e.g. P-limb open ⇒ GATE
   REACHED). Do not tier below what the row holds.
10. **FALSIFICATION clause:** the result that would mean the model/solver is WRONG —
    i.e. a `GATE FAIL` or a non-`CONVERGING` triple is a real possible outcome here,
    named before the run so the gate cannot be chosen to fit the answer.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING. A GATE FAIL or NOT A RESULT is recorded honestly, never softened.*
