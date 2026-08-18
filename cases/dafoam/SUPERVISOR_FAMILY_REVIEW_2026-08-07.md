# Family supervisor first-pass review: case-file discrepancies and the personal check on the two highest-risk code artifacts

**2026-08-07, DAFoam/adjoint family supervisor (standing, under the
SUPERVISION_CHARTER structure being drafted in `docs/charters/`).** First pass
over the full case file: `DAFOAM_CASE_STATUS.md`,
`DEFECT_ROBUSTNESS_mesh_and_setup.md`, `DISCRIMINATORS_A4_decomposition_mechanism.md`,
both `UPSTREAM_BUG_REPORT_*` drafts, `ladder-b/W4_ADJOINT_PC_UNBLOCK.md`, the
committed state of `demo-output/website/latex/dafoam_defect_report.tex`
(disclosed as under concurrent update), LESSONS L-29..L-38, and the four
supervisor verification sweeps they cite. Posture: the record is wrong until it
defends itself. Everything found is RECORDED HERE FIRST; the subset applied
in-place is listed at the end with the exact edits, per the fix-nothing-before-
recording rule.

Companion standing document produced by the same pass:
`FAMILY_SUPERVISION_GUIDELINES.md` (the rules; this file is the findings).

---

## Part 1 — cross-document discrepancy list (file:line)

### DISC-1. LESSONS.md L-37 carries the mis-transcribed KSP count the 2026-08-07 sweep ordered corrected everywhere. SEVERITY: MEDIUM (stale headline-adjacent number in a document other agents quote as law)

`LESSONS.md:1691` — "took the ... adjoint Krylov count from 590 to 41".
The defect-robustness supervisor sweep
(`VERIFICATION_defect_robustness_supervisor_sweep.md:28-31`, commit 8bd47b35)
established by fleet-wide grep that **719, not 590** is the established scotch
np=4 count (590 belongs to the `simple` 2x2x1 arm), and its correction list
names "the same figure quoted forward into any successor doc."
`DEFECT_ROBUSTNESS_mesh_and_setup.md` (erratum section, lines 1002-1010) and
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md` (addendum item 1) were
corrected; the lesson was not. Secondary: `LESSONS.md:1698` "163,600x" vs the
full-precision 163,548 (display-precision only per the sweep; both round to
1.6e5). **Applied in-place below (F-1).**

### DISC-2. DAFOAM_CASE_STATUS.md:91 carries the cost figure the mechanism sweep corrected. SEVERITY: LOW (cost bookkeeping, but it is the exact L-32 satellite-lag pattern)

`DAFOAM_CASE_STATUS.md:91` — "the five deciding arms cost 12.63" — vs
`DISCRIMINATORS_A4_decomposition_mechanism.md:258` — "~~12.63~~ **12.80**
core-min (corrected 2026-08-04, per the supervisor sweep ... commit 8e0a08bc:
the 12.63 omitted d_crossres2)". The satellite kept the uncorrected figure.
**Applied in-place below (F-2).**

### DISC-3. DAFOAM_CASE_STATUS.md's "Explicitly blocked" section contradicts the same file's own B3 entry. SEVERITY: MEDIUM (internal contradiction in the family's central record)

`DAFOAM_CASE_STATUS.md:270-276` (B3 bullet of "Explicitly blocked, stated
plainly", written 2026-07-28, never amended) — "Root cause not identified
within this rung's time budget" — while the same file's line 133 (2026-08-02
amendment) names the mechanism (singular ILU sub-block factorization,
reproduced outside DAFoam entirely), and
`ladder-b/W4_ADJOINT_PC_UNBLOCK.md` (2026-08-04) records the in-solver
unblock (sub-LU: reason 2, 667 iterations, first FD-verified field-inversion
gradient). A reader of the summary section alone gets a 10-day-stale claim
with no supersession marker. **Applied in-place below (F-3).**

### DISC-4. DAFOAM_CASE_STATUS.md cross-rung finding 1 still recommends a path measured to crash by construction. SEVERITY: MEDIUM (would send a future agent to a known-dead lever)

`DAFOAM_CASE_STATUS.md:199-200` — "A genuine matrix-free path exists
(`adjUseColoring=False`) but trades memory for an unmeasured runtime cost and
was not attempted anywhere in this ladder" — contradicted by
`DISCRIMINATORS_A4_decomposition_mechanism.md` (M2: `adjUseColoring: False`
hard-crashes the v5 mphys Krylov path by construction, `DAColoring.C:1021`;
forced identity coloring is memory-unbounded — >20 GiB on a case whose colored
path uses <2) and by the usability finding in
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md`. **Applied in-place below (F-4).**

### DISC-5. DAFOAM_CASE_STATUS.md B3 entry does not carry the 2026-08-04 sub-LU unblock beside its verdict. SEVERITY: MEDIUM (R11 pattern breach: patched-toolchain repair not recorded beside the stock verdict)

`DAFOAM_CASE_STATUS.md:128-137` — B3's record ends at the 2026-08-02 mechanism
naming and 2026-07-31 notes. Under grading policy R11 the shipped-toolchain
BLOCKED verdict stands (the shipped `DALinearEqn.C` still hard-codes `PCILU`),
but R11 points 2-3 require the diagnosis-confirmed-by-repair to be recorded
BESIDE the stock verdict — exactly as done for A1/A5's IDWarp patch. The
patched-image unblock (`dafoam-subpclu:v1`, reason 2, 667 iters, FD-verified at
0.085%/0.059%/0.199%, sweep cell 6490 at 0.0211%) and its 2026-08-07
inlet-contamination correction (objective computed under an accidentally
0.72-uniform `0/U`; FD gate unaffected, loss carries a 27% inlet bulk mismatch
— `W4_ADJOINT_PC_UNBLOCK.md` §5c correction block) are both absent.
**Applied in-place below (F-5).**

### DISC-6. The committed LaTeX report is stale against three 2026-08-07 corrections its own source documents now carry. SEVERITY: MEDIUM-HIGH if it ships; expected churn if the concurrent update lands them. NOT APPLIED (another agent owns the file); named for that agent:

1. `dafoam_defect_report.tex:548-572` (reach addendum) frames N9/`inletOutlet`
   as landing "in the clean class" with no operator-level caveat. The
   robustness campaign (R5b) measured that configuration's operator still
   wrong at 1.047x||b|| (163,548x its np=1 floor) under a 0.019% gradient —
   and `UPSTREAM_BUG_REPORT_decomposition_adjoint.md` addendum item 2 now
   mandates "any filed version must not describe inletOutlet-family
   configurations as unaffected: they are affected and silent." The citable
   companion currently says the thing the report of record forbids.
2. The tex's trigger-claim framing predates the limiter-branch findings
   entirely: R6 (the limiter gates the defect; one-word `limited`->`default`
   lever, 8.95%->0.849%, KSP 719->41), R7 (the conjunction does NOT acquire on
   a second mesh family; n=1-family confound stands), and R7f/L-38 (the
   limiter's SERIAL tape is wrong at 92.8% on A1 — the first
   decomposition-independent member of the branch class). Its lessons list
   stops at L-35; L-36..L-38 are the doctrine-level products of this arc.
3. `dafoam_defect_report.tex` §5 (conditioning) presents the CBFS objective
   1.5279278906359758e-02 and the beta gradient with no note of the
   2026-08-07 inlet-contamination correction (`W4_ADJOINT_PC_UNBLOCK.md` §5c:
   gate unaffected, loss mis-posed by a 27% inlet bulk mismatch).
   Also minor, internal: the "What is still open" item 3 and the artifact
   index still say the reach matrix is unscored; the tex's own 2026-08-05
   addendum supersedes them but the entries carry no strike marker (L-32
   style says mark in place).

### Checked and found consistent (so the next reader need not re-fight them)

- The "three vs six 27-component A5 groups" apparent conflict
  (`DAFOAM_CASE_STATUS.md:90` vs `dafoam_defect_report.tex:513`) resolves:
  the case status quotes the three published Upper groups, the sweep
  (`VERIFICATION_A4_decomposition_supervisor_sweep.md:159-164`) re-extracted
  all six including the three unpublished Lower groups (worst 3.8e-04). Both
  true; PROOF.md §25.5's over-broad "any group" sentence was already scoped
  per W-1.
- `ladder-a/A4_ahmed_body.{md,json}` — the L-32 staleness is FIXED (D-1
  reconciliation applied; `verdict_of_record` present, old wording struck in
  place). L-32's "it still is not" refers to the pre-fix state.
- A4's graded configuration (np=1 stock 1.10%) vs the 0.34%/0.76% siblings:
  consistently labeled everywhere (W-3 resolution carried into the case
  status, the tex table, and the robustness "on record" section).
- The R5/R6/R7 numbers quoted forward into the upstream report's addenda
  match the robustness record and its sweep to every digit checked
  (24,300x collapse, 1.047x, 0.849%, 2.82%, 92.8%, 0.121%).
- The sign-convention provenance (offline `res + 2b`) is stated identically
  in DISCRIMINATORS, the robustness R5 amendment, and the tex §sign-conv.
  (The instrument itself is another matter — Part 2, A-1.)

---

## Part 2 — personal check pass: line-by-line review of the two highest-risk code artifacts

Chosen per the charter: (A) the cross-residual instrument
(`/home/ubuntu/certonomous-runs/W4-a4-discriminators/runScript_w4.py`,
`build_maps.py`, `run_arm.sh`) — reused, re-pathed, by three campaigns
(discriminators, reach, robustness/R5/R7x) and named in both the upstream
report's reproduction protocol and the tex appendix; and (B) the sub-LU patch
and its env-switch plumbing
(`demo-output/website/dafoam/subpclu_patch/DALinearEqn_subpclu.patch`).
These reviews look for what number-reproduction sweeps cannot see: unit
assumptions, silent fallbacks, and reuse traps. **Nothing below is fixed;
every item is filed here first. Items marked [fix-forward] are safe to apply
without invalidating any recorded number (they change future runs only).**

### Artifact A — the cross-residual instrument

**A-1. SEVERITY HIGH (standing, already bit once): the sign convention is
still wrong in the reused tasks.** `runScript_w4.py:202` (`w4_dump`) and
`:293` (`w4_crossres`) compute `res = Atpsi - b` for a system that is
`A^T psi = -b`; only `w4_crossres2` (`:331`, `res = Atpsi + b`) is correct.
Consequences already on the record: every own-operator log line prints the
degenerate `ratio=2.000000e+00`, the published cross-residuals exist only as
offline `res + 2b` corrections, and one provenance erratum
(`DISCRIMINATORS...md:89-95`) was spent on exactly this. The trap that
remains: `w4x_res_*.npy` (needs `+2b`) and `w4x2_res_*.npy` (true residual)
are same-family filenames carrying DIFFERENT conventions, with nothing in
file or log line saying which — and the instrument has since been reused
unmodified by R5 and staged for R7x. The tex's own instruction ("fix the
convention in the instrument rather than offline") has not been executed.
[fix-forward: change the two sites to `Atpsi + b`, print the convention in
every W4X/W4D line, and bump the output prefix so old and new dumps cannot be
conflated. Do not re-derive any published number from post-fix outputs
without noting the convention change.]

> **OUTCOME 2026-08-07: FIXED** (fix agent; runs-tree files, not in git;
> repo-side record in commit 9796f90f's sibling, this file). Both sites in
> `runScript_w4.py` now compute `res = Atpsi + b`; every W4D/crossres log
> line prints an explicit convention banner ("residual convention:
> r = Atpsi + b for the system A^T psi = -b"); the sign-fixed `w4_crossres`
> writes `w4xf_res_*.npy` and logs as **W4XF**, so pre-fix `w4x_res_*.npy`
> (needs +2b) can never be conflated with true residuals
> (`w4x2_res_*.npy` always was the true residual). A future-runs-only header
> states that all historical numbers stand (corrected offline, documented).
> The sibling source copy `W4-a4-du0check/runScript_du0.py` carried the same
> defect and got the same fix. `run_arm.sh`'s tail grep extended to W4XF.
> No script copies exist under the repo tree (grep `w4_crossres`: markdown
> references only); `run_r5_dump.sh` and `run_a35_dump.sh` copy the now-fixed
> canonical directly, so R5/R7x reuse inherits the fix. In-arm historical
> `runScript.py` copies were left untouched as evidence of what ran.
> **Control reproduction on the existing d_np1 dump, no offline correction:**
> old convention ||Atpsi-b||/||b|| = 2.000000e+00 (degenerate); new
> convention ||Atpsi+b||/||b|| = **1.140697e-04** (~floor), equal to every
> digit with the documented offline `res + 2b` correction of the published
> `w4x_res_np1.npy`.

**A-2. SEVERITY MEDIUM: map validation is advisory, not enforced.**
`build_maps.py:99-115` prints the duplicated-phi copy agreement and mapped
primal-state agreement but asserts on neither; a failed validation still
writes `psi_on_np1.npy` and downstream tasks will consume it. The published
runs pass (2.7e-15), but a reuse with a subtly wrong map would emit its
warning into a log nobody greps and keep going. [fix-forward: hard-fail when
`d_copies.max()` exceeds a registered tolerance (the family floor is machine
precision; anything above ~1e-12 x scale is a wrong map), and non-zero exit.]

> **OUTCOME 2026-08-07: FIXED** (fix agent; `build_maps.py`, runs tree).
> Every validation is now a GATE: duplicate-copy disagreement above
> 1e-12 x max|w| (env `W4_MAPTOL_DUPSCALE`) or mapped primal-state relative
> error above 1e-2 (env `W4_MAPTOL_REL`) writes NO `psi_on_np1.npy` /
> `map_np4_to_np1.npz` for the arm and exits 1, and any pre-existing
> `psi_on_np1.npy` is removed up front so a failed run cannot leave a stale
> valid-looking file. Calibration note recorded in the script: this file's
> line above conflated two floors -- 2.7e-15 is the DUPLICATE-COPY agreement
> (machine precision, gated at 1e-12 x scale as prescribed); the mapped
> primal-state agreement on the published dumps is 2.0e-3/2.8e-3
> (independent reconvergence at primalMinResTol 1e-4), so that gate defaults
> to 1e-2 (a wrong map leaves O(1)). Tested on the published dumps:
> positive run passes all gates, exit 0, regenerated `psi_on_np1.npy`
> byte-identical to the published files for all three arms; negative run
> (`W4_MAPTOL_DUPSCALE=1e-30`) exits 1 and refuses to write psi.

**A-3. SEVERITY MEDIUM: hardcoded absolute paths with no case-identity
assertion.** `build_maps.py:24` (`BASE = .../W4-a4-discriminators`),
`run_arm.sh:10-11` (`BASE`, `SRC`). Every campaign reuse requires hand-editing
a constant ("re-pathed only" copies: `build_maps_a35.py`, `build_maps_upw.py`,
`build_maps_io.py`, `build_maps_a1lim.py`). The dangerous failure is the
forgotten edit: the stale path EXISTS and holds a self-consistent prior
campaign's dumps, so the script would produce fully "validated" numbers with
wrong provenance — the internal gates validate the map against its own dumps,
not the dumps against the intended arm. [fix-forward: take BASE/arm from
argv; assert identity by comparing the dumps' `w4_meta_rank0.json` CD0
against the arm log being analyzed.]

> **OUTCOME 2026-08-07: PARTIALLY FIXED / PARTIALLY DEFERRED** (fix agent).
> FIXED: case-identity assertions land in both directions. `w4_dump` now
> records `globalAdjSize`, `globalStatesNorm`, and the residual convention in
> `w4_meta_rank*.json` (post-fix dumps only), and `build_maps.py` asserts at
> load: per-rank size sums vs ownership range, np1 meta size vs the parsed
> indexing, arm-vs-np1 CD0 agreement within 1e-4 (env `W4_IDTOL_CD0`;
> measured reconvergence spread ~7e-6, so a stale prior-campaign path with a
> different case fails loudly), and the new meta fields when present. All
> identity checks are gates (nonzero exit, no psi written). DEFERRED: BASE
> is still a hand-edited constant (argv migration not taken in this pass);
> the re-pathed derivative copies `build_maps_{a35,upw,io,a1lim}.py` remain
> pre-fix and should be re-derived from the fixed canonical before any
> reuse.

**A-4. SEVERITY MEDIUM (already bit once, still unfixed): the driver
truncates evidence logs on re-run.** `run_arm.sh:46` writes
`> "$BASE/${TAG}.log"` per attempt; three nocolor attempts shared a TAG and
destroyed the cited crash log (the mechanism sweep's citation erratum,
`DISCRIMINATORS...md:163-172`). The truncation is still in the script.
[fix-forward: append an attempt-stamped log name, or refuse to run if
`${TAG}.log` exists.]

> **OUTCOME 2026-08-07: FIXED** (fix agent; `run_arm.sh`). Any existing
> `${TAG}.log` is rotated to `${TAG}.log.prev.<UTC-stamp>` before the run;
> `${TAG}.log` always holds the latest attempt, and no re-run can destroy a
> prior attempt's evidence. `bash -n` clean.

**A-5. SEVERITY MEDIUM (latent footgun): empty-TAG deletes the campaign.**
`run_arm.sh:12-14`: `TAG="$1"; D="$BASE/$TAG"; sudo rm -rf "$D"`. `set -u`
catches a MISSING argument but not an EMPTY one: `run_arm.sh "" 4 ...` makes
`D="$BASE/"` and `sudo rm -rf` removes the whole discriminators directory —
dumps, ledger, and all. [fix-forward: `[ -n "$TAG" ]` and reject TAG
containing `/` or `.`.]

> **OUTCOME 2026-08-07: FIXED** (fix agent; `run_arm.sh`). A `case` guard
> before any `rm` rejects empty TAG, TAG containing `/` or a space, and the
> `.`/`..` dot dirs, exit 2. Unit-tested: `""` and `"../evil"` refused,
> a normal tag proceeds.

**A-6. SEVERITY LOW-MEDIUM: objective name "CD" hardcoded in the b
evaluation.** `runScript_w4.py:197,281,321` pass the literal `"CD"` to
`calcJacTVecProduct(... "CD", "function", ...)`. Reuse on a case whose
function key differs (A5's `OBJ`, CBFS's `varianceU`) requires an edit; it is
not established whether a wrong name fails loudly or returns a zero vector —
a zero b would silently zero every ratio's denominator reference. Any graft
(as R7x plans) must verify `||b||` in-log against the case's own scale.

> **OUTCOME 2026-08-07: DEFERRED** (not in this fix pass's reproducibility
> scope; the in-log ||b|| line already prints for any graft to check).

**A-7. SEVERITY LOW: the capture hook takes the LAST reverse seed.**
`runScript_w4.py:22-30,236` (`_captures[-1]`). Correct for this model (one
objective, one warper call); on a model with multiple functions or
constraints the captured `dCD/dXv` could silently belong to a different
function. Fine as used; a reuse hazard to keep in mind for any multi-function
graft.

> **OUTCOME 2026-08-07: DEFERRED** (correct as used; hazard documented here).

**A-8. SEVERITY LOW: crossres tasks glob `psi_on_np1_*.npy` from the staging
dir.** `runScript_w4.py:286,324`. Stale psi files from a previous lever staged
in the same dir are silently included. Mitigated because tags name their arm;
worth a staging-dir hygiene line in the driver.

> **OUTCOME 2026-08-07: DEFERRED** (mitigation by arm-named tags stands; note
> that post-fix crossres runs also self-identify by the W4XF banner).

### Artifact B — the sub-LU patch and its env-switch plumbing

The one-hunk logic itself is sound: default path provably unchanged
(`localPCType` only moves when the env var matches; the env-off regression
reproduced the `-9` with all 13 residual digits, re-verified cold by the
conditioning sweep), the Info line gives an in-log witness, and OpenFOAM's
`Info` masters-only print is the right channel.

**B-1. SEVERITY MEDIUM: silent fallback on unrecognized values.**
`strcmp(subPCTypeEnv, "lu")` — exact match only. `DAFOAM_SUBPC_TYPE=LU`,
`Lu`, `lu ` (trailing space from a shell export), or a hopeful `superlu` all
silently run stock ILU with no message. A run believed patched can be stock,
and on a case where ILU happens to converge there is no loud tell. Mitigation
already in family practice: grep the `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC
set to complete LU` line in-log (the W4 record does). [fix-forward: warn on
any set-but-unrecognized value; make drivers assert the Info line before
trusting any sub-LU result — now codified in the guidelines.]

> **OUTCOME 2026-08-07: FIXED IN PATCH TEXT, REBUILD DEFERRED** (fix agent;
> commit 9796f90f). The regenerated `DALinearEqn_subpclu.patch` warns via an
> Info line on any set-but-unrecognized non-empty `DAFOAM_SUBPC_TYPE` value
> (behavior stays stock ILU; no numeric path touched). The deployed
> `dafoam-subpclu:v1` image is NOT rebuilt: the warn is recorded in the patch
> file's header as the next-rebuild delta, and drivers must keep asserting
> the sub-LU Info line per the guidelines until that rebuild lands.

**B-2. SEVERITY LOW-MEDIUM: the committed diff is not mechanically
applicable.** The patch headers are absolute paths into a session-ephemeral
scratchpad (`/tmp/claude-1000/.../scratchpad/src/DALinearEqn.C`) rather than
`a/src/adjoint/DALinearEqn/DALinearEqn.C` form. `git apply` fails on it
outright; reuse needs a hand-driven `patch` with an explicit target, and the
referenced tree no longer exists. The tex cites this file as the reproduction
diff. [fix-forward: regenerate the diff with repo-relative a/ b/ headers;
content unchanged.]

> **OUTCOME 2026-08-07: FIXED** (fix agent; commit 9796f90f). Regenerated
> against the stock `DALinearEqn.C` extracted from
> `dafoam/opt-packages:latest` with `a/src/adjoint/DALinearEqn/DALinearEqn.C`
> headers; `git apply --check` PASSES from the DAFoam repo root (expected
> working directory documented in the patch header: the directory containing
> `src/`, in-container `/home/dafoamuser/dafoam/repos/dafoam`). Content
> verified: the 19-line applied block is byte-identical to the modified file
> extracted from the deployed `dafoam-subpclu:v1` container (stock + block
> reproduces that file exactly); the only addition beyond it is the B-1 warn,
> declared in the header as not-yet-built.

**B-3. SEVERITY INFO: per-block getenv.** The check runs inside the sub-block
loop (guarded print at `i == 0`); repeated getenv is constant and harmless.
No unit assumptions; no numeric path touched when off. No further findings.

> **OUTCOME 2026-08-07: NO ACTION** (info only; unchanged in the regenerated
> patch).

---

## Part 3 — corrections applied after recording (smallest surgical set; everything else is named for its owner)

- **F-1** `LESSONS.md` L-37: 590 -> 719 with a dated parenthetical citing the
  sweep; 163,600 annotated to 163,548 full precision.
- **F-2** `DAFOAM_CASE_STATUS.md:91`: 12.63 -> 12.80, same strike-and-note
  style the DISCRIMINATORS erratum uses.
- **F-3** `DAFOAM_CASE_STATUS.md` "Explicitly blocked" B3 bullet: dated
  supersession note pointing at line 133's mechanism and the W4 unblock;
  shipped-toolchain BLOCKED verdict unchanged per R11.
- **F-4** `DAFOAM_CASE_STATUS.md` cross-rung finding 1: dated correction note
  on the `adjUseColoring=False` sentence (crashes by construction;
  memory-unbounded when forced).
- **F-5** `DAFOAM_CASE_STATUS.md` B3 entry: one dated bullet recording the
  sub-LU unblock beside the verdict, R11-style, including the 2026-08-07
  inlet-contamination correction.

NOT applied, named for owners: DISC-6 (the tex — concurrent updater);
Part 2's [fix-forward] items (instrument owners; each is a future-runs-only
change and none invalidates a recorded number — but A-1 and A-4 should be
executed before the R7x contingent or any new cross-residual arm runs).

## Escalations to the chief supervisor

1. **A-1** (sign convention still live in a reused instrument) is
  upstream-filing-relevant: the reproduction protocol in the unfiled report
  and the tex tells a maintainer to run an instrument whose logs print
  degenerate ratios. Recommend the fix-forward lands before any filing
  decision reaches Katie. *(2026-08-07 later: landed — see the A-1 outcome
  block; the instrument now prints the correct convention with an explicit
  banner, and the np1 control reproduces the corrected floor with no offline
  step.)*
2. **DISC-6** must land in the tex before it is treated as citable; item 1
  of it (inletOutlet framed as clean) is a safety-relevant contradiction of
  the report of record.
3. No scoring-grade claim was found wrong; no headline number moved. The
  discrepancies are currency and bookkeeping, all in the direction the
  sweeps' own errata already pointed.
