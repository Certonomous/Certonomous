# TEAM BRIEF REFERENCE AUDIT — every checkable assertion in `harness/teams.yaml`, graded against HEAD

**THIS AUDIT CHANGED NOTHING IN `harness/` OR `.claude/`. Not one byte was
written, edited, `sed -i`-ed or staged under either directory. Every proposed
edit in §9 is a PROPOSAL FOR SANAA'S DESK and nothing else** (CLAUDE.md rule 9:
nothing may change `.claude/` config, `CLAUDE.md` or permission settings on an
agent's say-so). The auditing lane read `harness/teams.yaml` and the ten
generated `.claude/agents/*.md` files read-only.

| field | value |
|---|---|
| **HEAD audited** | `cc2a2e039aa457213d4c24adbe46b1d40e906916` |
| **`date -u` in the writing invocation** | `Fri Sep 11 15:25:37 UTC 2026` |
| **Audited artifact** | `/home/ubuntu/Certonomous/harness/teams.yaml`, 510 lines, file version 1.2 dated 2026-08-24 |
| **Generated artifacts cross-referenced** | the ten files under `/home/ubuntu/Certonomous/.claude/agents/` |
| **Team** | verification (cross-team gate-audit mandate; `docs/*_AUDIT.md` is this team's territory) |
| **Compute** | zero core-minutes. No solver ran. Read-only audit; no ledger row owed. |

---

## 1. The occasion

The heat-transfer team found that `harness/teams.yaml:244` — and the generated
`.claude/agents/heat-transfer-supervisor.md:175` — still carries **D389** as
"open and unowned", while `docs/DOCKET.md` records **D393** settling it on
2026-08-18. A supervisor brief is loaded into every session of that team, so a
stale hazard line is not inert prose: it is a standing instruction that nearly
reintroduced an already-repaired defect.

The chief asked verification whether that was one bad line or a class. **It is a
class.** Sixteen assertions in the roster are stale, and two of them are worse
than D389 because they point a lane at a file or a directory that is not what the
brief says it is.

---

## 2. Method, and what it deliberately does not claim

1. **Every reference read from the HEAD blob, not the worktree.** `docs/DOCKET.md`
   diverges from HEAD by design under the private-index protocol (CLAUDE.md rule
   11). `scripts/check_docket_reconciliation.py` was run first and returned
   **`VERDICT: PASS`** — 676 rows committed, 676 in the working copy, **the same
   set of row IDs on both sides**, under a RECOGNITION control that found 5 of 5
   planted docket-row forms and correctly rejected 1 negative. Its own
   `CANNOT SEE` line is carried here unchanged: it cannot see **whether a row's
   CONTENT diverged** (same id, different body reads as reconciled). Every docket
   citation in this audit is therefore taken from
   **`git show cc2a2e039:docs/DOCKET.md`**, and the line numbers below are line
   numbers **in that blob** (1,006 lines), not in the worktree file.
2. **Path existence measured twice and labelled.** Each asserted path was tested
   both for tracking at HEAD (`git cat-file -e cc2a2e039:<path>`) and for presence
   on disk (`test -e`). Which of the two supports a verdict is stated in its row.
   `git status` was never relied on — it reads stale under concurrency, and there
   are ~6,348 dirty paths lab-wide.
3. **Charter versions read from the amendment FOOT, not the header.** CLAUDE.md
   rule 6 forbids editing a frozen file: a charter's header keeps its original
   version forever and the current version lives in the last dated amendment at
   the foot. Reading the header alone is exactly the error that makes a version
   claim look fresh when it is 86 amendments behind. Both were read for every
   charter and both are quoted.
4. **`grep` here is ugrep.** `grep -r` skips gitignored files and multi-file
   output races. Every search in this audit names a single artifact.
5. **One zero was planted before it was believed.** A first pass reported "the
   `N-D` numerics family does not exist — zero `^## N-D[0-9]` headings in
   `docs/NUMERICS_KNOWLEDGE.md`". The pattern was then fired at a copy of the same
   file with `## N-D9. planted` appended and returned **1**, proving the reader
   could see a non-zero. The zero was real *for that pattern* — and the pattern was
   wrong: `N-D` entries are written `**N-D1. …**`, not as `##` headings. A wider
   read finds **652 `N-D` mentions from `docs/NUMERICS_KNOWLEDGE.md:2271`,
   families N-D1 through N-D15+**. The claim is TRUE and was nearly graded false.
   The same trap fired a second time on `analyse_t3.py` (§5, row H-16). **Both
   near-misses are recorded rather than quietly corrected**, because a planted
   control that changes a verdict is the most useful thing in this document.

**What this audit cannot see, stated plainly:** whether a docket row's *body*
changed between the worktree and HEAD; whether any team has an unlanded commit
that would settle a row graded STALE here; and the truth of any claim requiring a
measurement the lane did not take (each such row is graded UNVERIFIABLE with the
specific unreached measurement named, never "probably").

---

## 3. Headline count

| | |
|---|---|
| **Assertions audited** | **171** |
| **STILL TRUE** | **148** |
| **STALE / SETTLED** | **16** |
| **UNVERIFIABLE** | **7** |

Of the 16 stale rows: **5** are settled by a named docket row; **9** are
superseded by repository state with no docket entry; **2** are section- or
file-identity errors that appear never to have been true at the version cited.

Reference census, verified by `grep -oE '\b(D[0-9]+|D-[0-9A-Za-z]+|L-[0-9]+|N-[A-Za-z0-9-]+)\b' harness/teams.yaml`
and extended beyond the brief's candidate list. **The complete set is fourteen
tokens**: `D389`, `D446`, `D-6`, `D-A`, `D-A2`, `D-B`, `D-B2`, `D-C`, `D-E`,
`L-144`, `L-219`, `L-220`, `L-223`, `N-D`. The brief's seven-token candidate list
was short by the seven `D-<letter>` upstream-defect class ids and `D-6`; all
seven are audited below. No `N-*` token other than `N-D` appears in the file.

---

## 4. `common:` and `defaults:` — the blocks every agent inherits

Rendered identically into all ten generated files; generated line numbers are
given for `closure-supervisor.md` and are the same block in each.

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| C-1 (64–79) | all agents :38 (:37 in cfd/verification/ansys) | The rule-16 silent-background convention, quoted verbatim | **STILL TRUE** | Matches `CLAUDE.md` rule 16 (lines 188–208) word for word, including the "Honest caveat" |
| C-2 (81) | :63 | `CLAUDE.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-3 (83) | :65 | `docs/LAB_STATE.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-4 (85) | :67 | `docs/charters/SUPERVISION_CHARTER.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-5 (87) | :69 | `docs/charters/ESCALATION_CHARTER.md` exists; git rules in §9.6 | **STILL TRUE** | tracked at HEAD + on disk |
| C-6 (89) | :71 | `docs/charters/COMPUTE_BUDGET_CHARTER.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-7 (91) | :73 | `docs/charters/REPORTING_CHARTER.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-8 (93) | :75 | `docs/charters/FILING_CHARTER.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-9 (95) | :77 | `docs/charters/VERIFICATION_CHARTER.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| C-10 (98) | :81 | `tail -60 docs/DOCKET.md` — target exists | **STILL TRUE** | tracked at HEAD + on disk, 1,006 lines at HEAD |
| C-11 (100) | :83 | the max-lesson-number command works on `docs/LESSONS.md` | **STILL TRUE** | run against the HEAD blob: returns **542** |
| C-12 (102) | :85 | `tail -60 docs/NUMERICS_KNOWLEDGE.md` — target exists | **STILL TRUE** | tracked at HEAD + on disk |
| D-1 (45) | frontmatter `model: opus` in all six supervisor files | `supervisor_model: opus` because "Fable capacity is currently exhausted" — a TEMPORARY departure from `SUPERVISION_CHARTER.md` §5 | **UNVERIFIABLE** | Whether Fable capacity has returned is not measurable from this box. **Recorded as a standing divergence, not a defect:** `CLAUDE.md:235–237` still asserts "Supervisors run on **Fable**", and the six generated files all declare `model: opus`. The YAML's own comment block (28–43) discloses this and names the revert condition; the divergence is documented, not silent. |
| D-2 (56) | closure/dafoam/heat-transfer/cfd/verification agent files, "At most 3 lanes" | `max_live_lanes: 3` = `SUPERVISION_CHARTER v1.4` §8's cap | **STILL TRUE** | §8 at `docs/charters/SUPERVISION_CHARTER.md:407`; the cap text at :458 — "*A lane cap: at most three lanes live per supervisor*" |
| D-3 (57) | all five non-ansys agent files | `worker_agent: lab-lane`; the generator round-trips | **STILL TRUE** | `python3 harness/generate_agents.py --check` → `OK: 10 agent file(s) round-trip from teams.yaml`, rc=0. **The YAML and the generated files are in sync — every stale line below has propagated.** |

---

## 5. Team `closure` (yaml 107–152) → `.claude/agents/closure-supervisor.md`

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| CL-1 (113) | :90 | `cases/RANS_LES_closure_models` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CL-2 (114) | :91 | `docs/closure` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CL-3 (115) | :92 | `docs/papers/closure` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CL-4 (116) | :42, :51 | `docs/charters/CLOSURE_MODELLING_CHARTER.md` owned | **STILL TRUE** | tracked at HEAD + on disk |
| CL-5 (126) | mandate | `L-219` exists | **STILL TRUE** | `docs/LESSONS.md:9314` (HEAD blob) — "A perturbation magnitude calibrated where the model is qualitatively right saturates where it is structurally wrong" |
| CL-6 (126) | mandate | `L-220` exists | **STILL TRUE** | `docs/LESSONS.md:9340` (HEAD blob) — "Test the envelope on the quantity that enters the equations" |
| CL-7 (126) | mandate | `D446` exists and carries the bands-vs-corrections finding | **STILL TRUE** | `docs/DOCKET.md:811` (HEAD blob) — D446, "L-157'S OPEN LOOP CLOSES WITH AN INVERSION"; the 1,344x envelope-to-signal figure is in the row |
| CL-8 (124) | mandate | "FS2 and FS5 are STANDING GATES" | **STILL TRUE** | `CLOSURE_MODELLING_CHARTER.md:815` — "## 22.5 FS2 degeneracy audit and FS5 extrapolation-coverage check are standing gates"; also `CLOSURE_LINE_RESTART_DOCTRINE.md:271` |
| CL-9 (131) | :52 | charter is **"v1.1.2 (2026-08-22)"** | **STILL TRUE** | Header at `:3` reads *"Version 1.1.2, dated 2026-08-22"*; the file carries **no** `## Amendment — v…` foot and no `\| amendment record \|` row, so the header IS the current version. 1,020 lines at HEAD. |
| CL-10 (131) | :52 | "§22 is the R-ladder's binding half" | **STILL TRUE** | §22 block present; §22.4 at :778, §22.5 at :815 |
| CL-11 (131) | :52 | "§22.4 carries the bands-vs-corrections caveat" | **STILL TRUE** | `:778` — "## 22.4 Every prediction ships the model-form band" |
| CL-12 (131) | :52 | "§19 parks submissions" | **STILL TRUE** | `:620` — "## 19. Submissions are parked; nothing leaves the machine" |
| CL-13 (131) | :52 | "§18 sets the 487 core-hour authorisation" | **STILL TRUE** | `:592` — "## 18. Compute: 487 core-hours pre-authorised"; the figure re-stated at `:594`, `:602` |
| CL-14 (132) | :53 | `docs/closure/README.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| CL-15 (133) | :54 | README "disagrees with Ling2016's RESULTS.md and the disagreement is known" | **UNVERIFIABLE** | Both files exist (`cases/RANS_LES_closure_models/Ling2016_TBNN/RESULTS.md`, tracked + on disk). **The disagreement itself was not re-measured** — that is a substantive re-read of two records and was outside this audit's scope. Not graded TRUE on the strength of the paths alone. |
| CL-16 (134) | :55 | `CLOSURE_LINE_RESTART_DOCTRINE.md` exists; "Parts 3 and 4 define R1-R6 and FS1-FS6" | **STILL TRUE** | tracked + on disk; FS2 section heading confirmed at `:271` |
| CL-17 (136) | :57 | `docs/closure/R2_SHORTLIST_MEMO.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| CL-18 (138) | :59 | `docs/papers/closure/MANIFEST.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| CL-19 (139) | :60 | `L-144` (title-page verification) exists | **STILL TRUE** | `docs/LESSONS.md:7046` (HEAD blob) |
| CL-20 (141–143) | :90–:92 | folder_scope ×3 | **STILL TRUE** | all three tracked at HEAD + on disk |
| CL-21 (145) | :95 | `/home/ubuntu/closure-data/` exists | **STILL TRUE** | **on disk** (external data is not tracked): 14 GB |
| CL-22 (146) | :96 | `/home/ubuntu/closure-challenge-benchmark/` exists | **STILL TRUE** | **on disk**: 1.3 GB |
| **CL-23 (151)** | **:172** | **"Several paths are staged-as-deleted while existing untracked on disk (`NASA_hump_gate/`, `_common/uq_eigenspace/`). A blind git checkout or reset would destroy R4 and the hump gate."** | **STALE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | **Measured:** `git diff-index --cached --name-status cc2a2e039 -- <both paths>` returns **empty** — the index matches HEAD for both. `git ls-tree -r cc2a2e039` lists **4 files under `NASA_hump_gate/`** and **4 under `_common/uq_eigenspace/`**; `find` on disk returns **the same 8 files**. Both paths are **tracked at HEAD and present on disk**; neither is staged-as-deleted and neither is untracked. The docket names `NASA_hump_gate` only once at `:810` (D445, a scoring finding), and nothing in the docket records the re-landing. |
| CL-24 (152) | :173 | `_common/commit_private.sh` exists; prefer the rule-10 single-invocation form (`L-223`) | **STILL TRUE** | `cases/RANS_LES_closure_models/_common/commit_private.sh` tracked at HEAD + on disk; `L-223` at `docs/LESSONS.md:9437` — the stale-`read-tree` hazard |

---

## 6. Team `dafoam` (yaml 154–196) → `.claude/agents/dafoam-supervisor.md`

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| DA-1 (160) | :90 | `cases/dafoam` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| DA-2 (161) | :91 | `docs/dafoam` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| DA-3 (162) | :92 | `docs/papers/adjoint_and_optimization` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| DA-4 (163) | :42, :51 | `docs/charters/DAFOAM_CHARTER.md` owned | **STILL TRUE** | tracked at HEAD + on disk |
| **DA-5 (176)** | **:52** | **charter is "v1.0b (2026-08-21)"** | **STALE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | Header at `docs/charters/DAFOAM_CHARTER.md:3` (HEAD blob) reads **"Version 1.0g, dated 2026-09-05"**. Seven letter-revisions and 15 days ahead of the brief. The file carries no `## Amendment — v…` foot, so the header is authoritative and the header itself has moved. |
| DA-6 (176) | :52 | "§10 is the NOT FILED clause" | **STILL TRUE** | `:376` — "## 10. Upstream filing is Sanaa's alone, and every defect record says so on its first screen" |
| **DA-7 (176)** | **:52** | **"§11 the toolchain identity rule"** | **STALE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | **§11 is not that clause and is not close to it.** `:412` reads "## 11. Lessons continue from L-186, and numerics facts are inserted at the end of the N-B block". The toolchain-identity rule is **§6**: `:201` — "## 6. Shipped and patched are always two rows, **and toolchain identity is an image ID and a library hash**, never a version string". A lane sent to §11 for the identity rule reads a filing convention instead. |
| DA-8 (176) | :52 | "the N-D numerics family is yours" | **STILL TRUE** | **This is the row the planted control saved** (§2.5). `docs/NUMERICS_KNOWLEDGE.md:2271` (HEAD blob) — "**N-D = DAFoam-team numerics facts, opened 2026-08-21**"; entries N-D1 (`:2275`) through N-D15 (`:3250`) and beyond, **652 `N-D` occurrences**. |
| DA-9 (177) | :53 | `docs/dafoam/README.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| DA-10 (178) | :54 | "§3 is the standing two-row (shipped/patched) verdict table" | **STILL TRUE** | `docs/dafoam/README.md:74` — "## 3. Standing verdict table — shipped and patched are always two rows" |
| DA-11 (179) | :55 | `docs/dafoam/TOOLCHAIN_INVENTORY.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| DA-12 (180) | :56 | "the hash is the identity; the version string is not" | **STILL TRUE** | corroborated by `DAFOAM_CHARTER.md:201` (§6), quoted at DA-7 |
| DA-13 (181) | :57 | `docs/dafoam/PRIOR_WORK_INVENTORY.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| DA-14 (182) | :58 | **"83 prior-work records"** | **UNVERIFIABLE** | The file holds **269 table rows** and contains the token `83` four times, none of them in the form "83 records" or "83 entries". The lane **could not reach a defensible record count**: the file mixes header, separator, defect-class and prior-work rows in one table and no row-class marker distinguishes them. Reported as unverified rather than graded against a row count that is the wrong denomination. |
| DA-15 (183) | :59 | `cases/dafoam/INDEX.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| **DA-16 (184)** | **:60** | **"most records still cite the old `demo-output/website/dafoam/` path — read it as `cases/dafoam/`"** | **STALE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | **Measured in the single named artifact** `cases/dafoam/INDEX.md`: the old path occurs **2** times; `cases/dafoam` occurs **22** times. "Most" is now **8.3 %**, and the migration the note warns about has substantially happened. The instruction "read it as `cases/dafoam/`" is harmless; the premise is false. |
| DA-17 (186–188) | :90–:92 | folder_scope ×3 | **STILL TRUE** | all three tracked at HEAD + on disk |
| DA-18 (190) | :95 | `/home/ubuntu/certonomous-runs/` exists | **STILL TRUE** | **on disk**: 116 GB |
| DA-19 (195) | :171 | "The F6 series under `cases/dafoam/` is plain simpleFoam with NO adjoint anywhere — it is 88 % of the tree by size" | **STILL TRUE** | **Measured:** `cases/dafoam` = 7,055,808 KB; `cases/dafoam/f6*` = 6,317,032 KB → **89.5 %** (the brief says 88 %; the direction and the magnitude hold, the figure has drifted +1.5 points as the tree grew). Five F6 trees: `f6a_epistemic_band` 1.3 G, `f6a_nasa_hump` 37 M, `f6b_periodic_hills` 71 M, `f6c_duct_dns` 28 K, `f6d_random_matrix_uq` 4.7 G. **Zero adjoint-named files** in any of the three sampled trees. Records in `verification/campaign/` confirmed (`F6a_DIFFUSION_RESULTS.md`, `F6C_RSM_SUCCESSOR_PREREGISTRATION.md`, `F6D_OPTION_A_RESULT.md`, …). |
| DA-20 (196) | :172 | Four upstream defect classes (`D-A`/`D-A2`, `D-B`/`D-B2`, `D-C`, `D-E`) prepared, ALL carrying `Status: NOT FILED ANYWHERE` | **STILL TRUE** | All six class ids present: `docs/dafoam/README.md:235` (D-C), `:236` (D-E); `docs/dafoam/PRIOR_WORK_INVENTORY.md:195` (D-A2), `:197` (D-B2), `:198` (D-C), `:200` (D-E). The string `NOT FILED ANYWHERE` is carried by **126 files** across `docs/` and `cases/`, including both upstream bug-report drafts (`cases/dafoam/UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`, `…_decomposition_adjoint.md`). **Rule 7 holds: nothing is filed.** |

---

## 7. Team `heat-transfer` (yaml 198–244) → `.claude/agents/heat-transfer-supervisor.md`

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| H-1 (204) | :91 | `docs/campaigns/T-family` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| H-2 (205) | :92 | `docs/campaigns/F14-cooling-ladder` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| H-3 (206) | :93 | `verification/runs/T-family` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| H-4 (207) | :94 | `verification/runs/F14-cooling-ladder` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| H-5 (208) | :95 | `verification/runs/THERMAL_K0_runs` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| H-6 (217) | :46 | `docs/charters/VERIFICATION_CHARTER.md` binds this team (owned by verification) | **STILL TRUE** | tracked + on disk; the generated file correctly marks it "owned by **verification**" |
| H-7 (218) | :47 | `docs/charters/CASE_SELECTION_CHARTER.md` binds | **STILL TRUE** | tracked at HEAD + on disk |
| H-8 (220) | :52 | `docs/campaigns/T-family/T_FAMILY_INDEX.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| H-9 (222) | :54 | `docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| H-10 (224) | :56 | `docs/campaigns/T-family/T1b_L4_AMENDMENT.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| H-11 (225) | :57 | "§7 is the completion rule and the age guard verbatim" | **STILL TRUE** | `docs/campaigns/T-family/T1b_L4_AMENDMENT.md:332` — "## 7. Completion rule, age guard, launch discipline". This is the provenance `CLAUDE.md` rule 4 itself cites. |
| H-12 (226) | :58 | `docs/campaigns/F14-cooling-ladder/` exists | **STILL TRUE** | tracked at HEAD + on disk |
| H-13 (228) | :60 | `docs/THERMAL_CAPABILITY_STATE.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| H-14 (231–238) | :91–:98 | folder_scope ×8, incl. three paper topics | **STILL TRUE** | all eight tracked at HEAD + on disk (`docs/papers/forced_convection_heat_transfer/`, `…/buoyant_natural_convection/`, `…/data_center_indoor_airflow/`) |
| H-15 (210–215) | mandate | This team is custodian of the completion rule + age guard, the planted-zero control, and Roache triple gating | **STILL TRUE** | All three are `CLAUDE.md` rules 4, 3 and 5, and all three cite this team's artifacts as provenance (`T1b_L4_AMENDMENT.md` §7, `T3_runs/analyse_t3.py`, `T1_runs/analyse_t1b_L4.py`) |
| H-16 (243) | :174 | "The comparators REFUSE (exit 2) rather than degrade. A refusal is a finding." | **STILL TRUE** | **Second planted-control save.** A literal `sys.exit(2)` search of `verification/runs/T-family/T3_runs/analyse_t3.py` returns **0**; the same reader returns **1** on `T10a_runs/analyse_t10a.py`, proving it can see a non-zero. The zero is a **notation** artifact: `analyse_t3.py:97` declares `EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2` and `:103` refuses with `sys.exit(EXIT_REFUSE)` after printing `REFUSE: `. The file's own docstring at `:55` states "exit 2 (REFUSE) unless DONE.<case> exists for all eight cases". **The claim is true; the census by identifier would have called it false.** |
| **H-17 (244)** | **:175** | **"D389 is open and unowned by one rung: S13 normalises peak-to-peak spread by the mean, which on an absolute temperature is ~24x looser than it reads. Changing it re-grades the whole thermal corpus. Do not settle it unilaterally."** | **STALE — SETTLED** | **`docs/DOCKET.md:758` (HEAD blob), D393: "SETTLES D389, AND REPAIRS A FALSE POSITIVE THIS AGENT SHIPPED HOURS EARLIER IN THE SAME CRITERION."** The repair is named in the row: the spread is now referred to **the range the quantity spanned over the run** (`docs/physics_rules.yaml` `heat_monitor_normaliser: range_spanned_over_run`, `MONITOR_STANDARD` v1.12, `scripts/check_convergence.py`); the 0.02 % threshold is unchanged. The corpus re-grade the note warns must happen **has happened**: all 49 committed cases (K0c 11, K2e 30, K2b 8) re-graded, **exactly two verdicts changed, both K2b's**. D389 itself stands at `:754`. **Two further details make the line worse than merely out of date:** (a) the "~24x" figure is D389's own and D393 measures the real factor at **3,343** on a rack-inlet temperature — the brief carries the smaller of two numbers the docket already reconciled; (b) the instruction "Do not settle it unilaterally" now instructs a team not to disturb a repair it already landed. |

---

## 8. Team `cfd` (yaml 246–300) → `.claude/agents/cfd-supervisor.md`

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| CF-1..CF-7 (252–258) | :90 | `cases/tmr`, `cases/hlpw6`, `cases/valve`, `cases/unsteady-cylinder`, `cases/committee-grids`, `cases/mega-batch`, `cases/demo-surfaces` in scope | **STILL TRUE** (7 rows) | all seven tracked at HEAD + on disk |
| CF-8 (259) | :93 | `docs/standards` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CF-9 (260) | :94 | `docs/OPENFOAM.md` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CF-10 (261) | :95 | `docs/OPENFOAM_SOLVER_BUILD.md` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CF-11 (262) | :92 | `verification/campaign` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CF-12 (263) | :96 | `models` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| CF-13 (273) | :45 | `docs/charters/CASE_SELECTION_CHARTER.md` binds | **STILL TRUE** | tracked at HEAD + on disk |
| CF-14 (274) | :46 | `docs/charters/RESULT_PRIORITY_CHARTER.md` binds (owned by verification) | **STILL TRUE** | tracked + on disk; correctly marked "owned by **verification**" |
| CF-15 (276) | :51 | `docs/standards/MESH_STANDARD.md` exists | **STILL TRUE** | tracked at HEAD + on disk, 2,075 lines, "Version 1.2, dated 2026-08-11" |
| **CF-16 (277)** | **:52** | **"the mesh standard; confirm the live path at read time, *a copy also sits at `docs/MESH_STANDARD.md`*"** | **STALE / FALSE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | **It is not a copy and the two documents are not the same subject.** Measured: `docs/standards/MESH_STANDARD.md` sha256 `3d1c766879141c04…`, **2,075 lines**, titled "**Certonomous Mesh Standard**, Version 1.2, dated 2026-08-11". `docs/MESH_STANDARD.md` sha256 `0f9bdeafd0d73d31…`, **260 lines**, titled "**Grid-Convergence Practice — Inherited from DPW-8/AePW-4 (D8)**", dated 2026-07-29. Different hash, 8x different length, different document. **`CLAUDE.md`'s own WHERE-THINGS-LIVE table already says so** (line 286): "`docs/MESH_STANDARD.md` is a **different** doc (grid families)". The brief contradicts the constitution on a file the cfd team reads before every mesh. |
| CF-17 (278) | :53 | `docs/standards/MONITOR_STANDARD.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| CF-18 (280) | :55 | `docs/OPENFOAM.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| CF-19 (282) | :57 | `docs/OPENFOAM_SOLVER_BUILD.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| CF-20 (284) | :59 | `verification/campaign/` exists | **STILL TRUE** | tracked + on disk; **458 `.md` files** |
| CF-21 (285) | :60 | "THE VERDICTS LIVE HERE … Most run dirs under `verification/runs/` carry no README, RESULTS or marker at all" | **STILL TRUE** | **Measured:** of **93** top-level families under `verification/runs/`, **83** carry no `README*` or `RESULTS*` at their top level — **89.2 %**. "Most" is an understatement. |
| CF-22 (287–295) | :90–:98 | folder_scope ×9 (the two exclusion-phrased entries plus `verification/campaign/`, `docs/standards/`, the two OpenFOAM docs, `models/`, and two paper topics) | **STILL TRUE** | `docs/papers/benchmark_test_cases/` and `docs/papers/turbulence_models/` both tracked at HEAD + on disk; the exclusion entries are definitional, and the excluded trees (`RANS_LES_closure_models/`, `dafoam/`, `T-family/`, `F14-cooling-ladder/`, `THERMAL_K0_runs/`) all exist and are scoped to their own teams |
| CF-23 (299) | :174 | "Verdicts live in `verification/campaign/*.md`, one level up from the run trees." | **STILL TRUE** | 458 `.md` files there; corroborated independently by CF-21's 83/93 measurement |
| CF-24 (300) | :175 | "`models/tmr/**` deliberately holds solver cases outside a run tree — a documented FILING_CHARTER §3 exception." | **STILL TRUE** | `models/tmr` on disk + tracked; `docs/charters/FILING_CHARTER.md:50–51` — "**`models/tmr/**`** holds solver cases outside a run tree. They are reference case definitions rather than run outputs" |

---

## 9. Team `verification` (yaml 302–364) → `.claude/agents/verification-supervisor.md`

This team's own brief carries four of the sixteen stale rows. They are graded here
without discount.

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| V-1 (308) | :41, :90 | `docs/charters/VERIFICATION_CHARTER.md` owned | **STILL TRUE** | tracked at HEAD + on disk |
| V-2 (309) | :42, :91 | `docs/charters/RESULT_PRIORITY_CHARTER.md` owned | **STILL TRUE** | tracked at HEAD + on disk |
| V-3 (310) | :92 | `docs/papers/verification_validation` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| V-4 (311) | :94 | `verification/certificates` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| V-5 (312) | :95 | `verification/credibility` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| V-6 (313) | :96 | `verification/monitor` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| V-7 (314) | :98 | `docs/UNCERTAINTY-DOCTRINE.md` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| V-8 (315) | :99 | `docs/VALIDATION_INVENTORY.md` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| **V-9 (331)** | **:52** | **charter is "v1.10 (2026-08-22)"** | **STALE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | The header at `:3` does read "Version 1.10, dated 2026-08-22" — **and it is frozen by rule 6 and will read that forever.** The current version is at the amendment foot: **`docs/charters/VERIFICATION_CHARTER.md:10140` — "## Amendment — v1.96, 2026-09-10"**, and the closing table at `:10154` reads `\| amendment record \| **v1.96** \|`. **86 amendments and 19 days ahead of the brief**; the charter is 10,159 lines at HEAD (worktree identical, same line count). The clauses added since v1.10 include §2bf–§2cf.2 — the arming-defect, planted-control and census clauses this very audit is written under. |
| V-10 (331) | :52 | "Read §1, §2, §2a, §2b, §2c, §2d/§2d.1, §2e, §3, §7, §9, §16" | **STILL TRUE** | every cited section token present in the HEAD blob: §1 (30 hits), §2a (323), §2b (241), §2c (109), §2d.1 (90), §2e (1), §3 (47), §7 (30), §9 (1), §16 (6). §2e and §9 are single-occurrence and were checked individually rather than inferred from a count. |
| V-11 (333) | :54 | RESULT_PRIORITY is **"v0.5 — a DRAFT awaiting Sanaa. Its orderings are proposals; only the bright line is settled"** | **STILL TRUE** | Header at `:3` — "Version 0.5, dated 2026-08-17. **This is a draft for the owner to react to, not…**"; no amendment foot; 691 lines. **Still awaiting her. This is the one version claim in the file that is exactly right, and it is right because nothing moved.** |
| V-12 (334) | :55 | `docs/papers/verification_validation/` exists | **STILL TRUE** | tracked + on disk; holds the Ansys manual PDF + sidecar and five other title-verified V&V papers with sidecars |
| **V-13 (335)** | **:56** | **"the V&V corpus, incl. the Ansys manual *and the incoming `VM2026R1_Fluids` case folder*"** | **STALE — SETTLED** | The folder never landed there and is now nowhere in the repository. **`docs/DOCKET.md:861` (HEAD blob), D496: "D-6 resolved by the new team's exclusive ownership of archives and manual"**, and **`:869`, D504: "D-6 EXECUTED"**. The canonical home is **`/home/ubuntu/ansys-vm2026r1/`**, outside git (see V-16). Nothing is "incoming". |
| V-14 (336) | :57 | `docs/UNCERTAINTY-DOCTRINE.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| V-15 (338–339) | :59, :60 | `docs/LESSONS.md` exists; "do not read cold — take the reading per `docs/MEMORY_ARCHITECTURE.md` §5" | **STILL TRUE** | both tracked at HEAD + on disk |
| **V-16 (344)** | **:93** | **folder_scope entry `VM2026R1_Fluids/`** | **STALE — SETTLED** | **The path does not exist, at HEAD or on disk, at the repository root or anywhere under it.** `git cat-file -e cc2a2e039:VM2026R1_Fluids` → absent; `test -e` → absent; a bounded `find` over the repo at depth 2 returns only `docs/VM2026R1_FILING_ANALYSIS.md`. **It is now `.gitignore`d by name** (`.gitignore:320`, under the header at `:314`: "*ANSYS VM2026R1 archive set -- D-6 ruling, 2026-08-24 … The canonical home is `/home/ubuntu/ansys-vm2026r1/`, OUTSIDE this repository*"). Settled by **D496 (`docs/DOCKET.md:861`)** and **D504 (`:869`)**. A folder-scope entry naming a gitignored, non-existent path is a scope that cannot be entered. |
| V-17 (352–357) | :102–:107 | six standing audits exist | **STILL TRUE** (6 rows) | `DEAD_LEVER`, `EXTERNAL_REFERENT`, `FAIL_OPEN_GATE`, `H4_ALLOCATION`, `LEDGER_HEADLINE`, `SWEEP_REFRAME` — all six `docs/*_AUDIT.md` tracked at HEAD + on disk |
| V-18 (359) | ladders | "Cross-team gate audit (incl. the ansys-verification team's VM2026R1 verdicts, from 2026-08-24); the six standing audits" | **STILL TRUE** | D496 (`:861`) ratifies the six-team structure on 2026-08-24; `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` holds graded rows to audit (2,707 lines, 518 VMFL-id citations) |
| **V-19 (361)** | **:183** | **"`VM2026R1_Fluids` is UNTRACKED and unpacked twice — at the repo root and under `docs/papers/verification_validation/`. Decide the canonical home under FILING_CHARTER R8/R6 and say which copy is authoritative *before grading anything from it*."** | **STALE — SETTLED** | **The decision was made, executed, and moved to another team.** `docs/DOCKET.md:861` (D496): Sanaa 2026-08-24, verbatim — *"yes it's approved by me. I ratify the six team structure. I apporve all actually"* — closing **D-3, D-4, D-5 and D-6**; `:869` (D504): "**D-6 EXECUTED**". The ruling is a tracked repository document: `docs/ansys_verification/ARCHIVE_HOME_RULING.md`, "**Status: RULING — in force**", clause (a): the canonical home is **`/home/ubuntu/ansys-vm2026r1/`**. **Both copies the note names are gone** — measured at `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`: **123 files, 2.5 GB, CFX 37 / FLUENT 77 / FORTE 9**, exactly the composition the charter's §9 inspection recorded for the pre-move copy. The ruling's own dated execution line of 2026-08-25T21:17Z records the same measurement and says of its earlier §3 table: "*THE RECORD ABOVE IS STALE … the disk says clause (c) IS DONE*". |
| **V-20 (362)** | **:184** | **"A known open conflict: charter §2 says GATE FAIL, some ledger cells read bare FAIL. Referred, unruled. Do not settle it silently."** | **STALE — SETTLED** | **`docs/DOCKET.md:861` (HEAD blob), D496, item (3): "D-5 closed under the chief's DISCLOSED interpretation — rule 1's vocabulary as written; the 3 legacy bare-`FAIL` cells are corrected to `GATE FAIL` by their owning teams by quote-and-strike, never rewritten; she can overturn the reading."** D-5 is the bare-`FAIL` desk item by name, and Sanaa's *"I apporve all actually"* of 2026-08-24 closes it. It is no longer "referred, unruled" — it is ruled, with the reading disclosed and a named remedy. **Collateral, reported and NOT changed:** `CLAUDE.md` rule 1 still ends "*Open conflict on record: some ledger cells read bare `FAIL` … referred, unruled*". That is the constitution, not this audit's territory, and it is flagged for Sanaa in §11 rather than edited. |
| V-21 (363) | :185 | "The Ansys manual's `.txt` sidecar EXISTS and is tracked since 2026-08-23 … its basename still does not match FILING_CHARTER R8's `author_year` pattern" | **STILL TRUE** (both measured halves) | Sidecar tracked at HEAD + on disk; first added in commit **`090c070cd`, dated 2026-08-23**, subject "verification: .txt sidecar for the Ansys Fluid Dynamics Verification Manual". R8 at `FILING_CHARTER.md:40` requires `author_year_identifier.pdf` + matching `.txt`; `Ansys_Fluid_Dynamics_Verification_Manual.txt` carries **no year** and still does not match. |
| **V-22 (363)** | **:185** | **"— rides in the D-6 memo §4"** (the trailing clause of V-21) | **STALE — SETTLED** | D-6 is closed (D496, `docs/DOCKET.md:861`) and the ruling that replaced the memo **expressly declines this question**: `docs/ansys_verification/ARCHIVE_HOME_RULING.md:53`, clause (f) — "*The manual PDF + sidecar stay tracked where they are; the R8 basename…*" — and `:81`, "**What the ruling deliberately does not decide.** The R8 basename of the manual…". **The R8 basename question is real, is still open, and no longer has a carrier.** A note pointing at a closed memo is how an open question goes missing. |
| V-23 (364) | :186 | "Since 2026-08-24 the RUNNING of the VM2026R1 cases and the canonical-home decision belong to the ansys-verification team … This team keeps `docs/papers/verification_validation/` and AUDITS their verdicts; it does not run the cases." | **STILL TRUE** | D496 (`:861`) creates the team on 2026-08-24 with Sanaa's verbatim directive; `docs/charters/ANSYS_VERIFICATION_CHARTER.md` exists and is that team's. **The canonical-home half is now not merely owned but executed** (V-19) — the ownership statement stands, the pending-decision framing around it does not. |

---

## 10. Team `ansys-verification` (yaml 366–498) → `.claude/agents/ansys-verification-supervisor.md` and the three lane files

| assertion (yaml line) | generated-file line | claim | verdict | evidence |
|---|---|---|---|---|
| AN-1 (372) | :100 | `docs/ansys_verification` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| AN-2 (373) | :101 | `cases/ansys_verification` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| AN-3 (374) | :102 | `verification/runs/ansys_verification` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| AN-4 (375) | :103 | `verification/credentials/ansys` in scope | **STILL TRUE** | tracked at HEAD + on disk |
| AN-5 (376) | :41, :104 | `docs/charters/ANSYS_VERIFICATION_CHARTER.md` owned | **STILL TRUE** | tracked at HEAD + on disk, 3,270 lines |
| AN-6 (377) | :105 | the manual **PDF** at the explicit path | **STILL TRUE** | tracked at HEAD + on disk |
| AN-7 (378) | :106 | the manual **.txt sidecar** at the explicit path | **STILL TRUE** | tracked at HEAD + on disk |
| AN-8 (401) | :51 | "290 pages" | **STILL TRUE** | `pdfinfo` on the PDF: **Pages: 290** |
| AN-9 (401) | :51 | "VMFL001–078" | **STILL TRUE** | sidecar holds **78 distinct `VMFL###` ids**, max **VMFL078** |
| AN-10 (401) | :51 | "VMFRT001–007" | **STILL TRUE** | sidecar holds **7 distinct `VMFRT###` ids** |
| AN-11 (401) | :51 | "VMFLGPU cases" | **STILL TRUE** | `VMFLGPU` occurs **45** times in the sidecar |
| AN-12 (401) | :51 | "Title-page verify it against the PDF (rule 15) before citing a number" | **STILL TRUE** | a standing instruction, consistent with `CLAUDE.md` rule 15 and `L-144` (`docs/LESSONS.md:7046`) |
| **AN-13 (403)** | **:53** | **charter is "v1.0 (2026-08-24)"** | **STALE — SUPERSEDED BY REPOSITORY STATE, no docket entry** | Header at `:3` reads "**Version 1.0, dated 2026-08-24**" and is frozen by rule 6. The amendment foot runs to **`docs/charters/ANSYS_VERIFICATION_CHARTER.md:3129` — "## Amendment — v1.34"** (v1.32 at `:2835`, v1.33 at `:2955`). **34 amendments ahead of the brief**, on a 3,270-line charter whose first version was 285 lines of table. |
| AN-14 (403) | :53 | the cited sections §1, §3, §4, §5, §6, §7, §8 all exist | **STILL TRUE** | present in the worktree file: §1 (127 hits), §3 (198), §4 (4), §5 (11), §6 (5), §7 (16), §8 (9); §9 (1) also present for the precondition at AN-22 |
| AN-15 (404) | :54 | `docs/ansys_verification/README.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| AN-16 (406) | :56 | `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| AN-17 (407) | :57 | "every case run so far, its verdict, artifact path, prereg sha, cost and date — append-only" | **STILL TRUE** | 2,707 lines; header row at `:22` carries exactly those columns (`# \| Case \| Date (UTC) \| Verdict \| Lab value \| Reference \| Tolerance (frozen) \| Artifact path \| Prereg sha \| Comparator sha …`); row 1 is **VMFL001, `NOT A RESULT`** — a negative verdict kept in the register, as the mandate requires |
| AN-18 (408) | :58 | `docs/VM2026R1_FILING_ANALYSIS.md` exists | **STILL TRUE** | tracked at HEAD + on disk |
| **AN-19 (409)** | **:59** | **"the verification team's D-6 memo … *the decision is now YOURS, first action*"** | **STALE — SETTLED** | The decision was taken on the day the team formed. `docs/DOCKET.md:869` (D504): "**D-6 EXECUTED**"; the ruling is `docs/ansys_verification/ARCHIVE_HOME_RULING.md`, "**Status: RULING — in force**", issued 2026-08-24, with a dated execution line at 2026-08-24T17:18Z. The memo is now input to a closed ruling, not a pending first action. |
| AN-20 (410–411) | :60, :61 | `VERIFICATION_CHARTER.md`; "§2 vocabulary, §2b amendment legality, §2d comparator freeze, §9 evidence record" | **STILL TRUE** | all four section tokens present in the HEAD blob (see V-10) |
| AN-21 (412–413) | :62, :63 | `COMPUTE_BUDGET_CHARTER.md`; "§5 the box cannot read its billing, §6 waste named separately; the calibration row at every completion (CLAUDE.md rule 12)" | **STILL TRUE** | file tracked + on disk; matches `CLAUDE.md` rule 12's own citations of §5 and §6 and the `docs/COST_CALIBRATION.md` duty |
| AN-22 (415–421) | :100–:106 | folder_scope ×7 | **STILL TRUE** | all seven tracked at HEAD + on disk (same paths as AN-1..AN-7) |
| **AN-23 (423)** | **:109** | **external_data: "`VM2026R1_Fluids/` at the repository root — UNTRACKED, 123 files, 2.5 GB (FLUENT 77 / CFX 37 / FORTE 9); the complete copy as of 2026-08-24"** | **STALE — SETTLED** | **The path is absent from the repository root**, at HEAD and on disk. The *contents* survive intact at the ruled canonical home: `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/` — **measured on disk: 123 files, 2.5 GB, FLUENT 77 / CFX 37 / FORTE 9**, the composition the brief states. Settled by **D496 (`docs/DOCKET.md:861`)** and **D504 (`:869`)**; `.gitignore:314–320` records the ruling and guards the name. **The counts are right and the location is wrong** — which is the dangerous shape, because a lane that verifies the counts will conclude the line is current. |
| **AN-24 (424)** | **:110** | **external_data: "`docs/papers/verification_validation/VM2026R1_Fluids/` — UNTRACKED, 10 files, 26 MB, CFX only, a DEAD partial transfer; 9 files byte-identical to the root copy, `VMFL011B.wbpz` TRUNCATED (327,680 of 670,152 bytes)"** | **STALE — SETTLED** | **The path does not exist** (HEAD or disk). Deleted under clause (c) of the ruling; `ARCHIVE_HOME_RULING.md:127` records the supervisor's own 2026-08-25T21:17Z disk read: "*(c) … "still holds **10 files**" — **ABSENT** — the path does not exist*". **And the truncation claim is separately withdrawn by that same record: `VMFL011B.wbpz` is 670,152 bytes — its FULL size.** The brief still tells a lane that a file in a deleted directory is corrupt. |
| AN-25 (426) | ladders | "VMFL001–078 … VMFRT001–007 (Forte) and VMFLGPU follow as capability allows" | **STILL TRUE** | corroborated by AN-9/AN-10/AN-11 against the sidecar |
| AN-26 (428) | :93 | precondition: read the manual sidecar first, title-page verified (rule 15) | **STILL TRUE** | sidecar exists (AN-7); the instruction is Sanaa's, recorded verbatim in D496 (`docs/DOCKET.md:861`) — *"Both supervisor and opus subagent must read th everification manual first"* |
| AN-27 (429) | :94 | precondition: every opus lane's brief names the case id, manual page, reference result and tolerance | **STILL TRUE** | consistent with `ANSYS_VERIFICATION_CHARTER` §5 and with the register's column set (AN-17) |
| **AN-28 (430)** | **:95** | **precondition: "FIRST ACTION of the team: rule on the archives' canonical home (D-6) … *Until you rule, neither copy is moved or deleted.*"** | **STALE — SETTLED** | **Ruled 2026-08-24 and executed.** `docs/ansys_verification/ARCHIVE_HOME_RULING.md` is in force; `docs/DOCKET.md:869` (D504) records "D-6 EXECUTED". Both copies **have** been moved and deleted, lawfully, under clauses (a)–(c) of that ruling. **This is the sharpest of the stale rows: it is a live prohibition on an action already taken, presented to the team as its first action at every session start.** |
| AN-29 (431) | :96 | precondition: no compute without a COMMITTED pre-registration; no GATE FAIL / NOT A RESULT softened | **STILL TRUE** | matches `CLAUDE.md` rules 1 and 2; the register's row 1 carries `NOT A RESULT` unsoftened (AN-17) |
| AN-30 (432–438) | :122 | `max_live_lanes: 4` with `lane_cap_note` naming Sanaa's 2026-08-24 exception to `SUPERVISION_CHARTER` v1.4 §8 | **STILL TRUE** | `docs/DOCKET.md:861` (D496) item (1): "*the 3-lane cap per supervisor of `SUPERVISION_CHARTER.md` §8 is standing law, with the ansys-verification team's 4 lanes (2 Opus, 2 Haiku) as her explicit exception — dated addendum at that charter's foot, lines renumbered above it: 0*"; the addendum is at `SUPERVISION_CHARTER.md:549` — "## Amendment record, continued: §8's lane cap ratified, with one owner's exception (2026-08-24)". **A disclosed override with its authority named, exactly as `defaults.max_live_lanes`'s own comment requires.** |
| AN-31 (440–458) | `ansys-lane-opus.md` | lane `ansys-lane-opus`, model `opus`, must_read the manual + the ansys charter | **STILL TRUE** | file exists; both must_read paths tracked at HEAD + on disk |
| AN-32 (459–478) | `ansys-lane-opus48.md` | lane `ansys-lane-opus48`, model `claude-opus-4-8`, same must_read | **STILL TRUE** | file exists; the model id is documented and D504 (`docs/DOCKET.md:869`) records the pin as "**load-verified**" |
| AN-33 (479–498) | `ansys-lane-haiku.md` | lane `ansys-lane-haiku`, model `haiku`, `tools: [Bash, Read, Grep, Glob]`, four `limits` | **STILL TRUE** | file exists with the restricted tool list; this is the one place `defaults.tools` permits a `tools:` key, and the generator's round-trip check passes |
| AN-34 (494–498) | `ansys-lane-haiku.md` limits | "You never move, delete, rename or git-add anything under `VM2026R1_Fluids/` (either copy)" | **UNVERIFIABLE** | The limit is still the right *instruction*, but **neither copy it names exists any more** (AN-23, AN-24). Whether it now binds the haiku lane at the canonical home `/home/ubuntu/ansys-vm2026r1/` **cannot be determined from the text** — the path is named only by its old spelling. Graded UNVERIFIABLE rather than STALE because the prohibition may be intended to follow the archives; only Sanaa's edit can say. |

---

## 11. WHAT SANAA'S DESK IS OWED

**Every line below is a PROPOSAL. Nothing here was applied. `harness/teams.yaml`
and `.claude/agents/` are byte-identical to their state at `cc2a2e039`** — and
must stay so until Sanaa rules, under `CLAUDE.md` rule 9.

Two operational facts for the desk:

- **The generator round-trips cleanly** (`generate_agents.py --check` → `OK: 10
  agent file(s)`). So **every YAML edit below is one edit with a known blast
  radius**: change the YAML line, re-run the generator, and the named generated
  line follows. No generated file should ever be hand-edited.
- **The sixteen stale rows are not one team's problem.** They are spread
  1 closure / 3 dafoam / 1 heat-transfer / 1 cfd / 4 verification / 4 ansys, plus
  2 counted inside dafoam and verification rows above. The verification team —
  the auditor — carries the equal-largest share.

### 11.1 The sixteen proposed edits

| # | yaml line | generated line | proposed replacement (PROPOSAL ONLY) | authority for the change |
|---|---|---|---|---|
| P-1 | **244** | `heat-transfer-supervisor.md:175` | **Delete the D389 hazard and replace with:** `"S13's peak-to-peak normaliser was D389 and is SETTLED by D393: the spread is referred to the range the quantity spanned over the run (docs/physics_rules.yaml heat_monitor_normaliser: range_spanned_over_run, MONITOR_STANDARD v1.12, scripts/check_convergence.py). The 49-case corpus re-grade is done; two K2b verdicts changed. Do not re-open it as if unsettled."` | `docs/DOCKET.md:758` (D393) |
| P-2 | **151** | `closure-supervisor.md:172` | **Replace with:** `"NASA_hump_gate/ and _common/uq_eigenspace/ are tracked at HEAD and present on disk (4 files each); the staged-as-deleted condition is cleared. The standing rule is unchanged: an unexpected change is inspected, never reverted (CLAUDE.md rule 10)."` | measurement: `git diff-index --cached` empty, `git ls-tree` 8 files, `find` 8 files |
| P-3 | **176** | `dafoam-supervisor.md:52` | **Replace `v1.0b (2026-08-21)` with `v1.0g (2026-09-05)`** | `docs/charters/DAFOAM_CHARTER.md:3` |
| P-4 | **176** | `dafoam-supervisor.md:52` | **Replace `§11 the toolchain identity rule` with `§6 the toolchain identity rule (an image ID and a library hash, never a version string)`** | `docs/charters/DAFOAM_CHARTER.md:201` vs `:412` |
| P-5 | **184** | `dafoam-supervisor.md:60` | **Replace with:** `"the case map; a few records still cite the old demo-output/website/dafoam/ path (2 of 24 path citations in this file) — read those as cases/dafoam/"` | measured in `cases/dafoam/INDEX.md`: 2 old vs 22 new |
| P-6 | **277** | `cfd-supervisor.md:52` | **Replace with:** `"the mesh standard (quality gates). docs/MESH_STANDARD.md is a DIFFERENT document — 'Grid-Convergence Practice, inherited from DPW-8/AePW-4 (D8)', grid families, 260 lines — not a copy of this one. Confirm the live path at read time."` | sha256 `3d1c…` vs `0f9b…`; 2,075 vs 260 lines; **`CLAUDE.md:286` already states it** |
| P-7 | **331** | `verification-supervisor.md:52` | **Replace `v1.10 (2026-08-22)` with `v1.96 (2026-09-10) — the header still reads v1.10 by rule 6; the current version is the amendment foot at :10140`** | `VERIFICATION_CHARTER.md:10140`, `:10154` |
| P-8 | **335** | `verification-supervisor.md:56` | **Delete `and the incoming VM2026R1_Fluids case folder`**; the corpus entry otherwise stands | D496 `docs/DOCKET.md:861`; D504 `:869` |
| P-9 | **344** | `verification-supervisor.md:93` | **Delete the folder_scope entry `VM2026R1_Fluids/`** | path absent at HEAD and on disk; `.gitignore:320` |
| P-10 | **361** | `verification-supervisor.md:183` | **Replace with:** `"The VM2026R1 archives' canonical home is RULED and EXECUTED: /home/ubuntu/ansys-vm2026r1/ (123 files, 2.5 GB), outside git, per docs/ansys_verification/ARCHIVE_HOME_RULING.md, D-6 closed at D496 and executed at D504. Neither in-repo copy exists. Audit the ansys team's verdicts; do not re-litigate the home."` | D496 `:861`; D504 `:869`; `ARCHIVE_HOME_RULING.md` |
| P-11 | **362** | `verification-supervisor.md:184` | **Replace with:** `"The bare-FAIL conflict (desk item D-5) is CLOSED at D496 under the chief's disclosed reading — rule 1's vocabulary as written; the 3 legacy bare-FAIL cells are corrected to GATE FAIL by their owning teams by quote-and-strike, never rewritten. Sanaa can overturn the reading. NOTE FOR THE DESK: CLAUDE.md rule 1 still describes this as 'referred, unruled'."` | D496 `docs/DOCKET.md:861` item (3) |
| P-12 | **363** | `verification-supervisor.md:185` | **Replace the trailing `— rides in the D-6 memo §4` with `— the D-6 ruling expressly declines this question (ARCHIVE_HOME_RULING.md §1(f) and 'what the ruling deliberately does not decide'); the R8 basename question is OPEN AND UNCARRIED and needs a home.`** | `ARCHIVE_HOME_RULING.md:53`, `:81` |
| P-13 | **403** | `ansys-verification-supervisor.md:53` | **Replace `v1.0 (2026-08-24)` with `v1.34 — the header reads v1.0 by rule 6; the current version is the amendment foot at :3129`** | `ANSYS_VERIFICATION_CHARTER.md:3129` |
| P-14 | **409** | `ansys-verification-supervisor.md:59` | **Replace `the decision is now YOURS, first action` with `input to the D-6 ruling, which is CLOSED — see docs/ansys_verification/ARCHIVE_HOME_RULING.md`** | D504 `docs/DOCKET.md:869` |
| P-15 | **423–424** | `ansys-verification-supervisor.md:109–110` | **Replace both external_data entries with a single entry:** `"/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/ — the canonical home ruled at D-6, OUTSIDE git and .gitignore-guarded: 123 files, 2.5 GB (FLUENT 77 / CFX 37 / FORTE 9). Both former in-repo copies are gone. VMFL011B.wbpz is COMPLETE at 670,152 bytes — the earlier truncation finding is withdrawn (ARCHIVE_HOME_RULING.md dated line 2026-08-25T21:17Z)."` | measured on disk; `ARCHIVE_HOME_RULING.md:127` and its dated execution line |
| P-16 | **430** | `ansys-verification-supervisor.md:95` | **Delete the precondition entirely, or replace with:** `"The archives' canonical home is RULED (D-6, 2026-08-24) and in force at docs/ansys_verification/ARCHIVE_HOME_RULING.md. Read it before touching an archive; do not re-rule it."` | D504 `docs/DOCKET.md:869`; the ruling in force |

### 11.2 Three things the desk should see that are NOT edits to `harness/`

1. **`CLAUDE.md` rule 1 is stale in the same way as P-11.** It still reads
   "*Open conflict on record: some ledger cells read bare `FAIL` … referred,
   unruled*", while D496 (`docs/DOCKET.md:861`) closed D-5 on 2026-08-24 with
   Sanaa's own words. **This audit did not touch `CLAUDE.md`** — rule 9 forbids
   it on any agent's say-so, and the constitution is Sanaa's document.
2. **`CLAUDE.md:282` says there are 12 charters; `ls docs/charters/*_CHARTER.md | wc -l`
   returns 14.** The line's own text names `ls | wc -l` as the authority over any
   prose count, so the line is self-correcting by its own terms — but it reads
   wrong. Reported, not changed.
3. **The Fable substitution (D-1) has no expiry check.** `teams.yaml:45` sets
   `supervisor_model: opus` as a *temporary* departure from
   `SUPERVISION_CHARTER` §5, and `CLAUDE.md:235–237` still asserts supervisors
   run on Fable. Nothing on this box can measure whether Fable capacity has
   returned, so **the temporary state has no condition that will ever fire**. A
   revert needs Sanaa; a date to re-ask would cost nothing.

### 11.3 The single most consequential stale line, argued

**It is not D389. It is `harness/teams.yaml:277` → `.claude/agents/cfd-supervisor.md:52`
— the claim that "a copy also sits at `docs/MESH_STANDARD.md`".**

D389 (P-1) is the loudest, and it nearly cost the lab a re-grade. But D389 fails
*safe*: it tells a team to be more careful than necessary about a gate it has
already repaired. A lane that obeys it wastes an hour and settles nothing wrong.
The same is true of AN-28's dead first-action precondition — an instruction to do
something already done is caught the moment the lane reads
`ARCHIVE_HOME_RULING.md`, which the same brief tells it to read.

CF-16 fails **open, and it fails silently**:

1. **It is a file-identity error, not a currency error.** The other fifteen stale
   rows describe a state that *used* to hold. This one describes a relationship
   between two files that the measurement says has never held at this HEAD:
   different sha256, 2,075 lines against 260, "Certonomous Mesh Standard v1.2"
   against "Grid-Convergence Practice — Inherited from DPW-8/AePW-4 (D8)". There
   is no date at which "a copy" was true of these two bytes.
2. **The word "copy" disarms the check the same sentence asks for.** The line
   says "confirm the live path at read time" — and then tells the lane the two
   candidates are interchangeable. A lane that confirms a path and lands on
   `docs/MESH_STANDARD.md` has satisfied the instruction it was given and is
   reading the wrong document. **The instruction and its own escape hatch are in
   one sentence.**
3. **The document it misroutes to is the one a mesh verdict is graded against.**
   `docs/standards/MESH_STANDARD.md` carries the quality gates. `docs/MESH_STANDARD.md`
   carries grid families. A lane grading a mesh against grid-family prose instead
   of quality gates produces a number with no gate behind it — and nothing
   downstream would catch it, because the run completes, the fields are present
   and the age guard passes. It is a **fail-open gate**, the failure class this
   team keeps a standing audit for (`docs/FAIL_OPEN_GATE_AUDIT.md`).
4. **It contradicts the constitution, which already got this right.**
   `CLAUDE.md:286` states plainly: "`docs/MESH_STANDARD.md` is a **different** doc
   (grid families)". The roster and the constitution disagree about a file, and
   the roster is what gets loaded into the cfd supervisor's context at every
   session start. When two authorities disagree and only one is in the brief, the
   brief wins by default — which is exactly why a wrong brief line is worse than a
   wrong line anywhere else.

D389 was the occasion for this audit. **CF-16 is the reason it was worth
running.**

---

## 12. Verdict on the audit itself

**GATE REACHED** — 171 assertions enumerated and graded against `cc2a2e039`, 148
STILL TRUE, 16 STALE, 7 UNVERIFIABLE, every stale row carrying either a docket
citation or a named measurement, and every unverifiable row naming the specific
measurement not taken. Zero core-minutes; no solver ran; no ledger row owed.

This is a **GATE REACHED** and not a PASS because no pre-registered threshold
existed for "how many stale rows is too many" — the audit was commissioned after
the first stale row was found, so there was no prediction to grade against. Under
`CLAUDE.md` rule 2 a gate chosen after the answer is visible has no evidentiary
content, and this document does not claim one. **The findings are measurements;
the disposition is Sanaa's.**

**SUBMISSIONS PARKED (rule 7). PERMANENTLY PRIVATE (rule 8). Nothing in this
document has been sent, filed or shared, and nothing in `harness/` or `.claude/`
was changed by the lane that wrote it.**
