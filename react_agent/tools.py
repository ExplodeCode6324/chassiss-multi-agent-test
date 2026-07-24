"""Explicit, in-process tools for arithmetic and fixed knowledge lookup."""

from __future__ import annotations

import math
import operator
from numbers import Real
from types import MappingProxyType
from typing import Iterable, Mapping, Protocol


class ToolInputError(ValueError):
    """Raised when tool arguments fail the tool's public contract."""


class ToolExecutionError(RuntimeError):
    """Raised when a valid tool request cannot be completed."""


class Tool(Protocol):
    """The minimal capability exposed to the agent dispatcher."""

    name: str

    def run(self, arguments: Mapping[str, object]) -> str:
        """Validate arguments and return a short observation."""


class ArithmeticTool:
    """Safe binary arithmetic with an explicit operation allow-list."""

    name = "arithmetic"
    _operations = MappingProxyType(
        {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": operator.truediv,
        }
    )

    def run(self, arguments: Mapping[str, object]) -> str:
        expected = {"operation", "left", "right"}
        if set(arguments) != expected:
            raise ToolInputError(
                "arithmetic requires exactly operation, left, and right"
            )

        operation_name = arguments["operation"]
        if not isinstance(operation_name, str) or operation_name not in self._operations:
            raise ToolInputError("arithmetic operation is not allowed")

        left = self._validated_number(arguments["left"], "left")
        right = self._validated_number(arguments["right"], "right")
        if operation_name == "divide" and right == 0:
            raise ToolInputError("division by zero is not allowed")

        result = self._operations[operation_name](left, right)
        if not math.isfinite(float(result)):
            raise ToolInputError("arithmetic result must be finite")
        return self._format_number(result)

    @staticmethod
    def _validated_number(value: object, label: str) -> Real:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ToolInputError(f"{label} must be a finite number")
        if not math.isfinite(float(value)):
            raise ToolInputError(f"{label} must be a finite number")
        return value

    @staticmethod
    def _format_number(value: Real) -> str:
        if float(value).is_integer():
            return str(int(value))
        return format(float(value), ".15g")


DEFAULT_KNOWLEDGE = MappingProxyType(
    {
        "react": "ReAct interleaves reasoning, actions, and observations.",
        "python": "Python is a general-purpose programming language.",
        "chassiss": "CHASSISS coordinates role-scoped project workflows.",
    }
)


class KnowledgeTool:
    """Exact-key lookup over a fixed, immutable table."""

    name = "knowledge"

    def __init__(self, entries: Mapping[str, str] | None = None) -> None:
        self._entries = MappingProxyType(dict(entries or DEFAULT_KNOWLEDGE))

    def run(self, arguments: Mapping[str, object]) -> str:
        if set(arguments) != {"key"}:
            raise ToolInputError("knowledge requires exactly key")
        key = arguments["key"]
        if not isinstance(key, str) or not key:
            raise ToolInputError("knowledge key must be a non-empty string")
        if key not in self._entries:
            raise ToolInputError("knowledge key was not found")
        return self._entries[key]


class ToolRegistry:
    """An explicit name-to-tool allow-list with no dynamic resolution."""

    def __init__(self, tools: Iterable[Tool]) -> None:
        registered: dict[str, Tool] = {}
        for tool in tools:
            if not tool.name or tool.name in registered:
                raise ValueError("tool names must be non-empty and unique")
            registered[tool.name] = tool
        self._tools = MappingProxyType(registered)

    @classmethod
    def default(cls) -> ToolRegistry:
        """Build an isolated default registry for one run."""

        return cls((ArithmeticTool(), KnowledgeTool()))

    def get(self, name: str) -> Tool | None:
        """Return only a tool that was explicitly registered."""

        return self._tools.get(name)

    @property
    def names(self) -> tuple[str, ...]:
        """Expose registered names for diagnostics without tool internals."""

        return tuple(self._tools)
