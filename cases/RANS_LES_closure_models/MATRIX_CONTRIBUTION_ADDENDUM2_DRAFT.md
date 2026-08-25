# DRAFT — NOT COMMITTED

*This file is a DRAFT handed to the closure supervisor. It is not part of any record until
the supervisor reads it personally and lands it. The block below the rule is the text
proposed for appending **at the very foot** of
`cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md`, after the line
`was edited. Owner: closure.` — **L-304: at the foot, never mid-file.** Nothing above that
point is touched. The lane that wrote this committed nothing.*

---

## ADDENDUM 2 — 2026-08-25 — WHY THE `G` COLUMN IS EMPTY. APPENDED AT THE FOOT.

**Appended 2026-08-25T01:06:22Z (box clock, read in the writing invocation) by a closure
lane at the closure supervisor's direction. Version v1.2 → v1.3.
lines whose number changed above this section: 0.**

**Proved, not asserted.** The pre-append prefix is the whole file as it stood — bytes
1–95,240, **1,171 lines** — sha256
`7ea0c2f1adabcee9441f34d670944245b209c111621c37d92ba7002b3044e820`, measured on the
working-tree file and **byte-identical to this file's blob at HEAD `af2b23b0`**, git blob
id `0e697bb96a047819d60c0ad3de5f8f0f0144808d`. Nothing above this line was edited,
renumbered, reflowed or restruck.

**This addendum MOVES NOTHING.** No tier, no verdict, no letter, no census figure. All six
rows keep the tiers §5(k)(1) gave them — four `NOT HELD`, two `SURVEYED` — and `G` stays
`NO` on every row. **This addendum answers a different question: not whether `G` is empty,
which §5(b) settled, but WHY it is empty, row by row.** The distinction it draws changes
no score and is not offered as mitigation.

**The `V` / `G` / `P` definitions used here are the ones quoted at §5(a), and they carry
the same label they carry there and everywhere else in this file: they are the CHIEF'S
RECONSTRUCTION of Sanaa's brief and NOT her verbatim words.** In particular `G` = *"a
CONVERGING Roache triple with GCI and an observed order"*. Nothing below is evidence about
what Sanaa said.

**Zero compute: 0.000 core-minutes, 0.000 GPU-hours.** Documentary and filesystem
inspection only; no solver ran, no run directory was created, no instance was started.
**SUBMISSIONS PARKED** (`CLAUDE.md` rule 7): nothing sent, filed, uploaded, registered,
posted or commented.

---

### A2.1 The finding, stated plainly

**The empty `G` column is a MIX, and the mix is not evenly split. Three of the six rows are
STRUCTURAL, two are a GAP, and one is structural in what it graded with a latent gap in
what it registered and never reached.**

Saying "closure never ran a grid study" is true of Rows 2 and 3 and **misdescribes** Rows
1, 4 and 5. For those three the graded quantity is an **a-priori** one — a model-form
error, a matrix rank, a coverage census — read off a **frozen reference field on the
reference dataset's own grid**. There is no mesh of the lab's to refine, the reference grid
is fixed and is not closure's, and a Roache triple is therefore **not defined** for the
quantity being gated. That is a different fact from "we did not get round to it", and the
record should not blur them.

**The correct summary sentence for the matrix owner is therefore:** *closure has never run
a grid-refinement study (Rows 2, 3, and Row 6's unreached G4), and for the majority of its
rows a grid-refinement study would not produce the quantity those rows gate (Rows 1, 4, 5).*

---

### A2.2 The per-row split

| row | what the row actually grades | **GAP or STRUCTURAL** | one-sentence reason, with artefact and line |
|---|---|---|---|
| **1** a-priori model fit | per-family and pooled **`b_rms`**, the RMS error of a predicted anisotropy tensor against the reference `b`, evaluated cellwise on the reference dataset's own grid; no PDE is solved to produce it | **STRUCTURAL** | The registered bar is an a-priori fit error on a frozen field — `R4_sparta_build/PREREGISTRATION.md:169–173` registers *"PASS requires the discovered model below train-mean `b_rms` on >= 3 of the 4 training families"* — so there is no lab mesh in the quantity and no triple is defined for it. |
| **2** a-posteriori propagation | **`U_rms`** of a converged RANS velocity field, and solver **continuity** | **GAP** | Both are discretisation-dependent solve outputs — `Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:192–193` (`TRUTH` must cut `U_rms` on T1 by ≥ 30 % against the SST gate 0.1985) and `:266` (*"GATE FAIL on H5 for any configuration exceeding 1e-3"*) — the meshes exist, the solve could be run at three levels, and it was not; the row's own frozen file admits it at `:313–315`. |
| **3** frozen-field ceiling | **`eps(U)_CEILING / eps(U)_NULL`** from a RANS solve with static injected `bijDelta` / `kDeficit`, plus continuity | **GAP**, with one named constraint | `R4_sparta_build/PREREGISTRATION.md:180–183` registers `eps(U)/eps(U_0) <= 0.6` and continuity `<= 1e-4`, and `:195–197` registers the `NOT A RESULT` branch on the ceiling failing to beat NULL by 30 % — all solve outputs on a mesh, so a triple is applicable and simply absent. **The constraint:** the injected fields are extracted from the truth on the reference grid, so a refined run would have to interpolate them, and the triple would then grade the discretisation of an interpolated source rather than convergence to a mesh-independent truth. That is a design question, **not** a reason the triple is undefined. |
| **4** FS2 degeneracy | **feature-matrix rank per family**, the count of algebraically-zero features, the condition number, and the **per-cell tensor-basis rank** | **STRUCTURAL** | These are algebraic properties of the field, not field values — `_common/features/FS2_DEGENERACY_REPORT.md` §1 (line 9), §2 (line 22), §4 (line 66) — and the rank collapse the report attributes to *"a statistically two-dimensional mean flow"* is bounded by the tensor algebra: refining the mesh adds **rows** to the feature matrix and cannot raise its rank, so no triple can classify it. |
| **5** FS5 extrapolation coverage | the **fraction of TEST cells whose feature values fall outside the pooled TRAINING range**, plus the A1 planted-value read-back | **STRUCTURAL** | `FS2_DEGENERACY_REPORT.md` §6 (line 124) and the repair gates at `_common/features/FS5_D476_CLIP_REPAIR_PREREGISTRATION.md:68` (A1), `:73` (A2), `:76` (A3), `:79` (A4) grade a set-membership census over a **fixed** reference dataset partition; the quantity has no continuum limit under `h → 0`, and the grid it lives on is the benchmark's, not the lab's. |
| **6** GPU training | **pooled test `b_rms`** (G1, G2) and the **realisability violation fraction / `max ‖b‖_F`** (G3) — every gate that was read is a-priori | **STRUCTURAL for what was graded; LATENT GAP for one registered limb** | `Ling2016_TBNN/gpu/PREREGISTRATION.md:269` and `:275` label G1 and G2 *a-priori*, and G3 is a cellwise realisability census on the reference grid — none of them meshed. **But `:296` registers `"G4 — a-posteriori, and it runs on CPU"`, which never ran because G3 fired**; had it run, it would have produced a mesh-convergent quantity and the absence there would be a gap of exactly the Row-2 kind. |

**Count: 3 STRUCTURAL (Rows 1, 4, 5), 2 GAP (Rows 2, 3), 1 MIXED (Row 6).**

**Ruling 7 of Addendum 1 is not disturbed and is extended.** That ruling already held that
`G`'s inapplicability to Rows 4 and 5 *changes no letter*, and that inventing an exemption
would be the same failure in the other direction. This addendum keeps `G = NO` on all six
rows for exactly that reason. What it adds is that **the same structural argument reaches
Rows 1 and 6**, which Ruling 7 did not cover, and that Rows 2 and 3 — where `G` is squarely
applicable — are the only two rows where "never ran it" is the whole of the story.

---

### A2.3 The decisive positive measurement: 266 meshes, and no flow at two cell counts

The documentary null in §5(b) is a search for words. This is a measurement of the meshes
themselves, and it is the stronger statement.

**Every `constant/polyMesh` directory** under `cases/RANS_LES_closure_models/`,
`/home/ubuntu/closure-data/` and `/home/ubuntu/closure-challenge-benchmark/` was located
and its `nCells` read from the `note` header of `owner` (falling back to `neighbour`, then
`faces`). **266 mesh directories, 0 unreadable, 11 distinct cell counts:**

| nCells | the flow it is |
|---|---|
| 2,209 | `AR_1_Ret_180` duct |
| 3,025 | `AR_1_Ret_360` duct |
| 6,627 | `AR_3_Ret_180` duct |
| 8,748 | `AR_3_Ret_360` duct |
| 11,045 | `AR_5_Ret_180` duct |
| 15,463 | `AR_7_Ret_180` duct |
| **15,600** | **every periodic-hill case** — all 29 `Parm_PH_29` parametric hills, `PHLL10595`, `PH_Breuer`, the `w2_legacy` hill, the five `ktest*` cases, the Kaandorp eigenspace envelope cases |
| 21,000 | `CBFS13700` (and the benchmark `CBFS`, and the `w2_legacy` `cbfs`) |
| 22,090 | `AR_10_Ret_180` duct |
| 31,819 | `AR_14_Ret_180` duct |
| 51,626 | `NASA_2DWMH` hump (and all three `hump_gate` configurations) |

**The map from flow to cell count is single-valued for every flow on the box. Not one flow
in closure territory exists at two cell counts, let alone three.** A Roache triple requires
one flow at three levels; the data on disk cannot supply even a **pair**. **That is why the
gap in Rows 2 and 3 could not have been closed by re-running what is already here** — it
would require generating meshes that do not exist.

**The instrument is demonstrated able to see a difference.** The same reader resolved
eleven distinct cell counts spanning 2,209 to 51,626 across the same 266 directories; a
reader that could not distinguish cell counts would have returned one value, and it did
not.

**Corroboration from the mesh dictionaries.** **85** `blockMeshDict` files exist across
closure territory and the out-of-repo data — and **all 85 carry the identical block
signature** `(40 25 30) simpleGrading; (120 65 1) simpleGrading; (120 65 1) simpleGrading`.
**One resolution is defined anywhere; no refined variant exists even as an unrun
dictionary.** Zero `snappyHexMeshDict`, zero `refineMeshDict`. *(Fired control, identical
apparatus and corpora: `-name 'controlDict*'` returns **226** files.)*

---

### A2.4 SEPARATE FINDING — the reference-data grid is never varied either

Asked as its own question, because a family with no mesh of its own could still have varied
the **reference** grid — a coarsened DNS, a subsampled field — and thereby have had a
convergence axis of a different kind. **It has not.**

Over `/home/ubuntu/closure-data/` and `/home/ubuntu/closure-challenge-benchmark/`
(**21,846 files**, binaries skipped), the pattern
`coarsen|coarsened|subsampl|sub-sampl|downsampl|down-sampl|decimat|every.other|thinned|resampl`
returns **0 line-hits**. *(Fired control, identical apparatus and corpus: `interpolat`
returns **1,481** line-hits.)*

The same pattern over closure's repo territory returns **34** line-hits, every one triaged,
and **none is a spatial coarsening of closure's own reference data**:

* **other people's papers, catalogued** — `docs/closure/PAPER_CATALOGUE.md` at lines 1078
  (*"one coarsening ratio"*), 1504, 1554, 1563, 1606, 1670, 1671, and
  `docs/closure/CLOSURE_METHOD_CLASSES_INVENTORY.md:566`, `:579`;
* **statistical, not spatial** — random-forest bootstrap/feature subsampling
  (`Wu2018_PIML_RF/PREREGISTRATION.md:101`) and EnKF observation-noise resampling
  (`Xiao2016_EnKF/PREREGISTRATION.md:36`, `:81`);
* **a seeded subsample for a rank census, explicitly not a grid** —
  `R4_sparta_build/assemble_dataset.py:128`, and its companion record states the opposite
  choice for the coverage figures: *"Full cell count, no subsample."*
  (`R4_sparta_build/COVERAGE.md:232`);
* **the phrase "every other"** in ordinary English, e.g. `R5C_omega_repair/RESULTS.md:110`.

**And closure has already said so, against its own favour, in a landed record.**
`Xiao2016_EnKF/RESULTS.md:160–162`: *"It cannot separate Reynolds number from mesh. Both
differ from the paper (3.78x and 2.0x in `Re`; 10.4x in cells) and only `Re` was varied. A
mesh-coarsening test at fixed `Re` is the obvious next falsifier and was not run."*

---

### A2.5 Every refinement-family candidate checked, with its cell count

Checked, not assumed. **No genuine grid family was found anywhere.** Every candidate and
its measured cell count, including the ones that turned out not to be grid families:

| candidate family | measured `nCells` | verdict |
|---|---|---|
| `alpha_XX_NNNN_{2024, 3036, 4048}` — all 27 R5C targets and all 29 `Parm_PH_29` hills, in the benchmark **and** in `closure-data/r4/frozen/` **and** in `closure-data/r5c/frozen/` | **15,600 on every one** | **NOT a grid family.** The suffix is the benchmark's PHLL29 parametric label. **This independently re-confirms the previous session's check and extends it**: that check covered only `alpha_10_9000_{2024,3036,4048}`; this one covers all nine `alpha`/`Re` groups and all three copies of each. |
| `alpha_075`, `alpha_125` | 15,600 each | NOT grid levels — parameter values. |
| `AR_1 / AR_3 / AR_5 / AR_7 / AR_10 / AR_14 _Ret_180` ducts | 2,209 / 6,627 / 11,045 / 15,463 / 22,090 / 31,819 | **NOT a grid family.** The count scales with the aspect ratio at fixed resolution — `2,209 = 47²`, and `6,627 = 3 × 2,209`, `11,045 = 5 × 2,209`, `22,090 = 10 × 2,209`. Same cell size, wider domain, different geometry. |
| `AR_1_Ret_180` vs `AR_1_Ret_360`; `AR_3_Ret_180` vs `AR_3_Ret_360` | 2,209 vs 3,025; 6,627 vs 8,748 | **NOT a grid family**, and this is the nearest miss on the box: same geometry, two cell counts — but a **different Reynolds number**, so a different flow, and two levels are not three. It is the confound `Xiao2016_EnKF/RESULTS.md:161` already names. |
| `closure-data/r4/{ktest, ktest2, ktest3, ktestA, ktestB}` | 15,600 each | NOT a grid family — `k`-transport tests on one mesh. |
| `AR_1_Ret_360__MEANB` vs `AR_1_Ret_360__MEANB64` | 3,025 vs 3,025 | Same mesh; the suffix is not a resolution. |
| `NASA_2DWMH`, `hump_gate/{G0a_shipped, G0a_corrected, G0b_null}` | 51,626 each | One mesh, three solver configurations. |
| `CBFS13700`, benchmark `CBFS`, `r5c/w2_legacy/cbfs` | 21,000 each | One mesh under three names. |
| `PHLL10595`, `PH_Breuer`, `r5c/w2_legacy/ph` | 15,600 each | One mesh under three names. |
| `alpha_10_9000_3036__EIG_{1C_vmax, 1C_vmin, 2C_vmax, 2C_vmin, 3C}` | 15,600 each | Eigenspace-envelope perturbations on one mesh. |
| `aposteriori/kaandorp/smoke` | 3,025 | The `AR_1_Ret_360` mesh, reused as a smoke case. |

---

### A2.6 Every null, with the non-zero its own apparatus returned

Rule 3's discipline applied to a documentary search: **a zero from a reader not shown able
to see a non-zero is not evidence.** Every null below was produced by
`find … -print0 | xargs -0 /bin/grep`, on explicit absolute paths, reading the **disk**.
This is not the shell's `grep`: on this box `grep` is a function wrapping `ugrep
--ignore-files`, which is blind to gitignored archives; `/bin/grep` (GNU grep 3.11) honours
no ignore file. Controls were run on the **identical apparatus over the identical corpus**.

| # | corpus | pattern | result | **fired control** |
|---|---|---|---|---|
| **N1** | repo closure territory — `cases/RANS_LES_closure_models/` + `docs/closure/`, **191 files on disk** | `[Rr]oache\|\bGCI\b\|gci_\|grid.?converg\|grid.?refine\|mesh.?refine\|observed order\|order of accuracy\|apparent order\|refinement ratio\|h-refinement\|mesh triple\|[Rr]ichardson\|p_obs\|CONVERGING\|OSCILLATORY\|STAGNANT\|roache_triple` | **no triple, no GCI, no observed order.** All hits triaged in A2.7 | `PREREGISTRATION` → **222 line-hits**; `bijDelta` → **208 line-hits** |
| **N2** | out-of-repo data — `/home/ubuntu/closure-data/` + `/home/ubuntu/closure-challenge-benchmark/`, **21,846 files**, binaries skipped | same pattern as N1 | **0 line-hits** | `nCells` → **585 files**; `kDeficit` → **1,662 files** |
| **N3** | same corpus as N2 | `coarsen\|subsampl\|downsampl\|decimat\|every.other\|thinned\|resampl` | **0 line-hits** | `interpolat` → **1,481 line-hits** |
| **N4** | repo closure territory, 191 files | closure code invoking a mesher: `blockMesh\|snappyHexMesh\|refineMesh\|extrudeMesh` | **exactly one file**, `R4_sparta_build/RESULTS.md:57`, and that line reads *"`snappyHexMesh`/`simpleFoam` logs dated 2026-08-16 — an earlier, unrelated"* run. **No closure script generates a mesh.** | `simpleFoam` → **24 files** |
| **N5** | repo closure territory + out-of-repo data | `-name 'snappyHexMeshDict*' -o -name 'refineMeshDict*'` | **0 files**; the 85 `blockMeshDict` files all carry one identical block signature (A2.3) | `-name 'controlDict*'` → **226 files** |
| **N6** | 266 `constant/polyMesh` directories | any flow present at two cell counts | **NONE** (A2.3) | the same reader resolved **11 distinct** cell counts, 2,209 to 51,626 |

---

### A2.7 The N1 hits, triaged, including a false-positive class worth keeping

Every N1 hit falls into one of five classes; **none is a grid triple, a GCI or an observed
order computed by closure.**

1. **`app-roache-s`.** The substring `roache` occurs inside the English word *approaches*.
   Six hits are this — `NASA_hump_gate/RESULTS.md:126`,
   `Xiao2016_EnKF/RESULTS.md:149`, `Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:306`,
   `Kaandorp2020_TBRF/aposteriori/RESULTS.md:266` and `:840`,
   `Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md:186`,
   `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md:414` — every one a cost sentence saying a cap
   was *never approached*. **§5(b) recorded five; the wider pattern used here surfaces
   more, and the class is the same.**
2. **Closure's own written admissions, in frozen and landed files.** These are the family
   telling the truth in advance, and they are the direct answer to the chief's question for
   Rows 2 and 3 — quoted in full in A2.8.
3. **Other people's papers, catalogued.** `docs/closure/PAPER_CATALOGUE.md` (Spalart's
   supersonic flat-plate study, `:1278`; DES moving 26 % under refinement, `:286`;
   *"no amount of grid refinement will override the influence of the empirical content of
   the turbulence model"*, `:301`; Lozano-Durán's non-monotonic convergence, `:1406`),
   `CLOSURE_METHOD_CLASSES_INVENTORY.md:1057–1058`, `FOUNDATIONAL_MODELS_INVENTORY.md:1605`,
   `_common/FEASIBILITY.md:108`. **Closure catalogued the requirement and never met it.**
4. **A citation of `CLAUDE.md` rule 5 as a direction argument** —
   `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md:605` and `:786`, on a non-`CONVERGING` triple
   as an analogy. No mesh, no triple, no refinement in that file.
5. **This file itself**, `MATRIX_CONTRIBUTION.md`, discussing the null in §5(b).

---

### A2.8 Closure's own admissions, quoted at HEAD with HEAD line numbers

Three landed files say it themselves. The first is the one §5(b) and §5(k)(1) cite, and its
exact extent at HEAD is **lines 313–315**, not the single line 314 those sections cite —
the sentence spans three lines of a wrapped bullet. `cases/RANS_LES_closure_models/
Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md`, 334 lines, git blob
`411b25f1d452330558824a52885a2950ceffa54f`, sha256
`3298d8bb4d1fd3b45636d0b098f4f2dd6d428d1389e6a1e2ba2fed8e93a5d744`, under the heading
`## 8. What this test CANNOT see` at line 311:

> ```
> 313  * **One Reynolds number per case.** Two ducts and one step; no `Re` sweep, no
> 314    mesh-refinement study. A converged answer on one mesh is not a grid-converged
> 315    answer.
> ```

*(Lines 314 and 315 carry a two-space continuation indent in the file.)* **Nothing in
§5(b) or §5(k)(1) is wrong — line 314 does carry the operative phrase — and this is
recorded only so a future citation resolves to the whole sentence.**

The same admission appears twice more, in the landed results and in the sibling lane:

* `Kaandorp2020_TBRF/aposteriori/RESULTS.md:281` — *"**One Reynolds number per case, one
  mesh, no grid-refinement study.**"*, repeated at `:892` in the closing list of standing
  limitations.
* `Xiao2016_EnKF/PREREGISTRATION.md:286–287` — *"A single case at a single Reynolds number,
  on one mesh, with no grid-refinement study."*

---

### A2.9 What this addendum did NOT do

**No tier moved. No verdict moved. No letter moved.** §5(k)(1) still governs: Rows 1, 2, 3
and 6 at `NOT HELD`, Rows 4 and 5 at `SURVEYED`, `G = NO` on all six. **No `NOT APPLICABLE`
was invented** for the structural rows — Ruling 7 forbade exactly that, and this addendum
obeys it: the honest record is that the evidence is absent, and the reason it is absent is
now stated. **No frozen file was edited.** No pre-registration, gate, threshold, cap or
label was altered anywhere. `docs/COVERAGE_MATRIX.md` remains untouched by closure, and
these rows remain closure's **offer**, which the owner re-maps, renames, merges or rejects
without asking.

**What this addendum cannot see.** It searched **text**; binary artefacts (`.npz`, `.pt`,
`.pkl`, `.db`) were not text-searched, so a triple hidden in a binary with no accompanying
record would not have been found — and under rule 2 would not be a result. The cell-count
census (A2.3) reads only `constant/polyMesh` directories that exist on this box now; a mesh
generated, used and deleted would leave no trace in it. Neither residue can move a letter.

**End of Addendum 2.**
