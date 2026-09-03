# ⚠ THE A1 2-D TEMPLATES' BOUNDING PLANES WERE CHANGED `symmetry` → `empty` BY COMMIT `d3f47bfa`, **AND THAT COMMIT IS NOT YET VERIFIED**

**Status: UNVERIFIED. Verification is registered, frozen and not yet run.**
**Read this before treating any case built from these templates as verified on patch identity.**

This is the reciprocal end of a condemnation clause. The other end is
`cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_PREREGISTRATION.md` §3b. Until this
session, the clause stood only in the commit message and in one board block — reachable only by
someone who already knew to run `git show`. This file is what a person opening a template finds.

---

## THE COMMIT

**`d3f47bfa50944c466ff0bad019b36a7b048a0fae`** (2026-09-03, dafoam), 41 files across three
templates:

- `cases/dafoam/work/NACA0012_Airfoil_Incompressible`
- `cases/dafoam/work_refined/NACA0012_Airfoil_Incompressible_probe`
- `cases/dafoam/work_refined/NACA0012_Airfoil_Incompressible_refined`

In each: `system/createPatchDict`'s `patchInfo` type for `symmetry1` and `symmetry2`, **and every
`0/` and `0.orig/` field file declaring those two patches**. A patch cannot be `empty` in the mesh
and `symmetry` in the field — OpenFOAM refuses the combination — so they are one logical change.

| object | md5 | patch type at lines 29 / 43 |
|---|---|---|
| `system/createPatchDict` at **`d3f47bfa^`** (before) | `5e89709961881491e3f05dc97bbcf75c` | `symmetry` |
| `system/createPatchDict` at **HEAD** (after) | `b06b32856f75d4813a763af819b6149c` | `empty` |

**Forward-only.** No run root was touched, no frozen registration re-pointed, nothing re-run. No
frozen registration anywhere pins the `5e897099…` md5; `D8R` names a *different* `createPatchDict`
(`5ef8b5ece78a1305cc9c5e2f85288924`), untouched by this commit.

---

## WHY IT WAS LANDED UNVERIFIED, AND IT SAYS SO IN ITS OWN MESSAGE

The verification requires **building a mesh in a container** and reading back both the patch types
and a solution-directions line reading `2` and `(1 1 0)`. **Launches in this family are
daemon-only**, and no agent invokes a driver, launcher or container outside the queue daemon to
test its own arithmetic. What was verified at the commit is **static only**: the byte change is
complete, self-consistent between dict and fields, and no `type symmetry;` survives on those two
patches in any of the three templates.

**What is unverified, precisely: that DAFoam's adjoint and IDWarp mesh warping accept `empty`
bounding planes on this case family.** The templates carry an **OpenFOAM v1812** header against the
image's v2506, which is evidence — **INFERRED, nothing fetched** — that `symmetry` came from the
upstream DAFoam tutorial rather than from this lab. If upstream chose it deliberately because the
adjoint or the warping requires it, `empty` will not survive contact with IDWarp.

**The upstream attribution is INFERRED and is `NOT FILED`.** Filing anything upstream is Sanaa's
decision alone (rule 7). **SUBMISSIONS PARKED.**

---

## THE CONDEMNATION CLAUSE, REGISTERED BEFORE ANY COMPUTE

> **A `GATE FAIL` on `G-DIRN.E` or `G-U2.E` in `A1ZE`, or a `G-EMPTY` `BLOCKED` on either
> treatment arm, CONDEMNS `d3f47bfa50944c466ff0bad019b36a7b048a0fae`, WHICH IS THEN REVERTED
> FORWARD.**
>
> No case built from these templates between `d3f47bfa` and A1ZE's verdict may be treated as
> verified on the patch-identity point.

**What a `GATE FAIL` condemns it FOR — narrowly, and this matters:**

| gate | what a FAIL means |
|---|---|
| `G-DIRN.E` | the solver still reports **3 solution directions** on a mesh the commit made `empty` — **the byte change did not reach the solver's mesh** |
| `G-U2.E` | a **`U2` equation is still assembled and printed** — the z-momentum equation is still solved on a one-cell layer, so the commit did not do the one thing it was made for |
| `G-EMPTY` `BLOCKED` | the mesh could not be built, or **IDWarp / the adjoint refused `empty`** — the upstream-deliberate hypothesis confirmed |

**⚠ WHAT IT IS NOT CONDEMNED FOR, AND THIS IS A CORRECTION MADE BEFORE A1ZE FROZE:** *failing to
change convergence, failing to lower a declared residual, or failing to move `CL`/`CD`.* It was
measured (A1ZE §1a, from D19T's `T08`/`T10`/`T12` logs and extended to A1WR's `sweep_I`) that
**`U2` is not in the quantity the solver declares convergence on** — `T10` declared 22 times at
~9.04e-11 while `U2`'s best over the whole run was 1.716383e-10 — and that **all 14 A1WR α points
miss 1e-8 even with `U2` excluded**. Removing a channel that was never in the criterion cannot
change the criterion. **A gate keyed to that effect would have condemned a correct commit for
failing to do something it was never able to do.** No such gate exists.

**Independent of every gate:** a one-cell-thick 2-D mesh should carry `empty` bounding planes.
The change is very likely right on its own merits; it is simply not yet verified in this box.

---

## ⚠ A DEFECT IN THE COMMIT MESSAGE ITSELF, RECORDED HERE BECAUSE HISTORY IS NOT EDITED

`d3f47bfa`'s message names *"`A1ZE`'s **MESHA**/`Ec` arms"* as its verification. **`A1ZE` has no
arm called `MESHA`** — its arms are `Sc`, `Ec`, `S3`, `E3`. `MESHA` belongs to a different item
(`A1WCT`). **The arms that actually verify this commit are `Ec` and `E3`**, the two treatment arms,
which are built from the HEAD templates **with no modification whatever** — that is what makes them
a test of the commit rather than of a hand-patch.

---

## WHAT IS AND IS NOT RETROFITTED

**Continuation phases of in-flight items are NOT retrofitted** — `D12R` phases 3/4 and `W2R`
phase 2 inherit their `symmetry` mesh deliberately, because rebuilding a mesh mid-item would be a
two-variable change inside one item. They carry the defect as a **recorded prediction** on their
queue rows.

---

**Verification item:** `A1ZE`, frozen 2026-09-03,
`cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_PREREGISTRATION.md`.
Grading path `a1ze_grade.py`, md5 `9b755c3b1a043879a664853a3d747c53`.
**Not launched. Not queued.** Its queue row is parked beside it and enters the queue only on
`dafoam-supervisor`'s personal check-4 sign-off.

**SUBMISSIONS PARKED. Nothing here is sent, filed, uploaded, registered, posted or commented
outside this box.**
