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
    "version: 0.5.0",
    "Stage 0 — 定义学习任务",
    "Stage 1 — Zotero 候选检索",
    "Stage 2 — 元数据与可访问性筛选",
    "Stage 3 — 选择 peer corpus",
    "Stage 4 — 分层阅读",
    "Stage 4A — 写作卡点学习回路",
    "Stage 5 — 抽取可迁移模式",
    "Stage 6 — 形成四类 profile（按需）",
    "Stage 7 — 交接主报告与可追溯附录",
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
    "WRITING_BLOCK_LEARNING",
    "writing_block_card",
    "evidence-driven-writing",
    "evidence map",
    "paragraph blueprint",
    "evidence-coverage.md",
    "annotation",
    "gene-, tissue-, and pathway-level analyses",
    "Evidence Profile",
    "Style Profile",
    "Argument Profile",
    "MATERIALS_PACKAGE",
    "evidence_usable",
    "style_usable",
    "argument_usable",
    "learning_decision",
    "learning_decisions.md",
    "POST_WRITE_MATERIALS_AUDIT",
    "写作优先边界",
    "Argument-first 全文阅读",
    "当前手稿映射",
    "目标期刊模式迁移门禁",
    "Writing Reasoning Profile",
    "writing_improvement_report.md",
    "transfer_scope",
    "reject_transfer",
    "不做格式审查",
    "WRITING_OPTIONS_CARD",
    "option_id",
    "rhetorical_angle",
    "claim_delta",
    "selection_status: pending",
    "候选比较表",
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
    for phrase in ("Candidate record", "Evidence profile row", "Style profile row", "Handoff record", "Writing-block card", "Learning decision", "File privacy"):
        if phrase not in schema:
            fail(f"schema reference missing: {phrase}")
    methods_reference = SKILL.parent / "references" / "methods-language-calibration.md"
    if not methods_reference.exists():
        fail(f"missing methods language calibration reference: {methods_reference}")
    methods_text = methods_reference.read_text(encoding="utf-8")
    for phrase in ("annotation", "functionally annotated", "pathway-enrichment", "prioritize candidate", "gene-, tissue-, and pathway-level analyses"):
        if phrase not in methods_text:
            fail(f"methods language reference missing: {phrase}")
    for reference_name, phrases in {
        "writing-first-contract.md": ("Writing-first contract", "formatting_scope: excluded", "argument architecture"),
        "argument-first-reading.md": ("Argument-first full-text reading", "reader_question", "recurring_genre_pattern"),
        "fidelity-first-gate.md": ("Fidelity-first transfer gate", "reject_transfer", "reasoning_gain"),
        "writing-improvement-report.md": ("Writing improvement report", "Manuscript Writing Diagnosis", "Revision Cards"),
    }.items():
        reference_path = SKILL.parent / "references" / reference_name
        if not reference_path.exists():
            fail(f"missing writing-first reference: {reference_path}")
        reference_text = reference_path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in reference_text:
                fail(f"writing-first reference {reference_name} missing: {phrase}")
    options_reference = SKILL.parent / "references" / "writing-options-card.md"
    if not options_reference.exists():
        fail(f"missing writing-options reference: {options_reference}")
    options_text = options_reference.read_text(encoding="utf-8")
    for phrase in ("WRITING_OPTIONS_CARD", "Conservative", "Field-native", "Logic-forward", "RIS action = Optional", "POST_WRITE_AUDIT"):
        if phrase not in options_text:
            fail(f"writing-options reference missing: {phrase}")
    if not re.search(r"\| Source ID \| Zotero key \| DOI/PMID \| Relevance", text):
        fail("missing corpus ledger table")
    if not re.search(r"\| Pattern ID \| Source ID \| Location \| Pattern type", text):
        fail("missing pattern ledger table")
    if "RIS" not in text or "zotero-evidence-review" not in text:
        fail("missing RIS boundary and evidence-review handoff")
    print("✅ literature-learning skill structure and guardrails passed")


if __name__ == "__main__":
    main()
