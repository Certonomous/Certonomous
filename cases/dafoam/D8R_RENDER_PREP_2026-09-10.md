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

---

## ADDENDUM 1 — 2026-09-10 — **SETTLED: the graded optimum's FLOW FIELD was never written. Its GEOMETRY was. That distinction is what the demo can be built on, and it is proven exactly.**

*lines whose number changed above this section: 0.* Appended; nothing above rewritten. Still **no verdict
claimed** — this is demo preparation. Zero solver compute; reads only. Original run root **re-verified
identical** (3151 files, sha256 manifest matches the pre-work baseline).

### THE ANSWER

**No time directory in O-P carries `CD_final = 0.0386386731443733`.** That design state was evaluated and
never written to disk. **`0.002` is the ENDPOINT, not the optimum.** My open item is closed in the
direction I flagged as legitimate: *the optimum's fields were never written.*

**AND THE CORRECTION THAT RESCUES THE DEMO: `0.002` still carries the OPTIMAL GEOMETRY.** `CD_final` and
`CD_endpoint` are **two primal solves at the SAME design**, not two designs.

### HOW IT WAS ESTABLISHED — three independent legs

**(1) `OptView.hst` is a SQLite database** (pyOptSparse 2.10.1 `History`; table `unnamed`, key → pickled
value), read read-only — **not** a pickle, as I had assumed. 36 records, **9 major iterations (0–8)**, four
records per iteration. `optTime = 4166.29 s`. Per-iteration CD: `0.03875568695691427`,
`0.038768215028677895`, `0.03867636310877341`, `0.03865068197917615`, `0.03864959515523057`,
`0.03864106044740419`, `0.03864114691440647`, `0.038639114803429714`, `0.03863519206490339`.
**None of the nine equals `CD_final`, `CD_endpoint` or `CD_start`.**

**(2) The counters, evidenced rather than inferred.** The log holds **16 primal blocks of 101 `CD:` prints
= 1616**, matching the total exactly. Blocks 0–3 are the cold primal plus three CL-trim primals; block 4 is
`CD_start`; blocks 5–13 are major iterations 0–8; **block 14 is `CD_final`**; block 15 is `CD_endpoint`.
The 20 time directories are written as **10 pair-events** (members 7–9 s apart, ~420 s between pairs), so
the time counter advances **once per primal and once per gradient evaluation** — one pair per major
iteration, plus one for the endpoint. **Cross-checked on O-S: 28 times → 13 geometries at `n_iter=12`.**

**(3) The decisive timing.** Placing each block on the wall clock by OpenFOAM's own `ClockTime`, every pair
write follows its block's end by **9–11 s, ten times consecutively**. Block 13 (iter 8) ends 23:36:49 →
`0.0018`/`0.0017` at 23:36:58. **Block 14 (`CD_final`) ends 23:43:16 → NO WRITE.** Block 15
(`CD_endpoint`) ends 23:43:45 → `0.002`/`0.0019` at 23:43:55. All 20 directories are accounted for by the
ten pairs, and neither pair 9 nor pair 10 was overwritten. `CD_start` (block 4) likewise wrote nothing.

### GEOMETRY IDENTITY — VERIFIED BY ME, WITH A READER SHOWN ABLE TO SEE A DIFFERENCE

The `points` **bodies** (header stripped) at `0.0017`, `0.0018`, `0.0019`, `0.002` are **byte-identical**;
geometric max displacement across those four times is **exactly 0.0**. My own independent read, stripping
from the first `(`:

| time | points-body md5 |
|---|---|
| `0.0001` (baseline, twist = 0) | `cb623834994bf5084367f3d194bfe3ff` |
| `0.001` | `7a66ebf8bbd6219bbba24911b25d8d02` |
| `0.0015`, `0.0016` | `62e79d1e42bb1a2a54be900716bd6d5c` |
| **`0.0017`, `0.0018`, `0.0019`, `0.002`** | **`1171263da2fd35e7eefb9d385e46b18d`** |

**PLANTED CONTROL (rule 3):** the same reader returns **DIFFERENT** digests for the baseline, an
intermediate design and the final one, and returns the paired equality at `0.0015`/`0.0016` that the
pair-write rule predicts. **So the four-way equality is a property of the geometry, not a blind reader.**
*(My digest differs from the lane's `67e9504a…` because we strip the header differently; what I verified is
the equality relation and the reader's discrimination, not their digest value.)* The flow **fields** at
those four times do differ (max |ΔT| 1.6 K, |Δp| 43 Pa, |ΔU| 11.6 m/s) — separate primal solves on one
design, exactly as claimed.

### A CORRECTION TO MY OWN LEAD, recorded because I sent the lane after it

I pointed at `divergence_shipped_vs_patched_CD_endpoint` and its note *"different endpoints; a reading"* as
support for the endpoint/optimum distinction. **It is not.** Read in full, its five entries compare
**adjoint derivatives** `J_shipped` vs `J_patched` per twist index, and "different endpoints" is a
**cross-arm** statement — O-S and O-P converged to different final designs — **not** a within-arm
`CD_final` vs `CD_endpoint` one. **My conclusion was right and my stated reason was wrong.** The real
evidence is the missing block-14 write.

### THE CAPTIONS, RESOLVED UNDER THE RULE

The rule bites on **both** renderable frames — neither carries a graded CD:

- **`0.0001`** → *"Baseline design — twist = 0°"*, **no CD number**. Its CD is `0.038755687`; the graded
  `CD_start` `0.038756491279745384` belongs to an earlier, unwritten primal (they part at the 7th
  significant figure).
- **`0.002`** → *"Final evaluated design — optimised twist"*, **no CD number**.
- **AND THE STRONG, HONEST FRAMING:** `0.002` **may** be captioned as **the optimised geometry**, because
  geometric identity with the optimum is proven exactly (0.0 displacement) and the deformation is real
  (max point displacement `0.0431`, all 45,104 points moved). **The graded numbers go in a text panel
  sourced from the grade json** — `CD_start 0.038756491279745384 → CD_final 0.0386386731443733`,
  **−0.3025 %**, CL held to `4.88e-06` — **bound to the record, not to a rendered frame.** That satisfies
  the rule without giving up the result.

### STILL UNVERIFIED, and the first two are the honest limits of the above

- **Per-iteration design variables were NOT extracted.** The history's keys are `dvs.twist` / `dvs.patchV`;
  a first extraction returned empty and was not re-run. **So it is NOT confirmed from the history that
  iteration 8's DVs equal `dvs_final`.** Design identity was established **geometrically instead** — the
  stronger evidence for a rendering question, but a different claim.
- **"No write for block 14" rests on a timing signature**, not on a log line saying so: ten consecutive
  9–11 s latencies, a clean 39 s outlier, and a complete accounting of all 20 directories. **No explicit
  suppression statement was found in the runScript**, and the DAFoam write-trigger logic was not located.
- **Why `CD_final` differs from every recorded major-iteration objective is NOT explained.** It is the
  state reported at `run_driver_done` (`wall_s=4196.45`), a 15th primal after the last major iteration;
  what triggered that extra evaluation was not established.
- **`dvs_final` membership in the grade json is unconfirmed** — only `CD_final` and `CD_start` are known to
  appear. If the demo captions the twist distribution, check that first.
- **No renderer has opened these fields.** Verification remains numerical read-back only.

### COST

This phase reads only: ≈150 wall s, 1 rank, **≈2.5 core-min**. **Cumulative with reconstruction: ≈350 wall
s ≈ 5.8 core-min ≈ $0.005 DERIVED, NOT MEASURED** at $0.0513/core-h. **Zero solver compute. 0 GPU-h.**
