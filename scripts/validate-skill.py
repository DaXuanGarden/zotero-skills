#!/usr/bin/env python3
"""Statically validate the zotero-evidence-review skill markdown.

This script checks SKILL.md structure, required workflow text, templates,
and safety guards. It does not connect to Zotero or execute PubMed/external
search workflows.
"""

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
REQUIRED_TEMPLATES = (
    "REFS_BLOCK",
    "CLAIM_EVIDENCE_MATRIX",
    "WRITING_SUGGESTIONS_TABLE",
    "DIFF_REVISED_PARAGRAPH",
    "EVIDENCE_REVIEW_REPORT",
    "RIS_REFERENCE_FILE",
    "VERIFICATION_REPORT",
)
REQUIRED_HEADINGS = [
    "## 0. Intent Detection",
    "## 0.5 Library Health Check",
    "## Tool Selection",
    "## Safety Rules",
    "## 1. Semantic + Structured Search",
    "## 1.5 Collection and Tag Search",
    "## 2. Paragraph Evidence & Citation Analysis",
    "## 2.5 Evidence Package Export",
    "## 3. Citation Verification Protocol",
    "## 4. Chinese Academic Writing Rules",
    "## 5. External Source Fallback",
    "## Appendix: Output Templates",
]
EVIDENCE_REPORT_SECTIONS = [
    "## 1. Bottom Line",
    "## 2. Recommended Manuscript Text",
    "## 3. Claim–Evidence Matrix",
    "## 4. Citation Placement",
    "## 5. Reference Table",
    "## 6. Zotero Search Summary",
    "## 7. PubMed Expansion",
    "## 8. Integrated Writing Advice",
    "## 9. Gaps and Reviewer-risk Assessment",
    "## 10. Metadata Quality Control",
    "## 11. Export File",
]
EVIDENCE_PACKAGE_REQUIREMENTS = [
    "zotero-evidence-output/",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris",
    "skill-named, topic-specific output folder",
    "LLM-generated brief topic slug",
    "simple-request entry defaults to the complete workflow",
    "generic literals",
    "emoji-only tags",
    "Evidence source",
    "Zotero + PubMed",
    "RIS standardization source",
    "PMID/PubMed",
    "reference export standardization by PMID/DOI",
    "Zotero local library and PubMed expansion are separate evidence steps",
    "Generated Evidence Package:",
    "zotero://select/items/0_",
    "zotero://open-pdf/library/items/",
    "https://doi.org/",
    "https://pubmed.ncbi.nlm.nih.gov/",
    "⚠️ Tool unavailable; search not executed",
    "Failed; query reported",
    "Possible metadata mismatch",
    "Missing metadata",
    "duplicate warning",
    "metadata quality-control section",
]
RIS_REQUIREMENTS = [
    "TY  - JOUR",
    "TY  -",
    "ER  -",
    "AU  -",
    "N1  - Zotero key:",
    "RIS records only; no Markdown headings, prose, code fences, or comments",
    "PubMed-only records require metadata from an actually completed PubMed search",
]
RIS_ITEM_TYPE_MAPPINGS = [
    "journalArticle` -> `JOUR",
    "book` -> `BOOK",
    "conferencePaper` -> `CONF",
    "preprint` -> `UNPB",
    "report` -> `RPRT",
    "thesis` -> `THES",
    "webpage` -> `ELEC",
    "bookSection` -> `CHAP",
    "dataset` -> `DATA",
    "patent` -> `PAT",
]
DEFAULT_EXPORT_REQUIREMENTS = [
    "Slash command and simple-request entry",
    "/zotero-evidence-review",
    "Paragraph-first, package by default for citation work",
    "使用技能",
    "完整工作流",
    "找引文",
    "补引用",
    "推荐引用",
    "citation",
    "refs",
    "参考文献",
    "文献引用",
    "Chat-only opt-out",
    "只在聊天输出",
    "不要生成文件",
    "不导出",
    "chat only",
    "Module 2 → Module 2.5",
]
UNIFIED_WORKFLOW_REQUIREMENTS = [
    "Paragraph Citation Package Workflow",
    "Module 2 + Module 2.5",
    "automatic PubMed expansion",
    "after Zotero local search",
    "PubMed-capable tool is configured and visible",
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


def extract_template(text: str, template: str) -> str:
    template_names = "|".join(re.escape(name) for name in REQUIRED_TEMPLATES if name != template)
    pattern = rf"^### {re.escape(template)}\n(?P<body>.*?)(?=^### (?:{template_names})\n|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        fail(f"missing appendix template definition: {template}")
    return match.group("body")


def extract_first_code_fence(template_body: str, template: str) -> str:
    match = re.search(r"```\w*\n(?P<body>.*?)(?:\n```)", template_body, flags=re.DOTALL)
    if not match:
        fail(f"{template} must contain a fenced template body")
    return match.group("body")


def require_all(haystack: str, needles: list[str], context: str) -> None:
    missing = [needle for needle in needles if needle not in haystack]
    if missing:
        fail(f"missing {context}: " + ", ".join(missing))


def require_ordered(haystack: str, needles: list[str], context: str) -> None:
    position = -1
    for needle in needles:
        next_position = haystack.find(needle, position + 1)
        if next_position == -1:
            fail(f"missing or out-of-order {context}: {needle}")
        position = next_position


def require_table_header(template: str, header_pattern: str, required_columns: list[str], context: str) -> None:
    match = re.search(header_pattern, template)
    if not match:
        fail(f"missing {context} table header")
    header = match.group(0)
    missing = [column for column in required_columns if column not in header]
    if missing:
        fail(f"missing {context} table column(s): " + ", ".join(missing))


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

    if "## 2.5 Evidence Package Export" not in no_code:
        fail("missing evidence package export module")
    require_all(text, EVIDENCE_PACKAGE_REQUIREMENTS, "evidence package requirement")
    ok("evidence package export requirements present")

    require_all(text, DEFAULT_EXPORT_REQUIREMENTS, "default export routing requirement")
    ok("default citation-support export routing requirements present")

    require_all(text, UNIFIED_WORKFLOW_REQUIREMENTS, "unified paragraph citation workflow requirement")
    ok("unified paragraph citation workflow requirements present")

    require_all(text, RIS_REQUIREMENTS, "RIS requirement")
    require_all(text, RIS_ITEM_TYPE_MAPPINGS, "RIS itemType mapping")
    ok("RIS export requirements present")

    for template in REQUIRED_TEMPLATES:
        if f"### {template}" not in no_code:
            fail(f"missing appendix template definition: {template}")
    ok("appendix template definitions present")

    evidence_report_template = extract_template(text, "EVIDENCE_REVIEW_REPORT")
    require_ordered(evidence_report_template, EVIDENCE_REPORT_SECTIONS, "Evidence Review report section")
    ok("Evidence Review report template sections present and ordered")

    require_table_header(
        evidence_report_template,
        r"\| # \| Citation \| Year \| Study type \| Main use \| Evidence source \| Zotero \| PDF \| DOI \|.*",
        ["DOI", "PMID", "Collection"],
        "Reference Table",
    )
    require_table_header(
        evidence_report_template,
        r"\| Affected claim / sentence \| Risk \| Severity \| Evidence basis \| Suggested fix \|",
        ["Affected claim / sentence", "Risk", "Severity", "Evidence basis", "Suggested fix"],
        "Reviewer-risk",
    )
    require_table_header(
        evidence_report_template,
        r"\| Citation \| Missing metadata \| Metadata mismatch \| Duplicate warning \| Evidence source \| RIS standardization source \| RIS action \|",
        ["Missing metadata", "Metadata mismatch", "Duplicate warning", "Evidence source", "RIS standardization source", "RIS action"],
        "Metadata Quality Control",
    )
    if "Source: Zotero local library; PubMed:" not in evidence_report_template:
        fail("Evidence Review report Source line must expose PubMed execution status")
    if "Not executed" not in evidence_report_template:
        fail("Evidence Review report PubMed status must allow Not executed")
    ok("Evidence Review report table schemas are consistent")

    ris_template = extract_template(text, "RIS_REFERENCE_FILE")
    ris_body = extract_first_code_fence(ris_template, "RIS_REFERENCE_FILE")
    if re.search(r"^#{1,6}\s", ris_body, flags=re.MULTILINE):
        fail("RIS_REFERENCE_FILE fenced body must not contain Markdown headings")
    if "```" in ris_body:
        fail("RIS_REFERENCE_FILE fenced body must not contain nested code fences")
    if not ris_body.lstrip().startswith("TY  -"):
        fail("RIS_REFERENCE_FILE fenced body must start with a RIS TY field")
    if not ris_body.rstrip().endswith("ER  -"):
        fail("RIS_REFERENCE_FILE fenced body must end with ER  -")
    ok("RIS_REFERENCE_FILE template is plain RIS")

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
    print("Static validation only: Zotero/PubMed workflows were not executed.")


if __name__ == "__main__":
    main()
