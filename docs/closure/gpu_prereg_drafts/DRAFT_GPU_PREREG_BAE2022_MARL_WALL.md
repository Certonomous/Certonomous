STATUS: **DRAFT — NOT FILED, NOT LAUNCHED.** Not frozen; Sanaa signs. No run, no
instance, no AWS call of any kind until the signed file is committed alone and its
sha256 recorded. GPU spend sits OUTSIDE the 2026-08-21 CPU blanket (CLAUDE.md
rule 12, `docs/GPU_CAPABILITY_STATE.md` §6): per-item sign-off by Sanaa only.

# PREREGISTRATION DRAFT — Bae & Koumoutsakos (2022) SciMARL wall model

Written 2026-08-23 by the closure supervisor. **Zero compute was spent writing
it.** For Sanaa's desk, indexed from `docs/closure/GPU_REPRODUCTION_PLAN.md`.

---

## 1. Paper — title-verified (L-144, rule 15)

* Title page, verified from the PDF 2026-08-23: *Scientific multi-agent
  reinforcement learning for wall-models of turbulent flows*, H. Jane Bae and
  Petros Koumoutsakos, arXiv:2106.11144v2; journal *Nature Commun.* 13:1443 (2022).
* On disk: `docs/papers/closure/Bae2022_marl_wall_model.pdf`, 22 pp, sha256
  `8962e018a8b47e3a3b7854674b8adae0f8802e6cc8e6f24a01c3434657d1e36d`, sidecar `.txt`.

## 2. What the paper claims, quoted for provenance

* Wall-stress agents (policy 2×128 softsign) trained by V-RACER/ReF-ER **inside**
  WMLES of channel flow at Re_tau ≈ 2000/4200/8000; 10^7 policy-gradient steps.
* Gate-able numbers: friction-velocity "prediction error ... less than 4%" across
  Re_tau 5200–10^6 (Fig. 3); VWM fails out-of-range at (h_m)+ beyond training;
  wall-stress/velocity cross-correlation ≈ 0.3 matching DNS where EQWM is
  perfectly correlated (Fig. 7); flat-plate C_f over Re_theta 1000–7000 (Fig. 5).
* **The paper's own compute statement, and it decides this draft:** "LLWM can be
  trained using **O(10^3) CPU-hours** with less than 1GB of storage" (vs O(10^7)
  CPU-h for supervised DNS data generation).

## 3. Feasibility triage

| needed | on this box? |
|---|---|
| their incompressible staggered FD channel/BL WMLES solver | **NO** ("available on demand" — requesting it is contact outside the box: Sanaa's alone, and SUBMISSIONS PARKED) |
| `smarties` RL library (open source, github.com/cselab/smarties) | not on disk; retrievable in principle |
| DNS references (channel Re_tau 2000–8000 statistics) | published tables/curves only; no field data needed |
| a GPU | **not needed** — the paper's training is CPU-class and the policy nets are 2×128 |

## 4. The honest registration: THIS IS NOT A GPU ITEM

**Recommendation carried by this draft, marked as one: do not launch a GPU for
this paper.** The training cost the paper states is O(10^3) CPU-hours; at the
owner-stated $0.0513/core-h that is **~$51 of CPU** (above the $25 pre-auth,
inside the 2026-08-21 blanket, and still requiring its own frozen
pre-registration), and the binding blocker is the **solver**: WMLES-with-RL
coupling does not exist in this lab and OpenFOAM is not the paper's code. A GPU
would idle while a CPU solver runs.

If Sanaa wants the line kept alive, the registrable first rung is a **CPU
solver-capability pilot** (WMLES channel at Re_tau 2000 with an equilibrium wall
model, graded against published mean-flow statistics) — a prerequisite that
proves the substrate before any RL arm is priced. That pilot would be drafted
under CPU rules (core-minutes, its own cap) and is **not started by this file.**

## 5. GPU-hour line, carried because the dispatch requires one

```
GPU-hours for the paper as published:  0 (training is CPU-class, paper's own
                                          statement; policy nets are tiny)
GPU-hours if an RL-eval GPU arm were forced anyway: <= 5 GPU-h
PROPOSED CAP if launched despite the recommendation: 5 GPU-h
```

**Cost estimate line: 0–5 GPU-h × ~$0.80/GPU-h (g6.xlarge, agent recall, NOT a
record) ≈ $0–$4 — estimate — needs console confirmation.** The real budget
question is the ~O(10^3) CPU-h (~$51 at the owner-stated rate) plus a
solver-build effort that has no core-hour denomination.

## 6. What this draft does not do

No instance, no run, no fetch of `smarties`, no solver build, no contact with
the authors for the "available on demand" code — that is a send, it is Sanaa's
alone, and SUBMISSIONS are PARKED (rule 7). Nothing leaves the box.
