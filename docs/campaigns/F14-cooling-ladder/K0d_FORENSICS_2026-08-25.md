# K0d FORENSICS — 2026-08-25, after two lanes died at a session limit ~20:45Z

**Author:** heat-transfer lane, on the supervisor's forensics brief.
**Compute:** zero core-minutes. No solver was fired, no case directory created,
no frozen file edited. `verification/runs/F14-cooling-ladder/K0d_runs` re-checked
**ABSENT** in this session, under a planted control in which the same reader
returned **PRESENT** on `verification/runs/F14-cooling-ladder/K0cS_runs`
(standing rule 3 — a zero from a reader not shown able to see a non-zero is not
evidence).

**Baseline HEAD for every comparison below: `ed726454`** (2026-08-25T20:47:34Z).

---

## 1. HEADLINE — the dying lane's last words were WRONG on one point, and its work SURVIVED

The second dead lane's final message said the board at `docs/LAB_STATE.md:2427`
carries `2 749.14` and that it was about to draft `AMENDMENT 2`.

**Both halves need correcting, and in the lab's favour:**

| the dying claim | what disk says |
| --- | --- |
| "`docs/LAB_STATE.md:2427` carries `2 749.14`" | **REFUTED.** Line 2427 at HEAD reads *"has not earned.** Audit dispatched; it costs zero core-minutes."* — it is a sentence about the thermal reference title-page audit and carries **no cap figure at all**. The nearest board cap line is **2438**, and it already reads **`2 748.64`**. |
| "Drafting AMENDMENT 2" | **IT LANDED.** `AMENDMENT 2` was **committed at `802418fc`, 2026-08-25T20:43:01Z** — roughly two minutes before the lane died. It is at HEAD, byte-identical in the worktree. **Nothing of AMENDMENT 2 was lost.** |

**There is therefore no board-versus-brief conflict to reconcile.** The board's
current entry and the brief agree on **2 748.64**; the three board lines that
still show `2 749.14` (2583, 2590, 2653) are **older entries further down a
reverse-chronological board**, and lines 2192, 2256 and 2368 explicitly record
2 748.64 as superseding them.

---

## 2. WHICH DOCUMENT IS OPERATIVE — this reframes everything else

**`K0d_PREREGISTRATION.md` IS SUPERSEDED. `K0d_REREGISTRATION.md` GOVERNS.**

`K0d_REREGISTRATION.md` line 3 states it on its face: it supersedes
`K0d_PREREGISTRATION.md` (blob `e629f5c4…`, 3 759 lines, v1.5 with AMENDMENT 1–5).
The reason, from its own §0 and from `K0d_FIRE_RULING_2026-08-25.md` §1:
**AMENDMENT 1 §A1.2 and AMENDMENT 5 §A5.7 reconciled the SAME 2.7539 % `Ra`
inconsistency two mutually exclusive ways** — `ν → 1.569e-5` versus
`β → 3.26577e-3` — and a contradiction between two frozen repairs is not a gap a
sixth amendment fills. Superseded, not deleted; the old file and all five
amendments stay byte-unchanged under rule 6.

**Consequence for the cap question, and it is the one genuine trap here:** the
superseded pre-registration's §10.3 still reads **`REGISTERED CEILING / TOTAL CAP
2 484.84`**, and all five of its amendments say *"No CAP moved."* **The raise to
2 748.64 exists ONLY in the re-registration.** Anyone reading the cap out of
`K0d_PREREGISTRATION.md` will read a superseded number.

---

## 3. EVERY K0d FILE, WITH ITS TRUE STATE

All eight are **tracked at HEAD**. The index is decayed and disagrees with both.

| absolute path | worktree vs HEAD | index vs HEAD |
| --- | --- | --- |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_PREREGISTRATION.md` | **MATCH** | **`M` — STAGED AT 986 LINES vs 3 759 AT HEAD** |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md` | **MATCH** | staged `D` (deletion) |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md` | **MATCH** | staged `D` |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_PREFLIGHT_EXECUTABILITY_FINDING.md` | **MATCH** | staged `D` |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_PREFLIGHT_SMOKE_TEST.md` | **MATCH** | staged `D` |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION_PHASE1_FINDINGS.md` | **MATCH** | staged `D` |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_TURBULENT_MIXED_CONVECTION_GATE.md` | **MATCH** | clean |
| `/home/ubuntu/Certonomous/docs/campaigns/F14-cooling-ladder/K0d_LANE_REPORT_FIRE.md` | **DIFFERS — worktree 476 lines vs HEAD 262** | staged `D` |

**THE INDEX DECAY IS CONFIRMED AND MEASURED.** The index stages
`K0d_PREREGISTRATION.md` at **986 lines against 3 759 at HEAD — 2 773 lines
short**, exactly the figure the brief warned of. It also stages **six K0d files
for deletion** while every one of them sits on disk byte-identical to HEAD. **A
bare `git commit` from this tree would delete six K0d records and truncate the
superseded pre-registration by 2 773 lines**, destroying AMENDMENT 1–5 of a
frozen document. Nothing in this session touched the shared index.

**Nothing K0d-related is untracked-and-new** except three scripts (§6) and this
file.

### 3a. The one piece of genuinely orphaned work

`K0d_LANE_REPORT_FIRE.md` carries **214 uncommitted lines (263–476)** in the
worktree: a `PHASE 1 REPORT — 2026-08-25T19:24Z` from the lane that wrote the
builder scripts. It is **superseded in substance but not worthless** — its central
recommendation was *"fold the four `build_k0d.py` gaps into `AMENDMENT 2`
alongside the ceiling correction"*, and **AMENDMENT 2 did exactly that** (§A2.1a–d).
It also records the three scripts' `--selftest` counts and a disclosed grading
reading. **Supervisor's call whether to land it; this lane did not commit it**,
because it is another lane's report and amending another lane's record is not
this lane's to do.

---

## 4. AMENDMENTS — WHICH EXIST, WHERE, AND WHETHER COMMITTED

**Two documents each carry their own amendment series. They must not be confused.**

### Superseded `K0d_PREREGISTRATION.md` (v1.5) — all five COMMITTED at HEAD

| # | line | date | version | commit |
| --- | ---: | --- | --- | --- |
| AMENDMENT 1 | 990 | 2026-08-24 | 1.0 → 1.1 | committed |
| AMENDMENT 2 | 1278 | 2026-08-25 | 1.1 → 1.2 | committed |
| AMENDMENT 3 | 1413 | 2026-08-25 | 1.2 → 1.3 | `361adbbe` 16:34:26Z |
| AMENDMENT 4 | 1958 | 2026-08-25 | 1.3 → 1.4 | `232cc532` 16:46:46Z |
| AMENDMENT 5 | 2607 | 2026-08-25 | 1.4 → 1.5 | `1799861d` 17:09:28Z |

All are pre-compute, all carry the rule-6 `lines whose number changed above this
section: 0` assertion. **All are now inert — the document they amend is superseded.**

### Operative `K0d_REREGISTRATION.md` (v1.2) — both COMMITTED at HEAD

| # | line | date | version | commit |
| --- | ---: | --- | --- | --- |
| AMENDMENT 1 | 641 | 2026-08-25 | 1.0 → 1.1 | `a2451872` 18:31:37Z |
| **AMENDMENT 2** | **933** | **2026-08-25** | **1.1 → 1.2** | **`802418fc` 20:43:01Z** |

### THE PLAIN STATEMENT THE BRIEF ASKED FOR

**`AMENDMENT 2` EXISTS AT HEAD — in BOTH documents.** In the operative
`K0d_REREGISTRATION.md` it is the ceiling correction the dying lane was drafting,
and it is **committed, not merely in the worktree**. **Nothing is uncommitted or
missing.**

**AMENDMENT 2 (re-registration) rule-6 and rule-2 compliance, verified from the
file:** version bump stated (1.1 → 1.2); the `lines whose number changed above
this section: 0` assertion present at line 935 and **stated as verified rather
than typed** — the first 929 lines were compared byte-for-byte against the v1.1
committed blob; the rule-2 pre-compute condition stated **and** checked by naming
the absent run directory at 20:39:05Z **under its own planted control** on
`K0cS_runs`. Its §A2.6 states what it did not move. **This one is clean.**

---

## 5. THE TWO CAP FIGURES — EVERY HIT, AND WHAT THE 0.50 IS

All figures are **core-minutes** unless the line itself derives dollars.

### The arithmetic, from `K0d_REREGISTRATION.md` §A2.2a–A2.2b

`CEILING = 3S + I`, with solver subtotal `S = 912.38` after `M1_m_seed`'s 85.27 line.

| `I` | ceiling | status |
| ---: | ---: | --- |
| **11.50** | **2 748.64** | **REGISTERED, CURRENT** |
| 12.00 | 2 749.14 | **SUPERSEDED** |
| — | 2 484.84 | **SUPERSEDED** — the v1.0 §8 cap |

**THE 0.50 IS ATTRIBUTED, AND THE DOCUMENTS SAY SO EXPLICITLY.** §A2.2a
enumerates the instruments: meshing 2.00 + `check_k0d_mesh.py` 0.50 +
`mark_done_k0d.py`/`analyse_k0d.py`/`--selftest` 1.00 + dual-scheme extraction
≤ 8.00 = **`I` = 11.50**. The check that this is the right enumeration: the first
three sum to **3.50**, reproducing the frozen §8 `instruments, bounded | 3.50`
line term by term. **The `12.00` in §A1.4's arrangement table is not reproducible
from §A1.4's own enumeration — `3.50 + 8.00 = 11.50`, and the remaining 0.50 is
recorded as UNEXPLAINED, with no line accounting for it.**

**So the 0.50 is not a disagreement between two derivations. It is an
unattributable residue in the earlier figure, which is why 2 749.14 was
superseded rather than defended** — and it is recorded as superseded with its
reason, not deleted (§A2.2b, `K0d_REREGISTRATION.md:1139`).

Derived dollars at the owner-reported $0.0513/core-h, **DERIVED, NOT MEASURED**
(the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5):
2 748.64 / 60 = 45.8107 core-h = **$2.3501**, 9.40 % of the $25 pre-authorisation.
POINT 922.71 core-min = **$0.789**; POINT/CEILING = **33.57 %**.

### Every occurrence, swept across `docs/` and `verification/`

**`docs/LAB_STATE.md`** — 2192 (the ruling: 2 748.64, 2 749.14 recorded superseded),
2256 (`I` = 11.50 → 2 748.64), 2368 (corrected ceiling), **2438** (desk item,
**2 748.64**), 2481 (taken off desk, 2 748.64), 2583 (older: re-costed 2 749.14),
2590 (older: raised to 2 749.14), 2653 (older desk item, 2 749.14).

**`docs/campaigns/F14-cooling-ladder/K0d_REREGISTRATION.md`** — 836 (arrangement
table, 2 749.14), 958–959 (raise to 2 748.64, 2 749.14 superseded), 1133
(arithmetic), 1138–1139 (status table), 1148 (derived dollars), 1162 (33.57 %),
1367 (legal only because no compute has run).

**`docs/campaigns/F14-cooling-ladder/K0d_LANE_REPORT_FIRE.md`** — 65–66 (the
authority argument: the ruling's part 1 *is* 2 749.14 and a lane silently
re-deriving it to 2 748.64 has widened its own authority), 81–82 (both rows),
201, 229. **This is the uncommitted-tail file; lines 65–229 are at HEAD.**

**THREE FALSE POSITIVES, named so nobody re-finds them as cap figures:**
`verification/runs/ansys_verification/VMFL045/R2/L3_360x304/0.0069997885/p:28964`
(`102749.1431`, a pressure value), `verification/runs/F4_runs/swbli_cylflare/
step0_instrumented/5.2e-05/omega:6078` (`2749.14892`, an omega value), and
`verification/runs/F14-cooling-ladder/K0cG_runs/.attempt1_stale/S_SST_x/
log.solve:142602` (`ExecutionTime = 2748.64 s` — **wall seconds of an unrelated
stale K0cG solve, a coincidence and not a cap**).

**`docs/LAB_STATE.md` is byte-identical between worktree and HEAD.**

---

## 6. HASH-VERIFY OF THE FROZEN FILES — the rule-2 freeze check

| file | worktree sha1 | HEAD blob | verdict |
| --- | --- | --- | --- |
| `K0d_PREREGISTRATION.md` (superseded) | `e629f5c4…` | `e629f5c4…` | **MATCH** |
| `K0d_REREGISTRATION.md` (**operative**) | `27a29bdd…` | `27a29bdd…` | **MATCH** |
| **the grading / comparator script** | — | — | **CANNOT BE HASHED — IT DOES NOT EXIST** |

### THE COMPARATOR DOES NOT EXIST, AND THIS IS THE FIRE-GATING FINDING

**`analyse_k0d.py` IS NOT ON DISK ANYWHERE**, tracked or untracked. A `find`
across the repository for `*analyse_k0d*` and `*analyze_k0d*` returned nothing.
**The grep was planted:** the identical pattern class run against the sibling
`verification/runs/T-family/T3_runs/analyse_t3.py` returned **15 hits**, so the
reader was shown able to see a non-zero before its zero on K0d was believed.

The three K0d scripts that **do** exist are all **untracked** (`??`):

| path | bytes | mtime |
| --- | ---: | --- |
| `/home/ubuntu/Certonomous/scripts/build_k0d.py` | 43 465 | 2026-08-25 20:46 |
| `/home/ubuntu/Certonomous/scripts/check_k0d_mesh.py` | 34 007 | 2026-08-25 20:45 |
| `/home/ubuntu/Certonomous/scripts/mark_done_k0d.py` | 21 005 | 2026-08-25 19:18 |

**None of the three is committed, so none can be hash-frozen against a blob.**
Rule 2 fixes the grading path at the pre-registration commit and requires the
frozen file to be hashed against the committed blob before grading; §9 of the
superseded document (line 633) registers that `analyse_k0d.py` is *"hashed
against its committed blob"* before analysis. **That check cannot be performed
on a file that was never written, and the two builder scripts cannot be
verified-as-run against blobs that do not exist.**

**`build_k0d.py` and `check_k0d_mesh.py` have mtimes AFTER AMENDMENT 2's
20:43:01Z commit** — they were being edited to consume the four gap rulings when
the lane died, and that editing is **uncommitted and unverified**. Their
`REGISTRATION_GAPS` table now names the AMENDMENT 2 values (`writeFormat ascii`
§A2.1a, `writePrecision 16` §A2.1b, `writeCompression off` §A2.1c,
`domain_thickness_t 0.010 m` §A2.1d), so the builder's exit-2 refusal appears to
have been cleared — **but this lane did NOT execute `build_k0d.py` to confirm
it, deliberately: running it writes the nine cases and would CREATE
`K0d_runs/`, destroying the pre-compute absence proof that §A2.0 and every
amendment's legality rest on.** Grep only.

---

## 7. K0d §0 — BLAY 1992 `NOT OBTAINED`, AND WHAT VERDICT IS REACHABLE

The re-registration puts it in its own §0 heading, *"THIS DOCUMENT STATES ITS OWN
CEILING, ON ITS FACE"*:

> **AS REGISTERED, THIS RUNG CANNOT REACH A GRADED VERDICT.** The primary —
> Blay, D., Mergui, S. and Niculae, C. (1992) — is **`NOT OBTAINED`**. Every
> graded row of the superseded §7.3 is `BLOCKED` by construction under its §7.4
> order 4 until a reference addendum arms §7.6, and the rung's tally stands at
> **0 of 10**. What firing this rung produces is the **solves and the
> physics-stage instruments** — convergence, achieved `y⁺`, the five guards, the
> Roache triples, the discrimination control — **not a gate.** Nobody may later
> read a completed run of this rung as a graded result.

The superseded §2 records the sourcing check as a fact: `find docs/papers` for
blay/mergui/niculae returned **nothing**, `find /home/ubuntu` returned
**nothing**, and `grep -ril 'blay' docs/papers/` returned **fifteen files, every
one a secondary**. No DOI exists (ASME HTD volumes of that era are unregistered);
venue metadata corroborated only by CiNii record CRID 1573105974176827520.

**What it does NOT block**, per the same section: the mesh ladder, the
iterative-convergence measurement, the heat-balance guard, the three
discrimination arms (`C_lam`, `B_hi`, `I_hi`), the wall-resolution report and the
cost science.

**The reachable verdict on firing today is `BLOCKED` on every graded row —
`0 of 10` — with the fine value, the Roache triple, the GCI and the achieved
`y⁺` printed as `REPORTED` information.** Today, unfired, the rung's state is
`PENDING` (the §9 display/queue state, explicitly *not* a softened `GATE FAIL`).

### The pre-registered gate, as frozen

- **Deviation.** `REL(q) = 100·|q_solve − q_ref| / |q_ref|` where the quantity
  does not cross zero; **absolute** `ABS(q) = |q_solve − q_ref|` where it does —
  every velocity row here. Taken on the **fine level**, gated by §8.
- **Band conversion rule**, registered instead of the answer:
  `BAND(r) = ± max( 2·u_val(r) , R(r)·S(r) )`, `u_val = sqrt(u_exp² + u_dig²)`.
  It works today because the scales are **boundary conditions**, not solution
  values: `ΔT_band = 20.0 K`, `U_in = 0.57 m/s`, `H = 1.04 m`.
  **`max`, not `min`** — a band tighter than the instrument that measured the
  reference grades measurement noise. **The addendum can only ever WIDEN a band,
  and only through a property of the reference.**
- **ANTI-WIDENING GUARD:** if `2·u_val(r) > 3·R(r)·S(r)`, that row is
  **REPORTED, not GRADED** — so an addendum arming a large `u_exp` cannot turn
  the gate into a formality everything passes.
- **Eleven registered profile stations**, fixed: `0.05, 0.10, 0.20, 0.30, 0.40,
  0.50, 0.60, 0.70, 0.80, 0.90, 0.95`. A row passes only if **every** station
  with a reference lies inside the band; missing stations are named `UNMEASURED`
  and **the denominator shrinks with them printed — never silently renormalised**.

**Thresholds, all ten graded rows:**

| row | quantity | scale | R | **BAND, absolute** |
| --- | --- | --- | ---: | --- |
| G1 | mean `Θ`, vertical mid-plane `x/H = 0.5` | `DT` | 0.05 | **± 1.00 K** |
| G2 | mean `Θ`, horizontal mid-plane `y/H = 0.5` | `DT` | 0.05 | **± 1.00 K** |
| G3 | mean `u` on `x/H = 0.5` | `UIN` | 0.10 | **± 0.0570 m/s** |
| G4 | mean `v` on `y/H = 0.5` | `UIN` | 0.10 | **± 0.0570 m/s** |
| G5a | ceiling wall-jet peak speed | `UIN` | 0.10 | **± 0.0570 m/s** |
| G5b | wall-normal location of that peak | `HGT` | 0.02 | **± 0.0208 m** |
| G6 | floor-averaged `Nu_floor` | `REF` | 0.10 | **± 10 % of `\|q_ref\|`** — the only band awaiting the reference |
| G7 | stratification `Θ(0.75) − Θ(0.25)` | `DT` | 0.05 | **± 1.00 K** |
| G8 | jet penetration length to `0.5 U_in` | `HGT` | 0.10 | **± 0.104 m** |
| S1 | global circulation structure | — | — | **EXACT MATCH, no band** |

Plus two **reported, never graded**: R1 (TKE) and M0 (the Boussinesq model-form
floor, ≈ 1.65 % on velocity and ≈ 0.031 % on Nusselt — **printed beside every
velocity row and G6 and NEVER subtracted from a deviation**).

**Verdict ladder, and the order is part of the freeze:** (1) any level NOT
CONVERGED → `NOT A RESULT`; (2) grid triple not `CONVERGING` → `NOT A RESULT`
with the fine value, both triples and both observed orders printed; (3) outside
the registered `y⁺` window or a failed guard → `NOT A RESULT` or REPORTED per the
guard's own clause; (4) **no primary on disk → `BLOCKED`**; (5) primary held →
`PASS` inside the band else `GATE FAIL`.

### Cap, label, cost, occupancy

- **CAP: `2 748.64` core-min** (re-registration §A2.2b — **the operative
  figure**). Superseded: `2 749.14` and `2 484.84`. **Reaching the cap STOPS the
  run; an overrun does not get a new budget.**
- **PER-CASE HARD STOP: 10× that case's registered POINT line**, converted to an
  enforced `timeout = cap_core_min × 60 ÷ ranks`, with **`ranks = 1` asserted,
  not assumed**.
- **Expected core-minutes — POINT: `922.71`** (solver subtotal `S = 912.38` plus
  instruments; up from 829.36 after `M1_m_seed`'s 85.27 line, +11.26 %).
  POINT/CEILING = **33.57 %**. POINT rate `2.549e-6` s per cell-iteration;
  CEILING rate `2 × POINT`.
- **Derived dollars, DERIVED NOT MEASURED:** POINT 15.379 core-h = **$0.789**;
  CEILING 45.819 core-h = **$2.351** (9.40 % of $25). **The authorisation is not
  the binding constraint; the cap is.**
- **LABEL: `BLOCKED`** on every graded row while the primary is unheld; **`0 of
  10`**; resolution class of the re-registration itself `[lab-attributed]` under
  Sanaa's desk-item disposal rule (`LAB_STATE.md:1880`), adopted by silence.
- **REGISTERED EXPECTED CPU OCCUPANCY: `62 %`** — the brief's expected figure,
  **CONFIRMED**. `K0d_REREGISTRATION.md:551–552`: mean K0d occupancy over its own
  critical path is `827.11 / 167.55 = 4.94` cores; with the five cores already
  busy that is **`(4.94 + 5)/16 = 62 %`, BELOW Sanaa's 80–90 % target**.
  Independently at `K0d_REREGISTRATION_PHASE1_FINDINGS.md:334`.

---

## 8. GRADER SELF-BLINDNESS CHECK — task 6

`scripts/check_grader_self_blindness.py` takes file paths (`[--selftest] [files ...]`).

**The tool's own planted control was run FIRST**, so its zeros mean something:

> `SELFTEST PASSED: each probe was shown able to FIRE on a planted defect and
> able to STAY QUIET on its clean counterpart.` — **exit 0**, four planted cases,
> both probes shown able to fire and to stay quiet.

**Run against the K0d comparator: IMPOSSIBLE — `analyse_k0d.py` does not exist.**
Run instead against the three K0d scripts that do:

> `scripts/mark_done_k0d.py: clean on both probes (NOT a proof of correctness)`
> `scripts/build_k0d.py: clean on both probes (NOT a proof of correctness)`
> `scripts/check_k0d_mesh.py: clean on both probes (NOT a proof of correctness)`
> — **exit 0**

**The tool's own words are the right caveat and are not softened here: "NOT a
proof of correctness." Two static probes passing is not a graded comparator, and
the graded comparator is the file that is missing.**

---

## 9. PLANTED-ZERO CONTROL AND THE STRICT COMPLETION RULE — task 7

### Registered (superseded `K0d_PREREGISTRATION.md` §8.1, lines 515–536) — three plants

| # | plant | into | refusal |
| --- | --- | --- | --- |
| P1 | `PLANT_T = 1.234e-03` K | a **copy** of `M1_f/<endTime>/T`, **by line index, never by regex over the value** | **exit 2** if the production reader does not see it |
| P2 | `PLANT_U = 1.234e-03` m/s, x-component | a copy of `M1_f/<endTime>/U` | **exit 2** — registered separately because six of ten graded rows are velocity rows and a scalar plant does not exercise the vector parser |
| P3 | **negative control**, exactly `0.0` | a copy of `M1_f/<endTime>/T` | reader must report NOT DISTINGUISHABLE FROM BACKGROUND; **if P3 fires, the control is broken and the comparator exits 2** |

Standing consequence: **a graded row returning exactly zero is `NOT A RESULT`
unless P1/P2 demonstrated on the same reader in the same invocation that a
non-zero is visible. A zero is a result only when it is a supported zero.**
*"The comparator refuses (exit 2) rather than degrades, on every clause."*

### IMPLEMENTED — item by item, with line numbers

| item | where it must live | present? |
| --- | --- | --- |
| `PLANT` / `plant_into` in the **comparator** | `analyse_k0d.py` | **ABSENT — THE FILE DOES NOT EXIST.** P1, P2 and P3 are **all three unimplemented.** |
| `PLANT` / `plant_into` in `mark_done_k0d.py` | — | **0 hits** (correctly — not its job) |
| `PLANT` / `plant_into` in `build_k0d.py` | — | **0 hits** |
| `PLANT` / `plant_into` in `check_k0d_mesh.py` | — | **5 hits — PRESENT** |
| *control:* same pattern on `analyse_t3.py` | — | **15 hits** — grep proven able to see a non-zero |

**Strict completion rule and the age guard — PRESENT and correctly written, in
`/home/ubuntu/Certonomous/scripts/mark_done_k0d.py`:**

| clause | line(s) |
| --- | ---: |
| clause 3 — last written time == `endTime` | 13, 246 |
| clause 4 — fields present at `endTime`, **PER CLOSURE** via `PER_CLOSURE_FIELDS`, never a single tuple | 15 |
| clause 5 — `ExecutionTime` line count == `endTime` | 16, 253 |
| **clause 6 — THE AGE GUARD: every field at `endTime` NEWER than the case's own `0/T`, because `0/T` is touched LAST at launch** | **17–19, 266, 272** |
| `endTime` read from `system/controlDict`, refusal if absent | 142, 234, 236 |
| refusal if no `0/T` — *"the run's start cannot be dated and the age guard cannot run"* | 266 |
| **exit-2 refusal path** (`sys.exit(EXIT_REFUSE)`) | **91** |
| its own planted fixtures for clauses 3, 5 and 6 | 360–363, 408–411 |

**So the reader half of the instrument is built and the grader half is not.**

---

## 10. WHAT THIS LANE COULD NOT VERIFY — stated plainly

1. **That `build_k0d.py` now runs.** Its `REGISTRATION_GAPS` table names the
   AMENDMENT 2 values, but **it was not executed**, deliberately: running it
   creates `K0d_runs/` and destroys the pre-compute absence proof every
   amendment's legality rests on. Whether the refusal is genuinely cleared is
   **unverified**.
2. **The three scripts' `--selftest` counts** (560/32, 448/29, 396/15) are quoted
   from the **uncommitted** tail of `K0d_LANE_REPORT_FIRE.md`. **This lane did
   not re-run them**; they are another lane's claim, not this lane's measurement.
3. **Whether the mtime-after-20:43 edits to `build_k0d.py` and
   `check_k0d_mesh.py` are complete or were cut off mid-edit.** Both are
   uncommitted; a lane died two minutes after the later mtime.
4. **The rule-6 assertions of the five superseded amendments** were read as
   present, **not** re-verified byte-for-byte against their parent blobs. Only
   AMENDMENT 2 of the re-registration states its own verification, and that
   statement was read, not independently reproduced.
5. **No comparator diff was read as a diff** — there is no comparator. The
   supervisor's undelegatable §3 check on the K0d comparator **cannot be
   performed and must not be recorded as performed.**

---

## 11. VERDICT

**`BLOCKED` — and on a different blocker than the fire ruling named.**

`K0d_FIRE_RULING_2026-08-25.md` blocked the rung on the over-determined `Ra`.
**That blocker is CLEARED**: the re-registration settled `ν = 1.569e-5`,
`β = 1/298`, `Ra = 2.135970e9` derived-and-reported, and AMENDMENT 2 §A2.5
explicitly corrects the standing `BLOCKED`-on-`Ra` claim elsewhere in the repo.

**The rung is now blocked on two things this forensics found instead:**

1. **`analyse_k0d.py` DOES NOT EXIST.** No comparator means no planted-zero
   control (all three plants unimplemented), no Roache triple gating in code, no
   hash-freeze against a committed blob, and no diff for the supervisor's
   undelegatable read. **Rule 2's grading path cannot be fixed at a commit that
   has no file.**
2. **All three existing K0d scripts are UNTRACKED**, so none can be
   hash-verified against a blob, and two carry uncommitted post-AMENDMENT-2 edits
   of unknown completeness.

**Cost of this forensics: zero core-minutes.** No solver, no case directory, no
frozen file edited, no shared index touched.

**Note for whoever commits next: the shared index would delete six K0d records
and truncate the superseded pre-registration by 2 773 lines. Use the
private-index protocol; this file was committed that way and named only itself.**

*Forensics by a heat-transfer lane, 2026-08-25, against HEAD `ed726454`.
Zero compute. Nothing sent — submissions remain PARKED (standing rule 7).*

---

# ADDENDUM — 2026-08-25, LATER THE SAME DAY: THE MISSING HALF OF THE INSTRUMENT IS BUILT

**Author:** the same heat-transfer lane, on the supervisor's ruling that K0d
does not fire on RIGOR (not cost) while `analyse_k0d.py` does not exist.
**Compute: zero core-minutes.** No solver fired. `build_k0d.py` was **not**
pointed at the registered run tree.
`verification/runs/F14-cooling-ladder/K0d_runs` **re-checked ABSENT after every
step of this work**, including after each selftest.

**This addendum records forensics and construction. It assigns no verdict to the
rung — that is the supervisor's, after the personal diff read.**

## A1. WHAT WAS BUILT

| script | path | lines | `--selftest` |
| --- | --- | ---: | --- |
| **`analyse_k0d.py`** | `/home/ubuntu/Certonomous/scripts/analyse_k0d.py` | **1 751** | **PASSED, 68 checks** |
| `build_k0d.py` | `/home/ubuntu/Certonomous/scripts/build_k0d.py` | 985 | **PASSED, 39 checks** |
| `check_k0d_mesh.py` | `/home/ubuntu/Certonomous/scripts/check_k0d_mesh.py` | 770 | **PASSED, 41 checks** |
| `mark_done_k0d.py` | `/home/ubuntu/Certonomous/scripts/mark_done_k0d.py` | 396 | **PASSED, 15 checks** |

`scripts/check_grader_self_blindness.py` over all four: **exit 0**, each
*"clean on both probes (NOT a proof of correctness)"* — the tool's own caveat,
carried unsoftened. Its own `--selftest` was run first (exit 0) so its clean
verdicts are not unplanted zeros.

## A2. THE THREE REGISTERED PLANTS, AND THE CHANNEL THEY PLANT INTO

Implemented as `K0d_REREGISTRATION.md` §7.4 adopts them from the superseded
§8.1 — **not to this lane's own design.**

| plant | line | what it does | refusal |
| --- | ---: | --- | ---: |
| **P1** | `run_planted_controls` at **382** | `PLANT_T = 1.234e-03` K (**110**) into a **copy** of `M1_f/<endTime>/T` **by line index** (`plant_into_scalar_copy`, **346**), read back through the production scalar reader (**301**) | exit 2 at **407** |
| **P2** | same call | `PLANT_U = 1.234e-03` m/s (**111**) into the **x-component** of a copy of `M1_f/<endTime>/U` (`plant_into_vector_copy`, **366**), read back through the production **vector** reader (**321**) | exit 2 at **422** |
| **P3** | same call | the **negative control**, `0.0` (**112**), which must read back **NOT DISTINGUISHABLE FROM THE BACKGROUND** | exit 2 at **450** if it fires |

**THE CHANNEL IS THE POINT.** Each plant writes into a **field file on disk** and
is read back through **the same reader that produces the graded number** — not
into a spec, a dict or a constants table. That is why the comparator performs
its own extraction from mesh + fields rather than reading `.xy` files written by
a separate utility: if the graded number came from a file some other program
wrote, a plant into the field would exercise a reader the graded path never
calls, which is the `AMENDMENT 2` §A2.3 defect one layer up. **The reading is
disclosed in the module docstring and flagged for the diff read**; it introduces
no free parameter, since every extraction number (`cellPoint`/`cell`, 2081
points, 5.000e-04 m, the two mid-plane lines) is registered in §A1.3a.

**Proved, not asserted:** the selftest plants into a field holding **twelve
identical values** and asserts **exactly one** changed — a plant by regex over
the value would have hit all twelve.

**The standing consequence** (`zero_is_supported`, **465**): a graded row
returning **exactly zero** is `NOT A RESULT` unless P1/P2 demonstrated a
non-zero **on the same reader in the same invocation**.

## A3. ROACHE TRIPLE GATING, IN THE STANDING-RULE-5 ORDER

`classify_triple` **658**, `observed_order` **679** (the **unequal-ratio**
fixed point, `r21 = 1.400000` vs `r32 = 1.401786` — this rung does not pretend
they are equal), `gci_fine` **708** at `Fs = 1.25`, `roache` **721**.

**A GCI IS NEVER QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE, and that is
enforced in `roache()` at line 729 — not left to the caller.** The selftest
recovers a **planted `p = 2.0` to within 1e-3** from the fixed point.

The ladder is `row_verdict` (**967**) and runs in the registered order: level
not converged → triple not `CONVERGING` → guard/`y⁺` → no primary → band.
**The direction of the gate is enforced by `gate_is_monotone` (962) and proved
by the selftest**: `PASS`/`GATE FAIL` may become `NOT A RESULT`; **`NOT A
RESULT` may never become `PASS` or `GATE FAIL`, and `BLOCKED` may never become
`PASS`.**

A **profile row takes the most severe of its thirteen station triples** — a
single `DIVERGENT` station makes the row `NOT A RESULT`. That **tightens and
cannot loosen**, and is disclosed as a reading.

## A4. THE SELFTEST WOULD ACTUALLY FAIL — TEN MUTATIONS, TEN CAUGHT

A green selftest that exercises the wrong channel is worse than none (the K0d
condition-C lesson). So the selftest was **mutation-tested**: ten defects were
injected one at a time into a copy and the selftest re-run.

**All ten were CAUGHT (`SELFTEST FAILED`):** P1 refusal removed; P2 refusal
removed; P3 negative-control refusal removed; the `DIVERGENT` branch disabled;
GCI quoted on non-monotone triples; station `0.25` dropped (back to eleven);
the ten-marker refusal removed; the ordering assertion removed; band
widening/anti-widening disabled; the unsupported-zero rule removed.
`__pycache__` was cleared first — a stale one inverts mutation tests.

68 checks, each a positive that must stay quiet **and** a negative that must
fire, including: nine-of-ten markers refused; a field/mesh length mismatch
refused; a **compressed** field refused (§A2.1a/§A2.1c register ascii and
`writeCompression off`); a missing `endTime−4000` checkpoint reported NOT
CONVERGED rather than assumed converged.

## A5. CONDITION C — ALREADY REPAIRED IN THE WORKTREE, AND VERIFIED HERE

The supervisor's brief described `condition_C(None, LEVELS[lo], None,
LEVELS[hi])`. **That is the HEAD form. The uncommitted worktree copy already
carried the repair**, written by the lane that died at 20:45Z. It was
**verified, not assumed**:

`block_cells_from_mesh` (**225**) counts each block from the mesh with the same
`_count_between` helper condition B uses; `condition_C` (**239**) **raises rather
than falling back to `LEVELS` when a mesh is missing** (**251**) — the fallback
*was* the defect; `condition_C_spec` (**271**) keeps the registered-table check
**labelled as not a check on the mesh**; `synthetic_mesh` (**387**) grows a
`redistribute` plant that moves cells out of block B.

**The assertion that proves the hole is closed fires:** *"REPAIRED CONDITION C
REFUSES a 20-cell block redistribution THAT A AND B BOTH LET THROUGH"*, with A
and B both shown quiet on the same synthetic mesh, and the control confirmed to
genuinely under-resolve block B (38 752 vs 43 232 cells). All six §A2.3c repair
items are satisfied, including item 5 — a single-level invocation says condition
C was not evaluated.

## A6. A LIVE DEFECT FOUND IN `build_k0d.py`, AND IT NEARLY COST THE ABSENCE PROOF

**`build_k0d.py --selftest` was FAILING one check when this work began.** The
diagnosis matters more than the fix:

**1. The check was STALE.** It asserted the builder refuses because a
registration gap is unresolved. `AMENDMENT 2` §A2.1a–d **resolved all four
gaps** (`writeFormat ascii`, `writePrecision 16`, `writeCompression off`,
`domain_thickness_t 0.010 m`), so that refusal no longer fires. **A check that
can no longer pass is not a check.**

**2. The check was DANGEROUS, and this is the finding.** It invoked the **real
builder** against a **real fixed path**, `/tmp/should_never_be_written`, and
asserted nothing was written there. **With the gaps closed the builder DID write
there — all ten case directories, measured and then removed.**

> **HAD THAT FIXED PATH BEEN THE REGISTERED RUN TREE, THE SELFTEST ITSELF WOULD
> HAVE CREATED `K0d_runs/` AND DESTROYED THE PRE-COMPUTE ABSENCE PROOF THAT
> EVERY AMENDMENT'S LEGALITY RESTS ON.**

**The repair** (`gap_tmp` probe, **826**), in the same shape as the §A2.3
lesson — **plant into the real channel, never into a spec**: a copy of the
script is written with **one gap re-opened to `None`** and *that copy* is run, so
the refusal produced is the real refusal path on the real code. Every root is a
**fresh tempdir**; **no fixed path is passed as `--root` anywhere in the
selftest**, and that is itself asserted (**874**).

A **positive counterpart** was added: with all four gaps closed the builder
**does** build into a tempdir — which is what proves the refusal check is a
control and not a tautology, **and it is the measurement that answers the
question the forensics left open: `build_k0d.py`'s refusal IS cleared.**

**One mistake made here is recorded rather than smoothed over** (**845**): the
first version of this probe appended the mutation to the end of the file, *after*
`sys.exit(main())`, where it never executed — the probe reported a pass while
proving nothing. It is now injected before the `__main__` block, and the
injection point is asserted.

**The stale success banner was also corrected** (**969**). It claimed *"main()
REFUSES while any registration gap is unresolved"*, which is no longer true.
**An instrument may not assert something false about itself** (§A2.3c item 4).
It now states plainly that **given `--root`, the script writes ten case
directories**, and must not be pointed at the registered run tree before the
fire order.

## A7. WHAT THIS LANE COULD NOT VERIFY

1. **No K0d field has ever been read.** Every reader, plant, guard and triple in
   `analyse_k0d.py` was exercised against **synthetic** fields and meshes built
   by its own selftest. **Nothing here is evidence about the real rung**, only
   about the instrument.
2. **The extraction reading is a reading.** §A1.3a's `setFormat raw` names
   OpenFOAM `sample` parameters; this comparator implements the registered
   semantics itself, for the reason in §A2. **If the supervisor rules that the
   graded number must come from `postProcess`, the plants must move with it** —
   and this lane does not amend a frozen registration to suit its own code.
3. **`build_k0d.py` was never pointed at the registered run tree**, so that it
   produces a *correct* case there is unverified — only that it no longer
   refuses, and that it writes into a tempdir.
4. **`analyse_k0d.py` has never been hashed against a committed blob**, because
   until this commit there was none. It prints its own blob sha1 and accepts
   `--expect-sha` so the freeze check becomes possible from the output.
5. **The supervisor's §3 check-1 diff read has NOT been performed** and is not
   recorded as performed. It is undelegatable and is the supervisor's.

## A8. STATUS

**`PENDING`** — the instrument is built and green; the rung has not run and this
lane assigns it no verdict. The blockers this forensics named in §11 are
addressed: `analyse_k0d.py` now exists, and all four scripts are committed in
one commit so the freeze binds on a true assertion rather than on a registration
naming a grading path that does not exist.

**The fire order remains the supervisor's, after the personal diff read.**

*Addendum by a heat-transfer lane, 2026-08-25. Zero core-minutes. Nothing sent —
submissions remain PARKED (standing rule 7).*
