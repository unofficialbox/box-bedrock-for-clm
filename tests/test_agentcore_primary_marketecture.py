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

        self.assertIn(
            "Orchestrate contract work across content, data, and teams.",
            document,
        )
        self.assertIn(
            "Coordinate agents, systems, and experts around every contract.",
            document,
        )
        for retired_copy in (
            "One agent experience. Every contract system.",
            "One intelligent experience, connected to every trusted system.",
            "Agents on top. Systems of record below. Humans govern across.",
        ):
            self.assertNotIn(retired_copy, document)
        self.assertIn("Curated analytical intelligence", document)
        self.assertIn("Content, business data, and analytics", document)
        self.assertIn("People approve consequential decisions", document)
        self.assertEqual(document.count("data:image/png;base64,"), 9)
        self.assertEqual(document.count("data:image/jpeg;base64,"), 1)
        self.assertGreaterEqual(document.count("data:image/svg+xml;base64,"), 5)
        for brand in ("aws", "agentcore", "box", "salesforce", "databricks"):
            self.assertIn(f'data-brand-logo="{brand}"', document)
        self.assertLess(
            document.index('id="architecture"'),
            document.index('class="hero shell"'),
        )
        self.assertIsNone(re.search(r'(?:src|href)=["\']https?://', document))


if __name__ == "__main__":
    unittest.main()
