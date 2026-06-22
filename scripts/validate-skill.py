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
    "## 0. Durable Output Language Policy",
    "## 0.25 MCP Readiness and Runtime Availability",
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
    "## 1. Metadata and Use Status",
    "## 2. Critical Warnings",
    "## 3. 核心结论（Bottom Line）",
    "## 4. 可直接使用的稿件文本（Copy-ready Manuscript Text）",
    "## 5. 注释版推荐文本（Annotated Recommended Text）",
    "## 6. 主张—证据矩阵（Claim–Evidence Matrix）",
    "## 7. 引文放置建议（Citation Placement）",
    "## 8. Evidence Logic Chain",
    "## 9. 参考文献表（Reference Table）",
    "## 10. Search Reproducibility",
    "## 11. Zotero 检索总结（Zotero Search Summary）",
    "## 12. PubMed 扩展检索（PubMed Expansion）",
    "## 13. 综合写作建议（Integrated Writing Advice）",
    "## 14. Claims to Revise or Remove",
    "## 15. 证据缺口与审稿风险（Gaps and Reviewer-risk Assessment）",
    "## 16. 元数据质量控制（Metadata Quality Control）",
    "## 17. 导出文件（Export File）",
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
    "reference_update",
    "检查参考文献",
    "更新参考文献",
    "编号引用",
    "6不支持",
    "citation 6 does not support",
    "replace citation",
    "refresh RIS",
    "regenerate RIS",
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
NUMBERED_CITATION_REPAIR_REQUIREMENTS = [
    "Existing numbered citation repair first",
    "Module 2.2: Existing Numbered Citation Repair",
    "citation number → supplied reference metadata → claim",
    "Keep",
    "Replace",
    "Remove",
    "Verify",
    "Add supporting citation",
    "reference-update workflow",
    "Claim supported by this number",
    "Support verdict",
    "Original citation number preserved for audit",
    "Final numbering handled by EndNote/Word",
    "Replacement candidate",
    "RIS action",
    "unsupported numbered citation",
    "EndNote/Word will renumber",
    "6 = Wang et al. 2022 Nat Genet physical activity/sedentary behavior GWAS",
    "LST directionally contributes to PCOS susceptibility",
    "Several genetic observations were consistent with",
    "weak opening",
    "current-study framing",
]
UNIFIED_WORKFLOW_REQUIREMENTS = [
    "Paragraph Citation Package Workflow",
    "Module 2 + Module 2.5",
    "automatic PubMed expansion",
    "after Zotero local search",
    "PubMed-capable tool is configured and visible",
]
MCP_READINESS_REQUIREMENTS = [
    "MCP Readiness and Runtime Availability",
    "metadata.requires: zotero-mcp",
    "metadata.optional: pubmed-mcp",
    "static validator can only inspect this Markdown specification",
    "does not connect to Zotero",
    "does not execute PubMed",
    "Zotero is not PubMed",
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
    "PubMed-only records only when PubMed status is `Completed`",
]

PUBMED_SEQUENTIAL_GUARDRAIL_REQUIREMENTS = [
    "PubMed Sequential Execution Guardrail",
    "Zotero local search and PubMed expansion as separate evidence phases",
    "dependency chain, not a batch job",
    "do not schedule `pubmed_search` in the same tool-call batch as downstream tools",
    "Run one PubMed step, inspect its result",
    "stop the PubMed chain immediately",
    "PubMed-only records must not be added to RIS unless PubMed status is `Completed`",
    "retry the query at most once",
    "do not fabricate PMIDs or continue to PubMed metadata inspection",
]

PHASE10_REQUIREMENTS = [
    "### Evidence Package Status",
    "Ready",
    "Caution",
    "Partial",
    "Superseded",
    "Unknown",
    "Generated Evidence Package:",
    "- Status:",
    "- Markdown report:",
    "- EndNote RIS:",
    "Critical Warnings:",
    "Evidence Logic Chain",
    "Claims to Revise or Remove",
    "Recommended action",
    "Recommended citation",
]
CLAIM_EVIDENCE_MATRIX_HEADER = (
    "| # | Claim | Source layer | Evidence level | Zotero evidence | PubMed evidence | "
    "Evidence status | Confidence | Risk | Recommended action | Recommended citation |"
)
NUMBERED_CITATION_REPAIR_HEADER = (
    "| Original citation number | Supplied reference | Claim supported by this number | "
    "Support verdict | Verification verdict | Evidence level | "
    "Action: Keep / Replace / Remove / Verify / Add supporting citation | Replacement candidate | "
    "Original citation number preserved for audit | Final numbering handled by EndNote/Word | RIS action | Reason |"
)
CITATION_SUPPORT_LEDGER_REQUIREMENTS = [
    "Citation Support Ledger",
    "Claim / sentence",
    "Recommended citation",
    "Source layer",
    "Evidence level",
    "Inspection route",
    "Evidence location",
    "Support verdict",
    "RIS action",
    "Required wording/action",
    "Zotero metadata",
    "Zotero full text",
    "Zotero abstract",
    "PubMed details",
    "PubMed abstract",
    "Not inspected",
    "supports",
    "partly supports",
    "background only",
    "contradicts",
    "not addressed",
    "not inspected",
    "not inspected`, `contradicts`, and `not addressed` must not enter RIS by default",
    "Existing Numbered Citation Repair rows must propagate",
]
CITATION_SUPPORT_LEDGER_HEADER = (
    "| Claim / sentence | Recommended citation | Source layer | Evidence level | "
    "Inspection route | Evidence location | Support verdict | RIS action | Required wording/action |"
)
QA_SELF_CHECK_REQUIREMENTS = [
    "Evidence Package QA Self-Check Prompt",
    "Run pre-write QA self-check, then write the two files",
    "Pre-write QA gate checklist",
    "Post-write QA gate",
    "Report 是否包含 Status、Critical Warnings、Copy-ready Manuscript Text",
    "Claim–Evidence Matrix 是否包含 Evidence level 和 Source layer",
    "Citation Support Ledger 是否覆盖所有推荐引文/RIS候选",
    "not inspected / contradicts / not addressed 的 citation ledger 行是否被排除出 RIS 或标记 Verify",
    "current-study finding 错写成 external evidence",
    "direct causality、BMI independence、horizontal pleiotropy",
    "PubMed status 是否真实反映工具执行情况",
    "PubMed-only RIS 是否只来自 completed PubMed search",
    "unresolved metadata mismatch 是否被排除出 RIS",
    "RIS 是否无 Markdown heading/code fence",
    "所有路径是否为相对路径",
    "最终 chat 只显示 status、paths 和 critical warnings",
    "Final response hygiene",
    "final chat exposes only status, relative paths, and critical warnings",
    "PubMed status truthfully reflects tool execution",
    "PubMed-only RIS records are included only when the PubMed search completed",
    "All generated-file paths shown in the report and final chat are relative paths",
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


def normalize_dependency(value: object) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {part.strip() for part in re.split(r"[,;]", value) if part.strip()}
    if isinstance(value, (list, tuple, set)):
        return {str(part).strip() for part in value if str(part).strip()}
    return {str(value).strip()}


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
    requires = normalize_dependency(metadata.get("requires"))
    optional = normalize_dependency(metadata.get("optional"))
    if "zotero-mcp" not in requires:
        fail("frontmatter metadata.requires must include zotero-mcp")
    if "pubmed-mcp" not in optional:
        fail("frontmatter metadata.optional must include pubmed-mcp")
    ok(f"frontmatter parsed; version {metadata['version']}; dependencies declared")

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
    require_all(text, NUMBERED_CITATION_REPAIR_REQUIREMENTS, "numbered citation repair requirement")
    require_all(text, CITATION_SUPPORT_LEDGER_REQUIREMENTS, "Citation Support Ledger requirement")
    ok("default citation-support, numbered-citation repair, and Citation Support Ledger routing requirements present")

    require_all(text, UNIFIED_WORKFLOW_REQUIREMENTS, "unified paragraph citation workflow requirement")
    ok("unified paragraph citation workflow requirements present")

    require_all(text, MCP_READINESS_REQUIREMENTS, "MCP readiness requirement")
    require_all(text, PUBMED_TOOL_REQUIREMENTS, "PubMed tool requirement")
    require_all(text, PUBMED_GUARDRAIL_REQUIREMENTS, "PubMed guardrail requirement")
    require_all(text, PUBMED_SEQUENTIAL_GUARDRAIL_REQUIREMENTS, "PubMed sequential execution guardrail")
    ok("MCP readiness and PubMed guardrail requirements present")

    require_all(text, PHASE10_REQUIREMENTS, "Phase 10 evidence package format requirement")
    ok("Phase 10 evidence package status, section, matrix, and final-chat requirements present")

    require_all(text, QA_SELF_CHECK_REQUIREMENTS, "Phase 9 QA self-check requirement")
    prompt_pos = text.find("### Evidence Package QA Self-Check Prompt")
    output_format_pos = text.find("### Output Format", prompt_pos)
    if prompt_pos == -1 or output_format_pos == -1:
        fail("Evidence Package QA Self-Check Prompt must appear before Module 2.5 Output Format")
    ok("Phase 9 pre-write/post-write QA self-check requirements present")

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
        re.escape(CLAIM_EVIDENCE_MATRIX_HEADER),
        [
            "#",
            "Claim",
            "Source layer",
            "Evidence level",
            "Zotero evidence",
            "PubMed evidence",
            "Evidence status",
            "Confidence",
            "Risk",
            "Recommended action",
            "Recommended citation",
        ],
        "Claim–Evidence Matrix",
    )
    require_table_header(
        evidence_report_template,
        r"\| Sentence / clause \| Recommended text \| Issue type / writing issue \| Source layer \| Evidence level \| Citation rationale \| Caveat / reviewer risk \|",
        ["Sentence / clause", "Recommended text", "Issue type / writing issue", "Source layer", "Evidence level", "Citation rationale", "Caveat / reviewer risk"],
        "Annotated Recommended Text",
    )
    require_table_header(
        evidence_report_template,
        r"\| # \| Citation \| Year \| Study type \| Main use \| Evidence source \| Zotero \| PDF \| DOI \|.*",
        ["DOI", "PMID", "Collection"],
        "Reference Table",
    )
    require_table_header(
        evidence_report_template,
        r"\| Source \| Query \| Mode \| Max results \| Status \| Included \| Notes \|",
        ["Source", "Query", "Mode", "Max results", "Status", "Included", "Notes"],
        "Search Reproducibility",
    )
    require_table_header(
        evidence_report_template,
        r"\| Affected claim / sentence \| Risk \| Severity \| Evidence basis \| Suggested fix \|",
        ["Affected claim / sentence", "Risk", "Severity", "Evidence basis", "Suggested fix"],
        "Reviewer-risk",
    )
    require_table_header(
        evidence_report_template,
        r"\| Selected reference \| Original citation number \| Canonical identifier \| DOI \| PMID \| Title check \| First author check \| Year check \| Canonical Zotero key \| Duplicate keys \| Duplicate check result \| Metadata source of truth \| RIS action \| Reason \|",
        [
            "Selected reference",
            "Original citation number",
            "Canonical identifier",
            "DOI",
            "PMID",
            "Title check",
            "First author check",
            "Year check",
            "Canonical Zotero key",
            "Duplicate keys",
            "Duplicate check result",
            "Metadata source of truth",
            "RIS action",
            "Reason",
        ],
        "Reference Canonicalization Gate",
    )
    require_table_header(
        evidence_report_template,
        re.escape(CITATION_SUPPORT_LEDGER_HEADER),
        [
            "Claim / sentence",
            "Recommended citation",
            "Source layer",
            "Evidence level",
            "Inspection route",
            "Evidence location",
            "Support verdict",
            "RIS action",
            "Required wording/action",
        ],
        "Citation Support Ledger",
    )
    require_table_header(
        evidence_report_template,
        re.escape(NUMBERED_CITATION_REPAIR_HEADER),
        [
            "Original citation number",
            "Supplied reference",
            "Claim supported by this number",
            "Support verdict",
            "Verification verdict",
            "Evidence level",
            "Action: Keep / Replace / Remove / Verify / Add supporting citation",
            "Replacement candidate",
            "Original citation number preserved for audit",
            "Final numbering handled by EndNote/Word",
            "RIS action",
            "Reason",
        ],
        "Existing Numbered Citation Repair",
    )
    require_table_header(
        evidence_report_template,
        r"\| Citation \| Original citation number \| Missing metadata \| Metadata mismatch \| Duplicate warning \| Evidence source \| RIS standardization source \| RIS action \|",
        ["Citation", "Original citation number", "Missing metadata", "Metadata mismatch", "Duplicate warning", "Evidence source", "RIS standardization source", "RIS action"],
        "Metadata Quality Control",
    )
    if "## 2. 推荐稿件文本（Recommended Manuscript Text）" in evidence_report_template:
        fail("old Recommended Manuscript Text section remains in Evidence Review report template")
    critical_warning_requirements = [
        "No critical warnings",
        "PubMed tool unavailable",
        "PubMed query failed",
        "central claim has no direct evidence",
        "External evidence contradicts the draft claim",
        "citation, concept, DOI/PMID",
        "Metadata mismatch remains unresolved",
        "Duplicate Zotero records affect selected references",
        "current-study finding could be mistaken for external evidence support",
        "Causal wording is not directly supported",
        "BMI-independent wording is not directly supported",
        "Horizontal pleiotropy wording is not directly supported",
        "Critical warnings must not be hidden only in later reviewer-risk or metadata-QC sections",
    ]
    require_all(text, critical_warning_requirements, "critical warning requirement")
    search_reproducibility_requirements = [
        "Zotero semantic query",
        "Zotero keyword query",
        "PubMed query",
        "PubMed max results",
        "PubMed status",
        "failed reason",
        "included PMIDs",
        "excluded records and reason",
        "full_text_inspected",
        "attempted or planned PubMed query",
        "included_count",
        "excluded_reason",
        "max_results",
    ]
    require_all(text, search_reproducibility_requirements, "search reproducibility requirement")
    reference_canonicalization_requirements = [
        "Existing Numbered Citation Repair",
        "Original citation number",
        "Claim supported by this number",
        "Support verdict",
        "Verification verdict",
        "Original citation number preserved for audit",
        "Final numbering handled by EndNote/Word",
        "unsupported numbered citation",
        "Reference Canonicalization Gate",
        "canonical identifier",
        "DOI, PMID, title, first author, and year",
        "canonical Zotero key",
        "duplicate keys",
        "Duplicate check result",
        "metadata source of truth",
        "RIS action",
        "Include",
        "Exclude",
        "Verify",
        "Optional",
        "Possible metadata mismatch",
        "Unresolved mismatch must not enter RIS",
        "If DOI or PMID is the same across candidates, merge them into one canonical record",
    ]
    require_all(text, reference_canonicalization_requirements, "reference canonicalization requirement")
    run_relationship_requirements = [
        "Run Relationship and Superseded Mechanism",
        "Related prior packages",
        "Run relationship rationale",
        "Potentially supersedes",
        "Complementary to",
        "Related; supersession unclear",
        "Do not automatically modify old evidence package files",
        "topic slug similarity",
        "core keyword overlap",
        "selected references overlap",
        "DOI/PMID overlap",
        "project-level summary only when the user asks",
    ]
    require_all(text, run_relationship_requirements, "run relationship requirement")
    require_all(
        evidence_report_template,
        ["| Related prior packages |", "| Run relationship rationale |"],
        "run relationship metadata row",
    )
    if "Critical Warnings:" not in text:
        fail("final chat summary must include Critical Warnings")
    metadata_pos = evidence_report_template.find("## 1. Metadata and Use Status")
    critical_pos = evidence_report_template.find("## 2. Critical Warnings")
    bottom_line_pos = evidence_report_template.find("## 3. 核心结论（Bottom Line）")
    if not (metadata_pos != -1 and metadata_pos < critical_pos < bottom_line_pos):
        fail("Critical Warnings must appear after metadata and before Bottom Line")
    if "citation should be verified" not in text:
        fail("Copy-ready rules must explicitly forbid citation-should-be-verified wording")
    if "manuscript-ready text only" not in evidence_report_template:
        fail("Copy-ready Manuscript Text template must be directly copyable and annotation-free")
    if (
        "来源：Zotero 本地库；PubMed:" not in evidence_report_template
        and "Source: Zotero local library; PubMed:" not in evidence_report_template
    ):
        fail("Evidence Review report Source line must expose PubMed execution status")
    if "该用中文报告的部分用中文" not in text:
        fail("Durable output language policy must preserve Chinese-first reporting rules")
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
