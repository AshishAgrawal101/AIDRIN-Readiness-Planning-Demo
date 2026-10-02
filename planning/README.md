# AIDRIN-guided planning examples

I wanted to test the part Mr. Li suggested: choosing useful readiness checks for a new dataset. This folder has eight synthetic dataset descriptions and suggested plans made in a Codex session using AIDRIN's installed skill and metric catalogue.

The examples include an unclear outcome column, a renamed outcome, missing privacy roles, hourly sensor data, and an image manifest. One case asks for subgroup ECE and Brier scores, which are absent from the captured built-in catalogue. The suggestion should explain that limitation instead of inventing a metric.

## Run

From the repository root:

```bash
python planning_demo.py
python planning_demo.py --case unclear_target
python -m unittest -v test_planning
```

These commands review saved suggestions. They do not call an AI model, run readiness metrics, or train anything. The JSON comparison report goes to `output/planning_review.json`.

`cases.json` contains descriptions, column types, and roles the user has already confirmed. There are no patient rows. `recorded_suggestions.json` contains the proposed checks, arguments, reasons, and clarification questions. `reference.json` is a small checklist for each case, written before the recorded suggestions were saved.

The validator rejects unknown metric names, nonexistent columns, duplicate checks, and unconfirmed roles. Every saved plan must say that human approval is required. This reviewer never executes a plan. The comparison then checks for expected metrics and questions. It does not judge the quality of the explanations or prove that the dataset is ready.

## How AIDRIN was used

I read the official skill and metric reference from the installed AIDRIN 2026.9.1 package and ran `aidrin list` to capture its 28 available metrics. The assistant then used those instructions to write the plans in this session. AIDRIN supplies the guidance and tools; the assistant supplies the suggestions.

The source version, guidance hashes, and catalogue are recorded in `catalogue.json`. `provenance.json` identifies the recorded run and the reference files. The capture script refreshes the catalogue from an installed AIDRIN environment:

```bash
python planning/capture_context.py
```

Use the Python environment containing AIDRIN for that command. Refreshing the catalogue changes the experiment context, so review the plans and provenance afterward.

## Try a separate planning session

To export prompts with the official skill, catalogue, and case descriptions, but no reference answers:

```bash
python planning_demo.py --export-prompts output/planning-prompts --skill .venv/Lib/site-packages/aidrin/skill/SKILL.md
```

Use the skill path from your installed AIDRIN environment. Give each prompt to a separate assistant session, save the replies as a JSON list in a new file, then compare them:

```bash
python planning_demo.py --suggestions new_suggestions.json
```

Record the assistant, model if known, date, and any manual edits. Do not show it the reference answers. A researcher should review the reference checklists too, since several plans can be reasonable for the same dataset.

## What this shows so far

This is a worked example of the planning workflow, not a measured AI accuracy rate. The same assistant session wrote the checklists and suggestions and could see both. They were not independently reviewed or blinded. A clean comparison is useful for checking the file format and review logic, but it does not establish how well an agent will perform on unfamiliar data.

The next useful test is a separate planning run against researcher-reviewed cases. After that, we can decide how an approved plan should connect to APPFL.
