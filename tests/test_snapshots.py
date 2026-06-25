from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from claude_agent_harness_optimization.snapshots import build_surface_snapshot


ROOT = Path(__file__).resolve().parents[1]


class SnapshotTests(unittest.TestCase):
    def test_surface_snapshot_captures_matrix_and_skill(self):
        snapshot = build_surface_snapshot(
            matrices=[ROOT / "evals" / "model_matrix" / "harness_trace_adapters.json"],
            skills=[ROOT / ".claude" / "skills" / "agent-audit" / "SKILL.md"],
        )
        self.assertEqual("1", snapshot["snapshot_version"])
        self.assertEqual(2, len(snapshot["items"]))
        matrix = snapshot["items"][0]
        self.assertEqual("model_matrix", matrix["type"])
        self.assertTrue(matrix["tool_variants"][0]["tools"][0]["surface_hash"])
        skill = snapshot["items"][1]
        self.assertEqual("skill", skill["type"])
        self.assertTrue(skill["hash"])

    def test_cli_snapshot_surface(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "snapshot.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "claude_agent_harness_optimization",
                    "snapshot-surface",
                    "--matrix",
                    "evals/model_matrix/harness_trace_adapters.json",
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
