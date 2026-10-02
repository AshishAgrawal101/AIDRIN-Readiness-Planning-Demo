# Proposed AIDRIN and APPFL integration

Different datasets need different readiness checks, and someone currently has to decide which checks to use or write a custom one. [APPFL supports built-in checks and custom CADRE modules](https://appfl.ai/en/stable/tutorials/examples_dr_integration.html). [AIDRIN's skill](https://aidrin.readthedocs.io/en/latest/aidrin_skill.html) helps an assistant inspect a dataset, choose metrics, confirm column roles, and explain the results. I want to see how that workflow could help people set up APPFL readiness reports with less manual work.

## What I have so far

The [planning demonstration](planning/README.md) records AIDRIN-guided assistant suggestions for eight synthetic descriptions and compares them with example checklists. The same assistant session produced both, so it is an unblinded worked example. A separate run with independently reviewed references is still needed before reporting planner accuracy. There is no standalone agent generating APPFL configurations yet.

## How I would connect them

First, I would give the planning assistant a description of a synthetic dataset. That description would include the kind of task, its data format, column names and types when relevant, and any roles a person has confirmed, such as the outcome column. I would start without patient rows. AIDRIN's normal workflow inspects sample statistics as well, so I need to find out what information is necessary for useful suggestions and what is appropriate to share.

The assistant would use AIDRIN's existing metric guidance to suggest checks and explain why they fit the data. Its answer would name the required inputs and distinguish checks APPFL already supports from checks that would need a new implementation. I would begin with tabular binary-classification data, then use feedback from the AIDRIN and APPFL teams to choose another data type worth testing.

Next, a small adapter would turn the suggestion into a structured plan. It would reject unknown checks, missing column roles, and conflicting settings. A person could edit or reject the plan before APPFL sends the same approved configuration to every client. For an existing APPFL check, the adapter could fill in the data-readiness configuration. If AIDRIN suggests a check APPFL lacks, I would treat it as a proposed metric or CADRE module for human review and testing. Generated Python should never be sent to hospitals to run automatically.

Each client would calculate the approved checks on its own data. AIDRIN might run some metrics there too. The server report would say which checks ran, which sites failed, and which tool produced each result. It would not assume that similarly named AIDRIN and APPFL metrics use the same formula. Any summaries sent away from a client would need a separate privacy review.

## How I would test the idea

I would compare the assistant's suggested plans with plans chosen by a person for several synthetic datasets. The tests should include different outcome-column names, an unclear outcome column, unsupported suggestions, and a client that fails while running a check. I would also verify that no check runs before approval and that the planning request and server report contain no patient rows. After the serial version works, I would try a local networked APPFL run.

A useful first result would show that AIDRIN can suggest reasonable checks, a person can correct the plan, and APPFL can run the approved version without someone hand-editing each client's configuration. That still would not make the system ready for real hospital data.

## Where I need feedback

I would like to ask the AIDRIN team what parts of their skill can work from a limited dataset description, and how they think custom metric suggestions should be reviewed. From the APPFL team, I would like to know where the planning and approval step belongs and what a good first contribution would be. I am keeping these experiments in this separate repo while the subgroup-calibration PR is reviewed.
