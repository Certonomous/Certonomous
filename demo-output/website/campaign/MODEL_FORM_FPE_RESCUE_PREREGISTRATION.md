# FPE-rescue pass — the four dead k-family cells under declared initializations: pre-registration

Written 2026-08-08 by the Cases family supervisor, **before the pass is
launched**. Chief-approved successor to the paired FPE diagnosis
(`FPE_DIAG_runs/FPE_DIAG_PREREGISTRATION.md`, verdict SHARED-BY-CLASS
(initialization), commit `9c4fbef4`). Machine spec:
`MODEL_FORM_runs/seeded_init_fpe_rescue.json`, read by the runner's new
`--seeded-init` (committed with this file).

## The rule that governs everything here

**The STANDING GATE decides admission exactly as for any member — no
criterion is softened anywhere.** The only change per cell is the initial
field state, each the tested cure from the diagnosis arm, each stamped into
the record's `initialization` block. A cell that converges under a
physically-better initialization is a member, full stop (the chief's
wording, binding); a cell that fails any gate clause is excluded exactly as
before, initialization noted.

## Seeding assignments, per cell (frozen here)

| cell | declared initialization | why (diagnosis-arm evidence) |
| --- | --- | --- |
| `H_re10595_kEpsilon` | k and epsilon seeded per-cell from the converged same-case kOmegaSST field (`F6b_runs/medium/5997`), epsilon = 0.09·k·omega cell-wise | the uniform derived init explodes globally (min eps 4.96e+45 by iter 13); HL1 survived 230× past the crash under this seed |
| `B_re1p2e7_kEpsilon` | potentialFoam init (Phi block per the F8 §12 lesson) | impulsive uniform start at nu 8.3e-8 diverges locally in momentum; BL1 survived 45× past the crash under this init |
| `B_re1p2e7_kOmegaSST` | potentialFoam init | same class, same lever, tested on this exact cell as BL1 |
| `B_re1p2e7_realizableKE` | potentialFoam init | same class by signature (crash iter 44, momentum divergence) |

Backstops: the families' own (H 12,000; B 12,000 = `BATCH_BACKSTOP`).
Gates: the families' own, verbatim (H: residualControl sentence +
exactly-two-crossings steady bubble + compliant mesh; B: sentence + S12 +
mesh + born-clean at entry). A potentialFoam failure is itself an exclusion
reason ("declared potentialFoam initialization failed"), never silently
skipped.

## Restatement branches, pre-declared

**Family B_re1p2e7** (currently 0 converged of 4; SA's backstop-stall record
stands untouched — no initialization was diagnosed for it and none is
applied):
- ≥2 of the three rescued cells admit → **family B's first band ever**,
  stated as an interval. No containment question exists at this regime (the
  batch carries no published reference at re1p2e7), so no containment
  verdict is possible regardless of n — stated now so nobody reads a band
  as a verdict.
- 1 admits → member stated, no band (the ≥2 rule).
- 0 admit → family B's no-band state stands, now with the crash class cured
  into (at best) the same stall its re3e6 sibling shows — itself
  informative.

**Family H** (currently n = 1, kOmegaSST):
- kEpsilon admits → **n = 2: the interval is stated and the containment
  verdict is STILL REFUSED below n = 3** (third live application of the
  n<3 rule). **n = 3 is UNREACHABLE from this pass**, stated plainly: SA is
  excluded on physics (converged bubble-less, its own record) and
  realizableKE is closed at the pre-declared 30,000 boundary — neither is
  in scope and neither verdict reopens here.
- kEpsilon excluded (stall, or converges without a steady bubble — the SA
  precedent makes this a live branch) → H stays n = 1, refusal stands.

## Predictions, put at risk

- **R1:** no cell crashes (S1/S2) — the cures hold at full length (the
  diagnosis arm proved survival to 3,000/2,000; the backstop asks for
  12,000).
- **R2:** `B_re1p2e7_SpalartAllmaras`-style stalls reappear: the three bump
  cells, cured of the crash, stall against the U 1e-08 target like every
  `B_re3e6` cell did — predicted outcome: family B stays band-less, with
  the exclusions converting from crash to stall. Declared alternative: the
  potential-flow start lands them close enough to converge — then family B
  gets its first band.
- **R3:** `H_re10595_kEpsilon` converges (HL1's residuals were falling at
  3,000) — and the risky half: it carries a **steady bubble** (exactly 2
  crossings), entering the family at n = 2. Named risk: the SA precedent —
  it converges bubble-less and is excluded on clause 3; either way the
  containment verdict remains refused below n = 3.

## Budget and mechanics

Measured basis: B cells ≈ 2.3–2.5 core-min each at the 12,000 backstop
(×3 ≈ 7.5); H kEpsilon ≈ 7–14 (hills rate). **Expected ≈ 15–21; budget
`--max-core-min 25`.** Launch: one runner invocation, `--redo-excluded`
(the four records supersede, never delete), `--seeded-init` with the
committed spec, setsid-detached, serial, queue gate live. Records carry
`levers_verified_active` mechanically (launcher echo) and the
`initialization` stamp; band regeneration is the runner's own end-of-run
`write_band()`. Watch handoff: the runner process and
`MODEL_FORM_runs/runner.log` are the state; any session collects with
`--list` and the band artifact.

*Nothing below this line existed when the pass was launched.*
