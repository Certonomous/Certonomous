# A3 sweep rung 3, patched-IDWarp np=4 — PROPOSAL for a re-registration

> **THIS IS NOT A PRE-REGISTRATION AND IT IS NOT FROZEN.** It is a **DRAFT PROPOSAL** for the
> dafoam supervisor to review before anything is frozen, and it is **UNCOMMITTED** by their
> instruction. **Nothing here authorises a launch. No arm may run under this document.** When and
> if it is approved it becomes a **NEW item with its own pre-registration, its own commit and its
> own budget** — it is **not** an amendment to `rung3_patched_idwarp_np4/PREREGISTRATION.md`,
> because that document took first compute at 2026-08-23T21:02:14Z and **gates close after first
> compute** (CLAUDE.md rule 2).
>
> Drafted 2026-08-23T21:15:13Z by the dafoam lane that ran the stopped attempt.

---

## 1. Why a new item exists at all

The first attempt is on the record as **NOT A RESULT — stopped by memory**
(`rung3_patched_idwarp_np4/RESULTS.md`, committed at `67edcc19`). It was killed at **85 s of a
2600 s budget** by its own registered guard on the **host floor** limb, with its own RSS at
**9.202 of 15.0 GiB**. **0 of 11 identity checkpoints were reached.** The question the item was
bought for — *does the patched toolchain inherit rung 3's conditioning wall unchanged?* — is
**still unanswered**, and the patched rung-3 cell of row 12b is answered by row 12d as NOT A
RESULT, not by a verdict.

**The first attempt failed for a registration-design reason, not a numerics reason, and that is
the whole content of this proposal.**

## 2. The defect being repaired, with its arithmetic

`rung3_patched_idwarp_np4/PREREGISTRATION.md` §7 registers two memory numbers that cannot both be
satisfied by this arm:

| registered | value |
|---|---|
| launch-gate memory limb | `MemAvailable ≥ **16 GiB**` |
| neighbourliness floor (the guard kills below it) | `MemAvailable ≥ **8 GiB**` |
| the arm's own measured peak, at the moment it was killed | **9.202 GiB** |

`16.0 − 9.2 = 6.8 GiB`, which is **already below the 8.0 GiB floor before a single co-tenant grows
by one byte.** The gate opened at **16.02 GiB** — 0.02 GiB of margin over the limb — and the floor
was breached **60 s later** as the preconditioner assembly allocated. **A gate that admits a launch
its own floor will then kill is not a gate.** This is the L-239 failure mode in a new costume: the
guard was correct, wired and proved; the *threshold it was paired with* was not.

**The general rule this proposes to register, stated so it can be checked rather than trusted:**

> **A launch gate's memory limb must be at least `neighbourliness_floor + predicted_arm_peak`.**
> Anything less registers a gate that cannot protect its own floor.

## 3. The honest version of the number, which is worse than 17.2 GiB

The supervisor's brief names `8.0 + 9.2 = 17.2 GiB`. **That is a floor on the floor, and this
document will not present it as the answer.** Three peaks are on the record for this mesh and
configuration, and they disagree:

| basis | peak | implied gate limb (`peak + 8.0`) | status |
|---|---|---|---|
| the stopped patched arm, **at 7% of preconditioner assembly** | 9.202 GiB | 17.2 GiB | **measured, but INCOMPLETE — the arm never reached its own peak** |
| the **shipped** arm at this exact mesh, np and configuration | **11.65 GiB** (`A3_RUNG3_N52_RESULT.md:50-51`) | **19.65 GiB** | **measured, complete — this is the defensible basis** |
| `A3-rung3-n52/lever_echo.txt` "record peak 17603.8 MiB", a **different lever set** (stage-0) | 17.19 GiB | 25.2 GiB | disclosed in the original §3 departure 3; **this item does not claim to know whether it governs** |

**Proposed registered limb: `MemAvailable ≥ 19.65 GiB`, from the shipped arm's complete measured
peak**, not from the stopped arm's partial one. Using 17.2 GiB would repeat the original defect in
a smaller size: it would be derived from a peak the arm is known to exceed.

**And the disclosure that has to sit beside the number rather than in a footnote:** if the 17.19 GiB
stage-0 record turns out to govern, **even 19.65 GiB is too low**, and the correct limb is 25.2 GiB
— **82% of this box's entire 30.64 GiB `MemTotal`**. The proposal does not resolve which governs.
**It registers the risk where the threshold is registered, and registers what happens if the guard
fires anyway: NOT A RESULT — stopped by memory, again, with no second budget.**

## 4. The box condition under which such a gate can realistically open

**This is the part that decides whether the item is worth buying, and it is not a numerics
question.** The box has `MemTotal` **30.64 GiB**. A 19.65 GiB limb requires **64% of the entire
machine to be free at launch**, and it must *stay* free enough that co-tenants plus this arm never
drive `MemAvailable` under 8 GiB for 15 consecutive seconds.

Measured co-tenancy during the stopped attempt, none of it this lane's and none of it touched:
4 `buoyantBoussinesqSimpleFoam` (T-family), 1 `simpleFoam` (closure), 1 peer dafoam container
(B3 peak-RSS chain). Host `MemAvailable` over the attempt ranged **15.04 → 7.38 GiB**, and the
observed floor with those tenants live was around **14 GiB of resident co-tenant demand**.

**So: with the current standing fleet live, a 19.65 GiB gate will not open, and the honest
prediction is that a 4-hour poll expires and the item records BLOCKED on host contention with
$0.00 of solver compute spent.** Registering a gate that cannot open is a different failure from
registering one that opens too eagerly, but it is still a failure, and this document says so before
the item is bought rather than after.

**Four dispositions, named so that one is chosen rather than drifted into. None is this lane's to
pick.**

1. **Wait for a genuine quiet window, with the poll widened and the item explicitly allowed to
   expire BLOCKED.** Cheapest and most honest; buys nothing if the fleet never quiets.
2. **Schedule the box** — run the arm in a window where the T-family and closure lanes are
   deliberately not launching. **A scheduling decision across teams; cross-family arbitration is
   reserved to Sanaa** (CLAUDE.md, *Reserved to Sanaa*).
3. **Reduce the arm's own peak** — a different np, or a preconditioner with a smaller footprint.
   **DECLINED BY NAME in this draft, not omitted:** an FD reference is never carried across np
   (`DAFOAM_CHARTER.md` §5) and the comparator for R3-P4 is a **np=4, matched-configuration**
   residual path. Changing either destroys the comparability the item exists for. If it is wanted,
   it is a **different question and needs its own pre-registration.**
4. **A larger instance.** **An instance change is reserved to Sanaa and to no agent at any level.**
   Named here only because it is the disposition that actually removes the constraint.

## 5. What the new item would measure, and what is already proved and need not be re-bought

**Unchanged from the original registration, and unchanged on purpose** — the question, the
comparator and the grading instrument are not being re-tuned after a failed attempt:

* **R3-P4**, the identity: 11 printed checkpoints, iterations 0–1000, compared as **strings**
  against `rung3_patched_idwarp_np4/shipped_cd_checkpoints.txt`, frozen at `97a54c07`.
* **R3-P5** (the patched adjoint converges) and **R3-P6** (the path differs while stagnating) with
  their registered dispositions and their stand-down branch intact.
* §4's *"It WOULD and WOULD NOT mean"* section carries over **verbatim**. In particular: a
  confirmed identity is **not** a gradient verdict, and the patched FD cell at rung 3 stays
  **NOT A RESULT**.

**Already proved in the stopped attempt and re-usable as evidence, though each guard must still
self-test in the launching session:**

| proved | evidence |
|---|---|
| **R3-P1** provenance | 4/4 ranks `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425`, import under `/opt/idwarp_patched/idwarp/` |
| **R3-P2** cold start | `1.018123970654079`, exact to 16 digits |
| **R3-P3** colouring READ | 1355 colours, **zero** `Calculating dRdW Coloring` |
| **R3-P9** the planted-difference control | all 8 `guard_selftest.sh` limbs, including exit **5** on the real shipped log, exit **6** on rung 2's real path, exit **7** standing down on a converging path |
| the memory guard actually kills | **it did** — this is the only item on the ladder with a live demonstration of its own memory stop firing on a real solver |

**These do not reduce the new item's price**, because the arm must run from cold and every guard
must re-prove itself in the launching session. They are listed so the new item is not written as
though nothing were known.

## 6. Price — a NEW budget, requiring authorisation, not a continuation

**The previous item's ceiling is spent-and-closed at 6.80 of 176.0 core-min. No part of the unspent
169.2 core-min carries over.** An overrun stops a run; an underrun does not become credit.

| item | ranks | predicted wall | predicted core-min | basis |
|---|---|---|---|---|
| R3-A′ patched stage 1, `ct_cd`, identity stop at iteration 1000 | 4 | **757 s** point (band 445 – 1157 s) | **50.5** (band 29.7 – 77.1) | **inherited from the original §8 and NOT re-derived** — 445 s is arithmetic from the shipped log's own `ExecutionTime` stamps (`1426 − (1416.00 − 435.44)`), inflated 1.0 – 2.6× |
| guard selftest (2 `alpine` + 6 file-only limbs) | 1 | ~70 s | **1.2** | **measured** in the stopped attempt: 68 s wall |
| per-rank pre-flight | 4 | 2 s | **0.133** | **measured** this session, not the 0.200 the original guessed |
| launch-condition polling | — | up to 4 h | **0.000** | polling costs no core-minutes |
| **predicted total** | | | **≈ 51.8** | band 31.0 – 78.4 |
| **worst case by construction** (`timeout 2600` × 4 / 60 + pre-flights) | | | **174.7** | |
| **PROPOSED CEILING** | | | **176.0** | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-hour, owner-stated 2026-08-21/22, corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure is REPORTED-BY-OWNER, NOT MEASURED.**
Predicted **≈ $0.0443 derived**; worst case **$0.1494 derived**. Well under the $25 bar.

**The 757 s point estimate is inherited and UNVALIDATED.** The stopped attempt reached 7% of
preconditioner assembly in 85 s and tells us nothing reliable about the full wall. It is carried
forward as the original's arithmetic, marked as such, and **will be scored as a prediction against
the same table rather than against a re-derived one.**

## 7. The changes this proposal makes, and the ones it deliberately does not

**Changed — one threshold, and only because the old pairing was internally inconsistent:**

* launch-gate memory limb **16 GiB → 19.65 GiB** (`floor 8.0 + shipped measured peak 11.65`), with
  §3's disclosure that a 17.19 GiB stage-0 regime would make even that too low.
* the free-cores limb, the neighbourliness floor (**8.0 GiB**), the RSS ceiling (**15.0 GiB**) and
  the `--memory=16g` cap are **unchanged**.

**Deliberately NOT changed, each declined by name:**

* **The neighbourliness floor is not lowered to make the gate open.** Lowering a floor to fit a
  gate is choosing the reading to fit the answer, and retiring or reinterpreting a threshold is
  **reserved to Sanaa**.
* **The RSS ceiling is not raised**, and the original's *"the cap is NOT raised"* disposition
  stands. The arm never approached its cap; the cap was not the problem.
* **np, the preconditioner, the tolerances, the colouring cache, the comparator and the checkpoint
  file are untouched.** The comparator file stays the one frozen at `97a54c07`.
* **No gate, threshold, band or label of the original document is edited.** The original stands as
  the record of the attempt that was stopped.

## 8. What must happen before this becomes a pre-registration

1. **The dafoam supervisor reviews this draft** and rules on §4's four dispositions — in
   particular whether the item is worth buying at all if the honest prediction is BLOCKED.
2. **If §4 disposition 2 or 4 is wanted, it goes to Sanaa**, not to a lane and not to a supervisor:
   cross-family scheduling arbitration and instance changes are both reserved to her.
3. **Verification is consulted on the general rule in §2** (`gate limb ≥ floor + predicted peak`),
   because if it is right it is not specific to this rung and belongs above this item.
4. Only then is a pre-registration written, **committed and frozen by sha**, with no run directory
   named in it existing at that commit — and only then may anything launch.

**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

---

> **2026-08-24T16:15:56Z — COMMITTED AS A REVIEWED PROPOSAL.** Reviewed by the dafoam supervisor on
> 2026-08-24 (rulings R1–R8) and committed unchanged, in the same commit as
> `rung3_patched_idwarp_np4_attempt2/PREREGISTRATION.md`, as the record of that review. Its own
> status line above stands: it was UNCOMMITTED when written and it remains **NOT a pre-registration**
> — the frozen document is the attempt-2 file, and where the two differ the attempt-2 file governs.
> **Lines whose number changed above this section: 0.**
