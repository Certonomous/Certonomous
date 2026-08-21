# Lessons draft — FS1/FS2 feature program. Supervisor renumbers and appends.

Placeholders `L-TBD-F*`; final numbers assigned at commit time from the tail of
`docs/LESSONS.md`. Written in the repository, not the scratchpad (L-186).

## L-TBD-F1. A 110-feature "maximal" library had rank 96 on the flow family it mattered most for

FS1 built the maximal set the doctrine asks for: Wu, Xiao & Paterson's 47
minimal-integrity-basis invariants of `{S, Omega, A_p, A_k}` under two
normalisations, eleven scalar flow markers, and Pope's five — **110 features**,
nothing selected. FS2 then measured what is actually there:

| family | rank / 110 | algebraically-zero features | condition number |
|---|---|---|---|
| ducts | **96** | **48** | 1.2e33 |
| hills | 100 | 22 | 2.2e17 |
| CBFS | 100 | 25 | 2.0e18 |
| hump | 100 | 44 | 2.8e18 |
| pooled | 100 | 12 | 3.3e17 |

**No family reaches full rank, and on the ducts nearly half the library is
identically zero.** The reason is the same one that collapses Pope's ten-tensor
basis to rank 3-4 (measured here: case means **3.006-3.987**, never above **5**):
every case in this benchmark is a statistically two-dimensional mean flow, and
high-order invariants of three or more tensors vanish.

The practical consequences are sharper than "some features are useless". A
regressor handed 110 columns on duct data is working in a space **14 dimensions
smaller than it thinks**, with a condition number of `1e33`; any L1 path,
mutual-information ranking or permutation importance computed there is
partly ranking noise directions. And a feature that is dead *here* is not dead in
general — the twelve pooled-dead invariants would revive on a three-dimensional
flow, which is exactly why a model fitted on this benchmark cannot be trusted off
it.

**Run the degeneracy audit before the selection method, not after.** It costs
minutes and it changes what the selection method is allowed to claim.

## L-TBD-F2. A relative-zero threshold across incommensurable features declared 105 of 110 features dead, confidently and wrongly

The first FS2 pass flagged a feature DEAD if its maximum absolute value fell
below an absolute floor **or** below `1e-12` times the largest value anywhere in
the feature matrix. That second clause is standard practice and it was
catastrophic here: the Pope invariants under the Durbin-bounded normalisation
reach `|lam3| = 1.5e11` and `|lam5| = 1.5e14`, so the "relative" threshold
evaluated to **150**, and every bounded feature in the library — all eleven `q`
markers, every normalised invariant, 105 of 110 — was reported algebraically
zero.

The output looked entirely plausible: a long list of feature names under a
correct-sounding heading. It was caught only because five of the names were the
`q` markers, which are bounded in `[0, 1]` by construction and *cannot* be near
zero — a sanity check that came from knowing what the features were, not from
the numbers.

**A relative tolerance presumes a common scale.** In a maximal feature library
there is deliberately no common scale — that is what "maximal" means. Use an
absolute test for "is this identically zero", a per-feature relative test for "is
this near-constant", and never a global-max normaliser across features with
different units. The corrected audit records the bug in its own output rather
than quietly fixing it.

## L-TBD-F3. A paper's Galilean-invariance proof can be correct and its steady-state implementation still not invariant

Wu, Xiao & Paterson normalise the pressure gradient by `rho |DU/Dt|` (Table 1,
p. 8) and devote Appendix C to showing the feature set is Galilean invariant.
The argument is correct — for the **unsteady** material derivative
`DU/Dt = dU/dt + U.grad U`, where the unsteady term supplies exactly the shift
that cancels the boost.

A converged steady RANS field has no `dU/dt`. The only implementable normaliser
is `|U.grad U|`, which is **not** boost-invariant. Measured on `CBFS13700` with a
boost of `0.37, -0.21, 0.13` times the mean speed: **58 of 110 features move, by
up to a relative 2.0**, and every one of them either contains `A_p` (53) or uses
the raw velocity (5).

This is not an error in the paper and it is not a bug in the code; it is a
property of the steady-state setting that the paper's proof does not cover.
Two habits follow. **Measure invariance on your own implementation rather than
inheriting the claim** — a boost and a rotation applied to one stored field cost
one script. And **when a normaliser is only invariant in the unsteady form,
either say so at the definition or drop the term**: our library keeps it and
flags all 58 by name, because a feature that is useful and non-invariant is a
legitimate choice and a feature that is silently non-invariant is not.

The measurement independently reproduces Kaandorp & Dwight's own annotation
(Table 1 footnote, p. 25): *"Features marked with dagger are rotationally
invariant but not Galilean invariant."* Their five daggered markers are exactly
the five this check flags.

## L-TBD-F4. Two audits that overlap catch each other's artefacts

The invariance check reported three features exceeding the rotation tolerance —
apparently a failure, since a trace of a rotating product is invariant by
construction. It was not. `trW2SWS2` has a maximum absolute value of **2.6e-18**
across the whole field: it is algebraically zero on a two-dimensional flow, so
the relative measure was dividing float64 roundoff by zero. The third,
`q8_kConvection` at `3.3e-12` for an O(1) feature, is at the tolerance itself.

The degeneracy audit had already flagged `trW2SWS2` as DEAD. **The FS2 result
explained the FS1 anomaly**, and neither audit alone would have resolved it:
invariance testing normalises by a scale that degeneracy testing is designed to
find is zero.

Keep the two adjacent, run them on the same library in the same session, and
**check the magnitude of anything that fails a relative test before calling it a
failure**. The general form: a relative error on a quantity that is identically
zero is not an error measurement, it is a division by zero with extra steps.

## L-TBD-F5. Three independent instruments agreed on the same case, and none of them needed a model

The NASA wall-mounted hump is out-of-family by every instrument the charter
requires, all measured before any training:

* **Mahalanobis distance** (charter 5a): **13.17%** of cells beyond the training
  p99, against 0.00-0.70% for the other seven test cases.
* **FS5 range coverage** (charter 22.5): **31.79%** of cells outside the training
  range on at least one feature, with **49 of 110** features going out of range —
  against 0.00-0.06% on the hills and 0.96-3.07% on the ducts.
* **Tensor-basis rank** (charter 5b): rank never exceeds 5 of 10 anywhere, so
  `g^(6..10)` are unconstrained the moment a flow leaves the 2-D family.

And every tensor-basis model trained on this benchmark blew up on exactly that
case, by factors of `1e2` to `1e7`.

**The instruments fired before the failure, on data alone.** That is the argument
for making them standing gates rather than post-mortem tools: three cheap,
model-free measurements identified the case that would break four different
models, and they agreed with each other.
