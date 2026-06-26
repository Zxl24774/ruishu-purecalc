#!/usr/bin/env python3
"""Lightweight lint for a Ruishu site profile JSON."""

import json
import sys
from pathlib import Path


REQUIRED_TOP = ["target", "entry_path", "headers", "cookie", "basearr", "verification"]


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: profile_lint.py site_profile.json")
    profile = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    errors = []
    for key in REQUIRED_TOP:
        if key not in profile:
            errors.append(f"missing top-level key: {key}")
    branches = profile.get("basearr", {}).get("branches", [])
    if branches is not None and not isinstance(branches, list):
        errors.append("basearr.branches must be a list")
    for i, branch in enumerate(branches or []):
        for key in ("name", "condition", "basearr_length"):
            if key not in branch:
                errors.append(f"branch[{i}] missing {key}")
    if errors:
        for err in errors:
            print("ERROR:", err)
        raise SystemExit(1)
    print("profile lint PASS")


if __name__ == "__main__":
    main(sys.argv)

