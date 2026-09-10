# dafoam front: THE 3D ADJOINTS — CASE PROTOCOL state

**Protocol:** `docs/charters/CASE_PROTOCOL_CHARTER.md` v1.0, in force from Sanaa's 2026-09-10 ~16:50Z
turn. **VERIFY — the charter was NOT yet at HEAD when this file was written** (`git cat-file -e` on
`HEAD:docs/charters/CASE_PROTOCOL_CHARTER.md` returned not-found at `477ce19b`). Everything below is
built on the chief's condensed relay, **which states the charter is the authority**. **I re-read the
charter from HEAD when it lands and correct this file against it; until then every protocol mapping
here is marked VERIFY.**

**Front, her words:** *"dafoam on the 3D adjoints"*. **"No new families."**
**Scope, accordingly: A6 CRM wing-body, A3 ONERA M6, A2 MACH wing.** A4 Ahmed and A5 U-bend are in my
ladder but are **NOT** opened — that would be a new family.

**BUDGET EXEMPTION, recorded here and to be repeated on each registration** (chief's reading of her
closing clause, labelled as his and correctable by her): for the 3D demo cases still to run, **no cap
STOPS the run**, time or core-minutes, until hard 3D demos exist. **They are still costed at
registration and calibrated at completion** (rule 12 is not suspended — only the stop is). Each
registration carries the line *"ran under the 2026-09-10 exemption"*. **Nothing else is relaxed:**
gates stay frozen, comparators stay pinned, SUBMISSIONS STAY PARKED.

---

## STATE LINES

| case | stage | state | owed next |
|---|---|---|---|
| **A6 CRM wing-body `D8R`** | **5 (grade complete)** | **PASS — TWO ROWS, `SHIPPED` PASS + `PATCHED` PASS.** `EXIT: Optimal Solution Found`, 12/30 iters. CD **0.038756491279745384 → 0.03863923943624545**. CL **0.4999951170634741**, dev **4.88e-06** vs tol 0.005. Shipped-vs-patched gradient divergence **0.0008 %–0.054 %** over five twist DVs. Fields **DECOMPOSED ONLY** (4 arms × `processor0..3`, only `0/` at case root). | **certificate from the record** (stage 5 tail); reconstruction **in a COPY** — lane running |
| **A3 ONERA M6** | **5 (graded, one open question)** | Cp vs experiment RMS dev **0.0741** at the 0.2 station; shock **x/c 0.6717 CFD vs 0.5753 exp**, shift 0.0964. **OPEN: the FD-table question at `722a1fbd`** — baseline primal ran at `primalMinResTol 1e-8`, FD perturbation solves accepted **100× looser**, and a fine-mesh FD primal was **REFUSED at 1e-8**. | settle the FD question **grading-only, zero compute**, per `N-D44`; certificate only after |
| **A2 MACH wing `D6RF10`** | **5 (graded)** | R1 `GATE FAIL` (1.681×), R2 `NOT A RESULT` (deadline ~4 % short), R3 **binding-field `PASS` / rung `GATE FAIL`**. Ladder 759.667 core-min vs 1275 hard stop. Fields **decomposed only**. | reconstruction owed; **successor is open ON THE LEVERS**, not on the terminal state |
| **A2-B2R** | **1 (successor registration owed)** | `NOT A RESULT` on the registered `DIVERGED-TRIM` branch. Physics passed every gate it reached (CD within **0.015 %**, CL within **2.33e-06**, worst `finalRes` 4.652519276e-07 ≤ 1e-6); lost only the `DECOMP_RESULT` print line. | successor registration; **registered stage-4 first action = catch `AnalysisError`, read CD/CL FROM THE SOLVER LOG, never `prob.get_val`** |
| **A3FL2** | **1 (successor registration owed)** | Exercise `NOT GREEN`; GREEN structurally unreachable (`SMOKE_PRIMAL_ENDTIME=25` against a 1000-iteration primal). Option-acceptance half is a measured `PASS`. | pre-compute amendment to the smoke override; `nd` proof still **half** closed (PETSc KSP-setup acceptance unproven) |

## STANDING CONSTRAINTS ON THIS FRONT — mine to enforce (§9 authority), and they are NOT budget gates

1. **A GRADED RUN ROOT IS EVIDENCE AND IS NEVER WRITTEN INTO.** `reconstructPar` for a render writes new
   time directories; doing that inside a graded case adds fields newer than the case's own `0/` — the
   exact condition the age guard exists to catch — and mutates the artifact a re-grade would read.
   **Reconstruct in a COPY, assert the original byte-identical afterwards.** A banked `PASS` is not
   risked for a picture. In force on the D8R lane now.
2. **The DAFoam `AnalysisError` abort is a stage-4 STOP with a cause class, not a blocker.** Cause class:
   *toolchain acceptance clause, intended upstream behaviour* (`N-D44`; release v3.1.1 confirms including
   turbulence in `primalResTol` was a deliberate fix). **Registered first action: catch it and read the
   functionals from the solver log's `calcAllFunctions` print.** **One registered action per stop, and
   never the same action twice on the same state** — so if the catch yields no `calcAllFunctions` block,
   the next action is a *different* one, not a retry.
3. **`prob.get_val` IS FORBIDDEN AFTER A CAUGHT `AnalysisError`.** The raise fires *before* states reach
   the OpenMDAO output vector, and `DAFoamFunctions.compute` then pushes the **stale** vector back into
   OpenFOAM. Reading it returns **a silent wrong answer, not a missing one.** This clause goes into every
   successor registration on this front, verbatim.
4. **The `logs_A3` archive is not edited** — it is a past run's evidence sitting beside its own logs.
   Asserted 0 files modified.
5. **Not published as a number:** anything with a `GATE FAIL`, `NOT A RESULT`, or an open cause class.
   D6RF10's R3 is **two clauses** and may never be quoted as a bare `PASS`.

## WITHDRAWN, so nobody builds a demo on it

**The ACTD render pass's "111 PNGs" (boarded S-147b) does NOT exist on disk.** Zero `.png` files under
`ACTD-a2-decomposition`, `ACTD-meshtime`, or any path matching `decomp`. **Not offered as a demo asset.**

---

## CORRECTION 1 — 2026-09-10 — **VERIFY CLEARED: charter read from HEAD. Two of my stage readings were WRONG, and §1 contains a rule that lands on the D6 family's gate design.**

*lines whose number changed above this section: 0.* Appended; nothing above rewritten or struck.

**VERIFY IS DISCHARGED.** `docs/charters/CASE_PROTOCOL_CHARTER.md` is at HEAD, landed by `e24953a6`,
85 lines, read by me in full. **My scope reading was right** — §7: *"dafoam on the 3D adjoints"*, and
*"No new families."* **My budget reading was right** and matches the charter's own provenance block, which
adds one clause I had already recorded: *"supervisors record which runs ran under it."* **Two other things
I had wrong:**

### (a) D8R IS NOT AT "STAGE 5 COMPLETE". Its gate leg is done; its FAMILY leg does not exist, and the item says so itself.

§5 is *"Grade: the gates, **then the family**"* — medium and fine levels launched by the same daemon,
**observed order and GCI computed**, iterative error verified at least ten times smaller than the
level-to-level difference, **and only then** *"Certificate assembled from the record."*

**D8R has no grid family.** Its own grade json says so verbatim: `no_gci = "no grid family; standing rule 5
has no row; NO GCI IS QUOTED"`. So **D8R cannot produce a §5 certificate as the charter writes it**, and
the chief's suggestion that it is a candidate for a first certificate is **not something I can execute
without either building it a grid family or obtaining an explicit §5 carve-out for
optimisation-convergence items.** I am not inventing the carve-out: **changing what a certificate requires
is not in a supervisor's §9 authority.** D8R's correct state line is **"§5 gate leg complete, family leg
absent by the item's own registration; certificate BLOCKED on a §5 requirement it was never designed to
meet."** Its two-row `PASS` is untouched and remains the strongest result on this front.

*(A6 is an optimisation-convergence item, not a grid-convergence item. That is not a defect in D8R — the
item registered `no_gci` deliberately and honestly. It is a mismatch between what this case class produces
and what §5's certificate demands, and it is the chief's or Sanaa's to resolve, not mine.)*

### (b) §1's T23G2Rn2 RULE LANDS DIRECTLY ON THE D6 FAMILY, and it is the sharpest consequence of `N-D44`.

§1, verbatim: *"Solver tolerance strictly tighter than any gate that reads its output (the T23G2Rn2 rule:
**a tolerance equal to a gate voids the rung**)."*

**D6RF10's gate IS the solver's own acceptance threshold — not tighter than it, identical to it.** Its
frozen pre-registration says so at line 89:

> `Threshold / accept floor = CONV_BAR = 1.0e-05` = `primalMinResTol 1e-08 × primalMinResTolDiff 1000`

And `N-D44` established that DAFoam's own `checkPrimalFailure()` tests
`primalMaxRes / primalMinResTol_ > primalMinResTolDiff` — i.e. against **exactly that product**, on
**exactly the same quantity family** the gate reads. **The gate and the solver's own acceptance test are
the same number applied to the same thing.** That is precisely the configuration §1 forbids.

**What this does NOT do:** it does **not** retroactively void D6RF10. That item was registered, frozen and
run **before** this charter existed, and a charter is not applied backwards to void a completed rung —
**and voiding a rung is not in my §9 authority anyway.** R1 `GATE FAIL`, R2 `NOT A RESULT`, R3
binding-field `PASS` / rung `GATE FAIL` all stand exactly as graded.

**What it DOES do, and it is binding forward:** **no D6-family successor may register `CONV_BAR` equal to
`primalMinResTol × primalMinResTolDiff` again.** Under §1 a successor must set the solver tolerance
**strictly tighter** than whatever gate reads its output. Concretely, a successor either tightens
`primalMinResTol` (or `primalMinResTolDiff`) so the solver's acceptance sits strictly below the gate, **or
it registers a gate strictly above the solver's product** — and it may not do the second by simply
loosening the gate to fit, because §9 forbids me changing a frozen gate and `N-D43`'s escalated
acceptance-rule question is still unruled and on Sanaa's desk. **This is registered here as a constraint on
the successor, not as a change to anything already frozen.**

**And it explains something the campaign kept running into.** A gate identical to the solver's own
acceptance means the run can only ever land at the bar, never strictly inside it — which is what
D6RF7 → D6RF9 → D6RF10 measured three times over. **`N-D44` gave the mechanism; §1 gives it a name.**

### (c) One reading of mine that §6 confirms rather than corrects

§6: *"Anything an agent relays that it did not read from a file carries VERIFY."* Every VERIFY I have
placed this session was on exactly that basis, and each is now either discharged (this charter) or still
open and marked (no renderer has opened the D8R fields; the arm→row mapping rests on the grade file alone).
