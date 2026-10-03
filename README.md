# AIDRIN readiness planning demo

This demo asks Gemini to choose readiness checks from synthetic dataset descriptions using AIDRIN's official skill and metric catalogue, then validates the suggestions and compares them with saved checklists.

It only produces plans. No metrics run, and APPFL integration is still proposed. Every plan needs human review.

The [live test](RESULTS.md) had 36 attempts: five plans returned, four checklist matches, and 31 API errors. There aren't enough results to judge reliability. The checklists were written by Codex, fixed before generation, and withheld from Gemini. They still need independent review.

## Run

Use Python 3.10 or newer. Review the eight original Codex-written examples without extra packages or an API key:

```bash
python planning_demo.py
python -m unittest -v
```

## Try Gemini

On GitHub, add `GEMINI_API_KEY` under **Settings > Secrets and variables > Actions**, then open **Actions > Run Gemini planner**. Select `extended` and `all` to try twelve descriptions. Never put the key in code.

Or run locally:

```bash
pip install aidrin==2026.9.1
python gemini_planner.py --dry-run
python gemini_planner.py
```

The dry run saves the prompt without calling Gemini. The live run asks privately for a key. Add `--suite extended --case all` for twelve cases. Output goes under `output/`.

Use a [free-tier key](https://aistudio.google.com/apikey) with billing disabled and synthetic descriptions only. Prompts go to Google. This uses AIDRIN's guidance, not its native agentic pipeline.

The [shared project plan](PLAN.md) describes the proposed APPFL connection.
