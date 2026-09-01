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


---

## AMENDMENT 1 — 2026-09-01: PREDICTION 1 IS STRUCK AS REFUTED BY A MEASUREMENT THAT PREDATES THIS FILING, AND THE PROBE IS WITHDRAWN

**Version: v1.0 to v1.1.** v1.0 designates this document as committed at `40ca3c35`,
2026-09-01.

**Lines whose number changed above this section: 0.** Nothing above this heading has been
edited, reordered, inserted or deleted. This section is appended below the closing rule.

**THIS IS A STRIKING AMENDMENT, NOT AN IMPROVING ONE.** It does not replace a prediction
with a better one, does not move a gate, threshold, cap or label, and does not improve any
prediction's odds of scoring well. It records that a registered prediction was **already
refuted by a measurement on this box before it was written**, and it withdraws the rung.
An amendment that improves a prediction is what rule 2 exists to prevent; an amendment that
records a refutation is what it exists to permit.

### The pre-compute condition, and how it was checked

**Checked in the amending invocation itself, not recalled:** `find -type f` over
`verification/runs/F13_ONERA_M6_runs/SUCCESSOR_tip_topology_trial/` returns **0 files**. The
tree holds two empty directories (`cap_probe/`, `logs/`) and `ls` of `cap_probe/*` returns
"No such file or directory". **No candidate mesh, log or `checkMesh` output exists. First
compute has not occurred**, so amendment is lawful under CLAUDE.md rule 2.

### What was already on the record, and what this filing's author failed to do

**`N-C6` in `docs/NUMERICS_KNOWLEDGE.md`**, landed **2026-08-25 by cfd, from the ONERA M6
topology study** — three days before this filing and on this exact geometry:

> *"A structured butterfly tip cap on a SHARP trailing edge has a non-orthogonality floor
> that REFINEMENT MAKES WORSE — the maximum rises to an asymptote and the severe-face
> fraction rises an order of magnitude."*

Its measured sweep, far-field blocks already repaired so the tip cap is the only mechanism
above 70°:

| variant | cells | max non-orthogonality | severe (> 70°) | severe fraction |
|---|---|---|---|---|
| `t1_SHELL` | 111,872 | **81.5834°** | 516 | 0.158 % |
| `t6_SHELL_NR16` | 118,784 | **81.9764°** | 1,812 | 0.523 % |
| `t7_SHELL_NR32` | 128,000 | **82.0355°** | 3,636 | 0.975 % |
| `t8_SHELL_NR64` | 146,432 | **82.0645°** | 7,200 | 1.694 % |

**§7 prediction 1 of this filing reads: *"At least one of C1 / C2 clears M1, with max
non-orthogonality in 50–68°."* C1 is the butterfly cap. It was measured at 81.58–82.06° on
this geometry three days earlier. THE PREDICTION IS STRUCK.**

**The failure is mine and it is not a modelling error — it is a failure to read.** The
prediction was reasoned from the `nofill` control at 51.2554°: *"a non-degenerate cap only
has to avoid being worse than the C-grid it attaches to."* That reasoning is wrong, and
`N-C6`'s operational reading 1 says so and gives a test costing no compute at all.

**§4's candidate ordering is also struck.** This filing presented C1 as changing *topology
only* and therefore as the safe candidate, and C3 as changing *geometry* and therefore the
poor one. **The topology-only candidate is the one with the measured floor in the 80s.**
The ordering was backwards and was relayed upward before it was caught.

### The arc-length criterion, computed here, which withdraws the probe

`N-C6` prescribes: compute the strip-to-core arc-length ratio at the break; a ratio of order
10 or more predicts a non-orthogonality floor in the 80s **without building anything**. The
mechanism is at `cases/F13_onera_m6/../topology_study/gen_topo.py:26` — the TE strip joins a
surface arc of `(1 − U2)·c` to a core edge of `(1 − CORE_S)·t2(U2)·c`, with `j` turning 90°
across the block.

Computed 2026-09-01 from the registered geometry (`m6_section.py`, `t/c_max = 0.09779` at
`x/c = 0.3803`), at the registered `U2 = 0.90`, `CORE_S = 0.50`:

| x/c | 0.80 | 0.85 | **0.90** | 0.95 |
|---|---|---|---|---|
| `t2` | 0.023670 | 0.018530 | **0.012913** | 0.006961 |
| **ratio R** | 16.90:1 | 16.19:1 | **15.49:1** | 14.37:1 |

**R = 15.49:1 at the registered break — an independent reproduction of `N-C6`'s recorded
"~16:1" by a separate route.**

**MOVING THE BREAK DOES NOT ESCAPE IT.** R is nearly flat in `U2`: **18.28:1 at 0.70 falling
only to 14.37:1 at 0.95.** Because `t2 → 0` at a sharp trailing edge, the numerator and
denominator shrink together. **That is a property of the section, not of the block
structure, so it does not care which cap topology is chosen** — which answers C2 (the O-grid
cap with a rectangular core) without building it.

Over the natural design region — `U2` in [0.70, 0.95], `CORE_S` in [0.30, 0.70] — the
**minimum is 10.26:1**, still at or above the criterion.

### THE HONEST LIMIT OF THIS ARGUMENT, WHICH IS NOT AS STRONG AS "REFUTED FOR EVERY CANDIDATE"

**The ratio IS escapable in principle, and this amendment will not overstate the case.**
`R < 10` is reachable at the registered break by shrinking the core: **`R < 10` requires
`CORE_S < 0.2256` at `U2 = 0.90`** (R = 9.68:1 at `CORE_S = 0.20`; 8.15:1 at 0.05). So the
premise is refuted **across the registered and natural design region**, and **not** across
the entire admissible space. A cap with a core below ~23 % scale is **untested**, and this
amendment records it as an open escape rather than declaring the question closed.

**The evidence against that escape is empirical and is on record, but it is indirect:**
`N-C6`'s own two core variants moved **away** from the gate, not toward it —
`t2_SIMCORE` **87.0192°** and `t4_CORE2` **84.8750°** against the `t1_SHELL` baseline
**81.5834°**. Those varied core *shape* rather than core *scale*, so they bound the question
without settling it.

### Consequence — the probe is WITHDRAWN, not run

- **§7 prediction 1: STRUCK** (refuted by `N-C6`, which predates this filing).
- **§4 candidate ordering: STRUCK** (C1 is the measured-worst candidate, not the safe one).
- **C3 is INADMISSIBLE** on the standing `TSCALE` ruling recorded in `N-C6`: a thickened
  aerofoil is a different aerofoil, and this is a reason to change the meshing method, never
  the geometry.
- **No candidate is built. No compute is spent. Gate M is never evaluated.**
- **The rung's cost falls from a 4.0 core-min estimate to 0.0 core-min actually spent.** A
  calibration row is owed under rule 12 recording an item closed at zero spend against a
  4.0 estimate, with the reason: the answer was already on disk.

**The standing outcome for F13 is unchanged and its CAUSE is corrected:** F13 remains
**`GATE FAIL`** on the mesh standard at R0 and the case remains **`BLOCKED`** on §5
admission. What changes is the diagnosis. The earlier reading — *"two collapsed lines in our
own generator; the ONERA geometry was never the problem"* — is **too kind to the geometry**.
The collapsed lines are the *generator's* contribution and are real, but the section's
half-thickness going to **zero at a sharp trailing edge** sets an arc-length ratio that a
core-based structured cap cannot escape in the design region. **The cause is geometric, and
that makes it a finding rather than a fixable oversight.**

**What this amendment does NOT claim:** that no cap topology anywhere can mesh this wing
inside 70°. It claims that the two candidates registered here are answered — one by direct
measurement, one by a topology-independent geometric ratio — and that the named residual
(a sub-0.23 core scale) is untested.
