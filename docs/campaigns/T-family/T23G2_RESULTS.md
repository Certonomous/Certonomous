# T23G2 — RESULTS. THE WALL-RESOLVED, SIMILARITY-REPAIRED GRID TRIPLE AT (305 W, 20 m/s)

## RUNG VERDICT: **NOT A RESULT**

Graded 2026-09-02 by `/home/ubuntu/Certonomous/docs/campaigns/T-family/analyse_t23g2.py`
against `/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs`, and by
nothing else. **No value in this record was hand-read, no GCI was computed
outside the comparator, and no gate was evaluated by a human.** The comparator
exited **3**, which is `EXIT_NOT_A_RESULT` at
`/home/ubuntu/Certonomous/scripts/roache_triple.py:177` — an unambiguous graded
verdict, **not** the exit-2 refusal. The comparator did not refuse on anything.

**The rung is `NOT A RESULT` on three grounds that are independent of one
another, and each of the three was established BEFORE and INDEPENDENTLY OF the
five repairs of 2026-09-02.**

---

## ⚠ 0. THE REPAIRS DID NOT PRODUCE THIS VERDICT, AND THIS IS THE FIRST THING IN THE RECORD BECAUSE IT IS THE THING MOST EASILY MISREAD

Five `§2d.1` repairs (`R1`–`R5`) were granted and landed on 2026-09-02, after all
three levels had solved. A reader who meets them at the foot of a `NOT A RESULT`
record will reasonably ask whether the repairs made the rung fail.

**They did not. Measured, not argued.**

- All three failing grounds below — `G-CONV`, `G-YPLUS` and `Q3`'s band — were
  present in the **frozen, pre-repair** comparator and in the solver logs written
  on 2026-09-01, hours before any repair existed. Each is readable from an
  artifact on disk with no repaired code in the path.
- `verification` ruled on the same question at
  `/home/ubuntu/Certonomous/docs/charters/VERIFICATION_CHARTER.md` §2d.8
  (v1.38, commit `3dad5bae`), in terms: *"NO COMBINATION OF R1–R6 CAN PRODUCE
  `PASS` OR `GATE REACHED` FOR T23G2. Measured, not argued. R1 makes the verdict
  REACHABLE; R2–R6 change the outcome by nothing measurable. **The repairs decide
  the QUALITY OF THE RECORD, not the verdict.**"*
- Direction of every repair is **restrictive or neutral**. `R3` can only *add* a
  `GATE FAIL` and on this data adds none — **and see §14: `R3`'s own gate is
  defective in a way this sentence does not cover, because it emits a `PASS` on a
  ladder rule 5 has already voided.** `R4`'s band limb *removes* two `PASS`es
  and no `GATE FAIL`. `R5` can only *refuse*. The one limb that could have moved
  the verdict in the permissive direction — `R4`'s rollup exclusion — is the one
  `verification` **refused**.
- `R1` alone changed reachability: before it, the completion instrument's
  allow-list refused `T23G2_L1` with rc 2 before reading a field, so **no**
  verdict of any kind could be produced. It made a verdict possible; it did not
  choose which one.

**The honest summary: the negative verdict is a property of the CASE. The repairs
are a property of the RECORD.**

---

## ⚠ 0a. AND THE RUNG ITSELF RAN CLEAN — THE VERDICT IS NOT AN EXECUTION FAILURE

This must be said as plainly as the verdict, because a `NOT A RESULT` is
routinely misread as a broken run.

**Rule 4 completion: `DONE` at all three levels, all six conjuncts.** Delegated,
as `T23G2_PREREGISTRATION.md:539-541` registers, to
`/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/mark_done_t23.py`,
called as a subprocess by the comparator. The six conjuncts are rc = 0; exactly
one `End` line; last written time == `endTime`; registered fields present at
`endTime`; `ExecutionTime` line count == `endTime`/`deltaT`; and the **age
guard** — every field at `endTime` newer than the case's own `0/T`.

| level | `rc` | `endTime` | completion |
|---|---|---|---|
| `T23G2_L1` | 0 | 6,000 | **`DONE`** |
| `T23G2_L2` | 0 | 12,000 | **`DONE`** |
| `T23G2_L3` | 0 | 24,000 | **`DONE`** |

`rc` is `READ-FROM-STATUS` at each level, from that level's own
`STATUS.T23G2_L<n>`, captured inside the launcher wrapper on the line after the
solver call. `verification` independently re-derived all three levels and all
six limbs including the age guard (`VERIFICATION_CHARTER.md` §2d.8, "Also
recorded, not ruled").

**Rule 2 freeze: clean, and the timeline is not close.**

| event | commit | UTC |
|---|---|---|
| pre-registration committed | `658b3ba4` | 2026-09-01T17:01:44Z |
| comparator committed (grading path frozen) | `976776f4` | 2026-09-01T18:57:39Z |
| **first compute** (first solver line) | — | **2026-09-01T19:07:26Z** |

First compute is read from
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_L1/START.T23G2_L1`,
field `start_utc`. The comparator froze **9 min 47 s before** the solver started.
**Nothing on the grading path was touched between the freeze and first compute**
— `git log` over that window, restricted to the five grading-path files, returns
`976776f4` and nothing else `[MEASURED]`.

That first-compute instant is itself a ruled question, not an assumption:
`§2i.8` would put first compute at meshing (18:39:59.8Z, which would place the
comparator freeze *after* gates closed). `VERIFICATION_CHARTER.md` §2d.6 ruled
that §2i.8 **has no object here**, because its condition is a mesh *the
registration did not fix*, and T23G2's registration fixed the cell counts
(40,320 / 90,720 / 204,120 at §2.1) with `gate_meshsim` refusing on a mismatch —
and the built meshes match exactly. First compute is the first solver line,
19:07:26Z. **The comparator's original commit was clean.**

**Rule 6: the frozen pre-registration was never edited.** Its blob today is
`b2721aaad40124c2aeb85055aee716fb35805764`, byte-identical to the blob in
`976776f4` — reported by the comparator's own sha recorder as `IDENTICAL`.

---

## 1. THE THREE INDEPENDENT GROUNDS

### 1.1 `G-CONV` — **`GATE FAIL`**

Registered at `T23G2_PREREGISTRATION.md:561`: `Uy Uz p_rgh k omega` initial
residual **≤ 1e-8** at the last iteration, `h` ≤ 1e-9 under Sanaa's tightened
criterion. `Ux` is excluded and the exclusion is itself measured.

| level | state | worst asserted residual | `Ux` exclusion basis |
|---|---|---|---|
| `T23G2_L1` | `CONVERGED` | all within tolerance (last `p_rgh` **9.18853420673e-09**) | max\|Ux\|/max\|Uz\| = 2.019e-16 |
| `T23G2_L2` | **`NOT CONVERGED`** | **`p_rgh` 1.04122627289e-08** | max\|Ux\|/max\|Uz\| = 3.304e-16 |
| `T23G2_L3` | `CONVERGED` | all within tolerance (last `p_rgh` **9.07512718378e-09**) | max\|Ux\|/max\|Uz\| = 5.170e-16 |

**4.1 % over the registered threshold, on one level of three.** Artifact:
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_L2/log.solve`.

This is the ground that propagates. Under `CLAUDE.md` rule 5 **step (a)** — *any
level not iteratively converged or not plateaued → `NOT A RESULT`* — a level that
is not iteratively converged disqualifies **every triple that contains it**, and
`T23G2_L2` is in all of them.

### 1.2 `G-YPLUS` — **`GATE FAIL`**

Registered at `T23G2_PREREGISTRATION.md:1117-1118` (amendment A2.2): **max y+ ≤
1.0 on EVERY wall patch, on EVERY level. Gated, not reported.**

`centrebody_up` exceeds it at all three levels, **the finest included**:

| level | patch | n | min | avg | **max** | verdict |
|---|---|---|---|---|---|---|
| `T23G2_L1` | `centrebody_up` | 80 | 0.7517 | 0.8131 | **1.8245** | **`GATE FAIL`** |
| `T23G2_L2` | `centrebody_up` | 120 | 0.5059 | 0.5476 | **1.3539** | **`GATE FAIL`** |
| `T23G2_L3` | `centrebody_up` | 180 | 0.3397 | 0.3681 | **1.0047** | **`GATE FAIL`** |

Every other patch passes at every level: `centrebody_down` max 0.7331 / 0.4934 /
0.3314; `duct_wall` max 0.6177 / 0.4574 / 0.3388; `fluid_to_housing` max 0.7513 /
0.5057 / 0.3397.

**Two instruments, both above 1.0, and they agree.** The maxima tabulated above
are the **independent field reader** (`yplus_from_fields`, computing y+ from the
`U` and `nut` fields at `endTime`). The **primary log instrument**
(`log.yPlus.fluid`) reads `centrebody_up` max **1.8245835202 / 1.3540190129 /
1.0047773564` `[MEASURED]`. The two readers differ in the fourth decimal
(relative miss ≈ 5e-5 to 1.2e-4), far inside the registered 2 % agreement check,
and the comparator confirmed *"primary instrument PRESENT and agrees with the
independent reader to within 2%"* at all three levels. **The gate fails on either
instrument alone.** Artifacts:
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_L{1,2,3}/log.yPlus.fluid`
and the `U`/`nut` fields at each level's `endTime`.

*Recorded because it is a difference between two numbers a reader may see quoted:
`VERIFICATION_CHARTER.md` §2d.8 quotes `1.8246 / 1.3540 / 1.0048` — the primary
log instrument to four decimals. This record's table is the independent field
reader. Neither is wrong; they are two readers, and the registration gates on
both agreeing, which they do.*

### 1.3 `Q3` fine value — band **`GATE FAIL`**

`Q3` is max(T) in the core region, graded as ΔT = T − 288.0 K, and it **receives
`Q4`'s registered band** by the §3 role table at `T23G2_PREREGISTRATION.md:453`.
Band **[46.0, 56.0] K**.

**Measured at `T23G2_L3`: ΔT = 56.70795433 K**, i.e. max T = **344.7079543331 K**.
**Outside the band, high, by 0.708 K.** Artifact:
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_L3/postProcessing/core/core_T/0/fieldMinMax.dat`.

The band verdict is computed **first and unconditionally** by the comparator, so
it is visible even though rule 5 then supersedes it: `Q3`'s row verdict is
`NOT A RESULT`, not `GATE FAIL`, because rule 5 can only turn a `GATE FAIL`
**into** `NOT A RESULT`, never the reverse.

---

## 2. EVERY GATE, AS THE COMPARATOR PRINTED IT

| gate | verdict | basis |
|---|---|---|
| `G-MESHSIM` | **`PASS`** | 15 checks; cell ratios 2.250000000 on fluid/housing/core at both steps; first-cell ratios 1.499995–1.500051 on all four patches at both steps; 8 cells across the housing wall at the coarsest level (floor 8; T23G carried 4) |
| `G-CONV` | **`GATE FAIL`** | §1.1 |
| `G-YPLUS` | **`GATE FAIL`** | §1.2 |
| `G-PLATEAU` | **`PASS`** | `PLATEAUED` on all six quantities at all three levels |
| `G-RATIO` | **`PASS`** | ratio ∞ on all six (finest iterative change exactly 0.0; smallest inter-level difference 6.66e-01 to 2.65e-05), threshold ≥ 10 — **and now licensed by a live control, see §4** |
| `G-ORDER` | **`PASS` — as printed by the comparator; ⚠ NOT CITABLE AS A PASSED GATE, §14** | p(`Q4`) = 0.6111, registered band [0.5, 1.5] at `:833-834`, finest triple `CONVERGING` — **but p(`Q4`) = 0.6111 is the observed order of a triple whose grid claim rule 5 step (1) voided, so there is no order to gate and this `PASS` licenses nothing; the gate as implemented never consults the iterative-convergence states (§14)** |
| **rung rollup** | **`NOT A RESULT`** | `NOT A RESULT` present in the verdict set and tested first |

**⚠ On `G-ORDER`'s `PASS` — and this paragraph is itself amended, because as
first written it did not go far enough. See §14 (2026-09-02).** The gate is
registered on p(`Q4`) and p(`Q4`) = 0.6111 does sit inside [0.5, 1.5]. But that p
is computed from a triple containing `T23G2_L2`, which rule 5 step (a) has
declared cannot support a grid claim. **The original wording of this paragraph
then said `G-ORDER`'s `PASS` "is a gate result, not a grid-convergence claim".
That concession was too weak and the record withdraws it.** A `PASS` computed
from a triple rule 5 voided at step (1) is not a gate result either: rule 5's
ordering puts step (1) *before* any grid claim, so the observed order — a
property of that claim — does not survive to be gated at all. `gate_order`
(`analyse_t23g2.py:917-918`) decides from exactly two fields, the finest triple's
observed order and its triple state, and **never consults
`row["iterative_convergence"]`**, which `RT.grade_ladder` stores on the same row
(`scripts/roache_triple.py:601`). **`G-ORDER`'s `PASS` therefore licenses
nothing and must not be cited as a passed gate**, neither as evidence about the
discretisation nor as a gate the rung cleared. A `§2d.1` repair (`R7`) is
petitioned at
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T23G2_R7_ORDER_GATE_PETITION.md`;
until `verification` rules, this record treats the `PASS` as reported, not as
earned. **The rung verdict is unaffected either way — `NOT A RESULT` on `G-CONV`
and `G-YPLUS` regardless.**

---

## 3. THE FIVE GRADED QUANTITIES — VALUES, TRIPLES, ORDERS, GCI

All graded on ΔT = T − 288.0 K. `dim = 2` (5° wedge, one cell
circumferentially). Cells 40,320 / 90,720 / 204,120; r21 = r32 = **1.5000**
(equal). Fs = 1.25.

| q | what | fine value [K] | triple values (L1, L2, L3) | state | order p | GCI | row verdict |
|---|---|---|---|---|---|---|---|
| `Q4` | core volume-avg T | **53.195** | 54.71544531, 53.86153602, 53.19504351 | `CONVERGING` | 0.6111 | 5.5696 % = 2.96273 abs | **`NOT A RESULT`** |
| `Q1` | housing max T | **52.6058** | 54.14725858, 53.28097866, 52.60582825 | `CONVERGING` | 0.6148 | 5.6670 % = 2.98115 abs | **`NOT A RESULT`** |
| `Q2` | `housing_to_fluid` areaAvg T | **50.7841** | 52.30761933, 51.45195967, 50.78410906 | `CONVERGING` | 0.6112 | 5.8455 % = 2.9686 abs | **`NOT A RESULT`** |
| `Q3` | core max T | **56.708** | 58.2380267, 57.37880185, 56.70795433 | `CONVERGING` | 0.6104 | 5.2661 % = 2.98627 abs | **`NOT A RESULT`** |
| `Q6` | housing volume-avg T | **50.8468** | 52.3698477, 51.51447503, 50.84681073 | `CONVERGING` | 0.6110 | 5.8382 % = 2.96854 abs | **`NOT A RESULT`** |

**Every triple is `CONVERGING` and monotone, so each GCI above is arithmetically
legitimate to quote** (rule 5's prohibition is on quoting a GCI when the three
values are not monotone; they are). **They still license nothing here.** Each row
carries the identical reason: *"levels `T23G2_L2` are not iteratively converged
or not plateaued; no grid claim can be made from this triple."* Rule 5 step (a)
fires before the triple state is ever consulted.

**⚠ And that applies to p(`Q4`) = 0.6111 in the table above wherever it is read.**
The five orders 0.6104–0.6148 are printed values of a voided claim. `G-ORDER`
nevertheless returned `PASS` on p(`Q4`) = 0.6111 because the gate reads the triple
state and not the row verdict — **§14**.

**Richardson extrapolates are REPORTED and NEVER GATED ON**, as §5 registers:
`Q4` 50.82486, `Q1` 50.220911, `Q2` 48.409226, `Q3` 54.318939, `Q6` 48.47198 (the
comparator also prints each in the sign-flipped parent-convention form).

**Band verdicts, computed first and unconditionally:** `Q1` `PASS`, `Q2` `PASS`,
`Q3` **`GATE FAIL`**. `Q4` and `Q6` also printed a band verdict (`PASS` and
`PASS`) and **both are `DISCLOSED, NOT GRADED`** — see §5, repair `R4`.

### `Q5` — REPORTED, NEVER GATED

Housing surface heat flux. Values **[−1.897401596355, −1.897375071212,
−1.897321993418]**, state **`DIVERGENT`**, order **−1.7108**.

`DIVERGENT` here is the **pre-registered expectation** under P4 (§5.2): the
quantity is pinned by the imposed 305 W source to ~4e-5 relative. It is not a
failure of this rung, and it is **not** what makes the rows `NOT A RESULT` —
`G-CONV` is. A `CONVERGING` `Q5` with p in [1.5, 2.5] would have meant P4 lost.

---

## 4. THE TWENTY PLANTED-ZERO CONTROLS — **20 of 20 CONSTRUCTED AND PASSED**

Registered at `T23G2_PREREGISTRATION.md:624-625`: *"Six quantities × three levels
= **18 controls**, plus the two y+ readers = **20**."*

**Controls 1–18 — every quantity, every level.** Each plants `PLANT = 1.234e-03`
into the last non-comment line of the **real** artifact, reads it back through
the **real** parser, and is asserted by `RT.assert_plant_control`, which
**refuses** on a control that did not read its plant back.

| quantity | `T23G2_L1` | `T23G2_L2` | `T23G2_L3` |
|---|---|---|---|
| `Q1` | `PASSED` | `PASSED` | `PASSED` |
| `Q2` | `PASSED` | `PASSED` | `PASSED` |
| `Q3` | `PASSED` | `PASSED` | `PASSED` |
| `Q4` | `PASSED` | `PASSED` | `PASSED` |
| `Q5` | `PASSED` | `PASSED` | `PASSED` |
| `Q6` | `PASSED` | `PASSED` | `PASSED` |

**Controls 19 and 20 — the two y+ readers, at `T23G2_L3`.**

- **[19/20] independent field reader.** Planted x(1 + 0.001234) into **181,694
  vectors** of `U`; every wall patch moved by sqrt(1 + PLANT) =
  **1.000616809773**, worst relative miss **2.219e-16** on `centrebody_down` —
  **`PASSED`**.
- **[20/20] primary log reader.** Planted 0.001234, read back 0.001234 —
  **`PASSED`**.

Row-level controls are additionally re-asserted inside each graded row: each of
`Q4`, `Q1`, `Q2`, `Q3`, `Q6` prints *"planted-zero control: PASSED planted
0.001234 reader `<Q>` @`T23G2_L3` saw 0.0012340000000108375"*.

---

## 5. THE GRADING-PATH SHA TABLE — FIVE FILES, TWO COLUMNS, AND IT DOES NOT CLAIM WHAT IT CANNOT

Registered at `T23G2_PREREGISTRATION.md:671`; built by repair `R2`, widened by
`VERIFICATION_CHARTER.md` §2d.7 from four files to five. The recorder **grades
nothing**: it reads no field and moves no comparison. "Frozen" is the blob in
`976776f4`, the commit that froze the comparator.

| grading-path file | post-repair (working tree) | pre-registration (frozen) | |
|---|---|---|---|
| `docs/campaigns/T-family/T23G2_PREREGISTRATION.md` | `b2721aaad40124c2aeb85055aee716fb35805764` | `b2721aaad40124c2aeb85055aee716fb35805764` | **`IDENTICAL`** |
| `docs/campaigns/T-family/analyse_t23g2.py` | `fa4e802f9e0eab63e8d4902e1d74e99f11748a8f` | `cc723d6f65245674f7d80c51de55fe986549477a` | **`DIFFERS`** |
| `docs/campaigns/T-family/t23g_readonly_diagnosis.py` | `73804c02d2f1ebbb2cd2ad63796f4b5cfb4d7067` | `73804c02d2f1ebbb2cd2ad63796f4b5cfb4d7067` | **`IDENTICAL`** |
| `verification/runs/T-family/T23_runs/mark_done_t23.py` | `37165979fafbe3c87921dab05b51e984878d90dc` | `ecd457ac87dbdab83498c6a9c0334226c3e66863` | **`DIFFERS`** |
| `scripts/roache_triple.py` | `78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` | `78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` | **`IDENTICAL`** |

**The two that differ are exactly the two files the granted repairs touch**, and
nothing else on the path moved: `mark_done_t23.py` carries `R1`;
`analyse_t23g2.py` carries `R2`–`R5`. **All FIVE working-tree shas above are also
the shas at `HEAD`** `[MEASURED]`, checked file by file — the grading was
performed against committed code, not against uncommitted working-tree state.

**What the recorder explicitly does NOT claim**, in its own words on the
artifact's face: *"THIS RECORDER DOES NOT RESTORE THE REGISTERED PROVENANCE AND
DOES NOT CLAIM TO."* `:671` contemplated shas present from the **first graded
solve**; adding the recorder changes the comparator's own sha, so only the
forward half is available (`§2d.4.3`). **No graded solve was ever produced under
a comparator carrying this recorder** — that line is printed by the instrument
itself, before the first gate.

The fifth file is not decoration. `analyse_t23g2.py:46` imports
`t23g_readonly_diagnosis` and uses it in `yplus_from_fields`,
`_first_cell_heights`, `gate_meshsim` and `_u_maxima` — **it is on the grading
path for `G-YPLUS`, `G-MESHSIM` and `G-CONV`**, and the petition's four-file list
omitted it. `verification` required five, on the ground that *"a sha recorder
that leaves a grading-path member silent is the defect it was built to cure."*

---

## 6. THE FIVE REPAIRS, AND THE GRANT THAT AUTHORISED THEM

**The grant.** `VERIFICATION_CHARTER.md` v1.38 **§2d.5–§2d.8**, commit
`3dad5bae`, 2026-09-02T21:25:25Z. Six items petitioned in
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T23G2_GRADING_PATH_REPAIR_PETITION.md`;
four granted (two widened beyond what was asked), one split with half refused,
one refused outright. **Zero solver compute; 0 core-min; $0.00. Gates,
thresholds, bands, caps and labels created, moved or retired: 0 · 0 · 0 · 0 · 0.**

**The new charter clause the grant rests on — `§2d.5`.** `§2d.1` condition (2)
demands an instrument independent of the hypothesis, and all its examples are
executable. Five of the six items were found by **reading the frozen registration
against the code**, and no executable instrument existed. `verification` ruled
that a **sha-frozen pre-registration IS such an instrument — when and only when
the defect is a demonstrable departure from its text**, exhibited by quotation
**and** by measurement, because a document written before the answers existed and
frozen by sha cannot know which direction a verdict wants. **And it narrows as
hard as it opens: silence cannot be departed from.** An inference from silence is
the preference condition (1) excludes.

| repair | commit | what was defective | what it fixed |
|---|---|---|---|
| **`R1`** completion allow-list | `768203a9` | `mark_done_t23.py`'s allow-list is a registry, and it did not carry `T23G2_L1/L2/L3` — it refused them with **rc 2 before reading a field**, against `:539-541` which registers completion as delegated to that very tool | Admits the three T23G2 names. Widening an allow-list **cannot make a failing case pass**; the instrument is fail-closed before and after. Blast radius measured: T23 carries its own `CASES` at `analyse_t23.py:88`, CASE3 inherits T23's position, T24 references it only in a docstring |
| **`R2`** grading-path sha recorder | `23d9d9b2` | A registered feature (`:671`) **never built** — zero occurrences of `grading_path`/`shas`/`hashlib`/`sha256` in 653 lines | Prints the five-file dual-sha table of §5, with `§2d.4.3`'s two-column condition and the line stating no graded solve ever ran under a recorder-carrying comparator |
| **`R3`** `G-ORDER` made reachable | `c2ce64a5` | `A1.2` at `:834` registers `G-ORDER`, but `ORDER_BAND` and `ORDER_QUANTITY` each occurred **twice**, both second occurrences inside a single `note()`, and `RT.grade_ladder` carries no order-band parameter — **the gate could not return `GATE FAIL` under any value of p** | `G-ORDER` is now a gate that can fail and folds into the rung rollup. The band [0.5, 1.5] is frozen **pre-compute** at `:833-834` and is untouched. **Direction: restrictive — it can only ADD a `GATE FAIL`. On this data it adds none** (p = 0.6111 ∈ [0.5, 1.5]). **⚠ AMENDED 2026-09-02 — `R3` AS DELIVERED IS ITSELF DEFECTIVE: the gate it built emits `PASS` from p(`Q4`) = 0.6111, an order belonging to a triple rule 5 step (1) had already voided, because `gate_order` consults only the triple state and never the iterative-convergence states. The `PASS` is not citable as a passed gate. Repair `R7` petitioned; see §14** |
| **`R4`** band limb *(rollup limb REFUSED)* | `ab5e753c` | `:455` gives `Q6`'s entire registered role with **no band**, and `:581` passed it `BAND_Q1` anyway. **`verification` found the petition under-reported its own defect: `Q4` receives the same unregistered band at the same line** (`:450` registers it as the primary order quantity with no fine-value band). Two quantities, not one | Band verdicts on `Q4` and `Q6` are now printed as **`DISCLOSED, NOT GRADED`** — what an unregistered band would have said, licensing nothing. **Non-permissive on this data:** both currently `PASS` that band, so the repair removes two `PASS`es and no `GATE FAIL` |
| **`R5`** the eighteen controls | `91bb04f8` | See §7 — **the most important of the six** | 18 quantity controls in place of 5, both y+ reader controls built and mutation-tested, and the exact-zero `G-RATIO` licence made **executable** |

**Refused, and recorded here so nobody reads the list as six granted:**

- **`R4`'s rollup-exclusion limb — REFUSED** on conditions (1) and (2) *and* on
  direction. No registration text excludes a reported-only quantity's verdict
  from the rollup; the petition cited none; it was an inference from silence.
  And the petition **misstated the direction** — it wrote that removing `Q6`
  *"could remove either a `PASS` or a `GATE FAIL`"*, when measured it removes
  **neither**: `Q6`'s row verdict is `NOT A RESULT`, and the rollup tests
  `"NOT A RESULT" in verdicts` **first**. The omitted case was the case that
  obtains, and it was the **strictly permissive** one. `verification` registered
  a general property from it: **removing a row from a rollup can only weaken the
  rollup or leave it equal — it can never strengthen it, so a rollup exclusion is
  ALWAYS permissive and requires registered text, never an inference.**
- **`R6` — REFUSED and REFERRED.** See §8. **It is not fixed and this record does
  not present it as fixed.**

---

## 7. ⚠ `R5`'s FINDING — SIX EXACT-ZERO `G-RATIO` PASSES WERE BEING CARRIED WHILE THIRTEEN OF THE EIGHTEEN REGISTERED CONTROLS DID NOT EXIST

**This is a standing-rule-3 failure, found in our own comparator, and it is the
most important thing this rung produced.**

`T23G2_PREREGISTRATION.md:624-625` registers **18 quantity controls plus 2 y+
readers = 20**. The frozen code built **five**: `plant_control_for` was called at
**one line**, at `LEVELS[-1]` only, for `Q4 Q1 Q2 Q3 Q6`. **`Q5` had no control
at all, and neither the coarse nor the medium level had one for anything.
THIRTEEN OF THE EIGHTEEN DID NOT EXIST.**

**Why this is not bookkeeping.** `G-RATIO` passes on **all six** quantities
**only** because the measured finest-level iterative change is **exactly `0.0`**,
and `g_ratio` returns `PASS` with ratio ∞ on a zero **on the stated ground that a
planted-zero control is what makes an exact zero mean something.** The series is
genuinely bit-identical (`3.411950435137e+02` at every sample, 13 significant
digits). So: **six exact zeros were carrying six `G-RATIO` passes while thirteen
of the eighteen controls that would license them did not exist.**

That is **standing rule 3's exact shape** — *a zero from a reader not shown able
to see a non-zero is not evidence*. **Even T23G2's PASSING gates were
unlicensed.**

§5.4 (`:601-602`) separately registers that the y+ reader *"must plant a known
perturbation and read it back, and refuse if it cannot see it (rule 3)"*.
`yplus_from_fields` contained **no plant** and argued its validity
**documentarily**. That is the second half of the same failure.

**What `R5` changed.** All 18 quantity controls are built, one per quantity per
level, and **each is asserted as it is built** by `RT.assert_plant_control`,
which **refuses** on a control that did not read its plant back — so an
unconstructable or blind control now **stops the comparator** instead of being
counted. Both y+ reader controls are built and live (§4, controls 19–20). And
`g_ratio` now **takes the finest-level control for that quantity as an argument
and refuses without it**: the exact-zero licence is no longer an argument in a
comment, it is executable.

**The generalisable lesson, stated plainly: a comparator that documents a control
it does not build is more dangerous than one with no control at all, because the
documentation is what stops anybody looking.** This is offered to the lab, not
just to T23G2 — the pattern is a registered count the code does not meet, and
`§2d.5` now makes exactly that shape findable by the registration itself.

---

## 8. ⚠ `R6` IS **REFUSED AND REFERRED** — `gate_yplus`'s "PRIMARY INSTRUMENT ABSENT" PASS-THROUGH IS UNREPAIRED

`analyse_t23g2.py`'s `gate_yplus` has three branches for the primary log
instrument: **PRESENT** (agreement checked at 2 %), **BLIND**, and **ABSENT**. On
`ABSENT` it prints *"the independent reader carries the gate"* and **continues to
grade**. `R6` proposed making an absent primary instrument a **refusal**.

**`verification` REFUSED it as a `§2d.1` repair** (`§2d.7`, `§2d.8`): §5.4
registers **two** instruments and a 2 % agreement check, and registers that a
**disagreement** is a refusal. **A missing instrument is neither agreement nor
disagreement — the registration does not name the case**, and the petition said
so itself. Under `§2d.5` **silence is not a departure**, so condition (2) has no
object and `§2d` stands.

**This is a refusal on the instrument, not on the merits.** `verification`
recorded that *"`R6` is a good change"* — it is strictly stricter, and it is
**measured inert on this data**: all three `log.yPlus.fluid` are present, parsed,
four patches each, and the `ABSENT` branch is **never taken** in this grading (the
comparator printed *"primary instrument PRESENT and agrees…"* at all three
levels).

> **OWED, AND OPEN: register the refusal PROSPECTIVELY in the next rung's
> pre-registration**, where it costs nothing and needs no exception. *"A gap in a
> registration is closed by the next registration, not by repairing the rung that
> revealed it."* **This record does not claim `R6` is fixed. It is not.**

---

## 9. THE REGISTERED PREDICTIONS — WHAT HELD AND WHAT LOST

| prediction | registered | measured | outcome |
|---|---|---|---|
| **P1′** the observed order | p(`Q4`) = 1.0, inside **[0.7, 1.3]** (`:977`) | **0.6111** | **LOST** — below the band. And it cannot even be scored as a grid claim: the triple contains a non-converged level |
| **P2′** the fine value | ΔT_max(`Q1`, `T23G2_L3`) = 51.0 K, inside **[48, 53]**, and **below** `T23G_F`'s 52.81450113 K (`:986-990`) | **52.60582825 K** | **HELD, both limbs** — inside the band, and below 52.8145. *Held on a triple that licenses no grid claim; the fine value is a measurement, not an extrapolation, so the directional claim survives that* |
| **P3** y+ on `fluid_to_housing` | **0.752 / 0.501 / 0.334**, each ±20 % (`:492`) | **0.751329 / 0.505692 / 0.339660** | **HELD** — misses of −0.09 %, +0.94 %, +1.69 %, all far inside ±20 % |
| **P3** y+ everywhere else | *"max y+ < 1.0 on every wall patch of every level"* (`:493-494`) | `centrebody_up` **1.8245 / 1.3539 / 1.0047** | **LOST** — §1.2 |
| **P4** `Q5` | **`DIVERGENT` or `STAGNANT`** (`:496-500`) | **`DIVERGENT`**, order −1.7108 | **HELD** — the failure was called before the run |
| **P5** similarity repair moves p by < 0.05 | registered as **not isolable by this rung** (`:502-506`) | — | **NOT EVALUABLE**, as registered. It needs the single-variable successor |
| **P6′** cost | actual inside **[400, 950] core-min**, ratio in **[0.69, 1.64]** (`:992-995`) | **536.77 core-min, ratio 0.9268** | **HELD** — §10 |

**A2.2's own forecast is falsified, and it belongs here because the registration
volunteered it.** A2.2 predicted maxima on `duct_wall` and `fluid_to_housing` —
**both met**. **It registered no prediction for `centrebody_up`, the one patch
that fails**, and closed with *"This costs nothing, because the design already
meets it."* **The run falsifies that sentence.** A prediction that covers only
the patches that pass is not a prediction. **The gate was still honestly
registered as "every wall patch", and it is the gate that binds, not the
forecast.**

### 9.1 A2.1 — THE DISCRIMINATING OBSERVATION, AND THIS RUNG CANNOT SETTLE IT

Registered before the run: **H-MESH** predicts spread(p(`Q4`), p(`Q1`)) **< 0.05**
with p in **[0.7, 1.3]**; **H-IFACE** predicts spread **> 0.15** with p in
**[0.25, 0.65]** and **the housing quantity LOWER**.

**Measured:** p(`Q4`) = **0.6111**, p(`Q1`) = **0.6148**, spread = **0.0036**.

| hypothesis | spread limb | p-range limb | ordering limb | reading |
|---|---|---|---|---|
| **H-MESH** | **met** (0.0036 < 0.05) | **missed** (0.611 ∉ [0.7, 1.3]) | — | half met |
| **H-IFACE** | **missed** (0.0036 ≯ 0.15) | met (0.611 ∈ [0.25, 0.65]) | **missed** — the housing quantity p(`Q1`) = 0.6148 is **HIGHER**, not lower | two of three limbs against |

**The observation points AGAINST H-IFACE and does not confirm H-MESH.** On T23G
the spread was 0.0027, a point against H-IFACE recorded before this run, and this
rung reproduces that direction at 0.0036.

**⚠ And it is offered as a direction, not a finding.** Both orders come from
triples containing `T23G2_L2`, which is not iteratively converged — rule 5 step
(a) says **no grid claim can be made from these triples**. **A2.1 is therefore
NOT settled by this rung**, and the successor that settles it must first produce
a triple in which every level converges.

---

## 10. COST CALIBRATION — RULE 12

**Actuals are core-minutes read from each level's own `STATUS.T23G2_L<n>` file**
under
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_L<n>/`.
**Ranks are MEASURED as 1** at every level — each `STATUS` carries `ranks=1`, and
each `START` carries `decomposition=NONE  # recorded AS AN ABSENCE`, i.e.
`decomposePar` was not run.

| level | cells | `endTime` | wall s | ranks | **actual core-min** | POINT | CAP | `capped` |
|---|---|---|---|---|---|---|---|---|
| `T23G2_L1` | 40,320 | 6,000 | 1,047 | 1 | **17.4500** | 17.0 | 45.0 | 0 |
| `T23G2_L2` | 90,720 | 12,000 | 5,118 | 1 | **85.3000** | 89.6 | 220.0 | 0 |
| `T23G2_L3` | 204,120 | 24,000 | 26,041 | 1 | **434.0167** | 472.6 | 1,100.0 | 0 |
| **CAMPAIGN** | | | | | **536.77** | **579.2** | **1,365** | **0** |

**Ratio actual/predicted = 0.9268.** **No level was capped; no timeout fired.**

**USD — DERIVED, NEVER MEASURED.** 536.77 core-min = 8.9461 core-h ×
$0.0513/core-h = **$0.4589**. `cost_basis = REPORTED-BY-OWNER`: the rate is
owner-stated (2026-08-21/22) and **the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5). No dollar figure in this record is a
measurement.

**Gap attribution — a mild UNDER-run, and it is misprediction in the
conservative direction, not waste.**

- **Waste: zero.** No level was restarted, no level was capped, no timeout fired,
  no level was abandoned and re-solved. Every core-minute above bought a
  completed level under rule 4. Nothing is folded into the ratio.
- **The figure published is GROSS, 536.77 core-min, and the stall rule is named
  rather than silently applied.** `COMPUTE_BUDGET_CHARTER.md` §2 defines cleaned
  as gross minus the rows its one stall rule matches — *"a ledger row over 3600
  wall seconds is an infrastructure stall, not solver cost"*. **Two of the three
  levels exceed 3600 wall s** (`L2` 5,118 s; `L3` 26,041 s). **They are not
  stalls**: each ran continuously to its registered `endTime` with rc 0, exactly
  one `End` line, and an `ExecutionTime` count equal to `endTime`, under
  registered timeouts of 13,200 s and 66,000 s that were set for precisely these
  durations at `:949-954`. **Mechanically applying the rule would strip 519.32 of
  the 536.77 core-min as "infrastructure" and leave a cleaned figure that is
  plainly false.** This record therefore publishes **gross** and states why, per
  §2's own instruction that a cleaned figure must name its rule: the rule's
  object is a `self_audit.py` ledger row, and a registered multi-hour solve is
  not that object. **Referred to `verification` as a live gap in §2, not decided
  here.**
- **The miss is in the per-iteration basis, and it is small.** The estimate was
  built from `T23G_F`'s **measured** 145.75 core-min for 10,000 iterations at
  158,720 cells at `ranks = 1` (0.0145750 core-min/iteration), scaled by T23G's
  measured superlinear exponent **1.1957** on cell count. Realised per-iteration
  cost came in **below** the basis at the two levels that dominate the spend and
  **slightly above** at the cheapest: `L1` **0.0029083** vs 0.0028300 predicted
  (**+2.8 %**), `L2` **0.0071083** vs 0.0074663 (**−4.8 %**), `L3` **0.0180840**
  vs 0.0196915 (**−8.2 %**). All three derived from the table above.
- **Direction is consistent with the box being quieter than the basis run.** The
  basis was measured on a shared box; `T23G2_L1`'s `START` records
  `loadavg=3.51 3.02 4.86` on 16 cores at launch. **The load at the basis
  measurement is not recorded**, so this attribution is **stated as the likely
  cause and NOT as a measurement.** It repeats the calibration lesson already in
  the ledger at row C-4: *record the load average beside any per-iteration cost
  basis, and state the load the basis is being re-applied at.*
- **P6′ HELD**: 536.77 ∈ [400, 950]; ratio 0.9268 ∈ [0.69, 1.64].

**A ledger row is landed for this rung** in
`/home/ubuntu/Certonomous/docs/COST_CALIBRATION.md`. `verification` noted at
`§2d.8` that no such row existed and that *"whether a rung that cannot be graded
has 'completed' for rule 12's purposes is heat-transfer's to state"*. **This team
states it: the rung is COMPLETE for rule 12's purposes.** The process that was
budgeted — build, solve three levels, grade — is finished, and it produced a
verdict from the fixed vocabulary. `NOT A RESULT` is a **verdict**, not an
absence of one, and a rung that spent 536.77 core-min to reach one has completed
exactly the process it was costed for.

---

## 11. ⚠ OPEN ITEMS — WHAT THIS RECORD CANNOT CLOSE

Stated as gaps, not as caveats, because each is something a reader could
otherwise assume is settled.

1. **The launcher is UNTRACKED, so the script that produced the sidecars cannot
   be proved to be the script on disk.**
   `/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/run_t23g2.sh`
   and
   `/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/preflight_gate_t23g2.py`
   are **not in git** — `git ls-files --error-unmatch` fails on both
   `[MEASURED]`. **They therefore have no committed sha**, and every figure this
   record takes from a `STATUS.` or `START.` sidecar — wall seconds, `rc`,
   `ranks`, `capped`, `start_utc` — is read from a file written by a program
   whose content at write time cannot be established. **The physics is unaffected:
   `log.solve` is the artifact for the solve itself, and rule 4's conjuncts are
   re-derivable from it. The provenance of the sidecars is not.** This is
   disclosed, not repaired.
2. **The comparator lives at the wrong registered path.**
   `T23G2_PREREGISTRATION.md:662-663` registers it as
   `verification/runs/T-family/T23G2_runs/analyse_t23g2.py`. It is at
   `/home/ubuntu/Certonomous/docs/campaigns/T-family/analyse_t23g2.py`. The
   grading was performed with the file at the second path. The sha table of §5
   pins **which bytes** ran; it does not reconcile **where they live** against the
   registration. Referred, not resolved here.
3. **The guards' mutation kill-rate is being measured separately, and this record
   is NOT FINAL until that lands.** `R5`'s controls and `R3`'s newly-reachable
   gate are asserted to refuse and to be able to fail; the *rate* at which the
   guard set kills injected mutations is a separate measurement in flight. **Until
   it lands, §4's "20 of 20 PASSED" is a statement that every control was
   constructed and read its plant back — it is not yet a statement about how much
   the guard set would catch.**
4. **`R6` is unrepaired** (§8) and is owed a **prospective** registration in the
   next rung.
5. **`P5` was never evaluable** by this rung, as registered. It needs the
   single-variable successor.
6. **⚠ `G-ORDER`'s `PASS` is unlicensed and the instrument that produced it is
   unrepaired.** `gate_order` gates on a triple rule 5 voided at step (1). This
   record caveats the `PASS` everywhere it appears (§2, §3, §6, §12, §14) but
   **cannot repair the gate** — the comparator is post-compute on the grading
   path and a repair is `verification`'s to grant. Petitioned as `R7` at
   `/home/ubuntu/Certonomous/docs/campaigns/T-family/T23G2_R7_ORDER_GATE_PETITION.md`.
   **Open until ruled.**

---

## 12. WHAT THIS RUNG DOES NOT LICENSE

- **No grid-convergence claim of any kind.** Every triple contains a level that is
  not iteratively converged. The `CONVERGING` states, the orders 0.610–0.615 and
  the GCIs 5.27–5.85 % are **printed and are not claims**.
- **No fine-value claim.** `Q1`'s 52.606 K and `Q4`'s 53.195 K are measurements
  at a mesh, not converged values.
- **No settlement of H-MESH vs H-IFACE** (§9.1).
- **No conclusion that y+ ≤ 1 was achieved.** It was achieved on three of four
  wall patches. The gate is on four.
- **No citation of `G-ORDER`'s `PASS` as a passed gate, at all.** It is not merely
  silent about the discretisation — the order it gates on belongs to a triple rule
  5 voided at step (1), and the gate never consults the iterative-convergence
  states, so the `PASS` licenses nothing whatever (§2, §14).

## 13. WHAT WOULD TURN THIS INTO A RESULT

1. **Converge `T23G2_L2`.** It missed by 4.1 % on one residual. This is the
   cheapest of the three and it is the one that propagates: clearing it alone
   removes rule 5 step (a) from every row.
2. **Resolve `centrebody_up`.** The registered ≤ 1.0 is missed by 82 % at L1 and
   by 0.47 % at L3 — the patch is converging toward the gate but has not reached
   it at 204,120 cells. It needs first-cell refinement on that patch
   specifically, not another uniform level.
3. **Re-examine `Q3`'s band.** 56.708 K against [46.0, 56.0] is 0.708 K high, and
   the fine value is still descending monotonically (58.238 → 57.379 → 56.708).
   The band may be right and the mesh not yet fine enough; the band cannot be
   moved for T23G2 (rule 2, gates closed) and the question belongs to the
   successor's registration.
4. **Register `R6` prospectively** and carry the mutation kill-rate measurement
   into the successor's pre-registration rather than after it.

---

## ⚠ 14. AMENDMENT, 2026-09-02 — `G-ORDER`'s `PASS` IS UNLICENSED, AND THE RECORD SAYS SO WHEREVER THE NUMBER APPEARS

**Nothing measured is changed by this amendment. No value, no order, no GCI, no
gate verdict as the comparator printed it, and not the rung verdict.** What
changes is what the record permits a reader to do with one printed `PASS`.

**Scope of the edit, stated because the convention is to state it.** This
amendment is appended at the foot, and **caveat markers were also inserted inline
at every place the affected number appears** — §0 (the `R3` direction bullet), §2
(the gate table row and the paragraph beneath it), §3 (beneath the quantity
table), §6 (the `R3` row), §11 (new open item 6) and §12. The brief this
amendment answers required the caveat to travel **in the same breath** as the
number rather than in a footnote, so unlike a frozen grading-path file this record
**cannot** assert `lines whose number changed above this section: 0` — line
numbers above did shift. **No sentence above was deleted; the one sentence that
was superseded (§2's "a gate result, not a grid-convergence claim") is quoted
verbatim where it stood and then withdrawn, not rewritten away.** **No file
external to this one cites this record by line**: a repository-wide `grep` for the
line-citation form of this filename returns exactly one hit, and it is this
sentence describing the check `[MEASURED]` 2026-09-02.

### 14.1 The defect

`gate_order` in
`/home/ubuntu/Certonomous/docs/campaigns/T-family/analyse_t23g2.py` — the
function repair `R3` delivered, committed at `c2ce64a5` — decides `G-ORDER` from
**exactly two fields of the graded row**:

- `row["orders"][-1]`, the finest triple's observed order (`:917`), and
- `row["states"][-1]`, the finest triple's state (`:918`).

It **never consults `row["iterative_convergence"]`**. That field is not missing.
`RT.grade_ladder` writes it onto the very same row it hands back
(`/home/ubuntu/Certonomous/scripts/roache_triple.py:601`), alongside `orders`
and `states`, which are populated **unconditionally at row construction**
(`:597-598`) — that is, *before* rule 5's step (a) runs at `:604-618` and sets
`row["verdict"] = "NOT A RESULT"`. So a row that step (a) has voided still
carries a `CONVERGING` triple state and a numeric order, and `gate_order` reads
those two and grades on them.

**The information required to decline the gate was present on the object being
gated, and was not read.**

### 14.2 The consequence, measured

Both readings are from the comparator's own captured output, landed beside the run
at
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/T23G2_GRADE.out`
(sha256 `40f2fa33f4818cad7834e86257cd9dac8c6b786f24662c87bb0ffe2927261d2b`; a
byte-identical copy of the stdout of the 2026-09-02 grading, placed under the run
directory because the original capture lived only in a session scratchpad, which
rule 13 forbids a repository document to cite — **it is a copy of a capture, not a
re-run, and is labelled as such**):

- **`:115`** (and identically `:126`, `:131`, `:136`, `:141` — one per graded
  quantity): `VERDICT: NOT A RESULT -- levels T23G2_L2 are not iteratively
  converged or not plateaued; no grid claim can be made from this triple`.
- **`:162`**: `G-ORDER: PASS`, from `:161` `p(Q4) = 0.6111, band [0.5, 1.5],
  finest triple CONVERGING`.

**`G-ORDER` reports a `PASS` derived from a ladder whose grid claim rule 5 had
already voided, forty-seven lines earlier in its own output.**

`CLAUDE.md` rule 5 fixes the ordering explicitly: step (1) — *any level not
iteratively converged or not plateaued → `NOT A RESULT`*. The observed order is a
property of the grid claim, and the grid claim does not survive step (1) to be
gated. **An unevaluable gate reported as a pass is the "evidence annotated as
non-binding" failure inverted: a non-binding number annotated as a gate result.**

### 14.3 The contrast that is the actual lesson

The lane that graded this rung had the right instinct **and applied it once**.

**At `A2.1` (§9.1) it refused to bank the discrimination**, in terms: *"Both
orders come from triples containing `T23G2_L2`, which is not iteratively converged
— rule 5 step (a) says no grid claim can be made from these triples. A2.1 is
therefore NOT settled by this rung."* p(`Q4`) = 0.6111 and p(`Q1`) = 0.6148 were
declined as evidence **on precisely the ground that voids `G-ORDER`**.

**The identical reasoning was simply not applied to `G-ORDER`.** The same two
numbers, from the same rows, disqualified in one section and gated in another. §2
went half the distance — it declined to read the `PASS` as evidence about the
discretisation while still calling it *"a gate result"* — and that half-step is
what this amendment completes.

**The comparator itself had already written the rule down.** Repair `R4`'s
`_apply_band_registration` states it as the whole safety argument
(`analyse_t23g2.py:870-874`): *"this can only turn a `PASS` or a `GATE FAIL` INTO
`NOT A RESULT`, which is the one direction rule 5 permits … It can never turn a
non-`PASS` into a `PASS`."* `R4` applies that; `R3` does not. **Two repairs
landed the same day in the same file, one honouring rule 5's ordering and one
not.**

### 14.4 What this record now asserts, and what it does not

- **`G-ORDER`'s printed verdict remains `PASS`.** That is what the comparator
  printed and the record reports it faithfully. **It is not citable as a passed
  gate**, in this record or anywhere downstream.
- **The rung verdict is untouched: `NOT A RESULT`**, on `G-CONV` and `G-YPLUS`,
  on grounds that predate every repair (§0, §1). **Nothing here would change it in
  either direction** — which is exactly why the repair petitioned below should be
  judged on the instrument and not on the outcome.
- **This record does not repair the gate and has no standing to.**
  `analyse_t23g2.py` is post-compute on the frozen grading path; a change to it
  is a `§2d.1` matter for `verification`. Petitioned as **`R7`** at
  `/home/ubuntu/Certonomous/docs/campaigns/T-family/T23G2_R7_ORDER_GATE_PETITION.md`.
  **The petition is a draft addressed to `verification-supervisor`. It has not
  been acted on, and heat-transfer has not ruled on it.**
- **`R6` remains refused and unrepaired** (§8). `R7` is a separate defect in a
  *granted* repair and is not an attempt to reopen `R6`.
