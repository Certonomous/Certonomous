# W3 — every guard that holds a ladder, swept over the whole corpus

Item: `w3-every-guard-that-holds-a-ladder`. Run 2026-08-01. **No compute**:
every rung in this file was already solved, and the work is arithmetic over
records that already exist. Measured cost 0.0 core-minutes, no ranks, no cells
per rank.

Machine-readable companion: `W3_GUARD_SWEEP.json`, written by refitting every
ladder in this tree through `chief_engineer.uq.eca_hoekstra_band` and reading
each verdict through `uq.guards_holding` and `uq.reportable_band`. The writer
asserts that every curriculum record reproduces its own stored `guards_failed`
and `conclusive` exactly; it does, on all nine fitted studies.

---

## 1. The sweep

**Twenty five ladders.** The ten curriculum studies, the five act ladders at
the precision the acts themselves fit, eight three-rung windows across the two
TMR verification cases, and the two windows of the Ahmed ladder measured on a
constant refinement ratio.

`p` and the extrapolated value are the fit's own. **Narrated** is the guard the
surface stated before this item; **binding** is every guard that independently
holds the ladder. They agree on nineteen and disagree on six.

| ladder | rungs (cells) | p | extrapolates to | binding guards | narrated | agree |
| --- | --- | --- | --- | --- | --- | --- |
| supersonic wedge, shock angle | 1 800 / 7 200 / 28 800 | 0.034 | **−15.753 deg** | order_window **+** extrapolation_sanity | order_window | **no** |
| naca0012 wing, Cd | 27 265 / 67 356 / 140 580 | 3.173 | 0.003359 | order_window **+** increment_trend **+** extrapolation_sanity | order_window | **no** |
| naca4412 wing, Cd | 27 237 / 67 826 / 137 569 | 10.467 | 0.021000 | order_window **+** increment_trend | order_window | **no** |
| B-52, Cd | 193 880 / 255 358 / 330 950 | 2.253 | 0.064842 | increment_trend **+** extrapolation_sanity | increment_trend | **no** |
| Ahmed 35 deg, Cd | 20 425 / 45 813 / 79 778 | 3.169 | 0.073929 | order_window **+** extrapolation_sanity | order_window | **no** |
| Ahmed constant ratio, c1/c2/c3 | 79 439 / 144 240 / 254 911 | 0.175 | **−0.084479** | order_window **+** extrapolation_sanity | order_window | **no** |
| Ahmed 25 deg, Cd | 20 621 / 45 753 / 79 439 | 1.950 | 0.073276 | extrapolation_sanity | extrapolation_sanity | yes |
| naca0015 sail, Cd | 63 920 / 156 089 / 243 929 | 1.696 | 0.005059 | extrapolation_sanity | extrapolation_sanity | yes |
| motorBike, Cd | 14 714 / 66 302 / 353 688 | 7.298 | 0.420091 | order_window | order_window | yes |
| cube, Cd | 53 861 / 103 934 / 299 493 | none | none | monotone | monotone | yes |
| aortic valve | not meshes | none | none | not_a_discretization_ladder | not_a_discretization_ladder | yes |
| airliner wing | no numerical channel on the record | | | | | yes |
| supersonic cone, shock angle | 1 800 / 7 200 / 28 800 | 0.800 | 26.223 deg | extrapolation_sanity | extrapolation_sanity | yes |
| diamond airfoil, wave drag | 2 000 / 8 000 / 32 000 | 6.296 | 0.036237 | order_window | order_window | yes |
| hypersonic cylinder, standoff | 1 000 / 4 000 / 16 000 | none | none | monotone | monotone | yes |
| cylinder vortex shedding, Strouhal | 2 496 / 5 032 / 8 640 | 2.430 | 0.167215 | extrapolation_sanity | extrapolation_sanity | yes |
| Ahmed constant ratio, c2/c3/c4 | 144 240 / 254 911 / 454 691 | none | none | monotone | monotone | yes |
| TMR flat plate Cd, 816/3 264/13 056 | | 1.083 | 0.0028817 | extrapolation_sanity | nothing narrates it | yes |
| TMR flat plate Cd, 3 264/13 056/52 224 | | 1.259 | 0.0028724 | extrapolation_sanity | nothing narrates it | yes |
| TMR flat plate Cd, 13 056/52 224/208 896 | | 1.634 | 0.0028670 | **none, it certifies** | nothing narrates it | yes |
| TMR flat plate cf, 816/3 264/13 056 | | 1.031 | 0.0027205 | extrapolation_sanity | nothing narrates it | yes |
| TMR flat plate cf, 3 264/13 056/52 224 | | 1.111 | 0.0027159 | extrapolation_sanity | nothing narrates it | yes |
| TMR flat plate cf, 13 056/52 224/208 896 | | 1.528 | 0.0027086 | **none, it certifies** | nothing narrates it | yes |
| TMR bump Cd, 3 520/14 080/56 320 | | 0.545 | 0.0036761 | extrapolation_sanity | nothing narrates it | yes |
| TMR bump cf, 3 520/14 080/56 320 | | 0.963 | 0.0060238 | extrapolation_sanity | nothing narrates it | yes |

**No verdict moved.** `uq.reportable_band` returns the same answer on every one
of the twenty five, before and after: a figure on the two finest TMR triples
and `None` on everything else.

## 2. The six mismatches, and what each one was telling a viewer

A ladder failing several guards while narrating one of them tells a viewer
something true and unimportant in place of something true and decisive. Every
one of these six invited the same wrong conclusion: *fix that one thing and the
ladder settles.*

* **The supersonic wedge** said its observed order was outside the credible
  window. Correcting the order alone would not have moved it: the same ladder
  extrapolates its shock angle below zero.
* **The NACA 0012 wing** fails three guards and named one. Its increments grow
  under refinement AND its extrapolated drag lands at 0.003359 against a
  working value of 0.012053, which is 27.9% of it.
* **The NACA 4412 wing** and **the Ahmed 35 degree body** each fail two and
  named one.
* **The B-52** named the growing increments, which is the earlier failure in
  precedence, and did not mention that the ladder also extrapolates outside
  everything it measured, by 247.4% of its own fit triple's range width.
* **The Ahmed ladder measured on a constant refinement ratio** named the order
  window and did not name that its extrapolation is a negative drag
  coefficient.

## 3. Two extrapolations are not merely outside a range, they are impossible

| ladder | extrapolates to | why no flow can produce it |
| --- | --- | --- |
| supersonic wedge, shock angle | **−15.753 deg** | a shock stands ahead of the wedge at a positive angle |
| Ahmed constant ratio, c1/c2/c3 | **−0.084479** in Cd | a body in a uniform stream with no power source cannot make thrust |

These are strictly stronger statements than "the observed order is outside the
credible window". An order is a judgement about a fit and can be argued about;
a negative shock angle cannot. **So an impossible value now leads the sentence
on every surface that states one**, ahead of every other guard, and it replaces
the generic extrapolation clause rather than being said twice beside it.

The check cannot live in the uncertainty layer, because that layer has no way
to know what any functional means. Each act states its own functional's
physical domain and its own reason: the wedge and the cone that a shock angle
is positive, the diamond and the geometry study that a drag coefficient below
zero is thrust with no source, the hypersonic cylinder that a standoff below
zero stands the bow shock inside the body, the vortex shedder that a shedding
frequency is positive. One of the six states a value outside its domain today,
the wedge. The rail is in place on all six either way.

## 4. What the surfaces say now

`uq.not_conclusive_reason` returned the first failure in `GUARD_PRECEDENCE` and
nothing else. It now names every guard the fit recorded as failing, in
precedence order, with the impossible-value clause first when the caller
supplied one. `uq.guards_holding_note` is the companion sentence, and it is
silent unless more than one guard binds.

The wedge, on camera:

> • The shock angle moved 2.895 deg across the three rungs, and no band is read
> from that spread.
> • The ladder is not conclusive: the shock angle the ladder extrapolates to is
> minus 15.753 deg, which is not a shock angle any flow can have, and the
> observed order p = 0.034 falls outside the credible range 0.5 to 2.5.
> • Two guards hold this ladder back independently, so correcting either one
> alone would not move the verdict.

A single-guard ladder reads exactly as it did. That is asserted rather than
asked for.

## 5. Two things the sweep found that it was not looking for

**The published extrapolated wedge angle was fitted from rounded rungs.** The
two-dimensional ladder refit reports −13.733 degrees; the act's own fit on its
own solved rungs gives −15.753. At an observed order this close to zero the
extrapolation amplifies the finest increment by 42.25, so rounding the rungs at
the third decimal moves the answer by 2.02 degrees. The correction is recorded
in `W3_2D_LADDER_REFIT.md` §4a with both readings and neither withdrawn. Same
guards, same verdict, different digit. The same caution applies to the other
four acts' orders, which move in the third decimal and change nothing.

**Eight TMR ladders carry a guard record that no surface reads.** Six of the
eight fail `extrapolation_sanity` and two certify, and the verification page
narrates none of it. That is not a mismatch, because nothing is narrated to
mismatch, and it is not this item's fix. It is the obvious next one.
