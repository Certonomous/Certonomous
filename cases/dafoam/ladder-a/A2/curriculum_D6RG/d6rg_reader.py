#!/usr/bin/env python3
"""D6RG -- THE ONE REPAIRED READER, AND NOTHING ELSE.

D6R-GRADER-DEF-2: `d6r_grade.py:615-624` `read_ipopt()` requires BOTH an
`Objective...............:` summary line AND an `EXIT:` line and refuses
(`:620-621`) if either is missing.  When IPOPT dies on `Eval_Error` it prints
the exception text WHERE THE SUMMARY BLOCK WOULD HAVE GONE, so the summary line
is absent and the reader cannot read a log that is otherwise complete.
MEASURED WITH A CONTROL, not inferred: D6R's `O_mp/opt_IPOPT.txt` has ZERO
matches of `^Objective\\.+:` and ONE `EXIT:` line; D4's
`CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` has exactly ONE of each -- the
reader is demonstrably able to see a non-zero, so the absence is real.

THIS MODULE RE-IMPLEMENTS NO GATE.  It supplies ONE function body for ONE
rebound name.  Every regex it matches with is the FROZEN module's own
(`OBJ_RE`, `EXIT_RE`, `NIT_RE`, `MAJOR_ROW_RE`), passed in; every refusal is
raised through the FROZEN module's own `refuse()`, passed in.  No band, no
threshold, no composition rule and no label lives here.

WHAT THE REPAIR MAY AND MAY NOT DO
  MAY: read the final objective OUT OF THE ITERATION TABLE THAT IS IN THE FILE.
  MAY NOT: invent an objective, coerce a non-finite one, or read a table whose
  own tail says it is incomplete.
The recovered value's PROVENANCE IS THE ITERATION ROW, NOT THE SUMMARY LINE,
and those are different claims: the table prints 8 significant figures where the
summary prints 17, and the table has ONE objective column where the summary has
two (scaled, unscaled).  The two columns may only be equated when the log's own
`nlp_scaling_method` is `none`, which is READ FROM THE FILE and refused on
otherwise.  Both facts are recorded on every recovered reading.

L-332: no `assert` anywhere; the caller AST-counts this file and refuses on any.
"""
import math
import re

# ---- REGISTERED, frozen with PREREGISTRATION.md ---------------------------------------
# The repair covers EXACTLY this exit and no other.  A different non-optimal exit that
# also lost its summary block is NOT covered here and REFUSES: widening the set is a
# registration change, not a reader change.
REGISTERED_NONFINITE_EXITS = ("EXIT: Invalid number in NLP function or derivative detected.",)
# IPOPT's iteration table carries ONE objective column.  It is the UNSCALED objective only
# when scaling is off.  Read, never assumed.
SCALING_LINE_RE = re.compile(r"^\s*nlp_scaling_method\s*=\s*(?P<v>\S+)", re.M)
REQUIRED_SCALING = "none"
OPTIMAL_PREFIX = "EXIT: Optimal Solution Found"


def read_scaling_method(txt):
    """The log's OWN option echo.  None when the log does not state it -- which is a
    refusal at the call site, never a default."""
    m = SCALING_LINE_RE.search(txt)
    return (m.group("v") if m else None)


def significant_digits(s):
    """Significant figures actually PRINTED in an IPOPT table mantissa, e.g.
    '2.2238800e-02' -> 8.  Used to record what the recovered number is worth."""
    mant = s.split("e")[0].split("E")[0].lstrip("+-")
    return len(mant.replace(".", "").lstrip("0")) or len(mant.replace(".", ""))


def iteration_table_rows(txt, MAJOR_ROW_RE):
    """Every major row the FROZEN module's own regex can see, in file order."""
    return [(int(m.group("n")), bool(m.group("rest")), m.group("obj"), m.group("inf_du"))
            for m in MAJOR_ROW_RE.finditer(txt)]


def recover_nonfinite_exit(path, txt, where, refuse, EXIT_RE, NIT_RE, MAJOR_ROW_RE):
    """THE REPAIR BRANCH.  Reached ONLY when the summary `Objective` line is absent.
    Seven gates stand between an unreadable log and a recovered number, and every one of
    them REFUSES through the frozen module's own `refuse()`.  A repaired reader that
    cannot still refuse is not repaired, it is disabled."""
    exits = EXIT_RE.findall(txt)
    if not exits:
        refuse(where, {"repair_declined_no_exit_line": path,
                       "note": "no EXIT line at all.  That is an ABSENT record, not a "
                               "recognised non-finite exit; the original refusal stands."})
    exit_line = exits[-1].strip()
    if exit_line not in REGISTERED_NONFINITE_EXITS:
        refuse(where, {"repair_declined_exit_not_registered": exit_line, "path": path,
                       "registered": list(REGISTERED_NONFINITE_EXITS),
                       "note": "the repair covers exactly the registered non-finite exit.  "
                               "Another exit that also lost its summary block needs its own "
                               "registration, not a wider reader."})
    scaling = read_scaling_method(txt)
    if scaling != REQUIRED_SCALING:
        refuse(where, {"repair_declined_nlp_scaling_method": scaling, "required": REQUIRED_SCALING,
                       "path": path,
                       "note": "the iteration table has ONE objective column.  It equals the "
                               "UNSCALED objective the frozen reader returns only when scaling "
                               "is off.  With scaling on the two are different numbers and the "
                               "unscaled one is NOT IN THE FILE."})
    nits = NIT_RE.findall(txt)
    if not nits:
        refuse(where, {"repair_declined_number_of_iterations_absent": path,
                       "note": "without the tail's own iteration count there is nothing to "
                               "corroborate the table against, so a truncated table cannot be "
                               "distinguished from a complete one."})
    n_iter = int(nits[-1])
    rows = iteration_table_rows(txt, MAJOR_ROW_RE)
    if not rows:
        refuse(where, {"repair_declined_no_iteration_table": path,
                       "number_of_iterations_reported": n_iter,
                       "note": "the tail reports iterations but NO major row is present.  "
                               "There is no objective in this file to recover."})
    nums = [n for n, _r, _o, _d in rows]
    if nums[-1] != n_iter:
        refuse(where, {"repair_declined_iteration_table_torn": path,
                       "last_table_major": nums[-1], "number_of_iterations_reported": n_iter,
                       "rows_matched": len(rows),
                       "note": "the tail says the run took more majors than the table shows, so "
                               "the last READABLE row is NOT the final objective.  Recovering it "
                               "would publish an intermediate value as an endpoint."})
    gaps = [[nums[i], nums[i + 1]] for i in range(len(nums) - 1)
            if nums[i + 1] not in (nums[i], nums[i] + 1)]
    if nums[0] != 0 or gaps:
        refuse(where, {"repair_declined_iteration_table_not_contiguous": path,
                       "first_major": nums[0], "gaps": gaps[:10],
                       "note": "majors must run 0..N with restoration rows repeating their "
                               "number; a hole means rows were lost between the ends."})
    obj_txt = rows[-1][2]
    try:
        val = float(obj_txt)
    except ValueError:
        refuse(where, {"repair_declined_objective_unparseable": obj_txt, "path": path})
    if not math.isfinite(val):
        refuse(where, {"repair_declined_recovered_objective_not_finite": obj_txt,
                       "float_value": str(val), "path": path,
                       "note": "a non-finite endpoint is REFUSED, never coerced to a number.  "
                               "The whole failure under repair is a non-finite evaluation; "
                               "silently returning one would be the laundering this reader exists "
                               "to prevent."})
    return {"objective": val, "objective_scaled": val,
            "exit": exit_line, "n_iter": n_iter,
            "optimal": exit_line.startswith(OPTIMAL_PREFIX), "path": path,
            # ---- PROVENANCE.  These are the claims that differ from the frozen reader's.
            "summary_line_present": False,
            "objective_provenance": "ITERATION_TABLE_ROW",
            "objective_row_major": nums[-1],
            "objective_row_text": obj_txt,
            "objective_printed_significant_digits": significant_digits(obj_txt),
            "objective_precision_note":
                "the iteration table prints %d significant figures; the summary line the frozen "
                "reader wants prints 17.  THIS IS THE TABLE'S NUMBER AT THE TABLE'S PRECISION AND "
                "IS NOT THE SUMMARY'S NUMBER." % significant_digits(obj_txt),
            "objective_scaled_equals_unscaled_because":
                "nlp_scaling_method = %s, READ from this log" % REQUIRED_SCALING,
            "n_major_rows_matched": len(rows),
            "n_restoration_rows": sum(1 for _n, r, _o, _d in rows if r),
            "repair_branch_taken": True,
            "repair_registered_exit": exit_line}
