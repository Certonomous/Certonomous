# T9a-R1b — one-row successor of T9a: R1 with the harmonic interface scheme (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** A **fresh registration**, never an amendment: T9a (`T9a_RESULTS.md`,
GATE FAIL on R1) is closed and unchanged. Verdict vocabulary fixed by
`CLAUDE.md` rule 1. Written by a heat-transfer lane; decisions `[lab-attributed]`.

## 0. The parent, the row, the cause, the fix

`T9a_RESULTS.md` §1.1 names the cause of R1's 2.41 mK miss against a 0.92 mK
GCI band: under `laplacianSchemes Gauss linear corrected` the face conductivity
at each material interface is the **arithmetic** mean of the two layer
conductivities (0.42 W/mK against the series-resistance 0.0762 at the 0.8|0.04
interface; 8.02 against 0.0798 at 0.04|16) — one face per interface too
conductive by a margin that shrinks with `dx`. T9a lists "a harmonic interface
treatment" as the untested successor (§ "what this rung did not measure").

**What moves — one line:** `laplacianSchemes { default Gauss linear corrected; }`
→ `{ default Gauss harmonic corrected; }`. **Everything else is the parent's
byte for byte**, taken from the parent's freeze `0cbaea26573924a27d489a8472fad233e198ca6d`
with `git show <sha>:<path>` (`0.orig/T`, `0.orig/DT`,
`constant/transportProperties`, `system/{blockMeshDict,controlDict,fvSolution}`),
on the same three wall levels `W_c/W_m/W_f` → `W1b_c/W1b_m/W1b_f`
(cells per layer 10/20/5, 16/32/8, 26/51/13). `build_t9aR1b.py` **refuses** if
the written `fvSchemes` differs from the parent blob by anything but that line
(driven: a planted extra line → exit 2).

**Capability-grid cell:** conduction × 1-D steady layered wall (the parent's
cell). This rung claims nothing about fins (T9a's F rows are untouched).

**Condition at freeze:** `verification/runs/T-family/T9aR1b_runs/W1b_{c,m,f}`
hold `0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`, build logs —
no `0/`, no time directory, no `log.solve`, no `STATUS.*`, no `DONE.*`. Zero
core-minutes in the registered tree. **Disclosed scratch probe:** copies of
`W_c` and `W_f` with the harmonic line were run outside the repository
(2026-08-26); both reproduced `T_i1` to **5.7e-14 K and 2.9e-12 K** and `q` to
1e-9 relative — the piecewise-linear exact solution lies in the null space of
the harmonic scheme's truncation error. That probe shaped §2 and is disclosed
rather than absorbed.

## 1. The graded row and its referent

| row | quantity | reference |
|---|---|---|
| **R1** | `T_i1`, interface-1 temperature, conductance-weighted mean of the two cells adjacent to the interface face — **the parent's reader form** (`analyse_t9a.measure_wall.iface_T`) | **348.781082398830 K**, derived in `analyse_t9aR1b.exact` from the series-resistance law and **cross-checked to T9a's registered 348.781082 K and q = 19.502682 W/m² to 1e-6** (a 1 mK planted error is refused — driven) |

R0 (`q` at the hot face) is **REPORTED, not graded**.

## 2. The gate — T9a's row rule, unchanged, with its EXACT case made operational

T9a's rule (`analyse_t9a.grade_triple`): convergence-gated (rule 5), **band =
the triple's own GCI** (`Fs` 1.25, unequal ratios from cell counts, `dim` 1,
`roache_triple.gci_unequal`), PASS iff |deviation| ≤ band. T9a's own text for
an EXACT triple — *"a zero band grades only a literally exact value"*
(`analyse_t9a.py:223`) — is made operational here, because the scratch probe
predicts exactly that outcome:

- a triple whose level differences are **both below the round-off floor
  1e-09 K** is EXACT (the parent's byte-identical EXACT for a scheme that hits
  the exact solution to ~1e-12 K rather than to the bit);
- an EXACT triple is graded by the **absolute floor |T_i1 − exact| ≤ 1e-06 K**
  — ~1000× the measured round-off and **900× tighter than T9a's R1 band of
  0.92 mK. No band is widened.**
- any other non-CONVERGING state → NOT A RESULT, `p` printed, GCI refused.

**Floors imported** (`MESH_STANDARD.md` §10.5): `STAGNANT_FLOOR, P_MIN, FS,
PLANT, gci_unequal, refinement_ratio` from `scripts/roache_triple.py`; the
comparator defines none and refuses if the registered copy differs (driven).

| control | what | on failure |
|---|---|---|
| C_CONV | `End` line; the last two written checkpoints (900, 1000) agree in `T` to 1e-09 K (the parent's checkpoint form, L-140/L-141) | gate (1) → NOT A RESULT |
| C_MAP | every cell's `DT` equals the registered layer conductivity at its centre (parent's C_MAP) | exit 2 |
| C_SCHEME | `CASE.txt` and `system/fvSchemes` on disk carry the harmonic line; the parent's linear line is refused (driven) | exit 2 |
| C_REF | referent cross-check (§1) | exit 2 |
| C_PZ | planted-zero control, rule 3: one-cell plant in the cell adjacent to interface 1 (the point reader's own station), both arms, measured ladder; refuses a blind/noisy reader or a read < 0.1 × plant | exit 2 |
| completion | `mark_done_t9aR1b.py` (T14's, fields `T DT`, `ExecutionTime` count == 1000, age guard); STATUS absent → REFUSE | NOT DONE → the grader refuses the rung |

**L-342 field classes** as T13/T14: physics-critical = `rc`, `End`, last time,
fields, count, age guard; infrastructure = `wall_s, timeout_s, ranks, core_min,
capped, checkmesh_rc, solver, solver_path, note, started_utc, ended_utc` —
absent → NOTE, grade proceeds (driven).

## 3. Predictions — registered before compute

- **P1.** The R1 triple is **EXACT** to round-off: |e21|, |e32| < 1e-09 K.
- **P2.** |T_i1 − 348.781082399| < 1e-09 K on every level → **PASS** by the floor.
- **P3.** R0 (reported): `q` within 1e-09 relative of 19.502682 on every level
  — the parent's 1.8 % linear-scheme excess vanishes.
- **P4.** If instead the triple is CONVERGING, `p` in [1.5, 2.5] and R1 inside
  its own GCI band.

## 4. Instruments — L-332

| instrument | selftest | `python3` | `-O` |
|---|---|---|---|
| `build_t9aR1b.py` | parent blob patched to the single line; written file with a planted extra line vs the blob → REFUSE; parent without the linear line → REFUSE; AST 0 (planted 1) | PASS | PASS |
| `analyse_t9aR1b.py` | 11 checks: floors import; referent cross-check with a 1 mK plant → REFUSE; forged ladders: exact → EXACT → PASS; exact + 2e-06 K → EXACT above floor → GATE FAIL; consistent second-order ladder → CONVERGING inside its GCI → PASS; ladder on a 1e-03 K constant error → GATE FAIL; checkpoints moving → NOT A RESULT; oscillating → NOT A RESULT; linear-scheme case → REFUSE; live tree without DONE → REFUSE; AST 0 | PASS | PASS, identical |
| `mark_done_t9aR1b.py` | 10 forged clauses incl. STATUS absent → REFUSE and infra absent → DONE + NOTE | PASS | PASS |

## 5. Cost — rule 12

Rate from the **parent's MEASURED** `STATUS.W_c` / `STATUS.W_f`: wall 0.09 s
per level, serial (scratch harmonic: 0.11–0.12 s). **POINT 0.0015 core-min per
level, 0.0045 total; cap 1 core-min per level (`timeout` 60 s), 3 total** —
$0.0026 derived at $0.0513/core-h, reported-by-owner, not measured. The cap is
a hang guard.

## 6. The launcher

`run_one_t9aR1b.sh` = `run_one_t14.sh` (freeze `5a870e54`) with the rung name
and field set (`T DT`) changed: rc in the wrapper, `capped` witness, cap read
from the registered JSON, **lineage-aware guard (`9fa66065`)**, `--no-detach`
queue mode. **Driven on scratch, both arms:** ARM A (runner form) → launched,
rc 0, 1000 steps, STATUS written, `mark_done` DONE; ARM B (planted `sleep`,
cwd in the case) → `REFUSE: pid 457468 is already running in W1b_c_armB
(foreign process, outside this launcher's lineage)`, exit 2, no STATUS.

## 7. The freeze set (committed with this document)

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T9aR1b_runs/build_t9aR1b.py` | `817f42719b70afc0` | `ef58986681c292c71fccbce2d478ac4a48facc18` | 159 |
| `verification/runs/T-family/T9aR1b_runs/analyse_t9aR1b.py` | `735a8690208a50f4` | `fd6c43a0da916e534b588c306edaf7da737c3c7a` | 396 |
| `verification/runs/T-family/T9aR1b_runs/mark_done_t9aR1b.py` | `67a3b8fc9da612aa` | `68c78731a061688ace56e7ca43133a4716b328a4` | 220 |
| `verification/runs/T-family/T9aR1b_runs/run_one_t9aR1b.sh` | `031e6e045604ef50` | `d7990722b87c592a1b5c8a09bd75e77092c86b32` | 193 |
| `verification/runs/T-family/T9aR1b_runs/T9aR1b_registered.json` | `6da0bebc54dd844f` | `cfe867c6c88dd4fd1094e9e0733966c650308ecb` | 165 |

Case inputs for `W1b_c/m/f` (`0.orig/`, `constant/` less `polyMesh`, `system/`,
`BUILD.txt`, `CASE.txt`, build logs) are committed alongside.

## 8. What this document does not do

It does not reopen, amend or re-grade T9a; it does not authorise a launch
(enqueueing is not authorisation); it does not claim a capability; it
authorises no send — **SUBMISSIONS REMAIN PARKED** (rule 7).
