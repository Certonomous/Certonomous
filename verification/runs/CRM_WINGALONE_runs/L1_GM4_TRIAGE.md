# L1 G-M4 TRIAGE — WHAT WAS TESTED, WHAT IT SHOWED, AND WHERE MY FIRST CONCLUSION WAS WRONG

## The observation

At **layer 3**, every L1 build returns a **NEGATIVE pyHyp Min Quality**, while `rc = 0`, `PYHYP_WROTE`
is printed, the product is written, and `Sl` reaches 1.000. **Min Volume stays POSITIVE at every
layer in every run.** Only a column read catches it.

## The configurations actually run — four of them, all at L1

| run | `s0` | `pGridRatio` | min quality @ layer 3 | artifact |
|---|---|---|---|---|
| triage | 1.0e-4 | 1.1 | **-0.02189** | `TRIAGE_L1_s0/s0_1.0e-4/pyhyp.log` |
| triage | 2.0e-4 | 1.1 | **-0.02203** | `TRIAGE_L1_s0/s0_2.0e-4/pyhyp.log` |
| first build | 4.0e-4 | 1.1 | **-0.07180** | `VARIANT_pGridRatio_1.1/L1/pyhyp.log` |
| **graded build** | 4.0e-4 | **1.03** | **-0.05046** | `L1/pyhyp.log` |

For comparison, **L2 at `s0` 2.0e-4 / `pGridRatio` 1.03 returns +0.00743 — POSITIVE, and G-M4 PASSES.**
L2 at `pGridRatio` 1.1 returned **-0.03220**.

## 🔴 A CONCLUSION OF MINE THAT THE LATER EVIDENCE OVERTURNED — CORRECTED HERE, NOT QUIETLY DROPPED

After the `s0` sweep I concluded the defect was *"intrinsic to the coarsened L1 surface, not to the
option set."* **That conclusion was over-reached and the later measurement refuted half of it.**

The sweep varied `s0` over 4x and held **`pGridRatio` fixed at 1.1**. It licensed only the narrow
claim it tested — *`s0` is not the lever* — which remains true. **It did not license a claim about
the option set as a whole**, and when `pGridRatio` was later forced down to 1.03 for an unrelated
reason (L3 would not start), **L2 crossed from -0.03220 to +0.00743.** The option set WAS a lever; I
had simply not varied the one that mattered.

*A sweep over one parameter is evidence about that parameter. Reading it as evidence about
"the configuration" is how a controlled result becomes an overclaim* — the same shape as the M6
route (c) error, where a controlled zero was read as an absent mechanism.

## What the evidence DOES support, stated at the resolution it was measured

**L1 is the only level that stays negative under every configuration tried.** Under the graded option
set, L1 = **-0.05046** and L2 = **+0.00743**. The two levels sit on surfaces that are **exact node
subsets** of one another (G-M5 deviation 0.000000e+00, planted-control verified), so the geometry is
identical and only the resolution differs.

**L2's margin is +0.00743 — barely positive.** The honest reading is that the whole family sits close
to the validity boundary at layer 3, and **the coarsest level falls off the wrong side of it.**

🔴 **And note the direction, because it is the opposite of the intuition.** At L1 the *smallest* `s0`
gave the *best* quality (-0.02189 at 1.0e-4 vs -0.07180 at 4.0e-4). But the family REQUIRES L1 to
carry the LARGEST near-wall spacing — that is what refining in the normal direction means. **The
family's own construction pushes L1 toward its worst configuration.** That is a structural tension
between the r = 2 requirement and this surface, not a tuning oversight.

## What I did NOT do, deliberately

**I stopped tuning.** Two build parameters have been changed and both are disclosed (`s0` anchor in
`BUILD_PARAMETERS.md`, `pGridRatio` in `PGRIDRATIO_FINDING.md`, the latter forced by a bound pyHyp
printed itself). Continuing to search option space until layer 3 turns positive would be **fitting
the build to the gate**, and the gate is frozen precisely so that cannot happen. **L1's verdict is
reported as measured and the decision is the supervisor's.**
