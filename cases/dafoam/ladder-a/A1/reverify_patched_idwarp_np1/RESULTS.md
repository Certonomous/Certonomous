# A1 NACA0012 — re-verification at np=1, shipped vs patched IDWarp: RESULTS

**Run 2026-08-21, Lane A.** Pre-registration: `PREREGISTRATION.md` in this directory, written and
committed **before** any arm launched; it is not revised by this file. Nothing filed upstream.

**Headline: every registered prediction held, including the three falsifiers that could have
stopped the run. The published FAIL reproduces at np=1 to 5 significant figures, the new patched
image reproduces the bind-mount's PASS, and the FD-invariance control is bit-exact on all 8
components and all 10 rows.**

Raw logs: `/home/ubuntu/certonomous-runs/P1-a1-np1/{stock,patched,wrongstep}.log`.
Ledger: `.../ledger.txt`. Staged case copies: `.../{stock,patched,wrongstep}/` — the published
`W5-regrade/a1_unpatched` directory was **copied, not run in**, so the regrade's evidence is intact.

---

## 1. Arms as executed

| arm | image | `IDWARP_SO_MD5` (printed by the run itself) | np | FD step | rc |
|---|---|---|---|---|---|
| 1 SHIPPED | `dafoam/opt-packages:latest` | `f0fcb488e0e98156575cd19548e91663` (**stock**) | 1 | 1e-3 | 0 |
| 2 PATCHED | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` (**patched**) | 1 | 1e-3 | 0 |
| 3 TRIVIAL BASELINE | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` (**patched**) | 1 | **1e-8** | 0 |

Each arm printed the md5 of the `libidwarp.so` **it actually loaded**, from inside the process that
loaded it. Since the version string reads `2.6.2` on both stacks and the two `.so` files are the
same 491,344 bytes, that hash is the only thing that identifies the stack
(`../../patched_build/BUILD.md` §2). Arm 3 differs from arm 2 by exactly one line of `runScript.py`
(`step=1e-3` → `step=1e-8`), verified by `diff` before launch.

## 2. Verdict rows — SHIPPED and PATCHED separate

Band (`../../A_stepsize_study.md:91-93`): PASS ≤5% with zero flagged components; CONDITIONAL 5-15%;
>15% **or any flagged component** → FAIL.

| row | arm | image | predicted | measured | verdict |
|---|---|---|---|---|---|
| `CD` wrt `shape` | **SHIPPED** | `dafoam/opt-packages:latest` | 11.4% ± 0.5 pt, one flip at idx6 | **11.4274%** (`1.142740e-01`), **one flip, idx6, 640.3696%** | **GATE FAIL** |
| `CD` wrt `shape` | **PATCHED** | `dafoam-idwarp-rot:v1` | 0.0375% ± 0.01 pt, zero flips | **0.03796%** (`3.795529e-04`), **zero flips**, idx6 1.1888% right-signed | **PASS** |
| `CD` wrt `shape` | **TRIVIAL BASELINE** | `dafoam-idwarp-rot:v1`, step 1e-8 | > 50% | **132.75%** (`1.327522e+00`) | **GATE FAIL — as designed** |
| `CL` wrt `shape` | SHIPPED | stock | ≈1.67% | **1.6705%** (`1.670513e-02`) | **PASS** |
| `CL` wrt `shape` | PATCHED | patched | ≈0.0149% | **0.01483%** (`1.482624e-04`) | **PASS** |
| `CL` wrt `shape` | TRIVIAL BASELINE | patched, step 1e-8 | large | **273.77%** (`2.737699e+00`) | **GATE FAIL — as designed** |
| `CD` wrt `patchV` | SHIPPED | stock | ≈0.232% | **0.2442%** (`2.441810e-03`) | **PASS** |
| `CD` wrt `patchV` | PATCHED | patched | unchanged | **0.2442%** — *bit-identical to SHIPPED* | **PASS** |
| `CL` wrt `patchV` | SHIPPED | stock | ≈0.232% | **0.2153%** (`2.153367e-03`) | **PASS** |
| `CL` wrt `patchV` | PATCHED | patched | unchanged | **0.2153%** — *bit-identical to SHIPPED* | **PASS** |
| `volcon`/`thickcon`/`rcon` wrt `shape` | SHIPPED | stock | 1e-14…1e-10 | `4.366597e-14` / `1.265004e-13` / `1.363491e-10` | **PASS** (machine precision) |
| `volcon`/`thickcon`/`rcon` wrt `shape` | PATCHED | patched | unchanged | **identical to every printed digit** | **PASS** |
| six `wrt patchV` constraint rows | both | — | 0/0 | `0.000000e+00` vs `0.000000e+00`, rel `nan` | **NOT A RESULT** (structural zeros) |

## 3. The control that makes the comparison readable: the FD did not move

Registered falsifier 2(a): *"Any `Fd Magnitude` differing between arms 1 and 2 → stop and report."*

| row | stock FD | patched FD | moved? |
|---|---|---|---|
| `CD` wrt `patchV` | `4.612331e-03` | `4.612331e-03` | **no** |
| `CD` wrt `shape` | `6.489584e-02` | `6.489584e-02` | **no** |
| `CL` wrt `patchV` | `1.342638e-01` | `1.342638e-01` | **no** |
| `CL` wrt `shape` | `4.977993e+00` | `4.977993e+00` | **no** |
| `volcon` / `thickcon` / `rcon` wrt `shape` | `5.225577e+00` / `4.006319e+01` / `3.784176e+01` | identical | **no** |

And **per component**, not just per norm — all eight raw `Jfd` entries of `CD wrt shape`:

| idx | stock FD | patched FD |
|---|---|---|
| 0 | `-1.01316400e-02` | `-1.01316400e-02` |
| 1 | `-1.98630500e-02` | `-1.98630500e-02` |
| 2 | `+7.26456000e-03` | `+7.26456000e-03` |
| 3 | `+1.29019600e-02` | `+1.29019600e-02` |
| 4 | `+3.99843900e-02` | `+3.99843900e-02` |
| 5 | `+4.33902000e-02` | `+4.33902000e-02` |
| 6 | `-1.05312000e-03` | `-1.05312000e-03` |
| 7 | `+3.53190000e-03` | `+3.53190000e-03` |

**Eight of eight bit-identical.** The patch is derivative-only and the image delivers it as a clean
single-variable change. **`dafoam-idwarp-rot:v1` is validated for use.**

Registered falsifier 2(c) also held: the `patchV` rows and the three geometric-constraint rows — the
ones that never cross `warpDeriv` — are identical to every printed digit across arms 1 and 2. That
is identity-gate **IG-2** behaving as the settlement says it must
(`../../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §5.2); it is reported as evidence and, per W-2,
**was not gated on**.

## 4. Per-component tables — the whole point of `compact_print=False`

### 4.1 SHIPPED, `CD wrt dvs.shape`, aggregate `1.142740e-01`

| idx | analytic | FD | rel. err | flag |
|---|---|---|---|---|
| 0 | `-1.13416500e-02` | `-1.01316400e-02` | 11.9429% | |
| 1 | `-2.21795800e-02` | `-1.98630500e-02` | 11.6625% | |
| 2 | `+6.79852000e-03` | `+7.26456000e-03` | 6.4153% | |
| 3 | `+1.23801600e-02` | `+1.29019600e-02` | 4.0443% | |
| 4 | `+3.89383200e-02` | `+3.99843900e-02` | 2.6162% | |
| 5 | `+4.23425000e-02` | `+4.33902000e-02` | 2.4146% | |
| **6** | **`+5.69074000e-03`** | **`-1.05312000e-03`** | **640.3696%** | **SIGN FLIP** |
| 7 | `+3.46681000e-03` | `+3.53190000e-03` | 1.8429% | |

**Exactly one sign flip, at index 6.** Registered falsifier 1(b) — "no sign flip, or a flip at an
index other than 6" — did not fire.

### 4.2 PATCHED, same row, aggregate `3.795511e-04`

| idx | analytic | FD (unchanged) | rel. err |
|---|---|---|---|
| 0 | `-1.01337900e-02` | `-1.01316400e-02` | 0.0212% |
| 1 | `-1.98777100e-02` | `-1.98630500e-02` | 0.0738% |
| 2 | `+7.26758000e-03` | `+7.26456000e-03` | 0.0416% |
| 3 | `+1.28972800e-02` | `+1.29019600e-02` | 0.0363% |
| 4 | `+3.99972200e-02` | `+3.99843900e-02` | 0.0321% |
| 5 | `+4.33856900e-02` | `+4.33902000e-02` | 0.0104% |
| **6** | **`-1.06564000e-03`** | `-1.05312000e-03` | **1.1888%** |
| 7 | `+3.52810000e-03` | `+3.53190000e-03` | 0.1076% |

**Zero sign flips; 8 of 8 in band.** idx6 goes from 640.37% with the wrong sign to 1.19% with the
right one. Note the analytic moved **toward the pre-existing, unchanged FD** on every component —
the direction a genuine fix must move and a comparison-rigging artifact could not.

### 4.3 The trivial baseline earned its keep

Arm 3 is the patched stack — the one that passes at 0.038% — run at `step=1e-8`:

| row | patched @ 1e-3 | patched @ 1e-8 |
|---|---|---|
| `CD` wrt `shape` | **0.03796%** | **132.75%** |
| `CL` wrt `shape` | 0.01483% | **273.77%** |
| `CD` wrt `patchV` | 0.2442% | **121.77%** |
| `CL` wrt `patchV` | 0.2153% | **221.68%** |
| `volcon` wrt `shape` | `4.366597e-14` | `4.236290e-09` |
| `thickcon` wrt `shape` | `1.265004e-13` | `1.137830e-08` |
| `rcon` wrt `shape` | `1.363491e-10` | `1.841192e-08` |

**The instrument can still fail on a stack that passes.** Arm 2's 0.038% is therefore a property of
the derivative, not of a harness rendered incapable of returning a large number. The analytic column
is **bit-identical** between arms 2 and 3 (e.g. `CD/shape` `6.490496e-02` in both) — only the FD
moved, which is exactly right, since the step is an FD-side parameter.

**An unregistered bonus finding.** The three *geometric-constraint* rows also degrade, by 4–5 orders
of magnitude (`1e-13` → `1e-8`). Those rows never touch the CFD solve; their degradation is pure
FD roundoff. That is an independent confirmation that arm 3's damage is the step, not the physics
and not the patch — and it is a cleaner diagnostic than the CD/CL rows because those constraints
have no defect in them to confound it.

## 5. What the np=1 arm settled that was not the question

The published A1 numbers were all measured at np≥2; **no stock np=1 A1 `check_totals` existed.**
Comparing arm 1 against the published np=2 regrade (`W5-regrade/a1_unpatched_stock.log`):

| row | published np=2 | measured np=1 | analytic moved? |
|---|---|---|---|
| `CD` wrt `shape` aggregate | `1.142743e-01` | `1.142740e-01` | 7th digit |
| `CD` wrt `shape` analytic | `6.460294e-02` | `6.460292e-02` | 7th digit |
| idx6 rel. err | 640.2586% | 640.3696% | 4 s.f. agreement |
| `CL` wrt `shape` analytic | `4.958230e+00` | **`4.958230e+00`** | **not at all** |
| `CD` wrt `patchV` analytic | `4.601100e-03` | **`4.601100e-03`** | **not at all** |
| `CL` wrt `patchV` analytic | `1.345505e-01` | **`1.345505e-01`** | **not at all** |
| `volcon`/`thickcon`/`rcon` | `4.366597e-14`/`1.265004e-13`/`1.363491e-10` | **identical** | **not at all** |

**A1's analytic gradient is decomposition-invariant to every printed digit on three of four rows and
to the 7th digit on the fourth.** What little movement there is between np=1 and np=2 lives in the
**FD** column (`CD/patchV` FD `4.611728e-03` → `4.612331e-03`; `CL/patchV` FD `1.342447e-01` →
`1.342638e-01`), which is why `CD wrt patchV` reads 0.2442% here against 0.2317% published — an
FD-noise-level difference, not a gradient change. This is consistent with, and independent of, the
decomposition-invariance measured on the limiter/freestream variant
(`../../VERIFICATION_A1_serial_limiter_supervisor_sweep.md` axis 2, 3.9e-04), and it is the first
time it has been shown on the **stock tutorial** case.

## 6. Cost, against the registered ceiling

Registered ceiling: **20 core-min / $0.02.**

| arm | ranks | wall | core-min | $ @ $0.0513/core-hr |
|---|---|---|---|---|
| 1 SHIPPED | 1 | 98 s | 1.633 | $0.0014 |
| 2 PATCHED | 1 | 104 s | 1.733 | $0.0015 |
| 3 TRIVIAL BASELINE | 1 | 54 s | 0.900 | $0.0008 |
| **total solve** | | **256 s** | **4.267** | **$0.0036** |
| image build (one-off, `../../patched_build/BUILD.md`) | — | 208 s | 0 (no solve) | ≈$0.00 |

**4.27 core-min against a 20 core-min ceiling — 21% of budget.** Predicted ~6.6; measured 4.27, i.e.
**35% under the prediction**, because np=1 turned out cheaper than the np=2 anchor scaled. Arm 3 is
faster than arms 1–2 because at `step=1e-8` the perturbed primals restart from a nearly-identical
state and converge in fewer iterations.

**One measurement-condition disclosure:** arms 2 and 3 ran while another lane held a container on
this box (`docker ps` showed a concurrent `dafoam/opt-packages:latest` during arm 2, and host load
rose from 0.13 to 4.51). Wall clocks here are therefore **contended** and should not be used as a
clean cost basis for scaling. The derivative values are unaffected — each arm had its own `--cpus=2`
cap and its own container.

## 7. What this run cannot see — restated against what it found

The four limits registered in `PREREGISTRATION.md` §6 all stand, and one is now sharper:

1. **The limiter defect is absent from this run by construction.** All three arms used the
   tutorial's unlimited `div(phi,U) bounded Gauss linearUpwindV grad(U)`. The second, independent A1
   defect — `cellLimited Gauss linear 1` feeding `linearUpwind`, which reads **92.8%** at np=1 **with
   the rotation guard already patched** — cannot appear here, because the scheme that triggers it is
   not installed. **Arm 2's PASS is a PASS for this scheme configuration only, and must not be read
   as "A1 is fixed".** The number that would make this concrete is C-3 (operator-level cross-residual
   on A1 serial with the limiter, ~2 core-min), still unbought.
2. **The decomposition axis** — absent by construction at np=1. §5 is a *comparison* against a prior
   np=2 run, not a decomposition arm.
3. **Regime 2 of the rotation defect** — invisible. `check_totals` evaluates at the undeformed
   baseline where the `sqrt(eps)` guard fires; the near-threshold ill-conditioned regime only appears
   at deformed states, is unpatched by design, and would govern any optimisation run from iteration 1.
4. **A vector norm can still hide a component.** Mitigated here rather than assumed away: §4 prints
   all eight, which is how idx6 is visible as `640.3696%` rather than folded into `11.4274%`.

## 8. Ledger

| item | value |
|---|---|
| solver core-minutes | **4.267** (against a registered ceiling of 20) |
| dollars | **$0.0036** |
| containers started | 3, all `--rm`, all foreground-or-polled, all rc=0 |
| processes needing a kill | 0 |
| frozen files edited | 0 |
| published case directories written into | 0 (staged copies used) |
| filed upstream | nothing |
