# T26 — COST_CHANNEL DEFECT NOTE: `scripts/cost_channel.py` is dead at its current path

> **NOT FILED. NOT SENT. NOT APPLIED.**
> This is a DRAFT defect note for the team that owns `scripts/`. Nothing here has
> been filed, uploaded, posted or reported outside this box (`CLAUDE.md` rule 7),
> and **the fix below has NOT been applied to the repository**. Sending and
> applying are decisions for the owning team and, for anything leaving the box,
> for Sanaa alone.

**Raised by:** a heat-transfer lane, 2026-09-10, while arming T26's comparator.
**Severity:** blocks T26's freeze (`T26_PREREGISTRATION.md:780-782` makes arming
the cost channel a freeze precondition). **Direction: FAIL-CLOSED** — the channel
refuses rather than reporting a false cost, so **no false figure was ever
published because of it.**

## The defect, in one line

`scripts/cost_channel.py:141`

```python
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
```

Three `..` from `scripts/` resolves to **`/home`**, not to the repository root.

## Why it is three, and why that was once right

The file's own usage docstring, `:4-6`, still reads:

```
    python3 verification/runs/T-family/cost_channel.py --selftest
```

From `verification/runs/T-family/`, three `..` **do** reach
`/home/ubuntu/Certonomous`. **The file was moved to `scripts/` and this constant
was not moved with it.** No copy remains at the old path, so the channel is dead
lab-wide, not merely in one caller.

## Measured consequence

| what | result |
|---|---|
| `cost_channel.REPO` as shipped | `/home` |
| repository root | `/home/ubuntu/Certonomous` |
| `python3 scripts/cost_channel.py --selftest` | **exit 2**, every fixture arm `FIXTURE MISSING` |
| `assert_cost_channel_armed()` | raises `SystemExit` for **every caller on this box** |

Every fixture path it builds is wrong, e.g. it looks for
`/home/verification/runs/T-family/T17_runs/STATUS.T17_CY_f`.

## The fix, PREPARED AND PROVED, NOT APPLIED

```diff
--- a/scripts/cost_channel.py
+++ b/scripts/cost_channel.py
@@ -139,7 +139,7 @@
 import sys
 
 REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
-                                    "..", "..", ".."))
+                                    ".."))
 TREES = ["verification/runs/T-family",
          "verification/runs/F14-cooling-ladder",
          "verification/runs/THERMAL_K0_runs"]
```

**Evidence it works, taken WITHOUT modifying the file** — `REPO` overridden in
memory only, in a throwaway interpreter:

- all four named fixtures resolve **PRESENT** at the corrected root
  (`STATUS.T17_CY_f`, `STATUS.M1_c`, `DONE.R_ff`, `DONE.T5_CUBE_c`);
- `assert_cost_channel_armed()` returns **`passed=True` over 15 arms, zero
  failing**, against the shipped `SystemExit` for every caller today.

## Why this lane did not apply it

1. **`scripts/` is not heat-transfer's territory.** `CLAUDE.md` team roster.
2. **The blast radius is every call site that currently refuses.** A one-line
   change that flips a lab-wide guard from always-refusing to actually-checking
   is a change the owning team must read, not one a consuming lane should slip in.
3. `CLAUDE.md` rule 9: a consuming team's need is not the owning team's consent.

## What it blocks

`T26_PREREGISTRATION.md:780-782` registers the cost channel as **MANDATORY** and
its arming as a **freeze precondition** — a ruling the heat-transfer supervisor
made 2026-09-10. `analyse_t26.py` therefore **REFUSES (exit 3)** with the defect
diagnosed by name, and **T26 cannot be frozen while this stands.**

The docstring at `:2-6` should be corrected in the same change, since it still
names the old path and is what makes the three `..` look deliberate.
