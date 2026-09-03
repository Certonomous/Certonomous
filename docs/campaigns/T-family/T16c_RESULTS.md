# T16c results — the re-grade of `T16_MC_c/m/f` under the repaired comparator — **`NOT A RESULT`**, on the registered unreachable branch of §4, and the ordering guard the predecessor fired on did **not** fire

**Graded 2026-09-03T20:55:59Z** by the heat-transfer grading lane, one invocation,
against the live tree `verification/runs/T-family/T16_runs/`.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL /
NOT A RESULT / BLOCKED / PENDING.**

---

## 1. THE VERDICT

**`NOT A RESULT`** — all four graded rows (`G1`, `G1b`, `G2`, `G3`), on the
**registered unreachable branch** of the frozen station rule.

| row | quantity | value | triple | verdict |
|---|---|---|---|---|
| `G1` | `v(Y = 0.25)/U0` on the station row | **NONE** — no station was selected | `null` | **`NOT A RESULT`** |
| `G1b` | `Y_max`, location of maximum upflow | **NONE** — no station was selected | `null` | **`NOT A RESULT`** |
| `G2` | RMS over the station row of `(T − T_lin)/dT` | **NONE** — no station was selected | `null` | **`NOT A RESULT`** |
| `G3` | `tau_hot / tau_cold` from the half-cell wall gradients | **NONE** — no station was selected | `null` | **`NOT A RESULT`** |

**The deciding number.** No `j` in the fine level's candidate set of **3,840 rows**
reaches `W1_T <= 1.0e-06`. The best is **row 4479 at `W1_T = 4.5837e-04`**, which is
**458.4× the floor**. `T16C_GRADE_OUTPUT_20260903T205559Z.txt:33`;
`gate_t16c.json` → `station.reachable = false`, `station.best_W1_T =
4.583706738858627e-04`, `station.selected = null`.

**This is the branch the frozen document registered in advance and without appeal**
(`T16c_PREREGISTRATION.md:210-217`): *"If no `j` in the candidate set satisfies the
threshold, T16c returns `NOT A RESULT`, the station is NOT relocated, the threshold
is NOT loosened, and the candidate set is NOT widened."* None of those three things
was done. The recorded reason is the one §4 fixed in advance: **the registered
referent does not describe this solve's regime, and the honest consequence is that
the *case*, not the comparator, needs changing.**

**THE EXIT CODE DID NOT CARRY THE VERDICT.** The grading invocation returned
**rc = 0** — *graded, not refused* — while its stdout carries `NOT A RESULT` on every
row. The verdict was read from stdout and from `gate_t16c.json`, never from the exit
code. This is the standing trap in this family and it fired here exactly as expected:
a reader who had checked `$?` would have recorded a clean grade.

### 1.1 WHAT THE REPAIR ACTUALLY BOUGHT — the predecessor's published diagnosis was false, and this run shows it

T16 refused these same three solves under one clause at `analyse_t16.py:573-576`
that published **"a transposed cell ordering"**. T16c splits that clause. Measured
here, all three levels, `T16C_GRADE_OUTPUT_20260903T205559Z.txt:25-28`:

| level | `\|slope/(−dT) − 1\|` | threshold | margin |
|---|---|---|---|
| `T16_MC_c` | `8.6008e-05` | `0.5` | **5,813× inside** |
| `T16_MC_m` | `7.6997e-05` | `0.5` | **6,494× inside** |
| `T16_MC_f` | `7.3629e-05` | `0.5` | **6,791× inside** |

**`C_TRANSPOSE` did not fire on any level.** The cell ordering is fine and was always
fine. The predecessor's refusal text named a defect that is not present, at a
tolerance six orders of magnitude away from the proposition it was actually testing.
**T16c reaches `NOT A RESULT` — but for the true reason and with the false diagnosis
withdrawn**, which is the entire content of the repair. A `NOT A RESULT` with a
correct cause is a different object from a refusal with a wrong one.

### 1.2 THE `W1_T` TRIPLE THAT §0.1(i) REFUSED TO QUOTE IS NOW MEASURED — and the registration was right to decline it

`T16c_PREREGISTRATION.md:45-54` recorded that the commissioning brief's triple
`1.204e-03 / 1.094e-03 / 1.050e-03` was **not on disk**, that a search returned zero
occurrences of its first two values, and that **"a number whose artifact is gone is
not a result"** — so the registration used §18.3's sourced ratio `~1050×` and did not
quote the triple.

**MEASURED this invocation**, `T16C_GRADE_OUTPUT_20260903T205559Z.txt:22-24`:

| level | `W1_T` | floor | ratio |
|---|---|---|---|
| `T16_MC_c` | `1.2042e-03` | `1e-06` | 1204.2× |
| `T16_MC_m` | `1.0940e-03` | `1e-06` | 1094.0× |
| `T16_MC_f` | `1.0504e-03` | `1e-06` | **1050.4×** |

The three values reproduce the commissioning brief's triple to every quoted digit,
and the fine level's `1050.4×` reproduces §18.3's `~1050×` independently. **The
registration's refusal to quote an unsourced number cost it nothing and the numbers
were right.** That is the case for the rule, not against it: the figures are now
**MEASURED with an artifact**, where before they were recollection.

**DERIVED, DIAGNOSTIC ONLY, NOT A GRADED ROW.** `W1_T` is a gate-(1) witness with no
registered band, so it is **not** graded and **no GCI is quoted for it**. Its three
values are monotone decreasing; `m−c = −1.1020e-04`, `f−m = −4.3600e-05`, ratio
`2.5275`, observed order `p = 1.338`; Richardson limit **`1.0219e-03` ≈ 1022× the
floor**. **`W1_T` mesh-converges to a non-zero value.** Refining will not bring the
temperature field into streamwise development anywhere in the candidate set — which
is why §4's branch is unreachable and why the fix is the case, not the mesh and not
the tolerance.

---

## 2. THE OPEN EXPOSURE THAT TRAVELS WITH THIS VERDICT — F2, **NOT DISCHARGED**

**A reader of the verdict above must meet this before anything else, and it is not
closed by this grading.**

`T16c_INSTRUMENT_DIFFS.txt:358` records ruling **F2** as a **NAMED OPEN EXPOSURE,
ESCALATED TO VERIFICATION AND NOT DISCHARGED**:

1. **`exact_t16.py` is UNPINNED.** The frozen document §5 (`:229-244`) registers
   **exactly one** pin, `T16_registered.json`. `exact_t16.py` supplies band constants
   to the comparator and is not pinned, **so a change there could move a band without
   producing any refusal.**
2. **Second limb, same exposure.** `analyse_t16.py` is likewise unpinned, and for
   **four** constants the comparator restates — **`CONV_FLOOR`, `G_TOL`,
   `MASS_FLOOR`, `PLAT_FLOOR`** — the frozen document **registers no literal at
   all**. MEASURED: the names `CONV_FLOOR` and `G_TOL` occur **zero** times in the
   frozen v1.0 bytes. They are bound only by §1 line 4's *"Every other floor …
   carried over byte-identically"* (`:104-105`) and §6's clause list (`:256-259`), so
   **their authority chain runs through an unpinned parent.**
3. **THE RULING WAS: DO NOT ADD A PIN.** A pin the frozen document does not register
   **is a new gate**, and §9 forbids moving a gate. The authoring lane declined to add
   one and that judgement is upheld. **No pin was added by this grading lane either.**
4. **The digest is therefore reported as `provenance_reported_not_gated`**, and it was
   so reported in this run: `exact_t16.py` `7ecc61a7…`, `build_t16.py` `cb19b3e3…`,
   `analyse_t16.py` `1a5c79e5…`
   (`T16C_GRADE_OUTPUT_20260903T205559Z.txt:3-5`; same three digests echoed into
   `gate_t16c.json` → `provenance_reported_not_gated`).
5. **CLOSING IT REQUIRES A SUCCESSOR REGISTRATION — a T16d that registers the
   additional pins — NEVER a patch** to this comparator or to the frozen document.

**What this means for the verdict above, stated plainly and not softened.** The
`NOT A RESULT` of §1 does not depend on any band, so the unpinned band constants
could not have produced it: §4's branch is decided by `W1_T` against `W1_FLOOR_T`,
and `W1_FLOOR_T = 1.0e-06` **is** registered as a literal (`:103`, `:187-188`) and
**is** checked. **But that is a fact about this particular outcome, not a discharge
of the exposure.** Had the station been reachable, `G1`/`G1b`/`G2`/`G3` would have
been graded against bands whose constants reach the comparator through an unpinned
parent. **The exposure stands open, and this record does not close it.**

---

## 3. RULE 4 — STRICT COMPLETION, RE-VERIFIED LIVE, PER CASE

All conjuncts were **re-read from the artifacts in the grading invocation**, not
taken from the `DONE.` markers. Artifact:
`T16C_GRADE_OUTPUT_20260903T205559Z.txt:6-9`.

| conjunct | `T16_MC_c` | `T16_MC_m` | `T16_MC_f` | evidencing artifact |
|---|---|---|---|---|
| `rc = 0` | 0 | 0 | 0 | each case's `STATUS.` / solver log, read by the comparator |
| `End` line present | True | True | True | `T16_MC_*/log.solve` |
| last time == `endTime` | 10000 == 10000 | 20000 == 20000 | 40000 == 40000 | `log.solve` + `system/controlDict` |
| fields present | `T, U, p_rgh, phi` | `T, U, p_rgh, phi` | `T, U, p_rgh, phi` | `T16_MC_*/<endTime>/` |
| `ExecutionTime` count == `endTime` | 10000 lines | 20000 lines | 40000 lines | `log.solve` |
| **AGE GUARD** vs the case's own `0/T` | **+744 s** | **+13,405 s** | **+129,117 s** | `0/T` and `<endTime>/{T,U,p_rgh,phi}` mtimes |

**All three cases PASS every conjunct of rule 4.**

**The age guard was genuinely re-run — there is no archival gap.** The `0/` directory
survives in all three cases (`T16_MC_f/0/` holds `T`, `U`, `alphat`, `p_rgh`,
verified on disk this invocation), so `0/T` was available as the datum and the
comparator measured a positive age delta for every field on every level rather than
reporting the guard as unavailable. **This conjunct is a pass, not a gap.**

**The field set is the registered one, not a weakened one.** `T, U, p_rgh, phi` is
`completion.needed_fields` in the **pinned** `T16_registered.json`, read from that
file this invocation. `CLAUDE.md` rule 4 names `T U p_rgh alphat nut k omega` for the
thermal family; T16 is a **laminar** mixed-convection case and carries no `nut`, `k`
or `omega` to require. The set is carried over under §6 and is gated by the §5 pin —
a change to it would have to change a file whose digest stops the run.

**Consistency with the `DONE.` markers, disclosed.** All three markers read *"strict
rule met on the PHYSICS-CRITICAL conjuncts P1–P5"* — the physics/infrastructure split.
The comparator did not rely on them: it re-derived every conjunct from the artifacts,
and its independent reading agrees.

---

## 4. THE ROACHE TRIPLE — rule 5

**No triple was formed, and none could be.** `station.selected = null`, so no station
row exists at which `G1`, `G1b`, `G2` or `G3` could be evaluated on any level. Every
row carries `value_fine: null`, `triple: null`, `triple_state: null` in
`gate_t16c.json`.

- **Triple classification: NONE — not `CONVERGING`, not `DIVERGENT`, not `STAGNANT`,
  not `OSCILLATORY`, not `EXACT`. There are no three values to classify.**
- **Observed order: NOT COMPUTED**, for the same reason.
- **NO GCI IS QUOTED**, for any row. Rule 5 permits a GCI only on a `CONVERGING`
  triple; there is no triple at all here, which is a stronger bar than a
  non-converging one.

**Rule 5's direction of travel was respected.** Gate (1) failed
(`gate1.ok = false`), and a failed gate (1) may only turn a verdict **into**
`NOT A RESULT`. It did exactly that, and it did so **before** any band was
evaluated — no `PASS` or `GATE FAIL` was computed and then overturned, because
no value ever existed to band. The one-way rule was never even under strain here.

The three-level consistency clause of §4 (`:203-208`) was likewise never reached:
it tests the selected `y/b` on all three levels, and no `y/b` was selected.

---

## 5. FREEZE VERIFICATION — done in the grading lane's own invocations

| what | expected | measured | result |
|---|---|---|---|
| frozen v1.0 prefix of `T16c_PREREGISTRATION.md`, first **19,049 bytes** | `0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f` | identical | **MATCH** |
| the same prefix taken from the blob at commit **`8ff2cf36`** | as above | identical | **MATCH** — the on-disk prefix *is* the frozen blob |
| whole file (v1.1, with AMENDMENT 1) worktree vs `HEAD` | — | `bbb658d4…` both | **MATCH** — no uncommitted drift |
| `analyse_t16c.py` disk vs `git show HEAD:` | — | `a91f4c4d1fb66504cc68710a888d841df1549405f47c14010a9e03658ee8f1a2` both | **MATCH** |
| `check_t16c_transcription.py` disk vs `HEAD` | — | `a1fd124394342e4a0dc1cc49ef46634ae2d5c2522b9c2a7c4985cdb2b2e623df` both | **MATCH** |
| `mutation_controls_t16c.py` disk vs `HEAD` | — | `6a68db4083da50657e05050d1d5a431b2c343c807a55c68ed24c792593e7ae35` both | **MATCH** |
| §5 pin, `T16_registered.json` | `aead91aaab8480f6a4321a3d9eb01536d9ceb4cbfb7a3774426cea608ae72845` | identical | **MATCH**, and **enforced** |

All three instrument digests also equal the values PART F recorded on 2026-08-31
(`analyse_t16c.py` `a91f4c4d…`, `check_t16c_transcription.py` `a1fd1243…`,
`mutation_controls_t16c.py` `6a68db40…`). All three are committed at
**`46d090f6`**. `CLAUDE.md` rule 2's requirement — *"verify the frozen file **is**
the file that ran by hashing it against the committed blob"* — is satisfied for the
registration and for all three instruments.

**The §5 pin is armed by construction, not by an optional flag.** There is no
`--expect-sha`-style argument to leave off: the comparator's whole CLI is
`--selftest`, `--selftest-inner`, `--root`, `--json`. `REG_SHA256` is a module
constant at `analyse_t16c.py:215` and `load_registered()` calls `pin()` at `:337`
**unconditionally on the production path** (`here is None`), refusing on mismatch.
There was no disarmable check to disarm.

**The registered invocation.** The frozen document states no literal command line;
it fixes the invocation's binding properties instead — §5 (`:231-235`): the
comparator *"loads … `T16_registered.json` **by absolute path** and **REFUSES (exit
2)** unless its SHA-256 is `aead91aa…`"*, and §10 (`:130-132`): *"Binding only on the
supervisor's freeze commit, with the comparator hashed against its committed blob
before any grading."* Both were satisfied before the run. The production path is the
bare invocation with the default root `LIVE_ROOT = PARENT = T16_runs`
(`analyse_t16c.py:211`, `:225`) and the default output `gate_t16c.json`.

**§9's absent registry was confirmed at the grading invocation, not assumed.**
`gate_t16c.json` **did not exist** before the run (checked immediately prior; the
directory listing carried only the three instruments and the diff file). The T16c
graded output that §9 requires to be absent at the freeze was still absent at the
grade, and this run created it.

### 5.1 THE STALE-BANNER QUESTION — reported, not "fixed"

**The banner is not in `analyse_t16c.py`.** That file's header carries no such
sentence; a `grep` for `NOT YET FROZEN` across the comparator returns zero hits, and
zero hits in **every** committed blob of it. **The banner is in
`T16c_INSTRUMENT_DIFFS.txt:7-10`**, verbatim:

> STATUS: THE SUPERVISOR'S PERSONAL DIFF READ IS COMPLETE (2026-08-31) AND ITS
> FOUR RULINGS ARE RECORDED IN PART F. THIS FILE IS NOT FROZEN. THE COMPARATOR
> IS NOT YET FROZEN AS A GRADING INSTRUMENT. NO T16c GRADED VALUE HAS BEEN
> COMPUTED AND `analyse_t16c.py` HAS NEVER BEEN RUN AGAINST THE LIVE T16 TREE.

**Finding: the banner was accurate when written and two of its four clauses are now
stale.**

- *"THIS FILE IS NOT FROZEN"* — **still true.** `T16c_INSTRUMENT_DIFFS.txt` is an
  instrument description, not a frozen registration, and nothing froze it.
- *"THE COMPARATOR IS NOT YET FROZEN AS A GRADING INSTRUMENT"* — **stale in
  substance.** **What the registration actually pins is the point:** it registers
  **one** digest pin (§5, on `T16_registered.json`) and **one** precondition on the
  comparator (§10: *hashed against its committed blob before any grading*). It does
  **not** register a separate comparator-freeze document, and there is no T16c entry
  in `scripts/check_comparator_freeze.py`. The on-disk comparator **satisfies what
  §10 pins**: it is committed at `46d090f6` and is byte-identical to that blob
  (`a91f4c4d…`, measured above). The banner was written at 20:00 on 2026-08-31; the
  commit that made the statement false landed at 20:02 the same day. It is a banner
  overtaken by a commit two minutes later, which is precisely the failure mode
  AMENDMENT 1(a) had just finished diagnosing on the registration's own line 3.
- *"NO T16c GRADED VALUE HAS BEEN COMPUTED"* and *"HAS NEVER BEEN RUN AGAINST THE
  LIVE T16 TREE"* — **true until this invocation, and falsified by it.** This
  document is the first T16c graded output.

**Nothing was edited.** This lane did not touch `T16c_INSTRUMENT_DIFFS.txt`, the
comparator, the registration or any frozen byte. The finding is reported here and the
correction — a dated foot amendment to the diff file under rule 6 — is the
supervisor's to make or decline.

---

## 6. THE INSTRUMENT CHECKS, IN THE ORDER THEY WERE RUN

### 6.1 Transcription checker — **rc 0, CERTIFIED**

`check_t16c_transcription.py`, which refuses (exit 2) on a bad transcription and sits
**off** the grading path. Certification line, verbatim:

> CERTIFIED: 14 constant(s) equal their registration in the document frozen at
> 8ff2cf36 (8 against a LITERAL the document states, 6 BY_REFERENCE against the
> parent it binds them to), 1 name-binding(s) still bind a name.

It also emitted the F2 exposure itself, unprompted, as a second line: the
`analyse_t16.py` digest `1a5c79e5…` reported **and not gated**, with *"the
BY_REFERENCE authority chain remains an OPEN exposure."* **It did not refuse. Nothing
was blocked, and grading proceeded on a clean certification.**

### 6.2 Comparator selftest — **40 limbs, 40 green, 0 failed, rc 0**

`analyse_t16c.py --selftest` → `SELFTEST PASS (0 failed)`, limbs `L01`–`L40`.

**Recorded as the lab's standing caveat, not as a boast: a selftest that passes is
the weak test.** The load-bearing question is whether the refusals fire, and the
green limbs that answer it are the ones that *drove* a refusal: `L32` (a limb pointed
at the live `T16_runs` root **refused at exit 2** and the watcher recorded **0** new
reads under the live tree), `L33` (S8b sentinel removed → refused), `L34` (symlink to
the live tree → refused), `L38` (**the watchers were shown able to see a non-zero**:
1 and 1 deliberate planted reads before clearing, so their zeros are evidence — rule
3), `L39` (**0** unallowed reads under `T16_runs`, **0** under `T16c_runs`), `L35`
(the source detector returns **1** on a planted `grade(HERE, …)`, the exact
`analyse_t18.py:509` shape, so its 0 is evidence).

### 6.3 The `python3 -O` limb — **the refusals still fire**

- `python3 -O analyse_t16c.py --selftest` → **rc 0, 40 limbs, 0 failed** — identical
  to the un-optimised run.
- `python3 -O analyse_t16c.py --selftest-inner` (a bare S8a probe) → **rc 2**, the
  S8a refusal text printed. **The guard fires under `-O`.**
- **The measured reason it fires: `analyse_t16c.py` contains ZERO `assert`
  statements** (AST count 0, confirmed independently by `grep -cE '^\s*assert\b'` = 0
  and by limb `L36`, whose counter was **shown able to see a planted assert: 1**).
  Every refusal in the file is `sys.exit(2)`.

**This is the lab-measured `-O` defect class (L-332, and the cfd converter repair at
`f403828e`/`463de30e`) meeting a file that was built against it.** The `-O` limb is
not a formality here — it is the control that proves the design claim, and it is
green because the guards are not asserts. **Reported, not repaired. Nothing needed
repair.**

### 6.4 Mutation controls — **M31 classified `EXACT`; the full sweep was NOT re-run, and why**

Run: `mutation_controls_t16c.py --only M31`.

- **Control (unmutated copy): exit 0, 0 red limbs** — *"the harness reports green on
  an unbroken file, so its reds are attributable."*
- **`M31` → `EXACT`, exit 1, reddened `L30` and nothing else.**
- **LIVE-TREE CONTROL: 161 entries fingerprinted under `T16_runs` before and after —
  IDENTICAL.** The mutation harness touched no byte of the live tree.
- Limb coverage under this single control: **1 of 40**. The harness names the other
  39 as `NOT VERIFIED (no control reddens them)` **in this invocation** — its own
  words, and they are reproduced here rather than left out.

**Why only M31, stated as a budget decision and not disguised as a methodological
one.** The harness runs a full `--selftest` per mutant. The unmutated control plus
`M31` alone took **70.4 s**; the full 41-mutant sweep is therefore **≈ 22 core-min**
against this rung's **2.0 core-min hard cap** — an eleven-fold breach. `CLAUDE.md`
rule 12: an overrun stops the run, it does not get a new budget. **`M31` was chosen
because it is the one PART G names as the `EXACT` control for the repaired `L30`
limb** — the control that caught the dead limb where `open(p, "w")` truncated
`log.solve` and the `End`-line conjunct of rule 4 *"was NEVER EXERCISED"* while the
limb printed green. It reddens `L30` and nothing else, exactly as PART G recorded.

**The full sweep's prior result is not re-claimed as this lane's measurement.** PART G
(`T16c_INSTRUMENT_DIFFS.txt`, G1–G4) records the 2026-08-31 full run: `M31` `EXACT`;
and **three limbs whose labels overstate what they prove — `L19`/`M20`, `L20`/`M21`,
`L34`/`M35`, each MEASURED as a MISS reddening nothing.** Those are that lane's
measurements, cited, **not re-verified here.** They remain open instrument findings.

---

## 7. COST — rule 12, estimate versus actual

**Registered** (`T16c_PREREGISTRATION.md:284-295`): solver **0.00 core-min**
[MEASURED — the runs were already on disk]; grading pass **< 0.5 core-min**
[ESTIMATED]; `ranks` **1**; **CAP 2.0 core-min, hard**.

**Measured**, wall × ranks ÷ 60, `ranks = 1`:

| invocation | wall s | core-min | budget status |
|---|---|---|---|
| **the grading pass** (`analyse_t16c.py`, one invocation) | **5.305** | **0.0884** | **the registered item** |
| `check_t16c_transcription.py` | 0.105 | 0.0018 | unbudgeted (see below) |
| `--selftest` | 32.308 | 0.5385 | unbudgeted |
| `-O --selftest` | 32.853 | 0.5476 | unbudgeted |
| `--only M31` (control + mutant) | 70.448 | 1.1741 | unbudgeted |
| **total, this lane** | **141.02** | **2.3503** | — |

*(The `-O --selftest-inner` probe was sub-second and was **not separately timed**;
it is excluded from the table and is stated here as untimed rather than estimated
into it.)*

**THE COMPARISON THE RULE ASKS FOR.**

- **Actual / predicted, the grading pass: `0.0884 / 0.5` = **0.177×**.** The grading
  pass came in at **17.7 % of its point estimate** and **4.4 % of the hard cap**.
- **Gap attribution: misprediction, in the conservative direction.** The estimate was
  sized *"on three cases of 20/40/80 station rows"* — i.e. against the station-row
  work. The run never reached a station: §4's branch was unreachable, so the
  four graded rows were never evaluated on any level. **A `NOT A RESULT` on gate (1)
  is structurally cheaper than the graded run that was budgeted for.** No contention
  (the box's other lanes were not competing for this single-rank pass) and **no
  waste** — nothing was spent on a run that had to be discarded.
- **Solver cost: 0.00 core-min, as registered.** No solver ran; no T16 case was
  re-run. Confirmed by the live-tree fingerprint control in §6.4 (161 entries,
  identical before and after).

**A SILENCE IN THE FROZEN DOCUMENT, DISCLOSED AND NOT FILLED QUIETLY.** §8 budgets and
caps **"the grading pass"** — *"an overrun stops the grading"* — and the document
**budgets no instrument-validation time at all**. The transcription checker, the
selftest, the `-O` limb and the mutation control together cost **2.2619 core-min**,
which **exceeds 2.0 core-min**. Under the document's literal words that is not a cap
overrun, because the cap's subject is the grading pass, which used 4.4 % of it. **The
honest position is that the reading is genuinely ambiguous, that this lane's total of
2.3503 core-min would breach the cap under the strict whole-rung reading, and that
the ambiguity is disclosed here rather than resolved in the lane's own favour and
left unsaid.** It is why the 41-mutant sweep was stopped rather than run: under
*either* reading, ≈ 22 core-min was not available. **A successor registration should
budget instrument validation explicitly.**

**USD, DERIVED — NOT MEASURED.** At **$0.0513/core-h**, c7a.4xlarge,
**reported-by-owner** (the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5): grading pass **≈ $0.000076**; total this lane
**≈ $0.00201**. Both derived from core-minutes at the recorded rate; neither is a
billing reading.

Calibration row landed in `docs/COST_CALIBRATION.md` per rule 12 and that file's
append rules.

---

## 8. ARTIFACTS

| artifact | path |
|---|---|
| grading stdout, verbatim | `verification/runs/T-family/T16c_runs/T16C_GRADE_OUTPUT_20260903T205559Z.txt` (6,559 B, sha256 `ab5d414e23fdb339724d3f4c546af39a2a99bac8ea5df4903cab6d20b1369c3a`) |
| machine gate record | `verification/runs/T-family/T16c_runs/gate_t16c.json` (11,243 B, sha256 `c1884d1cc39bbdd159955f6c525e59af3aa978c73024d2e71011df4b429d77f7`) |
| frozen registration | `docs/campaigns/T-family/T16c_PREREGISTRATION.md` (v1.1; v1.0 prefix 19,049 B, `0b425c40…cd3f`, frozen `8ff2cf36`) |
| comparator | `verification/runs/T-family/T16c_runs/analyse_t16c.py` (`a91f4c4d…`, committed `46d090f6`) |
| transcription checker | `verification/runs/T-family/T16c_runs/check_t16c_transcription.py` (`a1fd1243…`) |
| mutation harness | `verification/runs/T-family/T16c_runs/mutation_controls_t16c.py` (`6a68db40…`) |
| instrument diffs, PART F rulings | `verification/runs/T-family/T16c_runs/T16c_INSTRUMENT_DIFFS.txt` (F2 at `:358`) |
| the three solves | `verification/runs/T-family/T16_runs/T16_MC_{c,m,f}/` |
| pinned registration | `verification/runs/T-family/T16_runs/T16_registered.json` (`aead91aa…`) |

---

## 9. DISCLOSURES

1. **The F2 exposure is OPEN.** §2 above. `exact_t16.py` and `analyse_t16.py` are
   unpinned; `CONV_FLOOR`, `G_TOL`, `MASS_FLOOR` and `PLAT_FLOOR` have no registered
   literal. **No pin was added.** Closing it needs a **T16d**, not a patch.
2. **The three solves were graded UNEXAMINED as fields**, per frozen §10 item 1. This
   lane verified rule 4 against them and read the registered quantities; it did not
   audit the solutions. If a solve is defective, this rung would not know.
3. **The mutation sweep is partial in this invocation — 1 of 41 mutants, 1 of 40
   limbs covered.** §6.4. The other 39 limbs are `NOT VERIFIED` *by this lane's own
   run*; PART G's 2026-08-31 full sweep is cited, not re-claimed.
4. **PART G's three overstating limbs (`L19`, `L20`, `L34`) remain unrepaired** and
   were not re-measured here.
5. **Rule 4's `B1` reading remains RAISED and NOT RULED** (`T16c_INSTRUMENT_DIFFS.txt`
   E4, third bullet). This grading does not rule it.
6. **The stale banner in `T16c_INSTRUMENT_DIFFS.txt:7-10` was reported and NOT
   edited.** §5.1.
7. **The instrument-validation cost sits in a gap in the frozen document's cost
   section.** §7, final paragraph. Disclosed, not resolved.
8. **This record files nothing anywhere** (`CLAUDE.md` rule 7).
