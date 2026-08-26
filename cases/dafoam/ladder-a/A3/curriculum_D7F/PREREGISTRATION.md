# CURRICULUM D7F — PRE-REGISTRATION **v0.9 DRAFT. NOT FROZEN. NOTHING HAS FIRED.**

**A NEW ITEM. It gives A3 an FD table at arm `O`'s endpoint by applying D4's LANDED `D4-DEF-4`
repair.** Date drafted: 2026-08-26. Lane: dafoam `lab-lane`, on the dafoam-supervisor's direction
of 2026-08-26.

> ## THIS DOCUMENT IS **NOT FROZEN** AND **NO CONTAINER HAS STARTED.**
>
> It is committed **before** compute so the supervisor can read the plan and the instrument set as a
> diff, which is their non-delegable check. **§13 names exactly what is missing, and the item may not
> be frozen or fired until those items exist and this line is struck.** A lane does not freeze an
> item whose `LIMIT 1` precondition instruments have not been written.

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
| `d7_major_history.json` | `G2` bands A/B, `G4` cross-check | **`X`** | the **frozen** `d7_extract_endpoint.py`, invoked at C3 |
| `opt_IPOPT.txt`, `OptView.hst` | `G1` age guard, `G3`, `G4` | **inherited from D7R arm `O`** — gate `H4`, §5 | staged, never re-run |
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
recalling it.

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

`G1`–`G13` are graded by the committed `../curriculum_D7/d7_grade.py`, md5
**`10eb6d0928addc56272854f017e01538`** — **subject to §6's KNOWN LIMITATIONS, which are declared
before compute rather than discovered after it.** Three gates are added:

| gate | threshold | refusal |
|---|---|---|
| **`H3`** | the published `d7_endpoint_dvs_PHYSICAL.json` re-passes `CONTROL P` and `CONTROL B` **at grading time, re-read from disk** — never on the producer's say-so | `d7f_endpoint_locus.py --gate` refuses; the FD table is at the wrong design point |
| **`H4`** | the `OptView.hst` and `opt_IPOPT.txt` arm `X` reads were produced by **D7R arm `O`**, identified by md5 against `CURRICULUM-D7R-a3-m6-cdmin/O/`, and are **strictly older** than this item's launch datum while every artifact **derived** from them is strictly newer | `ENDPOINT_PROVENANCE` — refuses an unattributed or re-run endpoint. **The age guard runs in BOTH directions here and that is deliberate: an inherited input must be OLD, a produced output must be NEW, and one rule cannot say both** |
| **`ACC-1`** | **`LIMIT 1`.** One primal at the corrected physical design point reproduces arm `O`'s IPOPT objective `CD = 2.3048932443550496e-02` to **≤ 1e-3 relative** | the repair is **NOT FROZEN** and no FD number from it is graded. D4's own ACC-1 measured `2.34e-4` against this same band with a planted-zero control that PASSED |

**`ACC-1` IS A PRECONDITION OF THE FREEZE, NOT A FOLLOW-UP.** Two controls that grade nothing say the
corrected point is *self-consistent with the registration*. **Only a solve says it is the optimum.**

---

## 6. KNOWN INSTRUMENT LIMITATIONS, DECLARED BEFORE COMPUTE

**D7R §5 claimed gates were "inherited unchanged". That was true of the logic and FALSE of three
thresholds, and this item does not repeat the claim.**

| id | what | how this item handles it |
|---|---|---|
| **`D7R-GRADER-DEF-6`** | the frozen grader hard-codes **D7's** `CAPS = {P1 8.0, P2 60.0, O 600.0, F-S 130.0, F-P 130.0}` and `ITEM_CEILING_CORE_MIN = 928.0` | **`G10` IS DECLARED NON-BINDING FOR THIS ITEM IN ADVANCE.** Its `cap_matches_registered` limb compares against D7's numbers and **will read false**; that reading is an instrument-provenance artifact and **is not a budget finding**. The binding caps are §7's, checked by the launcher against the ledger it wrote. `G10` is **not** a hard gate in `map_verdict`, so nothing rests on it |
| **`D7R-GRADER-DEF-7`** | `g1_completion`'s docstring names three clauses and implements two — no terminal-log check exists in it | **`G1` is recorded `NOT ESTABLISHED` as named**, one-way (it may only remove a `PASS`). The terminal clause is enforced **by the launcher** — `rc`, an `End` line, and a `.log.ok.<stamp>` marker — and the record says which instrument did it. Detectable henceforth by `scripts/check_docstring_clauses.py` (**L-335**) |
| **`D7R-GRADER-DEF-5`** | the `--selftest` exit contract the file documents ("exit 3, used by nothing else") is not the one it has: success returns **0**, the same code a clean grade returns | **the selftest's result is read from its STDOUT `D7_SELFTEST units=… passed=… failed=…` line and from the ABSENCE of an `--out` file, never from its exit code.** Registered here so no reader of this item's record infers a grade from an exit 0 |
| **`D7R-DEF-8`** | the launcher/grader artifact mismatch | fixed by §3's table, checked cell by cell before the freeze |

---

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

## 11. PREDICTIONS, REGISTERED BEFORE COMPUTE

| id | prediction |
|---|---|
| `C1` | arm `X` reads `patchV[0]` driver-scaled as **`29.160000000000004`** from the FINAL history |
| `C2` | after descaling, `patchV[0]` reconstructs to **`291.6`** inside `1e-12` relative and `CONTROL P` passes |
| `C3` | **`CONTROL B` will find `shape` components outside `[-1, 1]` in the DRIVER-SCALED vector** — D4 measured 62 of 96. **A driver-scaled vector with every `shape` component inside its bounds would mean the endpoint barely moved, and that would contradict a 30.4 % drag reduction** |
| `C4` | `ACC-1` lands inside `1e-3`; D4's landed at `2.34e-4` |
| `C5` | `G5` **PASSES** band D on at least 4 of 5 components. **Registered as UNLIKELY-to-be-clean on `shape[115]`**, which A3 rung 2 measured at `0.0172 % → 0.1586 %` and rung 1 at `0.9273 % → 0.3826 %` — **the same component has moved in opposite directions on two rungs of this ladder** |
| `C6` | `F-S` and `F-P` return **DISTINCT** `.so` md5s and `G9` passes for the first time on this A3 line |

## 12. CONDITION AT DRAFTING, AND HOW IT WAS CHECKED

| check | reading |
|---|---|
| run root `/home/ubuntu/certonomous-runs/CURRICULUM-D7F-*` | **does not exist** |
| any `d7f_*` container | **none has ever been created** |
| arm directories | **0** |

---

## 13. WHAT IS MISSING BEFORE THIS MAY BE FROZEN OR FIRED — **THE HONEST LIST**

**This document is `v0.9 DRAFT` and not `v1.0` because of exactly these, and a lane does not freeze
past them:**

1. **`d7f_accept_primal.py` and `d7f_accept_compare.py` — NOT WRITTEN.** `ACC-1` is `LIMIT 1` and
   `LIMIT 1` is a **precondition of the freeze**. Ports of `d4_accept_primal.py` /
   `d4_accept_compare.py`, which must carry D4's **planted-zero control** (`plant = 0.001234`, the
   planted artifact required to fall OUT of band while the clean one stays in).
2. **`d7f_run_arm.sh` — NOT WRITTEN.** The launcher, with §3's table wired arm by arm, §7's caps,
   the `H4` provenance gate and the cold guard. Until it exists, §3's table is a plan and not a
   check.
3. **`G10`'s declared non-binding status (§6) needs the supervisor's assent**, because declaring a
   gate non-binding in advance is close to the line rule 2 draws and **a lane should not draw it
   alone.**
4. **The reporting-cap charter question (§7)** is on Sanaa's desk and unruled.
5. **§12's four readings must be RE-TAKEN at the freeze commit**, not carried from this draft.

**NOTHING FIRES BEFORE THIS DOCUMENT REACHES v1.0 WITH ITEMS 1–3 AND 5 DISCHARGED AND IS COMMITTED
IN THAT STATE.**
