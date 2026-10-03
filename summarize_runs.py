"""Combine repeated planning results without dropping failed attempts."""

import argparse
import json
from pathlib import Path

from gemini_planner import suite_cases, suite_references
from planning_demo import ROOT, evaluate, file_digest, metric_map, read_json


def summarize(runs, cases, references, catalogue):
    rows = {case["id"]: {"case_id": case["id"], "matched": 0, "valid_plans": 0,
                         "api_errors": 0, "rejected_plans": 0, "metric_sets": set()} for case in cases}
    sources = []
    seen_runs = set()
    for run in runs:
        report, plans = run["review"], run["suggestions"]
        run_id = report["github_run_id"]
        if not run_id or run_id in seen_runs:
            raise ValueError("missing or duplicate GitHub run ID")
        seen_runs.add(run_id)
        ids = [call["case_id"] for call in report["calls"]]
        if len(ids) != len(rows) or set(ids) != set(rows):
            raise ValueError("each run must attempt every case exactly once")
        results = evaluate(cases, plans, references, catalogue)
        if results != report["results"]:
            raise ValueError("saved and recomputed checklist results disagree")
        failure_map = {failure["case_id"]: failure for failure in report["failures"]}
        plan_map = {plan["case_id"]: plan for plan in plans}
        if len(failure_map) != len(report["failures"]) or set(failure_map) & set(plan_map):
            raise ValueError("duplicate or conflicting outcomes")
        if set(failure_map) | set(plan_map) != set(rows):
            raise ValueError("every attempt needs a plan or a recorded failure")
        for result in results:
            row = rows[result["case_id"]]
            row["matched"] += int(result["matched"])
            if result["case_id"] in plan_map:
                plan = plan_map[result["case_id"]]
                row["valid_plans"] += 1
                row["metric_sets"].add(tuple(sorted(check["metric"] for check in plan["checks"])))
            else:
                stage = failure_map[result["case_id"]]["stage"]
                if stage not in {"api", "plan"}:
                    raise ValueError("unknown failure stage")
                row["api_errors" if stage == "api" else "rejected_plans"] += 1
        sources.append({"run_id": run_id, "commit": report["git_commit"],
                        "url": "https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/" + str(run_id)})
    if not sources:
        raise ValueError("no runs supplied")
    per_case = []
    for row in rows.values():
        row["metric_sets"] = [list(names) for names in sorted(row["metric_sets"])]
        row["checklist_mismatches"] = row["valid_plans"] - row["matched"]
        per_case.append(row)
    return {
        "model": runs[0]["review"]["requested_model"],
        "case_count": len(cases), "run_count": len(runs), "attempts": len(cases) * len(runs),
        "matched": sum(row["matched"] for row in per_case),
        "valid_plans": sum(row["valid_plans"] for row in per_case),
        "api_errors": sum(row["api_errors"] for row in per_case),
        "rejected_plans": sum(row["rejected_plans"] for row in per_case),
        "checklist_mismatches": sum(row["checklist_mismatches"] for row in per_case),
        "sources": sources, "per_case": per_case,
        "limitations": [
            "Small synthetic-description test, not evidence of general reliability on real datasets.",
            "Checklists were assistant-authored and fixed before the batch runs, without independent human review.",
            "Reference answers were withheld from Gemini. The skill and schema constrain its choices.",
            "Only selected arguments and prohibited checks are graded; optional extra checks and explanation quality need review.",
            "Repeated runs use the same descriptions, not distinct datasets.",
            "No readiness metrics or APPFL execution took place.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, default=ROOT.parent / "output/evaluation_summary.json")
    args = parser.parse_args()
    cases, references = suite_cases("extended"), suite_references("extended")
    snapshot = read_json(ROOT / "catalogue.json")
    setup = read_json(ROOT / "evaluation_setup.json")
    runs = []
    for folder in args.runs:
        report = read_json(folder / "review.json")
        if (report.get("mode") != "live_gemini_planning" or report.get("suite") != "extended"
                or report.get("evaluation_setup") != setup or report.get("requested_model") != setup["model"]):
            parser.error("run does not match the fixed evaluation setup")
        for field, name in {"cases_sha256": "cases.json", "catalogue_sha256": "catalogue.json",
                            "reference_sha256": "reference.json"}.items():
            if report.get(field) != file_digest(ROOT / name):
                parser.error("run uses different context files")
        runs.append({"review": report, "suggestions": read_json(folder / "suggestions.json")})
    if len({run["review"]["git_commit"] for run in runs}) != 1:
        parser.error("runs used different commits")
    result = summarize(runs, cases, references, metric_map(snapshot))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Matched: {result['matched']}/{result['attempts']} attempts")
    print(f"API errors: {result['api_errors']}; rejected plans: {result['rejected_plans']}; checklist mismatches: {result['checklist_mismatches']}")
    for row in result["per_case"]:
        print(f"{row['case_id']}: {row['matched']}/{result['run_count']} matched")


if __name__ == "__main__":
    main()
