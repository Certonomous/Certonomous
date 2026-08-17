# AWS_TREE_PLAN: inventory and reorganisation plan for `/home/ubuntu`

**Status: INVENTORY AND PLAN ONLY. Nothing has been moved, renamed or deleted.**
Every path below is where it was when this was written. Execution is a separate
authorised step.

Frame taken 2026-08-17, 15:00–15:40 UTC, on `ip-172-31-43-247`. Scope is
everything under `/home/ubuntu` **except** the tracked contents of the two git
repositories `Certonomous/` and `Certonomous_closure_challenge/`, which have
their own reorganisation order.

---

## 0. How to read this, and what "size" means here

Three different byte quantities appear in this lab and they are not
interchangeable. This page states which one each figure is, every time.

| Quantity | How obtained | What it counts |
|---|---|---|
| **Apparent** | summed `st_size` over regular files | every hardlink instance separately |
| **Deduplicated** | same, keyed on `(st_dev, st_ino)` | each inode once |
| **Disk usage** | `du -s --block-size=1` | allocated blocks, plus directory inodes |

All totals on this page are **decimal bytes** (GB = 10⁹ B), summed from
unrounded byte counts. **No figure here is a GiB reading relabelled as GB.**
Where `du` was used it is named as `du`.

Every classification row also carries the class it belongs to, and each path in
scope appears in **exactly one** class.

---

## 1. Walk integrity: were the counts taken over a moving target?

The brief warns that full-tree walks under concurrency have silently lost files
here (three sweeps one night lost 238, then 119, then 0), and that
`find … | wc -l` discards those failures to stderr.

**This frame captured stderr on every walk. Zero walk errors were recorded.**

| Walk | Method | Errors captured |
|---|---|---|
| Per-directory file counts | `/usr/bin/find … -type f 2>>walk_err_<dir>.txt` | 0 across all 11 directories |
| Byte/inode measurement | `os.walk(onerror=…)` + `lstat`, errors collected | 0 |
| Duplicate hash sweep | `os.walk(onerror=…)` + full-file MD5 | 0 |
| `du -sb` on all nine in-scope directories | stderr redirected to file | 0 |

**Were the counts over a moving target?** Partly, and here is exactly where.

- **Stable during this frame:** `certonomous-runs/`, `backups/`, `OpenFOAM/`,
  `closure-venv/`, `dafoam-tutorials/`, `memory-import/`, `__pycache__/`,
  `closure-challenge-benchmark/`, `closure-challenge-pkg/`. Every one of these
  reproduced its LOCATIONS.md file count **exactly** (§2 below), which would be
  a remarkable coincidence if a walk had dropped files.
- **Moving during this frame:** three loose log files —
  `control_room.log`, `static_site.log`, `demo_servers.log` — are being appended
  to by a **live server process** (§7.6). Their byte counts are a reading at
  14:49 UTC and will have grown since.
- **Out of scope but moving:** `Certonomous_closure_challenge/` is the volatile
  working copy LOCATIONS.md §4.3 already flags; it read 201 files here against
  164 at frame `8cefb4e9`.
- **Out of scope and moving hard:** the `Certonomous/` repository itself was
  being committed to *during* this frame — HEAD advanced from `101079fd` to
  `7c606b74` across two commits while this page was being written, and its index
  currently holds an unrelated in-flight staged change (47 deletions, 6
  modifications, 0 additions; every affected file still present on disk). None
  of that touches the classification here, because the repo's tracked contents
  are outside this plan's scope — but no figure on this page should be read as a
  statement about the repository's tracked arm.

So: the size and count figures for the nine in-scope directories are solid; the
three live log sizes are floors, not censuses.

---

## 2. Verification of LOCATIONS.md — every in-scope figure re-derived

LOCATIONS.md was treated as an index to check, not to trust. **Every in-scope
figure it states still holds.** Nothing has drifted.

| LOCATIONS.md claim | Stated there | Measured now | Verdict |
|---|---|---|---|
| Run tree, regular files | 132,049 | 132,049 | ✅ exact |
| Run tree, symlinks | 748 | 748 | ✅ exact |
| Run tree, loose files at tree root | 36 | 36 | ✅ exact |
| Run tree, top-level study dirs | 446 | 446 | ✅ exact |
| Run tree, extra hardlink instances | 135 | 135 | ✅ exact |
| Run tree, apparent | 75.79 GB | 75.790 GB (75,789,971,753 B) | ✅ exact |
| Run tree, deduplicated | 69.36 GB | 69.365 GB (69,364,664,057 B) | ✅ exact |
| Benchmark clone, files | 6,263 | 6,263 | ✅ exact |
| Benchmark clone, size | 1.30 GB | 1.301 GB | ✅ exact |
| Benchmark clone, pinned commit | `deb91557…` | `deb91557184af3cb95f5190494ec52d8f2c6a0d1` | ✅ exact |
| `closure-venv/`, files | 9,797 | 9,797 | ✅ exact |
| `closure-venv/`, size | 0.38 GB | 0.376 GB | ✅ exact |
| `backups/`, files | 8 | 8 | ✅ exact |
| `backups/`, size | 0.36 GB | 0.359 GB | ✅ exact |
| `dafoam-tutorials/`, files | 1,215 | 1,215 | ✅ exact |
| `OpenFOAM/`, files | 19 | 19 | ✅ exact |
| `closure-challenge-pkg/`, files | 84 | 84 | ✅ exact |
| `memory-import/`, files | 8 | 8 | ✅ exact |
| §4.3 total, files | 17,558 | 17,558 (using its own 164 for the volatile row) | ✅ exact |
| Loose files in `/home/ubuntu` | 39, 0.91 GB | 39, 0.909 GB (909,065,714 B) | ✅ exact |
| Two tarballs carry almost all loose bytes | 0.544 + 0.362 GB | 544,309,252 + 362,066,284 B | ✅ exact |

**One sub-rounding note, reported for completeness, not as a drift.**
LOCATIONS.md §6 says the run tree's deduplicated byte count "matches `du -sb`
exactly". Measured here, deduplicated regular-file bytes are 69,364,664,057 and
`du -sb` is 69,364,681,327 — a difference of **17,270 bytes**, which is `du`
also counting directory inodes. Both round to 69.36 GB. This is a definitional
detail in the LOCATIONS.md wording, not a change in the tree.

### 2.1 What LOCATIONS.md does *not* cover

LOCATIONS.md enumerates the run tree, the named directories and the loose files.
It does **not** enumerate the dotted directories in `/home/ubuntu`, which hold
**13.87 GB** — more than six times the 2.06 GB its §4.3 "everything else" total
covers. Two of them are load-bearing evidence by its own §4.5 argument.

| Dotted directory | Files | `du -sb` | Note |
|---|---|---|---|
| `.mutarc-64b13819/` | 20,853 | 7,036,239,167 | **undocumented 7.04 GB git tree — see §8 ASK-1** |
| `.claude/` | 3,648 | 1,790,759,298 | agent dispatch records (LOCATIONS §4.5 evidence) |
| `.claude-sanaa/` | 3,273 | 1,762,655,576 | agent dispatch records (LOCATIONS §4.5 evidence) |
| `.local/` | 9,627 | 1,291,641,783 | user-installed tooling |
| `.cache/` | 302 | 125,677,762 | caches |
| `.texlive2023/` | 23 | 621,612 | TeX Live user tree |
| `.npm/` | 13 | 19,519 | npm cache |
| `.ssh/` | 10 | 3,167 | keys — do not relocate |
| `.config/` | 2 | 115 | |
| **Total** | **37,751** | **13,867,617,999 (13.87 GB)** | |

Agent dispatch records found: **1,557** `agent-*.jsonl` files across
`.claude/projects/` and `.claude-sanaa/projects/`. These are the only sound
evidence for R-ISOLATE (LOCATIONS.md §4.5) and no clone contains them.

**Recommendation: LOCATIONS.md should gain a section for the dotted
directories.** A reader following it today would conclude that everything
outside the repos and the run tree is 2.06 GB, and would be wrong by 13.87 GB —
including the entire independence-evidence corpus that §4.5 declares
irreplaceable.

---

## 3. Proposed target tree

The organising principle: **a newcomer should be able to tell, from the folder
name alone, whether a thing is evidence, an upstream import, a tool, or
scratch.** Two constraints override tidiness and are stated up front in §4.

```
/home/ubuntu/
├── Certonomous/                  # git repo — own reorganisation order, untouched here
├── Certonomous_closure_challenge/# git repo — own reorganisation order, untouched here
│
├── evidence/                     # NOTHING IN HERE IS EVER DELETED OR REWRITTEN
│   ├── runs/                     # ← certonomous-runs/  (MUST stay a stable path, §4.3)
│   ├── ledger-backups/           # ← backups/           recovery points for a gitignored ledger
│   ├── leaderboard/              # ← scratch_live_readme.md, renamed & dated
│   ├── status-records/           # ← NIGHT_STATUS.md, MIGRATION_STATUS.md
│   └── provisioning-logs/        # ← provision.log, suite*.log, openvsp.log
│
├── upstream/                     # third-party clones, pinned, re-clonable, never edited
│   ├── closure-challenge-benchmark/   # pinned deb91557…
│   ├── closure-challenge-pkg/         # pinned 1c4e22c  (MUST stay a stable path, §4.2)
│   └── dafoam-tutorials/              # pinned d3b7e38b
│
├── toolchain/                    # things that must exist at a fixed path to run
│   ├── OpenFOAM/  → symlink or in-place   (MUST stay a stable path, §4.1)
│   └── closure-venv/ → symlink or in-place (MUST stay a stable path, §4.2)
│
├── lab-scripts/                  # lab-authored loose scripts, deduplicated & versioned
│   ├── paraview-render/          # ← render_naca_*.py, test_paraview_*.py
│   └── plugins/                  # ← solverless_plugin.py
│
├── notes/                        # ← memory-import/  (agent memory notes)
│
├── archives/                     # ← the two large tarballs
│
└── var/log/                      # ← control_room.log, static_site.log, demo_servers.log
                                  #   (live append targets — see §4.4)
```

Every directory gets a `README.md` stating: what it is, whether it may be
deleted, what regenerates it, and what points at it.

---

## 4. Four hard constraints. Read before proposing any move.

These are the reasons the target tree above uses symlinks rather than clean
moves in three places. Each was verified by reading the referencing file, not
assumed.

### 4.1 `OpenFOAM/` is a hard-coded install target for published solvers

`OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/{bin,lib}` is what
`$FOAM_USER_APPBIN` / `$FOAM_USER_LIBBIN` resolve to. Published cases name these
binaries directly:

- `Certonomous/demo-output/website/campaign/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/Make/files`
  contains `EXE = $(FOAM_USER_APPBIN)/rhoCentralFoamBounded`
- `…/swbli_cylflare/warmup20_bounded/system/controlDict` and
  `…/warmup20_bounded_realtime/system/controlDict` both contain
  `application     rhoCentralFoamBounded;`
- run-tree studies `w3-qcr-duct/` and `w3-qcr-rank1/` load
  `libkOmegaSSTQCRTurbulenceModels` — confirmed present in
  `w3-qcr-duct/AR_10_Ret_180_qcr/system/controlDict`,
  `…/constant/turbulenceProperties` and `…/log.simpleFoam`

**Moving `OpenFOAM/` breaks re-running every one of those cases.** If it is
relocated, `~/OpenFOAM` must remain as a symlink.

### 4.2 `closure-venv/` is load-bearing, and it is coupled to `closure-challenge-pkg/` by absolute path

The brief asked what references the venv before anything is proposed. Checked,
and the answer is: a great deal.

**Exactly 15 reproduction scripts hard-code the interpreter path**, plus one
test fixture. This is a **complete** enumeration over `sdk/`, `scripts/` and
`docs/`, re-derived with no `head` after the truncation trap in §7.4 was found:
`/usr/bin/grep -rl -I "closure-venv" Certonomous/{sdk,scripts,docs}` returns 16
files — the 15 below plus
`sdk/tests/fixtures/absolute_claims_labelled_second_instance.json`.

**Scope limit, stated rather than glossed:** `demo-output/` was **not**
exhaustively counted — a full sweep of it timed out twice (it is the 11.9 GB
gitignored arm). At least one reference is known to exist there
(`ladder-b/B2_duct_baseline.json`, below). So 16 is a complete count for
`sdk/scripts/docs` and a **floor** for the repository as a whole.

Each of the 15 verified by reading the file:

| Script (under `sdk/scripts/`) | Hard-coded reference |
|---|---|
| `closure_duct_feature_degeneracy.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_decline_gate_audit.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_round5_points_order_check.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_ph_seed_sensitivity.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_round4_duct_rescale.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_eval_battery/build_master_table.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_eval_battery/run_ph_battery.py` | `taskset -c 0-1 /home/ubuntu/closure-venv/bin/python` |
| `closure_eval_battery/run_duct_battery.py` | `taskset -c 0-1 /home/ubuntu/closure-venv/bin/python` |
| `closure_round5_qcr_forward.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_round4_manifest.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_divergence_audit.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_duct_reynolds_transfer.py` | `/home/ubuntu/closure-venv/bin/python` |
| `closure_baseline_error_gate.py` | `source ~/closure-venv/bin/activate` |
| `train_closure_alpha05_regime_model.py` | `source ~/closure-venv/bin/activate` |
| `run_closure_challenge_evidence.py` | `python -m venv ~/closure-venv && source ~/closure-venv/bin/activate` |

**And a published evidence record names the venv as the scoring environment:**
`demo-output/website/dafoam/ladder-b/B2_duct_baseline.json` field
`scoring_environment`. When this plan was written that field read
`"~/closure-venv (numpy, scipy, Ofpp, closure_challenge==0.2.1)"`; on 2026-08-17
its prose was amended to pin the scorer by commit hash instead (§7.5), so it now
opens `"~/closure-venv (numpy, scipy, Ofpp), scoring through the eval package
clone /home/ubuntu/closure-challenge-pkg pinned at commit 1c4e22c8…"`. **No
figure in that record changed.** The point for this plan is unchanged: the venv
is named by a published record and cannot be quietly discarded.

**The venv also contains an editable install pointing outside itself:**

- `closure-venv/lib/python3.12/site-packages/_editable_impl_closure_challenge.pth`
  contains the single line `/home/ubuntu/closure-challenge-pkg/src`
- `closure-venv/lib/python3.12/site-packages/closure_challenge-0.3.1.dist-info/direct_url.json`
  contains `{"dir_info": {"editable": true}, "url": "file:///home/ubuntu/closure-challenge-pkg"}`

So `closure-venv/` and `closure-challenge-pkg/` are welded together at absolute
paths. **Moving either one, on its own, silently breaks `import
closure_challenge` in every script above.**

**Corrected 2026-08-17.** This paragraph previously read: *"Note also the version
skew worth flagging: the recorded scoring environment says
`closure_challenge==0.2.1`, while what is installed today is `0.3.1`."* And the
next one: *"rebuilding it will produce 0.3.1, not the 0.2.1 that the published
record names. It is classified **KEEP** on that basis."* **Both were wrong, and
the second put a real classification on a false basis.** There is no skew.
`0.2.1` and `0.3.1` are two reporting mechanisms — `__init__.__version__` and
the `dist-info` metadata — describing the *one* editable install of the *one*
clone pinned at `1c4e22c8`. §7.5 has the demonstration. Because the install is
editable and points at that pinned clone, rebuilding the venv reproduces the
identical scorer, byte for byte; it does not "produce 0.3.1" in any sense that
differs from what is there now.

`closure-venv/` therefore stays **KEEP**, but on the basis that actually holds:
the absolute-path welding to `closure-challenge-pkg` documented just above, the
25 scripts that hard-code paths into it, and a published record
(`B2_duct_baseline.json`) that names it as the scoring environment. It remains
technically REGENERABLE — `python -m venv ~/closure-venv`, per
`run_closure_challenge_evidence.py` — and the reason not to regenerate it is the
coupling, not a version number.

**Bound on the blast radius, measured.** A completed sweep of all 132,049
run-tree files found **zero** references to `closure-venv` (§7.4). The coupling
is entirely to repo scripts and the one published JSON record listed above. A
run-tree replay does not depend on the venv; the closure-challenge scoring path
does, totally.

### 4.3 `certonomous-runs/` is referenced as a stable path

69.36 GB deduplicated of solver evidence with no off-box replica
(LOCATIONS.md §6.3). If it is relocated, `~/certonomous-runs` must remain as a
symlink. Preference: **do not move it at all.** The value of a tidier name does
not exceed the risk to the lab's largest irreplaceable body of work.

### 4.4 Three loose logs are live append targets right now

A server is running as this is written:

```
ubuntu  1453  python3 -u -m http.server 8080 --directory demo-output/website
```

`control_room.log`, `static_site.log` and `demo_servers.log` were all appended to
at 14:49 UTC today. Moving a file that an open file descriptor is writing to
does not redirect the writer. **These may only be relocated while the servers are
stopped**, and whatever launches them must be updated in the same change.

---

## 5. Classification totals by class

Apparent bytes. Every in-scope path is in exactly one class.

| Class | Files | Apparent bytes | GB | Share of bytes |
|---|---:|---:|---:|---:|
| **EVIDENCE, DO NOT TOUCH** | 132,066 | 76,149,287,961 | 76.1493 | 96.6875% |
| **KEEP AND PLACE** | 17,400 | 1,695,962,037 | 1.6960 | 2.1534% |
| **REGENERABLE** | 10 | 6,483,109 | 0.0065 | 0.0082% |
| **DUPLICATE** | 2 | 3,446 | 0.0000 | 0.0000% |
| **ASK** | 5 | 906,388,323 | 0.9064 | 1.1509% |
| **TOTAL IN SCOPE** | **149,483** | **78,758,124,876** | **78.7581** | 100% |

**This reconciles exactly, and the check is the point.** The independent
enumeration of scope is 132,049 (run tree) + 8 (`backups`) + 19 (`OpenFOAM`) +
6,263 (benchmark) + 84 (pkg) + 9,797 (venv) + 1,215 (dafoam) + 8
(`memory-import`) + 1 (`__pycache__`) + 39 (loose, dotfiles included) =
**149,483 files**, and the apparent bytes over that population are
**78,758,124,876**. The five class rows sum to both figures with no residue, so
every path is classified once and nothing has been dropped or double-counted.

Three splits are worth naming because they are where a careless tally would go
wrong:

- `OpenFOAM/`'s 19 files split **10 source → KEEP** and **9 build artifacts →
  REGENERABLE** (§6.2, §6.3).
- `closure-challenge-benchmark/`'s 6,263 files split **6,262 → KEEP** and **1 →
  ASK** (the lab-authored `rans_identity_baseline.py`, ASK-3).
- The 39 loose files split **9 EVIDENCE** (8 logs/records + `.bash_history`),
  **24 KEEP** (13 render/paraview scripts, `solverless_plugin.py`, 3 live logs,
  7 shell/user config dotfiles), **2 DUPLICATE**, **4 ASK** (2 tarballs, 2
  `.bashrc` backups).

**The bottom line for the owner:** 96.7% of the bytes in scope are untouchable
evidence. The population deletable on this plan's own authority is **3,446
bytes** — two proven duplicates — plus 1,819 bytes of Python bytecode. The only
meaningful space on the table is the **0.906 GB** in ASK-5 and ASK-6, and both
need an answer first. **This job is about legibility, not disk.**

---

## 6. Full classification table

### 6.1 EVIDENCE, DO NOT TOUCH

The default class where anything is uncertain.

| Path | Files | Apparent B | Why it is evidence |
|---|---:|---:|---|
| `certonomous-runs/` | 132,049 | 75,789,971,753 | Every solver run the lab has executed. 446 studies, 748 symlinks, 135 extra hardlink instances. No off-box replica exists. LOCATIONS.md §4.1 points at it. |
| └ the 36 files at the run-tree root | (of above) | (of above) | Not incidental: these are the **drivers that produced the runs** — `w3_solve_queue.sh`, `stage_run.sh`, `triage_run.sh`, `a1_run.sh`, `w3_mesh_rung.sh`, `diag_run.sh`, `img_run.sh`, `commit_img.sh`, plus queue logs. They are the record of *how* the tree was generated and sit in no study directory. LOCATIONS.md §4.1 warns they are easy to miss. |
| `backups/` (4 × `.jsonl` + 4 × `.METADATA`) | 8 | 358,757,970 | Recovery points for `Certonomous/demo-output/website/mega-batch/ledger.jsonl`, which is **gitignored** — no clone has it. Each `.METADATA` records source path, MD5, row counts and `Partial tail dropped: YES`. All four are **byte-distinct** (MD5s `0f03fa06…`, `fec7b881…`, `7b2e586e…`, `1c2ee5be…`) and none equals the live ledger (`8c760796…`). Not duplicates; incremental recovery points. |
| `scratch_live_readme.md` | 1 | 10,080 | **Misleadingly named and easy to lose.** This is the retrieved live leaderboard, mtime `2026-08-11 23:33:50 UTC`, which matches LOCATIONS.md §4.2's "retrieved 2026-08-11T23:33Z" to the minute. It carries the six named entrants and their per-case scores. LOCATIONS.md's claim that the benchmark README "is not the live board" rests on this file, **18 repo files derive from it, and 5 of those are executable audit/test code that asserts against the board** (§7.4) — but it is the only copy of the retrieval itself. **Rename is verified safe** — a sweep excluding this file, run to a completion sentinel, found **zero** citations of `scratch_live_readme` in either repository (§7.4; an earlier assertion of this was retracted as unchecked before being re-established properly). Keep the bytes byte-identical and record the old name in the destination README. |
| `NIGHT_STATUS.md` | 1 | 79,268 | Outage post-mortem of 2026-07-27 with figures copied from logs, `sar` samples and filesystem timestamps. A contemporaneous incident record. |
| `MIGRATION_STATUS.md` | 1 | 4,178 | Records instance identity `i-0e417e686a5a6ac1a`, disk state, and the verified-working list at commit `47fffd3`, with the note that no git credentials are stored on this box. Provenance record for the whole machine. |
| `provision.log` | 1 | 305,369 | The actual build log of this instance. |
| `suite.log` | 1 | 135,265 | Test-suite evidence. |
| `suite-47fffd3.log` | 1 | 12,157 | Suite run pinned to commit `47fffd3`, cross-referenced by `MIGRATION_STATUS.md`. |
| `suite-47fffd3-solverless.log` | 1 | 124 | As above, solverless variant. |
| `openvsp.log` | 1 | 406 | Records a **failed** OpenVSP install (corrupt zip). Negative results are evidence; this explains why OpenVSP is absent. |
| `.bash_history` | 1 | 11,391 | A record of what was actually run on this box. Classified evidence under the brief's "when uncertain, this is the default" rule. Stays in `$HOME`; not relocated. |
| **Subtotal** | **132,066** | **76,149,287,961** | **76.1493 GB** |

**Placement:** `certonomous-runs/` stays exactly where it is (§4.3). The rest
move under `evidence/` as mapped in §3. `scratch_live_readme.md` should be
renamed on the move — proposed
`evidence/leaderboard/closure-challenge-live-board-2026-08-11T2333Z.md` — with
its bytes preserved and its old name recorded in the directory README, because
LOCATIONS.md §4.2 cites the retrieval time and a reader will come looking.

### 6.2 KEEP AND PLACE

| Path | Files | Apparent B | Where it goes, and why it earns a place |
|---|---:|---:|---|
| `closure-challenge-benchmark/` (6,262 tracked-upstream files; the 6,263rd is ASK-3) | 6,262 | 1,300,565,636 | → `upstream/`. Pinned at `deb91557184af3cb95f5190494ec52d8f2c6a0d1`, remote `github.com/rmcconke/closure-challenge-benchmark`. Publicly re-clonable, so arguably regenerable — but it is the **scoring** clone the lab's numbers were produced against, and re-cloning would silently take upstream's current tip. Keep pinned. **Carries one untracked lab-authored file — see ASK-3.** |
| `closure-venv/` | 9,797 | 376,085,773 | → stays at `/home/ubuntu/closure-venv` or is symlinked from it. Load-bearing for 15 documented reproduction commands (a complete count over `sdk/scripts/docs`; a floor repo-wide) and named in a published evidence record. Full argument in §4.2. |
| `dafoam-tutorials/` | 1,215 | 13,513,420 | → `upstream/`. Clean clone of `github.com/DAFoam/tutorials` at `d3b7e38b058aba2a98a74092e15c41ec455c570d`, **working tree clean** — verified, no local modifications. Reference cases for the DAFoam work. |
| `closure-challenge-pkg/` | 84 | 3,639,704 | → stays at `/home/ubuntu/closure-challenge-pkg` or is symlinked from it. Pinned at `1c4e22c` ("v0.3.1: vector magnitude metric, mean over cases"), remote `github.com/rmcconke/closure-challenge`. **The venv's editable install points here by absolute path** (§4.2). |
| `memory-import/` | 8 | 18,963 | → `notes/`. Eight hand-written agent-memory notes: `MEMORY.md`, `supervisor-delegation-doctrine.md`, `clock-audit-before-rate-judgments.md`, `katie-gui-conventions.md`, `openvsp-wsl-install.md`, `port-8765-reuseaddr-trap.md`, `wsl-glob-quoting-trap.md`, `wsl-glob-substitution-trap.md`. Lab-authored operating knowledge, not derived from anything. Small and genuinely useful to a newcomer. |
| `OpenFOAM/…/rhoCentralFoamBounded/` **source only** (10 files: `.C`, 6 × `.H`, `Make/files`, `Make/options`) | 10 | 20,007 | → stays in place (§4.1). **This is the authoritative copy.** The repo copy at `Certonomous/demo-output/website/campaign/F4_runs/swbli_cylflare/rhoCentralFoamBounded_src/` is **incomplete** — verified by `diff -rq`, it is missing `centralCourantNo.H`, `createFieldRefs.H`, `directionInterpolate.H`, `readFluxScheme.H` and `setRDeltaT.H`. The one file both hold, `rhoCentralFoamBounded.C`, is byte-identical (`b2d49a38…`). Do not treat the repo copy as the survivor; it cannot rebuild the solver. |
| `render_naca_*.py` (6) + `test_paraview_*.py` (7) | 13 | 38,691 | → `lab-scripts/paraview-render/`. All 13 are **byte-distinct** (13 distinct MD5s) — a version ladder, not copies. See ASK-4 on whether the superseded rungs are wanted. |
| `solverless_plugin.py` | 1 | 1,045 | → `lab-scripts/plugins/`. Lab-authored; `suite-47fffd3-solverless.log` is its run record, so the two belong together conceptually and the READMEs should cross-reference. |
| `control_room.log`, `static_site.log`, `demo_servers.log` | 3 | 2,026,268 | → `var/log/`, **but only with the servers stopped** (§4.4). Sizes are floors: these were being appended to during the frame. |
| `.bashrc`, `.profile`, `.bash_logout`, `.claude.json`, `.lesshst`, `.wget-hsts`, `.sudo_as_admin_successful` | 7 | 52,530 | **Stay exactly where they are.** Shell and user configuration that only works in `$HOME`. Listed for completeness of the 39-file loose population, not because anything should happen to them. |
| **Subtotal** | **17,400** | **1,695,962,037** | **1.6960 GB** |

### 6.3 REGENERABLE

| Path | Files | Apparent B | Command that reproduces it |
|---|---:|---:|---|
| `__pycache__/solverless_plugin.cpython-312-pytest-9.1.1.pyc` | 1 | 1,819 | Any `pytest` run over `solverless_plugin.py`. Bytecode cache, nothing else. The directory sitting bare in `$HOME` is exactly the "random" artefact the owner wants gone. |
| `OpenFOAM/…/platforms/linux64GccDPInt32Opt/lib/libspartaTurbulenceModels.so` | 1 | 1,574,800 | `wmake libso` in `Certonomous/sdk/openfoam/sparta/spartaTurbulenceModels/` (sources confirmed present: `kOmegaSSTCorrected.C`, `kOmegaSSTFrozen.C`, `spartaTurbulenceModels.C`) |
| `OpenFOAM/…/platforms/…/lib/libkOmegaSSTQCRTurbulenceModels.so` | 1 | 1,389,504 | `wmake libso` from the same sparta source tree |
| `OpenFOAM/…/platforms/…/bin/rhoCentralFoamBounded` | 1 | 970,456 | `wmake` in `OpenFOAM/ubuntu-v2606/applications/solvers/compressible/rhoCentralFoamBounded/` |
| `OpenFOAM/…/platforms/…/bin/kCorrectiveFrozenFoam` | 1 | 673,856 | `wmake` in `Certonomous/sdk/openfoam/sparta/kCorrectiveFrozenFoam/` (source `kCorrectiveFrozenFoam.C` confirmed present) |
| `OpenFOAM/…/rhoCentralFoamBounded/Make/linux64GccDPInt32Opt/` (`.o`, `.dep`, `sourceFiles`, `variables`, `options`) | 5 | 1,872,674 | Intermediate `wmake` output; recreated by the same `wmake` |
| **Subtotal** | **10** | **6,483,109** | **0.0065 GB** |

**Classified regenerable, but flagged: do not delete these without asking
(ASK-2).** They are the exact binaries that produced published results. A rebuild
is not guaranteed bit-identical, the build procedure is **not documented
anywhere in the repo** — a search for `WM_PROJECT_USER_DIR` or
`OpenFOAM/ubuntu-v2606` across `Certonomous/{sdk,scripts,docs}` returned **zero
hits** — and deleting them breaks §4.1's reproduction paths until someone
rebuilds. The honest status is "regenerable in principle, undocumented in
practice". **Writing that build procedure down is the prerequisite for ever
deleting them,** and is a worthwhile task in its own right.

### 6.4 DUPLICATE

Proven by full-file MD5, not by name or size.

| Path | Bytes | MD5 | Survivor (the copy to keep) | What references it |
|---|---:|---|---|---|
| `/home/ubuntu/lab.sh` | 779 | `18f449fa06e2a35c50a937f8c2ac3d25` | `Certonomous/scripts/installed/lab.sh` — **identical MD5**, and it is tracked in git, so it survives loss of this box | Nothing found referencing the `$HOME` copy by path. The repo path is the installed location by its own directory name. |
| `/home/ubuntu/provision.sh` | 2,667 | `7d39bacd7bff83609df4aace425124ec` | `Certonomous/docs/aws/provision.sh` — **identical MD5**, tracked in git | `provision.log` is the run record of this script; the log stays as EVIDENCE regardless. |
| **Subtotal** | **3,446** | | | |

**That is the entire actionable duplicate population in scope: 3,446 bytes.**

**A further 73,166,836 bytes (73.17 MB) of byte-identical redundancy exists, and
none of it should be touched.** A full MD5 sweep across all in-scope
directories (0 errors) found 377 duplicate groups. Every one of them lies
*inside* a pinned upstream clone:

| Redundancy located in | Redundant bytes | Why it must stay |
|---|---:|---|
| within `closure-challenge-benchmark/` | 67,825,675 | Upstream's own layout — e.g. `data/PH_Breuer/constant/polyMesh/faces` repeated across 30 `Parm_PH_29` case directories, and `NASA_2DWMH/0/` vs `2000/` field pairs. Deleting any of it dirties a clone pinned at `deb91557…`. |
| within `dafoam-tutorials/` | 4,284,769 | Upstream's own layout — e.g. `Ramp/steady/train/{c1,c2,tf_training}/constant/polyMesh/points.gz` across 11 cases. |
| `closure-challenge-benchmark/` ↔ `closure-challenge-pkg/` | 602,506 | Test fixtures under `pkg/tests/example_submission/` that match `benchmark/data/evaluation_points/`. Two independent upstream repos; each needs its own copy. |
| within `closure-venv/` | 400,992 | Ordinary site-packages duplication. |
| three-way, incl. `dafoam-tutorials/` | 52,370 | As above. |
| within `closure-challenge-pkg/` | 524 | Upstream's own. |

**No lab-authored file was found duplicated against another lab-authored file
anywhere in scope**, other than the two `$HOME` copies in the table above.

### 6.5 ASK

Five paths whose class cannot be settled without the owner. Full questions in §8.

| Path | Files | Apparent B | Question |
|---|---:|---:|---|
| `certonomous-git-backup-20260730T033814Z.tar.gz` | 1 | 544,309,252 | ASK-5 |
| `certonomous-cache.tar.gz` | 1 | 362,066,284 | ASK-6 |
| `.bashrc.bak` | 1 | 5,880 | ASK-7 |
| `.bashrc.bak2` | 1 | 4,080 | ASK-7 |
| `closure-challenge-benchmark/scripts/rans_identity_baseline.py` | 1 | 2,827 | ASK-3 |
| **Subtotal** | **5** | **906,388,323** | **0.9064 GB** |

**The default for every one of these while unanswered is: do nothing.** If
ASK-5 and ASK-6 are both answered "delete", **0.906 GB** is recoverable — the
only meaningful quantity of space in this entire plan. ASK-3 points the other
way: that file may need *more* protection, not less.

Two further ASK items (ASK-1, ASK-2) concern paths that are classified
elsewhere — `.mutarc-64b13819/` is outside the enumerated scope, and the
OpenFOAM binaries sit in REGENERABLE §6.3 with a hold placed on them. Neither
adds bytes to this subtotal.

---

## 7. Notes on specific paths

### 7.1 Items with designated owners — listed, not planned

Per the brief, these have owners and **no move is proposed for any of them**:

| Path | Note |
|---|---|
| `Certonomous/LAPTOP_SHOOT.md` | The owner's own file. Untouched. |
| `Certonomous/dist/` | Designated owner. Untouched. |
| `Certonomous/demo-output/website/latex/` | Designated owner. Untouched. |
| `Certonomous/demo-output/website/motorbike-video/` | Designated owner. Untouched. |

All four are inside the `Certonomous` repo and therefore outside this plan's
scope twice over. **A second copy of each exists** under
`.mutarc-64b13819/` (`LAPTOP_SHOOT.md`, `dist/`, `demo-output/website/latex/`,
`demo-output/website/motorbike-video/`) — this is part of why ASK-1 matters and
why no one should delete that tree on the assumption it is scratch.

### 7.2 `certonomous-runs/` — measurement traps that survive into execution

Anyone executing against this tree must carry LOCATIONS.md §4.1's warnings:

- `find` on this box is `bfs` and rejects GNU expressions such as `-printf`.
  Use `/usr/bin/find`.
- `-size -2M` and `-size +2M` are **not** complementary: 121,523 + 6,108 =
  127,631, leaving 4,418 files in neither band, because `±NM` rounds up to whole
  MiB. Any banded sweep must reconcile against an independent total.
- State which population a count is over: 132,049 regular files / 132,797
  including symlinks / 132,761 excluding the 36 root files.

### 7.3 The shell `grep` cannot see this tree

Confirmed by inspection: `grep` in this shell is a **function** wrapping
`ugrep -G --ignore-files --hidden -I --exclude-dir=.git …`. It honours
`.gitignore` silently and passes `-I`. **Any sweep of this tree must use
`/usr/bin/grep`** or it will miss the gitignored arm and every binary-marked
file. This plan used `/usr/bin/grep` throughout; the one search run with the
wrapper returned zero hits for `closure-venv` and was wrong, which is how the
trap was caught.

### 7.4 Long sweep results, including one correction to this page

Several `/usr/bin/grep -rl` sweeps were launched; the slow ones ran 20+ minutes
against the 69 GB run tree. Status is reported per sweep, because a plan that
quotes an unfinished walk is a failure mode this lab already knows about.

**A count on this page was wrong twice, for two different reasons. Both are
recorded rather than quietly fixed, because the second one is a trap worth
naming.**

The question was: how many files in `Certonomous/` carry the leaderboard entrant
text ("Reissmann, Fang, and Sandberg")?

| Reading | Answer given | Why it was wrong |
|---|---|---|
| First | 7 | Read off a `tail -8` of the sweep's output file **while the sweep was still writing it**. A partial file mistaken for a finished one. |
| Second | 10 | The sweep itself ended in `\| head -10`. It returned exactly its own truncation limit. **A bounded read reported as a census.** |
| Third, correct | **19** | `grep -rl … \| sort \| wc -l`, no `head`, run to completion. |

The second failure is the instructive one: `head -10` returning ten results does
not mean there are ten, and the pipeline gives no signal that it truncated —
exactly the family of defect LOCATIONS.md §4.1 warns about with `find … | wc -l`
discarding stderr, and with `-size ±2M` losing 4,418 files between two bands
that look complementary. **A count whose value equals its own limit should never
be trusted.** Any sweep in this lab that ends in `head -N` and returns `N` must
be re-run without the `head` before its number is quoted.

**One of the 19 is this file.** `AWS_TREE_PLAN.md` quotes the entrant string in
this very section, so the sweep matched it. The count of **pre-existing** repo
files is therefore **18**. Stating 19 without that caveat would be a measurement
contaminated by its own instrument.

The 18, in full:

```
demo-output/website/ACTIVE_RESEARCH.md
demo-output/website/CLOSURE_CHALLENGE_STATUS.md
demo-output/website/closure.html
demo-output/website/closure_challenge_C2_error_decomposition.md
demo-output/website/closure_challenge_decline_gate_audit.json
demo-output/website/closure_eval/closure_eval_master_table.md
demo-output/website/closure_eval/closure_eval_master_table.json
demo-output/website/campaign/BOARD_MOVED_2026-08-11.md
demo-output/website/campaign/BOARD_RESCORE_2026-08-14.md
demo-output/website/campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md
demo-output/website/campaign/reports/MORNING_REPORT_2026-08-04.md
demo-output/website/campaign/reports/MORNING_REPORT_2026-08-07.md
dist/certonomous-demo/site/closure.html
docs/papers/mcconkey_et_al_closure_challenge_2603.28884.txt
scripts/self_audit.py
scripts/use_mention_control_set.json
sdk/scripts/closure_decline_gate_audit.py
sdk/tests/test_rank_claim_surfaces.py
```

**And the widened result changes the picture materially.** The first two readings
suggested the board appeared only in prose reports. It does not. It is embedded
in **executable audit and test code** — `scripts/self_audit.py`,
`sdk/tests/test_rank_claim_surfaces.py`, `sdk/scripts/closure_decline_gate_audit.py`
— and in the machine-readable `use_mention_control_set.json` and
`closure_challenge_decline_gate_audit.json`. So the leaderboard is not merely
cited in the lab's writing; **a test suite asserts against it.** That raises the
stakes on `scratch_live_readme.md` rather than lowering them, and it is a
coupling nobody would have found from the truncated counts.

The conclusion stands and is strengthened: the board content is **not** unique to
`scratch_live_readme.md`, but that loose file remains the **only copy of the
retrieval itself**, and it is now known to sit upstream of test assertions. Its
EVIDENCE classification stands.

**A third wrong reading, on the same page, from the same cause.** An earlier
draft of this section asserted as an "established negative" that no repo file
cites the string `scratch_live_readme`, and used that to declare the §6.1 rename
safe. **That assertion was made from an output file that was still being
written** — the header line had appeared, the result line had not, and empty was
read as zero. The sweep's real answer, once it finished, was **7 lines**.

On inspection all 7 lines are inside **this file, `AWS_TREE_PLAN.md`** — the
sweep matched the plan's own prose about the rename. So the substantive
conclusion survives, but it was asserted before it was known, and the number
that would have contradicted it was sitting unread in a file this page had
already quoted from twice.

**Three readings on this page have now been wrong for two causes, and both
causes are "a bounded or partial read reported as a complete one":**

| # | Claim | Cause |
|---|---|---|
| 1 | "7 repo files carry the board text" | read a sweep's output while it was still being written |
| 2 | "10 repo files carry the board text" | the sweep ended in `\| head -10` and returned its own limit |
| 3 | "0 files cite `scratch_live_readme`" | read a sweep's output while it was still being written |

**And twice the instrument contaminated its own measurement:** this file matched
both the board-text sweep (1 of 19) and the filename sweep (7 of 7). Any sweep
run from inside a tree it is also describing must exclude itself, or say which
of its hits are its own reflection.

**The rename question, now actually settled.** A sweep excluding this file was
run to completion with an explicit end-of-run sentinel, so "finished" could be
distinguished from "still writing" — the precise failure that produced readings
1 and 3:

```bash
/usr/bin/grep -rn -I --binary-files=without-match --exclude=AWS_TREE_PLAN.md \
  "scratch_live_readme" /home/ubuntu/Certonomous /home/ubuntu/Certonomous_closure_challenge
# EXIT=1  (grep's "no matches"; 2 would be an error)
# LINES=0
# SWEEP-COMPLETE
```

**Zero citations.** No file in either repository references
`scratch_live_readme` by name. The rename proposed in §6.1 breaks nothing. The
earlier claim was right in substance and wrong in method; this one is checked.

Record the old name in the destination README regardless, because LOCATIONS.md
§4.2 cites the *retrieval time* and a reader will arrive looking for it.

**The method that finally worked, for reuse:** exclude the measuring file from
its own sweep, drop every `head`/`tail`, emit a sentinel line after the result,
and wait for the sentinel rather than for silence. Silence is indistinguishable
from an unfinished sweep, and that is what went wrong twice.

**Established negative — the run tree does not reference the venv.** The sweep
for `closure-venv` across all 132,049 run-tree files completed with **zero
hits**. This usefully bounds the blast radius of §4.2: the venv's couplings are
to repo scripts and one published JSON record, **not** to the run tree. The
constraint in §4.2 stands undiminished, but a run-tree replay is not among the
things that break.

**Did not finish.** The sweep for custom-solver library names
(`libspartaTurbulenceModels`, `kCorrectiveFrozenFoam`, `rhoCentralFoamBounded`,
`libkOmegaSSTQCR`) across the run tree was still running, I/O-bound in state
`D`, when this page was completed. **Nothing here depends on it.** §4.1's
coupling was established by targeted checks that did complete —
`w3-qcr-duct/AR_10_Ret_180_qcr/{system/controlDict,constant/turbulenceProperties,log.simpleFoam}`
plus the F4 `swbli_cylflare` `controlDict`s and `Make/files`.

**Do not quote as established:** any *count* of run-tree files referencing the
custom solvers. That number is unmeasured. The existence of the coupling is
established; its extent is not.

### 7.5 `closure-venv` version strings — resolved, and it was never a code skew

**This section previously read "`closure-venv` version skew" and left a
scientific question open: whether B2's published numbers were produced under
0.2.1 and are still consistent with a 0.3.1 environment. That question was
answered on 2026-08-17. The answer is *no, there is no skew* — the two version
strings are two reporting mechanisms describing one commit. The old framing is
recorded here rather than quietly deleted, because the reason it looked like a
hazard is itself the thing worth keeping.**

**There is only one scorer on this box, and it is `1c4e22c8`.** The venv's
`closure_challenge` is an *editable* install pointing at
`/home/ubuntu/closure-challenge-pkg/src` (§4.2), and that clone is pinned at
`1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`. There is no second checkout and
there never was a 0.2.1 install. Both strings come out of that one tree:

```sh
/home/ubuntu/closure-venv/bin/python -c \
  "import closure_challenge, importlib.metadata as m; \
   print(closure_challenge.__version__, m.version('closure-challenge'))"
# -> 0.2.1 0.3.1
```

`0.2.1` is `src/closure_challenge/__init__.py`'s `__version__`; `0.3.1` is the
`dist-info` metadata, built from `pyproject.toml`. Upstream bumped
`pyproject.toml` and never `__init__.py` — confirmed against the full upstream
history, where `__init__.py` is **byte-identical** from tag `v0.2.1` (`4796ce35`)
through the pin:

```sh
git -C /home/ubuntu/mirrors/closure-challenge.git diff 4796ce35 1c4e22c8 \
  -- src/closure_challenge/__init__.py    # empty
```

So the version strings differ **by reporting mechanism, not by code**. A tool
that reads `__version__` and a tool that reads package metadata will disagree
forever about this commit, and neither is reporting a different scorer.

**The metric change is real, and it is what makes the record checkable.**
`evaluate_individual_case` genuinely differs between `v0.2.1` and the pin —
componentwise `np.mean(np.abs(...))` became vector-magnitude
`np.mean(np.linalg.norm(..., axis=-1))` — so the two produce *different numbers
from identical inputs* and are distinguishable by inspection of any record
scored under them.

**What settles it is the record's own internal self-consistency, not its prose.**
All 14 scoring figures in `B2_duct_baseline.json` were re-derived from the same
fields, through the same unmodified scorer, under *both* candidate metrics, by
a read-only instrument added beside the original generator:

```sh
/home/ubuntu/closure-venv/bin/python \
  demo-output/website/dafoam/ladder-b/duct_baseline/recheck_scorer_revision.py
# -> AT PIN 1c4e22c8 (v0.3.1 metric): 14/14 reproduce exactly
#    AT TAG v0.2.1  (4796ce35 metric):  6/14 reproduce exactly
```

It writes nothing, and in particular does not overwrite
`score_our_baseline_result.json`, which `score_our_baseline.py` produced in
2026-07 and which is left as it stands. Under the metric at `1c4e22c8`, all 14
reproduce. Under the `v0.2.1` metric, restored from the mirror, the 8
metric-dependent figures all move and none reproduce:

| Figure | Published (= at `1c4e22c8`) | Under `v0.2.1` code |
|---|---|---|
| `AR_1` our score | 0.129 | 0.1414 |
| `AR_1` reproduced benchmark baseline | 0.1288 | 0.1412 |
| `AR_3` our score | 0.1251 | 0.1371 |
| `AR_3` reproduced benchmark baseline | 0.1243 | 0.1363 |

The remaining 6 figures are metric-independent — the two floor constants copied
from `closure_challenge_rans_floor.json`, and the two field-vs-field scaled MAEs
with their percentages, which are computed in numpy and never pass through the
scorer — so they match either way and carry no information about which metric
ran. **The record is self-consistent under `1c4e22c8` and under no other
revision.** `0.2.1` in its prose was a stale string, not a different scorer.

**Two caveats on that "all 14", stated because the arithmetic is not uniform.**
Two of the figures are rounded restatements of the figures beside them, not
independent quantities: `deviation_..._relative_pct` divides the *already
rounded* absolute deviation by the floor (`0.0008 / 0.1243 = 0.64%`, where the
unrounded deviation would give 0.62%), and `internal_field_scaled_mae_pct` is
`100 x` the scaled MAE shown at each case's own precision (0.023 for `AR_1`,
0.09 for `AR_3`). Both are reproducible on the record's own basis; neither is a
second measurement.

**What survives as a warning, and it is the useful half of the old section.**
Never cite this scorer by version string. `0.2.1` and `0.3.1` both name
`1c4e22c8`, and a `pip install closure-challenge` by name can resolve to a
genuinely different metric and return a different number for identical CSVs.
The lab's own written standard already says exactly this —
`Certonomous_closure_challenge/evidence/REPRODUCE.md:70`, *"Pin the scorer by
commit hash, not version string."* As of 2026-08-17 all seven published JSON
records that name an eval-package version also pin `1c4e22c8`;
`B2_duct_baseline.json` was the last one that did not — the other six already
did — and its `scoring_environment` prose was amended
to pin it (figures untouched; the amendment is recorded in the record itself
under `data_provenance.amendment_2026_08_17`).

**The real fragility this surfaced is the clone, not the version.**
`/home/ubuntu/closure-challenge-pkg` is a **depth-1 shallow clone** — its
`.git/shallow` contains exactly `1c4e22c8`, so it holds that one commit and
cannot show what changed to produce it. The counterfactual above was only
runnable because the `v0.2.1` history was fetched from GitHub. If that upstream
repository moved, were renamed or were deleted, this check would have become
unrebuildable and every record pinning `1c4e22c8` would have lost its referent.
A full mirror now exists at **`/home/ubuntu/mirrors/closure-challenge.git`** and
has been restored from with the network removed; see LOCATIONS.md §4.2b.

### 7.6 Live services

`python3 -u -m http.server 8080 --directory demo-output/website` (PID 1453,
started 14:49 UTC) is serving the demo website right now, and a control room is
listening on `:8765` (synthetic, per `control_room.log`). Execution of this plan
should either avoid the three log files entirely or stop the servers first.

---

## 8. ASK — the explicit list

Everything I cannot resolve without the owner. Each says what I would need to
know.

**ASK-1 — `.mutarc-64b13819/`: a 7.04 GB undocumented git tree. What is it?**
20,853 files, `du -sb` 7,036,239,167. It is a git working tree at HEAD
`36c5e2ea104f66b7c75cbf00735992ce1ff72ff9`, which is **not a revision present in
`/home/ubuntu/Certonomous`** (verified: `git log 36c5e2ea` there fails with
"unknown revision"). It carries a `.archive_sha` file containing
`e1ede44a12ed34147824bbbbc42bfb200567476e`, and its layout mirrors the
Certonomous repo — `sdk/`, `demo-output/`, `docs/`, `dist/`, `models/`,
`scripts/`, plus `LAPTOP_SHOOT.md`, `LESSONS.md`, `FILMING_COMMANDS.md`, two
vendored `.whl` files and a set of `mbc_retry*.log` files. Its name suffix
`64b13819` matches the current agent session ID, suggesting harness-managed
state, but its content is a **divergent snapshot of the lab's own repository**,
not a cache.
*I need to know:* is this harness scratch that the tooling will clean up, or a
snapshot holding work that never landed on `main`? Until answered it is
**untouchable** — it is 7 GB and LOCATIONS.md does not mention it, so no one
should assume it is disposable. If it holds unlanded commits, that is a finding
well beyond tidying.

**ASK-2 — May the four compiled OpenFOAM solver binaries be rebuilt rather than
kept?** They are §6.3 REGENERABLE by `wmake`, but they are the exact binaries
behind published `swbli_cylflare` and `w3-qcr-*` results, and **no build
procedure is documented anywhere in the repo**. *I need to know:* is a
bit-identical binary required for any published claim, or is "rebuildable from
tracked source" sufficient? My recommendation regardless: **keep them, and write
the build procedure down first.** 6.48 MB is not worth the risk.

**ASK-3 — `closure-challenge-benchmark/scripts/rans_identity_baseline.py`: a
lab-authored file living inside an upstream clone.** 2,827 bytes, MD5
`e5faef412884f3552222752e5a277c74`, the **only** untracked file in that clone,
and a whole-home search found **no other copy anywhere**. It is therefore
unique, lab-authored, and currently stored in the one directory a reader would
assume is pure upstream and safe to re-clone. *I need to know:* is this a
throwaway experiment or real work? If real, it should be moved into the
Certonomous repo and committed — **a `git clean` or a re-clone of that
benchmark destroys it, and it exists nowhere else.** This is the single most
fragile file found in the whole sweep.

**ASK-4 — the version-ladder scripts: keep every rung, or only the tip?**
Thirteen loose scripts, all byte-distinct, in two families:
`render_naca_{case,batch,batch_v2,json,json_v2,annotated}.py` and
`test_paraview_{simple,batch,headless,headless_v2..v5}.py`. The `_v2`…`_v5`
naming says the later ones supersede the earlier. They are not duplicates — no
two share an MD5 — so they cannot be resolved by hash. *I need to know:* is the
progression itself a record worth keeping (in which case all 13 move to
`lab-scripts/paraview-render/` with a README explaining the ladder), or should
only the working tip survive? Total at stake: 38,691 bytes, so there is no
space argument either way — this is purely about what a newcomer should see.

**ASK-5 — `certonomous-git-backup-20260730T033814Z.tar.gz` (544,309,252 B).**
Its contents begin `.git/` — it is a bare-ish backup of the repository's git
directory taken 2026-07-30. The repository is now on GitHub
(`git@github.com:Certonomous/Certonomous.git`), so in principle this is
redundant. **But** `MIGRATION_STATUS.md` records that this box holds **no git
credentials** and was synced by bundle over ssh, and this snapshot predates
current `main` (`101079fd…`). *I need to know:* does this tarball contain any
branch, stash or reflog entry that never reached GitHub? If not, it is 0.544 GB
of recoverable space. **I would not delete it without someone checking its refs
against the remote first** — that check is cheap and I can run it on request.

**ASK-6 — `certonomous-cache.tar.gz` (362,066,284 B).** Contents begin
`.mesh-cache/cone-M2.35-th10-fine/polyMesh/…` — an archived OpenFOAM mesh cache.
Meshes are regenerable by re-running `blockMesh`/`snappyHexMesh`, but
regenerating them costs compute and the cache may be what made specific runs
reproducible quickly. *I need to know:* is `.mesh-cache` still used by any active
workflow, and does an unpacked copy already exist inside the repo? If the answer
is no and no, this is 0.362 GB of recoverable space.

**ASK-7 — `.bashrc.bak` (5,880 B) and `.bashrc.bak2` (4,080 B).** Two manual
backups of `.bashrc` (4,152 B). All three are byte-distinct, so they are not
duplicates; `.bak` is notably *larger* than the live file, meaning something was
removed. *I need to know:* was anything deliberately dropped from `.bashrc` that
should be recoverable? If not, these are the definition of "random files lying
around". Trivial in size; listed because the brief asks for a complete
classification and dotfile backups are exactly the clutter a newcomer trips on.

**ASK-8 — should `LOCATIONS.md` be extended to cover the dotted directories?**
Not a file-disposition question, but it belongs on this list. §2.1 shows
LOCATIONS.md accounts for 2.06 GB outside the repos and run tree while the true
figure including dotted directories is 15.93 GB, and the 13.87 GB gap contains
the 1,557 agent dispatch records that LOCATIONS.md §4.5 itself calls the only
sound R-ISOLATE evidence. *I need to know:* whether extending LOCATIONS.md is in
scope for the reorganisation, or a separate task. **A newcomer reading
LOCATIONS.md today would not know the independence evidence has a size or a
location on disk.**

---

## 9. Recommended execution order, when authorised

Ordered so that the reversible and the checked come first, and nothing
irreversible happens before an ASK is answered.

1. **Answer ASK-1 and ASK-3 first.** Both concern data that exists in exactly one
   place and could be destroyed by ordinary tooling (`git clean`, harness
   cleanup) before anyone touches this plan.
2. **Create the target directories and write every README**, including the
   "do not delete" statements. Zero risk; immediately improves legibility.
3. **Move the EVIDENCE loose files** into `evidence/` — additive, reversible,
   nothing references them by path. Rename `scratch_live_readme.md` here.
4. **Move `memory-import/` → `notes/` and the lab scripts → `lab-scripts/`**
   (subject to ASK-4).
5. **Place `upstream/`** — move the three pinned clones, then immediately
   restore `~/closure-challenge-pkg` as a symlink (§4.2) and verify with
   `/home/ubuntu/closure-venv/bin/python -c "import closure_challenge"`.
6. **Leave `certonomous-runs/`, `OpenFOAM/` and `closure-venv/` physically where
   they are.** Represent them in the target tree by symlinks *into* the tidy
   names, never the reverse.
7. **Stop the servers, move the three live logs, restart, update the launcher.**
8. **Delete only after all of the above verifies:** the two proven duplicates
   (`lab.sh`, `provision.sh` — 3,446 B) and `__pycache__/` (1,819 B). Nothing
   else, and nothing at all from an unanswered ASK.

---

## 10. Reproducing this frame

```bash
# per-directory file counts, stderr captured (this is the step that must not be skipped)
for d in OpenFOAM backups certonomous-runs closure-challenge-benchmark \
         closure-challenge-pkg closure-venv dafoam-tutorials memory-import __pycache__; do
  /usr/bin/find /home/ubuntu/$d -type f 2>>walk_err_$d.txt | wc -l
done

# deduplicated bytes
du -sb /home/ubuntu/certonomous-runs

# apparent vs deduplicated, keyed on (st_dev, st_ino), with os.walk(onerror=...)
# and the duplicate sweep by full-file MD5: see §6.4

# loose files
ls -la /home/ubuntu

# NEVER use the shell `grep` for a coverage claim — it is ugrep --ignore-files (§7.3)
/usr/bin/grep -rn -I --binary-files=without-match PATTERN /home/ubuntu/...
```

**Limits of this page.** Every figure is a reading taken 2026-08-17 15:00–16:00
UTC, not a constant. Three loose log files were growing during the frame and
their sizes are floors. One full-tree grep — the custom-solver name sweep over
the run tree — did not finish (§7.4), and nothing here depends on it.

**One figure on this page was wrong twice before it was right** (§7.4): once
from reading a sweep's output file while it was still being written, and once
from a sweep that ended in `| head -10` and returned exactly 10. Assume other
figures could be wrong the same way. Before quoting any count from this page,
re-derive it with no `head`, no `tail`, and stderr captured — and check whether
this file is itself among the matches. No third party has re-derived any figure
on this page.
