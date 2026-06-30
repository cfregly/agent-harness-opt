from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_skill_surfaces import _check_agent_audit_skill, check_skill_surfaces


ROOT = Path(__file__).resolve().parents[1]


class CheckSkillSurfacesScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_skill_surfaces.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("skill surface check passed", result.stdout)

    def test_skill_check_rejects_incomplete_project_skill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dir = Path(temp_dir) / ".claude" / "skills"
            skill_dir = skills_dir / "agent-audit"
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: wrong-name
description: Too short.
---

# Agent Audit

TODO
""",
                encoding="utf-8",
            )
            (agents_dir / "openai.yaml").write_text(
                """interface:
  display_name:
  short_description:
  default_prompt:
""",
                encoding="utf-8",
            )

            failures = check_skill_surfaces(skills_dir)

        joined = "\n".join(failures)
        self.assertIn("frontmatter name must match skill directory", joined)
        self.assertIn("description is too thin", joined)
        self.assertIn("description must include trigger guidance", joined)
        self.assertIn("description missing", joined)
        self.assertIn("contains unresolved marker TODO", joined)
        self.assertIn("missing heading ## Decision Tree", joined)
        self.assertIn("decision tree must cover at least 10 routes", joined)
        self.assertIn("missing interface.display_name", joined)
        self.assertIn("missing value-bar routing language", joined)

    def test_agent_audit_skill_rejects_unknown_cli_commands(self):
        failures = _check_agent_audit_skill(
            Path(".claude/skills/agent-audit/SKILL.md"),
            """
## Decision Tree
1. Route.
2. Route.
3. Route.
4. Route.
5. Route.
6. Route.
7. Route.
8. Route.
9. Route.
10. Route.
## Commands
python -m claude_agent_harness_opt fake-command thing.json
## Review Method
## What To Look For
- Tools:
- Tool calls:
- Metrics:
- Selection cases:
- Model matrix:
- Skills:
- Harness grind:
- Tool outputs:
- Reasoning:
- Final answer:
- Value bar:
- Upstream PR packet:
## Reporting
Backing data:
Commands run:
Do not claim hidden reasoning exists
adversarially-confirmed to add value
""",
        )

        joined = "\n".join(failures)
        self.assertIn("unknown CLI command referenced: fake-command", joined)
        self.assertIn("missing required CLI command reference: audit-agent", joined)


if __name__ == "__main__":
    unittest.main()
