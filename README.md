# AIDRIN readiness planning demo

Mr. Li suggested exploring whether AIDRIN could help APPFL choose data-readiness checks for new datasets. This demo focuses on choosing the checks before connecting them to APPFL.

The [planning examples](planning/README.md) cover eight synthetic dataset descriptions. The saved suggestions were produced in a Codex session using AIDRIN's official skill and installed metric catalogue. They include reasons for each check and questions when column roles are unclear.

For example, when two columns could be the outcome, the plan asks which one to use. Another case requests subgroup ECE and Brier scores, which are absent from the captured built-in catalogue. The plan flags them as unsupported instead of inventing a metric.

## Run

```bash
python planning_demo.py
python planning_demo.py --case unclear_target
python -m unittest -v
```

Use Python 3.10 or newer. Reviewing the saved plans requires no third-party packages or API key. The script checks metric names, arguments, and confirmed column roles, then compares the suggestions with example checklists. It does not call an AI model or execute readiness checks. Results go to `output/planning_review.json`.

The checklists and suggestions came from the same session, so this is a worked example rather than an independent accuracy test. The [planning instructions](planning/README.md) explain how to export case-only prompts for a separate run. The [project plan](PLAN.md) describes how reviewed suggestions could eventually connect to APPFL.
