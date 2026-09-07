# RUNG 2 grid-family acquisition pre-registration — DPW5 refinement triple L1.T / L2.C / L3.M (hex)

**Team: cfd. Case id `RUNG2-GRID-ACQ`. v1.0, drafted 2026-09-07 by a `lab-lane` for the cfd supervisor,
under Sanaa's directive 2026-09-06T2115Z ("the designated family needs to upload the different levels
of committee grids as well to do the [G]CI") and the cfd supervisor's ruling at
`verification/campaign/RUNG2_CRM_M0_PREREGISTRATION.md` §15.**

> # ⚠ DRAFT — NOT AUTHORISED. CHECK 4 NOT TAKEN.
>
> **NO FETCH, NO CONVERSION AND NO COMPUTE HAS BEEN RUN UNDER THIS FILE. NOTHING IS ENQUEUED.**
>
> This lane drafted and froze the text, verified upstream availability by read-only HEAD requests
> (inbound acquisition, allowed; nothing was posted, registered, emailed or filed outward — rule 7),
> and spent **0.000 solver core-minutes** and **0 bytes of bulk download**. It did **NOT** authorise
> the acquisition and did **NOT** launch the bulk fetch.
>
> **The rule-2 freeze — pre-registration committed before compute — and the go/no-go on this fetch
> are the cfd supervisor's non-delegable check 4** (`SUPERVISION_CHARTER.md` §3). This lane does not
> take it. The supervisor must decide, with §5's honest caveat in front of him, whether the fetch and
> its mesh-gate screen are worth spending, because the strong prior is that the fetched levels FAIL the
> same hard mesh gates L1.T fails — in which case the fetch buys a refinement triple that still cannot
> carry a credential validated force.

---

## 1. PURPOSE, AND THE ONE GATE THIS FILE REGISTERS

**Purpose.** Acquire the two missing hex levels of the DPW5 committee grid family — **L2.C** and
**L3.M** — so that, together with **L1.T** already on the box, a **three-level hex refinement triple**
exists on this box for the first time. That triple is the physical prerequisite for a Roache/GCI
grid-convergence study on a CRM drag figure (rule 5), which is the binding gap the RUNG 2 (a)
disposition rests on: `RUNG2_CRM_M0_PREREGISTRATION.md` §15 rules that **ground (iii) — no refinement
triple exists on this box — is what binds Rung 2 (a)**, and that acquiring the further levels "is THE
ONLY ROUTE to a refinement triple for this ladder."

**What this file is NOT.** It is not a Rung 2 (a) drag pre-registration and it registers no force,
`C_D`, `C_L`, moment, GCI or comparison to any workshop scatter band. It acquires and screens grids.
Whether a validated force can EVER be graded on these grids is governed by the mesh-gate ruling in
`RUNG2_CRM_M0_PREREGISTRATION.md` §15 (ground (i): R12's exemption does not reach a credential force;
the hard gates do not widen), and this fetch does not touch that.

**The single registered outcome:** a measured answer to the ruling's mandatory cheap question —
**do L2.C and L3.M clear this lab's hard mesh gates?** — plus, if they do, a usable refinement triple.

---

## 2. UPSTREAM CENSUS — MEASURED 2026-09-07 BY READ-ONLY HEAD, NOT INHERITED FROM 2026-08-01

`RUNG2_CRM_M0_PREREGISTRATION.md` §15.6 point 4 flagged that the levels' **fetchability now** was not
established — the 2026-08-01 survey (`cases/committee-grids/logs/DPW5_size_survey.log`) proved only
that they existed then. This section establishes it now.

**Source of truth:** `https://dpw.larc.nasa.gov/DPW5/unstructured_grids.REV01/` — the workshop's
public NASA Langley mirror, the same host and directory L1.T was pulled from 2026-08-01 (anonymous
HTTPS, no account). HEAD requests issued 2026-09-07T03:3xZ:

| file | HTTP | Content-Length (bytes) | = MiB | Last-Modified | on this box? |
|---|---|---:|---:|---|---|
| `L1.T.rev01.p3d.hex.r8.ugrid` | **200 OK** | **37,131,204** | 35.41 | Fri 20 Jan 2012 20:51:12 GMT | **yes** — and the on-disk copy is **37,131,204 bytes, byte-for-byte the same length** |
| `L2.C.rev01.p3d.hex.r8.ugrid` | **200 OK** | **123,796,868** | 118.06 | Fri 20 Jan 2012 20:51:26 GMT | no — **to fetch** |
| `L3.M.rev01.p3d.hex.r8.ugrid` | **200 OK** | **291,645,252** | 278.14 | Fri 20 Jan 2012 20:52:00 GMT | no — **to fetch** |

**Three corroborations of provenance, not one:**
1. **All three return HTTP 200 and a real Content-Length** — the levels are served now, not merely in
   the 2012 upload or the 2026-08-01 survey.
2. **L1.T's upstream Content-Length equals the on-box file's byte count exactly (37,131,204).** The
   grid this lab already imported and Rung-0b-`PASS`ed IS, by length, the upstream file — the mirror
   has not been re-cut under us.
3. **All three carry Last-Modified within 48 seconds of each other on 2012-01-20** — one grid-family
   upload, consistent with a single committee release.

**A recorded L-144 warning about `Content-Type`, because it is exactly the trap.** The three files
returned **three different, wrong MIME types** — `text/troff` (L1.T), `text/plain` (L2.C),
`application/vnd.wolfram.mathematica.package` (L3.M). The server sniffs content and guesses; the type
is meaningless. **This is the concrete reason the admissibility check in §4 verifies the grid by its
own header contents, never by filename, hash or file type** (L-144).

---

## 3. THE CHEAP QUESTION, ANSWERED AS FAR AS DOCUMENTATION ALLOWS — AND IT DOES NOT ALLOW MUCH

`RUNG2_CRM_M0_PREREGISTRATION.md` §15 orders, verbatim: *"ESTABLISH WHETHER THE FURTHER LEVELS WOULD
THEMSELVES CLEAR THE MESH GATES … a cheap question to ask of published grid documentation and an
expensive one to answer by fetching."* This section asks it of documentation first.

**What was measured:**

- **No published per-level checkMesh quality figure exists on this box.** The Rung 0b record already
  states it (`verification/runs/RUNG0b_MESH_IMPORT_runs/.../RESULTS.json:191`, quoted at
  `RUNG2_CRM_M0_PREREGISTRATION.md` §15.6 point 1): *"no published quality figure located … no max
  non-orthogonality, skewness or aspect-ratio figure is published there."* Re-checked here: the grid
  store's `readme` and the committee-grid docs carry no non-orthogonality or skewness figure.
- **No such figure is published by DPW5 at all.** DPW publishes cell/node counts, `y+`, and aspect
  ratio — not the OpenFOAM `checkMesh` max-non-orthogonality / max-skewness metrics the lab's hard
  gates read. (The workshop reports, e.g., a max aspect ratio of 131×10³ on the 17M-point L4 level;
  aspect ratio is MESH_STANDARD §3.3 **advisory**, never a lone rejection, so it does not gate.)
  The hard-gate metrics (§3.1 max non-orthogonality 70°, §3.2 max skewness 4) are tool-specific and
  were never published for these grids.

**So the cheap-documentation route is EXHAUSTED and returns no number.** The only remaining way to
answer the cheap question by measurement is to fetch, convert and `checkMesh` — which is exactly the
"expensive to answer by fetching" path the ruling flagged. That collision is the honest core of this
draft, and §5 states it as a caveat the supervisor must weigh before spending anything.

**The STRONG PRIOR, stated as a prior and not as a measurement.** The hard gates read the **maximum**
non-orthogonality (L1.T: **89.7134°**, gate 70°, 28.2% past — `MESH_STANDARD.md:56`) and the
**maximum** skewness (L1.T: **14.0594**, gate 4, 3.5× past — `MESH_STANDARD.md:84`). A grid's maximum
angle/skew is set by a small number of geometrically singular cells — trailing-edge closure,
wing-body junction, wingtip cap, symmetry-plane collapse — whose worst-case angles are fixed by the
geometry and the grid topology, **not by cell size**. Refining within the same generator family
lowers *average* non-orthogonality and truncation error but does **not** generally relax the worst
cells. Two family signatures on this box point the same way: (a) `checkMesh` on this box printed
"Non-orthogonality check OK." at **89.71, 89.94 and 89.9985** degrees across this family
(`RUNG2_CRM_M0_PREREGISTRATION.md` §15.2 row 9), i.e. the family clusters at ~90° max; (b) aspect
ratio *grows* with refinement (L1.T 14,426.8 → L4 published 131,000), the wrong direction. **The prior
is therefore that L2.C and L3.M FAIL the same hard gates by similar margins.** It is a prior. It is
not registered as a result and does not pre-decide §4's screen.

---

## 4. THE ADMISSIBILITY CHECK EVERY FETCHED GRID MUST PASS

Two stages, in order. A fetched grid that fails stage A is discarded and never converted.

### 4.A Title-page verification (L-144) — by the grid's own header, never by filename/hash/type

For each fetched file, in one shell invocation, before any conversion:
1. **Completed-download integrity:** the received file's byte count equals the §2 upstream
   Content-Length exactly (L2.C 123,796,868; L3.M 291,645,252). A short read is a failed fetch, retried
   or abandoned — never converted.
2. **Header identity (the title page):** parse the ugrid r8 header (7 leading ints:
   `nnode ntri nquad ntet npyr nprism nhex`) with the lab's own `inspect_ugrid.py` and require it match
   the size-survey exactly — **L2.C:** `nodes=2,204,089`, `hex=2,156,544`, all of tet/prism = 0;
   **L3.M:** `nodes=5,196,193`, `hex=5,111,808`, all of tet/prism = 0. This is the L-144 title-page
   read: the grid is admitted on *what it contains*, not on its name, size or a hash that a sharpened
   lookalike could also carry.
3. **Family consistency:** node/cell ratio within the family band (L1.T 1.033, L2.C 1.022, L3.M
   1.0165) — a coarse guard against a mis-named level.

### 4.B Mesh-gate screen — the measured answer to §3's cheap question

Convert each admitted ugrid to OpenFOAM (`cases/committee-grids/ugrid_to_foam.py`, the Rung-0b-`PASS`ed
importer) and run `checkMesh`, reading **max non-orthogonality** and **max skewness** into a birth
certificate exactly as Rung 0b did for L1.T. Screen against:
- **MESH_STANDARD §3.1** — hard gate **70°** (`docs/standards/MESH_STANDARD.md:56`)
- **MESH_STANDARD §3.2** — hard gate **4** (`docs/standards/MESH_STANDARD.md:84`)

**This screen is a DIAGNOSTIC, not a credential gate**, and it decides only what the triple can carry:
- **If both levels clear both hard gates** — a usable refinement triple exists and (subject to the
  compressible-solver channel, `RUNG2_CRM_M0`) a credential-grade GCI on drag becomes reachable. This
  would be a surprise given L1.T fails, and it would be a genuine, reportable finding.
- **If either level fails either hard gate** (the strong prior) — the triple is real but **cannot
  carry a validated force / credential verdict** (`RUNG2_CRM_M0_PREREGISTRATION.md` §15 ground (i);
  R12 does not travel to a physics gate). It could still carry ranking-only or model-form-band work,
  registered as its own separate deliverable — not Rung 2 (a).

Either outcome is informative. Neither is a drag claim.

---

## 5. THE HONEST CAVEAT THE SUPERVISOR MUST WEIGH BEFORE AUTHORISING

Stated plainly because it changes whether this fetch is worth spending:

**The cheap-documentation question could not be answered (§3) — no per-level quality figure exists
anywhere reachable — and the strong physical prior is that L2.C and L3.M FAIL the same hard mesh
gates L1.T fails.** If that prior holds, this fetch and its screen buy a refinement triple that
**still cannot carry a credential validated force**, i.e. acquisition effort spent to arrive at the
same wall the mesh-gate ruling already named. That is precisely the risk `RUNG2_CRM_M0` §15 warned of.

**What the spend still buys even in the adverse case, so the decision is not falsely one-sided:**
1. It **converts a prior into a measurement** — the cheap question stops being "we believe" and becomes
   "we measured", at ≈ 8 core-min and $0.0068 derived. The ruling ordered the question asked; §3 shows
   documentation cannot answer it; §4.B is the only instrument that can.
2. A refinement triple, even on gate-failing grids, is the substrate for a **ranking-only /
   model-form-band** deliverable under R12 (its own registration), and for a grid-convergence
   *numerical-uncertainty* statement clearly labelled non-credential.

**What it does NOT buy, and must not be sold as:** a path to a Rung 2 (a) credential drag figure, if
the screen fails. The go/no-go is the supervisor's under check 4.

---

## 6. COST — registered before any fetch, with its basis named (rule 12)

**Basis, anchored on measured box artifacts, not guessed:**
- **Fetch:** L1.T pulled 2026-08-01 at 153 MB / 4 s = **38.25 MB/s measured** on this mirror
  (`COMMITTEE_GRID_NUMERICS.md:33`). The fetch is network-I/O-bound, single-stream, ≈ 1 core.
- **Convert + `checkMesh`:** Rung 0b converted+verified three L1.T grids (4,898,816 cells total) in
  **4.4333 core-min** (`RUNG0b_MESH_IMPORT_PREREGISTRATION.md`, record `33b77af5`) = **0.905
  core-min/Mcell** for the combined pipeline.

| line item | derivation | core-min |
|---|---|---:|
| Fetch L2.C + L3.M (415,442,120 B = 396.2 MiB) | 396.2 MiB / 38.25 MB/s ≈ 11 s wall + overhead, allow 60 s × 1 core / 60 | **1.0** |
| Convert + `checkMesh` L2.C (2,156,544 cells) | 2.157 Mcell × 0.905 | **1.95** |
| Convert + `checkMesh` L3.M (5,111,808 cells) | 5.112 Mcell × 0.905 | **4.63** |
| Title-page reads (§4.A), serial | — | **0.4** |
| **REGISTERED ESTIMATE** | 1.0 + 1.95 + 4.63 + 0.4 | **≈ 8.0 core-min** |
| **CAP** | ≈ 3.8× the estimate, set by this team, absorbs super-linear python conversion at 5M cells | **30.0 core-min** |

The convert estimate's honest weakness: `ugrid_to_foam.py` is serial python and may scale
super-linearly at 5M cells (memory, connectivity dict). The cap is set to absorb that; **an overrun
stops the run and does not get a new budget** (rule 12).

**Bandwidth:** **415,442,120 bytes (396.2 MiB) inbound, one-time.** No outbound.

**Disk:** raw ugrid 396.2 MiB (kept) + converted `polyMesh` for the two levels, estimated ≈ 2.5× raw
≈ 1.0 GiB transient. **Peak transient disk ≈ 1.4 GiB.** The box has room (L1.T's full store was
153 MB; §15's memory law predicts peak RSS 4,290 / 8,974 MiB for L2.C/L3.M solves, not relevant to a
`checkMesh`-only screen).

**Dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md`
§5, rule 12). At the on-box `c7a.4xlarge` rate **$0.0513/core-h**, `cost_basis:
on-box-owner-stated`:
- estimate 8.0 core-min = 0.1333 core-h → **$0.0068 DERIVED**
- cap 30.0 core-min = 0.5 core-h → **$0.0257 DERIVED**

**Under the $25 pre-authorised line and 0.015% of the $150 single-run escalation line.** This is an
on-box run: no rented node, no GPU, no unpriced backlog. **Estimate-versus-actual calibration is
mandatory at completion** (rule 12): a row in `docs/COST_CALIBRATION.md` and, if charged to the IBL
envelope, a row there, stating actual/predicted with waste named separately.

---

## 7. THE GATES — fixed vocabulary, thresholds pre-registered

| id | gate | threshold (pre-registered) | cap (core-min) | label if met | label if not |
|---|---|---|---:|---|---|
| **G-A0** | **Upstream availability.** ALREADY MEASURED — §2. | Both L2.C and L3.M return HTTP 200 with a Content-Length, from the L1.T host/directory | **0.0** (HEAD only, no bulk) | **PASS** — measured 2026-09-07, both 200 | **BLOCKED** — upstream gone; no fetch possible |
| **G-A1** | **Fetch integrity + title page** (§4.A, L-144). | Each fetched file's byte count == §2 Content-Length AND its ugrid header node/cell counts == the size-survey exactly | **1.4** | **PASS** — a verified DPW5 hex level, admitted on its header | **NOT A RESULT** for that level — a short read or a header mismatch is a failed/wrong grid, discarded, never converted |
| **G-A2** | **Mesh-gate screen** (§4.B). Diagnostic, not credential. | For each level, `checkMesh` max non-orthogonality and max skewness recorded in a birth certificate and compared to §3.1 (70°) / §3.2 (4) | **28.6** | **PASS** — the screen ran and both metrics are recorded per level (the *values*, pass-or-fail, are the finding; this gate passes on having MEASURED them) | **NOT A RESULT** — conversion or `checkMesh` did not complete for a level, so no quality metric was measured |
| **G-A3** | **Triple existence.** | After G-A1 PASS on both, three hex levels L1.T/L2.C/L3.M with monotone refinement (0.64M → 2.16M → 5.11M) are present and importable on the box | **0.0** (inside G-A1) | **PASS** — a refinement triple exists on this box for the first time | **NOT A RESULT** — the triple is incomplete |

**No gate here produces or implies a drag figure**, and **G-A2 passing on "metrics measured" is NOT
the same as the grids clearing the gates** — the pass/fail of §3.1/§3.2 is the *reported finding*, and
if the grids fail them the credential path stays `BLOCKED` under `RUNG2_CRM_M0` §15 ground (i).

**Total registered cap: 30.0 core-min.** An overrun stops the run (rule 12). A retry spends from the
same 30.0.

---

## 8. COMPLETION, REFUSAL, AND THE FROZEN GRADING PATH

- **Fetch completion** is the G-A1 byte-and-header check; a partial download is not a fetch.
- **Screen completion** for a level requires `checkMesh` to run to its normal end with the two metrics
  parsed into a birth certificate; a crash mid-`checkMesh` is `NOT A RESULT` for that level, not a
  quiet omission.
- **The grading path is fixed at this document's commit** and lives **beside the case**, not inside a
  run root (the same ruling as `RUNG2_CRM_M0` §8: a grader committed inside the run root forces the
  root to exist before launch, which rule 4's guard refuses). The screen/verify comparator is to be
  written as **`cases/committee-grids/grade_grid_acq.py`**, next to the committed `grade_rung0b.py`,
  hashed against its committed blob at grading time (`scripts/check_comparator_freeze.py`).
  **IT DOES NOT EXIST YET and is not authorised to be written until this file is frozen by the
  supervisor** — this is a precondition, stated and not yet satisfied, so this draft asserts no freeze
  it does not have (the exact failure `RUNG2_CRM_M0` §13 records; it is not repeated here).
- **Planted-zero control (rule 3):** the header reader and the `checkMesh` metric reader must each be
  shown able to see a non-conforming value (a planted wrong node count; a planted over-gate
  non-orthogonality) and refuse/flag it, before either level's read is believed. To be built into the
  comparator's `--selftest` exactly as `grade_r2_m0.py`'s C0–C7 were.

---

## 9. PRE-COMPUTE CONDITION — CHECKED, NOT ASSUMED (rule 2)

Read at the moment of this edit, 2026-09-07:
- No `verification/campaign/RUNG2_CRM_GRID_ACQUISITION*` file existed before this one.
- No `verification/runs/RUNG2_GRID_ACQUISITION*` run root exists — **ABSENT**.
- L2.C and L3.M are **not** on the box in any topology — plant-verified 2026-09-06 in
  `RUNG2_CRM_M0_PREREGISTRATION.md` §15.3 (READER-A and READER-B′ both 0 → 2 → 0), which is the reader
  for exactly this absence and remains valid.
- **Bulk download bytes:** 0. **Solver/convert core-minutes:** 0.000. Only read-only HEAD requests
  were issued (§2), which transfer no grid body.

Amendments to this draft before first compute are legal under rule 2 and must state the condition and
how it was checked; this section is that statement for v1.0.

---

## 10. SUBMISSIONS PARKED (rule 7)

Nothing here is sent, filed, uploaded, registered, posted or commented outside the box. The §2 HEAD
requests are **inbound** existence checks against a public mirror — they retrieve metadata, they post
nothing. The acquisition itself, when authorised, is an **inbound public-file download**; it contacts
no upstream party as an act, files nothing, and registers nothing outward. No queue row for this
acquisition exists and none was filed.

---

## 11. WHAT REMAINS FOR THE SUPERVISOR'S CHECK 4 BEFORE ANY FETCH SPEND

1. **Freeze this file** (rule 2) and verify it against its committed blob.
2. **Weigh §5's caveat** — decide, knowing the strong prior is that the levels fail the hard gates and
   the fetch would then buy a triple that cannot carry a credential force, whether ≈ 8 core-min /
   $0.0068 derived to convert that prior into a measurement (and to obtain a triple usable for
   ranking-only / model-form work) is worth spending. This is the go/no-go.
3. **Authorise (or not) the writing of `cases/committee-grids/grade_grid_acq.py`** and require its
   planted-zero `--selftest` to pass before any grid is believed.
4. **Confirm an idle box and no foreign live job** at launch time (the contention that cost a cfd lane
   85.75 core-min on 2026-09-04, `RUNG2_CRM_M0` §14.2, is a wait, not a stop).
5. **Only then** may the bulk fetch and screen run, inside the 30.0 core-min cap.

*Drafted by a cfd `lab-lane`, 2026-09-07. Upstream availability in §2 is this lane's own measurement
by read-only HEAD; the cost basis is anchored on the cited Rung-0b and 2026-08-01 records. This lane
authorised nothing and launched nothing.*
