# G1b — regrade of the G1 grid triple with a repaired fatal clause: RESULT

**RUNG VERDICT: `NOT A RESULT`.**

**And that is the headline, because it is the verdict the successor was NOT built
to produce.** The comparator was frozen at `dc61e9b5` before any functional value
existed, with every band copied verbatim from G1. It ran, it read the physics it
had never been allowed to see, and the answer did not improve. **A successor that
repaired an instrument and then failed to rescue the verdict is the strongest
evidence available that the ordering was honest.** Had G1b returned `PASS`, a
reader would be entitled to ask whether the repair had been shaped to produce it.
It did not, and that question is closed by the outcome rather than by assertion.

Graded 2026-08-28T16:30Z. Comparator sha256
`614e52064b8ade5dbe109c632ddea23274157a263eaf6755b822d1fc3d02535b` — **verified
identical on disk and in the committed blob at the freeze commit**, which is
rule 2's check that the frozen file is the file that ran. Exit status 1. Raw
stdout at `artefacts/g1b_grading_stdout_2026-08-28T1630Z.txt`.

---

## 1. The instrument repair worked, and it is proved in both directions

The comparator ran its new fatal control **before** the completion clauses that
consume it, and all nine fixtures behaved:

- **Positive, 8 of 8** — `FOAM FATAL ERROR`, `FOAM FATAL IO ERROR`,
  `sigFpe::sigHandler`, `sigSegv::sigHandler`, `Foam::error::printStack`,
  line-anchored `Floating point exception`, line-anchored `Segmentation fault`,
  and a realistic combined sigFpe trace — each written to disk, each read back
  `fatal=True` **for its own token**.
- **Negative, 1 of 1 — the direction that mattered** — a clean log carrying the
  `trapFpe` banner verbatim plus `End` read back **`fatal=False`**, after the
  control first confirmed the **old** G1 clause *does* fire on that same fixture.

**All three levels then passed completion**, where under G1's clause all three
had refused: rc 0, `End`, last time == endTime, fields present, age guard held,
`ExecutionTime` lines == endTime, residuals below registry, `gradP` plateaued —
L1, L2 and L3 alike. The three original planted controls (`gradP`, `Kint`, `xr`)
all round-tripped. The **read-only witness** reports **153 files** under the run
root with a stat digest **identical before and after** the grading pass: the
evidence was not touched.

The defect is carried into the record as infrastructure, never as a gate: clause
**I5** reports, per level, that the old clause matches exactly **1** line and
that **1** of those is the `trapFpe` banner.

## 2. The rung is `NOT A RESULT` for a REAL and PHYSICAL reason: the triple is DIVERGENT

| functional | L1 (3,840) | L2 (15,360) | L3 (61,440) | eps21 | eps32 | R | triple |
|---|---|---|---|---|---|---|---|
| **gradP** (primary) | 0.00842876291327 | 0.00843900963202 | 0.00852655352769 | 8.754390e-05 | 1.024672e-05 | **8.5436** | **DIVERGENT** |
| Kint (secondary-A) | 0.124425376623 | 0.124541912604 | 0.125086984736 | 5.45072e-04 | 1.16536e-04 | **4.6773** | **DIVERGENT** |
| xr (secondary-B) | — | — | — | — | — | — | no value on any level |

Standing rule 5 step 2: a triple classed `DIVERGENT` is `NOT A RESULT` whatever
its value, with the value and the triple printed beside it. **No observed order
and no GCI is quoted, and none was computed** — the comparator returns before
that arithmetic on any non-monotone branch. The gate turned a verdict **into**
`NOT A RESULT` and could not have done the reverse.

**What DIVERGENT means here, stated precisely.** `R = eps21/eps32 = 8.54 >= 1`
means the differences between successive levels **grow** under refinement instead
of shrinking. Concretely: **L1 → L2 moves gradP by 0.1216 %, and L2 → L3 moves it
by 1.0374 % — the later, finer step is 8.5x the larger.** L1 and L2 are nearly
the same answer and L3 departs from both. **The solution is not in the asymptotic
range on this grid family**, so Richardson extrapolation and a GCI would be
meaningless here and are correctly withheld. It is not a statement that the
solver is wrong, and it is not a statement that any value above is wrong.

**This is a finding about the case, not about the instrument**, and it is
separable from the fatal-clause defect because iterative error is excluded: every
level converged to final initial-residuals of 1e-9 to 1e-11 (`Ux` 3.312e-09 /
3.663e-10 / 4.018e-11), far below the 1e-5 registry, and `gradP` plateaued on all
three. What remains between the levels is **discretisation**, which is what the
triple is measuring.

## 3. The secondary that produced nothing, recorded rather than dropped

`xr` returned **no value on any level**: there is **no negative-to-positive
`tau_wx` crossing at x >= 0.5** on L1, L2 or L3. The crossing finder is not
blind — its planted control recovered a crossing planted on disk at x = 4.234500
in the same run and refuses on a profile with none.

So the reading is that **the registered reattachment criterion finds no
reattachment point on any of the three meshes.** That is a substantive result
about the computed flow and it is **left as a finding, not repaired**: changing
the criterion after seeing that it returned nothing is precisely the
answer-shaped edit the anti-gaming clause forbids. It is docketed for a
successor to diagnose under the L0 step of the non-convergence ladder — is the
separation bubble absent, is it present but not crossing the registered
threshold, or is the shear-stress component being read on the wrong patch or
sign convention. **Not guessed here.**

## 4. What must NOT be done next, and it is the important half

The divergent triple has an obvious and forbidden remedy: widen the `p` band, or
loosen the GCI ceiling, or swap the functional for one that behaves. **Every one
of those is barred.** `VERIFICATION_CHARTER` §2d.1 is explicit that a band is not
an instrument — *"nothing a verdict depends on may be repaired on the authority
of the verdict it produces"* — and Sanaa's §3 anti-gaming clause is absolute:
answer-changing choices are never selected by agreement with a reference, and
converged-but-wrong is `NOT HELD` with a diagnosis, never a parameter hunt.

The legitimate next step is a **fourth, finer level** (L4 at 245,760 cells) so
the triple can be re-formed as L2/L3/L4 and asked whether it converges once the
coarse level is dropped. That is a **new registration with its own frozen bands
and its own cap**, not an amendment of this one, and it is **costed before it is
proposed**: L3 measured 115.48 core-min at 61,440 cells, and the L2 → L3 step was
**superlinear**, so an L4 estimate built on a cell-count ratio would repeat
exactly the error this family already paid for at C-190. **No L4 estimate is
published here on that basis.** It is docketed with the requirement that its cost
come from a measured short pilot, not a ratio.

## 5. Cost, and the estimate-versus-actual calibration (rule 12)

| | value |
|---|---|
| new solver compute | **0.000 core-min** — the physics was already on disk; its 127.08 core-min is charged to G1 at `C-190` and is not double-counted |
| grading pass registered estimate | 1.0 core-min (cap 10.0) |
| **grading pass measured** | **0.188 core-min** (11.26 s wall, 1 rank; user 10.83 s, sys 0.26 s) |
| ratio actual/estimate | **0.188** |
| MaxRSS | 197,292 kB |
| dollars | **$0.00016 derived, not measured** at $0.0513/core-h |

**The whole repair-and-regrade cost about a fifth of a core-minute** against a
127-core-min run it re-read. That number is the argument for the successor route
made in `G1_grid_triple/RESULTS.md` §5, now measured rather than asserted: given
a choice between editing a frozen comparator and re-freezing a successor, the
successor cost 0.188 core-min and preserved a verifiable freeze.

## 6. Standing limit, unchanged

This rung grades **numerical convergence only**. It says nothing whatever about
agreement with LES or DNS truth: no reference field is read and none exists on
the L1 or L3 meshes. A divergent triple is a statement about grid behaviour, not
about physical accuracy, and neither is it evidence of physical accuracy.
