import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts/box_form_provisioner.py"
SPEC = importlib.util.spec_from_file_location("box_form_provisioner", MODULE_PATH)
provisioner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(provisioner)


class BoxFormProvisionerTests(unittest.TestCase):
    def valid_spec(self):
        return {
            "schemaVersion": 1,
            "name": "New Contract Request",
            "destinationFolderId": "${box.folders.intake}",
            "confirmationBehavior": "box-default",
            "provisioning": {
                "mode": "authenticated-browser-ui",
                "existingFormPolicy": "reconcile-exact-title",
                "saveForm": True,
                "publishLink": False,
                "share": False,
            },
            "fields": [
                {"key": "name", "label": "Name", "type": "shortText", "required": True},
                {"key": "region", "label": "Region", "type": "dropdown", "required": True, "options": ["US", "EU"]},
            ],
        }

    def test_repository_definition_is_valid(self):
        provisioner.validate_spec(provisioner.load_json(provisioner.DEFAULT_SPEC))

    def test_rejects_publish_or_share_enabled(self):
        spec = self.valid_spec()
        spec["provisioning"]["publishLink"] = True
        with self.assertRaisesRegex(provisioner.ProvisionerError, "provisioning.publishLink"):
            provisioner.validate_spec(spec)

    def test_rejects_duplicate_labels(self):
        spec = self.valid_spec()
        spec["fields"][1]["label"] = "Name"
        with self.assertRaisesRegex(provisioner.ProvisionerError, "duplicate field label"):
            provisioner.validate_spec(spec)

    def test_rejects_dropdown_without_options(self):
        spec = self.valid_spec()
        del spec["fields"][1]["options"]
        with self.assertRaisesRegex(provisioner.ProvisionerError, "at least two"):
            provisioner.validate_spec(spec)

    def test_builds_guarded_runtime_plan(self):
        plan = provisioner.browser_plan(
            self.valid_spec(),
            {"box": {"hostname": "example.box.com", "enterpriseId": "enterprise", "operatorLogin": "operator@example.com"}},
            {"box": {"folders": {"01 - Intake": "folder"}}},
        )
        self.assertEqual(plan["form"]["destinationFolderId"], "folder")
        self.assertEqual(plan["reconciliation"]["onMultipleMatches"], "stop-and-report-duplicates")
        self.assertIn("publish", plan["decisionGate"]["stopBefore"])
        self.assertFalse(plan["credentialHandling"]["callPrivateRestDirectly"])

    def test_prepare_writes_only_requested_runtime_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            config_path = root / "config.json"
            state_path = root / "state.json"
            output_path = root / "generated/plan.json"
            spec_path.write_text(json.dumps(self.valid_spec()))
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com", "enterpriseId": "enterprise", "operatorLogin": "operator@example.com"}}))
            state_path.write_text(json.dumps({"box": {"folders": {"01 - Intake": "folder"}}}))
            with redirect_stdout(io.StringIO()):
                provisioner.prepare(spec_path, config_path, state_path, output_path)
            plan = json.loads(output_path.read_text())
            self.assertEqual(plan["operation"], "reconcile-saved-form")
            self.assertEqual(plan["form"]["fields"][1]["builderType"], "Dropdown")

    def test_dry_run_does_not_require_runtime_files(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            provisioner.portable_dry_run(self.valid_spec())
        self.assertIn("destination remains runtime-bound", stdout.getvalue())

    def test_prepare_explicitly_says_no_box_changes_were_made(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            config_path = root / "config.json"
            state_path = root / "state.json"
            output_path = root / "generated/plan.json"
            spec_path.write_text(json.dumps(self.valid_spec()))
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com", "enterpriseId": "enterprise", "operatorLogin": "operator@example.com"}}))
            state_path.write_text(json.dumps({"box": {"folders": {"01 - Intake": "folder"}}}))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                provisioner.prepare(spec_path, config_path, state_path, output_path)
            self.assertIn("NO BOX CHANGES WERE MADE", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
