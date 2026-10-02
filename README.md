# AIDRIN readiness planning demo

This demo focuses on choosing readiness checks before connecting them to APPFL. It includes eight synthetic dataset descriptions, suggested checks, and questions about unclear column roles.

Codex used AIDRIN's official instructions and list of available metrics to write the saved plans. `planning_demo.py` checks their metric names, arguments, and column roles, then compares them with reference checklists. `gemini_planner.py` can ask Gemini for new plans using the same guidance.

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

Use `--case all` for eight requests or `--model <name>` to choose a supported model. If AIDRIN is installed elsewhere, use `--skill <path to SKILL.md>`. Plans and review results go to a new folder under `output/`. Invalid plans are rejected, and failures are recorded without automatic retries. No readiness checks run.

This is our Gemini planner using AIDRIN's skill, rather than AIDRIN's native agentic pipeline. APPFL execution is still proposed work. Every plan needs human review.

The reference checklists were written by the same assistant that wrote the saved plans. They still need independent review before we can report planner accuracy. The [project plan](PLAN.md) describes the proposed shared work and APPFL integration.
