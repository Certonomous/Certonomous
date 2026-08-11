# Archive note — the `controlDict`s in this tree do not restate the pre-registered caps

Added 2026-08-11 by an audit of the W2 SpaRTA archive. **No graded number in
`W2_SPARTA_FROZEN_CBFS.md` or `W2_SPARTA_REGRESSION.md` is affected by anything on this
page.** This note exists because a future reader who tries to reconstruct the campaign
protocol from the archived case dictionaries alone will get the iteration caps wrong in
six of the twenty-one cases, and in two different directions.

## The rule this note exists to obey

**The `controlDict` files in this tree have not been edited and must not be.** They are
the dictionaries the completed, cited solves actually read. Editing them to agree with the
pre-registration would be tidying that destroys the thing the archive is for: the archive
would stop matching the runs it documents, and the record of what was actually executed
would be replaced by a record of what was planned. The correction therefore lives here and
in the results documents' prose, never in the artifact.

## What was declared, and where

| Declaration | Source |
| --- | --- |
| Frozen solve: settle, not cap; **backstop cap 5,000 iterations**, hitting it is reported as NOT CONVERGED | `W2_SPARTA_PREREGISTRATION.md`, "Convergence criteria, declared now" |
| Static-field propagation: checkpoints 5,000 (CBFS) / 2,500 (PH); **cap 30,000 (CBFS) / 10,000 (PH)** iterations beyond restart | same |
| E1 / **E2 sign experiments: 500-iteration** propagation mini-runs | `W2_SPARTA_PREREGISTRATION.md`, "Sign-convention experiments" |
| Model-driven propagations: checkpoints 5,000 / 2,500, **caps 30,000 (CBFS) / 10,000 (PH)** | `W2_SPARTA_REGRESSION_PREREGISTRATION.md` §"Propagations" |
| **E3 sign falsifier: a 500-iteration** CBFS mini-run | `W2_SPARTA_REGRESSION_PREREGISTRATION.md` §"E3" |

## All 21 cases, checked — not a sample

Every directory in `W2_sparta_runs/` that carries a `system/controlDict` is listed. (The
twenty-second entry, `regression/`, holds only the four discovery JSONs and has no case
dictionary.) "Log stop" is read from the case's own `log.run` / `log.frozen` / `log.post`.

| # | Case | Role | Declared limit | Archived `endTime` | Log stop | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `cbfs_frozen` | frozen solve | backstop 5,000 | `5000` | settle at 295 + 59 verification = 354, `End` | **matches** |
| 2 | `ph_frozen` | frozen solve | backstop 5,000 | `5000` | settle at 1,243 + 249 verification = 1,492, `End` | **matches** |
| 3 | `cbfs_ic1` | IC1 zero-iteration exactness check | none (no time loop) | `0` | `Starting time loop` → `End`, no iterations | n/a |
| 4 | `cbfs_baseline_post` | `-postProcess` tau extraction on the shipped baseline | none (no time loop) | `30000` | `-time 30000`, `End` | n/a — `endTime` is the shipped solution's own time |
| 5 | `ph_baseline_post` | `-postProcess` tau extraction on the shipped baseline | none (no time loop) | `10000` | `-time 10000`, `End` | n/a — same |
| 6 | `cbfs_e2_plus` | E2 correct-sign mini-run | 500 | `500` | `End` after Time 500 | **matches** |
| 7 | `cbfs_e2_signR` | E2 `RScale -1` | 500 | `500` | `End` after Time 500 | **matches** |
| 8 | `cbfs_e2_signB` | E2 `bScale -1` | 500 | `500` | `End` after Time 500 | **matches** |
| 9 | `cbfs_e3_plus` | E3 discovered-model mini-run | 500 | `500` | `End` after Time 500 | **matches** |
| 10 | `cbfs_e3_minus` | E3 sign-flipped mini-run | 500 | `500` | `End` after Time 500 | **matches** |
| 11 | **`cbfs_prop`** | static-field propagation, CBFS | **30,000** | **`20000`** | 3 clean segments (`End` after 5,000 / 10,000 / 15,000) + a 4th launched at 15,001 and **killed mid-Time 15,519, no `End`** | **MISMATCH — understates the cap by 10,000** |
| 12 | **`ph_prop`** | static-field propagation, PH | **10,000** | **`12500`** | 5 clean segments, `End` after 12,500 | **MISMATCH — overstates the cap by 2,500** |
| 13 | **`cbfs_m1pub`** | model-driven propagation, M(1) as written | **30,000** | **`15000`** | one segment, `End` after 15,000 | **MISMATCH — understates the cap by 15,000** |
| 14 | **`cbfs_m2pub`** | model-driven propagation, M(2) as written | **30,000** | **`15000`** | one segment, `End` after 15,000 | **MISMATCH — understates the cap by 15,000** |
| 15 | **`cbfs_m3pub`** | model-driven propagation, M(3) as written | **30,000** | **`15000`** | one segment, `End` after 15,000 | **MISMATCH — understates the cap by 15,000** |
| 16 | **`cbfs_mdisc`** | model-driven propagation, discovered model | **30,000** | **`15000`** | one segment, `End` after 15,000 | **MISMATCH — understates the cap by 15,000** |
| 17 | `ph_m1pub` | model-driven propagation, M(1) | 10,000 | `10000` | `End` after 10,000 | **matches** |
| 18 | `ph_m2pub` | model-driven propagation, M(2) | 10,000 | `10000` | `End` after 10,000 (this is the genuine cap-stop-unsettled reported in `W2_SPARTA_REGRESSION.md` §6) | **matches** |
| 19 | `ph_m3pub` | model-driven propagation, M(3) | 10,000 | `10000` | `End` after 10,000 | **matches** |
| 20 | `ph_mdisc_cbfs` | discovered CBFS model on PH | 10,000 | `10000` | `End` after 10,000 | **matches** |
| 21 | `ph_mdisc_ph` | discovered PH model on PH | 10,000 | `10000` | `End` after 10,000 | **matches** |

**Tally: 12 match a declared limit, 3 have no declared iteration limit (they run no time
loop), and 6 mismatch.** Five of the six understate their cap; one overstates it.

## Why they differ — one cause per direction

**Understating (cases 11, 13-16).** The CBFS propagations were driven in manual
5,000-iteration segments so that a checkpoint could be scored between them. `endTime` was
raised segment by segment and the archived file is simply whichever value was in place
when the last segment was launched — `20000` for `cbfs_prop` (the fourth segment's
setting), `15000` for the four model-driven runs (which needed only one segment, launched
straight to the protocol's confirmation point after `cbfs_prop` had already established
that settle fires at 10,000 and confirms at 15,000). In every one of these five cases the
30,000 cap was **never approached**, so it never bound and no grade depends on it. The
archived `endTime` is a record of the last launch, not a record of the declared cap.

**Overstating (case 12).** `ph_prop` is the opposite: `endTime 12500` is *above* the
declared 10,000 cap because the settle rule fired between 7,500 and 10,000 and its
confirming checkpoint would have landed beyond the cap. One extra 2,500-iteration segment
was therefore run deliberately past the cap, purely as confirmation, and was labelled that
way at the time — `ph_prop/score_12500.json` carries the literal label
`"ph_prop @12500 (confirmation beyond cap)"`, and `W2_SPARTA_FROZEN_CBFS.md` §5 reports it
in the checkpoint table as *"12,500 (confirmation, deliberately beyond the pre-registered
cap)"*. **The graded PH value is checkpoint 10,000, the in-cap settled value.** The
archived `endTime` records the confirmation segment, not the graded run.

## How to reconstruct the protocol correctly

Take the caps from the two pre-registrations, not from the archived dictionaries. To
re-run a propagation as declared, set `endTime` to the declared cap (30,000 CBFS / 10,000
PH) with `writeControl timeStep` and `writeInterval` 5,000 (CBFS) / 2,500 (PH), and apply
the settle rule to the written checkpoints — that reproduces the *protocol*. It will not
reproduce the *segmenting*, which was manual and is visible only in the segment structure
of each `log.run`. Both are on the record; only one of them was ever declared.

## Related correction on the same tree

`W2_SPARTA_FROZEN_CBFS.md` §5 formerly described `cbfs_prop` as *"stopped at 15,000 by the
pre-registered protocol, not by a cap"*. The protocol's stop and the grade were indeed at
15,000, but a fourth continuation segment was launched and killed at ~15,519. That prose
was corrected on 2026-08-11; no reported number moved, because the fourth segment read the
`15000/` checkpoint and — with `writeInterval 5000` and its next write due at 20,000 —
never wrote anything. See the dated correction block in that document for the full
timestamp evidence.
