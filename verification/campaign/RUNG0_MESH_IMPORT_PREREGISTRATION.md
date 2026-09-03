# RUNG 0 pre-registration — committee-grid mesh-import lane, UGRID

**Team: cfd. v1.0, written 2026-09-03.**

> ## ⚠ DRAFT — **NOT FROZEN**. THE FREEZE IS THE cfd SUPERVISOR'S ACT, NOT THIS LANE'S.
>
> Under `SUPERVISION_CHARTER.md` §3 the *"pre-registration committed before compute"* check is one of
> the four the supervisor performs **personally and may never delegate**. This file is drafted by a
> lane and carries **no freeze**. **NO COMPUTE MAY BE LAUNCHED AGAINST IT** until the supervisor
> commits it as frozen and records the freezing commit sha at the head of this section. Nothing in
> this document is an authorisation.
>
> **Clock discrepancy, recorded rather than smoothed:** `date -u` on this box read
> **2026-09-03T16:10:34Z** while this file was being drafted. The governing directive capture is
> filed as `2026-09-03T1730Z_...`, i.e. **~80 minutes in the future of this box's clock**. The
> capture's *content* is Sanaa's and is not in doubt; its *stamp* disagrees with the box and is
> recorded here as measured, never reconciled by assumption.

**Authority.** Sanaa's standing order of 2026-09-03 ~00:30Z
(`etc/sessions/2026-09-03T0030Z_sanaa_industrial_benchmark_ladder.md`) and her rulings of
2026-09-03 ~17:30Z (`etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md`).
**The later capture governs where the two differ, and it differs in three places** — the gate
wording, Plot3D, and CGNS. Both are quoted verbatim below; neither is paraphrased into a gate.

**Case id `RUNG0`.** It is **NOT** `M6I`, `M6S`, `F13` or `F1`. Their verdicts are untouched here and
are neither reopened nor superseded.

---

## 0. REGISTER SEARCH BEFORE THE FREEZE (L-427)

**Searched** — with `find … -print0 | xargs -0 grep`, **never `grep -r`**, because `grep` in this
environment is `ugrep` and honours ignore files (memory note *grep-honours-ignore-files*):
`docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/standards/MESH_STANDARD.md`,
`docs/MESH_STANDARD.md`, `docs/CAPABILITY_GRID.md`, `verification/campaign/`, `cases/`,
`docs/campaigns/` for `rung 0`, `rung 1`, `rung 2`, `rung 3`, `mesh import`, `ugrid`, `plot3d`,
`cgns`, `committee grid`.

**It returned:**

- **NO registration, pre-registration or campaign-prose file for Rungs 0, 1, 2 or 3 of this ladder.**
  The literal string `rung 0` (case-insensitive) exists in **exactly one file in the repository,
  `docs/LAB_STATE.md`** — the cfd board. **Every Rung 0/1/2/3 number the lab has ever stated lives
  only on a board block and has no artifact behind it.** This registration is the first.
- `verification/campaign/M6I_PREREGISTRATION.md` — the ONERA M6 **imported** ladder. **POST-compute**
  (R0 graded `GATE FAIL`); its gates are closed and are not touched by this file.
- `verification/campaign/M6S_P_PYHYP_WALL_RESOLVED_PROBE_PREREGISTRATION.md` — the pyHyp
  feasibility probe. **POST-compute** as of this drafting; carries no verdict by its own §1.1.
- `verification/campaign/M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` — provenance record.
- `docs/standards/MESH_STANDARD.md` §3.1 (70° hard gate), §3.2 (skew 4), §6 (birth certificate),
  §8.1 (**BUILD BEFORE YOU FREEZE**), §11.3/§11.4 (aspect ratio and cell-volume ratio become
  **required to record**), §11.5 (MDS-1, and its recorded fact that
  **`cases/committee-grids/` holds ZERO `log.checkMesh` files**).
- `docs/MESH_STANDARD.md` — the **different** document: grid-**family** sizing, DPW-8/AePW-4
  guidelines, and the fact that the DPW committee publishes a **6-level** family (1 ≤ L ≤ 6).
- **`docs/CAPABILITY_GRID.md` carries NO "mesh import" row.** Confirmed here by direct read of the
  file and of `scripts/assemble_capability_grid.py`. §10 below drafts the row that must be created;
  **that file's owner is the verification supervisor, not cfd.**

---

## 1. WHAT RUNG 0 IS — AND THE TWO THINGS IT IS NOT

Rung 0 is the enabling capability for Sanaa's industrial benchmark ladder: a lane that brings a
published committee grid into OpenFOAM **without losing what makes it usable**, and reports what it
measures honestly.

**IT IS NOT AN ADMISSIBILITY LANE.** Import fidelity is a property of the **lane**; mesh quality is a
property of the **grid**. **A perfect import of an 89.98° grid faithfully reports 89.98°.** No pass
of any gate below makes any grid admissible for anything.

**IT IS NOT A MESHING-CAPABILITY CLAIM.** Sanaa's two-tier ruling is explicit — *"What committee
grids can never do is certify our meshing capability — that stays on in-house grids under 70°."*
Nothing graded here bears on whether this lab can **build** a mesh.

---

## 2. THE GATE — SANAA'S WORDS, VERBATIM

Quoted from `etc/sessions/2026-09-03T1730Z_sanaa_mesh_standard_and_freeze_enforcement.md`, item 2,
in full and unedited:

> Rung 0 wording amended: the gate is "import via UGRID with patch identity preserved; round-trip
> verified on cell count, patch names, and per-patch face counts; measured quality reported against
> the grid's own documentation." Plot3D is dropped (destroys patch identity). CGNS acquisition is
> deferred — bring it back as its own small registration if a target case only exists in CGNS.

**THE GATE SENTENCE, AS IT NOW READS AND AS EVERY GATE BELOW IS BUILT FROM IT:**

> **"import via UGRID with patch identity preserved; round-trip verified on cell count, patch names,
> and per-patch face counts; measured quality reported against the grid's own documentation."**

### 2.1 What her rewording removes from the 00:30Z order, stated so nothing is smuggled through

Her 00:30Z order read *"CGNS/UGRID/Plot3D → our solver format … verify cell count, patch names, y+
and quality against the grid's own documentation, and **re-export losslessly**."* The 17:30Z ruling
supersedes it. Three removals, each named:

| removed | her stated reason / effect | measured basis this lab already holds |
|---|---|---|
| **Plot3D** | *"destroys patch identity"* | `plot3dToFoam` imported M6I L1 (983,040 cells) as **ONE patch, `defaultFaces`, 27,648 faces**, with the `.mapbc`/`.nmf` files naming wing/symmetry/farfield **in the same directory, unread**. A single-patch mesh **cannot integrate a wing force separately from the farfield** |
| **CGNS as a Rung 0 blocker** | *"deferred — bring it back as its own small registration if a target case only exists in CGNS"* | No `cgnsToFoam`, no `libcgns`, no h5py/pyCGNS on this box, and **every `.cgns` here is ADF, not HDF5**, so h5py would not help. DPW5 and HLPW6 both publish in UGRID. **CGNS is NOT a Rung 0 gate and NOT a costed line item in §5.** |
| **"re-export losslessly"** as literally worded | replaced by *"round-trip verified on cell count, patch names, and per-patch face counts"* | No `foamToUGRID`, `foamToPlot3d` or `foamToCGNS` exists in stock tooling, so the literal clause was unmeetable for all three formats. **Her replacement names three specific quantities and is meetable.** |

### 2.2 ONE INTERPRETIVE QUESTION, SURFACED RATHER THAN DECIDED

*"Round-trip verified on cell count, patch names, and per-patch face counts"* admits two readings:

- **(i) the comparison reading** — an independent reader parses the **source** UGRID + `.mapbc` and
  compares the three quantities against the imported `polyMesh`. No writer is needed.
- **(ii) the writer reading** — the imported mesh is **written back out** to UGRID and re-read, and
  the three quantities must survive the trip.

**This registration does not gamble on a reading: it registers BOTH limbs (§4, R0-G2a and R0-G2b),
because the cost of the second limb is under two core-minutes.** If the supervisor or Sanaa rules
that (i) alone is meant, R0-G2b is struck by dated addendum and nothing else moves.

---

## 3. THE POPULATION — MEASURED ON DISK, NOT ASSUMED

`MESH_STANDARD.md` §8.1 forbids freezing a cfd mesh-ladder registration from an assumed mesh. Rung 0
is an import lane rather than a ladder, but the same discipline is applied: **every grid below is on
this box now, has already been converted, and has already been `checkMesh`'d.** Values are read off
the named log lines, never off a verdict string.

**Source grids (UGRID + AFLR3 `.mapbc`):**

| grid | source file | boundary groups in `.mapbc` |
|---|---|---|
| DPW5 L1.T hex | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/L1.T.rev01.p3d.hex.r8.ugrid` | **18** groups → 3 distinct names (`symmetry`, `wall`, `farfield`) |
| DPW5 L1.T prism | `.../L1.T.rev01.p3d.prism.r8.ugrid` | same `.mapbc` |
| DPW5 L1.T hybrid | `.../L1.T.rev01.p3d.hybrid.r8.ugrid` | same `.mapbc` |
| HLPW6 h6c1_rans_3a_1 | `/home/ubuntu/certonomous-runs/hlpw6-memory-probe/grid/h6c1_rans_3a_1.b8.ugrid` | **73** groups → 14 distinct names (`WING_UPPER`, `SLAT`, `SLAT_BRACKETS`, `SLAT_UPPER`, `WING`, `FLAP`, `FLAP_UPPER`, `FLAP_COVE`, `POS`, `WING_TIP`, `WING_TE`, `SLAT_TE`, `FLAP_TE`, `Box`) |

**Measured quality, from `cases/committee-grids/logs/*.log` and
`/home/ubuntu/certonomous-runs/hlpw6-memory-probe/logs/HLPW6_checkMesh.log`, read off the reported
MAXIMUM lines:**

| grid | cells | max non-orth | severe > 70° faces | max skewness | max aspect ratio | min / max cell volume | **cell-volume ratio (derived)** | closing line |
|---|---|---|---|---|---|---|---|---|
| DPW5 L1.T hex | 638,976 | **89.7134°** | 11,506 | **14.0594** (flagged) | **14426.8** (flagged) | 1.02355e-05 / 9.07367e+10 | **8.864e+15** | `Failed 3 mesh checks.` |
| DPW5 L1.T prism | 1,277,952 | **89.9441°** | 216,336 | **6.31513** (flagged) | **7488.42** (flagged) | 1.83438e-06 / 6.11359e+10 | **3.333e+16** | `Failed 3 mesh checks.` |
| DPW5 L1.T hybrid | 2,981,888 | **89.9985°** | 1,810,108 | **6.31513** (flagged) | **7488.42** (flagged) | 1.83438e-06 / 2.86379e+10 | **1.561e+16** | `Failed 3 mesh checks.` |
| HLPW6 h6c1_rans_3a_1 | 2,661,338 | **89.9835°** | 1,256,565 | **9.97161** (flagged) | **2286.2364** (flagged) | 2.9688178e-12 / 1.1622225e+09 | **3.915e+20** | `Failed 2 mesh checks.` |

**THE CLOSING LINE RANKS THEM BACKWARDS, MEASURED HERE AND NOT INHERITED.** HLPW6 is **more**
non-orthogonal than DPW5 hex (89.9835 vs 89.7134) and prints **`Failed 2`** where hex prints
**`Failed 3`**. **No gate in this registration reads a closing line.** Every threshold below reads a
named maximum.

**Patch identity is already preserved by the existing converter**, and this is a measured fact, not a
hope: `ugrid_to_foam.py` merges the `.mapbc` groups **by name**, producing DPW5 hex →
3 patches (`symmetry` 15,360 faces, `wall` 13,312, `farfield` 13,312) and HLPW6 → **14 named
patches** (`WING_UPPER` 39,685 faces, `SLAT` 31,844, `SLAT_BRACKETS` 16,714, `SLAT_UPPER` 12,361,
`WING` 10,971, `FLAP` 9,980, `FLAP_UPPER` 8,341, `FLAP_COVE` 7,010, `POS` 5,695, `WING_TIP` 3,934,
`WING_TE` 1,449, `SLAT_TE` 1,184, `FLAP_TE` 565, `Box` 56). **HLPW6's fourteen patches are exactly
what Rung 3's slat / wing / flap force decomposition needs and exactly what Plot3D destroyed.**

---

## 4. GATES, THRESHOLDS, CAPS AND LABELS — frozen at the freeze

All four grids in §3 are graded. **A grade is per grid; the rung's verdict is the conjunction.**

### R0-G1 — patch identity preserved

| check | threshold |
|---|---|
| number of patches in `constant/polyMesh/boundary` | **== the number of DISTINCT names in the source `.mapbc`** |
| patch names | **set-equal** to the distinct `.mapbc` names, exactly, case-sensitive |
| `defaultFaces` present | **forbidden** — its presence is an automatic `GATE FAIL` for that grid |
| every boundary face assigned | sum of `nFaces` over patches **==** the source's boundary-face count |

### R0-G2a — round-trip, comparison limb (reading (i) of §2.2)

An **independent reader** — not `ugrid_to_foam.py`, and not importing it — parses the source UGRID
and `.mapbc` and emits `(cells, {patch name → face count})`. Compared to the imported `polyMesh`:

| quantity | threshold |
|---|---|
| cell count | **exact integer equality** |
| patch names | **exact set equality** |
| per-patch face counts | **exact integer equality on every patch** |

**No tolerance. These are integers; a tolerance on an integer identity is an invitation.**

### R0-G2b — round-trip, writer limb (reading (ii) of §2.2)

`foam_to_ugrid.py` (**to be written; it does not exist**) writes the imported mesh back to UGRID +
`.mapbc`; the **same** independent reader of R0-G2a re-reads the written file. The three quantities
must be **exactly equal** to R0-G2a's source-side values.

**R0-G2b grades the ROUND TRIP, not the geometry.** It makes no claim that node coordinates survive
losslessly; that is not one of the three quantities Sanaa named and is not claimed here.

### R0-G3 — measured quality reported against the grid's own documentation

**REPORTED. NOT GATED. THIS GATE CANNOT FAIL ON A QUALITY VALUE.** It fails only on a **missing**
number. That asymmetry is the whole of Sanaa's condition (a) — *"their measured quality (max
non-orthogonality, skewness, the works) is reported on the certificate, not gated"* — and of
`MESH_STANDARD.md` §11.4 — *"No value of either quantity makes a mesh inadmissible under this
section. What makes a record INCOMPLETE is the ABSENCE of the number, never its size."*

Recorded per grid, into a `birth_certificate.json` beside the `polyMesh` (§6 of the standard) and
carrying §11.4's fields:

`cells`, `faces`, `max_non_orthogonality`, `severe_non_ortho_faces`, `max_skewness`,
`max_aspect_ratio`, `aspect_ratio_flagged`, `min_cell_volume`, `max_cell_volume`,
`cell_volume_ratio` (**stated as derived**, not as a checkMesh output), `geometric_directions`,
`checkMesh_log` (absolute path), `points_sha256`, `generator`, `created_at`, and —
**new, and required by Sanaa's condition (d)** —
`grid_provenance: "workshop committee family, quality as published"`.

**"Against the grid's own documentation" is a real comparison and is gated on being MADE, not on
agreeing.** Where the workshop publishes a quality figure for the grid, the certificate prints
**both** numbers side by side and the difference. Where it publishes none, the certificate says
**`no published quality figure located`** — never silence, never a blank.

### R0-G4 — the age guard and the no-clobber guard (rule 4)

The lane **refuses** a target case directory that already exists. Every artifact graded must be
**newer** than the run root's own creation stamp, recorded at launch in
`verification/runs/RUNG0_MESH_IMPORT_runs/RUN_ROOT_CREATED_EPOCH`.

### Verdict labels

`PASS` — R0-G1, R0-G2a, R0-G2b hold on **all four** grids and R0-G3 is complete on all four.
`GATE FAIL` — any integer identity above fails, or any R0-G3 field is absent.
`NOT A RESULT` — a reader's planted control (§7) does not fire.
`BLOCKED` — a source grid or its `.mapbc` is unreachable.
**No Roache triple is claimed by Rung 0 and no GCI is computed. Rule 5 does not bite on this rung
because nothing here is a grid-converged quantity.**

---

## 5. COST — rule 12

**Unit: core-minutes.** Dollars **DERIVED** at the recorded **c7a.4xlarge $0.0513/core-h**
(owner-stated 2026-08-21/22, corroborated `Xiao2016_EnKF/PREREGISTRATION.md:197`) and labelled
**derived, not measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**COST BASIS — MEASURED, RE-DERIVED FOR THIS FILE.** `ugrid_to_foam.py` is **SERIAL**; the rate is
**0.203 core-min/Mcell** (= 12.18 s/Mcell on one core), from the wall times in
`cases/committee-grids/measurements.jsonl` and the HLPW6 convert log, **±22 %** for contention —
the same HLPW6 grid converted in **30.5 s and 35.1 s** with a foreign solver live.

### 5.1 The estimate

| item | Mcell | core-min |
|---|---|---|
| import 4 grids (0.638976 + 1.277952 + 2.981888 + 2.661338 = **7.560154 Mcell**) | 7.560 | **1.535** |
| `checkMesh` on 4 imported meshes (allowed at 1× the converter rate) | — | 1.535 |
| `foam_to_ugrid.py` export of 4 meshes (1× converter rate) | — | 1.535 |
| independent reader, source side (0.5×) | — | 0.767 |
| independent reader, exported side (0.5×) | — | 0.767 |
| **subtotal** | | **6.139** |
| **+22 % contention band** | | **7.49** |
| **CLEAN GRADEABLE PASS (estimate)** | | **≈ 7.5 core-min — $0.0064 derived** |

**With Plot3D dropped and CGNS deferred, Rung 0 is CHEAPER than previously stated**, not dearer.
Both removals took work out and put none in.

### 5.2 Cap — **an overrun STOPS the run; it does not get a new budget**

| item | cap (core-min) | headroom | derived $ |
|---|---|---|---|
| **RUNG 0 total** | **200** | **26.7×** over the clean pass | **$0.1710 derived** |

**The headroom is a DEVELOPMENT allowance and is named as one, not disguised as solve cost.**
`foam_to_ugrid.py` and the independent reader do not exist; they will be written, selftested against
their planted controls, and re-run many times. **200 core-min is $0.17 and sits far inside Sanaa's
$25 blanket (= 29,240 core-min at the recorded rate).** A row over 3,600 wall s is a **stall**,
recorded as **waste, separately named, never absorbed** into the actual/predicted ratio
(`COMPUTE_BUDGET_CHARTER.md` §6).

### 5.3 THE OFF-BOX BRANCH — **NOT AUTHORISED BY THIS FILE, AND THE DOLLAR IS `BLOCKED-ON-PRICE`**

DPW5 **L4.F hybrid, 80.99 Mcells**, cannot be imported on this box. Sanaa ruled:

> Rented instance: do not rent 16 vCPU for a serial converter — take the smallest instance that fits
> memory. Parallelizing the converter is approved only if conversion becomes recurring; one-off
> imports don't justify it.

**Memory basis, re-verified for this file** from the three converter rows in
`cases/committee-grids/measurements.jsonl` (`sum_vmhwm_mib` 1013.8 / 1166.9 / 2519.3 at 0.638976 /
1.277952 / 2.981888 Mcell): a least-squares line gives **≈ 467 MiB + 674 MiB/Mcell**, against the
board's four-grid **495 MiB + 632 MiB/Mcell**. **Agreement to ~7 %; the fourth point was not
located, so this is a re-verification on three of four points and is stated as such.**

| basis | peak for 80.99 Mcell |
|---|---|
| board (495 + 632/Mcell) | 51,681 MiB ≈ 50.5 GiB |
| this file's 3-point refit (467 + 674/Mcell) | 55,054 MiB ≈ 53.8 GiB |
| **sizing figure used (the larger, plus margin)** | **≥ 56 GiB — target the smallest 64 GiB shape** |

**Work, and the waste that survives her ruling:**

| quantity | value |
|---|---|
| serial converter work | **80.99 × 0.203 = 16.44 core-min**, on **ONE** core |
| billed at 16 vCPU (the rejected shape) | ~263 core-min → **93.8 % waste** |
| billed at the smallest 64 GiB shape (8 vCPU) | ~131.5 core-min → **87.5 % waste** |

> **STATED PLAINLY BECAUSE IT WOULD BE EASY TO OVERSTATE THE FIX: her ruling roughly HALVES the
> billed cost (263 → ~132 core-min) but CANNOT REMOVE THE WASTE, because what is being rented is
> MEMORY, not cores, and a serial converter idles every core the memory drags along.** The honest
> unit for this rental is **GiB-hours**, not core-hours: ≈ **64 GiB × 0.30 h ≈ 19 GiB-h** of compute
> plus whatever the grid transfer costs.

**NO INSTANCE PRICE IS QUOTED. Rule 12 forbids it from recall and this box cannot read its own
billing.** The dollar figure for this branch is **`BLOCKED-ON-PRICE`**; the work is stated above in
core-minutes and GiB-hours so that a console price converts it in one multiplication. **This branch
is registered here as a named, costed gap. It is not authorised, not scheduled and not launched by
this file.**

### 5.4 Calibration — rule 12's estimate-versus-actual

At Rung 0's completion the actual core-minutes are read from the logs, the ratio actual/predicted is
stated, the gap is attributed (contention / waste / misprediction, **waste named separately, never
absorbed**), and **a row is filed to `docs/COST_CALIBRATION.md`** under that file's append rules and
the rule-10 private-index protocol. **A completion report without that comparison is incomplete.**

---

## 6. COMPLETION — rule 4, strict, all-or-nothing

Per grid: `rc = 0` on the converter, on `checkMesh`, on the writer and on both reader invocations;
`constant/polyMesh/{points,faces,owner,neighbour,boundary}` all present and non-empty;
`log.checkMesh` present and containing **both** a `Mesh non-orthogonality Max:` line **and** a
`Min volume = … Max volume = …` line; the `birth_certificate.json` of §4 present with **every** field
of R0-G3 **non-null**; and every one of those artifacts **NEWER** than
`RUN_ROOT_CREATED_EPOCH`. **The comparator refuses (exit 2) rather than degrade on any failed
clause. An absent `log.checkMesh` reads `ABSENT`. IT NEVER READS CLEAN.**

---

## 7. PLANTED CONTROLS — rule 3, on every zero this rung can report

**A zero from a reader not shown able to see a non-zero is not evidence.** Every reader plants, reads
back from disk, and **refuses if the plant is invisible.**

| reader | plant | must see |
|---|---|---|
| source UGRID/`.mapbc` reader | rename one `.mapbc` group in a **scratch copy** | the renamed patch appears in the emitted name set |
| source UGRID/`.mapbc` reader | delete one boundary face from a scratch copy | the per-patch face count drops by exactly 1 |
| `polyMesh` boundary reader | edit one `nFaces` in a scratch copy by +1 | R0-G2a reports **unequal**, not equal |
| `polyMesh` boundary reader | rename one patch in a scratch copy | R0-G2a reports **name-set mismatch** |
| `checkMesh` quality reader | fed a log of the **`=` label form** (`Max aspect ratio = 805.199 OK.`) **and** one of the **`:` form** (`***High aspect ratio cells found, Max aspect ratio: 2842.46`) | a **non-null** value from **each**, per §11.3's measured trap — a reader matching only the `=` form sees 761 of the lab's 916 logs and **silently misses exactly the 155 pathological ones** |
| `checkMesh` quality reader | fed a log with `Min volume` ≠ `Max volume` | a **non-trivial** derived ratio, never 1 |
| `foam_to_ugrid.py` round-trip | drop one face from the written file in a scratch copy | R0-G2b reports **unequal** |

**A `PASS` reported by a reader whose plant did not fire is `NOT A RESULT`, not a pass.**

---

## 8. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not make any grid admissible for anything.** §3's four grids breach
   `MESH_STANDARD.md` §3.1 by **17–20 degrees**. Rung 0 measures that faithfully and changes it by
   nothing.
2. **It does not certify this lab's meshing capability.** Sanaa's ruling reserves that to in-house
   grids under 70°.
3. **It claims no physics, no force, no `y⁺` and no comparison to any tunnel or workshop datum.**
4. **It does not claim node coordinates survive a round trip losslessly** — only cell count, patch
   names and per-patch face counts, which are the three quantities Sanaa named.
5. **It does not deliver condition (c)'s grid family.** See §11.
6. **It does not authorise the off-box branch of §5.3.**
7. **Nothing here is sent, filed, submitted or registered outside this box (rule 7).**

---

## 9. FROZEN PATHS

| what | path |
|---|---|
| this registration | `verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md` |
| run root (**ABSENT at drafting, verified**) | `verification/runs/RUNG0_MESH_IMPORT_runs/` |
| converter (existing) | `cases/committee-grids/ugrid_to_foam.py` |
| writer (**does not exist; to be written**) | `cases/committee-grids/foam_to_ugrid.py` |
| independent reader (**does not exist; to be written**) | `cases/committee-grids/read_ugrid_identity.py` |
| comparator (**does not exist; to be written**) | `verification/runs/RUNG0_MESH_IMPORT_runs/analyse_rung0.py` |
| results record | `verification/runs/RUNG0_MESH_IMPORT_runs/RESULTS.md` |

**No-compute condition, checked by direct filesystem test at drafting time and named here so it can
be re-checked:** `verification/runs/RUNG0_MESH_IMPORT_runs`, `verification/runs/RUNG0_runs`,
`verification/runs/RUNG1_runs`, `verification/runs/RUNG2_runs`, `verification/runs/RUNG3_runs`
— **all five ABSENT.**

---

## 10. THE REGISTER ROW — SANAA'S FIDELITY RULING, AND THE ROW DOES NOT YET EXIST

Her ruling, verbatim:

> Register wording: the mesh-import row certifies fidelity (faithful import + honest quality
> reporting), and says so; admissibility is the separate ruling above.

**The row does not exist.** `docs/CAPABILITY_GRID.md` and its generator
`scripts/assemble_capability_grid.py` carry no "mesh import" entry. **It must be CREATED**, and
`docs/CAPABILITY_GRID.md` is owned by the **verification supervisor** — cfd drafts the wording, it
does not land it.

**Drafted row wording, for verification to place (or amend) in `docs/capability/cfd_GRID.md` and thence
`docs/CAPABILITY_GRID.md`:**

> | **mesh import — committee grids (FIDELITY)** | **`<verdict>` — this row certifies **fidelity only**: that a published committee grid is imported **faithfully** and its **measured quality reported honestly**. It certifies **nothing about admissibility**, which is Sanaa's separate two-tier ruling of 2026-09-03, and **nothing about this lab's meshing capability**, which stays on in-house grids under the 70° gate. Import via **UGRID** with patch identity preserved; round-trip verified on cell count, patch names and per-patch face counts; measured quality reported against the grid's own documentation. **Plot3D is dropped** — it destroyed patch identity, importing M6I L1 (983,040 cells) as one `defaultFaces` patch of 27,648 faces. **CGNS is deferred** to its own registration. Grids imported and quality-reported: DPW5 L1.T hex / prism / hybrid, HLPW6 h6c1_rans_3a_1 — **all four measured at 89.71°–90.00° max non-orthogonality against the 70° gate, reported not gated.** |

**Why the qualifier is load-bearing and is not defensive padding:** an unqualified *"mesh import:
Held"* would be read as *we can bring in committee grids and use them*. Under the two-tier ruling
that reading is now **half true and half false** in a way a register cell cannot carry: the grids
are admissible for **validation-against-workshop-data** cases under conditions (a)–(d), and remain
inadmissible for **meshing-capability** claims. **The word `FIDELITY` in the row's name is what keeps
the cell honest.**

---

## 11. WHAT SANAA'S TWO-TIER RULING CHANGES DOWNSTREAM — AND WHERE OUR SCHEMA CANNOT YET SAY IT

Her ruling, verbatim:

> Two-tier mesh standard — this resolves the R12 question. The 70° gate is our generation standard:
> every mesh the lab builds must meet it, unchanged. Committee grids are a different object: they
> exist for comparability with the workshop's own results, where every participant used the same
> grids. Ruling: committee grids are admissible for validation-against-workshop-data cases without
> meeting the 70° gate, under these conditions: (a) their measured quality (max non-orthogonality,
> skewness, the works) is reported on the certificate, not gated; (b) solver-side mitigations
> (non-orthogonal corrector counts, relaxation) are registered before running; (c) the
> numerical-uncertainty band still comes from the grid family; (d) the certificate names the grid as
> "workshop committee family, quality as published" in the what-was-checked section. A full
> certificate IS reachable this way — a certificate's honesty is disclosure and verification, not our
> internal birth standard. What committee grids can never do is certify our meshing capability —
> that stays on in-house grids under 70°.

### 11.1 The board conclusion this OVERTURNS, named rather than quietly dropped

`docs/LAB_STATE.md`, cfd board 47, recorded a supervisor conclusion under the heading **"R12 DOES NOT
REACH A CERTIFICATE"**, asserting *"R12 buys a MODEL-FORM BAND ONLY. Sanaa's 'full certificate' is
NOT reachable on an R12-exempted grid."* **Her ruling overturns that conclusion.** It does so not by
disputing the R12 reading but by **superseding R12** with a two-tier standard, and it says in terms:
*"A full certificate IS reachable this way."* **This registration applies hers.** Board 47's block
stands as committed history and is not rewritten.

**What survives from that block, unaffected:** *"M6I does not qualify"* — M6I was produced by
invoking the public generator once with a namelist **this lab modified**. **Under the two-tier
standard M6I is therefore a LAB-BUILT mesh, the 70° generation gate binds it unchanged, and its
`GATE FAIL` at 87.66 / 86.46 / 87.75° stands.** Sanaa's ruling does not rescue M6I; it does not
reach it.

### 11.2 What changes in Rungs 1–3

| rung | before | after her ruling |
|---|---|---|
| **1 (ONERA M6)** | branch (c) framed as an "R12 re-import" buying a model-form band only | R12 is superseded. A committee M6 family run as validation-against-workshop-data can reach a **full certificate** under (a)–(d). **M6I itself is unaffected — lab-built, gate stands, `GATE FAIL` stands.** |
| **2 (NASA CRM / DPW)** | recorded as *"BLOCKED at section 3.1 on the very grids the workshops publish"* | **NOT BLOCKED.** Blocked→admissible under (a)–(d). **The binding constraint moves from mesh quality to condition (c)** — see 11.3. |
| **3 (HLPW)** | same block | same unblocking. HLPW6's 14 named patches make the slat/wing/flap decomposition reachable. Sanaa's own 00:30Z caveat still binds: *"Registered expectation must be honest about known RANS limits here."* |

### 11.3 THE NEW BINDING CONSTRAINT IS CONDITION (c), AND IT IS NOT SATISFIABLE FROM WHAT IS ON DISK

*"(c) the numerical-uncertainty band still comes from the grid family."* A band from a **family**
needs **three refinement levels** (`MESH_STANDARD.md` §9.1, Sanaa's own three-level ruling).

**What is on this box is `L1.T` in three CELL TYPES — hex, prism, hybrid. That is three
DISCRETISATIONS of one resolution, not a refinement family.** A Roache triple taken across them
would be `NOT A RESULT` on its face: there is no `h` to refine.

`docs/MESH_STANDARD.md` records that the DPW committee publishes a **six-level** family
(1 ≤ L ≤ 6), and board 47 measured a DPW5 **L4.F** hybrid at 80.99 Mcell, so the levels exist
upstream. **They are not here.** **Acquiring ≥ 3 nested committee levels is therefore a RUNG 0
deliverable, not a Rung 2 one, and it is not costed in §5** — acquisition cost is transfer and
storage, and the import cost scales at the §5 rate once the sizes are known. **This is the single
largest open item in the ladder and it is named here so it is not discovered at Rung 2.**

### 11.4 WHERE CONDITIONS (a)–(d) ARE NOT EXPRESSIBLE IN OUR EXISTING SCHEMA

Read at source, not from memory (`sdk/chief_engineer/certificate.py`,
`sdk/chief_engineer/mesh_certificate.py`, `docs/standards/MESH_STANDARD.md` §6).

**GOOD NEWS FIRST, because it is the load-bearing half of her ruling.** `_mesh_rows`
(`certificate.py:936`) renders max non-orthogonality as `"89.98° vs 70° gate"` with the verdict token
`caveat`, and that token **only changes the row's colour** (`certificate.py:1443`). **It blocks
nothing.** **A full certificate IS renderable today on a committee grid, exactly as Sanaa says.**

**Now the four gaps.**

| condition | gap | file |
|---|---|---|
| **(a)** *reported, not gated* | The schema has **no way to say "reported, not gated"**. The only lever is `mesh["non_orthogonality_gate"]`, and raising it to make the row read `pass` would **falsify the row** — the honest use is to leave it at 70 and let the row read `caveat`. A `quality_reporting_mode` (or `gate_basis`) field is needed so the row can render *"89.98°, reported not gated — workshop committee family"*. | `sdk/chief_engineer/certificate.py:936` |
| **(a)** *"the works"* | `_mesh_rows` emits **only** cells, non-orthogonality, skewness and severe-face count. It has **no aspect-ratio row and no cell-volume-ratio row**, so a certificate **cannot today carry** the two quantities `MESH_STANDARD.md` §11.4 made **required to record**. | same |
| **(d)** *the certificate names the grid "workshop committee family, quality as published" in the what-was-checked section* | **There is no what-was-checked section and no grid-provenance field anywhere in the certificate.** The v2 layout is masthead / subject / result + fidelity chip / three-channel uncertainty table / mesh validity / provenance footer (`verification/certificates/README.md`). **Sanaa's phrase has nowhere to land.** This is the hardest gap and it needs a new section, in a **shared** `sdk/` file that is not cfd's to edit. | `sdk/chief_engineer/certificate.py`, `verification/certificates/README.md` |
| **(a)/(d)** *the chokepoints still implement R12* | §6's birth certificate has verdicts `broken` / `flagged` / `clean`. A committee grid printing `Failed 2 mesh checks` with 1.26M severe faces certifies **`broken`**; all three mesh-cache layers then treat it as **NOT cached = quarantined**, and the model-form batch **refuses the solver launch**, its only escape being *"R12 family exemptions … through the batch's own exemption logic"*. **The code knows R12. It does not know the two-tier standard.** Until a `committee_family` admissibility state exists, condition (a) is expressible in prose and **refused in code**. | `sdk/chief_engineer/mesh_certificate.py`; `MESH_STANDARD.md` §6 |
| **(b)** *mitigations registered before running* | Expressible as a registration section — **but nothing pins the registered `fvSolution`/`fvSchemes` to the run.** `check_comparator_freeze.py` pins **comparators**, not case dictionaries, and board 47 measured it **invoked by ZERO executable files**. The only working precedent is a hand-written byte-identity assert in a wrapper (the JF1E E2b pattern). **Condition (b) is honoured today by discipline, not by tooling** — the same gap Sanaa's freeze-enforcement wiring order addresses. | `scripts/check_comparator_freeze.py` |
| **(c)** *band from the grid family* | Expressible (`scripts/roache_triple.py`), but **unsatisfiable from the grids on disk** — see 11.3. |  |

**None of these gaps is cfd's to close alone.** The certificate generator and the mesh-certificate
chokepoints are shared `sdk/` code; the standard is verification's; the register is verification's.
**They are reported here, named by file, so that they are closed before a certificate is claimed
under conditions (a)–(d) — not discovered while one is being written.**

---

## 12. WHAT IS OWED TO SANAA'S DESK

1. **Condition (d) has nowhere to land in the certificate.** Ruling needed on whether the phrase goes
   into a new what-was-checked section (a shared-`sdk` change) or, as an interim, into the mesh-validity
   block as a provenance row.
2. **The §2.2 round-trip reading.** This file registers both limbs; if only the comparison limb is
   meant, say so and R0-G2b is struck by addendum.
3. **Condition (c)'s missing committee refinement levels** (11.3) — an acquisition, not a solve.
4. **The off-box import branch's price** (§5.3), which is `BLOCKED-ON-PRICE` and cannot be quoted
   from this box.
