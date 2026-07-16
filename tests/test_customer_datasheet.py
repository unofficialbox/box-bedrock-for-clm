import importlib.util
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_customer_datasheet.py"


class CustomerDatasheetTests(unittest.TestCase):
    def test_builds_nontechnical_offline_datasheet(self) -> None:
        spec = importlib.util.spec_from_file_location("customer_datasheet", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as directory:
            module.OUTPUT = Path(directory) / "datasheet.html"
            output = module.build()
            document = output.read_text(encoding="utf-8")

        self.assertIn("Move work forward. Decide with confidence.", document)
        self.assertNotIn("Keep people in control", document)
        self.assertIn("Move faster", document)
        self.assertIn("Reduce risk", document)
        self.assertIn("Stay in control", document)
        self.assertIn("Start with contract lifecycle management", document)
        self.assertIn("Salesforce Agentforce", document)
        self.assertIn("AWS Bedrock AgentCore", document)
        self.assertNotIn("Powered by governed agent orchestration", document)
        self.assertNotIn("API", document)
        self.assertNotIn("database", document.lower())
        self.assertIsNone(re.search(r'(?:src|href)=["\']https?://', document))


if __name__ == "__main__":
    unittest.main()
