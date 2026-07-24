"""Bounded ReAct orchestration with explicit terminal outcomes."""

from __future__ import annotations

from typing import Sequence

from .models import (
    AgentResult,
    FinalAnswerDecision,
    TerminalStatus,
    ToolCallDecision,
    TracePhase,
    TraceStep,
)
from .policy import DeterministicPolicy, Policy
from .tools import ToolExecutionError, ToolInputError, ToolRegistry


def run(
    question: str,
    *,
    max_steps: int = 5,
    tools: ToolRegistry | None = None,
    policy: Policy | None = None,
) -> AgentResult:
    """Run an isolated deterministic agent and always return a typed result."""

    if not isinstance(question, str) or not question.strip():
        return _invalid_request("question must be a non-empty string")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
        return _invalid_request("max_steps must be a positive integer")

    registry = tools if tools is not None else ToolRegistry.default()
    active_policy = policy if policy is not None else DeterministicPolicy()
    trace: list[TraceStep] = []

    for _ in range(max_steps):
        try:
            decision = active_policy.next_action(question, tuple(trace))
        except Exception:
            _append(
                trace,
                TracePhase.ERROR,
                "The policy failed safely.",
                error="policy execution failed",
            )
            return _result(TerminalStatus.POLICY_FAILURE, "", trace)

        if isinstance(decision, FinalAnswerDecision):
            _append(trace, TracePhase.THOUGHT, decision.thought)
            _append(
                trace,
                TracePhase.FINAL,
                "The policy produced a terminal answer.",
                observation=decision.answer,
            )
            return _result(decision.status, decision.answer, trace)

        if not isinstance(decision, ToolCallDecision):
            _append(
                trace,
                TracePhase.ERROR,
                "The policy returned an invalid decision.",
                error="invalid policy decision",
            )
            return _result(TerminalStatus.POLICY_FAILURE, "", trace)

        _append(trace, TracePhase.THOUGHT, decision.thought)
        _append(
            trace,
            TracePhase.ACTION,
            "Dispatch an explicitly registered tool.",
            tool=decision.tool,
        )
        selected_tool = registry.get(decision.tool)
        if selected_tool is None:
            _append(
                trace,
                TracePhase.ERROR,
                "Tool dispatch was rejected.",
                tool=decision.tool,
                error=f"unknown tool: {decision.tool}",
            )
            return _result(TerminalStatus.UNKNOWN_TOOL, "", trace)

        try:
            observation = selected_tool.run(decision.arguments)
        except ToolInputError as error:
            _append(
                trace,
                TracePhase.ERROR,
                "Tool argument validation failed.",
                tool=decision.tool,
                error=str(error),
            )
            return _result(TerminalStatus.INVALID_ARGUMENTS, "", trace)
        except ToolExecutionError:
            _append(
                trace,
                TracePhase.ERROR,
                "The tool failed safely.",
                tool=decision.tool,
                error="tool execution failed",
            )
            return _result(TerminalStatus.TOOL_FAILURE, "", trace)
        except Exception:
            _append(
                trace,
                TracePhase.ERROR,
                "The tool failed safely.",
                tool=decision.tool,
                error="tool execution failed",
            )
            return _result(TerminalStatus.TOOL_FAILURE, "", trace)

        _append(
            trace,
            TracePhase.OBSERVATION,
            "The tool returned an observation.",
            tool=decision.tool,
            observation=observation,
        )

    _append(
        trace,
        TracePhase.FINAL,
        "The maximum decision count was reached before a final answer.",
        error="maximum steps reached",
    )
    return _result(TerminalStatus.MAX_STEPS, "", trace)


def _append(
    trace: list[TraceStep],
    phase: TracePhase,
    summary: str,
    *,
    tool: str | None = None,
    observation: str | None = None,
    error: str | None = None,
) -> None:
    trace.append(
        TraceStep(
            sequence=len(trace) + 1,
            phase=phase,
            summary=summary,
            tool=tool,
            observation=observation,
            error=error,
        )
    )


def _invalid_request(message: str) -> AgentResult:
    return AgentResult(
        status=TerminalStatus.INVALID_REQUEST,
        answer="",
        trace=(
            TraceStep(
                sequence=1,
                phase=TracePhase.FINAL,
                summary="The request was rejected before execution.",
                error=message,
            ),
        ),
    )


def _result(
    status: TerminalStatus,
    answer: str,
    trace: Sequence[TraceStep],
) -> AgentResult:
    return AgentResult(status=status, answer=answer, trace=tuple(trace))
