# Proposed AIDRIN and APPFL integration

Different datasets need different readiness checks, and someone currently has to decide which checks to use or write a custom one. [APPFL supports built-in checks and custom CADRE modules](https://appfl.ai/en/stable/tutorials/examples_dr_integration.html). [AIDRIN's skill](https://aidrin.readthedocs.io/en/latest/aidrin_skill.html) helps an assistant inspect a dataset, choose metrics, confirm column roles, and explain the results. The idea is to explore how that workflow could help people set up APPFL readiness reports with less manual work.

This is a starting proposal for discussion with the AIDRIN and APPFL teams. It describes work that could be shared, rather than a project one person would build alone. The scope and responsibilities have not been agreed on yet.

## Current demo

The [planning demonstration](README.md) includes saved AIDRIN-guided suggestions for eight synthetic descriptions and a Gemini planner that can generate new suggestions at runtime. The new runner validates plans and compares them with the example checklists. It does not run metrics or create APPFL configurations. The live API path still needs a run with a configured key.

The same assistant session produced the saved plans and reference checklists, so the original recording is an unblinded worked example. Independently reviewed references are still needed before reporting planner accuracy. The Gemini runner reads those references only after generation, but they have not been reviewed by a separate researcher.

## Possible workflow

First, the planning assistant would receive a description of a synthetic dataset. That description would include the kind of task, its data format, column names and types when relevant, and any roles a person has confirmed, such as the outcome column. The first experiments could use descriptions without patient rows. AIDRIN's normal workflow inspects sample statistics as well, so the collaborators would need to decide what information is necessary for useful suggestions and what is appropriate to share.

The assistant would use AIDRIN's existing metric guidance to suggest checks and explain why they fit the data. Its answer would name the required inputs and distinguish checks APPFL already supports from checks that would need a new implementation. An initial scope could be tabular binary-classification data, with another data type chosen together after reviewing the first results.

Next, a small adapter would turn the suggestion into a structured plan. It would reject unknown checks, missing column roles, and conflicting settings. A person could edit or reject the plan before APPFL sends the same approved configuration to every client. For an existing APPFL check, the adapter could fill in the data-readiness configuration. A check APPFL lacks would be treated as a proposed metric or CADRE module for human review and testing. Generated Python should never be sent to hospitals to run automatically.

Each client would calculate the approved checks on its own data. AIDRIN might run some metrics there too. The server report would say which checks ran, which sites failed, and which tool produced each result. It would not assume that similarly named AIDRIN and APPFL metrics use the same formula. Any summaries sent away from a client would need a separate privacy review.

## Testing the idea

The first evaluation could compare the assistant's suggested plans with researcher-reviewed checklists for several synthetic datasets. The tests should include different outcome-column names, an unclear outcome column, and unsupported suggestions. Reference reviewers should be separate from the assistant generating the plans.

Once the planning results are useful, integration tests could cover a client that fails while running a check, approval before execution, and whether patient rows appear in planning requests or server reports. A local networked APPFL run could follow the serial version.

A useful first result would show that AIDRIN can suggest reasonable checks, a person can correct the plan, and APPFL can run the approved version without someone hand-editing each client's configuration. That still would not make the system ready for real hospital data.

## Possible division of work

These are suggestions for discussion, not assigned responsibilities:

- I could develop the small prototypes, add synthetic test cases, and document the results and problems that come up.
- AIDRIN collaborators could advise on using the existing skill and tools, review metric selection, and help identify useful dataset descriptions.
- APPFL collaborators could advise on the configuration and client-server interfaces, review the adapter, and help decide what belongs in APPFL itself.
- The collaborators could choose the evaluation cases together, arrange independent review of the reference checklists, and agree on the privacy boundaries before using real data.

## Questions for discussion

Which parts of AIDRIN's skill can work from a limited dataset description? How should custom metric suggestions be reviewed? Where should the planning and approval step fit in APPFL, and what would be a useful first contribution?

This separate repository keeps the early experiments apart from the existing subgroup-calibration contribution while those questions are discussed.
