# CURRICULUM D12 (proper) — INSTRUMENT STATE, AND WHY THIS ITEM IS NOT ARMED

Dated **2026-08-25**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Lane→supervisor messaging is one-way; this committed file is this lane's channel upward.**
**Nothing here was filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

---

## 0. HEADLINE

# D12-proper is `PENDING`. **IT DID NOT RUN, AND IT COULD NOT HAVE.**

**COMPUTE SPENT ON D12-PROPER BY THIS LANE: 0.000 core-min. No container was started.**

I was dispatched to commit `PREREGISTRATION.md`, `d12r_grade.py` and `d12r_run_script.py` —
recovered from a lane killed by a session limit at ~20:45Z — and then fire the item. **I did
not commit the pre-registration as a frozen, armed document, and I did not fire.** The reason
is a fact I verified rather than inferred:

> **The pre-registration names FOUR instruments in its §4. TWO OF THEM DO NOT EXIST**, were
> never committed to any branch, and are nowhere on this filesystem. **One of the two is the
> launcher.** There is nothing to run.

Committing that pre-registration as `v1.0 FROZEN` would **close its gates** (`CLAUDE.md` rule 2)
against an instrument set that is half absent. It would also make the supervisor's own
non-delegable §3 check — *pre-registration committed before compute* — **certify a document
rather than an armed item**, which is the one thing that check exists to prevent.

**The three recovered files ARE committed by this lane, labelled exactly as what they are:
RECOVERED, REPAIRED, AND NOT ARMED.** An uncommitted finding is an invisible finding, and the
killed lane's 74,572 bytes of good work should not be lost to a session limit.

---

## 1. DEFECT A — TWO OF FOUR NAMED INSTRUMENTS DO NOT EXIST

`PREREGISTRATION.md` §4 tables four instruments:

| file | role per §4 | **on disk?** |
|---|---|---|
| `d12r_run_script.py` | the DAFoam driver | **YES** — 7,010 B, sound (§3) |
| `d12r_grade.py` | the comparator | **YES** — 39,798 B, three defects found and repaired (§2) |
| `d12r_series.py` | *"the `CD(t)` series reader and block-average engine. Reads the stage log file on disk."* | **NO** |
| `d12r_stage_and_run.sh` | *"the launcher. Asserts its own `CAP_CORE_MIN` against the value §6 names."* | **NO** |

**How I checked, so this is a measurement and not an impression:**

- `ls` of `cases/dafoam/curriculum_D12/` returns exactly three files.
- `git log --all -- '*d12r_stage_and_run*' '*d12r_series*'` returns **nothing**: they were never
  committed on any branch, so they are not recoverable from history.
- `find /home/ubuntu -name 'd12r_*'` returns **only** `d12r_grade.py` and `d12r_run_script.py`.
  They are not in a scratch tree, a worktree or a run root.
- `d12r_grade.py` contains **no reference to `d12r_series`** — it carries its own series reader
  inline. **So `d12r_series.py`'s absence is survivable.** The launcher's is not.

### WHY THE LAUNCHER IS NOT A SMALL GAP

`PREREGISTRATION.md` §3 registers a **ten-stage pipeline across two container images** — S0 mesh,
S1 the tutorial spin-up chain (`potentialFoam` → `simpleFoam` 500 iters → PIMPLE to `t = 10`),
S2 a 2,400-step diagnostic, S3 δ_repeat ×3, S4 the envelope at `n ∈ {20,40,80}` ×2, S5 the
adjoint at `W`, S6/S6b/S6c/S6d the sweeps, S7 the plant, S8 IPOPT — plus **FIELD_B** creation
with a per-file md5 manifest re-asserted before every stage, a `MemAvailable` read before every
launch, and an in-container md5 check of each instrument against its committed HEAD blob.

**And it is inherently TWO-PHASE.** G12R-4 sizes the FD sweep as `h_min = 100·δ_eff/|g_i|`,
where `δ_eff` comes from S3/S2 and `|g_i|` from **S5's adjoint**. **The steps S6 must run are not
computable until S5 has finished**, so the launcher cannot be a straight-line script; it must
stop, be graded, and resume. **The pre-registration describes that behaviour but does not specify
it**, and every clause §4 asserts about the launcher — the cap assertion, the md5 verification,
the memory floor, the manifest — is a claim about a file that does not exist.

### WHY I DID NOT SIMPLY WRITE IT — AND THIS IS A JUDGEMENT, FLAGGED AS ONE

I could have authored it. I did not, for a reason the supervisor may overrule:

**It would put the author and the auditor of a 250-core-min item in the same lane, at the same
moment, under a pre-registration written by a third lane.** I would be writing the instrument
whose behaviour §4 certifies, and simultaneously freezing the document that certifies it — so
the freeze would prove nothing about the launcher, which is exactly the evidentiary content
rule 2 says a freeze is *for*. **Every mismatch between my launcher and another lane's prose
would then be locked behind closed gates and repairable only as an addendum that cannot alter a
gate.**

**This is a judgement about who should author, not a claim that the work is hard.** If the
supervisor rules that this lane should author the launcher under this pre-registration, that is
a legitimate call and the item is a few hundred lines plus a ~250 core-min run away.
**What is NOT legitimate is firing compute against an instrument set that is half missing, and
that is the only thing I have actually refused.**

---

## 2. DEFECT B — THE COMPARATOR FAILED ITS OWN SELFTEST, AND A MUTATION TEST FOUND A THIRD GAP

**As recovered, `python3 d12r_grade.py --selftest` EXITED 1**, with **2 of 38 units failing**.
The brief's instruction was *"verify `d12r_grade.py` can FAIL… build a deliberate mutant and
confirm the units flip"*, and doing so turned up a third, worse defect.

**In all three cases the GATE LOGIC WAS RIGHT AND THE TEST WAS WRONG**, which is the better
outcome — the comparator's gates are sound; its evidence that they are sound was not.

### B1 — `U-06` (G12R-3, δ_window): the fixture's window was an exact multiple of its period

The fixture called `g3_delta_window([1,3,1,3,1,3], W=2)` and asserted `δ_window == 1.0`. The
series has **period 2** and `W = 2`, so **every** block average is exactly `2.0` and
`δ_window = 0.0`. **The grader returned 0.0 and was correct.**

**This fixture bug encodes a REAL HAZARD FOR D12 ITSELF, which is why it is worth this much
space.** `δ_window` is *identically zero* whenever the graded window `W` is an exact multiple of
the shedding period — not because the objective is noiseless, but because block averaging over
whole periods cancels the phase spread it is meant to measure. `W = 300` is registered; the
shedding period is measured by G12R-1. **If the period divides 300, `δ_eff = max(δ_repeat,
δ_window)` collapses toward zero and G12R-4's `h_min` collapses with it.**

**REPAIRED**, before first compute: `U-06` now uses `W = 3` on the same series (4 windows,
`δ_window = 2/3`), and a **new unit `U-06c`** locks the zero-spread case in as expected
behaviour so it can never be rediscovered as a bug.

### B2 — `U-09c` (G12R-6, the CONDITIONAL band): the fixture confused two statistics

The fixture built `g_fd = [1, 2, 3·1.3]` — a **30 % per-component** error — and asserted the
charter's **CONDITIONAL** band (5–15 %). But this gate's statistic is the **vector-relative
error**, which for that vector is **20.02 %**, above the 15 % FAIL threshold. **The grader
returned `FAIL` and was correct.**

**The fixture's error is precisely the confusion `DAFOAM_CHARTER.md` §2 exists to forbid** —
*"A vector norm and an average per-component error are different statistics, and quoting one
against the other is forbidden."* The clause caught its own comparator's test.

**REPAIRED:** `3.0·1.1` gives a vector aggregate of **7.526 %**, genuinely inside (5 %, 15 %],
plus an added assertion that the aggregate really lies in the band. **Until this repair the
CONDITIONAL band had never been exercised by a passing unit.**

### B3 — THE MUTATION TEST FOUND WHAT NEITHER SELFTEST FAILURE DID: the sign-flip override was untested

I ran six deliberate mutants against the repaired comparator. **Five were caught. One was not:**

> **M3 — deleting the sign-flip override from `g6_bright_line` entirely left the WHOLE selftest
> passing, exit 0, zero units failing.**

`DAFOAM_CHARTER.md` §2 makes that clause **independent of the aggregate**: *"FAIL above 15 % or
on any sign-flipped component regardless of the aggregate."* The existing unit `U-09s` uses a
vector whose aggregate is **160 %** — the aggregate alone already condemns it, so **the override
is never load-bearing in any test.** A sign-flipped component inside a vector with a small
aggregate would have passed a mutated grader silently.

**REPAIRED:** new unit `U-09s2` uses `g_adj = [10, 10, 0.01]`, `g_fd = [10, 10, −0.01]` —
aggregate **0.1414 %, comfortably inside the PASS band**, one flipped component. **Only the
override can condemn it.**

### STATE AFTER REPAIR — MEASURED, NOT ASSERTED

| check | before | **after** |
|---|---|---|
| `--selftest` exit | **1** | **0** |
| units | 36 ok / **2 FAIL** | **40 ok / 0 FAIL** |
| mutants caught | 5 of 6 | **6 of 6** |
| `check_grader_self_blindness.py` | clean | clean |

The six mutants: PASS band `0.05→0.50`; FAIL threshold `0.15→0.95`; **sign-flip override
deleted**; `h_max 0.05→50.0`; noise target `1 %→100 %`; harness floor `0.025→0.0`. **All six now
flip the selftest to exit 1.** The unmutated control exits 0.

**`check_grader_self_blindness.py` clean is NOT a proof of correctness and is not offered as
one** — probe B fires on `os.path.join` and is silent on `pathlib` and f-strings (`3dc99590`).

**These repairs change NO gate, NO threshold, NO cap and NO label.** They change test inputs and
add two units. They are legal because **no compute has happened** (`CLAUDE.md` rule 2), and the
condition is recorded in §5.

---

## 3. WHAT I CHECKED THAT WAS SOUND

Recorded because a defect note listing only defects misrepresents the file it describes.
**`PREREGISTRATION.md` is a strong document and most of the brief's checklist passes on it.**

| check | result |
|---|---|
| every gate, threshold, cap and label stated and numeric | **YES** — G12R-0…G12R-11, all numeric |
| cost predicted with a numeric stop threshold | **YES** — 250.4 core-min predicted (340.4 with the W2 contingency), **cap 600.0**, S8 sub-cap **350.0**, `MemAvailable` floor **14.0 GiB** |
| **toolchain pinned by IMAGE HASH, not tag** | **YES, AND I VERIFIED BOTH DIGESTS ARE REAL** rather than plausible extensions of a 12-char id: `docker inspect` returns `sha256:9d45679d…f07fc` for `dafoam/opt-packages:latest` and `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` for `dafoam-idwarp-rot:v1`, **both exactly as §2.1 claims**. The IDWarp md5s are correctly sourced from `docs/dafoam/README.md:154` |
| np=1 stated explicitly with `numberOfSubdomains 1` | **YES**, and decomposition is declared *not applicable and stated as such* rather than left blank |
| two-row shipped/patched, unbought rows named with consequences | **YES** — G12R-10 gives the patched row its **own** S0/S1/S2/FIELD_B and S5, on the correct ground that an FD reference is part of a **configuration**, and registers that the patched row carries a **one-step** FD table with that limit **in the verdict line itself** |
| planted zero on every gate that reads a number | **YES** — G12R-9, three readers, each planting, reading back from disk and refusing |
| **refusal on an empty/short component set, by count, with the count printed** | **YES** — unit `U-06e` is named *"the `d3_grade.py` defect"* in the file itself |
| `scripts/check_filing.py` on `cases/dafoam/curriculum_D12/` | **NO VIOLATION.** The tree has 27 pre-existing violations across 5 rules; **none is this directory.** §0's disclosed deviation from `ladder-a/A?/` is therefore **not** a filing violation, and **the check demands no move** |
| `d12r_run_script.py` | **SOUND.** Supports `run_model`/`compute_totals`/`opt`; `daOptions` is the tutorial's verbatim; **and its CLI discipline is better than mine** — it notes that argparse's negative-number matcher accepts `-1` and `-0.001` but **not exponent notation**, and forces `--name=value`, which resolves before any flag matching. That is a sharper fix for the D11-O′ class than the sign-as-a-word scheme I used in D12-F′ |

### ONE GAP IN G12R-0 AGAINST RULE 4, NAMED

`CLAUDE.md` rule 4 has limbs G12R-0 does not carry: **the age guard** (every field at `endTime`
newer than the case's own `0/` datum) and **`ExecutionTime` count == `endTime`**. G12R-0 does
carry `rc=0`, an `End` line, `last time == endTime`, JSON `COMPLETE`, `OOMKilled false`, the
cold-start assertion, the FIELD_B md5 manifest, a JSON-vs-log agreement clause, and the
`MemAvailable` floor.

**The cold-start assertion plus the per-stage fresh copy do most of the age guard's work** — the
guard exists to prove the answer fields were produced by the run allowed to produce them, and a
stage that provably began with no time directory cannot carry a stale field. **But "most" is not
"all", and the two limbs are not registered.** They should be added before the freeze — and
**every input G12R-0 reads is supplied by the manifest the LAUNCHER writes**, so this repair and
Defect A are the same piece of work.

---

## 4. A GAP IN THE PRE-REGISTRATION'S NOISE MODEL, FOUND BY MEASUREMENT TODAY

This is not a defect in draftsmanship. It is a gate that **may not fire when it should**, and the
evidence for it was bought by this lane a few hours earlier, in **D12-F′**
(`cases/dafoam/probes/curriculum_D12_unsteady_probe_Fprime/RESULTS.md`, calibration row **C-86**).

G12R-4 sizes the FD step from **`δ_eff := max(δ_repeat, δ_window)`**. Both terms are measured
from **unperturbed** runs:

- **`δ_repeat`** — three identical runs. G12R-2 already predicts, correctly, that this is **0 to
  machine precision**, and warns in advance that a zero is not a clearance. **D12-F′ MEASURED
  EXACTLY THAT: `0.000000e+00`.**
- **`δ_window`** — the spread of `W`-step block averages over one series. A **phase** quantity —
  and, per §2 B1, **identically zero** if `W` is a multiple of the shedding period.

**NEITHER MEASURES WHAT D12-F′ MEASURED.** On the probe's window the objective carried a
**perturbation-response floor of ≈ 1.65e-06 absolute (1.8e-05 relative)** on shape component 3 —
**three-plus orders above `δ_repeat`** — and **≈ 8.4e-09** on component 0, so **the floor is
component-dependent**. It was shown **model-free**: the FD signal `|obj(+h) − obj(−h)|` at
`h = 1e-5` is **smaller** than at `h = 1e-6`, which a linear response cannot do. That floor is
what closed the small-step end of the window and left **no plateau on either component**.

**Whether `δ_window` at `W = 300` on a developed limit cycle happens to exceed this
perturbation floor is NOT KNOWN — by me or by anyone.** D12-F′ cannot settle it: its window is a
5-step cold start where `δ_window` is not even defined. **If it does not dominate, `h_min` is
computed against a floor that is too small, and G12R-4's registered `h_min > h_max → NOT A
RESULT` branch — the branch that exists precisely to refuse when no admissible step exists —
could fail to fire when it should.**

> **RECOMMENDED REPAIR, and it can only make the gate STRICTER.** Add a third term `δ_pert`,
> measured from the sweep's own smallest steps by the model-free non-monotonicity test above,
> and take **`δ_eff := max(δ_repeat, δ_window, δ_pert)`**. **No threshold, band, cap or label
> changes**: a term added to a maximum can only raise `h_min` and can only make the
> `NOT A RESULT` branch easier to fire. It cannot rescue a failing number.

**I did not apply this one.** It changes a gate's inputs rather than a test fixture, and with the
pre-registration not yet frozen and the launcher not yet written, **the supervisor should rule on
it as part of deciding who authors the launcher.** Recording it is a lane's job; changing another
lane's gate on a lane's own initiative is not (`CLAUDE.md` rule 9).

---

## 5. THE AMENDMENT CONDITION, AND HOW I CHECKED IT

Every repair in §2 was made **before first compute**, which is what makes it legal
(`CLAUDE.md` rule 2). The condition:

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady/` DOES NOT
> EXIST.**

**How it was checked:** `test -e` on that exact path returned **false** at **2026-08-25T21:11Z**,
at the start of this lane's work, and **no container has been started for this item by anyone
since** — `docker ps` was empty of DAFoam containers throughout, and this lane launched only the
two probe FD arms, whose run roots are `…/CURRICULUM-PROBES-D10-D11-D12/D10F` and `…/D12F`.

**No gate, threshold, cap or label was altered by any repair in this file.**

---

## 6. WHAT THE SUPERVISOR MUST DECIDE

1. **Who authors `d12r_stage_and_run.sh`** — this lane, a fresh lane, or the supervisor's own
   design handed down. **Until it exists, D12-proper cannot fire.**
2. **Whether `δ_pert` joins `δ_eff`** (§4). Evidence is measured and committed; the ruling is not
   a lane's.
3. **Whether the age guard and `ExecutionTime` limbs join G12R-0** (§3). Same piece of work as
   the launcher, since G12R-0 reads the launcher's manifest.
4. **Whether the pre-registration is then re-frozen as v1.1** with §4's instrument table matching
   what exists. **It must not be frozen while it names files that do not.**

---

## 7. WHAT I COULD NOT VERIFY

- **I did not run D12-proper, or any part of it.** Every statement here about the pipeline is
  read from `PREREGISTRATION.md`; **no stage timing, memory figure or convergence claim in that
  document has been tested by me.**
- **I did not verify the S1 spin-up chain works** — `preProcessing.sh`, `controlDict_simple`,
  `controlDict_pimple_long`. I read that §3 names them; I did not run them.
- **I did not verify the 250.4 core-min prediction.** It rests on the two-point fit
  `wall(n) = 19.0 + 2.000n`, which §6.1 itself registers as **UNDER TEST** and calls an
  extrapolation rather than a law. **That is the document being honest, and I add no evidence
  either way.**
- **`check_grader_self_blindness.py` clean is not proof of correctness** and is blind to
  `pathlib` and f-strings.
- **Six mutants is not a proof of comparator correctness.** It is six specific gates shown to be
  load-bearing. **The gaps a mutation battery does not probe are unknown by construction**, and
  M3 is the standing proof that this battery finds real ones.
- **Whether `δ_window` dominates `δ_pert` at `W = 300`: UNKNOWN**, and unknowable from anything
  measured so far (§4).

**SUBMISSIONS ARE PARKED. Nothing in this file has been sent, filed, uploaded, registered,
posted or commented, and sending is Sanaa's decision alone.**
