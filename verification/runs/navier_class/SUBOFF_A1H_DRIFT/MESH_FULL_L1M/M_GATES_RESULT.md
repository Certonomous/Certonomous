# SUBOFF A1h — L1 MIRROR: MESH GATES M-1…M-7, AND THE M-d DISCLOSURE THAT TRAVELS WITH THEM

Gates frozen in `verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md`
§2.1 at commit `79b4de868e1e8bbf08e14cd6db3c1d6acb3240df`. Measured 2026-09-13.

## 🔴 READ THIS BEFORE THE GATE TABLE

**THE SOURCE MESH IS NOT ADMITTED.** `SUBOFF_A1b_PREREGISTRATION.md` §2 records `L1` as
**`GATE FAIL` on M-d** — minimum cell determinant **8.6227045e-04** against a registered
**1.0e-03**. The mirror does not repair it and was never going to: a mirror is an isometry.

> **M-d `GATE FAIL` by 1.16×, proceeding on SANAA'S DIRECTIVE E (2026-09-12, ~22:35Z).**

Her words, byte-exact, `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
lines 221–222: *"2.2e-5 vs 1e-6 is fine"* / *"ok then for me its a pass. And in general if
we are very close to the gate its fine"*. The chief's reading recorded there extends it to
**launching**: *"a value very close to its gate does not block proceeding — launching,
continuing, filming… A near-miss is reported to her as 'GATE FAIL by &lt;margin&gt;,
proceeding on directive E' — never rewritten as PASS by an agent; only she converts one."*

**THE VERDICT WORD IS NOT REWRITTEN.** This mesh is **not** admitted and is **not** a PASS
on M-d. It is a `GATE FAIL` the owner has pre-authorised proceeding past. The margin, stated
so the row cannot flatter itself: **1.0e-03 / 8.6227045e-04 = 1.16×**, against the **22.3×**
she personally converted in the instance she ruled on — and which the dafoam supervisor
recorded at the time was *"not 'very close'"*. **1.16× is.** That comparison is why this is
inside her ruling and not an extension of it.

**THE FAILURE TRAVELS WITH EVERY NUMBER.** `SUBOFF_A1b_RESULTS`' own sentence — *"that
failure travels with every number out of it"* — is **not** superseded by directive E. Every
`Y_v'` and `N_v'` produced on this mesh carries the M-d disclosure on its certificate.

**A1h ADDENDUM 1's DETERMINANT GAP STANDS, DISCLOSED AND UNREPAIRED.** §2.1's M-1…M-7
contain **no determinant limb**, so this mesh passes every gate this act registered while
failing one the lab registered elsewhere. **That gap is why the failure was nearly
invisible**, and this ruling does not add a limb — a dated addendum may not alter a gate or
a gate set. Recorded as a defect in the registration, not resolved by it.

## THE GATES — measured, and reported BESIDE the M-d disclosure, not instead of it

| # | gate | threshold | measured | |
|---|---|---|---|---|
| M-1 | `nCells` | exactly 2 × 3,268,613 | **6,537,226** | PASS |
| M-2 | patch `symm` | nFaces == 0 | **0 faces, 0 points, "ok (empty)"** | PASS |
| M-3 | z bounding box symmetric | ±2.9910566 | **(−2.9910566, +2.9910566)** | PASS |
| M-4 | topology closed | closed | **`".*"` ok (closed singly connected)** | PASS |
| M-5 | max non-orthogonality | ≤ 70° | **64.95288158°** (avg 7.277) | PASS |
| M-6 | max skewness | ≤ 4 | **2.913253394** | PASS |
| M-7 | **THE SEAM** | min vol > 0; ≤ 70° **and** ≤ whole-mesh | **4.597252787e-13 m³; 60.97032736°** | PASS |
| — | **A1b M-d (not an A1h limb)** | ≥ 1.0e-03 | **8.622704491e-04**, 2 under-determined cells | **GATE FAIL by 1.16× — proceeding on directive E** |

## M-7 — THE SEAM IS AGAIN BETTER THAN THE MESH

135,638 seam cells of 6,537,226; 71,765 seam points of 7,164,943.

| quantity | seam | whole mesh | reading |
|---|---|---|---|
| min `cellVolume` | **4.597252787e-13 m³** | 1.554469886e-13 m³ | smallest cell is **not** at the seam |
| max `nonOrthoAngle` | **60.97032736°** | 64.95288158° | worst non-orthogonality is **not** at the seam |

Plants, before the numbers were believed: **S-A** found 71,765 points at z = 0 and **0** at
an impossible plane; **S-B** planted −9.87e-30 into `cellVolume` and 123.456 into
`nonOrthoAngle` at a known seam cell and required both back as the extrema; the cell count
was **derived from `owner`/`neighbour` connectivity and cross-checked** against `checkMesh`.

## THE MERGE, PROVEN FROM THE GEOMETRY — NOT FROM A DOUBLED CELL COUNT

| quantity | L1 (half) | 2 × L1 | mirror, predicted | mirror, measured | |
|---|---|---|---|---|---|
| points | 3,618,354 | 7,236,708 | 2N − 71,765 = **7,164,943** | **7,164,943** | MATCH |
| faces | 10,145,599 | 20,291,198 | 2N − 67,889 = **20,223,309** | **20,223,309** | MATCH |
| seam points by vertex test | — | — | = `symm` patch points **71,765** | **71,765** | MATCH |

Three independent predictions, three exact matches. The seam was **merged, not duplicated**
— and the determinant's exact survival (0.00086227045 → 0.0008622704491) is the same
isometry seen from the other side.
