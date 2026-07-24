# Deterministic Python ReAct Agent

This repository contains a small, standard-library-only ReAct Agent. It accepts
a documented natural-language question, makes a bounded sequence of deterministic
policy decisions, dispatches only explicitly registered local tools, and returns
a terminal status, answer, and immutable ordered trace.

The component boundaries are:

- `react_agent.models`: immutable decisions, trace steps, terminal statuses, and
  results.
- `react_agent.tools`: safe binary arithmetic, fixed-table knowledge lookup, and
  the explicit in-process registry.
- `react_agent.policy`: the deterministic question grammar and next-action policy.
- `react_agent.agent`: bounded orchestration and failure-to-result conversion.
- `react_agent.cli`: argument parsing, trace rendering, and exit semantics.

No external package, hosted model, network client, shell command, subprocess, or
arbitrary Python evaluation is used.

## Supported questions

Arithmetic accepts one binary expression with a numeric operand on each side:

```text
calculate 2 + 3
what is -1.5 * 2?
```

The allowed symbols are `+`, `-`, `*`, and `/`.

Knowledge lookup accepts an exact built-in key:

```text
lookup react
lookup python
lookup chassiss
```

Unsupported wording returns the explicit `unsupported` status. The knowledge
table never falls back to files, environment variables, the user home directory,
or a network service.

## Python API

```python
from react_agent import run

result = run("calculate 2 + 3", max_steps=5)
print(result.status.value)  # completed
print(result.answer)        # 5
for step in result.trace:
    print(step.sequence, step.phase.value, step.summary)
```

Tests can inject a `ToolRegistry` or a policy implementing `Policy.next_action`
to reach deterministic failure paths.

## Command line

```bash
python3 -m react_agent "calculate 2 + 3" --max-steps 5
python3 -m react_agent "lookup react"
```

A completed answer exits with status code `0`. Explicit failure outcomes
(`invalid_request`, `unknown_tool`, `invalid_arguments`, `tool_failure`,
`policy_failure`, `max_steps`, and `unsupported`) exit with status code `2`.
Every outcome prints its status, answer (or `-`), and numbered trace.

## Verification

Run the complete deterministic unit-test suite:

```bash
python3 -m unittest discover -s tests -v
```

Run the frozen command-line smoke test:

```bash
python3 -m react_agent "calculate 2 + 3" --max-steps 5
```

The tests include an abstract-syntax-tree safety scan of the implementation and
exercise arithmetic success, knowledge success, ordered traces, unknown tools,
invalid arguments, declared and unexpected tool failures, exact maximum-step
exhaustion, unsupported inputs, and CLI rendering/exit behavior.

## CHASSISS collaboration

The accepted Requirements, Architecture, Mission, and Task are managed through
the CHASSISS CLI. Development, review, integration, and publication follow the
role-scoped CLI lifecycle. `rawdata/` contains the ordered multi-agent
interoperability record.
