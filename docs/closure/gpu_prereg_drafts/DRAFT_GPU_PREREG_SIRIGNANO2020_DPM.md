STATUS: **DRAFT — NOT FILED, NOT LAUNCHED.** Not frozen; Sanaa signs. No run, no
instance, no AWS call of any kind until the signed file is committed alone and its
sha256 recorded. GPU spend sits OUTSIDE the 2026-08-21 CPU blanket (CLAUDE.md
rule 12, `docs/GPU_CAPABILITY_STATE.md` §6): per-item sign-off by Sanaa only.

# PREREGISTRATION DRAFT — Sirignano, MacArt & Freund (2020) DPM, GPU reproduction

Written 2026-08-23 by the closure supervisor (re-formed after the 2026-08-22 GPU-PLAN
lane was killed by the session limit). **Zero compute was spent writing it.** For
Sanaa's desk, indexed from `docs/closure/GPU_REPRODUCTION_PLAN.md`.

---

## 1. Paper — title-verified (L-144, rule 15)

* Title page, verified from the PDF 2026-08-23: *DPM: A deep learning PDE
  augmentation method (with application to large-eddy simulation)*, Jonathan B.
  Freund, Jonathan F. MacArt, Justin Sirignano. **Printed author order is
  Freund, MacArt, Sirignano** (arXiv:1911.09145v1); the citation of record is
  Sirignano, MacArt & Freund, *J. Comput. Phys.* 423:109811 (2020). Recorded,
  not silently harmonised (`docs/papers/closure/MANIFEST.md` says the same).
* On disk: `docs/papers/closure/Sirignano2020_dpm_les.pdf`, 28 pp, sha256
  `378bc5820fba092bdf13b9aafd06e164e5677677404b04eb4407dda75983222d`, sidecar `.txt`.

## 2. What the paper claims, quoted for provenance and not yet as a target

* Training is **a-posteriori through the solver**: a 6-layer gated network
  (~248,418 parameters, NH=200) embedded in a 64³ LES of decaying isotropic
  turbulence, trained by an adjoint of the discrete solver against box-filtered
  1024³ DNS (initial Re_t,0 = 1749), RMSprop.
* Headline gates a reproduction could aim at: (i) k(t) decay on the three
  **out-of-sample viscosities** (mu/mu0 = 0.75, 1.25, 1.5) tracks filtered DNS
  where constant-C_S = 0.18 and dynamic Smagorinsky underpredict decay (Fig. 5);
  (ii) resolved spectrum at t/t_l,0 = 0.36, mu/mu0 = 1.5 (Fig. 6); (iii) the
  paper's own negative control — the a-priori-trained twin of the same network
  **fails a-posteriori** (Fig. 7).
* Total training cost: **NOT STATED** ("Training is distributed across multiple
  GPU nodes", Blue Waters K20X era). Per-step evaluation costs are in Table 4–6.

## 3. Feasibility triage — what this box has and what is missing

| needed | on this box? |
|---|---|
| 1024³ (and 2048³) DNS of decaying HIT at Re_t,0 = 1749, 12 runs | **NO — and not generable here.** Nothing in `/home/ubuntu/closure-data/` or `/home/ubuntu/closure-challenge-benchmark/` is this dataset |
| the paper's Python staggered FD LES solver + hand-coded adjoint | **NO — a bespoke build** (their code is not on disk; OpenFOAM is not it and has no adjoint of this class) |
| trained DPM weights | **NO — not published in any artefact on disk** |

**Consequence, stated plainly: an as-published reproduction is impossible on this
box.** What is registrable is a **SCALED VARIANT**, labelled as such in every
artefact it produces (the Wu2018/Ling2016 variant-labelling precedent).

## 4. Registered scope of the variant (draft — Sanaa may strike any arm)

* **ARM-DNS.** Generate our own decaying-HIT truth at **256³** (pseudo-spectral or
  staggered FD, periodic box), 3 training viscosities + 1 held-out, one phasing
  each — 4 runs, ~2 large-eddy times, fields stored at the cadence the training
  windows need and no denser. Box-filter to 64³.
* **ARM-TRAIN.** DPM-style adjoint training of a gated network (NH scaled to fit
  L4 memory) through a 64³ LES of the same discretisation, 5-step windows as the
  paper. **The solver and its adjoint are a build deliverable of this arm and
  the build is the dominant risk, not the GPU-hours.**
* **ARM-EVAL.** Grade on the held-out viscosity ONLY, against: filtered-DNS
  truth, no-model, constant-C_S Smagorinsky. Draft gates: (G-k) time-integrated
  |k_LES − k_fDNS|/k_fDNS on the held-out case beats the best Smagorinsky arm;
  (G-neg) the a-priori-trained twin does worse a-posteriori than the DPM-trained
  network (the paper's own Fig. 7 control, run at our scale); planted-zero
  control on every comparator (PLANT = 1.234e-03); strict completion rule per
  run. Numeric thresholds are set at freeze time from the DNS arm's measured
  variance between the two Smagorinsky baselines — **not chosen after seeing the
  DPM arm.**
* **NOT A RESULT modes**: truth and model graded at different filters; any gate
  threshold chosen after an ARM-TRAIN output is seen; a variant number presented
  beside a paper number without the VARIANT label.

## 5. Estimated GPU-hours — arithmetic shown, every assumption named

```
ARM-DNS   4 runs x 256^3 x ~2 eddy turnovers on 1x L4
          ASSUMED 2-6 GPU-h per run (no measurement exists on this box
          for any 3-D spectral/FD DNS on any GPU)          =  8 - 24 GPU-h
ARM-TRAIN adjoint windows, epochs NOT STATED by the paper;
          ASSUMED 10k-50k adjoint window iterations at
          ASSUMED 1-3 s each on L4                         = 10 - 40 GPU-h
ARM-EVAL  held-out LES sweeps, trivial beside the above    =  ~1 GPU-h
                                                    TOTAL  = 19 - 65 GPU-h
PROPOSED CAP: 80 GPU-h. Overrun stops the run (rule 12); no new budget.
```

**Cost estimate line: 19–65 GPU-h × ~$0.80/GPU-h (g6.xlarge on-demand, agent
recall, NOT a record) ≈ $15–$52 — estimate — needs console confirmation.**
`cost_basis` of the signed file must carry the console-read price per
`docs/GPU_CAPABILITY_STATE.md` §6. Instance `g6.xlarge` (4 vCPU, 1× L4 24 GB),
inside the granted 8-vCPU quota; **stopped when idle**, every idle hour reported
as waste, not absorbed.

## 6. What this draft does not do

No instance exists or is created by this file. No training, no DNS, no fetch of
the paper's data (none is on disk and none is retrievable as-published). Nothing
is sent, filed, uploaded, posted or registered outside this box (rule 7).
Whether the variant is worth $15–$52 plus a bespoke solver-and-adjoint build is
**Sanaa's call, and this draft takes no step toward it.**
