# VMFLGPU007 — THE BAND WAS FIXED BEFORE ANY CONVERGENCE PROBE RAN

**Written 2026-08-27, BEFORE the lab-box convergence probe, and committed with the
freeze so the ORDER of events is on the record and not merely asserted afterwards.**

## What is known at the moment this file is written

- The experimental reference: `reference/VMFL013_htc.xy`, Vogel & Eaton 1985 as digitised
  by Ansys — 19 two-column rows, **peak Nu = 64.8530 at x/H = 5.8209**.
- The manual's material properties, geometry table and turbulence model (p.243–244).
- That a 20-iteration smoke of this case runs `rc = 0` and writes every artefact.

## What is NOT known, and is deliberately NOT looked at before the band is fixed

**No converged Nusselt number of this lab's own solver exists, and the convergence probe
about to be run is instructed to print RESIDUALS and y+ ONLY.** It does not compute, print
or store a Nusselt number or a wall temperature. The probe exists to size two things that
are not gates — `endTime` (a duration) and the near-wall spacing (a wall-function validity
parameter) — and nothing else.

## THE BAND, fixed here, before the probe

| gate | band | why this number, from prior knowledge only |
|---|---|---|
| **C1 — peak Nusselt number** | `\|Nu_peak − 64.8530\| / 64.8530 ≤ 0.20` | Two independent contributions, added rather than tuned: (i) heat-transfer measurements of this class carry roughly ±5–8 % scatter; (ii) **standard k-ε with wall functions is documented to under-predict backward-facing-step reattachment and to mis-predict peak Nu by 10–20 %** — it is the best-known deficiency of this exact model on this exact flow. A band tighter than the model's own documented bias would fail the case for using the model the manual specifies. |
| **C2 — peak location** | `\|x_peak/H − 5.8209\| ≤ 1.5` (absolute) | The peak location is a LENGTH; a relative band on it would be arbitrary. 1.5 H is about a quarter of the measured reattachment-scale distance and is well inside the k-ε reattachment error of ~20–25 % of ~6 H. |

**Both must hold for limb C to hold.** C1 alone could be met by a curve of the wrong shape
peaking in the wrong place; C2 alone says nothing about magnitude.

## What this band CANNOT do, stated plainly

A 20 % band is wide because the model's own documented bias is wide, and that is registered
rather than hidden. It is still a real gate: a wrong wall flux, a wrong Prandtl number, a
wrong reference temperature or a mis-specified inlet would each move peak Nu by far more
than 20 %, and C2 would catch a curve that peaked in the wrong place. **What it does not do
is discriminate between good and excellent turbulence modelling, and no claim of that kind
will be made from it.**

**A limb C miss with limb B holding is a MODEL miss, not a GPU-path miss** — the GPU path
is still verified, because limb B (GPU ≡ forced-CPU to 1e-4) is the object under test and
is unaffected by turbulence-model bias. Registered here, before the run, so it cannot read
as an excuse afterwards.
