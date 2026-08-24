// Clamp e to [eMin_bound, eMax_bound] (see createFields.H for derivation),
// and report which cells needed it -- both the protective fix and the
// localisation diagnostic the original crash's own artifacts could not
// provide (no field write between t=0 and the SIGFPE at t=6.42e-7).
//
// INSTRUMENTED COPY -- verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md
// section 4.2. Everything below marked ADDED is additive diagnostic output. The
// published rhoCentralFoamBounded_src/boundE.H (md5 3c30480673b4b443ccc5ce7cceb53671)
// is NOT edited; this file lives only in rhoCentralFoamBoundedDiag_src/ and in
// the Step-1 tree copied from it. Inertness is ARGUED in prereg 4.2 and MEASURED
// by control C0 (prereg 6).
{
    const scalarField& eIn = e.primitiveField();

    // ADDED: read-only handles. rho and U are CURRENT at this point --
    // rho is advanced at :225 (continuity), U at :229-245 (momentum +
    // viscous correction), both before :265. T is NOT current: thermo.correct()
    // has not yet run for this step, so T lags by one correction. Reported
    // as Tprev and never as the clamped cell's temperature.
    // primitiveField() on a volField returns const Field<Type>&; there is no
    // non-const path from any of these three.
    const scalarField& rhoIn = rho.primitiveField();
    const vectorField& UIn   = U.primitiveField();
    const scalarField& TIn   = T.primitiveField();

    label nLow = 0, nHigh = 0;
    scalar worstLow = GREAT, worstHigh = -GREAT;
    label worstLowCell = -1, worstHighCell = -1;
    scalar xMinLow = GREAT, xMaxLow = -GREAT, rMinLow = GREAT, rMaxLow = -GREAT;

    // ADDED: function-local accumulators only. None outlives this block, none is
    // a field, a dimensioned quantity, a mesh object or a runTime entry.
    scalar rhoLowMin = GREAT, rhoLowMax = -GREAT;
    scalar magULowMin = GREAT, magULowMax = -GREAT;
    scalar TprevLowMin = GREAT, TprevLowMax = -GREAT;
    scalar worstLowRho = 0.0, worstLowMagU = 0.0, worstLowTprev = 0.0;

    // ADDED: 12 fixed histogram bin edges on implied T, in K:
    //   (-inf,0] (0,1] (1,2] (2,5] (5,10] (10,15] (15,18] (18,19] (19,19.5]
    //   (19.5,19.9] (19.9,19.99] (19.99,20)
    // The last bin is open at the top because a clamped cell has e < eMin_bound,
    // i.e. implied T strictly below TMin = 20 K by construction.
    FixedList<label, 12> histLow;
    forAll(histLow, bini)
    {
        histLow[bini] = 0;
    }

    const volVectorField& CC = mesh.C();

    forAll(eIn, celli)
    {
        const scalar v = eIn[celli];
        if (v < eMin_bound.value())
        {
            ++nLow;
            if (v < worstLow)
            {
                worstLow = v; worstLowCell = celli;
                // ADDED: the worst-low cell's own state, captured with it.
                worstLowRho   = rhoIn[celli];
                worstLowMagU  = mag(UIn[celli]);
                worstLowTprev = TIn[celli];
            }
            const scalar x = CC[celli].x();
            const scalar r = Foam::sqrt(sqr(CC[celli].y()) + sqr(CC[celli].z()));
            xMinLow = min(xMinLow, x); xMaxLow = max(xMaxLow, x);
            rMinLow = min(rMinLow, r); rMaxLow = max(rMaxLow, r);

            // ADDED: per-clamped-cell min/max over rho, |U| and the lagged T.
            const scalar rhoC   = rhoIn[celli];
            const scalar magUC  = mag(UIn[celli]);
            const scalar TprevC = TIn[celli];
            rhoLowMin   = min(rhoLowMin, rhoC);
            rhoLowMax   = max(rhoLowMax, rhoC);
            magULowMin  = min(magULowMin, magUC);
            magULowMax  = max(magULowMax, magUC);
            TprevLowMin = min(TprevLowMin, TprevC);
            TprevLowMax = max(TprevLowMax, TprevC);

            // ADDED: exact hConst inversion of the CURRENT e -- T = Tref + e/Cv,
            // with Cv_bound and Tref_bound the same constants createFields.H
            // :110-123 already uses to build eMin_bound. This is the clamped
            // cell's real temperature; TIn is not.
            const scalar Timp = Tref_bound + v/Cv_bound;
            label bini = 11;
            if      (Timp <=  0.00) bini =  0;
            else if (Timp <=  1.00) bini =  1;
            else if (Timp <=  2.00) bini =  2;
            else if (Timp <=  5.00) bini =  3;
            else if (Timp <= 10.00) bini =  4;
            else if (Timp <= 15.00) bini =  5;
            else if (Timp <= 18.00) bini =  6;
            else if (Timp <= 19.00) bini =  7;
            else if (Timp <= 19.50) bini =  8;
            else if (Timp <= 19.90) bini =  9;
            else if (Timp <= 19.99) bini = 10;
            ++histLow[bini];
        }
        else if (v > eMax_bound.value())
        {
            ++nHigh;
            if (v > worstHigh) { worstHigh = v; worstHighCell = celli; }
        }
    }

    if (nLow > 0)
    {
        Info<< "BOUND: e below eMin in " << nLow << " cell(s) at Time = "
            << runTime.timeName() << ", worst e = " << worstLow
            << " J/kg at cell " << worstLowCell
            << " C = " << mesh.C()[worstLowCell]
            << " | low-e cell extent: x=[" << xMinLow << "," << xMaxLow
            << "] r=[" << rMinLow << "," << rMaxLow << "]" << endl;

        // ADDED: two Info lines, tagged so a reader cannot confuse them with the
        // existing one. The time token is runTime.timeName() -- the SAME token
        // the BOUND: line above prints, which is how the grading reader keys
        // them together. Info<< writes to stdout only: not a reduction, not a
        // synchronisation point, and this case is serial (nProcs : 1).
        Info<< "BOUNDDIAG: t=" << runTime.timeName()
            << " nLow=" << nLow
            << " rhoLow=[" << rhoLowMin << "," << rhoLowMax << "]"
            << " magULow=[" << magULowMin << "," << magULowMax << "]"
            << " TprevLow=[" << TprevLowMin << "," << TprevLowMax << "]"
            << " worst: cell=" << worstLowCell
            << " rho=" << worstLowRho
            << " magU=" << worstLowMagU
            << " Tprev=" << worstLowTprev
            << " Timp=" << (Tref_bound + worstLow/Cv_bound)
            << endl;

        Info<< "BOUNDHIST: t=" << runTime.timeName()
            << " nLow=" << nLow << " bins=";
        forAll(histLow, bini)
        {
            if (bini > 0) { Info<< " "; }
            Info<< histLow[bini];
        }
        Info<< endl;
    }
    if (nHigh > 0)
    {
        Info<< "BOUND: e above eMax in " << nHigh << " cell(s) at Time = "
            << runTime.timeName() << ", worst e = " << worstHigh
            << " J/kg at cell " << worstHighCell
            << " C = " << mesh.C()[worstHighCell] << endl;
    }

    e = min(max(e, eMin_bound), eMax_bound);
}
