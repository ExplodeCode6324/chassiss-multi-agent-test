"""Immutable public models for deterministic ReAct execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Union


class TerminalStatus(str, Enum):
    """Stable terminal outcomes returned by the agent boundary."""

    COMPLETED = "completed"
    UNSUPPORTED = "unsupported"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN_TOOL = "unknown_tool"
    INVALID_ARGUMENTS = "invalid_arguments"
    TOOL_FAILURE = "tool_failure"
    POLICY_FAILURE = "policy_failure"
    MAX_STEPS = "max_steps"


class TracePhase(str, Enum):
    """The auditable phases emitted by the ReAct state machine."""

    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    ERROR = "error"
    FINAL = "final"


@dataclass(frozen=True)
class TraceStep:
    """One ordered, host-independent trace entry."""

    sequence: int
    phase: TracePhase
    summary: str
    tool: str | None = None
    observation: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class AgentResult:
    """The complete result of one isolated agent run."""

    status: TerminalStatus
    answer: str
    trace: tuple[TraceStep, ...]


@dataclass(frozen=True)
class ToolCallDecision:
    """A policy decision to invoke one explicitly registered tool."""

    thought: str
    tool: str
    arguments: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "arguments",
            MappingProxyType(dict(self.arguments)),
        )


@dataclass(frozen=True)
class FinalAnswerDecision:
    """A policy decision to terminate with an answer."""

    thought: str
    answer: str
    status: TerminalStatus = TerminalStatus.COMPLETED


Decision = Union[ToolCallDecision, FinalAnswerDecision]
