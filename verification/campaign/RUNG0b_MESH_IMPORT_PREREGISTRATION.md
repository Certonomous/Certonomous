# RUNG 0b — MESH IMPORT, THE SUCCESSOR REGISTRATION

**Case id:** `RUNG0b_MESH_IMPORT`
**Team:** cfd
**Drafted:** 2026-09-03. **Frozen at the commit that lands this file. Nothing below may
be read as registered until that commit exists.**

---

## 1. WHY A SUCCESSOR AND NOT A REPAIR — THE SHORT VERSION, BECAUSE IT IS THE WHOLE POINT

The predecessor `RUNG0_MESH_IMPORT` (`verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md`,
frozen **`d127d83d4ebf4caaaf0c12c39a063c5f624a03a4`**) registered **five** gates and could
run **four**. `R0-G2b`'s writer, `cases/committee-grids/foam_to_ugrid.py`, was registered
in its §9 as *"to be written; it does not exist"*, and it did not exist. Its comparator
therefore returned **`PENDING`** on all four grids and on the rung.

**It now exists.** And the route to a Rung 0 verdict is **not** to repair the predecessor.

> **THE PREDECESSOR'S COMPARATOR IS NOT DEFECTIVE.** It implements its registration
> faithfully. Four per-gate `PASS` branches exist in it — `analyse_rung0.py:448`
> (`R0_G1`), `:462` (`R0_G2a`), `:492` (`R0_G3`), `:505` (`R0_G4`). The **rung** `PASS`
> is withheld **deliberately** at `:512-518`, which prints its own reason — *"Reporting
> PASS here would be reporting a conjunction one of whose conjuncts was never
> evaluated"* — and the file's header at `:16-17` declares that it cannot emit a rung
> `PASS` and **refuses to**, citing §4's label. The omission of `R0_G2b` from the `per`
> list at `:507-508` is **also not a defect**: `per` is scanned only for `GATE FAIL`,
> `R0_G2b` is `PENDING` rather than failing, and including a `PENDING` conjunct in a
> `GATE FAIL` test would be wrong.

**This team asserted otherwise and was corrected.** cfd petitioned verification for a
`VERIFICATION_CHARTER.md` §2d.1 repair, on the ground that the comparator "has no PASS
branch". Verification **REFUSED the petition ON THE INSTRUMENT, not on the merits**, at
**`f5b8deec` (charter v1.52)**: the comparator and the registration **agree**, so §2d.1
**has no object** — there is no departure to repair and there never was. It also
**REFUSED BY NAME** the alternative of striking `R0-G2b` from the predecessor:

> *"a limb becoming runnable is not evidence it was never meant."*

The correction is recorded at
`verification/runs/RUNG0_MESH_IMPORT_runs/CORRECTION_no_pass_branch_framing.json`.

**Consequences that bind this file:**

1. **The predecessor is NOT amended, and its `PENDING` stands as committed.** No gate,
   threshold, cap or label of `d127d83d` moves. Nothing is struck.
2. **`analyse_rung0.py` is not touched** — not the rung `PASS`, not the `:507-508`
   conjunction, and not the `:334-342` string that now says `DOES NOT EXIST` about a
   file that exists. That string sits inside a comparator verification has just called
   faithful, and this registration supersedes it.
3. **Rung 0 gets its verdict through the front door**: a new registration, a new frozen
   grading path, and the same five gates graded **exactly as §4 always wrote them**.

---

## 2. THE ONE CLAIM THIS FILE HOLDS THE LINE ON

`R0-G2b` was **measured** `PASS` on all four grids on 2026-09-03, with its §7 round-trip
plant firing on all four, by `foam_to_ugrid.py --roundtrip`. That reading is recorded at
`verification/runs/RUNG0_MESH_IMPORT_runs/R0G2B_DIAGNOSTIC_NOT_A_GRADED_RUN.json`.

> **THAT IS A MEASUREMENT, NOT A VERDICT.** It was taken by an instrument **outside any
> frozen grading path**, after the artifacts it read were made. **It becomes a verdict
> only when this registration's own frozen comparator emits it from its own frozen
> path.** `grade_rung0b.py` therefore **recomputes it from scratch and cites nothing**;
> no clause below inherits it; and no reader of this file may report `R0-G2b` as graded
> until `RUNG0b`'s `RESULTS.json` exists. Verification asked specifically that this line
> be held, and it is held in the registration, in the comparator's own header, and in
> the comparator's code.

---

## 3. THE POPULATION — UNCHANGED, AND DELIBERATELY SO

The four committee grids of the predecessor's §3, **identical, with no addition and no
removal**, so that the successor's verdict is about the same objects the predecessor
returned `PENDING` on:

| grid | source | cells | source layout |
|---|---|---|---|
| DPW5 L1.T hex | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/L1.T.rev01.p3d.hex.r8.ugrid` | 638,976 | `.r8` big-endian Fortran unformatted |
| DPW5 L1.T prism | `.../L1.T.rev01.p3d.prism.r8.ugrid` | 1,277,952 | `.r8` |
| DPW5 L1.T hybrid | `.../L1.T.rev01.p3d.hybrid.r8.ugrid` | 2,981,888 | `.r8` |
| HLPW6 `h6c1_rans_3a_1` | `/home/ubuntu/certonomous-runs/hlpw6-memory-probe/grid/h6c1_rans_3a_1.b8.ugrid` | 2,661,338 | `.b8` big-endian raw C stream |

**Total 7.560154 Mcell.** The population is fixed in the comparator's own `GRIDS` tuple
rather than discovered by glob: *a comparator that grades whatever it happens to find
can be made to pass by deleting the grid that fails.*

**Each grid round-trips to its OWN source layout**, so the run exercises **both** the
Fortran-unformatted and the raw-C-stream paths on real data rather than on one of them
twice.

**⚠ THE ELEMENT CENSUS IS REGISTERED HERE, BECAUSE THE POPULATION'S COMPOSITION IS
LOAD-BEARING AND THIS FAMILY HAS BEEN BITTEN BY IT THREE TIMES.** Measured
2026-09-03 by `foam_to_ugrid.py`'s own classification:

| grid | tet | pyramid | prism | hex |
|---|---|---|---|---|
| DPW5 hex | 0 | **0** | 0 | 638,976 |
| DPW5 prism | 0 | **0** | 1,277,952 | 0 |
| DPW5 hybrid | 2,555,904 | **0** | 425,984 | 0 |
| HLPW6 | 436,961 | **341,341** | 1,883,036 | 0 |

**HLPW6 IS THE ONLY GRID IN THIS POPULATION THAT CONTAINS A SINGLE PYRAMID.** A writer
validated on the three DPW5 grids alone is **vacuously** validated for pyramids, and
this is not hypothetical: it is exactly how `foam_to_ugrid.py`'s first pyramid-template
defect was caught (962,824 regenerated triangle rows refused, on HLPW6 alone). Any
future reduction of this population must state, in its own registration, which element
types it stops covering.

---

## 4. GATES, THRESHOLDS, CAPS AND LABELS — §4 OF THE PREDECESSOR, AS WRITTEN, ALL FIVE

**Carried over verbatim in substance from the predecessor's §4. NOTHING IS WIDENED,
NOTHING IS NARROWED, AND NOTHING IS STRUCK.** A grade is per grid; the rung's verdict is
the conjunction.

### R0-G1 — patch identity preserved

| check | threshold |
|---|---|
| number of patches in `constant/polyMesh/boundary` | **== the number of DISTINCT names in the source `.mapbc`** |
| patch names | **set-equal** to the distinct `.mapbc` names, exactly, case-sensitive |
| `defaultFaces` present | **forbidden** — automatic `GATE FAIL` for that grid |
| every boundary face assigned | sum of `nFaces` over patches **==** the source's boundary-face count |

### R0-G2a — round trip, comparison limb

An **independent reader** — not `ugrid_to_foam.py`, and not importing it — parses the
source UGRID and `.mapbc` and emits `(cells, {patch name → face count})`. Compared to the
imported `polyMesh`: **cell count** exact integer equality; **patch names** exact set
equality; **per-patch face counts** exact integer equality on every patch.

**No tolerance. These are integers; a tolerance on an integer identity is an invitation.**

### R0-G2b — round trip, writer limb — **RUNNABLE, AND GRADED**

`cases/committee-grids/foam_to_ugrid.py` writes the imported mesh back to UGRID +
`.mapbc`; the **same** independent reader of R0-G2a re-reads the written file. The three
quantities must be **exactly equal** to R0-G2a's source-side values.

**R0-G2b grades the ROUND TRIP, not the geometry.** It makes no claim that node
coordinates survive losslessly; that is not one of the three quantities and is not
claimed here.

**REGISTERED AS A KNOWN AND ACCEPTED LOSS, so it cannot later be reported as a
discovery:** `ugrid_to_foam.py` merges the source `.mapbc` groups **by name**, and the
per-tag multiplicity **is not in the `polyMesh` at all** — `boundary` carries one AFLR3
code per patch, not the tag list. The writer therefore emits **one `.mapbc` group per
patch**: 3 against DPW5's 18, 14 against HLPW6's 73. **THE GROUP COUNT DOES NOT
ROUND-TRIP, IT IS NOT ONE OF THE THREE GRADED QUANTITIES, AND NO PART OF THIS
REGISTRATION CLAIMS IT DOES.**

### R0-G3 — measured quality reported against the grid's own documentation

**REPORTED. NOT GATED. THIS GATE CANNOT FAIL ON A QUALITY VALUE.** It fails only on a
**missing** number (`MESH_STANDARD.md` §11.4: *"What makes a record INCOMPLETE is the
ABSENCE of the number, never its size."*). Recorded per grid into a
`birth_certificate.json` beside the `polyMesh`, every field non-null:
`cells`, `faces`, `max_non_orthogonality`, `severe_non_ortho_faces`, `max_skewness`,
`max_aspect_ratio`, `aspect_ratio_flagged`, `min_cell_volume`, `max_cell_volume`,
`cell_volume_ratio` (**stated as derived**), `geometric_directions`, `checkMesh_log`,
`points_sha256`, `generator`, `created_at`, `grid_provenance`.

**NEW IN THIS REGISTRATION, and additive only:** the certificate also carries
`roundtrip_export` and `roundtrip_export_sha256`, naming and hashing the file R0-G2b
actually wrote. **These are recorded, NOT gated, and are not in the fail-on-absence
list** — a new field that could fail a gate would be a widened gate.

**L-459 IS BINDING ON EVERY NUMBER ABOVE.** Every quality value is **PARSED off its
named maximum line**; `checkMesh`'s own verdict strings are captured into a field named
`verdict_line_IGNORED_NEVER_A_GATE` **solely to show they were discarded**. On this box
`Non-orthogonality check OK.` is printed at 89.7134, 89.9441, 89.9985 and 89.9835
degrees against a 70-degree gate. **No gate in this registration reads a verdict line.**

### R0-G4 — the age guard and the no-clobber guard (rule 4)

The driver **REFUSES** (exit 3) a target case directory that already exists, writing
nothing. Every artifact graded must be **strictly newer** than the run root's own
creation stamp, recorded at launch in
`verification/runs/RUNG0b_MESH_IMPORT_runs/RUN_ROOT_CREATED_EPOCH`. This rung runs no
solver, so there is no `0/T` to date the run against and the run root's own stamp is the
age guard's analogue, exactly as the predecessor and R1-M0 did.

### Verdict labels

- **`PASS`** — R0-G1, R0-G2a, R0-G2b hold on **all four** grids and R0-G3 is complete on
  all four. **The conjunction over all five gates. A `PASS` IS REACHABLE FROM THIS
  REGISTRATION, and only this way.**
- **`GATE FAIL`** — any integer identity above fails, or any R0-G3 field is absent.
- **`NOT A RESULT`** — a planted control does not fire, **including B9 on any grid**.
- **`BLOCKED`** — a source grid or its `.mapbc` is unreachable.
- **`PENDING`** — display/queue state only: not yet run.

**No Roache triple is claimed and no GCI is computed. Rule 5 does not bite on this rung
because nothing here is a grid-converged quantity.**

---

## 5. COST — RULE 12, PRICED FROM MEASURED RATES RATHER THAN FROM THE PREDECESSOR'S ALLOWANCE

**Unit: core-minutes** (wall s × ranks ÷ 60). Dollars **DERIVED** at the recorded
**c7a.4xlarge $0.0513/core-h** (owner-stated 2026-08-21/22) and labelled **derived, not
measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**`decomposition seed`: `none` (identity).** Every step is **serial, np = 1**; no
`decomposePar` is run, so core-min = wall-min on every figure in this file. Recorded
explicitly as the required field rather than left blank.

### 5.1 The estimate — EVERY LINE MEASURED ON THIS BOX ON 2026-09-03, NOT INHERITED

The predecessor priced three of its five line items **by analogy to the converter rate**
and those three came in between 0.33× and 0.49×. **This registration prices every line
from a measurement of the same work on the same four grids**, which is what
`docs/COST_CALIBRATION.md` exists to make possible.

| item | measured basis (2026-09-03) | core-min |
|---|---|---|
| phase-A planted controls | **0.55 wall s measured** (`grade_rung0b.py --controls-only`) | **0.009** |
| convert 4 grids, `ugrid_to_foam.py` | **81 wall s** = **0.1786 core-min/Mcell** over 7.560154 Mcell (registered 0.203 in the predecessor; 12 % under, inside its own ±22 % band) | **1.350** |
| `checkMesh` on 4 meshes | **30 wall s** = **0.0661 core-min/Mcell** — **NOT the converter rate**; the predecessor priced this at 1× and measured 0.33× | **0.500** |
| grading: phase-B controls + all five gates, **including the four round trips** | round trips **68.08 wall s measured**; predecessor's grading pass **29.18 wall s measured**; phase-B plants are file-copy scale | **1.680** |
| **subtotal** | | **3.539** |
| **+22 % contention band** — the same HLPW6 grid converted in **30.5 s and 35.1 s** with a foreign solver live | | **0.779** |
| **REGISTERED ESTIMATE** | | **4.4 core-min — $0.003762 DERIVED** |

**The band is an allowance, not a prediction of contention.** In the predecessor's
attempt 3 it was not drawn at all (1.361 core-min unused), and that is recorded as an
insurance line that did not pay out rather than as an efficiency.

### 5.2 Cap — **an overrun STOPS the run; it does not get a new budget**

| item | value | derived $ |
|---|---|---|
| **HARD CAP** | **13.2 core-min** (= 3× the registered estimate, set by this team per Sanaa's 2026-09-03 ~18:00Z clause 2, not by her) | **$0.011286 DERIVED** |

**Enforced structurally, inside the driver.** `run_rung0b.sh` carries a budget of
13.2 × 60 ÷ 1 = **792 wall seconds**, **recomputed before every step** from that one
total and passed to `timeout`. **A cap nothing enforces is not a cap.**

### 5.3 The fleet safety ceiling — Sanaa 2026-09-03 ~21:00Z

> *"a fleet-wide safety ceiling on any single run (e.g. 3× its registered cost cap, or
> the box's remaining budget, whichever is smaller) … at the ceiling the monitor stops
> the run gracefully regardless of residual trend."*

| term | value |
|---|---|
| 3 × the registered cap | 3 × 13.2 = **39.6 core-min** = **$0.033858 DERIVED** |
| the box's remaining budget | **EXPLICITLY UNAVAILABLE AND NON-BINDING** — see below |
| **min(·, ·) — THE OPERATIVE CEILING** | **39.6 core-min = 2,376 wall s at 1 rank** |

> **⚠ THE SECOND TERM IS NAMED AND LEFT UNRESOLVED ON PURPOSE. IT IS NEVER SILENTLY
> RESOLVED TO 0 OR TO INFINITY.** The box cannot read its own billing
> (`COMPUTE_BUDGET_CHARTER.md` §5), so "the box's remaining budget" **cannot be
> evaluated on this machine**. Resolving it to **0** would make the ceiling zero and
> refuse every run; resolving it to **infinity** would silently delete half of Sanaa's
> rule. It is therefore recorded as **UNAVAILABLE and NON-BINDING**, the ceiling is
> taken from the first term alone, and **this paragraph is the disclosure that makes
> that a decision on the record rather than an omission.** The nearest resolvable proxy
> — the IBL envelope's remaining balance at
> `docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`,
> **$999.99 of $1,000, ≈ 1.17 million core-min** — is **four orders of magnitude above
> 39.6 core-min** and so could not bind even if it were the right quantity. It is quoted
> for scale and is **not** adopted as the second term.

The ceiling is enforced as a **second, independent** `timeout` around the whole driver,
so that a defect in the per-step budget arithmetic cannot let the box be eaten. That is
the one hard structural stop Sanaa's rule preserves.

### 5.4 Funding, and it is funding rather than licence

Sanaa's **$1,000 standing envelope** covers the industrial benchmark ladder, Rungs 0–3,
which is this rung. **This item is nonetheless costed on its own registered terms and
the 13.2 core-min cap binds regardless of what the envelope would permit** — a blanket
is not a per-item read (rule 9). The spend lands as a row in
`docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`.

### 5.5 Calibration — rule 12's estimate-versus-actual

At completion the actual core-minutes are read from the logs, the ratio actual/predicted
is stated, the gap is attributed (contention / waste / misprediction, **waste named
separately, never absorbed**), and **a row is filed to `docs/COST_CALIBRATION.md`**
citing the predecessor rows. **A completion report without that comparison is
incomplete.** This registration's own estimate is the first in this family built entirely
from measured rates, so its ratio is a direct test of whether that method is better than
the predecessor's analogies.

---

## 6. COMPLETION — rule 4, strict, all-or-nothing

Per grid: `rc = 0` on the converter, on `checkMesh`, on the writer and on every reader
invocation; `constant/polyMesh/{points,faces,owner,neighbour,boundary}` all present and
non-empty; `log.checkMesh` present and containing **both** a `Mesh non-orthogonality
Max:` line **and** a `Min volume = … Max volume = …` line; the `birth_certificate.json`
of §4 present with **every** R0-G3 field **non-null**; the R0-G2b export present with its
`sha256` recorded; and every one of those artifacts **strictly NEWER** than
`RUN_ROOT_CREATED_EPOCH`.

**The comparator refuses (exit 2) rather than degrade on any failed clause. An absent
`log.checkMesh` reads `ABSENT`. IT NEVER READS CLEAN.**

---

## 7. PLANTED CONTROLS — rule 3, on every zero this rung can report

**A zero from a reader not shown able to see a non-zero is not evidence.** Two phases,
**both mandatory**; a failure in either is `NOT A RESULT` at exit 2.

**PHASE A — before any conversion, so a failure costs ZERO conversion core-minutes.**

| id | plant | must see |
|---|---|---|
| **B10** | `foam_to_ugrid.py --selftest`, run as a subprocess | exit 0 with **all 21** of the writer's own controls fired — one tet, pyramid, prism and hex built by hand, the hex in all four layout variants, a C9 plant and a per-type mutation control on each, and three refusal controls |
| **B0** | a hand-built one-hex `polyMesh` exported and re-read, in **both** the Fortran and raw-stream layouts | cells 1, hex 1, `{lid: 2, sides: 4}`, bnd 6 — **known a priori**, because every other control here is differential and a reader returning a constant WRONG answer moves correctly around all of them |
| **B1** | rename one `.mapbc` group in a **scratch copy** | the renamed patch appears in the emitted name set |
| **B2** | delete one boundary face from a scratch copy of the **real** grid | **exactly one** patch's count drops by **exactly 1**, cells unchanged. The plant **checks its own byte arithmetic** and refuses if the file did not shrink by one face |
| **B5** | fed a `checkMesh` log of the **`=` label form** *and* one of the **`:` form** | a **non-null** value from **each** — a reader matching only `=` sees the healthy logs and **silently misses exactly the pathological ones** |
| **B6** | a log with `Min volume` ≠ `Max volume` | a **non-trivial** derived ratio, never 1 |
| **B7** | an absent `checkMesh` log | reads `ABSENT` and yields **no number**. **ABSENT NEVER READS CLEAN** |

**PHASE B — after conversion, before any gate reads a number.**

| id | plant | must see |
|---|---|---|
| **B3** | `+1` on one `nFaces` in a scratch `boundary` | R0-G2a reports **unequal**, not equal |
| **B4** | rename a patch in a scratch `boundary` | a **name-set mismatch** |
| **B8** | a header note **contradicting** the mesh's own lists, on **every distinct label form on disk** | the reader **REFUSES**. A control planted into only one form would certify a reader that still could not see the other |
| **B9** | **THE CONTROL THE PREDECESSOR RECORDED AS UNBUILT.** Drop one face from the **written** file in a scratch copy | **R0-G2b reports unequal.** Enforced *inside* `foam_to_ugrid.roundtrip()`, which refuses to report an equality it has not first been shown able to see fail, and surfaced **per grid** |

**A `PASS` reported by a reader whose plant did not fire is `NOT A RESULT`, not a pass.
B9 failing on ANY grid makes the whole rung `NOT A RESULT`.**

---

## 8. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not make any grid admissible for anything.** The four grids breach
   `MESH_STANDARD.md` §3.1 by **17–20 degrees**. This rung measures that faithfully and
   changes it by nothing.
2. **It does not certify this lab's meshing capability.** Sanaa's ruling reserves that to
   in-house grids under 70°.
3. **It claims no physics, no force, no `y⁺`, and no comparison to any tunnel or
   workshop datum.**
4. **It does not claim node coordinates survive a round trip losslessly** — only cell
   count, patch names and per-patch face counts.
5. **It does not claim the `.mapbc` group count round-trips.** §4 says why not.
6. **It does not claim element ORIENTATION or handedness survives.** `foam_to_ugrid.py`
   proves every written element's face **node sets** reproduce the mesh's own faces, for
   all 7,560,154 cells, and refuses otherwise. It does **not** check winding sense, which
   the importer's outward-face rewrite makes unrecoverable without re-deriving it from
   geometry. **Not one of the three graded quantities; named here so its absence is a
   decision rather than an oversight.**
7. **It does not amend, reopen, re-grade or supersede the predecessor's `PENDING`.**
8. **It does not authorise the off-box branch** of the predecessor's §5.3 (DPW5 L4.F
   hybrid, 80.99 Mcells). That remains a named, costed, unauthorised gap.
9. **Nothing here is sent, filed, submitted or registered outside this box (rule 7).**

---

## 9. FROZEN PATHS — AND THE COMPARATOR IS OUTSIDE THE RUN ROOT THIS TIME

| what | path | state at freeze |
|---|---|---|
| this registration | `verification/campaign/RUNG0b_MESH_IMPORT_PREREGISTRATION.md` | this file |
| **comparator (GRADING PATH)** | **`cases/committee-grids/grade_rung0b.py`** | **EXISTS at the freeze commit** |
| **writer (GRADING PATH)** | **`cases/committee-grids/foam_to_ugrid.py`** | **EXISTS**, committed `d1c5aa5d` |
| **independent reader (GRADING PATH)** | **`cases/committee-grids/read_ugrid_identity.py`** | **EXISTS**, unmodified |
| driver | `cases/committee-grids/run_rung0b.sh` | EXISTS at the freeze commit |
| converter — **the artefact under test, NOT the grading path** | `cases/committee-grids/ugrid_to_foam.py` | EXISTS, unmodified |
| run root | `verification/runs/RUNG0b_MESH_IMPORT_runs/` | **ABSENT** |
| R0-G2b exports (large binary, **outside git**) | `/home/ubuntu/certonomous-runs/RUNG0b_exports/` | **ABSENT** |
| results record | `verification/runs/RUNG0b_MESH_IMPORT_runs/RESULTS.json` | **ABSENT** |

**THE STRUCTURAL DEFECT THIS FILING FIXES, AND IT IS GENERAL RATHER THAN ABOUT THIS
RUNG.** The predecessor filed its comparator at
`verification/runs/RUNG0_MESH_IMPORT_runs/analyse_rung0.py` — **inside the run root
whose ABSENCE was its own pre-compute proof** under rule 2 (*"name the run directory that
does not exist"*). **Those two conditions cannot both hold at one commit**: committing
the comparator creates the run root, and an existing run root voids the absence proof.
Its queue row therefore measured **`ABSENT-AT-FREEZE`** and **no honest pin existed**.
Filing the whole grading path in `cases/` dissolves it: the freeze commit carries the
comparator, the writer and the reader **while the run root does not yet exist**, so
`git rev-parse <freeze>:cases/committee-grids/grade_rung0b.py` resolves and **the pin is
derivable**. The queue entry's `grading_freeze` names **all three** grading-path files.

**NO-COMPUTE CONDITION, CHECKED BY DIRECT FILESYSTEM TEST AT DRAFTING TIME AND NAMED
HERE SO IT CAN BE RE-CHECKED** — three ways, in the drafting shell:
`test -e verification/runs/RUNG0b_MESH_IMPORT_runs` → **non-zero**;
`find verification/runs -maxdepth 1 -iname 'RUNG0b*'` → **0 hits**;
`git ls-tree -r HEAD --name-only | grep -ci RUNG0b` → **0**.
`/home/ubuntu/certonomous-runs/RUNG0b_exports` → **ABSENT**.

---

## 10. LAUNCH

**NOT LAUNCHED BY THIS FILE.** Under Sanaa's 2026-09-03 ~21:00Z rule a pre-registration
mismatch never prevents a launch — the mismatch is recorded as a prediction, the run
launches under its monitor, and the frozen grader judges afterward on the certificate.
**No mismatch is predicted here**: the grading path exists at the freeze, the pin is
derivable, and the run root is absent.

**The one check that gates this launch is a person's, not a rule's:**
`SUPERVISION_CHARTER.md` §3 check 4 — *pre-registration committed before compute* — is
**the cfd supervisor's, personally, and is not delegable to a lane.** The supervisor has
stated they will confirm this commit exists before the run starts. **This lane does not
launch and has not launched.**

---

## 11. AUTHORITY

| what | where |
|---|---|
| the ruling that produced this successor route | **`f5b8deec`** — verification `CHARTER v1.52` |
| the predecessor, **not amended** | `verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md`, frozen **`d127d83d`** |
| the predecessor's verdict, **standing as committed** | `verification/runs/RUNG0_MESH_IMPORT_runs/RESULTS.json` — rung **`PENDING`**, sha256 `d0686c23…` |
| this team's own correction of the framing it sent upward | `verification/runs/RUNG0_MESH_IMPORT_runs/CORRECTION_no_pass_branch_framing.json` |
| the R0-G2b **measurement** (not a verdict) | `verification/runs/RUNG0_MESH_IMPORT_runs/R0G2B_DIAGNOSTIC_NOT_A_GRADED_RUN.json` |
| the falsifier that did **not** falsify verification's reading | `verification/runs/RUNG0_MESH_IMPORT_runs/CONTROL_2d1_CONDITION2_NOT_A_GRADED_RUN.json` |
| cost calibration for the predecessor | `docs/COST_CALIBRATION.md`, row `C-20260903T180819.145643Z-49087129` |
| the envelope this rung draws on | `docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md` |

---

## AMENDMENT 1 — 2026-09-03, **PRE-COMPUTE** — disclosure of a MEASURED defect in the pinned converter, and the exact scope of what a RUNG0b `PASS` would and would not certify

**Version: v1.0 → v1.1. Lines whose number changed above this section: 0.**
**This amendment CHANGES NO GATE, NO THRESHOLD, NO CAP AND NO LABEL. It is disclosure,
which is what rule 2's pre-compute amendment is for.**

**THE CONDITION, AND HOW IT WAS CHECKED — rule 2 requires both, so both are here, checked
in this amendment's own shell before it was written.** The run directory that does not
exist is **`verification/runs/RUNG0b_MESH_IMPORT_runs`**. Verified absent three ways:
`test -e` → **non-zero**; `find verification/runs -maxdepth 1 -iname 'RUNG0b*'` → **0
hits**; `git ls-tree -r HEAD --name-only | grep -c RUNG0b_MESH_IMPORT_runs` → **0**. The
export root `/home/ubuntu/certonomous-runs/RUNG0b_exports` is likewise **ABSENT**.
**NO COMPUTE HAS OCCURRED UNDER THIS REGISTRATION. NOT ONE GRID HAS BEEN CONVERTED, NOT
ONE GATE HAS READ A NUMBER, AND NO `RESULTS.json` EXISTS.**

### Why this amendment exists, and it is this team's own lesson turned on itself

`docs/LESSONS.md` **L-467**, filed by this team **today**, says: *the population that
validates an instrument must be shown to contain the feature the instrument handles, or
the validation is vacuous for that feature.* **RUNG0b tests `ugrid_to_foam.py` as the
artefact under test, on a population where that converter's known defect CANNOT FIRE.**
If RUNG0b returns `PASS` and the record does not say so, the certificate reads *"this
converter works"* when what was measured is *"this converter works on grids that cannot
trip its known defect."* **That is the same vacuity one level up, and writing it down
before the run is the only thing that stops it.**

### (i) The pinned blob carries a MEASURED defect

**§9 pins `cases/committee-grids/ugrid_to_foam.py` as the artefact under test. VERIFIED
BY THIS LANE, in this amendment's own shell:
`git show ace20cb1:cases/committee-grids/ugrid_to_foam.py` is `sha256 e2ce16902f09925b…`,
**17,590 bytes** — which is the **DEFECTIVE** copy, not the clean 15,004-byte one.
**The freeze pins the defective blob, deliberately and now on the record.**

The mechanism, **read by this lane directly out of that pinned blob** at its `sniff_layout`
(`:53-63`) rather than taken on report: the Fortran record-marker test runs **first** and
returns on `== 28`; only if that fails does control reach a **plausibility** branch that
accepts **the first byte order giving `0 < n < 2e9`, big-endian first**. A raw-C-stream
UGRID whose byte-swapped first word stays positive and under 2e9 is therefore **silently
mis-detected**, with no error and no warning.

### (ii) That defect is PROVEN INERT for this rung's four grids — and the proof is TEST ORDERING, not size

- **DPW5 L1.T hex, prism and hybrid** are **Fortran unformatted**. The record-marker test
  (28 big-endian, against 469,762,048 little-endian) **fires BEFORE the defective
  plausibility branch is ever reached.** The defect is unreachable for them by control
  flow, not by luck of magnitude.
- **HLPW6 `h6c1_rans_3a_1`** is the **only** one of the four saved by the negative-overflow
  mechanism instead.

> **⚠ THE PROVENANCE OF (ii) IS DISCLOSED RATHER THAN SMOOTHED, AND IT IS NOT YET FULLY
> ANCHORED.** The **13-header byte-budget audit** establishing that the defect mis-detects
> **only M6I L3/L4/L5** — and **nothing** in RUNG 0's population and **nothing** in the four
> R0-G2b round-trip exports — was performed by the **RUNG1 M6 lane**, not by this one. This
> lane was instructed **not to re-derive it** and has not. **At the time of this amendment
> that audit and its five-copy manifest are NOT COMMITTED and this lane could not locate
> them on disk under any search term.** The one artefact of that package that does exist is
> `verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/CONVERTER_CALLER_SCAN_certonomous_runs.json`
> — the **CLOSED** caller scan, `files_scanned` **9,225**, `skipped_over_50MB` **0**,
> `unreadable` **0**, `"COMPLETED": true`, 6 hits — and it is **UNTRACKED**, so it is cited
> here by path **and by its on-disk `sha256 1a1ea18d4c3dbaf9dbb1b14f8013612a…`**, which is
> resolvable and tamper-evident even while uncommitted.
>
> **CONSEQUENCE, STATED PLAINLY: the TEST-ORDERING half of (ii) is VERIFIED BY THIS LANE**
> (it is a property of the pinned blob's own source, quoted above, and of the three DPW5
> grids' registered `.r8` layout). **The 13-header audit half is RELAYED, NOT VERIFIED HERE,
> and rests on a record that is not yet in the repository.** The M6 lane owes that commit.
> Until it lands, **(ii) is a disclosed dependency rather than a closed proof**, and this
> sentence is what stops a later reader taking it for one. **It does not block the run**:
> the test-ordering argument alone already makes the defect unreachable for three of the
> four grids, and no gate in this registration reads the converter's layout decision.

### (iii) What a RUNG0b `PASS` would certify, and what it would NOT

> **A `PASS` HERE CERTIFIES THE CONVERTER ON THIS POPULATION ONLY — the four grids of §3,
> three Fortran-unformatted and one large raw C stream. IT MAKES NO CLAIM WHATEVER ABOUT
> SMALL RAW-C-STREAM UGRID FILES**, which are precisely the class the pinned defect
> mis-detects. Anyone citing a RUNG0b `PASS` for a `.b8`/`.lb8` grid outside this
> population is citing it for something it did not measure.

This joins §8's non-claims as **non-claim 10** and is binding on every downstream citation.

### (iv) The repaired converter is registered elsewhere, and NO COPY IS TOUCHED HERE

The repair rides the **M6 R2** registration — the lane whose population **contains** L3/L4/L5,
which is to say the population where the defect **fires**. **Repair it where it matters and
test it there.** This amendment **touches no converter copy**: the dedup end-state is
unresolved, five copies exist across two trees at two distinct hashes, and repairing one of
them is exactly the divergence hazard. **`cases/committee-grids/ugrid_to_foam.py` is
byte-unchanged and stays pinned as `e2ce1690…` for this rung.**

### What this amendment does not do

It does not move a gate, a threshold, a cap or a label; it does not alter §3's population,
§4's five gates, §5's 4.4/13.2/39.6 core-min figures, or §7's eleven controls. It does not
grade anything. **It does not authorise a launch** — `SUPERVISION_CHARTER.md` §3 check 4
remains the cfd supervisor's, personally and undelegably, and he has stated he will confirm
**both** this registration's commit **and** this amendment's commit exist, by reading them
himself, before anything computes.

---

## ADDENDUM NOTE TO AMENDMENT 1 — 2026-09-03, **STILL PRE-COMPUTE** — the caller scan is now COMMITTED; the 13-header audit is NOT, so clause (ii)'s marking STANDS

**Version: v1.1 → v1.2. Lines whose number changed above this section: 0.**
**Changes no gate, no threshold, no cap, no label. It does not rewrite Amendment 1 —
Amendment 1's text stands exactly as committed at `0b6cb24f`, including the sentence this
note supersedes.**

**WHY THIS NOTE EXISTS: AMENDMENT 1 ASSERTS SOMETHING THAT BECAME FALSE 38 SECONDS AFTER
IT WAS WRITTEN, AND THAT IS THE SAME DEFECT SHAPE THIS TEAM CORRECTED THIS MORNING** — a
frozen record asserting `DOES NOT EXIST` about a file that exists
(`CORRECTION_no_pass_branch_framing.json`). It is corrected the same way: by an appended
note, never by an edit.

### What changed

| Amendment 1 said | Now, verified at HEAD by this lane |
|---|---|
| `CONVERTER_CALLER_SCAN_certonomous_runs.json` **"IS UNTRACKED"** | **COMMITTED at `10ba2567`**, 2026-09-03T19:33:48Z — *"cfd converter-caller population CLOSED: five copies of `ugrid_to_foam.py` exist on this box, not three, and THREE carry the defective byte-order branch byte-identically"* |

**THE CONTENT-HASH CITATION DID ITS JOB, AND THAT IS WORTH RECORDING RATHER THAN PASSING
OVER.** Amendment 1 cited that file by on-disk `sha256 1a1ea18d4c3dbaf9dbb1b14f8013612a…`
precisely because it was uncommitted. **`git show 10ba2567:<path> | sha256sum` returns
`1a1ea18d4c3dbaf9dbb1b14f8013612a…` — byte-identical.** The citation resolves onto the
committed blob with nothing to reconcile. **A path-plus-content-hash citation of an
uncommitted artefact upgrades cleanly; a bare path citation would not have.**

**THE CROSSING IS DISCLOSED, NOT SMOOTHED.** `10ba2567` landed at **19:33:48Z** and
Amendment 1 at **19:34:26Z** — **38 seconds apart**. This lane's search ran before the
commit existed, so the amendment's report was **true when written and stale when read**.
It was not a failed search; it was an early one. Recorded because "my search found
nothing" and "it was not there" are different claims, and only the second was ever
warranted.

### What has NOT changed, and clause (ii)'s marking therefore STANDS

**`10ba2567` contains EXACTLY ONE FILE — the caller scan, 31 insertions.** It does **not**
carry the **13-header byte-budget audit** or the **five-copy manifest**. Verified by this
lane at HEAD: `git ls-tree -r HEAD` matching `13[-_]?header|five_copy|BYTE_BUDGET|
LAYOUT_AUDIT` → **0 hits**; the same terms in `10ba2567`'s own file list → **0 hits**.

> **CLAUSE (ii)'s "RELAYED, NOT VERIFIED HERE" MARKING IS NOT LIFTED BY THIS NOTE.** The
> **test-ordering** half remains verified by this lane from the pinned blob's own source;
> the **13-header audit** half remains relayed and remains unanchored in any committed
> record. **It is lifted only by a further dated note citing that audit's own path and
> commit, once the M6 lane lands it as its own item.** Until then §8's **non-claim 10**
> and clause (iii)'s population limit carry the full weight of the disclosure, which they
> were written to do.

**NOTHING HAS COMPUTED.** Re-checked in this note's own shell: `verification/runs/RUNG0b_MESH_IMPORT_runs`
**ABSENT**, `/home/ubuntu/certonomous-runs/RUNG0b_exports` **ABSENT**, no `RESULTS.json`.
**Launch remains held on `SUPERVISION_CHARTER.md` §3 check 4** — the cfd supervisor's
personal read of `ace20cb1` **and** `0b6cb24f`, undelegable, and not performed by this lane.

---

## LIFTING NOTE TO AMENDMENT 1 CLAUSE (ii) — 2026-09-03, **POST-COMPUTE** — the 13-header audit and the five-copy manifest are COMMITTED at `b78e8858`; clause (ii) is now VERIFIED-BY-COMMITTED-ARTIFACT and its RELAYED marking is LIFTED

**Version: v1.2 → v1.3. Lines whose number changed above this section: 0.**
**Changes no gate, no threshold, no cap and no label. It upgrades a CITATION and
nothing else.** Amendment 1 and the addendum note at `75ad7ef9` are **not rewritten**;
their text stands exactly as committed, RELAYED marking included, and this note is the
correction beside them.

**⚠ THIS NOTE IS POST-COMPUTE AND SAYS SO. RUNG0b RAN AT 19:40:38–19:45:04Z.** Under
rule 2, gates close at first compute and changes land only as dated addenda that cannot
alter a gate, threshold, cap or label. This one cannot and does not.

> **BUT THE EVIDENCE ITSELF IS PRE-COMPUTE, AND THE 50 SECONDS ARE STATED RATHER THAN
> GLOSSED.** `b78e8858` was committed at **19:39:48Z**; RUNG0b's `RUN_ROOT_CREATED_EPOCH`
> is **19:40:38.500946Z**. **The artifacts were in the repository 50 seconds before this
> rung's first compute.** The *evidence* anchoring clause (ii) therefore predates the run;
> only the *note recording it* does not. Both facts are here so neither can be read as the
> other.

### What is now citable by path and commit

| artifact, at `b78e8858` | what it establishes |
|---|---|
| `verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/UGRID_HEADER_AUDIT.json` | **13 files audited, 3 mis-detecting**, and the three are `M6I_runs/mesh/wing_strct.{3,4,5}.lb8.ugrid` — **nothing in RUNG 0's population and nothing in the four R0-G2b exports.** Carries `control_both_outcomes_observed: true`: it **refuses unless it observes both agreement and disagreement**, so its zero for RUNG 0 is a zero from a reader shown able to see a non-zero (rule 3) |
| `verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/CONVERTER_COPY_MANIFEST.json` | **5 copies, 2 equivalence classes, 3 defective.** Carries `control_frozen_copy_present_and_defective: true` |
| `verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/audit_converter_and_ugrid_headers.py` | the instrument that produced both, re-measured from disk |

**THE MANIFEST INDEPENDENTLY REPRODUCES THIS REGISTRATION'S OWN §9 PIN CHECK.** Its
defective class is `e2ce16902f09925b22cd…` and its `paths_carrying_the_defect` lists
`/home/ubuntu/Certonomous/cases/committee-grids/ugrid_to_foam.py` **first** — the exact
blob Amendment 1 clause (i) verified independently from `ace20cb1`. **Two instruments,
neither aware of the other, agree on which blob this rung pinned.**

### Clause (ii) restated, now on committed evidence

The audit's own `why_the_RUNG0_grids_are_safe_CORRECTED` field carries the mechanism
verbatim:

> *"NOT because they are large. The three DPW5 grids are Fortran unformatted and the
> record-marker test fires BEFORE the defective plausibility branch is reached: the marker
> reads 28 big-endian and 469,762,048 little-endian. Only HLPW6 is saved by the overflow
> mechanism. They are safe BY THE ORDERING OF THE TESTS, not by their size — a correct
> conclusion that rested on a wrong mechanism until it was measured."*

> **CLAUSE (ii)'s "RELAYED, NOT VERIFIED HERE" MARKING IS LIFTED. Both halves now stand
> on evidence: the test-ordering half verified by this lane from the pinned blob's own
> source, and the 13-header half verified by a committed instrument carrying its own
> refusal control.**

### What is NOT lifted, and this is the part that outlives the run

**§8 non-claim 10 and clause (iii) STAND UNCHANGED AND ARE NOT SOFTENED BY THIS NOTE.**
RUNG0b's `PASS` certifies the converter **on this population only** — three
Fortran-unformatted grids and one *large* raw C stream — and **makes no claim whatever
about small raw-C-stream files**, which is precisely the class the audit measured the
defect mis-detecting. **A closed proof that the defect was inert here is not a claim that
the converter is sound**; the manifest records three defective copies still on this box,
one of them outside git, and the repair is sequenced strictly after this record lands and
rides the M6 R2 registration.

**Also disclosed for the repair package and NOT acted on here (rule 6 — the pinned file is
not touched):** all **eight** guards in the pinned converter are **bare `assert`
statements** (`:81, :85, :97, :99, :204, :251, :292, :296`), so `python3 -O` deletes every
one of them (L-332). The byte-budget check at `:85` is doubly conditional — inside
`if fortran:` **and** an assert — so a raw C stream gets none of it, and `:296`
(`nbnd == ndecl`), the only structural check such a file does get, is an assert too.
**VERIFIED SAFE FOR THIS RUN AND CHECKED BEFORE LAUNCH, NOT ASSUMED:** `PYTHONOPTIMIZE`
unset, `__debug__` true, and no `-O` anywhere in `run_rung0b.sh`, so every guard executed.
