# T18 results — 3-D transient conduction in a cube (T11c), Robin faces on all three axes, EXACT tier

**Document version 1.0.** Rung `T18`, pre-registration
`docs/campaigns/T-family/T18_PREREGISTRATION.md`, frozen at commit
**`add2c78870625c75c2a48bdff018d7a034a2ff84`**. Run root
`verification/runs/T-family/T18_runs/`. Graded by the frozen `analyse_t18.py`,
gate artifact written 2026-08-31T15:11:44.670Z. Drafted by a heat-transfer
`lab-lane` 2026-08-31 on the heat-transfer supervisor's declaration
`[lab-attributed]`.

**THE DECLARED VERDICT — T18 rows G1, G2 and G3: `PASS`.**

**The declaration is the supervisor's act, not this lane's.** It was made on the
evidence in `verification/runs/T-family/T18_runs/T18_VERDICT_READINESS_AUDIT.md`
(landed at `a368b35b`) and `verification/runs/T-family/T18_runs/gate_t18.json`
(landed at `b6a56f20`). This document records that verdict and re-derives its
grounds from the artifacts; it does not decide it, widen it or restate it.

**And the rung's registered ceiling is `GATE REACHED`, not higher.**
`T18_PREREGISTRATION.md:29-32` and `gate_t18.json:4` both record, before compute,
*"GATE REACHED at best — the reference is EXACT, so this rung scores V and never
P; it can never reach HOLDS."* **The three `PASS` rows are gate verdicts against
an analytic referent; they are not a capability claim**, and nobody may read this
record as one. Whether the rung is worth its registered ceiling is a supervisor
ruling and is not taken in this document.

---

## 0. SCOPE — stated first, because it bounds everything below

`gate_t18.json:3` carries the scope the registration fixed: **"SOLID-ONLY 3-D
transient conduction (T11c); NOT conjugate, NOT a flow case."** Three limits
follow and none of them is a footnote:

- **Solid only.** `laplacianFoam` solves for `T` alone. There is no fluid, no
  momentum equation and no turbulence closure in this rung.
- **Not conjugate.** Nothing here is earned for a solid-fluid interface.
- **This is CODE VERIFICATION against an analytic referent, NOT VALIDATION
  against a public primary source.** The reference is the 80-term separable
  series of `exact_t18.py` (`T18_PREREGISTRATION.md:49-84`). **No comparison
  against published experimental or benchmark data is made or claimed here.**

`T18_PREREGISTRATION.md:25-27` said the same before the run: the rung "earns a
verdict for CONDUCTION, no flow, 3-D, EXACT tier, and nothing else."

---

## 1. Freeze verification — the file that ran is the file that was frozen

`git hash-object` on the working-tree pre-registration returns
`ffa5b145398900827fcb67b77bdf7c03a6b93958`, and
`git rev-parse add2c788:docs/campaigns/T-family/T18_PREREGISTRATION.md` returns
**the same blob**. The working tree **is** the frozen document, so every band and
threshold cited below by line number is the registered one.

All six grading-path files match their frozen blobs recorded at
`T18_PREREGISTRATION.md:313-318` — `exact_t18.py`, `build_t18.py`,
`analyse_t18.py` (blob `66477e3945f4a622c014613e941d671e0e5525b8`, sha256₁₆
`2372422cde2e47f8`, 539 lines), `mark_done_t18.py`, `run_one_t18.sh` and
`T18_registered.json`. **Six of six MATCH; zero drift.** Rule 2's grading-path
clause is satisfied by hash rather than by assertion.

---

## 2. Completion — rule 4, six clauses, four of four cases

**The registered field tuple is `('T',)` and it was read from the frozen
document, not assumed.** `T18_PREREGISTRATION.md:187-194` registers it
explicitly and states in terms that it is **"not copied from T1b's
thermal-family tuple `T U p_rgh alphat nut k omega`"**, because the registered
closure is NONE and requiring `omega` here would make completion impossible.
The completion instrument is registered at `:172` — *"`mark_done_t18.py`, rule 4
in full including the age guard"*.

Every clause below was re-derived **from the raw artifacts** — `log.solve`,
`system/controlDict`, the time directories and filesystem mtimes. The `DONE.*`
markers were **not** consulted as evidence for any clause (see §7 for why that
matters).

| clause | `T18_CU_c` | `T18_CU_m` | `T18_CU_f` | `T18_CU_f_CT` |
|---|---|---|---|---|
| 1. `rc = 0` | 0 — holds | 0 — holds | 0 — holds | 0 — holds |
| 2. one `End` line | 1 — holds | 1 — holds | 1 — holds | 1 — holds |
| 3. last time == `endTime` | 2.0 == 2.0 — holds | 2.0 == 2.0 — holds | 2.0 == 2.0 — holds | 2.0 == 2.0 — holds |
| 4. registered tuple `('T',)` present at `endTime` | holds | holds | holds | holds |
| 5. `ExecutionTime` count == `endTime`/`deltaT` | **20000** == 2/1e-4 — holds | **20000** — holds | **20000** — holds | **40000** == 2/5e-5 — holds |
| 6. **AGE GUARD**: field at `endTime` newer than that case's own `0/T` | **+31.544 s** — holds | **+328.577 s** — holds | **+2724.947 s** — holds | **+4444.602 s** — holds |

`rc`, `capped=no`, `checkmesh_rc=0` and `note=clean` are read from each
`verification/runs/T-family/T18_runs/STATUS.<case>`.

**THE AGE GUARD IS THE STRONGEST CLAUSE HERE, AND THE REASON IS A CORROBORATION
BY A SECOND INSTRUMENT.** `0/T` is touched last at launch, so the `0/T` → `2/T`
margin *is* the solve duration:

| case | margin (mtimes) | `wall_s` in `STATUS.<case>` | agreement |
|---|---:|---:|---|
| `T18_CU_c` | +31.544 s | 32 | < 1 s |
| `T18_CU_m` | +328.577 s | 329 | < 1 s |
| `T18_CU_f` | +2724.947 s | 2725 | < 1 s |
| `T18_CU_f_CT` | +4444.602 s | 4445 | < 1 s |

The four margins are computed from filesystem mtimes; the four `wall_s` figures
were written by the launcher's own clock, **by a different mechanism, into a
different file**. Two unrelated instruments agree on four numbers to better than
a second. **A field inherited from an earlier run cannot produce that
coincidence.**

*Planted control on this document's own age-guard reader (rule 3).* "The margin
is positive on all four" is a zero. The same reader was driven on a forged case
whose `0/T` mtime was pushed 1000 s into the future: it returns a margin of
**−1000.0 s** and the guard condition fails. **The reader that found four holding
margins is demonstrably able to find a failing one.**

Also observed and reported rather than absorbed: each `endTime` directory holds
`DT`, `flux`, `gradTx`, `gradTy`, `gradTz` and `uniform` beside `T`. These are
`laplacianFoam` write-time extras, **outside** the registered tuple; no clause
above depends on them.

**Gate (1) passed on all three graded levels.** `gate_t18.json:20-45` records
`gate1.ok = true`. Worst final linear residuals are 9.993e-13 / 9.720e-13 /
9.968e-13, **more than two orders inside the registered `C_CONV` floor of 1e-10**
(`T18_PREREGISTRATION.md:166`) and at the PCG/DIC solve tolerance of 1e-12
(`:96`). The permutation-symmetry witness `W0` is 4.008e-14 / 2.010e-14 /
5.007e-14, **six to seven orders inside the registered 1e-07 floor**
(`T18_PREREGISTRATION.md:167`) — so **prediction P4 (`:241`), which asked for
`W0` < 1e-09 sharper than the gate floor, is also won**. Rule 5's order (1) did
not fire on any row.

---

## 3. THE THREE GRADED ROWS — rule 5, verified from the values and not from the label

The triple is (c, m, f) at N = 20 / 40 / 80, refinement ratio **r = 2 exact**,
`dim = 3`, `Fs = 1.25`. The artifact prints `triple_state` `"CONVERGING"` on all
three rows; **that label was not trusted.** The triples were re-analysed from
`gate_t18.json`'s own `triple` blocks by an independent implementation of
`p = ln|d21/d32| / ln r` and `GCI = Fs · |(f−m)/f| / (r^p − 1)`.

| row | c | m | f | strictly monotone? | `d21/d32` | `p` recomputed | `p` in artifact | Δ |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| **G1** | 0.617762316345 | 0.617635439403 | 0.617603711650 | **yes**, decreasing | **3.999** | 1.999612671719 | 1.999612671719 | **0.000e+00** |
| **G2** | 0.860257031950 | 0.859397830881 | 0.859183115911 | **yes**, decreasing | **4.002** | 2.000573005839 | 2.000573005839 | **0.000e+00** |
| **G3** | 0.582617282125 | 0.581737283951 | 0.581519262001 | **yes**, decreasing | **4.036** | 2.013027140186 | 2.013027140186 | **0.000e+00** |

`d21` and `d32` carry the same sign on every row, so no triple is OSCILLATORY;
`|d21| > |d32|` on every row, so none is DIVERGENT; `d21 ≠ 0`, so none is EXACT;
and every `p` is far above both imported floors, `STAGNANT_FLOOR = 0.5` and
`P_MIN = 0.05` (`scripts/roache_triple.py:170-171`, recorded in
`gate_t18.json:15-19` with `"source": "scripts/roache_triple.py (imported)"`).
**The `CONVERGING` label is earned by the values.**

**The refinement ratios are the substance.** 3.999 / 4.002 / 4.036 against the
theoretical **4.000** for a second-order scheme at `r = 2`; the registered scheme
set is `Euler` in time with `Gauss linear corrected` in space
(`T18_PREREGISTRATION.md:96`). Prediction **P2** (`:233`) required all three `p`
in **[1.7, 2.3]** — measured 1.9996, 2.0006, 2.0130, **all inside**. G3 is the
outlier at 2.013, a deviation from 2 of 0.65 %.

| row | GCI recomputed | GCI in `gate_t18.json` | Δ | `Fs` inverted out of the artifact's own `gci_pct` |
|---|---:|---:|---:|---:|
| **G1** | **0.0021412809 %** | 0.0021412809 % | 0.000e+00 | **1.2500000000** |
| **G2** | **0.0104072353 %** | 0.0104072353 % | 1.7e-18 | **1.2500000000** |
| **G3** | **0.0154349049 %** | 0.0154349049 % | 1.7e-18 | **1.2500000000** |

`Fs = 1.25` is confirmed three independent ways: `factor_of_safety: 1.25` at
`gate_t18.json:14`; `FS = 1.25` at `scripts/roache_triple.py:168`, which
`analyse_t18.py:43` imports and does not redefine; and — the strongest form —
**inverting the artifact's own published `gci_pct` for `Fs` returns 1.2500000000
on each of the three rows.** Monotonicity holds everywhere, so quoting a GCI is
legitimate on all three (rule 5's last clause).

**The fine value is the graded value on every row.** The Richardson extrapolate
is carried under `richardson_REPORTED_ONLY` and no verdict is a function of it
(`T18_PREREGISTRATION.md:158-162`).

---

## 4. THE BANDS — resolved document-first, not by matching the artifact

The failure mode that matters is a band that agrees with the artifact but not
with the frozen document, so the check ran in that direction. The band chain has
two frozen links, both inside `add2c788`:

1. `T18_PREREGISTRATION.md:118-120` — relative half-widths **±5.0e-05 (G1)**,
   **±2.5e-04 (G2)**, **±3.0e-04 (G3)**.
2. `T18_registered.json:99, 106, 113` — `band_rel` `5e-05`, `0.00025`, `0.0003`,
   the values the comparator actually reads (`analyse_t18.py:323-324`).

**The two frozen links agree with each other.** Rebuilding each band as
`reference × (1 ∓ band_rel)` from the frozen half-widths reproduces the
artifact's six endpoints:

| row | reference | band rebuilt from the frozen prereg | Δlo | Δhi | `value_fine` | inside? | half-band consumed |
|---|---:|---|---:|---:|---:|---|---:|
| **G1** | 0.6175896496 | [0.6175587701033, 0.6176205290683] | **0.000e+00** | **0.000e+00** | 0.6176037116500 | **yes** | **0.4554** |
| **G2** | 0.8591137894 | [0.8588990109775, 0.8593285678722] | **0.000e+00** | **0.000e+00** | 0.8591831159110 | **yes** | **0.3228** |
| **G3** | 0.5814449853 | [0.5812705518094, 0.5816194188006] | **0.000e+00** | **0.000e+00** | 0.5815192620009 | **yes** | **0.4258** |

**Every value sits inside less than half its registered allowance.** No row is
sitting on an edge.

The comparator does not take the reference from the registered JSON: it derives
it from `exact_t18.py` at full precision and **refuses** (`analyse_t18.py:320`)
if the derived value differs from the registered one by more than 1e-9. Measured
gaps 1.423e-11 / 2.489e-11 / 5.034e-12 — three orders inside the refusal
threshold, and explained entirely by the registered values being the derived
ones rounded to ten decimals.

Relative deviations `(value_fine − reference)/reference` are **+2.277e-05 (G1),
+8.070e-05 (G2), +1.277e-04 (G3)**. The registration predicted **+2.06e-05,
~+1.2e-04, ~+1.45e-04** at `:118-120`. **Prediction P1 (`:231`) is won**: every
measured deviation has the predicted sign and order of magnitude, and each is at
or inside its prediction.

---

## 5. THE PLANTED-ZERO CONTROLS — rule 3, three readers, three controls

`gate_t18.json:46-101` carries a control for **G1, G2 AND G3** — not one — each
with `"status": "PASS"` quoted from the artifact. **No reader is unshown.**

| reader | cells planted | plant | recovered | gain | negative arm | demonstrated detection floor |
|---|---:|---:|---:|---:|---:|---:|
| G1 (`mean_of`, averaging) | 512 000 | 1.234e-03 | 0.0012339999999999574 | **1.000** | **0.0** exactly | **1e-07** |
| G2 (`theta_at(0,0,0)`, point) | 1 | 1.234e-03 | 0.004164749999999828 | **3.375** | **0.0** exactly | **1e-07** |
| G3 (`theta_at(1,0,0)`, point) | 1 | 1.234e-03 | 0.004164749999999939 | **3.375** | **0.0** exactly | **1e-07** |

Both arms are present on each. The negative arm requires **exactly 0.0** on
identical bytes — `analyse_t18.py:186` refuses a NOISY reader — and returned
exactly 0.0 on all three. The positive arm walks a descending ladder 1 → 1e-07
and refuses if no magnitude is visible (`:208`) or if the registered plant moves
the read by less than 0.1 × plant (`:210`); every ladder is visible at every rung
down to **1e-07, four orders below the plant**.

**The G2/G3 gain of 3.375 is not an anomaly — it is a structural confirmation
that the point readers are what the registration says they are.** 3.375 = 1.5³
exactly. `theta_at` (`analyse_t18.py:123`) is separable **linear extrapolation**,
weighting 1.5 on the nearest cell centre and −0.5 on the next in each of three
directions; a plant in the single nearest cell is amplified by 1.5 per direction,
1.5³ = 3.375 across the product. A point reader that read the plant back
unchanged would have been the suspicious result. G1 averages over all 512 000
planted cells, so its gain is 1.000. The two numbers are each what the reader's
construction requires.

Containment is enforced in code, not by assertion: the control copies the case to
`mkdtemp` and **refuses if the copy resolves inside the case tree**
(`analyse_t18.py:179`), restores the original bytes after every ladder rung, and
never writes into the case.

---

## 6. DISCLOSURE 1 — the comparator's selftest reports 16 ok / 1 FAIL

**`analyse_t18.py --selftest` exits 1, with sixteen units `[ok ]` and one
`[FAIL]`.** This is stated on the document's face and not in a footnote.

The failing unit is **(v)**, the live-tree arm at `analyse_t18.py:509`:
`grade(HERE, os.path.join(tempfile.gettempdir(), "t18_never.json"), reg)`. Two
facts bound what it can touch:

- **It can write only into `tempfile.gettempdir()`.** `grade()`'s sole JSON write
  is `analyse_t18.py:354`, `json.dump(out, open(json_out, "w"), indent=2)`, to
  the `json_out` parameter and nowhere else. It cannot write `gate_t18.json`.
- **It asserts nothing about a graded quantity.** Its single assertion is that
  `SystemExit(EXIT_REFUSE)` is raised by the DONE-marker guard at
  `analyse_t18.py:266-268`. **It asserts nothing about a value, an order, a GCI,
  a band or a control.**

Every unit that does touch a graded quantity routes through a forged tree on a
`mkdtemp` copy, and **every one of those is among the sixteen that passed** — the
nine-case rule-5 ladder, the outside-band case that requires the string
`GATE FAIL`, the value control that requires all three planted-zero controls
`PASS`, and the blind-reader mutant that requires the control to refuse a reader
which ignores the plant. **The verdict in this document does not rest on unit
(v).**

---

## 7. DISCLOSURE 2 — the DONE-marker guard is now UNTESTED, and the verdict does not depend on it

Stated plainly, because a verdict that hides its own weakness is not defensible:

**Unit (v) is the ONLY test of the DONE-marker guard at `analyse_t18.py:266-268`.
That limb is therefore uncovered.** If the four `DONE.*` markers were forged or
stale, the comparator's own refusal would no longer be under test.

**This is closed for this run, and closed by construction rather than by
argument.** §2 above re-derived all six completion clauses from `log.solve`,
`system/controlDict`, the time directories and filesystem mtimes, and **the
`DONE.*` markers were deliberately excluded as evidence for every clause**. The
fact the guard exists to protect — that all four cases really completed — is
established here by direct measurement of the raw artifacts, not by the guard.
The guard is untested; **the verdict does not depend on the guard**.

The gap remains real for any *future* run of this comparator. Repairing it
belongs to a successor registration: `T18_PREREGISTRATION.md` is frozen and rule
2 bars editing it.

---

## 8. DISCLOSURE 3 — the CLASS DEFECT, referred and NOT resolved here

Unit (v)'s condition is **destroyed by completing the rung's own DONE markers**,
and completing them is a precondition of ever grading. Before
2026-08-31T14:57:46Z: selftest 17/17, grading refuses. After: grading runs,
selftest 16/17 (`T18_SELFTEST_INCIDENT_RECORD.md:103-110`). **There is no state
in which both the arm and a grade can hold.**

**This is a family-wide construction, not a T18 mistake.** The
`grade(HERE, …, "<rung>_never.json")` construction was measured by source sweep
across `verification/runs/T-family/` and recorded at
`T18_SELFTEST_INCIDENT_RECORD.md:117-134` in seven comparators —
`analyse_t9aR1b.py:367`, `analyse_t9aR1c.py:934`, `analyse_t14.py:468`,
`analyse_t15.py:918`, `analyse_t17.py:616`, `analyse_t18.py:509`,
`analyse_t19.py:691`. **Every rung carrying it converts its own control arm from
live to dead on the way to a verdict.** The honest limit on that table, carried
from its source: it records where the *construction* is present and does **not**
establish that each arm is currently inverted, which depends on each rung's
DONE-marker state and was not measured.

A repair already exists as T16c's S8a–S8e apparatus
(`T18_SELFTEST_INCIDENT_RECORD.md:138-156`), which sources the refusal from a
root guard the selftest itself controls rather than from the DONE-marker state
the campaign consumes by succeeding.

**THE CLASS DEFECT IS REFERRED TO THE HEAT-TRANSFER SUPERVISOR AND TO
VERIFICATION TOGETHER, AND IS NOT RESOLVED IN THIS DOCUMENT.** Scheduling the
repair across the rungs listed above is not this lane's call and is not taken
here.

---

## 9. DISCLOSURE 4 — a standing instruction to anyone re-checking this rung

**`gate_t18.json` is BYTE-IDENTICAL to a preserved selftest by-product.** Both
are 5186 bytes with sha256
`335bbec520a20ff461398c0b7135e451b994459a7bc7f1dfdd63700afdd7e099`; the
by-product is
`verification/runs/T-family/T18_runs/T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.json`.

Read positively, that is exactly what a deterministic comparator run twice
against an unchanged tree must produce, and it **corroborates** the registered
artifact being a real grade.

**But it means CONTENT ALONE CANNOT DISTINGUISH the registered verdict from a
selftest by-product. Only provenance can.** The two are separated by:

- **mtimes** — `gate_t18.json` at 2026-08-31T15:11:44.670Z, **323.105 s later**
  than the by-product and not nanosecond-shared with it, so it was written, not
  copied;
- **the stdout log** — `T18_GRADE_OUTPUT_20260831T151113Z.txt`, mtime 13.147 ms
  after the gate JSON, whose line 14 names by absolute path the file it follows.

> **STANDING INSTRUCTION TO FUTURE READERS: anyone re-checking T18 must use the
> mtimes and the stdout log, NEVER a diff of the values.** A value diff between
> those two files is guaranteed to be empty and proves nothing whatever about
> which is the registered grade.

---

## 10. Cost — rule 12, actual against pre-registered

`T18_PREREGISTRATION.md:270-276` registers the POINT and cap per case; actuals
are `core_min` read from each `STATUS.<case>`, basis **gross**.

| case | actual core-min | POINT core-min | ratio | cap | under cap? | `capped` |
|---|---:|---:|---:|---:|---|---|
| `T18_CU_c` | 0.533 | 0.437 | 1.220 | 3 | yes | `no` |
| `T18_CU_m` | 5.483 | 3.499 | 1.567 | 20 | yes | `no` |
| `T18_CU_f` | 45.417 | 27.989 | 1.623 | 120 | yes | `no` |
| `T18_CU_f_CT` | 74.083 | 55.977 | 1.323 | 240 | yes | `no` |
| **total** | **125.516** | **87.902** | **1.428** | **383** | yes | |

**ATTRIBUTION: MISPREDICTION — not waste and not contention.** No case stalled,
no case was `capped`, and all four completed. The only `wall_s` above 3600 is
`T18_CU_f_CT` at 4445 s, which is a registered 40 000-step run and not a stall
under the charter §2 rule.

**The registration disclosed this miss in advance, in the right direction and
larger than it landed.** `T18_PREREGISTRATION.md:259-268` names the rate as
BORROWED from T14 across a 2-D → 3-D dimension change (4-neighbour to
6-neighbour stencil) and a 2 500 → 512 000 cell jump, and states an expected
one-sided **under-prediction of up to about 3×**. **The realised miss is 1.428×
— under half the named risk.** The caps, set at 4.3× to 6.9× the point precisely
to absorb it, were never approached.

Dollars **DERIVED, NOT MEASURED** at the owner-stated $0.0513/core-h,
c7a.4xlarge, **reported-by-owner** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5): actual **$0.1073**, predicted **$0.0752**.

**One spend disclosed rather than absorbed.** The verdict-readiness audit's own
selftest execution cost **0.777 core-min** (46.60 s × 1 rank), derived $0.0007.
It is an instrument check, not a solve, carries no pre-registered cap of its own,
and is named here rather than folded into any rung figure.

---

## 11. What this document did NOT verify, and one citation corrected

- **The pre-registration's §5 comparator diff-read is the supervisor's §3 check 1
  and remains outstanding.** `T18_PREREGISTRATION.md:218-227` records it as not
  yet done at freeze time. This document hashed the six instruments against their
  frozen blobs — **that is an identity check, not a diff read, and it does not
  discharge check 1.**
- **`build_t18.py`'s mesh outputs were not re-derived.** The `polyMesh`
  directories are 166 MB and excluded from git by design
  (`T18_PREREGISTRATION.md:320-324`); mesh quality rests on the committed
  `log.checkMesh.build` and `BUILD.txt`, which this document did not re-read.
- **The launcher's real-launch arm (ARM A) was never driven on scratch**
  (`T18_PREREGISTRATION.md:296-298`). The four production runs are the only
  exercise it has had.
- **A file-count discrepancy remains unexplained**: 148 files under the four case
  trees in the readiness audit against 196 in `T18_SELFTEST_INCIDENT_RECORD.md:56`,
  taken days apart. Most likely regenerable `polyMesh` content present then and
  absent now, but **that was not confirmed**. It touches no clause above, all of
  which cite named files.
- **The `16 ok / 1 FAIL` count is cited from the readiness audit's own measured
  run**, `T18_VERDICT_READINESS_AUDIT.md:275-279`; this document did not re-run
  the selftest, because re-running it produces a further side-effect artifact.
- **CITATION CORRECTED, NOT PROPAGATED.** `T18_VERDICT_READINESS_AUDIT.md:144`
  cites the floors import as `analyse_t18.py:44`. That line is blank; the import
  `from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT` is at
  **`analyse_t18.py:43`**. An off-by-one in a citation, corrected here rather
  than carried forward. **No number moves.**
- **Nothing was sent, filed, uploaded, registered or posted. SUBMISSIONS REMAIN
  PARKED** (`CLAUDE.md` rule 7).

---

## 12. Artifacts

| what | path |
|---|---|
| Pre-registration (frozen `add2c788`) | `docs/campaigns/T-family/T18_PREREGISTRATION.md` |
| Gate artifact (the registered grade) | `verification/runs/T-family/T18_runs/gate_t18.json` |
| Grade stdout log | `verification/runs/T-family/T18_runs/T18_GRADE_OUTPUT_20260831T151113Z.txt` |
| Verdict-readiness audit (`a368b35b`) | `verification/runs/T-family/T18_runs/T18_VERDICT_READINESS_AUDIT.md` |
| Selftest incident record | `verification/runs/T-family/T18_runs/T18_SELFTEST_INCIDENT_RECORD.md` |
| Registered bands and references | `verification/runs/T-family/T18_runs/T18_registered.json` |
| Comparator / referent / builder / marker / launcher | `verification/runs/T-family/T18_runs/{analyse,exact,build,mark_done}_t18.py`, `run_one_t18.sh` |
| Per-case completion and cost records | `verification/runs/T-family/T18_runs/STATUS.T18_CU_{c,m,f,f_CT}` |
| Run trees | `verification/runs/T-family/T18_runs/T18_CU_{c,m,f,f_CT}/` |
