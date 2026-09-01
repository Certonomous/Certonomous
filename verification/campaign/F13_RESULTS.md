# F1 (ONERA M6) — RESULTS

**Case id: `F1`.** The filename carries `F13` because it is a **frozen path token** registered in
§9 of the pre-registration and cited by `D527`; the correction is AMENDMENT 1 at the foot of
`verification/campaign/F13_ONERA_M6_PREREGISTRATION.md` (commit `3b88ab09`). **`F13` was never
allocated and remains unallocated.**

Registration frozen `2eabe5971b1c45624c189c669b69b5f17788a56e`
· AMENDMENT 1 (id) `3b88ab09` · AMENDMENT 2 (tip-cap fill) `73c264c3`.

## Rung ledger

| rung | what | verdict | core-min | record |
|---|---|---|---|---|
| **R0** | build L1/L2/L3, `checkMesh` ×3, §5 admission | **`GATE FAIL`** | **2.18** actual / 19.3 est / 90 cap | `verification/runs/F13_ONERA_M6_runs/R0_TERMINAL.md` |
| **R1** | Gate V (V1/V2/V3 + V3 negative control) | **`PENDING`** — not launched | 0 | — |
| **R2** | L1 primal, partitions A and B | **`PENDING`** — not launched | 0 | — |
| **R3** | L2 primal, partitions A and B | **`PENDING`** — not launched | 0 | — |
| **R4** | L3 primal, partitions A and B | **`PENDING`** — not launched | 0 | — |
| **Gate D** | §6 determinism, 60 `decomposePar` | **`PENDING`** — deliberately withheld | 0 | `R0_TERMINAL.md` |

**Gates V, G and P: `PENDING`. No value has been computed for any of them.**
`P` additionally cannot be computed at all from the held artifact — §2 and `D527`.

## The blocker, in one line each

1. **Max non-orthogonality 84.64 / 86.02 / 86.78° against a ≤ 70° gate**, and it **worsens with
   refinement** (severe faces 36 → 216 → 1 440). All of it is on AMENDMENT 2's tip-fill collapsed
   lines: the measured control with the fill omitted gives **51.26°, zero faces over 70°**.
   **A collapsed line is a geometric singularity — no level of this ladder can clear this gate.**
2. **`checkMesh` does not print `Mesh OK` at any level**, on **high aspect ratio** at the wake cut
   (5 934 / 6 469 / 6 749). **Identical in the control**, so it is §5's own frozen recipe — a 16m
   uniform wake against a 161 µm first normal cell — not the amendment. Clearing it needs a wake of
   **≤ 3.2 c_root**, which would compromise the C_D that G1 grades. **Not done.**

## What PASSED, and it is not nothing

Cell counts exact (108 216 / 865 728 / 6 925 824); **`r = 2.000000` on both pairs**; **node nesting
L1 ⊂ L2 ⊂ L3 = 0.000e+00 m exactly**, read from the built `polyMesh` under a live planted control
(1e-9 m perturbation seen at 1.000000083e-09 m); max skewness 1.443 against ≤ 4; L1 y⁺ estimate 39.7
against ≤ 300; L3 S2 cell 0.00625 c against ≤ 0.00650 c. **The ladder is exactly the geometrically
similar family §5 registered. What it is not is admissible.**

## Standing

**This case is `BLOCKED` on §5 admission.** Clearing it requires a decision that is **not this
lane's and not this rung's**: either a tip-fill topology without a collapsed line (which changes
the amended cell counts, and therefore `r`), or a ruling on the two §5 admission clauses — both
above a lane. **No solver runs until then.** Firing an inadmissible ladder is the F12 failure and
it is not repeated here.

---

## ADDENDUM 1 — 2026-09-01: THE CAUSE IS GEOMETRIC. THE VERDICT DOES NOT MOVE.

**Dated addendum under CLAUDE.md rule 2, which permits post-compute changes ONLY as dated
addenda that cannot alter a gate, threshold, cap or label.** Nothing above is edited,
reordered, inserted or deleted.

**THE VERDICTS ARE UNCHANGED AND ARE NOT BEING REVISITED.** R0 stands **`GATE FAIL`**;
the case stands **`BLOCKED`** on §5 admission; R1–R4 and Gate D stand **`PENDING`**. **Only
the recorded CAUSE changes**, and a cause is none of the four things rule 2 protects.

### Why an addendum was needed

The "Standing" section above names the route out as *"a tip-fill topology without a collapsed
line"*. **That reads as though the obstruction is a generator choice and a better cap would
clear it. On the measured evidence it is not, and a graded record whose verdict is right for
a reason now known to be wrong will mislead the next reader.**

### What the register already held

**`N-C6`** in `docs/NUMERICS_KNOWLEDGE.md`, landed **2026-08-25** by this team from the ONERA
M6 topology study: *"A structured butterfly tip cap on a SHARP trailing edge has a
non-orthogonality floor that REFINEMENT MAKES WORSE."* Its measured sweep, far-field blocks
already repaired so the cap is the only mechanism above 70°:

| variant | cells | max non-orthogonality | severe (> 70°) | severe fraction |
|---|---|---|---|---|
| `t1_SHELL` | 111,872 | 81.5834° | 516 | 0.158 % |
| `t8_SHELL_NR64` | 146,432 | 82.0645° | 7,200 | 1.694 % |

**A non-collapsing cap was already measured at 81.58–82.06°, rising to an asymptote, with the
severe-face fraction rising 10.7× while cells rose only 1.31×.**

### The independent check, computed 2026-09-01 at zero compute

By the arc-length route `N-C6` prescribes — the trailing-edge strip joins a surface arc of
`(1 − U2)·c` to a core edge of `(1 − CORE_S)·t2(U2)·c`:

| `U2` | 0.70 | 0.80 | **0.90** (registered) | 0.95 |
|---|---|---|---|---|
| ratio `R` | 18.28:1 | 16.90:1 | **15.49:1** | 14.37:1 |

**R = 15.49:1 at the registered break reproduces `N-C6`'s ~16:1 by a separate route** — that
figure is computed from the registered section geometry, `N-C6`'s from built meshes.

**And moving the break does not escape it.** `R` is nearly flat because the section
half-thickness `t2 → 0` at a sharp trailing edge, so numerator and denominator shrink
together. **That is a property of the SECTION, not of the block structure**, so it does not
depend on which cap topology is chosen.

### The corrected cause

**The collapsed lines at `cases/F13_onera_m6/make_blockmesh_m6.py:170-171` are real and are
the generator's contribution — but they are not the whole cause.** The section's half-thickness
going to zero at a sharp trailing edge sets an arc-length ratio that a core-based structured
cap cannot escape in the design region. **The earlier reading — that the geometry was never
the problem — is too kind to the geometry.**

### The honest limit, carried so this addendum is not read as stronger than it is

**The ratio is escapable in principle.** `R < 10` requires `CORE_S < 0.2256` at `U2 = 0.90`.
So the obstruction is established across the **registered and natural design region**
(minimum **10.26:1** over `U2` 0.70–0.95, `CORE_S` 0.30–0.70) and **not** across the entire
admissible space. **A cap with a sub-0.23 core scale is UNTESTED and is named here as an open
escape, not a closed question.** The evidence against it is indirect: `N-C6`'s own core
variants measured **87.0192°** and **84.8750°** against the **81.5834°** baseline — worse, not
better — but they varied core *shape* rather than core *scale*.

**Also standing, from `N-C6`:** thickening the section to relieve the ratio is
**INADMISSIBLE** (the `TSCALE` ruling) — a thickened aerofoil is a different aerofoil. This is
a reason to change the meshing method, never the geometry.

### Consequence for the successor filing

`F13_TIP_TOPOLOGY_PROBE_PREREGISTRATION.md` is **withdrawn before first compute** by its
AMENDMENT 1 (`579eaa1f`): its prediction 1 and its candidate ordering are struck as refuted
by a measurement predating the filing, no candidate was built, and **0.000 core-min was
spent** against a 4.0 estimate.

---

## ADDENDUM 2 — 2026-09-01: THE CAUSE RECORDED IN ADDENDUM 1 IS WRONG. THE VERDICTS STILL DO NOT MOVE.

**Dated addendum under CLAUDE.md rule 2, which permits post-compute changes ONLY as dated
addenda that cannot alter a gate, threshold, cap or label.** Appended at the foot under rule 6.
**Nothing above is edited, reordered, inserted or deleted.**

**Authorised by the cfd supervisor, 2026-09-01, who verified the finding personally from the
page before ruling.** F13 is cfd's ladder, so the ruling is cfd's to make.

**THE VERDICTS ARE UNCHANGED AND ARE NOT BEING REVISITED.** **R0 stands `GATE FAIL`. The case
stands `BLOCKED` on §5 admission. R1–R4 and Gate D stand `PENDING`.** No gate, threshold, band,
cap or label in this file or in `F13_ONERA_M6_PREREGISTRATION.md` is altered by this addendum.
**Only the recorded CAUSE changes, and a cause is none of the four things rule 2 protects.**

### What ADDENDUM 1 asserted, and what is now STRUCK

ADDENDUM 1 recorded the cause as geometric, resting on `N-C6`, whose mechanism is stated there
as *"the ratio is set by the section half-thickness `t2`, which goes to ZERO at a sharp trailing
edge — at the M6's registered break it is ~16:1"*.

> **STRUCK: the clause that the M6's own trailing edge is sharp, and that its section
> half-thickness goes to zero there.**

**It does not.** The defining document has now been retrieved, opened and title-page verified,
and it says otherwise.

### The measurement that strikes it, cited by both page numbers

**AGARD AR-138, `TABLE B1-1`, "M6 WING STREAMWISE SECTION COORDINATES (DESIGN VALUES)",
printed page `B1-7` = PDF page `333`** of
`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`
(sha256 `a96a73304c8328bd97c828cead2df9326675fd2340230d7e81fcf9f8191e7ffb`, 17,588,425 B).
**Both page numbers are given because the retrieved scan has 612 pages where the report's own
abstract card states 642, and that discrepancy is unexplained.**

**The table's final row reads `x/l = 1.0000000`, `z/l = 0.0007052`.** AR-138 clause 2.1.10
(printed `B1-1` = PDF page `327`) states the section is **symmetrical**, so the design trailing
edge carries

> **2 × 0.0007052 = 0.0014104 chord = 0.14104 % chord. THE ONERA M6 TRAILING EDGE IS BLUNT.**

**Read off the page image, not off the sidecar.** The OCR mangles this table — the `.txt`
sidecar renders these ordinates as strings such as `0.ZY37` and `n.11401` — so a grep of the
sidecar returns nothing and **a lane that had only grepped would have concluded the value was
absent.** The row was located by printed-page arithmetic (printed `B1-35` sits on PDF page
`361`, so printed `B1-1` is PDF page `327`) and read from the rendered page.

### The second struck clause: the tip

`F13_ONERA_M6_PREREGISTRATION.md` §5 records *"the M6 tip is a flat cut, so the cap is geometry,
not a simplification."*

> **STRUCK.** AR-138 clause **2.1.13** (printed `B1-2` = PDF page `328`) reads, verbatim:
> **"truncation parallel to wing root and addition of a half body of revolution."**
> **The M6 tip is ROUND.**

**Confirmed quantitatively, and the prediction was made before the confirming figure was read.**
A half body of revolution about the tip chord adds half the tip-section maximum thickness in
span: from the measured root `t/c = 0.097804` and `c_t = 0.453253 m`, **22.155 mm**. NASA TMR
publishes, for its CAD of this geometry, *"Semispan (last section): 1196.300000084 mm"* and
*"Rounded Tip Semispan: 1218.535 mm"* — a difference of **22.235 mm**. **Ratio 0.9964.**

### THE CORRECTED CAUSE

> **The ~16:1 strip-to-core arc-length ratio at the break is a property of THE GEOMETRY THIS
> LAB SHARPENED, not of the ONERA M6.** The M6's own trailing edge is 0.14104 % chord thick and
> its tip is a half body of revolution. `N-C6`'s mechanism requires a half-thickness going to
> zero; **the M6 does not supply one.**

**`N-C6` IS NOT REFUTED AND IS NOT WEAKENED.** It is correct about sharp trailing edges. What
was wrong was its **application** to this geometry, and the narrowing is recorded as a dated
addendum on `N-C6` itself in `docs/NUMERICS_KNOWLEDGE.md`.

### Why the verdict is right anyway, and why that matters

**R0 measured the mesh this ladder actually built**, and that mesh has a sharp trailing edge and
a collapsed tip-fill line. **84.64 / 86.02 / 86.78° against a ≤ 70° gate is a true measurement
of a true object, and `GATE FAIL` is the correct verdict for it.** What changes is that the
obstruction is **not** a property of the ONERA M6 and therefore **not** a reason to believe the
M6 is unmeshable. **A right verdict resting on a wrong cause is the most expensive kind of
record, because it closes a door that is open.**

### What this addendum does NOT do

1. **It does not reopen R0, R1–R4 or Gate D.** No solver has run under F13 and none runs now.
2. **It does not register a new geometry, ladder or build.** The AGARD-faithful blunt-TE route
   is visible and is **deliberately left shut** by the supervisor's ruling of 2026-09-01 until
   the `M6I` ladder is graded.
3. **It does not amend §5's cell counts, `r`, bands, caps or labels**, which rule 2 protects.

### F13's REGISTERED UNBLOCK IS SATISFIED — STATED, NOT ACTED ON

§2 of the pre-registration registered, before any compute, that if AGARD AR-138 reached this box
and title-page verified, the seven stations would be read from it and Gate P would become
claimable **without changing any gate, band, threshold, cap or label**.

**The document has reached this box. It title-page verifies.** Printed `B1-4` = PDF page `330`,
§5.1.1, verbatim: **"271 pressure orifices divided in 7 sections (y/b = 0.20/0.44/0.65/0.80/0.90/0.96
and 0.99)"**. The reference accuracy §2 recorded as UNAVAILABLE is also now held: printed
`B1-4` §6.1, **`ΔCp = ±0.02` at `Mo = 0.84`**; and printed `B1-5` = PDF page `331` §6.2,
**"Wall interference corrections: no corrections"**, at a semispan-to-tunnel-width ratio of
**0.7** (§4.2).

> **Gate P remains `PENDING`. It has not failed; it has not been attempted.** The condition is
> recorded as satisfied and **is not acted on here.**

### Assertions, MEASURED after the write

| assertion | value |
|---|---|
| lines of this file edited, reordered, inserted or deleted above this section | **none** |
| **lines whose number changed above this section** | **0** |
| md5 of this file's first 130 lines BEFORE the append | `e51194a3e2e27d62043842b2d5ce7dc2` |
| md5 of this file's first 130 lines AFTER the append | `e51194a3e2e27d62043842b2d5ce7dc2` |
| the two digests | **EQUAL — assertion MEASURED, verified after the write** |
