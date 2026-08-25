# The F-family triple-crown survey — which F cases can reach HOLDS, what it costs, and the honest tier

**Team:** cfd. **Lane:** `lab-lane` under `cfd-supervisor`. **Written** 2026-08-25.
**ZERO COMPUTE.** No solver, no mesher, no case directory was created in producing
this file. Every number below is quoted from a landed artefact and cites it; the only
work this lane performed itself is reading, counting and one rule-15 title-page
verification (§6.2), which is disclosed as this lane's own act.

**Submissions are parked.** Nothing here is filed, sent, uploaded, registered or
posted anywhere outside this box (standing rule 7).

---

## 0. The rubric is verification's. cfd defines nothing here.

Read from the HEAD blob of `docs/COVERAGE_MATRIX.md` (the working tree shows that
file deleted; `git show HEAD:docs/COVERAGE_MATRIX.md` is the authority used
throughout), together with `docs/charters/VERIFICATION_CHARTER.md`.

| column | scores green ONLY when |
| --- | --- |
| **V** — code verification | an **exact solution**, a **manufactured solution**, or a **correlation**, and the case was compared against it |
| **G** — grid convergence | a **CONVERGING Roache triple**, **GCI at Fs = 1.25**, and an **observed order p** |
| **P** — validation | against a **public primary source**, with the **pre-registration ON DISK** |

**Tier vocabulary — the MATRIX's five words**, and they are *distinct* from CLAUDE.md
rule 1's verdict vocabulary (`COVERAGE_MATRIX.md` §1.1): **HOLDS / GATE REACHED /
SURVEYED / NOT HELD / NEVER RUN**. A row may carry the verdict `PASS` and the tier
`GATE REACHED` simultaneously and that is not a contradiction. Verdict words used
below are rule 1's and only rule 1's.

**Ruling 1, FINAL FORM (second amendment, 2026-08-25) — the tier counts GREEN
columns, not missing ones:** 3 green → HOLDS; 1 or 2 green **under a frozen
pre-registration** → GATE REACHED, naming every missing letter; 0 green → SURVEYED;
a green column's own gate returned FAIL, or a blocker → NOT HELD; no solve → NEVER RUN.

**Ruling 4** — `P` is green only against **MEASURED PHYSICAL REALITY**. An exact
solution, analytic benchmark, manufactured solution, **correlation**, another code's
result or a numerical benchmark scores `V` if it qualifies there and **scores `P`
never**. **Ruling 3** — a benchmark reached **through a secondary source** does not
make `P` green; the lab must HOLD and be able to READ the source. **Ruling 2** — an
unsettled observed order still scores `G`, and the row must disclose that it is
unsettled and quote the sequence.

**Where this survey would score a row differently from the matrix owner, it says so
and does not act on it.** Two such places are §7.1 and §7.2.

---

## 1. HEADLINE — the finding, stated before the table

**No F case can reach HOLDS as it currently stands, and only two can reach it at
all.** Of the 21 F rungs enumerated in §2, **zero hold three green columns**, **zero
hold two**, and the F family's entire green inventory is **five V cells and one
contested P cell** — with **no `G` anywhere in the family**, earned or claimed.

**The lab's own headline is confirmed from the F side and is not softened here:
there are no HOLDS rows.**

Three further findings that are not in any existing record:

1. **F13 DOES NOT EXIST.** It was never allocated. It is named as "next unused" in one
   superseded document and expressly corrected in two others. The F family runs
   **F1–F12**; **F14 is the cooling ladder and is heat-transfer's**, not cfd's, and is
   out of scope here rather than annexed. (§2.1)
2. **The F family's best HOLDS candidate is NOT F12**, the case the chief routed as
   the lab's shortest path. It is **F5a, the cylinder**, and the reason is a single
   physical document: **Roshko (1954), NACA Report 1191 is ON DISK and this lane
   title-page verified it** — the **only** experimental primary in the entire F family
   the lab both holds and can read. (§6.2, §8)
3. **Sanaa's central hypothesis reaches the right conclusion by a mechanism that is
   wrong in an actionable way.** The conclusion — no F row carries both a
   code-verification reference and an experimental primary — is **CONFIRMED**. The
   mechanism is not that the two reference kinds are mutually exclusive per case. It
   is that **V is manufacturable and P is a procurement problem**, plus a rubric
   clause that spends the lab's most physical references on V. (§6)

---

## 2. The roster, enumerated from disk rather than assumed

**Method, stated per claim as instructed.** Tracked state read with
`git ls-tree -r HEAD verification/campaign/` and `git show HEAD:<path>` — never
`git status`, which is not a valid instrument here (the shared index carries 50 stale
paths). Disk state for `docs/papers/` read with a **non-ignoring** `find … | xargs
grep`, because a plain `grep -r` in this repository is `ugrep --ignore-files` and is
blind to gitignored trees. The roster itself comes from
`verification/campaign/CAMPAIGN_STATUS.md` (the F-family roster document) cross-read
against the tracked file list.

**21 rungs across 12 live case ids:**

| id | case | dimension | rung status source |
| --- | --- | --- | --- |
| F1 | ONERA M6 transonic wing | 3D | `CAMPAIGN_STATUS.md:7`, `:453` |
| F2 | Transonic NACA 0012 | 2D | `CAMPAIGN_STATUS.md:24`, `:454` |
| F3a / F3b / F3c | wedge / cone / diamond, exact supersonic theory | 2D / axisym / 2D | `F3_supersonic_exact_theory.md`, `F3_CONVERSION_PREREGISTRATION.md` |
| F4 | hypersonic blunt body, M 6–8 cylinder | 2D | `F4_hypersonic_blunt_body.md`, `F4_SIGFPE_STEP01_*` |
| F5a | unsteady cylinder, Reynolds ladder | 2D/3D | `F5a_cylinder_reynolds_ladder.md` |
| F5b | pitching airfoil physics rung | 2D | `F5b_PHYSICS_PREREGISTRATION.md` |
| F5c | unsteady statistics / lever isolation | 2D | `F5C_*`, `F5bc_unsteady_statistics.md` |
| F6a | NASA 2D wall-mounted hump | 2D | `CAMPAIGN_STATUS.md:169`, `F6a_*` |
| F6b | periodic hills | 2D | `CAMPAIGN_STATUS.md:204`, `F6b_*` |
| F6c | square/rectangular duct vs DNS | 3D | `CAMPAIGN_STATUS.md:189` |
| F6d | random-matrix / max-entropy model-form UQ | — | `F6d_random_matrix_uq.md`, `F6D_*` |
| F7a | dam break vs Martin & Moyce (1952) | 2D | `F7a_REGATE_PREREGISTRATION.md`, `F7a_REGATE_SPEC.md` |
| F7b | Wigley hull wave resistance | 3D | `F7_marine_free_surface.md` — BLOCKED |
| F7c | workshop hull, DTMB 5415 / KCS | 3D | `F7c_DTMB5415_STAGING_PLAN.md` — BLOCKED |
| F8 | rotating machinery, UAE Phase VI MRF | 3D | `F8_MRF_HAND2001_GATE.md` |
| F9 | pulsatile valve | axisym | `F9_pulsatile_valve.md` |
| F10 | 3D viscous RANS batch family | 3D | `CAMPAIGN_STATUS.md:443`, `:468` — NOT STARTED |
| F11 | lid-driven cavity vs Ghia | 2D | `F11_lid_driven_cavity_ladder.md`, `F11_CONVERSION_PREREGISTRATION.md` |
| F12 | RAE 2822 / AGARD AR-138 Case 9 | 2D | `F12_PREREGISTRATION.md` |

### 2.1 F13 was never allocated — a roster correction

The brief scoped this survey to "F1 … F13". **There is no F13.** A non-ignoring
tracked-tree sweep for `\bF13\b` returns five hits and **not one is an F-family CFD
case**: three are a dafoam falsifier id inside
`cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/`, one is a duplicate-paper flag in
`docs/closure/PAPER_CATALOGUE.md:601`, and the remaining two are the records that
retire the id:

- `docs/campaigns/F14-cooling-ladder/README.md:43` — *"F13 was named as 'next unused'
  in an older document written before F12 was checked; that reading is superseded by
  this one."*
- `verification/campaign/THERMAL_K0_PREREGISTRATION.md:237` — *"**§0's guess that 'F13
  is the next unused' is wrong and is superseded.** F12 is a live campaign with its own
  preregistration, which §0 did not check."*

**F14 through F22 were verified unused repository-wide** at that time, and F14 was
taken by the cooling ladder. **F14 is heat-transfer's territory and is out of scope
for this survey** — it is named here to say so explicitly, not to annex it.

---

## 3. THE RANKED TABLE — best candidate for HOLDS first

Ranked by **reachability of HOLDS**, not by interest. Rows that **cannot** reach HOLDS
rank below every row that can, each with the one-sentence reason.

**Green-column count uses Ruling 1's final form.** `V?` / `G?` / `P?` record the
column state **today**; `ceiling` records the best tier the case could ever reach if
every attainable column were bought.

| rank | id | V | G | P | tier TODAY | ceiling | why it ranks here |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **1** | **F5a** | **YES** — Roshko–Williamson **correlation** (`VERIFICATION_CHARTER.md:84`) | NO | **CANDIDATE** — Roshko 1954 NACA TR 1191 **held and title-verified** (§6.2) | **SURVEYED** (0 green under a frozen prereg — **there is no F5a prereg**) | **HOLDS** | **The only F case whose experimental primary the lab holds and can read.** All three columns are attainable; none is bought. |
| **2** | **F12** | **NO** — verified in §7.1 | **REGISTERED, UNFIRED** — 23,040/92,160/368,640, r = 2 exact, dim = 2 | **MATERIAL, SECONDARY** — `f8621.txt`; AGARD AR-138 not held | **NEVER RUN** (0 green) | **HOLDS** *only if* a V is manufactured **and** verification rules the secondary can support P | Registered G and a real experiment, but **no V at all** and a P that turns on someone else's ruling. |
| **3** | **F6a** | NO — no exact solution for separated turbulent flow | NO | **MATERIAL** — NASA hump experiment (`CAMPAIGN_STATUS.md:177-178`); primary-on-disk **UNVERIFIED** | **SURVEYED** (0 green; no prereg for the hump gate) | **GATE REACHED**, missing V | V is not earnable by this physics without a manufactured solution; P is real but unverified on disk. |
| **4** | **F3** (a+b+c) | **YES** — oblique-shock, Taylor–Maccoll, shock-expansion, all **exact analytic** | NO — three levels exist, no order, no GCI; **conversion prereg FROZEN and registers r = 2 triples** | **NO — IMPOSSIBLE** | **GATE REACHED**, missing G and P *(see §7.2 on the frozen-prereg qualifier)* | **Cannot reach HOLDS: exact theory admits no experiment**, so P can never be bought for this case. |
| **5** | **F4** | **YES** — Billig (1967) **correlation** + modified Newtonian | NO | **NO — IMPOSSIBLE via its own references** | **GATE REACHED**, missing G and P | **Cannot reach HOLDS: both its references are correlations, and Ruling 4 spends a correlation on V and never on P.** |
| **6** | **F11** | **NO — not earnable by this case at all** | **REGISTERED, UNFIRED** — n = 32/64/128, r = 2 by construction, `form="equal"` asserted | **BLOCKED** — no Ghia PDF anywhere on this box; and Ghia is a **numerical** benchmark | **SURVEYED** (0 green) | **GATE REACHED**, missing V and P | **Cannot reach HOLDS: the lid-driven cavity has no exact solution and Ghia is code-to-code — its own pre-registration says so before the core-minutes are spent.** |
| **7** | **F5b** | material — analytic **Theodorsen** hysteresis loop | NO | **NOT OBTAINED** (prereg §2 field 4) | **SURVEYED** (0 green; frozen but **unfired**) | GATE REACHED, missing G and P | **Cannot reach HOLDS: BLOCKED on a permission decision that is Sanaa's alone**, and its reference is not obtained. |
| **8** | **F1** | NO | NO | material — AGARD AR-138 experiment; **primary NOT on disk**, **and no pre-registration exists at all** | **SURVEYED** (0 green) | GATE REACHED, missing V | **Cannot reach HOLDS: the primary is absent and there is no prereg**, so P fails on rule 15 and on Ruling 3 simultaneously. |
| **9** | **F2** | NO | NO | **NO** — reference is a *"literature-recalled `x/c ~ 0.60`"*, `NOT OBTAINED`, and the AGARD comparison is **inviscid, numerical** | **SURVEYED** (0 green) | SURVEYED | **Cannot reach HOLDS: its reference was never obtained and what it compares to is another computation.** |
| **10** | **F6b** | NO — Fröhlich et al. (2005) is an **LES**, i.e. none of exact/manufactured/correlation | NO | NO — a numerical benchmark scores P never (Ruling 4) | **SURVEYED** (0 green) | SURVEYED | **Cannot reach HOLDS: an LES reference fills no column under this rubric.** |
| **11** | **F6d** | NO | NO | NO | **SURVEYED** (0 green) | SURVEYED | **Cannot reach HOLDS: it is a model-form UQ study, not a gated physics comparison.** |
| **12** | **F5c** | NO | NO | NO | **SURVEYED** (0 green) | SURVEYED | **Cannot reach HOLDS: effectively closed, headline withdrawn, Stage B never approved and moot.** |
| **13** | **F9** | **YES material** — Womersley (1955) **exact solution** — **but the V gate returned `GATE FAIL`** | NO — observed order **0.39 / 3.47 / 0.82** across triplets, not consistent, **not CONVERGING** | NO | **NOT HELD** | NOT HELD on the record as it stands | **Cannot reach HOLDS: its one green-eligible column's own gate FAILED**, which Ruling 1 sends straight to NOT HELD. |
| **14** | **F7a** | NO | NO | **CONTESTED** — see §7.2 | **NOT HELD** | NOT HELD on the record as it stands | **Cannot reach HOLDS: the gate returned `GATE FAIL`** at +7.8 % to +11.9 % against a 5 % band, and the tier is NOT HELD however P is ruled. |
| **15** | **F6c** | NO — DNS is a numerical benchmark | NO | NO | **NOT HELD** | NOT HELD | **Cannot reach HOLDS: `GATE FAIL` is structural** — a linear Boussinesq closure has zero normal-stress anisotropy by construction and captures 0 % of the DNS magnitude. |
| **16** | **F8** | NO | NO | NO — **neither primary publishes a tabulated 7 m/s torque**; `Q_ref = 800 N·m` is secondary-tier | **NOT HELD** | NOT HELD | **Cannot reach HOLDS: it could not produce a gateable number** — the measured band is 960 % of the reference against a 50 % cap. |
| **17** | **F7b** | — | — | — | **NEVER RUN** | — | **Cannot reach HOLDS: BLOCKED behind F7a's gate failure** under the campaign's hard ladder rule. |
| **18** | **F7c** | — | — | — | **NEVER RUN** | — | **Cannot reach HOLDS: BLOCKED behind F7b, which is itself blocked.** |
| **19** | **F10** | — | — | — | **NEVER RUN** | unknown | **Cannot reach HOLDS: not started, no record file exists** — and the `mega-batch`'s internal "Family F10" label is a **different** thing (`CAMPAIGN_STATUS.md:536`). |
| **20** | **F13** | — | — | — | **does not exist** | — | **Not a case.** The id was never allocated; see §2.1. |

**Census under the owner's rubric: HOLDS 0 · GATE REACHED 3 · SURVEYED 9 ·
NOT HELD 4 · NEVER RUN 3 · non-existent 1.**

**The F family holds five V cells (F3a, F3b, F3c collectively, F4, F9-failed, F5a,
F5b-unfired), ZERO G cells, and zero uncontested P cells.**

---

## 4. Per case: what it would take, whether it is even possible, and what it costs

Costs are **core-minutes**, the lab's measured unit. Dollars are **DERIVED at
$0.0513/core-h and are reported-by-owner, never measured** — this box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **A case with no costing basis is
reported UNCOSTED and is not guessed at.**

### F5a — rank 1. Three attainable columns, zero bought, and no pre-registration.
**Missing: all three, but none of them impossible.** V would come from the
Roshko–Williamson correlation the Re 100 gate already uses
(`VERIFICATION_CHARTER.md:84` records `0.1590` computed against `0.1578`, **0.77 %**,
`PASS`) — or, more defensibly, from a **manufactured solution** that avoids the
double-count objection in §6.3. G would come from an equal-ratio triple on a 2D
cylinder, which is cheap and geometrically unproblematic. P would come from Roshko's
**own measured Strouhal points**, from the primary the lab holds (§6.2) — and whether
digitising Figure 5 *of a held primary* is a primary reading, as against F7a's
digitisation of a 2021 *secondary*, is **verification's rubric call, which this
survey states and does not decide**.
**Blockers that are not compute:** no F5a pre-registration exists anywhere; the Re
1000 rung's experimental citation (Williamson & Brown 1998) is **not on disk**; the Re
2000 rung's reference is recorded `NOT OBTAINED` as a primary
(`VERIFICATION_CHARTER.md:1712`).
**Cost: UNCOSTED.** `CAMPAIGN_STATUS.md:458` records no core-minute figure for F5a and
no frozen pre-registration carries a cost table for it. The nearest **named analog**
is F11's 2D equal-ratio triple at **8.02 core-min** — but F11 is *steady* and a
Strouhal ladder is *unsteady*, so that analog does not transfer and this lane will not
extrapolate it. **A costed pre-registration is the first deliverable, not a run.**

### F12 — rank 2. Registered G, a real experiment, and no V whatsoever.
**Missing: V outright; G unfired; P contested.** The G is already registered
*pre-freeze* and is the strongest unfired ladder in the family. The P is material and
experimental but **secondary**. The V is simply absent — see §7.1, where this lane
verified that personally.
**What would fill V:** a **manufactured solution** on the same solver and mesh family.
Nothing else is available: RAE 2822 transonic viscous flow has no exact solution, and
adding a correlation would only re-run the F4 problem.
**Blockers that are not compute:** **no AGARD AR-138 exists under `docs/papers/`** — a
full-text sweep returns three files that merely *cite* it — so **rule 15 title-page
verification of F12's primary is IMPOSSIBLE**. The held artefact is the AFOSR-HTTM /
Stanford digitisation, flow case 8621, evaluator R. E. Melnik (1981), at
`verification/runs/F12_runs/reference/f8621.txt`, **title-page-verified against
nothing**. The pre-registration discloses this in its own words at its ~lines 32–37.
**Cost, from the frozen pre-registration's own table (`F12_PREREGISTRATION.md` §4,
§5):** **383.5 core-min estimated = $0.328 derived**; caps
**120 / 160 / 700 / 160 / 160 = 1,300 core-min = $1.111 derived**. **An overrun stops
the run; it does not get a new budget.** A manufactured-solution V rung would need its
own costed pre-registration and is **UNCOSTED** here.

### F6a — rank 3. A real experiment, unverified on disk, no prereg for the gate.
**Missing: V (not earnable without a manufactured solution), G, and P's document
check.** The hump gate compares separation `x/c` **0.6544 vs NASA experiment 0.665**
(−1.59 %) and reattachment **1.2534 vs 1.100** (+13.95 %), the documented SST
over-prediction. That is measured physical reality; **whether the NASA primary is on
disk and title-verifiable was NOT established by this lane and is marked UNVERIFIED.**
**Cost, measured analog:** the original F6a pass cost **5.25 core-min**
(`CAMPAIGN_STATUS.md:184` — Feasibility 0.28 + Physics 2.51 + Gate 2.47) =
**$0.0045 derived**. A three-level equal-ratio triple is **ESTIMATED** at roughly
**3 × the Gate rung**, i.e. **~7.4 core-min = $0.0063 derived** — **ESTIMATED from a
named analog, not measured, and not a substitute for a costed pre-registration.**

### F3 — rank 4. V bought, G one frozen run away, P forever out of reach.
**Missing: G and P. P is IMPOSSIBLE and that is not a compute problem** — wedge, cone
and diamond surface pressure at these conditions are compared to closed-form theory
because there is no experiment to compare them to.
**What would fill G:** the conversion pre-registration is **FROZEN at `2bf4915a` and
ARMED AND UNFIRED, zero compute**. Its §3 fixes five gates, all **exact analytic**
(G-F3-1 wedge `p2/p1` ±0.5 %; G-F3-2 wedge β ±2.0 %; G-F3-3 cone `pc/p1` ±0.5 %;
G-F3-4 cone β ±2.0 %; G-F3-5 diamond `cd` ±1.0 %), and its §4.4 registers grid triples
where **h halves exactly and r = 2 by construction**, with standing rule 5 written out
verbatim including *"no GCI quoted"* on a non-CONVERGING triple.
**Cost, from the frozen pre-registration's own §7 table:** **2,113.8 core-s = 35.23
core-min**, **$0.0301 derived**; **HARD CAP 39.5 core-min = $0.0338 derived**, with
three enforcement points in `rerun_f3.py`.
**Blocker that is not compute — REPORTED, NOT FIXED:** `F3_CONVERSION_PREREGISTRATION.md`
line 14 still introduces its motivating text as **"Sanaa's directive, verbatim"**. See
§9.

### F4 — rank 5. Two V references, and both of them lock P shut.
**Missing: G and P.** G is buyable; **P is impossible via F4's own references**, and
the reason is the rubric rather than the physics: Billig (1967) is an **empirical
correlation of measured shock standoff**, and modified Newtonian is an analytic
approximation. **Ruling 4 places a correlation in V and excludes it from P
explicitly.** So the reference that is *closest to measured reality* in this case is
spent on V and cannot buy P. See §6.1 — this is the sharpest instance of the rubric
mechanism in the family.
**Blocker that is not compute:** **no F4 conversion pre-registration has been
written.** The F4 record that exists (`F4_SIGFPE_STEP01_*`) is a **SIGFPE crash
diagnostic**, not a V/G/P rung, and its headline is **CONTINGENT on Sanaa's
event-1/event-2 ruling** — under verification's reading §9.1 row 4 applies and the
elimination of mechanism #7 becomes `NOT A RESULT`.
**Cost, measured analog:** the original F4 suite cost **14.66 core-min, all 9 runs,
single-core** (`CAMPAIGN_STATUS.md:364`) = **$0.0125 derived**. A re-run under a frozen
pre-registration with grid triples is **ESTIMATED** at **~30–40 core-min** by analogy
with F3's 35.23 (same solver class, same rung structure) — **ESTIMATED from a named
analog, not measured.**

### F11 — rank 6. Buys a G and can never buy anything else.
**Missing: V and P, both permanently.** The pre-registration says so itself, before
the core-minutes are spent, which is the behaviour the lab is trying to produce:
**V is not earnable by this case at all** (the lid-driven cavity has no exact
solution; Ghia is a **numerical** benchmark, not exact/manufactured/correlation), and
**P is BLOCKED** — no Ghia PDF exists anywhere on this box, so rule 15 title-page
verification is impossible, and independently, comparing against a numerical benchmark
is **code-to-code verification, not validation**.
**Cost, from the frozen pre-registration's own §7:** **8.02 core-min predicted**,
**HARD CAP 13.0 core-min** — a cap the lane set at 13.0 rather than the brief's 40 and
justified, because *a cap 5× the prediction is a rubber stamp*. **$0.0069 predicted /
$0.0111 at cap, DERIVED NOT MEASURED.**
**Blocker that is not compute:** **C4 CANNOT BE SATISFIED AS FROZEN.** The C4 mechanism
probe (0.2478 core-min actual against a ~1 core-min estimate, ratio 0.25) established
that under `timeStep`/250 the sampler emits nothing at the early `residualControl`
stop, so **all six runs would have graded `NOT A RESULT`** — a whole wave spent
measuring a dictionary defect. Arm B is adopted and is **pre-compute**; nothing
launches until three coordinated diffs are read personally by the supervisor.
**F11's ceiling is GATE REACHED, missing V and P, and no amount of compute moves it.**

### F5b — rank 7. Frozen, honest, and stopped on a permission decision.
**Missing: all three.** Its gates read the run's own output against an
analytically-derived reference (**Theodorsen**, V material), and its §2 field 4 records
the reference **`NOT OBTAINED`**. **Trap on record:** `F5b_cylinder_re100_act.json` is
a **different case** and shares the token `F5b` and nothing else.
**Blocker that is not compute, and it is absolute:** the `physics_p1` launch was denied
by the auto-mode classifier at ~17:45Z on 2026-08-24. **The lane correctly refused to
re-route it, and nobody in cfd re-launches** — handing a denied action to a second
agent is permission laundering by another name (rule 9). **The single launch command is
on Sanaa's desk.**
**Cost, from the frozen pre-registration:** point estimate **35.0 core-min**, **cap
72.0 core-min = $0.0616 derived**. The launch wrapper's assertions A1–A5 are
**UNEXERCISED** — they are descriptions of committed code, not measurements.

### F1 — rank 8. The experiment exists; the document and the pre-registration do not.
**Missing: all three.** **F1 has the experiment and no pre-registration** — confirmed
against an enumeration of **all 44 pre-registration files** in cfd territory (42 in
`verification/campaign/`, 2 under `verification/runs/`). Its primary, AGARD AR-138, is
**not on disk**, so P fails on rule 15 and Ruling 3 at once, and V is not earnable
without a manufactured solution.
**Cost, measured analog:** F1 cost **127.5 core-min** on the record
(`CAMPAIGN_STATUS.md:453`) = **$0.109 derived**. A 3D triple would be a **multiple** of
that and is **UNCOSTED** — no frozen table exists and this lane will not invent one.

### F2, F6b, F6d, F5c — ranks 9–12. Nothing to buy.
**F2's** reference was never obtained — *"a literature-recalled `x/c ~ 0.60`, stated to
two significant figures with no retained citation"* (`VERIFICATION_CHARTER.md:1711`),
and field 4 of the §6b disclosure is **empty**. **F6b** compares to Fröhlich et al.
(2005) **LES**, which is none of exact/manufactured/correlation and so fills **no**
column; its measured cost was **34.1 core-min** (4 ranks, 511 s wall). **F6d** is a
model-form UQ study with a negative headline and a correction to F6a. **F5c** is
effectively closed: headline withdrawn, the 1.313 H figure was relaxation, Stage B
never approved and moot. **All four are `SURVEYED` and all four stay there.**

### F9, F7a, F6c, F8 — ranks 13–16. NOT HELD, and honestly so.
**F9** holds the family's cleanest V *material* — the closed-form **Womersley (1955)**
solution — and **its gate returned `GATE FAIL`**: the F9 record's own cell reads
~~`FAIL`~~ **`GATE FAIL`** as a point comparison (corrected by quote-and-strike per
standing rule 1; the record itself is not rewritten — see §11), with a
first hypothesis refuted and a cause identified (a probe station close enough to an
81 %-open orifice that convective acceleration flattens the profile). Its grid study is
explicit that *"the observed order of convergence is not consistent across triplets"*
— **0.39 / 3.47 / 0.82** depending on which three levels are taken — so **no G, and
rule 5 forbids quoting a GCI here**. Cost to date **~80.9 core-min**, corrected upward
from a prior *"well under 35 core-minutes"* claim.
**F7a** is *one of the lab's most defensible rows*: the spec was frozen at **zero
compute**, pinning the measurement definition **refuted** the ambiguity hypothesis, and
every reading lands **+7.8 % to +11.9 %** against a 5 % band — all ~~`FAIL`~~
**`GATE FAIL`** (quote-and-strike, §11). Cost **~2.4
core-min original + 387.4 core-min for the R1 audit**.
**F6c** is a structural `GATE FAIL` and was shipped as a documented failure.
**F8** returned *"NO VERDICT"*, which is the honest outcome its own pre-registration
registered in advance — **and `NO VERDICT` / `NO MILESTONE` are outside rule 1's
vocabulary**, a defect referred to cfd by the matrix owner and repeated here so it is
not lost. Neither NREL primary publishes a tabulated 7 m/s torque; `Q_ref = 800 N·m` is
**secondary tier**.

### F7b, F7c, F10 — ranks 17–19. NEVER RUN.
F7b is blocked behind F7a's gate failure under the campaign's hard ladder rule; F7c is
blocked behind F7b. **F10 has produced no record file** and is `NOT STARTED`; the
`mega-batch`'s internally-labelled "Family F10" is **a different thing** and the roster
document flags the collision itself.

---

## 5. The recipe-fork ruling, applied — and it clears the F family

**Standing ruling, held and not softened:** an observed order computed across a
**RECIPE-FORKED** gap is **`NOT A RESULT`** — a slope fitted across a change of
experiment (`VERIFICATION_CHARTER.md` §3.2) — and under standing rule 5 a row whose
triple is not a valid CONVERGING triple is `NOT A RESULT` whatever its value.
**Any F case whose G leans on a forked ladder does not have a G.**

**Two things stay explicit wherever this is written, and they are written here:**
1. **It says nothing against the underlying solves** — only against the
   grid-convergence claims built on them.
2. **The affected rows move TOWARD `NOT A RESULT`, which rule 5's one-way door
   permits — never back.** The gate can turn a `PASS` or a `GATE FAIL` *into*
   `NOT A RESULT` and not the reverse.

**Applied to the F family, the result is a null and it is worth stating as one.** The
mechanised sweep (`scripts/recipe_audit.py`, `72bc966d`) covered **461 candidate
directories, 422 parsed, 14 ladders assembled: 7 RECIPE-FORKED, 4 recipe-clean, 3
unauditable.** The seven forked ladders are `ahmed_25`, `ahmed_35`, `naca0012_wing`,
`naca4412_wing`, `motorBike`, `airliner_wing_span52` and
`credential-repair-naca4412` — **all of them 3D curriculum studies under
`models/curriculum/uq-studies/`, and NOT ONE of them is an F-family ladder.**

**So the recipe-fork ruling removes no F-family G — because the F family has no G to
remove.** That is not a reprieve; it is the same finding from the other side.

**The stated limit on the instrument travels with this citation, as it must:**
`similarity_failures()` treats **any** change of a block's grading as a similarity
failure, which is right for the uniform-background snappy ladders the sweep covers and
**wrong for a correctly-built GRADED ladder**, which must change its grading string as
it refines precisely in order to keep the first cell scaling. **F12's repaired RAE 2822
ladder is exactly such a family, so running `recipe_audit.py` against it would report a
SPURIOUS FORK.** A check that overstates its reach is worse than none.

### 5.1 Plateau — and every F ladder is UNVERIFIED on it

**Standing rule 5 clause (1) binds every F ladder whether or not its pre-registration
names it:** any level not iteratively converged **or not plateaued** →
`NOT A RESULT`. ansys-verification's VMFL051 is the worked warning: a gate deviation
**inside the band at −0.2337 %** still returned **`NOT A RESULT`** on two independent
clauses — L1 and L2 failed the frozen **plateau** clause, and the triple came back
**OSCILLATORY at R = −1.3486**, with **no GCI quoted because the values are not
monotone**. **A comfortable deviation is not a PASS.**

**Scored honestly across the F family: no F ladder is known to have plateaued, because
no F ladder has been graded under a plateau clause at all.** Every G cell in §3 is
therefore marked **UNVERIFIED on plateau**, not assumed clean. The two registered-and-
unfired ladders (F11, F12) will each have to satisfy it at grading time, and F11's C4
probe already demonstrated how a frozen sampling clause can void a whole wave before
any physics is measured.

### 5.2 The instrument constraint, observed
**cfd quotes no GCI, observed order or Richardson value from
`sdk/workflows/tmr_verification.py`** — three implementations there quote a **negative
GCI (−10.714 %) on a divergent triple**. Its geometry helpers may be used; its GCI may
not. **No such value appears anywhere in this survey.** Roache/GCI values come from
`scripts/roache_triple.py` only (blob `8dee0d31`, sha256 `452f4751…`), and this survey
quotes none, because the F family has produced none.

---

## 6. THE CENTRAL HYPOTHESIS — tested, and the conclusion is right for the wrong reason

**The hypothesis as posed:** V and P pull against each other — a case with an exact or
manufactured reference has no experiment; a case with an experiment has no exact
solution — and therefore HOLDS requires a single row carrying both kinds of reference
at once, which no amount of compute manufactures.

### 6.1 The conclusion is CONFIRMED for the F family
**Question asked: is there any F case whose frozen pre-registration establishes both a
code-verification reference and a public experimental primary?**

**Answer: NO.** Enumerated over every frozen F pre-registration on disk:

| frozen pre-registration | what it establishes | both? |
| --- | --- | --- |
| `F3_CONVERSION_PREREGISTRATION.md` | five gates, **all exact analytic** | **V only** |
| `F11_CONVERSION_PREREGISTRATION.md` | six gates vs Ghia, a **numerical** benchmark | **neither** — it says so itself |
| `F12_PREREGISTRATION.md` | Gates 1–4, **all against measured experimental data** | **P material only** (§7.1) |
| `F5b_PHYSICS_PREREGISTRATION.md` | gates vs analytic **Theodorsen**; reference `NOT OBTAINED` | **V material only** |
| `F7a_REGATE_PREREGISTRATION.md` | Martin & Moyce (1952) front position | **P material only** |
| `F8_MRF_HAND2001_GATE.md` | Hand et al. (2001) LSS torque | **P material only** |
| `F4_SIGFPE_STEP01_PREREGISTRATION.md` | a **SIGFPE crash diagnostic** | **neither** — not a V/G/P rung |
| `F6a_*`, `F6b_*`, `F6D_*`, `F5C_*` | diffusion, QCR, ERCOFTAC, relaxation-invariance, lever-isolation probes | **neither** |

**Not one frozen F pre-registration carries both.** The hypothesis's conclusion stands.

### 6.2 But the mechanism is wrong, and the correction is the actionable part
Sanaa asked to be corrected rather than confirmed. **Here is the correction.**

**The two reference kinds are not mutually exclusive per case. Three separate things
are blocking P, and only one of them is the physics she named.**

**(a) The physics constraint — real, but it binds only PART of the family.** F3, F9 and
F5b genuinely have no experiment to compare to: closed-form supersonic theory, the
Womersley solution and the Theodorsen loop are what those cases are *for*. For these,
Sanaa is exactly right and no compute helps.

**(b) A RUBRIC constraint she did not name, and it is the sharpest one.** The rubric
lists **"correlation"** as a **V** instrument, and **Ruling 4's exclusion list also
contains "correlation"**. So an **empirical correlation — a fit to measured
experimental data — is definitively V and definitively not P.** The consequence is
counter-intuitive and it bites two F cases hard: **F4's Billig (1967) standoff
correlation and F5a's Roshko–Williamson Strouhal relation are among the most
physically-grounded references in the whole family — both are fits to wind-tunnel
measurements — and the rubric spends both on V and forbids either from buying P.**
This is not a fact about the flow; it is a fact about the scoring, and unlike (a) **it
is reversible by a ruling rather than by procurement.** *Stated as an observation for
the rubric's owner; cfd does not propose to change verification's ruling.*

**(c) A PROCUREMENT constraint, and it is the largest by count.** Where an experiment
*does* exist, P mostly dies on **document holding**, not on physics. Measured on disk
with a **non-ignoring** `find` over `docs/papers/` (237 files):

| F case | experimental primary needed | on disk? |
| --- | --- | --- |
| F12, F1 | Cook / McDonald / Firmin, **AGARD AR-138** (1979) | **NO** — a full-text sweep returns three files that merely *cite* it |
| F11 | **Ghia, Ghia & Shin (1982)** *(numerical anyway)* | **NO** — nothing under `docs/papers/`, nothing filesystem-wide |
| F7a | **Martin & Moyce (1952)** | **NO** — the held artefact is a 600 dpi digitisation of a **2021** figure |
| F8 | NREL/TP-500-29955 and -29494 | **held values are secondary**; neither report publishes a tabulated 7 m/s torque |
| F5a (Re 1000) | **Williamson & Brown (1998)** | **NO** |
| F5a (Re 2000) | any primary reporting St at Re = 2000 | **`NOT OBTAINED`** — fallback was a 2014 thesis figure |
| **F5a (Re 40–150)** | **Roshko (1954), NACA Report 1191** | **YES — HELD, AND TITLE-PAGE VERIFIED BY THIS LANE** |

**THE RULE-15 VERIFICATION, done by this lane and disclosed as its own act.**
`docs/papers/turbulence_models/roshko_1954_naca_tr_1191.pdf` (26,719,255 B) was opened
and **page 1 was rendered and read** — *not* checked by filename, file type or hash,
which rule 15 forbids. The title page reads: **REPORT 1191 — ON THE DEVELOPMENT OF
TURBULENT WAKES FROM VORTEX STREETS — By ANATOL ROSHKO — California Institute of
Technology — National Advisory Committee for Aeronautics.** Its `.txt` sidecar is
**284,526 B of real text**, not a stub. The document carries the fitted relation
**S = 0.212(1 − 21.2/R)** for the stable range **40 < R < 150**, states *"it is
believed that the best-fit line is accurate to 1 percent"*, and carries **Figure 5,
"Strouhal number against Reynolds number for circular cylinder"** — the measured
points themselves.

**(d) And the asymmetry that makes all of this actionable: V is manufacturable; P is
not.** A **manufactured solution** can be constructed for any solver at will — that is
the entire point of MMS — so **the lab can always ADD a V to any case it can run**. No
procedure manufactures a P. **The constraint is therefore not symmetric "pull"; it is
one cheap column and one expensive one**, and every hour spent hunting for cases that
happen to carry both is an hour not spent on the only two things that actually bind:
**acquiring one primary document, and running one honest triple.**

### 6.3 What a row would need to carry all three — and whether the lab has the ingredients
**A HOLDS row needs, simultaneously:**
1. a **frozen pre-registration** predating first compute, with the gate, threshold, cap
   and label committed and the grading path fixed by blob sha;
2. an **exact, manufactured or correlation** reference, compared against → **V**;
3. an **equal-ratio, recipe-clean, geometrically similar** triple that comes back
   **CONVERGING and plateaued**, with GCI at Fs = 1.25 and an observed order → **G**;
4. a comparison against **measured physical reality** from a primary the lab **HOLDS
   and can READ**, title-page verified → **P**;
5. and the V and P comparisons must be **two distinct comparisons**, not one reference
   counted twice — Ruling 4's stated rationale is precisely that *"reading P to cover
   them too would let one comparison score two columns."*

**Does the lab have the ingredients? For exactly one F case, yes — and clause 5 is
where it is fragile.**
**F5a, the 2D cylinder at Re 100:** (1) buildable at zero compute; (2) available —
though if V is taken as the Roshko–Williamson *correlation* and P as Roshko's *measured
points*, **clause 5 is arguably violated, because the correlation is a fit to those
same points**; the clean fix is to take V from a **manufactured solution** instead,
which owes nothing to Roshko; (3) buildable — a 2D cylinder equal-ratio triple is
geometrically unproblematic and cheap; (4) **available and verified, uniquely in this
family** (§6.2).

**That is the lab's shortest path to its first HOLDS, and it is not the path currently
being walked.**

---

## 7. Two places this survey would score differently from the matrix — stated, not acted on

### 7.1 F12 carries no V — the brief's worked datum, verified rather than inherited
**CONFIRMED, and it is stronger than the brief put it.** Reading the HEAD blob of
`verification/campaign/F12_PREREGISTRATION.md` (**736 lines**), the only V-type tokens
— `exact solution`, `manufactured`, `correlation` — occur at **exactly three lines:
567, 596 and 735**, and all three are **flat-plate correlations used to size the mesh
for y+**:
- **:567** — three standard flat-plate correlations (Schlichting 1/5-power, 1/7-power,
  Prandtl–Schlichting) at `Re_c = 6.5e6`, used to convert a wall distance to y+;
- **:596** — a flat-plate correlation with an assumed edge velocity, giving the
  leading-edge factor 1.709;
- **:735** — the closing provenance note, recording that the y+ arithmetic used *"named
  flat-plate correlations"* and that **all of it is ESTIMATED and none of it is
  measured**.

**None is a gate, and the document says so itself in its own words at :601-602:**
*"The 1.71 column is ESTIMATED, from a flat-plate correlation with an assumed edge
velocity; it is not measured and **it is not a gate**."*

**The gates are Gates 1–4 and every one of them is against measured experimental
data:** Gate 1 Cp RMS ≤ **0.08** upper / **0.04** lower; Gate 2 shock location ≤
**0.020** chord by the sonic crossing; Gate 3 |CN − 0.803|/0.803 ≤ **5 %**; Gate 4
|CD − 0.0168|/0.0168 ≤ **20 %**; CM reported and not gated.

**So F12 carries no V. The brief is right, and I could not find a clause that refutes
it.** The matrix's own §3.5 row already leaves F12's V cell as "—" rather than green,
which is consistent.

### 7.2 Two scoring questions this survey refers upward rather than settling
**(a) F7a's P cell — an internal conflict in the matrix, reported not fixed.**
`COVERAGE_MATRIX.md` §3.5 scores F7a's P as **"YES — experiment, public primary, spec
frozen on disk"**. But that same file's **Ruling 3** says a benchmark reached through a
secondary does not make P green, and `VERIFICATION_CHARTER.md:1713` records F7's
Martin & Moyce reference as **`NOT OBTAINED` as a primary**, the held artefact being a
600 dpi digitisation of a **2021** figure. **These cannot both be right.** **No tier
moves either way** — F7a is `NOT HELD` because its gate returned `GATE FAIL`, which is upstream of
the P question — so this is a cell defect, not a tier defect. **Referred to the matrix
owner; cfd does not edit `docs/COVERAGE_MATRIX.md`.**

**(b) The "under a frozen pre-registration" qualifier in Ruling 1.** Ruling 1's final
form awards `GATE REACHED` to 1–2 green columns **"under a frozen pre-registration"**.
Several F rows' V-greens — F3's, F4's, F5a's — rest on comparisons made **before** any
pre-registration existed; that absence is the very defect the F3 and F11 conversion
pre-registrations were written to repair. Read strictly, those rows are `SURVEYED`
rather than `GATE REACHED`. **The §3 table follows the matrix owner's already-entered
tiers where they exist** (F3 and F4 are entered as `GATE REACHED`) and flags the
question here. **It is the owner's to rule, not cfd's.**

---

## 8. THE BEST AVAILABLE ALTERNATIVE — what would actually buy the lab a HOLDS

**Since no F case can reach HOLDS as it stands, here is the ranked alternative, and the
first item is a proposal rather than a run.**

### 8.1 The ranked GATE REACHED rows, each naming its gap
1. **F3** — `GATE REACHED`, **missing G and P**. G is **35.23 core-min** away under a
   frozen, armed, unfired pre-registration with a **39.5 core-min hard cap**. **P is
   permanently unreachable.** *Best core-minutes-per-column in the family.*
2. **F12** — **missing V**, with G registered-and-unfired and P contested. **383.5
   core-min estimated / 1,300 capped.**
3. **F11** — **missing V and P, both permanently**. **8.02 core-min / 13.0 capped**, and
   **C4 is unsatisfiable as frozen** until arm B's three pre-compute diffs are read.
4. **F4** — **missing G and P**, and **no conversion pre-registration is written**.
5. **F6a** — **missing V**, with a real experiment whose primary is **unverified on
   disk**.

### 8.2 The proposal — F5a-MMS, and it is cheap
**A cylinder row that carries all three columns at once.** The claim being made is that
**this is the only F-family row for which every one of the five clauses in §6.3 is
satisfiable**, and the reason is §6.2's document check.

- **V** — a **manufactured solution** on the same solver and the same mesh family.
  Owes nothing to Roshko, so **clause 5 is clean** and the double-count objection in
  §6.3 does not arise.
- **G** — an equal-ratio 2D triple, `r = 2` by construction, `dim = 2` explicit,
  `form="equal"` asserted so the instrument **refuses** an unequal ladder, graded
  through `scripts/roache_triple.py` only, **with a plateau clause registered in
  advance** (§5.1).
- **P** — Strouhal against **Roshko's own measured points**, from the primary at
  `docs/papers/turbulence_models/roshko_1954_naca_tr_1191.pdf`, **held, readable and
  title-page verified** (§6.2), in the stable range **40 < R < 150** the paper itself
  delimits.

**The one open question, and it is not cfd's to answer:** whether digitising **Figure 5
of a primary the lab holds and has opened** is a primary reading, as against F7a's
digitisation of a **2021 secondary**. Ruling 3's own words are *"`P` is green only
against a source the lab HOLDS and can read"* — which Roshko satisfies and the F7a
artefact does not. **This is verification's rubric call. It is stated here and it is
not decided here.** If it is ruled the other way, F5a's P dies with every other P in
the family and **the finding becomes: the F family cannot produce a HOLDS at all.**

**Cost: UNCOSTED, deliberately.** No frozen pre-registration exists for F5a and no
measured core-minute figure for it appears in `CAMPAIGN_STATUS.md:458`. The nearest
named analog, F11's 2D equal-ratio triple at **8.02 core-min**, is **steady** where a
Strouhal ladder is **unsteady**, so it does not transfer and this lane will not
extrapolate it into a number that would then get quoted as if it were measured.
**The first deliverable is a costed pre-registration at zero compute, not a run.**

### 8.3 Out of the F family — noted, not annexed
The lab's strongest P *material* outside F is **Meinders**, whose primary is **on disk
and title-verified by page render** — its `.txt` sidecar is a **281-byte stub of
form-feeds** and the PDF has no text layer, so a **sidecar check would have verified
NOTHING while looking like it had**. That is the same rule-15 trap this survey avoided
in §6.2 by rendering the page. **But Meinders is T5, a heat-transfer rung, and it is
that team's to run, not cfd's to annex.**

---

## 9. Blockers that are not compute — the consolidated list

| case | blocker | class |
| --- | --- | --- |
| F1 | AGARD AR-138 **not on disk**; **no pre-registration exists at all** | missing primary + missing prereg |
| F2 | reference **`NOT OBTAINED`**, §6b field 4 **empty** | missing primary |
| F3 | **P is impossible** — exact theory admits no experiment | structural |
| F4 | **no conversion pre-registration written**; headline **CONTINGENT** on Sanaa's event ruling | missing prereg + open ruling |
| F5a | **no pre-registration exists**; Williamson & Brown not on disk; Re 2000 `NOT OBTAINED` | missing prereg + missing primary |
| F5b | **launch BLOCKED on a permission decision — Sanaa's alone**; reference `NOT OBTAINED` | permission |
| F6a | NASA hump primary-on-disk status **UNVERIFIED**; no prereg for the hump gate | unverified primary |
| F7a | Martin & Moyce held only as a **2021 digitisation** | secondary transcription |
| F7b, F7c | **BLOCKED** behind F7a's gate failure | ladder rule |
| F8 | **neither NREL primary publishes a tabulated 7 m/s torque**; `NO VERDICT` / `NO MILESTONE` are **outside rule 1's vocabulary** | missing datum + vocabulary defect |
| F10 | **no record file exists**; id collides with `mega-batch`'s internal "Family F10" | never started + id collision |
| F11 | **C4 unsatisfiable as frozen**; no Ghia PDF on the box; **V not earnable at all** | frozen-clause defect + structural |
| F12 | **AGARD AR-138 not held**; rule 15 verification of the primary **IMPOSSIBLE**; **no V at all** | missing primary + structural |
| F13 | **never allocated** | not a case |

### 9.1 One provenance defect, REPORTED and NOT fixed silently

**`verification/campaign/F3_CONVERSION_PREREGISTRATION.md` line 14 still introduces its
motivating text as "Sanaa's directive, verbatim":**

> *"CFD team — Re-run under frozen pre-registrations, <40 core-min each: F3
> (supersonic exact suite), F11 (per capability map), F4 (hypersonic) — the early
> PASSes that lack prereqs convert to HOLDS."*

**That attribution was WITHDRAWN by this team.** A non-ignoring `find | xargs grep`
sources the text to exactly two places — `docs/LAB_STATE.md` and cfd's **own** commit
messages `2bf4915a` and `157793db` — **and to nothing Sanaa said.** It is a **cfd
brief's paraphrase** and is cited as one throughout this survey. **It is never
reproduced as her words and it is never treated as a compute authorisation.**

**`F11_CONVERSION_PREREGISTRATION.md` carries the withdrawal properly**, as a dated
addendum that strikes the attribution, keeps the words and re-marks them as a brief's
paraphrase. **`F3_CONVERSION_PREREGISTRATION.md` does not.** It is a frozen document,
so the repair is a **dated addendum appended at the foot** under standing rule 6 — not
an edit — and it is **reported here for the supervisor to dispatch, not fixed by this
lane.**

**A second wording defect in the same quotation, already on record and repeated so it
is not lost:** the paraphrase calls these *"the early PASSes"*. **F11's 2026-07-30
verdict is `GATE REACHED`, not a `PASS`**, and the phrase does not describe that
family.

---

## 10. What this lane could not verify

Stated plainly, because an honest gap is worth more than a confident guess.

1. **Whether the NASA hump primary behind F6a is on disk and title-page verifiable.**
   Not checked. F6a's P is marked **UNVERIFIED**, not green and not absent.
2. **Whether Roshko's Figure 5 can be digitised to a usable band.** The figure exists
   and the paper states the best-fit line is *"accurate to 1 percent"*; **the digitisation
   itself was not attempted and no band is proposed here.**
3. **Whether the F5a MMS proposal's V and P would be ruled two distinct comparisons.**
   §6.3 clause 5 and §8.2 both flag it. **Verification's call.**
4. **Whether F7a's P cell or Ruling 3 is the one that is wrong** (§7.2a). Reported as a
   conflict; not adjudicated.
5. **Costs for F5a, F1's 3D triple, and any manufactured-solution rung.** **UNCOSTED.**
   No frozen table exists for any of them and none is guessed at.
6. **Whether any F ladder has plateaued.** None has been graded under a plateau clause,
   so every G cell is **UNVERIFIED on plateau** (§5.1) rather than assumed clean.
7. **The `docs/papers/` sweep was a filename-and-sidecar sweep**, so a primary filed
   under an unrelated name with no matching sidecar text would have been missed. It is
   corroborated by, not a substitute for, the full-text sweeps already on record for
   AGARD AR-138 and Ghia.

---

## 11. Vocabulary corrections made in this file, by quote-and-strike

**Standing rule 1 fixes the verdict vocabulary: `PASS` / `GATE REACHED` / `GATE FAIL` /
`NOT A RESULT` / `BLOCKED` / `PENDING`.** Two legacy cells quoted in this survey read a
bare **`FAIL`**, which is outside that vocabulary. `VERIFICATION_CHARTER.md` v1.9's
amendment item 1 records the same collision as an open, unruled conflict.

**They are corrected HERE, in this file only, by quote-and-strike — the source records
are NOT rewritten** (standing rule 6: a frozen record is departed from by a dated
amendment at its foot, never by an edit):

| source cell | as it reads | as it is read here |
| --- | --- | --- |
| `F9_pulsatile_valve.md`, Gate 2 | ~~`FAIL`~~ | **`GATE FAIL`** |
| `COVERAGE_MATRIX.md` §3.5, F7a row (*"all FAIL a 5 % band"*) | ~~`FAIL`~~ | **`GATE FAIL`** |

**Neither correction moves a tier or a verdict.** F9 is `NOT HELD` and F7a is
`NOT HELD` under either spelling. **Dispatching the dated amendments to the source
records is the supervisor's call, not this lane's** — and `docs/COVERAGE_MATRIX.md` is
verification's file, which cfd does not edit at all.

**A third vocabulary defect is reported and NOT corrected**, because it is not a
misspelling of a rule-1 word but a pre-registered branch label: **F8 grades
*"NO VERDICT"* and *"NO MILESTONE"***. These were legitimately registered in advance,
they are outside rule 1, and **a lab-wide sweep for verdicts does not see them.**
Already referred to cfd by the matrix owner; repeated here so it is not lost.

---

*Written 2026-08-25 by a `lab-lane` for the cfd team on a supervisor-directed
**ZERO-COMPUTE** task. No solver was launched, no mesh was built, no case directory was
created. Tier words are the matrix owner's five; verdict words are CLAUDE.md rule 1's
six; the two vocabularies are kept apart throughout. cfd defines no V, G or P of its
own here and applies `docs/COVERAGE_MATRIX.md`'s rubric verbatim.*
