# First live planning test

On October 2, 2026, I tested twelve synthetic dataset descriptions three times using Gemini with AIDRIN's official skill and metric catalogue. All three runs used [the same code](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/commit/f48db8fe6a53b3eab42f07f0f63d4db30d1b19ae) and the same checklists, which were saved before generation and were not sent to Gemini.

| Run | Attempts | Plans returned | Checklist matches | API errors |
| --- | ---: | ---: | ---: | ---: |
| [1](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/37080801038) | 12 | 4 | 3 | 8 |
| [2](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/37081118496) | 12 | 1 | 1 | 11 |
| [3](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/37081351311) | 12 | 0 | 0 | 12 |
| Total | 36 | 5 | 4 | 31 |

Fifteen requests returned HTTP 503 errors, and sixteen hit quota errors. Failed requests were kept in the results. There were no automatic retries, and the earlier single-case setup runs are outside this batch.

Four plans matched the checklists. These covered an unclear target, an unconfirmed demographic field, daily sensor readings, and file-reference validation. The remaining plan recognized that subgroup ECE and Brier were unsupported, but omitted the baseline quality checks expected by the guidance. All five plans passed the structural and column-role validation.

There are too few returned plans to judge reliability or consistency between runs. Seven descriptions never received a plan. The checklists were written by Codex and still need independent review. The comparison checks required metrics, selected arguments, questions, and prohibited choices, but does not fully grade explanations or optional extra checks.

No readiness metrics ran, and APPFL is not connected. All 58 offline code tests passed. The workflows show failure because the planning evaluation was incomplete or had a checklist mismatch.

Saved plans and reports are under [results/](results/). Recompute the summary with:

```bash
python summarize_runs.py results/run-37080801038 results/run-37081118496 results/run-37081351311 --output output/evaluation_summary.json
```

The next step is to review the checklists with the collaborators, address API availability, and test more descriptions before connecting approved plans to APPFL.
