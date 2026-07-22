"""Live worker-kill recovery: a sabotaged worker is reprovisioned and the
mission completes with the same numbers as an unsabotaged run (#22)."""

import os
import tempfile
import unittest
from types import SimpleNamespace

from chief_engineer.api import SyntheticApi
from chief_engineer.fleet import (ApiFleet, LocalVmProvider, WorkerTask,
                                  _sabotage_marker, clear_sabotage)
from chief_engineer.models import Candidate


def _tasks(n):
    out = []
    for i in range(n):
        candidate = Candidate(id=f"c{i}", parent_id=None, design={"span": float(i), "chord": 1.0},
                              proposed_by="geometry", rationale="probe", iteration=0)
        out.append(WorkerTask(candidate=candidate, specialist="aerodynamics",
                              analyses=("cfd",)))
    return out


class WorkerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.environ["CERTONOMOUS_SABOTAGE_DIR"] = self.dir

    def tearDown(self):
        os.environ.pop("CERTONOMOUS_SABOTAGE_DIR", None)

    def _fleet(self, events):
        return ApiFleet(LocalVmProvider(), lambda _h: SyntheticApi(), max_workers=4,
                        event_sink=lambda e, p: events.append((e, p)))

    def test_killed_worker_run_matches_a_clean_run(self):
        plan = SimpleNamespace(worker_count=3)
        tasks = _tasks(6)

        clean_events = []
        clean = self._fleet(clean_events).evaluate(tasks, plan)

        # Arm the sabotage for worker slot 1, then run the same tasks.
        _sabotage_marker(1).parent.mkdir(parents=True, exist_ok=True)
        _sabotage_marker(1).touch()
        sab_events = []
        sabotaged = self._fleet(sab_events).evaluate(tasks, plan)

        kinds = [e for e, _ in sab_events]
        self.assertIn("worker.killed", kinds)
        self.assertIn("worker.reprovisioned", kinds)
        # The clean run never reports a kill.
        self.assertNotIn("worker.killed", [e for e, _ in clean_events])

        # Every candidate is still evaluated, and the numbers match the clean run.
        self.assertEqual([r.candidate_id for r in sabotaged],
                         [r.candidate_id for r in clean])
        self.assertEqual({r.candidate_id: r.metrics for r in sabotaged},
                         {r.candidate_id: r.metrics for r in clean})
        # The recovery wave cleared the marker.
        self.assertFalse(_sabotage_marker(1).exists())

    def test_no_marker_means_no_recovery(self):
        clear_sabotage(1)
        events = []
        result = self._fleet(events).evaluate(_tasks(4), SimpleNamespace(worker_count=2))
        self.assertEqual(len(result), 4)
        self.assertNotIn("worker.killed", [e for e, _ in events])


if __name__ == "__main__":
    unittest.main()
