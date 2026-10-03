"""Test the Gemini runner without an API key or network calls."""

import copy
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from gemini_planner import (
    ENDPOINT, NoRedirect, call_gemini, get_api_key, main, parse_plan, plan_schema,
    suite_cases, suite_references,
)
from planning_demo import ROOT, file_digest, metric_map, read_json


class GeminiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = read_json(ROOT / "catalogue.json")
        cls.catalogue = metric_map(cls.snapshot)
        cls.case = next(case for case in read_json(ROOT / "cases.json") if case["id"] == "unclear_target")
        cls.plan = next(plan for plan in read_json(ROOT / "recorded_suggestions.json") if plan["case_id"] == cls.case["id"])

    def response(self, plan=None):
        return {"status": "completed", "model": "fixture-model", "usage": {"total_tokens": 123}, "steps": [
            {"type": "thought", "signature": "ignored"},
            {"type": "model_output", "content": [{"type": "text", "text": json.dumps(plan or self.plan)}]},
        ]}

    def test_completed_plan_is_validated(self):
        self.assertEqual(parse_plan(self.response(), self.case, self.catalogue), self.plan)

    def test_unconfirmed_target_is_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["checks"].append({"metric": "class-imbalance", "arguments": {"target-column": "event"}, "reason": "guess"})
        with self.assertRaisesRegex(ValueError, "unconfirmed"):
            parse_plan(self.response(plan), self.case, self.catalogue)

    def test_cannot_disable_human_review(self):
        plan = copy.deepcopy(self.plan)
        plan["approval_required"] = False
        with self.assertRaisesRegex(ValueError, "approval"):
            parse_plan(self.response(plan), self.case, self.catalogue)

    def test_incomplete_response_rejected(self):
        response = self.response()
        response["status"] = "failed"
        with self.assertRaises(ValueError):
            parse_plan(response, self.case, self.catalogue)

    def test_duplicate_fields_rejected(self):
        response = self.response()
        response["steps"][-1]["content"][0]["text"] = '{"case_id":"a","case_id":"b"}'
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            parse_plan(response, self.case, self.catalogue)

    def test_nonfinite_json_rejected(self):
        response = self.response()
        response["steps"][-1]["content"][0]["text"] = '{"anything": NaN}'
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            parse_plan(response, self.case, self.catalogue)

    def test_tool_calls_rejected(self):
        response = self.response()
        response["steps"].append({"type": "function_call"})
        with self.assertRaisesRegex(ValueError, "tool call"):
            parse_plan(response, self.case, self.catalogue)

    def test_malformed_steps_rejected(self):
        for steps in (None, {}, "text"):
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                parse_plan({"status": "completed", "steps": steps}, self.case, self.catalogue)

    def test_schema_uses_catalogue_argument_names(self):
        schema = plan_schema(self.case, self.catalogue)
        choices = schema["properties"]["checks"]["items"]["anyOf"]
        self.assertEqual(len(choices), len(self.catalogue))
        for choice in choices:
            name = choice["properties"]["metric"]["enum"][0]
            args = choice["properties"]["arguments"]
            self.assertEqual(set(args["required"]), set(self.catalogue[name]["required_args"]))
            self.assertFalse(args["additionalProperties"])

    def test_key_only_in_header(self):
        with patch("gemini_planner.request.build_opener") as builder:
            builder.return_value.open.return_value.__enter__.return_value.read.return_value = b'{"status":"completed"}'
            call_gemini({"model": "fixture-model", "input": "synthetic"}, "fixture-secret")
            req = builder.return_value.open.call_args.args[0]
            self.assertEqual(req.full_url, ENDPOINT)
            self.assertNotIn(b"fixture-secret", req.data)
            self.assertNotIn("fixture-secret", req.full_url)
            self.assertEqual(req.get_header("X-goog-api-key"), "fixture-secret")

    def test_http_errors_hide_response_body(self):
        with patch("gemini_planner.request.build_opener") as builder:
            builder.return_value.open.side_effect = HTTPError(ENDPOINT, 429, "fixture-secret", {}, BytesIO(b"fixture-secret"))
            with self.assertRaisesRegex(ValueError, "quota") as caught:
                call_gemini({}, "fixture-secret")
            self.assertNotIn("fixture-secret", str(caught.exception))

    def test_network_errors_hide_details(self):
        with patch("gemini_planner.request.build_opener") as builder:
            builder.return_value.open.side_effect = URLError("fixture-secret")
            with self.assertRaisesRegex(ValueError, "connection") as caught:
                call_gemini({}, "fixture-secret")
            self.assertNotIn("fixture-secret", str(caught.exception))

    def test_redirects_cannot_forward_key(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "", {}, "https://elsewhere.test"))

    def test_existing_key_does_not_prompt(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fixture-secret"}), patch("gemini_planner.getpass.getpass") as prompt:
            self.assertEqual(get_api_key(), "fixture-secret")
            prompt.assert_not_called()

    def test_hidden_prompt_when_no_key(self):
        with patch.dict("os.environ", {}, clear=True), patch("gemini_planner.sys.stdin.isatty", return_value=True), \
                patch("gemini_planner.getpass.getpass", return_value="fixture-secret"):
            self.assertEqual(get_api_key(), "fixture-secret")

    def test_missing_noninteractive_key_fails(self):
        with patch.dict("os.environ", {}, clear=True), patch("gemini_planner.sys.stdin.isatty", return_value=False):
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
                get_api_key()

    def test_dry_run_never_requests_key_or_calls_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text("fixture guidance", encoding="utf-8")
            snapshot = {**self.snapshot, "skill_sha256": file_digest(skill)}
            original = read_json
            def read(path):
                return snapshot if Path(path).name == "catalogue.json" else original(path)
            with patch("gemini_planner.read_json", side_effect=read), patch("gemini_planner.get_api_key") as key, \
                    patch("gemini_planner.call_gemini") as api:
                self.assertEqual(main(["--dry-run", "--skill", str(skill), "--output-dir", str(root / "run")]), 0)
                key.assert_not_called()
                api.assert_not_called()
            record = read_json(root / "run" / "review.json")
            self.assertEqual(record["mode"], "prompt_preview")
            prompt = (root / "run" / "unclear_target_prompt.txt").read_text(encoding="utf-8")
            self.assertNotIn('"required_metrics"', prompt)
            self.assertFalse((root / "run" / "suggestions.json").exists())

    def test_mocked_run_records_validated_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text("fixture guidance", encoding="utf-8")
            snapshot = {**self.snapshot, "skill_sha256": file_digest(skill)}
            original = read_json
            def read(path):
                return snapshot if Path(path).name == "catalogue.json" else original(path)
            with patch("gemini_planner.read_json", side_effect=read), \
                    patch("gemini_planner.get_api_key", return_value="fixture-secret"), \
                    patch("gemini_planner.call_gemini", return_value=self.response()) as api:
                self.assertEqual(main(["--skill", str(skill), "--output-dir", str(root / "run")]), 0)
                payload = api.call_args.args[0]
                self.assertFalse(payload["store"])
                self.assertNotIn("tools", payload)
                self.assertNotIn('"required_metrics"', payload["input"])
            record = read_json(root / "run" / "review.json")
            self.assertTrue(record["results"][0]["matched"])
            self.assertEqual(read_json(root / "run" / "suggestions.json"), [self.plan])
            for path in (root / "run").iterdir():
                self.assertNotIn("fixture-secret", path.read_text(encoding="utf-8"))

    def test_failed_call_saves_no_accepted_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text("fixture guidance", encoding="utf-8")
            snapshot = {**self.snapshot, "skill_sha256": file_digest(skill)}
            original = read_json
            def read(path):
                return snapshot if Path(path).name == "catalogue.json" else original(path)
            with patch("gemini_planner.read_json", side_effect=read), \
                    patch("gemini_planner.get_api_key", return_value="fixture-secret"), \
                    patch("gemini_planner.call_gemini", side_effect=ValueError("quota reached")):
                self.assertEqual(main(["--skill", str(skill), "--output-dir", str(root / "run")]), 1)
            record = read_json(root / "run" / "review.json")
            self.assertEqual(record["failures"][0]["error"], "quota reached")
            self.assertEqual(record["failures"][0]["stage"], "api")
            self.assertFalse(record["results"][0]["matched"])
            self.assertEqual(read_json(root / "run" / "suggestions.json"), [])

    def test_extended_suite_has_fixed_references_for_twelve_cases(self):
        cases = suite_cases("extended")
        references = suite_references("extended")
        self.assertEqual(len(cases), 12)
        self.assertEqual({case["id"] for case in cases}, set(references))

    def test_existing_suite_is_unchanged(self):
        self.assertEqual(len(suite_cases("examples")), 8)
        self.assertEqual(len(suite_references("examples")), 8)


if __name__ == "__main__":
    unittest.main()
