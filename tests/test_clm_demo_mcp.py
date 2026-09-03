import html
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts/clm_demo_mcp.py"
SPEC = importlib.util.spec_from_file_location("clm_demo_mcp", MODULE_PATH)
mcp = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mcp)

ROOT = Path(__file__).parents[1]
STORYBOARD = ROOT / "DEMO-STORYBOARD.html"


def converse(*messages: dict) -> list[dict]:
    """Drive the server the way a client does: newline-delimited JSON on stdin."""
    stdin = io.StringIO("".join(json.dumps(m) + "\n" for m in messages))
    stdout = io.StringIO()
    mcp.serve(stdin, stdout)
    return [json.loads(line) for line in stdout.getvalue().splitlines() if line]


class HandshakeTests(unittest.TestCase):
    def test_declares_prompts_and_echoes_the_client_protocol(self):
        [reply] = converse(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05"}}
        )
        self.assertEqual("2024-11-05", reply["result"]["protocolVersion"])
        self.assertIn("prompts", reply["result"]["capabilities"])

    def test_falls_back_to_its_own_protocol_when_the_client_names_none(self):
        [reply] = converse({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(mcp.DEFAULT_PROTOCOL, reply["result"]["protocolVersion"])

    def test_answers_nothing_to_a_notification(self):
        # The spec forbids replying to a message with no id; doing so wedges some clients.
        self.assertEqual([], converse({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_reports_an_unknown_method_rather_than_staying_silent(self):
        [reply] = converse({"jsonrpc": "2.0", "id": 7, "method": "resources/list"})
        self.assertEqual(mcp.METHOD_NOT_FOUND, reply["error"]["code"])

    def test_survives_a_line_that_is_not_json(self):
        stdin = io.StringIO('not json\n{"jsonrpc":"2.0","id":1,"method":"ping"}\n')
        stdout = io.StringIO()
        mcp.serve(stdin, stdout)
        self.assertEqual(1, json.loads(stdout.getvalue().strip())["id"])


class PromptTests(unittest.TestCase):
    def test_lists_every_beat_prompt_in_running_order(self):
        [reply] = converse({"jsonrpc": "2.0", "id": 2, "method": "prompts/list"})
        prompts = reply["result"]["prompts"]
        self.assertEqual(len(mcp.load_beats()), len(prompts))
        self.assertEqual(
            [step["label"] for step in mcp.load_beats()],
            [p["name"].split("-")[1] for p in prompts],
        )

    def test_numbers_match_the_beats_the_sheet_prints(self):
        # Numbering by position would be off by one: beat 1 is the portal and contributes
        # no prompt, so a presenter reading "beat 4" would be offered beat 5.
        labels = [step["label"] for step in mcp.load_beats()]
        self.assertEqual("2", labels[0])
        self.assertTrue(all(label[0].isdigit() for label in labels))

    def test_names_are_unique_even_when_one_beat_holds_several_prompts(self):
        # The signature beat drafts, refuses, then sends, so names cannot be per beat.
        names = [p["name"] for p in mcp.prompt_descriptors()]
        self.assertEqual(len(names), len(set(names)))

    def test_entries_sharing_a_heading_are_still_told_apart(self):
        # Three menu rows reading "Put the position on paper, then stop" are no menu at
        # all, so what a picker shows -- title and description -- must differ.
        shown = [(p["title"], p["description"]) for p in mcp.prompt_descriptors()]
        self.assertEqual(len(shown), len(set(shown)))

    def test_returns_the_prompt_text_verbatim(self):
        first = mcp.prompt_descriptors()[0]["name"]
        [reply] = converse(
            {"jsonrpc": "2.0", "id": 3, "method": "prompts/get", "params": {"name": first}}
        )
        message = reply["result"]["messages"][0]
        self.assertEqual("user", message["role"])
        self.assertEqual(mcp.load_beats()[0]["prompt"], message["content"]["text"])

    def test_the_offered_text_is_what_the_storyboard_shows(self):
        # The whole point is that nobody retypes a prompt, so a paraphrase here would be
        # a silent divergence from the run sheet the presenter is reading.
        storyboard = html.unescape(STORYBOARD.read_text(encoding="utf-8"))
        for step in mcp.load_beats():
            self.assertIn(step["prompt"], storyboard)

    def test_refuses_an_unknown_prompt_name(self):
        [reply] = converse(
            {"jsonrpc": "2.0", "id": 4, "method": "prompts/get", "params": {"name": "beat-99"}}
        )
        self.assertEqual(mcp.INVALID_PARAMS, reply["error"]["code"])

    def test_requires_a_name(self):
        [reply] = converse({"jsonrpc": "2.0", "id": 5, "method": "prompts/get", "params": {}})
        self.assertEqual(mcp.INVALID_PARAMS, reply["error"]["code"])


class MissingStoryboardTests(unittest.TestCase):
    def test_says_why_rather_than_offering_an_empty_menu(self):
        # An empty list reads as "this demo has no beats", which sends a presenter hunting
        # in the wrong place. Fail loudly with the path that could not be read.
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "DEMO-STORYBOARD.html"
            original = mcp.STORYBOARD
            try:
                mcp.STORYBOARD = absent
                mcp.load_beats.__defaults__ = (absent,)
                [reply] = converse({"jsonrpc": "2.0", "id": 6, "method": "prompts/list"})
                self.assertEqual(mcp.INTERNAL_ERROR, reply["error"]["code"])
                self.assertIn("storyboard not found", reply["error"]["message"])
            finally:
                mcp.STORYBOARD = original
                mcp.load_beats.__defaults__ = (original,)


if __name__ == "__main__":
    unittest.main()
