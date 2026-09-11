# DrivAer `snappyHexMeshDict` — MTIME MANIFEST

**Why this file exists.** The seven dicts listed below are the entire
configuration record of the DrivAer meshing defect this team is triaging, and
until the commit that carries this manifest they were **untracked** — not
gitignored, merely never committed. Their build chronology survived only in file
mtimes, which **git does not preserve**. One `cp -r`, one archive-and-restore, or
the commit itself would have destroyed the ordering that makes them evidence.

**This manifest is the chronology.** The dicts carry the content; this file
carries the timestamps, byte sizes and hashes that bind each dict to the build it
configured. Read the two together or neither is evidence.

Captured 2026-09-11 by the cfd lane, immediately before the commit that first
tracked these files. Every value below was read off the live filesystem.

## The seven dicts, in build order

| mtime (UTC, to the second) | bytes | sha256 (first 16) | `addLayers` | path |
|---|---|---|---|---|
| `2026-09-10T21:37:14Z` | 10011 | `e19b25ff08d97cfe` | **true** | `DIAG_v1_coarse_explicitSnap_tol2_noCarLayers/system/snappyHexMeshDict` |
| `2026-09-10T21:46:06Z` | 9717 | `b7ec145a5c38abbf` | **true** | `DIAG_v2_coarse_implicitSnap_tol1_layersON_BROKEN/system/snappyHexMeshDict` |
| `2026-09-10T21:46:07Z` | 9717 | `544aa1c445c79564` | **true** | `DIAG_v3_coarse_explicitSnap_tol2_layersFixed/system/snappyHexMeshDict` |
| `2026-09-10T21:50:21Z` | 9718 | `efc2c69114689a3b` | **false** | `r1_coarse/system/snappyHexMeshDict` |
| `2026-09-10T21:54:59Z` | 9718 | `efc2c69114689a3b` | **false** | `r1_medium/system/snappyHexMeshDict` |
| `2026-09-10T21:55:00Z` | 9718 | `efc2c69114689a3b` | **false** | `r1_fine/system/snappyHexMeshDict` |
| `2026-09-10T23:15:40Z` | 9718 | `8341c0060fe3d317` | **true** | `DIAG_v5_coarse_layersON_mergeTol1e-8/system/snappyHexMeshDict` |

Total: 7 files, 68317 bytes.

## Two facts that only this table shows

**1. The three graded levels share ONE dict, byte for byte.**
`r1_coarse`, `r1_medium` and `r1_fine` all hash to `efc2c69114689a3b` at 9,718
bytes. The graded family was not three independent configuration decisions; it
was **one decision taken at 21:50:21 and propagated** to medium at 21:54:59 and
fine at 21:55:00. (Consistent with `level (4 4)` being constant across the
family while the base block refines — the snappy dict genuinely does not need to
differ between levels.)

**2. `addLayers` was turned off 2m18s after the third consecutive collapse.**
The three `addLayers true` diagnostics ran 21:40:11 -> 21:48:04 and **all three
produced 0 % layers**. The single graded dict, with `addLayers false`, was
written at **21:50:21**.

## The decision itself

`diff DIAG_v3_coarse_explicitSnap_tol2_layersFixed/system/snappyHexMeshDict
r1_coarse/system/snappyHexMeshDict` — the complete change made at 21:50:21, four
lines in three hunks:

    12c12
    < addLayers       true;
    ---
    > addLayers       false;
    183c183
    <     tolerance       2.0;
    ---
    >     tolerance       1.0;
    187,188c187,188
    <     implicitFeatureSnap false;
    <     explicitFeatureSnap true;
    ---
    >     implicitFeatureSnap true;
    >     explicitFeatureSnap false;

So the 21:50:21 edit did **two** things: it turned layers off, and it reverted
snapping from explicit/tol 2.0 back to implicit/tol 1.0 — i.e. it reverted the
`DIAG_v3` "layersFixed" experiment wholesale and returned to the `DIAG_v2`
snapping settings while additionally disabling layers.

## What this evidence does and does not establish

**Does NOT establish** causation or intent. An mtime ordering is sequence, not a
reason. Nobody may cite this manifest as showing that `addLayers false` was
chosen *because* layers failed.

**Does establish** that the sequence is the one that hypothesis predicts and not
the one the competing explanation predicts: an independent design decision has no
reason to land two minutes after three consecutive collapses, nor to arrive as a
single propagated file rather than three considered ones.

The hypothesis is registered — not promoted — in
`verification/campaign/DRIVAER_LAYERFIX_PREREGISTRATION.md` §5 and Amendment 1.
**Arm A1 of that registration is its real falsifier.**

## Standing caution for anyone who edits these files

Git does not preserve mtime. From this commit forward the filesystem mtimes of
these seven dicts are **no longer trustworthy as build chronology** — a checkout,
clone or copy rewrites them. **This manifest is the record.** If a dict is
edited, append a new dated row here rather than relying on the filesystem.
