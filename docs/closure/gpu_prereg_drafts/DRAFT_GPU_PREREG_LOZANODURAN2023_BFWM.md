STATUS: **DRAFT — NOT FILED, NOT LAUNCHED.** Not frozen; Sanaa signs. No run, no
instance, no AWS call of any kind until the signed file is committed alone and its
sha256 recorded. GPU spend sits OUTSIDE the 2026-08-21 CPU blanket (CLAUDE.md
rule 12, `docs/GPU_CAPABILITY_STATE.md` §6): per-item sign-off by Sanaa only.

# PREREGISTRATION DRAFT — Lozano-Durán & Bae (2023) building-block-flow wall model

Written 2026-08-23 by the closure supervisor. **Zero compute was spent writing
it.** For Sanaa's desk, indexed from `docs/closure/GPU_REPRODUCTION_PLAN.md`.

---

## 1. Paper — title-verified (L-144, rule 15)

* Title page, verified from the PDF 2026-08-23: *Machine learning
  building-block-flow wall model for large-eddy simulation*, Adrián Lozano-Durán
  and H. Jane Bae, arXiv:2211.07879v3; journal *J. Fluid Mech.* 963:A35 (2023).
* On disk: `docs/papers/closure/LozanoDuran2023_wall_model.pdf`, 35 pp, sha256
  `d30b8bf9f86d09b97991f76596df410fe8175e2d9f4300d3aa2613685e3fd001`, sidecar `.txt`.

## 2. What the paper claims, quoted for provenance

* A classifier (5×20 ReLU, softmax over 7 building-block classes) plus five
  predictor ANNs (5×30 each), trained on **E-WMLES** of seven building-block
  flows whose truth rests on a **DNS database of "roughly 500 simulations"**.
* Gate-able numbers: ZPG TBL internal wall-stress error "below 0.5% for the BFWM
  and about 2% for the EQWM" (Fig. 9c); pipe at Re_tau ≈ 40,000 internal errors
  below 5% at the coarsest grids (Fig. 10); spanwise-transient channel internal
  errors "below 1% for all times" where EQWM misses the transient entirely
  (Fig. 13); NASA Juncture fuselage errors below 2%.
* Training hardware, stated: "roughly **12 hours to train each ANN using 4
  NVIDIA A100** with 40 GB of memory." Runtime overhead 1.1–1.3× EQWM.

## 3. Feasibility triage — and this one is BLOCKED on data

| needed | on this box? |
|---|---|
| the ~500-simulation building-block DNS database | **NO — not on disk, not public as an archive** |
| E-WMLES training data (generated in charLES with exact-for-mean SGS) | **NO** |
| charLES (Cascade Technologies) | **NO — proprietary; not obtainable without contact, which is Sanaa's alone** |
| 24 A100-class GPU capacity | **NO — quota is 8 vCPUs of G/VT class, one L4/A10G** |

**Consequence: the training-stage reproduction is BLOCKED on inputs this lab
cannot obtain by itself, and the stated training scale does not fit the granted
quota in any case.** Scaling their stated figure: 6 ANNs × 12 h × 4 A100 =
**288 A100-hours**; on one L4 at an ASSUMED 1/3–1/6 A100 throughput that is
**~900–1,700 GPU-hours ≈ $700–$1,400** at the recall rate — an order of
magnitude beyond anything this lab has ever spent on one item, for a variant
that would still lack the training data.

## 4. The honest registration

**Recommendation carried by this draft, marked as one: do not launch.** Record
the item as **BLOCKED** at the training data (the retired `BLOCKED-GPU` token
does not apply — capacity exists; the data does not).

The registrable fallback that needs no GPU and no charLES: a **validation-only
CPU arm** grading the paper's *checkable claims* — EQWM baseline errors on pipe
and channel at matched grids (their Figs. 9–10 EQWM curves) — in OpenFOAM,
labelled a VARIANT by construction since the paper's own consistency argument
ties BFWM training to its own solver. That arm tests our substrate against
their baselines, not their model, and would be drafted under CPU rules if Sanaa
wants it. **It is not started by this file.**

## 5. GPU-hour line, carried because the dispatch requires one

```
As-published training reproduction:  ~900-1,700 L4 GPU-h (assumption-scaled
     from the paper's 288 A100-h; throughput ratio ASSUMED 1/3-1/6)
     -> NOT PROPOSED. No cap is proposed because no launch is proposed.
BLOCKED at: training database + charLES, before any GPU-hour is reachable.
```

**Cost estimate line: ~900–1,700 GPU-h × ~$0.80/GPU-h (g6.xlarge, agent recall,
NOT a record) ≈ $700–$1,400 — estimate — needs console confirmation — and
recorded to show why this draft recommends against launch, not to price one.**

## 6. What this draft does not do

No instance, no run, no data fetch attempt, no contact with Cascade or the
authors (a send — Sanaa's alone; SUBMISSIONS PARKED, rule 7). Nothing leaves
the box.
