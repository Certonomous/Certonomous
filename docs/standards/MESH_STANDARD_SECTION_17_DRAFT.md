# DRAFT for `docs/standards/MESH_STANDARD.md` — Section 17

**Status: DRAFT, handed to the cfd supervisor. NOT COMMITTED TO THE STANDARD.**
This lane drafts; he appends and commits. To adopt: append §17 verbatim at the foot
of that file under standing rule 6 and carry the assertion line, **measured, not
asserted** (md5 of the first 2,429 lines before and after the append).

**The ordinal and the version were derived from the document's own tail in the same
shell invocation as this write**, per the §14 lesson that the two counters diverged
once already and that neither may be read off a neighbouring section:

```
max section ordinal present = 16   (ordinals run 1..16, contiguous, no gaps)  -> THIS IS SECTION 17
max section version present = v1.11 (v1.1..v1.11, and v1.11 is used TWICE)    -> THIS IS v1.12
md5 of MESH_STANDARD.md at draft time = 2ee7cf76f8c8c10adfc465885a04df1c, 2429 lines
```

Numbers marked **[VERIFIED HERE]** were read by this lane from the named file on
disk in this session. Numbers marked **[CITED]** come from another record and are
attributed to it.

---

## 17. PUBLISHED SNAPPYHEXMESH LAYER PRACTICE — SIX DICTIONARIES ON DISK, WHAT THEY SETTLE, AND WHAT THEY DO NOT (v1.12, 2026-09-13)

### 17.0 THIS SECTION EXISTS BECAUSE §16.0's CENTRAL EMPIRICAL CLAIM IS NOW FALSE

§16.0, committed at `50ce30f5` at 17:37 on 2026-09-13, says — and the claim is
load-bearing, because it is the argument for why §16 had to be house practice
rather than published practice:

> **Three for three. No published source is going to warn this lab about a
> snappyHexMesh relative-thickness defect, because none of them has a relative
> thickness to get wrong.** Retrieval cannot close this gap. A lab-side rule can.

**Retrieval closed the gap eighteen minutes later.** Under Sanaa's §J and §K
case-file instruction, three trees of *actual OpenFOAM case files* were retrieved,
hashed and parse-verified (`docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`,
committed `799c88e7`). They contain **six snappyHexMesh layer dictionaries**, every
one of which states `relativeSizes`, `nSurfaceLayers`, `expansionRatio`, a first- or
final-layer thickness, `minThickness` and `featureAngle` explicitly.

**§16.0's table is not wrong; its generalisation is.** The three sources §16.0 names
— Ashton et al. 2016 (STAR-CCM+), Sikirica et al. 2019 (block-structured),
DrivAerML 2024 (ANSA HeXtreme) — genuinely have no relative thickness to get wrong,
and they were *papers*. The error was concluding from three papers that **no**
published source could speak to this, when the objects that speak to it are **case
files, not papers** — and papers publish what a mesher produced, never its
dictionary. That distinction is the whole content of Sanaa's §G rule.

**§16's RULES L1 through L5 are untouched by this section and remain in force.**
What changes is §16.0's claim that published practice is unavailable, and one
numeric reading inside §16.3, narrowly, at §17.4.

---

### 17.1 THE SIX POINTS, WITH PROVENANCE

**[VERIFIED HERE]** — every row read from the file named, in a tree whose per-file
sha256 manifest is recorded in `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` §1.

| Case | Dictionary | `relativeSizes` | N | r | thickness as written | Background block | Base cell | Wall level | **S, local cells** |
|---|---|---|---|---|---|---|---|---|---|
| Wolf Dynamics DrivAer **coarse** | `drivaer_coarse/system/snappyHexMeshDict` | `true` | 3 | 1.2 | `finalLayerThickness 0.3` | uniform hex, `deltax=deltay=deltaz=0.2` | **0.2 m** | `body2 (3 3)` | **0.758333** |
| Wolf Dynamics DrivAer **fine** | `drivaer_fine/system/snappyHexMeshDict` | `true` | 6 | 1.2 | `finalLayerThickness 0.3` | same deltas | **0.2 m** | `body2 (4 4)` | **1.197184** |
| occDrivAer rotating mesh (Upstream CFD) | `occDrivAerRotMesh.orig/system/snappyHexMeshDict.full:512-516` | `true` | 2 | 1.2 | `finalLayerThickness 0.5` | 120×44×20 over 120×44×20 m | **1.0 m** | L9 body | **0.916667** |
| ONERA M6 (Alletto) | `OneraM6Wing/system/snappyHexMeshDict` | `true` | 5 | 1.5 | `finalLayerThickness 0.5` | 30×15×30 over ±18000 | **1200 units** | `wing (8 9)` | **1.302469** |
| ESI marine propeller (MB13) | `marinePropeller/system/snappyHexMeshDict:265-280` | **`false`** | 5 | 1.20 | `firstLayerThickness 1.0e-04 m` (tip), `2.0e-04 m` (stem) | 40×80×40 over 1.2×2.4×1.2 m | **0.03 m** | tip (4 5), stem (4 4) | **0.79377** (both) |
| High-lift CRM ONERA | `highLiftCommonResearchModelONERA_LRM-LDG-HV/system/snappyHexMeshDict:2075-2095` | `true` | 2 | **1** | `finalLayerThickness 0.8` | not extracted | — | — | **1.600** |

Arithmetic, so every S is re-derivable without opening a file:
`S = t_f · Σ_{i=0}^{N-1} r^(-i)` for a relative *final* thickness, and
`S = t_1 · (r^N − 1)/(r − 1) ÷ local cell` for an absolute *first* thickness.
Local cell = base cell ÷ 2^level.

**Set against §16.3's two measured points — 0.480 EXTRUDED, 1.6808 COLLAPSED — every
one of the six published requests falls between them**, clustering 0.76–1.30, with a
single outlier at 1.600 whose mechanism is §17.5.

---

### 17.2 THE LIMIT OF THIS EVIDENCE, STATED BEFORE ANY USE IS MADE OF IT

> **A published dictionary is a REQUEST. It is not an ACHIEVEMENT.**
> None of the six may be cited as a stack that extruded.

**No retrieved tree ships a `snappyHexMesh` log or a layer-coverage table for any of
these six cases.** [VERIFIED HERE] The only solver logs in the Wolf Dynamics tree are
`sol_logs/{coarse,fine}/log.solver`, which are `simpleFoam` runs; the string `layer`
occurs in `sol_logs/coarse/log.solver` **zero times**.

**PLANTED CONTROL, because a zero from a reader not shown able to see a non-zero is
not evidence** (standing rule 3). The same sweep, over the same three trees, with the
same pattern, **did** return `log.snappyHexMesh` files — in
`alletto-openfoamtutorials/membranBCSend/.../circularMembrane230Pa/` and
`circularMembrane230PaFine/`. **The reader can see a snappyHexMesh log when one
exists. It found none for any of the six.** The zero is therefore evidence.

**Worse for the Wolf Dynamics rows specifically: its shipped results cannot be
attributed to its snappy mesh at all.** [VERIFIED HERE] The tree ships *two mutually
exclusive* mesh routes — `run_mesh_shm.sh` (blockMesh + snappyHexMesh) and
`run_mesh_fluent.sh` (`fluent3DMeshToFoam mesh/mesh_coarse.msh`) — and its own
`README.TXT` recommends the second: *"Generating the mesh with SHM is time consuming
so better use the pre-generated mesh."* The shipped `log.solver` records
`Case : /home/joegi/OF_training/UNISA/COURSE/session2/Xdrivaer`, `Date : Apr 20
2022`, `nProcs : 4`, and names no mesher. **Which of the two meshes produced the
distributed `Cd` and `y+` is not recoverable from the tree.**

**Consequence for every use below.** These six points are evidence of what expert
practitioners *request* on this mesher — real evidence, and the lab had none of it an
hour ago. They are **not** evidence that any of those requests was granted. No rule
in this section converts a published S into a demonstrated-safe S.

---

### 17.3 RULE L6 — `relativeSizes` IS TOPOLOGY-CONDITIONAL, AND THAT IS WHY §16's L1 IS RIGHT FOR THIS LAB AND WRONG AS A DESCRIPTION OF THE WORLD

> **`relativeSizes true` is correct practice on a uniform Cartesian background block
> and catastrophic on a graded or wedge background.** The discriminator is not the
> flag; it is whether `hexRef8::getLevel0EdgeLength()` — the **global minimum**
> level-0 edge in the whole mesh — equals the base cell the author had in mind.
> **A registration that sets `relativeSizes true` must state the background topology,
> not merely the measured `level0Edge`.**

**[VERIFIED HERE]** Four of six use `true`, two use `false` — **and all six mesh a
body inside a uniform Cartesian block**, in which the global minimum level-0 edge
*is* the base cell and relative sizing means exactly what it says. **No retrieved
case uses `relativeSizes true` on a non-uniform background.**

The two that turn it off are the two whose thicknesses are physically pinned — the
ESI marine propeller (acoustics, absolute metres) and the aeroacoustic DrivAer
(33 body patches at `firstLayerThickness` 5.25e-06 to 1.17e-05 m). **Neither turns it
off to escape a topology defect.** They turn it off because they want a stated y+.

**This strengthens §16.1 rather than weakening it, and it changes its reasoning.**
L1 refuses `relativeSizes true` without a declared, measured `level0Edge`. The
published population shows *why* that refusal is right **here specifically**: this
lab's PPTC background is a **72° wedge**, whose global minimum level-0 edge is a 2 mm
axis rod's azimuthal chord, **2.09343825e-04 m**, poisoning every thickness by
**95.5×** [CITED, `docs/standards/MESH_STANDARD.md` §16.2]. Nobody in the published
set meshes on a wedge. **The world does not warn about this defect because the world
does not build the topology that has it.**

**Corollary, and it is the PPTC design decision.** Published propeller practice is
`relativeSizes false` **together with** a full-360° Cartesian box — the ESI case is
both at once. **The two choices travel together and neither alone is the published
practice.** A registration that adopts the absolute thicknesses but keeps the wedge
has adopted half of it.

---

### 17.4 SUPERSESSION, NARROW: §16.3's "ABOVE 1.0, EXPECT COLLAPSE" IS NOT SUPPORTED AS A NUMERIC THRESHOLD, AND ITS REGISTRATION DISCIPLINE IS UNAFFECTED

§16.3 rule L2 reads, in part:

> **A layer stack that asks for more than ONE local cell of total thickness is asking
> the mesher for room it does not have.** [...] **Above 1.0, expect collapse**

**[VERIFIED HERE]** Three of the six published requests sit above 1.0 — 1.197184,
1.302469 and 1.600 — and a fourth sits at 0.917. **Expert practitioners on this
mesher routinely request above 1.0.** §16.3 itself is explicit that it rests on
**"two measured points and only two"**, and the lower of those two (0.480) is now
shown to be **below every published request**, i.e. it was never near the transition.

**What is superseded:** the reading of **1.0** as a physical threshold at which
collapse begins. It is not one. The lab's own collapse at **1.6808** remains a
measurement and is not disturbed; what the six points show is that the transition
lies **somewhere above 1.30 and at or below 1.6808**, not at 1.0.

**What is NOT superseded, and is the part that matters:**
1. **Compute S before the run and record it in the registration.** Unchanged, and
   §17.2 makes it more necessary, not less: since no published case evidences
   achievement, S is a design number that must be declared and then *measured against
   the post-extrusion table* (§16.6 rule L5).
2. **§16.3's failure-mode warning is untouched and was never about the threshold:**
   *"Do not expect a too-thick stack to give you fewer layers. Expect it to give you
   none."* The mechanism cited for it — a pyramid volume failing `minVol` by 1.17×
   [CITED, `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:56-70`] — is a margin-of-order-one
   argument that does not depend on where the threshold sits.
3. **The lab's own 1.6808 collapse** [CITED, §16.3], which is a measurement on this
   box and outranks any published request.

**Restated clause, for L2:**

> Compute the stack in local cells, `S`, and record it in the registration.
> **Published snappyHexMesh practice spans S = 0.76 to 1.60** (§17.1), so a value in
> that band is not by itself a defect and needs no exception. **This lab has measured
> a collapse at S = 1.6808 and an extrusion at S = 0.480**; between 1.30 and 1.68 is
> unbracketed. **Above 1.60, a registration states its expectation explicitly and
> cites the post-extrusion table that will test it.** No value of S is
> demonstrated-safe on this box above 0.480 until a run measures it here.

---

### 17.5 THE 1.600 CASE BUYS ITS HEIGHT WITH TWO SETTINGS, AND THAT IS A MECHANISM, NOT A COINCIDENCE

**[VERIFIED HERE]** The high-lift CRM ONERA case is the only published request near
the lab's collapse point, and it differs from the other five in exactly two fields:

| Field | High-lift CRM | Other five |
|---|---|---|
| `expansionRatio` | **1** | 1.2 (four), 1.5 (one) |
| `maxThicknessToMedialRatio` | **3** | **0.3** (Wolf Dynamics, occDrivAerRotMesh, M6 Alletto, ESI propeller — all four) |
| `nGrow` | **−1** | 0 (all five) |

`maxThicknessToMedialRatio` is the field that reduces layer growth where the stack is
large relative to the distance to the medial axis — i.e. **the field that decides
whether a tall stack is thinned or kept**. Ten times the value every other case uses,
paired with a *uniform* layer stack (`expansionRatio 1`, so no geometric growth to
amplify), is a coherent way to ask for 1.6 local cells and expect to keep it.

**Registration consequence.** A registration asking for `S > 1.30` **states its
`maxThicknessToMedialRatio` and `expansionRatio` beside the S**, because at 0.3 and
1.2 — this lab's values, and four of the five others' — there is no published case
above 1.302 to point at. **[VERIFIED HERE]** the lab's collapsed DrivAer ran
`expansionRatio 1.25` at S = 1.6808 [CITED, §16.3], i.e. **the high-ratio, high-S
combination that no published case uses.**

---

### 17.6 PRISM-A2 IS NOW REGISTERED AT S = 0.794, AND HALF OF THE REASONING THAT MOVED IT THERE IS WITHDRAWN BY §17.2

**The sequence, because the record has to carry it.** PPTC PRISM-A2 Amendment 1 registered
**S = 1.000** under an explicit hedge: *"`S = 1.00` is NOT in the demonstrated-safe region.
§16.3's rule rests on two measured points and only two."* Amendment 2, committed
**`b3deca9b3` at 18:23:56Z on 2026-09-13**, struck that and moved the target to
**S = 0.794**, giving as its reason:

> *"That hedge is now superseded by evidence. Six published OpenFOAM cases report stacks of
> 0.758, 0.794, 0.917, 1.197, 1.302, 1.600 local cells."*
> — `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md`, Amendment 2

**§17.2 withdraws half of that reason, and the half it withdraws is the load-bearing half.**
Those six numbers are what those cases **ask for**. **No retrieved tree ships a
snappyHexMesh log or a layer-coverage table, so not one of the six is evidence that the
layers appeared.** A band populated by people willing to ship those numbers is not a band
demonstrated to extrude. **"Published practice achieves 0.794" is not a supported
statement and must not be made.**

**THE RULING SURVIVES ON A DIFFERENT AND WEAKER BASIS, AND THE WEAKER BASIS IS THIS LAB'S
OWN MEASUREMENTS:**

> **0.794 is nearer to the only stack this lab has measured EXTRUDING — our own 0.480 —
> and further from the 1.6808 we measured COLLAPSING, than 1.000 is.** That is the whole
> of the support, it comes from two measurements on this box, and it is enough to prefer
> 0.794 over 1.000 without being enough to call either safe.

**What the six published values DO still establish, stated at its real strength:** that
expert practitioners on this mesher are willing to ship stacks across 0.758–1.600, so a
value inside that band is **not anomalous** and needs no special pleading in a
registration. That is a statement about what is unremarkable to request. **It is not a
statement about what extrudes**, and §17.4's restated L2 clause is worded to claim only
the former.

**Recorded as a method point, because it is why this correction exists at all.** The
absence was found by **planting a control on the claim rather than asserting it**: the
same sweep that returned zero snappyHexMesh logs for the six cases **did** return
`log.snappyHexMesh` files elsewhere in the same trees (§17.2). Had the sweep simply
reported "none found", the absence would have been indistinguishable from a broken reader,
and Amendment 2's reasoning would have stood uncorrected.

### 17.7 THE PER-PATCH PATTERN WAS INDEPENDENTLY REPRODUCED, AND THAT IS THE STRONGEST SINGLE RESULT HERE

**[VERIFIED HERE]** The ESI marine propeller sets `firstLayerThickness 1.0e-04 m` on
`propellerTip` at refinement level 5 and `2.0e-04 m` on `propellerStem1/2` at level 4
— **a factor of two, exactly tracking the factor of two in local cell size**. Both
patches therefore land on the **same S = 0.79377**.

**[CITED]** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md`, A1.2, arrived at the same
construction without having seen that file: `blades` (level 5) 3.4091e-4 m, `hub` and
`cap` (level 4) 6.8182e-4 m, `shaft` (level 3) 1.3636e-3 m — **each a factor of two
apart, every patch on the SAME S.** (A1.2 set that common S to 1.000; Amendment 2
`b3deca9b3` moved it to 0.794 — **the per-patch PATTERN is unchanged by the move, which is
precisely what makes it a pattern and not a value.**)

> **RULE L7 — Under `relativeSizes false`, set each patch's absolute thickness in
> proportion to its own local cell, so that every layered patch lands on the SAME S.**
> This is what §16.4's rule L3 asks for stated forward: L3 observes that a *relative*
> dictionary gives different physical layers on different patches; L7 is the absolute
> dictionary's answer, and it is published practice, not a lab invention.

Two independent constructions reaching the same design pattern is the nearest thing
to external corroboration this section contains — **and it corroborates the pattern,
not the value.** Neither construction is evidenced as achieved (§17.2), and the pattern
would be the same at any common S.

---

### 17.8 SCOPE, AND WHAT THIS SECTION DOES NOT CLAIM

- It **does not claim any published stack extruded.** §17.2. No achievement record
  exists in any retrieved tree, and the zero carries a planted control.
- It **does not re-grade anything**, retire any gate, or touch §16's rules L1, L3, L4
  or L5. Its only supersession is the numeric reading inside §16.3, at §17.4, and it
  is bounded there.
- It **does not bracket the collapse transition.** It narrows the open interval from
  (0.480, 1.6808) to roughly (1.302, 1.6808) *as a statement about published requests*,
  which is weaker than a measurement. **A real threshold is still a separate
  measurement campaign on this box**, exactly as §16.3 said.
- It **does not claim that published practice ACHIEVES any value**, and it withdraws that
  claim where another record has already relied on it (§17.6). The six values bound what is
  unremarkable to REQUEST; the lab's own 0.480 and 1.6808 are the only extrusion evidence
  that exists anywhere in this section.
- It **does not claim the six cases are comparable to each other.** They span steady
  RANS, DDES and LES, three solvers, and length scales from a 0.224 m propeller to a
  44 m-wide car domain. What is comparable is the one dimensionless quantity S.
- It **makes no claim about OpenFOAM versions other than those the sources declare** —
  v2412, v2206, v2006, and OpenFOAM 9. The lab's own readings remain `OPENFOAM=2606`.
- The high-lift CRM row's background mesh and refinement levels were **not extracted**;
  its S is computed from its layer block alone and its base cell is unknown.
- **occDrivAer's static/HPC-Challenge case ships no mesher dictionary at all**; the
  row used here is its *rotating-mesh sibling*. The four agreeing numbers linking them
  are an **inference, not a proof** [CITED, `PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`
  F-1a].

---

### 17.9 A DEFECT IN §16's OWN AMENDMENT RECORD, NAMED AND NOT FIXED

**[VERIFIED HERE]** §16 is committed and rule 6 binds it, so this is disclosed rather
than corrected:

- §16's heading declares **`(v1.11, 2026-09-13)`**, but **§15.10 already declares
  `(v1.11)`**. Two sections claim the same version.
- §16's own amendment record at the file's foot reads **"Version 1.6 → 1.7"**, which
  matches neither its heading nor any neighbouring section. It appears to be the
  *draft's* intended bump carried through unedited — the same draft whose title line,
  still present in the committed file, reads **"# DRAFT for
  `docs/standards/MESH_STANDARD.md` — Section 11"** for what was adopted as §16.
- §14.5 already names a related, deliberately unresolved discrepancy: the file header
  at line 3 reads `Version 1.2, dated 2026-08-11` while the highest section version is
  far above it, and §14.5 rules that **the authoritative version is the highest
  section version**. This draft follows that ruling, which is why it is v1.12 and not
  v1.8.

**Recommended disposition: a separate, disclosed housekeeping amendment**, not folded
into this one, and not by this lane. Repairing it inside §17 would make §17 a document
about two unrelated things.

---

### 17.10 Sources

| Artifact | Used for |
|---|---|
| `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` (committed `799c88e7`) | provenance, hashes and parse checks for all three trees; F-1a; F-2; F-3 |
| `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.*.txt` (365 files) | per-file sha256 of every dictionary cited in §17.1 |
| `wolfdynamics-drivaer/drivaer_{coarse,fine}/system/snappyHexMeshDict` | §17.1 rows 1-2, §17.3, §17.4 |
| `wolfdynamics-drivaer/drivaer_coarse/{README.TXT,run_mesh_shm.sh,run_mesh_fluent.sh,sol_logs/coarse/log.solver}` | §17.2, the two mesh routes and the unattributable result |
| `openfoam-hpc-tc/.../occDrivAerRotMesh.orig/system/snappyHexMeshDict.full:512-516` | §17.1 row 3 |
| `openfoam-hpc-tc/.../marinePropeller/system/snappyHexMeshDict:265-280` | §17.1 row 5, §17.3, §17.7 |
| `openfoam-hpc-tc/.../highLiftCommonResearchModelONERA_LRM-LDG-HV/system/snappyHexMeshDict:2075-2095` | §17.1 row 6, §17.5 |
| `alletto-openfoamtutorials/OneraM6Wing/system/snappyHexMeshDict` | §17.1 row 4 |
| `alletto-openfoamtutorials/membranBCSend/.../log.snappyHexMesh` (×2) | §17.2 **planted control** — proof the sweep can see a snappy log |
| `docs/standards/MESH_STANDARD.md` §16.0, §16.1, §16.2, §16.3, §16.4, §16.6, §14.5, §15.10 | what is quoted, what is superseded, what is named |
| `verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md` A1.2, A1.3, :56-70 | §17.7, §17.4 point 2 |
| the same file, **Amendment 2, committed `b3deca9b3` 2026-09-13T18:23:56Z** | §17.6 — the S = 1.000 -> 0.794 reversal whose stated basis §17.2 half-withdraws |

---

### AMENDMENT RECORD — to be completed BY THE APPENDING COMMIT, measured not asserted

| | |
|---|---|
| section ORDINAL | **17** (derived from the tail: max present = 16, contiguous 1..16) |
| section VERSION | **v1.11 → v1.12** (derived from the tail: max present = v1.11, claimed twice) |
| gates changed | **0** |
| thresholds changed | **0** |
| results re-graded | **0** |
| solver compute | **0 core-min, $0.00** |
| retrieval compute | **~15 core-min**, single core, download + untar + sha256; no pre-registered estimate existed for a retrieval, so **no calibration ratio is claimable** |
| rules superseded | **one numeric reading only** — §16.3's "above 1.0, expect collapse"; §16 rules L1, L3, L4, L5 untouched |
| rules added | **L6** (§17.3), **L7** (§17.7) |
| **lines whose number changed above this section** | **0** — *to be MEASURED by the appending commit:* md5 of this file's first 2,429 lines before the append and after it must be **EQUAL**; at draft time that md5 is `2ee7cf76f8c8c10adfc465885a04df1c` |
| nothing written to `docs/physics_rules.yaml` | correct — §17 binds by being quoted, at §16's maturity |
