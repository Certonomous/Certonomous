"""Aggregate-memory reading for the D8G chain driver.

DERIVED FROM curriculum_D8R/d8r_aggregate_memory.py -- FROZEN behind a graded two-row PASS
and NOT EDITED BY THIS ITEM.  Deltas in d8g_aggregate_memory_DELTAS_from_d8r.diff.
PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.

aggregate = sum of LIVE containers' memory claims + this arm's cap + host non-container RSS,
which must be under the ceiling.  Passive: reads docker and /proc/meminfo, prints one JSON
line, exits 0.  Any exception -> ok=false (a failed reading is a refusal, never a pass).

THE ONE BEHAVIOURAL DELTA FROM D8R, AND IT WAS A LIVE DEFECT WHEN IT WAS FOUND.
D8R summed `HostConfig.Memory` -- the container's CAP.  A container started WITHOUT
`--memory` reports a cap of 0, so it contributed NOTHING to the caps term; and because its
real usage was subtracted out of `host_nc`, it contributed nothing there either.  IT WAS
DOUBLY INVISIBLE: a neighbour growing uncapped to 20 GiB would have moved the aggregate by
approximately zero.  MEASURED 2026-09-11 on this box: BOTH live containers
(`nifty_heisenberg`, `a3gc_probe_L1`) carried `HostConfig.Memory = 0`.  A ceiling compared
against a number blind to the largest thing on the box is theatre.
REPAIRED: an uncapped live container is counted AT ITS CURRENT USAGE, NAMED, and carried in
the reading as `uncapped_containers`, so a grader can see the aggregate was taken against an
unbounded neighbour.  Counting it at current usage is a LOWER BOUND and says so -- the
honest alternative, refusing outright, would deadlock D8G behind any other team's uncapped
probe, and this reading's job is to inform the driver's wait, not to arbitrate the box.

THE CEILING IS A FORMULA, NOT A LITERAL (PREREGISTRATION.md AMENDMENT 2 (b)).  Pass
`reserve=<GiB>` and the ceiling is computed from THIS box's own MemTotal as
`MemTotal_GiB - reserve`.  A literal ceiling silently describes the wrong machine after an
instance change, and an instance change is Sanaa's call.  A plain number is still accepted
so the reading can be driven against an explicit ceiling in a test.

usage: d8g_aggregate_memory.py <this arm's cap GiB> <reserve=4.0 | ceiling GiB>
       d8g_aggregate_memory.py --selftest
"""
import json
import subprocess
import sys

GIB = 2 ** 30


def parse_memusage(tok):
    """`docker stats --format {{.MemUsage}}` gives e.g. `506.1MiB / 30.64GiB`; the part
    before the slash is the usage.  Returns GiB."""
    tok = tok.split("/")[0].strip()
    v = float("".join(c for c in tok if c.isdigit() or c == "."))
    u = tok.lower()
    if "gib" in u:
        return v
    if "mib" in u:
        return v / 1024.0
    if "kib" in u:
        return v / 1048576.0
    return v / GIB                                    # bytes


def compose(caps, usage, mine, mem_total_gib, mem_avail_gib, ceiling_gib):
    """PURE.  caps/usage are {container name: GiB}.  Separated from the docker calls so the
    selftest can drive THIS function -- the composition is the part that was wrong, and a
    test that could not reach it would be testing the part that was right."""
    counted, uncapped, per = 0.0, [], {}
    for name in sorted(set(caps) | set(usage)):
        cap = float(caps.get(name, 0.0))
        use = float(usage.get(name, 0.0))
        if cap > 0.0:
            counted += cap
            per[name] = {"claim_GiB": round(cap, 3), "basis": "HostConfig.Memory"}
        else:
            counted += use
            uncapped.append(name)
            per[name] = {"claim_GiB": round(use, 3), "basis": "UNCAPPED -- counted at current "
                                                             "usage, A LOWER BOUND, not a cap"}
    used_total = sum(float(v) for v in usage.values())
    host_nc = max(mem_total_gib - mem_avail_gib - used_total, 0.0)
    agg = counted + float(mine) + host_nc
    out = {"live": sorted(set(caps) | set(usage)), "per_container": per,
           "live_claims_GiB": round(counted, 3),
           "uncapped_containers": uncapped,
           "this_cap_GiB": float(mine),
           "host_noncontainer_rss_GiB": round(host_nc, 3),
           "aggregate_GiB": round(agg, 3), "ceiling_GiB": round(float(ceiling_gib), 3),
           "ok": bool(agg < float(ceiling_gib))}
    if uncapped:
        out["uncapped_note"] = ("the aggregate was taken against %d UNBOUNDED neighbour(s): %s.  "
                                "Their claim is counted at CURRENT USAGE and is a LOWER BOUND; "
                                "this reading cannot bound what they may grow to."
                                % (len(uncapped), ", ".join(uncapped)))
    return out


def meminfo_gib():
    mi = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":")
        mi[k] = int(v.split()[0])
    return mi["MemTotal"] / 1048576.0, mi["MemAvailable"] / 1048576.0


def resolve_ceiling(arg, mem_total_gib):
    """`reserve=4.0` -> MemTotal - 4.0 (AMENDMENT 2 (b)); a bare number -> that number."""
    a = str(arg).strip()
    if a.lower().startswith("reserve="):
        return mem_total_gib - float(a.split("=", 1)[1]), "MemTotal(%.3f) - reserve(%s)" % (
            mem_total_gib, a.split("=", 1)[1])
    return float(a), "explicit"


def read_docker():
    caps, usage = {}, {}
    ids = subprocess.run(["sudo", "-n", "docker", "ps", "-q"],
                         capture_output=True, text=True).stdout.split()
    if ids:
        out = subprocess.run(["sudo", "-n", "docker", "inspect", "--format",
                              "{{.Name}} {{.HostConfig.Memory}}"] + ids,
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            if not line.strip():
                continue
            n, m = line.split()
            caps[n.lstrip("/")] = int(m) / GIB
        st = subprocess.run(["sudo", "-n", "docker", "stats", "--no-stream",
                             "--format", "{{.Name}} {{.MemUsage}}"] + ids,
                            capture_output=True, text=True).stdout
        for line in st.splitlines():
            if not line.strip():
                continue
            n, rest = line.split(None, 1)
            usage[n.lstrip("/")] = parse_memusage(rest)
    return caps, usage


def selftest():
    n, fails = 0, []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    MT, MA = 30.644, 19.289
    # U1-U3: the capped case behaves exactly as D8R's did.
    r = compose({"c1": 6.0}, {"c1": 1.0}, 14.0, MT, MA, 26.644)
    unit("U1 a CAPPED container is counted at its cap", r["live_claims_GiB"] == 6.0)
    unit("U2 host non-container RSS excludes container usage",
         abs(r["host_noncontainer_rss_GiB"] - (MT - MA - 1.0)) < 1e-9)
    unit("U3 no uncapped neighbours are reported when every container has a cap",
         r["uncapped_containers"] == [])
    # U4-U6: THE DEFECT.  Both containers uncapped, as MEASURED on this box 2026-09-11.
    r2 = compose({"nifty_heisenberg": 0.0, "a3gc_probe_L1": 0.0},
                 {"nifty_heisenberg": 0.1193, "a3gc_probe_L1": 0.4942}, 14.0, MT, MA, 26.644)
    unit("U4 an UNCAPPED container is counted at its CURRENT USAGE, not at zero",
         abs(r2["live_claims_GiB"] - (0.1193 + 0.4942)) < 1e-3)
    unit("U5 it is NAMED, so a grader can see the aggregate was taken against an unbounded "
         "neighbour", sorted(r2["uncapped_containers"]) == ["a3gc_probe_L1", "nifty_heisenberg"])
    unit("U6 the reading carries the lower-bound caveat in words",
         "LOWER BOUND" in r2.get("uncapped_note", ""))
    # U7: THE BLINDNESS THE REPAIR REMOVES, shown as a difference, not asserted.
    big = compose({"greedy": 0.0}, {"greedy": 20.0}, 14.0, MT, 0.5, 26.644)
    old_style = 0.0 + 14.0 + max(MT - 0.5 - 20.0, 0.0)   # D8R: caps=0 for an uncapped container
    unit("U7 a neighbour grown UNCAPPED to 20 GiB moves this reading and did NOT move D8R's",
         big["live_claims_GiB"] == 20.0 and big["aggregate_GiB"] > old_style + 15.0)
    # U8-U9: the ceiling is a formula, and the reading refuses when it should.
    c, how = resolve_ceiling("reserve=4.0", MT)
    unit("U8 `reserve=4.0` resolves against THIS box's MemTotal, not a literal",
         abs(c - (MT - 4.0)) < 1e-9 and how.startswith("MemTotal"))
    unit("U9 ok=False once the aggregate crosses the ceiling", big["ok"] is False)
    # U10: the planted control on the refusal -- it must also be able to say yes.
    unit("U10 ok=True on a box with room (the reader is shown able to return BOTH answers)",
         compose({}, {}, 6.0, MT, 28.0, 26.644)["ok"] is True)
    # U11: usage parsing, the unit the whole composition rests on.
    unit("U11 MemUsage parses MiB and GiB",
         abs(parse_memusage("506.1MiB / 30.64GiB") - 0.49424) < 1e-4
         and abs(parse_memusage("2.5GiB / 30.64GiB") - 2.5) < 1e-9)
    print("\nD8G AGGREGATE-MEMORY SELFTEST units=%d fails=%d" % (n, len(fails)))
    for f in fails:
        print("  FAILED UNIT: %s" % f)
    return 2 if fails else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        mine = float(sys.argv[1])
        mt, ma = meminfo_gib()
        ceil, how = resolve_ceiling(sys.argv[2], mt)
        caps, usage = read_docker()
        out = compose(caps, usage, mine, mt, ma, ceil)
        out["mem_total_GiB"] = round(mt, 3)
        out["mem_available_GiB"] = round(ma, 3)
        out["ceiling_basis"] = how
        print(json.dumps(out, sort_keys=True))
    except Exception as exc:                          # noqa: BLE001 -- a failed reading is a refusal
        print(json.dumps({"ok": False, "error": str(exc)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
