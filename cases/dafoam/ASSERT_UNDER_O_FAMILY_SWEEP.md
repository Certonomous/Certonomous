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

---
---

# PART 2 — THE **SECOND** HAZARD: unconditional success claim-prints (L-332)

**Added 2026-08-25 by the same lane**, commissioned mid-task by Amendment 1 to
`docs/dafoam/SUPERVISOR_ASSERT_UNDER_O_RULING.md` (commit `40ff9578`).
**Lines whose number changed above this section: 0.**

Instrument: `cases/dafoam/sweep_claim_prints_under_O.py`.

## P2.0 — WHY THIS IS A DIFFERENT SWEEP, NOT A RESTATEMENT

| | assert hazard (Part 1) | claim-print hazard (Part 2) |
|---|---|---|
| how it fails | **silently** — a vacuous battery still printing its count | **loudly and falsely** — an intact battery printing a success it never earned |
| what it leaves | **no evidence** | **counterfeit evidence** |
| worse? | invisible to a reader who looks | visible to a reader who looks — **and therefore believed** |

**They compose, and the composition is where the real defects are.** A `raise`-guarded claim is
`-O`-proof. An **assert**-guarded claim is not — and every one of the ten defects below is a
claim-print whose only guard is an `assert`. **Neither sweep alone finds them: Part 1 sees the
assert and cannot see what it was protecting; Part 2 sees the claim and cannot see that its
guard evaporates.**

## P2.1 — THE COUNTS

| | |
|---|---|
| population (tracked `.py`, dafoam folder scope, at HEAD) | **220** |
| print sites containing a success token | **144** |
| candidates after excluding guarded / ternary / value-report / tally shapes | **43** |
| **+ recovered from this scanner's OWN blind spot (P2.3)** | **+1** |
| **candidates READ** | **44** |
| **CLEARED by reading** | **34** |
| **DEFECTS** | **10** |

### The ten, bucketed as the assert census was

| bucket | count | sites |
|---|---|---|
| **GATE** | **2** | `r1_sens_vs_error.py:143`, `verify_macro_reader.py:170` |
| **SELFTEST** | **8** | `d10_grade.py:158`, `d10p_grade.py:158`, `d11_grade.py:181`, `d11p_grade.py:181`, `d11f_grade.py:181`, `d11o_grade.py:181`, `d12_grade.py:161`, `d11c_grade.py:441` |
| **NEITHER** | **0** | — a measured zero from a bucket the classification can express, not an absence of the question |

**`d12r_grade.py` contributes ZERO here, and that is the supervisor's A1.5 point measured
independently:** it has **no success claim-print at all**, so under `-O` it prints no falsehood —
**it goes vacuous silently with its unit count intact.** On the two axes together it is the worst
instrument in the family: **59 asserts and nothing in the output to notice their removal.**

## P2.2 — THE EIGHT SELFTEST CLAIMS ARE **HARD-CODED STRING LITERALS**, AND THAT IS WORSE THAN A DEGENERATE COUNTER

Seven of the eight print a **frozen literal**:

```
print("D10 GRADER SELFTEST: 6/6 PASS (A healthy, B blind-plant refuses, ...)")
```

**There is no counter.** `6/6` is characters in a string. The only thing that can stop the line
being reached is an exception escaping `selftest()` — and under `-O` the asserts that would raise
it are gone.

### MEASURED on `d10_grade.py`, with the surgical mutant the discrimination required

**My first mutant was too broad and discriminated nothing** — it short-circuited `grade()`
entirely, and unit **B**, guarded by an explicit `raise AssertionError` that **survives `-O`**,
caught it under both flags (`rc=1` either way). **That is the supervisor's own A1.4 failure mode
reproduced in my hands, and it is recorded rather than quietly retried.**

`d10_grade.py`'s battery is **half `-O`-proof**: units **A, C, F** are guarded by `assert`
(stripped); units **B, D, E** by explicit `raise AssertionError` (survive). The mutant therefore
had to break **only what unit A checks**:

| run | rc | closing line |
|---|---|---|
| frozen file, `python3 --selftest` | 0 | `D10 GRADER SELFTEST: 6/6 PASS (…)` |
| frozen file, `python3 -O --selftest` | 0 | **identical** |
| **surgical mutant** (`return "GATE REACHED"` → `"PASS"`, 1 substitution), `python3` | **1** | `AssertionError: selftest A: healthy record did not reach the gate, got 'PASS'` |
| **surgical mutant**, `python3 -O` | **0** | **`D10 GRADER SELFTEST: 6/6 PASS (A healthy, …)`** |

**A grader whose healthy verdict is wrong certifies itself `6/6 PASS`, exit 0, under `-O`.**
That is cfd's L-332 case reproduced inside dafoam, on a **frozen** instrument.

## P2.3 — MY OWN SCANNER'S FALSE **NEGATIVE**, FOUND BY MEASUREMENT AND REPORTED

The supervisor's scanner produced three **false positives** and cleared them by reading. **Mine
produced a false NEGATIVE, and it is the more dangerous direction** — a false positive costs a
lane's time; a false negative is a defect reported as clean.

I excluded "tally-shaped" prints (`%d/%d`, `failed=`) because A1.2 established a tally is a count
and not a claim. **`d11c_grade.py:441` is tally-shaped and IS a false claim**:
`print("… %d/%d PASS …" % (n, n))` — **the numerator and denominator are the same counter**, and
`n` increments unconditionally. It can only ever print `N/N`.

**I caught it only because Part 1 had already measured it.** So I went back and asked the
mechanism question — *is any `%` tuple printed with identical numerator and denominator?* — over
the whole population: **exactly one hit, `d11c_grade.py:441`.** The blind spot is now bounded by
a measurement rather than by my confidence.

**The lesson for the family's rule, and I think it should be written down:** *"a tally is not a
claim"* is true only when the denominator is **independent of the numerator**. `%d/%d % (n, n)`
is a claim wearing a tally's clothes. **A tally whose denominator is the numerator is the
degenerate case, and a scanner that whitelists tallies must exclude it.**

## P2.4 — THE TWO `GATE` DEFECTS

**1. `ladder-b/S1_work/scripts/r1_sens_vs_error.py:142–143` — both hazards in two adjacent lines**

```
assert d_perm < 1e-10, "PERMUTATION CONTROL FAILED -- stop here"
print("  PERMUTATION CONTROL PASSES. serial[perm[i]] = dv[i]; …")
```

Under `-O` the assert is gone and **the next line prints that the control passes,
unconditionally.** A control whose failure message is the word *"stop"*, followed by an
unconditional print of the word *"PASSES"*. **This is the single clearest instance of L-332 in
dafoam and it needs no mutant to see.**

**2. `ladder-b/duct_baseline/verify_macro_reader.py:170` — a HYBRID, and the interesting one**

`ROUND-TRIP VERIFICATION: PASS` is **correctly guarded** against every `if`-checked failure
(`if dup_result is None: print("FAIL"); sys.exit(1)`, three of them — textbook, `-O`-proof).
**But the same file's two controls at :40 and :118 are `assert`s**, and the final claim is **not**
guarded against those.

- `:40` — the planted **positive** control (*"plain Ofpp could not parse 0/U at all"*)
- `:118` — the **negative** control asserting the synthetic file *actually exercises the macro bug*

**Under `-O`, both controls vanish and `ROUND-TRIP VERIFICATION: PASS` still prints — including
for a test file that exercises nothing.** The author guarded the failures they thought of with
`if`/`exit` and the controls with `assert`. **The claim is protected against the ordinary
failures and unprotected against the ones that decide whether the test tested anything.**

## P2.5 — THE 34 CLEARED, AND WHAT CLEARED THEM

**Every one was read. None was cleared by inference.**

| cleared class | n | why |
|---|---|---|
| **narrative/exposition prints** (`S1_gp4_replacement`, `s1_zerocompute`) | 18 | multi-line prose printed as analysis text. `s1_zerocompute.py:295` prints *"G-P4: PASS."* **as an exhibit of what the OLD gate wrongly says** — the surrounding text explains it is blind. **A quotation, not a claim.** |
| **preceded by a `raise`-based refusal** | 5 | `d13_grade.py:275` / `d13_grade_supplement.py:316` — `if not all(v["pass"] …): B._refuse(…)`, and `_refuse` ends `raise Refuse(tag)` (**verified at `d13_basin.py:208`, not assumed**). `d1_fd_endpoint.py:125` (both copies) — `if not seen: … raise SystemExit(2)`. |
| **arithmetic tally + counted refusal** | 2 | `d3_grade.py:424` (both copies) — `bad` counter, `if bad: … return 2`, **then** `ALL CONTROLS SEEN`. Exactly the form ruling §4.1 requires. |
| **value reports** | 6 | print the *value*, so they say `False` on failure — `d3_grade.py:376`, `verify_macro_reader.py:164`, `probeHandComposition.py:211`, etc. A1.2's third false positive, avoided. |
| **vocabulary/label text** | 2 | `d3_grade.py:458` prints the verdict vocabulary as a legend. |
| **this sweep's own instrument** | 1 | `sweep_assert_under_O.py` — see P2.6. |

## P2.6 — L-332 APPLIED TO THIS LANE'S OWN INSTRUMENT

`sweep_assert_under_O.py` printed `coverage controls passed: …` **after** `if failures: sys.exit(2)`.
That is *safe* — the exit precedes it and is `-O`-proof — but it is **the shape L-332 forbids**,
and a later edit that turned the exit into an assert would leave the claim standing.
**Corrected: the claim now prints inside an explicit `else:`**, so removing the check removes the
claim. Re-run after the change: 173 hits, coverage controls pass, unchanged.

**I am not exempt from the rule I am enforcing, and finding the shape in my own file an hour
after writing it is the argument for the rule rather than against it.**

## P2.7 — `d7_g8_token.py`: **ARM 2 ACHIEVED**, and all three arms now measured

The supervisor's A1.4 records arm 2 as **not achieved**: two malformed mutants, each crashing
under both flags with `rc=1`, discriminating nothing. **The innocent explanation was already
established there and it is correct — run from a scratch path, the instrument's own C1
(on-disk md5 == HEAD blob) and `load_grader()` refuse. That is the control WORKING.**

**The way past it is to put the mutant in the DATA, which is where a real failure comes from,
and to leave the instrument untouched so its own controls pass.** The module was imported
**from its own directory** (so `HERE`, C1 and C2 resolve to the real committed files) and driven
against the **C5 write-gate** — not merely against `evaluate()`, which the selftest already
covers. `mod.TOKEN` was redirected to a scratch path so a refusal that failed to fire **could not
forge the real token and would still be visible.**

| arm | requirement | result |
|---|---|---|
| **1** — guarded path under `-O` | refuses | healthy case: `pass=True`, token written, `rc=0` — **and the failing case refuses**, `rc=2` |
| **2** — **MUTANT** under `-O` | **refuses** | **`D7_G8_TOKEN REFUSED  G8 did NOT pass -- the token is not written`, `rc=2`, NO token written** — **identical to plain `python3`** |
| **3** — AST check | zero `Assert` nodes | **0** |

**`d7_g8_token.py`'s C5 gate is `-O`-proof, measured on the gate itself.** The supervisor's
endorsement of this instrument now rests on all three arms.

**ZERO BYTES of `d7_g8_token.py` or `d7_grade.py` were modified. No mutant was committed.**
The real token `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/.d7_g8_pass` was
**verified byte-unchanged before and after** (605 bytes, mtime 22:02, both readings).

## P2.8 — COMBINED EXPOSURE, AND THE REPAIR LIST THAT IS THE SUPERVISOR'S TO RULE

| instrument | frozen | asserts | claim-print defect | combined |
|---|---|---|---|---|
| `d10_grade.py` | **yes** | 3 SELFTEST | **literal `6/6 PASS`** | **battery certifies itself under `-O` — MEASURED** |
| `d10p_grade.py` | **yes** | 3 SELFTEST | literal `6/6 PASS` | same shape |
| `d11_grade.py` | **yes** | 4 SELFTEST | literal `7/7 PASS` | same shape |
| `d11p/f/o_grade.py` | **yes** | 4 each | literal `7/7 PASS` | same shape |
| `d12_grade.py` | **yes** | 5 SELFTEST | literal `8/8 PASS` | same shape |
| `d11c_grade.py` | **yes** | 18 SELFTEST | **degenerate `%d/%d % (n,n)`** | **MEASURED (Part 1 §6b)** |
| `d12r_grade.py` | no | 59 SELFTEST | **none** | **silently vacuous — worst on both axes** |
| `r1_sens_vs_error.py` | no | 2 GATE | **`CONTROL PASSES` after the assert** | **both hazards, adjacent lines** |
| `verify_macro_reader.py` | no | 2 GATE | **`VERIFICATION: PASS` unguarded against them** | **hybrid** |
| `d8_gen_arm.py` | **yes** | 2 GATE | none | **silent wrong-arm generation — MEASURED** |
| `d13/d1_opt_runScript.py` | **yes** | 4 GATE | none | **FD table at eta = 0.0** |

**NINE frozen instruments carry a claim-print or producer defect. Repairing any of them is a
§2d.1 question and it is the supervisor's, not this lane's. Nothing was repaired.**

**The one edit this lane made to any instrument is to its OWN sweep (P2.6).**

## P2.9 — WHAT PART 2 DID NOT ESTABLISH

1. **The `-O` limb was measured on `d10_grade.py` and `d7_g8_token.py`.** The other six literal
   `N/N PASS` closers are classified **by reading**, on the ground that the print is a string
   literal at the end of the function — strong, but a reading, not a measurement.
2. **`verify_macro_reader.py`'s hybrid was NOT executed under `-O`.** It needs the CBFS dataset
   and I did not run it. **The claim that its final PASS survives the two stripped asserts is a
   READING of the control flow, and it is labelled as such.**
3. **The scanner's success-token list is a list.** A claim phrased in words not on it is invisible.
   The 144 sites are what the tokens found, not a proof there are only 144.
4. **`write()` and `_p()` were scanned alongside `print()`, but a claim written through a logging
   framework or an f-string built elsewhere and printed by a variable is not detected.**
5. **The 34 clearances are readings.** None was executed under `-O` with a mutant.
