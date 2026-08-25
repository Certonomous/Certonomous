# D10 CAPABILITY PROBE — RESULTS

## 1. Verdict

**`NOT A RESULT`.**

The grader refused, exit 2, on the probe's own planted control:

> `PLANTED-ZERO REFUSAL: a +1.234 K plant in 0/T moved HFX by only 0.000000e+00 relative (floor 1.0e-06). The reader has not been shown able to see a non-zero, so no HFX number here is evidence.`

Pre-registration frozen `c2913dcd`, Amendment 1 (before first compute) `c2ceab24`.
Grading path `d10_grade.py`, md5 `0ef3e76a83fa6baa88d5b0e3d28a300b`, verified against the
HEAD blob before the launch.

## 2. What ran

Three np=1 stages on a 720-cell 2D heated channel, image
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`. All three
`rc = 0`, `OOMKilled false`. The primal converged: *"Minimal residual
9.156898000411687e-09 satisfied the prescribed tolerance 1e-08"* at iteration 210.

| stage | task | rc | wall s | core-min | `HFX` |
|---|---|---|---|---|---|
| `base` | `compute_totals` | 0 | 11 | 0.1833 | `2846.286928273276` |
| `plant` | `run_model` | 0 | 7 | 0.1167 | `2846.286928273276` |
| `clean` | `run_model` | 0 | 7 | 0.1167 | `2846.286928273276` |

Artifacts: `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10/`.

## 3. The finding, and it is about the instrument

**The three stages agree to the last digit.** The plant was placed on the **initial
internal field** of `0/T`, and **a converged steady solve is independent of its initial
guess by construction** — the temperature boundary conditions were untouched, so the
solver was obliged to return the same answer. **That plant could not have moved the
objective whatever the capability did: the refusal was guaranteed before the container
started.**

**The refusal is therefore correct and the probe is what failed.** `CLAUDE.md` rule 3
exists precisely so that a number whose reader has not been shown responsive is not
banked, and it did its job on its author.

## 4. What is NOT claimed

The run produced `HFX = 2846.286928273276` and
`d(HFX)/d(patchV) = [197.7150296242168, −37.57503164797164]`, both finite and non-zero.
**Under the frozen mapping these are NOT results and are not quoted as the answer.** They
are recorded here as observations only, and the capability question is settled by
**D10-P′**, not by them.

## 5. Cost

**0.4167 core-min gross**, against a registered prediction of 2.5 and a cap of 5.0
(`0.167×`; the cap was never approached and the `CAP_CORE_MIN` guard never fired).
**= $0.000356 DERIVED, NOT MEASURED**, at $0.0513/core-h, c7a.4xlarge,
**reported-by-owner** (`COMPUTE_BUDGET_CHARTER.md` §5).

**All 0.4167 core-min is NAMED WASTE** under `COMPUTE_BUDGET_CHARTER.md` §6 — three
containers, no graded quantity — and is netted off nothing. It is not, however,
worthless: it bought the finding in §3, which is now carried in D10-P′'s freeze.
Calibration row **C-69**.

## 6. Successor

**D10-P′** (`../curriculum_D10_probe_Pprime/`), frozen `25c735ff`, re-plants the same
`+1.234 K` on the **heated wall's `fixedValue` boundary** — an input to the converged
answer — with the run script and case files **byte-identical**. Its verdict is
**`GATE REACHED`**.
