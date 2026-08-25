# DAFoam's contribution to the lab-wide coverage matrix — adjoint-gradient and adjoint-optimization rows

**NOT FILED ANYWHERE. Nothing in this document is filed, sent, emailed, uploaded, posted,
registered, submitted or commented outside this box, now or ever** (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.** The five upstream DAFoam defect drafts are
untouched by this document and remain **NOT FILED** drafts.

**Written 2026-08-24 by a DAFoam `lab-lane` (Opus) at HEAD `69d2f1ba`, on the dafoam supervisor's
brief. ZERO COMPUTE: no solver, no container, no probe was started to produce this file.** Every
figure below was re-read from the record named in its own row; nothing is from memory and nothing
is copied from the dispatching brief. Where the brief disagreed with a record, **the record wins**
and the disagreement is listed in §5.

**AUDITED AND REPAIRED 2026-08-25 by a second DAFoam `lab-lane`, adversarially, at the dafoam
supervisor's direction. ZERO COMPUTE on the audit as well: no solver, no container, no probe.** The
first draft was written by a lane that was killed in a fleet termination before anyone read it, so
it was treated as **a draft by a dead author, not as a record**. Every row was re-checked against
the verdict on record. What the audit changed is disclosed rather than quietly corrected, and each
change is listed where it belongs:

- **Five rows were structurally broken by literal `|` characters in cell text** — `G-23`, `O-05`,
  `O-07`, `O-08`, `O-10` — so **their lab verdict and matrix tier rendered in the wrong columns**.
  All are escaped and **every one of the 58 data rows is now asserted to carry exactly 14
  pipe-delimited fields** (§4.0).
- **The §4 census did not reproduce from the command §4 said produced it** — it shipped `51`
  against a true `58`. It is **withdrawn, disclosed and rebuilt**, and the new command **refuses
  with exit 2** rather than warning, with its refusals **planted and proved** (§4).
- **The `G` and `P` coverage columns were missing entirely** and have been added to all 58 rows,
  honestly: `G` is `NEVER RUN` in every row because this family has **no Roache triple anywhere**
  (§3.4), and `P` is `NEVER RUN` in 56 of 58 because only two rows name a public primary and
  **neither has a pre-registration on disk** (§3.5).
- **The V-standard placeholder `sha VERIFY` is discharged** in all sixteen cells: `4a6ea0b8`,
  blob `6b96fbd3` (§0.6).
- **Four verdict cells carried words outside the six-token vocabulary** and were repaired or
  quoted-and-flagged: `G-08`, `G-21`, `G-32`, `G-33`, `O-11` (§5 items 7, 8).
- **One row was retiered** — `O-11`, `NEVER RUN` → `NOT HELD`, against the document's own §0.2 map
  (§5 item 9). **No other tier was moved**, and in particular the four rows that decline to read a
  gate reserved to Sanaa are untouched.
- **Two rows gained mandatory qualifiers the record requires and the draft omitted**: `O-06`'s
  design-point-dependence clause (mechanism **UNTESTED**) and its `P5`
  prediction-miss-versus-gate-failure distinction (§5 items 10, 11).

**This file is a CONTRIBUTION, not the matrix.** `docs/COVERAGE_MATRIX.md` belongs to the
verification supervisor. This document is written so its rows can be lifted whole; it does not
create, edit or reserve any part of that file, and it asserts nothing about rows outside the
DAFoam family.

---

## 0. Front matter the reader must have before the first row

### 0.1 Two vocabularies, and one word that collides

This document carries **two distinct verdict columns and they must never be conflated.**

| column | vocabulary | who fixed it |
|---|---|---|
| **lab verdict** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` — and nothing else | `CLAUDE.md` rule 1; `VERIFICATION_CHARTER.md` §2, §9; `DAFOAM_CHARTER.md` §8 |
| **matrix tier** | `HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` / `NEVER RUN` — and nothing else | Sanaa's five tier words for the coverage matrix |

> **DISCLOSED COLLISION: `GATE REACHED` is a member of BOTH vocabularies and does not mean the same
> thing in both.** In the lab vocabulary it is a verdict about a run: a pre-registered gate was
> reached. In the matrix vocabulary it is a tier about coverage. A row may carry `GATE REACHED` in
> one column and something else in the other, and a reader who reads the two columns as one will
> get the wrong answer. **Every other word appears in exactly one of the two vocabularies.** This
> is stated here rather than discovered downstream.

No sixth word is used in either column, and no word in either column is hedged with an adjective.
Where a record's own status phrase is not a member of either vocabulary, the cell says so in the
record's words and the row is flagged in §5.

### 0.2 The tier mapping this document applied, stated so it can be overruled

The five tier words are Sanaa's; **the mapping from lab verdicts to them is this lane's proposal
and the verification supervisor may replace it.** It was chosen to be disjoint and exhaustive:

| tier | assigned when |
|---|---|
| **HOLDS** | the claim was tested against a pre-registered gate and passed — lab `PASS` |
| **GATE REACHED** | lab `GATE REACHED`: the registered gate was reached; the claim it serves is not thereby established |
| **SURVEYED** | an arm ran and something is on the record, but nothing was graded against a pre-registered gate — lab `NOT A RESULT`; a launched arm that delivered no gradeable value; or a diagnostic/corroborative row that carries no gate of its own |
| **NOT HELD** | the claim was tested and did not hold — lab `GATE FAIL`; **or** lab `BLOCKED` where the blocker was measured on the case itself (an adjoint that will not solve is a claim about that adjoint that does not hold) |
| **NEVER RUN** | no measurement of this cell exists **and** no arm was launched — zero compute. Lab `PENDING`, "NOT MEASURED", "NOT RUN"; **or** lab `BLOCKED` where the blocker is a standing decision rather than a measurement |

**The `BLOCKED` split is the mapping's one judgement call and it is deliberate.** B3 shipped is
`NOT HELD` because a `-9` at iteration 0 was measured on that case, four times; B3 Stage 4 is
`NEVER RUN` because nothing was launched and the blocker is Sanaa's fork-adoption call. Both are
lab `BLOCKED`. A single tier for both would have said something false about one of them.

**Control and trivial-baseline arms are not separate rows.** A registered wrong-step control
(`DAFOAM_CHARTER.md` §4) grades the instrument, not the claim; folding it into the row it controls
keeps the census a census of coverage. Every such control is named inside its row's cells.

### 0.3 The structural rule this document exists to obey

> **SHIPPED and PATCHED are ALWAYS SEPARATE ROWS. A patched row NEVER replaces a shipped row and
> the two are never merged into one cell** (`DAFOAM_CHARTER.md` §6; R11, `FAMILY_SUPERVISION_GUIDELINES.md`
> §3.4, `SUPERVISOR_RULINGS.md:195`).

A patched grade moves a shipped grade only if the fix ships upstream or Sanaa adopts a forked
toolchain, and that is her call. **B3 is `BLOCKED` against the shipped toolchain today and `PASS`
against `dafoam-subpclu:v2`, and both sentences are true** — the charter's own worked example, and
rows G-31 and G-32 below are those two sentences as two rows.

### 0.4 Toolchain identity — the hash, never the version string

**All three DAFoam images report DAFoam 5.0.0, OpenFOAM v2506, PETSc 3.15.5 and IDWarp 2.6.2. They
differ only in `DALinearEqn.C`** (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §1, §3, §6a, §6e;
`cases/dafoam/patched_build/subpclu/BUILD.md` §4.2–4.3). A version string is not an identity.

| key used in the rows | image | image ID | identity, verified in-image | patch on disk |
|---|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `9d45679d55fd` (`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`) | `DALinearEqn.C` md5 `f6a89e33b0f4772a0563cb0c8633ac48`, **507** lines, **0** `DAFOAM_SUBPC_TYPE`; `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`, 491,344 B | none — shipped image, no patch |
| **PATCHED-ROT** | `dafoam-idwarp-rot:v1` | `2927768a16ac` (`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`) | built `libidwarp.so` md5 **`85f59e87253e0a71a813f64ca6e4c425`** against stock `f0fcb488e0e98156575cd19548e91663`; **both 491,344 bytes and both report IDWarp `2.6.2`** | `cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`, 4,061 B, 2 files, **+44 lines** |
| **PATCHED-ROT †** | the same patched bytes **bind-mounted onto `PYTHONPATH` over the stock image**, host clone `/home/ubuntu/certonomous-runs/W5-patch/idwarp` | no image | **no md5 is stated in those records**; provenance is the in-log `IDWARP_IMPORTED_FROM:` stamp | same patch file |
| **PATCHED-SUBPCLU-v1** | `dafoam-subpclu:v1` | `ba2d16ab9d57` | `DALinearEqn.C` md5 `89e71ca2db5d80c06b1eda070ffc7a1b`, **526** lines (+19), **3** `DAFOAM_SUBPC_TYPE` | `cases/dafoam/subpclu_patch/DALinearEqn_subpclu.patch`, 3,841 B, 19-line block |
| **PATCHED-SUBPCLU-v2** | `dafoam-subpclu:v2` | `8352629516bb` | `DALinearEqn.C` md5 **`5b3159f88dbefcf7c52bd888401d097f`**, **539** lines, **4** occurrences; `libDASolver.so` 9,111,104 B / `libDASolverADR.so` 11,415,760 B / `libDASolverADF.so` 9,534,512 B, each **+48 B** over stock | same patch file, one hunk further on |
| **PATCHED-KSPOPTS** | `dafoam-kspopts:v1` | `d9d2aed02e36` | `DALinearEqn.C` md5 `96f5762819e33efbdaad34181a214082`, **534** lines, **3** occurrences, `KSPSetFromOptions` relocated to line **351** | `cases/dafoam/kspopts_patch/DALinearEqn_kspopts.patch`, 1,396 B. **Built ON `dafoam-subpclu:v1`, so it carries the sub-LU patch too, env-gated and off** |
| **PATCHED‡ (stock mode)** | `dafoam-subpclu:v1` run with `DAFOAM_SUBPC_TYPE` **unset** and stock IDWarp | `ba2d16ab9d57` | the image's own md5 above; the run is stock-*behaviour*, proved by the **absence** of the banner `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` | as v1 — present in the image, not active |

**`v1` versus `v2`, stated once and carried by every S1/B3 sub-LU row.** `dafoam-subpclu:v1`
produced every recorded sub-LU number in this lab and was built by a hand-run
`docker run` / `docker commit` in a scratch tree that no longer exists; the patch file on disk was
**one hunk ahead of the built image** and said so only in its own provenance header (finding B-1).
`BUILD.md` §4.2 gate **G2c** is the reproducibility claim that stands: `diff v1 v2` is **13 added
lines** (`285a286,298`), all inside an `else if` branch entered only for a `DAFOAM_SUBPC_TYPE`
value that is neither unset nor `lu` — a condition false in both arms of every sub-LU run on the
record — so **the numeric path of `v2` is byte-identical to the image that produced `reason 2` in
667 iterations**. Gate **G2d** closes the other half: applying the committed patch to the stock
file on the host yields md5 `5b3159f88dbefcf7c52bd888401d097f`, equal to the in-image figure.
md5 equality with `v1` was **predicted to fail by construction and did** — that gate is not the
claim.

**The exact-match trap, asserted on every sub-LU row.** `strcmp(subPCTypeEnv, "lu")` is exact, so
`LU`, `Lu`, `lu ` with a trailing space or `superlu` all run stock ILU **with no message**. The
in-log banner is asserted before any sub-LU result is trusted, and **its absence is the standing
proof a run was stock**.

### 0.5 THE STANDING FACT ON EVERY PATCHED ROW

> **Nothing a reader can install reproduces the patched numbers.** None of these patches has been
> filed upstream — filing is Sanaa's alone and nothing has been filed (`CLAUDE.md` rule 7;
> `DAFOAM_CHARTER.md` §10) — and **no container image has ever been pushed to a registry**; all
> five are local to this box. The IDWarp rotation fix exists in **no** container image at all
> (`TOOLCHAIN_INVENTORY.md` §4: the Fortran sources are absent from all three images) and in no
> upstream release; `dafoam-idwarp-rot:v1` COPYs a prebuilt `.so`, so if
> `/home/ubuntu/certonomous-runs/W5-patch/idwarp` is lost the image cannot be rebuilt bit-for-bit.

This sentence is restated in the patch-provenance cell of every PATCHED row below. It is repeated
per row and not once at the top **deliberately**: a reader lifting one row into another document
must carry it with the row.

### 0.6 The V column

**The V-column standard for this whole family is the finite-difference-versus-adjoint check**:
`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md` (curriculum item **D15**). The first draft of this
document was written at HEAD `69d2f1ba`, minutes before that standard landed, and carried the
placeholder `sha VERIFY` in **sixteen** cells. **The placeholder is now discharged and all sixteen
cells are filled.** The standard landed at commit **`4a6ea0b8`** — *"dafoam V-column standard:
FD-vs-adjoint recorded as the family's code-verification standard (curriculum D15)"* — as blob
**`6b96fbd3`**; this audit verified it present at HEAD (`git cat-file -e`) and an ancestor of HEAD
(`git merge-base --is-ancestor`), so the citation is to a committed object and not to a path that
might not exist.

**Every adjoint-gradient V cell in this document is FD-vs-adjoint and cites that standard, and no
V cell anywhere claims an exact or a manufactured solution for an adjoint gradient** — because none
exists, which is §3.1's subject. Where a row's V cell reads *"not the FD standard"* the row is
**not an adjoint-gradient row**: it is a primal gate, an external-data comparison, an
adjoint-convergence gate, a decomposition-invariance gate or a registered bit-identity gate, and
the cell names the instrument it is actually on rather than borrowing the FD one. The substantive band it codifies is the family's own
and is on the record independently (`DAFOAM_CHARTER.md` §2; `FAMILY_SUPERVISION_GUIDELINES.md`
§4.2–4.3):

> **`PASS` ≤ 5 % with zero flagged components; `CONDITIONAL` 5–15 %; `GATE FAIL` above 15 % or on
> ANY sign flip**, applied **per component**, at a step proved to lie in the plateau, at the graded
> run's own primal tolerance.

**`CONDITIONAL` is the charter's name for a BAND on an FD table, not a lab verdict**, and **no row
in this document carries it in a verdict column**. The verdict columns use the six tokens and
nothing else.

For **adjoint-gradient** rows the measured statistic is the vector-relative error
`‖J_an − J_fd‖ / ‖J_fd‖` (or the named per-component relative error where the record grades per
component, which the charter requires and which is stated in the cell). For **adjoint-optimization**
rows the measured statistic is **the optimiser's own termination string**, and the V column is the
mandatory endpoint FD check at the **final design point** (`DAFOAM_CHARTER.md` §9: an optimiser
stopped by a wall clock or an iteration cap is `GATE REACHED` or `NOT A RESULT`, never `PASS`).

### 0.7 How to read the three coverage columns — V, G and P

The lab coverage matrix scores every row on three columns. This document carries all three, and
they are **not** interchangeable:

| column | what it holds here | who fixed the standard |
|---|---|---|
| **V — code verification** | the **instrument and the measured statistic**. For this family the instrument is **FD-vs-adjoint** and nothing else — `docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md`, landed `4a6ea0b8`, blob `6b96fbd3` (curriculum D15). A row whose V cell says *"not the FD standard"* is not an adjoint-gradient row and names the instrument it is actually on. **The row's lab verdict IS its V verdict** for every adjoint-gradient row | `DAFOAM_CHARTER.md` §2, §3; the D15 standard |
| **G — grid convergence** | a **tier word**, and in this family it is **`NEVER RUN` in every row** — §3.4 | `CLAUDE.md` rule 5; `VERIFICATION_CHARTER.md` |
| **P — validation vs a public primary** | a **tier word**. `P` requires a **public primary** *and* a **pre-registration on disk**; the cell names both or it is not a P cell. Two rows name a real public primary and **neither has a pre-registration**, so both read `SURVEYED` — §3.5 | `VERIFICATION_CHARTER.md` §2b |

**The `matrix tier` column is the ROW's overall tier**, mapped from the row's lab verdict by §0.2.
It is not the V tier, the G tier or the P tier, and a reader lifting a row must lift all four cells.

### 0.8 NAMED, LIFTABLE ITEM FOR THE VERIFICATION SUPERVISOR: the two vocabularies share a token

> **The lab's six-token verdict vocabulary and the coverage matrix's five tier words SHARE THE
> STRING `GATE REACHED`, and it does not mean the same thing in the two places.**
>
> - As a **lab verdict** it is a statement about a run: a pre-registered gate was reached
>   (`CLAUDE.md` rule 1; `VERIFICATION_CHARTER.md` §2; `DAFOAM_CHARTER.md` §8).
> - As a **matrix tier** it is a statement about coverage.
>
> **Two rows in this contribution carry it in both columns at once** — `G-15` (A3's 399,360-cell
> primal) and `G-24` (A6's 579,072-cell primal). Both readings are correct; the collision is in the
> **design of the two vocabularies**, not in these rows.
>
> **This is surfaced, not resolved.** `docs/COVERAGE_MATRIX.md` is the verification supervisor's
> file and the tier words are Sanaa's, so the ruling is theirs and ultimately hers.
> **No fix is proposed that renames a lab verdict token**: `CLAUDE.md` rule 1 fixes that set and
> neither a lane nor a supervisor may widen or retire it. The disambiguation, if one is wanted,
> has to be on the tier side or in the matrix's column headers.
>
> Every **other** word in the two vocabularies appears in exactly one of them.


---

## 1. Adjoint-gradient rows

Columns: id | claim verified | toolchain row | patch provenance | V standard | measured statistic | **lab verdict** | **matrix tier** | record | sha last changing that record.

| id | claim verified | toolchain | patch provenance | V — code verification (FD-vs-adjoint) | G — grid convergence | P — validation vs public primary | measured statistic | lab verdict | matrix tier | record | sha |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **G-01** | A1 NACA0012, 4,032 cells, np=1: `CD` wrt `shape` from the discrete adjoint equals the true derivative | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd`, `DALinearEqn.C` md5 `f6a89e33…`/507 lines, `libidwarp.so` md5 `f0fcb488…` | FD-vs-adjoint, `docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md` (landed `4a6ea0b8`, blob `6b96fbd3`); central, step 1e-3 | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | vector-relative **11.4274 %** (`1.142740e-01`); **1 sign flip, idx6 at 640.3696 %** | `GATE FAIL` | **NOT HELD** | `cases/dafoam/ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` §2 | `be35dcad` |
| **G-02** | same claim, rotation-patched toolchain | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`; patch `rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch` 4,061 B / 2 files / +44 lines; built `libidwarp.so` md5 `85f59e87…` vs stock `f0fcb488…`, **both 491,344 B, both report 2.6.2**. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | as G-01. Registered wrong-step control (`§4`) folded in: **132.75 %** (`1.327522e+00`) at 1e-8 — GATE FAIL as designed | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **0.03796 %** (`3.795529e-04`); **zero flips**; idx6 right-signed at 1.1888 %; **8 of 8 raw FD components bit-identical across arms** | `PASS` | **HOLDS** | same file §2, §4.2, §4.3 | `be35dcad` |
| **G-03** | A2 MACH wing, 38,304 cells, np=4: six aggregate gradient rows | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd`, md5s as G-01 | FD-vs-adjoint (path above, landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `CD`/`shape` **1.714 %** (AN `4.801625e-02` vs FD `4.858158e-02`); `CL`/`shape` 1.165 %; `CD`/`patchV` **0.0212 %** | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A2/grading_confirmation/RESULTS.md` §1, §3 | `35171866` |
| **G-04** | same claim, rotation-patched | PATCHED † — patched IDWarp **bind-mounted onto `PYTHONPATH` over the stock image, NOT `dafoam-idwarp-rot:v1`**; host clone `/home/ubuntu/certonomous-runs/W5-patch/idwarp`; **no md5 is stated in this record** — provenance is the in-log `IDWARP_IMPORTED_FROM:` stamp. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed, and this arm is not even an image.** | — | as G-03 | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `CD`/`shape` **0.0506 %** (33.9× tighter); `CL`/`twist` 115.1× tighter; **`CD`/`twist` DEGRADES, 0.389 % → 0.505 %** | `PASS` | **HOLDS** | same file §3 | `35171866` |
| **G-05** | A2, the same gradient read **per component** (96 `CD` + 96 `CL`) | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | FD-vs-adjoint per component (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | aggregate PASS; **7 of 96 `CD` components beyond 15 %** — idx18 **−360.75 %**, idx46 −326.14 %; `CL` idx15 −80.20 %; **zero flips** | `PASS` (aggregate) | **SURVEYED** — tiered below the verdict because 7 components sit outside the per-component band; the aggregate PASS is recorded and is **not** overruled here | `cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md` | `79679a84` |
| **G-06** | A2 per component, rotation-patched — **the idx46 caveat** | PATCHED † — bind-mount over the stock image, no image ID, **no md5 in the record**, `IDWARP_IMPORTED_FROM:` stamp only. **Nothing a reader can install reproduces this row.** | — | as G-05 | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `CL` **96/96 within 5 %**; **1 sign flip, `CD` idx46**: AN `+2.27367571e-06` vs FD `−2.52460969e-06` | `PASS` (aggregate) **with a per-component caveat** | **SURVEYED** — the family band makes ANY sign flip a FAIL, so the per-component claim is not covered either way by an aggregate row; the record's verdict token is unchanged | same file §3.2 | `79679a84` |
| **G-07** | A3 ONERA M6 sweep rung 1, 21,840 cells, np=4: gradient agrees with FD | PATCHED‡ (stock mode) — `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE` **unset**, stock IDWarp; the record calls this **SHIPPED-equivalent**, which is **not** the stock image | `ba2d16ab9d57`; `DALinearEqn.C` md5 `89e71ca2…`/526 lines/3 occurrences. Stock behaviour asserted by the **absence** of the sub-LU banner. **Nothing a reader can install reproduces this image: not filed, never pushed.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `patchV[1]` **0.18 %**, `shape[115]` **0.93 %** (2 of 4 rows not evaluable) | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §2b | `35171866` |
| **G-08** | A3 rung 1, rotation-patched | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`; `libidwarp.so` md5 `85f59e87…` vs stock `f0fcb488…`. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `patchV[1]` **0.1816 %**, analytic bit-identical to shipped; `shape[115]` **0.9273 % → 0.3826 %, 2.42× BETTER** — the same unchanged library that made this row 9.2084× **worse** at rung 2; patch effect **0.940327 %** in L2, 120/120 components differ, **0** analytic flips; `twist[1]`, `shape[5]` flagged before the run, `NOT A RESULT` in the FD column on every arm | **DUAL READING, NOT FINAL UNTIL SANAA RULES.** Under the rung's registered per-component rule (`A3_FD3_PREREGISTRATION.md` §4) the arm is `PASS`. Under the aggregate band the record's own phrase is *"FAIL pending investigation"* (`rung1_patched_idwarp_np4/RESULTS.md:75`, `:94`) — **NOT a member of the six-token vocabulary**, quoted here and not translated, and flagged in §5 item 8 as a DAFoam record's own defect. Choosing between the two rules **reinterprets a gate threshold** and is reserved to Sanaa; this audit does not choose | **SURVEYED** — measured; the rule choice is Sanaa's, so no tier may claim it holds | `cases/dafoam/ladder-a/A3/rung1_patched_idwarp_np4/RESULTS.md` §1–§3 | `ac12b0fd` |
| **G-09** | A3 rung 2, 42,120 cells, np=4: gradient agrees with FD | PATCHED‡ (stock mode) — `dafoam-subpclu:v1`, banner absent | `ba2d16ab9d57`, md5 `89e71ca2…`/526. **Not filed, never pushed.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **0.0077 % / 0.2740 % / 0.0172 %**, all three evaluable — the tightest stock numbers on the ladder | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §2c | `35171866` |
| **G-10** | A3 rung 2, rotation-patched | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`; `libidwarp.so` md5 `85f59e87…`. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `patchV[1]` **0.0077 %** (analytic bit-identical to stock); `twist[1]` **0.2740 % → 0.9279 %**; `shape[115]` **0.0172 % → 0.1586 %** — **every warp-crossing row gets worse**; patch effect **1.469586 %** in L2; 3 analytic sign flips (idx 12, 13, 24, no FD there) | `PASS` | **HOLDS** — and it is the first measured A/B pair on this ladder that **degrades** (N-D18) | `cases/dafoam/ladder-a/A3/rung2_patched_idwarp_np4/RESULTS.md` §2, §5 | `0f56460d` |
| **G-11** | A3 rung 3, 79,560 cells, np=4: the adjoint linear solve converges | PATCHED‡ (stock mode) — `dafoam-subpclu:v1`, banner absent | `ba2d16ab9d57`, md5 `89e71ca2…`/526. **Not filed, never pushed.** | FD-vs-adjoint not reached — no gradient exists on this rung | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **4,000 iterations, `reason −3`, 1.31× residual reduction**; **peak 11.65 of 22 GiB — a conditioning wall, not a memory one** | `GATE FAIL` | **NOT HELD** | `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §2d | `35171866` |
| **G-12** | A3 rung 3 adjoint, rotation-patched, **attempt 1** | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…`. **Nothing a reader can install reproduces this row.** | not reached | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | killed at **85 s of a 2,600 s budget** by its own registered guard on the **HOST FLOOR** limb (`MemAvailable 7.3944 GiB < 8.0`, 3 consecutive samples) while its own RSS sat at **9.202 of 15.0 GiB**; **0 of 11 identity checkpoints reached**, no adjoint, no gradient, **no claim in any direction** | `NOT A RESULT` — stopped by memory | **SURVEYED** — compute was spent (6.80 core-min) and nothing was graded | `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4/RESULTS.md` §1–§3 | `67edcc19` |
| **G-13** | A3 rung 3 adjoint, rotation-patched, **attempt 2** | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…`. **Nothing a reader can install reproduces this row.** | not reached | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **all 11 printed KSP residual checkpoints bit-identical to the frozen SHIPPED-equivalent path, iterations 0–1000** (`1.615247229756e-02` at 1000; reduction **1.3133×**, flat — `1.446e-06` relative over 900→1000). **This arm printed NO `PetscConvergedReason`**; the terminal `−3` at 4,000 iterations is the shipped run's value carried across by the bit-identity — the registered word is **INHERITED**. Terminal rc=137 is the registered DELIBERATE STOP, not a crash | `GATE FAIL` (adjoint, INHERITED) | **NOT HELD** | `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md` (graded at `8871acf3`) | `bec36c9d` |
| **G-14** | A3 rung 3 **gradient**, rotation-patched | PATCHED — `dafoam-idwarp-rot:v1` | as G-13. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint not reached | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | no gradient was produced on rung 3 by any patched arm; the rung is **silent both ways** on rung 2's degradation finding | `NOT A RESULT` | **SURVEYED** | same file; grading commit `8871acf3` states it in terms | `bec36c9d` |
| **G-15** | A3 original campaign, **399,360 cells**, np=4: the primal converges to a force-stationary state | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | primal gate, not the FD standard | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | CD **`0.0229955633492643`**, CL **`0.3131158872361974`**, 1244.2 s | `GATE REACHED` | **GATE REACHED** *(see §0.1 — the word means different things in the two columns)* | `cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md` §1 | `35171866` |
| **G-16** | A3 399,360 cells: surface `Cp` matches AGARD 2308 | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | external-data comparison, **not** the FD standard | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **SURVEYED** — the primary is public and archived on disk: **AGARD AR-138 Case 2308** (Schmitt & Charpin 1979) via the NASA-TMR mirror, `cases/dafoam/ladder-a/logs_A3/case_2308.dat`, 22,695 B. **But NO pre-registration on disk registers this Cp comparison as a gate** — the comparison is post-hoc, so the cell is **not P** (§3.5) | pressure RMS **0.0128–0.0265** across seven stations; suction surface (carrying the shock) **0.0491–0.1139** | `PASS` | **HOLDS** | same file §1b, and its §-table row `:247` | `35171866` |
| **G-17** | A3 399,360 cells: an adjoint gradient is obtainable at all | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | not reached | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **8 mitigations exhausted, no gradient ever reached**: OOM at 12g **and** 18g at the identical coloring step; OOM at 399,360 **and** at 99,840; `decomposePar` SEGV twice at 24,960; np=2 drove host `MemAvailable` to **1.77 GB** | `BLOCKED` | **NOT HELD** — the blocker was measured on this case, repeatedly | same file §1c, §3 | `35171866` |
| **G-18** | A3 399,360 cells, rotation-patched, any scope | PATCHED — `dafoam-idwarp-rot:v1` | **no arm of any kind exists at this size on any patched image**; nothing to hash | — | **NEVER RUN** — a three-level mesh family exists on A3 (21,840 / 42,120 / 79,560 cells) but **no Roache triple was ever formed from it**: the 79,560 level produced no gradient, and no GCI and no observed order is computed anywhere on this case (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` — NOT MEASURED | **NEVER RUN** | `cases/dafoam/ladder-a/A3/rung2_patched_idwarp_np4/RESULTS.md` §10.6; `LADDER_A_STATUS.md` row 12b | `0f56460d` |
| **G-19** | A4 Ahmed-25, 2,777 cells, np=1 at the undeformed baseline: `dCD/dshape` agrees with FD — **the graded configuration** | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd`, md5s as G-01 | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`), serial before parallel (`DAFOAM_CHARTER.md` §5) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **1.10 %** (`1.1032e-02`; AN `2.3965e-01` vs FD `2.4232e-01`, `a4_np1_stock.log`) | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A4_ahmed_body.md:256-264` (`:195-196` for the supersession note) | `ddb99eca` |
| **G-20** | A4 baseline gradient, rotation-patched, np=1, **hash-certified image** — fills the gap the earlier bind-mount row left | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…` vs stock `f0fcb488…`. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **0.33929 %** (`3.392911e-03`; AN `0.24149949` vs FD `0.24232166`), **zero flips** | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A4/shipped_optimisation_np1/RESULTS.md` §4 (`LADDER_A_STATUS.md` row 33) | `f9a59d47` |
| **G-21** | A4 **decomposition arms**: how far the parallel decomposition moves the same gradient | PATCHED † — patched IDWarp by bind-mount, np=4, **no md5 stated in these records** | provenance is the `IDWARP_IMPORTED_FROM:` stamp; the DAFoam side is the stock image `9d45679d55fd`. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`), with the decomposition disclosed as `DAFOAM_CHARTER.md` §5 requires | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **np=4 `scotch` 8.95 %** (AN `2.2086e-01` vs FD `2.4258e-01`) against **np=4 `simple` 4×1×1 0.00054 %** — a **~16,600×** split on one lever, same mesh, same objective. The published **10.04 %** is the same `scotch` artefact; the graded number is G-19's np=1 **1.10 %**. Axis: np=2 scotch 0.26 %, np=3 scotch 6.05 %, np=4 scotch 8.95 % | `NOT A RESULT` — **no pre-registered gate of its own**: the arms produced values and nothing was registered to grade them against, which is exactly what this family's freezes reserve the token for. **This is NOT a dismissal of the measurement** — the ~16,600× split is cited as evidence in `DAFOAM_CHARTER.md` §5 — it is the honest token for a survey, and the row is tiered `SURVEYED` for the same reason | **SURVEYED** | `cases/dafoam/DEFECT_REACH_decomposition_cases.md:33`, `:138`, `:447`; `cases/dafoam/ladder-a/A4_ahmed_body.md:196`, `:257-261` | `ddb99eca` |
| **G-22** | A5 U-bend, **4,800 cells** (not 21,000), np=1: `OBJ.val` wrt `shapexUpper`, 27 components | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | FD-vs-adjoint per component (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **46.840 %** (`4.684019e-01`); **2 sign flips** — idx8 at 205.52 %, idx17 at 121.86 % | `GATE FAIL` | **NOT HELD** | `cases/dafoam/ladder-a/A5/reverify_patched_idwarp_np1/RESULTS.md` §2 | `35171866` |
| **G-23** | A5 U-bend, rotation-patched | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…`. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint per component (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **2.768 %** (`2.768361e-02`); **0 flips**; **22 of 27 components within ±12 %**; idx16 **0.90 %**; **27 of 27 FD components bit-identical across arms** (`max \|FD_stock − FD_patched\| = 0.0`). Three registered predictions **missed and reported as misses** | `PASS` on the aggregate band, per-component caveat (§5 of the record) | **HOLDS** — zero flips; the five components outside ±12 % are named in the record's own caveat | same file §2, §5 | `35171866` |
| **G-24** | A6 CRM wing-alone, **579,072 cells**: the primal reaches a force-stationary state | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | primal gate, not the FD standard | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | force-stationary at CD **`0.02090143421526141`**; **tolerance never met** | `GATE REACHED` | **GATE REACHED** *(collision — see §0.1)* | `cases/dafoam/ladder-a/A6_crm_wingbody.md`; `cases/dafoam/ladder-a/A6/README.md` | `ddb99eca` |
| **G-25** | A6 full size: a full adjoint is feasible on this box | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | not reached — `Main iteration` and `KSP Residual` appear **zero times** in all four A6 logs | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | predicted peak RSS **94.7–116.0 GiB against a 30 GiB box** (5 models; de-biased 74.6 GiB) — **3.2×–5.8× short**; and **independently** blocked by conditioning, the same solver family stagnating at 79,560 cells with memory comfortable. *"This verdict is recorded from prediction, not from an OOM, and that is the point."* | `BLOCKED` (memory) **and independently** `BLOCKED` (conditioning) | **NOT HELD** — measured on this case (the prediction is the measurement, and it cost nothing) | `cases/dafoam/ladder-a/A6/adjoint_feasibility/RESULTS.md` §1 | `be35dcad` |
| **G-26** | A6 full size, rotation-patched, any adjoint scope | PATCHED — `dafoam-idwarp-rot:v1` | **no A6 adjoint of any kind exists at full size on either image**; nothing to hash | — | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` — NOT MEASURED | **NEVER RUN** | `cases/dafoam/ladder-a/A6/adjoint_feasibility/RESULTS.md` | `be35dcad` |
| **G-27** | A6 rung **N=16**, 41,760 cells, np=1: the adjoint linear solve converges | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | adjoint-convergence gate | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **517 GMRES iterations, `PetscConvergedReason: 2`**, monotone over six decades — **the first A6 adjoint that has ever existed** (A3 rung 2 needed 987 at the same size) | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A6/rung_n16_np1/RESULTS.md` §5 | `5d1718df` |
| **G-28** | A6 N=16 gradient against the **original** FD reference | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd` | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `CD`/`twist` **56.24–341.51 %, 3 sign flips**; **8 of 9 components > 15 %**; vector norm `8.893021e-01` | `GATE FAIL` | **NOT HELD** — and superseded as an **FD-reference artefact**, not an adjoint defect (row G-30); the frozen file is not edited | same file §6.1, §6.2 | `5d1718df` |
| **G-29** | A6 N=16 gradient against the original FD reference, rotation-patched | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…`. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `CD`/`twist` **57.06–340.70 %, 3 sign flips**; **8 of 9 > 15 %**; vector norm **`8.895816e-01`**; only `patchV` idx1 in band at **3.29 %**. **The patched image is not better** — identical on `patchV`, 0.028 pp *worse* in FD relative error. Patch effect analytic-vs-analytic: `CD`/`patchV` **bit-identical**, `CD`/`twist` moves **0.664 %** in L2 against 97–99.5 % for the same defect on A1/A2/A5 shape rows | `GATE FAIL` | **NOT HELD** | same file §6.2, §6.4, §9.2 | `5d1718df` |
| **G-30** | A6 N=16 gradient against a **fixed, noise-sized FD reference**, all nine components | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…`. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint at the mechanical noise-sized step rule (landed `4a6ea0b8`, blob `6b96fbd3`) | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **8 of 9 GRADED, aggregate 1.0432 %, zero sign flips**: `patchV`0 0.569 %, `patchV`1 0.940 %, `twist`0 1.706 %, `twist`1 1.359 %, `twist`2 1.733 %, `twist`3 1.817 %, `twist`4 1.032 %, `twist`5 0.389 %. **`twist` idx6 excluded by name — `NOT A RESULT`** (clearance 2.42×, plateau 83.53 %). The five bought here read 57.62 / 67.93 / 57.06 / 90.17 / 82.79 % at the predecessor's noise-dominated step — **the adjoint never moved** | `PASS` on the 8 graded; `NOT A RESULT` on `twist` idx6 | **SURVEYED** — 8 of 9 is not a rung, and **whether a subset PASS is a rung PASS is Sanaa's** (D464). The matrix does not read that gate | `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md`; the 3-component predecessor is `cases/dafoam/ladder-a/A6/rung_n16_fixed_reference/RESULTS.md` (`66f42398`) | `9d5029e8` |
| **G-31** | A6 N=16 gradient at the **fixed** FD reference on the **shipped** image | SHIPPED — `dafoam/opt-packages:latest` | **no arm was launched**; the fixed-reference record states in terms that it *"does not re-grade the shipped-toolchain row"* (`:13`, `:557`) | — | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` — NOT MEASURED | **NEVER RUN** | `cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md:13`, `:557` | `9d5029e8` |
| **G-32** | A6 rung **N=29**, 79,560 cells: adjoint + gradient | — no toolchain: no image was started | **nothing launched, staged or queued; $0.00 and 0 core-min spent** | — | **NEVER RUN** — A6's mesh family is **N=16 only**; N=29 was never launched, so no triple can exist and none was attempted (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` — not yet run: nothing launched, staged or queued, $0.00 and 0 core-min. **The gate wording is Sanaa's under D464 and is NOT read here**: two readings are registered (charter-verbatim → NOT MET on one flagged component; subset-complete → GATE REACHED) and **the choice between them is hers** | **NEVER RUN** | `cases/dafoam/ladder-a/A6/rung_n16_np1/RESULTS.md` §9.2; `cases/dafoam/ladder-a/A6/README.md`; `LADDER_A_STATUS.md` rows 28, 37 | `5d1718df` |
| **G-33** | B2 duct baselines: the lab reproduces the benchmark's published floor | OTHER — **plain OpenFOAM, not a DAFoam image and not an adjoint at all**; the host runs OpenFOAM **v2606** while the DAFoam container ships **v2506** (`DAFOAM_CHARTER.md` §6, `VERIFICATION_CHARTER.md:1168-1171`) | no patch; **and no DAFoam image was involved** — a DAFoam number and a plain-OpenFOAM number are not on the same toolchain even when both are "OpenFOAM" | **NOT the FD-vs-adjoint standard** — there is no adjoint here; the V column is a published-floor comparison | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **SURVEYED** — the primary is public: the closure-challenge benchmark's own published RANS floor `closure_challenge_rans_floor.json` (`AR_1_Ret_360` = **0.1288**), clone at `/home/ubuntu/closure-challenge-benchmark`. **But NO pre-registration for B2 exists on disk** — there is no `B2` `PREREGISTRATION.md` anywhere under `cases/dafoam/` — so the cell is **not P** (§3.5) | `AR_1_Ret_360` **0.1290** against the published floor **0.1288** (+0.0002, 0.16 %); CBFS field **0.068 %** scaled MAE against the benchmark's own baseline field; ~**30.9 core-min**; fork gap measured at **10–13 %** in iteration count and **0.02–0.09 %** in the fields | `PASS`, with two deviations disclosed in the record | **HOLDS** | `cases/dafoam/ladder-b/B2_duct_baseline.md` (`:24`, `:26`, `:132`, `:169`) | `ddb99eca` |
| **G-34** | B3 CBFS field inversion, 21,000 cells: **an adjoint gradient exists on the shipped toolchain** | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd`, `DALinearEqn.C` md5 `f6a89e33…`/507 lines with `PCILU` hard-coded at line 266 | not reached | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | adjoint GMRES **`PetscConvergedReason = -9` at iteration 0**, residual **`7.091590452305e-04`**; re-measured 2026-08-21 at np=4 **and np=1** — **the `-9` persists in serial** | `BLOCKED` | **NOT HELD** — measured on this case, four times | `cases/dafoam/ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` | `3f8c6b13` |
| **G-35** | The same claim against the sub-LU image — **the charter's own worked example that BOTH sentences are true** | PATCHED — `dafoam-subpclu:v2`, `DAFOAM_SUBPC_TYPE=lu` | `8352629516bb`; `DALinearEqn.C` md5 **`5b3159f88dbefcf7c52bd888401d097f`**, **539** lines, 4 occurrences; `diff v1 v2` = **13 added lines** in a branch neither arm of any recorded run enters (G2c), and host-patched stock md5 == in-image md5 (G2d). **Banner asserted in the log.** **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed, and `v1`'s build tree no longer exists.** | not the FD standard — this row grades the linear solve | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`PetscConvergedReason: 2`, 667 iterations**, every printed residual **bit-identical** to the 2026-08-04 run from an image rebuilt 17 days later; the 21,000-component gradient reproduces to every printed digit (**`‖g‖ = 1.4558046603e-05`**) | `PASS` | **HOLDS** | same file | `3f8c6b13` |
| **G-36** | B3: the gradient is invariant to the decomposition (G1/G2/G3), reference **D-serial** not D-scotch | PATCHED — `dafoam-subpclu:v2`, `DAFOAM_SUBPC_TYPE=lu`, all arms PCLU | `8352629516bb`, md5 `5b3159f8…`/539. **Nothing a reader can install reproduces this row.** | decomposition-invariance gate (`DAFOAM_CHARTER.md` §5), gradients mapped to serial cell order first | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | all three converge `reason 2` — **serial 163 it** (band 50–500; ASM block boundaries cost **4.09×** in Krylov count), **scotch 667**, **simple 766**. **G1 scotch-vs-serial `1.680861e-04` (0.01681 %)**, **G2 simple-vs-serial `1.415579e-04`**, **G3 simple-vs-scotch `1.132033e-04`** — all **< 1e-3**. Contrast with G-21's A4 8.95 % on the same lever: **the defect is real but case-selective** | `PASS` | **HOLDS** — *"the S1 line does not inherit a decomposition defect"* | `cases/dafoam/ladder-b/B3/decomposition_np4/RESULTS.md` §6, §8 | `bb5088c4` |
| **G-37** | B3: the **objective** is bit-identical across decompositions (G4) | PATCHED — `dafoam-subpclu:v2`, as G-36 | as G-36. **Nothing a reader can install reproduces this row.** | registered bit-identity gate | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | spread **1.9e-07** — reconvergence noise from a primal stopping on a 1e-06 tolerance at 1580/1582/1584 iterations, **not** something an ASM choice can cause | `GATE FAIL`, recorded as a **miss** | **NOT HELD** | same file | `bb5088c4` |
| **G-38** | B3: a **runtime** PETSc option can lift the `-9` (ILU shift / fill) | PATCHED — `dafoam-kspopts:v1` | `d9d2aed02e36`; `DALinearEqn.C` md5 `96f5762819e33efbdaad34181a214082`, **534** lines, `KSPSetFromOptions` relocated to line **351**; **built ON `dafoam-subpclu:v1`, so it carries the sub-LU patch too, env-gated and off**. **Nothing a reader can install reproduces this row: not filed upstream, never pushed.** | registered 5-arm discrimination | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **5 arms of 5** return `Total iterations: 0. PetscConvergedReason: -9.`, residual `7.091590452305e-04` to 13 digits, and **every arm's `-ksp_view` dump is byte-identical to the control's**. Proof they were *overwritten* not merely ineffective: arm L-2 requested fill level 2 and its own dump reads **`1 level of fill`**. **5 predictions registered, 5 hit, 0 missed.** `[NONZERO]` is **NOT** evidence the shift landed — it is present in the control, which set no shift option | `BLOCKED`, 5 arms of 5 | **NOT HELD** — the runtime axis is closed from both ends | `cases/dafoam/ladder-b/B3/ilu_shift_runtime/RESULTS.md` | `804c3fd8` |
| **G-39** | B3 **Stage 4** — the field inversion the rung exists for | SHIPPED — `dafoam/opt-packages:latest` | **no arm launched**; blocked by construction until the fix ships upstream or Sanaa adopts a forked toolchain | — | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `BLOCKED` by construction | **NEVER RUN** — the blocker is Sanaa's fork-adoption decision, not a measurement (see §0.2) | `cases/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` §3.4; `docs/dafoam/README.md` §3 | `804c3fd8` |
| **G-40** | S1 CBFS field inversion, capability rung: the β-field gradient agrees with FD on the **real objective seed** | PATCHED — `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE=lu`, banner asserted (the E-arms of the capability rung ran on stock `dafoam/opt-packages:latest`, stated in the record) | `ba2d16ab9d57`; md5 `89e71ca2…`/526/3 occurrences. **`v1`'s build tree no longer exists; `v2`'s G2c is what carries reproducibility of the numeric path. Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | FD-vs-adjoint on a per-cell field DV — **no warp in the chain** (`WARP PROBE: {"warper_init": 0, "warper_jacvec": 0}`), so the charter's 2.5–5 % harness floor, calibrated on shape derivatives through IDWarp, is **not the same instrument** | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **2.674 %** at h=1e-3 and **2.683 %** at h=1e-4 — *"step-independent, convergence-independent, and unexplained"*; tightening the primal 1000× (1e-8 → 1e-11) moved it 2.6739 % → 2.6728 %. Adjoint convergence: E1 kOmega **80 iters reason 2**, E2 kOmegaSST **91 iters reason 2** | `PASS` on the resolvable set (capability); **the 2.67 % FD disagreement is on the record as unexplained**; NASA-hump target `BLOCKED` (`-9` at iteration 0) | **SURVEYED** — the capability holds; the FD row itself grades nothing while it is unexplained | `cases/dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md:152-153`, `:204-211` | `ddb99eca` |
| **G-41** | S1/W4 CBFS: the **21,000-component β gradient** agrees with FD on three named cells | PATCHED — `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE=lu`, 4 ranks, banner asserted | `ba2d16ab9d57`, md5 `89e71ca2…`/526. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint per component, step 0.05, no warp in the chain (as G-40) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **0.085 % / 0.059 % / 0.199 %** (cells 5491, 6740, 12486) — *"step-limited, not noise-limited, which is the signature of a correct derivative measured against a resolvable objective"* | `PASS` | **HOLDS** | `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md:319-326`; summarised at `docs/dafoam/PRIOR_WORK_INVENTORY.md:1343` | `ddb99eca` |
| **G-42** | S1 CBFS **re-inversion**: FD re-anchor at the repaired objective | PATCHED — `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE=lu`, 4 ranks, banner asserted | `ba2d16ab9d57`, md5 `89e71ca2…`/526. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint, 3 components, `-primalTol 1e-8` | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **0.032 % / 0.115 % / 0.009 %**, no sign flips. **The 1e-6 protocol defect is on the record as a miss** and was fixed by amendment before this anchor | `PASS` | **HOLDS** | `cases/dafoam/ladder-b/S1_CBFS_REINVERSION_RESULT.md:92`, `:42` | `ddb99eca` |
| **G-43** | S1 CBFS **weighted arm**: FD gate B at the weighted objective | PATCHED — `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE=lu`, 4 ranks, banner asserted | `ba2d16ab9d57`, md5 `89e71ca2…`/526. **Nothing a reader can install reproduces this row.** | FD-vs-adjoint, 3 components, with a refpoint identity control (`5319` and `3591` printed exactly; `Jw_raw = 27.465931825190644` against the fixed 27.4659 cross-check) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **0.033 % / 0.007 % / 0.029 %**, one adjoint (**676 iters, reason 2**) | `PASS` (gate B) | **HOLDS** | `cases/dafoam/ladder-b/S1_CBFS_WEIGHTED_ARM_RESULT.md` | `ddb99eca` |

---

## 2. Adjoint-optimization rows

For these rows the **measured statistic is the optimiser's own termination string**, and the V
column is the mandatory **endpoint FD check at the final design point** (`DAFOAM_CHARTER.md` §9).

| id | claim verified | toolchain | patch provenance | V — code verification (FD-vs-adjoint) | G — grid convergence | P — validation vs public primary | measured statistic (termination string) | lab verdict | matrix tier | record | sha |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **O-01** | A2 MACH wing, 38,304 cells, np=4: an IPOPT drag minimisation converges | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd`, md5s as G-01 | **no endpoint FD check exists** — the run never reached an accepted optimum | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`null` — IPOPT prints no `EXIT` line and no convergence statement anywhere in `opt_IPOPT.txt`; the table simply stops after iteration 47. Verified by grep: zero occurrences of `EXIT`** (`opt_IPOPT.txt`, sha256 `638504c1c412ee5254e1d90b7967764c3f6461a70d339f735fb6f9f039011036`, 6,546 bytes). 47 of ~100 majors; `converged_to_optimizer_tolerance: false`; `inf_pr 1.44e-05` / `inf_du 9.0e-05` against `tol 1e-5`; **28.275488 %** drag reduction at the point the 60-minute clock stopped; **it destroyed its own case directory** | `NOT A RESULT` (time-boxed, unconverged) | **SURVEYED** | `cases/dafoam/ladder-a/A2/grading_confirmation/RESULTS.md` §4 (`:132-149`) | `35171866` |
| **O-02** | A2 optimisation on a patched toolchain | PATCHED — `dafoam-idwarp-rot:v1` | **no patched A2 optimisation arm was ever launched**; nothing to hash | — | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` — NOT MEASURED | **NEVER RUN** | `LADDER_A_STATUS.md` (no A2 optimisation row on the patched column; rows 4, 5, 34, 35 are gradient rows) | `b840fcd5` |
| **O-03** | A4 Ahmed, 2,777 cells, np=1: **the lab's first converged optimisation** | PATCHED — `dafoam-idwarp-rot:v1` | `2927768a16ac`, `libidwarp.so` md5 `85f59e87…` vs stock `f0fcb488…`. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | endpoint FD at the optimised design: **0.4936 %** (`4.936157e-03`; AN `2.141012e-01` vs FD `2.151633e-01`), **zero sign flips**, clearance 453× — the lab's first gradient graded at a *deformed* design point. Registered charter-2c trivial baseline (`scaler=-1.0`) behaved as designed: CD **rose 9.090 %**, `shape` ran to the opposite corner `+0.04992374` → `NOT A RESULT` | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`EXIT: Optimal Solution Found.`**, **9 majors**, NLP error `6.2814e-07` < `tol 1e-6`; CD `0.15297385` → **`0.14153492`, −7.47770 %**; `shape` **−0.04999982** at the bound, feasible. **It did not stop on the iteration cap**, so the `GATE REACHED` ceiling of the prereg §9 does not bind | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A4/first_optimisation_np1/RESULTS.md` §2, §3, §4, §8 | `5d1718df` |
| **O-04** | The same A4 optimisation on the **shipped** toolchain | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — `9d45679d55fd`, md5s as G-01 | endpoint FD at the optimised design, shipped: **0.3112 %** (`3.111803e-03`; AN `0.21410204` vs FD `0.21477037`), zero flips. **Not a toolchain comparison against O-03's 0.4936 %**: the analytic gradients agree to `3.9e-06`, the FD references differ by `1.83e-03` (L-229) | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`EXIT: Optimal Solution Found.`**, **6 majors**, NLP error **`6.9114020645938298e-08`** < `tol 1e-6`; CD `0.1529738469354696` → **`0.14153518384107486`**, **−7.47753 %**; `shape` = `-0.05` exactly at the bound. Same optimum as O-03 to 7 significant figures | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A4/shipped_optimisation_np1/RESULTS.md` §1–§3 (`:13-18`, `:75-84`, `:410`) | `f9a59d47` |
| **O-05** | **Curriculum D1** — A1 NACA0012 **lift-constrained** drag minimisation, np=1: a constrained optimisation converges and its endpoint gradient is verified | PATCHED — `dafoam-idwarp-rot:v1` (arm O) | `2927768a16ac` (`sha256:2927768a16ac…f6d35`); `IDWARP_SO_MD5` printed **from inside the process that loaded the library**: `85f59e87253e0a71a813f64ca6e4c425`. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | endpoint FD at the design point the optimiser actually reached: **≤ 0.2553 % on 4 of 4 named components, zero sign flips**, steps chosen from `\|J_adj\|` and η alone before any FD value existed (η measured at `1.957349804806996e-08`). Registered trivial baseline at 1e-8: **112.6004 %**, sign-flipped | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`EXIT: Optimal Solution Found.`**, **11 major iterations**, `Overall NLP error 4.0871293161759560e-07` against `tol 1e-5`; **`CL = 0.5` to `1.879064e-07`**; all **24** geometric constraint rows inside their registered bounds; CD `0.020943920630946831` → `0.017527899854535338` = **−16.310321 %** | `PASS` | **HOLDS** | `cases/dafoam/ladder-a/A1/curriculum_D1/RESULTS.md` §1, §4 (results `b10260a0`; item CLOSED at `cffd90e7`) | `b10260a0` |
| **O-06** | **Curriculum D1-C′** — the **shipped-image endpoint gradient at arm O's own converged design point**, which closes D1's shipped row | SHIPPED — `dafoam/opt-packages:latest` | shipped image, no patch — digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` re-read from `docker images --no-trunc` in the launch invocation; `IDWARP_SO_MD5` printed from inside the loading process: **`f0fcb488e0e98156575cd19548e91663`** (stock, **not** `85f59e87…`) — the arm demonstrably ran the stock library | FD-vs-adjoint at the same two-step test as the patched row beside it — *"a shipped row graded on a weaker test than the patched row beside it is not a comparison"*. Graded rung `s_hi`: `shape[6]` **0.052732 %**, `shape[5]` **0.122770 %**, `shape[1]` **0.163546 %**, `patchV[1]` **0.255088 %** — **four components ≤ 0.2551 %, zero sign flips, all four GRADED**, `C_measured` 345–1193 against a floor of 5. The `s_lo` rung was bought, not absorbed: 0.096322 / 0.375922 / 0.298749 / 0.734110 % | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | endpoint gradient row — no optimiser ran in this mini-item; the design point is arm O's, consumed from the freeze | `PASS` (G-C1), all ten gates PASS, no falsifier fired. **`P5` was a registered POINT PREDICTION, not a gate.** It predicted the SHIPPED row would grade `GATE FAIL`, driven by `shape[6]` > 15 %; the row graded `PASS`, so **P5 is a MISSED PREDICTION** and is reported as a MISS, not adjusted (`RESULTS.md:30`, `:245`). **It is not a failed gate** — all ten gates PASS and no falsifier fired, and the two statements are therefore not in tension. Shipped and patched analytic gradients differ by at most **`5.16e-08` absolute / `2.80e-06` relative** at this design point, against a predicted `6.76e-03` / 640 % from the baseline A/B pair — **five orders of magnitude smaller**; both registered hypotheses H1 and H2 are falsified. **MANDATORY QUALIFIER, carried wherever this row is lifted:** the record states the design-point dependence of the stock IDWarp `warpDeriv` defect as *"a conjunction of two measurements, not a mechanism"* — catastrophically wrong at the undeformed baseline (640 %, sign-flipped at idx6) and indistinguishable from patched at arm O's converged design point (≤ 2.8e-06 relative). **THE MECHANISM IS UNTESTED.** The degenerate-`getRotationMatrix3d`-branch explanation is *"a hypothesis this run did not test"* and *"speculation until a registered arm measures the defect against rotation magnitude"* (`RESULTS.md:274-286`). The discriminating arm is `D` candidate **`D901`** — **not costed, not registered, not launched** | **HOLDS** | `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md` (graded `5bec45b7`; Addendum 1 `c4ce2b8f`; D1 CLOSED and Addendum 2 at `cffd90e7`) | `cffd90e7` |
| **O-07** | **Curriculum D2 arm A** (IPOPT) reproduces D1 arm O and converges | PATCHED — `dafoam-idwarp-rot:v1` | `IDWARP_SO_MD5` `85f59e87253e0a71a813f64ca6e4c425` printed from inside the loading process, both arms; `D1_CONTAINER_UID: 0`; `nProcs : 1`. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | endpoint FD, 4 of 4 GRADED, zero flagged, zero sign flips, worst **0.2553 %**; trivial baseline **112.6004 %** sign-flipped at 1e-8 | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`EXIT: Optimal Solution Found.`**, `Overall NLP error 4.0871e-07 < 1e-5`; **AB5 reproduces D1 arm O with all five continuous rows exactly `0.0` and majors `11 = 11`**; `\|CL − 0.5\| = 1.8791e-07`, 23 of 23 geometric rows inside | `PASS` (G-A1…G-A4, AB5) | **HOLDS** | `cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md` §1, §2 | `b840fcd5` |
| **O-08** | **Curriculum D2 arm B** (SLSQP) on a byte-identical run script, one CLI token apart | PATCHED — `dafoam-idwarp-rot:v1` | as O-07: `85f59e87…` read in-process, `nProcs : 1`, `--user 0:0`. **Nothing a reader can install reproduces this row.** | endpoint FD, 4 of 4 GRADED, zero flagged, zero sign flips, worst **0.2485 %**; trivial baseline **111.8888 %** sign-flipped at 1e-8 | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | pyOptSparse **`Inform = 0`, "Optimization terminated successfully."**; `\|CL − 0.5\| = 2.5566e-06`, 23 of 23 geometric rows inside | `PASS` (G-B1…G-B4) | **HOLDS** | same file §1 | `b840fcd5` |
| **O-09** | **D2 AB1** — two optimizers reach the same **objective value** | PATCHED — `dafoam-idwarp-rot:v1`, both arms | as O-07. **Nothing a reader can install reproduces this row.** | the A/B band was frozen before either arm ran | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | `Δrel = **0.7381 %**`, inside the registered `≤ 1.0 %` band. **The `< 0.10 %` point was NOT met** and is reported as not met | `PASS` | **HOLDS** | same file §1 | `b840fcd5` |
| **O-10** | **D2 AB2** — two optimizers reach the same **design point** — **the item's REGISTERED FINDING** | PATCHED — `dafoam-idwarp-rot:v1`, both arms | as O-07. **Nothing a reader can install reproduces this row.** | band frozen before either arm ran: `L2`-relative **10.0 %**, `L∞` **8.0e-03**, `\|ΔAoA\|` 0.25 deg | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **`‖Δshape‖₂ / ‖shape_A‖₂ = 33.259 %`** against the 10.0 % band; **`‖Δshape‖_∞ = 1.9379e-02`** against 8.0e-03 — *more than twice `shape[6]`'s entire value*; `\|ΔAoA\| = 0.2428` deg, inside. **AB1 passes and AB2 fails, and that combination is the result**: on this NLP the objective is close to flat along the direction that separates the two designs. **It is a statement about the two algorithms and the problem's conditioning, and is NOT an aerodynamic finding** | `GATE FAIL` — the item's registered finding, not a defect of the item | **NOT HELD** | same file §1 | `b840fcd5` |
| **O-11** | **D2's trust-region half** — the ratified curriculum row promised *"optimizer/trust-region behavior as a measured comparison"* | PATCHED — `dafoam-idwarp-rot:v1` (the graded image) | the image carries **no importable trust-region optimizer**: `ParOpt` ships as a package directory with **no compiled extension**; `SNOPT` and `NLPQLP` are absent. Measured by a **0.0333 core-min probe BEFORE the freeze**, disclosed on the pre-registration's first screen. **Nothing about building `ParOpt` was run or prepared.** | — | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `BLOCKED` — a **0.0333 core-min probe run BEFORE the freeze** measured that the precondition is absent: no trust-region optimizer is importable on the graded image. **The record's own status phrase is `NOT DELIVERED BY CONSTRUCTION`, which is NOT a member of the six-token vocabulary**; it is quoted here, not translated, and flagged in §5 item 7 as a DAFoam record's own defect. `BLOCKED` is entered because the verdict column must carry a token and that is the one the measured facts support | **NOT HELD** — **RETIERED BY THIS AUDIT.** The first draft tiered this row `NEVER RUN`, which **its own §0.2 map does not support**: §0.2 reserves `NEVER RUN` for zero compute with a blocker that is a standing decision, and here compute was spent and the blocker was **measured on the image itself**. §0.2's `BLOCKED` split puts it in `NOT HELD` | same file §1, §3.1 | `b840fcd5` |
| **O-12** | D2 on a **shipped** toolchain | SHIPPED — `dafoam/opt-packages:latest` | **no shipped arm was launched**; both D2 arms are patched rows and neither stands in for a shipped row | — | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` — NOT MEASURED | **NEVER RUN** | same file §1 (*"Both arms are patched-toolchain rows (R11)"*) | `b840fcd5` |
| **O-13** | **Curriculum D3 attempt 1** — A4 Ahmed **constrained** drag minimisation | PATCHED — `dafoam-idwarp-rot:v1` | `libidwarp.so` md5 **`85f59e87253e0a71a813f64ca6e4c425`** read at run time **from inside the process that loaded the library** (`geom.log:4`), imported from `/opt/idwarp_patched/idwarp/__init__.py`; `nProcs : 1` asserted at `geom.log:14, 23, 194, 450`. **Nothing a reader can install reproduces this row: not filed upstream, no image ever pushed.** | never reached — Stage G is a geometry probe that buys no flow solve | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **no optimiser ran.** Stage G crashed inside `prob.setup()` at the first `DVConstraints` call: `nom_addThicknessConstraints2D` and `nom_addVolumeConstraint` are called **without ever registering a triangulated surface** with the `DVConstraints` object. **0.30 core-min of a 29.8 core-min budget** — about 1 % of the item's predicted price. **Nothing was repaired; no frozen file was edited; no second budget was taken** | `BLOCKED` (a precondition prevented the measurement — **not** `NOT A RESULT`, which the freeze reserves for a value produced and ungradeable) | **NOT HELD** | `cases/dafoam/ladder-a/A4/curriculum_D3/RESULTS.md` | `616a2c8c` |
| **O-14** | **Curriculum D3 attempt 2** — the same claim after the two-line repair | PATCHED — `dafoam-idwarp-rot:v1` | as O-13: `85f59e87253e0a71a813f64ca6e4c425` printed **LIVE from inside the loading process** (`geom.log:4`) by the launcher's in-process `hashlib.md5` before `mpirun` was reached; `nProcs : 1` asserted. **Nothing a reader can install reproduces this row.** | never reached | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | **no optimiser ran.** The repair worked — attempt 1's `KeyError: 'Need to add surface "default"'` appears **0 times** in this run's 492-line `geom.log`, `prob.setup(mode="rev")` completed and the process ran past `om.n2` into the `geom_probe` block. **It died at the first line of that block**: `runScript.py:261` → `:253` `pts = dvg.update("aero")` → pyGeo `DVGeo.py:2012` → `pyBlock.py:745` → **`KeyError: 'aero'`** — no point set named `"aero"` is embedded in the FFD. **Falsifier class `F1c` (DOWNSTREAM-PRODUCER), decided mechanically by the final producer frame's line number (261) against the registered G11(d) rule; `P15` MISS.** **2.8667 core-min of the 69.2 HARD ceiling; 66.3333 unspent and not carried anywhere.** Stages η, O and T were not launched | `BLOCKED` at Stage G | **NOT HELD** | `cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/RESULTS.md` (graded `10b3e97c`) | `10b3e97c` |
| **O-15** | D3 on a **shipped** toolchain (Stage T-shipped) | SHIPPED — `dafoam/opt-packages:latest` | **no container of this image was started in either attempt**; the shipped hash is **inherited from the A4 record and NOT re-verified** by this item | — | **NEVER RUN** — no Roache triple, no GCI and no observed order exists anywhere in this family (§3.4) | **NEVER RUN** — no validation against a public primary (§3.5) | — | `PENDING` | **NEVER RUN** | `cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/RESULTS.md` §1; attempt 1 §1 | `10b3e97c` |

---

## 3. The honest limits of this family's V column

**These three sentences are load-bearing and are not a caveat paragraph. A reader who lifts a row
above without them has taken a number and left its meaning behind.**

### 3.1 There is no exact solution and no manufactured solution for a discrete adjoint gradient here

**This family has NO exact solution and NO manufactured solution for the quantity it verifies.**
The verified object is the derivative of a *discretely converged* objective with respect to a
design variable, through IDWarp's mesh warp, pyGeo's FFD and DAFoam's reverse-AD tape. Nothing in
the lab manufactures that quantity in closed form. **The entire V column of every row above
therefore rests on finite differences** — a second numerical approximation of the same discrete
object, with its own step-size, plateau and noise-floor failure modes. That is the family's
honest-limit statement, and the V standard
`docs/dafoam/V_STANDARD_FD_VS_ADJOINT.md` (landed `4a6ea0b8`, blob `6b96fbd3`) carries it in its own honest-limit
section.

**The cost of that limit has been paid on the record twice.** A6 rung N=16 `GATE FAIL`ed on both
images (G-28, G-29) and the measured cause was **the FD reference, not the adjoint**: a primal
stopping 556× short of tolerance leaves a derivative noise floor of `4.5e-3` that 8 of 9 FD
magnitudes never cleared. Fixing the reference — not the adjoint, not the toolchain — turned the
same components into an aggregate **1.0432 %** with zero sign flips (G-30). *"A converged adjoint
can outrun its own FD reference."* Conversely, the same test on A4 gives **453× clearance** and a
clean 0.4936 % PASS. **The discriminator between the two is whether the primal converged — not the
toolchain, not the DV class, not the mesh size.**

### 3.2 No complex-step build exists on this box, and the forward-AD build does not reproduce the plain primal (D460)

The two routes that would have escaped the FD limit are both closed here:

- **Complex step: no build exists on this box.** There is no complex-arithmetic DAFoam or
  OpenFOAM build in any of the five images, and none has been made. `DAFOAM_CHARTER.md` §2
  requires a record that does not reach for forward-AD or complex step to **say why**; this is the
  why, and it is a capability gap, not a choice.
- **Forward AD (ADF) is present and does not reproduce the plain primal — docket item D460.** The
  ADF library ships in all three images (`libDASolverADF.so`, rebuilt in the patched images and
  measured at 9,534,512 B in `subpclu:v2`), so the route looks available; it is not. Sweep 1 of
  D460 closed **PASS**, class **CONDITIONING / DIAGNOSABILITY**, and the defect draft
  `cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` records the non-reproduction. That
  draft's filing-readiness was reassessed and is **`NOT READY`** with 11 missing items, and it is
  **NOT FILED** and stays that way — filing is Sanaa's alone. **Sweep 2 is UNRUN AND UNAUTHORISED.**
  The precedent this sets is the one the curriculum now carries into every new capability:
  a *"supported"* feature returned NaN on the A6 forward-AD probe, so **no capability is promised
  before its probe**.

### 3.3 Every PATCHED row is unreproducible by any reader

**Restated here as a section because it is the single most misreadable property of this
contribution.** Every row in §1 and §2 whose toolchain cell reads PATCHED — including the `‡`
rows, which ran on a patched *image* in stock *mode* — carries numbers that **no reader outside
this box can reproduce**:

- **Nothing has been filed upstream.** All five defect classes (D-A/D-A2 IDWarp
  `getRotationMatrix3d`; D-B/D-B2 the decomposition adjoint and the serial `cellLimited` limiter;
  D-C `KSPSetFromOptions`; D-E the ASM sub-block ILU exact zero pivot; and the ADF
  non-reproduction) are prepared, drafted **NOT FILED**, and parked. **63 recorded searches across
  10 venues** answered the novelty question; only the filing decision is open, and it is Sanaa's.
- **No image has ever been pushed to a registry.** All five are local to this box.
- **The rotation fix is in no image at all** and cannot be obtained by choosing a tag: IDWarp ships
  as a built package with no Fortran sources in any of the three images, so the patched library
  exists only as a host-side clone injected by bind-mount and `PYTHONPATH`, and it still reports
  version `2.6.2`. **The version string cannot tell a patched run from a stock one** — which is
  why every such run prints `IDWARP_IMPORTED_FROM:` and, where an image was used, its
  `IDWARP_SO_MD5`.
- **One patched image cannot be rebuilt bit-for-bit if a host directory is lost**:
  `dafoam-idwarp-rot:v1` COPYs a prebuilt `.so` from
  `/home/ubuntu/certonomous-runs/W5-patch/idwarp`.
- **`dafoam-subpclu:v1`, which produced every recorded sub-LU number, was built in a scratch tree
  that no longer exists.** What replaces bit-reproducibility is `BUILD.md` §4.2 gate G2c, and the
  claim it supports is narrower and stated as such.

**A reader who installs DAFoam 5.0.0 with OpenFOAM v2506 and PETSc 3.15.5 gets the SHIPPED rows and
none of the PATCHED ones.** That is the whole reason the two are never merged into one cell.

### 3.4 The G column: this family has NO Roache triple, anywhere — and the two near-misses are named

**`G` requires a `CONVERGING` Roache triple with a GCI and an observed order** (`CLAUDE.md`
rule 5). **This family has none, on any case, on any toolchain.** Measured over
`cases/dafoam/**/*.md` and `docs/dafoam/**/*.md`:

- `GCI` — **zero occurrences**.
- `observed order`, `order of accuracy`, `grid triple`, `grid convergence` — **zero occurrences**.
- `Roache` — **one occurrence**, and it is a *future* curriculum item: `EXPERTISE_CURRICULUM.md:125`,
  item **D14**, *"ties Roache discipline into design claims"*. **D14 has never been run.**

**Every G cell in §1 and §2 therefore reads `NEVER RUN`.** It is not blank, and it is **not
borrowed from a primal study** — no DAFoam row inherits a grid-convergence cell from anywhere.

**Two mesh families exist and neither is a triple. Both are named in the G cells that touch them,
so nobody concludes a triple was hidden:**

1. **A3 ONERA M6 — three mesh levels, 21,840 / 42,120 / 79,560 cells.** This is the closest thing
   in the family to a grid family, and it is **not a Roache triple**: it was launched as an
   adjoint-feasibility sweep, no pre-registration ever registered a triple, and the **third level
   produced no gradient at all** — `reason −3` at the 4,000-iteration cap (G-11). No GCI and no
   observed order was computed on any of the three.
2. **A6 CRM — N=16 (41,760 cells) only.** N=29 (79,560 cells) was **never launched, staged or
   queued** (G-32), so the family has one level and a triple is not merely unanalysed but
   impossible from what exists.

**The honest consequence, stated for the matrix's owner:** on the G column this family is
**uncovered end to end**, and a grid-convergence claim for any DAFoam gradient in this lab would
today have to be **`NOT A RESULT`** under `CLAUDE.md` rule 5, because there is no triple to grade
and no GCI may be quoted where three monotone values do not exist.

### 3.5 The P column: two public primaries, and no pre-registration behind either

**`P` requires validation against a PUBLIC PRIMARY *and* a pre-registration ON DISK.** The cell
names both or the cell is not P. **Fifty-six of the fifty-eight rows have no public primary at
all** and read `NEVER RUN`: FD-vs-adjoint compares a gradient against a second numerical
approximation of the *same* discrete object, which is code verification and is not validation.

**Two rows name a real public primary. Neither has a pre-registration, so neither is a P cell, and
both read `SURVEYED`:**

| row | public primary | archived where | pre-registration |
|---|---|---|---|
| **G-16** A3 surface `Cp` | **AGARD AR-138 Case 2308**, Schmitt & Charpin 1979, via the NASA-TMR mirror | `cases/dafoam/ladder-a/logs_A3/case_2308.dat`, 22,695 B, on disk | **NONE.** `cases/dafoam/ladder-a/A3/grading_confirmation/` contains **only** `RESULTS.md`; no `PREREGISTRATION.md` exists there, and of the eighteen A3 pre-registrations on disk **not one registers a `Cp` gate** — the single AGARD mention anywhere in them is a flow-condition note (`A3_SUBLU_PREREGISTRATION.md:15`) |
| **G-33** B2 duct baselines | the closure-challenge benchmark's own **published RANS floor**, `closure_challenge_rans_floor.json` (`AR_1_Ret_360` = **0.1288**) | `/home/ubuntu/closure-challenge-benchmark` (outside the repo by design) | **NONE.** There is no `B2` pre-registration anywhere under `cases/dafoam/` |

**Why `SURVEYED` and not `HOLDS`.** Both comparisons were *made* and both are on the record with
numbers — A3's `Cp` at pressure-surface RMS **0.0128–0.0265** and B2's duct score at **0.1290**
against the **0.1288** floor. But §0.2 reserves `HOLDS` for a claim tested against a
**pre-registered** gate, and neither comparison had one. **A post-hoc comparison against a public
primary is a survey, not a validation**, however good the number is — that is `VERIFICATION_CHARTER.md`
§2b's whole point, and writing `HOLDS` here would be the exact failure the freeze rule exists to
prevent. Both rows keep their own lab verdicts (`PASS`) unchanged; it is the **P column** that
cannot be claimed.

**A cheap repair exists and is not taken here.** Either comparison could become a P cell by
pre-registering the gate *before* re-running the comparison. Neither is proposed, costed or
launched by this document.


---

## 4. Tier census

**WITHDRAWN AND REPLACED. The census shipped in this document's first draft did not reproduce from
the command that document said produced it, and the disclosure comes before the new numbers.**

> **What was wrong, stated plainly rather than quietly corrected.** The first draft's §4 opened
> *"Derived from the tables in §1 and §2 by the command below, not by counting in prose"* and then
> shipped a table its own command does not produce. Running that command verbatim printed
> **`TOTAL 58`** and roughly **thirty** buckets; the table carried five tier rows summing to
> **51**. Two adjacent sentences in the same paragraph asserted **51** and **58**. **58 is right.**
>
> **Two independent defects in the instrument, both now fixed:**
> 1. **It bucketed on the whole tier cell, not on the tier token.** After `gsub(/[* ]/,"",g)` it
>    keyed on the entire cell, so `HOLDS` and
>    `HOLDS — and it is the first measured A/B pair on this ladder that degrades (N-D18)` became
>    **two different buckets**. Every tier cell carrying explanatory prose — deliberately, many of
>    the best ones — became its own singleton. That alone shatters a census.
> 2. **It read `$4` and `$11` by position while five rows were structurally broken.** Five data
>    rows carried a **literal `|` inside cell text** (norm and absolute-value notation, some of it
>    inside code spans — backticks do **not** protect a pipe in a markdown table). Those rows split
>    into 14 and 16 fields instead of 12, so **the lab verdict and the matrix tier rendered in the
>    wrong columns** and the census misbucketed them on *both* the toolchain and the tier axis. The
>    five were `G-23`, `O-05`, `O-07`, `O-08`, `O-10`. **All five are now escaped as `\|`** and
>    every data row is asserted to have the correct field count.
> 3. **It bucketed the toolchain axis on `SHIPPED` first.** A `‡` row's cell reads
>    `PATCHED‡ (stock mode) … the record calls this **SHIPPED-equivalent**` — it contains **both**
>    words, so a `SHIPPED`-first test silently contradicted §4's own stated bucketing decision. The
>    repaired command buckets on the **leading token** of the toolchain cell, which is the decision
>    §4 always said it was making.
>
> **The errors ran in the conservative direction** — the withdrawn table made this family look
> slightly *worse* covered than it is (`HOLDS` understated by 6, `NOT HELD` overstated by 1). That
> is the right direction to err in and it is **still wrong**: a coverage matrix consumed by another
> team is wrong whichever way it leans.
>
> **The instrument-level lesson, which is why the new command REFUSES rather than warns.** An
> aggregation instrument that cannot say *"I could not count this row"* will report a number it did
> not count — which is exactly what happened: the old `awk` invented junk buckets instead of
> refusing, and the `51` went onto the page. This is `CLAUDE.md` standing rule 3 (the planted-zero
> control) applied to an aggregator, and it is **the same defect family** the DAFoam supervisor
> ruled on in curriculum D3 the same day, where a grader swallowed a `TypeError` and reported
> declared constants as measured. **Two independent instances, two different parts of this family,
> one session.**

### 4.0 The census command — self-checking, and it refuses

Paste and run from the repository root. The leading `sed` neutralises the escaped `\|` inside cell
text so the field split is on real cell delimiters only.

```
sed 's/\\|/@/g' cases/dafoam/MATRIX_CONTRIBUTION.md | awk -F'|' '
/^\| \*\*[GO]-[0-9]+\*\* \|/ {
  if (NF != 14) { printf "REFUSED: row %s has %d fields, expected 14\n", $2, NF; bad++; next }
  g=$11; gsub(/\*/,"",g); sub(/ —.*/,"",g); sub(/ \(.*/,"",g); gsub(/^[ \t]+|[ \t]+$/,"",g)
  if (g!="HOLDS" && g!="GATE REACHED" && g!="SURVEYED" && g!="NOT HELD" && g!="NEVER RUN") {
    printf "REFUSED: row %s unrecognised tier [%s]\n", $2, g; bad++; next }
  t=$4; gsub(/^[ \t*]+/,"",t)
  b = (t ~ /^PATCHED/) ? "PATCHED" : (t ~ /^SHIPPED/) ? "SHIPPED" : "OTHER"
  c[g "|" b]++; tier[g]++; tool[b]++; n++; if ($2 ~ /G-/) gr++; else opt++ }
END { for (k in c) print "  " k, c[k]
  printf "ROWS %d (G %d + O %d)\n", n, gr, opt
  s=0; for (k in tier) s+=tier[k]
  if (bad>0) { print "CENSUS REFUSED: " bad " row(s) uncounted"; exit 2 }
  if (s!=n)  { print "CENSUS REFUSED: buckets != rows"; exit 2 }
  if (gr!=43 || opt!=15) { print "CENSUS REFUSED: not 43 G-rows + 15 O-rows"; exit 2 }
  if (n!=58) { print "CENSUS REFUSED: rows != 58"; exit 2 }
  print "CENSUS OK" }'
```

**Four self-checks, each of which EXITS 2 rather than printing a warning:** any row whose field
count is not 14; any row whose tier is not one of the five words; tier buckets not summing to the
row total; and the row total not equal to **43 G-rows + 15 O-rows = 58**.

**The refusals are PLANTED AND PROVED, not asserted** (`CLAUDE.md` rule 3 — a checker not shown
able to fail is not evidence). Three controls were run against mutated copies of this file and all
three refused with `exit 2`, while the real file returns `CENSUS OK` with `exit 0`:

| planted control | what the command did |
|---|---|
| one extra literal `\|` inserted into `G-19` | `REFUSED: row **G-19** has 15 fields, expected 14`, **exit 2** |
| `G-01`'s tier mutated to `MOSTLY HELD` | `REFUSED: row **G-01** unrecognised tier [MOSTLY HELD]`, **exit 2** |
| row `G-03` deleted entirely | `CENSUS REFUSED: not 43 G-rows + 15 O-rows`, **exit 2** |
| **the file as shipped** | `ROWS 58 (G 43 + O 15)` … `CENSUS OK`, **exit 0** |

### 4.1 Census as tiered — built FROM the command's output, not adjusted toward it

**Bucketing decision, unchanged in substance and now actually implemented.** SHIPPED and PATCHED
split on **the image's identity, which is its hash** (`DAFOAM_CHARTER.md` §6), read off the
**leading token** of the toolchain cell. The `‡` rows — `dafoam-subpclu:v1` run with
`DAFOAM_SUBPC_TYPE` unset, described in their own records as *SHIPPED-equivalent* — therefore count
as **PATCHED**, because the image carries a patch even where the run does not exercise it. Two rows
are **OTHER**: `G-33` (B2, plain host OpenFOAM, no DAFoam image) and `G-32` (A6 N=29, no image was
ever started).

| matrix tier | SHIPPED | PATCHED | OTHER | **row total** |
|---|---|---|---|---|
| **HOLDS** | 6 | 17 | 1 | **24** |
| **GATE REACHED** | 2 | 0 | 0 | **2** |
| **SURVEYED** | 2 | 7 | 0 | **9** |
| **NOT HELD** | 6 | 9 | 0 | **15** |
| **NEVER RUN** | 4 | 3 | 1 | **8** |
| **column total** | **20** | **36** | **2** | **58** |

**Total rows: 58 = 43 adjoint-gradient rows (`G-01`…`G-43`) + 15 adjoint-optimization rows
(`O-01`…`O-15`).** The id ranges are contiguous and the census counts every id exactly once; the
command refuses if that stops being true.

**Every G cell is `NEVER RUN` (58 of 58) and every P cell is `NEVER RUN` except two, which are
`SURVEYED`** (§3.4, §3.5). Those two columns are deliberately **not** folded into the table above,
which tiers the **row**, not its columns.

**Cross-check against an independent count.** The DAFoam supervisor ran an independent census on
the pre-repair file and reported `HOLDS 20, NOT HELD 13, SURVEYED 9, NEVER RUN 9, GATE REACHED 2`
over the 53 rows that bucketed cleanly, with 5 rows uncountable. Adding the five repaired rows
(`G-23`, `O-05`, `O-07`, `O-08` → `HOLDS`; `O-10` → `NOT HELD`) gives `HOLDS 24, NOT HELD 14,
SURVEYED 9, NEVER RUN 9, GATE REACHED 2`. **The one remaining difference is `O-11`**, which this
audit **retiered from `NEVER RUN` to `NOT HELD`** — moving one row and reconciling the two counts
to the digit. The reason is in `O-11`'s own tier cell and in §5 item 7.

### 4.2 The census's own honesty clause

**The table in §4.1 is a reading, not an authority.** It was derived by the command in §4.0 and is
correct only for the row set present when it was run. Any row added, split or retiered changes it.
**Re-run the command; do not trust the table.** Three structural facts a re-runner needs:

1. **The first draft of this document shipped a census that did not reproduce from its own
   command** — the whole of §4's opening block. That is disclosed rather than quietly corrected,
   and it is why the self-checks in §4.0 exist and why they exit rather than warn. **The
   authority of this document rests on saying so.**
2. The `‡` bucketing decision is a judgement, not a measurement. Counting the `‡` rows as SHIPPED
   instead would move **3** rows (`G-07`, `G-09`, `G-11`) from PATCHED to SHIPPED, giving
   **23 / 33 / 2**. Both readings are legitimate and the verification supervisor may choose.
3. Control and trivial-baseline arms are **not** rows (§0.2), so the census counts coverage claims,
   not containers started. The DAFoam family has started far more containers than this table has
   rows.

### 4.3 What the census says when read down the columns

- **The PATCHED column is nearly twice the SHIPPED column (36 to 20), and every one of those 36
  rows is unreproducible by any reader** (§3.3). A coverage matrix that merged the two would report
  this family as far better covered than it is.
- **`NEVER RUN` is 8 rows and 4 of them are SHIPPED**: `G-31` (A6's fixed-reference regrade on the
  shipped image), `G-39` (B3 Stage 4), `O-12` (D2's shipped arm) and `O-15` (D3's shipped arm). The
  patched column has 3 (`G-18`, `G-26`, `O-02`) and `G-32` (A6 N=29) has no toolchain at all. **The
  shipped column is emptier in exactly the places that decide whether a finding is about DAFoam or
  about a local patch.**
- **`NOT HELD` is 15 rows and it is not one failure mode.** It holds measured `GATE FAIL`s (`G-01`
  A1 shipped, `G-22` A5 shipped, `G-28`/`G-29` A6 N=16 on **both** images, `G-11`/`G-13` A3 rung 3
  on both, `G-37` B3's bit-identity miss, `O-10` D2's AB2); measured `BLOCKED`s of **four different
  kinds** (`G-17` A3-399k by memory; `G-25` A6-full by memory **and independently** by conditioning;
  `G-34` B3's `-9` at iteration 0; `G-38` the runtime-option axis closed from both ends;
  `O-11` a capability absent from the image); and two Stage-G driver defects (`O-13`, `O-14`).
  **Conflating them produces a false statement, and the A3 record says so explicitly.**
- **The whole G column is `NEVER RUN` and 56 of 58 P cells are `NEVER RUN`.** Read honestly, this
  family's coverage is **deep on V and empty on G and P**. That is the single most important
  sentence the matrix's owner can take from this contribution.

---

## 5. Where this contribution's dispatching brief disagreed with the records — the record wins

Listed so a reader of the brief and a reader of this file do not diverge. **In every case the
figure in the table above is the record's.**

1. **A4's "first optimisation".** The brief gave *"CD −7.4775 %, 6 majors, `EXIT: Optimal Solution
   Found.`"* as one row. The records carry **two** rows and those figures belong to different ones:
   the **first** optimisation is the **PATCHED** run — **9 majors**, NLP error `6.2814e-07`,
   **−7.47770 %** (`LADDER_A_STATUS.md` row 15; `A4/first_optimisation_np1/RESULTS.md` §2) — while
   **6 majors**, NLP error `6.9114020645938298e-08` and **−7.47753 %** are the **SHIPPED**
   optimisation run a day later (row 31; `A4/shipped_optimisation_np1/RESULTS.md`). They are rows
   **O-03** and **O-04** and are not merged.
2. **A6 N=16's aggregate.** The brief said *"8-of-9"* without a number; the record's aggregate at
   the fixed reference is **1.0432 %** on the 8 graded components (row 37), and the 3-component
   predecessor read **1.0099 %** (row 36). Both are cited; the 8-of-9 row is **G-30**.
3. **D1-C′'s sha.** The brief gave *"graded `5bec45b7`"*. `5bec45b7` is the **grading** commit; the
   commit that **last changed the record** — which is what the sha column carries — is
   **`cffd90e7`** (D1 CLOSED + Addendum 2). Both are printed in **O-06**.
4. **A3 rung 3 patched attempt 2's sha.** The brief gave *"`8871acf3`"*, which is the **grading**
   commit; the last-changing commit is **`bec36c9d`** (Addendum 1, v1.0 → v1.1, zero compute: five
   §2.1 `patched.log` citations struck and corrected). Both are printed in **G-13**.
5. **D3's `EXIT` string.** The brief attributed *"`EXIT: Optimal Solution Found.`"* to A4's first
   optimisation, which is correct, but **no D3 attempt ever ran an optimiser** — both attempts died
   in Stage G before any flow solve, so O-13 and O-14 carry no termination string at all and say so.
6. **A2's optimisation claim.** The brief's *"the true statement is the weaker one, no optimiser run
   had ever converged at that point"* is consistent with the record but is **not** the record's
   sentence. What `A2/grading_confirmation/RESULTS.md` §4 actually states, and what O-01 quotes, is
   that IPOPT printed **no `EXIT` line and no convergence statement anywhere in `opt_IPOPT.txt`**
   (grep: zero occurrences of `EXIT`) and that the run *"is not a converged optimum and must never
   be quoted as one."* The chronology claim is supplied by the ladder, not by A2's own file.
7. **A vocabulary defect, and it is OURS.** D2's record carries the status phrase
   **`NOT DELIVERED BY CONSTRUCTION`** for the trust-region half (row **O-11**), and that string is
   **not a member of the six-token verdict vocabulary** (`CLAUDE.md` rule 1; `DAFOAM_CHARTER.md`
   §8). **This is a DAFoam record's own defect, on this family's side of the line — not the
   verification team's and not the matrix's.** It sits at
   `cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md:52`, and again at `:646`. **This audit did
   NOT repair that record**: it is frozen, and a departure goes in as a **dated amendment appended
   at its foot** with a version bump and the assertion `lines whose number changed above this
   section: 0` (`CLAUDE.md` rule 6) — which is a separate item, not this one.
   In the row itself the phrase is **quoted, not translated**, and the verdict column now carries
   **`BLOCKED`**, because the column must carry a token and `BLOCKED` is what the measured facts
   support: a pre-freeze probe of **0.0333 core-min** measured that no trust-region optimizer is
   importable on the graded image (`ParOpt` ships as a package directory with no compiled
   extension; `SNOPT` and `NLPQLP` absent). **The row was also RETIERED, `NEVER RUN` → `NOT HELD`**
   — see item 9.

8. **A second vocabulary defect, also ours.** A3 rung 1's record grades its aggregate-band reading
   **`FAIL pending investigation`** (`cases/dafoam/ladder-a/A3/rung1_patched_idwarp_np4/RESULTS.md:75`,
   and again at `:94`), carried into row **G-08**. `FAIL` bare is not a token — `GATE FAIL` is — and
   *"pending investigation"* is hedging prose, which rule 1 forbids. Same treatment as item 7:
   **quoted, not translated**, flagged here, **the frozen record NOT edited by this audit**, and the
   repair left as a dated amendment for whoever owns that file. The row's own `PASS` under the
   per-component rule is a real token and is unchanged, and **the choice between the two rules
   reinterprets a gate threshold and is Sanaa's** — this audit does not choose.

9. **One row was RETIERED by this audit, and it is the only tier this audit moved.** **O-11**
   (D2's trust-region half) was tiered `NEVER RUN` in the first draft. **The document's own §0.2 map
   does not support that**: §0.2 reserves `NEVER RUN` for *"no measurement of this cell exists and
   no arm was launched — zero compute"*, or a `BLOCKED` whose blocker is **a standing decision**.
   Neither holds. Compute **was** spent (0.0333 core-min) and the blocker was **measured on the
   image itself**, which §0.2's `BLOCKED` split places in **`NOT HELD`**. The row now reads
   `NOT HELD` and says in its own cell that this audit moved it and why. **No other tier in this
   document was changed by the audit** — in particular `G-08`, `G-30`, `G-32` and `G-39`, each of
   which declines to read a gate that is Sanaa's, are left exactly as the first draft had them.

10. **The brief's reading of D1-C′ is narrower than the record's, and the record wins in the
    direction that ADDS a caveat.** The dispatching brief described the design-point dependence of
    the stock IDWarp `warpDeriv` defect as *"registered as HYPOTHESIS ONLY with the mechanism
    UNTESTED"*. The record splits those two: the **dependence itself is a conjunction of two
    measurements, not a hypothesis** — 640 % and sign-flipped at the undeformed baseline, ≤ 2.8e-06
    relative at arm O's converged design point — while **the MECHANISM is the untested part**,
    stated by the record as *"a hypothesis this run did not test"* and *"speculation until a
    registered arm measures the defect against rotation magnitude"*
    (`cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md:274-286`). **Row O-06 now carries
    that qualifier as a mandatory clause**, so the row cannot be lifted without it, and names the
    discriminating arm — `D` candidate **`D901`**, **not costed, not registered, not launched**.

11. **`P5` is a prediction, not a gate, and the row now says so.** The brief and the first draft
    both carried the record's own sentence *"the registered `P5 = GATE FAIL` is a MISS"*, which sits
    uneasily beside D1-C′'s verdict of ten gates PASS with no falsifier fired. Checked against the
    record: `P5` is a **registered point prediction** that the SHIPPED row would grade `GATE FAIL`;
    it graded `PASS`, so **P5 MISSED as a prediction** and no gate failed
    (`curriculum_D1_Cprime/RESULTS.md:30`, `:245`). **O-06 now states which of the two it was**, so
    the two sentences are not in tension on the page.

---

## 6. What this contribution does not do

- It **does not create, edit, reserve or assert anything about `docs/COVERAGE_MATRIX.md`.**
- It **does not edit any frozen record.** No file in `cases/dafoam/ladder-a/` or
  `cases/dafoam/ladder-b/` was modified to produce it.
- It **does not read the D464 gate** on A6 N=29 (row G-32) or the A3 rung-1 §4 rule choice
  (row G-08). Both are Sanaa's, and a tier is not a ruling.
- It **files nothing.** No arm was launched, no container started, no probe run: **0 core-minutes**,
  by the drafting lane and by the auditing lane alike.
- It **does not repair the two frozen records whose status phrases break the verdict vocabulary**
  (§5 items 7 and 8). Both are named with file and line; both repairs are dated amendments under
  `CLAUDE.md` rule 6 and belong to whoever owns those files.
- **It does not cover the whole DAFoam family, and the gap is named rather than left to be
  discovered.** These 58 rows are **adjoint-gradient and adjoint-optimization rows only**. The
  **S1 CBFS field-inversion outcome itself** — `G1 PASS`, `G2 FAIL` on the re-inversion, and the
  finding that G2 as defined scores the adjoint's sensitivity map rather than the closure's error
  location (`ladder-b/S1_CBFS_REINVERSION_RESULT.md`, `S1_SENSITIVITY_VS_ERROR.md` §3) — **is not a
  row here.** Its FD gates are (`G-40`…`G-43`); its inversion verdict is not. Whether the matrix
  wants inversion-outcome rows is the verification supervisor's call.
- **It excludes the F6 series deliberately and completely.** `f6a_nasa_hump/`,
  `f6a_epistemic_band/`, `f6b_periodic_hills/`, `f6c_duct_dns/`, `f6d_random_matrix_uq/` and
  `rans_model_comparison/` sit under `cases/dafoam/` for historical reasons and are **88 % of that
  tree by size**, but every one is a plain OpenFOAM `simpleFoam` solve with **no DAFoam adjoint
  anywhere**; they belong to family **F6** and their records live at `verification/campaign/`
  (`docs/dafoam/README.md` §1). **They are not DAFoam work and appear in no row of this document** —
  verified by this audit: **zero occurrences of the string `F6` in any row of §1 or §2**, and none
  anywhere in the first draft at all; the only three occurrences in this file are in this bullet,
  which exists to say they are excluded.

*Nothing here has been filed, sent, uploaded, registered, posted or commented anywhere.*
