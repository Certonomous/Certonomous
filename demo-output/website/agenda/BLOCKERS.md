# Blocked items — consolidated waiting-on-Sanaa list

Single source of truth for work that cannot proceed on this box. Everything
here has been **verified blocked**, not assumed. Nothing else in the night queue
waits on an answer; each entry names the exact unblock action.

Kept as a separate file on purpose: `agenda.save_docket()` rewrites
`docket.json`'s proposal list wholesale, so a blocker parked as a top-level key
there would be silently destroyed by the next `refresh_docket()`.

Last updated: 2026-08-01 06:3x UTC.

---

## B-1. Billing alarm and spend cap cannot be confirmed from this instance

**Ops gate item 1. BLOCKED — verification, not assumption.**

| Check | Result |
| --- | --- |
| IAM instance role | **None.** `/latest/meta-data/iam/security-credentials/` returns 404 |
| `~/.aws` | Does not exist |
| `AWS_*` environment variables | None set |
| `aws` CLI | Not installed |

With no credentials and no role, this box cannot call CloudWatch or Billing,
so **I cannot report the configured alarm threshold or spend cap.** Installing
the CLI would not help; the credentials are the missing piece, not the tool.

**I am explicitly NOT reporting a number here.** Stating an unverified spend cap
would be exactly the kind of fabricated measurement the house rules forbid.

**Unblock:** attach an instance role with `cloudwatch:DescribeAlarms` and
`ce:GetCostAndUsage` (read-only is sufficient), or paste the configured numbers
directly and they will be recorded as reported-by-owner rather than measured.

---

## B-2. Ledger cannot be synced off-host

**Ops gate item 3. BLOCKED both paths.**

| Path | Status |
| --- | --- |
| S3 | No credentials, no role, no CLI — same as B-1 |
| Private GitHub remote | `origin` **is** configured (`https://github.com/Certonomous/Certonomous.git`) but there is no usable credential: `~/.ssh` holds only `authorized_keys` (no private key), and `ssh -T git@github.com` returns `Permission denied (publickey)`. No HTTPS token or credential helper is configured. |

**Current state and the honest risk.** A verified local backup exists at
`/home/ubuntu/backups/ledger_20260727_235551.jsonl` (89,964,387 bytes, MD5
`7b2e586edb384528b44f3df81ae2651e`, 192,409 lines). **It is on the same disk as
the ledger it backs up.** That protects against corruption, a bad
de-duplication, and accidental deletion. It does **not** protect against losing
the instance — which is precisely what happened on 2026-07-27. The disk
surviving that outage was luck, not design.

The single-instance lock stays in force (`acquire_runner_lock`, commit
`f198cf4`), which is the other half of ledger integrity and is **not** blocked.

**Unblock:** either an instance role with `s3:PutObject` on a backup bucket, or
a deploy key / PAT for the private repo. The moment either exists, the hourly
sync goes in — the backup script and rotation already work.

---

## B-3. TMR NACA 0012 closure run — approval ambiguity, NOT a technical block

Ladder C4 schedules the ~480 core-minute TMR closure run "within cap". Two
things are unresolved, and they are different:

1. **The cap itself is unknown** — see B-1. "Within cap" cannot be evaluated
   against a number nobody on this box can read.
2. The owner said "I am fine with the closure challenge cost" in response to a
   message that quoted **only** the TMR figure (~480 core-min / ~8 h) while also
   naming the separate closure-challenge track. The literal phrase matches the
   closure-challenge track, which needs no approval and is running.

**Handling:** the closure-challenge track (Ladder C1–C3) proceeds — it was never
gated. The 480 core-minute TMR run is scheduled per C4 but will be launched only
against a known cap or an explicit go, because launching an 8-hour compute
commitment on a misread of one ambiguous sentence is not a defensible default.

**Unblock:** confirm the spend cap (B-1), or say "yes, run the 480 core-min TMR
closure".

---

## B-4. External reachability cannot be settled from this box

**`w7-verify-reachability-from-outside`. BLOCKED on the half that matters.
Measured 2026-08-01 06:3x UTC.**

The gate asks readiness to name which surfaces are reachable from outside and
which are loopback only, **and to say how it knows**. Two different questions
hide in that sentence, and only one of them can be answered here.

**Answerable here, and now answered: the bind address.** `ss -ltnp` on this
instance:

| Port | Bind | Process |
| --- | --- | --- |
| 8080 | `0.0.0.0` | `python3 -m http.server 8080 --directory demo-output/website` (pid 1396) |
| 8765 | `0.0.0.0` | `python3 -m chief_engineer.server` (pid 2872620) |
| 22 | `0.0.0.0` and `[::]` | sshd |
| 53 | `127.0.0.53`, `127.0.0.54` | systemd-resolved |
| 35257 | `127.0.0.1` | ephemeral |

**Neither demo surface is loopback only.** That is a fact about this box and a
readiness check can assert it without leaving the instance. It is also not the
claim the shoot needed.

**Not answerable here: whether an outside client can open the socket.**

| Probe | Result |
| --- | --- |
| `http://127.0.0.1:8080/` | **200** |
| `http://172.31.43.247:8080/` (private address) | **200** |
| `http://16.58.201.228:8080/` (public address, from this box) | **000** |

The 000 is the trap, and it is worth naming precisely: **it is not evidence
that the port is closed.** An EC2 instance reaching its own elastic address
normally has no hairpin path back to itself, so 000 is the expected answer
whether the security group admits the world or blocks it. The check that looks
most like an outside test is the one check that can never distinguish the two
cases. It is a false negative by construction, in the same way the old
loopback test was a false positive by construction.

The security group is `launch-wizard-2`. Its inbound rules would settle the
question, and they cannot be read from here: there is no instance role
(`/latest/meta-data/iam/security-credentials/` returns 404), no `~/.aws`, no
`AWS_*` variables and no `aws` CLI, exactly as recorded in B-1.

**What readiness may claim today, and it should claim only this:** the bind
address of every listening socket, and a plain statement that reachability
from outside is unverified and cannot be verified from the instance.

**Unblock, cheapest first.**

1. From the operator laptop, off any Certonomous network:
   `curl -sS -o /dev/null -w '%{http_code}\n' --max-time 8 http://16.58.201.228:8080/`
   and the same for `:8765`. Two lines of output settle it permanently, and a
   200 or a 000 both go on the record with the vantage point named.
2. Or attach a read-only instance role with `ec2:DescribeSecurityGroups`, which
   turns this into a check the box can run for itself every week.

Until one of those exists, any readiness line that asserts external
reachability is asserting something nobody measured.

---

## B-5. ~~Five papers this box cannot open, and one it can~~ Four papers this box cannot open. The two it could, it has read.

**`w2-mit-access-list`, `w5-close-the-secco-2021-citation-gap`. Opened
2026-08-01. Waiting on Katie's library, not on this box.**

The full list, with what each item unblocks and the one section needed, is
`demo-output/website/agenda/LIBRARY_ACCESS_LIST.md`. It is ordered by
consequence and it is short enough to work in one sitting.

The first entry is the only one that can overturn something already published:
**Secco, Kenway, He, Mader and Martins, AIAA J. 59(4) 1151 to 1168, 2021, doi
10.2514/1.J059491**, which returned 403 on every URL tried and has no
open-access copy. The lab's root-cause document states that nothing qualifies
`warpDeriv` as approximate, and an undocumented defect and a documented
approximation are different things to report upstream. One paragraph of that
paper either upholds the claim or withdraws it.

**Re-attempted 2026-08-02 and the block is confirmed, not merely restated.**
Five umich URLs now, including the PDF link the authors' own MDO Lab
bibliography page offers, which returns 403 and redirects to a 404 page.
OpenAlex returns `oa_status: closed` and `any_repository_has_fulltext: false`
on the DOI; Semantic Scholar returns an empty `openAccessPdf.url`. Two
independent indexes say no open copy exists. **This one is genuinely Katie's
library or nothing,** and no further unpaid route is worth spending on it.

~~Item 6 on the list needs no library at all and is the one to do first anyway:
the closure challenge preprint, arXiv `2603.28884`.~~ **DONE 2026-08-02.** It
did need no library. Retrieved from `arxiv.org/html/2603.28884v1` at 05:14 UTC,
HTTP 200, read end to end, and **the quotation is upheld verbatim** — Section
2.1, *Test cases*. The submission draft no longer contains an unverified
quotation. Full audit of all 30 of its quotations:
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §9, which found and fixed two further
defects, both in citations of the lab's own surfaces rather than of the
benchmark's rules.

**Item 4 also needed no library and is also done.** Buchanan, Lăcătuş, West and
Dwight 2025 is on arXiv at `2504.06758`; the entry itself said to try that
before spending library access, and nobody had. Read end to end 2026-08-02. The
prior-art record had been citing the nearest published relative of the lab's own
decline gate **from its abstract**; it now quotes the methodology section, and
all three distinctions the lab claims survive on read wording. It also turned up
that the paper **trains on the NASA wall-mounted hump**, a scored test case of
the challenge, which puts its published coefficients off limits to our entry.

**Item 2, Pope 1975, was "not yet attempted from this box". Now attempted, and
closed** — OpenAlex reports `oa_status: "closed"` on doi
`10.1017/S0022112075003382`, with the JFM landing page as its only location.
**And moot within the hour:** W2 found a scan already sitting untracked in
`docs/papers/` and read it (commit `e7300baf`). The availability check and the
reading reached the same row from opposite directions and agree with each other.
The row is closed; it spawned two new ones, Spencer & Rivlin, both closed on
Unpaywall and neither blocking anything approved.

**Unblock:** open the list, work the four remaining entries top down, and paste
back the section named beside each. The list is shorter and every entry left on
it now carries a DOI plus the evidence that the free route was tried and failed.
Nothing else in the reading program waits on this.

---

## B-6. `closure-duct-field-inversion` is blocked on this box, and restating its cost does not change that

**Docket rank 178 of 180, `est_core_min` 420.0, approved 2026-07-31. Recorded
2026-08-01 while working the "these four are affordable" batch.**

The item was one of four ruled unaffordable by a forecast that used a mean over
a bursty series. The forecast was wrong and the item is cheap, but **cheap is
not the binding constraint here and the docket record does not say so.**

Its rationale states that the method "runs on the adjoint stack already verified
this session against the official airfoil tutorial." **The lab has already
tested that and it is false on the case this item needs.** Ladder B3 stood the
DAFoam primal up on CBFS successfully — it matches the independently-run
plain-OpenFOAM baseline to 0.087% (U), 0.23% (p), 1.41% (k), 1.20% (omega)
scaled MAE — and then the discrete-adjoint GMRES solve **diverged with PETSc
`KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at iteration 0**, reproduced
identically across two primal convergence levels (1e-4, 1e-6), two objective
types (a custom field-variance loss and a force objective known to work in this
lab's NACA0012 case), and two ILU preconditioner fill levels (1 and 4). Primary
evidence: `dafoam/ladder-b/B3_duct_field_inversion.md`, `B3_supervisor_debug.md`,
`campaign/NOT_PASSING_REGISTER.md:374-379`, case directories
`dafoam/ladder-b/B3_work/{CBFS,fixA_kbounds,fixB_SA,fixC_empty}`.

Two consequences the docket entry should carry and does not:

1. **The 420 core-minute estimate is unsupported, in both directions.** Its own
   `cost_basis` says it is "flagged as needing a timed pilot before it is
   trusted." The pilot ran. It measured the primal cost and the adjoint's fixed
   setup cost (colouring, Jacobian partials) and **could not measure the GMRES
   iteration cost — the dominant, scaling-critical unknown — because no run
   completed a single GMRES iteration.** So the number that was ranked on is not
   a measurement of this item.
2. **This is not the same defect as W5's.** The B3 design variable is the inlet
   `patchVelocity`; that adjoint does no mesh warping at all
   (`B3_supervisor_debug.md:101-103`). The `getRotationMatrix3d` patch does not
   touch it, and nobody should expect the W5 repair to unblock this.

**Unblock:** root-cause the CBFS adjoint's iteration-0 NaN/Inf. Until then the
item cannot spend its budget no matter how affordable the budget is. It is left
`approved` rather than dismissed because the objective — 62.9% of the deficit to
the rank-two entry sits in the two duct cases — is unchanged and worth doing the
moment the adjoint runs.

---

## B-7. The A2 wing's published gradient verification cannot be re-run from anything on this box

**Found 2026-08-01 while working `w5-regrade-every-published-gradient-claim`.
This blocks the regrade of the lab's most prominently published gradient claim.**

`benchmarks.html:115` states *"Every gradient below was verified against finite
differences before any optimisation result was allowed to stand"* over six
VERIFIED rows, and `:141` that this is *"why the 28.3% drag reduction that
followed is trustworthy rather than merely large."* **That verification ran once
and cannot currently be repeated.**

| A2 primal, nominally the same case | CD | CL |
| --- | --- | --- |
| published `run_model` (`ladder-a/A2_mach_tutorial_wing.md:23`) | 0.02772949388 | 0.4775877833 |
| the preserved case `/home/ubuntu/certonomous-runs/A2-mach-wing` | 0.03142017502 | 0.4967099218 |
| after re-running its own `preProcessing.sh` | 0.02964132667 | 0.4999507339 |
| two further copies of that, both identical | 0.03162405532 | 0.5216398962 |

**14% spread in CD**, and CL climbing monotonically as copies chain — consistent
with the angle-of-attack state in `0/U` being re-written by each run rather than
reset, so each copy inherits the last one's trim. The 47-iteration IPOPT
optimisation also ran in that directory (`OptView.hst`, `opt_IPOPT.txt`,
`opt_run_driver.log` are all still in it) and left the mesh deformed; a patched
`check_totals` launched against it died at **perturbation 132 of 211** with
`AnalysisError: ... Mesh quality error!` after **59.6 min at 4 ranks = 238
core-minutes** (`W5-regrade/a2_patched_checktotals.log`).

For contrast, A1's regrade the same afternoon reproduced its
`Minimal residual 9.646409714038222e-09` and every printed digit of its
derivative table. This is specific to A2's preserved state, not a general
property of the stack.

**Unblock:** restore A2 to the state its published `run_model` describes — a
pristine `0/` at the tutorial's default angle of attack plus a freshly generated
mesh — and confirm it by reproducing **CD 0.02772949388 / CL 0.4775877833**
before any gradient is computed. That check is ~2 core-minutes; the
`check_totals` that follows is ~210 core-minutes at 4 ranks (measured, published
run). Until the baseline reproduces, no number computed on that case regrades
anything.
