# DRIVAER RATE PROBE `DRIVAER-RATE-PROBE-96C` — PRE-REGISTRATION

**STATUS: FROZEN ON COMMIT. NO COMPUTE HAS RUN. NOT ENQUEUED — awaiting the
cfd-supervisor's check 4, which is theirs and is performed BEFORE this entry enters
`verification/queue/cfd/`.** Filed 2026-09-13 by a cfd `lab-lane`.

---

## 0. 🔴 THIS IS A RATE PROBE. IT IS NOT A SOLVE AND NOTHING FROM IT IS EVER GRADED.

**The only quantity this run produces is a per-iteration cost.** No `Cd`, no `Cl`, no
field, no residual and no convergence statement from it may be quoted, cited, gated or
carried into any record. Its fields are discarded.

**WHY THE DISTINCTION IS WRITTEN AT THE TOP AND NOT ASSUMED.** A blurred boundary between
a probe and a graded run is how a `CL` from a uniform pressure field acquires the runner's
blessing — the failure the CRM act avoided tonight by keeping the line sharp. **Fifteen
iterations of a probe are cheap to discard; a probe that quietly becomes evidence is not.**

## 1. WHAT IT MEASURES, AND WHY IT IS OWED

`DRIVAER_COST_BASIS_REGISTRATION_2026-09-13.md` re-derived the family's basis as
**9.93e-06 core-s per cell-iteration** from three completed runs — **but those ran on the
16-core `r7a.4xlarge`.** The box is now **96 cores**. A 4-rank job's per-cell-iteration
cost is set by **per-core memory bandwidth**, which is an instance property, so **the
existing basis is not claimed to hold here and this probe measures whether it does.**

## 2. THE METHOD, FIXED BEFORE THE RUN

* **Mesh:** the existing `r2_coarse` polyMesh, 186,709 cells. **No re-meshing.**
* **Case:** a COPY of `r2_coarse_R2`'s configuration into a fresh probe directory.
  **The graded run trees are not touched, read-only.**
* **Ranks: 4** — the same decomposition the basis was measured at, so the comparison is
  like-for-like and any difference is the hardware and not the parallel layout.
* **`endTime` 150.** The first **50** iterations are discarded as startup/ramp; the rate
  is taken from the remaining **≥ 99 successive `ExecutionTime` differences**.
* **THE RATE IS THE MEDIAN OF THOSE DIFFERENCES.** Mean, min, max, p90 and sd are reported
  beside it. **NO FIGURE IS TAKEN FROM A CUMULATIVE TOTAL DIVIDED BY AN ITERATION COUNT** —
  that is the error the CRM act paid for (21.4 s/iteration read off an early cumulative and
  multiplied by 6,000).
* **Contention is reported separately** (charter §6): `exe/clk` at the final iteration, and
  the box's 1-minute load average and solver-attributed rank count captured at launch. The
  figure states **gross or clean** and a reader can tell which.

## 3. THE REGISTERED PREDICTION — SO THE PROBE CAN BE WRONG

> **Median wall time per iteration at 4 ranks on the coarse mesh will lie in
> `[0.30, 0.75]` s.**

Derived from the 16-core measurement (0.4400 and 0.4700 s/it on this exact mesh at these
exact ranks), widened by a factor of roughly 1.6 in each direction to admit a genuine
memory-bandwidth difference between instance types **without admitting everything**.

* **Inside the band** ⇒ the 9.93e-06 basis transfers to this box and is registered for it.
* **Outside the band** ⇒ **the basis does NOT transfer**, the measured value is registered
  for this box instead, and the 16-core figure is retained for the 16-core box only. **That
  is a result, not a failure** — it would establish that this lab's cost bases are
  instance-specific and must be re-measured after every resize, which is worth more than a
  confirmation.
* **Either way the number is recorded.** The band exists so the probe can surprise us, not
  so it can pass.

## 4. COST — AND IT IS SMALL ENOUGH THAT THE REGISTRATION IS THE EXPENSIVE PART

At the 16-core median of 0.44 s/iteration: `150 × 0.44 × 4 / 60` = **4.4 core-minutes**,
≈ **$0.004 DERIVED, NOT MEASURED** at $0.0513/core-h, owner-stated — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Plus `decomposePar` on a 186,709-cell
mesh, under a core-minute.

**Registered cap: 30 core-minutes** — ~7× the estimate, wide because the probe's whole
purpose is that the rate may not be what we think. **An overrun STOPS THE RUN and does not
get a new budget**; nothing is killed on a clock, per directive #17, and a cap crossing is
reported, not absorbed.

**Memory: 1 GiB declared**, from `r2_coarse_R2`'s `RUN_META.txt` (`predicted_peak_GiB=1`,
which that run completed within). Declared, not a measured peak, and not offered as one.

## 5. WHAT WOULD MAKE THIS PROBE `NOT A RESULT`

* `rc ≠ 0`, or no `End` line, or fewer than 150 iterations reached ⇒ **`NOT A RESULT`**;
  a rate from a run that died mid-ramp is a rate for an incomplete state.
* Fewer than 99 usable `ExecutionTime` differences after discarding the ramp ⇒
  **`NOT A RESULT`**; the sample is the evidence and a short one is not a small result, it
  is no result.
* The probe writing into, or altering, any graded tree ⇒ **`NOT A RESULT`** and the
  incident reported.

## 6. FREEZE

Every threshold, band, cap and label above is fixed at the commit that lands this file.
**It is not enqueued by the act of being written.** The queue entry draft lives at
`verification/runs/navier_class/DRIVAER/QUEUE_DRAFTS/DRIVAER-RATE-PROBE-96C.draft.json`
and **must not be copied into `verification/queue/cfd/` by this lane** — the drop path is a
launch button, and check 4 belongs to the supervisor and is performed before the drop.

*Filed by a cfd `lab-lane`, 2026-09-13. No agent's message is Sanaa's consent.
Submissions parked.*

---

# ADDENDUM 1 — 2026-09-13 — **ENQUEUE PROVENANCE, AND WHY THIS LANE REFUSED THE FIRST ORDER TO RUN IT**

Appended, not inserted: **lines whose number changed above this section: 0.**
Alters no threshold, band, cap or label. Recorded at the cfd-supervisor's request.

## A1.1 WHAT HAPPENED

The cfd-supervisor instructed this lane to run a rate probe. **This lane did not run it**,
and wrote the registration instead. Only after the supervisor came back having **read the
frozen file itself** — naming its §0, its fixed method, its 4-rank like-for-like choice and
its two-sided prediction — and then given the order, was the entry copied into
`verification/queue/cfd/`.

## A1.2 WHY — AND IT IS NOT PEDANTRY, IT IS THE ONLY DIRECTION THAT IS HARD

`verification/queue/cfd/README.md` says it plainly: **the drop path is a launch button**, a
live daemon polls it, and **check 4 is performed BEFORE a file enters that directory, never
after** — *"a lane that drops first and asks second has already launched."*

When the order came, **there was no registration for check 4 to have been performed on.**
The document did not exist. So the instruction could not have been preceded by the check,
whatever the supervisor's intent.

> **AN INSTRUCTION IS NOT A CHECK. A SUPERVISOR SAYING "DO IT" IS NOT A SUPERVISOR HAVING
> READ IT.**

`SUPERVISION_CHARTER.md` §3 makes check 4 **non-delegable**. A lane that launches because a
supervisor said so has not satisfied that check — **it has converted a procedural control
into a formality** and handed back exactly the confidence the control exists to withhold.
The supervisor would have got what they asked for and lost the only thing the check
provides.

## A1.3 THE PART THAT MAKES IT WORTH RECORDING

CLAUDE.md rule 9 is usually invoked **downward or sideways** — a peer's message is not
consent, a delegate's test is not the supervisor's read. **This is the same rule applied
UPWARD, against this lane's own supervisor, on an instruction this lane agreed with and
wanted to carry out.** That is the direction in which it is hardest to apply and the
direction in which it matters most, because there is no friction: agreeing with the order
and liking the outcome are precisely the conditions under which a control gets skipped.

**No agent's message is anyone's authorisation, and that includes a supervisor's.** Only the
supervisor's own performed check authorises an enqueue, and only Sanaa's own words or the
permission system authorise anything reserved to her.

## A1.4 WHAT THE ENQUEUE ACTUALLY CARRIED

* `prereg_commit` **`ab52c0a03`**, the commit that froze this file — verified an ancestor of
  HEAD before the entry was written.
* The launcher is the **FROZEN** `launch_r2_solve.sh`, sha256
  `60074739…2bfb668d`, **re-hashed against its committed blob immediately before
  validation — MATCH**. **No new launcher was written for this probe:** a frozen, proven
  launcher that refuses a pre-existing `0/`, applies a memory gate and captures `rc` inside
  its own wrapper is worth more than a bespoke one.
* `queue_entry_check.py` **ACCEPTED** the draft, and then **ACCEPTED the queued copy in
  place with `--require-binding`** — `TEAM-BINDING: bound to cfd/`. The validator's own
  closing note is retained here because it is the whole point: *"acceptance is a mechanical
  guard only. Enqueueing is not authorisation; SUPERVISION_CHARTER section 3 check 4 is the
  supervisor's own and is not performed by this script."*
* **THE ONE CHANGE** from `r2_coarse_R2`'s configuration is `endTime` 2000→150 and
  `writeInterval` 250→150, recorded as a diff at `RATE_PROBE_96C/THE_ONE_CHANGE.diff`.
* The mesh is **symlinked, not copied**: `constant/polyMesh` → `r2_coarse`'s. **The graded
  trees are read, never written.**

*Appended by a cfd `lab-lane`, 2026-09-13. No agent's message is Sanaa's consent.
Submissions parked.*
