"""Tests for the Pope (1975) integrity-basis transcription.

The basis is the shared foundation under the two approved closure reproduction
rungs, and it was carried in this lab's records at second hand until 2026-08-02
(see ``demo-output/website/campaign/W2_POPE_1975_INTEGRITY_BASIS.md``). The
transcription lives in ``sdk/scripts/pope_1975_basis_check.py`` and the checks
there are the reason it can be trusted; this file exists so those checks run in
the suite rather than only when somebody remembers to.

Zero compute: pure algebra on synthetic velocity gradients, no solver, no mesh,
no data, nothing fitted.
"""

import sys
import unittest
from pathlib import Path

import numpy as np

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))
if str(SDK / "scripts") not in sys.path:
    sys.path.insert(0, str(SDK / "scripts"))

import pope_1975_basis_check as pope  # noqa: E402


class TestPopeBasisCheckerRuns(unittest.TestCase):
    def test_every_check_passes(self):
        """The script's own 17 checks, run as one test.

        If this fails, read the failing check's name: each one names the
        property of Pope's basis it is asserting, and a failure means the
        transcription or an identity derived from it has moved.
        """
        pope.CHECKS.clear()
        self.assertEqual(pope.main(), 0, "pope_1975_basis_check reported a failure")
        failed = [name for name, ok, _ in pope.CHECKS if not ok]
        self.assertEqual(failed, [], f"failing checks: {failed}")
        self.assertGreaterEqual(len(pope.CHECKS), 17)


class TestBasisProperties(unittest.TestCase):
    """A few of the load-bearing facts asserted directly, so that a rewrite of
    the script cannot quietly drop them."""

    def setUp(self):
        self.rng = np.random.default_rng(20260802)

    def test_ten_tensors_symmetric_and_traceless(self):
        for _ in range(50):
            s, w = pope.s_omega(pope.random_grad_3d(self.rng),
                                tau=self.rng.uniform(0.2, 4.0))
            for i, t in enumerate(pope.basis_3d(s, w), start=1):
                scale = max(np.abs(t).max(), 1e-30)
                self.assertLess(np.abs(t - t.T).max() / scale, 1e-13, f"T{i} not symmetric")
                self.assertLess(abs(np.trace(t)) / scale, 1e-13, f"T{i} not traceless")

    def test_there_are_ten_tensors_and_five_invariants(self):
        s, w = pope.s_omega(pope.random_grad_3d(self.rng))
        self.assertEqual(len(pope.basis_3d(s, w)), 10)
        self.assertEqual(len(pope.invariants_3d(s, w)), 5)
        self.assertEqual(len(pope.basis_2d(s, w)), 3)

    def test_pointwise_rank_is_five_in_3d_and_three_in_2d(self):
        """Five is the dimension of the symmetric traceless tensors, so the
        basis is complete pointwise and over-determined: the ten coefficients
        are not identifiable from a single point."""
        def rank(tensors):
            m = np.array([t.ravel() for t in tensors])
            return int(np.linalg.matrix_rank(m, tol=1e-10))

        for _ in range(50):
            s, w = pope.s_omega(pope.random_grad_3d(self.rng),
                                tau=self.rng.uniform(0.3, 3.0))
            self.assertEqual(rank(pope.basis_3d(s, w)), 5)
            s, w = pope.s_omega(pope.random_grad_2d(self.rng),
                                tau=self.rng.uniform(0.3, 3.0))
            self.assertEqual(rank(pope.basis_3d(s, w)), 3)

    def test_t5_and_t10_vanish_in_two_dimensions(self):
        """The two coefficients that no amount of 2-D training data can
        constrain. Also true on a unidirectional duct baseline."""
        for _ in range(50):
            s, w = pope.s_omega(pope.random_grad_2d(self.rng),
                                tau=self.rng.uniform(0.3, 3.0))
            t = pope.basis_3d(s, w)
            scale = max(np.abs(x).max() for x in t)
            self.assertLess(np.abs(t[4]).max(), 1e-12 * scale, "T5 is not zero in 2-D")
            self.assertLess(np.abs(t[9]).max(), 1e-12 * scale, "T10 is not zero in 2-D")

    def test_section_5_limit_case(self):
        """Pope p. 336 prints five component expressions for simple shear.
        Reproducing them from the transcription has no free parameter."""
        for _ in range(50):
            gamma, tau = self.rng.uniform(-3, 3), self.rng.uniform(0.2, 4.0)
            g0, g1, g2 = self.rng.normal(size=3)
            s, w = pope.s_omega(pope.simple_shear(gamma), tau=tau)
            t0, t1, t2 = pope.basis_2d(s, w)
            a = g0 * t0 + g1 * t1 + g2 * t2
            tg = tau * gamma
            printed = np.array([
                [-g0 / 6.0 - 0.5 * g2 * tg ** 2, 0.5 * g1 * tg, 0.0],
                [0.5 * g1 * tg, -g0 / 6.0 + 0.5 * g2 * tg ** 2, 0.0],
                [0.0, 0.0, g0 / 3.0]])
            self.assertLess(np.abs(a - printed).max(), 1e-12)

    def test_unidirectional_invariant_identities(self):
        """A duct or channel baseline: only lambda1 is independent. lambda3 and
        lambda4 vanishing was already proved in this lab's duct expressivity
        audit; lambda2 = -lambda1 and lambda5 = -lambda1^2/2 are the same kind
        of identity and take the effective count from five to one."""
        for _ in range(100):
            g = np.zeros((3, 3))
            g[0, 1], g[0, 2] = self.rng.normal(), self.rng.normal()
            s, w = pope.s_omega(g, tau=self.rng.uniform(0.1, 5.0))
            l1, l2, l3, l4, l5 = pope.invariants_3d(s, w)
            self.assertAlmostEqual(l2, -l1, places=12)
            self.assertAlmostEqual(l3 / max(abs(l1), 1e-30), 0.0, places=12)
            self.assertAlmostEqual(l4 / max(abs(l1), 1e-30), 0.0, places=12)
            self.assertLess(abs(l5 + 0.5 * l1 ** 2) / max(l1 ** 2, 1e-30), 1e-12)

    def test_pope_anisotropy_is_twice_lings(self):
        """Pope (3.1) a = <uu>/k - (2/3)I; Ling et al. b = <uu>/(2k) - (1/3)I."""
        rs = self.rng.normal(size=(3, 3))
        rs = rs @ rs.T
        k = 0.5 * np.trace(rs)
        a = rs / k - (2.0 / 3.0) * np.eye(3)
        b = rs / (2.0 * k) - np.eye(3) / 3.0
        self.assertLess(np.abs(a - 2.0 * b).max(), 1e-12)


if __name__ == "__main__":
    unittest.main()
