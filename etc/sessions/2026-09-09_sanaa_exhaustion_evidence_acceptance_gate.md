# Sanaa directive — 2026-09-09 — the exhaustion-evidence acceptance gate for a terminal GATE FAIL / NOT A RESULT

**Provenance.** Sanaa, online 2026-09-09, setting a lab-wide standard in her own words, relayed
verbatim to the verification-supervisor by the chief this session. A new standard is reserved to
Sanaa (CLAUDE.md rule 9 / FIRST-ACTION RULE); this capture records her exact words so the standard
cites her, not a paraphrase — matching the §2az / §2ba / §2bb capture precedent.

## Verbatim

> "per our rule, gate fail/ not a result are only valid entries if we have exhausted that its a
> numerics or model issue and that genuinly openfoam cant run it. Else not acceptable."

## What it means (chief's articulation; only the quote above is Sanaa's)

A `GATE FAIL` or `NOT A RESULT` is not an acceptable TERMINAL entry unless it carries exhaustion
evidence proving the failure is not a fixable numerics or model/setup artifact:
1. numerics exhausted (the fix-until-runs numerics ladder driven to its end — scheme/limiter/
   relaxation/timestep/grid — not a single attempt);
2. model/setup ruled out (BC, solver choice, staging/config, decomposition eliminated);
3. capability limit proven by measurement (the five-process-class OpenFOAM-can't-run-it rule-out,
   for a non-completing run).
Without this the verdict is premature → REJECTED → routed to a dated successor (fix-until-runs).

The gate is "prove it isn't a fixable numerics/setup artifact," NOT "never report a fail."

## The terminal exemptions (so teams don't loop forever) — BOUNDARY PENDING SANAA'S CONFIRM

- (E1) a MEASURED capability limit (the rule-out complete) — the case genuinely cannot run in OpenFOAM;
- (E2) for the closure-challenge line whose PRODUCT is measuring model error, a genuine model-accuracy
  miss WITH numerics already exhausted (the miss is the measurement).

The chief has asked Sanaa to confirm these two are the complete terminal set. The standard operates on
this boundary now; if Sanaa narrows or widens it, her words supersede by dated addendum.

## Where it landed

- Standard: `VERIFICATION_CHARTER.md` §2bc (v1.74, 2026-09-09) — "THE EXHAUSTION-EVIDENCE ACCEPTANCE
  GATE," strengthening §2ay (the fix-until-runs enforcement). Binds all six teams; flags-only /
  refuse-at-record, moves no landed verdict.
- Enforcement instrument: `scripts/check_exhaustion_evidence.py` — validates the `exhaustion_evidence`
  field of a terminal fail record and REFUSES (exit 2) an un-evidenced one; two-limb plant.
- Fleet-wide re-audit checklist: `verification/EXHAUSTION_REAUDIT_CHECKLIST.md` (the chief dispatches
  the per-team sweep on it so all six audit consistently).
- Composes with: §2ay (locates the fails; this defines terminal acceptability), §2an (closure-ladder
  routing = E2), the non-convergence standard §4 (mandatory completion; OpenFOAM-can't-run-it = E1),
  §2bb (per-rung pre-flight — stops process failures masquerading as terminal fails), and the M6 line
  (V-134: a premature "geometry/BC" terminal was correctly overturned when the numerics ladder was run).
