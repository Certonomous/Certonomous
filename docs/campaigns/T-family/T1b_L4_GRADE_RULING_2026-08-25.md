# T1b L4 — the pool grade, and the supervisor's rulings on it

**Date:** 2026-08-25. **Author:** heat-transfer supervisor.
**Authorisation:** Sanaa, byte-exact — *"Instruction for the heat transfer team:
You have my go. And once that is done, we can add more cases to run."*
**Lane record:** `verification/runs/T-family/T1_runs/L4_GRADE_REPORT_2026-08-25.md`.
**Graded artifact:** `verification/runs/T-family/T1_runs/gate_t1b_L4.json`.

---

## 1. THE VERDICT

**`NOT A RESULT` × 4. Zero graded rows. Zero `PASS`. Zero `GATE FAIL`. No GCI is
quotable anywhere in this rung.**

| row | Re | `Nu` at x | (m,f,x) state | order | gated by | verdict |
|---|---|---|---|---|---|---|
| X0 | 1e4 | 32.576755 | **DIVERGENT** | −0.4129 | **step (1)** — x not iteratively converged | **`NOT A RESULT`** |
| X1 | 3e4 | 73.904493 | **STAGNANT** | +0.4350 | **step (2)** — triple state alone | **`NOT A RESULT`** |
| X3 | 1e5 | 189.207411 | **STAGNANT** | +0.4217 | **step (1)** | **`NOT A RESULT`** |
| X4 | 3e5 | 457.101164 | **STAGNANT** | +0.4058 | **step (1)** | **`NOT A RESULT`** |

**All sixteen levels PLATEAUED** — worst spread `R_10k_x` at 0.0815 against a
0.2 × band threshold of 0.1758. **Plateau is not what defeated this rung.**
**Three of four x levels FAILED iterative convergence**: `R_10k_x` relative
4.832e-02 (**48 320 ×** the 1e-6 tolerance), `R_300k_x` 1.269e-04 (127 ×),
`R_100k_x` 1.954e-05 (19.5 ×). `R_30k_x` returned exactly 0.0. Every c/m/f level
converged.

**The step-(1)-before-the-triple ordering earned its keep.** Three of the four
rows are gated **before** any triple is classified. Had the triple been
classified first, the rung would have read as four `NOT A RESULT`s on grid state
— true, but it would have hidden that **three of the four finest meshes were not
iteratively converged at their own registered `endTime`**, which is the more
actionable fact and the one that determines what to do next.

**Nothing here contradicts the frozen comparator.** Its (c,m,f) verdicts are
carried beside, unchanged: `DIVERGENT` / `DIVERGENT` / `DIVERGENT` / `STAGNANT`,
orders −0.2189 / −0.1504 / −0.0585 / +0.0105. **The amended rule turned nothing
into a `PASS` and could not have** — it can only turn a `PASS` or `GATE FAIL`
into `NOT A RESULT`.

## 2. TIER — `NOT HELD`, and this one does NOT wait on Sanaa's V/P ruling

**T1b L4 is tiered `NOT HELD`.** It was gated and it returned `NOT A RESULT`;
that is not `SURVEYED`, which means ungated.

**This tiering is safe to make now precisely because no ruling on `V`/`P` can
raise it.** The `G` column fails on its own evidence — **not one triple is
`CONVERGING`** — so the rung sits at the floor whichever way the rubric question
falls. **The seven rows that DO turn on that ruling (S6, S13, S19, S22, C2, C10,
C15) remain flagged CONTINGENT and are not tiered here.**

## 3. THE §3.6 REGISTERED PREDICTION — COMPOUND, and TWO OF FOUR CLAUSES FAIL

The prediction is not the single clause it is usually quoted as. Graded whole:

| clause | verdict |
|---|---|
| `R_10k_x` NOT CONVERGED at 20 000 | **BORNE OUT**, decisively — 48 320 × tolerance |
| `R_30k_x` CONVERGED by 80 000 | **BORNE OUT** |
| `R_100k_x` CONVERGED by 80 000 | **NOT BORNE OUT** |
| `R_300k_x` CONVERGED by 80 000 | **NOT BORNE OUT** |

**Quoting only the first clause would have scored a failed prediction as a
success.** §3.6's parenthetical flagged 1e5/3e5 as *at risk*, and §4's extension
protocol was registered in advance against exactly that risk — **that is to the
pre-registration's credit and it does not convert a failed prediction into a
borne-out one.** Scored as it stands: **2 of 4.**

## 4. FOUR DEFECTS IN THE COMPARATOR — VERIFIED PERSONALLY, DOCKETED, NOT FIXED

**`analyse_t1b_L4.py` is FROZEN and is NOT EDITED.** Each of these was read by
the supervisor **as source**, and each consequence re-derived from
`gate_t1b_L4.json` independently of the lane that reported it.

1. **IT RETURNS EXIT 0 ON A RUNG WITH ZERO GRADED ROWS.**
   `return EXIT_FAIL if fails else EXIT_OK`, where `fails` counts **only**
   `GATE FAIL` rows. Four `NOT A RESULT`s and nothing graded exits **0**. **Its
   printed summary is honest — it says "0 graded rows" — but its EXIT CODE is
   not.** Any automated caller keyed on `rc` records this rung as fine.
2. **A GATED ROW'S DEVIATION IS NEVER COMPUTED.** The `NOT A RESULT` branch
   `continue`s before `verdict_amended()` runs, so `deviation_pct` is absent for
   X0, X3 and X4. **Re-derived by the supervisor from the artifact's own values:
   X0 is +5.4034 % against a 2.8437 % band — 1.90 × the band, OUTSIDE it — and
   that number appears NOWHERE in the artifact.** The three deviations a reader
   *can* see are +0.2989 %, −0.6255 % and +0.0828 %, all comfortably inside.
   **The row is correctly `NOT A RESULT` and is NOT regraded. The defect is that
   the artifact reads far rosier than the case is.**
3. **THREE OF FOUR REGISTERED FRICTION ROWS WERE NEVER EMITTED**, by the same
   `continue` — the friction row is written after it. **Only X2 (3e4) exists.**
   §3.4 registers friction as `REPORTED` at all four Reynolds numbers **as the
   attribution lever**, so three quarters of the registered attribution lever is
   missing from the artifact that records the rung.
4. **THE ROW TAGS ARE NOT STABLE IDENTIFIERS.** Line 129 registers *"Rows are
   tagged `X0..X7`"* — eight rows, 4 `Nu` + 4 `f` — and **fixes no tag-to-row
   mapping.** `tag_n` increments by **emission order**, so which row a tag
   denotes depends on how many rows were gated out. Realised here: X0 = `Nu`@1e4,
   X1 = `Nu`@3e4, X2 = `f`@3e4, X3 = `Nu`@1e5, X4 = `Nu`@3e5 — **five rows, not
   eight.** Had nothing been gated, X3 would have been `f`@3e4 and X4 would have
   been `Nu`@1e5. **Stated precisely: the claim is NOT that the tags contradict a
   registered mapping — no mapping was registered. It is that the registered
   RANGE is not realised and the scheme cannot identify a row stably across two
   gradings of the same rung.**

**Separately and neutrally:** the friction row carries `verdict: "REPORTED"`,
**outside standing rule 1's fixed vocabulary**. It **is** pre-registered (lines
128 and 210 register friction as `REPORTED`, not gated), so it was **not**
invented at grading time — but it sits in the `verdict` field where a downstream
ledger will read it as one. **Referred to verification as a vocabulary-boundary
question. It is not a defect of this rung and no fix is proposed here.**

## 5. A CLAIM OF THE LANE'S THAT DOES NOT SURVIVE MY CHECK

The lane wrote that the comparator carries no planted-zero control and that
**"no zero is load-bearing here"**, on the reasoning that five levels returned
non-zeros so the reader is demonstrably able to see them.

**The first half is right; the second half is too comfortable and is
CORRECTED.** **`R_30k_x` returned exactly `0.0` and was ruled iteratively
CONVERGED on that zero.** That is precisely the shape standing rule 3 exists for:
**a blind convergence reader returns 0.0 and reports CONVERGED — the flattering
direction, and the one failure a refusal path cannot catch.**

**What saves the verdict here is luck of the ordering, not the argument
offered:** X1 is gated at step (2) on its `STAGNANT` triple regardless, so the
zero **does not carry this verdict**. **It would carry a future one** the moment
that triple becomes `CONVERGING`.

**And the reassurance that does apply is narrower than it looks.** Yesterday's
planted-zero control exercised **`analyse_t1c.iterative_convergence` — the very
reader that gated X0, X3 and X4** — proving it not blind and not noisy: negative
arm `0.0` exactly, positive arm recovering `0.0012340000000108375` exactly and
flipping the state to `NOT_CONVERGED`. **So the reader that produced this rung's
decisive gating is the one reader in the chain that has been shown able to see a
non-zero.** But it was exercised on **`R_10k_x` only, one case of sixteen**, and
**it does not prove the reader CORRECT** — a reader that sees a difference and
then computes the wrong number passes that control unchanged. **`R_30k_x`'s zero
has not been controlled.**

## 6. WHAT THIS RUNG ESTABLISHES, AND WHAT IT DOES NOT

**Establishes:** four x cases ran to their registered `endTime` and met all six
clauses of the strict completion rule; all sixteen levels plateaued; and **on
this ladder, at these four Reynolds numbers, the (m,f,x) triples do not
converge** — orders cluster at **+0.41 ± 0.02** across 3e4/1e5/3e5, which is
`STAGNANT` by the frozen classifier and nowhere near a second-order scheme's
design order.

**Does NOT establish:** any mesh-converged Nusselt value at any Reynolds number;
any statement about the world; why the three levels failed to converge (that
needs residual history, not grading); or whether an extension would converge
them, or where. **The x values 32.58 / 73.90 / 189.21 / 457.10 are statements
about the finest mesh built, NOT about a limit.**

## 7. CONSEQUENCE — §4's EXTENSION PROTOCOL IS QUALIFIED, AND NOTHING IS LAUNCHED

**Three x cases — `R_10k_x`, `R_100k_x`, `R_300k_x` — now qualify for §4's
registered extension protocol.** **NOTHING WAS LAUNCHED.** That is compute, it
needs its own pre-registered cost, and Sanaa's pattern is **per-item approval
against a costed proposal**. It goes to her with core-minute figures derived from
**this rung's measured rates**, not from a guess — and this rung is exactly the
cautionary case, its pre-registered estimate having missed by 31 % because a
throughput rate was borrowed across a mesh-size jump.

## 8. WHAT IS NOT DONE HERE

No frozen file edited. No pre-registration amended. No verdict from the frozen
comparator moved. No tier assigned to any of the seven contingent rows. No case
selected and none launched. No send. The rung's cost calibration row is owed
under rule 12 and lands separately.
