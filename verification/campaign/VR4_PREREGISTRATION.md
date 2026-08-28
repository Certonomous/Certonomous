# VR4 — THE `exec_host` FIELD: MAKING `EXEC` MEASURABLE INSTEAD OF HOST-BLIND

**Repair-registration.** Frozen before any work under it.

## 1. The finding this repairs
`R-AGE-CWD.3` and `L-394`. `scripts/queue_entry_check.py:348` evaluates `Path(cwd).is_dir()` on the
**validator's** host while its own docstring reasons about `queue_runner.py:286/:293` chdir on the
**executing** host. On a two-host lab the justification **inverts**: a `cwd` present on the CPU box and
absent on the GPU host is **accepted**, recorded `LAUNCHED`, and dies at launch — the exact failure the
clause exists to prevent, delivered while it reports green. **Live instance: `VMFLGPU001` and
`VMFLGPU001-R2` both carry `host: ip-172-31-44-162` and a `cwd` that exists only here.**

## 2. WHAT IS MINE
`queue_entry_check.py` is **cfd's instrument** and the code change is theirs. **I ruled the clause's
meaning; what I owe is the SPEC and its control**, so their repair has something to be checked against
that was written before it.

## 3. Gate (frozen)
A committed spec under `docs/standards/` plus a control that:
- **G1** requires an entry whose execution host differs from the validator's to be **`NOT MEASURED`**
  for `EXEC` — **never a pass and never a refusal**.
- **G2** requires the finding text to **name the host** the proposition was tested on.
- **G3** control, both limbs (§2j): an entry with `exec_host` == local and an absent `cwd` still
  **refuses** (`EXEC` retained where it is meaningful); an entry with `exec_host` != local and a
  present `cwd` returns **`NOT MEASURED`**, not `PASS`.
- **G4** the two live GPU entries are re-validated under the spec and their outcome recorded.

## 4. Threshold / label
**PASS** = G1–G3 behave and G4 is recorded. **GATE FAIL** = any limb misbehaves.
**NOT A RESULT** if the control cannot be driven.

## 5. Cap
**10.0 core-minutes.** Zero solver compute.

## 6. Not claimed
No queue entry is refused or admitted by this item. It does not switch on any gate; it makes an
existing gate say which host it tested.
