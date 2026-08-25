# K0d pre-flight executability finding — LAUNCH ABORTED BEFORE FIRST COMPUTE

**Verdict: `BLOCKED`.** K0d was **not** launched. **Zero core-seconds were
consumed.** No case directory was built, no mesh was generated, the registered
pre-flight smoke test of `AMENDMENT 2` **was not run**, and
`verification/runs/F14-cooling-ladder/K0d_runs/` **still does not exist**.

Written 2026-08-25 by the heat-transfer lane dispatched to fire the rung.
**The abort is a finding about the pre-registration, not about the box**, and
under `SUPERVISION_CHARTER.md` §3 check 2 its triage is the supervisor's and is
not delegable to this lane.

---

## 1. The state this record was written in, and how it was checked

Checked in the shell invocation that preceded this write:

```
ls -d verification/runs/F14-cooling-ladder/K0d_runs   -> No such file or directory
find verification/runs -maxdepth 3 -iname '*K0d*'     -> nothing
find /home/ubuntu/certonomous-runs -iname '*k0d*'     -> nothing
```

**K0d has never consumed a core-second.** The pre-compute amendment window of
rule 2 is therefore **still open at the moment of this write**, and that is the
operative fact of this record — see §5.

**The freeze was verified before anything else.** `sha256` of
`docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md` on disk against its
committed blob at `HEAD` (`c420f3e5`):

```
disk = 8b1340d69cce6262c2e545692b15aed2da9c174d3930986dc91b35e3c9da0918
blob = 8b1340d69cce6262c2e545692b15aed2da9c174d3930986dc91b35e3c9da0918
```

**Identical.** The document that was read is the document that was frozen.

---

## 2. THE FINDING — §8.2 clause 4 requires a field that three of the nine registered cases cannot write

### 2.1 What the frozen document binds

§8.2 lists seven **binding conditions, "all of which must hold"**, for a case to
be certified complete. Clause 4 reads:

> 4. **`T U p_rgh alphat nut k omega` all present** at `endTime` (`C_lam` is
>    exempt from `nut k omega` and that exemption is registered here, not
>    discovered later)

**`omega` is named literally, and exactly one exemption is registered: `C_lam`.**

### 2.2 What the registered cases actually write — measured on this box, with both states visible

§5 registers nine cases. Three of them — `M2_c`, `M2_m`, `M2_f` — run
**`RNGkEpsilon`**, a `k`–`ε` closure. A `k`–`ε` closure does not carry an
`ω` field and `buoyantBoussinesqSimpleFoam` does not write one for it.

**This was not asserted from recall. It was read off completed runs of the same
solver, on this box, with a control that shows the reader can see both states**
(the planted-zero discipline of rule 3 applied to a directory listing):

| completed sibling case | closure | `omega` at `40000`? | `epsilon` at `40000`? |
| --- | --- | --- | --- |
| `K0cS_runs/S_SST_f` | `kOmegaSST` | **PRESENT** | absent |
| `K0cS_runs/S_KE_f` | `kEpsilon` | **ABSENT** | **PRESENT** |
| `K0cS_runs/C1_laminar` | laminar | absent | absent |

Both branches fire. A listing that reported "no `omega`" for `S_KE_f` while
being unable to see an `omega` anywhere would be worthless; `S_SST_f` is the
non-zero the reader was shown able to see.

**The laminar row independently confirms §8.2's `C_lam` exemption is correct**:
`C1_laminar` wrote `T U p_rgh alphat` and none of `nut k omega`, exactly as
registered. The exemption that *is* registered is sound. The one that is
**missing** is the `k`–`ε` one.

### 2.3 The consequence, and it is not confined to the `M2` leg

§8.2 closes with:

> **`analyse_k0d.py` refuses (exit 2) unless all nine `DONE.<case>` markers are
> present.**

Under the literal reading of clause 4, `M2_c`, `M2_m` and `M2_f` can **never**
earn a `DONE` marker, however cleanly they run. The comparator then **refuses
for the whole rung**. **All nine cases would run to completion and the rung
would grade nothing** — not `GATE FAIL`, not `NOT A RESULT` on the `M2` rows
only, but a comparator that exits 2 and produces no verdict at all.

**That is what makes this an abort rather than a disclosure.** The exposure is
the full registered POINT cost of **829.36 core-min**, not the `M2` leg's
**296.32 core-min**.

---

## 3. The honest counter-reading, stated because this lane must not overstate a defect

There is a second reading of §8.2 and it is not frivolous. The section's own
preamble says:

> `mark_done_k0d.py` applies, **for the thermal field set**, the rule that
> section states verbatim

On that reading, *"the thermal field set"* is the generic obligation, the
enumerated `T U p_rgh alphat nut k omega` is the **`kOmegaSST` instance of it**
quoted from `T1b_L4_AMENDMENT.md` (a `kOmegaSST` rung), and a correctly written
`mark_done_k0d.py` would take each case's own model field set — `epsilon` for
`M2`, `omega` for `M1`. Under that reading there is no defect, only a script yet
to be written correctly.

**This lane does not adopt that reading, for two reasons, and it does not adopt
the other one either — it refers both.**

1. Clause 4 sits inside a list introduced as *"this rung's binding conditions,
   **all of which must hold**"*, and it names `omega` literally.
2. The clause's own parenthetical — *"that exemption is registered here, **not
   discovered later**"* — is an explicit instruction that exemptions are
   pre-registered rather than inferred at run time. **A lane inferring a second,
   unregistered exemption for `M2` would be doing precisely what that phrase
   forbids**, on its own authority, to a frozen instrument.

**The ambiguity is itself the finding.** Whichever reading is right, it is the
supervisor's ruling and not this lane's, and the brief that dispatched this lane
was explicit: *a pre-registration that cannot be executed is a finding, not
something to reinterpret.*

---

## 4. This is the same defect class `AMENDMENT 2` was written to catch, one layer up

`AMENDMENT 2` §A2.2–A2.3 registered the pre-flight smoke test because **a
comparator selftest proves the grader, not the case**, and because a dictionary
can be **complete for one regime and incomplete for another** — VMFL045 crashed
at wall 0 s on an entry VMFL051 never needed, the two being separated by
`μ > 0`.

**This defect has the identical shape and sits one layer further out.** The
completion instrument is complete for the `kOmegaSST` regime it was quoted from
and incomplete for the `k`–`ε` regime `M2` introduces. It is **latent**: it does
not announce itself in review, it does not crash, and it would not have been
caught by the smoke test either — the smoke test exercises the **solver
dictionaries**, and this entry is in the **completion instrument**, which runs
only after 829 core-minutes have already been spent.

**`AMENDMENT 2` closed the case-dictionary hole. This is the instrument-side
hole of the same class, and it is recorded here rather than repaired here.**

---

## 5. WHY THIS WAS STOPPED BEFORE THE SMOKE TEST, AND NOT AFTER IT

This is the load-bearing operational point of the record.

`AMENDMENT 2` §A2.5 states of the smoke test: *"It is charged to K0d's rung and
appears in K0d's calibration row."* **The smoke test is K0d compute.** Running
it — or merely building the case tree, which falsifies the
`K0d_runs/ does not exist` check both amendments used to establish their own
legality — **closes the rule-2 pre-compute amendment window permanently.**

The asymmetry decided the abort:

| | if ruled **now** | if ruled **after first compute** |
| --- | --- | --- |
| legal instrument | a **pre-compute amendment**, which rule 2 permits to alter anything | only a **dated addendum**, which *"cannot alter a gate, threshold, cap or label"* |
| status of the fix | clean, uncontested | must argue itself through `VERIFICATION_CHARTER.md` §2d.1's four-condition repair exception, whose load-bearing condition (2) requires the error to have been found by an instrument **independent of the hypothesis** |
| cost of being wrong | one supervisor round trip | up to **829.36 core-min** graded by nothing |

**A window that is free to use now and contested later, guarding an exposure of
the entire rung, is not a window to spend a core-second against.**

---

## 6. CHECKED AND FOUND SOUND — recorded so a check that found nothing is distinguishable from a check never made

Per the practice `AMENDMENT 1` §A1.4 established. All of the following were
checked in this pre-flight and **none is a defect**:

| # | checked | result |
| --- | --- | --- |
| 1 | `buoyantBoussinesqSimpleFoam` **binary**, not merely the source tree §3.5 cites | **present and executable**, `platforms/linux64GccDPInt32Opt/bin/` |
| 2 | `RNGkEpsilon` instantiable for the **incompressible/Boussinesq** model set | **present** — 7 defined symbols in `libincompressibleTurbulenceModels.so`; control: `kOmegaSST` 48. Both visible, so the reader is shown able to see a present model and would have shown an absent one |
| 3 | §4 block arithmetic | `n_A + n_B + n_C = N_y` on all three levels (12+138+10=160; 17+193+14=224; 24+270+20=314) and `N_x × N_y` reproduces **25 600 / 50 176 / 98 596** exactly. §4 condition A is satisfiable |
| 4 | §4 condition B, slot cell counts | inlet slot **is** block C (`n_C` = 10/14/20 vs the required ≥ 10/14/20) and outlet slot **is** block A (`n_A` = 12/17/24 vs ≥ 12/17/24). Satisfied, **exactly at the bound on every level** — noted because there is no margin |
| 5 | §4 condition C, per-block ratio 1.40 ± 0.05 | block A 1.4167 / 1.4118; block B 1.3986 / 1.3990; block C 1.400 / 1.4286; `N_x` 1.400 / 1.4018. **All inside** |
| 6 | §4 condition D feasibility, first wall cell by two-sided geometric grading | arithmetically feasible on every block and both directions at the registered first-cell sizes. **Checked by arithmetic only — no mesh was built**, see §8 |
| 7 | §6 vs §10 durability | `writeInterval 4000`, `purgeWrite 2` retains `36000` and `40000` — exactly the two checkpoints §6's convergence criterion reads. Consistent |
| 8 | §8.2's `C_lam` exemption | **correct**, confirmed against `C1_laminar` (§2.2) |
| 9 | frozen file integrity | disk `sha256` == committed blob at `HEAD` (§1) |
| 10 | the box, before any launch | one foreign solver live — a `cfd` `pimpleFoam`, pid 2150855, ~200 s elapsed, 1 rank. **Not touched.** `T-family/T1_runs` carries `DONE` markers and no live process. 16 cores, load ~1.15 |

**On item 10 and the dispatching brief.** The brief that dispatched this lane
stated *"THE BOX IS CURRENTLY IDLE — no solver is running anywhere."* **That was
not true at dispatch**, and it is corrected here rather than carried: the `cfd`
team's `F5b physics_p1` `pimpleFoam` was and is running. It does not obstruct
K0d — one rank of sixteen, against a registered concurrency cap of 6 — but a
launch plan that assumed an empty box would have been built on a stale read, and
`AMENDMENT 2` §A2.4 records what a stale read of exactly this kind nearly cost
the ansys-verification team.

---

## 7. What the supervisor is asked to rule, and the launch that is ready behind it

**One ruling is needed, and nothing else is blocked.** Either:

- **(a)** issue `AMENDMENT 3` before first compute, registering the `M2`
  completion field set explicitly (`T U p_rgh alphat nut k epsilon`) alongside
  the `kOmegaSST` set and the existing `C_lam` exemption; or
- **(b)** rule that §8.2's *"thermal field set"* preamble governs and clause 4's
  enumeration is the per-model instance — in which case the ruling itself should
  be registered in the open window, so `mark_done_k0d.py` is not left resting on
  a lane's inference.

Either disposition is **purely subtractive-safe**: it changes no gate, no
threshold, no band, no cap, no label and no prediction, and it cannot turn a
`GATE FAIL` into a `PASS`. It only decides which cases can be certified
complete.

**The launch is built and costed and can fire immediately on the ruling.** The
plan this lane prepared, recorded so no successor re-derives it:

| case | closure | level | cells | POINT core-min | **enforced ceiling, core-min** | **`timeout` wall s (1 rank)** |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `M1_c` | kOmegaSST | L1 | 25 600 | 43.50 | 87.00 | 5 220 |
| `M1_m` | kOmegaSST | L2 | 50 176 | 85.27 | 170.54 | 10 232 |
| `M1_f` | kOmegaSST | L3 | 98 596 | 167.55 | 335.10 | 20 106 |
| `M2_c` | RNGkEpsilon | L1 | 25 600 | 43.50 | 87.00 | 5 220 |
| `M2_m` | RNGkEpsilon | L2 | 50 176 | 85.27 | 170.54 | 10 232 |
| `M2_f` | RNGkEpsilon | L3 | 98 596 | 167.55 | 335.10 | 20 106 |
| `C_lam` | laminar | L2 | 50 176 | 63.95 | 127.90 | 7 674 |
| `B_hi` | kOmegaSST, floor 35.5 °C | L2 | 50 176 | 85.27 | 170.54 | 10 232 |
| `I_hi` | kOmegaSST, inlet `k`,`ε` ×4 | L2 | 50 176 | 85.27 | 170.54 | 10 232 |
| **first-pass total** | | | | **827.11** | **1 654.22** | |

**How the cap is enforced, stated because getting it wrong spends `ranks` times
the authorised budget.** The lab's unit is **core-minutes = wall s × ranks / 60**;
`timeout` enforces **wall seconds**. **Every K0d case is serial (1 rank)**, so
the two coincide here and `timeout = ceiling_core_min × 60`. The identity is
`timeout = cap_core_min × 60 / ranks` and it is written that way in the launcher
so a later parallel case cannot inherit a silent factor-of-`ranks` overrun.

**Why the ceiling rate and not the 10× per-case stop.** §10.3 registers both a
per-case hard stop at **10× the POINT line** and a **total cap of 2 484.84
core-min**, *"and whichever is reached first stops the run"*, with §10.3's own
honest note that **for every case except the two coarse ones the rung cap binds
first**. Enforcing each case at the registered **CEILING rate (2 × POINT)** puts
the first-pass aggregate at **1 654.22 core-min**, inside the total cap, and
leaves the registered **continuation reserve of 827.11 core-min** intact for the
one authorised +20 000-iteration extension of §6. Enforcing 10× per case instead
would permit a first pass of 8 271 core-min — **3.3× the total cap** — which
rule 12 forbids outright.

Concurrency is held at the registered **6 solver processes**; nine cases run as
6 then 3. Launch is `setsid` detached so no solver dies with its agent, with a
`STATUS.<case>` per case in this team's `rc= wall= checkMesh_rc=` form and a
launch log carrying pid, cwd and start/end stamps, so a successor establishes
state from disk without the launching agent.

---

## 8. What this lane did NOT do, and therefore cannot vouch for

- **No compute of any kind was run.** No solver, no `blockMesh`, no `checkMesh`,
  no smoke test. **0 core-minutes against a registered POINT of 829.36.**
- **The registered pre-flight smoke test of `AMENDMENT 2` §A2.4 has NOT been
  run, and its question is therefore still open**: whether K0d's dictionaries,
  carried across the K2e Boussinesq boundary, are complete enough to take one
  timestep in this regime. **Nothing in this record answers that**, and this
  record must not be read as though it did — it is a *document* finding, found
  by reading; the smoke test is a *case* finding, found by running. §6's ten
  checks do not substitute for it either.
- **No case directory was built and no mesh was generated**, so §4's conditions
  A–G are **unverified against an actual `polyMesh`**; §6 item 6 is arithmetic
  feasibility only, and §4's condition G planted-positive test has **not** been
  fired.
- **No grading was performed**, no verdict was assigned to any row, and no tier
  was assigned. The ten graded rows remain `BLOCKED` on Blay 1992, which is
  still `NOT OBTAINED`.
- **Rule 12's estimate-versus-actual calibration is not yet due**: the process
  did not complete, and there is no actual to compare. The zero is recorded here
  so that the eventual calibration row starts from a known baseline rather than
  an assumption.

**Submissions remain PARKED** (rule 7). Nothing in this record leaves the box.

**K0d remains FROZEN and ARMED. It is now also `BLOCKED`, pending one
supervisor ruling, and it is still UNFIRED.**

*Written by the heat-transfer lane, 2026-08-25. Zero compute.*
