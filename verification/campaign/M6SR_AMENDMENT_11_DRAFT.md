# M6SR — DRAFT PRE-COMPUTE AMENDMENT 11 — 2026-09-04

## ⚠ THIS IS A DRAFT. IT IS **NOT APPENDED** TO THE REGISTRATION AND **NOT FROZEN**.

**Status: DRAFT, on the cfd supervisor's desk.** It was written by a lane, and a lane may not
freeze, may not re-pin a grading path and may not write a queue row. Nothing in this file has
force until the supervisor appends it to `verification/campaign/M6SR_PREREGISTRATION.md` under
that document's own amendment discipline (rule 6: appended at the foot, version bumped, with
the assertion `lines whose number changed above this section: 0`).

**SUBMISSIONS ARE PARKED (standing rule 7).** Nothing here is sent, filed, uploaded or
registered outside this box.

---

## 11.1 THE CONDITION, AND HOW IT WAS CHECKED — RULE 2 REQUIRES BOTH

Standing rule 2 permits an amendment **before first compute** and requires it to **state the
condition and how it was checked**, naming the run directory that does not exist.

> **CONDITION: no step of §2.4's cost table has been run. `B0`–`B6` are unspent.**
>
> **HOW IT WAS CHECKED, with a planted control (rule 3), by this lane on 2026-09-04:**
> `verification/runs/M6SR_runs` — the run root §9 registers, and whose absence is this
> registration's freeze proof — **reads ABSENT**. The reader was shown able to see a
> non-absent directory in the same act: `verification/runs/T-family` reads **EXISTS**, and a
> disk-level enumeration of `verification/runs/` returns nine M6-named siblings
> (`F13_ONERA_M6_runs`, `M6I_runs`, `M6S_runs`, `RUNG1_M6_runs`, `RUNG1_M6_R2_runs` and four
> preserved attempts) **none of which is `M6SR_runs`**. A reader that can see nine neighbours
> and not this one is discriminating; a bare "absent" would not have been evidence.
>
> The check was made on the **disk**, not through git — a cleanliness check that asks git is
> blind to exactly the clutter it hunts.

**Everything below is therefore lawful as a pre-compute amendment.** In addition, and
independently: **§8's case files and the B5 launcher are solver INPUTS, not graders.** Rule 2
fixes the **grading** path at the pre-registration commit; Amendment 10 item 10 already states
in terms that *"this is NOT necessarily a rule-2 violation — §8's case files are solver INPUTS,
not graders, and rule 2 fixes the grading path; writing them pre-compute is legal."*

---

## 11.2 WHAT THIS AMENDMENT ASKS THE SUPERVISOR TO DO

1. **Register two new executables into §9's frozen path table**, and pin them by blob sha at
   the freeze, exactly as Amendment 9 §15.3 pinned the first two:

   | what | path | role |
   |---|---|---|
   | **case writer** (NEW) | `cases/M6SR/write_m6sr_case.py` | writes §8's case files for one level. **A SOLVER INPUT. IT GRADES NOTHING.** |
   | **solve driver** (NEW) | `cases/M6SR/run_m6sr_b5.sh` | runs `B4` (checkMesh) and `B5a`/`B5b`/`B5c`. **IT GRADES NOTHING.** |

2. **Re-pin the comparator** `cases/M6SR/analyse_m6sr.py` at its new blob sha. Its Gate P
   invocation path and its CFD producer are new; **no gate, threshold, cap or label moves**
   (§11.4 enumerates every line that changed and why).

3. **Read §11.5's new findings.** Fourteen items are recorded that this document cannot
   satisfy as frozen. **One of them stops the solver at iteration zero.**

**THIS AMENDMENT ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** `A-MAP` is unchanged
(the comparator's frozen `A_MAP_YB` is read, never rewritten). `D1`'s margin is unchanged.
Gate GF's, Gate A's, Gate G's and Gate P's thresholds are untouched. §2.4's cost table is
untouched. Predictions `X1`–`X4` stand exactly as registered, and **`X1` in particular is NOT
disturbed: Gate P's per-station channel remains `NOT A RESULT` on the data** — see §11.3.

---

## 11.3 WHAT THE NEW INVOCATION PATH DOES AND DOES NOT REVIVE

**Amendment 10 item 5 recorded, by AST call graph, that `gate_p()` was defined with ZERO call
sites and was NOT reachable from `main()`, that `set_to_set_assignment()` was reachable only
from inside it, and that there was NO producer of `cfd_sections` anywhere.** Both Gate P
channels were dead **on the code**, on top of `X1` killing the per-station channel **on the
data**.

**Measured after this work, by an AST walk written independently of the comparator's own, with
two controls:**

| name | defined at | reachable from `main()` | call sites |
|---|---|---|---|
| `gate_p` | 1628 | **True** *(was False)* | **2** *(was 0)* |
| `set_to_set_assignment` | 1546 | **True** *(was False)* | 1 |
| `cfd_sections_from_surface` | 867 | True | 4 |
| `cfd_sections_for_case` | 937 | True | 1 |
| `gate_p_figure_data` | 969 | True | 1 |
| **`_control_unreachable_sentinel`** | 2239 | **False** | **0** | ← the control: it must read unreachable |
| `__no_such_function__` | — | **False** | 0 | ← the second control: a name that does not exist |

**65 functions defined, 61 reachable.** The four unreachable are the deliberate sentinel and
three nested `ast.NodeVisitor` methods dispatched by the visitor rather than called by name.
**A walker that reported everything reachable would have proved nothing about `gate_p`; both
controls read False, so it discriminates.**

The same walk is now a **permanent, executable control `C23`** inside the comparator's own
suite, so a future edit cannot silently orphan Sanaa's deliverable again. It fires.

> ### **WHAT THIS REVIVES: the ORDER-INDEPENDENT channel (§4.5) and THE FIGURE ITSELF.**
> ### **WHAT IT DOES NOT REVIVE: Gate P's PER-STATION channel.**
>
> **`X1` STANDS UNTOUCHED AND IS NOT WEAKENED BY ONE WORD OF THIS AMENDMENT.** Re-measured
> through the frozen reader on the pinned `case_2308.dat` after the change:
> **`D1` = `INDETERMINATE`, `Cn(7)/Cn(1) = 0.878747`** — the registered value to six decimals,
> inside the `(0.75, 1.333)` band, series non-monotone. Gate P's per-station channel therefore
> returns **`NOT A RESULT`**, exactly as `X1` predicts. Verified end to end: `gate_p()` called
> with the real reference data returns `per_station_channel_label = NOT A RESULT` with two
> stated reasons. **Building an invocation path is not evidence about the mapping, and this
> amendment claims nothing of the kind.**

---

## 11.4 THE COMPARATOR CHANGES, ENUMERATED — CHECK 1 IS THE SUPERVISOR'S

Read as a diff, not as this summary. Every change is one of three kinds.

**(a) NEW READERS AND A PRODUCER — additive; nothing existing is altered.**
`q_inf_pa()`, `registered_stations()`, `read_surface_scalar()`, `cut_surface_at_plane()`,
`cfd_sections_from_surface()`, `cfd_sections_for_case()`, `gate_p_figure_data()`,
`call_graph_reachable_from_main()`, `_control_unreachable_sentinel()`,
`_synthetic_sampled_surface()`. Constants `P_INF_PA`, `RHO_INF_KGM3`, `U_INF_MS`, `B_SEMI_M`,
`P_MIN_POINTS_PER_STATION`, `PLANT_SAMPLED_P_PA` — **every one quoted from §3 or §8.5; none
chosen here.**

The producer reuses the comparator's **own** `read_points()` and `read_faces()` on the sampled
surface directory, because the `foam` surface writer emits files named `points` and `faces` in
exactly the list form those readers parse. **There is one reader for "what a point is" in this
repository and it is the frozen one.**

**(b) THREE NEW PLANTED CONTROLS — rule 3 on every number the new path can report.**

| control | what is planted | what fires |
|---|---|---|
| **`C21`** | **4321.0 Pa** added to the sampled `p` field of a wing surface **written to and read back from disk** | all seven registered stations moved by exactly `0.086442677805583` in `Cp`, **worst deviation `2.78e-17`**; a reader that cannot see a known pressure offset is not evidence |
| **`C22`** | a station at span **5.0 m**, outside the surface's own extent `[0, 1.25] m` | the reader **REFUSES**. An empty `Cp` curve would compare as a **perfect absence** rather than as a disagreement — the same false zero rule 3 exists for |
| **`C23`** | the AST call graph, with `_control_unreachable_sentinel` as the known-negative | `gate_p`, `set_to_set_assignment`, `cfd_sections_from_surface`, `gate_p_figure_data`, `gate_g`, `gate_r` all reachable; the sentinel unreachable |

All three are added to the `--selftest` **mutation** loop: breaking each one's shipped
statistic must flip **exactly that control** to red.

**(c) TWO EDITS TO EXISTING CODE. THESE ARE THE ONES TO READ CLOSELY.**

1. **`main()`'s `--grade` branch.** Order is now: completion clauses (unchanged, still refuses)
   → **read reference, run `D1`, build `cfd_sections` for all three levels, and PERSIST
   `<run_root>/GATE_P_FIGURE_DATA.json`** → `gate_g()` (**unchanged, and its `Unregistered`
   refusal is NOT caught**) → `gci_fine_from_gate_g()` → `gate_p()` → emit.

   > **WHY THE FIGURE DATA IS WRITTEN BEFORE GATE G, AND WHY THAT IS NOT A GATE CHANGE.**
   > Gate G is registered to **REFUSE (exit 2)** for want of a registered refinement ratio
   > (`X3`). A refusal is a statement about a **gate**; the measured `Cp` curves are **not a
   > gate** and carry no label from the fixed vocabulary. Persisting them first is what keeps
   > Sanaa's named first physics from being taken down by a refusal about a band.
   > **`gate_g()`'s own code is byte-unchanged and its refusal still exits 2.**

2. **`gate_p()`'s `band_channels.numerical_mesh.status` string.** It previously read
   `"measured -- but a LOWER BOUND"` **unconditionally**, including when `gci_fine` is `None`.
   It now reads `"NOT AVAILABLE -- Gate G yielded no band ... NOT a zero."` in that case.
   **The value is untouched and no threshold moves.** The old string annotated an **absence**
   as a **measurement**, which is worse than a discrepancy never computed.

**NEW `--gate-p` MODE.** Grades Gate P alone and writes the figure data; Gate G is **not run**,
so the label passed in is **`NOT A RESULT`** — the strictly conservative direction and the only
one rule 5 lets a downstream constraint move a verdict in. **This mode can never produce a
`PASS`**, and it exists so the figure can be produced without a full grade.

**NEW HELPER `gci_fine_from_gate_g()`, AND IT IS NOT A CHOICE AMONG THE THREE RATIOS.** It
returns a value **only if every candidate agrees to 1e-12 relative**, and `None` otherwise —
verified on three fixtures: agreeing → the value; disagreeing → `None`; any candidate
withholding on non-monotonicity → `None`. Its basis is Amendment 10 item 7's own measurement,
and this amendment **restates that measurement rather than the instruction it refuted**:

> **`GCI_fine` IS `r`-INVARIANT. THERE IS ONE BAND AND THREE EXPONENTS, NOT THREE BANDS.**
> Measured across `r ∈ {1.10, 1.5874, 2.000, 4.000, 7.77}`: `GCI_fine` identical to **15
> significant figures** while `p_s` spans a factor of **21.5**, because `p_s` is fitted from
> the same triple, so `r^p_s ≡ |d32/d21|` and `r` cancels identically.

**RE-CONFIRMED, AND CHANGED IN NOTHING:** Gate G's refusal text promises that *"All three are
printed"*. **That promise is FALSE on the refusing path** — the `raise` discards the dict
before `_emit` and stdout is empty. `X3` records it. **This amendment does not repair it.**

---

## 11.5 🔴 FOURTEEN FURTHER ITEMS THAT CANNOT BE SATISFIED AS THIS DOCUMENT STANDS

**Found by this lane on the supervisor's explicit instruction to assume an eleventh exists.
There were fourteen. Recorded, NOT repaired — every one is a threshold-, instrument-,
state- or grading-path question and this lane is not entitled to any of them. Items 11, 12,
14 and 24 are the ones that stop a launch or move a number.**

| # | what cannot be satisfied | measured basis | consequence |
|---|---|---|---|
| **11** 🔴 | **§8.2 RULES THE WRONG ENERGY TERM. THE FROZEN `fvSchemes` CANNOT START THE SOLVER.** | MEASURED in the solver that will run, not recalled: `OpenFOAM-v2506/applications/solvers/compressible/rhoSimpleFoam/EEqn.H` reads `he.name() == "e" ? fvc::div(phi, volScalarField("Ekp", 0.5*magSqr(U) + p/rho)) : fvc::div(phi, volScalarField("K", 0.5*magSqr(U)))`. §8.4 registers `energy sensibleInternalEnergy`, so `he.name() == "e"` and the solver requests **`div(phi,Ekp)`**. It **never** requests `div(phi,K)`. §8.2 rules `div(phi,K)` and sets `default none;`, which §8.2 itself says "makes an unruled term a hard solver abort". | **`B5` aborts at iteration zero on the frozen dictionary.** The case writer writes `div(phi,Ekp)` carrying §8.2's ruled scheme (`bounded Gauss linear`) and keeps §8.2's `div(phi,K)` line, which is never requested. **⚠ §8.2's STATED REASON DOES NOT TRANSFER:** it justifies the scheme by "`K = |U|²/2` is a smooth, non-shock-bearing kinematic quantity", but `Ekp = |U|²/2 + p/ρ` and the `p/ρ` part **does** jump across the shock. **The term now has a registered scheme and an unsupported justification. THAT IS THE SUPERVISOR'S.** |
| **12** 🔴 | **§8.4 REGISTERS A TURBULENCE DICTIONARY THIS SOLVER DOES NOT READ.** | MEASURED: this is OpenFOAM **v2506 (ESI)**. Every `rhoSimpleFoam` tutorial in the shipped tree carries `constant/turbulenceProperties`; **none** carries `constant/momentumTransport`. The shipped `aerofoilNACA0012` tutorial reads `RAS { RASModel kOmegaSST; turbulence on; printCoeffs on; }`. §8.4's `momentumTransport` / `RAS { model … }` is the **OpenFOAM Foundation** spelling. | Without a repair the solver runs with **no turbulence model dictionary**. The writer emits `turbulenceProperties`/`RASModel`; **the model, the switches and their values are unchanged**. Registered as CHOICE `CH3`. |
| **13** | **§3's `Pr = 0.72` IS NOT SETTABLE UNDER §8.4's REGISTERED `sutherland` TRANSPORT.** | MEASURED: `sutherlandTransport` reads exactly `As_(readCoeff("As", dict))` and `Ts_(readCoeff("Ts", dict))`. **There is no `Pr` key**; conductivity comes from the modified Eucken relation. Derived from that documented relation (μ cancels, so it depends only on the registered `Cp` and `R`): **`Pr_achieved = 0.6903229`**. | **The case runs at `Pr = 0.6903`, `4.122 %` BELOW the registered `0.72`.** The writer does **not** substitute `const` transport to recover `Pr`, because §8.4 registers `sutherland` explicitly. **DERIVED, NOT MEASURED IN A SOLVER RUN**, and reported in every `CASE_PROVENANCE.json`. |
| **14** 🔴 | **§8.1's TABLE CONTRADICTS §8.1's OWN PROSE, AND THE TABLE DOES NOT REPRODUCE THE REGISTERED STATE.** | §8.1's table cell reads `(285.221 15.249 0)`. §8.1's prose two lines below reads `285.679356 × cos(3.06°) = 285.2721`. Recomputed: **285.27208**. With the table's `285.221`, `\|U\| = 285.628365 m/s` and **`M = 0.839350` against the registered `0.8395`**, and `Re` is `0.0179 %` off `11.72e6`. | **The table's value does not reproduce the registered state pair.** Both cells carry the same formula `U∞·(cos 3.06°, sin 3.06°, 0)`; the writer takes the **formula**, which is the content both cells agree on, and writes `285.2720290`, reproducing `M = 0.8395000` and `Re = 1.1720e7`. **A transcription slip in a frozen table is the supervisor's to strike, not a lane's.** |
| **15** | **§8.5 REGISTERS A FUNCTION OBJECT THAT DOES NOT EXIST IN THIS OPENFOAM.** | MEASURED: v2506 ships `src/functionObjects/utilities/solverInfo` and **no** function object named `residuals`; `etc/caseDicts/postProcessing/numerical/` holds `solverInfo` and `solverInfo.cfg` only. `residuals` is the pre-v1912 name. | The writer emits `solverInfo`. **NOTHING GRADES ON IT** — §5.1 names `scripts/residual_max_over_equations.py` as G2's **only** instrument and it reads `log.rhoSimpleFoam` directly. Provenance, not an instrument. |
| **16** | **§2.4's COST TABLE HAS NO ROW FOR STAGING L3's AND L2's MESHES INTO THE RUN ROOT.** | `B3` covers the **L1 build** only. L3's and L2's meshes live under `/home/ubuntu/certonomous-runs/`, which is **READ ONLY**, and a solver writes into its own case. The comparator's `_discover_levels()` already rules that an in-run-root copy supersedes the read-only source. | An **unbudgeted step**. The driver measures it, reports it on its own line as **`B3s`**, and **does not fold it into any registered row and does not absorb it into any ratio** (§9.3; `COMPUTE_BUDGET_CHARTER` §6). |
| **17** 🔴 | **`B4`'s `log.checkMesh` HAD NO PRODUCER EITHER — GATE A WAS AS UNRUNNABLE AS GATE P.** | §9's frozen path table registers two executables; `build_m6sr_l1.sh` runs `plot3dToFoam`/`autoPatch`/`createPatch`/`renumberMesh` and **no `checkMesh`**. Gate A reads *named numeric maxima* off `<run_root>/<L>/log.checkMesh`, and §5 rules that **"an absent `checkMesh` log reads `ABSENT`. It never reads clean."** | Amendment 10 item 10 found the hole at `B5`; **the same hole sits one gate further back at `B4`.** The new driver runs `checkMesh` in its `stage` phase. §2.4 gives **ONE** `B4` row (cap **2.0 core-min**) for "checkMesh ×3", so the driver treats it as a **running budget across the three levels**, tracked at `<run_root>/B4_SPENT_COREMIN.txt` and **refused when exhausted**. |
| **18** | **§8.3 REGISTERS NO `transonic` SWITCH FOR A `M∞ = 0.8395` TRANSONIC CASE.** | §8.3 registers `nNonOrthogonalCorrectors`, `consistent` and `residualControl` and nothing else, so `transonic` takes OpenFOAM's default `no`. MEASURED: `rhoSimpleFoam/pEqn.H:14` branches on `simple.transonic()` and the transonic limb uses `fvm::div(phid, p)` — **a different pressure equation**. | Registration by omission is still registration and the default is what runs. **But the registration nowhere states that it considered the switch on a transonic case**, and two further `div` terms would need ruling if it were ever turned on. Recorded as CHOICE `CH10`; **the switch is not set here**. |
| **19** | **AMENDMENT 4b's "`S_ref` IS CONSUMED BY NOTHING" CANNOT SURVIVE A RUNNABLE CASE.** | `forceCoeffs` **requires** `Aref` and `lRef`. There is no configuration of a runnable case in which `S_ref` is consumed by nothing and `C_D` is still a drag coefficient. | The writer uses `lRef = 0.64607` (MAC) and `Aref = 0.7532` (`S_ref`). **Amendment 4a's gate-by-gate invariance still holds** — G1's and G2c's thresholds are fractions of the L3–L2 `C_D` difference, i.e. **ratios in which any constant `Aref` cancels identically**. What is **not** invariant is the **printed value** of `C_D`. The alternative, `Aref = 1.0`, keeps 4b literally true and makes the printed "`C_D`" not a coefficient. **Both are stated; the supervisor picks.** |
| **20** | **§8.5's "seven constant-`y` planes" NAMES THE WRONG AXIS.** | The comparator's own `mesh_axes()` records, MEASURED on this box's M6 meshes, that **the span runs along `z`**, the thickness along `y` and the chord along `x`; §5 likewise writes the root section as "`y = 0`" and `mesh_axes()` flags that as the registration's **notation**. Confirmed on both existing levels: symmetry plane normal to `z`, `root_value = 0`. | Handled by **deriving** the span axis and refusing on an unexpected frame (CHOICE `CH8`), never by adapting silently. **The registration's text is nonetheless wrong on its face** in a clause that places Sanaa's seven stations. |
| **21** | **§4.5's CHANNEL INTERLEAVES THE UPPER AND LOWER SURFACES.** | `set_to_set_assignment()` builds both the experimental and the CFD curve as `sorted((x, cp))` and interpolates with `_interp()`, which is single-valued in `x`. At any `x/c` a wing section has **TWO** `Cp` values. The frozen channel therefore compares an interleaved sequence, not a section. | **NOT CHANGED HERE** — it is frozen behaviour and it applies **symmetrically** to experiment and CFD, so it is not a bias in the comparison. **But Sanaa's figure cannot be plotted from an interleaved curve** and will need the upper/lower split, which is a grading-path question if the RMS matrix is ever to mean what its name says. **THE SUPERVISOR'S.** |
| **22** 🔴 | **GATE P's VERDICT IS STILL UNREACHABLE ON THE PATH THAT MATTERS.** | `gate_g()` raises `Unregistered` (rc 2) on a **CONVERGING** family — prediction `X3`, and the whole point of the family is to converge. That raise fires **before** `gate_p()` in `--grade`. | **The FIGURE survives** (its data is persisted before Gate G runs) and `--gate-p` yields a standalone `NOT A RESULT`. **But a Gate P verdict printed beside a Gate G band cannot be produced until `X3`'s `r` question is ruled.** Catching the refusal would convert a registered exit-2 into an rc-0 output — **degrading a gate, which no lane may do.** It was not done. |
| **23** | **`B5c`'s 16 RANKS ARE THE BOX'S ENTIRE CORE COUNT, AND THE BOX IS NOT IDLE.** | MEASURED 2026-09-04: `nproc = 16`; load average at drafting **37.13 / 41.26 / 36.27**. §2.4's solve rate `3.40e-8 core-min/cell/iteration` is a **FOUR-RANK** measurement (Amendment 8 §8a) applied at 8 and 16 ranks, i.e. **assuming perfect strong scaling**. | Contention pushes actual core-minutes **up**, the same direction the rank-basis assumption already errs in. `B5c`'s cap is **1,630.0 core-min**; **an overrun stops the run** and does not get a new budget. Reported so the supervisor sizes the launch window rather than discovering it at the cap. |
| **24** 🔴 | **THE SEVEN STATIONS ARE PLACED ON A SEMISPAN THE WING DOES NOT HAVE — AND THIS BEARS DIRECTLY ON SANAA'S FIGURE.** | Three semispans live in this frozen document. §8.5 places the stations at `y/b × 1.19676 m`. §5's `GF4_SEMISPAN_M` is `1.1963 m`. **`X2` registers the instrument as the WALL-PATCH SPAN EXTENT and measures it at `1.2164045761791 m` on BOTH levels** — re-measured by this lane through the same reader: **`1.216405 m` on L3 and on L2, identical.** §8.5's `1.19676` is `+0.0385 %` from AGARD's physical semispan and **`−1.6150 %` from the wing this ladder will actually solve**. | **Every station is displaced inboard by ~1.6 % of the CFD wing's semispan.** The nominal `y/b = 0.99` ring sits at **`0.974012`** of the solved wing; `0.96` sits at `0.944496`; `0.20` at `0.196770`. Placing station 7 at 0.99 of the **solved** wing would move it **`0.019448 m` = `1.5988 %` of semispan** outboard. At §16.4's own exchange rate — 1 % of semispan ≈ 0.7 cm of chordwise shock displacement on this wing at `M = 0.8395` — **that is ~1.1 cm, and it is LARGER than the 0.96-vs-0.95 divergence §16.4 already registered as load-bearing, and points the SAME way.** ⚠ **BOTH READINGS ARE DEFENSIBLE** — the taps are at 0.99 of the **real** wing, so matching the physical coordinate is right for the inboard stations, while the ×4 family's inherited **rounded tip cap** (`X2` reason 4: it extends 2.11 cm beyond AGARD's semispan) makes "0.99 of the solved wing" a materially different aerodynamic place. **CHOOSING BETWEEN THEM IS A GATE-PARAMETER DECISION AND IS THE SUPERVISOR'S.** The comparator uses `1.19676` **as registered** and changes nothing. **All seven stations were verified to fall INSIDE both meshes' wall-patch extent `[0, 1.216405] m`, so the reader will not refuse on span** — station 7 clears the tip by `0.031612 m`. |

> **WHAT M6SR CAN AND CANNOT DO AFTER THIS AMENDMENT, STATED ONCE, PLAINLY.**
> **CAN:** run `B1`–`B3` (L1 mesh build, unchanged driver); **stage** L3/L2/L1 and run `B4`'s
> `checkMesh`; grade **`Gate GF`** and **`Gate A`**; run **`B5a`/`B5b`/`B5c`** to §8's spec;
> and **produce Sanaa's named first-physics figure DATA at
> `<run_root>/GATE_P_FIGURE_DATA.json`** — experimental taps and CFD `Cp` at the seven
> registered stations, every level, with clause `L-HONEST` verbatim.
> **CANNOT:** print a Gate P **verdict** beside a Gate G band while `X3` stands (item 22).
> **CANNOT:** grade Gate P's per-station channel — `X1`, unchanged.
> **`Gate G` will still REFUSE (exit 2) on a converging family** (`X3`); **`Gate GF`'s `GF2`
> and `GF4`-semispan limbs will still `GATE FAIL`** (Amendment 10 item 8, `X2`); **the control
> suite will still REFUSE (exit 2) on `C12`** (`X4`).
> **The frozen `fvSchemes` and `momentumTransport` of items 11 and 12 would have stopped the
> solver before iteration one.** That is a launch-readiness fact, not a prediction, and it is
> the supervisor's.

---

## 11.6 THE CHOICES MADE IN THE CASE FILES — TWELVE, EACH WITH ITS BASIS

§8 specifies most of a runnable case exactly, and this lane took every specified value
verbatim. Twelve things §8 did **not** fix, or fixed in a form this OpenFOAM does not accept,
were chosen **before first compute** and are recorded — **`CH1`–`CH12`, in
`cases/M6SR/write_m6sr_case.py`, and reproduced verbatim into every case's
`CASE_PROVENANCE.json`** so a reader of the run tree never has to open the source to learn
what was chosen. A choice made now is lawful and must be recorded; a choice made later is not.

`CH1` boundary conditions attached **by patch TYPE, never by name** (§7 does not predict the
names) · `CH2` `div(phi,Ekp)` (item 11) · `CH3` `turbulenceProperties`/`RASModel` (item 12) ·
`CH4` `lRef`/`Aref` (item 19) · `CH5` `forceCoeffs` writes **every time step**, because G1 needs
a 500-iteration tail and G2c a 2,000-iteration tail and §8.5's `writeInterval = endTime` would
leave **one** sample · `CH6` no `Pr` key (item 13) · `CH7` `solverInfo` (item 15) · `CH8`
freestream built from the **derived** axes, refusing on an unexpected frame (item 20) · `CH9`
`U_x = 285.2721` (item 14) · `CH10` `transonic` unset (item 18) · `CH11` the wing patch is
sampled and the seven planes are cut **by the comparator** — an OpenFOAM `cuttingPlane` cuts the
**volume** and cannot isolate the wing **surface**, and a failing function object would take
607.63 core-min down with it for an artifact nothing grades; cutting the point-interpolated
patch is **exact linear interpolation along triangle edges and introduces NO spanwise binning
tolerance**, which a face-centre reader would have required · `CH12` the mesh is **copied** into
the run root, because `certonomous-runs` is read only.

**SPECIFIED BY §8 AND TAKEN VERBATIM, CHOSEN IN NOTHING:** all seven `0/` internal values and
BC types; `fvSchemes` (bar item 11); the whole of `fvSolution`, including `residualControl`
**zero on every equation** and its stated reason; `molWeight 28.964425`, `As 1.571860616e-06`,
`Ts 110.4`, `Cp 1004.5`; `endTime` 3000/4000/5000; `writeControl timeStep` with
`writeInterval = endTime`; `hierarchical (n 1 1)` with `scotch` **not used**; ranks 4/8/16;
caps 31.0/163.0/1630.0 core-min; the seven `y/b` and `b_semi = 1.19676`.

**THE STATION SET, REGISTERED AND SOURCED:** `0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99`,
read off the comparator's own frozen `A_MAP_YB` constant — **nothing new is registered here.**
Its source is §16.4's: `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt`
**lines 13728–13729**, *"271 pressure orifices divided in 7 sections (y/b =
0.20/0.44/0.65/0.80/0.90/0.96 and 0.99)"*. **The sixth station is `0.96`, which is what AGARD
AR-138 §5.1.1 prints, and NOT the `0.95` of NASA TMR's widely circulated set.** §16.4 registers
that divergence as **`REPORTED, NOT GATED`**, and this amendment carries it forward unaltered —
now alongside item 24, which is **larger and points the same way**.

---

## 11.7 THE PLANTED CONTROLS AND THE MUTATION CONTROL — RULE 3, ON BOTH NEW EXECUTABLES

**The case writer carries its own suite**, because a writer that cannot be shown to write the
value it claims is not evidence about the case it produced. `--selftest`: **W1** unguessable
patch names classified by type · **W2** a second `wall` patch → **REFUSED** · **W3** the seven
`0/` fields written and every registered internal value read **back from disk** · **W3b** the
age guard's ordering — `0/U`'s mtime is the newest, because §8.6 dates the run from it ·
**W4** the **mutation**: `k_inf` corrupted, and the file then does not carry the registered
value, so W3's reader would have gone red · **W5** a rotated axis frame → **REFUSED**.

**Measured: all six FIRE. `rc = 0` identical under `python3` and `python3 -O`.**
The solve driver **runs that suite and REFUSES to launch if any control does not fire.**

**No bare `assert` anywhere in either new file** — verified by **AST parse, not grep**: zero
`ast.Assert` nodes, and a synthetic file carrying one `assert` reads **1**, so the checker
discriminates. Exit vocabulary `0` / `2` / `70` in both, verified: `--gate-p` and `--grade`
on an absent run root both return **2**, identical under `python3 -O`; the driver returns **2**
on a bad level and a bad phase.

**THE WRITTEN CASE WAS PARSED BY OPENFOAM ITSELF, NOT ONLY BY THIS LANE.** A case was written
from the real L3 mesh and every dictionary was read back through `foamDictionary` inside the
solver's own container:

> **All 13 parse: `fvSchemes`, `fvSolution`, `decomposeParDict`, `sampleDict`,
> `thermophysicalProperties`, `turbulenceProperties` and all seven `0/` fields.**
> `controlDict`'s `functions{}` resolves to exactly **`forceCoeffs`, `yPlus`, `solverInfo`,
> `sampleDict`** — so the `#include "sampleDict"` directive resolves and **Gate P's producer is
> wired into the run**.
>
> ⚠ **THIS IS A PARSE, NOT A SOLVE.** No solver has been launched. Dictionary **key
> acceptance** was established by reading OpenFOAM v2506's own source and shipped tutorials;
> **runtime acceptance by `rhoSimpleFoam`, `decomposePar`, `mpirun` and `reconstructPar`, and
> the on-disk layout the `foam` surface writer actually produces, are UNVERIFIED BY
> EXECUTION.** They are stated as inferences and are named as such.

**The state pair is reproduced by the written case, measured on the real L3 mesh:**
`|U| = 285.679356 m/s`, **`M = 0.8395000`**, **`Re = 1.1720e7` on the MAC** — the registered
values, from the registered formulae.

---

## 11.8 COST — RULE 12, AND NONE OF IT IS LADDER COMPUTE

**No step of §2.4's cost table was run and `verification/runs/M6SR_runs` does not exist.** What
this work spent is host arithmetic, read-only inspection of already-existing artifacts (two
polyMesh point/face sets, the pinned `case_2308.dat`), read-only `grep` inside a stopped
container image, and the two control suites. **Reported as wall time on one core; there is no
solver in it, and the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so any
dollar figure is DERIVED and REPORTED-BY-OWNER, never measured.**

The estimate-versus-actual comparison rule 12 owes at every process completion is **built into
both new executables** — `BUILD_RESULT.json`'s pattern is carried into `SOLVE_RESULT.json`,
which prints, per level, the §2.4 estimate, the cap, the **actual core-minutes computed from
the SOLVER LOG's own rank banner**, the ratio, and the **measured** solve rate in
core-min/cell/iteration beside the registered `3.40e-8` and its **four-rank basis** — so the
strong-scaling assumption is measured rather than assumed. Attribution is left **UNATTRIBUTED
at driver exit**, because contention versus waste versus misprediction is a reading a human
makes against the box's load record, and **waste is named separately and never absorbed into
the ratio**.

---

## 11.9 WHAT THIS AMENDMENT DOES **NOT** DO

- It does **not** freeze anything. A lane may not freeze.
- It does **not** write a queue row. `launch_cmd` now has a target; **writing the row and
  ordering the launch are the supervisor's.**
- It does **not** alter a gate, a threshold, a cap or a label.
- It does **not** touch the frozen body of `M6SR_PREREGISTRATION.md`. Not one line.
- It does **not** repair items 11–24. It **records** them.
- It does **not** revive Gate P's per-station channel. **`X1` stands.**
- It does **not** catch or soften Gate G's registered refusal. **`X3` stands.**
- It does **not** claim `A-MAP` is confirmed, or that any `Cp` agreement has been observed.
  **No solver has run.**
- **SUBMISSIONS ARE PARKED.** Nothing here is sent, filed, uploaded or registered outside
  this box.
