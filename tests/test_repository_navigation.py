from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class RepositoryNavigationTests(unittest.TestCase):
    def test_persona_and_scenario_entry_points_are_linked_from_root(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("Box Automate Agentic Orchestration", readme)
        self.assertIn("Cross-Platform Agentic Orchestration", readme)
        self.assertIn("docs/operator/README.md", readme)
        self.assertIn("docs/use-case-creator/README.md", readme)
        self.assertIn("docs/maintainers/README.md", readme)

    def test_approved_redundant_paths_are_removed(self):
        removed = [
            "clm-template-comparison-and-reconciliation.md",
            "docs/runbooks/03-agentcore-demo.md",
            "docs/runbooks/04-box-agentforce-react-demo.md",
            "docs/operator/scenarios/cross-platform-agentic-orchestration/"
            "supporting-react-scripts/component-manifest.md",
        ]
        for relative_path in removed:
            self.assertFalse((ROOT / relative_path).exists(), relative_path)

    def test_local_markdown_links_resolve(self):
        failures: list[str] = []
        markdown_files = sorted({*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md")})
        for source in markdown_files:
            for target in MARKDOWN_LINK.findall(source.read_text()):
                if target.startswith(("#", "http://", "https://", "mailto:")):
                    continue
                path_text = target.split("#", 1)[0]
                destination = (source.parent / path_text).resolve()
                if not destination.exists():
                    failures.append(f"{source.relative_to(ROOT)} -> {target}")
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
