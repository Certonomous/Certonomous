// Clamp e to [eMin_bound, eMax_bound] (see createFields.H for derivation),
// and report which cells needed it -- both the protective fix and the
// localisation diagnostic the original crash's own artifacts could not
// provide (no field write between t=0 and the SIGFPE at t=6.42e-7).
{
    const scalarField& eIn = e.primitiveField();

    label nLow = 0, nHigh = 0;
    scalar worstLow = GREAT, worstHigh = -GREAT;
    label worstLowCell = -1, worstHighCell = -1;
    scalar xMinLow = GREAT, xMaxLow = -GREAT, rMinLow = GREAT, rMaxLow = -GREAT;

    const volVectorField& CC = mesh.C();

    forAll(eIn, celli)
    {
        const scalar v = eIn[celli];
        if (v < eMin_bound.value())
        {
            ++nLow;
            if (v < worstLow) { worstLow = v; worstLowCell = celli; }
            const scalar x = CC[celli].x();
            const scalar r = Foam::sqrt(sqr(CC[celli].y()) + sqr(CC[celli].z()));
            xMinLow = min(xMinLow, x); xMaxLow = max(xMaxLow, x);
            rMinLow = min(rMinLow, r); rMaxLow = max(rMaxLow, r);
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
