#!/usr/bin/env python3
"""Validate the Zotero-grounded literature learning skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zotero-literature-learning" / "SKILL.md"
SCHEMA = ROOT / "zotero-literature-learning" / "references" / "materials-package-schema.md"

REQUIRED_PHRASES = (
    "name: zotero-literature-learning",
    "requires: zotero-mcp",
    "version: 0.1.0",
    "Stage 0 — 定义学习任务",
    "Stage 1 — Zotero 候选检索",
    "Stage 2 — 元数据与可访问性筛选",
    "Stage 3 — 选择 peer corpus",
    "Stage 4 — 分层阅读",
    "Stage 5 — 抽取可迁移模式",
    "Stage 6 — 形成三个 profile",
    "Stage 7 — 交接",
    "Stage 8 — 修改后回查",
    "zotero_get_recent",
    "zotero_semantic_search",
    "zotero_get_item_metadata",
    "zotero_get_item_children",
    "zotero_get_pdf_outline",
    "zotero_read_pdf_pages",
    "zotero_get_item_fulltext",
    "metadata-only",
    "abstract-only",
    "full-text-inspected",
    "calibration_confidence",
    "Evidence Profile",
    "Style Profile",
    "Argument Profile",
    "MATERIALS_PACKAGE",
    "POST_WRITE_MATERIALS_AUDIT",
    "不复制同行原句",
    "不生成 RIS",
    "corpus_status: unavailable",
    "unresolved_gaps",
    "done_when",
)


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def main() -> None:
    if not SKILL.exists():
        fail(f"skill file missing: {SKILL}")
    if not SCHEMA.exists():
        fail(f"schema reference missing: {SCHEMA}")
    text = SKILL.read_text(encoding="utf-8")
    schema = SCHEMA.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "name: zotero-literature-learning" not in text:
        fail("frontmatter does not declare zotero-literature-learning")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            fail(f"missing required workflow or guardrail phrase: {phrase}")
    for phrase in ("Candidate record", "Evidence profile row", "Style profile row", "Handoff record", "File privacy"):
        if phrase not in schema:
            fail(f"schema reference missing: {phrase}")
    if not re.search(r"\| Source ID \| Zotero key \| DOI/PMID \| Relevance", text):
        fail("missing corpus ledger table")
    if not re.search(r"\| Pattern ID \| Source ID \| Location \| Pattern type", text):
        fail("missing pattern ledger table")
    if "RIS" not in text or "zotero-evidence-review" not in text:
        fail("missing RIS boundary and evidence-review handoff")
    print("✅ literature-learning skill structure and guardrails passed")


if __name__ == "__main__":
    main()
