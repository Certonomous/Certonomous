# VMFRT005 — ECN REFERENCE DATA ACQUISITION RECORD

**Case:** VMFRT005 — Engine Combustion Network **Reacting** Flow Case **jkldaAL4**
(Spray A, 150 MPa injection, O2 = 15 %). Manual **page 265**.
**Reference form:** DISCRETE printed scalars **and** a machine-readable vapor
penetration profile — see the two subsections below. This acquisition adds the
profile; the scalars were already numeric in the manual.

**Retrieval:** inbound fetch only, `curl` from the manual-named `.gov` URL,
**2026-09-10**. Nothing left the box (rule 7/8 untouched); the query was the URL
the manual itself prints.

> NOTE: the detailed chemical mechanism for this case is filed separately under
> `../mechanism/` with its own `ACQUISITION_RECORD.md`. This record covers the ECN
> **reference data** only.

## SOURCE, AS THE MANUAL PRINTS IT

- Data-search hub, sidecar **L6741–6742** (verbatim): *"Retrieved from Engine
  Combustion Network data search utility: https://ecn.sandia.gov/ecn-data-search/
  Accessed on April 7, 2020."* (April 7 2020 is the **manual's** access date.)
- Vapor file, sidecar **L6770**: `https://ecn.sandia.gov/cvdata/assets/datafiles/pen/jkldaAL4-pen.txt`
- **No liquid file.** The manual states at **L6765–6766**: *"No liquid penetration
  length measurements were found on the ECN repository for this case, but
  experimental data for the vapor penetration length can be found ... in the form
  of a text file."* So only `jkldaAL4-pen.txt` exists — its absence of a `-liq`
  sister is expected, not an incomplete fetch.

The manual names `jkldaAL4` as this case's own identity at sidecar **L6738**.

**Filename-casing note (L-144 class):** the bullet at sidecar **L6768** spells the
file `jkldaAl4-pen.txt` (lowercase `l`), but the URL and the actually-served file
are `jkldaAL4-pen.txt` (uppercase `AL`). The served file matches the URL, not the
bullet's casing; recorded so a later reader does not chase the bullet's spelling.

## PART A — THE MACHINE-READABLE PROFILE (newly acquired)

| file | sha256 | data rows | bytes |
|---|---|---|---|
| `jkldaAL4-pen.txt` | `7bac133e5c588badab771921a134dc07b0a6bfdcd55e2e078e223f7f18568988` | 751 | 19632 |

**Columns (verbatim, tab-separated):** `time ASI [ms]` · `maximum vapor
penetration [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`.

**The `±` is stored as the literal HTML entity `&plusmn;`.** A comparator reading
column 4's header must decode `&plusmn;` or it will misparse the header.

Sample row (first row, verbatim; early points use scientific notation):
`-0.025	2.088e-006	5.1146e-006	4.5746e-006`

**Column 4 is the source's own stated experimental uncertainty:
`error ±2sigma/sqrt(N)` — a 95 % standard error, per timestep.**

## PART B — THE DISCRETE REFERENCE SCALARS (from the manual, verified against the PDF)

The manual prints a `Target / Predicted` table for this case. **Verified against
the PDF page itself** (physical PDF page **281**, printed page **267**), not only
the sidecar:

| quantity | Target (reference) | Forte Predicted |
|---|---|---|
| Lift-off length | **16.7 mm** | 18.0 mm |
| Ignition delay time | **0.41 ms** | 0.7 ms |

**"Target" is the reference result the case gates against** in the Ansys VM
convention; "Predicted" is Forte's own solve. So 16.7 mm and 0.41 ms are genuine
printed-scalar references, not incidental numbers. The manual attributes the
overprediction (sidecar L6774–6776) to *"imperfections in the low temperature
chemical kinetics"* — which is exactly what the separately-acquired nC12 mechanism
addresses.

**Standing of VMFRT005:** it is the only VMFRT case that carries **all three** of a
printed-scalar reference (Part B), a machine-readable profile (Part A), and an
already-acquired chemical mechanism (`../mechanism/`). That makes it the strongest
never-run candidate in the Forte suite on reference grounds — the cost/capability
question is separate and undecided.

## GATE-CEILING CONSEQUENCE

All references here are **experimental** (ECN spray database). Under charter
**§11.1 point 3**, any limb gated on them — profile or scalar — is capped at
**`GATE REACHED`**. Acquisition removes the reference-form blocker; it does not lift
that cap and does not make the case runnable (3-D transient reacting spray with
detailed chemistry — a new physics class for this box, not decided here).
