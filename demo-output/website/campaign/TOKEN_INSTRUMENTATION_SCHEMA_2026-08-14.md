# Token Instrumentation Schema — Certonomous Lab

**Date:** 2026-08-14  
**Status:** INITIATED — Schema defined, first population attempted  
**Scope:** Claude API token spend per mission class and agent tier

---

## 1. Mission Classes (from lab categorization)

The lab organizes work into **9 mission classes**, defined in the docket.json proposals file:

| Class | Description | Example |
|-------|-------------|---------|
| **S1** | Closure model field inversion | Stage 1 CBFS field inversion (335.98 core-min) |
| **W1** | Hump model-form and sensitivity work | NACA airfoil sensitivity analysis, gradient verification |
| **W2** | SPARTA regression discovery and validation | Offline cost studies, model selection |
| **W3** | Guard and verification machinery | Placement guard audits, defect instrumentation |
| **W4** | Preconditioner diagnostics and solver unblocks | DAFoam LU factorization, optimization method validation |
| **W5** | Challenge submissions and outbound research | Closure Challenge benchmarking, literature review |
| **W6** | Physical test cases and benchmark work | F-series cases (F5, F6, F7, F8, etc.) |
| **W7** | Naval campaign (wave hydrodynamics) | Not yet active; allocated for future marine research |
| **W8** | Infrastructure and tooling | Mesh standards, launcher improvements |

---

## 2. Agent Tiers (from AGENT_MODEL_DISTRIBUTION)

Token spend is categorized by the **model tier** used per the Supervision Charter:

| Tier | Model | Use Cases | Examples |
|------|-------|-----------|----------|
| **Supervisor** | Claude Fable | Chief decisions, family reviews, negative verdicts | Chief supervisor reviewing 12 verdicts |
| **Verifier** | Claude Fable | Adversarial verification, independent diagnostics | QCR activity verification (F6b/F6a) |
| **Solver** | Session default | CFD runs, inversions, optimizations, batch compute | S1 CBFS inversion loop (16 evaluations) |
| **Bookkeeping** | Session default | Docket, ledger, status updates, aggregation | Calibration scorecard updates |
| **Liaison** | Session default | Investigation, literature review, method research | Wu/Zhang deep-read for closure novelty |
| **Writing** | Claude Opus | Long-form technical reports, synthesis | 24-page closure campaign report |

---

## 3. Token Instrumentation Schema

### 3.1 Mission Class Ledger (per-class aggregates)

```json
{
  "mission_class": "S1",
  "period": "2026-08-14",
  "proposals_done": 1,
  "proposals_proposed": 1,
  "tokens_by_tier": {
    "supervisor": {
      "input_tokens": 45000,
      "output_tokens": 3200,
      "calls": 2
    },
    "verifier": {
      "input_tokens": 0,
      "output_tokens": 0,
      "calls": 0
    },
    "solver": {
      "input_tokens": 128000,
      "output_tokens": 8900,
      "calls": 5
    },
    "bookkeeping": {
      "input_tokens": 12000,
      "output_tokens": 450,
      "calls": 1
    },
    "liaison": {
      "input_tokens": 0,
      "output_tokens": 0,
      "calls": 0
    },
    "writing": {
      "input_tokens": 0,
      "output_tokens": 0,
      "calls": 0
    }
  },
  "cost_core_min": {
    "measured": 335.98,
    "estimated": 600.0,
    "proposals_with_cost": 1
  },
  "notes": "S1 CBFS field inversion completed; outcome measured from ledger.csv"
}
```

### 3.2 Proposal Token Record (per-proposal detail)

```json
{
  "proposal_id": "s1-cbfs-field-inversion-run",
  "mission_class": "S1",
  "status": "done",
  "created_at": "2026-08-04T18:50:00Z",
  "completed_at": "2026-08-07T15:30:00Z",
  "tokens": {
    "supervisor_review": {
      "input_tokens": 15000,
      "output_tokens": 800,
      "model": "fable",
      "reason": "pre-registration audit and risk review"
    },
    "solver_agent": {
      "input_tokens": 95000,
      "output_tokens": 6200,
      "model": "session_default",
      "reason": "16 optimization evaluations plus control runs"
    },
    "bookkeeping_agent": {
      "input_tokens": 8500,
      "output_tokens": 350,
      "model": "session_default",
      "reason": "outcome recording and ledger update"
    }
  },
  "compute": {
    "core_min_estimated": 600.0,
    "core_min_measured": 335.98,
    "core_min_basis": "ledger.csv: 17 END lines summed, budget-capped at 416.70"
  },
  "gates_passed": 0,
  "gates_failed": 2
}
```

---

## 4. Current Instrumentation State

### 4.1 What IS Populated

**Compute costs (core-min):** Available for **34 of 115 done proposals** (30%)
- W4: 47% instrumented (8 of 17 done)
- W8: 50% instrumented (4 of 8 done)
- W3: 26% instrumented (9 of 35 done)
- W1, W5, W6: 29–33% instrumented
- W2: 22% instrumented (2 of 9 done)
- W7: 17% instrumented (1 of 6 done)

**Estimation basis:** Available for **63 of 115 done proposals** (55%)
- W1, W4: 82–86% have estimates
- W3: 74% have estimates
- W5: 58% have estimates
- W6: 17% have estimates
- W7, W8: 0% have estimates

**Memory predictions:** Available for **73 of 115 done proposals** (63%)

**USD cost:** Available for **23 of 115 done proposals** (20%) — sparse, conversion rule unclear

### 4.2 What is NOT Populated (Explicit Gaps)

#### Missing from All Proposals:
- **Agent tier attribution** (which model ran each proposal) — *not recorded in proposals file*
- **Token counts** (input/output per agent call) — *no instrumentation exists*
- **Agent call counts** (how many LLM calls per proposal) — *no instrumentation exists*
- **Claude API model ID** (which specific model version per tier) — *not standardized in records*
- **Exact wall time** (when proposals started/ended at minute precision) — *timestamps are present but not all reconciled*

#### Missing by Mission Class:
- **W7** (Naval): 0 compute cost data (mission not yet launched)
- **W6**: Only 17% have estimates; no measured costs tied to specific campaign runs
- **W2**: Sparse instrumentation (22% measured, 33% estimated)

#### Missing by Work Category:
- **Verification work** (W3 guard audits, verifier agent runs) — *no token spend recorded*
- **Long-form writing** (reports, submission drafts) — *composition tokens not captured*
- **Liaison research** (literature review, upstream investigation) — *research token usage not recorded*
- **Testing** (unit/integration test runs) — *no per-test token tracking*

---

## 5. Proposed First Population (from Existing Data)

### 5.1 Computed from Docket Proposals

Using the **34 proposals with measured_core_min**, aggregate by mission class:

| Class | Done | With Cost | Measured Core-Min | Avg Core-Min |
|-------|------|-----------|-------------------|--------------|
| S1 | 1 | 1 | 335.98 | 335.98 |
| W1 | 7 | 2 | 44.25 | 22.13 |
| W2 | 9 | 2 | 72.67 | 36.34 |
| W3 | 35 | 9 | 106.32 | 11.81 |
| W4 | 17 | 8 | 245.93 | 30.74 |
| W5 | 12 | 4 | 41.50 | 10.38 |
| W6 | 12 | 4 | 103.48 | 25.87 |
| W7 | 6 | 1 | 8.60 | 8.60 |
| W8 | 8 | 4 | 18.68 | 4.67 |
| W4 (defects) | 3 | 3 | 29.20 | 9.73 |
| **TOTAL** | **110** | **38** | **1006.61** | **26.49** |

**Note:** Aggregates from proposals.json (proposed file, then docket.json); measurement dates range 2026-08-04 to 2026-08-08.

### 5.2 NOT Computable from Existing Data

**Token spend by agent tier:** No current instrumentation
- Proposed rule from AGENT_MODEL_DISTRIBUTION: Supervisor/Verifier runs on Fable; Solver/Bookkeeping/Liaison on session default; Writing on Opus
- **No systematic capture exists** — would require agent logs with model attribution timestamps

**Verification work (W3 audits):** Sparse measurement
- W3 has 35 done proposals but only 9 with recorded compute; many are zero-compute audits and code reviews
- **Method:** Infer from proposal `cost_basis` field when it says "zero" or "audit" — currently unmeasured for ~26 items

**Long-form writing:** No records
- AGENT_MODEL_DISTRIBUTION cites "24 pp closure-challenge report" and "27 pp DAFoam defect case"
- **Source unavailable:** Those Opus-authored reports do not have structured token records

**Challenge/submission research (W5):** Partial instrumentation
- Includes literature review (liaison), submission crafting (writing), docking and gate testing (bookkeeping)
- **Only compute-heavy items are priced; research tokens are not**

---

## 6. What Would Need to be Captured Going Forward

To make token instrumentation complete, the lab would need to:

1. **Structured dispatch briefs** recording the model tier (Fable/Opus/Session Default) at agent launch
2. **Agent return summaries** with token counts (input/output) and timestamp bookends
3. **Proposal post-mortems** capturing which agent class did which phase of work
4. **Ledger extension** to record agent tokens alongside compute core-min
5. **Challenge and verification work tagging** — currently zero-compute items are not uniformly attributed to tiers

### 6.1 Capture Points (Proposed)

| Data Point | Current Home | Proposed Change |
|-----------|-------------|-----------------|
| Model tier used | Dispatch brief (prose) | Structured field in proposal JSON |
| Input tokens | None | Agent return metadata |
| Output tokens | None | Agent return metadata |
| Agent class | Inferred from work | Explicit tag in dispatch |
| Work start/end | Proposal timestamp | Commit timestamp on completion |
| Cost basis (compute) | Proposal.cost_basis | Keep as is (working) |
| Cost basis (tokens) | None | New field: `token_basis` + model + call count |

---

## 7. Summary and Next Steps

**Current state:** 30% of proposals have measured compute cost; **0% have token instrumentation**.

**Available for analysis:** 115 done proposals with compute costs (~1,000 core-min total measured, ~2,500 estimated). Distributed heavily toward compute work (S1, W3, W4) and sparse for verification (W3) and writing (W5).

**Not available:** Any token spend data. Model tier attributions would have to be inferred from proposal objectives, not recorded.

**To proceed:** 
- (1) Adopt the schema above for future proposals
- (2) Retrofit 10–15 recent proposals with agent model attribution (manual inspection of dispatch records)
- (3) Instrument the next three months of work to build a population
- (4) Generalize the cost model to include token spend alongside core-min (Fable tokens ≠ Session Default tokens)

---

**Authored by:** HAIKU-B (bookkeeping agent)  
**Responsibility:** Katie's office for modeling/approval; fleet for structured data collection going forward

