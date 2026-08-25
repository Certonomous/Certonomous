# The family-wide `python3 -O` sweep — **the exposure is NOT confined to selftests**

**Written 2026-08-25 by the dafoam `-O` sweep lane**, commissioned by
`docs/dafoam/SUPERVISOR_ASSERT_UNDER_O_RULING.md` §6, which recorded that five instruments had
been checked and ~25 had not.

**SUBMISSIONS PARKED.** Every instrument named below is **this lab's own**. `D-ASSERT-O` is a
defect class in Certonomous instruments, **not** in DAFoam, OpenMDAO, pyOptSparse or IPOPT.
**No upstream report arises from this sweep and none is drafted** (`CLAUDE.md` rule 7,
`DAFOAM_CHARTER.md` §10).

Instrument: `cases/dafoam/sweep_assert_under_O.py`. Every count below is reproducible by running
it (`--classify` for the classification pass).

---

## 0. THE ANSWER, FIRST — AND IT CONTRADICTS THE EXPECTATION THE RULING SET

> **GATE 66 / SELFTEST 106 / NEITHER 1, over 173 `assert` statements in 44 files of a
> 217-file population.**
>
> **The honest answer to the question the ruling asked — "is the exposure confined to
> selftests?" — is NO. 66 asserts carry a refusal, guard or control on a path that runs during
> a REAL run.** The ruling's §3 finding *"THE GATES ARE CLEAN"* is **correct for the five
> instruments it examined and does not survive extension to the family.**

**This is a correction to the commissioning ruling, offered on the record as invited.** §3 was
not wrong about what it measured; it was a sample of five, and the five happened to be the
family's newest and best-built instruments. The older tier is built differently.

**The single most consequential hit, and it was MEASURED not reasoned:** `d8_gen_arm.py` — a
**frozen producer** whose own pre-registration names the assert *as the control*:

> `| d8_gen_arm.py | 0b8a8b34… | producer: 8 anchored edits to base/runScript.py, **each
> asserting anchor count == 1** |`
> — `cases/dafoam/ladder-a/A6/curriculum_D8/PREREGISTRATION.md`

Its `sub1()` reads `assert n == 1` then `return text.replace(old, new)`. **Under `-O` a MISSED
anchor does not refuse: `replace` is a silent no-op, the arm is generated WITHOUT the edit that
defines it, and the generator goes on to print `D8_GEN OK`.** This is standing rule 14's shape
(*"`libs` entries are inserted with an assert, never replaced"*) with the assert as the only
thing between a no-op and a mislabelled experimental arm.

---

## 1. MECHANISM, NOT TOKEN — why this sweep does not grep for "assert"

`python3 -O` / `PYTHONOPTIMIZE=1` elides the bytecode for the **`ast.Assert` node**. The sweep
therefore **parses every blob with `ast` and counts `ast.Assert` nodes.** A grep for the string
`assert` matches it in comments, docstrings and identifiers (`assert_close(...)`, `assertEqual`)
and agrees with the truth only by accident.

**The D4-DEF-4 precedent is the reason.** That sweep's first pass keyed on the token `set_val`,
returned 87 hits with 72 "FIRING", and **could not have seen D4 itself.** Keying on the
mechanism is not a stylistic preference; it is the correction that sweep paid for.

**`grep -r` on this box is ugrep honouring ignore files, so gitignored archives are invisible to
it. No enumeration path in this sweep is a grep, and no `head`, `tail` or pager appears in one.**

## 2. L-325 — every pattern planted BOTH WAYS, and the instrument REFUSED on its first run

A planted control that only proves the reader is alive **does not prove it can say no.** Both
directions are planted and the sweep **exits 2** if either fails.

| plant | expectation | returned |
|---|---|---|
| `curriculum_D12/d12r_grade.py` | present, **59** asserts, sole outer scope `selftest` | **59, `selftest`** |
| `curriculum_D7/d7_grade.py` | **present and ZERO** | present, 0 |
| `curriculum_D7/d7_g8_token.py` | **present and ZERO** | present, 0 |
| `curriculum_D12/d99_grade_does_not_exist.py` | **ABSENT — must NOT read as a zero** | `ABSENT` |
| `NO_SUCH_DIRECTORY_AT_ALL/x.py` | **ABSENT** | `ABSENT` |

**The refusal fired for real on the first run, and it is recorded rather than tidied away.** The
positive plant was entered with a *guessed* path (`ladder-a/A6/curriculum_D12/d12r_grade.py`);
the true path is `cases/dafoam/curriculum_D12/d12r_grade.py`. **The instrument returned `ABSENT`,
refused, and published no count.** Had `ABSENT` been folded into "0 asserts" — the ordinary way
to write such a reader — the sweep would have reported `d12r_grade.py` as **clean**, which is the
exact inversion of the truth.

**A second refinement the plant forced.** Keying on the *innermost* holding function reported
`d12r_grade.py`'s 59 asserts across **32 unrelated function names** (`u01`, `u02`, … `uW`) and
the positive control **failed**. Those 32 are nested *inside* the module-level `selftest`.
**Classification keys on the OUTERMOST scope; the innermost reading would have destroyed the
ruling's actual finding.** Both are recorded per hit.

## 3. POPULATION, AND WHAT IT CANNOT SEE

| population | enumeration | size |
|---|---|---|
| **A — tracked blobs at HEAD, dafoam folder scope** | `git ls-tree -r HEAD` over `cases/dafoam/` + `docs/dafoam/` | 289 `.py`/`.sh` — **217 `.py`**, 72 `.sh` |
| unparseable blobs in A | — | **0** |
| **B — untracked `.py` in the worktree under `cases/dafoam/`** | `find` on disk, differenced against A | **3** |
| **C — dafoam run roots outside git** | `os.walk` of `/home/ubuntu/certonomous-runs`, `processor*` pruned | **1,843 `.py`**, 126 with ≥1 assert, **376 asserts** |

**The worktree is deliberately NOT the population A source.** The shared index is heavily decayed;
sweeping the tree would measure other teams' uncommitted work rather than the lab.

**Population B was swept anyway rather than merely named** — the `d4_stage_F.sh` lesson is that
files outside git are not invisible merely because they are outside git. **All three carry ZERO
asserts**: `curriculum_D12R/d12x_grade.py`, `curriculum_D12R/d12x_run_script.py` (the in-flight
D12 re-registration — **already compliant with the ruling**) and this sweep's own instrument.
**Zero HEAD `.py` under `cases/dafoam/` are absent from disk** (checked in both directions).

**What this enumeration CANNOT see, named and not fixed:**

1. **Population C is counted but NOT classified.** 376 asserts in run-root copies are reported as
   a magnitude only. Most are staged copies of population A and upstream DAFoam tutorials, but
   **I did not classify them GATE/SELFTEST/NEITHER and I do not claim a count for them.**
2. **Instruments inside container images** — `dafoam/opt-packages:latest` was not walked. The
   ruling §2 measured `__debug__` **inside** that image and found it `True`; that is a statement
   about the interpreter, **not** a census of the image's own asserts.
3. **`/home/ubuntu/closure-data`, `/home/ubuntu/closure-challenge-benchmark`** and other
   out-of-git data areas.
4. **An assert reached through an imported helper module living outside dafoam folder scope.**
   Scope is by directory; a dafoam instrument importing a guard from `sdk/` has that guard
   counted against `sdk/`, not against dafoam. **This is the D4-DEF-4 §6 item-4 blind spot
   (a chain whose halves live in two trees) reappearing in a different sweep, and it is not
   closed here.**
5. **Non-Python instruments.** The 72 `.sh` files have **no `assert` mechanism at all**; their
   guards are explicit tests with `exit` codes and are `-O`-proof by construction. **They are
   counted in the population and excluded from the census for a stated reason, not silently.**

## 4. THE RETROSPECTIVE, EXTENDED FROM 5 INSTRUMENTS TO 289

The ruling §2 established on the host and inside the producer image that nothing ran under `-O`.
**I extended the tracked-script half of that check from a spot check to the whole folder scope:**

| check | population | result |
|---|---|---|
| invokes `python -O` / sets `PYTHONOPTIMIZE` | **all 72 `.sh` in scope** | **0** |
| invokes `python -O` / sets `PYTHONOPTIMIZE` | **all 217 `.py` in scope** | **0** |

**Nothing in dafoam folder scope turns the flag on. The ruling's retrospective holds at family
scale, and today's verdicts stand as run.**

## 5. THE CENSUS — 44 files, 173 asserts

| file | n | outer scope(s) |
|---|---|---|
| `curriculum_D12/d12r_grade.py` | 59 | `selftest` |
| `probes/curriculum_D11_mrf_probe_Cprime/d11c_grade.py` | 18 | `selftest` |
| `f6b_periodic_hills/case_breuer_re10595/foam_io.py` | 10 | 5 reader functions |
| `probes/curriculum_D12_unsteady_probe/d12_grade.py` | 5 | `selftest` |
| `ladder-a/A4/curriculum_D3/d3_sep_monitor.py` | 4 | 4 reader functions |
| `ladder-a/A4/curriculum_D3_attempt2/d3_sep_monitor.py` | 4 | 4 reader functions |
| `probes/curriculum_D11_mrf_probe{,_Dprime,_Fprime,_Oprime}/d11*_grade.py` | 4 each | `selftest` |
| `work/NACA0012_Airfoil_Incompressible/probeWallBranch.py` | 4 | `<module>` |
| `ladder-a/A1/curriculum_D13/d13_opt_runScript.py` | 3 | `<module>` |
| `ladder-a/A5/curriculum_D10_probe{,_Pprime}/d10*_grade.py` | 3 each | `selftest` |
| `f6d_random_matrix_uq/f6a_recheck.py` | 3 | `build` |
| `ladder-b/duct_baseline/score_our_baseline.py` | 3 | `<module>` |
| `ladder-a/A5/curriculum_D9/d9_grade_SUPPLEMENT.py` | 2 | `selftest` |
| `ladder-a/A6/curriculum_D8/d8_gen_arm.py` | 2 | `sub1`, `<module>` |
| `f6d_random_matrix_uq/build_ensemble.py` | 2 | `main` |
| `ladder-b/duct_baseline/verify_macro_reader.py` | 2 | `<module>` |
| `ladder-b/S1_work/scripts/r1_sens_vs_error.py` | 2 | `read_scalar_field`, `<module>` |
| *(+ 27 files at 1–2 each — full per-hit listing from the instrument)* | | |

**Files with ≥1 assert: 44 of 217. Total `ast.Assert` nodes: 173.**

### 5a. THE THREE COUNTS, with the definitions they are worthless without

These are the **ruling's own words** (§4: *"no `assert` in an instrument may carry a refusal,
guard, control or gate"*), applied literally.

| bucket | count | definition |
|---|---|---|
| **GATE** | **66** | carries a refusal, guard or control on a path that runs during a **real** execution. Removing it lets the instrument **proceed** with unvalidated data, an unmade substitution, a wrong execution mode or a skipped refusal. |
| **SELFTEST** | **106** | on the selftest/battery path **only**. Removing it makes the battery vacuous but changes no live verdict. Forbidden all the same — §4's extension, *a selftest IS a control*. |
| **NEITHER** | **1** | removing it cannot change any output **as the file is written**. |
| **TOTAL** | **173** | matches the census exactly; coverage is a **counted** control that refuses (exit 2), not an assert. |

**A parser length-guard is classified GATE, deliberately.** `assert len(vals) == n` failing open
yields a number **nothing checked** — that is a refusal in the rule-3 sense, and calling it
"sanity" would be the softening the vocabulary rule forbids. Where the call was close, it went to
GATE: the classification is biased toward **reporting more exposure**, and that bias is stated.

### 5b. GATE, broken down — because "66" is not actionable and the shape is

| subclass | n | what `-O` does to it |
|---|---|---|
| `READER_GUARD` | **39** | a mesh/field parse of the wrong length proceeds; every downstream number is computed on it |
| `LIVE_PRODUCER` | **12** | **an artifact is GENERATED WRONG and reports success** — the sharpest tier, §5c |
| `SERIAL_GUARD` | **7** | `assert comm.size == 1` in the A5 probes: under `mpirun` the probe silently reports **per-rank partial** derivatives as whole ones |
| `OTHER_GUARD` | 5 | DV-count and index-bounds guards |
| `NAMED_CONTROL` | **3** | a control **that names itself a control** in its own message, §5d |

### 5c. `LIVE_PRODUCER` — the tier the ruling's five-instrument sample could not have found

| instrument | assert | what proceeds under `-O` |
|---|---|---|
| `d8_gen_arm.py` `sub1` + E8 | `assert n == 1, "ANCHOR %s count=%d"` | **arm generated without the defining edit; prints `D8_GEN OK`** — MEASURED, §6 |
| `d13_opt_runScript.py` :453/:503/:505 | `assert _eta13 > 0.0, "D13_ETA must be exported"` | `_eta` falls back to **`0.0`** (`float(os.environ.get("D13_ETA","0") or 0)`) and `_fd_suite(...)` runs at **eta = 0.0** — a **complete, plausible FD table at a wrong step parameter** |
| `d1_opt_runScript.py` :433 | `assert _eta_env > 0.0` | same, on the `d1_opt` branch |
| `f6a_recheck.py` :58/:61/:62 | `assert 'eqn += fvc::div(deltaR);' in txt` | a case is built **without the model modification that defines the arm** |
| `build_ensemble.py` :318/:319 | `assert np.linalg.eigvalsh(R)[:,0].min() >= -1e-12` | **non-realizable Reynolds-stress tensors enter the ensemble silently** |
| `rmt_sampler.py` :433 | `assert np.isfinite(vals).all() and vals.min() >= -1e-12` | a non-finite interpolation operator is used |

**`d13_opt_runScript.py` is the same failure mode as `D4-DEF-4`, arrived at by a different
route.** D4-DEF-4's lesson was: *had the scaler been 1.0, a complete plausible FD table would
have been produced at a design point that is not the optimum, and every count-, plant- and
order-based control would have passed.* **`eta = 0.0` under `-O` produces exactly that artifact,
and no control in the family is positioned to catch it.**

**And the contrast sits in the same file, eleven lines below.** The `d1_endpoint_shipped` branch
reads `_d1.planted_zero_control(src_json)   # gate G5, refuses on failure` — an explicit,
`-O`-proof refusal. **One branch of one frozen file does it right and another does it with an
assert.** The repair is a `raise` on three lines.

### 5d. `NAMED_CONTROL` — 3 asserts that call themselves controls in their own failure message

| hit | message | under `-O` |
|---|---|---|
| `r1_sens_vs_error.py:142` | `assert d_perm < 1e-10, "PERMUTATION CONTROL FAILED -- stop here"` | **does not stop.** The very next statement prints `"PERMUTATION CONTROL PASSES."` — **unconditionally** |
| `verify_macro_reader.py:118` | `assert plain_result is None, "…the synthetic test file does not actually exercise the macro bug"` | the negative control asserting the test tests something **stops testing that it does** |
| `verify_macro_reader.py:40` | `assert bd is not None, "sanity check failed: plain Ofpp could not parse 0/U at all"` | the planted positive control is removed |

**`r1_sens_vs_error.py:142` is the sharpest single line in the sweep.** A control whose message
is the word *"stop"*, followed by a print of the word *"PASSES"* that `-O` makes unconditional.
**That is the sixth instance of the shape the ruling §3 named — a control that reports success
while measuring nothing — and this one says so in its own string literal.**

### 5e. NEITHER — one hit, and it is reported rather than rounded into GATE

`d4_accept_compare.py:181` `assert verdict in VOCAB`. Line 180 is
`verdict = "PASS" if g["ACC1_in_band"] else "GATE FAIL"` — both members of `VOCAB` (line 53).
**The assert cannot fire as the file is written.** It is a standing-rule-1 guard against a
*future* edit. **It is still on the wrong side of the ruling**, because the day someone adds a
third branch it will be guarding again — and under `-O` it would resume guarding **nothing**,
silently. Recorded as NEITHER on the mechanism and flagged as a live maintenance hazard.

---

## 6. THE `-O` LIMB WITH MUTANTS — measured on two instruments, not asserted

The ruling §4.2 requires a mutant, *"because comparing healthy-input output under the two flags
proves nothing."* **Both measurements below reproduce that warning exactly and then break past
it.**

### 6a. `d8_gen_arm.py` — the frozen producer, its ACTUAL `sub1` executed

The `sub1` `ast.FunctionDef` node was extracted from the **HEAD blob** and `exec`'d — **the frozen
source itself, not a transcription of it.**

| input | `python3` (`__debug__ True`) | `python3 -O` (`__debug__ False`) |
|---|---|---|
| **healthy** (anchor present ×1) | substitution applied | substitution applied — **IDENTICAL** |
| **MUTANT** (anchor absent, count 0) | **REFUSED** — `AssertionError: ANCHOR E1 count=0 (expected 1)` | **NO REFUSAL. text returned unchanged, rc=0** |

**The healthy rows are identical, exactly as the ruling warned. The mutant row is the entire
finding.**

### 6b. `d11c_grade.py` — a frozen grader's 12-unit battery, three ways

| run | rc | closing line |
|---|---|---|
| `python3 --selftest` | 0 | `D11-C' GRADER SELFTEST: 12/12 PASS (…)` |
| `python3 -O --selftest` | 0 | **byte-identical to the above** |
| all 18 asserts AST-stripped, `python3` | 0 | **byte-identical to the above** |

**Then the discriminator the ruling asked for and that `d12r`'s check did not include — a LOGIC
mutant.** `grade()`'s healthy return was changed from `"GATE REACHED"` to `"PASS"` (one
substitution):

| run | rc | result |
|---|---|---|
| logic mutant, `python3` | **1** | **CAUGHT** — `AssertionError: A: healthy record did not reach the gate, got 'PASS'` |
| logic mutant, `python3 -O` | **0** | **NOT CAUGHT** — `12/12 PASS` |

**This is stronger than the `d12r` result and it is the measurement that matters.** Stripping
asserts and getting identical output shows the battery's *output* does not change. **The logic
mutant shows the battery's DETECTION CAPABILITY is entirely the asserts.** Under `-O`,
`d11c_grade.py`'s battery would certify a grader whose healthy verdict is wrong.

### 6c. A defect in `d11c_grade.py`'s battery that has NOTHING to do with `-O`

Found while measuring 6b and reported because it is worse than the flag:

```
print("D11-C' GRADER SELFTEST: %d/%d PASS ..." % (n, n))
```

**The numerator and the denominator are the same counter**, and `n += 1` runs
**unconditionally** after each unit — `n` counts units **reached**, not units **passed**.
**The line is structurally incapable of printing `11/12`.** Its only failure channel is an
exception escaping the function, and under `-O` most of those exceptions are the stripped
asserts. **`12/12 PASS` is not a tally; it is `n/n`.**

This is why the ruling's requirement 1 — *"every unit tallies an EXPLICIT result… exits non-zero
by counting"* — is the load-bearing half of the repair and the `raise` conversion is the lesser
half. **A battery converted to `raise` but still printing `%d/%d % (n, n)` would satisfy the
letter of the rule and remain unable to report a failure.**

---

## 7. FROZEN INSTRUMENTS — **REPAIR NOT TAKEN**, and the list is the supervisor's to rule

**No instrument was edited by this lane. Rule 6 is absolute and §2d.1 is the supervisor's call,
not a lane's.**

**All 15 declared freezes were verified by hashing the HEAD blob against the md5 in the committed
pre-registration: 15 of 15 MATCH, 0 mismatches.** The exposure is therefore exactly the asserts
counted — **there is no freeze drift hiding additional ones.**

| frozen instrument | asserts | bucket | declared md5 | HEAD blob |
|---|---|---|---|---|
| `ladder-a/A6/curriculum_D8/d8_gen_arm.py` | 2 | **GATE (LIVE_PRODUCER)** | `0b8a8b34…` | **MATCH** |
| `ladder-a/A1/curriculum_D13/d13_opt_runScript.py` | 3 | **GATE (LIVE_PRODUCER)** | `bf6500c7…` | **MATCH** |
| `ladder-a/A1/curriculum_D2/d1_opt_runScript.py` | 1 | **GATE (LIVE_PRODUCER)** | `4c9811d1…` | **MATCH** |
| `ladder-a/A4/curriculum_D3/d3_sep_monitor.py` | 4 | GATE (READER_GUARD) | `cd07d7b8…` | **MATCH** |
| `ladder-a/A4/curriculum_D3_attempt2/d3_sep_monitor.py` | 4 | GATE (READER_GUARD) | `cd07d7b8…` | **MATCH** |
| `ladder-a/A2/curriculum_D4/d4_accept_compare.py` | 1 | **NEITHER** | `680a8280…` | **MATCH** |
| `probes/curriculum_D11_mrf_probe_Cprime/d11c_grade.py` | 18 | SELFTEST | `9987e18d…` | **MATCH** |
| `probes/curriculum_D12_unsteady_probe/d12_grade.py` | 5 | SELFTEST | `7797ec33…` | **MATCH** |
| `probes/curriculum_D11_mrf_probe/d11_grade.py` | 4 | SELFTEST | `2c9a5015…` | **MATCH** |
| `probes/curriculum_D11_mrf_probe_Dprime/d11p_grade.py` | 4 | SELFTEST | `a686c002…` | **MATCH** |
| `probes/curriculum_D11_mrf_probe_Fprime/d11f_grade.py` | 4 | SELFTEST | `0618094c…` | **MATCH** |
| `probes/curriculum_D11_mrf_probe_Oprime/d11o_grade.py` | 4 | SELFTEST | `2b88644c…` | **MATCH** |
| `ladder-a/A5/curriculum_D10_probe/d10_grade.py` | 3 | SELFTEST | `0ef3e76a…` | **MATCH** |
| `ladder-a/A5/curriculum_D10_probe_Pprime/d10p_grade.py` | 3 | SELFTEST | `00949e6d…` | **MATCH** |
| `ladder-a/A5/curriculum_D9/d9_grade_SUPPLEMENT.py` | 2 | SELFTEST | `baf7d69b…` | **MATCH** |

**`curriculum_D12/d12r_grade.py` (59, SELFTEST) carries NO declared md5** in any committed
`.md` under `cases/dafoam/`, `docs/dafoam/` or `verification/`. It is the D12 re-registration in
progress and is **not yet frozen** — which is precisely why it is the cheapest of all of these to
repair, and the ruling already directs that.

**Staged copies in the run roots were checked against the frozen blobs: 14 copies found, 14
byte-identical, 0 differing.** The instruments that ran are the instruments that were frozen.

**THE RULING NEEDED — three tiers, and they are NOT the same question:**

1. **`d13_opt_runScript.py`, `d1_opt_runScript.py`, `d8_gen_arm.py` — frozen, banked, and
   `LIVE_PRODUCER`.** These are the §2d.1 questions. A repair changes a **producer** that has
   already produced banked artifacts. **The verdicts stand** — ruling §2 measured `__debug__`
   true on both sides — **but any RE-RUN or any new arm generated from these files carries the
   exposure**, and ruling §5's *"no re-grade may run on an unrepaired instrument"* was written
   about graders and **applies with more force to producers.**
2. **The 9 frozen `SELFTEST` graders.** Lower urgency: their live gate paths are clean and the
   loss is the battery. §5 already disposes of these.
3. **`d4_accept_compare.py`'s NEITHER hit.** Arguably needs no repair at all today. Named so the
   decision is deliberate rather than an omission.

**I did not adjudicate which specific verdict each frozen case has banked.** A directory-level
scan for the vocabulary returns hits from prose *discussing* the vocabulary and is not a
measurement of a banked verdict. **Stated as unverified rather than guessed.**

---

## 8. OUT OF SCOPE — recorded, owner named, NOT TOUCHED

Six dafoam-adjacent instruments live in `sdk/`, **outside dafoam folder scope**:
`sdk/chief_engineer/docker_dafoam.py`, `sdk/scripts/build_a2_shape_frames.py`,
`sdk/scripts/extract_a5_fd_table.py`, `sdk/tests/test_a2_shape.py`,
`sdk/workflows/_a2_shape.py`, `sdk/workflows/adjoint_optimization.py`.

**They are NOT included in the 173 and NOT classified here.** `sdk/` is `cfd-supervisor`
territory (`CLAUDE.md` roster: *"`cases/` outside closure and dafoam"*, general tooling).
**Recorded for its owner; no change made by this lane.**

## 9. WHAT THIS SWEEP DID NOT ESTABLISH

1. **A zero assert count is a statement about `-O`, not about correctness** — the ruling §6's
   caveat, and it binds this sweep's 173 negatives too.
2. **The `-O` limb was measured on TWO instruments** (`d8_gen_arm`, `d11c_grade`), not on all 44.
   The other 42 are classified **by reading the source**, not by mutation. **Classification is a
   reading; only §6 is a measurement.**
3. **Population C (376 asserts in run roots) is counted, not classified.**
4. **I did not verify that the 12 `LIVE_PRODUCER` asserts have never fired.** A file that
   silently no-ops under `-O` is indistinguishable from one whose anchor always matched;
   distinguishing them needs the run logs, which I did not read.
5. **No repair was made to any instrument, frozen or not.** The counts above are a measurement of
   exposure, not a remediation.
