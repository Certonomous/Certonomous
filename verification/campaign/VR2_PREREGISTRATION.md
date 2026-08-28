# VR2 — THE ARMING MONITOR FOR THE 9 LATENT ORDERING-KEY SITES

**Repair-registration.** Frozen before any work under it.

## 1. The finding this repairs
`DEAD_LEVER_AUDIT` §9.1. Nine sites are **LATENT**: verdict-bearing `sorted(glob)[-1]` reads whose
function-object directories are single-member **today**. §9.1 records why they are non-divergent and
the reason is **fragile**: every time value falls in 0.002–3.12 s and 4.5–6.0 s, so **no `9.x` ever
stands against a `10.x`**. That is the **value range, not the code**. A longer run arms them.

## 2. WHAT IS MINE
The sites are cfd's and dafoam's; **their repair is theirs.** **LATENT is not a resting state — it is
an unmonitored one**, and converting it to a monitored one is verification's work.

## 3. Gate (frozen)
A committed monitor under `verification/monitor/` that, over the 9 sites:
- **G1** reports, per site, the current member count of the ordered set and whether
  `sorted(kids)[-1] != sorted(kids, key=float)[-1]`.
- **G2** **FIRES** (non-zero exit) the moment any site's set becomes multi-member **and** divergent —
  the arming condition — naming the site and both readings.
- **G3** is driven with **both limbs before any zero is believed** (§2j): a planted directory set
  `{0, 950, 2000}` must fire; `{0, 100, 200}` (lexicographic == numeric) must stay silent.

## 4. Threshold / label
**PASS** = G1 reports all 9, G2 silent on today's disk, G3 both limbs behave.
**GATE FAIL** = G2 fires on a real site (a LATENT site has armed) — which is a **finding, not a
failure of this item**. **NOT A RESULT** if G3's limbs do not both behave.

## 5. Cap
**12.0 core-minutes.** Zero solver compute.

## 6. Not claimed
No site is reclassified by this item. It does not repair; it makes the arming visible.
