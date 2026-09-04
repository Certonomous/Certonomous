# T5d — the coarse build STOPPED at its own registered `checkMesh` bar, and the triage found the failure is INHERITED FROM T5: findings record

**Rung `T5d`. Family: T. Team: heat-transfer. Dated 2026-09-04.**
**Status of the rung: `BLOCKED`.** The named blocker is in §8.

> **THIS RECORD CONTAINS NO AMENDMENT, NO PROPOSED AMENDMENT AND NO
> RECOMMENDATION THAT ANY BAR MOVE.** `T5d_PREREGISTRATION.md` is untouched by
> it. The registered stop condition in that document's §6 fired, the build
> stopped at it, and this record exists to carry the measurement and the two
> questions it raised to the teams that own them. The lane that hit the bar did
> not draft its own unblocker and the supervisor declined to draft one for it;
> the ruling recorded at §7 is that *the fact that the condition predates T5d
> does not un-fire it.*

**This record TRANSCRIBES measurements. It grades nothing.** Every figure below
is taken from an artifact named beside it, all of them on disk at the time of
writing. **No T5, T5b or T5c result is re-graded, re-opened or disturbed here**,
and no `checkMesh` was re-run into any T5 or T5b case directory — the comparison
logs were written to T5d's own directory.

---

## 1. THE STOP, AND ITS EXACT TEXT

`build_t5d.py --case T5_CUBE_c` returned `rc = 0` and built the mesh. The
builder's own quality check — `checkMesh -allRegions -allTopology -allGeometry`,
run by the frozen `build_t5.py` — then reported, on the **air** region:

```
 ***Cells with small determinant (< 0.001) found, number of cells: 7658
<...>
Failed 1 mesh checks.
```

The **epoxy** region reported `Mesh OK`.

`T5d_PREREGISTRATION.md` §6 registers, in its named-risks list:

> *"if `checkMesh` on the built coarse mesh reports anything other than
> `Mesh OK`, that is a **finding**, the build stops, and it goes to the
> supervisor — it is not worked around."*

**It stopped.** Verified on disk at the time of writing:

| condition | state |
|---|---|
| `T5_CUBE_c/0/` | **does not exist** |
| numeric time directories in `T5_CUBE_c/` | **none** |
| `STATUS.T5_CUBE_c` | **does not exist** — nothing ran |
| `T5_CUBE_c/log.solve` | **does not exist** — no solver started |
| `T5_CUBE_c/0.orig/` | present; the case is built and **unarmed** |

**Artifact:** `verification/runs/T-family/T5d_runs/T5_CUBE_c/log.checkMesh`

---

## 2. THE MESH ITSELF IS CORRECT — the repair landed, and a second instrument agrees

The stop is not a failure of the mesh repair. The repair is measured and it
holds.

**First-cell height, measured from the BUILT mesh's own
`constant/air/polyMesh/points`** by the builder's post-build guard, which refuses
unless every graded wall is within `1e-3` relative of the registered value:

| wall | measured | registered |
|---|---:|---:|
| `cube_front` | 7.999998e-05 m | 8.000000e-05 m |
| `cube_rear` | 8.000012e-05 m | 8.000000e-05 m |
| `cube_side_n` | 7.999996e-05 m | 8.000000e-05 m |
| `cube_top` | 8.000001e-05 m | 8.000000e-05 m |
| `floor` | 8.000000e-05 m | 8.000000e-05 m |
| `roof` | 7.999996e-05 m | 8.000000e-05 m |

**Cell counts unchanged, as the registration requires:** **52,684** air +
**869** epoxy — identical to T5b, so the frozen comparator's `CELLS_REGISTERED`
refusal still passes and the measured refinement ratios `r21 = 1.6060` /
`r32 = 1.5929` are undisturbed.

**Function objects:** 2 repaired blocks present, **0** surviving `writeTime`
controls.

### 2.1 THE CORROBORATION — a second instrument, not designed for this

| quantity | T5b coarse | T5d coarse | ratio |
|---|---:|---:|---:|
| minimum cell volume | 2.097146788e-12 m³ | 5.119993728e-13 m³ | **0.244141** |

**`0.625³ = 0.244141`.** Exact to six significant figures.

The minimum-volume cell is a corner cell that carries the first wall layer in
**x, y and z simultaneously**, and it shrank by exactly the **cube** of the
registered scale. This check was not designed to test the repair — it is a line
`checkMesh` prints anyway — and it confirms the first-layer change landed in all
three directions **independently of the points reader** that the builder's guard
uses. Two instruments agreeing is worth more than either alone.

---

## 3. THE TRIAGE — the SAME check flags on all three meshes

The failing check was run against the older meshes with the **identical**
invocation (`checkMesh -allRegions -allTopology -allGeometry`), so the
comparison is like for like and not an inference.

| mesh | max aspect ratio (air) | small-determinant cells | air-region verdict |
|---|---:|---:|---|
| **T5 coarse** | 133.2314384 | **4,406** | `Failed 1 mesh checks` |
| **T5b coarse** | 133.2314384 | **4,406** | `Failed 1 mesh checks` |
| **T5d coarse** | 233.5224778 | **7,658** | `Failed 1 mesh checks` |

**T5's and T5b's figures are byte-identical to each other** — same aspect ratio
to ten figures, same cell count, same minimum volume. **This check has been
failing on the T5-family coarse mesh since T5**, on the meshes that produced
every graded T5 and T5b run.

**T5d does not introduce the failure. T5d makes it worse:** 4,406 → 7,658 cells,
a factor of **1.738**, or **8.36 % → 14.54 %** of the 52,684-cell air mesh. On a
rung whose graded quantities are wall heat transfer, that worsening is recorded
rather than dismissed.

**Artifacts:**
`verification/runs/T-family/T5d_runs/CHECKMESH_TRIAGE_2026-09-04/checkMesh_T5_coarse_STRICT.txt`
`verification/runs/T-family/T5d_runs/CHECKMESH_TRIAGE_2026-09-04/checkMesh_T5b_coarse_STRICT.txt`

**The other registered mesh gates all pass on the T5d mesh**
(`docs/standards/MESH_STANDARD.md` §3.1–§3.4): non-orthogonality check OK;
max skewness `4.180131424e-13` against a gate of 4; max aspect ratio `233.52`
against an **advisory** 1,000; face areas, cell volumes and cell openness
(`1.636908269e-16`) all OK. The determinant test is **not** one of those four
registered gates. **That is stated as a fact about the standard, not as an
argument for anything.**

---

## 4. THE LARGER FINDING — the builder checks strictly, the LAUNCHER checks weakly, and only the WEAK result reaches `STATUS`

`run_one_t5b.sh:179` (and therefore `run_one_t5d.sh`, which is that file with
three mechanical substitutions) runs:

```
checkMesh -case "$CASE_DIR" -allRegions
```

**without `-allTopology -allGeometry`.** That invocation **does not run the cell
determinant test at all.** Measured, both invocations, both meshes:

| mesh | `-allRegions` only (**what the launcher runs, and what reaches `STATUS`**) | `-allRegions -allTopology -allGeometry` (**what the builder runs**) |
|---|---|---|
| **T5b coarse** | `Mesh OK` on both regions | `Failed 1 mesh checks` on air (4,406 cells) |
| **T5d coarse** | `Mesh OK` on both regions | `Failed 1 mesh checks` on air (7,658 cells) |

**Artifacts:**
`.../CHECKMESH_TRIAGE_2026-09-04/checkMesh_T5b_coarse_LAUNCHER_FLAGS.txt`
`.../CHECKMESH_TRIAGE_2026-09-04/checkMesh_T5d_coarse_LAUNCHER_FLAGS.txt`

**The consequence, stated plainly.** `STATUS.T5_CUBE_c`'s `checkMesh_rc=0` and
the `Mesh OK` sitting in T5b's case directory were written by a **weaker check
than the one the same family's builder runs**. A reader taking `checkMesh_rc=0`
for "this mesh passed checkMesh" is taking it for more than it says. **The
absence of an error is being read as the presence of a check** — and the
stricter check that would have produced the error was never invoked on the path
whose result gets recorded.

**SCOPE, AND IT IS DELIBERATELY NARROW.** This is reported **as measured on the
T5, T5b and T5d coarse meshes and nowhere else.** No sweep of other families'
launchers was performed by this lane or by its supervisor. **No claim is made
that any other launcher is clean, and none that any other is affected.**

---

## 5. A HYPOTHESIS, ATTRIBUTED, AND EXPLICITLY UNPROVEN

The following reading is **the heat-transfer supervisor's**, recorded here at
their direction as a hypothesis for whoever owns the standard to rule on. **It is
unproven, it is not relied on by this record, and nothing in this rung acts on
it.**

> On a Cartesian lattice with skewness `4.18e-13`, cell openness `1.6e-16` and
> non-orthogonality passing, `checkMesh`'s cell-determinant test may be largely a
> **restatement of anisotropy** rather than an independent defect, in which case
> an aspect ratio of 233 would explain the 7,658 cells without anything being
> wrong with the mesh.

**Why it is recorded as a hypothesis and not acted on.** The supervisor's stated
reason, adopted here: *a red with an innocent explanation is the easiest failure
to wave through, and one never writes "green" from an inference.* If the reading
is correct it should be established **by whoever owns the standard, in the
standard, on the record** — not adopted by the team that would benefit from it,
in order to unblock itself. It is therefore put upward labelled as unproven.

---

## 6. ONE PREDICTION MISS, RECORDED AS A MISS

`T5d_PREREGISTRATION.md` §3.4 and §11 predicted the near-wall cell aspect ratio
would rise by **≈ 1.6 ×**, to **≈ 213–225**.

| quantity | predicted | **measured** |
|---|---:|---:|
| T5d coarse max aspect ratio (air) | 213 – 225 | **233.5224778** |
| rise against T5b's 133.2314384 | ~1.6 × | **1.7528 ×** |

**The measurement is outside the registered band. The prediction is recorded as
WRONG, not as close enough.** The band was registered before the mesh was built
and it did not contain the answer.

**The consequence, which is not cosmetic.** The registered **15 % near-wall
stiffening allowance** on the cost POINT (`T5d_PREREGISTRATION.md` §11,
`T5D_CAPS.txt`) was reasoned from an assumed ≈ 1.6 × anisotropy rise. The actual
rise is larger. **That allowance remains unmeasured — the coarse solve that would
have tested it did not run — and the fine level's 399.7 core-min POINT rests on
it.** Re-derivation of the `m` and `f` costs is owed before either is armed.

---

## 7. THE RULING UNDER WHICH THIS RECORD EXISTS

Ruled by the heat-transfer supervisor 2026-09-04 `[lab-attributed]`, recorded
here verbatim in substance:

- **No amendment to `T5d_PREREGISTRATION.md` §6, by the supervisor or the lane.**
  Amending the bar that stopped a build, in order to let that build proceed, is
  the shape Sanaa forbade — *gates are never widened to fit* (session record
  `etc/sessions/2026-09-04T0050Z_sanaa_all_cases_mandatory.md`).
- It is noted that such an amendment **would be lawful** under `CLAUDE.md`
  rule 2's before-first-compute limb — T5d has had zero compute and the condition
  is checkable and was checked (§1). **Lawful and right come apart here**, and the
  ruling is that being lawful does not make it right.
- **The adopted formulation:** *the fact that the condition predates T5d does not
  un-fire it.*
- The lane declined to draft the amendment that would unblock its own build; the
  supervisor declined to draft it on the lane's behalf.

---

## 8. `BLOCKED` — and the blocker is NAMED

**T5d is `BLOCKED`.** Under Sanaa's standing order of 2026-09-04 that is a
**waypoint with an owner, not a resting place**, and the owner is the chief's
routing. The missing thing is named:

> **A ruling on whether `checkMesh`'s cell-determinant test gates a lab mesh** —
> and, if it does, what the threshold and the invocation are.

**Two questions are routed, and neither is heat-transfer's to answer**, because
the entanglement at §3 reaches outside this team's territory: **T5 coarse and
T5b coarse fail this check identically**, so a ruling either way reaches the
meshes under already-graded results of other rungs.

| # | question | owner |
|---|---|---|
| **Q1** | Does the cell-determinant test gate a lab mesh, and at what threshold and invocation? `docs/standards/MESH_STANDARD.md` §3.1–§3.4 registers four gates and this is not among them. | **cfd** (owns `MESH_STANDARD.md`) |
| **Q2** | The §4 asymmetry: the launcher's `checkMesh -allRegions` never runs the test, the builder's `-allTopology -allGeometry` does, and **only the launcher's result reaches `STATUS`**. Is that a fail-open, and how far does it extend? **Not swept beyond T5/T5b/T5d.** | **verification** |

**Nothing is asked for here and nothing is proposed.** The heat-transfer team
holds T5d at `BLOCKED` until a ruling exists.

---

## 9. RULE 12 — WHAT THIS COST, MEASURED

**No solver started, so the registered POINT is UNTESTED.** A calibration row is
**not** filed for `T5_CUBE_c` in `docs/COST_CALIBRATION.md`, because there is no
completion to calibrate: an actual/predicted ratio computed against a run that
did not happen would be a fabricated 0.000, not a measurement.

| figure | value | basis |
|---|---:|---|
| registered POINT, `T5_CUBE_c` | 19.3 core-min | `T5d_PREREGISTRATION.md` §11, frozen |
| registered CAP, `T5_CUBE_c` | 38.6 core-min | `T5D_CAPS.txt`, frozen |
| **SOLVER core-min spent** | **0.000** | no `log.solve`, no `STATUS` |
| build: dictionaries + `blockMesh` + `topoSet` + `splitMeshRegions` + strict `checkMesh` | **2.970 s** = **0.0495 core-min** | mtime span `system/blockMeshDict` 02:03:58.020Z → `CASE.txt` 02:04:00.990Z, 1 rank |
| triage: 4 × `checkMesh` on 52,684 cells | **2.392 s** = **0.0399 core-min** | measured per-run deltas 0.687 s and 0.509 s, ×2 each |
| **TOTAL non-solver spend against T5d** | **5.362 s = 0.0894 core-min** | 1 rank |

**USD 0.0000764 derived at $0.0513/core-h — derived, NOT measured**: this box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Honesty about the measurement itself:** `blockMesh`, `topoSet`,
`splitMeshRegions` and `checkMesh` write an `End` line but **no `ExecutionTime`
line**, so these figures are **wall-clock at 1 rank reconstructed from artifact
mtimes**, not CPU time read from a solver log. They are stated as such. The two
per-run `checkMesh` deltas (0.687 s, 0.509 s) are directly measured; the other
two runs are bounded by them rather than separately timed.

**Whether 0.0894 core-min spent producing no graded value is charter-§6 waste is
NOT decided here.** It produced the §3 triage and the §4 finding, which is not
nothing; the same question is already open at `docs/COST_CALIBRATION.md` row
`C-209` for T5b, and this record neither answers it nor absorbs it into a ratio.
It is named and left named.

---

## 10. WHAT THIS RECORD DOES NOT DO

- **It does not amend, propose amending, or recommend moving any bar, gate,
  threshold, target, tolerance or label.** `T5d_PREREGISTRATION.md` is unedited
  (rule 6).
- **It does not re-grade or re-open T5, T5b or T5c.** T5b's `0 of 6 NOT A RESULT`
  stands. No comparator was run to write this.
- **It does not touch T5's or T5b's directories.** The comparison `checkMesh`
  runs wrote to T5d's own directory; `log.checkMesh` inside `T5_runs/T5_CUBE_c`
  and `T5b_runs/T5_CUBE_c` are unmodified.
- **It does not claim the §4 asymmetry extends beyond T5, T5b and T5d.** No sweep
  was done.
- **It does not adopt the §5 hypothesis**, which is the supervisor's and is
  unproven.
- **It builds and launches nothing further.** `T5_CUBE_m` and `T5_CUBE_f` are not
  built and not armed.
- **Nothing here was sent, filed, uploaded, registered, posted or commented
  outside this box** (`CLAUDE.md` rule 7).

---

**Artifacts this record cites, all on disk at the time of writing:**
`verification/runs/T-family/T5d_runs/T5_CUBE_c/log.checkMesh`;
`verification/runs/T-family/T5d_runs/CHECKMESH_TRIAGE_2026-09-04/checkMesh_T5_coarse_STRICT.txt`;
`.../checkMesh_T5b_coarse_STRICT.txt`;
`.../checkMesh_T5b_coarse_LAUNCHER_FLAGS.txt`;
`.../checkMesh_T5d_coarse_LAUNCHER_FLAGS.txt`;
`verification/runs/T-family/T5d_runs/build_T5_CUBE_c.out`;
`docs/campaigns/T-family/T5d_PREREGISTRATION.md`;
`docs/standards/MESH_STANDARD.md`;
`docs/COST_CALIBRATION.md` row `C-209`.
