# W3 — the NACA 0012's published verdict does not survive its own mesh

**2026-08-02 06:36 UTC. No new compute.** Both numbers below were solved
earlier tonight under `agp-e71b0542e6f9` and
`w3-a-ladder-refined-below-its-own-mesh-noise`; nobody had put them beside the
credential.

---

## 1. The credential

`demo-output/website/wall/wall.json`, row `naca0012_wing`:

* measured C_d **0.01205**, 140 580 cells, tier SOLVER-BACKED;
* reference **0.009**, Abbott & von Doenhoff, *Theory of Wing Sections*
  (1959), NACA 0012 section data;
* `relative_error` **0.3393**;
* stated reason: *"measured C_d 0.012 is 34% from Abbott & von Doenhoff … C_d
  0.009, **outside the ±30% band**"*;
* area basis planform, "already on the reference's planform-area basis", so
  the comparison is direct and no rebasing is involved.

## 2. The same credential on four meshes built to the same recipe

**Extended 06:40 UTC**: §5 called two more replicates the cheapest
decision-relevant experiment left, at ~3 core-minutes each. They were run.
**All four converged on `residualControl`.**

| | background divisions | cells | Cd | converged | 2σ | vs reference 0.009 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **r1** — the published mesh | (33 60 20) | 140 545 | **0.012052229** | 153 iters | 5.45 × 10⁻⁷ | **+33.91%** | **OUTSIDE** ±30% |
| **r1b** | (34 59 21) | 139 621 | 0.009453575 | 149 iters | 2.02 × 10⁻⁷ | +5.04% | INSIDE |
| **r1c** | (32 61 21) | 127 857 | 0.010630335 | 157 iters | 3.09 × 10⁻⁷ | +18.11% | INSIDE |
| **r1d** | (35 58 20) | 135 601 | 0.009605314 | 149 iters | 1.47 × 10⁻⁶ | +6.73% | INSIDE |

**One of four is outside the band, and it is the one the wall publishes.**
n = 4: mean 0.010435363, range 2.5987 × 10⁻³ (21.6% of the published value),
sample standard deviation 1.1979 × 10⁻³. The published mesh is the **maximum**
of the four, +1.35σ from the sample mean.

**The spread is not a refinement effect, and the direction proves it.** The
cell counts span 127 857 to 140 545, a 10% range — and this ladder's own trend
is Cd *falling* with refinement (0.012052 → 0.010406 → 0.008479 as cells go
140k → 224k → 358k). The published mesh is the **finest** of the four and
gives the **highest** drag, which is the opposite of the trend. A coarser mesh
giving a lower Cd cannot be explained by resolution.

r1 reproduces the stored production rung's Cd of 0.012053 to **7.7 × 10⁻⁷**,
so it *is* the published solve. The two cases were verified byte-identical by
`diff -r` on `system/` and `0.orig/` and by md5 on the STL — **the only line
that differs in either case is the `hex (…)` division triple.** Both converged
on `residualControl` at 1e-4 and both are settled to 2σ below 6 × 10⁻⁷, which
is three to four orders of magnitude below the difference between them.

**Scatter 2.5987 × 10⁻³ — 21.6% of the published drag.**

## 3. What this means, stated carefully

**The row's verdict is not reproducible.** The sentence the wall prints —
"outside the ±30% band" — is true of one mesh and false of another mesh built
to the same recipe at the same resolution by the same generator, with both
solves converged and settled.

**This is not grounds for upgrading the row, and it must not be read as one.**
A verdict moving toward agreement deserves more scrutiny than one moving away,
not less, and the honest reading here damages *both* verdicts equally:

* it does not show the NACA 0012 agrees with Abbott & von Doenhoff to 5%;
* it does not show it disagrees by 34%;
* it shows that **this mesh family cannot resolve the difference between those
  two statements**, because mesh construction alone moves the answer by 21.6%
  of its own value while the entire question is whether it is 30% off.

The correct consequence is that the row should not state a verdict its evidence
cannot support — not that it should state a better one.

## 4. Where this leaves the numbers already on the record

Nothing measured tonight is withdrawn, and one thing is put in proportion.

The 0012's published **envelope** of ±0.015 is 17.3% of the mesh scatter's own
size — that is, the envelope is 5.8× *wider* than the scatter, so the scatter
sits comfortably inside it. `W3_PUBLISHED_RUNG_REPLICATES.md` §3 found the same
for the Ahmed 25° (19%) and the NACA 0015 sail (7%). **All three envelopes are
conservative against mesh scatter.**

But the 0012's envelope is also **125.45% of the value it decorates**, and that
is the point: an envelope larger than its own quantity will contain almost
anything, including a 21.6% mesh scatter. Passing that check is weak evidence,
and it is recorded as weak.

The **verdict** is the thing that fails, and the verdict is the part of the row
a reader acts on.

## 5. What should happen

Not decided here. This is evidence for the open ruling
`w3-a-declined-ladder-still-publishes-an-envelope`, which already covers this
row, and the ruling now has a second and sharper question to answer than the
one it was filed with:

1. the one it was filed with — may a credential print an envelope taken from a
   ladder the certifier declined? The 0012's ±0.015 at 125.45% of its value is
   the worst instance;
2. **the one this file adds — may a credential print a pass/fail verdict
   against a reference when an independently generated mesh at the same
   resolution moves the measured value across the boundary?**

The second is the more consequential, because the envelope is decoration on a
row whose headline is the verdict.

**The experiment this section originally proposed has been run** — see §2. It
asked whether 0.01205 or 0.00945 was the outlier. **The answer is 0.01205, the
published one.** Four meshes give 0.009454, 0.009605, 0.010630 and 0.012052;
three cluster between 0.0095 and 0.0106 and the published mesh sits alone at
the top, +1.35σ from the mean and the only one of four that fails the band.

That sharpens §3 rather than softening it. It is now not merely that the
verdict is irreproducible — it is that **the mesh the credential was built on
is the least representative of the four**, and it is the one whose reading
produced the failing verdict on the wall.

**It still does not license an upgrade.** n = 4 is four, the sample standard
deviation of 1.1979 × 10⁻³ is 11.5% of the mean, and a mean of four
arbitrarily chosen meshes is not a converged answer either — it is four
readings of a quantity this family cannot pin down. What it licenses is
removing a verdict, not replacing it with a better one.

**What would be worth running next, and was not:** the same four-mesh spread at
the 358 430-cell resolution, where the measured mesh scatter is 4.064 × 10⁻⁴
rather than 2.599 × 10⁻³ — a sixth of the size. If the spread there is small
enough to place the body cleanly inside or outside the ±30% band, the
credential has a resolution at which it can honestly be stated, and the
question becomes which mesh to publish rather than whether to publish a verdict
at all. About 20 core-minutes at 4 ranks on tonight's measurement.

## 6. Provenance

* r1: `/home/ubuntu/certonomous-runs/w3-naca0012_wing-family/r1`
* r1b: `/home/ubuntu/certonomous-runs/w3-naca0012_wing-family/r1b`
* Both `postProcessing/forceCoeffs1/0/coefficient.dat`, Cd as the mean over
  the final 20% of each run's own history.
* Pre-registrations: `W3_WING_VALID_FAMILY_PREREGISTRATION.md` (83e28569) and
  `W3_MESH_NOISE_FLOOR_PREREGISTRATION.md` (438de17c). Neither predicted this;
  it is a consequence of measurements made for other reasons, and it is
  labelled as such rather than presented as a hypothesis that was tested.
