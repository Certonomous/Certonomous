#!/usr/bin/env python3
"""memwatch.py -- run a command and instrument peak memory.

Reports, for the whole process tree of the command:
  peak_sum_rss_mib   : max over samples of sum(RSS) across all live descendants
  sum_vmhwm_mib      : sum of per-process VmHWM (peak RSS ever) -- conservative upper bound
  host_peak_used_mib : MemTotal - min(MemAvailable) observed during the run
  min_memavail_mib   : minimum MemAvailable observed during the run
Sampling interval 0.2 s. Writes a JSON line to --out.

Usage: memwatch.py --tag NAME --out FILE -- CMD ARGS...
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time

PAGE = 4096


def meminfo():
    d = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, _, v = line.partition(":")
            d[k] = int(v.split()[0])  # kB
    return d


def descendants(root):
    """All pids in the process tree rooted at root (inclusive)."""
    children = {}
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                with open(f"/proc/{pid}/stat", "rb") as f:
                    data = f.read()
            except OSError:
                continue
            rp = data.rfind(b")")
            if rp < 0:
                continue
            fields = data[rp + 2:].split()
            ppid = int(fields[1])
            children.setdefault(ppid, []).append(int(pid))
    except OSError:
        pass
    out, stack = [], [root]
    while stack:
        p = stack.pop()
        out.append(p)
        stack.extend(children.get(p, []))
    return out


def rss_kb(pid):
    try:
        with open(f"/proc/{pid}/statm") as f:
            return int(f.read().split()[1]) * PAGE // 1024
    except (OSError, IndexError, ValueError):
        return 0


def vmhwm_kb(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1])
    except OSError:
        pass
    return 0


class Watcher(threading.Thread):
    def __init__(self, root, interval=0.2):
        super().__init__(daemon=True)
        self.root = root
        self.interval = interval
        self.stop_flag = threading.Event()
        self.peak_sum_rss = 0
        self.hwm = {}          # pid -> highest VmHWM seen
        self.cmdline = {}      # pid -> comm
        self.min_avail = meminfo()["MemAvailable"]
        self.samples = 0

    def run(self):
        while not self.stop_flag.is_set():
            pids = descendants(self.root)
            total = 0
            for p in pids:
                total += rss_kb(p)
                h = vmhwm_kb(p)
                if h > self.hwm.get(p, 0):
                    self.hwm[p] = h
                    try:
                        with open(f"/proc/{p}/comm") as f:
                            self.cmdline[p] = f.read().strip()
                    except OSError:
                        pass
            if total > self.peak_sum_rss:
                self.peak_sum_rss = total
            a = meminfo()["MemAvailable"]
            if a < self.min_avail:
                self.min_avail = a
            self.samples += 1
            self.stop_flag.wait(self.interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cwd", default=None)
    ap.add_argument("--log", default=None)
    ap.add_argument("--timeout", type=float, default=3600.0)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd

    mt = meminfo()["MemTotal"]
    logf = open(a.log, "wb") if a.log else subprocess.DEVNULL

    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=a.cwd, stdout=logf, stderr=subprocess.STDOUT,
                            start_new_session=True)
    w = Watcher(proc.pid)
    w.start()
    timed_out = False
    try:
        rc = proc.wait(timeout=a.timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass
        try:
            rc = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            rc = proc.wait()
    wall = time.time() - t0
    w.stop_flag.set()
    w.join(timeout=5)
    if a.log:
        logf.close()

    top = sorted(((v, w.cmdline.get(k, "?"), k) for k, v in w.hwm.items()), reverse=True)[:20]
    rec = {
        "tag": a.tag,
        "cmd": cmd,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "exit_code": rc,
        "timed_out": timed_out,
        "wall_s": round(wall, 2),
        "samples": w.samples,
        "sample_interval_s": 0.2,
        "peak_sum_rss_mib": round(w.peak_sum_rss / 1024.0, 1),
        "sum_vmhwm_mib": round(sum(w.hwm.values()) / 1024.0, 1),
        "host_mem_total_mib": round(mt / 1024.0, 1),
        "min_memavailable_mib": round(w.min_avail / 1024.0, 1),
        "host_peak_used_mib": round((mt - w.min_avail) / 1024.0, 1),
        "top_processes_vmhwm_mib": [[c, p, round(v / 1024.0, 1)] for v, c, p in top],
        "log": a.log,
    }
    with open(a.out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in
                      ("tag", "exit_code", "wall_s", "peak_sum_rss_mib", "sum_vmhwm_mib",
                       "host_peak_used_mib", "min_memavailable_mib", "timed_out")}))
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
