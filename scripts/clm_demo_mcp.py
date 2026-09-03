#!/usr/bin/env python3
"""A local MCP server that offers the demo beats as prompts, so nothing is pasted.

Claude Desktop lists a server's prompts in its attachment menu, so the presenter picks
"Read it against our approved positions" instead of copying a block out of a run sheet on
a shared screen. The hosted Salesforce MCP server cannot do this -- an McpServerDefinition
exposes tools only -- which is why this runs locally beside it.

DEMO-STORYBOARD.html is the source of truth. The prompts are read out of the beats at
request time, so editing a beat changes the menu with nothing to regenerate, and a
validation check already fails when the beats and the custom-instruction run order
disagree.

Speaks JSON-RPC 2.0 over stdin/stdout, one message per line, with no dependencies: this
has to run on a presenter's laptop the morning of a demo, not survive a pip install.

Configure it in claude_desktop_config.json:

    {
      "mcpServers": {
        "clm-demo": {
          "command": "python3",
          "args": ["<repo>/scripts/clm_demo_mcp.py"]
        }
      }
    }
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORYBOARD = Path(os.environ.get("CLM_STORYBOARD", ROOT / "DEMO-STORYBOARD.html"))

SERVER_INFO = {"name": "clm-demo", "version": "1.0.0"}
DEFAULT_PROTOCOL = "2025-06-18"

# JSON-RPC error codes we actually use.
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class StoryboardError(RuntimeError):
    """The storyboard could not be read, which is worth saying rather than returning nothing."""


def _text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def _slug(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", title.lower())).strip("-")


def load_beats(path: Path = STORYBOARD) -> list[dict]:
    """Return one entry per prompt in the beats section, in running order.

    Each carries the beat number printed on the sheet, plus a `label` that adds a letter
    when one beat holds several prompts, so a presenter picking "Beat 6b" is picking what
    the sheet calls beat 6.
    """
    if not path.is_file():
        raise StoryboardError(f"storyboard not found at {path}")
    source = path.read_text(encoding="utf-8")

    marker = "<h2>The six beats</h2>"
    if marker not in source:
        raise StoryboardError(f"{path.name} has no beats section")
    beats = source[source.index(marker) :]

    steps: list[dict] = []
    heading = "Demo"
    beat = "?"
    # Walk markers, headings and prompt blocks together so each prompt keeps the beat
    # number the presenter is reading off the printed sheet. Numbering by position here
    # would be off by one, because beat 1 happens in a browser and contributes no prompt.
    pattern = re.compile(
        r"<div class=\"marker\">(?P<beat>\d+)<span"
        r"|<h3>(?P<heading>.*?)</h3>"
        r"|<div class=\"block-label\"><span>prompt</span>.*?<pre>(?P<prompt>.*?)</pre>",
        re.S,
    )
    for match in pattern.finditer(beats):
        if match.group("beat") is not None:
            beat = match.group("beat")
            continue
        if match.group("heading") is not None:
            heading = _text(match.group("heading"))
            continue
        prompt = _text(match.group("prompt"))
        if not prompt:
            continue
        steps.append({"beat": beat, "heading": heading, "prompt": prompt})

    if not steps:
        raise StoryboardError(f"{path.name} has a beats section but no prompts in it")

    # A beat can hold several prompts -- the signature beat refuses, then sends -- and
    # three menu entries reading "Put the position on paper, then stop" are no menu at
    # all. Letter them, the way the sheet reads aloud.
    counts: dict[str, int] = {}
    for step in steps:
        counts[step["beat"]] = counts.get(step["beat"], 0) + 1
    seen: dict[str, int] = {}
    for step in steps:
        if counts[step["beat"]] == 1:
            step["label"] = step["beat"]
        else:
            seen[step["beat"]] = seen.get(step["beat"], 0) + 1
            step["label"] = f"{step['beat']}{chr(ord('a') + seen[step['beat']] - 1)}"
    return steps


def prompt_descriptors() -> list[dict]:
    descriptors = []
    for step in load_beats():
        descriptors.append(
            {
                "name": f"beat-{step['label']}-{_slug(step['heading'])}",
                "title": f"Beat {step['label']} \u00b7 {step['heading']}",
                "description": step["prompt"],
                "arguments": [],
            }
        )
    return descriptors


def prompt_body(name: str) -> dict:
    for step, descriptor in zip(load_beats(), prompt_descriptors()):
        if descriptor["name"] == name:
            return {
                "description": descriptor["title"],
                "messages": [
                    {
                        "role": "user",
                        "content": {"type": "text", "text": step["prompt"]},
                    }
                ],
            }
    raise KeyError(name)


def handle(message: dict) -> dict | None:
    """Return a response, or None for a notification that takes no reply."""
    method = message.get("method")
    message_id = message.get("id")

    # A notification has no id, and the spec forbids answering one.
    if message_id is None:
        return None

    def ok(result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": message_id, "result": result}

    def error(code: int, text: str) -> dict:
        return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": text}}

    if method == "initialize":
        # Echo the client's protocol version when it names one: this server has nothing
        # version-specific in it, and refusing a version we would have satisfied is worse
        # than speaking the client's.
        requested = (message.get("params") or {}).get("protocolVersion")
        return ok(
            {
                "protocolVersion": requested or DEFAULT_PROTOCOL,
                "capabilities": {"prompts": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
            }
        )

    if method == "ping":
        return ok({})

    if method == "prompts/list":
        try:
            return ok({"prompts": prompt_descriptors()})
        except StoryboardError as failure:
            return error(INTERNAL_ERROR, str(failure))

    if method == "prompts/get":
        params = message.get("params") or {}
        name = params.get("name")
        if not name:
            return error(INVALID_PARAMS, "prompts/get needs a name")
        try:
            return ok(prompt_body(name))
        except StoryboardError as failure:
            return error(INTERNAL_ERROR, str(failure))
        except KeyError:
            return error(INVALID_PARAMS, f"no prompt named {name}")

    return error(METHOD_NOT_FOUND, f"{method} is not supported by this server")


def serve(stdin=sys.stdin, stdout=sys.stdout) -> None:
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            # Nothing to reply to: without a parsed id there is no one to answer.
            continue
        response = handle(message)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()


if __name__ == "__main__":
    serve()
