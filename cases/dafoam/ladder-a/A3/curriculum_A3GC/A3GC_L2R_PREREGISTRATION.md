# A3GC-L2R — PRE-REGISTRATION

**Frozen 2026-09-12. Written BEFORE any L2R compute. SUBMISSIONS PARKED.**

L2R is the **repaired re-run of A3GC-L2**, which was stopped at Time 1200/6000 as a certain
`NOT A RESULT` (`A3GC_L2_REPAIR_ADDENDUM_2026-09-12.md`). It carries **one changed numerical
setting** and is graded by a **new comparator** that reads the residual the old one could not.

**A3GC-L2's disposition is unchanged and is not rewritten. L2R produces a new row.**

---

## 1. THE DIAGNOSIS THIS REPAIR ACTS ON

L2 ran `nNonOrthogonalCorrectors 0` against a mesh measuring **max non-orthogonality 72.07°**
with **241 faces past 70°**, 586 low-quality tet faces and `Failed 2 mesh checks`
(`A3GC-L2/meshgen/logCheckMesh.txt:96,97,103`), while `fvSchemes:53,58` ask for a `corrected`
non-orthogonal term that was therefore **never iterated**. DAFoam's own `DACheckMesh` prints its
threshold as **`maxNonOrth: 70`** — L2 is past the **solver's** limit, not a guideline.

**The case's own dictionary already concedes the point:** `fvSolution`'s `potentialFlow` block
runs **`nNonOrthogonalCorrectors 20`**, while `SIMPLE` runs **0**. The initialiser was given
correctors for this mesh; the solver that produces the graded answer was not.

**And `r` does not explain it.** Not monotone — L2's 1.4006 sits between AR1's converging 1.1674
and L3's stalling 2.0880 — and **AR1 and L3 are identical at max non-orth 61.15806658877255** yet
behave differently. What is unique to L2 is being the **only** level past 70° with zero correctors.

**Newly measured, and it quantifies the conditioning:** with correctors enabled on L2's own mesh,
GAMG needs **28, 105 and 157 iterations** to achieve `relTol 0.1` — one decade — on the three
corrector solves of a single step (`A3GC_L2R_FIXTURE_multicorrector.log`). **Over a hundred
GAMG iterations per decade is pathological for a multigrid solver** and is what a 72° mesh costs.

## 2. THE CHANGE — ONE LEVER, WITH ITS PROVENANCE CHECKED

    SIMPLE { nNonOrthogonalCorrectors  0  ->  12; }

**Provenance, verified against the record rather than repeated from a brief**
(`cases/dafoam/ladder-a/A2/curriculum_D6RF10/D6RF10_GRADE_RECORD.md:62-65`):

| rung | configuration | outcome |
|---|---|---|
| R1 | `nNonOrth 3`, `DARhoSimpleFoam` | **GATE FAIL** — `p_first_uncorrected` 1.681236312e-05 |
| R2 | `nNonOrth 12`, `DARhoSimpleFoam` | **NOT A RESULT** — SIGKILLed ~4 % short of its deadline |
| R3 | `DARhoSimpleCFoam` + **`nNonOrth 12`**, `relax_p` 0.70 | **PASS** — `p_first_uncorrected` 6.3233727e-06 |

**Correction to the brief I was given:** `nNonOrth 12` did **not** pass on its own — R2 was never
graded. The PASS is **R3**, which pairs `nNonOrth 12` with the **SIMPLEC coupling**.

**That is exactly why the transfer is clean here. A3GC ALREADY HAS THE REST OF R3:** it runs
`DARhoSimpleCFoam` (`runScript_a3gc.py:28`) and relaxes `p` at **1.0**, at or above R3's 0.70.
**The single R3 lever A3GC lacks is `nNonOrth 12`, and that is the single lever L2R adds.**

`nNonOrth 3` is **not** chosen: A2 measured it GATE FAIL at R1.

**Nothing else changes.** GAMG `relTol` stays 0.1; the mesh, `runScript_a3gc.py`, `fvSchemes`,
`decomposeParDict`, `constant/` and every relaxation factor are **byte-identical to L2**.
`relTol` is deliberately left alone: §1 of the repair addendum measures leftover linear error at
~9.5 %, which **cannot** close a three-decade gap, so tightening it would add cost and confound
attribution without being the lever. **It is held in reserve as a registered next step.**

## 3. THE COMPARATOR — NEW FILE, NEW FREEZE, AND THE FROZEN ONE IS NOT TOUCHED

`a3gc_grade.py` **is not edited.** It stays at **md5 `73dbe368934956700da87e5a1f44ea0c`** and
continues to grade AR1 and AR1C, whose logs carry one `initRes` line per block and for which its
last-match rule is correct.

L2R is graded by **`a3gc_grade_l2r.py`**, md5 **`b188e7e1b0034a53267dc9b818138b8c`**, committed
in this same commit. **Its only semantic difference is one line:** `read_log` keeps the **FIRST**
match per equation per block instead of the last.

**Why FIRST, and why not MAX.** `DAUtility::primalResidualControl` is called inside
`while (simple.correctNonOrthogonal())` (`pEqnRhoSimpleC.H:42,60` — verified in
**`DARhoSimpleCFoam`**, the solver this case actually runs) and prints one line **per corrector**.
The **first** line is the outer iteration's initial residual **before any corrector has acted**,
which is precisely what "has this outer iteration converged" means. **FIRST is correct by
construction; MAX would usually coincide with it only because the first corrector usually carries
the largest residual — "usually" is a property of the arithmetic on a given day, not of the
definition.** This is also the lab's **existing ruled precedent**: A2's binding field is
`p_first_uncorrected`, "the FIRST/uncorrected p-solve of the final outer iteration"
(`curriculum_D6RF10/PREREGISTRATION.md:92`), upheld by supervisor ruling `a2978688`, 2026-09-08.

**THE 1e-06 GATE DOES NOT MOVE.** Only the reader changes, and it changes to read the residual
**before** the correctors reduced it — the **harder** number. **THIS AMENDMENT CAN ONLY LOWER A
VERDICT, NEVER RAISE ONE.** That direction is asserted by the control below on a real block, not
merely claimed here.

## 4. THE READER DRIVEN IN THREE DIRECTIONS, ON L2's OWN REAL ARTIFACTS

`a3gc_l2r_reader_control.py`, md5 **`a5f80cc1e58194f5ab0571bc087333c6`**, exits 0 only if all
three hold, and **refuses (exit 2) rather than degrade**. Fixtures are **real DAFoam output from
L2's own case**, committed beside it — no synthetic stand-ins:

- `A3GC_L2R_FIXTURE_singlecorrector.log` — the verbatim final `Time` block of L2's graded
  `primal.log`.
- `A3GC_L2R_FIXTURE_multicorrector.log` — a real 2-step DAFoam run on **L2's own mesh** with
  `nNonOrthogonalCorrectors 2` (generated for this purpose; **1.90 core-min** at the first
  attempt plus **47.5 core-min** at the second, see §6).

**Measured results:**

| direction | fixture | amended reader | frozen reader |
|---|---|---|---|
| **1** honest read | single-corrector, 1 `p` line | **9.9386797550e-04** OK | 9.9386797550e-04 (rules coincide) |
| **3** first line | multi-corrector, 3 `p` lines | **1.0000000000e+00** OK (the first) | 1.6883840070e-02 (**the last — the defect**) |
| **2** planted forgery | plant **1.234e-09** in the LAST corrector | **1.0000000000e+00** — plant **NOT** returned | **1.2340000000e-09** — **PLANT READ BACK** |

**Direction 2 is the one that matters: it is the exact forgery that would have shipped.** The
frozen reader returns the plant; the amended reader does not. The control **also refuses if the
frozen reader FAILS to return the plant**, because a control that cannot demonstrate the failure
proves nothing about the fix (rule 3). Direction-of-change asserted: amended `1.0` >= frozen
`0.0169` on a real block — the amended reader read the harder number.

**Honest note on how close this came to being retracted.** An early read of the fixture log
showed one `p initRes` line and appeared to refute the whole defect. **It was a log read
mid-step, before the block had finished being written.** The completed blocks carry three. The
source reading was right and the hasty log read was wrong; it is recorded because the opposite
mistake — dropping a correct finding on a bad read — would have shipped the forgery.

## 5. THE REGISTERED PREDICTION — AND THE BAND I REFUSE IN ADVANCE TO RELABEL

**Graded quantity:** `p initRes` at the last printed step, read by `a3gc_grade_l2r.py` (first
match per block). All A3GC gates apply as written; `REG_INITRES_MAX` = 1e-06 unchanged.

**PREDICTION P-L2R-1.** **PASS** if `p` **and** all of `U0 U1 U2 he nuTilda` read **<= 1e-06** at
the last printed step, with G-PLAT satisfied. Mechanism confirmed: L2's stall was an un-iterated
non-orthogonal correction on a mesh past 70°, and iterating it closes a three-decade gap.

**FALSIFICATION P-L2R-1.** **GATE FAIL** if `p` stays **above 1e-06** while the last 10 graded
samples are flat to **<= 5.0 %** peak-to-peak. The repair then moved the plateau without reaching
the gate, and the residual floor is a property of this mesh, not of the corrector count.

**Between the two -> `NOT A RESULT`** (above 1e-06 and peak-to-peak above 5.0 %): not a plateau,
so it licenses neither statement.

**THE BAND I PRE-COMMIT ON, BECAUSE IT IS THE LIKELY OUTCOME AND THE EASIEST TO SOFTEN.**
A3GC's gate is **1e-06**; A2's floor was **1e-05**. **R3's own PASS value, 6.3233727e-06, would
FAIL A3GC's gate.** So a result anywhere in **1e-06 to 1e-05** would be a **two-decade improvement
on L2's 9.94e-04 AND A GATE FAIL.** **I register now that such a result will be reported as
`GATE FAIL`** — with the improvement stated as a number beside it, never as a softening adjective,
and never relabelled `GATE REACHED` or "progress". *Registered before the run precisely because
this is the outcome most likely to invite a kinder word afterwards.*

**Reported, never gated:** CD and CL against anchor 0.0229956 / 0.3131159; GAMG iterations per
corrector; the value the **frozen** reader would have returned on the same final block, printed
beside the graded one so the size of the averted error is visible.

## 6. COST — PRE-REGISTERED, AND IT IS LARGE

**Measured, not guessed.** The §4 fixture run gives the first real cost of correctors on this
mesh: **182.0 s/step at `nNonOrth 2`, np=8**, against L2's measured **17.9 s/step at `nNonOrth 0`**
— a **10.2x** escalation for **2** correctors, driven by the 28/105/157 GAMG iteration counts.

- `nNonOrth 12` is **13** pressure solves per step against 3. Scaling the measured per-solve cost
  and allowing later correctors to converge faster, the estimate is **400-900 s/step**, i.e.
  **6000 steps in roughly 28-62 days wall at np=8**, or **270,000-600,000 core-minutes**.
- **This is stated plainly because it is a planning fact, not a detail.** It is an order of
  magnitude beyond any A3GC run to date. **It does not stop the run** — Sanaa's directive #17,
  2026-09-12: no run is stopped by a time or budget cap — but the supervisor may wish to re-scope
  the rung on cost grounds, and **that is a decision to take now rather than on day 20.**
- The estimate is **soft**: both probe steps were cold-start, where GAMG counts are inflated.
  Actual-versus-predicted lands in `docs/COST_CALIBRATION.md` (rule 12), and the first 100 steps
  will give a firm rate that I will report against this figure rather than quietly supersede it.
- **Memory measured: 5.86 GiB at np=8** on L2's mesh. Containment is set at `--memory=9g
  --memory-swap=9g --oom-score-adj=500`. **Containment is not a cap** and is retained; an earlier
  5 GiB attempt was OOM-killed (rc 137) and **the containment worked exactly as intended — my
  probe died and every protected run survived, `OOMKilled=false` on all of them.**
- **NO CAP of any kind**: no `timeout`, no deadline, no core-minute guard, no watchdog able to
  signal. Ranks **8**, for parity with L2's decomposition; those 8 were freed by stopping L2.

## 7. COMPLETION

Graded only if rc=0, an `End` line, **last time == `endTime` = 6000**, fields present, and the
`endTime` fields newer than the case's own `0`. A run failing any clause is **NOT A RESULT**.
