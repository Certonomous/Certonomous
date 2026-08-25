#!/usr/bin/env python3
"""RESIDUAL-CRITERIA AUDIT SWEEP -- doctrine clause C4, executed.

Instrument design is NOT invented here.  It is executed against the scope,
thresholds and classification axes already frozen in
docs/standards/PARALLEL_GATE_DOCTRINE.md sections 6.1-6.4:

  A1  DICTIONARY KEY.  residualControl{} is a CONVERGENCE CRITERION and is in
      scope for C2.  solvers{}{tolerance} is a LINEAR-SOLVER DROP TOLERANCE --
      a different key measuring a different quantity.  The two are NEVER pooled
      into one ratio.  Reported in separate columns.

  A2  CHANNEL ROLE.  <name>Final collapses onto <name>.  Regex channel patterns
      like "(U|p|k)" expand to their members.  A channel is PRIMARY if its name
      is a field present in the case's 0/ directory, AUXILIARY otherwise.  This
      classifies pcorr, Phi, cellDisplacement and pointDisplacement as auxiliary
      MECHANICALLY, without any of them being named in advance.

  A3  PARALLELISM.  numberOfSubdomains from system/decomposeParDict, confirmed
      against processor* directories.  A serial run cannot exhibit the F6a
      mechanism; C2's justification requirement still applies to it.

  bind_ratio = (loosest PRIMARY tol) / (tightest PRIMARY tol) under
  residualControl ONLY.  DIRECTIONAL.  FLAG at >= 100, HARD FLAG at >= 1000.

  LOOSEST-AND-UNOBSERVABLE: the loosest channel in a block that the case's own
  registration also names unverifiable/unobservable/not-echoed-to-logs.

STANDING RULE 3 -- PLANTED CONTROL.  Before any zero is believed this sweep
plants three synthetic cases and REFUSES (exit 2) unless it sees all three:
  P1  a HARD-FLAG bind_ratio  -> must be detected as HARD FLAG
  P2  a known auxiliary channel -> must be excluded from bind_ratio
  P3  a loosest-and-unobservable pair -> must fire that detector
and one NEGATIVE plant:
  N1  a harmonized block -> must stay silent (OK)
A classifier is exactly the kind of reader that returns a confident zero when
its rule silently matches nothing.

ZERO COMPUTE.  This is a dictionary parse.  No solver is launched, no case is
written, and nothing outside the scratch directory is modified.
"""
from __future__ import annotations
import json, os, pathlib, re, sys, subprocess

REPO = pathlib.Path("/home/ubuntu/Certonomous")
OUTGIT = [pathlib.Path("/home/ubuntu/closure-data"),
          pathlib.Path("/home/ubuntu/closure-challenge-benchmark"),
          pathlib.Path("/home/ubuntu/certonomous-runs")]

FLAG, HARD = 100.0, 1000.0
UNOBS = re.compile(r"unverifiable[- ]from[- ]logs|unobservable|not echoed|no log line echoes",
                   re.I)

# ---------------------------------------------------------------- dict parsing
def strip_comments(t: str) -> str:
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    t = re.sub(r"//[^\n]*", " ", t)
    return t

def find_block(text: str, key: str):
    """Return the body of the FIRST top-level `key { ... }`, brace-matched."""
    for m in re.finditer(r"(?<![A-Za-z0-9_])" + re.escape(key) + r"\s*\{", text):
        i = m.end() - 1
        d = 0
        for j in range(i, len(text)):
            if text[j] == "{": d += 1
            elif text[j] == "}":
                d -= 1
                if d == 0:
                    return text[i + 1:j]
        return None
    return None

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"

def entries(body: str):
    """(name, value) for `name value;` at the TOP level of `body` only."""
    out, d, i, n = [], 0, 0, len(body)
    buf = []
    while i < n:
        c = body[i]
        if c == "{":
            d += 1; buf = []
        elif c == "}":
            d -= 1; buf = []
        elif c == ";" and d == 0:
            s = "".join(buf).strip()
            mm = re.match(r'^("?[^\s"]+"?)\s+(' + NUM + r")$", s)
            if mm:
                out.append((mm.group(1).strip('"'), float(mm.group(2))))
            buf = []
        else:
            buf.append(c)
        i += 1
    return out

def subdicts(body: str):
    """(name, body) for each `name { ... }` at the TOP level of `body`."""
    out, i, n = [], 0, len(body)
    while i < n:
        m = re.search(r'("?[^\s{};"]+"?)\s*\{', body[i:])
        if not m: break
        start = i + m.end() - 1
        d = 0
        for j in range(start, n):
            if body[j] == "{": d += 1
            elif body[j] == "}":
                d -= 1
                if d == 0:
                    out.append((m.group(1).strip('"'), body[start + 1:j]))
                    i = j + 1
                    break
        else:
            break
    return out

def expand(name: str):
    """Expand an OpenFOAM regex channel pattern into member names; collapse Final."""
    n = name.strip('"')
    if re.fullmatch(r"[A-Za-z0-9_.]+", n):
        members = [n]
    else:
        m = re.fullmatch(r"\(?([^()]*)\)?(Final)?", n)
        core = m.group(1) if m else n
        parts = [p for p in re.split(r"\|", core) if p]
        members = []
        for p in parts:
            p = p.strip()
            p = re.sub(r"[()\[\]\.\*\?\^\$\+]", "", p)
            if p: members.append(p)
        if not members: members = [n]
    return [re.sub(r"Final$", "", x) for x in members if x]

# ------------------------------------------------------------------ territory
def territory(p: pathlib.Path) -> str:
    s = str(p)
    if "/cases/RANS_LES_closure_models/" in s or "/closure-data" in s \
       or "/closure-challenge-benchmark" in s: return "closure"
    if "/cases/dafoam/" in s: return "dafoam"
    if "/cases/ansys_verification/" in s or "/verification/runs/ansys_verification/" in s:
        return "ansys-verification"
    for t in ("T-family", "F14-cooling-ladder", "THERMAL_K0_runs"):
        if "/verification/runs/" + t in s: return "heat-transfer"
    if "/certonomous-runs" in s: return "out-of-git (cfd/dafoam run store)"
    return "cfd"

def case_dir(fv: pathlib.Path):
    return fv.parent.parent if fv.parent.name == "system" else fv.parent

def zero_fields(case: pathlib.Path):
    f = set()
    for d in ("0", "0.orig", "0.org"):
        z = case / d
        if z.is_dir():
            for e in z.iterdir():
                if e.is_file(): f.add(e.name)
    return f

def parallel_of(case: pathlib.Path):
    n, dp = None, case / "system" / "decomposeParDict"
    if dp.is_file():
        try:
            m = re.search(r"numberOfSubdomains\s+(\d+)\s*;", strip_comments(dp.read_text(errors="ignore")))
            if m: n = int(m.group(1))
        except Exception: pass
    procs = len([d for d in case.glob("processor*") if d.is_dir()])
    return n, procs

def unobservable_channels(case: pathlib.Path):
    """Channels the case's OWN records name unverifiable/unobservable."""
    out = set()
    for pat in ("*.md", "*/*.md"):
        for rec in list(case.glob(pat))[:40]:
            try: txt = rec.read_text(errors="ignore")
            except Exception: continue
            for line in txt.splitlines():
                if UNOBS.search(line):
                    for tok in re.findall(r"`([A-Za-z0-9_]+)`", line):
                        out.add(re.sub(r"Final$", "", tok))
    return out

# ----------------------------------------------------------------- the reader
def read_block(fv: pathlib.Path):
    try: raw = fv.read_text(errors="ignore")
    except Exception: return None
    text = strip_comments(raw)
    rc_owner, rc_body = None, None
    for owner in ("SIMPLE", "PIMPLE", "PISO", "relaxationFactors", None):
        host = find_block(text, owner) if owner else text
        if host is None: continue
        b = find_block(host, "residualControl")
        if b is not None:
            rc_owner, rc_body = owner or "top-level", b
            break
    sol = find_block(text, "solvers")
    return {"raw_has_rc": "residualControl" in text, "rc_owner": rc_owner,
            "rc_body": rc_body, "solvers_body": sol}

def analyse(fv: pathlib.Path):
    blk = read_block(fv)
    if blk is None: return None
    case = case_dir(fv)
    zf = zero_fields(case)
    row = {"path": str(fv), "territory": territory(fv),
           "has_residualControl": bool(blk["rc_body"] is not None),
           "rc_owner": blk["rc_owner"]}
    # --- residualControl, axis A2
    prim, aux = {}, {}
    if blk["rc_body"] is not None:
        for name, val in entries(blk["rc_body"]):
            if name in ("nCorrectors", "nNonOrthogonalCorrectors", "nOuterCorrectors",
                        "consistent", "pRefCell", "pRefValue"): continue
            if val <= 0: continue
            for ch in expand(name):
                (prim if (ch in zf or ch + ".orig" in zf) else aux)[ch] = val
        for sub, body in subdicts(blk["rc_body"]):
            for name, val in entries(body):
                if name in ("tolerance", "relTol") and val > 0:
                    for ch in expand(sub):
                        (prim if ch in zf else aux)[ch] = val
    row["channels_primary"] = sorted(prim); row["channels_auxiliary"] = sorted(aux)
    row["zero_fields_seen"] = len(zf)
    if len(prim) >= 2:
        lo, hi = min(prim.values()), max(prim.values())
        row["tol_primary_min"], row["tol_primary_max"] = lo, hi
        row["bind_ratio"] = hi / lo
    else:
        row["bind_ratio"] = None
    br = row["bind_ratio"]
    row["flag"] = "OK" if br is None or br < FLAG else ("HARD FLAG" if br >= HARD else "FLAG")
    # --- solvers{} tolerances, axis A1: SEPARATE column, NEVER ratioed against the above
    sp = {}
    if blk["solvers_body"]:
        for sub, body in subdicts(blk["solvers_body"]):
            for name, val in entries(body):
                if name == "tolerance" and val > 0:
                    for ch in expand(sub):
                        if ch in zf: sp.setdefault(ch, val)
    row["solver_tol_primary"] = sp
    row["solver_tol_ratio"] = (max(sp.values()) / min(sp.values())) if len(sp) >= 2 else None
    # --- A3
    n, procs = parallel_of(case)
    row["numberOfSubdomains"], row["processor_dirs"] = n, procs
    row["serial"] = (n in (None, 1) and procs == 0)
    # --- 6.3.4 detector
    row["loose_unobservable"] = False; row["loose_unobservable_channel"] = None
    allc = dict(prim); allc.update(aux)
    if allc:
        loosest = max(allc, key=lambda k: allc[k])
        if loosest in unobservable_channels(case):
            row["loose_unobservable"] = True
            row["loose_unobservable_channel"] = loosest
    return row

# --------------------------------------------------------------- plant control
def write_plant(root: pathlib.Path, name, rc, solvers, fields, extra_md=None):
    c = root / name; (c / "system").mkdir(parents=True, exist_ok=True); (c / "0").mkdir(exist_ok=True)
    for f in fields: (c / "0" / f).write_text("dummy\n")
    body = "solvers\n{\n" + solvers + "}\n\nSIMPLE\n{\n    residualControl\n    {\n" + rc + "    }\n}\n"
    (c / "system" / "fvSolution").write_text(body)
    if extra_md: (c / "REG.md").write_text(extra_md)
    return c / "system" / "fvSolution"

def plant_and_verify(scratch: pathlib.Path):
    root = scratch / "plants"
    if root.exists():
        import shutil; shutil.rmtree(root)
    root.mkdir(parents=True)
    res = {}
    # P1 HARD FLAG: 5000x on PRIMARY channels
    p1 = write_plant(root, "P1_hardflag",
                     '        "(U|p|k)"   5e-7;\n        omega       1e-10;\n',
                     "    p { solver GAMG; tolerance 1e-8; }\n", ["U", "p", "k", "omega"])
    # P2 auxiliary exclusion: pcorr is loosest but NOT in 0/ -> must not move bind_ratio
    p2 = write_plant(root, "P2_auxiliary",
                     '        "(U|p|k|omega)"  1e-6;\n        pcorr            1e-2;\n',
                     "    p { solver GAMG; tolerance 1e-8; }\n", ["U", "p", "k", "omega"])
    # P3 loosest-and-unobservable
    p3 = write_plant(root, "P3_loose_unobs",
                     '        "(U|p|k)"   1e-6;\n        pcorr       1e-2;\n',
                     "    p { solver GAMG; tolerance 1e-8; }\n", ["U", "p", "k"],
                     extra_md="The lever `pcorr` is declared unverifiable-from-logs here.\n")
    # N1 NEGATIVE: harmonized -> must stay OK
    n1 = write_plant(root, "N1_harmonized",
                     '        "(U|p|k|omega)"  1e-6;\n',
                     "    p { solver GAMG; tolerance 1e-8; }\n"
                     '    "(U|k|omega)" { solver smoothSolver; tolerance 1e-9; }\n',
                     ["U", "p", "k", "omega"])
    r1, r2, r3, rn = (analyse(x) for x in (p1, p2, p3, n1))
    res["P1_hardflag"] = {"bind_ratio": r1["bind_ratio"], "flag": r1["flag"],
                          "SEEN": r1["flag"] == "HARD FLAG" and abs(r1["bind_ratio"] - 5000) < 1e-6}
    res["P2_auxiliary"] = {"bind_ratio": r2["bind_ratio"], "aux": r2["channels_auxiliary"],
                           "SEEN": r2["bind_ratio"] == 1.0 and "pcorr" in r2["channels_auxiliary"]}
    res["P3_loose_unobs"] = {"detector": r3["loose_unobservable"],
                             "channel": r3["loose_unobservable_channel"],
                             "SEEN": r3["loose_unobservable"] and r3["loose_unobservable_channel"] == "pcorr"}
    res["N1_harmonized_NEGATIVE"] = {"bind_ratio": rn["bind_ratio"], "flag": rn["flag"],
                                     "solver_tol_ratio": rn["solver_tol_ratio"],
                                     "QUIET": rn["flag"] == "OK" and rn["bind_ratio"] == 1.0}
    ok = all(res[k].get("SEEN", res[k].get("QUIET")) for k in res)
    return ok, res

# ------------------------------------------------------------------------ main
def collect():
    files = []
    out = subprocess.run(["/usr/bin/find", str(REPO / "cases"), str(REPO / "models"),
                          str(REPO / "verification/runs"), "-name", "fvSolution",
                          "-not", "-path", "*/processor*/*"],
                         capture_output=True, text=True)
    files += [pathlib.Path(x) for x in out.stdout.split("\n") if x.strip()]
    for r in OUTGIT:
        if r.is_dir():
            o = subprocess.run(["/usr/bin/find", str(r), "-name", "fvSolution",
                                "-not", "-path", "*/processor*/*"],
                               capture_output=True, text=True)
            files += [pathlib.Path(x) for x in o.stdout.split("\n") if x.strip()]
    return sorted(set(files))

def main():
    scratch = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/f13sweep")
    scratch.mkdir(parents=True, exist_ok=True)
    ok, plants = plant_and_verify(scratch)
    print("=" * 78); print("PLANTED CONTROL (standing rule 3) -- run BEFORE any zero is believed")
    for k, v in plants.items(): print(f"  {k:26s} {v}")
    if not ok:
        print("\nREFUSING: the reader was not shown able to see every planted signal.")
        print("A clean report from a blinded reader is not evidence.")
        sys.exit(2)
    print("  ALL PLANTS SEEN, NEGATIVE PLANT QUIET -> the reader is not blind.")
    print("=" * 78)
    files = collect()
    rows = [r for r in (analyse(f) for f in files) if r]
    json.dump(rows, open(scratch / "rows.json", "w"), indent=1)
    print(f"\nfvSolution files read (non-processor*): {len(rows)}")
    print(f"  carrying residualControl : {sum(1 for r in rows if r['has_residualControl'])}")
    print(f"  NOT carrying it          : {sum(1 for r in rows if not r['has_residualControl'])}")
    inrepo = [r for r in rows if r["path"].startswith(str(REPO))]
    print(f"\nIN-REPO subset: {len(inrepo)} files, "
          f"{sum(1 for r in inrepo if r['has_residualControl'])} with residualControl")
    print("\nBY TERRITORY (files with a residualControl block / with a computable bind_ratio):")
    terr = {}
    for r in rows:
        t = terr.setdefault(r["territory"], {"n": 0, "rc": 0, "br": 0, "FLAG": 0, "HARD FLAG": 0, "lu": 0})
        t["n"] += 1
        if r["has_residualControl"]: t["rc"] += 1
        if r["bind_ratio"] is not None:
            t["br"] += 1
            if r["flag"] in ("FLAG", "HARD FLAG"): t[r["flag"]] += 1
        if r["loose_unobservable"]: t["lu"] += 1
    print(f"  {'territory':36s} {'files':>6} {'rc':>5} {'ratio':>6} {'FLAG':>5} {'HARD':>5} {'L&U':>4}")
    for k in sorted(terr):
        t = terr[k]
        print(f"  {k:36s} {t['n']:6d} {t['rc']:5d} {t['br']:6d} {t['FLAG']:5d} {t['HARD FLAG']:5d} {t['lu']:4d}")
    flagged = [r for r in rows if r["flag"] in ("FLAG", "HARD FLAG")]
    print(f"\nFLAGGED BLOCKS: {len(flagged)}  "
          f"(FLAG {sum(1 for r in flagged if r['flag']=='FLAG')}, "
          f"HARD FLAG {sum(1 for r in flagged if r['flag']=='HARD FLAG')})")
    for r in sorted(flagged, key=lambda x: -x["bind_ratio"]):
        print(f"  {r['flag']:10s} ratio {r['bind_ratio']:>12.6g}  {r['territory']:22s} "
              f"serial={r['serial']}  {r['path'].replace(str(REPO)+'/','')}")
        print(f"             primary {r['channels_primary']}  aux {r['channels_auxiliary']}")
    lu = [r for r in rows if r["loose_unobservable"]]
    print(f"\nLOOSEST-AND-UNOBSERVABLE detector: {len(lu)} hit(s)")
    for r in lu:
        print(f"  {r['loose_unobservable_channel']:16s} {r['path'].replace(str(REPO)+'/','')}")
    print(f"\nrows -> {scratch/'rows.json'}")

if __name__ == "__main__":
    main()
