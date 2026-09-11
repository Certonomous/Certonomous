"""G-CPUSET reading for the chain driver (D8R; = D17's, renamed; the aggregate-memory
script's form).  A LIVE container whose HostConfig.CpusetCpus shares a core with this
item's registered cpuset would halve the cores DELIVERED to a pinned 2-rank arm and fail
G12's delivered-cores floor for a placement reason -- so the driver WAITS (bounded) rather
than fire.  Passive: reads docker, prints one JSON line, exits 0.  Containers carrying
this item's own prefix are ignored (they are this chain's, already refused by G-ROOT.5 if
live).  Any exception -> ok=false (a failed reading is a refusal, never a pass).
usage: d8r_cpuset_overlap.py <registered cpuset, e.g. 12,15> <own prefix, e.g. d8r_>"""
import json
import subprocess
import sys


def expand(spec):
    out = set()
    for part in (spec or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


def main():
    mine, prefix = expand(sys.argv[1]), sys.argv[2]
    try:
        ids = subprocess.run(["sudo", "-n", "docker", "ps", "-q"],
                             capture_output=True, text=True).stdout.split()
        overlaps, live = [], []
        if ids:
            out = subprocess.run(["sudo", "-n", "docker", "inspect", "--format",
                                  "{{.Name}} {{.HostConfig.CpusetCpus}}"] + ids,
                                 capture_output=True, text=True).stdout
            for line in out.splitlines():
                toks = line.split()
                name = toks[0].lstrip("/")
                cs = toks[1] if len(toks) > 1 else ""
                if name.startswith(prefix):
                    continue
                shared = sorted(expand(cs) & mine)
                live.append({"name": name, "cpuset": cs})
                if shared:
                    overlaps.append({"name": name, "cpuset": cs, "shared_cores": shared})
        print(json.dumps({"registered_cpuset": sorted(mine), "live": live,
                          "overlaps": overlaps, "ok": bool(not overlaps)}))
    except Exception as exc:  # noqa: BLE001 -- a failed reading is a refusal
        print(json.dumps({"ok": False, "error": str(exc)}))


if __name__ == "__main__":
    main()
