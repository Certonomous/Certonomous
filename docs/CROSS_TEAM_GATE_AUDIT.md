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

---

## Audit pass 2 — 2026-08-23, verification-supervisor (same session as pass 1)

**Targets:** three of pass 1 §3's open list, each closed by reading the record
and the git chain personally.

### 4. A6 N=16 (dafoam) — §6a caveat check: CLEARS

The N-D21 limitation (the step-sizing proxy uses `|J_adj|`, the quantity under
test) travels adequately: `A6/rung_n16_remaining_components/RESULTS.md` carries
it in the grading table itself (per-component `C` at measured `|J_fd|` AND at
the registered proxy, side by side), states it plainly at its §7 limitation 8
("That failure mode is unmeasured and this record does not claim otherwise"),
and prices the missing measurement as an UNPRICED future item in its own
follow-up table. `LADDER_A_STATUS.md` row 37 names its referent ("gradient,
fixed FD reference") and points at the record. On THIS rung the proxy was
verified against the measured clearance (within 8% on ten of ten), so the
limitation concerns a future rung, not this verdict. Nothing owed.

### 5. Wu2018 aposteriori_frozenk (closure) — falsifier check: THE FIRED FALSIFIER IS THE REGISTERED ONE; one weakness named

The RESULTS' fired falsifier is quoted from `PREREGISTRATION.md` §5 and matches
the frozen file's own line verbatim ("if TRUTH still fails with `k` frozen, the
`k`-collapse explanation of the prior lane's NOT A RESULT was incomplete").
The later edit (`194f8670`) is a compliant dated correction appended at the
foot, §5 untouched — verified by diff. **The weakness:** the pre-registration's
FIRST commit is `62f781d0`, the same commit as the results — there is no commit
witness that the prereg predates compute; "frozen before any solve, unedited"
is self-attested. The NOT A RESULT stands (a falsifier firing against the
lane's own prior explanation is the anti-tuned direction), and the finding is
recorded as the reason the newer discipline — prereg committed ALONE before
compute (R5C `f364cf2d`), or at minimum an on-disk sha witness with a
zero-run-dirs check (T10a-R) — is the standard, not a nicety. Rung predates
2026-08-22; no re-grade owed.

### 6. A4 (dafoam) — design-point mismatch: RESOLVED by the 2026-08-22 twin

Pass 1 §3 carried the first fill's target "A4's two rows are measured at
different design points — the shipped/patched comparison has never actually
been made." That was true of the original rows and is no longer true:
`A4/shipped_optimisation_np1/RESULTS.md` (prereg committed BEFORE launch,
`239a007f`; results `f9a59d47`) runs the shipped image through the same
optimisation and compares like-for-like at BOTH matched points — at the
optimum (final CD agreeing to 7 s.f., analytic gradients 3.9e-06 relative
apart, the difference living in the path-dependent FD reference) and at the
undeformed baseline (patched 0.33929% vs shipped 1.1032% on the same image
family). Arm identity is asserted from inside the process (`IDWARP_SO_MD5`
printed by the run, shipped `f0fcb488…` vs patched `85f59e87…`) — the
lever-activity clause done properly. Target closed.

### Still open after pass 2

- **T1b L4** — after grading (three 80000-endTime siblings, ETA 2026-08-26).
- **T10a's 6 UNMEASURED controls** — confirm each is labelled unmeasured on
  every surface that cites the rung, per §9's `ran_before_found`.

**Cost of this pass:** zero core-minutes of solver compute; reads and diffs only.

---

## Audit pass 3 — 2026-08-23, verification-supervisor (same session): the freeze instrument re-run, and the two §3 personal checks it demanded

A lane re-ran `scripts/check_comparator_freeze.py` over the current corpus:
**19 comparators in scope (vs the §2d.1 baseline's 6); 7 FROZEN, 8 UNFROZEN,
4 AMENDED_AFTER; selftest passes.** Of the baseline six, five classify exactly
as the charter recorded; **K0cR flipped FROZEN → AMENDED_AFTER** because a
second commit (`6d58d898`) exists that the baseline pass predated. The two
findings below were checked by the supervisor personally, as diffs — not
relayed.

### 7. K0cR's post-marker comparator edit — READ AS A DIFF: display-only, disclosed, CLOSES CLEAN

`git show 6d58d898 -- …/analyse_k0cr.py`: the whole change is the condition on
the printed `"<- hollow pass, 2c"` annotation in the results table. Before, the
label fired on `pass_carries_evidence == False`, which is false both for a
hollow pass AND for a row SSG simply failed — so 20 of 26 plain failures were
labelled hollow passes. After, it fires only on `in_band_ssg AND
in_band_control`, the correct definition. No band, reference, row definition,
verdict rule, tally or JSON field is touched; the edit is a §6 label repair at
the source, in the honest direction (it removed overstated §2c hollowness).
`K0cR_RESULTS.md` §6 disclosed it the day it was made: *"On the grading path:
nothing. The change is one printed annotation."* The AMENDED_AFTER
classification is technically correct and carries no violation.

### 8. `analyse_t9aD` UNFROZEN — the classification is right on the commit test and the rung is still sound

The instrument is right that the comparator's only commit (`06410acd`,
18:21:01Z) postdates the tree's markers (18:02:17Z). The record already holds
what the instrument cannot see: a **checked, not asserted** freeze condition
(comparator sha'd `2d4ebb49…` at 17:58:41.441Z beside a
zero-`D_*`-dirs `find`, pasted verbatim; first solver +197.9 s later), and a
disclosed post-marker repair — the comparator REFUSED twice because a 1e-8
*relative* tolerance was applied to constants *printed to six and five
decimals* (rel 1.96e-08 = the rounding of the printed decimal). Repaired to
half-a-unit-in-last-place; the full diff of frozen-vs-ran is reproduced in the
run tree. 2d.1 audit: (1) demonstrable error — pure arithmetic; (2) found by
the comparator's own refusal, an instrument that grades nothing; (3) disclosed
and quantified; (4) pre-repair refusals quoted. **All four conditions hold.**

### 9. The instrument itself now owes three repairs (docketed this session)

1. **Unit-of-analysis defect, false positives:** `earliest_marker(tree)` pools
   every marker in a directory against every comparator in it.
   `T1_runs` pools 41 markers across ≥4 sub-campaigns; `analyse_t1b_L4.py` is
   reported UNFROZEN by −175,109 s while against its own `R_*_x` cases it is
   **FROZEN by +177,712 s** (proven by the lane; the false positive lands on
   the comparator CLAUDE.md rule 5 cites as the Roache gating authority). Four
   more pooled `T1_runs` UNFROZEN rows remain ungraded.
2. **Population gap:** it walks only `verification/` — eleven graders under
   `cases/` have zero freeze coverage, including R5C's `grade_r5c.py` (audited
   by hand in pass 1), the TBNN/TBRF analysers and the R4 scorers.
3. **It cannot see sha-witness freezes** (T9aD's kind) or marker files without
   `finished_utc` (falls back to mtime against its own docstring's preference).

**Verdict-cells reading, same lane:** current bare-`FAIL` count **3** (V5 line
1070, V14 line 1080, V15 line 1081) vs the recorded 4 — corpus churn, not
instrument change: V8's cell already reads charter-compliant `GATE FAIL` (D-5's
remedy applied there), V10 left, V14 entered via a 2026-08-17 D338 amendment.
Nothing edited; D-5 stays with Sanaa. **Instrument defect:** the D356 landing
control is BROKE by a control/implementation mismatch where the implementation
is the correct half (`_landed` takes the earliest add across spellings — the
true landing; the control demands the latest — the move commit, exactly the
re-dating `_history_spellings` prevents), the second landing control prints
VACUOUS, and `--selftest` exits 1. The instrument's most subtle planted control
currently provides no assurance. Docketed.

**Cost:** zero solver core-minutes (lane: reads + checker executions only).

---

## Audit pass 4 — 2026-08-23, verification lane (CANDIDATE, awaiting the verification supervisor's own read)

**lines whose number changed above this section: 0**

**Everything in this section is CANDIDATE.** It was produced by a `lab-lane` under
the verification supervisor's standing cross-team mandate, not by the supervisor.
`SUPERVISION_CHARTER.md` §3 is explicit that a relayed check is a summary and not
a check: passes 1–3 above were run by the supervisor personally and this one was
not. Nothing below is an audit finding of record until the supervisor re-derives
it. Every number here was re-derived by this lane from the artifact named beside
it — no figure is quoted from the auditee's prose.

**Target:** the dafoam team's **W4 M1+M2** verdicts, board record `108a87e3`
(2026-08-23T20:11:55Z, D478 / N-D22 / N-D23 / L-250–L-252). Five verdicts:
**O0 PASS, M2 PASS, M1-D PASS, M1 PENDING, O3 BLOCKED**.
Records: pre-registration `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md`,
results `cases/dafoam/ladder-b/W4_M1M2_RESULTS.md`, run root
`/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/`.
This audit was **read-only** toward dafoam's territory: no file under
`cases/dafoam/` or in the run root was written, and no compute was launched.

### 10. Comparator freeze (§2d) — RE-DERIVED BY THIS LANE, THE STRONG LIMB HOLDS

| check | finding |
|---|---|
| Prereg committed **alone**, before compute | **YES.** `c8254a4a424cc058b88351aa735a44cc6ab6199d`, `2026-08-23T19:33:04+00:00`, **one file, 632 insertions, nothing else in the commit** (`git show --stat`). |
| The frozen file **is** the file that ran | **YES, hashed by this lane, not quoted.** Committed blob `e7b5f0d427401663def453e968356bb8937602ce`, sha256 `92a6831cab7f71a5d16844fc4c5d1de6dddde6012ae3c3e45f5c13ea92348956`; on-disk sha256 **identical**; the prereg has **exactly one commit** in its history, so it has never been edited since the freeze. Both values equal the ones `W4_M1M2_RESULTS.md:7-9` claims. |
| First run artifact **after** the freeze | **YES, by 434 s.** Earliest compute artifact in the run root is `logs/o0.start`, mtime `19:40:18.967Z`. Every hump-touching path postdates it further: `m2_envoff/` `19:51:52Z`, `m1_dump/` `19:55:01Z`, `hump_dump/pmat.dat` `19:56:17Z`. The frozen §'s assertion that **no `dRdWTPC` dump of the hump existed at commit time** therefore holds on disk. |
| The two files that **did** exist at freeze | `w4_m1m2_memguard.sh` (`19:26:04Z`) and `memguard_selftest.log` (`19:26:15Z`) — both **pre-disclosed** in the frozen §6 (*"this directory does not exist except for the guard script and its self-test log at the moment of the freeze"*). Disclosure matches disk. |
| Instrument freeze (§5) | **All five md5s re-derived by this lane and equal to the frozen table:** `analyze_dump.py d35cb147…`, `analyze_dump3.py f85140f6…`, `pc_ladder.py b1388434…`, `runScript_hump.py d146c56a…`, `w4_m1m2_memguard.sh f102eb52…`. The three CBFS/A6 readers carry mtimes `2026-08-02` and `2026-08-04` — weeks before the freeze, so *"already exists and is not edited"* is a checked claim, not an asserted one. |
| Case-state freeze (§5a) | **All five md5s re-derived on the surviving M2 arm and equal:** `0/U 0b80aa8c…`, `caseDef ce7c5892…`, `fieldDef 5df70649…`, `dRdWColoring_4.bin c823a570…`, `constant/polyMesh/owner c7f7d0ed…`. |
| Every threshold's basis predates the freeze | **YES.** The prereg's numeric bands are cited to `hump_sublu_computetotals.log` (A6, mtime **2026-08-04T15:57:06Z**, 19 days before the freeze). This lane read the cited lines directly: `:271` `Global Adjoint States: 517240`, `:710` `7.98671e-05`, `:1744` `1.6263651522923017e-01`, `:2256` the sub-LU banner, `:2268` `1.094138002900e+00` at `174.97 s`. **Every citation resolves.** |

**Sequence of record:** prereg `c8254a4a` 19:33:04Z → first compute 19:40:19Z →
results `64479072` 20:03:58Z → board `108a87e3` 20:11:55Z.

**Instrument-population finding, extending pass 3 §9 item 2.**
`scripts/check_comparator_freeze.py` provides **zero** coverage of this rung even
after the D471.2 repair: its `POPULATION_ROOTS = ("verification", "cases")` and
its name patterns are `analyse_*.py` / `grade_*.py` / `score_*.py`, while W4's
four comparators live at `/home/ubuntu/certonomous-runs/…` (outside the repo
entirely) and are spelled `analyze_dump.py`, `analyze_dump3.py`, `pc_ladder.py`.
Two independent reasons for the miss. The freeze finding above is **hand-derived
only** and no automated check corroborates it.

### 11. Could the gates have failed? — YES, AND TWO OF TWENTY DID

**O0 (known-answer control) — AUDIT: SOUND.** Registered threshold, frozen §2c:
six published CBFS values, with the registered consequence of a MISS being **M1
`VOID`, no hump arm bought**. Measured at `logs/o0_cbfs_knownanswer.log`, read by
this lane: `:1` `210592 x 210592, nnz=13710468`; `:5`
`||b||_2 = 7.091590452305e-04`; `:11` `zero rows=0 zero cols=0 zero diagonal
entries=0`; `:14` `diagonal … log10=8.67`; `:20` `cos(b, A b) = +6.287343e-03`.
**Six of six exact, margin zero at every printed digit.** Honest limit, and the
frozen file states it before the run: this is a **reproduction** control, not a
discrimination control — same box, same binary dump, same script, so its prior
probability of passing was high. §2c says so verbatim (*"It does not establish
that the readers can see a defect they have never been shown"*), which is why it
is not read here as more than it is.

**M2 (negative control) — AUDIT: SOUND.** Seven pre-registered predictions, all
banded against A6's 2026-08-04 log. Measured by this lane in
`logs/m2_envoff_computetotals.log`: `:710` `7.98671e-05` (cold-start
discriminator), `:1744` `OBJ cfVar: 1.6263651522923017e-01` (17 digits),
`:2267` `Main iteration 0 KSP Residual norm 1.094138002900e+00 73.83 s`, `:2271`
`Total iterations: 0. PetscConvergedReason: -9`, `rc = 1`.
**The gate demonstrably could fail: M2-P7 did.** Wall 148 s against a registered
150–260 s band — **MISS low by 2 s, 1.3 % below the lower edge** — reported as a
miss and not re-banded. A warm-started arm would have broken M2-P2 outright.

**M1-D (assembly-to-dump) — AUDIT: SOUND.** Its success condition is fixed in
the frozen §6 to M1-P1/P2/P4/P5 only. Re-derived: `‖b‖₂ =
1.094138002900e+00` (`logs/o1_hump_stats.log:5`) equal to the solver's own
printed iteration-0 residual to 13 digits (`logs/m1d_dump_computetotals.log:2267`);
`517240 x 517240` exactly (`o1:1`); `rhs.dat` **4,137,928 B** on disk, exactly
`517240 × 8 + 8`; `pmat.dat` **406,022,696 B**, inside the 343–470 MB band and
**0.005 % from the 406 MB point prediction**. The point prediction was arithmetic
on a measured constant and it held: CBFS `165,368,000 / 13,710,468 = 12.061`
B/nnz, hump `406,022,696 / 33,662,810 = 12.061` — **agreement to five significant
figures on a quantity nobody had measured for this case.** `nnz(A) = 33,662,810`
sits 0.11 % from the 33.7e6 point inside a 28.4e6–38.8e6 band.

**The strongest anti-tuning evidence in the record, and this lane checked it as a
hash rather than believing it.** M1-P7 (diagonal spread) came back at **13.01
decades against a registered 7.5–11.0 band** — a MISS, and a number that sits
next to the M6 family's 14.17 rather than CBFS's 8.67, i.e. exactly the kind of
number a motivated lane would promote to a verdict. The frozen file forbids that
**in advance**: §2a labels M1-P7 *"Reported, not decision-bearing"* and §3 builds
the decision rule on the factorization axis instead. That text is inside the blob
whose sha256 this lane re-derived as equal to the committed one, so the label
provably predates the number. It was not promoted.

**The decisive arithmetic was applied against the lane's own interest — the
finding this question exists to hunt, resolved in the auditee's favour.** M1's
`PENDING` turns on `cumulative`. The frozen §4a says the lane computes it *"from
its own ledger"*. Two readings were available: **gross** (40.12 core-min →
remaining 19.88 < the 25.0 launch floor → **O2 not launched, no headline
result**) and **cleaned-of-waste** (20.12 → remaining 39.88 ≥ 25.0 → **O2
launchable, the decisive stage bought**). The lane took the gross reading, which
cost it its own decisive stage; and it carried the one unmeasured row (O0 run 1)
at its **cap**, 3.00 core-min, which maximises cumulative and again works against
it. Robustness re-derived here: at a true O0 run-1 cost of 0.25 core-min,
remaining is 22.63 — **still below 25.0**, so the branch fires either way.

**Cost ledger re-derived from the epoch files, not from prose**
(`logs/{o0,m2,m1d,o1}.{start,end}`): O0 run 2 3 s × 1 = **0.05**; M2 attempt 2
148 s × 4 = **9.87**; M1-D 107 s × 4 = **7.13**; O1 4 s × 1 = **0.07**.
Sum **17.12**, + O0 run 1 at its 3.00 bound = **20.12 CLEANED**, + 20.00 waste =
**40.12 GROSS**. Both totals in the results reproduce exactly.

### 12. Controls fired, not described — FIRED, WITH MEASURED VALUES

| control | finding |
|---|---|
| **O0 known-answer** | **FIRED.** Artifact on disk, six values, quoted above. Not prose. |
| **The lever-inactivity control (M2-P5), and it is a properly planted zero** | **FIRED, and the reader was shown able to see a non-zero — verified by this lane's own greps, not the auditee's.** `grep -ac 'ASM sub-block PC set to complete LU'` returns **0** on `m2_envoff_computetotals.log`, **0** on `m1d_dump_computetotals.log`, and **1** on A6's `hump_sublu_computetotals.log` (`:2256`). The zero counts because the same reader returns one on the same corpus. This is CLAUDE.md rule 3 satisfied on the axis that matters here. |
| **The memory guard's trigger path** | **FIRED before the freeze.** `memguard_selftest.log` (19:26:15Z, i.e. 7 min before the prereg commit) carries `ABORT reason=SOFT_FLOOR_TWO_CONSECUTIVE …` and, on the next line, **`KILL_ISSUED rc=0`** — the kill command executed, not merely scheduled. The guard's own `--selftest` **refuses with exit 1** unless the sentinel file exists (`w4_m1m2_memguard.sh:47`), so the printed `PASS` the prereg quotes is load-bearing. **One gap named honestly:** the sentinel `memguard_selftest.log.selftest-fired` is **no longer on disk**, so that half cannot be re-verified today; the `KILL_ISSUED rc=0` line can be and was. |
| **The guard in production** | **FIRED, all three guarded stages.** `logs/{m2,m1d,o1}_mem.log` each end `DONE container_gone`. Peaks re-derived from the guard's own printed fields: M2 `peak_footprint_kib=9736500` = **9.29 GiB** host drawdown vs **4.445 GiB** container; M1-D `3504140` = **3.34 GiB** vs **4.4 GiB**; O1 `485048` = **0.46 GiB**. Lowest `MemAvailable` across all guarded stages **18,697,604 kB = 17.83 GiB**, **2.97×** the 6.0 GiB soft floor. Every memory figure in the results reproduces. |
| **Residual control gap, disclosed in advance and carried forward** | **No perturbation was ever planted into the hump matrix**, so the O1/O2 statistics readers have never been shown able to see a defect on *this* operator. The frozen §2c states this verbatim before the run, so it is a disclosed limitation and not a concealed one. **Recommended to the O2 re-buy, not imposed here:** a plant is cheap on a dump that is already paid for — copy `pmat.dat`, zero one row, and confirm `analyze_dump.py` reports `zero rows=1` where it reports `0` on the real dump. That would convert the reproduction control into a discrimination control at near-zero core-minutes. |

### 13. M1 `PENDING` — IT IS A QUEUE STATE, NOT A SOFTENED `GATE FAIL`. AUDIT: SOUND

Three independent checks, all run by this lane:

1. **No run exists that would have graded.** `find` over the whole run root for
   any path matching `*o2*` or `*o3*` returns **nothing** — no
   `logs/o2_hump_lu.log`, no `logs/o3_pc_ladder.log`, no `o2_mem.log`. The
   `logs/` directory holds exactly four stages' artifacts (O0, M2, M1-D, O1).
   **There is no graded result being relabelled.**
2. **`PENDING` is a pre-registered branch, not a post-hoc word.** The frozen §3
   verdict table carries a `PENDING` row with its own registered condition
   (*"stage O2 not launched, or launched and stopped by the budget ceiling or the
   memory guard with zero completed `splu` factorizations"*), and the frozen §4a
   fixes the trigger numerically (*"If O2 cannot be given at least 1500 s (25.0
   core-min at `--cpus=1`), O2 is not launched and M1 is `PENDING`"*). Both
   sentences are inside the blob this lane re-hashed as equal to `c8254a4a`'s.
   The label was chosen before the situation arose.
3. **The registered consequence correctly did not fire.** §3's carried sentence
   — *"if M1 returns singular or catastrophically ill-conditioned, M4 and M5 are
   not bought"* — is not claimed as fired; the results say M4/M5 stay unbought
   *because M1 did not decide*, a distinct state, and refuse to collapse the two.
   §3a quarantines the operator statistics (`0/0/0` closes only the cheap half of
   D-SINGULAR) and draws no verdict from them. That is the charter §2a identity
   discipline used correctly.

This is `PENDING` in the charter's display/queue sense. Nothing here softens a
failure.

### 14. **DEFECT FOUND** — the one cost row that decided M1's verdict is not artifact-backed, and is not labelled as such

`W4_M1M2_RESULTS.md` §5 row 3 reads `M2 attempt 1 | 300 s | 4 | 20.00 core-min`,
and §5a quotes its traceback (`FileNotFoundError … 'reports/runScript_hump'`,
`PermissionError … 'reports'`), its `Forwarding signal 18 to job` hang, and a
container holding *"1.13 GiB flat for the whole five minutes"*.

**None of that is on disk.** Attempt 1 wrote to
`logs/m2_envoff_computetotals.log` and `logs/m2_mem.log`; **attempt 2 overwrote
both at the same paths** — the log's mtime is `19:53:12Z` and the guard log's own
first line reads `START … 19:50:45Z`, i.e. attempt 2 in both cases. A `grep -rl`
for the quoted traceback string across `/home/ubuntu/certonomous-runs/` returns
**zero files**. There are no `.start`/`.end` epoch files for attempt 1. A `find`
over the whole of `/home/ubuntu/certonomous-runs/` for files modified between
`19:40` and `19:51` returns exactly three paths, all of them O0 run 2's
(`logs/o0.start`, `logs/o0_cbfs_knownanswer.log`, `logs/o0.end`, 19:40:18.97–
19:40:21.40Z), and then nothing at all until `logs/m2.start` at `19:50:52.63Z`:
**attempt 1 left no filesystem trace anywhere on this box.**

**Why this matters rather than being bookkeeping: row 3 is the load-bearing input
to the `PENDING` verdict.** Remove it and `cumulative` = 20.12, remaining =
39.88 ≥ the 25.0 floor, and O2 would have been launched — the item's decisive
stage. The single figure that decided the headline is the single figure with no
surviving artifact.

**What the disk does support**, and it is a bound rather than a measurement: the
window between `logs/o0.end` (`19:40:21.4Z`) and the M2 attempt-2 guard `START`
(`19:50:45Z`) is **624 s**, which comfortably contains a 300 s timeout plus the
`chmod 777` repair and re-staging. A 300 s attempt fits; nothing on disk pins it
to 300 s rather than to some smaller value.

**Direction of the error, stated because it bears on severity.** An overstated
waste row cost this lane its own headline result — the anti-self-serving
direction, and the opposite of what a tuned record looks like. The record also
labels row 1 (O0 run 1) explicitly as *"A bound, not a measurement"* and
propagates a `≤` through every total; row 3 gets no such label despite being in
the same evidentiary class and mattering more.

**Recommended remedy — dafoam's to accept or refuse, not this lane's to impose,
and no verdict is overturned by it:** a dated addendum to
`W4_M1M2_RESULTS.md` (appended at the foot, §5 struck not rewritten, per
CLAUDE.md rule 6) labelling row 3 a **BOUND** on the same footing as row 1,
recording that its log was overwritten by attempt 2, and citing the 624 s window
as the corroborating bound. **M1 stays `PENDING`** — the label is pre-registered,
O2 genuinely never ran, and the gross-vs-cleaned choice was taken in the
conservative direction.

**Second-order finding, for whoever owns the next hump item:** the fault class is
generic — a re-run at the same log path destroys the failed attempt's evidence.
The cheap fix is a per-attempt suffix on the log and guard-log paths.

### 15. O3 `BLOCKED` — the blocker's mandatory limb is REAL and checkable; its refusal limb is NOT verifiable from disk. AUDIT: SOUND WITH DISCLOSED DEVIATIONS

The results name the blocker precisely (§6a): the command that starts
`w4_m1m2_memguard.sh` was refused by the session's permission system, and the
frozen prereg makes the guard mandatory.

- **The mandatory limb: REAL, and this lane verified it against the frozen file
  rather than the prose.** O3's registered launch command in the frozen §6 opens
  with `"$BASE/w4_m1m2_memguard.sh" w4m1m2_o3 6291456 3145728 …` — the guard is
  *part of the registered command*, so an unguarded O3 would have been a
  departure from the frozen launch command, not a shortcut. §7's registered
  floors and the L-239 quotation (*"a registered stop with nothing wired to
  trigger it is not a guard"*) sit in the same blob. O3 is also the item's
  memory-riskiest stage — predicted **10.0–26.0 GiB against this box's 30.65
  GiB**. Refusing to run *that* stage unguarded is the guard working.
- **The refusal limb: NOT VERIFIABLE FROM DISK, and this lane says so plainly.**
  A permission-classifier refusal leaves no artifact. Two observations, offered
  as neither confirmation nor contradiction: (i) the same guard was armed
  successfully **three times in the preceding seven minutes** (19:50:45,
  19:54:25, 19:57:22), so any refusal was invocation-specific rather than
  categorical; (ii) the absence of every O3 artifact is consistent with the
  account but is equally consistent with any other reason for not launching.
  **This lane cannot establish that the refusal occurred.**
- **What is positively good and worth recording:** D478 states that *"nobody
  re-attempts the denied command"* and routes the unblock to Sanaa. That is
  CLAUDE.md rule 9 honoured in the hard direction — satisfying a refusal by
  re-routing is exactly the laundering the rule forbids, and it was not done.
- **One unverifiable number:** §6a's *"its memory gate (25.91 ≥ 25.0 GiB)"* has
  no artifact this lane could find; no guard log exists for a stage that never
  launched.

`BLOCKED` is the right label under rule 1: a named external blocker, zero cost,
and the two dependent predictions (M1-P11, M1-P12) correctly carried as
`PENDING` rather than MISS — which the frozen §4a had also registered in advance.

### 16. Summary of this pass

| target | verdict as reported | AUDIT (CANDIDATE) |
|---|---|---|
| **O0** known-answer control | PASS | **SOUND** — six of six CBFS values exact from `logs/o0_cbfs_knownanswer.log`; reproduction-control limit pre-disclosed in the frozen §2c |
| **M2** negative control | PASS | **SOUND** — every value re-derived from `logs/m2_envoff_computetotals.log`; the gate could fail and M2-P7 did (148 s vs 150–260 s) |
| **M1-D** assembly-to-dump | PASS | **SOUND** — dump on disk at 406,022,696 B / 4,137,928 B, `‖b‖₂` = the solver's own residual to 13 digits; 12.061 B/nnz agreement to five s.f.; the M1-P7 MISS was registered non-decision-bearing before the number existed |
| **M1** overall | PENDING | **SOUND on the label** — no O2/O3 artifact exists anywhere in the run root, `PENDING` is a pre-registered §3/§4a branch, and the gross-vs-cleaned choice was taken against the lane's own interest — **but see §14: its load-bearing cost input is a DEFECT FOUND** |
| **O3** | BLOCKED | **SOUND WITH DISCLOSED DEVIATIONS** — the mandatory-guard limb verified in the frozen §6/§7; the permission-refusal limb is unverifiable from disk and is named as such |
| **§5 row 3**, the 20.00 core-min waste | reported as a measurement | **DEFECT FOUND** — no surviving artifact, the log overwritten by attempt 2, and it is the figure that decided M1 = PENDING. Remedy: label it a BOUND in a dated addendum. No verdict overturned |
| `scripts/check_comparator_freeze.py` coverage of W4 | — | **zero**, for two independent reasons (comparators outside the repo; names outside the `analyse_*`/`grade_*`/`score_*` patterns). Extends pass 3 §9 item 2 |

**Carried forward as open, so the next pass cannot drop it:** the O2 re-buy, if
authorised, should carry a **planted perturbation** on the existing dump (§12,
last row) — the operator is already paid for and the plant is near-free.

**Cost of this pass:** zero solver core-minutes; zero compute launched. Reads,
`git show`/`cat-file` hashes, `md5sum`, `grep -c` and `find` only. Nothing under
`cases/dafoam/` or in the run root was written.

---

## Audit pass 5 — 2026-08-23, verification LANE (CANDIDATE, not the supervisor's own read)

**Lines whose number changed above this section: 0.** This section is appended
at the foot of an append-only file; every section above it is byte-identical to
its HEAD blob, and the base for this edit was taken from
`git show HEAD:docs/CROSS_TEAM_GATE_AUDIT.md`, never from the worktree (L-253).

**This pass was run by a `lab-lane`, not by the verification supervisor
personally.** `SUPERVISION_CHARTER.md` §3 is explicit that a relayed check is a
summary and not a check, so **every finding below is CANDIDATE until the
verification supervisor re-derives it.** Each finding names the artifact it was
read from so re-derivation is cheap. The lane was **read-only toward
heat-transfer's territory** throughout: nothing under
`verification/runs/T-family/` or `docs/campaigns/T-family/` was written, no
comparator was re-executed, and no case was touched.

**Target:** heat-transfer's **T9aH** chain — `Gauss harmonic` re-grade of the
T9a composite wall and fin. Four commits: `0078fe9c` (pre-registration alone),
`1908bb7c` (run tree + instruments + Addendum A.1–A.6), `a66232c1` (A.7, A.8),
`359cccfb` (the grade), plus `b698dfc3` (board + the supervisor close-out note
appended to the results).

### 17. T9aH (heat-transfer) — CANDIDATE: SOUND. Two items owed, neither touching a verdict

| question | finding |
|---|---|
| Pre-registration frozen before compute (§2b, §2d)? | **YES, by 1,247 s, re-derived by this lane.** Prereg committed **alone** at `0078fe9c`, 2026-08-23 **19:52:16Z**; first compute — the `blockMesh` banner inside `W_c/log.blockMesh` — **20:13:03Z**. The doc's own §9 freeze condition was *checked, not asserted*: `date -u` 19:45:57.814Z beside `ls -d …/T9aH_runs` returning rc=2 and a `find … -name 'T9aH*'` returning 0. The `0078fe9c` blob hashes **`84af4208157418efcb41457f346e54a5f41e6360e5a5d7855bb8acd5ff629f0b`**, equal to the sha Addendum A claims for it. |
| Comparator frozen before its cases could answer it (§2d)? | **YES on the STRONG limb, by 469 s, three-way hash-identical.** `analyse_t9aH.py` committed at `1908bb7c` **20:05:14Z**, 469 s before the first `blockMesh`. Blob@`1908bb7c` == blob@HEAD == on-disk == **`8107ed38578fcade0196c6458cb2e8e0f3d1af620c1a4d2c1dd444cea97f2870`**, the value Addendum A.2 registered *while the tree still held zero case directories* (A.5's re-check, 20:02:53.680Z). Same three-way equality re-derived for `build_t9aH.py` `c7a742f2…787104a4`, `run_chain_t9aH.sh` `77c58025…9eac39aade`, `T9aH_registered.json` `2a5ee67c…def30151b8`, and for `check_t9aH_mesh.py` `5c45eb9c…2608db4d` against its `a66232c1` blob. **§2d.1's repair exception is neither invoked nor needed.** |
| Could the gate have failed (§2a)? | **YES — demonstrated on the same pipeline, not argued.** The registered null arm `RL_f` (identical mesh, identical `k`, `Gauss linear` instead of harmonic) missed **every** H-row bar: H1 **−2.4091842789175644e-03 K** = **240,918×** above the 1.0e-08 K bar, H2 **1.806464886613582e-02** = 1.81e+06×, H3 **−5.066098354404858e-04 K** = 50,661×. All three recomputed by this lane from `gate_t9aH.json`. Three gates that could *not* have failed are declared in advance and handled — see §18. |
| Controls fired, not described? | **ALL SIX REFUSAL CHANNELS AND ALL FOUR CONTROLS FIRED**; HC1/HC2/HC3 fired with a live computation but were **recorded as a bare boolean**. Detail and the lane's independent recomputation in §19. |
| Amendments legal (§2b/§2d)? | **YES — five amendments/addenda, all pre-first-compute and all gate-neutral; ZERO post-compute edits to the pre-registration.** Ledger in §20. |
| Verdict vocabulary (rule 1)? | **CLEAN. No bare `FAIL` verdict cell anywhere in the chain.** Detail in §21. |

### 18. Margins, and the three gates that could not have failed

Every value below was recomputed by this lane from `gate_t9aH.json`'s
`cases` and `exact_references` blocks by independent arithmetic, and reproduces
`T9aH_RESULTS.md` §2 to every printed digit.

| row | worst measured | bar | margin under the bar | what the null arm returned on the same row |
|---|---:|---:|---:|---:|
| H1 `T_i1` 400× | 3.183231456205249e-12 K | 1.0e-08 K | 3,141× | −2.409e-03 K (**2.41e+05× over**) |
| H2 `q″` 400× rel | 2.484899921384454e-11 | 1.0e-08 | 402× | 1.806e-02 (**1.81e+06× over**) |
| H3 `T_i2` 400× | 1.8758328224066645e-12 K | 1.0e-08 K | 5,331× | −5.066e-04 K (**5.07e+04× over**) |
| H4 `H40_f` absolute | 2.5011104298755527e-12 K | 1.0e-08 K | 3,998× | no linear counterpart registered at 40× |
| H4 drop clause | 2.598608970785584e+10 | > 1.0e+06 | 25,986× over | — |
| H5a `H4000_f` `T_i1` | 4.206412995699793e-12 K | 1.0e-08 K | 2,377× | no counterpart at 4000× |
| H5b `H4000_f` `q″` rel | 1.1406578348527318e-11 | 1.0e-08 | 877× | — |
| H6 fin, six deviations | 0.0 | 1.0e-09 | identity | — |

**Three gates could not have failed, and all three are declared in the frozen
record rather than found by this audit:**

1. **H6 is a near-identity.** Prereg §4.3 says so bluntly ("This row is close to
   an identity and is declared as one"), and `gate_t9aH.json` carries
   `counted_toward_hypothesis: false` on it. Five rows, not six, are counted.
   **Handled correctly.**
2. **H4's drop clause is not the binding one.** Addendum A.4 disclosed
   *before grading* that a drop below 1e+06 requires `|e1| > 6.5e-08 K`, which
   already fails the 1.0e-08 K absolute bar — so the drop clause is a
   cross-check on the baseline read from `gate_t9aD.json`, not an independent
   falsifier. This lane re-derived the crossover: `64.99408e-3 / 1.0e+06` =
   **6.499e-08 K**. §4.4's threshold was **not** changed for it.
3. **FR0–FR2 could not have PASSED** — the inverse failure mode, and the
   honest direction. Prereg §4.1 registered, before the run, a four-branch table
   of what the frozen rule does when the differences it builds a Roache band
   from are round-off, and named **"the most likely single outcome is
   OSCILLATORY → NOT A RESULT"**. The frozen comparator returned
   OSCILLATORY / OSCILLATORY / DIVERGENT on FR0 / FR1 / FR2 with `band_pct: null`
   — verified by this lane in `T9aH_runs/gate_t9a.json` — and the record
   publishes them as returned, including the comparator's own line *"the rung is
   unsound"*, reproduced verbatim rather than explained away.

**One observation the record already makes and this lane confirms rather than
raises.** H1–H3 at 400× are a **confirmation at a bar set 3,333× above a
residual T9a-D had already measured on the identical meshes** (0 / 3.2e-12 /
3.0e-12 K). Their surprise value is low by construction, and the prereg says so
in the "predicted" column. What is genuinely new is the **4000× contrast** (no
prior measurement) and **`H40_f` under harmonic** (T9a-D's 40× arm was
`Gauss linear`, and it grew the error 27–31×). **The rung's evidentiary weight
sits on HC4's discrimination and on those two extensions, not on the 400×
rows** — which is what §4.5 of the pre-registration already claims for it.

### 19. Controls — fired with a measured value, except three recorded as booleans

**Fired, with a number read back off disk** (all from `gate_t9aH.json` →
`refusals`, re-read by this lane):

- **RC6, the load-bearing plant.** `+1.234e-03 K` into cell **25** (x =
  0.04903846153846154 m) of a scratch copy of `W_f`: the frozen `measure_wall`
  moved `T_i1` from **348.78108239882687 K** to **348.78225871413395 K**, a
  shift of **1.1763153070774024e-03 K** against a registered floor of
  **1.0e-05 K** — **117.6× over the floor and 1.18e+05× over H1's own bar.**
  In a rung whose headline is a set of zeros this is the single most important
  artifact in the chain, and it is a real read-back, not an echo.
- **RC5, the convergence plant, on two cases.** `+1.234e-03 K` into `900/T` of
  scratch copies of **both** `W_f` and `H40_f`: frozen
  `iterative_convergence` returned `max_change` **1.2340000000108375e-03 K**
  and state **NOT_CONVERGED** on both. The `+1.08e-14 K` tail on the readback
  is the arithmetic signature of a genuine round trip.
- **RC3, the replica / builder control.** `RL_f` reproduces the frozen `W_f` of
  `T9a_runs/gate_t9a.json` to **0.0 K, 0.0 K, 0.0 W/m²** — bit-identical,
  against registered tolerances of 1e-9 K and 1e-7 W/m².
- **RC2, the `fvSchemes` readback.** Re-read by this lane from
  `gate_t9aH.json` → `cases[*]["laplacian(DT,T)"]`: **nine cases
  `Gauss harmonic corrected`, `RL_f` `Gauss linear corrected`** — the single
  registered change, verified from each case's own dictionary.
- **HC4, the discrimination test.** Records its three null errors and
  `rows_not_counted: []`.

**Fired but recorded as a bare boolean — the finding of this pass.** `HC1`,
`HC2` and `HC3` appear in `gate_t9aH.json` → `controls` as `met: true` plus a
`must` string and **no measured value**. This lane read
`analyse_t9aH.py:506–514` and confirms all three are **computed live from
disk-read case values** (`mw["f"]["q"]`, `mf["f"]["eta"]`, `m_c3`) — they
**fired**, they are not asserted — and recomputed each independently from the
same gate file:

| control | lane's independent recomputation | fails its bar by |
|---|---:|---:|
| HC1 arithmetic-mean `k̄` | `k̄` = 5.613333333333333 W/m·K (mean of 0.8 / 0.04 / 16.0, read from `T9a_registered.json`), `q_C1` = 1650.9803921568628 W/m²; measured `W_f` `q″` = 19.502681619207195 → **98.81872118458483 %** deviation (identical to the frozen path's own C1 figure) | 9.88e+07× |
| HC2 perfect fin | `\|η_f − 1\|` = **0.1668262943643002** | 1.67e+08× |
| HC3 trivial baseline `W_C3` | `\|T_i1 − exact\|` = **1.2189176011683571 K**; `\|T_i2 − exact\|` = **49.97562164797995 K**; `q″` relative **0.9999999998763257** | 1.2e+08× / 5.0e+09× / 1.0e+08× |

**The substance holds by eight to nine orders and this audit withdraws
nothing.** The finding is a **recording gap**: a reader holding only
`gate_t9aH.json` cannot see what deviation made HC1–HC3 `MET`, and
`T9aH_RESULTS.md` §3.2 repeats the boolean ("fails it", "fails all three")
rather than the number — the one place in an otherwise number-dense record
where a control is **described rather than quantified**. Contrast HC4, which
records its values. **The same class applies to two rows:** `H4` and `H5`
carry only `{row, threshold, verdict}` in the gate file, where H1/H2/H3/H6
carry `levels`, `errors` and `worst`; their values are recoverable from
`cases` + `exact_references` (this lane recomputed all six and they match the
results to every printed digit), so nothing is unsupported — but the row
records themselves are thinner than their siblings.

**RC4, the strict completion rule, verified independently by this lane.** It is
wired as a refusal loop over all ten cases calling the frozen `MARK.check`
(`analyse_t9aH.py:355–360`); it did not fire, and a refusal that does not fire
leaves no positive per-case record for the three extra cases (the seven frozen
cases do get `DONE.*` markers). Read from disk for `RL_f`, `H40_f`, `H4000_f`
and `W_f`: last time directory **1000** == `endTime`; exactly one `End` line;
**1000** `ExecutionTime` lines; and the **age guard** holds on every one —
`0/T` at 20:14:04.3678 / 20:14:04.7435 / 20:14:05.1215 / 20:13:54.8652Z against
`1000/T` at 20:14:04.4822 / 20:14:04.8562 / 20:14:05.2322 / 20:13:54.9782Z,
margins **113–115 ms**, every field at `endTime` newer than its own `0/T`. All
ten `STATUS.*` carry `rc=0` and `checkMesh_rc=0`. **The completion rule holds.**

### 20. Amendment legality — five items, all pre-compute, all gate-neutral

First compute is the `blockMesh` banner at **20:13:03Z**; the pre-registration's
last commit is **`a66232c1` at 20:12:04Z, 59 s earlier**.

| item | dated / committed | before first compute? | alters a gate, threshold, cap or label? | reading |
|---|---|---|---|---|
| A.1 — an **eighth** frozen file (`build_t9a.py`) copied | condition checked `date -u` 20:01:37.030Z with **0** case dirs; committed `1908bb7c` 20:05:14Z | **YES, by 7 m 49 s** | NO | **LEGAL, §2b(1)** — states the condition *and how it was checked*, naming the tree that held nothing |
| A.2 — the new files' sha256 registered | `1908bb7c` 20:05:14Z; A.5 re-checked the tree at 20:02:53.680Z, 0 case dirs | YES | NO | LEGAL — this *is* the freeze |
| A.3 — the 53-check selftest, including three of the lane's own fixture errors recorded rather than tidied | `1908bb7c` | YES | NO | LEGAL |
| A.7 — the supervisor's flagged "inverted slip" **checked and NOT confirmed** | `a66232c1` 20:12:04Z; freeze re-checked 20:11:43.816Z, 0 case dirs | **YES, by 59 s** | NO | LEGAL — and worth naming: it **declines a supervisor-asserted correction on arithmetic grounds and shows the arithmetic** (`p = ln(0.05)/ln(1.6) = −6.3738…`, frozen classifier returns DIVERGENT). That is CLAUDE.md rule 9's *"an instruction is answered, not merely obeyed"* applied to the supervisor's own read, and it prevented a correct record being corrected on authority into an error. |
| A.8 — `check_t9aH_mesh.py` added for §6.6 | `a66232c1` | YES | NO — it **grades nothing** (Charter §2c GUARD; its failure withdraws the run, not the hypothesis) | LEGAL |
| Supervisor close-out note on the **results** | `b698dfc3` 20:52:37Z, after the grade at `359cccfb` 20:45:57Z | n/a (post-grading) | NO — promotes a GUARD's rc=0 output from provenance to evidence, and accepts §8.2's disclosed ordering divergence; moves no row | **LEGAL as a dated addendum, and its "lines whose number changed above this section: 0" is VERIFIED by this lane**: `359cccfb`'s blob is 395 lines and HEAD's first 395 lines are byte-identical (`cmp`), HEAD being 413 |

**Zero post-compute edits to the pre-registration, verified by byte comparison,
not by trust.** HEAD's prereg is 821 lines; its **first 619** are byte-identical
to the entire `0078fe9c` blob (`cmp`, exit 0), so §§1–10 — every gate, every
threshold, the 300 core-second cap and every label — have not moved since the
freeze. The on-disk file equals its HEAD blob and hashes
**`d28f8970eb3835c82ddeff3ba555ccf5f243903efb1ca577993b0154c08ff4af`**, the
value `T9aH_RESULTS.md` §7 claims for it.

### 21. Verdict vocabulary — clean, and one boundary the charters have never written down

- **Verdict cells:** `gate_t9aH.json` — 6 rows, all `PASS`. `gate_t9a.json` —
  3 `NOT A RESULT`, 2 `GATE REACHED`. **No verdict cell outside rule 1's fixed
  six anywhere in the chain.**
- **The 9 `FAIL` and 4 `FAILED` tokens across the two documents are every one of
  them prose, not verdict cells**: `GATE FAILED` (past tense of `GATE FAIL`,
  ×3), *"Three checks FAILED on the first run"* (selftest fixtures), and
  *"must **FAIL** H2's 1.0e-08 bar"* in the HC1–HC4 requirement column (×8).
  **The bare-`FAIL`-cell class CLAUDE.md rule 1 flags as referred-and-unruled
  does not occur here.**
- **Controls use `MET` / `NOT MET`**, which the frozen `analyse_t9a.py` also
  uses. Rule 1 fixes the vocabulary for **gate verdicts**; no charter clause
  this lane could find states the control vocabulary. **Recorded as a boundary
  the charters leave implicit, not as a breach** — and not a thing a lane rules
  on.
- **Row renaming held.** Prereg §4.1 registered that the frozen rows would be
  called **FR0–FR4** in this rung's records and *"never presented as T9a's
  R0–R4"*. `gate_t9a.json` calls them R0–R4; `T9aH_RESULTS.md` §1 calls them
  FR0–FR4 and says which is which. **T9a's verdict was not re-opened and no T9a
  number moved** — both T9a gate files still hash `7c4c6826…b3a5f4f8` and
  `96e0dce0…0dc19993`, recorded in `gate_t9aH.json` → `refusals`.

### 22. The mtime hazard on this tree — the freeze checker would be right here, for a reason worth carrying

Pass 3 §9 item 3 records that the freeze instrument cannot see sha-witness
freezes and falls back to mtime on markers without `finished_utc`. T9aH's seven
`DONE.*` markers carry the bare text `strict rule met` and **no timestamp**, so
the fallback applies. Two things follow, offered as candidate repairs:

1. **A marker-based freeze test is systematically lenient by the
   solve-to-mark gap.** Against the earliest marker (20:37:07.6197Z) the
   instrument would report `analyse_t9aH.py` (mtime 20:02:40.363Z) **FROZEN by
   +2,067 s** — the right verdict, agreeing with the commit test. But **the
   margin that matters is comparator-committed → first `blockMesh`, which is
   469 s**, and the 1,444 s between first compute (20:13:03Z) and marking
   (20:37:07Z) inflates the reported figure by more than three-fold. Here there
   is margin to spare; on a tighter chain the reported number would not be the
   number that decides.
2. **The seven markers share one whole-second mtime — the same surface
   signature as `T1_runs`' 15-marker copy signature — but here it is NOT a
   copy.** They are distinct at sub-second (…619726333 → …619926474, a
   **monotone ~200 µs spread**) and were written by one `mark_done_t9a.py`
   process at 20:37:07. **A copy signature and a single-process batch write are
   indistinguishable at whole-second resolution and separable at nanosecond
   resolution; the discriminator is the sub-second spread and its monotonicity,
   and the instrument does not currently look at it.** Offered to the
   supervisor as a candidate repair, not as a ruling.

Also noted: the eight frozen copies inside `T9aH_runs/` carry **preserved
2026-08-20 mtimes** (`analyse_t9a.py` 19:01:15.530, identical to its `T9a_runs`
original) — a `cp -p` signature. **Here the preserved mtime happens to be honest
provenance** — the file *is* the `239ed2b8` blob, hash-verified three ways above
— **but a checker reading it as a creation time is reading a copy's clock, and
this tree is a clean example of why the hash test, not the clock, is the freeze
evidence.**

### 23. Owed — two items, neither touching a verdict

1. **No row in `docs/COST_CALIBRATION.md` for T9aH.** CLAUDE.md rule 12's
   calibration clause makes the estimate-versus-actual comparison a **completion
   requirement**, and the ledger holds five rows, none of them T9aH — verified
   by this lane (`grep -c T9aH` → 0). **The comparison itself exists and is
   complete** in `T9aH_RESULTS.md` §9: registered ≤ 90 core-s against a 300
   core-s cap, **actual gross 21.422 core-s = 0.357 core-min**, ratio **0.238×
   prediction and 0.071× cap**, `cost_basis` correctly stated as
   reported-by-owner and not measured. This lane re-derived the solver-only
   figure from the ten `STATUS.*` wall fields — **8.52 core-s**, `F_f` dominant
   at 5.89 s, no row within three orders of the 3600 wall-s stall rule.
   **What is owed is the ledger row, not the work, and it is heat-transfer's to
   land** — this lane is read-only toward their territory and did not write it.
2. **Three of the new instrument's four controls (HC1–HC3) and two of its six
   rows (H4, H5) are recorded without their measured value** — §19. The
   substance is sound and was recomputed here, so this is a **next-rung
   comparator item, not a repair**: `analyse_t9aH.py` is frozen at
   `8107ed38…a97f2870` and must not be edited for it (rule 6, and the rung's own
   §0 prohibition 4).

### 24. What this lane could NOT establish, named plainly

- **Whether the supervisor's §3 check-1 read of `analyse_t9aH.py` happened as a
  `diff -u`**, which prereg §1 demands in a box. Addendum A.7 is strong
  circumstantial evidence that a step-4 read occurred (it answers a specific
  line the supervisor flagged), and the close-out note evidences a later read of
  `check_t9aH_mesh.py`. **A personal read leaves no artifact by construction;
  this lane takes it as attested, not verified.**
- **The `build_t9aH.py` 0.004 core-s and `blockMesh` 2.246 core-s figures are
  bounds, not measurements**, exactly as §8.4 discloses. This lane confirms they
  cannot be recovered from what is on disk and did not try to improve them.
- **Neither comparator was re-executed.** Every row and control above was
  recomputed by **independent arithmetic over the values the instruments wrote
  to disk**. That tests the grading arithmetic and the thresholds; it does **not**
  test the readers that produced those values. **The readers are covered instead
  by RC6's planted control** — which is precisely why RC6, and not any H row, is
  the load-bearing artifact in this chain.
- **The shared git index is stale against HEAD on this tree** — `git ls-files`
  omits `T9aH_RESULTS.md`, `gate_t9aH.json` and `check_t9aH_mesh.py`, all three
  of which are committed and present. `T9aH_RESULTS.md` §8.3 discloses exactly
  this and records that the staged entries were **inspected, never reverted**.
  This lane read the same way — bases taken from `git show HEAD:<path>`, never
  from `git status` (L-253) — and **touched no staged entry**.

**Cost of this pass:** zero solver core-minutes. Reads, hashes and arithmetic
only.

---

## Audit pass 6 — 2026-08-23, verification LANE (CANDIDATE, not the supervisor's own read)

**Lines whose number changed above this section: 0.** This section is appended
at the foot of an append-only file. The base for this edit was taken from
`git show HEAD:docs/CROSS_TEAM_GATE_AUDIT.md`, never from the worktree (L-253),
and the two were verified byte-identical (`cmp` rc=0, 740 lines each) before the
append, so no peer's uncommitted work was overwritten.

**This pass was run by a `lab-lane`, not by the verification supervisor
personally.** `SUPERVISION_CHARTER.md` §3 is explicit that a relayed check is a
summary and not a check, so **every finding below is CANDIDATE until the
verification supervisor re-derives it.** Each finding names the artifact it was
read from. The lane was **read-only toward closure's territory** throughout:
nothing under `cases/RANS_LES_closure_models/` or `/home/ubuntu/closure-data/`
was written, no closure comparator was re-executed, and no case was touched.

**Target:** closure's **FS5/D476 clip repair** — the unclipped `q1_wallRe`
companion. Pre-registration frozen at `bf4956bc` (2026-08-23T20:40:34Z),
implemented and graded at `7e973ba8` (21:01:08Z). Reported verdicts **A1 PASS,
A2 PASS, A4 PASS, A3 GATE FAIL** (referred, not loosened).
Records: `cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_PREREGISTRATION.md`,
`…/FS5_D476_CLIP_REPAIR_RESULTS.md`, triage `/home/ubuntu/closure-data/D476_A3_triage/`,
pre-repair state and before-hashes `/home/ubuntu/closure-data/features_backup_pre_D476/`.
**This audit is the one prereg §7 blocks closure's adoption on.**

### 25. Comparator freeze (§2b, §2d) — RE-DERIVED, AND IT HOLDS

| check | finding |
|---|---|
| Prereg committed **alone**, before implementation | **YES.** `bf4956bc`, 2026-08-23T20:40:34Z, **one file, 118 insertions, nothing else in the commit**. |
| Frozen blob == the blob the record claims | **YES.** `git rev-parse bf4956bc:<prereg>` = **`8fac067cf4a2c19a205df529db6c79bd48e31f3d`**, exactly the value `FS5_D476_CLIP_REPAIR_RESULTS.md:4` claims for it. |
| Gates/thresholds/caps unmoved since freeze | **YES, by byte comparison, not by trust.** The whole 118-line freeze blob is byte-identical (`cmp` rc=0) to the **first 118 lines** of the 147-line file at HEAD. So §4's four gates, §6's 2–6 core-min estimate and 0.5 core-h cap, and every label are exactly as frozen. |
| History of the prereg path | **Exactly two commits**: `bf4956bc` (the freeze) and `7e973ba8` (+29 appended lines = Addendum 1). Disk == HEAD == `7e973ba8` blob = `6110dbe01ae089e5d115e5b7d8d971c08cbad3b2`. No third edit anywhere. |

**Freeze-before-evidence, re-derived from filesystem mtimes.** The earliest
A1–A4 evidence artifact anywhere on disk is
`features_backup_pre_D476/A2_before.json`, mtime **2026-08-23 20:43:16.227Z** —
**162 s AFTER** the freeze commit. The whole chain then runs in the registered
order: `build_features.py` edited **20:45:41.365Z** (145 s *after* the
before-hashes were taken, which is what makes A2 non-circular); first
regenerated `.npz` **20:46:56**, last **20:48:03**, `manifest.json`
**20:48:04.035**; `fs2_audit.py` edited **20:50:15.780**; delivered
`fs2_audit.json` **20:57:38.307**. Nothing that answers a gate predates the
freeze.

**One artifact legitimately predates the freeze and is not a violation.** The
A3 "old" side, `features_backup_pre_D476/fs2_audit.json`, is dated
**2026-08-21 18:01:25Z**, two days before. It is the pre-repair baseline the
gate compares *against*, not evidence produced under the pre-registration. Its
code-fairness is separately established in §27.

### 26. Could each PASS gate have failed — and the tautology hunt

**No tautological gate was found among A1, A2 and A4.** Each is named below with
the way it could have gone the other way.

**A2 — model-facing identity. PASS, re-derived independently: 40/40, zero
mismatches.** Registered criterion: for every case, sha256 of the `F` array and
of the `names` list byte-identical before vs after regeneration; one mismatch →
GATE FAIL and STOP. This lane wrote its **own** hasher (array content: dtype,
shape, C-order bytes — not the `.npz` container) and re-derived from the two
directories on disk:

- **40/40 cases** `F` sha256 identical; **40/40** per-case `names` sha256
  identical; **0** dtype or shape changes.
- Manifest `features` name-list sha256
  **`3a6ea49ad8d20b00090479ab77cc7419189a9a7554009be5a8c340f04e943512`** on
  **both** sides — the value `FS5_D476_CLIP_REPAIR_RESULTS.md:74` claims.
- `.npz` keys `['F','names']` → `['D','F','diag_names','names']`, as recorded.
- Closure's own recorded hashes are re-derivable, not asserted: `A2_before.json`
  reproduces **40/40** from the backup `.npz`, `A2_after.json` **40/40** from the
  live `.npz`.

*Could it have failed?* **Yes, three ways.** (i) The gate re-ran the entire
110-column build from raw OpenFOAM fields for all 40 cases, so nondeterminism
anywhere in that pipeline would have surfaced. (ii) The graded column was
genuinely refactored — `build_features.py:134` went from
`np.minimum(np.sqrt(np.maximum(k, 0)) * dwall / (50.0 * nu), 2.0)` to
`np.minimum(q1_wallRe_raw, 2.0)` with the subexpression hoisted, and `F` is cast
float64 → float32 on save. (iii) The before-hashes provably predate the code
edit by **145 s** (§25), so the comparison is not against something the edit
produced. Margin: **exact identity — the gate has no band to hide in.**

**A1 — planted control. PASS, and the evidence is a disk artifact, not a
transcription.** The control is wired *inside* `companion_block()` in
`fs2_audit.py` and runs before any coverage number is emitted, so its record
sits in the delivered `fs2_audit.json` under
`coverage.q1_wallRe_unclipped_companion.planted_control`. Read back by this
lane:

| field | value |
|---|---|
| case / cell | `AR_14_Ret_180`, cell index **31818** |
| planted value | **83.48553657531738** = 1.5 × training max **55.65702438354492** (this lane's arithmetic reproduces it exactly) |
| flagged cells | **0 → 1** |
| max read back | **83.48553466796875** |
| verdict | **PASS** |

The read-back sits **1.9e-06 absolute / 2.3e-08 relative** below the plant —
the float32 round trip of the `D` array; the registered acceptance is
`max_read_back >= plant × (1 − 1e-5)`, i.e. a tolerance **400×** the observed
slack, stated in code rather than in prose.

**This lane re-derived the plant TARGET independently from the case `.npz`**:
the smallest finite cell of `AR_14_Ret_180`'s `q1_wallRe_raw` column is index
**31818**, value **4.181547e-10** — so the code's stated choice ("plant into the
smallest finite cell, which is certainly not already flagged") is the cell
actually used, and `flagged_before` = 0 is a measured baseline, not an
assumption. Case cells **31819**, case max **3.60705**, both matching §7's
table.

*Could it have failed?* **Yes, and the failure path was exercised** — see §28.

**A4 — frozen-file form. PASS, verified by byte comparison.** Pre-amendment
blob `62733e3bc5eb8105d9678c5cc868422fd7b3faf7`, **205 lines / 16,477 B**;
post blob `f05124c9e5923a195cf30f9ed0b71bb0e87ebcb4`, **259 lines / 19,598 B**,
equal to the on-disk hash. `cmp` of the pre-blob against the **first 16,477
bytes** of the post-blob: **rc=0, strict byte prefix**. `**Document version
1.1**` at line 210; `lines whose number changed above this section: 0` at line
211. 54 lines added — the 54 the record claims are carried.

*Could it have failed?* **Yes, and by the exact mechanism §6 of the results
discloses**: `FEATURE_LIBRARY.md` is generated by a writer that opens it `"w"`,
so an amendment appended before the generator was fixed would have been silently
deleted by the next run of the reproduce block printed inside the file itself.

### 27. A3 GATE FAIL — the frozen comparator's own output, not loosened, and the diagnosis is artifact-backed on its load-bearing limb

**The failure is re-derived here with the verification team's OWN comparator.**
This lane wrote an independent stripper/differ (same registered semantics —
strip `frac_at_min`, `frac_at_max`, `q1_wallRe_unclipped_companion`; different
code from closure's `a3_audit_identity.py`) and ran it over the JSONs on disk:

| comparison | canonical-text identity of the stripped objects | leaf differences |
|---|---|---|
| OLD vs **delivered** `features/fs2_audit.json` | **False** | **6** |
| OLD vs `D476_A3_triage/fs2_audit_rep2.json` (repeat, unpinned) | **False** | **6**, same values |
| OLD vs `D476_A3_triage/fs2_audit_pinned4.json` (`OPENBLAS_NUM_THREADS=4`) | **True** | **0** |

All six differing leaves are `per_family.<family>.singular_value_ratio_first_to_last`
— **the distinct differing leaf-name set has exactly one member** — and every
value reproduces `FS5_D476_CLIP_REPAIR_RESULTS.md` §4's table to every printed
digit (POOLED `3.283683756107853e+17`→`2.3283210207745232e+17`; cbfs
`1.9974553177957281e+18`→`2.460895918948894e+17`; duct
`1.1668277550363688e+33`→`2.1724294644486465e+33`; hill
`2.181588325970533e+17`→`6.432994908028177e+17`; hill_breuer
`2.2260848443269914e+17`→`9.627266059057542e+17`; hump
`2.849150482633467e+18`→`2.0245029833104083e+17`).

**The gate does not pass vacuously.** In all three files the additions the gate
strips are genuinely present: saturation statistics on **110/110** features and
the companion block present. A stripped comparison that stripped everything
would be a tautology; this one is not.

**NOT LOOSENED — verified, not accepted.** §4's A3 text at HEAD is inside the
118-line byte-identical prefix (§25), so the criterion still reads *"exactly
identical. Mismatch → GATE FAIL and STOP; a nondeterminism finding is reported,
not absorbed."* **No threshold moved after first compute.** The delivered
`fs2_audit.json` is the **unpinned** run; the pinned run is retained as labelled
diagnostic evidence only.

**The strongest single fact in this chain, and it predates the number.** The
frozen §8, committed 20 minutes before any code was touched, pre-committed the
handling: *"if it fails, that is a finding under A3, not a reason to weaken
A3."* The failure mode was named and its treatment fixed **before the answer
existed** — which is the entire evidentiary content of a freeze.

**Is the BLAS-thread diagnosis artifact-backed or asserted?** Split verdict —
**the load-bearing limb is artifact-backed; three prose rows are not.**

*Artifact-backed, re-derived here:*

1. **The controlled pinned-vs-unpinned pair.** `pinned4` and the delivered run
   are the same amended code on the same regenerated inputs, differing only in
   the pinning, and they move **exactly those six values and nothing else**
   (0 differences vs 6). That is a controlled demonstration on disk.
2. **Determinism per environment.** `rep2` reproduces the delivered six values
   exactly — the figure is not stochastic.
3. **Baseline code-fairness, read as a diff by this lane.** The only commit
   touching `fs2_audit.py` between the baseline write (2026-08-21 18:01:25Z) and
   the repair is `fd3aa735`: **4 insertions, 0 deletions, all four inside a `#`
   comment block.** No computation changed.
4. **The rank deficiency that makes `s[-1]` analytically zero**, from the
   delivered JSON: POOLED **100/110**, cbfs 100/110, hill 100/110, hill_breuer
   100/110, hump 100/110, **duct 96/110**. Every family is rank-deficient.

*Not artifact-backed, named plainly:*

5. **Three of the five thread-sweep rows rest on prose only.** `a3_diagnose.py`
   prints to stdout and **no stdout was preserved** — the triage directory holds
   the script but no log. Two rows *are* independently corroborated by preserved
   JSON: **threads=4 → `2.849150482633467e+18`, exactly the pre-D476 baseline
   hump value**, and **threads=16 → `2.0245029833104083e+17`, exactly the
   delivered value.** The **threads = 1, 2 and 8** rows are transcribed figures
   with no surviving artifact.
6. **`fs2_audit.json` records no BLAS implementation, thread count or numpy
   version.** Its top-level keys are exactly `coverage, families, n_features,
   per_family, per_feature, rank_rcond, tensor_basis_rank, zero_abs, zero_test`.
   So the label "the delivered run was 16 threads" is an **inference** from the
   sweep, not a recorded fact. The controlled pair in item 1 does not depend on
   that inference; only the specific number does.

**Corroboration this lane adds, unprompted.** `duct`'s ratio is
**2.1724e+33** against `s[0]` ≈ 7.5e+02, implying `s[-1]/s[0]` ≈ **3.5e-31** —
roughly **eighteen orders of magnitude below double-precision epsilon**. A
denominator that small is not a small singular value; it is a cancellation
artifact of the SVD. Independent arithmetic support for recommendation (a) in
§30.

### 28. Controls — each one claimed, checked for execution with a measured value

| control | executed? | measured value, and where it lives |
|---|---|---|
| **Rule-3 planted control on the companion reader** | **YES, on disk** | The full record in §26 (cell 31818, 83.48553657531738, flagged 0→1, max read back 83.48553466796875). It is not an add-on script: `companion_block()` calls `planted_control()` **before it emits any coverage number** and `sys.exit(2)` on failure, so no coverage figure can be published by a reader that has not just been shown able to see a plant. |
| **Absent-companion refusal** | **wired, did not fire** | `companion_block()` exits 2 if the companion is missing from **any** case `.npz`, rather than degrading to silence — the failure mode being repaired. Verified as a `sys.exit(2)` in the code; a refusal that does not fire leaves no positive artifact, and this lane did not provoke it. |
| **A1 refusal-path mutation proof** (control rc 0, `clipped_reader` rc 2, `ignores_disk` rc 2) | **run, but its output was not captured** | `a1_refusal_proof.py` is preserved and was read by this lane. The mutations are genuine — `clipped_reader` re-applies `np.minimum(…, 2.0)`, i.e. **the D476 defect itself**; `ignores_disk` caches by basename so the re-read never happens — subprocesses are used so the exit status is the real one, and `__pycache__` is cleared before every mutant (the stale-bytecode inversion trap). **But no stdout was saved to any file**, so §2's rc table is transcribed prose. This lane did **not** re-run it: read-only toward closure. |
| **A2 before-hashes** | **YES, on disk** | `features_backup_pre_D476/A2_before.json` (12,461 B, 20:43:16.227Z) and `D476_A3_triage/A2_after.json` (13,541 B); both re-derived **40/40** by this lane from the `.npz` themselves. |

### 29. Verdict vocabulary, and the legality of the one amendment

- **Vocabulary is CLEAN.** Verdict cells across the pre-registration, the
  results, Addendum 1 and `FEATURE_LIBRARY.md` Amendment 1 are `PASS` ×3
  (A1/A2/A4) and `GATE FAIL` ×1 (A3); the planted-control record's own
  `verdict` field carries `PASS`. **No bare `FAIL` cell, no synonym, no hedged
  label.** The tokens "GATE FAIL and STOP" in §4 are criterion prose, not cells.
- **Exactly one amendment: Addendum 1**, appended at `7e973ba8`, i.e. **after**
  first compute. §2d permits this only as a dated addendum that alters no gate,
  threshold, cap or label, with originals struck rather than rewritten.
  **Verified by byte comparison rather than by its own assertion**: the 118-line
  freeze blob is byte-identical to the first 118 lines at HEAD, so nothing above
  the addendum moved. Its self-assertion `lines whose number changed above this
  section: 0` is therefore **VERIFIED, not accepted**. **LEGAL under §2d.**
- **The scope addition is a disclosed deviation, correctly handled.** The frozen
  §3 lists four files; a fifth, `make_feature_library.py`, was changed. It is
  disclosed in Addendum 1 item 1 and results §6 with the reason — a *generated*
  file whose `"w"` generator would erase a rule-6 amendment — and proven by a
  byte-identical round trip. It adds no gate and grades nothing.

### 30. The verification supervisor's two standards rulings, recorded verbatim

These are the supervisor's own words on the two questions closure referred, and
are recorded here as **recommendations**. Binding adoption of either is Sanaa's.

> (a) `s[0]/s[-1]` of an analytically singular matrix is not a publishable
> number — it measures BLAS rounding, not the matrix; publish rank + smallest
> singular value against the registered rtol, print the ratio only when `s[-1]`
> clears that tolerance, else label it "unbounded (analytically singular)".

> (b) Any gate whose pass criterion is exact identity of RECOMPUTED
> floating-point quantities must pin threads (`OMP_NUM_THREADS=1` or recorded
> fixed N) and record the BLAS implementation; the stronger rule is to gate on
> STORED primary bytes (sha256 of saved matrices), which needs no pinning.

This lane's measurements bear on both and are offered as supporting evidence,
not as a ruling: `duct`'s `s[-1]/s[0]` ≈ 3.5e-31 (§27) for (a); the absence of
any BLAS, thread-count or numpy field in `fs2_audit.json` (§27 item 6) for (b).
Note also that **gate A2 is already the (b)-preferred form** — it hashes stored
primary bytes and needed no pinning, and it is the gate that came out clean.

### 31. Residual hazards — candidate items, none of which moves a verdict

1. **The grading record does not cite the triage directory.** §2's rc table and
   §4.1's thread sweep are read from artifacts under
   `/home/ubuntu/closure-data/D476_A3_triage/`, and that string appears **nowhere**
   in `FS5_D476_CLIP_REPAIR_RESULTS.md` or the pre-registration. It *is* cited in
   `docs/LAB_STATE.md:817`, `docs/NUMERICS_KNOWLEDGE.md:3548` and
   `docs/DOCKET.md:849`. **A reader holding only the grading record cannot find
   the evidence it grades from.** Cheapest repair: one dated line in the results.
2. **The triage directory carries a copy signature and its mtimes date
   nothing.** All eight files have mtime == ctime inside
   `21:01:32.859738`–`21:01:32.865102` — an ~5.4 ms batch write, **24 s AFTER
   the commit at 21:01:08Z that reports their contents**. They are a `cp`
   (no `-p`) of the working set, correctly rescued out of a scratch location that
   L-186 says gets wiped — but **no timestamp inside that directory dates any
   run.** All the timing evidence in §25 rests on `features/` and
   `features_backup_pre_D476/`, which do carry live mtimes.
3. **`make_feature_library.py`'s carry-forward is guarded only when the marker
   is already present.** It asserts on both sides of the write, but under
   `if AMEND_MARK in prev:` — so a future hand-written amendment placed
   **without** the marker is silently dropped, which is the exact failure mode §6
   repairs. Amendment 1 does sit below the marker (line 206 of 259), so nothing
   is at risk today. A one-line strengthening (assert the marker is present
   whenever the destination is longer than the generated text) closes it.
   Candidate repair, not a defect in this grade.
4. **A presentation nit in results §8.** The sentence says "Three features have
   `frac_at_max` above 0.1 %" above a **four-row** table; the fourth,
   `q4_pgradAlongStreamline` at `frac_at_max` = **0.0006** (0.06 %), is below the
   stated threshold and is not marked as such. Re-read from the delivered JSON by
   this lane; the "three above 0.1 %" count is itself correct.
5. **No environment provenance in `fs2_audit.json`** — §27 item 6.

### 32. Cost calibration (rule 12) — present and complete on the auditee's side

`FS5_D476_CLIP_REPAIR_RESULTS.md` §9 states predicted **against** actual:
registered **2–6 core-min**, cap **0.5 core-h = 30 core-min**; measured
registered scope **~3.0 core-min** (73.44 s build wall + 105.81 measured audit
CPU-s); total gross **~10–12 core-min**; **no overrun**. `cost_basis` correctly
declares that the CPU-uncaptured runs are **estimated** from the one measured
~3× CPU-to-wall ratio and that dollar figures would be reported-by-owner. A
ledger row exists: **`docs/COST_CALIBRATION.md` row C-6** — ratio **0.75×**
cleaned/predicted against the 4 core-min midpoint, gross/predicted **2.5–3×**,
attribution *"misprediction of scope"*, zero waste, zero contention.
**Present and sufficient; nothing is owed on this question.**

### 33. Verdict, and what closure's adoption may rest on

**AUDIT: SOUND WITH DISCLOSED DEVIATIONS** (CANDIDATE — the verification
supervisor's own read governs).

| target | verdict as reported | AUDIT (CANDIDATE) |
|---|---|---|
| **A1** planted control | PASS | **SOUND** — record on disk in the delivered audit JSON; the plant target (cell 31818) independently re-derived; the control gates the emission of every coverage number |
| **A2** model-facing identity | PASS | **SOUND** — 40/40 `F` and 40/40 `names` re-derived by this lane's own hasher, 0 mismatches; before-hashes provably predate the code edit by 145 s; non-tautological three ways |
| **A4** frozen-file form | PASS | **SOUND** — strict byte prefix proven by `cmp` (rc=0, 16,477 B), version 1.1, renumbering assertion verified |
| **A3** audit identity up to addition | GATE FAIL | **SOUND, and correctly handled** — re-derived with this team's own comparator (6 leaves, one leaf-name); not vacuous (110/110 additions present); **not loosened** (criterion byte-identical to the freeze); referral recorded; the frozen §8 pre-committed the handling before the number existed |
| the BLAS-thread diagnosis | asserted as cause | **SOUND on the controlled limb** (pinned vs unpinned: 0 vs 6 differences, code-fair baseline read as a diff) — **three of five sweep rows are prose without an artifact**, and no environment provenance is recorded (§27, §31) |
| the scope addition (`make_feature_library.py`) | disclosed in Addendum 1 | **DISCLOSED DEVIATION, legal** under §2d — gate-neutral, reason given, proven by round trip |

**On closure's adoption block (prereg §7): on this lane's evidence the block
CAN be lifted, subject to the supervisor's own read.** §7 blocks adoption on
this team's audit of the diff as a cross-team gate-instrument change. The
instrument's model-facing surface is proven untouched (A2, re-derived 40/40
here); its new reader is under a live planted control that refuses rather than
degrades (measured, on disk); and the one failed gate is failed on a statistic
that (i) the amendment did not introduce, (ii) the amendment provably did not
move — the pinned comparison returns **0** differences — and (iii) reports BLAS
rounding rather than any property of the feature library. **Adoption of the
companion diagnostic is therefore not gated by A3.**

**What must NOT ride on that lift, stated so it cannot be read wider than it
is:** `singular_value_ratio_first_to_last` itself, whose publication is the open
standards question in §30(a); and **A3's status, which stays GATE FAIL** until a
registered decision changes the instrument or the statistic. Lifting the
adoption block is not a re-grade of A3, and no standing verdict moves — the
chief's no-retroactive-regrade clause quoted in the frozen §5 stands.

### 34. What this lane could NOT establish, named plainly

- **The supervisor's §3 check-1 personal diff read of the six changed files.**
  `docs/DOCKET.md:849` attests it in detail (all six read as diffs, the frozen
  text re-diffed by hand, the A3 mismatch scope confirmed by the supervisor's
  own stripped comparison). A personal read leaves no artifact by construction;
  **taken as attested, not verified.**
- **The threads = 1, 2 and 8 rows of the §4.1 sweep** — no surviving stdout
  (§27 item 5). The claim they support is separately established by the pinned
  pair, so nothing load-bearing rests on them, but they are not evidence.
- **That the delivered run ran at 16 threads specifically** — inferred from the
  sweep, not recorded anywhere in the artifact (§27 item 6).
- **The `_b`-form crowding pattern** the results §8 leaves open (frac_at_max = 0
  with p99 near the bound). This lane read the saturation columns and confirms
  they do not resolve it; resolving it is a new measurement, not an audit act,
  and none was taken.
- **No closure comparator was re-executed.** Every gate above was re-derived by
  **independent code over the values the instruments wrote to disk**, plus one
  independent re-read of the raw `.npz`. That tests the grading arithmetic, the
  thresholds and — via the `.npz` re-read — the A2 hashes and the A1 plant
  target. It does **not** test the field-reading front of `build_features.py`;
  that is covered instead by A2's own bit-identity across a full regeneration.

**Cost of this pass:** zero solver core-minutes. One compute step — the A2
re-derivation over 80 `.npz` arrays — measured by `/usr/bin/time` at **7.12 s
wall / 7.68 CPU-s single core = 0.128 core-minutes**, against this lane's own
pre-stated prediction of **3–6 core-minutes**: **ratio ≈ 0.032× of the low
end**, i.e. this lane **over-predicted by roughly 30×**; attribution:
mispricing compressed `.npz` reads at their full uncompressed size. Everything
else was reads, `git` hashes and JSON arithmetic. Nothing under
`cases/RANS_LES_closure_models/` or `/home/ubuntu/closure-data/` was written.

## Supervisor's own read of pass 6 — 2026-08-24, verification-supervisor: BELIEVED

**Lines whose number changed above this section: 0.** Appended at the foot,
built from `git show HEAD:docs/CROSS_TEAM_GATE_AUDIT.md`, never from the
worktree. This section carries no `###` number of its own so that the lane
passes appending concurrently (7, 8) keep the running section count.

Pass 6 above was a lane's CANDIDATE. The verification supervisor of the
session that dispatched it was killed before reading it (transient API error,
~16:00Z 2026-08-24; L-186 — nothing of that read survived). This supervisor,
its re-spawn, re-derived every load-bearing limb with **its own code, not the
lane's and not closure's**, read-only toward closure's territory:

| pass-6 claim | re-derived by the supervisor | agrees? |
|---|---|---|
| §25 freeze: `bf4956bc` one file, 118 insertions, alone | `git show --stat bf4956bc`: 1 file changed, 118 insertions(+), committer 2026-08-23T20:40:34Z | yes |
| §25 frozen blob `8fac067c…` == the sha `RESULTS.md:4` claims | `git rev-parse bf4956bc:<prereg>` = `8fac067cf4a2c19a205df529db6c79bd48e31f3d`; `RESULTS.md:4` reads the same | yes |
| §25 118-line freeze blob is a byte prefix of HEAD's 147-line file | `head -118 <disk> \| cmp - <frozen blob>` rc=0; disk == HEAD == `7e973ba8` blob `6110dbe0…`; path history exactly two commits | yes |
| §25 first evidence 162 s after the freeze | `A2_before.json` mtime 20:43:16.227Z vs freeze 20:40:34Z = +162 s; the A3 "old" side `features_backup_pre_D476/fs2_audit.json` dated 2026-08-21 18:01:25Z, the baseline compared against | yes |
| §26 A2 40/40 `F` and `names` identical | own hasher (dtype, shape, C-order bytes of `F`; `names` list equality) over `/home/ubuntu/closure-data/features/*.npz` vs `features_backup_pre_D476/*.npz`: **40 of 40 identical, 0 bad**; live keys `['D','F','diag_names','names']`, `F` float32 | yes |
| §27 A3: 6 leaves / one leaf-name unpinned; 0 pinned | own stripper/differ (strip `frac_at_min`, `frac_at_max`, `q1_wallRe_unclipped_companion`, compare every leaf path): delivered `fs2_audit.json` **6 differing leaves**, `rep2` **6**, `pinned4` **IDENTICAL**; the only differing leaf name is `singular_value_ratio_first_to_last`; hump `2.849150482633467e+18 → 2.0245029833104083e+17` as printed | yes |
| §26/§28 A1 planted-control record on disk | `coverage.q1_wallRe_unclipped_companion.planted_control` in the delivered JSON: case `AR_14_Ret_180`, cell 31818, planted 83.48553657531738 = 1.5 × 55.65702438354492, flagged 0 → 1, max read back 83.48553466796875, verdict PASS | yes |
| §27 rank deficiency | per_family ranks: cbfs 100/110, duct 96/110, hill 100/110, hill_breuer 100/110, hump 100/110, POOLED 100/110 | yes |
| frozen §4/§7/§8 text | read from the frozen blob: A3 criterion "exactly identical … a nondeterminism finding is reported, not absorbed"; §7 blocks adoption on this team's audit; §8 pre-commits "if it fails, that is a finding under A3, not a reason to weaken A3" | yes |

**Nothing the lane claimed failed to reproduce.** The residual hazards of
§31 and the four unestablishable items of §34 stand as written; none moves a
verdict. §34's first item — the closure supervisor's own §3 check-1 diff read —
remains attested, not verified, by construction.

**Ruling (this team's, under the standing cross-team-audit mandate):**
**AUDIT: SOUND WITH DISCLOSED DEVIATIONS — BELIEVED.** A1 PASS, A2 PASS,
A4 PASS, A3 GATE FAIL all stand as the frozen comparator's own output. **The
prereg-§7 adoption block on closure's amended FS5 instrument is released by
this audit** on exactly the grounds §33 states and no wider: the model-facing
surface is untouched (A2), the new reader is under a live planted control
that refuses rather than degrades (A1), and the A3 failure is on a statistic
the amendment neither introduced nor moved. A3 stays GATE FAIL; the
publication of `singular_value_ratio_first_to_last` is the open standards
question §30(a) — recommendation only, binding version Sanaa's; no standing
verdict moves (frozen §5). Relayed to the chief for closure's adoption ruling.

**Cost of this read:** zero solver compute; one Python step over 80 `.npz`
arrays and three JSONs, 5.54 s wall single core ≈ 0.09 core-min, plus git
reads. Pass 6 itself: 0.128 core-min measured against the lane's own 3–6
core-min prediction (ratio ≈ 0.03×, attribution mispricing compressed `.npz`
reads) — ledger row appended under this belief commit.

## Audit pass 8 — 2026-08-24, verification LANE (CANDIDATE, not the supervisor's own read)

**Lines whose number changed above this section: 0.** This section is appended
at the foot of an append-only file. The base for this edit was taken from
`git show HEAD:docs/CROSS_TEAM_GATE_AUDIT.md`, re-read inside the commit
invocation itself and never from the worktree — which is stale here by 48 lines
(a strict prefix of HEAD, the D486 index-decay signature), so writing the
worktree copy would have destroyed the supervisor's own pass-6 read. The blob
was staged by `hash-object` from the HEAD base plus this text, so no peer's
uncommitted work was overwritten and section numbering continues from **34**,
the highest numbered section at the HEAD this was built on.

**This pass was run by a `lab-lane`, not by the verification supervisor
personally.** `SUPERVISION_CHARTER.md` §3 is explicit that a relayed check is a
summary and not a check, so **every finding below is CANDIDATE until the
verification supervisor re-derives it.** Each finding names the artifact it was
read from. The lane was **read-only toward closure's territory** throughout:
nothing under `cases/RANS_LES_closure_models/` or `/home/ubuntu/closure-data/`
was written, no closure comparator was re-executed, and every gate below was
re-derived by this lane's **own code over the values closure's instruments
wrote to disk**.

**Target:** closure's **Ling 2016 TBNN GPU arm — the lab's FIRST GPU run.**
Pre-registration frozen at `e8309b6c` (2026-08-23T21:18:12Z); driver, comparator
and launcher at `11f93da6` (21:19:18Z); graded and committed at `353925c7`
(2026-08-24T16:07:26Z) as **NOT A RESULT** on its own gates. Records:
`cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/{PREREGISTRATION.md,RESULTS.md,
artefacts/grading_witness.json,run_all_gpu.sh,score_gpu_ling.py,train_gpu_ling.py}`;
run outputs `/home/ubuntu/closure-data/tbnn_gpu/`; ledger rows **C-16** and its
correction **C-19** in `docs/COST_CALIBRATION.md`; docket **D490**; lessons
**L-267**, **L-268**; numerics **N-B40**, **N-B41**, **N-B42**.

**Index decay, checked first because the brief flagged it.** All six `gpu/`
paths show a staged deletion (`D `) in the shared index. **It is not a
deletion.** For every one of the six the on-disk blob id equals the HEAD blob
id — `PREREGISTRATION.md` `910cea44…`, `RESULTS.md` `4c8afdde…`,
`artefacts/grading_witness.json` `daaf508d…`, `run_all_gpu.sh` `034cf739…`,
`score_gpu_ling.py` `3da5c706…`, `train_gpu_ling.py` `662b8461…` — and the
sha256 of each disk file equals the sha256 of its HEAD blob. **HEAD and disk
agree byte-for-byte on all six.** D486's mechanism is confirmed live on a
second, independent path set.

### 35. Freeze order — the strongest form this lab has produced, re-derived

| check | finding |
|---|---|
| Prereg committed **alone**, before any compute | **YES.** `e8309b6c`, committer 2026-08-23T21:18:12Z, **one file, 509 insertions, nothing else in the commit.** |
| Path history | **Exactly one commit** for `gpu/PREREGISTRATION.md` (checked without `--follow`, which otherwise reports the unrelated `PREREGISTRATION_DRAFT.md` ancestor at `9e82321b`). The path does not exist at `9e82321b`. **Never edited after the freeze.** |
| Frozen sha == the sha the record claims | **YES, three ways.** Disk sha256 = HEAD-blob sha256 = `61b2097f63a38f320aeb98275f4a7aaba8454880fe2389398ee59678d4d81d97`, which is the value in the `e8309b6c` commit message, in `RESULTS.md:6`, in `artefacts/grading_witness.json` (`prereg_sha256`) and in the run's own `/home/ubuntu/closure-data/tbnn_gpu/run_window.json`. |
| First artifact of the run window vs the freeze | **The run starts 197–200 s AFTER the freeze commit.** `run_window.json` mtime **2026-08-23 21:21:29.700Z** (+197 s) and it records `commit: e8309b6c` and the frozen sha *inside itself*; `driver.log` created **21:21:30.575Z** at **0 bytes**; the first gate artefact `out/status_g0.json` **21:21:32.575Z** (+200 s), its own `utc` field reading `2026-08-23T21:21:32Z`. **Nothing that answers a gate predates the freeze.** |
| The one file that legitimately predates it | `node_root/pip_install.log`, mtime **21:07:08.310Z**, 11 min before the freeze. It is the environment build on the bare node — F.3's *"Environment (installed 2026-08-23, bare node)"* — and answers no gate. |
| Do the run-directory mtimes date anything? | **YES, and this is the contrast with pass 6 §31 item 2.** The 55 files under `tbnn_gpu/` carry mtimes spread **continuously across the whole 10.71 h window** (21:21:29 → 08:03:58), stage by stage — `hist_tbnn_s0.csv` 22:25:50, `s1` 23:30:09, `s2` 00:34:24, … `pred_armb_s4.npz` 08:03:58.079, `spend.json` 08:03:58.081. That is a time-preserving sync, not the millisecond batch-write signature of a `cp` without `-p`. **The sync-back mtimes are live node times and they do date the run.** |

### 36. The three code files — hashes, mtimes, and the copy that actually ran

| check | finding |
|---|---|
| F.4's sha256 table == the `11f93da6` blobs | **YES, all three.** `train_gpu_ling.py` `1bac03bd…0ed3`, `score_gpu_ling.py` `4f9eda16…2aac`, `run_all_gpu.sh` `5b9c68eb…6fad`, re-hashed by this lane from `git show 11f93da6:<path>`. |
| F.4's table == disk | **YES**, same three values, re-hashed from disk. |
| Did any code file change after the freeze? | **NO.** Each of the three has **exactly one commit in its whole history** — `11f93da6` — and disk blob id == HEAD blob id == `11f93da6` blob id. There is no second edit anywhere. |
| The order the freeze fixed hashes in | **The code was written BEFORE the freeze and committed 66 s AFTER it.** Disk mtimes: `run_all_gpu.sh` **21:12:10.116Z**, `train_gpu_ling.py` **21:13:59.339Z**, `score_gpu_ling.py` **21:14:05.034Z** — all earlier than `PREREGISTRATION.md`'s own **21:18:11.693Z**. So F.4 fixed the hashes of files that already existed and were unchanged when `11f93da6` landed at 21:19:18Z. This is the correct order: the freeze names the grading path, and the commit that publishes it must hash to the names already frozen. It does. |
| The file that ran on the node | **Bit-identical to the frozen driver.** The synced node copy `/home/ubuntu/closure-data/tbnn_gpu/node_root/train_gpu_ling.py` (mtime 21:21:30.337Z, i.e. the launcher's re-copy at run start) hashes to **`1bac03bda82eab98b14dc49ccc01ca9542a764a8caf34d2d22e0213b79d10ed3`** — the frozen F.4 value. Rule 2's *"verify the frozen file IS the file that ran"* is satisfied for the driver by a hash of the actual node copy, not by assertion. |

**The frozen file against the draft it claims to preserve — checked by diff, not
by its own STATUS line.** `PREREGISTRATION.md` lines **9–405** are identical,
line for line, to `PREREGISTRATION_DRAFT.md` lines **2–398**. Two things are
absent from the frozen file: the draft's line-1 `STATUS: **DRAFT — NOT FILED,
NOT LAUNCHED**` stamp (replaced by the freeze STATUS block, as declared), and
the draft's whole **§14**, a 13-line supervisor addition. The STATUS block's
claim is *"sections 1-13 below are the draft's, byte-preserved"* — **literally
true, and verified.** But see §42: the dropped §14 is the section that said the
signed file's `cost_basis` *"must carry the console-read price"*, and its
removal is not flagged anywhere. **Gate-neutral** (§14 registered no gate,
threshold, arm, seed, range or cap), so it is a disclosure gap, not an
amendment violation.

### 37. The NOT A RESULT — the frozen comparator's own output, re-derived here

**This lane wrote its own grading arithmetic** (independent of
`score_gpu_ling.py`, reading only the values that comparator wrote to
`/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json`) and re-derived every
gate. **Every printed figure in `RESULTS.md` §1 and §2 reproduces.**

**G1 — ARM-A TBNN a-priori. Registered: below SST, below `b = 0` and below the
train-mean tensor on ≥ 6 of 8 TEST cases; 4–5 → GATE FAIL; ≤ 3, *or failure to
beat `b = 0` anywhere* → NOT A RESULT.** Re-derived per-case means over the five
seeds, computed here from `per_seed`, not read from any summary field:

| case | ARM-A TBNN | SST | `b = 0` | train-mean |
|---|---|---|---|---|
| AR_14_Ret_180 | 0.9182 | 0.5799 | 0.5842 | 0.4036 |
| AR_1_Ret_360 | 1.0534 | 0.5972 | 0.5996 | 0.4221 |
| AR_3_Ret_360 | 0.9052 | 0.5523 | 0.5580 | 0.3866 |
| NASA_2DWMH | **7.010e+07** | 0.3318 | 0.3398 | 0.2949 |
| α05_4071_2024 | 0.3622 | 0.3271 | 0.3457 | 0.2586 |
| α05_4071_4048 | 0.4004 | 0.3512 | 0.3791 | 0.3014 |
| α15_13929_2024 | 0.4929 | 0.3339 | 0.3355 | 0.2714 |
| α15_13929_4048 | 0.3178 | 0.2889 | 0.3128 | 0.2258 |

**Wins: 0 of 8 against SST, 0 of 8 against `b = 0`, 0 of 8 against the
train-mean.** The registered *"failure to beat `b = 0` anywhere"* branch fires
on its own terms. **The verdict is the gate's own branch, not a post-hoc
reading**, and the branch that fired is the one written into the frozen §8
before any compute existed.

**G2 — invariance embedding. GATE FAIL, re-derived.** TBNN pooled mean
**3.896e+07** (per-seed 2.015e+07–5.476e+07, spread 3.462e+07) against the plain
MLP's **0.360359** (per-seed 0.3182–0.4096, spread 0.09139). The TBNN is
**1.081e+08 ×** the MLP's pooled error — above it, not below it, before the
spread comparison even applies.

**G3 — realisability. NOT A RESULT on both TBNN models, re-derived against the
thresholds recomputed from the frozen wording**, not from the results' prose:
`truth_viol_frac_test` = **0.0079137162** in the grading JSON → 3× = **2.3741 %**;
2·√(2/3) = **1.632993**.

| model | per-seed violation % | per-seed max ‖b‖_F |
|---|---|---|
| ARM-A TBNN | 3.0999, 4.6053, 5.3390, 4.5142, 5.0354 | 1.694e10, 1.344e10, 1.614e10, 2.125e10, 7.813e9 |
| ARM-B best | 12.4567, 4.3044, 11.9899, 6.3336, 14.4388 | 8.181e8, 9.403e8, 5.563e6, 8.715e8, 3.204e8 |

**Every seed of both models fails both clauses**, the norm clause by nine to ten
orders of magnitude. Charter §4's *"regardless of RMSE"* is what makes ARM-B's
excellent RMSE irrelevant here, and the frozen §8 quoted that clause verbatim.

**Were any thresholds moved after first compute?** **NO, and this is verified by
byte comparison rather than accepted.** §8's whole text sits inside the
frozen file's single, never-amended commit (§35), so the criteria this lane
graded against are literally the bytes committed at 21:18:12Z, 200 s before the
first gate artefact existed. **`RESULTS.md` contains no amendment, no addendum
and no struck text**; its §4 "Disclosures and departures" are dated disclosures
that alter no threshold — D-1 says so explicitly: *"The gate fired on the
registered configuration; the threshold, budget and arm are not rewritten."*

**The two pre-stated falsifiers, re-derived.** Falsifier 1 fires as written
(ARM-A's TBNN loses to the CPU lane's on every case and every baseline, 0/8
against 7/8), and D-1 correctly bounds what that licenses — the arm ran the
paper's *rate* at one update per epoch against the paper's *"weights were updated
after each training point"*, so D3 is not settled. Falsifier 2 **does not fire**,
and this lane re-derived it from the two primary logs rather than from the
results table: CPU lane `../train_log.json` TBNN `val_best` = 0.169337, 0.164549,
0.162009, 0.162257, 0.164794 → **mean 0.164589, spread 0.007328**; ARM-B retrain
`out/status_armb_retrain.json` = 0.158399, 0.161046, 0.159979, 0.157543, 0.161073
→ **mean 0.159608, spread 0.003530**. Advantage **0.004981**, inside the
governing (larger) spread **0.007328**. *(Presentation nit: `RESULTS.md` §3
prints the advantage as `0.0051`, the difference of the rounded means; the
unrounded difference is 0.004981. The grade is identical either way — the margin
to the spread is 0.0023 — so nothing turns on it.)*

**The "search re-selects the CPU recipe" claim — checked against the CPU lane's
own source, not against its prose.** `../train_tbnn.py:34` `BATCH = 8192`,
`:35` `LR_TBNN = 1e-3`, Adam at `:189`, `nh=30, nlayers=8` at `:82`. The TPE
search's selection (`out/status_armb_search.json`, 100 trials complete):
**batch `8192` — identical**, **lr `1.0228870826023146e-3` — 2.29 % from `1e-3`**,
Adam, `LeakyReLU(0.01)`. Architecture 9×77 against 8×30. **The claim holds on the
optimiser axes exactly and the architecture axis is where it differs.**

### 38. Could the gates have passed — and the non-tautology proof is inside the same artefact

**No gate here is one that no model could pass, and the proof does not require a
hypothetical: the run contains a model that clears each.**

- **G3 is passable, demonstrably, in this very run.** The ARM-A control MLP,
  trained by the same driver on the same data and scored by the same comparator,
  reads **0.0000 % violation on all five seeds** with `max ‖b‖_F` **0.1179 to
  0.2223** — inside **both** G3 clauses on every seed. A gate that one of the
  three trained models satisfies at zero and two fail by ten orders of magnitude
  is discriminating, not decorative.
- **G1's shape is reachable in this run too.** ARM-B's 9×77 network beats **all
  three** baselines on **7 of 8** cases (re-derived here: 7/8 against SST, 7/8
  against `b = 0`, 7/8 against the train-mean) — i.e. it clears the ≥ 6-of-8 bar
  G1 sets. ARM-B is not a G1-gated model under the frozen §8, so this does not
  change the verdict; it establishes that **the threshold is one a model produced
  by this pipeline can meet.**
- **What would have passed G1**, stated as the brief asks: the ARM-A TBNN needed
  to be below `b = 0` on six cases. Its per-case ratios to `b = 0` are **1.016,
  1.048, 1.056, 1.469, 1.572, 1.622, …** — so on the three closest cases it was
  short by **1.6 %, 4.8 % and 5.6 %**, and it would have had to improve by
  ≈ 47 % on the fourth. Not a hair's breadth, but not a structurally impossible
  bar either.
- **What would have passed G2:** a TBNN pooled figure below **0.269** (the MLP's
  0.360359 less the governing spread 0.09139). It read 3.896e+07.
- **What would have passed G3:** violation ≤ 2.374 % *and* `max ‖b‖_F` ≤ 1.633.
  The MLP read 0.000 % and ≤ 0.223.

**One residual hazard on G3's second clause, named because it is a standards
question and not a defect in this grade.** The `b_RANS` (k-ω SST) baseline's own
`max ‖b‖_F` on the scored TEST cells is **3.4819** — **2.13 × the 1.633 norm
bound**. So G3's norm clause is an absolute bound that the RANS *reference field*
does not itself satisfy on these cells, while its violation-fraction clause is
scaled to the truth and the truth passes by construction. Nothing here turns on
it — both TBNN models exceed the bound by nine orders of magnitude — but a bound
the reference violates cannot discriminate at the margin, which is the same
family of question as pass 6 §30. **Candidate for the standards docket; no
re-grade, and this lane does not rule.**

### 39. Controls — each fired, with a measured value on disk

| control | executed? | measured value, and where it lives |
|---|---|---|
| **Rule-3 planted zero (G0a)** | **YES, twice, on two machines** | `out/status_g0.json` and `grading_gpu_ling.json.plant_control`: `PLANT` = **1.234e-03** into `b_LES[k,0,1]` and `[k,1,0]` of cell **474490**, case `AR_14_Ret_180`, `b01_before` = 0.029159002006053925. `rms_clean` **0.5841749700516138** → `rms_planted` **0.5841749740294948**, **diff 3.9779e-09 (non-zero)**, back-solved `recovered_plant` **0.0012340000000000198**, `rel_err` **1.5990664132282154e-14** against the registered 1e-9 tolerance — **inside by a factor of 6.25e+04**. |
| **Realisability-reader plant (G0b)** | **YES, on disk** | A cell forced to `diag(1,1,-2)`, `‖b‖_F` = **2.449489742783178** (= √6, as the frozen §9 registers): `g0b_flagged: true`, `g0b_min_bary: -5.0`. The reader is shown able to see an unrealisable tensor before G3 grades anything. |
| **Cross-machine determinism control** | **YES — and this lane checked it is genuinely two computations, not a copy** | All **nine** shared fields of the node's `status_g0.json` (written by `train_gpu_ling.py` on `gpu1`) and the lab box's `plant_control` (written by `score_gpu_ling.py` here, 18 h later) are **bit-identical**, to the last digit of `rms_clean`, `rms_planted`, `recovered_plant` and `rel_err`. **`score_gpu_ling.py` contains no reference to `status_g0.json`** (checked by grep of the source): it re-plants and re-reads from the clean dataset itself. So this is one control executed twice, on two machines, by two different programs, agreeing bit-for-bit. |
| **The refusal is structural, not an add-on** | **wired; did not need to fire** | `score_gpu_ling.py` refuses at lines 105–109 (`if diff == 0.0 or rel >= 1e-9` → print refusal, `sys.exit(2)` **with no JSON written**) and 117–119 (G0b blind → exit 2). **The existence of `grading_gpu_ling.json` is therefore itself proof the plant was read back** — no number in it could have been emitted by a reader that had not just been shown able to see the plant. The driver has the mirror image at `train_gpu_ling.py:256–261, 274–277`, writing a `REFUSED` status then exiting 2. |
| **Leakage / row-identity guard** | **wired; did not fire** | `score_gpu_ling.py:151–154`: if a prediction file's `idx` array is not equal to the clean dataset's TEST rows, it prints `[refuse]` and exits 2. Verified as source, not provoked. |
| **Seed control** | **YES** | `train_gpu_ling.py:360` `torch.manual_seed(seed); np.random.seed(seed)` per run; five seeds on every arm; TPE `sampler: TPE(seed=0)` recorded in `status_armb_search.json`. Both `pred_best` and `pred_final` were scored — `RESULTS.md` §2's claim that they differ only on TBNN seed 1 and on ARM-B is checkable in the grading JSON, which carries all six model blocks. |
| **Cap guard** | **wired; never fired, and its absence is verifiable** | `train_gpu_ling.py:205–211, 457–460, 508–513` write a `BLOCKED` status and `exit 3`. All **six** `status_*.json` files read `"state": "DONE"`; **no file anywhere in the run directory carries `BLOCKED` or `REFUSED`**. Spend 10.71 of the registered 60 GPU-h. |
| **`--frozen` interlock** | **wired** | `train_gpu_ling.py:23–24`: training never starts without `--frozen`; without it only `g0` runs. This is a code-level enforcement of rule 2, not a convention. |
| **The F.5(1) live refusal** ("the first implementation refused with exit 2, measured 9.3e-9") | **NOT verifiable** | Prose in the frozen file; **no stdout, log or status artefact of that refusal survives** anywhere this lane could find. See §47. |

### 40. **DEFECT FOUND** — two dangling lesson citations in the grading record (rule 11)

`RESULTS.md` §4 cites lessons that are not its own:

- **line 164** (disclosure D-1, the optimiser design defect): *"…must register
  **updates**, not epochs, and cost them **(L-264)**."*
- **line 174** (disclosure D-2, the idle waste): *"Cause: the completion→stop
  path depended on a live agent **(L-265)**."*

**At the parent of `353925c7` the maximum existing lesson id was 266**, and that
commit correctly added **L-267** and **L-268** — rule 11 applied properly at the
tail. **L-264 and L-265 already existed at that parent and belong to dafoam's
W4 O2 re-buy** (a cgroup memory cap; a spend prediction tested only by a run that
stops for the predicted reason). A reader following D-1's citation lands on a
memory-cap lesson from another team.

**Every other surface is correct**, which is what confines the defect: the
`LESSONS.md` blocks themselves name their targets right — L-267 *"Where it
fired: `Ling2016_TBNN/gpu/RESULTS.md` D-1, §3"*, L-268 *"… D-2, §5"* — and
`docs/DOCKET.md` D490 cites L-267 and L-268, ledger row C-16 cites L-268, and
`docs/LAB_STATE.md` cites L-267. **The back-references all point the right way;
only the forward references from the grading record are wrong.**

**No verdict moves.** `RESULTS.md` is a grading record, not a frozen file, so
rule 6 does not bar a repair; the lab's convention is a dated correction that
strikes rather than rewrites. Cheapest repair: two struck citations and a dated
line in §4. **Reported to closure, not repaired by this lane** — read-only.

**The mechanism worth carrying**, because it is rule 11's failure mode in a form
the rule's own text does not quite name: these were not stale *tail* numbers
drifting behind a moving maximum. **They were ids that were already occupied at
the moment the draft was written** — the draft reached below the tail, not past
it. Re-deriving the tail at commit time (which closure did, correctly, for the
LESSONS blocks) does not fix citations embedded in prose elsewhere in the same
commit. **A commit that assigns a new id must re-derive it in every file that
names it, not only in the file that defines it.**

### 41. Verdict vocabulary — CLEAN

Token census across the surfaces, taken from the HEAD blobs:

- **`PREREGISTRATION.md`**: `NOT A RESULT` ×9, `PASS` ×5, `GATE REACHED` ×5,
  `GATE FAIL` ×3, `BLOCKED` ×3, `PENDING` ×1.
- **`RESULTS.md`**: `NOT A RESULT` ×6, `GATE FAIL` ×3, `GATE REACHED` ×2,
  `PASS` ×1, `BLOCKED` ×1.
- **`artefacts/grading_witness.json`**: no verdict token — correctly, it is a
  hash witness and grades nothing.
- **`docs/DOCKET.md` D490** and **`docs/LAB_STATE.md`**: `G0 PASS`,
  `G1 NOT A RESULT`, `G2 GATE FAIL`, `G3 NOT A RESULT`, `Verdict: NOT A RESULT`.

**No bare `FAIL` cell.** The single apparent hit — `PREREGISTRATION.md:301`
beginning `FAIL**;` — is the token `GATE FAIL` wrapped across lines 300–301 by
markdown reflow, verified by reading the pair. **No synonym and no hedge**: a
sweep for "roughly converged", "partial pass", "near-pass", "inconclusive",
"marginal pass", "weak pass", "soft fail", "essentially passed" returns **zero
hits** in either file.

**One boundary, the same one pass 5 §21 named and the charters still have not
written down.** The driver's status files carry `DONE`, `RUNNING`, `BLOCKED` and
`REFUSED` as **stage states**, and `RESULTS.md` quotes two of them ("no BLOCKED
or REFUSED state was ever written"). `BLOCKED` is in the rule-1 vocabulary;
`DONE`, `RUNNING` and `REFUSED` are not, and they are machine states of a
process, not grades of a hypothesis. **No confusion arises here** — no stage
state is used as a verdict anywhere — but a process-state vocabulary that
overlaps the verdict vocabulary on exactly one token is a trap worth a charter
line. **Candidate, not a finding against this rung.**

### 42. GPU cost basis under rule 12 — the price is NOT a console read, and the record says so at every surface

**Rule 12's GPU clause requires a `cost_basis` "in GPU-hours priced from the
console, never from recall." The rate used is neither.**

The rate is **$0.8048/GPU-h** for `g6.xlarge`, Linux, on-demand, us-east-2, taken
from **AWS's published on-demand pricing feed**: `docs/GPU_CAPABILITY_STATE.md`
§9 records the source URL, the JSON path
(`regions["US East (Ohio)"]["g6 xlarge US East Ohio Linux"].price`), the
OnDemand rateCode term `JRTCKXETXF`, the literal payload string `"0.8048000000"`,
the retrieval stamp **2026-08-23 21:00:47 UTC**, and the payload's own
`hawkFilePublicationDate: 2026-08-21T02:02:57Z`.

**Is it labelled honestly? YES, and unusually so — at five surfaces.** The frozen
F.2 is headed *"cost_basis — published price list, not recall, not a console
read"*; §9's provenance-label row reads **"published price list, retrieved
2026-08-23 — satisfies 'never from recall'; the console itself remains Sanaa's to
read and a console figure supersedes this one if they ever differ"**;
`RESULTS.md` §5 repeats "published price list retrieved 2026-08-23"; ledger row
C-16 repeats it inside the actual-cost cell; D490 repeats it. **And §7's row
"Console price check: NOT DONE" is left standing, unedited, superseded only by
an explicit statement rather than by a silent overwrite.** Dollar figures are
labelled **"derived, not measured"** everywhere they appear, which is right — the
box cannot read its own billing.

**So: a documented deviation from rule 12's literal wording, disclosed rather
than papered over.** The source is strictly stronger than the "recall" the rule
forbids and strictly weaker than the "console" it names. **This lane does not
rule on whether the substitution is acceptable — that is the supervisor's, and
the console read is Sanaa's.**

**One thing that makes the substitution worth flagging rather than waving
through.** Two records had already committed to the console read specifically.
`GPU_CAPABILITY_STATE.md` §8 states the standing operational rule as *"nothing
trains until the Ling2016 TBNN pre-registration carries the console price in its
`cost_basis` **and** Sanaa's per-item sign-off."* And the draft's **§14** — the
section the frozen file dropped (§36) — said *"The signed file's `cost_basis`
must carry the console-read price."* **The frozen file both dropped the section
that stated the requirement and met the requirement with a substitute source,
and its STATUS block does not mention the dropped section.** Gate-neutral, so it
is a disclosure gap, not an amendment violation — but the two limbs together are
why this reads as a substitution rather than a satisfaction.

**Not independently verifiable from this box**, and this lane did not try: there
is **no AWS CLI on this machine** (`which aws` → absent), and rule 8 governs
what may leave the box. The feed value is taken as recorded.

### 43. Below the registered floor, and the waste — carried, separated, and re-derived

**The measured spend re-derives exactly.** Summing the six stage figures in
`out/spend.json` — g0 0.8595 s, p0 3.7290, arma_tbnn 19,278.6208, arma_mlp
9,742.4880, armb_search 9,309.3383, armb_retrain 204.5737 — gives **38,539.6093 s
= 10.705447 h**, against the file's own `total_hours` **10.7054**. At $0.8048 that
is **$8.6157 → $8.62 derived**, the figure of record. The wall window
21:21:29Z → 08:03:58Z is 10.708 h, i.e. **10 s of inter-stage overhead across
six stages** — the stage sum is not a proxy for the window, it is the window
minus a measured gap.

**The 12–52 GPU-h range against 10.7054 measured — BELOW THE FLOOR — is carried
on the verdict surface.** `RESULTS.md` §5's ratio row states it in the words
*"Actual/registered-floor **0.892 — below the 12–52 range**"*; ledger C-16's
ratio cell states *"0.974 vs P0 projection; 0.892 vs the registered floor —
**BELOW the registered range**"*; D490 states *"below floor"*. Re-derived:
10.7054 / 12 = **0.8921**; 10.7054 / 10.99 = **0.9741**. **It is not in the
top-of-file verdict block**, which carries the gate ladder only — a
presentational point, not a defect, since rule 12 places the estimate-vs-actual
comparison in the calibration ledger, where it is prominent. **An under-run is
not an overrun**, so rule 12's "an overrun stops the run" clause never engages;
what is owed is a calibration, and §45 finds it present.

**The 7.88 GPU-h idle is named separately and is NEVER absorbed into the
ratio.** `RESULTS.md` §5 gives it **its own table row** — *"waste, separately
named | 0 | **7.88 GPU-h idle after completion = $6.34 derived**"* — and C-16
carries it in the attribution column as *"WASTE, separately: 7.88 GPU-h = $6.34
derived"*. **Checked arithmetically, not taken on the word:** the ratios 0.892
and 0.974 are computed from **10.7054** alone; had the waste been folded in, the
figures would have been 18.585 GPU-h → 1.549 and 1.691. **They are not.** The
window 08:03:58Z → 15:56:45Z re-derives to **28,367 s = 7.8797 h = $6.3416**,
i.e. the 7.88 and $6.34 of record. Cause named, not absorbed: the overnight
session limit killed the fleet, so no agent existed to report completion
(L-268).

**Is the instance recorded STOPPED, with evidence?** `GPU_CAPABILITY_STATE.md`
§10 records **"`gpu1` — STOPPED by Sanaa (2026-08-24, reported without a
clock)"**, carrying her verbatim ruling *"GPU shutdown suggestion: yes approved
(also i stopped that instance)"*, and states plainly that **this box has no AWS
CLI and cannot read the instance's shutdown-behaviour attribute.**
**Owner-reported, labelled as owner-reported.**

**This lane added an independent probe, with a positive control on its own
reader** (rule 3's discipline applied to a reachability check, since an
unreachable host is a kind of zero):

| probe, 2026-08-24 ~16:20Z | result |
|---|---|
| `ssh ubuntu@172.31.44.162` (gpu1's canonical private IP, the `gpu1` alias in `~/.ssh/config`) | **`Connection timed out`**, then **`No route to host`** on the alias |
| **positive control** — the identical command against this box's own private IP `172.31.43.247` | **`Permission denied (publickey)`** — the TCP connection completed and SSH negotiated |

**So the reader can see a live SSH host and cannot see `gpu1`.** That is positive
evidence of unreachability from a reader shown able to detect reachability. It is
**not** proof of the AWS instance state — a running instance behind a revoked
security group reads the same — and no billing state is readable from this box.
**Recorded as corroboration of the owner's report, not as a verification of it.**

### 44. The comparator witness — what it closes, what it does not, and it is NOT the pass-2 class

The chief asked specifically whether the comparator's sha is now witnessed in the
grading artefact, since at 15:55Z it was not.

**What is there.** `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/artefacts/grading_witness.json`
exists, and **the HEAD blob and the disk file are identical** (blob
`daaf508db768616cdc5abaed56fae8632eb3d40c` both sides; no difference). It
carries the comparator's sha256 three ways and asserts they agree —
`comparator_sha256_on_disk_at_write`, `comparator_blob_at_11f93da6_sha256` and
`frozen_F4_table_sha256`, all **`4f9eda1617e860718ec7adb8f89d45452ec90929ba75968b145b1fc05fdb2aac`**,
with `all_three_equal: true`. **This lane re-derived all three independently**
(re-hashing the disk file, re-hashing `git show 11f93da6:<path>`, and reading the
F.4 table line from the frozen blob): **all four values agree.** It also carries
`grading_json_sha256` `f56dec949c68d6fc64402033319b2059e2051aa3bf00230958d9bee8e88867b8`
and `grading_json_bytes` 26981 — **re-hashed here from
`/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json`: identical, and the
byte count matches.**

**When it entered.** The witness's first and only commit is **`353925c7` — the
grade commit itself**, alongside `RESULTS.md`. **It did not enter after the
grade.**

**The gap that remains, stated exactly.** The comparator writes no sha into its
own output (`RESULTS.md` D-5, self-disclosed, and confirmed here: the grading
JSON's top-level keys are `written, dataset, pred_dir, plant_control,
realisability_source, n_test_predicted, n_test_scored,
n_test_dropped_nonfinite_bRANS, n_train, grades_verdict, note, models,
baselines, truth_viol_frac_test` — **no comparator field of any kind**). The
witness's own `written_utc` is **2026-08-24T16:07:25Z**, while the grading JSON's
`written` field and disk mtime are **15:55:27Z / 15:55:31.268Z**. **The
comparator's identity was therefore stamped 11 min 58 s after the artefact it
witnesses was produced**, by re-hashing a file rather than by the producing
process recording itself.

**Is that the pass-2 Wu2018 class? NO — it is a narrower and different
weakness.** Pass 2 §5's finding was that the pre-registration's **first commit
was the results commit**, so nothing witnessed that the prereg predated compute.
Here the prereg has its own commit **18 h 49 m before the grade** and **3 m 20 s
before the first compute artefact**, the grading path was fixed **by sha256
inside the frozen file**, and the driver that ran on the node hashes to that
frozen value (§36). The freeze witness is about as strong as this lab has
produced. The gap is only that **one artefact does not self-witness**.

**And the residual risk that a retrospective re-hash cannot close by itself —
an edit-run-restore between 15:55:27Z and 16:07:25Z — is closed by evidence
outside the witness:** `score_gpu_ling.py`'s mtime on disk is
**2026-08-23 21:14:05.034Z**, **18 h 41 m before the grading run**, and any
edit-then-restore would have moved it; and the path has **exactly one commit in
its history**, with disk blob id == HEAD blob id == `11f93da6` blob id. **So the
comparator that produced the NOT A RESULT is established as the frozen one — by
mtime and commit history, not by the witness alone.** The witness's real value is
that it makes the grading JSON's *content* pinnable at all, which nothing else
did. **Neutral finding; no re-grade; the standing repair D-5 already names is the
right one — a future comparator writes its own hash into its output.**

### 45. Cost calibration (rule 12) — present, complete, and C-19's correction audited

**C-16 is the row of record and it carries every limb rule 12 requires:**
predicted (12–52 GPU-h registered, cap 60, plus the in-run P0 projection 10.99),
actual (**10.7054 GPU-h**, cited to `out/spend.json`, **= $8.62 derived** at the
recorded rate with the provenance label attached), gross-vs-cleaned stated
(*"= gross … no solver-row stall rule applies"* — correct: the 3600-s stall rule
is a solver-row rule and a 5.4-hour GPU stage is hours-long by design), **ratio**
(0.974 and 0.892, both re-derived above), **attribution** (the 5–20× throughput
assumption against 42–80× measured, with the two cancelling errors inside the
projection named individually — ARM-B's mini-batch trials at **4.2×** and the MLP
at **0.52×**, both re-derivable from `spend.json` against the P0 rate), and
**waste separately named and excluded from the ratio** (§43).

**C-19, closure's own correction to C-16, is itself sound.** It states that C-16
left the post-sync idle "unmeasured", that Sanaa reported the stop **without a
clock**, and that the waste window therefore **ends at the last verified idle
read, 15:56:45Z**, with the 15:56:45Z → stop interval **"absent from the record —
neither measured nor estimated."** C-16's figures are explicitly unchanged.
**Audited: correct, and the honest direction.** The correction *narrows* a claim
rather than widening it, it names an absence instead of estimating into it, and
the closing point it uses is a real one — the last artefact touched on this box
in that window. `GPU_CAPABILITY_STATE.md` §10 carries the same reading in its
own table. **The two rows are consistent and neither over-claims.**

**Which row's numbers this pass grades:** C-16's, as corrected by C-19. The
correction moves no figure; it bounds one window's open end.

### 46. Verdict

**AUDIT: SOUND WITH DISCLOSED DEVIATIONS** (CANDIDATE — the verification
supervisor's own read governs).

| target | verdict as reported | AUDIT (CANDIDATE) |
|---|---|---|
| **Freeze order** | prereg committed alone before compute | **SOUND, and the strongest form on this lab's record** — one file, 509 insertions, one commit ever; first gate artefact 200 s later; the run's own `run_window.json` names the commit and sha; the node's driver copy hashes to the frozen F.4 value |
| **G0** planted zero | PASS | **SOUND** — measured on disk twice, on two machines, by two programs, bit-identical; `rel_err` 1.6e-14 against a 1e-9 tolerance; the refusal path writes no JSON, so every published number is downstream of a passed control |
| **G1** ARM-A a-priori | NOT A RESULT | **SOUND** — re-derived 0/8, 0/8, 0/8 by this lane's own arithmetic; the branch that fired is the frozen file's own registered branch; not vacuous (ARM-B clears the same 6-of-8 bar at 7/8 in the same run) |
| **G2** invariance embedding | GATE FAIL | **SOUND** — TBNN pooled 3.896e7 vs MLP 0.360359, re-derived; the direction of the comparison is not close |
| **G3** realisability | NOT A RESULT, both TBNN models | **SOUND, and the gate is demonstrably passable** — thresholds recomputed from the frozen wording (2.3741 %, 1.632993); every seed of both models fails both clauses; the control MLP clears both on all five seeds. **One standards hazard named**: the SST reference field's own `max ‖b‖_F` = 3.4819 exceeds the 1.633 norm bound (§38) |
| **thresholds after first compute** | none moved | **SOUND, verified by history, not by assertion** — the frozen file has one commit and no addendum; `RESULTS.md` carries dated disclosures that alter nothing |
| **cost basis** | $0.8048/GPU-h, published price list | **DISCLOSED DEVIATION from rule 12's "priced from the console"** — a documented feed with URL, JSON path, rateCode and retrieval stamp; labelled as not-a-console-read at five surfaces; §7's "NOT DONE" row left standing. **The dropped draft §14, which demanded the console read, is not flagged (§36, §42)** |
| **below-floor spend and waste** | 10.7054 vs 12–52; waste 7.88 GPU-h | **SOUND** — both re-derived; below-floor carried on three surfaces; waste separately named and arithmetically excluded from the ratio |
| **instance stopped** | STOPPED by Sanaa | **OWNER-REPORTED, correctly labelled** — no clock, no AWS CLI on this box; this lane's probe with a positive control corroborates unreachability but cannot verify instance state (§43) |
| **lesson citations in `RESULTS.md`** | (not claimed) | **DEFECT — two dangling citations, L-264 and L-265, pointing at another team's lessons (§40).** Confined to the grading record; every back-reference is correct; **no verdict moves** |
| **comparator witness** | repaired in the record (D-5) | **SOUND on the identity question, with the timing gap named** — all four sha256 values re-derived and agreeing; entered in the grade commit, not after it; the retrospective-hash risk closed by mtime and single-commit history rather than by the witness (§44) |

**The verdict `NOT A RESULT` is the frozen comparator's own output under the
registered gates, and this lane reproduced it independently.** It is not a
post-hoc reading, it is not a softened `GATE FAIL`, and it is the anti-tuned
direction: **the lab's first GPU run, costing $8.62 of a resource it had waited
weeks to obtain, returned nothing for the ladder** — and the record says so in
the first line of the file, then spends five sections explaining why the
findings underneath it are still worth having.

### 47. What this lane could NOT establish, named plainly

- **The F.5(1) refusal proof.** The frozen file states that a first
  implementation of the G0a back-solve *"refused live with exit 2, proving the
  refusal path (measured 9.3e-9)"*. **No artefact of that refusal survives** —
  no log, no `REFUSED` status, no captured stdout anywhere under
  `/home/ubuntu/closure-data/tbnn_gpu/`. The refusal path is verified as
  *source* (§39) and its structural consequence is verified (a refusal writes no
  JSON, so the JSON's existence proves the passing branch ran), but **the claim
  that it was once exercised live is transcribed prose.** Same class as pass 6
  §28's A1 mutation proof.
- **That the AWS instance is stopped.** Owner-reported without a clock; this box
  has no AWS CLI and cannot read the instance state, the shutdown-behaviour
  attribute or any billing figure. The probe in §43 shows unreachability, not
  state.
- **The $0.8048 feed value.** Recorded with URL, JSON path and retrieval stamp
  by a closure lane; **not re-fetched by this lane** (no AWS CLI, and rule 8
  governs what leaves the box). Taken as recorded.
- **The closure supervisor's own §3 personal reads.** `RESULTS.md:11` attests
  the supervisor *"graded personally"* and D-4 attests every figure was re-read
  by the supervisor from the primary artefacts rather than from a lane relay. A
  personal read leaves no artefact by construction; **taken as attested, not
  verified.** *(This lane's independent re-derivation of every number in §1 and
  §2 is, however, positive corroboration that whoever wrote them read the
  primary artefacts: they all reproduce.)*
- **The pre-launch idle.** Sanaa launched `gpu1` before 21:20Z on 2026-08-23 and
  the launch time is not on this box. `RESULTS.md` D-2 and C-16 both state it as
  unmeasured; this lane can add only that the earliest file synced from the node,
  `node_root/pip_install.log`, is dated **21:07:08.310Z**, so the instance was
  alive at least **14 min 21 s** before the run window opened. **That is a lower
  bound on the pre-launch idle, not a measurement of it**, and it is offered as
  such.
- **Nothing was re-executed.** No closure comparator, no driver, no GPU. Every
  gate above was re-derived by independent code over the values closure's
  instruments wrote to disk, plus source reads of the driver and comparator and
  primary reads of `../train_log.json` and the six `status_*.json`. That tests
  the grading arithmetic, the thresholds, the control records and the falsifier
  logic. It does **not** test the training front of `train_gpu_ling.py` or the
  prediction files themselves — the `pred_*.npz` arrays were not re-scored, so
  the per-case `b_rms` values are re-derived *from* the comparator's per-seed
  output, not *from* the raw predictions.

**Cost of this pass:** zero solver core-minutes, **zero GPU-hours** — nothing was
launched, and no GPU instance was contacted beyond one unreachable SSH probe.
Two Python steps were instrumented with `/usr/bin/time` and measured **0.02 CPU-s
combined ≈ 0.0003 core-minutes**; the remainder — `git` plumbing, hashing, a
handful of sub-second `python3 -c` reads and the SSH probe pair — was not
instrumented and is individually sub-second, bounding the pass **well under
0.1 core-minutes** against this lane's own pre-stated prediction of **≤ 1.0
core-minute**. Direction: over-predicted, the same way pass 6 was (C-20, ≈ 0.04×).
Nothing under `cases/RANS_LES_closure_models/` or `/home/ubuntu/closure-data/`
was written.

---

## Audit pass 7 — 2026-08-24, verification LANE (CANDIDATE, not the supervisor's own read)

**Lines whose number changed above this section: 0.** This section is appended at
the foot of an append-only file. The base for this edit was taken from
`git show HEAD:docs/CROSS_TEAM_GATE_AUDIT.md` (L-253), never from the worktree,
and the base was asserted to be a **strict byte prefix** of the file written
(`cmp` rc=0 over 129,151 B, 1,703 lines), so nothing above this line moved.

**Two disclosures about where this section sits, made because a reader will
notice both.** (i) **It lands after pass 8, not before it.** This pass was
commissioned as pass 7 and drafted as pass 7; while it was being drafted a peer
lane landed **pass 8** (the Ling2016 TBNN GPU arm, `9573db65`,
2026-08-24T16:27:11Z), taking §35–§47. Rule 11's discipline — numbers are
assigned at commit, from the tail — is applied here to sections rather than to
the pass label: this pass keeps the number its brief gave it and its **sections
continue from the actual tail, §48**. The file is therefore append-ordered, not
pass-ordered. (ii) **The worktree copy of this file was stale when this section
was written** — 1,110 lines against HEAD's 1,703 — and was verified to be a
strict byte prefix of the HEAD blob before being replaced, so no peer's text was
overwritten and nothing unique was lost (§60 records the same pattern on both
audit targets).

**This pass was run by a `lab-lane`, not by the verification supervisor
personally.** `SUPERVISION_CHARTER.md` §3 is explicit that a relayed check is a
summary and not a check, so **every finding below is CANDIDATE until the
verification supervisor re-derives it.** Each finding names the artifact it was
read from; no figure is quoted from the auditee's prose without being re-derived
beside it. The lane was **read-only toward dafoam's territory** throughout:
nothing under `cases/dafoam/`, `docs/dafoam/` or
`/home/ubuntu/certonomous-runs/` was written, no dafoam comparator was
re-executed, and every number below was re-derived with this lane's **own** code
or arithmetic over the values the instruments wrote to disk.

**Two targets.**

1. **W4 stage O2 re-buy** — the offline `scipy` exact-LU of the already-paid-for
   NASA-hump `dRdWTPC`. Pre-registration frozen `8d48fd46`
   (2026-08-23T21:03:46Z), RESULTS landed by the supervisor at `5a93f6ee`
   (2026-08-24T16:01:21Z, close-out §12), records `b69ac6ec` (L-264…L-266,
   N-D27, D488–D489), ledger row **C-15**. Reported: §3 decision **`PENDING`**,
   `spilu` **4 of 4** singular measured, `splu` killed at a 20 GiB cgroup cap at
   900 s, **15.00 core-min** measured against **35.0** registered. This is the
   successor to the item audited in **pass 4** (§10–§16).
2. **B3 decomposition** — `decomposition_np4/RESULTS.md` and its dated addendum
   (`bb5088c4`), the peak-RSS item (prereg `d062aace` + three addenda, RESULTS
   `b5ff25d7`), board `52c26ec1`. Reported: **M0 PASS**, **M4 falsified in the
   registered direction** (np=1 the larger), L-261.

### 48. Target 1 — comparator freeze (§2b, §2d): RE-DERIVED, AND IT HOLDS WITHOUT A SINGLE AMENDMENT

| check | finding |
|---|---|
| Prereg committed **alone**, before any compute | **YES.** `8d48fd46cb7a0e037d8871e63d241f11c2861153`, `2026-08-23T21:03:46+00:00`, **one file, 587 insertions, nothing else in the commit.** |
| Frozen blob **is** the blob the record claims | **YES, hashed by this lane.** Blob `47e2988efca221401f0e3b25b463a0aa155e0774`, sha256 `5321631691044757471bcf36522350f94e6767024e08cf8b6222aa41de5b2322`; the on-disk file re-hashes to the **same** sha256 today. Both values equal what `W4_O2_REBUY_RESULTS.md:7-9` claims. |
| Gates/thresholds/caps byte-unmoved since the freeze | **YES, and trivially total.** The prereg path has **exactly one commit** in its entire history. Freeze blob == HEAD blob == disk, 587 lines all three ways. There is **no amendment and no addendum to compare a prefix against** — nothing in §3, §4, §5, §7 or §9 has moved by a byte. |
| First compute **after** the freeze | **YES, by 507 s to the container.** Freeze 21:03:46Z; gate poll attempt 1 at **21:07:02Z** (203 s later, and it started **no container**); container `.start` **21:12:13Z**. The frozen §9's own reading, taken at **20:58:23Z**, records the gate **NOT MET** at 17.51 GiB — the document discloses that the box was busy at the moment of the freeze rather than smoothing it over. |
| The instrument that ran **is** the frozen instrument | **YES, re-derived today.** `analyze_dump3.py` md5 **`f85140f675bcc287f6e4aaf01276c0e4`**, 33 lines, mtime **2026-08-02 06:18:15Z** — **19 days before the freeze**, so *"already exists and is not edited"* is a checked claim. `pmat.dat` **406,022,696 B**, `rhs.dat` **4,137,928 B**, both mtime 2026-08-23 19:56:17Z (the parent item's dump, unchanged). All four equal the frozen §8 values. |
| The one disclosed deviation (§8a: the registered inline command transcribed to `run_o2_rebuy.sh`) | **VERIFIED BY BYTE COMPARISON, NOT ACCEPTED.** The frozen §6 `bash` block is 42 lines; lines 5–46 of `run_o2_rebuy.sh` (md5 `4beac779f4d1b18400fa5d71478f9bdf`) are **byte-identical to it** (`diff` rc=0). The file adds only a shebang, three comment lines, `echo LOGPATH=` and `exit $rc`, exactly as §8a says. **No token of the registered command was changed** — the `timeout 2700`, the `--cpus=1 --memory=20g --memory-swap=20g --oom-score-adj=500`, the mounts, `python -u` and the `PIPESTATUS[0]` read are all the frozen bytes. |
| The RESULTS' own provenance claim (§12: *"committed as found on disk, byte-for-byte above this section"*) | **VERIFIED.** The lane's pre-commit copy still on disk is **428 lines / 28,292 B**, mtime 2026-08-23 21:31:07Z; the committed blob is 466 lines. `cmp` of the disk copy against the **first 28,292 bytes** of the committed blob: **rc=0, strict byte prefix.** The supervisor's ~18-hour-later commit added §12 and touched nothing above it. |

**Sequence of record, all from artifacts:** freeze `8d48fd46` 21:03:46Z → gate
refusal 21:07:02Z (no container) → container 21:12:13Z → kill/`.end` 21:27:13Z →
lane's record written 21:31:07Z → supervisor's commit `5a93f6ee` 2026-08-24
16:01:21Z → records `b69ac6ec` 16:03:03Z.

### 49. Target 1 — could each graded row have failed, and the tautology hunt

**No tautological row was found, and the three rows that carried a measured
value are all graded against the auditee.**

**O2R-P4 (`spilu` singular at exactly 4 of 4) — HIT, and it could plainly have
gone the other way.** This lane read the frozen instrument. `analyze_dump3.py`'s
`spilu` loop is a `try/except` whose **success** branch prints a rich row
(`nnz(L+U)=…  info=…  matvecs=…  final rel res=…`) and whose failure branch
prints the **exception text**. The graded quantity is therefore not a boolean an
optimist could read either way: it is the string `Factor is exactly singular`,
which distinguishes a zero pivot from a memory failure, a convergence failure or
any other exception. **The same reader printed the success form three times on
CBFS** — see §50. Measured on the hump, from
`logs/o2_rebuy_hump_lu_20260823T211207Z.log:4-7`: four rows, every one
`FAILED: Factor is exactly singular`, at `drop_tol` 1e-2/1e-3/1e-4/1e-5 and
`fill_factor` 3/5/5/10.

**The identity line is a real check and this lane re-read both of its
citations.** `:1` prints `n=517240 nnz=33662810 ||b||=1.094138002900e+00`.
`W4_M1M2_RESULTS.md:117` carries `nnz(A)` = **33,662,810** and `:115` carries
`‖b‖₂` = **`1.094138002900e+00`** — so the operator this factorization was run
on is the one the parent item verified, and the reader that says so is the
frozen script rather than the record's prose.

**O2R-P5 (wall 1500–2700 s **and** the run completes) — MISS on both clauses,
reported as a miss.** `.start` `2026-08-23T21:12:13Z`, `.end`
`2026-08-23T21:27:13Z`, both read by this lane: **900 s**, and rc **137**.

**O2R-P6 (peak 8.0–20.0 GiB) — MISS (high), right-censored, and the censoring is
stated rather than hidden.** `CGROUP_PEAK_BYTES=21474836480` = **20 × 1024³ to
the byte**. A cgroup high-water cannot exceed the limit that killed the process,
so this is a **lower bound** on what the exact LU wanted, and the record says so
in exactly those terms. The frozen §7b and §7c registered this mapping — kill ⇒
MISS (high), right-censored, not a void — **before** the run.

**C-P1R (the exact LU exceeds 25.0 core-min) — MISS, and the freeze made it a
harder test on purpose.** The frozen §4b registers `--cpus=1` billing, under
which the hypothesis needs **more than 25 wall-minutes** where the original
C-P1's `--cpus=4` basis would have needed 6.25. Registering the harder billing
is anti-tuning and it is on the record before the spend.

**The registered `rc` semantics are the cleanest anti-tuning artifact in the
item.** The frozen §6 fixes `0` = completion, `124` = the `timeout` fired,
`137` = the cgroup OOM kill, *"anything else is triaged before grading and is a
finding, not a number to absorb"* — and it names the `tee`/`PIPESTATUS[0]`
footgun in the same paragraph. The observed `rc=137` maps onto a branch written
before the answer existed.

### 50. Target 1 — controls: one fired as a **refusal with a measured value**, one is asserted-only, and the rule-3 plant was declined in advance

| control | executed? | measured value, and where it lives |
|---|---|---|
| **The registered launch gate (§9)** | **FIRED, AS A REFUSAL, WITH A POSITIVE ARTIFACT ON DISK** | `logs/o2_rebuy_poller.out`, attempt 1 at **21:07:02Z**: `GATE free_cores=6 memavail_gib=19.77` → `GATE NOT MET -- BLOCKED, not launched`, `attempt 1 returned rc=3`, **no container started, 0.00 core-min**. Attempt 2 at 21:12:07Z read `free_cores=9 memavail_gib=26.84` and launched. This is stronger than the parent item's guard evidence audited at §12 of pass 4: there the refusal path was *wired but did not fire*; here the refusal **fired and left a number**. |
| **The four §8 void assertions** | **RAN AND PASSED, on both attempts, with their values printed** | `o2_rebuy_poller.out` prints the md5, both dump sizes and the full image ID on **each** attempt, all equal to the frozen values; this lane re-derived all four from disk today. **But they have never been shown able to refuse** — no run exists in which any of them differed, and no mutation was staged. They are a checked identity, not a demonstrated refusal. |
| **A rule-3 plant into the hump operator** | **NOT TAKEN, AND DECLINED IN THE FROZEN FILE BEFORE THE RUN** | The frozen §5a says, verbatim, *"No perturbation is planted into the hump matrix and this file does not claim one is"*, prices the alternative (re-running `analyze_dump3.py` on the CBFS dump, ≈ 10.5 core-min at `--cpus=1`) and declines it as a judgement recorded before the run. **Pass 4 §12's carried-forward recommendation — copy `pmat.dat`, zero one row, confirm `analyze_dump.py` reports `zero rows=1` — was therefore NOT taken.** It was refused in advance and in writing, which is the honest form of not doing it, but the recommendation stands unspent. |

**What this lane can add, unprompted, and it partly closes the rule-3 gap the
record leaves open.** `analyze_dump3.py` has mtime **2026-08-02 06:18:15Z** and
md5 `f85140f6…` — the value frozen at `c8254a4a` §5 — i.e. it is byte-unchanged
since 29 minutes before `W4-cbfs-reordering/analysis_final.log` was written at
**06:47:57Z**. That log, read by this lane, carries at `:10-12` **three
completed `splu` rows**:

| `diag_pivot_thresh` | `nnz(L+U)` | `‖Ax−b‖/‖b‖` |
|---|---|---|
| 0 | 322,328,834 | 2.3769e-10 |
| 0.1 | 362,261,983 | 6.4063e-12 |
| 1 | 389,944,580 | 2.5355e-12 |

**So the hump's "zero completed `splu`" is a zero from a reader that is
demonstrably able to print a non-zero `splu` completion** — same script, same
box, a different operator. That is *not* the plant rule 3 asks for (nothing was
planted into **this** matrix, and the demonstration is 21 days old on a
different case), but it is a materially stronger position than the record claims
for itself, and it is offered so the next reader is not left with an
uncontrolled zero. The remaining uncontrolled channel is unchanged: **no reader
in this chain has been shown able to see a defect planted in the hump
operator.**

### 51. Target 1 — **DEFECT FOUND**: `O2R-P2` is graded `PENDING` against a frozen rule that registered `MISS`

The frozen §5 row for **O2R-P2** reads, in the blob whose sha256 this lane
re-derived as equal to `8d48fd46`'s:

> **O2R-P2** | number of the **3** `diag_pivot_thresh` values (0, 0.1, 1) at
> which `splu` **completes** | **exactly 3 of 3** | HIT iff exactly 3; **any
> other count is a MISS** and is still graded under §3

The measured count is **0**, and it is observable on disk: the `splu` section
header printed at `:9` and **no row followed it** before `245 Killed` at `:10`.
`W4_O2_REBUY_RESULTS.md:136` grades that row **`PENDING`**, and §4a argues the
case at length — that completion is measured against termination, that a killed
threshold "was never asked the question to the end", and that calling it MISS
"would be wrong".

**On this lane's reading that grade is a post-compute departure from a frozen
HIT/MISS rule, and it is the one thing in this item that rule 1 forbids.** Four
reasons, each checkable:

1. **The frozen rule admits no third outcome for this row.** It says *any other
   count is a MISS*. Zero is another count.
2. **The freeze author demonstrably knew how to register a `PENDING` branch and
   chose not to for this row.** In the **same table**, O2R-P3 reads *"HIT iff
   inside band; **PENDING iff zero `splu` completed**"* and O2R-P6 reads *"An
   `UNAVAILABLE` cgroup read is **PENDING, not MISS**"*. Two rows carry an
   explicit `PENDING` branch; O2R-P2 carries an explicit *"any other count is a
   MISS"*. The asymmetry is deliberate and it is inside the frozen bytes.
3. **The argument that changes the grade was constructed after the answer
   existed.** §2d closes gates, thresholds and labels at first compute. §4a is a
   post-compute re-reading of what O2R-P2's quantity means, and it changes that
   row's label. Whatever its merits as reasoning, the freeze is the document's
   entire evidentiary content and this row's freeze says MISS.
4. **§3's `PENDING` does not reach it.** §4a's load-bearing sentence is that
   *"§3, inherited verbatim, routes a stop with zero completed `splu` to
   `PENDING`"*. §3 grades the **decision** — which of D-SINGULAR /
   D-ILLCOND-CATASTROPHIC / D-MERELY-SLOW / D-UNREGISTERED-CLASS applies. §5's
   table grades **predictions**. They are different objects with different
   registered rules, and the §3 row cannot supply a branch the §5 row was
   written without.

**Severity, stated so it is not read wider than it is.** **No headline verdict
moves.** The §3 decision is `PENDING` either way (§52); `spilu` 4-of-4 stands;
the `splu` measurement's `NOT A RESULT` stands; O2R-P5, O2R-P6 and C-P1R stay
MISSes. The direction of the error is mild self-flattery on one prediction row —
the opposite direction from the parent item's §5 row 3 defect found at pass 4
§14, which cost that lane its own headline. **Recommended remedy, dafoam's to
accept or refuse and not this lane's to impose:** a dated addendum to
`W4_O2_REBUY_RESULTS.md` (appended at the foot, §4/§4a struck not rewritten, per
rule 6) regrading **O2R-P2 = MISS** on the frozen arithmetic, keeping §4a's
reasoning verbatim as the *interpretation* of that MISS — the distinction
between "the operator failed" and "the item was stopped" is real and worth
keeping; it just is not a licence to move the label.

**By contrast, O2R-P1 and O2R-P3's `PENDING` grades are SOUND.** O2R-P3's is
registered explicitly. O2R-P1 names *"`nnz(L+U)` at the **highest completed**
threshold"* — a quantity that is **undefined**, not zero, when no threshold
completed; nothing was printed and nothing was read. That is the display/queue
sense. The freeze's failure to register a `PENDING` branch for O2R-P1 is a
small gap in the freeze, not a softening in the grade.

**Not caught upstream.** The supervisor's close-out §12 enumerates its personal
re-verification as O2R-P4 HIT, O2R-P5 MISS, O2R-P6 MISS, C-P1R MISS and the §3
`PENDING`. **O2R-P1, O2R-P2 and O2R-P3 are not mentioned.** The check that was
done is described in enough detail to be believed; it simply did not reach this
row.

### 52. Target 1 — the §3 decision's `PENDING` IS a queue state, not a softened `GATE FAIL` or `NOT A RESULT`. AUDIT: SOUND

This is the question the brief asks a position on, and this lane takes one.

**Position: sound, on the charter text.** `VERIFICATION_CHARTER.md` §9 fixes the
display sense in one sentence — *"A row whose act has not run prints PENDING and
is never filled in from a neighbouring run that happens to be close."* The test
the charter gives is therefore **whether the act that decides the row ran**, not
whether any container started. Applied here:

1. **The act that decides §3 is a completed `splu`, and it did not run to an
   answer.** All four §3 verdicts require `splu` to complete at ≥ 1 threshold
   (D-SINGULAR additionally admits a raise at all three, or a `zero rows/cols` >
   0 finding — and the latter half was already closed at O1 with 0/0/0, graded
   HIT). Zero completed. The registered input to the decision does not exist.
2. **The `PENDING` row was pre-registered with this exact condition, twice.**
   `c8254a4a` §3's verdict table carries *"stage O2 not launched, **or launched
   and stopped by the budget ceiling or the memory guard with zero completed
   `splu` factorizations**"*, and §3's partial-but-decisive clause repeats it.
   That text was re-frozen verbatim inside `8d48fd46` §3, in the blob this lane
   re-hashed. **The phrase "launched and stopped" is in the freeze**: this is
   not the "never launched" branch being stretched to cover an executed run — the
   executed-and-stopped case is the branch's own registered wording. `8d48fd46`
   §3 note 2 also disposes of the only wrinkle (the stop was a cgroup, not the
   watcher script) with *"a stop is a stop; the row grades on how many `splu`
   factorizations completed"*.
3. **Nothing that had a measured value was labelled `PENDING`.** The run's own
   measurement is graded **`NOT A RESULT`** — the correct label for an executed
   run stopped by its cap — and it is printed in the §1 verdict table beside the
   `PENDING`. The three predictions with measured values (O2R-P5, O2R-P6,
   C-P1R) are all **MISS**. The item did not spend `PENDING` on any number it
   actually had. (The one exception is O2R-P2, and that is §51.)
4. **The consequence that a softened verdict would have unlocked did not
   fire.** §3's carried sentence *"if M1 returns singular or catastrophically
   ill-conditioned, M4 and M5 are not bought"* is explicitly **not** claimed as
   fired; the record says M4/M5 stay unbought because **M1 has not decided**, a
   distinct state, and refuses to collapse the two. A lane softening a failure
   would have had the opposite incentive.

**Where the boundary actually sits, stated so the next auditor inherits it
rather than re-deriving it.** `PENDING` is legitimate for a **decision** whose
registered input was never produced, even when compute was spent trying — the
run's *own* label in that case is `NOT A RESULT`, and both appear. It is **not**
legitimate for a **prediction whose quantity is observable and was observed**,
which is precisely the O2R-P2 defect. Pass 4 §13 ruled the parent item's M1
`PENDING` a queue state on the "no run exists" limb; this pass extends that
ruling to the harder case — **a run that existed, was stopped, and still leaves
its decision's input non-existent** — and the extension is what the frozen
branch's own wording anticipated.

### 53. Target 1 — cost calibration (rule 12): present, complete and honest, including the part that works against the item

`W4_O2_REBUY_RESULTS.md` §5/§5a and ledger row **C-15** carry the comparison the
frozen §4c registered *before* the spend:

| field | value | this lane's check |
|---|---|---|
| predicted | **35.0 core-min** (band 25–45; ceiling **50.0**; wired stop 45.0) | in the frozen §4, byte-unmoved (§48) |
| actual | **15.00 core-min** | **re-derived**: `.start` 21:12:13Z → `.end` 21:27:13Z = 900 s × 1 cpu ÷ 60 = 15.00 |
| ratio | **0.43×** | 15.00 ÷ 35.00 = 0.4286 → 0.43 |
| dollars | predicted **\$0.02993**, actual **\$0.01283** | both labelled **DERIVED** at \$0.0513/core-h, **reported-by-owner, not measured** — correct under `COMPUTE_BUDGET_CHARTER.md` §5 |
| waste | **0.00, named** | every core-minute produced a graded measurement (the 4-of-4 singularity and the ≥ 20.0 GiB bound); the gate refusal is charged **0.00** and is correct — no ranks were held |
| gap attribution | contention 0.00, waste 0.00, misprediction 0.00, **truncation by the registered cap −20.00** | the frozen §4c required the three registered causes to sum to the gap *"or the shortfall is named"*. They sum to zero against a −20.00 gap, so the **fourth cause is written into the row** rather than smuggled into "misprediction" |

**The row's best sentence is the one that refuses the flattering reading**:
*"A cost that came in at 0.43× because the run was killed is not an estimate
that was too high."* C-15 repeats it and adds that the 35.0 duration estimate
was **never tested**. **Nothing is owed on this question**; this is the form the
directive asks for.

Two small honest notes, neither of which is a defect. The **wired budget stop
(`timeout 2700`) was never exercised** — the memory stop fired first at 900 s —
so this item has a proven memory stop and an unproven budget stop, which the
record itself states. And the mid-run `docker stats` reading of **100.05 %** cpu
that supports "contention 0.00" is labelled in the record as *"an observation,
not an artifact"*; this lane could not verify it and it is the only figure in
the ledger row with no file behind it. Nothing rests on it.

### 54. Target 2 — B3: the freeze and its three addenda, verified by byte comparison rather than by their own assertions

| check | finding |
|---|---|
| Peak-RSS prereg committed **alone**, before compute | **YES.** `d062aace`, `2026-08-23T19:51:22Z`. Its §0 states the freeze condition and how it was checked (the run root `ls` failing, with the `date -u` beside it) — rule 2's requirement met in the required form. |
| Frozen instruments == the instruments that ran | **YES, re-hashed by this lane from the committed blobs.** `analyse_peak_rss.py` sha256 **`c4db08fcf7a3e5d23327943d9093feb3b5983ec655083f50a103e30f9c6951eb`** and `b3_rss_watch.sh` **`e9db593ee5932a1b9bb16bf40560ddf38d1836ad34c4a7c281217d3d463dac29`**: `d062aace` blob == disk for both, and **each has exactly one commit in its history** — never edited since the freeze. |
| Gates/bands/caps byte-unmoved across three addenda | **YES, PROVEN BY `cmp`, NOT BY THE ASSERTIONS.** The freeze blob is **32,392 B / 484 lines**; the Addendum-1 state is **38,194 B / 601 lines**; HEAD is **42,873 B / 688 lines**. `cmp` of the freeze blob against the **first 32,392 bytes** of HEAD: **rc=0**. `cmp` of the Addendum-1 blob against the first 38,194 bytes: **rc=0**. So every band in §5.2, the M0 digit table in §5.4, the 12 GiB launch gate, the 4 GiB mid-run floor, the 182.0 core-min ceiling and the instrument hashes are **exactly as frozen**, and all three *"lines whose number changed above this section: 0"* assertions are **VERIFIED, not accepted**. |
| The `§2d.1` repair exception invoked at Addendum 3 | **LEGAL, and its four conditions are individually checkable.** (1) demonstrable error: both arms died at `prob.setup(mode="rev")` with `PermissionError: [Errno 13] … 'reports'`, **before any solver work**; (2) an instrument independent of the hypothesis: the paired `m755`/`m777` `mkdir` control, **which this lane found physically on disk** — `triage/m777/reports` **exists** (mode 777 parent), `triage/m755/` is **empty** (mode 755 parent), both mtime 19:59; (3) disclosed in Addenda 1–2 with the instrument named; (4) the pre-repair state recorded in full. **The repair sits upstream of the grading path**: no graded number ever existed, because the frozen grader **refused (exit 2)** on 3 samples against a registered minimum of 30. |
| Addendum 2 (the 775-not-755 correction) | **A dated correction in the required form** — quote-and-strike of the struck line, corrected table, and the mechanism (`o+w` absent in both 775 and 755; the container is uid/gid 1002 against an `ubuntu:ubuntu` 1000 tree, so the "other" bits govern) explained rather than re-asserted. It corrects a **prose** figure, not a graded number: attempt 1 produced none. |
| `decomposition_np4/RESULTS.md`'s dated addendum (`bb5088c4`) | **APPEND-ONLY, PROVEN.** The pre-addendum blob (`804c3fd8`) is **17,678 B / 271 lines** and is a **strict byte prefix** of the 372-line file at HEAD (`cmp` rc=0). Its opening asserts it alters no gate, threshold, band, cap or label, and by byte comparison it does not. |
| The np4 pre-registration's own freeze | **BEFORE COMPUTE, BUT NOT COMMITTED ALONE.** `b8ba5f8f`, 2026-08-21T17:55:29Z, carried **seven files** (a "Phase 2C checkpoint"). Freeze-before-compute still holds and this lane checked it on mtimes rather than on the message: the earliest np4 solver log is `logs/D_serial.log` at **2026-08-21 19:46:40Z**, **111 minutes after** the commit. Named because the pass-4/pass-6 standard is a single-file freeze commit and this one is not; nothing in the co-committed files is an artifact of this item's compute. |

### 55. Target 2 — could each row have failed: **three of seven did**, and M0 is not tautological

**M3a, M3b and M4 are GATE FAIL on the frozen bands.** A pass whose gates all
pass invites the §2a question; this one answers it by failing.

**M4 is the item's registered falsifiable claim and it was falsified in the
direction the freeze named in advance.** §5.2 registered *"if the serial LU is
the larger object, M4 fails and the 'np=1 is the arm at risk' reasoning of
`decomposition_np4/PREREGISTRATION.md:69` is vindicated a run too late"* — that
sentence is inside the 32,392-byte prefix proven unmoved at §54. This lane
**re-derived M4 from the watcher logs with its own parser**:

| instrument | np=4 (`D_simple2`) | np=1 (`D_serial`) | registered claim `np4 > np1` |
|---|---|---|---|
| cgroup `memory.peak` | 8,590,049,280 B = **8.000 GiB** | 11,954,151,424 B = **11.133 GiB** | **False**, by **3.133 GiB** |
| sampled tree RSS | 10,190,996 kB = **9.719 GiB** | 12,061,956 kB = **11.503 GiB** | **False**, by **1.784 GiB** |

**M0 is the row that could most easily have been a tautology and is not.** Three
independent reasons, all checked here:

1. **The archived digits are frozen inside the grader, and they are the real
   2026-08-21 printings.** `analyse_peak_rss.py:44-59` hard-codes `163`, `766`,
   `1.5279275989724403e-02`, `1.5279278602317540e-02`, the two `GRAD` tuples and
   the two iteration-0 residuals. This lane read the **original** logs in
   `/home/ubuntu/certonomous-runs/B3-decomposition-np4/logs/` and found
   `GRAD n=21000 norm=1.4557054356e-05 min=-4.694385e-07 max=1.915505e-06`,
   `Total iterations: 163`, and the D_simple2 counterparts at **766** — byte-for-byte
   the frozen constants. The grader was committed at 19:51:22Z, **51 minutes
   before** the first attempt-2 container. **The comparison is not circular.**
2. **The `D_simple2` arm regenerated its own coloring, so its iteration count
   was genuinely free to move.** `dRdWColoring_4.bin` mtime **2026-08-23
   21:05**, inside the arm's own window — this lane read the mtimes. The frozen
   §5.4 registered the innocent explanation *in advance* and refused it: a
   different count *"is an M0 failure, not a shrug"*, because the partitioner is
   identical here. **It reproduced at 766.** `D_serial`'s coloring, by contrast,
   is the carried-in file at **2026-08-21 16:43**, untouched — so the two arms'
   M0 passes carry different weight, exactly as the §2.4 asymmetry registered.
3. **The registered failure consequence is the strict one.** §5.4 fixes that an
   M0 failure turns **every band row** into `NOT A RESULT`, in the rule-5
   direction only (a gate may turn a PASS or GATE FAIL into NOT A RESULT, never
   the reverse). The grader exited **3** (a graded row is GATE FAIL), not 2 (a
   refusal) — so it graded rather than refused, which is itself a checkable fact
   about which path ran.

**M2b passed by 114,688 bytes and the record flags it rather than rounding it.**
This lane re-did the arithmetic: the 8.0 GiB band floor is **8,589,934,592 B**,
the arm measured **8,590,049,280 B**, margin **114,688 B = 112.0 KiB =
0.00134 %** of the floor. The band was **not** adjusted in either direction, and
the record states in terms that the row *"should not be relied on as evidence
that `D_simple2`'s peak is comfortably inside the registered range"*. That is the
correct handling of a near-tie.

**One disclosed censoring, and it is the item's own §9 that says so.** `M5`'s
memory clause (*`memory.peak` strictly below 12 GiB*) cannot distinguish "this
arm peaked at 11.13 GiB" from "this arm wanted more and the kernel reclaimed
cache under the cap". `D_serial` sat at **92.78 % of its 12 GiB cap with 0.867
GiB of headroom** (this lane's arithmetic). §9 states exactly this — *"these are
peaks under a 12 GiB cap, not unconstrained peaks … an unconstrained peak is not
derivable from 11.133 GiB and may be higher"* — and hands it on as a new
registration rather than absorbing it. **Disclosed limitation, not a defect**,
and it is the same corollary L-261 records.

### 56. Target 2 — controls fired with measured values, every one re-derived here by this lane's own parser

This lane wrote its **own** watcher-log parser (independent of
`analyse_peak_rss.py`, which was **not** executed) and re-derived every graded
quantity from `logs/D_serial_rss.log` and `logs/D_simple2_rss.log`:

| quantity | `D_serial` | `D_simple2` | agrees with `peak_rss.json` |
|---|---|---|---|
| samples | **581** | **157** | yes |
| max inter-sample gap | **3.0 s** (registered ≤ 5 s) | **3.0 s** | yes |
| cgroup `memory.peak` | **11,954,151,424 B = 11.133171 GiB** | **8,590,049,280 B = 8.000107 GiB** | **to the byte** |
| sampled tree-RSS max | **12,061,956 kB = 11.503178 GiB** | **10,190,996 kB = 9.718891 GiB** | yes |
| min host `MemAvailable` during the arm | **7,598,900 kB = 7.247 GiB** | 19,859,000 kB = 18.939 GiB | yes |
| ledger core-min | 1177 s × 1 ÷ 60 = **19.62** | 337 s × 4 ÷ 60 = **22.47** | yes |

| control | executed? | measured value, on disk |
|---|---|---|
| **Rule-3 planted control (§4.4)** | **YES, and this lane re-derived the read-back from the raw sampler log rather than from the verdict file** | `selftest/selftest_watch.log` final samples: `TREE_RSS_KB= 2105852` = **2.00833 GiB** and `MEM_PEAK_B= 2159976448` = **2.011584 GiB**, against a planted **2.00 GiB** and registered bands 2.00–2.60 / 2.00–3.50. `selftest/selftest_verdict.txt`: `PASS … utc=2026-08-23T20:43:16Z`, **80 s before the first graded arm**. The grader **refuses (exit 2)** without that file — a refusal demonstrated in the pre-registration itself against the not-yet-existing run root. |
| **The kill-trigger path (§3.1)** | **FIRED, WITH ITS SENTINEL STILL ON DISK** | `selftest/selftest_trigger.log`: driven against an unsatisfiable floor (`hard_floor_kib=32132604` = the box's whole `MemTotal`), it printed `ABORT reason=HOST_HARD_FLOOR` and **`KILL_ISSUED rc=0`** — and the sentinel **`selftest/.selftest_kill_fired` exists on disk today** (mtime 20:42). Pass 4 §12 had to record the W4 guard's equivalent sentinel as *no longer on disk*; **here both halves are re-verifiable**, and the second half is the one that proves the kill command ran rather than being scheduled. |
| **The frozen grader's own refusal path** | **FIRED ON ATTEMPT 1, WITH ITS MESSAGE PRESERVED** | Addendum 1 §A1.1 records `analyse_peak_rss: REFUSE: ./logs/D_serial_rss.log holds 3 samples, fewer than the registered minimum 30`, `exit=2`. **A comparator that refused rather than degraded, on a real failure, is the best evidence a refusal limb can leave**, and it is why no graded number ever existed for attempt 1. |
| **Attribution to a named container (§4.2, D-1)** | **YES** | Every number is read from `b3rss_D_serial` / `b3rss_D_simple2` by name → id → cgroup. The failure this repairs is on the record: a shared-box `docker stats` watcher once attributed **9.786 GiB** belonging to another lane's container. The record also names a peer container (`d460_psm`) that started **23 s after** the chain finished and therefore could not have entered these numbers. |
| **The age guard (completion clause 6)** | **YES, re-derived from mtimes by this lane** | `D_serial/cbfs_beta_grad.npy` **21:03:22.891Z** vs staged `D_serial/runScript.py` **20:42:13.576Z** (**+1269 s**); `D_simple2` **21:09:00.502Z** vs **20:42:14.684Z** (**+1606 s**). Both artefacts postdate the run that was allowed to produce them. |
| **Decomposition read back from each arm's own directory (§5.2)** | **YES** | `logs/D_serial_decomp.txt`: `numberOfSubdomains 1; method scotch; n (1 1 1)`, **0** `processor*` dirs. `logs/D_simple2_decomp.txt`: `numberOfSubdomains 4; method simple; n (4 1 1)`, **4** dirs. The §6a trap of the graded item — an arm that silently ran `scotch` and looked healthy — is closed by reading the file DAFoam itself wrote, not the launch command. |
| **The paired mode control behind the §2d.1 exception** | **YES, on disk** | `triage/m777/reports` exists; `triage/m755/` is empty. **One residual, named:** the control tested **755** against 777, while the mode that actually failed was **775** (Addendum 2). Addendum 2 bridges the gap by **mechanism** (`o+w` absent in both) rather than by measurement — no `m775` arm was ever run. The bridge is sound and it is disclosed; it is an argument where the other two rows are artifacts. |

### 57. Target 2 — the instrument-relation refutation, re-derived, with one arithmetic corroboration this lane adds

§5.2 of the frozen prereg asserted **`memory.peak` ≥ tree RSS *by
construction***. The RESULTS §4.1 reports it **refuted on both arms** and names
two candidate mechanisms without claiming either. This lane re-derived the gaps
from the raw sampler logs: `D_serial` tree RSS exceeds cgroup peak by
**+0.370 GiB**, `D_simple2` by **+1.719 GiB**. Both reproduce exactly.

**Corroboration this lane adds, and it narrows the candidate set for one arm.**
`D_serial`'s single solver process reached `VmHWM` **12,044,544 kB = 11.4866
GiB** — **0.354 GiB above the whole container's cgroup high-water of 11.133
GiB**. A single process cannot double-count pages against itself, so
mechanism 1 (tree RSS summing pages shared between ranks) is **arithmetically
excluded for `D_serial`**, exactly as §4.1 says, and mechanism 2 (resident pages
charged to a cgroup that faulted them in first — the plant container ran the
same image 80 s earlier) is the only one of the two left standing for that arm.
This is offered as support for the record's reasoning, not as a measurement of
the mechanism: **neither candidate was measured and this lane measured neither.**

**A second corroboration, which sharpens L-261 rather than contradicting it.**
L-261's binding half — *a sampled peak is a floor* — is right, and this
instrument's floor is a tight one: the **sum of per-pid kernel `VmHWM`** (a
kernel counter, not a sample) is **12,062,416 kB** against the 2 s sampler's
tree-RSS maximum of **12,061,956 kB** — the sampler lost **460 kB, 0.004 %**, on
`D_serial`, and **2,452 kB, 0.024 %**, on `D_simple2`. The 1.81× undersample
L-261 records is a property of the **5 s `docker stats`** figure it replaced, not
of this 2 s cgroup sampler. Both readings should travel together so the next
reader does not price a 2 s cgroup sampler as if it were the instrument that
missed by 1.81×.

### 58. Target 2 — verdict vocabulary, cost calibration, and two record-hygiene items owed

**Vocabulary is CLEAN across all three records.** A sweep of the emphasised
verdict cells at HEAD returns, for `W4_O2_REBUY_RESULTS.md`: `PENDING` ×9,
`NOT A RESULT` ×2, MISS ×5, HIT ×2. For `decomposition_peak_rss/RESULTS.md`:
`PASS` ×3, `GATE FAIL` ×3, HIT ×2. For `decomposition_np4/RESULTS.md`: `PASS`
×5, `GATE FAIL` ×2, `BLOCKED` ×1, HIT ×6, MISS ×2. **No bare `FAIL` cell, no
synonym, no hedged label anywhere.** (HIT/MISS are `DAFOAM_CHARTER.md` §12's
prediction tokens, distinct from the gate vocabulary, and are used only in
prediction tables — as passes 4 and 6 also read them.)

**Cost calibration (rule 12) is present and substantively complete** in
`decomposition_peak_rss/RESULTS.md` §8/§8.1: predicted **46.0** core-min against
**42.91** measured = **0.93×**, with per-line attribution (`D_serial` −2.08
favourable load; `D_simple2` +1.17 contention), **zero waste in attempt 2**, and
attempt 1's **21.0 core-min of waste named separately and not netted off** — the
form rule 12 and `COMPUTE_BUDGET_CHARTER.md` §6 require. Dollars are labelled
derived at the owner-stated rate. The **2.0 core-min** allotted to
watcher/staging/grading is **excluded and stated as excluded** rather than folded
in at its estimate, which is the honest treatment of an unmeasured line.

**Two record-hygiene items are owed, neither of which moves a number.**

1. **The B3 calibration row in `docs/COST_CALIBRATION.md` has no id.** At HEAD
   the ledger carries **22** rows matching `^| C-<n>` (max id **C-22**), and one
   further row — line **89**, the B3 peak-RSS row — whose first cell is a
   **date**, not an id. It sits between C-14 and C-15. Substantively the row is
   the best-formed in that file; it simply cannot be cited. **Remedy:** assign it
   the next id from the tail under rule 11, or carry an inline correction row.
   Dafoam's or the chief's call; this lane did not touch it.
2. **Two stale status statements point at the same committed file.**
   `decomposition_peak_rss/RESULTS.md` was committed at `b5ff25d7`, but its own
   header still reads **"DRAFT — NOT COMMITTED … with the dafoam supervisor for a
   personal read before any verdict is recorded"**, and its closing line still
   reads *"the item-level verdict is the supervisor's to record"* — while
   `L-261`, the board (`52c26ec1`) and the np4 addendum all cite its rows as
   findings of record. The calibration row's own reference cell repeats the
   staleness: it states the RESULTS **"is a DRAFT and is NOT YET COMMITTED"**.
   **A reader at HEAD is told by three places that a committed record does not
   exist in git.** Cheapest repair: one dated line at the foot of the RESULTS
   recording the commit and the supervisor's read, plus a correction cell in the
   ledger row. **No verdict moves** — every graded row came from the frozen
   grader and is byte-verified above.

### 59. L-262, the memory-stop proposal — **not applied as lab law anywhere this lane can find, and it must stay that way until Sanaa rules**

L-262 (2026-08-23, recorded 21:22:42Z at `52c26ec1`) states a rule in binding
language: *"the launch gate is derived as **floor + the largest measured (or
explicitly estimated, labelled so) own-peak among the arms + margin**, and a
registration whose gate cannot satisfy its own floor at the registered peaks is
refused at review"*.

**Empirically it is cited nowhere.** A repo-wide sweep for the string `L-262`
across `*.md`, `*.py` and `*.sh` returns **exactly one hit — its own block in
`docs/LESSONS.md:9807`**. Neither audited target cites it, and neither could:
the O2 freeze (21:03:46Z) and the B3 freeze (19:51:22Z) both **predate** it.

**But it is being applied in substance, once, in a third item, and that
application is legal.** The A3 rung-3 attempt-2 pre-registration
(`606930b4`, 2026-08-24T16:17:01Z) moves its own launch gate's memory limb
`MemAvailable ≥ 16 GiB → ≥ 19.65 GiB` and labels it *"the only threshold this
item changes"*, attributing it to **supervisor ruling R2**. **19.65 = 8.0
(that item's own neighbourliness floor) + 11.65 (its own measured peak)** —
L-262's arithmetic exactly, without the citation. This lane reads that as
**legal**: a new registration setting its **own** gate higher, in the safe
direction, touching neither the lab's standing 12 GiB `MemAvailable` floor nor
any other item's threshold. It is not a standard being retired, so it is not
Sanaa-reserved. *(That item is outside this pass's targets and is named here only
because the L-262 question required a sweep.)*

**The reason it must not harden into law without a ruling, and this pass supplies
the evidence.** Applied literally and retroactively, L-262 would have **refused
both of this pass's targets at review**:

| registration | its floor | its own registered peak | L-262's required gate | its actual gate | L-262 verdict |
|---|---|---|---|---|---|
| B3 peak-RSS (`d062aace`) | **4.0 GiB** mid-run hard floor | 5.5–11.0 GiB band, realised **11.133** | ≥ **15.1 GiB** | **12.0 GiB** standing launch gate | would be **refused** |
| W4 O2 re-buy (`8d48fd46`) | **12.0 GiB** standing floor | point **13.5 GiB**, capped at 20.0 | ≥ **25.5–32 GiB** | **24.0 GiB** | would be **refused** |

Both ran, both produced the measurement they were bought for, and **neither
harmed a co-tenant**. B3's registration reached the opposite resolution of the
same tension **deliberately and in writing**: §3.1 set the mid-run floor at
**4 GiB rather than 12** because *"a mid-run kill at 12 GiB would kill a healthy
arm on a shared box the moment a peer starts"* — and §6.4 of its RESULTS records
that `D_serial` spent part of its run at **7.25 GiB** host `MemAvailable`, below
the 12 GiB launch gate and well above the 4 GiB floor: **the arm a 12 GiB
mid-run floor would have killed is the arm that produced the item's headline
number.** O2's is a third design again — a **kernel** cap of 20.0 GiB with the
gate set at cap + 4.0 GiB, so the container provably cannot take the last 4 GiB
of what was available at launch.

**This lane's position, offered as evidence and not as a ruling.** L-262 is a
**PROPOSAL** and the lab currently holds three mutually inconsistent designs for
the same problem (floor + own-peak; a low mid-run floor with a high launch bar;
a kernel cap with a cap-derived bar). Adopting any one of them as binding is a
**standard**, and `CLAUDE.md`'s FIRST-ACTION rule reserves standards and gate
thresholds to Sanaa. **A lesson block cannot create lab law**, and L-262's
"Binding rule for every future memory-gated registration" wording reads as if it
already had — which is the specific hazard this section exists to flag. Two
things are owed and neither is this lane's to take: the wording should be marked
as proposed, and the three designs should be put on one page for a ruling.

### 60. A worktree/index observation on both targets, corroborating D486

`git status` at HEAD reports **`D `** (staged deletion) plus **`??`** for
`W4_O2_REBUY_RESULTS.md` and `decomposition_peak_rss/RESULTS.md`, and `MM` for
`decomposition_np4/RESULTS.md` and this audit file. This lane checked the disk
rather than trusting the index: **`decomposition_np4/RESULTS.md`,
`decomposition_peak_rss/{RESULTS,PREREGISTRATION}.md` and
`docs/CROSS_TEAM_GATE_AUDIT.md` all re-hash byte-identical to their HEAD blobs**
— phantoms, exactly the shared-index staleness D486 established as decay by
construction.

**One is not a phantom, and it matters to a reader.**
`cases/dafoam/ladder-b/W4_O2_REBUY_RESULTS.md` on disk is the lane's **428-line
pre-commit copy** (28,292 B, mtime 2026-08-23 21:31:07Z), while HEAD carries
**466 lines**. The disk copy is a strict byte prefix of the committed blob
(§48), so nothing is lost — but **a reader working from the worktree gets a file
without the supervisor's §12 close-out**, i.e. without the personal
verification, the calibration reading and the "what is owed" paragraph. Reading
that record from `git show HEAD:` rather than from disk is not optional today.
**This lane inspected and did not revert** (rule 10).

### 61. Verdicts

**Target 1 — W4 O2 re-buy: AUDIT: SOUND WITH DISCLOSED DEVIATIONS, AND ONE
DEFECT FOUND** (CANDIDATE — the verification supervisor's own read governs).

| item | as reported | AUDIT (CANDIDATE) |
|---|---|---|
| the freeze | prereg alone, before compute | **SOUND** — one commit in the path's whole history, blob and sha256 re-derived equal to the record's claim, 507 s before the container, instrument md5 19 days older than the freeze |
| the §6 command's transcription (§8a) | disclosed deviation | **DISCLOSED DEVIATION, VERIFIED** — 42 lines byte-identical to the frozen block (`diff` rc=0) |
| **§3 decision `PENDING`** | `PENDING` | **SOUND — a queue state, not a softener.** The registered branch's own wording covers *"launched and stopped … with zero completed `splu`"*; the run's own label is `NOT A RESULT`; every prediction that had a value is a MISS; the dependent consequence is explicitly not claimed as fired (§52) |
| `splu` measurement | `NOT A RESULT` | **SOUND** — killed at the registered cap inside the first threshold; `rc=137` and `CGROUP_PEAK_BYTES` = 20 × 1024³ to the byte, both mapped to their meanings in the freeze |
| `spilu` 4 of 4 singular | measured | **SOUND** — non-tautological (the reader's success branch prints a different, richer row, and has printed it), identity line cross-checked against both parent citations |
| O2R-P5, O2R-P6, C-P1R | MISS ×3 | **SOUND** — all three re-derived; the harder `--cpus=1` billing for C-P1R was registered in advance and against the lane's interest |
| **O2R-P2** | `PENDING` | **DEFECT FOUND** — the frozen rule reads *"any other count is a MISS"*, the count is observably 0, and two sibling rows in the same frozen table carry explicit `PENDING` branches while this one does not (§51). Remedy: a dated addendum regrading it MISS. **No headline verdict moves.** |
| controls | gate + void assertions | **SOUND WITH DISCLOSED DEVIATIONS** — the launch gate **refused with a measured value on disk** (19.77 GiB, rc=3, no container); the void assertions passed but have never been shown able to refuse; **no rule-3 plant into the hump operator**, declined in the frozen file in advance, so pass 4 §12's carried recommendation stays unspent (§50) |
| cost calibration | 15.00 vs 35.0, C-15 | **SOUND** — ratio, four-way attribution with the fourth cause named, zero waste, dollars labelled derived; the record refuses the flattering reading of 0.43× (§53) |

**Target 2 — B3 decomposition (peak-RSS item + the np4 addendum): AUDIT: SOUND
WITH DISCLOSED DEVIATIONS** (CANDIDATE).

| item | as reported | AUDIT (CANDIDATE) |
|---|---|---|
| the freeze and its three addenda | frozen `d062aace`, addenda gate-neutral | **SOUND** — gate-neutrality proven by `cmp` on two byte prefixes (32,392 B and 38,194 B), not by the assertions; both instruments one-commit-only |
| the `§2d.1` repair exception | authorised at Addendum 3 | **LEGAL** — all four conditions checkable; the independent instrument is **on disk**; the repair is upstream of a grading path that never produced a number, because the grader **refused (exit 2)** |
| **M0** | PASS, 18 of 18 | **SOUND, and non-circular** — the archived constants inside the grader are the literal 2026-08-21 log printings, which this lane read from the original logs; `D_simple2` regenerated its own coloring and still reproduced **766** |
| **M4** | GATE FAIL, falsified as registered | **SOUND** — re-derived with this lane's own parser on both instruments (false by 3.133 and 1.784 GiB); the failure direction and its meaning were registered before the run |
| M2a / M2b / M3a / M3b / M5 | PASS / PASS(flagged) / GATE FAIL / GATE FAIL / PASS | **SOUND** — every value re-derived to the byte from the raw sampler logs; the 114,688 B M2b margin is flagged rather than rounded; M5's memory clause is a **censored** test and the record's §9 says so |
| the §4.1 "by construction" refutation | refuted on both arms | **SOUND** — gaps reproduce (+0.370, +1.719 GiB); this lane's per-pid arithmetic **excludes** mechanism 1 for `D_serial`, supporting the record's own reading; neither mechanism was measured by anyone |
| controls | plant, kill-trigger, refusal, attribution, age guard | **SOUND — the strongest control set audited in this file so far.** Plant read back from the raw log; **kill sentinel still on disk**; the grader's refusal limb **fired on a real failure**; one residual: the paired mode control tested 755 where 775 failed, bridged by mechanism and disclosed (§56) |
| the np4 addendum (`bb5088c4`) | quantifying confirmation, no verdict moved | **SOUND** — strict byte prefix proven; it also records against the item's own grain that the 10–14 GiB prediction it had called a miss was right and the instrument wrong |
| cost calibration | 46.0 vs 42.91, 0.93× | **SOUND on substance; the ledger row has no id, and three places still call a committed record a draft** (§58) |

### 62. What this lane could NOT establish, named plainly

- **The dafoam supervisor's §3 personal checks.** `W4_O2_REBUY_RESULTS.md` §12
  attests a personal re-verification against the raw artifacts, and Addendum 3
  attests personal crash triage with the four §2d.1 conditions verified on disk.
  Both descriptions are specific enough to be checkable in their *outputs* and
  this lane checked those outputs; **the reads themselves leave no artifact by
  construction and are taken as attested, not verified.** What can be said is
  where one did not reach: O2R-P1/P2/P3 are absent from §12's enumeration (§51).
- **That any of the four O2 void assertions can refuse.** No run exists in which
  one differed; no mutation was staged; this lane staged none (read-only).
- **That a defect planted in the hump operator would be seen.** No plant exists
  on that matrix. The CBFS `splu` completions (§50) show the reader can print a
  non-zero, on a different operator, 21 days earlier — established here on
  mtime plus the frozen md5, which is evidence and not proof.
- **The `100.05 %` cpu reading** behind O2's "contention 0.00" — an operator
  observation with no file behind it (§53). Nothing rests on it.
- **Whether a 22 GiB cap would have let the hump `splu` finish.** Unknown and
  unknowable from this run, as `W4_O2_REBUY_RESULTS.md` §6a states; the record's
  own §3a arithmetic suggests the requirement may exceed 22 GiB by a wide
  margin, and §3a is correctly **quarantined** — it draws no verdict and is not
  promoted to a MISS on O2R-P1.
- **The mechanism behind `memory.peak` < tree RSS.** Two candidates are named by
  the auditee; this lane excluded one of them for one arm by arithmetic and
  **measured neither**.
- **The unconstrained peak of either B3 arm.** Every B3 figure is a peak under a
  12 GiB cap; the item hands that on as a new registration and this lane did not
  buy it.
- **No dafoam comparator was re-executed.** `analyse_peak_rss.py`,
  `analyze_dump3.py`, `b3_rss_watch.sh` and `chain_peakrss.sh` were **read, not
  run**. Every number above was re-derived by this lane's own parser and
  arithmetic over what those instruments wrote to disk, plus `git cat-file`
  hashes, `cmp` byte comparisons and filesystem mtimes. That tests the grading
  arithmetic, the freeze, the bands and the controls' recorded outputs. It does
  **not** test the samplers' front ends — the cgroup and `/proc` reads
  themselves — which are covered instead by the planted control and, for
  `memory.peak`, by the in-container read agreeing with the external sampler
  **to the byte on both arms**.

**Cost of this pass:** zero solver core-minutes; zero compute launched; nothing
under `cases/dafoam/`, `docs/dafoam/` or `/home/ubuntu/certonomous-runs/` was
written. One Python step — this lane's independent re-derivation over both
watcher logs (738 samples) and both 1.4 MB solver logs — measured by
`/usr/bin/time` at **0.05 s wall / 0.03 CPU-s single core = 0.0005
core-minutes**. Everything else was `git` reads and hashes, `cmp`, `md5sum`,
`stat` and arithmetic. Against this lane's pre-stated prediction of **≤ 1.0
core-min**, the measured figure is **0.0005 core-min**; the prediction was a
ceiling rather than a point and is recorded as met, not as a 2000× miss — the
calibration row states it that way. Lane wall **16 min** against a
predicted ≈ 45 min.

## Audit pass 9 — 2026-08-24, verification LANE (CANDIDATE, not the supervisor's own read)

**Lines whose number changed above this section: 0.** This section is appended
at the foot of an append-only file. The base for this edit was taken from
`git show HEAD:docs/CROSS_TEAM_GATE_AUDIT.md` inside the commit invocation
itself and never from the worktree copy, which is dirty with foreign edits.
Section numbering continues from **62**, the highest numbered section at the
HEAD this was built on.

**This pass was run by a `lab-lane`, not by the verification supervisor
personally.** `SUPERVISION_CHARTER.md` §3 is explicit that a relayed check is a
summary and not a check, so **every finding below is CANDIDATE until the
verification supervisor re-derives it.** The lane was **read-only toward
heat-transfer's territory** throughout: nothing under
`verification/runs/T-family/` or `docs/campaigns/T-family/` was written, no
T-family comparator was re-executed, and every number below was re-derived by
this lane's **own code** over what heat-transfer's instruments left on disk.

**Target:** heat-transfer's **T3 ext1 re-grade** — the heated backward-facing
step ladder, extended from `latestTime` and re-graded at commit **`3dd28411`**
(committer **2026-08-24T16:18:52Z**) as **`NOT A RESULT` 4 of 4** at gate (1),
with G2's grid triple **CONVERGING**. Records:
`docs/campaigns/T-family/{T3_PREREGISTRATION.md, T3_EXT1_AMENDMENT.md,
T3_RESULTS.md}`; instruments
`verification/runs/T-family/T3_runs/{analyse_t3.py, mark_done_t3.py,
mark_done_t3_ext1.py}`; graded artifact
`verification/runs/T-family/T3_runs/gate_t3.json`; run logs
`verification/runs/T-family/T3_runs/log.{analyse_t3.ext1.20260824T155826Z,
mark_done_ext1.20260824T155759Z}.txt`; calibration row **C-23**.

### 63. Freeze order — the comparator predates the first byte of every case, and the pre-registration was never touched after it

| check | finding |
|---|---|
| Comparator freeze commit | **`628ef452`, committer 2026-08-21T18:02:09Z.** `git log -- verification/runs/T-family/T3_runs/analyse_t3.py` returns **exactly one commit in the path's entire history.** The grading path has never been edited. |
| The frozen file **is** the file that ran (rule 2) | **YES, four ways.** Blob id **`d5e4a9eb1aac25d73c88f077c3fb95a549ae9bfb`** is identical on disk, at `HEAD` and at `628ef452`; sha256 **`f41c544d7552e7abfe6adeb8ff1d7ff4c14288017d36821ea3040f1158498741`** re-derived by this lane from all three, and it is the value the run's own log records **before and after** execution and the value `gate_t3.json` carries in `comparator_sha256`. |
| Pre-registration | `T3_PREREGISTRATION.md`, created in the **same commit** `628ef452`, amended once at **`bee3878b`, 2026-08-21T18:02:31Z**, and **never committed again.** Blob **`987c184576e7d4fbc5cc6671c995045555e7df38`** identical on disk, at `HEAD` and at `bee3878b`. |
| First evidence any case could answer a gate | **2026-08-21T18:02:44.163Z** — `R_c/system/blockMeshDict`, the earliest mtime under any of the eight case directories, found by this lane with a `find -printf '%T+'` sweep over all eight. **35 s after the comparator freeze; 13 s after the pre-registration amendment.** |
| Earliest `0/T` (the launch-dating file of rule 4) | **2026-08-21T18:03:22.426Z**, `R_f` — 73 s after the freeze. |
| Grading run | `gate_t3.json` `generated_utc` **2026-08-24T15:58:26.638871Z**, `finished_utc` **15:58:44.896088Z**, sha256 **`8e766cd5dbc59cff336f9756a90967d92f34e981094f3b8b427089eeb34ba573`**. Its predecessor (`5e23f84e…`) is named in the run log as committed at `fd831c11`, so the artifact the re-grade overwrote is **recoverable**, not lost. |

**Nothing that answers a T3 gate predates the instrument that grades it.** This
is the same strong form pass 8 §35 recorded for the GPU arm, reached by a
different route: there, the freeze was proved by a single-commit history plus a
run window; here by a single-commit history plus a filesystem sweep that found
no case artifact of any kind before the freeze.

### 64. Could the gates have failed — the non-tautology proof is inside the same run

The rung's gates are ordered in `T3_PREREGISTRATION.md` §7.1 and implemented in
`analyse_t3.py` `graded_verdict()`: (1) any ladder level not iteratively
CONVERGED → `NOT A RESULT`; (2) triple not CONVERGING → `NOT A RESULT`;
(3) band comparison → `PASS`/`GATE FAIL`. All four graded rows stopped at
gate (1). The audit question is whether either fired gate could have returned
the other answer.

| gate | could it have returned otherwise? | the evidence, from this run |
|---|---|---|
| **(1) iterative convergence** | **YES, and it did — five times.** | The reader returned `CONVERGED` for **5 of the 8 cases** and for **2 of the 3 ladder levels**: `R_m` relative **1.535e-08** (`T`) and **8.754e-09** (`U`), `R_f` **9.679e-08** and **7.796e-08**, against the registered tolerance **1e-6**. At attempt 1 *all three* levels were NOT CONVERGED. **The gate is not a constant function of its input, proven on the same instrument, in the same invocation, over the same tree.** |
| **(2) grid triple** | **YES, and it did — once.** | `x_peak_H` returned **CONVERGING**, `p = 4.3045`. It is the only CONVERGING triple T3 has ever produced, and it arrived on the run whose headline verdict is `NOT A RESULT`. |
| **(3) band** | **NO — and the record says so, in advance and in the output.** | `T3_reference_primary.json` **does not exist on disk** (checked by this lane); `gate_t3.json` `primary_present: false`, `primary_sha256: null`. The comparator prints *"PRIMARY NOT OBTAINED: no band is armed; a graded row that passes the convergence and triple gates is BLOCKED"*. `T3_PREREGISTRATION.md` §2 registered Vogel & Eaton (1985) as NOT OBTAINED **before any case existed**. **No `PASS` is reachable on this rung at all**, and that is stated as an unreached gate rather than replaced by a nearer one — `VERIFICATION_CHARTER.md` §2's M6 clause, honoured. |

**No row is graded `PASS` or `GATE FAIL` on a non-CONVERGING triple.** Tally
re-read from `gate_t3.json`: `PASS 0, GATE FAIL 0, NOT A RESULT 4, BLOCKED 0,
PENDING 0`. **Rule 5's one-way clause is honoured in the hardest available
case**: G2 has a CONVERGING triple and is still `NOT A RESULT`, because gate (1)
fires on level `c` before the triple is consulted. The gate turned a gradeable
row *into* `NOT A RESULT`; nothing turned a `NOT A RESULT` into anything else.

### 65. The completion rule — every limb re-derived by this lane's own code, and it holds 8 of 8

This lane wrote its own parser (`Time =` lines, `ExecutionTime` lines, the `End`
line, `controlDict` `endTime`, field mtimes, `0/T` mtime) and did **not** call,
import or read the output of `mark_done_t3_ext1.py`. Under the two-segment rule
of `T3_EXT1_AMENDMENT.md` §8 each case has `log.solve` (segment 1) and
`log.solve.ext1` (segment 2).

| case | `endTime` | segments (`Time =` span) | last time == `endTime` | Σ `ExecutionTime` == `endTime` | `End` | rc | age guard vs `0/T` | age guard vs `STATUS.<case>` |
|---|---:|---|---|---|---|---|---:|---:|
| `R_c` | 80 000 | 1→20 000, 20 001→80 000 | ✔ | 80 000 ✔ | ✔ ×2 | 0, 0 | **+87 240 s** | **+83 971 s** |
| `R_m` | 36 000 | 1→20 000, 20 001→36 000 | ✔ | 36 000 ✔ | ✔ ×2 | 0, 0 | **+100 039 s** | **+84 137 s** |
| `R_f` | 78 000 | 1→20 000, 20 001→78 000 | ✔ | 78 000 ✔ | ✔ ×2 | 0, 0 | **+247 794 s** | **+186 817 s** |
| `P_m` | 36 000 | 1→20 000, 20 001→36 000 | ✔ | 36 000 ✔ | ✔ ×2 | 0, 0 | **+99 094 s** | **+83 245 s** |
| `C_lam_m` | 80 000 | 1→20 000, 20 001→80 000 | ✔ | 80 000 ✔ | ✔ ×2 | 0, 0 | **+117 819 s** | **+107 504 s** |
| `W_m` | 80 000 | 1→20 000, 20 001→80 000 | ✔ | 80 000 ✔ | ✔ ×2 | 0, 0 | **+80 781 s** | **+79 291 s** |
| `D_m` | 28 000 | 1→20 000, 20 001→28 000 | ✔ | 28 000 ✔ | ✔ ×2 | 0, 0 | **+90 473 s** | **+79 893 s** |
| `O_m` | 46 000 | 1→20 000, 20 001→46 000 | ✔ | 46 000 ✔ | ✔ ×2 | 0, 0 | **+120 120 s** | **+93 340 s** |

- **The `ExecutionTime` count equals `endTime` to the unit on all eight**, summed
  across both segments, and **the two segments join without a gap or an overlap**
  (segment 2 begins at exactly segment 1's last time + 1) on all eight. Neither
  fact is asserted anywhere in the record; both were derived here.
- **`rc = 0` on both segments of all eight**, read from
  `STATUS.<case>` and `STATUS_EXT1.<case>`, not from the marker's summary.
- **Fields present.** Rule 4's thermal set `T U p_rgh alphat nut k omega` is
  complete at `endTime` for seven cases. **`C_lam_m` is missing `nut`, `k` and
  `omega`** — and that is correct, not a gap: `C_lam_m/constant/turbulenceProperties`
  reads `simulationType laminar`, and the marking tool imports `NEEDED` /
  `NEEDED_TURBULENT` from `mark_done_t3.py` and **selftests the exemption**
  (`mark_done_t3_ext1.py:353`, *"laminar case (no nut/k/omega) PASSES"*). The
  exemption is in code with a control, not in prose.
- **The ext1 age guard is STRICTER than rule 4, in the refusing direction.** The
  marking tool demands each field newer than `0/T` **and** newer than
  `STATUS.<case>`, the file that dates the end of segment 1 — so a field written
  by segment 1 and left in place cannot be mistaken for an extension product.
  This lane re-derived both margins independently (columns above); the tightest is
  `W_m` at **+79 291 s**, three orders of magnitude clear. **A tightening of a
  completion rule by a team on itself is worth recording as such.**

### 66. Roache triple gating re-derived — five of six agree to the digit, and **DEFECT FOUND** in the sixth number

This lane implemented Celik et al. (2008) / ASME V&V-20 from the method, not
from `analyse_t3.py`, and ran it over the three ladder values `gate_t3.json`
records. Refinement ratios re-derived from `nCells` (36 000 / 92 160 / 235 520,
two-dimensional, so `r = sqrt(N₂/N₁)`): **r21 = 1.598611, r32 = 1.600000**,
matching the comparator's stored `refinement_ratios` to 7 figures.

| quantity | triple (coarse, med, fine) | state — mine / record | `p` — mine / record | GCI(Fs=1.25) — mine / record |
|---|---|---|---|---|
| `St_peak` | 0.00336772, 0.00343791, 0.00350859 | DIVERGENT / DIVERGENT | **−0.0148 / −0.0148** | n/a |
| `x_peak_H` | 6.0895, 6.13516, 6.1412 | **CONVERGING / CONVERGING** | **4.3045 / 4.3045** | **0.0188 % / 0.0188 %** |
| `St_10H` | 0.00298296, 0.00304705, 0.00310443 | STAGNANT / STAGNANT | **0.2317 / 0.2317** | n/a |
| `St_20H` | 0.00224934, 0.0022961, 0.00233824 | STAGNANT / STAGNANT | **0.2175 / 0.2175** | n/a |
| `x_R_H` | 7.01291, 7.01011, 6.98336 | DIVERGENT / DIVERGENT | **−4.8092 / −4.8092** | n/a |
| `Cf_15H` | 0.00159321, 0.00163293, 0.00166925 | STAGNANT / STAGNANT | **0.1868 / 0.1868** | n/a |

**Every state, every observed order and the one GCI reproduce exactly.** The
`STAGNANT` band (`p < 0.5`) is stricter than textbook Roache, which would call
`St_10H`, `St_20H` and `Cf_15H` monotone-convergent at a very low order; the
band was frozen in the comparator before any case existed and it moves rows only
toward `NOT A RESULT`, never away. **`GCI_fine = 0.019 %` for G2 is correct**,
and rule 5's prohibition on quoting a GCI over a non-monotone triple is
observed — no GCI is printed for the five non-CONVERGING quantities.

**DEFECT — the Richardson extrapolate is printed on the wrong side of the fine
value.** `analyse_t3.py:384` computes

    e21 = f_med - f_fine                 # line 348
    richardson = f_fine + e21 / den      # line 384,  den = r21**p - 1

Celik's extrapolate is `φ_ext21 = (r21^p·φ1 − φ2)/(r21^p − 1)`, which with this
file's own sign convention for `e21` is **`f_fine − e21/den`**. The published
sign is inverted.

- **Measured consequence, the only place it surfaces:** `x_peak_H` converges
  **upward** with refinement (6.0895 → 6.13516 → 6.1412), so its extrapolated
  limit must exceed the finest value. This lane's Celik arithmetic gives
  **6.142121**; the comparator wrote and printed **`RE = 6.14027`** —
  **below the fine grid value**, off by **1.848e-03**, i.e. **0.0301 %** of the
  quantity and **1.6 × the GCI it is quoted beside**.
- **Blast radius: two frozen comparators, one line each.** The identical
  expression is at `verification/runs/T-family/T1_runs/analyse_t1c.py:337`,
  which `analyse_t3.py` imports as `T1C` and whose equal-ratio result its
  `--selftest` asserts it reproduces. A grep for `richardson=` across the
  T-family comparators returns those two sites and no others; `T10a_runs` has
  none.
- **Why the freeze did not catch it.** The `--selftest` block exercises
  `richardson` only for the **presence of the key** (`for k in ("order",
  "GCI_pct", "richardson")`, ~line 1096) and never against a known analytic
  limit. A control that checks a key exists cannot see a sign.
- **No verdict moves, and this lane checked that by reading the grading path,
  not by assuming it.** `graded_verdict()` compares the **fine** value to the
  band (`|fine − value| <= band`); `richardson` is assigned at line 703 for
  CONVERGING rows only and is never an operand of a comparison. The one
  CONVERGING row, G2, exits at gate (1) *before* line 703, so **no
  `gate_t3.json` row even carries a `richardson` key** — the wrong number lives
  only in `triples.x_peak_H.richardson` and in the console log's `RE = 6.14027`.
  **`VERIFICATION_CHARTER.md` §6 exists because of exactly this space, between a
  correct number and the words printed next to it.**
- **Remedy, for heat-transfer and the verification supervisor to weigh, not for
  this lane to apply:** the file is frozen, so rule 6 forbids editing it. The
  charter-clean paths are a dated addendum recording the defect and the corrected
  value, and a `--selftest` case pinning `richardson` to an analytic limit before
  any future rung uses the number.

### 67. Controls — the planted zero FIRED with a measured value, and what it does not establish

**It fired, and the artifact is the run's own log, not a description.**
`verification/runs/T-family/T3_runs/log.analyse_t3.ext1.20260824T155826Z.txt`,
line 10, records the control before any measurement:

    planted-zero control on R_m: {'passed': True, 'planted': 0.001234,
      'read_back_delta': 0.0012340000000108375, 'reader_max_change':
      0.0012340000000108375, 'reader_state': 'NOT_CONVERGED',
      'between': ['34000', '36000']}

- **The refusal limb is real and is upstream of everything.** `main()` calls
  `planted_zero_control()` **before** `measure()` and executes
  `refuse("planted-zero control failed: … its zeros mean nothing")` on a false
  `passed`. A refusal writes no `gate_t3.json`, so **every published T3 number is
  downstream of a control that passed.**
- **It plants into a temp copy, not the case.** `planted_zero_control()` copies
  the last two checkpoints' `T` files to a `tempfile.mkdtemp()` tree, plants
  there, and `shutil.rmtree`s in a `finally`. The graded run directory is never
  written by the control — which is why the age-guard margins in §65 are clean.
- **The read-back is exact.** `read_back_delta − PLANT = 1.084e-14`, i.e. the
  planted perturbation was written to disk, re-read from disk and recovered to
  double precision.

**What it does not establish, stated plainly.** `R_m`'s decision threshold is
`1e-6 × field_range = 1e-6 × 51.295947 K = 5.1296e-05 K`. The plant is
**1.234e-03 K = 24.06 × that threshold**, while the value the reader actually
reported for `R_m` is **7.875e-07 K = 0.0154 × the threshold**. So the control
proves the reader is **not blind**, at 24× above the decision boundary; it does
not exercise the boundary itself, and the reported value sits 64× below it. The
exact read-back argues the reader is a plain max-absolute-difference with no
resolution floor, which makes a boundary plant very likely redundant — but that
is an argument, not a measurement. **Candidate recommendation, not a finding
against the rung:** a second plant at `1.05 × tol_abs` would close it, and it is
a sub-second addition. **A further limitation:** the control is planted into
**`R_m` only**, one case of eight. The reader is the same object for all eight,
so what is established is the *reader class*, not each case's read.

### 68. Amendments after first compute — legal and gate-neutral, proved by byte prefix; and one **DEFECT** in a frozen stamp

First compute is **2026-08-21T18:02:44Z** (§63). Everything before it is a
pre-compute amendment; everything after must be a dated addendum that alters no
gate, threshold, cap or label.

| item | when | audit |
|---|---|---|
| `T3_PREREGISTRATION.md` amendment (`bee3878b`) | **18:02:31Z, 13 s BEFORE first compute** | **LEGAL under rule 2's first bullet, and it names its condition and how it was checked** — *"no T3 case directory existed — checked with `find verification/runs/T-family/T3_runs -type d`, which returned nothing"*. This lane confirmed the condition independently: the earliest artifact under any case directory is 13 s later. **It also registered, in advance, the outcome that occurred:** *"A separated RANS flow under SIMPLE may never meet this; if it does not, the rows are NOT A RESULT and the record says so — the criterion is not relaxed after the fact."* |
| `T3_EXT1_AMENDMENT.md` §14, the ordering disclosure (`586ea08c`) | 2026-08-22T18:14:25Z | Post-compute; disclosed on its face as a departure (extensions launched ahead of the committed amendment). Recorded, not re-litigated here. |
| `T3_EXT1_AMENDMENT.md` §15, predictions scored (`3dd28411`) | 2026-08-24T16:15:34Z | **GATE-NEUTRAL, PROVED BY BYTES, NOT BY ITS OWN ASSERTION.** The file's first **869** lines at `3dd28411` are byte-identical to the whole of the file at `586ea08c` (sha256 of both: `1f200321c4312f3e…`). Its rule-6 claim *"lines whose number changed above this section: 0"* is **true, verified mechanically.** §15 scores §6's predictions and adds no gate. |
| `T3_RESULTS.md` §14 (`3dd28411`) | 2026-08-24 | **Same test, same result.** First **504** lines byte-identical to the whole file at `fd831c11` (`e557c798df87181e…`). 486 lines appended, none inserted. |

**The predictions are scored against the team's own interest.** §15 records
**P3's secondary clause as FALSIFIED** — heat-transfer predicted that *none* of
G1–G4 would come back CONVERGING, and G2 did — and states the non-renegotiation
rule was honoured anyway. A record that files its own miss in the row next to
its hits is the behaviour rule 2 exists to produce.

**DEFECT — an in-record stamp inside a FROZEN pre-registration is written ahead
of its own commit, and read literally it falsifies the condition it asserts.**
`docs/campaigns/T-family/T3_PREREGISTRATION.md:241` reads *"amendment of
**2026-08-21 18:05 Z**"*. The commit that introduced the line, `bee3878b`, has
committer date **18:02:31Z** — the stamp is **+149 s ahead of the wall clock**,
the `bd3edfe8` class this lab built `scripts/check_stamp_vs_commit.py` for
(ledger row C-25). It matters more than the 149 s suggests: **18:05Z is 76 s
AFTER the first T3 case artifact appeared (18:02:44Z)**, so a reader taking the
document's own stamp as binding would conclude the amendment post-dated first
compute and was illegal. **It was not.** The binding evidence is the committer
date, which precedes first compute by 13 s, and the condition the amendment
names is independently true at that time. **Gate-neutral; no verdict moves; the
remedy is a dated addendum, since rule 6 forbids editing the frozen file.**

**An instrument finding against the verification team's own tool, recorded
here so it is not mistaken for a heat-transfer defect.** Run over the three T3
records, `check_stamp_vs_commit.py` reports **9 FIRES**. **Eight of them are
false positives of one class:** `T3_EXT1_AMENDMENT.md:660–667` are the **ETA
column of §10.4's rate table** — predicted finish times, correctly ahead of the
commit that wrote them (`D_m` 19:12:55Z … `R_f` 2026-08-25T14:54:30Z). The
checker's cue list caught the two *prose* sentences quoting the same ETAs
(lines 669 and `T3_RESULTS.md:873`, both reported as PLANNED) but **cannot see a
future-intent cue when the stamp is a table cell whose cue lives in the column
header.** Only the ninth fire, `T3_PREREGISTRATION.md:241`, is genuine. **Owed
by the verification team, not by heat-transfer: a table-aware cue (a header cell
matching `ETA|forecast|predicted|projected` marking its whole column PLANNED).**

### 69. Cost calibration (rule 12) and verdict vocabulary

**The calibration comparison is present, complete, and this lane re-derived its
arithmetic from the raw status files rather than accepting it.** Row **C-23** of
`docs/COST_CALIBRATION.md` (dated 2026-08-24, heat-transfer).

| element | the row's figure | this lane's independent re-derivation |
|---|---|---|
| actual, measured unit | 4 798.05 core-min = 79.968 core-h | **287 883 wall s** summed by this lane from the eight `STATUS_EXT1.<case>` files (13 782 + 14 884 + 162 094 + 15 095 + 33 909 + 7 230 + 6 380 + 34 509), serial at `nProcs 1`, ÷ 60 = **4 798.05 core-min** ✔ ÷ 3600 = **79.968 core-h** ✔ |
| dollars | $4.102 **derived, not measured** | 79.968 × 0.0513 = **$4.1023** ✔, and the row states the rate is owner-stated and the box cannot read its own billing ✔ |
| ratio | **1.005×** vs the §5 pre-launch estimate; 0.738× vs the §10.4 post-launch revision | 79.968 / 79.55 = **1.0053** ✔. **Both ratios are carried**, and the flattering one is not the only one shown. |
| rung to date | 120.29 core-h = $6.171 = 24.7 % of the $25 ceiling | segment-1 walls sum to **145 157 s**; + 287 883 = **433 040 s** = **120.289 core-h** ✔ × 0.0513 = **$6.171** ✔ ÷ 25 = **24.7 %** ✔ |
| waste | **nil, 0.00 core-min, separately named** | consistent with §65: all eight terminated under the solver's own hand, so there is no abandoned segment to name. Not absorbed into the ratio ✔ (`COMPUTE_BUDGET_CHARTER.md` §6). |
| gross vs cleaned | **gross == cleaned**, with the stall rule addressed rather than ignored | **All eight ext1 rows exceed rule 12's 3 600 wall-s stall heuristic** (smallest `D_m`, 6 380 s; largest `R_f`, 162 094 s). The row does not quietly pass over this: it argues the heuristic detects a *hung or abandoned* row and that every one of these carries `rc=0`, an `End` line, last time == `endTime` and a full `ExecutionTime` count — **all four of which this lane re-derived independently in §65.** **A reading of the heuristic, disclosed and evidenced, not a silent exemption.** |
| honesty about the model | *"two cancelling errors … NOT the record of an accurate model, and must not be filed as one"* | The row refuses the flattering reading of its own 1.005×, attributes the two errors (no fixed-cost term: `W_m` 1.617×, `D_m` 1.507×, `R_c` 1.404×; an over-extrapolated 5-minute contention window: `R_f` 0.917× of §5) and states the calibration lesson. **This is the standard the ledger should be held to.** |

**Verdict vocabulary — CLEAN.** Token census across the three records at
`3dd28411`: **10 `FAIL` tokens in total, every one of them part of `GATE FAIL`
or `GATE FAILED`** (2 / 3 / 5 in prereg / amendment / results). **No bare `FAIL`
cell** — the class CLAUDE.md rule 1 flags as referred-and-unruled does not occur
here. A sweep for *"roughly converged", "partial pass", "near-pass",
"inconclusive", "marginal pass", "weak pass", "soft fail", "essentially
passed"* returns **zero hits** in all three files. `gate_t3.json`'s verdict
cells are `NOT A RESULT` ×4 and `REPORTED` ×13.

**`REPORTED` is not one of rule 1's six words, and it is not a breach.** It was
**registered in advance** as a non-graded channel: `T3_PREREGISTRATION.md:94`
(*"is REPORTED, never graded. No verdict in this rung rests on it"*) and the
row table at lines 313–319 assign it to M1, DW, DD and the heat-balance guards
before any case existed; every such row carries `counted_in_tally=False` in the
JSON, and the tally sums **only** the graded rows. **One display candidate, not
a finding:** `gate_t3.json`'s stored `tally` dict includes the key
`"REPORTED": 0` while thirteen rows carry `verdict: "REPORTED"` — arithmetically
correct (zero *graded* rows are REPORTED) but capable of misleading a reader of
the JSON alone. The console output does not have the problem: it prints only
non-zero counts, as *"4 graded rows: NOT A RESULT 4"*. **This is the same
boundary passes 5 §21 and 8 §41 named — a second vocabulary living alongside the
verdict vocabulary, still unwritten in any charter.** Third sighting; it is
beginning to look like a charter line rather than a curiosity.

### 70. Verdict

**AUDIT: SOUND WITH DISCLOSED DEVIATIONS, AND TWO DEFECTS FOUND** (CANDIDATE —
the verification supervisor's own read governs). **Nothing in this pass moves a
heat-transfer verdict, and this lane wrote nothing in heat-transfer's
territory.**

| item | as reported | AUDIT (CANDIDATE) |
|---|---|---|
| **the freeze** | comparator frozen before any case existed | **SOUND** — one commit in the path's entire history; blob id and sha256 identical on disk, at HEAD and at `628ef452`; the earliest artifact under any of the eight case directories is **35 s later** |
| **the file that ran IS the frozen file** | claimed | **SOUND, verified four ways** — sha256 `f41c544d…498741` from disk, from HEAD, from `628ef452`, and recorded by the run itself before and after execution |
| **`NOT A RESULT` ×4 at gate (1)** | the comparator's own output | **SOUND, and non-tautological** — the same reader returned `CONVERGED` for 5 of 8 cases and 2 of 3 ladder levels in the same invocation (`R_m` 1.535e-08, `R_f` 9.679e-08 vs tol 1e-6) |
| **G2 triple CONVERGING** | `p = 4.304`, GCI 0.019 % | **SOUND** — `p = 4.3045` and GCI `0.0188 %` reproduced exactly by this lane's own Celik implementation; and the row is still `NOT A RESULT`, which is rule 5's one-way clause honoured in its hardest case |
| **the other five triples** | DIVERGENT ×2, STAGNANT ×3 | **SOUND** — all five states and all five observed orders reproduced to four decimals; no GCI quoted over a non-monotone triple |
| **the Richardson extrapolate** | `RE = 6.14027` | **DEFECT — the sign is inverted** (`analyse_t3.py:384`, and identically `analyse_t1c.py:337`). Celik gives **6.142121**; the printed value falls **below** the finest grid value on an upward-converging ladder, off by **1.848e-03 = 0.0301 %**, 1.6× the GCI beside it. **Display-only: `richardson` is never an operand of a verdict, and no `gate_t3.json` row carries the key.** The `--selftest` checks the key exists, never its value (§66) |
| **completion rule, 8 of 8** | strict rule met | **SOUND — every limb re-derived by this lane's own parser**, including two the record does not assert: the `ExecutionTime` count equals `endTime` to the unit on all eight, and the two segments join with no gap or overlap on all eight. `C_lam_m`'s missing `nut/k/omega` is a **coded, selftested laminar exemption**, not a gap |
| **the ext1 age guard** | fields newer than `0/T` | **SOUND, and STRICTER than rule 4** — also newer than `STATUS.<case>`; tightest margin **+79 291 s** (`W_m`), re-derived here |
| **planted-zero control** | passed | **SOUND — fired with a measured value on disk, upstream of every number**, read back to 1.084e-14, refusal limb real and JSON-suppressing. **One limitation named:** the plant is 24.06× the decision threshold and lands on `R_m` only; the boundary itself is unexercised (§67) |
| **gate (3), the band** | reference NOT OBTAINED, no band armed | **SOUND** — `T3_reference_primary.json` absent from disk, `primary_present: false`, registered as NOT OBTAINED before any case existed. **No `PASS` is reachable on this rung, and the record says so rather than substituting a nearer gate** |
| **amendments after first compute** | dated addenda, gate-neutral | **SOUND, proved by byte prefix rather than by their own assertions** — 869 lines and 504 lines byte-identical; and P3's secondary clause is filed as **FALSIFIED**, against the team's interest |
| **the frozen prereg's own stamp** | (not claimed) | **DEFECT — `T3_PREREGISTRATION.md:241` reads "2026-08-21 18:05 Z", +149 s ahead of its commit and 76 s AFTER first compute.** Read literally it falsifies the pre-compute condition the amendment asserts. **The condition is true on the binding evidence (committer date 18:02:31Z, 13 s before first compute); no verdict moves.** Remedy: a dated addendum, never an edit (§68) |
| **cost calibration (rule 12)** | C-23, 1.005×, waste nil | **SOUND, and among the best rows in the ledger** — every figure re-derived here from the raw `STATUS_EXT1` walls (287 883 s → 4 798.05 core-min → $4.102) and the rung total (433 040 s → 120.29 core-h → $6.171 → 24.7 %); both ratios carried; the 3 600-s stall heuristic **addressed with evidence rather than skipped**; the row refuses the flattering reading of its own result |
| **verdict vocabulary** | — | **CLEAN** — 10 `FAIL` tokens, all `GATE FAIL(ED)`; zero hedges; `REPORTED` registered in advance as a non-graded channel. One JSON display candidate (`"REPORTED": 0` beside 13 REPORTED rows) |

**The headline is the anti-tuned direction, and that is the point.** T3 spent
**120.29 core-h** across two attempts and returns **0 of 4 graded rows**. The
re-grade moved two ladder levels from NOT CONVERGED to CONVERGED, produced the
rung's first CONVERGING triple, closed the fine-level heat balance from 8.234 %
to 0.0003935 %, and **changed no verdict** — because the coarse level is in a
limit cycle that `T3_PREREGISTRATION.md` §11 registered in advance as an outcome
the rung reports rather than averages. A team that buys 79.97 core-h of compute,
gets a better-behaved ladder, and still writes `NOT A RESULT` in the first line
is doing the thing this charter was written to make possible.

### 71. What this lane could NOT establish, named plainly

- **The heat-transfer supervisor's §3 personal checks.** The commit message of
  `3dd28411` attests that this lane's counterpart *"independently re-hashed all
  six instruments against HEAD, re-derived every number from `gate_t3.json` and
  the case directories"*, and that the comparator run at 15:58:26Z and the
  marker at 15:57:59Z were executed by **a lane of a parallel session** before
  the chief redirected T3 to the recording session at 16:00Z. The disclosure is
  unusually specific and its *outputs* are checkable — this lane checked them —
  but **the reads themselves leave no artifact by construction and are taken as
  attested, not verified.**
- **That the run's `analyse_t3.py` invocation was the one that produced
  `gate_t3.json`.** The chain is strong but circumstantial: the log's own
  `EXIT_CODE=0`, the post-run sha256 `8e766cd5…4ba573` and the mtime
  15:58:44.918Z bracket `gate_t3.json`'s `finished_utc` of 15:58:44.896Z by
  22 ms. **No witness file cross-signs the pair.** Nothing suggests otherwise;
  it is stated because it is an inference, not a measurement.
- **Whether the convergence reader resolves a change at its own decision
  threshold.** §67: the plant is 24× above it and the reported value 64× below
  it. The exact read-back makes a resolution floor very unlikely, but no
  boundary plant exists.
- **The physics reading of `p = 4.304`.** `T3_RESULTS.md` reads it as *"levels
  too close to resolve an order, not fourth-order accuracy"* — a judgement about
  the scheme's formal order that this lane can neither confirm nor refute from
  the artifacts, and one that no gate rests on.
- **Whether the sign defect of §66 has ever produced a published number
  elsewhere.** `analyse_t1c.py:337` carries the same expression. Whether any T1c
  record quotes an `RE` value, and on which side of its ladder, was **not swept**
  — it is T-family territory and outside this pass's read. **Flagged for the
  verification supervisor to route.**
