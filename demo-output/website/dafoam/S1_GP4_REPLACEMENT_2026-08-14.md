# G-P4 replaced — a control that passed the treatment it existed to catch, and what stands in its place

**Executed 2026-08-14, 22:22–23:0x UTC (`date -u`, run). Repo commit anchor at writing: `48d3f05a`.**
**Compute spent: zero.** No solver, no container, no inversion, no scoring call, no network.
Every number below is arithmetic over arrays and log lines written by runs that completed on
2026-08-05 and 2026-08-07. Nothing was submitted, sent or registered, and **nothing here
authorises the 260 core-min purchase, which stays on hold as the owner's decision.**

Reproduction: `S1_gp4_replacement_2026-08-14/scripts/gp4_replacement.py`, full output archived
at `S1_gp4_replacement_2026-08-14/logs/gp4_replacement.out`. One file, numpy only, runs as
`__main__`, imports no local module; `__pycache__` was purged before every execution regardless
(docket D1/D1a — `PYTHONDONTWRITEBYTECODE` does not defeat a stale `.pyc`, it stops writing and
not reading).

---

## 0. What this changes, in one paragraph

`S1_PRIORS_PREREGISTRATION.md` §4's gate **G-P4** is **withdrawn** and replaced by **G-P4a**
(the gradient reproduction control those three legs actually were) and **G-P4b** (a control on
the posterior, whose negative control fires). The pre-registration retains G-P4's original text,
struck, with the falsifying measurement and its commit anchor beside it. The proposal record an
agent would dispatch from is corrected and **verified to load through the real inbox reader**.
The 260 core-min cap is **unchanged** — the replacement fixes the *direction* of the first
Hessian-vector product rather than adding one.

## 1. Frame, stated before any number

Two `.npy` files per run, all four **outside this repository** at
`/home/ubuntu/certonomous-runs/`, invisible to this shell's `grep` (which execs
`ugrep --ignore-files` and honours `.gitignore`); `find` and `/usr/bin/grep` were used
throughout. 21,000 cells.

- Every array is in **DV order**, as written by the run that produced it. **No permutation is
  applied anywhere in this analysis**, so the DV-versus-serial trap that nearly manufactured a
  finding in the 2026-08-14 triage §2.4 has no surface to bite on here. Nothing is compared
  across the two decomposition arms.
- `grad_eval*.npy` is the **raw** `d(varianceU)/d(beta)` (`cbfs_inv/runScript.py:158–160`, read),
  so `g_QoI = λ_QoI·gv` and `g_penalty = 2·λ_L2·(β−1)` (`invert_lbfgsb.py:113`, read). Both
  compositions were re-derived from the drivers, not carried over.
- λ from each run's own driver: inversion `λ_QoI = 65.448114804931393`, `λ_L2 = 1e-4`
  (`runScript_inversion.py:43–44`); reinversion `λ_QoI = 1625.7778891393064`, `λ_L2 = 1e-5`
  (`invert_lbfgsb.py:23–24`).

**Positive control on the reader, before any new arithmetic was trusted.** The reinversion driver
printed `‖g_total‖` into its own history file at every evaluation. Composed from the two arrays,
we return **1.986435e-01** at eval 1 against the archived **1.986e-01**, and **1.592554e-02** at
eval 10 against the archived **1.593e-02** — both to the precision the log carries. That is an
entry-for-entry reproduction of a value the run wrote, and it is what licenses the rest.

## 2. Reproduction of both headline claims

### 2.1 The cosine is fixed by the other two legs, to 2.2e-16

| quantity | recomputed | published |
|---|---|---|
| ratio `r = ‖g_pen‖/‖g_QoI‖` | 0.998441 | 0.998441 |
| cosine `c` | 0.999542138 | 0.999542 |
| rms‖β−1‖ | 0.016502 | 0.016502 |
| `‖g_total‖` | 1.450369e-05 | 1.450369e-05 |

With `ε = ‖g_total‖/‖g_QoI‖ = 3.027748e-02`, solving `ε² = 1 + r² − 2rc` for the cosine returns
**0.999542138470174** against the directly measured **0.999542138470174** — **2.220e-16**. The
triple has exactly one degree of freedom beyond `‖g_QoI‖`, and G-P4 reported it three times.

And the value is forced without knowing anything about the prior: `c ≥ 1 − ε²/(2r)` gives
**0.999540922** against the measured 0.999542138. The published 0.9995 is *"the run converged"*,
restated as an angle.

### 2.2 The prior-as-posterior treatment PASSES G-P4 — this is the whole argument, and it reproduces

Treatment **W is not this document's construction.** It is the specimen written up by the
zero-compute triage in `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` §2.2 at commit `d659ca61`, taken
over verbatim in its own terms: covariance = prior covariance, credible intervals straddling
β = 1 in 100% of cells, informed rank 0, handed the archived β. **Using the finder's specimen
rather than one of our own is deliberate and it is the stronger test** — a wrong treatment built
by the same hand that built the gate tends to be the wrong treatment that gate happens to catch.
The bar the replacement had to clear was therefore fixed by someone else, before the replacement
was designed. It returns **ratio 0.998441, cos 0.999542, rms 0.016502**.

**Relative error 0.0e+00 against the exactly recomputed targets; ≤ 1.2e-05 against the published
rounded ones, into a 1% tolerance. G-P4: PASS.**

*One correction to the record, stated rather than buried.* D67 reports this as 0.0e+00 flat. That
is exactly right against the unrounded targets; against the *published* six-digit targets the
residual is 1.2e-05, which is the rounding of the target and not a disagreement. Three to five
orders of margin either way, and the conclusion is unchanged: **no leg of G-P4 is a function of
any covariance, credible interval or Hessian, so the gate cannot see the defect.**

## 3. The W-3 legality check, which came first

Rule W-3: a pre-registration amendment is legal only while **no compute has run**, checked
against run directories, and the check must be stated in the amendment. It is, in
`S1_PRIORS_PREREGISTRATION.md` §4a. Enumerated:

| # | searched | found |
|---|---|---|
| 1 | the **444** top-level run directories, for `S1-priors` (the name §0.1 pre-declared) | **absent.** Only `S1-cbfs-inversion`, `S1-cbfs-reinversion`, `S1-cbfs-weighted-arm`, `S1-fiml` |
| 2 | `find` over the whole archive for *prior* / *lognormal* / *s1-prior* | 3 hits, all unrelated (one ONERA `_prior_state_backup_20260808`, two IDWarp `kdtree2_priority_queue` modules) |
| 3 | every `ledger.csv` in the archive | **exactly three**, all S1-cbfs, 72 / 41 / 40 lines. §5 requires this item's ledger before any evaluation is billed; there is none |
| 4 | `/usr/bin/grep` over archive csv and `log.*` for `lognormal`, `lam_LN`, `s1-priors`, `log(beta)` | **no match** |
| 5 | anything written in the archive since this file was authored (`-newermt "2026-08-11 16:00"`, no depth limit) | **0 files** |
| 6 | `sudo docker ps` | header row, no containers |
| 7 | the repository, for any S1-priors result record, ledger or field | only the pre-registration itself |

**Verdict: no compute has run. The amendment is legal.** The property L-44's freeze protects —
that a gate could not have been tuned to an answer — is intact, because there is no answer.

## 4. The replacement, and its negative controls firing

Full definitions and bars are in the pre-registration, which is where a gate belongs. What
belongs here is the evidence that it discriminates. Six treatments, scored by both gates:

| treatment | old G-P4 | new G-P4b | A / B / C | λ₁ | `sᵀHs` | variance removed / entitled |
|---|---|---|---|---|---|---|
| **W** prior reported as posterior — *the triage's specimen, `d659ca61` §2.2* | **PASS** | **FAIL** | F/F/F | 0.000e+00 | +3.719e-04 | 0 / 0 |
| **M** plateau β paired with the eval-1 gradient | FAIL | FAIL | F/F/F | 0.000e+00 | +3.719e-04 | 0 / 0 |
| **Z** spectrum read off the prior (eigenvalues ≡ 1) | **PASS** | **FAIL** | F/F/F | 1.000e+00 | +3.719e-04 | 5906 / 1.688 |
| **H** correct spectrum, Hv in the wrong frame | **PASS** | **FAIL** | P/**F**/P | 2.418e+03 | +2.397e-03 | 3.276 / 3.276 |
| **Q** real spectrum, intervals asserted not derived | **PASS** | **FAIL** | P/P/**F** | 2.418e+03 | +7.313e-01 | 1.181e+04 / 3.276 |
| **R** a genuine rank-6 low-rank Laplace posterior | PASS | **PASS** | P/P/P | 2.418e+03 | +1.024e+00 | 3.276 / 3.276 |

**The old gate cannot tell W, Z, Q and R apart — it returns PASS for all four.** The new gate
returns PASS for R alone, and each wrong treatment fails on the leg that names its defect: W and
Z compute no usable curvature, H has the science right and the instrument in the wrong frame,
Q asserts error bars its own reported spectrum cannot support.

Three things about that table deserve saying out loud.

1. **H and Q are not straw men.** H fails **leg B alone** — its spectrum is right and its
   intervals are right, and it is wrong only in the frame its Hessian-vector product was taken
   in. That is the DV-ordering class of mistake this lab has already made. Q fails **leg C
   alone** and is exactly G-P3's *"error bars asserted rather than computed"*, made scoreable.
2. **M is the one treatment the OLD legs catch**, at ratio 0.501974 against 0.998441. That is
   why they are retained as **G-P4a** rather than deleted: they are a sound reproduction control
   on the gradient, they would have caught the mismatched-evaluation error behind the 1.684×
   confusion, and they are not, and cannot be, a control on a posterior. Demoting them to their
   real name is the point.
3. **W is the finder's specimen; Z, H, Q and R are this document's.** The one that decides
   whether the replacement clears its bar — *the treatment that passes G-P4 at 0.0e+00 must fail
   the replacement* — is the one we did not write. The other four probe holes we chose to probe,
   and they are weaker evidence for exactly that reason.
4. **Treatment R is a stand-in and is labelled one.** Its spectrum is anchored at the secant
   Rayleigh quotient measured below, and its per-cell spread is **constructed** from six
   orthonormal directions rather than asserted. That construction is what caught a defect in the
   first draft of leg C: a draft that tightened 2,000 cells by 97% is not a rank-6 posterior at
   all, and the rank bound is what said so. **The controls corrected the gate before the gate
   was published**, which is the only reason this section is worth reading.

**What rank 6 in 21,000 dimensions actually looks like**, computed rather than asserted, because
§5's disclosure deserved a number: the stand-in posterior removes **3.2757 of 11,812.5 units of
prior variance — 0.0277% — and its largest per-cell standard-deviation reduction is 0.0143%.**

### 4.1 Where leg B's external referent comes from

`s = β₁₀ − β₁` and `y_QoI = λ_QoI(gv₁₀ − gv₁)` on the **reinversion**, the run this item
warm-starts from. By the mean-value form of the gradient map `sᵀy = sᵀH̄s` **exactly** for the
segment-averaged Hessian — not a finite difference. Reproduced against D70 entry for entry:

| | recomputed | D70 |
|---|---|---|
| ‖s‖ | 4.312344e+00 | 4.312344e+00 |
| `sᵀy_QoI` — **measurement** | +7.313133e-01 | +7.313133e-01 |
| `sᵀy_penalty` — **identity** `2λ_L2‖s‖²` | +3.719261e-04 | +3.719261e-04 |
| `sᵀy_QoI/‖s‖²` | +3.932573e-02 | +3.932573e-02 |
| ρ, Gaussian prior metric | 1.9663e+03 | 1.966e+03 |

`sᵀy_penalty` is a pure identity in (β, λ_L2). It is **reported here and gated on nowhere**,
which is what rule W-2 prescribes. Sign-randomised null, 200 draws, independent seed: the
measurement is **6.6 sd** from it. Cross-pair negative control (s from one run, y from the
other): **+1.2887e-04** against the matched **+3.9326e-02**, and **+1.7640e-02** against the
matched **+1.2172e-04** — two orders of magnitude wrong in both directions, which is what fires
leg B against treatment H.

### 4.2 Why leg A's bar is 10 and not the measured value

In the **lognormal** prior metric the same Rayleigh quotient evaluates to **2.4175e+03** at
β ≡ 1, **1.3617e+02** at the reinversion eval-10 field, and **6.1638e+01** at its final field.
That 40× spread is driven entirely by the 223 cells pinned at β = 0.2, where
`2λ_LN(1−log β)/β²` is 65× its value at β = 1. **A bar at 2.4e+03 would be a bar on which state
the MAP lands in**, which is not the question. So the bar is 10, the 6×–240× expected margin is
declared in advance rather than claimed afterwards, and what leg A actually discriminates is a
treatment that computed no curvature at all — for which λ₁ = 0 and no margin argument is needed.

This is the honest limit of what can be gated at this stage, and it is stated as one: **the
*scale* of the data-versus-prior curvature is free and on disk; the *decay* across several
eigenvalues, which is what falsifier F2 asks about, still costs gradient evaluations and is not
gateable from the archive.**

## 5. The D41 dispatch path — and a correction to D41 itself

**D41 as filed is discharged, and the surface is broken again in a different way.** D41 (filed
`0b0e002a`, 2026-08-11) reports that the proposal record *"carries the gate definition verbatim
… re-based onto the exact analytic |g_penalty|"*. Checked at HEAD before touching anything:
**it does not.** The same commit that filed D41 corrected the `gate` field to the restored
ratio-and-cosine form. What is live today is therefore the **third** variant — and it is the
form withdrawn above, so an agent dispatching from it would still gate on a control that cannot
fail. The defect is real; D41's description of it is one revision out of date, and that is
recorded rather than quietly fixed.

**Corrected.** The `gate` field now carries G-P4 struck with its commit anchor, then G-P4a and
G-P4b with their bars, their negative controls and the named hole in G-P4b. `cost_basis` had a
line pricing *"the plateau-balance re-basing"* as already done; that re-basing is withdrawn and
buys nothing, so the line is corrected, and the arithmetic is untouched — **260 core-min stands.**

**Proof the record loads, because a record that looks right and does not load is a known failure
mode here.** Executed against the real reader, not asserted:

```
agenda.read_inbox()                    -> 128 records, target present: True
agenda.proposal_violations(raw file)   -> []
agenda.text_violations(gate)           -> []
agenda.text_violations(amendment)      -> []
agenda.premise_violations(raw file)    -> []
```

**Three other records are refused by that same reader and none of them is this one:**
`dafoam-restore-ksp-options-escape-hatch` (file references in `cost_basis` and four citations),
`f5c-unsteady-probe-run` (file reference in `rationale`), and
`test-the-solver-default-relaxation-across-the-family` (six citation violations plus a
`hard_criterion` of `paired-solve`, outside the closed list). They are invisible to the queue
right now. Reported, not repaired — the inbox reader is being worked on by another agent and
this file does not touch it.

## 6. Sibling sweep — the identity test applied to every other gate in reach

| gate | quantity | derivable from its own inputs? |
|---|---|---|
| **G-P1** the λ is derived, not matched | `λ_LN = λ_QoI·σ_d²/(3N·s²)` | **YES — and worse, already published.** Executed: **8.133557e-06** against the **8.1335e-06** §3d prints, and the band floor **2.033389e-06** against the published 2.0334e-06. Four inputs, all supplied by the document. Its stated failure mode, *"a value chosen to match a previous run fails"*, cannot occur because the value is not chosen. **Filed, not withdrawn — the owner's call.** |
| **G-P2** pinned cells fall from 223 to < 60 | a **count** on the run's output field | No. The 8.2× restoring-pull ratio *is* an identity (reproduced: **8.18×**) and is correctly reported rather than gated on. The gate itself bars on a measurement. **Sound.** |
| **G-P3** the posterior is a posterior | deliverable completeness | No. A submission omitting the spectrum fails it. **Sound**, and it is the gate that closes G-P4b's named hole (ii). |
| **G-P4** | — | **YES. Withdrawn above.** |
| **§5 Hv symmetry check**, asymmetry > 5% stops | `v₁ᵀHv₂` vs `v₂ᵀHv₁` | No. Symmetry is exact for the operator but *not* for a finite difference of a truncated adjoint, so it can fail. **Sound.** |
| **F1 / F2 / F3** | interval coverage; spectral decay; window error reduction | No, all three. **Sound.** |
| **G1 / G2 / G1w** (the three completed S1 items) | `J_qoi` from a solve; top-decile geography of β_final | No. Empirically demonstrated: G2 has failed three times (29.0%, 26.9%, 42.7%) and G1w once. **Sound.** |

**One new instance, in the same class as G-P1, in the parallel document.**
`S1_WITH_PRIORS_PREREGISTRATION.md` §7 gate **(a) DERIVATION** commits **3.349e-05** in advance
and says so in its own words: *"Bar met in advance by construction."* That is a self-declared
W-2 identity, and it is the second instance of the same shape as G-P1. Filed together, as one
row, since the fix is one ruling.

**Cross-references, not re-filings.** The section 7 gate **(c)** of that same document bars on
the ratio and on rms‖β−1‖ while its addendum calls the second the cosine — and since
`|g_penalty| = 2λ_L2‖β−1‖₂`, that band is on the identity its own §2a forbids by name. Already
known; not re-filed here. And `B52_RUNG8_PREREGISTRATION.md:39` branches REAL versus REFUTED on
a fit whose inputs are printed seventeen lines above the branch — that is **D66**, it is the
**owner's** verdict, and nothing here withdraws it.

## 7. What this document does not establish

It does not establish that S1-priors should be bought. It does not establish anything about the
posterior — **there is no posterior**, and treatments W, Z, H, Q and R are instruments for
testing a gate, never evidence about nature. It does not price a spectrum: §4.2's numbers are a
*lower bound along one direction*, from one run, and F2's decay question is untouched. It does
not re-scope the experiment, change any other gate, or authorise a core-minute. And it does not
rule on G-P1 or on the parallel document's §7(a) — both are reported for the owner.

## Related

- `ladder-b/S1_PRIORS_PREREGISTRATION.md` §4 (the amended gates) and §4a (the W-3 check)
- `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` §2.2 (D67, the finding) and §2.3 (D70, the secant)
- `agenda/proposals/s1-regularization-chosen-by-prior-theory-with-a-posterior-on-beta.json`
- `docs/DOCKET.md` D41, D66, D67, D70
