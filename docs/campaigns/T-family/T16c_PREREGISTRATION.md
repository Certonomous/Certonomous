# T16c — successor to T16's `C_ORDER` clause: an ordering guard sized to its own signal, a profile gate with a station chosen by a frozen RULE, and `W1_T` moved upstream of both

> **STATUS: DRAFT. NOT FROZEN. NOT COMMITTED. AUTHORISES NO GRADING.**
> **This lane did not freeze it, deliberately — see §11.** `SUPERVISION_CHARTER.md`
> §3 check 4 (pre-registration **committed** before compute) is the supervisor's
> **personal, non-delegable** act, and a lane that freezes its own registration
> has self-certified the one check the charter reserves. The supervisor's own
> words two messages before this one: *"check 4 is mine."* That did not change.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE
FAIL / NOT A RESULT / BLOCKED / PENDING.**

---

## 0. **T16c IS NOT BLIND, AND EXACTLY HOW UNBLIND IS ITSELF A REGISTERED FACT**

**The three T16 solves are COMPLETE ON DISK** — `T16_MC_c`, `T16_MC_m`,
`T16_MC_f` under `verification/runs/T-family/T16_runs/`, each with a `DONE.` and
a `STATUS.` marker. **No new compute is required by this rung** (§8). **The
answer already exists; only the reading of it is in dispute. That is what makes
the freeze do all the work here, and it is why the station rule of §4 must be
frozen before the station is computed and not after.**

What is known, **each figure with the artifact that carries it**:

| # | fact | value | source | tag |
|---|---|---|---|---|
| 1 | `C_ORDER` refusal, coarse level | `slope/(-dT) - 1 = -8.601e-05`, `monotone True` | `T16_GRADE_OUTPUT_20260830T231921Z.txt`, last line | **MEASURED** |
| 2 | the same across `c/m/f` | `-8.60e-5 / -7.70e-5 / -7.36e-5` | `DEAD_LEVER_AUDIT.md` §18.1 | **MEASURED** (verification's) |
| 3 | differences and order | `m-c = 9.000e-06`, `f-m = 3.400e-06`, ratio 2.647, **p = 1.404** | §18.1 | **DERIVED** |
| 4 | Richardson limit of the departure | **−7.1536e-05**, i.e. **71× the 1e-06 tolerance** | §18.1 | **DERIVED** |
| 5 | `W1_T` (streamwise T development) | **~1050× over its 1e-06 floor, MESH-CONVERGED** | §18.3 | **MEASURED** (verification's) |
| 6 | `W1_g` (graded velocity reader) | **PASSES all three levels at ~second order** | §18.3 | **MEASURED** (verification's) |
| 7 | the split | **velocity is developed, temperature is not** | §18.3 | **DERIVED** from 5 + 6 |
| 8 | `C_ORDER` tolerance | **`1e-6`**, at `analyse_t16.py:573` | the frozen file | **TRANSCRIBED** |
| 9 | transposed-ordering signature | **−1.0** | §18.2 | **DERIVED** — see §1.2 |

**Fact 4 is the one that decides the rung**, and it is T16's own version of the
T16-class finding this family keeps meeting: *a quantity that mesh-converges to a
non-zero value is a physical feature of the solution, not numerical error, and
refining the mesh will never reduce it.*

### 0.1 TWO FIGURES IN THE COMMISSIONING BRIEF DO NOT SURVIVE CHECKING, AND ARE NOT USED

**(i) The triple `W1_T = 1.204e-03 / 1.094e-03 / 1.050e-03` IS NOT ON DISK.** A
search of `docs/` and `verification/` returns **zero** occurrences of
`1.204e-03` or `1.094e-03` in any T16 context. §18.3 records only the ratio
**"~1050× over its 1e-06 floor, MESH-CONVERGED"** — and `1.050e-03 / 1e-06`
= 1050 exactly, so the brief's third value is consistent with the audit and its
first two are not sourced anywhere this lane can find. **`CLAUDE.md`: a number
whose artifact is gone is not a result.** **This registration therefore uses
§18.3's `~1050×`, which has a source, and does not quote the triple.** If the
three values exist in a record this lane could not find, the supervisor should
name it and the table above can carry them by addendum.

*The distinction that makes this consistent rather than contradictory:* §18 twice
states **"no T16 graded value exists and none was computed."** That is true and
is not in tension with facts 1–7, because `T_slope_rel` and `W1_*` are **guard
and gate-(1) diagnostics**, not graded rows. **No `G1` or `G2` value exists, and
T16c computes none before its freeze.**

**(ii) `-1.000e+00` is NOT measured at `analyse_t16.py:922`.** That line is a
**selftest arm** that forges `transpose=True` and asserts only
`code == EXIT_REFUSE`; it neither prints nor asserts the value. The −1.0 comes
from **§18.2's statement**, and it is **derivable** rather than measured: a
transposed read walks an isothermal column, so `slope ≈ 0` and
`slope/(-dT) - 1 → -1`. **It is tagged DERIVED above and §2 registers the
planted control that will make it MEASURED**, which §18.4 clause 4 requires in
those words — *"shown by a planted control, not asserted."*

---

## 1. THE TEMPLATE — the ten registered lines

**1. CASE.** No new case. T16c re-grades the **existing, complete** `T16_MC_c/m/f`
under a repaired comparator. Geometry, solver, mesh, materials, `endTime` and all
three solves are **carried over from `T16_PREREGISTRATION.md` byte-identically
and unexamined** — this rung changes **the reading, not the run**.

**2. REFERENCE.** Unchanged for the velocity side. For the temperature side the
referent is unchanged **in form** — the hot-to-cold linear profile — and is
**applied only where it is valid**, at a station selected by the frozen rule of
§4. **The referent is NOT replaced.** §4.1 records why replacing it was rejected.

**3. QUANTITIES.** Unchanged graded rows (`G1`, `G2`) plus the clause split:

| id | quantity | replaces |
|---|---|---|
| **`C_TRANSPOSE`** | ordering guard: `\|slope/(-dT) - 1\|` against an **O(1)** threshold | half of `C_ORDER` |
| **`C_PROFILE`** | profile agreement at the selected station | the other half |
| **`W1_T`** | streamwise temperature development — **moved upstream of both** | ordering only |

**4. BANDS.**
- **`C_TRANSPOSE` threshold: `0.5` (dimensionless).** Sized to the **−1.0** signal
  it hunts, not to instrument precision. A true transpose reads −1.0 and is caught
  with 2× margin; the observed physics at −8.6e-05 is **5,800× inside** it and
  does not fire it. *This is §18.2's repair applied literally: size the tolerance
  to the defect, not to the instrument.*
- **`C_PROFILE` threshold: `1.0e-06`, CARRIED OVER UNCHANGED** from
  `analyse_t16.py:573`. **§18.4 clause 2 forbids relaxing it and it is not
  relaxed.** It is *moved to a station where it is valid*, which is a different
  act from loosening it, and §4 is the frozen rule that keeps that act honest.
- **`W1_FLOOR_T` = `1.0e-06`**, carried over from `analyse_t16.py:116`.
- Every other floor — `W1_FLOOR_V` 2.0e-4, `W1_FLOOR_G` 2.0e-5, `MASS_FLOOR`,
  `PLAT_FLOOR`, the Roache floors, `FS` — **carried over byte-identically. Not one
  is touched.**

**5. LADDER.** Unchanged: `c/m/f`, `r = 2`, Roache floors imported from
`scripts/roache_triple.py`.

**6. DECOMPOSITION SEED.** Unchanged. **No solver runs under this document.**

**7. CRITERIA.** In this order, and the order is **registered, not an
implementation detail** (§18.4 clause 5):
(i) strict completion (rule 4) — unchanged;
(ii) **`W1_T` IS READ AND REPORTED**;
(iii) `C_TRANSPOSE` — a refusal here is a genuine ordering defect;
(iv) station selection by §4's rule;
(v) `C_PROFILE` and the remaining gate-(1) clauses;
(vi) Roache classification, then band.

**8. COST.** **0.00 core-min of solver time** — no case is run. Grading pass
**< 0.5 core-min [ESTIMATED]**, `ranks` 1. CAP **2.0 core-min**, hard.

**9. ABSENT REGISTRY.** Not applicable in its usual form and **that is the
hazard**: the fields are **present and complete**. What must be ABSENT at the
freeze is any **T16c graded output**, and the supervisor must confirm that in the
committing invocation under a live planted control.

**10. AUTHORISATION.** Authorises **no grading**. Binding only on the
supervisor's freeze commit, with the comparator hashed against its committed blob
before any grading.

---

## 2. `C_TRANSPOSE` — the planted control §18.4 clause 4 requires

**REGISTERED: the ordering guard is admitted only if a PLANTED transposed
ordering is shown to fire it.** The comparator's selftest must forge a
transposed-ordering case, read it through the **real** reader, and assert **both**:
1. the guard **refuses** (exit 2), and
2. the **recovered value is within `0.1` of `-1.0`** — the signature is
   **measured and reported**, not asserted.

Clause 2 is the addition. `analyse_t16.py:922` already forges the transpose and
checks only the exit code, **so the −1.0 in §18.2 has never actually been read
back off an instrument.** A guard whose signal has never been measured is sized
against a number nobody has seen.

**And the negative arm:** the untransposed forged case must return
`|slope/(-dT) - 1| < 0.5` and **not** fire. Both arms, or the guard is not
admitted.

---

## 3. `W1_T` MOVES UPSTREAM — the ordering defect, with the line numbers

**MEASURED in the frozen file:** the `C_ORDER` refusal is at
`analyse_t16.py:573-576`. `W1_T` is first computed at `analyse_t16.py:582`.
**Nine lines.** The witness that produced verification's entire diagnosis sits
**nine lines below** the guard that made it unreachable.

**REGISTERED: `W1_v`, `W1_g` and `W1_T` are computed and PRINTED before any
gate-(1) clause can refuse.** They are **reported unconditionally**, including on
a refusing run, because §18.3's diagnosis was only available from them.

*This is `D576`'s shape and it is named as such:* **a diagnostic downstream of a
guard that fires on physics is a diagnostic you will lose exactly when you need
it.** The general form — *the most informative reader runs before the guards, not
after* — is **offered upward and NOT ruled here.**

---

## 4. THE STATION-SELECTION RULE — frozen before the station is known

**`[lab-attributed]`, the supervisor's ruling, recorded as theirs and disclosed
so it can be overturned.** Neither moving the station by hand nor changing the
referent by hand is permitted: the first picks a station that happens to work,
the second picks a yardstick after seeing the current one fail. **Both are
choosing after seeing the answer, which is what rule 2 exists to prevent.** So a
**rule** is frozen instead, and the station falls out of it.

**METRIC.** `W1_T(j)` — T16's **own** streamwise temperature-development witness,
`analyse_t16.py:340-354`: the max over the registered witness offsets of
`max_i |T(row j+k)_i − T(row j)_i| / dT`. **Not a new metric.**

**THRESHOLD.** `W1_T(j) <= 1.0e-06`, the registered `W1_FLOOR_T`
(`analyse_t16.py:116`). **Not a new number.** *Using T16's own floor is what keeps
this from being a yardstick chosen for the occasion.*

**SELECTION.** The graded station is the **smallest** `j` in the candidate set
satisfying the threshold **on the FINE level**, then applied to the coarse and
medium levels **by physical coordinate `y/b`, not by index**.

**CANDIDATE SET.** Every interior row `j` for which all registered witness
offsets lie inside the domain — frozen **as that formula**, not as a list, so it
is level-independent.

**TIE-BREAK.** None is possible: "smallest `j`" under a strict inlet-to-outlet
scan is unique. Stated because a rule with an unreachable tie-break clause
invites one to be invented later.

**THE THREE-LEVEL CONSISTENCY CLAUSE — not in the ruling, and registered because
without it the triple is meaningless.** The selected `y/b` must **independently**
satisfy `W1_T <= 1.0e-06` on **all three levels**. If the station were selected
per level, the Roache triple would compare **three different physical
locations**, and its observed order would be an artifact of the station drifting.
**If any level fails at the selected `y/b`, the rung is `NOT A RESULT`.**

**THE UNREACHABLE BRANCH — registered explicitly, because a criterion with no
failure branch is not a criterion.** **If no `j` in the candidate set satisfies
the threshold, T16c returns `NOT A RESULT`, the station is NOT relocated, the
threshold is NOT loosened, and the candidate set is NOT widened.** The recorded
reason is then the one §18.4 clause 3 already fixed: **the registered referent
does not describe this solve's regime** — and the honest consequence is that the
*case*, not the comparator, needs changing. That outcome is **accepted in
advance and without appeal.**

### 4.1 Why the referent is not replaced — the rejected alternative, recorded

Substituting a Graetz-class entry-region solution would discharge the finding and
is **rejected**: T16's values are known (§0), so choosing a referent now is
choosing it **after seeing which one failed**. Keeping the exact referent and
registering a rule that decides *where it is valid* leaves the referent exact
wherever it is applied. **Recorded as rejected rather than omitted.**

---

## 5. THE `sha256` PIN — a moved gate stops the comparator structurally

**REGISTERED:** the comparator loads
`/home/ubuntu/Certonomous/verification/runs/T-family/T16_runs/T16_registered.json`
**by absolute path** and **REFUSES (exit 2)** unless its SHA-256 is

    aead91aaab8480f6a4321a3d9eb01536d9ceb4cbfb7a3774426cea608ae72845

**(9,179 bytes, measured by this lane in the drafting invocation; the supervisor
must re-take it in the committing invocation — a digest taken now is not
transferable to a later commit.)**

Adopted from the T19b construction. **The point is structural, not
administrative:** every carried-over floor in §1 line 4 lives in that file, and a
promise that they are unchanged is worth less than a digest that stops the run if
they are not. **A moved gate then fails closed instead of grading quietly.**

---

## 6. WHAT IS REPLACED, AND WHAT IS CARRIED OVER

**REPLACED — exactly one clause:** `analyse_t16.py:573-576`, the single
`C_ORDER` refusal, becomes `C_TRANSPOSE` (§2) + `C_PROFILE` (§1 line 4) with
`W1_T` moved above both (§3). **Why:** it evaluated *"does the station-row T match
a linear profile to within 1e-06?"* while publishing *"a transposed cell
ordering"* — two propositions at one tolerance, six orders apart (§18.2).

**CARRIED OVER, unexamined and byte-identical:** every other gate, threshold,
band, cap and label in `T16_PREREGISTRATION.md`; all three solves; the Roache
floors and `FS`; `W1_FLOOR_V/G/T`; `MASS_FLOOR`; `PLAT_FLOOR`; `C_MASS`, `C_REV`,
`C_CONV`, `C_PLAT`, `C_G`; the completion rule; the cost basis.
**`mark_done_t16.py` is not touched** — T16b already fixed its blob at
`efcf7852` and **zero frozen bytes change under this document either.**

---

## 7. THE ID — `T16c`, and it does NOT consume a top-level number

`T16b_PREREGISTRATION.md` exists, so `c` is the next letter. **A sub-letter is
correct here and a plain number would be wrong:** T20 §0.3's rule, which T21 §0.3
restates, is that sub-letters mark **follow-on arms of an existing rung** while a
**new subject** takes the next free top-level number. **T16c is the same case,
the same solves and the same referent, with one clause repaired** — an arm, not a
subject.

**Re-derived from the MAXIMUM, never a count**, in the drafting invocation: the
maximum existing top-level `T` across `docs/campaigns/T-family/` ∪
`verification/runs/T-family/` is **22**, over the set
{1,3,4,5,6,8,9,10,11,13,14,15,16,17,18,19,20,21,22} — **nineteen ids with a
maximum of 22, which is again why a count is not the rule.** **T21 and T22 are
this lane's, provisional and uncommitted.** **T16c consumes none of it**, and the
supervisor must re-derive at the committing invocation regardless.

---

## 8. COST — rule 12

**No solver runs.** Solver cost **0.00 core-min [MEASURED — the runs are already
on disk and complete]**. Grading pass **< 0.5 core-min [ESTIMATED, not
measured]**, `ranks` 1, on three cases of 20/40/80 station rows. **CAP 2.0
core-min, hard**; an overrun stops the grading and does not get a new budget.
USD: **negligible, DERIVED NOT MEASURED**, at $0.0513/core-h.

**Calibration owed at completion** per rule 12: the grading pass is the actual,
compared against the < 0.5 estimate, appended to `docs/COST_CALIBRATION.md`.
*This rung's calibration value is small and its honesty value is not: it is a
zero-new-compute rung whose entire cost is instrument time.*

---

## 9. WHAT THIS RUNG DOES NOT DO

- **It does not relax the 1e-06 tolerance.** §18.4 clause 2. If a later reader
  finds themselves loosening it, **that is the signal to stop, not to proceed.**
- **It does not compute a T16 graded value before the freeze.** None exists.
- **It does not move a gate, band, cap or label** other than the one clause §6
  names.
- **It does not write the comparator, the builder or a launcher.** Separate acts
  under separate review; the supervisor reads measurement-script diffs **as
  diffs**, personally.
- **It does not rule** on §3's "informative readers run before guards" proposal.
- **It files nothing anywhere** (rule 7).

---

## 10. DECLARED OMISSIONS

1. **The three solves are carried over UNEXAMINED.** T16c inspected the
   comparator, not the fields. If a solve is defective, this rung would not know.
2. **`W1_T`'s three values are not in hand** (§0.1). The rung is unblind on the
   **ratio** `~1050×`, not on the triple.
3. **The station is not known at freeze — by construction.** The rule is frozen;
   which `j` it selects is not, and cannot be, without computing it.
4. **The 5,800× margin in §1 line 4 rests on the observed physics staying near
   −8.6e-05.** A different case could sit closer to −0.5, and the threshold would
   then need re-deriving **for that case, in its own registration** — not here.
5. **No claim about the entry region.** T16c says where the linear referent is
   valid, **not** what the solution does where it is not.

---

## 11. WHY THIS LANE DID NOT FREEZE IT

The commissioning brief said **"Freeze it, or freeze nothing."** This lane is
returning the third option, which the charter already provides: **the supervisor
freezes it.**

1. **`SUPERVISION_CHARTER.md` §3 check 4 is personal and non-delegable.** A lane
   that commits its own registration has performed the supervisor's check on the
   supervisor's behalf and called it done — the exact substitution
   `CLAUDE.md` rule 9 names, and the supervisor stated the rule themselves two
   messages earlier: *"check 4 is mine."*
2. **This lane's standing instruction is `DO NOT COMMIT`**, from the brief that
   opened its work. No later agent message lifts it.
3. **The document is stronger unfrozen for one more read**, because §0.1 carries
   **two corrections against the brief that commissioned it**. A registration
   frozen by the same lane that found the errors has had one reading, not two.

**The dilemma is false in one direction only, and this is the honest half:** the
brief was right that *a fifth admission that T16c is owed beats a registration
pretending to decide something it has not.* **T16c decides.** The station rule of
§4 is complete, its failure branch is registered, its metric and threshold are
carried from T16's own file, and nothing here awaits a further finding. **It is
ready to freeze. It needs a supervisor to do it.**
