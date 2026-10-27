#!/usr/bin/env python3
"""Validate the evidence-bound manuscript polishing contract and fixture."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "zotero-manuscript-thinking" / "SKILL.md"
REFERENCE = ROOT / "zotero-manuscript-thinking" / "references" / "polish-quality-gate.md"
FIXTURE = ROOT / "scripts" / "fixtures" / "polish_quality_gate_sample.json"

REQUIRED_SKILL_PHRASES = (
    "version: 0.7.0",
    "polish-quality-gate.md",
    "academic-introduction-polisher",
    "academic-discussion-polisher",
    "medical-english-precision-editor",
    "academic-reference-matcher",
    "academic-ref-check",
    "POST_WRITE_AUDIT",
    "claim_unchanged: yes",
    "numbers_units_direction_unchanged: yes",
    "citation_ownership_preserved: yes",
    "new_unsupported_claim: no",
)

REQUIRED_REFERENCE_PHRASES = (
    "# Evidence-bound Polish Quality Gate",
    "Gate A — Meaning gate",
    "Gate B — Section-logic gate",
    "Gate C — Field-native gate",
    "Gate D — Language-precision gate",
    "Gate E — Evidence and reviewer-risk gate",
    "accepted: pass | revise | author_review",
    "with an evidence-boundary failure is rejected",
)


def fails_acceptance(case: dict[str, object]) -> bool:
    return any(
        (
            case.get("meaning_gate") == "fail",
            case.get("section_logic_gate") == "fail",
            case.get("language_precision_gate") == "fail",
            case.get("evidence_boundary_gate") == "fail",
            case.get("claim_unchanged") == "no",
            case.get("numbers_units_direction_unchanged") == "no",
            case.get("citation_ownership_preserved") == "no",
            case.get("new_unsupported_claim") == "yes",
        )
    )


def fail(message: str) -> None:
    print(f"❌ {message}")
    raise SystemExit(1)


def main() -> None:
    if not SKILL.exists() or not REFERENCE.exists() or not FIXTURE.exists():
        fail("skill, quality-gate reference, or fixture is missing")

    skill_text = SKILL.read_text(encoding="utf-8")
    reference_text = REFERENCE.read_text(encoding="utf-8")
    for phrase in REQUIRED_SKILL_PHRASES:
        if phrase not in skill_text:
            fail(f"manuscript-thinking skill missing: {phrase}")
    for phrase in REQUIRED_REFERENCE_PHRASES:
        if phrase not in reference_text:
            fail(f"quality-gate reference missing: {phrase}")

    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) < 2:
        fail("fixture must contain at least a passing and a rejecting case")
    by_name = {case.get("name"): case for case in cases if isinstance(case, dict)}
    passing = by_name.get("clean_pass")
    rejecting = by_name.get("rejects_overclaim")
    if not passing or not rejecting:
        fail("fixture must include clean_pass and rejects_overclaim")
    if passing.get("accepted") != "pass" or fails_acceptance(passing):
        fail("clean_pass fixture does not satisfy the acceptance gate")
    if rejecting.get("accepted") == "pass" or not fails_acceptance(rejecting):
        fail("rejects_overclaim fixture is not rejected by the acceptance gate")
    print("✅ polish quality gate contract and fixture passed")


if __name__ == "__main__":
    main()
