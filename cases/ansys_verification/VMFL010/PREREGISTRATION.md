# VMFL010 — Laminar Flow in a 90° Tee-Junction: PRE-REGISTRATION (template form)

**NOT FILED ANYWHERE.** Nothing here or in the case it registers leaves this box
(CLAUDE.md rules 7, 8; `ANSYS_VERIFICATION_CHARTER.md` §8). **SUBMISSIONS PARKED.**

**NOT YET RUN — frozen before any solver starts** (rule 2). At writing,
**`verification/runs/ansys_verification/VMFL010/` did not exist** — `ls -d` at
**2026-08-25T17:08:06Z** returned *No such file or directory*. **Graded compute is
LOCKED**; the `ansys-verification-supervisor` unlocks it after four personal
checks, and **no agent message is Sanaa's consent** (rule 9). Drafted by
`ansys-lane-opus48` on the standard form. Departures = dated addenda at the foot
(rule 6).

**DISCLOSED IN ADVANCE, IN THIS FROZEN DOCUMENT, NOT AFTERWARDS: the reference is a
CODE-TO-CODE number. It buys NEITHER V NOR P. The best verdict this case can earn
is GATE REACHED — never PASS.** A register row scoring it as a validation
credential would rest on a false sentence.

---

## The standard form (frozen)

```
1. CASE       : VMFL010 — Laminar Flow in a 90° Tee-Junction — manual p.39.
                Solver = OpenFOAM v2606 simpleFoam (steady, laminar, incompressible).
                No Fluent/CFX on this box; archive read for setup only. NOT YET RUN;
                run dir absent at 2026-08-25T17:08:06Z.
2. REFERENCE  : flow split (fraction in the upper/main branch) = 0.887.
                Source = R.E. Hayes, K. Nandkumar, H. Nasr-El-Din, "Steady Laminar
                Flow in a 90 Degree Planar Branch", Computers & Fluids 17:537–553
                (1989). Ansys Fluent = 0.884, Ansys CFX = 0.8837 — CONTEXT ONLY.
3. REF KIND   : **code-to-code / published numerical benchmark → buys NEITHER V nor
                P.** The manual's own test text also speaks of comparison "with
                experimental results", but the provenance of the 0.887 value cannot
                be established independently from the manual; the conservative,
                honest classification is therefore NEITHER, and it is frozen here.
4. CEILING    : **GATE REACHED** (band met = we reproduced the reference number).
                It CANNOT reach PASS — reproducing a solver's benchmark is not a
                verification. GATE REACHED is this team's success (Sanaa 2026-08-25).
5. QUANTITIES : mass flow phi on patches inlet, mainOutlet, branchOutlet;
                split = |phi(mainOutlet)| / |phi(inlet)|. Read via flowRatePatch.
6. THE GATE   : |split_lab − 0.887| / 0.887 ≤ 0.03 (3%), at L3. Inside ⇒ GATE
                REACHED; outside ⇒ GATE FAIL. Tol = the manual's own 3% accuracy goal
                (§1.3): with a benchmark reference and no tighter provenance to lean
                on, tightening below the manual's stated class would not be defensible.
7. LADDER     : simpleFoam laminar (nu = 0.003333/1 = 0.003333 m²/s, air, manual p.39);
                fully-developed parabolic inlet Uc = 1.0 m/s via codedFixedValue; two
                pressure outlets at equal static pressure (p=0). Three birth-certified
                meshes (cases/ansys_verification/VMFL010/mesh_birth/).
8. SEED       : r=2 grid triple. N cells across the width W=1: L1/L2/L3 = 20/40/80,
                branch legs 3N. Cell counts 2800 / 11200 / 44800. Serial.
9. RISK       : **GEOMETRY FIDELITY — the named principal risk.** The split is
                sensitive to the exact junction/branch geometry and Reynolds number;
                the archive junction geometry could not be extracted here (no h5py,
                compressed HDF5), so the mesh is a defensible T-junction (junction
                1×1, legs L=3, W=1 per manual), NOT provably Hayes' exact geometry.
                A scratch smoke build of THIS geometry gave split 0.921 (vs 0.887,
                ~3.8% high) — i.e. even a perfect solver on this geometry risks GATE
                FAIL. **Build-time condition (amendable before first compute): extract
                the archive junction/lead geometry before the graded run; if it
                cannot be extracted, the graded verdict is honestly geometry-limited
                and may be GATE FAIL for that reason, recorded as such.**
10. ORDER     : formal p_f = 2 (bounded Gauss linear div, corrected laplacian).
                Expect p_obs ≈ 2 on the split; **p_obs > 2.3 SUSPICIOUS.**
11. WEDGE     : N/A — 2-D planar Cartesian, not axisymmetric. No sin(t)/t term.
12. COST      : ≈ 8 core-minutes total for the triple (2800–44800 cells, SIMPLE to
                residualControl 1e-7; smoke L1 = 1.9 wall-s at 400 iters). Basis =
                reported-by-owner (COMPUTE_BUDGET §5). CAP = 30 core-min; overrun STOPS.
13. CONTROLS  : comparator grade_vmfl010.py, --selftest GREEN. Planted-zero control
                fires on all three flow readers; mass-conservation guard (|in| =
                |main|+|branch| to 0.5%). Strict completion: rc, End, latest==endTime,
                age guard on 0/U (rule 4). Roache gating: non-CONVERGING ⇒ NOT A
                RESULT (rule 5). Success verdict is GATE REACHED, never PASS.
```

## Provenance of the driving input (NOT derived from the target)

The inlet **centerline velocity Uc = 1.0 m/s** (fully-developed parabolic profile)
was read from the **Ansys archive boundary profile** `plarb_r4.set.prof` — the `v`
column peaks at `1.000000e+00` at the width centre and is zero at both walls — **not**
back-solved from the 0.887 split. The manual p.39 text layer drops the profile
formula and its centerline value; the archive supplies it. Air ρ=1, μ=0.003333,
L=3.0, W=1.0 are on manual p.39. The archive's own converged Fluent run gives
mainOutlet/inlet = 0.591/0.667 = 0.887 (CONTEXT ONLY).

**Amendments before first compute** name the absent run directory and state the
condition checked (line 9 carries the one live condition). After first compute:
dated addenda only; no addendum may alter the gate, band, cap or the code-to-code
label.
