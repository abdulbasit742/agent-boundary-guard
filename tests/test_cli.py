from __future__ import annotations

import io
import json
from pathlib import Path
from contextlib import redirect_stdout
import unittest

from agent_boundary_guard.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_json_output_and_nonzero_exit_for_risky_repo(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["scan", str(FIXTURES / "risky_repo"), "--format", "json", "--fail-on", "high"])
        payload = json.loads(buffer.getvalue())
        self.assertEqual(1, exit_code)
        self.assertEqual(6, payload["finding_count"])
        self.assertEqual(5, payload["summary"]["high"])
        self.assertEqual(1, payload["summary"]["medium"])

    def test_text_output_and_zero_exit_for_safe_repo(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["scan", str(FIXTURES / "safe_repo"), "--format", "text", "--fail-on", "high"])
        output = buffer.getvalue()
        self.assertEqual(0, exit_code)
        self.assertIn("Agent Boundary Guard: 0 finding(s)", output)
        self.assertIn("Summary: critical=0 high=0 medium=0 low=0", output)


if __name__ == "__main__":
    unittest.main()
