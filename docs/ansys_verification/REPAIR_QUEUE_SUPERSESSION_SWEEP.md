# SUPERSESSION SWEEP OF THE REPAIR QUEUE — ALL 35 ROWS AT ONCE

**Team:** ansys-verification (opus lane). **Date:** 2026-08-31. **Zero compute — every number
below is read off an artifact already on disk.**

**Sources, by absolute path:**
- `/home/ubuntu/Certonomous/docs/ansys_verification/REPAIR_QUEUE.md` — the 35 rows in five tiers
- `/home/ubuntu/Certonomous/verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` — rows 1..51
- `/home/ubuntu/Certonomous/docs/ansys_verification/REGISTER_ID_CELL_AUDIT.md` — the id-cell hazard

**NOTHING IS RE-GRADED HERE.** No row's verdict moves. No register byte changes. `REPAIR_QUEUE.md`
is not edited. **Supersession is a queue fact, not a verdict change**, and every superseded row
stands on the register exactly as it was written.

---

## THE ANSWER FIRST

> **THE TRUE BACKLOG IS 14 ROWS, NOT 35. Twenty-one of the queue's thirty-five rows — 60 % —
> were already closed, already landed at their honest ceiling, or blocked by the manual itself
> before this queue was written.**
>
> **And the 14 open rows are not 14 pieces of work. They are 10 successor registrations over
> 8 distinct root defects, of which 6 are startable tonight for a combined 301.5 core-min
> ($0.2578 DERIVED, NOT MEASURED).**

| bucket | rows | count |
|---|---|---|
| **SUPERSEDED — COMPLETE** | 1, 18, 21, 25, 26, 27, 29, 31, 33, 40, #47, #49 | **12** |
| **SUPERSEDED — PARTIAL** | — none — | **0** |
| **CEILING-TERMINAL** (already `GATE REACHED` at the referent ceiling; no repair exists) | 20, 22, 23, 24, 30, 35, 39, 43 | **8** |
| **SOURCE-BLOCKED** (no gate registrable from the manual — not a hardware or effort problem) | 41 | **1** |
| **GENUINELY OPEN — CPU** | 4, 6, 9, 10, 11, 12, 14, 16, 17, 32, 37, #44 | **12** |
| **GENUINELY OPEN — GPU-BLOCKED for execution** | 34, 42 | **2** |
| | **total** | **35** |

**GPU-BLOCKED is 2 rows, not 7.** The brief lists seven GPU rows (33, 34, 39, 40, 41, 42, 43).
**Five of them need no GPU at all:** 33 and 40 are superseded (a paper fact); 39 and 43 **already
ran on the GPU and already landed `GATE REACHED`**; 41 is blocked by an evidence gap in the manual,
which no hardware fixes. Only 34 and 42 are open work waiting on the stopped instance.

---

## 1 — SUPERSEDED, COMPLETE: TWELVE ROWS, AND THE REGISTER SAYS SO ON THE SUCCESSOR'S FACE

For each: the successor's row id, its verdict, and the register's own phrase — quoted verbatim from
the successor's Case cell. **Two of these successors use the word "superseded" literally.**

| row | case | successor | successor verdict | the register's own words, on the successor's face |
|---|---|---|---|---|
| **1** | VMFL001 | **2** VMFL001-R2 | `PASS` | *"Re-run of row #1 after that row's `NOT A RESULT`, per `VERIFICATION_CHARTER.md` §6: a new row citing the old one, which is not removed, re-labelled or softened."* Row 2's Tolerance cell: band *"unchanged from row #1's freeze"*. |
| **18** | VMFL021 | **23** VMFL021-R2 | `GATE REACHED` | Established in `REPAIR_QUEUE.md` tier 2 and re-confirmed here: same case (p. 85 Case A), same gate `Cd`, same reference (Nurick 0.620), same 5 % band. |
| **21** | VMFL033 | **#48** VMFL033-R2 | `PASS` | *"A NEW REGISTRATION SUCCEEDING R1, NOT AN EDIT OF IT — R1 landed `NOT A RESULT` as row #21."* |
| **25** | VMFL004 | **28** VMFL004-R2 | `PASS` | *"re-registration of row #25 … Same case, same mesh family, **case files a verified byte-identical copy**."* |
| **26** | VMFL011 | **36** VMFL011-R3 | `GATE FAIL` | *"third attempt, cites rows #26 and #31, re-grades nothing"* … *"**Cites superseded rows #26 and #31**; those trees/preregs/comparators preserved."* Gate frozen *"byte-identical to attempts 1 and 2"*. |
| **27** | VMFL076 | **35** VMFL076-R2 | `GATE REACHED` | *"re-registration of row #27 under ANSYS_VERIFICATION_CHARTER §6, cites it, re-grades nothing"* … *"**Cites superseded row #27**; R1 tree/prereg/comparator preserved."* |
| **29** | VMFL064 | **30** VMFL064-R2 | `GATE REACHED` | *"Re-registration of row #29 … a NEW row that CITES row #29 and does NOT overwrite it"* … *"**Every gate-path constant is byte-identical to attempt 1** — reference, band, ceiling, mesh family, cap, `endTime`."* |
| **31** | VMFL011-R2 | **36** VMFL011-R3 | `GATE FAIL` | Same phrase as row 26 — row 36 names **both** as superseded. |
| **33** | VMFLGPU001 | **39** VMFLGPU001-R2 | `GATE REACHED` | *"**Successor to VMFLGPU001 (R1), row #33** (`NOT A RESULT` at plateau clause I5) — a fresh registration carrying two repaired CONTROLS, **every gate constant byte-identical to R1**."* |
| **40** | VMFLGPU007 | **43** VMFLGPU007-R2 | `GATE REACHED` | *"**RE-REGISTRATION of row #40 (VMFLGPU007, R1)** … it SUCCEEDS R1, which is FROZEN and PRESERVED and is NOT re-graded; R1's row #40 stands `NOT A RESULT`."* |
| **#47** | VMFL038 | **#51** VMFL038-R2 | `PASS` | *"NEW registration succeeding row #47 (`NOT A RESULT`) per VERIFICATION_CHARTER §6."* |
| **#49** | VMFL006 | **#50** VMFL006-R2 | `PASS` | *"Re-run succeeding row #49 (`NOT A RESULT`) per VERIFICATION_CHARTER §6."* |

### WHY ALL TWELVE ARE COMPLETE AND NONE IS PARTIAL — a structural fact, not a coincidence

**I looked for PARTIAL and found none.** The reason is uniform and it is the row-18 reason
generalised: **every one of the twelve superseded rows is `NOT A RESULT`, and a `NOT A RESULT` row
carries no certified gate value.** Its residual credentialed coverage is **zero by construction** —
there is nothing for the successor to fail to cover. In each case the successor also carries the
gate constants forward byte-identically (rows 28, 30, 36, 39, 43 say so explicitly), so the
comparison is like-for-like on reference, band, ceiling and mesh family.

**THE ONE PLACE A READER COULD REASONABLY DISAGREE, stated rather than buried: row 27 → row 35.**
Row 35's *only* change vs R1 is a **strictly COARSER** triple (600 / 2 400 / 9 600 cells). R1's finer
mesh data is therefore **not** reproduced by R2. I still class it COMPLETE, because row 27 is
`NOT A RESULT` and its finer-family numbers are not a credential — but the asymmetry is real and a
supervisor who wants the finer-mesh evidence preserved should know R2 does not carry it.

### THE QUEUE COUNTS FIVE PARENT/SUCCESSOR PAIRS AS TEN SEPARATE ROWS

Rows **18 & 23**, **29 & 30**, **27 & 35**, **33 & 39**, **40 & 43** are five pairs in which
**both halves sit in the same queue** — the dead parent in one tier and the landed successor in
another. That is the single largest source of the overstatement, and it is visible from the row ids
alone once you look for `-R2`.

---

## 2 — CEILING-TERMINAL: EIGHT ROWS THAT ARE FINISHED, NOT BROKEN

**These eight rows read `GATE REACHED` in the register's verdict column TODAY.** I counted the whole
register: **there are exactly eight `GATE REACHED` rows in it — 20, 22, 23, 24, 30, 35, 39, 43 — and
all eight are queue tier 4.** They are precisely the eight the queue's own tier-4 preamble points at
when it says *"this team has eight of them."*

**Tier 4's stated purpose is to "convert" these rows to clean `GATE REACHED` credentials. They are
already clean `GATE REACHED` credentials.** The conversion has happened. There is no work here.

| row | case | verdict | referent under the exact-PDE rule | why no repair can raise it |
|---|---|---|---|---|
| 20 | VMFL036 | `GATE REACHED` | **DIFFERENT** — code-to-code (Mittal 1999 / Tabata & Itakura 1998, computed spectral solutions) | *"buys NEITHER V NOR P and the TIER CEILING is `GATE REACHED`, frozen as the ceiling on pre-registration lines 3–4 and hard-coded in the comparator"* |
| 22 | VMFL023 | `GATE REACHED` | **DIFFERENT** — experimental St–Re correlation (White 1994 / Kim & Lee 2002) | correlation; caps however clean the run |
| 23 | VMFL021-R2 | `GATE REACHED` | **DIFFERENT** — experimental (Nurick 1976) | experiment; caps |
| 24 | VMFL002 | `GATE REACHED` | **DIFFERENT** — manual printed Target (White 1994 / Incropera 1981) | both gates already inside 2 % on two `CONVERGING` triples; 5.2 core-min measured |
| 30 | VMFL064-R2 | `GATE REACHED` | **DIFFERENT** — experimental (Armaly et al. 1983) | *"the ceiling was lowered in advance"*; 2.9389 % of a 10 % band |
| 35 | VMFL076-R2 | `GATE REACHED` | **DIFFERENT** — similarity solution (reduced boundary-layer model) | *"V present (similarity reference), P not attainable (tier ceiling frozen at `GATE REACHED`)"* |
| 39 | VMFLGPU001-R2 | `GATE REACHED` | ceiling **frozen** at `GATE REACHED` and *"hard-coded in the comparator, which cannot print `PASS`"* | all three limbs held, triple `CONVERGING` — ceiling HELD |
| 43 | VMFLGPU007-R2 | `GATE REACHED` | **DIFFERENT** — experimental (Vogel & Eaton) for limb C | limb C inside its band under the experimental ceiling |

**I DID NOT MANUFACTURE PASS-CAPABILITY FOR ANY OF THESE, AND THE HONEST STATEMENT IS THAT NONE IS
AVAILABLE.** `VERIFICATION_CHARTER §2h.8.1 (v1.28, 2026-08-31, the exact-PDE rule)` — the same words
frozen as `§2h.6.1` at v1.27, see §5 below — caps a reference *"drawn from a DIFFERENT MODEL —
nozzle relations, shock tables, lumped or series-resistance paths, correlations, experiment"* at
`GATE REACHED` **"HOWEVER EXACT ITS OWN ALGEBRA."** Eight `GATE REACHED` rows honestly reached are
eight real results.

## 2a — SOURCE-BLOCKED: ROW 41, AND NO RUN FIXES IT

Row **41** (`VMFLGPU004`, Anisotropic Conduction, manual pp. 233–234) is `BLOCKED`. Its register
cell: *"**NONE. The manual cites no reference for this case**, and prints no numeric target — only a
figure … the analytical solution depends on the conductivity matrix the manual does not supply, so
the analytic route is closed by the same absence that closes the input route. **No gate could be
registered.**"* Six named absences in the source document. Zero core-minutes, zero GPU-h spent.
**This is an evidence gap in the manual, not a defect this lab can repair, and it is not a GPU
blocker either** — restoring the GPU instance changes nothing about it.

---

## 3 — GENUINELY OPEN: 14 ROWS → 10 SUCCESSOR REGISTRATIONS → 8 ROOT DEFECTS

**Two root defects each account for more than one open row:**

1. **The VMFL003 unmeetable convergence clause accounts for FIVE rows — 6, 9, 10, 11, 12.** One case
   (manual p. 19), one gate quantity (Δp), one reference (21 744 Pa), one frozen band (2.5 %), one
   frozen leg (`RESID_TOL = 1.0e-8` on `p, Ux, k, ε/ω`). Row 6 is `simpleFoam` + **`kEpsilon`** +
   `nutkWallFunction`; row 9 (arm A) is the **same model** and reproduces row 6's gate value to nine
   significant figures — `20 800.824487444752` Pa vs `20 800.824488339003` Pa on the same `L3_1000x5`.
   Rows 10, 11, 12 are the same case under `realizableKE`, `RNGkEpsilon`, `kOmegaSST`.
   **These are ONE repair, not five.**
2. **The flow-split gate-design defect accounts for TWO rows — 14 (CPU) and 34 (GPU).** Same gate
   quantity (flow split), same reference (0.887, Hayes/Nandkumar/Nasr-El-Din 1989), same failure
   (`OSCILLATORY` triple). One gate redesign serves both; only the GPU limb waits on hardware.

**AND I MUST REPORT A ROW THAT IS *NOT* SUPERSEDED WHERE THE SHAPE INVITED IT.** Rows 9–12 cite run-1
row #6 on their faces — but they cite it, they do not succeed it. **No register row anywhere says
"successor to", "re-run of" or "re-registration of" for rows 4, 6, 9, 10, 11, 12, 14, 16, 17, 32, 34,
37, 42 or #44.** I checked every `-R2`/`-R3` case id in the register against each. There is no
`VMFL051-R2`, no `VMFL010-R2`, no `VMFL059-R2`, no `VMFL022-R2`, no `VMFL017-R3`, no `VMFL007-R3`, no
`VMFL063-R2`, no `VMFLGPU002-R2`, no `VMFLGPU005-R2`. **These fourteen rows survive checking as open.**

### THE RANKING — genuinely-open CPU work by real repair cost, cheapest first

Every core-minute figure below is **extrapolated from that case's own measured `COST.txt` /
`RUN_RC.txt` figure already in the register**, at ranks = 1. Dollars are **DERIVED, NOT MEASURED**, at
`$0.0513/core-h` (c7a.4xlarge, owner-stated 2026-08-21/22) — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

| # | row | case | measured spend to date | **repair SHAPE** | **est. repair, core-min** | **$ DERIVED** | §12.2 / exact-PDE ceiling |
|---|---|---|---|---|---|---|---|
| 1 | **16** | VMFL059 | 0.4167 | **gate redesign** — `rightWall` triple is `EXACT` (378.0 / 378.0 / 378.0); refinement carries no information, so the *quantity* must change, not the mesh | **1.5** | $0.0013 | **SAME** — closed-form analytic conduction (Incropera & Dewitt) is the exact solution of the same conduction PDE the solver discretises → **`PASS` available** |
| 2 | **14** | VMFL010 | 3.5833 | **gate redesign** — triple `OSCILLATORY` (0.8859 / 0.8845 / 0.8847); needs a family that resolves the split monotonically | **15** | $0.0128 | **DIFFERENT** — code-to-code benchmark → ceiling `GATE REACHED`, already declared in the R1 freeze |
| 3 | **17** | VMFL022 | 8.43 | **gate redesign** — triple `OSCILLATORY` (`R = −0.104878`, `p` and `GCI_fine` both `None`) | **35** | $0.0299 | **DIFFERENT** — experimental (Nurick 1976) → ceiling `GATE REACHED` |
| 4 | **37** | VMFL007-R2 | 9.2167 | **FULL FRESH TRIPLE — NOT an instrument fix.** *(the brief's own example, and I confirm it)* | **60** | $0.0513 | **SAME** — see the note below → **`PASS` available** |
| 5 | **4** | VMFL051 | 23.3167 | **longer `endTime` + re-registration** — rule 5 step 1 killed it (L1 and L2 never plateaued), not the physics: the value is **inside** the frozen ±0.5 % band by 2.14× | **70** | $0.0599 | **SAME** — Prandtl–Meyer is the exact solution of the steady Euler system `rhoCentralFoam` discretises inviscid → `PASS` available *(caveat below)* |
| 6 | **#44** | VMFL063 | 13.8333 | **gate redesign + finer levels** — `p = 0.143328`, `GCI_fine = 120.62 %`, still moving at L3 | **120** | $0.1026 | **DIFFERENT** — experimental (Lane & Loehrke 1980) → ceiling `GATE REACHED` **by construction (§3 of its own prereg)** |
| — | **6, 9, 10, 11, 12** | VMFL003 family | 154.534 total (13.5 + 29.962 + 31.152 + 39.93 + 39.99) | **REFERRED TO SANAA — not lab-actionable.** The only repair is a change to a **frozen convergence threshold**, reserved under `ESCALATION_CHARTER` §4.1 / D539 | 150 *if authorised* | $0.1283 | **DIFFERENT** — Moody-chart smooth-pipe branch, an empirical correlation → ceiling `GATE REACHED`; `PASS` unavailable and none sought |
| — | **32** | VMFL017-R2 | 300.0 (L1 cap, as registered) | **instrument change** — a supervisor solver decision, not a lane's | **NOT ESTIMABLE FROM DISK** | see below | **DIFFERENT** — experimental (Cook/McDonald/Firmin, AGARD AR-138) → ceiling `GATE REACHED` |

**Six startable CPU items: 1.5 + 15 + 35 + 60 + 70 + 120 = 301.5 core-min = 5.025 core-h =
$0.2578 DERIVED, NOT MEASURED.** Every one is inside the $25/run pre-authorisation, and the six
together cost about one hundredth of it.

**ROW 32'S COST IS NOT ESTIMABLE AND I WILL NOT INVENT ONE.** The only measured projection on disk is
the *infeasible* one: with the registered `rhoCentralFoam` instrument the full triple is
**≈ 1 231 583 core-min ≈ $1 053.00 DERIVED**, 42× the $25 blanket, from the measured L1 rate. That
number prices the instrument we are replacing, so it does not price the repair. **No artifact on disk
bounds the cost of the replacement instrument**, and a figure produced without one would be an
estimate presented as a measurement.

### NOTE ON ROW 37 — the brief's example, confirmed on the row's own text

Row 37 sits in the queue's `INSTRUMENT` tier and its record does contain a real instrument defect
(the comparator refused at its planted-zero control — planted `0.001234` at row 5000 of arm A1's
`pInlet` series and read back a change of **0**). **But no instrument repair can ever give this row a
verdict**, because its own Case cell says: *"**SINGLE-GRID, no Roache triple — verdict ceiling
`NOT A RESULT` by construction (rule 5).**"* It is a six-arm solver/preconditioner *screening slate*,
built to choose a stable arm for a future R3. **The repair is the R3 triple that slate was screening
for.** Cause class `INSTRUMENT`; repair class **full fresh triple**.

**And its ceiling runs the other way from the register's older annotation.** Row 37's Reference cell
reads *"closed-form / exact — buys V, never P."* Under `§2h.8.1` the test is **sameness of model**:
the Rabinowitsch–Mooney closed form is the exact solution of the **same** continuum momentum equation
`simpleFoam` + `powerLaw` discretises for fully-developed pipe flow. That is **SAME**, and `PASS` is
available — the identical argument row **#51** (VMFL038-R2) used for Bird/Stewart/Lightfoot's `tau_w`,
which the register calls *"the EXACT solution of the same continuum model `simpleFoam` discretises, so
model-form error is zero by construction"* and which landed **`PASS`**. Flagged for the supervisor's
read; **no row is re-labelled here.**

### NOTE ON ROW 4 — a mixed precedent, and it must be settled before the freeze

VMFL051's referent is the manual's printed Mach target for a centred Prandtl–Meyer fan, exact for the
steady Euler equations, which is what `rhoCentralFoam` integrates with viscosity off — **SAME** on the
exact-PDE test. **But this team's own sibling row #7 (VMFL045-R2, the analytic oblique shock — the
same shock-family question) landed `PASS` carrying tier `GATE REACHED`.** The precedent is mixed.
`ANSYS_VERIFICATION_CHARTER` §12.2 is explicit that this is decided *"IN THE REGISTRATION, BEFORE
COMPUTE. NEVER AT GRADING"* — so row 4's successor must answer §12.2's four questions on its face
before its freeze, and I do not pre-empt that answer here.

**And row 4 has the clean rule-2 escape.** Its gate value already met the band, so a successor written
now would be written by someone who has seen the answer — *unless* the band is carried **byte-identical
from row 4's own freeze**, which is exactly the pattern rows 30, 36, 39 and 43 used
(*"every gate constant byte-identical to R1"*). That escape is available and should be taken.

### GENUINELY OPEN — GPU, execution blocked on the stopped instance

| row | case | measured spend | repair shape | est. repair | §12.2 ceiling |
|---|---|---|---|---|---|
| **34** | VMFLGPU002 | 0.896944 GPU-h + 30.567 core-min (CPU arm) | **gate redesign**, shared with row 14 — `OSCILLATORY` on the flow split. Limb B already held at `4.07e-10` against a `1e-4` band: **the GPU path is verified; the gate is not.** | ≈ 1.0–1.5 GPU-h + ~30 core-min; **$0.80–$1.21 DERIVED** at $0.8048/GPU-h (g6.xlarge, us-east-2, published list — **not measured**) | **DIFFERENT** — code-to-code → `GATE REACHED`, ceiling hard-coded in the comparator |
| **42** | VMFLGPU005 | 1.6833 GPU-h (GPU arms) + 151.75 core-min (CPU arms) | **gate redesign** — 5 of 7 channels taken to `NOT A RESULT` by rule 5 before their bands decided | ≈ 2 GPU-h + ~150 core-min; **≈ $1.61 + $0.128 DERIVED** | **DIFFERENT** — value-vs-experiment → C1/C2 capped `GATE REACHED` (§2f.3). Limb B (GPU == forced-CPU, same discrete problem) is `PASS`-capable **and already PASSED** at 2.957e-10 |

---

## 4 — HOW MUCH SMALLER THE BACKLOG IS, SAID PLAINLY

- **35 queue rows → 14 genuinely open.** 21 rows (60 %) were already done, already terminal, or
  blocked by the source document.
- **14 open rows → 10 successor registrations**, because the VMFL003 family's five rows are one
  repair.
- **10 registrations → 8 distinct root defects**, because rows 14 and 34 share one gate-design defect.
- **Of the 10 registrations: 6 are startable tonight at 301.5 core-min / $0.2578 DERIVED**; 1 is
  **referred to Sanaa** (the VMFL003 threshold change); 1 needs a **supervisor solver decision** and
  cannot be costed from disk (row 32); 2 wait on the **GPU instance** (rows 34, 42).
- **The queue's own headline figures move:** *"ACTIONABLE NOW: 24 CPU rows. Blocked on GPU: 7.
  Already converted: 4."* → **actionable now 12 CPU rows in 8 registrations, of which 6 are startable;
  blocked on GPU 2; already converted or terminal 21.**
- **Tier 4 joins tiers 1 and 2 as empty.** `BUDGET/KILL` was emptied by inspection, `NAMING/PLUMBING`
  by a repair that had already happened, and **`REFERENT-CEILING` is empty because all eight of its
  non-`BLOCKED` rows are already at the ceiling and its ninth is blocked by the manual.** Three of
  Sanaa's five tiers contain nothing. **All the surviving work is in `INSTRUMENT` (one row, 37) and
  `GATE-DESIGN`.**

---

## 5 — THREE FINDINGS AGAINST MY OWN BRIEF, REPORTED BECAUSE THEY SURVIVED CHECKING

**(a) THE CITATION FORM THE BRIEF MANDATED HAS BEEN SUPERSEDED BY THE CHARTER ITSELF.** The brief
requires citing *"`VERIFICATION_CHARTER §2h.6.1`, v1.27, 2026-08-31, the exact-PDE rule"* and bans a
bare `§2h.6`. That was right when written. **`VERIFICATION_CHARTER` v1.28 has since renumbered the
rule**: `§2h.8.1` (`VERIFICATION_CHARTER.md:3762`) rules that *"`§2h.6` denotes NON-RETROACTIVITY
(v1.19) and nothing else"* and that *"the EXACT-PDE RULE is `§2h.8`"*, mapping `§2h.6.1`→`§2h.8.1`
one-to-one with **the words of each unchanged**. `§2h.8.3` fixes the lab-wide form as
**`VERIFICATION_CHARTER §2h.8.1 (v1.28, 2026-08-31, the exact-PDE rule)`** and adopts this team's ban
lab-wide. `§2h.8.4` preserves the validity of records frozen citing `§2h.6.1`. **I have used the
conforming v1.28 form throughout and given the mapping**; the brief's form is not wrong, it is one
version stale, and `ANSYS_VERIFICATION_CHARTER` §12.2 still cites `§2h.6.1` at its own line 902 —
which the supervisor may want to route to the verification team rather than edit.

**(b) THE SEVEN "GPU-BLOCKED" ROWS ARE TWO.** Detailed above. Restoring the GPU instance unblocks 34
and 42 and nothing else.

**(c) THE REGISTER CARRIES REFERENT ANNOTATIONS THAT `§2h.8.1` NOW CONTRADICTS — IN BOTH DIRECTIONS.**
Rows **17, 18, 19 and 32** each carry *"measured / experimental → **CAN buy P**"*, which the exact-PDE
rule contradicts by capping experiment at `GATE REACHED`; rows 30 and 44 already record their ceiling
as lowered, so the register is internally inconsistent on the same question. Row **37** carries
*"buys V, never P"*, which understates in the **other** direction (see §3). `ANSYS_VERIFICATION_CHARTER`
§12.2 closes on exactly this: *"an unnecessarily capped row is as inaccurate as an overclaimed one,
and 'we were being careful' is not a defence for a wrong label either way."*
**Recorded for the supervisor's read. NO REGISTER BYTE IS CHANGED HERE, and no row's verdict moves —
these are annotations about future ceilings, not the landed verdicts.**

---

## 6 — WHAT I DID NOT VERIFY

- **I did not open the run directories.** Every measured core-minute, GPU-hour, deviation, triple
  state and GCI above is quoted from the register's own cells, which cite their artifacts. Where the
  queue supplied a figure I did not re-derive (row 32's 1 231 583 core-min projection; the VMFL003
  94.3 %-after-convergence figure), I have said so and attributed it to `REPAIR_QUEUE.md`.
- **The repair-cost estimates are ESTIMATES, extrapolated from measured spend — never measurements.**
  Each is anchored on that case's own measured `COST.txt` figure, but the extrapolation (an extra
  refinement level, a longer `endTime`, a fresh triple) is a judgement. They are sized for planning,
  and each successor still owes its own pre-registered cap under rule 12.
- **I did not verify that the successor runs reproduce their parents' physics from raw fields.**
  Supersession here rests on the register's own successor declarations plus the byte-identity claims
  those successors make about their gate constants — a documentary check, which is what a queue fact
  requires and no more.
- **Row 4's `SAME`/`DIFFERENT` answer is my reading, not a ruling.** §12.2 reserves it for the
  registration, before compute, and row #7's mixed precedent means it is genuinely contestable.
