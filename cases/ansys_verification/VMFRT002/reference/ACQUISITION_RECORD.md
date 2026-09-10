# VMFRT002 — ECN REFERENCE DATA ACQUISITION RECORD

**Case:** VMFRT002 — Engine Combustion Network Nonreacting Flow Case **bklraAL4**
(Spray A, 50 MPa injection). Manual **page 259**.
**Reference form:** PROFILE — vapor and liquid penetration length vs time after
start of injection. This acquisition converts it from figure-only to
machine-readable.

**Retrieval:** inbound fetch only, `curl` from the manual-named `.gov` URLs,
**2026-09-10**. Nothing left the box (rule 7/8 untouched); the query was the URL
the manual itself prints.

## SOURCE, AS THE MANUAL PRINTS IT

- Data-search hub, sidecar **L6510–6511** (verbatim): *"Retrieved from Engine
  Combustion Network (ECN) data search utility:
  https://ecn.sandia.gov/ecn-data-search/ Accessed on April 7, 2020."*
  (April 7 2020 is the **manual's** access date, not ours.)
- Vapor file, sidecar **L6540**: `https://ecn.sandia.gov/cvdata/assets/datafiles/pen/bklraAL4-pen.txt`
- Liquid file, sidecar **L6544**: `https://ecn.sandia.gov/cvdata/assets/datafiles/liq/bklraAL4-liq.txt`

The manual names `bklraAL4` as this case's own identity at sidecar **L6507**
(*"Engine Combustion Network Nonreacting Flow Case - bklraAL4"*), so the filenames
map to the case by the manual's own naming, not by inference.

## WHAT ARRIVED (measured in the received files)

| file | sha256 | data rows | bytes |
|---|---|---|---|
| `bklraAL4-pen.txt` | `b5b1b04d87c93db01c44bf8b8997548c54b1f85451a5b849c8ea6cce4f3cf5b7` | 1281 | 34155 |
| `bklraAL4-liq.txt` | `a4b78c50b4974d543fea362f97b18539d0a13dd8d89383cb0e5466df6da7b964` | 1269 | 33840 |

## COLUMNS (verbatim, tab-separated) — A PARSER MUST HANDLE THE HTML ENTITY

- `bklraAL4-pen.txt`: `time ASI [ms]` · `maximum vapor penetration [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`
- `bklraAL4-liq.txt`: `time ASI [ms]` · `maximum liquid length [mm]` · `standard deviation [mm]` · `error &plusmn;2sigma/sqrt(N) [mm]`

**The `±` is stored as the literal HTML entity `&plusmn;`, not a Unicode/ASCII
character.** Any comparator reading column 4's header must decode `&plusmn;` or it
will misparse the header.

Sample rows (first non-zero point, verbatim):
- pen: `0.005	1.1817	0.92906	1.0728`
- liq: `0.005	1.008	0.22778	0.36302`

## STATED EXPERIMENTAL UNCERTAINTY — the reason this file matters

**Column 4 is the source's own stated experimental uncertainty:
`error ±2sigma/sqrt(N)` — a 95 % standard error, given per timestep.** This is the
term a future tolerance derives from; it must not be discoverable only by opening
the file, so it is recorded here.

## GATE-CEILING CONSEQUENCE

The data is **experimental**. Under charter **§11.1 point 3**, any limb gated on it
is capped at **`GATE REACHED`** — a converging triple cannot buy `PASS`. Acquisition
removes the reference-form blocker; it does not lift that cap and it does not make
the case runnable (3-D transient spray, Forte-class — a separate capability
question, not decided here).
