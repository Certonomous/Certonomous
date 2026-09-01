#!/usr/bin/env python3
r"""Curriculum D19O -- the AGGREGATE MEMORY reader the chain driver executes.

`DAFOAM_CHARTER.md` section 18.3 exists because `curriculum_SO2a`'s frozen
instrument table read *"eight of eight AGREE"* while `so2a_aggregate_memory.py`
-- which its frozen driver executed BY NAME, inside its poll loop -- was ABSENT
from the freeze commit.  **An md5-agreement control over a subset can read
agreement on every pin it holds while a dependency the frozen code executes is
missing.**  This file is therefore enumerated in PREREGISTRATION.md section 7
and its existence is asserted BEFORE any md5.

WHAT IT ANSWERS: may an arm needing `want_gib` start right now, against a
registered aggregate ceiling, given what this box's containers already hold?

  d19o_aggregate_memory.py <want_gib> <ceiling_gib>

  exit 0  -> GO      (aggregate would stay at or under the ceiling)
  exit 1  -> WAIT    (it would not; the driver polls and retries)
  exit 2  -> REFUSE  (the reading itself could not be taken)

**A WAIT IS NOT A FAILURE AND A REFUSE IS NOT A WAIT.**  The driver's poll loop
must be able to tell them apart, because a reader that cannot take its reading
would otherwise loop forever reporting "not yet".

`DAFOAM_CHARTER.md` section 7: the memory envelope is PREDICTED, STATED and
CHECKED before any adjoint launches, and a run stopped by memory is recorded as
stopped by memory and is NOT A RESULT about convergence.
"""
import json
import subprocess
import sys

CEILING_DEFAULT_GIB = 30.6


def container_reserved_gib():
    """What this box's RUNNING containers have RESERVED, from their own
    `HostConfig.Memory`.  Reservation, not usage: a container that has not yet
    touched its ceiling can still reach it, and an aggregate built on current
    RSS would authorise a launch that OOMs ten seconds later."""
    try:
        names = subprocess.run(["sudo", "-n", "docker", "ps", "--format", "{{.Names}}"],
                               capture_output=True, text=True, timeout=60)
        if names.returncode != 0:
            return None, "docker ps rc=%d" % names.returncode
        total, per = 0.0, {}
        for n in [x for x in names.stdout.split() if x]:
            r = subprocess.run(["sudo", "-n", "docker", "inspect", "--format",
                                "{{.HostConfig.Memory}}", n],
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                continue
            try:
                gib = int(r.stdout.strip()) / (1024.0 ** 3)
            except ValueError:
                continue
            per[n] = round(gib, 3)
            total += gib
        return {"total_gib": round(total, 3), "per_container": per}, None
    except Exception as exc:                                      # noqa: BLE001
        return None, repr(exc)[:200]


def mem_available_gib():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return round(int(line.split()[1]) / 1048576.0, 3)
    except Exception:                                             # noqa: BLE001
        return None
    return None


def main(argv):
    if len(argv) < 1:
        sys.stderr.write("usage: d19o_aggregate_memory.py <want_gib> [ceiling_gib]\n")
        return 2
    try:
        want = float(argv[0])
        ceiling = float(argv[1]) if len(argv) > 1 else CEILING_DEFAULT_GIB
    except ValueError:
        sys.stderr.write("D19O_AGG REFUSE non-numeric argument %r\n" % (argv,))
        return 2
    reserved, err = container_reserved_gib()
    avail = mem_available_gib()
    if reserved is None:
        sys.stdout.write(json.dumps({"state": "REFUSE", "why": "cannot read container "
                                     "reservations", "error": err}, sort_keys=True) + "\n")
        return 2
    total_after = reserved["total_gib"] + want
    go = total_after <= ceiling
    sys.stdout.write(json.dumps({
        "state": "GO" if go else "WAIT",
        "want_gib": want, "ceiling_gib": ceiling,
        "reserved_now_gib": reserved["total_gib"],
        "aggregate_if_started_gib": round(total_after, 3),
        "headroom_gib": round(ceiling - total_after, 3),
        "per_container": reserved["per_container"],
        "memavailable_gib": avail,
        "basis": "RESERVATION (HostConfig.Memory), not current RSS -- a container "
                 "that has not yet touched its ceiling can still reach it",
    }, sort_keys=True) + "\n")
    return 0 if go else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        ok = True
        print("D19O AGGREGATE MEMORY -- CONTROLS")
        r = main(["12.0", "30.6"])
        print("  live reading exit=%d (0 GO / 1 WAIT / 2 REFUSE)" % r)
        ok = ok and r in (0, 1, 2)
        r2 = main(["1000.0", "30.6"])
        print("  1000 GiB against a 30.6 GiB ceiling -> exit=%d (must be 1 = WAIT)" % r2)
        ok = ok and (r2 == 1)
        r3 = main(["not-a-number"])
        print("  non-numeric argument -> exit=%d (must be 2 = REFUSE)" % r3)
        ok = ok and (r3 == 2)
        r4 = main([])
        print("  no argument -> exit=%d (must be 2 = REFUSE)" % r4)
        ok = ok and (r4 == 2)
        print("D19O AGGREGATE MEMORY SELFTEST: %s"
              % ("OK -- GO/WAIT/REFUSE are distinguishable" if ok else "FAILED"))
        sys.exit(0 if ok else 1)
    sys.exit(main(sys.argv[1:]))
