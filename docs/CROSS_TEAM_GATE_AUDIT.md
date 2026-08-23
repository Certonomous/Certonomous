# The cross-team gate audit — rungs opened, checks run, what held and what is owed

The verification team's standing mandate (`harness/teams.yaml`;
`docs/charters/VERIFICATION_CHARTER.md` §2a, §2d, §2d.1): open another team's
rung and ask three questions — **could this gate have failed** (§2a identity
test); **was the comparator frozen before its cases could answer it** (§2d,
with the 2d.1 repair exception); **were the controls fired rather than
described**. Every check in this file was run by the verification supervisor
personally — a relayed check is a summary, not a check
(`SUPERVISION_CHARTER.md` §3) — and each entry names the exact commands' output
(hashes recomputed, not quoted) so the next auditor can re-run them.

This file is append-only: each audit pass is a dated section at the foot, and
existing sections are never edited (CLAUDE.md rule 6).

---

## Audit pass 1 — 2026-08-23, verification-supervisor

**Targets:** the two GATE FAIL verdicts new at HEAD since the board's first
fill — R5C (closure, `0ac76ec2`) and T10a-R (heat-transfer, `cdb5cc0b`).
Both are **negative verdicts on the auditee's own work**, the direction least
exposed to motivated reasoning; the audit still ran every check, because a
GATE FAIL produced by a broken instrument is as unusable as a PASS.

### 1. R5C, the omega-source repair (closure) — AUDIT: SOUND, verdict stands

Record: `cases/RANS_LES_closure_models/R5C_omega_repair/RESULTS.md`
(VERDICT: GATE FAIL, G1 identity 1.1848e-04 vs registered 1e-6 on
`alpha_10_12000_4048`).

| question | finding |
|---|---|
| Pre-registration frozen before compute? | **YES, verified by this auditor's own hash.** `git show f364cf2d:.../PREREGISTRATION.md \| sha256sum` = `a1cfae5a…1277a`, equal to the sha the RESULTS header claims. Commit chain: prereg ALONE 2026-08-22 20:43:01Z; solver/build/run scripts 20:56:27Z; results 2026-08-23 19:19:09Z. |
| Comparator frozen before its cases could answer it (§2d)? | **Compliant on the DISCLOSURE limb, not the freeze limb** — the same class as K0cX. `grade_r5c.py` first committed in commit 3 (with the results), against §7's registered plan of commit 2; disclosed in RESULTS D-4(a) with the file's own mtime (20:58Z, after commit 2 at 20:56:27Z). Mitigations on the record and re-verified: the grading path (every gate G0–G4, every threshold) is fixed numerically in the frozen prereg; the closure supervisor's independent re-grade with the same comparator sha256 regenerated `r5c_grading.json` with zero field differences. On-disk `grade_r5c.py` == committed blob == recorded sha `58eb99e3…605e5` — all three hashed by this auditor, all equal. |
| Could the gates have failed (§2a)? | **YES — G1 did fail**, and the no-op failure mode is covered: a treatment with the repair silently inactive would pass G1 trivially, and **G1c (lever-activity: `omegaSourceRepair true` in the runtime log AND `nNegSourceCells > 0`, on all 27 cases)** exists precisely to catch it — the charter §9 v1.5 lever-activity clause, present and PASS at 27/27 with counted cells (476–2,274). |
| Controls fired, not described? | **FIRED, with measured values.** G0a planted `PLANT = 1.234e-03` read back to 2.391e-10 relative of the analytic value; G0b byte-differ detected; G0c negative control (synthetic run carrying a `maxRelDomega = 0.0` pre-settle row and `bounding omega` lines) returned NOT CONVERGED on **each signature independently**. Refusal (exit 2) is wired; it did not need to fire. |

**Owed by nobody:** nothing. The GATE FAIL stands as graded; the registered
consequence ("R4's 12 targets stand, the 15 hills remain INCOMPLETE, R5C
targets used for nothing") is applied in the record.

### 2. T10a-R, the refinement arm on T10a's B1 ceiling (heat-transfer) — AUDIT: SOUND WITH DISCLOSED DEVIATIONS, verdict stands

Record: `docs/campaigns/T-family/T10aR_RESULTS.md` (GATE FAIL 5/4/0; D466,
L-244).

| question | finding |
|---|---|
| Every byte-level freeze claim in §1a | **RE-DERIVED BY THIS AUDITOR, ALL FIVE HOLD.** (1) Committed prereg blob `7150182b:…/T10aR_PREREGISTRATION.md` is 30,520 bytes, sha256 `c81223d8…b70e903`. (2) The on-disk file's **first 30,520 bytes** hash identically — the prefix property holds, so every gate, threshold, interval and falsifier applied is byte-identical to the committed record. (3) The remainder is exactly `\n---\n\n` + 5,958 bytes. (4) Those 5,958 bytes hash `ab90298a…a3d282`, equal to the preserved `T10aR_runs/ADDENDUM2_content_at_grading.txt`. (5) On-disk comparator `analyse_t10aR.py` == committed blob, sha256 `a3014a64…49c5ef`. |
| Comparator frozen (§2d)? | **YES on the strong limb**: written and hashed before any case directory existed, committed, byte-identical at analysis time, never edited. Imports T10a's own frozen `analyse_t10a.py` (redirected in-process by a context manager, no frozen file written) and reproduces T10a's published `B_f` values to every printed digit. |
| The two disclosed deviations | (a) **Prereg COMMIT 38 min 46 s after the first solver started** (on-disk sha freeze witnessed at 18:10:36Z with a zero-run-dirs `find`; commit `7150182b` 18:55:43Z). The record states this plainly — "the commit makes the freeze independently checkable, it does not retro-date it." A commit-before-compute breach class, disclosed, and graded anyway on the chief's ruling. (b) **ADDENDUM 2 unfrozen and uncommitted at grading** — its own commit was refused by the session's permission classifier, NOT re-routed (rule 9 honoured: a peer satisfying one session's refusal by writing elsewhere routes around the refusal), escalated to Sanaa. The prefix check above proves ADDENDUM 2 alters no applied gate. |
| Controls fired? | Planted-zero recovered on every case; lean-vs-frozen `F` validation bit-identical where both fit; RS1/RS2 recognised in the docket record as a charter §2a **identity** and reported as such, not counted as a control — the vocabulary used correctly. |

**Owed:** nothing new by the auditee — both deviations were disclosed before
this audit and carry the chief's ruling. The ADDENDUM 2 commit decision remains
on Sanaa's desk, where the record itself put it.

### 3. Opened but not yet audited — carried as open targets

Named so the next pass cannot quietly drop them
(`docs/LAB_STATE.md` verification section carries the same list):

- **T1b L4**: four PASS rows on DIVERGENT/STAGNANT triples (D440). Grading of
  the re-run waits on three 80000-endTime siblings, ETA 2026-08-26 — audit
  after grading.
- **A4** (dafoam): the two rows measured at different design points; the
  shipped/patched comparison the DAFoam bright line requires has not been made.
- **A6 N=16** (dafoam): N-D21's step-sizing proxy sizes FD steps from
  `|J_adj|`, the quantity under test; its failure mode is admitted unmeasured —
  check the caveat travels to every verdict surface (§6a).
- **Wu2018 aposteriori** (closure): NOT A RESULT with the registered falsifier
  fired — confirm the falsifier graded is the pre-registered one.
- **T10a**: 6 controls UNMEASURED; the 2d.1 zero-referent repair disclosure.

**Cost of this pass:** zero core-minutes of solver compute; hashing and reads
only.
