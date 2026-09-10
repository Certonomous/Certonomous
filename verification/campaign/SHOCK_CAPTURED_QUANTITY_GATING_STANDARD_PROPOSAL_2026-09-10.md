# PROPOSAL for Sanaa — a NAMED, GENERAL gating standard for shock-captured quantities

**DRAFT — FOR SANAA'S DECISION. NOT ENACTED. NOT A RULING.**
**Author:** verification-supervisor. **Date:** 2026-09-10. **Cost: 0 solver core-min, $0.00.**
**Status:** a candidate `VERIFICATION_CHARTER` clause. Adding a *named general standard* is
reserved to Sanaa (retiring/adding a standard — CLAUDE.md FIRST-ACTION rule; ESCALATION
§8). I therefore DRAFT it and place it on her desk; I do NOT enact it. **Nothing in the lab
depends on this**: every relevant case is already correctly gated on the existing per-case
precedent (see §3), so this is consolidation only, no urgency.

---

## 1 — Why this is on her desk

Across four independent pre-registrations the lab has now, case by case, ruled the SAME
gating design for a shock-CAPTURED quantity, each time as an *application of existing
precedent* rather than a new standard:

- **DMR Gate P2** — the double-Mach triple-point trajectory ANGLE χ: gated by within-rung
  self-similarity + rung-to-rung `|χ_R1 − χ_R2| ≤ 1.5°` + reported with its locator
  increment, **no external band, no Roache triple**. Its Gate V gates the shock POSITION
  against exact theory with a locator-increment-expressed tolerance, detector-first.
- **F19_SOD §5** — on record: *"a non-monotone x_s triple is a registered possible outcome
  (a captured shock's sub-cell position need not refine monotonically) … that is the
  instrument working, not a defect of the case."*
- **F4S_SHOCK_LOCUS** — REJECTS a discrete/whole-sample shock locator for a Roache triple
  precisely because it *"cannot vary continuously with the mesh"* — the same physics from
  the other direction.
- **SUP_BOOSTER E2 / Gate C2** (conical shock angle β) — ruled 2026-09-09
  (`SUP_BOOSTER_E2_C2_SHOCK_ANGLE_GATING_RULING_2026-09-09.md`): β located from a captured
  shock has a located radius with sub-cell jitter, so its Roache triple is *systematically
  OSCILLATORY even for a correct solution* (E1: β = 33.70/33.99/33.85°, all inside ±1.0° of
  TM 33.9147°, non-monotone). Reframed to value-in-band + a tighter consistency bound tied
  to the locator increment, decoupled from the Roache triple.

Four cases, one design. A *named* clause would let a team recognise the pattern at
pre-registration instead of routing each instance to me. That consolidation — turning a
repeatedly-applied precedent into a standing standard — is the kind of change reserved to
you, which is why it is a proposal, not a ruling.

---

## 2 — The proposed clause (draft wording for your edit)

> **§2be (proposed) — Shock-captured quantities are gated by value + consistency, not by a
> Roache triple, when a smooth primary carries the accuracy gate.**
> A quantity whose value is LOCATED FROM A CAPTURED (smeared) shock — a shock position,
> angle, or trajectory read off a detector rather than resolved on the mesh — carries a
> located value with sub-cell jitter that quantizes with the grid and therefore does NOT
> Richardson-extrapolate. For such a quantity, and ONLY such a quantity, a Roache grid
> triple is the WRONG instrument (systematically OSCILLATORY / non-monotone even for a
> correct solution), and Rule 5's *"triple not CONVERGING → NOT A RESULT"* does NOT apply.
> It is instead gated by, all PRE-REGISTERED and FROZEN before compute:
>   1. **Value-in-band** against a named reference: `|q_fine − q_ref| ≤ band`.
>   2. **A SEPARATE, TIGHTER rung-to-rung consistency bound** `max|q_i − q_j| ≤ B_cons`,
>      with `B_cons` set from the fine-grid sub-cell LOCATOR INCREMENT (a few increments,
>      sub-unit) — NOT re-using the accuracy band (which would be toothless).
>   3. **The band must EXCEED the locator increment**; the fine-grid increment is reported
>      and confirmed below the band, else the quantity is measuring locator resolution, not
>      accuracy, and the framing does not hold.
>   4. `q_fine` is **reported with its sub-cell locator increment**; **no Roache triple /
>      GCI / observed order / Richardson value is ever quoted** for it.
> **Mandatory precondition (anti-gaming):** the case's credential must rest on a SMOOTH
> PRIMARY quantity that carries the FULL Rule-5 accuracy gate (Roache CONVERGING + plateau
> + band, GCI printed). The shock-captured quantity CANNOT rescue a primary failure; a rung
> PASS still requires BOTH gates PASS. This precondition is what keeps §2be from becoming a
> route around Rule 5: it removes only a *spurious* captured-shock NOT-A-RESULT veto, never
> a legitimate accuracy veto, and it never applies to a smooth quantity.

---

## 3 — What it does and does not change

- **Changes no live verdict and no existing gate.** DMR / F19 / F4S / SUP_BOOSTER-E2 are
  already gated exactly this way on their per-case rulings; §2be would merely name the
  shared design. If you enact it, the four rulings become citations of §2be rather than
  standalone precedent.
- **Does not relax Rule 5.** Rule 5 continues to govern every quantity given a grid triple;
  §2be only declares that a captured-shock located quantity is one that should NOT be given
  one, and requires a smooth Rule-5-gated primary as the credential anchor.
- **Boundary to watch (flagged, your call):** the clause must not be read as licence to
  declare ANY inconvenient non-monotone quantity "captured-shock". The gate on the gate is
  §2be(3) — the located quantity must have a demonstrable sub-cell locator increment that
  quantizes with the grid; a smooth quantity that merely happens to be non-monotone on a
  coarse triple is NOT covered and stays under Rule 5.

---

## 4 — Recommendation

Enact §2be as drafted (edit freely), OR leave the four per-case rulings standing as
precedent and continue routing new instances to me. Either is defensible; the lab is not
blocked on this. I will enact only on your word (a named-standard addition is yours).

*— verification-supervisor, 2026-09-10.*
