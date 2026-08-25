# ONERA M6 — AMENDMENT TO MY TOPOLOGY RULING: **I WAS HALF RIGHT, AND THE HALF I GOT WRONG IS THE HALF THAT MATTERS**

**Written by the cfd supervisor personally, 2026-08-25.** Amends
`verification/campaign/F1_M6_TOPOLOGY_RULING_2026-08-25.md` (`3026c90e`).
**That document is NOT edited** — rule 6: originals are struck, never rewritten.
`[lab-attributed]`; **overrulable.**

Evidence: `c813b20d`, a `MESH_STANDARD.md` §8.1 build trial. **Nothing
pre-registered; the only gate applied is §3.1's standing 70°.** All numbers cite
`verification/runs/F1_MESH_TRIALS_2026-08-25/topology_study/`.

---

## 1. I ORDERED THE TEST THAT COULD REFUTE ME. IT REFUTED ME. THAT IS THE RECORD.

My ruling said, in terms: *"Replace ONLY the outer blocks with an orthogonal
far-field shell. If the maximum drops below 70°, my ruling is confirmed in its
strong form: the near-body butterfly was never the problem. **If it does not, my
ruling is WRONG and the near-body topology is implicated after all — and I want to
know that.**"*

**It did not drop below 70°. The corollary is FALSIFIED and I am striking it.**

**CONFIRMED — the far-field half.** `t1_SHELL`: maximum non-orthogonality
**excluding the 8 tip-cap blocks falls 81.9396° → 47.9767°**, at an **identical
cell count (111,872)**, skewness unchanged (1.4431 → 1.4430), **`F1_BETA` and
`F1_RFAC` untouched**, outlet plane still planar. **The far-field breach is a
topology defect and it is repairable in the outer blocks alone.**

**FALSIFIED — the corollary.** With the outer blocks repaired the **tip-cap
butterfly is the only thing left above 70°**, and the whole-mesh maximum lands on
**81.5834° — the tip-cap floor, to four decimals. `GATE FAIL`.**

## 2. TWO OF MY OWN BRIEFED PREMISES WERE WRONG, AND THE FIRST IS THE LESSON I COINED IN THE SAME DOCUMENT

**2.1 — "The maximum is NOT at the trailing edge" is TRUE AT THE REGISTERED BETA
AND FALSE OF THE FLOOR — and the floor is what has to be cleared.**

**I committed, in the very document where I coined it, the error the document
names**: *"Name the quantity before you name the place."* I named the place
(farfield) for the quantity **maximum-at-registered-beta**, and then reasoned
about a different quantity — **the dial-invariant floor** — as though the
localisation transferred. **It does not.** The floor was always mechanism B, at
the sharp trailing edge.

**That the lesson caught its own author within the hour is the strongest evidence
I have that it is worth landing.**

**2.2 — The `MK` test did NOT falsify the degeneracy hypothesis, and my "both
hypotheses falsified by measurement" claim was itself an artifact.** `MK` was run
against **mechanism A**, which `MK` cannot touch, **so it could not have moved
whatever `MK` did.** Measured against **mechanism B**, at a beta where B *is* the
maximum: `b3_BETA_5` **81.5834** vs `b3_BETA5_MK1` **81.5971**. **`MK` does move
the floor — by +0.0137°, the WRONG WAY.** The right block, an ineffective repair.

**A repair tested against the wrong mechanism produces a null that looks like a
refutation.** That is a general trap and it is worth a lesson of its own.

## 3. WHAT THE MAXIMUM ACTUALLY IS — MEASURED, WITH A NORMAL ATTACHED

`outer_face_geom.py` **imports** `te_study/worst_nonortho.py` and carries **both**
its planted controls (agreement with `checkMesh` to < 0.05° — **worst seen
0.00005**; and a point displacement that must move the angle — **seen on every
mesh**). It adds the **face normal**, which is what attaches a mechanism to a
number.

**My briefed "most likely reading" — an oblique far field — is FALSIFIED by five
decimal places.** The winning face's unit normal is
**`(−0.962154, 0.000010, 0.272506)`**, an x–z normal; the outer boundary there is
the plane `y = −16.118000` and **the radial lines meet it dead normal.**

**MECHANISM A — far-field fan.** `blk01`/`blk06`, **81.9396°**, 58 faces. The
block's inner *i*-edge is the curved wing surface and its outer *i*-edge is a
straight line **of a different arc length**; `blockMesh` grades both by the same
arc-length fractions, **so the *i*-lines fan.** The fan tapers the outermost radial
cell 3.2 % across its own 4.536-tall radial extent → centroid offset
`d_y = 1.192988e-02` against a through-face spacing of `1.690823e-03` →
`atan = 81.9396`. **And the natural control was already on disk and unread:**
`blk00` (`wake_lo`) has the **same grading, same aspect ratio and same far-field
plane**, but **both its *i*-edges are straight and equal in length — and it never
appears above 70°.**

**MECHANISM B — tip-cap fan. THE BINDING FLOOR.** `blk18`/`blk21`, **81.5834°**,
444 faces, **BETA-invariant**. Face centroid `(1.135483, −0.000732, 1.525873)` —
**|y| = 7.3e-04. That is the SHARP TRAILING EDGE of the tip cap, not the far
field.** `blk21` has three of four corners on `x = xb`; *j* turns 90° across the
block and **collapses ~16:1 onto the TE.**

## 4. THE TIP CAP IS CORNERED, AND THE OBSTRUCTION IS THE AEROFOIL, NOT A DIAL

**Three core placements built, all fail:** v2 **81.5834** (strips fail), fully
self-similar core **87.0192** (core fails), stations-only **84.8750** (strips fail
again). Whatever the core's shape, **the strip facing the TE must join a surface
arc of ~(1−U2)·c to a core edge of ~CORE_S·t2(U2)·c — a ratio ~16 at the
registered break, set by the section's half-thickness, which goes to ZERO at a
sharp trailing edge.**

**AND IT DOES NOT REFINE AWAY — this is the decisive number.**

> **81.5834 (nr = 4) → 81.9764 → 82.0355 → 82.0645 (nr = 64), RISING to an
> asymptote near 82.07.**

**That is `MESH_STANDARD.md` §8.1's own signature of a fixed fraction of the mesh
rather than a marginal miss.** Refinement makes it *worse*, converging to a
constant. **No amount of resolution reaches 70°.**

**The escape is closed too:** the H-block lens cap is refused by `blockMesh`
itself — Amendment 2 A2.2(2) records **rc = 134, 48 zero-area faces** — and the
`polyMesh` bypass is closed by **§8.2 and C1.3**.

## 5. THE LANE'S OWN REFUSAL, HANDLED CORRECTLY, AND I AM RECORDING IT AS CORRECT

`blockMesh` **refused** the first shell build (`rc = 1`, *"boundary face … either
an internal face or already belongs to the same patch … patch 0 named wing"*).
**It was right and the defect was the lane's** — it handed the shell block the
inner block's patch list. **The fix corrects a PATCH ASSIGNMENT; no block, vertex
or edge was changed to make a number appear. §8.2 is NOT engaged, and the refusal
was captured with its log rather than routed around.**

**That is exactly the behaviour §8.2 exists to produce**, and it is the second
time today a cfd lane has treated a tool's refusal as a diagnostic instead of an
obstacle.

## 6. THE AMENDED RULING

> **ONERA M6 as this lab builds it is `GATE FAIL` against `MESH_STANDARD.md` §3.1,
> and the binding obstruction is the SHARP TRAILING EDGE meeting a structured
> butterfly tip cap. It is GEOMETRIC and REFINEMENT-INVARIANT — it rises with
> refinement to an asymptote near 82.07° — and it is reachable by NO dial in the
> generator.**
>
> **The far-field repair is REAL and should be KEPT** (81.9396 → 47.9767 in the
> wrap at identical cell count): it removes mechanism A permanently and costs
> nothing. **It simply is not sufficient.**

**§3.1's 70° threshold is NOT touched.** It is not loosened, not widened, and no
exception is carved. **Retiring or widening a gate threshold is reserved to
Sanaa** (rule 9).

## 7. WHAT I AM PUTTING ON SANAA'S DESK, AND WHY IT IS HERS AND NOT MINE

**M6 is her named second HOLDS path, and this lab cannot mesh it to its own
standard with a structured generator.** Three routes exist and **the choice among
them is not a supervisor's:**

1. **A non-structured mesher** — `snappyHexMesh` or an unstructured tip
   treatment. **Changes the meshing method for this family**, and the M6
   pre-registration is written around a structured `blockMesh` generator.
2. **A rounded / blunted trailing edge.** **INADMISSIBLE and I am not proposing
   it** — a thickened or blunted section **is not the ONERA M6**, exactly as
   `TSCALE` was ruled inadmissible.
3. **A ruling on §3.1's threshold for sharp-trailing-edge geometry.** **RESERVED.**
   I state the evidence and take no part of the decision: the obstruction is a
   *fixed fraction* of the mesh (444 faces of 111,872), it is **refinement-rising,
   not refinement-vanishing**, and it is **intrinsic to a sharp TE**, so any
   structured cap on this geometry meets it.

**I recommend route 1** and note it needs a rule-2 amendment to the **unfired**
`F13_ONERA_M6_PREREGISTRATION.md`. **I do not take route 3 and no lane may.**

## 8. TWO LESSONS OWED

1. **Name the quantity before you name the place.** Now with **three** instances
   in one day — F1's population-vs-maximum, F12's origin-vs-terminus, and **my own
   maximum-vs-floor, committed inside the document that coined it.**
2. **A repair tested against the wrong mechanism produces a null that reads as a
   refutation.** `MK` against mechanism A "falsified" a degeneracy hypothesis that,
   tested against mechanism B, **it actually moves — the wrong way.**

## 9. COST

**This amendment: ZERO COMPUTE.** The §8.1 build trial's calibration row is **OWED
by the lane that ran it** — I did not run it and will not state an actual I did not
read from a log.
