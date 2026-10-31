#!/usr/bin/env python3
"""Validate the writing-first and fidelity-first contracts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zotero-literature-learning" / "SKILL.md"
FIXTURE = ROOT / "scripts/fixtures/writing_improvement_report_sample.json"

REQUIRED_FILES = (
    ROOT / "zotero-literature-learning/references/writing-first-contract.md",
    ROOT / "zotero-literature-learning/references/argument-first-reading.md",
    ROOT / "zotero-literature-learning/references/fidelity-first-gate.md",
    ROOT / "zotero-literature-learning/references/writing-improvement-report.md",
)

REQUIRED_SKILL_PHRASES = (
    "写作优先边界",
    "Argument-first 全文阅读",
    "当前手稿映射",
    "目标期刊模式迁移门禁",
    "Writing Reasoning Profile",
    "writing_improvement_report.md",
    "transfer_scope",
    "reject_transfer",
    "不做格式审查",
)


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def main() -> None:
    if not SKILL.exists():
        fail(f"skill file missing: {SKILL}")
    skill_text = SKILL.read_text(encoding="utf-8")
    for phrase in REQUIRED_SKILL_PHRASES:
        if phrase not in skill_text:
            fail(f"SKILL.md missing writing-first phrase: {phrase}")

    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"writing-first reference missing: {path}")

    if not FIXTURE.exists():
        fail(f"fixture missing: {FIXTURE}")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for key in ("mode", "target_section", "corpus_status", "calibration_confidence", "revision_cards"):
        if key not in fixture:
            fail(f"fixture missing top-level key: {key}")
    if not fixture["revision_cards"]:
        fail("fixture must contain at least one revision card")

    required_card_fields = {
        "revision_id",
        "draft_segment_id",
        "rhetorical_job",
        "target_reader_question",
        "current_reader_problem",
        "recommended_writing_action",
        "before",
        "after_options",
        "reasoning_gain",
        "source_pattern_ids",
        "transfer_scope",
        "claim_delta",
        "priority",
        "evidence_level",
        "risk",
        "author_check",
        "selection_status",
    }
    valid_scopes = {"preserve", "adapt", "author_decide", "reject_transfer"}
    valid_statuses = {"pending", "selected", "rejected"}
    valid_priorities = {"P0", "P1", "P2"}
    valid_evidence_levels = {"A", "B", "C", "D", "E"}
    for card in fixture["revision_cards"]:
        missing = required_card_fields - set(card)
        if missing:
            fail(f"revision card missing fields: {sorted(missing)}")
        if card["transfer_scope"] not in valid_scopes:
            fail(f"invalid transfer_scope: {card['transfer_scope']}")
        if card["selection_status"] not in valid_statuses:
            fail(f"invalid selection_status: {card['selection_status']}")
        if card["priority"] not in valid_priorities:
            fail(f"invalid revision priority: {card['priority']}")
        if card["evidence_level"] not in valid_evidence_levels:
            fail(f"invalid revision evidence level: {card['evidence_level']}")
        if not isinstance(card["after_options"], list):
            fail("revision after_options must be a list")
        if not card["source_pattern_ids"] and card["transfer_scope"] == "adapt":
            fail("adapted revision must cite source_pattern_ids")

    print("✅ writing-first and fidelity-first contracts passed")


if __name__ == "__main__":
    main()
