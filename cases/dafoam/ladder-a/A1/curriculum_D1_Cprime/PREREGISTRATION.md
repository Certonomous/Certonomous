# Curriculum mini-item D1-C′ — the SHIPPED-image endpoint gradient at arm O's converged design point

**NOT FILED ANYWHERE.** Nothing in this document or the item it registers is filed, sent, emailed,
uploaded, posted, registered, submitted or commented outside this box, now or ever (`CLAUDE.md`
rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.** Readiness is not sending, and no reading of
this file authorises a send.

**NOT FILED — the five upstream DAFoam defect drafts are untouched by this item and remain drafts.**

**Written 2026-08-24T16:45:23Z by Lane C′ (Opus), DAFoam team, on the dafoam supervisor's ruling at
`PREREGISTRATION.md` §17 of `../curriculum_D1/` (session `01ENBw3KPr5gMaj8Vt7rcxSB`).**
**Every UTC stamp in this file is `date -u` output read in the shell invocation that wrote it into
the file** (D1 Amendment 1 §A1.2, adopted here).

**PHASE 1 ONLY. This freeze authorises NOTHING. No container is started, no solver is run and no
core-minute is spent by the invocation that commits this file.** Launch authorisation comes
separately, in writing, from the supervisor, after its personal verification of this freeze
(`SUPERVISION_CHARTER.md` §3: pre-registration **committed** before compute, and the check is the
supervisor's, not this lane's).

---

## 0. What this mini-item is, in four lines

D1 arm C — the shipped-toolchain row of the endpoint gradient — died at 14 s before any solve, on a
producer/consumer key mismatch inside a frozen comparator that the frozen file's own §4.2(c)
forbids repairing in place (L-273; `../curriculum_D1/RESULTS.md` §8). The supervisor declined to
reinterpret that clause and re-registered the comparison as this mini-item (`../curriculum_D1/
PREREGISTRATION.md` §17). **D1-C′ measures the shipped-image analytic gradient at arm O's own
converged design point, against a finite-difference reference taken in the same run at the steps arm
O used, and reports it beside arm O's patched row — two rows, never merged (R11).** It fills row
**38b** of `../../LADDER_A_STATUS.md` and discharges D1 §3.3's bought deliverable.

**What is different this time, and it is the whole reason the item is cheap enough to buy twice:**
the comparator is **frozen in this repository by md5 before the run root exists**, and its
planted-zero control **plants into arm O's real artifact and has already been run against it, at
zero compute, with the output pasted into this file below the freeze line** (§5). D1 §4.2 had to
register *"the driver file cannot be hashed before it exists"*; that concession is not needed here
and is not taken.

---

## 1. Frozen inputs — arm O's design point, by line and by md5

**These are inputs, not results. They were produced by D1 arm O under its own frozen
pre-registration and are consumed here unchanged. A mismatch at launch VOIDS this item; it is not
repaired, re-derived or worked around.**

### 1.1 The two artifacts

| artifact | absolute path | md5 (read on the host at this freeze) | size |
|---|---|---|---|
| arm O's run log | `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO_20260824T160553Z_1400030.log` | **`64bee1631d28ab07973e56ec7e1f4bf3`** | 16,632 lines |
| arm O's endpoint JSON | `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO/endpoint_20260824T160552Z_1399954.json` | **`e63f57710cee6e2170f2e9cef39f8b2a`** | 4,910 bytes |

The JSON md5 is additionally **frozen inside the comparator itself** as
`d1c_endpoint.py:ARMO_JSON_MD5`, asserted before the file is opened, and re-asserted **after** the
planted-zero control has run, so the control cannot damage the evidence it reads.

### 1.2 The design point — the frozen input this item exists to re-solve at

`D1_ENDPOINT_PATCHED_SHAPE`, **log line 9251**, and `D1_ENDPOINT_PATCHED_PATCHV`, **log line 9252**;
identical to the `shape` and `patchV` keys of the endpoint JSON.

```
shape  = [0.02876504584608877, 0.047201042921213354, 0.016871666037627377, 0.036676713888073136,
          0.0472289265360477,  0.022959816884178426, 0.008262623112944891, 0.036138219756860344]
patchV = [10.0, 1.128636497545056]        # U0 pinned and inert; AoA in degrees
```

### 1.3 The patched reference values this item compares against, by line

All from the same log, md5 above. **They are read here for registration only; the run reads them
from the JSON, through the reader the planted-zero control exercises.**

| what | log line | value |
|---|---|---|
| `D1_ENDPOINT_PATCHED_CD` | 9249 | `0.017527899854535338` |
| `D1_ENDPOINT_PATCHED_CL` | 9250 | `0.49999981209363359` |
| `D1_ENDPOINT_PATCHED_JADJ` | **9283** | `shape[6] = -0.02770157042975438`, `shape[1] = 0.019112933615071107`, `shape[5] = 0.03886606849182183`, `patchV[1] = 0.0011232501148069679` |
| `D1_ENDPOINT_PATCHED_FDPLAN` | 9284 | the four step pairs, reproduced as literals in §4.3 |

The four graded FD estimates, `D1_ENDPOINT_PATCHED_FD … s_hi`, and their `s_lo` partners:

| component | `s_lo` line | FD @ `s_lo` | **`s_hi` line** | **FD @ `s_hi` (graded)** | arm O rel. err @ `s_hi` | plateau line | plateau |
|---|---|---|---|---|---|---|---|
| `shape[6]` | 9979 | `-0.027675197554269393` | **10754** | **`-0.027687022184045888`** | `5.254536e-04` | 10755 | `4.270820e-04` |
| `shape[1]` | 11530 | `0.019185108244210158` | **12385** | **`0.01914429682810017`** | `1.638254e-03` | 12386 | `2.131779e-03` |
| `shape[5]` | 13273 | `0.038982572416086658` | **14256** | **`0.038913886768361661`** | `1.228823e-03` | 14257 | `1.765068e-03` |
| `patchV[1]` | 15160 | `0.0011315588975650825` | **16079** | **`0.0011261246187973621`** | `2.552563e-03` | 16080 | `4.825646e-03` |

`D1_ENDPOINT_PATCHED_TRIVIAL`, **log line 16631**: `shape[6]` at `1e-8`, `fd = 0.21984666830066057`,
`rel_err = 1.126004049294347`, `sign_flip = true`.

### 1.4 Pre-existing gaps in the frozen chain, disclosed and non-load-bearing

Disclosed by Lane Z and carried forward here rather than silently repaired
(`../curriculum_D1/PREREGISTRATION.md` §17): **the endpoint JSON carries no `.ok.${STAMP}`
sentinel** (D1 §9.2 registers sentinels for the D1 chain), and **no `fdplan_${STAMP}.json` was
written** (D1 §10). **This item does not rely on either.** Its substitutes are stronger and are
registered here: the JSON is bound **by md5** rather than by sentinel, and the FD plan is bound by
**literals frozen in `d1c_endpoint.py:FROZEN_STEPS`** which the read value must equal or the
comparator refuses (§4.3, falsifier **F5**). A sentinel proves *which invocation* wrote a file; an
md5 proves *which bytes* are in it, and it is the bytes this item consumes.

---

## 2. Toolchain — two rows, and this item's graded row is the SHIPPED one (`DAFOAM_CHARTER.md` §6)

| row | image | image ID / digest | `libidwarp.so` md5 | role here |
|---|---|---|---|---|
| **SHIPPED** — **graded by this item** | `dafoam/opt-packages:latest` | **`9d45679d55fd`**, `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** | the one container this item runs |
| **PATCHED** — **read, never re-run** | `dafoam-idwarp-rot:v1` | **`2927768a16ac`**, `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | arm O's frozen numbers, consumed from §1 |

**Both digests were re-read from `docker images --no-trunc` on this box in the invocation that stamped
and committed this file, and both matched the values D1 §3 registered** — the assertion is
`dafoam/opt-packages:latest = sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`. A version string is not an identity:
IDWarp reads `2.6.2` on both stacks and the two `.so` files are the same size — the hash is the only
identity (`DAFOAM_CHARTER.md` §6).

**`IDWARP_SO_MD5` is printed from inside the process that loads the library** and must equal
`f0fcb488e0e98156575cd19548e91663`. A mismatch **voids the arm** (falsifier **F1**, gate **G-C7**).
`nProcs : 1` is asserted in the log.

**R11 is not touched.** A patched grade does not replace a shipped grade and a shipped grade does not
replace a patched one; whether the lab adopts a forked toolchain is Sanaa's call, not this item's.

---

## 3. The arm — one container, np = 1

| arm | image | task | what it does |
|---|---|---|---|
| **C′** | SHIPPED | `d1c_shipped` | zero-compute controls → inject arm O's design vector → **one cold primal** → **one adjoint** → central differences on the four named components at the **inherited** steps → the trivial baseline at `1e-8` → write `endpoint_shipped_${STAMP}.json` |

**np = 1** (`DAFOAM_CHARTER.md` §5: serial before parallel; A1 has no decomposition axis at np=1 and
every A1 figure this item leans on was measured at np=1). **The decomposition is stated with the
number in every table this item produces.**

**One difference from arm O that is registered rather than glossed.** Arm O reached the endpoint
through 11 optimiser majors, so its endpoint primal was warm-started from major 11. This arm reaches
the same design point by **injecting the vector into a cold-staged case and solving once from `0/`**.
The primal stopping rule is identical (`primalMinResTol 1e-8`), but the path is not.
`../../A4/shipped_optimisation_np1/RESULTS.md` §3.2 measured an FD reference at a deformed design
point to be **path-dependent at the 0.183 % level** (two runs, same optimum to `1.8e-07`). **The
consequence is bounded and registered:** the item's **primary** gate G-C1 compares the shipped
analytic against **this same run's own FD**, so it is path-immune; the **cross-run** comparison of
this run's FD against arm O's FD is a separate control, G-C3, banded at **0.5 %** for exactly this
reason (P7). **A difference beyond that band is a finding about path and cold start, not about the
toolchain, and will be reported as one.**

---

## 4. The comparator — frozen in this repository, by md5, before the run root exists

### 4.1 Two files, both frozen by the commit that carries this document

| file | md5 at this freeze | lines | what it is |
|---|---|---|---|
| `d1c_endpoint.py` | **`b20c829f7ea4b63d2a9fec5f673d1cbb`** | 368 | the comparator core: the reader, the planted-zero control, the negative control, the key-set control, the FD kernel, the grading band. **Standard library ONLY** |
| `d1c_runScript.py` | **`f7f17c64331df596434f19fbee907233`** | 478 | the case run script: the staged `runScript.py` head plus one task branch |

**Both live in this repository directory, are committed with this file, and are copied into the run
root at staging with their md5s re-asserted against the values above.** This is a deliberate
departure from D1 §4.2, which had to register that *"the driver file cannot be hashed before it
exists"* and then paid for the concession twice — once in L-266 (a rule dry-run that was never done)
and once in L-273 (a control that was never coupled to its producer). **Here the grading path is
fixed at the pre-registration commit in the literal sense `CLAUDE.md` rule 2 asks for: the frozen
file *is* the committed blob, and the launch invocation proves it by hash.**

**Neither file is edited after the first launch. An edit voids the arm; that voiding is reported,
not repaired** (D1 §4.2(c), adopted verbatim as this item's own condition).

### 4.2 `d1c_runScript.py` — the registered diff, asserted

Everything above line 231 is **byte-identical** to the staged case's own `runScript.py`
(md5 `0557da51f6f179f6de865144343c499f`; `head -231` md5 **`b34aa99e2f6f1c95b31a49b01070844d`**, equal
on both files, verified at this freeze). The single registered change is the replacement of that
file's task chain (its lines 232–252) by one `d1c_shipped` branch. **`diff` against the staged
`runScript.py` is 2 hunks — `232,238c232,369` and `240,249c371,475` — both inside the task chain, and
this hunk count is asserted again in `RESULTS.md`.** **No numeric setting is altered.** The IPOPT
option block is inert here because `run_driver()` is never called, and it is left untouched rather
than deleted so that the diff stays confined to the task chain.

### 4.3 The steps are INHERITED, and frozen twice

**No step is selected by this item.** Each is read from arm O's frozen plan **and** asserted equal to
a literal frozen in `d1c_endpoint.py:FROZEN_STEPS`, so a step cannot move even if the file read is
wrong (falsifier **F5**, refusal `STEP_MOVED`):

| component | `s_lo` | **`s_hi` — the graded step** |
|---|---|---|
| `shape[6]` | `1e-4` | **`3e-4`** |
| `shape[1]` | `1e-4` | **`3e-4`** |
| `shape[5]` | `1e-4` | **`3e-4`** |
| `patchV[1]` | `1e-3` | **`3e-3`** |

**Both rungs are run, not only the graded one.** The graded step is `s_hi`, exactly as arm O's. The
`s_lo` rung is bought — 8 extra warm primals, **0.37 core-min**, priced in §8 — solely so that the
**two-step plateau test** that makes a component GRADED under D1's G3 can be applied to the shipped
row on the same terms as the patched one. **A shipped row graded on a weaker test than the patched
row it sits beside is not a comparison.**

**Component order is `shape[6]`, `shape[1]`, `shape[5]`, `patchV[1]` and the FD kernel restores by
SET without solving** — arm O's order and arm O's kernel semantics
(`d1_fd_endpoint.py:62-80`, md5 `7e454d2f1830a40086465d9b5c57a941`), **reproduced rather than
improved**, because the warm-start history is part of the instrument and the comparison is
like-for-like only if it matches.

### 4.4 `η` — INHERITED, with the reason, and an observation bought for nothing

**`η = 1.957349804806996e-08` is INHERITED from D1 arm E run 2 and is NOT re-measured on the shipped
image.** Three reasons, and the first is the one that matters:

1. **It cannot alter a gate here.** Every step is inherited (§4.3). `η` enters this item only through
   the printed diagnostic `C_measured`, and even that is computed from the **measured primal
   difference** `|f(x+s) − f(x−s)| / η` rather than from the analytic under test (§4.5) — so `η`
   scales a diagnostic and selects nothing. D1's own reason for measuring `η` — to *choose* a step
   from `|J_adj|` — does not exist in this item.
2. **`η` is a property of the primal's stopping noise, and the primal is the same on both images.**
   The IDWarp rotation patch is a mesh-warp **derivative** change; the reverify A/B pair measured
   **8 of 8 raw `Jfd` components bit-identical** across the two images at np=1 on this case
   (`../reverify_patched_idwarp_np1/RESULTS.md` §3), which is a direct measurement that the primal —
   and therefore its noise floor — does not move with the image.
3. **A re-measurement would cost a second cold primal (~20 s ≈ 0.33 core-min) to produce a number
   that changes nothing.** That is not a reason on its own and is listed third deliberately.

**What is bought for nothing, and reported:** this arm's own cold primal prints `CD` at
`printInterval 10`, so the **endpoint** peak-to-peak over the last 5 printed samples is computable
from this arm's log at **0.000 core-min**, by the frozen helper `d1c_endpoint.py:eta_from_series`
under D1 Amendment 2 §A2.2's registered definition. **It is reported as `ETA_CPRIME_OBSERVED`, it
sizes nothing, and it is not used to grade anything.** It is registered because
`../curriculum_D1/RESULTS.md` §5.3 recorded, as a standing limitation, that the endpoint's own noise
floor had never been measured — and this item can observe it for free. **An observation is not a
measurement of the mitigation D1 registered, and this file does not upgrade it into one.**

### 4.5 `C_measured` is computed from the primal, never from the gradient under test

D1's rule prints `C(s) = |J_adj|·2s/η`. On the patched row that is harmless. **On the shipped row it
would clear a gradient against itself** — the shipped `shape[6]` analytic is the very quantity
suspected of being wrong, and a clearance computed from it would be large for the wrong reason.
**This item therefore computes `C_measured := |f(x+s) − f(x−s)| / η`**, which is algebraically
`|J_fd|·2s/η` and identical in value to what arm O's own JSON already reports as `C_measured`
(848.7095 / 586.8434 / 1192.8543 / 345.1988 at the graded steps). **The change removes a circularity
and moves no threshold: `C ≥ 5` is inherited unchanged.**

---

## 5. The planted-zero control (`CLAUDE.md` rule 3) — and the dry run against the REAL artifact, executed BEFORE this freeze

**This section is the reason this mini-item exists in the form it does, and it is the L-273 repair.**

`CLAUDE.md` rule 3: *a zero from a reader not shown able to see a non-zero is not evidence.* L-273
adds the half that killed D1 arm C: **a plant seen in a file no producer writes is not that
demonstration.** The control registered here therefore does four things D1's did not:

1. **It plants into a copy of arm O's REAL artifact**, md5-asserted `e63f57710cee6e2170f2e9cef39f8b2a`
   before and after, never into a hand-built fixture.
2. **It plants into EVERY channel this comparator consumes** — `shape`, `patchV`, `plan`, `eta`,
   `J_adj`, `fd` — and refuses unless **every one** reads back moved by exactly
   `PLANT = 1.234e-03`. A consumed channel the control does not plant into is precisely the hole
   L-273 names.
3. **It asserts the producer's key set** against a literal frozen in the comparator
   (`PRODUCER_KEYS`, read from the file arm O actually wrote), and refuses by name. **This is D1 arm
   C's own failure turned into a control:** the `keycheck` mode renames `CD` to `CD_final` — the exact
   mismatch that killed arm C at 14 s of container time — and the comparator must refuse with a named
   message rather than die on a `KeyError` inside a consumer.
4. **It carries a negative control**: a deliberately blind reader, one that returns the unperturbed
   file whatever path it is handed, **must be refused**. A control that cannot fail is not a control.

**All refusals exit 2. None degrades to a warning.**

### 5.1 The dry run, pasted verbatim, executed at zero compute before this freeze

**No container. Host `python3`, standard library only. The source artifact's md5 is shown before and
after and is unchanged.** The `WORK` directory here is a throwaway scratch directory used only to
prove the reader; **at launch the same code runs with the run root in its place, and no repository
document cites a scratch path** (`CLAUDE.md` rule 13, L-186).

```
UTC 2026-08-24T16:40:05Z | host ip-172-31-43-247 | Python 3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0] | stdlib only, NO container
SRC  = /home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO/endpoint_20260824T160552Z_1399954.json
WORK = <scratch dry-run dir; the launch invocation uses the run root instead>
SRC md5 BEFORE  = e63f57710cee6e2170f2e9cef39f8b2a

$ python3 d1c_endpoint.py selftest
D1C_SELFTEST_CUBIC {"calls": 2, "derivative": 12.00000001000845, "expected": 12.0, "pass": true, "rel_err": 8.340374317109914e-10}
  rc=0

$ python3 d1c_endpoint.py plantcheck $SRC $WORK      # plants PLANT=1.234e-03 into a copy of the REAL arm O artifact
D1C_G5_PLANTED_ZERO OK {"channel_seen": {"J_adj": true, "eta": true, "fd": true, "patchV": true, "plan": true, "shape": true}, "channels_planted": ["shape", "patchV", "plan", "eta", "J_adj", "fd"], "max_residual_vs_plant": {"J_adj": 2.3852447794681098e-18, "eta": 0.0, "fd": 1.0842021724855044e-18, "patchV": 1.7932703932910243e-16, "plan": 2.168404344971009e-19, "shape": 1.0842021724855044e-18}, "pass": true, "plant": 0.001234, "src_md5_after": "e63f57710cee6e2170f2e9cef39f8b2a", "src_md5_before": "e63f57710cee6e2170f2e9cef39f8b2a", "src_unchanged": true}
  rc=0

$ python3 d1c_endpoint.py negcheck  $SRC $WORK      # a deliberately blind reader MUST be refused
D1C_REFUSE PLANTED_ZERO {"channel_seen": {"J_adj": false, "eta": false, "fd": false, "patchV": false, "plan": false, "shape": false}, "channels_planted": ["shape", "patchV", "plan", "eta", "J_adj", "fd"], "max_residual_vs_plant": {"J_adj": 0.001234, "eta": 0.001234, "fd": 0.001234, "patchV": 0.001234, "plan": 0.001234, "shape": 0.001234}, "pass": false, "plant": 0.001234, "src_md5_after": "e63f57710cee6e2170f2e9cef39f8b2a", "src_md5_before": "e63f57710cee6e2170f2e9cef39f8b2a", "src_unchanged": true}
D1C_G5_NEGATIVE_CONTROL OK refused=PLANTED_ZERO
  rc=0

$ python3 d1c_endpoint.py keycheck  $SRC $WORK      # L-273 replayed: producer key 'CD' renamed to 'CD_final'
D1C_REFUSE KEYSET {"expected": ["CD", "CL", "J_adj", "cons", "eta", "fd", "feasible_note", "maxrss_GiB", "patchV", "plan", "shape", "tag", "trivial"], "extra": ["CD_final"], "found": ["CD_final", "CL", "J_adj", "cons", "eta", "fd", "feasible_note", "maxrss_GiB", "patchV", "plan", "shape", "tag", "trivial"], "missing": ["CD"], "where": "keyset_control_renamed.json"}
D1C_G5_KEYSET_CONTROL OK refused=KEYSET
  rc=0

SRC md5 AFTER   = e63f57710cee6e2170f2e9cef39f8b2a
```

**What this dry run establishes, stated precisely and no wider:** the frozen reader can see a plant
in **the real file the real producer wrote**, on every channel the comparator consumes; it refuses a
blind reader; and it refuses the exact key mismatch that blocked arm C. **It does not establish
anything about the shipped gradient, the container, or the solver** — those are what the run is for.

---

## 6. Gates — every one with its number

**Grading band (`DAFOAM_CHARTER.md` §2, `VERIFICATION_CHARTER.md` §7), applied PER COMPONENT:**
**PASS ≤ 5 % with zero flagged components; CONDITIONAL 5–15 % with the per-component breakdown
printed; GATE FAIL above 15 % or on ANY sign flip, whatever the aggregate.**

### G-C1 — the primary gate: shipped analytic vs this run's own FD, per component

Graded at `s_hi`. A component is **GRADED** only where `C_measured ≥ 5` at the graded step **AND**
its two steps agree within the inherited plateau tolerance of **10 %**. A component failing either
test is **FLAGGED and excluded BY NAME** from any aggregate (`DAFOAM_CHARTER.md` §3), never rescued
by a step at which it happens to cross.

**Verdict:** `PASS` if every graded component ≤ 5 % with zero sign flips; `CONDITIONAL` 5–15 % with
the table printed; **`GATE FAIL`** above 15 % **or on any sign flip**. **The per-component table is
the primary report and is never folded into an aggregate.** If an aggregate is quoted it is named as
**the vector-relative error `‖J_an − J_fd‖/‖J_fd‖` over the graded components only**, with the
flagged ones listed by name beside it — and **a vector norm is never compared against a published
per-component average** (`DAFOAM_CHARTER.md` §2).

### G-C2 — the §3.3 deliverable: the toolchain comparison, two rows, never merged

**This gate is on the instrument, not on the size of a difference.** It is **PASS** only if all of:
the shipped and patched analytic values are printed **per component, side by side, for all four
components**, with the difference and its relative size; **no aggregate is substituted for the
table**; the design point is proved identical (F2 and F6 both clear); and **neither row is described
as replacing the other** (R11). Otherwise **GATE FAIL**, and D1 §3.3's deliverable stays open.

**No threshold is placed on the difference itself.** The difference is the measurement this item was
bought to make; its predicted values and bands are P6, scored HIT/MISS, and a MISS there is a finding
about the defect's scaling, not a failure of the item.

### G-C3 — cross-run FD control: this run's FD vs arm O's FD at the same steps

**`|FD_C′ − FD_armO| / |FD_armO| ≤ 0.5 %` on all four components at both rungs.** Basis and reason in
§3 and P7. **A breach does not fail G-C1** — G-C1 is path-immune by construction — but it **caps what
G-C2 may claim**: beyond the band, the shipped-vs-patched difference can no longer be attributed to
the toolchain alone, and `RESULTS.md` says so in those words.

### G-C4 — trivial baseline (`DAFOAM_CHARTER.md` §4)

**The same probe at a deliberately wrong step: `shape[6]` at `step = 1e-8`, on the shipped stack.**
Registered prediction **> 50 %** (P10). **If the wrong step also passes (≤ 5 %), G-C1's verdict is
WITHDRAWN and this item reports that the gate was not measuring what it claimed.**

**Why `1e-8` and not one order off the registered step**, restated because the reasoning is
inherited and must not be assumed: one order off `3e-4` is `3e-3` and `3e-5`; `3e-3` sits **inside**
A1's measured plateau and `3e-5` sits on its shoulder, so a step there is not a wrong step on this
case and would build a control that passes for the same reason the real arm does. A1's own measured
roundoff branch is severe by `1e-8` (`../A_stepsize_study.md`; 94.95 % at `1e-8`), and the precedent
is executed and scored at `../reverify_patched_idwarp_np1/RESULTS.md` §4.3 (132.75 % on the patched
stack) and again by arm O (112.6004 %, sign-flipped).

### G-C5 — planted-zero control (`CLAUDE.md` rule 3)

§5, in full. **Dry-run against the real artifact before this freeze, with the output pasted above,
and re-run inside the container before the design point is touched.** All three sub-controls — plant,
negative, key-set — must return OK or the arm **refuses (exit 2)** and **no figure computed from a
file is reported anywhere in the record**.

### G-C6 — launch gate, re-run immediately before the launch

**`free_cores ≥ 4` AND `MemAvailable ≥ 12 GiB`**, where `free_cores := nproc − load1`
(`/proc/loadavg` field 1; `/proc/meminfo MemAvailable`). **The 12 GiB floor is the lab's standing
floor: this item neither touches it nor argues with it.** The gate is run as its **own command**,
its output appended to the run root's `preflight_history.txt` with a UTC stamp, and **its result is
read before the launch command is issued** — never polled by a background process. If the gate is not
open the arm **waits and the gate is re-run**; it is not launched under a departure on this lane's
authority. Any departure must be directed in writing by the supervisor and recorded as a dated
amendment **before** the launch, never after.

### G-C7 — image identity

`IDWARP_SO_MD5`, printed from inside the process that loaded the library, must equal
**`f0fcb488e0e98156575cd19548e91663`**. A mismatch **voids the arm**. `nProcs : 1` asserted.

### G-C8 — cold start

Verified **before** the launch, not after: the run root did not exist before staging (§11); the
staged tree contains **no `processor*` directory and no numeric time directory**; `0/` is restored
from `0.orig/` and its files are md5-equal to their `0.orig/` counterparts; no `reports/` is carried
over. **pyDAFoam writes the primal end state back into the time-0 directory at run end, so a second
run of a case directory silently warm-starts** (`DAFOAM_CHARTER.md` §6) — this arm runs in a
**freshly staged** directory that has never been run in, and the staging sources are copied FROM and
never run IN.

### G-C9 — memory envelope (`DAFOAM_CHARTER.md` §7)

Predicted peak **1.70 GiB**, ceiling **2.5 GiB** (P13). **Kernel cap `--memory=6g --memory-swap=6g`**
— equal, so there is no swap escape — plus **`--oom-score-adj=500`** and the stage `timeout`. **A
container the kernel OOM-killed (`.State.OOMKilled == true`, or exit 137) is recorded as stopped by
memory and is `NOT A RESULT` about anything else** — it is not re-labelled as a solver finding.
Equally, **a failure with headroom unused is not a memory finding either** (L-15), and the peak is
reported beside the cap so a reader can tell.

### G-C10 — cost ceiling

**HARD ceiling 10.0 core-min = $0.00855 DERIVED.** An overrun **stops the run**; it does not get a
new budget (`CLAUDE.md` rule 12). §8.

---

## 7. Predictions — numeric bands, cited bases, every one scored HIT/MISS in `RESULTS.md`

**The additive-defect model, stated once because five predictions rest on it.** The measured np=1
baseline A/B pair on this case at step `1e-3`
(`../reverify_patched_idwarp_np1/RESULTS.md` §4.1, §4.2) gives, per component,
`defect := J_shipped − J_patched`: **`shape[6] +6.756380e-03`**, **`shape[1] −2.301870e-03`**,
**`shape[5] −1.043190e-03`**. **H1** takes that absolute defect to the endpoint unchanged; **H2**
takes the *relative* error unchanged (640.3696 % / 11.6625 % / 2.4146 %). The two hypotheses are
**indistinguishable on `shape[1]` and `shape[5]`** (12.19 % vs 11.66 %; 2.80 % vs 2.41 %) and
**differ by a factor of 26 on `shape[6]`**, whose `|J|` grew 26× between baseline and endpoint
(`1.066e-3 → 2.770e-2`). **`shape[6]` is therefore the discriminator, and this item registers H1 as
its point prediction with H2 named as the registered alternative.** The mechanism behind H1: the
defect lives in IDWarp's `getRotationMatrix3d` **reverse-mode warp derivative**, so the erroneous
term is `(dCD/dXv)·Δ(dXv/dXs)` — set by the geometry and the flow state, **not** by the magnitude of
the correct gradient it is added to.

| id | prediction | point | **band (HIT if inside)** | basis |
|---|---|---|---|---|
| **P1** | shipped-vs-FD rel. err, **`shape[6]`** @ `3e-4`, **and NO sign flip** | **24.35 %** | **[10 %, 60 %], flip = FALSE** | H1 on the measured `+6.756380e-03` defect against arm O's FD `-0.027687022184045888`. **H2 would give ≈ 640 % WITH a flip and is the registered alternative; if H2 lands, P1 is a MISS and the finding is that the rotation defect scales with `\|J\|`, not with the geometry** |
| **P2** | shipped-vs-FD rel. err, **`shape[1]`** @ `3e-4` | **12.19 %** | **[4 %, 30 %]** | H1; H2 gives 11.66 %, inside the same band — this component does **not** discriminate and is registered as such |
| **P3** | shipped-vs-FD rel. err, **`shape[5]`** @ `3e-4` | **2.80 %** | **[0.5 %, 12 %]** | H1; H2 gives 2.41 %, also inside — does not discriminate |
| **P4** | shipped-vs-FD rel. err, **`patchV[1]`** @ `3e-3` — **the control component** | **0.2553 %** | **[0.15 %, 0.45 %]** | `patchV` is the only live DV that **does not cross `warpDeriv`** (identity gate IG-2), and the reverify pair measured its rows **identical to every printed digit across the two images**. Arm O's patched value at this step is `0.2553 %`. **If `patchV[1]` moves outside this band, the comparison is not isolating the warp-derivative defect and G-C2's attribution is withdrawn** |
| **P5** | **the SHIPPED row's G-C1 verdict** | **`GATE FAIL`** | **GATE FAIL, driven by `shape[6]` > 15 %, with ZERO sign flips on all four components** | P1–P4. Registered before the run so that the verdict cannot be chosen after the number is seen |
| **P6** | toolchain difference `J_shipped − J_patched`, per component | `shape[6]` **`+6.76e-03`**; `shape[1]` **`−2.30e-03`**; `shape[5]` **`−1.04e-03`**; `patchV[1]` **`0`** | `shape[6]` **[+2e-3, +2e-2]**; `shape[1]` **[−8e-3, −5e-4]**; `shape[5]` **[−5e-3, −1e-4]**; `patchV[1]` **`\|Δ\|/\|J\| < 1e-6`** | H1 and IG-2, as above. **The signs are part of the prediction** |
| **P7** | this run's FD vs arm O's FD, same steps, all four components, both rungs | **< 0.05 %** | **≤ 0.5 %** (gate G-C3) | 8/8 raw `Jfd` bit-identical across images at baseline (`../reverify_patched_idwarp_np1/RESULTS.md` §3) sets the image term to ~0; A4 §3.2's measured **0.183 %** path-dependence at a deformed design point sets the band |
| **P8** | two-step plateau, all four components | **≤ 1 %** | **≤ 10 %** (the inherited grading tolerance) | arm O measured `4.270820e-04` … `4.825646e-03` at the same steps; the plateau is an FD-side property and is image-independent |
| **P9** | `C_measured` at the graded step | `shape[6]` **848.7**, `shape[1]` **586.8**, `shape[5]` **1192.9**, `patchV[1]` **345.2** | **within 5 % of each** | arm O's own `C_measured`, recomputed from the primal difference (§4.5) |
| **P10** | trivial baseline, `shape[6]` @ `1e-8` | **109.5 %**, sign flip **TRUE** | **> 50 %** (the gate) — reported band **[50 %, 10000 %]** | arm O's FD at `1e-8` is `0.21984666830066057` against an H1 shipped analytic of `−2.09e-02`. **Stated honestly: an FD estimate at `1e-8` is roundoff noise and its VALUE is not expected to reproduce — only its magnitude class is predicted, which is why the band is two orders wide** |
| **P11** | `\|CD_shipped − CD_armO\|` at the injected design point | **< 1e-8** | **≤ 5e-6** (absolute) | the primal is image-independent and both runs stop on `primalMinResTol 1e-8`; arm O's endpoint `CD = 0.017527899854535338`. **This is the cold-start and design-point identity check** — falsifier **F6** |
| **P12** | cost, actual core-min | **1.62** | **≤ 3.24** (the 100 % contingency band); **HARD ≤ 10.0** | §8 |
| **P13** | peak RSS | **1.70 GiB** | **≤ 2.5 GiB** | arm O measured `1.6964 GiB` on a strictly larger workload (optimiser history, 11 majors); **reported only if `/usr/bin/time -v` exists in the image — it did NOT in any D1 arm (`D1_USRBIN_TIME: absent`), so `getrusage` from inside the process is used, and if neither is available P13 is `NOT EVALUATED`, said plainly** |

---

## 8. Cost (`CLAUDE.md` rule 12; `DAFOAM_CHARTER.md` §12)

`cost_basis: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.` The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); **every dollar
figure here is DERIVED.** Core-minutes are **wall seconds × ranks ÷ 60**, billed as **cores × wall
for the whole clock** — the lab's DAFoam convention, because `docker run` holds its cpu allocation
whether the solver saturates it or not.

**Every line below is derived from a MEASURED D1 anchor, and the anchor is named.**

| stage of the single container | predicted wall | measured anchor it is derived from |
|---|---|---|
| container start, imports, mesh read, OpenMDAO/DAFoam problem build | **14 s** | **arm C reached exactly this point and died at 14 s on the same image** (`../curriculum_D1/RESULTS.md` §8; ledger `wall_s=14`) |
| zero-compute controls (§5) inside the container | **< 1 s** | the host dry run above, stdlib only |
| one **cold** primal at the injected design | **20 s** | arm E run 2 was **27 s** wall total on the patched image, of which ~14 s is the startup above → cold primal ≈ **13 s**; **20 s** registered for the deformed, cambered design point |
| one adjoint (`CD` wrt `shape`, `patchV`) | **9 s** | arm O log elapsed **273.19 s → 281.77 s = 8.58 s** for exactly this call |
| 16 warm perturbed primals (4 components × 2 rungs × 2 signs) | **45 s** | arm O log elapsed **281.77 s → 323.99 s = 42.2 s** for exactly these 16 primals |
| trivial baseline, 2 warm primals | **4 s** | arm O log elapsed **323.99 s → 327.49 s = 3.50 s** |
| JSON write, `chown`, container inspect and teardown | **5 s** | arm O's whole-arm 361 s against its 327.49 s internal clock |
| **TOTAL predicted wall** | **97 s** | |

| | core-min | $ DERIVED |
|---|---|---|
| **REGISTERED PRICE (point)** | **1.62** | **$0.00138** |
| with 100 % contingency | **3.24** | $0.00277 |
| **HARD CEILING** | **10.0** | **$0.00855 — an overrun STOPS the run** |

**The supervisor's indicative figure of ~2.5 core-min** (`../curriculum_D1/PREREGISTRATION.md` §17)
**sits inside the contingency band; this lane re-derives 1.62 from the itemised anchors above and
discloses the gap rather than adopting the indicative number.** The 10.0 hard ceiling is the one
the brief registered and is not this lane's to move.

**The `s_lo` rung, priced separately because it was a choice** (§4.3): 8 of the 16 FD primals, **≈ 22 s
= 0.37 core-min**, **23 % of the registered price**. It buys the two-step plateau test on the shipped
row. **It is registered as bought, not absorbed.**

### 8.1 L-250 — `timeout` at the predicted envelope plus a stated margin, never at the budget's edge

*"A per-stage timeout cap is both the bound on a hang and the size of the loss."*

| stage | predicted wall | **registered `timeout`** | stated margin | loss bound if it hangs |
|---|---|---|---|---|
| arm C′ (the only container) | 97 s | **330 s** | **3.4×** | **5.50 core-min** |

**The `timeout`, not the ceiling, is the binding instrument**: 5.50 core-min is **55 % of the 10.0
ceiling**, so a hang is stopped by the wall clock well inside the budget and is recorded as stopped
by the wall clock. **The arm runs foreground-or-polled under its `timeout`; no unbounded process is
started, and no watcher script is used** (§9).

### 8.2 The calibration deliverable — Sanaa's standing directive, DRAFTED here and LANDED by the supervisor

Her directive, verbatim (2026-08-23, `CLAUDE.md` rule 12): *"for all teams involved once a process is
completed, the estimated costs must be compared with the actual incurred costs so we can improve the
lab's estimates."*

**This lane does not write `docs/COST_CALIBRATION.md`** (D1 Amendment 1 §A1.1, adopted). At
completion `RESULTS.md` will carry a **drafted row** in that file's registered ten-column format for
the supervisor to land under the rule-10 private-index protocol, with the table tail re-derived **in
the same shell invocation as the commit**. The row must carry: predicted **1.62** vs actual
core-min from this arm's own log and ledger; **dollars DERIVED** at $0.0513/core-h and labelled
derived; the **ratio** actual/predicted; and gap attribution split **contention / waste /
misprediction** with **waste separately named and never laundered into either of the others nor into
the ratio's explanation**. **Row id: derived at drafting time from the file's tail — the MAXIMUM
existing number, never a count (`CLAUDE.md` rule 11); the maximum at this freeze is `C-27`, so the
draft will read `C-28`, and it is RE-DERIVED at append time because peers commit constantly.**

**It is additionally registered that this row must state its relationship to `C-24`** — D1's own
calibration row, which closed with *"a correcting row is owed if arm C later runs."* **This item is
that run under a different registration, and the correcting row names C-24 explicitly**
(`../curriculum_D1/PREREGISTRATION.md` §17).

---

## 9. Memory, and the mechanism this item will NOT use

**Which guards can execute, in one sentence each:**

* **CAN execute — the kernel.** `--memory=6g --memory-swap=6g` (equal: no swap escape) and
  `--oom-score-adj=500`, enforced by the cgroup and not by any process this lane starts.
* **CAN execute — `timeout`.** §8.1, enforced by the kernel's signal delivery.
* **CANNOT execute — the host `MemAvailable` floor.** G-C6's 12 GiB is a **launch condition**,
  checked immediately before the launch and **not** re-checked in flight. **It is record-only in
  flight, it is stated as record-only here, and nothing in this item claims it stops anything.**

**No watcher-script mechanism is used, and this is not a preference:** a watcher start command is
under a permission denial in a peer context. This lane does **not** re-attempt it, does **not** route
around it, and does **not** treat any agent's message as authority to do either (`CLAUDE.md` rule 9).
D1 §8.1 removed A4's and A6's record-only RSS polling subshell for the same reason and this item
keeps it removed. **Consequence, accepted rather than worked around:** peak RSS comes from
`getrusage` inside the process; `/usr/bin/time -v` was **absent in every D1 arm** and is not relied
on; if no figure exists, P13 is **`NOT EVALUATED`**, said plainly, and the kernel cap holds either
way.

**`--rm` is dropped** so the kernel's own verdict survives the container: after the arm ends,
`docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}'` is recorded into the run root's
`ledger.txt`, **and only then** is the container removed explicitly. **`.State.OOMKilled` is the
kernel's own statement and it is what G-C9 grades.**

**Host headroom:** predicted peak 1.70 GiB, cap 6 GiB, launch floor 12 GiB — **10.3 GiB of headroom
above the cap at the floor** on a 30.64 GiB box. **This item is not memory-bound and does not claim
to characterise any memory boundary.**

---

## 10. Environment pinning (L-251) and staging discipline (L-252)

### 10.1 L-251 — uid and run-root mode, pinned in the same sentence

**The container runs as `--user 0:0` (root — the uid every recorded A1 arm on
`dafoam/opt-packages:latest` ran under, D1 arm C included), and in the same breath the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/` is created mode `0777`
(`mkdir -p` immediately followed by `chmod 0777`, asserted with `stat -c '%a'` before the launch), so
that OpenMDAO's `reports/` and `mphys.html` writes cannot hit the `PermissionError` that killed W4 M2
attempt 1 before its primal and burned 20.00 core-min under L-250.**

Asserted from inside the container: `id -u` prints **`0`**. After the arm, `sudo -n chown -R
ubuntu:ubuntu` over the run root so the host-side grading reads work.

### 10.2 L-252 — per-invocation unique names, `test -s`, provenance assert

*"In shared temp, a generic filename IS an accidental handoff."*

* **Every generated file carries a per-invocation stamp** `STAMP := $(date -u +%Y%m%dT%H%M%SZ)_$$` —
  the log (`armCprime_${STAMP}.log`), the container name (`d1c_${STAMP}`), the output
  (`endpoint_shipped_${STAMP}.json`). **No generic filename is written or read anywhere in the
  chain**, with one deliberate exception named here: the **frozen copy** of arm O's artifact is
  called `armO_endpoint_frozen.json`, because it is bound by **md5** and a stamp would weaken, not
  strengthen, that binding — the comparator refuses on md5 before it opens the file.
* **Every producing step writes `<file>.ok.${STAMP}` on its own success, and every consuming step
  asserts `test -s <file> && test -f <file>.ok.${STAMP}` before reading, hashing or committing it.**
  A file that exists but carries no sentinel from **this** invocation is a stale artifact and the
  chain **stops**.
* **`test -s` on every staged file before it is used**, and the three staging md5s re-asserted on the
  staged copy (§10.3).
* **Explicit `&&` chaining throughout; `set -e` is not relied on** — it did not stop the chain that
  earned L-252.
* **The scratchpad is temp only and is never a handoff channel** (`CLAUDE.md` rule 13, L-186).
  **This document cites no scratch path**, and the run root — not the scratchpad — carries every
  artifact `RESULTS.md` will cite.

### 10.3 Staging source, verified at zero compute in the invocation that wrote this section

**Staging source: `/home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched/`, copied and never run in**
— D1 §9.3's own source, on the three identities **re-read from disk at this freeze and all three
matching**:

| file | md5 (re-read at this freeze) |
|---|---|
| `constant/polyMesh/points.gz` | **`38a486d29a540ecd1b06e006e66475e7`** |
| `FFD/wingFFD.xyz` | **`6ddf378b028d03d8a18270488bee1759`** |
| `runScript.py` | **`0557da51f6f179f6de865144343c499f`** |

**The published `W5-regrade` and `P1-a1-np1` trees are copied FROM, never run IN**, so the evidence
behind the regrade and the np=1 A/B pair stays intact. **The `CURRICULUM-D1-a1-constrained-opt` run
root is READ ONLY — this item stages from `W5-regrade`, not from D1's run root, and writes nothing
into D1's run root, not even a `.plant` file** (the dry run in §5 proved that by md5, before and
after). Staging removes any numeric time directory, `processor*` and `reports/`, and restores `0/`
from `0.orig/` (G-C8). The three md5s are re-asserted on the staged copy before the launch.

---

## 11. Run root

**`/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/`** — registered here as
this item's only run root. **Verified NOT to exist at the moment this pre-registration is frozen**:
the check `test ! -e /home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint` is
executed **inside the same shell invocation that writes this file's commit**, and the commit does not
land if it fails. That is `CLAUDE.md` rule 2's condition made checkable — *name the run directory
that does not exist* — and it is the evidence that no compute preceded this freeze.

Artifacts it will hold: `ledger.txt`, `preflight_history.txt`, `armCprime_${STAMP}.log`,
`armO_endpoint_frozen.json`, `endpoint_shipped_${STAMP}.json`, the md5-verified copies of
`d1c_endpoint.py` and `d1c_runScript.py`, the `diff` of §4.2, and the staged case copy.
**`RESULTS.md` cites these paths; this repository document cites no scratch path** (rule 13).

---

## 12. What this item will NOT touch, listed by name

Nothing below is run, staged, queued, costed, edited or prepared by this item.

* **`../curriculum_D1/`'s frozen files** — `PREREGISTRATION.md` (and its Amendments 1–2 and Addenda
  §16, §17), `RESULTS.md`, and the frozen instruments in D1's run root: `d1_fd_endpoint.py`
  (md5 `7e454d2f1830a40086465d9b5c57a941`), `d1_opt_runScript.py`, `d1_run_arm.sh`. **Read only.
  Zero frozen files edited. The one-key defect that blocked arm C is NOT repaired by this item** —
  the supervisor ruled it is not repaired in place, and this item routes around nothing: it registers
  a new instrument instead.
* **D1's run root** `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/` — **read only,
  md5-asserted before and after every read.** No file is created, moved or deleted there.
* **Arm O's PASS and arm E's grade** — untouched. This item produces the SHIPPED row and cannot and
  does not alter the PATCHED row.
* **Anything N=29-gated.** A6 N=29 and the **D464** two-reading gate. **The gate is Sanaa's; it stays
  parked**, and no ratification of any curriculum grants her D464 reading.
* **Tier 6** (D16a CRM full-size, D16b MPhys/TACS, D16c GPU) — **NEEDS COSTING + Sanaa's explicit
  per-item approval**; **GPU spend is OUTSIDE the 2026-08-21 blanket**. Not touched, not costed here.
* **The peer session's claimed items** under the `docs/LAB_STATE.md ## dafoam` claim ledger — the ADF
  sweep 1 (GAMG→PBiCGStab / `useMeanStates`), the B3 RSS item, the A3 rung-1 / rung-3 items. Not
  entered.
* **O3** — **BLOCKED for Sanaa.** Not touched.
* **A shipped-image *optimisation* twin** — deferred by D1 §3.3 at ~19.8 core-min. **Not run, not
  re-priced, not re-argued here.** This item buys the endpoint gradient only.
* **The five upstream DAFoam defect drafts** — all **NOT FILED**, and this item files nothing.
* **`DAFOAM_CHARTER.md` §13's PROPOSAL** — unratified. **Not enforced** (§9 registers the underlying
  facts on their own merits, not as compliance with an unratified clause).
* **The `MemAvailable ≥ 12 GiB` standing floor** — neither touched nor argued (§6 G-C6).
* **`docs/COST_CALIBRATION.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md`,
  `CLAUDE.md`, any charter** — **this lane drafts rows and appends none of them.**

---

## 13. What this item owes on completion

Discharged at completion and **not before**:

1. **`RESULTS.md`** in this directory — every prediction P1–P13 scored **HIT/MISS**, MISSes reported
   as MISSes; the two-row shipped/patched table (R11, never merged); the per-component tables printed
   **in full** and never folded into an aggregate; every gate G-C1…G-C10 with its verdict from the
   fixed vocabulary; the falsifiers F1–F7 scored; the §8.2 cost comparison; and the ledger.
2. **A drafted `docs/COST_CALIBRATION.md` row** in that file's ten-column format, naming **C-24** as
   the row it corrects, id **re-derived at append time from the maximum** — **drafted by this lane,
   landed by the supervisor.**
3. **A drafted `LADDER_A_STATUS.md` row 38b** replacing the current `BLOCKED` cell with this item's
   verdict, its evidence path and its commit — **drafted, not appended by this lane.**
4. **A drafted execution-state ledger row** for `EXPERTISE_CURRICULUM.md` §7, moving D1 from
   `PENDING` on D1-C′ to its closing state, with this file's path and commit in it — **drafted, not
   appended.**
5. **Drafted `L-` / `N-D` / `D` rows** for the supervisor's append (`DAFOAM_CHARTER.md` §11).
   **Numbers re-derived at commit time, in the same shell invocation, from the tail — the MAXIMUM
   existing number, never a count** (`CLAUDE.md` rule 11). **At this freeze the maxima read `L-276`,
   `N-D31`, `D901`, `C-27`; they are re-derived at append and these figures are a snapshot, not a
   reservation.**
6. **Lab-wide propagation** of anything the whole lab must know — routed **through the chief** for
   `CLAUDE.md` or charter-level changes, **never edited by this lane.**

---

## 14. Falsifiers — registered before the run, each with its consequence

| id | falsifier | consequence |
|---|---|---|
| **F1** | the printed `IDWARP_SO_MD5` ≠ `f0fcb488e0e98156575cd19548e91663` | **that arm is VOID**; no figure from it is reported |
| **F2** | the injected design vector does not read back **bit-exactly** equal to arm O's | comparator **refuses**, arm **VOID** — the design point did not land |
| **F3** | the planted-zero control cannot see its plant on any consumed channel | **exit 2**; **no figure computed from a file is reported anywhere** |
| **F4** | arm O's endpoint JSON md5 ≠ `e63f57710cee6e2170f2e9cef39f8b2a` at any point, before or after | **the item is VOID** — the frozen input moved |
| **F5** | any step read from the plan ≠ the literal in `d1c_endpoint.py:FROZEN_STEPS` | comparator **refuses** (`STEP_MOVED`) — a step cannot move |
| **F6** | `\|CD_shipped − CD_armO\| > 5e-6` at the injected design point | the cold-start / design-point identity is broken; **G-C2's toolchain attribution is WITHDRAWN** and the arm's FD column is reported as a **path** finding, not a toolchain one |
| **F7** | the producer's top-level key set ≠ `d1c_endpoint.py:PRODUCER_KEYS` | comparator **refuses** (`KEYSET`) by name — **this is L-273's own defect, and the control that catches it has been dry-run against the real file (§5)** |

---

## 15. Verdict vocabulary

**`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`.** No other word grades
anything in this item, and no adjective softens one. **Shipped- and patched-toolchain verdicts are
reported as two separate rows and are never merged** (R11). A verdict is valid only against a gate or
falsifier registered above, **before** the run.

---

## 16. Launch-gate reading at the moment of this freeze

**Recorded because it is data, not authorisation. It is a snapshot; G-C6 is re-run immediately before
the launch and its reading at that moment is what governs.**

| quantity | reading, **2026-08-24T16:45:23Z** | gate | status |
|---|---|---|---|
| `nproc` | **16** | — | — |
| 1-minute load average | **3.09** | — | — |
| **free_cores** = `nproc − load1` | **12.91** | **≥ 4** | **OPEN** |
| **MemAvailable** | **28,774,628 kB = 27.44 GiB** | **≥ 12 GiB** | **OPEN** |
| `MemTotal` | 32,132,604 kB = 30.64 GiB | — | — |

**Both gate conditions read OPEN at this freeze. NO LAUNCH IS AUTHORISED BY THAT FACT**, and this
reading confers no authority on any later moment: the box is shared, peers commit and launch
constantly, and G-C6 is re-run as its own command immediately before the launch. **Contention is
attributed at grading, never absorbed into the ratio** (§8.2).

---

**END OF PRE-REGISTRATION. Frozen by commit. Nothing below this line existed when the gates,
thresholds, caps, bands and labels above were fixed. NOT FILED ANYWHERE.**
