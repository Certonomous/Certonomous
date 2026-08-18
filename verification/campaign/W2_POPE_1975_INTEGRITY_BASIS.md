# W2 reading well — Pope 1975, the integrity basis under both closure rungs

Date opened: 2026-08-02 (UTC). **Zero compute**: no solver, no mesh, no data.
Everything below is either read off the artifact or produced by
`sdk/scripts/pope_1975_basis_check.py`, which is pure algebra on synthetic
velocity gradients and runs in under two seconds.

Closes the gap named in `w2-pope-1975-integrity-basis` and
`w2-pope-1975-before-the-methods-that-use-it`: the ten-tensor basis that the
tensor-basis network and the sparse-regression rung both rest on had never
been read here, nor any substitute, and the lab's description of it came
entirely from those two methods papers restating it.

Provenance discipline per `docs/charters/LITERATURE_CHARTER.md` section 2.

---

## 0. The artifact, and its availability check

**S. B. Pope, "A more general effective-viscosity hypothesis", *Journal of
Fluid Mechanics* 72 (2), 331–340, 1975.** DOI `10.1017/S0022112075003382`.

**Tier: READ IN FULL.** All ten pages read this session, from
`docs/papers/pope_jfm1975_effective_viscosity_hypothesis.pdf`
(sha256 `fb366ef343a2ba60924c3836d7c80c17182e56bda8b540a6466fe336d3f98ca0`,
988,374 bytes, mtime 2026-08-01 10:19 UTC). The tensor list (p. 334), the
coefficient closure (p. 335–336) and the section 5 limit case (p. 336) were
read off the **page images**, not the OCR: the text extraction at
`..._effective_viscosity_hypothesis.txt` mangles every fraction in those
equations, and section 3 of the charter's rule about figures applies with
more force to a scanned equation than to a plotted curve.

**Availability, reported not assumed.** Unpaywall on the DOI, queried
2026-08-02 05:23 UTC: `is_oa: false`, `oa_status: closed`, zero OA locations.
The lab's copy is a scan that was placed in `docs/papers/` on 2026-08-01 and
carries **no provenance note and no git history** — it is untracked, and
`git log --diff-filter=A` returns nothing for it. That is a gap in the
record, flagged here rather than smoothed: the paper was read, and how the
copy was obtained is not written down. It is left untracked; whether a
closed-access publisher scan belongs in this repository is Katie's call, not
a night agent's.

---

## 1. Claim / source / where-it-applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The general effective-viscosity hypothesis is `a = sum_lambda G^lambda T^lambda` (3.6), equivalently `<u_i u_j> = (2/3) k delta_ij + k sum_lambda G^lambda T^lambda_ij` (3.7), with `a_ij = <u_i u_j>/k - (2/3) delta_ij` (3.1), `s_ij = (1/2)(k/eps)(U_i,j + U_j,i)` (3.2), `omega_ij = (1/2)(k/eps)(U_i,j - U_j,i)` (3.3). | Pope 1975, JFM 72, p. 333–335, READ IN FULL. | Any closure that writes the anisotropy as a tensor polynomial in a normalised strain and rotation rate. This is the equation both approved rungs implement. | It is a *representation*, not a model. Nothing in (3.6) says what the `G^lambda` are; sections 1–3 supply no closure at all. |
| **In three dimensions the basis is ten tensors and five invariants**, printed in full on p. 334: `T1 = s`, `T2 = s w - w s`, `T3 = s^2 - I{s^2}/3`, `T4 = w^2 - I{w^2}/3`, `T5 = w s^2 - s^2 w`, `T6 = w^2 s + s w^2 - (2/3) I{s w^2}`, `T7 = w s w^2 - w^2 s w`, `T8 = s w s^2 - s^2 w s`, `T9 = w^2 s^2 + s^2 w^2 - (2/3) I{s^2 w^2}`, `T10 = w s^2 w^2 - w^2 s^2 w`; invariants `{s^2}, {w^2}, {s^3}, {w^2 s}, {w^2 s^2}`. | Same, p. 334, READ IN FULL. Transcribed into `pope_1975_basis_check.py::basis_3d` and checked: all ten symmetric and traceless to 3.5e-15 relative. | Building a ten-tensor input layer. The transcription is now on disk and machine-checked, so the lab no longer takes the list from a restatement. | The isotropic subtractions differ between tensors — `1/3` in T3 and T4, `2/3` in T6 and T9 — and the check has teeth: writing `1/3` in T6 leaves `tr T6 = -3.98`, not zero. |
| **In two dimensions the basis is three tensors and two invariants**: `T0 = I_3/3 - I_2/2`, `T1 = s`, `T2 = s w - w s`; invariants `{s^2}`, `{w^2}`. | Same, p. 334, READ IN FULL. | Every 2-D family the lab runs: periodic hill, converging–diverging channel, curved backward-facing step, NASA hump, the bump. | `I_2` is the two-dimensional Kronecker delta appearing inside three-dimensional tensors; Pope defends the mixing in appendix A on the grounds that a preferential coordinate system has been chosen. It is not an isotropic tensor and does not survive an arbitrary 3-D rotation. |
| **The ten tensors and five invariants are not derived in this paper.** Appendix A, last paragraph: "The procedure is reported by Spencer & Rivlin (1959, 1960) and the results for this situation are quoted in the text." Pope derives the *two-dimensional* case himself (appendix A, from Cayley–Hamilton) and quotes the three-dimensional one. | Same, appendix A p. 339, READ IN FULL. | Attribution. The primary source for the 3-D integrity basis is Spencer & Rivlin, and Pope 1975 is a secondary source for it that says so on its own page. | Nothing here says Spencer & Rivlin are wrong or that Pope mis-transcribed them; we have not read Spencer & Rivlin (see section 4). It says our citation was one level removed and did not know it. |
| **Pope's validity domain is a high-Reynolds-number, *nearly homogeneous* flow.** Stated as the conclusion of section 2, p. 333: "for a high Reynolds number nearly homogeneous flow, the Reynolds stresses are uniquely related to the rates of strain and two independent scaling parameters, provided that all macroscales are proportional and that the boundary conditions affect only the scaling parameters." The homogeneity is *necessary*, and Pope derives why (p. 332): the triple correlation that carries turbulent transport "will be zero only when the Reynolds stresses and consequently the rates of strain are homogeneous". | Same, section 2, READ IN FULL. | The honest domain statement for any model of this form. | **This is narrower than every case in the closure challenge.** Separated and reattaching flows are the cases where transport is largest, and they are exactly the cases both approved rungs target. Neither Ling nor Schmelzer states this restriction; it is only in the primary source. |
| The coefficient closure of section 4 is model-dependent and stacks a second approximation on the first: `(4.1)`, Rodi's (1972) algebraic-stress weak-equilibrium assumption `transport of <u_i u_j> ~ (<u_i u_j>/k)(P - eps)`, applied to the Reynolds-stress equation of Launder, Reece & Rodi (1975), with `C_1 = 1.5` and `C_2 = 0.4` "suggested". Result: `a = -2 C_mu [s + g b_3 (s w - w s) + g b_2 {s^2} ((2/3) I_3 - I_2)]` (4.3), so `G0 = 4 C_mu g b_2 {s^2}`, `G1 = -2 C_mu`, `G2 = -2 C_mu g b_3`, with `b_1 = 8/15`, `b_2 = (5 - 9 C_2)/11`, `b_3 = (7 C_2 + 1)/11`, `g = (C_1 + P/eps - 1)^-1`. | Same, section 4 and p. 336, READ IN FULL. | Reading any claim that a tensor-basis closure is "derived from first principles". The derivation is first-principles up to (3.7) and model-fitted after it. | These `G` are for **two dimensions only**, and they inherit `C_1`, `C_2` and the LRR pressure–strain model. A data-driven `G^lambda` is not an improvement on these numbers; it is a different object answering the same question. |
| **Pope never determined the three-dimensional coefficients and says the 3-D form is useless.** Section 5, p. 337: the hypothesis "has the disadvantage of being restricted to two-dimensional flows. (The three-dimensional form is so intractable as to be of no value.)" | Same, section 5, READ IN FULL. | Framing both approved rungs correctly. TBNN's actual contribution is to supply, by learning, the ten `G^lambda` that Pope declined to derive — it is not "applying Pope's model" to three dimensions, because there is no such model in this paper. | Any lab sentence that reads "the ten-tensor model of Pope 1975". The ten-tensor *basis* is Pope's (quoting Spencer & Rivlin); the ten-tensor *model* is not, and does not exist here. |
| **Material indifference is explicitly rejected**, and its absence is Pope's diagnosis for a known failure. Section 3, p. 334: removing the dependence of `a` on `omega` "is unfounded in the present context" (after Lumley 1970). Section 5, p. 337: `C_mu` proposals with no dependence on the rotation invariant are "tantamount to assuming that the Reynolds stresses are materially indifferent … most likely responsible for the shortcomings of these isotropic-viscosity hypotheses in predicting flows with streamline curvature." | Same, sections 3 and 5, READ IN FULL. | The physical reason to carry `omega` at all, and a named mechanism for curvature error — useful wherever the lab reports a curved-wall or swirl discrepancy. | It is a diagnosis, not a measurement. Pope offers no curved-flow comparison in this paper; the only measured numbers he quotes are Champagne, Harris & Corrsin's homogeneous shear values. |
| Lumley's (1970) tensor polynomial is stated to be **wrong**: "In forming the tensor polynomial Lumley (1970) made illicit use of the alternating tensor density and so the result and some of the conclusions based upon it were incorrect." | Same, section 1 p. 332, READ IN FULL. | Any citation of Lumley 1970 for the basis itself. Pope corrects it. | Lumley 1970 is still the source Pope follows for the *approach* (which quantities enter, and the rejection of material indifference). The correction is to the polynomial, not to the programme. |
| The measured contrast that motivates the whole paper: Champagne, Harris & Corrsin (1970) measured, in nearly homogeneous shear, `a11 = 0.3`, `a22 = -0.18`, `a33 = -0.12`, `a12 = 0.33`; an isotropic-viscosity hypothesis predicts "at best" `a11 = a22 = a33 = 0`, `a12 = 0.33`. | Same, section 1 p. 332, READ IN FULL — Pope's quotation of Champagne et al., **not** read from Champagne et al. | The size of the normal-stress anisotropy a linear eddy-viscosity model must miss: it gets the shear stress right and the normal stresses identically wrong. Two significant figures, and no more may be asserted. | This is an INTERNAL-style hop: it is Pope's characterisation of a third paper, which the charter forbids as a *basis* of claim. Cite it as "Pope 1975 quotes Champagne et al. 1970 as measuring …", never as "Champagne et al. measured …". |

---

## 2. What the checker adds that reading alone did not

`sdk/scripts/pope_1975_basis_check.py`, 13/13 checks, exit 0, run
2026-08-02 05:22 UTC. Three of its results are not in Pope, not in Ling and
not in Schmelzer, and all three bear directly on the two approved rungs.

### 2.1 The basis is pointwise over-complete, so the ten coefficients are not identifiable from one cell

A symmetric traceless 3×3 tensor has **five** independent components. Ten
tensors evaluated at a single point therefore cannot be ten independent
directions, and the measured rank of `{T1..T10}` over 200 random
three-dimensional gradients is **exactly 5, every time**. In two dimensions
it is **exactly 3**, matching Pope's own count.

Consequence, stated plainly: `a = sum G^lambda T^lambda` at one cell is five
equations in ten unknowns. The ten `G^lambda` are only pinned down because
they are *functions of the five invariants shared across cells* — the
identifiability lives in the regression across the flow, not in the
representation. A per-cell inversion for ten coefficients is ill-posed by
construction, and would return whatever the regulariser prefers.

### 2.2 The exact two-dimensional reduction table, and two coefficients that are never trained

Pope says there are three independent tensors in two dimensions. He does not
print how the ten collapse onto them. Derived here and checked to 5.4e-16
relative over 300 random 2-D gradients:

| | reduction on any two-dimensional flow |
| --- | --- |
| `T3` | `-{s^2} T0` |
| `T4` | `-{w^2} T0` |
| `T5` | **identically zero** |
| `T6` | `{w^2} T1` |
| `T7` | `-{w^2} T2 / 2` |
| `T8` | `{s^2} T2 / 2` |
| `T9` | `-{s^2}{w^2} T0` |
| `T10` | **identically zero** |

So on a 2-D flow a ten-coefficient model has exactly three effective
coefficients,

```
G0 = -{s^2} g3 - {w^2} g4 - {s^2}{w^2} g9
G1 =  g1 + {w^2} g6
G2 =  g2 - {w^2} g7 / 2 + {s^2} g8 / 2
```

and **`g5` and `g10` multiply identically zero tensors: they receive no
gradient from the loss and are unconstrained by any amount of
two-dimensional training data.** Seven of the ten output degrees of freedom
are unidentified — two absolutely, and five more only in the three
combinations above.

Where this bites: a network trained on 2-D families and then evaluated on a
square duct is using `g5` and `g10` — which the training never touched — on
the exact tensors that carry a duct's secondary flow. Ling states only the
symptom ("b13 and b23 … are identically zero in this 2-D test case").
Schmelzer restricts to three tensors and two invariants and is therefore
honest by construction, at the price of not representing a duct at all. This
table is why those two positions are not substitutes, expressed as algebra
rather than as a preference.

### 2.3 The conventions, read off both sources rather than one

Both sides of this are now READ IN FULL, so nothing here is a hop through our
own extraction.

**The ten tensors are identical between the two papers.** Ling's Eq. 2 lists
`T(1) = S`, `T(2) = SR - RS`, `T(3) = S^2 - I·Tr(S^2)/3`, `T(4) = R^2 -
I·Tr(R^2)/3`, `T(5) = RS^2 - S^2R`, `T(6) = R^2S + SR^2 - (2/3)I·Tr(SR^2)`,
`T(7) = RSR^2 - R^2SR`, `T(8) = SRS^2 - S^2RS`, `T(9) = R^2S^2 + S^2R^2 -
(2/3)I·Tr(S^2R^2)`, `T(10) = RS^2R^2 - R^2S^2R`, and the five invariants
`Tr(S^2), Tr(R^2), Tr(S^3), Tr(R^2S), Tr(R^2S^2)`. Term for term, that is
Pope's p. 334 with `S` for `s` and `R` for `omega`. Our transcription is
therefore checked against two independent printings, not one.

**The object they multiply is not identical, and the difference is a factor of
two.** Pope (3.1) is `a_ij = <u_i u_j>/k - (2/3) delta_ij` and his (3.6) is
`a = sum G^lambda T^lambda`. Ling's own text, p. 6 of the manuscript, prints
`b_ij = u'_i u'_j / 2k - (1/3) delta_ij` and his Eq. 1 is `b = sum g^(n) T^(n)`
over the same ten tensors. **`a = 2b` exactly**, so `g^(n)` is half Pope's
`G^lambda` for the same flow. Assembling Pope's tensors and regressing them
onto `b` is not wrong, but the resulting coefficients are not Pope's and must
never be compared to (4.3)'s `G0, G1, G2` without the factor.

**And the strain-rate convention is not printed at all — an omission, which
section 3 of the charter says is a finding.** Ling states only that `S` and `R`
were *"non-dimensionalized using the turbulent kinetic energy k and the
turbulent dissipation rate ε as suggested by Pope [5]"*. There is no equation
defining either tensor anywhere in the manuscript, and no explicit factor, so
Pope's `1/2` in (3.2) and (3.3) has to be assumed rather than read.

That assumption is not a small one, because **Pope's tensors are of mixed
degree**. Dropping the `1/2` sends `s -> 2s` and `omega -> 2omega`, and the ten
tensors then scale by

`[2, 4, 4, 4, 8, 8, 16, 16, 16, 32]`

for `T1` through `T10`, while the five invariants — which are the network's
*input* features — scale by `[4, 4, 8, 8, 16]`. Verified in the checker.
**A convention error here is not one constant that a fitted coefficient
absorbs.** It is a different factor on each of the ten coefficients and a
simultaneous rescaling of every input the model reads, and a model trained
under one convention and evaluated under the other is wrong in a way no single
number repairs. Recorded before either rung is built, which is the whole point
of reading the basis first.

### 2.4b One published sentence that our record inherited, and that the primary source contradicts

Ling, manuscript p. 6, immediately before Eq. 2:

> "Pope [5] **gave a detailed derivation** of these 10 tensors, T(1), ...,
> T(10) and 5 invariants λ1, ..., λ5, which are listed below"

and, just above it, *"Pope [5] has previously derived the relevant integrity
basis."*

Pope, appendix A, p. 339, in full:

> "The procedure used in two dimensions is also applicable to three dimensions.
> The procedure is **reported by Spencer & Rivlin (1959, 1960)** and the results
> for this situation are **quoted in the text**."

Pope derives the two-dimensional case himself and quotes the three-dimensional
one. The detailed derivation Ling attributes to him is in Spencer & Rivlin.

This is not a defect in Ling's method and it changes none of his numbers. It is
recorded because our own `CLOSURE_METHODS.md` inherited the attribution from
this sentence, which is the literature charter's section 4 hazard verbatim —
*"another paper's characterisation of a third paper. The last one is the most
tempting and the most common way a wrong number propagates."* Here it
propagated an attribution rather than a number, and it was caught by the cheapest
possible means: reading the cited paper's own appendix.

### 2.4 Two results that were only assumed, now proved

- **Pope's section 5 limit case is reproduced exactly** from the
  transcription: assembling `a = G0 T0 + G1 T1 + G2 T2` for the simple shear
  flow and comparing against the five component expressions printed on p. 336
  gives a maximum difference of **4.4e-16** over 200 random
  `(G0, G1, G2, k/eps, U_1,2)`. That is an independent check that (3.1)–(3.3),
  `T0`, `T1` and `T2` were all transcribed correctly, with no free parameter
  to absorb an error. Charter section 6 trigger 4 — the paper's own limit case
  checked at zero compute — fired and passed.
- **The duct-degeneracy premise is an exact identity, not a numerical
  coincidence.** The open proposal `closure-duct-tensor-basis-carrier` states,
  from eight duct cases, that the third and fourth invariants are zero, the
  second is the negative of the first, and the fifth is `-lambda1^2/2`. For
  *any* unidirectional field — which is exactly what a fully developed duct or
  channel baseline is — `lambda2 = -lambda1`, `lambda3 = lambda4 = 0` and
  `lambda5 = -lambda1^2/2` hold to **0.0e+00** residual, analytically. The
  proposal's premise is confirmed and strengthened: it is not a property of
  those eight solves, so it cannot be escaped by solving them better, and
  five of seven scalar inputs carry one independent number on any
  unidirectional baseline whatsoever.

### 2.5 The duct, where this stops being an abstraction — and one correction to a lab record

The tensor-basis rung's demonstration case is a square duct, and this lab's own
record says of it: *"The duct is three-dimensional and its secondary flow is the
whole point; all ten of Pope's tensors are live"*
(`W2_TBNN_SPARTA_READING.md`). That sentence is about the **output** — the true
anisotropy does need more than three tensors to be written down. It is not true
of the **input**, and the input is what the basis is built from.

A linear-eddy-viscosity RANS solve on a straight duct produces **exactly zero
secondary flow** — measured here, not assumed, in
`closure_challenge_duct_anisotropy_expressivity.json` — so its mean field is
`U = (u(y,z), 0, 0)` and its velocity gradient has one non-zero row. Note this
is *two* shear components, `du/dy` and `du/dz`, not the single-component simple
shear of Pope's section 5; the results below are checked on the two-component
field, over 500 random gradients.

**Already known here, and credited rather than re-claimed.** That the third and
fourth invariants vanish identically on such a field is proved in the duct
expressivity audit, analytically over 50,000 random shear pairs and confirmed at
3.3e-14 and 1.1e-14 on 41,971 real duct cells. Nothing below re-derives it.

**Correction to that record.** The audit concludes *"Effective feature count for
this flow family is 5, not 7."* It is **3**. The audit named the two invariants
that vanish; it did not name the two that are *determined*. `lambda2 = -lambda1`
exactly and `lambda5 = -lambda1^2/2` exactly, both to 0.0e+00 and 3.1e-16
relative here — and both are visible in the audit's own published correlation
table, where every single Pearson `r` against `I2_W2` is the exact negative of
the one against `I1_S2` (0.1043 / -0.1043, 0.2125 / -0.2125, -0.2763 / 0.2763,
-0.0283 / 0.0283, 0.3940 / -0.3940, 0.4330 / -0.4330). Of the five Pope
invariants only `lambda1` is independent on a duct baseline, so the seven-feature
set carries `lambda1`, `Re_y` and `tke_ratio`: **three independent numbers, not
five**. The open proposal `closure-duct-tensor-basis-carrier` reached the same
count from eight duct solves; this is its analytic form.

**New here, and on the tensor side rather than the feature side.** All prior
work on this asks whether the scalar features *correlate* with the anisotropy.
This asks whether the tensor basis can *reach* it, which is a rank question and
has a harder answer:

- **The pointwise rank of `T1..T10` on a duct baseline is exactly 3**, over 500
  random two-component gradients. The velocity gradient has one non-zero row, so
  it is a rotation away from plane shear and the basis degenerates exactly as it
  does in two dimensions. `T5` and `T10` are identically zero, so **`g5` and
  `g10` have no effect on a duct baseline either** — the two coefficients that
  2-D training cannot constrain are also the two the duct cannot exercise.
- **A two-dimensional subspace of anisotropy is unreachable by any values of the
  ten coefficients.** Singular values of the ten tensors at a representative
  point: `[5.474, 3.448, 2.235, 5.8e-16, 3.1e-16]` — rank 3 with a clean gap.
- **One of the two unreachable directions is a pure cross-plane tensor**, with
  zero streamwise row and column to 4.7e-16. That is the component family
  associated with secondary flow of the second kind. The other is pure
  streamwise shear.

Stated carefully, because the physics reading and the algebra are different
claims: the algebra says a 2-D subspace including a purely `y-z` direction
cannot be produced. The inference that this is *the* mechanism of Prandtl's
second-kind motion is an interpretation, and the audit's own targets — `b_yz`
and `b_yy - b_zz` — are the lab's existing name for that direction.

**What it does not say.** It does not say a tensor-basis model cannot fix a
duct. A predicted anisotropy fed back into a solver generates secondary flow,
after which the baseline is no longer unidirectional and the basis is no longer
rank-deficient — the degeneracy is a property of the *first* iterate, not of the
method. It does say that a purely **a priori** evaluation on a converged LEVM
duct baseline, which is what the approved
`w2-tbnn-duct-reynolds-generalisation` gate specifies, is scored inside a
representation that is rank 3 out of 5 at every cell.

---

## 3. Charter section 6 — which trigger fired

- **Trigger 4 (limit case checkable at zero compute): FIRED.** Section 2.4;
  the paper's own section 5 result reproduced to 4.4e-16. Also section 2.2,
  the 2-D reduction, and section 2.1, the rank count.
- **Trigger 2 (admissibility expressible as thresholds): FIRED.** Two
  proposals filed below.
- **Trigger 1 (a number on a case we can build): did not fire.** Pope reports
  no case, no geometry and no graded quantity. The only measured numbers in
  the paper are quoted from Champagne, Harris & Corrsin (1970) for
  homogeneous shear, which is not a case this lab meshes, and figure 1 is a
  `C_mu` contour map with no flow attached.
- **Trigger 3 (disagrees with one of our results): did not fire.** Pope
  states no result of ours' kind. The nearest thing is a disagreement in
  *framing* — the record here described a "ten-tensor model of Pope 1975" —
  and that is corrected in place rather than run as an experiment.

---

## 4. Library list, and one correction to a citation year

**Spencer, A. J. M. & Rivlin, R. S. — the actual primary source for the
three-dimensional basis — is PAYWALLED and goes on the library list.**
Nothing here is asserted from it; it has not been read, at any tier.

Unpaywall, 2026-08-02 05:23 UTC:

| Reference | DOI | Unpaywall | Note |
| --- | --- | --- | --- |
| "The theory of matrix polynomials and its application to the mechanics of isotropic continua", *Arch. Rational Mech. Anal.* **2**, 309–336 | `10.1007/BF00277933` | `is_oa: false`, `oa_status: closed`, 0 OA locations | Pope's reference list gives the year as **1959**; the Crossref record gives **1958**. Volume and page range match Pope exactly. |
| "Further results in the theory of matrix polynomials", *Arch. Rational Mech. Anal.* **4**, 214–230 | `10.1007/BF00281388` | `is_oa: false`, `oa_status: closed`, 0 OA locations | Pope's reference list gives **1960**; Crossref gives **1959**. Volume and page range match Pope exactly. |

`link.springer.com` returns a 303 to the Springer identity provider for the
first DOI, which is the paywall answering. Both discrepancies are recorded,
not resolved: the year is read off Pope's own reference list in one column
and off the Crossref record in the other, and the lab should cite whichever
artifact it actually reads. This is exactly the failure mode the charter's
"a citation carried forward from another of our own documents" clause
describes, caught before it propagated.

**Does the paywall block anything?** No. Pope prints the ten tensors and the
five invariants in full, the transcription is machine-checked against the
properties they must have, and the 2-D case — the one Pope derives himself —
is reproduced exactly. Spencer & Rivlin would supply the *derivation*, which
would let the lab verify completeness rather than assume it. Nothing approved
is blocked on it, so it is a library-list row and not a blocker.

---

## 5. What this reading changes in the record

1. `docs/research/CLOSURE_METHODS.md` line 149 calls the basis "Pope 1975's
   tensor-polynomial construction". Accurate for 2-D; for the ten-tensor 3-D
   set it is Spencer & Rivlin's construction, quoted by Pope. Correction
   filed, not silently edited, since that file is in use by another hand.
2. Nothing in the lab's record stated Pope's homogeneity restriction. Every
   case both approved rungs target violates it. That does not forbid the
   rungs — a representation can be used outside the domain in which it was
   argued, and the whole data-driven programme is a bet that it can — but it
   is now the fourth column of the row, and a result that transfers badly to
   separated flow has a named prior reason.
3. The in-sample question does not arise for anything in this document. There
   is no training set: every number here comes from the paper or from algebra
   on synthetic gradients. `sdk/scripts/pope_1975_basis_check.py` reads no
   benchmark case and fits nothing.

---

## Related

- `sdk/scripts/pope_1975_basis_check.py` — the transcription and its 13 checks.
- `demo-output/website/campaign/W2_TBNN_SPARTA_READING.md` — the two methods
  papers that rest on this basis.
- `docs/research/CLOSURE_METHODS.md` — the taxonomy this corrects.
- `docs/charters/LITERATURE_CHARTER.md` — sections 2, 3, 6, 7.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/pope_jfm1975_effective_viscosity_hypothesis.pdf` | `docs/papers/turbulence_models/pope_jfm1975_effective_viscosity_hypothesis.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
