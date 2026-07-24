"""Command-line adapter for the deterministic ReAct Agent."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, TextIO

from .agent import run
from .models import AgentResult, TerminalStatus


def build_parser() -> argparse.ArgumentParser:
    """Create the documented command-line parser."""

    parser = argparse.ArgumentParser(
        prog="python -m react_agent",
        description="Run the deterministic local ReAct Agent.",
    )
    parser.add_argument("question", help="A documented arithmetic or lookup question")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="positive maximum number of policy decisions (default: 5)",
    )
    return parser


def render(result: AgentResult, stream: TextIO) -> None:
    """Render a stable status, answer, and numbered trace."""

    print(f"status: {result.status.value}", file=stream)
    print(f"answer: {result.answer or '-'}", file=stream)
    print("trace:", file=stream)
    for step in result.trace:
        details = [step.summary]
        if step.tool is not None:
            details.append(f"tool={step.tool}")
        if step.observation is not None:
            details.append(f"observation={step.observation}")
        if step.error is not None:
            details.append(f"error={step.error}")
        print(
            f"{step.sequence}. {step.phase.value}: {'; '.join(details)}",
            file=stream,
        )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the CLI and return zero only for completed answers."""

    output = stdout if stdout is not None else sys.stdout
    errors = stderr if stderr is not None else sys.stderr
    parser = build_parser()
    try:
        arguments = parser.parse_args(argv)
    except SystemExit as error:
        if stderr is not None:
            print("invalid command-line arguments", file=errors)
        return int(error.code)

    result = run(arguments.question, max_steps=arguments.max_steps)
    render(result, output)
    return 0 if result.status is TerminalStatus.COMPLETED else 2
