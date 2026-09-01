"""Aggregate-memory reading for the chain driver (ADDENDUM 2).
aggregate = sum of LIVE containers' memory caps + this arm's cap + host
non-container RSS, must be under the ceiling.  Passive: reads docker and
/proc/meminfo, prints one JSON line, exits 0.  Any exception -> ok=false."""
import json
import subprocess
import sys


def main():
    mine, ceil = float(sys.argv[1]), float(sys.argv[2])
    try:
        ids = subprocess.run(["sudo", "-n", "docker", "ps", "-q"],
                             capture_output=True, text=True).stdout.split()
        caps, used, names = 0.0, 0.0, []
        if ids:
            out = subprocess.run(["sudo", "-n", "docker", "inspect", "--format",
                                  "{{.Name}} {{.HostConfig.Memory}}"] + ids,
                                 capture_output=True, text=True).stdout
            for line in out.splitlines():
                n, m = line.split()
                caps += int(m) / 2 ** 30
                names.append(n.lstrip("/"))
            st = subprocess.run(["sudo", "-n", "docker", "stats", "--no-stream",
                                 "--format", "{{.MemUsage}}"] + ids,
                                capture_output=True, text=True).stdout
            for line in st.splitlines():
                tok = line.split("/")[0].strip()
                v = float("".join(c for c in tok if c.isdigit() or c == "."))
                u = tok.lower()
                used += v / 1024.0 if "mib" in u else (v if "gib" in u else v / 2 ** 20)
        mi = {}
        for line in open("/proc/meminfo"):
            k, v = line.split(":")
            mi[k] = int(v.split()[0])
        host_nc = max((mi["MemTotal"] - mi["MemAvailable"]) / 2 ** 20 - used, 0.0)
        agg = caps + mine + host_nc
        print(json.dumps({"live_caps_GiB": round(caps, 2), "live": names,
                          "this_cap_GiB": mine,
                          "host_noncontainer_rss_GiB": round(host_nc, 2),
                          "aggregate_GiB": round(agg, 2), "ceiling_GiB": ceil,
                          "ok": bool(agg < ceil)}))
    except Exception as exc:  # noqa: BLE001 -- a failed reading is a refusal
        print(json.dumps({"ok": False, "error": str(exc)}))


if __name__ == "__main__":
    main()
