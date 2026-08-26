# CURRICULUM D7F — PRE-REGISTRATION **v1.0. FROZEN. NOTHING HAS FIRED AT THIS COMMIT.**

**A NEW ITEM. It gives A3 an FD table at arm `O`'s endpoint by applying D4's LANDED `D4-DEF-4`
repair.** Date drafted: 2026-08-26. Lane: dafoam `lab-lane`, on the dafoam-supervisor's direction
of 2026-08-26.

> ## FROZEN AT THIS COMMIT. **NO CONTAINER HAS EVER BEEN CREATED FOR THIS ITEM** (§12).
>
> **v0.9 DRAFT was committed at `01e30d85` and is superseded by this version, not rewritten** — the
> draft's §13 named five blockers and this version discharges them one by one in §13. The freeze is
> this document's entire evidentiary content: it proves the gates, thresholds, caps and labels below
> could not have been chosen to fit an answer, because at this commit there is no answer.
>
> **The whole grading path is frozen WITH the document, in the same commit** (§14): the grader, the
> two repair instruments, the two acceptance instruments and the launcher, each by md5. **And the
> grader CHECKS ITS OWN CAPS AGAINST §7 OF THIS FILE and refuses on any disagreement** — the repair
> for `D7R-GRADER-DEF-6`, applied at its cause.

---

## 0. WHAT THIS ITEM DOES TO ITS PREDECESSOR: NOTHING

**`curriculum_D7R`'s document is SUPERSEDED, CITED, AND NEVER REWRITTEN** (`CLAUDE.md` rule 6). Its
verdicts stand exactly as recorded:

| D7R arm | verdict, standing |
|---|---|
| `P1` | **`PASS`** |
| `P2` | **`PASS`** — gates `H1` and `H2` both PASS |
| `O` | **`NOT A RESULT`** — the registered grader REFUSED, and band C missed at 30.402283 % against [3 %, 25 %] |
| `F-S`, `F-P` | **`BLOCKED`** |

**Nothing in this document alters, reinterprets or softens any of them, and nothing here reopens
D7R §11.**

### 0.1 What is CARRIED FORWARD — **RECORDED, NOT IMPORTED**

**A repeat is corroboration; a departure is a finding.** Each figure below is a D7R measurement this
item will encounter again, and **this item does not assume it:**

| carried | D7R's value | artifact |
|---|---|---|
| endpoint `CD` | `2.3048932443550496e-02` | `CURRICULUM-D7R-a3-m6-cdmin/O/opt_IPOPT.txt` |
| endpoint `CL` | `0.28761081` vs target `0.2876130251655752` | same; `O/d7_cl_target.json` |
| drag reduction | **30.402283 %** | same |
| `patchV[0]`, driver-scaled | **`29.160000000000004`** | `CURRICULUM-D7R-a3-m6-cdmin/D7R_DEF4_WITNESS.txt` |
| item spend | `P1` 0.733 + `P2` 62.733 + `O` 932.533 = **995.999** core-min | `CURRICULUM-D7R-a3-m6-cdmin/ledger.txt` |

**REGISTERED PREDICTION `C1`:** this item's arm `X` will read `patchV[0]` driver-scaled as
**`29.160000000000004`** from the FINAL `OptView.hst`. D7R's witness read that value from a
**partial, mid-run copy** at 22:48, ten minutes into a run that ended at 02:31. **A different value
from the final history is a FINDING about the witness, not a correction to it.**

---

## 1. THE DEFECT THIS ITEM EXISTS TO GET PAST, AND WHY IT IS SAFE TO GET PAST IT NOW

**`D7-DEF-4`**: OpenMDAO's `pyOptSparseDriver` applies each design variable's `scaler` **before**
pyOptSparse sees the problem; pyOptSparse's own scale is `1.0`; `OptView.hst` therefore holds
**driver-scaled** values; and `d7_extract_endpoint.py:40`'s `getValues(..., scale=False)` is
**INERT**. `d7_fd_endpoint.py:134-144` then reads `d7_endpoint_dvs.json` and applies those values as
**PHYSICAL** through `prob.set_val`. `shape`'s registered scaler is **10.0**.

**IT IS CONFIRMED BY MEASUREMENT, TWICE, AGAINST A PREDICTION FROZEN BEFORE THE ARTIFACT EXISTED**
(`5551db3d`, before any `OptView.hst` existed anywhere on this box — so it could only be confirmed or
refuted, never fitted):

* `patchV[0]` read **`29.160000000000004`**; registered prediction `291.6 × 0.1 = 29.16`. **The
  component is PINNED** (`d7_opt_runScript.py:241`, `lower[0] == upper[0] == U0`), so no optimiser
  can move it and its physical value is definitional.
* `patchV[1]` read **`0.30600000000000005`** `= 3.06 × 0.1` — **a second confirmation the prediction
  did not claim.**

**THE STANDING RULING IS THAT D7 INHERITS D4'S REPAIR RATHER THAN AUTHORING ITS OWN** (D7R §6): two
instruments would mean two chances to reintroduce a units error that is invisible to every count-,
plant- and order-based control in this family.

---

## 2. THE REPAIR — AND **THERE IS NO EXTRACTOR DIFF**

**D4's landed repair edits ZERO BYTES of any frozen file. That is its central property, not an
omission from it.** It is a **wrapper** that hashes the frozen extractor, imports it under a module
name that is not `__main__`, runs the frozen bytes, and corrects **downstream** of them.

**The supervisor asked for the extractor diff. The diff is empty, and the empty diff is the point:**

    $ diff cases/dafoam/ladder-a/A3/curriculum_D7/d7_extract_endpoint.py <the file arm X runs>
    (no output — byte-identical, md5 651d40c78cc52288a856934c108d1334, asserted at C1 before use)

**The reviewable artifacts are instead the two NEW instruments**, both committed with this document:

| instrument | ported from | what changed |
|---|---|---|
| `d7f_endpoint_locus.py` | `../../A2/curriculum_D4/d4_endpoint_locus.py` | **the parser and BOTH controls are carried byte-for-byte.** Mechanical renames only, plus the self-test's real-source plant retargeted to D7's file and D7's registered values |
| `d7f_endpoint_physical.py` | `../../A2/curriculum_D4/d4_endpoint_physical.py` | filenames `d4_*`→`d7_*`; the two frozen md5s replaced by **D7R §10's**; the authority paragraph extended |

**Retyping either file would have risked a transcription error in exactly the part that must not
change** — the same argument D7R §10 made for its launcher, and the reason both ports were produced
by verified token substitution with every substitution's occurrence count printed.

### 2.1 SATISFIABILITY, PROVEN BEFORE THE FREEZE AND NOT ASSERTED

**The single largest risk in the port was that D4's parser cannot read D7's registration.** It was
measured first, and it can:

    d7f_endpoint_locus.parse_registration("d7_opt_runScript.py")
      U0     291.6                                    READ from the source, not typed
      twist  lower -10.0  upper 10.0   scaler 0.1
      shape  lower  -1.0  upper  1.0   scaler 10.0
      patchV lower [291.6, 0.0] upper [291.6, 10.0]  scaler 0.1

**`patchV[0]` is pinned, so `CONTROL P` HAS A WITNESS and does not refuse itself** (L-302).

**`d7f_endpoint_locus.py --selftest`: 22 units, 22 PASS**, byte-identical under `python3 -O`;
**`ast.Assert` nodes: 0**. Among those 22, and these are the ones that matter:

* the **real D7-DEF-4 vector** makes **both** controls refuse — `CONTROL B` reporting
  `excess: 262.44` on `patchV[0]` (`291.6 − 29.16`);
* `mutant/pinned left driver-scaled (29.16 == THE MEASURED D7 WITNESS)` — **refuses**;
* a registration with **no** pinned component makes `CONTROL P` **refuse itself**;
* a pinned value off by `1e-13` does **not** fire, and off by `1e-9` **does** — the tolerance is a
  representation tolerance, four orders tighter than the smallest defect it exists to catch, and it
  cannot be tuned to admit one because no defect lives in that gap.

**`d7f_endpoint_physical.py`'s refusal chain was DRIVEN, not read:**

| condition driven | result |
|---|---|
| `--age-datum` omitted | **REFUSE** — "without it C3 cannot distinguish this arm's artifact from a stale one" |
| extractor absent | **REFUSE** `C1 ... absent` |
| extractor present but **not the frozen bytes** | **REFUSE**, with both md5s printed |
| both frozen instruments present | **C1 OK, C2 OK**, then the **frozen extractor's own** refusal fires: `D7_EXTRACT REFUSE history file OptView.hst absent` |

**The last row is the important one: the frozen bytes do the extraction and the frozen bytes do the
refusing.**

---

## 3. HOW `D7R-DEF-8` AND `D7R-DEF-9` ARE FIXED, PER ARTIFACT, BY ARM AND BY LINE

**An arm plan whose launcher cannot produce the artifacts its grader requires must not be frozen a
second time.** D7R's launcher invoked `d7_extract_endpoint.py` in **one place only — line 325,
inside the `F-S`/`F-P` branch that §6 blocked** — so arm `O` could never write
`d7_major_history.json` or `d7_endpoint_dvs.json`, and the grader refused at `G2`.

**REQUIRED-ARTIFACT TABLE. Every artifact the grading path reads, the arm that writes it, and the
line that writes it. A freeze is not legal until every cell below is filled and checked.**

| artifact | read by | written by arm | written at |
|---|---|---|---|
| `d7_endpoint_dvs_DRIVERSCALED.json` | `H3`, the record | **`X`** | `d7f_endpoint_physical.py` C4 |
| `d7_endpoint_dvs_PHYSICAL.json` | `H3`, `d7_fd_endpoint.py` | **`X`** | `d7f_endpoint_physical.py` C8 |
| `d7_endpoint_dvs.json` | `d7_fd_endpoint.py:134` | **`X`** | `d7f_endpoint_physical.py` C9 |
| `d7_major_history.json` | `G2` bands A/B, `G4` cross-check | **`X`** | the **frozen** `d7_extract_endpoint.py`, invoked at C3 — **VERIFIED: `d7_extract_endpoint.py:21` writes it** |
| `opt_IPOPT.txt`, `OptView.hst` | `G1` age guard, `G3`, `G4` | **inherited from D7R arm `O`** — gate `H4`, §5 | `d7f_run_arm.sh` `stage_endpoint()`, by md5 |
| `_final_CD` / `_final_CL` in the DV artifact | **`ACC-1`'s target cross-check** | **`X`** | the **frozen** extractor's `out["_final_" + short]`, `d7_extract_endpoint.py:68`, carried through the wrapper's C8 `dict(scaled_doc)` |
| `d7f_accept_primal.json` | `ACC-1` | **`ACC`** | `d7f_accept_primal.py`, rank 0, fsync |
| `d7f_accept_verdict.json` | the `F-S`/`F-P` launch gate (`LIMIT 1`) | **`ACC`** | `d7f_accept_compare.py --out` |
| `d7f_locus_gate.json` | `H3` | **`X`** | `d7f_endpoint_locus.py --gate` |
| `d7_fd_endpoint.json` | `G5` (the bright line), `G6`, `G6b`, `G7` | **`F-S`, `F-P`** | `d7_fd_endpoint.py` |
| `d7_decomp_A/B.json` | `G8` | **`P1`** | launcher `P1` branch |
| `d7_placement_rank*.json` | `G12` | every arm | launcher, each branch |
| `ledger.txt` | `G1`, `G9`, `G10`, `G11`, `G12` | launcher | every arm |

**`D7R-DEF-9` IS FIXED BY ARMING `F-S` AND `F-P`.** `map_verdict` hard-fails `G6`/`G6b`/`G7` on
**absent** FD artifacts; D7F's whole purpose is to produce them, so the absence that made D7R's
registered outcome unreachable does not arise. **`G9` — two rows carrying DISTINCT IDWarp `.so`
md5s — becomes reachable for the first time in this family's A3 line**, because `F-P` is armed.

**FALSIFIER `F-SAT`, registered here:** if, at the moment of freezing, any cell of the table above
is unfilled, **THE ITEM IS NOT FROZEN.** This is checked by re-reading the launcher, not by
recalling it. **DISCHARGED AT THIS COMMIT: every cell is filled and the launcher was re-read to fill
it.**

> **AND THE TABLE EARNED ITS KEEP BEFORE THE FREEZE, WHICH IS THE POINT OF HAVING IT.** While
> filling the `_final_CD` row I could not find that string anywhere in `d7_extract_endpoint.py` and
> was one step from recording that `ACC-1` could never grade — **the same `D7R-DEF-8` shape,
> reproduced inside its own repair.** It resolves the safe way: line 68 builds the key by
> *concatenation*, `out["_final_" + short]` for `short in ("CD", "CL")`, so a literal search for
> `_final_CD` finds nothing while the key is written on every run. **D4's own landed acceptance
> artifact carries `endpoint_final_CD_from_history: 0.021125978108239574`, which is D4's `CD_OPT` to
> all digits — the chain is not merely plausible, it has run once.** Recorded because the near-miss
> is the evidence that the table is a check and not a formality.

---

## 4. BAND C DOES NOT ARISE IN THIS ITEM, AND I AM NOT REGISTERING A NEW ONE

**The supervisor put this as a live question and offered the honest exit. I am taking it.**

**I cannot justify a drag-reduction band from the physics and the case without pointing at
30.4 %, and I am not going to pretend otherwise.** D7's [3 %, 25 %] was reasoned from a comparison
with D4's A2 band; nothing I can say about M 0.84 shock-dominated transonic drag on a 42,120-cell
ONERA M6 predicts a *ceiling* to better than a factor of two. Any number I proposed today would be
chosen by somebody who already knows the answer, and **`CLAUDE.md` rule 2 exists precisely because
that choice is undetectable afterwards.**

**IT DOES NOT MATTER, BECAUSE D7F RUNS NO OPTIMISER.** This item takes arm `O`'s endpoint as given
and measures a **gradient** there. **It produces no drag reduction of its own, so there is nothing
for band C to gate.**

* **The 30.402283 % is carried as a RECORDED D7R number, REPORTED AND NOT GATED** (§0.1). No gate in
  this item reads it, and **no verdict of this item may be stated in terms of it.**
* **The bright line here is `G5`** — endpoint FD versus adjoint, band D, **5.0 % per component and
  5.0 % aggregate**, inherited unchanged and **not re-derived by a lane that has seen an answer**,
  because **no D7 FD number exists yet in any direction.** That band was frozen at `0e229a0a` before
  any FD artifact existed and it is the one band in this family a re-registration cannot be accused
  of fitting.

---

## 5. GATES

`G1`–`G13` are graded by **`d7f_grade.py`**, this item's own port, md5
**`923662ef398ca229cc3734699670418a`** (§14) — **not** D7's blob, and §6 says exactly what changed
and why. **`G10` IS SPLIT INTO TWO LIMBS AND THE SPLIT IS REGISTERED HERE, BEFORE COMPUTE:**

| limb | what it checks | disposition |
|---|---|---|
| **`G10` LIMB 1** | **`enforced cap == REGISTERED cap`, per arm, READ BACK OUT OF THE LEDGER THE LAUNCHER WROTE**, never from the launcher's claim | **GATES.** It is an integrity check that the launcher enforced what this document registered — the `D7R-DEF-8` / D12R class, a launcher and a document disagreeing, which bit this family three times in one night. `g10_caps`'s `pass` is this limb **and this limb alone** |
| **`G10` LIMB 2** | **`actual ≤ cap`** | **REPORTED, GATES NOTHING.** Under §7's reporting-cap design this limb **is** the runaway guard, and a runaway guard that hard-fails a grade contradicts its own purpose. Precedent for registering a reported-not-gating channel in advance: D4's `ACC-2` (*"REPORTED, GATES NOTHING, exactly as registered"*) and D12R2's steady-stage step proxy (*"recorded and REPORTED, never gated"*) |

> **NON-GATING IS NOT NON-REPORTING, AND THAT IS THE HAZARD ATTACHED TO IT.** *A printed discrepancy
> labelled "diagnostic only" is worse than one never computed.* **Every limb-2 crossing is reported
> with its number in core-minutes AND in derived dollars, in the RESULTS headline and in the cost
> calibration row — never in a footnote and never as a bare "within tolerance".** The grader emits it
> under the key `LIMB2_REPORTED_NOT_GATING__CARRY_INTO_HEADLINE`, so a reader who lifts `G10`
> cannot lift it without seeing the crossing and a lane that omits it has dropped a key whose own
> name says it may not be dropped. **A quiet overrun is a defect.**

Three gates are added:

| gate | threshold | refusal |
|---|---|---|
| **`H3`** | the published `d7_endpoint_dvs_PHYSICAL.json` re-passes `CONTROL P` and `CONTROL B` **at grading time, re-read from disk** — never on the producer's say-so | `d7f_endpoint_locus.py --gate` refuses; the FD table is at the wrong design point |
| **`H4`** | the `OptView.hst` and `opt_IPOPT.txt` arm `X` reads were produced by **D7R arm `O`**, identified by md5 against `CURRICULUM-D7R-a3-m6-cdmin/O/`, and are **strictly older** than this item's launch datum while every artifact **derived** from them is strictly newer | `ENDPOINT_PROVENANCE` — refuses an unattributed or re-run endpoint. **The age guard runs in BOTH directions here and that is deliberate: an inherited input must be OLD, a produced output must be NEW, and one rule cannot say both** |
| **`ACC-1`** | **`LIMIT 1`.** One primal at the corrected physical design point reproduces arm `O`'s IPOPT objective `CD = 2.3048932443550496e-02` to **≤ 1e-3 relative** | the repair is **NOT FROZEN** and no FD number from it is graded. D4's own ACC-1 measured `2.34e-4` against this same band with a planted-zero control that PASSED |

**`ACC-1` IS A PRECONDITION OF THE FREEZE OF THE REPAIR, NOT A FOLLOW-UP.** Two controls that grade
nothing say the corrected point is *self-consistent with the registration*. **Only a solve says it is
the optimum.** **The launcher enforces it mechanically**: arms `F-S` and `F-P` refuse to start unless
`ACC/d7f_accept_verdict.json` exists and reads `"verdict": "PASS"`.

**GATE `H1` IS NOT CARRIED FORWARD, AND THAT IS A DISCLOSURE, NOT AN OMISSION.** D7R needed `H1`
because a colouring cache built by one arm was inherited by another and the `.bin.info` sidecar could
not refuse a foreign one. **This item inherits no colouring: `F-S` and `F-P` each BUILD FRESH, and
§7 prices the build into BOTH of them at 24.2 core-min each.** The price of dropping the gate is
24.2 core-min on arm `F-P`; the gain is one whole class of provenance risk removed. **A gate dropped
is disclosed; a gate quietly omitted is a defect.**

---

## 6. THE THREE INHERITED GRADER DEFECTS — **REPAIRED AT THEIR CAUSE, NOT DECLARED AWAY**

**D7R §5 claimed its gates were "inherited unchanged". That was true of the logic and FALSE of three
thresholds, and this item does not repeat the claim — it ports the instrument and fixes it.**

**The v0.9 draft asked the supervisor to assent to declaring `G10` non-binding. THE SUPERVISOR
REFUSED THE DECLARATION AS FRAMED AND WAS RIGHT TO** (ruling 3, 2026-08-26): *"declaring a gate
non-binding because your instrument carries the wrong numbers is repairing the RECORD instead of the
INSTRUMENT, and it would trade a five-minute fix for a permanent blind spot."* **This item is a new
item porting a new instrument; no frozen file stood in the way; the remedy for a wrong constant is
the right constant.**

| id | what it was | what this item did |
|---|---|---|
| **`D7R-GRADER-DEF-6`** | the ported grader hard-coded **D7's** `CAPS = {P1 8.0, P2 60.0, O 600.0, …}` and `ITEM_CEILING = 928.0` against D7R's registered 900.0 and none, so `g10_caps` read `overrun_core_min: 332.533` against a threshold that was never D7R's | **REPAIRED AT ITS CAUSE.** `d7f_grade.py` carries **this item's** `CAPS`, `CEILINGS` and `PREDICTED`, and `ITEM_CEILING_CORE_MIN` is **derived by `sum(CEILINGS.values())`, not typed.** And they are **CHECKED, NOT COPIED**: `assert_caps_against_document()` parses **§7 of this file** and REFUSES on any disagreement. **Measured at the freeze: 15 values checked (5 arms × cap, ceiling, prediction), all agreeing.** Driven both ways — moving one cap by 1.0 in a copy of this document makes it refuse and name the arm and the field; an unparseable document makes it refuse by count (L-302). An arm with no registered cap **refuses** rather than being skipped |
| **`D7R-GRADER-DEF-7`** | `g1_completion`'s docstring named three clauses and implemented two; in that whole 74,338-byte file the string `End` occurred **exactly once — inside the docstring that claimed the check** | **REPAIRED.** The terminal clause is now executable: it reads the **producer's own log FILE** — not the ledger's summary of it — and requires an `End` line **and** the `.log.ok.<stamp>` marker. **Driven in both directions in the selftest**, each mutant first asserting *that the mutation applied* so no unit can pass vacuously: marker removed → fails; `End` removed → fails; log absent → fails and is **not read as clean**; restored → passes again, so the clause is not a one-way switch. **`scripts/check_docstring_clauses.py` (L-335) reports `d7f_grade.py:g1_completion` as `RC_ZERO OK / LOG_TERMINAL OK / AGE_GUARD OK`, 0 alibis — against `d7_grade.py:g1_completion`'s 1 alibi, run side by side** |
| **`D7R-GRADER-DEF-5`** | the `--selftest` exit contract the file documents ("exit 3, used by nothing else") is not the one it has: success returns **0**, the same code a clean grade returns | **NOT repaired, and handled instead — because changing an exit contract is the kind of change that breaks a caller silently.** The selftest's result is read from its **stdout** `D7F_SELFTEST units=… passed=… failed=…` line and from the **absence** of an `--out` file, **never from its exit code**, and this record says so before compute so no reader of it infers a grade from an exit 0 |
| **`D7F-ACC-DEF-1`** | **found while porting, and it is a `-O` exposure**: D4's landed `d4_accept_compare.py:199` guards its verdict vocabulary with a bare `assert verdict in VOCAB`, and **`python3 -O` deletes it** — so under `-O` nothing stands between that instrument and a token outside `CLAUDE.md` rule 1's fixed vocabulary | **REPAIRED IN THIS PORT ONLY.** `d7f_accept_compare.py` raises a real refusal instead. **D4's frozen file is NOT edited** and the finding is reported to the supervisor. `ast.Assert` nodes across all five of this item's new instruments: **0** |

## 7. ARMS, CAPS, CEILINGS AND COST — priced from **D7R's own measured arms**

| arm | task | row | **prediction (core-min)** | **CAP** | **CEILING** |
|---|---|---|---|---|---|
| `P1` | decomposition determinism ×2 + placement | SHIPPED | **0.75** | 8.0 | 32.0 |
| `X` | the `D7-DEF-4` repair: frozen extractor + `CONTROL P`/`B` + PHYSICAL artifact | SHIPPED | **2.0** | 15.0 | 60.0 |
| `ACC` | **`LIMIT 1`** — one primal at the corrected point | SHIPPED | **25.0** | 60.0 | 240.0 |
| `F-S` | endpoint FD, 5 components | SHIPPED | **485.0** | 750.0 | 3000.0 |
| `F-P` | endpoint FD, 5 components | **PATCHED** | **485.0** | 750.0 | 3000.0 |
| | | | **ITEM 997.75** | | |

**EVERY TERM IS A D7R MEASUREMENT, AND THE ONE PLACE THE LOGS CANNOT ANSWER IS NAMED AS SUCH.**

* `P1` **0.75** — D7R `P1` measured **0.733**.
* `X` **2.0** — the D7R `D7-DEF-4` witness probe was the same shape of container and **its cost was
  never recorded**; 2.0 is a **guess bounded by `P1`'s measured 0.733 and by `X` doing strictly more
  I/O and no solve.** It is labelled a guess, not a measurement, and the cap is 7.5× it.
* `ACC` **25.0** — one converged primal. See the primal basis below.
* `F-S`/`F-P` **485.0** = **22 primals × 20.27** + **24.2 colouring** + **14.6 cold `compute_totals`**.

> **THE PRIMAL COST IS AN UPPER BOUND AND IS REGISTERED AS ONE.** D7R's logs **cannot separate**
> primal from adjoint: arm `O` interleaves them inside single OpenFOAM runs. What IS measurable is
> that arm `O` spent **932.533 core-min** delivering **46 objective evaluations** and 31 gradient
> evaluations (`O/opt_IPOPT.txt` summary block). **Charging the WHOLE arm to its objective
> evaluations alone gives 20.27 core-min/primal, which necessarily OVERSTATES a primal**, because it
> bills the adjoints to it. **This item registers the overstatement rather than a decomposition it
> cannot measure**, and the calibration row will report the ratio honestly as a deliberate
> over-prediction if it comes in low.
>
> **The colouring is priced with a number, per `C-89`: 24.2 core-min**, measured from **D7R's own**
> `P2` log — `Calculating dRdW Coloring... 34.74 s` → `Completed! 397.31 s`, 362.57 s × 4 ÷ 60 =
> **24.17**. D7R registered 24.43 from D7's log and measured 24.17 in its own: **ratio 0.99.**
> **This item BUILDS FRESH** (D7R §R3's ruling, unchanged: the `.bin.info` sidecar carries no mesh
> identity, so no cache control that can refuse is designable).
>
> **The 14.6 cold `compute_totals`** is D7R §4's adjoint term, which was registered there as a
> **FLOOR** and is still one.

**Cost basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Item **997.75** core-min → **$0.8531 DERIVED**.

**THE CAP REPORTS AND THE CEILING STOPS** — D7R §R1's design, carried forward unchanged, **and the
charter question it raises is referred to Sanaa's desk and is NOT answered by this document.** Until
it is ruled, this item registers both thresholds and the record names which one acted.

---

## 8. TOOLCHAIN — two rows, by digest, never by tag

| row | image | digest | `libidwarp.so` md5 |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` |

**Both digests were RE-MEASURED LIVE on 2026-08-26** by `docker inspect` and landed in
`docs/dafoam/TOOLCHAIN_INVENTORY.md` Amendment 1 — which, until that amendment, **named
`dafoam-idwarp-rot:v1` nowhere at all.** `DAFOAM_CHARTER.md` §11: the hash is the identity; **both
libraries report IDWarp `2.6.2` and both are 491,344 bytes**, so the version string discriminates
nothing.

**`F-P` IS ARMED, SO THIS ITEM CAN BE A TWO-ROW DAFOAM VERDICT — AND IT IS NOT ONE UNTIL `F-P`
RETURNS `rc=0` AND `G9` SEES TWO DISTINCT `.so` md5s.** If `F-P` is blocked or fails, **the record
says SHIPPED-only and says so in its headline**, exactly as D7R's did.

---

## 9. STRICT COMPLETION, THE AGE GUARD, AND THE COLD GUARD

`CLAUDE.md` rule 4: `rc = 0`; an `End` line; the `.log.ok.<stamp>` marker; fields present; every
**produced** artifact strictly newer than the arm's launch datum. **A guard refuses a case whose arm
directory already holds a time directory, `processor*`, `reports/`, an `OptView.hst`, a colouring
cache or any `d7_endpoint_dvs*.json`. A guard that refuses is the guard working and is never
disabled to get past it.**

**`H4`'s inherited-input clause runs the age comparison the other way** (§5) and the two directions
are registered separately so neither is mistaken for the other.

---

## 10. WHAT WOULD MAKE THIS ITEM A FAILURE — registered in advance

* **`ACC-1` misses its 1e-3 band** → the repair is **NOT FROZEN**, no FD number is graded, and that
  is a finding about the reconstruction, recorded before any regrade.
* **`CONTROL P` or `CONTROL B` refuses on the real vector** → the endpoint is not where the
  registration says it is; **`NOT A RESULT`**, and the FD arms do not run.
* **`G5` fails band D** → **`GATE FAIL`**, reported as a miss and **never re-banded**.
* **Any `G8` failure** → every np=4 number in this item is **`NOT A RESULT`**.
* **`F-P` blocked or `rc≠0`** → **not a two-row verdict**, said in the headline.
* **The grader refuses again on real artifacts** → a finding **before** any regrade, and §3's table
  is what will have been wrong.
* **`F-XCHK`, registered because it cannot be tested before compute.** `d7f_accept_compare.py`
  cross-checks its typed `CD_OPT` against the `_final_CD` the frozen extractor selected, at `1e-15`
  relative, and **refuses** on a mismatch — so a typo in the comparator cannot pass silently. **The
  extractor takes the LAST row of `OptView.hst`, and D7R's arm `O` log prints CL values from
  post-optimisation evaluations AFTER the IPOPT summary.** If the history's last row is one of those
  rather than the final major, `_final_CD` will not equal `2.3048932443550496e-02` and **`ACC-1`
  will refuse.** That refusal is **a finding about which row the extractor selects**, recorded
  before any regrade, and **the tolerance is not widened to admit it.** It cannot be settled before
  compute because reading `OptView.hst` requires `pyoptsparse`, which lives only in the container.

## 11. PREDICTIONS, REGISTERED BEFORE COMPUTE

| id | prediction |
|---|---|
| `C1` | arm `X` reads `patchV[0]` driver-scaled as **`29.160000000000004`** from the FINAL history |
| `C2` | after descaling, `patchV[0]` reconstructs to **`291.6`** inside `1e-12` relative and `CONTROL P` passes |
| `C3` | **`CONTROL B` will find `shape` components outside `[-1, 1]` in the DRIVER-SCALED vector** — D4 measured 62 of 96. **A driver-scaled vector with every `shape` component inside its bounds would mean the endpoint barely moved, and that would contradict a 30.4 % drag reduction** |
| `C4` | `ACC-1` lands inside `1e-3`; D4's landed at `2.34e-4` |
| `C5` | `G5` **PASSES** band D on at least 4 of 5 components. **Registered as UNLIKELY-to-be-clean on `shape[115]`**, which A3 rung 2 measured at `0.0172 % → 0.1586 %` and rung 1 at `0.9273 % → 0.3826 %` — **the same component has moved in opposite directions on two rungs of this ladder** |
| `C6` | `F-S` and `F-P` return **DISTINCT** `.so` md5s and `G9` passes for the first time on this A3 line |

## 12. CONDITION AT THE FREEZE COMMIT, RE-TAKEN HERE AND NOT CARRIED FROM THE DRAFT

**Re-taken at 2026-08-26T03:53:44Z, not copied from v0.9** — a condition check carried forward
from a draft is a memory of a check, not a check.

| check | command | reading |
|---|---|---|
| run root `/home/ubuntu/certonomous-runs/CURRICULUM-D7F-a3-m6-fd` | `ls -d …CURRICULUM-D7F* \| wc -l` | **0** — does not exist |
| containers named `d7f_` | `sudo -n docker ps -a --filter name=d7f_` | **0** — none has ever been created |
| arm directories `P1 X ACC F-S F-P` | — | **0 of 5** |
| any `*.log` under the run root | — | **0**, there being no run root |

---

## 13. THE FIVE v0.9 BLOCKERS, DISCHARGED ONE BY ONE

| # | v0.9 blocker | disposition at this commit |
|---|---|---|
| 1 | `d7f_accept_primal.py` / `d7f_accept_compare.py` NOT WRITTEN — `LIMIT 1` is a precondition of the freeze | **WRITTEN AND DRIVEN.** Ports of D4's landed pair. The comparator was driven on four fixtures: a point 2.0e-4 from arm `O`'s objective → **`PASS`**; one 90 % away → **`GATE FAIL`**; D4's DV counts → **REFUSE `count`**; a falsified cross-check target → **REFUSE `target_crosscheck`**. Identical under `python3 -O`. **The planted-zero control PASSED on every graded fixture** — the reader is shown able to see a non-zero before any zero is believed (`CLAUDE.md` rule 3) |
| 2 | `d7f_run_arm.sh` NOT WRITTEN | **WRITTEN**, `bash -n` clean, §3's table wired arm by arm, §7's caps in its own table, gate `H4` by md5, the cold guard extended to refuse a stale `d7_endpoint_dvs*.json` or acceptance artifact, and **`F-S`/`F-P` refusing to start unless `ACC-1` reads `PASS`** |
| 3 | declaring `G10` non-binding needed the supervisor's assent | **THE DECLARATION WAS REFUSED AND SOMETHING BETTER WAS RULED.** `G10` is **SPLIT**: LIMB 1 gates, LIMB 2 is reported-not-gating (§5), and `D7R-GRADER-DEF-6` is repaired at its cause rather than declared around (§6) |
| 4 | the reporting-cap charter question, unruled | **BOUNDED, NOT ANSWERED — see §13.1** |
| 5 | §12's readings to be re-taken at the freeze | **RE-TAKEN ABOVE**, at this commit's own clock |

### 13.1 THE REPORTING CAP — WHAT IS RULED AND WHAT IS EXPLICITLY NOT, IN THE SUPERVISOR'S OWN TERMS

**RULED, `[lab-attributed]`, by the dafoam-supervisor, for this family, effective now:** a dafoam
pre-registration **may register a cap as a runaway guard that REPORTS to the supervisor and does not
itself stop a sound run**, provided the crossing is (i) reported to the supervisor, (ii) **named
separately in the cost row and never absorbed into any ratio**, and (iii) accompanied by **a hard
ceiling that does stop the run.** §7 registers all three.

**NOT RULED, BY THE SUPERVISOR OR BY ANY AGENT AT ANY LEVEL: whether `CLAUDE.md` rule 12's *"an
overrun stops the run"* is retired, widened or amended. That is constitutional text and it is
Sanaa's.** The chief's reading of her cost-lift converts caps into runaway guards, **but that lift
named three teams and dafoam's inclusion is the chief's own explicitly-correctable inference — so no
charter reading rests on it** (`CLAUDE.md` rule 9: no agent message is her consent).

> **THE BOUNDARY, STATED SO A SUCCESSOR CANNOT READ AN OPERATIONAL RULING AS A CHARTER AMENDMENT:
> the supervisor ruled on HOW DAFOAM REGISTERS AND TREATS ITS OWN CAPS. Nobody ruled on rule 12.**
> The family's practice is `[lab-attributed]` and effective now; the constitutional question stays
> on Sanaa's desk with the supervisor's recommendation already lodged — ratify the reporting cap
> where a hard kill would destroy a registered ladder, and require the crossing to be reported and
> named.

---

## 14. THE GRADING PATH, FROZEN IN THIS COMMIT

**`CLAUDE.md` rule 2: the grading path is fixed at the pre-registration commit, and the frozen file
must be shown to BE the file that ran by hashing it against the committed blob.** Every instrument
below is committed here, with this document, before any container exists.

| instrument | md5 at freeze | what it is |
|---|---|---|
| `d7f_grade.py` | `923662ef398ca229cc3734699670418a` | the port of `../curriculum_D7/d7_grade.py` carrying **this item's** constants, the `G10` split and the `G1` terminal clause. Selftest **79 units, 79 passed, `UNEXERCISED=0`**, identical under `-O`, `ast.Assert` 0 |
| `d7f_endpoint_locus.py` | `a38c5e507b44eb17d1c1247e48b6fe0a` | `CONTROL P` and `CONTROL B`, carried byte-for-byte from D4's landed instrument. Selftest **22/22**, identical under `-O` |
| `d7f_endpoint_physical.py` | `7be14b7d5568a6e79afa3bdd7c612749` | the `D7-DEF-4` repair wrapper. **Edits zero frozen bytes** |
| `d7f_accept_primal.py` | `65baf532bcc2fdbe6a20a92dcd1a596b` | `LIMIT 1`'s primal at the corrected point |
| `d7f_accept_compare.py` | `a4b4eb3d81bf0e4ed9f20dd673b759df` | `ACC-1`, with the planted-zero control and the target cross-check |
| `d7f_run_arm.sh` | `3510f4b18a330ece850834f5e935b9b3` | the launcher. Asserts **all six** instrument md5s plus the two endpoint md5s before every launch and aborts on a mismatch |

**INHERITED AND ASSERTED, NEVER COPIED** — the launcher re-checks each against the committed blob
before every launch:

| inherited instrument | md5 | source |
|---|---|---|
| `d7_opt_runScript.py` | `e43902ed2cfc99022c6e21e075f88695` | `../curriculum_D7/` |
| `d7_extract_endpoint.py` | `651d40c78cc52288a856934c108d1334` | `../curriculum_D7/` — **carries `D7-DEF-4`, and is corrected DOWNSTREAM, never edited** |
| `d7_fd_endpoint.py` | `92b3fa8d20a41da029590ed3bdde4203` | `../curriculum_D7/` |

**GATE `H4`'s endpoint identifiers**, from D7R arm `O`:

| artifact | md5 |
|---|---|
| `OptView.hst` | `ed90aa4f0a38b2fadf93cdc0b601ec41` |
| `opt_IPOPT.txt` | `175969fb3e4fa609af708f4f49aa4a6a` |

**FROZEN. Nothing fires before this document and every instrument above are committed.**

---

## AMENDMENT 1 — 2026-08-26T03:58:27Z. **PRE-COMPUTE.** THE LAUNCHER TAKES THE `G-ROOT` GUARD, AND I INHERITED THE DEFECT THE RULE WAS ISSUED ABOUT.

**`CLAUDE.md` rule 2: before first compute, amendments are legal AND MUST STATE THE CONDITION AND
HOW IT WAS CHECKED.**

### A1.1 The condition, and how it was checked — not asserted

**NO COMPUTE HAS OCCURRED FOR THIS ITEM.** Checked at this amendment, by name and by command:

| check | reading |
|---|---|
| `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-D7F-a3-m6-fd` — **the run directory that does not exist** | **0** |
| `sudo -n docker ps -a --filter name=d7f_` | **0** containers, none ever created |
| arm directories `P1 X ACC F-S F-P` | **0 of 5**, there being no run root to hold them |

**This amendment therefore adds a guard and moves NOTHING: no gate, no threshold, no cap, no label,
and no arm.** §7's cap table is byte-unchanged, and `d7f_grade.py`'s
`assert_caps_against_document()` still reads **15 values, all agreeing**.

### A1.2 What was wrong, stated against myself

**The dafoam standing rule `G-ROOT` was issued at `217d4666`, BEFORE this item's freeze commit
`c4dbb33f`, and it names D7F: *"D7F takes the guard from birth."* I froze the launcher without it.**

`d7f_run_arm.sh` is a port of `d7r_run_arm.sh`, and **it inherited the exact defect the rule was
issued about**: `sudo -n rm -rf "$WORK"` with the `G-COLD` check **fourteen lines below it**.

> **A GUARD PLACED AFTER THE DELETION IS DECORATION, AND IT IS WORSE THAN A MISSING ONE: a missing
> guard is visible to anyone who looks, while a guard that runs after the act it guards READS AS
> PROTECTION TO EVERY SUBSEQUENT REVIEWER.** I ported it, hashed it, `bash -n`-ed it, wrote a §3
> table about which arm writes which artifact — and did not look at where the deletion sat. **The
> supervisor found it in a peer's launcher and the rule caught mine.**

### A1.3 What the guard is, and it was DRIVEN, not asserted

**PLACEMENT IS PART OF THE GUARD**, so the placement is the first thing recorded:

| line | what sits there |
|---|---|
| **50–89** | `G-ROOT.1` `.2` `.3` |
| **193–209** | `G-ROOT.4` — at the first point `$ARM` is known |
| **245** | the frozen-instrument md5 assertions |
| **≈300** | `sudo -n rm -rf "$WORK"` — **the destructive act, below every guard above** |

| limb | what it refuses | DRIVEN |
|---|---|---|
| `G-ROOT.1` | `BASE` that is not this item's registered root, under `realpath -m` | **fires** on D7R, D7, D4, D4-SHIPPED, D12R2 — **and on a trailing slash and on a `..` walk through this item's own root** |
| `G-ROOT.2` | a `BASE` resolving to a NAMED forbidden root, so the abort says whose evidence it protected | **fires**, naming the root and quoting *"D7R arm O alone is 932.533 core-min of graded output"*. **UNREACHABLE while `G-ROOT.1` stands — it is defence in depth and it was driven in a sacrificial copy with `REGISTERED_BASE` overridden. That is stated rather than left as a claim that it "was demonstrated"** |
| `G-ROOT.3` | a ledger carrying another item's rows | present; not driven, and said so |
| `G-ROOT.4` | **an arm that ALREADY HAS a ledger row or a success marker** — the limb that protects THIS item from itself | **fires on both**, and **two CONTROLS show it does NOT fire when it should not**: a clean root passes it, and arm `X` is not blocked by `P1`'s row |

**Census before and after driving all six refusal probes against the real roots:**
D7R **2,194 files → 2,194**; D4 **21,004 → 21,004**. **Nothing was deleted.**
*(D12R2 read 39,864 → 39,959 across the same window — **that is a peer's live container writing, not
this guard**, and it is named rather than left to read as damage.)*

**Backticks on executable lines: 0** — the D4-SHIPPED catch, because a backtick inside a
double-quoted `echo` is command-substituted, so a guard's own FAILURE PATH can execute the thing it
refuses, on the one path nobody exercises.

### A1.4 The struck row

**§14's `d7f_run_arm.sh` row is STRUCK, not rewritten** (`CLAUDE.md` rule 6). The launcher's md5 at
the freeze was `3510f4b18a330ece850834f5e935b9b3`; **at this amendment it is
`be99327e29e0dc6689fe57dd4053763b`**. Every other row of §14 is unchanged, and the five other instruments are
byte-identical to the freeze.

**STILL FROZEN. STILL NOTHING FIRED.**
