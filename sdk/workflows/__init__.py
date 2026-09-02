"""Certonomous mission workflows.

Each module answers one class of engineering request. The Chief Engineer's
router (``chief_engineer.router``) reads the request and dispatches here; every
number these workflows report comes from a real solver run.
"""

import os
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

# Resolved per host rather than hard-coded to WSL. See
# chief_engineer.openfoam.host_run_prefix for why.
from chief_engineer.openfoam import host_run_prefix  # noqa: E402
RUN_PREFIX = host_run_prefix()
OUT_ROOT = Path(os.environ.get(
    "CERTONOMOUS_OUTPUT",
    Path(__file__).resolve().parents[2] / "mission-output"))
OUT_ROOT.mkdir(parents=True, exist_ok=True)

NOMINAL_CYLINDER = {
    "cylinder_diameter": 1.0,
    "inlet_velocity": 1.0,
    "kinematic_viscosity": 0.05,
    "mesh_refinement": 1.0,
}


def safe_print(text: str) -> None:
    """Print without dying on a legacy console encoding.

    The chiefs speak in engineering prose (≈, ±, →, σ). A Windows console
    running cp1252 raises UnicodeEncodeError on those, which would otherwise
    kill a beat mid-run — the transcript must never be the thing that fails.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def make_transcript(mission: str, emit=None):
    """Transcript that prints to the terminal and streams to the control room."""
    from chief_engineer.transcript import Transcript

    sink = None
    if emit is not None:
        def sink(entry):
            emit("transcript.entry", entry.as_dict())
    return Transcript(mission, echo=safe_print, sink=sink)


def announce_plot(emit, beat: str, path, title: str,
                  caption: str = "", *, field: bool = False) -> None:
    """Tell the control room a plot is ready so it can render it inline.

    ``caption`` is the ONE LINE that renders under the figure, and it is
    optional because most callers have none. Twenty-nine of the thirty call
    sites in this package pass a title only; the thirtieth is the demo-mode
    results stage, which had four captions already authored and already
    validated by :class:`demo_mode.Figure` (title at most ten words, caption
    one line of at most twenty) and dropped every one of them on the floor,
    because this function had nowhere to put them.

    MEASURED BEFORE IT WAS ADDED: four of four figures on the jet-flap act
    published a title and no caption, so the caption row under every figure
    was empty for the whole act while the act's own author had written the
    text. The keyword is optional, so no existing caller changes behaviour.
    """
    if emit is None or not path:
        return
    from pathlib import Path as _Path

    payload = {"beat": beat, "file": _Path(path).name, "title": title,
               "url": f"/api/plot/{beat}/{_Path(path).name}"}
    if caption:
        payload["caption"] = caption
    # A FIELD PICTURE IS NOT JUST ANOTHER FIGURE. Sanaa's panel sequence is
    # geometry, then mesh, then FIELDS, and the stage cannot show a field it
    # cannot tell apart from a graph. The acts already separate the two --
    # ``Results.fields`` against ``Results.plots`` -- and that separation was
    # being flattened here, so every figure reached the page as a thumbnail and
    # the stage kept the grid standing through the report. The flag is only ever
    # set from the ``fields`` list, so nothing else can claim the stage.
    if field:
        payload["field"] = True
    emit("plot.ready", payload)


def announce_geometry(emit, *, name: str | None = None,
                      diameter: float | None = None, label: str = "",
                      url: str | None = None) -> None:
    """Tell the control room which surface this mission is working on.

    ``url`` overrides the address the page fetches from. WITHOUT IT the body
    is fetched from ``/api/geometry?name=<name>``, which the server resolves
    under ``sdk/geometry`` -- the SAME directory its upload handler writes
    into, under a bare filename. An act that hard-codes a filename therefore
    has its body replaceable by any upload of that name, and on 2026-09-01 one
    was: three missions were refused because the staged surface had been
    overwritten by a copy scaled 1.008966.

    An act that has moved its declaration off that directory passes the
    address of the copy it actually measures, so the PICTURE and the NUMBERS
    describe one body. Moving the file without moving the address would be
    worse than not moving it at all: the act would measure the right body and
    show the wrong one.
    """
    if emit is None:
        return
    if name:
        from chief_engineer.display_names import display_name

        emit("geometry.ready", {"url": url or f"/api/geometry?name={name}",
                                "label": label or display_name(name)})
    else:
        value = float(diameter if diameter is not None else 1.0)
        emit("geometry.ready", {"url": f"/api/geometry?diameter={value:.4f}",
                                "label": label or f"cylinder D={value:.3g} m"})


def acknowledge_reference_surface(script, emit, params, *, family: str
                                  ) -> str | None:
    """Acknowledge an uploaded surface as the reference body on file.

    Used by acts that run on a parametric family (the valve's orifice screen,
    the cylinder shape sweep): the surface is announced to the viewport under
    its display name, and the transcript states plainly that the screen runs
    on the parametric family while the uploaded surface stays on file as the
    reference shape. Nothing pretends the surface is meshed or solved by the
    screen. Returns the display name when a surface was acknowledged.
    """
    surface = str((params or {}).get("surface") or "").strip()
    if not surface:
        return None
    from chief_engineer.display_names import display_name

    surface_name = display_name(surface)
    announce_geometry(emit, name=surface,
                      label=f"reference body: {surface_name}")
    script.engineer(
        f"• Reference body received: {surface_name}. "
        f"• The surface is on file as the reference shape for this study. "
        f"• The screen itself runs on the parametric {family} family; the "
        f"uploaded surface is not meshed or solved by this screen.")
    return surface_name


# Wording doctrine (owner rule): the on-camera transcript never narrates the
# reuse machinery, never names a dash character, and never leans on the
# banned register below. Checked at authorship time rather than trusted, so a
# slip fails loudly in a test run instead of reaching the control room.
_BANNED_PHRASES = (
    "live", "real solve", "real solves", "solver backed", "solver-backed",
    "conceptual model", "demo", "stored", "saved", "cached", "precomputed",
    "reused", "trend",
)


#: Greek letters spelled out, which are SYMBOLS wearing the shape of ordinary
#: lower-case words. A bullet or caption may open with one; see the amendment
#: inside :func:`check_wording` for why the list has to be enumerated rather
#: than detected. Closed on purpose: quantity words in English ("pressure",
#: "velocity", "temperature") are deliberately absent and stay refused.
_SYMBOL_WORDS = frozenset({
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
    "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega",
})


def check_wording(text: str) -> None:
    """Raise if ``text`` breaks the on-camera wording doctrine.

    THE DASH BAN IS NOW THE WHOLE FAMILY. This checked the em-dash and the
    spaced hyphen only, so the house habit of rendering an em-dash as the
    double hyphen "--" walked straight through it and reached filmed strings.
    Sanaa, 2026-09-02 addendum, verbatim: "no dashes anywhere --". So the
    em-dash, the en-dash, the double hyphen and the spaced hyphen are all
    refused; re-punctuate with commas, colons or semicolons, content
    unchanged. A bare hyphen INSIDE a word ("k-omega", "second-order",
    "trailing-edge") is spelling, not punctuation, and stays legal.
    """
    if ("—" in text or "–" in text or "--" in text or " - " in text):
        raise ValueError(f"dash not allowed in transcript prose: {text!r}")
    lowered = text.lower()
    for phrase in _BANNED_PHRASES:
        if phrase in lowered:
            raise ValueError(f"banned phrase {phrase!r} in transcript prose: {text!r}")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("•"):
            body = stripped[1:].strip()
            # AMENDMENT, 2026-09-01. This read ``not body[0:1].isupper()``, so a
            # bullet was refused unless it began with a capital LETTER, and a
            # bullet beginning with a NUMBER was refused.
            #
            # THAT PUT THIS RULE IN DIRECT CONFLICT WITH A LATER INSTRUCTION OF
            # SANAA'S. Her 20:14Z directive, verbatim: "shorten the sentences
            # and have them in bullet points, and wherever the point can be
            # made accross with numbers its better." A screen that leads a
            # bullet with its number is what she asked for, and this rule
            # refused it. Measured on the battery act, which was written to that
            # directive: four bullets refused, and every one of them is a
            # number-led fact -- "8 cells at 30 mm pitch, 7 gaps at 3 mm",
            # "3,840 solid plus 12,768 coolant = 16,608 cells", "560 matched
            # faces, 1 to 1", "2 checks before anything is reported". The rule
            # was rejecting her own instruction, and it does it AT EMISSION, so
            # the refusal lands on camera rather than in a test.
            #
            # THE DEFECT CLASS THE RULE WAS WRITTEN FOR IS UNCHANGED. It exists
            # to catch a lowercase sentence FRAGMENT pasted into a bullet, and
            # that is now what it names: a bullet may not begin with a lowercase
            # letter. A digit still opens a fact, and a symbol still opens a
            # quantity -- "|U| (m/s)" is the caption form the figure standard
            # now requires and would have been refused here too.
            #
            # STRICTLY PERMISSIVE, WHICH IS WHY IT IS SAFE TO MAKE MID-CAMPAIGN:
            # every string that passed before still passes, so no act's screens
            # can change behaviour because of this. Only strings that were
            # CRASHING are affected.
            #
            # A LOWER-CASE *WORD* IS THE DEFECT; A LOWER-CASE *SYMBOL* IS NOT,
            # and testing the first CHARACTER cannot tell them apart. Written
            # that way this rule still refused "p/rho (m^2/s^2)" and "p (Pa)",
            # which are the exact caption forms the figure standard now
            # REQUIRES -- so one of Sanaa's rules would have been enforced by
            # crashing on another. The test is therefore the first WORD: an
            # all-alphabetic lower-case word of two or more letters is prose
            # starting mid-sentence. "p", "p/rho", "x/c", "|U|", "8" and
            # "3,840" are none of them.
            #
            # ONE CLASS OF LOWER-CASE WORD IS A SYMBOL AND HAS TO BE NAMED,
            # because nothing about its SHAPE distinguishes it from English:
            # a Greek letter spelled out. "rho (kg/m^3), 57,600 cells" is the
            # density caption this campaign actually renders, and by shape
            # "rho" is a three-letter lower-case word exactly like "the". The
            # list is closed, it is the Greek alphabet, and it is the only
            # exemption -- "pressure" and "velocity" are not on it and are
            # still refused, which is the whole point of the rule.
            first = body.split()[0] if body.split() else ""
            if (len(first) > 1 and first.isalpha() and first.islower()
                    and first not in _SYMBOL_WORDS):
                raise ValueError(
                    f"a bullet may open with a capital, a number or a symbol, "
                    f"but not with a lower-case word: {line!r}")


def bullets(sayer, *lines: str, **kwargs):
    """Emit one role entry holding every bullet on its own row.

    ``sayer`` is a bound method on the transcript, e.g. ``script.numericist``.
    Every line is prefixed with a bullet mark, checked against the wording
    doctrine, and joined into the single entry that role owns for this beat
    (never split across several entries, never the same role called twice in
    a row for one thought).
    """
    body = "\n".join(f"• {line.strip()}" for line in lines if line.strip())
    check_wording(body)
    return sayer(body, **kwargs)


def emit_table(emit, script, *, role: str, title: str, headers, rows,
              table_id: str, append: bool = False) -> None:
    """Put a transcript table on the record. Every result an act reports
    belongs here, never repeated as bare numbers in prose.

    The control room renders it as a compact table in the paced feed;
    ``append=True`` lands new rows into the existing table so rows arrive
    live as solves finish. Every row is mirrored into the saved transcript
    so the on-disk record keeps the numbers."""
    import time as _time

    from chief_engineer.transcript import Entry

    if emit:
        emit("transcript.table", {
            "role": role, "title": title,
            "headers": [str(h) for h in headers],
            "rows": [[str(cell) for cell in row] for row in rows],
            "table_id": table_id, "append": bool(append), "at": _time.time()})
    for row in rows:
        line = " | ".join(f"{h} {cell}" for h, cell in zip(headers, row))
        entry = Entry(role, f"[{title}] {line}")
        script.entries.append(entry)
        if emit is None and script.echo:
            script.echo(entry.render())


def announce_field(emit, beat: str, path, label: str) -> None:
    """Tell the control room a solved surface is painted and ready to render.

    Carries a bounding-box hint from the painted body so the viewport can
    auto-frame the camera on the vehicle rather than the old (possibly larger)
    geometry extent.
    """
    if emit is None or not path:
        return
    import json
    from pathlib import Path as _Path

    payload = {"beat": beat, "file": _Path(path).name, "label": label,
               "url": f"/api/field/{beat}/{_Path(path).name}"}
    try:
        bounds = json.loads(_Path(path).read_text(encoding="utf-8")).get("bounds")
        if bounds:
            payload["bounds"] = bounds
    except (OSError, ValueError):
        pass
    emit("field.ready", payload)


# The published sentence every act used to state unconditionally. It is kept
# here, once, so the claim and the action that earns it cannot drift apart.
WITHDRAWN_SENTENCE = ("The previous run's certificate is withdrawn, so "
                      "nothing out of date is served.")


def withdraw_certificate(path) -> tuple[bool, str]:
    """Withdraw a previous run's certificate page and say WHICH of three
    things happened -- never only two.

    DOCKET B2, and the defect is ours. Every act in this package opened with

        try:
            cert_path.unlink()
        except OSError:
            pass

    and then published, unconditionally, "The previous run's certificate is
    withdrawn, so nothing out of date is served." Injecting a PermissionError
    on that unlink while the new certificate also failed to build left an
    EARLIER MISSION's certificate on disk, byte for byte, under a transcript
    line saying it had been withdrawn. A withdrawal that could not happen is
    not a withdrawal, exactly as a surface that could not be read is not a
    surface that agrees.

    The three outcomes, and the middle one is why the two-valued form looked
    right for so long:

      * the page was there and is gone            -> withdrawn
      * there was no page to withdraw             -> withdrawn (nothing stale
        is served either way, which is the claim the sentence actually makes)
      * the page is there and could NOT be removed -> NOT withdrawn, and the
        caller must publish that instead of the clean sentence

    Returns ``(withdrawn, sentence)``. The sentence is the one the act should
    put on the record, so a caller cannot accidentally keep the clean claim.

    It does not raise: a certificate must never take down a good mission, and
    the reason that rule exists is the reason the failure has to be SAID
    rather than swallowed.
    """
    from pathlib import Path as _Path

    path = _Path(path)
    try:
        path.unlink()
    except FileNotFoundError:
        return True, WITHDRAWN_SENTENCE
    except OSError as exc:
        if not path.exists():
            return True, WITHDRAWN_SENTENCE
        return False, (
            f"The previous run's certificate COULD NOT be withdrawn "
            f"({type(exc).__name__}: {exc.strerror or exc}), so an "
            f"out-of-date page may still be served. Treat any certificate at "
            f"that address as belonging to an earlier run until it is "
            f"removed by hand.")
    except Exception as exc:                       # noqa: BLE001
        # Anything the filesystem layer can raise that is not an OSError
        # still may not become a silent success.
        return False, (
            f"The previous run's certificate COULD NOT be withdrawn "
            f"({type(exc).__name__}: {exc}), so an out-of-date page may still "
            f"be served.")
    return True, WITHDRAWN_SENTENCE
