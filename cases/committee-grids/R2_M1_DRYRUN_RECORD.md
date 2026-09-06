# R2-M1 DRY RUN — the driver's PRODUCTION SEQUENCE executed end to end on a stand-in seed

> # ⚠ NOT A RESULT.
>
> **This record describes a dry run of `cases/committee-grids/run_r2_m1.sh` against a 216-cell
> stand-in, not against the DPW5 CRM grid. It grades nothing. No number in it may be quoted as a
> measurement of anything on the committee grid, and it produces no force, drag, lift, moment or
> CRM claim of any kind.**
>
> **A GREEN HERE IS NOT "THE SEQUENCE VERIFIED ON REAL DATA."** §3 states exactly what it does not
> cover. Read §3 before reading §2.

*2026-09-06. Team: cfd. Registration: `verification/campaign/RUNG2_CRM_M1_PREREGISTRATION.md`
(Amendment 2, §14). Ruled by the cfd supervisor before check 4.*

---

## 0. WHY IT WAS RUN

`run_r2_m1.sh`'s cap, root guard, usage guard, writer block and comparator had each been driven
individually. **Its production sequence had never executed in order.** `L-495`: *a selftest that
exercises the PARTS but never the PRODUCTION SEQUENCE measures its own coverage, not the
instrument, and it hides defects BEHIND each other.* The fix for parts-coverage is to **run the
sequence**, not to run it bigger.

**The risk bought down is not the 5.27 core-min.** It is that **a defect in assembly could produce
a plausible wrong artifact rather than a crash.** A crash on the real grid would be seen; a subtly
mis-assembled arm might be graded.

**Reproduce it with:**

```
bash cases/committee-grids/build_r2_m1_standin.sh <dir> 4
bash cases/committee-grids/run_r2_m1.sh --dry-go <dir>
```

Both scripts are in this repository. **No scratch path is cited as evidence anywhere in this
record** (L-186) — everything below is reproducible from the two commands above.

**The stand-in exercises the warm-start chain rather than skipping it.** `build_r2_m1_standin.sh`
produces `processor*/200/{U,k,omega}` **with a real solver** and **in `writeFormat binary`**, and
asserts both before returning. That is deliberate: **M0's guard died reading a binary field in text
mode**, so a stand-in writing ASCII would sail through the repaired guard and prove nothing about
the defect the repair exists for. Its patches are named `wall`, `symmetry`, `farfield` for the same
reason — different names would drive the guard into its refusing branch and the run would report a
mapping failure that was an artifact of the fixture.

---

## 1. THE TWO DEFECTS IT FOUND, WHICH IS WHY IT WAS WORTH RUNNING

### 1.1 A fixture defect — and the driver was RIGHT to refuse

The first `--dry-go` **failed at exit 7**, four steps into assembly:

> `endTime not rewritten in .../B1/system/controlDict` → `ABORT(7): B1 endTime`

The first stand-in `controlDict` wrote `stopAt endTime;   endTime 120;` on **one line**.
`set_endtime` anchors on `^\s*endTime\s+<number>;`, and the **real seed has them on separate
lines** (`A0/system/controlDict:12-13`). **Semantically identical, textually different.**

**This was a FIXTURE defect, not a driver defect, and the distinction is the finding.** The driver
behaved correctly — and better than correctly: `set_endtime` **raises when its substitution count is
not exactly 1**, so it failed *loudly* at exit 7 instead of silently leaving B1 at `endTime 120`.
Had it been a silent no-op, **B1 would have run to 120 instead of 50 and the admission gate
`R2M1-G4` would have graded the wrong thing.** The dry run confirms that loud-failure property by
exercising it.

The repair is in the fixture: one key per line, plus **the anchor added to the builder's assertion
list — which had checked three anchors and omitted `endTime`.** ⚠ **That omission is the same
failure mode the supervisor named about the `selftest_cap` globals**: an enumeration that can
silently be incomplete. The builder now says so in a comment, and says that a new driver mutation
requires a new anchor here.

### 1.2 A stale note written into `STATUS` beside the fact that contradicted it

The completed dry run wrote:

```
b1_warmstart_mapped=1
b1_warmstart_note=not attempted        <-- STALE
```

`B1_FAIL_REASON` is initialised to `"not attempted"` and was **never cleared on success**, so a
sentence describing a state that no longer held was emitted **next to the fact that contradicted
it**. Nothing crashed; the artifact was simply wrong in a quotable way.

⚠ **This is this campaign's own disease.** M0's `WARMSTART.txt` said `FAILED TO MAP` about a map
that had already succeeded, and that sentence travelled through a lane, a supervisor, the chief and
to Sanaa unchallenged (`L-496`). **A note that outlives the state it described is exactly how a
false sentence gets quoted later.** Fixed: the note is cleared to `none -- mapped` on success, with
the reasoning in the code.

**Neither defect would have been found by any part-wise control**, because neither is in a part —
1.1 is in the *order* (assembly must precede the solve loop) and 1.2 is in a *variable's lifetime
across* the sequence. That is L-495's point, measured.

---

## 2. WHAT THE SEQUENCE DID, AFTER THE REPAIRS

`--dry-go`, `rc = 0`, 11 wall s, 4 ranks, 216 cells.

**The warm-start chain — the path that produced M0's false record — executed in full:**

| step | result |
|---|---|
| `B1_reconstruct` (`reconstructPar -time 200 -fields '(U k omega)'`) | `rc = 0` |
| **the guard's own control, at run time, on the real reconstructed field** | **accepts the good field, REFUSES the `farfield`-scrubbed copy — DISCRIMINATES** |
| `warm_guard` on the reconstructed `U` | passes, **reading a binary field** |
| `B1_decompose_fields` (`decomposePar -fields -time 0`) | `rc = 0` |
| marker | `B1/WARMSTART_MAPPED` — *"MAPPED via reconstructPar(200) -> guard(binary-safe, discriminated) -> decomposePar -fields"* |

**And the warm field genuinely landed rather than the command merely exiting 0** — which is the
whole distinction §1.2 of the registration is about:

| | bytes | note |
|---|---|---|
| stand-in seed `0/U` | 334 | uniform |
| `B0/0/U` (untouched arm) | 334 | unchanged, as it must be |
| **`B1/0/U`** | **9,920** | **the reconstructed warm field, binary** |
| `B1/processor0/0/U` | present | re-decomposed onto this arm's own addressing |

**All seven arms assembled EXACTLY as the registration's §4 table specifies** — checked field by
field, not inferred from `rc = 0`:

| arm | `endTime` | energy | `transonic` | `pMin` | writer block | steps completed | W1 records |
|---|---|---|---|---|---|---|---|
| B0 | **120** (seed's own) | `sensibleInternalEnergy` | no | — | yes | 120 | 120 |
| B1 | **50** (the only admission arm) | `sensibleInternalEnergy` | no | yes | yes | 50 | 50 |
| B2 | 3 | `sensibleInternalEnergy` | no | **—** (must be B0's case; only the trap differs) | yes | 3 | 3 |
| B5 | 3 | `sensibleInternalEnergy` | no | yes | yes | 3 | 3 |
| B3 | 3 | **`sensibleEnthalpy`** | no | yes | yes | 3 | 3 |
| B4 | 3 | `sensibleInternalEnergy` | **yes** | yes | yes | 3 | 3 |
| B6 | 3 | **`sensibleEnthalpy`** | **yes** | yes | yes | 3 | 3 |

**The 2×2 is correctly wired**: B5 (e, no) / B3 (h, no) / B4 (e, yes) / B6 (h, yes). **W1 records
== steps completed on every arm**, which is `R2M1-G1`'s condition, satisfied on a case where the
arms actually take steps.

**The registered run root was never created.** `--dry-go` asserts, in both directions, that its root
is neither the registered root nor inside it; pointed at the registered root **it refuses (exit 2)**
and that refusal was driven. The dry root carries `DRY_RUN_NOT_A_RESULT`, **written before anything
else in the run**.

**`R2M1-G0` returned `NOT A RESULT`** — `B0 rc=0, class=COMPLETED, thermo frames=0` — and the run
verdict is `NOT A RESULT`. **That is correct gate behaviour, not a finding about the arms.** G0 is a
reproduction control expecting `rc = 136` and a thermophysical frame; a stand-in that completes
cannot satisfy it, and the gate stopping the probe there is the precondition working.

**Comparator coverage is therefore split across two exercises, and neither alone is sufficient:**

| | what it drove |
|---|---|
| this dry run | the **driver's** sequence; the comparator only as far as `R2M1-G0` |
| the real-data drive (registration §8.2) | `G0`→`G1`→`G2`→`G3`→`G4`→`G5` on **M0's real logs**, `rc = 0`, correct shapes |

---

## 3. ⚠ WHAT THIS DOES NOT COVER — read this before quoting anything above

**A green in §2 must not be read as the sequence verified on real data.** It is not.

1. **THE REAL SEED.** The stand-in is a **216-cell box**. DPW5 L1.T hex is **638,976 cells** —
   roughly **3,000×** — with `max_non_orthogonality 89.7134`, **11,506 severe non-orthogonal
   faces**, `max_skewness 14.0594` and `max_aspect_ratio 14426.8`
   (`RUNG0b_MESH_IMPORT_runs/DPW5_L1T_hex/.../birth_certificate.json`). **Nothing about mesh
   quality, memory footprint or I/O at that size is tested here.**
2. **THE REAL DECOMPOSITION.** This ran **4** subdomains. The registered run is **14**. The real
   seed and the real warm source were each decomposed with `scotch` **independently**, which is the
   entire reason the warm start reconstructs and re-decomposes instead of copying processor to
   processor — **and that mismatch does not exist in this fixture.**
3. **THE REAL PHYSICS.** These arms **completed**; R2-M1's arms are expected to **abort at
   iteration ≤ 2**. This dry run says **nothing** about whether the compressible path is
   admissible, nothing about the mechanism, and nothing about the 2×2's outcome.
4. **THE REAL WARM-START FIELD.** Here it is a ~10 kB binary field over 4 subdomains. The real one
   is **15.6 MB** reconstructed from **14**. ⚠ **`decomposePar -fields` HAS STILL NEVER RUN ON THE
   REAL GRID.** Its success here is evidence about the **plumbing**, not about the real case: its
   cost remains **ESTIMATED, not measured**, its success remains **not assumed**, and `R2M1-G3`
   still returns **`BLOCKED`, not `GATE FAIL`**, if it fails (registration §2.4, §6.2, §9).
5. **THE REGISTERED CAP.** This ran under its own **10.0 core-min** cap, **not** the registered
   **55.0**. The cap's *mechanism* is driven by `--selftest-cap` (7/7); the registered *value* is
   untested by anything and does not need to be.
6. **THE `--go` PATH ITSELF.** `--dry-go` and `--go` share every function below the mode switch,
   but they are **not the same invocation**. The first `--go` remains the first execution of the
   sequence **against the real seed, at 14 ranks, on the committee grid.**

---

## 4. COST

| | |
|---|---|
| per completed dry pass, by the driver's own accounting at true rank counts | **0.2667 core-min** (16 core-s, `COST.tsv`) |
| conservative **upper bound** on the gross across all three dry passes and three stand-in builds | **≈ 2.7 core-min** — ~40 wall s priced as if every second were 4-rank; the true figure is **lower** because most steps are serial. **Stated as a BOUND, not a measurement.** |
| `cost_basis` | **on-box-owner-stated**, `c7a.4xlarge` $0.0513/core-h. **Dollars DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| derived dollars at the bound | **$0.0023 DERIVED** |
| DPW5 grid solves | **zero** |

**Check-repair cycles on the dry-run stage: 2** — §1.1 (fixture line shape) and §1.2 (stale note).
Both are recorded above rather than quietly repaired, because **a dry run that reports only its
final green has thrown away the thing it was run for.**
