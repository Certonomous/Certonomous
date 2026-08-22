# Lessons draft - Wu 2018 a-posteriori lane (Lane 2). Supervisor renumbers and appends.

Headings are placeholders: final numbers are assigned by the supervisor at commit time from the tail of docs/LESSONS.md (the DAFoam team is appending the same day). Written in the repo, not the scratchpad: that
path was cleared and repopulated by an unrelated workstream three times during
this programme.

## L-TBD-W1. **MERGE INTO L-186 (already committed, 22057f59) — do not append as a second entry.** The scratchpad is not a handoff channel, and the fix is to write where the commit comes from

Three times in this programme a file under the session scratchpad was destroyed
by another agent or another workstream: `lessons_B.md` and `numerics_B.md`
overwritten by a same-role peer; `tbrf.py` overwritten and restored to a
**pre-patch** state that could not reproduce the results it was credited with;
and finally the whole scratchpad cleared and repopulated with an unrelated
workstream's files, deleting `lessons_B_opus.md` outright.

Nothing was ultimately lost, and the reason is worth stating precisely: the
content had already been **committed to the repository** by the supervisor
(`docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`). The scratchpad copies were
never the authority; they were a queue. The near-miss was the third event, where
`lessons_B_opus.md` held roughly a day of drafting that happened to have been
appended upstream hours earlier.

The rule, and it is cheap: **anything a downstream reader will need must live on
the path that reader commits from.** A scratchpad is for intermediates you can
regenerate — extracted text, intermediate arrays, logs. The moment a file becomes
the only copy of a conclusion, it belongs in the repository, even in draft. Two
corollaries: name scratch artefacts after your instance, not your role, because a
role name collides; and if a file you were *given* rather than chose is your
output channel, append, never overwrite, because someone else may be doing the
same.

## L-TBD-W2. Report the comparator you can defend, not the one that is lying around

The obvious comparator for an a-posteriori closure test is the benchmark's own
shipped baseline field. Measured here, that field is not converged to the
standard the test itself uses: restarting it with zero corrections gives an
initial streamwise-momentum residual of **1.6e-3** on `AR_1_Ret_360` and
**9.3e-4** on `AR_3_Ret_360`, because those cases stopped on a `residualControl`
listing only `k` and `omega` (`k 5e-6; omega 1e-10;`) and never constrained `U`
or `p` at all.

Scoring an injected run against that field silently credits or debits the model
with the benchmark's own convergence gap. The fix is one extra run: a NULL
configuration with zero corrections under the **identical** solver, mesh copy,
stopping rule and iteration cap, used as the comparator, with `NULL - BASE`
reported once as a named quantity so the gap is visible rather than absorbed.

The generalisation: **before using a published or shipped field as a baseline,
restart it under your own stopping rule and read the first residual.** It costs
one iteration to find out whether the number you are about to compare against
means what you think it means.

## L-TBD-W3. A gate that contains no solve cannot be invalidated by a convergence argument

Mid-task a reviewer warned that a gate of the form "zero-correction re-solve vs
the shipped field, rel-L2 < 1e-10" would fail spuriously, because the shipped
fields are not converged to 1e-10 — a correct warning, and one that had already
bitten the parallel lane.

It did not apply. The gate under review was **pure algebra on the injected
field**: reconstruct `b_total = b_RANS + bijDelta` from the shipped `nu_t`, `k`,
`S` and check it equals the model's own prediction. No solver, no iteration, no
sensitivity to convergence at all. It passed at **1.24e-16**.

Two things worth carrying. First, when a review lands, check whether it describes
the artefact you actually built before acting on it; adopting a correction to a
different design would have meant reporting a non-existent defect. Second — and
this is why the exchange was still worth having — the reviewer's *additional*
gates were genuinely better than mine at what they tested (that the corrected
solver is inert at zero correction, verified here as **bit-identical** over 200
iterations), so the right response was to keep my gate, adopt theirs, and say
plainly which tested what.

## L-TBD-W4. Register a ceiling configuration, or your model will be blamed for the injection path

This lane set out to test whether a random forest's a-priori anisotropy gain
(`b_rms` 0.4138 -> 0.2213, a clean PASS) survives being solved. The
preregistration required a **TRUTH** configuration alongside it: inject the
*exact* anisotropy `b_LES - b_RANS` and see what the solver does with a perfect
prediction. It also registered, in advance, that a TRUTH row failing to cut
`U_rms` by 50% makes the case NOT A RESULT, and that a TRUTH row *worse* than the
baseline voids every ML row.

Both fired. Injecting the true anisotropy made `U_rms` **57-63% worse** on all
three cases. Without that configuration the ML rows - `U_rms` up 57-63%, `b_rms`
down by a factor of 5 - would have read as a devastating verdict on the model.
The model was never the problem: with `kDeficit = 0`, transported `k` collapses
to a third of baseline, so the realised stress `2k(b_lin + b^Delta)` is wrong by
that factor however good `b^Delta` is.

The general shape: **when you test a component through a pipeline, put the
pipeline's own perfect-input case in the preregistration as a gate, not as a
nicety.** It costs one extra run. Without it you cannot tell "the model is bad"
from "the harness cannot express what the model produces", and the first
explanation is always the more available one. Two supporting habits: register the
threshold *before* seeing the ceiling number, so the gate cannot be argued away
afterwards; and find an independent control that isolates the harness - here, the
lab's own W2 campaign putting `b^Delta` **and** `R` through the *same solver* to
reach the published `eps(U)/eps(U_0)` = 0.00165 (the lab's own W2 measurement: 0.003331, clearing the registered < 0.005 band) [dated correction 2026-08-21: originally quoted '0.0017' as the lab's own number], which proves the path is sound and the `b`-only
configuration is what fails.

The finding that survives is sharper than the one the lane set out to get: an
a-priori `b_ij` score bounds nothing about the solved field, and a closure that
predicts `b_ij` alone cannot be propagated without either a k-correction or a
frozen `k`. That is a statement about a whole class of data-driven closures, and
it came from the control, not the treatment.
