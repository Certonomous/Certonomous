# dafoam — GRADING CHAIN

**Filed under Sanaa's GRADING TRANSPARENCY ORDER, 2026-08-31** (`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`, captured verbatim; committed at `4116024a`).

Her rule for this page: *"If any link in your chain can't be named in one bullet, that's a finding, not a formatting problem."* Bullets 8–10 are findings. They are the honest state of this family's chain, not omissions.

**NOT FILED ANYWHERE.** Nothing in this document has been filed, posted or sent outside this box.

---

1. **What gets graded is a JSON artifact, never a log.** Each arm's in-container extractor writes a structured artifact — `<item>_X.json` for adjoint arms, `<item>_F.json` for FD arms — plus `ledger.txt`, `STATUS.<arm>` and `STATUS.chain`. The solver log is *evidence used in triage*, never the graded object. A missing artifact is a gradable state; a malformed one is a refusal (SO-3aR: `C3_artefact_absent`, and the comparator refused rather than degrading).

2. **The reader is the item's own frozen comparator**, `cases/dafoam/.../<item>_grade.py`, frozen at the pre-registration commit. Its identity is checked by hashing the file that ran against the committed blob (`CLAUDE.md` rule 2; `scripts/check_comparator_freeze.py`). The grading path is fixed at freeze, so the reader cannot be chosen after the answer is known.

3. **The frozen gate is the registered gate table** in `<case>/PREREGISTRATION.md` §3 — typically `G1` completion (the rule-4 clauses printed per arm, incl. the age guard), `G5`/`G5J` the FD bright line per component against band D, `G-TB` the trivial baseline, `G9` toolchain identity per row, `G10` caps, `G-M2` mesh identity. Gates close at first compute; afterwards only dated addenda that cannot move a gate, threshold, cap or label.

4. **The referee for every adjoint is a finite-difference table at a step proved to lie in the plateau.** This is the charter's bright line (`DAFOAM_CHARTER.md` §2): *"No DAFoam gradient enters a record, a report or an optimisation without a finite-difference table beside it."* No FD table, no gradient verdict.

5. **The proof that the reader can see is a planted control that has actually fired.** Citation, live and recent: SO-2M's comparator **refused at `grader_rc=2`** with `REFUSE CONTROL — G5m_did_NOT_flip_to_GATE_FAIL_under_the_planted_copy`, printing `plant = 0.001234`, `plant_needed_to_cross_band_D = 0.002488123110353001`, `plant_is_sufficient: false`. The refusal is live machinery, not decoration.

6. **A second, independent live control is the trivial baseline**, an arm run at a deliberately absurd step (h = 1e-8) that **must fail**. Citation: SO-1cR's trivial baseline failed 5 of 5 components — 97.7 / 92.9 / 345.8 / 101.6 / 62.8 %, two sign flips — demonstrating the gate is capable of failing on the same instrument that returned its PASS.

7. **The verdict lands in four places, in this order:** `<run root>/<ITEM>_grade_<stamp>.out|.json` (authoritative, written by the comparator) → `cases/dafoam/.../RESULTS.md` (the in-git record) → the two-row table in `docs/dafoam/README.md` §3 → `docs/LAB_STATE.md`. **Every item is TWO ROWS, SHIPPED and PATCHED**; an item with only one row executed yields **no verdict at all**, not a partial one.

8. **⚠ FINDING — the authoritative verdict is born outside version control.** Run roots live at `/home/ubuntu/certonomous-runs/`, outside git. Between the comparator writing a verdict and a `RESULTS.md` landing, the verdict of record exists only on disk. **Measured tonight:** SO-3aR died 20:22:15Z with `NOT A RESULT` in its run root while HEAD's newest mention of it still read *"SO-3aR LIVE"* — stale for 23 minutes, and it took a deliberate commit (`3a7e5219`) to close.

9. **⚠ FINDING — the last two hops of the chain are not mechanical.** Nothing links a graded verdict to `docs/dafoam/README.md` §3 or to `cases/dafoam/INDEX.md`. **Measured:** `INDEX.md` was last touched 2026-08-22 and carries **zero** entries for SO-2M, SO-3a or SO-3aR — the whole SO-series is unindexed. These hops are maintained by a person reading a page, and this page says so rather than implying automation that does not exist.

10. **⚠ FINDING — the planted control is registered per item, and has been registered wrong.** SO-2M's plant was inherited from a CD-scale item as a **bare absolute** and was never sized against the functional it had to perturb: `1.234e-03` is 33.76 % of a CD reference but only **2.48 %** of `CMZ`'s, and could not cross its own 5 % band. Fixed forward by the SO-2MR ruling — the plant is registered **relative**, `plant_i = K · (band_D/100) · |d_ref_i|`, as a rule fixed at freeze, never a number chosen after seeing an answer.

---

## Cause classes on this family's non-PASS verdicts

Per §2 of the order: one of exactly eight, assigned **by the grading record** and cited. Only `PHYSICS-FAIL` and `MODEL-LIMIT` say anything about the lab's ability to do physics.

| item | verdict | CAUSE CLASS | citation |
|---|---|---|---|
| **SO-3aR** | `NOT A RESULT` | **NAMING/PLUMBING** | Shared run directory: three scenarios, no per-point `run_directory`, all renaming to `0.0001`. `curriculum_SO3aR/RESULTS.md`; Sanaa's own worked example. |
| **SO-3a** | `NOT A RESULT` | **INSTRUMENT** | Unfilled fail-closed producer pin; extractor refused before physics. `SO3a_grade_…out`, `so3a_xf.py:111`. |
| **SO-2M** | `NOT A RESULT` | **GATE-DESIGN** | Every arm `rc=0`, physics clean; the **registered plant** was too small to cross its own band. The comparator was correct; the gate as registered was defective. |
| **SO-1c** | `NOT A RESULT` | **INSTRUMENT** | Row-label break in call sites the R8 repair never swept. |
| **D6** | `NOT A RESULT` | **BUDGET/KILL** | Container deadline `rc=124` at 30,008 s; **no `EXIT:` line at all**. `CURRICULUM-D6…/ledger.txt`. |
| **D6R** | `NOT A RESULT` | **BOOKKEEPING** *(corrected 2026-08-31T21:0xZ — was filed PHYSICS-FAIL; see the correction below)* | D6R's own frozen grader refused on `{"REFUSE": "G-D6R-OPT", "n_exit": 1, "n_obj": 0, "no_final_objective_or_exit": ".../O_mp/opt_IPOPT.txt"}`. **All four gradient gates read `ARM_DID_NOT_RUN`** — `D6RG_regrade.json` `grade/G-D6R-{1,2,3,4}/reason`. |
| **SO-1aR shipped row** | `GATE FAIL` | **PHYSICS-FAIL — against the SHIPPED TOOLCHAIN** | `shape[6]` 637.757 % with a sign flip vs a proven FD referee. |
| **D15 / D16 shipped rows** | `GATE FAIL` | **PHYSICS-FAIL — against the SHIPPED TOOLCHAIN** | D15 worst 44.87 % (`shape[6]`); D16 5.1511 % (`shape[0]`). |

**Two qualifications this family will not paper over:**

- **`PHYSICS-FAIL` against the shipped toolchain is a finding about DAFoam, not about this lab's ability to do physics.** The instrument is proven and the answer is genuinely wrong — so the class is right — but the capability question in §3 of the order should read these rows as *the shipped toolchain cannot do this*, not *the lab cannot*. The patched rows pass the same gates.
---

## ⚠⚠ CORRECTION, 2026-08-31 — D6R WAS FILED `PHYSICS-FAIL` AND THAT WAS WRONG

**Sanaa, on reading this family's conversations:** *"I saw in the dafoam conversations that there was actually no gradient failure in the multipoint compressible case and that the issue was a bookeeping one! this is what led me to ask for these clear denominations/separations."* (`etc/sessions/…`, commit `5e782552`.) **She is right, and this document had it wrong in its first version.** The correction is recorded here rather than by silently rewriting the row.

**There is no gradient failure in D6R because NO GRADIENT WAS EVER MEASURED.** From the verdict of record, `curriculum_D6RG/D6RG_regrade.json`:

- `grade/G-D6R-1/reason`, `G-D6R-2`, `G-D6R-3`, `G-D6R-4` — **all four read `ARM_DID_NOT_RUN`**, each `NOT A RESULT`, with per-point `cl04`/`cl05`/`cl06` likewise `ARM_DID_NOT_RUN`.
- `grade/G1/arms_not_run` — **`F_mp` (the FD arm) and `REF_off` never ran**, `REGISTERED_CHAIN_STOPPED_AT_FIRST_NONZERO`. `F_mp` is the arm that "reads the optimiser endpoint" — the finite-difference referee. **The FD table this family's bright line requires was never produced.**
- D6R's own frozen grader refused on a **record** defect: `n_exit = 1`, **`n_obj = 0`**, `no_final_objective_or_exit` in `O_mp/opt_IPOPT.txt` — the exit line was written, the final objective line was not.

**And the IPOPT message that made this look like physics is misleading.** `EXIT: Invalid number in NLP function or derivative detected.` comes from a guard at `IpOrigIpoptNLP.cpp:487` that fails **disjunctively** — on a false *status* OR a non-finite *value* — and prints the same string either way. Measured on the log: **671 `Primal solution failed!` banners against 673 cutbacks** (near 1:1); the objective printed immediately before the final cutback is **finite at `0.0222388`**; and a sweep of every `CD:`/`CL:` print across **264,607 lines returns ZERO non-finite tokens** (the only `NAN` strings sit in pyOptSparse's post-mortem table, written *after* the EXIT). **The guard tripped on failed primal status, not on a bad number.**

**Correct class: `BOOKKEEPING`.** Solve produced answers; the stamp was impossible. Second, separate non-physics finding on the same item, not folded in: `grade/G10/verdict = GATE FAIL` — the cap gate.

**What this item does NOT license, in either direction:** no physics claim, favourable or adverse, can rest on D6R. It is not evidence that the multipoint gradient is wrong, and it is not evidence that it is right.

**The one real physical phenomenon here is separate, ungraded, and is what `SO3D` exists to investigate:** multipoint primal-failure rate **D6R 68.68 % (671/977)** and **D6 66.42 % (546/822)**, against **D4 2.222 % (3/135)** and **D5 1.170 % (2/171)** single-point on the same base mesh, same image digest, identical `primalMinResTol`. **A thirty-fold contrast** — real, measured, and never yet the subject of a graded verdict.

**Why I got it wrong:** I reasoned from the IPOPT message's *wording* to a physics cause, instead of from the grading record — the precise failure this order exists to end, committed inside the document written to comply with it. The order's rule is that the class is assigned **by the grading record**; had I opened `D6RG_regrade.json` before classifying, `ARM_DID_NOT_RUN` was sitting in four consecutive keys.

**Revised headline split for this family: 3 physics-adverse / 6 non-physics** — and **all three physics-adverse rows are against the SHIPPED TOOLCHAIN, none against the lab.**

**D15/D16 re-checked against their records under this same order and they STAND as `PHYSICS-FAIL`**, unlike D6R: their FD arms *did* run, FD tables exist, and the shipped adjoint genuinely disagrees with a measured FD referee (D15 worst **44.87 %** on `shape[6]`, 3 of 5 components outside band D; D16 **5.1511 %** on `shape[0]`). Those are real gradient failures of the shipped toolchain. The separate weakness recorded at bullet 10's neighbourhood — that D15's **patched** `shape[7]` plateau is one-sided at `[1.156 %, 21.630 %]` — bears on the *patched* row's precision, not on the shipped row's failure, which sits an order of magnitude outside any plateau ambiguity.

**Not yet classified, and deliberately not guessed:** the AV-pair `BLOCKED` rows require the FAD-primal record to be read before `MODEL-LIMIT` or `PHYSICS-FAIL` can be assigned. The order says the class is assigned by the grading record; classifying from memory would breach it.
