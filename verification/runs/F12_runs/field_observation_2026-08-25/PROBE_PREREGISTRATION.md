# F12 RUNG-1 FIELD OBSERVATION ARM — pre-registration

**Registered 2026-08-25, cfd lane, BEFORE any compute of this arm.**
This arm GRADES NOTHING. It moves no gate, threshold, cap or label. It is an
observation arm under the cfd supervisor's triage
`verification/runs/F12_runs/RUNG2_DISPOSITION_AND_CRASH_TRIAGE_2026-08-25.md` §3.4.

## Question
WHERE in the domain, and at WHICH iteration, does the F12 rung-1 field first
depart? Discriminator: LOCALISED (indicts a boundary condition or the mesh at
that location) vs GLOBAL (indicts the initial state or the relaxation).

## What is changed relative to the registered rung-1 case — OUTPUT CONTROLS ONLY
`system/controlDict`:  `endTime` 6000 -> 15;  `writeInterval` 6000 -> 1;
`purgeWrite` 1 -> 0.  Nothing else.
NOT changed: every solver, smoother, preconditioner, tolerance, relTol,
residualControl entry, nNonOrthogonalCorrector count, pMinFactor, pMaxFactor,
every relaxation factor, every scheme, every boundary condition, every
`0/` field, `constant/`, and the mesh (copied byte-identical).
Ranks: 1 — which is what the REGISTERED rung 1 itself ran (`log.rhoSimpleFoam`
line 447, `nProcs : 1`). Rank count is therefore also unchanged.

## Cap — registered BEFORE the run (standing rule 12)
**10.0 core-minutes**, 1 rank, i.e. 600 wall s.  An overrun STOPS the run; it
does not get a new budget.  Basis: the registered rung 1 executed 148 iterations
in 13.29 s wall at 1 rank; 15 iterations is ~1.4 s.  The cap is ~430x the
expected spend and covers the planted-control reruns and the postProcess pass.

## Refusal conditions, committed in advance
1. If this arm cannot run without changing a lever, it STOPS and that fact is
   the finding, reported unchanged.
2. Standing rule 3: any "no departure here" is refused unless the field reader
   is first shown able to SEE a planted perturbation read back from disk.
3. The registered rung-1 directory is fingerprinted (sha256 of the sha256-list
   of every file under it) BEFORE and AFTER; inequality is a failure of this arm.
4. Rungs 2-5 asserted absent before and after.
5. `launch_f12_rung.py`, `F12_PREREGISTRATION.md` and rung 1's outputs are not
   edited.  The rung-2 interlock is not touched.
