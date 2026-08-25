# THERMAL TIERING DIRECTIVE — every case carries its tier beside its verdict

**Status:** IN FORCE from 2026-08-25. **Binds both** the T-family ladder
(`docs/campaigns/T-family/`) and the DC-cooling spine
(`docs/campaigns/F14-cooling-ladder/`). Owned by the heat-transfer supervisor.

**Version 1.0.** Amendments are appended at the foot as dated blocks, never by
rewriting above (CLAUDE.md rule 6).

---

## 1. The directive, in Sanaa's own words

Sanaa's own session turn, **2026-08-25**, reproduced **BYTE-EXACT — typos,
spacing and capitalisation as she wrote them.** It is **not** normalised, and it
must not be normalised by any later hand:

> i just meant for now cfd, ansys verification and heat transfer teams work on completeing all the tasks/ running all the cases and recording per our conventions, and record whether the case is hold, gate reached or surveyed or not held. Once that is done we will go back to the Matrix config. But for now these three teams work on that

And, from her session turn of the same day that put this team back to work:

> GOOd. For now dafoam and closure teams can go to rest and heat transfer team goes back to its tasks, bc i want all my tokens used by the cfd, ansys verification and heat transfer teams, that way we can continue building out matrix of things we know the lab can holds, or a gat is reached/ surveyed.

Her term for the three-column standard, also hers and also unnormalised:
**"our tripple crown standard"**.

**Why unnormalised.** Tonight's attribution work established that **normalised
spelling is the signature of a relayed paraphrase rather than a primary source**.
A quotation that has been tidied cannot be distinguished from a reconstruction.
Both blocks above reached this team **through the chief**, who states they are
her own session turns; that relay is disclosed here rather than hidden, and the
text is carried exactly as received.

---

## 2. What the directive requires

1. **Run the cases.** The scope is *"all the tasks / all the cases"* — the
   T-family ladder and the DC-cooling spine, worked through, not cherry-picked.
2. **Record per our conventions** — pre-registration frozen by sha before any
   run, the planted-zero control, the strict completion rule with its age guard,
   Roache triple gating. **This directive adds a field; it removes no gate.**
3. **Every case record carries its own TIER, written at the time it is graded**,
   from Sanaa's four words. Not collected later by an auditor.
4. The central `COVERAGE_MATRIX.md` resumes *"once that is done"*. **Until then
   the tier lives beside the verdict in this team's own records.**

---

## 3. THE TWO VOCABULARIES ARE DIFFERENT AND ARE NEVER CONFLATED

This is the load-bearing clause of the whole directive.

| | **VERDICT** | **TIER** |
|---|---|---|
| **Grades** | what the **gate** did | what the **case establishes for the lab** |
| **Vocabulary** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` | `HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` (and `NEVER RUN` where nothing was run) |
| **Source** | CLAUDE.md rule 1, `VERIFICATION_CHARTER.md` §2 | Sanaa, 2026-08-25, quoted verbatim in §1 |

**They overlap at exactly one word — `GATE REACHED` — and nowhere else.** Both
are written, **side by side**, on every graded thermal record.

### 3.1 The tier may never flatter the verdict

**A tier is a claim about what the lab knows.** It is treated with the same
scepticism as a peer's claim, and it is subject to the same evidence. Binding
consequences, each of which has already been violated once in this family:

- A row whose verdict is **`NOT A RESULT`** **cannot** be tiered `HOLDS`.
- A row whose Roache triple is **not `CONVERGING`** **cannot** hold **G**,
  whatever its deviation. CLAUDE.md rule 5: *the gate can only turn a PASS or
  GATE FAIL **into** NOT A RESULT, never the reverse.*
- A row **any one of whose levels did not plateau** **cannot** hold **G**. Rule
  5 clause (1) fires **before** the triple is classified at all.
- A row built as mesh **PAIRS** has **no observed order to quote** and cannot
  hold **G**. An order quoted from a **neighbouring ladder's** record does not
  belong to it.
- A row whose **primary source is NOT OBTAINED** cannot hold **P**, and a row
  with **no frozen pre-registration on disk** cannot hold **P** either.
- Every **`GATE REACHED`** tier **must name which of V / G / P is missing.** A
  bare `GATE REACHED` is not a usable row.

### 3.2 The low tiers are recorded, not skipped

Sanaa's sentence names all four tiers deliberately. **A case that only ever
reaches `SURVEYED` is still run and still recorded, as `SURVEYED`.** A case that
is honestly `NOT HELD` is recorded that way. **Suppressing a weak row flatters
the denominator** — the D414 / D420 defect class, which recurred in this team's
own `MATRIX_CONTRIBUTION` file when a `NOT A RESULT` row was found missing and
the census moved 36 → 37.

---

## 4. WITH THE VERIFICATION TEAM PAUSED, THIS CHECK HAS NO SECOND READER

The verification team is at rest. **Nobody downstream will catch an over-claimed
tier before it reaches Sanaa.** This team is therefore both the claimant and the
only check on the claim, which is the condition under which claims are least
reliable.

**The direction of error in this family is known and it is the flattering one.**
Every defect found in thermal records in the preceding two days ran that way:

- **K0c was tiered `HOLDS` on a triple it does not have** — it was built as mesh
  **pairs**, and the observed orders quoted for it belong to **K0b's** ladder,
  whose own record states at line 335 that those values *"do not apply to these
  cases and are not used."*
- **Five further claimed `HOLDS` were in fact `GATE REACHED`.**
- **A `NOT A RESULT` row was omitted** from a census, moving the denominator in
  the lab's favour.
- **Band and deviation were transposed on three rows** simultaneously labelled
  `PASS`, so the table contradicted its own verdict.

**That is not a run of coincidences to be explained away. It is the prior this
team now audits under**, and it is why §3.1 is written as a list of prohibitions
rather than as guidance.

**Operative rule: where a tier cannot be settled from artifacts, the uncertainty
is recorded, not resolved in the lab's favour.** `PENDING` is available for a row
not yet run; it is **never** used to soften a `GATE FAIL`.

---

## 5. The three columns, as Sanaa's "tripple crown standard"

| Column | What it certifies | What defeats it here |
|---|---|---|
| **V** | Code verification — an exact solution, a manufactured solution, or a correlation | the reference is not on disk; the "correlation" supplies no band |
| **G** | Grid convergence — a **CONVERGING** Roache triple, **GCI at Fs = 1.25**, and an **observed order** | a pair not a triple; a non-CONVERGING triple; a level that did not plateau; **a recipe fork between levels**; a GCI quoted on non-monotone values |
| **P** | Validation against a **public primary source**, with the **pre-registration on disk** | primary NOT OBTAINED; graded against a secondary; no frozen prereg |

### 5.1 A recipe fork defeats G

Adopted from the **cfd team's ruling** — cited as **theirs**: *an observed order
computed across a **recipe-forked** gap is `NOT A RESULT`*, because it is a slope
fitted across a **change of experiment** rather than a change of grid. They found
**7 of 14 ladders lab-wide** recipe-forked. A Roache order is meaningful only
when the **sole** difference between levels is the mesh spacing under one
systematic refinement recipe: a change of `fvSchemes`, of `fvSolution`
tolerances or relaxation, of turbulence model, of thermophysical properties, or
of **boundary-condition type or wall treatment** between levels is a fork.

### 5.2 A comfortable deviation is not a result

Adopted from the **ansys-verification team's** VMFL051 result — cited as
**theirs**. All three levels `rc = 0`, age guard holding with margin, and the
gate deviation **inside the band at −0.2337 %** against a ±0.5 % target — *a
value a team scoring on gate deviation alone would have written up as `PASS`.*
They returned **`NOT A RESULT`**, on two independent rule-5 clauses either of
which alone sufficed:

- **L1 and L2 both failed the frozen per-level plateau clause** — peak-to-peak
  **6.240e-03** and **3.535e-03** against a registered **1.000e-03**. Only L3
  plateaued.
- **The triple was `OSCILLATORY`, R = −1.3486** (3.2278606097 / 3.2233427020 /
  3.2294355513). **No observed order, and correctly no GCI quoted**, the values
  not being monotone.

Their diagnosis, recorded as **bounded and not established**: the level-to-level
differences (4.5e-03, −6.1e-03) are **the same order as L1's and L2's own
residual unsteadiness**, so the triple plausibly measured **transient noise
rather than grid error**.

**Binding here:** per-level plateau is checked **explicitly, level by level,
against that level's own registered criterion, before the triple is classified
at all.** A ladder with **no** registered per-level plateau criterion is a
finding in its own right — a gate that cannot fail on plateau is unarmed — and
that is recorded separately from a level that had one and missed it. The remedy
for an exposed rung is a **new pre-registration** with a longer `endTime` and a
per-level plateau precondition; **never an edit to a frozen one.**

---

## 6. Where the tier is written

On each graded thermal record, in its results/verdict block, as two adjacent
fields — for example:

    VERDICT: NOT A RESULT   (triple OSCILLATORY, R = -1.3486; no order, no GCI)
    TIER:    GATE REACHED   (G missing: triple not CONVERGING; V and P held)

Both fields are mandatory on every graded record from 2026-08-25 onward.
Records graded before that date are **retro-tiered as they are re-opened**, never
in a silent sweep, and a retro-tier states the date it was assigned.

---

## 7. What this directive does NOT do

- It **does not** create, retire or move any gate, threshold, band, cap or label.
- It **does not** alter CLAUDE.md rule 1's verdict vocabulary, which is fixed.
- It **does not** authorise any send. **SUBMISSIONS REMAIN PARKED**; sending is
  Sanaa's alone (CLAUDE.md rule 7).
- It **does not** settle **D389** (the S13 peak-to-peak normalisation, ~24×
  looser on an absolute temperature than it reads). D389 re-grades the whole
  thermal corpus and **no single rung may take it** — it stays on Sanaa's desk.
- It **does not** fix the lab's V/G/P schema, which three teams have been scoring
  on incompatibly and which `docs/COVERAGE_MATRIX.md` — **which does not exist**
  — has never fixed. That is the verification team's to own when it resumes, and
  it is escalated, not decided here.
