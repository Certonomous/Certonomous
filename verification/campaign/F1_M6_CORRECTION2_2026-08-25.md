# ONERA M6 — CORRECTION 2: **MY "UNFIRED" PREMISE WAS FALSE, AND IT MADE MY PROPOSED ROUTE UNLAWFUL**

**Written by the cfd supervisor personally, 2026-08-25.** Corrects
`F1_M6_TOPOLOGY_RULING_2026-08-25.md` §5 (`3026c90e`) and
`F1_M6_TOPOLOGY_RULING_AMENDMENT_2026-08-25.md` §7 (`43daff2f`). **Neither is
edited** — rule 6. `[lab-attributed]`; overrulable. **ZERO COMPUTE.**

**Caught by the lane, refused as a briefed premise, and VERIFIED BY ME against the
frozen blob before acceptance.** Fifth lane correction to this supervisor today,
and the fifth to be right.

---

## 1. THE CORRECTION

**I wrote, TWICE, that `F13_ONERA_M6_PREREGISTRATION.md` is UNFIRED and that a
rule-2 amendment was therefore still legal.** Original ruling §5: *"It is UNFIRED
— no solver has ever run under it — so under rule 2 an amendment is still legal."*
Amendment §7: *"needs a rule-2 amendment to the **unfired** …"*

**THAT IS FALSE.** Read by me from the frozen blob `7456a7b3dc62`:

- **`C1.5`, line 653** — *"**`GATE FAIL` on §5 admission at all three levels; tier
  `NOT HELD`; V, G and P `PENDING`**"*.
- **Line 623** — *"The ladder is closed `GATE FAIL` and this addendum cannot…"*
- **`C1.3`, line 637** — *"Moot for this ladder, **which is dead**"*.

**§5's admission gate has been GRADED. Amending it now would alter a gate after
its verdict, which standing rule 2 forbids outright.** My route was not merely
inadvisable; **it was unlawful, and I proposed it twice.**

**How I got it wrong.** I reasoned *"no solver has run, therefore no compute,
therefore gates are open."* **But §5's gate is a MESH ADMISSION gate — it is
graded by `blockMesh` and `checkMesh`, not by a solver.** Its compute happened and
its verdict landed. **"No solver has run" is not the same fact as "no gate has
fired", and I substituted one for the other.**

> **A gate that a mesher grades is fired when the mesher runs. Checking for a
> solver is checking the wrong instrument.**

**THE LAWFUL ROUTE IS A NEW PRE-REGISTRATION FOR A SUCCESSOR LADDER** — which
`C1.3` already anticipates, calling the dead ladder *"binding for its successor."*
**Not an amendment. The lane was right to draft none and to say so.**

## 2. A ROUTE I OMITTED, AND IT IS **MORE** FAITHFUL, NOT LESS

My amendment listed three routes and **missed the one the frozen document itself
discloses.** From **`AMENDMENT 2 §A2.2(1)`, line 491**, measured from the
registered STL `sdk/geometry/onera_m6_wing.stl`:

> **"THE M6 TIP IS NOT A FLAT CUT ON THE REGISTERED GEOMETRY, AND §5 SAYS IT IS."**

**So the mesh cuts flat a tip the reference geometry closes ROUND, and §5's stated
premise is contradicted by the STL §5 itself registers.**

**This is NOT the inadmissible move and I want the distinction on the record,
because a reader will otherwise file it with `TSCALE`.** `TSCALE` **thickens the
aerofoil section** — a different aerofoil, therefore not the ONERA M6, therefore
inadmissible. **Meshing the tip closure the registered STL actually has makes the
mesh MORE faithful to the M6, not less.** Those are opposite moves and I listed
only the first.

**Stated as the lane stated it: UNTESTED.** It is a candidate route, not a fix. **I
am not claiming it relieves mechanism B** — the 16:1 strip-to-core collapse is
driven by the section half-thickness going to zero at a **sharp trailing edge**,
which a rounded **tip** does not obviously touch. **That is a question for a build
trial, not for a supervisor's prose.**

## 3. WHAT STANDS UNCHANGED FROM THE AMENDMENT

- **`GATE FAIL`** against §3.1: best 81.5834° of nine variants, against 70°.
- **The far-field repair is real and should be kept**: 81.9396 → 47.9767 excluding
  the tip cap, **identical cell count**, dials untouched.
- **The tip-cap floor does not refine away**: 81.5834 (nr = 4) → 82.0645 (nr = 64),
  **rising to an asymptote near 82.07** — §8.1's signature of a fixed fraction of
  the mesh.
- **§3.1's 70° is NOT touched.** Scoping it is **reserved to Sanaa**, named and not
  proposed. **No lane may take it.**

## 4. COST, AND ONE CORROBORATION

Lane's measured cost: **6.367 core-min** (builds 0.217 + diagnostics 6.150) =
**$0.0054 derived, not measured**. **No pre-registered estimate exists, so the
ratio is recorded `N/A` and was NOT back-filled** — correct; a manufactured
predicted value would corrupt the calibration ledger it is meant to improve.
**Waste ≈ 0.13 core-min (~2 %), named separately.** Row **C-87**.

**Corroboration worth recording:** the lane re-derived the id from the **HEAD blob
tail, tolerant of plain AND bold forms**, and found max **86** — **independently
reproducing the peer finding that `append_record.py`'s regex misses the bold id
format.** Two teams, two derivations, same defect. **The hand-derivation
requirement in every cfd lane brief is doing its job.**

## 5. THE PATTERN I AM RECORDING AGAINST MYSELF

**Five lane corrections to this supervisor today, all five right:** `git ls-files`
hiding 18 % of the tracked population; the staleness class being L-253 recurring
rather than a discovery; the M6 maximum-vs-floor conflation; the `MK` test run
against the wrong mechanism; and now **a rule-2 premise that made my own proposed
route unlawful.**

**Three of the five are mine alone — not inherited from a brief I was handed.**
The common shape: **I reasoned from a plausible property to a conclusion without
checking the property on disk.** *"No solver has run"*, *"the maximum is at the
farfield"*, *"the index lists the tracked files"* — **each true-sounding, each
checkable in one command, each unchecked.**

**Recorded here rather than absorbed, because a supervisor's error rate is a
measurement about the supervisor and belongs where the next reader will find it.**
