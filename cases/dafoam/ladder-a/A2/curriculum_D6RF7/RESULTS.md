# D6RF7 — RESULTS (A2 wing convergence probe, P_conv)

**Verdict: `NOT A RESULT`.**  Single source of truth for every number below:
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF7-a2-wing-convergence-probe/d6rf7_official_verdict.json`
(frozen freeze sha `347976d2`). Nothing here is re-derived; each figure is quoted
from that file with its key.

This is a **ONE-ROW, PATCHED-ROW** verdict. It is **NOT** a full
`DAFOAM_CHARTER.md` §6 verdict about DAFoam and must not be read as one
(`two_row_rule.is_a_full_charter_section_6_verdict = false`).

---

## 1. The verdict and why

**`NOT A RESULT`** — the item lands on **rung 6** of the registered ladder:

> `verdict_reasons`: "rung 6: gate(s) `['G-DVL_endpoint_locus',
> 'G-FD_bright_line_on_J', 'G-OFF_per_point', 'G-PRICE_single_point']`
> NOT A RESULT for want of an input"

Those four CD-dependent gates **have no input**. The producing arm `P_conv` **RAN
clean** (rc=0, `End` line, age guard passed — `grade.G1.ran_clean = true`) and its
FD product `d6rf7_fd_endpoint.json` **is on disk**, but its `points` block is
**empty** because the baseline primal **RAISED BY DESIGN** — P_conv is the
convergence probe (`primal_raised = true`,
reason `ARM_RAN_PRIMAL_RAISED_POINTS_EMPTY`). There is no CD to read, so the FD
bright line, the per-point off-design gate, and the single-point price gate each
read `NOT A RESULT` for want of an input — **not** `GATE FAIL`, **not** an artefact
that was never written. `G-DVL` is `NOT A RESULT` because its second arm `REF_off`
was **not registered at this freeze** (the P_conv design vector itself passed:
`G-DVL.arms.P_conv.verdict = PASS`).

The FD bright line is therefore **uncrossable at this freeze**: it is the rung-6
"want of an input" condition, not a failed comparison.

## 2. The physics finding — the repair did NOT clear the floor

The gate that measures the repair is **`G-CONV`**, which reads `p` from the log,
not from CD. Its bar is the DAFoam accept floor:

- **Bar = `1.0e-05`** = `primalMinResTol` `1e-08` × `primalMinResTolDiff` `1000`
  (`grade.G-CONV.bar_provenance`; **N-D43**: the accept floor is the **PRODUCT**,
  never the tolerance alone). Carried forward from D6RF3 **unchanged**; the planted
  accept-floor control confirms it **did not move**
  (`accept_floor_unmoved = true`, `state = EXERCISED-PASS`, planted token `1e12`
  read back, `reader_saw_the_plant = true`).

**Fix #1** (fvSchemes `Gauss linear limited corrected 0.333`) **+ Fix #2**
(`nNonOrthogonalCorrectors 3`) — both installed and confirmed by `G-SCHEME`
(`PASS`; `nCorr_read_from_run = 3`, `coeff 0.333`, fvSchemes md5
`8374443e…` AS_REGISTERED) — **do NOT bring `p`'s first uncorrected solve under the
`1.0e-05` floor**. On the graded leg **L1** (the LIMITED-scheme baseline):

| field | initRes (final iter) | ratio to bar `1e-05` | verdict |
|---|---|---|---|
| `p_first_uncorrected` | `1.625570732e-05` | **1.626×** | `GATE FAIL` |
| `nuTilda` | `1.408231801e-05` | 1.408× | `GATE FAIL` |
| U0, U1, U2, he, p_corrected | all ≤ `7.7e-07` | ≤ 0.078× | `PASS` |

`G-CONV` verdict = **`GATE FAIL`** (worst field `p_first_uncorrected`). **The floor
held; the repair did not reach it.** The binding residual is the explicit
non-orthogonal-correction magnitude carried lagged into each first pressure
assembly — irreducible at fixed mesh and fixed scheme.

**F5 falsifier (reported):** the identical primal at D6RF4's ORIGINAL scheme
(leg L3, `nNonOrthogonalCorrectors 1`) gives `p_first_uncorrected`
`1.658293343e-05` = **1.658×** the bar → `GATE FAIL`, **AS PREDICTED**
(`falsifiers.F5.verdict = "AS PREDICTED"`, `withdraws = false`). The wrong setting
failed the gate it names, so G-CONV is measuring the linear-solver stopping rule
and its verdict stands.

## 3. Infrastructure gates (all PASS)

- **`G1` completion**: `PASS` — `rc=0`, `wall_s=204`, `ranks=4`,
  `core_min=13.6`, age guard clean, terminal line `Finalising parallel run`.
- **`G-CAPS`**: `PASS` — `cap_core_min = 186.0`, `core_min = 13.6`, `within_cap =
  true`, deadline frame pass.
- **`G-SCHEME`**: `PASS` — registered LIMITED discretisation ran (md5 AS_REGISTERED,
  3 correctors, 4 p-solves/final iter).
- **`G9` toolchain**: `PASS` — PATCHED IDWarp image
  (`digest_is_patched = true`); SHIPPED row `NAMED UNBOUGHT`.
- **`G12` placement**: `PASS` — cpuset `2,3,4,14`, 20g, delivered cores mean 3.373.
- **Planted controls**: price control `EXERCISED-PASS` (Δ `0.001234` read back);
  CD and FD controls `NOT EXERCISED` (nothing-to-plant-into: the product's `points`
  block is empty by primal-raise), reported, never counted as a pass.

## 4. Reported, not gated

- **`R-RED`** composite reduction `27.42 %` (J0 `0.030641631`, Jf `0.022238800`),
  inside the reference band [15 %, 40 %]; **not gated** — the producing
  optimisation exited on a non-finite objective, so this is a number along a
  trajectory, not a claim about a converged optimum.
- **`X-CDLOG`** stdout cross-check: `NOT PRODUCED` (same present-but-empty product).

## 5. Cost

- **Spend: `13.6` core-min** (`spend_core_min`), **$`0.011628` DERIVED**
  (`spend_usd_derived`).
- **Ceiling: `186` core-min** (`ceiling_core_min`; the arm cap, one registered arm).
- `cost_basis`: c7a.4xlarge at $0.0513/core-h, **REPORTED-BY-OWNER, NOT MEASURED**
  (`COMPUTE_BUDGET_CHARTER.md` §5); dollars **DERIVED**, never measured.
- `13.6 < 186` — no cap fired.

## 6. Two-row rule

- Row **BOUGHT**: `PATCHED` (patched IDWarp image).
- Row **NOT BOUGHT**: `SHIPPED`, **priced anyway at `155.70` core-min**
  (a second F_mp on stock IDWarp at the same cap; F_mp's own registered estimate,
  PREREGISTRATION.md §4a). An unbought row that is priced can be bought by a
  successor; an unbought row that is unpriced quietly becomes never.

## 7. What this leaves for the successor (D6RF8)

The floor held and the scheme repair did not clear it, which is itself the measured
finding: at this mesh (max non-orthogonality **71.48° > DAFoam default 70°**,
`docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md:56-58`), the explicit non-orthogonal
correction magnitude bounds `p`'s first uncorrected solve above `1e-05`. The
remaining un-tried lever is a **re-mesh below the non-orthogonality limit** — the
D6RF8 hypothesis. The `1.0e-05` floor stays; widening it is forbidden (N-D43).
