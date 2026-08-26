# dafoam grader field-class audit — L-342 / Sanaa's universal rule (2026-08-26)

**Written by a dafoam lab-lane for dafoam-supervisor, on the chief's order.** Rule under audit (Sanaa, verbatim, `d4d0c29d`, L-342): *"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts — and graders must separate physics-critical fields from infrastructure fields so a dead poller can never void a run again."*

**Question asked of every grader at HEAD** (`git ls-tree -r HEAD --name-only | grep -E 'cases/dafoam/.*grade.*\.py'`, 27 files): does an **ABSENT infrastructure field** — `memavail_pre/post`, `delivered_cores_mean`, `siblings_*`, cpu/mem series, `wall_s`/`core_min`/cap fields, ledger-row formatting, or the ledger row itself — cause a **refusal** or a **`NOT A RESULT`**? Physics-critical fields per L-342: solver logs, fields, histories, **the kernel/container record** (`rc`, `OOMKilled`). Infrastructure per the addendum: cost, memory, pids, timestamps, placement series.

**No grader was edited.** Proposals are diffs for the supervisor to read; they touch no band, threshold or verdict logic (addendum consequence 4).

## 1. The table

| grader (HEAD blob) | item state | conflation | where, by line | disposition |
|---|---|---|---|---|
| `A3/curriculum_D7FR/d7fr_grade.py` (`35f62221aa17`) | **LIVE** — `ACC` graded `PASS`, `F-S` running, `F-P` queued | **YES** | `read_ledger` :261-262 refuses on an absent ledger; G1 :404 `arm_absent_from_ledger` → `pass` False → `map_verdict` :1091 hard → **`NOT A RESULT`**; G1 :409-410 `_f(rec,"wall_s"/"core_min")` **refuses** on absence (:307) — both infrastructure; G10 :878-880 `_f` on `enforced_core_min`/`cap_core_min`/`core_min` **refuses**; G11 :949-957 absent `inspect(exit,oomkilled)` → `OOM_BIT_NOT_RECORDED` → `pass` False → :1095 hard → **`NOT A RESULT`** (the kernel bit is physics, but the grader can read it ONLY through the ledger row, a host-side transport). G12 :1022-1037 absent `delivered_cores_mean` → `GATE FAIL` on G12 — **reported, NOT in the hard list (:1090-1106), does not void**: correct already. G13 reads the arm log: physics, correct | **amendment proposal §2.1, pre-registered before `F-S`/`F-P` are graded** |
| `curriculum_D12R2/d12y_grade.py` (`3a76c8283b30`) | **LIVE** — W2R | **YES, one limb** | `REQUIRED_ROW_KEYS` :83-85 are all physics (`rc`, `oomkilled`, `end_line_present`, `last_time`, `endTime`, cold/age) — correct; `memavail_GiB` :402-405 refuses only when PRESENT and below floor, absent tolerated — correct; **G12R-0b :443-446 refuses on an ABSENT ledger** and :453-457 on a ledger with no `STAGE=` lines — the ledger is a host-side `tee -a` (`d12y_w2r_stage_and_run.sh:172,240`) and its absence voids the grade while the per-stage JSON, logs and container record are intact | **amendment proposal §2.2, before W2R is graded** |
| `curriculum_D12R/d12x_grade.py` (`b1602722c13e`) | **LIVE** — phases 3/4 fired by the queue runner 16:10–16:11Z | **NO** | G12R-0 :240-261 reads physics keys only; `memavail_GiB` :287 and `g8_envelope` :700-703 act only when the value is PRESENT (absent → not blocked); no ledger-binding limb | none; NAMED |
| `A2/curriculum_D4_SHIPPED/d4s_grade.py` (`01d380082e64`) | **PENDING** — arm O re-grade ordered (`d4d0c29d`, consequence 3) | **YES — the named instance** | `LEDGER_RE` :668-678 requires `memavail_pre/post`, `delivered_cores_mean`, `siblings_pre/post` for a row to parse at all; an unparsed row is invisible → :705-706 `no_rows_parsed` refusal, or G1 :222 `arm_absent_from_ledger` refusal; :700-701 `float()` on memavail | the supervisor has already routed this to Addendum 2 of that item; not duplicated here |
| `A2/curriculum_D4/d4_grade.py` (`1c231382cbe9`), `d4_grade_SUPPLEMENT.py` (`ef4c1cfaae90`) | SETTLED — D4 closed `GATE REACHED`, C-97 | YES, same `LEDGER_RE` shape (:545-554 / SUPPLEMENT :595-630) | NAMED, NOT REOPENED: every D4 row parsed (all fields present); no verdict rests on an absent field |
| `A3/curriculum_D7/d7_grade.py` (`73de934c5a1a`), `A3/curriculum_D7F/d7f_grade.py` (`1e6bb91f3273`) | SETTLED (D7 graded; D7F superseded by D7FR) | YES, the D7FR shape one port earlier (`_f` :216-220 / :307-311; `arm_absent_from_ledger` :236 / :335) | NAMED, NOT REOPENED |
| `A1/curriculum_D13/d13_grade.py` (`0202e852d38b`), `d13_grade_supplement.py` (`55f77e6195e1`) | SETTLED | YES (weak) — `read_ledger` :75-84 refuses `NO_LEDGER`/`LEDGER_EMPTY`; the row regex `LEDGER` gates parse | NAMED, NOT REOPENED |
| `A6/curriculum_D8/d8_grade.py` (`44661e2c85ef`) | SETTLED | YES (crash, not refusal) — :268/:453 `open(ledger.txt)` uncaught if absent; the ledger is read only for `ASSERT_MD5 OK` (:275/:460) | NAMED, NOT REOPENED |
| `curriculum_D12/d12r_grade.py` (`f04fb3c2fa11`) | SETTLED | NO — :198 refuses on `rc`, a physics key | NAMED |
| `A4/curriculum_D3/d3_grade.py` (×2, `8d2a666f9154`), `A5/curriculum_D10_probe*/d10*_grade.py` (3), `A5/curriculum_D9/d9_grade*.py` (2), `A6/curriculum_D8/d8_grade_entry.py`, `probes/curriculum_D11*/d11*_grade.py` (5), `probes/curriculum_D12_unsteady_probe*/d12*_grade.py` (2) | SETTLED | **NO** — none reads a ledger, host series or placement file; they grade solver artefacts and JSON outputs | NAMED |

**Count:** 27 graders; conflation YES in 10 (2 live, 1 pending re-grade, 7 settled); NO in 17.

## 2. Amendment proposals — diffs to be READ BY THE SUPERVISOR, not applied

Both proposals declare two labelled field classes and route every infrastructure absence to `NOT_MEASURED` + disclosure. **Neither moves a band, threshold, cap or verdict rule.** Each is an amendment to a frozen file (rule 6): appended, dated, version-bumped, `lines whose number changed above this section: 0` asserted by the committing lane, with a driven unit per changed branch.

### 2.1 `d7fr_grade.py` — proposed, NOT APPLIED

```diff
@@ field classes, declared once @@
+# L-342 FIELD CLASSES.  Gates read PHYSICS only.  INFRASTRUCTURE absent ->
+# NOT_MEASURED, disclosed in the output, the grade PROCEEDS.
+PHYSICS_FIELDS = ("rc", "inspect(exit,oomkilled)")           # the kernel's record
+INFRA_FIELDS   = ("wall_s", "core_min", "cap_core_min", "enforced_core_min",
+                  "enforced_wall_s", "memavail_pre_GiB", "memavail_post_GiB",
+                  "memavail_min_during", "delivered_cores_mean",
+                  "siblings_pre", "siblings_post")
+
+def _infra(rec, key):
+    v = rec.get(key)
+    if v is None:
+        return "NOT_MEASURED"
+    try:
+        return float(v)
+    except ValueError:
+        return "NOT_MEASURED"
@@ G1 :409-410 @@
-        out["arms"][arm] = {"rc": rc, "wall_s": _f(rec, "wall_s", "G1", arm),
-                            "core_min": _f(rec, "core_min", "G1", arm),
+        out["arms"][arm] = {"rc": rc, "wall_s": _infra(rec, "wall_s"),
+                            "core_min": _infra(rec, "core_min"),
@@ G1 :404 arm_absent_from_ledger -- physics fallback BEFORE voiding @@
-            out["arms"][arm] = {"status": "arm_absent_from_ledger"}
+            # A ledger row is bookkeeping.  The kernel's record survives it:
+            # the launcher's own marker (.ok/.fail, rc from docker inspect,
+            # d7fr_run_arm.sh:632-636) and, if the launcher died before :593,
+            # the container itself.  Only when NEITHER exists is the arm absent.
+            rc_fb = _rc_from_marker_or_container(base, arm)
+            if rc_fb is None:
+                out["arms"][arm] = {"status": "arm_absent_from_ledger"}
+                continue
+            rec = {"rc": rc_fb["rc"], "inspect(exit,oomkilled)": rc_fb["inspect"],
+                   "_source": rc_fb["source"], "_ledger_row": "NOT_MEASURED"}
@@ G10 :878-880 -- a bookkeeping gate reads bookkeeping; absence is NOT_MEASURED @@
-        enf = _f(rec, "enforced_core_min", "G10", arm)
-        cap = _f(rec, "cap_core_min", "G10", arm)
-        act = _f(rec, "core_min", "G10", arm)
+        enf, cap, act = (_infra(rec, k) for k in
+                         ("enforced_core_min", "cap_core_min", "core_min"))
+        if "NOT_MEASURED" in (enf, cap, act):
+            out["arms"][arm] = {"status": "NOT_MEASURED", "limb1": "NOT_MEASURED",
+                                "note": "ledger row incomplete; cap integrity "
+                                        "unverifiable from bookkeeping, disclosed"}
+            continue
@@ G11 :949-957 -- the OOM bit is PHYSICS; read it from the kernel when the row lacks it @@
         insp = (rec.get("inspect(exit,oomkilled)") or "").strip("[]")
+        if not insp:
+            fb = _rc_from_marker_or_container(base, arm)   # docker inspect if the container survives
+            insp = (fb or {}).get("inspect", "")
         if not insp:
```
`_rc_from_marker_or_container` reads `<BASE>/<ARM>_*.log.ok.*|.fail.*` (`rc=<n>` written from `docker inspect` at launcher :564) and then `sudo -n docker inspect` on `d7fr_<ARM>_*` if present; it returns `None` when neither exists. **G11 stays hard** (kernel record = physics); what changes is only that the grader no longer needs the ledger row to see it. **Units to drive:** ledger row absent + marker present → graded; ledger row lacking `wall_s` → `NOT_MEASURED`, verdict unchanged; ledger row lacking `inspect` + container gone + marker gone → G11 `NOT_MEASURED`, hard (unchanged behaviour, now the only path to it).

### 2.2 `d12y_grade.py` — proposed, NOT APPLIED

```diff
@@ G12R-0b :443-446 -- an absent second witness is NOT_MEASURED when the first witness is intact @@
-    if not os.path.isfile(ledger_path):
-        raise Refusal("G12R-0b: ledger %s is absent, so the manifest has NO SECOND "
-                      "WITNESS. ..." % ledger_path)
+    if not os.path.isfile(ledger_path):
+        # L-342: the ledger is a host-side `tee -a` (d12y_w2r_stage_and_run.sh:240).
+        # Its absence is a BOOKKEEPING failure.  The manifest rows still carry the
+        # physics keys (REQUIRED_ROW_KEYS) and each stage's own log and JSON are
+        # graded by G12R-0.  The binding limb is reported NOT_MEASURED, never a void.
+        return {"gate": "G12R-0b", "verdict": "NOT_MEASURED",
+                "reason": "ledger absent; manifest<->ledger binding unverifiable",
+                "manifest_rows": len(rows), "expected_rows": expected_rows,
+                "count_vs_registered": ("MATCH" if len(rows) == expected_rows else "MISMATCH")}
```
**Kept as refusals**, because both are physics-side or genuine disagreement: `REQUIRED_ROW_KEYS` absence (:250), and a ledger that EXISTS and DISAGREES with the manifest (:461-468). The `expected_rows` check against the registered stage count (:469) is retained on the manifest alone when the ledger is absent, and its result is printed beside the `NOT_MEASURED`. **Unit to drive:** ledger absent, manifest complete → `NOT_MEASURED` with `count_vs_registered: MATCH`, grade proceeds; ledger present and disagreeing → Refusal, unchanged.

## 3. What this audit does NOT claim

It did not run any grader; it read HEAD blobs. It does not say the live items are exposed *today*: D7FR's ledger row is written by the frozen launcher inside a `setsid` chain, which survives agent death (measured on `ACC`, `STATUS.ACC`); the exposure is a host reboot or a launcher death mid-arm. It does not reopen any settled verdict. It names `d4s_grade.py` as the supervisor already has and adds nothing to that item's Addendum 2.
