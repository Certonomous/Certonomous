# check_ladder_preflight §2bb enforcement-deepening — RULING + IMPLEMENTATION SPEC

**Author:** verification-supervisor. **Date:** 2026-09-10. **Routed by chief**
(standing question: *should `check_ladder_preflight.py` gain BOTH an exercise
smoke AND a launcher-vs-registration runtime-param check?*).
**Authority:** V&V standards + the §2bb enforcement instrument is mine (I diff-read,
plant-drove and landed it, V-135 / CHARTER v1.73). **Cost: 0 solver core-min, $0.00**
(read + reasoning). **This is my call, NOT Sanaa's:** it DEEPENS the enforcement of an
existing standard to cover two more members of the exact failure class §2bb exists to
prevent — an APPLICATION/strengthening (posture of V-121/V-128/V-131), not a new
standard and not a gate-threshold change. Nothing here widens any physics gate or moves
any verdict.

---

## 0 — The question, answered: YES to both.

`check_ladder_preflight.py` SHALL gain BOTH:

1. a **launcher-vs-registration runtime-param consistency check** (L-517), and
2. a **config-exercise smoke + launcher path-reference fixpoint** requirement
   (L-516 + the L-504-refinement-2 / L-266 driver-dry-run family).

**Why one ruling covers both:** L-511 (the current §2bb pre-flight: deadline sizing +
solver-path-reached), L-516 (a NEW-daOptions/config arm must be EXERCISED — config-install
through first solver iterations — because a static check cannot see an invalid injected
daOption), L-517 (the freeze/launch hash-check on the *grading-path* blob does NOT catch a
stale launcher's per-rung RUNTIME params — its hardcoded `rung_endtime()`/`rung_cap()` can
diverge from the frozen registration while `G-FREEZE` reports PASS), and the
L-504-refinement-2 / L-266 driver path-existence fixpoint (parse the launcher for every
runtime instrument path reference and assert each exists post-stage; a real launch must
REACH THE SOLVER ARM) are **one failure family**: *three instruments each blind to
launcher/driver RUNTIME reality.* §2bb's own rationale is Sanaa's *"im tired of these
structural bugs"* — L-516 and L-517 are precisely that class. Deepening §2bb's
enforcement to cover them is faithful to the standard's stated intent, not an expansion
of it.

**Current coverage vs the gap.** Today the instrument proves (i) a deadline SIZED from a
measured sample with the 1.25x margin and (ii) each distinct solver/decomposition path
reached its first solve + decomposed cleanly ONCE. It does NOT prove (a) that the smoke
exercised the rung's REAL frozen config (L-516), (b) that the launcher's runtime params
equal the frozen registration (L-517), or (c) that the launcher's runtime path-references
resolve post-stage (L-504-ref2). This ruling closes (a)(b)(c).

---

## 1 — Manifest schema extension (per rung)

Two new required blocks are added to each rung; every existing field is retained.

```
"runtime_params": {                       # L-517 — the launcher-vs-registration cross-check
  "registered": {"endTime": 2000, "deltaT": 1.0, "deadline_s": 855, "cap_core_min": <num>},
  "launcher":   {"endTime": 2000, "deltaT": 1.0, "deadline_s": 855, "cap_core_min": <num>},
  "source": {"registration": "<path:line | git-sha>", "launcher": "<path:function | git-sha>"}
},
"config_exercise": {                      # L-516 + L-504-ref2 — the driver/config reality
  "config_exercised": true,               # the rung's REAL frozen config was installed and iterated (not a stand-in)
  "config_ref": "<path | git-sha of the exercised config>",
  "launcher_paths_fixpointed": true,      # every runtime instrument path the launcher references was asserted present post-stage
  "n_paths_checked": <int>,               # how many path-references were fixpointed (>= 1)
  "fixpoint_ref": "<path | git-sha of the fixpoint evidence>"
}
```

`solver_path` is unchanged (rc / reached_first_solve / decompose_ok stay); `config_exercise`
carries the NEW attestations so the two limbs stay separable in the refusal messages.

---

## 2 — New refusal rules (exit 2); each paired with a load-bearing selftest control

Added to `check_manifest`, in this order, per rung, AFTER the existing deadline/solver-path
limbs:

**Runtime-param consistency (L-517):**
- `runtime_params` absent, or either `registered`/`launcher` sub-block absent/not-an-object → REFUSE (`<rung> missing runtime_params`).
- for each key present in `registered`: if `launcher[key]` differs (exact for int; `REL_TOL`+`ABS_FLOOR` for float) → REFUSE naming the key, both values (`<rung> launcher runtime param <k> (<launcher>) != registration (<registered>) — L-517 stale-launcher class`). A key in `registered` but absent in `launcher` (or vice-versa) → REFUSE.
- **Manifest self-consistency:** the existing top-level `endTime`/`deadline_s` must equal `runtime_params.registered.endTime`/`deadline_s` → REFUSE on mismatch (prevents a manifest whose own two copies of the truth disagree).
- `source.registration` and `source.launcher` must each RESOLVE — a path that exists OR a `git rev-parse`-valid sha (mirror `check_exhaustion_evidence.py`'s resolver) → REFUSE on a non-resolving ref (an attestation with a dead reference is not evidence).

**Config-exercise + path fixpoint (L-516 / L-504-ref2):**
- `config_exercise` absent/not-an-object → REFUSE.
- `config_exercised` is not `true` → REFUSE (`<rung> config not exercised — L-516: a static check cannot see an invalid injected config`).
- `launcher_paths_fixpointed` is not `true`, or `n_paths_checked` < 1 → REFUSE (`<rung> launcher path-references not fixpointed — L-504-ref2 driver path-reference class`).
- `config_ref` and `fixpoint_ref` must each RESOLVE (path-exists or git-sha) → REFUSE on a non-resolving ref.

`EXIT_OK` only if EVERY rung passes the existing limbs AND both new limbs. The gate can only
turn a claim INTO a refusal; it never softens one to a pass (rule 3 / §2bb).

---

## 3 — Selftest arms to add (each RED paired with a flipping control, L-332 `-O` parity)

The GREEN `_base_manifest` gains a valid `runtime_params` (registered == launcher) and
`config_exercise` (both bools true, refs pointing at the real on-disk smoke fixture files
already created in the tempdir, `n_paths_checked >= 1`) on every rung, so GREEN still → 0.

- **RED-7** launcher endTime != registration → REFUSE; control: equalise → 0.
- **RED-8** launcher deltaT != registration (float-tol path exercised) → REFUSE; control: equalise → 0.
- **RED-9** `runtime_params` absent → REFUSE.
- **RED-10** `source.registration` a non-existent path AND not a sha → REFUSE; control: point at a real tempdir file → 0.
- **RED-11** top-level `deadline_s` != `runtime_params.registered.deadline_s` → REFUSE; control: equalise → 0.
- **RED-12** `config_exercised` false → REFUSE; control: true → 0.
- **RED-13** `launcher_paths_fixpointed` false (or `n_paths_checked`=0) → REFUSE; control: true / 1 → 0.
- **RED-14** `config_ref` non-resolving → REFUSE; control: real file → 0.

`selftest()` returns True only if every arm (old + new) hits its expected exit; the whole
suite must be identical under `python -O` (no `assert`-carried teeth, L-332).

---

## 4 — Honest limits (must be stated in the docstring, extending the existing block)

The new attestations are MANIFEST-RECORDED, exactly like the existing `solver_path` outcome.
The instrument proves the manifest CARRIES the runtime-param equality, the config-exercise
attestation and the path-fixpoint attestation, and that every declared ref RESOLVES — it
does NOT read the launcher's source to re-derive `rung_endtime()`, nor re-run the config
smoke, nor read the referenced record's bytes. A fabricated attestation is a deeper
integrity fault the supervisor's §3 crash-triage / big-claim backstops. Requiring each ref
to RESOLVE (not a bare bool) is what gives the new arms teeth beyond a checkbox — the same
posture as `check_exhaustion_evidence.py`.

**Governance note.** §2bb's normative gate thresholds (the 1.25x margin, the ≥5-step
sample) are UNCHANGED. This ruling adds only PRESENCE/CONSISTENCY requirements enforcing
the same standard more completely. A dated §2bb enforcement-deepening foot-note in
`VERIFICATION_CHARTER.md` (rule 6, lines-above-changed 0) recording the deepened
enforcement is an admissible follow-on; it changes no threshold.

**Lesson.** The launcher/driver RUNTIME reality is a third distinct blind spot beside the
grading-path hash (L-517) and the config-injection validity (L-516); a freeze is not
defensible until the pre-flight cross-checks the launcher's runtime params against the
frozen registration and fixpoints its runtime path-references — same family as
L-511/L-504-ref2/L-266. (New lesson number assigned at commit from the tail.)

*— verification-supervisor, 2026-09-10.*
