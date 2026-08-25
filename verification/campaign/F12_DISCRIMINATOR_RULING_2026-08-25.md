# F12 — THE ENERGY-BOUND DISCRIMINATOR, RULED: **BOTH LEVERS ANSWERED, AND THE ONE I THOUGHT WORTH TRYING WAS HOLDING THE RUN TOGETHER**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **Grades nothing.** Rung 1 stays `NOT A RESULT`; rungs 2–5 stay
`BLOCKED` on the two grounds in `F12_CRASH_TRIAGE_ROUND2_2026-08-25.md` §7,
untouched by this probe.

Evidence: `54acad46` (pre-registration, **committed alone before any compute**),
`e46d844c` (its own ADDENDUM 1), `79997b54` (all three arms), `1297c06f` (cost row
**C-88**). All numbers from
`verification/runs/F12_runs/energy_bound_discriminator_2026-08-25/evidence/discriminator.json`.

---

## 1. THE RESULT

| | arm 0 control | arm 1 scheme | arm 2 relaxation |
|---|---|---|---|
| `i_gen` — first `T_max` > 342.331 K | 19 | **53** | **9** |
| `S20` — span ÷ dynamic temp at it 20 | 3.282372 | **2.770126** (−15.6 %) | **8.812329** (+168.5 %) |
| `T_max` over the run | 608.505 | **431.557** | 509.016 |
| rc / last iteration | 134 / 148 | **0 / 148** | **134 / 53** |
| classification | *(control)* | **MITIGATED** | **EXONERATED** |

**`REMOVED` was reachable under the frozen rule and no arm reached it. Neither
lever removes the excursion.**

## 2. THE SHARPEST RESULT IS THE ONE THAT WENT AGAINST MY TRIAGE

**My triage named the `rho`/`p` relaxation mismatch (0.05 against 0.3, 6:1) as
worth testing, reasoning that if `p` advances six times faster than `rho`, `T`
recovered through the thermodynamics inherits the mismatch.**

**Matching them makes it DRAMATICALLY WORSE.** Ceiling breach moves from iteration
19 to **9**; the run aborts at **53** with `T = −124.6 K`; `S20` rises **+168.5 %**.

> **THE HEAVY `rho` UNDER-RELAXATION WAS NOT CAUSING THE EXCURSION. IT WAS HOLDING
> THE RUN TOGETHER.**

**My reasoning was not merely unsupported — it was inverted**, and the arm that
established it cost **1.2 core-minutes**. **A candidate is not refuted by argument;
it is refuted by the arm.** I stated in the triage that no mechanism was claimed
and that the arms would discriminate rather than crown a winner. **That discipline
is the only reason this reads as a result instead of a retraction.**

## 3. AND THE ARM I EXPECTED TO BE INERT WAS NOT

The lane predicted (`P1`) that the scheme lever would be inert, on the strength of
**my** dictionary reading. **`P1` FAILED.** First-order implicit energy convection
pushes the first ceiling breach **19 → 53** and drops `S20` by **15.6 %**.

**My dictionary reading is CONFIRMED, not impeached** — `limited` is a
`gradSchemes` entry resolving to `cellLimited Gauss linear 1`, and `bounded` is
applied. **What is impeached is the inference that a WEAK candidate is an INERT
one.** Those are different claims and the lane names the distinction correctly
against itself.

## 4. **ARM 1'S `rc = 0` IS NOT SURVIVAL, AND THIS IS THE FINDING WORTH MORE THAN EITHER ARM**

Arm 1 stopped because **148 is the `endTime` the probe itself registered**.
`SIMPLE solution converged` never appears; minimum first-solve `p` over the run is
**6.98e-04**, three orders above the case's own `residualControl`; `T_max` goes
**343.07 at iteration 100 → 431.56 at 148**. Whether it aborts past 148 is
**UNMEASURED and stated as absent, not inferred.**

> **ARM 1 SATISFIES EVERY LIMB OF STANDING RULE 4** — `rc = 0`, an `End` line, last
> time == `endTime`, `ExecutionTime` count == `endTime`, all fields present, age
> guard held — **AND ITS SOLUTION SITS 99.2 K OUTSIDE THE FLOW'S OWN ADIABATIC
> CEILING. That is 3.07 dynamic temperatures.**

**COMPLETION AND PHYSICAL ADMISSIBILITY ARE INDEPENDENT.** Rule 4 is a rule about
whether a run *finished*; **it contains nothing that can notice a finished run
whose answer is impossible.** Here every limb holds on a non-physical solution.

**This is the strongest possible argument for the monitor my triage §4 called
for** — a check derivable from the boundary conditions **before the solver starts**
would have refused arm 1 at iteration 53, **with a reason**. **Referred to
verification; amending or extending a standing rule is not a supervisor's call and
certainly not a lane's.**

## 5. THREE CORRECTIONS TO MY OWN TRIAGE. ALL THREE ACCEPTED.

**5.1 — MY LOCAL-MACH FIGURE WAS WRONG, AND I PUBLISHED IT.** I reported
`T_min = 203.324 K` implying **M = 1.542**. **The correct figure is M = 1.781.**

I used `T∞ = 300 K` as the stagnation reference where the isentropic relation
requires **`T0 = 332.331 K`** — the same `T0` I had derived three paragraphs
earlier in the same document. **Re-derived by me:**
`T0/T = 332.331/203.324 = 1.63449`; `(1.63449 − 1)/0.2 = 3.17245`;
`√ = 1.7811`. **The lane is right.**

**It STRENGTHENS the conclusion it was offered to support** — the implied local
Mach is further from anything RAE 2822 case 9 supports, not nearer. **That is
precisely why it must be corrected rather than quietly carried: an error that
happens to favour your own conclusion is the one you are least likely to catch.**
**It appeared in `c146b6cf` and in a report upward, and both are corrected here.**

**5.2 — MY HEADLINE DISCRIMINATOR WAS NEAR-DEGENERATE.** I made *"first `T_max`
exceeds `T0`"* the headline. **A healthy converged adiabatic solve touches `T0` at
its stagnation cell BY CONSTRUCTION** — the control's own first crossing is over
by **0.65 K, about 2 % of the dynamic temperature.**

**The lane demoted it to reported-with-degeneracy-disclosed and promoted the
`T0 + 10 K` ceiling and the span ratio to primary. That is correct and it is a
better instrument than the one I specified.** **A discriminator that a
*passing* case also trips is not discriminating** — the same class as the gate
quantities that could never fail, in the mirror. **Every number I asked for is
still reported, so nothing was hidden by the demotion.**

**5.3 — A GAP IN MY ARM-1 SPEC.** `energy` is also referenced by `div(phi,K)` and
`div(phi,Ekp)`, so changing `div(phi,e)` alone leaves the **explicit**
`fvc::div(phi,Ekp)` term second order. **Registered as a scope limit.** So arm 1 is
a **partial** first-order test, and its MITIGATED reading is a **lower bound** on
what a full first-order energy treatment would do.

## 6. WHAT REMAINS OPEN, STATED AS OPEN

- **The mechanism.** Still open. **Two levers behaving differently names no third
  candidate and I assert none.** Four mechanism claims on this line have been
  corrected, two of them mine. **This document adds no fifth.**
- **Whether arm 1 aborts past iteration 148.** Not run.
- **Residual contention.** No uncontended control was bought; arms 0/1 running
  10–18 % slower than the anchor is **attributed** to contention, **not measured**
  as it. **Correctly labelled.**

## 7. COST

**1.212238 core-min gross / 1.201233 cleaned** against **1.31 predicted** —
**0.9254× gross, 0.9170× cleaned**, **12.1 % of the 10 core-min runaway guard, not
breached**. **$0.001036 derived, not measured.** **Waste named separately:
0.011005 core-min**, the reader pass the lane's own ADDENDUM 1 disclosed. Row
**C-88**.

**The id re-derivation caught a LIVE collision.** An earlier sweep returned max
**C-86**; a peer cfd lane landed **C-87** (`2067d167`) **while these arms ran**. The
worktree ledger copy was **stale, not dirty** — byte-identical to `2067d167^`,
verified before refresh — and the row was built on the **HEAD blob** so the peer's
tail could not be clobbered. **This is the third independent corroboration today
that `append_record.py` cannot be trusted for an id and that the hand-derivation
requirement is load-bearing.**

**`git ls-files` blindness independently corroborated a second time:** it returns
**0** matches for `launch_f12_rung.py` while `git ls-tree -r HEAD` returns **1**.
The lane located the interlock with `find` instead.

## 8. THE LANE'S OWN SELF-CORRECTION, RECORDED AS CORRECT

Its first fingerprint re-check **reported CHANGED and was wrong** — it used a
relative path where the runner used an absolute one, and **`sha256sum` embeds the
filename**. Re-checked absolute: `2fb24ff2…`, **unchanged**. **The runner's
assertions were sound; the after-the-fact check was not.** Disclosing an
instrument scare against yourself, with the cause, is worth more than never having
raised it.
