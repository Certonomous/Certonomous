# D8R (A6 CRM wing-body) — RENDER PREPARATION — 2026-09-10

**Not a graded result. No gate was pre-registered for this work, so it claims NO verdict from the fixed
vocabulary.** Demo preparation under Sanaa's 2026-09-10 3D-demo direction. `[lab-attributed]`.

**THE BANKED TWO-ROW `PASS` IS INTACT AND THAT WAS THE POINT.** The graded run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/` was **not written to**. Verified twice,
independently: the lane hashed all **3151** files before and after and the sha256 manifests match (it
probed its own comparator by flipping one character, so the match is not a blind zero); and I checked
separately that the **newest file anywhere under the root is `CHAIN_DONE` at 2026-08-28T02:13:30Z**, with
**zero files touched today**.

> **A correction that is MINE, recorded rather than quietly dropped.** I flagged *"6 files newer than the
> grade stamp"* against the lane's *"0"*. Chasing it: all six sit within **0.02 s** of the stamp and are
> the grader's own outputs — its two planted-control records, the grade `.json`/`.out`, `STATUS.chain`,
> `CHAIN_DONE`. The grade file reads as newer **than itself** because `stat -c %Y` truncates to the whole
> second while `find -newermt` compares sub-second. **The lane's reading was right in substance and my
> flag was my own rounding artifact.** My digest reader was planted-controlled in the same invocation
> (untouched copy → MATCH; one appended byte → DIFFER), so its zeros mean something.

## STATE LINES

| item | state |
|---|---|
| render copy | `/home/ubuntu/certonomous-runs/D8R-RENDER-COPY-20260910T165135Z/` — 432 M copied, 750 M after reconstruction; free disk 121 G |
| `reconstructPar` | `INNER_RC=0` ×3, rc captured **inside** the container; `End` line each; image `dafoam-idwarp-rot:v1` (`2927768a16ac`, the row D8R **bought**), OpenFOAM v2506 |
| reconstructed | **O-P 20/20 and O-S 28/28** flow times, 0 failed checks, 0 times missing a mesh |
| mesh | 41,760 cells / 45,104 points / 128,574 faces; patches `wing` (wall, 2784), `inout` (2784), `sym` (symmetry, 1020) |
| deformation | max point displacement **0.0431** mesh units, **all 45,104 points moved**, every time's mesh md5 distinct — the twist animates |
| geometry pinned to the verdict | the grade's `mesh_points_md5` `11b84f0de5fdf2d3e947fee8cea412a9` (the `G-M2` identity gate, identical across all four arms) **is** the md5 of `constant/polyMesh/points.gz` |
| cost | **4.0 core-min** (200 timed wall s + verification reads, single rank — `reconstructPar` is serial) → **$0.0034 DERIVED, NOT MEASURED** at $0.0513/core-h. 0 GPU-h |
| original root | **BYTE-IDENTICAL** (above) |

## THREE OF MY OWN BRIEF'S ASSUMPTIONS WERE WRONG. The lane measured instead of assuming.

1. **`base` cannot be rendered** — it has **no `processor*` dirs and no solution fields**, only setup. The
   baseline flow field was never retained in that arm.
2. **Time `0` is not a flow field** — in every arm `0/` holds uniform initial conditions (`T=300`,
   `U=(100 0 0)`, `p=101325`, `nut=4.5e-5`). **The true baseline flow is `0.0001`**, the first primal on
   the undeformed design.
3. **The mesh moves** — every flow time carries its own `polyMesh/points`, because the FFD twist deforms
   the geometry. That is what makes the demo work.

## THE READ-BACK CONTROL, quoted because it is the right instrument and generalises

`rc=0` was **not** trusted. Every reconstructed field was read back and required to satisfy three clauses
jointly: parses as `nonuniform`, `n_entries == 41760` (= `nCells` from the mesh header), and **`spread > 0`**.
The third clause exists because of a **plant**: a synthetic all-zero field of the correct length returns
`status=OK, n_entries=41760, spread=0.0`. **An existence-and-length check passes that.** Only `spread`
catches it. An empty body returns `EMPTY_BODY`; an absent file returns `ABSENT`; the real field returns
`spread = 72.01` K. **The discriminating channel is `spread`, not `status` — `status=OK` alone would have
been a false green.** Sample at the O-P terminus: `T` 261.4–333.4 K, `U` −146.8–399.8 m/s,
`p` 60887–151809 Pa, `rho` 0.722–1.638.

## RENDERER ENTRY POINT

- **Case:** `…/D8R-RENDER-COPY-20260910T165135Z/O-P/` (stub `d8r_OP.foam`; O-S has `d8r_OS.foam`)
- **Before/after pair: `0.0001` vs the terminus — NOT `0` vs the terminus** (see assumption 2)
- **Animation:** all 20 O-P times (28 for O-S) are continuous and each carries its deformed mesh
- **Renderable fields:** `p`, `U`, `T`, `nut`, `rho`. `phi`/`meshPhi` are **surface** fields (121,986 faces),
  not volume-renderable
- **Degenerate — do not colour by it:** `betaFINuTilda` is `uniform 1` everywhere at every time (the FIML
  correction field, never activated in this run). It renders flat
- Reconstructed files are owned by `root` (the container wrote them), mode 644 — readable, not overwritable

## OPEN, AND IT GATES WHAT MAY BE CAPTIONED

**The last time directory is NOT established to be the graded optimum, and there is positive evidence it
is not.** `O-P/d8r_O.json` carries three distinct values:

    CD_start    = 0.038756491279745384
    CD_final    = 0.0386386731443733       <- the GRADED optimum (matches the grade json's PATCHED terminus)
    CD_endpoint = 0.038637615752119894     <- a DIFFERENT value

**`CD_final` != `CD_endpoint`**, diverging at the 6th significant figure; and the grade json's own
`divergence_shipped_vs_patched_CD_endpoint` field is annotated *"different endpoints; a reading"*. O-P has
**20 flow times** against a graded **`n_iter=8`**, so the time counter and the major-iteration counter are
**not the same counter** and the mapping is unevidenced. The lane separately found the graded `CD_final`
at index **1514 of 1616** `CD:` prints — **not the last**.

**CAPTION RULE, imposed either way:** a demo frame may carry a CD value **only if that value is read from
the graded record**. Any other frame is captioned *"final evaluated design"* or carries no number.
**Captioning the last frame "the optimum" would publish a number that is not the graded one** — which is
exactly what a filmed demo must not do. Lane is settling the mapping from `OptView.hst`, read-only, zero
compute. **If the optimum's fields were never written as a time directory, that is a legitimate answer and
the demo is captioned accordingly.**

## WHAT IS STILL UNVERIFIED

- **No renderer has opened these fields.** Verification is numerical read-back only; ParaView ingesting the
  moving-mesh time series without complaint is **unconfirmed**.
- **The arm→row mapping** (O-P = PATCHED at `n_iter=8`, O-S = SHIPPED at 12) rests on the grade file alone;
  not independently corroborated.
- **`F-P`/`F-S` not reconstructed** — deliberately: they are finite-difference gradient references, not
  renderable trajectories. ~3 time dirs each, trivial to add.
- **`CASE_PROTOCOL_CHARTER.md` is still not at HEAD**, so its stage mapping for this work is VERIFY.
