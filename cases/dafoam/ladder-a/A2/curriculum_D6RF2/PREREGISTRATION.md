# Curriculum D6RF2 — `F_mp` and `REF_off` at a producer whose anchor is unique, and the registration-time gate that would have caught `D6RF-BLOCKING-1` before a launch

**Item id:** `D6RF2` (dafoam curriculum successor to `D6RF`). **Team:** dafoam. **Date:** 2026-09-03.
**Version 1.0 — FROZEN by the commit that introduces this file.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2).
Permission for detached launches: **`bc0e687e`**.
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6). **This item has burned 0 core-min, started no container, and
IS NOT ENQUEUED.**

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF2-a2-wing-multipoint-fd`, asserted
**ABSENT BY EXECUTION**:

    ROOT_ABSENCE_ASSERTED_BY_EXECUTION utc=2026-09-03T19:40:19Z
      /home/ubuntu/certonomous-runs/CURRICULUM-D6RF2-a2-wing-multipoint-fd=ABSENT

---

## 0. WHY A SUCCESSOR AND NOT AN AMENDMENT — and what is inherited unchanged

`D6RF` (`cases/dafoam/ladder-a/A2/curriculum_D6RF/`) registered `F_mp` and `REF_off`, the two arms
nobody in the D6 lineage had ever bought. It could not run them. **Ruled by the dafoam-supervisor
2026-09-03: successor, not amendment**, on three grounds — `D6RF` has had compute so
`VERIFICATION_CHARTER.md` §2d closes its gates; the fix touches a file frozen and md5-pinned in
`D6RF` §7b; and this family's precedent for an unrunnable registration is successor-not-amendment
(`D6`→`D6R`, `A1WR`→`A1WRT`).

**INHERITED BY CITATION FROM `D6RF`, UNCHANGED, AND NOT RESTATED HERE:** §1's three repairs
(`D6RF-DEF-1` the driver-scaled endpoint, `D6RF-DEF-2` the in-place `F_mp` staging, `D6RF-DEF-3`
`REF_off`'s 3.16×-short cap); §2's two arms and five FD components; §2a's staging contract S1–S8 and
its no-`rm -rf`, refuse-on-stale-directory rule; §3's gates, thresholds, bands and labels **in full**;
§4's anchors, caps `F_mp` **480.0** / `REF_off` **190.0**, ceiling **670.0**, `TMO` **7,110** /
**2,760** at `FRAME_ALLOWANCE_S = 90`, and the cost basis; §5's predictions; §6's two rows.
**NO GATE, THRESHOLD, BAND, CAP, LABEL, PREDICTION OR COST MOVES IN THIS ITEM.** What moves is the
producer's docstring, the pins that follow from it, and one new **pre-compute** gate.

---

## 1. `D6RF-BLOCKING-1` — the sentence explaining the anchor contained the anchor

`d6r_opt_runScript.py` carries the sentinel `# OpenMDAO setup` **twice**: at **`:230`**, the real
anchor, and at **`:21`**, inside the module docstring, in the sentence
*"The ANCHOR line `# OpenMDAO setup` is kept so that `d6r_fd_endpoint.py` and `d6r_ref_off.py` exec
the header exactly as D4's FD instrument does."* **The sentence explaining why the anchor exists
reproduces it, and thereby breaks it.**

Both consumers refuse on a count other than one — `d6r_fd_endpoint.py:67`, `d6r_ref_off.py:53` — so
**both arms were unrunnable, and so were `D6R`'s own.** `d4_opt_runScript.py` carries it **once**,
which is why D4's arm F3 ran.

**THE GUARDS WERE PROTECTING THE ITEM, AND THE MEASUREMENT SHOWS IT.** `split(ANCHOR)[0]` returns
**1,396 characters of a 12,861-character file**, truncated inside the docstring, where the correct
header is **10,275**. The truncated header carries **`daOptions`** — the docstring mentions it — but
**not `class Top`, not `POINTS`, not `U0`, not `CL_TARGETS`, not `WEIGHTS`**, every one of which the
consumers read out of the exec'd namespace. **A `daOptions`-only check would have passed it.**
Nothing about the detectors needs changing: a count-must-be-1 refusal is exactly what should happen.
**What was never checked is whether the producer could satisfy them.**

**HOW IT WAS FOUND, AND IT IS NOT TO THE LANE'S CREDIT.** `D6RF`'s own guard self-test started a
container by accident (`D6RF` ADDENDUM 3 §A3.3) and that container refused on this. **Without the
accident `D6RF` would have been re-enqueued after its `.gz` repair and spent `F_mp`'s registered
155.7 core-min reaching a guaranteed refusal.** That does not make the accidental launch acceptable;
it makes the disclosure valuable. `D6RF`'s `P2` — *"the chain COMPLETES"* — **MISSED, for a reason
established before the compute rather than after it.**

---

## 2. THE REPAIR — a docstring reword, and the pins that follow from it

### 2a. ⚠ A CORRECTION TO THE RULING THAT COMMISSIONED THIS ITEM

The ruling says the fix *"is a DOCSTRING REWORD and changes no executable byte"* and that the
successor *"stages its OWN copy of the producer with a new pin"*. **Both are true of the producer and
neither is sufficient**, because **both consumers hardcode
`PRODUCER_MD5 = "93edb4a231e13a7af065368f61a468ef"`** (`d6r_fd_endpoint.py:31`, `d6r_ref_off.py:30`)
and check it **before** they ever count the anchor. **A one-character reword therefore makes them
refuse one step EARLIER, at the md5.** So this item must derive the consumers too. It does — by
substitution of exactly two constants each, the producer's **name** and its **md5**, and nothing
else. `D6RF`'s `d6rf_endpoint_physical.py` pins the same md5 and is derived on the same terms.

**`D6R`'s originals are not edited, not moved and not re-pinned.** `D6R`'s record and its pins stand
intact, and this item reads them read-only.

### 2b. The derivation — enumerated, and every substitution asserted present-then-absent

`d6rf2_derive.py` derives four files from frozen bytes. **Anything not in the substitution set is the
source's bytes.** Each substitution must occur **exactly once** before and be **gone** after; a
substitution that matched nothing is a silent no-op and aborts.

| derived | from | substitutions |
|---|---|---|
| `d6rf2_opt_runScript.py` | `curriculum_D6R/d6r_opt_runScript.py` | **1 — the docstring sentence.** Prose only; **no executable byte changes** |
| `d6rf2_fd_endpoint.py` | `curriculum_D6R/d6r_fd_endpoint.py` | 2 — `PRODUCER`, `PRODUCER_MD5` |
| `d6rf2_ref_off.py` | `curriculum_D6R/d6r_ref_off.py` | 2 — `PRODUCER`, `PRODUCER_MD5` |
| `d6rf2_endpoint_physical.py` | `curriculum_D6RF/d6rf_endpoint_physical.py` | 3 — `RUNSCRIPT`, `MD5_RUNSCRIPT`, the locus module name |

`d6r_extract_endpoint.py` **does not use the anchor** (measured: zero occurrences) and is staged
**unchanged** under `D6R`'s own md5.

**The replacement names the anchor without reproducing it**, and the deriver **asserts the
replacement does not contain the sentinel**. Its closing line is registered here:
*"Name the anchor; never quote it."*

**THE REPAIR IS ASSERTED, NOT ASSUMED, and the assertions are stronger than a count:**

* the **original** must still carry the sentinel **twice** — otherwise the premise of this item has
  changed and the deriver aborts;
* the **repaired** producer must carry it **exactly once** — measured **2 → 1**;
* the header must be **≥ 10,000 characters** — measured **10,536**, against the broken **1,396**;
* the header must carry `class Top`, `POINTS`, `U0 =`, `daOptions`, `CL_TARGETS`, `WEIGHTS`;
* and the strongest form: **the repaired header is byte-for-byte the original's CORRECT header with
  the registered substitution applied.**
* every derived consumer must **name the repaired producer and pin its md5**, with the old md5
  **absent** from the file.

---

## 3. `G-ANCHOR` — THE NEW GATE, AND IT IS PRE-COMPUTE

**The rule, registered by the dafoam-supervisor 2026-09-03, in his words:**

> Any reader that splits a file on a sentinel must have that sentinel's **uniqueness asserted AT
> REGISTRATION**, on the bytes it will actually read — not merely refused at run time.

`d6rf2_anchor_gate.py` (md5 in §5) enforces it over **every anchor-scoped reader in this item**, and
it runs **before any container**, not as a grading gate. It **REFUSES (exit 3)** rather than
degrading. Its five clauses, each on the real bytes:

| clause | assertion |
|---|---|
| **A1** | the reader declares `PRODUCER`, `PRODUCER_MD5` and `ANCHOR`, **parsed out of the reader's own source by `ast`** — never typed into the gate, so a reader whose anchor changes cannot drift past it |
| **A2** | the producer it names is the one this item stages, it exists, and **the md5 it pins is that file's actual md5** — the clause the ruling did not anticipate |
| **A3** | the sentinel occurs **exactly once** in that producer |
| **A4** | the header `split(SENTINEL)[0]` is **≥ 9,000 characters** — *a count of 1 at the wrong site is still wrong* |
| **A5** | the header carries every symbol the consumers read out of the exec'd namespace |

**DRIVEN IN BOTH DIRECTIONS, ON REAL BYTES — 6/6, under `python3` AND `python3 -O`:**

* **positive:** the repaired producer passes for **both** readers — count 1, header **10,536**, all
  six symbols;
* **negative:** the **ORIGINAL producer, still on disk unedited**, **REFUSES at A3**, and the
  evidence prints the header it prevented — **1,396 chars, missing `class Top`, `POINTS`, `U0 =`,
  `CL_TARGETS`, `WEIGHTS`**, with a plant asserting that shape exactly;
* **A4:** a producer whose sentinel is **unique but moved to the top** — count still 1 — **REFUSES**;
* **A2:** a producer that **drifts by one comment** refuses **at the md5, before the anchor is ever
  counted**; a producer **absent** from the work directory refuses.

**This gate does not alter any inherited gate, threshold, band, cap or label.** It is a
registration-time admissibility check and it can only turn a launch into a refusal.

---

## 4. WHAT `D6RF`'s RUN ROOT COST, AND WHERE IT WENT

**Archived, never deleted**, on the supervisor's ruling, with the preservation asserted by count:

| | |
|---|---|
| from | `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF-a2-wing-multipoint-fd` |
| to | `…/CURRICULUM-D6RF-a2-wing-multipoint-fd_partial_20260903T193723Z` |
| paths | **617 → 617** |
| top-level entries | **25 → 25** |
| bytes | **68,393,914 → 68,393,914** |

**Total spend on that root: 0.800 core-min = $0.0007 DERIVED**, and **it is WASTE, named as waste
and never absorbed into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). `F_mp`'s staging abort produced
**no `ARM=` row** and `spent_before_arm=0.000`.

**The stray `ARM=REF_off rc=2` row is ANNOTATED, NOT EDITED.** A line appended to that ledger names
it a **guard-self-test artefact, not an arm attempt** — no chain requested it; `STATUS.chain` had
closed `STOPPED_AT_FIRST_NONZERO arm=F_mp rc=5 not_run=[REF_off]` five minutes earlier. **No grader
may read it as this item's or `D6RF`'s `REF_off` arm.** Its `rc=2` is nonetheless a real physics
finding and is the origin of `D6RF-BLOCKING-1`.

> **A CORRECTION TO A FIGURE, RECORDED BECAUSE IT WAS CAUGHT BEFORE IT TRAVELLED.** The supervisor's
> first reading of that total was **380.8** core-min, from a regex that matched `cap_core_min=380.0`
> as well as `core_min=`. He caught it himself before it left his hands. **A sum is only as good as
> its word boundary** — the same defect this item's own driver was driven against.

**`verification/queue/dafoam/launched/D6RF_chain.json` IS LEFT EXACTLY AS IT IS.** It carries
pre-ADDENDUM-2 pins. **It is the historical record of what the daemon actually launched, and
rewriting a launched row falsifies history.** Registered here so a reader meeting those stale pins
knows why they are stale.

---

## 5. INSTRUMENTS — the md5 table

| file | md5 | role |
|---|---|---|
| `d6rf2_opt_runScript.py` | **`137539e0a99be27f27fdb69e063b2a87`** | the repaired producer — **1 prose substitution, no executable byte** |
| `d6rf2_fd_endpoint.py` | **`0ce81a0b038abe12728b5b062e4420df`** | the FD instrument, re-pinned |
| `d6rf2_ref_off.py` | **`25f532e01156d8bd93458b23e1471d0a`** | the off-design instrument, re-pinned |
| `d6rf2_endpoint_physical.py` | **`6e5fa9f9c2048b0665593282f62ba3dc`** | the endpoint repair wrapper, re-pinned |
| `d6rf2_anchor_gate.py` | **`e34c0cb62df30e7a1565b896d07a32e6`** | **`G-ANCHOR`**, the new pre-compute gate |
| `d6rf2_units_assert.py` | **`34f8b79b96cc17d28d42ffd9ebc1874f`** | the units gate, `D6RF`'s, with the §5a repair |
| `d6rf2_endpoint_locus.py` | `341189ca866f302a7e1bba8eefad3a57` | **byte-identical to `D6RF`'s** |
| `d6rf2_derive.py` | **`bb6ea17332ec39d7479b200e28edba4f`** | the deriver |
| `d6rf2_selftest_evidence.txt` | **`c1fc50112f5b8199149209734cb7f098`** | seven drives |

Staged unchanged under `D6R`'s / D4's own md5s: `d6r_extract_endpoint.py` `1743dd42…`,
`d4_extract_endpoint.py` `ee7d3c99…`, `d4_opt_runScript.py` `2906d52a…`, `d4_endpoint_locus.py`
`e63df184…`, `d4_endpoint_physical.py` `74c35c80…`.

**SEVEN DRIVES, ZERO CONTAINERS:** `G-ANCHOR` **6/6**, units **25/25**, locus **30/30** — each under
`python3` **and** `python3 -O` — plus the deriver re-driven, re-asserting every substitution.

### 5a. ⚠ A DEFECT IN THIS ITEM'S OWN SELF-TEST, FOUND BY DRIVING IT AND FIXED BEFORE THE FREEZE

On its first drive `d6rf2_units_assert.py --selftest` reported **`0/25 PASS`**. Not one leg was
wrong: the self-test **spawned a hard-coded filename**, `d6rf_units_assert.py`, which stopped
existing at the rename into this item, so every subprocess errored. **A self-test that cannot find
itself reports total failure for a reason that has nothing to do with the thing it tests.**
Repaired by resolving the path from `__file__`, which cannot drift on a rename; re-driven **25/25**
under both interpreters. **It is recorded rather than quietly fixed, because a `0/25` that a lane
explains away instead of reading is how a broken instrument gets a clean bill.**

---

## 6. WHAT IS OUTSTANDING BEFORE THIS ITEM MAY BE ENQUEUED

**`d6rf2_run_arm.sh`, `d6rf2_chain_driver.sh` and `d6rf2_grade.py` ARE NOT WRITTEN.** They are
derived from `D6RF`'s — which now carry the ADDENDUM 2 vacuous-zero repair, the ADDENDUM 3
compressed-field repair and the self-test safety gate — by an enumerated substitution set on the
instrument names and pins, plus **one addition: `G-ANCHOR` is invoked by the launcher at staging,
before any container.** They land as a **dated pre-compute addendum**, and the condition is stated
and checked by execution: **the run root does not exist** (asserted above, and to be re-asserted).

**No queue row may be filed and no container may start until that addendum lands** carrying their
md5s, a **driven** `d6rf2_guard_selftest.py` with a container census before == after and zero
containers created, and the every-guard-precedes-every-destructive-step assertion with line numbers
recomputed from the file. **Nothing in §0–§5 changes when it lands.**

---

## 7. WHAT THIS ITEM MAY NOT CONCLUDE

* **Nothing that repairs `D6RF`'s or `D6R`'s verdicts.** `D6RF`'s `P2` MISSED and stays missed.
* **No claim that the anchor repair makes the arms run.** It removes one refusal, measured. **No
  container has ever run `F_mp` or `REF_off` at any point in this lineage**, and `L-316` binds: a
  self-test proves the **instrument**, never the **case**. **The first real container is still the
  first evidence about the case.**
* **No claim about the SHIPPED toolchain** — PATCHED-only, `D6RF` §6 inherited.
* **No GCI**; no grid family exists here.
* **A `GATE FAIL` or a `NOT A RESULT` here is a result and is reported as one.**

**`CLAUDE.md` check-1 and check-4 are the SUPERVISOR'S and this lane claims neither.** Enqueueing is
not authorisation.

---

# ADDENDUM 1 — 2026-09-03, PRE-COMPUTE. The launcher, the driver and the grader, derived rather than written, with `G-ANCHOR` invoked at staging before any container

**Version 1.1.** **Lines whose number changed above this section: 0.**

**PRE-COMPUTE, condition CHECKED BY EXECUTION:**

    ROOT_ABSENCE_RE_ASSERTED_BY_EXECUTION utc=2026-09-03T19:51:25Z
      /home/ubuntu/certonomous-runs/CURRICULUM-D6RF2-a2-wing-multipoint-fd=ABSENT

**0 core-min, no container, NOT ENQUEUED.** **Nothing in §0–§7 moves.** This addendum adds only the
machinery §6 named. **No gate, threshold, band, cap, label, prediction or cost is altered.**

## A1.1 DERIVED, NOT WRITTEN — and the reason is that re-typing would re-open every lesson

`d6rf2_derive_launcher.py` derives the three files from **`D6RF`'s repaired bytes** by an enumerated
substitution set, every substitution asserted **present-then-absent**, plus one addition asserted
**absent-then-present**. **Anything not in the set is `D6RF`'s bytes.** What that preserves, and what
re-typing would have put at risk:

* the **`.gz`-tolerant `field_path` / `assert_field`** helper with **no unrepaired call site** —
  four field-name sites plus the two `points.gz` sites (`D6RF` ADDENDUM 3);
* **`count_src_entries` returning `UNMEASURED`, never `0`**, and S4 refusing on `UNMEASURED` *and* on
  `0` — the vacuous-pass repair (`D6RF` ADDENDUM 2);
* the **age datum resolved by name and asserted a non-empty integer** before use;
* every guard's evidence line **naming its own trip count**;
* the **units gate at both call sites**, rc 7 / rc 77 distinct, and the launcher refusing to build an
  arm command that lacks it;
* **H5 and aggregate that HOLD and never refuse to launch**;
* **`rc` captured inside the wrapper**, `docker inspect` read **before** `docker rm`;
* exactly one `sudo -n rm -rf "$WORK"`, every guard preceding it, and `F_mp` **refusing** on a stale
  arm directory rather than removing one;
* and the **safety precondition, not a graded leg**: no launcher-invoking test can fire against a
  real existing root — the gate at the head of the self-test *and* the raise inside `run_launcher()`.

**A DISCIPLINE THE DERIVER ENFORCES AND THIS ITEM ADOPTS: an undeclared substitution that matches
nothing ABORTS.** A token that legitimately appears in only one of the three files must be
**declared optional at the call site**, and an absent optional is **printed**, never passed over.
*A silent no-op rename is the same disease as a vacuous pass, in a different costume.*

## A1.2 THE ONE STRUCTURAL ADDITION — `G-ANCHOR` at staging

The launcher md5-checks the gate, then runs it **over the arm directory's own staged bytes**, so it
checks what the container will actually read. **A refusal is rc 3 and NO CONTAINER IS CREATED.**
The gate already refuses at run time inside the consumers; invoking it at staging is what turns
*"this would have refused after a launch"* into *"this refuses before one"* — which is the whole
content of `D6RF-BLOCKING-1`.

**Placement asserted by RECOMPUTED line numbers, read from the derived file rather than predicted:**
the gate's md5 check at **623**, `G-ANCHOR` invoked at **624**, its OK line at **630**, the age datum
at **631**, the first `docker run` at **726**. From the self-test's own recomputation: guards end
**293**, the first executable recursive remove is at **486**, the first `docker run` at **726** —
**every guard precedes every destructive step, and the destructive step precedes the container.**

> **A CORRECTION MADE BEFORE THIS FILE WAS COMMITTED, RECORDED BECAUSE IT IS THE HOUSE DEFECT.** The
> first draft of this paragraph carried **480 / 500 / 486** — numbers this lane had *estimated from
> the shape of the edit* rather than read from the derived file. They were wrong. They were caught by
> reading the file before the commit, and the measured values above replace them. **A line number
> quoted without being read is the same error class as a residual quoted outside its basis**, and
> this family has now paid for it enough times to write it down.

## A1.3 THE PINS

| file | md5 |
|---|---|
| `d6rf2_run_arm.sh` | **`01e034e1c611e7fc4f0f4e31d3e34511`** |
| `d6rf2_chain_driver.sh` | **`5818d2ed385d46f5ec053493c052b7a2`** |
| `d6rf2_grade.py` | **`32a539780e34fe6d7945b7e301badc0f`** — **THE GRADING PATH** |
| `d6rf2_guard_selftest.py` | `ab9ed104794ac4e64f57f6a9b6dbeca3` |
| `d6rf2_derive_launcher.py` | `c798ee6d5391e47c7db13e7561f28df2` |
| `d6rf2_launcher_evidence.txt` | `979f17093fb6cb01b326f2baf746d050` |

**THE PIN CHAIN IS EXECUTABLE AND ABORTS A FIRE:** the driver asserts the launcher's md5 **twice per
fire**; the launcher asserts the **gate's** md5 and the **eleven** staged-instrument md5s before any
container and again inside each arm directory; and the grader verifies its own frozen set against
`git cat-file blob HEAD:` at execution — re-pointed to **this item's** paths, with the gate and the
repaired producer added to that set, so it cannot verify `D6RF`'s freeze and pass on the wrong one.

## A1.4 DRIVEN — 97/97, A FULL PASS, WITH NOTHING SKIPPED

| drive | result |
|---|---|
| `d6rf2_derive_launcher.py` re-driven | **OK**, every substitution re-asserted, **14/14 cross-checks** |
| `d6rf2_guard_selftest.py` under `python3` | **97/97 PASS** |
| `d6rf2_guard_selftest.py` under `python3 -O` | **97/97 PASS** |
| `d6rf2_anchor_gate.py --selftest` under `python3` | **6/6 PASS** |
| `d6rf2_anchor_gate.py --selftest` under `python3 -O` | **6/6 PASS** |

**ZERO CONTAINERS CREATED**, census before == after, no `d6rf2_` container has ever existed, and the
run root is asserted **still absent after every drive**. **This is a full pass and is cited as one:
`0` legs NOT RUN**, because the run root is absent and the launcher-invoking legs were therefore
safe to drive — the precondition doing its job in the permitting direction.

**The 14 cross-checks, so the number is not the claim:** no D6R producer md5 survives anywhere; no
single-`f` `d6rf_` token survives; the launcher invokes `G-ANCHOR`; `G-ANCHOR` precedes the age datum
and the first `docker run`; the driver pins the derived launcher; the launcher pins the gate; the
`.gz` helper, `count_src_entries` and the age-datum integer assert all survived; the units gate is at
both call sites; exactly one `sudo -n rm -rf "$WORK"`; H5 and aggregate HOLD; `docker inspect` before
`docker rm`.

## A1.5 TWO DEFECTS IN MY OWN DERIVATION, FOUND BY DRIVING IT AND FIXED BEFORE THE FREEZE

1. **The derived self-test's `U27` FAILED at first, 96/97.** Its regex spelled the units gate as
   `d6rf_units_assert\.py` — **escaped** — and the rename substitution matched only the unescaped
   form, so the check for the gate's second call site was looking for a filename that no longer
   existed. **A renamed instrument whose test still names the old spelling reports a defect that is
   not there** — the mirror of `D6RF`'s `0/25`, where a rename made a test report failure for a
   reason unrelated to what it tests. Repaired and re-driven **97/97**.
2. **Three substitutions I first declared mandatory are legitimately absent from one of the three
   files** (`d6r_cmd.sh` is the launcher's only; the shell `ITEM=D6RF` form is not the grader's,
   which uses `ITEM = "D6RF"`). The deriver **refused** rather than proceeding, and each was
   **declared optional at the call site** rather than the check being loosened. The refusal text is
   registered: *"if that is legitimate it must be DECLARED optional, not discovered."*

## A1.6 THE HARDENING NOTE — DECLINED, AND WHY

The supervisor offered, *"if it is free when you touch the file"*, an assertion that
`REQUIRED_SYMBOLS` and `READERS` are non-empty in `d6rf2_anchor_gate.py`. **It is not free: that file
is FROZEN at `3af45c05` and its md5 is pinned in §5.** Editing it to add an assertion would break the
freeze this item's own §5 records, for a property that is already visible in the source as two
literal non-empty tuples and whose trip counts the gate **prints on its pass line**. **It is left
unchanged, and the reason is recorded rather than the change made quietly.**

## A1.7 WHAT REMAINS BEFORE A QUEUE ROW

**Check 1 on the launcher is the supervisor's**, and no queue row is filed until he records it.
Nothing here is enqueued, nothing is sent, and **§7 stands verbatim: removing one refusal is not
evidence the arms run. No container has ever run `F_mp` or `REF_off` in this lineage; `L-316` binds;
the first real container is the first evidence about the case.**

---

## ADDENDUM — 2026-09-03T22:41Z — `G-DELIVERY`: THE GATE EXISTED AND WAS CORRECT; IT WAS NEVER DELIVERED

**Dated pre-compute addendum.** `F_mp` and `REF_off` have **still never run a
container in this lineage** — the 22:13:11Z launch aborted at **70 s**,
`rc=4`, **before any container**, at host-side staging. **`spent_before_arm =
0.000`.** So §7 stands verbatim and this addendum is written while the item is
still at zero solver compute.

**PRE-COMPUTE CONDITION, BY EXECUTION IN THE AMENDING INVOCATION:** the
registered run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF2-a2-wing-multipoint-fd/` is
**ABSENT** — archived by `mv` below, and asserted absent afterwards.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Caps
480.0 / 190.0, deadlines 7110 / 2760 s, `ranks` 4, the patched toolchain row,
`G-ANCHOR` itself, the units gate and its two call sites, and every verdict
label stand exactly as frozen. **Staging a file, and asserting that staged files
arrived, move nothing** — and an assertion that can only ever *refuse more* is
never a weakening.

### The defect, measured

`d6rf2_anchor_gate.py` **exists** in the case directory (11,067 bytes) and is
staged into `$BASE` by `d6rf2_chain_driver.sh:88-94`. **It was never copied into
the ARM directory `$WORK`**, where `d6rf2_run_arm.sh:623` md5-checks it and
`:624` executes it. Ten sibling instruments are copied into `$WORK`; that one was
missed. The launch aborted at `md5sum: .../F_mp/d6rf2_anchor_gate.py: No such
file or directory` / `ABORT G-ANCHOR gate md5`.

**BOTH ARMS WERE AFFECTED, NOT ONLY `F_mp`.** The reference at `:623`/`:624` is
**unconditional** — outside the `if [ "$ARM" = "F_mp" ]` block that spans the two
per-arm staging lists — and **neither** list stages it. `REF_off` would have
failed identically. **This is not one arm's staging bug; it is a required file no
arm delivers.**

**`G-ANCHOR` ITSELF IS NOT AT FAULT AND IS NOT EDITED.** It is correct, it is
md5-pinned, and it was read as a diff and signed off. **The gate was not wrong;
it was not there.** The supervisor records the reciprocal gap in his own practice:
the four §3 checks read the *instrument*, and **nothing in them reads the path
between the instrument and the run.**

### The repair — the class, not the file

**1. The file is staged**, into **both** arms' lists, md5-asserted **on both
sides of the copy**, the same shape `A1WRT`'s `S5b`/`S5c` proved in a live launch
the same evening. `F_mp` now stages **seven** instruments and `REF_off` **nine**.

**2. `G-DELIVERY`, and it DERIVES its requirement rather than restating it.** A
hand-written list of required files is what produced this defect and a second
hand-written list would produce the next one. **The launcher already states what
it needs** — every `$WORK/<file>` it md5-checks or executes **is** the
requirement — so the set is read out of **this launcher's own bytes at run time**,
never maintained as a parallel copy of the answer. It is **branch-aware** (the
arm block is located **by pattern, never by line number**), and it **fails closed
three ways**: the shape cannot be located → refuse; the derived set is **EMPTY** →
refuse, because a reader that requires nothing has not proved delivery but failed
to read; any required file absent → refuse **naming each missing file and the
directory it was expected in**.

**3. A distinct exit code, `8`, registered in the launcher's own table.** `rc=4`
on a bare `md5sum -c` says an md5 failed and says **nothing about delivery**.

**THE DERIVED SETS, as the guard computes them from the launcher's real bytes:**
`F_mp` **7** — `d6r_extract_endpoint.py`, `d6rf2_anchor_gate.py`,
`d6rf2_endpoint_locus.py`, `d6rf2_endpoint_physical.py`, `d6rf2_fd_endpoint.py`,
`d6rf2_opt_runScript.py`, `d6rf2_units_assert.py`. `REF_off` **9** — the four
`d4_*`, `d6rf2_anchor_gate.py`, `d6rf2_endpoint_locus.py`,
`d6rf2_opt_runScript.py`, `d6rf2_ref_off.py`, `d6rf2_units_assert.py`.

**DRIVEN BOTH WAYS, ZERO CONTAINERS:** `F_mp` gate missing → `REFUSE-MISSING 1
of 7` naming it; `F_mp` present → `OK 7`; **`REF_off` gate missing →
`REFUSE-MISSING 1 of 9`, which is the measurement proving both arms were
affected**; `REF_off` present → `OK 9`; six missing → `REFUSE-MISSING 6 of 7`
naming all six; a file with no arm branch → `REFUSE-SHAPE`. The launcher's `case`
branch drives 4/4: `OK`→0, `REFUSE-MISSING`→8, `REFUSE-SHAPE`→8, `REFUSE-EMPTY`→8.
*The two halves were driven separately, because `${BASH_SOURCE[0]}` binds to a
sourced block rather than to the launcher — and the guard REFUSED with
`REFUSE-SHAPE` when that was attempted, which is the fail-closed path firing on a
real mistake.*

### The run root is ARCHIVED, never deleted

`mv` to
`CURRICULUM-D6RF2-a2-wing-multipoint-fd_ABORTED_G-ANCHOR_20260903T221421Z`.
**Preservation asserted by count across the move: files 370 → 370, directories
84 → 84, bytes 44,745,593 → 44,745,593 — all three identical.** It holds
`ledger.txt`, `STATUS.chain` (`chain=STOPPED_AT_FIRST_NONZERO arm=F_mp rc=4
not_run=[REF_off]`), `CHAIN_DONE`, the staged `F_mp` tree and two
staging-evidence artefacts. **The registered run root is now absent, so
refuse-on-stale-directory stands unweakened. No `rm -rf` was executed.**

### Instrument pins

| instrument | md5 |
|---|---|
| `d6rf2_run_arm.sh` | **`eb4ad36dd03f466f80024db57859e8df`** — repaired; supersedes the pin in the launched queue row |
| `d6rf2_anchor_gate.py` | `e34c0cb62df30e7a1565b896d07a32e6` — **UNCHANGED. It was never the problem.** |
| `d6rf2_chain_driver.sh` | `5818d2ed385d46f5ec053493c052b7a2` — **UNCHANGED** |

**NOT RE-FIRED, AND NOT TO BE RE-FIRED UNTIL THE SUPERVISOR HAS READ THE CHANGED
HUNKS AS A DIFF.** §7 stands verbatim: removing one refusal is not evidence the
arms run, no container has ever run `F_mp` or `REF_off` in this lineage, and
**the first real container is the first evidence about the case.**

---

## ADDENDUM — 2026-09-03T22:49Z — THE `G-DELIVERY` REPAIR BROKE A PIN IT DID NOT UPDATE, AND THE ITEM'S OWN GUARD CAUGHT IT BEFORE THE RE-FIRE

**Dated pre-compute addendum. Still zero solver compute: no container has ever run
`F_mp` or `REF_off` in this lineage.** Run root asserted **ABSENT by execution**
in the amending invocation. **NO GATE, THRESHOLD, CAP OR LABEL MOVES** — caps
480.0 / 190.0, deadlines 7110 / 2760 s, ranks 4, the patched row, `G-ANCHOR`, the
units gate and its two call sites all stand exactly as frozen.

### What happened

The `G-DELIVERY` repair changed `d6rf2_run_arm.sh`
(`01e034e1c611e7fc4f0f4e31d3e34511` → `eb4ad36dd03f466f80024db57859e8df`).
**`d6rf2_chain_driver.sh:54` pins that md5, and the repair did not update it.**
The driver asserts the pin **twice per fire** — `:79` before staging and `:152`
before each arm — so the re-fire would have **aborted at `rc=4` before any
container**, for the third consecutive time and for a third distinct reason.

**IT WAS CAUGHT BY THIS ITEM'S OWN GUARD SUITE, NOT BY A READER.**
`d6rf2_guard_selftest.py` control **`U37` — "the driver's pinned launcher md5 ==
the launcher on disk" — returned `FAIL`, `rc=1`, under BOTH `python3` and
`python3 -O`**, on a pre-fire drive. **Verified as caused by the repair rather
than pre-existing:** the pin matched the launcher **exactly** at the repair
commit's parent, and differs only after it.

### The class, because it is the same one twice in one file

**The repair fixed "a file the launcher reads was never delivered" and then
committed "a file another file asserts about was changed without updating the
assertion".** Both are the same shape — **an artefact and a statement about it
drifting apart** — and `CLAUDE.md` rule 14 already names it: *a lesson is not
applied until EVERY call site asserts it.* **Updating the assertion is the second
half of the repair and is not optional.** The repair is only complete when
nothing that speaks about the changed file still speaks about the old one.

### The repair, and what it does not touch

`MD5_LAUNCHER` re-pinned to `eb4ad36dd03f466f80024db57859e8df`, with the reason
recorded at the constant itself so the next reader does not have to reconstruct
it. **Nothing executably pins `d6rf2_chain_driver.sh`'s own md5** — checked by
search across the case's shell and python before editing — so this change breaks
no further assertion.

**RE-DRIVEN AFTER THE FIX, both interpreters, zero containers:**
`D6RF2_GUARD_SELFTEST 97/97 PASS`, **0 FAIL, 0 NOT RUN**, `rc=0` under `python3`
and `python3 -O`; `U37` **PASS**. `G-DELIVERY` re-driven on the launcher's real
bytes and unchanged by this edit: `F_mp` gate missing → `REFUSE-MISSING 1 of 7`,
gate present → `OK 7`.

### Pins

| instrument | md5 |
|---|---|
| `d6rf2_chain_driver.sh` | **`a3e57f2bdb741b0ff4b3151759d07105`** — supersedes `5818d2ed385d46f5ec053493c052b7a2`, which the previous addendum recorded as UNCHANGED and which **that addendum's table is therefore now wrong about; this line is its correction** |
| `d6rf2_run_arm.sh` | `eb4ad36dd03f466f80024db57859e8df` — unchanged by this addendum |
| `d6rf2_anchor_gate.py` | `e34c0cb62df30e7a1565b896d07a32e6` — unchanged throughout |

**NOT FIRED.** The supervisor authorised a re-fire on the state as he read it;
**the item could not have fired in that state**, and firing on an authorisation
whose precondition is measured false is not obedience. **§7 stands verbatim: the
first real container is the first evidence about the case.**

---

## ADDENDUM — 2026-09-03T23:03Z — `G-DELIVERY` BECOMES A CLOSURE, AND IT FINDS A SECOND INSTANCE NOBODY HAD LOOKED FOR

**Dated pre-compute addendum. Still ZERO solver compute across three fires:
`spent_before_arm=0.000` on every one, and no container has ever been created in
this lineage.** Run root asserted **ABSENT by execution**. **NO GATE, THRESHOLD,
CAP OR LABEL MOVES** — caps 480.0 / 190.0, deadlines 7110 / 2760 s, ranks 4, the
patched row, `G-ANCHOR`, the units gate and its two call sites all stand as
frozen. §7 stands verbatim.

### The third abort, and what it proved about the second repair

The 22:54:37Z fire reached `G-ANCHOR` — **the furthest this item has ever got** —
and refused at **`rc=3`**, 69 s in, on the gate's own traceback:
`FileNotFoundError: .../F_mp/d6rf2_ref_off.py`, raised inside
`d6rf2_anchor_gate.py:130` iterating its own `READERS`.

**`G-DELIVERY` had passed immediately before, naming its seven.** So the guard was
not wrong — **it was one level too shallow.** `d6rf2_anchor_gate.py:53` declares
`READERS = ("d6rf2_fd_endpoint.py", "d6rf2_ref_off.py")`, and **the launcher
never mentions `d6rf2_ref_off.py` at all**: it is named only by the gate's own
tuple. The derivation enumerated one level; the dependency was two.

**AND IT IS THIS FAMILY'S SIGNATURE DEFECT AGAIN: one entry of a two-element
tuple was staged and its sibling was not.** Each branch reads as correct alone,
which is why no reader catches it and only execution does.

### The repair — a closure, not another level

**`d6rf2_ref_off.py` is NOT added to a list.** A hand list is what produced the
defect twice; a third would leave the class open one level further down.

1. **Level 0** is unchanged: what the launcher md5-checks or executes at `$WORK`,
   branch-aware, arm block located by pattern.
2. **Each derived instrument is parsed with `ast`** and its **module-level `.py`
   filename constants** — `READERS`, `PRODUCER`, `EXTRACTOR`, `RUNSCRIPT`,
   `STAGED_PRODUCER` and anything of that shape — are read **from the file's own
   bytes**, never from a pattern maintained in the guard.
3. **Iterated to a FIXED POINT**, bounded at 8 rounds, **refusing on
   non-convergence** rather than silently stopping at the bound, *because a set
   truncated at a depth is not a closure*.
4. **COMPLETENESS IS ASSERTED AGAINST THE DISK, NOT AGAINST THE CLOSURE.**
   Asserting the fixed point against itself would be **tautological** — the exact
   vacuous-predicate shape this lab has now catalogued three times. Instead:
   **every `.py` actually present in `$WORK`, including files that arrived with
   the base copy and were never derived, must reference only `.py` files that are
   also present.** That can fire, and on the 22:55:46Z state it does.
5. **The closure's requirements are STAGED FROM `$BASE`**, whose twelve
   instrument md5s the driver asserts before any arm runs, with the arm-side copy
   asserted **byte-identical by `cmp`** — so the requirement is met from verified
   bytes and still never from a second hand list. **Then the derivation is re-run
   as a READ-BACK**: write, read back, assert, the same shape as `S5b`/`S5c`.

### ⚠ WHAT THE CLOSURE FOUND THAT NOBODY HAD LOOKED FOR

**`REF_off` IS MISSING A FILE TOO, AND IT IS THE OTHER ENTRY OF THE SAME TUPLE.**
Its level-0 set of nine contains `d6rf2_ref_off.py` but **not
`d6rf2_fd_endpoint.py`**, which `d6rf2_anchor_gate.py` also reads. **`REF_off`
would have aborted at `G-ANCHOR` exactly as `F_mp` did, on the other reader, and
no one had noticed** — the arm never ran because the chain stops at the first
non-zero. **Measured, not argued:** the closure returns
`MISSING 1 of 10 ... d6rf2_fd_endpoint.py` for `REF_off`.
**A detection catches the level you thought of; a closure catches the level you
did not.**

### Driven, both directions, zero containers — twelve legs

| leg | condition | result |
|---|---|---|
| 1 | the **exact 22:55:46Z state** (the seven the old guard passed) | `MISSING 1 of 8 … d6rf2_ref_off.py` |
| 2 | + `d6rf2_ref_off.py` | `OK 8 (7 level-0, 1 by closure)` |
| 3 | **`REF_off`'s own nine** | `MISSING 1 of 10 … d6rf2_fd_endpoint.py` — **the new finding** |
| 4 | a staged file referencing an absent one | `REFUSE-DANGLING … d6r_fd_endpoint.py -> d6r_opt_runScript.py` |
| 5 | an 11-deep declaration chain against a bound of 8 | `REFUSE-NONCONVERGENT` |
| 6 | a required file that does not parse | `REFUSE-UNPARSEABLE … UNMEASURED, not assumed empty` |
| 7 | a file with no arm branch | `REFUSE-SHAPE` |
| 8 | the arm-branch opener altered | `REFUSE-SHAPE` |
| 9 | arm branch present, every `$WORK` reference stripped | `REFUSE-EMPTY` |
| 10 | `MISSING` → stage from `$BASE` → read-back | `rc 0`, staged and **asserted byte-identical** |
| 11 | required, and **absent from `$BASE` too** | `rc 8`, refusing by name |
| 12 | the staged copy does not land intact | `rc 8`, "NOT byte-identical" |

Every plant asserted to have landed before its verdict. **The two halves are
driven separately — `${BASH_SOURCE[0]}` binds to a sourced block rather than to
the launcher — and that split is reported rather than an end-to-end run implied.**

### The pin, applied without waiting to be caught

The repair moved the launcher's md5 again
(`eb4ad36d…` → **`01bc529b5a96f7589ebd8d3941200d1c`**), and
`d6rf2_chain_driver.sh:54` pins it. **It was updated as part of the repair this
time rather than after control `U37` caught it** — the previous addendum's whole
lesson. Driver md5 accordingly **`686e1cbcaa837229a40c145764c6d865`**,
superseding `a3e57f2bdb741b0ff4b3151759d07105`.

**Guard suite after the repair: `D6RF2_GUARD_SELFTEST 97/97 PASS`, 0 FAIL, rc 0
under both interpreters, `U37` PASS and `U9` PASS.** *(U9 — "the registered run
root is absent" — FAILED on a drive taken before the archive and PASSED after it:
a live precondition check, not a decoration.)*

### The run root is archived, never deleted

`mv` to `…_ABORTED_G-ANCHOR-READERS_20260903T225546Z`. **Preservation asserted by
count: files 371 → 371, dirs 84 → 84, bytes 44,759,156 → 44,759,156, all three
identical.** It holds `F_mp_launch.out` with the gate's full traceback,
`STATUS.chain`, `STATUS.F_mp` and the staged `F_mp` tree. **No `rm -rf`.**

**NOT RE-FIRED. The supervisor reads the changed hunks as a diff before any
re-fire. `F_mp` and `REF_off` remain the only genuinely unrun physics in this
family, and no container has ever run either in any lineage.**

---

## ADDENDUM — 2026-09-03T23:06Z — THE TWO `stage_say` LINES IN `G-DELIVERY` ARE LOAD-BEARING AND MAY NOT BE TIDIED AWAY

**Dated pre-compute addendum, appended before the fourth fire. Still ZERO solver
compute in this lineage.** Run root **ABSENT by execution**. **NO GATE,
THRESHOLD, CAP OR LABEL MOVES.**

### The condition on which the staging behaviour was accepted

`G-DELIVERY` both **asserts** delivery and, where the closure requires a file the
arm branch's hand list did not stage, **supplies it** from `$BASE` and re-runs
the derivation as a read-back. **The dafoam-supervisor accepted that on one
explicit condition, and the condition is registered here so a successor cannot
retire it by accident.**

> **The objection was never the staging. It was the SILENCE.** A guard that can
> repair the condition it checks will **mask a staging defect**: if an arm
> branch's list is wrong, `G-DELIVERY` quietly fills it in and nobody ever
> learns the list was wrong.

**What answers the objection is that it is LOUD**, and it is loud in exactly two
lines of `d6rf2_run_arm.sh`:

| line | text | why it is load-bearing |
|---|---|---|
| the `MISSING` branch | `D6RF2_G_DELIVERY closure requires files the arm list did not stage: $NEED` | **names the arm-branch omission, every fire, by filename** |
| the per-file line | `D6RF2_G_DELIVERY staged $f from $BASE, asserted byte-identical` | **records that the guard, not the arm list, delivered it** |

**⚠ IF EITHER LINE IS DROPPED, SOFTENED, DOWNGRADED TO A DEBUG CHANNEL OR MADE
CONDITIONAL, `G-DELIVERY` BECOMES A SILENT REPAIR AND THE SUPERVISOR'S OBJECTION
RETURNS IN FULL.** They are not logging. They are the reason a self-repairing
guard is admissible at all, and a future edit that removes them removes the
grounds on which this design was accepted — **not merely some output.** A
reader tidying the launcher's `stage_say` calls should treat these two as gates.

**The standing requirement that follows:** a file `G-DELIVERY` had to supply is a
**defect in the arm branch's staging list**, and it is to be repaired there — not
left to the guard indefinitely on the grounds that the guard handles it. The
guard is the backstop; the list is the mechanism.

### Why `$BASE` is the source and not a second hand list

`d6rf2_chain_driver.sh` asserts **twelve instrument md5s at `$BASE`** before any
arm runs, so `$BASE` is already the md5-verified source of truth. The arm-side
copy is asserted **byte-identical by `cmp`**, and the derivation is then re-run
against the new disk state. **Write, read back, assert** — the shape proven in a
live launch earlier tonight at `S5b`/`S5c`. **No filename-to-constant map is
maintained anywhere, which is the whole point.**
