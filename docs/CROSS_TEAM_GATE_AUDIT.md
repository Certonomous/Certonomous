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
