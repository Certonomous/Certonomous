# D6RF10-R2-REFIRE — **`BLOCKED` AT THE RUNNER'S GATE A.** The entry is written, validated and refused, and it is NOT being re-placed in a form that would pass by deceiving the gate.

**Date:** 2026-09-12. **Team:** dafoam. **Lane:** `lab-lane`. **Supervisor:** `dafoam-supervisor`.
**SUBMISSIONS PARKED** (rule 7). **Nothing was launched. Nothing on disk was modified to make a gate pass.**

---

## 1. WHAT HAPPENED, IN ORDER

1. The cap-removal, non-root and checkpoint work landed at commit **`86e4d58eb`**.
2. The queue entry was written and **`scripts/queue_entry_check.py` returned `ACCEPTED`**
   — `team=dafoam case=D6RF10-R2-REFIRE ranks=4 est=166.5 core-min`, with TEAM-BINDING,
   LAUNCH-TARGET and GRADING-FREEZE-PIN all clean.
3. **The queue runner then refused it**, and moved it to
   `verification/queue/dafoam/refused/D6RF10-R2-REFIRE.json` with a `.REFUSED.txt` beside it:

   > `GATE A CHECKPOINT: gate A: solver_class='dafoam-primal-containerised' is not one of
   > openfoam-steady / openfoam-transient / optimisation / utility, so no limb of the
   > checkpoint policy could be selected.`

**The first refusal was my error and I own it:** I invented a `solver_class` string instead
of using one of the four the runner registers. The correct declaration for this rung is
**`openfoam-steady`** — the legs run `DARhoSimpleFoam`/`DARhoSimpleCFoam` primals to a fixed
`endTime`, with no optimiser majors.

**But correcting that declaration does not make the entry launchable, and that is the real
blocker below.**

---

## 2. 🔴 THE REAL BLOCKER — A STRUCTURAL MISMATCH, NOT A TYPO

With `solver_class: openfoam-steady`, gate A takes the controlDict limb
(`scripts/queue_runner.py:648`, `checkpoint_gate`): it reads **`<cwd>/system/controlDict`**
and requires, **before launch**, that

- limb (i) `writeInterval` ≤ `1800 / iteration_rate_s`, and
- limb (ii) `purgeWrite` ≥ 2.

**`d6rf10_run_arm.sh` has no case directory at rest for that limb to read.** It *creates*
its run root at launch time (a fresh `…​.RERUN-R2-<UTC>` sibling), stages the case into it,
and **installs the controlDict inside the container** via `install_config`. Every candidate
`cwd` fails, and each for its own reason:

| candidate `cwd` | why it fails |
|---|---|
| the re-fire root `…​.RERUN-R2-<UTC>` | **does not exist yet** — gate A refuses a missing cwd (`:625`); and if it did exist, the launcher's own **`G-ROOT.3` aborts rc=3 on a root that already exists**. Genuinely circular. |
| the repo `/home/ubuntu/Certonomous` | has no `system/` — refused as "not an OpenFOAM case directory" (`:629`) |
| the staging source `…​CURRICULUM-D6RF7-a2-wing-convergence-probe/P_conv` | **it is D6RF7's GRADED root.** Measured: its `controlDict` carries `writeInterval 1000`, `purgeWrite 0` — which **refuses on both limbs** (1000 > 1800/4.54 = 396; 0 < 2). And **writing the fix into it is forbidden**: it holds another item's graded evidence and **this launcher's own `G-ROOT.2` aborts rc=3** on exactly that path. |

**Neither side is wrong.** Gate A is enforcing Sanaa's item 4 — *"The launcher refuses to
start any case whose controlDict or run script does not satisfy 1–3"* — exactly as written,
and it wants the guarantee **statically, before compute**. D6RF10's stage-then-install
design predates that directive and can only offer the guarantee **at container start**.

---

## 3. WHAT I DID NOT DO, AND WHY IT MATTERS

**I did not point `cwd` at a case-shaped directory that the run does not actually use.**
That would have passed gate A by having it read a controlDict with no causal connection to
the solve — a **decoy that defeats the precise thing the gate exists to guarantee**. Gate A
would report PASS while the 30-minute loss bound went unverified. That is the shape of
defect this lab writes lessons about, and a green light bought that way is worse than this
blocker.

**I also did not edit D6RF7's graded root** to make the source satisfy the limb.

**The checkpoint itself is real and is installed** (commit `86e4d58eb`): `install_config`
now sets `writeInterval` and `purgeWrite 2` and **reads both back from the file** after
writing, with a `D6RF10_CHECKPOINT_INSTALLED` marker. R2 gets `writeInterval 100` against
`endTime 300` at a measured 4.54 s/step ≈ 7.6 min per checkpoint. **The guarantee exists;
what does not exist is a way for gate A to see it before launch.**

---

## 4. THE THREE RESOLUTIONS — none of them a lane's to take

1. **Split the launcher into a `utility` staging entry and an `openfoam-steady` solve
   entry.** The first creates and stages the root; the second declares `cwd` as the staged
   `P_conv`, whose controlDict gate A can then read **and which the solver actually uses**.
   Honest and non-decoying. **But it restructures `G-ROOT.3`/`G-ROOT.4`, whose predicates
   the supervisor explicitly directed be kept intact** — so it is a supervisor call.
2. **Give gate A a registered limb for launchers that install their controlDict at container
   start**, verified another way — e.g. by pinning the md5 of the `install_config` that does
   it, which this launcher already carries the machinery for. **That is a change to a shared,
   cross-team gate: verification's and the supervisor's call, never a lane's.**
3. **Declare the rung `utility`** to skip the policy. **Rejected outright and recorded as
   rejected:** it is a solver run, the declaration would be false, and gate A's own comment
   says the point of the declaration is that it *"sits in the frozen entry where it can be
   graded"*.

**Recommendation: option 1**, with option 2 raised to verification as the general fix, since
every stage-then-install launcher in `cases/dafoam/` meets this same wall.

---

## 5. STATE

- **Cap removal, non-root, checkpoints: DONE and committed** (`86e4d58eb`).
- **Queue entry: `BLOCKED`.** It sits refused at
  `verification/queue/dafoam/refused/D6RF10-R2-REFIRE.json`, which is its record.
  **It is deliberately not re-placed.**
- **Nothing launched.** The runner is the only launcher (directive item 19), and no agent's
  message is Sanaa's consent.
