# K0d re-registration, PHASE 1: the gather. No physics chosen here.

**Written 2026-08-25 by a heat-transfer lane on the supervisor's brief. ZERO
COMPUTE. No case directory built, no solver launched, no registration written.**
`verification/runs/F14-cooling-ladder/K0d_runs/` does not exist at this write.

**This document CHOOSES NOTHING.** The `nu`-versus-`beta` ruling is the
supervisor's and is not taken here. Everything below is arithmetic, provenance
and measurement, assembled so that ruling can be made from artifacts.

---

## 1. HASH VERIFICATION — all five frozen K0d documents match HEAD

HEAD at this write: `81182ebfffe9ea1ddcfde8976a5f0b7a6b3b2921`.
`git hash-object <disk>` compared against `git rev-parse HEAD:<path>`:

| file | blob | disk == HEAD |
| --- | --- | --- |
| `K0d_PREREGISTRATION.md` (3 759 lines) | `e629f5c492a36772cf4ab0593440fd9666a119fe` | **MATCH** |
| `K0d_TURBULENT_MIXED_CONVECTION_GATE.md` | `7a033bd40bb28738bc7a61400b0fd741c2e9853b` | **MATCH** |
| `K0d_FIRE_RULING_2026-08-25.md` | `f1ae1892418b2c5aec151363167c9bc6a88e9f01` | **MATCH** |
| `K0d_PREFLIGHT_EXECUTABILITY_FINDING.md` | `71a1a71966f4d2cccf5208b278f418f76a512401` | **MATCH** |
| `K0d_PREFLIGHT_SMOKE_TEST.md` | `393f0e885bcae0a63bf4e5cc0d570a6d83ddabc8` | **MATCH** |

`sha256(K0d_PREREGISTRATION.md) = 6c6b72815c35e7215cb68d7515cce4357706279eeac2270298aa89dc02b5ada6`.

**THE SHARED-INDEX HAZARD IS STILL LIVE AND WAS RE-MEASURED, NOT INHERITED.**
`git ls-files -s` stages `K0d_PREREGISTRATION.md` at blob
`0238241345fee177d5ce67351c57c569b234045c` — **986 lines, 63 459 bytes**,
against HEAD's 3 759 lines. **A bare `git commit` by any agent deletes 2 773
lines and all five amendments.** Inspected, never reverted (rule 10).

---

## 2. THE 2.76 % CONTRADICTION — the source values and the two reconciliations

`Ra`, `g`, `beta`, `dT`, `H`, `nu` and `Pr` are **seven quantities bound by one
equation**, and the frozen document registers all seven:

```
  Ra = g * beta * dT * H^3 * Pr / nu^2
```

Registered inputs, each with its frozen locator:

| symbol | value | where |
| --- | ---: | --- |
| `Ra` | 2.13e9 | §3.4 — secondary (Oulghelou 2020 lines 694–697) |
| `g` | 9.81 m/s² | §5 line 312 |
| `dT` | 20.0 K | §3.3 clause 2 — **FIXED FOR ALL TIME IN THIS RUNG** |
| `H` | 1.04 m, `H³ = 1.124864 m³` | §3.1 |
| `Pr` | 0.71 | §3.2 — *this document's* design value |
| `nu` | **1.55e-5 m²/s** | §3.2 line 189 — *this document's* design value, "at the reference temperature 298 K" |
| `beta` | **1/298 = 3.3557047e-3 1/K** | §5 line 312 |

**At the values as frozen the equation does not close.** Full four-cell table,
recomputed here from the inputs and not transcribed:

| `nu` | `beta` | implied `Ra` | vs registered 2.13e9 |
| --- | --- | ---: | ---: |
| 1.55e-5 (§3.2) | 1/298 (§5 l.312) | **2.188657e9** | **+2.7539 %** |
| **1.569e-5 (`AMENDMENT 1` §A1.2)** | 1/298 | 2.135970e9 | +0.2803 % |
| 1.55e-5 | **3.26577e-3 (`AMENDMENT 5` §A5.7)** | 2.130000e9 | **0.0000 %** |
| 1.569e-5 | 3.26577e-3 | 2.078725e9 | −2.4073 % |

**Row 1 is the defect. Rows 2 and 3 are the two incompatible repairs, and both
are frozen in this document.**

---

## 3. OPTION A — move `nu` (`AMENDMENT 1` §A1.2, 2026-08-24, pre-compute)

`beta = 1/298 = 3.3557047e-3` held; `nu = 1.569e-5 m²/s`.

- **`Ra` = 2.135970e9**, +0.2803 % on the secondary's 2.13e9.
- **`Pr` = 0.71, UNCHANGED.** `Pr` is registered independently in §3.2 and is
  not the free variable in either option.
- `Gr = Ra/Pr =` **3.00841e9**; `Re_H = 0.57 × 1.04 / nu =` **3.77820e4**;
  `Ri = Gr/Re_H² =` **2.1075** (§3.4 registers 2.10, `AMENDMENT 1` 2.102).
- `Re_slot = 0.57 × 0.018 / nu =` **653.92** against the secondary's quoted
  **654** — **−0.01 %**. §3.4's *"mutually consistent"* claim is TRUE here.
- `epsilon = beta·dT =` **0.067114** → K2e floors **u 1.6494 %**,
  **Nu 0.03121 %** — the numbers §3.5 and row `M0` already carry.

**PROVENANCE, STATED EXACTLY.** §A1.2 did **not register** `nu = 1.569e-5`. It
used that value inside an independent re-derivation check, concluded *"the entire
non-dimensional set of §3.4 is therefore reproducible"*, and stated **"No gate,
threshold, cap or label moves."** The value `1.569e-5` appears in the frozen
document **only** inside §3.4's `Re` justification sentence and inside §A1.2's
check. **Option A is therefore an ARITHMETIC ROUTE THAT WAS NEVER REGISTERED AS A
SOLVER INPUT.** `AMENDMENT 5` §A5.13 Finding 9 states this and refers it.

**WHAT OPTION A COSTS IF IT IS RULED.** §4's mesh family computes the first wall
cell from `y_cell = 2 y⁺ nu / u_tau`, `u_tau = 0.57 × sqrt(0.005/2) = 0.0285 m/s`,
**at `nu = 1.55e-5`**: `2 × 1.55e-5 / 0.0285 =` **1.0877e-3 m**, the registered
L1 value 1.09e-3. At `nu = 1.569e-5` the design value becomes **1.1010e-3 m**,
**+1.23 %**, and the three levels become **1.101e-3 / 7.864e-4 / 5.618e-4**.
**§4 refusal condition D requires the first wall-normal cell to equal the design
value to 1 %. 1.23 % > 1 %.** So Option A obliges the new registration to
re-derive §4's first-cell column; it does not survive a copy-across.

---

## 4. OPTION B — move `beta` (`AMENDMENT 5` §A5.7, 2026-08-25, pre-compute)

`nu = 1.55e-5` held; `beta = Ra nu² / (g dT H³ Pr) =` **3.26577e-3 1/K**,
`TRef = 298.15 K`.

- **`Ra` = 2.130000e9**, exact by construction — it is the secondary's own figure.
- **`Pr` = 0.71, UNCHANGED**, same reason as Option A.
- `Gr =` **3.00000e9**; `Re_H = 0.57 × 1.04 / 1.55e-5 =` **3.82452e4**;
  `Ri =` **2.0510** (against §3.4's registered 2.10).
- `Re_slot = 0.57 × 0.018 / 1.55e-5 =` **661.94** against the quoted **654** —
  **+1.21 %**. §3.4's *"mutually consistent"* claim is FALSE here, which
  §A5.13 Finding 9 records.
- `epsilon = beta·dT =` **0.065315** → K2e floors **u 1.6050 %**,
  **Nu 0.02958 %**, which §A5.7.6 already discloses beside the frozen pair.

**PROVENANCE.** §A5.7 **is a registration**: it strikes §5 line 312 by
quote-and-strike at the foot under rule 6 and registers `beta = 3.26577e-3`,
`TRef = 298.15 K` into `constant/transportProperties` of all nine cases. It
labels itself a **SUPERSESSION of a registered input**, not a gap fill, and puts
the supervisor on notice in the instrument that reverting needs a further
amendment in the same window.

**SO THE TWO ARE NOT SYMMETRIC.** Option B is a registered supersession; Option A
is an unregistered arithmetic route inside a check. **The document nevertheless
contains both, and a reader cannot tell from it which `nu`/`beta` pair the
solver was meant to run** — which is exactly the supervisor's blocker.

---

## 5. WHICH PUBLISHED VALUE EACH IS CONSISTENT WITH — and the honest negative

**NEITHER SECONDARY STATES `nu`, `Pr` OR `beta` FOR THIS CASE. This was checked,
not assumed.** `oulghelou_beghein_allery_2020_2009.06724.txt` lines 688–726 and
`zou_zhao_chen_2018_building_simulation.txt` lines 667–705 were read in full and
grepped for *viscosity*, *Prandtl*, *expansion coefficient* and `1.5*e-5`:
Oulghelou defines `beta` symbolically (line 134) and gives **no number**; Zou's
hits are all *turbulent* viscosity and *turbulent* Prandtl numbers, none
molecular. **The primary, Blay, Mergui & Niculae (1992), is `NOT OBTAINED`.**

**So both options are LAB CHOICES and neither can be attributed to a source.**
Any new registration must say so on its face.

**What CAN be cited from this box** is the Sutherland air correlation, whose
constants are read from OpenFOAM v2606 dictionaries **on disk** — `As = 1.4792e-06`,
`Ts = 116` at
`/usr/lib/openfoam/openfoam2606/tutorials/heatTransfer/overBuoyantPimpleDyMFoam/movingBox/constant/thermophysicalProperties:41-42`
— with `rho = p/(R T)`, `p = 101 325 Pa`, `R = 287.058 J/kg·K`:

| registered number | air state it corresponds to |
| --- | --- |
| `nu = 1.55e-5` (§3.2) | **T = 297.81 K (24.66 °C)** — §3.2's own label *"at the reference temperature 298 K"* is right to 0.19 K |
| `nu = 1.569e-5` (§A1.2) | **T = 299.86 K (26.71 °C)** |
| `beta = 1/298` (§5 l.312) | ideal gas at **T = 298.00 K** |
| `beta = 3.26577e-3` (§A5.7) | ideal gas at **T = 306.21 K (33.06 °C)** |

**THE FLUID-STATE READING, WHICH THE FROZEN DOCUMENT NEVER MAKES.** For air as an
ideal gas `beta = 1/T_ref`, so `beta` and `nu` are **not independent** — both are
properties of one reference temperature.

- **Option A pairs `beta` at 298.00 K with `nu` at 299.86 K: a 1.86 K internal
  spread.**
- **Option B pairs `beta` at 306.21 K with `nu` at 297.81 K: an 8.40 K internal
  spread**, and 306.21 K (33.1 °C) is above the hot floor's own 35 °C by only
  1.9 K and 8 K above the cavity's registered `TRef = 298.15 K`.

**AND NO SINGLE AIR STATE REPRODUCES `Ra = 2.13e9` AT `dT = 20.0 K`.** Solving
`g (1/T) dT H³ Pr / nu_Sutherland(T)² = 2.13e9` gives **T_ref = 299.63 K**, at
which `beta = 3.337416e-3` and `nu = 1.5669e-5` — neither of the two registered
`beta` values and close to (not equal to) §A1.2's `nu`. At `dT = 20.5 K` it gives
**T_ref = 301.26 K**, `beta = 3.319381e-3`, `nu = 1.5821e-5`.

**A THIRD RECONCILIATION EXISTS AND IS PHYSICALLY REFUTED, RECORDED SO IT IS NOT
PROPOSED LATER.** Making `Pr` the free variable at `nu = 1.55e-5`, `beta = 1/298`
gives `Pr = 0.71 × 2.13/2.188657 =` **0.6910**. Air's molecular Prandtl number
does not go below ~0.70 anywhere near room temperature. **Moving `Pr` is not
available.**

**ONE FURTHER FACT FOUND WHILE READING THE SECONDARY, AND IT BEARS ON BOTH
OPTIONS.** Oulghelou 2020 defines its `Ra = 2.13e9` **on `theta_hot = 35.5 °C`
against `theta_cold = 15 °C`, i.e. `dT = 20.5 K`**, and separately imposes 35 °C
on the floor in its own solve. §3.3 froze `dT_band = 20.0 K` *for all time in
this rung*. **So the `Ra` both options treat as the anchor was published at a
`dT` neither option uses**, and reconciling at `dT = 20.5 K` gives
`beta = 3.186117e-3` at `nu = 1.55e-5` or `beta = 3.264707e-3` at
`nu = 1.569e-5`. §A5.7.4 registered the 2.44 % `beta` exposure this creates; it
is **not** repaired here and it is **not** a fourth option — it is the reason the
new registration should state which `dT` its `Ra` is anchored on, **in the same
line as `Ra` itself**.

**WHICH AMENDMENT IS LATER: `AMENDMENT 5` (2026-08-25) postdates `AMENDMENT 1`
(2026-08-24). BOTH ARE PRE-COMPUTE.** Zero core-minutes have been spent against
K0d's registered POINT of 829.36; `K0d_runs/` does not exist.

---

## 6. THE NINE CASES, THEIR CLOSURES, AND THE FIELDS EACH CLOSURE ACTUALLY WRITES

§5's registered table, with the completion field set in force **after** both
repairs (`AMENDMENT 3` §A3.4 made clause 4 per-closure; `AMENDMENT 5` §A5.8
added `phi` to all three sets):

| case | closure | level | cells | `endTime` | purpose | **completion field set in force** | count |
| --- | --- | --- | ---: | ---: | --- | --- | ---: |
| `M1_c` | `kOmegaSST` | L1 | 25 600 | 40 000 | ladder | `T U p_rgh alphat nut k omega phi` | 8 |
| `M1_m` | `kOmegaSST` | L2 | 50 176 | 40 000 | ladder | `T U p_rgh alphat nut k omega phi` | 8 |
| `M1_f` | `kOmegaSST` | L3 | 98 596 | 40 000 | ladder, **graded level** | `T U p_rgh alphat nut k omega phi` | 8 |
| `M2_c` | `RNGkEpsilon` | L1 | 25 600 | 40 000 | ladder | `T U p_rgh alphat nut k epsilon phi` | 8 |
| `M2_m` | `RNGkEpsilon` | L2 | 50 176 | 40 000 | ladder | `T U p_rgh alphat nut k epsilon phi` | 8 |
| `M2_f` | `RNGkEpsilon` | L3 | 98 596 | 40 000 | ladder, **graded level** | `T U p_rgh alphat nut k epsilon phi` | 8 |
| `C_lam` | laminar | L2 | 50 176 | 40 000 | Charter 2c discrimination control | `T U p_rgh alphat phi` | 5 |
| `B_hi` | `kOmegaSST`, floor **35.5 °C** | L2 | 50 176 | 40 000 | §3.3 arbitration guard | `T U p_rgh alphat nut k omega phi` | 8 |
| `I_hi` | `kOmegaSST`, inlet `k`,`eps` **× 4** | L2 | 50 176 | 40 000 | §3.2 inlet-turbulence sweep | `T U p_rgh alphat nut k omega phi` | 8 |

**Field-presence assertions: `5×8 + 3×8 + 1×5 =` 69, zero of them unsatisfiable**
(§A5.8's own count, reproduced).

**WHAT EACH CLOSURE ACTUALLY WRITES, and the defect that came from getting it
wrong.** `kOmegaSST` solves and writes `k` and **`omega`**; `RNGkEpsilon` solves
and writes `k` and **`epsilon`** and writes **no `omega` under any
circumstance**; laminar writes neither `k` nor a second turbulence field nor
`nut`. `phi` is written by `buoyantBoussinesqSimpleFoam` for all three
(`pEqn.H` line 39 assigns it), which §A5.8 verified from **five** solved cases on
disk including two laminar ones.

**§8.2's ORIGINAL clause 4 required `T U p_rgh alphat nut k omega` of every
case.** `M2_c`, `M2_m` and `M2_f` could never have satisfied it, and
`analyse_k0d.py` refuses (exit 2) unless all nine `DONE.<case>` markers exist —
**so the whole rung would have produced nothing.** That defect **was already
repaired in the frozen document** by `AMENDMENT 3` §A3.4 and further tightened by
`AMENDMENT 5` §A5.8. **The new registration must carry the table above, which is
the post-repair form, and not §8.2's original enumeration.**

---

## 7. THE COST, RE-DERIVED FROM §10.1's BASIS — NOT TRANSCRIBED

Basis (§10.1): `K0cS` measured rate **1.593e-6 s per cell-iteration** (fine 192²
pilot), × **1.6** developed-flow contingency = **POINT rate 2.549e-6**.
CEILING rate = 2 × POINT. `C_lam` carries a registered **0.75** scale factor.

| case | cells | core-s | **core-min** |
| --- | ---: | ---: | ---: |
| `M1_c` | 25 600 | 2 610.2 | 43.50 |
| `M1_m` | 50 176 | 5 115.9 | 85.27 |
| `M1_f` | 98 596 | 10 052.8 | 167.55 |
| `M2_c` | 25 600 | 2 610.2 | 43.50 |
| `M2_m` | 50 176 | 5 115.9 | 85.27 |
| `M2_f` | 98 596 | 10 052.8 | 167.55 |
| `C_lam` | 50 176 | 3 837.0 | 63.95 |
| `B_hi` | 50 176 | 5 115.9 | 85.27 |
| `I_hi` | 50 176 | 5 115.9 | 85.27 |
| **solver subtotal** | | | **827.11** |
| instruments (0.75 + 0.50 + 1.00) | | | **2.25** |
| **POINT** | | | **829.36** |

**829.36 core-min reproduces the registered POINT EXACTLY.**
CEILING = `2 × 827.11 + 827.11 + 3.50 =` `1 654.23 + 827.11 + 3.50 =`
**2 484.84 core-min — reproduces EXACTLY.**
Derived dollars at the owner-reported **$0.0513/core-h**: POINT
**13.823 core-h = $0.709**; CEILING **41.414 core-h = $2.125**.
**`cost_basis`: the rate is MEASURED (K0cS pilot); the dollar figures are
DERIVED, not measured — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).**

*(Method note: at the unrounded rate `1.593e-6 × 1.6 = 2.5488e-6` the subtotal is
827.05 and the POINT 829.30. The registered figures use the rate **rounded to
2.549e-6**, which is what §10.1 prints and what reproduces to the digit.)*

**DOES THE COST SURVIVE A PER-CLOSURE FIELD-SET CHANGE? YES, AND THE REASON IS
STATED RATHER THAN ASSERTED.** The field set is a **completion instrument**: it
governs which files `mark_done_k0d.py` must find at `endTime`. It changes no
transport equation, no iteration count and no mesh. `RNGkEpsilon` and
`kOmegaSST` are both **two-equation** closures, so the per-cell-iteration rate
§10.1 measured on `kOmegaSST` is the rate the estimate already applies to both —
that assumption is unchanged by the repair, not created by it. `phi` is written by
the solver regardless of whether a completion set names it. **No line of §10.2
moves and the POINT and CEILING stand at 829.36 / 2 484.84.**

---

## 8. BATCHING AND MEMORY — measured on this box, 2026-08-25T18:07Z

**Cores: 16.** Five processes at ≥95 % CPU, measured live:
three `buoyantBoussinesqSimpleFoam` (pids 2203927 / 2203944 / 2203947, all at
`verification/runs/T-family/T1_runs/R_*_x`, **209 920 cells each**), one
`simpleFoam` (pid 2324888, `ansys_verification/VMFL003_M2`, 2 500 cells) and one
`python` (pid 2230463, 10.39 GB RSS, D-state). `/proc/loadavg` read
**21.01 / 14.40 / 10.20** — the 1-minute figure includes this lane's own
`find`/`grep` sweeps; the 15-minute **10.20** is the honest steady figure and it
exceeds the five CPU-bound processes, so some contention is already present that
the process list does not show.

**Memory rate, MEASURED not guessed:** `buoyantBoussinesqSimpleFoam` at
209 920 cells holds **487–507 MB RSS**, i.e. **~2.4 kB/cell** flat, or
**~2.08 kB/cell above a ~60 MB baseline** (the baseline inferred from
`simpleFoam` at 2 500 cells = 50 MB, **which is a different solver and so the
baseline is INFERRED, not measured**). Per K0d case:

| level | cells | RSS estimate | conservative bound (flat 2.4 kB/cell + 100 MB) |
| --- | ---: | ---: | ---: |
| L1 | 25 600 | ~113 MB | ~162 MB |
| L2 | 50 176 | ~164 MB | ~220 MB |
| L3 | 98 596 | ~265 MB | ~337 MB |

**All nine concurrent: ~1.58 GB estimated, ~2.15 GB on the conservative bound.**
Against `MemAvailable` **17.7 GiB** and this family's **standing 12 GiB floor**
(`LAB_STATE.md:1871`), the headroom is **5.7 GiB**. **Nine concurrent K0d cases
fit with ~3.5 GiB to spare on the conservative bound.** The binding memory risk
is **not K0d**: it is pid 2230463's 10.39 GB adjoint, and if a second such job
launches the floor is the constraint, not the cores.

**PROPOSED BATCHING — one batch of nine, which lands inside Sanaa's band.**
`5 + 9 = 14` of 16 cores = **87.5 %**, inside the 80–90 % target, leaving 2 cores
for the chief session, git and instruments. All nine are serial, `nProcs = 1`,
2D — no `decomposePar`, so there is no partitioner and no MPI contention.

**AND THE HONEST LIMIT OF THAT PROPOSAL, WHICH IS THE SCHEDULING FINDING.**
K0d's ladder is imbalanced: 167.55 core-min against 43.50. At the POINT rate the
utilisation decays as cases retire:

| elapsed | cases still running | cores busy | utilisation |
| ---: | --- | ---: | ---: |
| 0 | all nine | 14 | **87.5 %** |
| ~43.5 min | `M1_c`, `M2_c` done | 12 | 75.0 % |
| ~64 min | `C_lam` done | 11 | 68.8 % |
| ~85 min | `M1_m`,`M2_m`,`B_hi`,`I_hi` done | 7 | 43.8 % |
| ~168 min | `M1_f`,`M2_f` done | 5 | 31.3 % |

Mean K0d occupancy over its own critical path is `827.11 / 167.55 =` **4.94
cores**, so **mean utilisation is `(4.94 + 5)/16 =` 62 %, below the 80–90 %
target.** **K0d alone cannot hold the band for its whole window** — the target is
met at launch and decays because the ladder is imbalanced. **The remedy is not to
inflate K0d: it is to backfill the retiring cores from the team's queue**, which
is what Sanaa's *"batches of 8–12"* asks for. Under-loaded-with-a-queue is the
same defect as idle, at lower severity, and this table is what makes it visible
in advance.

**Contention arithmetic.** At the disclosed-acceptable 5–11 %, the solver
subtotal inflates to **868.5–918.1 core-min**, i.e. **35–37 % of the CEILING** —
the 2× ceiling absorbs it with a wide margin. Per
`COMPUTE_BUDGET_CHARTER.md` §6, contention is **named separately at completion,
never absorbed into the actual/predicted ratio**.

**Wall clock.** Critical path is `M1_f` / `M2_f` at **10 052.8 s = 2.79 h** at the
POINT rate, **5.58 h** at the CEILING rate; add 11 % contention and
**3.10 h / 6.20 h**. Both rows exceed 3 600 wall s **by design**, which §10.3
already registers so no one later cleans them as stalls.

---

## 9. WHAT THIS LANE DID NOT DO

- **Chose no physics.** The `nu`-versus-`beta` ruling is the supervisor's.
- **Wrote no registration**, superseding or otherwise, and created no case
  directory, no mesh and no run directory.
- **Launched nothing.** Zero core-minutes. Rule 12's calibration is not
  triggered because no process completed.
- **Edited no frozen file.** `K0d_PREREGISTRATION.md` and its five amendments
  are byte-unchanged; the hashes in §1 were taken before and after this write.
- **Touched no gate, band, threshold, cap or label**, and did not touch
  `docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md` or
  `docs/COST_CALIBRATION.md`.
- **Did not clear or touch the shared git index** (rule 10); the 986-line staged
  blob is reported in §1 and left exactly as found.
- **Sent nothing** (rule 7). Submissions remain **PARKED**.

**K0d remains `BLOCKED` on the supervisor's fire ruling. This document does not
unblock it.**
