from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class RepositoryNavigationTests(unittest.TestCase):
    def test_persona_and_scenario_entry_points_are_linked_from_root(self):
        readme = (ROOT / "README.md").read_text()
        targets = {target.split("#", 1)[0] for target in MARKDOWN_LINK.findall(readme)}
        expected = {
            "docs/operator/README.md",
            "docs/use-case-creator/README.md",
            "docs/maintainers/README.md",
            "docs/operator/scenarios/box-automate-agentic-orchestration/README.md",
            "docs/operator/scenarios/cross-platform-agentic-orchestration/README.md",
        }
        self.assertTrue(expected.issubset(targets), expected - targets)

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
        tracked = subprocess.run(
            ["git", "ls-files", "*.md"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        markdown_files = [ROOT / relative for relative in tracked]
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
