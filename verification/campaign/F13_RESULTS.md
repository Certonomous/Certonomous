# F1 (ONERA M6) — RESULTS

**Case id: `F1`.** The filename carries `F13` because it is a **frozen path token** registered in
§9 of the pre-registration and cited by `D527`; the correction is AMENDMENT 1 at the foot of
`verification/campaign/F13_ONERA_M6_PREREGISTRATION.md` (commit `3b88ab09`). **`F13` was never
allocated and remains unallocated.**

Registration frozen `2eabe5971b1c45624c189c669b69b5f17788a56e`
· AMENDMENT 1 (id) `3b88ab09` · AMENDMENT 2 (tip-cap fill) `73c264c3`.

## Rung ledger

| rung | what | verdict | core-min | record |
|---|---|---|---|---|
| **R0** | build L1/L2/L3, `checkMesh` ×3, §5 admission | **`GATE FAIL`** | **2.18** actual / 19.3 est / 90 cap | `verification/runs/F13_ONERA_M6_runs/R0_TERMINAL.md` |
| **R1** | Gate V (V1/V2/V3 + V3 negative control) | **`PENDING`** — not launched | 0 | — |
| **R2** | L1 primal, partitions A and B | **`PENDING`** — not launched | 0 | — |
| **R3** | L2 primal, partitions A and B | **`PENDING`** — not launched | 0 | — |
| **R4** | L3 primal, partitions A and B | **`PENDING`** — not launched | 0 | — |
| **Gate D** | §6 determinism, 60 `decomposePar` | **`PENDING`** — deliberately withheld | 0 | `R0_TERMINAL.md` |

**Gates V, G and P: `PENDING`. No value has been computed for any of them.**
`P` additionally cannot be computed at all from the held artifact — §2 and `D527`.

## The blocker, in one line each

1. **Max non-orthogonality 84.64 / 86.02 / 86.78° against a ≤ 70° gate**, and it **worsens with
   refinement** (severe faces 36 → 216 → 1 440). All of it is on AMENDMENT 2's tip-fill collapsed
   lines: the measured control with the fill omitted gives **51.26°, zero faces over 70°**.
   **A collapsed line is a geometric singularity — no level of this ladder can clear this gate.**
2. **`checkMesh` does not print `Mesh OK` at any level**, on **high aspect ratio** at the wake cut
   (5 934 / 6 469 / 6 749). **Identical in the control**, so it is §5's own frozen recipe — a 16m
   uniform wake against a 161 µm first normal cell — not the amendment. Clearing it needs a wake of
   **≤ 3.2 c_root**, which would compromise the C_D that G1 grades. **Not done.**

## What PASSED, and it is not nothing

Cell counts exact (108 216 / 865 728 / 6 925 824); **`r = 2.000000` on both pairs**; **node nesting
L1 ⊂ L2 ⊂ L3 = 0.000e+00 m exactly**, read from the built `polyMesh` under a live planted control
(1e-9 m perturbation seen at 1.000000083e-09 m); max skewness 1.443 against ≤ 4; L1 y⁺ estimate 39.7
against ≤ 300; L3 S2 cell 0.00625 c against ≤ 0.00650 c. **The ladder is exactly the geometrically
similar family §5 registered. What it is not is admissible.**

## Standing

**This case is `BLOCKED` on §5 admission.** Clearing it requires a decision that is **not this
lane's and not this rung's**: either a tip-fill topology without a collapsed line (which changes
the amended cell counts, and therefore `r`), or a ruling on the two §5 admission clauses — both
above a lane. **No solver runs until then.** Firing an inadmissible ladder is the F12 failure and
it is not repeated here.
