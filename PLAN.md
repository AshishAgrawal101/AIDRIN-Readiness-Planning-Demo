# Proposed AIDRIN and APPFL integration

The idea is to use [AIDRIN's guidance](https://aidrin.readthedocs.io/en/latest/aidrin_skill.html) to help choose readiness checks for new datasets, then let [APPFL](https://appfl.ai/en/stable/tutorials/examples_dr_integration.html) run an approved plan on each client's data.

This is a shared-work proposal. The AIDRIN and APPFL teams would help decide the scope and responsibilities, starting with a review of the [current demo](README.md) and its limited [results](RESULTS.md).

## Proposed workflow

Start with synthetic tabular data. Give the assistant the task, column names and types, and confirmed roles such as the outcome column, so it can suggest checks without patient rows and ask about missing roles.

A small adapter would check the suggestions and turn supported checks into APPFL settings, with a person approving the plan before clients receive it. Any new metric would need separate review and tests before use, and generated code would never be sent to clients to run automatically.

Clients would calculate approved checks locally, and the server would report results and failures. Before treating AIDRIN and APPFL metrics as equivalent, we would check their formulas and inputs, and separately review the privacy of any shared summaries.

## Next steps together

I could work on prototypes and synthetic tests. AIDRIN collaborators could review the checklists and advise on the existing tools, while APPFL collaborators could help choose the adapter's place in the framework.

Next, resolve API access and have researchers independently review the checklists. Then test unseen descriptions before a small APPFL run covering approval and client failures, with checks for possible data leakage. The team would need to agree on privacy boundaries before using real data.
