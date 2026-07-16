import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_agentcore_primary_marketecture.py"


class AgentCorePrimaryMarketectureTests(unittest.TestCase):
    def test_builds_offline_agent_primary_architecture(self) -> None:
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            spec = importlib.util.spec_from_file_location("agentcore_market", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)

        with tempfile.TemporaryDirectory() as directory:
            module.OUTPUT = Path(directory) / "agentcore-marketecture.html"
            document = module.build().read_text(encoding="utf-8")

        self.assertIn("One agent experience. Every contract system.", document)
        self.assertIn("Curated analytical intelligence", document)
        self.assertIn("Governed systems of record", document)
        self.assertIn("Humans decide", document)
        self.assertEqual(document.count("data:image/png;base64,"), 8)
        self.assertIsNone(re.search(r'(?:src|href)=["\']https?://', document))


if __name__ == "__main__":
    unittest.main()
