# DRIVAER_LAYERFIX_B2 — **H2b REFUTED** — and the §6 enumeration is **EXHAUSTED**

Registration frozen `d9c30c657`, Addendum 1 `d43e3e74b`. One change from A1,
diff-verified: `minMedialAxisAngle 90 → 130`.

## Gate, in the registered order

| row | condition | result |
|---|---|---|
| 1 | rc≠0 / cap / **splice** / unreadable | NO — rc 0, 4.42 of 15 core-min, index test PASS |
| 2 | P ≥ 3 (patch set changed) | NO — **P = 0**, every candidate keeps its A1 face count |
| 3 | C < 3.00 | NO — **C = 4.14** |
| 4 | G < 50.057 % | NO — **G = 50.101 %** |
| 5 | R = 12 with control regression | NO |
| 6 | R ≥ 6 | NO |
| 7 | 1 ≤ R ≤ 5 | NO |
| 8 | **R = 0** | **YES → H2b REFUTED; §8 applies** |

## R = 0 of 12

| candidate | A1 | B2 |
|---|---|---|
| Mirrors2 | 0.00 | **0.63** |
| CTRL_SURFACE_Outlet | 0.00 | **0.48** |
| Tiresfront | 0.11 | 0.13 |
| Tiresrear | 0.03 | 0.11 |
| Rimsfront | 0.00 | 0.08 |
| WheelSupportfront1 | 0.02 | 0.02 |
| **BrakeDiscfront, BrakeDiscrear, ExhaustSystem1, Rimsrear, WheelSupportfront2, WheelSupportrear** | 0.00 | **0.00** |

Not one reached 1.00. The same two patches that crept up under B1 crept up again
(`Mirrors2` 0.63, `CTRL_SURFACE_Outlet` 0.48) and the noise floor refused them again.

## 🔴 The knob worked. The layers did not follow.

**This is not a null on the parameter — it is a null on the causal chain.**

| | A1 (90°) | B2 (130°) |
|---|---|---|
| medial-axis thickness-reduction node-events | **59,321** | **52,535** (−11.4 %) |
| achieved layer cells | 50.057 % | 50.101 % (+0.04 pp) |
| R | 0 | 0 |

Raising the angle **did** mark fewer medial-axis points, exactly as the source predicts.
The intermediate quantity moved by 6,786 node-events and **the outcome did not move at
all**. Relieving medial-axis marking is therefore **not sufficient** to extrude these
patches — which is a stronger statement than "the parameter had no effect".

## Addendum 1's prediction was correct, and it was written before this result

Addendum 1 (`d43e3e74b`, filed after launch and before the numbers) recorded that under
the **live** test — extrusion-vector disagreement, not nearest-wall-point disagreement —
two faces across a thin plate extrude nearly opposite, `d₀·d₁ ≈ −1`, **below −0.6428 as
well as below 0**, so they stay marked at 130° exactly as at 90°. It predicted **R = 0**.

The patches that stayed at exactly 0.00 are precisely the thin opposing-face parts:
brake discs, wheel supports, exhaust tip, rear rims. **The prediction is confirmed and it
changed no gate row** — R = 0 was already §7's last row before the prediction existed.

## Index test (§10, before any checkMesh number)

points **221,620**; max face index **221,619** → needs 221,620; unused trailing **0**;
`0/polyMesh` **ABSENT**; agrees exactly with snappy's `Layer mesh : faces:593126
points:221620`. **No splice.** checkMesh: max aspect ratio 20.11, **zero negative
volumes**, non-ortho 64.889, Failed 3 (skewness 4.875, determinant, concave — the same
three A1 and B1 fail).

## §8 now applies: THE ENUMERATION IS EXHAUSTED

All three hypotheses registered in `B1` §6 **before any of tonight's results** are dead:

- **H1** `maxThicknessToMedialRatio` — REFUTED (B1, `9a8242e57`)
- **H3** gap narrower than `minThickness` — REFUTED (ray measurement; blocked patches sit
  in 42.65–309.30 mm of clear space, one of them in open air)
- **H2b** `minMedialAxisAngle` — REFUTED here

Per §8, fixed before the answer was known:

1. **EXHAUSTED is a result, not a failure to find one.** The cause lies outside the
   enumeration, and that is now measured rather than suspected.
2. **No fourth hypothesis is promoted by drift.** Patch size does **not** become
   hypothesis four: median 77 mesh faces for failures against 491 for successes, with
   `NotchbackB_Pillar` — 54 faces, 4.31 layers — as the standing counterexample.
   Promoting the survivor of three refutations is choosing it, not testing it.
3. **The next step is not another parameter sweep.** It is a diagnostic reading snappy's
   own **per-point extrusion vectors** on the blocked patches — sharpened from §8's
   "per-patch extrusion decision" by Addendum 1. It needs its own registration.
4. Candidate for an upstream defect note, which would be a draft carrying **`NOT FILED`**
   in its opening lines. **SUBMISSIONS ARE PARKED.**

## Cost

265 wall s × 1 rank = **4.42 core-min** against 3.0 estimated, ratio **1.47**, cap 15.
**Outside the 0.8–1.2 contention band registered in §9**, so unlike A1 and B1 this one is
a genuine miss rather than noise, and §9's bar on claiming credit does not apply in
reverse — it is reported as a miss. No waste; staged once, built once.
