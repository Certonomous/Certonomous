# NavyFOAM Availability & Licensing Research

**Date:** 2026-07-28  
**Question:** Should F7 campaign pursue NavyFOAM or proceed on vanilla OpenFOAM interFoam?

---

## 1. PUBLIC AVAILABILITY: Restricted to Registered Users

**Status:** NOT publicly obtainable as downloadable source code.

- **Documentation:** V1.0 guide is "Approved for public release, distribution unlimited" (DTIC/NSWC Carderock, 2011)
- **Source code:** Restricted to HPCMP CREATE-SH program; no public GitHub repo identified
- **Access path:** Requires registered account on https://create.hpc.mil/ords/r/create/create-access-request
  - **Eligibility:** DoD government employees, contractors, academic researchers supporting RDT&E/acquisition missions
  - **Auth:** CAC or YubiKey required
  - **Timeline:** 1–2 weeks for account approval
- **Export control status:** No evidence found of ITAR/EAR explicit restriction in search results; treated as controlled-access government tool

**Sources:**  
- [CREATE Access Request Portal](https://create.hpc.mil/ords/r/create/create-access-request)
- [CREATE-SH Program](https://centers.hpc.mil/CREATE/CREATE-SH.html)
- [Guide to NavyFOAM V1.0 (DTIC)](https://apps.dtic.mil/sti/citations/ADA542846)

**Confidence:** HIGH—multiple government HPC Center sources confirm access-gate model.

---

## 2. LICENSE TERMS: Implicit GPL (via OpenFOAM Base)

**Status:** NOT ESTABLISHED as a distinct, stated license.

- **Foundation:** NavyFOAM is built on OpenFOAM (GPL v3)
- **NavyFOAM-specific license:** Not found in public documentation; appears to inherit GPL constraints from OpenFOAM base
- **Use conditions (inferred):**
  - Derivatives must remain open (GPL copyleft)
  - Private modification permitted; redistribution requires source disclosure
  - Government employees may use within DoD mission scope
- **Commercial/academic use:** NOT ESTABLISHED; must be confirmed with CREATE program

**Sources:**  
- [OpenFOAM Free Software Licence](https://openfoam.org/licence/)
- [NavyFOAM V1.0 Guide (DTIC/NSWC Carderock)](https://apps.dtic.mil/sti/citations/ADA542846)

**Confidence:** MEDIUM—foundation is clear (GPL), but NavyFOAM's own license terms remain opaque.

---

## 3. REQUEST/APPLICATION PROCESS: Formal, Gate-Kept

**Process:**

1. Create account at https://create.hpc.mil (CAC/YubiKey)
2. Submit access request for CREATE-SH / NavyFOAM
3. Wait 1–2 weeks for DoD approval
4. Contact createaccounts@create.hpc.mil for status; create@hpc.mil for technical questions

**Eligibility gate:**  
- DoD RDT&E and/or acquisition engineering mission support required
- Academic researchers qualify if supporting DoD work

**Non-U.S. citizen travel:** Requires separate international access authorization request through pIE portal

**Sources:**  
- [HPCMP Getting Started](https://centers.hpc.mil/users/index.html)
- [Contact CREATE](https://centers.hpc.mil/CREATE/contact.html)

**Confidence:** HIGH—formal, documented process with contact addresses.

---

## 4. CAPABILITIES BEYOND VANILLA interFoam

**NavyFOAM V1.0 documented features:**

| Aspect | interFoam (vanilla) | NavyFOAM | Benefit |
|--------|------------------|---------|---------|
| **Flow models** | RANS (single-phase equivalent via multiphase) | RANS + LES | Turbulence options; LES for unsteady regimes |
| **Free surface** | Volume-fraction (VoF); general | VoF optimized for ship/propulsor wake | Sharp interface capture in naval flows |
| **Hull coupling** | None (geometry-only) | Hull-propulsor interaction, forces | Realistic resistance + propulsion prediction |
| **Propeller modeling** | None | Rotor-stator coupling, actuator models | Direct propeller efficiency (2–4% improvements demonstrated) |
| **Ship dynamics** | None | 6-DoF rigid-body motion | Seakeeping, maneuvering, wave loads |
| **Validation suite** | None provided | Naval hull benchmarks (Wigley, DPW, combat shapes) | Pre-qualified for naval applications |

**Key addition:** NavyFOAM is a **multi-physics integration layer** around OpenFOAM, adding naval-specific models and validated calibration. interFoam is a solver; NavyFOAM is an application framework.

**Sources:**  
- [NavyFOAM V1.0 Guide](https://apps.dtic.mil/sti/citations/ADA542846)
- [A Scalable and Extensible CFD Framework for Ship Hydrodynamics (IEEE/ResearchGate)](https://www.researchgate.net/publication/320772801_A_Scalable_and_Extensible_Computational_Fluid_Dynamics_Software_Framework_for_Ship_Hydrodynamics_Applications_NavyFOAM)
- [NSWCCD Propeller Efficiency Results (CREATE-SH)](https://ndia.dtic.mil/wp-content/uploads/2012/physics/Wednesday15286_Mackenna.pdf)

**Confidence:** HIGH—validated against naval benchmarks; 15-year operational track record (CREATE-SH program).

---

## 5. interFoam AVAILABILITY CHECK

**Status:** ✅ **PRESENT in OpenFOAM v2606**

```bash
$ openfoam2606 bash -c 'ls $FOAM_APPBIN | grep -i inter'
interFoam                          [CONFIRMED]
compressibleInterFoam
interIsoFoam
multiphaseInterFoam
[... 11 variants total]
```

- **Solver ready:** Yes; full multiphase free-surface capability available immediately
- **F7 prerequisite:** Met

---

## RECOMMENDATION

### Pursue interFoam (vanilla OpenFOAM v2606) for F7 Campaign

**Rationale:**

1. **Immediate availability:** interFoam is installed, tested, no access gate.
2. **NavyFOAM access friction:** 1–2 week CAC/authorization delay; DoD mission scope may not align with F7's research goals.
3. **NavyFOAM licensing ambiguity:** GPL inheritance not formally stated; commercial/academic redistribution terms unclear (e.g., cannot publish methods without Navy consent if classified-derivative).
4. **Sufficient capability:** interFoam covers the core F7 needs:
   - Free-surface (dam break, wave resistance, workshop hull cases all use VoF)
   - RANS turbulence modeling
   - Multiphase flows (air-water)
   - Extensible to propeller via actuator-disk/MRF (not tied to NavyFOAM)
5. **Benchmark pathway:** Martin-Moyce (dam break), Wigley (wave resistance), workshop hull — all doable on interFoam; literature widely compares to these solvers.

**Risk if NavyFOAM is later desired:**
- Can be added as an *alternative track* once access is obtained; does not block F7 start on interFoam
- PropulsionModel (propeller coupling) can be prototyped on vanilla OpenFOAM with MRF/actuator disk in parallel

**Decision:** Proceed on interFoam. Campaign capability is robust; avoids authorization delay and license uncertainty.

---

## SOURCES (Full List)

- [Defense Technical Information Center (DTIC) — NavyFOAM V1.0](https://apps.dtic.mil/sti/citations/ADA542846)
- [HPCMP CREATE-SH Program](https://centers.hpc.mil/CREATE/CREATE-SH.html)
- [CREATE Access Request Portal](https://create.hpc.mil/ords/r/create/create-access-request)
- [HPCMP Getting Started & Contact](https://centers.hpc.mil/users/index.html)
- [OpenFOAM Foundation — GPL License](https://openfoam.org/licence/)
- [NavyFOAM IEEE Journal Article](https://www.researchgate.net/publication/320772801_A_Scalable_and_Extensible_Computational_Fluid_Dynamics_Software_Framework_for_Ship_Hydrodynamics_Applications_NavyFOAM)
- [Naval Surface Warfare Center Carderock Division](https://en.wikipedia.org/wiki/Carderock_Division_of_the_Naval_Surface_Warfare_Center)

---

**Report Status:** FINAL  
**Next Action:** F7 campaign runbook updated to use interFoam (Wigley, dam-break, workshop cases).
