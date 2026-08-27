# T9a-R1c (`W1c`) — FLOOR DEMONSTRATION on the layered wall's interface temperature

**Version 1.0 — DRAFT. NOT FROZEN. NOT COMMITTED. NOT ENQUEUED. NOTHING HAS RUN.**

Written 2026-08-27 by a heat-transfer lane at the supervisor's direction.
Decisions `[lab-attributed]`. Verdict vocabulary fixed by `CLAUDE.md` rule 1.

**This document is a proposal for the supervisor's personal checks 1 and 4
(`SUPERVISION_CHARTER.md` §3): the diff read of every measurement script, and
the pre-registration committed before compute. Neither is delegated and neither
has happened. Until they have, nothing here is registered.**

Repo HEAD when drafting began: `ffed68000f3cce03f8d2e4a114e6fb3e10d11179`.
HEAD when drafting finished: `018aab8ccc9bfcb428e9e0c1cf598f92a3c62981` — peers commit constantly and this document
was written across several of their commits. **The five sibling HEAD blob shas in
§8.1 were RE-VERIFIED at the later HEAD and are unchanged**, so the check-1 diffs
are against baselines that did not move under them.

---

## 0. What this rung is, why it exists, and what it may not claim

### 0.1 The predecessor and the ruling

`T9a-R1b` (`W1b`) registered a **Roache triple** on the layered-wall interface
temperature, measured that triple **`EXACT`** (`e21` −2.842e-13 K, `e32`
3.240e-12 K), and graded its row **`PASS`** on a **floor exception to standing
rule 5** frozen in its pre-registration before compute.

`VERIFICATION_CHARTER.md` **§2g** (v1.16, 2026-08-27T19:51:42Z) **REFUSED that
exception**:

> **"A pre-registration fixes the gate, threshold, cap and label FOR ITS CASE.
> It has no power to disapply a standing rule, and an exception to one is void
> however early it was frozen."**

The decisive ground is that rule 5's gate is **one-way** — *"the gate can only
turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse"* — so an
exception yielding `PASS` where rule 5 yields `NOT A RESULT` **runs the gate
backwards**. The heat-transfer supervisor adopted the ruling at
2026-08-27T20:28:10Z. **W1b's R1 row is `NOT A RESULT` on its Roache limb, and
its measurement is `REPORTED` beside it (D534's row class).**

### 0.2 The diagnosis, which is what makes a successor possible

§2g.3 does not dismiss the physics; it names the instrument:

> **THE DIAGNOSIS: the wrong instrument was registered.** Where the
> discretisation error is below the registered floor at every level, a Roache
> triple **has nothing to measure** — there is no order to observe and no GCI to
> quote. Registering a triple and then excepting the triple gate is registering
> the wrong instrument and patching it.
>
> **Rule 5 refuses to compute an ORDER from nothing. It does not say the VALUE
> is worthless.**

### 0.3 The claim this rung makes — exactly this, and no more

> **The discretisation error in `T_i1` is below `X` = 1.0e-04 K at 35 cells.**

This is a **strictly weaker claim than grid convergence** and it is the claim
the evidence supports. Its gate can return a verdict on its own pre-registered
threshold **without touching rule 5**, because it never computes an observed
order and never asserts convergence.

**A PHRASE THAT WAS IN THIS DOCUMENT AND HAS BEEN STRUCK, recorded because a
silent deletion is worse than the error.** Version 1.0 of this registration ended
that sentence *"…so the answer does not depend on the mesh at the resolution that
matters."* The phrase was taken **verbatim from `VERIFICATION_CHARTER` §2g.3**,
quoted approvingly in the supervisor's brief and in this lane's reports, and
copied by all of us without being tested. **`VERIFICATION_CHARTER` §2h.4(5)
(v1.17, 2026-08-27) narrowed §2g.3 against verification's own drafting and struck
it:** a floor demonstration establishes the error **at the meshes measured** and
says nothing about finer ones, because establishing behaviour **across** meshes
is what a Roache triple is for — and this instrument deliberately has none. **The
phrase would have smuggled back in exactly the claim the instrument was built to
avoid making.** It is removed from every artifact of this rung (§8.3).

### 0.4 What this rung is NOT, stated so nobody overstates it later

- It is **not** a grid-convergence study. No observed order, no GCI, no
  Richardson extrapolate and **no Roache triple is computed anywhere in the
  comparator** (§2a, and the executable guard `C_NOTRIPLE` in §4.3).
- It does **not** re-grade, reopen or amend T9a or T9a-R1b. Those records stand.
- It claims nothing about **fins** (T9a's F rows), about **interface 2** as a
  graded quantity, about **transient** conduction, or about **2-D/3-D**.
- **Capability-grid cell:** conduction × laminar × 1-D steady, layered wall —
  the parent's cell. Whether this rung counts toward that cell is the
  supervisor's call and the grid is not amended by this document.
- It authorises no launch. **Enqueueing is not authorisation.**
- It authorises no send. **SUBMISSIONS REMAIN PARKED** (rule 7).
- **And it is not a corroborating second measurement of W1b — see §0.6, which
  is the sharpest of these and is given its own subsection because a later
  reader is most likely to get exactly that one wrong.**

### 0.5 The rung id, and why `W1c`

`T9a` → `T9aD`, `T9aH`, `T9aR1b` is the family's successor convention (rung ids
carry lowercase). The successor to `T9a-R1b` is **`T9a-R1c`**, run root
`verification/runs/T-family/T9aR1c_runs/`, cases `W1c_c` / `W1c_m` / `W1c_f`.
Checked for collisions across the repository: **no `T9aR1c` and no `W1c` exists
anywhere**, and `T_FAMILY_INDEX.md` carries no such rung.

**The case names are new even though the case inputs are identical to W1b's**,
and the reason is a rule and not a preference: standing rule 4's **age guard**
dates a run from the case's own `0/T`, and both the guard and the launcher
**REFUSE a case directory that already holds a `0/` or a numeric time
directory** — W1b's do. A rung that reused W1b's directories could not evaluate
its own completion rule.

### 0.6 THIS RUNG IS RE-INSTRUMENTATION, NOT CORROBORATION — and the registration forecloses the mistake in advance

**THIS IS NOT A FRESH PREDICTION AND IT MUST NOT BE READ AS ONE. THE ANSWER IS
ALREADY KNOWN.**

The cases are byte-identical in physics to W1b's: the same parent blobs at the
same T9a freeze sha, the same single `laplacianSchemes` line, the same solver,
the same iteration count, serial, deterministic. **`W1c_c` will reproduce
2.899e-12 K.** No one involved is in doubt about that, and a document that
presented this rung as an open question would be misdescribing it.

Rule 2's freeze therefore proves something **narrower than usual here**, and this
section states exactly what, in both directions, so that neither can be quietly
widened later.

**WHAT THIS RUNG CLAIMS:**

- that the **CORRECT INSTRUMENT** is now registered for a measurement the lab
  already holds — a floor demonstration, which is the instrument the evidence
  supports, in place of a Roache triple, which is the instrument `VERIFICATION_
  CHARTER` §2g found had nothing to measure;
- that the measurement **clears a threshold fixed before this instrument
  existed**, from numbers registered by T9a before W1b was built (§3.3);
- that the threshold **discriminates** — the parent's own scheme fails it at
  this level, measured, at 5.43e-03 K against `X` = 1.0e-04 K.

That is **§2g.3's prescribed remedy in its own terms**, and it is why the rung
is worth building and worth its 0.002667 core-min.

**WHAT THIS RUNG DOES NOT CLAIM, AND A LATER READER MAY NOT CITE IT FOR:**

- **NOT independent confirmation of W1b.** It is the **same measurement,
  re-instrumented** — not a second, corroborating measurement of the interface
  scheme. Two runs of a deterministic case on identical inputs are one
  measurement reported twice.
- **NOT a prediction that could have failed.** §7's predictions are registered
  and each can lose, but they are predictions about a number this lab has
  already seen; they are recorded for discipline and for the calibration ledger,
  not offered as risk.
- **NOT new physical evidence.** No physics, mesh, scheme, solver or referent
  moved. Only the instrument did.
- **NOT a second entry anywhere the lab counts measurements.** If W1b and W1c
  ever appear in the same census, they are **one** case, and the capability grid
  is not amended by this document (§0.4).

**Why this is written into the registration rather than left to the results
record.** A successor mistaking re-instrumentation for corroboration is exactly
the flattering error this family is on notice for — it converts one measurement
into two without anyone deciding to, and it is easiest to commit long after the
people who knew are gone. **The only reliable guard is that the registration
forecloses it in advance**, before there is any result to be flattered by. This
subsection is that foreclosure and it is frozen with the rest of the document.

---

## 1. The referent — derived by two routes, cross-checked against four numbers this lab did not recompute

`exact_t9aR1c.py`. The problem is steady 1-D conduction through a three-layer
plane wall with piecewise-constant conductivity and Dirichlet faces; the exact
solution is **piecewise linear** and carries one flux.

| layer | `L` [m] | `k` [W/mK] |
|---|---:|---:|
| 1 | 0.05 | 0.80 |
| 2 | 0.10 | 0.04 |
| 3 | 0.02 | 16.0 |

`T_hot` 350 K, `T_cold` 300 K, interfaces at x = 0.05 and 0.15 m.

**Route A — closed form.** `R_tot = Σ L_i/k_i`; `q = ΔT / R_tot`;
`T_i1 = T_hot − q L_1/k_1`; `T_i2 = T_i1 − q L_2/k_2`.

**Route B — independent.** The two interface temperatures are the unknowns of a
**2×2 linear system** built from flux continuity, solved by **general Gaussian
elimination with partial pivoting**. Route B never forms `R_tot`. A dropped
layer, an inverted reciprocal or a sign error moves route A and does **not** move
route B. **Required to agree to 1e-12 relative or the module REFUSES.**
Measured: **3.41e-14**.

**The external cross-check (constraint 5 of the brief, T18/T19 discipline).**
Both routes are computed here, so their agreement proves arithmetic, not
provenance. The provenance check is against **rung `T9a`**, whose numbers are
**hard-coded from `docs/campaigns/T-family/T9a_RESULTS.md` §1 table and §1.1**:

| registered by T9a | value | derived here | \|difference\| |
|---|---:|---:|---:|
| `T_i1` | 348.781082 K | 348.781082398830 | 3.99e-07 |
| `q` | 19.502682 W/m² | 19.502681618723 | 3.81e-07 |
| layer-1 drop | 1.218918 K | 1.218917601170 | 3.99e-07 |
| layer-3 drop | 0.024378 K | 0.024378352023 | 3.52e-07 |

**Tolerance 1e-06 absolute, and the tolerance is the source's own precision** —
T9a states these to six decimal places. It is not a tolerance chosen so the
check passes. Disagreement is **exit 2**, never a note.

**The document says what the four numbers are not.** They are not four
independent facts: the layer-1 drop is `T_hot − T_i1` by definition. What the
extra two buy is **measured, not asserted** — a selftest arm perturbs layer-3
`k` by 1e-5 and shows the layer-3 drop moves **2.437e-07 K** while `T_i1` moves
only **5.943e-09 K**, so the layer-3 cross-check is the sensitive one for a
layer-3 defect that the `T_i1` check alone would miss.

**Derived referent values used by the gate:**
`T_i1 = 348.78108239882982 K`, `T_i2 = 300.02437835202340 K`,
`q = 19.502681618722573 W/m²`.

---

## 2. The registered cases (`build_t9aR1c.py`)

The physics is **W1b's, unchanged**. Every input is taken from T9a's freeze
commit `0cbaea26573924a27d489a8472fad233e198ca6d` with `git show <sha>:<path>`,
never from the working tree: `0.orig/T`, `0.orig/DT`,
`constant/transportProperties`, `system/{blockMeshDict,controlDict,fvSolution,fvSchemes}`.

**What moves against the T9a parent — one line:**
`laplacianSchemes { default Gauss linear corrected; }` →
`{ default Gauss harmonic corrected; }`. The builder **REFUSES** if the diff
against the parent blob is anything but that line (driven: a planted extra line
→ exit 2).

| case | level | parent case | cells per layer | cells | `endTime` | `deltaT` | ranks |
|---|---|---|---|---|---:|---:|---:|
| `W1c_c` | c (**graded**) | `W_c` | 10, 20, 5 | 35 | 1000 | 1 | 1 |
| `W1c_m` | m (evidence) | `W_m` | 16, 32, 8 | 56 | 1000 | 1 | 1 |
| `W1c_f` | f (evidence) | `W_f` | 26, 51, 13 | 90 | 1000 | 1 | 1 |

Solver `laplacianFoam`, serial. `blockMesh` + `checkMesh` run at build and are
recorded in `BUILD.txt`.

**CONDITION AT DRAFTING, checked and not assumed:**
`verification/runs/T-family/T9aR1c_runs/` contains the six instruments, this
rung's selftest evidence and its instrument diffs, **and no case directory at
all** — no `W1c_c`, no `W1c_m`, no `W1c_f`, therefore no `0/`, no time
directory, no `log.solve`, no `STATUS.*`, no `DONE.*`. **Zero core-minutes have
been spent in the registered tree.** Amendments to this document are therefore
legal under charter §2b limb 1 until first compute, and the condition named here
is the one to re-check before any of them.

### 2.1 The prior scratch probe, disclosed rather than absorbed

W1b's registration disclosed a scratch probe run **outside the repository** on
2026-08-26 that reproduced `T_i1` to 5.7e-14 K and 2.9e-12 K under the harmonic
scheme. **That probe, and W1b's own graded run, are both known to this lane.**
§3.2 states exactly what that knowledge was and was not allowed to touch.

---

## 2a. Standing rule 5 — the election, and it is an election about REACHABILITY, not about exemption

Registered under `VERIFICATION_CHARTER.md` **§2f**, clause by clause.

**§2f.2 — the status of the rule.**

> **This registration declares NO Roache triple. Rule 5's limb (2), the
> triple-state gate, is UNREACHABLE and NOT WAIVED. A row that cannot reach rule
> 5's gate has not passed it. The absence of a triple is a LIMITATION on what
> this rung may claim, never an exemption from the standard it is measured
> against — and §0.3's claim is written to be exactly that limited claim.**
>
> **Rule 5's limb (1) — a level not iteratively converged, or not plateaued, is
> `NOT A RESULT` — is UNAFFECTED and applies IN FULL** as gate (1) (§4.1).
> **"No triple" never means "no rule 5."**

**§2f.4 — the inadmissibility is a MODEL-FORM FACT, checkable without running
anything.** For a three-layer plane wall in steady 1-D conduction with
piecewise-constant `k`, the exact solution is piecewise linear and carries one
flux. With **harmonic** face interpolation of `DT`, the discrete face
conductance **is** the series conductance of the two half-cells, so the discrete
solution reproduces the exact solution to round-off **on every mesh that
resolves the layers**. The discretisation error therefore lies in the **null
space of the scheme's truncation error**, and a systematic-refinement triple has
nothing to measure: `e21` and `e32` are both round-off and
`p = ln|e32/e21| / ln r` is **noise divided by noise**. This is entailed by
choices already frozen — the layer table, the Dirichlet faces, and the
`laplacianSchemes` line — and a reader can verify it from those alone.

**This is a model-form fact and not a capability, budget or outcome statement.**
It is not "the mesher could not build it", not "we lacked the core-minutes", and
not "the finer level diverged".

**§2f.4's honest corollary — which case WOULD carry a triple.** T9a itself.
Under `Gauss linear corrected` the face conductivity at each interface is the
**arithmetic** mean, the interface error is O(dx) and shrinks with refinement,
and **T9a MEASURED a `CONVERGING` triple with `p` = 1.738 on exactly this
ladder**. That is a **different case**, not this one refined.

**§2f.5 — the prior triple, disclosed in full whatever it said.** A Roache
triple **was** run on this case family. `T9a-R1b` (`W1b_c`/`W1b_m`/`W1b_f` — the
same three levels, the same scheme, the same reader) returned state **`EXACT`**,
`e21` = −2.842e-13 K, `e32` = 3.240e-12 K, **no observed order defined**,
deviation 2.899e-12 K. Verification §2g refused the floor exception that graded
that triple `PASS`.

**The election is not selection by outcome.** The tell §2f.5 names is *"the
discarded arm is missing from the record"*; here it is in the record, with its
numbers, in this section. The ground for the election is §2g.3's own diagnosis
that the wrong instrument was registered — a **charter ruling**, not this team's
reading of an inconvenient result.

**§2f.6 — the mesh-family spread is a BOUND.** Row N2 reports max−min of `T_i1`
over the levels actually read. It is a bound on observed variation over the
meshes built; it is **not** an error estimate, **not** extrapolated, and it is
**never** called a GCI or an observed order. It is `REPORTED`, never graded.

---

## 3. The graded row, its threshold, and the gate

### 3.1 The rows

| row | class | quantity | graded? |
|---|---|---|---|
| **F1** | **`FLOOR_DEMONSTRATION`** | \|`T_i1` − `T_i1_exact`\| at the **coarsest** level `W1c_c` | **YES — one number, one level, one absolute threshold** |
| N1 | `REPORTED` | \|`T_i1` − exact\| at every level read | no verdict |
| N2 | `REPORTED` | mesh-family **spread** (§2f.6 bound) | no verdict |
| N3 | `REPORTED` | hot-face flux `q_hot`, relative deviation | no verdict |
| N4 | `REPORTED` | \|`T_i2` − exact\| at every level read — the interface F1 does **not** read | no verdict |

`T_i1` is read by **the parent's reader form**, unchanged through W1b: the
conductance-weighted mean of the two cells adjacent to the interface face
(`analyse_t9a.measure_wall.iface_T`).

### 3.2 THE GATE SENTENCE, verbatim, as it is registered

> **At the coarsest registered level `W1c_c`, WHICH IS 35 CELLS, the
> DISCRETISATION ERROR in the interface-1 temperature IS BELOW `X` = 1.0e-04 K:
> `|T_i1(W1c_c) − T_i1_exact| ≤ 1.0e-04 K`. PASS inside; GATE FAIL outside.
> The claim is bounded by the mesh actually run: it is a statement about 35
> cells, and about no finer mesh. It is NOT a claim that the solution is correct
> to `X`, and it is NOT a claim that the answer does not depend on the mesh —
> establishing behaviour ACROSS meshes is what a Roache triple is for, and this
> instrument deliberately has none. No observed order, no GCI, no Richardson
> extrapolate and no Roache triple is computed anywhere in the comparator.**

**This wording is itself a registered condition, not prose.** `VERIFICATION_
CHARTER` §2h.4(4) requires the registered sentence to read *"the discretisation
error is below X at N cells"* and **never** *"the solution is correct to X"* —
because **a floor demonstration WORDED as a continuum claim IS a continuum claim
and §2f.3 catches it.** `N` is stated explicitly (35). §2h.5 is express that no
machine check in this rung discharges it: **the AST guard proves the ABSENCE OF A
TRIPLE, not the wording of the claim, and those are different propositions.**

### 3.3 HOW `X` WAS CHOSEN, AND THE DISCLOSURE THAT MATTERS MOST IN THIS DOCUMENT

**The hazard, stated first and in the open.** The lane that wrote this document
**knew W1b's measured 2.899e-12 K before choosing `X`.** That is precisely the
condition rule 2 exists to prevent, and no amount of care makes the knowledge go
away. What can be done is to fix `X` from numbers that were registered **before
W1b was built**, to state them, and to show the arithmetic so a reader can check
independence rather than take it.

**`X` is fixed by a window with three walls, all three of them from T9a's own
record (registered 2026-08-20/22):**

| wall | value | source | what it fixes |
|---|---:|---|---|
| **upper — the decision magnitude** | 9.2e-04 K | T9a's registered R1 **GCI band, 0.92 mK** (`T9a_RESULTS.md` §1 table) | the size of error the lab itself already fixed as **deciding** this quantity. `X` must be below it or the demonstration decides nothing. |
| **discrimination** | 5.43e-03 K | T9a's **coarsest** level under the parent's `Gauss linear corrected` deviates **−5.43 mK** (`T9a_RESULTS.md` §1.1: the three levels are off by −5.43 / −3.33 / −2.41 mK) | `X` must be far below it, so that **the parent's own registered scheme GATE FAILS this gate at this very level.** |
| **lower — referent precision** | 1.0e-06 K | T9a states the referent to **six decimal places** (348.781082 K), so the cross-check is good to ~1e-06 K | `X` must be **above** it: a demonstration may not claim more precision than the referent it is checked against carries. |

**`X` = 1.0e-04 K is the round decade one order below the decision magnitude,
inside the window [1e-06, 9.2e-04] K.** It sits **9.2× below** the decision
band, **54.3× below** the discriminating magnitude, and **100× above** the
referent precision floor.

**The physical argument — what magnitude of temperature error would change a
conclusion drawn from this case.** The layer-1 temperature drop this row sits
inside is **1.218918 K**; the wall's total drop is **50 K**. `X` is 8.2e-05 of
the local drop and 2.0e-06 of the total. Downstream, on the DC-cooling spine
this rung is the conjugate entry to, the interface temperatures it feeds carry
**design margins of order 1 K** and **instrument resolutions of order
0.01–0.1 K**. `X` is at least three orders below anything a DC-cooling
conclusion could turn on, and one order below the tightest band this lab has
ever set on this quantity. **Both arguments — the lab-internal decision
magnitude and the downstream engineering magnitude — agree that 0.1 mK is
safely non-decisive, and the lab-internal one is the tighter by about four
orders, so it is the one that binds.**

**The falsifiability statement, which is the test of independence a reader can
actually run.** `X` is not a threshold drawn around a known answer:

- had this case returned **5e-04 K**, `X` = 1.0e-04 K would **GATE FAIL** it;
- had it returned **2.9e-05 K**, `X` would **PASS** it;
- the parent's linear scheme, at this level, returns **5.43e-03 K** and
  **GATE FAILS** by 54×.

**THE ARGUMENT THAT ACTUALLY DISPOSES OF THE CONCERN, AND IT IS ARITHMETIC
RATHER THAN PROVENANCE: THE VERDICT IS INSENSITIVE TO `X` ACROSS THE ENTIRE
DEFENSIBLE WINDOW.** Everything above defends *where the decade came from*, and
a reader is entitled to remain unsatisfied by any account an author gives of
their own state of mind. This does not depend on one. The measurement this rung
will produce is known — W1b's **2.899e-12 K**, and §0.6 says why it is known —
and it sits far below **every** candidate value in the window:

| candidate `X` | what it is | `X` / measured | orders of margin | verdict |
|---|---|---:|---:|---|
| 1.0e-06 K | window's lower wall (referent precision) | 3.449e+05 | **5.54** | PASS |
| **1.0e-04 K** | **`X` as registered** | 3.449e+07 | **7.54** | **PASS** |
| 9.2e-04 K | window's upper wall (decision magnitude) | 3.174e+08 | **8.50** | PASS |

**Any `X` anywhere in [1.0e-06, 9.2e-04] K yields the identical verdict**, so
the choice of decade **cannot** have been fitted to the answer in any way that
changes the outcome. That is checkable by a reader with arithmetic, and it does
not rest on this lane's word about its own state of mind.

**How far outside the window that invariance extends, since the stronger
statement is free.** The verdict flips only for `X` ≤ **2.899e-12 K**, which is
**345× below W1b's own registered round-off floor of 1e-09 K** and 3.4e+05× below
the referent's precision. **No `X` that could be defended at all flips it**: an
`X` below the round-off floor would be gating on bits, and an `X` below 1e-06 K
would claim more precision than the referent carries.

**And the DISCRIMINATION is invariant across the same window.** The parent's
linear scheme measures 5.43e-03 K at this level, which is **5.9× above even the
window's upper wall** — so across the whole window the harmonic scheme passes
and the linear scheme fails. **Every candidate `X` is a control and none is an
identity**, which is the property §2a asks about, established for the window
rather than for one chosen point.

**One correction to the supervisor's framing, made rather than repeated.** The
supervisor's instruction described the margin as *"~8 orders below EVERY
candidate value"*. That is right at the loose end (8.50) and **optimistic at the
tight end, where it is 5.54**. The numbers are stated per candidate in the table
above rather than as a single approximation. The conclusion is unchanged — 5.54
orders of margin at the tightest defensible threshold is decisive — but a
round-number margin that is wrong by three orders at one end of its own range is
the kind of figure that gets quoted onward, so it is corrected here.

**What this lane can and cannot claim about independence, plainly.** It can
claim that every number used to fix `X` predates W1b, that the arithmetic is
shown, that a gate at `X` discriminates between two schemes the lab has already
measured, and — the load-bearing one — that **the verdict is invariant across
the whole defensible window**. It **cannot** claim that a lane ignorant of
2.899e-12 K would have landed on the same decade — nobody can claim that about
themselves, and a document that did would be claiming the one thing rule 2 says
cannot be proved after the fact. **The supervisor's check 4 is the control on
that residue, not the lane's assurance.**

**THE FALLBACK WAS CONSIDERED AND REJECTED, AND THE GROUND IS RECORDED SO THE
CHOICE IS VISIBLE RATHER THAN SILENT.** This lane offered `X` = 9.2e-04 K —
T9a's registered band read straight off its record, with no decade chosen by
anyone — as a cheaper remedy if the supervisor judged the residual
contamination too high. **The heat-transfer supervisor considered it and
REJECTED it on 2026-08-27**, on a ground this lane had not seen and accepts:

> **A GCI band is a statement ABOUT GRID CONVERGENCE. Borrowing it as an
> absolute floor threshold in a rung whose entire point is that it makes NO
> convergence claim would import the category error this rung exists to
> remove.**

That is correct, and it is the same category error in a subtler dress than
W1b's: W1b registered a triple it could not use, and the fallback would have
registered a *convergence-derived number* as the threshold of a
*non-convergence* claim. **`X` = 1.0e-04 K stands**, on the window construction
above — one decade below the decision magnitude, two above the referent
precision — which is principled independently of the band's provenance.

### 3.4 The identity test — `VERIFICATION_CHARTER` §2a, answered in the gate's own text

**(1) What result would make this gate FAIL?**
\|`T_i1(W1c_c)` − exact\| > 1.0e-04 K. **This is not hypothetical**: the
parent's own registered scheme measures 5.43e-03 K at this level, 54× above the
floor. The gate is a control, not an identity: a wrong interface treatment
fails it, measurably, on the record.

**(2) Could a wrong treatment still PASS it?**
**YES, and the ways are named rather than denied.** Any treatment wrong about
something this row does not read passes it: interface 2, the fin rows, the
transient path, 2-D or 3-D conduction, or an error that happens to vanish at
interface 1 while being large elsewhere in the wall.

- **Gated against:** `C_MAP` (every cell's `DT` against the registered layer
  map), `C_SCHEME` (the harmonic line on disk), gate (1) (iterative plateau),
  the age guard, and the four-arm planted-zero control.
- **Carried as `REPORTED` precisely so a reader can see the uncovered part:**
  N4 (interface 2), N3 (hot-face flux), N2 (the mesh-family spread).

---

## 3a. THE LABEL CEILING — RULED. `PASS` IS AVAILABLE, on five conditions declared here before compute

**Registered ceiling: `PASS`.** Not on this lane's argument, and not on the
supervisor's: **ruled by `VERIFICATION_CHARTER` §2h (v1.17, commit `9fdb1d9f`,
2026-08-27)**, read at source.

### 3a.1 What was referred, and what came back

This registration's v1.0 flagged a conflict: §2g.3 says the floor-demonstration
gate **can `PASS`**; §2f.3's **CONTINUUM** row names *"exact or manufactured
solution"* and caps such a limb at **`GATE REACHED`**. The lane registered `PASS`
on §2g.3's express authority, argued §2f.3's stated ground did not obtain, and
**referred rather than proceeded**.

**§2h holds that §2f.3 never reached this limb, on two independent grounds:**

1. **§2f.3's own heading decides it — *"THE CAP ATTACHES TO WHAT A LIMB
   CLAIMS."*** A floor demonstration claims a property of **the discretisation**,
   not of the continuum solution. §2f.3's ground — *"discretisation error is not
   separable"* — is **not merely absent here but INVERTED: the quantity §2f.3
   protects against is the quantity being reported.**
2. **Express beats residual.** §2f.3's *"a limb that cannot be classified is
   CONTINUUM by default"* is a **residual** rule governing **unclassified** limbs.
   §2g.3 classifies this limb **expressly**. **The two clauses never both
   applied.**

**Verification recorded the drafting defect as its own** (§2h.3): §2f.3's row
groups four referents under one ground that holds for only two of them, and *"the
defect is in the drafting, not in heat-transfer's reading."* **§2f.3's row is NOT
amended** — narrowing a cap weakens a charter clause, which is **Sanaa's** (D539)
— so it is **referred to her with recommended wording**, and until she rules §2h
governs by express classification while §2f.3's cap **stands untouched for
everything else**. **No code changed. `label_ceiling` stays `"PASS"`.**

### 3a.2 The five conditions of §2h.4, discharged on the face of this document

`PASS` is available **only where all five hold, declared in the registration
BEFORE compute.** This table is that declaration.

| # | condition (§2h.4) | state | evidence |
|---|---|---|---|
| **1** | **The reference is the exact or manufactured solution OF THE SAME CONTINUUM MODEL the solver discretises** — the load-bearing one; anything else and §2f.3's cap applies in full | **MET**, with one caveat named in §3a.3 | §3a.3 |
| **2** | Iterative error separately gated by rule 5 limb (1), one-way | **MET** | `apply_gate()` is the only verdict-writing function; its **first** branch returns `NOT A RESULT` on `gate1_ok == False` **before the band is consulted**, so no path turns a non-converged level into a `PASS`. Driven both ways: *"dev 0, gate (1) failed → NOT A RESULT"* and *"dev 2 X, gate (1) failed → NOT A RESULT"* (§8). Registered channel: `C_CONV`, End line + last two checkpoints agreeing in `T` to 1e-09 K (§4.1). |
| **3** | **Round-off stated with its magnitude and shown negligible against the band — a number, not an assurance** | **MET** | §3a.4 |
| **4** | **The limb's wording makes no continuum claim** — *"the discretisation error is below X at N cells"*, never *"the solution is correct to X"* | **MET** | The registered sentence is §3.2, with `N` = **35** stated. **No machine check discharges this** (§2h.5): the AST guard proves the **absence of a triple**, not the wording. Discharged by the text sweep of every artifact, §8.3. |
| **5** | **The claim is bounded by the levels actually run** — *"below X at every level run"* is measured; *"so the answer does not depend on the mesh"* is a claim about meshes **not** run | **MET** | §2g.3's overreaching phrase is **struck from every artifact** (§0.3, §8.3). The graded row F1 is 35 cells; further levels run are reported in **N1**, measured, **extrapolated to none**. N2 is a §2f.6 **bound** over the meshes read, never a GCI. |

### 3a.3 CONDITION 1 IN FULL, because it is load-bearing and a bald assertion would be the flattering error

**What the solver discretises.** `laplacianFoam`, on a mesh whose transverse
patches are `empty` — so the discrete problem is genuinely **one-dimensional** —
with `hot { type fixedValue; value uniform 350; }` and `cold { type fixedValue;
value uniform 300; }`, and a per-cell `DT` field carrying the layer values
0.8 / 0.04 / 16 (verified cell by cell at grade time by `C_MAP`).

**What the referent solves.** `d/dx( k dT/dx ) = 0` on the same three-layer
domain, the same two Dirichlet values, the same `k` per layer — **the steady limit
of the very equation `laplacianFoam` integrates.** Not an experiment. Not a
correlation. **Not a different model.** So **model-form error is zero by
construction** and the residual **is** discretisation error, which is what §2h.4(1)
requires.

**THE ONE CAVEAT, NAMED RATHER THAN GLOSSED.** `laplacianFoam` integrates the
**transient** equation `∂T/∂t = ∇·(DT ∇T)`; the referent is its **steady** limit.
Strictly, the residual therefore also contains a **temporal** term — the distance
still to be travelled to steady state — and it would be dishonest to fold that
into "zero by construction" without measuring it. **It is measured, and it is
below anything representable:**

- Conservative slowest diffusive time constant, whole domain at the smallest
  diffusivity: `τ ≤ L_tot² / (π² D_min)` = `0.17² / (π² × 0.04)` = **7.32e-02 s**.
- `endTime` is **1000 s**, i.e. **≈ 13 660 e-folds**.
- Double precision underflows to **exactly zero** past about **745 e-folds**, so
  the temporal residual is **18.3× beyond the point where it is representable at
  all.** It is not small; it is **identically zero in the arithmetic.**

The transient term is **additionally** gated as iterative error by condition 2
(`C_CONV`), and W1b measured that checkpoint move at **0.000e+00 K exactly** on
all three levels.

**This lane's answer to the supervisor's direct question — "if you have ANY doubt
that condition 1 holds exactly, tell me" — is: it holds, and the caveat above is
why the answer is "it holds" rather than "obviously".** The one thing that would
break it is a referent solving a *different* model, and this one does not.

**A CORRECTION OWED UPWARD, made rather than absorbed.** The supervisor's
instruction described the referent as *"the exact series-resistance solution of
the same steady conduction model **buoyantBoussinesqSimpleFoam** is
discretising."* **This rung's solver is `laplacianFoam`**, registered as such
throughout and verified in the parent's `controlDict` at freeze `0cbaea26`
(`application laplacianFoam;`). `buoyantBoussinesqSimpleFoam` is **T19's** solver.
The conclusion is unaffected — condition 1 holds for `laplacianFoam` for the
reasons above — but **condition 1 is the one that decides the label, and a wrong
solver name inside it would be the worst possible place for a copied error to
survive.**

### 3a.4 CONDITION 3 — the round-off magnitude, as a number

**Why the condition exists, in verification's terms: a floor demonstration whose
floor is not shown to sit above the arithmetic noise is asserting the thing it
exists to measure.**

| quantity | value | how obtained |
|---|---:|---|
| binary64 unit round-off `u = 2⁻⁵³` | 1.110223e-16 | IEEE-754; OpenFOAM built double precision, case writes `writePrecision 16` |
| `ulp(350 K) = 2⁻⁴⁴` | **5.684342e-14 K** | 350 lies in [2⁸, 2⁹), so `ulp = 2^(8−52)` — the representation granularity at the operating magnitude |
| measured level difference \|`e21`\| | 2.842e-13 K = **5 ulp** | W1b's graded run on byte-identical inputs, `T9aR1b_RESULTS.md` §5 |
| measured level difference \|`e32`\| | **3.240e-12 K = 57 ulp** | as above — **the binding figure** |
| measured checkpoint move, t = 900 → 1000 | **0.000e+00 K exactly** | as above, all three levels |

**These level-to-level differences ARE the arithmetic noise**, and that is not an
assumption: the harmonic scheme carries no discretisation error to distinguish the
levels by (§2a), so what separates them is round-off and nothing else.

| margin | ratio | orders |
|---|---:|---:|
| band 1.0e-04 K / **3.240e-12 K** (binding, largest measured) | 3.086e+07 | **7.49** |
| band 1.0e-04 K / 5.684e-14 K (`ulp`) | 1.759e+09 | **9.25** |

**The larger measured figure is used as binding, not the `ulp`, because using the
larger is the conservative choice for a claim that the floor sits above the
noise.** **CONDITION 3 IS MET.**

**A second correction owed upward.** The referral expected *"~12 orders down"*.
**The arithmetic gives 7.49 orders against the binding measured figure and 9.25
against the `ulp` — neither is 12.** The condition is met on either figure with
room to spare, and the smaller true number is recorded here rather than the larger
expected one, because a margin quoted 3–4 orders high is the kind of figure that
gets repeated onward. This is the second such correction in this document; the
first is the "~8 orders" figure in §3.3.

### 3a.5 What §2h did NOT rule, named so it is not read in

- **Nothing touches W1b's refused exception**, which stands refused.
- **Nothing licenses a `PASS` on any limb whose reference is experimental or
  correlative.**
- **Whether §2f.3's row should be split is Sanaa's**, and is not settled.

### 3a.6 Launch authority

Verification confirmed nothing further is owed to it. The heat-transfer
supervisor's standing instruction: **freeze first, and launch only once the freeze
is committed and conditions 3 and 4 are confirmed discharged.** **A freeze commit
under this document does not itself carry launch authority**, and until first
compute every field here — `label_ceiling` included — remains amendable under
charter §2b limb 1, which §2 states and checks rather than assumes.


## 4. The controls

### 4.1 Gate (1) — standing rule 5's limb (1), and its scope

`C_CONV`: an `End` line in `log.solve`, and the **last two written checkpoints
(900, 1000) agree in `T` to 1e-09 K** — the parent's checkpoint form
(L-140/L-141).

**Scope, and this is one of the two changes §5.2 asks the supervisor to attack
hardest:** gate (1) is **BINDING on the graded level `W1c_c`** — F1 is
`NOT A RESULT` if it fails there — and is **EVALUATED AND REPORTED on `W1c_m`
and `W1c_f`**, where it flags their `REPORTED` rows and touches no verdict.
Ground: F1's claim is about the level it reads and no other. §2f.7 makes limb (1)
the only convergence gate a no-triple family has left, and it is not optional;
it is not thereby made to bind on rows that do not exist.

### 4.2 `C_CLASS` — a row may not claim what this comparator cannot gate

Every registered row carries a `claim_class`, and the **only admissible classes
are `FLOOR_DEMONSTRATION` and `REPORTED`**. A row registered with any other
class — in particular any row claiming a **grid-convergence property** —
**REFUSES (exit 2)**, because this comparator has **no rule 5 triple gate to
route it through**. Exactly one `FLOOR_DEMONSTRATION` row is admissible.

**This is the brief's non-negotiable constraint 1 implemented as a refusal
rather than as a promise.** There is no branch inside a triple gate, no flag
that short-circuits one, and no code path by which a non-`CONVERGING` triple can
produce a `PASS` on a convergence claim — because there is no triple and no
convergence claim, and the comparator refuses to accept one.

### 4.3 `C_NOTRIPLE` — the structural guard

An **AST scan of the comparator itself** refuses if it refers to `gci`,
`gci_equal`, `gci_unequal`, `refinement_ratio`, `richardson`, `observed_order`,
`GCI_abs`, `GCI_pct`, `grade_triple`, `triple_of`, `p_observed` or
`roache_gate`, and requires that the **only** name imported from
`scripts/roache_triple.py` is `PLANT`.

The scan is **AST-based and therefore blind to comments and docstrings**, which
is what lets the file explain at length why it computes no triple without
tripping its own guard — and that blindness is itself driven, both ways: a
planted `gci_unequal(...)` **call** is seen; the same names in a comment and a
docstring are **not**.

**Measured, AST-wise, against W1b's comparator:** every executable reference to
that machinery is **zero** in W1c (`triple_of` 2 → 0, `gci_unequal` 2 → 0,
`refinement_ratio` 3 → 0, `STAGNANT_FLOOR` 5 → 0, `P_MIN` 5 → 0, `FS` 2 → 0).
The table is reported AST-wise and not by text grep, because a text grep
conflates executable references with the guard's own forbidden-name list and
reads as though the machinery survived. It did not.

### 4.4 `C_MAP`, `C_SCHEME`, `C_REF`

- `C_MAP` — every cell's `DT` equals the registered layer conductivity for its
  centre position. Mismatch → exit 2, never a note.
- `C_SCHEME` — `CASE.txt` **and** `system/fvSchemes` on disk both carry
  `Gauss harmonic corrected`; the parent's linear line is **REFUSED**.
- `C_REF` — the two-route referent and its four external cross-checks (§1).

### 4.5 Completion — standing rule 4, no limb weakened

`mark_done_t9aR1c.py`, all-or-nothing: **rc = 0**; an **`End` line**; **last
written time == `endTime`**; **`T` and `DT` present at that time**;
**`ExecutionTime` line count == `endTime`/`deltaT`**; and **every needed field at
`endTime` NEWER than the case's own `0/T`** — the **age guard**. An **absent
`STATUS` file is a REFUSAL**, never an inference from an `End` line (K0d L1).
L-342 field classes as W1b's: the eleven infrastructure fields are `NOT
MEASURED` → `NOTE`, and the grade proceeds.

**The open tension on the `ExecutionTime`-count limb is carried, not settled.**
`CLAUDE.md` rule 4 lists it among the strict completion conjuncts;
`docs/L342_GRADER_AUDIT.md` classifies a refusal keyed on that count as
**CONFLATED — MISCLASSIFIED**; `T9aR1b_RESULTS.md` §3 referred that conflict to
the verification supervisor and it is still open. **This rung keeps the limb**,
because weakening a completion clause on a lane's own reading of an audit is
exactly the move the completion rule exists to forbid.

---

## 5. The planted-zero control — rule 3, FOUR arms, and why the third one is the point

### 5.1 Why a floor demonstration needs more than the usual plant

**A floor demonstration is a claim that a number is SMALL**, which is the single
most dangerous claim class in this lab, because **a blind reader returns small.**

This team's finding today sharpens it: **a plant that carries the same form the
reader is already looking for proves only that the reader is not blind TO THAT
FORM.** W1b's control planted a temperature value into cell `iL` — the point
reader's own station — which is exactly the form the reader was written for.

| arm | what is planted | what it refuses |
|---|---|---|
| **N** | nothing; the same bytes are read twice | a **NOISY** reader (any non-zero difference) |
| **P1** | the registered `PLANT` (1.234e-03 K, imported from `scripts/roache_triple.py`) into the reader's own stencil cell, on a **measured ladder** 1.0 … 1e-07 | a **BLIND** reader, and a read that moves by less than **0.1 × plant** (plant and read carry the same units, K into K, so W1b's sizing rule transfers — L-340) |
| **P2** | **A PERMUTATION.** The two stencil values are **SWAPPED**. **No value in the file changes — only their order.** | an **ORDER-BLIND** reader |
| **P3** | the registered `PLANT` into a **far cell in layer 3**, outside the stencil | a reader that has become a **whole-field statistic** (the read must move by **exactly zero**) |

### 5.2 Why P2 is adequate as "a form the reader was NOT written for"

The reader is a two-cell, position-indexed, conductance-weighted mean. **P2
perturbs no value at all.** Every failure mode in the class *value-based but
position-blind* — an index that has drifted, a cached constant, a block sum, a
whole-layer mean, a reader that silently fell back to a default — returns
**exactly the same number** before and after a permutation, and is refused.
**P1 cannot detect any of them**, because in every one of them a value plant at
`iL` still moves the read.

**And the arm is honest about what it can and cannot gate.** The comparator
predicts the permutation shift from the reader's **own** weights, so the
predicted-versus-measured agreement is an **identity** in charter §2a's sense —
it is **REPORTED and never gated**. The **gate is that the move is non-zero**.
Measured on the forged coarse level: the swap moves `T_i1` by **−1.15797 K**
against a registered visibility floor of 1e-06 K.

**An unarmable control is a REFUSAL, never a pass.** If the two stencil values
are equal — so that a swap could not move the read whatever the reader does —
the control refuses and says it could not be armed. Driven.

---

## 6. The rung is DECOUPLED by construction — a grading property that is also a cost property

**F1 reads ONE level.** `W1c_m` and `W1c_f` are **optional evidence levels**
feeding `REPORTED` rows. A level that is capped, crashed, mispriced or simply
not run is **recorded as such and cannot touch F1's verdict.**

**The exposure this avoids was measured on T16 today.** T16 priced three mesh
levels from **one flat per-cell-iteration rate** (3.8932e-06 core-s) and
measured 2.8890e-06 at coarse and 6.4883e-06 at medium — a **2.246× rise for a
4× cell count**, giving **two opposite errors out of one registration** (0.742×
over-priced, 1.667× under-priced), which is why they did not cancel and why
nobody saw it until the actuals arrived. On an **all-or-none** comparator, one
capped level makes the **whole rung ungradeable** — and T16's cap cannot be
fixed, because its first compute has closed rule 2 on it.

**A floor demonstration does not need a triple, so it must not be built to need
every level.** Registered:

- **mandatory:** `DONE.W1c_c`. Its absence is a **REFUSAL**.
- **optional:** `DONE.W1c_m`, `DONE.W1c_f`. Absence is `NOT RUN` or
  `RAN_NOT_COMPLETE`, **REPORTED**, never fatal.

**The cherry-picking hazard this opens is closed by three refusals, not by
assurance:**

1. **Every level whose `DONE` marker exists IS read.** The comparator cannot be
   told to skip one.
2. A level with a `STATUS` file and **no** `DONE` marker is recorded
   **`RAN_NOT_COMPLETE`** with mark_done's own reasons — it ran, it did not
   complete, and that appears in the record instead of vanishing.
3. A level holding a **written time directory and NO `STATUS` file is a
   REFUSAL** (K0d L1: an absent `STATUS` is never inferred from fields on disk).
   **A level cannot be dropped from this record by removing its markers.**

All five behaviours are driven end-to-end on forged bytes (§8).

---

## 7. Predictions — registered before compute, and every one can lose

**Read with §0.6.** These are registered and each can lose, but they are
predictions about a number this lab has already seen on byte-identical inputs.
They are recorded for discipline and for the calibration ledger. **They are not
offered as risk, and a hit here is not evidence of anything beyond the
instrument working as registered.**

- **P1.** \|`T_i1(W1c_c)` − exact\| < **1e-06 K**, two orders inside `X`.
  *Loses if the measurement lands anywhere in [1e-06, 1e-04) K — which would
  still be a PASS. This prediction can lose without the gate losing, which is
  why it is stated separately from the gate.*
- **P2.** \|dev(`W1c_c`)\| / 5.43e-03 K < **1e-04** — the registered scheme
  beats the parent's by at least four orders **at the same resolution**.
- **P3.** N3: \|`q_hot`/`q_exact` − 1\| < **1e-09** at every level read (T9a's
  1.8 % linear-scheme excess has vanished).
- **P4.** N2: the mesh-family spread is below **1e-08 K**.
- **P5.** N4: \|`T_i2` − exact\| < **1e-06 K** at every level read.
- **P6.** Gate (1) holds at every level: the last two checkpoints agree in `T`
  to better than 1e-09 K.

---

## 8. Instruments — L-332, and their MEASURED selftest state

Every instrument was run **twice**, under `python3` and under `python3 -O` (`-O`
strips `assert`, and an instrument whose refusals live in asserts silently stops
refusing). `__pycache__` was cleared first, because stale bytecode inverts
mutation tests. **Evidence file, produced by running them:**
`verification/runs/T-family/T9aR1c_runs/T9aR1c_SELFTEST_EVIDENCE.txt`.

| instrument | distinct arms | `python3` | `python3 -O` | `assert` count (AST) |
|---|---:|---|---|---|
| `exact_t9aR1c.py` | 8 | PASS | PASS | 0 (planted control: 1) |
| `analyse_t9aR1c.py` | **37** | PASS | PASS | 0 (planted control: 1) |
| `build_t9aR1c.py` | 4 | PASS | PASS | 0 (planted control: 1) |
| `mark_done_t9aR1c.py` | 11 | PASS | PASS | 0 (planted control: 1) |
| `sweep_wording_t9aR1c.py` | 11 | PASS | PASS | 0 (planted control: 1) |
| `run_one_t9aR1c.sh` | 3, driven on scratch | — | — | shell; `bash -n` clean |

**Total: 71 distinct arms, 142 driven executions, 0 failures.**

**The arms that carry the most weight, named so they are not lost in a listing:**

- **The floor gate is driven FAILING.** On numbers at both edges (0.99 `X` →
  PASS, 1.00 `X` → PASS, 1.01 `X` → GATE FAIL, 2.00 `X` → GATE FAIL) and
  **end-to-end on real bytes**: a 2.0e-04 K offset planted at the coarsest level
  → **GATE FAIL**. It is also driven at the parent scheme's measured 5.43e-03 K
  → **GATE FAIL**. *A gate never shown to fail is not an instrument.*
- **The one-way property is driven:** gate (1) failed → `NOT A RESULT`
  regardless of the deviation, and the label ceiling can only weaken
  (`PASS` → `GATE REACHED`) and never rescues a `GATE FAIL`.
- **`C_NOTRIPLE`'s scanner is shown able to see** a planted `gci_unequal(...)`
  call, and shown blind to the same names in a comment and a docstring.
- **`C_CLASS` is driven** on four claim classes and on a planted second graded
  row.
- **The permutation arm P2 is driven both PASSING and REFUSING**, and P3 is
  driven to refuse by overriding its "far" cell to a stencil cell.
- **Decoupling is driven five ways**, including the anti-cherry-pick refusal.
- **`C_REF` is driven** with planted 1e-4 conductivity errors in each of three
  layers, all refused.

### 8.1 Instrument diffs for the supervisor's check 1

`verification/runs/T-family/T9aR1c_runs/T9aR1c_INSTRUMENT_DIFFS.txt`.

Every baseline was sourced with **`git show HEAD:<path>`** — never from the
shared index, which lags HEAD and reports phantom staged deletions under
`verification/runs`, and never by `git checkout`/`git restore`, which restore
from that stale index. **Each baseline's HEAD blob sha is stated on its own diff
header** and each was confirmed byte-identical to the working-tree copy at
generation time.

| new instrument | baseline | HEAD blob | changed lines |
|---|---|---|---:|
| `build_t9aR1c.py` | `T9aR1b_runs/build_t9aR1b.py` | `ef58986681c2` | 16 |
| `mark_done_t9aR1c.py` | `T9aR1b_runs/mark_done_t9aR1b.py` | `68c78731a061` | 29 |
| `run_one_t9aR1c.sh` | `T9aR1b_runs/run_one_t9aR1b.sh` | `d7990722b87c` | 33 |
| `T9aR1c_registered.json` | `T9aR1b_runs/T9aR1b_registered.json` | `cfe867c6c88d` | 245 |
| `analyse_t9aR1c.py` | `T9aR1b_runs/analyse_t9aR1b.py` | `fd6c43a0da91` | **981 — a REWRITE** |
| `exact_t9aR1c.py` | **NEW, no line ancestor** | pattern: `T18_runs/exact_t18.py`, `T19_runs/exact_t19.py` | 283 |

**The diffs file names, up front, the two scope changes that make a verdict
EASIER to reach than W1b's comparator made it** — gate (1) binding on the graded
level only (§4.1), and the decoupling (§6) — because a change in that direction
is the one that needs the most justification, and it asks the supervisor to
attack both.

### 8.2 Filing — and the live checker returns a FALSE ZERO, which is said rather than banked

`python3 scripts/check_filing.py` reports 34 violations across 7 rules and **not
one names a `T9aR1c` or `W1c` path. That is not evidence of compliance.** The
checker enumerates paths from **HEAD** (`git ls-tree -r HEAD`,
`check_filing.py:86-105`) and every artifact of this rung is **uncommitted**, so
the checker **cannot see any of them**.

**Proved, not assumed:** a file literally named `Bad Name PLANT.md` was created
inside the run directory and the live checker still returned zero `T9aR1c` hits
and the same total of 34. The file was removed. **A zero from a reader not shown
able to see a non-zero is not evidence** (standing rule 3), and this reader was
shown blind.

The rules were therefore run **against the paths directly**, by importing
`check_filing`'s own rule set and substituting its HEAD enumeration. **0
violations on the nine paths as filed**, from a reader shown able to fire all
four planted shapes that govern this rung: R0 (a name with spaces), R6 (a run
output filed beside the prose), R7 (a campaign record not in `UPPER_SNAKE`), and
R7 (campaign helper code not `lower_snake`). Prose under
`docs/campaigns/T-family/` as `<RUNG>_<PURPOSE>.md`; instruments and run outputs
under `verification/runs/T-family/T9aR1c_runs/`, **never beside the prose**.

**One of those four plants first read as NOT FIRING, and the cause is recorded
against this lane rather than corrected quietly:** the rule *had* fired, and
this lane's own filter was matching the literal `T9aR1c` while the plant path
spells it `t9aR1c`. The instrument was right and the harness reading it was
blind — which is the defect class a planted control exists to expose, found here
in the checking harness. The full run's 34 violations are pre-existing, belong to
other paths, and are not this lane's to fix.

---

### 8.3 The wording sweep — the machine half of §2h.4(4)/(5), and it is a TEXT check, not the AST guard

`VERIFICATION_CHARTER` §2h.5 is express: the AST guard **proves the absence of a
triple, not the wording of the claim**, and those are different propositions.
Condition (4) is about the wording, so it is discharged by a text sweep —
`verification/runs/T-family/T9aR1c_runs/sweep_wording_t9aR1c.py`, which is
**re-runnable by the supervisor** and is **not part of the freeze set** (it grades
no case; it checks this rung's own documents).

**What it sweeps:** all **10** artifacts of the rung — this pre-registration, the
registered JSON, all six instruments, the instrument diffs and the selftest
evidence — for the **8** phrases in the sweep's own `PHRASES` tuple, which cover
the two constructions §2h.4 forbids: wording the limb as a continuum claim, and
wording it as a claim about meshes that were not run.

**The phrases are deliberately NOT enumerated here, and the reason is a
measurement.** Version 1.1 of this section listed all eight literally, and **the
sweep flagged this document as a violation for it** — correctly, since a bare
list in running prose is indistinguishable from an assertion. The list now lives
in **exactly one place**, `sweep_wording_t9aR1c.py`'s `PHRASES` tuple, which is
also the only region the sweep exempts and it exempts it **by AST node**. One
name, one number: a second copy in prose would be a copy that can drift, and it
would have needed an exemption that a Markdown file gives no structural way to
scope. **The instrument caught this, in its own selftest, on this very document,
before the freeze** — which is the argument for its existing.

**Finding the phrase is easy; classifying it is the instrument.** Four kinds of
occurrence exist and only one is a violation:

| class | what it is | verdict |
|---|---|---|
| **ASSERTION** | the document says it in its own voice | **VIOLATION** |
| DISCLAIMER | quoted in order to deny or strike it | required — a strike that cannot name what it struck is not a record |
| REMOVAL | a unified-diff `-` line in the diffs file | required — a diff that cannot quote removed text is useless |
| VOCABULARY | the sweep's own `PHRASES` tuple | required — a forbidden-phrase list must contain the forbidden phrases |

**MEASURED, on the artifacts as they now stand: 0 ASSERTIONS**, 55 DISCLAIMERS,
0 REMOVALS, 8 VOCABULARY, out of 63 occurrences at 2026-08-27T22:15Z.

**Only the first of those four numbers is stable and only the first is binding.**
The sweep reads the selftest evidence file, which grows every time the sweep is
run into it, so the DISCLAIMER and occurrence counts drift upward by design.
**`ASSERTIONS: 0` is the condition; the rest is context.** Re-run it — that is
what it is for.

**Three properties that stop this being a sweep that passes because it cannot
see:**

1. **The `VOCABULARY` exemption is located STRUCTURALLY** — the sweep parses its
   own source and exempts exactly the AST node of the `PHRASES` assignment
   (measured: source lines 69–71), **never a line number and never a filename
   test**. Driven: an asserting sentence injected into that same file *outside*
   the tuple is still a **VIOLATION**. The exemption covers one node, not a file.
   This is the same move `C_NOTRIPLE` makes, for the same reason.
2. **Every planted control is ASSEMBLED FROM `PHRASES` at runtime**, never written
   out literally, so **the sweep never writes a forbidden sentence in its own
   voice** and needs no exemption for its own selftest. **An instrument that had
   to be excused from its own rule in order to pass it would be evidence of
   nothing.**
3. **A file it cannot read is a REFUSAL, not a skip** — driven — because a sweep
   that silently skips a file is exactly the false zero §8.2 caught in
   `check_filing.py`.

**`REMOVALS: 0` is a real zero and the reader is shown able to return non-zero**:
the struck phrase never appeared in W1b's comparator, so it can only ever have
been a `+` line, and the diffs were regenerated after the strike. The REMOVAL
classifier is nonetheless driven live by a planted unified diff, and driven
*negative* by feeding the same bytes with diff handling off.

**A THIRD CASE-SENSITIVITY MISS, recorded because it is now a pattern.** The
first version of this classifier matched `STRUCK|struck` and **missed `Struck`**,
reporting a correctly-disclaimed line as a violation. That is the third time this
rung has been bitten by case: the `T9aR1c`/`t9aR1c` filing filter in §8.2, and
this, twice over. **A reader that is case-sensitive about English prose is blind
in a way that looks like vigilance.** The classifier is now case-insensitive and
carries a driven `Struck` control.

## 9. Cost — rule 12, priced PER LEVEL

### 9.1 The basis, registered up front

**Primary basis: `ExecutionTime`, per level.** `T9aR1b_RESULTS.md` §8's
transferable finding, adopted here **before compute**: below about one
wall-second per case the registered core-minute basis (`wall_s × ranks ÷ 60`)
cannot resolve the spend and returns **0**, and a 0 there means *"too small to
measure"*, **not** *"free"*. W1b's calibration row therefore carried **no ratio**
on the wall basis. This rung registers `ExecutionTime` up front so its
calibration row **can** carry one.

### 9.2 Each level is priced from its OWN measured rate

**A single flat per-cell-iteration rate across a mesh family is a measured
defect, not a simplification** — T16, 2026-08-27 (see §6). This rung does not
borrow another family's exponent: **it has a direct measurement at every level
it will run**, on these exact cases, from `T9aR1b_RESULTS.md` §2.

| case | cells | W1b measured `ExecutionTime` | per cell-iteration [core-s] | POINT [core-min] | POINT [USD, derived] |
|---|---:|---:|---:|---:|---:|
| `W1c_c` | 35 | 0.05 s | 1.4286e-06 | 0.000833 | 7.125e-07 |
| `W1c_m` | 56 | 0.05 s | 8.9286e-07 | 0.000833 | 7.125e-07 |
| `W1c_f` | 90 | 0.06 s | 6.6667e-07 | 0.001000 | 8.550e-07 |
| **total** | | **0.16 s** | | **0.002667** | **2.280e-06** |

**The scaling exponent, stated as an assumption with its evidence.** c → f is
35 → 90 cells (**2.5714×**) for 0.05 → 0.06 s (**1.2×**), so
`ln(1.2)/ln(2.5714)` = **0.193 on total time**, and the per-cell-iteration rate
therefore **falls** as `N^−0.807`. **The rate falls with size here — the
opposite sign to T16's +0.584** — because at 35–90 cells the run is dominated by
process start-up and field I/O rather than by the linear algebra.

**What happens if the exponent is wrong, quantified rather than hoped.** The cap
headroom is **1200×** at the coarse level (60 s cap against 0.05 s measured) and
**1000×** at the fine. Priced at T16's much steeper total exponent of **1.584**
the fine level would take **0.223 s**, still **269×** inside its cap; at a
pathological `N^3.0` it would take **0.85 s**, still **70×** inside it. **The
exponent would have to be wrong by three orders before any cap bound.** And
because this rung is **decoupled (§6)**, a capped or mispriced `W1c_m` or
`W1c_f` **cannot make it ungradeable**: F1 reads `W1c_c` alone. **The T16 failure
mode is structurally absent here, not merely unlikely.**

The wall-clock basis is carried for continuity at **POINT 0.0045 core-min**
(0.0015/level, from T9a's measured 0.09 s wall per level) and is **expected to
read 0.000 again** at this case size; it will be reported **UNRESOLVED**, never
as a 0.000 ratio.

### 9.3 The cap, and what actually enforces it

**CAP: 1 core-min per level, 3 core-min total.**

**`scripts/queue_runner.py` REPORTS a cap overrun and does NOT kill** (measured
lab-wide 2026-08-27; runner-side enforcement is being pre-registered separately
by cfd on the chief's order). **The launcher's `timeout` wrapper is therefore
the only thing that stops this run**, and the cap binds only through the
arithmetic

> **`timeout_s` = `cap_core_min` × 60 / `ranks` = 1 × 60 / 1 = 60 s**

`run_one_t9aR1c.sh` **REFUSES at pre-flight** if the registered `timeout_s` does
not equal that product, and separately **REFUSES a `--timeout` that is not equal
to the registered `timeout_s`** (a caller may neither widen a cap that rule 12
says stops the run nor narrow one into a manufactured cap-stop). Both refusals
are **driven on scratch** in the evidence file: ARM A (the registered file,
arithmetic holds) **proceeds past the check**, ARMs B and C **REFUSE**. **A cap
nothing enforces is not a cap.**

An overrun **stops the run**; it does not get a new budget.

### 9.4 Dollars, and the calibration owed at completion

| | core-min | USD at $0.0513/core-h |
|---|---:|---:|
| POINT (ExecutionTime basis) | 0.002667 | **2.280e-06** |
| POINT (wall basis, continuity) | 0.0045 | 3.85e-06 |
| CAP | 3 | **2.565e-03** |

**DERIVED, NOT MEASURED.** The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5) and the rate is **owner-stated** (Sanaa
2026-08-21/22, corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`), so every
dollar figure here is derived at that rate and **reported-by-owner**.

Well under the $25 pre-authorisation; that blanket is **not** a per-item read
(rule 9), and this cost is registered on its own terms.

**At completion (rule 12):** the actual is stated **per level** on the
`ExecutionTime` basis with the ratio actual/predicted, the wall basis is reported
**UNRESOLVED** rather than 0.000, waste is named separately, and the row lands in
`docs/COST_CALIBRATION.md`. **The comparison is per level and not one rung-wide
ratio — a rung-wide ratio is exactly what hid T16's two opposite errors.**

---

## 10. The launcher

`run_one_t9aR1c.sh` = `run_one_t9aR1b.sh` (HEAD blob `d7990722b87c`) with the
rung name and field set changed, **plus one substantive addition: the cap
arithmetic check of §9.3, which is the only new refusal in the whole instrument
set.**

Inherited unchanged: rc captured **inside** the wrapper (never around a `setsid`
line, which returns 0 for every outcome); the `capped` witness as an
**infrastructure** field; the registered cap read from the JSON; the
**lineage-aware** foreign-process guard (`9fa66065`); time directories matched by
**regex fullmatch**, never a shell glob; the OpenFOAM bashrc sourced with `set
-u` lifted; an existing `STATUS.<case>` **REFUSED** before anything is written; a
**pre-flight refusal writes NO `STATUS`** (nothing ran, so there is no rc, and
inventing one is back-dating); `0/` armed from `0.orig/` with **`0/T` touched
last** (the age-guard datum); and `exit "$RC"` as the last line.

The launch guard **REFUSES** a case that already holds a `0/` or any numeric time
directory — which is why §0.5's new case names are a rule and not a preference.

---

## 11. The freeze set — proposed, NOT YET FROZEN

**These are the files that would be frozen at the pre-registration commit, and
none of them is committed.** Recorded here so the supervisor's check-1 read is
against a fixed set and any later drift is visible.

| file | sha256 (first 16) | lines |
|---|---|---:|
| `verification/runs/T-family/T9aR1c_runs/build_t9aR1c.py` | `c4bf597a2ca2f876` | 167 |
| `verification/runs/T-family/T9aR1c_runs/exact_t9aR1c.py` | `bea38debb333be86` | 283 |
| `verification/runs/T-family/T9aR1c_runs/analyse_t9aR1c.py` | `ecd58da928dfc523` | 959 |
| `verification/runs/T-family/T9aR1c_runs/mark_done_t9aR1c.py` | `4cd92f35813cef73` | 231 |
| `verification/runs/T-family/T9aR1c_runs/run_one_t9aR1c.sh` | `f6ede1bb00cc52f2` | 206 |
| `verification/runs/T-family/T9aR1c_runs/T9aR1c_registered.json` | `9ddbb818ce35e24a` | 294 |

**HASHES AS OF %s.** Two of the six MOVED under the
supervisor's §2h additions, and this table is the record of which: `analyse_
t9aR1c.py` `9b5a3d0c…` → **`ecd58da9…`** (939 → 959 lines) and
`T9aR1c_registered.json` `6cb56312…` → **`9ddbb818…`** (275 → 294 lines), both
carrying the §2h.4(4) wording change and the §2h.4(3) round-off block. The other
four are **unchanged from the 21:48:26Z recording**, which is the check worth
making: a wording amendment must not have touched the builder, the referent, the
completion marker or the launcher, and it did not.

**`sweep_wording_t9aR1c.py` (`43acd8e60ae5dc90`, 248 lines) is DELIBERATELY NOT IN
THE FREEZE SET.** It grades no case and reads no run output; it checks this
rung's own documents, and freezing it would mean a later correction to the
document could not be re-checked. It is listed here so the supervisor can run it,
not so it can be frozen.

Case inputs do
not yet exist; they are built
by `build_t9aR1c.py` from T9a's freeze commit and would be committed alongside.

**Charter §2d requires the comparator's grading path to be fixed at the
pre-registration commit and verified byte-identical at analysis time by hashing
against the committed blob. That verification is owed and has not happened,
because nothing is committed.**

---

## 12. What this document does not do

- It does **not** authorise a launch. **Enqueueing is not authorisation.**
- It does **not** freeze anything: **check 1 and check 4 are the supervisor's,
  personally, and neither has been performed.**
- It does **not** re-grade, reopen or amend T9a, T9a-R1b, or the capability grid.
- It does **not** decide the §3a label-ceiling question, which is **REFERRED to
  the verification supervisor**.
- It does **not** settle the `ExecutionTime`-count classification conflict of
  §4.5, which remains referred.
- It does **not** offer a corroborating second measurement of W1b, and §0.6
  forecloses that reading in advance.
- It does **not** claim that the answer is mesh-independent, that the solution is
  correct to `X`, or anything about meshes that were not run. §2g.3's phrase to
  that effect was **struck under §2h.4(5)** and is absent from every artifact,
  measured (§8.3).
- It authorises no send. **SUBMISSIONS REMAIN PARKED** (rule 7). Nothing has
  been sent, filed, uploaded, registered, posted or commented outside this box.
