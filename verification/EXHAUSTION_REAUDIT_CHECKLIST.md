# Fleet-wide re-audit checklist — exhaustion-evidence classification of every standing GATE FAIL / NOT A RESULT

**Owner:** verification-supervisor. **Authority:** VERIFICATION_CHARTER §2bc (Sanaa 2026-09-09) +
§2ay (fix-until-runs). **Purpose:** the chief dispatches a per-team sweep on this checklist so all six
teams classify their standing `GATE FAIL` / `NOT A RESULT` entries CONSISTENTLY as
**EXHAUSTION-PROVEN-TERMINAL** (may stand) vs **NEEDS-SUCCESSOR** (premature → dated successor).
Flags-only: this re-audit moves NO landed number; it decides whether a fail may STAND as terminal or
must be routed. It refuses nothing on its own — it CLASSIFIES, and a NEEDS-SUCCESSOR row is owed a
dated fix-until-runs successor.

## Step 0 — enumerate

Run `scripts/check_completion_enforcement.py` (the §2ay sweep) for your team; it enumerates every
landed `GATE FAIL` / `NOT A RESULT`. Every enumerated fail gets a row in your team's re-audit output.
(Do not hand-pick; the sweep is the population.)

## Step 1 — is it already NON-TERMINAL? (§2ay state-(b))

- Does an ACTIVE dated fix-successor already exist (a `*PREREGISTRATION*`/`*SUCCESSOR*` with a
  line-leading `Predecessor:`/`Supersedes:` naming this fail, or a `gate_*.json "supersedes"`)?
  - **YES →** classify **NON-TERMINAL / has-successor**. Out of §2bc scope; the successor carries it.
    No exhaustion evidence owed yet (it is owed when the successor is CLAIMED final). Record the
    successor ref. Done.
  - **NO →** the fail is being claimed TERMINAL. Continue to Step 2.

## Step 2 — does the run COMPLETE? (rule 4)

- **Run does NOT complete** (rc≠0 / no End / last-time≠endTime / crash / timeout-incomplete): this is a
  CAPABILITY question. Component 3 (capability rule-out) is REQUIRED. Go to Step 3, path A.
- **Run COMPLETES but fails its gate** (a graded GATE FAIL on a complete run): this is a NUMERICS /
  MODEL question. Components 1–2 required. Go to Step 3, path B.

## Step 3 — the exhaustion test

**Path A — non-completing run (capability):**
- [ ] The five-process-class OpenFOAM-can't-run-it rule-out is COMPLETE and **MEASURED** (not inferred,
      not a single crash). Ref: __________
- [ ] Numerics exhausted where relevant (a crash is often a numerics artifact — the M6 lesson: a
      nonphysical blow-up co-located with a limiter pin is NUMERICS until the max-robustness ladder is
      run). Ref to the driven numerics ladder: __________
- [ ] Model/setup (BC, solver, staging, decomposition) ruled out as the crash cause — the D6RF9-R3/R4
      lesson: a decompose-collision rc=59 is a SETUP artifact, NOT a capability limit. Ref: __________
- **All checked with resolving refs →** EXHAUSTION-PROVEN-TERMINAL under exemption **E1** (measured
  capability limit). Goes to Sanaa's desk as a capability-gap filing (§2ay state-(a)).
- **Any unchecked →** **NEEDS-SUCCESSOR** (premature). The crash/timeout is a fixable numerics/setup
  artifact until proven otherwise (D6RF9-R2 timeout = unmeasured deadline, D6RF9-R3/R4 = decompose
  collision — both NEEDS-SUCCESSOR, and §2bb pre-flight prevents the recurrence).

**Path B — complete run, gate failed (numerics/model):**
- [ ] Numerics ladder driven to its END — scheme, limiter, relaxation, timestep, grid — recorded, not a
      single attempt. Ref: __________
- [ ] Model/setup ruled out (BC, solver choice, config). Ref: __________
- **Both checked with resolving refs, and the fail persists →** classify by line:
  - **Closure-challenge line** (product IS measuring model error): EXHAUSTION-PROVEN-TERMINAL under
    exemption **E2** — a genuine model-accuracy miss with numerics exhausted is the finding (§2an).
  - **Any other line:** a persistent complete-run gate fail with numerics exhausted and model/setup
    ruled out, that is NOT the closure line's model-error product, is **ESCALATED** to the chief/Sanaa
    (it is neither E1 nor E2 as currently bounded — the pending-confirm boundary decides it).
- **Any unchecked →** **NEEDS-SUCCESSOR** (premature): the gate fail may be a fixable numerics/model
  artifact; drive the numerics ladder / rule out setup before it may stand.

## Step 4 — record the classification (uniform output, so all six read the same)

For each fail, emit one row into your team's re-audit record with these fields:

    case/rung id | verdict (GATE FAIL|NOT A RESULT) | completes (y/n) |
    classification (NON-TERMINAL | EXHAUSTION-PROVEN-TERMINAL(E1) | EXHAUSTION-PROVEN-TERMINAL(E2) |
                    NEEDS-SUCCESSOR | ESCALATED) |
    numerics_ladder_exhausted ref | model_setup_ruled_out ref | capability_rule_out ref |
    successor ref (if NON-TERMINAL) | note

An EXHAUSTION-PROVEN-TERMINAL row must additionally carry the machine-readable `exhaustion_evidence`
block (§2bc.4) so `scripts/check_exhaustion_evidence.py` passes on it; run that check on each terminal
row before submitting. A NEEDS-SUCCESSOR row is owed a dated fix-until-runs successor (§2ay state-(b));
name the owed successor. An ESCALATED row goes to the chief.

## What this checklist does NOT do

It does not re-grade a number, widen a gate, or convert a fail into a pass (§2ay.4 boundary). It
classifies terminal acceptability and routes premature fails to successors. The refs it names must
RESOLVE (a paper ref citing nothing is not evidence); whether the referenced ladder was truly driven to
exhaustion is the supervisor's crash-triage / big-claim check (§3), which the classification does not
replace.
