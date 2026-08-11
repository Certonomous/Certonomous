# The docket — findings that are real but are not this rung's

Created 2026-08-11 by the chief supervisor, as the queue **R-CONVERGE** requires.

A rung that absorbs every new finding never closes. A rung that DROPS them is worse.
This file is the third option: a finding made outside a rung's declared scope is written
down here, with the rung it surfaced in and what would settle it, and the rung closes.

**This is a queue, not an archive.** An item leaves it by being executed or by Katie
ruling it out — never by ageing.

Rules that govern entries here:

- Every item names **where it was found**, **what it would take to settle**, and **who
  owns it** (fleet / chief / Katie).
- Items filed under **R-DEPTH** (depth-3 meta-work) stay filed unless a depth-2 finding
  falsified something published. They are marked `[R-DEPTH — filed, not executed]`.
- Items filed under **R-VALUE** are the residuals of a rung that closed as PASS WITH
  RESIDUALS. They are marked with the rung.
- No item here is a claim about the world. Where an item asserts something, it carries
  its evidence or it says it has none yet.

---

## A. Katie's — decisions the fleet cannot make

| # | Item | Where found | What settles it |
|---|------|-------------|-----------------|
| A1 | **8 transcript hits before filming.** Three acts narrate the cache, one names the solver binary, four carry internal doc paths. | Transcript sweep, 2026-08-11 | Katie's call on each: cut, reword, or accept on camera. |
| A2 | **40 core-min hump authorisation** — M1 offline + M2 negative control. Drawn from a 365 core-min list I recommend against buying as a block. | C1 lever audit | Katie authorises compute, or does not. Nothing runs meanwhile. |
| A3 | **`LAPTOP_SHOOT.md` still carries the withdrawn board claim.** It is Katie's file; the fleet does not edit it. | V15 round 5 reconciliation | Katie edits, or rules the claim stands. |
| A4 | **The auto-stop causal question.** A real code defect plus a real symptom is not a cause. Katie/Sanaa own the box's power control. | `auto-stop-ignores-control-room` | The fleet exhibits wiring, or the claim stays a candidate. |

## B. Machinery — each defect class becomes an executable check

A lesson without a check is a lesson that will recur. Owner: fleet.

| # | Item | Lesson | Status |
|---|------|--------|--------|
| B1 | **Sanctioned `sweep()` helper** — names its frame, filter and commit in its own output; cannot silently exclude; test asserts it sees a planted file inside an ignored path. Plus: re-run every standing sweep whose conclusion mattered; mark any that cannot be re-derived as **UNFRAMED**. | L-75 | **IN FLIGHT** (highest priority) |
| B2 | **Fail-false gates.** Every gate and parser answers "did the check run?" before "what did it find?", with a third verdict for unknown. Sweep all gates. | The V16 skip-is-not-agreement defect | Open |
| B3 | **Absolutes.** No absolute claim ("never", "always", "cannot") ships in a docstring, comment, report or camera surface without an executed test named beside it. Surface list derived mechanically, never enumerated. | L-76 | Open — pattern has now held four times |
| B4 | **Quoted generated numbers.** A generated figure quoted into prose carries its commit and the moment it was taken, or it is regenerated at read time. Prefer regeneration; forbid bare copies. | L-79 | Open |
| B5 | **Frames.** Every count carries frame + filter + commit. A number whose frame nobody can state is worse than no number. | L-75 | Open |
| B6 | **Shipped-helper blindness.** A check written with the same helpers as the thing it checks proves only transcription fidelity. Any load-bearing verification names its EXTERNAL referent, or declares it has none. | L-74 | Open |
| B7 | **Lever activity.** Configured is not active. Log-verified or it is not evidence. | L-40 class | Open |

## C. Memory as an audited system

| # | Item | Owner |
|---|------|-------|
| C1 | **Cold-start test, monthly.** A fresh agent with no context reaches correct current state from the durable files alone. Everything it gets wrong is a memory defect fixed **in the files**, never by explaining. First run due this week. | fleet |
| C2 | **`docs/MEMORY_ARCHITECTURE.md`** — what persists, who writes it, what dies at session end, and the cold-start reading order. | chief |
| C3 | **One home per fact.** Cross-reference; never copy. Copies drift (L-79). Supersession in place, dated — never a silent edit. | standing |

## D. Rung residuals

Filled as rungs close under R-VALUE. A rung closing here does not mean these are small;
it means they are not what that rung declared it would settle.

*(none yet — V16's closure will be the first entry)*

## E. Standing task-list items not yet executed

| # | Item |
|---|------|
| E1 | Print the 30 unprinted self-audit blind spots. |
| E2 | Fix the completion-record collector writing zero-byte `.done` files. |
