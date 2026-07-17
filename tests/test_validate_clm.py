from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import UTC, date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_clm.py"
SPEC = importlib.util.spec_from_file_location("validate_clm", MODULE_PATH)
validation = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


class CLMValidationTests(unittest.TestCase):
    def test_json_schema_and_link_checks_cover_repository_sources(self) -> None:
        self.assertRegex(validation.check_json_and_schemas(), r"\d+ JSON files")
        self.assertRegex(validation.check_local_links(), r"\d+ Markdown files")

    def test_broken_local_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[Missing](docs/nope.md)", encoding="utf-8")
            with self.assertRaisesRegex(validation.ValidationError, "Broken local Markdown links"):
                validation.check_local_links(root)

    def test_secret_and_live_environment_values_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "unsafe.json").write_text(
                '{"client' + 'Secret":"not-safe","url":"https://tenant' + '.ent.box.com/folder/1"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(validation.ValidationError, "Secrets or environment-bound values"):
                validation.check_secrets_and_runtime_ids(root)

    def test_manifest_and_screenshot_contract_is_current(self) -> None:
        detail = validation.check_manifests_and_screenshots(ROOT, today=date(2026, 7, 17))
        self.assertIn("12 current real screenshots", detail)

    def test_reset_and_idempotency_contract_is_present(self) -> None:
        self.assertIn("portable retry", validation.check_reset_and_idempotency_contract())

    def test_repository_mode_skips_live_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(validation.check_live_receipts(Path(directory), required=False).startswith("SKIP:"))
            with self.assertRaisesRegex(validation.ValidationError, "Presenter-ready validation requires"):
                validation.check_live_receipts(Path(directory), required=True)

    def test_presenter_ready_receipts_require_all_current_platforms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "config" / "runtime"
            runtime.mkdir(parents=True)
            receipts = {
                "freshnessDays": 30,
                "receipts": [
                    {
                        "platform": platform,
                        "environment": "current-demo",
                        "validatedAt": datetime.now(UTC).isoformat(),
                        "actionMode": "live-smoke-test",
                        "businessKey": "CLM-2026-0017",
                        "status": "passed",
                        "evidence": "external-run-log-17",
                        "cleanupOwner": "demo-operator",
                    }
                    for platform in ("Box", "Salesforce", "AgentCore", "Databricks")
                ],
            }
            (runtime / "validation-receipts.json").write_text(json.dumps(receipts), encoding="utf-8")
            self.assertIn("Box, Salesforce", validation.check_live_receipts(root, required=True))

    def test_execute_records_failure_without_stopping_matrix(self) -> None:
        result = validation.execute("expected", lambda: (_ for _ in ()).throw(validation.ValidationError("boom")))
        self.assertEqual("FAIL", result.status)
        self.assertEqual("boom", result.detail)


if __name__ == "__main__":
    unittest.main()
