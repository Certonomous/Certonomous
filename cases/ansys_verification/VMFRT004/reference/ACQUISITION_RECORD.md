# VMFRT004 — ECN REFERENCE DATA ACQUISITION RECORD

**Case:** VMFRT004 — Engine Combustion Network Nonreacting Flow Case **bkldaAL4**
(Spray A, 150 MPa injection). Manual **page 263**.
**Reference form:** PROFILE — vapor and liquid penetration length vs time after
start of injection. This acquisition converts it from figure-only to
machine-readable.

**Retrieval:** inbound fetch only, `curl` from the manual-named `.gov` URLs,
**2026-09-10**. Nothing left the box (rule 7/8 untouched); the query was the URL
the manual itself prints.

## SOURCE, AS THE MANUAL PRINTS IT

- Data-search hub, sidecar **L6663–6664** (verbatim): *"Retrieved from Engine
  Combustion Network data search utility: https://ecn.sandia.gov/ecn-data-search/
  Accessed on April 7, 2020."* (April 7 2020 is the **manual's** access date.)
- Vapor file, sidecar **L6692**: `https://ecn.sandia.gov/cvdata/assets/datafiles/pen/bkldaAL4-pen.txt`
- Liquid file, sidecar **L6694**: `https://ecn.sandia.gov/cvdata/assets/datafiles/liq/bkldaAL4-liq.txt`

The manual names `bkldaAL4` as this case's own identity at sidecar **L6660**, so the
filenames map to the case by the manual's own naming, not by inference.

## WHAT ARRIVED (measured in the received files)

| file | sha256 | data rows | bytes |
|---|---|---|---|
| `bkldaAL4-pen.txt` | `5df86a2115954dfbbffe70b04ed4974105cc5cdd8890eb49a7c826cc3f36b648` | 781 | 20930 |
| `bkldaAL4-liq.txt` | `dedf6cd14a4432f20e0d16f1500f602b477de4b34fc72734713b9cdabc2e076f` | 1421 | 37472 |

## COLUMNS (verbatim, tab-separated) — A PARSER MUST HANDLE THE HTML ENTITY

- `bkldaAL4-pen.txt`: `time ASI [ms]` · `maximum vapor penetration [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`
- `bkldaAL4-liq.txt`: `time ASI [ms]` · `maximum liquid length [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`

**The `±` is stored as the literal HTML entity `&plusmn;`.** Any comparator reading
column 4's header must decode `&plusmn;` or it will misparse the header.

Sample rows (first non-zero point, verbatim):
- pen: `0.005	2.1532	1.562	0.6817`
- liq: `0.005	0.4015	0.36027	0.27476`

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
