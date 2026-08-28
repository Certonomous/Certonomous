# D18 — RESULTS. `CURRICULUM-D18`, cone/wedge at Mach 5.0002, `DAHisaFoam`

**Item verdict: `PASS`.** Both rows `PASS`. Graded 2026-08-28T03:28:52Z by the frozen
comparator, `grader_rc=0`.

**Everything below is read from named artefacts in the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic` and from the grade file
`D18_grade_20260828T032852Z.json` in it.** No number in this record is recomputed from
memory, and every figure that is absent is named as absent rather than approximated.

---

## 0. THE HONEST-NAMING CAVEAT — READ THIS BEFORE QUOTING ANYTHING BELOW

**"Hypersonic" here names a MACH NUMBER and nothing else. It does not name a modelled
physical regime, and this item must never be quoted as a hypersonic-physics result.**

What the case ACTUALLY models, read from the staged case at
`<run root>/base/constant/thermophysicalProperties`, `constant/turbulenceProperties`,
`0.orig/U`, `0.orig/T` and `0.orig/include/freestreamConditions` — not assumed:

| what | as staged | consequence |
|---|---|---|
| equation of state | `perfectGas`, `molWeight 28.966` | **ideal gas.** No real-gas / high-temperature equation of state. |
| thermodynamics | `hConst`, **`Cp 1005` constant**, `Hf 0` | **calorically perfect.** Cp does not vary with temperature, so **vibrational excitation is not modelled at all** — the mode that begins to matter in air well below the stagnation temperature this freestream implies. |
| chemistry | `pureMixture`, `specie` with one species | **no chemistry, no dissociation, no ionisation, no finite-rate kinetics.** Air is one inert perfect gas. |
| transport | `transport const`, **`mu 0`** | **inviscid (Euler).** No boundary layer, no skin friction, no viscous heating. |
| turbulence | `simulationType RAS`, `RASModel dummy` | **no turbulence model does any work.** |
| wall | `cone`: `U` `slip`, `T` `characteristicWallTemperature` | **inviscid slip wall.** No wall heat flux is solved and none is graded. No radiation anywhere in the setup. |
| energy | `sensibleInternalEnergy` | sensible energy only; no formation enthalpy, no reaction source. |
| freestream | `U (1736.0 0 0)`, `p 101325.0`, `T 300.0` | a = 347.1887 m/s, **M = 5.0002** (gate G-MACH, below). |

**So the physics solved is: 2-D inviscid, calorically-perfect, single-species,
non-reacting compressible flow over an 11.3099° wedge at Mach 5.** Every phenomenon a
reader would expect from the word "hypersonic" — high-temperature gas effects,
vibrational excitation, dissociation, ionisation, viscous interaction, aerodynamic
heating, radiation — is **absent from this setup**, and its absence is a property of the
staged case, not an omission of this record. The grader carries the same statement in
its own output, in the `real_gas_caveat` field of
`D18_grade_20260828T032852Z.json`:

> *"PERFECT GAS, CALORICALLY PERFECT. thermophysicalProperties carries a constant Cp and
> mu 0; at M 5 real air begins to show vibrational excitation and, higher still,
> dissociation. NONE OF THAT IS MODELLED. This cell is hypersonic IN THE MACH NUMBER
> ONLY, and the record says so rather than letting the grid imply a physical regime the
> solver never solved."*

This was registered before compute, not discovered after: `PREREGISTRATION.md:13` fixes
the case as **inviscid** (`mu 0`, `RASModel dummy`), and `PREREGISTRATION.md:103` (§9,
"WHAT THIS ITEM WILL NOT ESTABLISH") registers **"nothing about real-gas hypersonics …
perfect gas, no vibrational excitation, no dissociation, no viscous or radiative
heating"**.

**What D18 therefore IS:** evidence that the DAFoam/`DAHisaFoam` adjoint produces a
gradient that agrees with finite differences **when the primal is a Mach-5 Euler solve on
this mesh**. It is a statement about the *adjoint machinery at a high Mach number*, not
about *hypersonic aerothermodynamics*.

---

## 1. TOOLCHAIN IDENTITY — BY HASH, NOT BY VERSION STRING

`DAFOAM_CHARTER.md` §6: a version string is not an identity. Both identities below are
**image digest + the md5 of the IDWarp shared object as read inside the running
container**, taken from the arm ledger `<run root>/ledger.txt` and cross-checked by the
grader against the value it read out of each arm's own artefact
(`gates.G9_toolchain.per_arm`, verdict `PASS`).

| row | arms | image digest | idwarp `.so` md5 (printed by the container) | `.so` md5 re-read from the artefact | agree |
|---|---|---|---|---|---|
| **SHIPPED** | MESH, X-S, F-S | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` | `f0fcb488e0e98156575cd19548e91663` (X-S, F-S) | yes |
| **PATCHED** | X-P, F-P | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | `85f59e87253e0a71a813f64ca6e4c425` | yes |

**`NOT MEASURED`, named:** `artefact_so_md5` for the **MESH** arm is `null` — that arm
writes `checkMesh.log` and no JSON artefact, so there is nothing to re-read the md5 out
of. The printed value stands alone for MESH. The grader records this and still returns
`PASS` for G9; it is recorded here rather than left to be inferred from a `null`.

**Grading path, frozen and verified.** `PREREGISTRATION.md:120` fixes `d18_grade.py` at
md5 `e4ade11ed9e3db18d2c4988b30e929b4`. Verified by this lane at write time: the file on
disk and the committed blob at HEAD both hash to
`e4ade11ed9e3db18d2c4988b30e929b4`. The file that graded is the file that was frozen
(standing rule 2).

**Pre-registration freeze:** `dae3dc9d17dab4ecda7d44e30c9a3016637f9987`
(2026-08-27T17:38:57Z). **Addendum A** landed at `ed4983bd` (2026-08-27T19:42:30Z), which
is **before first compute** (2026-08-28T02:18:44Z) and is therefore legal under rule 2;
its own §A.4 asserts that no gate, threshold, band, cap, label, prediction, cost, cpuset,
image or arm moves.

---

## 2. THE FD TABLE — THIS IS THE RESULT

The charter bright line: the FD table *is* the result. Per registered component the FD
reference is the **middle** of the three registered steps (`d18_grade.py:370-371`);
**PLATEAU** = the middle step agrees with **at least one** neighbour to **10 %**
(`PLATEAU_TOL_PCT = 10.0`, `d18_grade.py:85`, applied at `:379`); **band D** = per
component `|d_FD − J_adj| / |d_FD| ≤ 5.0 %` **and the same sign** (a sign flip is
`GATE FAIL` whatever the magnitude); **band E** = aggregate vector-relative error over
graded components ≤ 5.0 %. Steps registered `{1e-2, 1e-3, 1e-4}`, components
`shape[0,1,3,4,5]`, objective `cruise.aero_post.CD`
(`PREREGISTRATION.md:35`, `:48`).

**The FD columns `d_fd`, `d_ref` and `plateau_neighbour_pct` are IDENTICAL between the
two rows** — the FD table is produced once per objective from the F arms and the two rows
differ only in the adjoint `J_adj` they are compared against. That is why the plateau
failure at `shape[3]` appears in both rows.

### 2a. SHIPPED row — `PASS`

| dv | idx | `J_adj` | `d_fd` @ 1e-2 / 1e-3 / 1e-4 | `d_ref` (middle) | plateau vs neighbours (%) | `rel_err_pct` | sign flip | verdict |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | 1.7865473700422112e-02 | 1.774100208465218e-02 / 1.840853505871015e-02 / 1.8335994820956047e-02 | 1.840853505871015e-02 | 3.626215 / **0.394058** | **2.950052** | no | `PASS` |
| shape | 1 | 1.5581706431958487e-02 | 1.559826546200585e-02 / 1.568908602155722e-02 / 1.5635877086139782e-02 | 1.568908602155722e-02 | 0.578877 / **0.339146** | **0.684422** | no | `PASS` |
| shape | **3** | −2.4553924366522804e-04 | −5.879170205100315e-04 / −3.5147962595960536e-05 / −1.0391786910146639e-04 | −3.5147962595960536e-05 | **1572.691607 / 195.658301** | *(not computed)* | *(not computed)* | **`NOT A RESULT` — `NO_PLATEAU`** |
| shape | 4 | −3.988285477304851e-02 | −4.12962766875101e-02 / −4.046659090707616e-02 / −3.9732886569499026e-02 | −4.046659090707616e-02 | 2.050298 / **1.813111** | **1.442514** | no | `PASS` |
| shape | 5 | −6.195000827141202e-01 | −6.229321513856523e-01 / −6.194018700529241e-01 / −6.19569268747594e-01 | −6.194018700529241e-01 | 0.569950 / **0.027026** | **0.015856** | no | `PASS` |

**`n_graded` 4 · `n_pass` 4 · `n_gate_fail` 0 · `n_not_a_result` 1 · `sign_flips` 0.**
Aggregate (band E) **0.13046764846984363 %** against the 5.0 % band → `PASS`.
Band D `PASS`, band E `PASS`, **row verdict `PASS`**.
`CD_baseline` **0.07854521739673961**. `eta_F` (two-primal repeat noise floor)
**3.655409308578328e-14**.

### 2b. PATCHED row — `PASS`

| dv | idx | `J_adj` | `d_ref` (middle) | plateau vs neighbours (%) | `rel_err_pct` | sign flip | verdict |
|---|---|---|---|---|---|---|---|
| shape | 0 | 1.781191761130021e-02 | 1.840853505871015e-02 | 3.626215 / **0.394058** | **3.240983** | no | `PASS` |
| shape | 1 | 1.5511859458949001e-02 | 1.568908602155722e-02 | 0.578877 / **0.339146** | **1.129617** | no | `PASS` |
| shape | **3** | −8.742358210443467e-05 | −3.5147962595960536e-05 | **1572.691607 / 195.658301** | *(not computed)* | *(not computed)* | **`NOT A RESULT` — `NO_PLATEAU`** |
| shape | 4 | −3.981981389748575e-02 | −4.046659090707616e-02 | 2.050298 / **1.813111** | **1.598299** | no | `PASS` |
| shape | 5 | −6.195268673301305e-01 | −6.194018700529241e-01 | 0.569950 / **0.027026** | **0.020180** | no | `PASS` |

**`n_graded` 4 · `n_pass` 4 · `n_gate_fail` 0 · `n_not_a_result` 1 · `sign_flips` 0.**
Aggregate (band E) **0.1458900868751844 %** → `PASS`. **Row verdict `PASS`.**
`CD_baseline` **0.07854521739673961**, `eta_F` **3.655409308578328e-14** (the F arms are
the same table; the baseline is the SHIPPED primal's).

### 2c. `CL` — a SYMMETRY READING, NOT GRADED, MOVES NO VERDICT

Registered as a reading, not a gate (`PREREGISTRATION.md:13`, `:48`; D17 §3 (ii)): the
wedge is y-symmetric at 0° incidence, so `CL` and `dCL/dshape` are **zero by
construction** and a `NEAR_ZERO` grade would be an artefact of the geometry, not a finding
about the gradient.

| row | `CL_baseline` | `max abs J_adj CL` | `max abs d_FD CL` |
|---|---|---|---|
| SHIPPED | 5.828670879282072e-16 | 1.2191109233861477e-05 | 2.8221114205251308e-05 |
| PATCHED | 5.828670879282072e-16 | 2.0277704209849257e-05 | 2.8221114205251308e-05 |

Reported; **it moves no verdict**, by registration.

---

## 3. ⚠ ONE COMPONENT IS `NOT A RESULT` INSIDE A `PASS` ROW — STATED PLAINLY

**`shape[3]` is `NOT A RESULT` (`NO_PLATEAU`) in BOTH rows. It was not measured. The row
verdicts `PASS` do not cover it, and no reader should take "D18 PASS" to mean that all
five registered components were verified.**

**How many components were graded and how many passed:**

> **Per row: 5 components were registered; 4 were graded; 4 of those 4 passed; 1 —
> `shape[3]` — is `NOT A RESULT` and was never graded.** Across both rows: **10
> registered, 8 graded, 8 passed, 2 `NOT A RESULT` (the same component twice).**

**This is the REGISTERED behaviour, frozen before compute — not a post-hoc reading.**
The clause, quoted with its line, from the pre-registration D18 adopts verbatim
(`PREREGISTRATION.md:48` — *"Every gate, band, label and composition rule is D17 §3
(hence D16/D15), verbatim"*), at
**`cases/dafoam/ladder-a/A1/curriculum_D17_cone_supersonic/PREREGISTRATION.md:50`**,
clause (c):

> *"(c) the three-step plateau at 1e-4 may be noise-limited for the weakest component (η
> is measured by the two-primal repeat; **a component without a plateau is `NOT A RESULT`
> by name and the row still grades on ≥ 3**)."*

and the composition rule that lets the row stand, quoted with its line from
**`cases/dafoam/curriculum_D18_cone_hypersonic/PREREGISTRATION.md:48`**:

> *"**G5 band D 5.0 % per component with the sign-flip rule, band E 5.0 % aggregate,
> plateau 10 %, ≥ 3 graded components**"*

**The registered minimum is 3 graded components; 4 were graded.** The implementation of
that clause is `MIN_GRADED = 3` at `d18_grade.py:86`, enforced at `:396-398` (`if
n_graded < MIN_GRADED: … "NOT A RESULT", "reason": "fewer than 3 graded components"`), and
the grader's own selftest exercises **both** directions on a planted fixture:
`d18_grade.py:771-772` (U5) plants a no-plateau on one component and asserts the component
reads `NOT A RESULT` while the row still `PASS`es on 4 graded; `:773-774` (U6) plants three
no-plateau components and asserts the row and the item both become `NOT A RESULT`. So the
"a PASS row may contain a `NOT A RESULT` component" behaviour is registered, implemented
and tested, and the failing direction is tested too.

**Why `shape[3]` has no plateau, from its own numbers.** Its FD reference is
−3.5147962595960536e-05, roughly **four orders of magnitude smaller** than `shape[5]`'s
−0.619, and the three FD steps do not settle: 1e-2 gives −5.879e-04, 1e-3 gives −3.515e-05,
1e-4 gives −1.039e-04 — neighbour disagreements of **1572.69 %** and **195.66 %** against a
10 % tolerance. This is the *weakest component*, exactly the exposure clause (c) named in
advance. It is a **measurement-resolution statement about the FD probe at this component**,
not a statement that the adjoint is wrong there.

---

## 4. EVERY GATE READING

| gate | what it checks | reading | verdict |
|---|---|---|---|
| **G1** completion | arm-kind-aware, age guard, `.inspect.txt` kernel fallback, L-342 field classes | all 5 arms `kernel_rc = 0`, `oomkilled = false`, every field sourced from the `ledger_row`; artefacts `checkMesh.log` (MESH), `d18_X.json` (X-S, X-P), `d18_F.json` (F-S, F-P) | **`PASS`** |
| **G-M2** mesh identity | `cells == 40,000` (2 blocks × 100×100×1 = 20,000, doubled by `mirrorMesh`) | `mesh_cells` **40000** | **`PASS`** |
| **G5 SHIPPED** | the bright line, CD only | 4 graded, 4 pass, aggregate 0.1305 % | **`PASS`** |
| **G5 PATCHED** | the bright line, CD only | 4 graded, 4 pass, aggregate 0.1459 % | **`PASS`** |
| **G6** dot-product / duality | — | **`NOT MEASURED` — "the tutorial exposes no dot-product/duality test; named, never composed."** Registered as `NOT MEASURED` at `PREREGISTRATION.md:48`; it is not a gap discovered here. | `NOT MEASURED` |
| **G9** toolchain | two digests, two `.so` md5s, printed value == artefact value | all 5 arms `ok: true`; MESH `artefact_so_md5` `null` (no JSON artefact — named in §1) | **`PASS`** |
| **G10** caps | per-arm core-min against per-arm cap; item ceiling 785.0 | total **129.016** core-min; no arm crossed its cap; `not_measured: []` | **`PASS`** |
| **G11** OOM | kernel `OOMKilled` refuses G1 | `oomkilled = false` on all 5 arms | (folded into G1) |
| **G12** placement | delivered cores and `cpuset == 12,15` | cpuset `12,15` on all 5; delivered-core means 1.9867 / 1.9880 / 1.9910 / 1.9966 of 2 | **`PASS`**, with **MESH `delivered_cores_mean` `NOT_MEASURED`** (named in `not_measured: ["MESH"]`) |
| **G-MACH** freestream agreement | the BC file and the objective's normalisation are the same freestream, and it carries the registered value | `U0 = 1736.0` (registered 1736.0), `p0 = 101325.0`, `T0 = 300.0`, `a = 347.1887 m/s`, **`mach = 5.0002`**; `ledger_corroboration: PRESENT` | **`PASS`** |

**Per-arm caps and spend (G10):**

| arm | ranks | wall s | core-min | cap | crossed | actual/predicted |
|---|---|---|---|---|---|---|
| MESH | 1 | 11 | 0.183 | 5.0 | no | 0.915 |
| X-S | 2 | 205 | 6.833 | 90.0 | no | 0.7592 |
| F-S | 2 | 1918 | 63.933 | 300.0 | no | 0.7797 |
| X-P | 2 | 183 | 6.100 | 90.0 | no | 0.6778 |
| F-P | 2 | 1559 | 51.967 | 300.0 | no | 0.6337 |
| **total** | | | **129.016** | **ceiling 785.0** | **no** | **0.708** |

---

## 5. PLANTED CONTROLS (standing rule 3) — AND THEIR WORST RESIDUAL

Two independent plants, on two different readers, both **seen**:

**(i) The instrument's own `CTRL` component**, written by the producer with a derivative
of **exactly 0.0** and a companion **PLANTED** row with derivative exactly
`PLANT / (2·s)` where `PLANT = 1.234e-03` (`d18_xf.py:74`, `:245-254`). The grader re-reads
both from disk and **refuses** (`d18_grade.py:317-320`) unless the zero is exactly 0.0 and
the planted value matches to `1e-12` relative.

| row | `instrument_ctrl_zero` | `instrument_ctrl_planted` | `want` | seen |
|---|---|---|---|---|
| SHIPPED (S) | **0.0** | **0.617** | 0.617 | yes |
| PATCHED (P) | **0.0** | **0.617** | 0.617 | yes |

**(ii) The grader's own plant on the F table** (`d18_grade.py:324-348`): the grader writes
a copy of each F artefact with `PLANT = 1.234e-03` added to **every** physical `dCD`,
re-reads that copy **through the same `read_F` reader**, and refuses unless every value
moved by exactly `PLANT`.

| row | plant seen | values checked | **worst residual** | control file |
|---|---|---|---|---|
| SHIPPED | **true** | 15 | **4.2717565595928875e-17** | `<run root>/grader_controls/F_S_planted.json` |
| PATCHED | **true** | 15 | **4.2717565595928875e-17** | `<run root>/grader_controls/F_P_planted.json` |

**Worst residual across both: 4.2717565595928875e-17** — 14 orders of magnitude below the
plant. **The reader was shown able to see a non-zero before any zero it reports was
believed.** Both control files are on disk in the run root and are named above.

---

## 6. GCI — NONE IS QUOTABLE, AND NONE IS QUOTED

**There is no grid family in this item. D18 ran ONE mesh, 40,000 cells, and one only.**
Standing rule 5 has no row without a grid triple, so **no GCI is computed, no observed
order is computed, and no discretisation uncertainty is claimed anywhere in this record.**
This was registered before compute (`PREREGISTRATION.md:48`: *"no GCI (no grid family;
standing rule 5 has no row)"*) and the grader carries the same statement in its output
field `no_gci`:

> *"no grid family; standing rule 5 has no row; NO GCI IS QUOTED"*

**Consequence, stated so it cannot be glossed:** the FD-versus-adjoint agreement in §2 is
a **consistency check between two derivatives of the same discrete solution**. It says
nothing about how far that discrete solution is from the continuum one. **Mesh
convergence of `CD` at Mach 5 on this configuration is `NOT MEASURED` and is not claimed.**

---

## 7. PREDICTIONS, SCORED — INCLUDING THE TWO THAT MISSED

Scored by the frozen comparator, never adjusted.

| # | prediction | scored | reading |
|---|---|---|---|
| **P1** | `cells == 40,000` | **HIT** | 40,000 |
| **P2** | `abs(CL_baseline) ≤ 1.0e-3` | **HIT** | 5.83e-16 |
| **P3** | `CD_baseline` in [0.055, 0.105], point 0.078842 | **HIT** | **0.07854521739673961** — **0.377 %** from the oblique-shock point estimate. The 1-D attached-oblique-shock reading of this configuration does **not** break down at M 5. |
| **P4** | PATCHED row `PASS` with ≥ 4 of 5 in band D | **HIT** | row `PASS`, `n_pass` 4 |
| **P5** | SHIPPED `shape[0]` outside band D or sign-flipped | **MISS** | SHIPPED `shape[0]` is **inside** band D at 2.950052 % with no flip |
| **P6** | total core-min in [60, 450] | **HIT** | 129.016 |
| **P6b** | MESH wall ≤ 120 s | **HIT** | 11 s |
| **P7** | the two rows are **NOT** discriminating, S/N ≤ 1.0 | **MISS** | S/N **19.8691** |

### 7a. ⚠ A CAVEAT THIS LANE OWES AGAINST P7's OWN NUMBER — AND IT IS NOT A RE-RULING

`PREREGISTRATION.md:95` registered, before the run: *"If P7 MISSES — S/N > 1 — then D18
**is** discriminating and its P5 reading carries weight the D15/D16/D17 sequence did not.
That would be the surprise, and it is registered as such."* **P7 MISSED. The registered
reading of that MISS stands as written and this lane does not touch it.**

**But the reader must be told where the number comes from.** In `d18_grade.py:585-589`:

* the **numerator** (`worst_div`) is the worst shipped-vs-patched divergence over **all
  five registered components**, with **no filter on component verdict**;
* the **denominator** (`worst_noise`) is the worst PATCHED-row FD error over components
  that **have** a `rel_err_pct` — which **excludes** the `NOT A RESULT` component, because
  the grader never computes one for it (`:381-384`).

The measured numbers: `_P7_worst_divergence_pct` **64.39527107787734**, at **`shape[3]`** —
**the component both rows graded `NOT A RESULT` (`NO_PLATEAU`)**; `_P7_worst_patched_FD_error_pct`
**3.2409827588515716**, at `shape[0]`. The per-component divergences are `shape[0]`
0.299774 %, `shape[1]` 0.448263 %, **`shape[3]` 64.395271 %**, `shape[4]` 0.158065 %,
`shape[5]` 0.004323 %.

> **So the entire P7 signal is supplied by the one component the same grader declared was
> not measured.** Over the four **graded** components the worst divergence is
> **0.4482626682416995 %** (`shape[1]`) and the same S/N formula gives **0.1383** —
> which is **≤ 1.0**, the HIT side of the registered threshold. Arithmetic on the
> grader's own published numbers, computed by this lane and stated as such.

**This lane does not re-score P7 and does not touch the frozen grader** (rule 2: gates
closed at first compute; rule 6: frozen files are never edited). **P7 is `MISS` and stays
`MISS`.** What is recorded here is the caveat a reader needs in order not to draw the
strong conclusion: **the claim "D18 discriminates SHIPPED from PATCHED" rests on a
`NOT A RESULT` component, and P5 — the other discrimination prediction, which reads only
graded components — MISSED in the non-discriminating direction.** The two predictions do
not agree, and the disagreement is explained by which components each one is allowed to
see. **A defect note is owed against the D18 grader's P7 composition and is referred
upward; it is a successor's repair, never an edit to this item's frozen comparator.**

---

## 8. WHAT IS `NOT MEASURED`, NAMED

Nothing in this list is a failure; each is named so it cannot be read as measured.

1. **`G6` dot-product / duality test** — `NOT MEASURED`, registered as such: the tutorial
   exposes no such test. No duality/transpose consistency is claimed for `DAHisaFoam`.
2. **`G12` `delivered_cores_mean` for the MESH arm** — `NOT_MEASURED` (the arm is 11 s
   long, below the sampler's first tick). Recorded in `not_measured: ["MESH"]`.
3. **`G9` `artefact_so_md5` for the MESH arm** — `null`; that arm writes no JSON artefact.
4. **`shape[3]`, both rows** — `NOT A RESULT`, `NO_PLATEAU`. **Not measured.** §3.
5. **GCI / observed order / discretisation uncertainty** — none exists; one mesh. §6.
6. **Real-gas, chemical, viscous, turbulent and radiative physics** — not modelled at all.
   §0.
7. **Shock position and strength** — no `Cp` and no shock-angle quantity is graded
   (`PREREGISTRATION.md:103`).
8. **Optimisation** — no optimiser runs in this item; nothing is claimed about
   convergence to an optimum.
9. **Axisymmetric behaviour** — the case is planar 2-D, one cell thick, no `wedge` patch
   pair. The `axisym` capability row does not move.

---

## 9. COST — ESTIMATE VERSUS ACTUAL (rule 12)

| | figure | basis |
|---|---|---|
| predicted | **182.2 core-min** (band [60, 450]; ceiling 785.0 = Σ caps) | `PREREGISTRATION.md:63`, frozen `dae3dc9d` |
| actual | **129.016 core-min** | MEASURED, `wall_s × ranks ÷ 60` summed per arm from `<run root>/ledger.txt`; independently carried by the grader at `gates.G10_caps.total_core_min` |
| gross vs cleaned | **gross == cleaned** | no arm exceeds 3600 wall s (longest F-S at 1,918 s), so the stall rule matches no row |
| **ratio** | **0.708** actual/predicted | **29.2 % under** the registered point |
| waste | **0.000 core-min** | named separately per `COMPUTE_BUDGET_CHARTER.md` §6, folded into no ratio: no arm was killed, re-run or discarded; all five arms `rc=0` and all five were graded |
| dollars | **$0.1103 DERIVED** (2.1503 core-h × $0.0513/core-h); predicted $0.1558 | **DERIVED, NOT MEASURED** |
| `cost_basis` | c7a.4xlarge at **$0.0513/core-h**, **REPORTED-BY-OWNER, NOT MEASURED** | the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Gap attribution.** The 53.18 core-min shortfall is **misprediction in the conservative
direction, concentrated in the two F arms**, and it is attributable to a specific
registered assumption that did not hold. `PREREGISTRATION.md:65` priced the F arms at
**82.0 core-min each — above D17's MEASURED 75.733 / 82.000 — on the stated expectation
that "a stiffer shock may need more GMRES work per pseudo-step"**. It did not: F-S came in
at **63.933** (0.780×) and F-P at **51.967** (0.634×), together **98.1 %** of the total
shortfall (48.1 of 53.18 core-min). The X arms were also under (0.759× and 0.678×) and
MESH essentially on point (0.915×). **The Mach-5 primal was CHEAPER per pseudo-step than
the Mach-1.958 one, not dearer** — the step count is fixed at 500 and bounds the wall, and
the extra GMRES work the registration allowed for did not appear.

**Contention: present but small and named.** The ledger's `siblings_pre` / `siblings_post`
fields record that MESH, X-S and F-S each ran alongside `so1a` and `av2r` containers,
while X-P and F-P ran with **no siblings at all** — and the two PATCHED arms are the two
cheapest relative to prediction (0.678× and 0.634× vs 0.759× and 0.780× for their SHIPPED
twins). **So the residual 12–15 % spread between otherwise identical S and P arms is
consistent with peer contention on the SHIPPED half, and the delivered-core means
corroborate it directly**: 1.9867 (X-S) and 1.9880 (F-S) against 1.9910 (X-P) and 1.9966
(F-P) of 2.0. That is a real but second-order effect; **the first-order cause of the ratio
is the F-arm misprediction above.**

**Calibration row:** `docs/COST_CALIBRATION.md`, row **`C-198`**.

---

## 10. CAPABILITY GRID

`docs/capability/dafoam_GRID.md`, cell **`2D · steady · hypersonic`**, gradient column
(*"gradients computed + FD-verified"*), moves from `CAN NOT DO — not attempted` to
**`CAN DO, CAVEATS`**, landed as **Correction 3** at the foot of that file so that no line
above it changes number. The **optimisation column does not move** — D18 runs no
optimiser (`PREREGISTRATION.md:103`). The grader's own cell string, from
`capability_grid_cell`:

> *"2D · steady · hypersonic — gradients computed + FD-verified; this item moves ONLY that
> column"*

**The caveats, which travel with the cell and must not be dropped:** (a) **§0 — the cell
is hypersonic in the Mach number only**; perfect gas, calorically perfect, inviscid, no
chemistry. (b) **Single mesh, no GCI** (§6). (c) **1 of 5 registered components is
`NOT A RESULT`** in both rows (§3). (d) **No dot-product/duality check** anywhere in this
family (§4, G6).

---

## 11. PROVENANCE — EVERY ARTEFACT NAMED

Run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic`

| artefact | what it carries |
|---|---|
| `D18_grade_20260828T032852Z.json` (14,046 B) | the graded verdict, every gate, the FD tables, the controls, the predictions |
| `D18_grade_20260828T032852Z.out` | the same, as the comparator's stdout |
| `ledger.txt` | per-arm `IMG`/`DIGEST`/`rc`/`wall_s`/`ranks`/`core_min`/`cap`/`cpuset`/`delivered_cores_mean`/`siblings`, and `D4S_IDWARP_SO_MD5` per arm; the `G-MACH` record |
| `STATUS.chain`, `CHAIN_DONE` | chain started 2026-08-28T02:18:44Z, `chain=COMPLETE` 03:28:52Z, five arms `rc=0`, `grader_rc=0` |
| `grader_controls/F_S_planted.json`, `grader_controls/F_P_planted.json` | the grader's own plant, re-read from disk |
| `MESH/checkMesh.log` | the cell count G-M2 reads |
| `X-S/d18_X.json`, `X-P/d18_X.json` | adjoint gradients, identity, baselines |
| `F-S/d18_F.json`, `F-P/d18_F.json` | the FD tables and the `CTRL` planted-zero rows |
| `base/constant/thermophysicalProperties`, `base/constant/turbulenceProperties`, `base/0.orig/{U,T,include/freestreamConditions}` | the physics of §0, read directly |
| per-arm `*.log`, `*.inspect.txt`, `*.cpu.jsonl`, `*_h5_window_*.txt` | solver output, the kernel exit/OOM record, the delivered-core sampler, the memory window |

Case directory: `cases/dafoam/curriculum_D18_cone_hypersonic/` —
`PREREGISTRATION.md` (frozen `dae3dc9d`, addendum A `ed4983bd`, pre-compute),
`d18_grade.py` (md5 `e4ade11ed9e3db18d2c4988b30e929b4`, verified disk == HEAD blob),
`d18_chain_driver.sh`, `d18_run_arm.sh`, `d18_xf.py`, `d18_runScript.py`,
`d18_mach_agreement.py`, `d18_control_evidence.txt`,
`d18_groot5_selftest_evidence.txt`, `STATUS.D18_chain`, `launcher.queue.out`.

**Nothing in this item was sent, filed, uploaded, registered or posted. Submissions remain
parked (standing rule 7).**

---

## 12. SUCCESSOR NOTE — 2026-08-28, dafoam lane AA. APPENDED AT THE FOOT, NEVER AN EDIT. **Lines whose number changed above this section: 0.**

**No gate, threshold, band, cap or label moves. Nothing above this line is altered, struck
or renumbered.** The scoring in §7 stands exactly as the frozen comparator recorded it:
**P7 `MISS` at S/N 19.8691.** That is what the instrument produced and it is not re-ruled
here (rule 2: gates closed at first compute; rule 6: frozen files are never edited).

**The defect note §7a referred upward has been discharged** as item **`D18R-P7`**
(`cases/dafoam/curriculum_D18R_P7/`) — a **successor** comparator, frozen by sha at
**`9ef4b5ed`** *before* execution, run against **this item's preserved grade JSON** with
**zero solver compute**.

**Through the repaired composition, P7 re-grades to `HIT` at S/N 0.13831072288719595**
(signal **0.4482626682416995 %** at `shape[1]`; noise **3.2409827588515716 %** at PATCHED
`shape[0]`, unchanged; `shape[3]` **excluded** as `NOT A RESULT` in both rows). The
threshold **1.0 is this item's own**, inherited from `d18_grade.py:108`, not chosen by the
successor. Independently corroborated: `docs/capability/dafoam_GRID.md` Correction 3 row 5
published `0.4482626682416995 %` and `0.1383` from a separate derivation; the successor
returns the same to every published digit.

**Two citations in §7a are wrong, and the disclosure route is this note, not a rewrite of
the body.** §7a cites `d18_grade.py:585-589` for the composition and `:381-384` for the
omission.

* The composition defect is at **`:581-583`**, with the ratio at **`:588`** and the score at
  **`:589`**. `:585-589` **excludes `:581` — the numerator line that IS the defect.**
* `:381-384` brackets the `continue` and **is not called wrong**, but the mechanism is
  sharper than a range: at **`:379-380`** the `NO_PLATEAU` branch sets the verdict and at
  **`:382`** it `continue`s — **before `rel_err_pct` is assigned at `:385`**. So
  *"unreadable"* and *"carries no numeric error"* are **one state** in this producer. **That
  is why the denominator excludes such a component and the numerator does not** — the
  asymmetry is not an oversight in two independent filters, it is one filter applied to one
  half of a ratio and not the other.

`d18_grade.py` md5 `e4ade11ed9e3db18d2c4988b30e929b4` is **unchanged and disk == HEAD blob**,
so these are citation errors in the citing text, not drift in the cited file.

**NOTHING ELSE IN THIS ITEM MOVES, and the successor proves it rather than asserting it.**
`d18_grade.py:596-601` composes the item verdict from six readings — the two row verdicts,
`G-M2`, `G9`, `G10`, `G12` — and `preds` is absent from that expression. The successor
re-evaluates that expression from the preserved JSON's own gate fields and **refuses** if it
disagrees with the recorded verdict; it read back `PASS PASS PASS PASS PASS PASS` and
recomposed **`PASS`**. **Item verdict `PASS`. Both rows `PASS`. Capability-grid census
unchanged at 6 of 36.** The successor buys **nothing** about the physics, the mesh, grid
convergence (no grid family exists; **NO GCI IS QUOTED**), `G6`, complex-step, or the
shipped-versus-patched comparison **as a physical finding** — a corrected S/N ≤ 1 says only
that the two rows are not distinguishable **above the common-mode FD noise on the graded
components**, and says nothing at all about `shape[3]`, which remains unreadable in both.

**Full record:** `cases/dafoam/curriculum_D18R_P7/RESULTS.md`;
pre-registration `cases/dafoam/curriculum_D18R_P7/PREREGISTRATION.md` (frozen `9ef4b5ed`);
cost row `docs/COST_CALIBRATION.md` `C-207`. Nothing was sent, filed, uploaded, registered,
posted or commented outside this box (standing rule 7).
