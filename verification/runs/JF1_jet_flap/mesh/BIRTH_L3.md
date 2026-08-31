# JF1 MESH BIRTH CERTIFICATE — LEVEL L3

Required by `verification/campaign/JF1_PREREGISTRATION.md` §4.5 (frozen at
commit `12b1bd84`).  Every number below is parsed from this level's own
`build.log` and `checkMesh.log` in this directory; none is transcribed.

**TOPOLOGY: C-MESH**, the topology §3.2 registers.  This level is NOT the O-mesh
that `cases/JF1_JET_FLAP/build_jf1.py` emits and that the five completed L1
feasibility rows of 2026-08-31 ran on.  That generator is untouched.

| | |
|---|---|
| generator | `verification/runs/JF1_jet_flap/mesh/make_jf1_mesh.py` (§4.1) |
| generator md5 | `8bb1754cd601de9f030f72c83bd60525` |
| repository HEAD at emission | `db04e95a60d0309e051d01a5b78e1f95e24f343d` |
| ladder scale `s` | **1.8708** |
| `--topology` | `c` — REQUIRED on the command line, never defaulted |

## 1. Cell count, against the registered §4.2 table

| | registered §4.2 | emitted | |
|---|---|---|---|
| surface cells per side | 187 | 187 | match |
| wake cells per side | 243 | 243 | match |
| wall-normal cells | 181 | 181 | match |
| cells across `h` | 22 | 22 | match |
| **TOTAL** | **161006** | **161006** | **match** |

Block arithmetic: `2*(187 + 243)*181 + 243*22 =
161006`.  The generator REFUSES to emit a level whose counts differ from
this table.

## 2. Refinement ratios against the level below, per direction (§4.5)

| direction | level below | this level | ratio |
|---|---|---|---|
| surface tangential | 137 | 187 | **1.3650** |
| wake streamwise | 178 | 243 | **1.3652** |
| wall-normal | 133 | 181 | **1.3609** |
| across the slot `h` | 16 | 22 | **1.3750** |
| first-cell height `y1` | 3.651501e-06 | 2.672653e-06 | **1.3662** |

Cell-count refinement ratio against **L2**: `h ∝ N^(-1/2)` gives **1.36322**.  In Roache indices (section 4.2: fine = 1 is **L3**), this level is index **1 (fine)**.

## 3. Wall-normal distribution (§4.3)

| | |
|---|---|
| registered `y1` | 2.672653e-06 m |
| **ACHIEVED wall spacing, measured perpendicular** | min **2.669477824e-06** m, max **2.672653410e-06** m |
| spread along the airfoil | **0.1190 %** |
| first cell-CENTRE wall distance | 1.334738912e-06 m |
| normal cells `N` | 181 |
| **`g` SOLVED** from `y1 (g^N − 1)/(g − 1) = 25.0 m` | **1.077393** |
| assertion `g ≤ 1.15` | **YES, 1.077393 ≤ 1.15** |
| complete layers inside `delta` | **87** (registered floor 36) |

**THE ACHIEVED WALL SPACING IS CONSTANT ALONG THE AIRFOIL TO 0.1190 %.**  This
is recorded explicitly because F28's radial distribution was a RATIO applied to
rows of differing height, so its achieved wall spacing varied 1.0e-05 to
1.53e-05 m — a 53 % spread — and its `y+` gate was argued at one station only.
JF1 does **not** have that property: `y1` is an absolute length applied to the
true surface normal at every station, and the 0.1190 % residual is the cosine
of the small angle between the nodal normal and the two adjacent face normals,
not a distribution artefact.

## 4. `y+` — ESTIMATES ONLY, NOT MEASUREMENTS

`y+` can only be measured from a solved field.  **No solver has been run on this
mesh.**  The figures below are estimates formed from §4.3.2's envelope
`u_tau = 1.8837 m/s` (the worst GATED row, `C_mu_jet = 0.1`, `alpha = 8 deg`,
evaluated at `x = 5.0e-04 m`) applied to the ACHIEVED spacing above.

| quantity | estimate | registered gate |
|---|---|---|
| `max(y+)`, cell-HEIGHT convention (as §4.3.3 predicts) | **0.5034** | `≤ 1` |
| `min(y+)`, cell-HEIGHT convention | 0.5028 | — |
| §4.3.3's own predicted value for this level | 0.5035 | — |
| `max(y+)`, cell-CENTRE convention (what OpenFOAM's `yPlus` reports) | 0.2514 | — |

**Registered status: `PENDING` — measured `y+` awaits a solve** (§7.4 gates the
MEASURED value).  The two conventions differ by a factor of two and are both
printed so no reader takes one for the other.

## 5. Slot and wake resolution (§4.4)

| | |
|---|---|
| cells across `h` | **22** (L1 floor is 12) |
| base cell `h/n_sheet` | 2.272727e-04 m |
| surface spacing at the TE | 2.272727e-04 m — **matched to the base cell, verified by the generator, which refuses on a mismatch** |
| wake fine box, TE → 3 c | 152 cells, `g` SOLVED 1.042541 |
| wake coarse, 3 c → outlet | 91 cells, `g` SOLVED 1.012980 |
| streamwise cell at `x/c = 1` aft of the TE | 4.151326e-02 m |
| outer-boundary wake grading, SOLVED | 1.015034 |
| cells across the `max\|U\|` locus at `x/c = 1` | **PENDING — measurable only post-solve (§4.4, §7.4)** |

The jet-sheet block carries 22 cells across `h` for the whole wake, so
"the sheet is resolved for ≥ 1 c downstream" holds by construction of the
topology, as §3.2 requires — but the ≥ 8-cell assertion of §4.4 is on the solved
`max|U|` locus and is therefore `PENDING`, not claimed here.

## 6. `checkMesh` gates (§4.5)

| metric | gate | measured | verdict |
|---|---|---|---|
| max non-orthogonality | **< 65** (JF1's own, tighter than the lab standard's 70) | **35.3964** (average 6.2333) | **PASS** |
| max skewness | **< 4** | **0.223786** | **PASS** |
| negative volumes | **exactly 0** | min cell volume 2.857450e-10 m³ (> 0) | **PASS** |
| `checkMesh` overall | must print `Mesh OK` | see §7 below | see §7 |

Max cell volume 0.711275 m³; total volume 2281.97 m³.

## 7. `checkMesh` DID NOT PRINT `Mesh OK` — AND THE REASON IS THE ASPECT-RATIO ADVISORY, NOT A GATE

`checkMesh` reports `Failed 1 mesh checks` on this level.  **The single failed
check is the aspect-ratio advisory**, which fires at OpenFOAM's built-in
threshold of 1000.  §4.5 makes aspect ratio **REPORTED, never gated**, and §4.5's
D4 states in terms that `AR > 1000 is expected and is not a defect here`.  Every
gated `checkMesh` metric — non-orthogonality, skewness, negative volumes,
topology, face pyramids, cell openness, boundary closure — passes.

This is recorded in these words so that no downstream reader converts the
literal absence of the string `Mesh OK` into a mesh failure.

## 8. Aspect ratio — REPORTED, and the alignment justification stated honestly

| region | OpenFOAM 2-D aspect ratio |
|---|---|
| **whole mesh, maximum** | **152699.9** |
| whole mesh, mean | 1637.5 |
| airfoil first layer | 476.9 |
| airfoil block, all `j` | 476.9 |
| jet-sheet block | 1795.7 |
| wake, inside the 3 c box | 45884.4 |
| **wake, beyond the 3 c box** | **152699.9 — this region carries the maximum** |

| | |
|---|---|
| **TRUE geometric aspect ratio** (longest cell edge / shortest), maximum | **152699.9** |
| true geometric aspect ratio, airfoil first layer | **5204.3** |

**OpenFOAM's aspect ratio is a ratio of CARTESIAN COMPONENTS of `Σ|Sf|`, not a
cell shape.**  A mid-chord first-layer cell here is 2.9e-02 m by 5.0e-06 m — a
true 5800 — and OpenFOAM scores it 31.5, because the 1.8° surface slope leaks
`0.029 × sin(1.8°)` into the x component.  Both numbers are therefore printed.
A single OpenFOAM aspect-ratio figure quoted alone would understate the airfoil
and overstate nothing; this is worth knowing when comparing against any other
case's reported figure.

**REGISTERED ALIGNMENT JUSTIFICATION (§4.5, required on every certificate), and
where it does and does not apply.**  On the airfoil and through the jet-sheet
block, the anisotropy is **wall-normal and shear-layer-normal — aligned with the
direction being resolved**, on cells whose non-orthogonality is 35.3964 (gated
< 65) and whose skewness is 0.223786 (gated < 4).  That is the legitimate case
`MESH_STANDARD.md` §3.3 names.

**The maximum, 152699.9, is NOT on those cells.**  It sits in the wake beyond
the 3 c box, where the first cell off the sheet is still `y1` and the streamwise
cell has grown to order 1 m.  There is no wall and no resolved gradient there,
so the wall-normal alignment argument does **not** cover those cells and is not
claimed for them.  Their anisotropy is streamwise-aligned with the flow, which
is a weaker but real justification.  **This is disclosed rather than absorbed.**

The alternative was measured, not assumed: relaxing the wake first-cell height
downstream cuts the maximum aspect ratio to ~5e04 but raises max
non-orthogonality from 35.3964 to **88.2** on L1 — which would fail the §4.5
gate of 65 outright *and* trip the compound rule below.  The construction is
therefore forced, and the aspect ratio is the quantity that gives way, because
it is the one §4.5 does not gate.

**§4.5's COMPOUND PROMOTION** — `AR > 1000` together with non-orthogonality
`> 60` **or** skewness `> 2` is a JF1 `BLOCKED`.  Measured here:
non-orthogonality 35.3964 (≤ 60) and skewness 0.223786 (≤ 2).
**Compound condition: NOT TRIGGERED.**

## 9. Face-adjacent cell-volume ratio — REPORTED, gated by nothing

| | |
|---|---|
| **max face-adjacent cell-volume ratio** | **85.1721** |

This metric is in no registered gate set.  It is reported because a sister case
in this family (F28) was admitted by non-orthogonality, skewness and negative
volumes alone while carrying a neighbour volume jump of 28 735.

**The maximum here is not an accident of construction and cannot be tuned away.**
It sits on the sheet/wake faces at the trailing edge, where §4.3's `y1 =
5.0e-06 m` meets §4.4's 22 UNIFORM cells across `h` (2.272727e-04 m each).  The
ratio of those two registered lengths IS the number.  It is invariant under every
knob the generator exposes — measured identical across six settings that moved
max non-orthogonality from 33.6 to 88.6.

It is also invariant under `t_z`, which is a common factor of every cell volume.

## 10. `t_z` and the §7.4 slot-area cross-check

| | |
|---|---|
| `t_z` used | **1.0 m exactly** |
| basis | §5.6 registers `t_z = 1.0 m` EXACTLY and requires the mesh script to refuse otherwise; the generator asserts it |
| **`area(jetSlot)` MEASURED from the emitted faces** | **5.000000000e-03 m²** |
| §7.4 cross-check `= 0.005 m² to 1e-9` | **PASS** |
| `Aref = c · t_z` implied | **1.0 m²** (`forceCoeffs.C:164` reads `Aref` verbatim; §5.6 HAZARD 1) |

**The existing case directory `cases/JF1_JET_FLAP/case*` sets `t_z = 1.0e-02 m`
and `Aref = 0.01`, which is internally consistent but would make §7.4's frozen
cross-check REFUSE (exit 2).  That contradiction is on Sanaa's desk and is not
resolved here.**  This mesh follows the frozen §5.6/§7.4 value.  If it is
resolved the other way, these meshes must be re-emitted and `Aref` set to
`c · t_z` to match; the emitted mesh is otherwise unaffected, because with
`front`/`back` declared `empty` OpenFOAM discretises no z-direction flux and the
solution is invariant to `t_z` — it enters only the face areas that the force
integration uses.  (That last is a statement about OpenFOAM's empty-patch
treatment, not a measurement made on this box.)

## 11. Status

**`PENDING` — this is a mesh, not a result.**  No solver has been run on it.  No
gate of the fixed vocabulary attaches to any number in this certificate other
than the §4.5 `checkMesh` gates recorded in §6 above.
