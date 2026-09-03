# VR3-R2 — THE ansys CARDINALITY-GUARDED SITES: IS EACH SAFE **FOR THE REASON CLAIMED**?

**Second registration. Frozen before any measurement under it.**

**This is not a repair of a landed verdict.** VR3's `PASS` was withdrawn to **`NOT A RESULT`**
by verification-supervisor, so no valid verdict exists to repair, and `§2d.1` is not engaged.
`VR3_PREREGISTRATION.md` and `verification/credibility/vr3_guard_set_attribution.py` are
**frozen and untouched** (rule 6). VR3-R2 is a new registration with a new driver at a new
path: `verification/credibility/vr3r2_guard_set_attribution.py`.

---

## 1. WHAT VR3 GOT WRONG

Two defects, both read at source. A later reader is entitled to know why a second
registration exists.

### (a) POPULATION MISMATCH — the gate and the driver measured different things

`VR3_PREREGISTRATION.md:19` registers the gate over **"each of the 11 sites"** — ansys's
cardinality-guarded SAFE set less `grade_vmfl076` — with `G1`/`G2`/`G3`/`G4` named **per
site** (`:20-24`).

`vr3_guard_set_attribution.py:62-72` does not read that population. It walks **every**
`grade_*.py` under `cases/ansys_verification` and totals **every** wildcard-bound ordered
read, printing at `:73` *"G1/G2/G3 applied to every wildcard-bound ordered read in every
ansys grader"*. Driven today it returns **60 sites — 16 GUARDED, 44 UNGUARDED**.

**A different quantity over a different population.** The registered question — how many of
the registered sites resolve UNGUARDED — was never answered, and remains `NOT MEASURED`.

### (b) THE FAILING VERDICT WAS UNREACHABLE IN THE IMPLEMENTATION

`vr3_guard_set_attribution.py:76-79` is the whole of the driver's branching:

- the **only** non-`PASS` return is `tot['GUARDED'] == 0 and tot['UNGUARDED'] == 0`;
- the string `GATE FAIL` **does not occur anywhere in the file**;
- the `unguarded` list accumulated at `:72` is **never read**.

The registered failing verdict (`:27-28`, *"GATE FAIL = any site resolves to UNGUARDED"*)
**could not be emitted under any input**. Its `PASS` therefore carried no information: it is
`§2p`'s exact shape — *a pass that could not have come out any other way*.

---

## 2. THE POPULATION — STATED EXACTLY, AND DISCLOSED AS A RECONSTRUCTION

### 2.1 The list ansys's sweep produced does not exist on disk

`docs/LAB_STATE.md@c7176346` records the sweep as a table. Its **hazard** half is fully
enumerated — *"The nine: `VMFL002` (84, 207, 214), `VMFL004` (84, 206), `VMFL004-R2` (129,
318), `VMFL011` (84, 195), `VMFL011-R2` (178, 319), `VMFL011-R3` (178, 334), `VMFL021` (123,
131), `VMFL021-R2` (161, 169), `VMFL022` (123, 131)"* — **19 sites, by file and line.**

Its **SAFE** half is a **bare count**: *"SAFE — cardinality-guarded (`one_match`, refuses on
>1) | **12**"*. **No enumeration of those 12 exists** — not in that commit (which touched
only `docs/LAB_STATE.md`), not in `3c751f8a` (`docs/DEAD_LEVER_AUDIT.md` +
`ordering_key_census.py`), not in `docs/ansys_verification/`, not anywhere in the repository.
`DEAD_LEVER_AUDIT` §7.4 itself states the classification basis **conditionally** — *"if the
'12 cardinality-guarded SAFE' sites were classified by the presence of a `len(...) != 1`
refuse"* — so even the criterion is inferred, not recorded.

**The registered population is therefore a RECONSTRUCTION. It is not a transcription and is
nowhere treated as one.**

### 2.2 The reconstruction predicate, stated exactly

> A **site** is a binding `<name> = sorted(glob.glob(<pat>))` in a file matching
> `cases/ansys_verification/**/grade_*.py`, where `<pat>` resolves — inline, or through a
> string-valued name bound earlier in the same module — to at least one string literal
> containing a glob metacharacter (`*`, `?`, `[`), and where `<name>` is subscripted
> somewhere in the same module. Each binding is one site; a name rebound at three lines is
> three sites.
>
> A site is **cardinality-guarded (ansys's "SAFE")** iff `len(<name>)` appears in a
> comparison **anywhere in the module**; otherwise it is **HAZARD**.

The module-wide guard test is deliberately ansys's own — **crediting a guard anywhere in the
file with the safety of one binding is precisely the classifier defect under audit.** The
predicate reproduces the classification; §3 measures whether the classification is right.

### 2.3 The predicate is VALIDATED against the one enumerated half that exists

Applied to the ansys tree at `c7176346`, the predicate's **HAZARD** half returns **19 sites
in 9 files — the same 9 files, at the same 19 line numbers, that `docs/LAB_STATE.md@c7176346`
enumerates. 19/19, zero missed, zero extra.** An instrument that reproduces a fully-enumerated
half exactly is entitled to be believed on the complementary half.

### 2.4 The residual disagreement, disclosed and NOT reconciled

On the guarded half the predicate returns **14**, against ansys's bare count of **12**.
Every one of the 14 carries a genuine refuse-on-more-than-one comparison
(`len(hits) != 1` or `len(hits) > 1`), so the gap is **not** the guard operator.

**The two-site gap cannot be resolved, because the 12 were never enumerated.** The most
likely reading — and it is a reading, not a measurement — is that ansys's regex-based
site-finder missed two sites entirely, a failure mode that commit's own message records
twice (*"MY OWN first two scan patterns returned 0 on files already proven to carry the
shape"*). **This registration records the disagreement and proceeds on the reconstruction.
No claim below rests on the number being 12.**

### 2.5 STABILITY across the corpus growth — measured, not assumed

`cases/ansys_verification` grew from **40** to **53** `grade_*.py` files between `3c751f8a`
and HEAD. The site set is **identical** at both trees — same 33 sites, same files, same line
numbers, `old == new` exactly — while the two trees genuinely differ (33 differing entries
under `diff -rq`). The 13 newer graders route every read through a `one_match(...)` **call**
rather than a `sorted(glob.glob(...))` **binding**, so they contribute no site of this shape.
**The population is not drifting.**

### 2.6 THE REGISTERED POPULATION, N = 12

The 14 reconstructed cardinality-guarded sites, **less both `grade_vmfl076.py` sites**
(§7.4's exemplar, already read; note there are **two** files of that name — `VMFL076/` and
`VMFL076-R2/` — each contributing one site at `:677`, so the exclusion removes 2, not 1;
this is why N is 12 here where VR3 registered 11 from a count of 12).

All 12 are present at HEAD and located by the driver (12/12, no exception).

| # | site (path relative to repo root) | binding line | name |
|---|---|---|---|
| 1 | `cases/ansys_verification/VMFL001/grade_vmfl001.py` | 360 | `hits` |
| 2 | `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py` | 236 | `hits` |
| 3 | `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py` | 420 | `hits` |
| 4 | `cases/ansys_verification/VMFL005/grade_vmfl005.py` | 152 | `hits` |
| 5 | `cases/ansys_verification/VMFL019/grade_vmfl019.py` | 99 | `hits` |
| 6 | `cases/ansys_verification/VMFL050/grade_vmfl050.py` | 118 | `hits` |
| 7 | `cases/ansys_verification/VMFL050/grade_vmfl050.py` | 126 | `hits` |
| 8 | `cases/ansys_verification/VMFLGPU001/grade_vmflgpu001.py` | 249 | `hits` |
| 9 | `cases/ansys_verification/VMFLGPU001/grade_vmflgpu001.py` | 589 | `hits` |
| 10 | `cases/ansys_verification/VMFLGPU001-R2/grade_vmflgpu001_r2.py` | 274 | `hits` |
| 11 | `cases/ansys_verification/VMFLGPU001-R2/grade_vmflgpu001_r2.py` | 614 | `hits` |
| 12 | `cases/ansys_verification/VMFLGPU002/grade_vmflgpu002.py` | 278 | `hits` |

This table is the population. The driver carries it as a literal and **intersects** it with
HEAD: a registered site that cannot be located is `NOT A RESULT`, never a silent skip.

---

## 3. GATE (frozen) — G1/G2/G3/G4, PER SITE

For **each** of the 12 sites, a committed record stating:

- **G1** the ordered set that **decides the answer** — which `glob`/`listdir`, over what
  resolved pattern;
- **G2** the set each `len(...)` guard in that function actually **measures** — reported
  split into guards **attributed** to this binding (same enclosing function, after the
  binding, before any rebinding of the name) and **foreign** guards, each foreign guard named
  with its line, its enclosing function, and the pattern of the binding it actually measures;
- **G3** whether G1 and G2 are the **same set** — the discriminator, decided on **scope and
  dominance**, not on the mere presence of the name in a `len()` comparison somewhere in the
  module;
- **G4** the resulting class: **GUARDED** (an attributed cardinality guard measures the
  deciding set and precedes its first use), **REFERENCE** (numeric ordering key — reads the
  hard input correctly rather than refusing, `grade_vmfl076.py:669-685`'s shape), or
  **UNGUARDED** (no such guard; any guard present measures a different set).

---

## 4. THRESHOLD / LABEL (frozen)

- **PASS** — all 12 sites classified with G1–G3 named per site **and none resolves
  UNGUARDED**.
- **GATE FAIL** — **any** site resolves **UNGUARDED**. This would widen ansys's exposed
  candidate set beyond the ruled 19.
- **NOT A RESULT** — a registered site cannot be read or located at HEAD; **or** the
  population is empty; **or** the controls of §5 do not all pass.

**The failing verdict is reachable and its reachability is proved in the same run** (§5).

---

## 5. THE CONTROLS THE DRIVER MUST CARRY (frozen)

All four drive the **production** `classify_site()` and `verdict()` — never a copy
(`§2p.3(d)`) — and all run in the **same invocation** that produces the verdict, with their
outcome printed beside it. If any fails, the verdict is `NOT A RESULT` and no number in the
run is evidence.

1. **NEGATIVE / planted (CLAUDE.md rule 3, `§2p.3(e)`).** A synthetic grader carrying an
   UNGUARDED wildcard-bound ordered read, whose only `len()` guard lives in a **different
   function over a different set**, is planted and driven through the production path. The
   driver must classify it **UNGUARDED** and `verdict()` must return **GATE FAIL, rc 1**.
   *This is the reachability proof — the failing branch is executed, not asserted.*
2. **POSITIVE (`§2p.3(e)`).** A synthetic grader that **deserves** a pass — the guard measures
   the very set the subscript reduces — must classify **GUARDED** and must **not** produce
   GATE FAIL. *A refuser that refuses everything is indistinguishable from a correct one.*
3. **EMPTY-INPUT ARM (`§2p.2`).** An empty population must **REFUSE** — `NOT A RESULT`,
   rc 2 — never report clean.
4. **ABSENT-SITE ARM.** A registered site not locatable at HEAD must yield `NOT A RESULT`,
   never a silent skip.

**And a freeze arm, enforced by the driver itself:** the graded measurement refuses to run
unless this file is **committed at HEAD** and the working copy hashes equal to the committed
blob. A gate is only a gate if it was frozen before the measurement (rule 2).

---

## 6. COST (frozen)

**Zero solver compute.** Pure AST work, single rank.

| item | POINT ESTIMATE (prediction) | CAP (bound) |
|---|---|---|
| the graded driver run | **0.002 core-minutes** | **0.05 core-minutes** |
| the whole item, agent-session wall at 1 rank | **60 core-minutes** | **120 core-minutes** |

The point estimates are **predictions and are capable of being wrong**; the caps are bounds.
The run figure is grounded on the control invocation already driven at **0.03 s wall, 1 rank**
before this file was written — pre-compute calibration data, disclosed as such, not a
measurement of the graded run. The predecessor's `20.0` (`VR3_PREREGISTRATION.md:32`) was on
the agent-session basis; it is restated here on both bases so the two are comparable.

Dollars, if derived, are derived at the recorded `c7a.4xlarge` rate of **$0.0513/core-h** and
are **derived, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at
completion (rule 12).

---

## 7. NOT CLAIMED

- **Nothing here re-grades an ansys verdict.** `DEAD_LEVER_AUDIT` §7.3's finding stands: **no
  landed verdict is exposed**, because every hazard case produced exactly one start-time
  directory. This item can widen a **CANDIDATE** set; it can never move a **VERDICT**.
- **Nothing here disturbs ansys's hazard count.** The 19 in 9 files are ratified twice and
  reproduced a third time by this registration's own predicate. Only the *reason* the
  remainder were called safe is in question.
- **Nothing here claims the reconstructed population IS ansys's 12.** It is a reconstruction
  that agrees exactly on the enumerated half and disagrees by two on the half that was never
  enumerated (§2.4). That disagreement is disclosed in every place the population is named.
- **No repair is proposed or applied to any frozen grader.** Rule 2 bars a post-compute edit
  to a frozen comparator, and this item does not touch one.

---

## 8. WHAT IS MINE

Entirely verification's. This is a cross-team gate audit under the team's audit mandate. The
count is not in dispute — **only the reason is**, and a reason is what a later reader relies
on.
