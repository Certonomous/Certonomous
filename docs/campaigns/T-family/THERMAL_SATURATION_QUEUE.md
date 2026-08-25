# THERMAL SATURATION QUEUE — what else can start, ranked and costed

**Written 2026-08-25 by a heat-transfer lane, for the heat-transfer supervisor,
under Sanaa's 2026-08-25 saturation ruling (80–90 % of 16 cores held at all
times; small single-core cases in parallel batches of 8–12; per-case cap and
contention file kept; measured contention of 5–11 % acceptable **and
disclosed**; gate runs needing clean timing may reserve cores and say so;
memory guard enforced).**

**This lane launched nothing.** No solver, no mesh, no `blockMesh`, no
comparator. Zero core-minutes were spent producing this document. Every launch
decision below is the supervisor's.

**Verdict vocabulary is CLAUDE.md rule 1 only.** Where this lane does not know,
it writes **VERIFY** rather than guessing.

---

## 0. THE HEADLINE, BEFORE THE DETAIL

**Bucket A is almost empty, and that is the finding.**

Sweeping all five territory folders, **every committed pre-registration in the
T-family and the DC-cooling spine has already been fired, except K0d** — which
is already assigned to a separate lane. There is **no second committed
pre-registration with unrun compute anywhere in this team's territory.**

So the honest answer to *"what else can start"* is: **nothing else can start
tonight without either a commit or a document being written first.** The
supervisor's stated worry — that K0d's decay would open a gap discovered later
rather than scheduled from the start — is confirmed by measurement, and the gap
is **larger and earlier** than K0d's own §9.3 decay table implies, because
nothing in this team's queue is currently in a state to backfill it.

**The single fastest route out is T8.** `T8_PREREGISTRATION.md` is written,
complete, and frozen in prose — cases, cells, ladder, criteria, bands, cost,
cap, timeouts, controls, planted zero, exit-code contract — and it is **NOT
COMMITTED**. It is one instrument and one commit away from Bucket A, and it
delivers exactly the shape the schedule needs: **three single-rank cases, one of
them a 4.8-hour long pole.** It is also **DC spine position 3**.

---

## 1. LIVE BOX STATE, RE-DERIVED (2026-08-25 19:05–19:12 Z)

| item | measurement |
|---|---:|
| cores | **16** |
| load average (1 / 5 / 15 min) | **8.68 / 8.98 / 9.22** |
| `MemAvailable` | **18.1 GiB** |
| steady solver processes at ≥ 95 % CPU | **7** |
| — heat-transfer: `buoyantBoussinesqSimpleFoam` ×3 | pids 2203927 / 2203944 / 2203947 |
| — dafoam: `d4_opt_runScript.py … IPOPT` ×4 | pids 2359929–2359932, docker `--cpuset-cpus=5,6,7,9` |
| bursty, not steady | cfd `blockMesh`/`checkMesh` in `verification/runs/F1_MESH_TRIALS_2026-08-25/v2_m{1,2,4}` |
| steady occupancy | **7 / 16 = 43.8 %** |

**The three heat-transfer processes are the T1b L4 EXT2 arms**, running under
`T1b_L4_EXT2_PREREGISTRATION.md` (committed blob
`9d4beec421f1485ed4f7c400be8554191d23528f`), writing `log.solve.ext1` in
`verification/runs/T-family/T1_runs/R_{10k,100k,300k}_x`. Registered caps
1 100 / 1 300 / 2 750 core-min at `ranks = 1`, enforced as `timeout` 66 000 /
78 000 / 165 000 s. Elapsed at this reading **9 141 s**. **These three cores are
stable background for the next ~15–45 hours** and are not available for
backfill.

**Disclosure of what this team takes from other teams.** dafoam's four cores are
pinned to `cpuset 5,6,7,9` and are not touched. cfd's `F1` mesh trials are
bursty and single-core; **one core is left unallocated for them** in every batch
below. ansys-verification showed **no live solver** in this window — VERIFY
before launch, because their solvers are intermittent and a `ps` sweep is blind
to fleet agents (L-41).

---

## 2. A REGISTERED ARITHMETIC THAT HAS MOVED SINCE IT WAS WRITTEN

`K0d_REREGISTRATION.md` §9.1 registers **concurrency cap 9** and justifies it:

> Measured on this box at **2026-08-25T18:07Z**: 16 cores, five processes at
> ≥ 95 % CPU. **`5 + 9 = 14` of 16 = 87.5 %**, inside Sanaa's 80–90 % saturation
> band, leaving 2 cores for the session, git and the instruments.

**At 19:05Z the background is 7, not 5.** `7 + 9 = 16 of 16 = 100 %` — **above
Sanaa's band, and with none of the 2-core reserve §9.1 registered for the
session, git and the instruments.** The four dafoam IPOPT ranks are the
difference; they were not live at 18:07Z.

**This moves no gate, band, threshold, cap or label, and it is not an amendment
to a frozen document.** `9` is a **cap, not a floor**: launching fewer than nine
concurrently is inside the registration. **The registration-respecting fix is to
stage the batch** — §4 below does exactly that and lands on **14 of 16 = 87.5 %,
K0d's own registered figure.** The launch call is the supervisor's.

---

## 3. THE BUCKETS

### BUCKET A — READY TO FIRE NOW (committed pre-registration, case buildable, nothing blocking)

| rung | pre-registration | committed blob (sha) | cases | cells | endTime | **ranks** | POINT core-min | registered cap | `timeout = cap×60÷ranks` |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **K0d** | `docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md` | **`36b302f112a8f0bc2c779a8dcc1180a76b2e089e`** — verified byte-identical to the working tree by direct comparison against the HEAD blob, not by `git diff` | **9** | see below | 40 000 its | **1** (§7, serial, `nProcs = 1`, all nine) | **829.36** total | **2 484.84** total | per-case, §8.1 |

**K0d per-case lines, as registered:**

| case | cells | POINT core-min | 10× POINT cap (core-min) | enforced `timeout` (s) |
|---|---:|---:|---:|---:|
| `M1_c` | 25 600 | 43.50 | 435.00 | 26 100 |
| `M2_c` | 25 600 | 43.50 | 435.00 | 26 100 |
| `C_lam` | 50 176 | 63.95 *(registered ESTIMATE, not a measurement)* | 639.50 | 38 370 |
| `M1_m` | 50 176 | 85.27 | 852.70 | 51 161 |
| `M2_m` | 50 176 | 85.27 | 852.70 | 51 161 |
| `B_hi` | 50 176 | 85.27 | 852.70 | 51 161 |
| `I_hi` | 50 176 | 85.27 | 852.70 | 51 161 |
| `M1_f` | 98 596 | 167.55 | 1 675.50 | 100 530 |
| `M2_f` | 98 596 | 167.55 | 1 675.50 | 100 530 |

**The total rung cap of 2 484.84 core-min binds before the 10× per-case
threshold on every case except the two coarse ones.** Both are in force;
whichever is reached first stops the run.

**K0d's ceiling is on its own face and is not softened here.** §0: *"AS
REGISTERED, THIS RUNG CANNOT REACH A GRADED VERDICT."* Blay, Mergui & Niculae
(1992) is **NOT OBTAINED**; the tally stands at **0 of 10** graded rows; what
firing produces is solves and physics-stage instruments — convergence, achieved
`y⁺`, the five guards, the Roache triples, the discrimination control — **not a
gate.** Under the tiering directive that means K0d can earn **V** and **G** and
**cannot earn P**, and therefore **cannot be tiered `HOLDS`.**

**Bucket A contains exactly one rung, and it is already assigned.**

---

### BUCKET B — NEEDS A PRE-REGISTRATION (or a commit) FIRST — cheap prose, real compute behind it

Ranked by *how fast the document could reach a committed state* × *what it
unblocks on the DC spine (H-2: T3 → T5 → T8 → T12 → K2)*.

#### B-1. **T8 — MTT pure-plume entry rung. SPINE POSITION 3. RANK 1 BY A WIDE MARGIN.**

**State: written, complete, frozen in prose, NOT COMMITTED.**
`docs/campaigns/T-family/T8_PREREGISTRATION.md` is not in HEAD — checked with
`git cat-file -e HEAD:<path>`, which fails. It therefore **cannot be Bucket A**,
and no compute may touch it (CLAUDE.md rule 2).

Everything else about it is ready:

| item | value |
|---|---|
| cases | `T8_MTT_c`, `T8_MTT_m`, `T8_MTT_f` at `verification/runs/T-family/T8_runs/` |
| cells | **6 400 / 25 600 / 102 400**, `r = 2` exactly in both directions, no grading anywhere |
| `endTime` (iterations) | **8 000 / 12 000 / 20 000** |
| **ranks** | **1** — §6, R5, serial, no `decomposeParDict`, no `decomposePar`, invoked directly not through `mpirun` |
| POINT core-min | **7.13 / 42.81 / 285.40 = 335.34 total** |
| registered cap | **15 / 80 / 500 = 595 core-min** (9.92 core-h, **$0.509 derived, not measured**) |
| **`timeout = cap×60÷ranks`** | **900 s / 4 800 s / 30 000 s** |
| memory (at K0d's measured 2.4 kB/cell + ~60 MB baseline) | ~75 / ~121 / ~306 MB, **~0.50 GB for all three** |
| solver / closure | `buoyantBoussinesqSimpleFoam`, OpenFOAM v2606, `kEpsilon`, `Prt = 0.85` |
| reference tier | **partial EXACT** — Morton–Taylor–Turner plume theory is closed form; **no acquisition step** |

**THE ONE BLOCKER, NAMED AND SIZED.** §11 registers a four-path freeze set. Three
exist on disk; **`verification/runs/T-family/T8_runs/analyse_t8.py` does not
exist anywhere on this box** — a `find /` for it returns nothing. The document's
own freeze condition (line 12) asserts *"that tree holds `build_t8.py`,
`analyse_t8.py` and `run_one_t8.sh`"*, and §11 fixes `analyse_t8.py` as **"the
comparator — the grading path, fixed at this commit."**

**This is not a defect requiring an amendment, because the document is not yet
committed and therefore not yet frozen by sha.** Under rule 2 the pre-compute
state is still open. **Writing `analyse_t8.py` and committing it in the same
commit as the pre-registration makes the freeze statement true at the moment it
becomes binding.** Committing the document without the comparator would freeze a
false condition and fix a grading path onto a file that does not exist.

**What `analyse_t8.py` must carry, extracted from the frozen text so a lane can
be dispatched without re-reading all 12 sections:**

- **§9 — the planted zero (rule 3, "non-negotiable").** Copy the **fine** level's
  `endTime` `T` field to a temporary case; add **`PLANT = 1.234e-03 K`** to every
  cell in the **two axis-adjacent radial columns at every axial level, in the
  copy on disk**; read it back; **refuse** if the reader cannot see it.
- **§7 — strict completion (rule 4), per level, before the level is read at
  all.** `rc = 0` **recorded to a `STATUS` file, not inferred from the log**; an
  `End` line in `log.solve`; **last time == `endTime`**; fields
  **`T U p_rgh alphat nut k epsilon`** present at `endTime` — **`epsilon`, not
  `omega`**; `ExecutionTime` line count == `endTime`; **age guard** — every one
  of those fields at `endTime` newer than the case's own `0/T`.
- **§7 — criteria in this order, no other order permitted.** (1) all three levels
  iteratively converged to ≤ 1e-6 last-two-checkpoint relative change **and
  plateaued**, else `NOT A RESULT`; (2) triple `CONVERGING`, else `NOT A RESULT`
  with both triples (`e21`, `e32`), the observed order and the ratio printed
  beside it; (3) **`PASS` if the FINE-LEVEL value is inside its §4 band, else
  `GATE FAIL`** (ruling R1).
- **R1 / §12 S5 — the Richardson extrapolate is PRINTED, never gated on**, and
  the correct form is **`f_fine − e21/den`**. The prereg records that
  `analyse_t3.py:384` and `analyse_t1c.py:337` both compute the **inverted**
  form `f_fine + e21/den`, survivable only because it is display-only there.
  **`analyse_t8.py` must NOT import it**, and **`--selftest` must assert the
  correct sign against a closed-form case.**
- **R2(b) — deviation and band-utilisation fraction printed for every exponent**,
  not just the verdict. GCI at **`Fs = 1.25`** printed either way; **no GCI when
  the three values are not monotone.**
- **§12 S6 — exit-code contract, answering D522**: a comparator must not exit 0
  on a rung with zero graded rows.
- **§8 — a level killed by its cap is `PENDING`, a right-censored measurement,
  never `GATE FAIL`.**

`run_one_t8.sh` was inspected and is **complete and correct**: it refuses if
`0/` or any time directory exists, creates `0/` from `0.orig/` and **touches
`0/T` last** so the age guard dates the run, carries the three registered
timeouts as literals with the `cap_core_min × 60 ÷ ranks` identity in a comment,
writes `STATUS.T8_MTT_<level>`, and every step carries an explicit
`|| { echo ABORT…; exit 1; }` rather than relying on `set -e`. `build_t8.py`
exists (19 014 B). **No case directory of any kind exists in the registered
tree** — `T8_runs/` holds only those two scripts — so the freeze condition's
"zero core-minutes have been spent on this rung" is **true as measured**.

**Registered misprediction risk, carried forward (R6):** the rate
`1.196e5 cell·steps/(core·s)` is borrowed from `K2bU3_L025`, a **transient
PIMPLE** case, while T8 is a **steady SIMPLE-family** run. The arithmetic is
exact; **the rate is the exposure.** The direction of the error is not
predicted. This must be attributed as **misprediction** in the
`docs/COST_CALIBRATION.md` row, never absorbed.

**Estimated time to Bucket A: one lane-shift to write and self-test
`analyse_t8.py`, plus one private-index commit.**

#### B-2. **T3 fourth mesh level (`R_m`, `R_f`, `R_ff`) — SPINE POSITION 1, the spine's binding item.**

**PROPOSED and NOT RUN.** `T3_RESULTS.md` §14 and `T3_EXT1_AMENDMENT.md` §15
register it as T3's response and state it **needs its own costed
pre-registration**; rough bound **150–200 core-h (9 000–12 000 core-min), USD
8–10 derived**.

**Why it is the right response, stated so the supervisor need not reconstruct
it:** T3 is `NOT A RESULT` 4/4 at **gate (1) alone** of prereg §7.1. `R_m` and
`R_f` are iteratively CONVERGED (9.7e−08, 7.8e−08). It is **`R_c`** that stops
the ladder, sitting in a limit cycle at the 80 000-iteration cap — an outcome
§11 registered in advance as one the rung reports rather than averages. A fourth
level moves the graded triple **up** the ladder so the limit-cycling coarse level
drops out of it. G2 `x_peak/H` already returns a **CONVERGING** triple
(`p` 4.304, GCI 0.019 %) and is `NOT A RESULT` anyway because gate (1) fires
before a triple is consulted.

**Highest core-minute sink available to this team, and the only Bucket B item
large enough to hold cores for days rather than hours.** Rank 2 by spine value;
rank 3 by speed — the prereg is real work, and the cost bound is 15–20× T8's.

**Ceiling: even a CONVERGING triple leaves T3 unable to reach P.** Vogel & Eaton
(1985) is **NOT OBTAINED** (ASME closed; every open archive checked and named in
`T3_PREREGISTRATION.md` §2). Gate (3) is further downstream after ext1 than it
was before it.

#### B-3. **T5 — heated cubes, the rack physic. SPINE POSITION 2.**

`T5_PREREGISTRATION_DRAFT.md` is committed as a **draft** (blob
`d56018d18fef1ed4cedefdf54da19631026c98b3`) and therefore **not a
pre-registration**. Its line 5 states it *"freezes on Sanaa's reading **or on
the supervisor's promotion of this file**"* — **so this is not Sanaa-blocked;
the supervisor can promote it.** Twelve items are labelled `INTERPRETATION n`
in place and collected in §13.

**Primary HELD and rule-15 verified**: Meinders 1998 TU Delft thesis, sha256
`36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb`, **title page
VERIFIED BY EYE 2026-08-25** by rendering pages (the PDF has no text layer), and
the sidecar was **OCR-remediated the same day from 0 to 501 467 non-whitespace
characters** — `docs/papers/forced_convection_heat_transfer/SIDECAR_VERIFICATION_2026-08-25.md`.
Stated uncertainty 5 % mid-face / 10 % edges in local `h`. **No data appendix** —
every graded row must be **digitised** from figures, and the §10 digitiser keys
on the **printed caption on the page**, never a text cross-reference.

**Not a saturation-band backfill.** §11 registers **`nProcs = 4`** for `C`, `M`
and the arms and **`nProcs = 8` for `F`** — three grid levels at
**5.4e4 / 2.2e5 / 9.0e5 cells**, cost **USD 3.72–7.16** under two rate models,
predicted wall on the critical path 4.8 h (Model B) to 13.2 h (Model A) on 8
ranks. **This is a reserve-and-say-so rung, not a batch filler** — see §5.

#### B-4. **T11 entry arm — lumped and 1D transient conjugate, EXACT.**

**No document of any kind exists.** There is no `T11_*` file in the campaign
folder. But `T_FAMILY_INDEX.md` classifies it **partial EXACT**: the lumped and
1D transient solutions are **closed form**, so an entry rung can be built with
**no acquisition step** — the same shape as T1c, which graded a rung the whole
class was recorded as blocked on, and the same shape as T8's MTT arm.

**Cheapest new compute on the board and the fastest new prereg to write**, because
its reference cannot be argued with. Rank 4 by spine value (it is H-5 position 7),
**rank 2 by speed.** Worth starting in parallel with T8 precisely because the
schedule in §4 runs out of committed compute at t ≈ 85 min.

#### B-5. **T4 — impinging jet, the band-containment flagship. H-5 position 1.**

**Partially armable, which the index does not say plainly.** ERCOFTAC case025 is
held at `docs/campaigns/T-family/reference-data/ercoftac_case025/` (88 files
including 4 Nusselt tables, `Re` 23k/70k, `H/D` 2/6, one mislabeled header
noted), and the Martin correlation with its stated validity comes from
`narumanchi_hassani_bharathan_2005_nrel_tp540_38787.pdf` — **title page VERIFIED
2026-08-25**, sidecar proven byte-identical to a fresh `pdftotext -layout`
regeneration with 71 form-feeds against pdfinfo's 71 pages.

**The split:** the **flow-field** rows have stated uncertainties in case025 and
**can be graded**. The **`Nu` rows cannot** — the 2.4 % `Nu` uncertainty is
**second-hand**, a KB Wiki quoting Baughn & Shimizu, and the ASME primaries are
closed. So T4's `Nu` rows are report-only and **cannot reach P**; its flow rows
can. Charter §2e requires `Nu_stag` to be classified **forcing-class** in the
pre-registration.

#### B-6. **T12 — room-scale ventilation. SPINE POSITION 4. HIGHEST-VALUE ZERO-COMPUTE ACTION ON THE BOARD.**

`T_FAMILY_INDEX.md` records T12 as **ACQUIRE, over $25**. **That may be stale.**
`docs/papers/data_center_indoor_airflow/nielsen_rong_olmedo_2010_clima_annex20.pdf`
is on disk with a sidecar whose printed front matter reads:

> *The IEA Annex 20 Two-Dimensional Benchmark Test for CFD Predictions* —
> Peter V. Nielsen, Li Rong and Inés Olmedo, ISBN 978-975-6907-14-6, Clima 2010,
> 10th REHVA World Congress … *"Laser-Doppler measurements and hot-wire
> measurements are given for comparison with the obtained CFD predictions both
> for isothermal flow and for nonisothermal flow."*

**It carries NO rule-15 title-page verification record**, and rule 15 is
explicit that a paper counts as obtained **only on title-page verification,
never by filename or hash**. The only two title-page verification records in
this repository are `PAPER_INTAKE_2026-08-24.md` and
`SIDECAR_VERIFICATION_2026-08-25.md`, both covering the three
`forced_convection_heat_transfer` PDFs. **So this document is NOT OBTAINED under
rule 15 as things stand — not because it is absent, but because nobody has
opened its title page on the record.**

**Cost to settle: zero core-minutes and one reading.** If the title page
verifies and the paper carries the isothermal data with stated uncertainties,
**spine position 4 moves from ACQUIRE to armable.** Schwenke (1975) remains
`NOT OBTAINED` and would still block the **nonisothermal** case specifically.

**Rank 1 among zero-compute actions.** It costs nothing, it cannot fail
expensively, and it is on the spine.

#### B-7. **T1a / K0e — forced-convection flat plate. A BAND-ARMING BLOCK, NOT A MISSING PAPER.**

`K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` is `BLOCKED` **by construction**:
*no band can be honestly derived from a single correlation* — a source that
states a fit without stating its own uncertainty arms nothing, and setting the
band to the deviation models happen to show would be setting the band to the
answer.

**A candidate unblock is already on disk and is named here rather than acted
on.** `bahrami_2005_nasa_tm_212841.pdf` (title page **VERIFIED**, sha256
`0cd29adb…`) states eq. (1) `St = 0.0296 Re^-0.2 (Pr Tw/T∞)^-0.4` **and plots it
against the Von Karman analogy** (sidecar lines 401, 614, 876, 1039). **Two
published correlations for the same quantity** is exactly T1b's mechanism —
their disagreement is a **measured** band rather than a chosen one, computable
before any case is solved.

**This lane does not claim the band is armed.** `THERMAL_CAPABILITY_STATE.md`
addendum 2 registers the **circularity caution**: eq. (1) is Colburn-type and
sits in the same family as the Reynolds and Von Karman analogies, and the
Reynolds analogy is close to what a constant-`Prt` gradient-diffusion closure
asserts — so agreement is **partly structural rather than evidential**, with
`Pr^-0.4` against `Pr^-2/3` the only genuinely testing part of the gap. **Two
correlations from inside one analogy family may not be independent enough to arm
a band, and that is a supervisor's ruling, not a lane's.** Recorded as a
candidate, `VERIFY`.

#### B-8. **E4 third arm.** `E4a_RESULTS.md` and `E4a2_RESULTS.md` both return
**NOT A RESULT** (E4a2's predecessor prereg frozen at `628e29c4`). A third arm
would need a new pre-registration. **Off the spine, off H-5.** Lowest rank in
Bucket B; listed so the census is not flattered by omission.

---

### BUCKET C — GENUINELY BLOCKED

The supervisor asked specifically for every rung with **K0d's shape: a gate that
cannot reach P because its primary is not on disk.** They are enumerated here
with the blocker named and the exact unblock stated.

| rung | blocker | reachable | what would unblock it |
|---|---|---|---|
| **K0d** | **Blay, Mergui & Niculae (1992) `NOT OBTAINED`** — §0 states the ceiling on the document's own face, tally **0 of 10** | **V yes, G yes, P NO → cannot be `HOLDS`** | the primary. **Two secondaries are on disk and are named, not proposed**: `oulghelou_beghein_allery_2020_2009.06724.txt` line 727 (*"Comparison between the numerical results (CFD) and the experimental results (Exp Blay et al.)"*, ref [31] is Blay 1992) and `kayne_agarwal_2013_mixed_convection.txt` line 330 / ref [8]. A digitised secondary is **one tier below a primary and is REPORT-ONLY — it can never supply P.** Acquiring the primary is a **send** and is Sanaa's alone (rule 7) |
| **T3** | **Vogel & Eaton (1985) `NOT OBTAINED`** (ASME closed) | **P NO** | the primary. **Not today's binding constraint** — gate (1) fires ahead of gate (3); the ladder stops the rung first. Smirnov 2016 (CC-BY) is digitised as a **REPORT-ONLY** referent |
| **T7** | **generalises K0d and inherits Blay** | **P NO** | Blay 1992. Also flagged in the index as *"aggregate may exceed $25"* |
| **T2** | **the Zukauskas correlation's stated validity range is nowhere on disk.** A `grep -rliE 'Zukauskas'` and `'tube bank'` across all 45 sidecars returns **zero** hits for Zukauskas and one incidental hit for "tube bank" (inside the Meinders thesis) | **P NO as registered** | the index requires *"the correlation's stated validity range cited, not just its algebra."* **Algebra without a stated range arms no band** — the same defect that blocks K0e. This rung is mis-tiered in the index as **FORMULA**: it behaves as **ACQUIRE** until a source stating the range is obtained **and title-page verified** |
| **T6** | **3–4 decades of Rayleigh–Bénard `Nu`–`Ra` scaling data.** A sidecar sweep for `Rayleigh-B`, `Rayleigh–B` and `Nusselt.*Rayleigh.*scaling` returns **zero** hits | **P NO** | published scaling data. Also **transient and far over $25** — a cost block on top of the reference block |
| **T9b / T9c** | conjugate flat plate / conjugate cube reference data — none identified on disk | **P NO** | conjugate data. `T9aD_RESULTS.md` already registered **`Gauss harmonic`** for the conjugate ladder (D454, L-227), so the *numerics* entry is prepared; the *reference* is not. T9c is 3D and **likely over $25** |
| **T10b** | combined convection + radiation data — none identified | **P NO** | combined-mode data |
| **T12** | **Schwenke (1975) `NOT OBTAINED`** for the Annex 20 **nonisothermal** case | **nonisothermal P NO; isothermal `VERIFY`** | see **B-6** — the isothermal case may already be armable from Nielsen/Rong/Olmedo 2010, pending a rule-15 title-page verification that has never been done |
| **T1a / K0e** | **not a missing paper** — Bahrami 2005 is held and verified. **A single correlation cannot arm a band** | **P NO as registered** | see **B-7**: a second independent correlation, subject to the circularity caution |
| **K2a rack row module** | **awaiting Sanaa's approval** (`LAB_STATE.md`) | — | her word. Not a lab call |
| **T13 rack row** | **inherits everything above it**; unplaced — not in the spine, not in the H-5 order | — | the rungs above it. **Far over $25** |

**A cross-cutting rule-15 exposure, reported and not resolved.** Only **three**
PDFs in this repository carry a title-page verification record on disk, all
three in `forced_convection_heat_transfer`. **Ampofo & Karayiannis 2003, Betts &
Bokhari / ERCOFTAC Case 079, and Nielsen/Rong/Olmedo 2010 carry none** that this
lane could find. Their status is recorded in campaign prose (`READ IN FULL`,
`primary data files, 22 kept`) which may well be sufficient evidence obtained by
another route. **This lane did not check that and does not assert a defect:
`VERIFY`.** It matters because every P column in this family rests on it.

---

## 4. THE SCHEDULE — a concrete batch plan for 80–90 % of 16 cores

**Assumptions stated so they can be checked:** background holds at **7 steady
cores** (3 T1b EXT2 + 4 dafoam IPOPT); **1 core is left unallocated** for cfd's
`F1` mesh bursts and this session's git and instruments; K0d retirement times are
its own registered §9.3 POINT-rate table; T8 durations are its §8 POINT lines at
`ranks = 1`, so **core-minutes and wall-minutes coincide numerically**.

| batch | t (min) | what changes | heat-transfer cases live | **cores busy / 16** | **utilisation** | memory added |
|---|---:|---|---|---:|---:|---:|
| **B0** | **0** | fire **7 of K0d's 9** — `M1_c`, `M2_c`, `C_lam`, `M1_m`, `M2_m`, `B_hi`, `I_hi`. **Hold `M1_f`, `M2_f`.** | 3 EXT2 + 7 K0d | **14** | **87.5 %** | ~1.05 GB est / ~1.4 GB bound |
| **B1** | **~43.5** | `M1_c`, `M2_c` retire (−2) → release the two held L3 cases **`M1_f`, `M2_f`** | 3 EXT2 + 7 K0d | **14** | **87.5 %** | +0.53 GB |
| **B2** | **~64** | `C_lam` retires (−1) → start **`T8_MTT_f`** (the long pole: 285.40 core-min POINT, cap 500, `timeout` 30 000 s) | 3 EXT2 + 6 K0d + 1 T8 | **14** | **87.5 %** | +0.31 GB |
| **B3** | **~85** | `M1_m`, `M2_m`, `B_hi`, `I_hi` retire (−4) → start **`T8_MTT_m`** (42.81 core-min, `timeout` 4 800 s) and **`T8_MTT_c`** (7.13 core-min, `timeout` 900 s) | 3 EXT2 + 2 K0d + 3 T8 | **12** | **75.0 %** | +0.20 GB |
| **B4** | **~92** | `T8_MTT_c` retires (−1) | 3 EXT2 + 2 K0d + 2 T8 | **11** | **68.8 %** | — |
| **B5** | **~128** | `T8_MTT_m` retires (−1) | 3 EXT2 + 2 K0d + 1 T8 | **10** | **62.5 %** | — |
| **B6** | **~168** | `M1_f`, `M2_f` retire (−2) | 3 EXT2 + 1 T8 | **8** | **50.0 %** | — |
| **B7** | **~349** | `T8_MTT_f` retires (−1) | 3 EXT2 | **7** | **43.8 %** | — |

**Peak memory across the plan: ~2.1 GB of heat-transfer solver RSS on top of the
current 18.1 GiB `MemAvailable`**, leaving `MemAvailable` around **16 GiB** —
comfortably above this family's **standing 12 GiB floor** (`LAB_STATE.md:1871`).
K0d §9.2's registered drop rule (*if `MemAvailable` is under 14 GiB at launch,
drop to the seven non-L3 cases*) is **already satisfied by B0's staging**, which
launches exactly those seven. **Re-read `MemAvailable` immediately before B1**,
because the binding memory risk is not this team: dafoam's container is capped at
`--memory=12g` and a second such job would make the floor the constraint rather
than the cores.

### 4.1 THE GAP, STATED PLAINLY

**The band holds only to t ≈ 85 min. From B3 onward this team runs out of
committed compute and utilisation falls to 75 %, then 69 %, then 63 %, then
50 %.** Even with T8 committed and fired, **K0d + T8 together cannot hold
80–90 % beyond the first ninety minutes.** T8 buys the band an extra ~21 minutes
at 87.5 % and then keeps one core warm for another four hours — it is a long
pole, not a wide one.

**Closing B3–B7 needs Bucket B prose started NOW, in parallel with the runs,
not after them.** In priority order, and this is the whole recommendation:

1. **`analyse_t8.py` + the T8 commit** — turns B-1 into Bucket A and makes B2/B3
   real rather than hypothetical.
2. **The T3 fourth-mesh-level pre-registration** — the only item in this team's
   inventory large enough to hold 2–3 cores for days (9 000–12 000 core-min), and
   it is spine position 1.
3. **Promote `T5_PREREGISTRATION_DRAFT.md`** — the supervisor may do this; §11's
   `nProcs = 4`/`8` arms are the natural successor load once K0d's single-core
   batch has drained.
4. **A T11 EXACT entry-rung pre-registration** — cheapest new compute on the
   board, no acquisition step, and it can be written while the above run.
5. **The T12 rule-15 title-page verification of Nielsen/Rong/Olmedo 2010** — zero
   compute, cannot fail expensively, and it is on the spine.

**If B-1 is not committed, delete T8 from the table above.** Then the band holds
to t ≈ 43.5 min at 87.5 %, drops to 81 % at t ≈ 64 min, and is at **62.5 % from
t ≈ 85 min** — which is exactly the mean K0d's own §9.3 registered and called
*"BELOW Sanaa's 80–90 % band. K0d ALONE CANNOT HOLD THAT BAND FOR ITS OWN
WINDOW."*

### 4.2 CONTENTION, DISCLOSED

At Sanaa's disclosed-acceptable **5–11 %**, K0d's solver subtotal inflates from
827.11 to **868.5–918.1 core-min = 35–37 % of the 2 484.84 CEILING**, absorbed
with a wide margin (§9.4). **A per-case contention file is kept** and contention
is **named separately at completion, never absorbed into the actual/predicted
ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

For T8, contention interacts with the cap instrument and the interaction is
worth stating because it is not obvious: **§8's cap is enforced as a wall-clock
`timeout`, admissible only because `ranks = 1` makes core-minutes and wall
seconds coincide.** Under contention **wall inflates and core-minutes do not**,
so a heavily contended case can be killed by its timeout while still under its
core-minute cap. **T8_MTT_f has margin:** 285.40 POINT × 1.11 (11 % contention)
= 316.8 core-min → 19 008 s against a **30 000 s** timeout — **1.58× of headroom
remaining.** It tolerates roughly **1.75× wall inflation** before the timeout
bites. **No core reservation is needed for T8 at the disclosed contention band.**

### 4.3 RUNGS NEEDING CLEAN TIMING — RESERVE CORES AND SAY SO

- **Nothing in Bucket A needs reserved cores.** K0d and T8 are both `ranks = 1`
  with per-case contention files and generous cap headroom.
- **T5 does, when it runs.** Its §11 cost model assumes **parallel efficiency
  0.85 on 4 ranks (`scotch`)** and `nProcs = 8` for the fine level. **That 0.85
  is an assumption, not a measurement**, and measuring it under 5–11 % contention
  measures contention rather than parallel efficiency. **When T5 fires, it should
  reserve its ranks and say so in its cost registration**, or register explicitly
  that the efficiency figure is unmeasurable in that window.
- **Any future rung whose cap instrument is wall-clock at `ranks > 1`** inherits
  the §4.2 hazard **without** the numerical coincidence that makes it admissible
  at one rank. `timeout = cap_core_min × 60 ÷ ranks` must be coded as that
  identity, never as a copied literal.

---

## 5. WHAT THIS LANE COULD NOT VERIFY

- **ansys-verification's live core usage.** No solver of theirs appeared in the
  19:05–19:12 Z window; a `ps` sweep is blind to fleet agents (L-41) and their
  solvers are intermittent. **`VERIFY` before B0** — every core taken in B0
  assumes their occupancy is zero right now, and if it is not, B0 overshoots.
- **Whether Ampofo & Karayiannis 2003, Betts & Bokhari / ERCOFTAC 079 and
  Nielsen 2010 satisfy rule 15 by some record this lane did not find.** Stated as
  `VERIFY`, not as a defect.
- **Whether the two Blay secondaries carry digitisable tabulated values or only
  plotted curves.** The sidecars show figure captions comparing CFD to
  *"Exp Blay et al."*; this lane did not open the figures. Either way they are
  **REPORT-ONLY** and cannot supply P.
- **Whether B-7's two flat-plate correlations are independent enough to arm a
  band.** That is a supervisor's ruling under the registered circularity caution.
- **The K0d retirement times in §4** are its **registered POINT-rate
  expectations**, not measurements — no K0d case has ever run. Under the CEILING
  rate (2× POINT) every batch boundary in §4 doubles, which **helps** the band by
  stretching the window; it does not change the shape of the gap.

---

## 6. WHAT THIS DOCUMENT DOES NOT DO

- **It launches nothing and authorises nothing.** Every launch decision is the
  supervisor's.
- **It creates, moves and retires no gate, threshold, band, cap or label.**
- **It edits no frozen document.** The `K0d_REREGISTRATION.md` §9.1 background
  arithmetic in §2 above is reported as measured today, **beside** the frozen
  text, not in place of it. Whether that warrants a dated amendment is the
  supervisor's call, not this lane's.
- **It sends nothing. SUBMISSIONS REMAIN PARKED** (rule 7). Acquiring Blay 1992,
  Vogel & Eaton 1985, Schwenke 1975 or the Baughn & Shimizu ASME primaries would
  be a **send**, and sending is Sanaa's alone.
