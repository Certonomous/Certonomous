#!/usr/bin/env python3
"""DERIVE the machine-readable ANSYS register TSV from the prose register.
Prose register is the SOURCE OF TRUTH (append-only, CLAUDE.md rule 6); this file is DERIVED.
Reads register bytes from `git show <ref>:<path>` by default (the worktree lags HEAD in this
lab, L-350), so the committed/authoritative register is the source. Unreliable cells -> UNPARSED.
Usage: gen_ansys_register_tsv.py [--ref HEAD] [--from-file PATH] > out.tsv
"""
import re,sys,subprocess,hashlib,datetime

REG_PATH="verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md"
VOCAB=["PASS","GATE REACHED","GATE FAIL","NOT A RESULT","BLOCKED","PENDING"]
ROW=re.compile(r'^\| \*\*([0-9]+)\*\* \|')
VER=re.compile(r'^\*\*`(' + "|".join(re.escape(v) for v in VOCAB) + r')`\*\*')
CASE=re.compile(r'(VMFLGPU[0-9][0-9A-Za-z_-]*|VMFL[0-9][0-9A-Za-z_-]*)')
DATE=re.compile(r'^20\d\d-\d\d-\d\d$')
SHA=re.compile(r'`?\b([0-9a-f]{7,40})\b`?')
GPUH=re.compile(r'([0-9]+\.?[0-9]*)\s*GPU-h')
NUM=re.compile(r'([0-9]+\.?[0-9]*)')
U="UNPARSED"

def split_fields(line):
    return re.split(r'(?<!\\)\|', line)

def get_register_text(ref, from_file):
    if from_file:
        return open(from_file,encoding="utf-8").read()
    return subprocess.run(["git","show",f"{ref}:{REG_PATH}"],
                          capture_output=True,text=True,check=True).stdout

def path_tokens(field):
    toks=[]
    for tok in re.split(r'[\s`|]+', field.strip()):
        t=tok.strip('`*.,;()[]')
        if '/' in t and not t.startswith('http'):
            toks.append(t)
    return toks

def one_path(field):
    t=path_tokens(field)
    return t[0] if len(t)==1 else U

def one_sha(field):
    hs=SHA.findall(field)
    hs=[h for h in set(hs)]
    return hs[0] if len(hs)==1 else U

def one_gpuh(field):
    g=GPUH.findall(field)
    g=list(dict.fromkeys(g))
    return g[0] if len(g)==1 else U

def derive_rows(text):
    lines=text.split("\n")
    out=[]
    for l in lines:
        m=ROW.match(l)
        if not m: continue
        rid=int(m.group(1))
        f=split_fields(l)
        # verdict: first field matching the bolded-code verdict token
        verdict=None
        for fld in f:
            vm=VER.match(fld.strip())
            if vm: verdict=vm.group(1); break
        # case_id
        cm=CASE.search(f[2]) if len(f)>2 else None
        case_id=cm.group(1) if cm else U
        # date: exactly one bare-date field
        dates=[x.strip() for x in f if DATE.match(x.strip())]
        date_utc=dates[0] if len(dates)==1 else U
        canonical=(len(f)==15)
        is_gpu=('VMFLGPU' in l)
        if canonical:
            artifact=one_path(f[8])
            prereg=one_sha(f[9])
            comp=one_sha(f[10])
            costf=f[11]
            if is_gpu:
                gpu_h=one_gpuh(costf)
                core_min=U
            else:
                nm=NUM.search(costf); core_min=nm.group(1) if nm else U
                gpu_h=""  # non-GPU: empty by spec
            results=one_path(f[13])
        else:
            artifact=prereg=comp=core_min=results=U
            gpu_h=U if is_gpu else ""
        out.append(dict(row_id=rid,case_id=case_id,date_utc=date_utc,verdict=verdict,
                        prereg_sha=prereg,comparator_sha=comp,artifact_path=artifact,
                        cost_core_min=core_min,cost_gpu_h=gpu_h,results_path=results,
                        _rowline=l))
    return out

def rows_hash(rows):
    h=hashlib.sha256()
    h.update("\n".join(r["_rowline"] for r in rows).encode("utf-8"))
    return h.hexdigest()

COLS=["row_id","case_id","date_utc","verdict","prereg_sha","comparator_sha",
      "artifact_path","cost_core_min","cost_gpu_h","results_path"]

def main():
    ref="HEAD"; from_file=None
    a=sys.argv[1:]
    for i,x in enumerate(a):
        if x=="--ref": ref=a[i+1]
        if x=="--from-file": from_file=a[i+1]
    text=get_register_text(ref,from_file)
    rows=derive_rows(text)
    n=len(rows)
    census={v:0 for v in VOCAB}
    for r in rows: census[r["verdict"]]+=1
    creds=[r["row_id"] for r in rows if r["verdict"]=="PASS"]
    rh=rows_hash(rows)
    if from_file:
        blob="(from-file)"; headsha="(from-file)"
    else:
        headsha=subprocess.run(["git","rev-parse",ref],capture_output=True,text=True).stdout.strip()
        blob=subprocess.run(["git","rev-parse",f"{ref}:{REG_PATH}"],capture_output=True,text=True).stdout.strip()
    now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    o=sys.stdout
    o.write("# ANSYS VALIDATION REGISTER - machine-readable DERIVED view (TSV, tab-separated)\n")
    o.write("# SOURCE OF TRUTH: verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md (prose, append-only, CLAUDE.md rule 6).\n")
    o.write("# THIS FILE IS DERIVED - never hand-edit; regenerate with scripts/gen_ansys_register_tsv.py. Reconcile with scripts/check_ansys_register.py.\n")
    o.write(f"# Derived from {REG_PATH} at ref {headsha} blob {blob} on {now} by ansys-lane-opus48 (lane C).\n")
    o.write("# Verdict rule: FIRST field matching ^**`(PASS|GATE REACHED|GATE FAIL|NOT A RESULT|BLOCKED|PENDING)`** after escape-aware pipe split.\n")
    o.write("# Unreliably-extractable cells are the literal token UNPARSED (never guessed). cost_gpu_h empty where the row is not a GPU case.\n")
    o.write(f"# meta: n_rows={n}\n")
    o.write(f"# meta: credentials_pass_count={len(creds)}\n")
    o.write(f"# meta: credential_row_ids={','.join(str(x) for x in creds)}\n")
    o.write(f"# meta: rows_1_to_N_sha256={rh}\n")
    o.write("# census: "+" ".join(f"{k.replace(' ','_')}={census[k]}" for k in VOCAB)+"\n")
    o.write("\t".join(COLS)+"\n")
    for r in rows:
        o.write("\t".join(str(r[c]) for c in COLS)+"\n")

if __name__=="__main__":
    main()
