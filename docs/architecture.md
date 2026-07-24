---
kind: architecture
id: architecture
requirements_digest: sha256:0d12352103775f1ef1c2cd6d7aef6942d4e9ece2e99e89624352e33360cdab35
---
# Architecture

## System Context

The system is a local Python application used by a caller through either a typed Python API or a command-line adapter. A caller supplies a natural-language question and a positive maximum-step limit. The application runs a deterministic ReAct loop against two in-process, allow-listed tools and returns a final answer plus an ordered, serializable trace. Its boundary excludes language-model services, network I/O, shell processes, arbitrary Python evaluation, persistence, and user-home configuration.

## Components and Boundaries

- CMP-001: `models` owns immutable typed values for actions, observations, trace steps, terminal status, and the complete agent result; it performs no I/O.
- CMP-002: `tools` owns the tool protocol, tool-specific argument validation, the arithmetic implementation, the fixed knowledge table, and a registry containing only explicitly constructed local tools.
- CMP-003: `policy` deterministically maps the current question and observations to the next thought, tool call, or final answer; it cannot access the filesystem, network, process APIs, or tool internals.
- CMP-004: `agent` owns the bounded ReAct state machine, dispatches only through the injected registry, appends every transition to the trace, and converts failures into explicit terminal results.
- CMP-005: `cli` parses command-line input, invokes the public agent API, renders the answer and ordered trace, and maps terminal status to an exit code without embedding domain logic.

## Interfaces

- API-001: `run(question: str, *, max_steps: int = 5, tools: ToolRegistry | None = None, policy: Policy | None = None) -> AgentResult` validates non-empty input and a positive bound, executes at most `max_steps` decisions, and returns an `AgentResult`; expected tool and limit failures are represented in the result rather than raised across the boundary.
- API-002: `Tool.run(arguments: Mapping[str, object]) -> str` validates its own arguments and returns a short observation; invalid arguments raise a dedicated tool-input error and operational failures raise a dedicated tool-execution error for the agent boundary to capture.
- API-003: `Policy.next_action(question: str, trace: Sequence[TraceStep]) -> Decision` returns exactly one typed tool call or final-answer decision and receives no capability beyond the supplied values.
- API-004: `python -m react_agent QUESTION [--max-steps N]` prints a terminal status, answer, and numbered trace; valid completed runs exit zero and explicit failure outcomes exit nonzero.

## Data and State

- DATA-001: `AgentResult` owns the terminal status, answer text, and immutable ordered trace for one invocation; its lifetime ends with the caller unless explicitly serialized.
- DATA-002: Each trace step records its one-based sequence number, phase, summary, optional tool name, and optional observation/error without secrets or environment data.
- DATA-003: The arithmetic operation table and knowledge table are module constants. Callers may inject a test-only registry or policy instance, but no mutable global run state is retained between invocations.
- DATA-004: The loop counter is local to one run, increases once per decision, and enforces termination at the configured maximum.

## Security

- The tool registry is an explicit allow-list and never resolves names as imports, attributes, executable paths, or shell commands.
- Arithmetic dispatch uses an operation-to-function mapping and finite-number validation; no input is passed to `eval`, `exec`, a shell, or a subprocess.
- Knowledge lookup reads only an immutable built-in mapping and never falls back to files, environment variables, user-home paths, or network access.
- Tool exceptions are reduced to bounded error observations; raw stack traces and host details are not exposed through normal results.
- The CLI treats questions and tool arguments as data and performs no command interpolation.

## Validation Strategy

- Unit tests cover typed result/trace invariants, successful arithmetic, successful knowledge lookup, unknown tool, invalid arguments, injected tool failure, and exact maximum-step termination.
- CLI tests invoke the entry function with controlled argument/output streams, and one subprocess-free manual smoke command validates the documented module entry point.
- A repository scan rejects implementation call paths containing `eval`, `exec`, `subprocess`, `os.system`, or shell execution.
- Tests use only standard-library facilities and injected in-memory fakes, with no network or user-home dependency.

## Parallelization Boundaries

- Work on documentation and test cases can proceed independently after the public API and trace schema are fixed.
- Tool implementations can be developed independently from the ReAct loop when changes remain within API-002.
- The `models`, `agent`, and `policy` interface files form a shared contract and must not receive concurrent conflicting edits.
- Only one actor should modify package wiring, CLI exports, and the Task-owned integration files at a time; `.chassis`, accepted artifacts, and Git lifecycle state are never direct-write areas.

## Decisions Required from Master

- None
