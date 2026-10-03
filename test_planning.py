"""Check the plan validator and example comparison."""

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from planning_demo import (
    ROOT, compare, evaluate, export_prompts, file_digest, metric_map, read_json, validate_suggestion,
    verify_recording,
)


class PlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = read_json(ROOT / "cases.json")
        cls.recorded = read_json(ROOT / "recorded_suggestions.json")
        cls.references = read_json(ROOT / "reference.json")
        cls.snapshot = read_json(ROOT / "catalogue.json")
        cls.catalogue = metric_map(cls.snapshot)

    def pair(self, case_id="renamed_target"):
        case = next(case for case in self.cases if case["id"] == case_id)
        suggestion = next(item for item in self.recorded if item["case_id"] == case_id)
        return copy.deepcopy(suggestion), copy.deepcopy(case)

    def test_recorded_examples_match_checklists(self):
        results = evaluate(self.cases, self.recorded, self.references, self.catalogue)
        self.assertEqual(len(results), 8)
        self.assertTrue(all(result["matched"] for result in results))

    def test_reject_unknown_metric(self):
        plan, case = self.pair()
        plan["checks"][0]["metric"] = "subgroup-ece"
        with self.assertRaisesRegex(ValueError, "unknown AIDRIN metric"):
            validate_suggestion(plan, case, self.catalogue)

    def test_reject_unknown_column(self):
        plan, case = self.pair()
        plan["checks"][-1]["arguments"]["columns"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "invalid columns"):
            validate_suggestion(plan, case, self.catalogue)

    def test_approval_cannot_be_disabled(self):
        plan, case = self.pair()
        plan["approval_required"] = False
        with self.assertRaisesRegex(ValueError, "approval"):
            validate_suggestion(plan, case, self.catalogue)

    def test_numeric_truthy_approval_is_not_accepted(self):
        plan, case = self.pair()
        plan["approval_required"] = 1
        with self.assertRaises(ValueError):
            validate_suggestion(plan, case, self.catalogue)

    def test_missing_metric_is_reported(self):
        plan, _ = self.pair()
        plan["checks"] = [check for check in plan["checks"] if check["metric"] != "class-imbalance"]
        self.assertIn("missing metrics: class-imbalance", compare(plan, self.references["renamed_target"]))

    def test_feature_column_order_does_not_change_match(self):
        plan, _ = self.pair()
        plan["checks"][4]["arguments"]["numerical-columns"].reverse()
        self.assertEqual(compare(plan, self.references["renamed_target"]), [])

    def test_cannot_guess_an_existing_target_column(self):
        plan, case = self.pair("unclear_target")
        plan["checks"].append({"metric": "class-imbalance", "arguments": {"target-column": "outcome"}, "reason": "guess"})
        with self.assertRaisesRegex(ValueError, "unconfirmed"):
            validate_suggestion(plan, case, self.catalogue)

    def test_confirmed_target_must_be_used(self):
        plan, case = self.pair()
        plan["checks"][3]["arguments"]["target-column"] = "age"
        with self.assertRaisesRegex(ValueError, "incorrect role"):
            validate_suggestion(plan, case, self.catalogue)

    def test_reject_missing_arguments(self):
        plan, case = self.pair()
        plan["checks"][3]["arguments"] = {}
        with self.assertRaisesRegex(ValueError, "required arguments"):
            validate_suggestion(plan, case, self.catalogue)

    def test_reject_extra_arguments(self):
        plan, case = self.pair()
        plan["checks"][0]["arguments"] = {"shell_command": "anything"}
        with self.assertRaises(ValueError):
            validate_suggestion(plan, case, self.catalogue)

    def test_reject_duplicate_metrics(self):
        plan, case = self.pair()
        plan["checks"].append(plan["checks"][0])
        with self.assertRaisesRegex(ValueError, "duplicate metric"):
            validate_suggestion(plan, case, self.catalogue)

    def test_reject_empty_reason(self):
        plan, case = self.pair()
        plan["checks"][0]["reason"] = " "
        with self.assertRaisesRegex(ValueError, "reason"):
            validate_suggestion(plan, case, self.catalogue)

    def test_feature_relevance_needs_features(self):
        plan, case = self.pair()
        plan["checks"][4]["arguments"].update({"categorical-columns": [], "numerical-columns": []})
        with self.assertRaisesRegex(ValueError, "needs feature"):
            validate_suggestion(plan, case, self.catalogue)

    def test_empty_categorical_features_are_allowed(self):
        plan, case = self.pair()
        plan["checks"][4]["arguments"]["categorical-columns"] = []
        validate_suggestion(plan, case, self.catalogue)

    def test_clarification_status_requires_question(self):
        plan, case = self.pair("unclear_target")
        plan["questions"] = []
        with self.assertRaisesRegex(ValueError, "needs a question"):
            validate_suggestion(plan, case, self.catalogue)

    def test_missing_role_question_is_reported(self):
        plan, _ = self.pair("unclear_target")
        plan["questions"][0]["role"] = "unrelated"
        self.assertIn("missing clarification: target", compare(plan, self.references["unclear_target"]))

    def test_privacy_identifiers_cannot_be_guessed(self):
        plan, case = self.pair("privacy_roles_missing")
        plan["checks"].append({"metric": "k-anonymity", "arguments": {"quasi-identifiers": ["age", "zipcode"]}, "reason": "guess"})
        with self.assertRaisesRegex(ValueError, "unconfirmed"):
            validate_suggestion(plan, case, self.catalogue)

    def test_frequency_cannot_be_changed(self):
        plan, case = self.pair("hourly_sensor")
        plan["checks"][-1]["arguments"]["frequency"] = "D"
        with self.assertRaisesRegex(ValueError, "frequency"):
            validate_suggestion(plan, case, self.catalogue)

    def test_unsupported_status_requires_disclosure(self):
        plan, case = self.pair("unsupported_calibration")
        plan["unsupported_requests"] = []
        with self.assertRaisesRegex(ValueError, "unsupported request"):
            validate_suggestion(plan, case, self.catalogue)

    def test_focused_file_request_excludes_baseline(self):
        plan, _ = self.pair("image_manifest")
        plan["checks"].append({"metric": "completeness", "arguments": {}, "reason": "extra"})
        self.assertIn("checks exceed the focused request", compare(plan, self.references["image_manifest"]))

    def test_missing_case_is_not_silently_dropped(self):
        results = evaluate(self.cases, self.recorded[:-1], self.references, self.catalogue)
        self.assertEqual(results[-1]["problems"], ["missing suggestion"])

    def test_duplicate_case_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate case"):
            evaluate(self.cases, self.recorded + [self.recorded[0]], self.references, self.catalogue)

    def test_unknown_case_is_rejected(self):
        extra = {**self.recorded[0], "case_id": "unknown"}
        with self.assertRaisesRegex(ValueError, "unknown cases"):
            evaluate(self.cases, self.recorded + [extra], self.references, self.catalogue)

    def test_malformed_document_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be a list"):
            evaluate(self.cases, {}, self.references, self.catalogue)

    def test_extra_executable_field_is_rejected(self):
        plan, case = self.pair()
        plan["python_code"] = "print('not executed')"
        with self.assertRaisesRegex(ValueError, "plan fields"):
            validate_suggestion(plan, case, self.catalogue)

    def test_prompts_include_cases_but_no_reference_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text("Official-guidance fixture", encoding="utf-8")
            export_prompts(self.cases, self.snapshot, skill, root / "prompts")
            prompts = list((root / "prompts").glob("*.txt"))
            self.assertEqual(len(prompts), 8)
            for prompt in prompts:
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("Official-guidance fixture", text)
                self.assertNotIn('"required_metrics"', text)
                self.assertNotIn('"expected_arguments"', text)

    def test_malformed_status_is_rejected(self):
        plan, case = self.pair()
        plan["status"] = []
        with self.assertRaisesRegex(ValueError, "unknown status"):
            validate_suggestion(plan, case, self.catalogue)

    def test_saved_provenance_matches_files(self):
        verify_recording(read_json(ROOT / "provenance.json"), ROOT)

    def test_changed_recording_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "cases.json"
            path.write_text("original", encoding="utf-8")
            provenance = {"files_sha256": {"cases.json": hashlib.sha256(path.read_bytes()).hexdigest()}}
            verify_recording(provenance, root)
            path.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "has changed"):
                verify_recording(provenance, root)

    def test_digest_accepts_windows_or_unix_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unix.json").write_bytes(b"first\nsecond\n")
            (root / "windows.json").write_bytes(b"first\r\nsecond\r\n")
            self.assertEqual(file_digest(root / "unix.json"), file_digest(root / "windows.json"))


if __name__ == "__main__":
    unittest.main()
