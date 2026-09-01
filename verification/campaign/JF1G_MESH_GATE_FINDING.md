# JF1G — FINDING: MY OWN FROZEN MESH GATE FAILS THE FINEST LEVEL ON THE ONE QUANTITY THE LAB'S MESH STANDARD SAYS IS NEVER A LONE REJECTION

**Status: `FINDING`, and the study as frozen is `NOT A RESULT` on Gate G1.** The runs
that exposed it are `LABEL: diagnostic` and score nothing. Raised to
`cfd-supervisor`. **This lane has NOT amended the registration** — moving a frozen
gate is not a lane's call, and this document exists to put the question up with the
arithmetic already done.

- **Registration:** `verification/campaign/JF1G_GRID_CONVERGENCE_PREREGISTRATION.md`,
  frozen **`038f4bca`**, blob `0b947659…`, 2026-09-01 ~16:05Z.
- **Found by:** the `cfd` lab-lane that wrote the registration, from its own C3 mesh
  build, ~40 minutes after freezing it.

---

## 1. WHAT HAPPENED

Gate G1 of `038f4bca` requires every clause of §2.2, whose last row reads
**`checkMesh` | `Mesh OK` on every level**. §6.1 refusal 2 repeats it.

The three meshes were emitted at **exactly** the frozen §2 cell counts — 39,984 /
89,964 / 202,180 — so the `--n-rad` similarity repair that the registration exists to
enforce worked. **C1 and C2 print `Mesh OK`. C3 does not:**

```
***High aspect ratio cells found, Max aspect ratio: 1012.242839, number of cells 2
Failed 1 mesh checks.
```

`run_jf1g.sh` refused at `stage_at_exit checkMesh`, `rc 5`, having spent **0.0667
core-min**. The refusal worked exactly as designed. **The gate it enforced is the
problem.**

| level | max aspect ratio | max non-orthogonality | max skewness | `Mesh OK` |
|---|---|---|---|---|
| C1 (39,984) | 859.95 | 57.53 | 2.296 | **yes** |
| C2 (89,964) | 634.44 | 67.64 | 2.213 | **yes** |
| C3 (202,180) | **1012.24** | 75.14 | 2.181 | **NO** |

**Two cells out of 202,180 — 0.001 % of the mesh — fail the study.**

## 2. WHY THIS IS A REGISTRATION DEFECT AND NOT A MESH DEFECT

`docs/standards/MESH_STANDARD.md` is the lab's standing mesh authority. Its §3.3 is
titled, verbatim:

> **"Aspect ratio: advisory at 1000, never a lone rejection"**

and §11 (v1.6, 2026-08-27) records that **aspect ratio and cell-volume ratio became
*reported* mesh-admission evidence and that NO THRESHOLD IS SET FOR EITHER.** The
same section records the standard's reasoning that non-orthogonality and skewness are
"the load-bearing ones", and that a wall-resolved mesh **buys wall resolution with
aspect ratio, not with cell count** — which is precisely what a `y+ < 0.4` boundary
layer does.

**And §3.3 carries the calibration that settles it, in the standard's own words:**

> *"the NASA TMR flat-plate grids are reference-grade by construction, and their
> checkMesh reports on disk measure max aspect ratio **74041** (coarse), **69043**
> (medium), **66643** (fine) … **A hard aspect-ratio gate at 1000 would reject every
> reference-grade wall-resolved RANS grid the lab owns.**"*

**C3's max aspect ratio of 1012 is roughly 65× BELOW the reference-grade grids the lab
already holds and validates against** — grids that resolve the wall to average `y+`
0.14 and reproduce the flat-plate drag benchmark, at max non-orthogonality 0 and
skewness at machine precision. C3 is not a bad mesh by this lab's own calibration; it
is an ordinary wall-resolved one.

**`Mesh OK` bundles the advisory quantity into a hard pass/fail.** By writing
`Mesh OK` into Gate G1 I registered a gate **stricter than the lab's own standard**,
which then rejected the finest level for the single reason the standard says is never
a rejection on its own. **C3's non-orthogonality and skewness — the load-bearing
checks — both pass.**

**This is L-409's class, and I registered it having read that class this morning** in
`JF1_GATE6_FINDING.md`, whose whole subject is a JF1 gate that no run could ever
satisfy. §17.3-style satisfiability was not performed on Gate G1's mesh clause; had it
been, the question "can the finest level of a wall-resolved family print `Mesh OK`?"
was answerable from `MESH_STANDARD.md` §3.3 alone, before any mesh was built.

## 3. THE SECOND FINDING, WHICH IS A REAL MESH DEFECT AND IS SEPARATE

While triaging the above I measured that **`build_jf1.py`'s `--normal-smooth` is a
FIXED pass count that never scales with the ladder** (`build_jf1.py:446` passes
`args.normal_smooth` raw). Its consequence is visible in a quantity that geometric
similarity requires to be *invariant*: **max non-orthogonality drifts 57.53 → 67.64 →
75.14 across the family.**

**A prediction was made before the probe was run.** A discrete Laplacian smoothing's
diffusion length in node-index space goes as `sqrt(passes)`; to cover the same
*physical* arc when the node count scales by `s`, the pass count must scale as **`s²`**.
That predicts 500 / 1125 / 2531 for `s` = 1.000 / 1.500 / 2.250.

**Measured, by sweeping `--normal-smooth` at each level:**

| level | `s` | `500·s²` | max non-orthogonality **at `500·s²`** | at the unscaled default 500 |
|---|---|---|---|---|
| C1 | 1.000 | 500 | **57.53** | 57.53 |
| C2 | 1.500 | 1125 | **58.62** | 67.64 |
| C3 | 2.250 | 2531 | **58.89** | 75.14 |

The sweep's minimum lands on the predicted value at every level (C3 probed at 500 /
1125 / **2531** / 4000 / 6000 → 75.14 / 68.41 / **58.89** / 62.62 / 65.87 — a clean
interior minimum). **Under the `s²` law, max non-orthogonality is 57.53 / 58.62 /
58.89 across a 5× cell-count range: invariant, as similarity requires.** The
generator's own comment records 500 as a broad flat minimum found on this geometry at
the baseline resolution; the `s²` law reproduces that minimum at every level.

**This is the same defect class as the `--n-rad` finding in `038f4bca` §1 — a
generator parameter that does not scale with the ladder — and it is the second
instance in one afternoon.** It is a genuine similarity improvement and it is
independent of §2's frozen table: smoothing moves node *positions*, never counts, so
**every frozen cell count and every §2.2 ratio is unchanged by it, and C1 is
untouched (`500·1² = 500`), so C1 remains bit-identical to the grid the five
2026-08-31 sweep rows ran on.**

**⚠ It does NOT fix the aspect ratio.** AR is insensitive to smoothing across the
whole sweep (C3: 1012.24 → 1012.93 from 500 to 6000 passes). The two findings are
unrelated and neither remedies the other.

## 4. WHAT IS NOT KNOWN, STATED RATHER THAN CONSTRUCTED

**The mechanism of the aspect-ratio non-monotonicity — 860 → 634 → 1012 — is not
established.** Under uniform refinement AR should be roughly invariant, and it is
neither invariant nor monotone. Candidate causes not yet separated: integer rounding
of `n_side` (198 → 297 → 446, where 445.5 is exact); the fixed `--tang-ratio 1.12`
growth cap redistributing the two-sided tangential blend differently as cell count
grows; and the max simply relocating among discrete cells. **No claim is made about
which, and no number in this document depends on the answer.**

## 5. THE QUESTION FOR THE SUPERVISOR, AND IT IS A GATE-DESIGN QUESTION

**Rule 2 closes gates at first compute. C1 and C2 Pass-0 solves are running against
`038f4bca` right now, so on the literal reading Gate G1 is shut and JF1G as frozen is
`NOT A RESULT`, permanently.**

There is an argument the other way, and it is *not* this lane's to accept: **Pass 0 is
registered `LABEL: diagnostic` and §4 says in terms that it scores nothing and that no
`PASS`, `GATE REACHED`, observed order or GCI may be quoted or implied from it.** A
run whose output can never become a verdict cannot be used to fit a gate to an answer,
which is the hazard rule 2 addresses. **That is the identical argument
`JF1_GATE6_FINDING.md` §5 put to Sanaa and which she has not ruled on.** This lane
does not get to help itself to an unruled reading.

**Recommendation, offered and NOT acted on — reissue under a new sha, as `F23b`'s
successor was**, rather than amend `038f4bca`. A successor registration would:

1. **Align the mesh gate to the lab's own standard**: gate on **non-orthogonality and
   skewness**, and **report** aspect ratio and cell-volume ratio as
   `MESH_STANDARD.md` §3.3 and §11 require. **The change is pinned to a standing
   standard written 2026-08-27, six days before this study, not to anything read off
   a result** — the same structure that made the gate-6 `cos τ` repair non-answer-
   fitting.
2. **Register `--normal-smooth = 500·s²`** as a similarity clause with the §3 table as
   its derivation and confirmation.
3. **Change nothing else** — not the ladder, not the cell counts, not the `r`, not the
   graded quantity, not the tightness rule, not the acceptance band on `p`, not a cap.
4. **Carry no `CL` value forward.** No Pass-1 solve has run, so **no graded number
   exists that a reissued gate could have been fitted to**, and that is the strongest
   thing that can be said for the reissue's integrity.

**Until the supervisor rules, JF1G stands as frozen and is `NOT A RESULT` on Gate G1.**
The C1 and C2 Pass-0 solves continue — they score nothing, they cost 70.7 core-min
between them, and they are the only reason both of these findings surfaced before a
graded pass spent its budget on a gate the finest level could never pass.

---

**SUBMISSIONS PARKED.** Nothing in or derived from this document is sent, filed,
uploaded, posted or registered outside this box.
