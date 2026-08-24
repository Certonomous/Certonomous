/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2019-2021 OpenCFD Ltd.
    Copyright (C) YEAR AUTHOR, AFFILIATION
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "fixedValueFvPatchFieldTemplate.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "unitConversion.H"
#include "PatchFunction1.H"

//{{{ begin codeInclude

//}}} end codeInclude


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * Local Functions * * * * * * * * * * * * * * //

//{{{ begin localCode

//}}} end localCode


// * * * * * * * * * * * * * * * Global Functions  * * * * * * * * * * * * * //

// dynamicCode:
// SHA1 = 9d9f75ceaa7aae19ef2f8f01cb1a11f7a87fb674
//
// unique function name that can be checked if the correct library version
// has been loaded
extern "C" void poiseuilleInlet_9d9f75ceaa7aae19ef2f8f01cb1a11f7a87fb674(bool load)
{
    if (load)
    {
        // Code that can be explicitly executed after loading
    }
    else
    {
        // Code that can be explicitly executed before unloading
    }
}

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

makeRemovablePatchTypeField
(
    fvPatchVectorField,
    poiseuilleInletFixedValueFvPatchVectorField
);

} // End namespace Foam


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::
poiseuilleInletFixedValueFvPatchVectorField::
poiseuilleInletFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(p, iF)
{
    if constexpr (false)
    {
        printMessage("Construct poiseuilleInlet : patch/DimensionedField");
    }
}


Foam::
poiseuilleInletFixedValueFvPatchVectorField::
poiseuilleInletFixedValueFvPatchVectorField
(
    const this_bctype& rhs,
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    parent_bctype(rhs, p, iF, mapper)
{
    if constexpr (false)
    {
        printMessage("Construct poiseuilleInlet : patch/DimensionedField/mapper");
    }
}


Foam::
poiseuilleInletFixedValueFvPatchVectorField::
poiseuilleInletFixedValueFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    parent_bctype(p, iF, dict)
{
    if constexpr (false)
    {
        printMessage("Construct poiseuilleInlet : patch/dictionary");
    }
}


Foam::
poiseuilleInletFixedValueFvPatchVectorField::
poiseuilleInletFixedValueFvPatchVectorField
(
    const this_bctype& rhs,
    const DimensionedField<vector, volMesh>& iF
)
:
    parent_bctype(rhs, iF)
{
    if constexpr (false)
    {
        printMessage("Construct poiseuilleInlet : copy/DimensionedField");
    }
}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void
Foam::
poiseuilleInletFixedValueFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }

    if constexpr (false)
    {
        printMessage("updateCoeffs poiseuilleInlet");
    }

//{{{ begin code
    #line 40 "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL005/L3_400x40/0/U/boundaryField/inlet"
const scalar R    = 0.00125;   // pipe radius [m]
            const scalar Vavg = 2.0;       // average velocity [m/s]
            const vectorField& Cf = this->patch().Cf();
            vectorField v(Cf.size(), vector::zero);
            forAll(Cf, i)
            {
                const scalar r  = Foam::sqrt(sqr(Cf[i].y()) + sqr(Cf[i].z()));
                scalar ux = 2.0*Vavg*(1.0 - sqr(r/R));
                if (ux < 0) ux = 0;
                v[i] = vector(ux, 0, 0);
            }
            operator==(v);
//}}} end code

    this->parent_bctype::updateCoeffs();
}


// ************************************************************************* //

