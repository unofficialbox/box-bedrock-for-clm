import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "apps.py"
SPEC = importlib.util.spec_from_file_location("box_capture_apps", MODULE_PATH)
provisioner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(provisioner)


class ExperimentalBoxAppsPrivateApiTests(unittest.TestCase):
    def valid_spec(self):
        return {
            "schemaVersion": 1,
            "name": "CLM Surface API Lab - Apps Workspace",
            "description": "Unsupported experiment",
            "initialPageName": "Lab Overview",
            "pages": [
                {
                    "name": "Lab Overview",
                    "sections": [
                        {
                            "title": "Overview",
                            "position": 0,
                            "size": 1,
                            "layout": {},
                        }
                    ],
                }
            ],
            "provisioning": {
                "mode": "experimental-private-rest",
                "existingAppPolicy": "reconcile-exact-title",
                "delete": False,
                "publish": False,
                "share": False,
            },
        }

    def test_repository_definition_is_valid(self):
        provisioner.validate_spec(provisioner.load_json(provisioner.DEFAULT_SPEC))

    def test_rejects_production_title(self):
        spec = self.valid_spec()
        spec["name"] = "Contract Lifecycle Management"
        with self.assertRaisesRegex(provisioner.ExperimentalAppsProvisionerError, "must begin"):
            provisioner.validate_spec(spec)

    def test_rejects_publish_and_delete(self):
        for key in ("publish", "delete", "share"):
            spec = self.valid_spec()
            spec["provisioning"][key] = True
            with self.assertRaisesRegex(provisioner.ExperimentalAppsProvisionerError, key):
                provisioner.validate_spec(spec)

    def test_rejects_unsupported_section_items(self):
        spec = self.valid_spec()
        spec["pages"][0]["sections"][0]["items"] = ["unsupported"]
        with self.assertRaises(provisioner.ExperimentalAppsProvisionerError):
            provisioner.validate_spec(spec)

    def test_executor_is_exact_title_and_non_destructive(self):
        script = provisioner.executor_script(self.valid_spec(), "example.box.com")
        self.assertEqual(len(script.splitlines()), 1)
        self.assertIn('call("app.list", [])', script)
        self.assertIn('call("app.create"', script)
        self.assertIn('call("app.update.all"', script)
        self.assertIn('call("app.lock"', script)
        self.assertIn('call("app.cancelEdit"', script)
        self.assertNotIn('call("app.delete"', script)
        self.assertNotIn('app.publish', script)
        self.assertNotIn('app.share', script)

    def test_executor_reconciles_pages(self):
        script = provisioner.executor_script(self.valid_spec(), "example.box.com")
        self.assertIn('"pages":', script)
        self.assertIn('reconcilePages', script)
        self.assertIn('"name":"Lab Overview"', script)
        self.assertIn('"title":"Overview"', script)

    def test_write_requires_exact_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            config_path = root / "config.json"
            output_path = root / "executor.js"
            spec_path.write_text(json.dumps(self.valid_spec()))
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com"}}))
            with self.assertRaisesRegex(provisioner.ExperimentalAppsProvisionerError, "Refusing"):
                provisioner.write_executor(spec_path, config_path, output_path, "")
            self.assertFalse(output_path.exists())

    def test_executor_contains_no_credentials_or_live_ids(self):
        script = provisioner.executor_script(self.valid_spec(), "example.box.com")
        self.assertNotIn("cookie", script.lower())
        self.assertNotIn("authorization", script.lower())
        self.assertNotIn("enterpriseId", script)


if __name__ == "__main__":
    unittest.main()
