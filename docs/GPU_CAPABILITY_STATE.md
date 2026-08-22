# GPU capability state

**Version 1.0, dated 2026-08-22.** What the lab is permitted to launch on a GPU,
what it actually has, and what it could currently use one for. Companion to
`docs/THERMAL_CAPABILITY_STATE.md`; the binding rule is `CLAUDE.md` rule 12.

**Headline: the quota is GRANTED and no GPU is attached to anything.** Approval
removed a blocker. It did not deliver capacity, and nothing in the lab is running
on a GPU today.

---

## 1. The grant, recorded verbatim

AWS support, received 2026-08-22, pasted by Sanaa. Recorded, not paraphrased.

> Hello there,
>
> Greetings from AWS!
>
> Thank you for your patience while we worked on your request.
>
> I would like to inform you that I received an update from the internal team and
> they have approved and increased the limit. Now the All G and VT instances limit
> in the US East (Ohio) region has been increased to 8.
>
> Please keep in mind that it can sometimes take up to 30 - 60 minutes for the new
> limit to take effect and become available for use.
>
> Kindly note that for certain services, the console might display only the default
> quota, the applied quota, or both.
>
> In the meanwhile, should you face any issues using the new limits, feel free to
> reach out to us with the screenshot of the error message and I'll be glad to
> assist you further.
>
> Until then, have a great day!

**The case number is not in this message.** `DOCKET`/`LAB_STATE` carry AWS case
**178725840000468** as the G-instance quota case, recorded earlier as denied. It is
very likely the same case, now resolved in the lab's favour — but *that link is an
inference by this document and not something Sanaa stated*, and it is written here
as an inference rather than folded silently into the record. An earlier draft of
`CLAUDE.md` welded her phrase *"gpu compute got approved"* onto that case number as
if she had cited it; she had not, and it was reverted. Confirm the case number from
the console before any record cites it as fact.

## 2. The request, recorded verbatim

Sanaa's original quota request, pasted 2026-08-22:

> Use case: Single-GPU machine-learning training for computational fluid dynamics
> research : training turbulence closure models (tensor-basis neural networks,
> convolutional subgrid models) on existing simulation datasets. This is a small
> academic-style R&D workload, not a service.
>
> Instance: one g6.xlarge (8 vCPUs, 1× NVIDIA L4) in us-east-2. The 8-vCPU request
> allows a single instance plus headroom for one size step but 4 vCPUs would also be
> acceptable.
>
> Usage pattern: intermittent training runs of 1–6 hours each, approximately 20–40
> GPU-hours per week, instance stopped when idle. Expected monthly spend: $20–$60 at
> on-demand pricing. The account already runs a c7a.4xlarge (i-0e417e686a5a6ac1a)
> continuously for CPU CFD solves, so this adds a modest GPU component to an
> established, paid-in-good-standing workload.

## 3. What the grant permits

The quota is **"All G and VT instances" = 8**, and that quota is denominated in
**vCPUs, not instance count** — the request's own wording (*"The 8-vCPU request
allows a single instance plus headroom for one size step"*) reads it the same way.

| instance | vCPU | GPU | fits in 8 vCPU? |
|---|---|---|---|
| `g6.xlarge` | **4** | 1× L4 24 GB | yes — and two would also fit |
| `g6.2xlarge` | **8** | 1× L4 24 GB | yes, exactly one |
| `g6.4xlarge` | 16 | 1× L4 | **no** — over quota |
| `g5.xlarge` | 4 | 1× A10G 24 GB | yes |
| `g5.2xlarge` | 8 | 1× A10G 24 GB | yes, exactly one |

**One discrepancy in the request, and it does not change the outcome.** The request
says *"one g6.xlarge (8 vCPUs, 1× NVIDIA L4)"*. **`g6.xlarge` is 4 vCPU, not 8**;
the 8-vCPU instance in that family is `g6.2xlarge`. The request's *reasoning* is
nonetheless exactly right — 8 vCPUs is one `g6.xlarge` plus headroom for one size
step — so the grant delivers what was intended. Recorded because a later reader
sizing a run off the parenthetical would size it wrong.

**Region matches, and this is the load-bearing fact.** The grant is in
**us-east-2 (Ohio)** and the lab's box is `i-0e417e686a5a6ac1a`, a `c7a.4xlarge` in
**us-east-2c**. Same region, so a GPU instance can reach this box's data by snapshot
or attached volume. Cross-region would have meant moving the run tree —
**67 GB** in `/home/ubuntu/certonomous-runs` and **9.8 GB** in
`/home/ubuntu/closure-data` — before a single training step. That problem does not
exist. Verified from instance metadata 2026-08-22.

**Not live immediately.** AWS state 30–60 minutes for the limit to take effect.

## 4. What the lab actually has

    instance   c7a.4xlarge   i-0e417e686a5a6ac1a   us-east-2c   16 vCPU
    GPU        none          no /dev/nvidia*, no nvidia-smi     (2026-08-22)

A GPU is a **separate instance**. Nothing about the grant changes this machine.

## 5. What could use a GPU today — and the honest answer is: very little

Surveyed across the tracked tree, 2026-08-22:

| candidate | verdict |
|---|---|
| `cases/RANS_LES_closure_models/Ling2016_TBNN/train_tbnn.py` | **The one genuine candidate.** A tensor-basis neural network — the workload the request describes. Small. |
| Kaandorp2020 TBRF, Wu2018 PIML_RF | **No benefit.** Random forests; `sklearn` does not use a GPU. |
| R4 SpaRTA build | **No benefit.** Sparse/symbolic regression, CPU-bound. |
| OpenFOAM / DAFoam solvers | **Not GPU-capable here.** No CUDA, AMGX or PETSc-GPU work exists anywhere in the tree. Making the solvers GPU-capable is a build project no current rung has asked for. |
| "convolutional subgrid models" (named in the request) | **Do not exist in this repo yet.** A real GPU consumer if written; nothing to run today. |

**Standing recommendation: hold the capability, provision nothing.** Launching a
GPU box today would serve one small neural-net training while every one of the
lab's live solvers is CPU work this box already does well. Launch when a rung asks
for it, under its own pre-registration.

## 6. The spending rule

**GPU spend sits OUTSIDE the blanket approval of 2026-08-21.** That blanket was
given when no GPU could launch, and reading it onto GPU-hours would be permission
laundering (`CLAUDE.md` rule 9). Until Sanaa sets a GPU rate and cap:

- Every GPU run carries its own `cost_basis` **in GPU-hours**, priced **from the
  AWS console**, never from an agent's recall.
- **The instance is stopped when idle.** A forgotten running GPU box is the
  classic waste mode, and `COMPUTE_BUDGET_CHARTER` requires waste be reported
  rather than absorbed.

**One arithmetic check on the request's own figures, offered as a flag and not as a
measurement.** The request estimates **$20–$60/month** for **20–40 GPU-hours/week**.
20–40 h/week is roughly **87–173 GPU-hours/month**, so that range implies an
effective rate near **$0.12–$0.69/GPU-hour**. `g6.xlarge` on-demand list is, to this
agent's *recall and not from any record*, closer to **$0.80/hour**, which would put
the same usage nearer **$70–$140/month**. **This box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER` §5), so nothing here is a measurement — it is a prompt to
read the real number off the console before the first run, because the gap is large
enough to matter and it runs against the lab's interest to leave it unstated.

## 7. Status

| item | state |
|---|---|
| Quota | **GRANTED** — All G and VT, us-east-2, 8 vCPUs, 2026-08-22 |
| Case number linkage | **INFERRED, unconfirmed** — see §1 |
| GPU attached | **none** |
| Instance launched | **none** |
| `BLOCKED-GPU` | **retired as a standing verdict** — use only where capacity exists and a rung still cannot run |
| GPU spend authority | **outside the 2026-08-21 blanket**; per-run `cost_basis` + Sanaa's rate and cap |
| Console price check | **NOT DONE** — required before the first run |
| First candidate rung | Ling2016 TBNN training — **not registered, not costed, not started** |
