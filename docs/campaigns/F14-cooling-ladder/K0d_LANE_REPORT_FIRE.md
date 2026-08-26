# K0d FIRE LANE REPORT — THE RUNG DID NOT FIRE, ON TWO INDEPENDENT STOPS

**Verdict: `BLOCKED`.** Zero core-minutes spent. Nothing was built, meshed,
launched or graded. `verification/runs/F14-cooling-ladder/K0d_runs/` **still does
not exist**, verified in this lane's own invocation under a planted control
(§2.1). **`AMENDMENT 2` WAS NOT WRITTEN** — §1 says why, and the reason is that
writing it would have required this lane to choose one of two numbers the
supervisor's ruling did not authorise it to choose between.

Written 2026-08-25T19:07Z by the heat-transfer lane dispatched to implement the
supervisor's four-part ruling and then fire. **Both stops were pre-committed by
the supervisor in the dispatching brief itself** — ruling part 2 ("if 12.00 does
not reproduce from the document, report the discrepancy and STOP; do not adjust
it to fit") and gate (a) ("If `build_k0d.py` or `analyse_k0d.py` is absent or
differs from its registered hash, STOP and report — do not write or repair a
comparator to make the fire possible"). **This lane exercised neither escape.**

**The two stops are independent.** Repairing either one alone still leaves the
other standing.

---

## 1. STOP 1 — THE `12.00` INSTRUMENTATION FIGURE DOES NOT REPRODUCE. THE DOCUMENT'S OWN RULE GIVES `11.50`.

### 1.1 The enumeration, taken from the frozen document and not from this lane

`K0d_REREGISTRATION.md` `AMENDMENT 1` §A1.4 (lines 806–812) enumerates the
instrument lines. Every figure below is the document's, quoted from that table:

| instrument line | registered value | source line |
| --- | ---: | --- |
| meshing + `checkMesh`, 5 core-s per case | 0.83 at ten cases, **bounded ≤ 2.00** | §A1.4 row 2 |
| `check_k0d_mesh.py`, three `polyMesh` reads | 0.50 (explicitly unchanged) | §A1.4 row 3 |
| `mark_done_k0d.py` + `analyse_k0d.py` + `--selftest` | 1.00 | §A1.4 row 4 |
| dual-scheme extraction (new, §A1.3b) | **≤ 8.00** | §A1.4 row 5 |

- **POINT instruments** = 0.83 + 0.50 + 1.00 + 8.00 = **10.33**
- **BOUNDED instruments** = 2.00 + 0.50 + 1.00 + 8.00 = **11.50**

**Neither is 12.00.**

### 1.2 The enumeration rule is the DOCUMENT'S rule, not this lane's reading — and that is demonstrated, not asserted

The obvious objection is that this lane has invented a way of adding the lines up.
It has not, and the frozen document contains its own control for exactly this.

§8's pre-amendment ceiling registers **"instruments, bounded | 3.50"** (line 425)
against a POINT instrument total of **2.25** (line 418, "meshing 0.75, mesh reader
0.50, comparators 1.00"). Applying the rule used above to the nine-case lines —
**meshing taken at its ≤ 2.00 bound, the other two lines unbounded** — gives
`2.00 + 0.50 + 1.00 =` **3.50**, which is the registered figure **exactly**.

**The rule reproduces the document's own prior bounded instrument figure to the
cent.** That is what makes `11.50` the document's answer at ten cases and `12.00`
an unsourced one. The gap is **+0.50 core-min**, and the only line that could
carry it — `check_k0d_mesh.py` at 0.50 — is the one line §A1.4 marks
**"unchanged"**, with a stated reason (`M1_m_seed` reuses L2's mesh).

### 1.3 What this lane did NOT do

**It did not adjust 12.00 to 11.50 and proceed**, and it did not proceed on 12.00
either. Both were available and both were refused:

- Substituting 11.50 would re-choose the supervisor's own ruled ceiling number.
  The ruling's part 1 **is** the figure 2,749.14; a lane that silently re-derives
  it to 2,748.64 has widened its own authority over the one quantity the ruling
  consisted of (standing rule 9 — *approval of an item is approval of ITS cap*).
- Proceeding on 12.00 would register a ceiling whose instrument component cannot
  be derived from the registration it claims to derive from. **On a rung whose
  stated purpose is to eliminate numbers chosen for comfort**, a 0.50 core-min
  unsourced addend is not too small to matter — it is the same defect at a size
  chosen for comfort, which is the reasoning §A1.1 already recorded against the
  `T_ref` alternative at 0.050 %.

### 1.4 All four arrangements, re-costed at every instrument figure, so the ruling can be re-made from arithmetic in one round trip

`S = 912.38`. Registered cap **2,484.84**. Structure `CEILING = 3S + I`.

| I | CEILING | vs cap | core-h | derived $ at $0.0513/core-h |
| ---: | ---: | ---: | ---: | ---: |
| **12.00** (the ruling's figure, **unsourced**) | 2 749.14 | +264.30 (+10.64 %) | 45.8190 | $2.3505 |
| **11.50** (the document's bounded rule) | **2 748.64** | **+263.80 (+10.62 %)** | 45.8107 | **$2.3501** |
| 10.33 (the document's POINT rule) | 2 747.47 | +262.63 (+10.57 %) | 45.7912 | $2.3491 |

**The choice between them moves the ceiling by 1.67 core-min out of ~2,748 —
0.061 %.** It changes no conclusion: every arrangement still exceeds the
registered cap by ~10.6 %, the derived cost stays ~$2.35, and that stays **9.4 %
of the $25 pre-authorisation**. **The supervisor's parts 1, 3 and 4 are
unaffected in substance.** What is affected is whether the number the amendment
registers is one a reader can re-derive from the document, and that is the whole
evidentiary content of a frozen figure.

**The other two arrangements the ruling refused are NOT re-costed here** and are
not offered as options: part 2 of the ruling refused both concessions, this lane
agrees with the reasoning, and re-tabling a refused lever is how a refusal gets
quietly reopened.

---

## 2. STOP 2 — GATE (a) FAILS AT THE FLOOR: `build_k0d.py` AND `analyse_k0d.py` DO NOT EXIST. NOWHERE.

### 2.1 Measured, under a planted control (standing rule 3)

The reader was shown able to return PRESENT before any ABSENT was believed. In
one invocation, `test -e` over seven paths returned:

| path | reader |
| --- | --- |
| `scripts/check_grader_self_blindness.py` | **PRESENT** — the plant |
| `verification/runs/F14-cooling-ladder/K0cS_runs` | **PRESENT** — the plant |
| `scripts/build_k0d.py` | **ABSENT** |
| `scripts/analyse_k0d.py` | **ABSENT** |
| `scripts/mark_done_k0d.py` | **ABSENT** |
| `scripts/check_k0d_mesh.py` | **ABSENT** |
| `verification/runs/F14-cooling-ladder/K0d_runs` | **ABSENT** |

A second reader — `find /home/ubuntu -xdev` over all four script names **plus the
plant name** — returned **the plant and nothing else**. A reader that finds the
plant and no `build_k0d*` anywhere under `/home/ubuntu` is a reader shown able to
see a non-zero.

**Third reader, independent of the disk:** `git ls-tree -r HEAD` (HEAD
`c90f9411`) over the whole tree, filtered on `k0d`, returns **seven `.md` files
and not one `.py`**. The scripts are not in HEAD, not in the working tree, and
not on the filesystem.

### 2.2 There is no "registered hash" to compare against, because the artifact was never written

§7.5 of `K0d_REREGISTRATION.md` (line 384) registers the grading path as
`check_k0d_mesh.py` → solve → `mark_done_k0d.py` → `analyse_k0d.py`, and binds
that **"every comparator is hashed against its committed blob before analysis
(Charter 2d); the grading path is fixed at this document's commit."**

**No blob was ever committed for any of the four.** The gate the supervisor set
— *absent, or differs from its registered hash* — fails on the **first** limb,
which is the more serious one: a hash mismatch is a drift to investigate, an
absence is a path that was registered and never built.

**This lane did not write them.** The brief forbids it — *"do not write or repair
a comparator to make the fire possible"* — and standing rule 2 is the deeper
reason: a comparator written by the lane that is under instruction to fire, after
the registration is frozen, is a grading path chosen with the run in view.

### 2.3 Consequence for gates (c) and (d)

Both are **untestable, not passed and not failed**:

- **(c)** the ten-marker refusal per §A1.2b cannot be exercised on a grader that
  does not exist. **Recorded as a live obligation on whoever writes it**: §7.5
  line 386 still reads **"all nine"**, and only §A1.2b (line 747) moves it to
  **ten**. A comparator author reading §7 alone would build the nine-marker
  refusal and be wrong.
- **(d)** the `ranks == 1` assertion has no launcher to sit in. The **conversion
  arithmetic** was checked against §8.1's frozen table instead — see §4.

---

## 3. THE STOPS ARE NOT THE ONLY REASON THE FULL RUNG COULD NOT HAVE FIRED TODAY

Reported because the supervisor asked for contention to be **re-read at fire
time and disclosed, not ignored** — and it has moved materially against the
registration.

**Measured 2026-08-25T19:07Z:** 16 cores; `loadavg` **9.97 / 9.28 / 9.34**;
`MemAvailable` **18 823 244 kB = 17.95 GiB**.

**Foreign processes at ≥ 99 % CPU — SEVEN, not the five §9.1 registered:**

| identity | pids | cores |
| --- | --- | ---: |
| T-family `buoyantBoussinesqSimpleFoam` | 2203927, 2203944, 2203947 | 3 |
| dafoam `d4_opt_runScript.py` IPOPT drivers | 2359929, 2359930, 2359931, 2359932 | 4 |
| **total sustained** | | **7** |

plus transient ansys-verification work (`locate_bad_faces.py`, pid 2422906,
observed at 308 % — bursty, not counted as sustained).

**§9.1 registered `5 + 9 = 14` of 16.** The live figure is **`7 + 10 = 17` of
16 — over subscription.** At the supervisor's ~14/16 instruction the largest
K0d batch that seats is **14 − 7 = 7 cases**, so the ten-case rung **could not
have launched whole today** even with the amendment written and the comparators
present. Under the brief that is a "launch the largest batch that fits and say
so" case, not a silent shrink — **but it is moot, because nothing launched.**

**Memory (gate f) is NOT the constraint:** 17.95 GiB available against §9.2's
~2.15 GiB conservative bound for all ten and this family's standing 12 GiB floor.
§9.2's own drop-to-seven trigger (`MemAvailable` under 14 GiB) **is not tripped**.

**No contention file was written**, because a contention file records a launch
and there was no launch.

---

## 4. EVERY GATE, WITH ITS MEASURED VALUE

| gate | what it required | measured | status |
| --- | --- | --- | --- |
| **ruling pt 1** | `K0d_runs` absent, proved by `test -e` under a planted control | **ABSENT**; plants `K0cS_runs` and `check_grader_self_blindness.py` both PRESENT | **PASS** — the pre-compute window of rule 2 is genuinely still open |
| **ruling pt 2** | `12.00` reproduces from §A1.4/§10.2 | **DOES NOT.** Document's rule gives **11.50** bounded / 10.33 point; rule validated by reproducing the frozen 3.50 exactly | **GATE FAIL → STOP 1** |
| **ruling pt 3** | `M1_m_seed` stays L2, stays in the rung | not altered by this lane | upheld, untouched |
| **ruling pt 4** | derived cost, `[lab-attributed]`, referral | arithmetic verified: 2 749.14/60 = 45.8190 core-h × $0.0513 = **$2.3505 DERIVED**, 9.40 % of $25 | arithmetic **PASS**; not written, blocked by STOP 1 |
| **(a)** | frozen build/grade scripts hash against committed blobs | **`build_k0d.py`, `analyse_k0d.py`, `mark_done_k0d.py`, `check_k0d_mesh.py` ALL ABSENT** on disk, in HEAD, and under `/home/ubuntu` | **GATE FAIL → STOP 2** |
| **(b)** | `check_grader_self_blindness.py` over `analyse_k0d.py` | tool's **`--selftest` PASSES** (both probes shown able to fire on planted defects and stay quiet on clean counterparts, **rc = 0**); on the target it **exits rc = 1, `FileNotFoundError`** | **untestable** — no grader to scan |
| **(c)** | grader refuses (exit 2) below TEN `DONE.<case>` | no grader exists | **untestable** |
| **(d)** | `timeout = cap × 60 ÷ ranks`, `ranks == 1` asserted in the launcher | no launcher exists. §8.1's frozen table re-derived: 3 of 4 rows exact, **one row off by 1 s** (see below) | **untestable**; one observation |
| **(e)** | contention re-read and disclosed | load **9.97**; **7** sustained foreign cores, not 5; `7 + 10 = 17 > 16` | **disclosed** — §3 |
| **(f)** | memory re-read | **17.95 GiB** available; §9.2 trigger not tripped | **PASS** |
| **(g)** | detached `setsid` launch | **NOT REACHED — nothing launched** | n/a |

**Gate (d) observation, reported and not repaired.** With `ranks = 1` the
conversion is the identity `× 60`. Against §8.1's frozen table:
`M1_c`/`M2_c` 435.00 → 26 100 s **exact**; `M1_f`/`M2_f` 1 675.50 → 100 530 s
**exact**; `C_lam` 639.50 → 38 370 s **exact**; `M1_m`/`M2_m`/`B_hi`/`I_hi`
852.70 → **51 162 s**, where the document registers **51 161 s** — **1 second
low, 0.002 %**. It is a rounding artefact, it binds *tighter* than the rule so it
cannot license an overrun, and **it is left exactly as frozen.** Recorded here
because a lane that checks a conversion and mentions only the rows that matched
has not checked it.

---

## 5. WHAT THIS LANE DID NOT DO — each stated explicitly

- **`AMENDMENT 2` was NOT appended.** `K0d_REREGISTRATION.md` is **byte-unchanged**
  at blob `36b302f1`, still version 1.1, still ending at `A1.8`.
- **No comparator was written or repaired**, though writing one was the only way
  to make the fire possible.
- **No cap was raised.** 2,484.84 core-min stands as the registered cap. The
  ceiling was **not** moved to 2,749.14 or to anything else.
- **Nothing was launched.** No case directory, no mesh, no solver, no pid, no
  contention file. **Zero core-minutes.** Rule 12's estimate-versus-actual
  calibration is **not triggered** — no process completed, so there is nothing to
  calibrate, and `docs/COST_CALIBRATION.md` was not touched.
- **Findings 10 and 11 were not re-ruled** — closed by §A1.2b and §A1.3b
  respectively, and cited as closed.
- **`K0d_PREREGISTRATION.md` was not touched**; blob `e629f5c4` unchanged.
- **`docs/LAB_STATE.md`, `docs/DOCKET.md` and `docs/LESSONS.md` were not touched**,
  no id was assigned or reserved, and `scripts/append_record.py` was not used.
- **Nothing was sent** (standing rule 7). Submissions remain **PARKED**.

---

## 6. VERDICT AND WHAT IS NEEDED

**`BLOCKED`** — on two independent stops, both pre-committed by the supervisor in
the dispatching brief, neither of which a lane may clear:

1. **The `12.00` instrumentation figure is unsourced**; the document's own rule
   gives **11.50**. Re-ruling the figure is the supervisor's, and §1.4 costs
   every candidate so it can be done from arithmetic. **It changes no
   conclusion** — the overrun stays ~10.6 %, the derived cost stays ~$2.35.
2. **The entire registered grading path does not exist.** Four scripts, zero
   blobs. Until `build_k0d.py`, `check_k0d_mesh.py`, `mark_done_k0d.py` and
   `analyse_k0d.py` are written, committed and frozen, **K0d has no path to a
   completed run, let alone a graded one**, and no cap decision changes that.

**Stop 2 is the larger finding and it reorders the work.** The cap ruling was
being made for a rung that has no comparator. **A comparator author must be
dispatched before a cap is raised** — and the §2.3 nine-versus-ten marker trap is
handed to them here rather than left to be discovered.

*Written by a heat-transfer lane, 2026-08-25. Zero compute. Nothing fired.*

---

# PHASE 1 REPORT — 2026-08-25T19:24Z. THE BUILDER AND THE MESH CHECKER EXIST AND PASS. THE BUILDER REFUSES TO RUN, AND THAT REFUSAL IS THE FINDING.

**Verdict: `GATE REACHED` on Phase 1 — the two scripts on the critical path to a
running solver are written, self-tested and committed.** Still zero core-minutes.
`verification/runs/F14-cooling-ladder/K0d_runs/` **still does not exist and this
work did not create it** (§P1.6). Nothing was launched. **`PENDING`: the fire
order is the supervisor's and was not taken.**

Written under the supervisor's reorder of 2026-08-25 (Sanaa's directive: cost is
no longer a reason to refuse, defer or stop; rigor untouched). **Cost played no
part in anything below.** The one refusal in this report is a refusal about
*registration completeness*, and no directive about money makes an unregistered
input registered.

## P1.1 WHAT WAS BUILT

| script | path | lines | `--selftest` |
| --- | --- | ---: | --- |
| `build_k0d.py` | `/home/ubuntu/Certonomous/scripts/build_k0d.py` | 560 | **PASS**, 32 checks |
| `check_k0d_mesh.py` | `/home/ubuntu/Certonomous/scripts/check_k0d_mesh.py` | 448 | **PASS**, 29 checks |
| `mark_done_k0d.py` | `/home/ubuntu/Certonomous/scripts/mark_done_k0d.py` | 396 | **PASS**, 15 checks |

**`mark_done_k0d.py` is a PHASE 3 item and was already finished when the reorder
arrived.** It is reported rather than held back, but it does **not** consume the
Phase 2 gate: it is offered for the same personal diff read as the other two.
**`analyse_k0d.py` was NOT started** — Phase 2 says stop, and it is Phase 3 work.

**Location.** `scripts/`, per `FILING_CHARTER.md` ("Scripts | `scripts/`, as
`lower_snake.{py,sh}`"). §7.5 registers the four **by name and not by path**.
Putting them beside the run — the T3 sibling's habit — would have **created
`K0d_runs/` and destroyed the pre-compute absence proof** that §A1.0, §A4.0,
§A5.0 and this report all rest on. **The path is a disclosed lane choice with a
charter behind it, not a physics choice**, and `AMENDMENT 2` should register it.

## P1.2 STOP AND ASK — FOUR INPUTS THE FROZEN REGISTRATION DOES NOT FIX

Superseded §A5.11 clause 2, binding on this file and quoted in its docstring:
*"It may not choose anything this document leaves open. If the builder reaches a
value this document does not fix, that is a finding, it is referred upward, and
it is registered by amendment while the window is open — **it is not chosen by
the script**."*

**That clause is implemented literally. `build_k0d.py` REFUSES (exit 2) and
writes nothing while any gap is unresolved** — and it does not accept them from a
command-line flag, an environment variable or a default, because each of those is
the script choosing by proxy.

| gap | finding | why it is load-bearing |
| --- | --- | --- |
| `writePrecision` | FINDING 14 | **The heaviest of the four.** §7.1's convergence criterion is *"at most `1e-6` of that field's range"* between two checkpoints — on the registered 20.0 K range that is **2e-5 K**, which a coarse write precision cannot represent. The sibling K0cS writes at **16**; the scratch smoke test wrote at **8**. A criterion the rung cannot resolve is not a criterion. |
| `writeFormat` | FINDING 14 | §6 fixes `endTime`, `deltaT`, `writeInterval`, `purgeWrite` and nothing else about writing. |
| `writeCompression` | FINDING 14 | Decides whether the completion reader and the age guard must find `T` or `T.gz`. `mark_done_k0d.py` accepts **either**, so grading does not depend on the answer — but the builder must emit a `controlDict` that states one. |
| `domain_thickness_t` | FINDING 15 | **`blockMeshDict` cannot be written without a z-extent.** §A1.3a records `t` as unregistered and says it *"cancels in every registered quantity"* — true of the **graded quantities**, not of the mesh file, and §A1.3a's own registered sampling plane `z_m = t/2` needs it too. The scratch smoke test used 0.01 m. |

**All four are `AMENDMENT 5` §A5.13 items that were referred and never ruled.**
They are minor in physics and absolute in effect: **the rung cannot build until
they are registered.**

**RECOMMENDATION, and it saves a round trip: fold them into `AMENDMENT 2`
alongside the ceiling correction.** The builder needs an amendment before it can
run; the ceiling correction needs an amendment; **these should be one amendment,
not two.** `AMENDMENT 2` was not written in this phase — the reorder put Phase 2
before it, and writing it before the supervisor's diff read would have
pre-committed the gap values this lane is refusing to choose.

## P1.3 ONE READING DISCLOSED RATHER THAN TAKEN SILENTLY

§4 registers *"two-sided geometric grading to every wall and to both slot lips"*
and one design first-cell per level. **Read as: symmetric two-sided grading with
the registered first cell at BOTH ends of every block, in x and in y.**

It is a reading, so it is flagged. It is defensible because it introduces **no
free parameter**: the single registered first cell fixes both ends; condition D
is satisfied at the floor (block A) and the ceiling (block C); and cell size is
**continuous across both slot lips** as a consequence rather than as a further
choice. The alternative — a separate lip-side expansion — would have been a fifth
registration gap. **Overrule it and the builder changes in one function
(`grading_pair`).**

## P1.4 THE PROPERTIES THE SUPERVISOR SPECIFIED, EACH WITH ITS MEASUREMENT

- **Seed refusal.** `registered_seed()` REFUSES (exit 2) for any closure absent
  from §A1.2a's table. Verified in a subprocess so exit 2 is **observed, not
  inferred**. The `RNGkEpsilon` seed carries `epsilon` and **no `omega`**; the
  laminar seed carries **no `k`, `omega` or `nut`** — the per-closure defect this
  document exists to remove, checked in both directions.
- **`ranks == 1` ASSERTED, not assumed.** `RANKS = 1` with a module-level
  `assert` and the reason written beside it: `timeout = cap_core_min × 60 ÷ ranks`
  is the identity **only** at one rank, and a later decomposed rung would
  silently inherit a timeout `1/ranks` too long. All ten caps carry the
  conversion; `M1_m_seed` takes `M1_m`'s line exactly.
- **The one-second observation is carried forward as code, not prose.** §8.1
  registers **51 161 s** on the L2 row where `852.70 × 60 = 51 162`. The builder
  reproduces **the frozen table, not the recomputed value**, with the reason in
  the comment: it is a rounding artefact, it binds *tighter* so it cannot license
  an overrun, and standing rule 6 says a frozen file is not edited.
- **Caps as runaway guards.** The cap block records Sanaa's 2026-08-25 directive
  in terms — reaching a cap is **reported, not an automatic kill** — while
  keeping the **conversion** unchanged, because a guard set in the wrong units is
  not a guard.
- **Condition G actually fires, and the first version did not.** The planted
  inverted grading was **not refused** on the first run, because *reversing a
  symmetric two-sided distribution reproduces it exactly*. The plant was rebuilt
  to reverse **each half of each block independently** — a real inversion, coarse
  at the walls — and condition D now refuses it on all three levels while
  accepting the clean synthetic mesh. **A control that passes on the first try is
  the one to distrust; this one did not.**
- **Condition G is not a mode.** It runs on **every** invocation, before any real
  mesh is judged, and a run in which the plants are not refused REFUSES the whole
  check (exit 2).
- **`0/T` is touched LAST** by the builder, so its mtime dates the run allowed to
  produce the answer — the age guard of §7.2 clause 6 rests on that ordering, and
  it is now a property of the writer rather than a hope about it.
- **Clause 7 in both scripts.** The builder refuses a case directory that already
  exists; `mark_done_k0d.py --launch-guard` refuses a case in which `0` or any
  numeric time directory already exists.
- **TEN `DONE.<case>` markers, not nine.** `CASES` carries ten in both graders,
  the 77 field-presence assertions (`6×8 + 3×8 + 1×5`) are asserted arithmetically
  in the selftest, and §A1.2b is cited **in the code** as the governing clause —
  §7.5 line 386 still reads "all nine", and this author is the author that trap
  was flagged for.

## P1.5 THE BLINDNESS CHECKER — AND WHY ITS "CLEAN" MEANS SOMETHING HERE

`scripts/check_grader_self_blindness.py --selftest` **PASSES (rc = 0)**: both
probes shown able to fire on planted defects and to stay quiet on clean
counterparts. Over all three scripts: **rc = 0, zero findings.**

**That result would have been worthless without this next line**, per the
ansys-verification finding (`3dc99590`,
`docs/ansys_verification/GRADER_BLINDNESS_PROBE_COVERAGE.md`) that probe B fires
on `os.path.join` and is **silent on `pathlib` and f-string path construction**:

| script | `os.path.join` | `pathlib` | f-string paths |
| --- | ---: | ---: | ---: |
| `build_k0d.py` | 18 | **0** | **0** |
| `check_k0d_mesh.py` | 4 | **0** | **0** |
| `mark_done_k0d.py` | 32 | **0** | **0** |

**Every path in all three scripts is built with `os.path.join` — the one idiom
probe B can see.** The idiom was chosen for that reason. A clean report here is
therefore a statement about the code and not about the checker's blind spot.

Probe B's own defect shape is also guarded directly: `mark_done_k0d.py`'s fixture
builds time directories **numerically from `endtime`**, never from a shared
format constant that the checker then resolves the same way (L-321).

## P1.6 CONTENTION AND CAPACITY, RE-READ AT 2026-08-25T19:24Z

Load **7.31 / 8.31 / 8.95**, 16 cores, `MemAvailable` **18 869 192 kB = 17.99 GiB**.

**SEVEN sustained foreign cores at ≥ 99 %, unchanged in identity from 19:07Z:**
three T-family `buoyantBoussinesqSimpleFoam` (pids 2203927 / 2203944 / 2203947,
elapsed 2h47m) and four dafoam IPOPT ranks (pids 2359929–2359932, elapsed 1h11m).

**The box is 7 of 16 committed. Nine cores are nominally free, and K0d wants ten
single-rank cases.** §9.1 registered `5 + 9 = 14 of 16`; the live figure is
`7 + 10 = 17 of 16`. **A staged launch of at most SEVEN cases seats inside the
supervisor's ~14/16 ceiling**, with the remaining three queued behind the first
retirements. Memory is not the constraint (17.99 GiB against §9.2's ~2.15 GiB
conservative bound for all ten, and §9.2's drop-to-seven trigger at 14 GiB is not
tripped).

**No contention file was written, because there was no launch.** The file is
written *at* launch and records the load average, the count and identity of
foreign solvers, and the cores taken — `build_k0d.py` does not write it, because
building is not launching.

## P1.7 STATED PLAINLY FOR A LATER READER: THIS RUNG CANNOT PRODUCE A CREDENTIAL

**§0 of the re-registration holds unchanged.** Blay, Mergui and Niculae (1992) is
**`NOT OBTAINED`**. Every graded row is `BLOCKED` at §7.4 order 4 until a dated
reference addendum arms §7.6, and the tally stands at **0 of 10**.

**K0d therefore earns V and G but NOT P. Its verdict is `GATE REACHED` naming the
missing limb — never `HOLDS`.** What a completed fire produces is the solves and
the physics-stage instruments: convergence, achieved `y⁺`, the five guards, the
Roache triples, the discrimination control, the seed control and the dual-scheme
control. **On a converging triple that is real coverage and it is worth having.
It is not a candidate credential, and nobody may later read a completed run of
this rung as a graded result.**

Obtaining the primary is outside this box and is **Sanaa's alone** (standing
rules 7 and 8). It was not attempted.

## P1.8 WHAT PHASE 1 DID NOT DO

- **Nothing was launched.** No case directory, no mesh, no solver, no pid, no
  contention file. **Zero core-minutes.** `K0d_runs/` re-proved ABSENT under a
  live planted control in this phase's own committing invocation.
- **`AMENDMENT 2` was not written**, and `K0d_REREGISTRATION.md` is byte-unchanged
  at blob `36b302f1`. No cap was raised and no ceiling registered.
- **`analyse_k0d.py` was not started** (Phase 3).
- **No registration gap was chosen, defaulted or flagged past.** The builder
  refuses.
- **No comparator was repaired to make a fire possible**, and nothing was copied
  from the scratch smoke-test dictionaries.
- **`docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md` and
  `docs/COST_CALIBRATION.md` untouched**; no id assigned or reserved;
  `scripts/append_record.py` not used.
- **Nothing was sent** (standing rule 7). Submissions remain **PARKED**.

## P1.9 VERDICT

**`GATE REACHED`** — the two Phase 1 scripts exist, are self-tested against
planted controls in both directions, and are committed. **`BLOCKED`** on the
builder actually running, on **four unregistered inputs that only an amendment
can close**. **`PENDING`** the supervisor's personal diff read and fire order,
neither of which is this lane's.

*Phase 1 by a heat-transfer lane, 2026-08-25. Zero compute. Nothing fired.*
