# GPU reproduction plan — the five closure papers, triaged for Sanaa

**Version 1.0, 2026-08-23, closure supervisor.** Discharges the chief's
2026-08-22 dispatch (*"pre-register DPM, Bae, Lozano-Durán, Beck (and Ling2016
TBNN GPU training) with GPU-hour cost bases; nothing launches before Sanaa signs
each"*, `ff551ed5`). The lane that started this plan was killed by the session
limit after title-verifying the five papers; this file and four of the five
drafts were written by the re-formed supervisor, which re-verified all five
title pages against the PDFs and `MANIFEST.md` hashes on 2026-08-23 (rule 15).

**Zero compute was spent producing any of this. No GPU instance exists, none was
created, no AWS call of any kind was made. Every draft below is stamped
DRAFT — NOT FILED, NOT LAUNCHED, and every GPU-hour dollar figure in this file
is an estimate needing console confirmation** (`docs/GPU_CAPABILITY_STATE.md`
§6: the box cannot read its own billing; the ~$0.80/GPU-h used throughout is
agent recall, not a record). **GPU spend sits OUTSIDE the 2026-08-21 CPU
blanket** (CLAUDE.md rule 12 as amended at `e0cf8f0c`): each item needs Sanaa's
per-item sign-off on its own signed, frozen pre-registration.

---

## 1. The capability, in two lines

Quota **GRANTED**: All G and VT instances, us-east-2, 8 vCPUs — one
`g6.2xlarge`/`g5.2xlarge` or two `xlarge` (verbatim grant in
`docs/GPU_CAPABILITY_STATE.md` §1). **No GPU is attached to anything**; a GPU is
a separate instance, launched per signed run, stopped when idle.

## 2. The triage table

| # | paper (title-verified, sha in draft) | native data/solver on box? | registrable form | GPU-h (draft range) | est. $ (needs console confirmation) | draft's recommendation |
|---|---|---|---|---|---|---|
| 1 | **Ling 2016 TBNN** | variant dataset **YES** (closure-challenge benchmark; none of Ling's 9 flows) | GPU arms A (paper's own SGD to convergence, removes departure D3) + B (Bayesian architecture search) on the existing CPU-lane variant | **12–52, cap 60** | ~$10–$42 | **The one ready-to-sign item.** Data local, CPU lane already GATE REACHED, draft complete |
| 2 | **Beck 2019 DNN-LES** | **NO** — needs FLEXI (open source) + DHIT DNS; 55 TB-scale as published | SCALED VARIANT: reduced DHIT (≈256³ DOF, 4 runs) after a CPU pilot prices the DGSEM arm; GPU trains RNN-vs-MLP a-priori ordering | **7–27, cap 30** (+ unpriced CPU DNS pilot) | ~$6–$22 | Registrable second, contingent on the CPU pilot price |
| 3 | **Sirignano 2020 DPM** | **NO** — 1024³ DNS not generable; bespoke solver+adjoint build | SCALED VARIANT: own 256³ HIT truth + DPM-style adjoint training at 64³; build risk dominates | **19–65, cap 80** | ~$15–$52 | Registrable but the solver-and-adjoint build is the real cost; rank behind 1–2 |
| 4 | **Bae 2022 SciMARL wall model** | **NO** — solver "available on demand" (contact = send, PARKED); `smarties` retrievable | **NOT A GPU ITEM** — paper's own figure: O(10³) **CPU**-hours (~$51 at the owner-stated rate); prerequisite is a WMLES solver-capability pilot under CPU rules | 0–5, cap 5 if forced | ~$0–$4 | **Do not launch a GPU.** Decide the CPU pilot instead |
| 5 | **Lozano-Durán 2023 BFWM** | **NO** — ~500-DNS database + proprietary charLES; stated training scale 288 A100-h | **BLOCKED at the data**, and as-published scale (~900–1,700 L4 GPU-h) exceeds any sane cap and the quota's class | none proposed | (~$700–$1,400 shown to justify refusal) | **Do not launch.** CPU validation-only arm available if wanted |

## 3. Where the five drafts are

| paper | draft |
|---|---|
| Ling 2016 | `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/PREREGISTRATION_DRAFT.md` (written by the killed lane 2026-08-22; stamp aligned + estimate line added §14, 2026-08-23) |
| Sirignano 2020 | `docs/closure/gpu_prereg_drafts/DRAFT_GPU_PREREG_SIRIGNANO2020_DPM.md` |
| Bae 2022 | `docs/closure/gpu_prereg_drafts/DRAFT_GPU_PREREG_BAE2022_MARL_WALL.md` |
| Lozano-Durán 2023 | `docs/closure/gpu_prereg_drafts/DRAFT_GPU_PREREG_LOZANODURAN2023_BFWM.md` |
| Beck 2019 | `docs/closure/gpu_prereg_drafts/DRAFT_GPU_PREREG_BECK2019_DNN_LES.md` |

Every draft carries: the title-page verification with the PDF sha256; the
paper's gate-able numbers quoted for provenance; a feasibility triage against
what is actually on this box; a registered scope with draft gates, planted-zero
control (PLANT = 1.234e-03) and NOT A RESULT modes; the GPU-hour arithmetic
with **every assumption named**; a proposed cap under the overrun-stops-the-run
rule; and the cost estimate line marked **estimate — needs console
confirmation**.

## 4. The common conditions no signed file may drop

1. **Console price first.** The first act after Sanaa signs any item is reading
   the real on-demand price off the AWS console and writing it into the frozen
   file's `cost_basis` — the recall figure in these drafts dies at that moment.
2. **Instance stopped when idle**; idle hours are waste, reported not absorbed.
3. **Freeze before launch**: the signed pre-registration is committed alone,
   sha256 recorded, before any instance exists.
4. **Variant labelling**: none of the five native datasets is on this box, so
   every result except Ling arm A/B is a VARIANT and says so beside every number.
5. **No contact**: two papers' inputs are obtainable only by asking their
   authors or a vendor. Asking is a send; sends are Sanaa's alone and
   SUBMISSIONS are PARKED (rule 7).

## 5. Recommendation — marked as one; the choice is Sanaa's

Sign **Ling** (item 1) if any GPU item is wanted first: its data is local, its
CPU lane is graded, and its draft's arms remove that lane's largest departure.
Decide **Beck's CPU pilot** and **Bae's CPU solver pilot** as CPU questions on
their own merits — neither needs the GPU to start. **Do not launch** items 4–5
as GPU work; the drafts show the arithmetic. Holding the capability while
provisioning nothing remains a legitimate choice
(`docs/GPU_CAPABILITY_STATE.md` §5) and costs $0.
