#!/usr/bin/env python3
"""Validate the manuscript-level thinking companion skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zotero-manuscript-thinking" / "SKILL.md"

REQUIRED_HEADINGS = [
    "# Zotero Manuscript Thinking",
    "## 1. 何时触发",
    "## 2. 输入与范围门禁",
    "### 2.1A 领域地道语言与目标语料校准",
    "## 2.4 Methods 逻辑协议",
    "## 2.5 Results 逻辑协议",
    "## 3. 思考路由：先选一个主模型",
    "## 4. 统一执行流程",
    "## 5. 输出契约",
    "## 6. 与现有 Zotero 工作流的交接",
    "## 7. 安全与质量门",
    "## 9. 结束条件",
]

REQUIRED_PHRASES = [
    "thinking-model-router",
    "thinking-systems",
    "thinking-first-principles",
    "thinking-steel-manning",
    "thinking-socratic",
    "thinking-model-combination",
    "Current study",
    "Zotero external evidence",
    "PubMed external evidence",
    "Interpretive bridge",
    "Unsupported gap",
    "A–E",
    "P0",
    "P1",
    "P2",
    "P3",
    "MANUSCRIPT_STRATEGIC_REVIEW",
    "scope-limited checkpoint",
    "不编造",
    "paper-claim-audit",
    "revision-strategy-planner",
    "writing-core",
    "medical-english-precision-editor",
    "academic-introduction-polisher",
    "academic-discussion-polisher",
    "methods-section-writer",
    "method-writing",
    "methods-reverse-engineer",
    "results-section-structurer",
    "results-section-revision",
    "result-figure-consistencycheck",
    "Methods Logic Map",
    "Results Logic Map",
    "reproducibility",
    "quantitative anchor",
    "Methods–Results",
    "Language Audit",
    "Introduction Logic Map",
    "Discussion Logic Map",
    "meaning gate",
    "Domain Style Calibration",
    "style_corpus_ledger",
    "calibration_confidence",
    "do_not_adopt",
    "不复制原文",
    "zotero_semantic_search",
    "zotero_read_pdf_pages",
    "Zotero Style Evidence Ledger",
    "metadata-only",
    "WRITING_BLOCK_LEARNING",
    "zotero-literature-learning",
    "evidence-driven-writing",
    "writing_block",
    "修订顺序：先保意义，再校准领域语言",
    "meaning gate",
    "POST_WRITE_AUDIT",
    "Revision Decision Log",
    "annotation",
    "gene-, tissue-, and pathway-level analyses",
    "WRITING_OPTIONS_CARD",
    "selection_status: pending",
    "claim_delta",
]


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def main() -> None:
    if not SKILL.exists():
        fail(f"skill file missing: {SKILL}")
    text = SKILL.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "name: zotero-manuscript-thinking" not in text:
        fail("frontmatter does not declare zotero-manuscript-thinking")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            fail(f"missing heading: {heading}")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            fail(f"missing required guardrail or workflow phrase: {phrase}")
    if "不自动改写整篇论文" not in text or "不自动承诺新实验" not in text:
        fail("missing non-destructive scope boundary")
    reference = SKILL.parent / "references" / "domain-style-calibration.md"
    if not reference.exists():
        fail(f"missing domain style calibration reference: {reference}")
    reference_text = reference.read_text(encoding="utf-8")
    for phrase in (
        "peer corpus",
        "calibration_confidence",
        "Extract patterns, not prose",
        "do_not_adopt",
        "zotero_get_item_metadata",
        "zotero_get_pdf_outline",
        "zotero_read_pdf_pages",
        "Short source fragment",
    ):
        if phrase not in reference_text:
            fail(f"domain style calibration reference missing: {phrase}")
    options_reference = SKILL.parent / "references" / "writing-options-card.md"
    if not options_reference.exists():
        fail(f"missing writing-options reference: {options_reference}")
    options_text = options_reference.read_text(encoding="utf-8")
    for phrase in ("WRITING_OPTIONS_CARD", "Conservative", "Field-native", "Logic-forward", "RIS action = Include", "POST_WRITE_AUDIT"):
        if phrase not in options_text:
            fail(f"writing-options reference missing: {phrase}")
    if "scope-limited checkpoint" not in text or "files_not_read" not in text:
        fail("missing incomplete-input reporting")
    if not re.search(r"\| ID \| Location \| Problem \| Evidence / basis \| Risk \| Leverage \| Priority \| Action type \| Next owner \| Done when \|", text):
        fail("missing prioritized diagnosis table")
    print("✅ manuscript-level thinking skill structure and guardrails passed")


if __name__ == "__main__":
    main()
