# T-family index: what each rung needs before it can gate

Campaign T. Written 2026-08-19. **Updated as rungs report.**

---

## 1. The classification that matters most, and why it exists

D429 ranked the thermal side **reference-limited rather than compute-limited**
and put "obtain one forced-convection reference" first, calling it *"not compute
— requires a decision outside the compute authorisation."*

**T1c then graded a forced-convection rung that needed no reference at all.** Its
constants — `3.6567934`, `48/11`, `f·Re = 64` — are closed-form solutions of the
governing equations. **The cheapest rung in the class was one nobody had to
acquire anything for, and it sat unbuilt while the docket recorded the whole
class as blocked.**

**"We are reference-limited" was true of the class and false of some rungs in
it.** So every rung below is classified by **what its reference costs**, and the
exact-theory members are named explicitly — **they have no acquisition step and
can be built the moment compute is free.**

| tier | reference status | meaning |
| --- | --- | --- |
| **EXACT** | a closed-form solution | nothing to obtain; the reference cannot be wrong |
| **FORMULA** | a published correlation stated as an equation | reproducible from the formula; **no paper needed to evaluate it**, though its validity range must be cited |
| **ACQUIRE** | published data or a digitised figure | blocked until obtained |

---

## 2. The rungs

| rung | subject | reference tier | state |
| --- | --- | --- | --- |
| **T1c** | laminar pipe, `Nu` 3.657 / 48/11, `f·Re` 64 | **EXACT** | **REPORTED — GATE FAIL**, 3 of 4 rows pass |
| **T1b** | turbulent pipe vs Dittus–Boelter + Gnielinski | **FORMULA** | **PASS ×4 as returned by the frozen comparator, every grid triple DIVERGENT or STAGNANT** — D440, `T1b_RESULTS.md` |
| **T1a** | turbulent flat plate (= K0e) | ACQUIRE *(obtained)* | **BLOCKED** — reference held, but **no band can be armed from one correlation** |
| **T9a** | 1D composite wall, fin efficiency | **EXACT** | **REPORTED — GATE FAIL**, 2 of 3 graded rows pass (interface 1 fails by 2.4 mK against a 0.9 mK GCI band), 2 fin rows GATE REACHED below the 0.025 % O(Bi) floor, 4 controls MET — D442, `T9a_RESULTS.md` |
| **T10a** | view-factor enclosures vs analytic S2S | **EXACT** | **BUILDABLE NOW** — nothing to obtain |
| **T2** | tube bank vs Zukauskas | FORMULA | needs the correlation's **stated validity range** cited, not just its algebra |
| **T3** | heated backward-facing step, Vogel & Eaton 1985 | ACQUIRE | **not in the library** |
| **T4** | impinging jet, Martin lineage + jet data | ACQUIRE | **not in the library** |
| **T5** | heated cube(s), Meinders & Hanjalic | ACQUIRE | **not in the library**; also 3D, likely **over $25** |
| **T6** | Rayleigh–Bénard `Nu`–`Ra` scaling | ACQUIRE | 3–4 decades of published scaling data; **transient, far over $25** |
| **T7** | mixed-convection regime map | ACQUIRE | generalises K0d; per-run cheap, **aggregate may exceed $25** |
| **T8** | buoyant plume, stratified room | ACQUIRE + partial EXACT | **plume entrainment theory (Morton–Taylor–Turner) is closed form**; the room data is not |
| **T9b/c** | conjugate flat plate; conjugate cube | ACQUIRE | 3D for T9c, **likely over $25** |
| **T10b** | natural convection + radiation | ACQUIRE | combined-mode data |
| **T11** | transient conjugate module | partial **EXACT** | **lumped and 1D transient solutions are closed form**; the published transient data is not |
| **T12** | room-scale ventilation (Nielsen / IEA class) | ACQUIRE | **over $25** |
| **T13** | rack row | inherits everything | **far over $25** |

---

## 3. What this changes about the order of attack

The brief's default order is
**T1 → T3 → T5 → T9a → T4 → T6 → T7 → T10a → T2 → T8 → T11 → T10b → T12 → T13.**

**Three of the first five entries are ACQUIRE-blocked** (T3, T5, T4) while
**two rungs that need nothing sit at positions 4 and 8** (T9a, T10a).

**The recommendation, which is Sanaa's call and not taken unilaterally: pull
T9a and T10a forward to run alongside T1b.** They cost almost nothing, they are
unblockable by construction, and each opens a capability tier — T9a is the entry
to the whole conjugate ladder, T10a to radiation. **Nothing is reordered without
approval; the ordering above is recorded, not applied.**

**Partial-EXACT rungs are worth noticing too.** T8's plume entrainment theory and
T11's lumped/1D transient solutions are closed form, so **each has an
exact-theory entry rung that can be built before its data arrives** — the same
shape as T1c sitting available inside a class recorded as blocked.

---

## 4. What is NOT claimed here

**No rung above is a capability until it has reported.** T1c has, and it **GATE
FAILED**. T1b is running. Everything else in this table is a plan, and **naming a
plan as a capability is the error this campaign exists to avoid.**
