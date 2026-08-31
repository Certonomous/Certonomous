# T19b — successor to T19: the same rung, the same gates, with `residualControl` removed from the CASE so the registered experiment can actually happen

> **STATUS: DRAFT. FROZEN BY THE COMMIT THAT FIRST LANDS IT.** Not enqueued.
> Nothing is built, launched, marked or graded under this document until the
> heat-transfer supervisor has read both successor instruments as diffs
> (`SUPERVISION_CHARTER.md` §3 check 1) and discharged check 4 personally. The
> lane that wrote this drafted only: it launched no solver, enqueued nothing,
> committed nothing, and edited no frozen file.
>
> **THIS DOCUMENT MOVES NO GATE, NO THRESHOLD, NO BAND, NO FLOOR, NO CAP AND NO
> LABEL.** §2 enumerates every one of them and shows how each is carried over —
> not re-typed, but **loaded at grading time from T19's own frozen
> `T19_registered.json` by explicit path under a sha256 pin**. **No
> `VERIFICATION_CHARTER.md` §2d.1 grant is sought and none is needed**, on
> verification's own ruling at `998dc230`,
> `docs/DEAD_LEVER_AUDIT.md` §21.2: *"No gate, threshold, cap or label moves;
> rule 2 is satisfied without a §2d.1 grant, and none is sought."*
>
> **ZERO FROZEN BYTES CHANGE.** `build_t19.py`, `analyse_t19.py`,
> `exact_t19.py`, `mark_done_t19.py`, `run_one_t19.sh` and
> `T19_registered.json` are byte-identical to their HEAD blobs and stay that way
> — verified in §1 by hash, not asserted. The repair lives in two **new** files
> or nowhere.
>
> **SUBMISSIONS REMAIN PARKED** (rule 7). Nothing here has been or may be sent,
> filed, uploaded, registered, posted or commented outside this box.

Drafted 2026-08-31 by a heat-transfer `lab-lane` on the supervisor's freeze-ahead
brief, under Sanaa's 2026-08-28 directive 3. **Every number below was re-derived
by this lane from the artifact named beside it**; the brief's own figures were
re-measured rather than transcribed, and §9 boards the one place this lane's
measurement goes beyond what the brief and the ruling stated. Repository HEAD at
drafting: `c4fadb215f8749739516c2d5a633c3b7ae31476b` (HEAD moved during drafting
— `d910023e` → `c4fadb21` — as peers committed; the §1 hashes were taken at both
and reproduce).

**PROVENANCE TAGGING IS BINDING THROUGHOUT.** Every number carries one of
MEASURED / DERIVED / EXTRAPOLATED / REGISTERED / REPORTED-BY-OWNER / BORROWED /
ASSUMED / TRANSCRIBED, with its unit and referent. A compound number carries its
weakest input's tag. **The `BORROWED` tag is the whole moral of this rung** and
is used precisely below: T19 died of an unlabelled borrow.

---

## 0. Why T19b exists — one unguarded borrow and one tautological green

### 0.1 The defect that killed the rung: a load-bearing assumption stated, sourced, and never guarded

T19's registration declined an absolute residual gate on an explicit written
ground, and cited its evidence:

> *"T1c ran this solver for these 30 000 iterations and the solver's own
> `residualControl` never tripped on any of the six cases"* —
> `docs/campaigns/T-family/T19_PREREGISTRATION.md`, citing `build_t1c.py:57-63`.

**That fact was BORROWED from T1c and never measured on T19.** On T19 it is
false, on both cases that ran. Measured by this lane from the solvers' own logs,
not taken from the relay:

| case | converged at | `endTime` | `End` | `ExecutionTime` lines | time dirs on disk | artifact |
|---|---:|---:|:--:|---:|---|---|
| `P_q_c` | **828 iterations** [MEASURED, iterations] | **30 000** [REGISTERED] | 1 | **828** | `0`, `0.orig`, `828` | `verification/runs/T-family/T19_runs/P_q_c/log.solve:7521`; `P_q_c/system/controlDict` |
| `P_Ts_c` | **541 iterations** [MEASURED, iterations] | **30 000** [REGISTERED] | 1 | **541** | `0`, `0.orig`, `541` | `verification/runs/T-family/T19_runs/P_Ts_c/log.solve:4938` |

Both exited `rc=0`, `capped=no`, `note=clean`
(`T19_runs/STATUS.P_q_c`, `T19_runs/STATUS.P_Ts_c`) [MEASURED]. **They did not
crash. They succeeded at the wrong experiment.**

**THE DEFECT IS IN THE FROZEN BUILDER, NOT MERELY IN THE EMITTED CASE.**
`verification/runs/T-family/T19_runs/build_t19.py:211` writes

    "    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }\n}\n"

and that line reappears at `P_q_c/system/fvSolution:32` and
`P_Ts_c/system/fvSolution:32` [MEASURED]. Rebuilding the cases from the frozen
builder reproduces the defect. **A repair applied only to the emitted
`fvSolution` would be undone by the next build.**

**TWO GATES DIE ON THAT ONE FACT.** Both re-driven by this lane rather than
cited:

- **completion** (rule 4). `python3 mark_done_t19.py --root . P_q_c` returns
  **rc = 1** with *"last written time 828 != endTime 30000; 828 ExecutionTime
  lines, expected 30000"*; `P_Ts_c` likewise at 541 [MEASURED, rc captured
  directly from `$?`, not through a pipe]. **NOT DONE → `analyse_t19.py` refuses
  at its first check.** No `DONE.*` marker exists in `T19_runs` and none was
  written by this probe [MEASURED, `ls DONE.* | wc -l` = 0].
- **C_PLATEAU**, the rung's load-bearing convergence gate, defined as *each
  graded quantity recomputed at the previous write (28 000) must have moved no
  more than the floor by the last write (30 000)*. **Neither write exists.** The
  only time directories are `0` and `828` (`0` and `541`). The gate is not
  failed — **it is UNEVALUABLE.**

And C_PLATEAU is the one that matters, by T19's own words: *"the gate is
C_PLATEAU, which is the check that actually caught T1c's iteration-count
defect."*

### 0.2 The second defect: a selftest limb that was green because the campaign had not run

`verification/runs/T-family/T19_runs/analyse_t19.py:691-694` drove its limb
*"live tree, no DONE markers -> exit 2 REFUSE"* by calling

    grade(HERE, os.path.join(tempfile.gettempdir(), "t19_never.json"), reg)

where `HERE` is the **live `T19_runs` directory** [MEASURED, `analyse_t19.py:29`
sets `HERE` to the module's own directory]. It passes **only because nothing has
been marked DONE**. It is a **D574-class false green** — a limb with a built-in
expiry keyed to the campaign's own progress — and worse than a stale one: the
moment a `DONE` marker exists, that limb executes the real grading path across a
live run tree **as a side effect of its own selftest**.

`T20_PREREGISTRATION.md:956-960` already names this limb as the demonstrated
member of the D574 class, and `T17_RESULTS.md:299-302` records it as *"still
true — only because T19 has not run"*. **T19b is where it gets repaired.**

### 0.3 The governing ruling, which this document applies and does not relitigate

`docs/DEAD_LEVER_AUDIT.md` §21.1–§21.2, committed at `998dc230` by
verification. Its operative holdings, carried here in full force:

| ruling | applied here |
|---|---|
| **(a)** `P_q_c` and `P_Ts_c` are **NOT A RESULT** — physics sound, not voided | §3: they are preserved as the falsification specimen, and their physics is not re-graded, re-used or discarded |
| **(b)** the four `held/` entries are **NOT PROMOTABLE** as they stand | §5: they stay held; T19b's own stage 2 is what releases the m/f four |
| **(c)** the legal repair is to the **CASE**, not to a gate | §2 and §4: `build_t19b.py` drops `residualControl`; every gate is loaded from T19's own frozen JSON |
| **(d)** the coarse pair re-runs FIRST and **C_PLATEAU must be SEEN TO EVALUATE** before the m/f four are released | §5, the staging gate, written as a hard stop |
| **(e)** the repair, re-run and promotion are heat-transfer's | this document is heat-transfer's and claims nothing of verification's |

**THE RULING'S FALSIFIABLE PART IS CARRIED FORWARD AS A NAMED PREDICTION**
(§6, P0): if, after dropping `residualControl`, `P_q_c` still fails to reach
30 000, the cause is not the one verification named and the ruling is wrong.
**T19b's first C_PLATEAU evaluation is the test of that reasoning, and this rung
reports against it either way.**

---

## 1. The parent files are UNTOUCHED — verified by hash, not asserted

`git hash-object <path>` against `git rev-parse HEAD:<path>`, taken by this lane
in one shell invocation. **The shared git index carries hundreds of stale staged
deletions, so `git status` is actively misleading about tracked-ness here; the
comparison below is against the HEAD BLOB and never against the index.**

| frozen T19 file | worktree blob | HEAD blob | identical | sha256 (first 16) | matches T19 §9 freeze table |
|---|---|---|:--:|---|:--:|
| `verification/runs/T-family/T19_runs/exact_t19.py` | `053e2b50ee1d7526eb5b32a61ec53fdf1b49b014` | `053e2b50ee1d7526eb5b32a61ec53fdf1b49b014` | **YES** | `aeaae65c9e849c8a` | **YES** |
| `verification/runs/T-family/T19_runs/build_t19.py` | `d28e32a379afdda9f8c23be173953106f1609785` | `d28e32a379afdda9f8c23be173953106f1609785` | **YES** | `e27c1f02b52da46c` | **YES** |
| `verification/runs/T-family/T19_runs/analyse_t19.py` | `0bafecd0a4bece177d2735fd41cb044b47aa2fba` | `0bafecd0a4bece177d2735fd41cb044b47aa2fba` | **YES** | `c2d8120ff510b1c4` | **YES** |
| `verification/runs/T-family/T19_runs/mark_done_t19.py` | `13117be1af47e0153877f98e1b93feb339f217b2` | `13117be1af47e0153877f98e1b93feb339f217b2` | **YES** | `a4dee8b3eb2e1af2` | **YES** |
| `verification/runs/T-family/T19_runs/run_one_t19.sh` | `21c774c0b10776a0f0c7236c8215b9c4a68ac76b` | `21c774c0b10776a0f0c7236c8215b9c4a68ac76b` | **YES** | `e0c0bc1558916611` | **YES** |
| `verification/runs/T-family/T19_runs/T19_registered.json` | `d63e8a4bf5ef8b3a5982940b044b08c75d9b4da0` | `d63e8a4bf5ef8b3a5982940b044b08c75d9b4da0` | **YES** | `84b3652a5187f04e` | **YES** |

All six reproduce **and** all six sha256 prefixes match the freeze table at
`T19_PREREGISTRATION.md:369-374` [MEASURED]. **Rule 6 is satisfied by
construction: T19b edits none of them.**

**THIS CHECK IS LOAD-BEARING, NOT CEREMONIAL.** `analyse_t19b.py` pins
`T19_registered.json` and `exact_t19.py` by sha256 **at run time** and
**REFUSES** rather than grades if either digest fails to reproduce (§4.2). It is
the mechanism by which *"no gate moved"* is a measurement rather than a claim.

---

## 2. WHAT DOES NOT CHANGE — enumerated, so the claim is checkable

**T19b defines no gate, no threshold, no band, no floor, no cap and no label.**
It does not copy them either. `analyse_t19b.py` loads
`verification/runs/T-family/T19_runs/T19_registered.json` **by absolute path**
and reads every one of them out of T19's own frozen file. If somebody wanted to
move a gate under T19b they would have to alter the parent's file, which would
break the pin and stop the comparator.

### 2.1 The three graded rows — carried, not restated

| row | quantity | reference | band (rel.) | predicted fine deviation | source at grading time |
|---|---|---|---|---|---|
| **G1** | `f·Re` at the registered station, from the axial pressure gradient | **96.0** | **±8.0e-04** | **−3.12e-04** | `T19_registered.json` `graded_rows.G1` |
| **G2** | `Nu`, uniform wall heat flux | **8.2352942009** | **±1.6e-03** | **+6.19e-04** | `graded_rows.G2` |
| **G3** | `Nu`, uniform wall temperature | **7.5407008741** | **±3.5e-03** | **+1.41e-03** | `graded_rows.G3` |

All six figures are [REGISTERED, dimensionless, T19] and are reproduced here for
the reader only. **The comparator never reads this table.**

### 2.2 The controls and floors — carried, not restated

| control | floor | source at grading time |
|---|---|---|
| **C_PLATEAU** | **1e-06** | `controls.C_PLATEAU.floor` |
| **C_SYM** | **1e-06 K / 1e-09 m/s** | `controls.C_SYM.floor_T` / `.floor_U` |
| **C_MASS** | **1e-06** rel. | `controls.C_MASS.floor` |
| **C_ID** | **1e-06** rel. | `controls.C_ID.floor` |
| **STAGNANT_FLOOR / P_MIN** | **0.5 / 0.05** | **imported by name** from `scripts/roache_triple.py`; the comparator defines neither and REFUSES if the registered copy disagrees (driven, §7) |
| `Fs` / `dim` / `r` | **1.25 / 2 / 2** | module constants, byte-identical to the parent's |
| `PLANT` | **1.234e-03** | imported from `scripts/roache_triple.py` |

### 2.3 The gate order, the ceiling and the label — unchanged

Rule 5's order is unchanged and `apply_gate()` is **byte-identical** to the
parent's: (1) any level failing C_PLATEAU / C_SYM / C_MASS / C_ID → NOT A RESULT
on every row; (2) triple not CONVERGING → NOT A RESULT with `p` printed and GCI
REFUSED; (3) CONVERGING → PASS inside the band else GATE FAIL, GCI at
`Fs` = 1.25. One way only. **THE FINE VALUE IS GRADED, NEVER THE RICHARDSON
EXTRAPOLATE.**

**The ceiling does not move.** The referent is EXACT/derived, so under the
upheld V/P ruling this rung scores **V and never P**: **GATE REACHED at best,
and it can NEVER reach HOLDS.**

**The capability claim does not move.** T19b earns a verdict for **forced
convection × laminar × 2-D, EXACT tier**, and nothing else — nothing turbulent,
nothing 3-D, nothing conjugate, and nothing for the entrance region, which is
solved but not graded.

### 2.4 The physics, the mesh and the case — unchanged, and MEASURED to be

`b` = 0.02 m, `Dh` = 0.04 m, `L` = 1.2 m, station `x_s` = 0.8 m, `x+` = 0.28169,
`nu` = 1.5e-05 m²/s, `Pr` = 0.71, `Re_Dh` = 100, `U0` = 0.0375 m/s,
`T_in` = 300 K, `T_wall` = 400 K, `dT/dn` = 500 K/m,
`buoyantBoussinesqSimpleFoam` at `simulationType laminar`, `beta` = 0, `g` = 0,
`endTime` = 30 000, `deltaT` = 1, `writeInterval` = 2 000, ladder
120×20 / 240×40 / 480×80, 1 rank, serial [all REGISTERED, T19].

**This is measured rather than promised.** Both builders were driven into
scratch trees with `--no-mesh` and the two trees compared file by file:

- **72 emitted files on each side; the file lists are IDENTICAL** [MEASURED].
- **66 of 72 are byte-identical.**
- **The 6 that differ are the six `system/fvSolution` files, and each differs by
  exactly one DELETED line** — `    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }`
  — with **zero added lines** [MEASURED, `diff -ru`; the full diff is in
  `verification/runs/T-family/T19b_runs/T19b_INSTRUMENT_DIFFS.txt`].

Independently of the emitted bytes, at module level [MEASURED]:

- **18 module constants compared** (`B_GAP DH NU PR RE U0 L X_S WIDTH T_IN
  T_WALL DTDN END_TIME WRITE_INTERVAL LEVELS CASES FOAM_BASHRC EXIT_REFUSE`) —
  **0 differ**.
- **11 of 12 emitter functions return byte-identical text**: `block_mesh`,
  `control_dict`, `fv_schemes`, `transport`, `turbulence`, `gravity`, `field_U`,
  `field_p_rgh`, `field_T`, `field_alphat`, `header`. **Nothing that decides the
  mesh, the fields, the boundary conditions, the schemes or `endTime` differs.**
- The twelfth is `fv_solution`, and the relation is exact: **the parent's output
  with its one `residualControl` line deleted is byte-equal to the successor's
  output**, with **no line added**.
- **AST comparison, docstrings and comments stripped**: both modules define the
  **same 18 functions**; **exactly two bodies differ** — `fv_solution` (the
  repair) and `selftest` (the limb that checks the repair). **Nothing else.**

---

## 3. FRESH CASE DIRECTORIES — and the old ones are EVIDENCE

**T19b builds into `verification/runs/T-family/T19b_runs/`**, a new run root, with
the six registered case basenames unchanged (`P_q_{c,m,f}`, `P_Ts_{c,m,f}`).
Keeping the basenames is deliberate: it is what lets the **frozen**
`run_one_t19.sh` and `mark_done_t19.py` be reused **unedited** (§4.4).

> **`verification/runs/T-family/T19_runs/P_q_c/` and `.../P_Ts_c/` ARE THE
> FALSIFICATION SPECIMEN. They hold `828/` and `541/`, and they are PRESERVED
> AS EVIDENCE. They are not cleaned, not reused, not rebuilt, not re-run, not
> re-graded and not deleted, by this document or under it.** They are the only
> artifacts on disk that demonstrate the defect, and the record of §0.1 cites
> them by line. Deleting them would destroy the evidence for the ruling that
> authorises this successor.

**That is enforced mechanically, not merely written down.** `analyse_t19b.py`'s
selftest runs its whole limb set under a filesystem watcher over `T19_runs` that
permits **only the two pinned parent instruments** and records every other read;
the measured count is **0 in both passes** (§7), and mutation control **M4**
proves the watcher fires when a limb does read `P_q_c/828/T`. **The specimen is
measured untouched, not asserted untouched.**

**Condition at freeze** (rule 2), checked immediately before this document is
committed: `verification/runs/T-family/T19b_runs/` holds
`build_t19b.py`, `analyse_t19b.py`, `mutation_controls_t19b.py` and
`T19b_INSTRUMENT_DIFFS.txt` and **nothing else — no case directory, no `0/`, no
numeric time directory, no `log.solve`, no `STATUS.*`, no `DONE.*`, no
`gate_t19b.json`. Zero core-minutes have been spent in the T19b tree**
[MEASURED, `ls -la`, 2026-08-31T15:22:52Z].

---

## 4. ANALYST BLINDNESS — INTACT, AND VERIFIED BEFORE BEING ASSERTED

**This is the strength that distinguishes T19b from T15b, and it is checkable.**

**Claim: no graded T19 quantity has ever been computed by anyone.** Not by this
lane, not by the supervisor, not by verification. Nobody has seen a T19 number.
**The claim was checked before it was written, by four independent sweeps**
[all MEASURED, 2026-08-31]:

| sweep | result |
|---|---|
| `find / -name 'gate_t19*'` — the whole filesystem, not just the repo | **0 hits.** The comparator's output file has never existed anywhere on this box |
| `git log --all -- '*gate_t19*'` | **0 commits.** It has never been committed |
| every `DONE.*` in `T19_runs` | **0.** The comparator refuses at its first check and has therefore never reached a value |
| the two graded reference values `8.235294…` / `7.540700…` grepped across `docs/` and `verification/` | **2 files: `T19_PREREGISTRATION.md` and `T19_registered.json`** — both *references*, i.e. the analytic targets registered before compute. **No measured value, no deviation, no verdict, no GCI, no `p`** |

There is also **no `docs/COST_CALIBRATION.md` row for T19** [MEASURED, 0 hits],
so not even the cost channel has produced a filed number.

**So the analyst is genuinely blind here, and the mechanism is stronger than
discipline: the comparator has never run on real data.** `P_q_c` and `P_Ts_c`
produced fields, and **no graded value has ever been read from them** — the
grader refuses before reading, because `mark_done_t19.py` returns NOT DONE.

**IF ANY OF THAT IS WRONG, THE CLAIM IS WITHDRAWN AND NOT DEFENDED.** A single
recorded T19 value anywhere on the box falsifies it, and the four sweeps above
are exactly the queries that would surface one. **This lane found none.**

**What blindness buys, stated exactly.** T19b's bands could not have been tuned
to T19's answer because T19 has no answer. That is not a claim about anyone's
integrity — it is a structural fact about what exists on disk.

### 4.1 `build_t19b.py` — the repaired builder

`verification/runs/T-family/T19b_runs/build_t19b.py`, **389 lines**, a new file;
`build_t19.py` is **not edited** (§1). Its **only substantive change** is that
`fv_solution()` does not emit the `residualControl` block. The diff against the
parent is **3 removed lines and 42 added** [MEASURED], and the three removed
lines are:

    -"""Build T19's registered cases: fully developed laminar forced convection      (docstring title)
    -usage: build_t19.py --root DIR [--case NAME ...] [--no-mesh] | --check-levels | --selftest   (usage line)
    -        "    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }\n}\n"                (THE REPAIR)

**Two of the three are the file's own name. One is the defect.** The 42 added
lines are: the docstring paragraph stating the defect and the ruling, a comment
block at the deletion site recording what was removed and why, and one new
selftest limb. Nothing else. §2.4's emitted-tree and AST comparisons measure
that independently of the diff.

**The setting is DELETED, not relaxed and not made configurable.** A tolerance
of `1e-30`, or a switch, would leave a lever that can be set wrong; deletion
conforms the case to the registration exactly as `build_t1c.py` does.

### 4.2 `analyse_t19b.py` — the repaired comparator

`verification/runs/T-family/T19b_runs/analyse_t19b.py`, **1 041 lines**, a new
file; `analyse_t19.py` is **not edited**. Diff against the parent: **20 removed
lines, 305 added** [MEASURED]. **The 20 removed lines are the whole change
surface, and they are worth reading in full** — they are in
`T19b_INSTRUMENT_DIFFS.txt` and reduce to four groups:

1. the docstring title and the `rung="T19"` output key (identity);
2. `sys.path.insert(0, HERE)`, `p = os.path.join(root or HERE, ...)` and
   `--json` defaulting to `gate_t19.json` — **retargeting from `HERE` to the
   pinned parent path**, which is the mechanism of §2;
3. `EXIT_OK, EXIT_REFUSE` and `refuse()` **moved earlier in the file** (byte
   identical bodies) so the sha256 pin can run before the `exact_t19` import;
4. **the six lines of the defective limb**, including
   `grade(HERE, os.path.join(tempfile.gettempdir(), "t19_never.json"), reg)`.

**No reader, no control, no floor, no band and no verdict-writing function is
touched.** `apply_gate()`, `planted_zero_control()`, `read_scalar()`,
`read_ux()`, `nu_at_column()`, `f_Re_from_pressure()`, `symmetry_witness()`,
`triple_of()` and `grade()`'s body are unchanged.

**What the 305 added lines are**, in order of weight: the S8 machinery
(`_RootWatch`, `_here_refs_in_selftest`, `_populate_run_root`, the twice-run
`selftest()` driver) at roughly 200 lines; the sha256 pin at ~35; the repaired
no-DONE limb at ~30; docstring and comments for the rest.

**The S8 clause is adopted verbatim in substance from
`T20_PREREGISTRATION.md` §10.1**, which registers it as *"the most valuable line
in that document"*: **no selftest limb may read, `stat` or `glob` a live run
tree, and the invariance is MEASURED, not promised.** T19b implements it with
four detectors, each carrying its own planted control:

| id | detector | how it can fail |
|---|---|---|
| **S8a** | the **entire limb set runs twice in one invocation** — once against a synthetic run root that is **empty**, once against one **fully populated** (six complete cases, `0/`, `28000/`, `30000/`, `log.solve`, `STATUS.*`, `DONE.*`) — and the two outcome structures must be **byte-identical** | mutation **M6** |
| **S8b** | a filesystem **watcher** over the run root records every read through seven routes (`open`, `os.listdir`, `os.scandir`, `os.path.isfile/isdir/exists`, `glob.glob`); the count must be **0** | mutation **M3** |
| **S8c** | a second watcher over **`T19_runs`** allowing **only** the two pinned instruments, so the falsification specimen is measured untouched | mutation **M4** |
| **S8d** | a source-level detector: **0** references to the name `HERE` inside the selftest functions — `analyse_t19.py:691` held exactly one | mutation **M2** |

**RULE 3 IS APPLIED TO THE SELFTEST ITSELF, and this is the part this lane
thinks matters most.** A watcher that reports *"zero reads"* is worthless until
it has been shown able to report a non-zero. So before the limbs run, each
watcher is handed a **deliberate planted read** it must record; the record is
checked; and only then is it cleared. **Both probe paths are chosen not to
exist**, so nothing is learned about either tree — only about the watchers.
Mutation **M5** blinds the watcher and shows that the planted control, and only
the planted control, is what stands between a blinded watcher and a false green.

**The repaired no-DONE limb is STRICTLY STRONGER than the one it replaces.** The
parent pointed at a live directory holding **no cases at all**, so its refusal
was over-determined — it proved only that `grade` refuses on an empty directory.
The successor forges **six complete, fully readable cases** and removes **only**
the `DONE` markers, so the refusal is **attributable to the DONE check**; it
also asserts that **no gate json was written** [both MEASURED, §7].

### 4.3 `mutation_controls_t19b.py` — the proof the new limbs can fail

`verification/runs/T-family/T19b_runs/mutation_controls_t19b.py`, 191 lines.
**A limb that cannot fail is the defect being repaired**, so a green selftest is
not evidence about the successor until each new limb has gone red on a source
carrying the defect it detects. §7 records the six controls and their results.

### 4.4 What T19b does NOT need to write — and it is measured, not assumed

**`mark_done_t19.py` and `run_one_t19.sh` are REUSED UNEDITED.** Both were read
by this lane to establish that they are root-parameterised rather than
path-hardcoded:

- `mark_done_t19.py:212-220` accepts **`--root`**, defaulting to `HERE` only
  when absent, and its `CASES` tuple is exactly T19b's six basenames
  (`mark_done_t19.py:36`). `python3 mark_done_t19.py --root <T19b_runs>` is the
  registered invocation.
- `run_one_t19.sh:38-39` reads its cap from `$SELF/T19_registered.json` — i.e.
  from **T19_runs**, the frozen file — while `:63-66` derive `ROOT` and `CASE`
  from `--case-dir`, so `STATUS.<case>` lands in **T19b_runs**. The cap lookup
  keys on the case basename, which is unchanged, so **the registered caps apply
  to T19b unchanged and cannot be widened or narrowed at launch**
  (`run_one_t19.sh:75`). The foreign-process guard compares absolute `cwd`
  values (`:156`), so the shared basenames cannot collide across the two trees.
  `bash -n` returns **rc = 0** [MEASURED].

**No `T19b_registered.json` is created, and that is the point.** A copy could
drift from its original; a pinned pointer cannot.

**HONESTLY BOARDED, NOT PAPERED OVER:** `run_one_t19.sh`'s **ARM A (a real
launch) is still UNDRIVEN in the T19b tree** — it was driven twice under T19
(`STATUS.P_q_c`, `STATUS.P_Ts_c`, both `rc=0`), which is evidence the wrapper
works, but that is evidence from a different run root. The supervisor should
treat the first T19b coarse launch as also being the launcher's smoke test in
this tree.

---

## 5. STAGING — the ruling's (d), written as a hard stop

**STAGE 1 — the coarse pair, alone.** Build the six cases into `T19b_runs`;
launch **`P_q_c` and `P_Ts_c` only**. Both arms go together because they are one
grid level of one rung and C_ID compares them.

**THE STAGING GATE, and it is a stop rather than a preference:**

> **THE m/f FOUR ARE NOT RELEASED UNTIL `C_PLATEAU` HAS BEEN SEEN TO EVALUATE —
> PASS OR FAIL — ON THE COARSE PAIR.** A gate that has never once been computed
> is not yet known to be alive. Evaluating requires two numeric write
> directories on each coarse case (**28 000 and 30 000**), which requires
> `mark_done_t19.py --root <T19b_runs>` to return **DONE** on both, which
> requires the run to reach `endTime`. **A C_PLATEAU that is UNEVALUABLE is not
> a pass and does not release stage 2.**

**STAGE 2 — the medium and fine four**, released only after stage 1 clears the
gate above. The four `held/` queue entries stay **held** until then; promoting
them earlier would spend 181.152 core-min [REGISTERED] on runs the frozen
instrument is guaranteed to refuse, which is ruling (b).

**STAGE 3 — grade.** `analyse_t19b.py --root <T19b_runs>`, once all six carry
`DONE`. `grade()` refuses unless **all six** are marked: the whole rung is graded
or none of it is.

**Nothing in this document authorises a launch, and enqueueing is not
authorisation.** `verification/queue/heat-transfer/` is a launch button on a
one-minute cron tick with a validator that ignores unrecognised keys, so no
annotation makes an entry inert. **Dropping is the supervisor's, after check 4.**

---

## 6. PREDICTIONS — registered before compute, and every one can lose

- **P0 — THE RULING'S OWN TEST.** With `residualControl` removed, both coarse
  cases reach **`Time = 30000`**, write `28000/` and `30000/`, and C_PLATEAU
  **evaluates**. *Can lose*: if `P_q_c` still stops early, verification's §21.2
  diagnosis is wrong and **this lane reports it as wrong against that paragraph**.
- **P1.** G1, G2, G3 all **PASS** at −3.12e-04 / +6.19e-04 / +1.41e-03
  [REGISTERED, T19]. *Can lose*, and **G3 is the likeliest to**: its prediction
  is a scaled version of the only row T1c GATE FAILED.
- **P2.** All three triples CONVERGING with `p` in **[1.6, 2.4]**.
- **P3.** C_ID holds at better than **1e-12**, not merely better than its 1e-06
  floor: with `beta = 0` the two arms should produce bit-identical velocity and
  pressure fields.
- **P4.** The wall-to-wall Nusselt asymmetry (REPORTED, never gated) is below
  1e-08 relative on every level.
- **P5.** The REPORTED first-order wall-shear route for `f·Re` misses 96 by
  roughly `1/(2 ny)` while the GRADED pressure route is second order.
- **P6 — COST, and it is the one this lane adds.** Each coarse case lands
  between **1.3 and 2.6 core-min** at the full 30 000 iterations — i.e. the
  registered 2.952 POINT over-predicts by roughly **1.1× to 2.3×** [EXTRAPOLATED,
  core-min, §8.2]. *Can lose in both directions.*

**If a prediction loses it is reported as wrong.**

---

## 7. INSTRUMENTS — the measured selftest state, and the mutation controls

All runs below: `__pycache__` cleared first (stale bytecode has inverted mutation
tests in this lab before), `PYTHONDONTWRITEBYTECODE=1`, **rc captured directly
from `$?` or from the process object, never through a pipe**.

| instrument | result |
|---|---|
| `build_t19b.py --selftest` | **rc = 0, SELFTEST PASS (0 failed)**, 8 limbs — ladder `r` = 2 both directions with the station on a cell face at every level; a level pair sharing `ny` REFUSED; both arms write their wall condition on BOTH walls; **the built `fvSolution` emits no `residualControl`, with the same detector shown PRESENT on a copy carrying `build_t19.py:211`'s line**; `0.orig` holds exactly {U, p_rgh, T, alphat}; `check_case_provenance.py` rc = 0; AST assert count 0 with a planted control at 1 |
| `analyse_t19b.py --selftest` | **rc = 0, SELFTEST PASS (0 failed)**, 40 s wall — **22 limbs run twice** (S8 pass A empty root, pass B populated root, 18 entries) plus the five S8 measurements. VALUE CONTROL grades G1/G2/G3 **PASS** with `p` = **2.000 / 1.903 / 1.957** and fine deviations **+1.562e-04 / +7.610e-05 / +7.721e-05**, matching T19's registered reader components exactly; C_PLATEAU / C_SYM / C_MASS each broken → NOT A RESULT ×3; `f·Re` perturbation 30/ny² → **GATE FAIL**; both planted-zero controls PASS (Nu_H moved 2.09e-03, `f·Re` moved 2.81e+03, floors 1e-07); registered `P_MIN` mutated → REFUSE |
| S8a | **byte-identical** outcome structures over an empty vs a fully populated run root |
| S8b | **0 + 0** recorded reads of the run root across the two passes |
| S8c | **0** recorded reads under `T19_runs` beyond the two pinned instruments — **the falsification specimen is measured untouched** |
| S8d | **0** `HERE` references in the selftest functions; the same detector returns **1** on a planted `grade(HERE, …)` source |
| `mutation_controls_t19b.py` | **rc = 0, MUTATION CONTROLS PASS (8 of 8 behaved as registered)** |

**0 `ast.Assert` in both instruments** (L-332); every refusal is `sys.exit(2)`.

### 7.1 The six mutation controls — each new limb, driven red

Each control mirrors the repository's directory depth in a sandbox (symlinking
the real `scripts/` and `T19_runs/`) so the mutant computes the same `PARENT`,
`REPO` and pins as the real file and differs by **exactly one planted string**.
**The expectation is deliberately specific: rc = 1, a FAIL summary, and the limb
that goes red is THE NAMED ONE** — *"the selftest failed"* would prove nothing
about the limb under test.

| control | what is planted | limb that must go red | result |
|---|---|---|---|
| **baseline ×2** | nothing | — | **rc = 0, PASS (0 failed)** on both instruments |
| **M1** | `residualControl` planted **back** into `build_t19b.fv_solution` | *the built fvSolution emits NO residualControl block* | **rc = 1, FAIL (1 failed)** |
| **M2** | T19's `grade(HERE, …)` restored inside the limb set | **S8d** | **rc = 1, FAIL (1 failed)** |
| **M3** | a limb calls `os.listdir(run_root)` | **S8b** | **rc = 1, FAIL (1 failed)** |
| **M4** | a limb reads `T19_runs/P_q_c/828/T` — the specimen | **S8c** | **rc = 1, FAIL (1 failed)** |
| **M5** | the watcher is **blinded** (`_note` made a no-op) | **the planted control (rule 3)** | **rc = 1, FAIL (1 failed)** |
| **M6** | a limb's outcome made to depend on the run root's state | **S8a** | **rc = 1, FAIL (1 failed)** |

**Each mutant reddened exactly one limb** ("1 failed" throughout), so the six
controls are independent rather than one detector firing six times [MEASURED].

### 7.2 `CANNOT SEE` — recorded rather than repaired (L-401)

**The S8b/S8c watcher covers seven call routes and does NOT cover `os.stat`,
`os.path.getsize`, `os.walk`'s stat calls, `pathlib`, or `subprocess`.** This is
a real blind spot and it is named rather than glossed. **M6 exploits it
deliberately**: the mutant reads the run root through `os.stat`, is invisible to
both watchers, and is caught by **S8a** — which is precisely why S8a is
registered alongside them rather than instead of them. **The two detector
families cover each other's blind spots, and this lane measured that rather than
hoping for it.** OWNER: heat-transfer. RE-READ at T19b's grading, and at the
next T-family successor that adopts S8.

---

## 8. COST — rule 12

### 8.1 The registered cost, carried over verbatim

**T19b prices the FULL 30 000 iterations, so T19's own POINT and CAP figures are
the correct basis and are carried across unchanged.** They are not re-derived,
and no cap moves — a cap is a registered quantity and ruling (c) forbids moving
one.

| case | cells | **POINT core-min** | **CAP core-min** | `timeout` (s) | ranks |
|---|---:|---:|---:|---:|---:|
| `P_q_c` / `P_Ts_c` | 2 400 | **2.952** each | **12** each | 720 | 1 |
| `P_q_m` / `P_Ts_m` | 9 600 | **12.624** each | **50** each | 3 000 | 1 |
| `P_q_f` / `P_Ts_f` | 38 400 | **77.952** each | **250** each | 15 000 | 1 |
| **stage 1 (coarse pair)** | | **5.904** | **24** | | |
| **stage 2 (m/f four)** | | **181.152** | **600** | | |
| **total (6 cases)** | | **187.06** | **624** | | |

All [REGISTERED, core-min, `T19_registered.json` `cases.*.point_core_min` /
`cap_core_min` / `timeout_s`]. The underlying rate is
**[BORROWED, core-s per cell-iteration, from T1c's four completed runs]** —
2.46e-06 at 2 400 cells, 2.63e-06 at 9 600, 4.06e-06 at 38 400 — and T19's
registration already named the misprediction risk in carrying it across a 1.47×
mesh jump. **That borrow is labelled here exactly as it should have been
labelled in the sentence that killed T19.**

Dollars: POINT 187.06 core-min = 3.118 core-h = **$0.1599**; CAP 624 core-min =
10.4 core-h = **$0.5335**, at $0.0513/core-h — **DERIVED, not measured**; the
rate itself is **[REPORTED-BY-OWNER]** (`COMPUTE_BUDGET_CHARTER.md` §5: the box
cannot read its own billing). **Stage 1 alone is 5.904 core-min POINT = $0.0050
derived.** Well inside the pre-authorised ceiling. **An overrun stops the run;
it does not get a new budget.**

### 8.2 The 59× is a DETECTOR THAT FIRED, and it must not be filed as estimator error

T19's registered POINT for `P_q_c` was **2.952 core-min**
[REGISTERED, `T19_registered.json:29`] and the measured actual was **0.050
core-min** [MEASURED, `T19_runs/STATUS.P_q_c`, `wall_s=3 ranks=1`] — a ratio of
**59.0×**. For `P_Ts_c`: **2.952** against **0.033** [MEASURED,
`STATUS.P_Ts_c`, `wall_s=2`] — **89.5×**.

> **NEITHER RATIO IS AN ESTIMATOR ERROR AND NEITHER MAY BE FILED AS ONE.** The
> registration priced a **30 000-iteration** run; the cases stopped at **828**
> and **541**. The iteration ratios are **36.2×** and **55.5×** — same
> direction, same order, same two cases. **The cost channel detected the
> truncation.** A `docs/COST_CALIBRATION.md` row recording 59.0× as
> "estimator error" would have buried the finding in the ledger, which is
> `docs/LEDGER_HEADLINE_AUDIT.md`'s standing failure shape.

**AND THE RESIDUAL, WHICH IS THE PART THIS LANE ADDS AND THE BRIEF DID NOT ASK
FOR.** Dividing out the truncation leaves a real, separable misprediction
[DERIVED, dimensionless]:

| case | predicted core-s/iteration | measured core-s/iteration | residual over-prediction |
|---|---:|---:|---:|
| `P_q_c` | 177.12 / 30 000 = **5.904e-03** | 3 / 828 = **3.623e-03** | **1.63×** |
| `P_Ts_c` | **5.904e-03** | 2 / 541 = **3.697e-03** | **1.60×** |

**Both arms agree at ≈1.6× over-prediction per iteration**, in the direction
T19's registration named as the *unlikely* one (it predicted **under**-prediction
from the mesh jump). **BUT THE FIGURE IS WEAK AND IS LABELLED WEAK:** `STATUS`
records `wall_s` at **1-second granularity**, so a 3-second run carries roughly
±17 % and a 2-second run ±25 % from rounding alone, before contention. **A
1.6× taken from a 2-second measurement is a hint, not a calibration**, and it is
recorded as [EXTRAPOLATED] rather than [MEASURED] for that reason. It is the
basis of prediction **P6**, and stage 1's own actuals — measured over ~110
seconds rather than 2 — will be the first figure worth filing.

### 8.3 The calibration row that is owed

**Rule 12's estimate-versus-actual comparison is owed at every process
completion**, and for this rung it is owed **twice**: once at stage 1 (the
coarse pair) and once at stage 3 (the full six). Each row goes in
`docs/COST_CALIBRATION.md` under that file's append rules and the rule-10
private-index protocol, and **each must state the ratio actual/predicted,
attribute the gap, and keep waste separately named rather than absorbed into the
ratio**. **The stage-1 row must also carry the sentence that T19's 59.0× was a
truncation detector and not an estimator miss**, so the ledger cannot lose the
finding.

---

## 9. WHERE THIS LANE'S READING GOES BEYOND THE BRIEF — boarded, not silently adopted

1. **The brief named the `P_q_c` ratio (59.0×) as the cost witness. This lane
   measured the second one too** — `P_Ts_c` at 89.5× against an iteration ratio
   of 55.5× — and found that **both reduce to the same ≈1.6× residual
   over-prediction per iteration** (§8.2). That residual is a *new* finding, is
   in the direction T19's registration called unlikely, and is registered as a
   falsifiable prediction (**P6**) rather than asserted. It rests on 2- and
   3-second wall clocks and is labelled accordingly.
2. **The brief said "fresh case directories". This lane kept the six case
   BASENAMES and changed the run ROOT** (§3, §4.4), because that is what lets the
   frozen `run_one_t19.sh` and `mark_done_t19.py` be reused **unedited** — no
   third and fourth successor instrument to review, and one less place a gate
   could move. The two trees are fully separated by absolute path and the
   launcher's guards are absolute-path guards. **If the supervisor prefers
   distinct basenames, that is a larger change than it looks: it would require
   new copies of both frozen instruments and a new registered JSON, and this lane
   recommends against it.**
3. **The brief asked for at least three mutation controls; this lane wrote six**,
   one per new limb plus one for the watcher's own blindness, and required each
   to redden **only** its named limb.

---

## 10. THE FREEZE SET

New files, all under `verification/runs/T-family/T19b_runs/`. Hashes taken
**2026-08-31T15:22:52Z** at HEAD `c4fadb21`; **the supervisor must re-take them
at the freeze commit**, because a later edit would invalidate them and the pin in
`analyse_t19b.py` depends on the *parent's* digests, not on these.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `build_t19b.py` | `92149d455cd6f64b` | `b687db4df4411b51264cd643f3464e75b8ccd8b1` | 389 |
| `analyse_t19b.py` | `c7b1822538eb1a51` | `32c309e112152bca019cb774bb8e310f663f58f7` | 1041 |
| `mutation_controls_t19b.py` | `79dc0962c588382c` | `663adf76059df65a8a44f06e61f45ca32b222dfa` | 191 |
| `T19b_INSTRUMENT_DIFFS.txt` | `cf65a1ad9a629209` | `7157db64f9cf49cebaa11ade48ed602fc0318f0e` | 562 |

Pinned inside `analyse_t19b.py`, and **not** part of this freeze set because they
belong to T19:

| pinned parent instrument | sha256 |
|---|---|
| `T19_runs/T19_registered.json` | `84b3652a5187f04efeddb5b14cc91b2d1c5d9952b7608243bdd0078773a040b4` |
| `T19_runs/exact_t19.py` | `aeaae65c9e849c8a40d9594e412e3a1bc63ebe79274f5bc704837570cf52545d` |

**Filing.** `python3 scripts/check_filing.py` reports **40 pre-existing
violations across 8 rules and NONE of them names T19b or `T19b_runs`**
[MEASURED]. The pre-existing 40 are other teams' and are not this lane's to fix.

**Case inputs are not committed by this document** — the six T19b case
directories do not exist yet (§3, condition at freeze). They are written by
`build_t19b.py` at stage 1, and `constant/polyMesh` stays out of git as under
T19.

---

## 11. WHAT THIS DOCUMENT DOES NOT DO

It **moves no gate, threshold, band, floor, cap or label**, and seeks no §2d.1
grant. It **edits no frozen file** — T19's six frozen instruments are verified
byte-identical to HEAD in §1 and stay that way. It **does not delete, clean,
reuse, rebuild or re-grade `T19_runs/P_q_c` or `T19_runs/P_Ts_c`**, which are
preserved evidence. It **does not promote anything out of
`verification/queue/heat-transfer/held/`**. It **does not authorise a launch**,
and enqueueing is not authorisation. It **does not re-open or amend
`DEAD_LEVER_AUDIT.md` §21**, which it cites and applies. It claims **no
turbulent, 3-D or conjugate capability**. And it authorises **no send —
SUBMISSIONS REMAIN PARKED** (rule 7).
