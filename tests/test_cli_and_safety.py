from __future__ import annotations

import ast
import io
import pathlib
import unittest

from react_agent.cli import main


class CliTests(unittest.TestCase):
    def test_completed_cli_run_renders_answer_and_numbered_trace(self) -> None:
        output = io.StringIO()
        errors = io.StringIO()

        exit_code = main(
            ["calculate 2 + 3", "--max-steps", "5"],
            stdout=output,
            stderr=errors,
        )

        rendered = output.getvalue()
        self.assertEqual(0, exit_code)
        self.assertEqual("", errors.getvalue())
        self.assertIn("status: completed", rendered)
        self.assertIn("answer: 5", rendered)
        self.assertIn("1. thought:", rendered)
        self.assertIn("5. final:", rendered)

    def test_failure_cli_run_is_nonzero_and_auditable(self) -> None:
        output = io.StringIO()

        exit_code = main(
            ["calculate 2 + 3", "--max-steps", "1"],
            stdout=output,
        )

        self.assertEqual(2, exit_code)
        self.assertIn("status: max_steps", output.getvalue())
        self.assertIn("maximum steps reached", output.getvalue())


class SafetyTests(unittest.TestCase):
    def test_package_has_no_forbidden_execution_or_network_paths(self) -> None:
        package = pathlib.Path(__file__).parents[1] / "react_agent"
        forbidden_calls = {"e" + "val", "e" + "xec", "__" + "import__"}
        forbidden_imports = {
            "sub" + "process",
            "socket",
            "urllib",
            "http",
            "ftplib",
        }

        for source_path in package.glob("*.py"):
            tree = ast.parse(source_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_names = (
                        [alias.name for alias in node.names]
                        if isinstance(node, ast.Import)
                        else [node.module or ""]
                    )
                    for module_name in module_names:
                        self.assertNotIn(
                            module_name.split(".")[0],
                            forbidden_imports,
                            source_path,
                        )
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_calls, source_path)
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                ):
                    self.assertNotEqual("system", node.func.attr, source_path)


if __name__ == "__main__":
    unittest.main()
