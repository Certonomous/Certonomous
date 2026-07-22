import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.models import ParameterSpec
from chief_engineer.uncertainty import (
    CONFIDENCE_SURE,
    CONFIDENCE_UNKNOWN,
    CONFIDENCE_UNSURE,
    assess,
)


def _quadratic(x: float) -> float:
    return 4.0 - (x - 5.0) ** 2 / 10.0


SPAN = ParameterSpec("span", 0.0, 10.0)


def _samples(xs):
    return [({"span": x}, {"L_D": _quadratic(x)}) for x in xs]


class UncertaintyAssessmentTests(unittest.TestCase):
    def test_dense_evidence_reads_as_sure_with_numbers(self):
        xs = [0.5 * i for i in range(21)]  # 0.0 .. 10.0, dense
        report = assess(
            _samples(xs),
            {"span": 5.0},
            {"L_D": _quadratic(5.0)},
            design_id="winner",
            parameter_specs=(SPAN,),
        )
        (metric,) = report.metrics
        self.assertEqual(metric.metric, "L_D")
        self.assertEqual(metric.confidence, CONFIDENCE_SURE)
        self.assertLess(metric.relative, 0.02)
        self.assertIn("I am sure", metric.statement)
        self.assertIn("±", metric.statement)
        self.assertIn("95% CI", metric.statement)
        self.assertIn(metric.statement, report.narration)

    def test_sparse_distant_evidence_reads_as_not_sure(self):
        # Four far-apart samples; the assessed design sits in the widest gap.
        report = assess(
            _samples([0.0, 1.0, 9.0, 10.0]),
            {"span": 5.0},
            {"L_D": _quadratic(5.0)},
            parameter_specs=(SPAN,),
        )
        (metric,) = report.metrics
        self.assertEqual(metric.confidence, CONFIDENCE_UNSURE)
        self.assertIn("I am NOT sure", metric.statement)
        self.assertGreater(metric.std, 0.0)

    def test_uncertainty_grows_away_from_evidence(self):
        samples = _samples([0.0, 1.0, 2.0, 3.0, 4.0])
        near = assess(samples, {"span": 2.0}, {"L_D": _quadratic(2.0)},
                      parameter_specs=(SPAN,)).metrics[0]
        far = assess(samples, {"span": 9.0}, {"L_D": _quadratic(9.0)},
                     parameter_specs=(SPAN,)).metrics[0]
        self.assertLess(near.std, far.std)

    def test_too_few_samples_is_reported_honestly(self):
        report = assess(
            _samples([2.0, 8.0]),
            {"span": 5.0},
            {"L_D": _quadratic(5.0)},
            parameter_specs=(SPAN,),
        )
        (metric,) = report.metrics
        self.assertEqual(metric.confidence, CONFIDENCE_UNKNOWN)
        self.assertIn("cannot quantify", metric.statement)

    def test_design_parameters_are_not_assessed_as_outputs(self):
        samples = [
            ({"span": x}, {"L_D": _quadratic(x), "span": x}) for x in [1.0, 3.0, 5.0, 7.0, 9.0]
        ]
        report = assess(
            samples,
            {"span": 5.0},
            {"L_D": _quadratic(5.0), "span": 5.0},
            parameter_specs=(SPAN,),
        )
        self.assertEqual([item.metric for item in report.metrics], ["L_D"])

    def test_edge_of_sampled_region_is_flagged_thin(self):
        report = assess(
            _samples([0.0, 2.0, 4.0, 6.0, 8.0, 10.0]),
            {"span": 10.0},
            {"L_D": _quadratic(10.0)},
            parameter_specs=(SPAN,),
        )
        self.assertIn("span", report.thin_directions)
        self.assertIn("Evidence is thin along span", report.narration)


if __name__ == "__main__":
    unittest.main()
