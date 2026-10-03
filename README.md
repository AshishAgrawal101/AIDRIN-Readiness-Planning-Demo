# AIDRIN readiness planning demo

This demo tests whether an assistant can choose readiness checks from synthetic dataset descriptions. It does not run those checks or connect them to APPFL yet.

`gemini_planner.py` asks Gemini to suggest checks using AIDRIN's official instructions and metric catalogue. The code validates metric names, arguments, and confirmed column roles, then compares each plan with a saved checklist. The original eight Codex-written plans are also kept as worked examples.

## Run

```bash
python planning_demo.py
python planning_demo.py --case unclear_target
python -m unittest -v
```

Use Python 3.10 or newer. No extra packages or API key are needed to review the saved plans. Results go to `output/planning_review.json`. No readiness checks run.

## Try Gemini

On GitHub, add a repository secret named `GEMINI_API_KEY` under **Settings > Secrets and variables > Actions**. Paste the key in the **Secret** field, never in a code file. Then open **Actions > Run Gemini planner > Run workflow**. Start with `unclear_target`. The run saves its JSON results as a downloadable artifact. It only runs when you click the button.

To run it locally instead:

```bash
pip install aidrin==2026.9.1
python gemini_planner.py --dry-run
python gemini_planner.py
```

The dry run saves the prompt without an API call. The next command asks for a Gemini key in a hidden terminal prompt, then generates a plan for `unclear_target`. The key is not saved. Never paste it into GitHub.

Use a [Gemini free-tier key](https://aistudio.google.com/apikey) with billing disabled. These calls send the synthetic description, AIDRIN guidance, and metric catalogue to Google. No real patient data belongs in this demo.

Use `--case all` for the original eight cases, or `--suite extended --case all` for all twelve. On GitHub, select the `extended` suite and `all` case. If AIDRIN is installed elsewhere, use `--skill <path to SKILL.md>`. Plans and review results go to a new folder under `output/`. Invalid plans and API failures are recorded without automatic retries.

This is our Gemini planner using AIDRIN's skill, rather than AIDRIN's native agentic pipeline. APPFL execution is still proposed work. Every plan needs human review.

The [results](RESULTS.md) cover three live runs of twelve descriptions. Checklists were fixed before those runs and were not sent to Gemini, but they were assistant-written and still need independent review. This is a small planning test, not proof of reliability on real datasets. The [project plan](PLAN.md) describes possible shared work with the AIDRIN and APPFL teams.
