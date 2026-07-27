# Mega-batch ledger: the 1,168 duplicate rows

Measured 2026-07-27 03:20 UTC against `ledger.jsonl` as it stood at 180,369
lines (the state left by the STOP sentinel). Every number below is counted
from the file, not estimated. No rows were added, altered, or removed to
produce this document.

## What is actually in the file

| Quantity | Count |
| --- | --- |
| Lines in file | 180,369 |
| Lines that parse as JSON | 180,368 |
| Lines that do not parse | 1 (line 61,438) |
| Distinct `index` values | 179,200 |
| Indices appearing more than once | 1,168 |
| Extra rows beyond first occurrence | 1,168 |
| Maximum multiplicity | 2 (no index appears three times) |
| Index range of the duplicates | 59,899 to 61,068 |
| File-line span of the duplicate rows | 59,900 to 62,246 |
| Index range overall | 0 to 179,199, contiguous and complete |

The duplicate count matches the 1,168 reported in the handover exactly.

## The duplicates are not all equivalent

Each duplicated index has exactly two rows. Sorting the pairs by whether each
attempt succeeded is what decides the de-duplication question:

| First attempt | Retry | Pairs | Consequence |
| --- | --- | --- | --- |
| ok | ok | 1,106 | Redundant. Adds no information. |
| failed | ok | 37 | The retry rescued the evaluation. |
| ok | failed | 15 | The first attempt is the good one. |
| failed | failed | 10 | No successful row exists for these indices. |

This reconciles against the failure count exactly: 37 + 15 + (10 x 2) = 72,
and the ledger contains 72 rows with `ok: false`. All 72 carry an empty
`metrics` object, which is the runner behaving correctly. It records the
failure rather than fabricating a result.

All 72 failures fall between file lines 59,903 and 62,248, entirely inside the
duplicate zone. Their error strings carry Windows paths
(`C:\Users\mouza\github-cleanup\...`), which places the whole episode in the
earlier Windows session and nowhere else. The 178,000-plus rows outside that
zone contain no failures at all.

## The torn line

Line 61,438 is a fragment beginning mid-token:

```
cy": null, "extrapolated": false, "built_span": 61.818, "built_area": 258.427}, "ok": true, "wall_seconds": 6.609}
```

It is the tail of a wing row whose head was lost. It sits inside the duplicate
zone, which is consistent with the same cause as the duplicates: unsynchronized
concurrent appends during the Windows session. The distiller currently skips
this line silently. That is why the study reports 180,368 rows for a 180,369
line file.

## Does the restart depend on any of this? No

The runner resumes from `load_done_indices`, which builds a **set** of indices
already present. Duplicates collapse in a set, so they neither repeat nor skip
work. Indices 0 through 179,199 are present and contiguous, so the batch
resumes cleanly at 179,200. Verified on the 2026-07-27 restart: it logged
`resuming: 179200 indices already in ledger` and began issuing 179,200 upward.

**The duplicates cost nothing operationally.** They cost accuracy only in the
published statistics.

## What they do corrupt: the published counts

`learned_study.json` counts rows, not distinct evaluations. Every headline
number derived from it is therefore inflated:

| Published figure | Currently says | Distinct-evaluation truth | Error |
| --- | --- | --- | --- |
| Evaluations in the fleet | 180,368 | 179,200 | +1,168 (+0.65%) |
| Completed (ok) evaluations | 180,296 | 179,190 | +1,106 |
| Failed evaluations | 72 | 10 | 7.2x overstated |
| Failure rate | 0.040% | 0.0056% | 7.2x overstated |

The failure-rate error is the significant one. The study's own line, "72 of
180368 attempted evaluations failed", counts 62 failures that were subsequently
retried and succeeded. Those are not fleet failures; they are transient
failures that the fleet recovered from. Only 10 indices have no successful row.

Effect on the physics fits is small but real: 1,106 designs carry double weight
out of 179,200, a 0.62% reweighting concentrated in one contiguous index band.
That band is not a random sample of the design space, so the bias is not
guaranteed to cancel. It is well below the reported precision of the slopes and
r-squared values, but it is not zero.

## Recommendation

**Do not delete rows from the ledger.** It is an append-only durable record and
the 72 failure rows are the evidence for the reliability claim. Deleting them
would destroy the audit trail and would make the reliability number
unfalsifiable.

**De-duplicate in the distiller instead**, at read time, with a prefer-ok rule:

> For each `index`, keep the successful row. If both attempts failed, keep one.

The rule matters more than it looks. A naive de-duplication in either direction
corrupts data:

- **Keep-first** discards 37 good solves and keeps 37 failures in their place.
- **Keep-last** discards 15 good solves and keeps 15 failures in their place.

Only prefer-ok is correct. Neither naive rule should be used.

The torn line 61,438 should be **counted and reported** rather than silently
skipped, so that the row count reconciles against `wc -l` and a future torn
write cannot hide.

## Status

Reported, not acted on. Changing the distiller changes numbers that are already
published to the website, so that is Katie's call, not the supervisor's. The
ledger is untouched and the 1,168 rows remain in place as instructed.
