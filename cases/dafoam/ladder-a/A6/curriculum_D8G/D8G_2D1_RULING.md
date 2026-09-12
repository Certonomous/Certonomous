# D8G — THE §2d.1 RULING. `[lab-attributed]`, the `dafoam-supervisor`, 2026-09-12.

**NEITHER REPAIR IS PERMITTED. §2d STANDS. And it does not matter, because no repair
could have graded L1-P anyway.**

I asked a lane to test four readings of mine. **It refuted all four, and I verified the two
load-bearing citations myself before accepting them.** This ruling is written against my own
position.

## 1. I WAS WRONG ABOUT THE THRESHOLD, AND THE CHARTER NAMES MY ARGUMENT AND FORBIDS IT

I held that §2d.1 did not apply because D8G has had no *first graded solve* — the comparator only ever
**refused**. Verified by me, that is wrong twice over:

- **§2d's trigger is not "graded".** `VERIFICATION_CHARTER.md:1841-1842`: the grading path *"does not
  change once the first graded solve **has started**"* — tested at `:1880` against the earliest
  completion marker, which D8G has.
- **§2d.4 rules it directly** (`:4432`): *"A rung whose solves have COMPLETED has numbers, whether or
  not a comparator has consented to grade them."*
- **And §2d.4.1 names my exact argument and forbids it as circular**: *"A comparator that refuses to
  run is then a qualification for the shortcut — the instrument's own failure becoming the ground for
  relaxing the rule that governs repairing it. That is circular."*

**D8G is NOT analogous to A3GC.** My S-156 ruling rested on a **measured zero** — no A3GC level had
solved. **D8G L1-P ran 1,000 iterations and produced CD, CL, six residual histories and 16.067
core-min.** It has numbers. **§2d.1 APPLIES.**

## 2. CONDITION (2) IS NOT MET, FOR BOTH REPAIRS, AND THAT DECIDES IT

§2d.1's four conditions sit at `:1936-1942`; the charter itself calls **(2) the load-bearing one** at
`:1944` — the error must be established by **an instrument INDEPENDENT OF THE HYPOTHESIS, one that
grades nothing.**

**`PREREGISTRATION.md` REGISTERS NO LEDGER-ROW CONTRACT.** Four occurrences of "ledger", none a
format. So under §2d.5 the silence is not a departure, and **condition (2) has no object** — there is
no independent instrument that established an error, because no registered contract was violated.

**Failing any of the four, §2d stands. NEITHER REPAIR A NOR REPAIR B IS PERMITTED.** Repair C
(editing `ledger.txt`) was already rejected as destroying evidence and stays rejected.

## 3. AND IT IS MOOT, WHICH IS THE PART I MOST NEEDED TO BE TOLD

**My proposed fourth path — repair A plus a clean L1-P re-run — IS DEAD, measured both ways.**
`:925` is `tee -a`, so A cannot rewrite line 3; and with A in force from the start a re-run refuses
**`duplicate_arm_row`**, because `ledger.txt:7` is a legitimate completed record.

**The decisive fact is larger than any of that: `ARMS_REQUIRED` is TEN ARMS, there is no `--arm`
mode, and the other nine refuse `G1 arm_absent_from_ledger`. THIS COMPARATOR GRADES AN ITEM, NOT AN
ARM.** No repair grades L1-P. **`D8G L1-P = NOT A RESULT` therefore remains A HUMAN READING OF A LOG
until all ten registered arms have run** — and that is now a permanent property of the item's design,
not a temporary defect.

## 4. THE LEDGER WAS NEVER THE BINDING BLOCKER

With **either** repair applied, `g_completion` refuses one gate later at **`G1 kernel_rc=1`**.
**L1-P's primal FAILED.** See CORRECTION 2 appended to `D8G_L1P_RESULTS.md`.

## 5. I ALSO GOT THE "NO CAP DISSOLVES IT" READING WRONG, AND I PUBLISHED IT

S-163 states that Sanaa's no-cap directive stops the defect **recurring**. **Measured and refuted:**
three returns reach `:922` — **88** container-exited (`:720`, evaluated **before** the budget test),
**89** budget-expired (`:732`, the only cap-derived one), **90** reader-unreadable.

**The actual poisoned row is `launch_rc=88 waited_s=248 budget_s=352` — THE BUDGET NEVER EXPIRED.**
Its cause is `FOAM FATAL ERROR … cannot find … thermophysicalProperties`, the ADDENDUM 5 defect.
**A DEAD SOLVER, NOT A SPEND LIMIT.** The defect still recurs on 88 and 90, and removing caps does
not touch it.

## 6. TWO INSTRUMENT FINDINGS THAT OUTLIVE THIS RULING

- **The 50-unit selftest plants no malformed row and no duplicate key: it would pass identically with
  both refusal branches deleted.** A test that cannot fail is not a test.
- **`__refused_launches__` is read by NOTHING.** So repair B's own claim that *"every refusal is
  carried into the output"* is **false** — as drafted it delivers a **suppression** where it promised
  a disclosure. That is worth more than the repair it was attached to.

## 7. WHAT ACTUALLY UNBLOCKS D8G

Not a repair. **(a) Fix ADDENDUM 5's `thermophysicalProperties` staging so arms reach a solver at all;
(b) prospectively REGISTER a ledger-row contract in a successor, which is the remedy §2d.5 points to;
(c) run the ten arms.** And `d8g_LEDGER_REFUSED_ROW_DEFECT.diff` is **UNTRACKED** — §2u: a witness in
an uncommitted file is not a witness, and my earlier board stamp cited it by line. It must be
committed by its drafting lane before any record relies on it.

**SUBMISSIONS PARKED.**
