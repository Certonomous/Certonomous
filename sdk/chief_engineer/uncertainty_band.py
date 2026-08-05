"""Composing a case's channel records into the one band a viewer is shown.

The doctrine already fixes the arithmetic: the combined expanded uncertainty is
the root sum of squares over the channels that carry a figure, it lives in
`uq.combine_expanded`, and no act writes its own version. What the doctrine did
NOT have was one place that turns a case's stored channel records into that
call. Every act was assembling the argument list by hand, which is where the
doctrine's two limits get lost: a channel that is unquantified gets passed as
0.0 because 0.0 is easier to type than None, and a channel that shares an
evaluation with another gets squared in because nothing was checking.

This module is that place. It takes the records a case already stores and
returns the composed band together with the breakdown the doctrine requires be
shown one level down, and it refuses in the cases the doctrine says to refuse.

FOUR RULES, ENFORCED HERE RATHER THAN REMEMBERED

1. Unquantified is not zero. A channel with no figure is carried in `missing`,
   contributes nothing, and makes `covers_all_channels` false. The total then
   says out loud that it is a total over part of the budget.

2. A shared evaluation is withheld. A channel whose record carries
   `independent_of_numerical: false` is dropped from the quadrature with its
   reason recorded in `withheld`, because squaring two channels that share a
   point reports a total wider than either channel earned.

3. A coefficient-interval band is carried ALONGSIDE, never inside. The
   perturbed-coefficient envelope is an interval over an epistemic box with no
   density behind it. Converting it to a sigma so it can be squared into a
   quadrature invents the density. It travels as `coefficient_interval`, with
   its own width, and the composed band is reported next to it, not over it.

4. Nothing enters the total that the breakdown does not show. The returned
   record IS the breakdown; `contributions` and `combined_95` are produced by
   the same call and cannot drift apart.

WIRE-IN POINT FOR THE CERTIFICATE PATH -- NOT WIRED IN THIS PASS.
`sdk/chief_engineer/certificate.py` builds its uncertainty section from channel
values it assembles itself. The integration is to have it call `compose()` and
render `as_channel_table()` instead, which would give certificates the same
withholding and unquantified handling this module enforces. That change is
deliberately NOT made here: the certificate path took a truthfulness fix in
4925fafb and it should land on its own, with its own test pass, rather than
riding along with a UQ study. Follow-up item: "route certificate.py's
uncertainty section through uncertainty_band.compose".
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from chief_engineer import uq

__all__ = ["ChannelBand", "compose", "as_channel_table", "coefficient_interval"]

CHANNELS = ("input", "numerical", "model")


class ChannelBand(dict):
    """The composed band plus everything needed to display it honestly.

    A dict subclass so it serialises into a study record unchanged; the
    properties are conveniences for callers rendering it.
    """

    @property
    def combined(self) -> float | None:
        return self.get("combined_95")

    @property
    def complete(self) -> bool:
        return bool(self.get("covers_all_channels"))


def _figure(record: Any) -> float | None:
    """The band figure a channel record carries, or None when it carries none.

    Accepts the three shapes the lab's records actually take: a plain number, a
    record with `band_abs`, or a record with `band_rel` plus a working value
    the caller supplies separately (handled by `compose`). A record that exists
    but has no figure is unquantified, which is NOT zero.
    """
    if record is None:
        return None
    if isinstance(record, (int, float)):
        return abs(float(record))
    if isinstance(record, Mapping):
        value = record.get("band_abs")
        if value is None:
            return None
        return abs(float(value))
    raise TypeError(f"channel record of unsupported type {type(record)!r}")


def _independent(record: Any) -> tuple[bool, str | None]:
    if not isinstance(record, Mapping):
        return True, None
    if record.get("independent_of_numerical") is False:
        return False, str(record.get("shared_evaluation")
                          or record.get("independence_note")
                          or "shares an evaluation with the numerical channel")
    return True, None


def coefficient_interval(*, low: float, high: float, working: float | None = None,
                         n_samples: int | None = None,
                         method: str | None = None,
                         citations: Sequence[str] = ()) -> dict[str, Any]:
    """A coefficient-interval band, in the shape `compose` carries alongside.

    Built here rather than by each caller so the words that keep it out of the
    quadrature travel with the numbers, in every record that has one.
    """
    if high < low:
        raise ValueError("coefficient interval given high < low")
    band = {
        "low": float(low), "high": float(high),
        "width": float(high) - float(low),
        "n_samples": n_samples,
        "method": method or "perturbed-coefficient solve set on a held mesh",
        "citations": list(citations),
        "carried_as": "interval",
        "in_quadrature": False,
        "why_not_in_quadrature": (
            "an epistemic interval has no density behind it; turning its width "
            "into a sigma so it can be squared into an RSS invents the density "
            "and reports a total the evidence does not support"),
    }
    if working:
        band["working_value"] = float(working)
        band["width_pct_of_working"] = 100.0 * band["width"] / abs(float(working))
        band["working_inside"] = float(low) <= float(working) <= float(high)
    return band


def compose(channels: Mapping[str, Any], *,
            working_value: float | None = None,
            coefficient_band: Mapping[str, Any] | None = None,
            quantity: str = "the reported value") -> ChannelBand:
    """Compose the stored channel records of one case into its displayed band.

    `channels` maps any of "input", "numerical", "model" to that channel's
    record: a number, a record with `band_abs`, a record with `band_rel` (used
    against `working_value`), or None for a channel that was not quantified.
    `coefficient_band` is carried alongside and never combined.

    The arithmetic itself is delegated to `uq.combine_expanded` -- this module
    decides WHAT is passed to it, and the doctrine's one-function rule for HOW
    is untouched.
    """
    unknown = set(channels) - set(CHANNELS)
    if unknown:
        raise ValueError(f"unknown channel(s): {sorted(unknown)}")

    values: dict[str, float | None] = {}
    withheld: dict[str, str] = {}
    detail: dict[str, Any] = {}
    for name in CHANNELS:
        record = channels.get(name)
        figure = _figure(record)
        if (figure is None and isinstance(record, Mapping)
                and record.get("band_rel") is not None and working_value):
            figure = abs(float(record["band_rel"]) * float(working_value))
        ok, reason = _independent(record)
        if figure is not None and not ok:
            withheld[name] = reason or "not independent of the numerical channel"
            figure = None
        values[name] = figure
        detail[name] = {
            "quantified": figure is not None,
            "band_abs": figure,
            "method": (record.get("method")
                       if isinstance(record, Mapping) else None),
            "screening_estimate": (bool(record.get("screening_estimate"))
                                   if isinstance(record, Mapping) else False),
        }

    combined = uq.combine_expanded(input_2sigma=values["input"],
                                   numerical_abs=values["numerical"],
                                   model_abs=values["model"])
    missing = list(combined["missing"])
    out: dict[str, Any] = {
        "quantity": quantity,
        "combined_95": combined["combined_95"],
        "contributions": combined["contributions"],
        "largest": combined["largest"],
        "missing": missing,
        "withheld": withheld,
        "channels": detail,
        "covers_all_channels": not missing,
        "coverage_statement": _coverage_sentence(quantity, combined["contributions"],
                                                 missing, withheld),
        "combined_by": "chief_engineer.uq.combine_expanded (root sum of squares, "
                       "95 percent, over the quantified channels only)",
    }
    if working_value:
        out["working_value"] = float(working_value)
        if combined["combined_95"]:
            out["combined_95_pct"] = (100.0 * combined["combined_95"]
                                      / abs(float(working_value)))
    if coefficient_band is not None:
        band = dict(coefficient_band)
        band.setdefault("in_quadrature", False)
        out["coefficient_interval"] = band
        out["coefficient_interval_note"] = (
            "reported alongside the combined band, not inside it")
    return ChannelBand(out)


def _coverage_sentence(quantity: str, quantified: Mapping[str, float],
                       missing: Sequence[str],
                       withheld: Mapping[str, str]) -> str:
    if not quantified:
        return (f"No channel of {quantity} carries a figure, so there is no "
                f"total; the channels are reported unquantified.")
    covered = ", ".join(sorted(quantified))
    sentence = f"Total for {quantity} covers the {covered} channel"
    sentence += "s" if len(quantified) > 1 else ""
    if missing:
        sentence += (f"; {', '.join(sorted(missing))} "
                     f"{'are' if len(missing) > 1 else 'is'} unquantified and "
                     f"contributes nothing, so the total covers less than the "
                     f"whole budget")
    for name, reason in sorted(withheld.items()):
        sentence += f"; the {name} channel is withheld because it {reason}"
    return sentence + "."


def as_channel_table(band: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The breakdown a composed band must be displayed with, row per channel.

    The doctrine's contract is that the combined band is never presented
    without this table one level down, so it is produced from the same record
    the total came out of and cannot disagree with it.
    """
    rows = []
    channels = band.get("channels", {})
    withheld = band.get("withheld", {})
    for name in CHANNELS:
        detail = channels.get(name, {})
        if name in withheld:
            state = "withheld"
        elif detail.get("quantified"):
            state = "quantified"
        else:
            state = "unquantified"
        rows.append({
            "channel": name,
            "state": state,
            "band_abs": detail.get("band_abs"),
            "method": detail.get("method"),
            "screening_estimate": detail.get("screening_estimate", False),
            "note": withheld.get(name),
        })
    return rows
