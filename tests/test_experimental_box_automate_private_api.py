import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts/experimental_box_automate_private_api.py"
SPEC = importlib.util.spec_from_file_location("experimental_box_automate_private_api", MODULE_PATH)
provisioner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(provisioner)


class ExperimentalBoxAutomatePrivateApiTests(unittest.TestCase):
    def valid_spec(self):
        return {
            "schemaVersion": 1,
            "name": "CLM Surface API Lab - Automate Workflow",
            "description": "Unsupported experiment",
            "provisioning": {
                "mode": "experimental-private-graphql",
                "existingWorkflowPolicy": "reconcile-exact-title-empty-draft-only",
                "delete": False,
                "publish": False,
                "activate": False,
                "share": False,
                "run": False,
            },
        }

    def manual_start_spec(self):
        spec = self.valid_spec()
        spec["name"] = "CLM Surface API Lab - Automate Manual Start Graph"
        spec["graph"] = {
            "trigger": {
                "type": "manualStart",
                "scopeFolder": "workspace",
                "includeSubfolders": False,
                "description": "",
            }
        }
        spec["provisioning"]["existingWorkflowPolicy"] = (
            "reconcile-exact-title-manual-start-only"
        )
        return spec

    def test_repository_definition_is_valid(self):
        provisioner.validate_spec(provisioner.load_json(provisioner.DEFAULT_SPEC))

    def test_repository_manual_start_definition_is_valid(self):
        path = provisioner.ROOT / "config/box/private-api-lab-automate-manual-start-definition.json"
        provisioner.validate_spec(provisioner.load_json(path))

    def test_rejects_production_title(self):
        spec = self.valid_spec()
        spec["name"] = "CLM - Contract Intake Enrichment"
        with self.assertRaisesRegex(provisioner.ExperimentalAutomateProvisionerError, "must begin"):
            provisioner.validate_spec(spec)

    def test_rejects_consequential_behavior(self):
        for key in ("delete", "publish", "activate", "share", "run"):
            spec = self.valid_spec()
            spec["provisioning"][key] = True
            with self.assertRaisesRegex(provisioner.ExperimentalAutomateProvisionerError, key):
                provisioner.validate_spec(spec)

    def test_executor_uses_page_client_and_empty_draft_guard(self):
        script = provisioner.executor_script(self.valid_spec(), "example.box.com")
        self.assertEqual(len(script.splitlines()), 1)
        self.assertIn("window.__APOLLO_CLIENT__", script)
        self.assertIn("webpackChunkbox_workflow_client", script)
        self.assertIn("CreateItemV2", script)
        self.assertIn("UpdateItemV2", script)
        self.assertIn("Graph guard failed", script)
        self.assertIn('data.status !== "INACTIVE"', script)
        self.assertNotIn("PublishWorkflow", script)
        self.assertNotIn("ActivateWorkflow", script)
        self.assertNotIn("RunManualStartWorkflow", script)
        self.assertNotIn("DeleteItemV2", script)

    def test_manual_start_executor_uses_runtime_folder_and_deterministic_graph(self):
        script = provisioner.executor_script(
            self.manual_start_spec(),
            "example.box.com",
            {"box": {"folders": {"workspace": "123456789"}}},
        )
        self.assertIn('"triggerType":"MANUAL"', script)
        self.assertIn('"triggerSubtype":"START"', script)
        self.assertIn('"parentFolderId":"123456789"', script)
        self.assertIn('"includeSubfolders":"false"', script)
        self.assertIn("expected only a Manual Start trigger", script)
        self.assertNotIn("PublishWorkflow", script)
        self.assertNotIn("ActivateWorkflow", script)
        self.assertNotIn("RunManualStartWorkflow", script)
        self.assertNotIn("DeleteItemV2", script)

    def test_manual_start_requires_runtime_folder(self):
        with self.assertRaisesRegex(provisioner.ExperimentalAutomateProvisionerError, "bootstrap"):
            provisioner.executor_script(self.manual_start_spec(), "example.box.com")

    def test_write_requires_exact_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            config_path = root / "config.json"
            output_path = root / "executor.js"
            spec_path.write_text(json.dumps(self.valid_spec()))
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com"}}))
            with self.assertRaisesRegex(provisioner.ExperimentalAutomateProvisionerError, "Refusing"):
                provisioner.write_executor(spec_path, config_path, root / "bootstrap.json", output_path, "")
            self.assertFalse(output_path.exists())

    def test_inspector_is_read_only(self):
        script = provisioner.inspector_script("example.box.com")
        self.assertEqual(len(script.splitlines()), 1)
        for mutation in ("client.mutate", "CreateItemV2", "UpdateItemV2", "PublishWorkflow", "ActivateWorkflow", "DeleteItemV2"):
            self.assertNotIn(mutation, script)
        self.assertNotIn("client.query", script)
        self.assertIn("__reactContainer", script)
        self.assertIn("Publication guard failed", script)
        self.assertIn("mutated: false", script)
        self.assertIn("graphqlOperationsIssued: 0", script)

    def test_inspector_enforces_hostname_and_surface(self):
        script = provisioner.inspector_script("example.box.com")
        self.assertIn("Target guard failed", script)
        self.assertIn("Surface guard failed", script)
        self.assertIn('"example.box.com"', script)
        with self.assertRaisesRegex(provisioner.ExperimentalAutomateProvisionerError, "box.com"):
            provisioner.inspector_script("example.invalid.com")

    def test_inspector_title_guard_is_optional_but_exact(self):
        without = provisioner.inspector_script("example.box.com")
        self.assertIn("const expectedTitle = null", without)
        with_title = provisioner.inspector_script("example.box.com", "CLM - Contract Intake Enrichment")
        self.assertIn('const expectedTitle = "CLM - Contract Intake Enrichment"', with_title)
        self.assertIn("Title guard failed", with_title)

    def test_inspector_redacts_identifiers(self):
        script = provisioner.inspector_script("example.box.com")
        self.assertIn("<guid>", script)
        self.assertIn("<email>", script)
        self.assertIn("<id>", script)

    def test_inspector_derives_status_from_publication_timestamps(self):
        script = provisioner.inspector_script("example.box.com")
        self.assertIn('everPublished ? "PUBLISHED" : "DRAFT"', script)
        self.assertIn("statusSource", script)

    def test_inspector_does_not_contain_credentials(self):
        script = provisioner.inspector_script("example.box.com")
        self.assertNotIn("cookie", script.lower())
        self.assertNotIn("authorization", script.lower())
        self.assertNotIn("x-csrf-token", script.lower())

    def test_write_inspector_requires_exact_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            output_path = root / "inspector.js"
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com"}}))
            with self.assertRaisesRegex(provisioner.ExperimentalAutomateProvisionerError, "Refusing"):
                provisioner.write_inspector(config_path, output_path, "", None)
            self.assertFalse(output_path.exists())
            provisioner.write_inspector(config_path, output_path, provisioner.ACKNOWLEDGEMENT, None)
            self.assertTrue(output_path.exists())

    def test_executor_does_not_contain_credentials(self):
        script = provisioner.executor_script(self.valid_spec(), "example.box.com")
        self.assertNotIn("cookie", script.lower())
        self.assertNotIn("authorization", script.lower())
        self.assertNotIn("x-csrf-token", script.lower())


if __name__ == "__main__":
    unittest.main()
