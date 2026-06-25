from pathlib import Path
import json
import tempfile
import unittest

from claude_agent_harness_optimization.e2e import run_e2e_spec


class E2ETests(unittest.TestCase):
    def test_run_e2e_spec_with_fake_http(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            env_path = Path(tmp) / ".env"
            spec_path.write_text(
                json.dumps(
                    {
                        "name": "fake service",
                        "env": {"required": ["FAKE_TOKEN"]},
                        "checks": [
                            {
                                "expect_json_path": "result.id",
                                "expect_status": 200,
                                "headers": {"Authorization": "Bearer ${FAKE_TOKEN}"},
                                "name": "read fake object",
                                "read_only": True,
                                "type": "http_json",
                                "url": "https://example.test/object",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            env_path.write_text("FAKE_TOKEN=secret\n", encoding="utf-8")

            def fake_request(method, url, headers, body, timeout):
                self.assertEqual("GET", method)
                self.assertEqual("Bearer secret", headers["Authorization"])
                return 200, {"result": {"id": "obj_1"}}

            result = run_e2e_spec(spec_path, env_file=env_path, request_fn=fake_request)
            self.assertTrue(result["passed"])
            self.assertEqual("passed", result["checks"][0]["status"])

    def test_missing_env_fails_outside_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "name": "missing env",
                        "env": {"required": ["MISSING_TOKEN"]},
                        "checks": [],
                    }
                ),
                encoding="utf-8",
            )
            result = run_e2e_spec(spec_path)
            self.assertFalse(result["passed"])
            self.assertEqual(["MISSING_TOKEN"], result["missing_env"])

    def test_dry_run_validates_without_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "name": "dry run",
                        "env": {"required": ["MISSING_TOKEN"]},
                        "checks": [
                            {
                                "name": "planned",
                                "type": "http_json",
                                "url": "https://example.test",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run_e2e_spec(spec_path, dry_run=True)
            self.assertTrue(result["passed"])
            self.assertEqual("planned", result["checks"][0]["status"])


if __name__ == "__main__":
    unittest.main()
