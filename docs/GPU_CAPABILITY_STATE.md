# GPU capability state

**Version 1.1, dated 2026-08-23** (v1.0 dated 2026-08-22; all v1.0 sections stand
unedited — changes land only as the dated §8 below and this header). What the lab
is permitted to launch on a GPU, what it actually has, and what it could currently
use one for. Companion to `docs/THERMAL_CAPABILITY_STATE.md`; the binding rule is
`CLAUDE.md` rule 12.

**Headline: the quota is GRANTED and ~~no GPU is attached to anything~~
*(superseded 2026-08-23 — see §8)* the fleet now includes one launched GPU
instance (g6.xlarge, 1× NVIDIA L4), reachable from this box over SSH.** Still
true and unchanged: **no GPU is attached to the c7a box itself**, and nothing in
the lab is training on a GPU today — the console price check remains NOT DONE.

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

## 8. First instance launched — 2026-08-23

The §7 table above is a frozen v1.0 snapshot and is **not edited**; the rows it
carries as "GPU attached: none" and "Instance launched: none" are **superseded by
this section**. Every other §7 row stands, including **Console price check: NOT
DONE**.

Sanaa launched the lab's first GPU instance on 2026-08-23. Facts below are split
by provenance, per the lab's honesty convention.

**Metadata-verified** — read over SSH from this box on 2026-08-23 (IMDSv2
instance metadata, `nvidia-smi`, `df`), not from recall:

| item | value |
|---|---|
| instance type | `g6.xlarge` |
| private IP | **172.31.44.162** — *canonical address*: persists across stop/start |
| public IP | 3.16.124.210 — *ephemeral*: changes on stop/start; never record as canonical |
| GPU | 1× NVIDIA L4, 23034 MiB |
| driver | 595.91.07 |
| root volume | 96G, 83G free |
| AMI | Deep Learning OSS Nvidia Driver AMI GPU PyTorch 2.13 (Ubuntu 26.04), `ami-0dda0fd1cccbe2c28` |
| region / AZ | us-east-2 / us-east-2c — same region as this box, per §3 |
| SSH from this box | **verified 2026-08-23**: `ssh ubuntu@172.31.44.162` returns hostname `ip-172-31-44-162` and the L4 in `nvidia-smi -L`; alias `gpu1` added to this box's `~/.ssh/config` and verified |

**Owner actions** — done by Sanaa in the console; reported, not independently
verifiable from this box:

| item | value |
|---|---|
| launch itself | performed by Sanaa, 2026-08-23 |
| key pair | `certonomous` |
| security group | `launch-wizard-3` |
| login user | `ubuntu` |
| key bridge | this box's `id_ed25519.pub` placed into the instance's `authorized_keys` by Sanaa (the successful SSH above corroborates that the bridge works, not who placed it) |

**Still outstanding — console price.** Sanaa has **not yet provided the console
$/hr** for `g6.xlarge`. The §6 arithmetic flag stands: no rate exists on the
record, no cost may be quoted from recall, and **no run may be costed** until the
console number is read and recorded.

**Standing operational rule** (`CLAUDE.md` rule 12): **the instance is stopped
when idle**, and **nothing trains** until the Ling2016 TBNN pre-registration
carries the console price in its `cost_basis` and Sanaa's **per-item** sign-off —
GPU spend sits outside the 2026-08-21 blanket, and reading that blanket onto
GPU-hours would be permission laundering (rule 9).

## 9. Price check CLOSED and cost approved — 2026-08-23

**§7's "Console price check: NOT DONE" row and §8's "Still outstanding — console
price" paragraph are superseded by this section.** Neither is edited.

**The rate, from AWS's own published price list — not recall, not a screenshot:**

| item | value |
|---|---|
| `g6.xlarge`, Linux, on-demand, us-east-2 | **$0.8048/hr** (payload string `"0.8048000000"`) |
| `g6.2xlarge`, same feed | $0.9776/hr |
| `g5.xlarge`, same feed | $1.0060/hr |
| source URL | `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20(Ohio)/Linux/index.json` — the feed backing `aws.amazon.com/ec2/pricing/on-demand` |
| JSON path | `regions["US East (Ohio)"]["g6 xlarge US East Ohio Linux"].price`; entry fields `Instance Type: g6.xlarge`, `Operating System: Linux`, `Location: US East (Ohio)`; rateCode term `JRTCKXETXF` (the Price List API's OnDemand term code) |
| retrieved | **2026-08-23 21:00:47 UTC**, by a closure lane, bare GET, no lab data in the request |
| payload's own stamp | `hawkFilePublicationDate: 2026-08-21T02:02:57Z` |
| provenance label | **published price list, retrieved 2026-08-23** — satisfies "never from recall"; the console itself remains Sanaa's to read and a console figure supersedes this one if they ever differ |

The §6 arithmetic flag is resolved: the true rate ($0.8048/hr) sits where §6's
recall put it (~$0.80), so the request's own $20–$60/month at 20–40 GPU-h/week
was the optimistic reading, as §6 suspected.

**Sanaa's GPU cost approval, verbatim (2026-08-23, chief's session record):**

> regarding the GPU COST it's fine you have my approval.

Recorded with the same provenance form as the four D-2 compute facts
(owner-stated, chief's session record). Read together with §8 — Sanaa launched
`gpu1` herself, an owner action — this approves **GPU cost** for the plan's
ready item (Ling2016 TBNN, `GPU_REPRODUCTION_PLAN.md` §2 item 1) under that
item's own registered cap. **It is not a physics-scope change**: the other four
GPU items proceed only in the plan's own order and terms, each costed before it
runs. An overrun still stops the run; it does not get a new budget.

## 10. First run complete; instance STOPPED by Sanaa; self-shutdown approved — 2026-08-24

**Written 2026-08-24T16:11:46Z (clock read in the writing invocation).** §7–§9 are not edited;
this section supersedes §8's "instance launched" state.

**Sanaa's rulings, verbatim (2026-08-24, chief's session record):**

> 1. GPU shutdown suggestion: yes approved (also i stopped that instance).
> 2. Good for the dispatched work, i approve of everything.

| item | state |
|---|---|
| `gpu1` | **STOPPED by Sanaa** (2026-08-24, reported without a clock). Private IP 172.31.44.162 persists across stop/start; the public IP changes on restart and is never recorded as canonical |
| first run | Ling2016 TBNN GPU arm 1 — **NOT A RESULT** on its frozen gates (`gpu/RESULTS.md`, commit `353925c7`); 10.7054 GPU-h = $8.62 derived at §9's $0.8048/GPU-h |
| idle waste of record | **7.88 GPU-h = $6.34 derived**, 08:03:58Z → 15:56:45Z (the last verified idle read, ledger C-16). The window from 15:56:45Z to Sanaa's stop is **unmeasured** — she reported "stopped" without a clock — and is stated absent, not estimated (ledger correction C-19) |
| driver self-shutdown | **APPROVED as a standing mechanism** (ruling 1). Every future GPU driver ends with `sudo shutdown -h now` AFTER its completion marker and `spend.json` are written, so a failed halt is visible. **Precondition, VERIFY-by-Sanaa-in-console before first reliance:** the instance's *shutdown behaviour* attribute must read **stop** (the EBS-backed default); with *terminate* the root volume would be lost. This box has no AWS CLI and cannot read the attribute |
| next GPU item | Ling2016 arm 2 (matched update count) — approved under ruling 2 with per-item costing still required; pre-registration to be frozen BEFORE compute; the instance is started by Sanaa on the chief's request only |

## 11. WITHDRAWAL OF ATTRIBUTION — 2026-08-25. APPENDED AT THE FOOT.

**Written 2026-08-25T00:39:39Z (box clock, read in the writing invocation) by a
closure lane at the closure supervisor's direction. Version 1.1 → 1.2.
§1–§10 are NOT edited. lines whose number changed above this section: 0.**

**Proved, not asserted.** The pre-append prefix is bytes 1–14817 (258 lines);
sha256 `47c4c9c85432907301dc5ed1528a8c67ebf5f5e9e637b9b0cea14f461c566997` before
this block was written and the identical value after, and byte-identical to this
file's blob at HEAD `72bc966d`. **Disclosed tension:** rule 6 asks for a version
bump, and the file's version line is at line 3 — *above* this block. Editing it
would itself be a mid-file change, so **line 3 is deliberately left alone** and the
bump is carried here, following this repository's own precedent for foot-appended
disclosures. **The block is at the FOOT** — L-304.

**Status term: `ATTRIBUTION WITHDRAWN — TEXT STANDS AS A RELAYED PARAPHRASE`.** Not
one of `CLAUDE.md` rule 1's six verdict words, deliberately: no gate is graded here.
**This section can only TIGHTEN the GPU apparatus. It loosens nothing.**

### 11.1 WITHDRAWN — §9's GPU cost approval

§9 records, under the heading **"Sanaa's GPU cost approval, verbatim (2026-08-23,
chief's session record)"**:

> regarding the GPU COST it's fine you have my approval.

**The attribution is WITHDRAWN. The text stands as a relayed paraphrase.** From this
date that sentence reads as **wording relayed to the closure team, not as Sanaa's
verbatim words.** §9's text is kept exactly as written and is not altered or struck.

**Why.** Under a control-fired, non-ignoring `find | xargs grep -F` across the whole
worktree, that sentence exists in **exactly two files, and both are closure's own**:
this file (§9) and `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/PREREGISTRATION.md`
§F.1. `git log --all -S"regarding the GPU COST"` over `docs/ cases/` returns **exactly
two commits, and both are closure's**: `112b61b8` (2026-08-23 21:07:18Z, this file's
§9) and `e8309b6c` (2026-08-23 21:18:12Z, the arm-1 freeze). It is carried **nowhere**
on the chief's standing-directives section of `docs/LAB_STATE.md`, **nowhere** in
`docs/DOCKET.md`, **nowhere** in `docs/CROSS_TEAM_GATE_AUDIT.md`, **nowhere** in the
untracked harness session logs under `/home/ubuntu/harness-state/`, and **nowhere**
under `/home/ubuntu/notes/`.

**Controls fired on every one of those negatives** (rule 3's discipline applied to a
documentary search — a zero from a reader not shown able to see a non-zero is not
evidence): on the same worktree apparatus *"all the teams have my approval for
everything"* returned 2 files and *"R3: Sparta"* returned 6; on the same
`git log --all -S` apparatus *"R3: Sparta"* returned 8 commits; on `docs/LAB_STATE.md`
*"i approve of everything"* fired at line 55; on `docs/DOCKET.md` *"apporve"* fired at
line 861; on `/home/ubuntu/harness-state/` *"GPU quota"* fired in `msg8.txt`; on
`/home/ubuntu/notes/` *"delegation"* fired in three files. **The apparatus can see.
It does not see this sentence outside closure's own two records.**

**Class: SELF-ASSERTED ONLY.** Against the audit classes now standing: **C UNSOURCED**.

**This is the load-bearing one, and it is being reported against closure's own
favour.** That sentence is the *authorisation of record* in §F.1 of the arm-1
pre-registration and the cost authority under which the lab's first GPU run was
made. Withdrawing its attribution removes authority this team relied on.

**It is NOT a claim the words are not Sanaa's.** She may well have said exactly this,
and §8's separate record that **she launched `gpu1` herself** — an owner action no
agent can take — remains a real, independently meaningful act by her that is not
withdrawn. The finding is only that **closure cannot source the sentence to any
artefact on this disk independent of the two records asserting it, and will not
vouch for it. It is REVERSIBLE the moment Sanaa confirms**, in one line, with nothing
else re-opened.

**The frozen file is NOT edited.** `Ling2016_TBNN/gpu/PREREGISTRATION.md` §F.1 carries
the same sentence and is **frozen** (`e8309b6c`, sha registered) with arm 1 already
graded **NOT A RESULT**. It is left untouched. Whether a dated rule-6 addendum is
owed at its foot is the closure supervisor's call, not a lane's. Likewise
`cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md`, whose Arm-1 paragraph leans
on this quotation, carries its own foot note of this date; and closure's section of
`docs/LAB_STATE.md` (the phrase *"under Sanaa's verbatim GPU cost approval"*) is a
shared-board section this lane does not write.

### 11.2 NOT WITHDRAWN — §10 ruling 1, the self-shutdown mechanism and the stop

> GPU shutdown suggestion: yes approved (also i stopped that instance).

**This one is TRACEABLE and is NOT withdrawn. Reported loudly, because it is the
finding that protects the record rather than the one that damages it.** The same
apparatus finds it carried on **`docs/LAB_STATE.md` line 61 — the CHIEF's
standing-directives section** (lines 39–221, outside closure territory and not
closure's to write), landed at commit `123a3b92`, and again in
`docs/CROSS_TEAM_GATE_AUDIT.md` line 1521 (verification team, commit `9573db65`).

**Two honest caveats, stated rather than smoothed:**
1. The gate audit **explicitly cites `GPU_CAPABILITY_STATE.md` §10 as its source**,
   so it is a **relay of this very file** and is **not** independent corroboration.
2. `docs/LAB_STATE.md`'s row landed at **16:27:21Z**, sixteen minutes **after**
   closure's own `e88b86e6` at **16:11:47Z**. Ordering therefore cannot establish
   which record is primary, and **independence is not verifiable from git here** —
   every commit in this repository shares one Ubuntu identity.

**Class: TRACEABLE, by the letter of the standard (an artefact outside closure
carries it) — but honestly, B CORROBORATED-BY-REPETITION-ONLY, the dangerous
middle.** It is not withdrawn, because withdrawal of a quotation that another team's
board carries is not closure's to make. It is flagged here for the verification
team's standing **ATTRIBUTION INTEGRITY** sweep.

### 11.3 PARTIALLY WITHDRAWN — §10 ruling 2

> Good for the dispatched work, i approve of everything.

**Split finding.** The operative clause *"i approve of everything"* **is TRACEABLE**:
it is on the chief's standing-directives section at `docs/LAB_STATE.md` line 55. The
**prefix *"Good for the dispatched work,"* is SELF-ASSERTED ONLY** — under the same
control-fired search the full sentence exists only in this file (§10) and in
`Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md` line 10, both closure's.

**Therefore: the attribution of the PREFIX is withdrawn** and the sentence stands as
*"i approve of everything"* (attributed) **plus a relayed framing** ("Good for the
dispatched work,"). §10's text is kept exactly as written. **This narrows the
approval's recorded scope, it does not widen it** — and rule 9 already governed it:
a blanket is not a per-item read, and every GPU run still carries its own
GPU-hour `cost_basis`.

### 11.4 Effect on the arm-2 launch gate — TIGHTENED, never relaxed

Arm 2 remains **`PENDING` and UNFIRED. Nothing launches.** The arm-2
pre-registration and `run_all_gpu_v2.sh` are **frozen and were not touched.** The
three components of the launch gate, re-read against this section:

| gate component | rests on a withdrawn attribution? | state |
|---|---|---|
| Sanaa's own words giving the go | **Partly — see 11.3.** The go-clause *"i approve of everything"* is traceable; the framing is not; and the **cost** authority behind the GPU line (11.1) is **withdrawn**. | `LAUNCH_CHECKLIST.md` step 1 already requires her authorisation **quoted verbatim with its source**, pasted into the checklist before step 2 and **quotable back to her**. That step now covers the **cost** approval as well as the go. |
| Sanaa starts the instance | **No.** An owner action; no agent can take it, and no quotation stands in for it. | UNCHANGED. She starts it or it does not start. |
| Her two console readings (shutdown-behaviour attribute; the g6.xlarge us-east-2 on-demand price) | **No.** Both are registered as readings **still to be taken**, not as quotations already held. The $0.8048/GPU-h figure is labelled *published price list, retrieved 2026-08-23* — an artefact with a URL, a JSON path and a retrieval stamp, **not** an attribution to anyone. | UNCHANGED and still owed. |

**Net effect: strictly tighter.** A gate whose cost authority is now recorded as a
relayed paraphrase is a gate that needs Sanaa's word more, not less.

### 11.5 Scope

Records only. **Zero compute: 0.0 core-minutes** — no solver, no training, no GPU, no
run directory created, **no instance started**. Nothing sent, filed, uploaded,
registered, posted or commented: **SUBMISSIONS PARKED** (`CLAUDE.md` rule 7) stands.
No charter, `CLAUDE.md`, `.claude/`, `docs/LAB_STATE.md`, `docs/DOCKET.md`,
`docs/LESSONS.md`, `docs/COST_CALIBRATION.md` or any frozen file was edited. Owner:
closure.
