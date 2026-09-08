// Clamp internal energy e to [eMin_bound, eMax_bound] (see createFields.H for the
// DMR derivation) and report which cells needed it -- both the positivity-
// preserving fix and the localisation diagnostic the DMR crash's own artifacts
// could not provide (the failing R3 step at t=0.15464 was never written, so the
// cell/coordinate of the negative-T excursion at the reflecting-wall foot was
// never captured).
//
// The element-wise clip `e = min(max(e, eMin_bound), eMax_bound)` mirrors the
// proven rhoCentralFoamBounded (F4 SWBLI) boundE.H byte-for-byte. Two deliberate
// differences from that solver, both justified:
//   1. DMR is PLANAR (x-y, empty frontAndBack), so the low-e cell extent is
//      reported in (x,y), not the axisymmetric (x,r) of the cylinder-flare.
//   2. This case runs 4-rank (mpirun), so the FIRING COUNT and WORST e are reduced
//      to global values (returnReduce) -- an excursion living on a non-master rank
//      would otherwise be invisible in a master-only Info print. The per-rank cell
//      and coordinate of the excursion are emitted with Pout, so the rank actually
//      holding the negative-T cell reports it whichever rank that is.
//
// POSITIVITY-PRESERVING SAFEGUARD, NOT a numerical scheme change: with TMin = 1e-3
// (three orders below the coldest physical DMR state, ambient T = 1.0) the low
// clip fires ONLY on a nonphysical near-zero/negative-T excursion -- the crash
// itself. Every `BOUND:` line printed below is therefore a MEASURED report of an
// impossible state, not a routine correction. If eMax ever binds (TMax = 1e4,
// well above any true DMR peak) that too is a reported finding (a diverging solve),
// never a silent fix.
{
    const scalarField& eIn = e.primitiveField();
    const volVectorField& CC = mesh.C();

    label nLowLocal = 0, nHighLocal = 0;
    scalar worstLowLocal = GREAT, worstHighLocal = -GREAT;
    label worstLowCell = -1, worstHighCell = -1;
    scalar xMinLow = GREAT, xMaxLow = -GREAT, yMinLow = GREAT, yMaxLow = -GREAT;

    forAll(eIn, celli)
    {
        const scalar v = eIn[celli];
        if (v < eMin_bound.value())
        {
            ++nLowLocal;
            if (v < worstLowLocal) { worstLowLocal = v; worstLowCell = celli; }
            const scalar x = CC[celli].x();
            const scalar y = CC[celli].y();
            xMinLow = min(xMinLow, x); xMaxLow = max(xMaxLow, x);
            yMinLow = min(yMinLow, y); yMaxLow = max(yMaxLow, y);
        }
        else if (v > eMax_bound.value())
        {
            ++nHighLocal;
            if (v > worstHighLocal) { worstHighLocal = v; worstHighCell = celli; }
        }
    }

    const label nLow  = returnReduce(nLowLocal,  sumOp<label>());
    const label nHigh = returnReduce(nHighLocal, sumOp<label>());

    if (nLow > 0)
    {
        const scalar gWorstLow = returnReduce(worstLowLocal, minOp<scalar>());
        Info<< "BOUND: e below eMin in " << nLow << " cell(s) at Time = "
            << runTime.timeName() << ", global worst e = " << gWorstLow
            << " J/kg (eMin_bound = " << eMin_bound.value() << ")" << endl;
        if (nLowLocal > 0)
        {
            Pout<< "  BOUND-LOC: " << nLowLocal << " low-e cell(s), worst e = "
                << worstLowLocal << " J/kg at cell " << worstLowCell
                << " C = " << CC[worstLowCell]
                << " | low-e cell extent: x=[" << xMinLow << "," << xMaxLow
                << "] y=[" << yMinLow << "," << yMaxLow << "]" << endl;
        }
    }
    if (nHigh > 0)
    {
        const scalar gWorstHigh = returnReduce(worstHighLocal, maxOp<scalar>());
        Info<< "BOUND: e above eMax in " << nHigh << " cell(s) at Time = "
            << runTime.timeName() << ", global worst e = " << gWorstHigh
            << " J/kg (eMax_bound = " << eMax_bound.value() << ")" << endl;
        if (nHighLocal > 0)
        {
            Pout<< "  BOUND-LOC: " << nHighLocal << " high-e cell(s), worst e = "
                << worstHighLocal << " J/kg at cell " << worstHighCell
                << " C = " << CC[worstHighCell] << endl;
        }
    }

    e = min(max(e, eMin_bound), eMax_bound);
}
