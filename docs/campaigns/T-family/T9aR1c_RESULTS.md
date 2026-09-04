# T9a-R1c (`W1c`) results — FLOOR DEMONSTRATION on the layered wall's interface temperature

**RUNG VERDICT: `PASS` — one of one graded row `PASS`.**

**AND THE FIRST THING THIS RECORD SAYS IS WHAT THE VERDICT DOES NOT BUY.
THERE IS NO ROACHE TRIPLE IN THIS RUNG, BY REGISTRATION, SO EVERY NUMBER BELOW
CARRIES NO DISCRETISATION BOUND AT ALL** — no observed order, no GCI, no
Richardson extrapolate, and none is derivable from anything printed here. **A
floor demonstration shows an instrument can resolve below a threshold. It is not
a validation of any physics.** §4 and §9 state that at length, and §9 is the
section a later reader should read before citing this rung for anything.

Pre-registration: `docs/campaigns/T-family/T9aR1c_PREREGISTRATION.md`, frozen at
commit **`8268ffe2`** (2026-08-27T22:17:28Z).
Run root: `verification/runs/T-family/T9aR1c_runs/`.
Machine record: `verification/runs/T-family/T9aR1c_runs/gate_t9aR1c.json`.
Grade stdout: `verification/runs/T-family/T9aR1c_runs/W1c_GRADE_OUTPUT.txt`.

**Every value below was re-read from those artifacts at this writing, and the
verdict was re-issued by running the registered comparator (§1.1), not composed
by hand.** Decisions `[lab-attributed]`. Verdict vocabulary fixed by `CLAUDE.md`
rule 1.

---

## 0. Rule 2 — the freeze precedes first compute, measured

| | |
|---|---|
| registration and full instrument set frozen at | **`8268ffe2`**, 2026-08-27 **22:17:28 Z** |
| first compute | `W1c_c` `started_utc` **2026-08-28T02:44:48Z** (`STATUS.W1c_c`) |
| margin | **4 h 27 min 20 s** |

The freeze commit `8268ffe2` carries all ten of the rung's registered artifacts
in one commit — the pre-registration, the six freeze-set instruments, the
wording sweep, the selftest evidence and the instrument diffs — and **no case
directory existed anywhere under the run root at that moment**, which is the
condition §2 of the registration states and checks rather than assumes.

## 1. The freeze set — SEVEN of SEVEN MATCH on both channels

Disk bytes hashed against the blob at the **freeze commit** and against the blob
at **`HEAD`**, in one invocation. sha256, first 16 hex:

| file | §11 registered | freeze `8268ffe2` | `HEAD` | |
|---|---|---|---|---|
| `build_t9aR1c.py` | `c4bf597a2ca2f876` | `c4bf597a2ca2f876` | `c4bf597a2ca2f876` | MATCH |
| `exact_t9aR1c.py` | `bea38debb333be86` | `bea38debb333be86` | `bea38debb333be86` | MATCH |
| `analyse_t9aR1c.py` | `ecd58da928dfc523` | `ecd58da928dfc523` | `ecd58da928dfc523` | MATCH |
| `mark_done_t9aR1c.py` | `4cd92f35813cef73` | `4cd92f35813cef73` | `4cd92f35813cef73` | MATCH |
| `run_one_t9aR1c.sh` | `f6ede1bb00cc52f2` | `f6ede1bb00cc52f2` | `f6ede1bb00cc52f2` | MATCH |
| `T9aR1c_registered.json` | `9ddbb818ce35e24a` | `9ddbb818ce35e24a` | `9ddbb818ce35e24a` | MATCH |
| `sweep_wording_t9aR1c.py` (not frozen, by design) | `43acd8e60ae5dc90` | `43acd8e60ae5dc90` | `43acd8e60ae5dc90` | MATCH |

**No drift, and no frozen file was edited.** This discharges the verification the
registration itself recorded as **owed** at §11: *"Charter §2d requires the
comparator's grading path to be fixed at the pre-registration commit and verified
byte-identical at analysis time by hashing against the committed blob. That
verification is owed and has not happened, because nothing is committed."* It has
now happened, against a commit that exists.

### 1.1 The verdict was RE-ISSUED by the registered comparator, not transcribed

`python3 analyse_t9aR1c.py --json <scratch>/regrade_gate.json` was run at this
writing (2026-09-04), `rc = 0`. The gate JSON it produced is **identical in every
field and value** to the committed `gate_t9aR1c.json`; the stdout is identical to
the committed `W1c_GRADE_OUTPUT.txt` **on every line except the one naming the
output path**. The verdict in this record is the frozen comparator's, reproduced
today on the same bytes.

## 2. Completion — three of three, DRIVEN rather than cited

`python3 mark_done_t9aR1c.py --root . <level>` returns **`rc = 0` on all three**
levels, run at this writing. `DONE.W1c_c`, `DONE.W1c_m`, `DONE.W1c_f` present.
The six conjuncts of standing rule 4, read directly from each case:

| level | cells | `rc` | `End` line | last time / `endTime` | `ExecutionTime` lines | fields at 1000 | age guard (`1000/T` − `0/T`) |
|---|---:|---:|---|---|---:|---|---:|
| `W1c_c` | 35 | 0 | present | 1000 / 1000 | 1000 | `T`, `DT` (+ derived) | **+0.106 s** |
| `W1c_m` | 56 | 0 | present | 1000 / 1000 | 1000 | `T`, `DT` (+ derived) | **+0.104 s** |
| `W1c_f` | 90 | 0 | present | 1000 / 1000 | 1000 | `T`, `DT` (+ derived) | **+0.120 s** |

**The age guard holds on sub-second mtimes, and it has to be read at sub-second
resolution to hold at all** — every level ran in well under one wall-second, so
`0/T` and `1000/T` share the same whole second. Read to nanoseconds, `1000/T` is
newer than `0/T` on every level by the margins tabulated. A whole-second reading
would have reported them equal and the guard indeterminate; that is recorded here
because the next sub-second rung will meet it again.

## 3. THE GRADED ROW `F1`

| | |
|---|---|
| row | **`F1`**, `claim_class` **`FLOOR_DEMONSTRATION`** |
| quantity | \|`T_i1` − `T_i1_exact`\| at the **coarsest** registered level `W1c_c` (35 cells) |
| reader | the parent's form, unchanged through W1b: the conductance-weighted mean of the two cells adjacent to the interface face (`analyse_t9a.measure_wall.iface_T`) |
| measured `T_i1` | **348.781082398830 K** |
| referent `T_i1` | **348.781082398830 K** |
| **\|deviation\|** | **5.684e-14 K** |
| registered floor `X` | **1.000e-04 K**, frozen at `8268ffe2` before compute |
| margin | the deviation is **1.76e+09× inside** the floor — **9.24 orders of magnitude** |
| **verdict** | **`PASS`** |

The registered gate sentence, verbatim from pre-registration §3.2 and unchanged:

> **At the coarsest registered level `W1c_c`, WHICH IS 35 CELLS, the
> DISCRETISATION ERROR in the interface-1 temperature IS BELOW `X` = 1.0e-04 K:
> `|T_i1(W1c_c) − T_i1_exact| ≤ 1.0e-04 K`. PASS inside; GATE FAIL outside.**

**`PASS` is available to this limb by ruling, not by this team's argument:**
`VERIFICATION_CHARTER.md` **§2h** (v1.17, commit `9fdb1d9f`, 2026-08-27), on the
five §2h.4 conditions declared at pre-registration §3a.2 **before compute**. Two
of the five — (4) and (5), the wording conditions — **no machine check in this
rung discharges**; §2h.5 is express that the AST guard proves the absence of a
triple and not the wording of a claim. Their machine half, the text sweep, is
re-run at §6 and reports **0 ASSERTIONS**; their human half is the supervisor's
read, not this record's.

**The referent, and why it is a referent and not a correlation.** Derived by two
independent routes — closed-form series resistance, and a flux-continuity linear
solve — agreeing to **3.41e-14 relative**, and cross-checked against four numbers
T9a registered on 2026-08-20/22 and this lane did not recompute
(`T9a_RESULTS.md` §1 and §1.1), to a registered tolerance of 1e-06 K absolute:
`T_i1` 3.99e-07, `q` 3.81e-07, `drop_layer1` 3.99e-07, `drop_layer3` 3.52e-07 —
**all inside**. `q = 19.502681619 W/m²`, `T_i2 = 300.024378352023 K`.

## 4. NO ROACHE TRIPLE EXISTS — the central limitation of this record

**There is no Roache triple in this rung. None was registered, none was computed,
and none may be inferred from anything in this document.**

- **Standing rule 5 does not engage on limb (2).** The registration declares, at
  §2a under `VERIFICATION_CHARTER` §2f.2: *"This registration declares NO Roache
  triple. Rule 5's limb (2), the triple-state gate, is UNREACHABLE and NOT
  WAIVED. A row that cannot reach rule 5's gate has not passed it."* The gate
  file carries the same sentence in its `rule5_status` field. **Unreachable is
  not exempt**: the absence of a triple is a **limitation on what this rung may
  claim**, and §9 is where that limitation is spent.
- **Rule 5's limb (1) applies IN FULL** and is binding on the graded level as
  gate (1) — see §6. *"No triple" never means "no rule 5."*
- **The absence is structurally enforced, not merely asserted.** Control
  `C_NOTRIPLE` **PASSES**: an AST scan of the comparator refuses on any of **12
  forbidden names** (`gci`, `gci_equal`, `gci_unequal`, `refinement_ratio`,
  `richardson`, `observed_order`, `GCI_abs`, `GCI_pct`, `grade_triple`,
  `triple_of`, `p_observed`, `roache_gate`), none of which is present, and
  requires that the **only** name imported from `scripts/roache_triple.py` is
  `PLANT`. Measured against W1b's comparator, every executable reference to that
  machinery is **zero** in W1c.
- **Therefore: no observed order `p`. No GCI at any `Fs`. No Richardson
  extrapolate. No discretisation uncertainty. No error bar of any kind on any
  number in this record.** Quoting one would be the violation this instrument was
  built to make impossible.
- **`N2` is NOT a substitute for one.** The mesh-family spread of 3.240e-12 K
  (§7) is a **bound on observed variation over the three meshes actually built**,
  under `VERIFICATION_CHARTER` §2f.6. It is not an error estimate, it is not
  extrapolated, it is not a GCI and it is not an observed order.
- **The ground for having no triple is a MODEL-FORM FACT, checkable without
  running anything** (registration §2f.4): with harmonic face interpolation of
  `DT`, the discrete face conductance **is** the series conductance of the two
  half-cells, so the discrete solution reproduces the exact solution to round-off
  on every mesh that resolves the layers. The discretisation error lies in the
  null space of the scheme's truncation error; `e21` and `e32` are both round-off
  and `p = ln|e32/e21| / ln r` is **noise divided by noise**.
- **The discarded arm is IN the record, with its numbers.** A triple *was* run on
  this case family: `T9a-R1b` (`W1b`), same three levels, same scheme, same
  reader, returned **`EXACT`**, `e21` = −2.842e-13 K, `e32` = 3.240e-12 K, no
  observed order defined. The election here is not selection by outcome; its
  ground is `VERIFICATION_CHARTER` §2g.3's own diagnosis that **the wrong
  instrument was registered** — a charter ruling, not this team's reading of an
  inconvenient result.

**This record does not re-grade, reopen or amend `T9a`, `T9aD`, `T9aH` or
`T9a-R1b`. Those records stand as they are.**

## 5. The planted-zero control — rule 3, four arms, all `PASS`

A floor demonstration is a claim that a number is *small*, so the whole rung
turns on whether the reader could have seen a large one. Four arms, run on real
bytes copied into a temporary tree (the registered case directories are never
written to):

| arm | what it plants | measured | verdict |
|---|---|---|---|
| **P1 — value** | 1.234e-03 K into **cell 9**, the reader's own stencil cell | `T_i1` moved **1.175238e-03 K**; demonstrated detection floor **1e-07 K** | **`PASS`** |
| **P2 — permutation** | cells **9 ↔ 10** swapped: *no value changed*, only their order | `T_i1` moved **−1.157972 K** | **`PASS`** |
| **P3 — specificity** | 1.234e-03 K into **cell 34**, outside the stencil `{9, 10}` | `T_i1` moved **exactly 0.0 K** | **`PASS`** |
| **N — negative** | two reads of identical bytes | Δ **0.0 K** | **`PASS`** |

**P1's detection ladder is the number that matters**, because it fixes how far
below the floor the reader can actually see: plants of 1, 0.1, 0.01, 1.234e-03,
1e-04, 1e-05, 1e-06 and **1e-07 K** were each recovered, the last as
9.52381e-08 K. **The reader is demonstrated able to see a perturbation three
orders BELOW the registered floor `X`**, so the 5.684e-14 K it reports is a zero
from a reader shown able to see a non-zero.

**P2's identity is declared as an identity and is not gated.** Its predicted move
from the reader's own weights agrees with the measured move to 0.0 K — that is an
identity under `VERIFICATION_CHARTER` §2a, because the prediction uses the
reader's own weights. **The gate is that the move is non-zero**; the agreement is
`REPORTED` and decides nothing. Saying so is the point of the arm.

**P3 is the arm a floor demonstration specifically needs.** A reader that moved
on a plant *outside* its stencil would be reading something other than what it
claims to read, and its small numbers would mean nothing. It moved **exactly
zero**.

## 6. The other controls

| control | state | what it actually checked |
|---|---|---|
| **gate (1)** — rule 5 limb (1) | **`PASS`**, **BINDING** on `W1c_c` | `C_CONV`: an `End` line, and the last two written checkpoints (900, 1000) agreeing in `T` to 1e-09 K. **Checkpoint move 0.000e+00 K exactly, at every level.** Binding on the graded level (F1 would be `NOT A RESULT` if it failed there); **evaluated and REPORTED** on `W1c_m` and `W1c_f`, where it flags their `REPORTED` rows and touches no verdict. |
| **`C_CLASS`** | **`PASS`** | Every row carries a `claim_class` and only `FLOOR_DEMONSTRATION` and `REPORTED` are admissible; exactly one `FLOOR_DEMONSTRATION` row exists. A row claiming a grid-convergence property **refuses (exit 2)** — there is no triple gate to route it through. Measured: `F1` `FLOOR_DEMONSTRATION`; `N1`–`N4` `REPORTED`. |
| **`C_NOTRIPLE`** | **`PASS`** | §4. 12 forbidden names checked, none present; only `PLANT` imported from `roache_triple`. |
| **`C_MAP`** | **`PASS`** | Every cell's `DT` checked against the registered layer map inside `measure()`. Mismatch is exit 2, never a note. |
| **`C_SCHEME`** | **`PASS`** | `Gauss harmonic corrected` required on disk in `system/fvSchemes` **and** in `CASE.txt`; the parent's `Gauss linear corrected` line is refused. Verified present on all three levels at this writing. |
| **`C_REF`** | **`PASS`** | Two-route referent (3.41e-14 relative agreement) plus the four T9a cross-checks, all inside 1e-06 K absolute. |
| **wording sweep** (§2h.4(4)/(5), machine half) | **`PASS`**, `rc = 0` | `sweep_wording_t9aR1c.py`, re-run at this writing over 10 files, 8 phrases, 63 occurrences: **ASSERTIONS 0** — the only class that is a violation. DISCLAIMERS 55, REMOVALS 0, VOCABULARY 8, all required classes. |

**The gate is an instrument because it is driven FAILING, not because it passed.**
The registered selftest drives the floor gate at 0.99 `X` → `PASS`, 1.00 `X` →
`PASS`, **1.01 `X` → `GATE FAIL`**, 2.00 `X` → `GATE FAIL`, and end-to-end on
real bytes with a 2.0e-04 K offset planted at the coarsest level → **`GATE
FAIL`**; and at the parent's own measured 5.43e-03 K → **`GATE FAIL`**. The
one-way property is driven too: gate (1) failed → `NOT A RESULT` whatever the
deviation, and the label ceiling can only weaken and never rescues a `GATE FAIL`.
A gate never shown to fail is not an instrument.

### 6.1 ONE SELFTEST DRIVE NOW FAILS, AND IT IS A STATE DEPENDENCE, NOT A DEFECT — reported, not repaired

`analyse_t9aR1c.py --selftest` returned **`rc = 1`, one failed arm**, when re-run
at this writing:

> `[FAIL] live tree, no DONE markers -> REFUSE (exit 0)`

**The cause is measured and it is not an instrument fault.** Drive 8
(`analyse_t9aR1c.py:934-935`) hard-codes the **live** run root and asserts that
grading it **REFUSES**, because at freeze time no `DONE` marker existed there.
The run has since completed, `DONE.W1c_{c,m,f}` exist, and `grade()` therefore
succeeds (exit 0) instead of refusing. **The drive's precondition disappeared the
moment the rung ran.** The committed selftest evidence records it passing at
freeze time — `T9aR1c_SELFTEST_EVIDENCE.txt:217` and `:369`, both
`[ok ] live tree, no DONE markers -> REFUSE (exit 2)` — which is exactly the
pre-compute state.

- **No verdict rests on it.** The grading path itself returns `rc = 0` and
  reproduces byte-identical output (§1.1); every other drive in the suite passes.
- **It is NOT repaired.** The file is frozen and the rung has fired.
  `VERIFICATION_CHARTER` §2d.1 governs a post-compute grading-path repair and it
  is **not this lane's route**. The finding is recorded and referred; a frozen
  file is not edited (rule 6).
- **Carried forward as a class:** a selftest drive whose precondition is *the
  absence of the rung's own output* is a **one-shot** drive. It is meaningful
  exactly once, before compute, and any later re-run of the suite will report it
  failing. A successor should either scope such a drive to a scratch root or
  register up front that the suite is only re-runnable pre-compute.

## 7. The `REPORTED` rows — N1 to N4, no verdict on any of them

**None of these is graded. None carries a verdict, a band or an uncertainty**,
and they are carried precisely so a reader can see the part `F1` does not cover.

| row | quantity | `W1c_c` (35) | `W1c_m` (56) | `W1c_f` (90) |
|---|---|---:|---:|---:|
| **N1** | \|`T_i1` − exact\| per level | 5.684e-14 K | 3.183e-12 K | 2.899e-12 K |
| **N2** | mesh-family **spread**, max−min of `T_i1` over the three levels read (one number for the family, not per level) | — | **3.240e-12 K** | — |
| **N3** | `q_hot` relative deviation | +5.920e-14 | +3.417e-12 | +3.044e-12 |
| **N4** | \|`T_i2` − exact\| — **the interface `F1` does NOT read** | 5.684e-14 K | 6.821e-13 K | 1.876e-12 K |

**N2 is a `VERIFICATION_CHARTER` §2f.6 BOUND on observed variation over the
meshes actually built. It is not an error estimate, not extrapolated, not a GCI
and not an observed order** — the comparator prints that sentence beside the
number every time it writes it, and it is repeated here for the same reason.

**N1 is not a convergence statement.** The three deviations are not monotone
(5.684e-14 → 3.183e-12 → 2.899e-12 K) and no order may be fitted to them; they
are three round-off residuals, and the registration says so before compute.

**N4 is the honest exposure.** `F1` reads interface 1 only. A treatment wrong
about interface 2 would not be caught by the graded row, which is why interface 2
is reported rather than silently absent — as are the hot-face flux (N3) and the
mesh-family spread (N2).

## 8. Predictions — six of six HIT, and the registration says in advance why that is not evidence

| | prediction (registered `8268ffe2`) | measured | |
|---|---|---|---|
| **P1** | \|dev(`W1c_c`)\| < 1e-06 K | 5.684e-14 K | **HIT** |
| **P2** | \|dev(`W1c_c`)\| / 5.43e-03 K < 1e-04 | **1.047e-11** | **HIT** |
| **P3** | N3 \|`q_hot`/`q_exact` − 1\| < 1e-09 at every level | 5.92e-14 / 3.42e-12 / 3.04e-12 | **HIT** |
| **P4** | N2 spread < 1e-08 K | 3.240e-12 K | **HIT** |
| **P5** | N4 \|`T_i2` − exact\| < 1e-06 K at every level | 5.68e-14 / 6.82e-13 / 1.88e-12 K | **HIT** |
| **P6** | gate (1) holds at every level, checkpoints agree to < 1e-09 K | **0.000e+00 K** at all three | **HIT** |

**A clean sweep here is worth almost nothing and the registration said so before
the solver started.** §0.6, frozen: *"THIS IS NOT A FRESH PREDICTION AND IT MUST
NOT BE READ AS ONE. THE ANSWER IS ALREADY KNOWN… `W1c_c` will reproduce
2.899e-12 K."* The cases are byte-identical in physics to W1b's — same parent
blobs at the same T9a freeze sha, same single `laplacianSchemes` line, same
solver, same iteration count, serial and deterministic. **This rung is
RE-INSTRUMENTATION, not corroboration**, and six hits are evidence that the
instrument works as registered and of nothing beyond that.

**P2 deserves its own line because it is the one comparison that discriminates.**
The parent's own registered scheme, `Gauss linear corrected`, deviates
**−5.43e-03 K at this very level** (`T9a_RESULTS.md` §1.1). The registered floor
would **`GATE FAIL` the parent's scheme by 54×** at 35 cells. So the gate is a
control and not an identity: a different, defensible interface treatment fails
it, measurably, on the record.

## 9. WHAT THIS RUNG DOES NOT ESTABLISH — read this before citing it

**A floor demonstration shows that an instrument can resolve below a threshold at
a stated mesh. It is not a validation of any physics.** Everything in this
section was registered before compute, and it is restated here because a
`PASS` travels further than the sentence that qualifies it.

1. **It is NOT grid convergence, and NOT mesh independence.** No observed order,
   no GCI, no Richardson extrapolate, no triple. The claim is bounded by the
   meshes actually run and **extrapolated to none**. A phrase to the contrary —
   *"so the answer does not depend on the mesh at the resolution that matters"* —
   was in version 1.0 of the registration, was taken verbatim from
   `VERIFICATION_CHARTER` §2g.3 and copied by everyone who quoted it, and was
   **struck** under §2h.4(5) before compute. It is absent from every artifact of
   this rung, measured by the text sweep. It must not be reintroduced here.
2. **It is NOT "the solution is correct to `X`".** That is a continuum claim and
   `VERIFICATION_CHARTER` §2f.3 caps it. The claim is: *the discretisation error
   in `T_i1` is below `X` = 1.0e-04 K at 35 cells.* That, and no more.
3. **It carries NO uncertainty on any number.** With no triple there is no
   discretisation uncertainty, and none of the round-off residuals in §7 may be
   given one.
4. **It says nothing about anything `F1` does not read**: interface 2 as a graded
   quantity, the fins (T9a's F rows), transient conduction, 2-D or 3-D
   conduction, radiation, convection, or any coupled case. A treatment wrong
   about those and right at interface 1 would pass this gate — the ways are
   named, not denied, at registration §3.4(2).
5. **It is NOT a corroborating second measurement of `T9a-R1b`.** The inputs are
   byte-identical in physics; a second run of the same bytes corroborates
   nothing. §0.6 forecloses that reading in advance and this record adopts it.
6. **It does NOT rescue, re-grade or amend `T9a-R1b`.** W1b's R1 row stands
   `NOT A RESULT` on its Roache limb under `VERIFICATION_CHARTER` §2g, with its
   measurement `REPORTED` beside it; the frozen `gate_t9aR1b.json` was not edited
   and will not be. **W1c is the successor §2g.3 ordered, not a repair of the
   predecessor's verdict.**
7. **It does NOT settle the capability-grid question.** Whether this rung counts
   toward the conduction × laminar × 1-D steady cell is the supervisor's call and
   the grid is not amended by this record.
8. **The margin is nine orders wide, and a gate cleared by nine orders
   discriminates very little.** What makes the gate non-vacuous at all is P2: the
   parent's own scheme fails it by 54× at the same resolution. Absent that
   comparison, a 5.7e-14 K deviation against a 1e-04 K floor is a statement about
   double-precision arithmetic more than about a discretisation.

## 10. Cost — rule 12, estimate against actual

**The registered primary basis is `ExecutionTime`, per level, adopted BEFORE
compute** (registration §9.1) on W1b's transferable finding that below about one
wall-second the core-minute wall basis returns 0, and that a 0 there means *too
small to measure*, not *free*.

| level | cells | predicted [core-min] | measured `ExecutionTime` | measured [core-min] | ratio |
|---|---:|---:|---:|---:|---:|
| `W1c_c` | 35 | 0.000833 | **0.05 s** | 0.000833 | **1.000×** |
| `W1c_m` | 56 | 0.000833 | **0.06 s** | 0.001000 | **1.200×** |
| `W1c_f` | 90 | 0.001000 | **0.06 s** | 0.001000 | **1.000×** |
| **total** | | **0.002667** | **0.17 s** | **0.002833** | **1.063×** |

- **Gross = cleaned.** No level is within three orders of the 3600 wall-s stall
  rule; no cleaning applied.
- **Cap: 1 core-min per level, 3 total.** Headroom used: **0.094 %**. No overrun.
- **The wall basis is UNRESOLVED, not a ratio.** All three `STATUS.W1c_*` read
  `wall_s = 0`, `core_min = 0.000`, exactly as the registration predicted;
  `0.000 / 0.0045` would enter a false perfect-underspend into the ledger and is
  **not** stated as a ratio.
- **Gap attribution: one clock quantum on one level. No contention. Waste
  0.000 core-min, named separately.** OpenFOAM prints `ExecutionTime` to 0.01 s,
  so on a 0.05 s measurement one quantum **is** 20 %. `W1c_m` came in at 0.06 s
  against 0.05 s carried from `W1b_m`; the gap is below the instrument's
  resolution and **no rate should be revised from it.**
- **Dollars: predicted $2.28e-06, actual $2.42e-06 — DERIVED, NOT MEASURED**, at
  $0.0513/core-h, c7a.4xlarge, owner-stated (Sanaa 2026-08-21/22). The box cannot
  read its own billing (`COMPUTE_BUDGET_CHARTER` §5), so `cost_basis` is
  **reported-by-owner**.

**The calibration row required by rule 12 ALREADY EXISTS and no duplicate was
added by this record.** `docs/COST_CALIBRATION.md`, row
**`C-20260903T180449.568767Z-c7e2af11`** (2026-09-03), carries the per-level
comparison, the 1.063× ratio, the UNRESOLVED wall basis and the clock-quantum
attribution. Its figures were re-measured against the same artifacts at this
writing and **agree**. That row states the rung verdict as `PASS`; **this record
is where that verdict is actually issued, from the comparator, and the row's
statement of it is thereby made good rather than left free-standing.**

## 11. Disclosures

1. **The `X` provenance hazard, disclosed by the registration itself and not
   softened here.** The lane that wrote the registration **knew W1b's measured
   2.899e-12 K before choosing `X`** (§3.3, frozen). What disposes of the concern
   is arithmetic rather than provenance: `X` sits inside a window
   [1.0e-06, 9.2e-04] K whose three walls all come from T9a's record registered
   2026-08-20/22, and **every candidate `X` anywhere in that window yields the
   identical verdict** (margins 5.54 to 8.50 orders). The verdict flips only for
   `X` ≤ 2.899e-12 K, which is 345× below the round-off floor. **No `X` that
   could be defended at all flips it.** What cannot be claimed — and is not —
   is that a lane ignorant of the answer would have landed on the same decade.
2. **The evidence set was UNTRACKED for six days.** From 2026-08-28 until
   `c679b7c4` (2026-09-03) the gate file, the grade output, the `STATUS`/`DONE`
   markers and the three case trees were held by no commit — an arm `PASS`
   resting on files git did not hold. Landed at `c679b7c4`, 56 explicit paths.
   Disclosed, not smoothed over.
3. **The verdict was owed from 2026-08-28 and is issued on 2026-09-04.** The
   grading ran on 2026-08-28 and no results record was written;
   `T_FAMILY_INDEX.md` §5.3 carried `T9aR1c` as *"no `*_RESULTS.md`; no rung
   verdict — STILL OPEN"* through 2026-09-03. **An arm `PASS` is not a rung
   verdict**, and for seven days this rung had the former and not the latter.
4. **One selftest drive now fails by state dependence** — §6.1. Reported, not
   repaired; a frozen file is not edited and §2d.1 is not this lane's route.
5. **`scripts/check_filing.py` enumerates paths from `HEAD`**, so at
   pre-registration time it was structurally blind to this rung and its zero was
   a **false zero** — proved at the time by planting a file named `Bad Name
   PLANT.md` in the run directory and watching the total not move (registration
   §8.2). The artifacts are committed now; the checker was re-run against this
   record and reports **no `T9aR1c` or `W1c` violation and no increase in the
   pre-existing total.**
6. **`sweep_wording_t9aR1c.py` is deliberately NOT in the freeze set** and never
   was. It grades no case and reads no run output; it checks this rung's own
   documents, and freezing it would mean a later correction to a document could
   not be re-checked. Its hash is recorded at §1 for drift, not for freeze.
7. **Nothing was sent. SUBMISSIONS REMAIN PARKED** (rule 7). Nothing in this rung
   has been filed, uploaded, registered, posted or communicated outside this box.
