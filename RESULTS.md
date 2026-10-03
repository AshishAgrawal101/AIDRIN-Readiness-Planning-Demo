# First live planning test

On October 2, 2026, twelve synthetic descriptions were tested three times with Gemini using AIDRIN's skill and catalogue, [the same code](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/commit/f48db8fe6a53b3eab42f07f0f63d4db30d1b19ae), and checklists fixed beforehand and withheld from Gemini.

| Run | Attempts | Plans returned | Checklist matches | API errors |
| --- | ---: | ---: | ---: | ---: |
| [1](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/37080801038) | 12 | 4 | 3 | 8 |
| [2](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/37081118496) | 12 | 1 | 1 | 11 |
| [3](https://github.com/AshishAgrawal101/AIDRIN-Readiness-Planning-Demo/actions/runs/37081351311) | 12 | 0 | 0 | 12 |
| Total | 36 | 5 | 4 | 31 |

There were fifteen HTTP 503 errors and sixteen quota errors. Failed requests were kept without automatic retries, and earlier setup runs are excluded.

Four plans matched. The fifth recognized that subgroup ECE and Brier were unsupported, but omitted the baseline quality checks. All five passed structural and column-role validation.

This cannot establish reliability. Seven descriptions received no plan, and the Codex-written checklists still need independent review. Scoring covers required checks and selected arguments, not every extra suggestion or explanation.

All 58 offline tests passed, but no metrics ran or APPFL connection was made. Workflow failures reflect API errors or a checklist mismatch.

The full records are in [results/](results/). Recompute the summary with:

```bash
python summarize_runs.py results/run-37080801038 results/run-37081118496 results/run-37081351311 --output output/evaluation_summary.json
```
