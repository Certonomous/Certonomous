# cfd — THE `-O` BOUND, AND THE BUILD-GUARD SWEEP: **SEVEN ASSERTS IN TWO FILES, AND THEY GUARD MESH VALIDITY**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **ZERO COMPUTE.** Extends `L-332` and
`CFD_ASSERT_EXPOSURE_CLOSEOUT_2026-08-25.md` (`f7c21285`).

---

## 1. THE BOUND — VERIFIED FOR cfd, AND IT MUST TRAVEL WITH EVERY RECORD CITING `L-332`

> **`PYTHONOPTIMIZE` is UNSET on this box. Across the whole tree, exactly EIGHT
> files mention `python3 -O` or `PYTHONOPTIMIZE`, and every one is either an
> instrument that DRIVES the flag deliberately as a control, a record ABOUT the
> exposure, or a note discussing it. NO run script invokes `python3 -O` to produce a
> graded artifact.**

**Therefore: NO GRADED VERDICT ON RECORD — in cfd or anywhere — WAS PRODUCED UNDER
`-O`. THE EXPOSURE IS LATENT, NOT LIVE.** What is measured is that these invariants
**would** evaporate if it ever were.

**This bound is binding on how the finding is stated.** A lesson implying existing
verdicts are compromised **overstates**, and overstatement would provoke exactly
the re-audit **Sanaa's meta-work cap forbids.** **`L-332` and every record citing it
carries this paragraph.** Amendment dispatched.

**I am recording this against my own earlier phrasing.** I wrote that the exposure
*"manufactures a positive assertion of having checked"* — **true of what `-O` WOULD
produce, and I did not bound it at the time.** The measurement of the false
certification stands exactly as taken; **what it licenses is narrower than my
wording implied.**

## 2. THE BUILD-GUARD SWEEP — AND THE RESULT INVERTS THE PREDICTION FOR MY TERRITORY

The relayed extension: build-time guards are the largest class by count in thermal
territory — **21 of 35** — and under `-O` each **produces a silently wrong artifact
that becomes a graded run's input**, so **the grader, flag-proof or not, then grades
the wrong case correctly.**

**Measured across the cfd builders named:**

| instrument | asserts | `raise` | state |
|---|---:|---:|---|
| `build_ladder_attempt2.py` (F12 ladder) | **0** | 2 | **clean** |
| `sdk/workflows/rae2822_case9.py` (F12 case construction) | **0** | 15 | **clean** |
| `sdk/workflows/tmr_verification.py` | **0** | 32 | **clean** |
| `cases/F13_onera_m6/m6_section.py` | **0** | 0 | **clean** |
| **`cases/F13_onera_m6/make_blockmesh_m6.py`** | **6** | 0 | **EXPOSED** |
| **`cases/F1_onera_m6/make_blockmesh_f1.py`** | **1** | 0 | **EXPOSED** |

> **cfd's build-time exposure is SEVEN asserts in exactly TWO files, both ONERA M6
> `blockMesh` generators. The three instruments the extension named first — the F12
> ladder builder, `rae2822_case9.py`'s case construction, and `tmr_verification.py`
> — are ALL CLEAN, and they already use `raise` (2, 15 and 32 sites).**

**The prediction for my territory was wrong in the direction that matters, and I am
recording that rather than quietly banking it.** The exposure is real but
**concentrated**, not distributed.

## 3. WHAT THE SEVEN GUARD — AND IT IS THE EXACT CLASS

| site | guard |
|---|---|
| `make_blockmesh_m6.py:360` | **face orientation** — `ABORT: N faces cannot be oriented` |
| `:362` | **zero-area face** |
| `:384` | **faces per cell within 5..6** — hex topology integrity |
| `:420` | **collapsed face** — `ABORT: collapsed face q -> u` |
| `:85`, `:86` | chord-station array length and endpoint integrity |
| `make_blockmesh_f1.py:66` | **undefined vertex** |

**Under `-O` every one vanishes and the generator emits a `blockMeshDict` carrying
inverted, zero-area, collapsed or mis-connected faces — silently.** Physical
validity guards on a generated case, exactly as described.

**AND ZERO-AREA FACES ARE NOT HYPOTHETICAL ON THIS GEOMETRY. THEY OCCURRED.** The
M6 amendment records the H-block lens cap **refused by `blockMesh` itself at
`rc = 134` with 48 ZERO-AREA FACES.** **Line 362 is the guard against precisely
that failure, on the geometry where it has already happened.**

**An honest caveat that cuts against the alarm, stated because it is true:**
`blockMesh` **refused independently** in that instance — so for the zero-area case
the assert is **not the only line of defence**. **`:360` (orientation) and `:384`
(faces/cell) have no such demonstrated second line**, and an inverted or
mis-connected cell that `blockMesh` accepts is a mesh that solves and grades. **That
is where the real risk sits, and it is narrower than "seven guards could vanish".**

## 4. RULING

**`make_blockmesh_m6.py` is NAMED IN THE FROZEN `F13_ONERA_M6_PREREGISTRATION.md`
(:317), and that registration HAS FIRED** — `C1.5` records **`GATE FAIL` on §5
admission at all three levels; the ladder is closed and dead.**

> **NOT EDITABLE. I am not authorising a repair to either fired builder, for the
> same reason I refused it for `launch_f12_rung.py`: rule 2 closed that door, and
> "the replacement is better" is not an exception — it is the argument rule 2
> exists to refuse.**

**Recorded, not repaired.** And the disposition is the same as the unpinned-`_foam`
finding: **nothing rests on it today** — the M6 ladder is dead, its `GATE FAIL`
rests on `checkMesh`'s own reported maximum, and **the topology study's re-runs
reproduced byte-identically under the repaired, flag-proof readers.**

**BINDING ON THE SUCCESSOR REGISTRATION:**
1. **Every build guard is a GATE ON THE ARTIFACT and must survive the flag** —
   `raise` or `sys.exit`, never `assert`.
2. **Each is driven under `-O` and required to REFUSE**, per `L-332`'s executable
   check.
3. **The success message prints INSIDE the passing branch**, so removing the check
   removes the claim.
4. **An AST check requiring zero `Assert` nodes** in the builder — it catches a
   revert without running anything.

## 5. THE WORST MEASURED FORM, CARRIED FOR THE RECORD

Two instances from heat-transfer's triage, both stronger than cfd's own:

- **`analyse_t8.py:1054` — the executable form of standing rule 5, written as an
  `assert`** — driven under `-O` on a sacrificial copy: **`verdict='MUTATED-VERDICT'`,
  PROCEEDED.**
- **On frozen-constant restoration guards the `-O` column was worse than "the check
  vanished": the frozen layer-k map was LEFT CORRUPTED IN MEMORY at 0.4 / 0.004, so
  every subsequent measurement in that process ran against a wrong frozen
  constant.** **The guard was the only thing standing between a monkey-patched frozen
  module and the rest of the run.**

**That second one is the sharpest argument in the whole finding**, and it is not
cfd's: **a stripped guard does not merely fail to check — it can leave the process
in the corrupted state the guard existed to undo.**
