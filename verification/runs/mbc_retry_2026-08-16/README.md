# mbc retry sequence, 2026-08-16

Ten logs from five consecutive retry batches, run 13:47-14:24 on 2026-08-16. They
sat loose at the repository root until 2026-08-18, when the filing charter's R1
rule reported them. **The move is the only thing that changed; no file was edited.**

The sequence is legible from the tails and is recorded here because it ends well:

| batch | outcome |
| --- | --- |
| `mbc_retry` | batch finished, 1 failed stage |
| `mbc_retry2` | batch finished, 1 failed stage |
| `mbc_retry3` | empty log; its `.err` carries `SyntaxError: unterminated string literal (detected at line 349)` -- the batch died before it ran |
| `mbc_retry4` | batch finished, 1 failed stage |
| `mbc_retry6` | **batch finished, 0 failed stages** |

There is no `mbc_retry5`. Whether it was never run or was removed is not
recorded anywhere found on 2026-08-18, and no claim is made either way.

**Nothing here is graded**, and the closing zero is not a result: it is the last
line of a log whose batch was never re-verified. A rung that wants this outcome
re-runs it.
