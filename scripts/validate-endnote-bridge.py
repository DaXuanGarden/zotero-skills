#!/usr/bin/env python3
"""Static contract checks for the Zotero–EndNote bridge skill."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zotero-endnote-bridge" / "SKILL.md"
REQUIRED = [
    "zotero-endnote-bridge",
    "--dry-run",
    "--apply --apply-sqlite",
    "manifest.json",
    "backup",
    "EndNote must be closed",
]


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")
    readme = (SKILL.parent / "README.md").read_text(encoding="utf-8")
    contract_text = text + "\n" + readme
    if not text.startswith("---\n") or "name: zotero-endnote-bridge" not in text:
        raise SystemExit("invalid bridge frontmatter")
    missing = [item for item in REQUIRED if item not in contract_text]
    if missing:
        raise SystemExit("missing bridge contract: " + ", ".join(missing))
    if re.search(r"/Users/[^\s`]+", text):
        raise SystemExit("skill contains a private absolute path")
    for path in ("scripts/endnote_bridge.py", "scripts/endnote_metadata.py", "scripts/endnote_audit.py", "tests/fixtures/sample.ris", "tests/fixtures/assignments.json"):
        if not (SKILL.parent / path).exists():
            raise SystemExit(f"missing bridge file: {path}")
    print("✅ Zotero-EndNote bridge skill contract passed")


if __name__ == "__main__":
    main()
