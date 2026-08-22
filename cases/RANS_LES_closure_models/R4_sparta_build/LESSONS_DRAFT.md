# LESSONS_DRAFT — R4 SpaRTA-class build lane

**FILED — DO NOT APPEND AGAIN.** These four lessons were committed to
`docs/LESSONS.md` as **L-235, L-236, L-237 and L-238** in the order below, at
`7965d08b` (2026-08-22), the numbers taken from the tail (L-234) at commit time.

Numbers are assigned by the supervisor at commit, **from the tail of
`docs/LESSONS.md` — the maximum existing number, never a count**
(`grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1`).
Re-derive at commit time; peers commit constantly. At the time of writing the
tail was **L-231** (it was L-221 when this lane began — peers commit
constantly, which is exactly why the number is taken at commit and not now).

---

## L-<n>. A settle criterion that measures change cannot tell convergence from clipping, and the clipped field looks like an answer

The frozen-RANS extraction declares itself converged when `omega`'s initial
residual is below `1e-8` and its maximum relative change below `1e-9` for 50
consecutive iterations. On two of twenty-one hills it declared **`CONVERGED
(settle criterion) at iteration 51`** with a verification drift of **exactly
0.0** — the strongest-looking convergence in the whole set.

What actually happened is three lines above it in the log. The first `omega`
solve had an initial residual of 0.933 and was followed by `bounding omega,
min: -193215225.4 max: 762695.6 average: -50081.6`. OpenFOAM's `bound()`
replaces every negative cell with a local average; the field was flattened, and
from iteration 2 onward `omega initRes = 9.26e-18` and `max rel domega = 0` at
every single iteration. **The field stopped changing because it had been
clipped, not because it had converged**, and every mechanical completion clause
— `rc = 0`, an `End` line, a last time directory equal to the write iteration,
fields present and newer than `0/` — was satisfied.

This is the L-221 shape one layer up. L-221's lesson was that a silent no-op
returns the *unperturbed* field, which looks physical. Here a silent clip
returns a *flat* field, which looks converged. Both are failures whose output
passes inspection.

**A convergence test on `d(field)` must be paired with a test that the field was
not clipped.** The repair is one line: count the solver's own bounding
messages before the field write and refuse the run if there are any. The six
hills that genuinely converged bound `omega` **zero** times; the thirteen that
hit the backstop bound it on **all 5000** iterations. The counter separates all
three populations perfectly and costs nothing.

---

## L-<n+1>. Put an arithmetic impossibility in your gate: it is the only check that caught a scrambled design matrix

A sparse-regression pipeline ran cleanly on a tensor design matrix whose rows
had been reshaped through an intermediate `(cell, candidate, component)` shape,
so candidate row *r* and target row *r* belonged to **different cells**. It
survived: the elastic-net path, leave-one-family-out cross-validation, three
seeds returning an identical three-term model, a condition number of 4.1, and a
planted-zero control that **passed**. Every internal consistency check the
fitting code had was happy.

What caught it was the preregistered a-priori gate, which scores the discovered
model against a **constant** baseline. It returned a model whose error against
its own training target was **larger than predicting zero** — on all four
families at once. A least-squares fit cannot do that: the zero vector is in its
feasible set. The number was not a bad result, it was an impossibility, and the
fit and the 24 propagation arms already launched from it were withdrawn.

**The most valuable clause in a gate is the one whose violation is arithmetically
impossible rather than merely surprising.** A threshold tells you the model is
poor; an impossibility tells you the code is wrong. Charter §3's train-mean
baseline was written to stop closure lanes scoring against a bar a constant can
clear — it also turns out to be the cheapest bug detector in the pipeline,
because "worse than the trivial predictor on its own training data" has exactly
one explanation.

Corollary, and it is the uncomfortable half: **three seeds agreeing is not
evidence of correctness.** The scrambling was deterministic, so every seed
scrambled identically and all three agreed to the last digit.

---

## L-<n+2>. The exact degeneracy that justified an exclusion existed only in the field nobody was fitting

A preregistration excluded two library members from duct-only fits on a measured
exact collinearity: on `AR_1_Ret_180`, `T4 = -T3` to machine precision
(`||T3+T4||/||T3||` median **2.74e-17**), `I2 = -I1` identically, and a per-cell
tensor-basis rank of **exactly 3.000** on 4,000 of 4,000 cells. The measurement
was right and reproduces to four figures.

It was made on the **baseline RANS** field. The fit is done on the
**frozen-RANS** field, whose velocity is the DNS mean. There the same three
numbers are **1.28e-02**, **7.04e-05** and **3.965** — 2,132 of 2,209 cells at
rank 4. The cause is physical and was already in the lab's own record from the
other direction (L-219): a linear eddy-viscosity duct has no secondary flow, so
`S^2 + Omega^2` is isotropic and the deviatoric parts cancel exactly; the DNS
mean flow *does* have secondary motion, so they do not.

**State which field a degeneracy was measured on, because a data-driven closure
is fitted on a different one than it is evaluated in.** The rule the measurement
justified is not wrong here — it was scoped to a fit this lane never ran — but a
future lane applying it to a ducts-only frozen fit would be excluding two live
directions for a collinearity that is not there.

---

## L-<n+3>. A held-out family can tell you a selected term is worse than noise, and the selector cannot

Two planted-zero columns with a true coefficient of exactly zero — a seeded
permutation of the strongest candidate and a seeded Gaussian at the same RMS —
were appended to every design matrix. On one of four fits a **selected** term
scored **below both of them** on leave-one-family-out permutation importance:
permuting it *improved* held-out error by **−322.2** where the planted zeros
scored −1.6e−03 and −1.8e−03. The cross-family-CV elastic net had selected it
anyway.

The same control reported a second thing, which is about the method rather than
the model: **at its own cross-validated optimum the elastic net is not a sparse
selector.** It retained 15 of 20 columns *including the permuted planted zero*,
at a coefficient of 6.7e−03. A term set read off the CV-optimal coefficient
vector would have shipped noise.

**Plant the zero, and rank it — do not only check that it was excluded.** The
useful output is not "the planted column was not selected"; it is the position
of the planted column relative to the terms that *were*. Where a real term
ranks below a planted one, the selection has found structure the held-out data
does not support, and no amount of seed agreement will say so.
