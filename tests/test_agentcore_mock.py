import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "scripts/run_agentcore_mock.py"
SPEC = importlib.util.spec_from_file_location("run_agentcore_mock", MODULE_PATH)
run_agentcore_mock = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(run_agentcore_mock)


class AgentCoreMockTests(unittest.TestCase):
    def test_box_context_uses_tenant_neutral_local_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "output/pdf/northstar-msa-redline-v3.pdf"
            pdf.parent.mkdir(parents=True)
            pdf.write_bytes(b"fixture")

            with patch.object(run_agentcore_mock, "ROOT", root):
                context = run_agentcore_mock.box_context()

            self.assertEqual(context["workspaceId"], "local-fixture")
            self.assertEqual(context["source"], "generated-local-assets")
            self.assertEqual(
                context["files"]["northstar-msa-redline-v3.pdf"],
                "local-fixture:northstar-msa-redline-v3.pdf",
            )

    def test_box_context_prefers_operator_bootstrap_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "config/runtime/bootstrap-state.json"
            state.parent.mkdir(parents=True)
            state.write_text(
                json.dumps(
                    {
                        "box": {
                            "folders": {"workspace": "new-workspace"},
                            "files": {"northstar-dpa.pdf": "new-file"},
                        }
                    }
                )
            )

            with patch.object(run_agentcore_mock, "ROOT", root):
                context = run_agentcore_mock.box_context()

            self.assertEqual(context["workspaceId"], "new-workspace")
            self.assertEqual(context["source"], "operator-bootstrap-state")
            self.assertEqual(context["files"]["northstar-dpa.pdf"], "new-file")

    def test_box_context_can_ignore_operator_state_for_deterministic_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "config/runtime/bootstrap-state.json"
            state.parent.mkdir(parents=True)
            state.write_text(json.dumps({"box": {"folders": {"workspace": "live"}, "files": {}}}))
            pdf = root / "output/pdf"
            pdf.mkdir(parents=True)
            (pdf / "northstar-msa-redline-v3.pdf").write_bytes(b"fixture")
            with patch.object(run_agentcore_mock, "ROOT", root):
                context = run_agentcore_mock.box_context(use_runtime=False)
            self.assertEqual(context["source"], "generated-local-assets")
            self.assertEqual(context["workspaceId"], "local-fixture")


if __name__ == "__main__":
    unittest.main()
