from __future__ import annotations

import unittest
from typing import Mapping, Sequence

from react_agent import (
    TerminalStatus,
    ToolCallDecision,
    ToolExecutionError,
    ToolRegistry,
    TracePhase,
    TraceStep,
    run,
)


class FixedDecisionPolicy:
    def __init__(self, decision: ToolCallDecision) -> None:
        self.decision = decision
        self.calls = 0

    def next_action(
        self,
        question: str,
        trace: Sequence[TraceStep],
    ) -> ToolCallDecision:
        self.calls += 1
        return self.decision


class BrokenTool:
    name = "broken"

    def run(self, arguments: Mapping[str, object]) -> str:
        raise ToolExecutionError("internal detail must not escape")


class UnexpectedlyBrokenTool:
    name = "unexpected"

    def run(self, arguments: Mapping[str, object]) -> str:
        raise RuntimeError("host detail must not escape")


class AgentTests(unittest.TestCase):
    def test_arithmetic_success_has_ordered_complete_trace(self) -> None:
        result = run("calculate 2 + 3")

        self.assertEqual(TerminalStatus.COMPLETED, result.status)
        self.assertEqual("5", result.answer)
        self.assertEqual(
            [
                TracePhase.THOUGHT,
                TracePhase.ACTION,
                TracePhase.OBSERVATION,
                TracePhase.THOUGHT,
                TracePhase.FINAL,
            ],
            [step.phase for step in result.trace],
        )
        self.assertEqual(
            list(range(1, len(result.trace) + 1)),
            [step.sequence for step in result.trace],
        )

    def test_arithmetic_supports_each_allowlisted_operation(self) -> None:
        cases = {
            "calculate 7 - 2": "5",
            "calculate 3 * 4": "12",
            "calculate 8 / 4": "2",
            "what is -1.5 + 2?": "0.5",
        }
        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertEqual(expected, run(question).answer)

    def test_knowledge_success_uses_exact_documented_key(self) -> None:
        result = run("lookup react")

        self.assertEqual(TerminalStatus.COMPLETED, result.status)
        self.assertEqual(
            "ReAct interleaves reasoning, actions, and observations.",
            result.answer,
        )

    def test_unknown_tool_is_explicit(self) -> None:
        policy = FixedDecisionPolicy(
            ToolCallDecision("Try an unavailable capability.", "missing", {})
        )

        result = run("test", policy=policy)

        self.assertEqual(TerminalStatus.UNKNOWN_TOOL, result.status)
        self.assertEqual(TracePhase.ERROR, result.trace[-1].phase)
        self.assertIn("unknown tool", result.trace[-1].error or "")

    def test_invalid_tool_arguments_are_explicit(self) -> None:
        policy = FixedDecisionPolicy(
            ToolCallDecision(
                "Send invalid typed operands.",
                "arithmetic",
                {"operation": "add", "left": "2", "right": 3},
            )
        )

        result = run("test", policy=policy)

        self.assertEqual(TerminalStatus.INVALID_ARGUMENTS, result.status)
        self.assertEqual("left must be a finite number", result.trace[-1].error)

    def test_division_by_zero_is_an_invalid_argument(self) -> None:
        result = run("calculate 1 / 0")

        self.assertEqual(TerminalStatus.INVALID_ARGUMENTS, result.status)
        self.assertEqual(
            "division by zero is not allowed",
            result.trace[-1].error,
        )

    def test_declared_tool_failure_is_bounded_and_redacted(self) -> None:
        policy = FixedDecisionPolicy(
            ToolCallDecision("Exercise a failing tool.", "broken", {})
        )

        result = run(
            "test",
            policy=policy,
            tools=ToolRegistry((BrokenTool(),)),
        )

        self.assertEqual(TerminalStatus.TOOL_FAILURE, result.status)
        self.assertEqual("tool execution failed", result.trace[-1].error)
        self.assertNotIn("internal detail", str(result.trace))

    def test_unexpected_tool_failure_is_bounded_and_redacted(self) -> None:
        policy = FixedDecisionPolicy(
            ToolCallDecision("Exercise a failing tool.", "unexpected", {})
        )

        result = run(
            "test",
            policy=policy,
            tools=ToolRegistry((UnexpectedlyBrokenTool(),)),
        )

        self.assertEqual(TerminalStatus.TOOL_FAILURE, result.status)
        self.assertEqual("tool execution failed", result.trace[-1].error)
        self.assertNotIn("host detail", str(result.trace))

    def test_maximum_step_count_is_exact(self) -> None:
        policy = FixedDecisionPolicy(
            ToolCallDecision(
                "Repeat a safe action.",
                "arithmetic",
                {"operation": "add", "left": 1, "right": 1},
            )
        )

        result = run("test", max_steps=3, policy=policy)

        self.assertEqual(TerminalStatus.MAX_STEPS, result.status)
        self.assertEqual(3, policy.calls)
        self.assertEqual(
            3,
            sum(step.phase is TracePhase.ACTION for step in result.trace),
        )
        self.assertEqual(TracePhase.FINAL, result.trace[-1].phase)

    def test_one_step_default_run_exhausts_after_one_decision(self) -> None:
        result = run("calculate 2 + 3", max_steps=1)

        self.assertEqual(TerminalStatus.MAX_STEPS, result.status)
        self.assertEqual(
            1,
            sum(step.phase is TracePhase.ACTION for step in result.trace),
        )

    def test_unsupported_question_is_clear_and_bounded(self) -> None:
        result = run("tell me a story")

        self.assertEqual(TerminalStatus.UNSUPPORTED, result.status)
        self.assertIn("Unsupported question", result.answer)
        self.assertEqual(2, len(result.trace))

    def test_invalid_public_inputs_return_results(self) -> None:
        for question, max_steps in (("", 5), ("ok", 0), ("ok", -1)):
            with self.subTest(question=question, max_steps=max_steps):
                result = run(question, max_steps=max_steps)
                self.assertEqual(TerminalStatus.INVALID_REQUEST, result.status)
                self.assertEqual(1, len(result.trace))


if __name__ == "__main__":
    unittest.main()
