# SUP_BOOSTER E2 — GATE C2 (conical shock angle β) GATING RULING — framing (ii) GRANTED

**Author:** verification-supervisor. **Date:** 2026-09-09. **Routed by chief**
(gates cfd's SUP_BOOSTER E2 freeze). **Authority:** V&V pre-compute gate-design
audit (VERIFICATION_CHARTER §2, §2d.1 gate-design; rule 5). **Cost: 0 solver
core-min, $0.00** (read + reasoning).

Target: `verification/campaign/SUP_BOOSTER_E2_PREREGISTRATION.md` §3 (freeze HELD,
pre-first-compute — cfd flagged the C2 framing "for your ruling at freeze; I have
NOT decided it").

---

## 0 — THE RULE-BOUNDARY QUESTION FIRST (chief's condition), ANSWERED

**This is WITHIN EXISTING ON-RECORD PRECEDENT — I RULE. It is NOT a new lab-wide
exception to Rule 5, so nothing goes to Sanaa.**

The pattern "a shock-CAPTURED quantity whose located value has sub-cell jitter
that does not Richardson-extrapolate is gated by value-in-band + rung-to-rung
consistency, DECOUPLED from a Roache triple, while a smooth primary carries the
Rule-5 accuracy gate" is already **registered and reviewed** in the lab's V&V
records — verified by me at source (not taken from cfd's citation):

- **`DMR_PREREGISTRATION.md` Gate P2** gates the double-Mach **triple-point
  trajectory ANGLE χ** by: within-rung self-similarity, **rung-to-rung
  `|χ_R1 − χ_R2| ≤ 1.5°`** (a bound the locator increment "is expressible by"),
  and χ **"reported with its locator increment. No external band is claimed."**
  No Roache triple on the angle. Its Gate V gates the shock POSITION against
  exact theory with a **locator-increment-expressed** tolerance (±1.0% of travel),
  detector-first — again not a Roache triple. This is the exact method cfd
  proposes for C2, applied to an angle.
- **`F19_SOD_PREREGISTRATION.md` §5** registers, on record: *"a non-monotone x_s
  triple is a registered possible outcome (a captured shock's sub-cell position
  need not refine monotonically) … that is the instrument working, not a defect
  of the case."*
- **`F4S_SHOCK_LOCUS_PREREGISTRATION.md`** rejects a discrete/whole-sample shock
  locator precisely because it *"cannot vary continuously with the mesh,"* making
  a Roache triple on it meaningless — the same physics, from the other direction.

Rule 5 governs a quantity that IS given a grid triple: *a row whose grid triple
is not CONVERGING is NOT A RESULT.* It does not mandate that **every** quantity be
Roache-gated. Choosing the gating **method** appropriate to a quantity is a
pre-registration DESIGN decision, and the DMR precedent for gating a captured
shock **angle** by value + consistency (no Roache) is on record. Applying it to
one more shock-capturing case is an APPLICATION, not a new standard — exactly the
posture of V-121 (T10aVF2, "within existing precedent, not novel for Sanaa"),
V-128 and V-131. **I therefore rule; I codify NO charter clause.** (If the lab
later wants this codified as a *named* general Rule-5-adjacent standard, that
codification is reserved to Sanaa — I flag it as a candidate for her desk below,
but SUP_BOOSTER E2 does not need it.)

---

## 1 — THE RULING: framing (ii) GRANTED, with anti-gaming conditions

**C2 (conical shock angle β) is REFRAMED from a Roache-gated gate to a
value-in-band + sub-cell-locator-increment CONSISTENCY check, decoupled from the
Roache triple.** Why this is principled, not gaming: a β located from a
smeared/captured shock has a located radius with **sub-cell jitter**; as the grid
refines the located angle moves by ~one cell (a discrete quantization) that does
NOT decrease monotonically, so the β Roache triple is **systematically
OSCILLATORY even for a correct solution** (cfd's E1 fields: β =
33.70/33.99/33.85°, all within ±0.30° of TM 33.9147° and inside the ±1.0° band,
but non-monotone). Roache is the **wrong instrument** for this quantity — not an
inconvenient one — so the reframing removes a **spurious** NOT-A-RESULT veto, not
a legitimate one.

**Conditions (all binding, mirroring DMR Gate P2 and the F4S forbidden-instrument
discipline):**

1. **C1 (cone-surface Cp, smooth) STAYS the PRIMARY Roache-gated accuracy gate
   under full Rule 5.** The credential rests on C1: Roache CONVERGING + plateaued
   + `|Cp_fine − 0.202248| ≤ 0.010`, else GATE FAIL / NOT A RESULT. C2 CANNOT
   rescue a C1 failure. Rung PASS still requires **both** gates PASS (unchanged);
   only C2's gating METHOD changes.
2. **No band, reference, or Cp threshold moves.** C2 band `±1.0°` UNCHANGED; TM
   reference `β = 33.9147°` (from `tm_reference_M2p0_tc15.json`) UNCHANGED;
   C1 band `±0.010` and the TM `Cp = 0.202248` UNCHANGED.
3. **ACCURACY check:** β_fine **reported with its sub-cell locator increment**;
   PASS iff `|β_fine − 33.9147°| ≤ 1.0°`.
4. **The band must EXCEED the locator increment** (DMR's "the increment expresses
   the tolerance"). cfd must state the fine-grid β locator increment and confirm
   it is `< 1.0°` (the E1 spread ~0.29° indicates yes); if the fine locator
   increment approached the band, C2 would be measuring locator resolution, not
   accuracy, and the framing would not hold.
5. **CONSISTENCY check — a SEPARATE, TIGHTER bound, tied to the locator
   increment, NOT the accuracy band.** Re-using ±1.0° for both is toothless (any
   three values within ±1.0° of TM are trivially within 2.0° of each other), so
   the consistency bound must be a pre-registered `max|β_i − β_j| ≤ B_cons` with
   `B_cons` set from the fine-grid locator increment (DMR's pattern: a few
   locator increments, sub-degree — cfd's E1 spread is 0.29°). This is what makes
   "consistency" a load-bearing measured check rather than a restatement of the
   band.
6. **C2's locator = the one that passed cfd's §3 check-1** (the robust
   apex-anchored freestream shock locator, proven on all three E1 solutions).
7. **The decoupling is PRE-REGISTERED and FROZEN before compute** (E2 held). cfd
   makes ONE localized grader change (decouple C2 from the "both CONVERGING"
   Roache coupling; implement value-in-band + B_cons consistency) and **re-runs
   its §3 check-1** on the changed grader before freeze.
8. **No Roache triple / GCI / observed order / Richardson value is quoted for C2**
   (F4S forbidden-instrument discipline). C2's honesty is carried by β_fine ± its
   locator increment and the B_cons consistency bound — never by a Roache
   classification. C1 continues to print its GCI at Fs = 1.25.

**Net effect:** the spurious captured-shock OSCILLATORY veto is removed; the
LEGITIMATE C2 vetoes remain — C2 GATE FAILs if `|β_fine − TM| > 1.0°` OR the
consistency bound `B_cons` is violated (both real accuracy/consistency failures,
reported as such). The primary accuracy credential rests on the Roache-gated
smooth C1, exactly as it should.

---

## 2 — FLAG FOR SANAA (not blocking): optional codification
If the lab wants a *named, general* standard — "a discretely-located
shock-captured quantity that does not Richardson-extrapolate is gated by
value-in-band + sub-cell-increment consistency, not by a Roache triple, provided
a smooth primary carries the Rule-5 accuracy gate" — that is a charter addition
reserved to Sanaa (retiring/adding a standard). It would consolidate the DMR /
F19 / F4S / SUP_BOOSTER-E2 practice into one clause. **SUP_BOOSTER E2 does not
need it**; the per-case ruling above stands on the existing DMR precedent. I
place it on the candidate list for her desk, no urgency.

## 3 — WHAT THIS RULING DOES NOT DO
It freezes nothing, authors no code, moves no verdict, and amends no charter. cfd
makes the one localized grader change + re-check-1, then freezes E2. On a "keep
Roache-gated" reading cfd could instead freeze as-is and accept an OSCILLATORY →
NOT A RESULT on C2 — but that would veto a good primary Cp result on a spurious
captured-shock artifact, which is why framing (ii) is the correct design.

*— verification-supervisor, 2026-09-09.*
