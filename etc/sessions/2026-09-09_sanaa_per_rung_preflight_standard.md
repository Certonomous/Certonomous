# Sanaa directive — 2026-09-09 — the per-rung / per-configuration pre-flight validation standard

**Provenance.** Sanaa, online 2026-09-09, minting a new lab-wide ENFORCED standard in her
own words, relayed verbatim to the verification-supervisor by the chief this session. A new
lab standard AND its enforcement are reserved to Sanaa (CLAUDE.md rule 9 / FIRST-ACTION
RULE); this capture records her exact words so the standard cites her, not a paraphrase,
matching the §2az / §2ba precedent
(`2026-09-08_sanaa_codify_convergence_standard_and_plain_english_status.md`,
`2026-09-09_sanaa_dual_mechanism_run_standard.md`).

## Verbatim

> "from now on, this should be a lab wide lesson ENFORCED every time bc im tired of these
> structural bugs. and yes for the fix."

Her "ENFORCED every time" is what makes this a GATING check, not merely a lesson document —
the enforcement instrument refuses an un-pre-flighted ladder at the freeze.

## What "this" and "the fix" refer to (the D6RF9 confound — chief's articulation, not Sanaa's words)

The standard's substance is the chief's articulation of the D6RF9 lesson Sanaa ordered
enforced; only the sentence quoted above is hers. The D6RF9 confound: a four-rung ladder
(D6RF9) was frozen and run, then 3 of 4 rungs came back CONFOUNDED —

- **R2 timed out incomplete** (rc=124, `final_time 200/2000`, rule 4 last-time ≠ endTime):
  its heavier config (12 non-orthogonal correctors) had a per-step cost that was never
  measured against its frozen wall-clock deadline, so it silently could not reach endTime.
- **R3/R4 crashed rc=59** on a latent `decomposePar` "already decomposed" collision (staged
  `mp0X` directories carried `processor*` dirs) — a path R1 never exercised.

The pre-flight that DID run verified the grading path and that R1 reached the solver, but
did NOT validate each rung's own config. "The fix": before a multi-rung / multi-config
ladder may be frozen, EACH rung must pass a pre-flight smoke that measures, on its OWN
artifact, (1) its deadline sizing and (2) its distinct solver/decomposition path
end-to-end.

## Where it landed

- Standard: `VERIFICATION_CHARTER.md` §2bb (v1.73, 2026-09-09) — "THE PER-RUNG /
  PER-CONFIGURATION PRE-FLIGHT VALIDATION STANDARD." Binds all six teams; gates the freeze;
  moves no verdict (flags-only, §2ay/§2ba boundary).
- Enforcement instrument: `scripts/check_ladder_preflight.py` — validates the
  `LADDER_PREFLIGHT.json` manifest and REFUSES (exit 2) any ladder not fully pre-flighted;
  carries its own two-limb plant (`--selftest`).
- Lesson: `L-511`.
- First live application: the D6RF10 B-300 endTime-shortening ruling (the plateau
  demonstration IS the pre-flight for the endTime/deadline lever).
