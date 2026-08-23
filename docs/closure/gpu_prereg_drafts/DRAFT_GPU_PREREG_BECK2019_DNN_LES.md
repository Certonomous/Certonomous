STATUS: **DRAFT — NOT FILED, NOT LAUNCHED.** Not frozen; Sanaa signs. No run, no
instance, no AWS call of any kind until the signed file is committed alone and its
sha256 recorded. GPU spend sits OUTSIDE the 2026-08-21 CPU blanket (CLAUDE.md
rule 12, `docs/GPU_CAPABILITY_STATE.md` §6): per-item sign-off by Sanaa only.

# PREREGISTRATION DRAFT — Beck, Flad & Munz (2019) deep NNs for LES closure

Written 2026-08-23 by the closure supervisor. **Zero compute was spent writing
it.** For Sanaa's desk, indexed from `docs/closure/GPU_REPRODUCTION_PLAN.md`.

---

## 1. Paper — title-verified (L-144, rule 15)

* Title page, verified from the PDF 2026-08-23: *Deep Neural Networks for
  Data-Driven Turbulence Models* (the preprint's printed title; the journal
  title is *Deep neural networks for data-driven LES closure models* — the
  difference is recorded in `docs/papers/closure/MANIFEST.md` and here, not
  harmonised), Andrea D. Beck, David G. Flad, Claus-Dieter Munz,
  arXiv:1806.04482v3; journal *J. Comput. Phys.* 398:108910 (2019).
* On disk: `docs/papers/closure/Beck2019_deep_neural_les.pdf`, 27 pp, sha256
  `5e871ebae97db5cd6e9f90b8773709e57dd7136ee6ad113486c1db603e63c7d9`, sidecar `.txt`.

## 2. What the paper claims, quoted for provenance

* Residual CNNs (RNN, 3-D conv, 16/32 feature maps) trained ~60,000 mini-batch
  iterations (50 epochs, Adam) to predict the **exact DG closure terms** of DHIT
  (Re_lambda ≈ 180, Ma 0.1) from coarse-grid data: DNS 64³ elements × N=7
  (512³ DOF), 20 randomised runs (18 train / 1 val / 1 test).
* Gate-able numbers: best RNN cross-correlation to the exact closure term
  **0.477 overall / up to 0.767 inner-element** (Table 3), against MLP ≈ 0.254
  — "less than half"; feature ablation Table 5 (full 0.4706 vs velocities-only
  0.3665); a-posteriori the direct ANN closure is long-term unstable and the
  derived eddy-viscosity form with mu_ANN clipped to [−mu0, 20·mu0] matches
  filtered-DNS E_kin, beating Smagorinsky C_s = 0.17 (Fig. 11).
* Training hardware: "an Nvidia K40c Tesla GPU as well as an Nvidia P100"; wall
  time NOT STATED. Data-side remark: **55 TB** for 0.2 T* of stored fields.

## 3. Feasibility triage

| needed | on this box? |
|---|---|
| the 20-run DGSEM DHIT DNS set (512³ DOF) | **NO**, and at their cadence the storage alone (55 TB-scale) disqualifies this box |
| FLEXI-class split-form DGSEM solver | **NO on disk — but open source and CPU-buildable**; the closure term is defined BY that discrete operator, so no OpenFOAM substitute exists even in principle |
| exact closure-term extraction pipeline | NO — comes with the solver build |
| a GPU for CNN training | fits: their nets trained on K40c/P100-class; one L4 is comparable or better |

**An as-published reproduction is out of reach for storage and DNS scale. A
SCALED VARIANT is registrable**, labelled VARIANT in every artefact.

## 4. Registered scope of the variant (draft — Sanaa may strike any arm)

* **ARM-DNS (CPU).** Build FLEXI; run DHIT DNS at **reduced scale** (e.g. 32³
  elements × N=7 ≈ 256³ DOF), **4 runs** (3 train / 1 test), snapshots only at
  the training cadence — sized to fit this box's disk with a registered storage
  cap checked before launch. **This arm is CPU core-hours, not GPU-hours, and
  must be priced by a 1-run pilot before the full set is approved** — no
  measured DGSEM rate exists in this lab and this draft refuses to invent one.
* **ARM-TRAIN (GPU).** Reproduce the paper's central a-priori ordering at our
  scale: RNN-class beats MLP-class on held-out-run cross-correlation. Draft
  gates: (G-CC) RNN CC exceeds MLP CC on the held-out run by a margin fixed at
  freeze time from the validation-run spread; (G-abl) the feature ablation
  ordering (full > velocities-only) reproduces in sign. Planted-zero control on
  every comparator (PLANT = 1.234e-03); strict completion rule per training run
  (loss history on disk, final checkpoint newer than the config, seed recorded).
* **ARM-POST (CPU, optional).** The derived eddy-viscosity closure with the
  paper's clipping, a-posteriori at our scale, vs Smagorinsky and no-model.
* **NOT A RESULT modes**: CC computed on any run seen in training; thresholds
  set after ARM-TRAIN output; closure terms extracted by any operator other
  than the solver's own DG operator (the paper's entire point); variant numbers
  shown beside paper numbers without the VARIANT label.

## 5. Estimated GPU-hours — arithmetic shown, every assumption named

```
ARM-TRAIN  ~60,000 mini-batch iterations (the paper's own count) on 1x L4,
           ASSUMED 0.2-0.8 s per iteration at our reduced sample size
           = 3.3 - 13.3 GPU-h; x2 architectures (RNN + MLP control) and
           ablations                                        =  7 - 27 GPU-h
PROPOSED GPU CAP: 30 GPU-h. Overrun stops the run (rule 12).
ARM-DNS    CPU core-hours: NOT ESTIMATED HERE - priced by the registered
           1-run pilot under CPU rules before any approval of the full set.
```

**Cost estimate line: 7–27 GPU-h × ~$0.80/GPU-h (g6.xlarge on-demand, agent
recall, NOT a record) ≈ $6–$22 — estimate — needs console confirmation.**
`cost_basis` of the signed file must carry the console-read price. Instance
`g6.xlarge`, **stopped when idle**; idle hours reported as waste.

## 6. What this draft does not do

No instance, no FLEXI build, no DNS, no training. The storage cap and the DGSEM
pilot are conditions inside a future signed file, not actions of this one.
Nothing is sent, filed, uploaded, posted or registered outside this box (rule 7).
