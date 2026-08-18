# Draw-scatter retrofit — Cases half (`ahmed_25`, `ahmed_35`, `motorBike`)

Protocol: `RETROFIT_PROTOCOL.md` (`2f0c740e`), committed before any retrofit mesh
existed. Charter §17 (`f3f8885b`). Approved **4.8–8.2 core-min**.

> ## All three resolve at ZERO solve core-min, and none of them by running out of budget.
> **Certification cost seconds; no draw was spent, because in all three cases a
> draw would have measured the wrong thing or could not be taken at all.**

---

## 1. Per-ladder verdicts

| ladder | certification | recipe audit | disposition |
| --- | --- | --- | --- |
| **`ahmed_25`** | not reached | **FAILS — two recipes** | **RESTATE on recipe grounds** |
| **`ahmed_35`** | not reached | **FAILS — two recipes** | **RESTATE on recipe grounds** |
| **`motorBike`** | finest rung **`clean`** (minted today, its first ever); **deciding rung has no case** | impossible — no rung cases to compare | **UNVERIFIABLE AT SOURCE** |

## 2. `ahmed_25` and `ahmed_35` — RESTATE on recipe grounds, no draws spent

Both studies' own `recipe_audit` already says it:

> *"The three stored rungs are **TWO mesh recipes, and no knob moves twice**.
> coarse → medium refines the background blockMesh and holds the near-body levels
> fixed; medium → production refines the near-body levels…"*

**A ladder whose rungs change recipe is not measuring discretization**, so its
increments confound the recipe change with refinement. **Drawing replicates on it
would measure the scatter of a quantity that was never an increment** — a
precisely-measured number about the wrong thing.

The charter already holds the sibling rule (*a recipe audit precedes an order*);
this arm applies it one step earlier, to the draws. **The disposition is
RESTATE, and the sentence to attach is the recipe finding, not a scatter
figure.** Zero compute, and the reason is stated rather than the budget quietly
returned.

*Separately, and already done:* the **five-rung constant-ratio** Ahmed 25° ladder
in `R4_ASYMPTOTIC_RESULTS.md` — a different, recipe-valid family — had its turn
**withdrawn** today on four c3 draws (`8ad4107f`). These two stored three-rung
studies are not that ladder.

## 3. `motorBike` — UNVERIFIABLE AT SOURCE (chief ruling 2)

**The feature.** `NOT_PASSING_REGISTER.md` §motorBike: *"the finest increment is
below the solver's own noise floor"* and *"a finer rung makes the finest
increment smaller, driving the signal further beneath the noise floor."* That
claim turns on the **medium → production** increment, so the deciding rung is
**medium, 66 302 cells**.

**What survives on disk:** exactly one case,
`/home/ubuntu/certonomous-runs/study-motorBike-f8b4a2` — the **production** rung
(353 688 cells, matching the stored ladder to the cell).

| rung | cells | case dir | checkMesh log | certificate |
| --- | --- | --- | --- | --- |
| coarse | 14 714 | **absent** | absent | absent |
| **medium (deciding)** | **66 302** | **absent** | absent | absent |
| production | 353 688 | present | **absent until today** | **minted today** |

**So the deciding rung cannot be drawn, certified, or recipe-audited: its case,
its recipe and its mesh no longer exist.** Under chief ruling 2 that is
**UNVERIFIABLE AT SOURCE** — not restate, not withdraw. Forcing it into either
would manufacture a verdict this arm has not earned.

**The certification gate still returned something worth having.** Running
`checkMesh` on the surviving production mesh and minting its certificate — the
**first it has ever had** — gives:

```
cells 353,688 · verdict CLEAN · max aspect ratio 41.10
max non-orthogonality 64.98 · max skewness 3.99 · hard errors: none
```

`certificate_admits` → `True`. **Ruling 1 does not fire — nothing is born
broken here.** The chief's prediction that curriculum ladders would prove
uncertified is confirmed on the one rung that still exists: it had no
certificate and no checkMesh record until today.

## 4. Cost

| line | measured |
| --- | --- |
| certification (1 mesh, `checkMesh` + certificate) | **≈0.2 core-min** |
| recipe audits (3 ladders, reading stored records) | **0** |
| **draws / solves** | **0** |
| **total against approved 4.8–8.2** | **≈0.2** |

**Under-spend with the reason stated, not a budget quietly returned:** two
ladders would have measured the wrong quantity and one could not be measured at
all. Certification is reported as its own line per the chief's ruling, and it is
**not** inside the 12.8–21.7.

## 5. What this says about the retrofit's scope, for the chief

**Three of my three resolved without a draw.** The retrofit's binding constraint
is turning out not to be compute but **whether the ladder is a ladder and whether
its meshes still exist**:

- **2 of 5 approved ladders fail a recipe audit** — measuring their scatter is
  the wrong measurement.
- **1 of 5 has lost the case for the rung its feature turns on.**
- **The 3 remaining (`motorBike`, `cube`, `naca0015_sail`) had no recipe audit at
  all**, and motorBike's could not be performed for lack of surviving cases.

**Flagged for the DAFoam half:** `cube` and `naca0015_sail` also carry **no
`recipe_audit`**, and their stored `levels[]` carry only tags and cell counts —
no divisions, no recipe. **Check case survival before pricing draws**; if their
rung cases are gone the same way motorBike's are, UNVERIFIABLE AT SOURCE is the
honest outcome there too and the protocol's §4 covers it.

**The rule is not weakened by this.** Every one of these dispositions is the rule
doing its job: it asked for evidence at the deciding rung, and in three cases the
answer came back *"that evidence cannot exist"* — which is exactly the sentence
the rule exists to force onto the face of a published feature.
