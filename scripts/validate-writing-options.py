#!/usr/bin/env python3
"""Validate the shared multi-option writing contract and fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATHS = [
    ROOT / "zotero-evidence-review/references/writing-options-card.md",
    ROOT / "zotero-literature-learning/references/writing-options-card.md",
    ROOT / "zotero-manuscript-thinking/references/writing-options-card.md",
]
FIXTURE = ROOT / "scripts/fixtures/writing_options_card_sample.json"
REQUIRED_PHRASES = (
    "WRITING_OPTIONS_CARD",
    "meaning gate",
    "option_id",
    "rhetorical_angle",
    "claim_delta",
    "evidence_level",
    "citation_set",
    "selection_status",
    "Conservative",
    "Field-native",
    "Logic-forward",
    "Introduction",
    "Methods",
    "Results",
    "Discussion",
    "RIS action = Include",
    "RIS action = Optional",
    "POST_WRITE_AUDIT",
    "Peer papers provide abstracted writing patterns",
)
OPTION_FIELDS = {
    "option_id",
    "option_name",
    "rhetorical_angle",
    "target_section",
    "rhetorical_job",
    "copy_ready_text",
    "claim_delta",
    "evidence_level",
    "citation_set",
    "style_basis",
    "why_this_works",
    "when_to_choose",
    "risks",
    "author_check",
}


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def main() -> None:
    for path in REFERENCE_PATHS:
        if not path.exists():
            fail(f"writing-options reference missing: {path}")
    texts = [path.read_text(encoding="utf-8") for path in REFERENCE_PATHS]
    digests = {hashlib.sha256(text.encode("utf-8")).hexdigest() for text in texts}
    if len(digests) != 1:
        fail("writing-options references have drifted; keep the three copies identical")
    for phrase in REQUIRED_PHRASES:
        if phrase not in texts[0]:
            fail(f"shared writing-options reference missing: {phrase}")
    if not FIXTURE.exists():
        fail(f"fixture missing: {FIXTURE}")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for key in ("task_id", "input_scope", "target_section", "corpus_status", "calibration_confidence", "selection_status", "options"):
        if key not in data:
            fail(f"fixture missing top-level key: {key}")
    if not 2 <= len(data["options"]) <= 3:
        fail("fixture must contain two or three options")
    ids = set()
    for option in data["options"]:
        missing = OPTION_FIELDS - set(option)
        if missing:
            fail(f"fixture option missing fields: {sorted(missing)}")
        if option["option_id"] in ids:
            fail(f"duplicate option_id: {option['option_id']}")
        ids.add(option["option_id"])
        if option["evidence_level"] not in {"A", "B", "C", "D", "E"}:
            fail(f"invalid evidence level: {option['evidence_level']}")
    print("✅ shared writing-options contract and fixture passed")


if __name__ == "__main__":
    main()
