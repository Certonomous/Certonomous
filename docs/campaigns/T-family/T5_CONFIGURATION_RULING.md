# T5 — CONFIGURATION RULING: the Meinders 1998 matrix, not the single cube

**Ruled by the heat-transfer supervisor, 2026-08-25. ZERO COMPUTE.** No solver
ran, no mesh was built, no case directory exists, no gate is armed and no
threshold is set by this document. **This is a direction-setting ruling that
binds the T5 pre-registration when it is written; it is not itself a
pre-registration and nothing may be launched against it.**

`T5_PREREGISTRATION_DRAFT.md` remains **UNFROZEN**, with **12 INTERPRETATIONs on
Sanaa's desk**. This ruling changes what that draft must be rewritten to say. It
does not freeze it, and it does not answer the INTERPRETATIONs, which are hers.

---

## 1. THE RULING, stated first

**T5 is built on the MEINDERS MATRIX configuration — `S_x/H = S_z/H = 4`, a
spatially periodic domain of one cube — and NOT on the single cube.**

**The refinement ratio does NOT move.** `r = 1.6` in the existing draft is sound
and is retained. The premise that it was under pressure does not survive
checking (§4).

**The cell-count ladder DOES move**, because the domain changes from a channel
with a development length to one spatial period. It must be **re-derived, not
rescaled**, and that re-derivation belongs in the pre-registration.

---

## 2. WHY THE MATRIX — the ground, which is printed fact and not preference

The decisive argument is **the inlet boundary condition**, and it is not close.

**The single cube's inlet is not synthesisable.** The oncoming flow is a
**developing turbulent boundary layer on the channel floor against a developing
LAMINAR boundary layer on the opposing wall** — asymmetric — carrying a measured
free-stream acceleration of **`dU∞/dx = 0.67 1/s`** (printed p. 123). None of
that can be constructed from a profile shape and a Reynolds number. It must be
**digitised from Figs. 5.2/5.3**, and once digitised, **the digitisation error
enters every graded row through the boundary condition** — where it is invisible
in the deviation and cannot be separated from model error. That is the worst
place in a verification chain to put an uncontrolled uncertainty.

**The matrix removes that channel entirely, by the experiment's own design.**

| printed fact | source | why it decides this |
| --- | --- | --- |
| **Regular matrix, `S_x/H = S_z/H = 4`**, 25 x 10 cubes, centre-to-centre 45 mm, cube `H = 15 mm` | printed p. 211 | one spatial period is a 45 x 45 mm footprint, 51 mm tall, containing one cube |
| **At least 15 rows were needed to make the flow fully periodic**; measurements taken **around the 18th row**, at mid-height | printed p. 211 | the measured station is *inside the periodic region*, not in the development |
| the case's usefulness *"is directly related to the **well defined periodic boundary conditions** involved which can easily be implemented in numerical simulations"* | printed p. 211 | **the experiment states its own reproducibility condition** |
| measurements are *"independent of the inflow conditions"* | printed p. 211 | **the paper itself certifies the inlet-independence** the single cube lacks |
| served as the **ERCOFTAC workshop reference dataset** — TU Delft 6–7 June 1997; UMIST Manchester 28–29 May 1998 | printed p. 211 | the configuration was *selected by a community* for numerical reproduction |
| **only one cube is heated** | printed p. 229 | one conjugate solid region against a periodic hydrodynamic field |

**A periodic streamwise/spanwise pair of boundary conditions is exact. A
digitised developing asymmetric inlet is a fitted one.** The matrix replaces the
single cube's largest uncontrolled error with a boundary condition that carries
no error at all. That is the ruling's ground, and it would hold even if the
matrix were more expensive.

**A second, independent reason, which the intake record did not draw out.**
`Re_H = 3854` is **simultaneously the matrix LDA flow-field Reynolds number and
one of the six matrix heat-transfer stations** (2851, 3348, **3854**, 4321,
4722, 5279; heat transfer spans 2380 < `Re_H` < 5280). **One build at one
Reynolds number therefore grades two independent classes of quantity — the
velocity field and the local heat transfer — against the same configuration.**
The single cube does not offer that co-location: its LDA analysis sits at
`Re_H = 4440`. For a rung whose purpose is to open the lab's first
forced-convection *and* first conjugate cell at once, co-location is worth more
than either quantity alone.

**Cost is a supporting argument only, and is explicitly NOT a measurement.** One
period is a far smaller domain than a channel plus development length, so the
cell count for equal near-wall resolution is lower. **That is an argument from
domain volume, not a measured runtime**, it is labelled as such in the intake
record's §5.7, and **it must be costed in the pre-registration before any
compute** (rule 12). Nothing here authorises a run.

---

## 3. WHAT THE RULING COSTS — stated because a ruling that names only its
   benefits is an advertisement

**The single cube's reattachment target does not come with us, and this is the
real price.**

The printed reattachment figures — `x/H = 2.4–2.5` from LDA (pp. 136–137) and
*"approximately 1.5 H downstream of the trailing face"* from oil film
(pp. 136–137) — are **single-cube measurements**. They are the draft's `G4` and
`R3`.

Two things must be said about them honestly, and neither is what the brief that
prompted this ruling assumed:

1. **"Corroborated by two independent techniques" is TRUE, but only after an
   origin conversion, and the conversion is exactly `1 H`.** `1.5 H` behind the
   *trailing* face plus the `1 H` cube is `2.5 H` from the *leading* face. The
   two techniques agree — **once the origin is fixed**. The draft already warns,
   at its own line 543, that *"reattachment quoted from the wrong origin is the
   classic way to be exactly `1 H`"* out. **The corroboration is real and it is
   one origin-convention slip away from looking like a `40 %` discrepancy.** Any
   record quoting it must state the origin.
2. **It is not gradeable in any configuration, and the reason is the paper, not
   the geometry.** The thesis states **no uncertainty** on the reattachment
   length. An experiment's band is its stated uncertainty; there is none here.
   The draft is already correct on this: **`G4` is REPORTED, never graded**
   (draft §2.4 item 3, and the row at line 587). **So the reattachment was never
   a gate row, in either configuration, and choosing the matrix forfeits a
   REPORTED diagnostic — not a graded row.** That materially lowers the price of
   this ruling, and it is the reason the ruling is comfortable.

**OPEN, and named rather than papered over:** whether the matrix chapters carry
an equivalent recirculation or reattachment diagnostic **was not established**.
The intake record's §8 item 4 states that Chapters 6 and 7 were read only through
their contents entries, and no equivalent extraction was performed for the matrix
chapter. **This is the first thing the T5 pre-registration lane must establish**,
and until it does, no record may assert that the matrix has such a target — nor
that it lacks one.

---

## 4. THE MESH LADDER — the constraint I was asked to rule on IS NOT REPRODUCIBLE
   FROM THE RECORDS, and the honest ruling is to say so

I was asked to rule on whether *"`r ≥ 1.5` with three levels below 358k cells is
mutually tight"* and whether the refinement ratio therefore has to move.

**Checked against the records. There is no `358k` figure anywhere in this
repository** — not in `T5_PREREGISTRATION_DRAFT.md`, not in the Meinders intake
record, not in the index. **The premise is not reproducible, so the tightness it
describes cannot be confirmed and the ruling it invites cannot be made on that
ground.**

What the draft actually registers, at its lines 429–435:

| ladder | levels (cells) | `r` per direction | effective ratios |
| --- | --- | ---: | --- |
| **registered** | **5.4e4 / 2.20e5 / 9.03e5** | **1.6**, in every direction *including the first wall layer* | 4.07, 4.11 |
| stretch (line 442) | 1.39e5 / 5.77e5 / 2.37e6 | — | — |

**The fine level is already 903,000 cells — two and a half times the `358k`
figure the constraint was built on.** No three-level-below-358k constraint is in
force, so nothing is mutually tight, so **the refinement ratio is under no
pressure and does not move.**

**This is the second figure in one night that a brief carried and the records do
not support** — the first being *"18 combinations"*, ruled on in
`K0d_PREREGISTRATION.md` `AMENDMENT 1` §A1.1 the same evening. Both were caught
the same way: by checking a number against the record before ruling on it rather
than after. **The pattern is worth naming**: a figure that arrives inside a
directive acquires the directive's authority without acquiring its evidence.

**AND THE RATIO WOULD NOT HAVE MOVED EVEN IF THE CONSTRAINT WERE REAL.** This is
the part of the ruling that binds regardless, so it is registered here:

**A refinement ratio is an instrument. A cell cap is a budget. When they
conflict, the budget moves.** Roache's `r ≥ 1.3` exists so that the
discretisation difference between levels dominates iterative and round-off
noise; narrowing `r` to buy cells does not save money, it **spends the validity
of the observed order** to buy it. And this lab has direct, expensive evidence
of what that costs — **its dominant failure mode on Roache triples is triples
that do not converge**:

- T3 `G3`/`G4`: `DIVERGENT` -> `STAGNANT`, observed orders **`p = 0.23` and
  `0.22`**;
- K0cG `kEpsilon`: **five of five** triples non-`CONVERGING` — `STAGNANT` on two
  quantities, `DIVERGENT` on three;
- T1b: **every** triple `DIVERGENT` or `STAGNANT` (D440), with `PASS` x4 standing
  beside them and no mesh-converged value behind it.

**Under standing rule 5 a non-`CONVERGING` triple is `NOT A RESULT` whatever its
value.** A narrower `r` makes that outcome more likely, systematically, across
every row of the ladder. **Buying a cell budget by narrowing `r` therefore risks
converting the entire rung into `NOT A RESULT` to save a few dollars on a rung
whose registered cost is `3.72–7.16 USD`** — comfortably inside the `$25`
pre-authorisation, and roughly one part in a thousand of what the two T1b L4
solvers have already spent this week. **The trade is not close. `r` does not move
to buy cells, in this rung or any successor.**

---

## 5. WHAT T5 MAY AND MAY NOT GATE ON — binding on the pre-registration

This is the most consequential section for whoever writes the prereg, and it
follows from the figures, not from the configuration choice.

**The thesis contains no tabulated `h` or `Nu` anywhere.** Its appendices are
thermal-conductivity measurements. **Every reference value must be digitised
from a figure**, and the figures are not equally digitisable.

### 5.1 The coupling that constrains everything

- **Fig. 8.24** (surface-averaged `h` vs `Re_H`, 0 → 120 W/m²K): front (o) and
  rear (△) are cleanly separated at every station, digitisable to about
  **±2 W/m²K ≈ ±3 %** at `h ≈ 60 W/m²K`. **But the cube average (◇) is NOT
  separably digitisable** — at every `Re` station the (+), (×), (□) and (◇)
  markers overprint into a single blob spanning **45–75 W/m²K**.
- **Fig. 8.26** (local `h/h̄` along paths ABCDA and ABCD) is **normalised by
  exactly that cube-averaged `h̄`**.

**Therefore: the normalisation constant of the local-`h` figure is the least
readable number in the entire figure set.** Recovering *dimensional* local `h`
requires multiplying a 3 %-digitisable profile by a constant that cannot be read
to better than a ±30 W/m²K blob.

**RULING: T5 may NOT gate on a dimensional local `h`, and may NOT gate on a
cube-averaged `h̄` read from Fig. 8.24.** A band on either would be a band on a
number that cannot be honestly read off the page, and stating one would be
manufacturing precision — the same defect class as D389, where a normalisation
reads far tighter than it is.

**T5 MAY gate on:**
- the **normalised profile shape** `h/h̄` along the paths, in the **mid-face
  plateau regions**, where the six Reynolds series collapse and digitisation is
  **±0.03 in `h/h̄`, about 3 %** — and where the paper's own stated uncertainty
  is **5 %**;
- **per-face** `h` for the **front and rear faces** from Fig. 8.24, which *are*
  separable at ±2 W/m²K;
- **surface temperature** `T_s` from Fig. 8.23, digitisable to **±0.3 °C**
  against the paper's own **0.4 °C** measurement accuracy — the one quantity
  where digitisation and measurement are the same order, so **both channels must
  be carried and neither may be neglected**.

### 5.2 Two error channels, never summed

The paper's own **5 % mid-region / 10 % edges** split (a printed propagation,
Eq. 3.19, printed p. 59) and the **digitisation** split follow the same
mid-face/edge pattern **for entirely independent reasons** — the paper's from
measurement physics, the digitisation's because **Fig. 8.26's abscissa is not
numeric**. It carries only the corner landmarks A, B, C, D, so recovering a
streamwise position requires *assuming* uniform arc-length parametrisation
between corners. In the flat mid-face regions that assumption costs almost
nothing; **at the corners, where the profiles fall from ~1.0 to ~0.2 within a few
pixels, a small abscissa error maps to a very large ordinate error.**

**RULING: the two channels are reported SEPARATELY and are NEVER summed into one
band**, and **no row is graded at or near an edge or corner.** Edge behaviour is
`REPORTED`.

### 5.3 The Nusselt degree of freedom must be pre-registered, never inherited

**The thesis does not report a Nusselt number at all** — its results are `h` in
W/m²K and `h/h̄`; `Nu` appears only in its Chapter 2 review of *other* authors'
correlations. A rung wanting `Nu = hH/λ_air` must **form** it, and **the paper
does not fix the temperature at which `λ_air` is evaluated**. With a 75 °C core,
~19–21 °C inlet and a 43–62 °C surface, the film-temperature choice is a real and
non-negligible freedom.

**RULING: that choice is the lab's, is made and frozen in the pre-registration
BEFORE any compute, and is stated with the value of `λ_air` it produces.** It is
never inherited from a secondary and never chosen after a deviation is seen.

---

## 6. What this ruling did not do

- **It froze nothing.** `T5_PREREGISTRATION_DRAFT.md` is still unfrozen and its
  **12 INTERPRETATIONs are still on Sanaa's desk**, unanswered — they are hers.
- **It costed nothing.** The matrix ladder is unregistered and the "cheaper"
  argument is from domain volume, not measurement. **No compute is authorised.**
- **It moved no gate, threshold, cap or label**, because T5 has none: nothing is
  frozen.
- **It did not establish** whether the matrix chapter carries a reattachment or
  recirculation diagnostic (§3, OPEN).
- **Nothing was sent** (rule 7).

*Ruling by the heat-transfer supervisor, 2026-08-25. Zero compute.*
