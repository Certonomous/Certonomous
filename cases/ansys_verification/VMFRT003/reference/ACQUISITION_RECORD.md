# VMFRT003 — ECN REFERENCE DATA ACQUISITION RECORD

**Case:** VMFRT003 — Engine Combustion Network Nonreacting Flow Case **bklfaAL4**
(Spray A, 100 MPa injection). Manual **page 261**.
**Reference form:** PROFILE — vapor and liquid penetration length vs time after
start of injection. This acquisition converts it from figure-only to
machine-readable.

**Retrieval:** inbound fetch only, `curl` from the manual-named `.gov` URLs,
**2026-09-10**. Nothing left the box (rule 7/8 untouched); the query was the URL
the manual itself prints.

## SOURCE, AS THE MANUAL PRINTS IT

- Data-search hub, sidecar **L6585–6586** (verbatim): *"Retrieved from Engine
  Combustion Network data search utility: https://ecn.sandia.gov/ecn-data-search/
  Accessed on April 7, 2020."* (April 7 2020 is the **manual's** access date.)
- Vapor file, sidecar **L6614**: `https://ecn.sandia.gov/cvdata/assets/datafiles/pen/bklfaAL4-pen.txt`
- Liquid file, sidecar **L6616**: `https://ecn.sandia.gov/cvdata/assets/datafiles/liq/bklfaAL4-liq.txt`

The manual names `bklfaAL4` as this case's own identity at sidecar **L6582**, so the
filenames map to the case by the manual's own naming, not by inference.

## WHAT ARRIVED (measured in the received files)

| file | sha256 | data rows | bytes |
|---|---|---|---|
| `bklfaAL4-pen.txt` | `964d90a82910680b7c4da6ddf476a6b46adffcd9b48eb967c98ba6261abc374f` | 941 | 25554 |
| `bklfaAL4-liq.txt` | `458f8ab6993a1204634982230902f668dc6981d848cc8ea14edb3070d1f9d530` | 1269 | 32692 |

## COLUMNS (verbatim, tab-separated) — A PARSER MUST HANDLE THE HTML ENTITY

- `bklfaAL4-pen.txt`: `time ASI [ms]` · `maximum vapor penetration [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`
- `bklfaAL4-liq.txt`: `time ASI [ms]` · `maximum liquid length [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`

**The `±` is stored as the literal HTML entity `&plusmn;`.** Any comparator reading
column 4's header must decode `&plusmn;` or it will misparse the header.

Sample rows (first non-zero point, verbatim):
- pen: `0.005	3.03	1.2269	1.4167`
- liq: `0.005	2.6806	0.3705	0.4705`

## STATED EXPERIMENTAL UNCERTAINTY

**Column 4 is the source's own stated experimental uncertainty:
`error ±2sigma/sqrt(N)` — a 95 % standard error, per timestep.** It is the term a
future tolerance derives from and is recorded here so it need not be rediscovered
by opening the file.

## GATE-CEILING CONSEQUENCE

The data is **experimental**. Under charter **§11.1 point 3**, any limb gated on it
is capped at **`GATE REACHED`**. Acquisition removes the reference-form blocker; it
does not lift that cap and does not make the case runnable (3-D transient spray,
Forte-class — a separate capability question, not decided here).
