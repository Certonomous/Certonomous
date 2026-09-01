# F13 successor — ONERA M6 tip-topology admission probe — pre-registration

Written 2026-09-01, **before any candidate tip mesh exists**. Successor filing to
`F13_ONERA_M6_PREREGISTRATION.md` (frozen `2eabe597`, AMENDMENT 1 `3b88ab09`,
AMENDMENT 2 `73c264c3`), whose R0 rung is graded **`GATE FAIL`** and whose case is
**`BLOCKED`** on §5 admission. **That filing is closed and is not amended here.**

**Condition checked before writing, and how:** no candidate mesh exists —
`verification/runs/F13_ONERA_M6_runs/SUCCESSOR_tip_topology_trial/` contains two
empty directories (`cap_probe/`, `logs/`) and **zero files**, confirmed by a
`find -type f` returning nothing, not inferred from a directory listing.

---

## 1. The question, and why it is worth 4 core-minutes

F13 failed the mesh standard's non-orthogonality gate at every level:
**84.6437° / 86.0173° / 86.7767° against ≤ 70°**, worsening under refinement, with
severe faces rising **36 → 216 → 1,440**.

**But the failure is localised, and the localisation is already measured.** The
identical C-grid built with the tip fill omitted —
`verification/runs/F13_ONERA_M6_runs/mesh/CONTROL_nofill_L1_checkMesh.log` —
reports **max non-orthogonality 51.2554°, "Non-orthogonality check OK", zero faces
over 70°, max skewness 1.44254**. The fill alone carries the mesh from 51.26° to
84.64°.

**And the cause is a single line of topology, not a property of the wing.**
`cases/F13_onera_m6/make_blockmesh_m6.py:170-171`:

```
fpid[0, :, :]  = pid[self.i_le, 0, NSW:][None, :]     # LE line, collapsed
fpid[NA, :, :] = pid[self.i_te_lo, 0, NSW:][None, :]  # TE line, collapsed
```

The tip fill is a lens whose leading- and trailing-edge boundaries are **collapsed
to lines**. A collapsed line is a geometric singularity: the faces around it
approach 90° and get worse with refinement, which is exactly the measured
36 → 216 → 1,440 trend. **The ONERA M6 geometry is not the problem. The tip
closure topology is.**

**So the question this probe answers is narrow and decidable:** does a tip closure
**without collapsed edges** clear the lab's ≤ 70° gate on the same real geometry?

## 2. THE GATE IS NOT WIDENED, BY ME OR BY ANYONE HERE

The gate is `docs/standards/MESH_STANDARD.md` §3.1, **hard gate 70°**, basis
`nonOrthThreshold_ = 70` in the OpenFOAM v2606 source. **Retiring, widening or
narrowing a gate threshold is reserved to Sanaa** (CLAUDE.md, FIRST-ACTION RULE).
This probe either clears the standing gate or it does not, and "a demo needed a
mesh" is not a reason to move it. A mesh quietly accepted at 85° is the exact
failure this lab exists to catch.

**Equally refused, and named in advance:** shortening the wake to buy a `Mesh OK`
line. `R0_TERMINAL.md` already declined that trade — the wake's aspect ratio comes
from §5's own frozen 16m-uniform recipe and bringing it under 1000 would need the
domain cut to ~3.2 c_root behind the trailing edge, compromising the very C_D the
ladder exists to grade. **That refusal stands and this probe does not revisit it.**

## 3. Scope — mesh only

**No solver runs. No flow is computed. No force, no Cp, no verdict about M6
physics is produced or claimable from this rung.** One level (L1, the coarsest of
the F13 family), serial, 1 rank, so core-min == wall-min. Domain decomposition is
not applicable and its absence is not an omission.

Geometry: `sdk/geometry/onera_m6_wing.stl`, 12,480 triangles, with
`c_root = 0.8059 m`, unchanged from the F13 filing. **Provenance limit, restated
because it binds what may be claimed:** that STL is *derivative* of the DAFoam
tutorial; **no primary definition of the M6 planform or the ONERA D section is
held on this box** (`F13_ONERA_M6_PREREGISTRATION.md:25-30`). V and G are
unaffected by this; **P is not claimed**, here or later, on this geometry.

## 4. Candidates (all three declared now; none may be added after the first build)

| id | tip closure | why it is a candidate |
| --- | --- | --- |
| **C1** | **H-block (butterfly) cap** — the flat tip section's interior meshed as one topologically-rectangular block, LE→TE by lower→upper, every cell keeping six faces | the standard fix for a flat tip cut; no edge degenerates anywhere |
| **C2** | **O-grid cap with a rectangular core** — a contour-following ring plus a core block | keeps near-wall orthogonality at the section contour, still no collapse |
| **C3** | **the existing lens with its two collapsed lines resolved into finite edges** (one cell of blunting at LE and TE) | the smallest possible change to the existing block structure; registered so that the cheap option is tested rather than assumed inadequate |

`make_blockmesh_m6.py` is a **frozen path token** (its §9) and **is not edited**.
Candidates are built by a successor generator committed beside it. The existing
`nofill` mode is retained unchanged as the diagnostic control.

## 5. Gate M — admission, read from each candidate's own `checkMesh`

| id | check | threshold | source |
| --- | --- | --- | --- |
| **M1** | max non-orthogonality | **≤ 70.0°** | `MESH_STANDARD.md` §3.1, **unchanged** |
| **M2** | max skewness | **≤ 4.0** | checkMesh default `skewThreshold_` |
| **M3** | topologically closed and valid | all checkMesh topology checks OK; **zero collapsed faces** (fewer than 4 unique points) | the generator's own `assert len(u) == 3, "ABORT: collapsed face"` |
| **M4** | max aspect ratio | **REPORTED, NOT GATED** | §3.3 — *"advisory at 1000, never a lone rejection"* |

**M4 is reported with §3.3's compound flag evaluated explicitly**, never waived:
aspect ratio above 1000 **together with** non-orthogonality above 60° **or**
skewness above 2 is a flag for investigation. The wake cut's ~5,934 is anisotropy
aligned with a resolved direction on orthogonal cells, which is the legitimate
case §3.3 names, and the alignment justification goes on the record either way.

### Labels — fixed vocabulary, decided in advance

- **Any candidate satisfying M1 AND M2 AND M3 → `GATE REACHED`** on mesh
  admission at L1. **This means one thing only: a mesh exists that the lab's own
  standard admits.** Nothing is solved; no physics is claimed; the ladder becomes
  worth costing in a further filing under §8.1 ("build before you freeze").
- **No candidate satisfying M1 AND M2 AND M3 → `GATE FAIL`** on the mesh standard.
  **That is the finding.** It goes to Sanaa, and M6 is not filmed as a success.
- **The generator cannot execute, or the geometry cannot be read → `BLOCKED`**,
  with the reason named. An absent `checkMesh` log reads **ABSENT**, never clean.

## 6. Planted control (CLAUDE.md rule 3), on two real artifacts of known and different value

The reader that parses `Mesh non-orthogonality Max:` must be shown able to return
a non-zero, and two genuine logs already on disk carry **known, different** values:

- `mesh/m1/log.checkMesh` → must return **84.6437**
- `mesh/CONTROL_nofill_L1_checkMesh.log` → must return **51.2554**

The reader **refuses** if it returns the same value for both, if it cannot match
the pattern, or if the log is absent. **A number from a reader that cannot
distinguish those two logs is not evidence, and no candidate is graded until the
control passes.** The control is additionally required to be shown able to fail,
by the same mutation route used on `dmr_locator_v2.py`.

## 7. Predictions (scored afterwards, left as written)

1. **At least one of C1 / C2 clears M1**, with max non-orthogonality in
   **50–68°**. Basis: the nofill control already measures 51.2554° for the entire
   mesh minus the fill, so a non-degenerate cap only has to avoid being worse than
   the C-grid it attaches to.
2. **C3 does NOT clear M1**, predicted **70–85°**: one cell of blunting leaves the
   edge nearly degenerate.
3. **M4 is unchanged by any tip work at ~5,934** — it is the wake cut, not the tip
   — and **§3.3's compound flag does NOT fire** for any candidate that clears M1,
   because non-orthogonality would then be below 60 and skewness below 2.
4. Cost ≤ 5 core-min.

## 8. Budget, disqualifiers, honesty clause

| item | core-min | basis |
| --- | --- | --- |
| build + `checkMesh`, three candidates at L1 | **2.2** | R0 measured **2.18** core-min for three levels built and checked, serial |
| parser, planted control, mutation check | 0.5 | serial, no mesh built |
| one repeat build if a candidate needs a second pass | 0.7 | one level |
| contingency | 0.6 | |
| **ESTIMATE** | **4.0** | **serial, 1 rank — core-min == wall-min** |
| **HARD CAP** | **20.0** | **a breach STOPS the run and writes a breach file; it does not get a new budget** |

**Dollars are DERIVED, never measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). At $0.0513/core-h, c7a.4xlarge,
**reported-by-owner**: estimate **$0.0034**, cap **$0.0171**.

**Estimate-versus-actual calibration is owed at completion**, as a row in
`docs/COST_CALIBRATION.md` (CLAUDE.md rule 12).

**Disqualifiers.** Widening, narrowing or reinterpreting the ≤ 70° gate — Sanaa's
alone; shortening the wake or the domain to buy a `Mesh OK` line; editing
`make_blockmesh_m6.py`, a frozen path token; accepting a candidate whose
`checkMesh` log is absent or unparsed; adding a fourth candidate after the first
build; any edit to a gate, threshold, cap or label in this file after the first
build.

**What this probe buys, honestly.** **Admission, not physics.** A `GATE REACHED`
here says a mesh exists that the standard admits — nothing more. It says nothing
about whether the M6 primal converges: DAFoam's run plateaus at nuTilda
**1.02e-06 against a 1e-08 tolerance**, changing by a factor of 0.997 across its
entire final third, and that is a **separate and unresolved** question
(`A3_onera_m6_plateau.md`). It says nothing about surface pressure: the
experimental Cp comparison was moved to **`NOT A RESULT`** on 2026-08-25 because
both sides of it import station values from a document this lab does not hold, and
**no amount of compute recovers that** — obtaining the document under rule-15
title-page verification is the only route, and it is not this filing's.

**And it does not lift the router's standing policy.** `sdk/chief_engineer/router.py:567-576`
records, in the router's own voice with its branch commented out, that ONERA M6 is
deliberately not routed from the control room because *"the control room is a
promotional surface and carries only cases that reach a clean result"*. **That
policy is binding on this filing and is Sanaa's alone to lift.** It is not edited,
not uncommented, and not routed around. A `GATE REACHED` on mesh admission is
**not** the "clean result" that comment names.

---
*Nothing below this line existed when the first candidate was built.*
