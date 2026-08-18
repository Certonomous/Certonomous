# W3 — how much of the cube's published envelope is its solve not stopping

**Written 2026-08-02 06:25 UTC, launched 06:24:48, with no result read.** The
mesh is the cube's own production mesh, rebuilt from the same dictionaries that
produced 299 493 cells an hour ago; the only change to any file is
`controlDict`'s `endTime` and `writeInterval`, 300 → 3000.

Follows `W3_PUBLISHED_RUNG_REPLICATES.md` §5, which named this experiment,
priced it, and declined to do it inside a rung item. Authorised under the
standing blanket approval recorded on `r4-asymptotic-range-ladders`
(2026-07-31, "OK for all ur proposals, dont wait for me to confirm"), with the
cost basis below as the gate.

---

## 1. The question, and why it is worth 60 core-minutes

The cube's credentials-wall row publishes **±0.0078 "across the 3-mesh
refinement study"**. Measured tonight:

* no cube solve — not the original behind the credential, not either of two
  re-solves — prints "SIMPLE solution converged"; all three stop at
  `run_uq_studies`' fixed 300-iteration cap;
* the original run's final-20% window 2σ is **7.255 × 10⁻³**, which is **93%**
  of that envelope;
* the same mesh at a different rank count moves the answer **5.98 × 10⁻³**,
  76% of it;
* and the whole three-rung ladder spans **6.26 × 10⁻³** across a 5.6× change
  in cells — less than one rung's own iterative wobble.

So the envelope is being read as a discretization uncertainty and may be
mostly the solve still moving. **One long run settles which.** It is the
cheapest way to find out and it needs no new mesh.

## 2. What is running

The cube production mesh, `residualControl` untouched at 1e-4, kOmegaSST,
magUInf 100, `lRef` 1, `Aref` 1, **4 MPI ranks scotch, ~74 900 cells per
rank**, `endTime` 3000 instead of 300. The force history is written every
iteration, so one run yields the whole settle curve rather than a single
endpoint.

**Cost, before the fact.** The same case ran 300 iterations in 189.68 s of
`ExecutionTime` on 4 ranks, so 3000 iterations is estimated at **≈1900 s
ExecutionTime, ≈126 core-minutes**, and less if `residualControl` fires first.
That is the whole gate: if it does not settle by 3000 it will be reported as
not settling by 3000, and no further budget goes into it tonight.

## 3. Predictions, on the record before the run finishes

**P1 — the cube settles, and it settles late.** The NACA 0012 and 4412 reach
`residualControl` in 117–156 iterations; the cube does not in 300.
**Predicted: it converges between 600 and 3000 iterations.** If it does not
converge at all in 3000, the cube's steady solve is not steady and the finding
is about the flow, not the budget — which is what R4 found on the Ahmed 25° at
834 351 cells.

**P2 — the value moves by more than the published envelope claims to cover.**
The three 300-iteration means measured tonight are 1.102404922, 1.108388909 and
1.093505136. **Predicted: the settled Cd sits outside the interval [1.1024 −
0.0078, 1.1024 + 0.0078] = [1.0946, 1.1102] around the value the credential
publishes.** If it lands inside, the envelope survives its own solve and that
is worth knowing too.

**P3 — the trailing-window spread at 300 iterations is not small compared with
what is left to move.** **Predicted: |Cd(settled) − Cd(300)| exceeds the 300-
iteration window 2σ of 1.4686 × 10⁻²**, i.e. the wobble at the cap
under-reports the distance still to travel — which is exactly the failure mode
`tmr_verification`'s own comment records on the 208 896-cell flat plate, where
the value at the 15 000 cap sat 1.05% above where it settled while its
tail-50 spread suggested a plateau.

## 4. What will not be done with the answer

**The cube's wall row will not be edited tonight whatever this returns.** Its
envelope is inside the open ruling
`w3-a-declined-ladder-still-publishes-an-envelope`, and a number about to be
ruled on should move once, by the ruling. This run supplies the ruling with a
number it does not currently have: how much of that envelope is discretization
and how much is a solve that was stopped by a constant.

*Nothing below this line existed when the solver was launched.*
