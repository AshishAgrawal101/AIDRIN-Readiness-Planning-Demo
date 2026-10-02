# AIDRIN readiness planning demo

This demo focuses on choosing readiness checks before connecting them to APPFL. It includes eight synthetic dataset descriptions, suggested checks, and questions about unclear column roles.

Codex used AIDRIN's official instructions and list of available metrics to write the saved plans. The script reviews those plans rather than generating new ones. It checks metric names, arguments, and column roles, then compares the plans with reference checklists.

## Run

```bash
python planning_demo.py
python planning_demo.py --case unclear_target
python -m unittest -v
```

Use Python 3.10 or newer. No extra packages or API key are needed to review the saved plans. Results go to `output/planning_review.json`. No readiness checks run.

For a separate assistant run, export prompts with `--export-prompts <folder> --skill <installed AIDRIN SKILL.md>`. Save its replies as a JSON list and review them with `--suggestions <file>`.

The saved plans and reference checklists came from the same assistant session. This is a worked example, not an independent test of AI accuracy. The [project plan](PLAN.md) describes the proposed shared work and APPFL integration.
