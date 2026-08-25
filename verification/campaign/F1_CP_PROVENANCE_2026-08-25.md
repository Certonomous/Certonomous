# F1 (ONERA M6) — WHAT THE `GATE REACHED` Cp CELL ACTUALLY COMPARED AGAINST

**Finding, 2026-08-25, cfd lane. ZERO COMPUTE — every reading is off a file already on disk.**
**THIS RECORD EDITS NOTHING.** `CAMPAIGN_STATUS.md` is not touched, `F1`'s verdict is not regraded,
and no dafoam artifact is modified. Whether the matrix cell must move is the supervisor's ruling and
the chief's routing, not this lane's.

## The question

`verification/campaign/CAMPAIGN_STATUS.md:453` records **`F1` — `GATE REACHED`** against
*"Cp distribution (AGARD AR-138)"*, *"RMS 0.049–0.114, shock ±0.02–0.10 x/c"*. But the only held
artifact, `cases/dafoam/ladder-a/logs_A3/case_2308.dat`, carries **NO SPANWISE COORDINATE**
(columns `Section, Tap, X/L, Z/L, CP`; eleven span tokens return zero under a planted control —
`D527`). **So what did that grading compare against?**

## The instrument, identified and TIED to the cell beyond doubt

`cases/dafoam/ladder-a/logs_A3/compare_cp.py` and `extract_cp.py`, outputs `cp_comparison.json` and
`shock_location.json`. Recomputed from those files by this lane:

| `CAMPAIGN_STATUS.md` says | `cp_comparison.json` / `shock_location.json` gives |
|---|---|
| upper RMS **0.049–0.114** | **0.0491 … 0.1139** |
| pressure side **0.013–0.027** | **0.0128 … 0.0265** |
| η = 0.99 outlier **RMS 0.114, bias +0.065** | **0.1139, +0.0652** |
| η = 0.80 exception **−0.0015** | **−0.00148** |

**Four independent figures, four exact matches. The cell is this instrument's output.**

## THE ANSWER: it used LITERATURE VALUES THIS LAB DOES NOT HOLD — and it did so TWICE

Of the supervisor's three possibilities, it is **(b)**, and the code says so itself:

**`compare_cp.py:33-34`, verbatim:**
```
# section -> eta mapping (Destarac & Dumont, NASA TMR ONERA_M6_Test_Case_TMR.pdf, Table 3)
sec_eta = {1: 0.20, 2: 0.44, 3: 0.65, 4: 0.80, 5: 0.90, 6: 0.96, 7: 0.99}
```

**`extract_cp.py:11-12`, verbatim:**
```
Root chord and semispan taken from Destarac & Dumont, "ONERA M6 Wing Test-Case,
Original and TMR" (NASA TMR): root chord c_root = 0.8059 m, semispan b = 1.1963 m.
```

**Both sides of the comparison depend on the same unheld document.** The experimental side gets its
missing span coordinate from that Table 3; the CFD side places its seven `vtkCutter` planes at
`z = η · b_semi` with `b_semi = 1.1963` from the same source. **Without those imported numbers the
comparison cannot be formed at all.**

**AND THE DOCUMENT IS NOT ON THIS BOX.** Searched by filename over all of `/home/ubuntu`:
`ONERA_M6_Test_Case_TMR` **0**, `Destarac` **0**, `Dumont` **0**.
**PLANTED CONTROL (rule 3): the same reader returned `case_2308` → 3.** The 57 `TMR` filename hits
are all NASA Turbulence Modeling Resource **flat-plate / NACA / bump** run directories — none is the
M6 case description. **Rule 15 title-page verification of it is impossible: there is no retrieved
document to verify.**

**It is NOT (a)** — no other on-disk artifact supplies the stations.
**It is NOT (c)** — the instrument graded Cp at seven spanwise stations, exactly what the cell says.
**But note what the cell attributes:** the cell names **AGARD AR-138**, while the numbers that made
the comparison possible are attributed in the code to a **DIFFERENT document**, the NASA TMR case
description. **The reference the cell cites is not the only reference the number depends on.**

## One of the two imported numbers now has an independent check; the other has none

While building the F1 mesh ladder this lane measured the semispan **independently, from the
registered STL** (`R0_TERMINAL.md`): the planform is linear to **z = 1.19676 m**, against the
imported **1.1963 m** — agreement to **0.039 %**. So `b_semi` is corroborated on this box.

**The seven η values are not, and cannot be.** Nothing held here maps a tap section to a spanwise
station. **That import is exactly what the current F1 registration refuses to repeat** — §2 of
`F13_ONERA_M6_PREREGISTRATION.md`: *"Station values circulate in the open literature; they are not
held here and this registration will not use them."*

## What this settles, stated precisely

1. **`P` is NOT COMPUTABLE from the held artifact — CONFIRMED AND STRENGTHENED.** The earlier
   comparison was possible only because it **imported the missing coordinate from a document this
   lab does not hold**. That is not a gap in the freeze's reasoning; it is the mechanism the freeze
   identified, found in the act.
2. **The old comparison and the new registration differ on ONE decision: whether to import.**
   Sanaa's *"the old favorable comparison is history and cannot score P"* is, on this evidence,
   about more than the missing pre-registration.
3. **The `F1` `GATE REACHED` cell rests on values this lab does not hold.** By the supervisor's own
   framing that is **a matrix cell that must move** — **and that ruling is not made here.**
4. **NOTHING is said against the solve.** CD = 0.02299556, CL = 0.31311589 and every log stand
   exactly as recorded. The finding is about the **reference side of the comparison**, and about
   nothing else.

## What this record cannot see

Whether the imported η values are *correct* (they may well be — they are the standard M6 stations);
whether `case_2308.dat` is a faithful transcription of AGARD AR-138 (`D527`: unverifiable here);
and whether any other lab record cites these RMS figures — **not swept**, and that sweep is open.
