import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts/experimental_box_forms_private_api.py"
SPEC = importlib.util.spec_from_file_location("experimental_box_forms_private_api", MODULE_PATH)
provisioner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(provisioner)


class ExperimentalBoxFormsPrivateApiTests(unittest.TestCase):
    def valid_spec(self):
        return {
            "schemaVersion": 1,
            "name": "CLM Forms API Lab - Contract Intake",
            "description": "Unsupported experiment",
            "provisioning": {
                "mode": "experimental-private-rest",
                "existingFormPolicy": "reconcile-exact-title",
                "delete": False,
                "publishLink": False,
                "share": False,
                "submitTestResponse": False,
            },
            "fields": [
                {"key": "experimentField", "label": "Experiment field", "type": "shortText", "required": True}
            ],
        }

    def test_repository_lab_definition_is_valid(self):
        provisioner.validate_spec(provisioner.load_json(provisioner.DEFAULT_SPEC))

    def test_rejects_production_title(self):
        spec = self.valid_spec()
        spec["name"] = "New Contract Request"
        with self.assertRaisesRegex(provisioner.ExperimentalProvisionerError, "must begin"):
            provisioner.validate_spec(spec)

    def test_rejects_any_delete_behavior(self):
        spec = self.valid_spec()
        spec["provisioning"]["delete"] = True
        with self.assertRaisesRegex(provisioner.ExperimentalProvisionerError, "provisioning.delete"):
            provisioner.validate_spec(spec)

    def test_field_identifiers_use_required_element_prefix(self):
        content = provisioner.form_content(self.valid_spec())
        field = content["components"]["group-0"]["items"][0]
        self.assertTrue(field.startswith("element-"))
        self.assertEqual(content["components"][field]["id"], field)

    def test_proven_field_types_map_to_observed_private_schema(self):
        spec = self.valid_spec()
        spec["fields"] = [
            {"key": "short", "label": "Short", "type": "shortText", "required": True},
            {"key": "long", "label": "Long", "type": "longText", "required": False},
            {"key": "email", "label": "Email", "type": "email", "required": True},
            {"key": "number", "label": "Number", "type": "number", "required": False},
            {"key": "choice", "label": "Choice", "type": "dropdown", "options": ["A", "B"], "required": True},
            {"key": "date", "label": "Date", "type": "date", "required": False},
            {"key": "upload", "label": "Upload", "type": "fileUpload", "required": False},
        ]
        content = provisioner.form_content(spec, "123456")
        components = [
            content["components"][field_id]
            for field_id in content["components"]["group-0"]["items"]
        ]
        self.assertEqual(
            [component["type"] for component in components],
            ["textField", "textField", "textField", "numberField", "selectField", "dateTimeField", "uploadField"],
        )
        self.assertTrue(components[1]["multiline"])
        self.assertEqual(components[2]["textType"], "email")
        self.assertEqual(components[4]["maximumSelections"], 0)
        self.assertEqual(components[5]["dateTimeMode"], "date")
        self.assertEqual(components[6]["folderId"], "123456")

    def test_dropdown_requires_unique_options(self):
        spec = self.valid_spec()
        spec["fields"][0] = {
            "key": "choice",
            "label": "Choice",
            "type": "dropdown",
            "options": ["A", "A"],
            "required": True,
        }
        with self.assertRaisesRegex(provisioner.ExperimentalProvisionerError, "unique"):
            provisioner.validate_spec(spec)

    def test_upload_requires_runtime_folder(self):
        spec = self.valid_spec()
        spec["fields"][0]["type"] = "fileUpload"
        with self.assertRaisesRegex(provisioner.ExperimentalProvisionerError, "parentFolderId"):
            provisioner.form_content(spec)

    def test_executor_is_exact_title_and_non_destructive(self):
        script = provisioner.executor_script(self.valid_spec(), "example.box.com")
        self.assertEqual(len(script.splitlines()), 1)
        self.assertIn('/file-requests?limit=20&sortDirection=DESC&sortField=modifiedAt&type=form', script)
        self.assertIn('body?.data', script)
        self.assertIn('fileRequestId', script)
        self.assertIn('/form-version/', script)
        self.assertIn('Duplicate guard failed', script)
        self.assertNotIn('method: "DELETE"', script)
        self.assertNotIn('/publish', script)
        self.assertNotIn('/share', script)
        self.assertNotIn('/submit', script)

    def test_write_requires_exact_acknowledgement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            config_path = root / "config.json"
            output_path = root / "executor.js"
            spec_path.write_text(json.dumps(self.valid_spec()))
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com"}}))
            with self.assertRaisesRegex(provisioner.ExperimentalProvisionerError, "Refusing"):
                provisioner.write_executor(
                    spec_path,
                    config_path,
                    root / "unused-form-runtime.json",
                    output_path,
                    "",
                )
            self.assertFalse(output_path.exists())

    def test_write_executor_contains_no_runtime_ids_or_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            config_path = root / "config.json"
            output_path = root / "executor.js"
            spec_path.write_text(json.dumps(self.valid_spec()))
            config_path.write_text(json.dumps({"box": {"hostname": "example.box.com"}}))
            provisioner.write_executor(
                spec_path,
                config_path,
                root / "unused-form-runtime.json",
                output_path,
                provisioner.ACKNOWLEDGEMENT,
            )
            script = output_path.read_text()
            self.assertNotIn("cookie", script.lower())
            self.assertNotIn("authorization", script.lower())
            self.assertNotIn("enterpriseId", script)
            self.assertNotIn("folderId", script)


if __name__ == "__main__":
    unittest.main()
