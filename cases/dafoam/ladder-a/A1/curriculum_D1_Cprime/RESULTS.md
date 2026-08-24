# Curriculum mini-item D1-C′ — RESULTS: the SHIPPED-image endpoint gradient at arm O's converged design point

**NOT FILED ANYWHERE.** Nothing in this document is filed, sent, emailed, uploaded, posted,
registered, submitted or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.** The five upstream DAFoam defect drafts are
untouched by this item and remain **NOT FILED** drafts.

**Written 2026-08-24T17:25:41Z by a DAFoam lab-lane (Opus), on the dafoam supervisor's launch
authorisation.** Every UTC stamp in this file is `date -u` output read in the shell invocation that
wrote it into the file.

**Graded against `PREREGISTRATION.md` frozen at `c19e0cbc`, and against nothing else.** The freeze
was re-verified by this lane in the launch invocation: the three frozen files on disk are
byte-identical to both their `c19e0cbc` blobs and their current-HEAD blobs —
`PREREGISTRATION.md` `11d6a97f01bff816bc2934ee20d551be`, `d1c_endpoint.py`
`b20c829f7ea4b63d2a9fec5f673d1cbb` (368 lines), `d1c_runScript.py`
`f7f17c64331df596434f19fbee907233` (478 lines). The last two equal the §4.1 literals, and the same
two md5s were re-asserted on the STAGED copies before the container started.
**Zero frozen files were edited. No in-place repair was performed anywhere** (D1 §17's ruling; the
one-key defect that killed D1 arm C is still not repaired, and this item routed around nothing —
it registered a new instrument).

---

## 0. The headline, in four lines

**The SHIPPED image's analytic endpoint gradient is not defective at arm O's converged design
point.** All four components agree with this run's own finite differences to **≤ 0.2551 %** with
**zero sign flips**, every component **GRADED**, so **G-C1 = `PASS`**. The registered verdict
**P5 = `GATE FAIL` is a MISS**, and it is reported as a MISS, not adjusted.

**The shipped and patched analytic gradients are indistinguishable at this design point**: the
largest toolchain difference is `5.16e-08` absolute / `2.80e-06` relative, against a predicted
`6.76e-03` absolute / 640 % relative from the baseline A/B pair — **five orders of magnitude
smaller**, and at the noise floor of a cross-run comparison. **Both registered hypotheses H1 and H2
are falsified; a third behaviour was measured.**

---

## 1. Toolchain — TWO ROWS, NEVER MERGED (G-C2, R11)

**A patched grade does not replace a shipped grade and a shipped grade does not replace a patched
one.** Whether the lab adopts a forked toolchain is Sanaa's call, not this item's, and nothing
below is a recommendation to adopt or to drop either stack.

| row | image | image digest (re-read at launch) | `IDWARP_SO_MD5` printed by the process that loaded the library | np | role | verdict |
|---|---|---|---|---|---|---|
| **SHIPPED — graded by this item** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** (stock) | 1 | the one container this item ran | **`PASS`** (G-C1) |
| **PATCHED — read, never re-run** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` (patched) | 1 | arm O's frozen numbers, consumed from §1 of the freeze | **`PASS`** — arm O's own grade, **unaltered by this item** |

The digest assertion was re-read from `docker images --no-trunc` in the launch invocation and
matched. `nProcs : 1` is in the log and in the run-root `ledger.txt`. `D1C_CONTAINER_UID: 0`
(L-251). **A version string is not an identity** — IDWarp reads `2.6.2` on both stacks; the hash is
the only identity, and the two hashes differ, so the arm demonstrably ran the stock library.

---

## 2. The per-component table — THE PRIMARY REPORT (G-C1), never folded into an aggregate

**Graded step is `s_hi`, inherited from arm O. Band (`DAFOAM_CHARTER.md` §2), applied PER
COMPONENT: `PASS` ≤ 5 % with zero flagged components; `CONDITIONAL` 5–15 %; `GATE FAIL` above 15 %
or on ANY sign flip.** A component is GRADED only where `C_measured ≥ 5` at the graded step AND its
two steps agree within the inherited plateau tolerance of 10 %.

### 2.1 The graded rung, `s_hi`

| component | `s_hi` | **shipped analytic** | **FD, this run** | **rel. err** | sign flip | `C_measured` | plateau | GRADED? | **grade** |
|---|---|---|---|---|---|---|---|---|---|
| `shape[6]` | `3e-4` | `-0.027701622079335214` | `-0.027687022182727498` | **`5.273191e-04` = 0.052732 %** | **False** | `848.7095` | `4.354852e-04` | **yes** | **`PASS`** |
| `shape[1]` | `3e-4` | `0.019112987168878263` | `0.019144296828406637` | **`1.635456e-03` = 0.163546 %** | **False** | `586.8434` | `2.131779e-03` | **yes** | **`PASS`** |
| `shape[5]` | `3e-4` | `0.038866112216096101` | `0.038913886768864731` | **`1.227699e-03` = 0.122770 %** | **False** | `1192.8543` | `1.765068e-03` | **yes** | **`PASS`** |
| `patchV[1]` | `3e-3` | `0.0011232520143767072` | `0.0011261246188285872` | **`2.550876e-03` = 0.255088 %** | **False** | `345.1988` | `4.825646e-03` | **yes** | **`PASS`** |

**Flagged and excluded by name: NONE.** All four components GRADED; `C_measured` ranges 345–1193
against the inherited floor of 5; every plateau is inside the inherited 10 % tolerance by more than
an order of magnitude.

### 2.2 The `s_lo` rung — bought, not absorbed (§4.3), so the shipped row is graded on the same test as the patched row

| component | `s_lo` | **FD, this run** | rel. err vs shipped analytic | sign flip | `C_measured` |
|---|---|---|---|---|---|
| `shape[6]` | `1e-4` | `-0.027674964893868031` | `9.632238e-04` = 0.096322 % | False | `282.7823` |
| `shape[1]` | `1e-4` | `0.019185108244019339` | `3.759222e-03` = 0.375922 % | False | `196.0315` |
| `shape[5]` | `1e-4` | `0.038982572414664185` | `2.987494e-03` = 0.298749 % | False | `398.3199` |
| `patchV[1]` | `1e-3` | `0.001131558897386406` | `7.341096e-03` = 0.734110 % | False | `115.6215` |

**A shipped row graded on a weaker test than the patched row beside it is not a comparison** — it
was graded on the same two-step test, and passed it.

### 2.3 G-C1 verdict

**`PASS`.** Every graded component ≤ 5 % (worst `2.550876e-03` = **0.2551 %**, `patchV[1]`), zero
sign flips on all four, zero flagged components.

**Aggregate, quoted only in the form the freeze permits** and never substituted for the table
above: the **vector-relative error `‖J_an − J_fd‖/‖J_fd‖` over the graded components only** is
**`1.146925e-03` = 0.1147 %**, with **no flagged components to list beside it**. It is not compared
against any published per-component average (`DAFOAM_CHARTER.md` §2).

---

## 3. G-C2 — the §3.3 deliverable: the toolchain comparison, per component, side by side

**This gate is on the instrument, not on the size of a difference.**

| component | **SHIPPED analytic** (this run) | **PATCHED analytic** (arm O, read) | **difference `shipped − patched`** | **relative size** |
|---|---|---|---|---|
| `shape[6]` | `-0.027701622079335214` | `-0.02770157042975438` | **`-5.164958083447857e-08`** | **`1.864500e-06`** |
| `shape[1]` | `0.019112987168878263` | `0.019112933615071107` | **`+5.3553807156242472e-08`** | **`2.801967e-06`** |
| `shape[5]` | `0.038866112216096101` | `0.03886606849182183` | **`+4.3724274270684482e-08`** | **`1.124999e-06`** |
| `patchV[1]` | `0.0011232520143767072` | `0.0011232501148069679` | **`+1.899569739352569e-09`** | **`1.691137e-06`** |

**G-C2 = `PASS`.** All four components are printed side by side with the difference and its relative
size; no aggregate is substituted for the table; the design point is proved identical (F2 and F6
both clear, §6); and neither row is described as replacing the other. **D1 §3.3's bought deliverable
is discharged.**

### 3.1 What this table may and may not be read to say — the resolution limit, stated as a limit

**The measured differences are at or below this comparison's own noise floor, so they are an UPPER
BOUND, not a resolved defect.** Three measured figures set that floor, and they are of the same
order as the differences themselves:

* the two runs' converged primals differ by `|CD_shipped − CD_armO| = 9.229353e-09` (§6, P11) —
  cold-staged single solve here against arm O's warm major-11 endpoint;
* the inherited primal noise floor is `η = 1.957349804806996e-08`;
* **`patchV[1]` — the component that never crosses `warpDeriv` (identity gate IG-2), and which the
  baseline A/B pair measured *bit-identical* across the two images — nevertheless differs here by
  `1.899570e-09` (`1.691137e-06` relative).** That difference **cannot** be a warp-derivative defect;
  it is the cross-run primal-state difference showing through. It is therefore the cleanest available
  measurement of this comparison's floor, and it sits at the same `~1e-6` relative level as the three
  `shape` differences.

**The defensible statement is therefore: `|J_shipped − J_patched| ≤ 5.2e-08` on every component at
this design point, i.e. `≤ 2.8e-06` relative — indistinguishable from zero at this instrument's
resolution.** The signs and magnitudes of the individual `~1e-8` entries are **not** claimed as
measurements of a defect, and no mechanism is inferred from them.

---

## 4. G-C3 — cross-run FD control: this run's FD against arm O's FD at the same steps

**Band `≤ 0.5 %` on all four components at both rungs.**

| component | `s_lo` rel. diff | `s_hi` rel. diff |
|---|---|---|
| `shape[6]` | **`8.406820e-06` = 0.00084 %** (worst of the eight) | `4.761761e-11` |
| `shape[1]` | `9.946234e-12` | `1.600825e-11` |
| `shape[5]` | `3.648998e-11` | `1.292777e-11` |
| `patchV[1]` | `1.579030e-10` | `2.772786e-11` |

**G-C3 = `PASS`.** Worst `8.406820e-06` = **0.00084 %**, against a 0.5 % band — inside it by a
factor of ~595, and inside the P7 point prediction (< 0.05 %) as well. **Seven of the eight agree
to `1e-10` or better, which is far tighter than A4 §3.2's measured 0.183 % path-dependence would
have allowed for.** G-C2's attribution is therefore **NOT capped by G-C3**; the cap that does apply
is the resolution limit of §3.1, which is a different and smaller thing.

---

## 5. G-C4 — the trivial baseline: the same probe at a deliberately wrong step

`shape[6]` at `step = 1e-8`, on the shipped stack, restored by SET without solving, exactly as the
graded probes.

| quantity | this run (SHIPPED) | arm O (PATCHED) |
|---|---|---|
| FD @ `1e-8` | `0.21984667194357987` | `0.21984666830066057` |
| analytic | `-0.027701622079335214` | `-0.02770157042975438` |
| **rel. err** | **`1.1260042821409841` = 112.6004 %** | `1.126004049294347` = 112.6004 % |
| **sign flip** | **TRUE** | TRUE |

**G-C4 = `PASS`.** The wrong step does **not** pass (112.6004 % ≫ 5 %, with a sign flip), so
**G-C1's `PASS` is NOT withdrawn**: the gate was measuring what it claimed. The instrument can still
return a large number on the very stack that passes at the registered step — which is the whole
point of the control, and it is the third independent execution of this precedent on this case
(`../A_stepsize_study.md` 94.95 %; `../reverify_patched_idwarp_np1/RESULTS.md` §4.3 132.75 %; arm O
112.6004 %).

---

## 6. G-C5 — the planted-zero control (`CLAUDE.md` rule 3, L-273 repaired), run LIVE in the container

**Run inside the container, against the run root, BEFORE the design point was touched.** All three
sub-controls returned OK; a refusal would have exited 2 and no figure computed from a file would
appear anywhere in this record.

| sub-control | result | evidence |
|---|---|---|
| **kernel selftest** | `pass: true` | cubic derivative `12.00000001000845` vs `12.0`, rel. err `8.340374317109914e-10`, 2 calls |
| **plant, all six consumed channels** | **OK, `pass: true`** | `PLANT = 1.234e-03` seen on **every** channel — `shape`, `patchV`, `plan`, `eta`, `J_adj`, `fd` — worst read-back residual `2.3852447794681098e-18` (`J_adj`); `src_md5_before = src_md5_after = e63f57710cee6e2170f2e9cef39f8b2a`, `src_unchanged: true` |
| **negative control** (a deliberately blind reader) | **OK, refused** `PLANTED_ZERO` | all six channels read `false`, residual exactly `0.001234` on each — the control can fail |
| **key-set control** (L-273's own defect replayed: `CD` → `CD_final`) | **OK, refused** `KEYSET` | refused **by name** with `missing: ["CD"]`, `extra: ["CD_final"]` — the exact mismatch that killed D1 arm C at 14 s is now caught by a named refusal instead of a `KeyError` inside a consumer |

**G-C5 = `PASS`.** **The zero is planted:** the reader was shown able to see a non-zero on every
channel it consumes, in the real file the real producer wrote, and shown able to refuse.

---

## 7. Every gate, with its verdict

| gate | what it tests | verdict | figure |
|---|---|---|---|
| **G-C1** | shipped analytic vs this run's own FD, per component, at `s_hi` | **`PASS`** | worst 0.2551 %, zero flips, zero flagged, all four GRADED |
| **G-C2** | the §3.3 deliverable: two rows, never merged | **`PASS`** | table §3; F2 and F6 clear; neither row replaces the other |
| **G-C3** | this run's FD vs arm O's FD, same steps, both rungs | **`PASS`** | worst `8.406820e-06` = 0.00084 % vs the 0.5 % band |
| **G-C4** | trivial baseline at `1e-8` | **`PASS`** | 112.6004 % with a sign flip; G-C1 not withdrawn |
| **G-C5** | planted zero, negative control, key-set control | **`PASS`** | §6; all three OK, run live in the container |
| **G-C6** | launch gate, own command, read before launch | **`PASS`** | `2026-08-24T17:19:34Z … nproc=16 load1=4.83 free_cores=11.17 memavail_GiB=27.50 gate=OPEN` — appended to `preflight_history.txt`, read before the launch command was issued, never polled by a background process. **One reading, one launch; no waiting, no departure** |
| **G-C7** | image identity | **`PASS`** | `IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663`, printed from inside the process that loaded the library; `nProcs : 1` |
| **G-C8** | cold start, verified BEFORE the launch | **`PASS`** | run root verified ABSENT immediately before `mkdir`; staged tree carried no `processor*`, no `reports/`, no numeric time directory; `0/` restored from `0.orig/` and **md5-equal on every one of the seven fields** (`U epsilon k nuTilda nut omega p`) |
| **G-C9** | memory envelope | **`PASS`** | peak **1.6813 GiB** (`getrusage`; `/usr/bin/time` **absent** in the image, as in every D1 arm) against cap **6 GiB** and predicted 1.70 GiB. `docker inspect` → `ExitCode 0`, **`OOMKilled false`** — the kernel's own statement, read before the container was removed. **Headroom was not exhausted, and no memory boundary is characterised by this item** |
| **G-C10** | cost ceiling 10.0 core-min | **`PASS`** | **1.483 core-min**, 14.8 % of the ceiling; no overrun, so nothing was stopped |

**Every gate registered in the freeze returned a verdict. None was skipped, none was softened.**

---

## 8. Falsifiers F1–F7, scored

| id | falsifier | fired? | evidence |
|---|---|---|---|
| **F1** | printed `IDWARP_SO_MD5` ≠ `f0fcb488…` | **NO** | printed value equals the registered literal exactly |
| **F2** | injected design vector does not read back **bit-exactly** | **NO** | `D1C_DV_READBACK_EXACT True` — all 8 `shape` and both `patchV` entries bit-exact |
| **F3** | planted-zero control cannot see its plant on any consumed channel | **NO** | all six channels seen; §6 |
| **F4** | arm O's endpoint JSON md5 ≠ `e63f5771…` at any point, before or after | **NO** | asserted at four separate points — host pre-launch, inside `planted_zero_control` before and after the plant, on the frozen copy in the container, and host post-launch — all `e63f57710cee6e2170f2e9cef39f8b2a`. **D1's run root was mounted `:ro` as a single file and nothing was written into it** |
| **F5** | any step read from the plan ≠ the `FROZEN_STEPS` literal | **NO** | no `STEP_MOVED` refusal; all eight steps matched (`shape[*]` `1e-4`/`3e-4`, `patchV[1]` `1e-3`/`3e-3`) |
| **F6** | `\|CD_shipped − CD_armO\| > 5e-6` | **NO** | `9.229353e-09`, **541× inside** the 5e-6 falsifier bound. G-C2's attribution stands |
| **F7** | producer's top-level key set ≠ `PRODUCER_KEYS` | **NO** | `assert_keys` passed on the real artifact; and the control that would catch it was **proved live** by the key-set sub-control (§6) |

**No falsifier fired. The arm is not void.**

---

## 9. Predictions P1–P13, every one scored

**Registered before the run so the verdict could not be chosen after the number was seen. Six MISS,
seven HIT — and the MISSes are the result.**

| id | prediction | band (HIT if inside) | **measured** | **score** |
|---|---|---|---|---|
| **P1** | `shape[6]` rel. err @ `3e-4` = 24.35 %, no flip | [10 %, 60 %], flip FALSE | **0.052732 %**, flip FALSE | **MISS** — inside on the flip, three orders below the band |
| **P2** | `shape[1]` = 12.19 % | [4 %, 30 %] | **0.163546 %** | **MISS** — below band |
| **P3** | `shape[5]` = 2.80 % | [0.5 %, 12 %] | **0.122770 %** | **MISS** — below band |
| **P4** | `patchV[1]` = 0.2553 % (the control component) | [0.15 %, 0.45 %] | **0.255088 %** | **HIT** — to four significant figures |
| **P5** | **the SHIPPED row's G-C1 verdict = `GATE FAIL`**, driven by `shape[6]` > 15 %, zero sign flips | `GATE FAIL` | **`PASS`** (zero sign flips: true) | **MISS** — **graded as registered; the verdict was not adjusted to fit** |
| **P6** | toolchain difference per component | `shape[6]` [+2e-3,+2e-2]; `shape[1]` [−8e-3,−5e-4]; `shape[5]` [−5e-3,−1e-4]; `patchV[1]` \|Δ\|/\|J\| < 1e-6 | `shape[6]` **`−5.164958e-08`**; `shape[1]` **`+5.355381e-08`**; `shape[5]` **`+4.372427e-08`**; `patchV[1]` rel **`1.691137e-06`** | **MISS on all four** — three outside their bands by ~5 orders (and two with the sign reversed); `patchV[1]` misses its `< 1e-6` band marginally at `1.69e-6`, which §3.1 attributes to the cross-run primal-state floor, not to the image |
| **P7** | this run's FD vs arm O's FD, 4 components × 2 rungs, < 0.05 % | ≤ 0.5 % | **worst 0.00084 %** | **HIT** — band and point prediction both |
| **P8** | two-step plateau, all four ≤ 1 % | ≤ 10 % | **worst 0.482565 %** (`patchV[1]`) | **HIT** — band and point prediction both |
| **P9** | `C_measured` at the graded step: 848.7 / 586.8 / 1192.9 / 345.2 | within 5 % of each | **848.7095 / 586.8434 / 1192.8543 / 345.1988** | **HIT** — all four within 0.01 % |
| **P10** | trivial baseline 109.5 %, flip TRUE | > 50 % (reported [50 %, 10000 %]) | **112.600428 %**, flip TRUE | **HIT** |
| **P11** | `\|CD_shipped − CD_armO\|` < 1e-8 | ≤ 5e-6 absolute | **`9.229353e-09`** | **HIT** — band and point prediction both |
| **P12** | cost = 1.62 core-min | ≤ 3.24 (HARD ≤ 10.0) | **1.483 core-min** | **HIT** |
| **P13** | peak RSS = 1.70 GiB | ≤ 2.5 GiB | **1.6813 GiB** (`getrusage`; `/usr/bin/time` absent, so P13 is evaluated by the registered fallback and is **not** `NOT EVALUATED`) | **HIT** |

### 9.1 The MISSes are the finding, and both registered hypotheses are falsified

The freeze registered a two-hypothesis discriminator on `shape[6]` (§7 of `PREREGISTRATION.md`):
**H1**, the absolute defect `+6.756380e-03` carries to the endpoint unchanged (⇒ 24.35 %); **H2**,
the *relative* error carries unchanged (⇒ ≈ 640 % **with** a sign flip). `shape[6]`'s `|J|` grew 26×
between baseline and endpoint, so the two differ by a factor of 26 there and `shape[6]` was the
registered discriminator.

**Measured: `5.16e-08` absolute, `0.0527 %` relative, right sign.** H1 is out by a factor of
**1.3 × 10⁵**; H2 is out by a factor of **1.2 × 10⁴**. **Neither hypothesis survives, and the
measurement is not between them — it is five orders below both.**

**The baseline defect is real and is not in dispute.** `../reverify_patched_idwarp_np1/RESULTS.md`
§4.1 measured, at the **undeformed** design point on the same case at np=1, shipped `shape[6]`
analytic `+5.69074e-03` against an FD of `-1.05312e-03` — **640.3696 % with a sign flip** — while
§4.2's patched row gave `-1.06564e-03`, 1.1888 %, right sign; and §3 measured **8 of 8 raw `Jfd`
components bit-identical across the two images**, so the FD side did not move. Two md5-identified
images, one case, np=1 in both.

**So the honest statement of the finding is a conjunction of two measurements, not a mechanism:**

> On the A1 NACA0012 case at np=1, the stock IDWarp analytic `dCD/dshape` is **catastrophically
> wrong at the undeformed baseline design point** (640 % and sign-flipped at index 6) and
> **indistinguishable from the patched result at arm O's converged, deformed design point**
> (≤ 2.8e-06 relative, all four probed components, right signs). **The defect is design-point
> dependent.**

**What this item does NOT establish, said plainly.** It does not identify *why*. One candidate
worth registering — and it is a **hypothesis this run did not test**, offered only so the next
item can be pre-registered against it — is that the defect lives in a degenerate branch of
`getRotationMatrix3d`'s reverse mode that is reached when the local warp rotation is at or near
zero, which is exactly the undeformed baseline and is not the deformed endpoint. **That is
speculation until a registered arm measures the defect against rotation magnitude.** The
sign-and-magnitude pattern of the individual `~1e-8` differences in §3 must **not** be read as
support for it: §3.1 shows those entries sit at the cross-run noise floor, and `patchV[1]` — which
cannot carry a warp-derivative defect at all — shows a difference of the same relative size.

**What the finding does bear on, and what it does not.** It bears on the *scope* of the patched
toolchain's value: the evidence for the patch is at the undeformed point, and this item found no
resolvable difference at a converged one. **It is not a recommendation to adopt, drop or narrow
either stack** — R11 is untouched, both rows stand separately, and the adoption question is Sanaa's
(`CLAUDE.md` FIRST-ACTION RULE, reserved matters). **Arm O's `PASS` and arm E's grade are
untouched by this item.**

### 9.2 `ETA_CPRIME_OBSERVED` — bought for nothing, reported, and honestly qualified

`d1c_endpoint.py:eta_from_series` under D1 Amendment 2 §A2.2's registered definition, applied to
this arm's own cold primal, which printed six `CD` samples at `printInterval 10`:

```
0.6225258675378997, 0.01836922739337122, 0.01755904457374216,
0.01752931311712901, 0.01752796723993185, 0.01752790908388821
```

**`ETA_CPRIME_OBSERVED = 8.413183094830093e-04`** (peak-to-peak of the last five).

**It sizes nothing, selects nothing and grades nothing** (every step in this item is inherited), and
it is reported with the caveat that makes it honest: **this cold primal converged in ~60 iterations,
so the last five printed samples span the convergence transient rather than a plateau.** The figure
is therefore **not** a noise floor — it is 4.3 × 10⁴ times the inherited
`η = 1.957349804806996e-08`, which is itself a plateau measurement from arm E run 2. **D1 §5.3's
standing limitation — that the endpoint's own noise floor has never been measured — is NOT
discharged by this number, and this record does not upgrade an observation into a measurement.**
A future item wanting the endpoint noise floor must run the primal past convergence with a
plateau of printed samples; that is not bought here.

---

## 10. Cost — the §8.2 calibration deliverable (`CLAUDE.md` rule 12; Sanaa's 2026-08-23 directive)

`cost_basis: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.` The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); **every dollar
figure in this record is DERIVED, not measured.**

| | core-min | $ DERIVED |
|---|---|---|
| **REGISTERED PRICE (point)** | **1.62** | $0.0013851 |
| contingency band | 3.24 | $0.0027702 |
| **ACTUAL, MEASURED** | **1.483** (89 s wall × 1 rank ÷ 60, from the run-root `ledger.txt`) | **$0.0012680** |
| HARD CEILING | 10.0 | $0.00855 |

**Ratio actual/predicted = 0.915× ; 0.148× of the hard ceiling. No overrun; nothing was stopped.**

**Gross or cleaned:** **= gross, 1.483 core-min.** The 3600-s stall rule matches no row — the single
row's wall is 89 s.

### 10.1 Gap attribution — contention / waste / misprediction, kept separate

**WASTE: 0.000 core-min, named separately and never folded into the ratio or into either of the
other two.** One staging, one gate reading, one launch, one container, `rc=0`, no abort, no
re-stage, no re-run, no voided arm, no second budget. **The `s_lo` rung is a bought instrument
(§4.3), not waste** — registered at ≈ 0.37 core-min and **measured at ≈ 0.35 core-min** (21 s of
`ClockTime` across the four `s_lo` pairs), 23.6 % of actual spend, and it is what let the shipped row
be graded on the same two-step plateau test as the patched row.

**CONTENTION: not separately measured, and no penalty is claimed.** The gate read `load1 = 4.83` on
16 cores with 27.50 GiB available, and the container was pinned `--cpus=1`, so the box was quiet and
the arm was not competing for its single core. Contention cost **schedule only, and here not even
that**: the gate opened on the first reading, so unlike D1 arm C (which waited 73 s across two
`NOT_OPEN` readings at 0.000 core-min) this arm waited zero.

**MISPREDICTION: −0.137 core-min (−8.5 %), and it is the sum of two large, opposite, individually
nameable errors that nearly cancelled.** Measured from the log's own `ClockTime` stamps:

| stage | §8 predicted wall | **measured wall** | error |
|---|---|---|---|
| container start, imports, mesh read, problem build, **plus** JSON write / `chown` / inspect / teardown | 14 + 5 = **19 s** | **15.86 s** (89 s outer − 73.14 s internal `D1C_WALL_S`) | −3.14 s |
| zero-compute controls | < 1 s | sub-second | — |
| **one cold primal at the injected design** | **20 s** | **≈ 6 s** | **−14 s** |
| **one adjoint** | **9 s** | **≈ 23 s** | **+14 s** |
| 16 warm perturbed primals | 45 s | ≈ 42 s | −3 s |
| trivial baseline, 2 warm primals | 4 s | ≈ 2 s | −2 s |
| **TOTAL** | **97 s** | **89 s** | **−8 s** |

**The calibration content, and it is transferable:** the adjoint anchor was taken from arm O's log
at elapsed `273.19 s → 281.77 s = 8.58 s` — a **mid-run** adjoint on a case whose
`dRdWColoring_1.bin` was already on disk. **This arm is cold by construction (G-C8), so its first
adjoint had to compute the colouring, and the log states the price directly:
`Calculating dRdW Coloring... Completed! 14.47 s`.** That single one-time cost is the whole +14 s,
measured and not inferred. **Rule candidate for the next DAFoam pre-registration: an adjoint on a
COLD-staged case is priced as `mid-run adjoint anchor + the colouring cost`, and the colouring is
read from a log line, not estimated — a mid-run anchor applied to a cold arm under-prices the first
adjoint by roughly 2.5× on this case.** In the opposite direction, the cold primal at a *converged*
design point is much cheaper than the 20 s registered for "the deformed, cambered design point":
the injected vector is already the optimum, so the primal converges in ~60 iterations from `0/`.

**Both errors are named because they cancelled.** The 0.915× headline ratio is the least
informative number in this section: it would have read ~0.77× or ~1.06× had either error occurred
alone, and a future estimate that copies the headline without the two stage rows will inherit both
mistakes.

### 10.2 Drafted row for `docs/COST_CALIBRATION.md`

**Drafted by this lane; the id is re-derived from the file's tail — the MAXIMUM existing number,
never a count (`CLAUDE.md` rule 11) — inside the shell invocation that appends it.** The freeze
recorded the maximum at `C-27` as a snapshot; by the time this ran, peers had landed `C-28` and
`C-29`, so the drafted id is **`C-30`**, and it is **re-derived again at append time**. The row
names **C-24** as the row it corrects, per `../curriculum_D1/PREREGISTRATION.md` §17 and C-24's own
closing sentence *"a correcting row is owed if arm C later runs."*

---

## 11. Ledger — the artifacts this record cites, by absolute path

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D1Cprime-a1-shipped-endpoint/`
(created mode 0777 at `2026-08-24T17:17:55Z`, verified ABSENT immediately before `mkdir`).
**This record cites no scratch path** (`CLAUDE.md` rule 13, L-186).

| artifact | absolute path | md5 / note |
|---|---|---|
| arm log | `…/armCprime_20260824T171942Z_1479979.log` | 2,420 lines; sentinel `.ok.20260824T171942Z_1479979` |
| arm output | `…/endpoint_shipped_20260824T171942Z_1479979.json` | sentinel `.ok.20260824T171942Z_1479979` |
| grading output | `…/GRADE_20260824T171942Z_1479979.json` | produced by `…/d1c_grade.py`, which imports the **staged frozen comparator** and asserts its md5 |
| frozen input copy | `…/armO_endpoint_frozen.json` | `e63f57710cee6e2170f2e9cef39f8b2a` — bound by md5, not by stamp (§10.2's one registered exception) |
| run ledger | `…/ledger.txt` | wall, ranks, core-min, `docker inspect` exit/OOMKilled, uid, `IDWARP_SO_MD5`, `nProcs`, F4 before/after |
| launch gate history | `…/preflight_history.txt` | the single `gate=OPEN` reading at `2026-08-24T17:19:34Z` |
| staged comparator | `…/armCprime/d1c_endpoint.py` | `b20c829f7ea4b63d2a9fec5f673d1cbb` — re-asserted on the staged copy |
| staged run script | `…/armCprime/d1c_runScript.py` | `f7f17c64331df596434f19fbee907233` — re-asserted on the staged copy |
| §4.2 diff | `…/d1c_script.diff` | **2 hunks, `232,238c232,369` and `240,249c371,475`**, both inside the task chain; `head -231` md5 `b34aa99e2f6f1c95b31a49b01070844d` equal on both files |
| stage / launch / gate scripts | `…/d1c_stage.sh`, `…/d1c_run_arm.sh`, `…/d1c_preflight.sh` | written by this lane in the run root; not frozen instruments and not claimed as such |
| **frozen inputs, READ ONLY** | `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO/endpoint_20260824T160552Z_1399954.json` | `e63f57710cee6e2170f2e9cef39f8b2a`, **unchanged before and after** — mounted `:ro` as a single file; **nothing was written into D1's run root, not even a `.plant`** |
| | `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO_20260824T160553Z_1400030.log` | `64bee1631d28ab07973e56ec7e1f4bf3`, read only |
| staging source, copied FROM, never run IN | `/home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched/` | `points.gz 38a486d29a540ecd1b06e006e66475e7`, `wingFFD.xyz 6ddf378b028d03d8a18270488bee1759`, `runScript.py 0557da51f6f179f6de865144343c499f` |

**Run row:** `ARM=armCprime IMG=dafoam/opt-packages:latest TASK=d1c_shipped rc=0 wall_s=89 ranks=1
core_min=1.483 inspect(exit,oomkilled)=[0 false] maxrss_GiB=1.6813 timeout_s=330`.

---

## 12. What departed from the freeze — nothing that touches a gate, and it is listed anyway

1. **Nothing was edited in any frozen file, and no gate, threshold, band, cap or label was changed.**
   The comparator that graded is the committed blob, proved by md5 at four points.
2. **The `timeout` bound was not approached**: 89 s against the registered 330 s, so the L-250 loss
   bound of 5.50 core-min was never in play.
3. **Three scripts not named in §11 of the freeze were written into the run root by this lane** —
   `d1c_stage.sh`, `d1c_run_arm.sh`, `d1c_preflight.sh`. §11's list is of artifacts the run root
   *will hold*, not an exhaustive inventory, and the freeze registers the launch conditions these
   implement (§6 G-C6/G-C8, §9, §10) without naming a file. **They are not frozen instruments, they
   graded nothing, and no number in this record depends on them** beyond the wall clock in
   `ledger.txt`. Disclosed rather than left to be noticed.
4. **`d1c_grade.py`** was written by this lane to render the tables above. It **imports the staged
   frozen comparator and asserts its md5 before use**, and takes every band, tolerance, floor and
   grading function from it (`grade`, `eta_from_series`, `PLATEAU_TOL`, `CMIN`, `FROZEN_STEPS`,
   `NAMED`, `ARMO_JSON_MD5`). **It defines no threshold of its own.** The per-component rel. errs,
   plateaus, `C_measured`, `graded` flags and grades it reports were computed **inside the container
   by the frozen comparator** and are read from the arm's own JSON, not recomputed.
5. **`ETA_CPRIME_OBSERVED` is reported with a qualification the freeze did not anticipate** (§9.2) —
   the registered definition was applied unchanged; what is added is the honest statement that the
   available samples are a transient, not a plateau. **It grades nothing, so no gate is affected.**

---

## 13. Candidate records — DRAFTED for the supervisor's append, appended by no one here

**This lane appends nothing to `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md`,
`LADDER_A_STATUS.md` or `EXPERTISE_CURRICULUM.md`.** Numbers below are snapshots read at drafting
time and **must be re-derived from the tail — the MAXIMUM existing number, never a count — in the
same shell invocation that appends** (`CLAUDE.md` rule 11).

**`L-` candidate (max at drafting: `L-276`).** *A defect measured at one design point is a
measurement at that design point, not a property of the code.* The stock IDWarp warp-derivative
error on A1 NACA0012 at np=1 is 640 % with a sign flip at the **undeformed** baseline and
**≤ 2.8e-06 relative — unresolvable — at arm O's converged design point.** Two md5-identified
images, one case, both measurements pre-registered. Predictions built by carrying a defect from one
design point to another (H1: absolute defect carries; H2: relative error carries) were wrong by
10⁴–10⁵. **Before extrapolating any measured defect to a new operating point, register the
extrapolation as a falsifiable hypothesis with a discriminator — this item did, and both
hypotheses died.**

**`N-D` candidate (max at drafting: `N-D31`).** *An adjoint on a COLD-staged DAFoam case buys the
`dRdW` colouring; a mid-run adjoint anchor under-prices it.* Measured on A1 NACA0012, np=1,
`dafoam/opt-packages:latest`: mid-run adjoint 8.58 s (arm O) vs cold first adjoint ≈ 23 s, of which
**14.47 s is `Calculating dRdW Coloring`, stated by the log itself**. Conversely, a cold primal at
an already-converged design point is ~3× cheaper than one at an arbitrary deformed point
(≈ 6 s vs 20 s registered).

**`N-D` candidate (second).** *A cross-run analytic-gradient comparison between two containers has a
resolution floor set by the primal state difference, and `patchV` measures it.* Here
`|CD_A − CD_B| = 9.23e-09` between a cold single solve and a warm major-11 endpoint at the same
design vector, and the `patchV[1]` row — which never crosses `warpDeriv` (IG-2) and was
bit-identical across images at baseline — differed by `1.69e-06` relative. **Any claimed
toolchain difference below ~`1e-5` relative in such a comparison is at the floor and must be
reported as an upper bound.**

**`D` candidate (max at drafting: `D901`).** *The design-point dependence of the IDWarp rotation
defect is unexplained and is worth one pre-registered arm.* A cheap discriminator exists: run the
shipped-vs-patched analytic A/B at a **sequence of FFD deformation magnitudes** between the
undeformed baseline and arm O's endpoint, and measure where the 640 % collapses to noise. Cost is
of the order of this item per point. **Not costed, not registered and not launched here.**

**`LADDER_A_STATUS.md` row 38b (drafted, replacing the current `BLOCKED` cell):**
`38b | SHIPPED-image endpoint gradient at arm O's design point (curriculum D1-C′) | PASS (G-C1; all four components ≤ 0.2551 %, zero sign flips, all GRADED) | cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md | <this commit> | 1.483 core-min`

**`EXPERTISE_CURRICULUM.md` §7 execution-state row (drafted):** D1 moves from `PENDING` on D1-C′ to
**closed** — D1 §3.3's bought deliverable (the toolchain comparison) is **discharged by G-C2 =
`PASS`**, the shipped row is graded `PASS`, and the item's registered point prediction P5 is a
**MISS**, reported as one. Path `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md`,
pre-registration frozen `c19e0cbc`, this commit.

**Lab-wide propagation:** nothing in this item requires a `CLAUDE.md` or charter change, so nothing
is routed to the chief. **R11 is untouched; the adoption question is Sanaa's and stays parked.**

---

**END OF RESULTS. The pre-registration above the freeze line fixed every gate, band, cap and label
before this arm ran; six of thirteen predictions missed and are reported as misses. NOT FILED
ANYWHERE.**
