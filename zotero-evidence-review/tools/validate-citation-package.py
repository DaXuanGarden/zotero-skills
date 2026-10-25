#!/usr/bin/env python3
"""Validate the durable citation handoff added by zotero-evidence-review 3.7.

This is a structural guardrail. It does not judge whether a paper supports a claim;
that remains the job of the evidence matrix and Citation Support Ledger.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys

REQUIRED_SECTIONS = (
    "Metadata and Use Status",
    "Critical Warnings",
    "Copy-ready Manuscript Text",
    "Claim–Evidence Matrix",
    "Citation Insertion Sheet",
    "Annotated Recommended Text",
    "Diff / Change Log",
    "Claim–Evidence Matrix",
    "Citation Placement",
    "Citation Support Ledger",
    "Metadata Quality Control",
    "Export File",
)
INSERTION_FIELDS = (
    "sentence_id",
    "insertion_anchor",
    "copy_ready_citation",
    "search_tokens",
    "canonical_record",
    "PMID",
    "DOI",
    "evidence_role",
    "support_verdict",
    "RIS_action",
)
DIFF_FIELDS = (
    "sentence_id",
    "original_phrase",
    "revised_phrase",
    "change_type",
    "reason",
    "evidence_level",
    "citation_effect",
)
MATRIX_FIELDS = (
    "sentence_id",
    "claim_id",
    "Revised sentence / clause",
    "主张摘要（中文）",
    "Recommended citation",
    "Evidence role",
    "Evidence level",
    "Source layer",
    "Support verdict",
    "insertion_anchor",
    "Manual action",
)
COMPOUND_LEVEL_RE = re.compile(r"(?<![A-Za-z])(?:A/B|A/C|B/C|C/D|D/E)(?![A-Za-z])")


def section_present(text: str, name: str) -> bool:
    return name in text


def validate_report(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for name in REQUIRED_SECTIONS:
        if not section_present(text, name):
            errors.append(f"missing report section: {name}")
    for field in INSERTION_FIELDS:
        if f"`{field}`" not in text and field not in text:
            errors.append(f"missing insertion-sheet field: {field}")
    for field in DIFF_FIELDS:
        if field not in text:
            errors.append(f"missing diff/change-log field: {field}")
    matrix_heading = re.search(r"^##\s+.*Claim[–-]Evidence Matrix.*$", text, flags=re.MULTILINE | re.IGNORECASE)
    if not matrix_heading:
        errors.append("missing Claim–Evidence Matrix heading")
    else:
        matrix_block = text[matrix_heading.end():]
        next_heading = re.search(r"^##\s+", matrix_block, flags=re.MULTILINE)
        if next_heading:
            matrix_block = matrix_block[: next_heading.start()]
        header_line = next((line for line in matrix_block.splitlines() if line.strip().startswith("|") and line.strip().endswith("|")), "")
        for field in MATRIX_FIELDS:
            if field not in header_line:
                errors.append(f"missing claim-matrix field: {field}")
        if COMPOUND_LEVEL_RE.search(matrix_block):
            errors.append("claim matrix contains compound evidence level; use exactly one A-E level per row")
    if re.search(r"/(?:Users|home|private)/", text):
        errors.append("report contains an absolute local path")
    if "Citation Insertion Sheet" in text and "Author–Year Quick Lookup" not in text:
        errors.append("missing Author–Year Quick Lookup")
    return errors


def validate_ris(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not text.strip():
        return ["RIS is empty"]
    if "```" in text or re.search(r"^#{1,6} ", text, re.MULTILINE):
        errors.append("RIS contains Markdown prose")
    records = [chunk.strip() for chunk in re.split(r"(?=^TY  - )", text, flags=re.MULTILINE) if chunk.strip()]
    if not records:
        return ["RIS contains no TY records"]
    for i, record in enumerate(records, 1):
        if not record.startswith("TY  - "):
            errors.append(f"RIS record {i} does not start with TY  -")
        if not record.rstrip().endswith("ER  -"):
            errors.append(f"RIS record {i} does not end with ER  -")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--ris", type=Path)
    args = parser.parse_args()
    errors = validate_report(args.report)
    if args.ris:
        errors.extend(validate_ris(args.ris))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    print(f"- report: {args.report}")
    if args.ris:
        print(f"- ris: {args.ris}")
    print("- citation handoff structure and RIS envelope validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
