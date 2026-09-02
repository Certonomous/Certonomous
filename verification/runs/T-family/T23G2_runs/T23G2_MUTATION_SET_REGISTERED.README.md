# READ THIS BEFORE READING `T23G2_MUTATION_SET_REGISTERED.md`

**Sidecar to a pre-execution freeze. The frozen file is not edited and must not
be — not even to append a dated addendum.**

`T23G2_MUTATION_SET_REGISTERED.md` is the mutation set for the T23G2
comparator-guard exercise of 2026-09-02, **frozen before any mutation was run**.
Its entire evidentiary content is that it is the bytes that existed before the
answers were known: it proves the set could not have been chosen after seeing
which mutations survived. A pre-execution freeze that gets corrected after the
fact is no longer one.

**Integrity check.** The frozen file is unedited at
`sha256 5807609a214a57e8dacf0c399c269ef06ce73664bd8240abf6315d8b5f73299e`, the
value published in `docs/campaigns/T-family/T23G2_RESULTS.md` §15.1. If that no
longer matches, the freeze has been broken and the file has lost its standing.

---

## THE DEFECT IN THE FROZEN FILE: ITS CLOSING ARITHMETIC IS WRONG

The final line reads:

```
# TOTAL REGISTERED: 54.  S = 18, P = 36.
```

**The total is right and the split is wrong.** Recounting the direction letters
the file itself assigns to each arm:

- **`S` (strict) = 17** — `A1`–`A8` (8), plus `C8`, `E1`, `F2`, `G1`, `G2`, `H1`,
  `H2`, `I1`, `I2`.
- **`P` (permissive) = 37.**
- 17 + 37 = 54, so the registered total is correct.

**No direction letter was changed and none is in dispute.** Every arm carries
exactly the `S`/`P` label it was frozen with; only the tally at the foot was
miscounted. The error is the running lane's own and is disclosed rather than
glossed.

**Every rate reported from this exercise already uses the corrected split** —
overall 36/46 = 78 %, strict 14/15 = 93 %, permissive 22/31 = 71 %, after
excluding the eight unconstructable-or-inert arms from both numerator and
denominator.

**This correction is not new here.** It is already recorded in
`docs/campaigns/T-family/T23G2_RESULTS.md` **§15.2**, which makes the same
finding and gives the same reason for not editing the file. This sidecar closes a
gap in the standalone artifact only: a reader who opens the frozen set alone would
otherwise carry away a wrong split.

---

## A SECOND DEFECT IN THE FROZEN FILE, ALSO DISCLOSED

**The frozen set carries no cost line.** `CLAUDE.md` rule 12 requires every run to
be costed in its pre-registration. The exercise launched no solver and created no
run directory — every arm re-ran the comparator against existing artifacts on
scratch copies — but it was **not instrumented for cost**, and the omission is a
defect in the registration rather than an exemption from the rule. The actual is
reported in `T23G2_RESULTS.md` §15; there is no pre-registered estimate to compare
it against, so rule 12's estimate-versus-actual calibration cannot be performed
for this exercise and is reported as not performed.

---

## WHAT THIS FILE IS NOT

It is **not** an amendment to the frozen set, **not** a re-registration, and
**not** a gate verdict. The `KILLED` / `SURVIVED` / `SURVIVED-CHANGED` /
`UNCONSTRUCTABLE` labels in the set are the driver's own mutation-outcome labels
and are **never** to be read as `CLAUDE.md` rule 1 gate verdicts. The T23G2 rung
verdict is `NOT A RESULT` and nothing here affects it.

Full analysis: `docs/campaigns/T-family/T23G2_RESULTS.md` §15.
Companion sidecar: `T23G2_MUTATION_CONTROL.README.md` in this directory.
