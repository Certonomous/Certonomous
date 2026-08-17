# MOVE_MAP execution plan — the batches, their invariants, and what breaks between them

**Nothing was moved, renamed, deleted or untracked in preparing this document,
and `.gitignore` was not edited.** Three artefacts were created:
`scripts/lab_paths.py`, `scripts/hand_carry.py`, and their tests
`sdk/tests/test_lab_paths.py` and `sdk/tests/test_hand_carry.py`. This record is
the fourth.

Companion to `campaign/MOVE_MAP_2026-08-16.md`, which remains the rule set. This
document adds three things the map left as prose: an executable hand-carry, the
`lab_paths` shim its §4.1 proposed, and a batch order whose every step states
what breaks if the next one never lands.

Measured at **`f40f6ef5`** unless a different anchor is named beside it, and
**over `git ls-tree -r HEAD`, not `git ls-files`** — §1 is about why that
distinction moved an answer. The tree moves several times an hour; every count
below is a reading at a frame. `THERMAL_K0_runs` was measured three times in
forty minutes at 387, 362 and 368 files, and then turned out not to belong on
the list at all — both facts are recorded in §3 rather than smoothed away.

---

## 1. The reconciliation — and the frame it was taken in is the wrong one

**The map counts the INDEX, and this lab's own commit protocol never writes
it.** `MOVE_MAP` §2 states that its totals *"reconcile to `git ls-files | wc -l`
exactly"*, and every count in it was taken that way. `git ls-files` lists
**index** entries. `docs/USING_THIS_LAB.md` §8.5's private-index form — the
mandated one — builds a commit under `GIT_INDEX_FILE` and **never touches the
shared index**, so every file a conforming agent lands is in HEAD and absent
from `git ls-files` until somebody runs `git add` or `git reset`. Under a live
fleet nobody does.

Measured at `f40f6ef5`:

```
git ls-files                     | wc -l   ->  13,814
git ls-tree -r --name-only HEAD  | wc -l   ->  13,974
comm -13  (in HEAD, not the index)         ->     160
comm -23  (in the index, not HEAD)         ->       0
```

**160 tracked files are invisible to the frame the map counts in**, and the
asymmetry says what they are: nothing is staged that HEAD lacks, so all 160 are
landed work that the index has not caught up with. `scripts/lab_check.py:486-496`
records this exact repair — `tracked_frame` moved from `git ls-files` to
`git ls-tree -r HEAD` on docket D274, ruled 2026-08-16 — with the reasoning that
applies verbatim here: *"the question this frame answers is 'will this travel'…
and the index is a per-machine, per-moment scratch state no reader of the
repository ever sees."*

**This is not bookkeeping. It changed an answer in §3**, and the direction it
changed it in is the dangerous one: `campaign/THERMAL_K0_runs/` holds **97
tracked files at HEAD and 0 in the index**, so the index frame called it dark
and put it on the hand-carry list — a tree `git mv` is about to rename, hand-moved
out from under it, leaving the index and the disk pointing at different places.

### The counts

Re-derived over the index frame, for comparability with the map, classifying
every tracked path into exactly one rule with **zero unclassified**:

| | claimed at `371be610` | measured at `371be610` | measured at HEAD (index frame) |
|---|---:|---:|---:|
| tracked total | 20,762 | **20,762** | **13,814** |
| R11 `demo-output/plots/` | 752 | 752 | **752** |
| R20 campaign `*_runs`/`*_work` | 7,940 | 13,742 − 5,802 = 7,940 | **7,940** |
| R22 `dafoam` | 3,268 | 3,268 | **3,268** |
| R23 `race` / `agenda` | 179 / 139 | 179 / 139 | **179 / 139** |
| R3 / R4 / R7 / R9 | 327/202/137/52 | same | **same** |
| R10 / R12 / R24 | 77 / 10 / 7 | same | **same** |
| **R21 campaign records** | **269** | **269** | **271** |

The map was exactly right at its own anchor, in its own frame. It does not close
at HEAD, and the brief's account of why — *"the four extra being files landed
within the hour"* — is half wrong:

1. **R21 is 271, not 269 (+2).** `LADDER_V_V7_GRADE_2026-08-16.md` and
   `MOVE_MAP_2026-08-16.md` itself, the map having since been committed into its
   own corpus. These **are** new files. The move subtotal becomes **13,084**.
2. **`uq_batch.err` and `uq_batch.log` are still tracked (+2), and they are
   supposed to be.** They are not stragglers of an incomplete sweep.
   `.gitignore:105-113` carries a named exception for exactly these two files,
   in as many words: *"They stay tracked."* The map's **U2 count of 12 is
   wrong** — it is 10 (`mbc_retry*.{err,log}`), and the two `uq_batch` files
   belong in the **keep-in-place** bucket, not the untracking one. The map
   contradicts the repository's own committed ignore policy at that line.

```
    723   keep in place   R0(3) R3(327) R4(202) R7(137) R9(52) + uq_batch(2)
 13,084   move            R21 now 271
      7   exceptions      X1(1) X2(1) X3(5)
 ------
 13,814   =  git ls-files | wc -l     <-- the INDEX frame, and 160 short of HEAD
```

`comm` over the two index frames: **6,950 paths left tracking and 2 arrived**,
all 6,950 U-rule files — U1 2 wheels, U2 10 `mbc_retry*`, U3 5,802, U4 1,136.
**Zero R-rule files lost tracking.** Batch 1 executed cleanly.

**Before batch 0 runs, the whole of §2 must be re-derived over
`git ls-tree -r HEAD`**, and the 160-file gap says the rule counts will move.
That re-derivation is not done here: it is the map's, and it is a batch-0
prerequisite rather than a note.

**A second counting hazard for whoever runs it.**
`git ls-files -- 'demo-output/*.png'` returns **874**, not R12's 10: git pathspec
globs match across `/`. R12 is only measurable with an anchored regex over a
path snapshot.

---

## 2. Two inherited claims, checked rather than carried

### 2.1 The struck `_SHIPPING_RE` claim — the withdrawal is CORRECT

§4.3 struck its own "this one fails open" claim about
`scripts/check_absolutes.py:707`. The withdrawal was itself this document's
own, so it was re-traced by execution, every link:

- `_SHIPPING_RE` is read in **exactly one place**, `check_absolutes.py:726`:
  `if _SHIPPING_RE.match(path) or suffix == ".html": score += 1`. `grep` returns
  only `:707` and `:726` repo-wide.
- `blast_radius` is called once, at `:625`, inside `classify_unit`. The verdict
  cascade at `:643-690` — `gate` → `QUOTED` → `dangling` → `resolved` →
  `HEDGED` → `RULE` → `DEFINITIONAL` → `UNBACKED` — **references `blast` in no
  branch**; it is attached to the `Claim` at `:697` and nowhere consulted.
- `Claim.is_defect` (`:336-337`) is `self.verdict in DEFECT_CLASSES`, and
  `DEFECT_CLASSES = (UNBACKED, CITES_MISSING_CHECK)` (`:294`).
  `AuditResult.verdict` (`:800-804`) reads `walk_error`, `skips.blinding`,
  `defects`. The exit code (`:1129`) maps that verdict alone.
- The only code-level caller is `scripts/lab_check.py:913`, which invokes the
  module with **no arguments** and reads the exit code.

**Verdict: the withdrawal holds. `_SHIPPING_RE` cannot reach a verdict, exit
code, gate, threshold, filter or suppression.** Traced by reading every
consumer and confirmed by executing the module over the whole tracked corpus,
rather than by reading the struck paragraph. The `.html` claim also holds, by
short-circuit `or` at `:726`, confirmed by execution: `web/closure.html` scores
1 on suffix alone.

**One thing the withdrawal's wording understates.** `blast` *does* feed a
truncation — `:874-877`, `ranked[:top]` with `top=40` — and a ranking that feeds
a truncation is a verdict path in effect. So it was measured rather than argued.
Over the full tracked sweep: `FLAGGED`, 11,502 defects, blast distribution
`{4: 237, 3: 4813, 1: 5131, 0: 1321}`; the displayed rows at positions 1, 40 and
41 all sit at blast 4, with 237 claims tied at that score. A claim demoted 1→0
sits roughly two hundred positions below the cut and can neither enter nor leave
the visible window. **The truncation exists and is unreachable by this bit at
the tracked frame.** It is still re-pointed in the move commit, at the priority a
ranking defect earns.

### 2.2 The `audit(paths=)` fail-open repair — STILL IN PLACE, and it was real

`b0ab070d` added `Skips.missing`, folded it into `Skips.blinding`
(`check_absolutes.py:771`), and put an existence pre-pass **before** the suffix
filter (`:927-932`):

```python
for p in selected:
    if not p.exists():
        skips.missing += 1
        skips.unreadable_paths.append(f"{p} (named but does not exist)")
    elif p.suffix not in suffixes:
        skips.out_of_frame += 1
```

- **Still present at HEAD.** `git log b0ab070d..HEAD -- scripts/check_absolutes.py`
  is empty and the worktree copy is byte-identical to HEAD's blob.
- **Pinned by a test that exists and passes.**
  `sdk/tests/test_absolute_claims.py:389`
  `test_a_caller_named_path_that_does_not_exist_yields_unknown_not_pass`, with
  its must-not-match control at `:436`. `pytest sdk/tests/test_absolute_claims.py`
  → **25 passed, 9 subtests passed**.
- **Executed.** `python3 scripts/check_absolutes.py --paths this/path/never/existed`
  → **exit 3**, `UNKNOWN … 1 named path(s) do not exist`.
- **Falsified against the pre-repair module**, loaded from
  `git show b0ab070d^:scripts/check_absolutes.py`: `this/path/never/existed`,
  `web/benchmarks.json` and `web/plot.png` all returned **CLEAN / exit 0**, while
  `web/closure.md` returned UNKNOWN. Three of four PASS for a file never read,
  the outcome turning on the filename's suffix. That is the reported fail-open,
  reproduced, and the repair closes all four.

This is the map's own hazard in miniature and it is why `lab_paths` is built the
way it is: after the move every caller naming a moved path would have been told
PASS by a checker that read nothing.

### 2.3 A third figure that failed re-derivation — §9.1's control-corpora count

§9.1 calls the labelled control corpora *"the highest-value item in the whole
R2/R3 repair set"* and states **269 path fields / 306 string occurrences**,
re-measured at `dce05a01` *"by parsing the JSON rather than grepping it"*. Parsed
again, at that same anchor and at HEAD:

| Corpus | records | `demo-output/`-rooted `path` fields | `demo-output` string occurrences |
|---|---:|---:|---:|
| `scripts/use_mention_control_set.json` | — | **115** | 139 |
| `sdk/tests/fixtures/absolute_claims_labelled.json` | 100 | **62** | 69 |
| `…_labelled_second_instance.json` | 75 | **46** | 98 |
| | | **223** | **306** |

**306 is right. 269 is not, and neither is the 92 it is built from.** The
second-instance corpus holds **75 records with one `path` field each**, so 92
path fields is not a quantity it can have; its file has not changed since
`3e9d7908`, so this is not drift. §6.4 and §9.1 also disagree with each other on
the first fixture (62 vs 66).

**The gate's baseline is 223, not 269.** This matters more than the arithmetic:
§9.1's pass condition is *equality* with the count recorded before the batch. A
gate seeded at 269 fails every batch forever, and the cheapest way to make it
green is to loosen it — which is how the positive controls stop being controls.

Measured now against `lab_paths.resolve()`: **223 of 223 resolve, 0 unresolved.**
That is the pre-batch baseline the gate compares against.

### 2.4 The same frame defect, live in a second instrument

`scripts/check_absolutes.py:520-547`'s `known_test_names()` derives the set of
names that can back an absolute claim from **`git ls-files`**. Its docstring
gets the intent exactly right — *"a suite nobody has named must still be able to
back a claim"* — and then reads the frame that cannot see a suite landed by this
lab's own commit protocol.

Measured at `f40f6ef5`, running its own harvester over both frames:

```
ls-files (index):  2,334 test names
ls-tree  (HEAD) :  2,393 test names
```

**59 test functions exist in HEAD and are invisible to the checker.** Every
absolute claim citing one of them is condemned `CITES_MISSING_CHECK` — the more
severe class, and one that deliberately is not rescued by a resolving sibling
citation. That is a false positive produced by the instrument, on the claims most
likely to be freshly evidenced, and it is D274's defect class unrepaired in a
second place. Not repaired here: `check_absolutes` is a shared instrument
mid-flight and this is not that batch. Recorded so it is not rediscovered.

**One consequence worth carrying forward for record authors.** The same function
resolves a `test_*` token only against **function and class definitions**, so a
test MODULE's filename never resolves: writing `sdk/tests/test_lab_paths.py` in
prose yields the token `test_lab_paths`, which is not a function, and condemns
the unit. Every `Evidence:` line in this record and in both new modules
therefore names functions, not files — and they will keep reading as dangling
until the index catches up with HEAD.

---

---

## 3. The hand-carry set, derived

**`git mv` never moves a directory containing no tracked file.** The rule set of
§2 was built by classifying *tracked* paths, so such a directory is invisible to
it: in no rule, not in the 13,084, and nothing in the plan says it should move.
The path constant that names it is a plain string in a `.py` or `.sh` file, and
§4.3's mechanical prefix rewrite moves it happily. Constant in the new tree,
files in the old one, everything green.

Derived by `python3 scripts/hand_carry.py derive`, which walks the worktree,
finds every directory holding files but no tracked file beneath it, and asks
whether any ancestor is renamed as a unit. **It is re-derived at every
invocation and the numbers below are a frame, not a constant.**

### 3.1 HAND-CARRY — `git mv` will never reach these

| Tree | files | bytes | destination | why |
|---|---:|---:|---|---|
| `demo-output/website/solve_registry` | 300 | **1,508,128,888** | `evidence/solve_registry` | in no rule at all — 0 tracked files at HEAD, so the classifier never saw it |
| `demo-output/website/surfaces` | 7 | 2,180,257 | `evidence/surfaces` | in no rule; §9 already records `**/surfaces/` stranded once |
| | **307** | **1,510,309,145** | | |

The numbers on `solve_registry` reproduce §4.3's "300 files / 1.51 GB" exactly.
`surfaces/` is new, and it is the `**/surfaces/` §9 records as stranded once
before — seven `.stl` geometries caught by an ignore rule aimed at
functionObject sampled-surface output.

**`campaign/THERMAL_K0_runs/` was on this list and has been struck.** Over the
index frame it read 0 tracked files, 368 on disk, and the derivation put it here
as *"a rule pointing at a tree it cannot move"*. Over HEAD it holds **97 tracked
files** — `0.orig/` initial conditions and `constant/` dictionaries, landed by
another agent behind `.gitignore:122-123`'s re-inclusion, which was added
**today**. `git mv` moves it under R20 and a hand-carry would have been wrong.
The claim, its retraction and the frame that caused it are all §1.

Two further buckets the derivation separates and the mover must not confuse:

- **DISCARD — 8 trees, 38 files, 976,586 bytes.** `__pycache__` and
  `.pytest_cache` go dark like anything else, and a rule's prefix will claim
  them: `demo-output/website/campaign/__pycache__` redirects cleanly to
  `verification/campaign/__pycache__`. Carrying one is wrong twice — it is not
  evidence, and a stale `.pyc` carries an embedded source path that no longer
  exists. They are reported and never carried.
- **STAYS PUT — 7 trees, 16,027 files, 1,484,990,437 bytes** (§3.5).

**Destinations follow §7.3's own rule** — *"/verification/runs/ is the
tracked-record side, /evidence/ is the gitignored bulk"* — rather than an
invention. `solve_registry` and `surfaces` are 100% gitignored bulk cited from
records (`.gitignore:37` and `:76` say so of `solve_registry` in as many words),
so they go to `/evidence/`. `THERMAL_K0_runs` goes where R20 sends it, because
`.gitignore:122-123` — added **today** — deliberately re-includes
`THERMAL_K0_runs/*/0.orig/` so that its initial conditions become tracked. **All
three destinations are decisions and are the owner's to ratify.** They live in
one place, `lab_paths._MOVES`, and changing them there changes every consumer.

`THERMAL_K0_runs` was measured at **387 files**, then at **362**, then at
**368**, across forty minutes. It is live. That is why the carry re-measures
immediately before the move and aborts on any drift from the plan, rather than
trusting a number in a checklist.

### 3.2 The `.gitignore` re-point that must land in the same commit

A carried tree whose ignore rule still names its old path **stops being ignored
the moment it lands**, and the next `git add` sweeps 300 files of solver log
into the index. Reported by `hand_carry.py plan`, never edited by it:

```
.gitignore:38  demo-output/website/solve_registry/  ->  evidence/solve_registry/
```

`.gitignore:68`'s `**/surfaces/` is path-independent and needs nothing.

**Two more `.gitignore` lines belong to batch 7 rather than to the carry**, and
they are the reason the frame repair mattered:

```
.gitignore:122 !demo-output/website/campaign/THERMAL_K0_runs/*/0.orig/    -> !verification/runs/THERMAL_K0_runs/*/0.orig/
.gitignore:123 !demo-output/website/campaign/THERMAL_K0_runs/*/0.orig/**  -> !verification/runs/THERMAL_K0_runs/*/0.orig/**
```

`THERMAL_K0_runs` moves by `git mv` under R20, and its 97 tracked files are
tracked **only because those two negations re-include them**. If R20's move
lands without re-pointing them in the same commit, the ignore rule above them
(`campaign/*_runs/*/[0-9]*/`) no longer has its exception at the new path and
the case's initial conditions stop being tracked at the next index refresh.

### 3.3 The hazard the plan creates for itself — `MESH_AUDIT_runs`

`demo-output/website/campaign/MESH_AUDIT_runs/` holds **78 tracked files, and
every one of them is a `*.log.checkMesh`** — solver-utility output, precisely
the class batch 2 untracks. **The moment batch 2 lands, this directory goes
dark, and batch 7's `git mv` of it aborts.** 78 files, 380,082 bytes. Nothing in
the tree says so until batch 7 runs and takes the whole batch down with it,
because `git mv` with several sources aborts all of them.

Derived by `hand_carry.py derive`'s projection, which re-runs the whole
derivation against the projected post-batch-2 tracked set and reports the
difference. **It is the only such directory**; the first cut of that projection
reported 771 and was wrong, because it did not apply the carrier logic — a
directory going dark is harmless while an ancestor is still renamed as a unit.

**Two ways out, and batch 2 must pick one before it runs** (§4, batch 2).

### 3.4 RIDES ALONG — 963 trees, 33,819 files, **10,560,965,662 bytes**

These are dark trees that an ancestor's rename carries: `dafoam/f6d_random_matrix_uq/ens`
(6,223 files, 2.79 GB), `f6d_option_a` (8,723 files, 1.70 GB),
`mega-batch/work` (1,229 files, 395 MB), and 928 more.

**They ride along ONLY if every `git mv` is made against the DIRECTORY, never
file-by-file.** `git mv <dir>` is a `rename(2)`, so gitignored content travels;
a per-file `git mv` loop leaves 10.5 GB behind. That is the invariant on batches
4 through 7, stated as an invariant because §9's own note — *"`git reset --hard`
does not undo a `git mv`'s effect on gitignored siblings"*, the revert having
stranded ~11 GB — is the same 10.56 GB seen from the other side.

### 3.5 STAYS PUT — named by constants, mapped by no rule

| Tree | files | bytes | consumers |
|---|---:|---:|---|
| `docs/campaigns/F14-cooling-ladder/K0b_mesh_sensitivity` | 4,964 | 765,858,513 | — (R7 keeps `docs/**`) |
| `mission-output` | 8,625 | 573,298,685 | **13 tracked modules**, incl. `self_audit.py`, `gate_table.py`, `build_laptop_bundle.py` |
| `docs/campaigns/F14-cooling-ladder/K0c_runs` | 776 | 98,781,140 | — (R7) |
| `sdk/chief-engineer-runs` | 1,568 | 41,241,873 | `self_audit.py:6518` (R3 keeps `sdk/**`) |
| `dist/certonomous-demo` | 90 | 5,432,332 | X1 DEFERRED |
| `chief-engineer-runs` (root) | 3 | 157,442 | 6 `sdk/scripts/` modules |
| `.claude` | 1 | 182 | infrastructure |

**`mission-output/` appears nowhere in §1's target tree**, and it is 573 MB
named by thirteen modules. It does not move under this map. Saying so here is
what stops the next sweep from tidying it into the new tree — and `lab_paths`
binds it as a non-moving name for the same reason.

---

## 4. The batches

**Suite command** — `scripts/lab_check.py` is the only entry point; exit
contract **0 PASS / 1 FAIL / 3 UNKNOWN**, and **3 is not green**:

```bash
python3 scripts/lab_check.py --root /home/ubuntu/Certonomous              # full,  ~18 min
python3 scripts/lab_check.py --no-tests --root /home/ubuntu/Certonomous   # gates, ~3 min
```

**Three gates run after every batch from 4 onward, before it is called green.**
A green suite is necessary and not sufficient:

```bash
# G1  the carry set must not have grown.  Reads HEAD, never the index --
#     see section 1; the index is 160 files behind and calling a tracked tree
#     dark is the error that strands data.
python3 scripts/hand_carry.py derive | sed -n '/HAND-CARRY/,/RIDES/p'

# G2  the control corpora -- section 2.3's 223, fail-closed on any field that
#     resolves at neither its literal location nor its successor
python3 - <<'EOF'
import json, sys; sys.path.insert(0, "scripts"); import lab_paths as L
C = ["scripts/use_mention_control_set.json",
     "sdk/tests/fixtures/absolute_claims_labelled.json",
     "sdk/tests/fixtures/absolute_claims_labelled_second_instance.json"]
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("file", "path", "paths"):
                for x in ([v] if isinstance(v, str) else v if isinstance(v, list) else []):
                    if isinstance(x, str): yield x
            else: yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
n = m = 0
for c in C:
    for v in walk(json.load(open(c))):
        if not v.startswith("demo-output"): continue
        n += 1; m += L.resolve(v) is None
print("path fields", n, "unresolved", m)
sys.exit(1 if (n != 223 or m) else 0)
EOF

# G3  the shim still binds every root it claims
python3 -c "import sys;sys.path.insert(0,'scripts');import lab_paths as L;\
print(L.unknown_reason(*L.RECORD_ROOT_NAMES) or 'roots OK'); print(L.AMBIGUOUS)"
```

G2's counted total is the gate. **A count that FELL is a blinded instrument; a
count that ROSE is a corpus that absorbed something it should not have.**
Neither is a pass. And per §9.1's third clause, fire one control both ways —
plant a path that must resolve and one that must not — because a corpus whose
every field resolves can still have stopped discriminating.

---

| # | Batch | Invariant | Verification | What breaks if the next batch never lands |
|---:|---|---|---|---|
| **0** | Supersede F1 | No path changes. `git ls-files \| wc -l` unchanged | `--no-tests`; `git ls-files \| wc -l` = 13,814 ± peers | **Nothing.** `PHASE2_MOVE_MAP.tsv` is marked stale, which is strictly better than the current state. This batch is safe to land alone and permanently |
| **1** | Untrack the already-ignored — **LANDED** | Files leave the index, none leaves disk | `comm` over the two `ls-files` frames: 6,950 out, all U-rule; `find` counts on disk unchanged | **Nothing.** Already stable in this state and defensible with no reference to the target tree |
| **2** | `.gitignore` rebuild + untrack §7.2 | Same as 1, plus: **no move source loses its last tracked file** | `hand_carry.py derive` — the *goes-dark-after-batch-2* section must read **0** afterwards, not 1 | **Nothing breaks, but batch 7 becomes impossible.** `MESH_AUDIT_runs` goes dark and R20's `git mv` of it aborts, taking every source in that invocation with it. Stopping here is safe; proceeding to 7 without §3.3's fix is not |
| **3a** | `lab_paths` module + tests — **this commit** | Behaviour-identical. No consumer imports it yet; `scripts/lab_check.py` classifies it *no-entry-point* and never runs it | `pytest sdk/tests/test_lab_paths.py sdk/tests/test_hand_carry.py` (59 passed); full suite | **Nothing.** Two new modules nothing imports and 59 tests. Dead weight, not a defect |
| **3b** | Convert the 13 split constants + ~150 mechanical ones to import it | Behaviour-identical: every constant resolves to the same path it did before | full suite; `git grep -c 'demo-output' -- '*.py' '*.sh'` falls, and G3 | **Nothing at rest.** Consumers read the same paths through one module. This is the batch that makes 4-8 edit one file instead of thirteen; skipping it makes every later batch thirteen times more expensive, but breaks nothing |
| **4** | Leaves: `media/` (R10 R11 R12 R2), `ops/` (R6 R8 R19), `docs/` (R1) — 871 files | **Every `git mv` names a DIRECTORY, one source per invocation, stderr never redirected** | full suite + `crontab -l` read back + `/usr/local/bin/auto-stop.sh` re-installed via `installed_registry.py` + G1 G2 G3 | **The crontab dangles.** `@reboot` invokes `scripts/demo_servers.sh`, which R8 moves to `ops/`. No repo sweep sees it. The re-install of `/usr/local/bin/auto-stop.sh` is in this batch for the same reason. Halting here leaves a box that does not come back up correctly after a reboot, and **that is the one batch whose incompleteness is not visible from inside the repository** |
| **5** | Research: R14-R18, R23 — 437 files, incl. R6's proposals move | Directory granularity. The R23 many-to-one merges preserve the child segment (§5 below) | full suite + G1 G2 G3 + `python3 -c "import json,glob;[json.load(open(p)) for p in glob.glob('research/agenda/proposals/*.json')]"` | **`research/closure/` is half-assembled.** R14/R15/R18 put `benchmarks.json`, `benchmarks.png` and `wall.json` under it while R23's four `closure_*` source trees are still under the webroot, so a reader finds a `research/closure/` that contains the outputs and none of the inputs. Recoverable, and legible, but the directory lies about itself until batch 5 completes |
| **6** | Cases: R5, R22 — 3,553 files | Directory granularity. **786 files under `dafoam/**/work_sail/` are root-owned** — `chown` them BEFORE the batch, not on discovery | full suite + G1 G2 G3 + `find cases -user root \| wc -l` | **`cases/` and the webroot both hold physics families.** The R22 sources are ten separate directories, so a partial batch is a tree where `cases/tmr` exists and `cases/dafoam` does not. Every citation still resolves through `lab_paths.resolve()`, which is what makes stopping here survivable rather than merely bad |
| **7** | Verification: R20, R21, R24 — 8,216 files, the mass | Directory granularity per run archive. **`campaign/` is never moved as a unit** — R20 and R21 split it | full suite + G1 G2 G3 + `hand_carry.py derive` carry set unchanged | **`verification/campaign/` and `verification/runs/` are populated and `demo-output/website/campaign/` still exists.** The 45 `LADDER_V_*` records keep their `campaign/` segment either way, so intra-ladder citations survive. This is the largest batch and the one most likely to be stopped part-way; it is also the one where `git status --porcelain` is most useless — it reported **19,975 renames** at the reverted attempt, pairing byte-identical OpenFOAM case files across unrelated studies. **Git's rename inference is never quoted here** |
| **7H** | **The hand-carry** — §3.1's two trees, plus `MESH_AUDIT_runs` if batch 2 took it | Source empty or gone; destination holds the **exact measured path set**, not merely the count | `hand_carry.py plan --manifest M` → `carry --manifest M` → `verify --manifest M`; **and the `.gitignore` re-points of §3.2 in the same commit** | **1.51 GB is in the old tree while four modules look for it in the new one.** `dispatch_queue.py:63`, `check_convergence_sweep.py:62`, `contention_audit.py:55` and `launch_solve.sh:21` would find an empty or absent directory. `dispatch_queue.py:137` guards with `if REGISTRY.is_dir()`, so **it returns an empty record set rather than raising** — a dispatch audit that silently sees no jobs. This batch has no suite signal at all and is why the carry verifies itself |
| **8** | **The webroot cut** — R13, 5 files, **with every §5 re-point in the same commit** | The four pages answer over HTTP after the commit | full suite + a live fetch of all four pages off port 8080 + G1 G2 G3 | **A live surface goes down.** This is the only batch that can do that, which is why it is last. If it lands and batch 9 never does, `check_evidence_paths_exist` walks a webroot with five files in it and reports a clean sweep of nothing — §6 |
| **9** | The guard resolver | `check_evidence_paths_exist` resolves a citation at its literal location **or** its successor, via `lab_paths.resolve()` | full suite + a planted control both ways: a citation that must resolve and one that must not | **`check_evidence_paths_exist` is blind.** 1,236 backticked `demo-output/…` citations across 234 records, and after batch 8 the guard's `WEB.rglob("*.md")` reaches almost none of them. It does not fail — it scans fewer documents and passes. That is the silent-zero failure this corpus has recorded repeatedly, and it is the reason batch 9 is not optional |

**Order rationale.** Batches 0-3b change no path and are individually revertible
with no residue. Batch 3a in particular is free: two modules nothing imports.
Batches 4-7 move, in increasing order of mass, so that the mechanics are proven
on 871 files before they are trusted with 8,216. Batch 8 is last because it is
the only one that can take a live surface down.

**A batch fails** on suite exit 1 **or** 3, on any `git mv` reporting to stderr,
on any file count not matching its predicted delta, or on G1/G2/G3. The response
is rollback, not repair-forward.

**Rollback, and it is never `git reset --hard` alone.** That restores tracked
files and leaves the gitignored siblings that followed the physical rename in
the new directories, where `git status` will not show them and `git clean` would
delete them. Every move batch carries a written inverse-`mv` list produced
*before* it runs; `hand_carry.py plan` emits one for the carry set, and batches
4-7 need the equivalent for §3.4's 931 ride-along trees. **A batch without its
inverse list does not start.**

---

## 5. What must land in the same commit as a code change, and why

Two classes, and they fail differently.

**Class 1 — the shipping surfaces (R2/batch 8).** Every line in §5 of the map
must land in the commit that moves the file it names, or a live surface breaks
*between* commits: `build_wall.py:38`'s `_OUT` splitting into two constants,
`build_benchmarks.py:51-52`, `demo_servers.sh:46`'s `--directory`,
`audit_camera_discretion.sh:141-142`'s `PAGES` array,
`build_laptop_bundle.py:514`, `self_audit.py:6484-6489`'s `_BUNDLE_PAGES`, and
`test_head_engineer.py:164,241,418`.

**Class 2 — `check_absolutes.py:707`'s `_SHIPPING_RE`, which must land in the
move commit and NOT BEFORE.** No `web/` path exists yet, so adding the
alternative early is a rule matching nothing. Its post-move form is
`^(?:web/|.*/latex/|.*\.tex$)`. §2.1 establishes this is a severity-ranking
degradation and not a fail-open, so it lands at the priority a ranking defect
earns — but it lands in that commit, because the window in which it is wrong is
the window in which somebody reads the ranking.

**`test_head_engineer.py:418` is worse than a failure — it is silent.**
`vetted_case_reason` (`head_engineer.py:137-143`) does a `str.endswith` suffix
match and never touches disk, so after the move **the test still passes while
asserting on a path that no longer exists.** It is the reason a green suite is
necessary and not sufficient evidence for any batch here.

**One decision this plan makes that the map left open.** §2.2's R23 sends four
`closure_*` source directories to `research/closure` without saying whether each
keeps its own segment. R21 *does* preserve its segment, and §6 gives the reason:
a preserved segment keeps every relative citation in 45 ladder records alive.
**`lab_paths` applies that reasoning uniformly and preserves the child segment
on every many-to-one merge** — `research/closure/closure_eval/`,
`cases/tmr/tmr-naca0012-transient-300cu/`, `research/race/race-gui/`. §4.3's own
example (`battery_common.py:59`, `closure_eval/` → `research/closure/`) reads the
other way. The decision sits in exactly one place, `lab_paths._MOVES`, and
**batch 5 must ratify it before it runs.**

---

## 6. `scripts/lab_paths.py` — what it is and why it is shaped this way

One module, imported rather than re-spelled. §4's census found the prefix was
*already* being re-spelled — 8 times in `test_rank_claim_surfaces.py`, 4 in
`model_form_batch.py`, 3 verbatim in `mega_batch_keeper.sh` — so a repair that
fixes 13 constants and leaves that pattern buys the next reorganisation the same
bill.

**Every name is bound to a PAIR — legacy and successor — and resolved against
the filesystem at import.** Resolution order: the successor if it exists, else
the legacy path if it exists, else the legacy path *and* the name recorded in
`UNRESOLVED`. That is what lets the same module be correct before the move,
between batches 4 and 8 with the tree half-migrated, and after — **with no edit
to it between batches.** The map's batch 3 asked for a module holding *current*
paths that later batches would rewrite; holding both is strictly better, and it
is why 3a can land today with §8 still years away in the ordering.

**It does not fail open**, and §2.2 is why. `require()` raises on an unresolved
name rather than handing back a path that is not there. `unknown_reason()`
returns the sentence a check prints before exiting 3. `resolve()` returns `None`
for a citation to something that never existed. The load-bearing half of the
suite is the must-not-match control beside each of those: a shim that always
answered UNKNOWN would satisfy every fail-closed assertion and be worthless.
Evidence: `test_require_raises_rather_than_returning_a_path_that_is_not_there`,
`test_unknown_reason_names_the_missing_roots`,
`test_resolve_returns_none_for_something_that_never_existed`, and the control
`test_the_must_not_match_control`.

It also supplies the three things §4.1 and §5 named as having no single
successor:

- `RECORD_ROOTS()` replaces `WEB.rglob("*.md")` (`self_audit.py:4319`, `:4837`),
  deduplicated so that pre-move — when every root is under the one webroot — it
  does not walk it twice and double-count every finding.
- `SWEEP_ROOTS()` replaces `self_audit.py:4309`'s whitelist and, **before the
  move, reproduces its exact seven roots** — pinned by a test that reads them
  out of `self_audit.py`'s source rather than from a copy, so drift on either
  side reddens.
- `BUNDLE_PAGES()` replaces `self_audit.py:6484-6489`'s triple, pinned the same
  way.
- `redirect()` is the MOVE_MAP as a function, and is what batch 9's guard
  resolver is built on.

**37 tests, 67 subtests**, in `sdk/tests/`. Seven mutants planted in the module — campaign split
inverted, never-move dropped, `require` fails open, `unknown_reason` always
clean, the TMR merge flattened into a collision, `resolve` falls back to a path
that is not there, the served PNG losing to the campaign split — and **each was
caught by the specific test written for it**, not by collateral.

`scripts/hand_carry.py` carries 22 tests with **ten** mutants, including two
that survived the first cut and were only caught after the tests that should
have caught them were found to be masked: one by the drift check firing first,
one because nothing exercised the check inside `carry` as opposed to the one
inside `verify`. Both are now pinned. Evidence:
`test_a_tree_that_gained_a_tracked_file_is_refused`, rewritten to commit a file
already on disk so the counts do not move and the drift check cannot mask it,
and `test_the_carry_itself_reddens_when_the_move_does_not_land_it_all`.

**One instrument observation, recorded because it will recur.**
`check_absolutes.py`'s `_named_checks` resolves a `test_*` token against
`known_test_names()`, which harvests **function and class definitions** from
`git ls-files`. A test MODULE's filename therefore never resolves: writing
`sdk/tests/test_lab_paths.py` in prose yields the token `test_lab_paths`, which
is not a function, and the unit is condemned `CITES_MISSING_CHECK` — the more
severe class, because a dangling name beside a resolving one is deliberately
not rescued by it. Every `Evidence:` line in this record and in both new
modules therefore names **functions**, not files. Two consequences worth
carrying forward: a record that cites a test file by name is charged for it,
and a citation to a test that is landing in the same commit dangles until that
commit lands, because the harvester reads the tracked frame.

---

## 7. What this pass did not do

No file was moved, renamed, copied, deleted or untracked. No directory was
created or removed. `.gitignore` was not edited. `git mv` was not invoked. The
shared index was not touched: no `git add`, no `git read-tree` against it, and
the 47 staged deletions it reports were left exactly as found. No consumer was
converted to import `lab_paths`; §4.3's ~150 mechanical rewrites are batch 3b
and are not in this commit. No solver was launched and nothing was registered.
