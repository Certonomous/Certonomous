# F1 (ONERA M6) — RUNG R0 TERMINAL RECORD

**Written ONCE, at the end of R0. Not amended, not rewritten.**
Registration `verification/campaign/F13_ONERA_M6_PREREGISTRATION.md`, frozen
`2eabe5971b1c45624c189c669b69b5f17788a56e`; AMENDMENT 1 `3b88ab09`, AMENDMENT 2 `73c264c3`.

## VERDICT

> ## `GATE FAIL` — §5 ADMISSION, AT ALL THREE LEVELS.
> ## **NO SOLVER STARTS. THIS IS A NAMED BLOCKER, NOT A LAUNCH.**

Two of the seven §5 admission channels fail at **every** level. §5's own rule applies: the
comparator **refuses to grade G on a level that fails admission**. R1–R4 are **`PENDING`** and
**not launched**. Nothing was lowered to let a run start.

## What was measured — three REAL `checkMesh` logs, `rc = 0` read from disk

| §5 channel | gate | **L1 (m=1)** | **L2 (m=2)** | **L3 (m=4)** | |
|---|---|---|---|---|---|
| cells built | 108 216 / 865 728 / 6 925 824 | **108 216** | **865 728** | **6 925 824** | **PASS** |
| max non-orthogonality | **≤ 70°** | **84.6437** | **86.0173** | **86.7767** | **GATE FAIL ×3** |
| — severely non-orth. faces (> 70°) | — | 36 | 216 | 1 440 | — |
| max skewness | **≤ 4** | **1.44254** | **1.44298** | **1.44318** | **PASS ×3** |
| `checkMesh` prints `Mesh OK` | required | **NO** | **NO** | **NO** | **GATE FAIL ×3** |
| — `Failed n mesh checks` | — | 1 | 1 | 1 | — |
| — max aspect ratio (**not gated**) | — | 5 934.1 / 4 992 cells | 6 469.0 / 40 032 | 6 748.5 / 311 216 | — |
| node nesting, read from the BUILT `polyMesh` | **≤ 1e-12 c_root** = 8.059e-13 m | L1⊂L2 **0.000e+00** | L2⊂L3 **0.000e+00** | L1⊂L3 **0.000e+00** | **PASS** |
| `r = (N_ref/N)^(1/3)` | **2.000 ± 0.002** | L1→L2 **2.000000** | L2→L3 **2.000000** | | **PASS** |
| L1 max y⁺ (**ESTIMATE**, no solve exists) | ≤ 300 | **39.72** | 18.22 | 8.74 | **PASS** |
| L3 S2 chordwise cell | **≤ 0.00650 c** | 0.02500 c | 0.01250 c | **0.00625 c** | **PASS** |

**PLANTED CONTROL (rule 3), on the nesting reader.** The three `0.000e+00` values above are from a
reader **shown able to return non-zero**: a **1e-9 m** perturbation planted into one L3 point on
disk was read back at **1.000000083e-09 m**, over the 8.059e-13 m tolerance. Had the reader not
seen it, the comparator **refuses (exit 2)** and the zeros are not evidence.

## The two failing channels are DIFFERENT FAULTS with DIFFERENT OWNERS

**(1) NON-ORTHOGONALITY — this is AMENDMENT 2's tip fill, and it does NOT improve under refinement.**
All severely non-orthogonal faces lie on the tip fill's **two collapsed lines**, at the tip section's
leading edge and trailing edge. The **measured control** — the identical C-grid built with the fill
**omitted**, `verification/runs/F13_ONERA_M6_runs/mesh/CONTROL_nofill_L1_checkMesh.log` — gives
**51.2554°, ZERO faces over 70°**. So the fill carries the mesh from **51.26° to 84.64°**.
**And refining makes it worse, not better: 84.6437 → 86.0173 → 86.7767, asymptoting toward 90°,
with the severe-face count rising 36 → 216 → 1 440.** A collapsed line is a geometric singularity;
**no level of this ladder can clear this gate, so this is not a "build it finer" problem.**

**(2) `Mesh OK` — this is §5's OWN FROZEN RECIPE, and it is IDENTICAL in the control.**
The single failed `checkMesh` check at every level is **high aspect ratio**, on the **wake cut**
(L1: 4 992 cells at |y| ≈ 6e-4, x from 1.15 to 15.8). It is arithmetic, not an accident: §5 freezes a
**16m uniform** wake and a **32m exponential** wall-normal family over 20 c_root, so the wake cell
is `(X_exit − x_TE)/16m` against a first normal cell of δ₀, giving **0.958 / 1.616e-4 ≈ 5 934** at
L1. The control mesh, which has no tip fill at all, reports **the same 5 934.1 on the same 4 992
cells**. To bring this under `checkMesh`'s default 1000 the wake would have to be **≤ 2.58 m — about
3.2 c_root behind the trailing edge**, which would compromise the very C_D that Gate G1 grades.
**This lane did not shorten the domain to buy a `Mesh OK` line.** Trading a real physics extent for a
checkMesh string is the wrong trade and it is named here rather than made.

## What was NOT run, and why that is not an omission

**§6's ADMISSION GATE D (determinism: 60 `decomposePar` invocations) was NOT EXECUTED.** §5 already
refuses to grade G on a level that fails admission, so proving `hierarchical` deterministic on a mesh
that **cannot feed a gate** would spend an estimated ~15 core-min to certify an unusable ladder. That
is withheld spend, **not waste and not a result**: gate D is **`PENDING`** and runs unchanged the
moment an admissible mesh exists.

**R0 IS SERIAL, 1 RANK.** Mesh generation and `checkMesh` both run single-rank, so §6's partition
pair does **not** enter this rung. Stated explicitly so an absent decomposition is not later read as
an omission. It enters at R1–R4.

## Completion, measured

`rc` was **measured, never proxied**: every step wrote its own `RC_*.txt` and `sync`ed, and the
values were read back from disk — `RC_make.txt` = 0 and `RC_check.txt` = 0 at all three levels,
`RC_analyse.txt` = 0, `RC_r0.txt` = 0. **A missing or non-integer value is a refusal, not a pass.**

## Cost — R0

| | core-min | basis |
|---|---|---|
| **pre-registered estimate** | **19.3** | §8 R0 row (build ×3, `checkMesh` ×3, nesting + r + y⁺, **and gate D's 60 `decomposePar`**) |
| **HARD CAP** | **90** | §8 — **not breached**; `R0_CAP_BREACH.txt` absent |
| **actual, executed portion** | **2.18** | 131 s wall × 1 rank ÷ 60, from `log.r0` |
| **ratio actual/predicted** | **0.113** | on the whole rung as costed |
| **dollars** | **$0.0019 DERIVED, never measured** | 2.18 core-min = 0.0364 core-h × $0.0513/core-h |

**Gap attribution.** The 17.1 core-min underspend is **not** a good estimate meeting a fast machine:
**~15 core-min of it is gate D, deliberately withheld** (above), and the rest is that §8 priced
meshing at the team's measured `blockMesh` fit (74.9 s for all three levels) while the instrument
that actually ran writes `polyMesh` from Python and took **74 s** for the same three — **the fit was
right to within 1 %, on a different tool, by coincidence rather than by transfer.** No stall row: the
longest step was 66 s, far under the 3600 s stall rule. **Waste: none identified.**
**Separately named, not folded into the ratio:** ≈**0.5 core-min** of serial scratch dry-runs during
instrument development, run **outside every registered path**, disclosed on the face of AMENDMENT 2
§A2.2(4).

## Artifacts

`mesh/m{1,2,4}/log.checkMesh` · `mesh/m{1,2,4}/log.makeMesh` · `mesh/m{1,2,4}/RC_{make,check}.txt` ·
`mesh/CONTROL_nofill_L1_checkMesh.log` · `R0_ADMISSION.json` · `log.analyse_f13` · `log.r0` ·
`RC_r0.txt` · `R0_RESUME.md` · `run_r0.sh` · `analyse_f13.py`.
The built `constant/polyMesh` trees (20 M / 164 M / 1.4 G) are on disk and are **gitignored by
`.gitignore:66`** — they are regenerable exactly from `cases/F13_onera_m6/make_blockmesh_m6.py`.
