# Agent model distribution in the Certonomous lab

## Overview

This document records how the lab assigns agent tasks across model tiers (Haiku, Fable, Opus, session default). The distribution follows a single rule established in the Supervision Charter and proven across three months of execution.

**The standing rule** (SUPERVISION_CHARTER v1.0, section 5):

> **Family supervisors and adversarial verifiers run on Fable. Solver, bookkeeping and liaison agents inherit the session default. Long-form technical writing goes to Opus.**

The rule exists because judgment-heavy work (supervision, verification) and lengthy composition (research reports) demand stronger models, while mechanical solves and bookkeeping can run cost-effectively on the session default. Silent overrides in either direction are charter violations.

---

## Task distribution by class

| Task class | Model tier | Reasoning | Real examples (date) |
|---|---|---|---|
| **Chief supervisor** | Fable | The chief makes scoring calls, cross-family arbitration, and negative-verdict reviews. These are binding judgments that shape the record and cannot be delegated. The four personal checks of a supervisor (measurement-script diffs, crash triage, big-claim verification, pre-registration audits) are assumed-wrong verification work. | SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07 (chief personally conducted all 12 verdict reviews with independent diagnostics); adversarial verification on F6b QCR activity check (1a14e90b, 2026-08-08), A3 transonicPCOption arm (11b90d25, 2026-08-08), F8 BEM cross-check (6d806733, 2026-08-08) — each one an independent carry-through of a supervisor's judgment into record-grade findings. |
| **Family supervisors** | Fable | Four family supervisors (DAFoam/adjoint, Closure+UQ, Cases/campaigns, Infrastructure) conduct first-pass reviews of family state, issue written guidelines (FAMILY_SUPERVISION_GUIDELINES.md per family), and personally read the four checks of SUPERVISION_CHARTER §3 before family work is believed. DAFoam supervisor's first pass (770436f9, 2026-08-07) found A-1 sign-error live in the reusable cross-residual instrument and B-2 dead-path citation defects. Infra supervisor's first pass (675e2873, 2026-08-07) fixed 19 silently-dropped inbox files and three suite defects. Structure caught real defects in every family on day one. | DAFoam supervisor sweep on A4 decomposition (27d25762, 2026-08-04), rotation-patch verification (6782d33a, 2026-08-04), A1 serial adjoint kink trap (0858e640, 2026-08-07); Closure supervisor on closure-challenge metric definition (03814b0a, 2026-08-05) and gate verification; Cases supervisor on F6b ERCOFTAC mesh verification (242de6fd, 2026-08-05), B52 noise-floor measurement. |
| **Adversarial verifiers** | Fable | Independent diagnostics on big claims before they are repeated upward. Assume wrong until defended. The pattern is already on record: R4 regenerated a gate row from first principles; R7 re-derived the affected wall rows; R11 verified two supervisor sweeps on the grading convention before adopting it as policy. | QCR-activity verification on both F6b and F6a separated-flow legs (1a14e90b, 2026-08-08) — an agent that ran neither verified fields differed, model selection confirmed in logs, confound-closers traced to code (momentum equation, pressure extrema, internal velocity deltas). A1 serial adjoint kink trap closed (0858e640, 2026-08-07) by sweeping the FD to rule out the one axis that could gut the finding. |
| **Long-form technical writing (LaTeX)** | Opus | Closure-challenge campaign report (24 pp, 0249c6e9, 2026-08-05) and DAFoam defect case (27 pp, d7d87a05, 2026-08-05). Dispatched to Opus agents per Katie's 2026-08-05 directive. Pattern: every number artifact-traced, hedges preserved, companion to unfiled upstream reports. The reports scale beyond simple extraction — they synthesize findings across campaigns, integrate literature, and rewrite narratives when the evidence shifted (defect report reframed when branch hypothesis held; both Opus, not Fable). | Reports recompiled with amendments (defect report set with trigger addendum, 3640debd/f3d231b3, 2026-08-05; round-5 update on closure report, 49f71b8c, 2026-08-05). Opus owners designated to keep both current as submissions pending (Katie, 2026-08-07 restructuring directive). |
| **Solver and campaign runners** | Session default | High-volume mechanical work: solves, inversion loops, model-form batch cells, uncertainty propagation. Pre-registered before compute, ledgered after. Agents own completion and cost tracking. Inherit the session default model to minimize spend on pure computation. | S1 CBFS inversion (335.98 core-min, 2026-08-07, pre-reg e6321e95); model-form batch cell collection (a8f2329a/691eb11f, 22.5/120 core-min, 2026-08-05, idempotent after kills); UQ propagation ladder (44.7/100 core-min, 2026-08-05, 42 Monte Carlo + order-2 PCE); QCR2000 arms on F6a hump (6 core-min, 9d711efb, 2026-08-08) and F6b hills (c29a1a91, 2026-08-08); A3 sub-LU/transonicPCOption arms (0263d950/11b90d25, 2026-08-08, 15.2/30 + 7.33 core-min). |
| **Records / bookkeeping / docket agents** | Session default | Mechanical aggregation: ledger updates, status summaries, docket item filing and retrieval. No judgment, no composition beyond template application. Inherit the session default. | Morning report emitter (scripts/morning_report.py, e9ef5a78, 2026-08-04) and 26 tests; spend ledger catch on daily runs; supervisor negative-verdict docket filing (six proposals from entry 1 alone, filed 2026-08-08); S1 reinversion outcome recording (71dbf5a8, 2026-08-08). |
| **Liaison research** | Session default | Investigation and literature review in response to breakage or Katie's asks. Maintains a living problem-research protocol. Searches upstream issues, forums, literature. Compiles findings into method docs. | Liaison research on DIVERGED_NANORINF/PCILU (2026-08-05), DAFoam method-papers fetch+read (bf6ac53b, 2026-08-05 — surveyed parallel adjoint verification in literature), Wu/Zhang deep-read for closure-method novelty (393ad74f, 2026-08-05), community novelty sweep on the DAFoam defects (63 searches, 10 venues, zero prior reports — 3c74dc03, 2026-08-05). |
| **Lightweight documentation & audits** | Haiku | Extracting and organizing existing information without creating new knowledge: read-only surveys, data compilation, documentation pulls, fact-finding. This task (AGENT_MODEL_DISTRIBUTION.md) is the canonical example. No judgment, no inference, no synthesis — pure extraction. Haiku's speed and cost-efficiency suffice. | This document (reading charters, gathering real examples, formatting a table — 2026-08-08). |
| **Unspecified** | Chief's judgment | Tasks that don't fit the above categories or situations where the charter intentionally defers to Katie's call. | Example: charter section 5 allows "A dispatch that overrides this rule says so in the brief and says why." New task classes or edge cases between tiers are escalated. |

---

## How to choose the right model for a new task

If you are designing a task for this lab, ask these questions in order:

1. **Is this judgment-heavy work or verification?**
   - Does it require re-reading code, checking an argument against evidence, or defending a claim until it breaks?
   - Does it assume the output is wrong until proven right?
   - Is it one of the four personal checks (measurement-script diff, crash triage, big-claim verification, pre-registration audit)?
   - **→ Fable.** Includes chief supervisor, all four family supervisors, and adversarial verifiers.

2. **Is this long-form technical composition?**
   - Does it synthesize findings from multiple sources into prose, integrate literature, or write reports that shape the record?
   - Examples: 24-page LaTeX reports, method-paper companions, narrative rewrites when evidence shifts.
   - **→ Opus.** Long-form writing goes to Opus; short status updates and templates go to session default.

3. **Is this mechanical high-volume work?**
   - Solves, inversion loops, batch cell runners, ledger updates, docket filing, status summaries with no novel judgment?
   - Pre-registered before compute, output is ledgered, the task owns cost tracking?
   - **→ Session default.** Includes all solver/campaign runners, bookkeeping agents, and liaison research unless that research demands synthesis (e.g., method novelty sweep vs. responding to a specific breakage).

4. **Is this pure information extraction with no inference?**
   - Reading existing documents, gathering examples, organizing findings, formatting tables?
   - No creation of new knowledge, no synthesis beyond what the sources already state?
   - **→ Haiku.** Fast, cost-efficient, and sufficient. This task is the example.

5. **Does it not fit these categories?**
   - **Escalate to Katie.** The charter section 5 allows chief judgment for cases that don't fit the rule. Say what you need and why in your dispatch brief.

---

## Notes on the charter and enforcement

**What the charter leaves unspecified:**
- Hybrid tasks (e.g., an Opus report whose production requires some solver arms) are dispatched as two separate tasks: the solver (session default) and the report (Opus). Coordination is Katie's or the chief's.
- Single-agent multi-task roles (e.g., a solver agent that also maintains a ledger) inherit the session default. If the ledger tasks grow judgment-heavy, split the role.
- Liaison research sits at the boundary: mechanical searches inherit session default; synthesis of findings into new hypotheses escalates to Fable.

**Enforcement:**
- Section 7 of SUPERVISION_CHARTER: "Nothing mechanical verifies that a dispatch used the designated model. Those are checked by asking the section 1 question, and the honest state is recorded here so that the gap is a known gap." This document is part of that record. Silent overrides (upgrading a solver agent to Fable without saying why, or downgrading a supervisor to Haiku to save cost) are charter violations and discoverable after the fact.

**The rule in context:**
The model-designation rule is one of five rules in section 5 of the charter:
- *Family supervisors and adversarial verifiers run on Fable.* — The strongest model for judgment work and verification.
- *Solver, bookkeeping and liaison agents inherit the session default.* — Cost efficiency for mechanical work.
- *Long-form technical writing goes to Opus.* — A middle tier for synthesis and composition.
- *A dispatch that overrides this rule says so in the brief and says why.* — Transparency when exceptions are necessary.
- *A silent override is a violation, in either direction.* — Integrity of the model-selection discipline.

---

## See also

- `docs/charters/SUPERVISION_CHARTER.md` — The standing rule and the four personal checks that justify putting supervisors on Fable.
- `docs/charters/VERIFICATION_CHARTER.md` — The background on big-claim verification and what "assumed wrong until defended" means in practice.
- `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` — 12 worked examples of adversarial verification in action, each showing what a Fable-tier judgment task looks like on the record.
- `demo-output/website/dafoam/FAMILY_SUPERVISION_GUIDELINES.md`, `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md`, `campaign/CASES_FAMILY_SUPERVISION_GUIDELINES.md` — Family-specific rules from each supervisor's first pass.
- `docs/PRODUCT_LIST.md` — The 2026-08-05 changelog entry (lines 282–341) citing the Opus reports as precedent for long-form technical writing.
