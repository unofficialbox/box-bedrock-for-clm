import importlib.util
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_executive_marketecture.py"


class ExecutiveMarketectureTests(unittest.TestCase):
    def test_builds_offline_target_architecture(self) -> None:
        spec = importlib.util.spec_from_file_location("executive_marketecture", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as directory:
            module.OUTPUT = Path(directory) / "marketecture.html"
            output = module.build()
            document = output.read_text(encoding="utf-8")

        self.assertIn("Cross-platform traffic director", document)
        self.assertIn("AWS Bedrock AgentCore", document)
        self.assertIn("Salesforce Agentforce", document)
        self.assertIn("Databricks", document)
        self.assertNotIn("Optional orchestration", document)
        self.assertEqual(document.count("data:image/png;base64,"), 8)
        self.assertIsNone(re.search(r'(?:src|href)=["\']https?://', document))


if __name__ == "__main__":
    unittest.main()
