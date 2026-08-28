# Unique selector rule — a filter that selects ONE thing must prove it selected one thing

**Status: SPEC, FROZEN AT ITS COMMIT. No code exists yet.** This document is written
**before** the implementation precisely so the implementation cannot be shaped to pass its
own test (`CLAUDE.md` rule 2's discipline applied to tooling). The commit that lands this
file is the freeze; the code that follows cites that sha, and any departure from what is
written here is a dated amendment at the foot, never an edit above it (rule 6).

**Owner:** cfd-supervisor. The three sites this document repairs are cfd's
(`verification/runs/F3_runs/successor_triple_2026-08-26/`).
**Provenance:** the defect class is `docs/LESSONS.md` **L-398** (`:16905` at HEAD) — cited,
not restated; read it for the mechanism. Verification routed the three sites to cfd on
2026-08-28. Every count, filename and file:line below was re-measured against the tree by
cfd lane **F3S** the same day. **Three statements in the routing brief were falsified on
that check** and are corrected in §2a rather than carried forward.

**This document adds no gate, no threshold, no band, no cap and no label.** It **widens**
the conditions under which a reader refuses. Widening is the safe direction; §5's negative
control exists anyway, because a widening that is really a disable looks identical from
outside.

> **REFERRAL, NOT A DECISION — for the chief.** The rule in §1 is written to be general and
> is worth applying beyond cfd, but **this document binds cfd's readers only.** Whether it
> becomes a lab-wide standard other teams' comparators must satisfy is not cfd's call to
> make for the lab.

---

## 1. The invariant

> **A filter written to select exactly one artifact must ASSERT that it selected exactly
> one, and must NAME the field it wants rather than describe it by accident.**

Two clauses, both required (§4 argues why neither substitutes for the other):

- **U — cardinality.** `len(cands) != 1` → **refuse, exit 2**. Never `[0]`, never `[-1]`,
  never "take the first and hope".
- **P — predicate.** The test is on the **field token**, not on the whole filename. For
  OpenFOAM's `surfaces`/`sets` writers the artifact is `<field>_<surfaceName>.<fmt>`, so the
  pressure file is the one whose **leading token before the first `_` is exactly `p`** —
  and, where the surface name is known to the reader, the one whose **full basename equals
  the constructed `p_<surfaceName>.raw`** (§3.3, the stronger form, recommended).

---

## 2. Why — the defect, and it is a MISREAD FIELD, not a missing file

`grade_f3s.py:239` selects the graded surface pressure with

```python
    cands = sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)
    path  = os.path.join(d, cands[0])
```

`"p" in f` is a substring test standing in for *"this is the pressure field"*. It is not
that test. It admits any basename containing the letter `p` anywhere.

**The decoys are already in the directory that produced the landed verdict.** Measured
2026-08-28 — `verification/runs/F3_runs/successor_triple_2026-08-26/runs/wedge/M2.5_th10/fine/postProcessing/surfaceSampleDict/3.11989651/`
holds **three** files:

```
T_wedgeSurface.raw    p_wedgeSurface.raw    rho_wedgeSurface.raw
```

They are three because `run_f3s.py:199` writes `fields (p rho T);` into the case's own
`surfaceSampleDict`. `T_wedgeSurface.raw` and `rho_wedgeSurface.raw` are excluded by
**nothing but the absence of the letter `p` from the strings `T`, `rho` and `wedgeSurface`.**

**The near-miss is one character wide, and the sort is already pointing the wrong way.**
`'T'` is ASCII 84, `'p'` is 112, so `sorted(...)[0]` prefers `T_…` over `p_…` whenever both
match. The only reason it does not fire here is the surface's name. Rename the patch to
`ramp`, `plate`, `pipe`, `plenum` or `upper` — all natural for a wedge/ramp case, and F3S
**is** a wedge/ramp case — and `T_ramp.raw` becomes `cands[0]`: **a temperature field read
into `p_wall_mean` and graded against a ±0.5 % pressure band.** Dimensionally silent,
numerically plausible, nothing in the record looks wrong.

### 2a. THREE STATEMENTS IN THE ROUTING THAT WERE FALSIFIED ON CHECK

**(i) Verification's `wallShearStress_plate.raw` claim is TRUE, and the supervisor's
rebuttal of it is FALSE ON THE FACT.** The brief states the file "does not exist anywhere in
the repo." It exists at **10+ paths**, e.g.
`cases/tmr/runs/fine/postProcessing/plateCf/2846/wallShearStress_plate.raw` and
`verification/runs/MODEL_FORM_runs/P_re5e6_kOmegaSST/postProcessing/wallCf/966/wallShearStress_plate.raw`.
`wallShearStress_bump.raw` exists too. Both are **non-pressure basenames containing `p`** —
exactly L-398's point, which is stated there as *"the premise is already false elsewhere on
the same disk"* and was never a claim about `grade_f3s.py`'s own directory.
**Why the check missed them: they are gitignored** — `.gitignore:67` matches
`**/postProcessing/` — so any git-mediated search returns zero. A zero from a reader that
cannot see the file is not evidence (rule 3, and the standing "gitignored is not filed"
finding). **The supervisor's *routing* conclusion survives intact and is confirmed below;
only the supporting fact was wrong.**

**(ii) The lesson is `L-398`, not `L-396`, and the rule-11 collision the brief asks to be
flagged is ALREADY REPAIRED at HEAD.** `git show HEAD:docs/LESSONS.md` carries exactly one
`## L-396` (`:16797`, closure's). The selector lesson sits at `:16905` as **L-398**, carrying
its own renumber note dated 2026-08-28T17:00Z: *"Cite this lesson as L-398; L-396 is
closure's."* Max existing id re-derived under rule 11: **398**. Nothing to repair; the
residual is cosmetic only — L-398 sits **above** L-397 in file order, because the renumber
did not move the block.

**(iii) The three sites do not all have decoys.** The brief treats them as one defect in
three places. `postProcessing/surfSeries/` — the `run_f3s.py:285` site — is written by a
function object declaring `fields (p);` (`run_f3s.py:84`), so it holds **one** file by
construction. The other two read `surfaceSampleDict/`, which holds **three**. §4 splits the
fix accordingly.

### 2b. THE REALISATION MEASUREMENT — independently reproduced, and WIDENED

The supervisor's measurement was re-run by this lane with the real predicate
(`f.endswith(".raw") and "p" in f`) walking the disk, not git:

| scope | dirs with ≥1 match | exactly 1 | **more than 1** |
|---|---|---|---|
| `verification/runs/F3_runs` (supervisor's scope) | **1,191** | **1,191** | **0** |
| whole repository (this lane's widening) | **1,837** | **1,837** | **0** |

Distinct matching basenames repo-wide: `p_airfoil.raw`, `p_airfoilSurface.raw`,
`p_coneSurface.raw`, `p_cylSurface.raw`, `p_wallValues.raw`, `p_wedgeSurface.raw`,
`wallShearStress_bump.raw`, `wallShearStress_plate.raw` — and the last two never share a
directory with another match.

**RULING ON REALISATION: the supervisor is CORRECT. The defect is LATENT. No F3S verdict is
exposed, and none anywhere in the repository is.** The landed F3S row cites
`…/3.11989651/p_wedgeSurface.raw` (`F3S_GRADED.json`) — the right file, selected for the
wrong reason. **Latent is not safe:** what disarms it is a naming accident in a dict that
`run_f3s.py` writes itself, and the successor is free to name its patch anything.

---

## 3. The predicate — §1's clause P, derived and checked against the disk

### 3.1 The convention, verified before being relied on

OpenFOAM's `surfaces` writer emits **one file per field per surface**, named
`<field>_<surfaceName>.<surfaceFormat>`. Verified against every `.raw` basename on this disk
(`p_wedgeSurface.raw`, `T_wedgeSurface.raw`, `rho_wedgeSurface.raw`,
`wallShearStress_plate.raw`, …): **the field name is the leading token before the first
`_`, without exception in this tree.**

### 3.2 Minimum form, and what it does about `_` in a surface name

```python
    cands = sorted(f for f in os.listdir(d)
                   if f.endswith(".raw") and f.split("_", 1)[0] == "p")
```

**A surface name containing `_` is harmless.** `split("_", 1)[0]` consumes only the first
separator, so `upper_wall` → `p_upper_wall.raw` → token `p` → matched. Underscores to the
right of the field name are never inspected.

**A file with no `_` at all is harmless.** `split("_", 1)[0]` on `foo.raw` returns
`"foo.raw"`, which is not `"p"`. No `IndexError` — this is why the `maxsplit` form is
specified rather than `split("_")[0]`, which is equivalent here but relies on a list that
happens never to be empty.

**Measured against the near-miss:** on `{T_ramp.raw, p_ramp.raw}` the token test yields
exactly `["p_ramp.raw"]` — one member, correct member, and the sort never gets a vote.
On `{p_plate.raw, wallShearStress_plate.raw}` it yields exactly `["p_plate.raw"]`, where the
substring test yields both and `sorted()[0]` returns `p_plate.raw` **by luck** (`p` < `w`).

### 3.3 THE RESIDUAL THE TOKEN TEST DOES NOT CLOSE — `p_rgh`, and the stronger form

**An OpenFOAM field name may itself contain `_`.** `p_rgh` is the standard buoyant-solver
pressure and is a live field name in this lab (`cases/ansys_verification/VMFLGPU005/case/0/p_rgh`
and others). If a dict ever writes `fields (p p_rgh);`, then `p_rgh_wedgeSurface.raw` has
leading token `p` and the token test **admits it as a second member.**

That outcome is **correct behaviour, not a hole**, and only because clause U is also
present: two members → refuse. Without U it would be a silent second false positive. This is
the concrete case §4 is built on.

**RECOMMENDED, where the reader knows the surface name — construct the basename, do not
describe it:**

```python
    want = "p_%s.raw" % surface_name        # read from the case's own surfaceSampleDict
    cands = sorted(f for f in os.listdir(d) if f == want)
```

Exact equality admits `p_rgh_…` never, admits `Cp_…` never, and reduces clause U to a
present-or-absent check that still must be written, because `want` can match zero files.
`surface_name` is **read from the case's own `system/surfaceSampleDict`**, never hard-coded —
a literal reintroduces the same class of assumption one layer up.

---

## 4. WHY BOTH CLAUSES, AND WHY NEITHER SUBSTITUTES FOR THE OTHER

**U without P refuses correctly and reports the wrong cause.** Add only the cardinality
guard, rename the patch to `ramp`, and the reader hits `{T_ramp.raw, p_ramp.raw,
rho_ramp.raw}`, counts 3, and refuses. The verdict is safe — nothing is misgraded — but the
message says *"expected one, found three"* about a directory that contains **exactly one
pressure file**. The next person is sent to look for a duplicate-write bug in the sampling
dict that does not exist. A refusal that misnames its cause costs a debugging session and
can be "fixed" by deleting the wrong file.

**P without U is silent.** Fix only the predicate and the reader is correct for every case in
this tree today — until `fields (p p_rgh)` (§3.3), at which point two members match, `[0]`
takes one, and **nothing refuses.** A silent wrong answer is strictly worse than a noisy
refusal, and this is the failure P alone cannot see: P narrows the set, it never counts it.

**Neither is downstream of the other.** L-398 makes the distinction and it is the reason the
sort key is not mentioned in §1: ordering asks *which member is chosen*; this defect asks
*whether the set has members it was never meant to contain*. Repairing `sorted()` repairs
nothing. **U is the guard, P is the intent; the pair is the rule.**

---

## 5. The three sites are NOT identical — `os.listdir` + substring vs `glob`

`grade_f3s.py:239` uses `os.listdir(d)` filtered by `endswith(".raw") and "p" in f`.
`run_f3s.py:255` and `:285` use `glob.glob(os.path.join(surfd, "*p*.raw"))`. On this tree
they return the same file. **Their failure sets differ, in four ways, and the fixes differ
with them.**

| # | difference | `os.listdir` + substring | `glob("*p*.raw")` |
|---|---|---|---|
| 1 | **dotfiles** | `.p_foo.raw` is returned | `*` does not match a leading `.`; **invisible** |
| 2 | **metacharacters in the DIRECTORY component** | `d` is used as a plain path; a case dir containing `[`, `]`, `?` or `*` is read literally | `surfd` is interpolated **unescaped** into the pattern and is parsed as glob syntax; a case dir named `M2.5_th10[fine]` silently matches **nothing** |
| 3 | **empty result** | guarded — `if not cands: return None, None` | **`[0]` on `[]` raises `IndexError`** at `:255`; guarded by `if g:` at `:285` |
| 4 | **return shape** | basenames; `sorted()` orders basenames | full paths; `sorted()` orders paths, identical here only because the prefix is shared |

Rows 2 and 3 are the load-bearing ones. Row 3 means `run_f3s.py:255` **crashes** where
`grade_f3s.py:239` returns `None` — different observable behaviour from the same absence, and
a crash inside a runner mid-campaign is a different incident from a `None` inside a grader.

### 5.1 Per-site specification

| site | current | clause U | clause P | note |
|---|---|---|---|---|
| **`grade_f3s.py:239`** | `os.listdir` + `"p" in f`, `cands[0]`; directory holds **3** files | `len(cands) != 1` → `refuse(...)`, exit 2 | token test §3.2, or §3.3 constructed form | **decoys present.** The `if not cands: return None, None` early return is **deleted** — absence is a refusal, not a `None` that the caller may interpret |
| **`run_f3s.py:255`** | `glob("*p*.raw")[0]`; directory holds **3** files | `len(g) != 1` → `refuse(...)`, exit 2 | **replace `glob` with `os.listdir` + token test** | fixes rows 1, 2 **and** 3 at once: the `IndexError` becomes a named refusal and the unescaped-directory hazard disappears with the glob |
| **`run_f3s.py:285`** | `glob("*p*.raw")`, `g[0]` under `if g:`; directory holds **1** by construction (`fields (p);`, `run_f3s.py:84`) | `len(g) != 1` → `refuse(...)`, exit 2 | same replacement | **`if g:` is DELETED, not kept.** It currently makes a missing pressure sample a **silently skipped time point** in the plateau series — the series shortens and nothing says so. That is a second, independent defect at this site and it is the reason the cardinality guard must **replace** the truthiness test rather than sit inside it |

**`run_f3s.py:285` is the site whose repair is not cosmetic.** Its directory is genuinely
single-membered today, so clause U will never fire there on current dicts — but `if g:`
silently drops time points, and the plateau state that decides limb (1) of rule 5 is computed
from that series.

---

## 6. The refusal — exact contract

One helper, used at all three sites. Both files already carry
`def refuse(msg): sys.stderr.write("REFUSED: %s\n" % msg); sys.exit(2)`
(`grade_f3s.py:88-90`, `run_f3s.py:44-46`); the shape below is written **through** it.

```python
def select_one(d, want_field, ext=".raw"):
    """Select the single artifact for `want_field` in `d`, or REFUSE."""
    names = sorted(os.listdir(d))
    cands = [f for f in names if f.endswith(ext)
             and f.split("_", 1)[0] == want_field]
    if len(cands) != 1:
        refuse(
            "UNIQUE-SELECTOR: expected exactly 1 artifact for field %r in\n"
            "  %s\n"
            "  predicate : basename.endswith(%r) and basename.split('_',1)[0] == %r\n"
            "  matched   : %d -> %s\n"
            "  directory : %d entries -> %s\n"
            "A reader that cannot say how many things it matched cannot say it\n"
            "matched the right one. Not degraded, not defaulted: refused."
            % (want_field, os.path.abspath(d), ext, want_field,
               len(cands), cands, len(names), names)
        )
    return os.path.join(d, cands[0])
```

**Exit code: 2.** Same as every other refusal in this path (`grade_f3s.py:54`, `:90`,
`:588`), so a launcher reading `rc` cannot tell a selector refusal from a gate refusal by
accident and treat one as a crash.

**Message shape — four things named, all mandatory:**
1. the **absolute directory**, so it can be pasted into `ls` without a working-directory guess;
2. the **predicate, in full, as evaluated** — the extension and the field token, not a prose paraphrase;
3. **every candidate matched**, listed;
4. **every entry in the directory**, listed, with its count.

Item 4 is what separates this from the existing reference implementation.
`cases/ansys_verification/grade_vmfl076.py:677-680` is the lab's prior art for clause U —
`if len(hits) != 1: refuse("G2", "%s: expected exactly one gateLine T file, found %d")` —
and **it prints only the count.** A reader told "found 3" must go to the disk to learn
which three, and by then the run directory may have been cleaned. **The refusal is the
record.** Where item 4 would be unbounded (a directory of thousands), print the first 20 and
the total, and say the list was truncated — never silently.

**Refusal is unconditional.** No `--force`, no environment override, no "degrade to the
first match with a warning". Rule 4's *refuse rather than degrade*.

---

## 7. Controls — mandatory, planted, driven through the real reader

Implemented as `--selftest` on each repaired file, refusing (exit 2) if any control fails.
Every control runs **through the real `select_one`** on a **real temporary directory with
real files on disk**. A control that calls a re-implementation of the selector tests the
re-implementation (rule 3; and this lane notes the sweep-measures-its-own-regex failure
recorded in the ansys guard-shape sweep — a check that never sees a true positive is
measuring itself).

| id | fixture (files written to a temp dir) | assertion, exactly |
|---|---|---|
| **C1 — positive control for U** | `p_wedgeSurface.raw`, `p_rgh_wedgeSurface.raw` | `select_one(d, "p")` **raises `SystemExit` with `code == 2`**; captured stderr contains `UNIQUE-SELECTOR`, the substring `matched   : 2`, **and both basenames**. Two members is the case §3.3 proves is reachable, so this control is the reachable one, not a contrived one. |
| **C2 — the singleton passes** | `p_wedgeSurface.raw`, `rho_wedgeSurface.raw`, `T_wedgeSurface.raw` (the graded directory's exact contents, §2) | `select_one(d, "p")` returns a path whose basename `== "p_wedgeSurface.raw"`, **no exception**. Proves the widened refusal did not break the case that actually ran. |
| **C3 — THE NEAR-MISS, reproduced** | `T_ramp.raw`, `p_ramp.raw` (byte-distinguishable contents) | `select_one(d, "p")` returns basename `== "p_ramp.raw"`. **And, in the same control, the old predicate is evaluated on the same directory and asserted to return `T_ramp.raw` first** — `sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)[0] == "T_ramp.raw"`. Fails the selftest if it does not. **The control must SHOW the defect firing before it shows the repair holding**, or it is a zero from a reader not shown able to see a non-zero. |
| **C4 — negative control: the selector was not disabled** | empty directory; **and** a directory holding only `T_ramp.raw`, `rho_ramp.raw` | `select_one(d, "p")` **exits 2 in both**, stderr containing `matched   : 0`. A repair that "fixes" the defect by never refusing, or by returning `None` for absence, fails here. |
| **C5 — mutation control** | run C1–C4 against a copy of the module with `if len(cands) != 1:` mutated to `if False:` | **C1 and C4 must FLIP to failure.** A guard whose deletion changes no control was never being exercised (`F.2` of the F3S pre-registration, applied to this repair). |
| **C6 — flag-proof** | `python3 -O <file> --selftest` | rc **2**. Zero `assert` statements in the repaired code — all refusals are `raise`/`sys.exit(2)` (L-332), re-checked by AST node count, not by grep. |

**C3 is the control this specification exists for.** C1, C2, C4 could all pass on a reader
that still used `"p" in f`.

---

## 8. SCOPE — what may be repaired now, and what needs a successor

**This follows from the freeze ruling, which is stated here because the repair route depends
entirely on it.** Evidence in §8.1; ruling in §8.2.

### 8.1 What the tree says

- **Freeze commit `5891db27`**, 2026-08-26T03:39:53Z, confirmed by the pre-registration's own
  CORRECTION ADDENDUM (`F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md:863-908`, v3.2→v3.3).
- **§9 of that pre-registration** (`:104-111`) names the frozen grading path as **exactly
  two files**: `instrument.py` and `grade_f3s.py`. **`run_f3s.py` is not named.**
- **ADDENDUM 1** (`:692-700`) re-pins the graded path by blob, ordered:
  `check_complete_f3s.py` (`f972d071`), then `grade_f3s.py` (`d67d415f`, unchanged from the
  freeze). **`run_f3s.py` is not named there either.** It is named nowhere in the 911-line
  registration or any of its four addenda.
- **`run_f3s.py` did not exist at the freeze commit.** `git ls-tree 5891db27` on the rung
  directory returns three files: `grade_f3s.py`, `instrument.py`, `selftest_fixture.py`. It
  first appears at `501c2690`, 2026-08-26T03:48:31Z — **9 minutes after the freeze.**
- **First compute happened.** Run root
  `verification/runs/F3_runs/successor_triple_2026-08-26/runs/` — `_control` 03:51,
  `wedge` 03:54, `diamond` 03:59; `F3S_GRADED.json` and `COMPLETION.json` 04:09;
  `RESULTS.md` 04:15. **Verdicts landed: 0 PASS · 0 GATE FAIL · 3 NOT A RESULT.** Cost
  **15.8298 core-min** measured of a 17.6541 cap, calibration row **C-112**
  (`docs/COST_CALIBRATION.md:188`).
- **`run_f3s.py` ran, and it produced a graded quantity.** It writes `out["p_wall_mean"]`
  (`:256`) into each case's `result.json`, and `grade_f3s.py` reads `result.json`
  (`:375`, `:465`, `:490`) and cites it as an artifact in `F3S_GRADED.json`.
- **But the graded pressure number is NOT `run_f3s.py`'s.** `grade_f3s.py` carries its own
  independent reader, `read_p_wall_mean(case_dir)` (`:234-243`), reaching the `.raw` directly;
  `F3S_GRADED.json` cites
  `…/M2.5_th10/fine/postProcessing/surfaceSampleDict/3.11989651/p_wedgeSurface.raw` as the
  artifact for that row. `run_f3s.py`'s `p_wall_mean` is a **parallel** value the grader does
  not grade from.

### 8.2 THE RULING

> **`run_f3s.py` is OUTSIDE the pre-registration's enumerated frozen grading path, and it is
> POST-FIRST-COMPUTE. Both are true, and the second governs.**
>
> **Neither file may be edited in place. The repair for BOTH halves is a successor.**

The coordinator's description of `run_f3s.py` as "the unfrozen driver half" is **half right
and operationally wrong**, and it is refused here:

1. **It is genuinely not in the enumerated path** — §9 names two files, ADDENDUM 1 pins two
   files, and `run_f3s.py` is in neither list and did not exist at the freeze. The commit
   message's "committed BEFORE firing" is accurate as to *timing* and is evidence about
   *intent*, but a commit message cannot enrol a file into a registration that does not name
   it. On the enumeration alone, it is outside.
2. **The enumeration is not what bars the edit — first compute is.** `run_f3s.py` **ran**,
   on 2026-08-26 between 03:51 and 03:59, and its outputs are cited in a graded record that
   landed three verdicts and a cost row. Rule 2's second bullet closes *changes* after first
   compute; rule 2's fourth bullet requires that the file which ran can be **hashed against
   its committed blob**. Editing `run_f3s.py` in place destroys that identity for a file
   whose `result.json` output is cited as an artifact in `F3S_GRADED.json` — the record
   would then cite a producer that no longer exists in the form that produced it. **A file
   outside the frozen path is not thereby outside the rule that fixes the record.**
3. **The rung's own precedent already rules this way, twice.** ADDENDUM 1 §7
   (`:752-761`) found a real defect in the same `run_f3s.py` — buffered solver stdout making
   a stall indistinguishable from progress — and declined to fix it in place, in terms that
   answer this question directly: *"changing the runner mid-rung would alter what is being
   measured after compute began … belongs in the next rung's launcher."* And L-398's own
   closing line rules the grader half the same way: *"Found post-compute in a frozen
   comparator, so NOT repaired."*
4. **The rung's authority is spent.** The correction addendum's own words: *"no further
   compute may be launched under this registration."* There is nothing left for an in-place
   repair to serve.

**What this means for the routing.** The distinction the brief draws — grader frozen,
driver free — collapses. **Nothing in `successor_triple_2026-08-26/` is repairable in
place.** The correction owed back to the coordinator is that the repair is **one successor
covering all three sites**, not a split repair.

**No route is left open by omission.** `VERIFICATION_CHARTER.md` §2d.1's four-condition
post-compute repair exception is **not invoked and is not argued here**; a latent defect that
has misgraded nothing does not need it, and invoking it to save nine minutes of re-registration
would be the wrong precedent.

### 8.3 The successor

| | |
|---|---|
| **route** | a NEW rung, NEW directory, NEW pre-registration frozen before compute |
| **directory** | `verification/runs/F3_runs/successor_<name>_<date>/` — **the name is the supervisor's to set**, not this spec's |
| **carries** | all three repaired sites, `select_one`, and controls C1–C6 |
| **inherits** | the bands, the cap discipline and the `grade_ladder` routing of the fired rung, **re-registered, never inherited by reference** |
| **cites** | this spec's commit sha, and L-398 |
| **must also** | re-register `run_f3s.py`'s successor **into §9's enumerated grading path by name and blob**. Its exclusion is the root cause of this ambiguity: a file that writes a graded quantity was outside the list that says what grades. |
| **should also** | close ADDENDUM 1 §7's buffered-stdout gap, deferred to exactly this successor |

**Recommended, and outside this spec's authority to decide:** the successor's sampled surface
should be named to **fire** the old predicate — `ramp` — so that C3's near-miss is not only a
fixture but the rung's own live geometry. A repair proven on the naming that breaks the
original is worth more than one proven on the naming that hid it.

---

## 9. What this specification does NOT do

- **No gate, no threshold, no band, no cap, no label** is added, moved or removed. The bands
  stay ±0.5 % / ±2.0 % / ±1.0 %; the cap stays 17.6541 core-min.
- **F3's records are NOT re-graded.** F3 stays CLOSED at 5 PASS · 1 GATE FAIL · 1 NOT A
  RESULT · 3 PENDING. F3S stays at 0 PASS · 0 GATE FAIL · 3 NOT A RESULT, cost row C-112.
  **The defect is latent (§2b) and no landed verdict is exposed**, so there is nothing to
  re-grade — and that finding is the reason, stated so it cannot later be read as leniency.
- **No file under `successor_triple_2026-08-26/` is edited** (§8.2).
- **No compute is authorised.** This is a specification. The successor's own
  pre-registration, frozen and costed, is what authorises a run.
- **Nothing is sent, filed or submitted** (rule 7).
- **No claim is made about readers outside cfd.** The 1,837-directory sweep in §2b covers the
  whole repository and found zero realisations, but the ruling and the repair are cfd's.

---

## 10. Filing note, reported not repaired

`grade_f3s.py`, `run_f3s.py`, `instrument.py`, `launch_f3s.py` and `check_complete_f3s.py`
are measurement code living inside a **run tree**. `python3 scripts/check_filing.py` was run
2026-08-28: **34 violations across 7 rules (R0, R1, R5, R6, R7, R8, R9), rc 1, and zero of
them under `verification/runs/F3_runs/`.**

**Measurement code in a run tree is NOT a filing violation** by the binding artifact.
`R3-SCRIPTS-LOWER` is gated on `len(parts) == 2 and parts[0] == "scripts"`
(`check_filing.py:183`) and cannot reach a nested path; `R6-RUNTREE` fires only on a file
basenamed `controlDict` (`:207`). No rule in the checker constrains `.py` placement outside
`scripts/`. The pre-registration's *"one rung, one root"* (`:105`) is consistent with the
checker: co-locating a rung's instruments with its runs is the lab's practice, not a defect.
**Reported, not repaired, and no rule change is proposed** — retiring or amending a standard
is Sanaa's alone.

---

*Spec ends. Written before implementation; the commit that lands it is the freeze.*
