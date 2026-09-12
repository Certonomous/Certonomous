# h_surf MEASURED DIRECTLY — a DIAGNOSTIC that GRADES NOTHING

**Run AFTER `DRIVAER_R2B_LAYER_PROBE_C2_PREREGISTRATION.md` was frozen (`d4142f0ee`,
04:46:10Z) and AFTER C2 was launched (04:48:52Z). It could not have influenced the
freeze.** It changes no gate, no threshold and no exit. **E1 and E2 fire on MEASURED
coverage and MEASURED y⁺, never on anything below.** Nothing here is cited in C2's
verdict. Authorised as a diagnostic by the cfd-supervisor; run because the frozen
registration itself named this quantity as its weakest input.

## What was inferred, and what is measured

C2's frozen table used `h_surf` = **51.900 mm**, backed out of the control's y⁺ **by
assuming the relative spec delivers what it requests**. Measured directly off the built
control mesh — the wall face is the outer face of the first layer, so its edge length
*is* the surface cell size — `sqrt(area / nFaces)`:

| group | area | faces | **h_surf** |
|---|---|---|---|
| layered (`r2_coarse`) | 24.959 m² | 14,057 | **42.137 mm** |
| unlayered (`r2_coarse`) | 5.931 m² | 3,803 | 39.490 mm |

**The inferred value was 23.2 % too large, and the assumption behind it is false.**

## The finding: the over-delivery is NOT confined to absolute sizing

| spec | requested t₁ | delivered t₁ | factor |
|---|---|---|---|
| relative (`r2_coarse`, 0.2048·h) | 8.630 mm | 10.628 mm | **1.2315** |
| absolute (C1, 5.0 mm→no, 2.10 mm) | 2.100 mm | 3.519 mm | **1.6758** |

snappyHexMesh over-delivers first-layer thickness **under both specifications**, and the
factor **falls 0.3143 per ln(thickness ratio)** — it over-delivers most when asked for
least, which is the behaviour C2's registration hypothesised and could not establish from
one point. **Two points is still two points**; this is a measured trend, not a law.

## What it implies for C2 — A PREDICTION, RECORDED BEFORE C2 LANDS

On the measured axis, C2's registered 5.00 mm request sits at thickness ratio 0.11866:

- predicted delivery factor **1.4031** → delivered t₁ **7.016 mm** → **y⁺ ≈ 318**
- coverage refit on the measured axis (28.222 pts/ln) → **≈ 56.9 %**

**So the sharpened prediction is that C2 PASSES the coverage floor and FAILS the band,
i.e. E2 FIRES.** The frozen registration predicted coverage 53.7 % and y⁺ 227–380 and
said in terms that the upper half of that range is out of band; this narrows it to a
point estimate 18 above the limit. **It is recorded here before the run lands so it is
falsifiable, and it grades nothing either way.**

If C2 instead lands in band, this diagnostic's trend is wrong and that is a finding
about the extruder, not a rescue of the prediction.
