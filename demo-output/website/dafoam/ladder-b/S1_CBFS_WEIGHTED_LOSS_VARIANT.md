# S1 — offline weighted-loss variant: pre-registration, then the numbers

Item `s1-cbfs-weighted-loss-offline-variant` (entry-12 dispatch, supervisor review
commit 94349b83; the entry-7 diagnostic extended to the S1 objective). **Zero solver
core-min**: everything below is host-side arithmetic on fields already on disk
(`S1-cbfs-reinversion/cbfs_inv/340` repaired baseline, `cbfs_inv/2500` final,
`beta_accept_iter*.npy` checkpoints, `J_history_main.csv`).

## Part I — pre-registration (committed before any weighted number is computed)

### 0. Honesty preamble: what is already known and what is new

The regional aggregates are already on the record (reinversion result §4: window
−94.9%, near-wall −95.9%, y>2 −21.6%), so the primary reductions below are **expected
to land near those numbers — this variant is not pretending ignorance of them**. What
is genuinely unmeasured at this writing: the per-cell **hurt census** (entry 7's
relocation mechanism — did the correction increase error anywhere, and where), the
**region-equalized and sparse-point sensitivity schemes**, and the **trajectory
decomposition** (when the out-of-window beta effort grew relative to the window
effort). The verdict rule binds on the full set, hurt cap included, so the outcome is
not foreordained by the known aggregates.

### 0b. A correction found while preparing this item, disclosed before use

Spatial mapping of DV-indexed vectors requires the DV→serial-cell permutation. It was
recovered **exactly** from `processor*/constant/polyMesh/cellProcAddressing`
(concatenated rank order; verification: permuted `beta_final.npy` matches the written
`2500/betaFIOmega` to 5.1e-15, all 21,000 entries, bijective). Consequence: the FD
cell "neighborhood" labels in the reinversion records applied serial centres to DV
indices and are **wrong** — DV 5363/5428/5491 are serial cells 187/330/471, all three
in the separated shear layer just downstream of the crest ((0.446,0.995),
(0.930,0.926), (1.089,0.900)), not "step crest / downstream recovery / upstream
channel". The FD **numbers** are index-consistent and stand (0.032%/0.115%/0.009%);
the "three distinct mesh neighborhoods" claim is retracted by dated addendum on the
result document, and the selection rule is restated as what it actually did: the
three top-|g|-rank components (1, 5, 4), which happen to cluster in the shear layer —
physically where the top of the gradient distribution should live. The same caveat
plausibly applies to W4 §5d's corrupted-objective cell labels (flagged for W4's
owner; not edited here). All loss-geography and G2 audits are unaffected — they were
computed on written serial-order fields throughout.

### 1. Weighting schemes, chosen on stated grounds, fixed now

All schemes weight the per-cell squared residual d²_i = |U_i − UData_i|² (all three
components unless stated); R_w = 1 − Σw·d²(final) / Σw·d²(baseline).

- **W1 — window-only (PRIMARY):** w=1 in the pre-registered G2 window
  (0≤x/h≤6, 0≤y/h≤2), else 0. Ground: G2's own declared physics region — the loss G2
  implicitly wishes the QoI had looked at.
- **W2 — window ∪ near-wall (PRIMARY):** w=1 on window or y<0.5 anywhere, else 0.
  Ground: the two regions where the S1 records place model-form error (near-wall held
  56.5% of the repaired baseline loss).
- **W3 — region-equalized (sensitivity):** four regions (window; y<0.5 outside
  window; y>2; remainder), each weighted 1/(its baseline loss share) so every region
  contributes equally at beta=1. Ground: entry 7's point-density idea — removes the
  equal-cell-weight choice without zeroing anything.
- **W4 — Wu/Zhang sparse-point proxy (sensitivity):** 30 cells nearest a 6×5 grid
  spanning x∈[0.5,5.5], y∈[0.1,1.2], **x-component only** (Σ(Ux−UxData)²). Ground:
  the reproduction target's own loss shape (30 LES x-velocity points in the
  separation region).

### 2. Hurt-cap discipline (entry 7's, pre-registered)

Per region: hurt = Σ over cells with d²(final) > d²(baseline) of the increase; gross
reduction = Σ over improved cells of the decrease. **Cap: inside each PRIMARY
weighted region (W1, W2 supports), hurt < 10% of that region's gross reduction.**
Relocation census everywhere else (y>2, remainder) reported loudly, no cap — the
uncapped regions are exactly where entry 7's blind-strip mechanism would hide.

### 3. Verdict rule, fixed now

- **CAPTURABLE** iff R_W1 ≥ 0.70 AND R_W2 ≥ 0.70 AND the hurt cap holds in both
  primary regions. Meaning: the achieved beta already contains the window answer
  under a loss that looks at it; G2's fail is a placement-of-effort artifact of
  equal-weight training plus a global top-decile accounting. Action per entry 12: a
  weighted REINVERSION arm (~250 core-min class) is filed as its own priced item.
- **NOT CAPTURABLE** otherwise. Meaning: even where the loss looks, the achieved
  correction under-serves the window or bought it by relocating error into it.
  Action per entry 12: a documented G2-bar revision proposal — the bar interrogates
  reference-level mismatch, not model correction — filed loudly.
- W3/W4 never decide. If W4 (the reproduction target's own shape) disagrees in sign
  with the verdict, that disagreement is flagged as a loud caveat on whatever
  follow-up is recommended.
- Descriptive, no gate: trajectory decomposition — per accepted iterate k (1..11,
  mapped to evals 2,5,6,7,10,11,12,13,14,15,16), rms(beta−1) inside vs outside the
  window (via the exact permutation), set against the accepted J. Tests the temporal
  form of the placement hypothesis: did the out-of-window effort grow only after the
  window signal was spent?

*Nothing below this line existed when this file was committed.*
