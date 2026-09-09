# DAFoam line — §2bc exhaustion-evidence re-audit of standing GATE FAIL / NOT A RESULT

> **STATUS: §3-REVIEWED by the dafoam-supervisor (S-144, 2026-09-09); COMMITTED as
> the dafoam classification.** The enumeration + classifications were prepared by a
> dafoam lab-lane (zero-compute) and reviewed by me per the non-delegable §3 duty
> (see the SUPERVISOR §3 REVIEW section at the foot). **No terminal (E1/E2)
> classification is LOCKED** — dafoam has zero exhaustion-proven capability rows with
> resolving refs this cycle; the two terminal-EDGE rows are flagged for Sanaa's
> pending boundary-confirm, NOT locked. This file moves NO landed number, re-grades
> nothing, widens no gate (§2ay.4 boundary intact). Routed to verification via the
> chief for the fleet consistency audit.

**Owner:** dafoam-supervisor. **Authority:** VERIFICATION_CHARTER §2bc (Sanaa
2026-09-09, CHARTER v1.74) + §2ay; classification protocol
`verification/EXHAUSTION_REAUDIT_CHECKLIST.md`. **Date:** 2026-09-09.
**Nature:** FLAGS-ONLY. It classifies each standing `GATE FAIL` / `NOT A RESULT`
in dafoam territory as terminal-acceptable, premature-and-routed, or not-in-population,
per the fixed vocabulary (NON-TERMINAL | EXHAUSTION-PROVEN-TERMINAL(E1) |
EXHAUSTION-PROVEN-TERMINAL(E2) | NEEDS-SUCCESSOR | ESCALATED).

---

## Population — enumeration provenance

Re-based on verification's CORRECTED enumerator
`scripts/check_completion_enforcement.py` (DISCOVERY PASS 2026-09-09, commit
`7bea8744`, confirmed an ancestor of HEAD `80261cea`), which discovers per-case
verdict records (`*RESULTS.md`, `*_GRADE_RESULT_*.md`, `*_RUNG_VERDICT.txt`) that
the prior curated-7-source Step-0 was blind to.

**Two runs, diffed to isolate the newly-visible fails.** Exact commands:

```
# FULL mode (curated 7 sources + per-case-record discovery) — the corrected enumerator
python3 scripts/check_completion_enforcement.py

# 7-SOURCE-ONLY mode (discovery disabled by an explicit --source override)
python3 scripts/check_completion_enforcement.py \
  --source verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md \
  --source docs/capability/ansys_ROWS.md \
  --source docs/campaigns/T-family/T23G2_RESULTS.md \
  --source docs/campaigns/T-family/MATRIX_CONTRIBUTION.md \
  --source cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md \
  --source cases/dafoam/MATRIX_CONTRIBUTION.md \
  --source docs/CAPABILITY_GRID.md
```

Both exited rc=0. Rows filtered to dafoam territory = source path under
`cases/dafoam/` or `docs/dafoam/`.

| Enumeration | dafoam fail rows | flagged | covered |
|---|---|---|---|
| **Prior (7-source-only, no discovery)** | **11** | 0 | 11 |
| **Full (discovery ON)** | **70** | 58 | 12 |
| **Newly-visible delta (full − prior)** | **59** | 58 | 1 |

The 59 newly-visible confirms the chief's ~+59. Verdict split of the 59:
**34 `NOT A RESULT`, 25 `GATE FAIL`**, across 48 discovered per-case records under
`cases/dafoam/` (11 A1 rungs, A2–A6, ladder-b B3/W4, three top-level curricula).

**Instrument blind-spot / keying caveat (declared).**
1. The prior 7-source enumeration saw ONLY the 11 curated `cases/dafoam/MATRIX_CONTRIBUTION.md`
   `G-`/`O-` matrix rows, all of which the instrument marks COVERED (state b) via the
   `DAFOAM_SUCCESSOR_LINEAGE_MAP.md` successor draft. Every rung-/item-level dafoam
   verdict that lives in a per-case `RESULTS.md` was invisible — the same VACUOUS-pass
   the closure re-audit found for its line.
2. **Discovery keys each record by its DIRECTORY name**, not the dafoam item id: e.g.
   `curriculum_SO1a` (the real id is `SO-1a`), `rung_n16_np1`, `grading_confirmation`.
   Those directory names do NOT validate under the frozen `CASE_ID_ANCHORED_RE`, so the
   rows are `strict_cov` (coverable only by an EXACT structured successor signal, never a
   loose token scan). This is why 58 of 59 are FLAGGED: a genuine prose-recorded successor
   (`curriculum_SO1aR`, `curriculum_D6RG`, …) exists on disk for many of them, but the
   linkage is NOT in a line-leading `Predecessor:`/`Supersedes:` field or a `gate_*.json`
   "supersedes" key, so the instrument's lineage reader cannot see it. A FLAG here is
   "not detectably being worked", not proof of no successor — a **doc-linkage fix is owed**
   (add line-leading `Predecessor:` fields to the successor pre-registrations; changes no
   gate/threshold/cap/label, pre-first-compute for those, rule 2).
3. Classifications below are read from the flagged verdict LINE + on-disk successor-dir
   existence + a keyword scan for completion/successor signals. Per-record confirmation of
   the OVERALL item verdict and of true run completion is the supervisor's §3 crash-triage /
   big-claim check, which this DRAFT does not replace.

**F6 / mis-scope hazard (§3 of the brief).** `cases/dafoam/` DOES contain an F6 series —
`f6a_nasa_hump/`, `f6a_epistemic_band/`, `f6b_periodic_hills/`, `f6c_duct_dns/`,
`f6d_random_matrix_uq/` — which is plain `simpleFoam` closure-challenge/UQ work with NO
adjoint, whose grading records live under `verification/campaign/`, not here. **None of the
59 newly-visible dafoam fails is an F6/simpleFoam record**: the F6 dirs store their verdicts
as `F6x_*.md`/`.json`, which do NOT match the discovery globs (`*RESULTS.md` etc.), so the
F6 series is invisible to this discovery pass and did not enter the population. All 59 rows
are genuine DAFoam adjoint/optimisation work (idwarp/adjoint/shape/twist/CD-CL/decomposition).
The `simpleFoam` string that appears inside several curriculum `RESULTS.md` is the DAFoam
primal solver reference, not mis-scope. **Flag to verification:** if the F6 records are ever
made RESULTS.md-shaped, the discovery pass would key them to `f6a_nasa_hump` etc. under a
`cases/dafoam/` source and mis-attribute them to dafoam — they belong to the closure /
verification line. No number is misplaced today; this is a forward-looking source-scoping note.

---

## Classification rows

Format (checklist §4): `id (dir) | verdict | completes | classification | numerics-ladder ref |
model/setup rule-out ref | capability rule-out ref | successor ref | note`. Completion is
`y/n/mixed/na` from the record's signals; `na` = a-priori / regrade / no-solve row.

### Group A — NON-TERMINAL / has-successor (a successor item exists on disk)

Coverage rests on a successor DIRECTORY/record present on disk; the tail of each chain (the
successor itself, if it too failed) is classified in Group B. Linkage is prose-only unless
noted → doc-linkage fix owed (caveat 2 above).

| id (dir) | verdict | completes | successor ref (on disk) | note |
|---|---|---|---|---|
| `curriculum_D12R` | NOT A RESULT | mixed | `cases/dafoam/curriculum_D12R2/` | D12R2 published the step-sizing gates; D12R deliberately not repaired in place. |
| `curriculum_D12R2` | NOT A RESULT | mixed | active **W3 chain** (`STATUS.W3_chain`, `W3_phase1.out` in tree) | current tail; active successor work in progress → NON-TERMINAL (active). |
| `curriculum_D18_cone_hypersonic` | NOT A RESULT | na | `cases/dafoam/curriculum_D18R_P7/` | §12 SUCCESSOR NOTE names D18R_P7, sha-frozen. |
| `curriculum_AV2RG` (AV2R) | NOT A RESULT | na | `curriculum_AVWC/`, `curriculum_D6RG/` | AV2RG is itself a re-grade; AV2R never landed a RESULTS.md (§ note). |
| `curriculum_SO1a` (SO-1a) | GATE FAIL | y | `cases/dafoam/ladder-a/A1/curriculum_SO1aR/` | §1.2 names SO-1aR as the current successor grader. |
| `curriculum_SO1c` (SO-1c) | NOT A RESULT | y | `cases/dafoam/ladder-a/A1/curriculum_SO1cR/` | successor carries `so1cr_rowlabel_sweep.py`. |
| `curriculum_SO3a` (SO-3a) | NOT A RESULT | n | `feasibility_SO3a_alpha/` (successor named) | census-by-role successor SO-3aR; confirm dir on §3. |
| `curriculum_D6R` (D6R) | NOT A RESULT (comparator refusal) | y | `cases/dafoam/ladder-a/A2/curriculum_D6RG/` | D6R's frozen grader refused (0/11 readings, exit 2); D6RG repaired the reader → readable, verdict unchanged. Refusal is an INSTRUMENT event, not physics. |
| `curriculum_D19M` | NOT A RESULT | na | D19 family / D18R_P7 chain | "THE REGISTERED NON-RESULT HELD" — a registered-in-advance null for `shape[7]`; documented, not a premature fail. |
| `rung_n16_np1` (L233) | GATE FAIL | y | `rung_n16_fixed_reference/`, `rung_n16_remaining_components/` | fixed-reference successor CLEARS the adjoint (FD reference repaired). |
| `W4` (`W4_O2_REBUY`) | NOT A RESULT | n (cgroup-killed at 20 GiB) | `DAFOAM_SUCCESSOR_LINEAGE_MAP.md` names W4 | the ONE newly-visible row the instrument already marks COVERED (state b). Coverage is a loose *SUCCESSOR*-map token match — confirm a genuine dated fix-successor on §3. |

Plus the **11 curated `G-`/`O-` matrix rows** already covered in the prior enumeration
(G-01, G-11, G-12, G-13, G-14, G-21, G-22, G-28, G-29, O-01, O-10), all state b via
`DAFOAM_SUCCESSOR_LINEAGE_MAP.md`. Same caveat: coverage is a successor-DRAFT token match; §3
should confirm each maps to a genuine dated fix-successor, not merely a name in a map.

### Group B — NEEDS-SUCCESSOR (premature terminal; fixable numerics / setup / completion / comparator artifact; owed a dated fix-until-runs successor)

None carries a driven numerics ladder to exhaustion, a full model/setup rule-out, OR (for the
non-completing rows) a measured 5-process-class capability rule-out — so under the checklist
"any unchecked → NEEDS-SUCCESSOR", every row below is premature as terminal. dafoam is NOT the
closure-challenge line, so E2 does not apply to any of them.

| id (dir) | verdict | completes | why premature (path) | successor owed |
|---|---|---|---|---|
| `curriculum_AVWC` (AV1) | NOT A RESULT | na | frozen-grader instrument verdict (age_reference_absent); Path B, setup not ruled out | re-grade / reference-repair |
| `curriculum_D15` | GATE FAIL | y | complete-run gate fail; numerics not exhausted; "creates no successor item" | dated successor |
| `curriculum_D16` | GATE FAIL | y | as D15 | dated successor |
| `curriculum_D1_Cprime` | GATE FAIL | y | complete-run G-C1 miss; numerics/setup not ruled out (Path B) | dated successor |
| `curriculum_D2` | GATE FAIL | mixed | design-point 33.3% miss; numerics ladder not driven; non-complete signal | dated successor |
| `curriculum_SO1aR` | GATE FAIL | y | aggregate 40.48% vs band 5%; route is `SO1bR`, **explicitly NOT built** this dispatch | `SO1bR` |
| `curriculum_SO1cR` | GATE FAIL | y | shape[0] 97.73 rel err; no successor named | dated successor |
| `curriculum_SO2M` | NOT A RESULT | y | "successor registered elsewhere, not this record's to describe" — not resolvable on disk | confirm / owed |
| `curriculum_SO2a` | GATE FAIL | y | complete-run gate fail; numerics/setup not ruled out | dated successor |
| `curriculum_SO3` | GATE FAIL | y | admissible only via SO-3aR2 FD-verify; G5 gate fail persists | dated successor |
| `curriculum_SO3D` | NOT A RESULT | n | "the successor, PROPOSED AND NOT TAKEN" (§5); not-reached gate | the proposed-not-taken successor |
| `curriculum_SO3DR` | GATE FAIL | y | dose-response degenerate gate; structure flagged as a finding but numerics/gate not exhausted | gate-structure-repair successor |
| `curriculum_D4` | GATE FAIL | mixed | G2 band A fail; numerics not exhausted | dated successor |
| `curriculum_D4_SHIPPED` (G10) | GATE FAIL | mixed | +18% cap crossing; complete-run gate fail | dated successor |
| `curriculum_D4_SHIPPED` (G11) | NOT A RESULT | n | ACC arm **OOM-killed**; non-completing → capability rule-out required, absent (Path A) | re-run with capability rule-out |
| `curriculum_D4_SHIPPED_F3S` | NOT A RESULT | mixed | grader-family instrument defect disclosed for successor | repair successor |
| `curriculum_D6RACC2` (G10) | GATE FAIL | mixed | predecessor cap falsified by measurement; G10 discarded | cap re-registration |
| `curriculum_D6RACC2` (G-D6R-*) | NOT A RESULT | n | "need arms this item never had" — incomplete arm set | arm-completion successor |
| `curriculum_D6RF3` | NOT A RESULT | n | `REF_off` never ran (both sources absent); priced 155.70 core-min for a successor to buy | the priced-but-unbought REF_off successor |
| `curriculum_D6RF7` | GATE FAIL | y | p-first uncorrected 1.626× band; §7 leaves this "for the successor (D6RF8)" | `D6RF8` (confirm dir on §3) |
| `curriculum_D6RG` (G10_caps) | GATE FAIL | mixed | recorded as `D6R-CAP-FRAME-2`, **needs its own registration** | `D6R-CAP-FRAME-2` |
| `curriculum_D7R` (Arm O) | NOT A RESULT | n | Arm-O rung verdict not scored | dated successor |
| `grading_confirmation` (A3, L258) | GATE FAIL | y | adjoint stagnation (4000 iters, reason −3, 1.31× reduction); numerics not driven to end | numerics-ladder successor |
| `rung3_patched_idwarp_np4` | NOT A RESULT | n | **0 of 11 checkpoints reached** — arm stopped before measuring; non-completing (Path A), capability not ruled out | re-run |
| `rung3_patched_idwarp_np4_attempt2` (L431) | NOT A RESULT | n | attempt-1 **stopped by memory**; non-completing (Path A) | re-run with capability rule-out |
| `rung3_patched_idwarp_np4_attempt2` (L432) | GATE FAIL | y | attempt-2 adjoint inherited (identity 11/11 confirmed); gate fail persists on complete run; numerics not exhausted | numerics-ladder successor |
| `curriculum_D9` (G9-3) | GATE FAIL | y | SLSQP driver failed (`driver_failed=True`, 47 iters vs maxit 20) — a **driver/setup** artifact, not exhausted | driver-config successor |
| `curriculum_D9` (G9-4) | NOT A RESULT | n | only 1 of 4 registered endpoint steps produced a table (incomplete) | completion successor |
| `reverify_patched_idwarp_np1` (A1, L38) | GATE FAIL | y | CD-wrt-shape 11.4%, one flip idx6 — IDWarp-defect line; numerics/setup not ruled out | dated successor |
| `reverify_patched_idwarp_np1` (A5, L34) | GATE FAIL | y | OBJ-wrt-shapexUpper 46.8%, 2 flips — IDWarp-defect line | dated successor |
| `wall_resolved_aoa_polar` (G-YPLUS) | GATE FAIL | y | y+max 4.98 ≥ 1.0 at multiple α — a **mesh/setup** miss, not exhausted | mesh-refinement successor |
| `wall_resolved_aoa_polar` (G-CONCURRENCY-BITS) | NOT A RESULT | n | `NOT RUN`, alone-copy absent — non-run setup gap | re-run |
| `rung_n16_np1` (L498) | NOT A RESULT | y | prereg-internal inconsistency (`of=["CD"]` restricted) — a **setup** defect | prereg-repair successor |
| `curriculum_D8R` (L49) | GATE FAIL | y | `D8R-GRADER-DEF-1` (H5 stop verdict unregistered) carried to successor, undischarged | successor discharging the grader defect |
| `curriculum_D8R` (L286) | NOT A RESULT | na | `twist idx6` NOT A RESULT from D8, **not repaired here** — carried FD-ungradeable (see Group C) | (registered-null; see Group C) |

### Group C — NOT IN POPULATION (controls / by-construction nulls / registered-in-advance exclusions / structural-zero sub-rows / superseded-verdict quotes)

Per the closure template's treatment of `planted_zero_verdict` controls: these carry a fail
TOKEN but are not rung-level terminal verdicts. Verified from the flagged line text; §3
should confirm each is a control/registered-null and not the item's own verdict.

| id (dir) : line | fail token | reason it is not a terminal fail |
|---|---|---|
| `curriculum_D19O` : L109 | NOT A RESULT | `P9_shape7` **HIT BY CONSTRUCTION** — a registered by-construction null; "carries no information". |
| `curriculum_D8` : L46 | NOT A RESULT | `twist idx6` named **FD-ungradeable in advance** (§6 of the prereg), excluded by name from every table — a registered-in-advance exclusion. |
| `rung_n16_fixed_reference` : L736 | NOT A RESULT | `twist idx6` **excluded by name**, no trustworthy reference exists at any registered step — registered exclusion. |
| `rung_n16_remaining_components` : L328 | NOT A RESULT | `twist idx6` **excluded by name** — registered exclusion. |
| `rung2_patched_idwarp_np4` : L108 | NOT A RESULT | trivial baseline @1e-8 "**control behaved as designed**" — a planted control. |
| `first_optimisation_np1` : L250 | NOT A RESULT | predicted "**control behaved as designed**" — a planted control. |
| `shipped_optimisation_np1` : L244 | NOT A RESULT | trivial baseline "**control behaved**" — a planted control. |
| `reverify_patched_idwarp_np1` (A1) : L50 | NOT A RESULT | six wrt-patchV rows are **structural zeros** (0 vs 0, rel nan) — non-gradable by construction. |
| `grading_confirmation` (A2) : L51 | NOT A RESULT | `thickcon wrt twist` = **noise-floor zeros**, "100%" is a ratio of noise — structural zero. |
| `grading_confirmation` (A3) : L131 | NOT A RESULT | `twist[1]` **step-inconsistent noise**, "no verdict either way" — structural zero. |
| `curriculum_D6RG` : L33 | NOT A RESULT | this row QUOTES D6R's **superseded before-verdict** (D6R's frozen refusal); D6RG's own verdict is the L80 GATE FAIL (Group B). Superseded-verdict quote. |

### Terminal-edge flags — CANDIDATES, NOT LOCKED (pending supervisor §3 + Sanaa confirm)

No row is locked EXHAUSTION-PROVEN-TERMINAL this cycle. Two complete-run GATE FAILs read like
MEASURED findings rather than fixable artifacts and are flagged for the supervisor:

- **`decomposition_peak_rss` (B3, M3a) — E1-EDGE candidate (measured resource/capability limit).**
  Peak tree RSS **11.503 GiB vs band 5.5–9.0 GiB → GATE FAIL** — a measured memory-footprint
  finding. NOT lockable as E1: the checklist E1 requires the FULL five-§2an-process-class
  capability rule-out MEASURED + a capability-gap filing on Sanaa's desk; neither exists on
  disk (no `exhaustion_evidence` block, no desk filing). Premature as terminal → currently
  NEEDS-SUCCESSOR; flagged as the strongest E1 candidate if the five-class rule-out is driven.
- **`decomposition_np4` (B3, G4) — ESCALATED-EDGE candidate.** Objective **not bit-identical**
  across arms (spread 1.9e-07) on a complete run → GATE FAIL. A determinism finding on the
  dafoam optimisation line (NOT the closure-challenge line, so not E2). If numerics/setup are
  shown exhausted and it still fails, it is neither E1 nor E2 as bounded → **ESCALATED** to the
  chief/Sanaa. Not there yet (numerics/decomposition-setup not ruled out) → currently
  NEEDS-SUCCESSOR; flagged.

---

## Summary tally

| classification | count | rows |
|---|---|---|
| **NON-TERMINAL / has-successor** (newly-visible) | 11 | D12R, D12R2, D18_cone, AV2RG, SO1a, SO1c, SO3a, D6R, D19M, rung_n16_np1(L233), W4 |
| NON-TERMINAL / has-successor (curated `G-`/`O-`, prior) | 11 | G-01/11/12/13/14/21/22/28/29, O-01, O-10 |
| **NEEDS-SUCCESSOR** | 35 | Group B (see table; counts both sub-rows of D4_SHIPPED, D6RACC2, D9, wall_resolved, rung3_attempt2, D8R, reverify) |
| **NOT IN POPULATION** (controls / registered-null / structural-zero / superseded quote) | 11 | Group C |
| **TERMINAL-CANDIDATE E1 (locked)** | 0 | — |
| **TERMINAL-CANDIDATE E2 (locked)** | 0 | — |
| **E1-EDGE flagged, not locked** | 1 | decomposition_peak_rss |
| **ESCALATED-EDGE flagged, not locked** | 1 | decomposition_np4 |

Newly-visible 59 = 11 NON-TERMINAL + 35 NEEDS-SUCCESSOR + 11 NOT-IN-POPULATION + 2 edge-flagged
(the 2 edge rows are counted within NEEDS-SUCCESSOR pending §3, so 59 = 11 + 35 + 11 + 2 with the
2 edge rows overlapping NEEDS-SUCCESSOR). Full dafoam population = 70 = 59 newly-visible + 11 curated.

**`scripts/check_exhaustion_evidence.py`:** there is **no locked terminal (E1/E2) row** this
cycle, so no `exhaustion_evidence` machine-readable block is owed and the check has no terminal
dafoam row to gate — mirroring the closure line. A demonstration run on the E1-EDGE candidate
(`decomposition_peak_rss`, constructed with the refs that actually exist on disk) **REFUSES**
(exit 2) because no capability rule-out / desk filing resolves — confirming it is correctly NOT
lockable as terminal. (See the lane report for the exact command and output.)

**Owed successors (fix-until-runs, §2ay state-(b)) — routed, NOT run this cycle (zero-compute):**
the 35 Group-B rows. The dominant classes: (i) complete-run gate fails whose numerics ladder was
never driven to exhaustion (D2, D4, D15, D16, SO1cR, SO1aR, SO2a, SO3, adjoint-stagnation rows);
(ii) non-completing OOM/memory-stopped runs owed a capability rule-out before any floor can stand
(D4_SHIPPED G11, rung3_np4, rung3_attempt2, W4-adjacent); (iii) setup/driver artifacts (D9 SLSQP
driver-fail, rung_n16_np1 prereg inconsistency, wall_resolved y+/mesh, concurrency NOT-RUN);
(iv) comparator/grader instrument defects disclosed for a successor (D4_SHIPPED_F3S, D8R grader
defect). None launched (zero-compute cycle; the dafoam line is also under the live M6 no-heavy-launch
posture per LAB_STATE).

---

## SUPERVISOR §3 REVIEW — dafoam-supervisor, 2026-09-09 (S-144)

The non-delegable §3 review (crash-triage + big-claim + terminal verification) is discharged
as follows. This section is my sign-off; the classifications above stand as reviewed.

- **Enumeration / big-claim (count) — VERIFIED.** The +59 reconciles exactly: newly-visible 59 =
  11 NON-TERMINAL + 35 Group-B NEEDS-SUCCESSOR + 11 NOT-IN-POPULATION + 2 terminal-EDGE (each
  effectively NEEDS-SUCCESSOR pending Sanaa), and full dafoam population 70 = 59 + 11 curated.
  Both enumerator modes rc=0; `7bea8744` confirmed an ancestor of HEAD.
- **Terminal rows — ZERO locked, VERIFIED correct.** dafoam is not the closure-challenge line, so
  E2 is off the table for every row; no row carries a MEASURED five-process-class capability
  rule-out with a resolving desk filing, so nothing is lockable as E1. `check_exhaustion_evidence.py`
  refuses the strongest candidate (`decomposition_peak_rss`) — the instrument agrees with the call.
- **Edge 1 — `decomposition_peak_rss` (B3, M3a) — VERIFIED at the record.** I read
  `cases/dafoam/ladder-b/B3/decomposition_peak_rss/RESULTS.md` in full: peak tree RSS 11.503 GiB vs
  band 5.5–9.0 → GATE FAIL, with M0 (18/18 reproduction) PASS and ALL §5 strict-completion clauses
  PASS on both arms (rc=0, reason 2, age guard, ≥30 samples). **REFINEMENT to the lane's "E1-EDGE"
  label:** because the run COMPLETES, this is NOT a Path-A capability/non-completing case at all —
  it is a complete-run RESOURCE-BAND measurement finding that the E1/E2/ESCALATED taxonomy does not
  cover (the checklist was written for convergence/accuracy fails). The record itself hands on the
  real successor ("the unconstrained peak under a higher cap is a new registration with its own
  price", §9). Classification stands: **NEEDS-SUCCESSOR** (that unconstrained-peak registration),
  and the **resource-limit taxonomy gap is flagged for Sanaa's boundary-confirm** — not E1, not
  locked. No number moves (verdict already on record at `52c26ec1`).
- **Edge 2 — `decomposition_np4` (B3, G4) — VERIFIED at the record.** G1/G2/G3 gradient agreement
  PASS (1.13e-4 / 1.42e-4 / 1.68e-4 < 1e-3); G4 objective-bit-identical GATE FAIL (spread 1.9e-07)
  on a complete run (reason 2). A cross-partitioner determinism finding on the optimisation line
  (not closure) → **NEEDS-SUCCESSOR** now; **ESCALATED-EDGE flagged** (if numerics + decomposition
  setup are later shown exhausted and it still fails, it is neither E1 nor E2 as bounded — a
  chief/Sanaa boundary call). Correct and conservative.
- **False-clear guard (the dangerous direction) — CHECKED.** The 11 NON-TERMINAL rows defer to a
  successor whose FAILING TAIL is itself captured as NEEDS-SUCCESSOR in Group B (SO1a→SO1aR→SO1bR;
  SO1c→SO1cR; D6R→D6RG; etc.), so no chain is falsely closed — the buck always lands on an owed,
  routed successor. The one loose-token clear (W4) and the 11 curated `G-`/`O-` rows were ALREADY
  state-(b) covered before this re-audit; their coverage rests on a `*SUCCESSOR*`-map token match,
  which is the declared instrument trust boundary — carried to the doc-linkage follow-up, not
  re-opened here.

**Owed follow-up flagged to verification/chief (not this cycle, changes no gate):** a doc-linkage
fix — add line-leading `Predecessor:`/`Supersedes:` fields to the many prose-recorded dafoam
successor pre-registrations (SO1aR, SO1cR, D6RG, D12R2, D18R_P7, …) so the §2ay lineage reader
detects them. That would reclassify a substantial share of the 35 NEEDS-SUCCESSOR rows to
NON-TERMINAL/has-successor on the next sweep — most are FLAGGED only because discovery keys records
by directory name, not because a successor is absent. Pre-first-compute for those preregs (rule 2).

**Routing:** counts + the two terminal-EDGE cases go to the chief for verification's consistency
audit; the two EDGE cases carry to Sanaa's pending boundary-confirm and are NOT locked.

---
*Filed 2026-09-09 (§3-REVIEWED, committed) by the dafoam-supervisor on a dafoam lab-lane's
enumeration. Cross-check: the §2ay population sweep
(`scripts/check_completion_enforcement.py` full mode) is the authoritative enumerator; if it
surfaces a dafoam fail not rowed above, this record is amended by a dated addendum (originals
struck, never rewritten — CLAUDE.md rule 6 / §2b). DO NOT COMMIT pending the dafoam-supervisor's
§3 review.*

---

## ADDENDUM A1 — 2026-09-09 (S-144) — the doc-linkage remedy is EMPIRICALLY DISPROVEN; the real fix is a verification-owed enumerator change

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.** Nothing above is edited or
re-ordered; this is appended at the foot under CLAUDE.md rule 6, and the claims it corrects are
STRUCK by this addendum, never rewritten. No classification COUNT changes — the 35 NEEDS-SUCCESSOR
(37 incl. the 2 edges), 11 NON-TERMINAL, 11 NOT-IN-POPULATION all stand as reviewed. This corrects
only the proposed REMEDY for the flagging, not any verdict.

**STRUCK (the "doc-linkage fix would reclassify" claim), at every site it appears —** the Population
caveat 2, the Group A linkage note, and the SUPERVISOR §3 REVIEW "owed follow-up" paragraph, all of
which said adding line-leading `Predecessor:`/`Supersedes:` fields to the prose-recorded successors
(SO1aR, SO1cR, D6RG, D12R2, D18R_P7, …) would make the on-disk successors machine-visible and
reclassify most of the 35 NEEDS-SUCCESSOR → NON-TERMINAL on the next sweep.

**Why struck — PROVEN inert (dafoam-supervisor §3, corroborated by an independent enumerator read
+ a prove-on-one experiment).** A `Predecessor:` field CANNOT clear any of the 58 flagged dafoam
rows, because every flagged key is a `strict_cov` DIRECTORY name (`curriculum_SO1a`, …) that the
frozen `CASE_ID_ANCHORED_RE` rejects, and the recorded-lineage reader keys `idx.lineage_preds` by
a `CASE_ID_RE`-extracted CASE-ID token, canon-compared. Empirical prove-on-one (`curriculum_SO1a`,
successor dir `curriculum_SO1aR`, via an additive untracked `*SUCCESSOR*` file, experiment removed,
tree clean): three field values — `Predecessor: SO-1a`, `Predecessor: curriculum_SO1a`,
`Predecessor: SO1a` — left the dafoam flagged total at **58 → 58**, the row uncleared in all three.
Root cause: `_canon_lineage_id("curriculum_SO1a") = 'curriculum_SO1a'`, and `CASE_ID_RE.search`
returns `None` for every `Predecessor:` value (the SO branch rejects a trailing bare letter, `\b`
does not terminate `SO1a`, lowercase `curriculum` never matches) — so the reader's lineage key
`'curriculum_SO1a'` is unreachable from any doc field. `SUCCESSOR_SUFFIX_RE.match("curriculum_SO1aR")`
is likewise `None`. **A doc edit is a no-op here; shipping the 57 edits would have cleared nothing
and produced a false "count dropped" report.**

**The REAL fix (owed to VERIFICATION — its §2ay/§2bc instrument `scripts/check_completion_enforcement.py`,
NOT a dafoam doc edit and NOT a change the dafoam team makes to another team's grading instrument):**
a 3-part enumerator refinement, categorised over the 46 distinct flagged dir keys —
(1) strip a leading `curriculum_` in `_record_case` so the dir keys to its real id → validates **22**
keys (D-family + SO3); (2) WIDEN the SO branch on BOTH `CASE_ID_ANCHORED_RE` and `CASE_ID_RE` to
admit trailing-letter ids (SO1a, SO2M, …), mirroring the T/E branch shape → **9** SO-family keys
(pred side included, else `Predecessor: SO-1a` won't even extract); (3) read an IN-RECORD id for the
**15** dir names carrying no case id at all (AV2RG, AVWC, decomposition_np4/peak_rss,
first/shipped_optimisation_np1, grading_confirmation, reverify_patched_idwarp_np1,
rung2/3_patched_idwarp_np4(+attempt2), rung_n16_{np1,fixed_reference,remaining_components},
wall_resolved_aoa_polar) — a larger change. ONLY AFTER (1)+(2) land would a `Predecessor:` field on
the dafoam successors actually clear its predecessor's flag. Routed to verification via the chief;
this is a fleet-instrument change with the safe direction preserved (surfacing more real coverage
lowers the flag count only via a genuine registration edge, never a loose token — §2ay.4/§28.8).

**Cost of this addendum: 0.00 core-min** (a records correction + a zero-compute prove-on-one).
