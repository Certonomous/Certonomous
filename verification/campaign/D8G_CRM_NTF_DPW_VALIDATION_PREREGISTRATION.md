# D8G-CRM-NTF — NASA CRM WING-BODY CL/CD/CM vs NTF/AMES TUNNEL DATA, PRE-REGISTRATION

**Item:** `D8G_CRM_NTF_DPW`
**Team:** dafoam. **Lane:** `lab-lane`. **Supervisor:** `dafoam-supervisor`.
**Authority:** Sanaa, `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md:7` and `:34` —
*"Same for D8G: CL, CD, CM at the DPW condition (Mach 0.85, CL 0.5) against the NTF/Ames
CRM tunnel data, band registered, then graded"*; *"band registered before grading …
with the DPW scatter as the honest tolerance"*. And `:7`: *"The band must be registered
before the comparison is run."*

**STATUS: FROZEN AT THE COMMIT THAT INTRODUCES THIS FILE.**
No comparison number exists at the moment of the freeze.

🔴 **HEADLINE, SO IT IS NOT READ PAST: THIS DOCUMENT REGISTERS A BAND AND THEN
REFUSES TO GRADE THE EXISTING L1-P PRIMAL AGAINST IT, FOR THREE INDEPENDENT REASONS,
ANY ONE OF WHICH IS SUFFICIENT.** Sanaa, same directive: *"A comparison at the wrong
condition is worse than none."*

**NO SOLVER RUNS UNDER THIS DOCUMENT.** Directive item 19: the runner is the only
launcher. Nothing here launches anything.

---

## 1. THE REGISTERED BAND — ITS RULE IS FROZEN NOW; ITS NUMBERS ARE NOT YET AVAILABLE

### 1.1 The quantities

**CL, CD, CM** on the NASA CRM **wing-body** configuration at **M∞ = 0.85**, at the
**fixed-lift condition CL = 0.50**, Re = 5.0×10⁶ on `c_ref` — the DPW design point.
CD is reported in **drag counts** (1 count = 1.0×10⁻⁴).

### 1.2 The band rule — FROZEN BY THIS COMMIT, AND IT CANNOT BE TUNED LATER

For each quantity Q ∈ {CL, CD, CM}:

> **`PASS` iff `Q_cfd` lies inside `[Q_ref − S_Q, Q_ref + S_Q]`**, where
> `Q_ref` is the **NTF/Ames tunnel value** at the registered condition and
> `S_Q` is the **DPW participant scatter** for Q at the matched grid level,
> taken as the **interquartile range** of the participant population as published by
> the DPW summary paper, **not** as a standard deviation and **not** as a full range.

> `GATE FAIL` iff the primal is admissible under §3 and any quantity falls outside.
> `NOT A RESULT` iff any §3 precondition fails. This overrides both.

The **rule, the statistic (IQR), the configuration (wing-body), the condition
(M 0.85, CL 0.50, Re 5×10⁶) and the reporting unit (counts)** are frozen here. Only
`Q_ref` and `S_Q` — which are *the reference's own published numbers, not ours* —
remain to be read off a verified document. **Because they come from the reference and
not from us, filling them in later cannot bend the gate toward our answer.** That is the
whole evidentiary content of a freeze (rule 2) and it is preserved.

### 1.3 🔴 BLOCKER R-1 — THE REFERENCE IS NOT ON THIS BOX

Swept by this lane, 2026-09-12, across `docs/papers/`, `cases/`, `verification/` and
`/home/ubuntu/certonomous-runs/`:

| candidate on disk | title-page verified? | does it carry CRM wing-body CL/CD/CM at M 0.85, CL 0.5, with DPW scatter? |
|---|---|---|
| `docs/papers/benchmark_test_cases/vassberg_2008_nasa_common_research_model.pdf` — **AIAA 2008-6919**, Vassberg, DeHaan, Rivers, Wahls | **YES** — read from the PDF's own first page | **NO.** It is the *model development* paper. Its own abstract: the performance data *"is presented in such a manner as to not bias CFD predictions planned for the fourth AIAA CFD Drag Prediction Workshop"*. It **deliberately withholds** the data this band needs. |
| `docs/papers/benchmark_test_cases/sansica_2025_dpw8_aepw4_buffet_workinggroup.pdf` | **YES** — read from the PDF's own first page | **NO.** It is the **ONERA OAT15A supercritical AIRFOIL** (2D buffet, Test Case 1), not the CRM wing-body. Its scatter figures (≈10/50/90 CD counts at α = 1.50/3.10/3.90°) are **airfoil** scatter and **must not be borrowed** for a wing-body band. |
| `docs/DPW-CRM-SCOPING.md` | **n/a — it is our own scoping note, not a reference** | **NO, AND IT MUST NOT BE USED AS ONE.** Its figures (median 257 counts, IQR ±4–5 counts, band 252–262) are transcribed from **web URLs**, with **no document on this box and no title-page verification** (rule 15). It also records that the tunnel values themselves *"are held proprietary by NASA for the ongoing workshop"*. **A band frozen on numbers nobody on this box has verified is not a frozen band.** |

**Therefore `Q_ref` and `S_Q` are `BLOCKED` pending acquisition and title-page
verification of a DPW summary carrying CRM wing-body forces and participant statistics**
(the named candidates: the DPW-VI summary, Tinoco et al.; and an NTF CRM test report,
Rivers & Dittberner). **Acquisition is a retrieval, not a submission** — nothing is sent
(rule 7). Until that document is on disk and its title page read, **no number may be
written into §1.2, and none is written here.**

---

## 2. 🔴 THE CONDITION THE EXISTING PRIMAL ACTUALLY HOLDS — AND IT IS NOT THE REGISTERED ONE

Read by this lane from the case's **own inputs**, not from its outputs:
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R2-a6-grid-triple/L1-P/d8g_runScript.py`
and the arm's own row `d8g_P.json`.

| | registered condition (§1.1) | what L1-P actually holds | match? |
|---|---|---|---|
| **Mach** | 0.85 | `U0 = 295.0` m/s, `T0 = 300.0` K → a = √(1.4·287·300) = 347.189 m/s → **M = 0.84968** | **YES** (Δ = 0.0003) |
| **Lift** | **CL = 0.50** | run in **mode P** (primal) at **fixed** `patchV = [295.0, aoa0 = 2.11031707°]`; achieved **CL = 0.34000584724055816** | 🔴 **NO** |
| Reynolds | 5.0×10⁶ on `c_ref` | not established at the registered `c_ref`; the case normalises on `A0 = 3.407014` | **not established** |
| configuration | CRM **wing-body** | `"designSurfaces": ["wing"]`, FFD `FFD/wingFFD.xyz`, force patches `["wing"]` | 🔴 **wing only** |
| mesh | DPW committee family (L1 medium ≈ 16.9 M cells) | **`cells` = 5,568**, three readers agreeing (`owner` body max+1, `owner` header note) | 🔴 **~3,000× coarser** |

**`CL_target = 0.5` appears in `d8g_runScript.py:28`, but it is the OPTIMISATION
constraint, not this arm's state.** Mode P is a single primal at a fixed angle of attack;
it was never trimmed to CL = 0.50. **The primal sits at CL = 0.34, which is 32% below the
registered condition.** CD, CL and CM are all strong functions of CL at a transonic
design point, so a comparison at CL = 0.34 against a CL = 0.50 reference is not a loose
comparison — it is a different question.

🔴 **REFUSAL C-1: THE COMPARISON IS NOT FORCED. The Mach matches; the lift does not.**
Per Sanaa's instruction, the condition the primal actually holds is stated instead:
**M = 0.84968, α = 2.11031707°, CL = 0.34000584724055816, CD = 0.04380537021659878,
on 5,568 cells, wing-only.** No band is applied to those numbers by this document, and
none of them is offered as a validation result.

For scale, and **as an observation carrying no verdict**: CD = 0.0438 is **438 drag
counts** on a wing-only 5,568-cell mesh. Whatever the CRM wing-body reference turns out
to be, this row is not in a position to be compared with it.

---

## 3. PRECONDITIONS — ALL THREE FAIL TODAY, AND EACH IS INDEPENDENTLY SUFFICIENT

Before any deviation may be printed under this document:

- **PC-1 — the reference exists and is title-page verified (rule 15).**
  **`BLOCKED`.** See §1.3. `Q_ref` and `S_Q` do not exist on this box.
- **PC-2 — the primal holds the registered condition (§1.1), within
  |ΔM| ≤ 0.005 and |ΔCL| ≤ 0.01.**
  🔴 **FAILS.** Mach passes (Δ 0.0003); **CL fails by 0.16** (0.340 vs 0.500),
  16× the tolerance. Configuration and grid level also fail. Comparison **refused**.
- **PC-3 — the primal's own row is a result.**
  🔴 **FAILS.** See §4.

---

## 4. 🔴 THE TWO THINGS THAT TRAVEL WITH ANY D8G NUMBER, AND THEY ARE NOT NEGOTIABLE

**(1) PATCHED ROW ONLY.** Every D8G L1-P figure comes from the **patched** toolchain row
(`idwarp_file = /opt/idwarp_patched/idwarp/__init__.py`, `libidwarp_so_md5 =
85f59e87253e0a71a813f64ca6e4c425`). **There is no shipped row.** Therefore **no D8G
number is a verdict about DAFoam as distributed** — it is a verdict about DAFoam with
this lab's patch. Anything that drops the qualifier misreports it.

**(2) THE L1-P ROW IS GRADED `NOT A RESULT`.** By D8G's own frozen comparator
`d8g_grade.py` (md5 `12688063e20cbb6fa79cf08d0996d4e1`, unchanged), recorded at
`cases/dafoam/ladder-a/A6/curriculum_D8G/D8G_R2_GRADING_RECORD.md:31`:

```
REFUSE G1-RUN  arm L1-P  endTime_registered 1000.0  last_time 2000.0
"rule 4: last time == endTime.  A primal that stopped short is not done,
 however plateaued its tail looks"
```

The R3 repair package's knob 5 set `endTime 2000` while the frozen comparator gates on
`ENDTIME_REGISTERED = 1000.0` (`d8g_grade.py:290`). **The registration changed something
the untouched instrument gates on, so the arm is ungradeable by its own frozen
comparator by construction.**

**The physics of that primal is sound and cited; the graded row is not a result.**
The two statements are both true and neither cancels the other. **This document never
quotes a D8G number without both.**

For the record and for no other purpose, the nuTilda reading the brief carries:
**7.873598471886472e-05 = 0.787× its 1.0e-04 floor** — i.e. the R2 arm cleared the floor
that made its **predecessor** (`CURRICULUM-D8G-a6-grid-triple`, endTime 1000,
nuTilda 4.074e-04, *"Primal solution failed!"*) a rule-5-clause-1 `NOT A RESULT`.
**R2 failed at a different and deeper gate**, not at that one. yPlus mean 141.70.

---

## 5. VERDICT OF THIS DOCUMENT, TODAY

**`BLOCKED`** — on PC-1, reference acquisition; the band's rule is frozen and its
numbers cannot honestly be filled from anything on this box.

**And, independently, `NOT A RESULT` for the L1-P primal as a CRM validation row** —
on PC-2 (CL 0.340 vs 0.500, wing-only, 5,568 cells) and PC-3 (`REFUSE G1-RUN`).

**No CL/CD/CM comparison number is produced by this document, and producing one would
be worse than producing none.**

---

## 6. WHAT UNBLOCKS IT — the shortest honest path, in order

1. **Acquire and title-page verify** a DPW summary carrying CRM **wing-body** CL/CD/CM
   and participant statistics at M 0.85 / CL 0.50, plus an NTF or Ames 11-ft CRM test
   report for `Q_ref`. File under `docs/papers/benchmark_test_cases/` with a `.txt`
   sidecar. **Then, and only then, an addendum writes `Q_ref` and `S_Q` into §1.2** —
   an addendum may fill a value the reference publishes; it may not alter the rule,
   the statistic, the condition or the label (rule 2).
2. **Run a primal at the registered condition** — trimmed to CL = 0.50, on the CRM
   **wing-body** geometry, on a **committee grid** admissible under the two-tier mesh
   standard. That is the directive's own run plan (`:35`): *"D8G L1 converges already
   → register the comparison → then L2 on the committee family."* **The comparison is
   now registered. The L2 on the committee family is what it is waiting for.**
3. **Fix the endTime contradiction** (§4) so the arm is gradeable by its own comparator.

**This document is the deliverable the directive asked for at step 2's front: the band
exists, frozen, before any D8G number is compared to anything.**

---

## 7. COST (rule 12)

**No compute. No solver runs. 0.000 core-minutes, 0 GPU-hours.** Desk work.
Predicted 0; actual 0; ratio n/a. Any future grading arm registers its own cost before
it runs. Dollars, if ever quoted, are **derived, not measured** at the owner-stated
$0.0513/core-h; the box cannot read its own billing.

---

## 8. FREEZE

Committed together with the M6 registration and comparator. **No comparison number
existed when this commit was made.** Changes land only as dated addenda that cannot
alter a gate, threshold, cap or label; originals are struck, never rewritten.
**SUBMISSIONS PARKED** (rule 7) — nothing here is sent, filed or registered anywhere
outside this box.
