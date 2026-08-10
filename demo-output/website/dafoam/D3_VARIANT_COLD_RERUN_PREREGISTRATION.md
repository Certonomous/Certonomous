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

## 5. Status

**FILED, NOT LAUNCHED.** Awaiting the chief's scope pick. Rung 2 came in at 99.5 core-min
against a ~47 estimate (cause diagnosed and corrected: pricing off cells when iterations scale
superlinearly), so spending 80–150 more core-min without an explicit pick would be exactly the
silent-overrun the standing rule forbids.
