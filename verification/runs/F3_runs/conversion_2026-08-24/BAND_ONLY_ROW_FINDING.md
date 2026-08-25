# What a BAND-ONLY row buys: it is a CITABLE VERDICT and it is NOT a CREDENTIAL

**Written 2026-08-25 by a cfd lab-lane under cfd-supervisor. ZERO COMPUTE: no solver was
started, no case directory was created, no file under `runs/` was touched, and no successor
pre-registration was drafted.**

**Tasked** to establish, before drafting any successor to F3, what a band-only row with no
grid triple actually produces under standing rule 5 and under F3's own frozen text — the task
being gated on that answer. The answer stops the task, which was the outcome the brief
explicitly allowed for. This document records the finding so the refusal is auditable and so
the next reader does not re-open it as an oversight.

---

## 1. The short answer, in two limbs that come apart

| question | answer | authority |
| --- | --- | --- |
| Does a band-only row produce a **citable verdict**? | **YES** — `PASS` or `GATE FAIL`, annotated | frozen §4.4; frozen `grade_f3.py` `apply_gate`; an executed precedent already on disk |
| Does a band-only row become a **credential**? | **NO** — not under F3's frozen §9 | §9's `PASS` bullet is conditioned on a CONVERGING triple, and §9 may not be re-read after compute |

**These are different properties and for these two runs they come apart.** The brief's Part 2
gate was worded on *citability* and its STOP condition was worded on *credential status*. On
the evidence those two conditions do not agree, and the conservative limb governs: **STOPPED,
no successor drafted.** The choice between them is a label decision and is referred at §7.

---

## 2. CITABLE — established from the frozen text and the frozen code, not from reasoning

### 2.1 The frozen registration says it in terms

`verification/campaign/F3_CONVERSION_PREREGISTRATION.md` (disk `git hash-object` ==
`HEAD:` blob == `774dad4684295a0bf80299ed7092e06aa4c29b18`, verified this session), **§4.4,
lines 219–221**:

> Rows carrying no triple (wedge M3.0, wedge M2.5, diamond M2.5) are graded on the band alone
> and **carry the annotation "no grid triple — no discretization-error estimate" on their
> face**; they are not presented as grid-converged.

So the frozen document does address the case, it addresses it by name for exactly the three
band-only pairs, and it says they **are graded**.

### 2.2 The frozen comparator's code path — read, not inferred

`verification/runs/F3_runs/conversion_2026-08-24/grade_f3.py`, blob `6fea2e1d` (disk ==
HEAD, verified), **lines 407–417**:

```python
def apply_gate(dev_pct, band_pct, triple):
    """Standing rule 5 order of operations. The triple can only turn a PASS or a
    GATE FAIL INTO NOT A RESULT, never the reverse."""
    band_verdict = "PASS" if abs(dev_pct) <= band_pct else "GATE FAIL"
    if triple is None:
        return band_verdict, "no grid triple -- band only, no discretization-error estimate"
    if triple["klass"] != "CONVERGING":
        return "NOT A RESULT", ...
```

**With `triple is None` the comparator returns the band verdict and an annotation.** It does
not refuse, it does not exit 2, and it does not return `NOT A RESULT`. The triple is passed as
`None` deliberately, from a `has_triple` flag carried per pair in the frozen matrix
(`grade_f3.py:530`, `:545`, `:553`, `:601`, `:616`).

### 2.3 Why rule 5 does not make it uncitable

Rule 5's clause 2 is a test **on a triple**. With no triple there is nothing to classify, so
clause 2 is not evaluated — it is not silently passed. Rule 5's own asymmetry, quoted in the
docstring above and in §4.4, is the reason this is not a loophole: *the triple can only turn a
PASS or a GATE FAIL **into** NOT A RESULT, never the reverse.* An **absent** triple has nothing
to turn. What the absence costs is stated exactly and is not nothing: **no discretization-error
estimate, and the row may not be presented as grid-converged.**

### 2.4 There is already an executed precedent on disk

`wedge/M3.0_th15/fine` is a band-only run of this same registration. It was launched (wave 5),
completed (`status: "COMPLETE"`, all six completion keys true, `core_s: 184.83`), and the
frozen comparator graded it:

| row | verdict | measured | exact | deviation | band |
| --- | --- | --- | --- | --- | --- |
| G-F3-1 / M3.0_th15 | **PASS** | 2.821769172727273 | 2.821562321277495 | +0.00733 % | ±0.5 % |
| G-F3-2 / M3.0_th15 | **PASS** | 31.931111435642887 | 32.240400182744665 | −0.9593 % | ±2.0 % |

both with `"triple": null` and `"basis": "no grid triple -- band only, no
discretization-error estimate"` — `F3_CONVERSION_GRADED.json`, `gates` section. Both are
carried in `RESULTS.md` with triple column **"single level"** and both are counted in the
published tally **5 PASS, 1 GATE FAIL, 1 NOT A RESULT, 3 PENDING**.

**So the question is not open. Two of F3's five PASSes are band-only rows.**

---

## 3. CREDENTIAL — and here the answer reverses

§9 of the frozen registration is titled *"What each outcome will mean"* and opens: *"Stated
now, so no outcome can be re-read afterwards."* Its first bullet, **lines 399–400**:

> - **PASS** on a gate whose triple CONVERGES: the 2026-07-28 claim is converted and becomes
>   a credential.

**The credential is conditioned on a CONVERGING triple.** §9 assigns no credential meaning to
a band-only PASS — it does not deny one either; it is silent. Three things close that silence
in the restrictive direction, and none of them is this lane's preference:

1. **§9's own preamble.** The meanings were stated in advance precisely so that no outcome
   could be re-read once seen. Reading "PASS on a converging triple → credential" as "any PASS
   → credential" is a widening performed **after** two band-only PASSes are on the record. That
   is the manoeuvre §9 exists to prevent.
2. **Standing rule 2.** After first compute, gates are closed and addenda may not alter a gate,
   threshold, cap or **label**. Credential status is a label. F3 has had first compute.
3. **§4.4's own restriction.** A band-only row is *"not presented as grid-converged"* and must
   carry its annotation *"on its face"* — a standing presentation constraint that travels with
   the row wherever it is cited.

**Nothing in lab-wide law supplies the missing grant.** `VERIFICATION_CHARTER.md` mentions a
credentials wall (§6 scope, lines 786, 830) but nowhere makes a grid triple a precondition for
a credential, and nowhere permits a single-level row to become one.
`docs/standards/MESH_STANDARD.md` §7.0 governs whether **one mesh is admissible** — a mesh
quality question, not a credential question — and does not speak to this.
`verification/credentials/` currently holds only the ansys register.

**So the restriction found here is F3's own §9, not lab-wide doctrine.** That precision
matters: this finding does not establish that the lab may never ship a single-mesh credential.
It establishes that **this registration did not authorise one**, and that a successor
inheriting §9 unchanged would not either.

---

## 4. A wrong inference this lane made and CORRECTED, recorded so no one repeats it

It is tempting to carry AMENDMENT 1's reasoning about the withheld cone M3.0/θc12 pair across
to these two runs. **It does not transfer, and this lane checked rather than assumed.**

AMENDMENT 1 (prereg lines ~636–645) argues that adding one fine cone M3.0 run *"converts
nothing. It would produce exactly the class of row whose deficiency is the thing being
repaired."* That holds **because the cone M3.0 pair's specific §1 defect is the absence of
refinement evidence** — §1's table: *"the M3.0 pair has **no fine mesh at all** — it was graded
PASS on a medium mesh."* A single added level cannot cure a missing-refinement defect.

**The two runs at issue are not in that position.** The 2026-07-28 record
(`verification/campaign/F3_supersonic_exact_theory.md`) shows both pairs already had fine
meshes:

- **wedge M=2.5, θ=10°** — medium (7,200 cells, 18.9 core-s) **and fine (28,800 cells, 148.1
  core-s)**; §1's table records **no** refinement weakness for the wedge pressure gate.
- **diamond M=2.5, ε=5.0°** — coarse (2,000), medium (8,000) **and fine (32,000, 189.8
  core-s)** — a full three-level set; §1's table records no weakness for the diamond gate.

So for these two pairs the §1 defect is **the missing pre-registration alone**, and a fine run
under a frozen band **does** cure it. Firing them would repair the §1 defect and would **still**
not yield a §9 credential, because **§9 keys the credential on the triple, not on the defect**.
That is the sharp point of this finding: for these two pairs, **§1's defect axis and §9's
credential axis come apart**, and the brief's assumption that they move together is what fails.

*(Noted in passing, acted on by nobody: the old diamond M2.5 three-level set is non-monotone —
0.013428 → 0.013395 → 0.013406 — so a re-run triple there would plausibly grade `OSCILLATORY`
and therefore `NOT A RESULT` under rule 5, exactly as G-F3-1/M2.0 did. This is an observation
about the old record, not a prediction registered against anything.)*

---

## 5. What band-only waves have been buying, quantified

Of F3's **2,005.06 core-s** launched, **184.83 core-s (9.2 %)** went to `wedge/M3.0_th15/fine`,
the one band-only run that fitted inside the cap. It bought **two `PASS` rows that count in the
published tally and are not credentials under §9.** That is what a band-only wave buys: a
graded, annotated, citable row that carries no discretization-error estimate and converts no
prior claim into a credential.

**This is not a criticism of §6's matrix.** §6 spent its triple budget on the three pairs the
conversion existed for and bought breadth cheaply at the other three. The finding is that the
breadth purchased is **verdict breadth, not credential breadth**, and F3's own §9 says so.

---

## 6. Consequence for the successor, and why none was drafted

The ruling this lane was given fixed the successor's form: **carry F3's frozen bands over
unchanged, re-derive nothing, the only new content being a new cap and the two run
directories.** That form is correct on the band-contamination objection and this lane does not
dispute it — carrying the bands over eliminates the objection rather than arguing against it.

**But that same form carries §9 over unchanged too.** A successor whose only new content is a
cap and two run directories inherits the credential clause verbatim, and therefore its two
band-only rows would be citable, annotated, non-credential rows — for **~6.4 core-min** — that
by the brief's own requirements *do not alter F3's tally, do not regrade F3's closed rows, and
leave F3's three rows `BLOCKED`/`PENDING`.*

**Granting credential status to a band-only PASS would require a successor §9 that differs
from F3's.** That is legal in a new registration before its first compute — but it is a
**label** decision under rule 2's frozen quartet, it is outside the ruling this lane was given,
and it is above a lane's level. **It is not taken here, and no reason to proceed was
manufactured.**

---

## 7. The decision referred to cfd-supervisor, stated as a choice and not as a recommendation

1. **Accept a non-credential row set.** Fire the two runs under a successor that carries §9
   over unchanged, spending ~6.4 core-min for two citable annotated rows that convert nothing.
   Legitimate, cheap, and honest about what it produces.
2. **Write a successor §9 that grants credential status to a band-only PASS**, defended on its
   own terms before its own first compute. A label decision, above a lane.
3. **Run full grid triples for the two pairs** — the only route to a §9-style credential —
   which is a materially larger scope item than the one costed in the brief and was not costed
   here.
4. **Do nothing.** F3's three rows stay `BLOCKED`/`PENDING` as
   `PENDING_ROWS_DISPOSITION.md` leaves them, which no option above changes.

**None of these is taken by this lane.**

---

## 8. Secondary observation, stated narrowly and deliberately NOT overstated

**This is a documentation gap, NOT a freeze breach, and it does not bear on §1–§7.**

§8 of the frozen registration lists `grade_f3.py` at sha256
`fe9fe6df…a847d9003e6ab05c129585cfdff04f87`. The file that actually ran, and that is on disk
and at HEAD today, is sha256 `e7602996cb75fd61e95a51a85910b24cf0a675b6eee05e8b7c3d2e5ae0b88570`
(blob `6fea2e1d`) — repaired by **AMENDMENT 2** under §2d.1.

**The grade is defensible.** §8's operative mechanism is a **blob** check against the commit
passed as `--prereg-commit`, not a comparison against the §8 literal;
`F3_CONVERSION_GRADED.json` records `prereg_commit: "48b7812a"`, `sha256: e7602996…`,
`frozen_match: true`, and `RESULTS.md` discloses the re-freeze on its face: *"Grading path
re-frozen at `48b7812a`, blob `6fea2e1d`."*

**What is genuinely missing** is only this: AMENDMENT 2 does not record the post-repair sha256
anywhere in the pre-registration, so a reader who hashes `grade_f3.py` against §8's literal
gets a mismatch with no in-document pointer to the explanation — and AMENDMENT 1, written
earlier, asserts at line 557 that *"the §8 grading-path sha256 pair … stand exactly as"*
frozen, which the later repair overtakes. Frozen files are not edited (rule 6); the fix, if the
supervisor wants one, is a further dated addendum recording the post-repair sha256. **Flagged,
not taken.**

---

## 9. What this lane did NOT verify

- **Whether the successor's two runs would in fact PASS.** Nothing was run and no gate quantity
  was observed. No prediction is offered and none should be read into §4's remarks about the
  old record's numbers, which are quotations from a committed 2026-07-28 document.
- **Whether option 3's full triples fit any budget.** Not costed here.
- **Whether any other campaign in this lab relies on band-only rows as credentials.** Not
  swept; this document establishes the F3 position only, and §3 states plainly that the
  restriction found is F3's own §9 rather than lab-wide law.

---

## 10. Cost calibration (standing rule 12)

**No compute was incurred by this lane: 0.0000 core-minutes, $0.00.** No row is added to
`docs/COST_CALIBRATION.md`, because no process consuming compute completed — a calibration row
for zero compute would place a fictitious measurement in the ledger. F3's own calibration
stands at rows **C-66** / **C-68**, ratio **1.1290** over launched runs only, and is not
restated here as new.

---

## 11. Verdict

**Part 1 answers, and the task stops on the second.**

| question | answer |
| --- | --- |
| band-only row → citable verdict? | **YES** — `PASS` / `GATE FAIL`, annotated, not grid-converged |
| band-only row → credential under F3 §9? | **NO** |
| successor drafted? | **NO — STOPPED at the brief's own instruction** |
| F3's three rows | unchanged: **`BLOCKED`** as a launch request, **`PENDING`** as graded cells |

No frozen file was edited to record this. Nothing was sent, filed or submitted.
