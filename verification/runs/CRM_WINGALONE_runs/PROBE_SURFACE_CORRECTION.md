# 🔴 CORRECTION TO THE FROZEN REGISTRATION §6 AND §7 — THE PROBE RAN ON THE **L3** SURFACE, NOT `A6`

**The frozen document is NOT edited (rule 6).** This is a separate measured record. Whether it
becomes a dated addendum is the supervisor's call, not this lane's. **It alters no gate, threshold,
cap or label** — see "consequences" below, where every affected number moves in the SAFE direction.

## What the registration says

> *"The probe ran at `N` 53 on the **`A6`** surface (579,072 cells)"* — §7
> *"the `59dfc5232` route probe marched **579,072** volume cells for ~7.5 core-min at 1 rank ->
> **12.952 core-min/Mcell**, and wrote **282.5 bytes/cell**"* — §6

## What is on disk

| evidence | value |
|---|---|
| `PYHYP_ROUTE_PROBE/work/surfMesh.cgns` md5 | **4793fe5bee90** |
| `COARSEN_PROBE/src/ACT9_CRM_surfMesh.cgns` md5 | **4793fe5bee90 — IDENTICAL** |
| `COARSEN_PROBE/src/A6_surfMesh.cgns` md5 | 8f6ed3c37ea5 — different |
| `PYHYP_ROUTE_PROBE/work/pyhyp.log` header | **Total Nodes 46762, Unique Nodes 44681, Total Faces 44544** |
| census of `ACT9_CRM_surfMesh.cgns` (this lane) | **46762 / 44681 / 44544 — EXACT MATCH** |
| census of `A6_surfMesh.cgns` (this lane) | 12258 / 11205 / 11136 — no match |

**Two independent identifications agree: a byte-identical file, and the solver's own printed node
and face counts.** The probe marched the **44,544-cell `ACT9` surface — which is L3's surface.**

Volume cells actually marched = 44,544 x 52 = **2,316,288**, not 579,072.
**579,072 = 11,136 x 52** — the figure that would be right had the surface been `A6`.

## Consequences — one root cause, one factor, both in the SAFE direction

`44,544 / 11,136 = 4`, so both §6 anchors are wrong by exactly **4.00x**, both **over-estimates**:

| §6 anchor | registered | **measured** | direction |
|---|---|---|---|
| extrusion rate | 12.952 core-min/Mcell | **3.246 core-min/Mcell** | registered is **4.00x TOO HIGH** |
| Plot3D disk rate | 282.5 bytes/cell | **70.62 bytes/cell** | registered is **4.00x TOO HIGH** |

**No gate, cap or precondition is loosened.** The registered cap of **1,464 core-min stands
unchanged** and is now known to be more conservative than it read. The §6.1 disk precondition
(~2.99 GB of volume meshes, L3 held behind >= 8 GB) is likewise conservative: the true Plot3D
requirement for all three levels is **~0.74 GB**, not 2.99 GB. *A precondition that was too strict
is a safe error; it is corrected here so the next rung does not inherit a 4x-inflated rate.*

## 🔴 THE PART THAT IS NOT BOOKKEEPING — §7's RISK POINTED AT THE WRONG END OF THE LADDER

§7 registered the risk as *"`N` 105 and 209 are untested regimes"*, reasoning from a probe believed
to sit near L1. **Corrected, the probe sat on L3's surface** — so:

- **L3's SURFACE was the proven one.** Only its `N` = 209 is new.
- **L1's 2,784-cell surface had never been marched by anything**, and neither had L2's.
- **The measured failure landed on L1** (negative min quality at layer 3), the level §7 implicitly
  treated as nearest the proven configuration.

§7's *conclusion* — *"the probe's exact configuration has never been run"* — is **correct and was
load-bearing**. Its *premise* was wrong, and the wrong premise pointed the registered risk at the
fine end of the ladder while the defect was waiting at the coarse end.
