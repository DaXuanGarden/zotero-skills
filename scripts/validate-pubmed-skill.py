#!/usr/bin/env python3
"""Statically validate the pubmed-literature-search skill markdown.

This script checks SKILL.md structure, PubMed MCP tool references, output
templates, and safety guards. It does not connect to PubMed or execute NCBI
search workflows.
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - fallback for minimal environments
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "pubmed-literature-search" / "SKILL.md"

REQUIRED_HEADINGS = [
    "## 0. Intent Detection",
    "## 0.25 PubMed MCP Readiness and Runtime Availability",
    "## 0.5 PubMed MCP Health Check",
    "## Tool Selection",
    "## Safety Rules",
    "## 1. PubMed Search Workflow",
    "## 2. PMID Metadata Inspection",
    "## 3. Related and Review Expansion",
    "## 4. OA Full-text Triage",
    "## 5. PubMed Review Package Export",
    "## Appendix: Output Templates",
]

PUBMED_TOOL_REQUIREMENTS = [
    "pubmed_search",
    "pubmed_get_details",
    "pubmed_extract_info",
    "pubmed_find_related",
    "pubmed_detect_fulltext",
    "pubmed_download_fulltext",
    "pubmed_system_status",
    "pubmed_manage_cache",
]

PUBMED_GUARDRAIL_REQUIREMENTS = [
    "⚠️ Tool unavailable; search not executed",
    "Failed; query reported",
    "Not executed",
    "Only actual PubMed execution plus inspected metadata can justify `Completed`",
    "Tool visibility alone is not enough",
    "PubMed-only RIS records",
    "Do not treat Zotero MCP as PubMed MCP",
]

PUBMED_SEQUENTIAL_GUARDRAIL_REQUIREMENTS = [
    "Sequential Execution Guardrail",
    "dependency chains, not batch jobs",
    "Do not schedule `pubmed_search` in the same tool-call batch as downstream tools",
    "Run one PubMed step, inspect its result",
    "stop the PubMed chain immediately",
    "do not schedule dependent details, related, full-text, export, or PubMed-only RIS steps",
    "retry the query at most once",
    "do not fabricate PMIDs or continue to metadata inspection",
]

OUTPUT_REQUIREMENTS = [
    "pubmed-literature-output/",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_pubmed_review.md",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris",
    "Generated PubMed Literature Package:",
    "Critical Warnings:",
    "PUBMED_REVIEW_REPORT",
    "RIS_REFERENCE_FILE",
]

REPORT_SECTIONS = [
    "## 1. Metadata and Use Status",
    "## 2. Critical Warnings",
    "## 3. Search Reproducibility",
    "## 4. Included Studies",
    "## 5. Related and Review Expansion",
    "## 6. Metadata Quality Control",
    "## 7. Export Files",
]

PMID_INSPECTION_LEDGER_HEADER = (
    "| PMID | Citation | Inspection status | Inspection tool / route | Inspected fields | "
    "DOI | Abstract status | Retraction / metadata warning | Evidence use | RIS action |"
)
PMID_INSPECTION_LEDGER_REQUIREMENTS = [
    "PMID Inspection Ledger",
    "Inspection status",
    "Inspection tool / route",
    "Inspected fields",
    "Abstract status",
    "Retraction / metadata warning",
    "Evidence use",
    "RIS action",
    "completed",
    "partial",
    "not inspected",
    "failed",
    "pubmed_get_details",
    "pubmed_extract_info",
    "equivalent visible PubMed metadata tooling",
    "search snippets alone are insufficient",
    "Only PMIDs with `Inspection status = completed`",
    "may use `RIS action = include`",
    "not inspected`, `partial`, `failed`",
]

RIS_REQUIREMENTS = [
    "RIS records only; no Markdown headings, prose, comments, or code fences",
    "TY  - JOUR",
    "AU  -",
    "TI  -",
    "JO  -",
    "PY  -",
    "DO  -",
    "UR  - https://pubmed.ncbi.nlm.nih.gov/{PMID}/",
    "N1  - PMID: {PMID}",
    "ER  -",
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


def normalize_dependency(value: object) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {part.strip() for part in re.split(r"[,;]", value) if part.strip()}
    if isinstance(value, (list, tuple, set)):
        return {str(part).strip() for part in value if str(part).strip()}
    return {str(value).strip()}


def strip_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


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


def extract_template(text: str, template: str) -> str:
    pattern = rf"^### {re.escape(template)}\n(?P<body>.*?)(?=^### [A-Z_]+\n|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        fail(f"missing appendix template definition: {template}")
    return match.group("body")


def main() -> None:
    if not SKILL_PATH.exists():
        fail(f"Missing skill file: {SKILL_PATH}")

    text = SKILL_PATH.read_text(encoding="utf-8")
    no_code = strip_code_fences(text)

    frontmatter = parse_frontmatter(text)
    if frontmatter.get("name") != "pubmed-literature-search":
        fail("frontmatter name must be pubmed-literature-search")
    if "zcode" not in str(frontmatter.get("compatibility", "")):
        fail("frontmatter compatibility must include zcode")
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict) or not metadata.get("version"):
        fail("frontmatter metadata.version is required")
    requires = normalize_dependency(metadata.get("requires"))
    optional = normalize_dependency(metadata.get("optional"))
    if "pubmed-mcp" not in requires:
        fail("frontmatter metadata.requires must include pubmed-mcp")
    if "zotero-mcp" not in optional:
        fail("frontmatter metadata.optional must include zotero-mcp")
    ok(f"frontmatter parsed; version {metadata['version']}; dependencies declared")

    fence_count = text.count("```")
    if fence_count % 2 != 0:
        fail(f"unbalanced markdown code fences: {fence_count}")
    ok(f"markdown code fences balanced: {fence_count}")

    require_ordered(no_code, REQUIRED_HEADINGS, "workflow heading")
    ok("required workflow headings present and ordered")

    require_all(text, PUBMED_TOOL_REQUIREMENTS, "PubMed tool requirement")
    require_all(text, PUBMED_GUARDRAIL_REQUIREMENTS, "PubMed guardrail requirement")
    require_all(text, PUBMED_SEQUENTIAL_GUARDRAIL_REQUIREMENTS, "PubMed sequential execution guardrail")
    ok("PubMed tool and guardrail requirements present")

    require_all(text, OUTPUT_REQUIREMENTS, "output requirement")
    require_all(text, PMID_INSPECTION_LEDGER_REQUIREMENTS, "PMID Inspection Ledger requirement")
    ok("PubMed package output and PMID Inspection Ledger requirements present")

    report_template = extract_template(text, "PUBMED_REVIEW_REPORT")
    require_ordered(report_template, REPORT_SECTIONS, "PubMed review report section")
    require_all(
        report_template,
        [
            "| Source | Query | Sort | Max results | Status | Hits reviewed | Selected PMIDs |",
            "| Priority | Citation | PMID | DOI | Study type | Main finding/use | Caveat |",
            PMID_INSPECTION_LEDGER_HEADER,
            "| PMID | DOI | Title check | Authors check | Year check | Metadata warning | RIS action |",
        ],
        "PubMed report table schema",
    )
    ok("PubMed review report template sections and tables present")

    ris_template = extract_template(text, "RIS_REFERENCE_FILE")
    require_all(ris_template, RIS_REQUIREMENTS, "RIS requirement")
    if "```ris" not in ris_template:
        fail("RIS_REFERENCE_FILE must contain a RIS fenced template body")
    ok("RIS_REFERENCE_FILE template is plain RIS")

    print("\nAll PubMed skill validations passed.")
    print("Static validation only: PubMed workflows were not executed.")


if __name__ == "__main__":
    main()
