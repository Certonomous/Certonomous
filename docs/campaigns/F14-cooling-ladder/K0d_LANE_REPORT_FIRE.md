# K0d FIRE LANE REPORT — THE RUNG DID NOT FIRE, ON TWO INDEPENDENT STOPS

**Verdict: `BLOCKED`.** Zero core-minutes spent. Nothing was built, meshed,
launched or graded. `verification/runs/F14-cooling-ladder/K0d_runs/` **still does
not exist**, verified in this lane's own invocation under a planted control
(§2.1). **`AMENDMENT 2` WAS NOT WRITTEN** — §1 says why, and the reason is that
writing it would have required this lane to choose one of two numbers the
supervisor's ruling did not authorise it to choose between.

Written 2026-08-25T19:07Z by the heat-transfer lane dispatched to implement the
supervisor's four-part ruling and then fire. **Both stops were pre-committed by
the supervisor in the dispatching brief itself** — ruling part 2 ("if 12.00 does
not reproduce from the document, report the discrepancy and STOP; do not adjust
it to fit") and gate (a) ("If `build_k0d.py` or `analyse_k0d.py` is absent or
differs from its registered hash, STOP and report — do not write or repair a
comparator to make the fire possible"). **This lane exercised neither escape.**

**The two stops are independent.** Repairing either one alone still leaves the
other standing.

---

## 1. STOP 1 — THE `12.00` INSTRUMENTATION FIGURE DOES NOT REPRODUCE. THE DOCUMENT'S OWN RULE GIVES `11.50`.

### 1.1 The enumeration, taken from the frozen document and not from this lane

`K0d_REREGISTRATION.md` `AMENDMENT 1` §A1.4 (lines 806–812) enumerates the
instrument lines. Every figure below is the document's, quoted from that table:

| instrument line | registered value | source line |
| --- | ---: | --- |
| meshing + `checkMesh`, 5 core-s per case | 0.83 at ten cases, **bounded ≤ 2.00** | §A1.4 row 2 |
| `check_k0d_mesh.py`, three `polyMesh` reads | 0.50 (explicitly unchanged) | §A1.4 row 3 |
| `mark_done_k0d.py` + `analyse_k0d.py` + `--selftest` | 1.00 | §A1.4 row 4 |
| dual-scheme extraction (new, §A1.3b) | **≤ 8.00** | §A1.4 row 5 |

- **POINT instruments** = 0.83 + 0.50 + 1.00 + 8.00 = **10.33**
- **BOUNDED instruments** = 2.00 + 0.50 + 1.00 + 8.00 = **11.50**

**Neither is 12.00.**

### 1.2 The enumeration rule is the DOCUMENT'S rule, not this lane's reading — and that is demonstrated, not asserted

The obvious objection is that this lane has invented a way of adding the lines up.
It has not, and the frozen document contains its own control for exactly this.

§8's pre-amendment ceiling registers **"instruments, bounded | 3.50"** (line 425)
against a POINT instrument total of **2.25** (line 418, "meshing 0.75, mesh reader
0.50, comparators 1.00"). Applying the rule used above to the nine-case lines —
**meshing taken at its ≤ 2.00 bound, the other two lines unbounded** — gives
`2.00 + 0.50 + 1.00 =` **3.50**, which is the registered figure **exactly**.

**The rule reproduces the document's own prior bounded instrument figure to the
cent.** That is what makes `11.50` the document's answer at ten cases and `12.00`
an unsourced one. The gap is **+0.50 core-min**, and the only line that could
carry it — `check_k0d_mesh.py` at 0.50 — is the one line §A1.4 marks
**"unchanged"**, with a stated reason (`M1_m_seed` reuses L2's mesh).

### 1.3 What this lane did NOT do

**It did not adjust 12.00 to 11.50 and proceed**, and it did not proceed on 12.00
either. Both were available and both were refused:

- Substituting 11.50 would re-choose the supervisor's own ruled ceiling number.
  The ruling's part 1 **is** the figure 2,749.14; a lane that silently re-derives
  it to 2,748.64 has widened its own authority over the one quantity the ruling
  consisted of (standing rule 9 — *approval of an item is approval of ITS cap*).
- Proceeding on 12.00 would register a ceiling whose instrument component cannot
  be derived from the registration it claims to derive from. **On a rung whose
  stated purpose is to eliminate numbers chosen for comfort**, a 0.50 core-min
  unsourced addend is not too small to matter — it is the same defect at a size
  chosen for comfort, which is the reasoning §A1.1 already recorded against the
  `T_ref` alternative at 0.050 %.

### 1.4 All four arrangements, re-costed at every instrument figure, so the ruling can be re-made from arithmetic in one round trip

`S = 912.38`. Registered cap **2,484.84**. Structure `CEILING = 3S + I`.

| I | CEILING | vs cap | core-h | derived $ at $0.0513/core-h |
| ---: | ---: | ---: | ---: | ---: |
| **12.00** (the ruling's figure, **unsourced**) | 2 749.14 | +264.30 (+10.64 %) | 45.8190 | $2.3505 |
| **11.50** (the document's bounded rule) | **2 748.64** | **+263.80 (+10.62 %)** | 45.8107 | **$2.3501** |
| 10.33 (the document's POINT rule) | 2 747.47 | +262.63 (+10.57 %) | 45.7912 | $2.3491 |

**The choice between them moves the ceiling by 1.67 core-min out of ~2,748 —
0.061 %.** It changes no conclusion: every arrangement still exceeds the
registered cap by ~10.6 %, the derived cost stays ~$2.35, and that stays **9.4 %
of the $25 pre-authorisation**. **The supervisor's parts 1, 3 and 4 are
unaffected in substance.** What is affected is whether the number the amendment
registers is one a reader can re-derive from the document, and that is the whole
evidentiary content of a frozen figure.

**The other two arrangements the ruling refused are NOT re-costed here** and are
not offered as options: part 2 of the ruling refused both concessions, this lane
agrees with the reasoning, and re-tabling a refused lever is how a refusal gets
quietly reopened.

---

## 2. STOP 2 — GATE (a) FAILS AT THE FLOOR: `build_k0d.py` AND `analyse_k0d.py` DO NOT EXIST. NOWHERE.

### 2.1 Measured, under a planted control (standing rule 3)

The reader was shown able to return PRESENT before any ABSENT was believed. In
one invocation, `test -e` over seven paths returned:

| path | reader |
| --- | --- |
| `scripts/check_grader_self_blindness.py` | **PRESENT** — the plant |
| `verification/runs/F14-cooling-ladder/K0cS_runs` | **PRESENT** — the plant |
| `scripts/build_k0d.py` | **ABSENT** |
| `scripts/analyse_k0d.py` | **ABSENT** |
| `scripts/mark_done_k0d.py` | **ABSENT** |
| `scripts/check_k0d_mesh.py` | **ABSENT** |
| `verification/runs/F14-cooling-ladder/K0d_runs` | **ABSENT** |

A second reader — `find /home/ubuntu -xdev` over all four script names **plus the
plant name** — returned **the plant and nothing else**. A reader that finds the
plant and no `build_k0d*` anywhere under `/home/ubuntu` is a reader shown able to
see a non-zero.

**Third reader, independent of the disk:** `git ls-tree -r HEAD` (HEAD
`c90f9411`) over the whole tree, filtered on `k0d`, returns **seven `.md` files
and not one `.py`**. The scripts are not in HEAD, not in the working tree, and
not on the filesystem.

### 2.2 There is no "registered hash" to compare against, because the artifact was never written

§7.5 of `K0d_REREGISTRATION.md` (line 384) registers the grading path as
`check_k0d_mesh.py` → solve → `mark_done_k0d.py` → `analyse_k0d.py`, and binds
that **"every comparator is hashed against its committed blob before analysis
(Charter 2d); the grading path is fixed at this document's commit."**

**No blob was ever committed for any of the four.** The gate the supervisor set
— *absent, or differs from its registered hash* — fails on the **first** limb,
which is the more serious one: a hash mismatch is a drift to investigate, an
absence is a path that was registered and never built.

**This lane did not write them.** The brief forbids it — *"do not write or repair
a comparator to make the fire possible"* — and standing rule 2 is the deeper
reason: a comparator written by the lane that is under instruction to fire, after
the registration is frozen, is a grading path chosen with the run in view.

### 2.3 Consequence for gates (c) and (d)

Both are **untestable, not passed and not failed**:

- **(c)** the ten-marker refusal per §A1.2b cannot be exercised on a grader that
  does not exist. **Recorded as a live obligation on whoever writes it**: §7.5
  line 386 still reads **"all nine"**, and only §A1.2b (line 747) moves it to
  **ten**. A comparator author reading §7 alone would build the nine-marker
  refusal and be wrong.
- **(d)** the `ranks == 1` assertion has no launcher to sit in. The **conversion
  arithmetic** was checked against §8.1's frozen table instead — see §4.

---

## 3. THE STOPS ARE NOT THE ONLY REASON THE FULL RUNG COULD NOT HAVE FIRED TODAY

Reported because the supervisor asked for contention to be **re-read at fire
time and disclosed, not ignored** — and it has moved materially against the
registration.

**Measured 2026-08-25T19:07Z:** 16 cores; `loadavg` **9.97 / 9.28 / 9.34**;
`MemAvailable` **18 823 244 kB = 17.95 GiB**.

**Foreign processes at ≥ 99 % CPU — SEVEN, not the five §9.1 registered:**

| identity | pids | cores |
| --- | --- | ---: |
| T-family `buoyantBoussinesqSimpleFoam` | 2203927, 2203944, 2203947 | 3 |
| dafoam `d4_opt_runScript.py` IPOPT drivers | 2359929, 2359930, 2359931, 2359932 | 4 |
| **total sustained** | | **7** |

plus transient ansys-verification work (`locate_bad_faces.py`, pid 2422906,
observed at 308 % — bursty, not counted as sustained).

**§9.1 registered `5 + 9 = 14` of 16.** The live figure is **`7 + 10 = 17` of
16 — over subscription.** At the supervisor's ~14/16 instruction the largest
K0d batch that seats is **14 − 7 = 7 cases**, so the ten-case rung **could not
have launched whole today** even with the amendment written and the comparators
present. Under the brief that is a "launch the largest batch that fits and say
so" case, not a silent shrink — **but it is moot, because nothing launched.**

**Memory (gate f) is NOT the constraint:** 17.95 GiB available against §9.2's
~2.15 GiB conservative bound for all ten and this family's standing 12 GiB floor.
§9.2's own drop-to-seven trigger (`MemAvailable` under 14 GiB) **is not tripped**.

**No contention file was written**, because a contention file records a launch
and there was no launch.

---

## 4. EVERY GATE, WITH ITS MEASURED VALUE

| gate | what it required | measured | status |
| --- | --- | --- | --- |
| **ruling pt 1** | `K0d_runs` absent, proved by `test -e` under a planted control | **ABSENT**; plants `K0cS_runs` and `check_grader_self_blindness.py` both PRESENT | **PASS** — the pre-compute window of rule 2 is genuinely still open |
| **ruling pt 2** | `12.00` reproduces from §A1.4/§10.2 | **DOES NOT.** Document's rule gives **11.50** bounded / 10.33 point; rule validated by reproducing the frozen 3.50 exactly | **GATE FAIL → STOP 1** |
| **ruling pt 3** | `M1_m_seed` stays L2, stays in the rung | not altered by this lane | upheld, untouched |
| **ruling pt 4** | derived cost, `[lab-attributed]`, referral | arithmetic verified: 2 749.14/60 = 45.8190 core-h × $0.0513 = **$2.3505 DERIVED**, 9.40 % of $25 | arithmetic **PASS**; not written, blocked by STOP 1 |
| **(a)** | frozen build/grade scripts hash against committed blobs | **`build_k0d.py`, `analyse_k0d.py`, `mark_done_k0d.py`, `check_k0d_mesh.py` ALL ABSENT** on disk, in HEAD, and under `/home/ubuntu` | **GATE FAIL → STOP 2** |
| **(b)** | `check_grader_self_blindness.py` over `analyse_k0d.py` | tool's **`--selftest` PASSES** (both probes shown able to fire on planted defects and stay quiet on clean counterparts, **rc = 0**); on the target it **exits rc = 1, `FileNotFoundError`** | **untestable** — no grader to scan |
| **(c)** | grader refuses (exit 2) below TEN `DONE.<case>` | no grader exists | **untestable** |
| **(d)** | `timeout = cap × 60 ÷ ranks`, `ranks == 1` asserted in the launcher | no launcher exists. §8.1's frozen table re-derived: 3 of 4 rows exact, **one row off by 1 s** (see below) | **untestable**; one observation |
| **(e)** | contention re-read and disclosed | load **9.97**; **7** sustained foreign cores, not 5; `7 + 10 = 17 > 16` | **disclosed** — §3 |
| **(f)** | memory re-read | **17.95 GiB** available; §9.2 trigger not tripped | **PASS** |
| **(g)** | detached `setsid` launch | **NOT REACHED — nothing launched** | n/a |

**Gate (d) observation, reported and not repaired.** With `ranks = 1` the
conversion is the identity `× 60`. Against §8.1's frozen table:
`M1_c`/`M2_c` 435.00 → 26 100 s **exact**; `M1_f`/`M2_f` 1 675.50 → 100 530 s
**exact**; `C_lam` 639.50 → 38 370 s **exact**; `M1_m`/`M2_m`/`B_hi`/`I_hi`
852.70 → **51 162 s**, where the document registers **51 161 s** — **1 second
low, 0.002 %**. It is a rounding artefact, it binds *tighter* than the rule so it
cannot license an overrun, and **it is left exactly as frozen.** Recorded here
because a lane that checks a conversion and mentions only the rows that matched
has not checked it.

---

## 5. WHAT THIS LANE DID NOT DO — each stated explicitly

- **`AMENDMENT 2` was NOT appended.** `K0d_REREGISTRATION.md` is **byte-unchanged**
  at blob `36b302f1`, still version 1.1, still ending at `A1.8`.
- **No comparator was written or repaired**, though writing one was the only way
  to make the fire possible.
- **No cap was raised.** 2,484.84 core-min stands as the registered cap. The
  ceiling was **not** moved to 2,749.14 or to anything else.
- **Nothing was launched.** No case directory, no mesh, no solver, no pid, no
  contention file. **Zero core-minutes.** Rule 12's estimate-versus-actual
  calibration is **not triggered** — no process completed, so there is nothing to
  calibrate, and `docs/COST_CALIBRATION.md` was not touched.
- **Findings 10 and 11 were not re-ruled** — closed by §A1.2b and §A1.3b
  respectively, and cited as closed.
- **`K0d_PREREGISTRATION.md` was not touched**; blob `e629f5c4` unchanged.
- **`docs/LAB_STATE.md`, `docs/DOCKET.md` and `docs/LESSONS.md` were not touched**,
  no id was assigned or reserved, and `scripts/append_record.py` was not used.
- **Nothing was sent** (standing rule 7). Submissions remain **PARKED**.

---

## 6. VERDICT AND WHAT IS NEEDED

**`BLOCKED`** — on two independent stops, both pre-committed by the supervisor in
the dispatching brief, neither of which a lane may clear:

1. **The `12.00` instrumentation figure is unsourced**; the document's own rule
   gives **11.50**. Re-ruling the figure is the supervisor's, and §1.4 costs
   every candidate so it can be done from arithmetic. **It changes no
   conclusion** — the overrun stays ~10.6 %, the derived cost stays ~$2.35.
2. **The entire registered grading path does not exist.** Four scripts, zero
   blobs. Until `build_k0d.py`, `check_k0d_mesh.py`, `mark_done_k0d.py` and
   `analyse_k0d.py` are written, committed and frozen, **K0d has no path to a
   completed run, let alone a graded one**, and no cap decision changes that.

**Stop 2 is the larger finding and it reorders the work.** The cap ruling was
being made for a rung that has no comparator. **A comparator author must be
dispatched before a cap is raised** — and the §2.3 nine-versus-ten marker trap is
handed to them here rather than left to be discovered.

*Written by a heat-transfer lane, 2026-08-25. Zero compute. Nothing fired.*
