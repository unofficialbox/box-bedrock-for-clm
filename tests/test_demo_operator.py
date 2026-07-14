import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "scripts/demo_operator.py"
SPEC = importlib.util.spec_from_file_location("demo_operator", MODULE_PATH)
demo_operator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(demo_operator)


class DemoOperatorTests(unittest.TestCase):
    def write_config(self, directory: str, **overrides):
        config = {
            "box": {
                "parentFolderId": "123", "allowRootFolder": False, "enterpriseId": "456",
                "operatorLogin": "operator@example.com", "hostname": "example.box.com", "appUrl": "https://example.box.com/app/a",
                "formUrl": "https://example.box.com/f/f", "hubUrl": "https://example.box.com/hubs/h",
                "workflowUrl": "https://example.box.com/automate/workflow/edit/w", "reviewerLogins": ["reviewer@example.com"],
            },
            "salesforce": {
                "orgAlias": "demo", "orgId": "00D000000000001", "myDomainUrl": "https://example.my.salesforce.com",
                "integrationUsername": "integration@example.com", "integrationEmail": "admin@example.com",
            },
        }
        config.update(overrides)
        path = Path(directory) / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    def test_missing_config_has_actionable_message(self):
        with self.assertRaisesRegex(demo_operator.OperatorError, "Copy config/runtime"):
            demo_operator.load_json(Path("/does/not/exist"))

    def test_template_command_includes_fields_and_options(self):
        command = demo_operator.box_template_command({
            "displayName": "Demo",
            "templateKey": "demo",
            "fields": [{"key": "status", "type": "enum", "options": ["Open", "Done"]}],
        })
        self.assertIn("--enum", command)
        self.assertEqual(command.count("--option"), 2)
        self.assertIn("status", command)

    def test_parse_id_accepts_box_json(self):
        self.assertEqual(demo_operator.parse_id('{"id":"123"}'), "123")
        self.assertEqual(demo_operator.parse_id('{"templateKey":"clmContract"}'), "clmContract")
        self.assertEqual(demo_operator.parse_id(""), "DRY_RUN")

    def test_doctor_reports_blank_org(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_config(directory, salesforce={"orgAlias": ""})
            with patch.object(demo_operator, "require_tools", return_value=[]):
                with self.assertRaisesRegex(demo_operator.OperatorError, "orgAlias"):
                    demo_operator.doctor(path, offline=True)

    def test_doctor_rejects_unapproved_box_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_config(directory)
            config = json.loads(path.read_text())
            config["box"]["parentFolderId"] = "0"
            path.write_text(json.dumps(config))
            with patch.object(demo_operator, "require_tools", return_value=[]):
                with self.assertRaisesRegex(demo_operator.OperatorError, "allowRootFolder"):
                    demo_operator.doctor(path, offline=True)

    def test_salesforce_deploy_dry_run_uses_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_config(directory)
            with patch.object(demo_operator, "run") as run:
                with redirect_stdout(io.StringIO()):
                    demo_operator.salesforce_deploy(path, dry_run=True)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn("demo", commands[0])
            self.assertTrue(any("CLM_Demo_Operator" in command for command in commands))

    def test_box_foundation_skips_resources_recorded_in_state(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = self.write_config(directory)
            state_path = Path(directory) / "state.json"
            template_keys = [
                item["templateKey"]
                for item in demo_operator.load_json(demo_operator.ROOT / "config/box/metadata-templates.json")["templates"]
            ]
            state = {
                "box": {
                    "folders": {"workspace": "1", **{name: str(index + 2) for index, name in enumerate(demo_operator.FOLDERS)}},
                    "metadataTemplates": {key: key for key in template_keys},
                    "files": {Path(path).name: "file" for paths in demo_operator.UPLOADS.values() for path in paths},
                }
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            with patch.object(demo_operator, "STATE_PATH", state_path), patch.object(demo_operator, "run") as run, patch.object(demo_operator, "doctor"):
                with redirect_stdout(io.StringIO()):
                    demo_operator.box_foundation(config_path, dry_run=False)
            run.assert_not_called()

    def test_validate_requires_published_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_config(directory, box={"parentFolderId": "123", "enterpriseId": "456"})
            with self.assertRaisesRegex(demo_operator.OperatorError, "appUrl"):
                demo_operator.validate(path, scenario="box-automate-agentic-orchestration", offline=True)

    def test_resolve_value_reports_and_replaces_bindings(self):
        unresolved = set()
        result = demo_operator.resolve_value(
            {"folder": "${box.folders.workspace}", "url": "https://${box.hostname}/folder/${box.folders.missing}"},
            {"box.folders.workspace": "123", "box.hostname": "example.box.com"},
            unresolved,
        )
        self.assertEqual(result["folder"], "123")
        self.assertEqual(result["url"], "https://example.box.com/folder/${box.folders.missing}")
        self.assertEqual(unresolved, {"box.folders.missing"})

    def test_resolve_config_writes_environment_specific_spec(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "config/box/spec.json"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps({"folder": "${box.folders.workspace}", "host": "${box.hostname}"}))
            state_path = root / "config/runtime/bootstrap-state.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(json.dumps({"box": {"folders": {"workspace": "123"}, "files": {}, "metadataTemplates": {}}}))
            config_path = root / "config/runtime/demo-environment.json"
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com", "reviewerLogins": []}}))
            with patch.object(demo_operator, "ROOT", root), patch.object(demo_operator, "STATE_PATH", state_path), patch.object(demo_operator, "PORTABLE_SPECS", ["config/box/spec.json"]):
                with redirect_stdout(io.StringIO()):
                    demo_operator.resolve_config(config_path, allow_unresolved=False)
            result = json.loads((root / "config/runtime/generated/box/spec.json").read_text())
            self.assertEqual(result, {"folder": "123", "host": "example.box.com"})

    def test_metadata_numbers_use_box_cli_number_syntax(self):
        self.assertEqual(demo_operator.metadata_data({"count": 12, "owner": "Legal Ops"}), ["--data", "count=#12", "--data", "owner=Legal Ops"])

    def test_metadata_seed_dry_run_plans_all_dashboard_records(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = self.write_config(directory)
            missing_state = Path(directory) / "missing-state.json"
            with patch.object(demo_operator, "STATE_PATH", missing_state), patch.object(demo_operator, "doctor"), patch.object(demo_operator, "run", return_value="") as run:
                with redirect_stdout(io.StringIO()):
                    demo_operator.seed_metadata(config_path, dry_run=True)
            self.assertEqual(run.call_count, 16)

    def test_validate_urls_rejects_cross_tenant_box_url(self):
        config = {"box": {"hostname": "a.box.com", "appUrl": "https://b.box.com/app/1"}, "salesforce": {"myDomainUrl": "https://example.my.salesforce.com"}}
        self.assertIn("box.appUrl hostname does not match box.hostname", demo_operator.validate_urls(config))


if __name__ == "__main__":
    unittest.main()
