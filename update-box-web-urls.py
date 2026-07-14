#!/usr/bin/env python3
"""Update published CLM Box App/Form URLs in the local live manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MANIFEST = Path(__file__).resolve().parent / "config" / "box" / "live-box-surface.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-url", help="Published Box App URL.")
    parser.add_argument("--form-url", help="Published Box Form URL.")
    args = parser.parse_args()

    if args.app_url is None and args.form_url is None:
        parser.error("Provide --app-url, --form-url, or both.")

    data = json.loads(MANIFEST.read_text())
    if args.app_url is not None:
        data["boxAppUrl"] = args.app_url
    if args.form_url is not None:
        data["boxFormUrl"] = args.form_url
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Updated {MANIFEST}")


if __name__ == "__main__":
    main()
