#!/usr/bin/env python3
"""Minimal reader for the BCL artifact format used by box-dispatch.

BCL is the only supported config format in this repository. This module reads
the HCL-like inventory that `bcl.LoadBCL` parses in box-dispatch:

    locals {
      "bcl" = {
        "resources" = [
          { "name" = ... "type" = ... "provider" = ... "config" = { ... } }
        ]
      }
    }

Only the read path is implemented, and only the subset the capture tooling
needs: the config payload of the first (or named) resource. Writing BCL stays
in box-dispatch.

Port note: box-dispatch already owns an equivalent parser in
internal/bcl/bcl.go (`parseBCLLocals` plus `hclLikeParser`). A Go port of this
package should call that instead of reimplementing it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BCLError(RuntimeError):
    """Raised when a BCL document cannot be read."""


class _Parser:
    """Parses the HCL-like value grammar: objects, arrays, strings, numbers, bools, null."""

    def __init__(self, src: str, pos: int = 0) -> None:
        self.src = src
        self.pos = pos

    def skip(self) -> None:
        while self.pos < len(self.src):
            char = self.src[self.pos]
            if char in " \t\r\n":
                self.pos += 1
            elif char == "#":
                while self.pos < len(self.src) and self.src[self.pos] != "\n":
                    self.pos += 1
            else:
                break

    def value(self) -> Any:
        self.skip()
        char = self.src[self.pos]
        if char == "{":
            return self.mapping()
        if char == "[":
            return self.sequence()
        if char == '"':
            return self.string()
        for literal, parsed in (("true", True), ("false", False), ("null", None)):
            if self.src.startswith(literal, self.pos):
                self.pos += len(literal)
                return parsed
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos] not in " \t\r\n}],":
            self.pos += 1
        token = self.src[start : self.pos]
        for cast in (int, float):
            try:
                return cast(token)
            except ValueError:
                continue
        return token

    def string(self) -> str:
        if self.src[self.pos] != '"':
            raise BCLError(f"expected a string at offset {self.pos}")
        self.pos += 1
        out: list[str] = []
        while self.src[self.pos] != '"':
            if self.src[self.pos] == "\\":
                nxt = self.src[self.pos + 1]
                out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, "\\" + nxt))
                self.pos += 2
            else:
                out.append(self.src[self.pos])
                self.pos += 1
        self.pos += 1
        return "".join(out)

    def bare_key(self) -> str:
        start = self.pos
        while self.src[self.pos] not in " \t\r\n=":
            self.pos += 1
        return self.src[start : self.pos]

    def mapping(self) -> dict[str, Any]:
        self.pos += 1
        out: dict[str, Any] = {}
        while True:
            self.skip()
            if self.src[self.pos] == "}":
                self.pos += 1
                return out
            if self.src[self.pos] == ",":
                self.pos += 1
                continue
            key = self.string() if self.src[self.pos] == '"' else self.bare_key()
            self.skip()
            if self.src[self.pos] == "=":
                self.pos += 1
            out[key] = self.value()

    def sequence(self) -> list[Any]:
        self.pos += 1
        out: list[Any] = []
        while True:
            self.skip()
            if self.src[self.pos] == "]":
                self.pos += 1
                return out
            if self.src[self.pos] == ",":
                self.pos += 1
                continue
            out.append(self.value())


def load_document(path: Path) -> dict[str, Any]:
    """Return the whole BCL inventory document."""
    if not path.is_file():
        raise BCLError(f"Missing required file: {path}")
    src = path.read_text(encoding="utf-8")

    # canonical JSON payloads are also valid BCL documents
    try:
        parsed = json.loads(src)
    except json.JSONDecodeError:
        pass
    else:
        if isinstance(parsed, dict) and parsed.get("provider"):
            return parsed

    key = src.find('"bcl"')
    if key < 0:
        raise BCLError(f"Missing bcl inventory block in {path}")
    parser = _Parser(src, key)
    parser.string()
    parser.skip()
    if parser.src[parser.pos] != "=":
        raise BCLError(f"Malformed bcl inventory block in {path}")
    parser.pos += 1
    document = parser.value()
    if not isinstance(document, dict):
        raise BCLError(f"Expected a bcl inventory object in {path}")
    return document


def load_config(path: Path, resource_name: str | None = None) -> dict[str, Any]:
    """Return one resource's `config` payload.

    This is what the capture tooling consumes: the portable artifact body,
    without the identity fields box-dispatch uses for import.
    """
    document = load_document(path)
    resources = document.get("resources") or []
    if not resources:
        raise BCLError(f"No resources in {path}")
    if resource_name is None:
        resource = resources[0]
    else:
        matches = [r for r in resources if r.get("name") == resource_name]
        if not matches:
            raise BCLError(f"No resource named {resource_name!r} in {path}")
        resource = matches[0]
    config = resource.get("config")
    if not isinstance(config, dict):
        raise BCLError(f"Resource in {path} has no config object")
    identity = {
        "provider",
        "provider_object_id",
        "artifact_name",
        "artifact_type",
        "enterprise_id",
        "created_at",
    }
    return {key: value for key, value in config.items() if key not in identity}
