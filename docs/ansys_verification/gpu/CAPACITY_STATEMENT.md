# CAPACITY STATEMENT — AWS g6 capacity in us-east-2

**DRAFT, `ansys-lane-opus48` for `ansys-verification-supervisor`, 2026-08-25. Zero
compute; no instance or AWS endpoint contacted.**

## The question

Sanaa's sequence boots a `g6.xlarge` (NVIDIA L4) in us-east-2. Two distinct things must
both be true for that boot to succeed:

1. **Quota** — the account is *permitted* the instance. **GRANTED**: All G and VT, 8
   vCPUs, us-east-2, AWS support 2026-08-22 (`GPU_CAPABILITY_STATE.md` §1). A `g6.xlarge`
   is 4 vCPU and fits.
2. **Capacity** — AWS *has* a `g6.xlarge` to give in us-east-2 at boot time. Quota being
   granted does **not** guarantee capacity; `InsufficientInstanceCapacity` is a separate,
   time-and-AZ-varying condition.

## The answer

**Capacity: UNKNOWN.**

- `docs/GPU_CAPABILITY_STATE.md` does **not** record whether AWS capacity is currently
  available. It records that Sanaa **did** launch `gpu1` on 2026-08-23 (§8) and **did**
  stop it on 2026-08-24 (§10) — which proves capacity existed *at those moments in
  us-east-2c* — but says **nothing** about capacity **now** (2026-08-25) or on the next
  boot.
- **I do not infer present capacity from the 2026-08-23 launch.** Capacity is not a
  property that persists; a successful launch two days ago is not evidence of capacity
  today, and treating it as such would be exactly the kind of stale inference this lab's
  rules forbid. A stopped instance's **restart** is generally more likely to find capacity
  than a fresh launch (AWS holds nothing for a stopped instance, but the AZ is fixed to
  us-east-2c), yet "more likely" is not "known," and I will not dress it as known.

## Why I record UNKNOWN rather than test it

I could not establish present capacity without an AWS API/console call, which is not mine
to make (this box has no AWS CLI; launching/booting is Sanaa's owner action, rule 9). The
honest state is therefore **UNKNOWN**, written as UNKNOWN, not inferred from the prior
launch and not softened.

## What settles it, and when

Capacity is settled **at boot**, by Sanaa, and only then:

- If the start/launch **succeeds**, capacity was available — record the fact with its UTC.
- If it returns `InsufficientInstanceCapacity`, capacity is absent **right now**; the
  standard mitigations are retry, a different AZ within us-east-2 (subject to the fixed AZ
  of a stopped instance and to where the data volume lives), or a wait. None of that is an
  agent action.

**This statement gates nothing on its own** — it exists so the record does not silently
assume capacity. It should be updated to KNOWN (with a UTC and the outcome) the moment
Sanaa attempts the boot, per Sanaa's sequence.
