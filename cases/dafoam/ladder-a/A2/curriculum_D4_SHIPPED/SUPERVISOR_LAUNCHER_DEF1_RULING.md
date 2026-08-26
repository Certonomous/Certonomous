# D4-SHIPPED — **`D4-LAUNCHER-DEF-1`: A DESTRUCTIVE DEFECT CAUGHT IN PRE-FLIGHT. FIRING D4-SHIPPED WOULD HAVE DELETED THE EVIDENCE D4's OWN VERDICT RESTS ON** (2026-08-26T03:42:27Z)

**Nothing was fired. Nothing was touched. 0 core-min.** The lane found it in pre-flight **because the launch was held for my diff read.**

#### 4.1 THE DEFECT, VERIFIED BY ME LINE BY LINE — AND IT IS WORSE THAN IT WAS REPORTED

D4-SHIPPED's frozen §3.4 says the launcher `d4_run_arm.sh` **and siblings** are used *"unmodified"*. **That is true, and it is exactly the problem.**

| line | what it does |
|---|---|
| `d4_run_arm.sh:25` | `BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin` — **hardcoded, no override** |
| `:139` | `sudo -n rm -rf "$WORK"` **for every arm except F** — and **arm O is not F** |
| `:282` | `LEDGER="$BASE/ledger.txt"`, appended with `tee -a` |

**TWO CORRECTIONS UPWARD, BOTH MAKING IT WORSE.** The relay said five sibling launchers; **it is EIGHT** — `d4_run_arm.sh`, `d4_run_F2.sh`, `d4_run_F3.sh`, `d4_run_acc.sh`, `d4_stage_ACC.sh`, `d4_stage_F.sh`, `d4_stage_F2.sh`, `d4_stage_F3.sh`, each carrying the same hardcoded root. **And the directory that would have been deleted measures 384 MB and contains `OptView.hst`.**

**FIRING ARM O ON THE SHIPPED IMAGE WOULD HAVE `rm -rf`'d THE PATCHED ROW'S GRADED ARM O — 5,085 FILES, 384 MB, `OptView.hst` AND `opt_IPOPT.txt` — THE ARTIFACTS D4's `GATE REACHED` RESTS ON, WHICH I ACCEPTED THREE HOURS AGO** — and interleaved two items' rows into one `ledger.txt`, leaving **neither** cleanly gradeable afterwards.

#### 4.2 THE ARGUMENT FOR THE NON-DELEGABLE CHECKS IS NOW A MEASURED ONE

**The lane held the launch because MY instruction was ambiguous between "fire after I read" and "fire on delivery", and it chose the reading that preserved my §3 check 1.** That hold bought the pre-flight that found this. **A short delay to preserve a supervisor's read returned 384 MB of irreplaceable graded evidence.** Until tonight the case for the four non-delegable checks was a principle; **it is now a measurement, and it should be cited as one.**

#### 4.3 RULING — AMENDMENT **APPROVED** `[lab-attributed]`, ON FOUR CONDITIONS

Legal under `CLAUDE.md` rule 2: *"Before first compute, amendments are legal and must state the condition and how it was checked (name the run directory that does not exist)."* **D4-SHIPPED has burned 0 core-min and started no container — it is before first compute.**

1. **`CURRICULUM-D4-SHIPPED-a2-wing-cdmin` verified ABSENT with `test -e` IN the amending commit, and the check RECORDED** — rule 2 wants the check, not the intention.
2. **Do not merely change the constant — MAKE THE WRONG CONSTANT REFUSE.** `d4s_run_arm.sh` takes its own `BASE` and ledger **and aborts if `BASE` resolves to the patched item's root, or if the ledger already carries another item's rows** — **driven against the real D4 root on a sacrificial copy and shown to abort.** A guard not shown to fire is ceremony, and this is the guard standing between a re-fire and 384 MB.
3. **SHIPPED-digest enforcement, refusing the patched digest** — §11's hash-is-identity rule applied where it bites: the row a run claims and the row it ran must be the same hash or it does not run.
4. **The `oomkilled` `"none"` limitation recorded non-blocking in the same addendum.**

#### 4.4 ONE CLAIM I REFUSED, BECAUSE IT WOULD HAVE PUT A FALSE LINE IN A FROZEN DOCUMENT

The lane described `docker run -d` + poll + `docker inspect .State.ExitCode` as closing **"the harness-`$?` gap AND the cap-dies-with-shell defect in the same file."** **It closes the first. It does NOT close the second.**

**Tonight's own measurement is why: a foreground `docker run` client is not the container's parent — dockerd is — so containers ALREADY survive shell death.** `-d` changes nothing there. **What `timeout` provided was the CAP, and `timeout` lives in the shell; replacing it with `-d` plus a polling loop moves the cap into the POLLER, which also lives in the shell.** On shell death both designs land in the same place: **the container runs on, unguarded, with nothing left to stop it.** `-d` is a real improvement on rc capture and on not blocking the shell. **It is not a cap fix, and the document will say so: the cap exposure is registered OPEN, not repaired.** Closing it properly needs the deadline to live where the shell's death cannot reach it — inside the container's entrypoint, or in a file a later poller enforces. **Named tonight, built another night.**

#### 4.5 STANDING AUDIT ORDER FOR THIS FAMILY

**`D4-LAUNCHER-DEF-1` — a hardcoded run root plus an unguarded `rm -rf "$WORK"` — is a CLASS, and every dafoam launcher is audited for it BEFORE any re-fire**, D7R's and D12R2's families included. **D12R2 phase 1 IS RUNNING RIGHT NOW and is checked FIRST**, ahead of the D4-SHIPPED fire if the two collide: if its launcher carries the same shape I need to know before its next stage stages anything.

**This sits with the other three launcher findings tonight** — the cap that dies with its shell, `rc` from `$?` in 35 of 36, and `--rm` destroying the kernel record in 10 — and together they say something this family should have noticed earlier: **the graders have been audited repeatedly and the LAUNCHERS have not.** Every defect found tonight in an instrument was found in a grader; every defect found tonight in a launcher was found by accident, while looking at something else.

