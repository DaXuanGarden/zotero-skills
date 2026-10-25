#!/usr/bin/env python3
"""Validate the sentence-level citation matrix contract.

This validator is deliberately source-agnostic: it checks the structured matrix
that a paragraph evidence package should be able to expose, without calling
Zotero or PubMed. It catches missing sentence coverage, broken claim links, and
unsafe RIS actions before a Markdown/RIS package is presented to the author.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "scripts" / "fixtures" / "sentence_citation_matrix_sample.json"

ALLOWED_NEEDS = {
    "citation_required",
    "citation_optional",
    "current_study",
    "common_knowledge",
    "interpretive_bridge",
    "unsupported",
}
ALLOWED_LAYERS = {
    "Current study",
    "Zotero external evidence",
    "PubMed external evidence",
    "Interpretive bridge",
    "Unsupported gap",
}
ALLOWED_LEVELS = {"A", "B", "C", "D", "E"}
ALLOWED_VERDICTS = {
    "supports",
    "partly supports",
    "background only",
    "contradicts",
    "not addressed",
    "not inspected",
}
ALLOWED_RIS = {"Include", "Optional", "Exclude", "Verify"}
UNSAFE_VERDICTS = {"contradicts", "not addressed", "not inspected"}


def fail(message: str) -> None:
    raise SystemExit(f"❌ {message}")


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"matrix input missing: {path}")
    except json.JSONDecodeError as exc:
        fail(f"matrix input is not valid JSON: {exc}")
    if not isinstance(data, dict):
        fail("matrix input must be a JSON object")
    return data


def validate(data: dict) -> None:
    if not data.get("paragraph_id"):
        fail("paragraph_id is required")
    sentences = data.get("sentences")
    if not isinstance(sentences, list) or not sentences:
        fail("sentences must be a non-empty list")

    sentence_ids: list[str] = []
    claim_ids: set[str] = set()
    computed = {
        "input_sentences": len(sentences),
        "citation_required": 0,
        "citation_required_covered": 0,
        "current_study": 0,
        "optional_or_common_or_bridge": 0,
        "unsupported_or_verify": 0,
    }

    for index, sentence in enumerate(sentences, start=1):
        if not isinstance(sentence, dict):
            fail(f"sentence {index} must be an object")
        required = {
            "sentence_id",
            "original_sentence",
            "claim_ids",
            "citation_need",
            "source_layer",
            "evidence_level",
            "recommended_citations",
            "support_verdict",
            "evidence_location",
            "wording_action",
            "ris_action",
            "author_check",
        }
        missing = sorted(required - set(sentence))
        if missing:
            fail(f"sentence {index} missing fields: {', '.join(missing)}")

        sentence_id = str(sentence["sentence_id"])
        if not re.fullmatch(r"S\d{2,}", sentence_id):
            fail(f"invalid sentence_id {sentence_id!r}; use S01, S02, ...")
        sentence_ids.append(sentence_id)
        claim_list = sentence["claim_ids"]
        if not isinstance(claim_list, list) or not claim_list or not all(str(item).strip() for item in claim_list):
            fail(f"{sentence_id} must contain one or more claim_ids")
        claim_ids.update(str(item) for item in claim_list)

        need = sentence["citation_need"]
        if need not in ALLOWED_NEEDS:
            fail(f"{sentence_id} has invalid citation_need: {need}")
        layer = sentence["source_layer"]
        if layer not in ALLOWED_LAYERS:
            fail(f"{sentence_id} has invalid source_layer: {layer}")
        level = sentence["evidence_level"]
        if level not in ALLOWED_LEVELS:
            fail(f"{sentence_id} has invalid evidence_level: {level}")
        verdict = str(sentence["support_verdict"]).lower()
        if verdict not in ALLOWED_VERDICTS:
            fail(f"{sentence_id} has invalid support_verdict: {verdict}")
        ris_action = sentence["ris_action"]
        if ris_action not in ALLOWED_RIS:
            fail(f"{sentence_id} has invalid RIS action: {ris_action}")
        if not str(sentence["evidence_location"]).strip():
            fail(f"{sentence_id} must state an evidence_location or 'none'")
        if verdict in UNSAFE_VERDICTS and ris_action == "Include":
            fail(f"{sentence_id} has unsafe verdict {verdict!r} with RIS action Include")

        citations = sentence["recommended_citations"]
        if not isinstance(citations, list):
            fail(f"{sentence_id}.recommended_citations must be a list")
        has_eligible_citation = bool(citations) and ris_action in {"Include", "Optional"} and verdict not in UNSAFE_VERDICTS
        if need == "citation_required":
            computed["citation_required"] += 1
            if has_eligible_citation:
                computed["citation_required_covered"] += 1
            elif ris_action not in {"Exclude", "Verify"} or verdict not in UNSAFE_VERDICTS:
                fail(f"{sentence_id} is citation_required without an eligible citation or explicit gap decision")
        elif need == "current_study":
            computed["current_study"] += 1
        else:
            computed["optional_or_common_or_bridge"] += 1
        if need == "unsupported" or ris_action == "Verify":
            computed["unsupported_or_verify"] += 1

    if len(set(sentence_ids)) != len(sentence_ids):
        fail("sentence_id values must be unique")
    expected_ids = [f"S{index:02d}" for index in range(1, len(sentences) + 1)]
    if sentence_ids != expected_ids:
        fail(f"sentence_id values must preserve order: expected {expected_ids}, got {sentence_ids}")

    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        fail("coverage must be an object")
    for key, value in computed.items():
        if coverage.get(key) != value:
            fail(f"coverage.{key}={coverage.get(key)!r} does not match computed value {value}")
    unmapped_claims = coverage.get("unmapped_claims")
    orphan_ris = coverage.get("orphan_ris_candidates")
    if not isinstance(unmapped_claims, list) or not isinstance(orphan_ris, list):
        fail("coverage.unmapped_claims and coverage.orphan_ris_candidates must be lists")
    if unmapped_claims:
        fail("unmapped_claims must be empty in a valid matrix fixture")
    if orphan_ris:
        fail("orphan_ris_candidates must be empty; every RIS record needs a sentence/claim trace")
    status = coverage.get("status")
    if status not in {"complete", "partial", "blocked", "not_applicable"}:
        fail(f"invalid coverage.status: {status}")
    expected_status = "complete" if computed["citation_required"] == computed["citation_required_covered"] and not computed["unsupported_or_verify"] else "partial"
    if status != expected_status:
        fail(f"coverage.status={status!r} does not match expected {expected_status!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a structured sentence-level citation matrix")
    parser.add_argument("--input", default=str(DEFAULT_FIXTURE), help="JSON matrix to validate")
    args = parser.parse_args()
    validate(load(Path(args.input)))
    print("✅ sentence-level citation matrix contract and fixture passed")


if __name__ == "__main__":
    main()
