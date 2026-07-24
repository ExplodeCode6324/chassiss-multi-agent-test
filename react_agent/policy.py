"""A deterministic policy for the documented question grammar."""

from __future__ import annotations

import re
from typing import Protocol, Sequence

from .models import (
    Decision,
    FinalAnswerDecision,
    TerminalStatus,
    ToolCallDecision,
    TracePhase,
    TraceStep,
)


class Policy(Protocol):
    """A policy receives values only and returns one typed decision."""

    def next_action(
        self,
        question: str,
        trace: Sequence[TraceStep],
    ) -> Decision:
        """Return one tool call or one final answer."""


_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
_ARITHMETIC = re.compile(
    rf"^\s*(?:calculate|what\s+is)\s+({_NUMBER})\s*([+\-*/])"
    rf"\s*({_NUMBER})\s*\??\s*$",
    re.IGNORECASE,
)
_LOOKUP = re.compile(
    r"^\s*(?:lookup|what\s+is)\s+([a-z][a-z0-9_-]*)\s*\??\s*$",
    re.IGNORECASE,
)
_OPERATION_NAMES = {
    "+": "add",
    "-": "subtract",
    "*": "multiply",
    "/": "divide",
}


class DeterministicPolicy:
    """Recognize a small grammar and finish from the latest observation."""

    def next_action(
        self,
        question: str,
        trace: Sequence[TraceStep],
    ) -> Decision:
        observation = self._latest_observation(trace)
        if observation is not None:
            return FinalAnswerDecision(
                thought="A successful tool observation is available.",
                answer=observation,
            )

        arithmetic = _ARITHMETIC.fullmatch(question)
        if arithmetic:
            left, symbol, right = arithmetic.groups()
            return ToolCallDecision(
                thought="The question matches the safe binary arithmetic grammar.",
                tool="arithmetic",
                arguments={
                    "operation": _OPERATION_NAMES[symbol],
                    "left": self._number(left),
                    "right": self._number(right),
                },
            )

        lookup = _LOOKUP.fullmatch(question)
        if lookup:
            return ToolCallDecision(
                thought="The question requests an exact built-in knowledge key.",
                tool="knowledge",
                arguments={"key": lookup.group(1).lower()},
            )

        return FinalAnswerDecision(
            thought="The question does not match the documented deterministic grammar.",
            answer=(
                "Unsupported question. Use 'calculate NUMBER OP NUMBER' "
                "or 'lookup KEY'."
            ),
            status=TerminalStatus.UNSUPPORTED,
        )

    @staticmethod
    def _number(text: str) -> int | float:
        return float(text) if "." in text else int(text)

    @staticmethod
    def _latest_observation(trace: Sequence[TraceStep]) -> str | None:
        for step in reversed(trace):
            if step.phase is TracePhase.OBSERVATION:
                return step.observation
        return None
