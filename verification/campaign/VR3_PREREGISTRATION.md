# VR3 — THE 11 ansys "SAFE" SITES: IS EACH SAFE **FOR THE REASON CLAIMED**?

**Repair-registration.** Frozen before any work under it.

## 1. The finding this repairs
`DEAD_LEVER_AUDIT` §7.4, open since `3c751f8a`. ansys's sweep classified 12 sites as
cardinality-guarded SAFE. **Reading `grade_vmfl076.py` showed the claim was wrong on the mechanism**:
it does not refuse on 40 directories, it **`float(name)`-keys and sorts numerically**, and its
`len(hits) != 1` guard covers the **inner file set — a different set** from the outer start-time
directories that carry the hazard. **So a site can carry a prominent cardinality guard and still be
unguarded on the set that decides the answer**, and whether the remaining **11** are safe for the
reason claimed is **`NOT MEASURED`**.

## 2. WHAT IS MINE
Entirely mine. This is a cross-team gate audit and the count is not in dispute — **only the reason
is**, and a reason is what a later reader relies on.

## 3. Gate (frozen)
For each of the 11 sites, a committed record stating:
- **G1** the ordered set that **decides the answer** (which glob/listdir, over what members);
- **G2** the set each `len(...)` guard in that function actually **measures**;
- **G3** whether G1 and G2 are the **same set** — the discriminator;
- **G4** the resulting class: **GUARDED** (guard covers the deciding set), **REFERENCE** (numeric key,
  reads it correctly), or **UNGUARDED** (guard covers a different set).

## 4. Threshold / label
**PASS** = all 11 classified with G1–G3 named per site. **GATE FAIL** = any site resolves to
**UNGUARDED**, which would widen ansys's exposed set beyond the ruled 19. **NOT A RESULT** if a site
cannot be read at HEAD.

## 5. Cap
**20.0 core-minutes.** Zero solver compute.

## 6. Not claimed
Nothing re-grades an ansys verdict. §7.3's finding stands: **no landed verdict is exposed**, because
every hazard case produced exactly one start-time directory. This item can only widen the
**candidate** set, never move a **verdict**.
