# DAFoam NEWER-ID VERDICT RECORD — landed post-Aug-25 fails, for §2ay enumeration

**Written 2026-09-07 by a `lab-lane` on the dafoam-supervisor's brief. ZERO COMPUTE.** The Aug-25
`cases/dafoam/MATRIX_CONTRIBUTION.md` predates the curriculum ids `D#`/`SO#`, so the completion
enforcer (`scripts/check_completion_enforcement.py`, §2ay) — which enumerates landed fails **only from
its declared SOURCES** — cannot see them. This file is the **enumeration record** for the newer landed
fails: it renders each as a verdict row so the enforcer can enumerate it, while the **coverage** for
each (its active dated fix-successor, state (b)) lives in the recorded-lineage `Supersedes:` fields of
`cases/dafoam/DAFOAM_SUCCESSOR_LINEAGE_MAP.md` §2.

**NOT FILED ANYWHERE. SUBMISSIONS PARKED** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

> **ACTION OWED BY VERIFICATION (their call, not taken here):** to have these rows enumerated, this
> file's path must be added to `DEFAULT_SOURCES` in `scripts/check_completion_enforcement.py`. That
> edit belongs to the verification-supervisor — the enforcer is their instrument. Until then these
> rows are inert to the default scan; a demonstration run passing this file via `--source` (below,
> §5 of the lane report) shows they enumerate AND clear once the source is present.

---

## 1. LANDED NEWER FAILS — enumerable verdict rows (coverage recorded in the lineage map §2)

Each `Case` cell carries an id the enforcer's `CASE_ID_RE` extracts cleanly; the `Verdict` cell is a
bare fail token so `_row_verdict` reads it; the successor column names the state-(b) attempt whose
`Supersedes:` field in the lineage map clears the row.

| # | Case | Verdict | mechanism measured | active fix-successor (state b) — coverage in `DAFOAM_SUCCESSOR_LINEAGE_MAP.md` §2 |
|---|---|---|---|---|
| **1** | **D6R** | `NOT A RESULT` | A2 compressible multipoint optimisation: no IPOPT EXIT; primal-acceptance failure (maxNonOrth over floor). | successor chain: the D6RF5 primal repair, then Stage-2, then the D6R2 multipoint re-run. |
| **2** | **D6RF4** | `NOT A RESULT` | A2-wing convergence probe: `p` first-solve at 1.66× the 1e-05 accept floor. | the D6RF5 non-orthogonal-correction repair (REGISTERED, sizing frozen `9ed7aa78`). |
| **3** | **D9** | `NOT A RESULT` | A5 U-bend optimisation: SLSQP driver failure + endpoint outside the mesh-quality envelope (maxNonOrth 80.93 > 70). | the D9successor meshQualityKS-constrained optimisation (REGISTERED, ruled constraint-alone `cdca4d1e`). |

## 2. CONTEXT — NOT landed fails, so NOT enumerated as verdict rows (PENDING / frozen registrations)

These are named in the brief but are **not landed fail rows** and are deliberately kept out of the
table above so the enforcer does not mis-enumerate them:

- **D6RF5** — the A2 primal repair: a REGISTERED successor with its **freeze in flight**; a
  registration, not a landed fail. `PENDING`.
- **MP-A1** — the A1 multipoint FD basis, **frozen `c4e84348`**; a frozen registration, not a fail.
  (Also: the enforcer's `CASE_ID_RE` extracts `MP-A1` as `A1`, colliding with the A1 ladder id — a
  second reason to keep it out of an enumerable row.)
- **D6R2** — the A2 multipoint optimisation, **gated on the D6RF5 → Stage-2 chain**; `PENDING`, not a
  landed fail.

## 3. KNOWN ENFORCER BLIND SPOT — `SO3DR` (reported to verification, not worked around here)

`SO3DR` is a landed `GATE FAIL` (A2 dose-response, H2 refuted — a valid result) whose successor,
**SO3DR Stage-2** (the cl04-standalone discrimination, REGISTERED, `curriculum_SO3DR_stage2/`,
`c83bfd41`), is recorded in `DAFOAM_SUCCESSOR_LINEAGE_MAP.md` §2 (state (b)). **But the enforcer's
`CASE_ID_RE` cannot extract the string `SO3DR`:** its `SO[-_]?\d+` branch matches `SO3` and then the
trailing `\b` fails between `3` and `D`, and the `D\d+` branch fails on `DR`. Verified 2026-09-07 by
running `CASE_ID_RE.search("SO3DR")` against the committed instrument — it returns `None`.

**Consequence:** `SO3DR` is therefore **not written as a verdict row here**, because any descriptive
row would mis-key onto a later cell's case-id (e.g. `A2`) and enumerate a phantom fail. It is instead
recorded in this prose so it is surfaced, not hidden. If added as a source, `SO3DR`'s own row would
land in the enforcer's `unparsed` channel ("fail verdict but no case id extractable"), which is the
honest could-not-see report, not a standing violation.

**This is a defect in the enforcer's `CASE_ID_RE`, whose own comment claims to cover `SO3DR`. The fix
(a `SO\d+[A-Z]*` shape, or an alternation that admits a trailing alpha run) is the
verification-supervisor's call on their instrument. Reported here; not edited here** (`CLAUDE.md`
rule 9 — the instrument is not ours to change).
