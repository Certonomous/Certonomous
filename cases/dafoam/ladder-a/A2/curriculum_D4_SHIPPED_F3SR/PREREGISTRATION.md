# D4S-F3SR — pre-registration: **THE TWO-ROW ENDPOINT FD TABLE, WITH THE AGE CLAUSE AND THE CAP FRAME REPAIRED**

**Item id:** `D4S-F3SR` — successor of `D4S-F3S` (`cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_F3S/`, **FROZEN at `8dfb4598c2810f136d6d2fb69983fe77e2455a7d`**, no addenda), itself successor of `D4-SHIPPED` (Addendum 2e at `d75b38d2`) and of `curriculum_D4` §11 (`1697ea49`). **Version 1.0, FROZEN at the commit that carries this file.** Authored 2026-08-27 by dafoam lane I on the dafoam-supervisor's order of 2026-08-27 (`[lab-attributed]`). **Nothing here is sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7). **No frozen file is edited** (rule 6): `D4S-F3S`'s files are cited by path and md5 and are not touched; the two instruments this item reuses are **byte-identical copies**, and the four it changes are **new files with a DELTAS diff beside each**.

> **ID-NAMESPACE WARNING (carried by every document in this family).** `docs/DOCKET.md:129,130,139,140` carries fleet defects numbered D5, D6, D14, D15; those are different objects from the dafoam curriculum items of the same number. No bare `D<n>` here is a docket row.

> **DISCLOSURE, MADE FIRST BECAUSE IT BEARS ON EVERY BAND BELOW (rule 2).** This lane **has read `D4S-F3S`'s graded output**, including both rows' G5 values. **No band, threshold, cap or label has moved as a result**, and §2 states each one's provenance so a reader can check that claim rather than take it. The one band that is new — P5 — is **strictly tighter** than the one it sits beside and is labelled as derived from a measurement already seen, so it can only turn a `HIT` into a `MISS`, never the reverse.

---

## 1. WHY THIS ITEM EXISTS — two registration defects, one of them a singleton and one of them a class

### 1.1 `D4S-F3S-AGE-DEF-1` — an age clause that was unsatisfiable by construction

`D4S-F3S` graded **19 of 20 gate readings `PASS`** and was recorded **`NOT A RESULT`** on one limb. `G5` was 5/5 components in band on **both** rows — aggregate vector-relative error **0.1634 %** (patched) and **0.3501 %** (shipped) against a 5 % band, no sign flips, plateau met everywhere. `G_ACC` accepted 22/22 primals on both rows. `G6`'s planted control moved in all three channels; `G9`'s digests were exact and the two rows distinct. The single failing limb was **`G1`'s age clause, `n_stale = 1`, on `OptView.hst`**.

**`OptView.hst` is a staged INPUT of this item and never a product.** `d4s_f3s_stage_arm.sh:61-63` copies it with `cp -a`, logging *"mtime semantics = cp -a, PRESERVE"*, and the item re-runs no optimiser. **A file that is never produced can never post-date the launch, so the clause was unsatisfiable by construction.** Measured from disk on both arms of the predecessor's run root: `F-S` datum `1787838479`, `OptView.hst` mtime `1787728010` (30.6 h older); `F-P` datum `1787839128`, `OptView.hst` mtime `1787689205`. The entry at `d4s_f3s_grade.py:61` was inherited from the optimiser-arm shape, where **`D5`'s `SOLVER_ARTEFACTS` uses the same file correctly, because there it genuinely is a product.**

**The predecessor's 26/26 grader selftest could not catch it.** Its fixture **created `OptView.hst` fresh** at `d4s_f3s_grade.py:599-601` against a datum pinned at epoch `1000000000`, so **real staging semantics were never exercised**. A passing selftest is what makes this class dangerous, and the repair therefore lands in the fixture as much as in the list (§3.3).

**The defect is a measured SINGLETON, and this is a singleton repair, not a class migration.** The sweep across the eight drop-path items (`AV1R`, `AV2R`, `D18`, `SO1a`, `SO1b`, `FADR`, `W3_r3`, `D5_r4`) came back clean: every age-checked entry in every one of their graders is a product of that item's own run. Across the dafoam corpus `d4s_f3s_grade.py:61`'s `OptView.hst` is the only age-checked entry an item does not produce.

**Why the predecessor's verdict STANDS and this is a successor, not an amendment.** (i) Rule 2 — `D4S-F3S` spent **75.867 core-min**, the comparator has fired, gates are closed. (ii) Standing rule 5 is one-way: a gate may turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse, and repairing the list in place would convert `NOT A RESULT` → `PASS` on an item whose answer is already visible. (iii) This is **not** the L-342 / R-RC shape: D12R's grader refused on **launcher metadata** carrying no physical quantity, whereas this refused on a **file-system fact about a physics artefact, misclassified in the registration** — a registration defect, and registration defects re-register. This family has refused §2d.1 five times, and calling a wrong `ARTEFACTS` list "bookkeeping" would widen L-342 into a general licence to repair any gate that inconveniences a result. (iv) The ordinary path is open and cheap. **The 75.867 core-min is not waste**: it bought a measurement that prices this successor (§4) and it bought this finding.

### 1.2 `D4S-F3S-CAP-DEF-1` — the cap enforced in one time frame and graded in another

Checked because lane G found the same shape on `D6` (`d6_run_arm.sh:347` vs `:376-399`) on 2026-08-27. **It is present in `D4S-F3S` too, and it is present one level up.**

`d4s_f3s_run_arm.sh:394` puts the deadline **inside** the container — `timeout -k 60 $TMO`, `TMO = CAP*60/RANKS = 1800 s` — and `:355`/`:425-426` compute the graded `core_min` from a **host** bracket `T0..T1` that **strictly contains** the container clock:

| term | why it is inside the host bracket and outside the container's `timeout` | bound |
|---|---|---|
| `docker run` client call, container create/start, and the in-container preamble (`source loadDAFoam.sh`, the idwarp import and md5, the echoes) that runs **before** `timeout` begins | `T0` is taken at `:355`, before `docker run` at `:387`; `timeout` starts at `:394` | **measured ≤ 3.3 s** on the predecessor's own `F-S` arm (`T0 ≈ 1787838552` to the first in-container product `d4_major_history.json` at mtime `1787838555.29`); registered at 10 s |
| `timeout -k 60` TERM→KILL escalation | `:394` | 60 s |
| the poll loop's `sleep 10` granularity on `T1` | `:404-420` | 10 s |
| `docker logs` of the arm log + `docker inspect`, both before `T1` | `:421-423`, `T1` at `:425` | 5 s |

**An arm stopped exactly at its own registered deadline therefore records a host wall above 1800 s and trips the grader's own `within_cap` limb (`core_min <= cap`, `d4s_f3s_grade.py:435`) — a `GATE FAIL` manufactured by the measurement frame rather than by the run.** `D4S-F3S` never fired it only because its arms landed at 577 s and 561 s against 1800 s, a 3× margin. **This is reported as a clean structural finding on an item that did not trip it, which is the only honest time to find it.**

**The repair does NOT widen the cap.** The registered cap stays **120.0 core-min exactly** and the ceiling stays **240.0**. What moves is the **enforced deadline, downward**: `TMO = CAP*60/RANKS − FRAME_ALLOWANCE_S = 1800 − 90 = 1710 s`, so the host bracket cannot exceed the cap even when the deadline fires. The assertion inverts and **re-adds** the allowance, so no edit to it can silently widen the cap (§4b).

## 2. WHAT IS INHERITED **BY CITATION**, unchanged

| inherited | source | value (the cited document governs) |
|---|---|---|
| the case, mesh, np, decomposition | `curriculum_D4/PREREGISTRATION.md` §1, §5 | MACH wing CD-min at CL 0.5, 38,304 cells, np=4, `scotch` ×4; the arms inherit their source arm O's `processor*` |
| **band D / E** — the bright line | `curriculum_D4/PREREGISTRATION.md:82`, carried by `D4S-F3S` §2 | **`FD_BAND_PCT` 5.0 per graded component, `AGG_BAND_PCT` 5.0 aggregate, zero sign flips; `PLATEAU_TOL_PCT` 10.0** |
| the five graded components, in order | `curriculum_D4/PREREGISTRATION.md` §6 | `shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV[1]` |
| the stationarity acceptance rule and its four clauses R1–R4 | `D4S-F3S` §3, `d4s_f3s_accept.py` md5 `7377fd5e…` | `END_TIME_REGISTERED` 1000, `WINDOW_ITERS` 200, `MIN_WINDOW_SAMPLES` 3, `STATIONARITY_TOL` 1.0e-3, `CONTINUITY_BOUND` 1.0e-6 — **the file is copied byte-identically, not re-derived** |
| the FD instrument, the step ladder, the disarm read-back | `D4S-F3S` §3.4, `d4s_f3s_fd_endpoint.py` md5 `9ce78caa…` | **byte-identical copy**; `DISARM_TOL_DIFF` 1.0e12 |
| the two toolchain identities by HASH | `curriculum_D4_SHIPPED/PREREGISTRATION.md` §3.1 | SHIPPED `sha256:9d45679d…` / `libidwarp.so` `f0fcb488…`; PATCHED `sha256:2927768a…` / `85f59e87…` |
| L-342 field classes; planted zero; count refusals; positional terminal statement; G5/G6/G6b/G7/G9/G11/G12 | `D4S-F3S` §5 | ported with their bands and thresholds unchanged |
| cpuset, memory, **cap and ceiling** | `D4S-F3S` §4 | **5,6,7,9; 12 g; 120.0 core-min per arm; 240.0 ceiling — UNCHANGED** |
| `P4` cost band | `D4S-F3S` §6 | **[0.8, 1.5] per arm — UNCHANGED** |

**No band, threshold, cap or label in that table is altered here.** The grader asserts this in its own selftest (cases `12f`, `12g`): `FD_BAND_PCT_PER_COMPONENT == 5.0`, `FD_BAND_PCT_AGGREGATE == 5.0`, `PLATEAU_TOL_PCT == 10.0`, the five components in order, `CAPS == {120.0, 120.0}`, `ITEM_CEILING == 240.0`, `P4_BAND == (0.8, 1.5)`.

**Toolchain identity re-verified LIVE at this freeze** (`DAFOAM_CHARTER.md` §6; `TOOLCHAIN_INVENTORY.md` §3's list is stale by its own Amendment A1.2, Amendment 2 at `1f3eef3c`, so the register is not the authority — `docker image inspect` is):

| row | tag | digest read live from the local store 2026-08-27 | registered | `libidwarp.so` md5 |
|---|---|---|---|---|
| SHIPPED | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **MATCH** | `f0fcb488e0e98156575cd19548e91663` |
| PATCHED | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **MATCH** | `85f59e87253e0a71a813f64ca6e4c425` |

**Instrument-drift check on the predecessor, following the addendum trail (not the §7 table alone).** `D4S-F3S/PREREGISTRATION.md` carries **no addenda** — `git log` on that path returns the single freeze commit `8dfb4598` — so its §7 md5 table is current and the trail is empty. All eight entries re-hash equal on disk **and** against the committed blobs (`git show 8dfb4598:<path> | md5sum`). **NO DRIFT. Reported in both directions, as required.**

## 3. WHAT IS NEW — the two repairs, and only those

### 3.1 The repaired age classification (`d4s_f3sr_grade.py`, `d4s_f3sr_stage_arm.sh`, `d4s_f3sr_run_arm.sh`)

Two **complementary and jointly exhaustive** clauses over two **disjoint** registered sets. Every registered file must satisfy exactly one; no file can satisfy both; and the disjointness is **checked first**, before anything is graded.

**(a) `ARTEFACTS` — the age-checked set. FILES THIS ITEM'S OWN RUN PRODUCES, AND ONLY THOSE.** Clause: mtime **strictly newer** than the datum.

| file | produced by | absent from BOTH source `O/` trees? |
|---|---|---|
| `d4_endpoint_dvs.json` | `d4_endpoint_physical.py`, in-container | **yes**, verified from disk |
| `d4_endpoint_dvs_PHYSICAL.json` | `d4_endpoint_physical.py` | **yes** |
| `d4_endpoint_dvs_DRIVERSCALED.json` | `d4_endpoint_physical.py` | **yes** |
| `d4_major_history.json` | `d4_endpoint_physical.py` | **yes** |
| `d4s_f3s_fd_endpoint.json` | `d4s_f3s_fd_endpoint.py` | **yes** |
| `d4s_f3s_fd_endpoint.jsonl` | `d4s_f3s_fd_endpoint.py` | **yes** |
| `d4s_f3s_accept.jsonl` | the stationarity rule inside the FD instrument | **yes** |

Three names are **added** relative to the predecessor (`d4_endpoint_dvs.json`, `d4_endpoint_dvs_DRIVERSCALED.json` — both already on the launcher's `G-COLD` list and both genuine products) and **one is removed** (`OptView.hst`). Removing one and adding three is a **net widening of the age check over products**, not a narrowing.

**(b) `STAGED_INPUTS_EXCLUDED_FROM_AGE` — the exclusions, REGISTERED BY NAME WITH THEIR REASON, in the frozen document and in the frozen grader.** Clause (the **inverse** clause): mtime **not newer** than the datum.

| file | reason registered | how it is gated instead |
|---|---|---|
| `OptView.hst` | staged input: the optimiser history the endpoint is **read from**. Copied with `cp -a` (mtime PRESERVE); this item re-runs no optimiser and never writes it, so an age clause on it is unsatisfiable by construction. | the inverse clause; md5 equality with the source, from the run's own manifest; existence asserted at stage time **and** before launch |
| `opt_IPOPT.txt` | staged input: the optimiser log beside `OptView.hst`, carried by the same `cp -a`. | same |

> **`opt_IPOPT.txt` is a CORRECTION AGAINST THE BRIEF THIS LANE WAS GIVEN.** The brief names `OptView.hst` as the single defect. It is the single *failing* limb — but `opt_IPOPT.txt` is the same kind of file, carried by the same copy into both arms (verified from disk: `F-S` mtime `1787728010` ≤ datum `1787838479`; `F-P` mtime `1787689205` ≤ datum `1787839128`), and it escaped only because the predecessor never listed it anywhere. **An unclassified file is the defect this repair exists to end**, and `d5_run_arm.sh:292-294` refuses on this pair *together*. Registering one and leaving the other unclassified would reproduce the defect in a quieter form.

**Excluding a file from the age clause does NOT leave it unchecked.** The inverse clause is the **positive proof** that the file is an input this item carried in rather than a product it made — exactly the fact the predecessor asserted in prose and never tested. And the exclusions are not taken on the grader's word: `d4s_f3sr_stage_arm.sh` step (h) writes `.d4s_f3sr_staged_inputs.json` into the arm — source path, source md5, staged md5, both mtimes, `produced_by_this_item: false` — and the grader **binds its registered list to that manifest**, refusing on a name mismatch, a datum mismatch, an absent manifest, an absent input, an input newer than the datum, or bytes that are not the ones the stager copied.

### 3.2 The sibling protection the predecessor lacked (`d4s_f3sr_stage_arm.sh`)

The five chain-arm siblings carry this twice; `D4S-F3S` carried it not at all.

| repair | pattern followed | where it lands here |
|---|---|---|
| `rm -f` the staged carry-over of this item's own registered artefacts and the foreign datum | `so1b_run_arm.sh:415`, `av1r_run_arm.sh:331` | step **(d2)**, then **verified**: zero registered products and zero primal captures remain in the copy, else `exit 5` |
| the age reference is **touched LAST** — after the copy, after the `rm`, after the D4-DEF-6 drop — and the datum is read **from it** | `so1b:431/432`, `av1r:352/353`, `d5_run_arm.sh:298/299` | step **(g)** |
| refuse if the optimiser's own products already exist in the work dir | `d5_run_arm.sh:292-294` (`OptView.hst`, `opt_IPOPT.txt`, exit 5) | the launcher's widened `G-COLD`; and D5's *discrimination* is preserved — D5 correctly leaves `OptView.hst` out of its **F** arms' list because there the F arms run inside the O arm's directory where that file must pre-exist, which is the same fact this item's exclusion registers |

> **A REGISTERED DEPARTURE FROM THE SIBLING PATTERN, and it is load-bearing.** The siblings `touch "$WORK/0"/*` and read the datum from `0/U`. **This item may not.** `pyDAFoam` writes the primal end state back into the time-0 directory at run end (`DAFOAM_CHARTER.md` §6), and it was **measured doing so in the predecessor's own arm**: `CURRICULUM-D4S-F3S-a2-wing-cdmin/F-S/processor0/0/U.gz` carries mtime `1787839098`, **619 s after** that arm's staging datum `1787838479`. No OpenFOAM field in this tree is safe as an immutable datum. The reference is therefore a **dedicated sentinel, `.d4s_f3sr_age_ref`**, that nothing in the container writes; its mtime is the datum and is **also frozen into an integer file** so a later rewrite of anything cannot move the recorded datum. The grader refuses if the sentinel is absent or if its mtime disagrees with the frozen integer.

### 3.3 The fixture repair — real staging semantics, and the clause DRIVEN BOTH WAYS

The predecessor's fixture created `OptView.hst` fresh against a datum pinned at epoch `1000000000`. **This fixture stages it.**

1. a real **source tree** is built under `<root>/_src/<arm>/` and its staged inputs are given mtimes **100,000 s before** the datum, as the real sources are (measured: 30.6 h and 41.6 h);
2. the arm directory is staged by a **real `cp -a` subprocess** — not `shutil`, not a fresh write — so the mtime-preserve semantics under test are the ones the stager actually uses;
3. the copy is **verified** to have preserved the source mtime, and that mtime is **verified** to predate the datum, before anything is graded — `FIXTURE_STAGING_EVIDENCE.json`, 4 rows, all `cp_a_preserved: true`;
4. the age reference is created and **touched after** the copy and the datum is read from it, as the stager does;
5. only then are the products written, and they are stamped strictly newer.

**Driven both ways, and the count is 54/54 under `python3` and `python3 -O` with `__pycache__` cleared before each run** (`d4s_f3sr_grade_selftest_evidence.txt`; the two runs' output is identical apart from the mode label):

| direction | case | result |
|---|---|---|
| **PASSES on a fresh product, with the staging semantics real** | `1b` `cp -a` mtime preserved (4/4); `1b` staged `OptView.hst` predates the datum by 100,000 s; `1c` **the predecessor's defect replayed now PASSES**, `n_stale = 0` on both arms; `1c` the exclusions are registered and checked, not silent | OK |
| **REFUSES on a genuinely stale product** | `4` one real product back-dated → `G1` `NOT A RESULT`, `n_stale = 1`, **the stale file NAMED and it is the planted one**, and the staged inputs are **not** counted stale | OK |
| **the inverse clause fires** | `4c` a staged input made newer than the datum → `EXCLUSION_REFUSED` by name | OK |
| **the registration is required** | `4d` absent manifest → refuse; `4e` tampered staged bytes → refuse on md5; `4f` absent age sentinel → refuse; `4g` an absent registered staged input → refuse (excluding a name may never excuse its absence) | OK |
| **the mutation control** | `4h(i)` the **predecessor's list applied to this fixture's own disk state reproduces the defect**: `n_stale = 1`, named `OptView.hst`; the repaired list on the **same** disk state gives `n_stale = 0`. `4h(ii)` putting the name back into `ARTEFACTS` makes the grader **refuse by name** on the fixture that otherwise passes; control restored, the same fixture passes | OK — **the mutation is NOT inert** |

**On inert mutations, reported as the brief requires.** The **first** form of the mutation control written for this file *was* inert as a test even though the guard fired: inserting `OptView.hst` into `ARTEFACTS` tripped the disjointness refusal before the stale count was reached, so the assertion — which demanded `n_stale == 1` — read `MUTATION INERT`. The response was **not** to weaken the assertion. The disjointness check was moved to the **top** of `G1` where a static check on the registered constants belongs, and the control was split into the arithmetic proof `4h(i)` (computed from the fixture's own disk state, which reproduces `n_stale = 1` on `OptView.hst` under the predecessor's exact list) and the guard-fires proof `4h(ii)`. Both fire. **The intermediate reading is disclosed here because a mutation that proves nothing must be reported as proving nothing.**

### 3.4 The cap-frame repair (§1.2), and what it is not

`TMO_REGISTERED_S = 1710`, `FRAME_ALLOWANCE_S = 90`, `KILL_GRACE_S = 60`, all in the launcher and the grader, both asserting `(TMO + FRAME_ALLOWANCE) × RANKS ÷ 60 = 120.000000` — **the registered cap, to six decimals**. Driven live at this freeze (§8, smoke drive 2). The launcher additionally reads the **container's own kernel clock** (`.State.StartedAt` / `.State.FinishedAt`, in the same inspect and **before** the `rm`) into the ledger as `container_wall_s`.

`G10` gains two limbs and **loses none**. `within_cap` is unchanged and unwidened: the **host** bracket must not exceed 120.0 core-min. New: `deadline_frame_pass` (`container_wall_s ≤ 1710 + 60`) and `frame_gap_within_allowance` (`host_wall_s − container_wall_s ≤ 90 − 60 = 30`). **The container clock is BOUND, not printed** — a discrepancy nobody grades is worse than one never computed. If it is `NOT_MEASURED` (L-342 infrastructure: absent → disclosed, present-but-garbage → refuse), `G10` falls back to the host bracket alone, which is the **stricter** reading, so the fallback can never turn a failing cap into a passing one.

**Driven both ways, `12b`–`12e`.** At the repaired deadline: `container_wall_s = 1710`, host wall `1735 s` → `115.667 core-min ≤ 120.0` → `PASS`. **Under the predecessor's deadline the same arm would have recorded `1825 s` → `121.667 core-min > 120.0` → `GATE FAIL` on its own `within_cap` limb.** The selftest asserts the flip and, in the same case, that `CAPS == {120.0, 120.0}` and `ITEM_CEILING == 240.0` **did not move**.

## 4. ARMS, PLACEMENT, COST — every run costed before it runs (rule 12)

| arm | row / image | source of the staged copy (READ-ONLY, on this launcher's FORBIDDEN list) | cap core-min | memory | deadline in-container | predicted core-min |
|---|---|---|---|---|---|---|
| **F-S** | SHIPPED `dafoam/opt-packages:latest` `9d45679d…` | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/O` | 120.0 | 12 g | **1,710 s** | 37.931 |
| **F-P** | PATCHED `dafoam-idwarp-rot:v1` `2927768a…` | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O` | 120.0 | 12 g | **1,710 s** | 37.931 |

**THE ANCHOR IS NAMED, AND IT IS NOT THE ONE THAT MISSED.** `D4S-F3S` §4:78 derived **47.267 core-min/arm from `D4`'s whole F3 ARM TOTAL** (709 s × 4) — an arm total that carries **32.2 s/primal of fixed overhead** — while §4:80's *stated* basis was 22 primals at ~25 s, which predicts 36.667. The arms landed at **38.467** (`F-S`) and **37.400** (`F-P`), i.e. ratios **0.814 / 0.791** against the arm-total anchor (P4 `MISS`) but **1.049 / 1.020** against the stated per-primal basis. **The error was in the ANCHOR, not the rate.**

This item prices from the **two-term decomposition measured on the predecessor's own two arms**, using the FD instrument's own per-primal `wall_s` records:

```
wall_s  =  OVERHEAD_S  +  N_PRIMALS × RATE_S_PER_PRIMAL
F-S     577 s = 114.273 + 22 × 21.033        (Σ per-primal wall 462.727 s, 19.8 % overhead)
F-P     561 s = 115.789 + 22 × 20.237        (Σ per-primal wall 445.211 s, 20.6 % overhead)
pooled  OVERHEAD_S 115.0    RATE_S_PER_PRIMAL 20.635    N_PRIMALS 22    ranks 4
predicted per arm = (115.0 + 22 × 20.635) × 4 ÷ 60 = 568.97 s × 4 ÷ 60 = 37.931 core-min
```

*Artifact for every figure above:* `CURRICULUM-D4S-F3S-a2-wing-cdmin/{F-S,F-P}/d4s_f3s_fd_endpoint.jsonl` (22 `wall_s` rows per arm) and `.../ledger.txt`.

**Point 75.862 core-min = 2 × 37.931; ceiling 240.0 = Σ caps** (unchanged). Dollars **DERIVED** at $0.0513/core-h, **reported-by-owner, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.0649 point, $0.2052 at the ceiling.** Ranks 4, cpuset **5,6,7,9**, H5 floor 16.0 GiB (45 samples / 60 s), aggregate caps + 12 g + host RSS < 30.6 GiB wait-and-retry bounded 14,400 s. Chain order **F-S then F-P**; the chain stops at the first non-zero rc. Runner watch: `cap_core_min_registered = 240.0`.

**CONTENTION IS NOT CLAIMED AS AN EXPLANATION OF ANYTHING.** The predecessor measured delivered cores at **3.9802 / 3.9561 of 4** — contention runs in the *opposite* direction to the underspend and explains none of it. It is recorded, and it is not used.

**Already spent by this registration: 0.000 solver core-min.** The two frozen-instrument smoke drives (§8) created no container and ran no solver; container count on the box was **16 before and 16 after**.

### 4b. The frame allowance, registered

| term | bound | basis |
|---|---|---|
| `docker run` client + container create/start + in-container preamble before `timeout` begins | 10 s | **measured ≤ 3.3 s** on `D4S-F3S`'s `F-S` arm |
| `timeout -k 60` TERM→KILL escalation | 60 s | the flag in the launcher |
| poll-loop `sleep 10` granularity on `T1` | 10 s | the loop in the launcher |
| `docker logs` + `docker inspect` before `T1` | 5 s | 251 KB log, sub-second measured |
| **`FRAME_ALLOWANCE_S`** | **90 s** (bound 85 s) | |

`TMO = 1800 − 90 = 1710 s`. **The cap is 120.0 core-min and does not move.** The launcher refuses if `TMO ≤ 0` and refuses if `(TMO + FRAME_ALLOWANCE_S) × RANKS ÷ 60` differs from the registered cap by more than 0.02 core-min.

## 5. GATES — thresholds by citation, composition stated before compute

| gate | reads | verdict rule |
|---|---|---|
| **G1** per arm (SOLVER) | ledger row (`rc` = kernel `ExitCode`, `OOMKilled`), the arm log's LAST non-empty line, the age datum and its sentinel, the staged-input manifest | `PASS` iff kernel rc 0 ∧ OOM false ∧ `Finalising parallel run` positional ∧ **every registered PRODUCT strictly newer than the datum (0 stale)** ∧ **every registered STAGED INPUT present, md5-bound and not newer than the datum**; harness/kernel disagreement → REFUSE; the two registered sets overlapping → REFUSE **first**; absent sentinel / absent manifest / manifest-name mismatch / manifest-datum mismatch / staged input newer / staged bytes not the copied bytes → REFUSE |
| **G-ACC** per arm | the per-primal captures, `d4s_f3s_accept.jsonl`, the `disarm` record, the FD file's `n_primals`, the log's `Running Primal Solver` count | `PASS` iff every capture re-evaluates ACCEPTED ∧ every instrument record agrees ∧ disarm read-back = 1e12; count disagreement → REFUSE; zero captures → REFUSE |
| **G5** per row — THE BRIGHT LINE | `d4s_f3s_fd_endpoint.json` | count refusal first (5 registered components in order); `PASS` iff aggregate ≤ 5 % ∧ every component ≤ 5 % ∧ 0 sign flips ∧ 0 without plateau (≤ 10 %); `NOT A RESULT` if 0 graded; else `GATE FAIL` |
| G6 / G6b / G7 per row | the FD file on disk | plant 1.234e-03 into `d_hi`, re-read through the same reader, all three channels must move and the source md5 must not; a blind reader must be REFUSED; empty / short / reordered / key-absent must each be refused by NAME |
| **G9** per row + distinct | the `D4S_IDWARP_SO_MD5:` line of the arm's log, the ledger's digest | F-S must carry `f0fcb488…` + `9d45679d…`, F-P `85f59e87…` + `2927768a…`; the two md5s must differ |
| **G10** | ledger caps vs registered, Σ ≤ 240.0, **and the container's own kernel clock** | `PASS` iff `cap_core_min == enforced_core_min == 120.0` ∧ `core_min ≤ 120.0` (host bracket, **unwidened**) ∧ — when `container_wall_s` is measured — `container_wall_s ≤ 1710 + 60` ∧ `host_wall_s − container_wall_s ≤ 30` ∧ the ledger's `frame_allowance_s == 90`; `NOT_MEASURED` → the frame limbs are disclosed as such and the gate rests on the host bracket alone (the stricter reading); else `GATE FAIL` (reports; never absorbs) |
| G11 | `OOMKilled` | any true → `NOT A RESULT` |
| G12 | `d4_placement_rank*.json` (4 files, count refusal), ledger cpuset, delivered mean (`NOT_MEASURED` tolerated, ≥ 3.0 if present) | `PASS` iff affinity ⊆ {5,6,7,9}, distinct single cores, cpuset as registered |
| **ITEM** | the above | `NOT A RESULT` if any arm fails G1 or G-ACC, any control fails, any OOM, or any row's G5 is `NOT A RESULT`; else **`PASS` iff both rows' G5 `PASS`; else `GATE FAIL`** (a two-row divergence is a finding, D4-SHIPPED §5) |

L-342: absent INFRASTRUCTURE fields (`memavail_*`, `delivered`, `siblings_*`, `container_wall_s`, `frame_allowance_s`) → `NOT_MEASURED`, disclosed, the grade proceeds; present-but-garbage → REFUSE; absent PHYSICS field → REFUSE. No GCI (no grid family; rule 5 has no row). **Grader selftest 54/54 under `python3` and `python3 -O`, `__pycache__` cleared before each, output identical apart from the mode label** (`d4s_f3sr_grade_selftest_evidence.txt`). `ast.Assert` **0** in the grader, **0** in the acceptance rule and **0** in the FD instrument, with the counter shown counting a **planted** assert (case `0_ast_counter_sees_planted_assert`).

## 6. PREDICTIONS — scored HIT / MISS / UNSCORED by the grader, never adjusted

| id | prediction | falsifier |
|---|---|---|
| **P1** *(inherited)* | both arms: every primal of the sweep (22 each) is ACCEPTED under the stationarity rule, and both FD tables exist | any primal rejected, or a `REFUSE` by the reader, on either row |
| **P2** *(inherited)* | SHIPPED row G5 = `GATE FAIL` with `shape[18]` outside band D or sign-flipped | **P2 MISSES if the SHIPPED row is 5/5 inside band D** — and that MISS is the finding that the IDWarp rotation defect does not reach the endpoint gradient on this case, recorded, never averaged with a HIT |
| **P3** *(inherited)* | PATCHED row reproduces `curriculum_D4` §11.3 to the printed digits (≤ 1e-12 relative on `J_adj` and `d_hi`) | any component off by > 1e-12 relative |
| **P4** *(inherited, band UNCHANGED)* | cost ratio actual/predicted per arm in **[0.8, 1.5]** | either arm outside |
| **P5** *(NEW, STRICTLY TIGHTER)* | cost ratio actual/predicted per arm in **[0.90, 1.15]** against the two-term anchor of §4 | either arm outside. **Registered as new and tighter than P4, derived from a measurement this lane has already read; it can only turn a HIT into a MISS.** |
| **P6** *(NEW)* | **both rows reproduce `D4S-F3S`'s own FD tables to ≤ 1e-12 relative** on every graded component's `J_adj` and `d_hi` | any component off by more — which would be a reproducibility finding about this box and these images, recorded as such |
| **P7** *(NEW — THE REPAIR'S OWN FALSIFIER)* | **`G1`'s age clause is satisfiable on both arms**: `n_stale = 0`, `inverse_clause_pass` true, exactly 2 registered staged inputs excluded and each verified not-newer-than-datum and md5-bound | any stale product, any staged input failing the inverse clause, or a count other than 2. **A MISS here says the repair did not work and the item is `NOT A RESULT` again — this is the prediction the item exists to test.** |

**What each outcome means, registered now.** If P7 HITS and both rows' G5 PASS, the item is **`PASS`** and D4's optimum-endpoint gradient becomes toolchain-independent on this case. If P2 HITS the item is `GATE FAIL` on the SHIPPED row and that two-row divergence is the reportable finding. If P6 HITS, **this item's numbers ARE the predecessor's numbers** — see §9, which says plainly what that does and does not buy.

## 7. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT — and the diffs for the supervisor's check 1

| file | md5 | ancestor / diff to read |
|---|---|---|
| `d4s_f3sr_stage_arm.sh` | `39a01c8d76d3cd27285ff1fb754bf12b` | `d4s_f3sr_stage_arm_DELTAS_from_d4s_f3s.diff` (271 lines) from `d4s_f3s_stage_arm.sh` `f0d0dd36…`; carries repairs (1) sibling `rm -f`, (2) touch-last age reference, (3) staged-input manifest; `bash -n` clean; **driven** at this freeze and refused with `rc=5` because the registered run root is ABSENT (§8) |
| `d4s_f3sr_run_arm.sh` | `ae13edeae807be82269de2fa5c5dc488` | `d4s_f3sr_run_arm_DELTAS_from_d4s_f3s.diff` (252) from `d4s_f3s_run_arm.sh` `d65da2e0…`; the cap-frame repair, the widened `G-COLD`, the pre-launch inverse clause, the container kernel clock; `bash -n` clean; **0 backticks on executable lines**; **driven** at this freeze to `rc=4` with the CAP FRAME assertion printed and **no container created** (§8) |
| `d4s_f3sr_grade.py` | `9596c7bf711a934313a9b4d5801481c6` | `d4s_f3sr_grade_DELTAS_from_d4s_f3s.diff` (829) from `d4s_f3s_grade.py` `2ed0651c…`; selftest **54/54** plain and `-O`; `ast.Assert` 0 |
| `d4s_f3sr_chain_driver.sh` | `05f2aed77b1f58edbeb41a11e943805b` | `d4s_f3sr_chain_driver_DELTAS_from_d4s_f3s.diff` (109) from `d4s_f3s_chain_driver.sh` `da74cd11…`; **adds an md5 assertion on the STAGER before every arm** — the predecessor asserted only the launcher and the grader, and the age repair lives in the stager; `bash -n` clean |
| `d4s_f3s_accept.py` | `7377fd5e1eb0a558c2d38fc8da125fc2` | **BYTE-IDENTICAL** to `D4S-F3S`'s at `8dfb4598`. The acceptance rule is untouched by either repair. |
| `d4s_f3s_fd_endpoint.py` | `9ce78caab9c46d13398ee1d0643cf982` | **BYTE-IDENTICAL** to `D4S-F3S`'s at `8dfb4598`. Same output names, so this item's FD numbers are directly comparable to the predecessor's (P6). |
| `d4s_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | byte-identical to D4-SHIPPED's and D4S-F3S's |
| `d4s_f3sr_instruments.md5` | `ba8d916ba6e2cfecaf9cf5c0fd3f6289` | the two staged instruments, asserted by the stager in the case dir and in the root, and by the launcher before every arm |

## 8. FREEZE

**Condition, named and checked:** `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3SR-a2-wing-cdmin` **must be ABSENT.** Checked three ways at 2026-08-27T21:53Z: by `ls` (no such file or directory); by **executing the frozen stager**, which refused with `rc=5` and the message *"run root … absent — the chain driver creates it"*; and by **executing the frozen launcher**, which passed `G-ROOT.1`, `G-ROOT.2`, `G-ROOT.3`, `G-ROOT.5` and the cap-frame assertion and then refused at the `L-251` mode check with `rc=4` because the directory does not exist. **Container count on the box: 16 before, 16 after. No container created, none signalled, none removed. 0 solver core-min spent by this registration.**

*Operational note, not a gate:* the launcher's `D4_HOST_PRE` line read `MemAvailable_GiB=11.06` during that drive, **below** the chain driver's registered H5 floor of 16.0 GiB, because another item's arm is live on the box. The driver's H5 window would refuse this item today, correctly. That is a scheduling fact for the supervisor, not a defect.

**Guard placement, verified by line number in `d4s_f3sr_run_arm.sh`** — every guard precedes every destructive step and the first `docker run`:

`G-ROOT.1` 96 · `G-ROOT.2` 126 · `G-ROOT.3` 141, 149 · `G-ROOT.5` 225, 241 · cap-frame assertion 279 · `D4S_CAP_FRAME` 281 · `D4_CAP_ASSERT` 282 · `L-251` root mode 291 · staged-instrument md5s 294–297 · image digest 307 · `G-ROW` 315 · age sentinel + manifest 336–339 · inverse clause `D4S_STAGED_INPUTS_OK` 352 · root instrument md5s 353–354 · widened `G-COLD` 362–366 → **first `docker run` at 464.** **This launcher contains no `rm -rf` at all** — the stager owns staging and refuses an existing destination — so there is no destructive host step for a guard to precede other than the container launch itself. In the stager, the destructive steps are the `rm -f` at (d2) and the `rm -rf` of arm-O time dirs at (f); both are preceded by `G-ROOT.1`/`G-ROOT.2`, the source-exists and destination-absent checks (a), the answer-file and staged-input-presence assertions (b), and the mesh assertions (c).

The grading path is `d4s_f3sr_grade.py` at the md5 above, asserted by the driver before it runs and **to be hashed against this commit's blob before any grade is believed**. After first compute gates are closed; changes land only as dated addenda that cannot alter a gate, threshold, cap or label.

**Launch path of record:** the queue runner — a `verification/queue/dafoam/D4S_F3SR_chain.json` whose `prereg_commit` is the sha of **this commit and no addendum**, argv `bash <case dir>/d4s_f3sr_chain_driver.sh F-S F-P`, `cap_core_min_registered 240.0`, validated by `scripts/queue_entry_check.py`. The draft entry sits beside this file as `queue_entry_D4S_F3SR_DRAFT.json` and **is not enqueued**: the freeze sha goes to the supervisor first, and **enqueueing is not authorisation** — `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own.

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

**Said first and plainly, because it is the honest limit of the repair.** If P6 HITS, **this item's FD numbers ARE `D4S-F3S`'s numbers** — same case, same sources, same images, same byte-identical instruments, same 22 primals. **What the successor buys is a GRADEABLE VERDICT, not a new measurement.** It converts a table that already exists and cannot be graded into one that can, and it does so by re-registering the classification rather than by moving a gate. That is worth 75.9 core-min and it is not worth more than that; a reader who wants a *new* measurement of this gradient must change the case, the mesh, the np or the toolchain, and this item changes none of them.

Nothing about arm O (both optimisations are cited as graded/recorded: PATCHED `Optimal Solution Found` 80 majors; SHIPPED `Maximum Number of Iterations Exceeded` 100 majors, `inf_pr` 6.59e-05 — D4-SHIPPED RESULTS §7); nothing about a mesh other than D4's; no GCI; nothing at another np, decomposition, image or primal tolerance; nothing about the 91 `shape` components not in the table; nothing about physical accuracy against experiment. The FD and the adjoint share the primal and are wrong together where it is wrong (`V_STANDARD_FD_VS_ADJOINT.md` §13 item 12).

**Nothing here establishes that the cap-frame defect is confined to `D4S-F3S` and `D6`.** Two items have been checked and both carry it. **The class question is open and is named as open**; this item repairs its own instance and does not claim the sweep.
