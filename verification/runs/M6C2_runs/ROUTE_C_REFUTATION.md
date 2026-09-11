# M6 ROUTE (c) — **TERMINATED BY MEASUREMENT. THE FAR-FIELD MARCHING MECHANISM IS INTRINSIC TO THE EXTRUSION, NOT AN ARTIFACT OF A3's SURFACE.**

**`M6C1` verdict: `BLOCKED` — UNCHANGED.** Nothing here alters a gate, threshold, cap,
band or label. This file records **what route (c) established** and why no L3 was built.

## THE FINDING

**The over-gate non-orthogonality that route (c) was built to escape is a property of
pyHyp hyperbolic extrusion at `marchDist` = 12 on a wing O-mesh, and it is located in the
FAR FIELD. It has now been produced on TWO DIFFERENT BODIES.**

| mesh | body | max non-orth (gate 70) | over-gate faces | where |
|---|---|---:|---:|---|
| `ROUTE_PROBE` | **A3's** M6 surface | **80.3435** | 11,571 | **100 % beyond r ≥ 2 m** |
| route (c) **L1** | **our own** AR-138 body | 66.4228 | **0** | — |
| route (c) **L2** | **our own** AR-138 body | **74.6431** | 1,019 | **99.41 % beyond r ≥ 2 m** |

**`L1_RESULT.md` read L1's zero as showing the probe's sheet was *"specific to A3's
surface, not intrinsic to marching a wing O-mesh at N = 33 / marchDist = 12."* That
reading is REFUTED by its own family's next level.** The mechanism was never absent from
our body — **it was below the resolution of the level it was read on**, and a ×1.5 march
refinement resolved it.

**🔴 A MECHANISM ABSENT AT ONE LEVEL AND PRESENT AT THE NEXT WAS NOT ABSENT. IT WAS
UNRESOLVED.** This was catchable only by building L2, and it is the whole return on
having built it.

## 🔴 THE SCOPE OF THE CLAIM, STATED NARROWLY ON PURPOSE

**This finding covers the hyperbolic-extrusion routes ONLY — the probe and route (c) —
and it must not be widened to "all three topologies failed the same way." They did not:**

| topology | method | how it failed | **same mechanism?** |
|---|---|---|---|
| 1 | structured O-grid + flat cap by interior fill | 66.57 → **70.99**, worsening; **all 72 over-gate faces at L2 are the ONE nose-lens corner** | **NO — a corner, not the far field** |
| 2 | rounded tip by collapsing the O-ring | hole in the boundary, 566 cells at openness 1, **179.77°** — not closed at all | **NO — a broken mesh** |
| 3 / probe / route (c) | **pyHyp hyperbolic extrusion** | **far-field over-gate sheet, r ≥ 2 m** | **YES, on two bodies** |

**Topology 1 and route (c) both cross the same gate between L1 and L2 at almost the same
L1 value (66.57 and 66.4228) — and they do it by DIFFERENT MECHANISMS IN DIFFERENT
PLACES.** Reading those two as one failure would be a coincidence of numbers mistaken for
a shared cause. The shared-mechanism claim is made for the extrusion routes and for
nothing else.

## WHY NO L3 WAS BUILT — AND THE COST WAS NOT THE REASON

**L2 is inadmissible.** `MESH_STANDARD` §3.1 sets a **hard gate of 70** on max
non-orthogonality; L2 measures **74.6431**, and §3.1's action is *"above 70, no validated
force from this mesh."* §8.1 requires a mesh ladder to be **"SHOWN ADMISSIBLE against the
gates that registration will carry"**, and this family cannot be — **L2 is over the gate
whatever L3 would show.** §8 was itself ruled on the **F1 ONERA M6 ladder**, which failed
the same §3 gate and could not be repaired by amendment.

**Completing Axis B would fill in a table about a family that cannot yield a validated
result.** The partition's six unreachable cells are a real loss and are recorded as one —
but reaching them is **not** a verification purchase.

**⚠️ TWO PRECISIONS, BECAUSE THE RECORD SHOULD NOT INHERIT AN OVERSTATEMENT.**
1. **No clause reads "a triple one of whose levels is inadmissible cannot be graded."**
   §3.1 caps trust and forbids a validated force; §8.1 requires admissibility before a
   freeze. The conclusion follows from those two, and is stated as following from them
   rather than quoted as a rule that does not exist.
2. **The F1 precedent is not identical.** F1 was inadmissible **at every level**
   (84.64 / 86.02 / 86.78°). Route (c) **clears at L1** and fails at L2. The families
   differ; what they share is that neither can be shown admissible throughout.

**§A4.4's 300 core-min cap was NOT the deciding factor and was not stretched.** The cap
could not have held L3 — `MP/L3_COST_FIT.md` fits L3 at **380.6–398.8 core-min** against
~191 remaining — but **the route ends on the gate, not on the budget.** Recording the
convenient reason as the true one would misstate why this stopped.

## WHAT THE NEXT ATTEMPT IS TOLD NOT TO TRY

- **Do not re-run pyHyp hyperbolic extrusion at `marchDist` = 12 on this O-mesh topology
  expecting the far field to clear.** Two bodies, three meshes; it does not.
- **Do not read a single level's clean non-orthogonality as evidence the mechanism is
  absent.** L1 read **zero** over-gate faces, under a *controlled* zero — four non-empty
  sibling sets proved the set-writer could see faces — **and the zero was still
  resolution-limited.** A controlled zero is evidence that the reader worked, **not that
  the mechanism is absent at finer resolution.**
- **The tip trailing-edge corner is a SEPARATE and unresolved defect.** Exactly 2 skew
  faces at both levels, at the same physical point to **3.83e−05 m**, magnitude falling
  4.90021 → 4.15016. It is not what stopped route (c) and it is not solved.

## ARTIFACTS

`MP/L1_RESULT.md` (`9572e4f42`), `MP/L2_RESULT.md` and `MP/L3_COST_FIT.md` (`a64a0840f`),
`MP/L2_L3_OUTCOME_PARTITION.md` (`9651f6cc4`, frozen before either build),
`ROUTE_PROBE/PROBE_RESULT.md`, `verification/campaign/M6C1_PREREGISTRATION.md`.
Cost calibration row `C-20260911T184518.275220Z-a187f375`.

**Route (c) spend ≈ 109 core-min of the 300 registered; derived $0.093 — DERIVED, NOT
MEASURED.** L3 unbuilt: `MP/L3/` does not exist.

---

## ADDENDUM 1 — 2026-09-11. **THE `SUBOFF_A1` PRECEDENT, ADDED AFTER VERIFICATION — AND IT SHARPENS THE §3.1/§8.1 POINT RATHER THAN REPLACING IT.**

The body of this file rests on F1 and deliberately omitted a SUBOFF precedent, because
the SUBOFF rung this lane checked — **`R1b`** — does not support it:
`SUBOFF_R1b_RESULTS.md:265` says its `NOT A RESULT` *"stands on rule 5 clause 1 alone"*,
a non-converged level, not a mesh-admission failure. **That check was aimed at the wrong
rung.** The precedent is **`SUBOFF_A1`**, verified here directly:

- `SUBOFF_A1_PREREGISTRATION.md:388` — *"**`PASS` iff M-a, M-b, M-c and M-d all hold at
  L1, L2 and L3. Any limb failing at any level ⇒ `GATE FAIL`, and no solver is launched.**"*
- `:1000` — **L1, 3,268,613 cells, min cell determinant `8.6227045e-04`**, below M-d's
  registered floor of `1.0e-03`. **A mesh-admission failure at L1 ended the family with no
  solver launched, regardless of what L3 would have shown.**

**That is the closer structural parallel to route (c) than F1, and it is added here.**

**🔴 BUT IT DOES NOT RETIRE §5's SECOND PRECISION — IT EXPLAINS IT.** A1 could stop on
*"any limb failing at any level"* because **A1 REGISTERED that rule in its own
pre-registration.** It is a **per-registration limb, not a lab-wide clause.**
**`M6C1_PREREGISTRATION.md` registers no such limb**, so route (c)'s conclusion still
cannot be quoted from an any-level rule — **it follows from `MESH_STANDARD` §3.1 (hard
gate 70, no validated force above it) and §8.1 (a ladder must be SHOWN ADMISSIBLE), which
is how the body of this file states it.** A1 shows what the lab does when the rule *is*
registered; it does not supply the rule where it is not.

**The lesson underneath both corrections is the same in both directions: a precedent
checked costs a minute, and a precedent taken on trust propagates.** This lane checked a
supervisor's citation and found the wrong rung; the supervisor checked this lane's
correction and found the right one. **No gate, threshold, cap, band or label is altered.**
**Lines whose number changed above this section: 0.**
