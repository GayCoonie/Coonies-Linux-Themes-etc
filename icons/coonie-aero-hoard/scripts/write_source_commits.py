#!/usr/bin/env python3
"""Record exact source revisions without embedding source repositories."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


REPOS = {
    "ocd": "ocd",
    "crystal-remix": "crystal-remix",
    "oxygen-refit": "oxygenrefit2-gitlab",
    "nuovext": "nuovext",
    "gnome-colors": "gnome-colors",
    "newaita": "newaita-reborn",
    "papirus": "papirus",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = {}
    for name, directory in REPOS.items():
        root = args.sources / directory
        result[name] = {
            "commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
            "commit_date": subprocess.check_output(["git", "-C", str(root), "show", "-s", "--format=%cs", "HEAD"], text=True).strip(),
            "remote": subprocess.check_output(["git", "-C", str(root), "remote", "get-url", "origin"], text=True).strip(),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

