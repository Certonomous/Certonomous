# Curriculum item AV2RG — AV2R and AV2 re-graded from their preserved run roots through the recovered `gmresRelTol`: RESULTS

**Team:** dafoam. **Lane:** `lab-lane`. **Date:** 2026-08-30.
**Solver compute: ZERO.** Nothing meshed, nothing solved, no container, no GPU.
**Pre-registration:** `PREREGISTRATION.md`, frozen `2f827746` (v1.0), amended pre-compute
`42a3c988` (v1.1, Amendment 1 — AV2 added), amended post-compute under
`VERIFICATION_CHARTER.md` §2d.1 at `cb9adb7f` (v1.2, Amendment 2 — two unit assertions).

> **A NOTE ON THIS DOCUMENT'S SHAPE, because the instruction and the charter disagreed.** The
> assigning ruling asked for "the `REPORTING_CHARTER`'s six fixed headings matched literally".
> **Those six headings are the MORNING REPORT's frame** (`REPORTING_CHARTER.md:48-63`:
> `CERTONOMOUS MORNING REPORT` … `## 1. SPEND` … `## 6. WAITING LIST`), and §2 rule 2 forbids
> adding to or retitling them. A case `RESULTS.md` wearing that frame would be a **false
> morning report**. This document therefore follows the family's own convention for a
> successor re-grade — `curriculum_AVWC/RESULTS.md` and `curriculum_D6RG/RESULTS.md` — and the
> departure is flagged to the supervisor rather than taken silently.

---

# 1. Item verdicts

| item | ORIGINAL | **RE-GRADED** | rows (SHIPPED / PATCHED) | names rebound |
|---|---|---|---|---|
| **AV2R** | `NOT A RESULT` — `G-DP` refusal, `gmresRelTol_in_artefact: null` | **`BLOCKED`** | `BLOCKED` / `BLOCKED` | **`[]`** — none |
| **AV2** | `NOT A RESULT` — `G1 age_reference_absent`, then `G-DP` `gmresRelTol_in_artefact: null` after AVWC's datum repair | **`BLOCKED`** | `BLOCKED` / `BLOCKED` | **`["arm_datum"]`** |

**The word changed and so did the object.** Both items previously died at a **refusal** — the
comparator stopped and no gate returned a reading. Both now produce a **composed verdict**
from gates that all ran. `BLOCKED` here is a statement about **DAFoam**, not about a missing
field: the forward-mode AD channel does not produce a tangent on this case.

**Source:** `AV2RG_regrade.json`, `AV2RG_full_grades.json`.

# 2. What the repair bought — every reachable gate returned a reading

| gate | AV2R | AV2 |
|---|---|---|
| `G1` completion (all five arms) | reached, no refusal | reached, no refusal |
| `G-M2` mesh identity | **`PASS`**, cells **4032** | **`PASS`**, cells **4032** |
| `G9` toolchain (3-source) | **`PASS`** | **`PASS`** |
| `G10` caps | **`PASS`**, **20.766** core-min vs ceiling **75.0** | **`PASS`**, **19.085** core-min vs **75.0** |
| `G12` placement | **`PASS`** | **`PASS`** |
| `G-DP` SHIPPED / PATCHED | **`BLOCKED`** both, on `CD` and on `CL` | **`BLOCKED`** both |

**Recovered `gmresRelTol` = `1e-06`** (dimensionless) on **all four repaired arms of both
items**, from all three registered sources in exact agreement. **The artefact mtime was
preserved on every one** (`mtime_preserved: true` × 4 × 2), so the rule-4 age guard still
dates the solver's write and not this instrument's.

**Source:** `AV2RG_full_grades.json`; `PREREGISTRATION.md` §A2.6.

# 3. Why `BLOCKED` — the forward channel, and it is one failure repeated twenty times

**5 of 5 registered components are `blocked` on `CD` and on `CL`, on the SHIPPED row and the
PATCHED row, in both items** — twenty component-readings, **zero graded**, and **one distinct
reason** across all of them:

```
AnalysisError("'scenario1.coupling.solver' <class DAFoamSolver>:
              Error calling solve_nonlinear(), Primal solution failed!")
```

The forward-mode primal does not converge. This is **exactly the outcome AV2R's own frozen
text anticipated** (`curriculum_AV2R/PREREGISTRATION.md:156`), which also fixes its scope: it
says nothing about forward mode *in general* — only that **on this case, at this `endTime` and
this `primalMinResTolDiff`, the primal does not reach acceptance.** That limit is inherited
here unchanged.

**Two of the frozen grader's own controls consequently did not run, and the record says so
rather than implying they passed:** `sign_flipped_XS_read_as_GATE_FAIL` and
`silent_zero_FADS_refused` both report `seen: false`, because `av2r_grade.py:530-532` takes
its registered `blocked_any` branch — *"FAD-S blocked; the transpose control has nothing to
read"*. **A control that had nothing to read is not a control that passed.**

**Source:** `AV2RG_full_grades.json` `gates.G-DP_SHIPPED.G-DP_CD.components`, `.controls`.

# 4. Prediction P1, registered before execution — **HIT**

`PREREGISTRATION.md` §8 registered: *"the re-graded item will not read `PASS`… the most likely
outcome is `BLOCKED` from the `FAD` rows"*, reasoning from AV-2's `5/5 BLOCKED` forward rows
and explicitly stating that `blocked_any` had **not** been read from AV2R's own artefacts
before the freeze. **Both items read `BLOCKED`.**

The **frozen items' own** predictions, scored by their own code and not adjusted: `P4`
forward-channel controls **HIT**; `P5_total_core_min_band` **HIT**; `P6_mesh_wall_le_120s`
**HIT**; `P7_cells_4032` **HIT**; `P5_fad_over_x_cost_ratio_shipped` **MISS**; `P1`, `P2`,
`P3` **`NOT_MEASURED`** — they are all questions about graded components, and there are none.

# 5. THE THIRD INDEPENDENT INSTRUMENT LANDS ON `shape[0]` AND `shape[6]`

The shipped-vs-patched divergence on the **reverse** `CD` gradient is **reported, never
gated** (`av2r_grade.py:537-542`), and it is **identical in both items** to every digit — same
case, same images, same `np = 1`:

| component | divergence, SHIPPED vs PATCHED |
|---|---|
| `shape[0]` | **10.6497 %** |
| `shape[3]` | 4.0095 % |
| **`shape[6]`** | **118.7258 %** |
| `shape[7]` | 1.7374 % |
| `patchV[1]` | **0.0000 %** |

Set beside the two independent readings already on record:

| instrument | `shape[0]` | `shape[6]` |
|---|---|---|
| **AV2RG** (this item) — toolchain divergence, reverse `CD` | 10.6497 % | **118.7258 %** |
| **SO1aR** — FD vs adjoint, shipped row (`curriculum_SO1aR/RESULTS.md:53,:80`) | 11.9330 % | **637.7570 %, SIGN FLIPPED** (and `dCL/dx` 19.8033 %) |
| **`A_stepsize_study.md`** — FD step plateau | excluded from the plateau (`:45-46`) | excluded; *"no step at which idx6 is a trustworthy estimate"* (`:40`) |

**Three instruments, three methods, one pair of design variables — and `patchV[1]`, which
cannot cross `warpDeriv`, reads exactly `0.0000 %`, which is the control that makes the other
four numbers legible.**

**NOTHING CAUSAL IS CLAIMED.** This is a convergence, not a mechanism. It is recorded with its
citations so it is not lost in a table. **SUBMISSIONS REMAIN PARKED** (rule 7): nothing here
is filed, sent or reported outside this box.

**Source:** `AV2RG_full_grades.json` `divergence_rev_shipped_vs_patched_CD`;
`cases/dafoam/ladder-a/A1/curriculum_SO1aR/RESULTS.md:53`, `:80`;
`cases/dafoam/ladder-a/A_stepsize_study.md:40`, `:45-46`.

# 6. The FD position — registered as a split, and it does not collapse

Per the supervisor's ruling of 2026-08-30 (`PREREGISTRATION.md` §A1.4): AV2R is the
forward-AD-versus-reverse-AD **duality** rung, whose reference is an **exact** derivative with
no step and no plateau question, so `DAFOAM_CHARTER.md` §2's second clause discharges the
bright line **by forward AD rather than by FD**. Per component:

* **MAY claim FD corroboration:** `shape[3]`, `shape[7]`, `patchV[1]`.
* **MAY NOT:** **`shape[0]` and `shape[6]`** — outside the five-of-eight plateau.

**On this run the distinction is moot in one direction and sharp in the other:** the duality
reference itself never produced a value (§3), so **neither** the forward-AD discharge **nor**
the FD corroboration delivers a number for any component here. **AV2RG quotes no FD verdict
and no duality verdict.**

# 7. The birth requirement — 28/28, both directions, on the real frozen graders

**`rc = 0` under `python3` AND `python3 -O`, 28 of a frozen `EXPECTED_UNITS = 28`, failures 0**,
from a **proven-clean** state (`__pycache__` verified 0 before and after each pass).

Must-flag limbs that carry the item: **U13–U18** every source absent or disagreeing, and the
`runScript` md5 pin firing **before** any value is parsed; **U19/U25** a wrong-but-present
`1e-5` makes each item's **own frozen clause** fire; **U20** the age guard still refuses a
back-dated artefact; **U21** a doubled reverse total does not read `PASS`; **U22** AV2 with the
`GMRES` repair **alone** still refuses on the datum, proving it carries both defects;
**U27/U28** the two post-compute-corrected assertions are **driven to FALSE** with the reader
stubbed not to refuse, and the stub's restoration is itself checked.

**Source:** `av2rg_selftest_evidence_v1_2_clean.txt`; the failing predecessor run is preserved
unaltered in `av2rg_selftest_evidence.txt`.

# 8. The preserved roots were not mutated — read from the disk, not from git

md5 manifest of **every regular file** taken before and after **every** re-grade:
**378 files** in each root, `root_manifest_identical: true` throughout, including all 15
re-grades of the selftest. Independently reconfirmed afterwards: 378 files each, **0 entries
newer than 2026-08-29**. A run root is not in git, so `git status` is blind to exactly the
thing being protected.

# 9. The frozen files were never edited — proved by hash

`av2r_grade.py` `8a2dcebd954f56d9970601fc7761787a`, `av2r_xf.py`
`32a755bc9fa84bc0e03ab02bb6ec3c3c`, `av2_grade.py` `4bde0ad7dbdd3e460dcef1fe6d063979`,
`av2_xf.py` `76bc93090062e0bf03de2344709e384f`, `avwc_grade.py`
`6e390f8f3c0df5d4229dd3640590ca44`, `avwc_reader.py` `1a7f3f211f44c7b67b4f8f2d4c65bf4a` —
each verified **disk == `HEAD` blob**, and each re-verified by the comparator itself at
execution, which refuses on a mismatch. AV2R's and AV2's own `PREREGISTRATION.md` registrations
of the first two were checked against, not accepted from.

**AV2R's `RESULTS.md` does not exist** — that item never landed one — so a successor note is
appended to **AV2's** `RESULTS.md` only, and AV2R's successor record is this document plus its
own frozen pre-registration.

# 10. Two defects in this item's own instruments, disclosed rather than patched

1. **v1.0 laundered a physics guard, and it was caught before first compute.**
   `repair_identity_in_copy` rewrote the artefact and stamped it with **the successor's own
   mtime**, which would have satisfied the frozen age guard (a rule-4 PHYSICS field) *because
   of the instrument's own write*. Closed with the mtime restore-and-verify plus **U9** and
   **U20**. Full write-up at `PREREGISTRATION.md` §A2.6. **General rule for the next
   successor: a repair that touches a file touches every property of that file a grader might
   read, and content is only one of them.**
2. **v1.1's selftest FAILED, 24/26**, on two unit **assertions** naming a clause the reader
   cannot raise on that path. Repaired only under §2d.1, with the four conditions tested one
   at a time, the corrected assertions **driven** able to fail, the whole battery re-run from
   clean, and **`VERDICTS MOVED: 0, BANDS MOVED: 0, THRESHOLDS MOVED: 0, REFUSAL CLAUSES OF
   THE FROZEN GRADER MOVED: 0`**. The exception was granted by **this family's own supervisor
   on this family's own item**; the protection is condition (2)'s blindness — **the verdicts
   in §1 were read only after the repair was committed** — and the ruling is routed to
   `verification-supervisor` for independent audit. **If verification overturns it, the repair
   is withdrawn and this section says so.**

# 11. Cost — actual against the frozen estimate (rule 12)

| | |
|---|---|
| Registered (v1.1) | **6.00 core-min**, cap **15.00**, ranks 1 |
| Measured | **≈ 0.20 core-min** — failing v1.1 battery 5 wall s, repaired v1.2 battery 5 wall s, real re-grade < 1 s, evidence dump ≈ 1 s, at ranks 1 |
| Ratio actual / predicted | **≈ 0.033**; **1.3 % of cap** — the cap was never approached and nothing was stopped |
| Attribution | **MISPREDICTION, not waste.** An instrument-only re-grade of preserved artefacts is dominated by **I/O, not CPU**, and both roots were **warm** in the page cache from the earlier passes. This is the third row in a row (`C-212` 20.1× cold/warm, `C-214` ≈ 7×) to miss on the **cache-state term**, and this estimate still did not carry one |
| Waste | **0 core-min.** The failing v1.1 battery is **not** waste: it bought the finding that two controls were mis-specified, which is the birth requirement doing its job |
| Dollars | **$0.000171 — DERIVED, NOT MEASURED** at $0.0513/core-h; `cost_basis` **REPORTED-BY-OWNER** (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Carry-forward:** price a warm manifest of a ~380-file / 26 MB root at **≈ 0.15 s**, and
**state which cache state the estimate assumes** — an estimate that does not say is
unfalsifiable by an order of magnitude.

# 12. What this item establishes, and what it does not

**Establishes.** That AV2R's and AV2's `G-DP` refusals were a **producer** defect — one
byte-identical `idwarp_identity()` omitting one key — and not a missing measurement: the
tolerance was on disk three ways, at `1e-06`, on every arm. That with the field restored, both
items compose a verdict from gates that all return, and that verdict is **`BLOCKED`** because
the **forward-mode AD primal fails on this case**. That `G-M2`, `G9`, `G10` and `G12` all
`PASS` on both items, which was previously unknown because the comparator never reached them.

**Does not establish.** Nothing about physics, mesh or solver beyond the forward-mode primal's
failure **on this case at these settings** — no solver ran here. **No duality result**: the
dot-product test remains **not measured** in this family, and this item does not move that
census line. **No FD verdict.** Nothing about forward mode in general. No capability-grid cell
moves. **A `BLOCKED` is not a `PASS` deferred** — it is the registered mapping for a row whose
forward channel returned nothing.

# 13. What is owed, and to whom

* A `docs/COST_CALIBRATION.md` row, landing with this document.
* A dated successor note appended to `curriculum_AV2/RESULTS.md` (AV2R has none).
* **The `verification-supervisor` audit of the §2d.1 grant**, routed by the dafoam supervisor.
* **Nothing is enqueued:** this item registers no solver arm, so there is nothing runnable for
  the overnight queue to carry.

# 14. Artefacts, all still on disk

`PREREGISTRATION.md` (v1.2, Amendments 1–2) · `av2rg_grade.py` md5
`2dc1cc87eada389da28118e2c3318fd0` · `av2rg_reader.py` md5
`51f65b1d67885b8960201acfc1d2a44d` · `av2rg_dump_full_grades.py` · `AV2RG_regrade.json` ·
`AV2RG_full_grades.json` · `av2rg_selftest_evidence.txt` (the failing v1.1 run, preserved) ·
`av2rg_selftest_evidence_v1_2_clean.txt` (28/28) · preserved roots
`/home/ubuntu/certonomous-runs/CURRICULUM-AV2R-a1-naca0012-duality` and
`/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality`, 378 files each, unmutated.
