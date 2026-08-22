# T-family index: what each rung needs before it can gate

Campaign T. Written 2026-08-19. **Updated as rungs report.** Ordering in force
is the section dated 2026-08-22 below; section 3 is superseded and retained.

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
| **T1b** | turbulent pipe vs Dittus–Boelter + Gnielinski | **FORMULA** | **PASS ×4 as returned by the frozen comparator, every grid triple DIVERGENT or STAGNANT** — D440, `T1b_RESULTS.md`. **L4 arms `R_*_x` running since 2026-08-21**: `R_10k_x` ETA 2026-08-23 ~01:40Z, `R_30k_x` / `R_100k_x` / `R_300k_x` ~2026-08-26 06–08Z. Until they land, the four Nu rows carry no mesh-converged value |
| **T1a** | turbulent flat plate (= K0e) | ACQUIRE *(obtained)* | **BLOCKED** — reference held, but **no band can be armed from one correlation** |
| **T9a** | 1D composite wall, fin efficiency | **EXACT** | **REPORTED — GATE FAIL**, 2 of 3 graded rows pass (interface 1 fails by 2.4 mK against a 0.9 mK GCI band), 2 fin rows GATE REACHED below the 0.025 % O(Bi) floor, 4 controls MET — D442, `T9a_RESULTS.md` |
| **T10a** | view-factor enclosures vs analytic S2S | **EXACT** | **REPORTED — GATE FAIL**, 3 of 4 graded box rows pass (ceiling fails at 0.125 % against a 0.077 % GCI band); both sphere rows NOT A RESULT on DIVERGENT triples — the outer-sphere row-sum defect (4.3–4.8 %, non-converging under fixed quadrature) dominates, so the grey graded claim stays open (ε = 1 verified to 0.005 %); 12 controls MET, 6 UNMEASURED; one 2d.1 zero-referent repair disclosed, graded rows byte-identical across it — D447, `T10a_RESULTS.md` |
| **T2** | tube bank vs Zukauskas | FORMULA | needs the correlation's **stated validity range** cited, not just its algebra |
| **T3** | heated backward-facing step, Vogel & Eaton 1985 | ACQUIRE | **all 8 cases complete under the strict rule 2026-08-22 (`R_f` 10:59Z); comparator run; NOT A RESULT 4/4 (gates (1)/(2) of prereg §7.1: no case at 1e-6, triples DIVERGENT/OSCILLATORY); primary (Vogel & Eaton 1985) still NOT OBTAINED — necessary, not sufficient; ext1 extension launched 2026-08-22 (`T3_EXT1_AMENDMENT.md`); see `T3_RESULTS.md`.** The primary is NOT OBTAINED (ASME closed; every open archive checked and named in `T3_PREREGISTRATION.md` §2) and its absence remains disqualifying, but it is not today's binding constraint — the ladder is: `gate_t3.json` returns `NOT A RESULT` ×4 on gates (1)/(2) of §7.1, which fire ahead of gate (3). Design frozen, comparator frozen at `628ef452` with the binding triple gate; open secondary (Smirnov 2016, CC-BY) digitised as REPORT-ONLY referent |
| **T4** | impinging jet, Martin lineage + jet data | ACQUIRE *(partial 2026-08-21)* | **OPEN**: ERCOFTAC case025 tabulated `Nu(r/D)` at `Re` 23k/70k, `H/D` 2/6 (kept in `reference-data/ercoftac_case025/`, one mislabeled header noted) + Martin correlation with stated validity from an open NREL report; **the Nu uncertainty is second-hand (2.4 %, KB Wiki quoting Baughn & Shimizu)** — graded rows need the closed ASME primaries; report-only enabled today |
| **T5** | heated cube(s), Meinders & Hanjalic | ACQUIRE *(obtained 2026-08-21)* | **PRIMARY HELD**: Meinders 1998 TU Delft thesis, OPEN, title-page verified, sha256 36c89a54…, stated uncertainty 5 % mid-face / 10 % edges in local `h`; data are digitisable figures, no tabulated appendix; single cube `Re_H` 2500–5000, matrix 2380–5280 — spend approved 2026-08-21; 3D cost to be registered before build. **Primary HELD — sha256 re-verified on disk 2026-08-22 under H-1; cost registration pending, and it is next after the cheap arms.** |
| **T6** | Rayleigh–Bénard `Nu`–`Ra` scaling | ACQUIRE | 3–4 decades of published scaling data; **transient, far over $25** |
| **T7** | mixed-convection regime map | ACQUIRE | generalises K0d; per-run cheap, **aggregate may exceed $25** |
| **T8** | buoyant plume, stratified room | ACQUIRE + partial EXACT | **plume entrainment theory (Morton–Taylor–Turner) is closed form**; the room data is not |
| **T9b/c** | conjugate flat plate; conjugate cube | ACQUIRE | 3D for T9c, **likely over $25** |
| **T10b** | natural convection + radiation | ACQUIRE | combined-mode data |
| **T11** | transient conjugate module | partial **EXACT** | **lumped and 1D transient solutions are closed form**; the published transient data is not |
| **T12** | room-scale ventilation (Nielsen / IEA class) | ACQUIRE | **over $25** |
| **T13** | rack row | inherits everything | **far over $25** |

---

## Ordering under the Thermal Buildup Directive (2026-08-22)

**This is the order of attack in force.** It comes from Sanaa's directive of
2026-08-22, recorded verbatim in `THERMAL_BUILDUP_DIRECTIVE.md`. Section 3 below
is the ordering this index recommended on 2026-08-19; it is **superseded
2026-08-22 by `THERMAL_BUILDUP_DIRECTIVE.md`, retained** — retained because the
reasoning in it is what produced the T9a and T10a pulls that have since
reported, and a superseded recommendation that is deleted cannot be checked
against what happened.

**1. Cheap arms first**, run while T1b's L4 arms finish (`R_*_x`, started
2026-08-21; `R_10k_x` ETA 2026-08-23 ~01:40Z, the other three ~2026-08-26
06–08Z):

| # | arm | directive | why it is first |
| --- | --- | --- | --- |
| 1 | **T10a ceiling refinement** | H-3a | a discretisation finding on a rung that has already reported; cheap |
| 2 | **T9a interface diagnosis** (interface scheme vs mesh vs property jump, one change per run) | H-4 | the 2.4 mK miss against a 0.92 mK band, on an EXACT rung; cheap |
| 3 | **T10a view-factor quadrature characterisation** (mesh-family sweep, geometry sweep, reproducer from clean case) | H-3b | joins the upstream queue as candidate #4; **filing remains Sanaa's call** |

**2. The DC spine**, which is the product path and takes priority inside the
T-family behind only R4's CPU-minutes:

**T3 → T5 → T8 → T12 → K2 rack row.**

| rung | the DC physic it carries | state entering the spine |
| --- | --- | --- |
| **T3** | separated thermal | **NOT A RESULT 4/4** (gates (1)/(2) of prereg §7.1: no case at 1e-6, triples DIVERGENT/OSCILLATORY); primary (Vogel & Eaton 1985) still NOT OBTAINED — necessary, not sufficient; ext1 extension launched 2026-08-22 (`T3_EXT1_AMENDMENT.md`) |
| **T5** | heated cubes = the rack physic | **primary HELD**; cost registration pending |
| **T8** | plume / stratification = the aisle physic | partial EXACT entry rung available (Morton–Taylor–Turner) |
| **T12** | room-scale validation | ACQUIRE, over $25 |
| **K2 rack row** | the rack row itself (campaign F14) | inherits the four above |

**3. Tier completion, after the spine** (H-5, in this order):

**T4 → T6 → T7 → T2 → T9b/c → T10b → T11.**

T4 is the band-containment flagship and is sharpened by the shelf-D finding:
the registered question is whether eigenspace bands contain the documented
stagnation-`Nu` bias. Charter §2e of 2026-08-22 governs how that band may be
armed, and requires `Nu_stag` to be classified as forcing-class in the
pre-registration.

**T13 is unplaced.** It is not in the spine, not in the H-5 completion order,
and inherits everything above it; nothing is scheduled for it here.

---

## 3. What this changes about the order of attack — SUPERSEDED

**Superseded 2026-08-22 by `THERMAL_BUILDUP_DIRECTIVE.md`, retained.** Nothing
below is in force; it is kept as the record of the recommendation that produced
the T9a and T10a pulls.

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
