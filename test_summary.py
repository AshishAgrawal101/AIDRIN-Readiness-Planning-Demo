"""Check that failed planning attempts stay in the results."""

import copy
import unittest

from planning_demo import ROOT, evaluate, metric_map, read_json
from summarize_runs import summarize


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.cases = read_json(ROOT / "cases.json")
        self.plans = read_json(ROOT / "recorded_suggestions.json")
        self.references = read_json(ROOT / "reference.json")
        self.catalogue = metric_map(read_json(ROOT / "catalogue.json"))

    def run_fixture(self, number):
        plans = copy.deepcopy(self.plans)
        return {"suggestions": plans, "review": {
            "github_run_id": str(number), "git_commit": "fixture", "requested_model": "fixture",
            "calls": [{"case_id": case["id"]} for case in self.cases], "failures": [],
            "results": evaluate(self.cases, plans, self.references, self.catalogue),
        }}

    def score(self, runs):
        return summarize(runs, self.cases, self.references, self.catalogue)

    def test_repeated_runs_count_attempts_not_unique_datasets(self):
        result = self.score([self.run_fixture(1), self.run_fixture(2)])
        self.assertEqual(result["attempts"], 16)
        self.assertEqual(result["case_count"], 8)
        self.assertEqual(result["matched"], 16)

    def test_transport_failure_is_not_removed(self):
        run = self.run_fixture(1)
        missing = run["suggestions"].pop()
        run["review"]["failures"] = [{"case_id": missing["case_id"], "stage": "api", "error": "503"}]
        run["review"]["results"] = evaluate(self.cases, run["suggestions"], self.references, self.catalogue)
        result = self.score([run])
        self.assertEqual(result["attempts"], 8)
        self.assertEqual(result["matched"], 7)
        self.assertEqual(result["api_errors"], 1)
        self.assertEqual(result["checklist_mismatches"], 0)

    def test_valid_plan_can_still_fail_checklist(self):
        run = self.run_fixture(1)
        run["suggestions"][0]["checks"] = run["suggestions"][0]["checks"][:3]
        run["review"]["results"] = evaluate(self.cases, run["suggestions"], self.references, self.catalogue)
        result = self.score([run])
        self.assertEqual(result["valid_plans"], 8)
        self.assertEqual(result["checklist_mismatches"], 1)

    def test_duplicate_run_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.score([self.run_fixture(1), self.run_fixture(1)])

    def test_changed_saved_results_are_detected(self):
        run = self.run_fixture(1)
        run["review"]["results"][0]["matched"] = False
        with self.assertRaisesRegex(ValueError, "disagree"):
            self.score([run])

    def test_missing_attempt_is_rejected(self):
        run = self.run_fixture(1)
        run["review"]["calls"].pop()
        with self.assertRaisesRegex(ValueError, "every case"):
            self.score([run])


if __name__ == "__main__":
    unittest.main()
