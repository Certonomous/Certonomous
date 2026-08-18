# D3 n15 variant-lever cold reruns — PRE-REGISTRATION (filed, NOT launched)

Filed 2026-08-10T15:25Z, chief ruling 2 of the ladder dispatch. Per the instruction — "if the
pair exceeds ~25 core-min, pre-register both but run the rung first and report before launching
D3" — this is the filing; **no compute has been spent and none will be until the chief picks a
scope**, because every honest scoping exceeds the bar (prices below, from measured walls).

## 1. What is flagged and why

`WARMSTART_AUDIT.md` (9bb948b2) row 6: the D3 n15 variant-lever arms — `mgso`,
`mgso_restart1000`, `mgso_sparsify`, `noresnorm`, `noresnorm_bigbudget`, `noresnorm_cl_only`,
`noresnorm_fill1`, `noresnorm_mgso`, `noresnorm_richardson`, `sparsify`, `sparsify_fill1`
(**11 variants**, scripts on disk in `A3-onera-m6-sweep-n15_21840/`, `reports/runScript_*` n2
dirs proving each ran) — were WARM-CONTAMINATED: they ran sequentially in the one case dir
after the record run overwrote time-0 with its end state, and their logs were lost with the
interrupted session. Verdict then: formally INDETERMINATE, mechanism certain, **cold rerun
required before any future citation**.

## 2. The reframing that changes what these reruns are worth (new since the audit)

Every one of those variants was measured against a configuration now known to be broken in a
single token: they all carried `transonicPCOption: 2`, **dead code for `DARhoSimpleCFoam`**,
so each lever was being tested on top of an inactive transonic preconditioner, against a
`-5` that the token alone explains (negative control 551a7ba5, bit-for-bit). Rungs 1 and 2 now
converge and pass FD with the PC active. So a faithful cold reproduction of those nulls would
re-measure levers against a configuration nobody will run again — it would convert
INDETERMINATE rows into COLD-CLEAN rows about a dead baseline.

## 3. Three scopes, priced from measured walls — the chief picks

Price basis: measured at this exact rung with the coloring cache warm — 7.33 core-min for a
converging `compute_totals` (110 s x 4), ~28 core-min for the record's double-`-5` run (which
burns its full iteration budget before breaking down). Staged-copy pattern (guidelines §8)
means one fresh case copy per variant; cold proof = first continuity error
`0.5969274433533561`.

| scope | what it answers | price (measured basis) |
|---|---|---|
| **A. Faithful reproduction** — all 11 variants cold, unchanged (`transonicPCOption 2`) | converts the flagged rows to COLD-CLEAN or changed, about the dead baseline | 11 x ~7–10 core-min ≈ **80–110 core-min** |
| **B. Retire as superseded** — record the rows as closed-by-supersession, citing the token finding and the negative control, with no compute | costs nothing, states plainly that the nulls concern a configuration superseded by the token fix and are not to be cited | **0 core-min** |
| **C. Re-ask the question that now matters** — the same 11 levers cold ON TOP of the working config (`transonicPCOption 1`), graded on ITERATION COUNT rather than reason code | whether any lever cuts the iteration count that rung 2 measured scaling at cells^1.5–1.7 — i.e. whether the taller rungs get cheaper | 11 x ~10–14 core-min ≈ **110–150 core-min**; a 3-lever triage subset (`mgso`, `richardson`, `fill1`) ≈ **35–45 core-min** |

**Recommendation, stated as mine and reversible:** **B for the audit obligation, plus C's
3-lever triage subset if the ladder is going up.** Scope A buys bookkeeping about a dead
configuration at the price of a full rung; scope C's subset is the only version whose answer
could change what rung 3 costs — and rung 3 is priced at ~113 core-min precisely because
nothing is known to reduce its iteration count.

## 4. Pre-registered mechanics, whichever scope is picked

Staged copy per variant (never sequential reruns in one dir), `decomposePar -force` from the
pristine serial `0/`, in-log cold proof `0.5969274433533561` required before a result counts,
launcher lever echo plus the solver's own DAOption dump as the L-40 pair, setsid + `.t0/.rc/.t1`
ledger per variant, mesh already certified (`certificate_admits() == True`, verdict clean, the
n15 mesh's sweep row is `W4-m6-reordering` by points-hash dedupe). Grading: for scope A/B the
family's reason-code criteria; for scope C, iterations-to-reason-2 versus rung 1's baseline
(CD 368 / CL 383), with a lever counted as material only if it moves iterations by >10% —
pre-registered here so no lever gets credit for noise.

## 5. Status — DECIDED 2026-08-10: scope B ADOPTED, scope C triage APPROVED

Chief ruling of 2026-08-10: **scope B adopted (0 core-min)** — the 11 flagged variants are
RETIRED AS SUPERSEDED, §6 below — and **scope C's 3-lever triage approved** (35–45 core-min),
running BEFORE rung 3 because its output is instrumental to rung 3's price
(`A3_TRIAGE_LEVERS_PREREGISTRATION.md`). Scope A is declined.

## 6. RETIREMENT OF THE 11 FLAGGED VARIANTS (scope B, executed here)

**The 11 D3 n15 variant-lever arms are retired as SUPERSEDED. They are not unverified findings
awaiting a rerun; they are findings about a configuration that never ran the preconditioner.**

The reasoning, stated in full so a future reader cannot mistake retirement for avoidance:

1. Every one of the 11 arms (`mgso`, `mgso_restart1000`, `mgso_sparsify`, `noresnorm`,
   `noresnorm_bigbudget`, `noresnorm_cl_only`, `noresnorm_fill1`, `noresnorm_mgso`,
   `noresnorm_richardson`, `sparsify`, `sparsify_fill1`) carried `"transonicPCOption": 2`.
2. `2` is dead code for `DARhoSimpleCFoam`: the only live branch is `== 1`
   (`DAResidualRhoSimpleCFoam.C:173`); `== 2` exists solely in `DAResidualTurboFoam.C:176`, a
   different solver. So the transonic preconditioner was **inactive in all 11 runs**.
3. The `-5` those levers were being tested against is explained by that token alone — proven,
   not argued, by the negative control (551a7ba5): the record configuration reruns on today's
   host and reproduces the double `-5` **bit-for-bit**, while flipping the single token
   converges (rung 1, 11b90d25) and converges again one mesh up (rung 2, 4e982b4a).
4. Therefore each null means "this lever did not rescue a run whose preconditioner was off" —
   a true statement about a baseline that no future run will use. Reproducing them cold would
   convert INDETERMINATE rows into COLD-CLEAN rows **about a superseded baseline**: correct
   bookkeeping, zero forward value, at the price of a full rung.
5. The audit's requirement — *cold rerun before any future citation* — is **satisfied by never
   citing them**. Retirement is the stricter option, not the lazier one: it forecloses the
   citation the audit was protecting against, rather than licensing it with fresh logs.

What is NOT retired: the levers themselves as questions. Whether any of them reduces iteration
count **on the working (PC-active) configuration** is a live and separately valuable question —
that is scope C, approved as a 3-lever triage, and its answer is about the ladder's cost, not
about the dead baseline.
