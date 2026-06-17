#!/usr/bin/env python3
"""Validate the zotero-evidence-review skill markdown."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - fallback for minimal environments
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "zotero-evidence-review" / "SKILL.md"
REQUIRED_TEMPLATES = {
    "REFS_BLOCK",
    "CLAIM_EVIDENCE_MATRIX",
    "WRITING_SUGGESTIONS_TABLE",
    "DIFF_REVISED_PARAGRAPH",
    "VERIFICATION_REPORT",
}
REQUIRED_HEADINGS = [
    "## 0. Intent Detection",
    "## 0.5 Library Health Check",
    "## Tool Selection",
    "## Safety Rules",
    "## 1. Semantic + Structured Search",
    "## 1.5 Collection and Tag Search",
    "## 2. Paragraph Evidence & Citation Analysis",
    "## 3. Citation Verification Protocol",
    "## 4. Chinese Academic Writing Rules",
    "## 5. External Source Fallback",
    "## Appendix: Output Templates",
]


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"✅ {message}")


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter is not closed")
    raw = text[4:end]
    if yaml is not None:
        data = yaml.safe_load(raw)
    else:
        data = {}
        current_parent: str | None = None
        for line in raw.splitlines():
            if not line.strip():
                continue
            if not line.startswith(" ") and ":" in line:
                key, value = line.split(":", 1)
                value = value.strip()
                if value:
                    data[key] = value
                    current_parent = None
                else:
                    data[key] = {}
                    current_parent = key
            elif current_parent and line.startswith("  ") and ":" in line:
                key, value = line.strip().split(":", 1)
                parent = data.setdefault(current_parent, {})
                assert isinstance(parent, dict)
                parent[key] = value.strip()
    if not isinstance(data, dict):
        fail("SKILL.md frontmatter did not parse to a mapping")
    return data


def strip_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def main() -> None:
    if not SKILL_PATH.exists():
        fail(f"Missing skill file: {SKILL_PATH}")

    text = SKILL_PATH.read_text(encoding="utf-8")

    frontmatter = parse_frontmatter(text)
    if frontmatter.get("name") != "zotero-evidence-review":
        fail("frontmatter name must be zotero-evidence-review")
    if "zcode" not in str(frontmatter.get("compatibility", "")):
        fail("frontmatter compatibility must include zcode")
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict) or not metadata.get("version"):
        fail("frontmatter metadata.version is required")
    ok(f"frontmatter parsed; version {metadata['version']}")

    fence_count = text.count("```")
    if fence_count % 2 != 0:
        fail(f"unbalanced markdown code fences: {fence_count}")
    ok(f"markdown code fences balanced: {fence_count}")

    no_code = strip_code_fences(text)
    for heading in REQUIRED_HEADINGS:
        if heading not in no_code:
            fail(f"missing required heading: {heading}")
    ok("required workflow headings present")

    if "## 6. External Source Fallback" in no_code:
        fail("old section numbering still present: ## 6. External Source Fallback")
    if "## 5. Chinese Academic Writing Rules" in no_code:
        fail("old section numbering still present: ## 5. Chinese Academic Writing Rules")
    ok("section numbering is consistent")

    for template in REQUIRED_TEMPLATES:
        if f"### {template}" not in no_code:
            fail(f"missing appendix template definition: {template}")
    ok("appendix template definitions present")

    risky_phrases = [
        "recommend these free MCP Servers",
        "When CDP is unavailable, execute all of the following:",
        "and search external MCP tools such as",
    ]
    found = [phrase for phrase in risky_phrases if phrase in text]
    if found:
        fail("external-tool availability guards are incomplete: " + ", ".join(found))
    ok("external-tool availability guards present")

    print("\nAll validations passed.")


if __name__ == "__main__":
    main()
