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
