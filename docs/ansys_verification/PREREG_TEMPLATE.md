# ANSYS-VERIFICATION PRE-REGISTRATION TEMPLATE — the standard-case, template-speed form

**Authority.** Sanaa's directive of 2026-08-25, byte-exact:

> "Prereg goes template-speed: standard verification/validation cases use the
> 10-line prereg form (case, reference, quantities, bands, ladder, decomposition
> seed, criteria) — minutes to freeze, not sessions. Bespoke frozen documents are
> reserved for novel or contested cases only."

And, on the ceiling this team can score:

> "it's fine that itll reach gate reach at best. Anything gate reached for for that
> team means we reached ansys, which is good enough."

And the constraint that governs this template:

> "We are raising the denominator — core-hours — not lowering the bar."

**Read this last sentence as the rule for this form. The template makes a
registration SHORT, never WEAKER.** Every standing clause still binds: the gate and
band frozen **before** any number exists (CLAUDE.md rule 2); the planted-zero
control with the reader shown able to see a non-zero and refusing if it cannot
(rule 3); strict completion (rule 4); Roache triple gating (rule 5); the cost and
cap (rule 12); the freeze committed before compute. **If a clause will not fit in
ten lines, the ten lines CITE the standing clause by name — they never omit it.**
This file is a frozen file under CLAUDE.md rule 6.

---

## The standard form (copy this block; fill it; freeze it; commit before compute)

```
1. CASE            : VMFLnnn — <title> — manual p.<pp>. Solver=<...>. NOT YET RUN;
                     verification/runs/ansys_verification/VMFLnnn/ absent at <UTC>.
2. REFERENCE       : <value> <unit>, source=<citation>.  Ansys reported=<...> (CONTEXT ONLY).
3. REFERENCE KIND  : {closed-form/exact = buys V | correlation = buys V, NEVER P |
                     measured/experimental = can buy P | manual's own code output /
                     code-to-code = buys NEITHER}.  → decides the score column.
4. TIER CEILING    : {PASS | GATE REACHED} — with one-line reason (a code-to-code
                     reference CANNOT exceed GATE REACHED, whatever the number).
5. QUANTITIES      : <what is measured, on which patch/probe, in what unit>.
6. BANDS (THE GATE): |lab − ref|/|ref| ≤ <tol>  (or absolute band if ref≈0), at the
                     finest level. Justify <tol> from the manual's 3% goal + target
                     rounding + grid, NEVER from a first run.
7. LADDER          : solver, model, mesh family; birth-certified (MESH_STANDARD §6).
8. DECOMPOSITION   : grid triple (r, three levels + cell counts) and any parallel
   SEED              decomposition/RNG seed. Single-grid? say so, verdict is single-grid.
9. PRINCIPAL RISK  : the ONE named failure mode predicted BEFORE compute (the field
                     that let VMFL003 call its own failure and be right).
10. EXPECTED ORDER : formal order p_f and expected observed p_obs; declare p_obs
                     "SUSPICIOUSLY HIGH" if it would exceed p_f (a warning, not a win).
11. WEDGE/GEOM BIAS : axisymmetric only — carry sin(t)/t area deficit (N-AV9) in the
                     error budget; note the PRESSURE-DROP form differs from the
                     AREA-DEFICIT form. Cartesian case → "N/A (not axisymmetric)".
12. COST + CAP     : estimate in core-minutes (basis stated); cap; overrun STOPS the run.
13. CONTROLS       : planted-zero (rule 3) fires in the comparator; strict completion
                     (rule 4); Roache gating (rule 5); LAUNCHER FREEZE CHECK (rule 2) — non-droppable (see Amendment 2). Comparator sha + --selftest green.
```

Lines 1–8 and 12 are Sanaa's seven fields (case, reference, quantities, bands,
ladder, decomposition seed, criteria) expanded only where this team was bitten.
Lines 3–4, 9–11, 13 are the fields the team's own runs proved load-bearing —
**none may be dropped to save lines; where they do not apply, they say so.**

### Why each added field exists (the scar it closes)

- **REFERENCE KIND (line 3)** — required by Sanaa's V/P ruling. It alone decides
  which column a case can score: a **closed-form/exact** reference buys V; a
  **correlation** buys V but NEVER P (ruled); a **measured/experimental** reference
  can buy P; **the manual's own code output** (or any code-to-code comparison) buys
  **NEITHER** — reproducing a solver's number is not a verification. A row that
  quietly scored a code-to-code case as a credential rests on a false sentence.
- **TIER CEILING (line 4)** — stated up front so the honest ceiling is frozen with
  the gate, not discovered after. `GATE REACHED` is this team's success (Sanaa);
  it is not a shortfall.
- **PRINCIPAL RISK (line 9)** — VMFL003's registration named its own failure mode
  before compute and was right. The field forces that prediction.
- **EXPECTED ORDER, suspicious-high declared (line 10)** — an observed order above
  the scheme's formal order is a WARNING (cancellation, a lucky mesh, a reference
  coincidence), not a triumph. Both compressible cases were bitten by this.
- **WEDGE/GEOM BIAS (line 11)** — charter v1.4 / N-AV9: an OpenFOAM axisymmetric
  wedge under-represents the circular section by sin(t)/t (0.127% at 5°), a
  modelling bias no grid refinement removes. **The pressure-drop form of the term
  is not the area-deficit form** — a ΔP driven by wall shear scales differently from
  a bulk area deficit, so the budget term is case-shaped, not one number.
- **COST + CAP (line 12)** — rule 12; a proposal with no cost is disqualified.

---

## Worked example (VMFL059 — closed-form, buys V)

```
1. CASE      : VMFL059 — Conduction in a Composite Solid Block — p.185. laplacianFoam.
               NOT YET RUN; run dir absent at 2026-08-25T17:08:06Z.
2. REFERENCE : cooled wall 378 K, adiabatic wall 413 K; Incropera & DeWitt 5e p.117
               (closed form). Ansys Fluent 378.14 / 413.17 (CONTEXT ONLY).
3. REF KIND  : closed-form/exact → buys V.
4. CEILING   : PASS (a real validation credential if the band is met).
5. QUANTITIES: areaAverage(T) on rightWall (cooled) and leftWall (adiabatic) [K].
6. THE GATE  : |T_lab − T_exact|/|T_exact| ≤ 0.01 on BOTH walls, at L3.
7. LADDER    : laplacianFoam; DT read as a FIELD (75/150 via setFields), q'''=1.5e6
               W/m3 via scalarSemiImplicitSource in material-1 zone; 3 birth-certified meshes.
8. SEED      : r=2 triple L1/L2/L3 = 280/1120/4480 cells; serial (no decomposition).
9. RISK      : conductivity smearing at the x=0.05 interface if it is not a cell
               face → block boundary pins it a face at every level.
10. ORDER    : p_f=2 (Gauss linear); expect p_obs≈2; >2.3 SUSPICIOUS.
11. WEDGE    : N/A (Cartesian planar, not axisymmetric).
12. COST     : ≈3 core-min total (3 tiny 2-D solves), reported-by-owner basis; cap 15.
13. CONTROLS : grade_vmfl059.py --selftest green; plant K=1.234; rule 4 + rule 5 wired.
```

## When a case is NOT standard — use a bespoke document instead

**One-line rule:** a case is **contested** (→ bespoke frozen document, not this form)
when the reference number's **value, provenance, or reference-KIND cannot be pinned
from the manual + archive without a judgement call** — a disputed benchmark, a
tolerance that must be argued at length, a driving input the manual omits, or a
modelling choice that changes which column the case scores. Everything else —
a reference you can cite and a gate you can justify in the lines above — is standard,
and standard goes template-speed.

*(VMFL010 sits on the line: its reference kind is code-to-code, disclosed on line 3,
and it still fits the form — the disclosure IS the honest ceiling, not a dispute.)*

---

## AMENDMENT 1 — 2026-08-25 — tier-ceiling vocabulary and the VMFL059 worked example corrected (category error at the source)

This template is a frozen file (header, rule 6); this correction is a dated amendment
appended at the foot, not an edit above. **lines whose number changed above this
section: 0.**

**Why.** The form and its worked example taught a category error — a closed-form case
given a tier ceiling of `PASS` and called "a validation credential" — which VMFL059
inherited verbatim, and which every future case copying this form would inherit. `PASS`
is a **verdict** word, not a **tier**; the tier vocabulary is `HOLDS / GATE REACHED /
SURVEYED / NOT HELD`, in active use across this team (VMFL045 RESULTS, VMFL007 and
VMFL003_M2 comparators, COVERAGE_ROWS). The two vocabularies overlap only at `GATE
REACHED`. Fixed here at the source.

**Struck and corrected.**

- **Line 4 of the standard form**, struck: "4. TIER CEILING : **{PASS | GATE REACHED}**
  …". Corrected to: **"4. TIER CEILING : {HOLDS | GATE REACHED}"** — the credential tier
  is `HOLDS`, earned only where the reference is **measured/experimental** (buys
  P/validation) and the gate is met. `GATE REACHED` is the ceiling for a case that can
  buy only **V** (closed-form/exact or correlation) or **neither** (code-to-code); such a
  case **cannot exceed** `GATE REACHED`, whatever the number.

- **Line 98 of the worked example (VMFL059)**, struck: "4. CEILING : **PASS (a real
  validation credential** if the band is met)." Corrected to: **"4. CEILING : GATE
  REACHED (closed-form buys V, never P; band met = code verification, NOT a validation
  credential)."** VMFL059 is closed-form → buys V → its ceiling is `GATE REACHED`,
  matching the VMFL007 precedent and VMFL059 PREREGISTRATION.md AMENDMENT 1 of this date.

**What did NOT change.** No standing clause, gate rule, band rule, cost/cap rule, control
or completion rule moved; the ten-line form's structure and the reference-KIND →
score-column mapping on line 3 (correct as written) are unchanged. Only the tier-ceiling
vocabulary (line 4) and the VMFL059 worked-example ceiling (line 98) are corrected.

---

## AMENDMENT 2 — 2026-08-25 — the LAUNCHER FREEZE CHECK is now a REQUIRED, non-droppable artifact

This template is a frozen file (header, rule 6); this correction is a dated amendment
appended at the foot, not an edit above. **lines whose number changed above this
section: 0** — line 13 (CONTROLS) was extended in place with no line added or removed,
so every line number, including the worked example's line 98 cited by Amendment 1, is
unchanged.

**Why.** The two template-speed cases (VMFL059, VMFL010) were built from this form and
each launcher shipped with **zero** launch-time freeze-verification lines, while the
bespoke launchers (VMFL003-M2: 3 lines; VMFL007: 1) prove at launch that the
pre-registration and the comparator on disk ARE the blobs committed at HEAD. A launcher
that does not re-prove the freeze at launch can run a solver against a pre-registration
or a grading path that has drifted from the committed one — the freeze is the evidence,
and an unverified freeze is no freeze. Sanaa's directive for this form was *"minutes to
freeze, not sessions"* alongside *"We are raising the denominator — core-hours — not
lowering the bar."* **A dropped guard is lowering the bar; short must never mean weaker.**

**The requirement (now binding on every case built from this form).** The case's launcher
MUST, before any solver starts, verify BOTH:

1. the **pre-registration** on disk hashes equal to `HEAD:<prereg path>`, and
2. the **comparator** on disk hashes equal to `HEAD:<comparator path>`,

each check **gating EXPLICITLY** with `|| { echo ABORT...; exit 1; }` — `set -e` does NOT
gate at a Bash tool's top level and `( set -e; … )` fails silently — and the resolved shas
recorded into the run's own launch record (e.g. `LAUNCH_RECORD.txt`). This artifact sits
in the **same non-droppable list** as the planted-zero control (line 13, rule 3) and the
mesh birth certificate (line 7, MESH_STANDARD §6): it is named in the form, it is not
optional, and a launcher without it is incomplete regardless of how short the form is.

**What did NOT change.** No gate rule, band rule, reference-KIND → score-column mapping,
tier-ceiling vocabulary, cost/cap rule, or completion/Roache rule moved; only line 13 was
extended in place to name the launcher freeze check, and this amendment states the
requirement in full.
